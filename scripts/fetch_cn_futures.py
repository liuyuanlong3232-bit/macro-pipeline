#!/usr/bin/env python3
"""
中国期货行情采集 — Tushare API
品种: 大商所(生猪/豆粕/玉米/大豆) + 郑商所(小麦)
认证: TUSHARE_TOKEN (2000积分免费)
"""
import os, sys, requests, sqlite3
from pathlib import Path
from datetime import datetime, timedelta

# ── 配置 ──
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.utils import load_env, DATA_DIR
load_env()
token = os.getenv("TUSHARE_TOKEN", "")

now = datetime.now()
today_str = now.strftime("%Y%m%d")
start_str = (now - timedelta(days=3)).strftime("%Y%m%d")

TUSHARE_URL = "http://api.tushare.pro"

# ── 品种定义 (ts_code → 名称/单位) ──
# ⚠️ 注意：合约代码含到期月份（如2607=2026年07月），到期后需手动更新为下一主力合约
CONTRACTS = {
    "LH2607.DCE": ("生猪", "元/吨"),   # ⚠️ 2026年07月到期，到期前需换月
    "M2607.DCE": ("豆粕", "元/吨"),
    "C2607.DCE": ("玉米", "元/吨"),
    "A2607.DCE": ("大豆一号", "元/吨"),
    "CS2607.DCE": ("玉米淀粉", "元/吨"),
    "WH2607.CZC": ("强麦", "元/吨"),
}

DB = str(Path.home() / "hermes-macro-data" / "hermes.db")

# ── 建表 ──
conn = sqlite3.connect(DB)
conn.execute("""CREATE TABLE IF NOT EXISTS cn_futures (
    symbol TEXT, name TEXT, date TEXT,
    close REAL, pre_close REAL, vol REAL,
    change_pct REAL, unit TEXT,
    source TEXT, fetched_at TEXT,
    PRIMARY KEY (symbol, date)
)""")
conn.commit()

total = 0
for code, (name, unit) in CONTRACTS.items():
    try:
        payload = {
            "api_name": "fut_daily",
            "token": token,
            "params": {"ts_code": code, "start_date": start_str, "end_date": today_str},
            "fields": "ts_code,trade_date,close,pre_close,vol"
        }
        r = requests.post(TUSHARE_URL, json=payload, timeout=15)
        data = r.json()
        if data.get("code") != 0:
            print("FAIL {}: code={}".format(code, data.get("code")))
            continue
        items = data.get("data", {}).get("items", [])
        if not items:
            print("NONE {}: 无数据".format(code))
            continue
        
        latest = items[0]
        close_val = float(latest[2]) if latest[2] else 0
        pre_close = float(latest[3]) if latest[3] else 0
        vol_val = float(latest[4]) if len(latest) > 4 and latest[4] else 0
        chg_pct = round((close_val - pre_close) / pre_close * 100, 2) if pre_close else 0
        trade_date = latest[1]
        
        conn.execute("""INSERT OR REPLACE INTO cn_futures 
            (symbol, name, date, close, pre_close, vol, change_pct, unit, source, fetched_at)
            VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (code, name, trade_date, close_val, pre_close, vol_val, chg_pct,
             unit, "Tushare API", now.strftime("%Y-%m-%d %H:%M")))
        total += 1
        print("OK {} {}: ¥{:.0f} ({:+.1f}%) {}手".format(code, name, close_val, chg_pct, int(vol_val)))
    except Exception as e:
        print("FAIL {}: {}".format(code, e))

conn.commit()
conn.close()
print("\n{}条已入库".format(total))
