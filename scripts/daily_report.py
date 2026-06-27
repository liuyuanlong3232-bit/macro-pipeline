#!/usr/bin/env python3
"""
宏观日报 v1.2 — 三因子信号系统 + 农业天气
新结构:
  1. Raw Data（偏离值）
  2. Event Layer（金十财经日历）
  3. 三因子模型（USD/Liquidity/Demand分数）
  4. 资产模型（Gold/Silver/Tin/Oil信号）
  5. 信号输出（↑↓ + score）
  5-B. 农业与天气（C区+D区）
  6. 总结（risk-on/off + 主导因子 + 主线资产）
  + 金十快讯(F区)
"""
import sys, sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

# 金十数据 MCP API
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
try:
    from jin10_api import get_weekly_calendar, get_latest_flash, get_quote
    HAS_JIN10 = True
except ImportError:
    HAS_JIN10 = False

# 动态定位项目根目录
PIPELINE_ROOT = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, PIPELINE_ROOT)

# 导入三因子信号模块
try:
    from macro_signal import calc_signals
    HAS_SIGNAL = True
except ImportError:
    HAS_SIGNAL = False
    print("⚠️ macro_signal 模块未找到，三因子功能禁用")

NOW = datetime.now()
TODAY = NOW.strftime("%Y-%m-%d")
DB = str(Path.home() / "hermes-macro-data" / "hermes.db")
DATA_FRESHNESS = {}

# ═══════ 工具函数 ═══════
def db_one(sql, params=None):
    source = sql.split(" FROM ", 1)[-1].split()[0]
    try:
        conn = sqlite3.connect(DB); cur = conn.cursor()
        cur.execute(sql, params or ()); r = cur.fetchone(); conn.close()
        if r is None:
            print(f"[data-read] source={source} status=MISSING fallback=caller-default")
        return r
    except Exception as e:
        print(f"[data-read] source={source} status=FAILED fallback=caller-default error={type(e).__name__}")
        return None

def gv(series_id):
    r = db_one('SELECT "數值", "日期" FROM fred_indicators WHERE "系列ID"=? ORDER BY "日期" DESC LIMIT 1', (series_id,))
    return (str(r[0]), str(r[1])) if r else ("—", "—")

def yv(kw):
    r = db_one('SELECT "最新價", "日漲跌幅%", "日期" FROM yahoo_futures WHERE "品種" LIKE ? ORDER BY "日期" DESC LIMIT 1', (f"%{kw}%",))
    if r and r[0]: return (float(r[0]), str(r[1] if r[1] else "0"), str(r[2]) if r[2] else "")
    return (None, "", "")

def _record_freshness(name, value, source_time="", fetched_time="", fallback=False):
    last_updated_time = str(fetched_time or source_time or "")
    if value in (None, "", "—"):
        freshness_status = "MISSING"
    elif fallback or not last_updated_time or last_updated_time[:10] != TODAY:
        freshness_status = "STALE"
    else:
        freshness_status = "OK"
    DATA_FRESHNESS[name] = {
        "last_updated_time": last_updated_time,
        "freshness_status": freshness_status,
    }

def _append_freshness_table(lines):
    if not DATA_FRESHNESS:
        return
    lines.append("")
    lines.append("📡 数据新鲜度")
    lines.append("")
    lines.append("| 指标 | freshness_status | last_updated_time |")
    lines.append("|------|------------------|-------------------|")
    for name in ("DXY", "GOLD", "SILVER", "TIP"):
        info = DATA_FRESHNESS.get(name, {})
        lines.append(
            f"| {name} | {info.get('freshness_status', 'MISSING')} | {info.get('last_updated_time', '') or '—'} |"
        )


def gv_meta(series_id):
    r = db_one('SELECT "數值", "日期", "抓取日" FROM fred_indicators WHERE "系列ID"=? ORDER BY "日期" DESC LIMIT 1', (series_id,))
    if r:
        return (str(r[0]), str(r[1] or ""), str(r[2] or ""))
    return ("—", "", "")

def yv_meta(kw):
    r = db_one('SELECT "最新價", "日漲跌幅%", "日期", "抓取日" FROM yahoo_futures WHERE "品種" LIKE ? ORDER BY "日期" DESC LIMIT 1', (f"%{kw}%",))
    if r and r[0]:
        return (float(r[0]), str(r[1] if r[1] else "0"), str(r[2] or ""), str(r[3] or ""))
    return (None, "", "", "")

def cv(kw):
    r = db_one('SELECT "COT Index(26W)" FROM cotdata WHERE "品種" LIKE ? LIMIT 1', (f"%{kw}%",))
    return float(r[0]) if r and r[0] else None

def tin_v():
    """获取伦锡数据 - 从CSV文件读取"""
    try:
        csv_dir = Path.home() / "hermes-macro-data" / "csv" / datetime.now().strftime("%Y-%m-%d")
        csv_path = csv_dir / "akshare_tin.csv"
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            if not df.empty and '最新价' in df.columns:
                return (float(df['最新价'].iloc[0]), float(df['涨跌幅'].iloc[0]) if '涨跌幅' in df.columns else 0)
    except Exception:
        pass
    return (None, 0)

def chg_s(v, threshold=2.0):
    try:
        pct = float(v)
        arrow = "🔺" if pct > 0 else "🔻" if pct < 0 else ""
        alert = " ⚠️" if abs(pct) > threshold else ""
        return f"{arrow}{pct:+.2f}%{alert}"
    except Exception: return "—"

def fmt(v, dp=2):
    if v is None: return "—"
    try: return f"{float(v):,.{dp}f}"
    except Exception: return str(v)

def _risk_float(v):
    try:
        if v in (None, "", "—", "暂无数据"):
            return None
        return float(str(v).replace(",", "").replace("%", ""))
    except Exception:
        return None

def _risk_level(points):
    if points >= 6:
        return "🔴 危机"
    if points >= 4:
        return "🟠 警戒"
    if points >= 2:
        return "🟡 注意"
    return "🟢 正常"

def _risk_value_line(name, value, date="", suffix=""):
    if value in (None, "", "—"):
        return f"  · {name}: 暂无数据"
    date_part = f" ({str(date)[:10]})" if date and date != "—" else ""
    return f"  · {name}: {value}{suffix}{date_part}"

def _append_financial_risk_monitor(L, dxy_px=None, dxy_dt="", tips_v="—", tips_d="", dgs10_v="—", dgs10_d=""):
    """Append-only financial risk monitor. Does not feed any existing score model."""
    try:
        dgs2_v, dgs2_d = gv("DGS2")
        stlfsi_v, stlfsi_d = gv("STLFSI4")
        hy_oas_v, hy_oas_d = gv("BAMLH0A0HYM2")
        default_v, default_d = gv("DRBLACBS")
        cp_v, cp_d = gv("CPF3M")
        loan_v, loan_d = gv("TOTLL")
        credit_growth_v, credit_growth_d = gv("BUSLOANS")
    except Exception:
        dgs2_v = dgs2_d = stlfsi_v = stlfsi_d = hy_oas_v = hy_oas_d = "—"
        default_v = default_d = cp_v = cp_d = loan_v = loan_d = credit_growth_v = credit_growth_d = "—"

    kbe_px, kbe_chg, kbe_dt = yv("KBE")
    kre_px, kre_chg, kre_dt = yv("KRE")
    hyg_px, hyg_chg, hyg_dt = yv("HYG")

    dxy_num = _risk_float(dxy_px)
    tips_num = _risk_float(tips_v)
    dgs2_num = _risk_float(dgs2_v)
    dgs10_num = _risk_float(dgs10_v)
    stlfsi_num = _risk_float(stlfsi_v)
    hy_oas_num = _risk_float(hy_oas_v)
    kbe_chg_num = _risk_float(kbe_chg)
    kre_chg_num = _risk_float(kre_chg)
    hyg_chg_num = _risk_float(hyg_chg)
    curve_num = None
    if dgs10_num is not None and dgs2_num is not None:
        curve_num = dgs10_num - dgs2_num

    us_points = 0
    if dxy_num is not None and dxy_num >= 108: us_points += 1
    if tips_num is not None and tips_num >= 2.5: us_points += 1
    if dgs2_num is not None and dgs2_num >= 5.0: us_points += 1
    if dgs10_num is not None and dgs10_num >= 5.0: us_points += 1
    if curve_num is not None and curve_num <= -0.75: us_points += 1
    if stlfsi_num is not None and stlfsi_num >= 1.0: us_points += 2
    if hy_oas_num is not None and hy_oas_num >= 5.0: us_points += 2
    if hyg_chg_num is not None and hyg_chg_num <= -2.0: us_points += 1
    if kbe_chg_num is not None and kbe_chg_num <= -3.0: us_points += 1
    if kre_chg_num is not None and kre_chg_num <= -3.0: us_points += 1
    us_level = _risk_level(us_points)

    credit_points = 0
    default_num = _risk_float(default_v)
    cp_num = _risk_float(cp_v)
    loan_num = _risk_float(loan_v)
    credit_growth_num = _risk_float(credit_growth_v)
    if default_num is not None and default_num >= 4.0: credit_points += 2
    if cp_num is not None and cp_num >= 5.5: credit_points += 1
    if loan_num is not None and loan_num < 0: credit_points += 1
    if credit_growth_num is not None and credit_growth_num < 0: credit_points += 1
    credit_risk = "高" if credit_points >= 3 else "中" if credit_points >= 1 else "低"

    global_risk = "正常"
    if dxy_num is not None and dxy_num >= 108:
        global_risk = "偏紧"
    if dxy_num is not None and dxy_num >= 112:
        global_risk = "紧张"

    total_points = us_points + credit_points
    if global_risk == "偏紧":
        total_points += 1
    elif global_risk == "紧张":
        total_points += 2
    overall = _risk_level(total_points)

    if "🔴" in overall:
        summary = "金融压力已进入高风险区间，需要重点关注信用利差、银行股和美元流动性共振。"
    elif "🟠" in overall:
        summary = "信用风险开始累积，建议提高风险意识。"
    elif "🟡" in overall:
        summary = "金融条件略有收紧，但暂未出现系统性金融危机特征。"
    else:
        summary = "当前尚未出现系统性金融危机特征，信用环境保持稳定。"

    L.append("")
    L.append("=" * 25)
    L.append("Financial Risk Monitor")
    L.append("金融风险监测")
    L.append("=" * 6)
    L.append("")
    L.append("该模块用于监测系统性金融风险，不参与现有黄金、白银、锡、原油评分。")
    L.append("")
    L.append("一、美国金融系统（每日）")
    L.append(f"风险等级：{us_level}")
    L.append("一句话说明：美元、实际利率、收益率曲线、金融压力、信用利差与银行ETF共同监测。")
    L.append(_risk_value_line("DXY", fmt(dxy_px) if dxy_px not in (None, "", "—") else "暂无数据", dxy_dt))
    L.append(_risk_value_line("TIP实际利率代理", tips_v if tips_v != "—" else "暂无数据", tips_d, "%"))
    L.append(_risk_value_line("2Y Treasury", dgs2_v if dgs2_v != "—" else "暂无数据", dgs2_d, "%"))
    L.append(_risk_value_line("10Y Treasury", dgs10_v if dgs10_v != "—" else "暂无数据", dgs10_d, "%"))
    curve_text = f"{curve_num:.2f}%" if curve_num is not None else "暂无数据"
    L.append(_risk_value_line("收益率曲线（10Y-2Y）", curve_text))
    L.append(_risk_value_line("STL Financial Stress Index", stlfsi_v if stlfsi_v != "—" else "暂无数据", stlfsi_d))
    hy_proxy = hy_oas_v if hy_oas_v != "—" else (f"HYG {chg_s(hyg_chg)}" if hyg_px is not None else "暂无数据")
    L.append(_risk_value_line("信用利差（HY OAS/HYG代理）", hy_proxy, hy_oas_d if hy_oas_v != "—" else hyg_dt, "%" if hy_oas_v != "—" else ""))
    bank_parts = []
    if kbe_px is not None: bank_parts.append(f"KBE {fmt(kbe_px)} ({chg_s(kbe_chg)})")
    if kre_px is not None: bank_parts.append(f"KRE {fmt(kre_px)} ({chg_s(kre_chg)})")
    L.append(_risk_value_line("银行ETF（KBE/KRE）", " / ".join(bank_parts) if bank_parts else "暂无数据", kbe_dt or kre_dt))
    L.append("")
    L.append("二、信用风险（每周）")
    L.append(f"信用风险：{credit_risk}")
    L.append(_risk_value_line("企业债违约率", default_v if default_v != "—" else "暂无数据", default_d, "%"))
    L.append(_risk_value_line("Commercial Paper", cp_v if cp_v != "—" else "暂无数据", cp_d, "%"))
    L.append(_risk_value_line("银行贷款增速", loan_v if loan_v != "—" else "暂无数据", loan_d))
    L.append(_risk_value_line("信贷扩张速度", credit_growth_v if credit_growth_v != "—" else "暂无数据", credit_growth_d))
    L.append("")
    L.append("三、全球风险（每周）")
    L.append(f"全球风险：{global_risk}")
    L.append("  · BIS Credit Gap: 暂无数据")
    L.append("  · 全球美元流动性: 暂无数据")
    L.append("  · 全球外汇储备变化: 暂无数据")
    L.append("")
    L.append("四、综合判断")
    L.append(f"金融风险：{overall}")
    L.append(summary)
    L.append("数据源: FRED, BIS, Yahoo Finance, Treasury, TIP代理；缺失数据以“暂无数据”显示。")

def cn_weather():
    """获取中国城市天气"""
    try:
        conn = sqlite3.connect(DB); cur = conn.cursor()
        cur.execute("SELECT city, temp, text, humidity, wind_dir, wind_scale FROM cn_weather WHERE date=? AND hour='now' ORDER BY city", (TODAY,))
        rows = cur.fetchall(); conn.close(); return rows or []
    except Exception: return []

def agri_weather_detail():
    """获取全球6产区最近天气详情"""
    regions = [
        ("US_IL", "美国IL玉米带"), ("US_IA", "美国IA玉米带"),
        ("BR_MT", "巴西马托格罗索"), ("BR_PR", "巴西帕拉纳"),
        ("AR_BA", "阿根廷大豆带"), ("US_KS", "美国堪萨斯小麦"),
    ]
    try:
        conn = sqlite3.connect(DB); cur = conn.cursor()
        result = []
        for code, name in regions:
            rows = cur.execute("""SELECT AVG(temp_mean_c), SUM(precip_mm), COUNT(*) 
                FROM agri_weather WHERE region=? AND date >= ? AND temp_mean_c IS NOT NULL""",
                (code, (NOW-timedelta(days=7)).strftime("%Y-%m-%d"))).fetchone()
            if rows and rows[0] is not None:
                avg_t, total_p, cnt = rows
                today_r = cur.execute("""SELECT temp_mean_c, precip_mm FROM agri_weather 
                    WHERE region=? AND date=? AND temp_mean_c IS NOT NULL""",
                    (code, TODAY)).fetchone()
                t_today, p_today = (today_r[0], today_r[1]) if today_r else (None, None)
                result.append((name, avg_t, total_p, cnt, t_today, p_today))
            else:
                result.append((name, None, None, 0, None, None))
        conn.close()
        return result
    except Exception:
        return []


def cn_futures():
    """获取国内期货数据(只取最新一天)"""
    try:
        conn = sqlite3.connect(DB); cur = conn.cursor()
        cur.execute("SELECT name, close, change_pct, vol, unit FROM cn_futures WHERE date=(SELECT MAX(date) FROM cn_futures) ORDER BY name")
        rows = cur.fetchall(); conn.close(); return rows or []
    except Exception: return []

# ═══════ 主函数 ═══════

def main():
    """主函数：拉取数据、组装报告"""
    # ── 基础数据 ──
    dxy_px, dxy_chg, dxy_dt, dxy_fetched = yv_meta("ICE美元")
    _record_freshness("DXY", dxy_px, dxy_dt, dxy_fetched)
    
    # 黄金：优先金十，备用Yahoo
    jin10_gold = get_quote("XAUUSD") if HAS_JIN10 else None
    if jin10_gold and jin10_gold.get("close"):
        gold_px = float(jin10_gold["close"])
        gold_chg = float(jin10_gold.get("ups_percent", 0))
        gold_dt = jin10_gold.get("time", "")[:10]
        _record_freshness("GOLD", gold_px, gold_dt)
        print("[jin10] 黄金: {} ({:+.2f}%)".format(gold_px, gold_chg))
    else:
        gold_px, gold_chg, gold_dt, gold_fetched = yv_meta("黃金期貨")
        _record_freshness("GOLD", gold_px, gold_dt, gold_fetched, fallback=True)
    
    # 白银：优先金十，备用Yahoo
    jin10_silver = get_quote("XAGUSD") if HAS_JIN10 else None
    if jin10_silver and jin10_silver.get("close"):
        silver_px = float(jin10_silver["close"])
        silver_chg = float(jin10_silver.get("ups_percent", 0))
        silver_dt = jin10_silver.get("time", "")[:10]
        _record_freshness("SILVER", silver_px, silver_dt)
        print("[jin10] 白银: {} ({:+.2f}%)".format(silver_px, silver_chg))
    else:
        silver_px, silver_chg, silver_dt, silver_fetched = yv_meta("白銀期貨")
        _record_freshness("SILVER", silver_px, silver_dt, silver_fetched, fallback=True)
    tin_px, tin_chg = tin_v()
    vix_px, vix_chg, vix_dt = yv("VIX恐慌")
    dgs10_v, dgs10_d = gv("DGS10"); tips_v, tips_d, tips_fetched = gv_meta("DFII10")
    
    # TIP ETF代理TIPS
    tip_px, tip_chg, tip_dt, tip_fetched = yv_meta("TIP ETF")
    if tips_v != "—":
        _record_freshness("TIP", tips_v, tips_d, tips_fetched)
    else:
        _record_freshness("TIP", tip_px, tip_dt, tip_fetched, fallback=tip_px is not None)
    tip_tips_est = None
    if tip_px:
        tip_tips_est = round(1.8 + (112 - tip_px) * 0.08, 2)
    gold_cot = cv("黄金"); silver_cot = cv("白银")
    ff_v, ff_d = gv("FEDFUNDS"); cpi_v, cpi_d = gv("CPIAUCSL")
    unemp_v, unemp_d = gv("UNRATE")
    # WTI：优先金十，备用Yahoo
    jin10_wti = get_quote("USOIL") if HAS_JIN10 else None
    if jin10_wti and jin10_wti.get("close"):
        wti_px = float(jin10_wti["close"])
        wti_chg = float(jin10_wti.get("ups_percent", 0))
        wti_dt = jin10_wti.get("time", "")[:10]
    else:
        wti_px, wti_chg, wti_dt = yv("WTI原油")
    
    # Brent：优先金十，备用Yahoo
    jin10_brent = get_quote("UKOIL") if HAS_JIN10 else None
    if jin10_brent and jin10_brent.get("close"):
        brent_px = float(jin10_brent["close"])
        brent_chg = float(jin10_brent.get("ups_percent", 0))
        brent_dt = jin10_brent.get("time", "")[:10]
    else:
        brent_px, brent_chg, brent_dt = yv("Brent原油")
    
    # ── C区：农业+天气 ──
    corn_px, corn_chg, corn_dt = yv("玉米期貨")
    soy_px, soy_chg, soy_dt = yv("大豆期貨")
    wheat_px, wheat_chg, wheat_dt = yv("小麥期貨")
    soyoil_px, soyoil_chg, soyoil_dt = yv("豆油期貨")
    soymeal_px, soymeal_chg, soymeal_dt = yv("豆粕期貨")
    cotton_px, cotton_chg, cotton_dt = yv("棉花期貨")
    sugar_px, sugar_chg, sugar_dt = yv("糖期貨")
    corn_cot = cv("玉米"); soy_cot = cv("大豆"); wheat_cot = cv("小麦")

    # ── 天气异常检测 + 产区详情 ──
    weather_alerts = []
    for region, name in [("US_IL","美中西部IL"), ("US_IA","美中西部IA"), ("BR_MT","巴西MT"), ("BR_PR","巴西PR"), ("AR_BA","阿根廷"), ("US_KS","美国KS")]:
        r = db_one('SELECT AVG(precip_mm) FROM agri_weather WHERE region=? AND date >= ? AND precip_mm IS NOT NULL',
                   (region, (NOW-timedelta(days=30)).strftime("%Y-%m-%d")))
        if r and r[0]:
            avg30 = float(r[0])
            if avg30 < 1.0:
                weather_alerts.append(f"⚠️ {name}: 30天均降水 {avg30:.1f}mm（偏干）")
            elif avg30 > 8.0:
                weather_alerts.append(f"⚠️ {name}: 30天均降水 {avg30:.1f}mm（偏湿）")
    agri_wx = agri_weather_detail()

    # ── D区：中国农业+天气 ──
    cn_wx = cn_weather()
    cn_ft = cn_futures()

    # ── 获取三因子信号 ──
    signals = None
    if HAS_SIGNAL:
        try:
            signals = calc_signals()
        except Exception as e:
            print(f"⚠️ 三因子计算失败: {e}")

    # ═══════ 组装报告 ═══════
    L = []
    L.append("📅 宏观日报 v1.1 | " + TODAY)
    L.append("━" * 55)
    L.append("")

    # ━━━ 飞前自检 ━━━
    missing = []
    for name, kw in [("DXY","ICE美元"), ("黄金","黃金"), ("白银","白銀"), ("WTI","WTI原油"), ("VIX","VIX")]:
        if not db_one('SELECT 1 FROM yahoo_futures WHERE "品種" LIKE ? LIMIT 1', (f"%{kw}%",)):
            missing.append(name)
    if tin_px is None:
        missing.append("伦锡")
    if missing:
        L.append("⚠️ 缺失: " + ", ".join(missing))
    else:
        L.append("✅ 数据完整 · 全资产就绪")

    # ═════════════ ① Raw Data（偏离值）═════════════
    L.append("")
    L.append("━" * 55)
    L.append("📊 ① Raw Data（偏离值）")
    L.append("")
    # TIP代理行
    tip_line = ""
    if tip_px and tip_tips_est:
        tip_line = " | TIP代理: ~{}% (TIP={})".format(tip_tips_est, fmt(tip_px))
    L.append("  DXY: {} ({}) | 10Y: {}% | TIPS: {}%{}".format(
        fmt(dxy_px), chg_s(dxy_chg), dgs10_v, tips_v, tip_line))
    L.append("  黄金: ${} ({}) | 白银: ${} ({})".format(
        fmt(gold_px,0), chg_s(gold_chg), fmt(silver_px,2), chg_s(silver_chg)))
    L.append("  伦锡: {} ({:+.2f}%) | WTI: ${} ({}) | Brent: ${} ({})".format(
        fmt(tin_px,0), tin_chg, fmt(wti_px), chg_s(wti_chg), fmt(brent_px), chg_s(brent_chg)))
    L.append("  VIX: {} ({})".format(fmt(vix_px,2), chg_s(vix_chg)))

    # ═════════════ ② Event Layer（金十财经日历）═════════════
    L.append("")
    L.append("━" * 55)
    L.append("📅 ② Event Layer（金十财经日历）")
    L.append("")
    if HAS_JIN10:
        try:
            weekly_cal = get_weekly_calendar(stars_min=3)
            if weekly_cal:
                for item in weekly_cal[:8]:
                    t = item.get("pub_time", "")[-5:]
                    title = item.get("title", "")
                    star = item.get("star", 0)
                    actual = item.get("actual") or "—"
                    consensus = item.get("consensus") or "—"
                    prev = item.get("previous") or "—"
                    L.append("  {} ★{} {}".format(t, star, title))
                    L.append("    前值:{} | 共识:{} | 实际:{}".format(prev, consensus, actual))
                L.append("")
                L.append("  数据源: 金十数据MCP · 本周{}条重要事件".format(len(weekly_cal)))
            else:
                L.append("  本周暂无重要经济数据")
        except Exception as e:
            L.append("  ⚠️ 金十日历获取失败: {}".format(str(e)[:50]))
    else:
        L.append("  金十数据未配置")

    # ═════════════ ③ 三因子模型（双层架构）═════════════
    L.append("")
    L.append("━" * 55)
    L.append("🧮 ③ 三因子模型（双层架构）")
    L.append("")
    if signals:
        factors = signals["factors"]
        # USD双层显示
        usd_final = factors["USD"]
        usd_macro = factors.get("USD_macro", 0)
        usd_market = factors.get("USD_market", 0)
        
        L.append("  USD_final:  {:+.2f}  ({})".format(
            usd_final, "美元强势" if usd_final > 0 else "美元弱势"))
        L.append("  ├─ Macro:   {:+.2f}  (趋势方向，权重0.6)".format(usd_macro))
        L.append("  └─ Market:  {:+.2f}  (短期偏离，权重0.4)".format(usd_market))
        L.append("")
        L.append("  Liquidity:  {:+.2f}  ({})".format(
            factors["Liquidity"], "流动性充裕" if factors["Liquidity"] > 0 else "流动性紧张"))
        L.append("  Demand:     {:+.2f}  ({})".format(
            factors["Demand"], "中国需求强" if factors["Demand"] > 0 else "中国需求弱"))
        L.append("")
        L.append("  联邦基金: {}% | CPI: {} | 失业率: {}%".format(ff_v, cpi_v, unemp_v))
    else:
        L.append("  ⚠️ 三因子模块未加载")

    # ═════════════ ④ 资产模型 ═════════════
    L.append("")
    L.append("━" * 55)
    L.append("📈 ④ 资产模型（Gold/Silver/Tin/Oil信号）")
    L.append("")
    if signals:
        assets = signals["assets"]
        for name, info in assets.items():
            icon = "🥇" if name == "Gold" else "🥈" if name == "Silver" else "🔩" if name == "Tin" else "🛢️"
            L.append("  {} {}: {} {:+.2f} ({})".format(
                icon, name, info["dir"], info["score"], info["str"]))
        L.append("")
        L.append("  COT黄金: {} ({}) | COT白银: {}".format(
            gold_cot or "—",
            "极度看多" if gold_cot and gold_cot >= 90 else "看多" if gold_cot and gold_cot >= 70 else "中性" if gold_cot and gold_cot >= 30 else "—",
            silver_cot or "—"))
    else:
        L.append("  ⚠️ 三因子模块未加载")

    # ═════════════ ⑤ 信号输出 ═════════════
    L.append("")
    L.append("━" * 55)
    L.append("🎯 ⑤ 信号输出（↑↓ + score）")
    L.append("")
    if signals:
        assets = signals["assets"]
        L.append("  ┌─────────┬──────┬───────┬────────┐")
        L.append("  │ 资产    │ 信号 │ 分数  │ 强度   │")
        L.append("  ├─────────┼──────┼───────┼────────┤")
        for name, info in assets.items():
            L.append("  │ {:<7} │  {}  │ {:+.2f} │ {:<6} │".format(
                name, info["dir"], info["score"], info["str"]))
        L.append("  └─────────┴──────┴───────┴────────┘")
    else:
        L.append("  ⚠️ 三因子模块未加载")

    # ═════════════ ⑤-B 农业与天气 (C区 + D区) ═════════════
    L.append("")
    L.append("━" * 55)
    L.append("🌾 ⑤-B · 农业与天气")
    L.append("")
    L.append("━━ C区 · 农业与天气 ━━")
    L.append("")
    if corn_px or soy_px or wheat_px:
        agri_core = []
        if corn_px: agri_core.append(f"玉米 {fmt(corn_px,2)}¢ ({chg_s(corn_chg)})")
        if soy_px: agri_core.append(f"大豆 {fmt(soy_px,2)}¢ ({chg_s(soy_chg)})")
        if wheat_px: agri_core.append(f"小麦 {fmt(wheat_px,2)}¢ ({chg_s(wheat_chg)})")
        L.append("  " + "  ·  ".join(agri_core))
        cot_agri = []
        if corn_cot: cot_agri.append(f"玉米COT:{corn_cot:.0f}")
        if soy_cot: cot_agri.append(f"大豆COT:{soy_cot:.0f}")
        if wheat_cot: cot_agri.append(f"小麦COT:{wheat_cot:.0f}")
        if cot_agri: L.append("  " + " | ".join(cot_agri))
        if cotton_px: L.append(f"  棉花 {fmt(cotton_px)}¢ ({chg_s(cotton_chg)}) | 糖 {fmt(sugar_px)}¢ ({chg_s(sugar_chg)}) | 豆油 {fmt(soyoil_px)}¢ | 豆粕 ${fmt(soymeal_px)}")
        if agri_wx:
            L.append("  ┌──────────────┬──────┬────────┬──────┐")
            L.append("  │ 产区         │ 均温 │ 7日降水│ 今日 │")
            L.append("  ├──────────────┼──────┼────────┼──────┤")
            for name, avg_t, total_p, cnt, t_today, p_today in agri_wx:
                t_str = f"{avg_t:.1f}°" if avg_t is not None else "—"
                p_str = f"{total_p:.1f}mm" if total_p is not None else "—"
                td_str = f"{t_today:.0f}°" if t_today is not None else "—"
                flag = ""
                if total_p is not None and total_p < 1.0: flag = " 🔥"
                elif total_p is not None and total_p > 15.0: flag = " 🌊"
                L.append(f"  │ {name:<12} │{t_str:>5}│{p_str:>7}{flag}│{td_str:>5}│")
            L.append("  └──────────────┴──────┴────────┴──────┘")
        if weather_alerts:
            L.append("  ⚠️ 异常预警:")
            for wa in weather_alerts: L.append("    " + wa)
    else:
        L.append("  板块正常，无异常波动")
    L.append("")
    L.append("━━ D区 · 中国农业 ━━")
    L.append("")
    if cn_ft:
        L.append("  国内期货:")
        for row in cn_ft:
            name, close, chg, vol, unit = row
            arrow = "🔺" if (chg or 0) > 0 else "🔻" if (chg or 0) < 0 else "➡️"
            chg_str = "{:+.1f}%".format(chg) if chg else "—"
            L.append("  {} ¥{:.0f}{} {} {}手".format(name, close, unit, arrow+chg_str, int(vol or 0)))
        L.append("")
    if cn_wx:
        L.append("  城市天气:")
        for row in cn_wx:
            city, temp, text, hum, wdir, wscale = row
            tag = " 🔥" if (temp or 0) > 35 else " ❄️" if (temp or 0) < 0 else ""
            L.append("  {} {}°C {} 湿度{}%{}{}".format(city, temp, text, hum, tag, ""))
        L.append("")
    L.append("  数据源: Tushare(2000积分) + 和风天气(50K次/月免费)")

    # ═════════════ ⑥ 总结 ═════════════
    L.append("")
    L.append("━" * 55)
    L.append("📝 ⑥ 总结（risk-on/off + 主导因子 + 主线资产）")
    L.append("")
    if signals:
        summary = signals["summary"]
        regime = summary["regime"]
        regime_icon = "🟢" if regime == "risk-on" else "🔴" if regime == "risk-off" else "🟡"
        L.append("  市场状态: {} {}".format(regime_icon, regime.upper()))
        L.append("  主导因子: {}".format(summary["dominant"]))
        L.append("  主线资产: {}".format(summary["leader"]))
    else:
        L.append("  ⚠️ 三因子模块未加载")

    # ═════════════ F区：实时快讯 ═════════════
    L.append("")
    L.append("━" * 55)
    L.append("⚡ F区 · 实时快讯（Top 5）")
    L.append("")
    if HAS_JIN10:
        try:
            flashes = get_latest_flash(5)
            if flashes:
                for i, f_item in enumerate(flashes, 1):
                    ft = f_item.get("time", "")[:16].replace("T", " ")
                    content_text = f_item.get("content", "")
                    if len(content_text) > 120:
                        content_text = content_text[:120] + "..."
                    L.append("  {}. [{}] {}".format(i, ft, content_text))
                L.append("")
                L.append("  数据源: 金十数据MCP · 实时快讯")
            else:
                L.append("  暂无最新快讯")
        except Exception as e:
            L.append("  ⚠️ 金十快讯获取失败: {}".format(str(e)[:50]))
    else:
        L.append("  金十数据未配置")

    # ═════════════ 预警 ═════════════
    alerts_list = []
    if vix_px and vix_px > 25: alerts_list.append(f"VIX={vix_px:.1f}>25")
    if gold_cot and gold_cot >= 90: alerts_list.append(f"黄金COT={gold_cot:.0f}>90极度拥挤")
    if gold_cot and gold_cot <= 10: alerts_list.append(f"黄金COT={gold_cot:.0f}<10极度悲观")
    try:
        t = float(tips_v) if tips_v!="—" else 0
        if t < -0.5: alerts_list.append(f"TIPS={tips_v}%负利率")
        if t > 3: alerts_list.append(f"TIPS={tips_v}%高利率压制")
    except Exception: pass

    if alerts_list:
        L.append("")
        L.append("━" * 55)
        L.append("⚠️ 预警信号")
        for a in alerts_list: L.append("  · " + a)

    # ═════════════ 附表 ═════════════
    L.append("")
    L.append("━" * 55)
    L.append("📋 数据附表")
    L.append("")
    L.append("| 指标 | 数值 | 日期 |" )
    L.append("|------|------|------|")
    rows = [
        ("ICE DXY", fmt(dxy_px), dxy_dt[:10] if dxy_dt else TODAY),
        ("黄金", f"${fmt(gold_px,0)}", gold_dt[:10] if gold_dt else TODAY),
        ("白银", f"${fmt(silver_px,2)}", silver_dt[:10] if silver_dt else TODAY),
        ("伦锡", f"{fmt(tin_px,0)}", TODAY),
        ("WTI原油", f"${fmt(wti_px)}", wti_dt[:10] if wti_dt else TODAY),
        ("Brent原油", f"${fmt(brent_px)}", brent_dt[:10] if brent_dt else TODAY),
        ("VIX", fmt(vix_px,1), vix_dt[:10] if vix_dt else TODAY),
        ("10Y美债", f"{dgs10_v}%", dgs10_d[:10]),
        ("TIPS实际利率", f"{tips_v}%", tips_d[:10]),
    ]
    for name, val, dt in rows:
        L.append(f"| {name} | {val} | {dt} |")
    _append_freshness_table(L)

    L.append("")
    L.append("  数据: FRED, Yahoo, CFTC, Open-Meteo, EIA, 金十数据, Tushare, 和风天气")
    L.append("  模型: 三因子 USD/Liquidity/Demand → Gold/Silver/Tin/Oil + 农业天气")
    L.append("  生成: " + NOW.strftime("%Y-%m-%d %H:%M") + " CST · 不构成投资建议")

    _append_financial_risk_monitor(L, dxy_px, dxy_dt, tips_v, tips_d, dgs10_v, dgs10_d)

    report = "\n".join(L)

    # ═══════ 输出 ═══════
    outdir = Path.home() / "hermes-macro-data" / "reports"
    outdir.mkdir(parents=True, exist_ok=True)
    outpath = outdir / ("daily_" + TODAY + ".md")
    outpath.write_text(report, encoding="utf-8")
    print("日报: " + str(outpath))

    # 存档异常信号供周报使用
    sigdir = Path.home() / "hermes-macro-data" / "signals"
    sigdir.mkdir(parents=True, exist_ok=True)
    sigfile = sigdir / (TODAY + ".txt")
    sig_lines = [f"date={TODAY}"]
    if signals:
        factors = signals["factors"]
        assets = signals["assets"]
        summary = signals["summary"]
        sig_lines.append("factors=USD:{:.2f};Liquidity:{:.2f};Demand:{:.2f}".format(
            factors["USD"], factors["Liquidity"], factors["Demand"]))
        sig_lines.append("assets=" + ";".join(f"{k}:{v['dir']}:{v['score']:+.2f}" for k,v in assets.items()))
        sig_lines.append("regime={};dominant={};leader={}".format(
            summary["regime"], summary["dominant"], summary["leader"]))
    if alerts_list: sig_lines.append("alerts=" + ";".join(alerts_list))
    sig_lines.append(f"gold={gold_px}|{gold_chg}|silver={silver_px}|{silver_chg}|tin={tin_px}|{tin_chg}|wti={wti_px}|{wti_chg}")
    sigfile.write_text("\n".join(sig_lines), encoding="utf-8")
    print("信号存档: " + str(sigfile))


if __name__ == "__main__":
    main()
