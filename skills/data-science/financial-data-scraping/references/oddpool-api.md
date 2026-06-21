# oddpool.com FedWatch API Endpoints

## Discovery Method
The oddpool.com FedWatch page is a Next.js SPA. To find the real API:
1. Open browser DevTools → Network tab
2. Load the page
3. Filter by "api" in the URL
4. Look for `/api/events/history/` endpoints

## Endpoints

### Get "Fed maintains rate" probability
```
GET https://www.oddpool.com/api/events/history/no_change?event_id=fomc-2026-06-17&hours=1
```

### Get "Cut 25bps" probability
```
GET https://www.oddpool.com/api/events/history/cut_25bps?event_id=fomc-2026-06-17&hours=1
```

### Get "Hike 25bps" probability
```
GET https://www.oddpool.com/api/events/history/hike_25bps?event_id=fomc-2026-06-17&hours=1
```

## Response Format
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
  "polymarket": [...]
}
```

## Event ID Discovery
FOMC meetings typically happen mid-month. To find the correct event_id:
```python
for m_offset in range(0, 2):
    m = now.month + m_offset
    y = now.year + (m - 1) // 12
    m = (m - 1) % 12 + 1
    for day in [17, 16, 18, 15, 19, 14, 20]:
        event_id = f"fomc-{y}-{m:02d}-{day:02d}"
        # try API call
```

## Validation
Sum of hold + cut_25 + hike_25 should be ~100%. If >105%, data is corrupt.

## Current Values (verified 2026-06-14)
- Fed maintains rate: 99.0% (Kalshi)
- Cut 25bps: 1.0% (Kalshi)
- Hike 25bps: ~0.6%
