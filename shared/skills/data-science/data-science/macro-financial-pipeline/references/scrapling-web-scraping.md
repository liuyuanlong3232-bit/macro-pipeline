# Scrapling — Adaptive Web Scraping for Data Sources

## Overview

Scrapling (v0.4.9+) is an adaptive web scraping framework that handles anti-bot bypass, stealth headers, and automatic element relocation. Installed on both Desktop (Windows) and VPS (Ubuntu).

## Installation

```bash
pip3 install scrapling
pip3 install browserforge curl_cffi playwright  # core dependencies
```

## API Reference

```python
from scrapling import Fetcher

# Basic GET
f = Fetcher()
resp = f.get("https://example.com")
print(resp.status)                              # 200
print(resp.css("title").first.text)             # "Example Domain"

# With proxy (Windows, behind v2rayN)
resp = f.get("https://httpbin.org/headers",
             proxies={"http": "http://127.0.0.1:10808",
                      "https": "http://127.0.0.1:10808"})

# Without proxy (VPS)
resp = f.get("https://api.example.com/data")

# JSON parsing
data = resp.json()  # parses response as JSON
```

## Pitfalls

1. **Proxy format** — Scrapling uses `curl_cffi` under the hood which expects dict proxies (not string). Use `proxies={"http": "...", "https": "..."}`, NOT `proxies="http://..."`.

2. **Deprecation warning** — `Fetcher()` shows a warning about `configure()` being the new API. Ignore for now until v0.5; the current API still works.

3. **User-Agent stealth** — Scrapling auto-fingerprints browser headers. No manual UA setting needed.

4. **Timeouts** — Default timeout is generous. Set explicit timeout for data source scraping:
   ```python
   resp = f.get(url, timeout=15)
   ```

5. **VPS has no proxy** — calls are direct. On Windows behind v2rayN, always pass `proxies={...}`.
