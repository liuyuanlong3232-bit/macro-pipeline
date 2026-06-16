#!/usr/bin/env python3
"""
贵金属日报生成器 v3 — 全资产作战室
四板块: 贵金属宏观 + 能源 + 农业天气 + 中国农业
智能分级: 每个板块只看 Core，只报异常
"""
import sys, sqlite3
from pathlib import Path
from datetime import datetime, timedelta

# 动态定位项目根目录
PIPELINE_ROOT = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, PIPELINE_ROOT)

NOW = datetime.now()
TODAY = NOW.strftime("%Y-%m-%d")
DB = str(Path.home() / "hermes-macro-data" / "hermes.db")

# ═══════ 工具函数 ═══════
def db_one(sql, params=None):
    try:
        conn = sqlite3.connect(DB); cur = conn.cursor()
        cur.execute(sql, params or ())
        r = cur.fetchone(); conn.close(); return r
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

def cn_weather():
    try:
        conn = sqlite3.connect(DB); cur = conn.cursor()
        cur.execute("SELECT city, temp, text, humidity, wind_dir, wind_scale FROM cn_weather WHERE date=? AND hour='now' ORDER BY city", (TODAY,))
        rows = cur.fetchall(); conn.close(); return rows or []
    except Exception: return []

def cn_futures():
    try:
        conn = sqlite3.connect(DB); cur = conn.cursor()
        cur.execute("SELECT name, close, change_pct, vol, unit FROM cn_futures ORDER BY name")
        rows = cur.fetchall(); conn.close(); return rows or []
    except Exception: return []

# ═══════ 主函数 ═══════

def main():
    """主函数：拉取数据、组装报告、发送邮件"""
    # ── A区：贵金属+宏观 ──
    dxy_px, dxy_chg, dxy_dt = yv("ICE美元")
    if dxy_px is None:
        r = gv("DTWEXBGS"); dxy_px, dxy_chg, dxy_dt = (float(r[0]) if r[0]!="—" else 0), "—", r[1]
    gold_px, gold_chg, gold_dt = yv("黃金期貨")
    silver_px, silver_chg, silver_dt = yv("白銀期貨")
    vix_px, vix_chg, vix_dt = yv("VIX恐慌")
    dgs10_v, dgs10_d = gv("DGS10"); tips_v, tips_d = gv("DFII10")
    gold_cot = cv("黄金"); silver_cot = cv("白银")
    ff_v, ff_d = gv("FEDFUNDS"); cpi_v, cpi_d = gv("CPIAUCSL")
    pce_v, pce_d = gv("PCEPILFE"); unemp_v, unemp_d = gv("UNRATE")
    m2_v, m2_d = gv("M2SL"); t5y_v, t5y_d = gv("T5YIFR")
    t10yie_v, t10y_d = gv("T10YIE")

    # ── B区：能源 ──
    wti_px, wti_chg, wti_dt = yv("WTI原油")
    brent_px, brent_chg, brent_dt = yv("Brent原油")
    ng_px, ng_chg, ng_dt = yv("天然氣")
    eia_crude_date = db_one('SELECT MAX("日期") FROM eia_energy WHERE "類別"="原油庫存"')
    eia_last = str(eia_crude_date[0]) if eia_crude_date and eia_crude_date[0] else "?"

    # ── C区：农业+天气 ──
    corn_px, corn_chg, corn_dt = yv("玉米期貨")
    soy_px, soy_chg, soy_dt = yv("大豆期貨")
    wheat_px, wheat_chg, wheat_dt = yv("小麥期貨")
    soyoil_px, soyoil_chg, soyoil_dt = yv("豆油期貨")
    soymeal_px, soymeal_chg, soymeal_dt = yv("豆粕期貨")
    cotton_px, cotton_chg, cotton_dt = yv("棉花期貨")
    sugar_px, sugar_chg, sugar_dt = yv("糖期貨")
    corn_cot = cv("玉米"); soy_cot = cv("大豆"); wheat_cot = cv("小麦")

    # ── 天气异常检测 ──
    weather_alerts = []
    for region, name in [("US_IL","美中西部IL"), ("US_IA","美中西部IA"), ("BR_MT","巴西MT"), ("AR_BA","阿根廷")]:
        r = db_one('SELECT AVG(precip_mm) FROM agri_weather WHERE region=? AND date >= ?',
                   (region, (NOW-timedelta(days=30)).strftime("%Y-%m-%d")))
        if r and r[0]:
            avg30 = float(r[0])
            if avg30 < 1.0:
                weather_alerts.append(f"⚠️ {name}: 30天均降水 {avg30:.1f}mm（异常偏干）")
            elif avg30 > 8.0:
                weather_alerts.append(f"⚠️ {name}: 30天均降水 {avg30:.1f}mm（异常偏湿）")

    # ── D区：中国农业+天气 ──
    cn_wx = cn_weather()
    cn_ft = cn_futures()
    cn_agri_available = False
    try:
        r = db_one('SELECT COUNT(*) FROM yahoo_futures WHERE "品種" LIKE "%豬%"')
        if r and r[0] > 0: cn_agri_available = True
    except Exception: pass

    # ═══════ 异常收集 ═══════
    anomalies = []
    for name, px, chg in [("黄金", gold_px, gold_chg), ("白银", silver_px, silver_chg),
                            ("WTI", wti_px, wti_chg), ("天然气", ng_px, ng_chg),
                            ("玉米", corn_px, corn_chg), ("大豆", soy_px, soy_chg),
                            ("小麦", wheat_px, wheat_chg)]:
        try:
            if abs(float(chg)) > 2:
                anomalies.append((name, chg))
        except Exception: pass
    if gold_cot and gold_cot >= 90:
        anomalies.append(("黄金COT", "极度拥挤"))
    alerts_list = []
    if vix_px and vix_px > 25: alerts_list.append(f"VIX={vix_px:.1f}>25")
    if gold_cot and gold_cot >= 90: alerts_list.append(f"黄金COT={gold_cot:.0f}>90极度拥挤")
    if gold_cot and gold_cot <= 10: alerts_list.append(f"黄金COT={gold_cot:.0f}<10极度悲观")
    try:
        t = float(tips_v) if tips_v!="—" else 0
        if t < -0.5: alerts_list.append(f"TIPS={tips_v}%负利率")
        if t > 3: alerts_list.append(f"TIPS={tips_v}%高利率压制")
    except Exception: pass

    # ═══════ FedWatch ═══════
    fed_hold = "—"
    try:
        import requests; r = requests.get("https://oddpool.com/api/fedwatch", timeout=8)
        if r.status_code == 200: fed_hold = str(r.json().get("hold", "?"))+"%"
    except Exception: pass

    # ═══════ 组装报告 ═══════
    L = []
    L.append("📅 全资产日报 | " + TODAY)
    L.append("━" * 55)
    L.append("")

    # ━━━ 飞前自检 ━━━
    missing = []
    for name, kw in [("DXY","ICE美元"), ("黄金","黃金"), ("白银","白銀"), ("WTI","WTI原油"), ("VIX","VIX")]:
        if not db_one('SELECT 1 FROM yahoo_futures WHERE "品種" LIKE ? LIMIT 1', (f"%{kw}%",)):
            missing.append(name)
    if missing:
        L.append("⚠️ 缺失: " + ", ".join(missing))
    else:
        L.append("✅ 数据完整 · 全资产就绪")

    # ═════════════ A区 ═════════════
    L.append("")
    L.append("━" * 55)
    L.append("🔴 A区 · 贵金属与宏观")
    L.append("")
    core_items = []
    if dxy_px: core_items.append(f"DXY {fmt(dxy_px)} ({chg_s(dxy_chg)})")
    if gold_px: core_items.append(f"黄金 ${fmt(gold_px,0)} ({chg_s(gold_chg)})")
    if silver_px: core_items.append(f"白银 ${fmt(silver_px,2)} ({chg_s(silver_chg)})")
    if vix_px:
        vtag = " ⚡高" if vix_px>25 else ""
        core_items.append(f"VIX {fmt(vix_px,2)}{vtag}")
    core_items.append(f"10Y {dgs10_v}% | TIPS {tips_v}%")
    L.append("  " + "  ·  ".join(core_items))
    L.append("")
    # COT
    if gold_cot:
        gs = "极度看多" if gold_cot>=90 else "看多" if gold_cot>=70 else "中性" if gold_cot>=30 else "看空" if gold_cot>=10 else "极度看空"
        L.append(f"  COT黄金: {gold_cot:.0f} ({gs}) | COT白银: {silver_cot:.0f}" if silver_cot else f"  COT黄金: {gold_cot:.0f} ({gs})")
    L.append(f"  联邦基金: {ff_v}% | CPI: {cpi_v} | 失业: {unemp_v}% | FOMC维持: {fed_hold}")

    # ═════════════ B区 ═════════════
    L.append("")
    L.append("━" * 55)
    L.append("🛢️ B区 · 能源")
    L.append("")
    if wti_px or brent_px or ng_px:
        energy_core = []
        if wti_px: energy_core.append(f"WTI ${fmt(wti_px)} ({chg_s(wti_chg)})")
        if brent_px: energy_core.append(f"Brent ${fmt(brent_px)} ({chg_s(brent_chg)})")
        if ng_px: energy_core.append(f"天然气 ${fmt(ng_px,3)} ({chg_s(ng_chg)})")
        L.append("  " + "  ·  ".join(energy_core))
        L.append(f"  EIA库存: {eia_last}")
        energy_anom = []
        try:
            if abs(float(wti_chg)) > 3: energy_anom.append(f"WTI波动{float(wti_chg):+.1f}%")
            if abs(float(ng_chg)) > 5: energy_anom.append(f"天然气暴动{float(ng_chg):+.1f}%")
        except Exception: pass
        if energy_anom: L.append("  ⚠️ " + " · ".join(energy_anom))
    else:
        L.append("  板块正常，无异常波动")

    # ═════════════ C区 ═════════════
    L.append("")
    L.append("━" * 55)
    L.append("🌾 C区 · 农业与天气")
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
        if weather_alerts:
            L.append("  ☀️ 天气预警:")
            for wa in weather_alerts: L.append("    " + wa)
        else:
            L.append("  ☀️ 产区天气正常")
    else:
        L.append("  板块正常，无异常波动")

    # ═════════════ D区 ═════════════
    L.append("")
    L.append("━" * 55)
    L.append("🐷 D区 · 中国农业")
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
    L.append("  不构成投资建议 · 仅供学习参考")

    # ═════════════ 预警 ═════════════
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
    L.append("| 板块 | 指标 | 数值 | 日期 |")
    L.append("|------|------|------|------|")
    rows = [
        ("A区", "ICE DXY", fmt(dxy_px), dxy_dt[:10] if dxy_dt else TODAY),
        ("A区", "黄金", f"${fmt(gold_px,0)}", gold_dt[:10] if gold_dt else TODAY),
        ("A区", "白银", f"${fmt(silver_px,2)}", silver_dt[:10] if silver_dt else TODAY),
        ("A区", "VIX", fmt(vix_px,1), vix_dt[:10] if vix_dt else TODAY),
        ("A区", "10Y美债", f"{dgs10_v}%", dgs10_d[:10]),
        ("A区", "TIPS实际利率", f"{tips_v}%", tips_d[:10]),
        ("B区", "WTI原油", f"${fmt(wti_px)}", wti_dt[:10] if wti_dt else TODAY),
        ("B区", "Brent原油", f"${fmt(brent_px)}", brent_dt[:10] if brent_dt else TODAY),
        ("B区", "天然气", f"${fmt(ng_px,3)}", ng_dt[:10] if ng_dt else TODAY),
        ("C区", "玉米", f"{fmt(corn_px)}¢", corn_dt[:10] if corn_dt else TODAY),
        ("C区", "大豆", f"{fmt(soy_px)}¢", soy_dt[:10] if soy_dt else TODAY),
        ("C区", "小麦", f"{fmt(wheat_px)}¢", wheat_dt[:10] if wheat_dt else TODAY),
    ]
    for block, name, val, dt in rows:
        L.append(f"| {block} | {name} | {val} | {dt} |")

    L.append("")
    L.append("  数据: FRED, Yahoo Finance, CFTC, Open-Meteo, EIA, 和风天气")
    L.append("  生成: " + NOW.strftime("%Y-%m-%d %H:%M") + " CST · 不构成投资建议")

    report = "\n".join(L)

    # ═══════ 输出 ═══════
    outdir = Path.home() / "hermes-macro-data" / "reports"
    outdir.mkdir(parents=True, exist_ok=True)
    outpath = outdir / ("daily_" + TODAY + ".md")
    outpath.write_text(report, encoding="utf-8")
    print("日报: " + str(outpath))

    # ═══════ 邮件(容错) ═══════
    try:
        from send_email import send_report
        send_report(str(outpath), "macro")
    except Exception as e:
        print("邮件发送失败(不影响日报生成): " + str(e))

    # ═══════ 输出摘要(供本地Hermes读取) ═══════
    print("")
    print("=" * 50)
    print(report[:500])

    # 存档异常信号供周报使用
    sigdir = Path.home() / "hermes-macro-data" / "signals"
    sigdir.mkdir(parents=True, exist_ok=True)
    sigfile = sigdir / (TODAY + ".txt")
    sig_lines = [f"date={TODAY}"]
    if anomalies: sig_lines.append("anomalies="+";".join(f"{n}:{v}" for n,v in anomalies))
    if alerts_list: sig_lines.append("alerts="+";".join(alerts_list))
    if weather_alerts: sig_lines.append("weather="+";".join(weather_alerts))
    sig_lines.append(f"gold={gold_px}|{gold_chg}|silver={silver_px}|{silver_chg}|wti={wti_px}|{wti_chg}|corn={corn_px}|{corn_chg}|soy={soy_px}|{soy_chg}|wheat={wheat_px}|{wheat_chg}")
    sigfile.write_text("\n".join(sig_lines), encoding="utf-8")
    print("信号存档: " + str(sigfile))


if __name__ == "__main__":
    main()
