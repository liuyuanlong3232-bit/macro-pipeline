#!/usr/bin/env python3
"""
贵金属日报生成器 v2 — 智能化改造
三标签体系 (Core/Trend/Alert) + 三段式输出 + 发前自检
"""
import sys, sqlite3, re
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, "/root/hermes-pipeline")

NOW = datetime.now()
TODAY = NOW.strftime("%Y-%m-%d")
DB = str(Path.home() / "hermes-macro-data" / "hermes.db")

# ══════════════════════════════════════════════════════
# 工具函数
# ══════════════════════════════════════════════════════

def db_one(sql, params=None):
    try:
        conn = sqlite3.connect(DB); cur = conn.cursor()
        cur.execute(sql, params or ())
        r = cur.fetchone(); conn.close(); return r
    except: return None

def db_all(sql, params=None):
    try:
        conn = sqlite3.connect(DB); cur = conn.cursor()
        cur.execute(sql, params or ())
        r = cur.fetchall(); conn.close(); return r
    except: return []

def gv(series_id):
    """读FRED指标 (值, 日期)"""
    r = db_one('SELECT "數值", "日期" FROM fred_indicators WHERE "系列ID"=? ORDER BY "日期" DESC LIMIT 1', (series_id,))
    return (str(r[0]), str(r[1])) if r else ("—", "—")

def yv(kw):
    """读Yahoo期货 (价格, 涨跌幅%, 日期)"""
    r = db_one('SELECT "最新價", "日漲跌幅%", "日期" FROM yahoo_futures WHERE "品種" LIKE ? ORDER BY "日期" DESC LIMIT 1', (f"%{kw}%",))
    if r and r[0]:
        return (float(r[0]), str(r[1] if r[1] else "0"), str(r[2]) if r[2] else "")
    return (None, "", "")

def cv(kw):
    """读COT Index"""
    r = db_one('SELECT "COT Index(26W)" FROM cotdata WHERE "品種" LIKE ? LIMIT 1', (f"%{kw}%",))
    return float(r[0]) if r and r[0] else None

def vix_price():
    """VIX实时价格(Yahoo)"""
    r = db_one('SELECT "最新價" FROM yahoo_futures WHERE "品種" LIKE "%VIX%" ORDER BY "日期" DESC LIMIT 1')
    return float(r[0]) if r and r[0] else None

def cot_report_date():
    """COT最近报告日期"""
    r = db_one('SELECT "報告日期" FROM cotdata ORDER BY "報告日期" DESC LIMIT 1')
    return str(r[0])[:10] if r and r[0] else None

def cot_next_update():
    """计算距下次COT更新还有几天。CFTC每周五发布，cotdata次日可查。"""
    today = NOW.date()
    # 找到下一个周六（美国周五发布，北京周六凌晨可用）
    days_until_sat = (5 - today.weekday()) % 7  # weekday: 0=Mon, 5=Sat
    if days_until_sat == 0:
        days_until_sat = 7
    return days_until_sat

def table_count(table):
    r = db_one(f'SELECT COUNT(*) FROM "{table}"')
    return r[0] if r else 0

def chg_str(v, threshold=2.0):
    """涨跌幅格式化，超过阈值高亮"""
    try:
        pct = float(v)
        arrow = "🔺" if pct > 0 else "🔻" if pct < 0 else ""
        alert = " ⚠️波动异常" if abs(pct) > threshold else ""
        return f"{arrow}{pct:+.2f}%{alert}"
    except:
        return "—"


# ══════════════════════════════════════════════════════
# 第一阶段：发前自检
# ══════════════════════════════════════════════════════

preflight_errors = []

# 1. Core数据完整性
core_checks = {
    "ICE DXY": ("yahoo_futures", "品種", "%ICE美元%"),
    "黄金": ("yahoo_futures", "品種", "%黃金期貨%"),
    "白银": ("yahoo_futures", "品種", "%白銀期貨%"),
    "WTI": ("yahoo_futures", "品種", "%WTI原油%"),
    "VIX": ("yahoo_futures", "品種", "%VIX%"),
}
for name, (tbl, col, kw) in core_checks.items():
    r = db_one(f'SELECT COUNT(*) FROM "{tbl}" WHERE "{col}" LIKE ?', (kw,))
    if not r or r[0] == 0:
        preflight_errors.append(f"⚠️ 今日缺少{name}数据，请检查采集源！")

# 2. 时效性检查
for tbl, col, label, max_delay in [
    ("yahoo_futures", "日期", "Yahoo期货", 2),
    ("fred_indicators", "日期", "FRED宏观", 5),
    ("agri_weather", "date", "天气", 2),
]:
    r = db_one(f'SELECT MAX("{col}") FROM "{tbl}"')
    if r and r[0]:
        try:
            last = datetime.strptime(str(r[0])[:10], "%Y-%m-%d")
            delay = (NOW - last).days
            if delay > max_delay:
                preflight_errors.append(f"⚠️ {label}延迟{delay}天（上次:{r[0]}）")
        except: pass

# 3. 异常值检测 (>2%波动的核心指标)
anomaly_items = []
for name, kw in [("黄金", "黃金"), ("白银", "白銀"), ("WTI", "WTI原油"), ("DXY", "ICE美元")]:
    px, chg, dt = yv(kw)
    try:
        pct = float(chg)
        if abs(pct) > 2:
            anomaly_items.append(f"⚠️ {name}单日波动{pct:+.2f}%，异常！")
    except: pass


# ══════════════════════════════════════════════════════
# 第二阶段：数据拉取
# ══════════════════════════════════════════════════════

# ── Core ──
dxy_px, dxy_chg, dxy_dt = yv("ICE美元")
if dxy_px is None:
    r = gv("DTWEXBGS")
    dxy_px, dxy_chg, dxy_dt = (float(r[0]) if r[0]!="—" else 0), "—", r[1]

gold_px, gold_chg, gold_dt = yv("黃金期貨")
silver_px, silver_chg, silver_dt = yv("白銀期貨")
wti_px, wti_chg, wti_dt = yv("WTI原油")
vix_px, vix_chg, vix_dt = yv("VIX恐慌")
dgs10_v, dgs10_d = gv("DGS10")
dgs2_v, dgs2_d = gv("DGS2")
tips_v, tips_d = gv("DFII10")

# ── Trend ──
gold_cot = cv("黄金")
silver_cot = cv("白银")
ff_v, ff_d = gv("FEDFUNDS")
cpi_v, cpi_d = gv("CPIAUCSL")
pce_v, pce_d = gv("PCEPILFE")
unemp_v, unemp_d = gv("UNRATE")
gdp_v, gdp_d = gv("GDP")
m2_v, m2_d = gv("M2SL")
t5y_v, t5y_d = gv("T5YIFR")
t10yie_v, t10y_d = gv("T10YIE")

# ── Alert ──
alerts = []
if vix_px and vix_px > 25:
    alerts.append(f"⚠️ VIX={vix_px:.1f}，超25恐慌线")
if gold_cot is not None and gold_cot >= 90:
    alerts.append(f"⚠️ 黄金COT Index={gold_cot:.0f}，极度拥挤")
if gold_cot is not None and gold_cot <= 10:
    alerts.append(f"⚠️ 黄金COT Index={gold_cot:.0f}，极度悲观")
try:
    t = float(tips_v) if tips_v != "—" else 0
    if t < -0.5:
        alerts.append(f"⚠️ TIPS={tips_v}%，负实际利率")
    if t > 3:
        alerts.append(f"⚠️ TIPS={tips_v}%，高实际利率压制")
except: pass

# ── 金银比 ──
gsr = gold_px / silver_px if (gold_px and silver_px) else None

# ── FedWatch ──
fed_hold = "—"
try:
    import requests; r = requests.get("https://oddpool.com/api/fedwatch", timeout=8)
    if r.status_code == 200: fed_hold = str(r.json().get("hold", "?")) + "%"
except: pass

# ── DB统计 ──
fr_rows = table_count("fred_indicators")
yah_rows = table_count("yahoo_futures")
wx_rows = table_count("agri_weather")
db_total = fr_rows + yah_rows + wx_rows

# ── COT更新日 ──
cot_days = cot_next_update()
cot_date = cot_report_date()


# ══════════════════════════════════════════════════════
# 第三阶段：一句话点评
# ══════════════════════════════════════════════════════

comment_parts = []

# DXY方向
try:
    dxy_c = float(dxy_chg) if dxy_chg and dxy_chg != "—" else 0
    if dxy_c < -0.3: comment_parts.append("美元走弱")
    elif dxy_c > 0.3: comment_parts.append("美元走强")
except: pass

# TIPS方向
try:
    t_val = float(tips_v) if tips_v != "—" else 2
    if t_val > 2: comment_parts.append("实际利率偏高")
    elif t_val < 1: comment_parts.append("实际利率下行")
except: pass

# COT
if gold_cot is not None and gold_cot >= 90:
    comment_parts.append("COT极度拥挤")

# 综合
if not comment_parts:
    comment_parts.append("宏观信号中性")

comment = "，".join(comment_parts) + "。"


# ══════════════════════════════════════════════════════
# 第四阶段：组装报告
# ══════════════════════════════════════════════════════

def fmt(v, dp=2):
    """安全格式化数字"""
    if v is None: return "—"
    try: return f"{float(v):,.{dp}f}"
    except: return str(v)

L = []

# ── 报头 ──
L.append("📅 贵金属日报 | " + TODAY)
L.append("━" * 50)
L.append("")

# 飞前错误
if preflight_errors:
    L.append("⚠️ 数据采集异常：")
    for e in preflight_errors:
        L.append("   " + e)
    L.append("")
else:
    L.append("⚙️ 系统状态: ✅ 数据完整 | COT距下次更新" + str(cot_days) + "天")
    L.append("")

# ═══════════════════ 🔴 Core ═══════════════════
L.append("🔴 今日核心信号")
L.append("")

# 构建Core信号行
core_lines = []
if dxy_px:
    core_lines.append("ICE DXY {:.2f} ({})".format(dxy_px, chg_str(dxy_chg)))
if gold_px:
    core_lines.append("黄金 ${:,.0f} ({})".format(gold_px, chg_str(gold_chg)))
if silver_px:
    core_lines.append("白银 ${:.2f} ({})".format(silver_px, chg_str(silver_chg)))
if wti_px:
    core_lines.append("WTI ${:.2f} ({})".format(wti_px, chg_str(wti_chg)))
if vix_px:
    vix_tag = " ⚡高" if vix_px > 25 else (" ✅" if vix_px < 20 else "")
    core_lines.append("VIX {:.2f}{}".format(vix_px, vix_tag))
core_lines.append("10Y {}%  |  TIPS {}%".format(dgs10_v, tips_v))

L.append("  " + "  |  ".join(core_lines))
L.append("")
L.append("  💬 " + comment)
L.append("")

# 异常高亮
if anomaly_items:
    for a in anomaly_items:
        L.append("  " + a)
    L.append("")

# ═══════════════════ ⚙️ 系统 ═══════════════════
L.append("━" * 50)
L.append("⚙️ 系统运行状态")
L.append("")
L.append("  📊 今日入库: {}条 (FRED {} + Yahoo {} + 天气 {})".format(db_total, fr_rows, yah_rows, wx_rows))
status_line = "  🔍 核心数据: " + ("✅ 完整" if not preflight_errors else "❌ 有缺失")
L.append(status_line)
L.append("  📅 COT数据: {} ({}天前, 下次周{}更新)".format(cot_date or "?", (NOW-datetime.strptime(cot_date,"%Y-%m-%d")).days if cot_date else 0, "六"))
L.append("")

# ═══════════════════ 🟡 Trend ═══════════════════
L.append("━" * 50)
L.append("🟡 宏观趋势信号")
L.append("")
L.append("| 指标 | 当前值 | 信号 | 方向 |")
L.append("|------|--------|------|------|")
sig_v = "↓宽松" if ff_v and ff_v!="—" and float(ff_v)<3 else "→中性" if ff_v and ff_v!="—" and float(ff_v)<5 else "↑紧缩"
L.append("| 联邦基金利率 | {}% | {} | {} |".format(ff_v, sig_v, ff_d[:7] if ff_d!="—" else "—"))
sig_cpi = "↑通胀" if cpi_v!="—" and float(cpi_v)>4 else "→温和" if cpi_v!="—" else "—"
L.append("| CPI | {} | {} | {} |".format(cpi_v, sig_cpi, cpi_d[:7] if cpi_d!="—" else "—"))
sig_unemp = "↑恶化" if unemp_v!="—" and float(unemp_v)>5 else "→正常" if unemp_v!="—" else "—"
L.append("| 失业率 | {}% | {} | {} |".format(unemp_v, sig_unemp, unemp_d[:7] if unemp_d!="—" else "—"))
sig_t5y = "↑预期" if t5y_v!="—" and float(t5y_v)>3 else "→中性" if t5y_v!="—" else "—"
L.append("| 5Y通胀预期 | {}% | {} | {} |".format(t5y_v, sig_t5y, t5y_d[:7] if t5y_d!="—" else "—"))
sig_m2 = "↑扩张" if m2_v!="—" else "—"
L.append("| M2 | {} | {} | {} |".format(m2_v, sig_m2, m2_d[:7] if m2_d!="—" else "—"))
L.append("")

# COT
L.append("| COT持仓 | Index | 信号 | 报告日期 |")
L.append("|---------|-------|------|---------|")
if gold_cot is not None:
    gcot_sig = "极度看多" if gold_cot>=90 else "看多" if gold_cot>=70 else "中性" if gold_cot>=30 else "看空" if gold_cot>=10 else "极度看空"
    L.append("| 黄金 | {:.0f} | {} | {} |".format(gold_cot, gcot_sig, cot_date or "?"))
if silver_cot is not None:
    scot_sig = "极度看多" if silver_cot>=90 else "看多" if silver_cot>=70 else "中性" if silver_cot>=30 else "看空" if silver_cot>=10 else "极度看空"
    L.append("| 白银 | {:.0f} | {} | {} |".format(silver_cot, scot_sig, cot_date or "?"))
L.append("")

# ═══════════════════ 🟢 Alert ═══════════════════
if alerts:
    L.append("━" * 50)
    L.append("🟢 预警信号")
    L.append("")
    for a in alerts:
        L.append("  " + a)
    L.append("")

# ═══════════════════ 📋 附表 ═══════════════════
L.append("━" * 50)
L.append("📋 详细数据附表")
L.append("")
L.append("| 指标 | 数值 | 日期 | 标签 |")
L.append("|------|------|------|------|")
rows = [
    ("ICE DXY", "{}".format(fmt(dxy_px)), dxy_dt[:10] if dxy_dt else TODAY, "🔴Core"),
    ("黄金", "${}".format(fmt(gold_px,0)), gold_dt[:10] if gold_dt else TODAY, "🔴Core"),
    ("白银", "${}".format(fmt(silver_px,2)), silver_dt[:10] if silver_dt else TODAY, "🔴Core"),
    ("WTI原油", "${}".format(fmt(wti_px)), wti_dt[:10] if wti_dt else TODAY, "🔴Core"),
    ("VIX", "{}".format(fmt(vix_px,1)), vix_dt[:10] if vix_dt else TODAY, "🔴Core"),
    ("10Y美债", "{}%".format(dgs10_v), dgs10_d[:10], "🔴Core"),
    ("TIPS", "{}%".format(tips_v), tips_d[:10], "🔴Core"),
    ("联邦基金利率", "{}%".format(ff_v), ff_d[:10], "🟡Trend"),
    ("CPI", "{}".format(cpi_v), cpi_d[:10], "🟡Trend"),
    ("核心PCE", "{}".format(pce_v), pce_d[:10], "🟡Trend"),
    ("失业率", "{}%".format(unemp_v), unemp_d[:10], "🟡Trend"),
    ("GDP", "{}".format(gdp_v), gdp_d[:10], "🟡Trend"),
    ("M2", "{}".format(m2_v), m2_d[:10], "🟡Trend"),
    ("5Y通胀预期", "{}%".format(t5y_v), t5y_d[:10], "🟡Trend"),
    ("10Y通胀预期", "{}%".format(t10yie_v), t10y_d[:10], "🟡Trend"),
    ("FOMC维持概率", "{}".format(fed_hold), TODAY, "🟡Trend"),
]
if gsr:
    rows.append(("金银比", "{:.1f}x".format(gsr), TODAY, "🟡Trend"))
for name, val, dt, tag in rows:
    vol_flag = ""
    if "⚠️波动异常" in val:
        vol_flag = " ⚡"
    L.append("| {} | {}{} | {} | {} |".format(name, val, vol_flag, dt, tag))
L.append("")
L.append("  数据来源: FRED, Yahoo Finance, CFTC, Oddpool(FedWatch), Open-Meteo")
L.append("  生成时间: " + NOW.strftime("%Y-%m-%d %H:%M") + " CST")
L.append("  声明: 不构成投资建议，仅供学习参考")

report = "\n".join(L)

# ══════════════════════════════════════════════════════
# 输出 + 发送
# ══════════════════════════════════════════════════════

outdir = Path.home() / "hermes-macro-data" / "reports"
outdir.mkdir(parents=True, exist_ok=True)
outpath = outdir / ("daily_" + TODAY + ".md")
outpath.write_text(report, encoding="utf-8")
print("日报已生成: " + str(outpath))

from send_email import send_report
send_report(str(outpath), "macro")
