# Baker Hughes钻机数调试记录

## 最终方案：AOGR网站（✅ 已接入）

`aogr.com/web-exclusives/us-rig-count/{year}` 提供Baker Hughes周度钻机数据，静态HTML表格，无Cloudflare。

```python
# data_scrapers.py → fetch_baker_hughes()
# 解析 Tailwind CSS div-based 表格（不是 <table> 标签）
# 关键：用 _parse_aogr_rig_cell() 提取 span.tc-tot-curr 的文本
# 返回：{"date": "2026-06-12", "total": 562, "oil": 433, "gas": 121, "misc": 8}
```

**解析陷阱**：AOGR用Tailwind CSS div布局，不是HTML表格。`get_text(strip=True)` 会把 `-1` 和 `562` 合并成 `-1562`。必须用DOM导航找到 `tc-tot-curr` span的直接文本子节点。

**URL**: `https://www.aogr.com/web-exclusives/us-rig-count/2026` (年份自动)

## 其他已尝试的方案（均失败）

| 方案 | 本地(Windows) | VPS(Ubuntu) | 结果 |
|------|-------------|-------------|------|
| requests.Session + UA | 403 Cloudflare | 403 Cloudflare | ❌ |
| Scrapling Fetter + proxy | 403 | — | ❌ |
| curl + UA | 200 ✅(curl可过) | curl 92(TLS阻断) | ⚠️ 本地通、VPS不通 |
| Trading Economics API | — | 410(guest已停) | ❌ |
| FRED搜索 | — | 无钻机系列 | ❌ |

## 根因

Baker Hughes网站(rigcount.bakerhughes.com)使用：
1. Cloudflare CDN/WAF — Python requests无论是否带UA都403
2. TLS指纹检测 — VPS上curl也被阻断(exit code 92)
3. curl本地Windows能通是因为浏览器缓存或TLS指纹不同
