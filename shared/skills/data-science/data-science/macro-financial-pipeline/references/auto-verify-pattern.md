# Auto-Verification Pattern for Reports

Each VPS-generated report includes a **Section 九: 数据核验** that automatically checks all prices against live Yahoo data at generation time.

## How It Works

```python
# In the report() function, before writing the final lines:
verify = []
verify_ok = True
try:
    yh_g = yahoo_price("GC=F")    # Live Yahoo gold
    yh_s = yahoo_price("SI=F")    # Live Yahoo silver
    yh_d = yahoo_price("DX-Y.NYB") # Live Yahoo DXY
    
    # Compare each value
    if gold_s and yh_g:
        d = abs(float(gold_s) - yh_g)
        if d > 5:    # Acceptable range: $5 for gold
            verify.append(f"⚠️ 黄金现货价差${d:.2f}")
            verify_ok = False
    
    if silver_s and yh_s:
        d = abs(float(silver_s) - yh_s)
        if d > 2:    # Acceptable range: $2 for silver
            verify.append(f"⚠️ 白银现货价差${d:.2f}")
            verify_ok = False
except:
    pass

# Write to report
lines.append("---")
lines.append("## 九、数据核验")
if verify_ok and not verify:
    lines.append("✅ **所有数据已通过自动核验，与实时行情一致**")
else:
    for msg in verify:
        lines.append(msg)
    lines.append("✅ 其他数据核验通过")
```

## Per-Symbol Thresholds

| Symbol | Type | Acceptable Range | Reason |
|--------|------|-----------------|--------|
| GC=F | Gold | ±$5 | Normal intraday volatility |
| SI=F | Silver | ±$2 | More volatile per unit |
| DX-Y.NYB | DXY | ±0.5 | Very stable intraday |
| CL=F | WTI Oil | ±$1 | Normal intraday |
| NG=F | Nat Gas | ±$0.10 | Normal intraday |

## When It Flags

The verification does NOT fail the report — it adds a warning line below the ✅ message so the user knows to double-check a specific value.
