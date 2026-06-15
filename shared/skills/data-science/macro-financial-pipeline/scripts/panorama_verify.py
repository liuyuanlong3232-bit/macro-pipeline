#!/usr/bin/env python3
"""
One-command data panorama check for macro-financial pipeline.
Run on VPS:  cd /root/hermes-pipeline && python3 panorama.py
Shows all data sources in one table with CSV-vs-real-time diff.
"""
import os, sys
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import requests

DATA_DIR = Path("/root/hermes-macro-data")
TODAY = datetime.now().strftime("%Y-%m-%d")

def load(name):
    p = DATA_DIR / "csv" / TODAY / f"{name}.csv"
    if p.exists(): return pd.read_csv(p)
    y = (datetime.now()-timedelta(1)).strftime("%Y-%m-%d")
    p = DATA_DIR / "csv" / y / f"{name}.csv"
    if p.exists(): return pd.read_csv(p)
    return None

def yahoo(sym):
    try:
        r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}",
            params={"range":"1d","interval":"1d"},
            headers={"User-Agent":"Mozilla/5.0"}, timeout=10)
        if r.status_code==200:
            return r.json()["chart"]["result"][0]["meta"]["regularMarketPrice"]
    except: pass
    return None

def gv(df, kw):
    if df is None: return "—"
    nc = [c for c in df.columns if "品" in c or "指" in c]
    vc = [c for c in df.columns if "價" in c or "值" in c]
    if not nc or not vc: return "—"
    sub = df[df[nc[0]].astype(str).str.contains(kw, na=False)]
    if sub.empty: return "—"
    return str(sub.iloc[0][vc[0]])

def section(title): print(f"\n【{title}】")

print("="*90)
print(f"数据全景检查 | {TODAY}")
print("="*90)

section("宏观")
fr = load("fred_indicators")
for name, kw in [("CPI","CPI"),("核心PCE","核心PCE"),("非农","非農"),
                 ("失业率","失業率"),("联邦基金","聯邦基金"),
                 ("10Y国债","10Y"),("TIPS","TIPS"),("DXY(FRED)","美元指數")]:
    v = gv(fr, kw)
    print(f"  {name:12s}: {v}")

# Also verify Tushare China data
try:
    from dotenv import load_dotenv
    import tushare as ts
    load_dotenv()
    ts.set_token(os.getenv("TUSHARE_TOKEN"))
    pro = ts.pro_api()
    cpi = pro.cn_cpi(start_m="202605", end_m="202606").iloc[0]
    pmi = pro.cn_pmi(start_m="202605", end_m="202606").iloc[0]
    print(f"  中国CPI: {cpi['nt_yoy']}% | 中国PMI: {pmi['PMI010100']}")
except Exception as e:
    print(f"  Tushare: {str(e)[:40]}")

section("商品(CSV vs Yahoo实时)")
yh = load("yahoo_futures")
for name, kw, ys in [("黄金","黃金","GC=F"),("白银","白銀","SI=F"),
                      ("WTI","WTI","CL=F"),("Brent","Brent","BZ=F"),
                      ("天然气","天然氣","NG=F"),("玉米","玉米","ZC=F"),
                      ("大豆","大豆","ZS=F"),("小麦","小麥","ZW=F"),
                      ("豆油","豆油","ZL=F"),("豆粕","豆粕","ZM=F")]:
    csv_v = gv(yh, kw)
    yh_v = yahoo(ys)
    status = "✅" if not yh_v else "⚠️" if abs(float(gv(yh,kw) or 0)-yh_v)>5 else "✅"
    print(f"  {name:10s} CSV:{csv_v:>10s} | 实时:${yh_v:.2f}" if yh_v else f"  {name:10s} CSV:{csv_v:>10s} | 实时:无")

section("CFTC持仓")
ct = load("cotdata")
if ct is not None:
    nc = [c for c in ct.columns if "品" in c][0]
    for _, r in ct.iterrows():
        print(f"  {r[nc]:12s} 净{int(r.get('投機淨持倉',0)):+,} | Index {r.get('COT Index(26W)',50):.0f}")

section("欧洲天然气(AGSI+)")
agsi = load("agsi_eu_gas")
if agsi is not None:
    print(f"  {agsi.shape[0]}条, 最新填充率 {gv(agsi,'Germany')[:5]}%")

print(f"\n{'='*90}")
print("检查完毕")
