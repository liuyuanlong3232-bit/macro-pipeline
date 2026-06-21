#!/usr/bin/env python3
"""
宏观日报 v1.1 — 三因子信号系统
新结构:
  1. Raw Data（偏离值）
  2. Event Layer（金十财经日历）
  3. 三因子模型（USD/Liquidity/Demand分数）
  4. 资产模型（Gold/Silver/Tin/Oil信号）
  5. 信号输出（↑↓ + score）
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
    from jin10_api import get_weekly_calendar, get_latest_flash
    HAS_JIN10 = True
except ImportError:
    HAS_JIN10 = False

# 动态定位项目根目录
PIPELINE_ROOT = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, PIPELINE_ROOT)

# 导入三因子信号模块
try:
    from macro_signal import calc_all_signals
    HAS_SIGNAL = True
except ImportError:
    HAS_SIGNAL = False
    print("⚠️ macro_signal 模块未找到，三因子功能禁用")

NOW = datetime.now()
TODAY = NOW.strftime("%Y-%m-%d")
DB = str(Path.home() / "hermes-macro-data" / "hermes.db")

# ═══════ 工具函数 ═══════
def db_one(sql, params=None):
    try:
        conn = sqlite3.connect(DB); cur = conn.cursor()
        cur.execute(sql, params or ()); r = cur.fetchone(); conn.close(); return r
    except Exception: return None

def gv(series_id):
    r = db_one('SELECT "數值", "日期" FROM fred_indicators WHERE "系列ID"=? ORDER BY "日期" DESC LIMIT 1', (series_id,))
    return (str(r[0]), str(r[1])) if r else ("—", "—")

def yv(kw):
    r = db_one('SELECT "最新價", "日漲跌幅%", "日期" FROM yahoo_futures WHERE "品種" LIKE ? ORDER BY "日期" DESC LIMIT 1', (f"%{kw}%",))
    if r and r[0]: return (float(r[0]), str(r[1] if r[1] else "0"), str(r[2]) if r[2] else "")
    return (None, "", "")

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

# ═══════ 主函数 ═══════

def main():
    """主函数：拉取数据、组装报告"""
    # ── 基础数据 ──
    dxy_px, dxy_chg, dxy_dt = yv("ICE美元")
    gold_px, gold_chg, gold_dt = yv("黃金期貨")
    silver_px, silver_chg, silver_dt = yv("白銀期貨")
    tin_px, tin_chg = tin_v()
    vix_px, vix_chg, vix_dt = yv("VIX恐慌")
    dgs10_v, dgs10_d = gv("DGS10"); tips_v, tips_d = gv("DFII10")
    gold_cot = cv("黄金"); silver_cot = cv("白银")
    ff_v, ff_d = gv("FEDFUNDS"); cpi_v, cpi_d = gv("CPIAUCSL")
    unemp_v, unemp_d = gv("UNRATE")
    wti_px, wti_chg, wti_dt = yv("WTI原油")
    brent_px, brent_chg, brent_dt = yv("Brent原油")
    
    # ── 获取三因子信号 ──
    signals = None
    if HAS_SIGNAL:
        try:
            signals = calc_all_signals()
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
    L.append("  DXY: {} ({}) | 10Y: {}% | TIPS: {}%".format(
        fmt(dxy_px), chg_s(dxy_chg), dgs10_v, tips_v))
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

    # ═════════════ ③ 三因子模型 ═════════════
    L.append("")
    L.append("━" * 55)
    L.append("🧮 ③ 三因子模型（USD/Liquidity/Demand分数）")
    L.append("")
    if signals:
        factors = signals["factors"]
        L.append("  USD:       {:+.2f}  ({})".format(
            factors["USD"], "美元强势" if factors["USD"] > 0 else "美元弱势"))
        L.append("  Liquidity: {:+.2f}  ({})".format(
            factors["Liquidity"], "流动性充裕" if factors["Liquidity"] > 0 else "流动性紧张"))
        L.append("  Demand:    {:+.2f}  ({})".format(
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

    L.append("")
    L.append("  数据: FRED, Yahoo, CFTC, Akshare, EIA, 金十数据")
    L.append("  模型: 三因子 USD/Liquidity/Demand → Gold/Silver/Tin/Oil")
    L.append("  生成: " + NOW.strftime("%Y-%m-%d %H:%M") + " CST · 不构成投资建议")

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
