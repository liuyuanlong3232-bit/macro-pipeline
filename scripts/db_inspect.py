#!/usr/bin/env python3
"""检查VPS数据仓库结构"""
import sqlite3
from pathlib import Path

db = "/root/hermes-macro-data/hermes.db"
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print(f"📦 {db} ({len(tables)}张表)")
for t in tables:
    cur.execute(f'SELECT COUNT(*) FROM "{t}"')
    cnt = cur.fetchone()[0]
    cur.execute(f'PRAGMA table_info("{t}")')
    cols = [r[1] for r in cur.fetchall()]
    print(f"  📊 {t}: {cnt}行")
    print(f"     列: {cols}")
conn.close()
