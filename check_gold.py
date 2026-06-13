import sqlite3
from pathlib import Path
db = sqlite3.connect(str(Path.home() / "hermes-macro-data" / "hermes.db"))
rows = db.execute("SELECT 日期, 收盘 FROM price_history WHERE 品种 = 'gold' ORDER BY 日期 DESC LIMIT 10").fetchall()
print("黄金最近10条:")
for r in rows:
    print(f"  {r[0]}: {r[1]}")
rows2 = db.execute("SELECT 日期, 收盘 FROM price_history WHERE 品种 = 'gold' ORDER BY 日期 ASC LIMIT 3").fetchall()
print("最早3条:")
for r in rows2:
    print(f"  {r[0]}: {r[1]}")
db.close()
