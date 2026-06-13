# 宏光流水线数据采集方式清单

> 2026-06-13 更新
> 分类：API（有官方接口）/ 爬取（网页解析）/ 未接入（无免费源）

---

## 一、API（官方接口，稳定可靠）

| # | 数据 | 接口 | 报告 | 函数位置 | 说明 |
|---|------|------|------|---------|------|
| 1 | **FRED宏观指标** | `api.stlouisfed.org/fred/series/observations` | 宏观/贵金属 | macro_pipeline.py → `fetch_fred()` | 需API Key(`FRED_API_KEY`)，75个经济系列 |
| 2 | **EIA原油库存/SPR/产量/开工率** | `api.eia.gov/v2/petroleum/stoc/wstk` | 能源 | energy_weekly.py → `fetch_eia_energy()` | 需API Key(`EIA_API_KEY`)，6个实时端点 |
| 3 | **EIA OPEC产量预测** | `api.eia.gov/v2/steo` | 能源 | opec_data.py → `fetch_eia_opec()` | 同上Key，STEO月度预测 |
| 4 | **Yahoo期货价格** | `query1.finance.yahoo.com/v8/finance/chart` | 所有报告 | macro_pipeline.py → `fetch_yahoo_futures()` | 无需Key，指数退避防429 |
| 5 | **Yahoo外汇/VIX** | 同上 | 宏观 | macro_weekly.py 通过 `gv_yf()` 读取 | 代码 EURUSD=X, USDJPY=X, CNH=X, ^VIX |
| 6 | **Tushare中国期货** | `api.tushare.pro` (POST) | 中国农业 | agri_weekly.py → `fetch_china_futures()` | 需Token(`TUSHARE_TOKEN`)，仅交易日 |
| 7 | **Open-Meteo降水/温度** | `api.open-meteo.com/v1/forecast` | 国际农业 | data_scrapers.py → `fetch_openmeteo_precip()` | **完全免费，无Key**，5个农业区坐标 |
| 8 | **AKShare中国宏观** | 本地Python库 | 宏观 | macro_weekly.py → `fetch_cn_macro()` | pip install akshare，无Key |
| 9 | **Tushare社融(sf_month)** | `api.tushare.pro` → `pro.sf_month()` | 宏观 | 待集成(积分不足) | 需2000积分(当前120)，接口名sf_month，文档doc_id=310 |
| 10 | **Finnhub财经新闻** | `finnhub.io/api/v1/news` | 能源/地缘 | macro_pipeline.py → `fetch_finnhub()` | 需API Key(`FINNHUB_KEY`) |
| 11 | **AGSI+欧洲天然气库存** | `agsi.gie.eu/api` | 能源 | macro_pipeline.py → `fetch_agsi()` | 需API Key(`AGSI_KEY`) |
| 12 | **Cotdata.net CFTC持仓** | `cotdata.net` demo接口 | 贵金属/农业 | macro_pipeline.py → `fetch_cot()` | 目前用公开demo，后续需关注稳定性 |
| 13 | **FedWatch降息概率** | `oddpool.com` | 宏观 | macro_pipeline.py → `fetch_fedwatch()` | 网页API，不挑用户代理 |
| 14 | **EIA weather 天气** | `api.eia.gov/v2/weather` | 宏观(备用) | macro_pipeline.py → `fetch_weather()` | 同上EIA Key |
| 15 | **日本e-Stat宏观** | `api.e-stat.go.jp` | 宏观(备用) | macro_pipeline.py → `fetch_estat()` | 需Key(`ESTAT_API_KEY`)，国内可能慢 |

### AKShare 中国宏观函数表

| 函数 | 获取数据 | 最新值(2026-06-12) |
|------|---------|-------------------|
| `ak.repo_rate_query()` | DR007 (FR007) + FR001/FR014 | 1.47% |
| `ak.macro_china_shibor_all()` | SHIBOR全期限(ON/1W/1M/1Y) | 1W=1.45% |
| `ak.macro_china_lpr()` | LPR 1Y / LPR 5Y | 3.0% / 3.5% |
| `ak.macro_china_reserve_requirement_ratio()` | 存款准备金率(大/中小金融机构) | 9.5% |
| `ak.macro_china_shrzgm()` | 社会融资规模 | ⚠️ SSL握手失败(2026-06)；改用Tushare `sf_month`(需2000分) |

---

## 二、爬取（网页解析，无官方API）

| # | 数据 | 目标URL | 报告 | 函数位置 | 爬取方法 |
|---|------|---------|------|---------|---------|
| 1 | **USDA作物优良率** | `usda.library.cornell.edu/concern/publications/8336h188j` | 国际农业 | data_scrapers.py → `fetch_usda_crop_condition()` | **两步：①爬Cornell页面找最新PDF链接 → ②下载PDF用pdfplumber解析表格**。需`pip install pdfplumber`。 |
| 2 | **BDI波罗的海干散货运价** | `investing.com/indices/baltic-dry` | 国际农业 | data_scrapers.py → `fetch_bdi()` | **requests+BeautifulSoup，按data-test属性提取**价/涨跌幅/前收。VPS直连失败(Investing.com反爬)，本地代理可通。 |
| 3 | **Baker Hughes钻机数** | `rigcount.bakerhughes.com` | 能源 | data_scrapers.py → `fetch_baker_hughes()` | **VPS上用curl绕过Cloudflare→BeautifulSoup解析HTML表格**。Python requests被CDN拦截(403)，curl可通。但curl有时被TLS阻断(exit code 92)，不稳定。 |
| 4 | **OPEC MOMR月报**(备用) | `momr.opec.org/pdf-download` | 能源 | opec_data.py → `fetch_opec_momr()` | **Scrapling StealthyFetcher**过Cloudflare turnstile，约20s。目前没用(主用EIA STEO)。 |
| 5 | **NOAA降水** | `cpc.ncep.noaa.gov` | 国际农业(备用) | data_scrapers.py → `fetch_noaa_precip()` | **已废弃**。CPC网站结构变更导致404，已改为Open-Meteo API。 |
| 6 | **USDA出口检验** | `ams.usda.gov/mnreports/wa_gr101.txt` | 国际农业 | data_scrapers.py → `fetch_usda_export_inspections()` | **直接请求TXT文件，正则解析**。美湾谷物出口数据，网站无反爬。 |

### 爬虫技术对比

| 技术 | 适用场景 | 示例 | 成功率 |
|------|---------|------|--------|
| **requests + BeautifulSoup** | 无反爬的静态页面 | USDA出口TXT, BDI(本地) | 高 |
| **curl subprocess + BeautifulSoup** | Cloudflare拦截requests但放过curl | Baker Hughes(VPS) | 中(TLS有时断) |
| **PDF下载 + pdfplumber解析** | USDA/Cornell托管PDF | USDA优良率 | 高 |
| **Scrapling StealthyFetcher** | Cloudflare turnstile高强度反爬 | OPEC MOMR | 中(20s慢) |

---

## 三、未接入（无免费数据源）

| # | 数据 | 原因 | 潜在付费方案 |
|---|------|------|-------------|
| 1 | **美湾港口库存** | 无公开免费API | Platts/S&P Global |
| 2 | **南美结转库存** | 无公开免费API | USDA FAS付费订阅 |
| 3 | **中国油厂压榨率** | 卓创/钢联付费 | 卓创数据(¥5000+/年) |
| 4 | **豆粕/玉米商业库存** | 同上 | 同上 |
| 5 | **生猪能繁存栏** | 农业部月度数据，滞后 | 涌益咨询/钢联 |
| 6 | **USDA出口销售(周度)** | USDA FAS需FTP订阅 | 免费：USDA出口检验(TXT)已替代 |
| 7 | **波罗的海BDI** | Investing.com有反爬 | 可换Yahoo Finance ^BDI |
| 9 | **中国DR007/社融/MLF** | AKShare已替代DR007/LPR/存准率；Tushare `sf_month` 需2000积分 | Tushare Pro升级积分 |
| 10 | **NOAA CPC降水** | 网站结构调整404 | Open-Meteo已完美替代 |

---

## 四、数据流向图

```
API源                             爬虫源
─────────────────                ─────────────────
FRED (75系列) ──┐                 USDA PDF ──┐
EIA (6端点) ────┤                 TXT文件 ────┤
Yahoo (15品种) ─┤                 curl+BS4 ───┤
Tushare (10品) ─┤                 Scrapling ──┤
AKShare (5函数) ─┤                             │
Open-Meteo ──────┤                             │
Finnhub ─────────┤                             │
cotdata.net ─────┤                             │
                 │                             │
                 ▼                             ▼
          ┌──────────────┐
          │  macro_pipeline.py  │  → CSV文件
          │  (每日采集)         │
          └──────────────┘
                 │
                 ▼
          ┌──────────────────────┐
          │  报告脚本            │  → Markdown报告
          │  macro/energy/       │  → QQ邮件
          │  metals/agri/agri_cn │
          └──────────────────────┘
                 │
                 ▼
          ┌──────────────┐
          │  data_scrapers.py   │  → 报告内联调用
          │  (实时爬取)         │     (USDA/BDI/BH)
          └──────────────┘
```

---

## 五、安装/依赖

### Python包
```bash
pip install pandas requests python-dotenv akshare pdfplumber beautifulsoup4
pip install scrapling    # OPEC备用爬虫
pip install tushare      # 中国期货
```

### 系统工具
```bash
# VPS需要curl
apt install curl -y
```

### API Key（存.env或环境变量）
```
FRED_API_KEY=...
EIA_API_KEY=...
TUSHARE_TOKEN=...
FINNHUB_KEY=...
AGSI_KEY=...
```
