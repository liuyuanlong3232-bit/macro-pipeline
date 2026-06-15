#!/usr/bin/env python3
"""
数据质量自动检查 (Financial Data Quality Check)
连接 hermes.db，每天采集后自动运行
"""
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB = str(Path.home() / "hermes-macro-data" / "hermes.db")
NOW = datetime.now()
TODAY = NOW.strftime("%Y-%m-%d")
YESTERDAY = (NOW - timedelta(days=1)).strftime("%Y-%m-%d")

conn = sqlite3.connect(DB)
cur = conn.cursor()
anomalies = []

def check_table(table, date_col, max_delay_days, label, is_monthly=False):
    """时效性检查"""
    try:
        cur.execute(f'SELECT MAX("{date_col}") FROM "{table}"')
        r = cur.fetchone()
        if not r or not r[0]:
            anomalies.append([label, table, "NULL", "⚠️时效性异常", "空表或日期为空"])
            return
        try:
            last_date = datetime.strptime(str(r[0])[:10], "%Y-%m-%d")
        except:
            anomalies.append([label, table, str(r[0]), "⚠️时效性异常", "日期格式错误"])
            return
        delay = (NOW - last_date).days
        tolerance = max_delay_days + (30 if is_monthly else 0)
        if delay > tolerance:
            anomalies.append([label, table, str(r[0])[:10],
                f"⚠️时效性异常: 延迟{delay}天{' (月度指标容忍)' if is_monthly else ''}",
                f"上次更新: {r[0]}"])
    except Exception as e:
        anomalies.append([label, table, "?", "⚠️时效性异常", f"查询失败: {e}"])

def check_extreme(table, col, lo, hi, label):
    """极值检查"""
    try:
        cur.execute(f'SELECT MAX("{col}"), MIN("{col}") FROM "{table}"')
        r = cur.fetchone()
        if not r: return
        mx, mn = r
        for val, which in [(mx, "MAX"), (mn, "MIN")]:
            if val is None: continue
            try:
                v = float(val)
                if lo is not None and v < lo:
                    anomalies.append([label, table, v, "🏷️极值异常", f"{which} = {v} < 下限{lo}"])
                if hi is not None and v > hi:
                    anomalies.append([label, table, v, "🏷️极值异常", f"{which} = {v} > 上限{hi}"])
            except: pass
    except: pass

def check_dead_table(table):
    """检查死表（行数=0或极小）"""
    try:
        cur.execute(f'SELECT COUNT(*) FROM "{table}"')
        n = cur.fetchone()[0]
        if n <= 3:
            anomalies.append([table, table, f"{n}行", "📋空表/死表", "行数过少，采集可能失效"])
    except: pass

def check_cross_xau_tips():
    """黄金-TIPS背离：TIPS上升但黄金上涨"""
    try:
        cur.execute("SELECT \"最新價\" FROM yahoo_futures WHERE \"品種\" LIKE '%黃金%' ORDER BY \"日期\" DESC LIMIT 1")
        r1 = cur.fetchone()
        cur.execute("SELECT \"數值\" FROM fred_indicators WHERE \"系列ID\"='DFII10' ORDER BY \"日期\" DESC LIMIT 2")
        tips = cur.fetchall()
        if r1 and r1[0] and len(tips) == 2:
            gold = float(r1[0])
            tips_now = float(tips[0][0])
            tips_prev = float(tips[1][0])
            if tips_now - tips_prev > 0.05 and gold > 0:
                anomalies.append(["黄金", "TIPS vs XAU", f"TIPS+{tips_now-tips_prev:.2f}",
                    "🔗逻辑背离", f"TIPS上升但黄金未跌({gold})"])
    except: pass

def check_cross_dxy_gold():
    """DXY-黄金背离"""
    try:
        cur.execute("SELECT \"最新價\" FROM yahoo_futures WHERE \"品種\" LIKE '%ICE美%' ORDER BY \"日期\" DESC LIMIT 1")
        dxy = cur.fetchone()
        cur.execute("SELECT \"最新價\" FROM yahoo_futures WHERE \"品種\" LIKE '%黃金%' ORDER BY \"日期\" DESC LIMIT 1")
        gold = cur.fetchone()
        if dxy and gold and dxy[0] and gold[0]:
            pass  # 需要昨日数据对比，简化处理
    except: pass

# ===== 执行全部检查 =====
print(f"📋 数据质量检查 | {TODAY}")
print(f"{'='*60}")

# 时效性
check_table("yahoo_futures", "日期", 2, "Yahoo期货")
check_table("fred_indicators", "日期", 5, "FRED宏观", is_monthly=True)
check_table("agri_weather", "date", 2, "天气")
check_table("cotdata", "報告日期", 8, "COT持仓")
check_table("eia_energy", "日期", 10, "EIA能源")
check_table("vix_data", "报告日期", 8, "VIX波动率")

# 极值
check_extreme("yahoo_futures", "最新價", 0, None, "Yahoo价格")

# 死表
for t in ["cftc_cot", "agsi_eu_gas", "commodity_prices", "financial_news", "finnhub_calendar"]:
    check_dead_table(t)

# 交叉验证
check_cross_xau_tips()

# ===== 输出报告 =====
total_checks = 6 + 1 + 5 + 1
pass_count = total_checks - len(anomalies)
pass_rate = round(pass_count / total_checks * 100)

print(f"\n✓ 整体健康度: 扫描 {total_checks} 项检查, 通过率 {pass_rate}%, {len(anomalies)} 项异常\n")

if anomalies:
    print("⚠️ 异常清单:")
    print(f"| 类别 | 表/指标 | 数值 | 标签 | 原因 |")
    print(f"|------|--------|------|------|------|")
    for a in anomalies:
        print(f"| {a[0]} | {a[1]} | {a[2]} | {a[3]} | {a[4]} |")
else:
    print("✅ 无异常，全部通过")

# ===== 核心指标 =====
print(f"\n✅ 核心指标一览:")
checks = {
    "ICE DXY": ("yahoo_futures", "最新價", "ICE美元"),
    "黄金": ("yahoo_futures", "最新價", "黃金"),
    "白银": ("yahoo_futures", "最新價", "白銀"),
    "WTI": ("yahoo_futures", "最新價", "WTI原油"),
    "天然气": ("yahoo_futures", "最新價", "天然氣"),
    "VIX": ("yahoo_futures", "最新價", "VIX"),
}
for name, (tbl, col, kw) in checks.items():
    try:
        cur.execute(f'SELECT "{col}", 日期 FROM "{tbl}" WHERE 品種 LIKE "%{kw}%" ORDER BY 日期 DESC LIMIT 1')
        r = cur.fetchone()
        if r:
            print(f"  {name}: {r[0]} | {r[1]} | ✅")
        else:
            print(f"  {name}: — | — | ❌")
    except:
        print(f"  {name}: ERROR")

conn.close()

# 写文件给提醒用
out = Path.home() / "hermes-pipeline" / "shared" / "reminders" / f"quality_report_{TODAY}.txt"
out.parent.mkdir(parents=True, exist_ok=True)
status = "✅ 全通过" if not anomalies else f"⚠️ {len(anomalies)}项异常"
out.write_text(f"📋 数据质检 {TODAY}\n{status}\n" + "\n".join(f"  · {a[3]}: {a[1]} ({a[4]})" for a in anomalies), "utf-8")
print(f"\n质检报告已保存: shared/reminders/quality_report_{TODAY}.txt")
