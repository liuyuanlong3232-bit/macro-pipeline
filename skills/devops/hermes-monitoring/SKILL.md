---
name: hermes-monitoring
description: "Hermes Agent usage monitoring: token costs, cache efficiency, session analytics. Use when the user asks about token usage, costs, API consumption, or cache hit rates."
triggers:
  - token usage
  - cost analysis
  - cache hit rate
  - API consumption
  - usage report
  - how much did we use
  - billing
---

# Hermes Monitoring & Cost Analysis

## Quick Overview

`hermes insights --days N` gives totals but does NOT break down cache vs non-cached tokens. For cache breakdown, export sessions and parse.

## Step 1: Quick Insights

```bash
hermes insights --days 7        # last 7 days overview
hermes insights --days 1        # today only
hermes insights --source cli    # filter by platform
```

Shows: sessions, messages, tool calls, input/output/total tokens, platforms, top tools, skills.

**Important**: The "Total tokens" includes cache_read_tokens. It is NOT equal to input + output.

## Step 2: Cache vs Non-Cached Breakdown

`hermes insights` does not expose cache detail. Use session export:

```bash
hermes sessions export /root/sessions_export.jsonl
```

Then extract per-session token fields:

```bash
grep -oP '"input_tokens":\s*\d+|"output_tokens":\s*\d+|"cache_read_tokens":\s*\d+' /root/sessions_export.jsonl
```

### Token Field Meanings (state.db schema)

| Field | Meaning | Billing |
|-------|---------|---------|
| `input_tokens` | New (non-cached) input per session | Full price |
| `output_tokens` | Model output tokens | Full price |
| `cache_read_tokens` | Tokens served from prompt cache | Discounted (often 1/10) |
| `cache_write_tokens` | Tokens written to cache | Usually 0 |
| `reasoning_tokens` | Thinking/reasoning tokens | Provider-dependent |

**Total API call** = input_tokens + cache_read_tokens + output_tokens

### One-liner Sum

```bash
grep -oP '"input_tokens":\s*\d+|"output_tokens":\s*\d+|"cache_read_tokens":\s*\d+' /root/sessions_export.jsonl | awk -F'[: ]' '
{
    val = $NF + 0
    if (/input_tokens/) input += val
    if (/output_tokens/) output += val
    if (/cache_read_tokens/) cache += val
}
END {
    total = input + cache + output
    printf "Non-cached input: %12d (full price)\n", input
    printf "Cache hits:       %12d (discounted)\n", cache
    printf "Output:           %12d (full price)\n", output
    printf "API total:        %12d\n", total
    printf "Cache rate:       %11d%%\n", int(cache * 100 / (input + cache))
}'
```

## Pitfalls

- **`hermes insights` total ≠ input + output**: It includes cache_read_tokens in the total.
- **Log file only has recent API calls**: agent.log gets overwritten on restart. Per-call cache detail (e.g. `cache=17472/17510 (99%)`) is ephemeral. Session DB is the durable source.
- **state.db is the source of truth**: Located at `~/.hermes/state.db`. Has columns: input_tokens, output_tokens, cache_read_tokens, cache_write_tokens, reasoning_tokens.
- **Export includes full message content**: The JSONL export can be large. Don't read it raw — grep for specific fields.
