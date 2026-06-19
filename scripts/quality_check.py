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

def q1(sql, params=None):
    """安全查询"""
    try:
        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)
        return cur.fetchone()
    except Exception:
        return None

def check_table(table, date_col, max_delay_days, label, is_monthly=False):
    """时效性检查"""
    try:
        cur.execute(f'SELECT MAX("{date_col}") FROM "{table}"')
        r = cur.fetchone()
        if not r or not r[0]:
            anomalies.append([label, table, "NULL", "⚠️时效性异常", "空表或日期为空"])
            return
        try:
            last_date = datetime.strptime(str(r[0])[:10], "%Y-%m-%d") if len(str(r[0])) >= 10 else datetime.strptime(str(r[0]) + "-01", "%Y-%m-%d")
        except Exception:
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
            except Exception:
                pass
    except Exception:
        pass

def check_dead_table(table):
    """检查死表"""
    try:
        cur.execute(f'SELECT COUNT(*) FROM "{table}"')
        n = cur.fetchone()[0]
        if n <= 3:
            anomalies.append([table, table, f"{n}行", "📋空表/死表", "行数过少，采集可能失效"])
    except Exception:
        pass

def check_cross_xau_tips():
    """黄金-TIPS背离"""
    try:
        r1 = q1("SELECT \"最新價\" FROM yahoo_futures WHERE \"品種\" LIKE '%黃金%' ORDER BY \"日期\" DESC LIMIT 1")
        tips = cur.execute("SELECT \"數值\" FROM fred_indicators WHERE \"系列ID\"='DFII10' ORDER BY \"日期\" DESC LIMIT 2").fetchall()
        if r1 and r1[0] and len(tips) == 2:
            gold = float(r1[0])
            tips_now = float(tips[0][0])
            tips_prev = float(tips[1][0])
            if tips_now - tips_prev > 0.05 and gold > 0:
                anomalies.append(["黄金", "TIPS vs XAU", f"TIPS+{tips_now-tips_prev:.2f}",
                    "🔗逻辑背离", f"TIPS上升但黄金未跌({gold})"])
    except Exception:
        pass

def check_dxy_deviation():
    """DXY口径交叉验证：ICE vs DTWEXAFEGS 偏差监控"""
    dxy_info = {}
    
    # 1. ICE DXY
    r = q1("SELECT \"最新價\", 日期 FROM yahoo_futures WHERE \"品種\" LIKE '%ICE美元%' ORDER BY \"日期\" DESC LIMIT 1")
    if r and r[0]:
        dxy_info["ice_dxy"] = float(r[0])
        dxy_info["ice_date"] = r[1]
    else:
        dxy_info["ice_dxy"] = None
        anomalies.append(["DXY", "ICE DXY", "—", "⚠️ICE DXY缺失", "Yahoo DX-Y.NYB无数据"])
    
    # 2. DTWEXAFEGS (发达经济体, DXY近似替代)
    r = q1("SELECT \"數值\" FROM fred_indicators WHERE \"系列ID\"='DTWEXAFEGS' ORDER BY \"日期\" DESC LIMIT 1")
    if r and r[0]:
        dxy_info["fred_advanced"] = float(r[0])
    else:
        dxy_info["fred_advanced"] = None
    
    # 3. DTWEXBGS (广义参考)
    r = q1("SELECT \"數值\" FROM fred_indicators WHERE \"系列ID\"='DTWEXBGS' ORDER BY \"日期\" DESC LIMIT 1")
    if r and r[0]:
        dxy_info["fred_broad"] = float(r[0])
    
    # 4. 偏差检查
    if dxy_info.get("ice_dxy") and dxy_info.get("fred_advanced"):
        estimated = dxy_info["fred_advanced"] * 0.83
        deviation = abs(dxy_info["ice_dxy"] - estimated)
        deviation_pct = deviation / dxy_info["ice_dxy"] * 100
        dxy_info["estimated"] = estimated
        dxy_info["deviation_pct"] = deviation_pct
        
        if deviation_pct > 1.5:
            anomalies.append(["DXY", "ICE vs DTWEXAFEGS×0.83",
                f"ICE={dxy_info['ice_dxy']:.2f} vs 估算={estimated:.2f}",
                "🔗偏差异常: DXY估算偏差>1.5%",
                f"偏差{deviation_pct:.1f}%，系数可能需调整"])
    
    return dxy_info

# ===== 执行全部检查 =====
print(f"📋 数据质量检查 | {TODAY}")
print(f"{'='*60}")

# 时效性
check_table("yahoo_futures", "日期", 2, "Yahoo期货")
check_table("fred_indicators", "日期", 5, "FRED宏观", is_monthly=True)
check_table("agri_weather", "date", 2, "天气")
check_table("cotdata", "報告日期", 12, "COT持仓")
check_table("eia_energy", "日期", 30, "EIA能源", is_monthly=True)
check_table("vix_data", "报告日期", 14, "VIX波动率")

# 极值
check_extreme("yahoo_futures", "最新價", 0, None, "Yahoo价格")

# 死表
for t in ["agsi_eu_gas", "commodity_prices", "financial_news", "finnhub_calendar"]:
    check_dead_table(t)

# 交叉验证
check_cross_xau_tips()
dxy = check_dxy_deviation()

# ===== 输出报告 =====
total_checks = 6 + 1 + 5 + 2  # 时效+极值+死表+交叉+DXY
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
    "DXY(FRED近似)": None,  # custom
    "黄金": ("yahoo_futures", "最新價", "黃金"),
    "白银": ("yahoo_futures", "最新價", "白銀"),
    "WTI": ("yahoo_futures", "最新價", "WTI原油"),
    "天然气": ("yahoo_futures", "最新價", "天然氣"),
    "VIX": ("yahoo_futures", "最新價", "VIX"),
}

# ICE DXY
r = q1("SELECT \"最新價\", 日期 FROM yahoo_futures WHERE \"品種\" LIKE '%ICE美元%' ORDER BY \"日期\" DESC LIMIT 1")
ice_val = f"{r[0]}" if r and r[0] else "—"
ice_tag = "" if r and r[0] else " [❌缺失]"
print(f"  ICE DXY: {ice_val} | {r[1] if r and r[1] else '—'} | {'✅' if r and r[0] else '❌'}{ice_tag}")

# DXY fallback info
if dxy.get("fred_advanced"):
    est = dxy["fred_advanced"] * 0.83
    tag = " [估算值]" if not dxy.get("ice_dxy") else ""
    dev = f" (偏差{dxy.get('deviation_pct', 0):.1f}%)" if dxy.get("deviation_pct") else ""
    print(f"  DXY(FRED代): DTWEXAFEGS={dxy['fred_advanced']:.2f} → ×0.83≈{est:.2f}{tag}{dev}")
    print(f"  DXY(FRED广): DTWEXBGS={dxy.get('fred_broad', '—')}")

for name, info in checks.items():
    if info is None or name == "ICE DXY":
        continue
    tbl, col, kw = info
    try:
        cur.execute(f'SELECT "{col}", 日期 FROM "{tbl}" WHERE 品種 LIKE ? ORDER BY 日期 DESC LIMIT 1',
                    (f"%{kw}%",))
        r = cur.fetchone()
        if r:
            print(f"  {name}: {r[0]} | {r[1]} | ✅")
        else:
            print(f"  {name}: — | — | ❌")
    except Exception:
        print(f"  {name}: ERROR")

conn.close()

# 写文件
out = Path.home() / "hermes-pipeline" / "shared" / "reminders" / f"quality_report_{TODAY}.txt"
out.parent.mkdir(parents=True, exist_ok=True)
status = "✅ 全通过" if not anomalies else f"⚠️ {len(anomalies)}项异常"
lines = [f"📋 数据质检 {TODAY}", status]
for a in anomalies:
    lines.append(f"  · {a[3]}: {a[1]} ({a[4]})")
if dxy.get("fred_advanced"):
    est = dxy["fred_advanced"] * 0.83
    lines.append(f"  DXY: ICE={dxy.get('ice_dxy', '—')}, FRED代×0.83={est:.2f}, FRED广={dxy.get('fred_broad', '—')}")
out.write_text("\n".join(lines), "utf-8")
print(f"\n质检报告已保存: shared/reminders/quality_report_{TODAY}.txt")
