---
name: dispatching-parallel-agents
description: Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies. Dispatches focused delegate_task subagents in parallel.
version: 1.0.0
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
metadata:
  hermes:
    tags: [delegation, parallel, subagents, concurrency, efficiency]
    related_skills: [subagent-driven-development, writing-plans]
---

# Dispatching Parallel Agents

## Overview

Delegate independent tasks to focused subagents via `delegate_task`. Each subagent gets isolated context — they never inherit your session history. You construct exactly what they need. This preserves your own context for coordination.

**Core principle:** One agent per independent problem domain. Let them work concurrently.

## When to Use

**Use when:**
- 2+ tasks with different problem domains
- Tasks can be understood independently
- No shared state between investigations
- Each task is self-contained enough for a subagent

**Don't use when:**
- Tasks are related (fixing one might fix others)
- Need to understand full system state first
- Agents would edit the same files
- You're still in discovery phase (use brainstorming first)

## The Pattern

### 1. Identify Independent Domains

Group work by what's independent:
- Different files, different subsystems, different concerns
- Each domain can succeed or fail without affecting others

### 2. Create Focused Agent Tasks

Each agent gets via `delegate_task`:
- **goal:** One clear objective
- **context:** All information needed — error messages, file paths, constraints
- **toolsets:** Only what's needed (e.g., `['terminal', 'file']`)

### 3. Dispatch in Parallel

```python
# Batch mode — runs up to 3 concurrently
delegate_task(tasks=[
    {
        "goal": "Fix authentication validation in auth_handler.py",
        "context": "Error: [paste error]. File: src/auth_handler.py. Run: pytest tests/test_auth.py -v",
        "toolsets": ["terminal", "file"]
    },
    {
        "goal": "Fix rate limiting in api_gateway.py",
        "context": "Error: [paste error]. File: src/api_gateway.py. Run: pytest tests/test_gateway.py -v",
        "toolsets": ["terminal", "file"]
    },
    {
        "goal": "Fix CSV export formatting in reports.py",
        "context": "Error: [paste error]. File: src/reports.py. Run: pytest tests/test_reports.py -v",
        "toolsets": ["terminal", "file"]
    }
])
```

### 4. Review and Integrate

When agents return:
1. Read each summary — understand what changed
2. Verify fixes don't conflict (same files edited?)
3. Run full test suite / verification
4. Integrate all changes

## Agent Prompt Structure

Good prompts are:

1. **Focused** — one clear problem domain
2. **Self-contained** — all context needed to understand the problem
3. **Specific about output** — what should the agent return?
4. **Constrained** — what should the agent NOT do?

```python
delegate_task(
    goal="Fix the 3 failing tests in tests/test_auth.py",
    context="""
    Failing tests:
    1. test_token_expiry — expects 401, gets 200
    2. test_refresh_flow — refresh token not invalidated
    3. test_concurrent_sessions — race condition on session store

    Root cause likely in src/auth/session.py or src/auth/tokens.py.

    Constraints:
    - Do NOT modify test expectations unless tests are wrong
    - Do NOT change the public API
    - Run: pytest tests/test_auth.py -v to verify

    Return: Summary of root cause and changes made.
    """,
    toolsets=["terminal", "file"]
)
```

## Hermes-Specific Notes

- `delegate_task` supports batch mode: pass `tasks=[...]` for parallel execution
- Max 3 concurrent subagents (`MAX_CONCURRENT_CHILDREN`)
- Max depth 2 (subagents cannot spawn their own subagents)
- Subagents cannot use: `delegate_task`, `clarify`, `memory`, `send_message`
- Results returned as JSON with status, summary, duration, token usage, and tool trace

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Too broad goal | One clear problem domain per agent |
| No context | Paste error messages, file paths, commands |
| No constraints | Specify what NOT to change |
| Vague output request | "Return summary of root cause and changes" |
| Related tasks split | Investigate together if fixing one might fix others |

## Verification

After agents return:
1. **Review each summary** — understand what changed
2. **Check for conflicts** — did agents edit same code?
3. **Run full suite** — verify all fixes work together
4. **Spot check** — agents can make systematic errors; don't trust blindly
