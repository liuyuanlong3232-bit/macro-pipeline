---
name: writing-skills
description: Use when creating new Hermes skills, editing existing skills, or adapting external skill content for the Hermes agent.
version: 1.0.0
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
metadata:
  hermes:
    tags: [skills, authoring, documentation, meta, process]
    related_skills: [test-driven-development, brainstorming]
---

# Writing Skills

## Overview

Skills are reusable reference guides for proven techniques, patterns, or tools. They help the agent find and apply effective approaches across sessions.

**Core principle:** If you didn't test the skill with a real scenario, you don't know if it teaches the right thing.

## What is a Skill?

**Skills are:** Reusable techniques, patterns, tools, reference guides
**Skills are NOT:** Narratives about solving one specific problem

## When to Create a Skill

**Create when:**
- Technique wasn't intuitively obvious
- You'd reference this again across sessions or projects
- Pattern applies broadly (not project-specific)

**Don't create for:**
- One-off solutions
- Standard practices well-documented elsewhere
- Project-specific conventions (put in `.hermes.md`)

## Hermes Skill Structure

```
skills/<category>/<skill-name>/
  SKILL.md              # Main reference (required)
  supporting-file.*     # Only if needed
```

### SKILL.md Format

```yaml
---
name: skill-name
description: Use when [specific triggering conditions]
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [relevant, search, terms]
    related_skills: [other-skill-names]
---

# Skill Name

## Overview
Core principle in 1-2 sentences.

## When to Use
Bullet list with symptoms and use cases.
When NOT to use.

## Core Pattern
Steps, before/after, the actual technique.

## Hermes Agent Integration
How this works with delegate_task, memory, terminal, etc.

## Quick Reference
Table or bullets for scanning.

## Common Mistakes
What goes wrong + fixes.
```

### Key Rules

- **`name`**: letters, numbers, hyphens only
- **`description`**: Start with "Use when..." — triggers only, NOT workflow summary
- **`tags`**: terms the agent would search for
- **`related_skills`**: skills that pair with this one

### Description Anti-Pattern

```yaml
# BAD: Summarizes workflow — agent may follow description instead of reading skill
description: Use for debugging — gather evidence, form hypothesis, test minimally

# GOOD: Just triggers — agent reads full skill for process
description: Use when encountering any bug, test failure, or unexpected behavior
```

## Testing Skills

### Before Writing

Run the scenario WITHOUT the skill. Document:
- What choices the agent made
- What rationalizations it used
- Where it went wrong

### After Writing

Run same scenario WITH the skill. Verify the agent now follows the process.

### Discipline-Enforcing Skills

For skills that enforce rules (TDD, verification):
- Test with pressure scenarios
- Add rationalization tables countering specific excuses
- Add "Red Flags" lists for self-checking
- Close every loophole explicitly

## Token Efficiency

Skills load into every conversation where they're relevant. Be concise.

- Getting-started skills: <150 words
- Frequently-loaded skills: <200 words
- Other skills: <500 words
- Move heavy reference to separate files
- One excellent example beats many mediocre ones

## Skill Creation Checklist

1. **Baseline:** Run scenario without skill, document failures
2. **Write:** Address specific baseline failures, YAML frontmatter, core pattern
3. **Test:** Run scenario with skill, verify compliance
4. **Refine:** Close loopholes found during testing
5. **Deploy:** Place in `skills/<category>/<name>/SKILL.md`

## The Bottom Line

Skills are tested documentation. Same rigor as code: test first, iterate, keep concise.
