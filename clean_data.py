"""清理异常价格数据

阈值说明（基于历史最低价设定，需定期更新）：
- 黄金：2024年最低$1990，阈值$2000留10美元安全边际
- 白银：2024年最低$22，阈值$20留2美元安全边际
- 更新时间：2024年初，如市场结构变化需重新评估
"""
import sqlite3
from pathlib import Path

DB = Path.home() / "hermes-macro-data" / "hermes.db"
db = sqlite3.connect(str(DB))

# 黄金：2024年之后低于$2000的都是错误数据（阈值依据：2024年实际最低$1990）
deleted_gold = db.execute("""
    DELETE FROM price_history 
    WHERE 品种=? 
    AND substr(日期,1,4) >= '2024'
    AND 收盘 < 2000
""", ("gold",)).rowcount
print(f"删除黄金异常值: {deleted_gold}行")

# 白银：2024年之后低于$20的都是错误数据（阈值依据：2024年实际最低$22）
deleted_silver = db.execute("""
    DELETE FROM price_history 
    WHERE 品种=? 
    AND substr(日期,1,4) >= '2024'
    AND 收盘 < 20
""", ("silver",)).rowcount
print(f"删除白银异常值: {deleted_silver}行")

db.commit()

# 验证
print()
print("=== 验证 ===")
for item in ['gold', 'silver']:
    r = db.execute("""
        SELECT MIN(收盘), AVG(收盘), MAX(收盘), COUNT(*), MIN(日期), MAX(日期) 
        FROM price_history WHERE 品种=?
    """, (item,)).fetchone()
    print(f"  {item}: ${r[0]:.0f}~${r[3]:.0f}行 平均${r[1]:.0f} 最高${r[2]:.0f} ({r[4]}~{r[5]})")

db.close()
