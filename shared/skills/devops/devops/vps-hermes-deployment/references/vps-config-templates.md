# VPS Configuration Reference

## SSH Configuration

### Local Machine (~/.ssh/config)
```config
Host vps
    HostName 45.77.126.71
    Port 58234
    User root
    IdentityFile C:\Users\Administrator\.ssh\id_rsa
```

### VPS (~/.ssh/config)
```config
Host vps
    HostName 45.77.126.71
    Port 58234
    User root
    IdentityFile /root/.ssh/id_ed25519
```

## QQ Bot Configuration Template

### config.yaml (correct format)
```yaml
model:
  provider: xiaomi
  default: xiaomi/mimo-v2.5-pro
  base_url: https://token-plan-cn.xiaomimimo.com/v1

gateway:
  bind: 0.0.0.0:8642

platforms:
  qq:
    enabled: true
    extra:
      app_id: "YOUR_APP_ID"
      client_secret: "YOUR_SECRET"
      markdown_support: true
      dm_policy: "open"
      group_policy: "open"
```

### .env Template
```bash
# MiMo Token Plan
XIAOMI_API_KEY=tp-cpy...n
XIAOMI_BASE_URL=https://token-plan-cn.xiaomimimo.com/v1

# QQ Bot
QQ_APP_ID=1904159904
QQ_CLIENT_SECRET=IVUFl2...n
QQ_ALLOW_ALL_USERS=true
GATEWAY_ALLOW_ALL_USERS=true

# Financial Data APIs
FRED_API_KEY=40fa26...n
EIA_API_KEY=IjwseZ...n
TUSHARE_TOKEN=ca8f00...n
FINNHUB_API_KEY=d8jdg9...n
AGSI_API_KEY=35ae75...n

# Email
EMAIL_HOST=smtp.qq.com
EMAIL_PORT=465
EMAIL_USER=452731778@qq.com
EMAIL_PASS=your_smtp_password
EMAIL_TO=452731778@qq.com
```

## Cron Job Templates

### /etc/cron.d/hermes-reports
```bash
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Data Collection (China Time UTC+8)
# Daily FRED/Yahoo
0 8 * * * root cd /root/hermes-pipeline && python3 -c "import macro_pipeline; macro_pipeline.fetch_fred(); macro_pipeline.fetch_yahoo_futures()" >> /var/log/hermes_data.log 2>&1

# EIA (Wednesday 22:30 Beijing)
0 23 * * 3 root cd /root/hermes-pipeline && python3 -c "import macro_pipeline; macro_pipeline.fetch_eia()" >> /var/log/hermes_data.log 2>&1

# COT (Friday 03:30 Beijing)
0 4 * * 5 root cd /root/hermes-pipeline && python3 -c "import macro_pipeline; macro_pipeline.fetch_cot()" >> /var/log/hermes_data.log 2>&1

# Report Generation (China Time)
0 9 * * 1 root cd /root/hermes-pipeline && python3 run_report.py macro >> /var/log/hermes_reports.log 2>&1
0 9 * * 4 root cd /root/hermes-pipeline && python3 run_report.py energy >> /var/log/hermes_reports.log 2>&1
0 9 * * 5 root cd /root/hermes-pipeline && python3 run_report.py agri >> /var/log/hermes_reports.log 2>&1
0 20 * * 5 root cd /root/hermes-pipeline && python3 run_report.py agri_cn >> /var/log/hermes_reports.log 2>&1
0 9 * * 6 root cd /root/hermes-pipeline && python3 run_report.py metals >> /var/log/hermes_reports.log 2>&1
0 10 * * 0 root cd /root/hermes-pipeline && python3 run_report.py allocation >> /var/log/hermes_reports.log 2>&1
```

## Custom Skills Template

### SKILL.md Template
```markdown
---
name: skill-name
description: "Short description"
version: 1.0.0
author: User
metadata:
  hermes:
    tags: [tag1, tag2, tag3]
---

# Skill Name

## Overview
Brief description of what this skill does.

## Usage
How to use this skill.

## Rules
1. Rule 1
2. Rule 2

## Examples
Example usage.
```

## Troubleshooting Commands

### Check System Status
```bash
# Timezone
timedatectl | grep "Time zone"

# Hermes status
hermes gateway status
hermes --version

# Cron jobs
cat /etc/cron.d/hermes-reports
crontab -l

# Logs
tail -20 /root/hermes-pipeline/logs/gateway.log
tail -20 /var/log/hermes_reports.log
```

### Test API Connections
```bash
# FRED
export FRED_API_KEY=*** && python3 -c "import requests; r=requests.get('https://api.stlouisfed.org/fred/series/observations?series_id=GDP&api_key='+\"$FRED_API_KEY\"+'&file_type=json&limit=1'); print(r.status_code)"

# QQ Bot
python3 -c "
import asyncio, aiohttp
async def test():
    async with aiohttp.ClientSession() as s:
        async with s.post('https://bots.qq.com/app/getAppAccessToken', json={'appId':'YOUR_ID','clientSecret':'YOUR_SECRET'}) as r:
            print(await r.json())
asyncio.run(test())
"
```

### Restart Services
```bash
# Restart gateway
hermes gateway stop
sleep 2
nohup hermes gateway > /tmp/hermes_gateway.log 2>&1 &

# Reload environment
source ~/.bashrc
source /root/hermes-pipeline/.env
```
