#!/usr/bin/env python3
"""生成报告用图表 - 基于SQLite数据库"""
import os, sys
from pathlib import Path
from datetime import datetime
import sqlite3
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# ===== 配置 =====
DB = Path.home() / "hermes-macro-data" / "hermes.db"
CHART_DIR = Path.home() / "hermes-macro-data" / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)

# 设置中文字体
zh_fonts = [f.name for f in fm.fontManager.ttflist if "Noto Sans CJK" in f.name]
zh = zh_fonts[0] if zh_fonts else "DejaVu Sans"
plt.rcParams["font.family"] = zh
plt.rcParams["axes.unicode_minus"] = False

def conn():
    return sqlite3.connect(str(DB))

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16)/255 for i in (0, 2, 4))

# ===== 1. COT净持仓排行榜 =====
def chart_cot_net():
    """各品种投机净持仓柱状图"""
    db = conn()
    rows = db.execute(
        'SELECT 品種, "投機淨持倉" FROM cotdata ORDER BY "投機淨持倉" DESC'
    ).fetchall()
    db.close()

    items = [r[0] for r in rows]
    vals = [float(r[1])/1000 for r in rows]  # 千单位

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["#E74C3C" if v < 0 else "#2ECC71" for v in vals]
    bars = ax.barh(range(len(items)), vals, color=colors, height=0.6)

    ax.set_yticks(range(len(items)))
    ax.set_yticklabels(items, fontsize=10)
    ax.set_xlabel("投机净持仓 (千手)", fontsize=10)
    ax.set_title("COT投机净持仓排行榜", fontsize=13, fontweight="bold")
    ax.axvline(0, color="gray", linewidth=0.8)

    # 柱上标注数值
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

# ===== 2. COT Index一览 =====
def chart_cot_index():
    """COT Index (0-100) 柱状图, 标极端区"""
    db = conn()
    rows = db.execute(
        'SELECT 品種, "COT Index(26W)" FROM cotdata ORDER BY "COT Index(26W)" DESC'
    ).fetchall()
    db.close()

    items = [r[0] for r in rows]
    vals = [float(r[1]) for r in rows]

    fig, ax = plt.subplots(figsize=(10, 5))

    # 背景区域：超买(红色) / 超卖(绿色)
    ax.axvspan(0, 5, alpha=0.08, color="#E74C3C")
    ax.axvspan(95, 100, alpha=0.08, color="#E74C3C")
    ax.axvspan(5, 95, alpha=0.04, color="#3498DB")

    colors = []
    for v in vals:
        if v >= 95: colors.append("#E74C3C")  # 极端多头
        elif v <= 5: colors.append("#27AE60")  # 极端空头
        else: colors.append("#3498DB")

    bars = ax.barh(range(len(items)), vals, color=colors, height=0.6)

    ax.set_yticks(range(len(items)))
    ax.set_yticklabels(items, fontsize=10)
    ax.set_xlabel("COT Index (26周)", fontsize=10)
    ax.set_title("COT Index 一览", fontsize=13, fontweight="bold")
    ax.set_xlim(0, 105)

    # 标注数值
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

# ===== 3. FRED关键指标走势 =====
def chart_fred_trends():
    """联准利率、CPI、失业率走势"""
    db = conn()
    indicators = {
        "聯邦基金利率": "#E74C3C",
        "CPI 消費者物價指數": "#3498DB",
        "失業率": "#27AE60",
    }
    data = {}
    for name, color in indicators.items():
        rows = db.execute(
            "SELECT 日期, 數值 FROM fred_indicators WHERE 指標=? AND 數值 IS NOT NULL ORDER BY 日期",
            (name,)
        ).fetchall()
        dates = [r[0] for r in rows]
        vals = [float(r[1]) for r in rows]
        data[name] = (dates, vals, color)
    db.close()

    fig, ax1 = plt.subplots(figsize=(10, 5))

    for name, (dates, vals, color) in data.items():
        if not dates:
            continue
        ax1.plot(range(len(vals)), vals, color=color, linewidth=2,
                 marker="o", markersize=3, label=name)
        # 标注最新值
        ax1.text(len(vals)-1, vals[-1], f" {vals[-1]:.2f}",
                 va="bottom", fontsize=8, color=color, fontweight="bold")

    ax1.set_xticks(range(0, len(next(iter(data.values()))[0]), max(1, len(next(iter(data.values()))[0])//6)))
    ax1.set_xticklabels([next(iter(data.values()))[0][i] if i < len(next(iter(data.values()))[0]) else "" for i in range(0, len(next(iter(data.values()))[0]), max(1, len(next(iter(data.values()))[0])//6))],
                        rotation=45, fontsize=8)
    ax1.set_ylabel("数值", fontsize=10)
    ax1.set_title("美国关键宏观指标走势", fontsize=13, fontweight="bold")
    ax1.legend(fontsize=9, loc="upper left")
    ax1.grid(True, alpha=0.3)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    plt.tight_layout()
    p = CHART_DIR / "fred_trends.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ FRED走势: {p}")
    return p

# ===== 4. COT多空对比 =====
def chart_cot_long_short():
    """投機多頭 vs 投機空頭 对比"""
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

# ===== 主函数 =====
def generate_all():
    print(f"📊 生成图表 ({datetime.now().strftime('%Y-%m-%d %H:%M')})")
    charts = {}
    try:
        charts["cot_net"] = chart_cot_net()
    except Exception as e:
        print(f"  ❌ COT净持仓: {e}")
    try:
        charts["cot_index"] = chart_cot_index()
    except Exception as e:
        print(f"  ❌ COT Index: {e}")
    try:
        charts["cot_long_short"] = chart_cot_long_short()
    except Exception as e:
        print(f"  ❌ COT多空对比: {e}")
    try:
        charts["fred_trends"] = chart_fred_trends()
    except Exception as e:
        print(f"  ❌ FRED走势: {e}")
    print(f"  ✅ 共生成 {len(charts)} 张图")
    return charts

if __name__ == "__main__":
    generate_all()
