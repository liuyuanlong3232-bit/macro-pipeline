# VPS配置陷阱汇总

## 1. SSH密钥不是id_ed25519

**症状：** `ssh -p 58234 -i /d/hermes-ssh/id_ed25519 root@45.77.126.71` 超时
**原因：** VPS重装后，SSH密钥变为 `~/.ssh/id_rsa`，不是自定义的 `id_ed25519`
**解决：** 使用 `ssh -p 58234 -i C:\Users\Administrator\.ssh\id_rsa root@45.77.126.71`
**验证：** `ssh -o ConnectTimeout=5 myvps "echo ok"`

### SSH别名配置
```bash
# ~/.ssh/config
Host myvps
    HostName 45.77.126.71
    User root
    Port 58234
    IdentityFile C:\Users\Administrator\.ssh\id_rsa

Host vps
    HostName 45.77.126.71
    Port 58234
    User root
    IdentityFile /d/hermes-ssh/id_ed25519  # ❌ 这个不对
```

## 2. HERMES_HOME路径映射

**症状：** API Key报错 "401 Invalid API Key" 或 ".env 加载不到"
**原因：** VPS上 `HERMES_HOME=/root/hermes-pipeline`，而 `/root/.hermes/` 也有一个 config.yaml，但Hermes读的是前者

**关键文件位置：**
| 文件 | 正确路径 |
|------|---------|
| config.yaml | `/root/hermes-pipeline/config.yaml` |
| .env | `/root/hermes-pipeline/.env` |
| state.db | `/root/hermes-pipeline/state.db` |
| SOUL.md | `/root/.hermes/SOUL.md` |
| skills | `/root/hermes-pipeline/skills/` |
| 系统config.yaml | `/root/.hermes/config.yaml`（**不读这个！**） |

**检查当前配置：**
```bash
hermes config            # 看 Paths 段的 Config 指向哪里
hermes config env-path   # 看 .env 路径
```

## 3. VPS时区

**症状：** cron任务在错误时间运行
**原因：** VPS默认Etc/UTC，用户在中国（UTC+8）
**解决：** `timedatectl set-timezone Asia/Shanghai`
**验证：** `date` 显示 CST (+0800)

## 4. cron任务时间必须匹配数据源发布时间

| 数据源 | 发布时间（北京） | 采集时间 |
|--------|----------------|---------|
| EIA | 周三22:30 | 周三23:00 |
| COT | 周五03:30 | 周五04:00 |
| FRED/Yahoo | 每日 | 每日08:00 |

**注意：** cron用的是系统时区。改时区后，cron任务时间也跟着变。

## 5. VPS.getenv不工作

**症状：** Python脚本中 `os.environ.get()` 返回 `None`
**原因：** SSH会话不会自动加载 `.bashrc`（非交互式shell）
**解决：** 

```bash
# 方法1：export后再运行
export HERMES_HOME=/root/hermes-pipeline
python3 script.py

# 方法2：写.env文件，用python-dotenv加载（推荐）
```

## 6. QQ Bot配置位置

**症状：** "No messaging platforms enabled"
**原因：** QQ Bot配置写在了 `/root/.hermes/config.yaml`，但网关读的是 `/root/hermes-pipeline/config.yaml`

**解决：** 确保配置在 `$HERMES_HOME/config.yaml` 下

## 7. skills目录

**症状：** `/skill xxx` 显示 "not found"
**原因：** 技能放在 `/root/.hermes/skills/` 不会被扫描到，需要放在 `/root/hermes-pipeline/skills/`
**解决：** `mv /root/.hermes/skills/xxx /root/hermes-pipeline/skills/`
