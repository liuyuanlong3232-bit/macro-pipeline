# FRED Series Reference for Macro Analysis

## Interest Rates & Monetary Policy
| Series ID | Description | Frequency | Notes |
|-----------|-------------|-----------|-------|
| FEDFUNDS | Effective Federal Funds Rate | Daily | Current monetary policy rate |
| DGS1MO | 1-Month Treasury Yield | Daily | Shortest end of curve |
| DGS3MO | 3-Month Treasury Yield | Daily | Bill market benchmark |
| DGS1 | 1-Year Treasury Yield | Daily | Short-end benchmark |
| DGS2 | 2-Year Treasury Yield | Daily | Policy sensitivity |
| DGS5 | 5-Year Treasury Yield | Daily | Medium-term |
| DGS10 | 10-Year Treasury Yield | Daily | Key benchmark, mortgage correlation |
| DGS30 | 30-Year Treasury Yield | Daily | Long-end, inflation outlook |
| T10Y2Y | 10Y-2Y Spread (Yield Curve) | Daily | Inversion = recession signal |
| T10Y3M | 10Y-3M Spread | Daily | Alternative curve measure |
| T5YIFR | 5-Year Breakeven Inflation | Daily | Market-implied inflation expectation |
| T10YIE | 10-Year Breakeven Inflation | Daily | Key inflation expectation gauge |

## Real Rates
| Series ID | Description | Frequency | Notes |
|-----------|-------------|-----------|-------|
| DFII5 | 5-Year TIPS Yield | Daily | Short real rate |
| DFII10 | 10-Year TIPS Yield | Daily | KEY: proxy for gold opportunity cost |
| DFII20 | 20-Year TIPS Yield | Daily | Long real rate |
| DFII30 | 30-Year TIPS Yield | Daily | Longest real rate |

## Inflation
| Series ID | Description | Frequency | Notes |
|-----------|-------------|-----------|-------|
| CPIAUCSL | CPI All Items | Monthly | Headline inflation |
| CPILFESL | CPI Core (ex Food & Energy) | Monthly | Core inflation |
| PCEPILFE | Core PCE (ex Food & Energy) | Monthly | Fed's preferred measure |
| PCE | Personal Consumption Expenditures | Monthly | Broader consumption measure |
| PCEPILFE | PCE Core Price Index | Monthly | KEY: drives Fed policy |
| PPIACO | PPI Final Demand | Monthly | Producer prices, leading indicator |
| WPSFD49502 | PPI Final Demand (Services) | Monthly | Service sector inflation |
| OVX | CBOE Crude Oil Volatility Index | Daily | Energy inflation proxy |

## Employment
| Series ID | Description | Frequency | Notes |
|-----------|-------------|-----------|-------|
| PAYEMS | Nonfarm Payrolls | Monthly | KEY: jobs created |
| UNRATE | Unemployment Rate | Monthly | U-3 headline rate |
| U6RATE | U-6 Underemployment Rate | Monthly | Broader measure |
| JTSJOL | Job Openings (JOLTS) | Monthly | Labor demand |
| AWHMAN | Avg Weekly Hours (Manufacturing) | Monthly | Leading indicator |
| AHETPI | Avg Hourly Earnings | Monthly | Wage inflation |
| CIVPART | Labor Force Participation Rate | Monthly | Structural trend |

## GDP & Growth
| Series ID | Description | Frequency | Notes |
|-----------|-------------|-----------|-------|
| GDP | GDP (Billions) | Quarterly | Headline output |
| GDPC1 | Real GDP (Billions Chained) | Quarterly | Inflation-adjusted |
| GDPNOW | GDPNow Forecast | Daily | Atlanta Fed nowcast |
| INDPRO | Industrial Production | Monthly | Manufacturing output |
| TCU | Capacity Utilization | Monthly | Output slack |
| HOUST | Housing Starts | Monthly | Housing activity |
| PERMIT | Building Permits | Monthly | Leading indicator |

## Money & Dollar
| Series ID | Description | Frequency | Notes |
|-----------|-------------|-----------|-------|
| M2SL | M2 Money Supply | Monthly | Liquidity measure |
| M1SL | M1 Money Supply | Monthly | Narrow money |
| DTWEXBGS | Trade-Weighted USD Index | Weekly | Fed's broad dollar index |
| DTWEXM | USD Index (Major Currencies) | Weekly | Narrower USD measure |
| TOTCI | Total Net Corporate Inflows | Monthly | Capital flows |

## Consumer & Sentiment
| Series ID | Description | Frequency | Notes |
|-----------|-------------|-----------|-------|
| UMCSENT | Michigan Consumer Sentiment | Monthly | KEY: consumer confidence |
| CCI | Conference Board Consumer Confidence | Monthly | Alternative sentiment gauge |
| RRSFS | Real Retail Sales | Monthly | Consumer spending |
| MSP | Median Sales Price (New Homes) | Monthly | Housing affordability |

## Commodity-Specific
| Source | Data | Frequency | Access |
|--------|------|-----------|--------|
| CFTC | COT: Gold/Silver/Crude futures positioning | Weekly (Tue) | cftc.gov/dea/newcot/deafut.txt |
| AGSI+ | EU gas storage by country | Daily | agsi.gie.eu/api |
| EIA | US crude production | Monthly | api.eia.gov/v2/ |
| USDA NASS | Crop yields/production | Periodic | quickstats.nass.usda.gov |
| Alpha Vantage | Spot gold/silver/oil prices | Daily | alphavantage.co |
| Finnhub | Financial news, economic calendar | Daily | finnhub.io |
| Oddpool | FedWatch FOMC probabilities | Daily | oddpool.com/fed-market-watch |

## FRED API Usage
```python
import requests

# Single series, latest observations
url = "https://api.stlouisfed.org/fred/series/observations"
params = {
    "series_id": "DGS10",
    "api_key": "YOUR_KEY",
    "file_type": "json",
    "sort_order": "desc",
    "limit": 10,
}
resp = requests.get(url, params=params).json()
for obs in resp["observations"]:
    print(obs["date"], obs["value"])
```

## Common Errors & Fixes
| Error | Likely Cause | Fix |
|-------|-------------|-----|
| 400 Bad Request | Wrong series ID | Check spelling at fred.stlouisfed.org/series/ |
| API key empty | .env not loaded | Check path: HERMES_HOME vs ~/.hermes |
| SSL error on Windows | Python SSL config | Set REQUEST_CA_BUNDLE or use proxy |
