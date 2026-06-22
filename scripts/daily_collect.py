#!/usr/bin/env python3
"""每日采集FRED+Yahoo，并导入SQLite"""
import sys, sqlite3, csv
from pathlib import Path
from datetime import datetime

# 动态定位项目根目录
PIPELINE_ROOT = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, PIPELINE_ROOT)

# 1. 获取最新数据
import macro_pipeline as m
m.fetch_fred()
m.fetch_yahoo_futures()

today = datetime.now().strftime("%Y-%m-%d")
db_path = str(Path.home() / "hermes-macro-data" / "hermes.db")

# 允许导入的表名白名单，防止SQL注入
ALLOWED_TABLES = {"fred_indicators", "yahoo_futures", "cotdata", "eia_energy",
                  "agsi_eu_gas", "commodity_prices", "financial_news", "vix_data"}

def import_csv_to_table(csv_name, table_name):
    # 白名单校验表名
    if table_name not in ALLOWED_TABLES:
        print(f"[collect] ❌ 非法表名: {table_name}")
        return
    csv_path = Path.home() / "hermes-macro-data" / "csv" / today / csv_name
    if not csv_path.exists():
        print(f"[collect] {csv_name} 不存在，跳过")
        return
    db = sqlite3.connect(db_path)
    with open(str(csv_path), encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if not fieldnames:
            print(f"[collect] {csv_name} 为空")
            db.close()
            return
        # 列名安全处理：只允许字母/数字/下划线/中文
        import re
        safe_cols = [c for c in fieldnames if re.match(r'^[\w\u4e00-\u9fff%]+$', c)]
        if len(safe_cols) != len(fieldnames):
            print(f"[collect] ⚠️ {csv_name} 含非法列名，已过滤")
        col_str = ",".join(f'"{c}"' for c in safe_cols)
        db.execute(f'DELETE FROM "{table_name}"')
        for row in reader:
            vals = [row[k] for k in safe_cols]
            q = ",".join(["?"] * len(vals))
            db.execute(f'INSERT INTO "{table_name}" ({col_str}) VALUES ({q})', vals)
    db.commit()
    cnt = db.execute(f'SELECT COUNT(*) FROM "{table_name}"').fetchone()[0]
    db.close()
    print(f"[collect] ✅ {csv_name} → {table_name} ({cnt}行)")

# 2. FRED入库
import_csv_to_table("fred_indicators.csv", "fred_indicators")

# 3. Yahoo入库
import_csv_to_table("yahoo_futures.csv", "yahoo_futures")

# 4. 伦锡入库 (AKShare)
try:
    import macro_pipeline as mp
    tin_df = mp.fetch_akshare_tin()
    if tin_df is not None and not tin_df.empty:
        print("[collect] 伦锡数据已采集")
except Exception as e:
    print(f"[collect] 伦锡采集失败: {e}")
