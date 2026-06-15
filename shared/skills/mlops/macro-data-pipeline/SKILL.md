---
name: macro-data-pipeline
description: "Build and maintain automated financial macro data pipelines — API integrations, scheduled collection, CSV/JSON storage, VPS deployment."
version: 1.0.0
author: Hermes Agent
platforms: [linux, macos, windows]
---

# Macro Data Pipeline

Build automated data collection pipelines for financial macro data. Covers API integration, scheduled cron jobs, proxy handling, data storage, and VPS deployment.

## Workflow Principles

1. **Step by step** — present one data source at a time. Test it end-to-end before moving to the next. Do not batch-implement multiple sources in a single response.
2. **Check official docs first** — before guessing API endpoints, consult the provider's documentation. Guessed URLs waste time. If docs aren't available, test with a minimal probe before building the full integration.
3. **CSV/Excel is a valid data source** — not everything needs to be an API or a scraper. Government websites often provide CSV/Excel downloads that are more stable than any API. Treat file downloads as first-class data sources.
4. **Precise naming** — use instrument names as they appear in the official source (e.g. "COMEX" not just "futures", "WTI" not just "crude", "TFF" not just "financial COT"). Match the data provider's terminology.
5. **Verify before writing** — prove a single call works with curl or a minimal Python script before writing the permanent pipeline function.
6. **One source at a time** — do not attempt to integrate multiple data sources in a single turn. Complete and test one, then move to the next.

## Trigger Conditions

Use this skill when the user asks to:
- Set up automated financial/macro data collection
- Configure API keys for market data sources
- Build daily/weekly data pipelines
- Deploy data collection to a VPS
- Add new data sources to an existing pipeline

## Workflow

### 1. API Key Management

```python
from dotenv import load_dotenv
import os
from pathlib import Path

# ALWAYS use HERMES_HOME for .env location on Windows
ENV_PATH = Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))) / ".env"
load_dotenv(ENV_PATH)
```

**Pitfall**: On Windows with Hermes Desktop, `.env` is at `%HERMES_HOME%\.env` (typically `C:\Users\<user>\AppData\Local\hermes\.env`), NOT `~/.hermes/.env`. Always check `$HERMES_HOME` first.

**Pitfall**: When saving API keys to `.env` via Python heredocs, `*** ` (triple-asterisk-space) may be written as the literal value instead of the real key. Use Python dicts + f-strings like `f'{k}={v}\n'` or write to a `.py` file and execute it — never embed key values inside heredoc strings that contain `***`.

**Pitfall**: The `read_file` tool cannot read `.env` (Hermes redacts credential files). Use `terminal` with `python3 -c` for binary reads, or grep with raw byte output to verify keys.

### 2. Proxy Detection (China/GFW)

When running from mainland China or behind a VPN client, Python's `requests` library does NOT use Windows system proxy settings automatically.

```python
# Auto-detect common proxies
if not os.environ.get("HTTP_PROXY") and not os.environ.get("http_proxy"):
    import socket
    for host, port in [("127.0.0.1", 10808), ("127.0.0.1", 10809),
                       ("127.0.0.1", 7890), ("127.0.0.1", 7891)]:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.3)
        if sock.connect_ex((host, port)) == 0:
            os.environ["HTTP_PROXY"] = f"http://{host}:{port}"
            os.environ["HTTPS_PROXY"] = f"http://{host}:{port}"
            os.environ["http_proxy"] = f"http://{host}:{port}"
            os.environ["https_proxy"] = f"http://{host}:{port}"
            break
        sock.close()
```

Set BOTH uppercase and lowercase variants — `requests` prefers lowercase, but some libraries check uppercase.

**Known proxy ports**: v2rayN=10808, Clash=7890/7891

### 3. Data Source Integration

#### FRED (Federal Reserve)
```
Base: https://api.stlouisfed.org/fred/series/observations
Params: series_id=<ID>, api_key=<KEY>, file_type=json, sort_order=desc, limit=30
```

Key series: `FEDFUNDS`, `CPIAUCSL`, `PCEPILFE`(core PCE), `DFII10`(TIPS), `DGS1/2/10`(yields), `T5YIFR`(breakeven), `DTWEXBGS`(dollar), `PAYEMS`(nonfarm), `UNRATE`, `VIXCLS`

**Pitfall**: `TREAST` (1-Year Treasury) returns price-index values (millions), not yield percentages. Use `DGS1` for actual yield.

**Pitfall**: `T10YIFR` is not a valid FRED series ID. Use `T10YIE` for 10-year breakeven inflation rate.

#### Alpha Vantage (Commodities)
```
Base: https://www.alphavantage.co/query
Params: function=GLOBAL_QUOTE, symbol=<SYMBOL>, apikey=<KEY>
Rate limit: 5 calls/min (free tier) — add `time.sleep(12)` between calls
```

Symbol mapping:
- Gold: `XAUUSD`
- Silver: `XAGUSD`
- Crude Oil: `CL`
- GLD ETF: `GLD`
- SLV ETF: `SLV`
- S&P 500: `SPX`
- SLV ETF: `SLV`
- S&P 500: `SPX`

**Pitfall**: `GC=F` and similar Yahoo-style tickers do NOT work. Use forex-style symbols for metals.
**Pitfall**: `USDX` returns incorrect values (~25) — use FRED's `DTWEXBGS` for the dollar index instead.

#### Yahoo Finance (Futures & VIX)
```
Base: https://query1.finance.yahoo.com/v8/finance/chart/{symbol}
Params: range=5d&interval=1d
Headers: User-Agent: Mozilla/5.0
Rate limit: None documented, build exponential backoff for 429/403
Proxy: REQUIRED from mainland China (Yahoo blocks CN IPs)
```

Symbol mapping:
- Gold futures: `GC=F`
- Silver futures: `SI=F`
- WTI crude futures: `CL=F`
- VIX spot: `%5EVIX` (URL-encoded `^VIX`)

Exponential backoff pattern:
```python
def yahoo_quote(symbol, retries=3):
    import time, random
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    params = {"range": "5d", "interval": "1d"}
    for attempt in range(retries):
        r = requests.get(url, params=params, headers=headers, timeout=15)
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 429:
            time.sleep((2**attempt) + random.random()*2)
        elif r.status_code == 403:
            time.sleep(5)
        else:
            time.sleep(2**attempt)
    return None
```

#### CFTC COT (cotdata.net)
```
Base: https://cotdata.net/api/cot
Params: instrument=<CFTC_CODE>, table=legacy|tff|disaggregated
Rate: 10 req/min (free), no auth required
Free tier: latest week only (no from/to)
```

CFTC codes: Gold=`088691`, Silver=`084691`, Crude WTI=`067651`, DXY=`098662`

Response includes: `non_commercial` (legacy), `managed_money` (disaggregated), `cot_index_26w/52w`, `zscore_26w/52w`, `net_change`, `pct_long`

**Pitfall**: Old CFTC.gov CSV URLs (`/dea/futures/dea_futures.csv`) are 404. The legacy format endpoint at `/dea/newcot/deafut.txt` still works but has complex column positioning. Prefer `cotdata.net` API.

#### Tushare (China Futures + Social Financing)
```
Base: http://api.tushare.pro (POST)
Auth: token=<TUSHARE_TOKEN>
```

**China futures** (daily):
```python
pro = ts.pro_api(TOKEN)
df = pro.fut_daily(ts_code='AU2606.SHF', start_date='20260601', end_date='20260613')
```

**Social financing (sf_month)**:
```python
df = pro.sf_month(start_m='202501', end_m='202606')
# Returns: month, inc_month (月增量亿元), inc_cumval (累计亿元), stk_endval (存量万亿)
```

**Pitfall**: `sf_month` requires 2000 integration credits (not basic 120). The API name is `sf_month`, NOT `social_financing` or `shrzgm`. Always check official docs at `https://tushare.pro/document/2?doc_id=310` before guessing API names.

#### Finnhub (News + Market Data)
```
Base: https://finnhub.io/api/v1
Key: FINNHUB_API_KEY
News: /news?category=general — works from China without proxy
Calendar: /calendar/economic — requires premium tier (403 on free)
```

**Pitfall**: `NewsAPI` (newsapi.org) is blocked from mainland China. Use Finnhub news as replacement.
**Pitfall**: Yahoo Finance API is also blocked from China (returns Yahoo China shutdown page). Use Alpha Vantage or FMP through proxy instead.

#### CFTC TFF (Financial Futures — VIX via ZIP)

For financial futures (VIX, other index/rate products), use the TFF ZIP archive from CFTC:

```
URL: https://www.cftc.gov/files/dea/history/fut_fin_txt_2026.zip
File inside: FinFutYY.txt
Format: CSV with 87 columns, TFF (Traders in Financial Futures)
```

TFF column mapping (0-indexed):
```
[7]  = Open_Interest_All
[8]  = Dealer_Positions_Long_All
[9]  = Dealer_Positions_Short_All
[10] = Dealer_Positions_Spread_All
[11] = Asset_Mgr_Positions_Long_All
[12] = Asset_Mgr_Positions_Short_All
[13] = Asset_Mgr_Positions_Spread_All
[14] = Lev_Money_Positions_Long_All
[15] = Lev_Money_Positions_Short_All
[16] = Lev_Money_Positions_Spread_All
[17] = Other_Rept_Positions_Long_All
[18] = Other_Rept_Positions_Short_All
```

**Pitfall**: TFF format has DIFFERENT column layout from Legacy format. In Legacy, column 7 is NonComm Long. In TFF, column 7 is Open Interest and column 8 is Dealer Long. Do not mix them.

**Pitfall**: VIX CFTC code is `1170E1` — search for `VIX FUTURES` in the `Market_and_Exchange_Names` column (row[0]). The ZIP file spans one calendar year; update the year in the filename when crossing January.

Available annual ZIP files: `fut_fin_txt_2026.zip`, `fut_fin_txt_2025.zip`, etc. at the same base URL pattern.

#### VIX Data (Combined)
VIX has two components:
1. **Price**: Yahoo Finance `%5EVIX` (requires proxy from China)
2. **Positioning**: CFTC TFF ZIP → parse `VIX FUTURES - CBOE FUTURES EXCHANGE` row

#### EIA STEO (Solar & Industrial Energy)
```
Base: https://api.eia.gov/v2/steo/data/?api_key=<KEY>&length=N
```

Solar photovoltaic series (US only — EIA API does not provide international solar):
- `SODTC_US`: Total Small-Scale Solar PV Capacity
- `SODTP_US`: Total Generation from Small-Scale Solar PV
- `SPEPCGWX`: Electric Power Sector Solar PV Net Summer Capacity
- `SODCC_US`: Commercial Solar PV Capacity
- `SODIC_US`: Industrial Solar PV Capacity
- `SODRC_US`: Residential Solar PV Capacity
- `SODCP_US`: Commercial Solar PV Generation
- `SODIP_US`: Industrial Solar PV Generation

Industrial energy consumption:
- `ELICP_*`: Industrial Electricity Retail Sales (by region: ENC, ESC, MTN, PAC, etc.)
- Natural gas/petroleum industrial series are available under relevant STEO categories.

**Pitfall**: Solar data is US-only. International solar capacity/generation data requires IRENA or BloombergNEF (no free API).

#### Other Sources
- **AGSI+ European Gas**: `https://agsi.gie.eu/api` with `x-key` header. Country `EU` returns empty — use `DE` for Germany.
- **EIA Energy**: `https://api.eia.gov/v2/petroleum/crd/crpdn/data/` — frequency must be `monthly` or `annual`, not `weekly`.
- **FedWatch**: `https://www.oddpool.com/fed-market-watch` — scrape FOMC probability table. CME website blocks direct requests (403).
- **FMP** (Financial Modeling Prep): Free tier only supports basic stock quotes via `/stable/quote?symbol=X`. Futures/ETFs require premium (402).

#### Baker Hughes Rig Count (via AOGR)
```
URL: https://www.aogr.com/web-exclusives/us-rig-count/{year}
Method: requests + BeautifulSoup (no Cloudflare)
```

AOGR publishes weekly U.S. rig count data in clean HTML div-based tables (Tailwind CSS). Parse `rig_count_container` divs for: date, total rigs, oil rigs, gas rigs, misc rigs.

**Pitfall**: `rigcount.bakerhughes.com` has Cloudflare protection — curl from VPS gets blocked (HTTP 403 or TLS error 92). Use AOGR instead, which has the same Baker Hughes data in static HTML.

#### BDI Baltic Dry Index (via TradingEconomics)
```
URL: https://tradingeconomics.com/commodity/baltic
Method: requests + BeautifulSoup (no Cloudflare, no proxy needed)
```

TradingEconomics provides BDI data in clean HTML. Parse the price element and change percentage. Falls back to Investing.com if TradingEconomics fails.

**Pitfall**: `investing.com` has Cloudflare protection — returns 403 from VPS. Use TradingEconomics which works from both VPS and residential IPs without proxy.

### 4. Data Storage Structure

```
~/hermes-macro-data/
├── csv/YYYY-MM-DD/     ← Daily raw data (CSV)
├── reports/YYYY-MM-DD.md  ← Generated reports
├── logs/               ← Pipeline logs
└── meta/               ← Pipeline summary JSONs
```

### 5. Cron Scheduling

On Hermes Desktop (Windows): cron runs only when the app is open. Use `hermes cron create` + workdir path.

On VPS (Linux): use system cron:
```bash
crontab -e
# Add:
0 8 * * * cd ~/macro-pipeline && python3 macro_pipeline.py >> ~/hermes-macro-data/logs/cron.log 2>&1
0 9 * * * cd ~/macro-pipeline && python3 macro_pipeline.py --report >> ~/hermes-macro-data/logs/report.log 2>&1
```

**Pitfall**: Hermes Desktop's cron scheduler only fires when the gateway is running. For 24/7 operation, deploy to a VPS.

### 6. VPS Deployment & Security

Package as:
```
~/hermes-deploy/
├── pipeline/
│   ├── macro_pipeline.py
│   ├── generate_report.py
│   └── run_daily.sh
├── install_on_vps.sh
└── VPS_SECURITY_GUIDE.md
```

Security checklist for Vultr/Ubuntu:
1. Create non-root user
2. Disable root SSH login
3. SSH key authentication only (no passwords)
4. UFW firewall (only 22/tcp)
5. Install fail2ban

## References

See `references/data-sources.md` for a complete API endpoint reference table.

## Charts Formatting

When generating macro indicator charts, use independent Y-axis per indicator (not shared axes). This makes each indicator's trend clearer:

```python
# ❌ Bad: 5 indicators on one chart with shared Y-axis
fig, ax = plt.subplots(figsize=(12, 5.5))
for name, color in indicators:
    ax.plot(x, vals, label=name)  # All on same scale — hard to read

# ✅ Good: 4 independent charts, each with own Y-axis
fig, axes = plt.subplots(4, 1, figsize=(12, 4))
for ax, (name, color) in zip(axes, indicators):
    ax.plot(x, vals, color=color)
    ax.set_title(name)
```

Standard chart annotations: `tag_start()` (left-bottom) + `tag_end()` (right-bottom with white box).

## Pitfalls Summary

| Pitfall | Context |
|---------|---------|
| `.env` path differs on Windows Desktop vs Linux CLI | Always use `$HERMES_HOME` |
| `*** ` literal in heredoc key values | Use Python dict + f-string |
| Yahoo Finance blocked in China | Use Alpha Vantage or proxy |
| NewsAPI blocked in China | Use Finnhub news |
| FRED `TREAST` is not yield | Use `DGS1` |
| CME FedWatch blocks scrapers | Use oddpool.com |
| `T10YIFR` invalid FRED code | Use `T10YIE` |
| Alpha Vantage `USDX` wrong | Use FRED `DTWEXBGS` |
| EIA must use monthly/anual freq | Not weekly |
| AGSI+ `country=EU` returns empty | Use specific country code |
| Baker Hughes `rigcount.bakerhughes.com` Cloudflare blocked | Use AOGR static HTML |
| Investing.com `baltic-dry` Cloudflare blocked | Use TradingEconomics |
| Tushare API names are not obvious | Always check official docs before guessing |
| Hermes cron jobs for reports waste LLM tokens | Reports are Python-generated, no LLM needed — use VPS system cron |
| MiMo model change requires restart | `/reset` alone does not switch models mid-conversation — restart Hermes Desktop |
| VPS may be unreachable | Have local fallback for report generation; check VPS status before relying on it |

## Key Learnings (2026-06-13)

### MiMo Token Plan Configuration
MiMo 2.5 Pro via Token Plan is configured as a custom provider in Hermes:

```yaml
# config.yaml
model:
  default: xiaomi/mimo-v2.5-pro
  provider: xiaomi
  base_url: https://token-plan-cn.xiaomimimo.com/v1
```

```bash
# .env
XIAOMI_API_KEY=tp-xxxxx  # Token Plan key format
XIAOMI_BASE_URL=https://token-plan-cn.xiaomimimo.com/v1
```

After config change, **restart Hermes Desktop** — `/reset` does not switch models mid-conversation.

### CSV/Excel as Data Sources
Government and institutional websites often provide CSV/Excel downloads that are more stable than APIs:
- USDA AMS: XLSX export from MARS API
- Baltic Exchange: CSV from official site
- Baker Hughes: XLSX from rigcount.bakerhughes.com (static-files endpoint)
- CONAB (Brazil): CSV from official safras pages

Always check if a direct file download is available before building a scraper.

### Cron Job vs Python Script for Reports
When reports are generated by Python scripts (not LLM), Hermes cron jobs that use LLM to generate the same reports are redundant and waste tokens. Use VPS system cron to run Python scripts directly — zero LLM cost.
