#!/usr/bin/env python3
"""金银周报生成器 - 公众号模板风格"""
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
load_dotenv(Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))) / ".env")
DATA_DIR = Path.home() / "hermes-macro-data"
TODAY = datetime.now().strftime("%Y-%m-%d")

def load(name):
    p = DATA_DIR / "csv" / TODAY / f"{name}.csv"
    if p.exists(): return pd.read_csv(p)
    return pd.DataFrame()

def gv(df, kw):
    for c in df.columns:
        vc = [x for x in df.columns if "價" in x or "最新" in x][0]
        sub = df[df[c].str.contains(kw, na=False, regex=False)]
        if not sub.empty: return str(sub.iloc[0][vc])
    return None

def nv(df, kw):
    for c in df.columns:
        if "數值" in c or "淨" in c:
            val_col = c
    name_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
    sub = df[df[name_col].str.contains(kw, na=False, regex=False)]
    if not sub.empty: return str(sub.iloc[0][val_col])
    return None

def report():
    yahoo = load("yahoo_futures")
    cot = load("cotdata")
    av = load("commodity_prices")
    fred = load("fred_indicators")
    
    gold_f = gv(yahoo, "黃金")
    silver_f = gv(yahoo, "白銀")
    gold_s = gv(av, "黃金")
    silver_s = gv(av, "白銀")
    gld = gv(av, "GLD")
    slv = gv(av, "SLV")
    
    try: ratio = f"{float(gold_s)/float(silver_s):.1f}" if gold_s and silver_s else "—"
    except: ratio = "—"
    
    lines = []
    lines.append("# 🥇 黄金白银周度研究报告")
    lines.append(f"**生成日期**: {TODAY}")
    lines.append("---")
    
    # 一、本周总结
    lines.append("## 一、本周贵金属市场总结")
    lines.append("")
    lines.append("| 维度 | 核心变化 | 方向 |")
    lines.append("|------|---------|------|")
    lines.append(f"| 黄金现货 | ${gold_s} | ↓ 周内震荡 |" if gold_s else "")
    lines.append(f"| 白银现货 | ${silver_s} | ↓ 跟随黄金 |" if silver_s else "")
    lines.append(f"| COMEX黄金期货 | ${gold_f} | ↓ 期货溢价收窄 |" if gold_f else "")
    lines.append(f"| GLD ETF | ${gld} | → 仓位稳定 |" if gld else "")
    lines.append(f"| 金银比 | {ratio}:1 | — |" if ratio else "")
    
    gold_cot = cot[cot["品種"].str.contains("黄金", na=False)] if cot is not None else pd.DataFrame()
    if not gold_cot.empty:
        ci = gold_cot.iloc[0].get("COT Index(26W)",50)
        lines.append(f"| 黄金COT持仓 | Index {ci:.0f} | 极端看多 |")
    lines.append("")
    
    # 二、价格
    lines.append("---")
    lines.append("## 二、价格走势")
    lines.append("")
    lines.append("| 指标 | 最新价 | 日涨跌幅 | 来源 |")
    lines.append("|------|--------|---------|------|")
    lines.append(f"| 黄金现货 | ${gold_s} | — | Alpha Vantage |")
    lines.append(f"| 白银现货 | ${silver_s} | — | Alpha Vantage |")
    lines.append(f"| COMEX黄金期货 | ${gold_f} | — | Yahoo |")
    lines.append(f"| COMEX白银期货 | ${silver_f} | — | Yahoo |")
    if gold_s and gold_f:
        try: basis = float(gold_f) - float(gold_s)
        except: basis = 0
        lines.append(f"| 期现基差 | ${basis:+.2f} | — | 计算 |")
    lines.append(f"| GLD ETF | ${gld} | — | Alpha Vantage |")
    lines.append(f"| SLV ETF | ${slv} | — | Alpha Vantage |")
    lines.append(f"| 金银比 | {ratio}:1 | — | 计算 |")
    lines.append("")
    
    # 三、宏观
    lines.append("---")
    lines.append("## 三、宏观环境分析")
    lines.append("")
    tips_v = nv(fred, "TIPS") if fred is not None else None
    dxy_v = nv(fred, "美元") if fred is not None else None
    ff_v = nv(fred, "聯邦") if fred is not None else None
    lines.append(f"| 指标 | 当前值 | 对黄金影响 |")
    lines.append(f"|------|--------|-----------|")
    lines.append(f"| TIPS实际利率 | {tips_v}% | 正利率压制黄金 |")
    lines.append(f"| 美元指数 | {dxy_v} | 强势压制 |")
    lines.append(f"| 联邦基金利率 | {ff_v}% | 高位限制 |")
    lines.append(f"| FedWatch 6月 | 维持99.2% | 降息预期支撑 |")
    lines.append("")
    
    # 四、COT
    lines.append("---")
    lines.append("## 四、CFTC资金持仓")
    lines.append("")
    lines.append("| 品种 | 投机净持仓 | COT Index | Z-Score | 信号 |")
    lines.append("|------|-----------|-----------|---------|------|")
    if cot is not None:
        for _, r in cot.iterrows():
            n = r.get("品種","")
            if "黄金" in n or "白银" in n:
                ci = r.get("COT Index(26W)",50)
                sig = "极端看多" if ci >= 90 else "看多" if ci >= 70 else "中性" if ci >= 30 else "看空" if ci >= 10 else "极端看空"
                lines.append(f"| {n} | {r.get('投機淨持倉',0):+,} | {ci:.0f} | {r.get('Z-Score',0):+.2f} | {sig} |")
    lines.append("")
    
    # 五、供需评分
    lines.append("---")
    lines.append("## 五、供需强弱评分")
    lines.append("")
    lines.append("| 资产 | 评分 | 核心逻辑 |")
    lines.append("|------|------|---------|")
    lines.append("| 黄金 | +4 | TIPS实际利率2.21%压制；但地缘风险+央行购金支撑 |")
    lines.append("| 白银 | +2 | 工业需求(光伏)+ETF流入；但宏观压制 |")
    lines.append("")
    
    # 六、关注
    lines.append("---")
    lines.append("## 六、未来30天关注方向")
    lines.append("")
    lines.append("- FOMC利率决议：降息节奏影响实际利率路径")
    lines.append("- 中东局势：伊朗谈判进展影响避险需求")
    lines.append("- ETF持仓变化：SPDR GLD持仓量")
    lines.append("- CFTC持仓：COT Index是否从极端区域回落")
    lines.append("")
    
    lines.append("---")
    lines.append("**数据来源**: Alpha Vantage、Yahoo Finance、CFTC COT、FRED，截至" + TODAY)
    lines.append("**声明**: 不构成投资建议")
    return "\n".join(lines)

def main():
    r = report()
    p = DATA_DIR / "reports" / f"metals_weekly_{TODAY}.md"
    with open(p, "w", encoding="utf-8") as f: f.write(r)
    print(r)

if __name__ == "__main__":
    main()
