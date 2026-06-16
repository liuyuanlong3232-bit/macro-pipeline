# 项目全景文档（2026-06-16 最新版）

## 一、系统架构

### 分工

| 角色 | 硬件 | 定位 | 状态 |
|------|------|------|------|
| **本地 Hermes** | Windows 10 + RTX 4060 8GB | 主力交互、分析决策、代码开发 | ✅ 运行中 |
| **VPS** | Vultr 1vCPU/1GB/25GB Ubuntu 22.04 | 7×24 数据工厂、定时采集、邮件发送 | ✅ 运行中 |

### VPS Hermes 已停用

- 停用时间：2026-06-16
- 原因：用户觉得复杂没用，保留纯数据采集功能即可
- 保留：hermes.db + cron + scripts + 数据采集
- 去掉：AI 对话 + QQ Bot

---

## 二、数据源清单

### 已接入（8个）

| 数据源 | 内容 | 更新频率 | 免费额度 |
|--------|------|----------|----------|
| FRED | 31个宏观指标 | 每日 08:00 | 无限制（需Key） |
| Yahoo Finance | 16个国际期货 | 每日 08:00 | 免费 |
| Tushare | 5个中国期货（生猪/豆粕/玉米/大豆/淀粉） | 每日 08:04 | 2000积分免费 |
| 和风天气 | 9个中国城市天气 | 每日 08:03 | 50K次/月免费 |
| Open-Meteo | 6个全球农业产区天气 | 每日 08:05 | 10K次/天免费 |
| CFTC | 持仓数据（via cotdata.net） | 每周五 04:00 | 免费 |
| EIA | 能源库存 | 每周三 23:00 | 需Key |
| ICE | DXY美元指数 | 每日 08:00 | 免费 |

### 待接入

| 数据源 | 内容 | 优先级 |
|--------|------|--------|
| USDA NASS | 产量/面积 | 中 |
| CNGOIC | 中国压榨率 | 低 |
| CONAB | 巴西产量 | 低 |

---

## 三、数据库

### hermes.db（23MB）

| 表 | 行数 | 内容 |
|----|------|------|
| fred_indicators | 403 | FRED 宏观指标 |
| yahoo_futures | 17 | 国际期货行情 |
| cn_futures | 5 | 中国期货行情 |
| cn_weather | 36 | 中国城市天气 |
| agri_weather | 33K | 全球农业天气历史 |
| cotdata | — | CFTC 持仓 |
| eia_energy | 36 | 能源库存 |
| vix_data | 805 | VIX 恐慌指数 |
| price_* | 15万+ | 14品种历史价格 |

---

## 四、日报系统（ABCD 四区）

### 生成流程

```
cron 08:00 UTC → daily_collect.py（FRED+Yahoo）
cron 08:03 UTC → fetch_cn_weather.py（和风天气9城）
cron 08:04 UTC → fetch_cn_futures.py（Tushare中国期货）
cron 08:05 UTC → fetch_weather.py（Open-Meteo全球天气）
cron 08:10 UTC → quality_check.py（数据质检）
cron 08:30 UTC → daily_report.py（生成日报+发邮件）
```

### 日报结构

```
📊 全资产日报 · YYYY-MM-DD

A区 · 贵金属+宏观
  黄金 $xxxx | 白银 $xx.xx | DXY xx.xx
  10Y国债 x.xx% | TIPS x.xx%

B区 · 能源
  WTI $xx.xx | Brent $xx.xx | 天然气 $x.xx

C区 · 农业天气
  玉米 xxx¢ | 大豆 xxx¢ | 小麦 xxx¢
  6产区天气异常检测

D区 · 中国农业
  国内期货：生猪/豆粕/玉米/大豆/淀粉
  城市天气：哈尔滨/郑州/北京/济南/石家庄/呼和浩特/通辽/巴彦淖尔/呼伦贝尔

⚠️ 预警信号
📋 数据附表
```

---

## 五、Cron 配置

### 部署方式

- **文件**：`deploy/hermes-cron`（Git版本控制）
- **部署**：scp 到 VPS `/etc/cron.d/hermes-reports` + `crontab`
- **VPS 时区**：UTC（00:00 = 08:00 CST）

### 任务清单（15条）

| UTC时间 | CST时间 | 任务 |
|---------|---------|------|
| 00:00 | 08:00 | FRED+Yahoo 采集 |
| 00:03 | 08:03 | 和风天气 9 城 |
| 00:04 | 08:04 | Tushare 中国期货 |
| 00:05 | 08:05 | Open-Meteo 全球天气 |
| 00:10 | 08:10 | 数据质检 |
| 00:30 | 08:30 | **日报生成+邮件** |
| 08:00 Fri | 16:00 Fri | 周报摘要 |
| 22:00 Mon | 06:00 Tue | USDA 过期检查 |
| 15:00 Wed | 23:00 Wed | EIA 库存采集 |
| 20:00 Thu | 04:00 Fri | COT 持仓采集 |
| 20:00 daily | 04:00 daily | 记忆推送到 GitHub |
| 21:00 daily | 05:00 daily | Git 拉取+记忆导入 |
| 12:00 Sun | 20:00 Sun | 知识库自检提醒 |
| 01:00 15th | 09:00 15th | 月度里程碑检查 |
| 02:00 Wed/Fri | 10:00 Wed/Fri | 天气启动提醒 |

---

## 六、MCP 配置

### 已部署

| MCP | 引擎 | 费用 | 状态 |
|-----|------|------|------|
| OpenWebSearch | 百度/Bing/DuckDuckGo | $0 | ✅ 本地+VPS |

### 认证方式

- 和风天气：Header `X-QW-Api-Key` + Host `pg7dnaywrf.re.qweatherapi.com`
- FRED：`?api_key=`
- Tushare：Token in `.env`
- EIA：`?api_key=`

---

## 七、项目文件结构

```
D:\hermes\pipeline\                    ← 代码仓库（Git）
├── scripts/                           ← 19个活跃脚本
│   ├── daily_collect.py               ← FRED+Yahoo采集
│   ├── daily_report.py                ← 日报生成+邮件
│   ├── fetch_cn_weather.py            ← 和风天气9城
│   ├── fetch_cn_futures.py            ← Tushare中国期货
│   ├── fetch_weather.py               ← Open-Meteo全球天气
│   ├── quality_check.py               ← 数据质检
│   ├── weekly_summary.py              ← 周报摘要
│   ├── fix_eia_collect.py             ← EIA库存采集
│   ├── import_memory.py               ← 记忆导入
│   ├── import_usda.py                 ← USDA导入
│   ├── import_yahoo.py                ← Yahoo导入
│   ├── check_usda.py                  ← USDA过期检查
│   ├── reminder_monthly.py            ← 月度提醒
│   ├── reminder_weather.py            ← 天气提醒
│   ├── reminder_weekly.py             ← 知识库自检
│   ├── sync_memory.py                 ← 记忆同步
│   ├── sync_shared.py                 ← shared同步
│   ├── vps_memory_push.py             ← 记忆推GitHub
│   └── import_history.py              ← 历史导入
│
├── shared/                            ← Git同步
│   ├── utils.py                       ← 公共工具(load_csv/fetch_fedwatch)
│   ├── knowledge/                     ← 14个知识库文件
│   └── memories/                      ← 记忆同步
│
├── deploy/                            ← 部署配置
│   ├── hermes-cron                    ← cron定义文件
│   └── HERMES_RULES.md                ← 工作纪律
│
├── prompts/                           ← 4个提示词模板（不改）
├── macro_pipeline.py                  ← 核心采集引擎
├── send_email.py                      ← 邮件发送模块
├── monitor.py                         ← 价格预警
└── *.py                               ← 22个旧文件（备用）

C:\Users\Administrator\.hermes\         ← 本地Hermes
├── plans/                             ← 29个计划文档
├── knowledge/                         ← 知识库
├── config.yaml                        ← 配置（含MCP）
└── skills/                            ← 92个技能

VPS /root/hermes-pipeline/             ← VPS项目（Git同步）
├── scripts/                           ← 19个脚本（与本地一致）
├── .env                               ← API密钥
└── config.yaml                        ← MCP配置

VPS /root/hermes-macro-data/           ← VPS数据仓库
├── hermes.db                          ← 23MB SQLite
├── reports/                           ← 日报/周报
├── signals/                           ← 每日信号
├── csv/                               ← 每日原始CSV
└── charts/                            ← 图表PNG
```

---

## 八、农业项目

### 当前状态

| 阶段 | 状态 |
|------|------|
| 底层数据基建 | ✅ 完成 |
| ABCD日报系统 | ✅ 运行中 |
| 稳定观察期 | 🔄 6/16 ~ 6/20 |
| 农业报告开发 | ⏸️ 等稳定后启动 |
| 产品孵化 | 📝 方案已完成（见agri-data-plan-complete.md） |

### 产品孵化三方案

| 优先级 | 产品 | 周期 | 技术依赖 |
|--------|------|------|----------|
| 🥇 | 农产品价格参照助手 | 1-2周 | cn_futures + 5年百分位算法 |
| 🥈 | 区域性病害风险预警 | 3-4周 | 和风天气 + 病害规则库 |
| 🥉 | 农学论文速读助手 | 1-2周 | 4060跑8B RAG |

---

## 九、工作纪律

### 铁律

1. 禁止私自写 Python 代码
2. 执行前必须：查skills → 查plugins/tools → 缺啥装啥 → 写代码前请示同意
3. 常用代码封装为 skill
4. 定期清理无效代码碎片

### 代码修改流程

```
本地改 → VPS测试 → 推Git
```

### 不允许

- 直接在VPS改代码
- 没测试就推Git
- 跳过VPS测试
- 不问就改代码

---

## 十、成本

| 项目 | 月费 |
|------|------|
| VPS（Vultr） | ~¥35 |
| MiMo 2.5 Pro | ¥0（已停） |
| FRED API | $0 |
| Yahoo Finance | $0 |
| Tushare | $0（2000积分） |
| 和风天气 | $0（50K次/月） |
| Open-Meteo | $0 |
| **合计** | **~¥35/月** |

---

## 十一、Git 同步

- 仓库：`github.com/liuyuanlong3232-bit/macro-pipeline`
- 本地 → GitHub → VPS
- 每次改动推Git后，VPS通过 `git pull` 同步
- 记忆通过 `shared/memories/` 双向同步
