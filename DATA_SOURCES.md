# 宏光流水线数据采集方式清单

> 2026-06-13 更新
> 分类：API（官方接口）/ 爬取（网页解析）/ CSV文件（手动下载或直链）/ 未接入

---

## 交底原则

1. **API优先** — 有官方稳定API的优先使用
2. **官方文档为准** — 接任何新API前先查官方文档，不猜系列ID/参数
3. **CSV/Excel批量** — 政府/交易所官网提供CSV/Excel下载的，直接用文件对接，比爬虫稳定
4. **爬虫兜底** — 无反爬的静态页面/PDF用爬虫

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
| 7 | **Tushare社融(sf_month)** | `api.tushare.pro` → `pro.sf_month()` | 宏观 | macro_weekly.py → `fetch_social_financing()` | 需2000积分 ✅ 已接入 |
| 8 | **Open-Meteo降水/温度** | `api.open-meteo.com/v1/forecast` | 国际农业 | data_scrapers.py → `fetch_openmeteo_precip()` | **完全免费，无Key**，5个农业区坐标 |
| 9 | **AKShare中国宏观** | 本地Python库 | 宏观 | macro_weekly.py → `fetch_cn_macro()` | pip install akshare，无Key |
| 10 | **Finnhub财经新闻** | `finnhub.io/api/v1/news` | 能源/地缘 | macro_pipeline.py → `fetch_finnhub()` | 需API Key(`FINNHUB_KEY`) |
| 11 | **AGSI+欧洲天然气库存** | `agsi.gie.eu/api` | 能源 | macro_pipeline.py → `fetch_agsi()` | 需API Key(`AGSI_KEY`) |
| 12 | **Cotdata.net CFTC持仓** | `cotdata.net` demo接口 | 贵金属/农业 | macro_pipeline.py → `fetch_cot()` | 目前用公开demo，后续需关注稳定性 |
| 13 | **FedWatch降息概率** | `oddpool.com` | 宏观 | macro_pipeline.py → `fetch_fedwatch()` | 网页API，不挑用户代理 |
| 14 | **日本e-Stat宏观** | `api.e-stat.go.jp` | 宏观(备用) | macro_pipeline.py → `fetch_estat()` | 需Key(`ESTAT_API_KEY`)，国内可能慢 |

### AKShare 中国宏观函数表

| 函数 | 获取数据 | 最新值(2026-06-12) |
|------|---------|-------------------|
| `ak.repo_rate_query()` | DR007 (FR007) + FR001/FR014 | 1.47% |
| `ak.macro_china_shibor_all()` | SHIBOR全期限(ON/1W/1M/1Y) | 1W=1.45% |
| `ak.macro_china_lpr()` | LPR 1Y / LPR 5Y | 3.0% / 3.5% |
| `ak.macro_china_reserve_requirement_ratio()` | 存款准备金率(大/中小金融机构) | 9.5% |

---

## 二、爬取（网页解析，无官方API）

| # | 数据 | 目标URL | 报告 | 函数位置 | 爬取方法 |
|---|------|---------|------|---------|---------|
| 1 | **USDA作物优良率** | `usda.library.cornell.edu/concern/publications/8336h188j` | 国际农业 | data_scrapers.py → `fetch_usda_crop_condition()` | **两步：①爬Cornell页面找最新PDF链接 → ②下载PDF用pdfplumber解析表格**。需`pip install pdfplumber`。 |
| 2 | **USDA出口检验** | `ams.usda.gov/mnreports/wa_gr101.txt` | 国际农业 | data_scrapers.py → `fetch_usda_export_inspections()` | **直接请求TXT文件，正则解析**。美湾谷物出口数据，网站无反爬。 |
| 3 | **BDI波罗的海干散货运价** | `investing.com/indices/baltic-dry` | 国际农业 | data_scrapers.py → `fetch_bdi()` | **requests+BeautifulSoup**。VPS直连失败(Investing.com反爬)，本地代理可通。 |
| 4 | **OPEC MOMR月报**(备用) | `momr.opec.org/pdf-download` | 能源 | opec_data.py → `fetch_opec_momr()` | **Scrapling StealthyFetcher**过Cloudflare，约20s。主用EIA STEO。 |

### 已废弃的爬虫

| 数据 | 原方法 | 废弃原因 | 新方案 |
|------|--------|---------|--------|
| Baker Hughes钻机数 | curl+BS4 | Cloudflare+TLS不稳定 | **方案见CSV下载** |
| NOAA降水 | requests+BS4 | CPC网站404 | Open-Meteo API |

---

## 三、CSV/Excel文件（手动下载或直链，比爬虫稳定）

> 这些数据有官方CSV/Excel直接下载链接，不需要爬虫，定期下载即可。

| # | 数据 | 下载地址 | 报告 | 方案 | 说明 |
|---|------|---------|------|------|------|
| 1 | **Baker Hughes钻机数** | `https://bakerhughesggi.com/rig-count/` | 能源 | 每周定时请求PDF/HTML静态页 | 报告页面无反爬，比curl绕过Cloudflare稳定 |
| 2 | **BDI波罗的海干散货运价** (替代) | `https://www.balticexchange.com/en/data-and-information/dry-bulk-indices.html` | 国际农业 | 直接下载CSV | 官方数据，无反爬，比Investing.com稳定 |
| 3 | **美湾港口库存** | `https://mymarketnews.ams.usda.gov/` | 国际农业 | USDA AMS公开数据，支持CSV批量导出 | 美湾大豆/玉米/小麦港口周度库存，完全免费无需注册 |
| 4 | **南美结转库存** | `https://www.conab.gov.br/info-agro/safras` | 国际农业 | CONAB官网CSV批量导出 | 巴西大豆/玉米/白糖官方库存数据，完全免费 |
| 5 | **南美结转库存(阿根廷)** | `https://www.magyp.gob.ar/sitio/areas/estimaciones/principal.php` | 国际农业 | 阿根廷农业部公开数据 | 阿根廷大豆/玉米/小麦结转库存 |
| 6 | **中国油厂压榨率/开工率** | `https://www.grainoil.com.cn/` | 中国农业 | 国家粮油信息中心(CNGOIC)周报PDF/Excel | 每周发布全国大豆压榨量/开工率，免费注册 |
| 7 | **豆粕/玉米商业库存** | `https://www.feedtrade.com.cn/` | 中国农业 | 饲料行业信息网公开数据 | 每日更新豆粕/玉米港口库存 |

> **待接优先级**：BDI官方CSV > Baker Hughes报告页 > 美湾库存(USDA AMS) > 南美库存(CONAB) > 压榨率(CNGOIC) > 商业库存

---

## 四、未接入（无免费数据源）

| # | 数据 | 原因 | 潜在付费方案 |
|---|------|------|-------------|
| 1 | **生猪能繁存栏** | 农业部月度数据，更新滞后1-2月 | 涌益咨询/钢联 |
| 2 | **USDA出口销售(周度)** | USDA FAS需FTP订阅 | 免费：USDA出口检验(TXT)已替代 |
| 3 | **社融（AKShare版）** | SSL握手失败 | Tushare sf_month ✅ 已接入 |
| 4 | **NOAA CPC降水** | 网站结构调整404 | Open-Meteo ✅ 已替代 |

---

## 五、技术选型原则

```
有官方API      → 用API（稳）
有CSV下载      → 下载文件（比爬虫稳）
纯静态页面     → requests+BeautifulSoup
PDF报告        → pdfplumber
Cloudflare     → curl 或 换数据源
付费才能拿的   → 留空，标注"待补"
```

### 爬虫技术对比

| 技术 | 适用场景 | 成功率 |
|------|---------|--------|
| **requests + BeautifulSoup** | 无反爬的静态页面 | 高 |
| **PDF下载 + pdfplumber解析** | 报告类PDF | 高 |
| **curl subprocess + BS4** | Cloudflare拦requests | 中 |
| **Scrapling StealthyFetcher** | Cloudflare turnstile | 中(慢) |

---

## 六、数据流向图

```
API源                       爬虫源                    CSV/Excel源
─────────────────           ─────────────────         ───────────────────
FRED (75系列) ──┐            USDA PDF ──┐              Baker Hughes ──┐
EIA (6端点) ────┤            TXT文件 ───┤              波罗的海  ─────┤
Yahoo (15品种) ─┤            BDI ───────┤              USDA AMS ─────┤
Tushare (10品) ─┤            Scrapling ─┤              CONAB ─────────┤
AKShare (5函数) ─┤                        │              CNGOIC ────────┤
Open-Meteo ──────┤                        │              feedtrade ────┤
Finnhub ─────────┤                        │                             │
cotdata.net ─────┤                        │                             │
                 │                        │                             │
                 ▼                        ▼                             ▼
          ┌─────────────────────────────────────────────────────┐
          │  macro_pipeline.py  +  data_scrapers.py  +  manual  │
          │  (每日采集)          (实时爬取)          (文件导入)   │
          └─────────────────────────────────────────────────────┘
                                    │
                                    ▼
          ┌──────────────────────────────────────┐
          │  报告脚本  →  Markdown  →  QQ邮件    │
          │  macro/energy/metals/agri/agri_cn    │
          └──────────────────────────────────────┘
```

---

## 七、安装/依赖

### Python包
```bash
pip install pandas requests python-dotenv akshare pdfplumber beautifulsoup4
pip install scrapling    # OPEC备用爬虫
pip install tushare      # 中国期货+社融
```

### 系统工具
```bash
# VPS
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

---

## 八、接新API的标准流程（自我约束）

1. **先搜官方文档** — 不猜系列ID/参数名称
2. **本地测试** — 先跑一遍确认返回数据结构
3. **再集成** — 写入对应脚本
4. **全报告测试** — 确保不破坏其他数据
