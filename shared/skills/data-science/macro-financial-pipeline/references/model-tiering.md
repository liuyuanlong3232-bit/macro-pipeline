# Model Tiering & Naming

## Hermes Model Name Mapping

| Actual Model | Hermes Name (model.default) | Cost | Use Case |
|---|---|---|---|
| DeepSeek V4 Flash | `deepseek/deepseek-v4-flash` | Low (~$0.1/report) | Daily conversation, data queries, quick checks |
| DeepSeek V4 Pro | `deepseek/deepseek-v4-pro` | High (~$1-2/report) | Weekly reports — macro, metals, energy, agriculture |
| DeepSeek V3 (legacy) | `deepseek/deepseek-chat` | Medium | AVOID — this is V3, not V4 |

**Critical:** `deepseek/deepseek-chat` is V3, not V4 Flash. Flash and Pro are both in the V4 family and use the `deepseek-v4-*` naming pattern. Using `deepseek-chat` by mistake means paying for V3 instead of the faster/cheaper V4 Flash.

## Cron Per-Job Model Assignment

```python
# Daily conversation / data collection → Flash (cheap)
cronjob(action='create', name='数据采集', schedule='0 8 * * *',
        model={'model': 'deepseek/deepseek-v4-flash', 'provider': 'deepseek'})

# Weekly reports → Pro (quality)
cronjob(action='create', name='宏观周报', schedule='0 9 * * 1',
        model={'model': 'deepseek/deepseek-v4-pro', 'provider': 'deepseek'})
```

## VPS Report Generators (No LLM)

On a US VPS, deploy pure-Python report generators that do NOT call any LLM API. These:
- Read CSVs directly
- Fill templates with hardcoded analysis text
- Cost $0 to run (no API call)
- Never hallucinate data
- Run via Linux crontab, independent of Hermes

The fixed generators and LLM-powered reports can coexist — VPS generators cover you when the computer is off, Hermes cron with DeepSeek Pro covers you when it's on.
