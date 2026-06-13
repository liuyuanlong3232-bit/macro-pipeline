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
    lines.append("# 全球农业周度研究报告")
    lines.append(f"生成日期: {TODAY}")
    lines.append("")
    lines.append("---")
    lines.append("## 一、本周农产品市场总结")
    lines.append("")

    if not yahoo.empty:
        agri = yahoo[yahoo["品種"].str.contains("玉米|大豆|小麥|豆油|豆粕|棉花|糖", na=False)]
        for _, r in agri.iterrows():
            n = r.get("品種","")
            p = r.get("最新價","—")
            c = r.get("日漲跌幅%","")
            em = "↑" if c and not str(c).startswith("-") and str(c) != "0" else "↓" if c else ""
            if p != "—":
                lines.append(f"- {em} {n}: ${p} ({c})")
    
    lines.append("")
    lines.append("---")
    lines.append("## 二、关键品种价格表")
    lines.append("")
    lines.append("品种 | 价格 | 日涨跌幅 | 来源")
    lines.append("--- | --- | --- | ---")
    for _, r in yahoo.iterrows() if not yahoo.empty else []:
        n = r.get("品種","")
        if any(k in n for k in ["玉米","大豆","小麥","豆油","豆粕","棉花","糖"]):
            lines.append(f"{n} | ${r.get('最新價','—')} | {r.get('日漲跌幅%','—')}% | Yahoo")
    lines.append("")

    lines.append("---")
    lines.append("## 三、CFTC资金持仓")
    lines.append("")
    lines.append("品种 | 投机净持仓 | COT Index | Z-Score | 信号")
    lines.append("--- | --- | --- | --- | ---")
    if not cot.empty:
        for _, r in cot.iterrows():
            n = r.get("品種","")
            if any(k in n for k in ["玉米","大豆","小麥","糖","棉花"]):
                ci = r.get("COT Index(26W)",50)
                sig = "极端看空" if ci <= 10 else "看空" if ci <= 30 else "中性" if ci <= 70 else "看多" if ci <= 90 else "极端看多"
                lines.append(f"{n} | {r.get('投機淨持倉',0):+,} | {ci:.0f} | {r.get('Z-Score',0):+.2f} | {sig}")
    lines.append("")

    lines.append("---")
    lines.append("**数据来源**: Yahoo Finance、CFTC COT")
    return "\n".join(lines)

# ═══ 中国农业 ═══
def china_agri():
    china_data = fetch_china_futures()
    
    lines = []
    lines.append("# 中国农业周度研究报告")
    lines.append(f"生成日期: {TODAY}")
    lines.append("")
    lines.append("---")
    lines.append("## 一、本周中国市场总结")
    lines.append("")

    if china_data:
        for d in china_data:
            chg = d.get("涨跌幅","")
            price = d.get("最新价","—")
            em = "↑" if isinstance(chg, (int,float)) and chg > 0 else "↓" if isinstance(chg, (int,float)) and chg < 0 else ""
            if price != "—":
                lines.append(f"- {em} {d['品种']}: {price} (涨跌{chg:+.2f}%)")
        lines.append("")
    else:
        lines.append("> 中国农产品期货数据本次未获取到 (Tushare可能无当日数据)")
        lines.append("")

    lines.append("---")
    lines.append("## 二、关键品种价格")
    lines.append("")
    lines.append("品种 | 交易所 | 最新价 | 涨跌幅 | 来源")
    lines.append("--- | --- | --- | --- | ---")
    if china_data:
        for d in china_data:
            ex = "DCE" if d["品种"] in ("豆粕","豆油","玉米","豆一","生猪","棕榈油","鸡蛋") else "CZCE"
            price = d["最新价"] if d["最新价"] != "—" else "—"
            chg = f"{d['涨跌幅']:+.2f}%" if isinstance(d["涨跌幅"], (int,float)) else "—"
            lines.append(f"{d['品种']} | {ex} | {price} | {chg} | Tushare")
    else:
        for name, ts_code in TUSHARE_MAP.items():
            ex = "DCE" if ts_code in ("M","Y","C","A","LH","JD","P") else "CZCE"
            lines.append(f"{name} | {ex} | 未获取 | — | Tushare")
    lines.append("")

    lines.append("---")
    lines.append("## 三、现货基差与供需")
    lines.append("")
    if china_data:
        lines.append("数据基于Tushare主力合约收盘价")
    lines.append("1) 豆粕: 现货端随进口大豆到港节奏波动")
    lines.append("2) 玉米: 售粮进度与深加工需求")
    lines.append("3) 生猪: 能繁母猪存栏与猪周期位置")
    lines.append("4) 白糖: 广西压榨进度与进口配额")
    lines.append("")

    lines.append("---")
    lines.append("**数据来源**: Tushare大商所/郑商所")
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
