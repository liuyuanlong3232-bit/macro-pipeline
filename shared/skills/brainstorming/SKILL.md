---
name: brainstorming
description: Use before any non-trivial task — research, feature design, system configuration, creative work, or any goal requiring more than a couple of tool calls. Explores intent, requirements, and approach before execution.
version: 1.0.0
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
metadata:
  hermes:
    tags: [planning, design, brainstorming, requirements, discovery]
    related_skills: [writing-plans, subagent-driven-development]
---

# Brainstorming Ideas Into Designs

Turn ideas into fully formed designs through collaborative dialogue. Understand context, ask questions one at a time, present a design, get approval.

<HARD-GATE>
Do NOT invoke any implementation skill, write any code, execute any plan, or take any action until you have presented a design and the user has approved it. This applies to EVERY non-trivial task regardless of perceived simplicity.
</HARD-GATE>

## Anti-Pattern: "This Is Too Simple To Need A Design"

Every non-trivial task goes through this process. A config change, a research task, a simple feature — all of them. "Simple" tasks are where unexamined assumptions cause the most wasted work. The design can be short (a few sentences for truly simple tasks), but you MUST present it and get approval.

## Checklist

Complete these in order:

1. **Explore context** — check relevant files, docs, recent history, current state
2. **Ask clarifying questions** — one at a time, understand purpose/constraints/success criteria
3. **Propose 2-3 approaches** — with trade-offs and your recommendation
4. **Present design** — in sections scaled to complexity, get user approval after each section
5. **Write design doc** — save to `.hermes/plans/YYYY-MM-DD-<topic>-design.md`
6. **Spec self-review** — check for placeholders, contradictions, ambiguity, scope
7. **User reviews written spec** — ask user to review before proceeding
8. **Transition to implementation** — invoke writing-plans skill to create implementation plan

## The Process

**Understanding the idea:**

- Check out the current state first (files, docs, config, recent changes)
- Before asking detailed questions, assess scope: if the request describes multiple independent subsystems, flag this immediately and help decompose
- Ask questions one at a time to refine the idea
- Prefer multiple choice questions when possible
- Focus on understanding: purpose, constraints, success criteria

**Exploring approaches:**

- Propose 2-3 different approaches with trade-offs
- Lead with your recommended option and explain why
- For non-coding tasks (research, configuration, data gathering), approaches might be: which tools to use, what order to investigate, what to prioritize

**Presenting the design:**

- Scale each section to its complexity: a few sentences if straightforward, up to 200-300 words if nuanced
- Ask after each section whether it looks right so far
- For coding tasks: architecture, components, data flow, error handling, testing
- For research tasks: sources, methodology, deliverables, success criteria
- For operational tasks: steps, rollback plan, verification method

**Design for isolation and clarity:**

- Break work into smaller units with clear boundaries
- Each unit should be independently understandable and verifiable
- Smaller units are also better suited for delegate_task subagents

## After the Design

**Documentation:**

- Write the validated design to `.hermes/plans/YYYY-MM-DD-<topic>-design.md`
- This serves as both the spec and the memory artifact for future reference

**Spec Self-Review:**

1. **Placeholder scan:** Any "TBD", "TODO", incomplete sections?
2. **Internal consistency:** Do sections contradict each other?
3. **Scope check:** Focused enough for a single implementation plan?
4. **Ambiguity check:** Could any requirement be interpreted two ways?

Fix issues inline.

**User Review Gate:**

> "Spec written to `<path>`. Please review and let me know if you want changes before we proceed."

Wait for approval. Only then invoke writing-plans skill.

## Key Principles

- **One question at a time** — don't overwhelm
- **Multiple choice preferred** — easier to answer
- **YAGNI ruthlessly** — remove unnecessary scope
- **Explore alternatives** — always propose 2-3 approaches
- **Incremental validation** — get approval before moving on

## Hermes Agent Integration

### With delegate_task

For scope assessment, dispatch investigation subagents:

```python
delegate_task(
    goal="Survey the current state of [system/component]",
    context="Report: what exists, what's configured, what's missing. Do NOT make changes.",
    toolsets=['terminal', 'file']
)
```

### With Memory

After the design is approved, key decisions and rationale should be recorded in memory for future sessions. Use the active memory provider to persist:
- Why this approach was chosen over alternatives
- Key constraints discovered during brainstorming
- User preferences revealed during the conversation

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "This is just a simple change" | Simple changes have assumptions. 2-minute design catches them. |
| "I already know what to do" | Your confidence isn't evidence. Present the plan. |
| "User wants it done fast" | Fast wrong work is slower than fast right work. |
| "It's not a coding task" | Research, config, and ops tasks need designs too. |
| "Let me just explore first" | Exploration IS part of the design. Do it here. |
