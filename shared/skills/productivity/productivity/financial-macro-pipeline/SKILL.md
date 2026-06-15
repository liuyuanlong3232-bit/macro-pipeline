---
name: financial-macro-pipeline
description: >-
  Build and operate automated financial/commodity macro data pipelines with
  Hermes cron: multi-source data collection, CFTC COT parsing, FRED series
  management, proxy-aware scraping, and daily report generation for precious
  metals, energies, and macro indicators.
version: 1.0.0
author: Hermes Agent
tags:
  - finance
  - macro
  - trading-data
  - pipeline
  - cron
  - precious-metals
  - data-collection
platforms: [linux, macos, windows]
---

# Financial Macro Data Pipeline

Build an automated pipeline that collects macro-economic data, commodity prices, futures positioning (CFTC COT), energy storage data, and news daily — then generates structured reports.

Trigger: user says "set up data collection", "build a macro pipeline", "I need daily [gold/oil/macro] reports", or provides API keys for financial data sources.

## Architecture

```
Hermes cron (daily 08:00)
  ├── FRED (24 macro indicators) ✓ verified
  ├── Alpha Vantage (gold/silver/oil spot + GLD/SLV) ✓
  ├── Yahoo Finance (COMEX/Brent/NG + 9 agri futures) ✓ 429-backoff
  ├── cotdata.net (COT Index+Z-Score, 15 instruments) ✓ recommended
  ├── CFTC TFF ZIP (VIX positioning) ✓ weekly Tue
  ├── Finnhub (20 financial news headlines) ✓
  ├── EIA STEO (solar capacity/generation + industrial) ✓
  ├── AGSI+ (European gas storage by country) ✓
  ├── FedWatch (Oddpool FOMC probabilities) ✓ fallback
  ├── OpenWeather (9 trading center weather) ✓
  └── EIA/USDA/e-Stat (energy/agriculture/Japan) ✓
      ↓
  CSV/JSON storage → Daily report (09:00 cron)
                     ↑ CFTC COT added weekly (Tuesday)
```

## Data Source Setup
## Data Source Setup

### API Keys
Store in `$HERMES_HOME/.env`:
```env
FRED_API_KEY=***...ANTAGE_API_KEY=***
NEWSAPI_KEY=***
OPENWEATHER_API_KEY=***
FINNHUB_API_KEY=***
EIA_API_KEY=***
AGSI_API_KEY=***
USDA_NASS_API_KEY=***
CFTC_COT_ID=***
CFTC_COT_SECRET=***
```

**⚠️ .env path**: Hermes Desktop stores .env at `AppData/Local/hermes/.env`, NOT `~/.hermes/.env`. Always resolve via `HERMES_HOME` env var:
```python
from pathlib import Path
import os
ENV_PATH = Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))) / ".env"
```

**⚠️ Secret redaction**: Hermes auto-masks API keys in tool output with `***`. Use raw binary reads to verify actual file content during debugging: `open(path, 'rb')`.

### Proxy Configuration (Windows/China)
Python's `requests` library does NOT use Windows system proxy by default (v2rayN:10808, Clash:7890). Auto-detect in pipeline scripts at module init time:

```python
import socket
for host, port in [("127.0.0.1", 10808), ("127.0.0.1", 7890)]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.3)
    if sock.connect_ex((host, port)) == 0:
        for var in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]:
            os.environ[var] = f"http://{host}:{port}"
        break
    sock.close()
```
Set ALL FOUR variants (uppercase+lowercase HTTP+HTTPS) for broader library compatibility — `requests` checks uppercase, `urllib` checks lowercase.

### Naming & Rigor Requirements
When building financial data pipelines, the following are MANDATORY:
1. **Check official API documentation** before implementing. Don't guess endpoints or parameter formats.
2. **Use precise names** for financial instruments and data series. "GOLD - COMMODITY EXCHANGE INC." not just "gold". "CFTC Legacy Format" not just "CFTC data".
3. **Verify every data point** before adding it to the pipeline. Run the exact API call, check the returned value makes sense, document the unit.
4. **Document every API call's rate limits** and implement exponential backoff for 429/403 responses.
5. **Data accuracy is critical** for trading decisions — any error in series ID, column offset, or unit conversion directly impacts analysis quality.
6. **Add one data source at a time**, verify it independently, then integrate.



## Key FRED Series for Macro/Commodity Analysis

| Series | Description | Frequency |
|--------|-------------|-----------|
| FEDFUNDS | Federal Funds Rate | Daily |
| CPIAUCSL | CPI (Consumer Price Index) | Monthly |
| PCEPILFE | Core PCE (ex food & energy) | Monthly |
| UNRATE | Unemployment Rate | Monthly |
| PAYEMS | Nonfarm Payrolls | Monthly |
| DGS1/DGS2/DGS10 | Treasury Yields 1Y/2Y/10Y | Daily |
| DFII10 | 10Y TIPS Yield (real rate) | Daily |
| T5YIFR | 5Y Breakeven Inflation | Daily |
| DTWEXBGS | Trade-Weighted USD Index | Weekly |
| M2SL | M2 Money Supply | Monthly |
| PPIACO | PPI Producer Price Index | Monthly |
| INDPRO | Industrial Production | Monthly |
| HOUST | Housing Starts | Monthly |
| UMCSENT | Michigan Consumer Sentiment | Monthly |

## CFTC COT Data

### Sources (two options)

#### Option A: cotdata.net API (RECOMMENDED — cleaner, richer data)
- URL: `https://cotdata.net/api/cot?instrument={CFTC_CODE}&table=legacy`
- **Free tier**: No auth required, latest week only, 10 req/min, full COT Index + Z-Score
- Paid tier: £19/mo for 3-year history, 60 req/min
- Key CFTC codes:
  | Code | Instrument | Exchange |
  |------|-----------|----------|
  | 088691 | Gold | COMEX |
  | 084691 | Silver | COMEX |
  | 067651 | Crude Oil WTI | NYMEX |
  | 067411 | Crude Oil Brent | ICE |
  | 098662 | US Dollar Index (DXY) | ICE |
  | 001602 | Wheat SRW | CBOT |
  | 002602 | Corn | CBOT |
  | 005602 | Soybeans | CBOT |
  | 025601 | Sugar #11 | ICE |
  | 033601 | Cotton | ICE |
  | 073601 | Soybean Oil | CBOT |
  | 092691 | Copper | COMEX |
  | 112601 | Natural Gas | NYMEX |

- Response includes: `non_commercial`(legacy), `managed_money`(disaggregated), plus `cot_index_26w`, `cot_index_52w`, `zscore_26w`, `zscore_52w`, `net_change`

#### Option B: CFTC.gov Legacy CSV (free, full history)
- URL: `https://www.cftc.gov/dea/newcot/deafut.txt`
- Released: Every Tuesday at ~3:30 PM ET
- Format: Legacy CSV with fixed column positions

### Column Mapping
```
[0]  Market Name
[1]  Date Code (YYMMDD)
[6]  Market Code (ignored for position)
[7]  Open Interest
[8]  NonCommercial Long
[9]  NonCommercial Short
[10] NonCommercial Spreading
[11] Commercial Long
[12] Commercial Short
```

### Key Commodity Contract Specs
| Commodity | Exchange | Multiplier | CFTC Market Name |
|-----------|----------|------------|-------------------|
| Gold | COMEX | 100 oz | "GOLD - COMMODITY EXCHANGE INC." |
| Silver | COMEX | 5,000 oz | "SILVER - COMMODITY EXCHANGE INC." |
| Crude Oil (WTI) | ICE/NYMEX | 1,000 bbl | "CRUDE OIL, LIGHT SWEET-WTI..." |

### Sentiment Thresholds
| Ratio (Long/Short) | Signal |
|--------------------|--------|
| > 5.0 | Strongly bullish |
| 3.0 - 5.0 | Bullish |
| 1.5 - 3.0 | Mildly bullish |
| 0.8 - 1.5 | Neutral |
| < 0.8 | Bearish |

### CFTC TFF Format (for VIX and Financial Futures)

Financial futures (VIX, Eurodollar, etc.) use a DIFFERENT format from physical commodities. They live in `fut_fin_txt_YYYY.zip` at `https://www.cftc.gov/files/dea/history/fut_fin_txt_2026.zip`. Inside the ZIP, the file is `FinFutYY.txt`.

**TFF Column Mapping** (DO NOT use Legacy mapping for TFF):
```
[7]  Open Interest
[8]  Dealer/Intermediary Long
[9]  Dealer/Intermediary Short
[10] Dealer/Intermediary Spread
[11] Asset Manager Long
[12] Asset Manager Short
[13] Asset Manager Spread
[14] Leveraged Money Long
[15] Leveraged Money Short
[16] Leveraged Money Spread
```

**VIX**: Market name in TFF is `"VIX FUTURES - CBOE FUTURES EXCHANGE"`. Use `urllib.request` with ProxyHandler, then parse with `zipfile.ZipFile` + `csv.reader`.

### DXY (US Dollar Index) COT

CFTC code `098662` (ICE US). Accessible via cotdata.net or the Legacy format. The DXY free tier on cotdata.net includes full history as a live demo.

## Report Generation Principles

When generating market/financial reports, follow these rules STRICTLY:

1. **Data-first**: Lead with numbers, not narrative. Metrics before interpretation.
2. **No price targets**: Never predict specific price levels or ranges.
3. **No trading advice**: Never say "buy", "sell", "long", "short", "enter position", "accumulate", "reduce exposure".
4. **No action plans**: Never recommend specific actions or strategies.
5. **Date every data point**: Every metric MUST show its as-of date.
6. **Source every metric**: Every data point MUST show its source (FRED, CFTC, etc.).
7. **Context over opinion**: Describe what happened and what changed, not what "should" happen.
8. **Geopolitical awareness**: Note relevant geopolitical events (wars, sanctions, policy changes) and their observable market impact — but do NOT extrapolate or predict outcomes.

### Report Structure (Precious Metals Daily)
```
📅 Precious Metals Daily | YYYY-MM-DD
━━━
📊 Key Data Snapshot
  Gold: $X,XXX  |  Silver: $XX.XX  |  Oil: $XX.XX
  Macro: CPI, PCE, TIPS, Dollar, Fed Rate
  FOMC: Hold X% / Hike Y% / Cut Z%

🏛️ Macro Environment (all data with dates)
🥇 Gold Analysis (TIPS, geopolitical factors, positioning)
🥈 Silver Analysis (gold-silver ratio, industrial context)
🌍 Geopolitics & Risk Events (5 top headlines)
```

## Report Generation Against Fixed Prompt Templates

This pipeline generates **5 weekly reports** (macro, energy, precious metals, international agriculture, China agriculture) whose output structures are determined by **fixed prompt template files** that the user provides and must NOT be modified.

### Template Location & Lockdown

- Templates live in `prompts/<report-name>.txt` alongside the pipeline code.
- **NEVER modify these .txt files.** They are the user's source of truth for output structure, section ordering, header phrasing, and mandatory disclaimer text.
- The user changes them intentionally (drag-drop from Desktop); an agent should only re-copy the files, never edit them.

### Workflow: Mapping Templates to Code

1. Read the relevant prompt template file to get exact section headers and table column definitions.
2. Open the existing Python report generator (e.g. `macro_weekly.py`).
3. **Do NOT rewrite the file from scratch.** Use `patch` operations to insert/remove/reorder sections. Rewriting destroys module headers, import chains, data loading functions, and .env path resolution that were working fine.
4. For each section in the template, verify the Python code produces a matching `## Section Title`. Add missing sections, remove surplus ones, update table column headers to match.
5. After changes, output the report in Markdown, then pipe `grep "^## "` to verify module counts and ordering match the template 1:1.
6. Report to the user exactly which sections were added, removed, or renamed.

### Template Sections (all 5 reports)

| Report | Template File | Sections |
|--------|--------------|----------|
| Macro | `prompts/全球宏观周度研究报告.txt` | 一~七 (7 sections) |
| Energy | (not in prompt dir — user said "energy doesn't need changing") | 一~八 (8 sections) |
| Precious Metals | `prompts/贵金属周报.txt` | 一~八 (8 sections) |
| Intl Agriculture | `prompts/全球农业周报（国际原版）.txt` | 一~七 (7 sections) |
| China Agriculture | `prompts/全球农业周报（中国本土版）.txt` | 一~七 (7 sections) |

### Mandatory Tail (copied verbatim from each template)

Each report ends with THREE lines (not two):
```markdown
数据来源：..., 截至XXXX年XX月XX日
免责声明：本文仅为...数据周度复盘，不构成任何投资建议。...风险极高，入市需谨慎。
AI生成标注：本文AI辅助整理，全部核心数据人工核验校准。
```

### Tushare Integration (China agriculture)

- `fetch_china_futures()` in `agri_weekly.py` calls Tushare `fut_daily` API.
- Uses `start_date`/`end_date` range (not `trade_date` single-day) for weekend fallback.
- .env path on VPS is `/root/hermes-pipeline/.env`, NOT `~/.hermes/.env`. Set `load_dotenv` to resolve from `hermes-pipeline` on the VPS.
- Covered DCE symbols: 豆粕(M), 豆油(Y), 玉米(C), 豆一(A), 生猪(LH), 棕榈油(P), 鸡蛋(JD)
- Covered CZCE symbols: 白糖(SR), 棉花(CF), 菜籽油(OI)
- Weekend: returns "未获取" for all symbols (no trading data). This is correct — do not fall back to stale data.

## Chart Generation Pipeline

8 standard charts generated by `charts.py` and embedded in HTML emails.

### Setup (VPS — one-time)

```bash
apt-get install -y fonts-noto-cjk-extra
pip3 install matplotlib
```

Chinese font: `Noto Sans CJK JP`. Set with:
```python
plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.rcParams["axes.unicode_minus"] = False
```

### Chart Inventory

| Chart | Function | Used By | Data Source |
|-------|----------|---------|-------------|
| fred_trends.png | `chart_fred_trends()` | Macro report | `macro_history` table (3-year slice, DESC LIMIT 1100) |
| gold_price.png | `chart_gold_price()` | Metals report | `price_history WHERE品种='gold'` |
| silver_price.png | `chart_silver_price()` | Metals report | `price_history WHERE品种='silver'` |
| gold_silver_ratio.png | `chart_gold_silver_ratio()` | Metals report | `price_history` gold/silver merged by date |
| cot_net.png | `chart_cot_net()` | All reports with COT | `cotdata` table, current snapshot |
| cot_index.png | `chart_cot_index()` | All reports with COT | `cotdata` table, current snapshot |
| cot_long_short.png | `chart_cot_long_short()` | Metals/Energy | `cotdata` table, current snapshot |
| cot_net_history.png | `chart_cot_net_history()` | Metals report | `cot_history WHERE commodity='gold'` |

### Data Cleaning (critical)

The 15-year `price_history` table contains outlier values (~$397 gold). Always filter:
```python
# Gold: 1000 < close < 6000
# Silver: 5 < close < 200
```

### Y-Axis Independence

When showing subplots (gold 15yr + 3yr + 1yr), each subplot gets its own y-axis range:
```python
ypad = (max(y) - min(y)) * 0.12
ax.set_ylim(min(y) - ypad, max(y) + ypad)
```

### Labeling Convention (all line charts)

- Start value: bottom-left, gray, `ha="left", va="bottom"`
- End value: upper-right, bold, white background box

### Email Delivery (base64 HTML)

Charts are delivered inside the email body, not as attachments. QQ SMTP:
```
EMAIL_HOST=smtp.qq.com, EMAIL_PORT=465
```
Each report's `chart_type` parameter controls which charts get embedded:
- `macro` → only FRED trend chart
- `metals` → 6 charts (gold price, silver price, gold-silver ratio, COT history, COT ranking, COT index)
- `energy` → COT net ranking + COT index
- `agri` / `agri_cn` → no charts

## Historical Excel Import

When the user provides Excel files at `D:\commodity_research_platform\export\merged\`, use `import_history.py`:

| Source File | Target Table | Description |
|-------------|-------------|-------------|
| 商品价格.xlsx | `price_history` | Daily OHLCV for 17 commodities (2011~2026) |
| 宏观经济.xlsx | `macro_history` | 13 US macro indicators (2011~2026) |
| 期货持仓.xlsx | `cot_history` | COT positions for 17 instruments (2011~2026) |
| 能源.xlsx | `energy_history` | European gas storage + EIA data (2020~2026) |

## Download & Send Invariant

All weekly reports go through `run_report.py` (wrapper) then `send_email.py` (QQ SMTP with base64 HTML). Reports send by VPS system cron, NOT Hermes cron (Hermes gateway not running on VPS).

## Cron Setup

```bash
# Daily data collection at 08:00
hermes cron create "0 8 * * *" \
  --name "macro-data-pipeline" \
  --workdir /path/to/pipeline \
  --prompt "Run the daily macro data pipeline script"

# Daily report generation at 09:00
hermes cron create "0 9 * * *" \
  --name "macro-report-gen" \
  --workdir /path/to/pipeline \
  --prompt "Generate the daily macro report"
```

⚠️ Cron jobs only fire when Hermes gateway is running. On a local Windows desktop, the Hermes Desktop app handles scheduling. On a VPS/server, run `hermes gateway install` or use system cron (`crontab`).

## VPS Deployment Checklist

### System Requirements
- 1 vCPU, 1 GB RAM, 25 GB SSD minimum
- Ubuntu 22.04 LTS recommended
- Python 3.10+ (Hermes installs its own)

### Security (before deploying pipeline)
1. Create non-root user: `adduser hermes && usermod -aG sudo hermes`
2. SSH key auth only: `ssh-keygen` then `ssh-copy-id`
3. Disable root login & password auth in `/etc/ssh/sshd_config`
4. Enable firewall: `ufw allow 22/tcp && ufw --force enable`
5. Install fail2ban: `apt install -y fail2ban`

### Transfer & Run
```bash
# From local machine
scp pipeline/*.py user@host:~/macro-pipeline/
scp .env user@host:~/macro-pipeline/

# On VPS
cd ~/macro-pipeline
pip3 install requests pandas python-dotenv
python3 macro_pipeline.py
```

## Pitfalls

- **CRITICAL — Report generation code: patch, don't rewrite**: When modifying `macro_weekly.py`, `metals_weekly.py`, `agri_weekly.py`, etc., use `patch` for targeted edits. NEVER rewrite the entire file. Rewriting destroys import chains, data-loading paths, .env resolution, and working data connections — and inevitably drops sections the user expects. The user's fixed prompt templates define output structure; the Python code is the implementation that already has the data plumbing working. Change only the section headers and table columns.

- **CRITICAL — Report what changed**: After modifying any report generator, list exactly which sections were added, removed, or renamed. The user reviews all changes and will notice omissions.

- **CRITICAL — Verify against ALL five report formats**: After modifying `send_email.py` or any shared component, test ALL five report types (macro, energy, metals, agri, agri_cn) — not just one. Each report uses different Markdown table syntax. A fix that works for metals may break agriculture. Run `python3 run_report.py <rpt>` for all five and confirm all emails send.

- **CRITICAL — Do not modify prompt template files**: The `.txt` files in `prompts/` are the user's source of truth. Copy them from Desktop, save them, reference them — never edit them.

- **Yahoo Finance blocked in China**: Yahoo domains are inaccessible from mainland China. Even with proxies, Yahoo's v10 API requires a crumb/token that's hard to automate. Use chart API `v8/finance/chart/{SYMBOL}` with `range=5d&interval=1d` instead of the quoteSummary endpoint.

- **Yahoo exponential backoff**: Must handle 429 (rate limit) and 403 (blocked). Pattern:
  ```python
  import time, random
  for attempt in range(retries):
      r = requests.get(url, timeout=15)
      if r.status_code == 200: return r.json()
      elif r.status_code == 429: time.sleep((2**attempt) + random.random()*2)
      elif r.status_code == 403: time.sleep(5)
  ```

- **CME FedWatch blocked**: CME Group returns 403 to programmatic requests. Use oddpool.com/fed-market-watch as aggregation proxy.

- **CFTC URL changes**: CFTC restructures their site periodically. If the Legacy format URL disappears, check `www.cftc.gov/MarketReports/CommitmentsofTraders/` for current download links. The Historical Compressed ZIP files at `https://www.cftc.gov/files/dea/history/` are more stable.

- **CFTC format mismatch**: Legacy (physical commodities) and TFF (financial futures) have COMPLETELY DIFFERENT column layouts. Verify column mapping against each report type's header.

- **Alpha Vantage rate limits**: 5 calls/minute on free tier, 25/day. Insert `time.sleep(12)` between calls. Only schedule once daily to stay under the 25/day limit.

- **EIA STEO requires data[] parameter**: The EIA STEO endpoint `https://api.eia.gov/v2/steo/data/` REQUIRES `data[0]=value` in the query parameters, otherwise no values are returned — only metadata fields.

- **FRED 400 errors**: Double-check series IDs. Common mistakes: T10YIFR (wrong) vs T10YIE (correct), TREAST (price index) vs DGS1 (yield). FRED search API has timeout issues from China.

- **NewsAPI blocked in China**: newsapi.org is unreachable from mainland China. Use Finnhub news endpoint as replacement (works without proxy).

- **Secret redaction masking**: Hermes auto-masks strings that look like API keys in tool output with `***`. Use raw binary reads (`open(path, 'rb').read()`) to verify actual .env file content during debugging.

- **.env path mismatch**: Hermes Desktop stores .env at `AppData/Local/hermes/.env`, NOT `~/.hermes/.env`. Always resolve via `HERMES_HOME` env var:
  ```python
  ENV_PATH = Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))) / ".env"
  ```

- **cotdata.net rate limit**: Free tier is 10 requests/minute. When adding many instruments, expect 429 errors for later requests. Accept partial results (the first 10 will succeed) rather than retrying.

- **CRITICAL: .env key writing via heredoc/shell corrupts values**: NEVER write API keys to .env using `cat << 'EOF' | >>`, `echo ... >>`, or shell heredocs. Special characters (`*`, `$`, `\`, `!`) get mangled, values get truncated with `...`, or `***` gets written literally. ONLY use Python scripts with `write()` to a file. Pattern:
  ```python
  with open(env_path, "w") as f:
      f.write(f"FRED_API_KEY={actual_key_value}\n")
  ```
  Then verify with `open(path, 'rb').read()` (bypasses Hermes redaction) to check actual byte content and value length.

- **CRITICAL: API keys MUST be the actual key string, not placeholder text like `*** ` or `...n`**: When constructing key-value pairs in Python, use the ACTUAL hex/string key value. A common failure mode: writing `f'FRED_API_KEY=***'` literally writes `*** ` into the file. Verify by checking value length — a 32-char hex key should show 33 chars (32+newline).

- **Tushare fut_daily**: Use `trade_date="YYYYMMDD"` parameter, NOT individual `ts_code`. This returns ALL futures for the date. 2000积分 tier does cover futures daily data despite initial assumption.

- **Chinese vs Traditional character handling**: Pipeline writes Traditional Chinese column names (失業率, 聯邦基金, 國債). Report generators must use these exact characters for `str.contains()` searches, but output Simplified Chinese in the report text. Use `regex=False` to avoid regex interpretation issues with parentheses in column names.

- **FMP API deprecated**: Financial Modeling Prep's legacy API (v3/v4) now returns 403 "Legacy Endpoint". The new "stable" API requires a paid subscription for futures/ETF data. Free tier only supports basic stock quotes.

## Related Resources

See `references/fred-series-guide.md` for the complete FRED series reference.
See `references/report-format-principles.md` for detailed report formatting rules, the six hard rules, and the full five-report weekly framework (precious metals, energy, agriculture, macro, asset allocation).
See `references/email-html-rendering.md` for the send_email.py HTML table rendering architecture, chart embedding logic, and known bug fixes.
See `references/scrapling-finance-sources.md` for Scrapling data-source patterns (fetcher selection, proxy config, CSS selector patterns).
See `references/all-data-sources.md` for the complete verified API endpoint catalog (16+ sources, codes, series IDs, rate limits, and pitfalls).
