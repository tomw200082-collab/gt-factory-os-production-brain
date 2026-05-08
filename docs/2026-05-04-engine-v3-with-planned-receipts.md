# Engine v3 — Planned Receipts + Daily MRP Design

**Date:** 2026-05-04
**Status:** Design proposal, awaiting Tom review. **No code in this document. No migration. No function changes.**
**Authors:** Tom (problem statement) + Claude (research synthesis)
**Supersedes (in scope):** `fn_propose_weekly_production_plan` v2 (`db/migrations/0140_fn_propose_weekly_production_plan_v2.sql`)
**Companion:** `docs/2026-05-03-daily-production-plan-design.md` (engine policy §3 — this doc operationalizes that spec into a correct algorithm)

---

## 1. The bug in v2 (one paragraph)

`fn_propose_weekly_production_plan` v2 (migration 0140) computes per-base demand for the proposal week, subtracts only **current physical stock** (`current_balances` × `base_fill_qty_per_unit`), divides the residue by the 500 L batch size, and assigns batches to work days. The function never reads `production_plan` itself. As a consequence, every Recompute treats the universe as if no production has yet been planned. If Tom already planned 1 CAL batch for May 4 and runs Recompute, v2 sees the same gross demand, the same zero current stock, and proposes **another** CAL batch on top — the classic "MRP without scheduled receipts" failure mode.

---

## 2. Industry / academic sources surveyed

The "scheduled receipts" concept is one of the most thoroughly settled ideas in operations research. There is no live debate about whether they belong in a net-requirements calculation; the only real choices are about lot sizing on top of a correct net-requirements layer.

| # | Source | Key takeaway for engine v3 |
|---|---|---|
| 1 | **Joseph Orlicky, *Material Requirements Planning*, McGraw-Hill, 1975** (1st ed.); revised by Plossl/Wight, 2nd ed. McGraw-Hill 1995 | Establishes the canonical MRP record (Gross Requirements → Scheduled Receipts → Projected On Hand → Net Requirements → Planned Order Receipts → Planned Order Releases). "Scheduled receipts" = orders that have **already been released** (already-issued POs, already-planned production). Net requirements are computed *after* netting both on-hand and scheduled receipts. |
| 2 | **APICS / ASCM CPIM Body of Knowledge** — Dictionary 16th ed. (2023) and CPIM Part 2 *Detailed Scheduling and Planning* | Defines the six-row MRP record verbatim; defines `Net Requirements = Gross Requirements − Scheduled Receipts − Projected Available Balance(prior period) + Safety Stock` with `max(0, …)`. Lead-time offset rule: Planned Order Release = Planned Order Receipt offset *back* by lead time. ([APICS Exam Warehouse — MRP Mechanics](http://www.apicsexamwarehouse.com/cpim-exams-2/detailed-scheduling-and-planning/mrp-mechanics%E2%80%93the-basics/)) |
| 3 | **Hopp & Spearman, *Factory Physics*, 3rd ed., Waveland 2011, ch. 3 + ch. 5** | Decomposes MRP into "netting → lot sizing → backward scheduling → BOM explosion." Recommends safety stock as a **floor on projected on-hand**, not as a deduction from demand — explicitly warns against "double-counting" safety stock against scheduled receipts. ([Waveland Press](https://www.waveland.com/browse.php?t=587)) |
| 4 | **Wagner & Whitin, "Dynamic Version of the Economic Lot Size Model," *Management Science* 5(1), 1958, pp. 89–96** | Optimal dynamic lot-sizing via DP for deterministic time-varying demand. O(T²) classic, O(T log T) modern. Optimal property: zero-inventory ordering (a lot exactly covers an integer number of future periods). **Not directly applicable here** because Tom's Q is **fixed at 500 L** by the physical tank — there is no order-quantity decision, only an order-timing decision. ([Wikipedia — Dynamic lot-size model](https://en.wikipedia.org/wiki/Dynamic_lot-size_model); [Management Science](https://pubsonline.informs.org/doi/10.1287/mnsc.5.1.89)) |
| 5 | **Silver & Meal, "A Heuristic for Selecting Lot Size Requirements for the Case of a Deterministic Time-Varying Demand Rate and Discrete Opportunities for Replenishment," *Production and Inventory Management Journal*, 1973** | Min-cost-per-period heuristic. Forward-march alternative to W-W. Same fixed-Q caveat — not the right tool for our problem, but useful for understanding **why fixed-Q under-uses small-demand periods** (extra inventory rolls forward). ([Wikipedia — Silver–Meal heuristic](https://en.wikipedia.org/wiki/Silver%E2%80%93Meal_heuristic)) |
| 6 | **Hadley & Whitin, *Analysis of Inventory Systems*, Prentice-Hall 1963 (esp. ch. 4 — "Lot-Size Reorder-Point Models")** | Foundational continuous-review (s, Q): "when inventory position drops to s, order Q." Q fixed by economics (here, by physics). The reorder point s is set to cover demand during lead time + safety stock. ([Hadley & Whitin reference](https://www.scirp.org/(S(i43dyn45teexjx455qlt3d2q))/reference/ReferencesPapers.aspx?ReferenceID=1157422)) |
| 7 | **Steven Nahmias, *Production and Operations Analysis*, 7th/8th ed., Waveland 2015 / 2021, ch. 8 (Push & Pull Production Control: MRP and JIT)** | The canonical undergraduate treatment. Presents a fully worked MRP table with scheduled receipts; explicitly: "scheduled receipts are open orders — orders released before period 1 but not yet delivered." Net requirements = max(0, GR − SR − POH(prev) + SS). ([Production and Operations Analysis archive](https://archive.org/details/productionoperat0000nahm)) |
| 8 | **R. J. Tersine, *Principles of Inventory and Materials Management*, 4th ed., Prentice-Hall 1994, ch. 11** | Applied perspective. Distinguishes `firm planned orders` from `planned orders` — once the planner releases a planned order, it becomes a scheduled receipt and is no longer recomputed by the engine. This is exactly the v2→v3 distinction Tom is asking for. |
| 9 | **SAP S/4HANA — Stock/Requirements List (transaction MD04)** + Oracle EBS MRP user guide | Industry implementation: every ERP MRP engine displays scheduled receipts (planned orders, production orders, purchase orders, schedule lines) **on the same pegged timeline as gross requirements** and nets them in the projected-available-balance column. SAP `Available Quantity` = stock + receipts − requirements, computed period-by-period. ([SAP Help — MD04](https://help.sap.com/docs/SAP_S4HANA_CLOUD/2bba750d1e124e1ea2a039bb1cd9b6c5/daf35d93b67542c0b1f6a18807e9f6e9.html); [erplingo MD04 walk-through](https://www.erplingo.com/sap-transaction-code/en/MD04)) |

**The unanimous verdict from these sources:** every credible MRP implementation, academic or industrial, computes net requirements **after** subtracting scheduled receipts. v2 violates this in our codebase. v3 must fix it.

---

## 3. The standard MRP record format (with example table)

The canonical six-row record, as Orlicky / APICS / Nahmias all present it, looks like this for one item across periods 1..N:

| Row | Period 1 | Period 2 | Period 3 | Period 4 | Period 5 |
|---|---:|---:|---:|---:|---:|
| **Gross Requirements (GR)** | 100 | 100 | 100 | 100 | 100 |
| **Scheduled Receipts (SR)**  *(already-released supply)* | 0 | 200 | 0 | 0 | 0 |
| **Projected On-Hand (POH)** *(end-of-period)* | 50 | 150 | 50 | -50 → 450 | 350 |
| **Net Requirements (NR)** *(= max(0, GR − SR − POH(prev) + SS))* | 0 | 0 | 0 | 50 | 0 |
| **Planned Order Receipts (POR)** *(lot-sized)* | 0 | 0 | 0 | 500 | 0 |
| **Planned Order Releases (PORL)** *(POR offset by lead time L=1)* | 0 | 0 | 500 | 0 | 0 |

Walk-through (POH start = 150, SS = 0, lot size Q = 500, lead time L = 1):
- P1: 150 + 0 − 100 = 50. NR = 0.
- P2: 50 + 200 − 100 = 150. NR = 0. (The scheduled receipt of 200 in P2 prevents NR firing.)
- P3: 150 + 0 − 100 = 50. NR = 0.
- P4: 50 + 0 − 100 = −50 → trigger NR = 50; POR = 500 (rounded up to Q); POH ends at 450.
- P5: 450 + 0 − 100 = 350. NR = 0.
- PORL: place the P4 receipt one period earlier, in P3.

**Two properties carry over to engine v3:**
1. The scheduled receipt of 200 in P2 is what stops MRP from ordering again. Without it, P2 NR would have been 50 and the engine would have planned a second 500-unit lot. **This is exactly Tom's bug.**
2. The lead-time offset (lot lands one period after release) maps directly to GT Factory OS's "production day → bottle-available day" lag of +1 day.

---

## 4. Three candidate algorithm variants (A / B / C)

### Variant A — Strict daily MRP

- **Time bucket:** 1 day. Horizon: 56 days (matches `v_daily_inventory_projection`).
- **Per base, per day:** compute `gross_requirements[d]`, `scheduled_receipts[d]`, `projected_on_hand[d]`, `net_requirement[d]`, `planned_order_receipt[d]`, `planned_order_release[d]`.
- **Lot sizing:** when `projected_on_hand[d] < safety_stock_l`, schedule one 500 L batch. Lead time L = 1 day, so the planned order **release** date = need date − 1, restricted to a work day. The new receipt is added to `scheduled_receipts[d]` and the projection forward of `d` is recomputed in the same sweep.
- **Pros:** matches the data shape we already have (`v_daily_inventory_projection` is daily); matches Tom's spec §3 verbatim; matches SAP / Oracle MRP day-bucket implementations; no information loss.
- **Cons:** more rows in the temp table; subtle handling needed for non-work-day stockouts (must release earlier). Pure SQL is feasible but a CTE chain is bigger.

### Variant B — Weekly bucket MRP with daily disaggregation at the end

- Compute net requirements at weekly granularity (matches v2's existing structure), then disaggregate batches across the work days of the chosen week.
- **Pros:** smallest delta from v2; reuses the weekly proposal envelope; simpler SQL.
- **Cons:** **Information loss.** A weekly bucket smears the timing of stockouts. For example, a stockout on Sunday vs. Wednesday has very different release-date implications under L=1. With Tom's daily-paced operation and 1-batch/day capacity, weekly buckets will systematically under-schedule when demand spikes early in a week. This is the textbook reason Hopp & Spearman recommend the smallest meaningful bucket.

### Variant C — Continuous-review (s, Q) policy

- Set s_base = SAFETY_DAYS × avg_daily_demand_l. When inventory_position (= on-hand + scheduled receipts) drops below s, fire a 500 L batch.
- **Pros:** tiny code (single trigger expression). Robust to noisy daily demand because it pegs to position, not point-in-time projection.
- **Cons:** time-varying deterministic demand violates the (s, Q) stationarity assumption (Hadley & Whitin 1963 §4 caveat). Loses the explicit per-day stockout-prediction surface that Tom's UI already uses (the v_daily_inventory_projection bands). And the (s, Q) policy decides **whether** to fire today; it does not by itself answer "which work day in the week." We'd still need a daily projection to schedule.

### Why not Wagner-Whitin or Silver-Meal?

Both are **lot-sizing optimizers** — they decide how many periods of demand to bundle into one order, trading setup cost vs. holding cost. **In our problem, Q is fixed at 500 L by the tank** (Tom's spec §3.4: "Each batch is always 500 L"). There is no "how big should the lot be" decision left, and therefore no setup-vs-holding trade-off to optimize. Wagner-Whitin and Silver-Meal would be the right tool if Tom were deciding lot size; he is not. They remain useful framing for a future v4 (e.g., "should we do a half-tank batch when net requirement is small and the next demand is far away?") but are out of scope here.

---

## 5. Recommended variant + why

**Recommend Variant A — strict daily MRP at 56-day horizon, applied per base.**

Reasons:
1. **Tom's data shape is daily.** The portal already renders a daily calendar grid; `v_daily_inventory_projection` is already daily. Anything coarser than daily would lose information that the rest of the system has.
2. **The +1 production lag is a daily quantity.** A weekly bucket can't represent it without conventions that hide the bug we're trying to fix.
3. **Capacity is daily.** `max_batches_per_day` is the binding constraint, not `max_batches_per_week`. A daily projection lets us see capacity-overflow days directly — the same engine emits the `CAPACITY_OVERFLOW` exception on the right day.
4. **Industry standard.** SAP MD04 and Oracle MRP both run at daily (or even shift-level) granularity. None ship "weekly MRP" as the production model — they aggregate to weekly only for display.
5. **Migration delta is small.** v2 already computes per-base liters and assigns to work days. v3 inserts a per-base daily projection CTE and changes the trigger from "demand > 0" to "projected_on_hand < safety_stock". Rest of the structure (the per-day cursor walk, the row insert into `production_plan`, the `consumed_by_proposal_id` marking) is unchanged.
6. **Defensibility.** Tom asked for the world's most authoritative sources. Variant A is what those sources describe. Variants B and C are simplifications that would require justification *against* the canonical model; Variant A *is* the canonical model.

**Net:** Variant A is the only variant that simultaneously (a) preserves v2's surface contract (one proposal_id, base-batch shape, draft status) and (b) closes the scheduled-receipts bug without introducing a second approximation.

---

## 6. Worked example — live CAL data, 2026-05-04

Pulled live from Supabase (`scripts/_v3_research_cal_extract.mjs`, 2026-05-04). Base = `BOM-BASE-CAL-REG`. The 4 CAL FGs (FG-CAL-1L, FG-CAL-1L-NS, FG-CAL-500ML, FG-CAL-500ML-NS) all have `on_hand = 0` units in `current_balances` today; total CAL stock in liters = **0 L**.

Demand horizon (next 14 days, all CAL FGs combined, in liters; weekly buckets spread evenly across 7 days, matching `v_daily_inventory_projection` logic):

| Day | DOW | Forecast (L) | Open orders (L) | Total demand (L) |
|---|---|---:|---:|---:|
| Sun May 3 | 0 | 10.5 | 21.9 | 32.3 |
| Mon May 4 | 1 | 10.5 | 21.9 | 32.3 |
| Tue May 5 | 2 | 10.5 | 21.9 | 32.3 |
| Wed May 6 | 3 | 10.5 | 21.9 | 32.3 |
| Thu May 7 | 4 | 10.5 | 21.9 | 32.3 |
| Fri May 8 | 5 | 10.5 | 21.9 | 32.3 |
| Sat May 9 | 6 | 10.5 | 21.9 | 32.3 |
| Sun May 10 | 0 | 10.5 | 0    | 10.5 |
| Mon May 11 | 1 | 10.5 | 0    | 10.5 |
| ...     |...| 10.5 | 0    | 10.5 |
| Sat May 16 | 6 | 10.5 | 0    | 10.5 |

(Open orders are A3-locked to the current ISO week per migration 0099, hence the May 10 cliff. Forecast is a flat monthly disaggregation.)

Currently scheduled production (`production_plan` rows in draft / planned / in_production):

| plan_id | plan_date | batch_size_l | status |
|---|---|---:|---|
| 24c79d42… | Mon May 4, 2026 | 500 | draft |

Policy (live `planning_policy`):
- `batch_size_l` = 500
- `safety_days_per_base` = 5
- `work_days_of_week` = `{0,1,2,3,4}` (Sun–Thu)
- `max_batches_per_day` = 1

### 6a. Safety stock floor

```
avg_daily_demand_first_7d = 32.3 L/day
s_base = 5 × 32.3 = 161.6 L
```

(One could argue for the blended average across the full 14-day window — ~21 L/day — which gives s ≈ 105 L. Either way the conclusion below is the same; the doc uses the conservative 162 L.)

### 6b. v3 daily MRP record for CAL (Variant A)

Lead time L = 1 day; the May 4 batch's release date is May 4, its receipt date is May 5.

| Day | GR (L) | SR (L) | POH end (L) | NR (L) | POR (L) | PORL (L) |
|---|---:|---:|---:|---:|---:|---:|
| Sun May 3 | 32.3 | 0 | -32.3 → already short* | n/a* | 0 | 0 |
| Mon May 4 | 32.3 | 0   | -64.6 | already short* | 0 | 0 |
| Tue May 5 | 32.3 | **500** | 403.1 | 0 | 0 | 0 |
| Wed May 6 | 32.3 | 0 | 370.8 | 0 | 0 | 0 |
| Thu May 7 | 32.3 | 0 | 338.5 | 0 | 0 | 0 |
| Fri May 8 | 32.3 | 0 | 306.2 | 0 (non-work day) | 0 | 0 |
| Sat May 9 | 32.3 | 0 | 273.8 | 0 (non-work day) | 0 | 0 |
| Sun May 10 | 10.5 | 0 | 263.3 | 0 | 0 | 0 |
| Mon May 11 | 10.5 | 0 | 252.8 | 0 | 0 | 0 |
| Tue May 12 | 10.5 | 0 | 242.4 | 0 | 0 | 0 |
| Wed May 13 | 10.5 | 0 | 231.9 | 0 | 0 | 0 |
| Thu May 14 | 10.5 | 0 | 221.4 | 0 | 0 | 0 |
| Fri May 15 | 10.5 | 0 | 211.0 | 0 | 0 | 0 |
| Sat May 16 | 10.5 | 0 | 200.5 | 0 | 0 | 0 |

\* The May 3–4 deficit pre-dates this Recompute and is **not** corrected by adding more batches in this run — the May 4 batch was the corrective action and the receipt landing on May 5 is the earliest possible relief under L=1. v3 should emit a `historical_shortage` exception for these days but not propose retro-active batches. (See edge case §8.A.)

**v3 conclusion:** projected on-hand stays above the 162 L safety floor through the entire 14-day window. **Net requirement = 0 every day. v3 emits zero new CAL batches on Recompute.**

### 6c. v2 behaviour on the same Recompute (the bug)

v2's logic: gross liters demanded summed across CAL FGs over the proposal week's recommendations, minus current stock (0 L), divided by 500 L = 1 batch (rounded up from any positive number). v2 has no awareness of the May 4 batch sitting in `production_plan`. **v2 emits 1 new CAL batch — duplicate.**

### 6d. The contrast

| | v2 (current) | v3 (proposed) |
|---|---|---|
| Reads `production_plan` scheduled receipts? | No | Yes (status ∈ {draft, planned, in_production}) |
| Reads `production_actual` already-completed batches? | No (correctly, they're in current_balances) | No (same; double-count avoided) |
| Time bucket | week-implicit | day, 56-day horizon |
| Lead time | not modeled | +1 day, work-day-aware |
| Safety stock | implicit (via demand padding) | explicit floor on POH |
| Result for CAL today (May 4, 1 batch already scheduled) | proposes a second 500 L batch | proposes nothing |

---

## 7. Algorithm specification (pseudocode + SQL outline)

### 7a. High-level pseudocode

```
input:  p_week_start date, p_actor uuid
output: proposal_id uuid

1. snapshot actor (unchanged from v2)
2. read planning_policy keys (unchanged from v2)
3. log engine_missing_base_metadata exceptions (unchanged from v2)

4. for each base B with at least one approved-unconsumed production rec:
     read current_stock_l[B]                                  -- from current_balances × base_fill_qty_per_unit
     read demand_l[B][d] for d in [today, today+55]            -- from v_planning_demand spread across 7 days
     read scheduled_receipts_l[B][d+1] for each row in
         production_plan WHERE base_bom_head_id=B
                           AND status IN ('draft','planned','in_production')
                           AND plan_date >= today              -- the +1 lag: receipt lands plan_date+1
     poh[B][today-1] := current_stock_l[B]
     for d in [today, today+55]:
         poh[B][d] := poh[B][d-1] + scheduled_receipts_l[B][d] - demand_l[B][d]

5. sweep days forward in [p_week_start, p_week_start+6]:
     for each base B (priority = earliest day where poh < s_base):
         find earliest "need date" d* = first day in horizon where poh[B][d*] < s_base[B]
         if d* exists and d* > today:
             release_date := d* - 1
             walk release_date back to nearest work day if needed (Sun-Thu); if not within p_week_start..p_week_end → CAPACITY_OVERFLOW exception
             check max_batches_per_day for release_date; if full → next available work day before d* (else overflow)
             insert one production_plan row (base-batch shape, 500 L, draft, proposal_id=v_proposal)
             scheduled_receipts_l[B][release_date+1] += 500
             recompute poh[B][d] for all d ≥ release_date+1
             repeat for the same base if poh again drops below s_base later in the window

6. mark consumed recommendations (unchanged from v2)

7. return v_proposal
```

### 7b. SQL outline (for reference only — NOT for implementation in this dispatch)

The function shape stays plpgsql + temp tables. The new ingredients are:

```
-- New CTE 1: scheduled receipts per (base, day)
WITH scheduled_receipts AS (
  SELECT pp.base_bom_head_id,
         (pp.plan_date + 1) AS receipt_day,    -- +1 production lag
         SUM(pp.batch_size_l) AS receipt_l
    FROM private_core.production_plan pp
   WHERE pp.base_bom_head_id IS NOT NULL
     AND pp.status IN ('draft','planned','in_production')
     AND pp.plan_date >= CURRENT_DATE
   GROUP BY pp.base_bom_head_id, pp.plan_date + 1
),

-- New CTE 2: demand per (base, day) over 56-day horizon
demand_by_day AS (
  SELECT i.base_bom_head_id,
         vpd.period_bucket_key + (gs - 1) AS demand_day,
         SUM(vpd.demand_qty * COALESCE(i.base_fill_qty_per_unit, 0) / 7.0) AS demand_l
    FROM api_read.v_planning_demand vpd
    JOIN private_core.items i ON i.item_id = vpd.item_id
    CROSS JOIN generate_series(1, 7) gs
   WHERE i.base_bom_head_id IS NOT NULL
   GROUP BY i.base_bom_head_id, vpd.period_bucket_key + (gs - 1)
),

-- New CTE 3: per-base avg daily demand for safety_stock_l
avg_demand AS (
  SELECT base_bom_head_id,
         AVG(demand_l) FILTER (WHERE demand_day BETWEEN CURRENT_DATE AND CURRENT_DATE + 13) AS avg_d_l
    FROM demand_by_day
   GROUP BY base_bom_head_id
)
```

The plpgsql body then walks days forward per base, accumulating `poh` in a local array, firing batches when `poh[d] < s_base`, and adjusting subsequent `scheduled_receipts` entries for the new batch.

This can also be written in a single recursive CTE, but the plpgsql loop is more debuggable and matches v2's existing structure.

---

## 8. Edge cases + exception handling

### A. Historical shortage (POH already negative on day 0)

If a base's `poh[today]` is already negative (today's stock + today's scheduled receipts can't cover today's demand), v3 must **not** retroactively schedule a batch for yesterday. Instead, emit a new exception category `historical_shortage_at_proposal_open` and continue the projection from `max(0, poh[today])` for the rest of the sweep. This mirrors APICS Dictionary "exception 10 / 15" rescheduling semantics — the system flags the operator to act, it does not invent a time machine.

### B. Receipt lands on a non-work day

`scheduled_receipts` are timestamped by **receipt date** (= plan_date + 1), not by production date. A Thursday batch lands Friday (a non-work day in our calendar). The Friday receipt is real — bottles arrive Friday morning. This is fine; non-work days in `work_days_of_week` are *production* constraints, not *availability* constraints.

### C. Cancelled or moved planned batches between two Recomputes

If Tom cancels a planned batch (`status` → `cancelled`), the v3 query filter `status IN ('draft','planned','in_production')` automatically drops it from `scheduled_receipts`. The next Recompute sees the gap and fills it. If Tom moves a batch to a different `plan_date`, same thing — the old date drops out, the new date drops in.

### D. `production_actual` rows must NOT be added to scheduled_receipts

`production_actual` posts a `production_completion` event into `stock_ledger` via the BOM-explosion handler (`fn_explode_bom_to_components_v2`). That event is reflected in `current_balances` via the projection trigger. If v3 also added the corresponding `production_plan` row (now `status='completed'`) into `scheduled_receipts`, it would double-count. The status filter `IN ('draft','planned','in_production')` excludes `completed` and `cancelled` for exactly this reason. **This is the load-bearing invariant.** A test should pin this.

### E. Capacity overflow

If the priority-queue sweep cannot fit all required releases into work days within the proposal week (or pushes a needed release outside the work-day calendar), v3 emits a `capacity_overflow` exception per affected (base, week) pair (already a recognized category from spec §3.7). The unfilled net requirement is deferred to next week's Recompute, which sees the same gap and tries again under the next week's capacity.

### F. Concurrency between two simultaneous Recomputes

v2 already uses `proposal_id` as the unit of atomicity. v3 inherits this. A unique `idempotency_key` per inserted row already guarantees no double-insert under retry. No new concurrency surface.

### G. Items lacking `base_fill_qty_per_unit`

Already handled by v2's exception logger (`engine_missing_base_metadata`). v3 inherits this guard before the projection step.

### H. Stockout deeper into the horizon than the proposal window

If the projection shows a stockout in week 3 of an 8-week horizon, v3 still **only schedules into the proposal week** (`p_week_start..p_week_start+6`) — the rest is left for future weekly Recomputes. This matches Tom's existing operational rhythm ("review system recommendations weekly") and avoids the engine over-committing future capacity that may be re-planned. The 56-day horizon is a *visibility* horizon, not a *commitment* horizon.

---

## 9. Migration path from v2 to v3

A single migration `0141_fn_propose_weekly_production_plan_v3.sql` is sufficient:

1. `CREATE OR REPLACE FUNCTION private_core.fn_propose_weekly_production_plan(date, uuid) RETURNS uuid` — preserves the public signature; no API or portal change required.
2. New temp tables inside the function: `_demand_by_day`, `_scheduled_receipts`, `_projection`. Same `ON COMMIT DROP` + `DROP TABLE IF EXISTS` discipline as v2 (see migration 0140 lines 137–141).
3. INSERT INTO `production_plan` retains the base-batch shape (item_id NULL, uom 'L', planned_qty = 500, pack_manifest non-empty) — v2's compliance with the 0139 CHECK constraint is preserved verbatim.
4. New `planning_run_exceptions` category: `historical_shortage_at_proposal_open` (warning severity). Adds to the category enum check (similar one-liner to migration 0100 / 0106 / 0137 pattern).
5. Tests: extend `db/tests/0140_fn_propose_weekly_production_plan_v2.test.sql` with three new pgTAP cases:
   - **idempotency-of-recompute:** seed 1 planned CAL batch, run propose twice → second run inserts 0 new rows.
   - **scheduled-receipt-respected:** seed (current_stock=0, planned_batch=1, demand=200 L over 14 days) → propose returns 0 new rows.
   - **scheduled-receipt-removed-on-cancel:** start as above, then cancel the planned batch, run propose → returns 1 new row.
6. Rollback: re-apply migration 0140 verbatim (CREATE OR REPLACE).

**No breaking change to** API surface, portal, `production_plan` schema, `planning_policy` schema, or any other function. The change is local to one plpgsql function plus one exception-category CHECK.

---

## 10. Open questions for Tom

1. **Safety-stock denominator.** Should `s_base = SAFETY_DAYS × avg_daily_demand` use (a) the next 7 days, (b) the next 14 days, (c) the full 56-day horizon, or (d) a fixed liters number per base in `planning_policy`? My recommendation is **(d)** — daily demand swings (open-orders cliff at end of current ISO week is a clear example) make running averages noisy, and a per-base policy value is the simplest planner-tunable control. But this is a real choice and worth Tom's call.

2. **Horizon for the projection.** 56 days matches the existing `v_daily_inventory_projection`. Should v3's projection look further (e.g., 84 days, matching the spec's 8-week mention) so it can pre-warn about slow-moving bases? Cost: 50% more rows in the temp table; not material at scale.

3. **What to do when `poh[today]` is already negative.** Recommendation in §8.A is to flag and continue. Tom may prefer an alternative: refuse to propose anything for that base until someone clears the historical shortage exception. Either is defensible; the recommended approach is more "auto-pilot keeps going, surfaces the alarm" and matches Tom's preference (per `feedback_blockers_scale_plus_urgency`) to expose both scale and urgency.

4. **Does v3's daily MRP need to honor IL holidays?** Migration 0092 / 0119 / 0120 manage `holidays_il`. v2 today honors only `work_days_of_week` (DOW filter). For v3 we *can* skip holidays as production days easily; demand on a holiday is already handled by the demand spread (forecast doesn't care; orders for that day are real). My read of the spec: yes, v3 should skip IL holidays as production days (consistent with the current capacity model). Worth confirming.

5. **Multi-base batching same day.** `max_batches_per_day = 1` today. If two bases both need a batch on the same earliest work day, v2's deterministic tiebreaker is `ORDER BY earliest_shortage NULLS LAST, base_bom_head_id`. v3 keeps this. Is this still what Tom wants, or should the tiebreaker include "highest projected stockout severity" or similar?

---

**End of v3 design.**
