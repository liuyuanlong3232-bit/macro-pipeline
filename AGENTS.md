# Hermes Project Development Rules

This file is the single authoritative development workflow for the Hermes project. If older notes, memories, scripts, or documentation conflict with this file, follow this file.

## Default Workflow

1. Local development on Windows
   - Modify code locally in the Windows workspace.
   - Run local syntax checks.
   - Run local functional validation when it will not trigger production side effects.

2. Git
   - Check `git status` and `git diff` before staging.
   - Stage only files related to the current task.
   - Do not use broad staging such as `git add -A` unless the user explicitly asks for it and the diff has been reviewed.
   - Commit the scoped change.
   - Push to GitHub.

3. VPS production deployment
   - Deploy by pulling from GitHub or by the current project deployment method.
   - Do not directly edit production code on the VPS.
   - Run syntax checks on the VPS after deployment.
   - Confirm the expected production file or module is present.

4. Verification
   - Confirm production files have updated.
   - Confirm key modules or strings exist when relevant.
   - Do not manually send daily reports unless explicitly requested.
   - Do not modify cron unless explicitly requested.

## Development Principles

- Use incremental updates by default.
- Do not refactor unless the user explicitly asks for a refactor.
- Preserve backward compatibility by default.
- Do not change existing features, weights, scores, models, or data interfaces unless the user explicitly requests it.
- Before any operation that may affect production, explain the operation and then execute only after the requested workflow allows it.
- Keep changes scoped to the current request.
- Prefer existing project style and structure over new abstractions.

## Production Safety

- The VPS is production.
- Never patch production files directly as the default workflow.
- Avoid commands that trigger report sending, email sending, or cron changes unless the user explicitly asks for them.
- Deployment validation should use read-only checks, hash/content checks, and syntax checks.

## Git Workflow

- GitHub is the single source of truth for Hermes project code.
- All code must be developed locally first.
- Check `git diff` before making changes.
- Stage only files related to the current task.
- Do not use `git add -A` by default.
- Before committing, check:
  - `git status`
  - `git diff --cached --stat`
  - `git diff --cached --check`
- Deploy to the VPS only after commit and push succeed.
- Code that has not been pushed must not be treated as the production version.

## VPS Production Workflow

- The VPS is only the production runtime environment, not the default development environment.
- Do not directly modify business code on the VPS.
- If an emergency production fix is required, sync it back to GitHub so code remains consistent.
- VPS updates must come from GitHub using `git pull --ff-only` or the established project deployment workflow.
- After deployment, run:
  - `python3 -m py_compile scripts/daily_report.py`
  - Necessary functional checks.
- Unless the user explicitly asks, do not:
  - Run commands that send daily report emails.
  - Modify cron.
  - Modify systemd.
  - Restart production services.

## Development Priority

Priority order:

1. `AGENTS.md` as the single authoritative development rules.
2. The current user's explicit request.
3. Existing project code.
4. Historical documentation, for reference only.
5. Deprecated old rules.

If historical documentation conflicts with `AGENTS.md`, always follow `AGENTS.md`.
