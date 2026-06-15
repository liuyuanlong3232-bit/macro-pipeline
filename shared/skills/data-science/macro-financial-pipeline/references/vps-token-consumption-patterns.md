# VPS Token Consumption Patterns

## Code Refactoring vs Normal Usage

### One Heavy Code Refactoring Session (6 files, 2026-06-14)
| Model | Tokens | Credit Multiplier | ≈Credits |
|-------|--------|------------------|----------|
| mimo-v2.5 | 40,655,926 | 1x | 40M |
| mimo-v2.5-pro | 195,405,750 | 2x-4x | 390M-822M |
| **Total** | **236,061,676** | — | **~430M-860M** |

### Normal Daily Chat/Report Analysis (Whole Day)
| Model | Tokens | Credit Multiplier | ≈Credits |
|-------|--------|------------------|----------|
| mimo-v2.5 | 645,338 | 1x | 645K |
| Total per day (normal) | ~750K | — | **~3M** |

### Lifetime Plan Lifespan
At heavy code refactoring pace:
| Plan | Credits | Days | Cost/Day |
|------|---------|------|----------|
| Lite ¥39 | 4.1B | ~5-8 days | ¥5-8 |
| Standard ¥99 | 11B | ~13-20 days | ¥5-8 |
| Pro ¥329 | 38B | ~45-90 days | ¥3-7 |

At normal analysis pace:
| Plan | Credits | Days | Cost/Day |
|------|---------|------|----------|
| Lite ¥39 | 4.1B | ~1365 days | ¥0.03 |
| Standard ¥99 | 11B | ~3666 days | ¥0.03 |

## Key Insight
The ¥39 Lite plan is more than sufficient for data analysis, report generation, and daily conversation. Code refactoring on VPS is the only activity that drains credits quickly. Keep heavy editing on local if cost matters.
