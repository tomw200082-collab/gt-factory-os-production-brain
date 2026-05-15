# Phase 10 — Economics Layer Design Spec

> **Status:** DRAFT — pending Tom approval. No migration, no code change, no live system touch until Tom signs off on this spec in writing.
>
> **Owner:** Tom (sole approver).
> **Author:** AI brain (PRODUCTION).
> **Date:** 2026-05-13.
> **Phase:** 10 — Economics Layer (cost rollup, FG COGS, gross margin, inventory valuation).
> **Prerequisite:** Gate 5 closed (Phase 8 Run F Wave 4 — kernel rewrite, runtime quiet).
> **Companion brief (for external consultant):** `docs/superpowers/plans/2026-05-13-phase10-economics-advisor-brief.md`.
>
> **Authority alignment:**
> - `CLAUDE.md` — locked decisions, tiebreakers, schema posture (money_4dp, qty_8dp, append-only audit, net-of-VAT, ledger semantics).
> - `EXECUTION_POLICY.md` — frozen flags, write boundaries, evidence standard.
> - `CURRENT_STATE.md` — Phase 10 listed as "NOT ATTEMPTED: post-closure stretch per A11. Reserved migrations 0058+." Reservation supersedes original number — actual migration numbers will be allocated from current tip `0186` (next available `0187`).
> - `docs/contracts/SCHEMA_GUIDANCE.md` — Green Invoice rules (net-of-VAT, no auto-update active prices, validation required), Path B cost architecture (2026-04-23 decision).
>
> **Reservation:** this is a design spec, not an authority document and not a migration. It does not bind the system until Tom approves and a migration lands.

---

## 0. Authority and stop conditions (re-affirmed)

Before reading any further, the following remain in force and **cannot be overridden by anything in this spec**:

1. `LIONWHEEL_FG_OUT_BRIDGE_ENABLED = false` — frozen.
2. `SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED = false` — frozen.
3. `change_log` and `price_history` are append-only — enforced by trigger `change_log_append_only_guard()`. **This spec does not weaken append-only.** Every new audit table added here uses the same guard.
4. No autonomous `git push`, merge, deploy.
5. All cost writes require Tom approval; automated systems land **draft rows only**.
6. All amounts in `money_4dp` (numeric(18,4)), all quantities in `qty_8dp` (numeric(24,8)). All amounts **net of VAT** (17% Israeli VAT excluded from internal storage and computation).
7. No fabricated data. If a field or behavior has not been verified, it lands in §11 Open Assumptions and **blocks downstream work that depends on it**.

---

## 1. Goal

Answer four questions for every active FG SKU, every day, with audit history:

| Q | Answer surface |
|---|---|
| What does it cost us to make one unit? | `cogs_per_unit_ils` from `fg_cogs_snapshots` |
| What did we sell it for on average recently? | `avg_sale_price_ils` from `fg_avg_sale_price_snapshots` |
| What's the gross margin? | `gross_margin_ils` and `gross_margin_pct` in `v_fg_economics` |
| What's sitting in our warehouse worth? | `fg_inventory_value_at_cost`, `fg_inventory_value_at_sale_price`, `embedded_gross_margin_in_stock` in `v_fg_economics`, plus RM/PKG value from `current_balances × supplier_items.std_cost_per_inv_uom` |

Non-goal: actual cost (FIFO/LIFO/weighted-average from real receipts). v1 uses **standard cost only**. Actual-cost variance analysis is deferred.

---

## 2. Architecture decision (LOCKED by Tom, 2026-05-13)

Three approaches were evaluated in the advisor brief (`docs/superpowers/plans/2026-05-13-phase10-economics-advisor-brief.md` §Phase 10 architecture approaches).

| Approach | Status | Allowed use |
|---|---|---|
| **A** — On-demand computation (no snapshots, compute at every read via `fn_explode_bom_to_components`) | **NOT primary reporting source.** Allowed **only** as a verification / debug tool to compare against snapshot output, run ad-hoc, never wired to the dashboard. | Verification, drift detection, debugging discrepancies. |
| **B** — Append-only snapshot tables + view | **PRIMARY.** All reporting flows from snapshots. Snapshots are immutable history. | Production reporting, dashboards, audit. |
| **C** — Mutable computed columns on `items` (e.g., `items.std_cost_computed_ils`, `items.avg_sale_price_ils`) | **REJECTED.** No mutable cost columns added to `items` as a source of truth. A read-optimized cache is **not** considered for v1 and would not be the audit source. | Not in v1. Not in this spec. |

Rationale (matches Tom's brief decisions):
- B mirrors existing system design (`balance_anchors`, `stock_ledger`, `current_balances`, `price_history` — all append-only history + projection patterns).
- B gives free history: `cogs_per_unit_ils` for any FG on any past date is a `WHERE snapshot_at <= …` query.
- B gives free drift detection: compare yesterday's snapshot to today's, surface unexpected jumps.
- A cannot be primary because BOM explosion across the catalog at dashboard read time is heavyweight and provides no audit trail.
- C would weaken `items` invariants and create a second writable surface for the same fact (the `supplier_items` cost is already the authoritative input under Path B).

---

## 3. Data model

### 3.1 New tables (all append-only, all `private_core`, all use `change_log_append_only_guard()` triggers)

#### 3.1.1 `private_core.fg_cogs_snapshots`

Append-only history of computed per-unit COGS for every active FG item, written by the COGS snapshot job.

```sql
create table private_core.fg_cogs_snapshots (
  fg_cogs_snapshot_id      uuid primary key default gen_random_uuid(),

  item_id                  text not null references private_core.items(item_id),

  -- Authoritative per-unit standard COGS in ILS, net of VAT.
  -- NULL when cogs_complete = false. Never zero unless verified to be a zero-cost item.
  cogs_per_unit_ils        private_core.money_4dp,

  -- TRUE iff every input component used by this item's BOM (or supplier mapping
  -- for BOUGHT_FINISHED / REPACK) has a non-null std_cost_per_inv_uom on its
  -- primary supplier_items row (or on components.std_cost_per_inv_uom as
  -- documented Path B fallback) AND every BOM line resolves cleanly.
  cogs_complete            boolean not null,

  -- When cogs_complete = false: ordered JSONB array of objects identifying
  -- which inputs are missing cost.
  -- Shape: [
  --   {"component_id":"PKG-...","reason":"no_primary_supplier_cost"},
  --   {"component_id":"RM-...","reason":"primary_supplier_cost_null"},
  --   {"item_id":"FG-BF-...","reason":"bought_finished_no_primary_supplier_cost"}
  -- ]
  -- Empty [] when cogs_complete = true.
  missing_cost_components  jsonb not null default '[]'::jsonb,

  -- Per-component breakdown for verification + drift forensics.
  -- Shape: [
  --   {"component_id":"...","qty_per_fg_unit":"1.23000000","unit_cost_ils":"4.5600","line_cost_ils":"5.6088"},
  --   ...
  -- ]
  -- Always populated (even on cogs_complete=false rows; missing lines have
  -- unit_cost_ils=null and contribute null to the sum).
  cost_breakdown           jsonb not null default '[]'::jsonb,

  -- Which supply path produced this row. Mirrors items.supply_method exactly
  -- at snapshot time so historical reads stay self-describing if supply_method
  -- ever changes for an item.
  supply_method_snapshot   text not null
                           check (supply_method_snapshot in
                                  ('MANUFACTURED','BOUGHT_FINISHED','REPACK')),

  -- Snapshot semantics: event_at = the business date this COGS applies to
  -- (default now() in v1; opens room for back-dated re-snapshots later);
  -- posted_at = row insertion time.
  event_at                 timestamptz not null default now(),
  posted_at                timestamptz not null default now(),

  -- Run lineage. NULL allowed if a manual one-off insert is ever needed for
  -- verification (rare; must be approved).
  run_id                   uuid,
  source                   text not null
                           check (source in ('nightly_job','manual_verification','backfill')),

  -- Actor (system row pattern, same as price_history).
  actor_user_id            uuid references private_core.app_users(user_id),
  actor_snapshot           text not null
);

create index idx_fg_cogs_snapshots_item_event
  on private_core.fg_cogs_snapshots(item_id, event_at desc);

create index idx_fg_cogs_snapshots_run
  on private_core.fg_cogs_snapshots(run_id)
  where run_id is not null;

create trigger trg_fg_cogs_snapshots_no_update
  before update on private_core.fg_cogs_snapshots
  for each row execute function private_core.change_log_append_only_guard();

create trigger trg_fg_cogs_snapshots_no_delete
  before delete on private_core.fg_cogs_snapshots
  for each row execute function private_core.change_log_append_only_guard();
```

#### 3.1.2 `private_core.fg_avg_sale_price_snapshots`

Append-only history of qty-weighted average sale price per FG, written by the monthly agent.

```sql
create table private_core.fg_avg_sale_price_snapshots (
  fg_avg_sale_price_snapshot_id  uuid primary key default gen_random_uuid(),

  item_id                  text not null references private_core.items(item_id),

  -- Qty-weighted average: SUM(qty * unit_price) / SUM(qty) over the period.
  -- NULL when transaction_count = 0. Never fabricated.
  avg_sale_price_ils       private_core.money_4dp,

  -- Period the window covers. Inclusive bounds in business-date space.
  period_start             date not null,
  period_end               date not null,
  check (period_end >= period_start),

  -- Total transactions counted (after filters: status, returns, mappable SKU).
  transaction_count        integer not null check (transaction_count >= 0),

  -- Total units sold in the period (denominator of the weighted average).
  total_qty_sold           private_core.qty_8dp not null default 0,

  -- Reliability flag (see §6.4 thresholds; values not invented — confirm before code lands).
  -- 'HIGH' | 'LOW' | 'NONE'
  reliability_flag         text not null
                           check (reliability_flag in ('HIGH','LOW','NONE')),

  -- Snapshot meta.
  posted_at                timestamptz not null default now(),
  run_id                   uuid,
  source                   text not null
                           check (source in ('monthly_job','manual_verification','backfill')),

  actor_user_id            uuid references private_core.app_users(user_id),
  actor_snapshot           text not null,

  -- Audit trail of input filters applied. JSONB so we can extend without
  -- migration. Recommended keys (not enforced):
  --   {
  --     "min_transaction_threshold": 5,
  --     "excluded_statuses": ["cancelled","returned"],
  --     "currency_assumption": "ILS-net-of-VAT",  -- BLOCKED until A10-1 resolved
  --     "lw_price_parser_version": "v1"
  --   }
  filter_meta              jsonb not null default '{}'::jsonb
);

create index idx_fg_avg_sale_price_item_period
  on private_core.fg_avg_sale_price_snapshots(item_id, period_end desc);

create trigger trg_fg_avg_sale_price_snapshots_no_update
  before update on private_core.fg_avg_sale_price_snapshots
  for each row execute function private_core.change_log_append_only_guard();

create trigger trg_fg_avg_sale_price_snapshots_no_delete
  before delete on private_core.fg_avg_sale_price_snapshots
  for each row execute function private_core.change_log_append_only_guard();
```

#### 3.1.3 `private_core.supplier_cost_drafts` (GI prefill staging)

Draft suggestions from GI ingest. Mutable (UPDATE allowed) because admin can edit before approval. Approval is a one-way transition: `pending → approved` (which writes the live cost and inserts `price_history`) or `pending → rejected`.

```sql
create table private_core.supplier_cost_drafts (
  supplier_cost_draft_id   uuid primary key default gen_random_uuid(),

  supplier_item_id         uuid not null references private_core.supplier_items(supplier_item_id),

  -- Suggested net-of-VAT cost from GI invoice line.
  suggested_cost_ils       private_core.money_4dp not null check (suggested_cost_ils >= 0),

  -- Reference to the GI document this came from.
  source_invoice_id        text,
  source_invoice_date      date,
  source_line_ref          text,

  -- Editable by admin before approval.
  reviewer_note            text,

  -- State machine.
  status                   text not null default 'pending'
                           check (status in ('pending','approved','rejected','superseded')),

  -- When approved: timestamp + actor + the price_history_id we wrote.
  approved_at              timestamptz,
  approved_by_user_id      uuid references private_core.app_users(user_id),
  approved_actor_snapshot  text,
  resulting_price_history_id uuid references private_core.price_history(price_history_id),

  -- When rejected: timestamp + actor + reason.
  rejected_at              timestamptz,
  rejected_by_user_id      uuid references private_core.app_users(user_id),
  rejected_actor_snapshot  text,
  rejection_reason         text,

  created_at               timestamptz not null default now(),
  updated_at               timestamptz not null default now()
);

create trigger trg_supplier_cost_drafts_touch_updated_at
  before update on private_core.supplier_cost_drafts
  for each row execute function private_core.touch_updated_at();

create index idx_supplier_cost_drafts_status
  on private_core.supplier_cost_drafts(status, created_at desc);

create index idx_supplier_cost_drafts_supplier_item
  on private_core.supplier_cost_drafts(supplier_item_id);
```

**Critical constraint** (enforced in handler, not DDL, because the cross-table write is application-level):

- On `status='approved'`: the handler **must in a single transaction**:
  1. `UPDATE private_core.supplier_items SET std_cost_per_inv_uom = suggested_cost_ils, updated_at = now() WHERE supplier_item_id = …`
  2. `INSERT INTO private_core.price_history (supplier_item_id, unit_price_net, source='manual', event_at = source_invoice_date, posted_at = now(), actor_user_id, actor_snapshot, source_document_id = source_invoice_id, notes = 'Approved from GI prefill draft #<draft_id>')` — capture the returned `price_history_id`.
  3. `UPDATE private_core.supplier_cost_drafts SET status='approved', approved_at=now(), approved_by_user_id, approved_actor_snapshot, resulting_price_history_id = <inserted_id> WHERE supplier_cost_draft_id = …`
  4. Emit `change_log` row with `action='SUPPLIER_PRICE_UPDATE_MANUAL'` per `change_log_contract.md §3.3`.

If any step fails, the whole transaction rolls back. No partial state ever.

**Reserved status value — `'superseded'`.** The `status` CHECK constraint admits four values: `'pending'`, `'approved'`, `'rejected'`, and `'superseded'`. Only the first three are **operational** in this spec. `'superseded'` is a **reserved** value, non-operational in v1, intended for a future flow where a newer pending draft replaces an older pending draft for the same `supplier_item_id` (the older row would be transitioned `pending → superseded` rather than left to age). No code in Wave 10A or Wave 10B writes `status='superseded'`; no handler reads it as a meaningful state; no UI surface renders it. The value is included in the CHECK enum now solely to avoid a future migration when the supersede flow is added. Reviewers should treat any v1 code that writes or reads `'superseded'` as a defect.

### 3.2 New view

#### `private_core.v_fg_economics`

The single reporting surface for the economics dashboard. Joins latest COGS snapshot + latest avg-sale-price snapshot + current FG balance. **Reads must always go through this view, not the snapshot tables directly**, so column semantics stay enforced.

```sql
create or replace view private_core.v_fg_economics as
with latest_cogs as (
  select distinct on (item_id)
    item_id,
    cogs_per_unit_ils,
    cogs_complete,
    missing_cost_components,
    supply_method_snapshot,
    posted_at as cogs_snapshot_at
  from private_core.fg_cogs_snapshots
  order by item_id, event_at desc, posted_at desc
),
latest_asp as (
  select distinct on (item_id)
    item_id,
    avg_sale_price_ils,
    period_start,
    period_end,
    transaction_count,
    reliability_flag,
    posted_at as avg_sale_price_snapshot_at
  from private_core.fg_avg_sale_price_snapshots
  order by item_id, period_end desc, posted_at desc
),
fg_qty as (
  select item_id, qty_on_hand
  from private_core.current_balances
  where entity_kind = 'item'   -- TODO verify: confirm current_balances column name before code lands
)
select
  i.item_id,
  i.item_name,

  c.cogs_per_unit_ils,
  coalesce(c.cogs_complete, false) as cogs_complete,
  coalesce(c.missing_cost_components, '[]'::jsonb) as missing_cost_components,
  c.cogs_snapshot_at,

  a.avg_sale_price_ils,
  case
    when a.period_start is not null
    then a.period_start::text || ' to ' || a.period_end::text
    else null
  end as avg_sale_price_period,
  coalesce(a.transaction_count, 0) as transaction_count,
  coalesce(a.reliability_flag, 'NONE') as reliability_flag,
  a.avg_sale_price_snapshot_at,

  -- Surface total_qty_sold alongside transaction_count so the UI can show
  -- BOTH numbers (per §16.7). Reliability is never a black box.
  coalesce(a.total_qty_sold, 0) as total_qty_sold,

  -- Material margins (LOCKED naming per §16.6 — labor + overhead excluded
  -- from v1 COGS, every margin column reflects "material margin before
  -- labor & overhead"). NULL on either side propagates to NULL.
  case
    when c.cogs_per_unit_ils is not null and a.avg_sale_price_ils is not null
    then a.avg_sale_price_ils - c.cogs_per_unit_ils
    else null
  end as material_margin_ils,
  case
    when c.cogs_per_unit_ils is not null
     and a.avg_sale_price_ils is not null
     and a.avg_sale_price_ils > 0
    then round(((a.avg_sale_price_ils - c.cogs_per_unit_ils) / a.avg_sale_price_ils) * 100, 2)
    else null
  end as material_margin_pct,

  -- Stock-on-hand valuations. ALWAYS both. Labels matter (see §7).
  coalesce(q.qty_on_hand, 0) as qty_on_hand,
  case
    when c.cogs_per_unit_ils is not null and q.qty_on_hand is not null
    then c.cogs_per_unit_ils * q.qty_on_hand
    else null
  end as fg_inventory_value_at_cost,
  case
    when a.avg_sale_price_ils is not null and q.qty_on_hand is not null
    then a.avg_sale_price_ils * q.qty_on_hand
    else null
  end as fg_inventory_value_at_sale_price,
  case
    when c.cogs_per_unit_ils is not null
     and a.avg_sale_price_ils is not null
     and q.qty_on_hand is not null
    then (a.avg_sale_price_ils - c.cogs_per_unit_ils) * q.qty_on_hand
    else null
  end as embedded_material_margin_in_stock

from private_core.items i
left join latest_cogs c on c.item_id = i.item_id
left join latest_asp a on a.item_id = i.item_id
left join fg_qty q on q.item_id = i.item_id
where i.status = 'ACTIVE';
```

Columns (final, satisfies Tom's "at least" list with reliability_flag, snapshot_at, and total_qty_sold added):

| # | Column | Type | Nullable | Notes |
|---|---|---|---|---|
| 1 | `item_id` | text | no | |
| 2 | `item_name` | text | no | |
| 3 | `cogs_per_unit_ils` | money_4dp | yes | NULL when `cogs_complete=false` |
| 4 | `cogs_complete` | boolean | no | default false |
| 5 | `missing_cost_components` | jsonb | no | `[]` when complete |
| 6 | `cogs_snapshot_at` | timestamptz | yes | |
| 7 | `avg_sale_price_ils` | money_4dp | yes | NULL when `transaction_count=0` |
| 8 | `avg_sale_price_period` | text | yes | e.g., `"2026-04-13 to 2026-05-13"` |
| 9 | `transaction_count` | integer | no | default 0 |
| 10 | `total_qty_sold` | qty_8dp | no | default 0 — surfaced for UI reliability display per §16.7 |
| 11 | `reliability_flag` | text | no | `'HIGH'|'LOW'|'NONE'` — internal grouping only; UI shows raw counts |
| 12 | `avg_sale_price_snapshot_at` | timestamptz | yes | |
| 13 | `material_margin_ils` | money_4dp | yes | NULL on either-side NULL; material-only (before labor & overhead) |
| 14 | `material_margin_pct` | numeric(6,2) | yes | NULL on either-side NULL; material-only |
| 15 | `qty_on_hand` | qty_8dp | no | default 0 from `current_balances` |
| 16 | `fg_inventory_value_at_cost` | money_4dp | yes | `qty × COGS` |
| 17 | `fg_inventory_value_at_sale_price` | money_4dp | yes | `qty × avg_sale_price` |
| 18 | `embedded_material_margin_in_stock` | money_4dp | yes | `qty × material_margin` |

### 3.3 Schema impact summary

- New tables: 3 (`fg_cogs_snapshots`, `fg_avg_sale_price_snapshots`, `supplier_cost_drafts`).
- New view: 1 (`v_fg_economics`).
- Modified tables: **none.** `items`, `components`, `supplier_items`, `price_history`, `bom_*`, `current_balances`, `orders_mirror_lines` are not altered.
- New triggers: 4 (append-only guards on the two snapshot tables; `touch_updated_at` on drafts).
- No change_log enum extension required — `SUPPLIER_PRICE_UPDATE_MANUAL` and `PRICE_HISTORY_INSERT` already exist (migration 0025).

---

## 4. COGS computation logic

### 4.1 Per supply_method

Driven by `items.supply_method`. Same code path as the planning engine wherever possible — **reuse the per-item overload `private_core.fn_explode_bom_to_components(p_item_id text, p_qty qty_8dp DEFAULT 1)`** from **migration 0191** (added during Wave 10A Task 2.1 as an architectural fix when the implementer discovered that migration 0041 defined only a `(p_run_id uuid)` variant used by the planning engine); do not rebuild BOM walking. The function is pure (`LANGUAGE sql STABLE`) and returns one row per leaf component with columns `(component_id text, qty_per_unit qty_8dp, source_layer text)` where `source_layer ∈ ('PACK', 'BASE', NULL)` so the cost breakdown can surface which BOM layer each component came from (used for the Product drilldown §16.4). The planning engine's existing `(p_run_id uuid)` variant from migration 0041 is **unchanged** — both functions coexist via PostgreSQL overload resolution.

| supply_method | COGS source |
|---|---|
| `MANUFACTURED` | Walk BOM via `fn_explode_bom_to_components(p_item_id := item_id, p_qty := 1)`, sum each component's `qty_per_unit × unit_cost`. Two-stage items (with both `base_bom_head_id` and `primary_bom_head_id` + `base_fill_qty_per_unit`) are already handled by the function — base-BOM rows return `source_layer='BASE'`, pack-BOM rows return `source_layer='PACK'`. **Verify on a known two-stage item before snapshot job goes broad** (§9). |
| `BOUGHT_FINISHED` | Look up `supplier_items` row where `item_id = …` AND `is_primary = true`. Take `std_cost_per_inv_uom`. |
| `REPACK` | **A10-4 open.** Verify with Tom: do REPACK items consume a single input component × ratio (most likely), or do they have a single-line BOM? Spec assumes single-line BOM path for now; if it turns out to be a special-cased component reference, computation logic adapts but storage shape stays identical. |

### 4.2 Per-component unit cost lookup (Path B)

For each component returned by BOM explosion:

1. **Primary:** `supplier_items.std_cost_per_inv_uom` for the row where `component_id = X AND is_primary = true`.
2. **Fallback:** `components.std_cost_per_inv_uom` (Path B documented default — migration 0075 line 142).
3. **If both NULL:** add to `missing_cost_components`, set `cogs_complete = false`, `cogs_per_unit_ils = NULL`.

No averaging across suppliers in v1 — primary supplier is authoritative.

### 4.3 Missing-cost blocking (Tom decision, locked)

If `cogs_complete = false` for an FG item, that FG is **blocked from the economics dashboard's "computed" sections** (no margin, no inventory-at-cost, no embedded-margin shown). The item still appears with:
- `cogs_complete = false`
- `missing_cost_components` enumerating exactly which inputs to fix
- A clear UI affordance: "Fix supplier cost for X → opens master-data editor scoped to that supplier_items row"

This realizes Tom's earlier answer: block the **entire product**, not just the missing line. Avg sale price still shows (it's independent of cost completeness).

### 4.4 Snapshot job

- Cadence: nightly (recommended slot: ~02:00 Israel time, after planning rebuild).
- Wrapper: `pg_cron` (already in use for `audit_runs`).
- Run pattern: one `run_id = gen_random_uuid()` per job invocation; every row written in the run carries the same `run_id` for forensic trace.
- One row per active item per run — even when nothing changed since the prior run. (Append-only by design; cheap storage; allows clean date-range queries.)
- Failures: row-level errors are caught and logged to `audit_runs`; partial runs are acceptable (other items still snapshot) but the run is marked DEGRADED.

### 4.5 Net-of-VAT discipline

All `unit_cost` reads from `supplier_items.std_cost_per_inv_uom` are already net-of-VAT (Path B + GI ingest rule per CLAUDE.md). COGS rolls up net amounts; the resulting `cogs_per_unit_ils` is net-of-VAT. The dashboard label must state this explicitly.

---

## 5. Avg sale price computation logic

### 5.1 Source data

Sale transactions live in `private_core.orders_mirror_lines` (the LionWheel mirror). Relevant columns:

- `lw_sku` (text, not null) — supplier-facing SKU. Maps to `items.item_id` via a mapping that **must be located and verified** before any code lands (A10-8).
- `lw_qty_ordered` (qty_8dp, not null) — parsed numeric quantity.
- `lw_price_raw` (text, nullable) — **string-encoded, currency unstated**. Parsing **explicitly deferred** per migration 0024 comment. This is the central blocker.
- `lw_status` / parent `orders_mirror` status — to filter cancelled / returned orders. Status semantics must be verified (A10-2).
- **Business-date column** — `created_at` (order creation) is the obvious candidate but is **likely wrong** for management reporting. Delivery date or invoice date is usually more correct. Resolution required (A10-10) before window filter goes live.

### 5.2 Blocking dependency on A10-1

`lw_price_raw` is text with no currency declaration. Until currency is disambiguated (most likely ILS gross-of-VAT based on Israeli e-commerce convention, but **this is unverified**), the parser cannot land. Until the parser lands, the monthly job cannot run. Until the monthly job runs, `avg_sale_price_ils` for all items is NULL and the entire margin column in `v_fg_economics` is NULL.

**This is acceptable** for the initial Phase 10 rollout. The system ships with COGS first, margin second once currency is resolved. The view degrades gracefully (NULLs all the way) and never fabricates.

### 5.3 Computation (once A10-1 resolves)

For each active FG with mappable `lw_sku`:

```
WITH window AS (
  SELECT
    l.lw_sku,
    parsed_price_net_ils(l.lw_price_raw)::money_4dp AS unit_price_net,
    l.lw_qty_ordered AS qty,
    o.status,
    o.created_at
  FROM private_core.orders_mirror_lines l
  JOIN private_core.orders_mirror o USING (lw_order_id)
  WHERE o.<business_date_column> >= (CURRENT_DATE - INTERVAL '30 days')   -- A10-10 verify (delivery / invoice / created_at)
    AND o.<business_date_column> <  CURRENT_DATE
    AND o.status NOT IN ('cancelled','returned')   -- A10-2 verify
    AND l.lw_price_raw IS NOT NULL
    AND l.lw_qty_ordered > 0
)
SELECT
  map.item_id,
  CASE
    WHEN SUM(qty) > 0
    THEN SUM(qty * unit_price_net) / SUM(qty)
    ELSE NULL
  END AS avg_sale_price_ils,
  COUNT(*) AS transaction_count,
  SUM(qty) AS total_qty_sold
FROM window w
JOIN <sku_to_item_mapping> map ON map.lw_sku = w.lw_sku
GROUP BY map.item_id;
```

### 5.4 Reliability — expose both numbers (not a single flag)

**UI rule (LOCKED per §16.7):** every screen showing `avg_sale_price_ils` must also show **both** `transaction_count` and `total_qty_sold` verbatim. No UI screen displays a bare "LOW reliability" label without the underlying numbers — Tom (or any planner) judges meaningfulness from the actual counts.

Internal `reliability_flag` column is kept for grouping / filtering / future automation, with provisional thresholds (Tom to confirm at first real-data review):

| `transaction_count` over 30-day window | `reliability_flag` |
|---|---|
| 0 | `NONE` (and `avg_sale_price_ils = NULL`) |
| 1–4 | `LOW` |
| ≥5 | `HIGH` |

The flag is **not** load-bearing in v1 UI logic — it informs visual treatment only. If the thresholds turn out wrong on first real data, the UI does not break; only the badge color shifts.

### 5.5 Cadence

- Default: monthly (Tom's stated preference).
- Each run computes the latest 30-day window ending at run date.
- Same `run_id` pattern as COGS snapshots.

### 5.6 No fabrication

If the SKU has 0 mappable transactions in the window: `avg_sale_price_ils = NULL`, `reliability_flag = 'NONE'`, `transaction_count = 0`. Never invented. Never copied forward from an old snapshot. A future manual-override mechanism may be added but is **not in v1**.

---

## 6. GI prefill flow (draft + approval only)

### 6.1 What the system does

1. A scheduled GI ingest script (or operator-triggered "Pull recent invoices" button) hits the GI API for invoices in a configurable window.
2. For each invoice line where a supplier mapping exists (supplier → supplier_items relationship), the script writes a `supplier_cost_drafts` row with `status='pending'`, suggesting the net-of-VAT line price.
3. **Nothing is written to `supplier_items` or `price_history` at this point.**

### 6.2 What the operator does

1. Admin opens "Cost Drafts" screen (admin role only).
2. Sees pending drafts grouped by supplier, with: current `supplier_items.std_cost_per_inv_uom`, suggested cost, delta %, source invoice ID/date.
3. For each draft: approve, edit-then-approve, or reject (with reason).

### 6.3 What approval writes (atomic transaction)

See §3.1.3 — the handler does all four steps or none.

### 6.4 What approval does **not** do

- Does not auto-bump cost beyond a threshold without explicit confirmation.
- Does not bypass `change_log` emit.
- Does not write to `supplier_items` directly without also writing `price_history`.
- Does not delete or mutate the draft row — `status` transitions append the approval metadata; the row itself is preserved for audit.

### 6.5 GI ingest is contract-bounded

CLAUDE.md §Integration guidance / Green Invoice: "Do not auto-create new components from invoice lines. Do not auto-update active prices unless mapping quality and threshold rules pass. Net-of-VAT cost semantics." Phase 10 enforces this by routing **all** GI-suggested costs through `supplier_cost_drafts` first, regardless of confidence. No bypass.

---

## 7. Financial labeling rules (LOCKED — UI cannot deviate)

The dashboard surface for Phase 10 **must** use these exact labels. Hebrew register entries land alongside English per `portal_language_direction_audit.md`. **Every margin column is "material-only, before labor & overhead"** — see §16.6 for the locked naming.

| Computed value | English label | Hebrew label | Forbidden |
|---|---|---|---|
| `cogs_per_unit_ils` | "Material cost per unit (net of VAT, before labor & overhead)" | "עלות חומרים ליחידה (ללא מע״מ, לפני עבודה ותקורות)" | "Cost", "Unit cost" without qualifier; "Gross cost"; bare "COGS" without "material" qualifier |
| `avg_sale_price_ils` | "Average sale price (last 30 days, net of VAT)" | "מחיר מכירה ממוצע (30 ימים אחרונים, ללא מע״מ)" | "Price", "Sale price" without window |
| `material_margin_ils` | "Material margin per unit (before labor & overhead)" | "מרווח חומרי ליחידה (לפני עבודה ותקורות)" | "Gross margin", "Profit", "Margin" without qualifier |
| `material_margin_pct` | "Material margin %" | "מרווח חומרי %" | "Gross margin %", "Markup %" |
| `fg_inventory_value_at_cost` | "FG inventory value at standard cost" | "שווי מלאי תוצרת מוגמרת בעלות תקן" | "Inventory value" (bare); "Inventory worth" |
| `fg_inventory_value_at_sale_price` | "FG sales-value estimate (at avg sale price)" | "אומדן שווי מכירה למלאי תוצרת (במחיר מכירה ממוצע)" | "Inventory value", "Inventory worth" |
| `embedded_material_margin_in_stock` | "Embedded material margin in current stock" | "מרווח חומרי טמון במלאי הנוכחי" | "Unrealized profit", "Potential profit", "Embedded gross margin" |
| RM/PKG inventory total (computed separately from `current_balances × supplier_items.std_cost_per_inv_uom`) | "RM/PKG inventory at standard cost" | "שווי חומרי גלם ואריזות בעלות תקן" | "Inventory value" (bare) |

**Mandatory footnote on every screen showing margin (English + Hebrew):**

> "Margins shown are material-only, before labor and overhead. Operational profitability requires adding direct labor and allocated overhead."
>
> "המרווחים המוצגים הם חומרי בלבד, לפני עבודה ותקורות. רווחיות תפעולית מחייבת הוספת עבודה ישירה ותקורה מוקצית."

Rationale: the difference between "at cost" and "at sale price" is the single most common confusion in factory accounting. Tom must never have to ask "which one is this." Labels carry the qualifier.

---

## 8. Acceptance criteria — Phase 10 Done

Phase 10 is **not** done when tables exist. Phase 10 ships in two waves (§16.8); each wave has its own closure record. **"Phase 10 fully done" = both Wave 10A and Wave 10B closures signed.**

### Wave 10A — Cost foundation (no A10-1 dependency)

| # | Criterion | Evidence required |
|---|---|---|
| AC1 | `fg_cogs_snapshots` table exists with append-only trigger | Migration applied; trigger verified by attempting an UPDATE and seeing it raise. pgTAP test. |
| AC2 | `supplier_cost_drafts` table exists with the state machine constraint enforced in the approval handler | Migration applied; handler integration test. |
| AC3 | `v_fg_economics` view exists with all 18 columns from §3.2 (avg-sale-price columns return NULL until 10B) | View introspection (`\d+ v_fg_economics`) shows the column list verbatim. |
| AC4 | Nightly COGS snapshot job operational | Job ran ≥3 nights, latest run produced one row per active item, no DEGRADED states. |
| AC5 | Missing-cost-blocking enforced in UI | Manual test: pick an item, NULL its supplier cost, rerun snapshot, verify the FG appears with `cogs_complete=false` and the "computed" sections greyed out + actionable fix CTA. |
| AC6 | GI prefill draft flow live (admin-only) | End-to-end test: ingest creates draft → admin approves → `supplier_items.std_cost_per_inv_uom` updated, `price_history` row inserted, `change_log` row emitted, draft status flips to `approved`. All four observable in one transaction. |
| AC7 | Verification evidence on 2–3 known items, **signed off by Tom** | §9 evidence packet attached to the closure record; `delta_pct ≤ 1%` on every verified item. |
| AC8 | Financial labels audited (English + Hebrew, no ambiguous "inventory value", "material margin" qualifier present on every margin field) | ux-content-state-designer review pass; report attached. |
| AC9 | Economics surfaces live (admin/planner role only) — Dashboard (KPIs 2 + 5 populated; 1, 3, 4 show "Pending sale price data"), Product Economics table, Product drilldown, Cost Data Admin (Tabs 1 + 2 + 3) | Routes reachable, RLS verified, screenshots of populated state with the four surfaces from §16.1. |
| AC10 | Mandatory footnote present on every screen showing margin ("Margins shown are material-only…") | Screenshot evidence. |

### Wave 10B — Sale-price + margin (gated on A10-1, A10-2, A10-8, A10-10)

| # | Criterion | Evidence required |
|---|---|---|
| AC11 | `fg_avg_sale_price_snapshots` table exists with append-only trigger | pgTAP test. |
| AC12 | `lw_price_raw` parser landed with verified currency/VAT semantics | A10-1 resolution document; parser unit tests covering ≥5 known invoice values reconciled to known totals. |
| AC13 | Business-date column resolved (A10-10) | A10-10 resolution document showing which column on `orders_mirror` was chosen and why. |
| AC14 | Monthly avg-sale-price agent operational | Job ran at least once post-resolution; produced reasonable values for ≥1 SKU with `HIGH` reliability and ≥1 SKU with `LOW`. |
| AC15 | `avg_sale_price_ils` reconciled against ≥5 known invoice prices, delta ≤ 1% | Reconciliation table. |
| AC16 | KPIs 1, 3, 4 populated on the dashboard; margin columns populated in Product Economics table; sale-price history populated in drilldown | Screenshot evidence. |
| AC17 | UI shows **both** `transaction_count` and `total_qty_sold` next to every avg-sale-price display (no bare reliability flag) per §16.7 | Screenshot evidence. |

Phase 10 closure record (eventually goes in `CURRENT_STATE.md`) must check **all 17** boxes across both waves.

---

## 9. Verification gate (BLOCKS broad rollout)

Before the snapshot job runs over the full FG catalog, COGS must be hand-verified on **at least three items spanning the three supply paths**:

1. **One MANUFACTURED single-stage** — pick an item with `base_bom_head_id IS NULL` and a non-trivial component list.
2. **One MANUFACTURED two-stage** — pick an item with both `base_bom_head_id` and `primary_bom_head_id` set, plus a non-null `base_fill_qty_per_unit`. This is the most error-prone case (two BOM walks + scaling).
3. **One BOUGHT_FINISHED or REPACK** — depending on which exists in the catalog. If only BOUGHT_FINISHED exists in the catalog, verify that; REPACK verification can defer until a REPACK item is created.

For each verified item:

| Field | Source |
|---|---|
| `expected_cogs_ils` | Tom (manual computation from workbook or fresh hand-calculation) |
| `computed_cogs_ils` | `fg_cogs_snapshots.cogs_per_unit_ils` from the snapshot run |
| `delta_ils` | absolute |
| `delta_pct` | relative |
| `cost_breakdown` | full JSONB breakdown from the snapshot row, attached for line-by-line comparison |

Acceptance: `delta_pct ≤ 1%` on every verified item, and Tom signs off in writing.

**No production rollout of the dashboard until verification passes.** If `delta_pct > 1%`, root-cause the breakdown before touching the snapshot logic — it is almost always a missing supplier_items row, a wrong `pack_conversion`, or a stale `purchase_to_inv_factor`.

---

## 10. Migration sequence (actual numbers landed; updated post-Task 2.1)

Reservation order (logical and numeric), grouped by wave per §16.8. Wave 10A landed four planned slots (M1–M4) plus one architectural insertion (M-insert) discovered during Task 2.1; Wave 10B slot numbers shifted accordingly.

**Wave 10A migrations (no A10-1 dependency):**

| Slot | Migration # | Purpose |
|---|---|---|
| M1 | 0187 | `fg_cogs_snapshots` + append-only triggers + indexes |
| M2 | 0188 | `supplier_cost_drafts` + updated_at trigger + indexes |
| M3 | 0189 | `v_fg_economics` view v1 (avg-sale-price columns return NULL until 10B) |
| M4 | 0190 | `pg_cron` nightly COGS schedule entry (inserted disabled; enabled at G3 PASS) |
| **M-insert** | **0191** | **`private_core.fn_explode_bom_to_components(p_item_id text, p_qty qty_8dp DEFAULT 1)` per-item overload — landed during Task 2.1 when the implementer found that migration 0041 only defined a `(p_run_id uuid)` variant. Pure (`LANGUAGE sql STABLE`); coexists with the planning-engine variant via PostgreSQL overload resolution. See §4.1 for usage.** |

**Wave 10B migrations (gated on A10-1, A10-2, A10-8, A10-10) — numbers shifted by +1 from earlier draft to accommodate 0191 architectural insertion:**

| Slot | Migration # | Purpose |
|---|---|---|
| M5 | 0192 | `fg_avg_sale_price_snapshots` + append-only triggers + indexes (was 0191 in earlier draft) |
| M6 | 0193 | `v_fg_economics` rebuild v2 to JOIN sale-price snapshots — replaces M3/0189 (was 0192 in earlier draft) |
| M7 | 0194 | `pg_cron` monthly avg-sale-price schedule entry (was 0193 in earlier draft) |

Current migration tip at spec-write time was `0186`; Wave 10A landed at `0187–0191` (five migrations after the M-insert was added); Wave 10B is reserved at `0192–0194`. The "Reserved 0058+" note in `CURRENT_STATE.md` predates intervening work and is superseded by the actual tip.

Each migration follows existing conventions: `BEGIN`/`COMMIT`, `set search_path to private_core, public`, header docstring citing this spec.

---

## 11. Open assumptions (must be verified before downstream code lands)

| ID | Assumption | Verification required | Blocks |
|---|---|---|---|
| **A10-1** | `lw_price_raw` currency is ILS gross-of-VAT. Parser strips VAT (÷ 1.17 or similar) before storage. | Inspect ≥5 live invoices vs. corresponding LionWheel order line `lw_price_raw` values. Reconcile to known invoice totals. | `fg_avg_sale_price_snapshots`, monthly job, all margin columns in `v_fg_economics`. |
| **A10-2** | `orders_mirror.status` values include explicit `'cancelled'` and/or `'returned'` markers we can filter on. | Query `SELECT DISTINCT status FROM private_core.orders_mirror`; map each value to keep/exclude. | Monthly job filter logic. |
| **A10-3** | GI invoice lines can be mapped to `supplier_items` rows with sufficient confidence to drive prefill drafts. | Sample 20 recent GI invoice lines; attempt mapping by supplier + product name/SKU; report match rate. | GI prefill script. |
| **A10-4** | REPACK COGS = cost of the single input component × consumption ratio. | Inspect any existing REPACK item's BOM in `bom_lines`; confirm shape. | COGS for REPACK items (not blocking if no REPACK items exist in catalog yet). |
| **A10-5** | `supplier_items.std_cost_per_inv_uom` (Path B) is **net of VAT** for all currently-populated rows. | Spot-check 5 supplier_items rows against their known invoice prices. | All COGS rollups; entire `v_fg_economics`. |
| **A10-6** | Reliability flag thresholds (1–4=LOW, ≥5=HIGH) match Tom's intuition. | Tom decision after seeing first real data. | Final values, not the column itself. |
| **A10-7** | Snapshot frequency: nightly COGS, monthly avg sale price. | Tom confirm at spec sign-off (already provisionally agreed). | Job schedule definitions. |
| **A10-8** | `lw_sku → item_id` mapping exists and is queryable. | Locate the mapping table or view; if it doesn't exist as a first-class artifact, identify how planning currently resolves LionWheel sales to FG items. | Monthly job join logic. |
| **A10-9** | `current_balances` schema (column names, `entity_kind` discriminator) — confirm the column names used in `v_fg_economics` match the live table. | `\d+ private_core.current_balances` | The view's `fg_qty` CTE. |
| **A10-10** | Which date column on `orders_mirror` represents the correct business date for sale-price windowing? Candidates: delivery date, invoice date, `created_at` (order creation). For management reporting, delivery or invoice date is probably more correct than `created_at`. | Inspect `orders_mirror` schema; list all date/timestamp columns; map each to a business event; Tom decides which one feeds the 30-day window. | Monthly job WHERE clause; meaning of every avg-sale-price snapshot. **Blocking for Wave 10B.** |

**Any A10-* item that remains open at implementation time MUST be either resolved or explicitly carried as a known gap in the closure record.** No code that depends on an open A10-* item lands.

---

## 12. Out of scope for v1

- Actual cost (FIFO / LIFO / weighted-average from real receipt prices). v1 uses standard cost only.
- Variance analysis (std vs actual).
- Multi-currency cost (assume ILS only; no FX tracking).
- Per-customer pricing tiers.
- Discount / promotion attribution.
- Labor and overhead allocation (COGS in v1 is material-only). **Naming and label discipline make this explicit on every screen** — every margin label says "material margin before labor & overhead" and every dashboard surface carries the mandatory footnote from §7. Operational profit/loss reporting is a separate future module.
- Cost smoothing (e.g., 90-day moving average of supplier costs). v1 uses point-in-time `supplier_items.std_cost_per_inv_uom`.
- Forecast-driven cost simulation ("what if supplier X raises prices 5%?").
- Cost rollup for components themselves (we cost FG; we do not currently store rolled-up component costs as snapshots).

Each of these can be added later without breaking the v1 snapshot tables — append-only history accommodates more columns via add-only migrations.

---

## 13. Review and approval gates

| Gate | Wave | Action | Who |
|---|---|---|---|
| G1 — Spec approval | — | Read this document; approve / request changes in writing | Tom |
| G2 — Migrations 10A land | 10A | Apply M1–M4 against dev; verify with pgTAP | backend-db-executor (after G1) |
| G3 — Verification | 10A | Run COGS snapshot job on dev; produce §9 evidence table on 2–3 items | backend-db-executor + Tom sign-off |
| G4 — Dashboard surface | 10A | Implement Economics Dashboard + Product Economics table + Product drilldown + Cost Data Admin (admin/planner gating) | portal-production-executor after RUNTIME_READY(Phase10-Wave10A) |
| G5 — GI prefill | 10A | Land draft ingest + approval UI (Cost Data Admin Tab 2) | integration-boundary-executor (drafts) + portal-production-executor (UI) |
| G6 — Wave 10A closure | 10A | AC1–AC10 met; closure record drafted | factory-os-governor |
| G7 — A10-1 unblock | 10B-gate | Resolve LionWheel `lw_price_raw` currency disambiguation; produce A10-1 resolution document | Tom + integration-boundary-executor |
| G8 — A10-10 unblock | 10B-gate | Resolve business-date column for sale-price window | Tom + integration-boundary-executor |
| G9 — Migrations 10B land | 10B | Apply M5–M6 against dev; rebuild view; verify with pgTAP | backend-db-executor |
| G10 — Monthly job + reconciliation | 10B | Land avg-sale-price job; reconcile ≥5 known invoice prices | backend-db-executor + Tom sign-off |
| G11 — Wave 10B portal surfacing | 10B | KPIs 1/3/4 populated, margin columns populated, drilldown sale-price history populated | portal-production-executor |
| G12 — Phase 10 full closure | 10B | AC11–AC17 met; both wave closure records cited | factory-os-governor |

No gate may be skipped. No gate may proceed without the previous one's evidence.

---

## 14. Stop conditions specific to Phase 10

In addition to the system-wide stop conditions in CLAUDE.md, this phase halts on:

1. Attempt to write to `supplier_items.std_cost_per_inv_uom` outside the `supplier_cost_drafts` approval handler.
2. Attempt to insert into `price_history` without a corresponding `change_log` row.
3. Attempt to UPDATE/DELETE a row in any append-only snapshot table.
4. `v_fg_economics` returning a non-NULL `cogs_per_unit_ils` while `cogs_complete = false`.
5. `avg_sale_price_ils` non-NULL with `transaction_count = 0` (fabrication detector).
6. Snapshot job running with any A10-* item flagged "blocking" still unresolved.

Any of the above ⇒ halt, emit signal, route to factory-os-governor.

---

## 15. Open questions for Tom (small, before implementation)

1. **Business-date column candidate (A10-10)** — your instinct is delivery date or invoice date over `created_at`. Should we treat **delivery date** as the recommended candidate to verify first (when goods left the warehouse), with **invoice date** as fallback? Or do you have a different preference?
2. **Snapshot retention** — append-only means rows accumulate forever. Acceptable in v1 (volumes are tiny), but do you want a future archive/prune policy noted as future-out-of-scope?
3. **Verification items** — would you like to pre-pick the 3 items now (so they're documented before G3), or pick at G3 time?
4. **Bulk approval threshold for GI prefill drafts (§16.5 Tab 2)** — proposed default is "Approve all where delta ≤ 5%". Acceptable, or different number?

(Note: Q1 from earlier draft — labor/overhead labeling — now resolved via §16.6 + §7 mandatory footnote. Q2 — reliability thresholds — now resolved via §16.7: both raw numbers are shown verbatim, internal flag is informational only.)

---

## 16. System Integration + UX Contract

Phase 10 is **not** a set of cost tables — it is a small managerial module for product and inventory economics. The UX shape below is the contract; data and migrations exist to serve it.

### 16.1 Surface inventory

Phase 10 ships **four UI surfaces**, not one:

| Surface | Route (proposed) | Audience | Purpose | Frequency |
|---|---|---|---|---|
| Economics Dashboard | `/economics` | admin + planner | daily executive read; 5 KPIs only | daily |
| Product Economics table | `/economics/products` | admin + planner | drill from dashboard or direct; per-product economics | daily / on-demand |
| Product drilldown | `/economics/products/[item_id]` | admin + planner | one product: cost composition + history + source attribution | on-demand |
| Cost Data Admin | `/admin/cost-data` (with `/drafts` deep link) | admin only | maintenance of supplier costs + GI prefill draft review | weekly / on-demand |

All routes RLS-enforced. Operators (production / packing roles) **do not** see these surfaces — same posture as Inbox (planner+admin only per `project_inbox_audience_planner_admin_only`).

### 16.2 Economics Dashboard — exactly 5 KPIs (no charts, no tables)

| # | KPI | Source | Empty state |
|---|---|---|---|
| 1 | FG sales-value estimate (current stock) | SUM(`fg_inventory_value_at_sale_price`) over FG where `avg_sale_price_ils` not null | "Pending sale price data" + count of items pending; link to Cost Data Admin |
| 2 | FG inventory at standard cost | SUM(`fg_inventory_value_at_cost`) over FG where `cogs_complete=true` | "Pending cost data" + count of `cogs_complete=false` items; link to Cost Data Admin |
| 3 | Embedded material margin in stock | SUM(`embedded_material_margin_in_stock`) over FG where both sides non-null | NULL-degrades when either side missing |
| 4 | Average material margin % (catalog-weighted) | `SUM(qty × material_margin_ils) / SUM(qty × avg_sale_price_ils)` over eligible FG | "Insufficient sale-price coverage" |
| 5 | Data quality issues count | COUNT(FG where `cogs_complete=false` OR `avg_sale_price_ils IS NULL`) | "All clean" |

Each KPI tile is clickable → routes to the relevant filtered slice of the Product Economics table.

### 16.3 Product Economics table

One row per active FG item.

**Columns (left to right):**

1. Item name (sticky-left, clickable → drilldown)
2. Quantity on hand
3. Material cost per unit (`cogs_per_unit_ils`)
4. Average sale price (`avg_sale_price_ils`, with reliability badge showing **both** `transaction_count` and `total_qty_sold` per §16.7)
5. Material margin per unit
6. Material margin %
7. Value at standard cost (`fg_inventory_value_at_cost`)
8. Sales-value estimate (`fg_inventory_value_at_sale_price`)
9. Embedded material margin (`embedded_material_margin_in_stock`)
10. Status badges (`cogs_complete` / sale-price reliability)

**Default sort:** descending by `embedded_material_margin_in_stock`. Falls back to descending by `fg_inventory_value_at_sale_price` for rows where embedded margin is NULL (so items with missing cost data still appear in a useful order). Alphabetical is an allowed re-sort but **never** the default.

**Filter chips at top:** "All" / "Missing cost data" / "Missing sale-price data" / "Low-reliability sale price". Default = "All".

**No pagination in v1** — catalog is small enough; virtual scroll if it grows.

### 16.4 Product drilldown

Drill from any item row. One product, full picture:

**Section A — Current state:** the same row from §16.3 but full-width, all numeric fields prominently displayed with their full §7 labels.

**Section B — Cost breakdown** (from `cost_breakdown` JSONB on latest snapshot):

| Component | Qty in BOM (per FG unit) | Unit cost (net of VAT) | Line cost | % of product cost |
|---|---|---|---|---|
| RM-… | 1.23 | 4.56 | 5.61 | 38.2% |
| PKG-… | 1.00 | 0.92 | 0.92 | 6.3% |
| … | … | … | … | … |
| **Total** | | | **14.68** | **100%** |

Rows sortable by % of product cost (default) or alphabetical. Components with NULL unit cost render as "MISSING — fix in Master Maintenance" with a deep link to the supplier_items editor for that component's primary supplier.

**Section C — History strip:** small time-series of `cogs_per_unit_ils` from the last ~12 snapshots + `avg_sale_price_ils` from the last ~6 monthly snapshots. Sparkline-only in v1.

**Section D — Source attribution:**
- "Cost snapshot from: 2026-05-13 02:00 (nightly job, run #abc-…)"
- "Sale price snapshot from: 2026-05-01 (last 30 days), 47 transactions covering 312 units"

### 16.5 Cost Data Admin

Admin-only. Three tabs:

**Tab 1 — Supplier costs (table):**
- One row per `supplier_items` where the target component (or BOUGHT_FINISHED item) is in active use.
- Columns: component/item name, supplier name, current `std_cost_per_inv_uom`, last update date, last source (`manual` / `green_invoice` / `seed`).
- **Default sort: stalest first** (oldest `updated_at` on top) — Tom sees what's drifting.
- Click row → inline edit (writes through the same approval handler: updates `supplier_items` + `price_history` + emits `change_log`, in one transaction).

**Tab 2 — GI prefill drafts:**
- Pending drafts first.
- Columns: supplier, component/item, current cost, suggested cost, delta %, invoice date, invoice ID, source line ref.
- Per-row actions: **Approve** / **Edit-then-approve** / **Reject** (with reason).
- **Bulk action:** "Approve all where delta ≤ X%" (default 5%; confirm dialog required). Even bulk approval emits **one** `change_log` row + **one** `price_history` row per draft — no aggregation.

**Tab 3 — Price history (read-only):**
- Filter by supplier_items.
- Reverse-chronological list of `price_history` rows with source, actor, document reference.

### 16.6 Naming — material margin (LOCKED, supersedes §7 draft column names)

Margin column names changed from initial draft to remove ambiguity:

| Was (initial §3.2 draft) | Is (LOCKED) |
|---|---|
| `gross_margin_ils` | `material_margin_ils` |
| `gross_margin_pct` | `material_margin_pct` |
| `embedded_gross_margin_in_stock` | `embedded_material_margin_in_stock` |

User-facing labels follow §7. The naming change matters because: **v1 COGS is material-only** (no labor, no overhead). Calling it "gross margin" would over-promise; "material margin before labor & overhead" tells the truth.

### 16.7 Reliability — show both numbers, not a single flag

**Every screen showing `avg_sale_price_ils` must also show both `transaction_count` and `total_qty_sold` verbatim.** No screen displays a bare "LOW reliability" label without the underlying counts.

Display pattern:

```
₪ 18.20
47 orders · 312 units
(last 30 days)
```

The internal `reliability_flag` column classifies HIGH/LOW/NONE for grouping and filtering only, with provisional thresholds (§5.4). Visual badge color may follow the flag, but **no text decision** is gated on it. Tom (or any planner) judges meaningfulness from the actual counts.

### 16.8 Rollout — two waves (decoupled by A10-1)

Phase 10 ships in two waves so the COGS foundation lands without blocking on LionWheel currency disambiguation.

**Wave 10A — Cost foundation (no A10-1 dependency):**
- Migrations M1–M4
- Nightly COGS snapshot job
- Dashboard KPIs 2 + 5 functional; KPIs 1, 3, 4 show "Pending sale price data"
- Product Economics table functional with cost data; sale-price + margin columns blank with explainer
- Product drilldown functional (cost breakdown + cost history)
- Cost Data Admin Tabs 1 + 3 functional
- GI prefill drafts (Tab 2) ship: integration boundary executor lands ingest; admin UI ships
- §9 verification gate satisfied on 3 items
- Tom sign-off ⇒ Wave 10A closure (AC1–AC10)

**Wave 10B — Sale-price + margin (gated on A10-1, A10-2, A10-8, A10-10):**
- Migrations M5–M6
- Monthly avg-sale-price agent
- KPIs 1, 3, 4 populated
- Product Economics table margin columns populated
- Product drilldown sale-price history section populated
- Reconciliation against ≥5 known invoice prices
- Tom sign-off ⇒ Phase 10 fully closed (AC11–AC17)

**"Phase 10 done" = both wave closures signed.** Until Wave 10B, the experience is incomplete, and the dashboard explicitly says so via the empty-state copy on KPIs 1/3/4.

### 16.9 No new agent kinds, no new background workers beyond two snapshot jobs

All four UI surfaces consume `v_fg_economics` (or its precursor tables) read-only. Cost Data Admin write paths route through the **existing** supplier-items mutation handlers + the **new** `supplier_cost_drafts` approval handler. The only new scheduled work is:

1. Nightly COGS snapshot job (Wave 10A)
2. Monthly avg-sale-price agent (Wave 10B)

This keeps the operational surface small. No new always-on workers, no streaming, no event bus.

### 16.10 What "complete economics experience" means

A Phase 10 UI is **complete** when, opening the Economics Dashboard, Tom can in one minute:

- See the cash sitting in finished-goods stock (KPI 1 + 2)
- See how much of that is margin vs cost (KPI 3 + 4)
- Click into "Data quality issues" (KPI 5) and immediately know which items are broken and why
- Open the Product Economics table sorted so the most economically significant items are on top
- Click into any one product and see, line-by-line, where the cost comes from and what the sale price has been
- Trust the numbers because every average is backed by visible transaction counts and unit totals, every cost is timestamped to its snapshot, and every label tells the truth about what's included and excluded

Anything less than this is not Phase 10 done.

---

**End of spec.**

Drafted 2026-05-13. Amended 2026-05-13 (Tom UX/integration section added pre-implementation; margin columns renamed material_*; A10-10 added; AC list split into Wave 10A + Wave 10B). Pending Tom final approval before any migration, code, or UI work begins.
