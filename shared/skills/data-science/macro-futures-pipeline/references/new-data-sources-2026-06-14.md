# New Data Sources Integrated (2026-06-14)

## Baker Hughes钻机数 → AOGR网站

### Problem
Original source (rigcount.bakerhughes.com) blocked by Cloudflare on VPS.

### Solution
AOGR website (aogr.com) has same Baker Hughes data as static HTML.

### Implementation
```python
def fetch_baker_hughes():
    """Fetch Baker Hughes rig count from AOGR website"""
    url = "https://www.aogr.com/web-exclusives/us-rig-count/2026"
    # Uses requests + BeautifulSoup
    # Returns: {"date": "2026-06-12", "total": 562, "oil": 433, "gas": 121, "misc": 8}
```

### Key Points
- URL uses `datetime.now().year` for automatic year detection
- Returns backward-compatible fields: us_count, canada_count, na_total
- No Cloudflare blocking
- Tested on VPS: 562 rigs (oil 433, gas 121, misc 8)

---

## BDI海运运价 → TradingEconomics

### Problem
Original source (investing.com) blocked by Cloudflare.

### Solution
TradingEconomics has BDI data without Cloudflare.

### Implementation
```python
def fetch_bdi():
    """Fetch BDI from TradingEconomics"""
    url = "https://tradingeconomics.com/commodity/baltic"
    # Uses requests + BeautifulSoup
    # Returns: {"price": 2729.0, "date": "2026-06-12", "source": "TradingEconomics"}
```

### Key Points
- No proxy required (unlike investing.com)
- Returns backward-compatible fields: price, change_pct, prevClose
- Tested on VPS: BDI = 2729.0

---

## 美湾粮食检验 → USDA TXT文件

### Problem
USDA AMS API returns 403 from VPS (Akamai CDN blocks cloud IPs).

### Solution
USDA TXT file (wa_gr101.txt) is accessible and contains Gulf data.

### Implementation
```python
def fetch_usda_export_inspections():
    """Fetch Gulf grain export inspections from USDA TXT file"""
    url = "https://www.ams.usda.gov/mnreports/wa_gr101.txt"
    # Uses requests + regex parsing
    # Returns: gulf_total_mt, gulf_corn_mt, gulf_soybeans_mt, gulf_wheat_mt
```

### Key Points
- URL: https://www.ams.usda.gov/mnreports/wa_gr101.txt
- Published: Weekly (Monday 10:00 AM CT)
- Data includes: Gulf region (East Gulf, Mississippi River, N. Texas)
- VPS may get 403 from cloud IPs, works from residential IPs
- Already implemented in data_scrapers.py

---

## 社融数据 → Tushare sf_month

### Problem
AKShare's macro_china_shrzgm() has SSL handshake failure.

### Solution
Tushare Pro sf_month API (requires 2000 integration points).

### Implementation
```python
def fetch_social_financing():
    """Fetch social financing data from Tushare sf_month"""
    pro = ts.pro_api(TS_TOKEN)
    df = pro.sf_month(start_m="202501", end_m=datetime.now().strftime("%Y%m"))
    # Returns: month, inc_month (增量当月值亿元), inc_cumval (累计值), stk_endval (存量万亿)
```

### Key Points
- API name: sf_month
- Documentation: https://tushare.pro/document/2?doc_id=310
- Requires: 2000 integration points (user has 2000)
- Returns: monthly social financing data
- Tested: 70,546亿月增量，存415.19万亿

---

## VPS Timezone Configuration

### Problem
VPS uses UTC time, cron jobs run at wrong time for China.

### Solution
Set timezone to Asia/Shanghai (UTC+8).

### Implementation
```bash
timedatectl set-timezone Asia/Shanghai
# Verify: date "+%Y-%m-%d %H:%M:%S %Z"
```

### Cron Job Times (China Time)
- Daily 08:00: FRED/Yahoo data collection
- Wednesday 23:00: EIA data (released 22:30)
- Friday 04:00: COT data (released 03:30)
- Monday 09:00: Macro report
- Thursday 09:00: Energy report
- Friday 09:00/20:00: Agriculture reports
- Saturday 09:00: Metals report
- Sunday 10:00: Allocation report

---

## Monitor.py Removal

### Problem
Data is not real-time (1-2 day lag), 4-hour monitoring is useless.

### Solution
Remove monitor.py cron job, rely on weekly reports for threshold alerts.

### Rationale
- Yahoo futures: daily collection (1-day lag)
- FRED: daily collection (1-2 day lag)
- COT: weekly collection (1-week lag)
- EIA: weekly collection (1-day lag)
- Real-time monitoring would require Bloomberg/Reuters API (expensive)

---

## QQ Bot Configuration (Critical)

### Correct Format
```yaml
platforms:
  qq:                          # NOT "qqbot"
    enabled: true
    extra:                     # Credentials under "extra"
      app_id: "YOUR_APP_ID"
      client_secret: "YOUR_SECRET"  # NOT "secret"
```

### Environment Variables
```bash
QQ_APP_ID=1904159904
QQ_CLIENT_SECRET=IVUFl2...n
QQ_ALLOW_ALL_USERS=true
```

### Common Mistakes
- ❌ `platforms.qqbot.secret` → ✅ `platforms.qq.extra.client_secret`
- ❌ `QQ_APP_SECRET` → ✅ `QQ_CLIENT_SECRET`
- ❌ Credentials directly under platform → ✅ Under `extra`

### Limitations
- Proactive messages: 4/month per user (limit)
- Passive messages: unlimited (user asks, bot replies)
- Supports: Markdown, images, files
- Use case: daily conversation, not report delivery (use email instead)
