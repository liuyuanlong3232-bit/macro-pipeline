---
name: executing-plans
description: Use when you have a written implementation plan to execute. Load plan, review critically, execute tasks with subagents, verify at checkpoints.
version: 1.0.0
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
metadata:
  hermes:
    tags: [execution, plans, implementation, workflow, delegation]
    related_skills: [writing-plans, subagent-driven-development, dispatching-parallel-agents, verification-before-completion, finishing-a-development-branch]
---

# Executing Plans

## Overview

Load plan, review critically, execute all tasks, report when complete.

**Core principle:** Follow the plan. Use subagents to keep context clean. Stop when blocked — don't guess.

**Prefer subagent-driven-development** when subagents are available (they are in Hermes). This skill is the fallback for sequential single-agent execution.

## The Process

### Step 1: Load and Review Plan

1. Read plan file from `.hermes/plans/`
2. Review critically — identify questions or concerns
3. If concerns: raise them with the user before starting
4. If no concerns: proceed

### Step 2: Execute Tasks

For each task in the plan:

**If tasks are independent**, use `delegate_task` batch mode (see dispatching-parallel-agents skill):

```python
delegate_task(tasks=[
    {"goal": "Task 1 description", "context": "...", "toolsets": ["terminal", "file"]},
    {"goal": "Task 2 description", "context": "...", "toolsets": ["terminal", "file"]},
])
```

**If tasks are sequential**, execute one at a time:

1. Execute the task (directly or via `delegate_task` for isolation)
2. Run verifications as specified in the plan
3. Confirm completion before moving to next task

### Step 3: Checkpoint Reviews

After completing each logical group of tasks:
- Run the verification commands from the plan
- Check that the work matches the spec
- If something diverges from the plan, stop and discuss

### Step 4: Complete Development

After all tasks complete and verify:
- Use the **finishing-a-development-branch** skill
- Follow that skill to verify, present options, execute choice

## When to Stop and Ask

**STOP immediately when:**
- Hit a blocker (missing dependency, test fails, instruction unclear)
- Plan has critical gaps preventing progress
- You don't understand an instruction
- Verification fails repeatedly (3+ attempts)

**Ask for clarification rather than guessing.**

## Documentation

Throughout execution:
- Record decisions and deviations in `.hermes/plans/` alongside the plan
- If the plan needed modification, update it with what actually happened
- On completion, write a summary of what was built, any deviations, and verification results

## Hermes Agent Integration

### With delegate_task

For each plan task, dispatch a focused subagent:

```python
delegate_task(
    goal="[Task title from plan]",
    context="""
    Plan task: [paste task details from plan]
    
    Files to modify: [list from plan]
    Verification: [command from plan]
    
    Constraints:
    - Follow the plan exactly
    - Do NOT make changes outside the specified files
    - Run verification before reporting completion
    """,
    toolsets=["terminal", "file"]
)
```

### With Memory

After plan execution completes:
- Key architectural decisions should be persisted to memory
- Deviations from the plan and their reasons are valuable context
- Record what verification methods worked for this type of change

## Remember

- Review plan critically first
- Follow plan steps exactly
- Don't skip verifications
- Stop when blocked, don't guess
- Use subagents to keep context clean
- Document what actually happened vs. what was planned
