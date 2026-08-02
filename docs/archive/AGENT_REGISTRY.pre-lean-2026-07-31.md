# GT Factory OS — Agent Registry

> **Authority layer:** compact index of every agent in `PRODUCTION/.claude/agents/`.
>
> **Source of truth on agent status:** the agent files themselves. This file is a navigational index — it does not duplicate agent body content.
>
> **Update cadence:** every time an agent is added, archived, or has its status change. Maintained by `ops-docs-curator` after `factory-os-governor` approval.
>
> **Total active agents (2026-05-08, Phase 8 Run F Wave 2):** 17
> - 3 Run A core production brain
> - 5 Run A UX agents
> - 4 Run B execution agents
> - 5 legacy agents (active until Wave 6 deprecation per `docs/phase8/deprecation/ACTIVE_SURFACE_REDUCTION_PLAN.md`)

---

## Run A — Core production brain (3)

| Agent | Path | Class | Lane | Write mode | Status | Purpose |
|---|---|---|---|---|---|---|
| `factory-os-governor` | `.claude/agents/factory-os-governor.md` | core | governance | read-only | active | Go/no-go verdicts; source-of-truth hierarchy arbitration; lane control; frozen-flag guard. Successor to `governor.md`. |
| `release-verifier` | `.claude/agents/release-verifier.md` | core | release-gate | read-only | active | Pre-merge / pre-deploy verification. Produces SAFE_FOR_HUMAN_REVIEW / CONDITIONALLY_SAFE / NOT_SAFE / BLOCKED verdicts. |
| `source-of-truth-auditor` | `.claude/agents/source-of-truth-auditor.md` | core | source-of-truth | read-only | active | Cross-doc drift classification (STALE/CONFLICTING/ORPHANED/SHADOW). Proposes patches; does not apply. |

## Run A — UX agents (5)

| Agent | Path | Class | Lane | Write mode | Status | Purpose |
|---|---|---|---|---|---|---|
| `ux-flow-architect` | `.claude/agents/ux-flow-architect.md` | UX | ux-audit | read-only | active | End-to-end operational flow auditing. Decision-grade vs flow-completion vs polish classification. |
| `interaction-design-specialist` | `.claude/agents/interaction-design-specialist.md` | UX | ux-audit | read-only | active | Buttons, forms, undo/cancel/reversal, disabled states, daily-use density. |
| `visual-system-designer` | `.claude/agents/visual-system-designer.md` | UX | ux-audit | read-only | active | Tokens, layout, typography, rhythm, component consistency. |
| `ux-content-state-designer` | `.claude/agents/ux-content-state-designer.md` | UX | ux-audit | proposal-only on `portal_ux_standard.md` | active | Microcopy, status terms, error messages, Hebrew/English clarity. Sole writer of `portal_ux_standard.md`. |
| `accessibility-usability-auditor` | `.claude/agents/accessibility-usability-auditor.md` | UX | ux-audit | read-only | active | WCAG basics, focus order, keyboard nav, ARIA, screen-reader announcements. |

## Run B — Execution agents (4)

| Agent | Path | Class | Lane | Write mode | Status | Purpose |
|---|---|---|---|---|---|---|
| `backend-db-executor` | `.claude/agents/backend-db-executor.md` | execution | backend-db | write_with_approval | active | Backend API + DB + migrations + jobs. Successor to `executor-w1`. |
| `portal-production-executor` | `.claude/agents/portal-production-executor.md` | execution | portal | write_with_approval | active | Next.js portal authoring. Successor to `executor-w2`. |
| `integration-boundary-executor` | `.claude/agents/integration-boundary-executor.md` | execution | integration | write_with_approval | active | LionWheel / Shopify / Green Invoice / Edge Functions; sole frozen-flag gatekeeper. Successor to `executor-w4`. |
| `ops-docs-curator` | `.claude/agents/ops-docs-curator.md` | execution | docs | write_with_approval | active | Docs hygiene, archive index, deprecation planning. New role; no executor-era predecessor. |

## Legacy agents (5; active until Wave 6 deprecation)

Wave 6 archival is governed by `docs/phase8/deprecation/ACTIVE_SURFACE_REDUCTION_PLAN.md`. Until then, both legacy and new agents are dispatchable; default is the new production agent unless Tom specifies otherwise.

| Agent | Path | Class | Lane | Write mode | Status | Replacement |
|---|---|---|---|---|---|---|
| `executor-w1` | `.claude/agents/executor-w1.md` | legacy | backend-db | write_with_approval | legacy-active | `backend-db-executor` |
| `executor-w2` | `.claude/agents/executor-w2.md` | legacy | portal | write_with_approval | legacy-active | `portal-production-executor` |
| `executor-w4` | `.claude/agents/executor-w4.md` | legacy | integration | write_with_approval | legacy-active | `integration-boundary-executor` |
| `governor` | `.claude/agents/governor.md` | legacy | governance | read-only | legacy-active | `factory-os-governor` |
| `verifier` | `.claude/agents/verifier.md` | legacy | release-gate | read-only | legacy-active (kept indefinitely per CLAUDE.md §Production agent architecture) | n/a — `verifier.md` is preserved as the post-executor PASS/FAIL verifier |

---

## Allowed-paths summary (compact)

For full allowed/forbidden paths, see each agent's body. This is the one-line summary:

| Agent | Allowed write paths (summary) |
|---|---|
| `backend-db-executor` | `gt-factory-os/api/**`, `gt-factory-os/db/**`, `gt-factory-os/scripts/**` (excl. archive); appends to `PRODUCTION/.claude/state/runtime_ready.json` |
| `portal-production-executor` | `gt-factory-os-portal/src/**`, `window2-portal-sandbox/src/**` |
| `integration-boundary-executor` | `gt-factory-os/docs/integrations/**`, `gt-factory-os/docs/contracts/**`, `gt-factory-os/api/src/integrations/**` (handler skeleton only; impl is backend-db-executor) |
| `ops-docs-curator` | `PRODUCTION/docs/**` (excl. authority docs), `PRODUCTION/archive/**` (proposes moves) |
| `factory-os-governor` | read-only across all repos; may save evidence under `PRODUCTION/docs/phase8/` |
| `release-verifier` | read-only |
| `source-of-truth-auditor` | read-only |
| UX agents | read-only (except `ux-content-state-designer` proposes `portal_ux_standard.md` updates) |
| Legacy executors | same as their replacements (see Phase 8 production agent mapping in `EXECUTION_POLICY.md`) |

---

## Sister relationships

- `backend-db-executor` ↔ `executor-w1` — additive replacement; one active per dispatch.
- `portal-production-executor` ↔ `executor-w2` — additive replacement.
- `integration-boundary-executor` ↔ `executor-w4` — additive replacement.
- `factory-os-governor` ↔ `governor` — additive replacement.
- `release-verifier` ↔ `verifier.md` — `verifier.md` is kept indefinitely; `release-verifier` is pre-merge / pre-deploy gating, not a replacement.

---

## Agent count integrity check

`ls PRODUCTION/.claude/agents/*.md | wc -l` = 17 (verified 2026-05-08, Phase 8 Run F Wave 2).
This file references all 17. If the count drifts, `/source-truth-audit` flags the inconsistency.

---

**Owner:** `ops-docs-curator` (writes; under `factory-os-governor` approval).
**Last updated:** 2026-05-08 (Phase 8 Run F Wave 2 — initial creation).
