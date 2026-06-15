# Auto-Verify & Panorama Check Patterns

## 1. Auto-Verify at Report Generation Time

Every fixed-template report must end with a "数据核验" section that compares all prices against live Yahoo data:

```python
# Price safety guard — all values pass through this
def safe_price(val, name, min_v, max_v):
    try:
        v = float(val)
        if v < min_v or v > max_v:
            print(f"⚠️ {name} 价格异常: {v} (正常范围{min_v}-{max_v})")
            return None
        return v
    except:
        return None

# At report generation, verify against Yahoo live
try:
    yh_g = yahoo_price("GC=F")
    if gold_s and yh_g:
        d = abs(float(gold_s) - yh_g)
        if d > 5:
            verify.append(f"⚠️ 黄金现货价差${d:.2f}")
except: pass

# Embed verification results in report
if verify_ok and not verify:
    lines.append("✅ **所有数据已通过自动核验，与实时行情一致**")
else:
    for msg in verify:
        lines.append(msg)
```

## 2. Safety Ranges for Financial Data

| Asset | Min | Max | Source |
|-------|-----|-----|--------|
| Gold (GC=F or XAUUSD) | 1000 | 10000 | Yahoo/AV |
| Silver (SI=F or XAGUSD) | 10 | 200 | Yahoo/AV |
| WTI Crude (CL=F) | 10 | 200 | Yahoo |
| Brent (BZ=F) | 10 | 200 | Yahoo |
| Henry Hub NG (NG=F) | 1 | 20 | Yahoo |
| DXY Index (DX-Y.NYB) | 90 | 130 | Yahoo |
| Corn (ZC=F) | 100 | 1000 | Yahoo |
| Soybean (ZS=F) | 500 | 2000 | Yahoo |
| TIPS real rate | -5 | 10 | FRED |
| Fed Funds rate | 0 | 10 | FRED |

## 3. Panorama Check (Full Data Audit)

Run on VPS: `cd /root/hermes-pipeline && timeout 45 python3 panorama.py`

Displays every data source with CSV value vs Yahoo live value + status:
✅ = diff < 5% (normal market movement)
⚠️ = diff 5-20% (check source)
❌ = diff > 20% (data error)
⏳ = not yet collected today

## 4. YoY/MoM Calculation for FRED

Pipeline stores 13 observations per series. At panorama/report time:

```python
vals = sub[vc].dropna().tolist()
dates = sub[dc].tolist()
cur = vals[0]

# MoM: compare to previous observation
mom = (float(cur) - float(vals[1])) / float(vals[1]) * 100

# YoY: find observation ~12 months back with same month
target_month = str(dates[0])[5:7]
for i in range(1, len(dates)):
    if str(dates[i])[5:7] == target_month:
        yoy = (float(cur) - float(vals[i])) / float(vals[i]) * 100
        break

# Display
print(f"{name}: {cur} | 同比 {yoy:+.1f}% | 环比 {mom:+.1f}%")
```
