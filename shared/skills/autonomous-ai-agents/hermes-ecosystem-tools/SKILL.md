---
name: hermes-ecosystem-tools
description: "Install, configure, and integrate third-party community tools (G-Stack, GBrain, WebUI, Self-Evolution, etc.) into Hermes Agent on any platform."
version: 1.0.0
author: Hermes Agent
tags: [hermes, ecosystem, gstack, gbrain, integration, windows, bun]
---

# Hermes Ecosystem Tools

Class-level skill for discovering, installing, and integrating community tools and services into Hermes Agent. Covers the recurring patterns that span across multiple ecosystem projects.

## Trigger Conditions

Use this skill whenever the user asks you to:
- Install a community tool/skill/plugin for Hermes
- Integrate an external service (knowledge graph, web UI, memory backend)
- Set up GBrain, G-Stack, Hermes WebUI, Self-Evolution, or similar projects
- Find or evaluate Hermes ecosystem projects

## General Workflow

### 0. Discovery First

Always search for the project before promising auto-install:

```bash
# Search skills hub
hermes skills search <name>

# Broader web search
web_search(query="<project> hermes agent")
```

Then assess what kind of installation it needs:
- **Skills Hub install** → `hermes skills install <id>` (simplest)
- **git clone + setup script** → needs local build tools
- **bun/npm global install** → needs runtime
- **Docker Compose** → needs Docker daemon running
- **Standalone repo** → clone and configure independently

### 1. Skill-Based Tools (G-Stack Pattern)

G-Stack and similar structured skill collections use `bun` + a generator:

```bash
# Clone
git clone --depth 1 https://github.com/<owner>/<repo>.git

# Install deps (bun required)
cd <repo> && bun install

# Build binaries (if applicable)
bun run build

# Generate Hermes-adapted skills
bun run gen:skill-docs --host hermes

# Move generated skills to Hermes skills directory
SKILLS_DIR="$HERMES_HOME/skills"
GEN_DIR="$SKILLS_DIR/<repo>/.hermes/skills"
mkdir -p "$SKILLS_DIR/<category>"
for dir in "$GEN_DIR"/gstack*; do
  mv "$dir" "$SKILLS_DIR/<category>/$(basename "$dir")"
done

# Clean up generated temp directory
rm -rf "$SKILLS_DIR/<repo>/.hermes"

# Register with Hermes config
hermes config set skills.external_dirs '["<path-to-category-dir>"]'
```

**Important:** After adding external_dirs, the user needs to `/reset` or start a new session for skills to appear. The `/reload-skills` slash command may also work in-session.

### 2. CLI/MCP Tools (GBrain Pattern)

GBrain and similar standalone CLI tools install via `bun` or `npm`:

```bash
# Global install
bun install -g github:<owner>/<repo>

# OR clone + run directly
git clone --depth 1 https://github.com/<owner>/<repo>.git
cd <repo>
bun install
```

**Initialization** (GBrain specifically):
```bash
# PGLite mode — NO Docker needed, runs embedded
bun run <path-to-cli>.ts init --pglite

# Defer embedding if no API key
bun run <path-to-cli>.ts init --pglite --no-embedding

# Connect to Hermes via MCP
bun run <path-to-cli>.ts serve --http
```

Connect to Hermes via Hermes MCP tool (`hermes mcp add`).

### 3. Docker-Based Tools

For tools that need Docker (Supabase, Postgres, etc.):

```bash
# Check Docker daemon status
docker info
docker ps

# If Docker Desktop is installed but not running, start it:
"/c/Program Files/Docker/Docker/Docker Desktop.exe"
# Wait ~20s for daemon to become ready
```

## Windows-Specific Pitfalls

### Bun PATH Issues

When using `bun install -g`, the compiled `.exe` binary (`~/.bun/bin/<tool>.exe`) may fail with "bun is not installed in %PATH%" even though `bun` is available from npm/other sources.

**Fix:** Run the tool source directly instead:
```bash
bun run ~/.bun/install/global/node_modules/<package>/src/cli.ts -- <args>
```

Or create an alias:
```bash
alias <tool>="bun run ~/.bun/install/global/node_modules/<package>/src/cli.ts"
```

### G-Stack gen:skill-docs on Windows

The `gen:skill-docs --host hermes` generator auto-rewrites Claude Code tool names to Hermes equivalents:
- `Bash tool` → `terminal tool`
- `Write tool` → `patch tool`
- `Read tool` → `read_file tool`
- `Edit tool` → `patch tool`
- `Agent tool` → `delegate_task`
- `Grep tool` → `search for`
- `Glob tool` → `find files matching`

It also rewrites paths: `CLAUDE.md` → `AGENTS.md`, `~/.claude/skills` → `~/.hermes/skills`.

### Docker Desktop on Windows

- Installed at `C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe`
- Start with `terminal(background=true, command="/c/Program Files/Docker/Docker/Docker Desktop.exe")`
- Wait ~20s after starting before running `docker ps`
- Skip Docker when possible — check if the tool supports an embedded/standalone mode first

## API Key Writing Pitfall (Critical)

When writing API keys to Hermes `.env`, NEVER embed key values directly in heredoc strings or shell cat blocks. The `***` redaction or truncation will silently corrupt them.

**Symptoms:** A 32-char hex key shows as 10-12 chars in raw byte verification → it's been replaced with `***` literal text.

**Safe patterns:**

```python
# ✅ SAFE: Write from Python variables (keys stored in dict)
with open(env_path, 'a') as f:
    f.write(f'FRED_API_KEY={fred_actual_key}\\n')

# ✅ SAFE: Write a dedicated .py script, then run it
# write_keys.py contains: f.write(f'KEY={value}\\n') for each key

# ❌ NEVER: heredoc with embedded key text (gets mangled)
cat >> .env << 'EOF'
KEY=*** # will end up as literal '***...'
EOF
```

**Verification:** After writing keys, always check raw file bytes (terminal stdout is redacted):
```python
with open(env_path, 'rb') as f:
    for line in f.read().split(b'\\n'):
        if b'API_KEY=*** in line:
            val = line.split(b'=', 1)[1]
            print(f'{len(val)} chars')  # 32+ chars = real key, 10-12 = corrupted
```

## Related Skills

- `hermes-agent` — core Hermes Agent configuration
- `macro-financial-pipeline` — multi-source data pipeline (VPS deployment notes in references/)
- G-Stack (gstack-*) — YC methodology skill collection
- `llm-wiki` — alternative knowledge base pattern

## Verification Checklist

After installing a community tool:

- [ ] Binary/tool responds to `--help` or `--version`
- [ ] Skill appears in `hermes skills list` (if skill-based)
- [ ] Path aliases work across shell restarts (check `~/.bashrc`)
- [ ] MCP endpoint is reachable (if MCP-based)
- [ ] User can load skill with `/skill <name>` in a new session
