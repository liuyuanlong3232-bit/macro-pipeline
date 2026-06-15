# API Reference: Financial Macro Data Sources

## FRED (Federal Reserve Economic Data)

**Base URL**: `https://api.stlouisfed.org/fred`
**Auth**: API key in query param `api_key=`
**Endpoint**: `/series/observations`

Key parameters:
- `series_id`: FRED series code
- `file_type`: `json`
- `sort_order`: `desc`
- `limit`: max observations

Common FRED series:
- `FEDFUNDS` — Federal Funds Rate
- `CPIAUCSL` — Consumer Price Index
- `GDP` — Gross Domestic Product
- `UNRATE` — Unemployment Rate
- `PAYEMS` — Nonfarm Payrolls
- `DGS10` — 10-Year Treasury Yield
- `DGS2` — 2-Year Treasury Yield
- `T10Y2Y` — 10Y-2Y Spread (yield curve)
- `M2SL` — Money Supply M2
- `PPIACO` — Producer Price Index
- `INDPRO` — Industrial Production
- `HOUST` — Housing Starts
- `UMCSENT` — Michigan Consumer Sentiment
- `TREAST` — 1-Year Treasury (note: FRED returns raw values; check units before display)
- `DTWEXBGS` — Trade-Weighted USD Index

## Alpha Vantage

**Base URL**: `https://www.alphavantage.co/query`
**Auth**: API key in query param `apikey=`
**Rate limit**: 5 calls/minute (free tier). Insert `time.sleep(1.2)` between calls.

Key endpoint: `function=GLOBAL_QUOTE`
- `symbol=CL=F` — Crude Oil
- `symbol=GC=F` — Gold
- `symbol=SI=F` — Silver
- `symbol=NG=F` — Natural Gas
- `symbol=ZC=F` — Corn
- `symbol=ZS=F` — Soybeans
- `symbol=ZW=F` — Wheat
- `symbol=HG=F` — Copper
- `symbol=DX-Y.NYB` — US Dollar Index
- `symbol=SPY` — S&P 500 ETF

Returns: `{"Global Quote": {"01. symbol": "...", "05. price": "...", "10. change percent": "..."}}`

## EIA (U.S. Energy Information Administration)

**Base URL**: `https://api.eia.gov/v2`
**Auth**: API key in query param `api_key=`
**Endpoint**: `/petroleum/crd/crpdn/data/` — crude oil production
**Endpoint**: `/natural-gas/cons/sum/data/` — natural gas consumption

Parameters: `frequency=weekly`, `data[0]=value`, `facets[duoarea][]=NUS`, `sort[0][column]=period`, `sort[0][direction]=desc`

## CFTC COT (Commitments of Traders)

**Public CSV**: `https://www.cftc.gov/dea/futures/dea.txt`
**Auth**: Public — no key needed for basic CSV download.
Search keywords: GOLD, SILVER, CRUDE OIL, LIGHT SWEET
The API key from cftc.gov is for the registered data API; the public CSV endpoint requires no auth.

## Finnhub

**Base URL**: `https://finnhub.io/api/v1`
**Auth**: API token in query param `token=`
- `/calendar/economic` — economic calendar (may 403 on free tier)
- `/news` — market news, param `category=general`

## AGSI+ / ALSI / IIP (GIE — Gas Infrastructure Europe)

**Base URL**: `https://agsi.gie.eu/api`
**Auth**: Header `x-key: YOUR_KEY`
Parameters: `country=EU`, `date_from=`, `date_to=`, `size=30`
Returns: `{"data": [{country, gasDayStart, gasInStorage, fillingRate, workingGasVolume, injection}]}`

The same key works for all three GIE platforms (AGSI, ALSI, IIP).

## USDA NASS (National Agricultural Statistics Service)

**Base URL**: `https://quickstats.nass.usda.gov/api/api_GET/`
**Auth**: API key in query param `api_key=`
Parameters: `source_desc=SURVEY`, `sector_desc=CROPS`, `commodity_desc=CORN`, `statisticcat_desc=YIELD`, `year__GE=2023`

## NewsAPI

**Base URL**: `https://newsapi.org/v2/everything`
**Auth**: API key in query param `apiKey=`
Parameters: `q=` (search query), `language=en`, `sortBy=publishedAt`, `pageSize=20`

## OpenWeather

**Base URL**: `https://api.openweathermap.org/data/2.5/weather`
**Auth**: API key in query param `appid=`
Parameters: `q=City,CC`, `units=metric`
Useful for commodity-impact weather monitoring at exchange locations.

## Japan e-Stat

**Base URL**: `https://api.e-stat.go.jp/rest/3.0/app/getSimpleStatsData`
**Auth**: API key in query param `appId=`
Parameters: `lang=J`, `statsCode=00200561` (CPI), `limit=10`
