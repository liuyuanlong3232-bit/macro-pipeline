# API Endpoint Reference — Verified Working Configuration

All endpoints tested and confirmed working on 2026-06-12.

## FRED

```python
# ✅ DGS1 returns 3.9 (yield percentage)
# ❌ TREAST returns 4479919 (price index, NOT a yield)
# ✅ T10YIE works (NOT T10YIFR — that's invalid)
series = {
    "DGS1": "1-Year Treasury Yield",
    "DGS2": "2-Year Treasury Yield",
    "DGS10": "10-Year Treasury Yield",
    "FEDFUNDS": "Fed Funds Rate",
    "CPIAUCSL": "CPI",
    "PCEPILFE": "Core PCE (ex Food & Energy)",       # ✅ Added this session
    "PCE": "Personal Consumption Expenditures",       # ✅ Added this session
    "DFII10": "10-Year TIPS Yield (Real Rate)",       # ✅ Added this session
    "T5YIFR": "5-Year Breakeven Inflation",           # ✅ Added this session
    "T10YIE": "10-Year Breakeven Inflation",          # ✅ Added this session (NOT T10YIFR)
    "UNRATE": "Unemployment Rate",
    "PAYEMS": "Non-Farm Payrolls",
    "GDP": "GDP",
    "T10Y2Y": "10-2 Year Spread",
    "M2SL": "M2 Money Supply",
    "DTWEXBGS": "Trade-Weighted USD",
    "PPIACO": "PPI",
    "INDPRO": "Industrial Production",
    "HOUST": "Housing Starts",
    "UMCSENT": "Consumer Sentiment",
}
```

Sample response (DFII10, 2026-06-10):
```
{"observations": [{"date": "2026-06-10", "value": "2.21"}]}
```

## Alpha Vantage

```python
# Rate limit: 5 calls/minute, sleep 12s between calls
symbols = {
    "XAUUSD": "Gold Spot",           # ✅ $4194.96
    "XAGUSD": "Silver Spot",         # ✅ $67.08
    "CL": "WTI Crude Oil Futures",   # ✅ $89.39
}

# Sample response for XAUUSD (2026-06-12):
# {"Global Quote": {"05. price": "4194.9600", "10. change percent": "-0.5917%"}}
```

NOT working: `USOIL`, `BZ=F`, `GC=F` (Yahoo format doesn't work here).

## EIA

```python
# Monthly crude production - works
url = "https://api.eia.gov/v2/petroleum/crd/crpdn/data/"
params = {
    "frequency": "monthly",                    # NOT "weekly"
    "facets[duoarea][]": "NUS",
    "sort[0][column]": "period",
    "sort[0][direction]": "desc",
    "length": 6,
}

# Natural gas - 500 error on /natural-gas/cons/sum/data/
# May need different facet paths - investigate further
```

## AGSI+ (European Gas Storage)

```python
url = "https://agsi.gie.eu/api"
params = {"country": "DE", "size": 7}          # NOT "EU"
headers = {"x-key": AGSI_API_KEY}

# Sample response:
# {"data": [{"name": "Germany", "gasInStorage": "87.9032",
#            "workingGasVolume": "247.7476", "injection": "499.53"}]}

# Calculate fill rate: 87.9032 / 247.7476 * 100 = 35.5%
```

## Finnhub

```python
# ✅ News (100 results per call, works on free tier)
url = "https://finnhub.io/api/v1/news"
params = {"token": FINNHUB_KEY, "category": "general"}

# ❌ Economic calendar (403 Forbidden on free tier)
url = "https://finnhub.io/api/v1/calendar/economic"  # 403

# ✅ Earnings calendar (works, may return 0)
url = "https://finnhub.io/api/v1/calendar/earnings"

## FedWatch (via Oddpool Aggregation)

```python
# ✅ Works — no API key required (web scrape)
url = "https://www.oddpool.com/fed-market-watch"
# Extract via regex from page text:
# "Fed maintains rate.*?(\d+\.?\d*)%" — Hold probability
# "Hike 25bps.*?(\d+\.?\d*)%"        — Hike probability
# "Cut 25bps.*?(\d+\.?\d*)%"         — Cut probability

# Sample (2026-06-12):
#   Fed maintains rate: 99.2%
#   Hike 25bps: 0.8%
#   Cut 25bps: 0.7%
#   Effective Fed Funds Rate: 3.63%
#   Taylor Rule implied: 4.75% (policy is accommodative)
```

⚠️ CME FedWatch website returns 403 — don't try to scrape cmegroup.com directly.
```