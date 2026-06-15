---
name: macro-financial-pipeline
description: "Build automated multi-source financial/macro/commodity data collection pipelines with cron scheduling, structured storage, and report generation."
version: 1.0.0
author: Hermes Agent
tags: [finance, data-pipeline, cron, macro, commodities, api-integration]
user_preferences:
  naming: "Use official, precise source names matching the data provider's own terminology ('EIA STEO' not 'EIA能源', 'CFTC COT Legacy Format' not 'CFTC持仓')."
  pace: "Step by step — do NOT add multiple data sources without confirmation. The user spends months finding/testing sources."
  accuracy: "Data quality affects trading decisions. Every API value must be verified before entering the pipeline."
  docs: "Check official documentation before implementing an API endpoint. Do NOT guess parameters or symbol formats."
  verifiability: "Every report entry must include both source name and as-of date."
  beginner_mode: "The user is a 小白 (beginner) who explicitly doesn't want to switch platforms or learn new tools. Keep everything in ONE ecosystem. Do NOT suggest installing OpenClaw, adding MCP servers that require debugging, switching to new CLI tools, or any multi-tool architecture. If a feature can't work within Hermes alone, say so honestly rather than proposing a complex workaround."
  initiative: "The user wants me to ACT, not ask. When given a task, build it end-to-end and show the result. Do not pause mid-stream to ask 'should I continue?' The user explicitly said: '你怎么老让我干' (why do you always make ME do it) and '你是超级智能体，只有你不能干的时候再告诉我' (you're a super agent, only tell me when you CAN'T do it). Default to action, show results, let them redirect. Permission-seeking is the wrong default. This was REINFORCED multiple sessions in a row."
  email_legibility: "Email reports use QQ mail HTML rendering. Render Markdown tables as proper HTML `<table>` elements with `<th>`/`<td>` and border styling. Handle both formats: (A) `| 品种 | 价格 |` and (B) `品种 | 价格` (no leading pipe). CRITICAL: strip ALL `|------|------|` separator rows — they render as visible garbage on QQ mobile mail. The charts supplement the tables, NOT replace them — the user explicitly said '数据应该生成表格'."
  historical_data_source: "The user has a local Excel archive at D:\\commodity_research_platform\\export\\merged\\ with 15 years of daily market data (商品价格.xlsx, 宏观经济.xlsx, 期货持仓.xlsx, 能源.xlsx). Import to SQLite as reference tables (price_history, macro_history, cot_history, energy_history) for chart generation. These are static snapshots — NOT live-updated. The daily pipeline CSVs remain the primary source for current values."
---

# Macro Financial Data Pipeline

Class-level skill for setting up automated data collection from financial/macro API sources, storing structured data, and generating daily reports via Hermes cron.

## Trigger Conditions

Use this skill when the user asks to:
- Collect financial/macro/commodity data automatically
- Set up a data pipeline with multiple API sources
- Schedule daily data collection with Hermes cron or system crontab
- Generate daily/weekly market reports (metals, energy, macro, agriculture, asset allocation)
- Connect financial API keys to Hermes's environment
- Deploy a data pipeline to a VPS (Vultr, DigitalOcean, etc.)

### Take Initiative — User's Explicit Demand (Session-Verified, Reinforced x2)

The user WILL get frustrated if you ask "what should I do next" at every step. They said: **"我感觉是你在用我"** (I feel like you're using ME). This was reinforced across multiple sessions — every time I asked permission before acting, the user re-stated their desire for me to just build.

**The correct behavior pattern:** When the user provides a template, data source, or VPS credentials, your ONE job is to BUILD and DEPLOY everything in a single uninterrupted work session. Show the final result. Do not stop midway to ask "should I continue?" — that IS the permission-seeking they hate.

Specifically:
1. **When they give a template, write the generator CODE immediately.** When they give VPS access, UPLOAD and CONFIGURE. When a data source needs testing, TEST IT now.
2. Only stop for a genuine blocker: missing key, paywalled source, impossible data request. Never stop to ask "which one should I do first" — always pick the most impactful next step and execute.
3. Default mode is ACTION. Show results, let them redirect. Permission-seeking is the wrong default.
4. When they say "行呢" or "可以" to a proposal, STOP explaining and START executing.
5. **When multiple reports or data sources need the same treatment, do ALL of them in one pass.** Don't ask "should I do the next one too?" — the pattern has been established, replicate it. The user will stop you if they don't want more.
6. **Never ask "how should I approach this?" when the user has already given you the approach.** That wastes their time and frustrates them. If they provided a template in a text file, start writing the generator.

Every "shall I proceed? / what do you want me to do?" is a wasted turn — and they've told you this twice now.

- Python 3.11+ with `requests`, `pandas`, `python-dotenv`
- Hermes cronjob tool available
- API keys for target data sources (stored in `$HERMES_HOME/.env`)

## Data Sources — API Patterns

### FRED (Federal Reserve Economic Data)

Base URL: `https://api.stlouisfed.org/fred`

Key series IDs:
- `DGS1` / `DGS2` / `DGS10` — Treasury yields (use DGS*, NOT TREAST)
- `DGS30` — 30-Year Treasury Yield
- `FEDFUNDS` — Fed funds rate
- `CPIAUCSL` — CPI
- `PCEPILFE` — Core PCE (ex food & energy)
- `PCE` — Personal Consumption Expenditures
- `DFII10` — 10-Year TIPS Yield (real interest rate)
- `T5YIFR` — 5-Year Breakeven Inflation Rate
- `T10YIE` — 10-Year Breakeven Inflation Rate (NOT T10YIFR)
- `UNRATE` — Unemployment
- `GDP` — GDP
- `PAYEMS` — Non-farm payrolls
- `AHETPI` — Average Hourly Earnings (all employees)
- `CES0500000003` — Average Hourly Earnings (production/nonsupervisory)
- `JTSJOL` — JOLTS Job Openings
- `JTSQUR` — JOLTS Quit Rate (%)
- `T10Y2Y` — Yield curve spread
- `M2SL` — Money supply
- `DTWEXBGS` — Trade-weighted USD index
- `PPIACO` — PPI
- `INDPRO` — Industrial production
- `HOUST` — Housing starts
- `UMCSENT` — Consumer sentiment
- `FYFSD` — Federal Deficit (millions $)
- `CLVMNACSCAB1GQEA19` — Euro Area GDP
- `IRSTCI01EZM156N` — Euro Area Interest Rate (%)

**Pitfall:** `TREAST` series returns price indexes (values in millions), NOT yields. Use `DGS1` for 1-year yield.
**Pitfall:** `T10YIFR` is invalid — use `T10YIE` instead.
**Pitfall:** ISM Manufacturing PMI (`NAPM`, `ISM_MAN`) are NOT freely available via FRED API.

### Alpha Vantage — ⛔ REMOVED from Pipeline

Base URL: `https://www.alphavantage.co/query`
Rate limit: **5 calls/minute free tier** — must `time.sleep(12)` between requests
Free tier limit: **25 calls/day**

Valid symbol mappings:
- `XAUUSD` — Gold spot price ✅
- `XAGUSD` — Silver spot price ✅
- `CL` — WTI Crude Oil ✅
- `GLD` — SPDR Gold Shares ETF ✅
- `SLV` — iShares Silver Trust ETF ✅
- `SPX` — S&P 500 ⚠️ (may return empty)
- `USDX` — USD Index ⚠️ (value may be incorrect)

**Pitfall:** Alpha Vantage uses non-standard symbols. Yahoo Finance symbols (`GC=F`, `CL=F`) do NOT work. Test each symbol individually before adding.
**Pitfall:** GLD/SLV calls consume the same 25/day quota. Adding them means 5 calls/day for gold+silver+oil+GLD+SLV — leave headroom.
**Pitfall:** Alpha Vantage XAUUSD (gold spot) data has significant latency — consistently lags behind real-time markets by ~$15-20. For accurate gold/silver spot prices on a US VPS, use Yahoo Finance GC=F (COMEX gold futures) delivered via Bloomberg infrastructure. On VPS, always prefer Yahoo Futures over Alpha Vantage for precious metals pricing. **DXY index: use Yahoo DX-Y.NYB** (ICE US Dollar Index futures, ~99.8), NOT FRED DTWEXBGS (trade-weighted index, ~120 — different calculation).

### Yahoo Finance Chart API (Futures & Indices)

Base URL: `https://query1.finance.yahoo.com/v8/finance/chart/{symbol}`
No API key needed. Rate limit: ~10 calls/minute (soft).

**403/429 handling — MANDATORY exponential backoff:**
```python
import time, random
for attempt in range(retries):
    r = requests.get(url, params=params, headers=headers, timeout=15)
    if r.status_code == 200:
        return r.json()
    elif r.status_code == 429:
        wait = (2 ** attempt) + random.random() * 2
        time.sleep(wait)
    elif r.status_code == 403:
        time.sleep(5)
```

Valid futures symbols (Yahoo format):
- `GC=F` — COMEX Gold Futures ✅
- `SI=F` — COMEX Silver Futures ✅
- `CL=F` — WTI Crude Oil Futures ✅
- `BZ=F` — Brent Crude Oil Futures ✅
- `NG=F` — Henry Hub Natural Gas Futures ✅
- `ZC=F` — Corn Futures ✅
- `ZS=F` — Soybean Futures ✅
- `ZW=F` — Wheat Futures ✅
- `ZL=F` — Soybean Oil Futures ✅
- `ZM=F` — Soybean Meal Futures ✅
- `CT=F` — Cotton Futures ✅
- `SB=F` — Sugar Futures ✅
- `EURUSD=X` — EUR/USD Exchange Rate ✅
- `^VIX` — CBOE Volatility Index ✅

**Pitfall:** Yahoo is blocked from mainland China. Must route through proxy (v2rayN 10808, Clash 7890).
**Pitfall:** Yahoo uses `^` prefix for indices (VIX, SPX) — URL-encode as `%5E` in GET requests.

### EIA (US Energy)

Base URL: `https://api.eia.gov/v2`

Weekly Petroleum Status (库存数据):
- Path: `/petroleum/stoc/wstk/data/`
- Requires `data[0]=value` parameter (same as STEO)
- Only `series` facet works — other facets may cause empty return

Verified weekly petroleum series IDs:
- `WCRSTUS1` — Commercial Crude Oil Stocks (千桶) ✅ weekly
- `WCESTUS1` — Cushing Crude Oil Stocks (千桶) ✅ weekly
- `WGTSTUS1` — Gasoline Stocks (千桶) ✅ weekly
- `WDISTUS1` — Distillate Fuel Oil Stocks (千桶) ✅ weekly
- `W_EPC0_RP` — Refinery Utilization Rate ⚠️ NOT at wstk endpoint; use `petroleum/refm/refin/` or STEO

Frequencies: `monthly`, `annual` only (NOT `weekly`) for production/supply endpoints

Paths:
- `/petroleum/crd/crpdn/data/` — Crude oil production

EIA STEO (Short-Term Energy Outlook) **requires `data[0]=value` parameter** to return numeric values:
```
/api/v2/steo/data/?api_key=KEY&data[0]=value&facets[seriesId][]=SODTC_US
```

Verified STEO series:
- `SODTC_US` — Total Small-Scale Solar PV Capacity (megawatts)
- `SODTP_US` — Total Small-Scale Solar PV Generation (billion kWh)
- `SOEPGEN_US` — Utility-Scale Solar PV Generation, Electric Power (billion kWh)
- `SOCHGEN_US` — Utility-Scale Solar PV Generation, Commercial (billion kWh)
- `ELICP_US` — Industrial Electricity Retail Sales (billion kWh)
- `NGINCNS_US` — Industrial Natural Gas Consumption (billion cubic feet/month)

**Pitfall:** Without `data[0]=value`, STEO returns metadata only (period, seriesId, unit) — no actual values.

### CFTC COT (Commitments of Traders)

**Preferred source (free, no key, COT Index + Z-Score):** `cotdata.net`
```python
GET https://cotdata.net/api/cot?instrument={CFTC_CODE}&table=legacy
    → Returns { market_name, report_date, open_interest, non_commercial: { long, short, net, cot_index_26w, zscore_26w }, commercial: {...} }
```
Free tier: latest week only, 10 requests/min, no auth needed.

Key CFTC codes:
- `088691` — Gold (COMEX) ✅ COT Index 100 (max bullish)
- `084691` — Silver (COMEX) ✅
- `067651` — Crude Oil WTI (NYMEX) ✅
- `067411` — Crude Oil Brent (ICE) ✅
- `098662` — USD Index (ICE) ✅
- `001602` — Wheat SRW (CBOT) ✅
- `001612` — Wheat HRW (KCBT) ✅
- `002602` — Corn (CBOT) ✅
- `005602` — Soybeans (CBOT) ✅
- `025601` — Sugar #11 (ICE) ✅
- `033601` — Cotton (ICE) ⚠️ (404)
- `073601` — Soybean Oil (CBOT) ⚠️ (429)
- `092691` — Copper (COMEX) ⚠️ (429)
- `112601` — Natural Gas (NYMEX) ⚠️ (429)

**Pitfall:** cotdata.net has 10 req/min limit — batch requests with delays or accept partial coverage.
**Pitfall:** Some codes return 404 (instrument not found) or 429 (rate limited). Filter failed codes silently.

**VIX (CBOE Volatility Index):** Use CFTC ZIP archive (TFF format), NOT cotdata.net:
```
Download: https://www.cftc.gov/files/dea/history/fut_fin_txt_2026.zip
Extract:  FinFutYY.txt
Format:   Traders in Financial Futures (TFF)
```

TFF column mapping (critical — differs from Legacy):
```
[7]  = Open_Interest_All
[8]  = Dealer_Positions_Long_All
[9]  = Dealer_Positions_Short_All
[10] = Dealer_Positions_Spread_All
[11] = Asset_Mgr_Positions_Long_All
[12] = Asset_Mgr_Positions_Short_All
[13] = Asset_Mgr_Positions_Spread_All
[14] = Lev_Money_Positions_Long_All
[15] = Lev_Money_Positions_Short_All
[16] = Lev_Money_Positions_Spread_All
```

**Pitfall:** Legacy format and TFF format have DIFFERENT column index layouts. Do NOT use Legacy column indices for TFF data (VIX, financial futures).

Alternative COT source: CFTC Legacy CSV at `https://www.cftc.gov/dea/newcot/deafut.txt` (no auth, weekly updated Tuesdays)

### AGSI+ (European Gas Storage)

Base URL: `https://agsi.gie.eu/api`
Auth: `x-key` header

Country codes: `DE` (Germany), `NL`, `FR`, `UK` — NOT `EU` (returns empty)
Fields: `gasInStorage` (TWh), `workingGasVolume` (TWh)
**Filling rate is NOT returned directly** — calculate: `gasInStorage / workingGasVolume * 100`

### Finnhub

Free tier endpoints (work without paid subscription):
- `/api/v1/news` — Market news ✅ (returns 100 articles max)
- `/api/v1/calendar/earnings` — Earnings calendar
- `/api/v1/calendar/ipo` — IPO calendar

**Pitfall:** `/api/v1/calendar/economic` returns 403 on free tier — needs paid subscription.
**Pitfall:** Finnhub news is accessible from mainland China (unlike NewsAPI/Yahoo). Preferred news source for China-based setups.

### NOAA CPC (Climate — ENSO / El Niño / La Niña)

**Fully free, no API key needed.** Accessible from China with proxy.

URLs:
- `https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices` — Sea Surface Temp by Nino region ✅
- `https://www.cpc.ncep.noaa.gov/data/indices/wksst8110.for` — Weekly SST data ✅
- `https://psl.noaa.gov/data/correlation/oni.data` — Oceanic Niño Index (1950-present) ✅

ONI interpretation: ONI > +0.5°C = El Niño, ONI < -0.5°C = La Niña, between = Neutral.

**Data format:** Monthly values, space-delimited, one row per year. Parse with numpy/pandas read_table.

### ECB SDW (Eurozone Economics)

Endpoint: `https://sdw-wsrest.ecb.europa.eu/service`
**⚠️ Blocked from China** — SSL errors with v2rayN proxy. Directly accessible from US/EU VPS.

Pre-configured endpoints (in `ecb_config.py`):
- `/data/EXR/D.USD.EUR.SP00.A` — EUR/USD
- `/data/ICP/M.U2.Y.000000.3.INX` — Eurozone HICP
- `/data/FM/B.U2.EUR.4F.KR.MRR_FR.LEV` — ECB Main Refinancing Rate
- `/data/MNA/Q.N.I9.W2.S1.S1.B.B1GQ._Z._Z._Z.S.V.N._T.IX` — Eurozone GDP

FRED alternatives (usable from anywhere):
- `CLVMNACSCAB1GQEA19` — Euro Area GDP
- `IRSTCI01EZM156N` — Euro Area Interest Rate (%)

### OPEC MOMR (Monthly Oil Market Report)

**Blocked by Cloudflare from China** — needs US VPS clean IP.

- **Priority:** Excel appendix (`.xlsx`) over PDF
- **PDF fallback:** Only for text summary / narratives
- **Update:** Monthly, 11th–15th
- URL: `https://www.opec.org/opec_web/static_files_project/media/downloads/publications/MOMR_{Month}_{Year}.pdf`

### CONAB (Brazilian Crops)

**Fully public, no API key.** Needs US VPS (blocked from China).

- Reports in **Portuguese**
- Number format: `.` = thousands separator, `,` = decimal (BRAZILIAN)
- **Must clean** before entering pipeline:
  ```python
  value = raw.replace('.', '').replace(',', '.')  # '1.234,56' → '1234.56'
  ```
- **Update:** Monthly, 10th–15th
- URL: `https://www.conab.gov.br/info-agro/safras/graos`

### Tushare (中国金融数据)

No official free API. Oddpool aggregates CME FedWatch + Kalshi + Polymarket data:

```
Source: https://www.oddpool.com/fed-market-watch
```

Extract via regex from the page HTML:
```python
import re
m = re.search(r'Fed maintains rate.*?([\d.]+)%', page_text)
hold_pct = m.group(1) if m else "?"
```

Current data (June 2026): Maintain rate 99.2%, Hike 25bp 0.8%, Cut 25bp 0.7%

### NewsAPI

Base URL: `https://newsapi.org/v2/everything`
**Pitfall:** `newsapi.org` is often unreachable from mainland China networks. Use Finnhub news as fallback.

## Tushare (中国金融数据)

```python
import tushare as ts
pro = ts.pro_api("your_token")

# 中国宏观（低频，2000积分够用）
pro.cn_cpi(start_m="202601", end_m="202606")       # CPI: nt_val, nt_yoy
pro.cn_pmi(start_m="202601", end_m="202606")       # PMI: PMI010100(制造业PMI)
pro.cn_gdp(start_q="2024Q1", end_q="2026Q1")       # GDP: gdp, gdp_yoy
pro.cn_m(start_m="202601")                          # 货币供应量: m0/m1/m2 + yoy

# 中国农产品期货（2000积分可查）
pro.fut_daily(trade_date="20260612")                # 全市场日线（1075+条/日）
```

Field mappings:
- CPI: `nt_yoy` = national CPI yoy% (e.g. 1.2), `nt_val` = index value (e.g. 101.2)
- PMI: `PMI010100` = Manufacturing PMI (e.g. 51.1 = expansion)
- GDP: `gdp` = nominal GDP, `gdp_yoy` = real GDP yoy%

**Chinese agricultural futures — verified symbols (DCE/CZCE, use `trade_date=` not individual codes):**

```python
df = pro.fut_daily(trade_date="20260612")
# Then filter by regex patterns for each product:

# DCE (大连商品交易所)
r'^C\d\.DCE'      → 玉米 (Corn), close=2351 ✅
r'^CS\d\.DCE'     → 玉米淀粉 (Corn Starch), close=2725 ✅
r'^A\.DCE$'       → 豆一 (Soybean #1), close=4744 ✅  (NOT A\d — matches AG, AO)
r'^B\.DCE$'       → 豆二 (Soybean #2), close=3515 ✅  (NOT B\d — matches BU, BR)
r'^M\d\.DCE'      → 豆粕 (Soybean Meal), close=2941 ✅
r'^Y\d\.DCE'      → 豆油 (Soybean Oil), close=8357 ✅
r'^P\d\.DCE'      → 棕榈油 (Palm Oil), close=9321 ✅
r'^JD\d'          → 鸡蛋 (Eggs), close=4690 ✅
r'^LH\d'          → 生猪 (Live Hog), close=12140 ✅
# CZCE (郑州商品交易所)
r'^SR\d'          → 白糖 (Sugar), close=5315 ✅
r'^CF\d'          → 棉花 (Cotton), close=15765 ✅
r'^OI\d'          → 菜籽油 (Rapeseed Oil), close=9874 ✅
r'^RM\d'          → 菜粕 (Rapeseed Meal), close=2259 ✅
r'^AP\d'          → 苹果 (Apple), close=7698 ✅
r'^CJ\d'          → 红枣 (Red Dates), close=8900 ✅
r'^PK\d'          → 花生 (Peanut), close=8426 ✅
```

**Pitfall:** Don't use `fut_daily(ts_code="C888.DCE")` — the continuous contract code `888` is NOT supported. Use `fut_daily(trade_date="YYYYMMDD")` to get all markets, then filter by regex.

**Pitfall — weekend fallback:** On weekends (Saturday/Sunday), Tushare returns empty because there are no trades. Use `start_date` + `end_date` range query instead of `trade_date` alone. Sort results by trade_date descending and take the most recent entry.

**Pitfall:** `A\\d` matches AG (白银) and AO (氧化铝). Use `^A\\.DCE$` (exact match) for Soybean #1. Same for `B` — `B\\d` matches BU (沥青) and BR (丁二烯橡胶).

**Pitfall:** Tushare uses point-based billing. `fut_daily(trade_date=...)` costs points per query. One call returns all markets (~1075+ contracts). Use a single call and filter programmatically rather than calling per product. This gives each product a marginal cost near zero.

### World Gold Council / Gold.org

**No free API available.** All known endpoints return 404/403. For GLD/SLV holdings data, use alternative sources or manual updates.


## Hybrid Cron Pipeline (Data + LLM Report Generation)

For optimal quality, set up TWO cron jobs:

```
8:00  — 数据采集 cron (Python script — guarantees data accuracy)
9:00  — 报告生成 cron (LLM reads CSVs + template → writes analysis)
```

The 9:00 cron prompt should be self-contained — it tells the agent which CSVs to read, which report template to follow, and where to save output. The agent writes natural language analysis (logic chains, scoring rationale, risk assessment) while data tables come from verified CSV values.

Report schedule (FINAL — user-approved, coordinated with data release times, Beijing time, delivers to QQ email):

| Day | Time | Report | Fresh Data | Cron + Email |
|-----|------|--------|------------|--------------|
| Mon | 09:00 | 宏观周报 | Prior week FRED data | `0 9 * * 1` |
| Thu | 09:00 | 能源周报 | EIA from Wed 22:30 | `0 9 * * 4` |
| Fri | 09:00 | 国际农业 | USDA export from Thu 20:30 | `0 9 * * 4` |
| Fri | 20:00 | 中国农业 | Tushare after market close | `0 20 * * 5` |
| Sat | 09:00 | 贵金属周报 | COT from Sat 03:30 | `0 9 * * 6` |
| Sun | 10:00 | 资产配置总控 | All 6 reports published | `0 10 * * 0` |

**VPS crontab delivery chain** — each report cron chains email sending in the same line:
```bash
# 周六贵金属 → 自动发邮件
0 9 * * 6 root cd /root/hermes-pipeline && python3 metals.py && python3 -c "from send_email import send_report; import glob; r=sorted(glob.glob('/root/hermes-macro-data/reports/metals_weekly_*.md')); send_report(r[-1])" >> /var/log/hermes_reports.log 2>&1
```

Email config: QQ SMTP (smtp.qq.com:465 SSL, authorization code). See `references/email-delivery-pattern.md`.

**Key scheduling logic:**
- Tuesday/Wednesday intentionally left empty — no major data releases those mornings
- Chinese agricultural report goes Friday 20:00 (evening) — after market close at 15:00, Tushare has the complete week's data
- The user explicitly chose TWO reports on Friday (国际农业 09:00 + 中国农业 20:00) to keep them separate thematically
- Report output goes to both file AND email — user reads on phone without accessing VPS

**COT release time detail:** CFTC reports are published US Eastern Time Friday 15:30 = Beijing time Saturday 03:30 (夏令时) or 04:30 (冬令时). The Saturday 09:00 slot catches this data fresh. ⚠️ Not Tuesday — the common misunderstanding is that COT publishes Tuesday, but it publishes Friday US time.

**EIA release time detail:** Weekly Petroleum Status is published US Eastern Time Wednesday 10:30 = Beijing time Wednesday 22:30. The Thursday 09:00 slot catches this data fresh.

### VPS Cron (Non-Hermes, Native Linux)

On a Linux VPS, use native crontab instead of `hermes cron` (no gateway needed):

```bash
# Collection: 8:00 daily
0 8 * * * cd /root/hermes-pipeline && python3 -c "from dotenv import load_dotenv; load_dotenv(); from macro_pipeline import main; main()" >> /var/log/hermes.log 2>&1

# Fixed report generation (pure Python, no LLM):
# Thursday 9:00 — 能源周报
0 9 * * 4 cd /root/hermes-pipeline && python3 energy.py >> /var/log/hermes.log 2>&1
# Saturday 9:00 — 贵金属周报
0 9 * * 6 cd /root/hermes-pipeline && python3 metals.py >> /var/log/hermes.log 2>&1
```

### SSH Key Survival (Windows Reinstall)

Store SSH keys on D: drive so they survive a Windows reinstall:

```bash
mkdir D:\\hermes-ssh
copy %USERPROFILE%\\.ssh\\hermes_vps D:\\hermes-ssh\\id_ed25519
copy %USERPROFILE%\\.ssh\\hermes_vps.pub D:\\hermes-ssh\\id_ed25519.pub
```

Then configure `~/.ssh/config` to reference the D: path:

```
Host vps
    HostName 45.77.126.71
    Port 58234
    User root
    IdentityFile /d/hermes-ssh/id_ed25519
```

This path (`/d/hermes-ssh/...`) works in git-bash/MSYS on Windows.

### Telegram Bot Setup for Report Delivery

```bash
# 1. Create bot: Telegram → @BotFather → /newbot → name → get token
# 2. Get chat ID:
curl -s https://api.telegram.org/botYOUR_TOKEN/getUpdates
# Start a chat with the bot first, then the response will show "chat":{"id":12345,...}

# 3. In cron, set deliver to include Telegram:
cronjob(action='create', ..., deliver='telegram:CHAT_ID', 
        model={'model': 'deepseek/deepseek-v4-pro', 'provider': 'deepseek'})
```

Telegram works from China with proxy (SOCK5/HTTP configured in app settings). Notification delivery is not guaranteed inside China due to push channel blocking — the bot responds when the user opens the app.

## Architecture Pattern

```
~/.hermes/.env              ← API keys (FRED_API_KEY, ALPHA_VANTAGE_API_KEY, etc.)
~/hermes-macro-pipeline/    ← Python scripts
  ├── macro_pipeline.py     ← Main collection script (one function per source)
  ├── generate_report.py    ← Daily report generator
  ├── build_db.py           ← CSV → SQLite daily importer
  └── run_daily.sh          ← Cron wrapper script
~/hermes-macro-data/        ← Output data
  ├── csv/YYYY-MM-DD/       ← CSV files per source per day
  ├── reports/YYYY-MM-DD.md ← Generated daily reports
  ├── hermes.db             ← SQLite database (built by build_db.py)
  └── logs/                 ← Pipeline run logs
```

### SQLite Database Integration

After daily collection, import all CSVs into a single SQLite DB for fast mid-conversation queries:

```bash
# In cron: chain after main collection
python3 macro_pipeline.py && python3 build_db.py
```

The DB lives at `~/hermes-macro-data/hermes.db` with one table per source (table name = lowercase CSV stem). This enables instant queries like "黄金最新价多少" without reading files.

**Benefit:** The agent can answer data questions mid-conversation with `python3 -c` SQL queries — no CSVs to hunt down, no column guessing.

**Core query patterns:**
```python
import sqlite3; from pathlib import Path
db = sqlite3.connect(str(Path.home() / "hermes-macro-data" / "hermes.db"))
# FRED data — latest per indicator
cur = db.execute("""
   SELECT DISTINCT 指標, 數值, 日期 FROM fred_indicators 
   WHERE 日期 = (SELECT MAX(日期) FROM fred_indicators WHERE 指標 = '聯邦基金利率')
   ORDER BY 指標
""")
# COT — sort by net position
cur = db.execute('SELECT 品種, "投機淨持倉", "COT Index(26W)" FROM cotdata ORDER BY "投機淨持倉" DESC')
# Futures — latest prices
cur = db.execute('SELECT 品種, 最新價 FROM yahoo_futures ORDER BY 最新價 DESC')
```

**Pitfall — MCP SQLite on Windows encoding:** Building an MCP server in Python to expose SQLite as a tool fails on Windows due to UTF-8 encoding issues with stdio transport. The error `'utf-8' codec can't decode byte 0xb6` comes from Windows console encoding. Workaround: skip MCP and use direct Python SQL queries via `terminal()` instead — it's faster (no handshake protocol) and more reliable.

## Chart Generation & Email Embedding

For reports with visuals, generate matplotlib charts and embed them as base64 images directly in the HTML email body (no attachments needed):

```bash
# Live on VPS:
python3 charts.py          # Generates 8 chart PNGs to charts/ dir
python3 run_report.py metals  # charts → report → embed → email
```

**charts.py** generates up to 8 chart types from SQLite data (both daily snapshot + 15-year history tables):

| Chart | Source | Description |
|-------|--------|-------------|
| `cot_net.png` | cotdata (current) | 投机净持仓 horizontal bar |
| `cot_index.png` | cotdata (current) | COT Index 0-100 with extreme zones |
| `cot_long_short.png` | cotdata (current) | Long vs short side-by-side |
| `fred_trends.png` | macro_history (15yr) | Fed rate, CPI, unemployment, 10Y yield, TIPS yield over time |
| `gold_price.png` | price_history (15yr) | 3-panel: all-time, 3yr, 1yr |
| `silver_price.png` | price_history (15yr) | Silver with 50/200-day MA |
| `gold_silver_ratio.png` | price_history (15yr) | Ratio with long-term mean line |
| `cot_net_history.png` | cot_history (15yr) | Gold COT net position over time |

**Historical data cleaning pattern** — price_history from Excel contains occasional outlier values (gold at $397 during COVID). Apply range filters:
```python
cleaned = [(r[0], float(r[1])) for r in rows if 1000 < float(r[1]) < 6000]  # gold
cleaned = [(r[0], float(r[1])) for r in rows if 5 < float(r[1]) < 200]      # silver
```

**send_email.py** (enhanced version):
- Embeds charts as `data:image/png;base64,...` in the HTML body
- **Table rendering: `|` separators stripped → use Chinese spacing.** Mobile QQ mail renders `|` visibly, which looks bad. Convert table rows to `　`-delimited text lines.
- `send_alert()` function for key-level alerts (plain text)
- QQ SMTP: host=smtp.qq.com, port=465, SSL, auth via authorization code
- Chart type param controls which charts to include:
  - `macro`: FRED trends chart only
  - `metals`: gold_price + silver_price + gold_silver_ratio + cot_net_history + cot_net + cot_index (6 charts)
  - `energy`: cot_net + cot_index (2 charts)
  - `""`: no charts (agri, allocation)

### Chart Quality — Y-Axis & Label Positioning (Session-Verified Fixes)

From the 2026-06-13 session where 15-year gold data was first charted:

1. **Outlier cleaning is CRITICAL.** The user's local Excel export `D:\commodity_research_platform\export\merged\商品价格.xlsx` contains ~31 rows where Yahoo returned implausible gold values ($397-$444 during 2026, instead of the actual $4000+ range). These are likely decimal-shifted exports. Always apply range filters:
   ```python
   cleaned = [(r[0], float(r[1])) for r in rows if 1000 < float(r[1]) < 6000]  # gold
   cleaned = [(r[0], float(r[1])) for r in rows if 5 < float(r[1]) < 200]      # silver
   ```
   Without this, the 15-year chart gets Y-axis compressed to show everything from $0-$5000 and shows as garbage.

2. **Multi-panel charts must have independent Y-axes.** When plotting "all time / 3yr / 1yr" in subplots, set `ax.set_ylim()` per subplot. Matplotlib default is to auto-scale globally which crushes near-term detail:
   ```python
   ymin, ymax = min(y), max(y)
   padding = (ymax - ymin) * 0.15
   ax.set_ylim(ymin - padding, ymax + padding)
   ```

3. **Text labels need fixed positioning** — the user noticed labels appearing "有些在大数字后，有些在大数据前" (labels behind vs in front of data points). Fix:
   ```python
   # Starting value — top-left of line, no bbox
   ax.text(0, y[0], f"${y[0]:,.0f}", fontsize=9, ha="left", va="top", color="#7F8C8D")
   # Latest value — right side with white bbox for legibility
   ax.text(len(y)-1, y[-1], f"${y[-1]:,.0f}", fontsize=11, ha="right", va="bottom",
           color=col, fontweight="bold",
           bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=col, alpha=0.8))
   ```

### agri_weekly.py .env Loading — VPS vs Desktop Paths

**Pitfall verified 2026-06-13:** The `agri_weekly.py` script was loading `.env` from `~/.hermes/.env` (the Hermes default path), which does NOT exist on the VPS. The VPS stores `.env` at `/root/hermes-pipeline/.env`. Fix:

```python
# On VPS:
load_dotenv(Path(os.environ.get("HERMES_HOME", str(Path.home() / "hermes-pipeline"))) / ".env")
```

**General rule for VPS scripts:** The `.env` with API keys (Tushare, etc.) lives beside the Python scripts, NOT in the default Hermes path. Scripts that work locally (`~/.hermes/.env`) will fail silently on VPS because the .env loads with no error, but the keys are empty. Always verify the .env path is correct for the deployment target.

### run_report.py agri_cn — Report Generation Split

`agri_weekly.py` generates BOTH `agri_global_*` and `agri_china_*` reports in a single run. The `run_report.py` config:

```python
"agri": {
    "script": "agri_weekly.py",
    "outfile": "agri_global_{TODAY}.md",
    "chart_type": "",
    "need_charts": False
},
"agri_cn": {
    "script": "",  # ← Intentionally empty: agri_weekly.py already generates both
    "outfile": "agri_china_{TODAY}.md",
    "chart_type": "",
    "need_charts": False
},
```

The `agri_cn` entry has `script: ""` because running `run_report.py agri` already generates both global and China reports. `run_report.py agri_cn` just sends the existing China report to email without re-running the generator.

### HTML Table Rendering — Universal `|` Stripping

The final working approach for QQ mail HTML rendering (verified 2026-06-13):

```python
# 1. Strip leading/trailing | from EVERY line
raw = stripped
while raw.startswith("|"):
    raw = raw[1:].strip()
while raw.endswith("|"):
    raw = raw[:-1].strip()
raw = raw.strip()

# 2. Detect and skip table separator lines
if not raw or set(raw) <= set("-: "):
    continue

# 3. For remaining text, replace ALL | with Chinese full-width space
clean = raw.replace("|", "　")

# 4. Check for ALL markdown separator patterns, not just "|---"
if stripped.startswith("|---") or stripped.startswith("|:---") or stripped.startswith("___"):
    continue
if set(stripped) <= set("|-: "):
    continue
```

This is more robust than only handling `| `-prefixed lines because it catches edge cases where markdown table rows have different whitespace after the pipe, or where the report generator produces non-standard table formatting.

### Email Rendering — QQ Mobile Mail (Session-Verified Fix, Iterated 3x)

This user reads reports on QQ mobile mail. After 3 iterations on 2026-06-13, the FINAL correct approach is:

1. **Intercept ALL `|------|------|` separator rows FIRST** — strip them before any table detection. They render as visible garbage on QQ mobile.

2. **Render Markdown tables as HTML `<table>` elements** — the user explicitly rejected stripped-pipe text: "还是需要表格版的，数据应该生成表格". QQ mobile renders HTML tables correctly; the earlier assumption that CSS stripping would ruin tables was wrong.

3. **Handle both table formats** — with leading `|` (macro/metals/energy) and without (agri reports).

4. **Charts supplement the tables, NOT replace them** — the user reversed their earlier "doesn't need text" decision.

Final detection logic in `send_email.py`:
```python
# Step 1: Check for pure separator rows FIRST
stripped_no_pipe = stripped.replace("|", "").replace("-", "").replace(":", "").strip()
if not stripped_no_pipe and "|" in stripped:
    continue  # skip |------|------| silently

# Step 2: Check if this is a data table row
if "|" in stripped:
    cells_raw = [c.strip() for c in stripped.split("|")]
    real_cells = [c for c in cells_raw if c.strip() and not set(c.strip()) <= set("-: ")]
    if len(real_cells) >= 2:
        is_table_row = True

# Step 3: Extract cells — both formats
cells = [c.strip() for c in stripped.split("|")]
if stripped.startswith("|") and stripped.endswith("|"):
    cells = cells[1:-1]  # Format A
cells = [c for c in cells if c.strip()]

# Step 4: Flush as HTML <table>
def flush_table():
    html = '<table style="border-collapse:collapse;width:100%;margin:10px 0;font-size:12px;">\n'
    for is_header, cell_list in table_rows:
        tag = "th" if is_header else "td"
        bg = "#f8f9fa" if is_header else "#fff"
        fw = "bold" if is_header else "normal"
        row = "<tr>"
        for c in cell_list:
            row += f'<{tag} style="border:1px solid #ddd;padding:6px 8px;background:{bg};font-weight:{fw};text-align:center;">{c}</{tag}>'
        row += "</tr>\n"
        html += row
    html += "</table>\n"
    return html
```

See `references/qq-mail-mobile-legibility.md` for the complete history.

2. **Base64-embedded charts are the primary content.** When charts are present, the Markdown-to-HTML conversion should produce MINIMAL text below the images — the user said "有这个图片版的就不需要文字版了" (if there's a picture version, there's no need for the text version). Actions:
   - Strip Markdown `|---` separator rows entirely
   - Strip `### `-style headers that just repeat what the chart already shows
   - Convert remaining text to compact `<p>` elements, not table rows
   - The full Markdown text remains as the MIME `text/plain` fallback

3. **Chart count vs email size tradeoff.** 8 charts at 150 DPI = ~500KB total base64. Fits QQ mail's limit but can cause SMTP timeout (120s+). If timeout occurs: reduce DPI to 120, reduce charts to the 6 most important for `metals` type, or split into two emails. The `metals` chart_type sends 6 charts (gold_price, silver_price, gold_silver_ratio, cot_net_history, cot_net, cot_index).

4. **HTML structure** — wrap body in `font-family: 'Microsoft YaHei', sans-serif; max-width: 800px;` for proper Chinese font rendering on QQ mobile. Use `data:image/png;base64,...` directly in `<img>` src, NOT as MIME attachments.

**run_report.py** — unified wrapper script chaining all steps:
```python
python3 run_report.py macro      # charts + macro_weekly + email
python3 run_report.py metals     # charts + metals_weekly + email
python3 run_report.py energy     # charts + energy_weekly + email
python3 run_report.py agri       # agri_weekly (no charts) + email
python3 run_report.py agri_cn    # agri_china (no charts) + email
python3 run_report.py allocation # allocation (no charts) + email
```

### Chart Defaults
- matplotlib sans-serif Chinese font via `Noto Sans CJK JP` (install with: `apt-get install fonts-noto-cjk-extra`)
- DPI=150, compact layout, no axis spines top/right
- Each chart file ~30-70KB (fits email attachment limits)
- Charts saved to `~/hermes-macro-data/charts/` directory

## Key Level Monitoring (Alerts)

**monitor.py** — runs every 2h via VPS cron, checks for threshold breaches and sends email alerts:

```python
# configurable thresholds (in the script):
THRESHOLDS = {
    "gold": {"min": 4000, "max": 4500, "label": "COMEX黄金"},
    "silver": {"min": 50, "max": 80, "label": "COMEX白银"},
    "dxy_net": {"min": 0, "max": 10000, "label": "DXY投机净持仓"},
}
COT_EXTREME = {"index": {"min": 5, "max": 95}}
```

- Price threshold breach (gold < 4000 or > 4500)
- COT Index extreme values (>=95 = max bullish, <=5 = max bearish)
- **Deduplication:** Same alert not re-sent within 24h (stored in `alert_log.json`)
- Sends via `send_email.send_alert()` function
- VPS cron: `0 */2 * * * root cd /root/hermes-pipeline && python3 monitor.py`

### VPS Cron — Full Schedule (using run_report.py)

```bash
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Mon 09:00 宏观周报
0 9 * * 1 root cd /root/hermes-pipeline && python3 run_report.py macro >> /var/log/hermes_reports.log 2>&1
# Thu 09:00 能源周报
0 9 * * 4 root cd /root/hermes-pipeline && python3 run_report.py energy >> /var/log/hermes_reports.log 2>&1
# Fri 09:00 国际农业 + 20:00 中国农业
0 9 * * 5 root cd /root/hermes-pipeline && python3 run_report.py agri >> /var/log/hermes_reports.log 2>&1
0 20 * * 5 root cd /root/hermes-pipeline && python3 run_report.py agri_cn >> /var/log/hermes_reports.log 2>&1
# Sat 09:00 贵金属
0 9 * * 6 root cd /root/hermes-pipeline && python3 run_report.py metals >> /var/log/hermes_reports.log 2>&1
# Sun 10:00 资产配置
0 10 * * 0 root cd /root/hermes-pipeline && python3 run_report.py allocation >> /var/log/hermes_reports.log 2>&1
# Every 2h — key level monitoring
0 */2 * * * root cd /root/hermes-pipeline && python3 monitor.py >> /var/log/hermes_monitor.log 2>&1
```

**Pitfall — stale cron script names:** The cron entries MUST use the EXISTING script filenames on the VPS. In this user's pipeline, the report scripts are `macro_weekly.py`, `energy_weekly.py`, `metals_weekly.py`, `agri_weekly.py` (NOT `macro.py`, `energy.py`, `metals.py`, `agri_intl.py`, `agri_cn.py`, `allocation.py` which do NOT exist). After deploying new files, always verify cron runs with `ls /root/hermes-pipeline/*.py` and `cat /etc/cron.d/hermes-reports` side by side. Broken cron = zero reports delivered for weeks.

**Pitfall — stale backup files mislead:** If the pipeline has a `.bak` suffix directory (e.g. `hermes-pipeline.bak/send_email.py`) with old versions, tools like `grep -r` may find the old file and create a false impression that the current pipeline has that tool. Always check the LIVE directory, not backups. The VPS had a `hermes-pipeline.bak/` dir with the only copy of `send_email.py` while the active `/root/hermes-pipeline/` had none — causing email sending to silently fail for every cron run.

**build_db.py** — the daily CSV-to-SQLite importer lives at the pipeline root:
```python
csv_dir = DATA_DIR / "csv" / TODAY
for csv_file in sorted(csv_dir.glob("*.csv")):
    df = pd.read_csv(csv_file)
    table = csv_file.stem.replace("-", "_").replace(" ", "_").lower()
    df.to_sql(table, conn, if_exists="replace", index=False)
```
Deploy to VPS alongside macro_pipeline.py. Chain in cron: `macro_pipeline.py && python3 build_db.py`.

## Report Template Structure

### Daily Report (Precious Metals Focus)

```
📅 贵金属日报 | 2026-06-12
━━━━━━━━━━━━━━━━━━━━━
📊 关键数据速览
  黄金: $4194.96 (-0.59%) | 白银: $67.08 (-0.66%) | 原油(WTI): $89.39
  美债10Y: 4.55% | TIPS: 2.21% | 美元: 120.08
  CPI: 333.98 | 核心PCE: 129.63 | 失业率: 4.3%
  FOMC 6月: 维持 99.2%

## User Preferences (Financial Data Context)

This user is a professional macro/commodity researcher writing reports for WeChat Official Account publication. Observe these rules strictly:

1. **Take initiative — do NOT ask for permission at every step.** The user provides templates, data sources, and API keys. Build the pipeline and generate the reports. Only ask when you hit a genuine blocker (missing API key, paid data source, impossible data request). Asking repeatedly "what should I do next" frustrates the user. Pick the next logical step, do it, show the result, let them redirect if needed. The user explicitly said "我感觉是你在用我" when asked too many questions — default to ACTION. When they give you a template or VPS access, BUILD. Don't ask "are you ready?" — just do it and show results.

2. **Check official docs before implementing.** Never guess API parameters, column indices, or symbol formats. The user noticed: "你有限名字也不严谨，官方文档你也不查". Wrong data affects trading decisions.

3. **Use precise, official naming.** Match the data provider's own terminology. "EIA STEO" not "EIA能源", "CFTC COT Legacy Format" not "CFTC持仓", "cotdata.net" not "COT数据网站", "NOAA CPC" not "NOAA数据". Ambiguous naming confuses the reports.

4. **Data accuracy above all.** Every API value must be verified before entering the pipeline. Log raw responses. Compare against expected ranges. Never fabricate data. If an API call fails, report the failure honestly.

5. **Label every data point with source + date.** Trading decisions depend on knowing when and where the number came from. Omission of either invalidates the data.

6. **All reports output in Simplified Chinese only.** Data pipeline CSVs may use Traditional Chinese column names internally, but ALL user-facing report text (headers, labels, descriptions, analysis) must be Simplified Chinese. Search keywords in code may use Traditional (to match CSV columns), but output display text is Simplified. Use `regex=False` in `str.contains()` when search terms contain parentheses.

7. **Vision / Auxiliary model config** — Two options for chart/table/image analysis:
   - **GLM route (no extra key needed):** Set `auxiliary.vision.provider=glm` and `auxiliary.vision.model=glm-4v-plus` in config.yaml. Note: GLM-4v-plus requires充值 at bigmodel.cn.
   - **OpenRouter route (recommended for beginners, $0.0058/image):** Register at openrouter.ai/keys, get an `sk-or-v1-...` key, then:
     ```bash
     # Write key to .env
     echo "OPENROUTER_API_KEY=sk-or-v1-..." >> ~/AppData/Local/hermes/.env
     # Configure vision
     hermes config set auxiliary.vision.provider openrouter
     hermes config set auxiliary.vision.model openai/gpt-4o-mini
     ```
     The main chat model stays unchanged (DeepSeek/GLM). OpenRouter is ONLY used for vision tasks. Set a $2 monthly budget on openrouter.ai/activity to avoid surprises.

8. **Don't rush.** The user spends months finding and testing data sources. One source at a time. Confirm the current step works before proceeding.

9. **结论先行，不铺垫，不废话，数据带来源日期。** The user wrote the SOUL.md persona requiring: first sentence = conclusion, then supporting data with source + date, then stop. No padding text, no "正如我前面提到的", no unnecessary explanations. If the user asks a question, answer immediately with data — don't explain methodology first.

10. **User is a 小白 (beginner) — one platform, one tool, no complex architecture.** The user explicitly said "不想换软件，用的太多学不过来" and "不换、不堆、不瞎搞". Do NOT suggest installing OpenClaw, adding MCP servers that require debugging, switching to new CLI tools, or any multi-tool architecture. Every recommendation must be executable within Hermes Desktop alone. If a feature can't work within Hermes, say "做不到" honestly rather than proposing a multi-tool workaround.

11. **Built-in auto-verification at report generation time.** Every fixed-template report must end with a "九、数据核验" section that compares all prices against live Yahoo data. Use a `safe_price(val, name, min_v, max_v)` guard that rejects any value outside reasonable bounds (e.g. gold 100-10000, silver 10-200, WTI 10-200). If a value fails the check, log a warning and skip it rather than propagating bad data. The auto-verify section should show ✅ if all checks pass, or ⚠️ with specific discrepancies.

12. **Alpha Vantage XAUUSD gold price is NOT accurate.** It consistently lags ~$15-20 behind Yahoo real-time. On US VPS, always fetch gold/silver from live Yahoo API (GC=F, SI=F, DX-Y.NYB) at report time. Fall back to CSV only if Yahoo fails.

13. **DXY must come from Yahoo DX-Y.NYB** (ICE US Dollar Index, ~99.8), NOT from FRED DTWEXBGS (trade-weighted index, ~120 — different calculation). The FRED series gives a completely different number.

14. **YoY/MoM calculation for FRED data:** Store 13 observations per series (not 5). At report time, sort by date descending: observations[0] is current, observations[1] is prior period (use for mom), find the observation ~12 months back with same month for yoy. Display format: "CPI: 333.98 | 同比 +3.0% | 环比 +0.47%".

15. **Email delivery pattern for VPS cron:** After each report generation, chain email sending in the same cron line.
    ```
    0 9 * * 1 root cd /root/hermes-pipeline && python3 report.py && python3 -c "from send_email import send_report; import glob; r=sorted(glob.glob('/path/reports/*.md')); send_report(r[-1])"
    ```
    QQ SMTP config: host=smtp.qq.com, port=465, SSL, auth via authorization code (not password). Store in .env as EMAIL_HOST/EMAIL_PORT/EMAIL_USER/EMAIL_PASS/EMAIL_TO.

16. **Asset allocation master report** reads the 4 preceding weekly reports and generates a cross-market synthesis. Deploy on Sunday 10:00 (after all 6 reports are published). Report sections: core narrative (1-3 themes), asset strength ranking (top 3), risk ranking (top 3), asset allocation conclusion (🥇🥈🥉), model failure conditions (3 items). Must NOT re-read or repeat the source reports — only synthesize.

17. **Follow the energy report template style for all weekly reports.** Once a template is approved, apply the same structure (summary table → detailed tables per asset → CFTC → scoring → risk watch) to all reports. The templates are saved as reference files.

18. **API key writing pitfall.** NEVER use shell heredocs (`cat << EOF > .env`) for API keys — truncation is silent. Always write keys from a dedicated Python script using `f.write()`, then verify with a raw byte check. When fixing truncated keys, read the file, remove corrupted section, re-append with full values — patching in-place is unreliable with Hermes redaction.

## 🚨 CRITICAL DISCIPLINES — Session-Verified 2026-06-13

### 1. Prompt Templates Are FIXED — Do NOT Modify

The user provided 4 fixed prompt templates stored in `prompts/` directory:
- `全球宏观周度研究报告.txt`
- `贵金属周报.txt`
- `全球农业周报（国际原版）.txt`
- `全球农业周报（中国本土版）.txt`

**NEVER edit these files.** They define EXACT section names, table formats, and footer text. When user says output structure is wrong, ONLY modify the generator Python files (macro_weekly.py, metals_weekly.py, agri_weekly.py, etc.) to match the templates. The templates are the spec; the code implements the spec.

### 2. Report Structure Must Match Templates Exactly

After the fix on 2026-06-13, the verified section structure per report:

| Report | Sections | Match Source |
|--------|----------|-------------|
| macro_weekly | 一~七（本周总结→指标价格→央行经济→资金持仓→中国高频→评分→关注+风险） | 全球宏观周度研究报告.txt |
| metals_weekly | 一~八（总结→价格分析→宏观驱动→COT持仓→产业需求→地缘联动→评分→关注+风险） | 贵金属周报.txt |
| agri_weekly (global) | 一~七（国际市场总结→品种价格→海外供需→COT持仓→天气产区→评分→关注+风险） | 全球农业周报（国际原版）.txt |
| agri_weekly (china) | 一~七（国内市场总结→农品价格→国内政策供需→内盘资金→产业刚需→评分→关注+风险） | 全球农业周报（中国本土版）.txt |

If the user says a report has wrong modules, fix the generator code (patch, not rewrite) — never touch the template txt files.

### 3. Change Log Transparency

After any batch of modifications, output a structured change log (Chinese, before user inspects):

```
修改内容：
macro_weekly.py
  - 改了什么: XXXX
  - 原因: YYYY
metals_weekly.py
  - ...
```

Do NOT make the user reverse-engineer the diff.

### 4. Data Connection Verification After Edits

The `.env` path is the #1 silent failure. After modifying ANY script that uses API keys (Tushare, FRED, etc.):
- Desktop: loads from `~/.hermes/.env`
- VPS: loads from `/root/hermes-pipeline/.env`
- The `agri_weekly.py` .env path was correct on Desktop but silently empty on VPS — caused hours of confusion.

Verification step after edit: run a quick API call test on BOTH environments.

### 5. HTML Table Rendering — Final Verdict After 3 Iterations

*2026-06-13 session: the user went through 3 attempts before settling on the right approach.*

**Correct approach:** Render Markdown tables as HTML `<table>` with proper `<th>`/`<td>` and border styling. Handle both table formats:
- Format A (with leading `|`): `| 品种 | 价格 | 来源 |` — used by macro/metals/energy
- Format B (no leading `|`): `品种 | 价格 | 来源` — used by agri reports

**Critical: ALL `|------|------|` separator rows must be stripped.** Detection logic:
```python
# Intercept separator rows first, before any table detection
stripped_no_pipe = stripped.replace("|", "").replace("-", "").replace(":", "").strip()
if not stripped_no_pipe and "|" in stripped:
    continue  # pure separator — skip
```

**Cell extraction (handles both formats):**
```python
cells = [c.strip() for c in stripped.split("|")]
if stripped.startswith("|") and stripped.endswith("|"):
    cells = cells[1:-1]  # strip leading empty from Format A
cells = [c for c in cells if c.strip()]
```

**Render as proper HTML `<table>`:**
```python
html = '<table style="border-collapse:collapse;width:100%;margin:10px 0;font-size:12px;">'
for is_header, cell_list in rows:
    tag = "th" if is_header else "td"
    bg = "#f8f9fa" if is_header else "#fff"
    row = f"<tr><{tag} style='...'>" + f"</{tag}><{tag} style='...'>".join(cell_list) + f"</{tag}></tr>"
    html += row
html += "</table>"
```

### 6. Never Rewrite Report Generators for Formatting Changes

When the user asks about visuals (charts, email formatting, table layout), ONLY touch:
- `charts.py` — chart generation and appearance
- `send_email.py` — HTML rendering, image embedding

Do NOT touch report generators (macro_weekly.py, metals_weekly.py, energy_weekly.py, agri_weekly.py) for visual/formatting requests. They define content structure and data connections, not layout.

### 7. Always Patch, Never Rewrite

Prefer `patch` over `write_file` for report generators. A rewrite inevitably loses modules, data connections, formatting, or the `.env` path. Patch shows the diff and prevents accidental deletion.

### 8. Superpowers Installed

On 2026-06-13, installed `mechovation/superpowers-hermes` — 8 workflow skills (brainstorming, executing-plans, verification-before-completion, etc.) and a plugin that nudges toward planning/delegation/verification. Plugin enabled, takes effect on next session. The skills live at `~/.hermes/skills/`.

## 🏛️ 宏观环境（全部带日期和来源）
🥇 黄金分析（TIPS实际利率、美元、地缘风险）
🥈 白银分析（金银比）
🌍 地缘政治与风险事件（新闻头条）
```

### Weekly Report Structure (User Template)

When the user requests a full weekly report, use this structure with data annotation requirements:

1. **本周核心事实**
2. **本周关键数据表** — 指标｜当前值｜周变化｜日期｜来源
3. **黄金分析** — 核心逻辑链、最大利多、最大利空
4. **白银分析** — 核心逻辑链、最大利多、最大利空
5. **资金面分析** — CFTC、ETF流向
6. **市场定价程度** — 利空/利好定价、多空拥挤度
7. **周期位置分析** — 1周/1月/3月/6月/1年
8. **评分系统** — 宏观/利率/美元/ETF/CFTC/央行购金/供需
9. **下周关注** — 可能推翻当前逻辑的事件

**User requirement:** 不预测价格目标、不提供买卖建议、不生成行动计划。所有数据标注日期和来源。

## Hybrid Cron Pipeline (Data + LLM Report Generation)

For optimal quality, set up TWO cron jobs:

```
8:00  — 数据采集 cron
        Runs macro_pipeline.py (Python — guarantees data accuracy)
9:00  — 报告生成 cron
        Reads the CSV files + user's report template → generates LLM-written analysis
```

The 9:00 cron prompt should:
1. Load the macro-financial-pipeline skill for data source reference
2. Load the report generator script to read CSVs
3. Receive the user's approved report template as the output format instruction
4. The LLM writes analysis text (logic chains, scoring rationale, risk assessment) while the data tables come from verified CSV values

This gives: Python-guaranteed data accuracy + LLM-written natural language analysis.

### Model Tiering Strategy

Allocate models by task complexity to manage API costs:

| Tier | Model | Cost | Used For |
|------|-------|------|---------|
| **Flash** | `deepseek-v4-flash` | Low (~$0.1/report) | Daily data collection, conversation, quick queries |
| **Pro** | `deepseek-v4-pro` | High (~$1-2/report) | Weekly reports (macro, metals, energy, agriculture, allocation) |

Set per-job model in cron:
```python
cronjob(action='create', name='宏观周报', schedule='0 9 * * 1',
        model={'model': 'deepseek/deepseek-v4-pro', 'provider': 'deepseek'},
        prompt='...')
```

The Hermes model names differ from the API provider names:
- DeepSeek V4 Flash → `deepseek/deepseek-v4-flash`
- DeepSeek V4 Pro → `deepseek/deepseek-v4-pro`
- DeepSeek V3 (legacy) → `deepseek/deepseek-chat` (avoid — this is V3, not V4)

### VPS Fixed Report Generator (No LLM, Pure Python)

For reliability when the user's computer is off, deploy a **pure-Python report generator** on the VPS that reads CSVs and fills templates without calling any LLM. This guarantees 100% data accuracy but uses hardcoded analysis text.

Pattern:
```python
# VPS crontab (independent of Hermes, no gateway needed)
0 9 * * * cd /root/hermes-pipeline && python3 metals.py >> ~/hermes-macro-data/logs/cron.log 2>&1
```

The fixed generator:
- Reads CSVs from `/root/hermes-macro-data/csv/{date}/`
- Outputs Markdown to `/root/hermes-macro-data/reports/`
- Uses `get_val(df, col_like, kw)` with automatic column name detection (handles Chinese/Traditional column names)
- Column mapping is automatic: searches for "品" or "指" for name column, "價" or "值" for value column
- For COT data, column names contain "淨" for net positions, "Index" for COT Index, "Score" for Z-Score
All output is Simplified Chinese.
- **Gold/silver prices come from live Yahoo Finance API (GC=F, SI=F) on VPS, NOT from Alpha Vantage CSV files**, because Alpha Vantage XAUUSD has known latency issues (~$20 lag)
- Fallback: if Yahoo fails, read from the day's commodity_prices.csv as backup
- **Auto-verification:** Every report includes a "九、数据核验" section that compares all prices against live Yahoo data at generation time
- **Safe price bounds:** All numeric values pass through `safe_price(val, name, min_v, max_v)` — any value outside reasonable range is silently skipped and logs a warning (see `references/auto-verify-pattern.md`)
- **DXY must come from Yahoo `DX-Y.NYB`**, NOT from FRED's DTWEXBGS (trade-weighted, ~120) which a different index

See `references/vps-report-generator-pattern.md` for the full code template.

### The Macro Weekly Report Template (Global Macro Focus)

Seven sections, Simplified Chinese output only:

1. 本周核心事实 — US/China/Eurozone/Japan key figures with dates
2. 关键数据表 | 指标 | 当前值 | 日期 | 来源
3. 宏观逻辑链 — 数据变化 → 市场定价 → 资产影响
4. 市场定价程度 — 利空/利好定价评分(0-10)
5. 周期位置 — 1周/1月/3月/6月/1年
6. 评分系统 — 经济增长/通胀/就业/利率/美元（总分 -10~+10）
7. 下周关注事项 — 可能推翻逻辑的事件

**All data entries must include source name AND as-of date.** Data coming from the pipeline CSVs uses Traditional Chinese column names internally. Map to Simplified Chinese for output — never pass raw column names through to the user.

### Template File

A ready-to-fill daily report template is available at:
`skill_view(name="macro-financial-pipeline", file_path="templates/precious-metals-daily-report.md")`

### Data Source Accuracy — Precious Metals Pricing (Session-Verified)

This session discovered that **Alpha Vantage XAUUSD gold spot prices are consistently inaccurate**:

| Source | Gold Price | Silver Price | Notes |
|--------|-----------|-------------|-------|
| Alpha Vantage XAUUSD | $4,194.96 | $67.076 | ~$16-20 behind Yahoo; lags real market |
| Yahoo GC=F (VPS live) | $4,238.80 | $67.974 | Current; matches Bloomberg-class feeds |
| User's trading platform | $4,210.47 | $67.767 | Timestamp not provided; within normal variance |

**Root cause:** Alpha Vantage's XAUUSD endpoint uses a 15-20 minute delayed feed or lower-tier data provider for forex pairs. Yahoo Finance GC=F is delivered via ICE/Bloomberg infrastructure and is more up-to-date on a US VPS.

**Fix applied in VPS metals report generator:** Fetch gold/silver prices LIVE from Yahoo API at report time, NOT from Alpha Vantage CSV files. Alpha Vantage is kept only for GLD/SLV ETF prices (which it handles accurately).

## .env Loading Pattern

Use `HERMES_HOME` to find the correct .env path on any OS:

```python
from pathlib import Path
from dotenv import load_dotenv
import os

env_path = Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))) / ".env"
load_dotenv(env_path)
```

This works because:
- **Windows Desktop**: `HERMES_HOME` = `C:\Users\...\AppData\Local\hermes`
- **Linux VPS**: `HERMES_HOME` unset, falls back to `~/.hermes/`

## Environment Variable Loading Pitfall

**NEVER hardcode `Path.home() / ".hermes" / ".env"`** — on Windows with Hermes Desktop, the actual path is under `AppData\Local\hermes\.env`, not `~/.hermes/.env`. Always use `os.environ.get("HERMES_HOME", ...)`.

## CRITICAL DISCIPLINES — Session-Verified (2026-06-13, reinforced 2026-06-13 pt2)

### 1. NEVER rewrite report generators when asked for formatting/visual changes

The user corrected me sharply: "我让你改排版，没让你改提示词，怎么输出了模块少了" — I rewrote `agri_weekly.py` content (deleted 天气/USDA/评分 modules) when they only wanted chart/email formatting fixes.

**The rule:** When the user asks about visuals (charts, email formatting, table layout), ONLY touch:
- `charts.py` — chart generation
- `send_email.py` — HTML rendering, image embedding

Do NOT touch report generators (`macro_weekly.py`, `metals_weekly.py`, `energy_weekly.py`, `agri_weekly.py`) — these define report STRUCTURE and data connections. Only modify them when the user explicitly asks for content changes.

### 2. Change Log Transparency

After the module deletion, the user demanded: "请你以后把改了什么具体都在对话框告诉我，ok？"

**The rule:** After every batch of modifications, output a structured change log listing each file and what changed (Chinese, specific, actionable). Do NOT make the user reverse-engineer the diff.

### 3. Data Connection Verification After Edits

The user noted: "修改一次，后不会在把数据连接上" — after rewriting agri_weekly.py, Tushare data silently failed because the .env path changed to `~/.hermes/` (Desktop) instead of `/root/hermes-pipeline/` (VPS).

**The rule:** After modifying ANY script, verify .env path, SQLite queries, and API calls before deployment. The .env path is the #1 silent failure — hardcoded `~/.hermes/.env` works on Desktop but fails on VPS.

### 4. Agriculture Reports — No Macro Charts

Agriculture (`agri`, `agri_cn`) must have `chart_type: ""` in `run_report.py`. NEVER attach FRED macro charts to agriculture reports.

### 5. Report Prompt Templates Are FIXED — Do NOT Modify

The user provided 4 fixed prompt templates (macro, metals, agri-intl, agri-china) and said: **"请按这个来，请固定，不要在修改提示词"** — these are saved in `prompts/` directory of the pipeline repo and MUST NOT be edited. All report generators must produce output that matches the template structure EXACTLY — same section names, same table formats, same footnote text. When the user says a report's structure is wrong, fix the GENERATOR code, not the template.

### 6. Email Table Rendering — Handle Both Markdown Formats

The email renderer in `send_email.py` must handle two table formats:
- **Format A (with leading |):** `| 品种 | 价格 | 来源 |` — macro/metals/energy
- **Format B (no leading |):** `品种 | 价格 | 来源` — agri reports

Detection (verified 2026-06-13):
```python
if "|" in stripped:
    cleaned = stripped.replace("|", "").replace("-", "").replace(":", "").strip()
    if cleaned and len(cleaned) > 2:
        cells = [c.strip() for c in stripped.split("|")]
        real_cells = [c for c in cells if c.strip()]
        if len(real_cells) >= 2:
            is_table_row = True
```

Cell extraction (handles both formats):
```python
cells = [c.strip() for c in stripped.split("|")]
if stripped.startswith("|") and stripped.endswith("|"):
    cells = cells[1:-1]  # strip leading empty from Format A
cells = [c for c in cells if c.strip()]
```

Then render as proper HTML `<table>` (not plain text with stripped pipes).

### 7. FRED Chart — Show 3 Years, Not 15

The macro report's chart must show ~3 years. Implement via SQL LIMIT:
```python
rows = db.execute(
    "SELECT date, value FROM macro_history WHERE indicator=? AND value IS NOT NULL ORDER BY date DESC LIMIT 1100",
    (name,)
).fetchall()
rows = list(reversed(rows))
```

User rejected 15-year macro charts: "宏观数据图不需要十五年的".

### 8. Report Rewrite Protocol — Preserve ALL Existing Sections

When modifying a report generator, FIRST read the original file completely and identify all sections. Never delete sections unless explicitly requested. Use `patch` (not `write_file`) for all report generator modifications so the diff is visible and prevents accidental section loss.

## Data Source Architecture — Three-Tier Classification

*Session-verified 2026-06-13: the user identified that many data items were listed as "无免费源" when CSV/Excel downloads exist.*

All data sources fall into one of three tiers. **Check all three before declaring a data item unavailable:**

### Tier 1: API (Official Interfaces)
Preferred when available. Stable, documented, automatic. Before implementing ANY new API, search for the OFFICIAL documentation page. The user's rule: "api官方文档你有事也要查询" (you need to look up the official API docs). Do NOT guess parameters or series IDs.

### Tier 2: Web Scraping (No Official API)
Use when Tier 1 is unavailable but data is public on a web page. Success rate: Static HTML requests > Scrapling Fetcher > curl subprocess > StealthyFetcher.

### Tier 3: CSV/Excel/File Download
**Often overlooked but frequently the best option.** Government/exchange websites frequently provide CSV/Excel/PDF downloads of the same data. Anti-bot measures don't apply to direct file requests. Examples: Baltic Exchange BDI CSV, Baker Hughes rig count report page, USDA AMS Gulf port grain stocks CSV, CONAB Brazil crop data CSV, CNGOIC China crush rate PDF.

Before declaring "no free source," search for CSV/Excel downloads at the source's website.

## ⚠️ Cron Architecture: VPS > Hermes Local (Revenue-Saving Critical)

*Session discovery 2026-06-13: the user was paying for DeepSeek V4 Pro on 6 Hermes local cron jobs that duplicated free VPS Python scripts.*

| Cron System | What It Runs | Cost | Status |
|------------|-------------|------|--------|
| VPS system cron | `python3 run_report.py` | **Free** | ✅ Active |
| Hermes local cron | LLM writes reports | **$$$** | ❌ **STOPPED 2026-06-13** |

**Fix applied:** All 6 Hermes local report-generating cron jobs removed. Only the data-collection cron (cheap Flash) remains.

**Rule:** Weekly reports are generated by VPS system cron via Python scripts (no LLM cost). When deploying a pipeline to VPS with its own crontab, review and remove Hermes-local cron jobs that duplicate it.

## Model Pricing &amp; Token Management

### MiMo Token Plan vs DeepSeek Pay-as-you-go

| Model | Plan | Monthly Cost | Credits/Tokens | Intelligence Score |
|-------|------|-------------|----------------|-------------------|
| MiMo 2.5 Pro | MiMo Token Plan Lite | ¥39 | 41亿 Credits | 86 |
| MiMo 2.5 Pro | MiMo Token Plan Standard | ¥99 | 110亿 Credits | 86 |
| DeepSeek V4 Flash | Pay-as-you-go | ~¥12/mo | ~85M tokens | 57 |
| DeepSeek V4 Pro | Pay-as-you-go | ~¥36-40/mo | ~85M tokens | ~51 |

**Key insight:** MiMo 2.5 Pro and DeepSeek V4 Pro are the same price ($0.435/$0.87 per M tokens) but MiMo scores much higher (86 vs 51). The Token Plan ¥39/mo is great value for light use but heavy code refactoring can consume it in ~5 days.

### Credit Consumption Rules (MiMo Token Plan)

| Model context | Multiplier | 1 token = |
|--------------|------------|-----------|
| MiMo-V2-Omni 256K | 1x | 1 Credit |
| MiMo-V2.5-Pro 256K | 2x | 2 Credits |
| MiMo-V2.5-Pro 1M | 4x | 4 Credits |

**Night discount:** 0:00-8:00 Beijing time = 0.8x multiplier.

### VPS Heremes Config — Path Mismatch Pitfall

The VPS Hermes instance has HERMES_HOME set to `/root/hermes-pipeline`, NOT the default `~/.hermes/`. This means:

```bash
# Config is here, NOT in ~/.hermes/:
hermes config → reads from /root/hermes-pipeline/config.yaml
# .env is here:
hermes config env-path → /root/hermes-pipeline/.env
# Skills go here:
/root/hermes-pipeline/skills/  (NOT /root/.hermes/skills/)
```

**Always use these paths on VPS:** config.yaml, .env, and skills are all under `/root/hermes-pipeline/`. The `~/.hermes/` directory may not exist or have empty files.

### VPS SSH Connection

**The correct SSH key is `C:\Users\Administrator\.ssh\id_rsa`, NOT `/d/hermes-ssh/id_ed25519`.**

The `/d/hermes-ssh/id_ed25519` key exists but the VPS does NOT accept it. The `id_rsa` key (one stored in the default `~/.ssh/` on Windows) is the one in VPS's `authorized_keys`.

SSH config alias:
```
Host myvps
    HostName 45.77.126.71
    Port 58234
    User root
    IdentityFile C:\Users\Administrator\.ssh\id_rsa
```

### VPS Timezone Fix

VPS defaults to UTC, but data releases and report generation should run on China time (UTC+8):

```bash
timedatectl set-timezone Asia/Shanghai
```

After applying, `date` shows correct Beijing time. Cron entries remain at the same numeric values but now execute at China time instead of UTC.

### QQ Bot Integration

QQ Bot is the preferred mobile interface in China (Telegram is blocked). Hermes supports QQ Bot natively.

**Key configuration files:**

```yaml
# /root/hermes-pipeline/config.yaml (NOT ~/.hermes/config.yaml)
platforms:
  qq:
    enabled: true
    extra:
      app_id: "1904159904"
      client_secret: "your-secret"
      markdown_support: true
      dm_policy: "open"
      group_policy: "open"
```

```bash
# /root/hermes-pipeline/.env
QQ_APP_ID=1904159904
QQ_CLIENT_SECRET=your-secret
QQ_ALLOW_ALL_USERS=true
```

**IMPORTANT configuration format:** The platform key is `qq` NOT `qqbot`. The credentials go under `extra:` NOT directly under the platform. Environment variable names are `QQ_APP_ID` and `QQ_CLIENT_SECRET` (not `QQ_APP_SECRET`).

**Limitations:** 
- Monthly proactive messages: 4 per user
- Passive messages (reply to user): Unlimited
- Support: Markdown, images, files
- Sandbox mode: Test in designated QQ group first

**Gateway startup:**
```bash
nohup hermes gateway > /var/log/hermes_gateway.log 2>&1 &
hermes gateway status  # Check connection
```

**Pairing first user:**
```bash
# User sees pairing code in their QQ chat
hermes pairing approve qqbot PAIRING_CODE
```

### Chart Design — Separate Independent Charts

The user rejected multi-indicator composite charts. Each major indicator gets its OWN chart:

| Chart | Indicator | Color |
|-------|-----------|-------|
| `fred_fed_rate.png` | 联邦基金利率 | #E74C3C |
| `fred_cpi.png` | 美国CPI | #3498DB |
| `fred_10y.png` | 美国10年国债收益率 | #F39C12 |
| `fred_tips.png` | 10年TIPS收益率 | #9B59B6 |

Each chart: `figsize=(12, 4)`, independent Y-axis, start/end annotations with white bbox.

**send_email.py sends 4 separate charts in the macro report email.**

## Pitfalls &amp; Debugging

### API Key Writing — Never use heredocs

**NEVER write API keys to .env using shell heredocs** (`cat << 'EOF' >> .env`). The keys get silently truncated to `*** ` and the pipeline silently fails for hours.

**Correct pattern:**
```python
with open(env_path, 'a') as f:
    f.write(f'FRED_API_KEY={actual_full_key}\n')
```

**Always verify key length** after writing — Hermes may redact in display, so check programmatically:
```python
with open(env_path, 'rb') as f:
    raw = f.read()
for key_name in ['FRED_API_KEY', 'ALPHA_VANTAGE_API_KEY']:
    idx = raw.find(key_name.encode())
    if idx >= 0:
        val = raw[idx:idx + len(key_name) + 40]  # peek past the key
        print(f'{key_name}: {len(val)} chars')
```

### Proxy Detection (China Networks)

When running on a Windows machine with v2rayN, Clash, or similar proxy tools:
- **Python `requests` does NOT use system proxy by default** — must set `HTTP_PROXY` / `HTTPS_PROXY` env vars
- Common proxy ports: `127.0.0.1:10808` (v2rayN), `127.0.0.1:7890` (Clash), `127.0.0.1:10809`

Add auto-detection at script startup:
```python
if not os.environ.get("HTTP_PROXY"):
    import socket
    for host, port in [("127.0.0.1", 10808), ("127.0.0.1", 7890)]:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.3)
        if sock.connect_ex((host, port)) == 0:
            os.environ["HTTP_PROXY"] = f"http://{host}:{port}"
            os.environ["HTTPS_PROXY"] = f"http://{host}:{port}"
            os.environ["http_proxy"] = f"http://{host}:{port}"
            os.environ["https_proxy"] = f"http://{host}:{port}"
            break
        sock.close()
```

On a VPS (no proxy), this detection finds nothing and the script proceeds without proxy — no change needed.

### Cron Scheduling — Gateway Required

Hermes cron on **local Desktop** requires the Hermes gateway to be running for jobs to fire. If `hermes cron list` shows `⚠ Gateway is not running`, the jobs exist but won't execute.

| Scenario | Cron works? | Fix |
|----------|------------|-----|
| Hermes Desktop (Windows) | ✅ Desktop app handles scheduler internally | No action needed |
| Hermes CLI (Linux VPS) | ❌ Gateway stops cron | Run `hermes gateway run` or use systemd |
| Cron via Linux `crontab` | ✅ Independent of Hermes | Add native cron entries (see VPS deployment guide) |

On a VPS, prefer **Linux crontab** entries instead of `hermes cron`:
```bash
crontab -e
0 8 * * * cd ~/macro-pipeline && python3 macro_pipeline.py >> ~/hermes-macro-data/logs/cron.log 2>&1
```

### Data Source Corrections

**Alpha Vantage Symbols:**
- WTI Crude Oil uses `CL` (not `CL=F`, not `USOIL`)
- Gold uses `XAUUSD` (not `GC=F`)
- Silver uses `XAGUSD` (not `SI=F`)

**AGSI+ Fill Rate:**
The API does NOT return `fillingRate` as a field. Calculate it:
```python
storage = float(item.get("gasInStorage", 0) or 0)
capacity = float(item.get("workingGasVolume", 1) or 1)
fill_rate = round(storage / capacity * 100, 1) if capacity > 0 else 0
```
Country code `EU` returns empty — use specific codes like `DE`, `NL`, `FR`.

### Data Source Verification

After adding a new source, always verify with a quick Python test:
```python
import requests
r = requests.get(url, params=params, timeout=15)
data = r.json()
print(json.dumps(data, indent=2)[:500])
```

### Common Failure Modes

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| `401 Unauthorized` | API key missing or wrong format | Check .env file with raw byte read |
| `403 Forbidden` | Endpoint requires paid tier | Switch to free alternative |
| `500 Server Error` | Invalid API path/params | Check endpoint docs for correct facets |
| Empty response | Wrong symbol/ID format | Test with known-good values first |
| Connection timeout | Network blocked (Great Firewall) | Use alternative source |
| `OperationalError: near "FROM"` | SQL column name with special chars (%, (), space) not quoted | Use double-quotes around column names: `SELECT "日漲跌幅%"`, `SELECT "COT Index(26W)"` |
| No alert emails received | cron script names don't match actual files | `ls /root/hermes-pipeline/*.py` vs `cat /etc/cron.d/hermes-*` side by side |

### API Key Writes

**NEVER use shell heredocs for API keys** — they get truncated. Write keys from a dedicated Python script using `f.write()`.

## VPS Deployment

### Prerequisites

- Ubuntu 22.04+ VPS (1vCPU/1GB RAM minimum for data pipeline; 2GB+ for GBrain)
- SSH key access (copy your public key to `~/.ssh/authorized_keys`)
- Custom SSH port (change from default 22 for security)
- Docker (optional, for GBrain)

### Steps

```bash
# 1. Upload files
scp -P PORT -i KEY -r ~/hermes-deploy/* root@IP:~/hermes-pipeline/
scp -P PORT -i KEY .env root@IP:~/hermes-pipeline/.env

# 2. Install dependencies
pip3 install pandas python-dotenv requests tushare

# 3. Set up directory structure
mkdir -p ~/hermes-macro-data/csv/$(date +%F)
mkdir -p ~/hermes-macro-data/reports

# 4. Native crontab (NOT hermes cron — gateway not running on VPS)
crontab -e
0 8 * * * cd ~/hermes-pipeline && python3 -c "from dotenv import load_dotenv; load_dotenv(); from macro_pipeline import main; main()" >> ~/hermes-macro-data/logs/cron.log 2>&1
```

### SSH Key from Windows to VPS

```bash
# Generate key
ssh-keygen -t ed25519 -f ~/.ssh/hermes_vps -N ""

# Copy public key
cat ~/.ssh/hermes_vps.pub
# → Paste into VPS ~/.ssh/authorized_keys

# SSH config (so you type `ssh vps` not the full IP/port)
cat >> ~/.ssh/config << 'EOF'
Host vps
    HostName VPS_IP
    Port VPS_PORT
    User root
    IdentityFile ~/.ssh/hermes_vps
EOF

# Test
ssh vps "echo connected"
```

### Security Hardening (Required Before Deploying API Keys)

```bash
# Close password login — key only
sed -i 's/^PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^#ChallengeResponseAuthentication yes/ChallengeResponseAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^#PermitRootLogin prohibit-password/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config
systemctl restart sshd

# UFW firewall (if managing via console)
ufw allow PORT/tcp
ufw enable
```

**Pitfall:** Run hardening from a session that stays connected. If you lock yourself out AND your key stops working, you'll need Vultr web console to recover.

**Verify after hardening:** Open a SECOND terminal and test SSH before closing the first one.

### STORING KEYS ON D:\ DRIVE (Windows, Survives Reinstall)

```powershell
mkdir D:\hermes-ssh
copy %USERPROFILE%\.ssh\hermes_vps D:\hermes-ssh\id_ed25519
copy %USERPROFILE%\.ssh\hermes_vps.pub D:\hermes-ssh\id_ed25519.pub
```

Then reference in `~/.ssh/config`:
```
IdentityFile /d/hermes-ssh/id_ed25519
```

## Telegram Bot Notification Setup

For auto-delivery of reports to Telegram (each report cron job can deliver to Telegram):

```bash
# 1. Create bot via @BotFather — get token like 123456:ABCdef_xxx
# 2. Start a chat with your bot (any message)
# 3. Get chat ID:
curl https://api.telegram.org/botYOUR_TOKEN/getUpdates
# The chat ID is under message.chat.id

# 4. Add to cronjob deliver parameter:
cronjob(action='create', ..., deliver='origin,telegram:CHAT_ID')
```

**No authentication needed beyond the bot token.** Works for personal use without any certification or approval.

## Related Skills

- `data-pipeline` — Generic multi-source pipeline pattern (abstract; `macro-financial-pipeline` is the concrete implementation)
- `hermes-agent` — Cron job management, .env configuration

## Linked Files

| File | Purpose |
|------|---------|
| `references/api-endpoints-verified.md` | Exact endpoints, sample responses, and failure modes for every data source tested |
| `references/data-source-status.md` | Complete access audit — what's free, blocked, or needs VPS |
| `references/report-template-patterns.md` | All 5 weekly report templates (metals, energy, macro, agri-intl, agri-china) with section-by-section structure |
| `references/vps-deployment.md` | Full VPS deployment guide (Ubuntu, crontab, systemd, security hardening) |
| `references/qq-bot-integration.md` | QQ Bot configuration and gateway setup on VPS |
| `references/agri-china-weekly-template.md` | China agriculture weekly report template |
| `references/agri-international-weekly-template.md` | International agriculture weekly report template |
| `references/macro-weekly-template.md` | Global macro weekly report template |
| `references/metals-weekly-template.md` | Gold/silver weekly report template |
| `references/vps-metals-report-pattern.md` | VPS metals report generator code pattern (live Yahoo price + fallback to CSV) |
| `references/chart-visualization-standards.md` | Chart formatting standards (Y-axis, labels, QQ mail rendering, data cleaning) — session-verified 2026-06-13 |
| `references/scrapling-web-scraping.md` | Scrapling adaptive web scraping for data sources |
| `references/vps-token-consumption-patterns.md` | Token usage for code refactoring vs normal analysis on VPS |
| `references/fred-api-key-fix.md` | Fix truncated FRED_API_KEY in .env |
| `references/auto-verify-and-panorama.md` | Auto-verify at report generation time + panorama full check + YoY/MoM calc |
| `references/github-sync-workflow.md` | GitHub push → VPS pull sync workflow |
| `references/sqlite-daily-import.md` | SQLite DB import script, cron chain, and sample queries |
| `references/soul-persona-pattern.md` | SOUL.md persona template for quant/research assistant identity |
| `templates/precious-metals-daily-report.md` | Placeholder-based daily report template |
| `references/vps-metals-report-pattern.md` | VPS metals report generator code pattern (live Yahoo price + fallback to CSV) |
| `references/chart-visualization-standards.md` | Chart formatting standards (Y-axis, labels, QQ mail rendering, data cleaning) — session-verified 2026-06-13 |
