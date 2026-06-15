# VPS Deployment for Hermes + Ecosystem Tools

Migrating from local Windows desktop to an Ubuntu VPS (e.g. Vultr $5/mo tier).

## Target Spec Validated

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 1 vCPU | 2 vCPU |
| RAM | 1 GB | 2 GB |
| Storage | 25 GB | 50 GB |
| OS | Ubuntu 22.04 | Ubuntu 24.04 |

1vCPU/1GB/25GB is sufficient for: Hermes CLI + cron scheduler + data pipeline Python scripts + daily report generation.

## Security Hardening (9 Steps)

Run these in order on a fresh Ubuntu 22.04 VPS:

### Step 1-3: User + SSH lockdown

```bash
# Create non-root user
adduser hermes
usermod -aG sudo hermes

# On LOCAL machine, upload public key:
ssh-copy-id -i ~/.ssh/your_key hermes@<VPS_IP>

# On VPS, disable password + root login:
sudo sed -i 's/^PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/^PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

### Step 4-5: Firewall + fail2ban

```bash
sudo ufw allow 22/tcp
sudo ufw --force enable

sudo apt install fail2ban -y
sudo systemctl enable --now fail2ban

# Optional: allow HTTP/HTTPS if serving a web UI
# sudo ufw allow 80/tcp; sudo ufw allow 443/tcp
```

### Step 6: Install Hermes

```bash
su - hermes
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
source ~/.bashrc
pip3 install requests pandas python-dotenv
```

### Step 7: Transfer pipeline files

```bash
# From LOCAL PowerShell:
scp -i ~/.ssh/your_key ~/hermes-deploy/pipeline/*.py hermes@<VPS_IP>:~/macro-pipeline/
scp -i ~/.ssh/your_key ~/hermes-deploy/install_on_vps.sh hermes@<VPS_IP>:~/
```

### Step 8: Systemd service for Hermes gateway

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

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now hermes-gateway
```

### Step 9: Cron jobs

On the VPS, the Hermes-built-in cron works when the gateway is running (`hermes cron list`). Alternatively use system cron for simplicity:

```bash
crontab -e
# Add:
0 8 * * * cd ~/macro-pipeline && python3 macro_pipeline.py >> ~/hermes-macro-data/logs/cron.log 2>&1
0 9 * * * cd ~/macro-pipeline && python3 generate_report.py >> ~/hermes-macro-data/logs/report.log 2>&1
```

## GBrain on VPS

GBrain (PGLite mode) can run on 1GB RAM but it's **tight** (~300-400MB for bun + PGLite). Steps:

```bash
# Install bun (official installer)
curl -fsSL https://bun.sh/install | bash
source ~/.bashrc

# Install gbrain
bun install -g github:garrytan/gbrain

# Initialize (PGLite, defer embedding)
# On Linux, the compiled binary works — no PATH workaround needed
gbrain init --pglite --no-embedding

# Verify
gbrain doctor
```

## Email Delivery Setup

Once the VPS runs 24/7, configure SMTP in `$HERMES_HOME/.env` so the daily report auto-delivers:

```env
EMAIL_ADDRESS=your@email.com
EMAIL_PASSWORD=app_password
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
```

Then set a cron to email the report:

```bash
0 9 * * * cat ~/hermes-macro-data/reports/$(date +\%Y-\%m-\%d).md | mail -s "Daily Macro Report" your@email.com
```

## Verification Checklist

- [ ] Hermes CLI responds: `hermes --version`
- [ ] Gateway starts: `hermes gateway run` (test foreground first)
- [ ] Pipeline runs: `cd ~/macro-pipeline && python3 macro_pipeline.py`
- [ ] Report generates: `python3 generate_report.py`
- [ ] Cron fires: check `~/hermes-macro-data/logs/cron.log`
- [ ] SSH key-only: test disconnect/reconnect
- [ ] Firewall only: `sudo ufw status` shows port 22 only
- [ ] GBrain (if installed): `gbrain doctor` passes
