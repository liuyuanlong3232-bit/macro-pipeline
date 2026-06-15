# QQ Bot配置格式（已验证通过）

## 正确配置格式（已测试可用）

### config.yaml
```yaml
platforms:
  qq:                        # ❗ 平台名是 qq 不是 qqbot
    enabled: true
    extra:
      app_id: "1904159904"
      client_secret: "IVUFl25tTovnQoGV"  # ❗ 字段名是 client_secret 不是 secret
      markdown_support: true
      dm_policy: "open"
      group_policy: "open"
```

### .env 文件
```
QQ_APP_ID=1904159904
QQ_CLIENT_SECRET=IVUFl2...GV
QQ_ALLOW_ALL_USERS=true
GATEWAY_ALLOW_ALL_USERS=true
```

## 错误格式（不生效）

### ❌ 错误1：平台名不对
```yaml
platforms:
  qqbot:       # ❌ 应为 qq
```

### ❌ 错误2：字段名不对
```yaml
secret: "..."  # ❌ 应为 client_secret
```

### ❌ 错误3：配置在错误位置
`/root/.hermes/config.yaml` 是系统默认路径，但 **VPS上 HERMES_HOME 指向 `/root/hermes-pipeline/`**，所以配置必须写在 `/root/hermes-pipeline/config.yaml`。

## 网关启动日志验证
成功连接后，日志应显示：
```
Connecting to qqbot...
[QQBot:1904159904] Access token refreshed
[QQBot:1904159904] WebSocket connected
[QQBot:1904159904] Connected
[QQBot:1904159904] Identify sent
✓ qqbot connected
Gateway running with 1 platform(s)
```

## 网关启动命令
```bash
# 启动（前台）
hermes gateway run

# 启动（后台）
nohup hermes gateway > /tmp/hermes_gateway.log 2>&1 &

# 检查状态
hermes gateway status

# 查看日志
tail -f /root/hermes-pipeline/logs/gateway.log
```

## 常见问题
1. **"No messaging platforms enabled"** → 检查config.yaml格式是否正确
2. **"invalid appid or secret"** → 重新从q.qq.com复制凭证
3. **"yuanbao failed to connect"** → 清除YUANBAO环境变量（`unset YUANBAO_APP_ID`）
4. **网关不读config.yaml** → 检查 `HERMES_HOME` 指向的路径，配置必须在其下
5. **配置了两个.env文件要考虑是哪个** → VPS上 `.env` 在 `/root/hermes-pipeline/.env`，不是 `/root/.hermes/.env`
