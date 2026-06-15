# Historical Data Import (Excel → SQLite)

The user has 15 years of daily market data in Excel files at `D:\commodity_research_platform\export\merged\`. Import to SQLite for chart generation with historical context.

## Source Files

| File | Size | Contents |
|------|------|----------|
| 商品价格.xlsx | 2.5MB | 17 commodities, daily OHLCV from 2011 |
| 宏观经济.xlsx | 1.5MB | 47 sheets (US, EU, CN, JP, BIS indicators) |
| 期货持仓.xlsx | 2.4MB | 17 COT products + FedWatch |
| 能源.xlsx | 1.3MB | 8 AGSI countries + EIA energy data |
| 数据概览.xlsx | 9KB | Metadata |
| 新闻.xlsx | 24KB | News headlines |

## Target Tables (in hermes.db)

| Table | Source | Rows | Span |
|-------|--------|------|------|
| `price_history` | 商品价格.xlsx | 45,262 | 2011-06 ~ 2026-06, 17品种 |
| `macro_history` | 宏观经济.xlsx | 20,054 | 13 US indicators |
| `cot_history` | 期货持仓.xlsx | 10,697 | 17 COT products |
| `energy_history` | 能源.xlsx | 19,317 | AGSI + EIA |

## Data Cleaning

The Excel files contain occasional outlier values (likely from COVID-era volatility or data-entry errors). **Always filter before plotting:**

```python
# Gold price validation: 1000 < price < 6000
# Silver price validation: 5 < price < 200
# WTI price validation: 10 < price < 200

cleaned = [(date, float(close)) for date, close in rows if 1000 < float(close) < 6000]
```

## Import Script Pattern

```python
import pandas as pd, sqlite3
from pathlib import Path

SRC = Path(r"D:\commodity_research_platform\export\merged")
DB = Path.home() / "hermes-macro-data" / "hermes.db"

# Read all sheets, filter useful ones, concatenate, write to SQLite
xl = pd.ExcelFile(SRC / "商品价格.xlsx")
full = pd.concat([
    df[["date","open","high","low","close","volume","commodity","symbol"]]
    for sheet in xl.sheet_names
    if (df := pd.read_excel(xl, sheet_name=sheet)) is not None
    and "date" in df.columns and "close" in df.columns
])
# Rename to Chinese columns
full.columns = ["日期","开盘","最高","最低","收盘","成交量","品种","代码"]
full.to_sql("price_history", conn, if_exists="replace", index=False)
```

## Deployment

The import script runs LOCALLY (Windows) because the Excel files are on the user's D: drive. After import, SCP the resulting hermes.db (~8MB) to VPS:

```bash
scp -P 58234 -i /d/hermes-ssh/id_ed25519 \
  /c/Users/Administrator/hermes-macro-data/hermes.db \
  root@45.77.126.71:/root/hermes-macro-data/hermes.db
```

Keep a backup (`cp hermes.db hermes.db.bak`) before overwriting on VPS — the daily pipeline writes its own tables there.
