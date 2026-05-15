# GT Factory OS — Command Registry

> **Authority layer:** compact index of every slash-command in `PRODUCTION/.claude/commands/`.
>
> **Source of truth on command behavior:** the command files themselves. This file is a navigational index — it does not duplicate command body content.
>
> **Update cadence:** every time a command is added, retired, or has its primary verdict vocabulary change. Maintained by `ops-docs-curator` after `factory-os-governor` approval.
>
> **Total active commands (2026-05-08, Phase 8 Run F Wave 2):** 15
> - 7 UX (Run A): button-logic-review, design-system-check, empty-error-state-audit, operator-task-simulation, screen-scorecard, ux-flow-audit, ux-release-gate
> - 3 governance & audit (Run A): production-go-no-go, release-check, source-truth-audit
> - 5 execution (Run B): docs-hygiene-check, gate-close, incident-triage, integration-dry-run, portal-pr-review

---

## UX commands (7)

| Command | Path | Primary agent | Supporting agents | Type | Verdicts | Writes? | Intended use |
|---|---|---|---|---|---|---|---|
| `/button-logic-review` | `.claude/commands/button-logic-review.md` | `interaction-design-specialist` | (none) | UX audit | DECISION_GRADE, FLOW_COMPLETION (P-finding codes) | optional dry-run | Audit button/action logic completeness on a single route |
| `/design-system-check` | `.claude/commands/design-system-check.md` | `visual-system-designer` | (none) | UX audit | VISUAL-NNN finding codes | optional dry-run | Audit visual hierarchy, token drift, component consistency |
| `/empty-error-state-audit` | `.claude/commands/empty-error-state-audit.md` | `interaction-design-specialist` | `accessibility-usability-auditor` | UX audit | INTER-NNN, A11Y-NNN | optional dry-run | Audit loading/empty/error/post-action states |
| `/operator-task-simulation` | `.claude/commands/operator-task-simulation.md` | `ux-flow-architect` | `interaction-design-specialist` | UX audit | FLOW-NNN, ARCH_REQUIRED, BLOCKED | optional dry-run | Trace operator task end-to-end; identify process gaps |
| `/screen-scorecard` | `.claude/commands/screen-scorecard.md` | UX agents (all 5) | (aggregator) | UX audit | P0/P1/P2/P3 counts; SHIP_READY / NEEDS_WORK / BLOCKED | optional save | Aggregate UX findings into per-route scorecard |
| `/ux-flow-audit` | `.claude/commands/ux-flow-audit.md` | `ux-flow-architect` | `ux-content-state-designer`, `accessibility-usability-auditor`, `interaction-design-specialist` | UX audit | DECISION_GRADE, FLOW_COMPLETION, POLISH_ACCELERATION, ARCH_REQUIRED | dry-run + handoff packet | Audit end-to-end operational flow on portal route |
| `/ux-release-gate` | `.claude/commands/ux-release-gate.md` | UX agents (all 5) | `factory-os-governor` (verdict) | UX gate | SHIP, CONDITIONAL_SHIP, HOLD | dry-run; formal record after Tom approval | Full UX gate check before portal release |

## Governance & audit commands (3)

| Command | Path | Primary agent | Supporting agents | Type | Verdicts | Writes? | Intended use |
|---|---|---|---|---|---|---|---|
| `/production-go-no-go` | `.claude/commands/production-go-no-go.md` | `factory-os-governor` | `release-verifier`, `source-of-truth-auditor` | gate | PROCEED, PROCEED_WITH_CONSTRAINTS, HOLD, SWITCH_LANE | optional dry-run | Determine if phase/release/task may proceed |
| `/release-check` | `.claude/commands/release-check.md` | `release-verifier` | `factory-os-governor` | gate | SAFE_FOR_HUMAN_REVIEW, CONDITIONALLY_SAFE, NOT_SAFE, BLOCKED | optional report | Verify PR/branch readiness before human merge |
| `/source-truth-audit` | `.claude/commands/source-truth-audit.md` | `source-of-truth-auditor` | `factory-os-governor` | audit | STALE, CONFLICTING, ORPHANED, SHADOW (D1–D10 scan IDs) | optional dry-run | Find conflicting / stale / orphaned facts across authority docs |

## Execution commands (5)

| Command | Path | Primary agent | Supporting agents | Type | Verdicts | Writes? | Intended use |
|---|---|---|---|---|---|---|---|
| `/docs-hygiene-check` | `.claude/commands/docs-hygiene-check.md` | `ops-docs-curator` | (none) | audit | CLEAN, MINOR_DRIFT, SIGNIFICANT_DRIFT, CRITICAL_DRIFT | hygiene report under `docs/phase8/hygiene/` | Hygiene scan of operational docs; identify stale archives, drift |
| `/gate-close` | `.claude/commands/gate-close.md` | `factory-os-governor` | `release-verifier`, `source-of-truth-auditor`, all execution agents | closure | READY_TO_CLOSE, READY_WITH_CONSTRAINTS, NOT_READY | closure packet under `docs/phase8/handoffs/` | Assemble closure packet for Phase / Wave / Gate with exit evidence |
| `/incident-triage` | `.claude/commands/incident-triage.md` | `integration-boundary-executor` | `factory-os-governor`, `release-verifier`, `source-of-truth-auditor`, `ops-docs-curator` | triage | P0/P1/P2/P3, ROUTED, NEEDS_TOM, NO_INCIDENT | triage report under `docs/phase8/incidents/` | Read-only diagnosis of integration / sync / exception issues |
| `/integration-dry-run` | `.claude/commands/integration-dry-run.md` | `integration-boundary-executor` | `factory-os-governor`, `release-verifier` | dry-run | READY_FOR_FLIP_REQUEST, READY_FOR_EXTERNAL_WRITE_REQUEST, NOT_READY | dry-run record under `docs/phase8/dry-runs/` + freshness log append | Dry-run integration handler with no external writes |
| `/portal-pr-review` | `.claude/commands/portal-pr-review.md` | `portal-production-executor` | All UX agents, `release-verifier`, `factory-os-governor` | review | MERGE_OK, MERGE_OK_WITH_CONSTRAINTS, BLOCK, HOLD_FOR_TOM | optional review report | Review portal PR/branch before merge |

---

## Verdict-vocabulary cross-reference

For canonical definitions of every verdict token used in any command, see `VERDICT_GLOSSARY.md`. Run F decision E: existing verdicts are NOT renamed; the glossary documents collisions (notably `HOLD`) without resolving them in commands.

---

## Notes on command stacking

Several commands compose cleanly when run in sequence. Run F does not change command behavior; this is informational guidance for dispatchers:

- `/release-check` → `/production-go-no-go` (release-check is a pre-gate; production-go-no-go is the policy decision).
- `/portal-pr-review` (per-PR) → `/ux-release-gate` (per-release).
- `/gate-close` produces evidence consumed by `/production-go-no-go`.
- `/screen-scorecard` aggregates findings produced by `/ux-flow-audit`, `/button-logic-review`, `/design-system-check`, `/empty-error-state-audit`.

Verdict collisions (documented in `VERDICT_GLOSSARY.md` but not renamed in Run F):
- `HOLD` in `/production-go-no-go` (dependency-blocked) vs `HOLD` in `/ux-release-gate` (P0 finding present). Different semantics; same token. Dispatchers must read the surrounding context.
- `BLOCK` vs `HOLD_FOR_TOM` in `/portal-pr-review` — both block merge; differ on escalation path.

---

## Command count integrity check

`ls PRODUCTION/.claude/commands/*.md | wc -l` = 15 (verified 2026-05-08, Phase 8 Run F Wave 2).
This file references all 15. If the count drifts, `/source-truth-audit` flags the inconsistency.

---

## Forbidden in Run F

- No new command created.
- No verdict renamed.
- No command policy duplicated; commands cite authority docs by section.

---

**Owner:** `ops-docs-curator` (writes; under `factory-os-governor` approval).
**Last updated:** 2026-05-08 (Phase 8 Run F Wave 2 — initial creation).
