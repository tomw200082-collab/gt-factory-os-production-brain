# GT Factory OS — AI Brain Router

> Routing decision engine. Read by every dispatch: input → lane → agent → command → permissions → evidence.
> Read-only. Produces routing blocks, ⊥ code. ⊥ relax a locked decision in `CLAUDE.md`.
> Scope: factory-os. Future modules ! `MODULE_TEMPLATE.md` filled + Tom-approved before entering the table.

## 1. Classify input (pick one, highest first)

| Type | Example |
|---|---|
| `pasted_claude_update` | checkpoint / PASS-FAIL / stop-condition text pasted by Tom |
| `approval_request` | "ready to flip flag X"; "approve PR #N" |
| `bug_failure` | "endpoint Y returns 500"; "wrong on-hand for SKU Z" |
| `feature_request` | "add forecast workspace v2" |
| `module_request` | "add CRM module" |
| `ux_audit_request` | "audit /planning/blockers"; "run UX release gate" |
| `backend_migration_request` | "add column to stock_ledger" |
| `integration_change` | "LionWheel reversal handling"; "Shopify SKU mapping" |
| `docs_governance` | "reconcile CURRENT_STATE with runtime_ready.json" |
| `release_request` | "ship portal wave 2" |
| `data_quality_issue` | "BOM head sum wrong"; "synthetic data in live DB" |

Fits >1 type → take the highest in this order.

## 2. Lanes

`backend-db` → `backend-db-executor` · `portal` → `portal-production-executor` · `integration` → `integration-boundary-executor` · `docs` → `ops-docs-curator` — ≤4 simultaneous, per-module scope.
Read-only, ⊥ count as lane: `ux-audit` (5 UX agents, parallel) · `governance` → `factory-os-governor` (always-on) · `release-gate` → `release-verifier` · `source-of-truth` → `source-of-truth-auditor` (on demand).
Legacy `executor-w1/w2/w4`, `governor`, `verifier` dispatchable until Wave 6. One lane = legacy **or** new, never both. Default new.

## 3. Decision tree — first match wins

1. **Stock-truth-impacting?** (`stock_ledger`, `balance_anchors`, projection table, BOM cluster) → `backend-db` + Tom-approval gate + `factory-os-governor` pre-check.
2. **Frozen flag / code sentinel?** (`EXECUTION_POLICY.md` §Frozen flags) → `integration` + Tom written approval HARD + dry-run + ≥24h soak + RUNTIME_READY.
3. **New module?** → `verdict: NEW_MODULE_REQUIRED`. Fill `MODULE_TEMPLATE.md`. ⊥ invoke another agent yet.
4. **User-visible portal surface?** → `ux-audit` (parallel) → handoff packet → `portal-production-executor`. Backend-bound surface ! `RUNTIME_READY(form)`.
5. **Backend contract, no portal change?** → `integration-boundary-executor` authors contract → `backend-db-executor` implements.
6. **Authority-doc reconciliation / drift audit?** → `source-of-truth-auditor` (read-only) → patch proposals → `ops-docs-curator` under governor approval. `CLAUDE.md` ! Tom.
7. **Release / merge / deploy?** → `release-verifier` → `factory-os-governor` go/no-go. Push, merge, prod deploy & prod-DB migration apply are **Claude's to do autonomously** when gates are green, per `CLAUDE.md` §Authorization — announce, ⊥ wait.
8. **Audit / dry-run / scorecard?** → relevant audit agent → evidence under `docs/phase8/dry-runs/`. ⊥ production change.
9. **Anything else?** → `factory-os-governor` classifies; emits `assumption_failure` if ⊥ unambiguously routable. ⊥ silently dispatch.

## 4. Output contract

Every routing decision emits:

```yaml
classification:   <§1 type>
target_module:    factory-os | crm | leads | sales | marketing | finance | cross-system
owner_lane:       backend-db | portal | integration | docs | ux-audit | governance | release-gate | source-of-truth
recommended_agent: <REGISTRY.md>
recommended_command: <REGISTRY.md, or "direct dispatch">
allowed_paths:    [globs]
forbidden_paths:  [globs]
write_mode:       read_only | proposal_only | write_with_approval | write
tom_decisions_required: [named]
backend_readiness_required: {required: yes|no, signal: <name>}
ux_handoff_required:        {required: yes|no, packet: <path>}
first_checkpoint: <one concrete step before any write>
stop_conditions:  [list]
expected_evidence: [artifact types]
collision_risk:   none | <lane>
verdict:          ROUTED | NEEDS_TOM | NO_VALID_LANE | NEW_MODULE_REQUIRED
```

## 5. Worked example — backend migration on stock_ledger

```yaml
classification: backend_migration_request
target_module: factory-os
owner_lane: backend-db
recommended_agent: backend-db-executor
recommended_command: direct dispatch; /release-check before merge
allowed_paths: [gt-factory-os/db/migrations/**, gt-factory-os/db/tests/**, gt-factory-os/api/src/**]
forbidden_paths: [gt-factory-os-portal/**, .claude/state/runtime_ready.json]
write_mode: write_with_approval
tom_decisions_required: [new movement_type if applicable]
backend_readiness_required: {required: no}
first_checkpoint: git status clean; FR1 fresh-read on db/migrations/; read existing schema for affected table
stop_conditions:
  - DROP COLUMN/TABLE in prod -> destructive_migration_blocked
  - UPDATE/DELETE on stock_ledger -> ledger_mutation_attempted
  - parity gate failure -> halt, root-cause
expected_evidence: migration file, pgTAP test, parity verifier output, RUNTIME_READY entry
collision_risk: integration lane if migration touches integration handler tables
verdict: ROUTED
```

5 further examples (UX audit · integration boundary · docs governance · new module · pasted update) → `docs/archive/AI_BRAIN_ROUTER.pre-lean-2026-07-31.md` §7.

## 6. Router ⊥ do

⊥ implement work · ⊥ relax a locked decision · ⊥ flip frozen flags (only routes the request) · ⊥ author agents/commands/skills · ⊥ invent lanes (! `CLAUDE.md` change, Tom only) · ⊥ override per-module isolation.

## 7. Maintenance

Update on: new module approved · new lane (Tom-approved `CLAUDE.md` change first) · agent renamed/archived · decision-tree branch found insufficient (governor proposes, Tom approves).
⊥ update for: per-cycle dispatch records (`docs/phase8/dry-runs/`) · live state (`CURRENT_STATE.md` / `ACTIVE_NOW.md`) · locked-decision changes (`CLAUDE.md` / `LOCKED_DECISIONS.md`).

---
**Owner:** `factory-os-governor` proposes · **Approver:** Tom (§2 lanes, §3 modules).
