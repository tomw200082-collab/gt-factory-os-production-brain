# GT Factory OS — Procurement System Map

Exact reference for everything the procurement-planning skill reads or calls. Verified live against
`gt-ops-prod` on 2026-06-25; re-verified + corrected 2026-07-16 (item_type taxonomy, fn signatures,
tier ADR §7b, 0284/0285 engine additions §7c). If a query errors on a column, the schema has evolved —
re-introspect with `information_schema.columns` and update, rather than guessing.

## Table of contents
1. Connection constants & actor resolution
2. Master data tables
3. Demand & stock tables
4. Planning engine (MRP) tables
5. Purchase execution tables
6. Policy levers (`planning_policy`) — the tunable knobs
7. Engine functions — what to call, what is draft vs committing
8. Economics views
9. Known structural traps (read before trusting any number)
10. Master-data quality baseline (2026-06-25 snapshot)

---

## 1. Connection constants & actor resolution

- **Supabase project_id**: `rvadsozabmxkkrktwgnv` (label `gt-ops-prod`)
- **Schema**: `private_core` (everything below lives here)
- **Default site**: `site_id = 'GT-MAIN'`
- **Currency of record**: ILS; money stored as `numeric(18,4)`
- **Actor** — never hardcode a UUID. Engine functions need `p_actor*`. Resolve at runtime:
  ```sql
  select id, display_name, role from private_core.app_users
  where role in ('admin','owner','planner') and status='active'
  order by role limit 5;
  ```
  Confirm with Tom which `id` to act as before any mutating call.

---

## 2. Master data tables

### `components` — raw material + packaging master (the things you buy)
Key planning columns:
- `component_id` (TEXT PK), `component_name`, `component_class`, `component_group`, `material_group_key`, `status`
- UOM chain: `inventory_uom`, `purchase_uom`, `bom_uom`, `purchase_to_inv_factor` (purchase→inventory multiplier)
- `primary_supplier_id`, `lead_time_days`
- `moq_purchase_uom`, `order_multiple_purchase_uom`  ← MOQ + order rounding in purchase UOM
- `std_cost_per_purchase_uom`, `std_cost_per_inv_uom`
- `criticality` (free text; used for ABC/service-level tiering), `planned_flag` (only `true` are planned), `planning_policy_code`
- `fg_twin_item_id`, `fg_twin_units_per_inv_uom` (dual-role buy-finished-and-consume items)

### `suppliers`
- `supplier_id` (TEXT PK), `supplier_name_official`, `supplier_name_short`, `status`, `supplier_type`
- `currency`, `payment_terms`, `default_lead_time_days`, `default_moq`
- `primary_contact_name`, `primary_contact_phone`, `green_invoice_supplier_id`

### `supplier_items` — supplier × (component OR bought-finished item)
This is where supplier-specific overrides live (they beat the component/supplier defaults):
- `supplier_id`, `component_id` XOR `item_id`, `relationship`, `is_primary`
- `order_uom`, `inventory_uom`, `pack_conversion` (authoritative supplier UOM conversion)
- `lead_time_days`, `moq`, `safety_days`, `payment_terms`, `std_cost_per_inv_uom`, `approval_status`

### `component_procurement_specs` — exact "how to re-order this" detail (only 22 rows; high value)
- `component_id`, `supplier_id`, `spec` (jsonb: dimensions/material/finish/print/grind/packaging)
- `supplier_catalog_wording` (paste-ready ordering text), `ordering_notes` (quirks)
- `last_unit_price_net`, `last_price_invoice_ref`, `last_price_date`, `moq`, `order_multiple`
Use this verbatim when drafting a supplier order message.

### `planning_item_config` — per-ITEM (finished-good) planning overrides
Currently **0 rows** → every FG uses global defaults. Columns:
- `planning_mode` (auto | manual_review | blocked), `safety_stock_days`
- `min_coverage_days`, `target_coverage_days`, `max_coverage_days`  ← DDMRP-style bands
- `min_batch`, `max_batch`, `batch_multiple`, `production_lead_time_days`, `forecast_confidence_behavior`
Note: component (RM/PKG) buffers are tuned via `planning_policy` keys (§6), not this table.

---

## 3. Demand & stock tables

### `forecast_versions` / `forecast_lines` — demand input
- version: `cadence`, `horizon_start_at`, `horizon_weeks` (default 8), `status` (draft→published→superseded)
- line: `item_id`, `period_bucket_key` (week start date), `forecast_quantity`
- Only a **published** version feeds planning. Check freshness before every run.

### `current_balances` — on-hand projection (real table, transactionally maintained)
- `site_id`, `item_type` ('COMPONENT' | FG types), `item_id`, `batch_id_or_empty`
- `calculated_on_hand`, `last_event_at`, `last_refreshed_at`
- Parity is guaranteed by `rebuild_verifier()`; `planning_runs.rebuild_verifier_drift_at_run` records drift at run time (expect 0).

### `stock_ledger` — append-only event log (source for historical usage / ADU)
- `movement_type`, `item_type`, `item_id`, `batch_id`, `qty_delta` (sign = direction), `uom`
- `event_at`, `posted_at`, `post_status` (use `POSTED`), `reason_code`, `source_tab`
- `related_po_line_id`, `related_bom_version_id`, `related_movement_id` (reversal pointer)
- Consumption rows have `qty_delta < 0`.
- **item_type taxonomy (verified live 2026-07-16): `'RM' | 'PKG' | 'FG'` — in
  `stock_ledger`, `current_balances` AND `physical_counts` alike. There is NO
  `'COMPONENT'` value; components are RM + PKG. Filtering on
  `item_type='COMPONENT'` returns zero rows and silently produces an
  empty/green result (this bug lived in an earlier revision of
  `sql_library.md` §1b/§2/§3/§9 — fixed 2026-07-16).**

### `physical_counts` — last count per item (staleness check; `stale_count_days`=7)
Verified columns (2026-06-25): `submission_id` (uuid), `item_type`, `item_id`, `counted_quantity`, `unit`,
`snapshot_quantity`, `snapshot_at` (timestamptz — **the count timestamp**), `computed_delta`, `notes`.
Note: there is **no** `site_id` or `created_at` column — key staleness off `snapshot_at` and join on
(`item_type`,`item_id`) (see `sql_library.md` §1b).

---

## 4. Planning engine (MRP) tables — outputs of a planning run

- `planning_runs` — run header. Key cols: `planning_horizon_start_at`, `planning_horizon_weeks`,
  `policy_snapshot` (jsonb of the levers at run time), `demand_snapshot_forecast_version_id`,
  `stock_snapshot_anchor_refreshed_at`, `rebuild_verifier_drift_at_run`, `status` (draft→running→completed→superseded).
- `planning_run_component_demand` — gross component demand per (run, component, bucket): `required_qty`, `sources` (jsonb per-FG trace).
- `planning_run_component_netting` — **the netting math**: `demand_qty`, `on_hand_qty`, `open_po_qty`,
  `net_purchase_qty = greatest(demand − on_hand − open_po, 0)`, `po_substrate_present` (see trap §9).
- `planning_run_recommendations` — type-aware recs (`recommendation_type` = purchase | production).
  `required_qty`, `recommended_qty` (after MOQ rounding), `order_by_date`, `due_date`, `shortage_date`,
  `feasibility_status`, `supplier_id`, `moq_rounding_trace`, `logic_trace`, `blocking_issues`, `source_trace`.
- `planning_run_fg_coverage` — FG coverage per bucket (`shortage_flag`, `shortage_date`).

---

## 5. Purchase execution tables — the weekly session and its drafts

- `purchase_session` — one row per engine run. `session_type` ('weekly'), `session_date`, `status`
  ('open'→'completed'), `horizon_days`, `consolidation_window_days`, `demand_model_version`,
  `firmed_window`, `warnings` (jsonb — **read these every time**).
- `purchase_session_po` — one consolidated draft PO per supplier. `supplier_id`, `tier`, `status`
  ('proposed'→'approved'→'placed'/'skipped'), `order_by_date`, `earliest_need_date`, `covered_through_date`,
  `total_cost`, `order_document_text` (paste-ready supplier message), `logic_trace`, `blocking_issues`.
- `purchase_session_po_line` — lines. `component_id` XOR `item_id`, `line_label`, `recommended_qty`,
  `final_qty` (editable), `uom`, `unit_cost`, `line_cost` (generated), `earliest_need_date`,
  `coverage_trace` (jsonb), `is_user_added`, `is_dropped`, `edited_by_user_id`.
- `purchase_orders` / `purchase_order_lines` — committed POs (PK `PO-YYYY-NNNNN`). Lines carry
  `ordered_qty`, `received_qty`, `open_qty`, `line_status`, `expected_receive_date`,
  `actual_first_receipt_at`, `actual_last_receipt_at` (← lead-time-actual source). Header carries
  `order_date`, `payment_terms*`, `total_net/gross`. **DELETE forbidden** on both.

---

## 6. Policy levers (`planning_policy`) — the tunable knobs (current values 2026-06-25)

Read/write as key-value text rows. The buyer-relevant levers:

| Key | Value | Meaning / how to use |
|---|---|---|
| `planning.horizon_weeks` | 8 | Planning horizon (FAIL-HARD if missing). |
| `planning.grain` | weekly | Bucket grain (v1 weekly only). |
| `planning.purchase.horizon_days` | 56 | Daily-MRP projection horizon for purchasing. |
| `planning.purchase.consolidation_window_days` | 21 | **Lot size**: when a component crosses reorder, order covers this many days forward (period-order-quantity). Bigger = fewer/larger orders. |
| `planning.purchase.demand_rate_window_days` | 28 | Forward window used to derive each component's avg daily demand for the days-of-cover floor. |
| `planning.purchase.session_day_of_week` | 0 (Sun) | Weekly session day; drives the must-order-now release fence. |
| `planning.purchase.session_horizon_visible_days` | 56 | Read by API/portal surfaces for display windows (not by the engine itself). |
| `stale_count_days` | 7 | Physical-count staleness threshold; also read by the 0284 session input-integrity snapshot. |
| `planning.purchase.po_overdue_warning_days` | 7 | Open-PO line flagged `po_overdue_receipt` after N days past expected. |
| `planning.safety.component_cover_days_default` | 7 | **Global component buffer** (days of avg daily demand, applied as on-hand floor). Override per component → see below. This is THE highest-leverage lever and is currently flat for all 184 components. |
| `planning.safety.stock_days_default` | 0 | FG safety buffer (days). |
| `planning.supplier.default_lead_time_days` | 14 | Last-resort lead-time fallback when both supplier_items and suppliers are null. |
| `planning.order.min_trigger_pct_of_moq` | 10 | Skip a rec when `recommended_qty < MOQ × 10%`. |
| `planning.recommendation.auto_dismiss_if_coverage_days_above` | 90 | Auto-dismiss a rec if projected coverage (incl. the rec) exceeds 90 days (over-buy guard). |

**Per-component buffer override pattern** (the key the skill writes to tune buffers):
```
key   = 'planning.safety.component_cover_days.<COMPONENT_ID>'
value = '<days>'   -- e.g. '21'
```
This overrides the flat 7 for that one component. Writing these is a GATED action (Tom approval first).
Production-side per-base overrides also exist: `planning.production.safety_stock_l.<bom_head_id>` and
`planning.production.safety_days_per_base.<bom_head_id>`.

---

## 7. Engine functions — call surface

**Read/compute (projections — safe, no writes):**
- `fn_compute_daily_fg_projection(p_start date, p_end date)`
- `fn_compute_daily_supply_side_projection(p_start date, p_end date)`
- `fn_forecast_daily_demand(p_start date, p_end date)`
- `fn_tea_base_daily_demand_l(p_start, p_end)`

**Planning run pipeline (creates DRAFT rows — safe to run, nothing is ordered):**
- `fn_execute_planning_run(p_actor_user_id uuid, p_trigger_source text, p_idempotency_key text, p_horizon_start_at date, p_horizon_weeks integer)`
  → orchestrates `fn_compute_fg_net_requirements` → `fn_compute_component_net_purchase`
  → `fn_generate_purchase_recommendations` + `fn_generate_bf_purchase_recommendations`.

**Purchase session (creates DRAFT consolidated POs — safe to run):**
- `fn_generate_purchase_session(p_actor uuid, p_session_date date, p_session_type text)`
  → writes `purchase_session` + `purchase_session_po` + `purchase_session_po_line`.

**Production proposal (if a run also needs production):**
- `fn_propose_weekly_production_plan(p_week_start date, p_actor uuid)`,
  `fn_plan_tea_production(p_actor, p_horizon_days)`, `fn_plan_matcha_repack(p_actor, p_horizon_days)`.

**COMMITTING — gated, requires explicit Tom approval (real PO, real cash):**
- `fn_place_purchase_order(p_po_id text, p_actor_user_id uuid, p_actor_snapshot text, p_payment_terms text, p_payment_terms_net_days integer, p_payment_terms_eom boolean, p_line_prices jsonb, p_confirm_price_update boolean, p_expected_receive_date date, p_line_qty_overrides jsonb)`
  (signature re-verified 2026-07-16 — two params were added since the 2026-06-25 snapshot: the expected receive date, which closes the double-order trap at placement time, and per-line qty overrides)

Rule of thumb: **drafts may be generated after a quick confirmation; placement is never automatic.**

### 7b. Session tier logic — ADR (documented as-found 2026-07-16, unchanged by 0284)

`purchase_session_po.tier` is computed inside `fn_generate_purchase_session`
(SQL only — the API just reads the column). Exact semantics:

```
per line:      is_urgent = (need_date − lead_time_days < p_session_date)   -- release date already passed
                           OR (projected_on_hand_at_need < 0)              -- projected to go negative
per supplier:  urgent      = bool_or(line is_urgent) OR min(release_date) < p_session_date
               must        = min(release_date) < release_fence             -- next session day (Sunday)
               recommended = otherwise
```

Properties that follow (all verified live):
- **Dates/projection only** — no ₪ exposure, criticality or spend weighting.
- `need_date` is the first day projected stock dips below the **safety floor**
  (cover-days × ADU), not below zero — so "urgent" fires on floor breaches.
- One late line paints its **entire supplier PO** urgent (`bool_or`).
- With demand visible only ~2–3 firmed weeks ahead, a flat 7d buffer and
  7–14d lead times, release dates are chronically in the past → since May
  2026 the live distribution has been ~97% `urgent` (e.g. 16/16 on
  2026-07-16), 0–2 `must`, 0–1 `recommended`. Items whose lead time exceeds
  the 56d horizon (e.g. 127d matcha/bottles) can never be "on time".
- `p_session_date` matters: the portal start API passes `current_date`; the
  plan-production-14d ritual passes next Sunday — the fence and the
  `urgent` cutoffs shift accordingly.

Portal note (tranche 132): `/planning/procurement` no longer buckets by this
tier — it classifies each PO from the per-line `coverage_trace` (estimated
zero-stock date vs. arrival-if-ordered-today) and shows quantified expected
shortage instead. The tier column remains for API consumers and the calendar
view. Changing the SQL tier itself is a separate, Tom-gated decision.

### 7c. 0284/0285 additions (2026-07-16)

- `purchase_session.input_integrity` (jsonb): forecast `{age_days,
  coverage_end, horizon_end, uncovered_days}`, counts `{targets, fresh,
  stale, never_counted, threshold_days, oldest_age_days}` over the buy-list
  targets, `verifier_drift`. Read this instead of recomputing §1 when a
  fresh session exists.
- `coverage_trace` now carries `trace_version: 3`, `lt_source`
  (`component_master | supplier_item | supplier_default | global_default`),
  `criticality`, `last_count_age_days` (null = never counted), `moq`,
  `order_multiple`, `qty_purchase_before_rounding`.
- Lead-time resolution now follows the documented waterfall for components
  (previously: component master → global 14d, silently skipping
  supplier_items / suppliers defaults).
- `items.item_type='SYSTEM'` placeholders (EXCLUDED-NONSTOCK) are excluded
  from BF demand; SEMI-FRE/CAL/NAM-BASE are `planned_flag=false` (0285) —
  in-house brewed bases, never purchasable.

---

## 8. Economics views

- `v_rm_pkg_economics` — RM/PKG cost economics (use for spend/ABC and order valuation).
- `v_fg_economics` — finished-good economics.
- `v_cogs_breakdown_per_item` — per-item COGS breakdown.

---

## 9. Known structural traps (READ BEFORE TRUSTING ANY NUMBER)

1. **Open-PO supply not netted (double-order risk).** When an open PO line has no `expected_receive_date`,
   the engine does NOT count it as incoming supply and may recommend re-buying it. This surfaces as a
   `purchase_session.warnings` entry `po_missing_expected_delivery` (and the netting flag
   `po_substrate_present=false`). Live example seen 2026-06-25: `PO-2026-00252` (RAW-LIME-PUREE, 77) and
   `PO-2026-00253` (PKG-BAG-MAT-500G, 5000). (Re-verified 2026-06-25: the live list is broader — **4**
   open lines lack an ETA: `PO-2026-00216` (PKG-BOTTLE-1L, 32999), `PO-2026-00252`, `PO-2026-00253`,
   `PO-2026-00255` (RAW-LIME-PUREE, 20).) **Always resolve these dates before placing.**
2. **Flat buffers.** All 187 planned components share the global 7-day cover and 21-day consolidation;
   there are 0 per-component overrides. A flat buffer over-stocks stable items and under-protects volatile
   ones — the single biggest tuning opportunity (see methodology §Buffer mapping, incl. the 2026-07-16
   reality check: the naive daily-σ formula over-buffers here; use plan-aware/weekly variability).
3. **Master-data gaps fill silently with fallbacks.** Missing lead time → the
   0284 waterfall (supplier mapping → supplier default → global 14d, with
   `lt_source` recorded per line); missing MOQ → no rounding; missing cost →
   order can't be valued (line carries a `missing_price` blocking flag and
   costs 0 — understating session ₪). See §10. Gaps among the components *in
   this run's scope* matter most — scope the data-health check to them.
   **MOQ reality check (2026-07-16): MOQ is 0/NULL on all 187 planned
   components AND on all 269 approved supplier mappings — the entire
   MOQ/rounding mechanism is currently a no-op, and the min-trigger +
   90d-over-buy guards live only in the diagnostic planning-run path, not in
   the live session path.**
4. **Stale counts / verifier drift.** If `rebuild_verifier_drift_at_run` ≠ 0 or a scoped component's last
   physical count is older than `stale_count_days` (7), on-hand is suspect → netting is suspect.

---

## 10. Master-data quality baseline (2026-07-16 snapshot; count MOQ/multiple **zeros as missing** — 0 disables the mechanism exactly like NULL)

Across **187 planned, active components** and **269 approved component mappings**:
- 23 components (12%) missing lead time — of which 12 have a real value available
  today in supplier_items/suppliers (the 0284 waterfall now picks those up);
  **187 (100%) missing/zero MOQ; 187 (100%) missing/zero order multiple**;
  38 (20%) missing std cost; 15 (8%) missing primary supplier; 33 (18%) missing criticality.
- **10 components have NO approved supplier mapping** → un-orderable through the engine.
- supplier_items (approved, component-linked): 212/269 carry a lead time; **0/269 carry an MOQ**.
  Item mappings: 13/31 carry a lead time (BF items lean hardest on the global default).
- **0** per-component buffer overrides; **0** `planning_item_config` rows — the flat 7d
  cover is still universal.
- Catalog hygiene fixed 2026-07-16: SEMI-FRE/CAL/NAM-BASE `planned_flag=false` (0285);
  `EXCLUDED-NONSTOCK` (item_type=SYSTEM) filtered out of BF demand (0284).

Treat these as a moving baseline; the skill recomputes the scoped subset live each run —
and since 0284 the freshest per-session picture is already on
`purchase_session.input_integrity` + each line's `coverage_trace`.
