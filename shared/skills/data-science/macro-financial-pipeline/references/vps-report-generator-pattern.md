# VPS Fixed Report Generator Pattern

## Architecture

Fixed-template reports (no LLM) run directly on VPS via Python crontab. They read CSVs from `/root/hermes-macro-data/csv/{date}/` and output Markdown to `/root/hermes-macro-data/reports/`.

## Core Pattern

```python
import pandas as pd

DATA_DIR = Path("/root/hermes-macro-data")
TODAY = datetime.now().strftime("%Y-%m-%d")

def load(name):
    p = DATA_DIR / "csv" / TODAY / f"{name}.csv"
    if p.exists(): return pd.read_csv(p)
    # Fallback to yesterday
    y = (datetime.now()-timedelta(1)).strftime("%Y-%m-%d")
    p = DATA_DIR / "csv" / y / f"{name}.csv"
    if p.exists(): return pd.read_csv(p)
    return None

def yahoo_price(symbol):
    """Live price from Yahoo (no API key, no delay)"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        r = requests.get(url, params={"range":"1d","interval":"1d"},
                        headers={"User-Agent":"Mozilla/5.0"}, timeout=10)
        if r.status_code == 200:
            return r.json()["chart"]["result"][0]["meta"]["regularMarketPrice"]
    except: return None

def safe_price(val, name, min_v, max_v):
    try:
        v = float(val)
        if v < min_v or v > max_v:
            print(f"⚠️ {name} 价格异常: {v}")
            return None
        return v
    except: return None

def get_val(df, kw):
    """Auto-detect column names and extract value by keyword"""
    if df is None: return None
    nc = [c for c in df.columns if "品" in c or "指" in c]
    vc = [c for c in df.columns if "價" in c or "值" in c]
    if not nc or not vc: return None
    sub = df[df[nc[0]].astype(str).str.contains(kw, na=False, regex=False)]
    if sub.empty: return None
    return str(sub.iloc[0][vc[0]])
```

## Data Source Precedence

1. **Gold/Silver spot price** → `yahoo_price("GC=F")` / `yahoo_price("SI=F")` (live, best quality)
2. **DXY** → `yahoo_price("DX-Y.NYB")` (ICE US Dollar Index, NOT FRED DTWEXBGS)
3. **Other futures** → `yahoo_price(symbol)` with fallback to `get_val(yahoo_csv, kw)`
4. **FRED macro** → `get_val(fred_csv, kw)` (FRED data is official, no Yahoo alternative)
5. **COT** → `get_val(cot_csv, kw)` (cotdata.net, updates weekly Saturday 03:30 Beijing)

## Email Delivery Chain

Each VPS cron chains email sending in the same line:

```bash
0 9 * * 6 root cd /root/hermes-pipeline && python3 metals.py && python3 -c "from send_email import send_report; import glob; r=sorted(glob.glob('/root/hermes-macro-data/reports/metals_weekly_*.md')); send_report(r[-1])"
```

## VPS Crontab (Full Schedule)

```bash
# Daily data collection
0 8 * * * cd /root/hermes-pipeline && python3 -c "from dotenv import load_dotenv; load_dotenv(); from macro_pipeline import main; main()" >> /var/log/hermes.log 2>&1

# Macro - Mon 9:00
0 9 * * 1 root cd /root/hermes-pipeline && python3 macro.py && [email]
# Energy - Thu 9:00
0 9 * * 4 root cd /root/hermes-pipeline && python3 energy.py && [email]
# Intl Agri - Fri 9:00
0 9 * * 5 root cd /root/hermes-pipeline && python3 agri_intl.py && [email]
# China Agri - Fri 20:00
0 20 * * 5 root cd /root/hermes-pipeline && python3 agri_cn.py && [email]
# Metals - Sat 9:00
0 9 * * 6 root cd /root/hermes-pipeline && python3 metals.py && [email]
# Allocation - Sun 10:00
0 10 * * 0 root cd /root/hermes-pipeline && python3 allocation.py && [email]
```
