#!/usr/bin/env python3
"""
贵金属日报生成器 (Precious Metals Daily Report Generator)
读取 macro_pipeline.py 采集的 CSV 数据，生成结构化日报。
"""
import os
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

load_dotenv(Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))) / ".env")

DATA_DIR = Path.home() / "hermes-macro-data"
TODAY = datetime.now().strftime("%Y-%m-%d")
YESTERDAY = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")


def load_csv(name, date=None):
    d = date or TODAY
    for try_date in [d, YESTERDAY]:
        p = DATA_DIR / "csv" / try_date / f"{name}.csv"
        if p.exists():
            return pd.read_csv(p)
    return pd.DataFrame()


def gv(df, keyword):
    """get_fred_value - 取指标最新值"""
    col = [c for c in df.columns if "標" in c or "指" in c]
    if not col:
        return "—", "—"
    sub = df[df[col[0]].str.contains(keyword, na=False)].sort_values("日期", ascending=False)
    if sub.empty:
        return "—", "—"
    val_col = [c for c in df.columns if "值" in c][0]
    return str(sub.iloc[0][val_col]), str(sub.iloc[0]["日期"])


def gen_report():
    fred = load_csv("fred_indicators")
    prices = load_csv("commodity_prices")
    news = load_csv("financial_news")
    agsi = load_csv("agsi_eu_gas")
    fedwatch = load_csv("fedwatch")

    gold_px, gold_chg = "—", ""
    silver_px, silver_chg = "—", ""
    oil_px, oil_chg = None, ""

    if not prices.empty:
        for _, r in prices.iterrows():
            nm = str(r.iloc[0])
            v = r.iloc[2] if len(r) > 2 else "—"
            chg = r.iloc[3] if len(r) > 3 else ""
            if "黃金" in nm or "黄金" in nm:
                gold_px, gold_chg = v, chg
            elif "白銀" in nm or "白银" in nm:
                silver_px, silver_chg = v, chg
            elif "原油" in nm:
                oil_px, oil_chg = v, chg

    lines = []
    lines.append(f"📅 贵金属日报 | {TODAY}")
    lines.append("━" * 45)
    lines.append("")
    lines.append(f"  📊 关键数据速览")
    lines.append(f"    黄金: ${gold_px} ({gold_chg})  |  白银: ${silver_px} ({silver_chg})")
    if oil_px:
        lines.append(f"    原油(WTI): ${oil_px} ({oil_chg})")
    lines.append("")

    if not fred.empty:
        for kw, label in [("CPI", "CPI"), ("核心PCE", "核心PCE"), ("10 年期國債", "美债10Y"),
                          ("TIPS", "TIPS"), ("美元指數", "美元"), ("聯邦基金利率", "联邦基金利率")]:
            v, d = gv(fred, kw)
            if v != "—":
                lines.append(f"    {label}: {v} ({d})")
    lines.append("")

    if not fedwatch.empty:
        r = fedwatch.iloc[0]
        keys = list(r.keys())
        hold = r.get(keys[2], "?") if len(keys) > 2 else "?"
        hike = r.get(keys[3], "?") if len(keys) > 3 else "?"
        cut = r.get(keys[4], "?") if len(keys) > 4 else "?"
        lines.append(f"    FOMC 6月: 维持 {hold}%  |  加息 {hike}%  |  降息 {cut}%")
    lines.append("")

    # Macro details
    components = [("CPI", "CPI"), ("核心PCE", "核心PCE"), ("失業率", "失业率"),
                  ("非農", "非农"), ("10 年期國債", "10年期国债"), ("TIPS", "TIPS"),
                  ("美元指數", "美元指数")]
    for fname, label in components:
        v, d = gv(fred, fname)
        if v != "—":
            lines.append(f"    {label}: {v} ({d})")
    lines.append("    来源: FRED")
    lines.append("")

    # Gold
    lines.append("━" * 45)
    lines.append("🥇 黄金分析")
    lines.append("")
    lines.append(f"    现货黄金: ${gold_px}")
    tips_v, _ = gv(fred, "TIPS")
    try:
        t = float(tips_v) if tips_v != "—" else 0
        if t > 0:
            lines.append(f"    TIPS {t}%: 正实际利率环境, 黄金持有成本上升")
        else:
            lines.append(f"    TIPS {t}%: 负实际利率, 利好黄金")
    except:
        pass
    if not news.empty:
        txt = str(news.values).lower()
        if any(k in txt for k in ["war", "iran", "conflict", "tariff"]):
            lines.append("    地缘风险升温, 黄金避险需求存在支撑")
    lines.append("")

    # Silver
    lines.append("━" * 45)
    lines.append("🥈 白银分析")
    lines.append(f"    现货白银: ${silver_px}")
    try:
        ratio = float(gold_px) / float(silver_px)
        lines.append(f"    金银比: {ratio:.1f}x")
        if ratio > 85:
            lines.append("    金银比处于高位, 白银相对低估")
    except:
        pass
    lines.append("")

    # News
    lines.append("━" * 45)
    lines.append("🌍 地缘政治与风险事件")
    if not news.empty:
        for _, r in news.head(5).iterrows():
            t = str(r.iloc[0])[:70] if len(r) > 0 else ""
            lines.append(f"    · {t}")
    lines.append("")
    lines.append("━" * 45)
    lines.append(f"    数据来源: FRED, Alpha Vantage, Finnhub, AGSI+, Oddpool")
    lines.append(f"    生成时间: {datetime.now():%Y-%m-%d %H:%M}")
    lines.append(f"    声明: 不构成投资建议")

    return "\n".join(lines)


def main():
    report = gen_report()
    report_dir = DATA_DIR / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / f"{TODAY}.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    return report


if __name__ == "__main__":
    main()
