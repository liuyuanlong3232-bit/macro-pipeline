# Database Schema Mappings for Report Scripts

All data collected by `macro_pipeline.py` is stored in SQLite at `~/hermes-macro-data/hermes.db`. Report scripts must use the correct table and column names — they differ from what you might expect.

## FRED Indicators Table

**Table:** `fred_indicators`

| Column | Example | Notes |
|--------|---------|-------|
| `日期` | `2026-05-01` | Observation date |
| `指標` | `联邦基金利率` | Display name (traditional Chinese) |
| `系列ID` | `FEDFUNDS` | Series identifier — **this is the key column for lookups** |
| `數值` | `3.63` | The actual value |
| `抓取日` | `2026-06-12` | Collection date |

**Correct lookup pattern:**
```python
cur.execute("SELECT 數值, 日期 FROM fred_indicators WHERE 系列ID = ? ORDER BY 日期 DESC LIMIT 1", (series,))
```
❌ DO NOT use `WHERE 系列 = ?` — that column is `系列ID`, not `系列`.

**Missing series:** `DGS5` (5-year Treasury) has no data rows. Use `DGS10` as fallback.

## Yahoo Futures Table

**Table:** `yahoo_futures`

| Column | Example | Notes |
|--------|---------|-------|
| `品種` | `COMEX黃金期貨` | Traditional Chinese names |
| `代碼` | `GC=F` | Yahoo ticker |
| `最新價` | `4212.1` | Latest price |
| `日漲跌幅%` | `-2.855` | **Column name includes `%` — requires quoting** |

**Correct lookup pattern:**
```python
cur.execute('SELECT 最新價, "日漲跌幅%" FROM yahoo_futures WHERE 品種 LIKE ?', (f"%{kw}%",))
```
❌ `日漲跌幅` (without %) will not match.

**Available symbols (繁体):**
`COMEX黃金期貨`, `COMEX白銀期貨`, `WTI原油期貨`, `Brent原油期貨`, `天然氣期貨(Henry Hub)`, `玉米期貨`, `大豆期貨`, `小麥期貨`, `豆油期貨`, `豆粕期貨`, `棉花期貨`, `糖期貨`

**Not available in yahoo_futures:** VIX, DXY, USDJPY, EURUSD. See `vix_data` and `cotdata`/FRED for those.

## COT Data Table

**Table:** `cotdata`

| Column | Example | Notes |
|--------|---------|-------|
| `品種` | `黄金` | **Simplified Chinese** (简体) |
| `交易所` | `COMEX` | |
| `報告日期` | `2026-06-02` | |
| `投機淨持倉` | `176020` | |
| `COT Index(26W)` | `100.0` | **Column name contains parentheses** |
| `Z-Score` | `1.73` | |

**Correct lookup pattern:**
```python
cur.execute('SELECT "COT Index(26W)" FROM cotdata WHERE 品種 LIKE ?', (f"%{kw}%",))
```
❌ Use **simplified Chinese** keywords: `黄金`, `白银` (NOT 繁體 `黃金`, `白銀`)

## VIX Data Table

**Table:** `vix_data` (separate from yahoo_futures!)

| Column | Example | Notes |
|--------|---------|-------|
| `品種` | `VIX` | |
| `报告日期` | `2026-06-02` | |
| `价格` | `18.99` | |
| `杠杆基金净` | `-33033` | |

**Correct lookup:**
```python
cur.execute('SELECT 价格 FROM vix_data WHERE 品種 = "VIX" ORDER BY 报告日期 DESC LIMIT 1')
```

## Key Gotchas

1. **繁简混用:** Yahoo uses 繁體 (`黃金`), COT uses 简体 (`黄金`). Match the source.
2. **Special chars in column names:** `日漲跌幅%`, `COT Index(26W)` need double-quoting.
3. **VIX is in its own table:** Not in `yahoo_futures`.
4. **DXY, USDJPY, EURUSD:** Not in `yahoo_futures`. Use `fred_indicators` (`DTWEXBGS`) for DXY. No free source for forex in current pipeline.
5. **`系列ID` not `系列`:** FRED lookup column name differs from the display name.
6. **DGS5 missing:** Use `DGS10` as fallback if 5-year treasury data is needed.
