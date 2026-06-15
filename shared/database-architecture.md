# 数据库架构 · 完整盘点

> 最后更新：2026-06-15

## 📦 hermes.db（23MB，100+张表，~15万行）

### 历史数据（刚导入的，来自 D:\commodity_research_platform\export\merged）

| 类别 | 表数 | 行数 | 时间范围 | 内容 |
|------|------|------|---------|------|
| **macro_** | 46 | ~50,000 | 2011-2026 | 美国/欧元区/日本/中国全宏观指标 |
| **price_** | 18 | ~56,000 | 2011-2026 | 14品种日线OHLCV |
| **energy_** | 9 | ~19,000 | 2020-2026 | AGSI 7国天然气库存 + EIA |
| **agri_** | 8 | ~2,400 | 2016-2026 | USDA种植进度 + WASDE供需 |
| **cot_** | 17 | ~11,000 | 2011-2026 | 全品种CFTC持仓 |
| **news_** | 11 | ~70 | 2022-2026 | 历史新闻 |
| **summary_** | 1 | 111 | — | 数据概览 |

### 实时/采集数据

| 表 | 行数 | 说明 |
|----|------|------|
| fred_indicators | 377 | 29个FRED系列每日更新 |
| yahoo_futures | 16 | 每天采集覆盖 |
| cotdata | 10 | cotdata.net |
| eia_energy | 6 | EIA API |
| eia_steo | 6 | EIA STEO |
| vix_data | 1 | CFTC TFF |
| price_history | 45,231 | 历史K线 |
| cot_history | 10,697 | CFTC历史 |
| macro_history | 20,054 | FRED历史 |
| energy_history | 19,317 | EIA历史 |

### 实体Excel备份
VPS: `/root/hermes-macro-data/history/*.xlsx`（7个文件，7.9MB）
本地原始位置：`D:\commodity_research_platform\export\merged\`

---

## ❌ 仍然缺失的数据

| 数据 | 说明 | 计划 |
|------|------|------|
| **天气历史数据** | Open-Meteo有免费历史API，可回溯到1940年 | 下一个要做 |
| 中国CNGOIC | 压榨率PDF | 待确认版权 |
| 饲料库存 | 行业网站 | 待确认ToS |

---

## 历史数据中天气情况

| 文件 | 包含天气吗 |
|------|-----------|
| 7个Excel | ❌ 不含天气数据 |
| Open-Meteo | ✅ 有完整历史API → `https://archive-api.open-meteo.com/` |
| 计划 | 下次做天气入库时一起拉历史，回溯到2011年 |
