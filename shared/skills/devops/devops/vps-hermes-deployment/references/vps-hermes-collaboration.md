# VPS Hermes Collaboration Pattern

## The Discovery (2026-06-15)

VPS Hermes can **diagnose** problems but cannot **fix** them alone:

```
User ←→ Local Hermes (chat, decisions)
           │
           ├─ SSH root → VPS system (fix cron, edit .env, restart services)
           │
           └─ hermes chat -q → VPS Hermes (diagnose, analyze, report)
```

## VPS Hermes Capabilities

| Can Do | Cannot Do |
|--------|-----------|
| ✅ Check cron syntax | ❌ Write to `/etc/cron.d/` |
| ✅ Read log files | ❌ Read `.env` (credential protection) |
| ✅ Diagnose missing email config | ❌ Modify system files |
| ✅ Verify .env variables exist | ❌ Run unapproved terminal commands |
| ✅ Analyze report quality | ❌ Self-heal without user approval |

## VPS Hermes Blocked By

1. **Security policy**: `patch` tool refuses `/etc/cron.d/hermes-reports`
2. **Credential guard**: `read_file` refuses `.env`
3. **User approval**: `terminal` blocked without explicit consent
4. **SELinux/AppArmor**: system-level file protection

## Effective Workflow

1. VPS Hermes discovers problem → reports to user
2. User tells local Hermes: "VPS Hermes says cron has syntax error"
3. Local Hermes SSHs to VPS → fixes it with root access
4. Local Hermes reports back to user: "Fixed, verified"

## Why This Works

- VPS Hermes has full context of VPS state (logs, config, data)
- Local Hermes has root SSH access (can fix anything)
- User stays in control (approves changes)

## Anti-Patterns

- ❌ Letting VPS Hermes try to fix system files (it can't)
- ❌ Running `hermes chat -q` for simple commands (use direct SSH)
- ❌ Duplicating work: if local Hermes can fix it directly via SSH, do that
- ✅ Use VPS Hermes for diagnosis, local Hermes for execution
