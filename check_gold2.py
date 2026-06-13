"""检查黄金数据中的异常值"""
import sqlite3
from pathlib import Path

db = sqlite3.connect(str(Path.home() / "hermes-macro-data" / "hermes.db"))

# 全部黄金数据按价格排序
rows = db.execute("""
    SELECT 日期, 收盘, 品种 
    FROM price_history 
    WHERE 品种='gold' 
    ORDER BY 收盘 ASC
""").fetchall()

print(f"黄金总行数: {len(rows)}")
print()

# 看最低的20条
print("=== 价格最低的20条 ===")
for r in rows[:20]:
    print(f"  {r[0]}: ${r[1]:.2f}")

print()

# 看最高的20条
print("=== 价格最高的20条 ===")
rows_desc = db.execute("""
    SELECT 日期, 收盘 
    FROM price_history 
    WHERE 品种='gold' 
    ORDER BY 收盘 DESC 
    LIMIT 20
""").fetchall()
for r in rows_desc:
    print(f"  {r[0]}: ${r[1]:.2f}")

print()

# 按年份统计最大值、最小值
print("=== 按年份统计 ===")
years = db.execute("""
    SELECT substr(日期,1,4) as yr, 
           MIN(收盘), AVG(收盘), MAX(收盘), COUNT(*) 
    FROM price_history 
    WHERE 品种='gold' 
    GROUP BY yr 
    ORDER BY yr
""").fetchall()
for r in years:
    print(f"  {r[0]}: 最低${r[1]:.0f}  平均${r[2]:.0f}  最高${r[3]:.0f}  ({r[4]}行)")

db.close()
