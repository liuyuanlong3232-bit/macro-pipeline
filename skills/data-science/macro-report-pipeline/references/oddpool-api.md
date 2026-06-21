# oddpool.com FedWatch API Reference

**Discovery date**: 2026-06-14

## Problem
oddpool.com/fed-market-watch is a Next.js SPA. `requests.get()` returns a ~26-byte empty shell HTML. All regex-based scraping fails.

## Solution: REST API Endpoints

The site exposes clean JSON APIs that the frontend fetches via XHR.

### Base URL
```
https://www.oddpool.com/api/events/history
```

### Endpoints

| Endpoint | Outcome | Response Key |
|----------|---------|--------------|
| `/no_change` | Fed maintains rate | `probabilities.no_change` |
| `/cut_25bps` | Cut 25bps | `probabilities.cut_25bps` |
| `/cut_50bps` | Cut >25bps | `probabilities.cut_50bps` |
| `/hike_25bps` | Hike 25bps | `probabilities.hike_25bps` |
| `/hike_50bps` | Hike >25bps | `probabilities.hike_50bps` |

### Parameters
- `event_id`: `fomc-YYYY-MM-DD` (the FOMC meeting date)
- `hours`: Lookback window in hours (use `1` for latest, `168` for 7-day history)

### Response Format
```json
{
  "kalshi": [
    {
      "timestamp": "2026-06-14T04:32:01.579466",
      "probabilities": {"no_change": 0.99},
      "yesAsks": {"no_change": 0.99},
      "noAsks": {"no_change": 0.02}
    }
  ],
  "polymarket": [
    {
      "timestamp": "2026-06-14T04:32:01.579466",
      "probabilities": {"no_change": 0.995}
    }
  ]
}
```

### Key Notes
- Probabilities are **0-1 floats** (multiply by 100 for display)
- Take `items[-1]` for the latest data point
- Prefer Kalshi data (more liquid, more frequent updates)
- FOMC dates are typically mid-month (15-19). Try days 14-20 to find the right event_id.
- Validate: hold + cut_25 + hike_25 should sum to ~100%. Reject if > 105%.

### Other Useful API Endpoints (from browser network inspection)
```
/api/events/volume-candles/<outcome>?event_id=<id>&hours=<N>&interval_minutes=<N>
/api/whales/event/by-ticker/<ticker>?limit=<N>&offset=<N>
/api/trades/live?venue=kalshi&identifier=<id>&limit=<N>
/api/orderbook/live?venue=kalshi&identifier=<id>&side=yes
```

### CME FedWatch Tool
CME's own FedWatch page (cmegroup.com) returns HTTP2 protocol errors when accessed programmatically. oddpool.com's API is more reliable as an alternative data source.
