# Daily Production Plan — Design Spec

**Date:** 2026-05-03
**Status:** Approved by Tom (brainstorming session 2026-05-03), pending implementation
**Authors:** Tom (product owner) + Claude (synthesis)
**Scope:** End-to-end redesign of the production planning + reporting flow
**Touches:** schema (private_core), API (`gt-factory-os/api`), portal (`window2-portal-sandbox`)

---

## 1. Problem Statement

The existing `/planning/production-plan` page is conceptually wrong for how Tom actually runs the factory.

**Current behavior (broken):**
1. Engine emits hundreds of per-FG production recommendations (365 in latest run).
2. Recommendations are duplicated per item (FG-DET-1L appears 6 times across weekly buckets).
3. Tom must approve each rec individually, then click "Add from Recommendations" per rec, then assign a day.
4. No visibility into total weekly capacity vs demand.
5. No grouping by what is actually produced (a base, not a finished good).

**What Tom actually does:**
- Produces ONE base liquid (e.g., DETOX) at a time.
- That base is packed into multiple finished-good variants (1L, 0.5L, sugar-free, etc.).
- One base per production day by default; Tom can override.
- Maximum 500 L per batch (physical tank constraint).
- Reviews system recommendations weekly and applies "final tuning" — moves days, swaps bases, changes pack quantities.

**Goals:**
1. Replace the per-FG recommendation list with a base-grouped weekly schedule.
2. Engine proposes the schedule; Tom edits and approves.
3. Production Actual auto-fills from the day's plan.
4. Algorithm guarantees: full 500 L batches AND zero stock-outs (forward-projected).

---

## 2. Concept Model — "Base Batch"

The unit of production planning becomes a **Base Batch**: one 500 L production of a specific base on a specific day, with a manifest of finished-good packs that come out of it.

### 2.1 Data shape (one row per `production_plan` record)

| Field | Type | Source | Notes |
|---|---|---|---|
| `plan_id` | uuid | system | PK |
| `plan_date` | date | system / Tom | Production day |
| `base_bom_head_id` | text | system / Tom | NEW column — first-class link to the BASE BOM head |
| `bom_version_id_pinned` | uuid | system | Pinned BASE version at proposal time |
| `batch_size_l` | numeric | policy | Default 500; from `planning_policy.batch_size_l` |
| `pack_manifest` | jsonb | system / Tom | NEW column — `[{item_id, qty}, ...]` |
| `linked_recommendation_ids` | uuid[] | system | NEW column — recs that fed this batch |
| `proposal_id` | uuid | system | NEW column — groups all batches from one Recompute call |
| `is_user_modified` | boolean | system | NEW column — true after any user edit |
| `status` | text | system / Tom | draft / planned / in_production / completed / cancelled |
| `notes` | text | Tom | Freeform |
| `idempotency_key` | text | system | Existing |
| `created_by_user_id` / `_snapshot` | uuid / text | system | Existing |
| `updated_by_user_id` / `_snapshot` | uuid / text | system | Existing |
| `cancelled_at` / `_by_user_id` / `cancel_reason` | various | Tom | Existing |
| `completed_submission_id` | uuid | system | Existing — link to first Production Actual |
| `created_at` / `updated_at` | timestamptz | system | Existing |

### 2.2 Item exclusions

| supply_method | In production plan? | How |
|---|---|---|
| `MANUFACTURED` (with `base_bom_head_id`) | Yes — base-batch flow | Calendar grid |
| `MANUFACTURED` (no base — pure pack/assembly) | Yes — simpler | Card without "500 L" — shows "1 production run" |
| `REPACK` (e.g., FG-MAT-30G) | Yes — different unit | Phase 2 — separate visual; uses input-component qty, not 500 L cap |
| `BOUGHT_FINISHED` | No | Lives in Purchase Orders flow |

---

## 3. Engine Policy — Smart Proposal

### 3.1 Two competing goals

- **Goal A — Efficiency:** Every batch is full (500 L). Never produce 200 L when we could produce 500 L.
- **Goal B — No stock-out:** Projected daily stock stays positive for every FG.

Resolved with a **(s, Q) reorder-point policy with daily forward projection**, fixed Q = 500 L, anchored to MRP-style net requirements.

### 3.2 Daily projection per base (8-week horizon)

```
projected_liters[base, day] =
    current_stock_in_liters
  + scheduled_production_landing_on_or_before(day)
  - sum_of_daily_demand_in_liters_through(day)

daily_demand_in_liters = SUM over all FGs sharing the base of:
       (forecast_per_day + open_orders_per_day) × items.base_fill_qty_per_unit
```

The monthly forecast is disaggregated to daily run-rate (existing migration 0128 logic, extended).

### 3.3 Reorder Point per base

```
s_base = SAFETY_DAYS × avg_daily_demand_liters
```

`SAFETY_DAYS` is per-base in `planning_policy` (default 5; override per criticality).

### 3.4 Fire-a-batch rule (fixed Q = 500 L)

```
For each base, sweep days forward through the 8-week horizon:

  for day in horizon:
      proj = projected_liters[base, day]
      if proj < s_base:
          fire_day = first available production slot ≤ (day - 1)
          schedule_batch(base, fire_day, 500L)
          for subsequent_day in [fire_day .. horizon_end]:
              projected_liters[base, subsequent_day] += 500L
```

Each batch is always 500 L. A batch fires only when projection drops below the reorder point.

### 3.5 Multi-base scheduling under capacity

```
capacity_per_week = WORK_DAYS_COUNT × MAX_BATCHES_PER_DAY_DEFAULT
                    (default = 5 days × 1 batch = 5 batches/week)

Build priority queue: bases with earliest must_fire_by_day first.
Walk production days; pop most-urgent base whose deadline ≥ day; assign 500 L batch.
After scheduling, leftover unfilled deadlines raise a CAPACITY_OVERFLOW exception.
```

### 3.6 Per-batch pack distribution

For each scheduled batch B at day D, fill its 500 L greedily by FG urgency:

```
For each FG sharing B's base:
    remaining_demand[fg] = SUM(forecast + orders) from D onward
                          minus already-allocated qty in earlier batches
Pack B's 500 L greedily, earliest-shortage FG first, until 500 L is full
or no remaining demand.
```

### 3.7 Capacity overflow surfacing

When demand exceeds capacity, the system raises a typed exception (does NOT silently produce excess):

```
⚠️ CAPACITY_OVERFLOW
   base: DETOX
   deficit: 3 batches (1500 L) over weeks 1-2
   projected stockout dates if not produced:
     FG-DET-1L:    May 9   (will hit -200u)
     FG-DET-500ML: May 12  (will hit -50u)
   options:
     A) Boost capacity: 2 batches/day for 3 days (Tom override)
     B) Accept partial stockout (system recommends FG prioritization)
     C) Defer some FG variants (skip 0.5 L this round)
```

### 3.8 Provenance

Algorithm rooted in standard Operations Research:
- MRP (Orlicky 1975) — net-requirements logic, time-phased planning
- (s, Q) policy (Hadley & Whitin 1963) — fixed-quantity reorder-point
- Wagner-Whitin (1958) — optimal lot-sizing for deterministic demand (we use the simpler ROP heuristic since Q is fixed)
- Silver-Meal (1973) — varying-demand heuristic
- MRP II / S&OP — capacity-planning layer for multi-base scheduling
- Lean / TPS heijunka — preference for level loading across days

---

## 4. UI — Calendar Week Grid

### 4.1 Page header

```
Daily Production Plan
Week of May 4-10, 2026                ⏪ Previous Week | This Week | Next Week ⏩

📊 5 bases · 8 batches · 4,000 L · ⏱ Updated 13:42 by Tom

[♻️ Recompute] [💾 Save] [📤 Send to Operators] [⋯ More]
```

### 4.2 Calendar grid (5 work days)

```
┌──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
│   Sun May 4  │   Mon May 5  │   Tue May 6  │   Wed May 7  │   Thu May 8  │
├──────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ ╔══════════╗ │ ╔══════════╗ │ ╔══════════╗ │              │ ╔══════════╗ │
│ ║ DETOX    ║ │ ║ DETOX    ║ │ ║ FRESH    ║ │  (no batch)  │ ║ NAMASTEA ║ │
│ ║ 1×500 L  ║ │ ║ 1×500 L  ║ │ ║ 1×500 L  ║ │              │ ║ 2×500 L  ║ │
│ ║          ║ │ ║          ║ │ ║          ║ │ [+ Add       │ ║          ║ │
│ ║ Pack as: ║ │ ║ Pack as: ║ │ ║ Pack as: ║ │   batch]     │ ║ Pack as: ║ │
│ ║ 1L: 500u ║ │ ║ 1L: 250u ║ │ ║ 1L: 727u ║ │              │ ║ 1L: 709u ║ │
│ ║ 0.5L: 0  ║ │ ║ 0.5L:310 ║ │ ║ NS-1L:88 ║ │              │ ║ 0.5L:390 ║ │
│ ║          ║ │ ║          ║ │ ║          ║ │              │ ╚══════════╝ │
│ ║⚠ Shortage║ │              │              │              │              │
│ ║   May 4  ║ │              │              │              │              │
│ ╚══════════╝ │ ╚══════════╝ │ ╚══════════╝ │              │ [+ Add batch]│
│              │              │              │              │              │
│ [+ Add batch]│ [+ Add batch]│ [+ Add batch]│              │              │
└──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
```

**Display rules:**
1. Each batch = one mini card (500 L). Same-base same-day batches collapse to a "×N" pill.
2. Bases share a color across all days for at-a-glance "which days are DETOX."
3. Empty days show only the "+ Add batch" affordance.
4. Shortage warnings appear on the card when the engine's projection shows a stockout risk before production day.

### 4.3 Empty / loaded / locked states

| State | Display |
|---|---|
| Empty (before any planning) | Centered: "No production planned for this week. [♻️ Recompute] or [+ Add Manually]" |
| Loaded | Calendar grid as above |
| Locked (status `planned`+) | Read-only with "PLANNED" / "IN PRODUCTION" / "COMPLETED" badge per card; edit requires unlock confirmation |

### 4.4 Capacity overflow banner

Rendered above the grid when the engine raises `CAPACITY_OVERFLOW`:

```
⚠️ 23 batches deferred to weeks of May 10-31 due to capacity (5 batches/week).
   Top deferred bases: DETOX (16), NAMASTEA (4), FRESH (2).
   [Open 8-week view →]
```

`Open 8-week view` opens a wider read-only timeline so Tom can see how deferred work spreads. From there he can boost `MAX_BATCHES_PER_DAY` for selected weeks (planning override) or accept the spread.

---

## 5. Interactions

### 5.1 Click a batch card → Side drawer

```
                                    ┌──────────────────────────────────────┐
[grid behind, dimmed]               │  ✕ Close                             │
                                    │                                      │
                                    │  🟢 DETOX BASE                       │
                                    │  Sun May 4, 2026 · Batch 1 of 1     │
                                    │                                      │
                                    │  ──── Batch composition (500 L) ──── │
                                    │                                      │
                                    │  Final packs:                        │
                                    │  ┌────────────────────────────────┐  │
                                    │  │ DETOX 1L (FG-DET-1L)           │  │
                                    │  │   Qty: [_500_]                 │  │
                                    │  ├────────────────────────────────┤  │
                                    │  │ DETOX 0.5L (FG-DET-500ML)      │  │
                                    │  │   Qty: [_0_]                   │  │
                                    │  ├────────────────────────────────┤  │
                                    │  │ DETOX 1L NS (FG-DET-1L-NS)     │  │
                                    │  │   Qty: [_0_]                   │  │
                                    │  └────────────────────────────────┘  │
                                    │  [+ Add pack]                        │
                                    │  ✓ Total: 500 L (of 500 L max)       │
                                    │                                      │
                                    │  ──── Required components ────────── │
                                    │  RAW-LUI         X.X kg              │
                                    │  RAW-WATER       Y.Y L               │
                                    │  PKG-BOTTLE-1L   500 units           │
                                    │  PKG-LABEL-DET   500 units           │
                                    │  ⚠️ PKG-CAP short in stock           │
                                    │                                      │
                                    │  ──── Recommendation source ──────── │
                                    │  Merged from 3 recommendations:      │
                                    │  • rec #4f08 — qty 2352              │
                                    │  • rec #49a6 — qty 2352              │
                                    │  • rec #2af8 — qty 1962              │
                                    │  shortage_date: May 4 (today)        │
                                    │                                      │
                                    │  ──── Notes ──────────────────────── │
                                    │  [_____________________________]     │
                                    │                                      │
                                    │  [💾 Save] [🗑️ Remove batch]         │
                                    └──────────────────────────────────────┘
```

**Drawer interactions:**
- Pack quantities are editable inline. Each change updates "Total L" in real time.
- If total > 500 L → red warning: "Exceeds 500 L. Split batch or reduce qty."
- "+ Add pack" → dropdown of FGs sharing the same `base_bom_head_id`.
- "Remove batch" → confirmation: "Return linked recommendations to bank?"

### 5.2 Drag-and-drop between days

- Long-press + drag a card to a different day's column.
- Drop zones highlight blue during drag.
- Warning fires if move would cause shortage:
  > "DETOX must be in stock by May 4. Moving to May 7 will cause projected stockout of 200 units."
  > [Cancel] [Override anyway]
- Cross-week drag → "Save and move to next week's plan?"

### 5.3 "+ Add batch" picker

```
┌─────────────────────────────────────────────────────────┐
│  Add batch to Sun May 4                            ✕    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ── From recommendations (3 available) ──────────────   │
│  ◯ FRESH        800 L needed (1.6 batches)             │
│    shortage: May 5                                      │
│  ◯ NAMASTEA     1,100 L needed (2.2 batches)           │
│    shortage: May 6                                      │
│  ◯ SANGRIA RED  400 L needed (0.8 batches)             │
│    shortage: May 7                                      │
│                                                         │
│  ── Add manually ────────────────────────────────────   │
│  ◯ Pick base from master... [dropdown]                 │
│                                                         │
│  [Cancel]                              [+ Add to day]  │
└─────────────────────────────────────────────────────────┘
```

Primary suggestions = bases not yet scheduled this week (from approved recs). Manual = break-glass for un-recommended bases.

### 5.4 Bulk tools (above grid)

- 🎨 **Group by base** — toggle: each card separate / collapse same-base same-day to ×N
- ⏰ **Sort by urgency** — within each day, sort cards by `shortage_date`
- 👁️ **Hide empty days** — compact view
- 📋 **Copy week** — clone current week's plan to next as baseline for editing

### 5.5 Save & lifecycle

Two save tiers:
1. **💾 Save** — persists edits as `production_plan` rows with `status='draft'`. Tom-only visibility.
2. **📤 Send to Operators** — transitions to `status='planned'`. Appears on Daily Production Report (Section 6) and operator dashboard. Email/notification fires.

### 5.6 Optimistic UI + concurrency

- Edits save optimistically with minimal indicator ("Saving... ✓").
- Concurrent edits use `expected_updated_at` optimistic locking.
- 409 → "Adi changed this batch 2 minutes ago. [Reload] [Override]"

---

## 6. Production Actual — Daily Auto-fill from Plan

### 6.1 Concept

The `/production-actual` page becomes a **Daily Production Report** that auto-fills quantities from the day's planned batches. Tom edits where reality differs and submits all FGs at once.

### 6.2 Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  Production Actual — Daily Report                                    │
│  Sun May 4, 2026  ⏪ Previous | Today | Next ⏩                       │
│                                                                      │
│  📊 Planned: 1 base · 1 batch · 500 L                                │
│  📊 Reported so far: 0 / 3 FGs                                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  🟢 DETOX BASE — batch 1 of 1 (500 L planned)                        │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ DETOX 1L (FG-DET-1L)                                           │ │
│  │   Planned: 500u   Actual: [_500_]u   Scrap: [_0_]u             │ │
│  │   ✓ Matches plan      BOM v.7   Notes: [_____________]         │ │
│  ├────────────────────────────────────────────────────────────────┤ │
│  │ DETOX 0.5L (FG-DET-500ML)                                      │ │
│  │   Planned: 0u     Actual: [_0_]u     Scrap: [_0_]u             │ │
│  │   ⏸️ Not in plan today                                          │ │
│  ├────────────────────────────────────────────────────────────────┤ │
│  │ DETOX 1L NS (FG-DET-1L-NS)                                     │ │
│  │   Planned: 0u     Actual: [_0_]u     Scrap: [_0_]u             │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  📐 Liters consumed: 500 L (with current values) ✓ matches 500 L    │
│  ⚠️ If you report 600u of FG-DET-1L → 600 L > 500 L planned          │
│     (would require an extra batch)                                   │
│                                                                      │
│  [+ Add unplanned FG] [+ Report unplanned batch]                    │
└─────────────────────────────────────────────────────────────────────┘

[💾 Save draft]                      [📥 Submit all]
```

### 6.3 Behavior

- **Pre-fill from plan:** On open, query `production_plan` for `plan_date = selected_day`. Populate "Actual" with planned qty, "Scrap" with 0.
- **Inline edits:** Each change updates "Liters consumed" with green/yellow/red indicator vs 500 L target.
- **"Not in plan today":** Pack rows present in plan with qty=0 are visible but greyed; editable if reality differs.
- **"+ Add unplanned FG":** Allows reporting an FG that wasn't in the plan but shares an existing batch's base.
- **"+ Add unplanned batch":** Picker for an entirely unplanned base produced ad-hoc.
- **Submit:** Posts N parallel `POST /api/v1/mutations/production-actual` calls (one per FG with qty>0). Each carries `from_plan_id` (existing column from Gate 5 signal #18). Failures don't roll back successful submissions; toast summarizes "Submitted 4 of 5; 1 failed: <reason>."
- **Component consumption:** Existing two-head BOM explosion handler (`fn_explode_bom_to_components_v2`) computes RM consumption on each submission. No change.

### 6.4 Page states

| State | Display |
|---|---|
| No plan for selected day | "No production planned for May 4. [📋 Open Production Plan] or [+ Report unplanned batch]" |
| Partial plan reported | Per-FG status: ✓ Reported (qty=X) or ⏳ Pending |
| Full plan reported | "✅ All planned production for May 4 reported. [📋 Back to Plan]" |
| Future date | Warning: "You are reporting on May 7, which is in the future. Continue?" |

### 6.5 Round-trip back to plan

Breadcrumb at top: `Production Plan → Daily Report (May 4)`. Clicking "Production Plan" returns to the calendar with the reported day highlighted. After full submission, the day's card on the plan grid carries a green "✅ Completed" tag.

---

## 7. State Machine & Lifecycle

```
   ┌─────────┐  user edits          ┌─────────┐  Send to Operators    ┌──────────┐
   │  draft  │─────────────────────▶│ planned │─────────────────────▶│in_prod   │
   │         │◀─── recompute        │         │                       │          │
   └─────────┘     overwrites       └─────────┘                       └──────────┘
        │                                │                                  │
        │ Tom deletes batch              │ Tom edits (with confirm)         │ first
        │                                │                                  │ Production
        ▼                                ▼                                  │ Actual
   ┌─────────┐                     ┌──────────┐                            │ posted
   │cancelled│                     │  edited  │ (back to planned on save)  ▼
   └─────────┘                     └──────────┘                       ┌──────────┐
                                                                      │completed │
                                                                      └──────────┘
```

| Status | Editable by | Visible to operators |
|---|---|---|
| `draft` | Owner only | No |
| `planned` | Owner with confirmation | Yes (Production Actual day picker) |
| `in_production` | Locked (cancel-only) | Yes (yellow "in progress" badge) |
| `completed` | Read-only | Yes (green "done" badge) |
| `cancelled` | Read-only | No |

---

## 8. Recompute Behavior (most important edge case)

| Scenario | Behavior |
|---|---|
| All current-week plans are `draft`, no edits | Silently replace with new proposal |
| Some `draft` rows have `is_user_modified=true` | Modal: "3 batches you edited will be overwritten. [Keep my edits & merge new] [Discard my edits] [Cancel]" |
| Any rows are `planned` / `in_production` / `completed` | New proposal only for unscheduled days. Locked rows untouched. Banner: "2 batches in flight — recompute affects only Mon, Wed, Fri." |
| Recompute would defer a `planned` batch to overflow | Block with error: "Recomputing would push DETOX to next week, but it's already promised. Cancel current plan first." |

**"Keep my edits & merge new"** logic: preserve user-edited batches; new proposal fills only empty days.

---

## 9. Schema Changes

```sql
-- Add to private_core.production_plan
ALTER TABLE private_core.production_plan
  ADD COLUMN base_bom_head_id text NULL
    REFERENCES private_core.bom_head(bom_head_id),
  ADD COLUMN pack_manifest jsonb NOT NULL DEFAULT '[]'::jsonb,
  ADD COLUMN linked_recommendation_ids uuid[] NULL,
  ADD COLUMN proposal_id uuid NULL,
  ADD COLUMN is_user_modified boolean NOT NULL DEFAULT false,
  ADD COLUMN batch_size_l numeric NOT NULL DEFAULT 500;

-- Add to private_core.planning_policy (one row per policy class)
ALTER TABLE private_core.planning_policy
  ADD COLUMN safety_days_per_base integer NOT NULL DEFAULT 5,
  ADD COLUMN batch_size_l numeric NOT NULL DEFAULT 500,
  ADD COLUMN work_days_of_week int[] NOT NULL DEFAULT ARRAY[0,1,2,3,4],
  ADD COLUMN max_batches_per_day integer NOT NULL DEFAULT 1;

-- Add to private_core.planning_run_recommendations
ALTER TABLE private_core.planning_run_recommendations
  ADD COLUMN consumed_by_proposal_id uuid NULL;

-- New SQL function
CREATE OR REPLACE FUNCTION private_core.fn_propose_weekly_production_plan(
  p_week_start date,
  p_actor_user_id uuid
) RETURNS uuid -- proposal_id
AS $$ ... $$;

-- New view powering the 8-week overflow drill-down
CREATE OR REPLACE VIEW api_read.v_daily_inventory_projection AS
  SELECT site_id, base_bom_head_id, projection_day, projected_liters,
         scheduled_inflow_l, demand_l, days_of_cover
  FROM ...;
```

---

## 10. API Surface

```
NEW
  POST   /api/v1/mutations/production-plan/propose
         body: { week_start: date }
         effect: runs fn_propose_weekly_production_plan
         returns: { proposal_id, batches_created, deferred_count, exceptions[] }

  GET    /api/v1/queries/production-plan/week/:week_start
         returns: { batches[], proposal_meta, overflow_banner, capacity }

  GET    /api/v1/queries/production-plan/projection/:base_bom_head_id?weeks=8
         returns: { daily_projection[], reorder_point, batches_scheduled[] }

  PATCH  /api/v1/mutations/production-plan/:plan_id
         body: { plan_date?, pack_manifest?, notes?, expected_updated_at }
         effect: marks is_user_modified=true; recomputes total_liters; concurrency check
         returns: { plan, conflict_warnings[] }

  POST   /api/v1/mutations/production-plan/:plan_id/cancel
         body: { reason: string, expected_updated_at }

  POST   /api/v1/mutations/production-plan/send-to-operators
         body: { week_start: date, plan_ids: uuid[] }
         effect: bulk transition draft → planned

EXISTING (extend with from_plan_id wiring; already in place)
  POST   /api/v1/mutations/production-actual
         body: { ..., from_plan_id?: uuid }   -- column added Gate 5 signal #18

NEW
  GET    /api/v1/queries/production-actual/day/:date
         returns: { plans[], pack_rows_with_status[], reported_actuals[] }
         (powers the Daily Report pre-fill)
```

---

## 11. Implementation Tranches

```
PHASE 1 — Smart proposal + calendar grid + basic edit
  ✅ Migration: schema additions (Section 9)
  ✅ Migration: planning_policy seed defaults
  ✅ Function: fn_propose_weekly_production_plan
  ✅ View: v_daily_inventory_projection
  ✅ Backend: new endpoints (Section 10)
  ✅ Portal: calendar grid layout
  ✅ Portal: drawer + drag-drop + add batch
  ✅ Portal: save / send to operators
  ✅ Portal: production-actual auto-fill from plan
  ✅ Polish iteration #1 (mandate per Tom)

PHASE 2 — Resilience & multi-week
  • Capacity overflow banner + 8-week drill-down view
  • REPACK item support (separate visual + math)
  • Concurrency presence indicators
  • Cancel / re-open flow
  • Polish iteration #2

PHASE 3 — Optimization assistance
  • "Suggest day swaps" — algorithm shows alternative spreads
  • Per-base color theming consistency across all surfaces
  • Dashboard widget on /dashboard/v2 (planned vs actual)
  • Polish iteration #3
```

---

## 12. Polish Iteration Cadence (process commitment)

Every tranche ends with a dedicated **UX/UI polish loop** before moving to the next tranche, per Tom's mandate (brainstorming session 2026-05-03):

```
For each tranche:
  1. Build to functional acceptance (works end-to-end, schema correct,
     happy path + 1 edge case verified)
  2. STOP — open the surface in browser
  3. Polish iteration (1-3 cycles):
       a) Tom walks through the surface as a real operator
       b) Records every friction, every "this is ugly", every "wrong info shown"
       c) Each item gets a fix in the same tranche before moving on
  4. Tranche closes only when Tom signs off polish
  5. Move to next tranche
```

### 12.1 Per-surface acceptance criteria (non-negotiable, every tranche)

- Empty state has a clear next action
- Loading state never flashes layout shift
- Every action has feedback (toast / inline status / disabled state)
- Mobile (375 px) renders without horizontal scroll
- Keyboard navigation works for primary actions
- LTR alignment correct for all data and chrome
- Color usage consistent with existing palette

---

## 13. Out of Scope (explicit)

- Shift-level scheduling (within-day timing of batches)
- Operator skill matching (who runs which batch)
- Equipment scheduling beyond "1 batch/day" capacity
- Cost-optimized lot sizing (we optimize for stock-out avoidance + full batches; cost not modeled)
- Multi-site (`site_id` stays `GT-MAIN` throughout)

---

## 14. Open Questions for Implementation

1. **`base_fill_qty_per_unit` coverage:** Confirm every MANUFACTURED item in `items` has this column populated. Current state may have nulls — needs audit before the engine runs.
2. **Daily disaggregation source:** Currently `v_planning_demand` weeklyizes via migration 0128. We need either daily-aware projection or smart even-spread within weekly buckets. Recommend the latter for v1 (simpler, monthly forecast inherently lacks per-day granularity).
3. **Per-base color palette:** Tom to choose 8-12 colors for top bases (or accept system default).
4. **Operator notification on "Send to Operators":** Email, banner on dashboard, or both? (Banner exists on `/dashboard/v2` cycle 7; email is new infra.)
5. **Concurrency optimistic-locking column source:** `production_plan.updated_at` already exists; confirm trigger updates it on every PATCH.

---

## 15. Source

This spec is the synthesis of a brainstorming session with Tom on 2026-05-03 (transcript in conversation history, available on request). All design decisions in this doc were approved verbatim by Tom in that session before commit.

---

**End of design spec.**
