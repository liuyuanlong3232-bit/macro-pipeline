# GitHub Sync Workflow for VPS Pipeline

## Architecture

```
Local PC (git-bash) → GitHub → VPS (git pull)
```

Two key files:
- **`.gitignore`**: excludes `.env`, `.ghtoken`, `__pycache__/`, `*.pyc`
- **`sync_to_vps.sh`**: one-command deploy script (see below)

## Setup (One-Time)

### 1. Create GitHub Repo

```python
# From local PC (with proxy):
import requests
token = "ghp_your_token_here"
r = requests.post("https://api.github.com/user/repos",
    headers={"Authorization": f"token {token}"},
    json={"name": "macro-pipeline", "private": False})
# → https://github.com/YOUR_USER/macro-pipeline
```

### 2. Initialize Local Repo

```bash
cd ~/hermes-macro-pipeline
git init
git add macro_pipeline.py metals_weekly.py energy_weekly.py ... # core scripts
git commit -m "initial commit"
git remote add origin https://YOUR_TOKEN@github.com/YOUR_USER/macro-pipeline.git
git push -u origin main
```

**Pitfall:** GitHub is blocked from China. Use `git config http.proxy http://127.0.0.1:10808` before pushing. Unset after with `git config --unset http.proxy`.

### 3. Clone on VPS

```bash
mv /root/hermes-pipeline /root/hermes-pipeline.bak  # backup
git clone https://github.com/YOUR_USER/macro-pipeline.git /root/hermes-pipeline
cp /root/hermes-pipeline.bak/.env /root/hermes-pipeline/  # restore secrets
```

Use a `.git-credentials` file on VPS so pull doesn't ask for auth:
```bash
git config --global credential.helper "store --file ~/.git-credentials"
echo "https://YOUR_TOKEN:@github.com" > ~/.git-credentials
```

### 4. Daily Sync Script (`sync_to_vps.sh`)

```bash
#!/bin/bash
set -e
echo "=== 1. Local commit ==="
cd "$(dirname "$0")"
git add -A
git commit -m "$(date '+%Y-%m-%d %H:%M') update" || echo "Nothing changed"
git push

echo "=== 2. VPS pull ==="
ssh -p PORT -i /d/hermes-ssh/id_ed25519 root@VPS_IP '
cd /root/hermes-pipeline
git pull
echo "VPS synced"
'

echo "=== Done ==="
```

## Security Notes

- **Token in URL**: `https://TOKEN@github.com/...` — the token is embedded in the remote URL. Anyone with access to `.git/config` sees it.
- **`.ghtoken` file**: Create a file containing only the raw token for use in scripts. Add to `.gitignore` immediately.
- **SSH key on D:\**: Store `id_ed25519` on `D:\hermes-ssh\` so it survives Windows reinstall. Reference in `~/.ssh/config` as `/d/hermes-ssh/id_ed25519`.
