#!/usr/bin/env python3
"""把最新Yahoo CSV导入SQLite数据库"""
import sqlite3, csv
from pathlib import Path
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")
csv_path = Path.home() / "hermes-macro-data" / "csv" / today / "yahoo_futures.csv"

if not csv_path.exists():
    print(f"[import_yahoo] CSV不存在: {csv_path}")
    exit(1)

db = sqlite3.connect(str(Path.home() / "hermes-macro-data" / "hermes.db"))
with open(str(csv_path), encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    db.execute("DELETE FROM yahoo_futures")
    for row in reader:
        cols = [k for k in row.keys()]
        vals = [row[k] for k in cols]
        q = ",".join(["?"] * len(vals))
        c = ",".join([f"\"{k}\"" for k in cols])
        db.execute(f"INSERT INTO yahoo_futures ({c}) VALUES ({q})", vals)
db.commit()
db.close()
print(f"[import_yahoo] 导入完成: {csv_path}")
