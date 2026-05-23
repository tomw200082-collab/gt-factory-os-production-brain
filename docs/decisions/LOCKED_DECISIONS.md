<!--
PROVENANCE: Extracted verbatim from PRODUCTION/CLAUDE.md on 2026-05-08 (HEAD: 5833fe6)
at the start of Phase 8 Run F kernel rewrite.

Source line ranges in pre-rewrite CLAUDE.md:
- Mission: lines 17-30
- Absolute non-negotiables: lines 32-43
- Locked decisions (UX doctrine, deployment, tech stack, auth, UI language, ledger
  semantics, stock model, RM batch, orders/integrations, LionWheel pickup, Excel,
  forecast, production reporting v1, counting v1, receipts and POs): lines 44-155
- Source-of-truth map: lines 170-177
- Rules for key workflows (Goods Receipt, Physical Count, Waste/Adjustment,
  Production Actual, PO workflow): lines 224-254
- Testing posture: lines 317-326
- What Claude must not do: lines 328-337
- Uncertainty discipline: lines 339-340
- Final project framing: lines 342-355

This file is a continuation of CLAUDE.md authority -- not a downgrade. The post-rewrite
CLAUDE.md kernel points here for full text. If this file conflicts with the new CLAUDE.md
kernel on locked decisions, CLAUDE.md wins (authority hierarchy rule 1).

Pre-rewrite full archive: PRODUCTION/docs/archive/CLAUDE.md.pre-kernel-rewrite-2026-05-08.md
-->

# GT Factory OS — Locked Decisions

> **Authority layer:** continuation of `CLAUDE.md` authority. Full text of locked decisions, non-negotiables, workflow rules, testing posture, and final framing extracted from CLAUDE.md to keep the kernel thin.
>
> **Authority rules (inherited from CLAUDE.md):**
> 1. If `CLAUDE.md` conflicts with this file on a locked decision, **CLAUDE.md wins**. This file cannot relax a locked decision.
> 2. **`CURRENT_STATE.md` is the only authority on live gate status, completion range, active critical path, and major open gaps.** This file does not restate live state.

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

---

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

---

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
- **Reversal — delivery-correction class (primary):** if a delivered task is later corrected to non-delivered (cancellation, return, dispute), append a `FG_OUT_PICK_REVERSAL` row with idempotency-key format derived from the original (`lw_fg_out_pick:{lw_task_id}:{lw_order_item_id}` plus reversal marker per implementation). Never UPDATE/DELETE the original.
- **Reversal — count-freeze interaction class (secondary; Tom-ratified 2026-05-23):** when the daily morning physical count snapshot includes FG quantities that have already been picked but not yet anchored, the picked rows are reversed via `FG_OUT_PICK_REVERSAL` with idempotency-key format `reversal-YYYY-MM-DD-<SKU>` and note `"Reversal of YYYY-MM-DD LW deliveries — items pre-picked before morning count"`. Distinct from delivery-correction reversal; both classes coexist; both are append-only; never UPDATE/DELETE the original. The chain's reconciliation handler MUST honour `ON CONFLICT (idempotency_key) DO NOTHING` for both key formats. Auditors MUST distinguish the two classes in dashboards and runbooks. Historical reference: 29 rows posted 2026-05-13 in the live ledger match this pattern; no rewrite of historical rows is performed by this ratification.
- **Pre-anchor guard (§5):** if `event_at <= latest_anchor_at` for the item, skip the ledger write and emit `lw_pick_pre_anchor_skipped` exception. The count anchor already reflects pre-anchor outflows; double-decrementing them is forbidden.
- **Implementation: `api/src/integrations/lionwheel/reconciliation.ts:reconcileAfterPoll` is the canonical implementation.** Any new chain function attempting a different trigger (e.g. `pickup_at <= now()`) is **forbidden** and must be reverted.
- **Forbidden movement_types — production code:** `LIONWHEEL_PICK` and `LIONWHEEL_UNPICK` remain wholly forbidden; production code may not emit them. Preserved in the enum (migration 0149) only to avoid breaking historical cleanup-window rows. Production code uses `FG_OUT_PICK` and `FG_OUT_PICK_REVERSAL` exclusively for the chain.
- **`LIONWHEEL_PICK_ADJUSTMENT` — Tom-approved manual reconciliation class (Tom-ratified 2026-05-23, Option A):** permitted ONLY for Tom-approved manual data-fix rows authored outside production code (e.g., direct psql or Supabase SQL editor). When used, the row MUST carry:
  - note text beginning with `"manual:<adjustment-kind> backfill <YYYY-MM-DD> (Tom-approved)"` followed by operational context (LW task id, original-vs-corrected qty, picker pattern); AND
  - idempotency-key format `<original-key-prefix>_backfill:<lw_task_id>:<lw_order_item_id>`.
  Production code (handlers, jobs, edge functions, reconciliation logic) may not emit `LIONWHEEL_PICK_ADJUSTMENT` under any circumstance. **Any future use of this movement type requires explicit Tom approval per row batch** (no standing authorization; Tom-approved-manual-only). If a production-code defect is corrected by manual backfill, the production-code fix MUST land in the same window (precedent: backend commit `b12e230` 2026-05-17 fixed the matcha carton/bag mismatch same-window as the 6 backfill rows). Historical reference: 6 rows posted 2026-05-17 match this pattern; this ratification does NOT authorize any rewrite of those rows; rewrite would require a separate Tom-approved data-correction migration.
- **Bridge gate `LIONWHEEL_FG_OUT_BRIDGE_ENABLED`:** must remain `false` until the cron→Node bridge is built, the chain has soaked clean for ≥24h, and Tom explicitly authorizes the flip in writing.
  - **Tom-ratified post-cutover state (2026-05-23):** the flag was authorized and flipped at Sunday 2026-05-10 cutover. Cron→Node bridge is operational; live ledger reflects continuous use (see `CURRENT_STATE.md` §"Post-cutover state"). The flag now must remain in its post-cutover state post-cutover. A flip back to `false` requires explicit Tom rollback decision plus parity replay. The four pre-flip prerequisites (Tom written approval, dry-run evidence, ≥24h soak, RUNTIME_READY signal) are historically satisfied; the post-cutover RUNTIME_READY signal coverage should be re-verified against `.claude/state/runtime_ready.json`. **Exact Railway env-var literal for `LIONWHEEL_FG_OUT_BRIDGE_ENABLED` is `NEEDS_READONLY_VERIFICATION` as of 2026-05-23 — behavioral evidence is TRUE; no env-var read or write performed in the 2026-05-23 docs cycle.**

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

---

## Source-of-truth map

- **Database is authoritative for:** master data after seed import; stock events; stock projections; forecast versions; planning runs; purchase recommendations; production recommendations; exceptions; audit trails
- **LionWheel is authoritative for:** open orders; shipment state
- **Shopify is authoritative for:** nothing operationally critical. Sync target and commercial boundary only. Platform wins on disagreement.
- **Green Invoice is authoritative for:** supplier invoice evidence. Not active prices by itself without validation rules.
- **Excel is authoritative for:** nothing long-term. Only transitional seed import and read-only exports.

---

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

---

## Testing posture
Before implementation is accepted, require:
- parity tests for stock projection
- idempotency tests for forms
- count-freeze race tests
- rebuild-from-ledger verification
- integration smoke tests
- form E2E tests on critical golden paths

Do not rely on ad hoc manual checking as the primary confidence mechanism.

---

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

---

## Uncertainty discipline
When uncertain, do **not** guess. Mark assumptions explicitly and halt until resolved. The live list of current UNRESOLVED items lives in `CURRENT_STATE.md`.

---

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
