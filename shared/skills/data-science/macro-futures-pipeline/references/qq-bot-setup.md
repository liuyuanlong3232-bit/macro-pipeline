# QQ Bot 配置指南

## 为什么用QQ Bot

用户手机无法使用Telegram（国内被墙，注册需要会员才能收验证码）。
QQ Bot使用官方API，安全不封号，用户已有QQ号。

## 注册流程

1. 打开 https://q.qq.com
2. 扫码登录（用现有QQ号）
3. 点"创建机器人"
4. 填写名称（如"Hermes助手"）
5. 创建成功后复制 **AppID** 和 **AppSecret**

## 配置到VPS Hermes

### 方法1: 交互式配置（推荐）

```bash
# SSH到VPS
ssh vps

# 运行gateway setup
hermes gateway setup

# 选择 QQ Bot（第15项）
# 填入 AppID 和 AppSecret
```

### 方法2: 手动配置

**config.yaml 格式（关键！）：**

```yaml
# /root/hermes-pipeline/config.yaml (当 HERMES_HOME=/root/hermes-pipeline)
platforms:
  qq:                                    # 注意：是 qq，不是 qqbot
    enabled: true
    extra:                               # 注意：凭证在 extra 下
      app_id: "1904159904"               # 你的 AppID
      client_secret: "IVUFl25tTovnQoGV"  # 你的 AppSecret
      markdown_support: true
      dm_policy: "open"                  # 私聊策略：open/allowlist/disabled
      group_policy: "open"               # 群聊策略：open/allowlist/disabled
```

**⚠️ 常见错误格式（不要用）：**
```yaml
# ❌ 错误：platform 名是 qqbot 而不是 qq
platforms:
  qqbot:
    enabled: true
    app_id: "..."
    secret: "..."  # ❌ 错误：应该是 client_secret
```

**.env 格式：**
```bash
# /root/hermes-pipeline/.env
QQ_APP_ID=1904159904
QQ_CLIENT_SECRET=IVUFl25tTovnQoGV
QQ_ALLOW_ALL_USERS=true
```

### 依赖安装

```bash
pip install aiohttp httpx
```

### 验证连接

```bash
# 测试 AppID/Secret 是否有效
python3 -c "
import asyncio, aiohttp
async def test():
    async with aiohttp.ClientSession() as s:
        async with s.post('https://bots.qq.com/app/getAppAccessToken',
            json={'appId': 'YOUR_APP_ID', 'clientSecret': 'YOUR_SECRET'}) as r:
            print(await r.json())
asyncio.run(test())
"
```

### 启动网关

```bash
# 后台启动
nohup hermes gateway > /tmp/hermes_gateway.log 2>&1 &

# 检查状态
hermes gateway status

# 查看日志
tail -20 /tmp/hermes_gateway.log
```

### 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `invalid appid or secret` | AppID或AppSecret错误 | 检查QQ开放平台的"开发设置"页面 |
| `No messaging platforms enabled` | config.yaml格式错误 | 检查platforms.qq.extra格式 |
| Yuanbao连接失败 | 环境变量冲突 | 移除.env中的YUANBAO_*配置 |
| `python-dotenv could not parse` | .env文件格式错误 | 检查引号和特殊字符 |

## 限制说明

| 类型 | 限制 | 影响 |
|------|------|------|
| 主动消息（Bot主动发） | 每月4条/用户 | 定时报告用邮箱替代 |
| 被动消息（用户问Bot答） | 无限制 | 日常对话完全够用 |
| Markdown | 支持 | 报告格式没问题 |
| 图片 | 支持 | 图表可以发 |
| 文件 | 单聊支持 | PNG长图可以发 |

## VPS部署要求

- 公开IP：45.77.126.71（已有）
- IP白名单：在QQ开放平台配置
- 域名+SSL：Webhook方式可能需要（可用免费域名）

## 安全性

- 官方API，不是外挂
- 不会封号
- 不需要小号，直接用现有QQ号
- 美国VPS没问题，API只认IP不认地区

## 替代方案

如果QQ Bot配置复杂，可以继续用：
- QQ邮箱发报告（已在用）
- VPS上的 `hermes chat`（SSH直接对话）
