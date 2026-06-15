# Scrapling Proxy & Environment Reference

## Proxy: dict required, not string

Scrapling v0.4.9 requires `proxies=` as a **dict**, not a string:

```python
# ✅ CORRECT
resp = f.get(url, proxies={"http": "http://127.0.0.1:10808", "https": "http://127.0.0.1:10808"})

# ❌ WRONG — AttributeError: 'str' object has no attribute 'get'
resp = f.get(url, proxies="http://127.0.0.1:10808")
```

## Environment variables

`HTTP_PROXY` / `HTTPS_PROXY` env vars work as fallback when not passed explicitly:

```python
import os
os.environ["HTTP_PROXY"] = "http://127.0.0.1:10808"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:10808"
```

## Deprecated API

`Fetcher.configure()` is deprecated and raises `AttributeError` in v0.4.9.
Just instantiate `Fetcher()` directly and pass `proxies=` to `.get()`.

## Local vs VPS

| Environment | Proxy needed | Syntax |
|-------------|-------------|--------|
| Local Windows (v2rayN) | Yes (10808) | `proxies={"http": "...", "https": "..."}` |
| VPS (Ubuntu) | No | Direct access, no proxies arg |

### Auto-detect: 一份代码兼容本地和VPS

```python
import requests
def get_proxy():
    """本地走v2rayN，VPS直连"""
    try:
        r = requests.get("http://127.0.0.1:10808", timeout=1)
        return {"http": "http://127.0.0.1:10808", "https": "http://127.0.0.1:10808"}
    except:
        return None  # VPS或代理未运行时

# 使用
proxies = get_proxy()
r = requests.get(url, proxies=proxies, timeout=15)
```

关键：`requests.get()` 传 `proxies=None` 等同于直连，不会报错。

## Fetcher vs DynamicFetcher vs StealthyFetcher

| Class | Use case | Install required |
|-------|----------|-----------------|
| `Fetcher` | Static HTML, APIs | `scrapling` base |
| `DynamicFetcher` | JS-rendered pages | `scrapling[all]` + Playwright |
| `StealthyFetcher` | Cloudflare protection | `scrapling[all]` + Playwright |

## CSS selector gotchas

- `.css("title").text` → **AttributeError** (Selectors has no `.text`)
- `.css("title").first.text` → ✅ returns first match text
- `.css("a::attr(href)").getall()` → ✅ returns all hrefs

## 503 handling

Scrapling may get 503 from some sites (httpbin.org). Always check `resp.status`
before parsing. If 503, the body is not JSON — catch `orjson.JSONDecodeError`.
