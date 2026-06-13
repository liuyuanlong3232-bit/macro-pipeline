import sqlite3
from pathlib import Path
db = sqlite3.connect(str(Path.home() / "hermes-macro-data" / "hermes.db"))
tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
for t in tables:
    n = db.execute(f"SELECT COUNT(*) FROM \"{t[0]}\"").fetchone()[0]
    print(f"{t[0]}: {n}行")
    if n > 0 and t[0] == "price_history":
        items = db.execute("SELECT DISTINCT 品种 FROM price_history").fetchall()
        print(f"  品种: {[r[0] for r in items]}")
        for item in items[:3]:
            cnt = db.execute(f"SELECT COUNT(*) FROM price_history WHERE 品种='{item[0]}'").fetchone()[0]
            print(f"    {item[0]}: {cnt}行, 最早: ", end="")
            r = db.execute(f"SELECT min(日期), max(日期) FROM price_history WHERE 品种='{item[0]}'").fetchone()
            print(f"{r[0]} ~ {r[1]}")
db.close()
