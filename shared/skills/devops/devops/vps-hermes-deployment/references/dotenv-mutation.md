# .env Mutation Pattern

## Root Cause
Every shell-based edit to `.env` on VPS risks corruption:
- `echo "KEY=value" >> .env` → double-quote conflicts if value contains special chars
- `sed -i` → silent truncation to `***` for values with `#` or `"` chars
- `cat >> .env << 'EOF'` → accidental garbage lines like `✅ 邮箱配置已添加` or `echo "===" when heredoc boundaries shift
- `ssh root@vps "echo 'FRED_API_KEY=*** >> .env"` → double-quote-inside-double-quote almost always fails

## Damaged Output Examples
```
# Bad: truncated key (3 chars instead of 32)
FRED_API_KEY=***

# Bad: shell command artifacts left in .env
grep "EMAIL" /root/hermes-pipeline/.env
EMAIL_USER=452731778@qq.com
✅ 邮箱配置已添加

# Bad: duplicate lines after multiple failed edits
EMAIL_USER=452731778@qq.com
EMAIL_USER=452731778@qq.com
```

## Correct Approach: Write Complete .env from Python

```python
# clean_env.py — run locally to generate clean .env, then scp to VPS
lines = []
lines.append("# MiMo Token Plan")
lines.append("XIAOMI_API_KEY=...")
lines.append("")
lines.append("# QQ Bot")
lines.append("QQ_APP_ID=1904159904")
lines.append("QQ_CLIENT_SECRET=...")
lines.append("QQ_ALLOW_ALL_USERS=true")
lines.append("")
lines.append("# FRED API")
lines.append("FRED_API_KEY=...")
lines.append("")
lines.append("# Email (QQ邮箱)")
lines.append("EMAIL_USER=452731778@qq.com")
lines.append("EMAIL_PASS=...")
lines.append("EMAIL_TO=452731778@qq.com")
lines.append("EMAIL_HOST=smtp.qq.com")
lines.append("EMAIL_PORT=465")

with open("tmp_env_clean", "w") as f:
    f.write("\n".join(lines) + "\n")
```

Then transfer:
```bash
scp -P 58234 -i C:\Users\Administrator\.ssh\id_rsa tmp_env_clean root@45.77.126.71:/root/hermes-pipeline/.env
```

## Python Heredoc (Second-Best)
```bash
ssh root@vps 'python3 << '\''PYEOF'\''
key = "40fa26cf844e61f5be94820c5ded91b2"
with open("/root/hermes-pipeline/.env", "w") as f:
    f.write("FRED_API_KEY=" + key + "\n")
PYEOF'
```

## Never Do This
- `echo "FRED_API_KEY=*** >> /root/hermes-pipeline/.env` via SSH — **will truncate or fail**
- `sed -i "/OLD/d; /$KEY/a NEW=$KEY" .env` — **near-guaranteed corruption**
- Multiple sequential `echo >>` calls to the same `.env` — **accumulates garbage**