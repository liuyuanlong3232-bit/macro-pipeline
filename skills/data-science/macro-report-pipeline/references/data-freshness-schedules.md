# Data Freshness & Official Update Schedules

Reference for auditing whether report data matches official publication timelines.
Use this when: reviewing generated reports, debugging stale data, or explaining "—" gaps to users.

## Daily Data (T+1 to T+3 expected delay)

| Series | FRED ID | Publishes | Typical Delay | Weekend Behavior |
|--------|---------|-----------|---------------|------------------|
| 1Y Treasury | DGS1 | Daily | T+1 | No data Sat/Sun; latest = Friday |
| 2Y Treasury | DGS2 | Daily | T+1 | Same |
| 5Y Treasury | DGS5 | Daily | T+1 | Same (⚠️ may be empty — verify series) |
| 10Y Treasury | DGS10 | Daily | T+1 | Same |
| 30Y Treasury | DGS30 | Daily | T+1 | Same |
| TIPS 10Y | DFII10 | Daily | T+1 | Same |
| 10Y-2Y Spread | T10Y2Y | Daily | T+1 | Same |
| Breakeven Inflation | T10YIE, T5YIFR | Daily | T+1 | Same |
| DXY (broad) | DTWEXBGS | Daily | **T+5 to T+7** | Same — but ~1 week lag! |
| VIX | Yahoo ^VIX | Real-time | 0 (market hours) | Last close on weekends |
| Commodity futures | Yahoo / CL=F etc | Real-time | 0 (market hours) | Last close on weekends |
| AGSI Gas Storage | AGSI API | Daily | T+1-2 | Same |

**Weekend rule**: On Saturday/Sunday, daily data from Friday (T-1) is the freshest possible.
A report generated Sunday showing Thursday data is normal for T+1 series.

## Weekly Data

| Series | Source | Release Day | Typical Lag |
|--------|--------|-------------|-------------|
| EIA Petroleum Status | EIA API | Wednesday | 0-1 days |
| EIA Natural Gas Storage | EIA API | Thursday | 0-1 days |
| CFTC COT (legacy) | cftc.gov financial_lf.htm | Friday | 5 days (report date is T-5) |
| CFTC COT (disaggregated) | cftc.gov ag_lf.htm | Friday | 5 days |
| CFTC TFF | cftc.gov financial_lf.htm | Friday | 5 days |
| Baker Hughes Rig Count | data_scrapers | Friday | 0-1 days |
| cotdata.net COT Index | cotdata.net | ~Saturday | ~5-6 days |

**CFTC staleness rule**: If today is Saturday and CFTC report date is >7 days ago, data is stale.
Expected: Friday's release covers positions from the prior Tuesday.
Example: Released Friday 6/13 → report date 6/10 (Tuesday).

## Monthly Data (US)

| Series | FRED ID | Release Schedule | Typical Lag |
|--------|---------|-----------------|-------------|
| CPI | CPIAUCSL | ~13th of month | 13 days after reference month |
| PPI | PPIACO | ~14th of month | ~2 weeks |
| PCE / Core PCE | PCEPILFE | ~last week of month | ~3 weeks |
| Unemployment | UNRATE | 1st Friday | ~5 days |
| Nonfarm Payrolls | PAYEMS | 1st Friday | ~5 days |
| JOLTS | JTSJOL | ~2nd Tuesday | ~6 weeks (e.g., May data released mid-July) |
| Industrial Production | INDPRO | ~mid-month | ~2 weeks |
| Housing Starts | HOUST | ~mid-month | ~2 weeks |
| Michigan Sentiment | UMCSENT | Prelim: mid-month, Final: last Friday | ~2-3 weeks |
| ISM PMI | NAPM | 1st business day | Same month |
| Average Hourly Earnings | AHETPI | 1st Friday (with jobs) | ~5 days |
| Fed Funds Rate | FEDFUNDS | Monthly (lagged) | ~45 days |
| GDP | GDP | Quarterly, 3 estimates | 1-3 months |

**FRED monthly staleness rule**: If current date is past the 20th and the latest data
is from 2 months ago (not 1), the series likely has a lag or the fetch missed data.

## Quarterly / Irregular Data

| Series | Source | Schedule | Lag |
|--------|--------|----------|-----|
| Eurozone GDP | FRED CLVMNACSCAB1GQEA19 | Quarterly | ~2 months |
| Eurozone Rate | FRED IRSTCI01EZM156N | Quarterly | ~1 month |
| Federal Fiscal Deficit | FRED FYFSD | Annually (Oct) | ~9 months |
| China Social Financing | Tushare sf_month | Monthly | ~15 days |
| Cross-border RMB | SAFE | Monthly | ~6 weeks |
| ECB M2 | ECB SDW | Monthly | ~2 months |
| BOJ M2 | BOJ Statistics | Monthly | ~6 weeks |
| EIA STEO | EIA API | Monthly | Same month |

## Audit Methodology

When reviewing a report, for EACH data point:
1. Note the report generation date (header)
2. Note the actual data date (from CSV or API)
3. Check against the table above
4. Flag if: actual_date + expected_lag + 3 days < generation_date
   (3-day grace for weekends/holidays)

### Quick commands for freshness check:
```bash
# FRED: latest date per indicator
awk -F',' 'NR>1{key=$2; if(!(key in max) || $1>max[key]) max[key]=$1} END{for(k in max) print max[k], k}' \
  ~/hermes-macro-data/csv/$(date +%Y-%m-%d)/fred_indicators.csv | sort -r

# Yahoo: latest date
head -3 ~/hermes-macro-data/csv/$(date +%Y-%m-%d)/yahoo_futures.csv

# CFTC: report date
head -3 ~/hermes-macro-data/csv/$(date +%Y-%m-%d)/cotdata.csv

# Pipeline log: check failures
cat ~/hermes-macro-data/logs/pipeline_$(date +%Y%m%d).log | grep -E 'ERROR|WARNING|失敗|失敗|401|403|404|502'
```

## Known Pipeline URL Issues (as of 2026-06-14)

| Source | Broken URL | Status | Fix |
|--------|-----------|--------|-----|
| CFTC (pipeline) | `cftc.gov/dea/futures/dea.txt` | 404 | Use `cftc.gov/dea/newcot/FinFutWk.txt` (fixed 2026-06-14) |
| CFTC (data_scrapers) | `cftc.gov/dea/futures/financial_lf.htm` | 200 | Working — used by `fetch_cftc_cot_treasury()` |
| USDA NASS | `quickstats.nass.usda.gov/api` | Timeout | **Cloud IP blocked** (not key issue) — works from residential IPs. See pitfalls #21 |
| Finnhub Calendar | `finnhub.io/api/v1/calendar/economic` | 403 | **Free tier exclusion** (not token expiry) — requires paid plan. News endpoint works fine. |
| Japan e-Stat | `api.e-stat.go.jp` | 502 | Server-side issue, retry later |
| FedWatch (pipeline) | `oddpool.com/fed-market-watch` | SPA | **FIXED 2026-06-14**: Pipeline now uses correct API `/api/events/history/` |
