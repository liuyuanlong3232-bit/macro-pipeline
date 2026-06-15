# Deploying to a Linux VPS

After building the pipeline locally on Windows, here's how to migrate it to an Ubuntu VPS (e.g. Vultr, DigitalOcean, Linode).

## Prerequisites on VPS

- Ubuntu 22.04+ with Python 3.11+
- `pip3 install requests pandas python-dotenv`
- Hermes Agent installed (`curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash`)

## Transfer Pipeline

```bash
# From local terminal:
scp macro_pipeline.py generate_report.py user@vps:~/macro-pipeline/
scp .env user@vps:~/macro-pipeline/.env  # API keys
```

### From Windows PowerShell

```powershell
scp -i ~/.ssh/vultr_key .\macro_pipeline.py user@IP:~/macro-pipeline/
```

### Creating .env on VPS (if not transferring)

Do NOT use shell heredocs for API keys — they get truncated. Use a small Python script:

```bash
cd ~/macro-pipeline
python3 -c "
with open('.env', 'w') as f:
    f.write('FRED_API_KEY=your_full_key_here\n')
    f.write('ALPHA_VANTAGE_API_KEY=your_full_key_here\n')
"

## Cron on VPS

On the VPS, Hermes built-in cron (via `hermes cron`) runs when the gateway is active. Or use system cron directly:

```bash
crontab -e
# Add lines:
0 8 * * * cd ~/macro-pipeline && python3 macro_pipeline.py >> ~/hermes-macro-data/logs/cron.log 2>&1
0 9 * * * cd ~/macro-pipeline && python3 generate_report.py >> ~/hermes-macro-data/logs/report.log 2>&1
```

## Systemd Service for Persistence

Create `/etc/systemd/system/hermes-gateway.service`:

```ini
[Unit]
Description=Hermes Agent Gateway
After=network.target

[Service]
Type=simple
User=hermes
ExecStart=/home/hermes/.local/bin/hermes gateway run
Restart=always
RestartSec=10
Environment=HERMES_HOME=/home/hermes/.hermes

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now hermes-gateway
```

## Path Difference: Windows → Linux

| Windows | Linux | Note |
|---------|-------|------|
| `C:\Users\Admin\AppData\Local\hermes\.env` | `~/.hermes/.env` | Same path when HERMES_HOME is default |
| `C:\Users\Admin\hermes-macro-pipeline\` | `~/macro-pipeline/` | Pipeline scripts |
| `C:\Users\Admin\hermes-macro-data\` | `~/hermes-macro-data/` | Data output |

The pipeline script auto-detects `HERMES_HOME` env var and falls back to `~/.hermes/`.

## Verification

```bash
cd ~/macro-pipeline
python3 macro_pipeline.py     # Full data collection
python3 generate_report.py    # Generate today's report
cat ~/hermes-macro-data/reports/*.md
```

## VPS Security Hardening (Before Deploying)

New VPS instances — especially $5 tier — often ship with root password SSH open. Harden before exposing anything:

### 1. Create a non-root user

```bash
adduser hermes           # Set password, then:
usermod -aG sudo hermes
su - hermes               # Test it works
```

### 2. SSH key authentication only

```powershell
# From local Windows PowerShell:
ssh-keygen -t ed25519 -f ~/.ssh/vultr_key
type C:\Users\You\.ssh\vultr_key.pub | ssh root@IP "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

```bash
# Then on VPS, disable password + root login:
sudo sed -i 's/^#*PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/^PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

### 3. Firewall

```bash
sudo ufw allow 22/tcp    # SSH only — unless you also serve web
sudo ufw --force enable
```

### 4. Fail2ban (anti-brute-force)

```bash
sudo apt install fail2ban -y
sudo systemctl enable --now fail2ban
```
