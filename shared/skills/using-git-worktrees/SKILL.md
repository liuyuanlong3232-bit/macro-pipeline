---
name: using-git-worktrees
description: Use when starting feature work that needs isolation from current workspace, or before executing implementation plans in a separate branch.
version: 1.0.0
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
metadata:
  hermes:
    tags: [git, worktree, isolation, branching, workspace]
    related_skills: [executing-plans, finishing-a-development-branch, subagent-driven-development]
---

# Using Git Worktrees

## Overview

Git worktrees create isolated workspaces sharing the same repository, allowing work on multiple branches simultaneously without switching.

**Core principle:** Systematic directory selection + safety verification = reliable isolation.

## Directory Selection

Follow this priority:

1. **Check existing:** `ls -d .worktrees worktrees 2>/dev/null` — if found, use it (`.worktrees` wins if both exist)
2. **Check config:** Look for worktree directory preference in `.hermes.md` or project config
3. **Ask user:** If nothing found, ask where to create worktrees

## Safety Verification

For project-local directories, verify they're gitignored:

```bash
git check-ignore -q .worktrees 2>/dev/null
```

**If NOT ignored:** Add to `.gitignore` and commit before proceeding.

## Creation Steps

### 1. Create Worktree

```bash
project=$(basename "$(git rev-parse --show-toplevel)")
git worktree add .worktrees/$BRANCH_NAME -b $BRANCH_NAME
cd .worktrees/$BRANCH_NAME
```

### 2. Run Project Setup

Auto-detect and run:

```bash
[ -f requirements.txt ] && pip install -r requirements.txt
[ -f pyproject.toml ] && pip install -e ".[all]" 2>/dev/null || pip install -e .
[ -f package.json ] && npm install
[ -f Cargo.toml ] && cargo build
[ -f go.mod ] && go mod download
```

### 3. Verify Clean Baseline

Run tests to ensure worktree starts clean:

```bash
pytest tests/ -q  # or project-appropriate command
```

**If tests fail:** Report failures, ask whether to proceed or investigate.

### 4. Report Location

```
Worktree ready at <full-path>
Tests passing (<N> tests, 0 failures)
Ready to implement <feature-name>
```

## Hermes Agent Integration

### With delegate_task

Subagents automatically get their own task_id for file operation isolation. You don't need worktrees for subagent isolation — but worktrees are valuable when YOU need to work on a branch without affecting the main workspace.

### Cleanup

When work is complete, use `finishing-a-development-branch` skill which handles:
- Merging or PR creation
- Worktree removal: `git worktree remove <path>`
- Branch cleanup

## Quick Reference

| Situation | Action |
|-----------|--------|
| `.worktrees/` exists | Use it (verify ignored) |
| Neither exists | Check config -> Ask user |
| Directory not ignored | Add to .gitignore + commit |
| Tests fail at baseline | Report + ask |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Skip ignore verification | Always `git check-ignore` first |
| Assume directory location | Follow priority: existing -> config -> ask |
| Proceed with failing tests | Report failures, get permission |
| Forget cleanup | Use finishing-a-development-branch skill |
