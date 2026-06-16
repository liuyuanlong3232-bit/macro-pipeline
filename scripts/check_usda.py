import sqlite3
from pathlib import Path
from datetime import datetime

db = str(Path.home() / "hermes-macro-data" / "hermes.db")
if not Path(db).exists():
    print("[USDA提醒] 数据库不存在")
    exit()

conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute("SELECT MAX(日期) FROM usda_agriculture")
row = cur.fetchone()
if row and row[0]:
    last = row[0]
    days = (datetime.now() - datetime.strptime(last, "%Y-%m-%d")).days
    if days > 3:
        print(f"[USDA提醒] 数据已{days}天未更新, 最新:{last}")
        print("操作: 双击本地 scripts/usda_sync.bat")
    else:
        print(f"[USDA] 正常, 最新:{last}")
else:
    print("[USDA提醒] 无数据, 需手动采集")
conn.close()
