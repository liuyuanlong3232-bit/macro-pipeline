# 数据采集方式

## API（官方接口，稳定可靠）
| # | 数据 | 接口 | 报告 | 需Key | 备注 |
|---|------|------|------|-------|------|
| 1 | FRED宏观(75系列) | `api.stlouisfed.org/fred` | 宏观/贵金属 | FRED_API_KEY | FEDFUNDS/CPIAUCSL/DGS10等 |
| 2 | EIA原油库存/SPR/产量 | `api.eia.gov/v2/petroleum/stoc/wstk` | 能源 | EIA_API_KEY | 6个实时端点 |
| 3 | EIA OPEC产量 | `api.eia.gov/v2/steo` → PAPR_OPEC | 能源 | 同上 | 月度预测 |
| 4 | Yahoo期货/外汇/VIX | `query1.finance.yahoo.com/v8/finance/chart` | 全部 | 无需 | 15品种+外汇+VIX |
| 5 | Tushare中国期货 | `api.tushare.pro` → fut_daily | 中国农业 | TUSHARE_TOKEN | 仅交易日 |
| 6 | Tushare社融 | `sf_month`接口(需2000积分) | 宏观 | 同Token | month/inc_month/inc_cumval/stk_endval |
| 7 | Open-Meteo降水/温度 | `api.open-meteo.com/v1/forecast` | 国际农业 | 完全免费无Key | 5个农业区坐标7日预报 |
| 8 | AKShare中国宏观 | Python库(akshare) | 宏观 | 无Key | DR007/LPR/存准率/SHIBOR |
| 9 | Finnhub新闻 | `finnhub.io/api/v1/news` | 能源/地缘 | FINNHUB_KEY | |
| 10 | AGSI+欧洲天然气 | `agsi.gie.eu/api` | 能源 | AGSI_KEY | 德国填充率 |
| 11 | Cotdata.net CFTC | `cotdata.net` demo | 贵金属/农业 | 公开demo | COT Index+Z-Score |
| 12 | FedWatch | `oddpool.com` | 宏观 | 无需 | 降息概率 |

## 爬取（网页解析）
| # | 数据 | URL | 报告 | 方法 | 依赖 |
|---|------|-----|------|------|------|
| 1 | USDA作物优良率 | `usda.library.cornell.edu` | 国际农业 | PDF下载→pdfplumber解析 | pdfplumber |
| 2 | BDI波罗的海干散货 | `tradingeconomics.com/commodity/baltic` | 国际农业 | requests+BS4解析(主)；Investing.com(备) | bs4 |
| 3 | Baker Hughes钻机 | `aogr.com/web-exclusives/us-rig-count/{year}` | 能源 | requests+BS4解析Tailwind div表格 | bs4 |
| 4 | OPEC MOMR(备用) | `momr.opec.org/pdf-download` | 能源 | Scrapling StealthyFetcher | scrapling |
| 5 | USDA出口检验 | `ams.usda.gov/mnreports/wa_gr101.txt` | 国际农业 | requests TXT+正则 | — |

## 未接入（无免费源，需手动下载）
- 美湾港口库存 — USDA AMS MARS API(需注册Key)
- 南美结转库存 — CONAB/阿根廷农业部CSV(需手动下载)
- 中国油厂压榨率/豆粕库存/商业库存 — 卓创/钢联付费
- 生猪能繁存栏 — 农业部月度数据滞后
