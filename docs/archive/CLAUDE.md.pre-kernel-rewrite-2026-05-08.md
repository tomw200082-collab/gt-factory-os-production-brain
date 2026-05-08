<!--
ARCHIVED 2026-05-08 immediately before Phase 8 Run F kernel rewrite.

Source path at archive time: PRODUCTION/CLAUDE.md
Source HEAD at archive time: 5833fe60155b7de9aae696c801b2bfb6b4f6cb1e
Source line count: 355

Restore procedure: replace `PRODUCTION/CLAUDE.md` with the body of this file
(everything below the closing comment marker). All locked decisions in this
file remain authoritative as a fallback if the kernel rewrite is reverted.

The kernel rewrite extracts most content from this file into:
- PRODUCTION/docs/decisions/LOCKED_DECISIONS.md
- PRODUCTION/docs/contracts/SCHEMA_GUIDANCE.md
plus pointers in EXECUTION_POLICY.md / CURRENT_STATE.md / WORKSPACE_MAP.md /
AI_BRAIN_ROUTER.md / AGENT_REGISTRY.md / COMMAND_REGISTRY.md / VERDICT_GLOSSARY.md /
AGENT_TEMPLATE.md / MODULE_TEMPLATE.md.

This archive copy is read-only historical reference. Do not edit it.
-->

# GT Factory OS — Durable Contract

> **Authority layer:** durable contract. This file is **thin on purpose**.
> Mission, non-negotiables, locked architecture and source-of-truth boundaries, locked scope rules, high-level gate model, forbidden assumptions. **No current state. No execution policy. No transient context.**
>
> **Sibling docs (in this directory):**
> - `CURRENT_STATE.md` — volatile runtime status (completion range, gate status, critical path, open gaps, failure modes).
> - `EXECUTION_POLICY.md` — operational governance. Mirrors the `factory-os-autonomous-builder` skill.
> - `ACTIVE_NOW.md` — short, fast-moving operator context.
>
> **Authority rules:**
> 1. If this file conflicts with any sibling, **this file wins** on locked decisions. Sibling files cannot relax a locked non-negotiable.
> 2. **`CURRENT_STATE.md` is the only authority for live gate status, completion range, active critical path, and major open gaps.** Every other file (including memory files, ACTIVE_NOW.md, and this file) must **point** to it, never **restate** it.

---

## Mission
Rebuild GT Factory OS from an Excel-centered operational workbook into a production-grade operational platform for GT Everyday — a small beverage factory in Israel producing cocktails, teas, smoothies, and margaritas.

This project is a system rebuild, not an Excel cleanup.

The rebuilt platform must deliver:
- trusted stock truth
- simple operator workflows
- clean source-of-truth boundaries
- reliable purchase and production recommendations
- minimal Excel dependence
- cloud-first runtime with on-prem read-only fallback

The workbook `GT_Factory_OS.xlsx` is a **current-state source only**. Do not preserve its structure.

## Absolute non-negotiables
1. Stock truth ships before planning cutover.
2. Excel is transitional only. It is not the long-term system brain.
3. Forms and integrations create events.
4. Postgres stores truth.
5. The ledger stores immutable history.
6. Projections compute current state.
7. The planning engine computes recommendations.
8. Dashboard and Excel consume curated read models only.
9. No Excel round-trip ever.
10. Prefer the simplest architecture that will not break under daily factory use.

## Locked decisions

### UX / UI doctrine

UX/UI is a first-class production discipline, not a polish layer. The portal is the
operator workflow and the operator workflow is half the platform. The following is locked:

- The five UX agents (`ux-flow-architect`, `interaction-design-specialist`,
  `visual-system-designer`, `ux-content-state-designer`, `accessibility-usability-auditor`)
  are read-only auditors. They do not write portal source.
- `portal_ux_standard.md` (in the portal repo) is the locked register; only
  `ux-content-state-designer` may write it.
- A surface with an open P0 finding from `/ux-release-gate` may not ship.
- Hebrew operator copy is per-string Tom-pinned; no surface-wide approval is implied.
- Every user-visible portal change requires a UX handoff packet before merge.

The UX gate runs in parallel with the technical gate; both must pass.

### Deployment
- Cloud primary
- On-prem Linux replica for read-only dashboard fallback only
- No writable on-prem fallback
- Outage fallback for writes = paper forms + back-entry if outage is prolonged

### Tech stack
- Database/platform: Supabase managed Postgres
- API: Node 20 + Fastify + Zod + Kysely
- Portal: Next.js 15 App Router + Tailwind + shadcn/ui + TanStack Query
- Language: TypeScript across app code

### Auth and roles
- Supabase magic-link email auth
- No passwords
- No 2FA in v1
- Roles: `operator`, `planner`, `admin`, `viewer`

### UI language
- Developer-facing artifacts (code, comments, tests, docs, migration files, API field names, internal contracts): English only.
- GT operator/planner/admin-facing workflow UI (form labels, buttons, banners, status text, empty-state messages, column headers, and any copy a factory user reads during daily operations): plain operational Hebrew where Tom explicitly requires it. Tom's per-surface Hebrew copy register is the authoritative source; if no register entry exists for a surface, English is acceptable.
- Hebrew appears in data values (supplier names, contacts, payment terms, addresses) regardless of the above rule.
- No full RTL layout in v1.

### Ledger semantics
- `event_at` is authoritative for balance math
- `posted_at` is for idempotency and audit
- Backdating is allowed
- Ledger is append-only; corrections by reversal rows, never delete/update in production

### Stock model
- `balance_anchors` is separate from `stock_ledger`
- Current stock = anchors + posted ledger deltas since anchor
- Do **not** implement `v_live_stock` as a Postgres materialized view with assumed incremental refresh
- Use a transactionally maintained projection table (or equivalent current-balance read model) plus a nightly rebuild-verification job

### RM batch and expiry
- Schema may support RM batch fields for future use
- v1 operational workflows and projections **ignore RM batch**
- **No expiry logic in v1.** No FEFO, QA hold, or expiry alerts.

### Orders and integrations
- LionWheel is the operational source for open orders and shipments
- Planning demand = forecast + open orders
- System does not own customer orders
- Shopify is a finished-goods stock sync boundary; if Shopify and the platform disagree, the platform is authoritative
- Green Invoice supplies supplier invoice evidence and price history
- Active supplier price auto-updates only when mapping is unambiguous and the price change is within threshold

### LionWheel pickup → ledger decrement (Tom-locked 2026-05-07, ratifies decision #46 anchor)
- **Trigger is delivery confirmation, NOT pickup_at.** A `FG_OUT_PICK` ledger row is written ONLY when a LionWheel task transitions to `status IN ('ROUNDTRIP_DELIVERED','COMPLETED')` — i.e. the driver has confirmed delivery to the customer.
- **Rationale:** Factory OS on-hand represents physical inventory at the factory **before handover**. A task at `ASSIGNED`/`ACTIVE`/`IN_TRANSFER` means goods have left the warehouse but have not been delivered to the customer; per the operational model the on-hand is unchanged until handover. Shopify "available" already accounts for committed open orders; the platform's on-hand IS the physical-at-factory number.
- **Quantity is `lw_qty_picked` from `/tasks/show/<id>` (enriched on terminal status), never `lw_qty_ordered`.** If `lw_qty_picked` is NULL, no ledger row is written and an exception is emitted; the chain re-tries on next poll.
- **Idempotency key:** `lw_fg_out_pick:{lw_task_id}:{lw_order_item_id}` (no transition counter). `ON CONFLICT (idempotency_key) DO NOTHING` blocks replays.
- **Reversal:** if a delivered task is later corrected to non-delivered (cancellation, return, dispute), append a `FG_OUT_PICK_REVERSAL` row; never UPDATE/DELETE the original.
- **Pre-anchor guard (§5):** if `event_at <= latest_anchor_at` for the item, skip the ledger write and emit `lw_pick_pre_anchor_skipped` exception. The count anchor already reflects pre-anchor outflows; double-decrementing them is forbidden.
- **Implementation: `api/src/integrations/lionwheel/reconciliation.ts:reconcileAfterPoll` is the canonical implementation.** Any new chain function attempting a different trigger (e.g. `pickup_at <= now()`) is **forbidden** and must be reverted.
- **Forbidden movement_types for v1 LionWheel chain:** `LIONWHEEL_PICK`, `LIONWHEEL_UNPICK`, `LIONWHEEL_PICK_ADJUSTMENT`. These were briefly added by migration 0149 in support of an alternative trigger that was rejected after live ratification. Migration 0149 retains the values to avoid breaking historical rows from the cleanup window, but **no production code may emit them**. Use `FG_OUT_PICK` and `FG_OUT_PICK_REVERSAL` only.
- **Bridge gate `LIONWHEEL_FG_OUT_BRIDGE_ENABLED`:** must remain `false` until the cron→Node bridge is built, the chain has soaked clean for ≥24h, and Tom explicitly authorizes the flip in writing.

### Excel
- Excel is transitional only
- **Allowed:** one-time seed import for masters; nightly values-only export; temporary sanity review during transition
- **Forbidden:** workflow execution; stock truth; planning truth; integration logic; operator authoring; round-trip editing

### Forecast
- Owned by Tom and Alex
- Monthly first, then weekly, then daily operationally
- 8-week horizon
- Versioned; freeze window applies

### Production reporting v1
- Operator reports output quantity + scrap quantity + notes
- System computes standard consumption from the **two-head BOM**:
  - **PACK head** (`items.primary_bom_head_id` → `bom_kind='PACK'` or `'REPACK'`): packaging components consumed proportionally to (output + scrap).
  - **BASE head** (`items.base_bom_head_id` → `bom_kind='BASE'`, when present): liquid raw-material components consumed proportionally to total base liters required, derived from the PACK BOM's single `BASE_BOM` line (`component_ref_type='BASE_BOM'`, `final_component_id=NULL`, `final_component_qty=`liters per pack output).
  - REPACK and pure-pack items have no BASE head — single-head explosion applies.
- Both BOM versions (PACK and BASE-when-applicable) are **pinned at form-open time** and **rejected on stale submission** (409 `STALE_BOM_VERSION` for PACK / `STALE_BASE_BOM_VERSION` for BASE).
- All consumption rows for a single submission are written to `stock_ledger` inside one transaction with the form's `idempotency_key`. Per-row idempotency keys carry the source (`pack` / `base`) and `component_id` so pack and base never collide: `PA:<idem>:CONSUME:<source>:<component_id>`.
- `related_bom_version_id` on each `stock_ledger` row is source-correct (PACK lines → pack version; BASE lines → base version).
- Do **not** collect manual per-component actual consumption in v1.

### Counting v1
- Full monthly count is the base process
- Small discrepancies auto-post; large discrepancies require approval
- Count uses start/submit freeze semantics
- Do not overbuild cycle counting in v1

### Receipts and POs
- Partial receipts are supported in v1
- Purchase flow: system recommends → planner reviews → planner approves → user creates PO via workflow → PO becomes OPEN → receipts may attach
- Goods Receipt must still allow PO-less receipt when no pre-entered PO exists
- Supplier returns are **not** in v1
- Manual PO creation is permitted in v1 as a guarded planner/admin exception path. A planner or admin may author a PO directly without an approved purchase recommendation, but must supply supplier, canonical line items where available, quantities, expected delivery date, and a reason. Source = `manual` is recorded; `source_recommendation_id` / `source_run_id` remain NULL; no stock movement is posted; no Goods Receipt is created automatically. Goods Receipt can later reference the manual PO normally.

## Core architectural model
The system is designed as these layers:

1. **Canonical master data** — items, components, BOM (head/version/lines), suppliers, supplier_items, planning policy, UOM tables
2. **Operational event intake** — forms, planning screens, integrations, admin imports
3. **Validation and policy gate** — required fields, idempotency, duplicate detection, approval thresholds, UOM validation, permission checks
4. **Canonical ledger** — append-only stock ledger; one source of stock history; reversal rows only
5. **Projection layer** — current stock projection, open orders mirror views, open supply views, readiness and exception projections
6. **Planning engine** — SQL-first; writes to `planning_runs` and `planning_run_lines`; never mutates masters or ledger
7. **Portal** — operator/planner/admin workflows; role-gated routes
8. **Dashboard** — read-only control tower; no editing
9. **Jobs and integrations** — LionWheel pull, planning recompute, nightly exports, integrity checks, digest emails

## Source-of-truth map

- **Database is authoritative for:** master data after seed import; stock events; stock projections; forecast versions; planning runs; purchase recommendations; production recommendations; exceptions; audit trails
- **LionWheel is authoritative for:** open orders; shipment state
- **Shopify is authoritative for:** nothing operationally critical. Sync target and commercial boundary only. Platform wins on disagreement.
- **Green Invoice is authoritative for:** supplier invoice evidence. Not active prices by itself without validation rules.
- **Excel is authoritative for:** nothing long-term. Only transitional seed import and read-only exports.

### Production agent architecture (Phase 8)

Production execution is performed by four conservative agents:
- `backend-db-executor` — backend API, DB, migrations, jobs (replaces `executor-w1` after Wave 6).
- `portal-production-executor` — Next.js portal authoring (replaces `executor-w2` after Wave 6).
- `integration-boundary-executor` — LionWheel / Shopify / Green Invoice / Edge Functions (replaces `executor-w4` after Wave 6).
- `ops-docs-curator` — docs hygiene + archive (new role; no executor-era predecessor).

Governance is performed by:
- `factory-os-governor` — go/no-go (replaces `governor.md` after Wave 6).
- `release-verifier` — pre-merge / pre-deploy verification.
- `source-of-truth-auditor` — cross-doc drift classification.
- `verifier.md` — post-executor PASS/FAIL (kept indefinitely).

The five UX agents listed in §UX / UI doctrine round out the operating layer. All agents
follow the source-of-truth hierarchy already locked in this document.

## Input-source map

- **Forms (human-reported facts):** Goods Receipt; Waste / Adjustment; Physical Count; Production Actual (Phase 3); PO creation workflow
- **Planning screens (structured judgment):** Forecast planning workspace; Purchase recommendation review; Production recommendation review
- **Integrations:** LionWheel orders and shipments; Shopify FG stock sync; Green Invoice invoice/price evidence
- **Admin / bulk import:** item master; component master; BOM maintenance; supplier maintenance; planning policy
- **CLI / scripts:** initial imports; backfills; repair scripts; migration scripts; one-off reconciliation
- **Explicitly forbidden as runtime dependency:** MCP is not a runtime input channel. Claude Code tooling must not become part of the live operational path.

## Gate model (high level)

No gate may run partially in production while the previous gate is unverified. Each gate owns its own exit evidence.

1. **Gate 1 — Alignment / Contracts** — architecture map, schema map, portal module map, form definitions, integration contracts, migration phases, validation gates, rollback logic. Exit: artifacts internally consistent; no implementation begins before exit.
2. **Gate 2 — Foundation / Masters / Admin** — schema foundation, auth + roles, master-data import, admin CRUD, nightly export + jobs monitor baseline. Exit: masters round-trip through API; nightly export runs green; jobs monitor records every scheduled run.
3. **Gate 3 — Stock Truth** — ledger, anchors, stock projection, Goods Receipt, Waste / Adjustment, Physical Count, parity / rebuild verification. Exit: projection equals rebuild-from-ledger within tolerance; idempotency tests pass; count-freeze race tests pass; minimal Exceptions Inbox in place. **Stock truth must ship before any planning cutover.**
4. **Gate 4 — Operational Mirrors / Forecasting** — LionWheel mirror, forecast planning screen, shipment / open-order context, freshness checks. Exit: LionWheel mirror reconciles end-to-end including split/merge/cancel; forecast versioning + freeze enforced; freshness exceptions emit on stale integration.
5. **Gate 5 — Planning / Recommendations** — planning engine, purchase recommendations, production recommendations, Production Actual, cost rollup. Exit: planning runs reproducible from inputs; recommendations require human approval before becoming POs; Production Actual posts BOM-derived consumption against pinned BOM version; cost rollup matches manual reconciliation on a known fixture.

## Recommended v1 scope
Ship only the narrow platform needed to create trust.

- **Phase 0:** database schema foundation; auth and roles; admin CRUD for masters; one-time master import; nightly Excel export; jobs monitor
- **Phase 1:** stock ledger; anchors; stock projection; Goods Receipt; Waste / Adjustment; Physical Count; minimal Exceptions Inbox; minimal Dashboard; parity and rebuild verification gates
- **Phase 2:** LionWheel mirror; Forecast Planning Screen; shipment handling if needed; data freshness checks
- **Phase 3:** planning engine; recommendations; Production Actual form; cost rollup

Do not expand v1 into full WMS, full procurement, FEFO, location/bin tracking, customer pricing, or finance write-back.

## Rules for key workflows

### Goods Receipt
- May attach to open PO
- Must allow PO-less receipt
- Supports partial receipt
- Creates stock-affecting event(s)
- Must be idempotent

### Physical Count
- Blind count by default
- Snapshot projected quantity at form open
- Compute delta against that snapshot at submit
- Small discrepancies auto-post; large discrepancies go to approval
- Approved count may create a new anchor

### Waste / Adjustment
- Negative adjustments allowed per policy
- Positive "found stock" adjustments require stronger control
- Use approval rules, not free editing

### Production Actual
- Simplified v1 model only: output + scrap + notes
- Compute consumption from pinned BOM version
- Never resolve BOM version at submit time if already pinned earlier

### PO workflow
- Purchase recommendations are produced only by the planning engine. The engine never creates purchase orders autonomously.
- **Recommendation path (preferred):** Planning run → purchase recommendations → planner reviews → planner approves → convert to PO → PO OPEN → receipts attach. This is the standard daily flow.
- **Manual path (guarded exception):** A planner or admin may create a PO directly from the PO list without an approved recommendation. Required fields: supplier, line items (component or item), quantities, expected delivery date, and a reason. The PO is created in OPEN status. `source_type = 'manual'` is recorded. No stock is posted at creation. GR may reference the PO normally. Operator and viewer roles cannot create POs via either path.
- **No autonomous ordering** means no engine- or system-created POs without explicit human action. It does not forbid controlled manual PO authoring by planner/admin.

## Schema guidance

### Primary keys
- Legacy text IDs as PKs for business masters where stable and meaningful
- UUIDs for system-generated records, forms, runs, approvals, history

### Precision
- Exact numeric types, never float
- High-precision numeric standard for quantities, ratios, UOM conversions
- Separate lower-scale money standard for money
- Prefer domains to keep quantity/money semantics consistent

### BOM modeling
- Versioned structure: `bom_head` / `bom_version` / `bom_lines`
- `items` points to a BOM head / active version model, never to ad hoc version fields

### Purchased finished goods
- Do not duplicate `BOUGHT_FINISHED` items into components
- `items.supply_method` enum (exact legacy values, not normalized): `('MANUFACTURED','BOUGHT_FINISHED','REPACK')`
  - `MANUFACTURED` — produced from a BOM
  - `BOUGHT_FINISHED` — resold as-is; direct supplier mapping via `supplier_items.item_id`
  - `REPACK` — produced by repackaging an input component; supplier mapping lives on the input component, not on the repack output

### Audit semantics
For important human actions, preserve both a user foreign key and a display-name snapshot.

## Integration guidance

### LionWheel
- Mirror internally
- Never compute planning directly from live API calls
- Use polling plus webhooks where available
- Track snapshot runs and retirement semantics
- Treat split/merge and cancellation handling as first-class reconciliation concerns

### Shopify
- Sync FG stock from the rebuilt system to Shopify
- Reconcile periodically
- Exception-based review for unexplained drift

### Green Invoice
- Feed `price_history`
- Do not auto-create new components from invoice lines
- Do not auto-update active prices unless mapping quality and threshold rules pass
- Net-of-VAT cost semantics

## Security and access rules
- Core tables live in a private schema
- Browser does not talk directly to core operational tables
- API is the permission boundary
- Selective RLS only where it actually helps
- Protect audit tables and ledger from update/delete
- Prefer soft-delete / archive for masters

## Observability and operations
- Keep a jobs run log
- Track latest successful run for every scheduled job
- Emit exceptions for stale integrations and failed jobs
- Global break-glass mode that makes the system read-only and pauses jobs
- Prefer clear failure over silent drift

## Testing posture
Before implementation is accepted, require:
- parity tests for stock projection
- idempotency tests for forms
- count-freeze race tests
- rebuild-from-ledger verification
- integration smoke tests
- form E2E tests on critical golden paths

Do not rely on ad hoc manual checking as the primary confidence mechanism.

## What Claude must not do
- Do not preserve workbook structure by default
- Do not assume Excel remains editable
- Do not build a second writable fallback system
- Do not overbuild offline/PWA features in v1
- Do not introduce a second planning service in v1
- Do not model FEFO / expiry / location / bin complexity in v1
- Do not add customer pricing unless explicitly confirmed
- Do not build an ERP for everything
- Do not guess live API field names for LionWheel or Green Invoice without inspection

## Uncertainty discipline
When uncertain, do **not** guess. Mark assumptions explicitly and halt until resolved. The live list of current UNRESOLVED items lives in `CURRENT_STATE.md`.

## Final project framing
This is a **narrow, high-trust factory operations platform.** It is not a generic ERP.

It succeeds if:
- stock truth becomes trusted
- operator workflows become simpler than the workbook
- planning recommendations become reproducible and auditable
- Excel stops carrying operational risk
- the system can be rolled forward and rolled back safely

Tiebreakers:
- If there is tension between elegance and reliability, choose **reliability**.
- If there is tension between scope and trust, choose **trust**.
- If there is tension between speed and irreversible complexity, choose the **simpler path**.
