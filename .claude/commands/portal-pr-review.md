# /portal-pr-review

Read-only review of a portal PR (or local working tree) before merge. Coordinates `portal-production-executor`,
the four UX agents, `release-verifier`, and `factory-os-governor` to produce a go/no-go verdict on portal changes.

## Purpose

Bring portal changes through a single coordinated review pass that checks: contract compliance,
UX doctrine compliance, accessibility, interaction completeness, copy register adherence, RUNTIME_READY
consumption, and FLOW-003 freeze respect. Produces a formal verdict before any merge.

## Usage

```
/portal-pr-review
/portal-pr-review <PR-number>
/portal-pr-review branch:<branch-name>
/portal-pr-review surface:<route>
/portal-pr-review local
```

**With no argument:** review the current portal working tree against `main` (or the configured base).

**With `<PR-number>`:** fetch the PR via `gh` (read-only), inspect its diff, and run the review.

**With `branch:`:** review the named branch's diff against base.

**With `surface:`:** focus the review on a specific route.

**With `local`:** explicitly review only local uncommitted changes (helpful for pre-commit gating).

## Arguments

| Arg | Required | Description |
|-----|---------|-------------|
| target | no | PR number, branch name, route, or `local`. If omitted, review current working tree. |

## Agents involved

| Agent | Role in this command |
|-------|----------------------|
| `portal-production-executor` | Drives the review; reads diff and source files; never edits |
| `ux-flow-architect` | Audits flow completeness for any user-visible surface change |
| `interaction-design-specialist` | Audits buttons, forms, confirmations, undo paths |
| `ux-content-state-designer` | Audits microcopy and Hebrew register adherence |
| `accessibility-usability-auditor` | Audits a11y on the changed surface |
| `visual-system-designer` | Audits token usage and design-system consistency |
| `release-verifier` | Pre-merge verification (clean tree, scope, validation checklist) |
| `factory-os-governor` | Final go/no-go verdict |

## Required inputs

1. The diff of the PR / branch / working tree.
2. `gt-factory-os-portal/docs/portal_ux_standard.md` — locked UX standard.
3. `PRODUCTION/docs/phase8/ux/UX_RELEASE_GATE.md` — current gate state.
4. `PRODUCTION/docs/phase8/ux/BUTTON_AND_ACTION_RULES.md`, `CONTENT_AND_MICROCOPY_GUIDE.md`,
   `STATUS_EMPTY_ERROR_STATES.md`, `ACCESSIBILITY_CHECKLIST.md` — UX doctrine.
5. `PRODUCTION/.claude/state/runtime_ready.json` — for any API-bound surface.
6. UX handoff packets in `gt-factory-os-portal/docs/ux/` or `PRODUCTION/docs/phase8/handoffs/` for
   any user-visible surface in the diff.
7. `PRODUCTION/docs/phase8/decisions/FLOW-003-planning-blockers-p0-decision-packet.md` — for any
   change touching `/planning/blockers`.

## Required outputs

A markdown review report including:

1. **Scope** — files changed, surfaces touched.
2. **UX doctrine compliance** — per-surface check against the four locked UX docs.
3. **A11y findings** — keyboard, focus, ARIA, contrast, motion.
4. **Interaction findings** — button completeness, confirmation patterns, undo paths.
5. **Microcopy findings** — register adherence, Hebrew approval status.
6. **Visual-system findings** — token usage, spacing, typography.
7. **RUNTIME_READY check** — every API-bound change references a live signal.
8. **FLOW-003 freeze check** — confirm the diff does not touch frozen files.
9. **Verdict** — one of:
   - `MERGE_OK` — clean; release-verifier independently confirms.
   - `MERGE_OK_WITH_CONSTRAINTS` — clean if listed constraints hold.
   - `BLOCK` — confirmed blocker; named.
   - `HOLD_FOR_TOM` — Tom approval required (e.g. Hebrew register).

## Allowed scope (read-only)

- Read any file in `gt-factory-os-portal/` or `window2-portal-sandbox/`.
- Read any file in `PRODUCTION/docs/`.
- Read PR metadata via `gh pr view`, `gh pr diff` (no comment posting).
- Read `git diff`, `git log`, `git status` on portal repos.

## Forbidden scope

- **No file writes.** This command is read-only.
- **No edits to portal source.**
- **No edits to UX doctrine docs.**
- **No edits to `portal_ux_standard.md`.**
- **No PR comments posted via `gh pr comment` (the human posts the review summary).**
- **No merges, deploys, or pushes.**
- **No FLOW-003 resolution** — even if the verdict suggests a fix, the fix is gated by the
  FLOW-003 decision packet.

## Side-effect policy

**Read-only.** No mutations to source, docs, PR state, or external systems. Optionally writes
the review report to `PRODUCTION/docs/phase8/portal-reviews/<date>-<target>.md` if requested
explicitly with `save:true`. Default is to print only.

## Validation requirements

The command must verify:

1. The diff has been read in full (no summary-only review).
2. Every changed user-visible surface has a UX handoff packet (or a documented exception).
3. The FLOW-003 frozen file list has been checked against the diff.
4. RUNTIME_READY signals exist for every API-bound surface.
5. No `.env*`, secrets, or credentials are in the diff.
6. No file outside the portal repo is in the diff.

## Tom approval triggers

The review verdict alone does not authorize a merge. Tom must explicitly authorize:

- Any merge that crosses a Hebrew register change.
- Any merge that touches `middleware.ts` or `(auth)/**`.
- Any merge that touches `next.config.*` or `tsconfig.json`.
- Any merge that adds a new operator-facing form.
- Any merge that touches FLOW-003 frozen files.

## Stop conditions

| Condition | Action |
|-----------|--------|
| Diff includes FLOW-003 frozen files | `BLOCK` immediately; cite decision packet |
| Diff includes Hebrew copy without a register entry | `HOLD_FOR_TOM` |
| Diff includes a backend file | `BLOCK`; route to `backend-db-executor` review |
| Diff includes `.env*` or secrets | `BLOCK`; cite secrets policy |
| RUNTIME_READY missing for API-bound change | `BLOCK`; route to `backend-db-executor` |
| UX handoff packet missing | `BLOCK`; route to UX agent |
| `UX_RELEASE_GATE.md` shows HOLD on the surface | `BLOCK`; cite gate doc |

## GitHub / mobile usability

- The command works without GitHub if a PR number is not provided (use `local` or `branch:`).
- If a PR number is provided, the command uses `gh pr view` and `gh pr diff`. Requires `gh`
  authenticated locally.
- The review report is plain markdown so it can be pasted into a PR comment by the human.

## Local-only limitations

- This command does not run the dev server or Playwright. Browser smoke tests are
  `portal-production-executor`'s responsibility before commit; this command verifies that
  smoke-test evidence exists in the PR description, not that it runs.
- This command does not run `pnpm typecheck` or `pnpm build`; those are pre-commit obligations
  for `portal-production-executor`.

## Example

```
/portal-pr-review surface:/(po)/purchase-orders
/portal-pr-review 47
/portal-pr-review local
```

## Not usable for

- Merging PRs.
- Posting PR comments.
- Resolving FLOW-003.
- Editing portal source.
- Running production deploys.
