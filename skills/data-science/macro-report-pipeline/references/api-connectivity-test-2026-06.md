# API Connectivity Test Results — 2026-06-14

Tested from cloud server (Linux 5.15.0-179-generic, V2Ray transparent proxy only, no HTTP/SOCKS outbound proxy).

## Summary

| API | Endpoint | HTTP Status | Latency | Notes |
|-----|----------|-------------|---------|-------|
| FRED | api.stlouisfed.org/fred/series/observations | 200 | 0.23s | Works with valid 32-char key |
| Yahoo Finance | query1.finance.yahoo.com/v8/finance/chart/ | 200 | ~1s | Futures, forex, VIX all work |
| oddpool.com | oddpool.com/api/events/history/ | 200 | ~1s | FedWatch FOMC probabilities |
| EIA v2 | api.eia.gov/v2/petroleum/ | 200 | ~2s | URL-encode `[]` as `%5B%5D` for curl |
| CFTC FinFutWk | cftc.gov/dea/newcot/FinFutWk.txt | 200 | ~2s | Plain text, weekly commitments |
| CFTC financial_lf | cftc.gov/dea/futures/financial_lf.htm | 200 | ~2s | HTML, treasury futures COT |
| CFTC ag_lf | cftc.gov/dea/futures/ag_lf.htm | 200 | ~2s | HTML, agricultural COT |
| Finnhub News | finnhub.io/api/v1/news | 200 | ~0.5s | Free tier OK |
| Finnhub Calendar | finnhub.io/api/v1/calendar/economic | **403** | 0.2s | Requires paid plan |
| USDA NASS | quickstats.nass.usda.gov/api/api_GET/ | **Timeout** | 60s+ | Blocks cloud/datacenter IPs |
| CFTC dea.txt | cftc.gov/dea/futures/dea.txt | **404** | — | URL decommissioned |
| Japan e-Stat | api.e-stat.go.jp/rest/3.0/ | **502** | ~3s | Server-side issue (intermittent) |

## Key Findings

1. **USDA NASS blocks cloud IPs**: DNS resolves (13.77.235.253) but TCP connection times out. This is IP reputation blocking, not a key issue. Workaround: fetch locally + upload CSV, or use residential proxy.

2. **Finnhub free tier limitations**: News endpoint works, economic calendar returns 403. Don't integrate Finnhub calendar without paid plan.

3. **CFTC URL migration**: `dea.txt` is dead (404). Use `FinFutWk.txt` for pipeline's plain-text parsing, or `financial_lf.htm`/`ag_lf.htm` for HTML parsing (used by `data_scrapers.py`).

4. **EIA API curl gotcha**: The `data[0]=value` parameter contains `[]` which curl interprets as a glob pattern. URL-encode as `data%5B0%5D=value` or use `--data-urlencode`.

5. **V2Ray on this server**: Runs as transparent proxy (dokodemo-door on 127.0.0.1:61240) for API gateway. No HTTP/SOCKS outbound proxy configured. All API calls go direct.

## API Key Status (as of 2026-06-14)

| Key | In ~/.hermes/.env | In shell env | Status |
|-----|-------------------|--------------|--------|
| FRED_API_KEY | ✅ (correct 32-char) | ❌ (wrong 33-char) | Shell env overrides .env — use `_load_env_key()` |
| EIA_API_KEY | ✅ | ✅ | Working |
| FINNHUB_API_KEY | ✅ | ✅ | News OK, calendar 403 (paid) |
| AGSI_API_KEY | ✅ | ✅ | Working |
| TUSHARE_TOKEN | ✅ | ✅ | Working |
| USDA_NASS_API_KEY | ✅ (added 2026-06-14) | ❌ (not set) | Key valid but server IP blocked |
| ALPHA_VANTAGE_API_KEY | ✅ (added 2026-06-14) | ❌ (not set) | Not tested |
| CFTC_COT_ID | ✅ (added 2026-06-14) | ❌ (not set) | Not tested |
