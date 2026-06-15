# Verified Data Source Reference

All API endpoints, symbols, series IDs verified working as of June 2026. Updated when new data sources are added to the pipeline.

## 1. FRED (Federal Reserve Economic Data)
**Base URL**: `https://api.stlouisfed.org/fred/series/observations`
**Auth**: API key in `FRED_API_KEY`
**Rate limit**: 120 requests/min (generous)

### Macro Indicators (verified working)
| Series ID | Description | Frequency | Verified |
|-----------|-------------|-----------|----------|
| FEDFUNDS | Fed Funds Rate | Daily | 3.63% |
| CPIAUCSL | CPI All Items | Monthly | 333.979 |
| PCEPILFE | Core PCE (ex F&E) | Monthly | 129.63 |
| PCE | Personal Consumption | Monthly | 21979.4 |
| GDP | GDP Nominal | Quarterly | 31819.464 |
| UNRATE | Unemployment Rate | Monthly | 4.3% |
| PAYEMS | Nonfarm Payrolls | Monthly | 159001 |
| AHETPI | Avg Hourly Earnings (all) | Monthly | 32.31 |
| CES0500000003 | Avg Hourly Earnings (private) | Monthly | 37.53 |
| JTSJOL | JOLTS Job Openings | Monthly | 7618 |
| JTSQUR | JOLTS Quit Rate | Monthly | 1.9% |
| DGS1 | 1Y Treasury Yield | Daily | 3.9% |
| DGS2 | 2Y Treasury Yield | Daily | 4.13% |
| DGS10 | 10Y Treasury Yield | Daily | 4.55% |
| DGS30 | 30Y Treasury Yield | Daily | 5.03% |
| T10Y2Y | 10Y-2Y Spread | Daily | 0.4 |
| DFII10 | 10Y TIPS Real Yield | Daily | 2.21% |
| T5YIFR | 5Y Breakeven Inflation | Daily | 2.18% |
| T10YIE | 10Y Breakeven Inflation | Daily | — |
| M2SL | M2 Money Supply | Monthly | 22804.5 |
| DTWEXBGS | Trade-Weighted USD | Weekly | 120.083 |
| PPIACO | PPI Final Demand | Monthly | 292.504 |
| INDPRO | Industrial Production | Monthly | 102.496 |
| HOUST | Housing Starts | Monthly | 1465 |
| UMCSENT | Michigan Consumer Sentiment | Monthly | 49.8 |
| FYFSD | Federal Deficit ($M) | Annually | -1.77T |

### Not Available on FRED
- ISM Manufacturing PMI (proprietary)
- China/Eurozone/Japan PMI (not in FRED free tier)

## 2. Alpha Vantage
**Base URL**: `https://www.alphavantage.co/query`
**Auth**: API key in `ALPHA_VANTAGE_API_KEY`
**Rate limit**: 5 calls/min, 25 calls/day (free tier)

### Verified Symbols (function=GLOBAL_QUOTE)
| Symbol | Description | Verified |
|--------|-------------|----------|
| XAUUSD | Gold spot (USD/oz) | $4,194.96 |
| XAGUSD | Silver spot (USD/oz) | $67.08 |
| CL | Crude Oil WTI | $89.39 |
| GLD | SPDR Gold Shares ETF | $386.32 |
| SLV | iShares Silver Trust ETF | $60.82 |
| SPX | S&P 500 Index | $737.76 |

### Not Available
- COMEX futures (GC=F, SI=F, CL=F) — use Yahoo Finance
- INCOMPLETE symbols: USOIL, XCUUSD, USDX — wrong format for Alpha Vantage

## 3. Yahoo Finance (Futures)
**Base URL**: `https://query1.finance.yahoo.com/v8/finance/chart/{SYMBOL}`
**Auth**: None (free, but blocked in China without proxy)
**Rate limit**: Implicit; handle 429 with exponential backoff (2^attempt + random)

### Verified Futures Symbols
| Symbol | Description | Type |
|--------|-------------|------|
| GC=F | COMEX Gold Futures | Precious metals |
| SI=F | COMEX Silver Futures | Precious metals |
| CL=F | WTI Crude Oil Futures | Energy |
| BZ=F | Brent Crude Oil Futures | Energy |
| NG=F | Henry Hub Natural Gas Futures | Energy |
| ZC=F | Corn Futures | Agriculture |
| ZS=F | Soybean Futures | Agriculture |
| ZW=F | Wheat Futures | Agriculture |
| ZL=F | Soybean Oil Futures | Agriculture |
| ZM=F | Soybean Meal Futures | Agriculture |
| CT=F | Cotton Futures | Agriculture |
| SB=F | Sugar #11 Futures | Agriculture |
| ^VIX | CBOE Volatility Index | Index |

### Pattern (exponential backoff)
```python
for attempt in range(3):
    r = requests.get(url, params={"range": "5d", "interval": "1d"}, 
                     headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    if r.status_code == 200: return r.json()
    elif r.status_code == 429: time.sleep((2**attempt) + random.random()*2)
    elif r.status_code == 403: time.sleep(5)
```

## 4. CFTC COT (Commitments of Traders)

### Source A: cotdata.net (recommended)
**URL**: `https://cotdata.net/api/cot?instrument={CFTC_CODE}&table=legacy`
**Auth**: None (free tier: latest week, 10 req/min)
**Provides**: COT Index (26W/52W/3Y), Z-Score, net_change, full positioning

| CFTC Code | Instrument | Verified |
|-----------|-----------|----------|
| 088691 | Gold (COMEX) | COT Index 100 (极度看多) |
| 084691 | Silver (COMEX) | COT Index 57 (中性) |
| 067651 | Crude Oil WTI (NYMEX) | COT Index 14 (看空) |
| 067411 | Crude Oil Brent (ICE) | COT Index 100 (极度看多) |
| 098662 | US Dollar Index DXY (ICE) | COT Index 71 (看多) |
| 001602 | Wheat SRW (CBOT) | COT Index 14 (看空) |
| 001612 | Wheat HRW (KCBT) | COT Index 14 |
| 002602 | Corn (CBOT) | COT Index 14 |
| 005602 | Soybeans (CBOT) | COT Index 14 |
| 025601 | Sugar #11 (ICE) | COT Index 50 (中性) |

### Source B: CFTC Legacy CSV (futures only)
**URL**: `https://www.cftc.gov/dea/newcot/deafut.txt`
**Frequency**: Weekly, released Tuesday 3:30pm ET

### Source C: CFTC TFF ZIP (financial futures)
**URL**: `https://www.cftc.gov/files/dea/history/fut_fin_txt_2026.zip`
**Contains**: VIX Futures, Eurodollar, Treasury futures (Financial/TFF format)
**Parsing**: Extract `FinFutYY.txt` from ZIP → parse as CSV with TFF column mapping

## 5. EIA STEO (Short-Term Energy Outlook)
**Base URL**: `https://api.eia.gov/v2/steo/data/`
**Auth**: API key in `EIA_API_KEY`
**Important**: MUST include `data[0]=value` in params to get actual data values.

| Series ID | Description | Unit |
|-----------|-------------|------|
| SODTC_US | Small-Scale Solar PV Total Capacity | megawatts |
| SODTP_US | Small-Scale Solar PV Total Generation | billion kWh |
| SOEPGEN_US | Utility-Scale Solar Generation (Electric Power) | billion kWh |
| ELICP_US | Industrial Electricity Sales | billion kWh |
| NGINCNS_US | Industrial Natural Gas Consumption | billion cu ft/month |

## 6. Finnhub
**URL**: `https://finnhub.io/api/v1/news?token={KEY}&category=general`
**Auth**: API key in `FINNHUB_API_KEY`
**Status**: ✅ 20 news articles/request; works in China (no proxy needed)

## 7. FedWatch (FOMC Rate Probabilities)
**URL**: `https://www.oddpool.com/fed-market-watch` (web scrape)
**Or**: `centralbank.watch/federal-reserve/`
**Why not CME**: CME returns 403 to all programmatic requests.

## 8. AGSI+ (European Gas Storage)
**URL**: `https://agsi.gie.eu/api?country=DE&size=7`
**Auth**: API key in `AGSI_API_KEY`
**Note**: Use individual country codes (DE=Germany, NL=Netherlands), NOT "EU"

## 9. VIX
**Price**: Yahoo Finance `^VIX` (via chart API with proxy)
**COT**: CFTC TFF format from `fut_fin_txt_YYYY.zip`
**Current**: $18.99, OI 410,614 (as of 2026-06-02)

## 10. Not Available (No Free API)

| Data | Reason |
|------|--------|
| SPDR GLD / SLV holdings | SPDR website has no open API; Yahoo requires crumb auth |
| COMEX inventory | CME shields all data |
| ISM PMI | Proprietary data |
| Global/China/EU PMI | Not in FRED free tier |
| International solar capacity | EIA/IRENA APIs require paid plans |
| VIX spot price history | Yahoo free tier only returns ~5 days |
