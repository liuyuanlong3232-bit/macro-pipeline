# SQLite Daily Import (build_db.py)

## Purpose

Import all daily CSVs into a single SQLite database for fast mid-conversation queries. The agent can answer "黄金最新价多少" or "COT净多最高的是哪个" with a single SQL query instead of hunting through CSV files.

## File Location

`~/hermes-macro-pipeline/build_db.py`

## Core Logic

```python
DATA_DIR = Path.home() / "hermes-macro-data"
TODAY = datetime.now().strftime("%Y-%m-%d")
DB_PATH = DATA_DIR / "hermes.db"

csv_dir = DATA_DIR / "csv" / TODAY
if not csv_dir.exists():
    # fallback to latest data dir
    dates = sorted([d for d in (DATA_DIR/"csv").iterdir() if d.is_dir()], reverse=True)
    csv_dir = dates[0]

conn = sqlite3.connect(str(DB_PATH))
for csv_file in sorted(csv_dir.glob("*.csv")):
    df = pd.read_csv(csv_file)
    table = csv_file.stem.replace("-", "_").replace(" ", "_").lower()
    df.to_sql(table, conn, if_exists="replace", index=False)
conn.close()
```

## Deploy & Cron Chain

On VPS, chain after main collection:

```bash
# crontab
0 8 * * * cd /root/hermes-pipeline && python3 macro_pipeline.py && python3 build_db.py >> /var/log/hermes.log 2>&1
```

## VPS Verification

```bash
ssh -p PORT -i KEY root@IP 'cd /root/hermes-pipeline && python3 build_db.py'
# Should print: ✅ table_name: N rows for each source
```

## Common Queries

```python
import sqlite3; from pathlib import Path
db = sqlite3.connect(str(Path.home() / "hermes-macro-data" / "hermes.db"))

# Latest FRED indicators
db.execute("""
    SELECT 指標, 數值, 日期 FROM fred_indicators 
    WHERE 日期 = (SELECT MAX(日期) FROM fred_indicators WHERE 指標 = '聯邦基金利率')
    ORDER BY 指標
""").fetchall()

# COT by net position (descending)
db.execute('SELECT 品種, "投機淨持倉", "COT Index(26W)" FROM cotdata ORDER BY "投機淨持倉" DESC').fetchall()

# Futures prices (descending)
db.execute('SELECT 品種, 最新價 FROM yahoo_futures ORDER BY 最新價 DESC').fetchall()

# List all tables
db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
```

**Note:** Always quote column names containing special chars with double quotes: `"COT Index(26W)"` or `"投機淨持倉"`.
