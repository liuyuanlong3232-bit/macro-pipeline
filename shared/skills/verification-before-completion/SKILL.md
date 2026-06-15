---
name: verification-before-completion
description: Use when about to claim work is complete, fixed, or passing — requires running verification commands and confirming output before making any success claims. Evidence before assertions always.
version: 1.0.0
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
metadata:
  hermes:
    tags: [verification, quality, testing, completion, honesty]
    related_skills: [test-driven-development, systematic-debugging, finishing-a-development-branch]
---

# Verification Before Completion

## Overview

Claiming work is complete without verification is dishonesty, not efficiency.

**Core principle:** Evidence before claims, always.

**Violating the letter of this rule is violating the spirit of this rule.**

## User Workflow Corrections (embedded preferences)

This user has repeatedly corrected three patterns. Embed them now:

### 1. After every modification, LIST changes explicitly
```
BAD:  "I fixed the issue" (vague)
GOOD: "I patched send_email.py — changed 3 things:
       1. Line 119: swapped naive split for streaming parser
       2. Line 154: extracted _is_sep() helper, -20 lines
       3. Line 200: fixed separator detection"
```

If the user has to ask "what did you change", you skipped this step.

### 2. Prefer `patch` over full-file rewrite
```
BAD:  Rewrite entire file → user's modules disappear → data connections break
GOOD: Use patch() with old_string/new_string → only the targeted lines change
```

Full rewrite is ONLY acceptable when creating a new file, or when the ENTIRE
existing content must be replaced and you have VERIFIED no data/module is lost
by comparing against the original line by line. "凭记忆重写" (rewrite from
memory) is never acceptable — you will lose content every time.

### 3. Verify ALL output variants, not just one
```
BAD:  Test 1 report → "all good" → 3 other reports have broken tables
GOOD: Test EVERY variant (macro/energy/agri_intl/agri_cn/metals) before
      claiming completion. Different reports may use different Markdown
      formats (some with leading `|`, some without).
```

When the task involves multiple outputs (report templates, data formats,
platform targets), run verification on EVERY one. The first one working
does not mean they all work.

### 4. After every modification, explicitly LIST what changed

```
BAD:  "好了，改完了" (user has to ask what you did)
GOOD: "本次修改 agri_weekly.py:
       1. 恢复了四、进口与政策模块
       2. 加回了尾部声明语句
       3. 修复了Tushare .env路径指向
       （energy_weekly.py 未改动）"
```

User stated clearly: "请你以后把改了什么具体都在对话框告诉我，ok？"
If you can't produce this list, you haven't finished communicating the change.

### 5. Re-read reference files before every modification

When a user has provided reference files (prompts in `prompts/`, templates,
spec docs), re-read them BEFORE touching code — not after. Your memory of
what they contain is unreliable across turns.

Also: NEVER modify these reference/prompt files themselves. They are locked
templates. Only the code that reads them should change.

### 6. Test every output variant, not just one

When the task involves multiple outputs (report templates, data formats,
platform targets), run verification on EVERY variant before claiming done.

```
BAD:  Test only metals report → "表格正常" → agri reports have broken tables
GOOD: Run ALL 5 reports (macro/energy/agri_intl/agri_cn/metals) → confirm
      all produce correct tables
```

Different variants may use different Markdown conventions (some with leading
`|`, some without). Testing one does not prove the others work.

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you haven't run the verification command in this turn, you cannot claim it passes.

## The Gate Function

```
BEFORE claiming any status:

1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
5. ONLY THEN: Make the claim

Skip any step = lying, not verifying
```

## Common Failures

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | Test output: 0 failures | Previous run, "should pass" |
| Build succeeds | Build command: exit 0 | Linter passing |
| Bug fixed | Original symptom test passes | "Code changed, assumed fixed" |
| Requirements met | Line-by-line checklist | Tests passing alone |
| Agent completed | VCS diff shows changes | Agent reports "success" |

## Red Flags — STOP

If you catch yourself:
- Using "should", "probably", "seems to"
- Expressing satisfaction before verification ("Great!", "Done!")
- About to commit/push without verification
- Trusting agent success reports without checking
- Relying on partial verification
- Thinking "just this once"

**ALL of these mean: RUN THE VERIFICATION.**

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "Should work now" | RUN the verification |
| "I'm confident" | Confidence != evidence |
| "Just this once" | No exceptions |
| "Agent said success" | Verify independently |
| "Partial check is enough" | Partial proves nothing |

## Key Patterns

**Tests:**
```
OK:  [Run test command] [See: 34/34 pass] "All tests pass"
BAD: "Should pass now" / "Looks correct"
```

**Requirements:**
```
OK:  Re-read plan -> checklist -> verify each -> report gaps or completion
BAD: "Tests pass, phase complete"
```

**Agent delegation:**
```
OK:  Agent reports success -> check diff -> verify changes -> report actual state
BAD: Trust agent report
```

## Hermes Agent Integration

### After delegate_task

When subagents return results:
1. Read the summary
2. Check what files were actually modified
3. Run verification commands yourself
4. Only then claim the task is complete

### With Memory

Record verification outcomes. If a verification method was insufficient (missed a bug), record that so future sessions use better verification.

## The Bottom Line

**No shortcuts for verification.**

Run the command. Read the output. THEN claim the result.

This is non-negotiable.
