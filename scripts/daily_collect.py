#!/usr/bin/env python3
"""每日采集FRED+Yahoo，并导入SQLite"""
import sys, sqlite3, csv
from pathlib import Path
from datetime import datetime

# 把 /root/hermes-pipeline 加到模块路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 1. 获取最新数据
import macro_pipeline as m
m.fetch_fred()
m.fetch_yahoo_futures()

today = datetime.now().strftime("%Y-%m-%d")
db_path = str(Path.home() / "hermes-macro-data" / "hermes.db")

def import_csv_to_table(csv_name, table_name):
    csv_path = Path.home() / "hermes-macro-data" / "csv" / today / csv_name
    if not csv_path.exists():
        print(f"[collect] {csv_name} 不存在，跳过")
        return
    db = sqlite3.connect(db_path)
    with open(str(csv_path), encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if not fieldnames:
            print(f"[collect] {csv_name} 为空")
            db.close()
            return
        db.execute(f'DELETE FROM "{table_name}"')
        for row in reader:
            vals = [row[k] for k in fieldnames]
            q = ",".join(["?"] * len(vals))
            c = ",".join([f'"{k}"' for k in fieldnames])
            db.execute(f'INSERT INTO "{table_name}" ({c}) VALUES ({q})', vals)
    db.commit()
    cnt = db.execute(f'SELECT COUNT(*) FROM "{table_name}"').fetchone()[0]
    db.close()
    print(f"[collect] ✅ {csv_name} → {table_name} ({cnt}行)")

# 2. FRED入库
import_csv_to_table("fred_indicators.csv", "fred_indicators")

# 3. Yahoo入库
import_csv_to_table("yahoo_futures.csv", "yahoo_futures")
