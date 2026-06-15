# Financial Data Sources Quick Reference

## Macro Indicators (FRED)

| Series ID | Description | Frequency |
|-----------|-------------|-----------|
| FEDFUNDS | Federal Funds Rate | Daily |
| CPIAUCSL | CPI (Consumer Price Index) | Monthly |
| PCEPILFE | Core PCE (ex Food & Energy) | Monthly |
| PCE | Personal Consumption Expenditures | Monthly |
| GDP | Gross Domestic Product | Quarterly |
| UNRATE | Unemployment Rate | Monthly |
| PAYEMS | Nonfarm Payrolls | Monthly |
| DGS1 | 1-Year Treasury Yield | Daily |
| DGS2 | 2-Year Treasury Yield | Daily |
| DGS10 | 10-Year Treasury Yield | Daily |
| T10Y2Y | 10Y-2Y Spread | Daily |
| DFII10 | 10-Year TIPS (Real Yield) | Daily |
| T5YIFR | 5-Year Breakeven Inflation | Daily |
| T10YIE | 10-Year Breakeven Inflation | Daily |
| M2SL | M2 Money Supply | Monthly |
| DTWEXBGS | Trade-Weighted USD Index | Daily |
| PPIACO | PPI (Producer Price Index) | Monthly |
| INDPRO | Industrial Production Index | Monthly |
| HOUST | Housing Starts | Monthly |
| UMCSENT | U.Mich Consumer Sentiment | Monthly |
| VIXCLS | CBOE Volatility Index (VIX) | Daily |

## Commodities (Alpha Vantage)

| Symbol | Product | Notes |
|--------|---------|-------|
| XAUUSD | Gold Spot | Works |
| XAGUSD | Silver Spot | Works |
| CL | Crude Oil WTI | Works |
| GLD | SPDR Gold ETF | Works |
| SLV | iShares Silver ETF | Works |
| SPX | S&P 500 Index | Sometimes empty |

## Futures (Yahoo Finance)

| Symbol | Product | Notes |
|--------|---------|-------|
| GC=F | Gold Futures (COMEX) | Needs proxy from CN |
| SI=F | Silver Futures (COMEX) | Needs proxy from CN |
| CL=F | WTI Crude Futures | Needs proxy from CN |
| %5EVIX | VIX Spot Index | Needs proxy from CN |

## CFTC COT (cotdata.net API)

| CFTC Code | Instrument | Table | Notes |
|-----------|-----------|-------|-------|
| 088691 | Gold (COMEX) | legacy/disaggregated | COT Index, Z-Score |
| 084691 | Silver (COMEX) | legacy/disaggregated | COT Index, Z-Score |
| 067651 | Crude Oil WTI (NYMEX) | legacy/disaggregated | COT Index, Z-Score |
| 098662 | USD Index (ICE) | legacy | COT Index, Z-Score |
| 099741 | Euro FX (CME) | tff | TFF format |

## CFTC TFF (ZIP Archive — Financial Futures)

| Market | Search Key | Report | Notes |
|--------|-----------|--------|-------|
| VIX Futures | VIX FUTURES | fut_fin_txt_2026.zip | Dealers/AM/Leveraged Funds |

## VIX Data

| Component | Source | Symbol/Code |
|-----------|--------|-------------|
| Price | Yahoo Finance | %5EVIX |
| Open Interest | CFTC TFF ZIP | fut_fin_txt_2026.zip |
| Dealer Positioning | CFTC TFF ZIP | TFF columns [8]-[10] |
| Asset Mgr Positioning | CFTC TFF ZIP | TFF columns [11]-[13] |
| Lev Fund Positioning | CFTC TFF ZIP | TFF columns [14]-[16] |

## EIA STEO (Solar & Industrial)

| Series ID | Description | Frequency |
|-----------|-------------|-----------|
| SODTC_US | Total Small-Scale Solar PV Capacity | Monthly |
| SODTP_US | Total Small-Scale Solar PV Generation | Monthly |
| SPEPCGWX | Electric Power Solar PV Summer Capacity | Monthly |
| SODCC_US | Commercial Solar PV Capacity | Monthly |
| SODIC_US | Industrial Solar PV Capacity | Monthly |
| SODRC_US | Residential Solar PV Capacity | Monthly |
| SODCP_US | Commercial Solar PV Generation | Monthly |
| SODIP_US | Industrial Solar PV Generation | Monthly |
| SODRP_US | Residential Solar PV Generation | Monthly |
| ELICP_ENC | Industrial Electricity Sales: E North Central | Monthly |
| ELICP_ESC | Industrial Electricity Sales: E South Central | Monthly |
| ELICP_MTN | Industrial Electricity Sales: Mountain | Monthly |
| ELICP_PAC | Industrial Electricity Sales: Pacific | Monthly |

Note: Solar data is US-only. International solar requires IRENA or BNEF.

## Other APIs

| Source | Endpoint | Auth | Limits |
|--------|----------|------|--------|
| Finnhub News | finnhub.io/api/v1/news | FINNHUB_API_KEY | 100 req/min free |
| AGSI+ Gas | agsi.gie.eu/api | x-key header | Free |
| Oddpool FedWatch | oddpool.com/fed-market-watch | None | Web scraping |
| cotdata.net | cotdata.net/api/cot | None | 10 req/min, latest week only |

## Output File Mapping

| CSV File | Source Function | Key Columns |
|----------|----------------|-------------|
| fred_indicators.csv | fetch_fred() | 日期, 指標, 數值, 系列ID |
| commodity_prices.csv | fetch_alpha_vantage() | 品種, 最新價, 漲跌幅% |
| yahoo_futures.csv | fetch_yahoo_futures() | 品種, 最新價, 日變化, 5日範圍 |
| financial_news.csv | fetch_news() | 標題, 來源, 發布時間 |
| cotdata.csv | fetch_cot() | 品種, 投機淨持倉, COT Index, Z-Score |
| vix_data.csv | fetch_vix() | 價格, 未平倉合約, 交易商淨, 槓桿基金淨 |
| eia_energy.csv | fetch_eia() | 日期, 數值, 單位 |
| agsi_eu_gas.csv | fetch_agsi() | 國家, 庫存(TWh), 填充率% |
| fedwatch.csv | fetch_fedwatch() | 維持概率%, 加息概率%, 降息概率% |
