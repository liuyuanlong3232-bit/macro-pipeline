---
name: scrapling-finance-scraper
version: 1.0.0
description: |
  Use Scrapling (0.4.9+) to scrape financial/commodity/government data sources
  (EIA, CFTC, USDA, NOAA, CME, etc.) with stealth anti-bot bypass and proxy
  support. Handles static HTML, JS-rendered pages, and Cloudflare-protected sites.
  Knows about v2rayN proxy (127.0.0.1:10808) for Chinese network environment.
triggers:
  - "scrape EIA data"
  - "scrape CFTC"
  - "scrape USDA"
  - "scrape NOAA"
  - "scrape financial data with Scrapling"
  - "scrape with proxy"
  - "fetch commodity data"
tools:
  - terminal
  - write_file
  - read_file
mutating: true
---

# Scrapling Finance Scraper

## Contract

This skill guarantees:
- Uses Scrapling's Fetcher/StealthyFetcher with proper proxy configuration
- Handles three site types: static (Fetcher), JS-rendered (DynamicFetcher), Cloudflare-protected (StealthyFetcher)
- Proxy-aware: auto-detects v2rayN (10808), Clash (7890), or uses env HTTP_PROXY
- Returns structured data as CSV/JSON for pipeline consumption
- Each scrape call includes: url, method, proxy config, parser, output format
- Timeout and retry strategy built in

## Phases

1. **Identify the target.** URL + site type (static/JS/Cloudflare) + data format needed.
2. **Choose the right fetcher.**
   - Static: `Fetcher.get(url)` — fast, no browser
   - JS-rendered: `DynamicFetcher.fetch(url, headless=True)` — Playwright browser
   - Cloudflare: `StealthyFetcher.fetch(url, solve_cloudflare=True)` — full stealth
3. **Configure proxy.** 
   - Local (v2rayN): `proxies={'http': 'http://127.0.0.1:10808', 'https': 'http://127.0.0.1:10808'}`
   - VPS: no proxy needed (direct access)
   - Or set env: `HTTP_PROXY=http://127.0.0.1:10808`
4. **Parse with CSS selectors.** Use `resp.css('selector').text` / `.getall()` / `.first.attrs`
5. **Structure output.** Write to CSV or return dict for pipeline.
6. **Error handling.** Catch timeouts, 503, Cloudflare challenges, retry max 3x with exponential backoff.

## Output Format

```python
{
    "source": "EIA/CFTC/USDA/NOAA",
    "url": "https://...",
    "fetched_at": "2026-06-13T17:30:00",
    "data": [{"field1": "value1", "field2": "value2"}, ...]
}
```

## Anti-Patterns

- Using Scrapling when a simple API call works (check for API first)
- Forgetting proxy on local Windows (will timeout behind GFW)
- Using StealthyFetcher for static pages (wastes 5-15s per request)
- Not handling 503/rate-limit responses gracefully
- **Using deprecated `proxies=str` syntax (must be dict in v0.4.9)** — `Fetcher.get(url, proxies="http://...")` crashes with `AttributeError: 'str' object has no attribute 'get'`. Always use `proxies={"http": "...", "https": "..."}`.
- Calling `.css().text` on empty Selectors (crashes — use `.first.text` or `.getall()`)
- Trying `resp.css("title").text` on a `Selectors` object (use `.first.text` or `.get()`)
- Writing Scrapling code that only works on one machine — proxy config differs between local (v2rayN :10808) and VPS (no proxy)
- **Hardcoding proxy when running on VPS** — VPS上 `127.0.0.1:10808` 不存在，会报 `Connection refused`。使用自动检测：

```python
def get_proxy():
    try:
        r = requests.get("http://127.0.0.1:10808", timeout=1)
        return {"http": "http://127.0.0.1:10808", "https": "http://127.0.0.1:10808"}
    except:
        return None  # VPS直连
proxies = get_proxy()
```

## Common Data Sources

See `references/common_sources.md` for full proxy reference, known-good source configurations, CSS selector patterns, and gotchas.

| Source | URL Pattern | Type | Method |
|--------|------------|------|--------|
| EIA API (原油/产量/库存) | API v2: `api.eia.gov/v2/` | API | `requests.get()` |
| EIA Weekly Petroleum | `https://www.eia.gov/petroleum/supply/weekly/` | Static | Fetcher |
| OPEC MOMR PDF | `https://momr.opec.org/pdf-download/` | Cloudflare | StealthyFetcher |
| CFTC COT | `https://www.cftc.gov/dea/newcot/ftp/` | Static | Fetcher |
| USDA WASDE | `https://www.usda.gov/oce/commodity/wasde` | Static | Fetcher |
| **USDA Crop Progress** | `https://usda.library.cornell.edu/concern/publications/8336h188j` | PDF | **pdfplumber (非爬虫)** |
| **Open-Meteo天气** | `https://api.open-meteo.com/v1/forecast` | **API（免费无Key）** | `requests.get()` |
| NOAA ENSO | `https://www.cpc.ncep.noaa.gov/` | Static | Fetcher |
| CME Open Interest | `https://www.cmegroup.com/market-data/volume-open-interest/` | JS | DynamicFetcher |

> **Prefer EIA API over scraping** — EIA has a free v2 API returning clean JSON. Much faster and more reliable than scraping HTML. API Key in `.env` as `EIA_API_KEY`. See `macro-futures-pipeline/references/eia-api-endpoints.md` for endpoints.

## Reference Files

- `references/proxy-and-env.md` — Proxy dict syntax (not string), local vs VPS,
  Fetcher vs StealthyFetcher, CSS selector gotchas, 503 handling

## Example

```python
from scrapling import Fetcher

# Local with proxy (注意: proxies必须是dict, 不能传字符串)
f = Fetcher()
resp = f.get(
    "https://www.eia.gov/petroleum/supply/weekly/",
    proxies={"http": "http://127.0.0.1:10808", "https": "http://127.0.0.1:10808"}
)
# Parse table
rows = resp.css("table.petroleum-table tr.data-row::text").getall()
print(f"Fetched {len(rows)} rows from EIA")
```

## Reference Files

- `references/scrapling-notes.md` — 代理dict语法（不是string）、CSS取值陷阱、Cloudflare绕过（OPEC.org实战）、HTTP状态码处理
