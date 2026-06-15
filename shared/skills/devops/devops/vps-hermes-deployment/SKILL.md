---
name: vps-hermes-deployment
description: "Deploy and configure Hermes Agent on VPS (Vultr/AWS/Lightsail) with QQ Bot, cron jobs, and Chinese timezone support"
version: 1.0.0
author: Agent
metadata:
  hermes:
    tags: [vps, deployment, qq-bot, cron, china, timezone]
---

# VPS Hermes Deployment

Deploy Hermes Agent on a VPS for 24/7 automated report generation, data collection, and messaging integration.

## Prerequisites

- VPS with Ubuntu 22.04+ (1vCPU/1GB minimum)
- SSH access (key-based auth recommended)
- API keys for LLM provider (MiMo/DeepSeek/OpenRouter)
- QQ Bot credentials (if using QQ integration)

## Critical Configuration Facts

### SSH Key Path
**VPS SSH key is `id_rsa`, NOT `id_ed25519`**
```bash
# Correct connection command
ssh -p 58234 -i C:\Users\Administrator\.ssh\id_rsa root@45.77.126.71
```

### HERMES_HOME Path
**VPS uses `/root/hermes-pipeline/` NOT `/root/.hermes/`**
```bash
# Correct config location
/root/hermes-pipeline/config.yaml
/root/hermes-pipeline/.env
```

### Timezone Configuration
**Must set to Asia/Shanghai for Chinese cron jobs**
```bash
timedatectl set-timezone Asia/Shanghai
# Verify: date "+%Y-%m-%d %H:%M:%S %Z"
```

## QQ Bot Configuration

### Correct Config Format
```yaml
# /root/hermes-pipeline/config.yaml
platforms:
  qq:                          # NOT "qqbot"
    enabled: true
    extra:                     # Credentials under "extra"
      app_id: "YOUR_APP_ID"
      client_secret: "YOUR_SECRET"  # NOT "secret"
      markdown_support: true
      dm_policy: "open"
      group_policy: "open"
```

### Common Mistakes
- ❌ `platforms.qqbot.secret` → ✅ `platforms.qq.extra.client_secret`
- ❌ `QQ_APP_SECRET` in .env → ✅ `QQ_CLIENT_SECRET` in .env
- ❌ Credentials directly under platform → ✅ Credentials under `extra`

### Environment Variables (.env)
```bash
QQ_APP_ID=1904159904
QQ_CLIENT_SECRET=IVUFl25tTovnQoGV
QQ_ALLOW_ALL_USERS=true
```

### Verification
```bash
# Test QQ Bot connection
hermes gateway status
# Check logs
tail -20 /root/hermes-pipeline/logs/gateway.log
```

## Cron Job Configuration

### ⚠️ Cron Pattern: Use Script Files, NOT inline `python3 -c`

**NEVER use `python3 -c "..."` in cron.** The double-quotes inside the string clash with cron's shell quoting, causing silent truncation, syntax errors, and missing data. Always create a dedicated script file.

```bash
# ❌ WRONG (causes quoting/truncation bugs):
0 8 * * * root cd /root/hermes-pipeline && python3 -c "import macro_pipeline; macro_pipeline.fetch_fred()"

# ✅ CORRECT (use --source flag on main pipeline):
0 8 * * * root cd /root/hermes-pipeline && python3 macro_pipeline.py --source fred

# ✅ CORRECT (use dedicated script for complex logic):
0 6 * * 2 root cd /root/hermes-pipeline && python3 scripts/check_usda.py
```

**NOTE:** `--source` takes a SINGLE value, not comma-separated. To run multiple sources, call the pipeline multiple times or use a helper script.

See `references/cron-pattern-python.md` for the detailed pattern.

### Data Collection (China Time)
```bash
# /etc/cron.d/hermes-reports
# Daily FRED+Yahoo collection — read both sources with macro_pipeline methods
0 8 * * * root cd /root/hermes-pipeline && python3 -c "import macro_pipeline as m; m.fetch_fred(); m.fetch_yahoo_futures(); m.save_data()" >> /var/log/hermes_data.log 2>&1

# EIA (Wednesday 22:30 Beijing → collect 23:00)
0 23 * * 3 root cd /root/hermes-pipeline && python3 macro_pipeline.py --source eia >> /var/log/hermes_data.log 2>&1

# COT (Friday 03:30 Beijing → collect 04:00)
0 4 * * 5 root cd /root/hermes-pipeline && python3 macro_pipeline.py --source cot >> /var/log/hermes_data.log 2>&1
```

### Report Generation (China Time)
```bash
# Daily 08:30 — Daily snapshot report
30 8 * * * root cd /root/hermes-pipeline && python3 scripts/daily_report.py >> /var/log/hermes_data.log 2>&1

# Weekly reports
0 9 * * 1 root cd /root/hermes-pipeline && python3 run_report.py macro >> /var/log/hermes_reports.log 2>&1
0 9 * * 4 root cd /root/hermes-pipeline && python3 run_report.py energy >> /var/log/hermes_reports.log 2>&1
0 9 * * 5 root cd /root/hermes-pipeline && python3 run_report.py agri >> /var/log/hermes_reports.log 2>&1
0 20 * * 5 root cd /root/hermes-pipeline && python3 run_report.py agri_cn >> /var/log/hermes_reports.log 2>&1
0 9 * * 6 root cd /root/hermes-pipeline && python3 run_report.py metals >> /var/log/hermes_reports.log 2>&1
0 10 * * 0 root cd /root/hermes-pipeline && python3 run_report.py allocation >> /var/log/hermes_reports.log 2>&1

# Checks
0 6 * * 2 root cd /root/hermes-pipeline && python3 scripts/check_usda.py >> /var/log/hermes_data.log 2>&1
```

### Data Source Release Schedule (Beijing Time)
| Source | Release Time | Collect Time |
|--------|-------------|--------------|
| FRED | Daily (varies) | 08:00 |
| Yahoo | Real-time | 08:00 |
| EIA | Wednesday 22:30 | Wednesday 23:00 |
| COT | Friday 03:30 | Friday 04:00 |
| USDA | Friday (varies) | Friday 09:00 |

## Skill Deployment

### Custom Skills Location
**VPS skills go in `/root/hermes-pipeline/skills/` NOT `/root/.hermes/skills/`**
```bash
# Create skill directory
mkdir -p /root/hermes-pipeline/skills/my-skill

# Write SKILL.md
cat > /root/hermes-pipeline/skills/my-skill/SKILL.md << 'EOF'
---
name: my-skill
description: "Skill description"
---
# Skill content
EOF

# Verify
hermes skills list | grep my-skill
```

## Gateway Management

### Start/Stop/Restart
```bash
# Start gateway
nohup hermes gateway > /tmp/hermes_gateway.log 2>&1 &

# Check status
hermes gateway status

# Stop gateway
hermes gateway stop

# Install as system service
hermes gateway install
sudo loginctl enable-linger root
```

### Log Locations
```bash
/root/hermes-pipeline/logs/gateway.log
/root/hermes-pipeline/logs/agent.log
/root/hermes-pipeline/logs/errors.log
/var/log/hermes_gateway.log
/var/log/hermes_reports.log
```

## Email Configuration

### QQ Mail SMTP
```bash
# .env
EMAIL_HOST=smtp.qq.com
EMAIL_PORT=465
EMAIL_USER=452731778@qq.com
EMAIL_PASS=your_smtp_password
EMAIL_TO=452731778@qq.com
```

**⚠️ Email config is fragile.** These 5 lines are easily lost during `.env` edits. If email delivery suddenly stops working, check that all EMAIL_ variables are still present. See `references/dotenv-mutation.md` for the safe approach to modifying `.env`.

Daily report generation uses `scripts/daily_report.py` which reads from the SQLite database directly. See the `data-pipeline` skill's `references/database-schema-mappings.md` for correct table and column names (繁简 differences, special characters in column names, VIX in separate table).

## Token Consumption Patterns

### Code Refactoring is Expensive
One session of code refactoring (6 files, 3178 insertions, 1567 deletions) consumed ~236M tokens:
- mimo-v2.5: 40M tokens
- mimo-v2.5-pro: 195M tokens

At the most expensive multiplier (4x for 1M context Pro), this equals ~822M Credits = ~20% of Lite plan.

**Monthly plan lifespan at heavy code refactoring pace:**
| Plan | Monthly Credits | Days at Current Pace |
|------|----------------|---------------------|
| Lite ¥39 | 4.1B | ~5 |
| Standard ¥99 | 11B | ~13 |
| Pro ¥329 | 38B | ~45 |
| Max ¥659 | 82B | ~90+ |

**Mitigation:**
- Normal report generation (no code refactoring) uses far fewer tokens
- Restrict VPS Hermes to data collection + report generation only
- Keep code editing tasks on local Hermes (you can see/approve consumption)
- Use `mimo-v2.5` (non-Pro, 1x credit) for simpler tasks

## Skill Deployment via tar.gz

For bulk skill deployment (e.g., gbrain with 81 skills):

```bash
# Local: package skills
cd ~/AppData/Local/hermes/skills
tar czf /tmp/vps_skills.tar.gz hermes-dojo brainstorming gbrain

# Send to VPS
scp -P 58234 -i C:\\Users\\Administrator\\.ssh\\id_rsa /tmp/vps_skills.tar.gz root@45.77.126.71:/tmp/

# On VPS: extract
cd /root/hermes-pipeline/skills
tar xzf /tmp/vps_skills.tar.gz

# Verify
hermes skills list | grep -E "skill-name"
```

## VPS Workflow Pattern

See `references/vps-workflow-pattern.md` for the "code on VPS, chat on local" workflow.

All code changes should be done directly on VPS (root, no interruptions). Local Hermes handles chat and decision-making only. After VPS changes, sync to local and push to GitHub.

For the VPS Hermes collaboration model (diagnose vs fix), see `references/vps-hermes-collaboration.md`.
For a concrete example with the cron 6-field syntax error, see `references/vps-hermes-collaboration-example.md`.
For cron syntax rules (5-field requirement), see `references/cron-5-field-syntax.md`.
For `.env` mutation dangers, see `references/dotenv-mutation-lessons.md`.
For cron script best practices (avoid inline -c), see `references/cron-script-best-practices.md`.
For memory sync between local and VPS (scp method), see `references/memory-sync-scp.md`.

## Pitfalls

1. **Wrong SSH key**: Always use `id_rsa`, not `id_ed25519`
2. **Wrong HERMES_HOME**: VPS uses `/root/hermes-pipeline/`
3. **QQ Bot credential format**: Must be under `extra`, not directly under platform
4. **Timezone**: Must set to Asia/Shanghai for Chinese cron jobs
5. **Monitor.py**: Don't use 4-hour monitoring for non-real-time data (use weekly reports instead)
6. **FRED API key truncation**: Bash `echo` truncates keys. Use Python `f.write()`. See `references/fred-api-key-fix.md`.
7. **Environment variables**: Always verify with `echo $VAR` after setting
8. **`.env` mutation is destructive**: Every `echo >> .env`, `sed -i`, or inline edit on `.env` risks corrupting keys, introducing garbage lines (like `✅ 邮箱配置已添加`), or silently truncating values to `***`. **Never edit `.env` inline on VPS.** Write the complete file from Python or scp a clean copy from local. See `references/dotenv-mutation.md`.
9. **Cron `--source` is single-value**: `--source fred,yahoo` fails. Run `macro_pipeline.py` once per source or use a helper script.
10. **SSH quoting hell**: Avoid `ssh root@vps "echo 'FRED_API_KEY=xxx' >> .env"` — the double-quote-inside-double-quote pattern almost always fails. Write to a local file, scp it, or use `python3 << 'PYEOF'` heredoc on the remote.
11. **Cron MUST have exactly 5 time fields**: `30 8 * * *` not `0 30 8 * * *` (6 fields). One extra field causes the ENTIRE crontab file to be silently ignored by cron daemon. All tasks stop running. Always verify with `grep -n "python3" /etc/cron.d/hermes-reports | awk '{fields=0; for(i=1;i<=5;i++) if($i ~ /^[0-9*]/) fields++; print NR\": \"fields\" fields\"}'`.
12. **VPS Hermes cannot self-repair**: VPS Hermes (hermes chat) is blocked from writing to `/etc/cron.d/`, reading `.env`, and running unapproved terminal commands. It can DIAGNOSE problems but cannot FIX them. The fix must come through SSH (from local Hermes). Pattern: VPS Hermes diagnoses → reports to user → user tells local Hermes → local Hermes SSHs to VPS → fixes it.
