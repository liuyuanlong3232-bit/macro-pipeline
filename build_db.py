#!/usr/bin/env python3
"""每天采集完后更新SQLite数据库"""
import os, sys
from datetime import datetime
from pathlib import Path
import pandas as pd
import sqlite3

DATA_DIR = Path.home() / "hermes-macro-data"
TODAY = datetime.now().strftime("%Y-%m-%d")
DB_PATH = DATA_DIR / "hermes.db"

def build_db():
    csv_dir = DATA_DIR / "csv" / TODAY
    if not csv_dir.exists():
        print(f"今日数据不存在: {csv_dir}")
        # 回退到最新的目录
        dates = sorted([d for d in (DATA_DIR/"csv").iterdir() if d.is_dir()], reverse=True)
        if not dates:
            print("无数据目录")
            return
        csv_dir = dates[0]
        print(f"回退到: {csv_dir}")

    conn = sqlite3.connect(str(DB_PATH))
    
    for csv_file in sorted(csv_dir.glob("*.csv")):
        try:
            df = pd.read_csv(csv_file)
            table = csv_file.stem.replace("-", "_").replace(" ", "_").lower()
            # 清空旧数据插入新数据
            df.to_sql(table, conn, if_exists="replace", index=False)
            print(f"  ✅ {table}: {len(df)} 行")
        except Exception as e:
            print(f"  ❌ {csv_file.name}: {e}")

    conn.close()
    print(f"\n数据库: {DB_PATH}")
    # 复用连接查询表数量
    conn = sqlite3.connect(str(DB_PATH))
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print(f"表数量: {len(tables)}")
    conn.close()

if __name__ == "__main__":
    build_db()
