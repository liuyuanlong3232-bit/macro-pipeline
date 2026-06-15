# MiMo Token Plan — Hermes 配置指南

> 2026-06-13 创建
> 来源：platform.xiaomimimo.com 官方文档

## 套餐概览

| 套餐 | 月费 | Credits/月 | 适合场景 |
|------|------|-----------|---------|
| **Lite** | ¥39 | 41亿 | 轻度使用 |
| **Standard** | ¥99 | 110亿 | 日常开发 |
| **Pro** | ¥329 | 380亿 | 专业高频 |
| **Max** | ¥659 | 820亿 | 重度依赖 |

- 夜间（0:00-8:00 北京时间）消耗打8折
- 首购88折，新用户首开自动续费77折
- 包年再省12%

## Hermes 配置

### 1. 订阅获取 API Key

订阅后在「订阅管理」页获取：
- **API Key**：格式 `tp-xxxxx`（不是普通的 API Key）
- **Base URL**：根据区域选择

### 2. .env 配置

```bash
# MiMo Token Plan
XIAOMI_API_KEY=tp-xxxxx
XIAOMI_BASE_URL=https://token-plan-cn.xiaomimimo.com/v1
```

区域 Base URL：
- 中国：`https://token-plan-cn.xiaomimimo.com/v1`
- 新加坡：`https://token-plan-sgp.xiaomimimo.com/v1`
- 欧洲：`https://token-plan-ams.xiaomimimo.com/v1`

### 3. config.yaml 配置

```yaml
model:
  default: xiaomi/mimo-v2.5-pro
  provider: xiaomi
  base_url: https://token-plan-cn.xiaomimimo.com/v1
```

### 4. 切换模型

```bash
hermes config set model.provider xiaomi
hermes config set model.default xiaomi/mimo-v2.5-pro
hermes config set model.base_url https://token-plan-cn.xiaomimimo.com/v1
```

### 5. 生效方式

**必须重启 Hermes Desktop**。`/reset` 不会切换模型，只清除对话历史。

## 支持的模型

Token Plan 支持全部8款 MiMo 模型：
- `mimo-v2.5-pro` — 旗舰推理，1M上下文
- `mimo-v2.5` — 全模态理解
- `mimo-v2-flash` — 轻量快速
- TTS 系列（4款）— 语音合成

## 对比 DeepSeek

| 对比 | DeepSeek V4 Flash | DeepSeek V4 Pro | MiMo 2.5 Pro |
|------|------------------|----------------|-------------|
| Input/M tokens | $0.14 | $0.435 | $0.435 |
| Output/M tokens | $0.28 | $0.87 | $0.87 |
| Intelligence | 57 | ~51 | **86** |
| Agentic | 49.1 | — | **68.4** |
| 缓存命中/M | — | $0.0036 | $0.0036 |

MiMo 2.5 Pro 和 DeepSeek V4 Pro 同价但更聪明。

## 常见问题

### Q: 为什么切换模型后没生效？
A: `/reset` 只清除对话历史，不切换模型。需要重启 Hermes Desktop。

### Q: Token Plan 的 Credits 怎么计算？
A: Credits 是 MiMo 平台的计量单位，与 token 的换算取决于模型类型。MiMo 2.5 Pro 按量计费约 ¥21/1M tokens 输出。

### Q: 能同时用 DeepSeek 和 MiMo 吗？
A: 可以。Hermes 的 `providers` 配置支持多 provider。但默认模型只有一个，切换需要改 config 或用 `hermes model` 命令。
