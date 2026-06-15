---
name: hermes-ecosystem-claims
description: "Evaluate, search, and verify claimed Hermes Agent ecosystem projects, plugins, and features. Map community terminology to official capabilities and set realistic expectations."
version: 1.1.0
author: Hermes Agent
metadata:
  hermes:
    tags: [hermes, ecosystem, community, research, chinese, verification, skills-hub]
    related_skills: [hermes-agent, github-repo-management]
---

# Hermes Ecosystem Claims Verifier

When a user asks you to install a Hermes "plugin", "slot", "core system", or ecosystem project they heard about, use this workflow to verify what actually exists vs. what is community reframing or marketing material.

## Triggers

- User asks to install something described as a "Hermes plugin / slot / core system"
- User references Chinese community terminology like "五个插槽", "身份系统", "gbrain", "g stack"
- User says "能安装吗？" about a claimed Hermes feature
- User asks you to "自动安装所有" or "一键部署" ecosystem components
- User expresses expectations of self-maintaining/self-updating feature installation

## Step 1: Search and Classify

Always search for claimed projects across multiple sources. Classify each finding:

| Classification | Meaning | Example |
|---|---|---|
| **Official feature** | Built into Hermes core, use `hermes config` or CLI | SOUL.md, memory, STT/TTS, compression, `/personality` |
| **Hub skill** | Installable via `hermes skills install` or direct URL | G-Stack (`skills-sh/garrytan/gstack/gstack`), dockwatch |
| **Standalone project** | Separate GitHub repo, needs git clone + manual setup | GBrain (Docker), Hermes WebUI, self-evolution |
| **READ ME list** | Not installable — a curated directory/resource list | awesome-hermes-agent (`0xNyk/awesome-hermes-agent`) |
| **Not real** | No GitHub repo, no community adoption, no code | "RTK technology", "genetic algorithm" as built-in, "211 Chinese templates" (as official) |

### Known Ecosystem Projects (verified)

| Name | GitHub | Stars | Type | Hermes Install Method |
|------|--------|-------|------|----------------------|
| **G-Stack** | `garrytan/gstack` | — | Hub skill (skills.sh) + standalone toolkit | `hermes skills install skills-sh/garrytan/gstack/gstack` OR `git clone + bun run gen:skill-docs --host hermes` |
| **GBrain** | `garrytan/gbrain` | — | Standalone Docker project | Docker compose + MCP HTTP connection |
| **Hermes WebUI** | `nesquena/hermes-webui` | 14.2K⭐ | Standalone web app (Python) | `git clone && pip install && python app.py` |
| **Hermes Studio** | `EKKOLearnAI/hermes-web-ui` | 7.7K⭐ | Standalone web app (TypeScript/npm) | `npm install -g hermes-web-ui && hermes-web-ui start` |
| **awesome-hermes-agent** | `0xNyk/awesome-hermes-agent` | 1.7K⭐ | README resource list | Not installable — browse on GitHub |
| **Hermes Self-Evolution** | `NousResearch/hermes-agent-self-evolution` | 4.0K⭐ | Standalone CLI tool (Python) | `git clone && pip install -e ".[dev]"` |

## Step 2: Map Community Terminology to Official Features

Chinese community often reframes Hermes features with poetic names. Always translate:

| Community term | Actual Hermes feature |
|---|---|
| 身份系统 / Soul / 插槽1 | `~/.hermes/SOUL.md` + `/personality` command |
| 记忆系统 / Palace | `session_search`, `hermes memory`, FTS5 session store |
| 感知能力 / Perception | `web_search`, `web_extract`, `browser_*`, Jina, OCR tools |
| 表达能力 / Expression | STT (Whisper), TTS (`/voice`, Edge/ElevenLabs), `image_gen` |
| 效率 / Evolution | `compression.*` config, skills system, Curator (not "genetic algorithm") |
| G-Stack / g stack | Garry Tan's YC startup methodology skill collection — hub skill on skills.sh |
| GBrain / g brain | Garry Tan's personal knowledge graph — standalone Docker project, connects via MCP |
| Hermes WebUI | nesquena/hermes-webui — standalone Python web app |
| Hermes Studio | EKKOLearnAI/hermes-web-ui — standalone npm package |
| awesome-hermes-agent | 0xNyk/awesome-hermes-agent — README resource list |
| hermes-agent-self-evolution | NousResearch/hermes-agent-self-evolution — DSPy+GEPA evolution framework |

## Step 3: Set Realistic Expectations

When the user expects auto-install of everything with ongoing self-maintenance:

1. **Clarify what type each project is** — don't lump all into "plugins"
2. **Explain the install method** for each (skill install vs git clone vs Docker)
3. **Be honest about limitations** — Hermes has a Curator for skill cleanup, but no "auto-find-new-versions-and-update" daemon for third-party projects
4. **Offer to install what's actually installable, document why others aren't**

## Pitfalls

- **Don't pretend you can auto-install everything** — be transparent about what needs manual setup (Docker, npm install, separate Python env)
- **Don't confuse community reframing with official plug-in slots** — "五个插槽" is a conceptual teaching tool, not an architected feature
- **Don't save environment-dependent failures** (missing Docker, no npm, rate limits) as skill content — those are setup state, not durable rules
- **Don't harden tool refusal claims** — "X tool is broken" becomes a self-imposed constraint. Capture the fix, not the failure
- **Skills Hub installs can hang on slow connections** — when `hermes skills install <hub-name>` times out (30s+), fall back to `hermes skills install "https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>/SKILL.md" --name <name>`
- **`./setup --host hermes` in G-Stack may just print instructions and exit** — G-Stack's setup script handles Claude Code/Codex/Cursor directly but only prints guidance for Hermes. The real install path is `bun run gen:skill-docs --host hermes` inside the cloned repo.

## G-Stack Installation Workflow (Hermes-specific)

When a user asks to install G-Stack for Hermes, follow these steps:

### 1. Clone and Prepare

```bash
cd $HERMES_HOME/skills
git clone --depth 1 https://github.com/garrytan/gstack.git
cd gstack
bun install              # Install dependencies (227+ packages)
bun run build            # Build browse, design, make-pdf binaries
```

The build compiles Windows .exe binaries automatically when run in MSYS/Git Bash.

### 2. Generate Hermes-adapted Skills

```bash
bun run gen:skill-docs --host hermes
```

This creates skills under `gstack/.hermes/skills/gstack-*/SKILL.md` — each skill has:
- Hermes-appropriate paths (`.hermes/skills/gstack` instead of `.claude/skills/gstack`)
- Tool name rewrites (`terminal tool` for `Bash tool`, `patch tool` for `Edit tool`, etc.)
- AGENTS.md references instead of CLAUDE.md
- Suppressed Claude Code-specific resolvers (CODEX_SECOND_OPINION, REVIEW_ARMY, etc.)

### 3. Move Skills to Hermes Skills Directory

```bash
mkdir -p $HERMES_HOME/skills/gstack-skills
for dir in gstack/.hermes/skills/gstack*; do
  mv "$dir" "$HERMES_HOME/skills/gstack-skills/$(basename "$dir")"
done
```

### 4. Register with Config

```bash
hermes config set skills.external_dirs '["/path/to/hermes/skills/gstack-skills"]'
```

Then `/reload-skills` or start a new session.

### 5. Browser Binary

G-Stack includes a headless Chromium-based QA browser (`browse/dist/browse.exe`). It's already compiled during `bun run build`. The skill preamble in each SKILL.md sets up `GSTACK_BROWSE` and the session tracking directory.

### Known Issues

- **53 skills ≈ 825K total tokens** — loading all G-Stack skills in one session is expensive. Only load the specific skills you need (e.g. `/skill gstack-spec` for spec writing, `/skill gstack-review` for code review).
- **Windows file copies** — G-Stack's setup script auto-detects MSYS/Git Bash and uses `cp -R` instead of symlinks. Re-run `bun run gen:skill-docs` after `git pull` to refresh stale copies.
- **browse binary** requires Chromium — Playwright installs it automatically via `bun run build`.

## Reference Files

- `references/five-slot-mapping.md` — detailed mapping of Chinese community "five slots" framework to real Hermes features, with install status for each
- `references/ecosystem-discovery-protocol.md` — step-by-step protocol for discovering and verifying Hermes ecosystem projects from scratch

## Workflow: User Says "Install X plugin for Hermes"

```
1. Search web for "hermes agent X" + "hermes X plugin" + "github X hermes"
2. Check Skills Hub: hermes skills search X
3. Classify the finding (see table above)
4. If skill: install it (try hub name first, fall back to raw URL)
5. If standalone: explain setup requirements
6. If README/not real: explain what it actually is
7. If community reframing: map to real feature name + show how to use it
8. Never promise auto-updates or self-healing for third-party projects
```
