# QQ Bot Integration Reference

## VPS Gateway Configuration

### Config.yaml format (NOT ~/.hermes/config.yaml — use /root/hermes-pipeline/config.yaml)

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
      app_id: "1904159904"
      client_secret: "your-secret-here"
      markdown_support: true
      dm_policy: "open"
      group_policy: "open"
```

### .env file

```bash
QQ_APP_ID=1904159904
QQ_CLIENT_SECRET=your-secret-here
QQ_ALLOW_ALL_USERS=true
GATEWAY_ALLOW_ALL_USERS=true
```

### Common pitfalls

1. **Wrong platform key**: Use `qq` NOT `qqbot` in config.yaml
2. **Wrong env var names**: `QQ_CLIENT_SECRET` NOT `QQ_APP_SECRET`
3. **Credentials under `extra:`**: NOT directly under platform
4. **Hermes reads from /root/hermes-pipeline/**, NOT from /root/.hermes/ on this VPS
5. **API Key format**: `tp-xxxxx` for Token Plan, different from regular API key
6. **Token Plan uses different base URL**: `https://token-plan-cn.xiaomimimo.com/v1` (NOT `https://api.xiaomimimo.com/v1`)

### Gateway management

```bash
# Start
nohup hermes gateway > /var/log/hermes_gateway.log 2>&1 &

# Check
hermes gateway status

# Stop (before editing config)
hermes gateway stop
sleep 2
nohup hermes gateway > /var/log/hermes_gateway.log 2>&1 &

# Pair first user
# User sends a message to the bot → gets a pairing code
hermes pairing approve qqbot PAIRING_CODE

# Check logs
tail -f /root/hermes-pipeline/logs/gateway.log
tail -f /root/hermes-pipeline/logs/errors.log
```

### Limits
- Proactive messages: 4/month per user
- Passive (replies): Unlimited
- Markdown, images, files supported
- Need QQ开放平台 app registration at https://q.qq.com
- Need IP whitelist configured (VPS IP: 45.77.126.71)
