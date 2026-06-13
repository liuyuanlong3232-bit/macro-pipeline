#!/usr/bin/env python3
"""生成报告用图表 - 基于SQLite数据库（含15年历史数据）"""
import os, sys
from pathlib import Path
from datetime import datetime, timedelta
import sqlite3
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.dates as mdates
import numpy as np

DB = Path.home() / "hermes-macro-data" / "hermes.db"
CHART_DIR = Path.home() / "hermes-macro-data" / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)

zh_fonts = [f.name for f in fm.fontManager.ttflist if "Noto Sans CJK" in f.name]
zh = zh_fonts[0] if zh_fonts else "DejaVu Sans"
plt.rcParams["font.family"] = zh
plt.rcParams["axes.unicode_minus"] = False

def conn():
    return sqlite3.connect(str(DB))

# ============ 1. FRED关键指标走势 ============
def chart_fred_trends():
    """用15年历史数据画走势图"""
    db = conn()
    # macro_history表: date, value, indicator
    indicators = {
        "联邦基金利率": {"color": "#E74C3C", "ylabel": "%"},
        "美国CPI": {"color": "#3498DB", "ylabel": "指数"},
        "美国失业率": {"color": "#27AE60", "ylabel": "%"},
        "美国10年国债收益率": {"color": "#F39C12", "ylabel": "%"},
        "10年TIPS收益率": {"color": "#9B59B6", "ylabel": "%"},
    }
    
    fig, ax = plt.subplots(figsize=(12, 5.5))
    
    for name, style in indicators.items():
        rows = db.execute(
            "SELECT date, value FROM macro_history WHERE indicator=? AND value IS NOT NULL ORDER BY date",
            (name,)
        ).fetchall()
        if len(rows) < 2:
            print(f"  ⚠️ {name}: 数据不足({len(rows)}行)")
            continue
        dates = [r[0] for r in rows]
        vals = [float(r[1]) for r in rows]
        
        ax.plot(range(len(vals)), vals, color=style["color"], linewidth=1.5,
                label=name, alpha=0.85)
        # 标注最新值
        ax.text(len(vals)-1, vals[-1], f" {vals[-1]:.2f}",
                va="bottom", fontsize=9, color=style["color"], fontweight="bold")

    ax.set_title("美国关键宏观指标走势（15年）", fontsize=14, fontweight="bold")
    ax.set_ylabel("数值", fontsize=11)
    ax.legend(fontsize=9, loc="upper left", framealpha=0.8)
    ax.grid(True, alpha=0.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    
    plt.tight_layout()
    p = CHART_DIR / "fred_trends.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ FRED走势(15年): {p}")
    return p

# ============ 2. 黄金价格走势 ============
def chart_gold_price():
    """黄金日线收盘价走势（从2011年）"""
    db = conn()
    rows = db.execute(
        "SELECT 日期, 收盘 FROM price_history WHERE 品种='gold' AND 收盘 IS NOT NULL ORDER BY 日期"
    ).fetchall()
    db.close()
    
    if len(rows) < 10:
        print(f"  ⚠️ 黄金数据: {len(rows)}行")
        return None
    
    # 数据清洗：过滤明显异常值（黄金价格应在 1000-6000 之间）
    cleaned = [(r[0], float(r[1])) for r in rows if 1000 < float(r[1]) < 6000]
    if len(cleaned) < 10:
        print(f"  ⚠️ 黄金数据清洗后不足: {len(cleaned)}行")
        return None
    
    dates = [r[0] for r in cleaned]
    vals = [r[1] for r in cleaned]
    print(f"  黄金: {len(cleaned)}行 ({dates[0]} ~ {dates[-1]}, ${vals[-1]:.0f})")
    
    # 区间: 最近1年, 3年, 全部
    n = len(dates)
    slices = [
        ("全部(2011~)", 0, n),
        ("近3年", max(0, n-756), n),
        ("近1年", max(0, n-252), n),
    ]
    
    fig, axes = plt.subplots(3, 1, figsize=(12, 9), gridspec_kw={"height_ratios": [3, 2, 2]})
    
    labels_zh = ["全部走势（15年）", "近3年走势", "近1年走势"]
    colors = ["#2C3E50", "#E74C3C", "#3498DB"]
    
    for ax, (label, start, end), lbl, col in zip(axes, slices, labels_zh, colors):
        s, e = start, end
        x = list(range(e - s))
        y = vals[s:e]
        ax.plot(x, y, color=col, linewidth=1.2)
        ax.fill_between(x, y, alpha=0.08, color=col)
        ax.set_title(lbl, fontsize=11, fontweight="bold", color=col)
        ax.set_ylabel("$", fontsize=10)
        
        # 标注首尾值
        ax.text(0, y[0], f"{y[0]:.0f}", fontsize=9, va="bottom", color="#7F8C8D")
        ax.text(len(y)-1, y[-1], f"${y[-1]:,.0f}", fontsize=11, va="bottom", color=col, fontweight="bold")
        
        ax.grid(True, alpha=0.2)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    
    plt.tight_layout()
    p = CHART_DIR / "gold_price.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ 黄金走势(15年): {p}")
    return p

# ============ 3. 白银价格走势 ============
def chart_silver_price():
    """白银日线走势"""
    db = conn()
    rows = db.execute(
        "SELECT 日期, 收盘 FROM price_history WHERE 品种='silver' AND 收盘 IS NOT NULL ORDER BY 日期"
    ).fetchall()
    db.close()
    
    if len(rows) < 10:
        return None
    
    cleaned = [(r[0], float(r[1])) for r in rows if 5 < float(r[1]) < 200]
    if len(cleaned) < 10:
        return None
    dates = [r[0] for r in cleaned]
    vals = [r[1] for r in cleaned]
    n = len(dates)
    
    fig, ax = plt.subplots(figsize=(12, 4.5))
    x = range(n)
    ax.plot(x, vals, color="#7F8C8D", linewidth=1.0, alpha=0.6)
    ax.fill_between(x, vals, alpha=0.05, color="#7F8C8D")
    
    # 均线
    ma50 = [np.mean(vals[max(0,i-50):i+1]) for i in range(n)]
    ma200 = [np.mean(vals[max(0,i-200):i+1]) for i in range(n)]
    ax.plot(x, ma50, color="#E67E22", linewidth=1.5, label="50日均线", alpha=0.8)
    ax.plot(x, ma200, color="#E74C3C", linewidth=1.5, label="200日均线", alpha=0.8)
    
    ax.text(n-1, vals[-1], f" ${vals[-1]:.2f}", fontsize=12, color="#2C3E50", fontweight="bold")
    ax.set_title("白银走势（15年）", fontsize=14, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    
    plt.tight_layout()
    p = CHART_DIR / "silver_price.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ 白银走势(15年): {p}")
    return p

# ============ 4. 金银比 ============
def chart_gold_silver_ratio():
    """金银比走势"""
    db = conn()
    gold = db.execute(
        "SELECT 日期, 收盘 FROM price_history WHERE 品种='gold' AND 收盘 IS NOT NULL ORDER BY 日期"
    ).fetchall()
    silver = db.execute(
        "SELECT 日期, 收盘 FROM price_history WHERE 品种='silver' AND 收盘 IS NOT NULL ORDER BY 日期"
    ).fetchall()
    db.close()
    
    g = {r[0]: float(r[1]) for r in gold if 1000 < float(r[1]) < 6000}
    s = {r[0]: float(r[1]) for r in silver if 5 < float(r[1]) < 200}
    
    common_dates = sorted(set(g) & set(s))
    if len(common_dates) < 10:
        return None
    
    ratios = [g[d]/s[d] for d in common_dates]
    
    fig, ax = plt.subplots(figsize=(12, 4.5))
    x = range(len(ratios))
    ax.plot(x, ratios, color="#8E44AD", linewidth=1.2, alpha=0.7)
    ax.fill_between(x, ratios, alpha=0.06, color="#8E44AD")
    
    ax.axhline(np.mean(ratios), color="#2C3E50", linestyle="--", alpha=0.5, label=f"均值 {np.mean(ratios):.1f}x")
    
    ax.text(len(ratios)-1, ratios[-1], f" {ratios[-1]:.1f}x", fontsize=12,
            va="bottom", color="#8E44AD", fontweight="bold")
    ax.set_title("金银比走势（15年）", fontsize=14, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    
    plt.tight_layout()
    p = CHART_DIR / "gold_silver_ratio.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ 金银比(15年): {p}")
    return p

# ============ 5. COT净持仓历史 ============
def chart_cot_net_history():
    """COT黄金净持仓历史走势"""
    db = conn()
    rows = db.execute(
        "SELECT date, noncomm_net FROM cot_history WHERE commodity='gold' AND noncomm_net IS NOT NULL ORDER BY date"
    ).fetchall()
    db.close()
    
    if len(rows) < 10:
        return None
    
    dates = [r[0] for r in rows]
    vals = [float(r[1]) for r in rows]
    n = len(dates)
    
    fig, ax1 = plt.subplots(figsize=(12, 4.5))
    
    x = range(n)
    ax1.fill_between(x, vals, where=[v>=0 for v in vals], color="#2ECC71", alpha=0.3)
    ax1.fill_between(x, vals, where=[v<0 for v in vals], color="#E74C3C", alpha=0.3)
    ax1.plot(x, vals, color="#2C3E50", linewidth=1.2)
    ax1.axhline(0, color="gray", linewidth=0.8)
    
    ax1.set_ylabel("净持仓(手)", fontsize=11)
    ax1.set_title("黄金COT投机净持仓历史走势", fontsize=14, fontweight="bold")
    ax1.grid(True, alpha=0.2)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    
    # 标注最新值
    ax1.text(n-1, vals[-1], f" {vals[-1]:+,.0f}", fontsize=11, fontweight="bold", color="#2C3E50")
    
    plt.tight_layout()
    p = CHART_DIR / "cot_net_history.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ COT净持仓历史(15年): {p}")
    return p

# ============ 6-8. 原本的COT快照图 ============
def chart_cot_net():
    db = conn()
    rows = db.execute(
        'SELECT 品種, "投機淨持倉" FROM cotdata ORDER BY "投機淨持倉" DESC'
    ).fetchall()
    db.close()
    items = [r[0] for r in rows]
    vals = [float(r[1])/1000 for r in rows]
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["#E74C3C" if v < 0 else "#2ECC71" for v in vals]
    bars = ax.barh(range(len(items)), vals, color=colors, height=0.6)
    ax.set_yticks(range(len(items)))
    ax.set_yticklabels(items, fontsize=10)
    ax.set_xlabel("投机净持仓 (千手)", fontsize=10)
    ax.set_title("COT投机净持仓排行榜", fontsize=13, fontweight="bold")
    ax.axvline(0, color="gray", linewidth=0.8)
    for i, (v, bar) in enumerate(zip(vals, bars)):
        label = f"{v:+.1f}K" if abs(v) < 1000 else f"{v/1000:+.2f}M"
        x = v + (50 if v >= 0 else -50)
        ha = "left" if v >= 0 else "right"
        ax.text(x, i, label, va="center", ha=ha, fontsize=8, color="#2C3E50")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    p = CHART_DIR / "cot_net.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ COT净持仓: {p}")
    return p

def chart_cot_index():
    db = conn()
    rows = db.execute(
        'SELECT 品種, "COT Index(26W)" FROM cotdata ORDER BY "COT Index(26W)" DESC'
    ).fetchall()
    db.close()
    items = [r[0] for r in rows]
    vals = [float(r[1]) for r in rows]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axvspan(0, 5, alpha=0.08, color="#E74C3C")
    ax.axvspan(95, 100, alpha=0.08, color="#E74C3C")
    ax.axvspan(5, 95, alpha=0.04, color="#3498DB")
    colors = []
    for v in vals:
        if v >= 95: colors.append("#E74C3C")
        elif v <= 5: colors.append("#27AE60")
        else: colors.append("#3498DB")
    bars = ax.barh(range(len(items)), vals, color=colors, height=0.6)
    ax.set_yticks(range(len(items)))
    ax.set_yticklabels(items, fontsize=10)
    ax.set_xlabel("COT Index (26周)", fontsize=10)
    ax.set_title("COT Index 一览", fontsize=13, fontweight="bold")
    ax.set_xlim(0, 105)
    for v, bar in zip(vals, bars):
        ax.text(v + 1.5, bar.get_y() + bar.get_height()/2, f"{v:.0f}",
                va="center", fontsize=8, color="#2C3E50")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    p = CHART_DIR / "cot_index.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ COT Index: {p}")
    return p

def chart_cot_long_short():
    db = conn()
    rows = db.execute(
        'SELECT 品種, "投機多頭", "投機空頭" FROM cotdata ORDER BY "投機淨持倉" DESC'
    ).fetchall()
    db.close()
    items = [r[0] for r in rows]
    longs = [float(r[1])/1000 for r in rows]
    shorts = [float(r[2])/1000 for r in rows]
    fig, ax = plt.subplots(figsize=(10, 5))
    y = range(len(items))
    ax.barh(y, longs, height=0.35, color="#2ECC71", alpha=0.8, label="投機多頭")
    ax.barh([i+0.35 for i in y], shorts, height=0.35, color="#E74C3C", alpha=0.8, label="投機空頭")
    ax.set_yticks([i+0.175 for i in y])
    ax.set_yticklabels(items, fontsize=10)
    ax.set_xlabel("持仓 (千手)", fontsize=10)
    ax.set_title("COT投机多空对比", fontsize=13, fontweight="bold")
    ax.legend(fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    p = CHART_DIR / "cot_long_short.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ COT多空对比: {p}")
    return p

# ============ 主函数 ============
def generate_all():
    print(f"📊 生成图表 ({datetime.now().strftime('%Y-%m-%d %H:%M')})")
    charts = {}
    
    for name, fn in [
        ("cot_net", chart_cot_net),
        ("cot_index", chart_cot_index),
        ("cot_long_short", chart_cot_long_short),
        ("fred_trends", chart_fred_trends),
        ("gold_price", chart_gold_price),
        ("silver_price", chart_silver_price),
        ("gold_silver_ratio", chart_gold_silver_ratio),
        ("cot_net_history", chart_cot_net_history),
    ]:
        try:
            p = fn()
            if p:
                charts[name] = p
        except Exception as e:
            print(f"  ❌ {name}: {e}")
    
    print(f"  ✅ 共生成 {len(charts)} 张图")
    return charts

if __name__ == "__main__":
    generate_all()
