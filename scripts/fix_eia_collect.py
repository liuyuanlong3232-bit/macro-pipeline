#!/usr/bin/env python3
"""最终修复：EIA采集函数扩展+入库"""
import os, sys, requests
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

# 读EIA_KEY
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.utils import load_env, DATA_DIR
load_env()
key = os.getenv("EIA_API_KEY", "")

today = datetime.now().strftime("%Y-%m-%d")
EIA_BASE = "https://api.eia.gov/v2"
results = []

# 1. 原油库存
r = requests.get(f"{EIA_BASE}/petroleum/stoc/wstk/data/", params={
    "api_key": key, "frequency": "weekly", "data[0]": "value",
    "facets[duoarea][]": "NUS", "facets[product][]": "EPC0",
    "sort[0][column]": "period", "sort[0][direction]": "desc",
    "offset": 0, "length": 12}, timeout=15)
if r.status_code == 200:
    for item in r.json()["response"]["data"]:
        results.append({"來源":"EIA","類別":"原油庫存","日期":item["period"],"數值":item["value"],"單位":"千桶","抓取日":today})

# 2. 汽油库存
r2 = requests.get(f"{EIA_BASE}/petroleum/stoc/wstk/data/", params={
    "api_key": key, "frequency": "weekly", "data[0]": "value",
    "facets[duoarea][]": "NUS", "facets[product][]": "EPM0C",
    "sort[0][column]": "period", "sort[0][direction]": "desc",
    "offset": 0, "length": 12}, timeout=15)
if r2.status_code == 200:
    for item in r2.json()["response"]["data"]:
        results.append({"來源":"EIA","類別":"汽油庫存","日期":item["period"],"數值":item["value"],"單位":"千桶","抓取日":today})

# 3. 原油产量
r3 = requests.get(f"{EIA_BASE}/petroleum/crd/crpdn/data/", params={
    "api_key": key, "frequency": "monthly", "data[0]": "value",
    "facets[duoarea][]": "NUS", "facets[product][]": "EPC0",
    "sort[0][column]": "period", "sort[0][direction]": "desc",
    "offset": 0, "length": 6}, timeout=15)
if r3.status_code == 200:
    for item in r3.json()["response"]["data"]:
        results.append({"來源":"EIA","類別":"原油產量","日期":item["period"],"數值":item["value"],"單位":"千桶/日","抓取日":today})

# 4. 天然气库存
r4 = requests.get(f"{EIA_BASE}/natural-gas/stor/wkly/data/", params={
    "api_key": key, "frequency": "weekly", "data[0]": "value",
    "facets[series][]": "NG.N9010US2.W",
    "sort[0][column]": "period", "sort[0][direction]": "desc",
    "offset": 0, "length": 12}, timeout=15)
if r4.status_code == 200:
    for item in r4.json()["response"]["data"]:
        results.append({"來源":"EIA","類別":"天然氣庫存","日期":item["period"],"數值":item["value"],"單位":"Bcf","抓取日":today})

print(f"EIA采集: {len(results)}条")
for r in results[:5]:
    print(f"  {r['日期']} | {r['類別']}: {r['數值']} {r['單位']}")

# 写入SQLite
if results:
    import sqlite3
    db = sqlite3.connect(str(Path.home() / "hermes-macro-data" / "hermes.db"))
    for r in results:
        db.execute("""INSERT OR REPLACE INTO eia_energy ("來源","類別","日期","數值","單位","抓取日")
                      VALUES (?,?,?,?,?,?)""",
                   (r["來源"], r["類別"], r["日期"], r["數值"], r["單位"], r["抓取日"]))
    db.commit()
    cnt = db.execute("SELECT COUNT(*) FROM eia_energy").fetchone()[0]
    db.close()
    print(f"eia_energy: {cnt}行")

# 同时保存CSV
df = pd.DataFrame(results)
csv_dir = Path.home() / "hermes-macro-data" / "csv" / today
csv_dir.mkdir(parents=True, exist_ok=True)
df.to_csv(str(csv_dir / "eia_energy.csv"), index=False, encoding="utf-8-sig")
print(f"CSV已保存")
