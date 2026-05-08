# Supply-Side Inventory Flow (Components + BOUGHT_FINISHED) — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a sister "Inventory Flow" page that shows daily projection for the **supply universe** — `private_core.components` (RM + PKG) plus `private_core.items` where `supply_method = 'BOUGHT_FINISHED'` — mirroring the existing FG flow page but with a different demand model (BOM-driven production consumption instead of, or alongside, customer demand).

**Architecture:** Parallel data layer behind a new SQL projection function + view, a new Fastify endpoint, and a new Next.js page that **reuses** the FG flow UI primitives (`DayCell`, `WeekCell`, `FlowGridDesktop`, `MobileCardStream`, `Sparkline`, `FilterBar`) by extending the shared `FlowItem`/`FlowResponse` Zod shape with one new field (`sku_kind`) and treating `family` as polymorphic (FG `family` for items, `component_class` for components). A tab navigator at the top of `/planning/inventory-flow` toggles between the FG view and the Supply view.

**Tech Stack:** PostgreSQL (Supabase) + Kysely + Fastify + Zod + Next.js 15 App Router + TanStack Query + Tailwind + shadcn/ui. pgTAP for DB tests, Vitest for handler tests, Playwright for portal smoke.

---

## Repository / Path Conventions

This project lives across two roots:

| Concern | Root |
|---|---|
| Backend (DB migrations, API, contracts, tests) | `C:/Users/tomw2/Projects/gt-factory-os/` |
| Frontend (Next.js portal) | `C:/Users/tomw2/Projects/window2-portal-sandbox/` |
| Authority docs + plans + state files | `c:/Users/tomw2/GTeveryday Dropbox/Data Center/Tom/AI Agents & Projects/Code Agents/PRODUCTION/` |

All file paths in tasks below are absolute. Backend paths start with `gt-factory-os/`; frontend paths start with `window2-portal-sandbox/`. The plan itself is saved under PRODUCTION's `docs/superpowers/plans/`.

**Latest DB migration on disk: `0145_v_daily_inventory_flow_include_manual_rows.sql`. The new migration in this plan is `0146`.**

---

## Scope (locked by Tom on 2026-05-06)

The Supply-side flow page covers **two SKU kinds**, unioned:

| sku_kind | Source table | Inflow | Outflow #1 | Outflow #2 |
|---|---|---|---|---|
| `COMPONENT` | `private_core.components` (RM + PKG) | PO receipts via `purchase_order_lines.component_id` | BOM consumption from `production_plan` (PACK BOM + BASE BOM if applicable, exploded to leaf components) | n/a — components are not sold direct |
| `ITEM` (BOUGHT_FINISHED only) | `private_core.items` WHERE `supply_method='BOUGHT_FINISHED'` | PO receipts via `purchase_order_lines.item_id` | n/a — BOUGHT_FINISHED items are not consumed in BOMs | LionWheel customer demand + forecast (same logic as existing FG flow) |

The page therefore renders **a heterogeneous list** keyed by `(sku_kind, sku_id)` where `sku_id = component_id` or `sku_id = item_id`. A single SKU never appears in both rows: COMPONENT is keyed by `component_id` (a separate ID space from items).

**Out of scope for v1:**
- Components consumed in production but **also** sold directly (no current schema link). If such a SKU exists, it's modeled today as either a component OR a BOUGHT_FINISHED item, never both.
- `MANUFACTURED` items (already on the FG flow page).
- `REPACK` items (already on the FG flow page).
- The planned-production overlay (already on the FG flow page; not requested for supply view in v1).
- Component-level BOM-consumption drill-down per planned batch (defer to v2; v1 surfaces aggregated daily consumption only).

---

## Design Decisions (locked)

### 1. Sku-kind unification on the wire

Extend the existing `FlowItemSchema` minimally so the Supply response can reuse it:

- Add `sku_kind: z.enum(['ITEM', 'COMPONENT'])` (defaults to `'ITEM'` for backward compat in the FG endpoint).
- Allow `supply_method` to be `null` (components have no supply_method).
- `family` remains a `string | null` field. For components, `family = component_class`.
- Everything else (`item_id`, `item_name`, `current_on_hand`, `risk_tier`, `days_of_cover`, `days[]`, `weeks[]`) is shape-identical.

This means **the FG endpoint stays binary-compatible**: it always emits `sku_kind='ITEM'`. The portal hook+grid components are agnostic to `sku_kind`.

### 2. SQL projection function

Create `private_core.fn_compute_daily_supply_side_projection(p_start date, p_end date)` returning rows shaped exactly like `fn_compute_daily_fg_projection` plus a `sku_kind text` column, keyed by `(sku_kind, sku_id, day)`. The function is the single source of truth for daily on-hand math; the view just decorates with master fields.

The function unions two sub-queries:
- **COMPONENT branch:** keyed by `component_id`, demand = daily BOM consumption from `production_plan` (status IN ('draft','planned','in_production')) on `plan_date`, supply = PO lines on `expected_receive_date`, seed_on_hand = SUM(`current_balances.calculated_on_hand`) WHERE `item_type IN ('RM','PKG') AND item_id = component_id`.
- **BOUGHT_FINISHED branch:** keyed by `item_id`, demand = LionWheel + forecast per `fn_compute_daily_fg_projection` (factored out of that function or recomputed inline), supply = PO lines on `expected_receive_date`, seed_on_hand = SUM(`current_balances.calculated_on_hand`) WHERE `item_type = 'FG' AND item_id = items.item_id AND items.supply_method = 'BOUGHT_FINISHED'`.

### 3. BOM-driven component daily consumption

The COMPONENT branch's demand requires a leaf-level BOM explosion of every `production_plan` row, on the plan's `plan_date`. The function `private_core.fn_explode_bom_to_components` (migration 0126) already does this for **planning_run buckets**, not per day. We will create a sibling helper:

`private_core.fn_explode_production_plan_to_daily_components(p_start date, p_end date)` returns `(component_id text, day date, qty private_core.qty_8dp)` rows, internally walking PACK BOM (and BASE BOM via the `BASE_BOM` line ref type) for each non-cancelled `production_plan` row whose `plan_date BETWEEN p_start AND p_end`.

This helper is called by the projection function for the COMPONENT branch's `demand_total_qty`.

### 4. Risk tier semantics

Identical Hybrid D model as FG (`fn_compute_daily_fg_projection`):
- `effective_lead_time_days` = `supplier_items.lead_time_days` (or `suppliers.default_lead_time_days`) + non-working day padding.
- `days_of_cover_at_day` = days from this day until on-hand goes below zero (or horizon end).
- `risk_tier` = stockout | critical | watch | healthy by `days_of_cover` vs `effective_lead_time_days`.
- `cell_tier_with_production` is **not** computed for the supply view in v1 (no planned-production overlay applies to components or to BOUGHT_FINISHED items). The field defaults to the same value as `tier` to keep the contract shape stable.

### 5. Page route + tab nav

- New page: `/planning/inventory-flow/supply` (sub-route of the existing inventory-flow tree).
- Tab nav at the top of **both** pages (`/planning/inventory-flow` and `/planning/inventory-flow/supply`):
  - "Finished Goods" (links to `/planning/inventory-flow`)
  - "Supply (RM + Bought-Finished)" (links to `/planning/inventory-flow/supply`)
- The tab nav is a small new shared component placed in `_components/InventoryFlowTabs.tsx`.
- Both pages reuse: `FilterBar`, `FlowGridDesktop`, `MobileCardStream`, `DayCell`, `DayPopover`, `WeekCell`, `Sparkline`, `InsightsHero`, `UnmappedSkusBanner`. The Supply page does **not** render `PlannedOverlayToggle` / `PlannedChip` / `PlannedTooltip` / `PlannedFooterCaveat` (no overlay in v1).

### 6. API surface

| Method | Path | Returns |
|---|---|---|
| GET | `/api/v1/queries/inventory/supply-flow` | `FlowResponseSchema` (with `sku_kind` populated on each row) |
| GET | `/api/v1/queries/inventory/supply-flow/sku/:sku_kind/:sku_id` | `FlowItemDetailSchema` per-SKU drill-down (POs + BOM-consumption events for COMPONENT; POs + LionWheel orders for ITEM) |

Frontend Next.js proxies:
- `GET /api/inventory/supply-flow` → upstream `GET /api/v1/queries/inventory/supply-flow`
- `GET /api/inventory/supply-flow/sku/[skuKind]/[skuId]` → upstream `GET /api/v1/queries/inventory/supply-flow/sku/{kind}/{id}`

### 7. Auth gate

Identical to FG flow: Operator + Planner + Admin (`roleAllowsInventoryFlowRead`). No new role check function — reuse the existing helper.

---

## File Structure

### Files to CREATE

**Backend (gt-factory-os):**
- `db/migrations/0146_v_daily_supply_side_flow.sql` — new SQL function `fn_compute_daily_supply_side_projection`, helper `fn_explode_production_plan_to_daily_components`, and view `api_read.v_daily_supply_side_flow`.
- `db/tests/0146_v_daily_supply_side_flow.test.sql` — pgTAP tests for the new function + helper + view.
- `api/src/inventory/contracts.supply_flow.ts` — Zod schemas (`SupplyFlowQuerySchema`, `SupplyFlowItemDetailSchema`). FlowResponse schema gets `sku_kind` extension via the shared mod (see edits below).
- `api/src/inventory/handler.supply_flow.ts` — `handleSupplyFlow`, `handleSupplyFlowSkuDetail`. Mirrors `handler.flow.ts`.
- `api/src/inventory/handler.supply_flow.test.ts` — Vitest unit tests (auth gate, validation, query shape).

**Frontend (window2-portal-sandbox):**
- `src/app/api/inventory/supply-flow/route.ts` — Next.js proxy → upstream Fastify.
- `src/app/api/inventory/supply-flow/sku/[skuKind]/[skuId]/route.ts` — drill-down proxy.
- `src/app/(planning)/planning/inventory-flow/supply/page.tsx` — page wrapper.
- `src/app/(planning)/planning/inventory-flow/supply/SupplyFlowClient.tsx` — client component, mirrors `InventoryFlowClient.tsx` minus planned-production overlay.
- `src/app/(planning)/planning/inventory-flow/supply/_lib/useSupplyFlow.ts` — TanStack hook.
- `src/app/(planning)/planning/inventory-flow/_components/InventoryFlowTabs.tsx` — shared tab nav.

### Files to MODIFY

**Backend:**
- `api/src/inventory/contracts.flow.ts` — extend `FlowItemSchema` with `sku_kind: z.enum(['ITEM','COMPONENT']).default('ITEM')` and relax `supply_method: z.string()` to `z.string().nullable()`. The FG handler will pass `sku_kind: 'ITEM'` and existing `supply_method` value.
- `api/src/inventory/handler.flow.ts` — set `sku_kind: 'ITEM'` on every FG response item (one-line addition in the row mapper).
- `api/src/inventory/route.ts` — register two new routes (`/supply-flow` and `/supply-flow/sku/:sku_kind/:sku_id`).

**Frontend:**
- `src/app/(planning)/planning/inventory-flow/_lib/types.ts` — add `sku_kind: 'ITEM' | 'COMPONENT'` to `FlowItem`; relax `supply_method` to `string | null`.
- `src/app/(planning)/planning/inventory-flow/InventoryFlowClient.tsx` — render `<InventoryFlowTabs activeTab='fg' />` at the top of the page.
- `src/app/(planning)/planning/inventory-flow/page.tsx` — no change required (server-side metadata only).

### Files to LEAVE UNTOUCHED (reused as-is)

`DayCell.tsx`, `DayHeaderRow.tsx`, `DayPopover.tsx`, `FilterBar.tsx`, `FlowGridDesktop.tsx`, `HeroBar.tsx`, `InsightsHero.tsx`, `MobileCardStream.tsx`, `MobileItemCard.tsx`, `Sparkline.tsx`, `StickyItemPanel.tsx`, `UnmappedSkusBanner.tsx`, `WeekCell.tsx`, `_lib/format.ts`, `_lib/risk.ts`, `_lib/family.ts`. (FilterBar's "family" chip will say "Class" effectively — the chip label is data-driven from the `family` field, which for components carries `component_class`. The semantics are equivalent enough for v1.)

---

## Chunk 2: Backend (DB + contracts + handler + route)

> Reference skills: @superpowers:test-driven-development, @superpowers:verification-before-completion. Every code change starts with a failing test or a verification command and ends with a green run before the commit step.

Working directory for this chunk: `C:/Users/tomw2/Projects/gt-factory-os/`.

---

### Task 1: DB migration 0146 — daily component-consumption helper (TDD start)

**Goal:** Create the helper `fn_explode_production_plan_to_daily_components(p_start, p_end)` that returns `(component_id, day, qty)` rows by walking PACK + BASE BOM for every non-cancelled `production_plan` row in the window. This is the **demand source** for the COMPONENT branch of the projection.

**Files:**
- Create: `db/migrations/0146_v_daily_supply_side_flow.sql` (helper function only in this task; full migration completed in Task 2 + 3)
- Create: `db/tests/0146_v_daily_supply_side_flow.test.sql` (helper tests in this task; projection tests added in Task 2; view tests in Task 3)

- [ ] **Step 1: Write the failing pgTAP tests for the helper**

Create `db/tests/0146_v_daily_supply_side_flow.test.sql` with this header + first three tests. Use `begin; … rollback;` so fixtures don't pollute the DB.

```sql
-- ===========================================================================
-- 0146_v_daily_supply_side_flow.test.sql
-- ===========================================================================
-- pgTAP tests for migration 0146:
--   * fn_explode_production_plan_to_daily_components(start, end)
--   * fn_compute_daily_supply_side_projection(start, end)
--   * api_read.v_daily_supply_side_flow
-- ===========================================================================

begin;
create extension if not exists pgtap;
select plan(12);   -- will grow as later tasks add tests
set search_path to private_core, public;

-- ---------------------------------------------------------------------------
-- Fixture: 1 manufactured FG, 1 base, 1 PACK BOM with 1 packaging line +
-- 1 BASE_BOM line, 1 base BOM with 1 raw line, 1 production_plan row.
-- ---------------------------------------------------------------------------
insert into private_core.components (component_id, component_name, component_class, status, inventory_uom)
  values ('PKG-BTL-1L', 'Bottle 1L', 'PKG', 'ACTIVE', 'EA'),
         ('RM-BASE-X',  'Base X',    'RM',  'ACTIVE', 'L');

insert into private_core.items (item_id, item_name, status, supply_method, sales_uom, primary_bom_head_id, base_bom_head_id)
  values ('FG-FRESH-1L', 'Fresh 1L', 'ACTIVE', 'MANUFACTURED', 'EA', 'BH-FRESH-PACK', 'BH-FRESH-BASE');

-- (insert bom_head + bom_version + bom_lines for PACK and BASE; pack output = 300, base output = 500L,
--  pack BASE_BOM line carries final_component_qty = 1L per pack output)

insert into private_core.production_plan (plan_date, item_id, planned_qty, status, base_bom_head_id, pack_manifest)
  values (current_date + 2, 'FG-FRESH-1L', 300, 'planned', null, '[]'::jsonb);  -- legacy/manual shape

select is(
  (select count(*) from private_core.fn_explode_production_plan_to_daily_components(current_date, current_date + 7)),
  2::bigint,
  'helper returns one row per leaf component (PKG-BTL-1L + RM-BASE-X) for the planned production'
);

select is(
  (select qty from private_core.fn_explode_production_plan_to_daily_components(current_date, current_date + 7)
            where component_id = 'PKG-BTL-1L'),
  300::private_core.qty_8dp,
  'PACK leaf qty = pack_output qty (300 bottles for 300 pack)'
);

select is(
  (select qty from private_core.fn_explode_production_plan_to_daily_components(current_date, current_date + 7)
            where component_id = 'RM-BASE-X'),
  300::private_core.qty_8dp,
  'BASE leaf qty = pack_output * (1L per pack / 1L per base) = 300L'
);

-- (further tests added in subsequent tasks)
rollback;
```

- [ ] **Step 2: Run tests; confirm they fail**

Run: `cd /c/Users/tomw2/Projects/gt-factory-os && pg_prove -d "$DATABASE_URL" db/tests/0146_v_daily_supply_side_flow.test.sql`
Expected: ERROR `function private_core.fn_explode_production_plan_to_daily_components(date, date) does not exist`.

- [ ] **Step 3: Write the helper function**

Create `db/migrations/0146_v_daily_supply_side_flow.sql` and add only the helper function for now (the projection function and view come in Tasks 2 and 3):

```sql
-- ===========================================================================
-- 0146_v_daily_supply_side_flow.sql
-- ===========================================================================
-- Supply-side Inventory Flow page: read-model for the COMPONENT (RM+PKG)
-- universe + BOUGHT_FINISHED items, paralleling 0144 (FG flow).
--
-- This migration installs three objects in dependency order:
--   1. fn_explode_production_plan_to_daily_components(start, end)
--   2. fn_compute_daily_supply_side_projection(start, end)
--   3. api_read.v_daily_supply_side_flow
--
-- Authority: docs/superpowers/plans/2026-05-06-supply-side-inventory-flow.md
-- ===========================================================================

begin;
set search_path to private_core, public;

-- ---------------------------------------------------------------------------
-- 1. fn_explode_production_plan_to_daily_components
-- ---------------------------------------------------------------------------
-- For every non-cancelled production_plan row in [start, end] walks PACK BOM
-- and (when applicable) BASE BOM and returns one row per leaf component, on
-- the plan_date (NOT plan_date+1 — consumption is on the production day).
--
-- Branches mirror migration 0145's union over (base-batch shape, manual shape):
--   * base-batch: base_bom_head_id IS NOT NULL, pack_manifest is jsonb array of
--     {item_id, qty}; iterate each pack element.
--   * manual:     base_bom_head_id IS NULL, item_id + planned_qty populated;
--                 use the row directly.
-- ---------------------------------------------------------------------------
create or replace function private_core.fn_explode_production_plan_to_daily_components(
  p_start date,
  p_end   date
) returns table (
  component_id text,
  day          date,
  qty          private_core.qty_8dp
)
language sql
stable
as $$
  with plans as (
    -- Branch 1 — base-batch shape (engine-output)
    select pp.plan_date as day, (pack ->> 'item_id')::text as fg_item_id,
           coalesce((pack ->> 'qty')::numeric, 0)::private_core.qty_8dp as fg_qty
    from private_core.production_plan pp,
         lateral jsonb_array_elements(pp.pack_manifest) as pack
    where pp.status in ('draft','planned','in_production')
      and pp.base_bom_head_id is not null
      and pp.plan_date between p_start and p_end
    union all
    -- Branch 2 — legacy/manual shape
    select pp.plan_date as day, pp.item_id as fg_item_id,
           pp.planned_qty::private_core.qty_8dp as fg_qty
    from private_core.production_plan pp
    where pp.status in ('draft','planned','in_production')
      and pp.base_bom_head_id is null
      and pp.item_id is not null
      and pp.plan_date between p_start and p_end
  ),
  pack_explosion as (
    -- For each (day, fg_item, fg_qty), walk the PACK BOM leaf lines.
    -- Component leaf: component_ref_type IN ('RAW_NAME','COMPONENT'), final_component_id NOT NULL.
    select p.day, bl.final_component_id as component_id,
           (p.fg_qty * bl.final_component_qty / bv.final_bom_output_qty)::private_core.qty_8dp as qty
    from plans p
    join private_core.items i        on i.item_id = p.fg_item_id
    join private_core.bom_version bv on bv.bom_head_id = i.primary_bom_head_id
                                    and bv.is_active   -- assumes single active version flag
    join private_core.bom_lines bl   on bl.bom_version_id = bv.bom_version_id
    where bl.component_ref_type in ('RAW_NAME','COMPONENT')
      and bl.final_component_id is not null
  ),
  base_explosion as (
    -- For each plan, find the PACK BOM's BASE_BOM line, compute total_base_units,
    -- then walk the BASE BOM leaf lines.
    with base_link as (
      select p.day, p.fg_qty,
             i.base_bom_head_id,
             bl.final_component_qty as base_l_per_pack,
             bv.final_bom_output_qty as pack_output
      from plans p
      join private_core.items i        on i.item_id = p.fg_item_id
      join private_core.bom_version bv on bv.bom_head_id = i.primary_bom_head_id and bv.is_active
      join private_core.bom_lines bl   on bl.bom_version_id = bv.bom_version_id
                                       and bl.component_ref_type = 'BASE_BOM'
      where i.base_bom_head_id is not null
    )
    select bl.day, bom_bl.final_component_id as component_id,
           ((bl.fg_qty * bl.base_l_per_pack / bl.pack_output)
              * bom_bl.final_component_qty / base_bv.final_bom_output_qty)::private_core.qty_8dp as qty
    from base_link bl
    join private_core.bom_version base_bv on base_bv.bom_head_id = bl.base_bom_head_id and base_bv.is_active
    join private_core.bom_lines   bom_bl  on bom_bl.bom_version_id = base_bv.bom_version_id
    where bom_bl.component_ref_type in ('RAW_NAME','COMPONENT')
      and bom_bl.final_component_id is not null
  )
  select component_id, day, sum(qty)::private_core.qty_8dp as qty
  from (select * from pack_explosion union all select * from base_explosion) u
  group by component_id, day;
$$;

comment on function private_core.fn_explode_production_plan_to_daily_components(date, date) is
  'Per-day leaf-component consumption from production_plan. Walks PACK BOM + BASE BOM (when applicable). Mirrors fn_explode_bom_to_components (0126) but per plan_date, not weekly bucket. Used by fn_compute_daily_supply_side_projection (this migration). status filter and union-of-shapes mirror migration 0145.';

commit;
```

> **Note:** The `bv.is_active` predicate above assumes a single-active-version flag on `bom_version`. The executor must verify the actual column name (likely `is_current` or `status='ACTIVE'`) by reading `db/migrations/0003_bom_three_table.sql` before running the tests. If the flag is named differently, adjust both calls. **Do not invent a column.**

- [ ] **Step 4: Re-run tests; confirm they pass**

Run: `pg_prove -d "$DATABASE_URL" db/tests/0146_v_daily_supply_side_flow.test.sql`
Expected: 3/3 passing (the helper assertions; placeholder count `plan(12)` will report under-run until later tasks).

- [ ] **Step 5: Commit**

```bash
git add db/migrations/0146_v_daily_supply_side_flow.sql db/tests/0146_v_daily_supply_side_flow.test.sql
git commit -m "feat(db): add fn_explode_production_plan_to_daily_components helper for supply-side inventory flow"
```

---

### Task 2: DB migration 0146 — projection function `fn_compute_daily_supply_side_projection`

**Goal:** Add the main projection function that returns one row per `(sku_kind, sku_id, day)` with all the columns the FG flow already produces (`demand_lionwheel_qty`, `demand_forecast_qty`, `demand_total_qty`, `incoming_supply_qty`, `projected_on_hand_eod`, `risk_tier`, `days_of_cover_at_day`, `effective_lead_time_days`, `is_working_day`, `holiday_name_he`).

**Files:**
- Modify: `db/migrations/0146_v_daily_supply_side_flow.sql` (append projection function before `commit;`)
- Modify: `db/tests/0146_v_daily_supply_side_flow.test.sql` (add tests after the helper tests)

- [ ] **Step 1: Add failing tests for the projection function**

Append before the `rollback;` line in the test file:

```sql
-- Test: COMPONENT branch returns rows for components with demand or supply.
select is(
  (select sku_kind from private_core.fn_compute_daily_supply_side_projection(current_date, current_date + 7)
            where sku_id = 'PKG-BTL-1L' and day = current_date + 2 limit 1),
  'COMPONENT',
  'COMPONENT branch labels sku_kind correctly'
);

select is(
  (select demand_total_qty from private_core.fn_compute_daily_supply_side_projection(current_date, current_date + 7)
            where sku_id = 'PKG-BTL-1L' and day = current_date + 2),
  300::private_core.qty_8dp,
  'COMPONENT branch demand_total_qty equals BOM-exploded consumption on plan_date'
);

-- Fixture: a BOUGHT_FINISHED item with a current_balance row.
insert into private_core.items (item_id, item_name, status, supply_method, sales_uom)
  values ('BF-WIDGET-1', 'Widget', 'ACTIVE', 'BOUGHT_FINISHED', 'EA');

insert into private_core.current_balances (site_id, item_type, item_id, calculated_on_hand)
  values ('DEFAULT', 'FG', 'BF-WIDGET-1', 50);

select is(
  (select sku_kind from private_core.fn_compute_daily_supply_side_projection(current_date, current_date + 1)
            where sku_id = 'BF-WIDGET-1' and day = current_date limit 1),
  'ITEM',
  'BOUGHT_FINISHED branch labels sku_kind = ITEM'
);

select is(
  (select projected_on_hand_eod from private_core.fn_compute_daily_supply_side_projection(current_date, current_date + 1)
            where sku_id = 'BF-WIDGET-1' and day = current_date),
  50::private_core.qty_8dp,
  'BOUGHT_FINISHED branch seeds on_hand from current_balances FG row'
);

-- Negative test: MANUFACTURED items must NOT appear (they belong to FG flow).
insert into private_core.items (item_id, item_name, status, supply_method, sales_uom)
  values ('FG-MANUF', 'Manuf', 'ACTIVE', 'MANUFACTURED', 'EA');

select is(
  (select count(*) from private_core.fn_compute_daily_supply_side_projection(current_date, current_date + 1)
            where sku_id = 'FG-MANUF'),
  0::bigint,
  'MANUFACTURED items are excluded from supply-side projection'
);
```

Update `select plan(12);` to match the actual count after additions.

- [ ] **Step 2: Run; confirm failures**

Run: `pg_prove -d "$DATABASE_URL" db/tests/0146_v_daily_supply_side_flow.test.sql`
Expected: ERROR `function private_core.fn_compute_daily_supply_side_projection(date, date) does not exist`.

- [ ] **Step 3: Implement the projection function**

Append to `db/migrations/0146_v_daily_supply_side_flow.sql` before `commit;`:

```sql
-- ---------------------------------------------------------------------------
-- 2. fn_compute_daily_supply_side_projection
-- ---------------------------------------------------------------------------
-- Single source of truth for daily on-hand math on the supply universe:
--   sku_kind='COMPONENT' for private_core.components (RM + PKG)
--   sku_kind='ITEM'      for private_core.items WHERE supply_method='BOUGHT_FINISHED'
--
-- Returns one row per (sku_kind, sku_id, day) over [p_start, p_end].
--
-- Demand model:
--   COMPONENT: BOM consumption from fn_explode_production_plan_to_daily_components.
--   ITEM:      LionWheel + forecast (mirrors fn_compute_daily_fg_projection demand model;
--              same orders_mirror_lines.pickup_at + planning_demand disaggregation).
-- Supply model:
--   COMPONENT: SUM(open_qty) from purchase_order_lines.component_id, on expected_receive_date.
--   ITEM:      SUM(open_qty) from purchase_order_lines.item_id, on expected_receive_date.
-- Seed on-hand:
--   COMPONENT: SUM current_balances WHERE item_type IN ('RM','PKG') AND item_id = component_id.
--   ITEM:      SUM current_balances WHERE item_type = 'FG' AND item_id = item.item_id.
--
-- Status filter for items.status / components.status: only 'ACTIVE'.
-- Risk tier model: same Hybrid D as fn_compute_daily_fg_projection.
-- ---------------------------------------------------------------------------
create or replace function private_core.fn_compute_daily_supply_side_projection(
  p_start date,
  p_end   date
) returns table (
  sku_kind                  text,
  sku_id                    text,
  day                       date,
  is_working_day            boolean,
  holiday_name_he           text,
  demand_lionwheel_qty      private_core.qty_8dp,
  demand_forecast_qty       private_core.qty_8dp,
  demand_total_qty          private_core.qty_8dp,
  incoming_supply_qty       private_core.qty_8dp,
  projected_on_hand_eod     private_core.qty_8dp,
  risk_tier                 text,
  days_of_cover_at_day      private_core.qty_8dp,
  effective_lead_time_days  integer
)
language plpgsql
stable
as $$
declare
  ...  -- see below for body
begin
  -- The body is structurally a UNION ALL between two CTEs:
  --   * component_universe: keys = (component_id, day in days)
  --   * bf_item_universe:   keys = (item_id, day in days)
  -- For each universe:
  --   1. Build a calendar (days BETWEEN p_start AND p_end).
  --   2. Compute demand per day (per universe rule above).
  --   3. Compute supply per day (per universe rule above).
  --   4. Compute seed_on_hand (single value per SKU).
  --   5. Compute projected_on_hand_eod via a window function:
  --        seed + cumulative SUM(supply - demand) ORDER BY day.
  --   6. Compute days_of_cover_at_day via correlated lookahead
  --      (mirrors fn_compute_daily_fg_projection lines that handle this).
  --   7. Compute risk_tier from days_of_cover vs effective_lead_time_days.
  -- Return UNION ALL of both universes.
  --
  -- The exact body should be modeled on db/migrations/0097_fn_compute_daily_fg_projection.sql
  -- (the FG projection function). The executor must read 0097 in full before writing
  -- this body — the `is_working_day` / `holiday_name_he` calendar join, the cumulative
  -- on-hand window, and the days_of_cover lookahead all have specific patterns that
  -- the supply-side function must mirror to keep risk-tier semantics aligned.
  return query
  with ... -- (executor: write the full SQL here, mirroring 0097)
  ;
end
$$;

comment on function private_core.fn_compute_daily_supply_side_projection(date, date) is
  'Daily projection for the supply universe (components + BOUGHT_FINISHED items). Sister of fn_compute_daily_fg_projection (0097). Risk tier model identical (Hybrid D). Demand model differs per branch: COMPONENT = BOM consumption, ITEM = LionWheel+forecast.';
```

> **Implementation directive for the executor:** read `db/migrations/0097_fn_compute_daily_fg_projection.sql` end-to-end **before** writing this body. The function must be a strict generalization — every column the FG function emits must be emitted here, with identical rounding and identical risk-tier thresholds. Differences are limited to the demand-source CTEs and the seed_on_hand CTE.

- [ ] **Step 4: Re-run; confirm pass**

Run: `pg_prove -d "$DATABASE_URL" db/tests/0146_v_daily_supply_side_flow.test.sql`
Expected: all helper + projection tests pass.

- [ ] **Step 5: Commit**

```bash
git add db/migrations/0146_v_daily_supply_side_flow.sql db/tests/0146_v_daily_supply_side_flow.test.sql
git commit -m "feat(db): add fn_compute_daily_supply_side_projection (COMPONENT + BOUGHT_FINISHED)"
```

---

### Task 3: DB migration 0146 — view `api_read.v_daily_supply_side_flow`

**Goal:** Decorate the projection function with master-data fields (`sku_name`, `family`, `supply_method`, `status`) so the API handler can render UI rows without a second master join.

**Files:**
- Modify: `db/migrations/0146_v_daily_supply_side_flow.sql` (append view before `commit;`)
- Modify: `db/tests/0146_v_daily_supply_side_flow.test.sql` (add view smoke tests)

- [ ] **Step 1: Add failing view smoke tests**

```sql
-- View shape: shipped column list matches contract.
select is(
  (select count(*) from information_schema.columns
     where table_schema = 'api_read' and table_name = 'v_daily_supply_side_flow'),
  17::bigint,
  'view exposes 17 columns (13 from projection + sku_name + family + supply_method + status)'
);

-- COMPONENT row carries component_class as `family`.
select is(
  (select family from api_read.v_daily_supply_side_flow
            where sku_id = 'PKG-BTL-1L' and day = current_date + 2 limit 1),
  'PKG',
  'view maps components.component_class -> family for COMPONENT rows'
);

-- ITEM row carries items.supply_method.
select is(
  (select supply_method from api_read.v_daily_supply_side_flow
            where sku_id = 'BF-WIDGET-1' and day = current_date limit 1),
  'BOUGHT_FINISHED',
  'view passes items.supply_method through for ITEM rows'
);
```

- [ ] **Step 2: Run; confirm failure**

Expected: ERROR `relation api_read.v_daily_supply_side_flow does not exist`.

- [ ] **Step 3: Append the view definition**

Append to migration:

```sql
-- ---------------------------------------------------------------------------
-- 3. api_read.v_daily_supply_side_flow
-- ---------------------------------------------------------------------------
create or replace view api_read.v_daily_supply_side_flow as
with proj as (
  select * from private_core.fn_compute_daily_supply_side_projection(
    current_date, (current_date + interval '14 days')::date
  )
)
select
  p.sku_kind,
  p.sku_id,
  case p.sku_kind
    when 'COMPONENT' then c.component_name
    when 'ITEM'      then i.item_name
  end as sku_name,
  case p.sku_kind
    when 'COMPONENT' then c.component_class
    when 'ITEM'      then null::text  -- BOUGHT_FINISHED items have no `family` analog; portal renders supply_method
  end as family,
  case p.sku_kind
    when 'COMPONENT' then null::text
    when 'ITEM'      then i.supply_method
  end as supply_method,
  case p.sku_kind
    when 'COMPONENT' then c.status
    when 'ITEM'      then i.status
  end as status,
  p.day, p.is_working_day, p.holiday_name_he,
  p.demand_lionwheel_qty, p.demand_forecast_qty, p.demand_total_qty,
  p.incoming_supply_qty, p.projected_on_hand_eod, p.risk_tier,
  p.days_of_cover_at_day, p.effective_lead_time_days
from proj p
left join private_core.components c on p.sku_kind = 'COMPONENT' and c.component_id = p.sku_id
left join private_core.items      i on p.sku_kind = 'ITEM'      and i.item_id      = p.sku_id
where (p.sku_kind = 'COMPONENT' and c.status = 'ACTIVE')
   or (p.sku_kind = 'ITEM'      and i.status = 'ACTIVE' and i.supply_method = 'BOUGHT_FINISHED');

comment on view api_read.v_daily_supply_side_flow is
  '14-day daily supply-side projection. Sister to api_read.v_daily_inventory_flow (FG). Decorates fn_compute_daily_supply_side_projection with master-data fields. ACTIVE-only, BOUGHT_FINISHED-only on the ITEM branch.';
```

- [ ] **Step 4: Re-run all tests; confirm pass**

Run: `pg_prove -d "$DATABASE_URL" db/tests/0146_v_daily_supply_side_flow.test.sql`
Expected: all tests pass; the planned `plan(12)` (or whatever count is final) is honored.

- [ ] **Step 5: Apply the migration to the dev DB and re-run the gauntlet**

Run: `cd /c/Users/tomw2/Projects/gt-factory-os && bash scripts/db-apply.sh 0146` (or whatever wrapper the repo uses; see `db/README.md` for the canonical apply command). Then run `bash scripts/db-test.sh` to ensure no regressions in the rest of the test suite.
Expected: ALL pgTAP tests still pass (parity tests, anchors tests, ledger tests).

- [ ] **Step 6: Commit**

```bash
git add db/migrations/0146_v_daily_supply_side_flow.sql db/tests/0146_v_daily_supply_side_flow.test.sql
git commit -m "feat(db): add api_read.v_daily_supply_side_flow view (COMPONENT + BOUGHT_FINISHED)"
```

---

### Task 4: Extend `FlowItemSchema` with `sku_kind` (backwards-compatible)

**Goal:** Add the one new field the supply response needs, without breaking the FG endpoint or the existing portal.

**Files:**
- Modify: `api/src/inventory/contracts.flow.ts` (one schema line addition + nullable)
- Modify: `api/src/inventory/handler.flow.ts` (set `sku_kind: 'ITEM'` on emitted rows)
- Test: existing `api/src/inventory/handler.flow.test.ts` (or create one if absent — the executor must check; the FG handler currently has **no** test file per `ls` output, so a smoke test is added in this task)

- [ ] **Step 1: Write a Vitest smoke test that asserts the new field**

Create `api/src/inventory/handler.flow.test.ts`:

```ts
import { describe, it, expect } from 'vitest';
import { FlowItemSchema, FlowResponseSchema } from './contracts.flow.js';

describe('FlowItemSchema', () => {
  it('accepts sku_kind="ITEM" and nullable supply_method', () => {
    const ok = FlowItemSchema.safeParse({
      item_id: 'X', item_name: 'X', family: null,
      supply_method: null, sku_kind: 'ITEM',
      risk_tier: 'healthy', days_of_cover: 99,
      effective_lead_time_days: 14, current_on_hand: 10,
      earliest_stockout_date: null,
      stockout_at_day_with_production: null,
      days_cover_with_production: 56,
      days: [], weeks: [],
    });
    expect(ok.success).toBe(true);
  });

  it('defaults sku_kind to ITEM when omitted (FG endpoint backwards compat)', () => {
    const parsed = FlowItemSchema.safeParse({
      item_id: 'X', item_name: 'X', family: null,
      supply_method: 'MANUFACTURED',
      risk_tier: 'healthy', days_of_cover: 99,
      effective_lead_time_days: 14, current_on_hand: 10,
      earliest_stockout_date: null,
      stockout_at_day_with_production: null,
      days_cover_with_production: 56,
      days: [], weeks: [],
    });
    expect(parsed.success).toBe(true);
    if (parsed.success) expect(parsed.data.sku_kind).toBe('ITEM');
  });
});
```

- [ ] **Step 2: Run; confirm failure**

Run: `cd /c/Users/tomw2/Projects/gt-factory-os/api && npx vitest run src/inventory/handler.flow.test.ts`
Expected: parse fails — `sku_kind` not in schema, `supply_method` not nullable.

- [ ] **Step 3: Edit `contracts.flow.ts`**

In `FlowItemSchema` (around line 120):

```ts
// Was:
//   supply_method: z.string(),
// Now:
   supply_method: z.string().nullable(),
   sku_kind: z.enum(['ITEM', 'COMPONENT']).default('ITEM'),
```

- [ ] **Step 4: Run; confirm pass**

Expected: 2/2 passing.

- [ ] **Step 5: Update FG handler to set `sku_kind: 'ITEM'`**

In `handler.flow.ts`, locate the row mapper that builds each `FlowItem` (search for `family:` to find it) and add `sku_kind: 'ITEM' as const,` to the object literal. Re-run the test to confirm still green.

- [ ] **Step 6: Commit**

```bash
git add api/src/inventory/contracts.flow.ts api/src/inventory/handler.flow.ts api/src/inventory/handler.flow.test.ts
git commit -m "feat(api): extend FlowItemSchema with sku_kind for supply-side flow"
```

---

### Task 5: Create `contracts.supply_flow.ts`

**Goal:** Define the supply-flow query schema (which differs slightly from FG — `family` filter is `component_class` semantically; no `supply_method` filter on the wire because COMPONENT rows have `supply_method=null`) and the per-SKU drill-down schema (which differs in shape: COMPONENT detail shows BOM consumption events instead of LionWheel orders).

**Files:**
- Create: `api/src/inventory/contracts.supply_flow.ts`

- [ ] **Step 1: Write the failing parser test**

Append to `handler.flow.test.ts` (or create `handler.supply_flow.test.ts` if cleaner):

```ts
import { SupplyFlowQuerySchema, SupplyFlowItemDetailSchema } from './contracts.supply_flow.js';

describe('SupplyFlowQuerySchema', () => {
  it('accepts at_risk_only and family but not supply_method', () => {
    const ok = SupplyFlowQuerySchema.safeParse({ at_risk_only: 'true', family: 'PKG' });
    expect(ok.success).toBe(true);
  });
});

describe('SupplyFlowItemDetailSchema', () => {
  it('requires sku_kind on the header', () => {
    const bad = SupplyFlowItemDetailSchema.safeParse({
      as_of: new Date().toISOString(),
      sku: { sku_id: 'X', sku_name: 'X', family: null, supply_method: null, status: 'ACTIVE', current_on_hand: 0 },
      pos: [], consumptions: [], orders: [],
    });
    expect(bad.success).toBe(false);
  });
});
```

- [ ] **Step 2: Run; confirm failure (module not found)**

- [ ] **Step 3: Create the contract**

```ts
// api/src/inventory/contracts.supply_flow.ts
import { z } from 'zod';
import { FlowDaySchema, FlowWeekSchema, FlowSummarySchema, FlowItemPoSchema, FlowItemOrderSchema } from './contracts.flow.js';

// Query — no supply_method (COMPONENT rows have null), `family` is reused.
export const SupplyFlowQuerySchema = z.object({
  start: z.string().date().optional(),
  horizon_weeks: z.coerce.number().int().min(1).max(12).default(8),
  family: z.string().optional(),       // component_class or items.family
  at_risk_only: z.coerce.boolean().default(false),
});
export type SupplyFlowQuery = z.infer<typeof SupplyFlowQuerySchema>;

// Per-SKU header on drill-down.
export const SupplyFlowSkuHeaderSchema = z.object({
  sku_kind: z.enum(['ITEM','COMPONENT']),
  sku_id: z.string(),
  sku_name: z.string(),
  family: z.string().nullable(),
  supply_method: z.string().nullable(),
  status: z.string(),
  current_on_hand: z.number(),
});

// COMPONENT-only: planned BOM consumption row.
export const SupplyFlowConsumptionSchema = z.object({
  plan_date: z.string().date(),
  fg_item_id: z.string(),
  fg_item_name: z.string(),
  qty: z.number(),
});

// Drill-down response: pos[] (always), orders[] (only ITEM/BOUGHT_FINISHED), consumptions[] (only COMPONENT).
export const SupplyFlowItemDetailSchema = z.object({
  as_of: z.string().datetime(),
  sku: SupplyFlowSkuHeaderSchema,
  pos: z.array(FlowItemPoSchema),
  orders: z.array(FlowItemOrderSchema),       // empty array for COMPONENT
  consumptions: z.array(SupplyFlowConsumptionSchema), // empty array for ITEM
});
export type SupplyFlowItemDetail = z.infer<typeof SupplyFlowItemDetailSchema>;
```

- [ ] **Step 4: Run; confirm pass**

- [ ] **Step 5: Commit**

```bash
git add api/src/inventory/contracts.supply_flow.ts api/src/inventory/handler.flow.test.ts
git commit -m "feat(api): add SupplyFlowQuerySchema + SupplyFlowItemDetailSchema contracts"
```

---

### Task 6: Create `handler.supply_flow.ts`

**Goal:** Mirror `handler.flow.ts` but read from `api_read.v_daily_supply_side_flow` and emit `FlowResponse` with each `FlowItem` carrying `sku_kind`. Reuse `flow-cache.ts` for SWR (separate cache key namespace).

**Files:**
- Create: `api/src/inventory/handler.supply_flow.ts`
- Modify: `api/src/inventory/handler.flow.test.ts` (add handler smoke test that mocks Db and asserts auth gate + payload shape)

- [ ] **Step 1: Write the auth-gate failing test**

```ts
import { handleSupplyFlow } from './handler.supply_flow.js';
import { AuthError } from '../auth/session.js';

describe('handleSupplyFlow auth gate', () => {
  it('rejects viewer role with 403', async () => {
    const stubDb = {} as any;
    const session = { user_id: 'u', role: 'viewer' as const };
    await expect(
      handleSupplyFlow(stubDb, session, { horizon_weeks: 8, at_risk_only: false }),
    ).rejects.toBeInstanceOf(AuthError);
  });
});
```

- [ ] **Step 2: Run; confirm failure (module not found)**

- [ ] **Step 3: Implement `handler.supply_flow.ts`**

Mirror `handler.flow.ts` structurally:
- `roleAllowsInventoryFlowRead` import + reuse (do not duplicate).
- `flowCache` from `flow-cache.ts` — but with a separate cache key namespace (e.g., prefix `supply|`).
- `computeSupplyFlow(db, query)`:
  - Read `api_read.v_daily_supply_side_flow` ordered by (sku_kind, sku_id, day).
  - Group rows into `FlowItem` objects keyed by `(sku_kind, sku_id)`.
  - For weekly rollup (weeks 3–8), call `fn_compute_daily_supply_side_projection(current_date, current_date + 55 days)` directly (mirrors how `handler.flow.ts` does the FG weekly query).
  - Compute `current_on_hand` from `current_balances` (UNION over RM/PKG and FG-BOUGHT_FINISHED).
  - Compute summary: `at_risk_count`, `earliest_stockout`, `open_orders_count` (always 0 for v1 — no LionWheel context for supply universe; placeholder), `exceptions_count` (0 for v1; later: PO-related exceptions).
  - Always set `sku_kind` from the row; set `cell_tier_with_production` = `tier` (no overlay in v1); set `stockout_at_day_with_production` = `earliest_stockout_date`; set `days_cover_with_production` = `days_of_cover`.
- `handleSupplyFlow(db, session, query)`: auth gate → cache lookup → return.
- `handleSupplyFlowSkuDetail(db, session, skuKind, skuId)`: queries `purchase_order_lines` for `pos[]` (filtered by `sku_kind`-appropriate column), `production_plan` + BOM explosion for `consumptions[]` (when COMPONENT), `orders_mirror_lines` for `orders[]` (when ITEM/BOUGHT_FINISHED, identical query to FG drill-down).

> **Implementation directive:** structurally mirror `handler.flow.ts` line-by-line. Do not introduce a new abstraction. The two handlers stay parallel so future maintenance touches both files together.

- [ ] **Step 4: Run; confirm pass**

- [ ] **Step 5: Commit**

```bash
git add api/src/inventory/handler.supply_flow.ts api/src/inventory/handler.flow.test.ts
git commit -m "feat(api): add handleSupplyFlow + handleSupplyFlowSkuDetail handlers"
```

---

### Task 7: Register routes in `api/src/inventory/route.ts`

**Goal:** Wire `GET /api/v1/queries/inventory/supply-flow` and `GET /api/v1/queries/inventory/supply-flow/sku/:sku_kind/:sku_id`.

**Files:**
- Modify: `api/src/inventory/route.ts`
- Test: `api/src/inventory/route.test.ts` (or extend the handler test file with a Fastify smoke test if a route test file doesn't exist)

- [ ] **Step 1: Write a failing Fastify integration test**

Create `api/src/inventory/route.test.ts`:

```ts
import { describe, it, expect } from 'vitest';
import Fastify from 'fastify';
import { registerInventoryRoute } from './route.js';

describe('GET /api/v1/queries/inventory/supply-flow', () => {
  it('exists and returns 401 without auth', async () => {
    const app = Fastify();
    const fakeDb = {} as any;
    const fakeExtract = async () => { throw Object.assign(new Error('unauth'), { statusCode: 401 }); };
    registerInventoryRoute(app, { db: fakeDb, extractSession: fakeExtract as any });
    const res = await app.inject({ method: 'GET', url: '/api/v1/queries/inventory/supply-flow' });
    expect(res.statusCode).toBe(401);
  });
});
```

- [ ] **Step 2: Run; confirm 404 (route not registered)**

- [ ] **Step 3: Add route registrations**

In `route.ts`, mirror the existing `/inventory/flow` block. Add imports at top:

```ts
import { SupplyFlowQuerySchema } from './contracts.supply_flow.js';
import { handleSupplyFlow, handleSupplyFlowSkuDetail } from './handler.supply_flow.js';
```

Add two `app.get` blocks at the end of `registerInventoryRoute`, structurally identical to the FG flow + drill-down blocks but using the supply schemas/handlers. The drill-down route shape: `/api/v1/queries/inventory/supply-flow/sku/:sku_kind/:sku_id`. Validate `sku_kind` against the literal set `{'ITEM','COMPONENT'}` before calling the handler; reject with 422 if invalid.

- [ ] **Step 4: Run; confirm 401**

- [ ] **Step 5: Commit**

```bash
git add api/src/inventory/route.ts api/src/inventory/route.test.ts
git commit -m "feat(api): register supply-flow and supply-flow/sku routes"
```

---

## Chunk 3: Frontend (proxy + page + client + tab nav)

> Reference skills: @superpowers:test-driven-development, @superpowers:verification-before-completion, @feature-dev:frontend-design (for the tab nav visual). Working directory for this chunk: `C:/Users/tomw2/Projects/window2-portal-sandbox/`.

---

### Task 8: Next.js API proxies

**Goal:** Proxy the new Fastify routes through the portal so the browser hits same-origin endpoints.

**Files:**
- Create: `src/app/api/inventory/supply-flow/route.ts`
- Create: `src/app/api/inventory/supply-flow/sku/[skuKind]/[skuId]/route.ts`

- [ ] **Step 1: Write the proxies**

`src/app/api/inventory/supply-flow/route.ts`:

```ts
import { proxyRequest } from "@/lib/api-proxy";

// GET /api/inventory/supply-flow → upstream /api/v1/queries/inventory/supply-flow.
// Same SWR cache headers as /api/inventory/flow.
export async function GET(req: Request): Promise<Response> {
  const res = await proxyRequest(req, {
    method: "GET",
    upstreamPath: "/api/v1/queries/inventory/supply-flow",
    forwardQuery: true,
    errorLabel: "supply flow",
  });
  if (res.ok) {
    res.headers.set("Cache-Control", "private, max-age=30, stale-while-revalidate=60");
  }
  return res;
}
```

`src/app/api/inventory/supply-flow/sku/[skuKind]/[skuId]/route.ts`:

```ts
import { proxyRequest } from "@/lib/api-proxy";

// GET /api/inventory/supply-flow/sku/[skuKind]/[skuId]
//   → /api/v1/queries/inventory/supply-flow/sku/{skuKind}/{skuId}.
export async function GET(
  req: Request,
  { params }: { params: Promise<{ skuKind: string; skuId: string }> },
): Promise<Response> {
  const { skuKind, skuId } = await params;
  return proxyRequest(req, {
    method: "GET",
    upstreamPath: `/api/v1/queries/inventory/supply-flow/sku/${encodeURIComponent(skuKind)}/${encodeURIComponent(skuId)}`,
    forwardQuery: false,
    errorLabel: "supply flow detail",
  });
}
```

- [ ] **Step 2: Verify the proxies start**

Run: `cd /c/Users/tomw2/Projects/window2-portal-sandbox && npm run dev`
Then `curl -i http://localhost:3000/api/inventory/supply-flow` (no auth) — expected 401 from upstream once it's running. If upstream is down, the proxy must return a 502 with `errorLabel`. Confirm the route file is hit (no 404).

- [ ] **Step 3: Commit**

```bash
git add src/app/api/inventory/supply-flow
git commit -m "feat(portal): add /api/inventory/supply-flow proxy routes"
```

---

### Task 9: Update FG types — add `sku_kind` to `FlowItem`

**Goal:** Keep the portal type system aligned with the extended Zod contract from Task 4.

**Files:**
- Modify: `src/app/(planning)/planning/inventory-flow/_lib/types.ts`

- [ ] **Step 1: Read the file**

Open `_lib/types.ts` and find the `FlowItem` interface.

- [ ] **Step 2: Edit the interface**

Add:
```ts
sku_kind: 'ITEM' | 'COMPONENT';
```
And change:
```ts
// was
supply_method: 'MANUFACTURED' | 'BOUGHT_FINISHED' | 'REPACK';
// becomes
supply_method: 'MANUFACTURED' | 'BOUGHT_FINISHED' | 'REPACK' | null;
```

- [ ] **Step 3: Type-check**

Run: `cd /c/Users/tomw2/Projects/window2-portal-sandbox && npm run typecheck`
Expected: PASS. If anything in the existing FG components reads `supply_method` non-null, fix the call site (defensive `?? 'ITEM'` or similar).

- [ ] **Step 4: Commit**

```bash
git add src/app/(planning)/planning/inventory-flow/_lib/types.ts
git commit -m "feat(portal): add sku_kind to FlowItem type; relax supply_method"
```

---

### Task 10: Create `InventoryFlowTabs` shared nav component

**Goal:** A small two-tab segmented control rendered at the top of both pages, persisting the current tab in the URL via Next link navigation.

**Files:**
- Create: `src/app/(planning)/planning/inventory-flow/_components/InventoryFlowTabs.tsx`

- [ ] **Step 1: Write the component**

```tsx
"use client";

import Link from "next/link";
import { cn } from "@/lib/cn";

type Tab = "fg" | "supply";

export function InventoryFlowTabs({ activeTab }: { activeTab: Tab }) {
  return (
    <nav
      role="tablist"
      aria-label="Inventory flow view"
      className="inline-flex rounded-md border border-border bg-muted p-0.5 text-sm"
    >
      <Link
        role="tab"
        aria-selected={activeTab === "fg"}
        href="/planning/inventory-flow"
        className={cn(
          "px-3 py-1.5 rounded-sm font-medium transition-colors",
          activeTab === "fg"
            ? "bg-background text-foreground shadow-sm"
            : "text-muted-foreground hover:text-foreground",
        )}
      >
        Finished Goods
      </Link>
      <Link
        role="tab"
        aria-selected={activeTab === "supply"}
        href="/planning/inventory-flow/supply"
        className={cn(
          "px-3 py-1.5 rounded-sm font-medium transition-colors",
          activeTab === "supply"
            ? "bg-background text-foreground shadow-sm"
            : "text-muted-foreground hover:text-foreground",
        )}
      >
        Supply (RM + Bought-Finished)
      </Link>
    </nav>
  );
}
```

> **Visual reference:** match the segmented control already in use elsewhere in the planning module (search the codebase for `role="tablist"` to locate one; if none, this design is the new house style).

- [ ] **Step 2: Mount in FG client**

Edit `InventoryFlowClient.tsx`. Near the top of the JSX (above `<WorkflowHeader />` or alongside it), insert:

```tsx
import { InventoryFlowTabs } from "./_components/InventoryFlowTabs";
// ...
<div className="mb-3"><InventoryFlowTabs activeTab="fg" /></div>
```

- [ ] **Step 3: Verify in dev**

Run dev server, navigate to `/planning/inventory-flow`, confirm the tab nav renders with "Finished Goods" highlighted.

- [ ] **Step 4: Commit**

```bash
git add src/app/(planning)/planning/inventory-flow/_components/InventoryFlowTabs.tsx \
        src/app/(planning)/planning/inventory-flow/InventoryFlowClient.tsx
git commit -m "feat(portal): add InventoryFlowTabs and mount on FG page"
```

---

### Task 11: Create `useSupplyFlow` hook

**Goal:** TanStack Query hook that mirrors `useInventoryFlow` but hits the supply endpoint. Same SWR characteristics (30s staleTime, 60s refetchInterval).

**Files:**
- Create: `src/app/(planning)/planning/inventory-flow/supply/_lib/useSupplyFlow.ts`

- [ ] **Step 1: Write it**

Mirror `useInventoryFlow.ts` (read it first). Differences:
- Endpoint: `/api/inventory/supply-flow`
- Query key: `["inventory", "supply-flow", params]`
- Same params type `FlowQueryParams` (no `supply_method`).

- [ ] **Step 2: Type-check**

Run: `npm run typecheck`. PASS expected.

- [ ] **Step 3: Commit**

```bash
git add src/app/(planning)/planning/inventory-flow/supply/_lib/useSupplyFlow.ts
git commit -m "feat(portal): add useSupplyFlow TanStack hook"
```

---

### Task 12: Create the supply page (`page.tsx` + `SupplyFlowClient.tsx`)

**Goal:** Mount the supply view at `/planning/inventory-flow/supply`. Mirror the FG client minus planned-overlay machinery.

**Files:**
- Create: `src/app/(planning)/planning/inventory-flow/supply/page.tsx`
- Create: `src/app/(planning)/planning/inventory-flow/supply/SupplyFlowClient.tsx`

- [ ] **Step 1: Page wrapper**

```tsx
// src/app/(planning)/planning/inventory-flow/supply/page.tsx
import type { Metadata } from "next";
import { SupplyFlowClient } from "./SupplyFlowClient";

export const metadata: Metadata = {
  title: "Supply Flow — GT Factory OS",
  description: "Daily projection for raw materials, packaging, and bought-finished items.",
};

export default function SupplyFlowPage() {
  return <SupplyFlowClient />;
}
```

- [ ] **Step 2: Client component**

`SupplyFlowClient.tsx` mirrors `InventoryFlowClient.tsx` with these deletions/changes:
- Remove imports for `PlannedFooterCaveat`, `PlannedOverlayToggle`, `usePlannedOverlayEnabled`, `usePlannedInflow`, `indexByItemDate`. The supply view does **not** show the planned-production overlay in v1.
- Replace `useInventoryFlow` import with `useSupplyFlow`.
- Render `<InventoryFlowTabs activeTab="supply" />` at the top.
- Title in `WorkflowHeader`: "Supply Flow"; description: "Raw materials + bought-finished daily projection".
- Pass the same `FlowItem[]` to `FlowGridDesktop` and `MobileCardStream` (they read shape-agnostic fields).
- The drill-down link from each row should route to `/planning/inventory-flow/supply/sku/{sku_kind}/{sku_id}` (drill-down page deferred to v2 — for v1, leave the link as `#` or to a stub page that says "Drill-down coming soon").

> **YAGNI note:** the per-SKU drill-down page is **deferred to v2**. The contract + handler are already in place from Tasks 5 + 6, but the portal page that renders them is not in this plan. Tom's brief said "build it quickly" — drill-down for the supply universe was not part of the explicit ask.

- [ ] **Step 3: Verify in dev**

Run dev server. Navigate to `/planning/inventory-flow/supply`. Confirm:
- Tab nav shows "Supply" highlighted.
- Grid renders rows for COMPONENT and BOUGHT_FINISHED items (assuming the dev DB has fixtures — if empty, the page should show `EmptyState`).
- Switching to the FG tab and back works.
- No console errors.

- [ ] **Step 4: Manual smoke (Playwright optional)**

If a Playwright config exists in the repo, add a smoke test that loads `/planning/inventory-flow/supply` and asserts the tab nav + at least one grid row OR the EmptyState. Otherwise, document the manual smoke steps in the commit message.

- [ ] **Step 5: Commit**

```bash
git add src/app/(planning)/planning/inventory-flow/supply
git commit -m "feat(portal): add /planning/inventory-flow/supply page (RM + bought-finished)"
```

---

## Chunk 4: End-to-end verification + acceptance gate

> Reference skills: @superpowers:verification-before-completion. No "✅ done" claims without a green run captured in the commit message or in the acceptance log.

---

### Task 13: Run the full local gauntlet

**Goal:** Confirm the new code does not break any existing test surface.

- [ ] **Step 1: DB tests**

```bash
cd /c/Users/tomw2/Projects/gt-factory-os
bash scripts/db-test.sh    # or the canonical pgTAP runner; check db/README.md
```
Expected: ALL tests pass, including the new 0146 file.

- [ ] **Step 2: API unit tests**

```bash
cd /c/Users/tomw2/Projects/gt-factory-os/api
npx vitest run
```
Expected: PASS, including the new tests in `handler.flow.test.ts`, `route.test.ts`, and any new files added in Tasks 4–7.

- [ ] **Step 3: API typecheck + build**

```bash
npx tsc -p tsconfig.json --noEmit
npm run build
```
Expected: PASS.

- [ ] **Step 4: Portal typecheck + build**

```bash
cd /c/Users/tomw2/Projects/window2-portal-sandbox
npm run typecheck
npm run build
```
Expected: PASS.

- [ ] **Step 5: Manual smoke against a real DB**

Apply migration 0146 to the dev DB, restart the API, restart the portal dev server. In a browser:
1. Visit `/planning/inventory-flow` — confirm tab nav, FG view still works.
2. Click "Supply" tab — confirm new view loads without errors.
3. Confirm at least one COMPONENT row and one BOUGHT_FINISHED ITEM row appear (assuming fixtures exist; otherwise confirm EmptyState).
4. Toggle "At risk only" on/off — confirm it filters.
5. Open browser devtools network tab — confirm `/api/inventory/supply-flow` returns 200 with valid JSON conforming to `FlowResponseSchema`.

- [ ] **Step 6: Commit if any fixes were needed; otherwise just record the verification.**

If Steps 1–5 surfaced bugs, fix them in dedicated sub-commits referencing the failing assertion. Do **not** mark this task complete until every step is green.

---

### Task 14: Update CURRENT_STATE.md and ACTIVE_NOW.md

**Goal:** Record the new surface in the authority docs so future sessions know it exists.

**Files:**
- Modify: `c:/Users/tomw2/GTeveryday Dropbox/Data Center/Tom/AI Agents & Projects/Code Agents/PRODUCTION/CURRENT_STATE.md`
- Modify: `c:/Users/tomw2/GTeveryday Dropbox/Data Center/Tom/AI Agents & Projects/Code Agents/PRODUCTION/ACTIVE_NOW.md`

- [ ] **Step 1: Read both files**

Identify the section that lists shipped surfaces (look for "inventory-flow" or "Inventory Flow" headings).

- [ ] **Step 2: Add a one-line entry**

Under the existing FG flow entry, add a sibling line: `Supply Flow page (/planning/inventory-flow/supply) — RM + PKG components + BOUGHT_FINISHED items; daily 14d band + 6w weekly tail; covered by migration 0146 + supply-flow API; v1 has no planned-overlay and no per-SKU drill-down page.`

- [ ] **Step 3: Commit**

```bash
git -C "c:/Users/tomw2/GTeveryday Dropbox/Data Center/Tom/AI Agents & Projects/Code Agents/PRODUCTION" add CURRENT_STATE.md ACTIVE_NOW.md
git -C "c:/Users/tomw2/GTeveryday Dropbox/Data Center/Tom/AI Agents & Projects/Code Agents/PRODUCTION" commit -m "docs(state): record supply-side inventory flow shipped"
```

---

## Acceptance gate

The plan is "complete" only when **all** of the following hold:

1. Migration 0146 is applied to the dev DB and pgTAP shows green.
2. `/api/v1/queries/inventory/supply-flow` returns 200 + a valid `FlowResponse` body for an authenticated request.
3. `/planning/inventory-flow/supply` renders in the browser, tab nav works both directions, at least one COMPONENT row and one BOUGHT_FINISHED ITEM row are visible (with non-zero `current_on_hand`).
4. The FG page (`/planning/inventory-flow`) still works exactly as before — same behavior, same tier colors, same numbers. **Regression check:** load the FG page side-by-side with a pre-merge baseline and confirm rows are unchanged.
5. CURRENT_STATE.md and ACTIVE_NOW.md mention the new surface.
6. No CLAUDE.md non-negotiable is violated:
   - No new writable on-prem fallback (✓ — read-only view).
   - No Excel round-trip (✓).
   - Stock truth still flows through the ledger; the new surface is read-only on top of `current_balances` + projection function (✓).
   - English-only developer artifacts (✓ — page tab labels and metadata are English; if Tom later supplies a Hebrew register for these strings, they can be swapped).

---

## Risks & open questions

- **R1 — BOM `is_active` flag name.** Migration 0146 Task 1 assumes `bom_version.is_active`. If the actual flag is named differently (e.g. `bom_version.status='ACTIVE'`), the executor must read `db/migrations/0003_bom_three_table.sql` and adjust both helper queries before running tests. **Halt the migration** if multiple active versions exist for a head — that's a data-quality problem the supply view must surface, not silently aggregate.
- **R2 — Components used in production AND sold direct.** If such a SKU exists today (a component that also appears as a BOUGHT_FINISHED item via some link), this plan does **not** unify them. Defer; surface as v2 if it ever comes up.
- **R3 — `current_balances.site_id` scoping.** The supply projection assumes a single-site model. If multi-site lands later, the function signature must accept `p_site_id text`.
- **R4 — Cache key collision.** If `flow-cache.ts` is a global module-level Map, the FG cache and supply cache share a Map. The implementation in Task 6 must ensure the cache key prefix `supply|` is applied so a supply request never returns a cached FG payload.
- **R5 — Drill-down deferred.** Task 12 ships the supply page without per-SKU drill-down rendering. The backend route exists (Task 7) but no UI consumes it. Document this clearly so the next planner does not assume completeness.

---

## Glossary

- **FG flow** — the existing `/planning/inventory-flow` page (finished goods).
- **Supply flow** — the new `/planning/inventory-flow/supply` page added by this plan.
- **COMPONENT** — `private_core.components` row (RM + PKG).
- **BOUGHT_FINISHED ITEM** — `private_core.items` row with `supply_method='BOUGHT_FINISHED'`.
- **BOM consumption** — quantity of a component consumed by a planned production batch on `plan_date`, derived by walking PACK BOM + BASE BOM.
- **Hybrid D risk model** — the days-of-cover vs effective-lead-time tier model used by `fn_compute_daily_fg_projection` and inherited by the supply projection.

---
