# 全资产数据基础设施文档

> 2026-06-17 完整版

## 一、系统概览

### 数据流架构

```
数据源 (API/CSV)
    ↓
采集脚本 (Python)
    ↓
SQLite数据库 (hermes.db)
    ↓
报告生成器 (daily_report.py)
    ↓
输出 (Markdown + 邮件)
```

### 存储位置

| 类型 | 位置 | 说明 |
|------|------|------|
| SQLite | `/root/hermes-macro-data/hermes.db` | 23MB，核心数据库 |
| CSV | `/root/hermes-macro-data/csv/YYYY-MM-DD/` | 每日原始数据 |
| 报告 | `/root/hermes-macro-data/reports/` | 日报/周报 |
| 信号 | `/root/hermes-macro-data/signals/` | 每日信号存档 |
| 状态 | `/root/hermes-macro-data/meta/` | orchestrator状态 |

---

## 二、SQLite数据库 (hermes.db)

### 2.1 表格清单（按类别）

#### A. 宏观经济指标

| 表名 | 行数 | 数据源 | 更新频率 |
|------|------|--------|----------|
| fred_indicators | 377 | FRED API | 每日 |
| macro_history | 20,054 | 历史导入 | 一次性 |
| macro_联邦基金利率 | 180 | FRED | 月度 |
| macro_美国CPI | 179 | FRED | 月度 |
| macro_美国核心CPI | 179 | FRED | 月度 |
| macro_美国GDP | 60 | FRED | 季度 |
| macro_美国失业率 | 179 | FRED | 月度 |
| macro_美国非农就业 | 180 | FRED | 月度 |
| macro_美国PPI | 179 | FRED | 月度 |
| macro_美国核心PPI | 179 | FRED | 月度 |
| macro_美国M2 | 179 | FRED | 月度 |
| macro_美国工业产出 | 179 | FRED | 月度 |
| macro_ISM制造业指数 | 180 | FRED | 月度 |
| macro_美国零售销售 | 179 | FRED | 月度 |
| macro_美国10年国债收益率 | 3,747 | FRED | 日度 |
| macro_美国2年国债收益率 | 3,747 | FRED | 日度 |
| macro_10Y_2Y利差 | 3,749 | FRED | 日度 |
| macro_10年TIPS收益率 | 3,747 | FRED | 日度 |
| macro_5年盈亏平衡通胀率 | 3,749 | FRED | 日度 |
| macro_美元日元汇率 | 3,746 | FRED | 日度 |
| macro_美元人民币汇率 | 3,746 | FRED | 日度 |

#### B. 欧元区/日本/中国宏观

| 表名 | 行数 | 数据源 |
|------|------|--------|
| macro_欧元区CPI | 55 | FRED |
| macro_欧元区GDP | 60 | FRED |
| macro_欧元区失业率 | 140 | FRED |
| macro_ECB利率 | 5,476 | FRED |
| macro_德国10年国债收益率 | 176 | FRED |
| macro_日银利率 | 179 | FRED |
| macro_日本10年国债收益率 | 179 | FRED |
| macro_日本CPI | 121 | FRED |
| macro_日本GDP | 60 | FRED |
| macro_日本失业率 | 178 | FRED |
| macro_中国CPI | 167 | FRED |
| macro_中国GDP | 50 | FRED |
| macro_中国出口 | 178 | FRED |
| macro_中国进口 | 178 | FRED |
| macro_中国LPR利率 | 168 | FRED |
| macro_中国M1 | 91 | FRED |
| macro_中国M2 | 190 | FRED |

#### C. BIS汇率数据

| 表名 | 行数 | 频率 |
|------|------|------|
| macro_BIS央行政策利率_日度 | 5,847 | 日度 |
| macro_BIS央行政策利率_月度 | 185 | 月度 |
| macro_BIS名义有效汇率_广义_日度 | 6,208 | 日度 |
| macro_BIS名义有效汇率_广义_月度 | 184 | 月度 |
| macro_BIS名义有效汇率_狭义_日度 | 5,866 | 日度 |
| macro_BIS名义有效汇率_狭义_月度 | 184 | 月度 |
| macro_BIS实际有效汇率_广义_月度 | 184 | 月度 |
| macro_BIS实际有效汇率_狭义_月度 | 184 | 月度 |
| macro_BIS汇率_年度 | 15 | 年度 |
| macro_BIS汇率_日度 | 6,125 | 日度 |
| macro_BIS汇率_月度 | 185 | 月度 |

#### D. 期货价格

| 表名 | 行数 | 数据源 | 品种 |
|------|------|--------|------|
| yahoo_futures | 16 | Yahoo Finance | 国际期货实时 |
| price_黄金 | 3,771 | Yahoo Finance | 历史日线 |
| price_白银 | 3,771 | Yahoo Finance | 历史日线 |
| price_原油 | 3,772 | Yahoo Finance | 历史日线 |
| price_天然气 | 3,773 | Yahoo Finance | 历史日线 |
| price_铜 | 1 | Yahoo Finance | 历史日线 |
| price_铝 | 1 | Yahoo Finance | 历史日线 |
| price_锌 | 1 | Yahoo Finance | 历史日线 |
| price_镍 | 1 | Yahoo Finance | 历史日线 |
| price_锡 | 1 | Yahoo Finance | 历史日线 |
| price_玉米 | 3,769 | Yahoo Finance | 历史日线 |
| price_大豆 | 3,771 | Yahoo Finance | 历史日线 |
| price_小麦 | 3,771 | Yahoo Finance | 历史日线 |
| price_豆粕 | 3,771 | Yahoo Finance | 历史日线 |
| price_豆油 | 3,771 | Yahoo Finance | 历史日线 |
| price_棉花 | 3,772 | Yahoo Finance | 历史日线 |
| price_糖 | 3,773 | Yahoo Finance | 历史日线 |
| price_咖啡 | 3,772 | Yahoo Finance | 历史日线 |
| price_可可 | 3,772 | Yahoo Finance | 历史日线 |
| price_铂金 | 1 | Yahoo Finance | 历史日线 |
| price_钯金 | 1 | Yahoo Finance | 历史日线 |
| cn_futures | 10 | Tushare API | 中国期货 |

#### E. CFTC持仓数据

| 表名 | 行数 | 数据源 |
|------|------|--------|
| cotdata | 10 | cotdata.net |
| cftc_cot | 3 | CFTC官网 |
| cot_history | 10,697 | 历史导入 |
| cot_COT黄金 | 805 | cotdata.net |
| cot_COT白银 | 805 | cotdata.net |
| cot_COT原油 | 803 | cotdata.net |
| cot_COT天然气 | 805 | cotdata.net |
| cot_COT玉米 | 805 | cotdata.net |
| cot_COT大豆 | 805 | cotdata.net |
| cot_COT小麦 | 805 | cotdata.net |
| cot_COT棉花 | 805 | cotdata.net |
| cot_COT糖 | 805 | cotdata.net |
| cot_COT铜 | 805 | cotdata.net |
| cot_COT美元指数 | 226 | cotdata.net |
| cot_COT恐慌指数 | 805 | cotdata.net |
| cot_COT纳斯达克100 | 805 | cotdata.net |
| cot_COT标普500 | 805 | cotdata.net |
| cot_COT比特币 | 442 | cotdata.net |
| cot_COT以太坊 | 270 | cotdata.net |
| cot_COT瑞波币 | 55 | cotdata.net |
| cot_COT_Solana | 46 | cotdata.net |
| cot_FedWatch加息概率 | 14 | FedWatch |

#### F. 能源数据

| 表名 | 行数 | 数据源 |
|------|------|--------|
| eia_energy | 36 | EIA API |
| eia_steo | 6 | EIA API |
| energy_history | 19,317 | 历史导入 |
| energy_AGSI*储气 | 2,352×8国 | AGSI+ API |
| agsi_eu_gas | 7 | AGSI+ API |

#### G. 农业数据

| 表名 | 行数 | 数据源 |
|------|------|--------|
| agri_weather | 33,882 | Open-Meteo API |
| agri_USDA玉米种植进度 | 606 | USDA |
| agri_USDA玉米供需 | 42 | USDA |
| agri_USDA大豆种植进度 | 533 | USDA |
| agri_USDA大豆供需 | 42 | USDA |
| agri_USDA小麦种植进度 | 424 | USDA |
| agri_USDA小麦供需 | 42 | USDA |
| agri_USDA棉花种植进度 | 559 | USDA |
| agri_USDA棉花供需 | 128 | USDA |

#### H. 天气数据

| 表名 | 行数 | 数据源 |
|------|------|--------|
| cn_weather | 81 | 和风天气 API |
| agri_weather | 33,882 | Open-Meteo API |

#### I. 新闻/日历

| 表名 | 行数 | 数据源 |
|------|------|--------|
| financial_news | 20 | Finnhub API |
| finnhub_calendar | 10 | Finnhub API |
| news_economic_calendar_* | 21 | Finnhub API |
| news_news_* | 2-32 | Finnhub API |

#### J. 其他

| 表名 | 行数 | 说明 |
|------|------|------|
| commodity_prices | 5 | 商品价格 |
| vix_data | 805 | VIX历史 |
| summary_数据概览 | 111 | 数据统计 |

---

## 三、数据源详情

### 3.1 API数据源

| 数据源 | API地址 | 认证方式 | 更新频率 | 免费额度 |
|--------|---------|----------|----------|----------|
| FRED | api.stlouisfed.org | API Key | 每日 | 无限制 |
| Yahoo Finance | query1.finance.yahoo.com | 无需Key | 每日 | 无限制 |
| Tushare | api.tushare.pro | Token | 每日 | 2000积分 |
| 和风天气 | pg7dnaywrf.re.qweatherapi.com | Header Key | 每日 | 50K次/月 |
| Open-Meteo | api.open-meteo.com | 无需Key | 每日 | 10K次/天 |
| EIA | api.eia.gov | API Key | 每周 | 无限制 |
| CFTC | cftc.gov | 无需Key | 每周 | 无限制 |
| cotdata.net | cotdata.net | 无需Key | 每周 | 无限制 |
| Finnhub | finnhub.io | API Key | 每日 | 60次/分钟 |
| AGSI+ | agsi.gie.eu | API Key | 每日 | 无限制 |
| FedWatch | oddpool.com | 无需Key | 每日 | 无限制 |

### 3.2 CSV数据源

| 文件 | 位置 | 说明 |
|------|------|------|
| fred_indicators.csv | csv/YYYY-MM-DD/ | FRED每日采集 |
| yahoo_futures.csv | csv/YYYY-MM-DD/ | Yahoo每日采集 |
| 历史Excel | history/ | 一次性导入 |

---

## 四、数据采集流程

### 4.1 每日采集 (cron 08:00-08:10 CST)

```
08:00 daily_collect.py
  ├── fetch_fred() → fred_indicators.csv → fred_indicators表
  └── fetch_yahoo_futures() → yahoo_futures.csv → yahoo_futures表

08:03 fetch_cn_weather.py
  └── 和风天气API → cn_weather表 (9城市)

08:04 fetch_cn_futures.py
  └── Tushare API → cn_futures表 (5品种)

08:05 fetch_weather.py
  └── Open-Meteo API → agri_weather表 (6产区)

08:10 quality_check.py
  └── 检查所有表数据质量
```

### 4.2 每周采集

| 时间 | 脚本 | 数据源 |
|------|------|--------|
| 周三 23:00 | fix_eia_collect.py | EIA API |
| 周五 04:00 | macro_pipeline.py --source cot | cotdata.net |
| 周二 06:00 | check_usda.py | USDA |

### 4.3 报告生成 (cron 08:30 CST)

```
daily_report.py
  ├── 读取SQLite数据
  ├── 生成ABCD四区报告
  ├── 保存Markdown文件
  ├── 发送邮件 (send_email.py)
  └── 存档信号 (signals/)
```

---

## 五、报告结构

### 5.1 日报 (ABCD四区)

```
📊 全资产日报 · YYYY-MM-DD

A区 · 贵金属+宏观
  黄金 $xxxx | 白银 $xx.xx | DXY xx.xx
  10Y国债 x.xx% | TIPS x.xx% | VIX xx.xx

B区 · 能源
  WTI $xx.xx | Brent $xx.xx | 天然气 $x.xx
  EIA库存: xxxx

C区 · 农业天气
  玉米 xxx¢ | 大豆 xxx¢ | 小麦 xxx¢
  6产区天气异常检测

D区 · 中国农业
  国内期货: 生猪/豆粕/玉米/大豆/淀粉
  城市天气: 9城市实时数据

⚠️ 预警信号
📋 数据附表
```

### 5.2 周报摘要 (周五16:00)

```
weekly_summary.py
  ├── 读取本周5天信号文件
  ├── 统计异常次数
  ├── 计算周涨跌幅
  └── 列出下周事件
```

---

## 六、Orchestrator风控系统

### 6.1 三态检测

| 状态 | 触发条件 | 行为 |
|------|----------|------|
| 🟢 NORMAL | HTTP 200 | 正常请求 |
| 🟡 THROTTLED | HTTP 429 | 冷却60-90秒 |
| 🔴 BLOCKED | 连续3次429/2次403 | 冷却10-30分钟 |

### 6.2 三模式运维

| 模式 | 用途 | 请求限制 |
|------|------|----------|
| DEV | 开发测试 | ≤5次/session |
| TEST | 稳定性验证 | ≤20次/batch |
| PROD | 正式运行 | ≤6次/min/domain |

### 6.3 状态持久化

文件: `meta/orchestrator_state.json`

```json
{
  "updated_at": "2026-06-17T02:56:13",
  "sources": {
    "fred": {"state": "NORMAL", "total_requests": 29, "total_errors": 0},
    "yahoo": {"state": "NORMAL", "total_requests": 16, "total_errors": 0}
  }
}
```

---

## 七、邮件发送

### 7.1 配置

| 配置项 | 值 |
|--------|-----|
| SMTP服务器 | smtp.qq.com |
| 端口 | 465 (SSL) |
| 发件人 | 452731778@qq.com |
| 收件人 | 452731778@qq.com |

### 7.2 发送流程

```
daily_report.py
  → send_email.py
    → SMTP连接
    → 构建MIME邮件 (HTML表格+PNG图表)
    → 发送
    → 返回 True/False
```

---

## 八、Cron任务清单

| UTC时间 | CST时间 | 任务 |
|---------|---------|------|
| 00:00 | 08:00 | FRED+Yahoo采集 |
| 00:03 | 08:03 | 和风天气9城 |
| 00:04 | 08:04 | Tushare中国期货 |
| 00:05 | 08:05 | Open-Meteo全球天气 |
| 00:10 | 08:10 | 数据质检 |
| 00:30 | 08:30 | 日报生成+邮件 |
| 04:00 | 12:00 | Orchestrator状态检查 |
| 08:00 Fri | 16:00 Fri | 周报摘要 |
| 20:00 daily | 04:00 daily | 记忆推送到GitHub |
| 21:00 daily | 05:00 daily | Git拉取+记忆导入 |

---

## 九、数据质量控制

### 9.1 质检脚本 (quality_check.py)

检查项目：
- 数据时效性（是否过期）
- 极值校验（是否异常）
- 跨资产逻辑验证
- 完整性校验

### 9.2 输出

- 质检报告: `shared/reminders/quality_report_YYYY-MM-DD.txt`
- 健康度评分: 通过率百分比

---

## 十、文件结构总览

```
/root/hermes-pipeline/
├── scripts/                    ← 20个采集/报告脚本
├── shared/                     ← 公共模块
│   ├── utils.py                ← 工具函数
│   ├── orchestrator.py         ← 风控调度器
│   ├── mode.py                 ← 模式管理
│   └── knowledge/              ← 知识库
├── deploy/                     ← 部署配置
│   ├── hermes-cron             ← cron定义
│   └── HERMES_RULES.md         ← 工作纪律
├── config/                     ← 配置文件
│   └── mode.json               ← 当前模式
├── macro_pipeline.py           ← 核心采集引擎
├── send_email.py               ← 邮件模块
└── monitor.py                  ← 价格预警

/root/hermes-macro-data/
├── hermes.db                   ← SQLite数据库 (23MB)
├── csv/YYYY-MM-DD/             ← 每日CSV
├── reports/                    ← 报告文件
├── signals/                    ← 信号存档
├── meta/                       ← 状态文件
│   └── orchestrator_state.json
└── history/                    ← 历史数据
```
