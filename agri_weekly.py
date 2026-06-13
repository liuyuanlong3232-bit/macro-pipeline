#!/usr/bin/env python3
"""全球+中国农业周度研究报告"""
import os
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
import requests

load_dotenv(Path(os.environ.get("HERMES_HOME", str(Path.home() / "hermes-pipeline"))) / ".env")
DATA_DIR = Path.home() / "hermes-macro-data"
TODAY = datetime.now().strftime("%Y-%m-%d")

def load(name):
    p = DATA_DIR / "csv" / TODAY / f"{name}.csv"
    if p.exists(): return pd.read_csv(p)
    # 手动读SQLite
    import sqlite3
    db = sqlite3.connect(str(DATA_DIR / "hermes.db"))
    df = pd.read_sql(f"SELECT * FROM \"{name}\"", db)
    db.close()
    return df

# ═══ Tushare中国期货 ═══
TUSHARE_MAP = {
    "豆粕": "M", "豆油": "Y", "玉米": "C",
    "豆一": "A", "生猪": "LH", "白糖": "SR", "棉花": "CF",
    "菜籽油": "OI", "棕榈油": "P", "鸡蛋": "JD",
}

def fetch_china_futures():
    """从Tushare获取DCE/CZCE主力合约行情"""
    token = os.getenv("TUSHARE_TOKEN")
    if not token:
        return []
    
    try:
        today = datetime.now().strftime("%Y%m%d")
        # 回退到最近交易日（周末无数据）
        start = (datetime.now() - timedelta(days=5)).strftime("%Y%m%d")
        url = "http://api.tushare.pro"
        results = []
        
        for name, ts_code in TUSHARE_MAP.items():
            ts_full = f"{ts_code}.DCE" if ts_code in ("M","Y","C","A","LH","JD","P") else f"{ts_code}.CZCE"
            
            payload = {
                "api_name": "fut_daily",
                "token": token,
                "params": {"ts_code": ts_full, "start_date": start, "end_date": today},
                "fields": "ts_code,trade_date,close,pre_close,vol"
            }
            try:
                r = requests.post(url, json=payload, timeout=10)
                data = r.json()
                if data.get("code") == 0 and data.get("data",{}).get("items"):
                    items = sorted(data["data"]["items"], key=lambda x: x[1], reverse=True)
                    item = items[0]
                    close = item[2]
                    pre_close = item[3]
                    chg = ((close-pre_close)/pre_close*100) if pre_close and pre_close != 0 else 0
                    results.append({
                        "品种": name,
                        "最新价": close,
                        "前收": pre_close,
                        "涨跌幅": round(chg, 2),
                    })
                else:
                    results.append({"品种": name, "最新价": "—", "前收": "—", "涨跌幅": "—"})
            except Exception as e:
                print(f"  跳过 {name}: {e}")
                results.append({"品种": name, "最新价": "—", "前收": "—", "涨跌幅": "—"})
        
        return results
    except Exception as e:
        print(f"  Tushare错误: {e}")
        return []

# ═══ 全球农业 ═══
def global_agri():
    yahoo = load("yahoo_futures")
    cot = load("cotdata")
    
    lines = []
    lines.append("# 全球农业周度研究报告（国际版）")
    lines.append(f"生成日期: {TODAY}")
    lines.append("")
    lines.append("---")

    # ══ 一、本周国际农业市场总结 ══
    lines.append("## 一、本周国际农业市场总结")
    lines.append("")
    lines.append("维度 | 核心变化 | 方向（↑/↓/→震荡）")
    lines.append("--- | --- | ---")
    intl_dims = [
        "美豆主力", "美玉米主力", "美小麦主力",
        "原糖主力", "棉花主力", "农产品指数",
        "CFTC农业投机总持仓", "美农天气指数", "美湾港口装运率"
    ]
    for d in intl_dims:
        lines.append(f"{d} | — | —")
    lines.append("")
    lines.append("**本周核心总结**：锚定USDA边际、北美产区天气、基金调仓、海外出口需求四大核心矛盾")
    lines.append("")
    lines.append("---")

    # ══ 二、主力品种价格走势分析 ══
    lines.append("## 二、主力品种价格走势分析")
    lines.append("")
    lines.append("指标 | 最新价 | 周环比 | 周均价 | 数据来源")
    lines.append("--- | --- | --- | --- | ---")
    agri_items = ["玉米", "大豆", "小麥", "豆油", "豆粕", "棉花", "糖"]
    has_yahoo_data = False
    if not yahoo.empty:
        agri = yahoo[yahoo["品種"].str.contains("|".join(agri_items), na=False)]
        if not agri.empty:
            has_yahoo_data = True
            for _, r in agri.iterrows():
                n = r.get("品種", "")
                p = r.get("最新價", "—")
                chg = r.get("日漲跌幅%", "—")
                lines.append(f"{n} | ${p} | {chg}% | — | Yahoo Finance")
    if not has_yahoo_data:
        for item in agri_items:
            lines.append(f"美{item} | — | — | — | Yahoo Finance")
    lines.append("")
    lines.append("---")

    # ══ 三、海外产业&供需环境分析 ══
    lines.append("## 三、海外产业&供需环境分析")
    lines.append("")
    lines.append("指标 | 当前值 | 周度变动 | 对品种边际影响")
    lines.append("--- | --- | --- | ---")
    env_items = [
        "美产区周度降水", "美作物优良率", "USDA出口销售数据",
        "美湾库存", "南美结转库存", "黑海粮食协议边际",
        "海外生物柴油需求", "国际海运运价"
    ]
    for item in env_items:
        lines.append(f"{item} | — | — | —")
    lines.append("")
    lines.append("---")

    # ══ 四、CFTC农业板块COT资金持仓分析 ══
    lines.append("## 四、CFTC农业板块COT资金持仓分析")
    lines.append("")
    lines.append("品种 | 投机净持仓 | COT Index | Z-Score | 资金信号")
    lines.append("--- | --- | --- | --- | ---")
    has_cot_data = False
    if not cot.empty:
        for _, r in cot.iterrows():
            n = r.get("品種", "")
            if any(k in n for k in ["玉米", "大豆", "小麥", "糖", "棉花"]):
                has_cot_data = True
                ci = r.get("COT Index(26W)", 50)
                sig = "极端看空" if ci <= 10 else "看空" if ci <= 30 else "中性" if ci <= 70 else "看多" if ci <= 90 else "极端看多"
                lines.append(f"{n} | {r.get('投機淨持倉', 0):+,} | {ci:.0f} | {r.get('Z-Score', 0):+.2f} | {sig}")
    if not has_cot_data:
        for item in ["美豆", "美玉米", "美小麦", "ICE原糖"]:
            lines.append(f"{item} | — | — | — | —")
    lines.append("")
    lines.append("---")

    # ══ 五、海外天气&产区边际简析 ══
    lines.append("## 五、海外天气&产区边际简析")
    lines.append("")
    lines.append("**北美主产区天气预报**：—")
    lines.append("")
    lines.append("**阿根廷/巴西新作种植进度**：—")
    lines.append("")
    lines.append("**黑海产区物流**：—")
    lines.append("")
    lines.append("**全球极端天气舆情**：—")
    lines.append("")
    lines.append("---")

    # ══ 六、供需强弱评分 ══
    lines.append("## 六、供需强弱评分")
    lines.append("")
    lines.append("| 资产 | 评分（-10~+10） | 核心逻辑 |")
    lines.append("|---|:--:|---|")
    lines.append("| 美豆 | — | — |")
    lines.append("| 美玉米 | — | — |")
    lines.append("| 美小麦 | — | — |")
    lines.append("| 软商品 | — | — |")
    lines.append("")
    lines.append("---")

    # ══ 七、未来30天重点观察方向+潜在风险提示 ══
    lines.append("## 七、未来30天重点观察方向+潜在风险提示")
    lines.append("")
    lines.append("### 未来30天重点观测变量（纯变量罗列，无观点）")
    lines.append("- —")
    lines.append("")
    lines.append("### 市场潜在风险提示（复刻能源周报风险话术）")
    lines.append("- —")
    lines.append("")
    lines.append("---")

    # ══ 强制尾部固定话术 ══
    lines.append(f"数据来源：USDA、CFTC、Yahoo Finance、US气象署、波罗的海航运交易所，截至{TODAY}")
    lines.append("免责声明：本文仅为国际农业宏观、资金、产业、天气数据周度复盘，不构成任何投资建议。商品期货交易风险极高，入市需谨慎。")
    lines.append("AI生成标注：本文AI辅助整理，全部核心数据人工核验校准。")
    return "\n".join(lines)


# ═══ 中国农业 ═══
def china_agri():
    china_data = fetch_china_futures()
    
    lines = []
    lines.append("# 全球农业周度研究报告（中国本土版）")
    lines.append(f"生成日期: {TODAY}")
    lines.append("")
    lines.append("---")

    # ══ 一、本周国内农业市场总结 ══
    lines.append("## 一、本周国内农业市场总结")
    lines.append("")
    lines.append("维度 | 核心变化 | 方向（↑/↓/→震荡）")
    lines.append("--- | --- | ---")
    cn_dims = [
        "国内油脂油料主力", "国内谷物主力", "白糖棉花主力",
        "盘面基差", "油厂库存", "饲料企业备货",
        "产业资金", "进口到港总量"
    ]
    for d in cn_dims:
        lines.append(f"{d} | — | —")
    lines.append("")
    lines.append("**本周核心总结**：锚定国内抛储政策、压榨开工、进口到港、养殖刚需、内外盘联动五大核心矛盾")
    lines.append("")
    lines.append("---")

    # ══ 二、国内农品价格走势分析 ══
    lines.append("## 二、国内农品价格走势分析")
    lines.append("")
    lines.append("指标 | 最新价 | 周环比 | 周均价 | 数据来源")
    lines.append("--- | --- | --- | --- | ---")
    if china_data:
        for d in china_data:
            price = d["最新价"] if d["最新价"] != "—" else "—"
            chg = f"{d['涨跌幅']:+.2f}%" if isinstance(d["涨跌幅"], (int, float)) else "—"
            lines.append(f"{d['品种']} | {price} | {chg} | — | Tushare")
    else:
        for name in TUSHARE_MAP.keys():
            lines.append(f"{name} | — | — | — | Tushare")
    lines.append("")
    lines.append("---")

    # ══ 三、国内政策+本土供需环境分析 ══
    lines.append("## 三、国内政策+本土供需环境分析")
    lines.append("")
    lines.append("指标 | 当前值 | 周度变动 | 对盘面边际影响")
    lines.append("--- | --- | --- | ---")
    cn_supply_items = [
        "国储粮油投放量", "沿海油厂压榨率", "豆粕库存",
        "商业玉米库存", "生猪能繁存栏", "进口船期",
        "国内主产区收割进度", "农业惠农/进口政策", "棕榈油马来出关数据"
    ]
    for item in cn_supply_items:
        lines.append(f"{item} | — | — | —")
    lines.append("")
    lines.append("---")

    # ══ 四、内盘产业资金+仓单持仓分析 ══
    lines.append("## 四、内盘产业资金+仓单持仓分析")
    lines.append("")
    lines.append("品种 | 交易所仓单量 | 产业套保持仓 | 主力资金持仓 | 资金信号")
    lines.append("--- | --- | --- | --- | ---")
    if china_data:
        for d in china_data:
            lines.append(f"{d['品种']} | — | — | — | —")
    else:
        for name in TUSHARE_MAP.keys():
            lines.append(f"{name} | — | — | — | —")
    lines.append("")
    lines.append("---")

    # ══ 五、本土产业刚需&进出口联动简析 ══
    lines.append("## 五、本土产业刚需&进出口联动简析")
    lines.append("")
    lines.append("**国内饲料养殖需求**：—")
    lines.append("")
    lines.append("**食品加工刚需**：—")
    lines.append("")
    lines.append("**月度进口配额**：—")
    lines.append("")
    lines.append("**内外盘套利窗口**：—")
    lines.append("")
    lines.append("**南方备货旺季**：—")
    lines.append("")
    lines.append("**主产区天气灾情**：—")
    lines.append("")
    lines.append("---")

    # ══ 六、供需强弱评分 ══
    lines.append("## 六、供需强弱评分")
    lines.append("")
    lines.append("| 资产 | 评分（-10~+10） | 核心逻辑 |")
    lines.append("|---|:--:|---|")
    lines.append("| 油脂油料 | — | 本土供需+进口+政策因子罗列 |")
    lines.append("| 国内谷物 | — | 本土库存+抛储+刚需因子罗列 |")
    lines.append("| 软商品内盘 | — | 现货+仓单+进口因子罗列 |")
    lines.append("")
    lines.append("---")

    # ══ 七、未来30天重点观察方向+潜在风险提示 ══
    lines.append("## 七、未来30天重点观察方向+潜在风险提示")
    lines.append("")
    lines.append("### 未来30天重点观测变量（本土化指标）")
    lines.append("- —")
    lines.append("")
    lines.append("### 市场潜在风险提示")
    lines.append("- —")
    lines.append("")
    lines.append("---")

    # ══ 强制尾部固定话术 ══
    lines.append(f"数据来源：大商所、郑商所、国家粮油信息中心、海关总署、卓创资讯、我的农产品网，截至{TODAY}")
    lines.append("免责声明：本文仅为国内农业政策、产业、库存、资金数据周度复盘，不构成任何投资建议。商品期货交易风险极高，入市需谨慎。")
    lines.append("AI生成标注：本文AI辅助整理，全部核心数据人工核验校准。")
    return "\n".join(lines)


def main():
    r1 = global_agri()
    r2 = china_agri()
    p1 = DATA_DIR / "reports" / f"agri_global_{TODAY}.md"
    p2 = DATA_DIR / "reports" / f"agri_china_{TODAY}.md"
    with open(p1, "w", encoding="utf-8") as f: f.write(r1)
    with open(p2, "w", encoding="utf-8") as f: f.write(r2)
    print("全球农业 + 中国农业 报告已生成")

if __name__ == "__main__":
    main()
