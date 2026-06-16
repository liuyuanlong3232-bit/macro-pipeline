# Hermes Macro Data Orchestrator 规范

> 2026-06-16 老大提供

## 核心目标

不是最快获取数据，而是**长期稳定运行，不触发风控**。

---

## 数据源范围

### 合规公开数据源

| 数据源 | 类型 | 需要Key |
|--------|------|:--:|
| CFTC | TXT / ZIP / HTML | ❌ |
| USDA | PDF / HTML / TXT | 部分 |
| EIA | API | ✅ |
| FRED | API | ✅ |
| Yahoo Finance | 公共数据 | ❌ |
| 和风天气 | API | ✅ |
| Tushare | API | ✅ |

### 禁止访问

- OpenAI / ChatGPT / Codex
- 登录态网站绕过访问
- 非公开接口探测
- 高频扫描行为

---

## 风控状态识别

### 🟢 NORMAL（正常）

- HTTP 200
- 无延迟增长
- 无429/403

### 🟡 THROTTLED（限流）

- HTTP 429
- 响应变慢
- 返回空数据/部分数据

### 🔴 BLOCKED（风控/降权）

- HTTP 403 / 421
- Cloudflare challenge
- cf-ray异常变化
- Cookie/JS challenge出现

---

## 自动调度策略

### 🟢 NORMAL 状态

- 按标准节奏执行
- 批次：5~10个请求
- 间隔：1~3秒 jitter

### 🟡 THROTTLED 状态

自动进入"降速模式"：

- 请求间隔 ×2~3
- 批次减半（10 → 5）
- 单域名冷却 5~15分钟

冷却规则：
```
触发429 → 同源暂停300~900秒
```

### 🔴 BLOCKED 状态

- 立即停止该源所有请求
- 标记为不可用
- 等待人工确认后恢复
- 通知用户

---

## 实现要求

### 每次请求必须记录

- 时间戳
- 目标URL
- HTTP状态码
- 响应时间
- 数据量
- 当前状态（NORMAL/THROTTLED/BLOCKED）

### 状态转换必须日志化

```
2026-06-16 08:00:01 FRED NORMAL → NORMAL (200, 0.3s, 377行)
2026-06-16 08:00:03 Yahoo THROTTLED → NORMAL (200, 1.2s, 16行)
2026-06-16 08:00:05 CFTC NORMAL → BLOCKED (403, 0.1s, 0行)
```

### 调度器必须支持

- 手动暂停/恢复某个数据源
- 查看所有数据源当前状态
- 查看历史触发记录
- 配置冷却时间
