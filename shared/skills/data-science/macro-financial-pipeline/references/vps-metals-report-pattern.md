# VPS Metals Weekly Report Generator Pattern

## Architecture

Pure Python script that runs on VPS **without calling any LLM**. Reads data from:
1. **Live Yahoo Finance API** — gold/silver spot prices (preferred, real-time)
2. **CSV files** from the daily data pipeline — COT, FRED, all other indicators
3. **Fallback** to CSV for prices if Yahoo is unreachable

## Key Pattern: Live Price Fetch

```python
def yahoo_price(symbol):
    """从Yahoo实时拉价格"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        r = requests.get(url, params={"range": "1d", "interval": "1d"},
                        headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if r.status_code == 200:
            meta = r.json()["chart"]["result"][0]["meta"]
            return float(meta.get("regularMarketPrice", 0))
    except:
        return None
    return None

# In report():
yg = yahoo_price("GC=F")       # COMEX Gold futures
ys = yahoo_price("SI=F")       # COMEX Silver futures
gld = yahoo_price("GLD")       # GLD ETF price
slv = yahoo_price("SLV")       # SLV ETF price

# Use live price if available, fallback to CSV
gold_s = f"{y:.2f}" if yg else get_val(yahoo, "黃金")
silver_s = f"{ys:.3f}" if ys else get_val(yahoo, "白銀")
```

## Why This Matters

**Alpha Vantage XAUUSD gold prices are consistently ~$16-20 behind** Yahoo GC=F prices. On a US VPS, Yahoo Futures are delivered via ICE/Bloomberg infrastructure and match the user's trading platform closely.

## Column Detection (Applies to All CSVs)

Do NOT hardcode column names — CSVs may have Traditional Chinese headers:

```python
def get_val(df, kw):
    if df.empty: return None
    name_col = df.columns[0]
    for c in df.columns:
        if "品" in c or "指" in c: name_col = c; break
    val_col = None
    for c in df.columns:
        if "價" in c or "值" in c: val_col = c; break
    if not val_col: val_col = df.columns[-1]
    sub = df[df[name_col].astype(str).str.contains(kw, na=False)]
    if sub.empty: return None
    return str(sub.iloc[0][val_col])
```

## COT Data Extraction

```python
gc, gci, gz = "", "", ""
if not cot.empty:
    nc = cot.columns[0]
    for c in cot.columns:
        if "品" in c: nc = c; break
    for _, r in cot.iterrows():
        n = str(r[nc])
        if "黄金" in n:
            gc = f"{int(r['投機淨持倉']):+,}"
            gci = f"{r['COT Index(26W)']:.0f}"
            gz = f"{r['Z-Score']:+.2f}"
```

## Report Structure (Metals Only)

Eight sections, Simplified Chinese:

1. **一周、本周贵金属市场总结** — summary table with price/ETF/ratio/COT
2. **二、价格走势分析** — table: 指标 | 最新价 | 周均价 | 数据来源
3. **三、宏观驱动环境分析** — TIPS/DXY/FF rate + impact
4. **四、CFTC COT资金持仓分析** — net position / COT Index / Z-Score / signal
5. **五、产业&需求基本面简析** — solar PV demand for silver
6. **六、地缘&跨资产联动影响** — Middle East, Fed expectations
7. **七、供需强弱评分** — -10 to +10 with logic bullets
8. **八、未来30天重点观察方向+潜在风险提示**
