#!/usr/bin/env python3
"""生成报告用图表 - 基于SQLite数据库（含15年历史数据）
   排版规范：所有图统一标准
   - 线图：左下标起始值，右下标最新值（白底框）
   - 柱图：标注在柱末端外侧
   - 字体：标题13粗 轴标10 数据标签9 统一灰色
   - 网格：alpha=0.2 浅灰
   - 边框：只留底部+左侧
"""
import os, sys
from pathlib import Path
from datetime import datetime
import sqlite3
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
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

# 常用颜色
C = {
    "gold":   "#E67E22",
    "silver": "#7F8C8D",
    "red":    "#E74C3C",
    "green":  "#27AE60",
    "blue":   "#2980B9",
    "purple": "#8E44AD",
    "orange": "#F39C12",
    "dark":   "#2C3E50",
    "gray":   "#95A5A6",
    "bg":     "#ECF0F1",
}

def tag_start(ax, x, y, txt):
    """起始值标注：左下角"""
    ax.text(x, y, txt, fontsize=9, ha="left", va="bottom",
            color="#7F8C8D", fontweight="normal")

def tag_end(ax, x, y, txt, color="#2C3E50"):
    """最新值标注：带白底框"""
    ax.text(x, y, txt, fontsize=11, ha="right", va="top",
            color=color, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor=color, alpha=0.85))

def clean_spines(ax):
    """只保留底部+左侧边框"""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#DDD")
    ax.spines["bottom"].set_color("#DDD")

def setup_grid(ax):
    ax.grid(True, alpha=0.2, color="#CCC")
    ax.set_axisbelow(True)

# ============ 1. FRED关键指标走势 ============
def chart_fred_trends():
    """近3年FRED宏观指标走势"""
    indicators = [
        ("联邦基金利率", "#E74C3C"),
        ("美国CPI", "#3498DB"),
        ("美国失业率", "#27AE60"),
        ("美国10年国债收益率", "#F39C12"),
        ("10年TIPS收益率", "#9B59B6"),
    ]

    fig, ax = plt.subplots(figsize=(12, 5.5))
    db = conn()

    # 只取近3年（约1095天）
    for name, color in indicators:
        rows = db.execute(
            "SELECT date, value FROM macro_history WHERE indicator=? AND value IS NOT NULL ORDER BY date DESC LIMIT 1100",
            (name,)
        ).fetchall()
        rows = list(reversed(rows))  # 恢复时间顺序
        if len(rows) < 10:
            continue
        vals = [float(r[1]) for r in rows]
        x = range(len(vals))
        ax.plot(x, vals, color=color, linewidth=1.5, label=name, alpha=0.85)
        # 最新值标注
        if len(vals) > 0:
            last_val = vals[-1]
            ax.text(len(vals)-1, last_val, f"  {last_val:.2f}",
                    va="bottom" if name != "美国CPI" else "top",
                    fontsize=8, color=color, fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                              edgecolor=color, alpha=0.8))

    db.close()
    ax.set_title("美国关键宏观指标走势（15年）", fontsize=13, fontweight="bold", color=C["dark"])
    ax.legend(fontsize=9, loc="upper left", framealpha=0.8)
    setup_grid(ax)
    clean_spines(ax)
    plt.tight_layout()
    p = CHART_DIR / "fred_trends.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ FRED走势(15年): {p}")
    return p

# ============ 2. 黄金价格走势 ============
def chart_gold_price():
    """黄金走势：15年+近3年+近1年"""
    db = conn()
    rows = db.execute(
        "SELECT 日期, 收盘 FROM price_history WHERE 品种='gold' AND 收盘 IS NOT NULL ORDER BY 日期"
    ).fetchall()
    db.close()

    if len(rows) < 10:
        return None

    cleaned = [(r[0], float(r[1])) for r in rows if 1000 < float(r[1]) < 6000]
    if len(cleaned) < 10:
        return None

    dates = [r[0] for r in cleaned]
    vals = [r[1] for r in cleaned]
    n = len(dates)

    slices = [
        ("全部走势（15年）", 0, n, C["dark"]),
        ("近3年走势", max(0, n-756), n, C["red"]),
        ("近1年走势", max(0, n-252), n, C["blue"]),
    ]

    fig, axes = plt.subplots(3, 1, figsize=(12, 9),
                              gridspec_kw={"height_ratios": [3, 2, 2]})

    for ax, (title, s, e, color) in zip(axes, slices):
        y = vals[s:e]
        x = list(range(len(y)))
        ax.plot(x, y, color=color, linewidth=1.2)
        ax.fill_between(x, y, alpha=0.08, color=color)

        # 各自独立Y轴
        ypad = (max(y) - min(y)) * 0.12
        ax.set_ylim(min(y) - ypad, max(y) + ypad)

        # 标注：左下起始，右下最新
        tag_start(ax, 0, y[0], f"${y[0]:,.0f}")
        tag_end(ax, len(y)-1, y[-1], f"${y[-1]:,.0f}", color)

        ax.set_title(title, fontsize=12, fontweight="bold", color=color)
        ax.set_ylabel("USD/oz", fontsize=9, color="#666")
        setup_grid(ax)
        clean_spines(ax)

    plt.tight_layout()
    p = CHART_DIR / "gold_price.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ 黄金走势(15年): {p}")
    return p

# ============ 3. 白银走势 ============
def chart_silver_price():
    """白银日线+50日均线+200日均线"""
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
    vals = [r[1] for r in cleaned]
    n = len(vals)

    ma50 = [np.mean(vals[max(0,i-50):i+1]) for i in range(n)]
    ma200 = [np.mean(vals[max(0,i-200):i+1]) for i in range(n)]

    fig, ax = plt.subplots(figsize=(12, 4.5))
    x = range(n)

    ax.plot(x, vals, color=C["gray"], linewidth=0.8, alpha=0.5, label="收盘价")
    ax.plot(x, ma50, color=C["orange"], linewidth=1.5, label="50日均线", alpha=0.85)
    ax.plot(x, ma200, color=C["red"], linewidth=1.5, label="200日均线", alpha=0.85)

    tag_start(ax, 0, vals[0], f"${vals[0]:.2f}")
    tag_end(ax, n-1, vals[-1], f"${vals[-1]:.2f}", C["dark"])

    ax.set_title("白银走势（15年·均线系统）", fontsize=13, fontweight="bold", color=C["dark"])
    ax.set_ylabel("USD/oz", fontsize=9, color="#666")
    ax.legend(fontsize=9, loc="upper left", framealpha=0.8)
    setup_grid(ax)
    clean_spines(ax)
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
    g = {r[0]: float(r[1]) for r in db.execute(
        "SELECT 日期, 收盘 FROM price_history WHERE 品种='gold' AND 收盘 IS NOT NULL ORDER BY 日期"
    ).fetchall() if 1000 < float(r[1]) < 6000}
    s = {r[0]: float(r[1]) for r in db.execute(
        "SELECT 日期, 收盘 FROM price_history WHERE 品种='silver' AND 收盘 IS NOT NULL ORDER BY 日期"
    ).fetchall() if 5 < float(r[1]) < 200}
    db.close()

    common = sorted(set(g) & set(s))
    if len(common) < 10:
        return None
    ratios = [g[d]/s[d] for d in common]
    n = len(ratios)
    avg_ratio = np.mean(ratios)

    fig, ax = plt.subplots(figsize=(12, 4.5))
    x = range(n)
    ax.plot(x, ratios, color=C["purple"], linewidth=1.0, alpha=0.6)
    ax.fill_between(x, ratios, alpha=0.06, color=C["purple"])

    ax.axhline(avg_ratio, color=C["dark"], linestyle="--", alpha=0.4,
               label=f"均值 {avg_ratio:.1f}x")

    tag_start(ax, 0, ratios[0], f"{ratios[0]:.1f}x")
    tag_end(ax, n-1, ratios[-1], f"{ratios[-1]:.1f}x", C["purple"])

    ax.set_title("金银比走势（15年）", fontsize=13, fontweight="bold", color=C["dark"])
    ax.set_ylabel("金价/银价", fontsize=9, color="#666")
    ax.legend(fontsize=9, loc="upper left", framealpha=0.8)
    setup_grid(ax)
    clean_spines(ax)
    plt.tight_layout()
    p = CHART_DIR / "gold_silver_ratio.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ 金银比(15年): {p}")
    return p

# ============ 5. COT净持仓历史 ============
def chart_cot_net_history():
    """黄金COT投机净持仓历史走势"""
    db = conn()
    rows = db.execute(
        "SELECT date, noncomm_net FROM cot_history WHERE commodity='gold' AND noncomm_net IS NOT NULL ORDER BY date"
    ).fetchall()
    db.close()
    if len(rows) < 10:
        return None

    vals = [float(r[1])/1000 for r in rows]  # 千手
    n = len(vals)

    fig, ax = plt.subplots(figsize=(12, 4.5))
    x = range(n)

    ax.fill_between(x, vals, where=[v>=0 for v in vals],
                    color=C["green"], alpha=0.15)
    ax.fill_between(x, vals, where=[v<0 for v in vals],
                    color=C["red"], alpha=0.15)
    ax.plot(x, vals, color=C["dark"], linewidth=1.2)
    ax.axhline(0, color=C["gray"], linewidth=0.8)

    tag_start(ax, 0, vals[0], f"{vals[0]:+,.0f}K")
    tag_end(ax, n-1, vals[-1], f"{vals[-1]:+,.0f}K", C["dark"])

    ax.set_title("黄金COT投机净持仓历史走势", fontsize=13, fontweight="bold", color=C["dark"])
    ax.set_ylabel("净持仓 (千手)", fontsize=9, color="#666")
    setup_grid(ax)
    clean_spines(ax)
    plt.tight_layout()
    p = CHART_DIR / "cot_net_history.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ COT净持仓历史(15年): {p}")
    return p

# ============ 6. COT净持仓排行榜 ============
def chart_cot_net():
    """COT净持仓柱状图"""
    db = conn()
    rows = db.execute(
        'SELECT 品種, "投機淨持倉" FROM cotdata ORDER BY "投機淨持倉" DESC'
    ).fetchall()
    db.close()
    if not rows:
        return None

    items = [r[0] for r in rows]
    vals = [float(r[1])/1000 for r in rows]

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = [C["red"] if v < 0 else C["green"] for v in vals]
    bars = ax.barh(range(len(items)), vals, color=colors, height=0.6, edgecolor="white", linewidth=0.5)

    ax.set_yticks(range(len(items)))
    ax.set_yticklabels(items, fontsize=10)
    ax.set_xlabel("投机净持仓 (千手)", fontsize=10, color="#555")
    ax.set_title("COT投机净持仓排行榜", fontsize=13, fontweight="bold", color=C["dark"])
    ax.axvline(0, color=C["gray"], linewidth=0.8)

    # 柱末端标注
    for v, bar in zip(vals, bars):
        offset = 8
        x_pos = v + offset if v >= 0 else v - offset
        ha = "left" if v >= 0 else "right"
        ax.text(x_pos, bar.get_y() + bar.get_height()/2,
                f"{v:+,.0f}K", va="center", ha=ha, fontsize=9,
                color=C["dark"],
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                          edgecolor="none", alpha=0.7))

    clean_spines(ax)
    plt.tight_layout()
    p = CHART_DIR / "cot_net.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ COT净持仓: {p}")
    return p

# ============ 7. COT Index一览 ============
def chart_cot_index():
    """COT Index 柱状图"""
    db = conn()
    rows = db.execute(
        'SELECT 品種, "COT Index(26W)" FROM cotdata ORDER BY "COT Index(26W)" DESC'
    ).fetchall()
    db.close()
    if not rows:
        return None

    items = [r[0] for r in rows]
    vals = [float(r[1]) for r in rows]

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.axvspan(0, 5, alpha=0.06, color=C["red"])
    ax.axvspan(95, 100, alpha=0.06, color=C["red"])
    ax.axvspan(5, 95, alpha=0.03, color=C["blue"])

    colors = []
    for v in vals:
        if v >= 95:
            colors.append(C["red"])
        elif v <= 5:
            colors.append(C["green"])
        else:
            colors.append(C["blue"])

    bars = ax.barh(range(len(items)), vals, color=colors, height=0.6,
                    edgecolor="white", linewidth=0.5)

    ax.set_yticks(range(len(items)))
    ax.set_yticklabels(items, fontsize=10)
    ax.set_xlabel("COT Index (26周)", fontsize=10, color="#555")
    ax.set_title("COT Index 一览", fontsize=13, fontweight="bold", color=C["dark"])
    ax.set_xlim(0, 108)

    # 在柱末端标注数值
    for v, bar in zip(vals, bars):
        x_pos = v + 0.8
        ax.text(x_pos, bar.get_y() + bar.get_height()/2,
                f"{v:.0f}", va="center", fontsize=9, color=C["dark"])

    clean_spines(ax)
    plt.tight_layout()
    p = CHART_DIR / "cot_index.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ COT Index: {p}")
    return p

# ============ 8. COT多空对比 ============
def chart_cot_long_short():
    """投机多空对比"""
    db = conn()
    rows = db.execute(
        'SELECT 品種, "投機多頭", "投機空頭" FROM cotdata ORDER BY "投機淨持倉" DESC'
    ).fetchall()
    db.close()
    if not rows:
        return None

    items = [r[0] for r in rows]
    longs = [float(r[1])/1000 for r in rows]
    shorts = [float(r[2])/1000 for r in rows]

    fig, ax = plt.subplots(figsize=(10, 5))
    y = range(len(items))

    ax.barh([i+0.18 for i in y], longs, height=0.35,
            color=C["green"], alpha=0.85, label="投機多頭")
    ax.barh([i-0.18 for i in y], shorts, height=0.35,
            color=C["red"], alpha=0.85, label="投機空頭")

    ax.set_yticks(range(len(items)))
    ax.set_yticklabels(items, fontsize=10)
    ax.set_xlabel("持仓 (千手)", fontsize=10, color="#555")
    ax.set_title("COT投机多空对比", fontsize=13, fontweight="bold", color=C["dark"])
    ax.legend(fontsize=9, loc="lower right", framealpha=0.8)

    clean_spines(ax)
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
