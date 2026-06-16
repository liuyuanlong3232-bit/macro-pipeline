# Hermes Macro Data Orchestrator — 三模式运维规范

> 2026-06-16 老大提供

## 核心原则

DEV不会污染PROD，TEST不会触发PROD降级，PROD永远是稳定唯一真源。

---

## 一、三种模式

### 🟢 DEV（开发模式）

- 用途：新数据源接入、代码逻辑验证、API结构测试
- 允许：mock数据、低质量数据
- 禁止：高频请求、全量pipeline运行
- 限制：≤5 requests/session，手动触发，单模块执行
- 目标：验证逻辑，不追求稳定性

### 🟡 TEST（测试模式）

- 用途：验证完整流程、小规模真实数据拉取、风控行为验证
- 规则：使用真实数据源，限制请求规模，启用风控检测（不启用自动修复）
- 限制：≤10~20 requests/batch，分批执行，batch间间隔≥5~15分钟
- 允许：jitter、分源测试
- 禁止：全量数据运行、高频循环测试
- 目标：验证系统稳定性

### 🔴 PROD（生产模式）

- 用途：正式每日运行、自动调度、数据输出
- 规则：完整pipeline运行，启用所有风控模块（rate limit/jitter/fallback/健康评分）
- 限制：严格限速（≤6 req/min/domain），分批执行，随机时间窗口（07:40–08:40）
- 目标：长期稳定运行

---

## 二、模式切换规则

- 禁止自动切换模式
- DEV → TEST：手动确认
- TEST → PROD：必须通过稳定性验证（≥3次无异常运行）

---

## 三、全局风控规则（所有模式通用）

### 请求控制
- 必须使用jitter：sleep(1~5s)
- 禁止burst（集中请求）
- 禁止并发超过10个请求

### HTTP策略
- 429 → 指数退避
- 403/421 → 进入BLOCKED（仅当前源）
- 5xx → 重试≤3次

### User-Agent统一
```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36
```

---

## 四、系统行为隔离

- DEV请求不计入风控评分
- TEST只影响局部数据源评分
- PROD才影响全局health_score

---

## 五、日志隔离

### DEV日志
- debug log
- mock log

### TEST日志
- test_run.log
- partial_data.log

### PROD日志
- production.log
- system_health.log

---

## 六、稳定性原则

优先级：PROD稳定性（最高）> TEST正确性 > DEV灵活性

---

## 七、实现清单

### 需要新增的文件

| 文件 | 用途 |
|------|------|
| `shared/orchestrator.py` | 风控调度器（已有，需扩展三模式） |
| `shared/mode.py` | 模式管理（DEV/TEST/PROD） |
| `config/mode.json` | 当前模式配置 |

### 需要修改的文件

| 文件 | 改动 |
|------|------|
| `macro_pipeline.py` | 集成模式检查+风控规则 |
| `daily_collect.py` | 根据模式调整行为 |
| `daily_report.py` | 根据模式调整行为 |

### 需要新增的日志目录

```
logs/
├── dev/
│   ├── debug.log
│   └── mock.log
├── test/
│   ├── test_run.log
│   └── partial_data.log
└── prod/
    ├── production.log
    └── system_health.log
```
