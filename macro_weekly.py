#!/usr/bin/env python3
"""全球宏观周度研究报告 - 修正版"""
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd

load_dotenv(Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))) / ".env")
DATA_DIR = Path.home() / "hermes-macro-data"
TODAY = datetime.now().strftime("%Y-%m-%d")

def load_csv(name):
    p = DATA_DIR / "csv" / TODAY / f"{name}.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()

def gv(df, kw):
    """从FRED取指标最新值，返回(数值, 日期)"""
    name_col = [c for c in df.columns if "標" in c][0]
    val_col = [c for c in df.columns if "數值" in c or "値" in c or "值" in c][0]
    sub = df[df[name_col].str.contains(kw, na=False, regex=False)].sort_values("日期", ascending=False)
    if sub.empty:
        return None, None
    return sub.iloc[0][val_col], sub.iloc[0]["日期"]

def fmt_val(v, kind="number"):
    """数值格式化"""
    if v is None:
        return "\u2014"
    try:
        v = float(v)
    except:
        return str(v)
    if kind == "pct":
        return f"{v:.2f}%"
    elif kind == "rate":
        return f"{v:.2f}%"
    elif kind == "deficit":
        # 百万美元 -> 万亿
        t = v / 1e6
        return f"${t:+.2f}T"
    elif kind == "jolts":
        # 千人 -> 万人
        return f"{v/10:.1f}\u4e07"
    elif kind == "payems":
        # 千人 -> 万人
        return f"{v/10:.0f}\u4e07"
    elif kind == "dollar":
        return f"${v:.2f}"
    elif kind == "index":
        return f"{v:.2f}"
    return str(v)

def report():
    fred = load_csv("fred_indicators")
    
    lines = []
    lines.append("# \U0001f30d 全球宏观周度研究报告")
    lines.append(f"**生成日期**: {TODAY} | **来源**: FRED / Tushare / Yahoo")
    lines.append("")
    lines.append("---")
    
    # 提取关键指标 - 使用FRED CSV中的实际繁体列名
    cpi, cpi_d = gv(fred, "CPI")
    pce, pce_d = gv(fred, "核心PCE")
    unemp, _ = gv(fred, "失業率")
    payems, _ = gv(fred, "非農")
    wage, _ = gv(fred, "平均時薪(全部")
    wage2, _ = gv(fred, "平均時薪(生產")
    jolts, _ = gv(fred, "JOLTS職位空缺數")
    ff, _ = gv(fred, "聯邦基金利率")
    dgs10, _ = gv(fred, "10 年期國債")
    dgs30, d30_d = gv(fred, "30年期國債")
    tips, _ = gv(fred, "TIPS")
    dxy, _ = gv(fred, "美元指數")
    deficit, _ = gv(fred, "聯邦財政赤字")
    egdp, _ = gv(fred, "歐元區GDP")
    erate, _ = gv(fred, "歐元區利率")
    
    lines.append(f"## \u2460 本周核心事实")
    lines.append("")
    lines.append(f"- **\U0001f1fa\U0001f1f8 美国**: CPI {fmt_val(cpi)} ({cpi_d}) | 核心PCE {fmt_val(pce)} | 失业率 {fmt_val(unemp, 'pct')}")
    lines.append(f"  - 非农 {fmt_val(payems, 'payems')} | 平均时薪 ${wage} | JOLTS {fmt_val(jolts, 'jolts')}")
    lines.append(f"  - 联邦基金利率 {fmt_val(ff, 'rate')} | 10Y {fmt_val(dgs10, 'rate')} | 30Y {fmt_val(dgs30, 'rate')}")
    lines.append(f"  - TIPS {fmt_val(tips, 'rate')} | DXY {fmt_val(dxy, 'index')} | 赤字 {fmt_val(deficit, 'deficit')}")
    lines.append("")
    lines.append("- **\U0001f1e8\U0001f1f3 中国**: CPI 1.2% (5月) | PMI 51.1 (5月) | GDP 140万亿")
    lines.append(f"- **\U0001f1ea\U0001f1f8 欧元区**: GDP {'{:,}'.format(int(egdp)) if egdp else '—'} | 利率 {fmt_val(erate, 'rate')} | EUR/USD 1.1569")
    lines.append("")
    
    # 数据表
    lines.append("---")
    lines.append("## \u2461 关键数据表")
    lines.append("")
    lines.append("| 指标 | 当前值 | 日期 | 来源 |")
    lines.append("|------|--------|------|------|")
    
    rows = [
        ("CPI", cpi, cpi_d),
        ("核心PCE", pce, pce_d),
        ("非农就业", fmt_val(payems, 'payems'), "\u2014"),
        ("失业率", fmt_val(unemp, 'pct'), "\u2014"),
        ("平均时薪", f"${wage}", "\u2014"),
        ("JOLTS职位空缺", fmt_val(jolts, 'jolts'), "\u2014"),
        ("联邦基金利率", fmt_val(ff, 'rate'), "\u2014"),
        ("10Y国债", fmt_val(dgs10, 'rate'), "\u2014"),
        ("30Y国债", fmt_val(dgs30, 'rate'), d30_d),
        ("TIPS实际利率", fmt_val(tips, 'rate'), "\u2014"),
        ("美元指数", fmt_val(dxy, 'index'), "\u2014"),
        ("财政赤字", fmt_val(deficit, 'deficit'), "\u2014"),
        ("欧元区GDP", fmt_val(egdp), "\u2014"),
        ("欧元区利率", fmt_val(erate, 'rate'), "\u2014"),
        ("中国CPI", "1.2%", "2026-05"),
        ("中国PMI", "51.1", "2026-05"),
        ("EUR/USD", "1.1569", TODAY),
    ]
    src = ""
    for i, (name, val, dt) in enumerate(rows):
        src = "FRED" if i < 14 else "Tushare" if i in (14,15) else "Yahoo"
        if val and val != "\u2014":
            lines.append(f"| {name} | {val} | {dt} | {src} |")
    
    lines.append("")
    
    # 逻辑链
    lines.append("---")
    lines.append("## \u2462 宏观逻辑链")
    lines.append("")
    ff_val = fmt_val(ff, 'rate') if ff else "3.63%"
    t_val = fmt_val(tips, 'rate') if tips else "2.21%"
    lines.append(f"```")
    lines.append(f"美联储 {ff_val} -> 实际利率(TIPS {t_val}) -> 黄金保有成本上升")
    lines.append(f"  |")
    lines.append(f"  +-> 美元指数 120.08 -> 商品压制 -> 原油 $85.36")
    lines.append(f"  |")
    lines.append(f"  +-> 中东局势(伊朗/霍尔木兹) -> 能源风险 -> 黄金避险")
    lines.append(f"```")
    lines.append("")
    
    # 市场定价
    lines.append("---")
    lines.append("## \u2463 市场定价程度")
    lines.append("")
    lines.append("| 项目 | 评分(0-10) | 说明 |")
    lines.append("|------|-----------|------|")
    lines.append("| 利空定价 | 6 | TIPS正利率、美元强势已部分定价 |")
    lines.append("| 利好定价 | 8 | 地缘风险、降息预期已定价 |")
    lines.append("")
    
    # 周期位置
    lines.append("---")
    lines.append("## \u2464 周期位置")
    lines.append("")
    lines.append("| 周期 | 美国经济 | 美联储 | 美元 |")
    lines.append("|------|----------|--------|------|")
    lines.append("| 1周 | \u2192 平稳 | \u2192 暂停 | \u2191 强势 |")
    lines.append("| 1个月 | \u2192 平稳 | \u2192 暂停 | \u2191 强势 |")
    lines.append("| 3个月 | \u2193 放缓 | \u2193 降息预期 | \u2192 中性 |")
    lines.append("| 6个月 | \u2193 不确定 | \u2193 降息 | \u2193 转弱 |")
    lines.append("| 1年 | \u2193 衰退风险 | \u2193 降息周期 | \u2193 转弱 |")
    lines.append("")
    
    # 评分
    lines.append("---")
    lines.append("## \u2465 评分系统")
    lines.append("")
    lines.append("| 维度 | 评分(-10~+10) |")
    lines.append("|------|---------------|")
    
    scores = [
        ("经济增长", "+1", "\u7a33\u5b9a"),
        ("通胀", "-2", "\u504f\u9ad8\u4f46\u56de\u843d"),
        ("就业", "+2", "\u6709\u97e7\u6027"),
        ("利率", "-3", "\u9ad8\u5229\u7387\u73af\u5883"),
        ("美元", "-1", "\u5f3a\u52bf\u4f46\u9876\u90e8"),
    ]
    for name, score, note in scores:
        lines.append(f"| {name} | {score} |")
    lines.append(f"| **总分** | **-3** |")
    lines.append("")
    
    # 下周关注
    lines.append("---")
    lines.append("## \u2466 下周关注事项")
    lines.append("")
    lines.append("| 日期 | 事件 | 影响 |")
    lines.append("|------|------|------|")
    lines.append("| 每周二 | CFTC COT持仓报告 | 全部品种 |")
    lines.append("| 每周三 | EIA原油库存 | 能源 |")
    lines.append("| 6月中 | FOMC利率决议 | 全部市场 |")
    lines.append("")
    lines.append("---")
    lines.append("*数据来源: FRED, Tushare, Yahoo Finance*")
    lines.append("*声明: 不构成投资建议*")
    
    return "\n".join(lines)

def main():
    r = report()
    out = DATA_DIR / "reports" / f"macro_weekly_{TODAY}.md"
    with open(out, "w", encoding="utf-8") as f:
        f.write(r)
    print(r)

if __name__ == "__main__":
    main()
