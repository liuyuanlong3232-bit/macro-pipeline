# `.env` File Mutation is Destructive

## The Problem

`.env` files on VPS are fragile. Multiple edits over a session inevitably corrupt them:

```
# After 3-4 edits, the file becomes:
# MiMo Token Plan
XIAOMI_API_KEY=tp-cpy...fsqe
# QQ Bot
QQ_APP_ID=1904159904
QQ_CLIENT_SECRET=***
QQ_ALLOW_ALL_USERS=true
# Financial Data APIs
# FRED API
# FRED API
FRED_API_KEY=40fa26...91b2
# Email (QQ邮箱)
✅ 邮箱配置已添加          ← GARBAGE from echo command
grep "EMAIL" ...             ← GARBAGE from failed heredoc
EMAIL_USER=452731778@qq.com  ← DUPLICATE from multiple appends
EMAIL_USER=452731778@qq.com  ← DUPLICATE
EMAIL_PASS=vqpbntclsvadbiii
EMAIL_TO=452731778@qq.com
EMAIL_HOST=smtp.qq.com
EMAIL_PORT=465
```

The Email config was completely lost during FRED key fixes (2026-06-14~15), causing all report delivery to silently fail for 24+ hours.

## Why This Happens

1. `echo "VALUE" >> .env` fails when VALUE contains special chars
2. `sed -i` leaves orphaned comment lines
3. Heredoc syntax (`<< 'EOF'`) breaks in SSH quoting
4. Multiple operations leave duplicates and garbage

## The Safe Approach

### Option 1: Write from Python (on VPS)
```python
python3 << 'PYEOF'
lines = [
    "# MiMo", "XIAOMI_API_KEY=...", "",
    "# QQ", "QQ_APP_ID=...", "QQ_CLIENT_SECRET=...", "",
    "# FRED", "FRED_API_KEY=...", "",
    "# Email", "EMAIL_USER=...", "EMAIL_PASS=...",
    "EMAIL_TO=...", "EMAIL_HOST=smtp.qq.com", "EMAIL_PORT=465",
]
open("/root/hermes-pipeline/.env", "w").write("\n".join(lines) + "\n")
PYEOF
```

### Option 2: scp from local
```bash
# Write clean .env locally
echo "...content..." > C:\tmp\env_clean

# Upload to VPS
scp C:\tmp\env_clean root@vps:/root/hermes-pipeline/.env
```

### Option 3: Use write_file tool (when available)
The Hermes `write_file` tool writes complete files atomically, no shell quoting issues.

## NEVER Do This
- `echo "KEY=VALUE" >> .env` (truncation, garbage)
- `sed -i` on .env (leaves orphan lines)
- `ssh root@vps "echo ..."` (double-quote hell)
- Multiple incremental edits (accumulate errors)

## Recovery Checklist

If email delivery stops:
1. Check `grep EMAIL /root/hermes-pipeline/.env` — all 5 vars present?
2. Check for garbage lines (non-KEY=VALUE patterns)
3. Remove duplicates with `sed -i "/^EMAIL/d; echo 'EMAIL_USER=...'"` (NO — this is the problem pattern!)
4. Instead: rewrite the entire .env from a clean template
