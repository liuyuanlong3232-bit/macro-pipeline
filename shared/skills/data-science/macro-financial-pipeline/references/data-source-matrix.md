# 数据源分类矩阵 — 2026-06-13 更新

## 一、API（官方接口）

| 数据 | 接口 | Key | 费用 |
|------|------|-----|------|
| FRED宏观指标 | `api.stlouisfed.org/fred` | FRED_API_KEY | 免费 |
| EIA能源数据 | `api.eia.gov/v2` | EIA_API_KEY | 免费 |
| Yahoo期货/外汇 | `query1.finance.yahoo.com` | 无 | 免费(防429) |
| Tushare中国期货+社融 | `api.tushare.pro` | TUSHARE_TOKEN | 积分制(2000分) |
| Open-Meteo天气 | `api.open-meteo.com/v1/forecast` | 无 | 完全免费 |
| AKShare中国宏观 | 本地Python库 | 无 | 完全免费 |
| Finnhub新闻 | `finnhub.io/api/v1/news` | FINNHUB_KEY | 免费(有限额) |
| AGSI+欧洲天然气 | `agsi.gie.eu/api` | AGSI_KEY | 免费 |
| cotdata.net CFTC | `cotdata.net/api/cot` | 无 | 免费(10req/min) |
| oddpool FedWatch | `oddpool.com` | 无 | 免费 |

## 二、爬取（网页解析）

| 数据 | URL | 方法 | 成功率 |
|------|-----|------|--------|
| USDA作物优良率 | Cornell PDF | pdfplumber | 高 |
| USDA出口检验 | TXT文件 | 正则解析 | 高 |
| BDI海运(备用) | Investing.com | requests+BS | 中(反爬) |
| OPEC MOMR(备用) | OPEC官网 | StealthyFetcher | 中(Cloudflare) |

## 三、CSV/Excel下载（稳定替代爬虫）

| 数据 | 来源 | 下载方式 |
|------|------|---------|
| BDI干散货运价 | Baltic Exchange官网 | CSV下载，官方源 |
| Baker Hughes钻机数 | 报告页面 | 静态HTML，反爬低 |
| 美湾港口库存 | USDA AMS | CSV批量导出 |
| 南美结转库存 | CONAB/阿根廷农业部 | CSV导出 |
| 中国压榨率/库存 | CNGOIC周报 | PDF/Excel(免费注册) |

## 四、未接入（无免费源）

| 数据 | 问题 |
|------|------|
| 生猪能繁存栏 | 农业部月度数据滞后 |
| 豆粕/玉米商业库存 | 卓创付费(替代: feedtrade免费版) |
