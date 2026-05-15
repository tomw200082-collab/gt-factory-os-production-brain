# GT Factory OS — AI Brain Router

> **Authority layer:** routing decision engine. Read by every dispatch to classify input → lane → agent → command → permissions.
>
> **This file is read-only governance.** It does not implement work. It produces routing decisions.
>
> **Scope:** factory-os (current). Future modules (CRM, lead intake, sales, marketing, finance) require `MODULE_TEMPLATE.md` filled and Tom-approved before they enter the routing table.
>
> **Sibling docs:**
> - `CLAUDE.md` — boot kernel and locked decisions (this router cannot relax any locked decision).
> - `EXECUTION_POLICY.md` — operating law (lanes, modes, signals, retry, approvals, frozen flags).
> - `CURRENT_STATE.md` — live runtime state.
> - `ACTIVE_NOW.md` — ephemeral active-lane context.
> - `WORKSPACE_MAP.md` — repo geography.
> - `AGENT_REGISTRY.md` — current agent inventory (referenced; not duplicated).
> - `COMMAND_REGISTRY.md` — current command inventory (referenced; not duplicated).
> - `VERDICT_GLOSSARY.md` — verdict semantics.
> - `AGENT_TEMPLATE.md` — required structure for new agents.
> - `MODULE_TEMPLATE.md` — required declaration for new modules.

---

## 1. Purpose

The router is the single decision engine for any incoming request. It maps an arbitrary input — a Tom message, a Claude checkpoint, a bug report, a pasted update, a feature request, an audit trigger — to a deterministic routing block (lane, agent, command, permissions, evidence, stop conditions).

Without the router, routing decisions depend on memory of which lane owns what. The router replaces that with a checked decision tree that scales when modules are added.

---

## 2. Input classification

Every dispatch begins by classifying the input as exactly one type:

| Input type | Examples |
|---|---|
| `pasted_claude_update` | A Claude Code checkpoint, PASS/FAIL report, or stop-condition message pasted by Tom |
| `approval_request` | "Tom, ready to flip frozen flag X"; "Approve PR #N" |
| `bug_failure` | "Production endpoint Y returns 500"; "Inventory shows wrong on-hand for SKU Z" |
| `feature_request` | "Add forecast workspace v2"; "Add critical-today block on dashboard" |
| `module_request` | "Add CRM module"; "Add lead-intake module" |
| `ux_audit_request` | "Audit /planning/blockers for accessibility"; "Run UX release gate" |
| `backend_migration_request` | "Add column X to stock_ledger"; "New migration for forecast freeze table" |
| `integration_change` | "LionWheel chain needs reversal handling"; "Shopify SKU mapping update" |
| `docs_governance` | "Reconcile CURRENT_STATE.md with runtime_ready.json"; "Audit drift" |
| `release_request` | "Ship portal Wave 2"; "Cut release branch X" |
| `data_quality_issue` | "Recipe BOM head has wrong sum"; "Synthetic data still in live DB" |

If the input fits more than one type, the router picks the **highest-priority** type from the order above (top-down).

---

## 3. Lane model

The active lane set for factory-os today:

| Lane | Owner agent | Active simultaneously | Module-scope or system-wide |
|---|---|---|---|
| `backend-db` | `backend-db-executor` (or legacy `executor-w1` until Wave 6) | yes | per-module |
| `portal` | `portal-production-executor` (or legacy `executor-w2` until Wave 6) | yes | per-module |
| `integration` | `integration-boundary-executor` (or legacy `executor-w4` until Wave 6) | yes | per-module |
| `docs` | `ops-docs-curator` | yes | system-wide |
| `ux-audit` | 5 UX agents (read-only, parallel) | yes | system-wide |
| `governance` | `factory-os-governor` (or legacy `governor` until Wave 6) | always-on, read-only | system-wide |
| `release-gate` | `release-verifier` (or legacy `verifier`) | on-demand, read-only | system-wide |
| `source-of-truth` | `source-of-truth-auditor` | on-demand, read-only | system-wide |

Maximum **4 simultaneous executor lanes** (backend + portal + integration + docs). UX, governance, release-gate, source-of-truth are read-only and do not count as a lane.

A lane may be carried by either the legacy executor or the new production agent — never both at once. Default is the new production agent unless Tom specifies otherwise.

### 3.1 Per-module lane isolation (forward-looking)

When a future module is approved (CRM, leads, sales, marketing, finance), each module gets its own scoped backend-db / portal / integration agents. A CRM-backend-builder cannot touch factory-os schema, and vice versa. This isolation is enforced through allowed-paths declarations in the module's filled `MODULE_TEMPLATE.md`.

---

## 4. Future module rule (hard)

A new module cannot be built until:

1. `PRODUCTION/MODULE_TEMPLATE.md` is filled out for that module (all required sections completed).
2. Tom approves the filled declaration in writing.
3. The router updates this document with the new module's lane row(s).

**Until those three conditions hold, every input that requests work on the new module returns `verdict: NEW_MODULE_REQUIRED`** and points the dispatcher at `MODULE_TEMPLATE.md`.

This rule is non-negotiable. Adding CRM by ad-hoc dispatch — without a filled module declaration — will create overlapping ownership and stock-truth contamination risk. The router prevents this by design.

---

## 5. Routing decision tree (compact)

For each input, walk the tree in order. The first matching rule produces the routing block.

1. **Stock-truth-impacting operation?** (any change to `stock_ledger`, `balance_anchors`, projection table, or BOM cluster)
   → lane=`backend-db` + agent=`backend-db-executor` + Tom-approval gate REQUIRED + factory-os-governor pre-check.

2. **Frozen-flag change?** (`LIONWHEEL_FG_OUT_BRIDGE_ENABLED`, `SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED`, or any flag listed in `EXECUTION_POLICY.md` §Frozen flags log)
   → lane=`integration` + agent=`integration-boundary-executor` + Tom written approval HARD-REQUIRED + dry-run + ≥24h soak + RUNTIME_READY signal.

3. **New module (CRM, leads, sales, marketing, finance)?**
   → verdict=`NEW_MODULE_REQUIRED`. Dispatcher fills `MODULE_TEMPLATE.md`; no other agent is invoked yet.

4. **User-visible portal surface change?**
   → ux-audit lane (parallel UX agents) → handoff packet → `portal-production-executor`. Backend readiness (`RUNTIME_READY(form)`) required if surface depends on a new contract.

5. **Backend contract change without portal change?**
   → lane=`integration` + `integration-boundary-executor` authors contract → `backend-db-executor` implements handler.

6. **Authority-doc reconciliation or drift audit?**
   → lane=`source-of-truth` (read-only `source-of-truth-auditor`) → patch proposals → `ops-docs-curator` applies under factory-os-governor approval. CLAUDE.md changes require Tom (sole writer).

7. **Release / merge / deploy decision?**
   → lane=`release-gate` (`release-verifier`) → `factory-os-governor` final go/no-go. Push / merge / deploy follow `EXECUTION_POLICY.md` §Git / deploy execution authority (2026-05-15): mission-scoped — Claude-authorized inside a Tom-approved mission/corridor with all safety gates passing, explicit Tom instruction otherwise, hard stop gates always Tom-only.

8. **Audit / dry-run / scorecard?**
   → relevant UX or audit agent → evidence under `docs/phase8/dry-runs/` → no production change.

9. **Anything else?**
   → factory-os-governor classifies and emits `assumption_failure` if input cannot be unambiguously routed. Do not silently dispatch.

---

## 6. Router output contract

Every routing decision must produce this structured block:

```yaml
classification: <input_type from §2>
target_module: factory-os | crm | leads | sales | marketing | finance | cross-system
owner_lane: backend-db | portal | integration | docs | ux-audit | governance | release-gate | source-of-truth
recommended_agent: <agent name from AGENT_REGISTRY.md>
recommended_command: <command from COMMAND_REGISTRY.md, or "direct dispatch (no command)">
allowed_paths: [list of repo + path globs]
forbidden_paths: [list]
write_mode: read_only | proposal_only | write_with_approval | write
tom_decisions_required: [named decisions]
backend_readiness_required:
  required: yes | no
  signal: <signal name if yes>
ux_handoff_required:
  required: yes | no
  packet: <path if yes>
first_checkpoint: <one concrete first step the dispatched agent must do before any write>
stop_conditions: [list]
expected_evidence: [artifact types]
collision_risk: none | <named lane that may collide>
verdict: ROUTED | NEEDS_TOM | NO_VALID_LANE | NEW_MODULE_REQUIRED
```

The router is read-only. It does not write code. It produces this block.

---

## 7. Worked examples

### 7.1 Portal UX fix on /planning/blockers

```yaml
classification: ux_audit_request
target_module: factory-os
owner_lane: ux-audit
recommended_agent: ux-flow-architect (lead) + interaction-design-specialist (parallel)
recommended_command: /ux-flow-audit /planning/blockers
allowed_paths:
  - PRODUCTION/docs/phase8/dry-runs/**
  - PRODUCTION/docs/phase8/ux/**handoff**.md
forbidden_paths:
  - gt-factory-os-portal/**
  - window2-portal-sandbox/**
  - api/**
  - db/**
write_mode: proposal_only
tom_decisions_required: []
backend_readiness_required:
  required: no
ux_handoff_required:
  required: yes
  packet: PRODUCTION/docs/phase8/ux/<surface>-handoff-<date>.md
first_checkpoint: read PRODUCTION/docs/phase8/ux/UX_OPERATING_PRINCIPLES.md and the existing /planning/blockers source files before producing findings
stop_conditions:
  - any P0 finding -> escalate to factory-os-governor
  - missing RUNTIME_READY for a backend-bound surface -> blocked
expected_evidence: dry-run record under docs/phase8/dry-runs/, findings table, handoff packet
collision_risk: none (UX lane is read-only, parallel-safe)
verdict: ROUTED
```

### 7.2 Backend migration: add column to stock_ledger

```yaml
classification: backend_migration_request
target_module: factory-os
owner_lane: backend-db
recommended_agent: backend-db-executor
recommended_command: direct dispatch (no command); /release-check before merge
allowed_paths:
  - gt-factory-os/db/migrations/**
  - gt-factory-os/db/tests/**
  - gt-factory-os/api/src/**
forbidden_paths:
  - gt-factory-os-portal/**
  - PRODUCTION/.claude/state/runtime_ready.json (only emitted, never overwritten)
write_mode: write_with_approval
tom_decisions_required: [Production DB migration approval, new movement_type approval if applicable]
backend_readiness_required:
  required: no (this work emits readiness)
ux_handoff_required:
  required: no
first_checkpoint: confirm git status clean, run FR1 fresh-read on db/migrations/ to capture next free slot, read existing schema for the affected table
stop_conditions:
  - DROP COLUMN or DROP TABLE in production -> destructive_migration_blocked
  - UPDATE/DELETE on stock_ledger -> ledger_mutation_attempted
  - parity gate failure -> halt; root-cause investigation
expected_evidence: migration file, pgTAP test, parity verifier output, RUNTIME_READY signal entry
collision_risk: integration lane if same migration touches integration handler tables
verdict: ROUTED
```

### 7.3 Integration boundary change: LionWheel reversal handling

```yaml
classification: integration_change
target_module: factory-os
owner_lane: integration
recommended_agent: integration-boundary-executor (contract author) + backend-db-executor (handler implementer, downstream)
recommended_command: /integration-dry-run lionwheel
allowed_paths:
  - gt-factory-os/docs/integrations/**
  - gt-factory-os/docs/contracts/**
  - gt-factory-os/api/src/integrations/lionwheel/** (only after contract is authored)
forbidden_paths:
  - .env*, credentials/**, secrets/**
  - LIONWHEEL_FG_OUT_BRIDGE_ENABLED flip without Tom written approval
write_mode: write_with_approval
tom_decisions_required: [contract approval, frozen-flag flip if reversal handling changes the bridge state]
backend_readiness_required:
  required: yes
  signal: RUNTIME_READY(LionWheelReversal) if a new signal is needed
ux_handoff_required:
  required: no
first_checkpoint: read CLAUDE.md "LionWheel pickup -> ledger decrement" locked decision, confirm bridge flag is false, run dry-run before any external call
stop_conditions:
  - frozen flag found unexpectedly true -> frozen_flag_unexpected_state
  - direct ledger write attempted -> direct_ledger_write_attempted
  - non-terminal LionWheel status triggers -> halt
expected_evidence: dry-run record, contract diff, soak window evidence (>=24h)
collision_risk: backend-db lane (handler implementation)
verdict: ROUTED
```

### 7.4 Docs / governance: reconcile CURRENT_STATE drift

```yaml
classification: docs_governance
target_module: factory-os
owner_lane: source-of-truth
recommended_agent: source-of-truth-auditor (find) -> ops-docs-curator (apply patches under governor approval)
recommended_command: /source-truth-audit
allowed_paths:
  - PRODUCTION/CURRENT_STATE.md (only via ops-docs-curator after factory-os-governor approval)
  - PRODUCTION/ACTIVE_NOW.md
  - PRODUCTION/EXECUTION_POLICY.md
  - PRODUCTION/docs/archive/**
forbidden_paths:
  - PRODUCTION/CLAUDE.md (Tom is sole writer)
  - .claude/state/runtime_ready.json (only emitters write)
write_mode: proposal_only -> write_with_approval (after factory-os-governor PROCEED)
tom_decisions_required: [CLAUDE.md changes always require Tom]
backend_readiness_required:
  required: no
ux_handoff_required:
  required: no
first_checkpoint: full /source-truth-audit run, classify every conflict (STALE/CONFLICTING/ORPHANED/SHADOW), produce patch proposals
stop_conditions:
  - CLAUDE.md violation suggested -> halt + escalate to Tom
  - unresolvable by authority hierarchy -> escalate
expected_evidence: audit report under docs/phase8/dry-runs/, patch proposals, factory-os-governor verdict
collision_risk: none (read-only audit; patches are gated)
verdict: ROUTED
```

### 7.5 New CRM module request

```yaml
classification: module_request
target_module: crm (proposed)
owner_lane: <undefined until module declaration approved>
recommended_agent: <none — Tom + dispatcher fills MODULE_TEMPLATE.md first>
recommended_command: <none>
allowed_paths: []
forbidden_paths: ["everything until module declaration is approved"]
write_mode: read_only
tom_decisions_required: [module declaration approval]
backend_readiness_required:
  required: no
ux_handoff_required:
  required: no
first_checkpoint: open PRODUCTION/MODULE_TEMPLATE.md, fill every required section, submit to Tom
stop_conditions:
  - any code work attempted before declaration approved -> halt
expected_evidence: filled MODULE_TEMPLATE.md, Tom written approval
collision_risk: factory-os lane scope contamination if module is built without isolation
verdict: NEW_MODULE_REQUIRED
```

### 7.6 Pasted Claude status report

```yaml
classification: pasted_claude_update
target_module: <inferred from content>
owner_lane: governance (initial classification)
recommended_agent: factory-os-governor (read the pasted text + classify)
recommended_command: /production-go-no-go (if approval-shaped) or direct triage
allowed_paths: read-only across PRODUCTION/
forbidden_paths: any write before classification completes
write_mode: read_only
tom_decisions_required: [depends on classification]
backend_readiness_required:
  required: depends on classification
ux_handoff_required:
  required: depends on classification
first_checkpoint: read the pasted text fully, classify per §2 above, then re-route
stop_conditions:
  - input cannot be unambiguously classified -> emit assumption_failure
expected_evidence: classification block, downstream routing block
collision_risk: depends
verdict: ROUTED (to a downstream classification)
```

---

## 8. What the router does NOT do

- It does not implement work. It produces routing decisions.
- It does not relax any locked decision in `CLAUDE.md`.
- It does not flip frozen flags. It can only route a flip request to `integration-boundary-executor` with HARD Tom-approval gate.
- It does not author new agents, commands, or skills. Those require explicit Tom approval and the relevant template.
- It does not invent new lanes. Adding a lane requires a `CLAUDE.md` change (Tom only).
- It does not override per-module isolation. If a module's filled `MODULE_TEMPLATE.md` says backend-db cannot touch factory-os schema, the router enforces that.

---

## 9. Maintenance

This file is updated when:
- A new module is approved (add lane row(s) to §3 and entries in §7).
- A new lane is added (Tom-approved CLAUDE.md change first).
- An agent is renamed or archived (cross-reference to AGENT_REGISTRY.md updated).
- A routing decision tree branch is found insufficient and a new branch is needed (factory-os-governor proposes; Tom approves).

This file is NOT updated for:
- Per-cycle dispatch records (those live in `docs/phase8/dry-runs/`).
- Live state changes (those go to `CURRENT_STATE.md` / `ACTIVE_NOW.md`).
- Locked-decision changes (those go to `CLAUDE.md` / `LOCKED_DECISIONS.md`).

---

**Owner:** `factory-os-governor` (proposes updates).
**Approver:** Tom (for §3 lane changes and §4 module additions).
**Last updated:** 2026-05-08 (Phase 8 Run F Wave 2 — initial creation).
