# Hermes 配置文件位置问题

## 问题描述

当 `HERMES_HOME` 环境变量设置后，Hermes 会从该目录读取配置，而不是默认的 `~/.hermes/`。

## 关键路径

| 场景 | config.yaml 路径 | .env 路径 |
|------|-----------------|-----------|
| HERMES_HOME 未设置 | `~/.hermes/config.yaml` | `~/.hermes/.env` |
| HERMES_HOME=/root/hermes-pipeline | `/root/hermes-pipeline/config.yaml` | `/root/hermes-pipeline/.env` |

## 诊断命令

```bash
# 检查 Hermes 实际读取的路径
hermes config 2>&1 | grep -A 3 "Paths"

# 输出示例：
# ◆ Paths
#   Config:       /root/hermes-pipeline/config.yaml
#   Secrets:      /root/hermes-pipeline/.env
#   Install:      /usr/local/lib/hermes-agent
```

## 常见问题

### 1. API Key 报错 "Invalid API Key"

**症状：** `HTTP 401: Invalid API Key`

**原因：** .env 文件放错位置了。Hermes 读的是 `HERMES_HOME/.env`，不是 `~/.hermes/.env`。

**解决：**
```bash
# 检查实际读取路径
hermes config | grep "Secrets"

# 如果路径不对，同步 .env 到正确位置
cp ~/.hermes/.env /root/hermes-pipeline/.env
```

### 2. QQ Bot 配置不生效

**症状：** `No messaging platforms enabled`

**原因：** config.yaml 放错位置了。

**解决：**
```bash
# 检查实际读取路径
hermes config | grep "Config"

# 确保 platforms 配置在正确的 config.yaml 中
cat /root/hermes-pipeline/config.yaml | grep -A 10 "platforms:"
```

### 3. 环境变量冲突

**症状：** 网关尝试连接错误的平台（如 Yuanbao 而不是 QQ Bot）

**原因：** .env 或 shell 环境中有其他平台的配置（如 YUANBAO_APP_ID）

**解决：**
```bash
# 检查环境变量
env | grep -i "yuanbao\|元宝"

# 移除冲突配置
sed -i "/YUANBAO/d" /root/hermes-pipeline/.env
```

## 最佳实践

1. **统一使用 HERMES_HOME**：在 `.bashrc` 和 `/etc/environment` 中设置
2. **检查路径**：每次配置前先运行 `hermes config | grep Paths`
3. **备份配置**：修改前先 `cp config.yaml config.yaml.bak`
4. **验证生效**：修改后重启网关并检查日志

## VPS 特定配置

```bash
# /root/.bashrc 或 /etc/environment
export HERMES_HOME=/root/hermes-pipeline

# 验证
echo $HERMES_HOME
hermes config | grep "Config"
```
