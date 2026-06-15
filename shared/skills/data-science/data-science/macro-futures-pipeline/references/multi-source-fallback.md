# 数据源多级回退策略

当报告数据空缺时，按此顺序尝试每个数据源，记录每个的结果。

## 多源回退链（按优先级）

### 美湾/南美库存
1. EIA API → try `petroleum/stoc/wstk data?facets[duoarea][]=R3P`（PADD 3 美湾）→ 返回空
2. FRED API → search "gulf coast crude stocks" → 无匹配系列
3. 结论：无免费数据源

### Baker Hughes钻机数
1. Python requests → 403 (Cloudflare)
2. curl（VPS）→ TLS阻断，curl exit code 92
3. FRED → 搜索无结果
4. Trading Economics API → guest账号已关停(410)
5. 结论：四种方式全部失败

### BDI波罗的海干散货运价
1. Investing.com 爬虫 → VPS直连超时
2. Yahoo Finance ^BDI → 代码存在但数据不完整
3. 结论：VPS直连不可用

### USDA作物优良率（成功案例）
1. 直接爬usda.gov → 失败(301)
2. Cornell图书馆 `usda.library.cornell.edu/concern/publications/8336h188j` → 拿到最新报告PDF URL
3. pdfplumber解析PDF → 成功提取玉米/大豆优良率
4. 始终稳定的方案

### OPEC产量（成功案例）
1. Scrapling爬OPEC官网 → Cloudflare拦截(403)
2. StealthyFetcher → 能过Cloudflare但太慢(20s+)
3. EIA STEO API → `seriesId=PAPR_OPEC` → 实时返回，1s完成
4. 结论：EIA API为稳定主用方案

### 中国宏观数据（成功案例）
1. FRED → 无中国利率系列
2. Tushare API → 无利率接口(repo/mlf返回40101)
3. AKShare → `repo_rate_query()` + `macro_china_lpr()` → 全部成功
4. 结论：AKShare为唯一免费方案

## 核心理念

```
首选API → 免费第三方API → Scrapling爬虫 → curl替代 → 
如实标注"无数据源"并告知用户原因
```

不要编造数据代替失败结果。
