# GT Factory OS — Execution Policy

> Operating law: lanes, modes, signals, retry, approvals, frozen flags.
> ⊥ relax a locked decision in `CLAUDE.md` — `CLAUDE.md` wins on every conflict.
> Retired amendments (Mode B-AMMC, Mode B-Portal-Refactor, Mode B-Planning-Corridor, Mode B-LionWheel-Runtime-Closure) → `docs/archive/EXECUTION_POLICY.pre-lean-2026-07-31.md`.

## Purpose

Standing-order model: once scope is locked, lanes proceed on pre-authorized backlogs without per-item re-authorization, bounded by rules below. Less babysitting, ⊥ less stock-truth discipline.

## Window ownership

| W | Owns | ⊥ own |
|---|---|---|
| **W1** DB / schema / migrations / tests / imports | schema, migrations, pgTAP, imports, fixture validation, runbooks, Gate 3 runtime closure | UI; integration contracts |
| **W2** canonical portal / production UI | portal UI, route tree, contracts-layer reconciliation, admin/planner/operator surfaces | ⊥ invent backend contracts; ⊥ adopt sandbox files literally |
| **W3** sandbox / mock UI | experimental & reference UI, concepts, patterns | ⊥ ever canonical; ⊥ own prod routes; ⊥ source stock truth |
| **W4** integrations / jobs / exports / dashboard contracts | LionWheel / Shopify / Green Invoice contract-first specs, jobs, exports, read-model contracts | ⊥ invent core truth contracts; ⊥ write ledger directly |
| **W5** architecture / governance | orchestration, gating, overlap detection, stop conditions, cross-window conflict resolution | ⊥ implement features — routes work, ⊥ perform it |

Boundary crossing without W5 approval = `ownership_conflict`.

## Lanes & agents

| Lane | Production agent | Legacy (dispatchable until Wave 6) |
|---|---|---|
| `backend-db` | `backend-db-executor` | `executor-w1` |
| `portal` | `portal-production-executor` | `executor-w2` |
| `integration` | `integration-boundary-executor` | `executor-w4` |
| `docs` | `ops-docs-curator` | — |
| `governance` | `factory-os-governor` | `governor` |
| `release-gate` | `release-verifier` | `verifier` (kept indefinitely) |
| `source-of-truth` | `source-of-truth-auditor` | — |
| `ux-audit` | 5 UX agents (read-only, parallel) | — |

≤4 simultaneous executor lanes: backend + portal + integration + docs. UX / governance / gates ⊥ count as a lane. One lane carried by legacy **or** new agent, never both. Default = new agent unless Tom says otherwise. Wave 6 archival per `docs/phase8/deprecation/ACTIVE_SURFACE_REDUCTION_PLAN.md`; each step ! Tom approval.

UX agents are read-only, own no window, produce handoff packets `portal-production-executor` consumes.

## W2 modes

- **Mode A** (default): read-only audits, pattern extraction, handoff-prep, convention docs. ⊥ contract authoring, ⊥ canonical authoring.
- **Mode B** (auto-authorized on `RUNTIME_READY(form)`, scoped to that **one named form**): canonical portal authoring for that form. ⊥ re-authorization needed for A→B. **Exit:** back to A once local portal E2E green for that form.

Mode B ⊥ generalize. Each additional form ! its own `RUNTIME_READY`. Only one form in Mode B at a time.
All pan-form carve-outs are **retired** (Tom 2026-07-31). Any pan-form authoring now needs a fresh Tom-authorized amendment — shape (distilled from 3 retired precedents):
1. Cites a Tom-approved plan file naming the corridor in-scope, by section.
2. Enumerates allowed/forbidden explicitly — ⊥ inherit blanket W2 canonical rights.
3. Exit gate is per-tranche: typecheck + build + lint + smoke on touched surfaces + role-matrix walkthrough; `active_mode.json` records exit.
4. Names its expiry condition (e.g. "N named P0 findings all CLOSED").
5. Single-active-variant: only one pan-form amendment live at a time, even if others are unexpired.

## Signals

⊥ aliases.

- **`FILE_READY(form)`** — files/surfaces exist in usable handoff shape. **⊥ authorize W2 canonical authoring.**
- **`RUNTIME_READY(form)`** — W1 execution-authorization. Backend contract closed & evidenced → W2 may author that one form under Mode B.
- **`TOOL_FAILURE_UNCLEARED`** — W4 artifact whose same tool failure repeated after one retry. Parks the artifact. Lives inside `tool_failure` class, ⊥ a sixth class.

**Rule:** A→B only on `RUNTIME_READY`, never on `FILE_READY` alone. ⊥ silently alias the two.
**Editorial (docs-curation passes):** an older doc using `FILE_READY` loosely as "go-ahead" ! be upgraded to `RUNTIME_READY` on sight, ⊥ preserved as ambiguous history.

## Retry

1→2→3 (retry / replan / human checkpoint) applies to W1 critical path and W2 Mode B authoring.
W4: retry once; same failure repeats → mark `TOOL_FAILURE_UNCLEARED`, park it. W4 may advance to next backlog item only if ⊥ open `contract_failure`, ⊥ open `assumption_failure`, ⊥ dependency collision with the parked artifact. Dependency unclear → escalate W5, ⊥ silently skip. A single W4 tool failure ⊥ trigger whole-project reassessment. `contract_failure` | `assumption_failure` inside W4 collapses its two-try budget to 0 → governor.

## W4 backlog & constraints

Order: 1 Shopify FG sync spec · 2 Green Invoice supplier-price evidence spec · 3 dashboard read-model spec · 4 integration freshness / failure-surface spec.

Per artifact (hard): requirements-only, file-only. ⊥ schema, ⊥ migrations, ⊥ mirror tables, ⊥ runtime code, ⊥ handlers, ⊥ jobs, ⊥ invented provider field names, ⊥ endpoint invention, ⊥ auth-mechanics invention, ⊥ reopening locked decisions.

### FR1→write→FR2 bracket (mandatory)

**Scope:** any W4 artifact referencing `db/migrations/` filenames by number, implying a "next free slot" claim, or whose correctness depends on the migrations directory state. ⊥ apply to specs naming no migration file.

1. **FR1** — immediately before write, list `gt-factory-os/db/migrations/`. Capture filenames + latest mtime. Collision with a number about to be referenced, **or** an unexpected new migration since last verifier run → **HALT**, emit `contract_failure`. ⊥ silently substitute a renumbered target.
2. **WRITE** — ! complete ≤60s after FR1. Over 60s → abort, discard, restart from fresh FR1.
3. **FR2** — immediately after last write, re-list. New migration appeared between FR1 and completion → **HALT**, emit `contract_failure` (W1 raced the bracket).

Second FR1 collision or FR2 race on the same artifact in the same cycle = `TOOL_FAILURE_UNCLEARED` → park + governor. ⊥ third bracket.

**Failure classes:** FR1 collision or FR2 race → `contract_failure` (no retry, human checkpoint !). Silent renumber substitution → `assumption_failure` (no retry, human checkpoint !).

**Same-day same-slot pairing exception** (Tom 2026-05-23) — permitted when ALL hold: same dispatch (or coordinated dispatches agreeing in commit message) · co-applied in one atomic deployment · distinct concerns with ⊥ schema/contract ownership collision (⊥ two `CREATE TABLE` of same table, ⊥ two `CREATE OR REPLACE FUNCTION` of same signature) · commit message enumerates the pair + rationale. Then FR1 ! NOT classify it as `contract_failure`. Precedent: 2026-05-15 co-applied `0198_cleanup_test_forecasts.sql` + `0198_fg_projection_v3_fast_days_of_cover.sql`.
Still failures: a second author silently renumbering an existing same-slot file (`assumption_failure`) · a pair needing deterministic apply order outside one transaction · a pair landing in different deployments.

**Why:** cycles 3/4/5/5c produced a recurring W1↔W4 race — autonomous W1 migration landings invalidated W4 renumber math mid-flight. Bounding the write window and verifying both sides catches it deterministically. Non-retroactive.

## W5 — service on demand

Invoked for: approve/reject review of a landed artifact · real ownership collision · `contract_failure`/`assumption_failure` arbitration · explicit execution-map revision. ⊥ a continuously running lane.

**Artifact visibility (hard):** W5 reviews only when (a) full artifact text pasted inline, or (b) a verified readable path whose content was actually inspected. **Summary-only review ⊥ permitted** → emit `assumption_failure`, request the artifact.

## Reply discipline

- **No dead air.** A response ⊥ end with all lanes parked and no next action. Every reply names the single smallest concrete operator action. "Waiting" / "all lanes idle" ⊥ valid output states.
- **Per-window blocks.** Input spanning >1 window → separate labelled block per window + one overall next action reconciling across them.
- **Window-label sanity.** Label ≠ actual surface touched → reclassify **before** routing, and record it: "labeled WX → reclassified WY because …". ⊥ pass a mislabeled window downstream.

## Stop semantics

Halts the standing order for the affected lane, forces governor arbitration: stop condition · ownership collision · `contract_failure` · `assumption_failure` · W4 `TOOL_FAILURE_UNCLEARED` with unclear dependency.
Standing orders ⊥ override the failure taxonomy or human-checkpoint rules. Collapsing any of these into silent continuation is an anti-pattern.

## Global constraints

⊥ DDL outside W1 ownership · ⊥ auth wiring beyond locked decisions · ⊥ W3→canonical promotion · ⊥ reopening locked decisions · ⊥ live integration runtime beyond what `CLAUDE.md` §Authorization permits · ⊥ assume a flag/bridge/gate's state before an external write — verify live; a non-terminal upstream status ! be treated as complete.

> Claude tooling MAY be in the live operational path and MAY write to connected systems, per `CLAUDE.md` §Authorization (Tom 2026-06-20). Prior blanket prohibitions here are superseded.

## Frozen flags

Stay `false` until Tom written approval + dry-run + ≥24h soak + RUNTIME_READY. A flip without all four emits `frozen_flag_unexpected_state` and halts integration writes.

| Flag | State |
|---|---|
| `LIONWHEEL_FG_OUT_BRIDGE_ENABLED` | behaviorally **`true`** since cutover 2026-05-10; four prerequisites historically satisfied. Exact Railway env literal `NEEDS_READONLY_VERIFICATION`. Rollback to `false` ! Tom decision + parity replay |
| `SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED` | `false` — Phase 5 only, ⊥ approved |
| `SHOPIFY_FG_SYNC_LIVE_ADAPTER_WIRED` (code sentinel, `factory_os_jobs/index.ts:87`) | `false` — Tom-locked 2026-05-07 R1. Gates every live Shopify mutation. Flip = code change + deploy, ⊥ a DB flag |
| `SHOPIFY_FULFILLMENT_BRIDGE_LIVE_ADAPTER_WIRED` (code sentinel) | `false` |

`private_core.feature_flags.shopify_available_reconcile_live` **is** the live gate on the sole Shopify writer (Edge Fn `shopify_available_reconcile`, cron 24) — it has a reader, just not one visible from repo grep alone (was deployed-only; adopted to source 2026-08-01). `shopify_fg_sync_v2_live` gates a dormant delta-writer, flag-disabled since 0307. Detail: skill `shopify-sync`. Cost of the grep-proves-absence error: migration `0302`.

## Approval thresholds

Aligned to `CLAUDE.md` §Authorization — that file wins on conflict.

| Action | Approval |
|---|---|
| Frozen flag / code sentinel flip | Tom written + dry-run + ≥24h soak + RUNTIME_READY |
| New `movement_type` on `stock_ledger` | Tom written |
| BOM head/version/lines column change | Tom written |
| External write: irreversible, mass-scale, or money-/customer-facing | Tom written + dry-run |
| Auth flow change (`middleware.ts`, `(auth)/**`) | Tom written |
| Hebrew copy change | Tom register entry |
| Archiving a legacy agent | Tom written + Wave 6 evidence |
| `CLAUDE.md` edit | Tom (sole writer) |
| Other authority docs | `ops-docs-curator` under `factory-os-governor` approval |
| **`git push` + PR merge** | **none** — Claude autonomous when checks green & verified (Tom 2026-06-20) |
| **Prod deploy + prod-DB migration apply** | **none** — Claude autonomous when deploy gates green; announce-then-proceed (Tom 2026-07-24) |
| External write: reversible, single-scope, low blast radius | none — proceed when confident |
| RUNTIME_READY emission with full test evidence | none — self-authorizing |
| Local dev work on dev DB · new tests | none |
