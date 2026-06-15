# Scrapling数据采集（金融数据源）

## 本地代理配置（Windows + v2rayN）

```python
from scrapling import Fetcher
f = Fetcher()
resp = f.get("https://example.com",
    proxies={"http": "http://127.0.0.1:10808", "https": "http://127.0.0.1:10808"}
)
```

VPS上不需要代理，直连。⚠️ proxies参数在v0.4.9必须是dict，传str会报 `AttributeError: 'str' object has no attribute 'get'`。

## 三种Fetcher选型

| 模式 | 类 | 场景 | 速度 |
|------|----|------|------|
| HTTP静态 | `Fetcher.get(url)` | EIA/CFTC/USDA静态页面 | 快（~1s） |
| JS渲染 | `DynamicFetcher.fetch(url, headless=True)` | CME/交互式图表 | 中（~5s） |
| 反爬 | `StealthyFetcher.fetch(url, solve_cloudflare=True)` | Cloudflare保护站点 | 慢（+5-15s） |

## CSS选择器用法

```python
resp.css("h1::text").first.text           # 第一个h1的文本
resp.css("a::attr(href)").getall()         # 所有链接
resp.css("table tr.data td::text").getall() # 表格数据
resp.xpath('//div[@class="content"]/text()').getall()  # XPath也行
```

⚠️ 不要直接 `.css("title").text` — `Selectors`对象没有`.text`，必须用`.first.text`或`.get()`/`.getall()`。

## 已验证的数据源

| 数据源 | URL | 类型 | 代理 | 结果 |
|--------|-----|------|------|------|
| httpbin.org | https://httpbin.org/headers | 静态 | 需要 | 503 (Scrapling请求头触发) |
| example.com | https://example.com | 静态 | 需要 | ✅ 200 |
