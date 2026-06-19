#!/usr/bin/env python3
"""合并所有CSV文件更新SQLite数据库（取每个表的最新数据）"""
import os, sys
from pathlib import Path
import pandas as pd
import sqlite3

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared.utils import DATA_DIR

DB_PATH = DATA_DIR / "hermes.db"

def build_db():
    csv_base = DATA_DIR / "csv"
    if not csv_base.exists():
        print("无CSV目录")
        return

    # 收集所有CSV文件，按表名分组
    table_files = {}
    for date_dir in sorted(csv_base.iterdir()):
        if not date_dir.is_dir():
            continue
        for csv_file in date_dir.glob("*.csv"):
            table = csv_file.stem.replace("-", "_").replace(" ", "_").lower()
            if table not in table_files:
                table_files[table] = []
            table_files[table].append((date_dir.name, csv_file))

    conn = sqlite3.connect(str(DB_PATH))

    for table, files in sorted(table_files.items()):
        # 取每个表的最新文件（按日期排序最后一个）
        latest_date, latest_file = files[-1]
        try:
            df = pd.read_csv(latest_file)
            df.to_sql(table, conn, if_exists="replace", index=False)
            print(f"  ✅ {table}: {len(df)} 行 (from {latest_date})")
        except Exception as e:
            print(f"  ❌ {table}: {e}")

    conn.close()
    print(f"\n数据库: {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print(f"表数量: {len(tables)}")
    conn.close()

if __name__ == "__main__":
    build_db()
