# Email Delivery Pattern for VPS Reports

## QQ SMTP Configuration

Store in `.env` on the VPS:

```
EMAIL_HOST=smtp.qq.com
EMAIL_PORT=465
EMAIL_USER=452731778@qq.com
EMAIL_PASS=<authorization_code>
EMAIL_TO=452731778@qq.com
```

Authorization code is NOT the QQ password. Generate at: QQ Mail → Settings → Account → POP3/IMAP/SMTP → Generate Authorization Code.

SMTP settings: smtp.qq.com:465, SSL required. Port 587 with STARTTLS also works but 465 SSL is more reliable.

## send_email.py — Enhanced Version (with Chart Embedding)

The enhanced `send_email.py` supports TWO modes:

### Mode 1: send_report(filepath, chart_type) — HTML email with embedded charts

Charts are base64-encoded and embedded as `data:image/png` directly in HTML body — no attachments needed. Recipient sees charts inline in the email without downloading anything.

```python
def send_report(filepath, chart_type=""):
    # chart_type controls which charts to include:
    # "macro"  → fred_trends.png
    # "metals" → cot_net.png + cot_index.png + cot_long_short.png
    # "energy" → cot charts only
    # ""       → no charts (agri, allocation)
    
    # Builds styled HTML:
    # - Chart section at top (heading + embedded base64 PNG)
    # - Report content rendered as markdown-to-HTML tables
    # - QQ mail compatible (no CSS @import, no JavaScript)
    # - Font: Microsoft YaHei via font-family fallback
```

### Mode 2: send_alert(subject, message) — Plain text alert (no charts)

```python
def send_alert(subject, message):
    # Prefix subject with "⚠️ "
    # Plain text body (works on all email clients)
    # Used by monitor.py for key-level alerts
```

### File structure layout:

```
~/hermes-macro-data/
  ├── charts/           ← Generated PNG files (~30-70KB each)
  │   ├── cot_net.png
  │   ├── cot_index.png
  │   ├── cot_long_short.png
  │   └── fred_trends.png
  ├── reports/          ← Generated markdown reports
  │   └── metals_weekly_2026-06-13.md
  └── alert_log.json    ← Alert dedup log (monitor.py)
```

## Chained Cron Pattern (using run_report.py wrapper)

Use the unified `run_report.py` wrapper instead of chaining individual commands:

```bash
0 9 * * 1 root cd /root/hermes-pipeline && python3 run_report.py macro  >> /var/log/hermes_reports.log 2>&1
0 9 * * 4 root cd /root/hermes-pipeline && python3 run_report.py energy >> /var/log/hermes_reports.log 2>&1
0 9 * * 5 root cd /root/hermes-pipeline && python3 run_report.py agri   >> /var/log/hermes_reports.log 2>&1
0 20 * * 5 root cd /root/hermes-pipeline && python3 run_report.py agri_cn >> /var/log/hermes_reports.log 2>&1
0 9 * * 6 root cd /root/hermes-pipeline && python3 run_report.py metals >> /var/log/hermes_reports.log 2>&1
0 10 * * 0 root cd /root/hermes-pipeline && python3 run_report.py allocation >> /var/log/hermes_reports.log 2>&1
```

What `run_report.py` does internally:
1. `python3 charts.py` (for macro/metals/energy — generates 4 PNGs)
2. `python3 <report_script>.py` (generates markdown)
3. `send_report(report_path, chart_type)` (embeds + sends)

## Cron Email Schedule (FINAL, Beijing Time)

```
周一 09:00  → 宏观周报 (含FRED趋势图) → QQ邮箱
周四 09:00  → 能源周报 (含COT图)    → QQ邮箱
周五 09:00  → 国际农业                → QQ邮箱
周五 20:00  → 中国农业                → QQ邮箱
周六 09:00  → 贵金属周报 (含COT全套图) → QQ邮箱
周日 10:00  → 资产配置总控            → QQ邮箱
每2小时     → 关键位预警              → QQ邮箱
```

## Stale Cron Script Name Pitfall

The cron entries MUST use the EXISTING script filenames on the VPS. Common mis-matches:

| Expected in cron | Actual file | Problem |
|-----------------|-------------|---------|
| `macro.py` | `macro_weekly.py` | ❌ File does not exist |
| `energy.py` | `energy_weekly.py` | ❌ File does not exist |
| `metals.py` | `metals_weekly.py` | ❌ File does not exist |
| `agri_intl.py` / `agri_cn.py` | `agri_weekly.py` | ❌ Single file for both |
| `send_email.py` | not deployed | ❌ Missing entirely |

Fix: Always verify with a dual check:
```bash
ls /root/hermes-pipeline/*.py           # what exists
cat /etc/cron.d/hermes-reports          # what cron references
```

If they don't match, the cron job silently succeeds (exit code 0) but produces no output. The user gets no reports and no errors — completely invisible failure.
