# GT Factory OS — Registry

> Agents · commands · skills. Replaces `AGENT_REGISTRY.md` + `COMMAND_REGISTRY.md` (both archived 2026-07-31).
> **Names & descriptions are auto-injected by the harness every session — ⊥ duplicated here.**
> This file carries only what the harness ⊥ give you: lane, write mode, allowed paths.
> Source of truth on any agent = its own file in `.claude/agents/`.

## Agents — lane & write mode (17)

| Agent | Lane | Write | Allowed write paths |
|---|---|---|---|
| `backend-db-executor` | backend-db | approval | `gt-factory-os/api/**`, `db/**`, `scripts/**` (excl. archive); appends `.claude/state/runtime_ready.json` |
| `portal-production-executor` | portal | approval | `gt-factory-os-portal/src/**` |
| `integration-boundary-executor` | integration | approval | `gt-factory-os/docs/integrations/**`, `docs/contracts/**`, `api/src/integrations/**` (skeleton only) |
| `ops-docs-curator` | docs | approval | `docs/**` excl. authority docs; `archive/**` (proposes moves, ⊥ deletes) |
| `factory-os-governor` | governance | read-only | may save evidence under `docs/phase8/` |
| `release-verifier` | release-gate | read-only | — |
| `source-of-truth-auditor` | source-of-truth | read-only | — |
| `ux-flow-architect` | ux-audit | read-only | — |
| `interaction-design-specialist` | ux-audit | read-only | — |
| `visual-system-designer` | ux-audit | read-only | — |
| `ux-content-state-designer` | ux-audit | proposal | sole writer of `portal_ux_standard.md` |
| `accessibility-usability-auditor` | ux-audit | read-only | — |
| `executor-w1` *(legacy)* | backend-db | approval | = `backend-db-executor` |
| `executor-w2` *(legacy)* | portal | approval | = `portal-production-executor` |
| `executor-w4` *(legacy)* | integration | approval | = `integration-boundary-executor` |
| `governor` *(legacy)* | governance | read-only | — |
| `verifier` *(legacy, kept indefinitely)* | release-gate | read-only | post-executor PASS/FAIL verification |

Legacy ↔ new are additive pairs — one active per dispatch, default new. Wave 6 archival per `docs/phase8/deprecation/ACTIVE_SURFACE_REDUCTION_PLAN.md`, each step ! Tom approval.
`release-verifier` ≠ replacement for `verifier` — it is pre-merge/pre-deploy gating; `verifier` stays.

## Commands (15)

**Governance / release:** `/gate-close` · `/production-go-no-go` · `/release-check` · `/source-truth-audit` · `/incident-triage` · `/docs-hygiene-check`
**Portal / integration:** `/portal-pr-review` · `/integration-dry-run`
**UX (7):** `/ux-flow-audit` · `/ux-release-gate` · `/button-logic-review` · `/empty-error-state-audit` · `/design-system-check` · `/screen-scorecard` · `/operator-task-simulation`

**Stacking:** `/gate-close` → evidence consumed by `/production-go-no-go` · `/release-check` (pre-gate) → `/production-go-no-go` (policy decision) · `/portal-pr-review` (per-PR) → `/ux-release-gate` (per-release) · `/screen-scorecard` aggregates `/ux-flow-audit` + `/button-logic-review` + `/design-system-check` + `/empty-error-state-audit`.
**Verdict-token collision:** `HOLD` means dependency-blocked in `/production-go-no-go` but P0-finding-present in `/ux-release-gate` — same token, different cause. Read context, ⊥ assume.

## Skills (7)

`daily-ops-guardian` · `daily-delivery-dispatch` · `route-print-pack` · `procurement-planning` · `plan-production-14d` · `goods-receipt-from-invoice` · `close-session`

Skill creation threshold: `docs/phase8/decisions/STEP4-SKILLS-DECISION.md`. ⊥ create skills below it.

## Drift check

`ls .claude/agents/*.md | wc -l` = 17 · `find .claude/commands -name '*.md' | wc -l` = 15 · `ls -d .claude/skills/*/ | wc -l` = 7.
Counts diverge → `/source-truth-audit` flags it.

---
**Owner:** `ops-docs-curator` under `factory-os-governor` approval.
