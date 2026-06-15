# 数据时效性：CSV → SQLite 导入链

## 问题

2026-06-15 发现：日报显示的价格是6月12日（周五）的，不是6月15日（周一）的。

根因：`macro_pipeline.fetch_yahoo_futures()` 只保存CSV，不导入SQLite。日报脚本从数据库读数据，所以一直拿到旧值。

## 数据流向

```
Yahoo API → fetch_yahoo_futures() → CSV文件
                                     ↓
                               daily_collect.py → SQLite ← daily_report.py
```

如果没有第二步（CSV → SQLite），日报永远用的是上次手动导入的数据，而不是当天采集的最新数据。

## 修复方案

创建 `scripts/daily_collect.py`，在采集后自动执行CSV → SQLite导入：

```python
# 1. 采集
import macro_pipeline as m
m.fetch_fred()
m.fetch_yahoo_futures()

# 2. 导入CSV到数据库
import sqlite3, csv
from pathlib import Path
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")
csv_path = Path.home() / "hermes-macro-data" / "csv" / today / "yahoo_futures.csv"

db = sqlite3.connect(str(Path.home() / "hermes-macro-data" / "hermes.db"))
with open(str(csv_path), encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    db.execute("DELETE FROM yahoo_futures")
    for row in reader:
        cols = list(row.keys())
        vals = [row[k] for k in cols]
        q = ",".join(["?"] * len(vals))
        c = ",".join([f'"{k}"' for k in cols])
        db.execute(f"INSERT INTO yahoo_futures ({c}) VALUES ({q})", vals)
db.commit()
db.close()
```

## 验证

采集后检查数据库中的最新日期：

```sql
SELECT 品種, 最新價, 日期 FROM yahoo_futures LIMIT 3;
```

日期应与当天匹配（或最近交易日，周末时）。

## CRITICAL数据库查询注意

| 表 | 列名 | 注意事项 |
|---|------|---------|
| fred_indicators | `系列ID` | **不是** `系列` |
| yahoo_futures | `日漲跌幅%` | 列名含%需引号包裹 |
| cotdata | `COT Index(26W)` | 列名含括号需引号包裹 |
| cotdata | 品種值 | **简体** (`黄金`) 不是繁体 (`黃金`) |
| yahoo_futures | 品種值 | **繁体** (`黃金`) 不是简体 (`黄金`) |
| vix_data | 品種=`VIX` | VIX在独立表中，不在 yahoo_futures |
