"""清理异常价格数据"""
import sqlite3
from pathlib import Path

DB = Path.home() / "hermes-macro-data" / "hermes.db"
db = sqlite3.connect(str(DB))

# 黄金：2024年之后低于$2000的都是错误数据（实际黄金2024最低$1990）
deleted_gold = db.execute("""
    DELETE FROM price_history 
    WHERE 品种='gold' 
    AND substr(日期,1,4) >= '2024'
    AND 收盘 < 2000
""").rowcount
print(f"删除黄金异常值: {deleted_gold}行")

# 白银：2024年之后低于$20的都是错误数据（实际白银2024最低$22）
deleted_silver = db.execute("""
    DELETE FROM price_history 
    WHERE 品种='silver' 
    AND substr(日期,1,4) >= '2024'
    AND 收盘 < 20
""").rowcount
print(f"删除白银异常值: {deleted_silver}行")

db.commit()

# 验证
print()
print("=== 验证 ===")
for item in ['gold', 'silver']:
    r = db.execute(f"""
        SELECT MIN(收盘), AVG(收盘), MAX(收盘), COUNT(*), MIN(日期), MAX(日期) 
        FROM price_history WHERE 品种='{item}'
    """).fetchone()
    print(f"  {item}: ${r[0]:.0f}~${r[3]:.0f}行 平均${r[1]:.0f} 最高${r[2]:.0f} ({r[4]}~{r[5]})")

db.close()
