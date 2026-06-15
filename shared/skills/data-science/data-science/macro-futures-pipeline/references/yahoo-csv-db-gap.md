# Yahoo CSV → SQLite Import Gap

## Problem

`macro_pipeline.py` saves Yahoo data to CSV only. The daily report script (`scripts/daily_report.py`)
reads from SQLite. After collection, the database still has stale data — the CSV never gets imported.

**Symptoms:**
- Daily report shows prices from 3 days ago
- `yahoo_futures` table in `hermes.db` has old rows
- New CSV exists at `hermes-macro-data/csv/<today>/yahoo_futures.csv` but DB unchanged

## Solution: `scripts/daily_collect.py`

Created a dedicated collection script that does both:

1. Call `macro_pipeline.fetch_fred()` and `fetch_yahoo_futures()` for fresh CSV
2. Import the new CSV into SQLite `yahoo_futures` table

```python
# Key import logic:
import csv, sqlite3
from pathlib import Path
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")
csv_path = Path.home() / "hermes-macro-data" / "csv" / today / "yahoo_futures.csv"

if csv_path.exists():
    db = sqlite3.connect(str(Path.home() / "hermes-macro-data" / "hermes.db"))
    with open(str(csv_path), encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        db.execute("DELETE FROM yahoo_futures")
        for row in reader:
            vals = [row[k] for k in reader.fieldnames]
            q = ",".join(["?"] * len(vals))
            c = ",".join([f'"{k}"' for k in reader.fieldnames])
            db.execute(f"INSERT INTO yahoo_futures ({c}) VALUES ({q})", vals)
    db.commit()
    db.close()
```

## Cron Update

Old: `python3 -c "import macro_pipeline as m; m.fetch_fred(); m.fetch_yahoo_futures(); m.save_data()"`
New: `python3 scripts/daily_collect.py`

## Database Schema Reminders for daily_report.py

| Table | Column Name | Quirk |
|-------|------------|-------|
| fred_indicators | `系列ID` | NOT `系列` |
| yahoo_futures | `"日漲跌幅%"` | Contains `%` — needs quotes |
| cotdata | `"COT Index(26W)"` | Contains parentheses — needs quotes |
| cotdata | `品種` | Uses simplified Chinese (`黄金` not `黃金`) |
| yahoo_futures | `品種` | Uses traditional Chinese (`黃金` not `黄金`) |
| vix_data | `价格` | VIX lives in separate table, not yahoo_futures |
