---
name: macro-report-pipeline
description: Build and maintain multi-source financial macro data report generators (FRED, Yahoo Finance, CFTC, EIA, FedWatch, AKShare, Tushare). Covers architecture, data validation, common pitfalls, and report quality auditing.
tags: [finance, macro, reports, data-pipeline, python, fred, commodities]
related_skills:
  - financial-data-scraping
  - report-pipeline-auditing
triggers:
  - weekly/monthly financial report generation
  - macro data pipeline maintenance
  - auditing financial report output for errors
  - adding new data sources to existing report scripts
  - any task involving FRED, CFTC COT, EIA, FedWatch, AGSI data
  - data freshness audit / staleness check / update schedule verification
---

# Macro Report Pipeline

Build and maintain Python scripts that pull from multiple financial data APIs/CSVs and generate structured markdown reports (weekly/monthly). Typical outputs: macro overview, energy, precious metals, agricultural commodity reports.

## Architecture

Each report is a standalone Python script that:
1. Loads CSV data from `~/hermes-macro-data/csv/<date>/` (with date fallback)
2. Fetches live data from APIs (FRED, AKShare, Tushare, Yahoo Finance, EIA, oddpool.com)
3. Computes derived metrics (weekly change, YoY, scores, ratios)
4. Renders a structured markdown report to `~/hermes-macro-data/reports/`

Key scripts in `~/hermes-pipeline/`:
- `macro_weekly.py` — global macro (treasuries, DXY, VIX, FedWatch, China macro)
- `energy_weekly.py` — crude oil, natural gas, EIA inventory, OPEC, CFTC
- `metals_weekly.py` — gold, silver, COMEX futures, COT positioning
- `agri_weekly.py` — agricultural commodities
- `run_report.py` — single report entry point (generate + email)
- `run_all_reports.py` — batch generate all 5 reports + email
- `send_email.py` — email delivery (QQ SMTP with HTML + embedded charts)
- `macro_pipeline.py` — data collection pipeline (CSV generation)
- `data_scrapers.py` — individual data fetchers (CFTC, ISM PMI, SAFE, etc.)
- `charts.py` — chart generation for email embedding

## Data Source Reference

| Source | Data | CSV File | API |
|--------|------|----------|-----|
| FRED | Treasuries, CPI, PCE, unemployment, DXY | `fred_indicators.csv` | FRED API (繁体中文列名!) |
| Yahoo Finance | Futures prices, FX rates, VIX | `yahoo_futures.csv` | yfinance / Yahoo chart API |
| CFTC/COT | Speculative positioning, COT Index | `cotdata.csv` | cotdata.net |
| CFTC TFF | Treasury futures COT (2Y/5Y/10Y/30Y) | N/A (live only) | `data_scrapers.fetch_cftc_cot_treasury()` — cftc.gov plain text |
| CFTC Ag | Cotton COT | N/A (live only) | `data_scrapers.fetch_cftc_cot_cotton()` — cftc.gov plain text |
| ISM PMI | US Manufacturing PMI | N/A (live only) | FRED series `NAPM` via `data_scrapers.fetch_ism_pmi()` |
| Alpha Vantage | Spot gold/silver, GLD/SLV ETF | `commodity_prices.csv` | Alpha Vantage API |
| EIA | Crude/gas inventory, production, refinery | `eia_energy.csv` | EIA v2 API |
| EIA STEO | OPEC supply forecasts | `eia_steo.csv` | EIA STEO API |
| AGSI+ | European gas storage (Germany) | `agsi_eu_gas.csv` | AGSI+ API |
| FedWatch | FOMC rate probabilities | N/A (live only) | oddpool.com REST API (NOT page scraping — SPA!) |
| AKShare | DR007, LPR, SHIBOR, reserve ratio, China CPI | N/A (live only) | akshare library |
| Tushare | Social financing (sf_month) | N/A (live only) | tushare library |
| SAFE | Cross-border RMB payments | N/A (live only) | `data_scrapers.fetch_safe_cross_border()` — Excel download |
| ECB | Eurozone M2 | N/A (live only) | `data_scrapers.fetch_global_m2()` — ECB SDW |
| BOJ | Japan M2 | N/A (live only) | `data_scrapers.fetch_global_m2()` — BOJ statistics |
| 99qh.com | Chinese futures warehouse receipts | N/A (live only) | `data_scrapers.fetch_cn_warehouse_receipts()` |

## Critical Pitfalls

See `references/pitfalls.md` for the full catalog with code examples and detection commands.
See `references/oddpool-api.md` for FedWatch API endpoint details.
See `references/new-data-sources-2026-06.md` for recently added sources (SAFE, ECB, BOJ, CFTC Treasury, warehouse receipts).

Top issues:

1. **Hardcoded values** — dates, prices, probabilities that should be dynamic. Always check for string literals that look like data.
2. **繁简混用** — FRED CSVs use 繁体中文 column names (聯邦基金利率, 美元指數). Report text must be 简体. Keep gv() lookups in 繁体, display strings in 简体.
3. **Index vs rate** — CPI/PPI from FRED are index levels, not YoY %. Must compute YoY manually.
4. **Price vs change %** — Yahoo CSV has both `最新價` and `日漲跌幅%`. Don't conflate them.
5. **Probability validation** — FedWatch probabilities must sum ≤ 100%. Add sanity checks.
6. **Score-text alignment** — When a score is negative (bearish), the explanation text must lead with bearish factors, not bullish ones.
7. **Date fallback** — Scripts use `load_csv()` with date fallback. Report header says TODAY but data may be from YESTERDAY.
8. **Empty DataFrame guards** — `df["column"]` on empty DataFrame raises KeyError. Always check `not df.empty and "column" in df.columns`.
9. **Patch reliability** — Multiple patch calls on same file can silently conflict. Prefer `write_file` for bulk changes.
10. **Markdown table pipes** — Conditional f-strings must include trailing ` | ` in BOTH branches.
11. **CFTC is plain text, not HTML** — CFTC COT reports (financial_lf.htm, ag_lf.htm) are fixed-width text. BeautifulSoup won't find tables. Parse with `text.find()` + `line.strip().split()`.
12. **CPI YoY date matching** — Don't use array index `[11]` for 12-months-ago CPI. Data has gaps (missing months). Use `dateutil.relativedelta` to find the exact date match.
13. **oddpool API, not page** — oddpool.com is a Next.js SPA. `requests.get()` returns empty shell. Use `/api/events/history/{event_type}?event_id=fomc-YYYY-MM-DD` endpoints.
14. **DTWEXBGS ≠ DXY** — FRED series `DTWEXBGS` is the Fed's "broad trade-weighted dollar index" (~120). The market DXY (ICE US Dollar Index) is a completely different index (~105-106). Reports showing "美元指数 120.08" from DTWEXBGS mislead readers who expect DXY. Either use DXY from Yahoo (`DX-Y.NYB`) or clearly label the index type. DTWEXBGS also has ~1 week publication delay.
15. **Yahoo futures CSV date lag** — `yahoo_futures.csv` may lag behind `commodity_prices.csv` by 1+ days. When the energy report shows WTI at $85.36 (Wednesday) but commodity_prices.csv has $89.45 (Friday), the report is reading the stale Yahoo CSV. Always cross-check both CSVs for the freshest price.
16. **Pipeline ALL_SOURCES gap** — Functions like `fetch_yahoo_futures()` and `fetch_cot()` exist but aren't registered in the `ALL_SOURCES` dict, so `run_all()` never calls them. Always verify every `def fetch_*` has a corresponding entry in ALL_SOURCES. See `references/pitfalls.md` #13.
17. **CFTC URL dead** — Pipeline's `dea.txt` URL returns 404. Fixed to `FinFutWk.txt`. See `references/pitfalls.md` #14.
18. **Yahoo staleness threshold** — Use `>= 2` not `> 2` for weekend coverage. See `references/pitfalls.md` #15.
19. **.env key gaps** — `write_keys.py` was for Windows; keys never written to server `.env`. See `references/pitfalls.md` #16.
20. **FRED DGS5 series may not return data** — DGS5 (5Y Treasury yield) is in FRED_SERIES dict but produces 0 rows in CSV. Often caused by FRED rate limiting (29 rapid requests). Add `time.sleep(0.3)` between calls. See `references/pitfalls.md` #20.
21. **Data freshness ≠ report date** — Report header says generation date but actual data dates vary widely (treasury 6/11, CFTC 6/2, JOLTS 4/1). Annotate each indicator with actual data date. See `references/data-freshness-schedules.md`.
22. **ALL_SOURCES must be AFTER all fetch_* functions** — If ALL_SOURCES dict is defined before fetch_vix/fetch_eia_steo, Python raises NameError. Move ALL_SOURCES + run_all + main to end of file. See `references/pitfalls.md` #18.
23. **Shell env var overrides .env** — `load_dotenv()` doesn't override existing env vars. If `FRED_API_KEY` is set in shell with wrong value, .env's correct key is ignored. Check `echo "$VAR"` vs `.env`. See `references/pitfalls.md` #19.
24. **Cloud server API blocking** — USDA NASS blocks cloud IPs (TCP timeout). Finnhub economic calendar requires paid plan (403). Test API connectivity from server before integrating. See `references/pitfalls.md` #21.
25. **Python .pyc cache** — Code changes don't take effect if `__pycache__/*.cpython-310.pyc` is stale. Always `rm __pycache__/*.pyc` after major edits, or use `python3 -B`. See `references/pitfalls.md` #22.
26. **Multiple script copies** — `find / -name "macro_pipeline.py"` may reveal 4+ copies in different dirs. Verify with `realpath` before editing. See `references/pitfalls.md` #23.
27. **Direct .env file reading** — When `load_dotenv(override=True)` fails to override shell env vars, read .env directly with a `_load_env_key()` function and set `os.environ[]` explicitly. See `references/pitfalls.md` #24.
28. **Partial report delivery** — Running `run_report.py macro` only sends the macro report. Other reports stay at previous date. Use `run_all_reports.py` to batch-generate all 5. Check completeness with: `ls ~/hermes-macro-data/reports/*$(date +%Y-%m-%d)*.md | wc -l` (should be 5).
29. **QQ邮箱授权码 ≠ QQ密码** — The SMTP password is NOT your QQ account password. It's a special authorization code generated in QQ邮箱设置→账户→POP3/IMAP/SMTP. Using the wrong password causes `smtplib.SMTPAuthenticationError`.
30. **Crontab syntax kills all tasks** — One malformed line in `/etc/cron.d/hermes-reports` causes cron to silently ignore the ENTIRE file. A `0 30 8 * * *` (6 fields) instead of `30 8 * * *` (5 fields) disabled ALL scheduled reports. Check `journalctl -u cron` for syntax errors. See `references/pitfalls.md` #27.

## Report Quality Audit Checklist

When reviewing generated reports, check:
- [ ] No hardcoded dates, prices, or percentages that should be dynamic
- [ ] No 繁体中文 in display text (OK in gv() lookup keys)
- [ ] CPI/PPI shown as YoY %, not index level
- [ ] Weekly change columns populated (not all "—")
- [ ] Probability sums ≤ 100%
- [ ] Score explanations match score direction
- [ ] No dev notes/debug text in output (e.g., "复刻XX话术")
- [ ] Data source dates are dynamic, not hardcoded
- [ ] Cross-report consistency (same indicator = same value across reports)
- [ ] **Data freshness**: Each indicator's actual data date annotated, not just report generation date
- [ ] **DTWEXBGS vs DXY**: If showing "美元指数" with value > 110, it's DTWEXBGS (broad), not DXY — label correctly
- [ ] **Yahoo price cross-check**: Compare yahoo_futures.csv vs commodity_prices.csv — use the fresher one
- [ ] **CFTC report date**: Should be within 7 days of generation date (weekly Friday releases)
- [ ] **FRED monthly lag**: JOLTS, INDPRO, HOUST, UMCSENT should be within 1-2 months, not 3+
- [ ] **Pipeline log check**: Review `pipeline_YYYYMMDD.log` for ERROR/WARNING before generating reports

See `references/data-freshness-schedules.md` for official update frequencies and audit methodology.
See `references/api-connectivity-test-2026-06.md` for server-side API reachability test results.

## Yahoo Finance Direct API (Fallback for Stale CSV Data)

When `yahoo_futures.csv` is stale or missing symbols, fall back to Yahoo's chart API.

### Staleness detection (add to each report's `report()` function):

```python
yahoo = load("yahoo_futures")
yahoo_stale = True
if yahoo is not None and not yahoo.empty and "日期" in yahoo.columns:
    try:
        latest_date = yahoo["日期"].max()
        from datetime import datetime as dt
        days_diff = (dt.strptime(TODAY, "%Y-%m-%d") - dt.strptime(str(latest_date), "%Y-%m-%d")).days
        yahoo_stale = days_diff >= 2  # >= 2, NOT > 2 (weekends!)
    except Exception:
        yahoo_stale = True
```

**Critical**: Use `>= 2`, not `> 2`. On Sunday, Friday data is exactly 2 days old — `> 2` misses it.

### Live fetch function:

```python
def yahoo_quote_direct(symbol, retries=3):
    """Direct Yahoo Finance API — use when CSV is stale."""
    import time, random
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    params = {"range": "5d", "interval": "1d"}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=15)
            if r.status_code == 200:
                data = r.json()
                result = data["chart"]["result"][0]
                meta = result.get("meta", {})
                price = meta.get("regularMarketPrice")
                return price, TODAY
            elif r.status_code == 429:
                time.sleep((2 ** attempt) + random.random() * 2)
        except Exception:
            time.sleep(2 ** attempt)
    return None, None
```

### Fallback pattern (append live data to DataFrame):

```python
if yahoo_stale:
    for sym, name, keyword in [("CL=F", "WTI原油期貨", "WTI"), ("BZ=F", "Brent原油期貨", "Brent")]:
        price, date = yahoo_quote_direct(sym)
        if price is not None:
            new_row = pd.DataFrame([{
                "來源": "Yahoo Finance (直连)", "品種": name,
                "代碼": sym, "日期": date, "最新價": price, "抓取日": TODAY
            }])
            yahoo = pd.concat([yahoo, new_row], ignore_index=True)
```

Applied to: `energy_weekly.py` (WTI/Brent/NG), `metals_weekly.py` (gold/silver futures), `agri_weekly.py` (7 agri futures).

## Report Delivery (Email)

Reports are sent via QQ邮箱 SMTP using `send_email.py`.

### Configuration (.env)
```
EMAIL_USER=your@qq.com
EMAIL_PASS=<QQ邮箱授权码>    # NOT your QQ password — get from QQ邮箱设置→账户→POP3
EMAIL_TO=recipient@qq.com
EMAIL_HOST=smtp.qq.com
EMAIL_PORT=465
```

### Entry Points
- `run_report.py <macro|energy|metals|agri|agri_cn|allocation>` — generate ONE report + send email
- `run_all_reports.py` — generate ALL 5 reports + send all emails (batch mode)
- `send_email.py <report_path> [chart_type]` — send a single report file

### Chart Types
The `chart_type` parameter controls which charts are embedded in the HTML email:
- `macro` — FRED trends chart
- `metals` — gold, silver, gold/silver ratio, COT charts (6 images)
- `energy` — COT net + COT index charts
- `""` (empty) — no charts (agri reports)

### Pitfall: Partial Report Generation
Running `run_report.py macro` only generates and sends the macro report. The other 4 reports (energy, metals, agri_global, agri_china) remain at their previous date. Always use `run_all_reports.py` for complete delivery.

### Pitfall: Report Date vs Delivery Date
Report filenames use generation date (e.g., `macro_weekly_2026-06-15.md`), but the email subject includes the send date. If a report is generated on Saturday but sent on Monday, the dates will differ.

## Adding a New Data Source

1. Create/update the CSV scraper to save to `~/hermes-macro-data/csv/<date>/<name>.csv`
2. In the report script, add `load("<name>")` and a `gv()` lookup
3. Add a row to the appropriate report table
4. If the source requires API keys, document in `.env` and the script's header
5. Add fallback handling (return "—" if data unavailable)
