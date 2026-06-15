# Cron 脚本化最佳实践

## Why Not `python3 -c` in Cron

**`python3 -c "..."` in crontab entries is fragile.**  Reasons:
1. Double-quote nesting conflicts with cron's shell quoting
2. Long one-liners are unreadable and error-prone
3. Syntax errors cause entire crontab file to be silently ignored
4. Truncation can silently occur when commands get too long

## Correct Pattern

Create a dedicated script file, reference it from cron:

```bash
# ✅ GOOD: Dedicated script
30 8 * * * root cd /root/hermes-pipeline && python3 scripts/daily_report.py

# ✅ GOOD: Pipeline with --source flag (single value)
0 23 * * 3 root cd /root/hermes-pipeline && python3 macro_pipeline.py --source eia
```

## Anti-patterns That Broke in Production

```bash
# ❌ FRAGILE: Inline -c with complex logic
0 8 * * * root cd /root/hermes-pipeline && python3 -c "import macro_pipeline as m; m.fetch_fred(); m.fetch_yahoo_futures(); import sqlite3,csv; from pathlib import Path; ..." 

# ❌ BROKEN: 6-field time spec
0 30 8 * * * root ...  # → cron silently ignores entire file

# ❌ BROKEN: Comma-separated --source
python3 macro_pipeline.py --source fred,yahoo  # → argparse rejects
```

## 2026-06-15 Production Incident

**Root cause:** `0 30 8 * * *` (6-field) in cron caused entire `/etc/cron.d/hermes-reports` to be silently ignored by cron daemon. All 11 tasks stopped.

**Symptom:** No reports or data collection for 2 days. Log file at `/var/log/hermes_reports.log` had zero new entries since June 13.

**Detection:** `grep "bad hour" /var/log/syslog`

**Fix:** `sed -i 's/0 30 8 \* \* \*/30 8 * * */' /etc/cron.d/hermes-reports`

**Verification:** `cron` daemon prints `RELOAD (/etc/cron.d/hermes-reports)` in syslog when file is corrected.
