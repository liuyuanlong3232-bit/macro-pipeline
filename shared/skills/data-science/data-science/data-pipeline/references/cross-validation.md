# Cross-Validation: Multi-Source Data Integrity Checks

Data pipelines pulling from multiple APIs often have silent drift — one source breaks, another returns stale data, a third has a schema change. Cross-validation detects this before it reaches reports.

## Why Cross-Validate

| Scenario | Detection Method |
|----------|-----------------|
| Source A returns stale/missing data | Compare timestamp with Source B for same metric |
| Source B's units changed (e.g. percent vs decimal) | Compare ratio between two independent sources |
| Source A rate-limited / returned 429 error | Check that both sources agree within tolerance |
| API schema changed silently | Known-constant series (e.g. day-count) should match |

## Practical Checks

### Price-based (same asset, different sources)

| Asset | Source A | Source B | Tolerance | Action on breach |
|-------|----------|----------|-----------|-----------------|
| Gold | Yahoo `GC=F` | Alpha Vantage `GC=F` | ±1.0% | Log warning, use higher-volume source |
| Silver | Yahoo `SI=F` | Alpha Vantage `SI=F` | ±1.5% | Log warning |
| WTI Crude | Yahoo `CL=F` | EIA spot price | ±2.0% | Log warning (EIA may be delayed) |
| US Dollar | FRED `DTWEXBGS` | cotdata.net DXY | ±0.5% | Log warning |
| 10Y Treasury | FRED `DGS10` | Yahoo `^TNX` / 10Y | ±0.1 (absolute) | Log warning |

### Derived-metric (same concept, different calculations)

| Metric | Source A | Source B | Check | Action |
|--------|----------|----------|-------|--------|
| Gold/Silver Ratio | Yahoo price ratio | Manual calc from OHLC | ±0.5 | Compare, warn if diverging |
| Yield Curve Slope | `DGS10 - DGS2` | `T10Y2Y` series | ±0.05 | Both are FRED — should match exactly |
| Inflation Expectations | `DGS10 - DFII10` | `T10YIE` series | ±0.1 | Both FRED, slight calc differences normal |

### Temporal (same source, different timeframes)

| Check | Method | Action |
|-------|--------|--------|
| Stale data | Compare `observations[0].date` with yesterday | If >7 days stale, warn |
| Gap detection | Count expected vs actual records | If missing >10% of expected dates, warn |
| Flatline detection | Std dev of last 5 values < threshold | If zero variance, suspect broken feed |

## Implementation Pattern

```python
def cross_validate_price(source_a, source_b, asset_name, tolerance=0.01):
    """Compare two independent price sources."""
    if source_a is None or source_b is None:
        return {"asset": asset_name, "status": "MISSING", "detail": "One source returned None"}
    
    diff = abs(source_a - source_b) / source_a
    if diff > tolerance:
        return {
            "asset": asset_name,
            "status": "BREACH",
            "a": source_a, "b": source_b,
            "diff_pct": round(diff * 100, 2)
        }
    return {"asset": asset_name, "status": "OK", "diff_pct": round(diff * 100, 4)}

# Batch run at end of collection
results = []
results.append(cross_validate_price(gold_yahoo, gold_alpha, "Gold"))
results.append(cross_validate_price(silver_yahoo, silver_alpha, "Silver"))

alerts = [r for r in results if r["status"] == "BREACH"]
if alerts:
    logger.warning(f"Cross-validation: {len(alerts)} breach(es)")
```

## When NOT to Cross-Validate

- Sources that inherently differ (e.g. spot vs futures — expect basis)
- Sources with different update frequencies (e.g. weekly vs daily)
- Data that was manually entered (no machine-readable reference)

## Integration

Add cross-validation as the last step in `macro_pipeline.py` after all sources are collected. Write results to:
```
~/hermes-macro-data/logs/cross_validate_<date>.json
```

If a breach exceeds `max_tolerance` (configurable per-asset), the pipeline warns in the daily report header so the analyst knows which data point to treat cautiously.
