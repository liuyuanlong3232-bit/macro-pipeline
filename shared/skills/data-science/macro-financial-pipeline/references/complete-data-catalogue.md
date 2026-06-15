# Complete Data Source Catalogue

Verified endpoints, working symbols, failure modes, and access notes for every data source in the pipeline.

## FRED (Federal Reserve)

**Base:** `https://api.stlouisfed.org/fred`  
**Auth:** API key via `FRED_API_KEY` env var  
**Rate:** No significant limit  
**All 24 verified series:**

| Series ID | Name (Simplified) | Batch Verified |
|-----------|-------------------|---------------|
| FEDFUNDS | 联邦基金利率 | ✅ 3.63% |
| CPIAUCSL | CPI | ✅ 333.979 |
| PCEPILFE | 核心PCE | ✅ 129.63 |
| PCE | PCE | ✅ 21,979.4 |
| GDP | GDP | ✅ 31,819 |
| UNRATE | 失业率 | ✅ 4.3% |
| PAYEMS | 非农就业 | ✅ 159,001 |
| AHETPI | 平均时薪(全部员工) | ✅ $32.31 |
| CES0500000003 | 平均时薪(生产/非管理) | ✅ $37.53 |
| JTSJOL | JOLTS职位空缺数 | ✅ 7,618 |
| JTSQUR | JOLTS离职率 | ✅ 1.9% |
| DGS1 | 1年期国债收益率 | ✅ 3.9% |
| DGS2 | 2年期国债收益率 | ✅ 4.13% |
| DGS10 | 10年期国债收益率 | ✅ 4.55% |
| DGS30 | 30年期国债收益率 | ✅ 5.03% |
| T10Y2Y | 10-2年利差(收益率曲线) | ✅ 0.4 |
| DFII10 | 10年期TIPS收益率(实际利率) | ✅ 2.21% |
| T5YIFR | 5年盈亏平衡通胀率 | ✅ 2.18% |
| T10YIE | 10年盈亏平衡通胀率 | ✅ (T10YIFR invalid) |
| M2SL | M2货币供应量 | ✅ 22,804 |
| DTWEXBGS | 美元指数(贸易加权) | ✅ 120.08 |
| PPIACO | PPI | ✅ 292.5 |
| INDPRO | 工业生产指数 | ✅ 102.5 |
| HOUST | 新屋开工 | ✅ 1,465 |
| UMCSENT | 密歇根消费者信心指数 | ✅ 49.8 |
| FYFSD | 联邦财政赤字(百万$) | ✅ -$1.77T |
| CLVMNACSCAB1GQEA19 | 欧元区GDP | ✅ 2,880,687 |
| IRSTCI01EZM156N | 欧元区利率(%) | ✅ 1.93% |

## Alpha Vantage

**Base:** `https://www.alphavantage.co/query`  
**Auth:** API key via `ALPHA_VANTAGE_API_KEY`  
**Rate:** 5 calls/min, 25 calls/day (free)  
**Function:** `GLOBAL_QUOTE`

| Symbol | Name | Status | Price |
|--------|------|--------|-------|
| XAUUSD | 黄金现货 | ✅ | $4,194.96 |
| XAGUSD | 白银现货 | ✅ | $67.08 |
| CL | WTI原油 | ✅ | $89.39 |
| GLD | SPDR Gold Shares ETF | ✅ | $386.32 |
| SLV | iShares Silver Trust | ✅ | $60.82 |
| SPX | S&P 500 | ❌ Returns empty | — |
| USDX | 美元指数 | ⚠️ Wrong value | 25.71 (incorrect) |

**Pitfall:** Must add `time.sleep(12)` between calls to respect 5/min rate.

## Yahoo Finance Chart API

**Base:** `https://query1.finance.yahoo.com/v8/finance/chart/{symbol}`  
**Auth:** None  
**Rate:** ~10 calls/min soft limit  
**Range param:** `range=5d&interval=1d`  

| Symbol | Name | Status | Price |
|--------|------|--------|-------|
| GC=F | COMEX黄金期货 | ✅ | $4,212 |
| SI=F | COMEX白银期货 | ✅ | $66.63 |
| CL=F | WTI原油期货 | ✅ | $85.36 |
| BZ=F | Brent原油期货 | ✅ | $88.24 |
| NG=F | Henry Hub天然气 | ✅ | $3.102 |
| ZC=F | 玉米期货 | ✅ | $411.75 |
| ZS=F | 大豆期货 | ✅ | $1,114.25 |
| ZW=F | 小麦期货 | ✅ | $584.25 |
| ZL=F | 豆油期货 | ✅ | $73.85 |
| ZM=F | 豆粕期货 | ✅ | $303.00 |
| CT=F | 棉花期货 | ✅ | $76.54 |
| SB=F | 糖期货 | ✅ | $14.34 |
| EURUSD=X | EUR/USD汇率 | ✅ | 1.1569 |
| ^VIX | VIX波动率指数 | ✅ | $18.99 |

**Pitfall:** Blocked from mainland China. Must route through proxy.  
**Pitfall:** `^` prefix for indices needs URL encoding: `%5EVIX`.

## cotdata.net (CFTC COT — preferred source)

**Base:** `https://cotdata.net/api/cot`  
**Auth:** None (free tier)  
**Rate:** 10 req/min  
**Data:** Latest week only, no history on free tier  
**Includes:** COT Index (26W/52W), Z-Score, net changes

| CFTC Code | Name | Status | COT Index | Z-Score |
|-----------|------|--------|-----------|---------|
| 088691 | 黄金 | ✅ | 100 (极端看多) | +1.73 |
| 084691 | 白银 | ✅ | 57 (中性) | -0.16 |
| 067651 | 原油WTI | ✅ | 14 (看空) | -1.44 |
| 067411 | 原油Brent | ✅ | 100 (极端看多) | +2.13 |
| 098662 | 美元指数DXY | ✅ | 71 (看多) | +0.64 |
| 001602 | 小麦SRW | ✅ | 14 (看空) | -1.89 |
| 001612 | 小麦HRW | ✅ | 14 (看空) | -1.87 |
| 002602 | 玉米 | ✅ | 14 (看空) | -1.75 |
| 005602 | 大豆 | ✅ | 14 (看空) | -1.49 |
| 025601 | 糖#11 | ✅ | 50 (中性) | -0.25 |
| 033601 | 棉花 | ❌ 404 | — | — |
| 073601 | 豆油 | ❌ 429 | — | — |
| 092691 | 铜 | ❌ 429 | — | — |
| 112601 | 天然气 | ❌ 429 | — | — |

**Pitfall:** 429 errors when exceeding 10 req/min. Space requests 3+ seconds apart or accept partial coverage.

## CFTC ZIP Archives (VIX + Financial Futures)

**URL:** `https://www.cftc.gov/files/dea/history/fut_fin_txt_2026.zip`  
**Contains:** TFF format data (Traders in Financial Futures)  
**Content:** `FinFutYY.txt` — all financial futures including VIX

**TFF column layout (CRITICAL — differs from Legacy):**
```
[7]  = Open_Interest_All
[8]  = Dealer_Positions_Long_All
[9]  = Dealer_Positions_Short_All
[10] = Dealer_Positions_Spread_All
[11] = Asset_Mgr_Positions_Long_All
[12] = Asset_Mgr_Positions_Short_All
[13] = Asset_Mgr_Positions_Spread_All
[14] = Lev_Money_Positions_Long_All
[15] = Lev_Money_Positions_Short_All
[16] = Lev_Money_Positions_Spread_All
```

**VIX data (2026-06-02):** OI 410,614 | Dealers net +49,337 | Asset Mgrs net -12,516 | Lev Funds net -33,033

**Pitfall:** Legacy and TFF have DIFFERENT column indices. Do NOT use Legacy indices for TFF data.

## AGSI+ (European Gas Storage)

**Base:** `https://agsi.gie.eu/api`  
**Auth:** `x-key` header with `AGSI_API_KEY`  
**Country codes that work:** `DE` (Germany), not `EU`  
**Fill rate:** NOT returned as a field. Calculate: `gasInStorage / workingGasVolume * 100`

## EIA STEO

**Base:** `https://api.eia.gov/v2/steo/data/`  
**Auth:** `EIA_API_KEY`  
**Must include:** `data[0]=value` param to get numeric values

## OpenWeather

**Auth:** `OPENWEATHER_API_KEY`  
**Verified cities:** Chicago, New York, London, Singapore, Shanghai, Tokyo, Sao Paulo, Buenos Aires, Rostov

## News Sources

| Source | Status | Blocked in China? | Notes |
|--------|--------|------------------|-------|
| Finnhub | ✅ 20条/日 | ✅ No | Preferred for China |
| NewsAPI | ⚠️ Timeout | ❌ Blocked | Connection timeout from China |

## Tushare (中国宏观)

**Token:** Stored in `TUSHARE_TOKEN`  
**Points:** 2000 (limited — use only for monthly/quarterly macro)  
**Working endpoints:**
- `cn_cpi()` — CPI: field `nt_yoy` = yoy% change
- `cn_pmi()` — PMI: field `PMI010100` = Manufacturing PMI
- `cn_gdp()` — GDP: fields `gdp`, `gdp_yoy`
- `cn_m()` — Money supply: fields `m0`, `m1`, `m2`

**Latest data (2026-05):** CPI 1.2%, PMI 51.1

## Japan e-Stat

**Key:** Stored in `ESTAT_API_KEY`  
**API:** v3 — `https://api.e-stat.go.jp/rest/3.0/app/getSimpleStatsData`  
**Status:** API endpoint alive (200), but needs correct `statsDataId` parameter. Currently returns 101 "specify statsDataId or dataSetId".

## ECB SDW (Eurozone)

**Endpoint:** `https://sdw-wsrest.ecb.europa.eu/service`  
**Status:** ❌ SSL error from China (even through v2rayN proxy)  
**VPS:** Directly accessible from US VPS  
**FRED alternatives (work from anywhere):** CLVMNACSCAB1GQEA19, IRSTCI01EZM156N

## OPEC MOMR

**Status:** ❌ Cloudflare blocked from China  
**VPS needed:** Yes (US clean IP)  
**Priority:** Excel appendix > PDF  
**Update:** Monthly, 11th-15th  
**URL pattern:** `https://www.opec.org/opec_web/static_files_project/media/downloads/publications/MOMR_{Month}_{Year}.pdf`

## CONAB (Brazilian Agriculture)

**Status:** ✅ Public, no API key  
**VPS needed:** Yes (blocked from China)  
**Language:** Portuguese  
**Number format:** `.` = thousand sep, `,` = decimal  
**Update:** Monthly, 10th-15th  
**Must clean:** `value = raw.replace('.', '').replace(',', '.')`

## NOAA ENSO

**Status:** ✅ Fully free, no API key  
**URLs:**
- Weekly SST: `https://www.cpc.ncep.noaa.gov/data/indices/wksst8110.for`
- ONI Index: `https://psl.noaa.gov/data/correlation/oni.data`
- SST by region: `https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices`

## ISM PMI (Manufacturing & Services)

**URL:** `https://www.ismworld.org/supply-management-news-and-reports/reports/ism-report-on-business/`  
**Status:** ❌ Behind paywall/login (SSO required)  
**Verdict:** Not available via free API. Do not pursue further.

## China Agricultural Futures

**Attempted sources (all failed):**
- Tushare fut_daily(): ❌ 2000积分不覆盖期货日线
- Yahoo Finance Chinese agri symbols: ❌ 404
- **Status:** Data source needed. Options: upgrade Tushare, scrape sina/eastmoney, or Wind API.
