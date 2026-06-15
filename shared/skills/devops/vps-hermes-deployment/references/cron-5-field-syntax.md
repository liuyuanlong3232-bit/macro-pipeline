# Cron Syntax: The 5-Field Rule

## The Bug

```
❌ 0 30 8 * * * root cd .../daily_report.py
   ^^^^^^^^^ 6 fields → ENTIRE crontab silently ignored

✅ 30 8 * * * root cd .../daily_report.py
   ^^^^^^^^ 5 fields → correct
```

## Diagnosis

When cron suddenly stops executing ALL tasks, check for syntax errors:

```bash
# Check system logs
grep "hermes-reports" /var/log/syslog | tail -5
# Look for: "ERROR (Syntax error, this crontab file will be ignored)"

# Count time fields per line
grep -n "python3" /etc/cron.d/hermes-reports | while read line; do
  echo "$line" | awk '{c=0;for(i=1;i<=5;i++)if($i~/^[0-9*]/)c++}END{print c" fields"}'
done
```

## Root Cause: 08:30 vs 8:30

The temptation to write `0 30 8 * * *` comes from thinking "midnight + 30 minutes + 8 hours". But cron's format is:
```
minute hour day month weekday
```
So "8:30 AM every day" = `30 8 * * *` (minute=30, hour=8).

## Correct Patterns

| Intent | Correct | Wrong |
|--------|---------|-------|
| Every day 08:30 | `30 8 * * *` | `0 30 8 * * *` |
| Every day 08:00 | `0 8 * * *` | `0 0 8 * * *` |
| Every day 23:30 | `30 23 * * *` | `0 30 23 * * *` |

## Validation

After ANY cron edit, verify:
```bash
# 1. All lines have 5 time fields
grep -n "python3" /etc/cron.d/hermes-reports | awk '{c=0;for(i=1;i<=5;i++)if($i~/^[0-9*]/)c++}END{print NR": "c" fields"}'

# 2. Cron daemon accepted the file
grep "hermes-reports" /var/log/syslog | tail -3
# Should show RELOAD, NOT "Syntax error... ignored"
```

## Impact

One bad line = **entire file ignored**. All reports, all data collection, daily snapshots, USDA checks — everything stops. No partial execution. This is why a simple 6-field typo caused all reports to fail for 24+ hours on 2026-06-14~15.
