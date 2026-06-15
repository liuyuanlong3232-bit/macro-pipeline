# Scrapling v0.4.9 — Proxy & API Pitfalls

## 代理配置 (Windows v2rayN)

⚠️ **必须用 dict 传 proxy，不能传字符串。** Scrapling v0.4.9 底层用 curl_cffi，
不接受老的字符串格式。

```python
# ✅ 正确
from scrapling import Fetcher
f = Fetcher()
resp = f.get("https://example.com",
    proxies={"http": "http://127.0.0.1:10808", "https": "http://127.0.0.1:10808"})

# ❌ 错误 — AttributeError: 'str' object has no attribute 'get'
resp = f.get("https://example.com", proxies="http://127.0.0.1:10808")
```

## Fetcher 初始化 (v0.3+ 的弃用警告)

```
WARNING: This logic is deprecated now, and have no effect; It will be removed
with v0.3. Use `Fetcher.configure()` instead before fetching
```

这是无害的弃用警告，不影响功能。`Fetcher.configure()` 需要传递 `huge_tree`、
`adaptive` 等解析器参数，不是用来配代理的。**忽略这个警告即可。**

```python
# 无需调用 configure() — 直接 Fetcher() 就能用
f = Fetcher()
```

## CSS 取值 — 常见坑

```python
# ✅ 正确
resp.css("title").first.text          # 取第一个元素的文本
resp.css("a::attr(href)").getall()    # 取所有链接
resp.css("tr.data-row td::text").getall()  # 取多行数据

# ❌ 错误 — Selectors 对象没有 .text 属性
resp.css("title").text                # AttributeError
```

## 环境差异

| 环境 | 代理 | 命令 |
|------|------|------|
| 本地Windows (v2rayN) | 需要 | `proxies={"http":"http://127.0.0.1:10808", "https":"..."}` |
| VPS (Vultr) | 不需要 | 不加 proxy 参数，直接走公网 |

## 测试命令

```bash
# 快速验证 Scrapling 是否工作
python3 -c "
from scrapling import Fetcher
f = Fetcher()
resp = f.get('https://example.com')
print(resp.css('title').first.text)
"
```
