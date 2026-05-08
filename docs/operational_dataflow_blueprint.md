# GT Factory OS — Operational Dataflow Blueprint

> **Status:** First-class permanent artifact. Authored 2026-04-23 from the GT Factory OS Master Operating Blueprint (plan `you-are-now-acting-giggly-pond.md`).
>
> **Authority:** This document is the primary lens for all audits. Every audit should step through the relevant rows and answer: "does this event actually flow all the way through, from birth to planning input?" A gap anywhere in a row is a real operational gap, regardless of what gate or signal claims it is complete.
>
> **Maintenance:** Update this document whenever any event's flow changes — new handlers, new projection logic, new exception triggers, new reversal paths.

---

## Core principle

The system's trustworthiness is not determined by which tables exist or which API handlers are written. It is determined by whether **every material event flows correctly from its source through to every downstream read model and planning calculation** — and whether operators can see that truth and act on it.

A handler that writes to `stock_ledger` but does not trigger a correct `current_stock_v2` update is not operational. A planning run that reads `v_planning_demand` but where `v_planning_demand` contains stale LionWheel data is not trustworthy. Every link in the chain matters.

---

## Event / Object Dataflow Map

| Event / Object | Where born | Source of truth | Write path | Stock/truth changed | Read models updated | Planning effect | Operator visibility | Exception triggers | Correction / reversal |
|---|---|---|---|---|---|---|---|---|---|
| **Forecast** | Forecast workspace (portal), authored by Tom + Alex | `forecast_versions` + `forecast_lines` | Portal → `POST /api/v1/mutations/forecasts` → form_submissions envelope → forecast_lines upsert; freeze window enforced | Demand signal changes | `v_planning_demand` (FG demand component); freshness_check producer | Net FG requirement changes on next planning run; production recommendations change | Forecast workspace; dashboard demand freshness tile | Stale forecast (>7 days, freshness_check); G-07 audit trigger; G-10 publication wiring | New forecast version created; previous version frozen; old lines DO NOT disappear — versioning is additive |
| **Open Orders (LionWheel)** | LionWheel system — GT does not own orders | LionWheel (authoritative); `orders_mirror` is the local copy | pg_cron → Supabase Edge Function → `orders_mirror` + `orders_mirror_lines` upsert with snapshot/retirement semantics | No stock change on mirror event; demand changes | `v_planning_demand` (open order demand component); freshness_check producer | Net FG requirement changes; open order fulfillment status | Dashboard freshness tile; LionWheel integration status screen | `lionwheel_unknown_sku` (42-168 open); mirror stale (> 4h, freshness_check); split/merge/cancel not resolved | Alias seeding resolves unknown SKUs; cancellations retire mirror rows; split/merge handled via snapshot retirement |
| **Goods Receipt** | GR form (portal), submitted by operator | Supabase DB after posting | Portal → `POST /api/v1/mutations/goods-receipts` → form_submissions envelope → `goods_receipts` record → `stock_ledger` row (GR_POSTED) → trigger → `current_stock_v2` balance update | RM or FG stock **increases** by received qty × UOM conversion; if PO-linked: PO `received_qty` increments, PO status → PARTIAL or RECEIVED | `current_stock_v2` (immediate trigger); PO status (trigger); change_log row | Reduces net purchase requirement on next planning run; reduces shortage flags; reduces open PO supply signal | GR success screen; stock balance visible on dashboard; PO status updated on PO detail | Large receipt discrepancy vs. PO qty; supplier-item not mapped (if future validation added) | GR reversal → `stock_ledger` GR_REVERSAL row; PO `received_qty` decrement (UNRESOLVED-GP-1, proposed Layer 2 fix) |
| **Waste / Adjustment** | Waste/Adj form (portal), submitted by operator | Supabase DB after posting | Portal → `POST /api/v1/mutations/waste-adjustments` → form_submissions envelope → `waste_adjustments` record → `stock_ledger` row (WASTE or ADJUSTMENT event_type) → trigger → `current_stock_v2` balance update; large positive adjustments → approval queue | RM or FG stock **decreases** (loss) or **increases** (found stock, requires approval); stock does NOT change until approval completes for large positive adjustments | `current_stock_v2` (trigger, only after approved/auto-posted); exceptions_inbox for large adjustments | Corrects stock truth for next planning run; influences net requirement | Waste success screen; approval queue for pending large adjustments; dashboard shows updated balance (only after posting) | Positive adjustment above threshold → approval exception; SYSTEM_TEST adjustments (should be flagged and cleaned) | Waste reversal → WASTE_REVERSAL row in stock_ledger; reversal requires admin authorization |
| **Physical Count** | Physical Count form (portal), operator blind count | Operator observation + Supabase DB projected qty snapshot | Portal → `POST /api/v1/mutations/physical-counts` → form_submissions envelope → `count_freezes` record; projected qty snapshotted at form open (blind count); delta computed at submit; small delta → `stock_ledger` COUNT_ADJUST → trigger → `current_stock_v2`; large delta → approval queue; approved count may create new `balance_anchors` row | Stock balance corrected to operator-counted qty; anchor optionally updated (replaces projection baseline) | `current_stock_v2` (trigger); `balance_anchors` (if anchor created); rebuild_verifier results | Corrects the stock baseline that planning reads; a count with large discrepancy may trigger a full re-plan recommendation | Count result screen (shows projected vs. counted vs. delta); approval queue if large delta | Large discrepancy → approval exception; rebuild_verifier > 0 (if anchor math breaks) | COUNT_ADJUST_REVERSAL row in stock_ledger; if anchor was created, it must be superseded by a new anchor (never deleted) |
| **Production Actual** | Production Actual form (portal), submitted after a production run | Supabase DB after posting; BOM version pinned at form open | Portal → `POST /api/v1/mutations/production-actuals` → form_submissions envelope → `production_actual` record with pinned `bom_version_id`; system computes per-RM consumption = output_qty × bom_lines.qty_per_unit; posts: PRODUCTION_OUTPUT (FG +output_qty), PRODUCTION_SCRAP (FG −scrap_qty), PRODUCTION_CONSUMPTION (RM −computed_qty per line) | FG stock **increases** by output_qty, then **decreases** by scrap_qty; each RM stock **decreases** by BOM-computed consumption; net stock_ledger: (output_qty − scrap_qty) FG gain, standard-BOM-derived RM losses | `current_stock_v2` for FG and all consumed RMs (multiple trigger updates, one per ledger row) | Reduces net FG production requirement; reduces net RM purchase requirement on next planning run; scrap increases future production recommendation quantity | Production Actual success screen showing what was output, scrapped, and consumed; stock balances update | Large scrap ratio → exception; RM stock falls below safety stock → shortage exception | PRODUCTION_OUTPUT_REVERSAL + PRODUCTION_SCRAP_REVERSAL + PRODUCTION_CONSUMPTION_REVERSAL rows; all three must be posted together |
| **BOM Version** | BOM maintenance screen (admin), authored by Tom or admin | `bom_head` + `bom_version` + `bom_lines` tables | Admin CRUD → `PUT /api/v1/mutations/boms/[id]` → `bom_version` record with new `bom_lines`; `bom_head.active_version_id` updated | No stock change on BOM edit itself; but future Production Actuals use the new version | Planning engine reads active BOM version at planning run time; Production Actual pins BOM version at form open | All future production recommendations recalculated with new BOM ratios; purchase requirements change if ratios change | BOM detail screen; version history visible; version pinned on production actual | No exception; but a BOM ratio change that is not yet reflected in current stock is a silent risk | Cannot undo a BOM version; only create a new version; pinned production actuals continue to use old version — this is correct behavior |
| **Stock Projection / Current Balances** | Derived continuously from ledger + anchors | `current_stock_v2` table (trigger-maintained) | Trigger on `stock_ledger INSERT` → update `current_stock_v2.balance` per balance key; rebuild_verifier() nightly confirms parity | Not an event source — it IS the result of all events above | Read by all planning functions and portal stock views | Primary input to `fn_compute_fg_net_requirements` and `fn_compute_component_net_purchase` | Dashboard stock health tiles; stock list `/stock/`; inline during form entry (proposed) | rebuild_verifier() > 0 → halt new events immediately; stock balance < 0 → ledger invariant violation | Only correct via new ledger events (COUNT_ADJUST, reversal rows); never UPDATE `current_stock_v2` directly |
| **Purchase Recommendations → PO lifecycle** | `fn_generate_purchase_recommendations` (planning run) | `planning_run_recommendations` table | Planner triggers run → `fn_execute_planning_run` → recommendations generated; planner reviews and approves → `fn_convert_recommendation_to_po` → `purchase_orders` OPEN + `purchase_order_lines` | No stock change on PO creation; PO is a pending supply signal | `purchase_orders` visible to operator on GR form; open POs visible on PO list | Open POs reduce net purchase requirement on next planning run (pending supply) | PO list `/purchase-orders`; PO detail page; GR form shows open POs for attachment | PO stale beyond supplier lead time → alert; recommendation not acted on → exception | PO cancellation; GR reversal → PO decrement (UNRESOLVED-GP-1, proposed Layer 2) |
| **Production Recommendations** | `fn_generate_production_recommendations` (planning run) | `planning_run_recommendations` table | Same planning run as purchase recs; feasibility enum: FEASIBLE \| INSUFFICIENT_RM \| INSUFFICIENT_CAPACITY \| BOM_MISSING | No stock change | `planning_run_recommendations` viewed by planner | Tells planner what to produce and in what quantities; INSUFFICIENT_RM → triggers purchase review | Production recommendation review screen | INSUFFICIENT_RM → planner must address RM shortage first; BOM_MISSING → blocks production recommendation | Recommendations are replaced on each planning run; previous run's recommendations are retained for audit |
| **Re-planning cycle** | Planner-triggered (not automatic) | Planning run output | Planner clicks "Run Planning" → fn_execute_planning_run reads current state: `current_stock_v2` + `v_planning_demand` (forecast + open orders) + open POs as pending supply + BOM | No stock change; recommendations replaced | `planning_run_recommendations`; planning history | Entire planning output is replaced; previous run kept for audit | Planning run history; run status; recommendation lists | Planning run FAILED status → exception; reproducibility check on demand | Runs are immutable after completion; correction = new run |

---

## BOM / Recipe Semantics — Deep Map

This is the most frequently misunderstood area. A plan or production actual that gets BOM semantics wrong produces incorrect stock truth without any error signal.

### How BOM consumption is computed

```
For each bom_line in pinned bom_version:
  consumption_qty = output_qty × bom_lines.qty_per_unit
  stock_ledger row: PRODUCTION_CONSUMPTION, balance_key = component, qty = −consumption_qty
```

### Scrap semantics

- `scrap_qty` reduces **FG output only**: `PRODUCTION_SCRAP` posts `−scrap_qty` against the FG balance key
- `scrap_qty` does **NOT** change RM consumption: consumption is based on `output_qty`, not `output_qty + scrap_qty`
- If you produce 100 units but 5 are scrapped: FG net gain = 95, RM consumed = BOM × 100
- This is a deliberate v1 simplification (no yield-adjusted consumption); operators must be explicitly trained on this

### Batch / output scaling

- BOM is ratio-based: `qty_per_unit` scales linearly with `output_qty`
- `bom_version.min_batch_units` exists in schema but v1 planning does NOT enforce batch rounding
- A recommendation for 3.5 units is valid even if the minimum batch is 10 — known v1 gap, may produce operationally impractical recommendations

### BOM version pinning

- The portal pins `bom_version_id` at Production Actual form open time (not submit time)
- If a BOM is updated between form open and form submit, the pinned version is used — correct behavior
- The pinned version is stored on `production_actual.bom_version_id` for permanent audit trail
- The planning engine uses `bom_head.active_version_id` at planning run execution time — not at recommendation-approval time

### Ratio vs. absolute quantities

- All BOM ratios are in units defined by the component's `default_uom_id`
- UOM conversion may be required if the operator enters in different units than the BOM specifies
- The API handler must enforce UOM-consistent inputs before posting consumption rows

### Correctness verification

After any Production Actual submission, run this check:

```sql
-- Verify: FG net gain = output_qty − scrap_qty
-- Verify: each RM net change = −(output_qty × bom_lines.qty_per_unit)
SELECT movement_type, balance_key, quantity
FROM private_core.stock_ledger
WHERE idempotency_key = '<production_actual_idempotency_key>'
ORDER BY movement_type;
```

---

## Inventory Semantics — Deep Map

**Terminology the system must enforce and auditors must verify:**

| Term | Definition in this system | How it's computed | What can make it wrong |
|------|--------------------------|-------------------|----------------------|
| **On-hand** | What is physically in the warehouse right now | `current_stock_v2.balance` | Unposted events; pending-approval adjustments that haven't posted yet; stale anchor with no new events |
| **Available** | In v1: same as on-hand (no reservation system) | `current_stock_v2.balance` | Same as on-hand; v1 does not track reservations or allocations |
| **Future available** | On-hand + expected inflows − expected outflows | On-hand + open PO qty + in-progress production output − open production order consumption | Open POs and production orders are signals, not certainties; planning uses this for net requirement |
| **In-flight / pending** | Events submitted but not yet posted (in approval queue) | Not reflected in `current_stock_v2` until approved | Pending waste adjustments; pending count adjustments — these exist in `form_submissions` but have NOT changed stock yet |
| **Waste pending approval** | Waste adjustment submitted, above threshold, awaiting admin approval | Does NOT change `current_stock_v2` or `stock_ledger` until approved | Operators must understand: submitting a waste adjustment does not immediately show in stock — only approved postings do |
| **Count pending approval** | Physical count discrepancy above threshold, awaiting approval | Does NOT change `current_stock_v2` until approved | Same as waste pending — the projected balance shown on the dashboard is NOT yet corrected by a pending count |
| **Count replacement behavior** | An approved count creates a COUNT_ADJUST ledger row that corrects the running balance | `stock_ledger` COUNT_ADJUST row; `current_stock_v2` trigger update; optionally creates new `balance_anchors` row | If anchor is created but rebuild_verifier() is not re-run immediately, the parity check may miss a divergence window |
| **Production scrap** | Finished goods that fail QC — reduce FG stock but RM consumption is NOT reduced | PRODUCTION_SCRAP row subtracts from FG; PRODUCTION_CONSUMPTION already posted based on full output_qty | If scrap is mis-entered (too high), RM consumption is already committed — cannot reduce RM retroactively without a reversal |
| **Safety stock** | Minimum balance below which a shortage exception should fire | Defined in `planning_policy` per item | If planning_policy is not kept current, shortage exceptions may be silent or spurious |

### The most dangerous semantic trap

A waste adjustment submitted with `status = pending_approval` does NOT reduce stock. If an operator sees "I submitted the waste" and then looks at the dashboard, the stock will not have changed yet. This will be a point of confusion that creates distrust.

**The portal must make the pending/posted distinction unmistakably clear.**

---

## Re-planning cycle — How real events feed planning

This is the full loop the system is designed around:

```
Real events (GR / Waste / Count / Production)
  → stock_ledger rows
  → current_stock_v2 updates (trigger)
  → v_planning_demand refreshed (from forecast + LionWheel mirror)
  → Planner triggers new planning run
  → fn_execute_planning_run reads current stock + current demand
  → New purchase + production recommendations generated
  → Planner reviews and approves
  → POs created from approved purchase recs
  → GR attached to POs as goods arrive
  → loop repeats
```

The system is never in a "plan-committed" state. Every planning run is independent and reproducible. Events between runs change stock truth; the next run incorporates those changes.

### Where this can break

- If `v_planning_demand` is stale (LionWheel mirror hasn't run) → plan uses old demand
- If `current_stock_v2` has a parity failure → plan uses wrong starting stock
- If BOM version is stale (admin hasn't updated recipe) → plan uses wrong consumption ratios
- If planning_policy is stale (lead times, MOQs not current) → plan produces impractical recommendations

All four must be verified before any planning run is used for real operational decisions.

---

## Audit usage

Run the relevant rows of the event table for any audit. For each row under audit, answer:

1. **Born**: Is the form/screen/integration working?
2. **Write path**: Does the portal call the correct API endpoint?
3. **Stock/truth changed**: Does the DB record the correct ledger row(s)?
4. **Read models updated**: Does `current_stock_v2` reflect the change immediately?
5. **Planning effect**: Does a planning run run immediately after reflect the updated stock?
6. **Operator visibility**: Does the portal show the correct updated state?
7. **Exception triggers**: Do relevant exceptions fire as expected?
8. **Correction / reversal**: Is there a clean reversal path?

"Handler exists" or "tests pass" does not answer any of these questions. Walk the chain with real data.

---

## False-green guards for this blueprint

| Claim | Why it may be false | How to verify |
|-------|--------------------|--------------| 
| "GR handler is done" | Handler exists; no real GR has ever posted to production DB | SELECT from stock_ledger after a real form submission |
| "Planning runs work" | Planning engine code passes tests; never been run against real stock + real demand simultaneously | Run fn_execute_planning_run after a real GR event and read recommendations |
| "LionWheel mirror is live" | Edge Function deployed; jobs_runs may show 0 successful runs | SELECT from jobs_runs WHERE job_name = 'lionwheel_mirror' ORDER BY run_at DESC LIMIT 5 |
| "rebuild_verifier() = 0" | True against 209 seed anchors; never verified after a stream of real events | Run SELECT rebuild_verifier() after the first real GR post |
| "Stock truth is established" | True at DB layer with seeds; zero real daily events exist in production | Confirmed only after operators use forms for 2+ weeks |

---

*Authored: 2026-04-23. Source: GT Factory OS Master Operating Blueprint, section B2.*
*Next update: after Layer 0 closed-loop validation is completed and first live stock event evidence is recorded.*
