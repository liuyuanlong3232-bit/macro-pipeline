# 数据采集方式分类（2026-06-13）

## 🔵 API（官方接口，稳定可靠，14个）

| 数据 | 接口 | 报告 | Key？ |
|------|------|------|-------|
| FRED宏观指标(75系列) | api.stlouisfed.org/fred/series/observations | 宏观/贵金属 | ✅ FRED_API_KEY |
| EIA原油库存/SPR/产量/开工率 | api.eia.gov/v2/petroleum/stoc/wstk | 能源 | ✅ EIA_API_KEY |
| EIA天然气库存 | api.eia.gov/v2/natural-gas/stor/wkly | 能源 | ✅ 同上 |
| EIA OPEC产量预测(STEO) | api.eia.gov/v2/steo (PAPR_OPEC) | 能源 | ✅ 同上 |
| Yahoo期货价格(15品种) | query1.finance.yahoo.com/v8/finance/chart | 全部 | ❌ 无需Key |
| Yahoo外汇(EURUSD=X等) | 同上 | 宏观 | ❌ 无需Key |
| Tushare中国期货(10品种) | api.tushare.pro (POST) | 中国农业 | ✅ TUSHARE_TOKEN |
| Tushare中国宏观 | tushare pro (cn_cpi/cn_gdp/shibor) | 宏观 | ✅ 同上 |
| Open-Meteo降水/温度 | api.open-meteo.com/v1/forecast | 国际农业 | ❌ 完全免费无Key |
| AKShare中国利率 | 本地库（repo_rate_query等） | 宏观 | ❌ 免费 |
| Finnhub财经新闻 | finnhub.io/api/v1/news | 能源/地缘 | ✅ FINNHUB_KEY |
| AGSI+欧洲天然气库存 | agsi.gie.eu/api | 能源 | ✅ AGSI_KEY |
| cotdata.net CFTC持仓 | cotdata.net | 贵金属/农业 | ❌ 公开demo |
| FedWatch降息概率 | oddpool.com | 宏观 | ❌ 无需Key |

## 🟢 爬取（网页解析，6个）

| 数据 | URL | 方法 | 成功率 |
|------|-----|------|--------|
| USDA优良率 | usda.library.cornell.edu | 找PDF->pdfplumber解析 | ✅ 高 |
| USDA出口检验 | ams.usda.gov/mnreports/wa_gr101.txt | requests TXT->正则 | ✅ 高 |
| **BDI海运运价** | **tradingeconomics.com/commodity/baltic** | **requests+BS4解析** | **✅ VPS可用** |
| **Baker Hughes钻机** | **aogr.com/web-exclusives/us-rig-count/{year}** | **requests+BS4解析Tailwind div** | **✅ VPS可用** |
| OPEC MOMR(备用) | momr.opec.org | StealthyFetcher | ⚠️ 20s慢 |
| NOAA降水(弃用) | cpc.ncep.noaa.gov | 废弃(404) | ❌ 已弃用(Open-Meteo替代) |

## ⚪ 未接入（无免费数据源）

| 数据 | 原因 | 潜在付费方案 |
|------|------|-------------|
| 美湾港口库存 | 无公开免费API | Platts/S&P Global |
| 南美结转库存 | 无公开免费API | USDA FAS付费订阅 |
| 油厂压榨率/商业库存/存栏 | 卓创/钢联付费 | 卓创数据 |
| 生猪能繁存栏 | 农业部月度数据滞后 | 涌益咨询/钢联 |

**已接入的历史空缺项：**
- 社会融资规模(社融) → Tushare `sf_month` ✅（需2000积分）
- Baker Hughes钻机 → AOGR网站 ✅
- BDI海运运价 → TradingEconomics ✅

## 爬虫技术对比

```
requests + BeautifulSoup      -> USDA出口TXT、BDI(本地)     ✅ 高
PDF下载 + pdfplumber解析      -> USDA优良率(Cornell)      ✅ 高
curl + BeautifulSoup           -> Baker Hughes(VPS)        ⚠️ 中
Scrapling StealthyFetcher     -> OPEC MOMR(Cloudflare)     ⚠️ 慢
```
