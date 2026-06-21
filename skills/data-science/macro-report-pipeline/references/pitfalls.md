# Macro Report Pipeline — Pitfalls Catalog

Discovered during 2026-06-14 audit and iterative fixes of macro_weekly.py, energy_weekly.py, metals_weekly.py.

## 1. Hardcoded Values

**Symptom**: Report shows static data that never updates between runs.
**Examples found**:
- `energy_weekly.py` CFTC section: `"报告日期: 2026-06-02"` hardcoded
- `metals_weekly.py` FedWatch: `"维持99.2%"` hardcoded
- `metals_weekly.py` 10Y yield: `tnx_disp = f"4.55%"` hardcoded
- `energy_weekly.py` scoring text: static bullish/bearish explanations

**Fix pattern**: Replace string literals with variables from CSV/API. For dates, read from the CSV's date column. For probabilities, use the same fetch function as other reports.

**Detection**: Search for quoted numbers that look like financial data: `grep -n '"[0-9]\+\.[0-9]\+%"' *.py`

## 2. 繁简体混用

**Symptom**: Report body has 繁体中文 mixed with 简体.
**Root cause**: FRED CSV column names are 繁体 (聯邦基金利率, 美元指數, 失業率, 10 年期國債). The `gv()` function uses these as lookup keys, but the display strings should be 简体.

**Fix**: Keep `gv(fred, "聯邦基金利率")` as-is (matching CSV), but all `us_reasons.append()`, `lines.append()`, and display strings must use 简体.

**Key mappings**:
| 繁体 (lookup) | 简体 (display) |
|---------------|----------------|
| 聯邦基金利率 | 联邦基金利率 |
| 美元指數 | 美元指数 |
| 失業率 | 失业率 |
| 實際利率 | 实际利率 |
| 強勢 | 强势 |
| 曲線 | 曲线 |
| 倒掛 | 倒挂 |
| 歷史 | 历史 |
| 壓制 | 压制 |
| 新興 | 新兴 |
| 適中 | 适中 |

## 3. CPI/PPI Index vs YoY %

**Symptom**: Report shows CPI = 333.979 instead of ~2.26%.
**Root cause**: FRED CPIAUCSL series is the index level (1982-84=100), not YoY change. Script just displays `fmt_val(cpi)` without computing YoY.

**Fix**: Compute YoY using dateutil.relativedelta for exact month matching:
```python
from dateutil.relativedelta import relativedelta

cpi_all = gv_all(fred, "CPI")
cpi_vals = [(float(v), d) for v, d in cpi_all if v is not None]
latest_val = cpi_vals[0][0]
latest_date = cpi_vals[0][1]
dt = datetime.strptime(str(latest_date), "%Y-%m-%d")
target = dt - relativedelta(months=12)
target_str = target.strftime("%Y-%m-01")

# Find exact month match
yoy_val = None
for v, d in cpi_vals:
    if str(d)[:7] == target_str[:7]:
        yoy_val = v
        break

# Fallback: extrapolate from oldest available data point
if yoy_val is None:
    oldest_val = cpi_vals[-1][0]
    oldest_date = cpi_vals[-1][1]
    dt_old = datetime.strptime(str(oldest_date), "%Y-%m-%d")
    months = (dt.year - dt_old.year) * 12 + (dt.month - dt_old.month)
    yoy_pct = (latest_val - oldest_val) / oldest_val * 100 * (12 / months)

yoy_pct = (latest_val - yoy_val) / yoy_val * 100
```

**Pitfall**: Array index `[11]` does NOT guarantee 12 months ago if there are gaps in the data (e.g., missing months). Always match by date string, not array position.

**Also applies to**: PPI (PPIACO), PCE price index (PCEPILFE)

## 4. Price vs Change Percentage

**Symptom**: "周涨跌幅" column shows 85.36% instead of -6.51%.
**Root cause**: `gv(yahoo, "WTI")` returns `最新價` (85.36), and the code appends "%" to it. The actual change is in `日漲跌幅%` column.

**Fix**: Create a separate function that returns both price and change:
```python
def gv_chg(df, kw):
    """返回(价格, 日涨跌幅%)"""
    for c in df.columns:
        if "指標" in c or "品種" in c:
            vc = [x for x in df.columns if "數值" in x or "最新" in x or "價" in x][0]
            chg_cols = [x for x in df.columns if "漲跌幅" in x or "涨跌幅" in x]
            chg_col = chg_cols[0] if chg_cols else None
            sub = df[df[c].str.contains(kw, na=False, regex=False)]
            if not sub.empty:
                price = str(sub.iloc[0][vc])
                chg_val = sub.iloc[0][chg_col] if chg_col else None
                chg = f"{chg_val}%" if chg_val is not None else "—"
                return price, chg
    return None, None
```

## 5. FedWatch: oddpool.com is a JS SPA — Use API, Not Scraping

**Symptom**: `requests.get("https://www.oddpool.com/fed-market-watch")` returns HTML with length ~26 bytes. All regex patterns fail. Probability sum shows 297% because regex matches unrelated page content.

**Root cause**: oddpool.com is a Next.js SPA. The page content is rendered client-side via JavaScript. `requests.get()` only gets the shell HTML, not the data.

**Solution**: Use oddpool.com's REST API endpoints directly:

```python
def fetch_fedwatch_oddpool():
    base = "https://www.oddpool.com/api/events/history"
    headers = {"User-Agent": "Mozilla/5.0 ..."}
    # Dynamic event_id: fomc-YYYY-MM-DD (try dates around mid-month)
    event_id = "fomc-2026-06-17"
    
    # Get "maintains rate" probability
    r = requests.get(f"{base}/no_change", params={"event_id": event_id, "hours": 1}, headers=headers)
    data = r.json()  # {"kalshi": [...], "polymarket": [...]}
    hold = data["kalshi"][-1]["probabilities"]["no_change"] * 100  # 99.0
    
    # Get "cut 25bps" probability
    r2 = requests.get(f"{base}/cut_25bps", params={"event_id": event_id, "hours": 1}, headers=headers)
    cut = r2.json()["kalshi"][-1]["probabilities"]["cut_25bps"] * 100  # 1.0
    
    # Get "hike 25bps" probability
    r3 = requests.get(f"{base}/hike_25bps", params={"event_id": event_id, "hours": 1}, headers=headers)
    hike = r3.json()["kalshi"][-1]["probabilities"]["hike_25bps"] * 100
```

**API endpoint pattern**: `https://www.oddpool.com/api/events/history/<outcome>?event_id=<id>&hours=<N>`
- Outcomes: `no_change`, `cut_25bps`, `cut_50bps`, `hike_25bps`, `hike_50bps`
- Response: `{"kalshi": [{"timestamp": "...", "probabilities": {"<outcome>": 0.99}}], "polymarket": [...]}`
- Take `items[-1]` for latest value
- Probabilities are 0-1 floats (multiply by 100 for display)

**Event ID discovery**: FOMC dates are mid-month. Try days 14-20 for current and next month until a valid response comes back.

**Validation**: hold + cut_25 + hike_25 should sum to ~100%. Reject if > 105%.

## 6. Score-Text Alignment

**Symptom**: Score is -3 (bearish) but text says "伊朗局势支撑 + 欧佩克减产执行" (bullish).
**Root cause**: Scoring text was written independently of the scoring logic.

**Fix**: For negative scores, lead with bearish factors. For positive scores, lead with bullish factors. The text should explain WHY the score is that value.

## 7. Missing Weekly Change Calculations

**Symptom**: "周环比" column shows "—" for all indicators despite multi-date data.
**Root cause**: Rows were defined with hardcoded "—" placeholders. No calculation logic was implemented.

**Fix**: Add `wow_stats(df, keyword)` function that:
- Gets all values via `gv_all()` (sorted by date desc)
- Computes change: latest vs 5 trading days ago
- Computes average of recent 5 data points
- Returns (change_str, avg_str)

## 8. Dev Notes in Output

**Symptom**: "市场潜在风险提示（复刻能源风险话术）" appears in published report.
**Root cause**: Developer annotation was never removed before production use.

**Fix**: Search output for Chinese parentheses content that looks like dev notes: `grep '（.*）' report.md`

## 9. Cross-Report Inconsistency

**Symptom**: Same indicator (e.g., 10Y yield, FedWatch) shows different values across reports.
**Root cause**: Each script fetches independently; one may use stale data or hardcoded values.

**Fix**: All reports should use the same fetch functions and same data date. When auditing, compare indicator values across all report files.

## 10. CSV Date Fallback Missing

**Symptom**: Script crashes with KeyError when TODAY's CSV directory doesn't have all expected files.
**Root cause**: `load()` function only checks TODAY directory, returns empty DataFrame.

**Fix**: Always add date-based fallback:
```python
def load(name):
    p = DATA_DIR / "csv" / TODAY / f"{name}.csv"
    if p.exists(): return pd.read_csv(p)
    csv_root = DATA_DIR / "csv"
    if csv_root.exists():
        base = datetime.strptime(TODAY, "%Y-%m-%d")
        for i in range(1, 8):
            d = (base - timedelta(days=i)).strftime("%Y-%m-%d")
            p2 = csv_root / d / f"{name}.csv"
            if p2.exists(): return pd.read_csv(p2)
    return pd.DataFrame()
```

## 11. Empty DataFrame Column Access

**Symptom**: `KeyError: '品種'` when cotdata CSV is missing.
**Root cause**: `cot[cot["品種"].str.contains(...)]` fails when `cot` is an empty DataFrame (no columns at all).

**Fix**: Always guard: `if not cot.empty and "品種" in cot.columns:` before accessing columns.

## 12. Patch Tool Reliability with Multi-File Edits

**Symptom**: Multiple patch operations on the same file in one session may silently fail or get overwritten by subsequent patches.
**Root cause**: The patch tool uses fuzzy matching; if the file changes between patches (from an earlier patch), later patches may match stale context.

**Fix**: For large-scale changes to a single file, prefer `write_file` (full rewrite) over multiple `patch` calls. Read the full file first, make all changes, then write once. Reserve `patch` for single targeted edits.

## 13. Pipeline ALL_SOURCES Registration Gap

**Symptom**: A data-fetch function exists in `macro_pipeline.py` (e.g., `fetch_yahoo_futures()`, `fetch_cot()`) but never runs — no CSV generated, no log entries.

**Root cause**: `ALL_SOURCES` dict at line ~792 is a **hard reassignment**, not incremental. Any function added dynamically before that line (e.g., via `patch_cot()` at line 685) gets overwritten. Functions defined but not listed in the `ALL_SOURCES = {...}` block are invisible to `run_all()`.

**Fix**: Add every fetch function directly to the `ALL_SOURCES` dict literal:
```python
ALL_SOURCES = {
    "fedwatch": ("FedWatch FOMC概率", fetch_fedwatch),
    "fred": ("美聯儲 FRED", fetch_fred),
    ...
    "cot": ("CFTC COT持仓 (cotdata.net)", fetch_cot),      # WAS MISSING
    "yahoo": ("Yahoo Finance 期貨/外匯", fetch_yahoo_futures), # WAS MISSING
    ...
}
```

**Detection**: `grep -n 'def fetch_' macro_pipeline.py` to list all fetch functions, then `grep 'ALL_SOURCES\[' macro_pipeline.py` to see which are registered. Any fetch function not in ALL_SOURCES is dead code.

## 14. CFTC Pipeline URL Dead (dea.txt → 404)

**Symptom**: Pipeline log shows `CFTC 返回狀態碼 404`.

**Root cause**: `macro_pipeline.py` fetches from `https://www.cftc.gov/dea/futures/dea.txt` which was taken down. The `data_scrapers.py` functions use different URLs that still work.

**Fix**: Change pipeline URL to `https://www.cftc.gov/dea/newcot/FinFutWk.txt` (returns 200 as of 2026-06-14). The file is plain text with CFTC weekly commitments data.

**Alternative**: `financial_lf.htm` (200) and `ag_lf.htm` (200) also work but are HTML format requiring different parsing.

## 15. Yahoo CSV Staleness Threshold for Weekends

**Symptom**: Report generated on Sunday shows Thursday's prices even though Friday's close is available via Yahoo API.

**Root cause**: Staleness check uses `days_diff > 2`. On Sunday, Friday's data is 2 days old, which does NOT trigger `> 2`. The report falls back to the stale CSV (which has Thursday data from a Saturday pipeline run).

**Fix**: Use `>= 2` not `> 2`:
```python
yahoo_stale = days_diff >= 2  # Weekend: Fri→Sun = 2 days, should trigger
```

**Pattern**: When adding Yahoo direct API fallback to report scripts:
1. Load CSV with `load("yahoo_futures")`
2. Check `yahoo["日期"].max()` vs TODAY
3. If `days_diff >= 2`, fetch live from Yahoo Chart API for key symbols
4. Append live rows to DataFrame before generating report

This pattern was applied to `energy_weekly.py`, `metals_weekly.py`, and `agri_weekly.py`.

## 16. .env Key Gaps from Windows Migration

**Symptom**: Pipeline data sources return 401/403 despite keys being "known".

**Root cause**: `write_keys.py` was written for Windows path (`C:\Users\Administrator\...`). Keys were never written to the server's `~/.hermes/.env`. Missing keys: `USDA_NASS_API_KEY`, `CFTC_COT_ID`, `CFTC_COT_SECRET`, `ALPHA_VANTAGE_API_KEY`.

**Fix**: Check `.env` has all keys referenced by `macro_pipeline.py`:
```bash
grep -oP 'os\.getenv\("[A-Z_]+"' macro_pipeline.py | sort -u
# Compare with:
grep '^[A-Z_]*=' ~/.hermes/.env | sed 's/=.*//' | sort -u
```

**Note**: Adding the key to .env doesn't guarantee it's valid. USDA key `7CE43998-...` returns 401 even after being added — may need re-registration at nass.usda.gov/developers.

## 17. Markdown Table Pipe Missing

**Symptom**: Table row renders broken — missing closing `|`.
**Root cause**: f-string conditional branches that omit trailing ` | `:
```python
# BAD — missing | when tips_v is set
lines.append(f"| TIPS | {tips_v}% | — | text" if tips_v else "| TIPS | — | — | text")
# GOOD
lines.append(f"| TIPS | {tips_v}% | — | text |" if tips_v else "| TIPS | — | — | text |")
```

**Fix**: Always include trailing ` | ` in both branches of conditional f-strings.

## 18. ALL_SOURCES Must Be Defined AFTER All fetch_* Functions

**Symptom**: `NameError: name 'fetch_vix' is not defined` when running `python3 macro_pipeline.py`.

**Root cause**: `ALL_SOURCES` dict is defined at line ~846, but `fetch_vix()` is at line ~919 and `fetch_eia_steo()` at line ~998. Python evaluates dict values at creation time, so forward references fail.

**Fix**: Move `ALL_SOURCES`, `run_all()`, `main()`, and `if __name__` to the VERY END of the file, after ALL `def fetch_*` functions. File structure must be:

```
1. Imports + config
2. Utility functions (safe_get, save_csv, etc.)
3. ALL def fetch_* functions (fred, news, weather, eia, usda, cftc, finnhub, agsi, estat, fedwatch, cot, yahoo_futures, vix, eia_steo)
4. ALL_SOURCES = { ... }
5. def run_all()
6. def main()
7. if __name__ == "__main__": main()
```

**Detection**: `grep -n 'def fetch_\|^ALL_SOURCES\|^def run_all\|^def main\|if __name__' macro_pipeline.py` — verify ALL_SOURCES comes after the last `def fetch_*`.

## 19. Environment Variable Overrides .env — load_dotenv() Pitfall

**Symptom**: Pipeline uses wrong API key despite `.env` having the correct one. FRED returns 400 Bad Request, but `curl` with the .env key works fine.

**Root cause**: Shell environment variables take priority over `.env` file values. `load_dotenv(path)` does NOT override existing env vars by default. Even `load_dotenv(path, override=True)` may not work if the env var is set at the shell level before Python starts.

**Diagnosis**:
```bash
# Compare env var vs .env value
echo "$FRED_API_KEY" | head -c 10   # shell env
grep '^FRED_API_KEY=' ~/.hermes/.env | cut -c1-22  # .env file
```

**Fix options** (in order of reliability):
1. `export FRED_API_KEY=<correct_key>` in `~/.bashrc` + `source ~/.bashrc`
2. `load_dotenv(path, override=True)` in the script (may not override shell env)
3. Use `os.environ["FRED_API_KEY"] = key` explicitly after load_dotenv

**General rule**: When a pipeline API call returns 400/401 but the same key works via curl, the script is using a DIFFERENT key than what's in `.env`. Check the shell environment first.

## 20. FRED Rate Limiting with Rapid Sequential Requests

**Symptom**: Some FRED series (e.g., DGS5) produce 0 rows in CSV while others work fine. No error logged — `safe_get()` silently returns None after retries.

**Root cause**: The pipeline sends 29 FRED API requests in a tight loop with no delay. FRED's rate limiter occasionally rejects individual requests. Which series fails is non-deterministic (depends on timing).

**Fix**: Add `time.sleep(0.3)` between FRED API calls:
```python
for series_id, name in FRED_SERIES.items():
    data = safe_get(f"{FRED_BASE}/series/observations", params=params)
    # ... process data ...
    time.sleep(0.3)  # Prevent FRED rate limiting
```

Also add failure tracking:
```python
failed_series = []
# ... in loop:
if data and 'observations' in data:
    # process
else:
    failed_series.append(f"{series_id}({name})")
# after loop:
if failed_series:
    log.warning(f"FRED {len(failed_series)} series failed: {', '.join(failed_series)}")
```

## 21. Cloud Server API Connectivity Issues

**Symptom**: APIs return timeout (HTTP 000) or connection refused from cloud servers, but work fine from local machines.

**Known blocked services (as of 2026-06-14)**:
| Service | Symptom | Root Cause | Workaround |
|---------|---------|-----------|------------|
| USDA NASS (quickstats.nass.usda.gov) | TCP timeout 60s | Blocks cloud/datacenter IPs | Proxy through residential IP, or fetch locally + upload CSV |
| Some government APIs | 403/timeout | Geo-blocking or IP reputation | Route through V2Ray/Clash with residential exit |

**Diagnosis**: DNS resolves but TCP hangs:
```bash
nslookup quickstats.nass.usda.gov  # Works
curl -m 10 https://quickstats.nass.usda.gov/...  # Timeout
```

**Not blocked** (verified from cloud server): FRED, Yahoo Finance, EIA, oddpool.com, CFTC, AGSI+, Finnhub (news).

**Finnhub note**: Free tier does NOT include `/calendar/economic` endpoint (returns 403 "You don't have access to this resource"). News endpoint works fine on free tier.

**General approach**: For each new API, test connectivity from the server before integrating. Don't assume local=cloud connectivity.

## 22. Python .pyc Cache Causing Stale Code Execution

**Symptom**: Code changes to `.py` file don't take effect. Debug prints don't appear, old logic persists, new functions aren't called.

**Root cause**: Python caches compiled bytecode in `__pycache__/*.cpython-3XX.pyc`. If the `.pyc` timestamp is confused (e.g., NFS, Docker volumes, clock skew), Python uses the cached version without recompiling.

**Diagnosis**:
```bash
ls -la /path/to/__pycache__/macro_pipeline.cpython-310.pyc  # Compare with .py
```

**Fix**:
```bash
rm /path/to/__pycache__/macro_pipeline.cpython-310.pyc
# Or: python3 -B script.py  (the -B flag prevents .pyc creation)
```

**Prevention**: After major edits, always clear `__pycache__` before testing.

## 23. Multiple Copies of Same Script

**Symptom**: Editing a file but changes don't appear when running it.

**Root cause**: Multiple copies exist in different directories. `cd /root/hermes-pipeline && python3 macro_pipeline.py` should use the local file, but import paths or shell aliases may resolve differently.

**Diagnosis**: `find / -name "macro_pipeline.py" -not -path "*/proc/*" 2>/dev/null`

**Fix**: Use absolute paths. Keep one canonical location. Delete or rename stale copies.

## 24. Direct File Reading for .env Keys (Bypasses All Override Issues)

**Symptom**: `load_dotenv(override=True)` doesn't override shell env vars. Pipeline uses wrong API key despite `.env` having the correct one. FRED returns 400 Bad Request, but `curl` with the .env key works.

**Root cause**: Shell environment variables are set before Python starts (via `export` in `.bashrc` or parent process). `load_dotenv(override=True)` may not override these depending on python-dotenv version.

**Fix**: Read the `.env` file directly, bypassing dotenv entirely:
```python
def _load_env_key(key_name, env_path):
    """Read key directly from .env file — immune to shell env pollution."""
    try:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith(f"{key_name}=") and not line.startswith("#"):
                    return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return os.getenv(key_name, "")  # Fallback to env var

FRED_API_KEY = _load_env_key("FRED_API_KEY", ENV_PATH)
os.environ["FRED_API_KEY"] = FRED_API_KEY  # Force override shell env
```

**Critical**: Also remove any downstream `VAR = os.getenv("VAR", "")` lines that would re-read from the (wrong) shell environment.

**General rule**: When a pipeline API call returns 400/401 but the same key works via curl, the script is using a DIFFERENT key than what's in `.env`. Check the shell environment first with `echo "$VAR" | head -c 10`.

## 25. Partial Report Generation / Missing Reports

**Symptom**: User receives only 1-2 reports via email instead of all 5. Other reports are at previous day's date.

**Root cause**: Using `run_report.py <type>` generates only ONE report type. The other 4 remain at whatever date they were last generated.

**Report types**: macro, energy, metals, agri (global), agri_cn (China)

**Fix**: Use `run_all_reports.py` for complete batch generation:
```bash
python3 ~/hermes-pipeline/run_all_reports.py
```

**Verification**: Check all 5 reports have today's date:
```bash
ls ~/hermes-macro-data/reports/*$(date +%Y-%m-%d)*.md
# Should list: macro_weekly, energy_weekly, metals_weekly, agri_global, agri_china
```

## 27. Crontab Syntax Error Silently Disables ALL Scheduled Tasks

**Symptom**: Scheduled reports don't run despite crontab being configured. `cronjob list` (Hermes) shows empty. No log entries in `/var/log/hermes_reports.log`.

**Root cause**: `/etc/cron.d/hermes-reports` has a syntax error. Cron silently ignores the ENTIRE file when any line is malformed — one bad line kills all tasks in that file.

**Error found**: `0 30 8 * * *` — 6 time fields instead of standard 5.
```
# WRONG (6 fields — cron rejects entire file)
0 30 8 * * * root cd /root/hermes-pipeline && python3 scripts/daily_report.py

# CORRECT (5 fields: minute hour day month weekday)
30 8 * * * root cd /root/hermes-pipeline && python3 scripts/daily_report.py
```

**Cron format**: `分钟 小时 日 月 星期 命令` (exactly 5 time fields)

**Detection**: Check cron service logs for syntax errors:
```bash
journalctl -u cron --since "1 hour ago" | grep -i "error\|syntax\|bad"
# Look for: "Error: bad hour; while reading /etc/cron.d/hermes-reports"
#           "ERROR (Syntax error, this crontab file will be ignored)"
```

**Key insight**: `crontab -l` shows the user crontab, but `/etc/cron.d/` files are system-level and may differ. Always check BOTH locations. The system crontab files require an extra `user` field after the time fields.

**Fix**: Edit the malformed line in `/etc/cron.d/hermes-reports` and cron will auto-reload.

**Also check**: `/etc/cron.d/` files must have exactly 6 or 7 fields per line (5 time + user + command). Missing or extra fields cause silent rejection.

## 26. QQ邮箱 SMTP Authentication

**Symptom**: `smtplib.SMTPAuthenticationError: (535, b'Error: authentication failed')`

**Root cause**: Using QQ account password instead of authorization code (授权码).

**Fix**: 
1. Log into QQ邮箱 (mail.qq.com)
2. Settings → Account → POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV service
3. Enable SMTP service
4. Generate authorization code (授权码) — this is a 16-char string like `vqpbntclsvadbiii`
5. Use this code as `EMAIL_PASS` in `.env`, NOT your QQ password

**Config in .env**:
```
EMAIL_USER=your@qq.com
EMAIL_PASS=<authorization code, NOT QQ password>
EMAIL_TO=recipient@qq.com
EMAIL_HOST=smtp.qq.com
EMAIL_PORT=465
```

**Test**: `python3 ~/hermes-pipeline/test_email.py` — sends the latest metals report.
