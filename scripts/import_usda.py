#!/usr/bin/env python3
"""手动导入本地采集的USDA CSV到数据库"""
import os, sys
from pathlib import Path
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")
csv_dir = Path.home() / "hermes-macro-data" / "csv" / today
csv_file = csv_dir / "usda_agriculture.csv"

if not csv_file.exists():
    print(f"❌ 未找到USDA数据文件: {csv_file}")
    print("请先在本地运行采集，然后 scp 到VPS")
    sys.exit(1)

print(f"📄 找到USDA数据文件: {csv_file}")

# 导入到数据库
import sqlite3, csv
db = sqlite3.connect(str(Path.home() / "hermes-macro-data" / "hermes.db"))

with open(str(csv_file), "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

if not rows:
    print("❌ CSV为空")
    sys.exit(1)

# 清空旧数据
db.execute("DELETE FROM usda_agriculture")

# 写入新数据
for row in rows:
    cols = ", ".join(f{k} for k in row.keys())
    vals = ", ".join(f{v} for v in row.values())
    db.execute(f"INSERT INTO usda_agriculture ({cols}) VALUES ({vals})")

db.commit()
db.close()
print(f"✅ 已导入 {len(rows)} 条USDA数据")
print("📊 运行报告: python3 run_report.py agri")
