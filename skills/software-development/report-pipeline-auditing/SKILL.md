---
name: report-pipeline-auditing
description: >
  Audit and fix data pipeline report generators — compare generated output against
  source data, identify mismatches/missing data/formatting errors, fix systematically
  by priority, verify end-to-end. Covers Python scripts that read CSV/API data and
  produce markdown/HTML/text reports.
triggers:
  - "audit report"
  - "check report for errors"
  - "report data mismatch"
  - "fix report generator"
  - "report quality"
  - "data pipeline report"
---

# Report Pipeline Auditing

## When to Use

When the user asks to audit, verify, or fix scripts that generate reports from data sources (CSV files, APIs, databases). Common in financial/macro/analytical report pipelines.

## User Preferences (this user)

- Language: Chinese (simplified). Reports and communication in Chinese.
- Wants THOROUGH audit first — compare every data point in output against source.
- Wants severity-ranked issue list (P0/P1/P2) before fixing.
- Wants systematic fix-by-fix execution with verification at the end.
- Prefers a detailed audit report table showing: issue, location, expected vs actual, severity.
- After fixing, wants the reports re-generated so they can visually verify.
- **Key preference**: When data is missing from reports, the user wants you to go to official sources and get the actual data, not just leave "—". Use browser tool to visit official sites, extract data, and either fix the scraper or hardcode verified values as fallback. The user explicitly asked: "这些你去官网搜一手资料发报告前填写上就行".

## Workflow

### Phase 1: Audit (do NOT skip)

1. **Read all generator scripts** — understand what data sources they use, what transforms they apply, what output they produce.
2. **Read all source data files** (CSV, API responses) — know what data is actually available.
3. **Read the generated output** — the report(s) to audit.
4. **Compare systematically**: For every data point in the report, trace it back to the source. Check:
   - Value correctness (is the number right?)
   - Source attribution (does the report cite the right source?)
   - Formatting (%, units, decimal places, language consistency)
   - Missing data (shows "—" but source has the value? Or source is genuinely missing?)
   - Hardcoded values (dates, probabilities, prices that should be dynamic)
   - Stale data (using old data when newer exists)
5. **Produce audit report** with:
   - Severity levels: P0 (data error), P1 (missing data/format), P2 (cosmetic/wording)
   - For each issue: file, line, what's wrong, expected value, source of truth
   - Summary table of all issues

### Phase 2: Fix (one by one)

1. Fix P0 issues first, then P1, then P2.
2. After each fix, confirm the edit applied correctly (search_files or read_file).
3. Mark each fix as completed in a todo list.

### Phase 3: Verify

1. Re-run all generator scripts.
2. Check output for the specific fixes applied.
3. Report remaining known limitations to user.

## Common Pitfalls (from experience)

See `references/pitfalls.md` for detailed patterns. Key ones:

1. **CSV fallback missing** — Generator only checks TODAY directory, crashes when today's data doesn't exist. Always add date-based fallback.
2. **Empty DataFrame access** — `df["column"]` on empty DataFrame raises KeyError. Always guard with `not df.empty and "column" in df.columns`.
3. **Hardcoded dates/probabilities** — CFTC report dates, FedWatch percentages, prices. Replace with dynamic reads.
4. **Language mixing** — Traditional Chinese characters in simplified Chinese reports (common when code evolves across developers).
5. **Value vs percentage confusion** — Displaying raw price where % change should be, or CPI index instead of YoY%.
6. **Missing markdown table pipes** — f-string conditional branches that omit trailing ` | `.
7. **Dev notes in output** — Comments like "复刻XX话术" that leak into generated text.
8. **External API sanity** — FedWatch probabilities summing to >100%, negative prices, etc. Always validate.
9. **JS SPA detection** — If web scraping returns minimal HTML (~26 bytes), the page is likely a SPA. Look for REST API endpoints in browser DevTools Network tab instead.
10. **Patch tool reliability** — Multiple patch calls on same file can silently conflict. Prefer write_file for bulk changes. When a patch "applies successfully" but the change doesn't appear in the file, the fuzzy matcher may have found a different location. Always verify with search_files after patching.
11. **data_scrapers import failure** — If `data_scrapers.py` imports a missing module (e.g., `pdfplumber`), the entire module fails to import, and all `from data_scrapers import X` calls silently fail in try/except blocks. Always add inline fallback data in report scripts so they never depend solely on scraper imports.
12. **JS SPA pages** — If `requests.get()` returns HTML with length <100 bytes, the page is a JavaScript SPA. Use browser DevTools Network tab to find the actual REST API endpoints the page calls.
