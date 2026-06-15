# Scrapling实战笔记

## 代理配置（v0.4.9）

⚠️ proxies参数必须是dict，传字符串会崩溃：
```python
# ✅ 正确
Fetcher.get(url, proxies={"http": "http://127.0.0.1:10808", "https": "http://127.0.0.1:10808"})

# ❌ 错误 — AttributeError: 'str' object has no attribute 'get'
Fetcher.get(url, proxies="http://127.0.0.1:10808")
```

Fetcher.configure()在新版v0.4.9中已弃用，不要用。

## CSS取值

```python
# ⚠️ resp.css("title") 返回 Selectors 对象，没有 .text 属性
resp.css("title")          → Selectors (collection)
resp.css("title").first    → Selector (single element)
resp.css("title").first.text  → "Example Domain" ✅
resp.css("title").get()    → "Example Domain"  ✅
resp.css("a::attr(href)").getall() → ["url1", "url2", ...]
```

## Cloudflare绕过（OPEC.org经验）

OPEC官网有Cloudflare，Fetcher返回403。需要用StealthyFetcher：
```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch(
    "https://momr.opec.org/pdf-download/",
    headless=True,
    solve_cloudflare=True,
    block_webrtc=True,
)
# 耗时约15-25秒（Cloudflare求解时间）
```

## EIA API（替代方案）

OPEC数据用EIA STEO API更可靠：
- Series ID: `PAPR_OPEC` (总石油供应)
- 频率: monthly
- 端点: `https://api.eia.gov/v2/steo/data/`
- 需要EIA_API_KEY

## HTTP状态码处理

| 状态码 | 含义 | 应对 |
|--------|------|------|
| 200 | 正常 | 正常解析 |
| 307 | 重定向 | StealthyFetcher自动跟随 |
| 403 | Cloudflare/反爬 | 换StealthyFetcher |
| 503 | 临时限流 | 指数退避重试 |
