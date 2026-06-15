---
name: finishing-a-development-branch
description: Use when implementation is complete and you need to decide how to integrate the work — verify, present options, execute, clean up.
version: 1.0.0
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
metadata:
  hermes:
    tags: [git, branching, merge, pr, completion, workflow]
    related_skills: [verification-before-completion, executing-plans, subagent-driven-development]
---

# Finishing a Development Branch

## Overview

Guide completion of development work by presenting clear options and handling chosen workflow.

**Core principle:** Verify tests -> Present options -> Execute choice -> Clean up.

## The Process

### Step 1: Verify

**Before presenting options, verify work is complete:**

```bash
# Run project's test suite
pytest tests/ -q
# or appropriate command for the project
```

**If tests fail:** Stop. Don't proceed to Step 2. Fix first.

**If tests pass:** Continue.

### Step 2: Summarize Work

Prepare a concise summary:
- What was built/changed and why
- Key files modified
- Test coverage
- Any deviations from the original plan

### Step 3: Present Options

Present exactly these options:

```
Implementation complete and verified. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)
4. Discard this work

Which option?
```

### Step 4: Execute Choice

#### Option 1: Merge Locally

```bash
git checkout <base-branch>
git pull
git merge <feature-branch>
# Verify tests on merged result
pytest tests/ -q
git branch -d <feature-branch>
```

#### Option 2: Push and Create PR

```bash
git push -u origin <feature-branch>
```

Create PR with summary from Step 2.

#### Option 3: Keep As-Is

Report: "Keeping branch `<name>`. You can return to it later."

#### Option 4: Discard

**Confirm first:**
```
This will permanently delete:
- Branch <name>
- All commits since branching

Type 'discard' to confirm.
```

Wait for exact confirmation.

### Step 5: Document Results

Write completion summary to `.hermes/plans/` or memory:
- What was delivered
- Final verification status
- How it was integrated (merged, PR, kept, discarded)

## Hermes Agent Integration

### With Memory

On completion, persist to memory:
- What was built and the approach taken
- Any lessons learned or patterns discovered
- User preferences for integration workflow (merge vs PR vs keep)

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Skip test verification | Always verify before offering options |
| Open-ended "what next?" | Present exactly 4 structured options |
| Auto-discard without confirm | Require typed "discard" confirmation |
| No summary of work | Always summarize what was done |

## Red Flags

**Never:**
- Proceed with failing tests
- Merge without verifying
- Delete work without confirmation
- Force-push without explicit request
