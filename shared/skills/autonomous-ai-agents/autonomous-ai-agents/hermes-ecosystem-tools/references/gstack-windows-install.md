# G-Stack Windows Installation (Hermes)

**Source:** garrytan/gstack v1.57.10.0  
**Date:** 2026-06-12  
**Platform:** Windows 10 (git-bash / MSYS2)

## Installation Steps

```bash
# 1. Clone (shallow, fast)
cd $HERMES_HOME/skills
git clone --depth 1 https://github.com/garrytan/gstack.git

# 2. Install bun dependencies
cd gstack
bun install        # 227 packages

# 3. Build binaries (browse, design, make-pdf)
bun run build

# 4. Generate Hermes-adapted skills
bun run gen:skill-docs --host hermes

# 5. Move skills to Hermes skills directory
SKILLS_DIR="$HERMES_HOME/skills"
GEN_DIR="$SKILLS_DIR/gstack/.hermes/skills"
mkdir -p "$SKILLS_DIR/gstack-skills"
for dir in "$GEN_DIR"/gstack*; do
  mv "$dir" "$SKILLS_DIR/gstack-skills/$(basename "$dir")"
done

# 6. Clean up generated temp dir
rm -rf "$SKILLS_DIR/gstack/.hermes"

# 7. Register in Hermes config
hermes config set skills.external_dirs '["<full-path>/gstack-skills"]'

# 8. Reload (new session or /reload-skills)
```

## Key Facts

- **53 skills** generated (gstack, gstack-spec, gstack-review, gstack-ship, etc.)
- **Tool name rewrites** handled automatically by gen:skill-docs (Bash→terminal, Write→patch, etc.)
- **Path rewrites:** `CLAUDE.md`→`AGENTS.md`, `~/.claude/skills`→`~/.hermes/skills`
- **Browse binary** at `gstack/browse/dist/browse.exe` (requires Chromium via Playwright)
- **Hermes setup** does NOT auto-build — the `./setup` script only prints instructions for Hermes. Must use `bun run gen:skill-docs --host hermes` directly.

## Post-Install

- Skills are usable after `/reset` or starting a new `hermes` session
- Load with: `/skill gstack-spec` or launch with: `hermes -s gstack-spec`
