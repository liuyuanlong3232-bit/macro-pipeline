# Common Financial Data Sources — Scrapling Config

## Proxy Quick Reference

| Environment | Proxy Config |
|-------------|--------------|
| Local Windows (v2rayN) | `proxies={"http": "http://127.0.0.1:10808", "https": "http://127.0.0.1:10808"}` |
| Local Windows (Clash) | `proxies={"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}` |
| VPS (direct) | No proxy needed |
| Env var fallback | `os.environ.get("HTTP_PROXY")` → `proxies={"http": env_val, "https": env_val}` |

## Known-Good Source Configurations

### EIA Weekly Petroleum
```python
# Static HTML table
from scrapling import Fetcher
f = Fetcher()
resp = f.get("https://www.eia.gov/petroleum/supply/weekly/")
# Table rows typically have class containing "data-row"
# Date columns often in <th> with class "row-date"
```

### CFTC COT (Legacy ZIP)
```python
# FTP/HTTP ZIP download — use requests for the binary file, not Scrapling
import requests
url = "https://www.cftc.gov/files/dea/history/fut_fin_txt_2026.zip"
r = requests.get(url)
# Save as .zip, extract, parse the TXT
```

### USDA WASDE
```python
# Static PDF/HTML
resp = f.get("https://www.usda.gov/oce/commodity/wasde")
# Usually a PDF download link — extract href from <a> tag
```

### NOAA ENSO Advisory
```python
# Static text
resp = f.get("https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso_advisory/")
# ENSO discussion is in plain text paragraphs
# Find by CSS: resp.css(".normal p::text").getall()
```

### CME Open Interest (JS-rendered)
```python
# Requires DynamicFetcher (Playwright)
from scrapling.fetchers import DynamicFetcher
page = DynamicFetcher.fetch(
    "https://www.cmegroup.com/market-data/volume-open-interest/",
    headless=True,
    wait_selector=(".table-container", "visible"),
    network_idle=True,
)
```

## CSS Selector Patterns

| Data | Likely CSS Pattern |
|------|-------------------|
| Table rows | `table tr`, `.data-row`, `tr.data` |
| Table cells | `td`, `.cell`, `.value` |
| Headers | `th`, `h1`, `h2`, `.title` |
| Links | `a::attr(href)`, `a[href$=".pdf"]` |
| Numbers | `::text` then `float(re.sub(r'[,$%]', '', text))` |
| Dates | `::text` then `datetime.strptime(text.strip(), "%Y-%m-%d")` |

## Gotchas

- **503 errors** with Scrapling Fetcher → the site might detect curl_cffi. Fall back to `DynamicFetcher` or `StealthyFetcher`.
- **httpbin.org** returns 503 via Scrapling (detected). Use `example.com` for basic connectivity tests instead.
- **Timeout units differ**: `Fetcher` timeout is **seconds**, `DynamicFetcher`/`StealthyFetcher` timeout is **milliseconds** (default 30000).
