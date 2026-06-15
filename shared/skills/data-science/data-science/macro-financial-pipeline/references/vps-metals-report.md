# VPS Fixed Report Generator — Precious Metals

## Architecture

A pure-Python script on the VPS reads CSVs from the data collection pipeline and generates Markdown reports. No LLM involved — 100% data accuracy.

## Key Data-Sourcing Pattern

**Gold/silver spot prices** are fetched LIVE from Yahoo Finance API, NOT from the collected CSV files (which use Alpha Vantage with known latency):

```python
import requests
def fetch_live_prices():
    """Get latest COMEX futures from Yahoo as gold/silver proxy"""
    gold = None; silver = None
    try:
        r = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/GC=F",
            params={"range": "1d", "interval": "1d"},
            headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if r.status_code == 200:
            meta = r.json()["chart"]["result"][0]["meta"]
            gold = float(meta.get("regularMarketPrice", 0))
    except: pass
    try:
        r = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/SI=F",
            params={"range": "1d", "interval": "1d"},
            headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if r.status_code == 200:
            meta = r.json()["chart"]["result"][0]["meta"]
            silver = float(meta.get("regularMarketPrice", 0))
    except: pass
    return gold, silver
```

This works on a US VPS (direct connection) but NOT from mainland China (Yahoo is blocked).

## CSV Column Auto-Detection

The `get_val()` function handles Chinese/Traditional column names automatically:

```python
def get_val(df, col_like, kw):
    if df.empty: return None
    # Find name column
    name_col = df.columns[0]
    for c in df.columns:
        if "品" in c or "指" in c:
            name_col = c; break
    # Find value column
    val_col = None
    for c in df.columns:
        if col_like in c:
            val_col = c; break
    if val_col is None:
        for c in df.columns:
            if "價" in c or "值" in c:
                val_col = c; break
    if not val_col:
        val_col = df.columns[-1]
    sub = df[df[name_col].astype(str).str.contains(kw, na=False)]
    if sub.empty: return None
    return str(sub.iloc[0][val_col])
```

Usage: `get_val(fred_df, "數值", "TIPS")` finds the "數值" column in a FRED dataframe and returns the first row where the name column contains "TIPS".

## COT Data Parsing (COT Index + Z-Score)

```python
n_col = cot.columns[0]
for c in cot.columns:
    if "品" in c: n_col = c; break
net_col = cot.columns[-1]
for c in cot.columns:
    if "淨" in c: net_col = c; break

for _, r in cot.iterrows():
    n = str(r[n_col])
    if "黄金" in n:
        gold_cot = f"{int(r[net_col]):+,}" if pd.notna(r[net_col]) else "—"
        for c in cot.columns:
            if "Index" in c: gold_ci = f"{r[c]:.0f}"
            if "Score" in c: gold_z = f"{r[c]:+.2f}"
```

## Basis Calculation Edge Cases

```python
basis = ""
if gold_f and gold_s:
    try:
        gf = float(gold_f); gs = float(gold_s)
        basis = f"+${gf-gs:.2f}" if gf >= gs else f"-${gs-gf:.2f}"
    except: basis = "—"
```

Must handle both positive (期货溢价) and negative (期货贴水) basis with correct sign.

## File Output

```python
from pathlib import Path
DATA_DIR = Path("/root/hermes-macro-data")
TODAY = datetime.now().strftime("%Y-%m-%d")
out = DATA_DIR / "reports" / f"metals_weekly_{TODAY}.md"
with open(out, "w", encoding="utf-8") as f:
    f.write(report_text)
```
