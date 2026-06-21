# Report Pipeline Auditing — Pitfalls Catalog

General patterns discovered during report pipeline auditing sessions.

## 1. CSV Date Fallback Missing

Generator only checks TODAY directory, crashes when today's data doesn't exist. Always add date-based fallback scanning recent dates.

## 2. Empty DataFrame Column Access

`df["column"]` on empty DataFrame raises KeyError. Guard with `not df.empty and "column" in df.columns`.

## 3. Hardcoded Dates/Probabilities/Prices

CFTC report dates, FedWatch percentages, yield values, scoring text. Search for quoted numbers: `grep -n '"[0-9]\+\.[0-9]\+%"' *.py`

## 4. Language Mixing (繁简体)

FRED CSVs use 繁体中文 column names. Report text must be 简体. Keep lookup keys in 繁体, display strings in 简体.

## 5. Index vs Percentage

CPI/PPI from FRED are index levels, not YoY %. Must compute YoY from 12-month-ago data point. Use date string matching, NOT array indexing (gaps in data break index-based lookup).

## 6. Price vs Change % Confusion

Yahoo CSV has both `最新價` and `日漲跌幅%`. Don't conflate them. Create separate accessor functions for each.

## 7. Missing Markdown Table Pipes

f-string conditional branches that omit trailing ` | `:
```python
# BAD
f"| TIPS | {v}% | — | text" if v else "| TIPS | — | — | text"
# GOOD — both branches must end with |
f"| TIPS | {v}% | — | text |" if v else "| TIPS | — | — | text |"
```

## 8. Dev Notes in Output

Comments like "复刻XX话术" or "(调试用)" that leak into generated text. Search output for Chinese parentheses: `grep '（.*）' report.md`

## 9. Score-Text Alignment

When a score is negative (bearish), explanation must lead with bearish factors. Positive score → bullish factors first. Text should explain WHY.

## 10. Cross-Report Inconsistency

Same indicator shows different values across reports. Each script fetches independently. Compare values across all report files during audit.

## 11. JS SPA Pages Can't Be Scraped with requests.get()

Web pages built with React/Next.js/Vue return minimal HTML shell. `requests.get()` gets ~26 bytes, not the data. Look for underlying REST API endpoints by:
1. Open browser DevTools → Network tab
2. Filter by XHR/Fetch
3. Look for JSON API calls the page makes
4. Use those API URLs directly in Python

## 12. Patch Tool Reliability with Multi-File Edits

Multiple `patch` operations on the same file in one session may silently fail or get overwritten. The patch tool uses fuzzy matching; if the file changes between patches, later patches may match stale context.

**Fix**: For large-scale changes to a single file, prefer `write_file` (full rewrite) over multiple `patch` calls. Read the full file, make all changes mentally, then write once.

## 13. FedWatch / Prediction Market APIs

oddpool.com aggregates Kalshi + Polymarket data. It's a Next.js SPA — cannot scrape with requests. But has REST API:
- `GET /api/events/history/<outcome>?event_id=<id>&hours=<N>`
- Outcomes: `no_change`, `cut_25bps`, `hike_25bps`, etc.
- Returns JSON with Kalshi/Polymarket probability arrays
- Probabilities are 0-1 floats

## 14. CFTC Reports Are Plain Text, Not HTML

CFTC COT reports (financial_lf.htm, ag_lf.htm) are fixed-width PLAIN TEXT, not HTML tables. BeautifulSoup `find_all("table")` returns nothing.

**Detection**: If scraping returns data but no HTML tables, check `response.text[:200]` — CFTC starts with whitespace and fixed-width columns.

**Parsing approach**:
```python
idx = text.find("UST 10Y NOTE")
block = text[idx:idx+600]
# Find the data line: split by whitespace, expect 14+ numbers
for line in block.split('\n'):
    nums = line.strip().split()
    if len(nums) >= 14:
        am_net = int(nums[3].replace(",","")) - int(nums[4].replace(",",""))  # AM Long - Short
        lev_net = int(nums[6].replace(",","")) - int(nums[7].replace(",",""))  # Lev Long - Short
        break
```

**Column positions** (disaggregated format):
- 0: Open Interest
- 1-2: Producer/Merchant Long/Short
- 3-5: Swap Dealers Long/Short/Spreading
- 6-8: Managed Money Long/Short/Spreading
- 9-11: Other Reportables Long/Short/Spreading
