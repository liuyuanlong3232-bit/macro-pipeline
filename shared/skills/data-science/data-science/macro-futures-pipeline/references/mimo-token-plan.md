# MiMo Token Plan 配置

## 套餐信息
- **套餐**: Lite ¥39/月（41亿 Credits）
- **Base URL**: `https://token-plan-cn.xiaomimimo.com/v1`
- **模型**: `xiaomi/mimo-v2.5-pro`
- **夜间优惠**: 0:00-8:00 消耗打8折

## Hermes配置
```yaml
# ~/.hermes/config.yaml
model:
  default: xiaomi/mimo-v2.5-pro
  provider: xiaomi
  base_url: https://token-plan-cn.xiaomimimo.com/v1
```

## .env配置
```
XIAOMI_API_KEY=tp-xxxxx
```

**注意：** VPS上Hermes读的.env路径是 `/root/hermes-pipeline/.env`，不是 `/root/.hermes/.env`。

## 切换模型
```bash
hermes config set model.default xiaomi/mimo-v2.5-pro
hermes config set model.provider xiaomi
hermes config set model.base_url https://token-plan-cn.xiaomimimo.com/v1
```

## SSH别名配置
在本地 `~/.ssh/config` 里添加：
```
Host vps
    HostName 45.77.126.71
    Port 58234
    User root
    IdentityFile C:\Users\Administrator\.ssh\id_rsa
```

以后直接 `ssh vps` 就能连上。

## ⚠️ 新会话才生效
模型切换后需要**新开会话**，当前会话不会变。
