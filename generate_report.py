#!/usr/bin/env python3
"""贵金属日报生成器"""
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
        return "\u2014", "\u2014"
    sub = df[df[col[0]].str.contains(keyword, na=False)].sort_values("\u65e5\u671f", ascending=False)
    if sub.empty:
        return "\u2014", "\u2014"
    val_col = [c for c in df.columns if "值" in c][0]
    return str(sub.iloc[0][val_col]), str(sub.iloc[0]["\u65e5\u671f"])


def gen_report():
    fred = load_csv("fred_indicators")
    prices = load_csv("commodity_prices")
    news = load_csv("financial_news")
    agsi = load_csv("agsi_eu_gas")
    fedwatch = load_csv("fedwatch")

    # Determine column names from CSV
    name_col = [c for c in (fred.columns if not fred.empty else []) if "標" in c or "指" in c]
    name_col = name_col[0] if name_col else "name"
    val_col = [c for c in (fred.columns if not fred.empty else []) if "值" in c]
    val_col = val_col[0] if val_col else "value"
    date_col = "\u65e5\u671f"
    src_col = [c for c in (fred.columns if not fred.empty else []) if "來源" in c or "源" in c]
    src_col = src_col[0] if src_col else "source"

    lines = []
    lines.append(f"\U0001f4c5 贵金属日报 | {TODAY}")
    lines.append("\u2501" * 45)
    lines.append("")

    # Gold/Silver prices
    gold_px = "\u2014"
    gold_chg = ""
    silver_px = "\u2014"
    silver_chg = ""
    oil_px = None
    oil_chg = ""

    if not prices.empty:
        for _, r in prices.iterrows():
            nm = str(r.iloc[0])
            v = r.iloc[2] if len(r) > 2 else "\u2014"
            chg = r.iloc[3] if len(r) > 3 else ""
            if "\u9ec3\u91d1" in nm or "\u9ec4\u91d1" in nm:
                gold_px = v
                gold_chg = chg
            elif "\u767d\u9280" in nm or "\u767d\u94f6" in nm:
                silver_px = v
                silver_chg = chg
            elif "\u539f\u6cb9" in nm:
                oil_px = v
                oil_chg = chg

    lines.append(f"  \U0001f4ca 关键数据速览")
    lines.append(f"    黄金: ${gold_px} ({gold_chg})  |  白银: ${silver_px} ({silver_chg})")
    if oil_px:
        lines.append(f"    原油(WTI): ${oil_px} ({oil_chg})")
    lines.append("")

    # Macro snapshot
    if not fred.empty:
        cpi_v, _ = gv(fred, "CPI")
        ff_v, _ = gv(fred, "\u806f\u90a6\u57fa\u91d1")
        dgs10_v, _ = gv(fred, "10 \u5e74\u671f\u570b\u50b5")
        tips_v, _ = gv(fred, "TIPS")
        dxy_v, _ = gv(fred, "\u7f8e\u5143\u6307\u6578")
        pce_v, _ = gv(fred, "\u6838\u5fc3PCE")
        unemp_v, _ = gv(fred, "\u5931\u696d\u7387")

        lines.append(f"    美债10Y: {dgs10_v}%  |  TIPS: {tips_v}%  |  美元: {dxy_v}")
        lines.append(f"    CPI: {cpi_v}  |  核心PCE: {pce_v}  |  失业率: {unemp_v}%")
        lines.append(f"    联邦基金利率: {ff_v}%")
    lines.append("")

    if not fedwatch.empty:
        r = fedwatch.iloc[0]
        hold = r.get(r.keys()[2], "?")
        hike = r.get(r.keys()[3], "?")
        cut = r.get(r.keys()[4], "?")
        lines.append(f"    FOMC 6月: 维持 {hold}%  |  加息 {hike}%  |  降息 {cut}%")
    lines.append("")

    # Macro details table
    if not fred.empty:
        lines.append("\u2501" * 45)
        lines.append("\U0001f3db\ufe0f 宏观环境")
        lines.append("")
        macro_keys = [
            "\u806a\u90a6\u57fa\u91d1\u5229\u7387", "CPI", "\u6838\u5fc3PCE",
            "\u5931\u696d\u7387", "\u975e\u8fb2", "10 \u5e74\u671f\u570b\u50b5",
            "TIPS", "\u7f8e\u5143\u6307\u6578",
        ]
        for kw in macro_keys:
            v, d = gv(fred, kw)
            if v != "\u2014":
                lines.append(f"    {kw}: {v} ({d})")
        lines.append("")
        lines.append("    来源: FRED")
    lines.append("")

    # Gold analysis
    lines.append("\u2501" * 45)
    lines.append("\U0001f947 黄金分析")
    lines.append("")
    lines.append(f"    现货黄金: ${gold_px}")
    try:
        t = float(tips_v) if tips_v != "\u2014" else 0
        if t > 0:
            lines.append(f"    TIPS {t}%: 正实际利率环境, 黄金持有成本上升")
        else:
            lines.append(f"    TIPS {t}%: 负实际利率, 利好黄金")
    except Exception:
        pass
    if not news.empty:
        txt = str(news.values).lower()
        if any(k in txt for k in ["war", "iran", "sanction", "conflict"]):
            lines.append("    地缘风险升温, 黄金避险需求存在支撑")
    lines.append("")

    # Silver analysis
    lines.append("\u2501" * 45)
    lines.append("\U0001f948 白银分析")
    lines.append("")
    lines.append(f"    现货白银: ${silver_px}")
    try:
        ratio = float(gold_px) / float(silver_px)
        lines.append(f"    金银比: {ratio:.1f}x")
        if ratio > 85:
            lines.append("    金银比处于高位, 白银相对低估")
        elif ratio > 70:
            lines.append("    金银比中性偏高")
    except Exception:
        pass
    lines.append("")

    # News
    lines.append("\u2501" * 45)
    lines.append("\U0001f30d 地缘政治与风险事件")
    lines.append("")
    if not news.empty:
        for _, r in news.head(5).iterrows():
            t = str(r.iloc[0])[:70] if len(r) > 0 else ""
            lines.append(f"    \u00b7 {t}")
    lines.append("")

    # Footer
    lines.append("\u2501" * 45)
    lines.append(f"    数据来源: FRED, Alpha Vantage, Finnhub, AGSI+, Oddpool(FedWatch)")
    lines.append(f"    生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
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
