# Ecosystem Discovery Protocol

Step-by-step protocol for discovering and verifying Hermes ecosystem projects from scratch, based on the "five claimed projects" investigation.

## Phase 1: Parallel Search

For each claimed project name, fire a batch of web searches:

```python
queries = [
    f'Hermes Agent "{project_name}" plugin',
    f'"{project_name}" hermes github',
    f'"{project_name}" hermes agent',
]
```

Check the Skills Hub simultaneously:

```bash
hermes skills search "<project_name>"
```

## Phase 2: Classify Each Result

Use the classification table from SKILL.md. Key distinctions:

- **Does the result have a GitHub repo with code?** → standalone project or hub skill
- **Is it a README-only repo?** → resource list (not installable)
- **Is it only mentioned in blog posts / forum content?** → community reframing or not real
- **Does it appear in official docs (hermes-agent.nousresearch.com)?** → official feature

## Phase 3: Validate with Raw Data

For GitHub projects:
```bash
# Check if SKILL.md exists (skills.sh indexed pattern)
curl -sI "https://raw.githubusercontent.com/<owner>/<repo>/main/<path>/SKILL.md" | head -1

# Check repo exists
curl -s "https://api.github.com/repos/<owner>/<repo>" | grep -E '"name"|"description"|"stargazers_count"'
```

For multi-agent projects like G-Stack, check the `hosts/` directory for Hermes support:
```bash
# Check if the project has a native Hermes host config
curl -sI "https://raw.githubusercontent.com/<owner>/<repo>/main/hosts/hermes.ts" | head -1
```
A `hosts/hermes.ts` file means the project produces Hermes-adapted skills using its own generation script. The `./setup --host hermes` command may just print installation instructions rather than auto-installing — check the setup script's `case "$HOST" in hermes)` block to see the actual behavior.

For claimed official features:
```bash
web_extract("https://hermes-agent.nousresearch.com/docs/...")
```

## Phase 4: Map Terminology

When the user's terminology doesn't match official Hermes naming, look for conceptual equivalence:

- "插槽 / slot" → often a thematic category, not a code-level module
- "自动安装全部" → almost always unrealistic; decompose into what's a skill, what's a standalone project, what's conceptual
- "后台自检 / 自动更新" → Hermes has no unified auto-update daemon for third-party tools

## Phase 5: Honest Delivery

Format the response as a table with three columns:
| Project | Status (✅/⚠️/❌) | What To Do |
Then explain each row. Never promise auto-install of something that needs Docker, git clone, or npm install without caveats.

## Phase 6: When Setup Scripts Only Print Guidance (G-Stack Pattern)

Some ecosystem projects are designed with Claude Code as the primary target, and their `./setup --host hermes` command only prints guidance text instead of actually installing. When this happens:

1. **Check `hosts/<agent>.ts`** — the host config file has the real skill generation logic
2. **Run the skill generation directly** — look for package.json scripts like `gen:skill-docs`
3. **Check what the host config rewrites** — look at `pathRewrites` (path substitution patterns) and `toolRewrites` (tool name mapping) in the host config
4. **Move generated skills manually** — the generator outputs to `.hermes/skills/gstack-*/` relative to the project root; these need to be moved to `$HERMES_HOME/skills/`
5. **Register with config** — add `skills.external_dirs` to Hermes config if the skills are in a non-standard location
6. **Build binaries** — many toolkits include compiled binaries (browse, design tools); check `package.json` scripts for `build`

### Key Indicators a Project Shares This Pattern

- `./setup --host hermes` exits with `echo` instructions instead of running install logic
- A `hosts/hermes.ts` config file exists (signals the project knows about Hermes)
- `package.json` has a `gen:skill-docs` script
- Path rewrites reference `.hermes/skills/` (instead of `.claude/skills/`)
- Tool rewrites map `Bash tool → terminal tool`, `Edit tool → patch tool`, etc.
