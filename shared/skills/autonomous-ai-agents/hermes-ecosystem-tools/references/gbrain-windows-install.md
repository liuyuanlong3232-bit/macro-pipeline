# GBrain Windows Installation (Hermes)

**Source:** garrytan/gbrain v0.42.40.0  
**Date:** 2026-06-12  
**Platform:** Windows 10 (git-bash / MSYS2)

## Installation Steps

### Method 1: Global bun install (recommended)

```bash
# Install globally
bun install -g github:garrytan/gbrain

# Run source directly (compiled .exe may have PATH issues)
alias gbrain="bun run ~/.bun/install/global/node_modules/gbrain/src/cli.ts"
```

### Method 2: Clone and run

```bash
cd $HERMES_HOME/skills
git clone --depth 1 https://github.com/garrytan/gbrain.git
cd gbrain
bun install
```

### Initialize

```bash
# PGLite mode — NO Docker needed
bun run ~/.bun/install/global/node_modules/gbrain/src/cli.ts init --pglite

# Without an embedding API key, use --no-embedding
bun run ~/.bun/install/global/node_modules/gbrain/src/cli.ts init --pglite --no-embedding
```

## Key Facts

- **PGLite mode** runs embedded (no Postgres server, no Docker). Only use Docker/Supabase for team deployments.
- **110 schema migrations** run on first init (version 1 → 115).
- **51 built-in skills** loaded on init.
- **0 pages initially** — user imports knowledge with `gbrain import <dir>`.
- **Cannot embed without API key** — needs OPENAI_API_KEY, ZEROENTROPY_API_KEY, or VOYAGE_API_KEY for vector embeddings.

## PATH Workaround for Windows

`bun install -g` compiles a `.exe` at `~/.bun/bin/gbrain.exe`. This binary requires `bun` on PATH at runtime, which often fails.

**Fix:** Run source directly:

```bash
bun run ~/.bun/install/global/node_modules/gbrain/src/cli.ts <command>
```

## Connecting to Hermes via MCP

```bash
# Start GBrain HTTP MCP server
bun run ~/.bun/install/global/node_modules/gbrain/src/cli.ts serve --http

# In Hermes, add MCP server
hermes mcp add gbrain --command "bun run <path>/src/cli.ts serve"
```

## Post-Install

- `gbrain import ~/my-knowledge` — bulk-import markdown
- `gbrain sync --watch` — live-sync a git repo
- `gbrain autopilot --install` — background daemon for nightly enrichment
- `gbrain doctor` — health check
