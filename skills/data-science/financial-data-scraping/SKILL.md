---
name: financial-data-scraping
description: Scrape financial data from official sources — FRED API, CFTC COT reports, oddpool FedWatch, Yahoo Finance, TradingEconomics. Covers parsing fixed-width CFTC text, FRED series discovery, and fallback chains for market data.
triggers:
  - financial data scraping
  - FRED API
  - CFTC COT
  - FedWatch probabilities
  - treasury futures data
  - commodity COT data
  - market data pipeline
  - macro indicators
related_skills:
  - macro-report-pipeline
  - report-pipeline-auditing
---

# Financial Data Scraping

## Data Sources & Access Patterns

### FRED API (Federal Reserve Economic Data)
- Base URL: `https://api.stlouisfed.org/fred/series/observations`
- Auth: `FRED_API_KEY` env var (32-char key from https://fred.stlouisfed.org/docs/api/api_key.html)
- Common series: DGS1/DGS2/DGS5/DGS10/DGS30 (Treasury yields), TIPS (DFII10), CPI (CPIAUCSL), NAPM (ISM PMI), UNRATE, PAYEMS, FEDFUNDS, DTWEXBGS (USD index)
- **Pitfall**: `limit=30` fetches 30 observations; for monthly series (CPI), `all_obs[:13]` gives ~13 months. For YoY calculation, match by DATE not array index — use `dateutil.relativedelta` to find 12-months-ago entry.
- **Pitfall**: Some series (like DGS5) may return "." values filtered out. If a series seems missing, verify with direct API call before assuming it's not configured.
- Response: JSON with `observations[].date` and `observations[].value`

### CFTC COT Reports (Commitments of Traders)
- **Treasury futures**: `https://www.cftc.gov/dea/futures/financial_lf.htm`
- **Agricultural futures**: `https://www.cftc.gov/dea/futures/ag_lf.htm`
- **Format**: Fixed-width PLAIN TEXT, NOT HTML tables. BeautifulSoup won't work.
- Parsing pattern:
  ```python
  idx = text.find("UST 10Y NOTE")
  block = text[idx:idx+600]
  oi_m = re.search(r'Open Interest is ([\d,]+)', block)
  for line in block.split('\n'):
      nums = line.strip().split()
      if len(nums) >= 14:
          # nums[3]=AM Long, nums[4]=AM Short, nums[6]=Lev Long, nums[7]=Lev Short
          am_net = int(nums[3].replace(",","")) - int(nums[4].replace(",",""))
          break
  ```
- Cotton: `COTTON NO. 2` in ag_lf.htm, look for `All :` data line
- **Pitfall**: CFTC doesn't update on weekends. Report date is typically Tuesday.
- **Pitfall**: URL `deacotfo.htm` returns 404. Correct agricultural URL is `ag_lf.htm`.

### FedWatch via oddpool.com API
- **Do NOT scrape the HTML page** — it's a Next.js SPA, `requests.get()` returns empty shell.
- Use the JSON API endpoints:
  - `GET https://www.oddpool.com/api/events/history/no_change?event_id=fomc-2026-06-17&hours=1`
  - `GET https://www.oddpool.com/api/events/history/cut_25bps?event_id=fomc-YYYY-MM-DD&hours=1`
  - `GET https://www.oddpool.com/api/events/history/hike_25bps?event_id=fomc-YYYY-MM-DD&hours=1`
- Response: `{"kalshi": [{"timestamp": "...", "probabilities": {"no_change": 0.99}}], "polymarket": [...]}`
- Take last item's probabilities from either venue.
- **Event ID discovery**: Try dates around FOMC meetings (typically mid-month). Loop `day in [17,16,18,15,19,14,20]` for current and next month.
- **Validation**: Sum of hold+cut+hike should be ~100%. If >105%, data is corrupt — discard.

### Yahoo Finance API
- URL: `https://query1.finance.yahoo.com/v8/finance/chart/{symbol}`
- Params: `{"range": "5d", "interval": "1d"}`
- Parse: `data["chart"]["result"][0]["meta"]["regularMarketPrice"]`
- Symbols: EURUSD=X, USDJPY=X, CNH=X, ^VIX, GC=F (gold), CL=F (WTI)
- **Pitfall**: Rate-limited (429). Use exponential backoff with retries.

### TradingEconomics
- Often blocks requests (403). Prefer FRED API for same data when possible.
- For ISM PMI: Use FRED series `NAPM` instead.

### SAFE (国家外汇管理局) — Cross-border RMB Payments
- Data page: `https://www.safe.gov.cn/safe/2018/0419/8806.html`
- Excel files linked from page: `https://www.safe.gov.cn/safe/file/file/<date>/<hash>.xls`
- Sheet: "以人民币计值（月度）"
- Columns: 人民币收入, 人民币支出, 差额
- **Pitfall**: May need to try multiple Excel links on the page. First link is usually the time-series.

### ECB Statistical Data Warehouse — Eurozone M2
- Series: `BSI.M.U2.Y.V.M20.X.1.U2.2300.Z01.E`
- URL: `https://data.ecb.europa.eu/data-detail/<series_id>`
- Unit: EUR (millions), seasonally adjusted
- **Pitfall**: FRED series MYAGM2EZM196N is discontinued (data only to 2017). Use ECB directly.

### Bank of Japan — Japan M2
- BOJ Money Stock Statistics: `https://www.boj.or.jp/statistics/money/ms1702.htm`
- Also available via ECB RTD dataset: `RTD.M.JP.Y.M_M2.J`
- **Pitfall**: FRED series MYAGM2JPM189N is discontinued. Use BOJ or ECB directly.

### 99qh.com — Chinese Futures Warehouse Receipts
- URL: `https://www.99qh.com/daily/warehouse`
- Aggregates DCE + CZCE warehouse receipt data
- Products: 豆粕, 豆油, 玉米, 棕榈油, 白糖, 棉花, 菜籽油
- **Pitfall**: May use JavaScript rendering. If requests fails, fallback to known data.

## Anti-Bot Fallback Strategy

Many financial websites block `requests.get()` (CFTC, TradingEconomics, SAFE, 99qh.com). The scraper pattern should be:

```python
def fetch_something():
    """Try live fetch, fall back to verified static data."""
    try:
        r = requests.get(url, timeout=15, headers=UA)
        if r.status_code == 200:
            # parse and return
            ...
    except:
        pass
    # Fallback: verified data from official source (date-stamped)
    return {"source": "verified 2026-06-14", "value": 54.0, ...}
```

**Key rule**: Reports should NEVER show "—" for data that exists in the real world. If the scraper fails, return the last verified value with its date. The user can verify freshness from the date stamp.

**Verification workflow**: Use browser tool to visit official site, extract data visually, then hardcode as fallback in the scraper. Update fallback values during periodic report audits.

## Report Generation Patterns

### CSV Fallback Chain
When loading data for date `TODAY`:
```python
def load_csv(name):
    p = DATA_DIR / "csv" / TODAY / f"{name}.csv"
    if p.exists(): return pd.read_csv(p)
    # Fallback: scan recent dates
    for i in range(1, 8):
        d = (base - timedelta(days=i)).strftime("%Y-%m-%d")
        p2 = csv_root / d / f"{name}.csv"
        if p2.exists(): return pd.read_csv(p2)
    return pd.DataFrame()
```
**Pitfall**: Every script with `load()` needs this fallback. Without it, reports fail when TODAY's CSV is incomplete.

### CPI YoY from Index Values
FRED CPI series (CPIAUCSL) is an index, not percentage. Compute YoY:
```python
from dateutil.relativedelta import relativedelta
dt = datetime.strptime(str(latest_date), "%Y-%m-%d")
target = dt - relativedelta(months=12)
target_str = target.strftime("%Y-%m-01")
for v, d in cpi_vals:
    if str(d)[:7] == target_str[:7]:
        yoy_pct = (latest_val - v) / v * 100
```
**Pitfall**: Don't use array index `[11]` — data has gaps (missing months). Always match by date string.

### Weekly Change Calculation
For indicators with multiple daily observations (TIPS, DGS10, etc.):
- Take latest value and value from ~5 trading days ago (index [4])
- For rates (<20): show as `+0.05bp`
- For prices (>20): show as `-2.85%`
- Weekly average: mean of last 5 data points
