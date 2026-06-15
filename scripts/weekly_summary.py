#!/usr/bin/env python3
"""
周报摘要 — 读取本周5天日报信号，自动拼成复盘
周五16:00自动运行（替代所有独立周报）
逻辑: 读 signals/ 目录下本周所有 .txt → 统计异常 → 算周涨跌 → 列下周事件
"""
import sys, re
from pathlib import Path
from datetime import datetime, timedelta

NOW = datetime.now()
TODAY = NOW.strftime("%Y-%m-%d")

# 本周一~周五 (如果今天是周五就用本周，否则用上周)
if NOW.weekday() < 4:  # 还没到周五
    print("[weekly] 不是周五，跳过")
    sys.exit(0)

# 本周一
monday = NOW - timedelta(days=NOW.weekday())
weekdays = [(monday + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(5)]

sigdir = Path.home() / "hermes-macro-data" / "signals"
daily_files = {d: sigdir / (d + ".txt") for d in weekdays}

# 读取所有信号文件
all_anomalies = []
all_alerts = []
prices = {}  # {品种: [(日期, 价格), ...]}

for d, f in daily_files.items():
    if not f.exists(): continue
    for line in f.read_text("utf-8").split("\n"):
        if line.startswith("anomalies="):
            for a in line.split("=",1)[1].split(";"):
                if a: all_anomalies.append(f"{d}:{a}")
        elif line.startswith("alerts="):
            for a in line.split("=",1)[1].split(";"):
                if a: all_alerts.append(f"{d}:{a}")
        elif line.startswith("weather="):
            for w in line.split("=",1)[1].split(";"):
                if w: all_alerts.append(f"{d}:天气-{w}")
        elif "=" in line and "|" in line:
            # gold=4328.1|5.35|silver=70.225|8.71|wti=80.71|-10.35|...
            pairs = line.split("|")
            for pair in pairs:
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    if k in prices: prices[k].append((d, v))
                    else: prices[k] = [(d, v)]

# ═══════ 统计 ═══════
# 异常统计
from collections import Counter
anom_counter = Counter()
for a in all_anomalies:
    # 提取品种名
    name = a.split(":")[-1].split(" ")[0] if ":" in a else a
    anom_counter[name] += 1

alert_counter = Counter()
for a in all_alerts:
    name = a.split(":")[-1][:20]
    alert_counter[name] += 1

# 周涨跌
week_changes = {}
for name, vals in prices.items():
    if len(vals) >= 2:
        try: start = float(vals[0][1]); end = float(vals[-1][1])
        except: continue
        if start and start != 0:
            week_changes[name] = (end - start) / start * 100

# ═══════ 下周事件 ═══════
next_events = []
next_monday = monday + timedelta(days=7)
# 固定事件
next_events.append((next_monday.strftime("%m/%d"), "宏观周报发布"))
next_events.append(((next_monday+timedelta(days=2)).strftime("%m/%d"), "EIA原油库存"))
next_events.append(((next_monday+timedelta(days=3)).strftime("%m/%d"), "USDA出口检验/优良率"))
next_events.append(((next_monday+timedelta(days=4)).strftime("%m/%d"), "CFTC COT持仓"))
# 如果周五有非农日
if next_monday.day <= 7:
    next_events.append(((next_monday+timedelta(days=4)).strftime("%m/%d"), "⚠️月度非农数据"))

# ═══════ 组装周报 ═══════
L = []
L.append("📊 本周宏观与全资产复盘 | " + TODAY)
L.append("━" * 55)
L.append("")

# 1. 焦点
L.append("## 🔥 本周焦点")
L.append("")
if anom_counter:
    top = anom_counter.most_common(3)
    L.append("异常信号最多品种:")
    for name, cnt in top:
        L.append(f"  · {name}: 异常 {cnt} 次")
else:
    L.append("  本周无异常信号，市场平稳")
L.append("")
if alert_counter:
    L.append("预警触发:")
    for a, cnt in alert_counter.most_common(3):
        L.append(f"  · {a}: {cnt}次")

# 2. 趋势总结
L.append("")
L.append("## 📈 本周趋势")
L.append("")
L.append("| 品种 | 周涨跌 | 信号 |")
L.append("|------|--------|------|")
name_map = {"gold":"黄金","silver":"白银","wti":"WTI原油","corn":"玉米","soy":"大豆","wheat":"小麦"}
for k, v in week_changes.items():
    cn = name_map.get(k, k)
    arrow = "🔺" if v > 0 else "🔻" if v < 0 else "➡️"
    sig = "强" if abs(v) > 5 else "中" if abs(v) > 2 else "弱"
    L.append(f"| {cn} | {arrow} {v:+.1f}% | {sig} |")
L.append("")

# 3. 异常日志
if all_anomalies or all_alerts:
    L.append("## ⚠️ 本周异常日志")
    L.append("")
    for a in all_anomalies[-10:]:
        L.append(f"  · {a}")
    for a in all_alerts[-5:]:
        L.append(f"  · {a}")

# 4. 下周关注
L.append("")
L.append("## 📅 下周关注")
L.append("")
for dt, evt in sorted(next_events):
    L.append(f"  · {dt}: {evt}")

L.append("")
L.append("━" * 55)
L.append("  来源: 本周5天日报信号自动聚合")
L.append("  生成: " + NOW.strftime("%Y-%m-%d %H:%M") + " CST")
L.append("  声明: 不构成投资建议")

report = "\n".join(L)

# ═══════ 输出+发送 ═══════
outdir = Path.home() / "hermes-macro-data" / "reports"
outdir.mkdir(parents=True, exist_ok=True)
outpath = outdir / ("weekly_" + TODAY + ".md")
outpath.write_text(report, encoding="utf-8")
print(report)

from send_email import send_report
send_report(str(outpath), "weekly_summary")
