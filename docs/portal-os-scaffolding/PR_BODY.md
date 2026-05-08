## Summary

Bootstrap the **Portal Improvement Operating System** for this portal. Infrastructure-only. No src/, tests/, middleware, or backend changes.

This is a scaffolding PR — it lands the operating surface (commands, subagents, hooks, workflows, artifacts) that will drive all future portal-improvement work through GitHub-first, mobile-friendly loops.

## Scope (32 files, all additive)

- `CLAUDE.md` — thin pointer to the Portal OS
- `.claude/README.md` + `settings.json`
- `.claude/commands/` × 6: `portal-audit`, `portal-scorecard`, `portal-tranche-plan`, `portal-tranche-fix`, `portal-regression-guard`, `portal-readiness`
- `.claude/agents/` × 5: `portal-route-auditor`, `portal-admin-surface-auditor`, `portal-flow-continuity-auditor`, `portal-tranche-verifier`, `portal-regression-sentinel`
- `.claude/hooks/` × 4: `session_start`, `pre_tool_use` (tranche-scope + quarantine + secrets), `subagent_stop` (evidence required), `stop` (no dead air)
- `.github/workflows/` × 3: `claude.yml` (@claude mention handler), `portal-pr-guard.yml` (typecheck + vitest + playwright + registry-presence on every PR), `portal-drift-weekly.yml` (Monday 06:00 UTC cron)
- `docs/portal-os/` × 12: `registry.md`, `route-manifest.json`, `scorecard.{json,md}`, `quarantine.json`, `baseline.json`, `tranches/000-template.md`, `tranches/_active.txt`, + `audit-reports/`, `drift-reports/`, `readiness/` with `.gitkeep`s

## Invariants this OS enforces

1. Every portal change is scoped to exactly one active tranche (PreToolUse hook).
2. Every "done" claim carries an `Evidence: <path>` that exists (SubagentStop hook).
3. Dead / quarantined / fake-session surfaces cannot re-enter primary nav (regression-sentinel + PR gate).
4. Scorecard is versioned JSON — drift detectable by diff.
5. No destructive operations run without human merge approval.
6. Every response ends with `Next action: ...` (Stop hook).

## Verification run before commit

- JSON parse OK on: `settings.json`, `route-manifest.json`, `quarantine.json`, `baseline.json`, `scorecard.json`.
- `bash -n` syntax OK on all 4 hook scripts.
- `js-yaml` deep parse OK on all 3 workflow files.
- Markdown frontmatter (`---`) present on all 6 commands + 5 agents.
- `npx tsc --noEmit` clean (no portal code touched; baseline preserved).

## Safety posture

- Branched from `main` at `8d3d9bc` (Tranche A head). Commit: `dfd9483`.
- Staged with explicit paths. No `git add -A` / `git add .` anywhere in the flow.
- Orthogonal pre-existing WIP on `main`'s working tree (7 M + 6 ??) is **not** included in this commit — verified by `git diff --cached --name-only`.
- No touching of: `src/`, `tests/e2e/`, `middleware.ts`, auth, backend, any runtime logic.
- No `.env*` touched. No secret touched. No existing permission loosened.
- No push-to-main. No auto-merge.

## Required manual follow-ups (not code changes)

1. **Add repo secret** `CLAUDE_CODE_OAUTH_TOKEN` via Settings → Secrets → Actions (generate in a local Claude Code session with `/install-github-app`). Without it, `.github/workflows/claude.yml` and the drift cron will fail to authenticate.
2. **Configure branch protection** on `main` (Settings → Branches): require status check `portal-pr-guard / ci` + 1 reviewer approval on PRs labelled `tranche-fix`. The PreToolUse hook can't enforce this from code.

## How to use from the phone (after secret + branch protection land)

1. Comment `@claude /portal-audit all` on any PR or issue.
2. Action produces `docs/portal-os/audit-reports/<date>-all.md` on a branch + PR.
3. Comment `@claude /portal-tranche-plan <focus>` → plan PR.
4. Comment `@claude /portal-tranche-fix NNN` on that PR → execution PR with full verification.
5. `portal-pr-guard` runs; when green + 1 approval, merge on mobile.

## Test plan

- [ ] Add repo secret `CLAUDE_CODE_OAUTH_TOKEN` (manual, phone-accessible via GitHub Settings).
- [ ] Configure branch protection on `main` (manual).
- [ ] Comment `@claude /portal-audit all` on this PR and confirm the action produces a first audit report.
- [ ] Run `/portal-scorecard` after the audit to seed the first real `scorecard.json`.
- [ ] Run `/portal-regression-guard` to confirm hook + sentinel wire together.
- [ ] Merge this PR once the smoke test is green.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
