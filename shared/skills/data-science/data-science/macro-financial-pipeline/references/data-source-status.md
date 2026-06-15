# 数据源可访问性审计

## 国内可用（本地 / v2rayN代理）

| 数据源 | 授权方式 | 更新频率 | 
|--------|---------|---------|
| FRED | API Key | 日/月/季 |
| Alpha Vantage | API Key (25次/日) | 日 |
| Yahoo Finance | 免费 | 日 |
| cotdata.net | 免费 (10次/分) | 周 (周二) |
| CFTC ZIP | 免费 | 周 (周二) |
| Finnhub | API Key | 日 |
| AGSI+ | API Key | 日 |
| EIA STEO | API Key | 月 |
| NOAA CPC | 免费 | 周 |
| FedWatch/Oddpool | 免费 | 日 |
| Tushare | API Key (2000积分) | 月/季 |
| 日本e-Stat | API Key | 月 |

## 需美国VPS直连

| 数据源 | 原因 | 更新频率 |
|--------|------|---------|
| ECB SDW | SSL证书被国内代理阻断 | 日/月 |
| OPEC MOMR | Cloudflare防护 | 月 (11-15日) |
| CONAB | 巴西IP限制 | 月 (10-15日) |
| 布交所 | IP限制 | 周 |

## 付费墙（非免费）

| 数据源 | 替代方案 |
|--------|---------|
| ISM PMI | 需ISM订阅，无免费替代 |
| SPDR GLD/SLV持仓 | 无免费API，手动查 |
| 全球央行购金 | WGC季度报告，手动导入 |
