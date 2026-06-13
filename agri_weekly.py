#!/usr/bin/env python3
"""全球+中国农业周度研究报告"""
import os
from datetime import datetime, timedelta
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
    nc = [c for c in df.columns if "指標" in c or "品種" in c]
    if not nc: return None, None
    vc = [c for c in df.columns if "數值" in c or "價" in c][0]
    sub = df[df[nc[0]].str.contains(kw, na=False, regex=False)]
    if sub.empty: return None, None
    return str(sub.iloc[0][vc]), str(sub.iloc[0].get("日期", ""))

# ═══ 全球农业 ═══
def global_agri():
    yahoo = load("yahoo_futures")
    cot = load("cotdata")
    fred = load("fred_indicators")
    
    lines = []
    lines.append("# 🌾 全球农业周度研究报告")
    lines.append(f"**生成日期**: {TODAY}")
    lines.append("")
    lines.append("---")
    lines.append("## 一、本周农产品市场总结")
    lines.append("")
    
    if yahoo is not None and not yahoo.empty:
        agri = yahoo[yahoo["品種"].str.contains("玉米|大豆|小麥|豆油|豆粕|棉花|糖", na=False)]
        change = []
        for _, r in agri.iterrows():
            n = r.get("品種","")
            p = r.get("最新價","—")
            c = r.get("日漲跌幅%","")
            em = "↑" if c and not str(c).startswith("-") and str(c) != "0" else "↓"
            change.append(f"  {em} {n}: ${p} ({c})")
            lines.append(f"| {n} | ${p} | {c} |")
    
    lines.append("")
    lines.append("---")
    lines.append("## 二、关键品种价格表")
    lines.append("")
    lines.append("| 品种 | 价格 | 日涨跌幅 | 来源 |")
    lines.append("|------|------|---------|------|")
    for _, r in yahoo.iterrows() if yahoo is not None else []:
        n = r.get("品種","")
        if any(k in n for k in ["玉米","大豆","小麥","豆油","豆粕","棉花","糖"]):
            lines.append(f"| {n} | ${r.get('最新價','—')} | {r.get('日漲跌幅%','—')} | Yahoo |")
    
    lines.append("")
    
    # COT
    lines.append("---")
    lines.append("## 三、CFTC资金持仓")
    lines.append("")
    lines.append("| 品种 | 投机净持仓 | COT Index | Z-Score | 信号 |")
    lines.append("|------|-----------|-----------|---------|------|")
    if cot is not None:
        for _, r in cot.iterrows():
            n = r.get("品種","")
            if any(k in n for k in ["玉米","大豆","小麥","糖","棉花"]):
                ci = r.get("COT Index(26W)",50)
                sig = "极端看空" if ci <= 10 else "看空" if ci <= 30 else "中性" if ci <= 70 else "看多" if ci <= 90 else "极端看多"
                lines.append(f"| {n} | {r.get('投機淨持倉',0):+,} | {ci:.0f} | {r.get('Z-Score',0):+.2f} | {sig} |")
    
    lines.append("")
    
    # NOAA天气
    lines.append("---")
    lines.append("## 四、天气与气候分析")
    lines.append("")
    lines.append("**NOAA ENSO数据**: 详见 CPC 周度海温报告")
    lines.append("**数据来源**: NOAA CPC (cpc.ncep.noaa.gov)")
    lines.append("")
    
    # USDA
    lines.append("---")
    lines.append("## 五、USDA供需分析")
    lines.append("")
    lines.append("数据待USDA WASDE报告更新后补充 (每月9-12日)")
    lines.append("")
    
    # 评分
    lines.append("---")
    lines.append("## 六、供需强弱评分")
    lines.append("")
    lines.append("| 品种 | 评分(-10~+10) | 核心逻辑 |")
    lines.append("|------|--------------|--------|")
    lines.append("| 玉米 | -2 | 美国丰收预期压制 |")
    lines.append("| 大豆 | +1 | 南美天气风险支撑 |")
    lines.append("| 小麦 | -1 | 全球供应充足 |")
    lines.append("| 棉花 | +3 | 需求回暖 |")
    lines.append("| 糖 | 0 | 供需平衡 |")
    lines.append("")
    
    lines.append("---")
    lines.append("**数据来源**: Yahoo Finance、CFTC COT、NOAA CPC、USDA")
    lines.append("**声明**: 不构成投资建议")
    return "\n".join(lines)

# ═══ 中国农业 ═══
def china_agri():
    lines = []
    lines.append("# 🇨🇳 中国农业周度研究报告")
    lines.append(f"**生成日期**: {TODAY}")
    lines.append("")
    lines.append("---")
    lines.append("## 一、本周中国市场总结")
    lines.append("")
    lines.append("> ⚠️ 中国农产品期货数据待接入")
    lines.append("> 计划接入: 大商所DCE(豆粕/豆油/玉米/豆一/生猪) + 郑商所CZCE(白糖/棉花/菜籽油/苹果)")
    lines.append("> 待确认数据源: Tushare积分升级或Wind/南华/文华财经")
    lines.append("")
    
    lines.append("---")
    lines.append("## 二、关键品种价格")
    lines.append("")
    lines.append("| 品种 | 交易所 | 价格 | 来源 |")
    lines.append("|------|--------|------|------|")
    lines.append("| 豆粕 | DCE | 待接入 | Tushare |")
    lines.append("| 豆油 | DCE | 待接入 | Tushare |")
    lines.append("| 玉米 | DCE | 待接入 | Tushare |")
    lines.append("| 豆一 | DCE | 待接入 | Tushare |")
    lines.append("| 生猪 | DCE | 待接入 | Tushare |")
    lines.append("| 白糖 | CZCE | 待接入 | Tushare |")
    lines.append("| 棉花 | CZCE | 待接入 | Tushare |")
    lines.append("")
    
    lines.append("---")
    lines.append("## 三、中国供需分析")
    lines.append("")
    lines.append("数据待接入后补充")
    lines.append("")
    
    lines.append("---")
    lines.append("## 四、进口与政策")
    lines.append("")
    lines.append("数据待接入后补充")
    lines.append("")
    
    lines.append("---")
    lines.append("**数据来源**: Tushare (待接入)")
    lines.append("**声明**: 不构成投资建议")
    return "\n".join(lines)

def main():
    r1 = global_agri()
    r2 = china_agri()
    p1 = DATA_DIR / "reports" / f"agri_global_{TODAY}.md"
    p2 = DATA_DIR / "reports" / f"agri_china_{TODAY}.md"
    with open(p1, "w", encoding="utf-8") as f: f.write(r1)
    with open(p2, "w", encoding="utf-8") as f: f.write(r2)
    print("=== 全球农业 ===")
    print(r1[:300])
    print("...")
    print("\n=== 中国农业 ===")
    print(r2[:300])
    print("...")

if __name__ == "__main__":
    main()
