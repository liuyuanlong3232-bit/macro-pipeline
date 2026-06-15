# QQ Bot Configuration Pitfalls

## Critical: Correct Config Format

### ❌ WRONG (what we tried first)
```yaml
platforms:
  qqbot:
    enabled: true
    app_id: "1904159904"
    secret: "IVUFl25tTovnQoGV"
    sandbox: false
```

### ✅ CORRECT (what actually works)
```yaml
platforms:
  qq:                          # "qq" not "qqbot"
    enabled: true
    extra:                     # Credentials MUST be under "extra"
      app_id: "1904159904"
      client_secret: "IVUFl25tTovnQoGV"  # "client_secret" not "secret"
      markdown_support: true
      dm_policy: "open"
      group_policy: "open"
```

## Environment Variables

### ❌ WRONG
```bash
QQ_APP_SECRET=IVUFl2...n### ✅ CORRECT
```bash
QQ_APP_ID=1904159904
QQ_CLIENT_SECRET=IVUFl2...n## Why This Matters

The QQ Bot adapter reads credentials from `extra.client_secret`, not from `secret` directly under the platform. This is documented in the Hermes source code:

```python
# From gateway/platforms/qqbot/adapter.py
# Configuration in config.yaml:
#   platforms:
#     qq:
#       extra:
#         app_id: "your-app-id"
#         client_secret: "your-secret"
```

## Common Error Messages

### "invalid appid or secret"
- Cause: Wrong credential format or location
- Fix: Move credentials under `extra`, use `client_secret` not `secret`

### "No messaging platforms enabled"
- Cause: Platform name is wrong (`qqbot` instead of `qq`)
- Fix: Change `platforms.qqbot` to `platforms.qq`

### "Yuanbao connect() failed"
- Cause: Old environment variable `YUANBAO_APP_ID` in shell
- Fix: Remove from `.env` and `.bashrc`, unset in current shell

## Verification Steps

1. Test credential validity:
```python
import asyncio, aiohttp
async def test():
    async with aiohttp.ClientSession() as s:
        async with s.post('https://bots.qq.com/app/getAppAccessToken', 
                         json={'appId':'YOUR_ID','clientSecret':'YOUR_SECRET'}) as r:
            print(await r.json())
asyncio.run(test())
```

2. Check gateway logs:
```bash
tail -20 /root/hermes-pipeline/logs/gateway.log
```

3. Verify QQ Bot connected:
```bash
hermes gateway status
# Should show: ✓ qqbot connected
```

## IP Whitelist

Don't forget to add VPS IP to QQ开放平台 whitelist:
- Go to https://q.qq.com
- Development Settings → IP Whitelist
- Add: 45.77.126.71
