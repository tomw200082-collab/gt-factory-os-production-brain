# Phase 10 Economics Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land the Phase 10 economics layer so Tom can answer "what does each FG cost, what does it sell for, what's the margin, and what's sitting in the warehouse worth" with audit history — first the COGS / material-cost foundation (Wave 10A), then the sale-price + margin layer (Wave 10B) once `lw_price_raw` currency and business-date column are resolved.

**Architecture:** Append-only snapshot tables (Approach B per spec §2) feeding a single read-only view `v_fg_economics`. COGS computed nightly via `private_core.fn_explode_bom_to_components(p_item_id text, p_qty qty_8dp DEFAULT 1)` — per-item overload added in **migration 0191** (Task 2.1 architectural fix; migration 0041 defines only the `(p_run_id uuid)` planning-engine variant; both coexist via PostgreSQL overload resolution). Sale price computed monthly from `orders_mirror_lines` once parser lands. GI prefill writes draft rows; admin approval atomically updates `supplier_items` + appends `price_history` + emits `change_log` in one transaction. No mutable cost columns on `items`. No autonomous price writes.

**Tech Stack:**
- DB: PostgreSQL 15+ (`private_core` schema), pgcrypto, pg_cron, pgTAP for tests, append-only triggers per `change_log_contract.md §5.3`.
- Backend (`gt-factory-os/api`): Fastify, TypeScript, Kysely, Zod, `node:test` (built-in; **not** Vitest — implementation diverged from plan skeleton; tests live in `api/test/*.test.ts`, not `api/src/**/__tests__/`).
- Portal (`window2-portal-sandbox` — sole owner, sister tree of `gt-factory-os-portal`): Next.js 15 App Router, TanStack Query, shadcn/ui, Tailwind.
- Integrations: existing `api/src/integrations/greeninvoice/` and `api/src/integrations/lionwheel/` modules. `sku_resolver.ts` + `private_core.integration_sku_map` already handles `lw_sku → item_id` (A10-8 pre-resolved).

**Source spec:** `docs/superpowers/specs/2026-05-13-phase10-economics-design.md` (G1 approved 2026-05-13).

**Wave structure:**
- **Wave 10A** — Sections 1–10. COGS foundation. No `lw_price_raw` dependency. Ships independently.
- **Wave 10B** — Sections 11–18. Sale-price + margin. Gated on A10-1 (`lw_price_raw` currency) + A10-10 (business-date column).

**Tom's locked answers (carried from G1):**
1. A10-10 business date: **delivery date primary, invoice date secondary, `created_at` last fallback** (§11 verification documents the chosen column).
2. Snapshot retention: **append-only forever in v1, no pruning**. Future archive policy documented as future-out-of-scope.
3. Verification items: **pick at G3** by the criteria in spec §9; not pre-locked.
4. GI bulk approval: 5% delta is **a UI flag only**, never auto-approve. Each approval is explicit.

---

## File structure

### Backend (`gt-factory-os` repo)

```
db/migrations/
  0187_fg_cogs_snapshots.sql                     [10A]
  0188_supplier_cost_drafts.sql                  [10A]
  0189_v_fg_economics_v1.sql                     [10A — sale-price cols NULL-only]
  0190_pg_cron_cogs_nightly.sql                  [10A]
  0191_fn_explode_bom_per_item.sql               [10A — architectural insertion during Task 2.1; per-item overload of fn_explode_bom_to_components (commit e2ed3a2)]
  0192_lw_price_parsed.sql                       [10B — was 0191 in earlier draft, shifted +1]
  0193_fg_avg_sale_price_snapshots.sql           [10B — was 0192, shifted +1]
  0194_v_fg_economics_v2.sql                     [10B — was 0193, shifted +1; replaces 0189]
  0195_pg_cron_avg_sale_price_monthly.sql        [10B — was 0194, shifted +1]

db/tests/
  0187_fg_cogs_snapshots.test.sql                [10A]
  0188_supplier_cost_drafts.test.sql             [10A]
  0189_v_fg_economics_v1.test.sql                [10A]
  0191_fn_explode_bom_per_item.test.sql          [10A — added with the architectural migration]
  0193_fg_avg_sale_price_snapshots.test.sql      [10B — was 0192, shifted +1]
  0194_v_fg_economics_v2.test.sql                [10B — was 0193, shifted +1]

api/src/cogs/
  cogs-rollup.ts                                 [10A — single-item compute]
  cogs-snapshot-job.ts                           [10A — orchestrator]
  __tests__/cogs-rollup.test.ts
  __tests__/cogs-snapshot-job.test.ts

api/src/cost-drafts/
  approve-cost-draft.ts                          [10A — atomic 4-step handler]
  reject-cost-draft.ts                           [10A]
  __tests__/approve-cost-draft.test.ts
  __tests__/reject-cost-draft.test.ts

api/src/integrations/greeninvoice/
  cost-prefill-ingest.ts                         [10A — draft creator]
  __tests__/cost-prefill-ingest.test.ts

api/src/sale-price/
  lw-price-parser.ts                             [10B]
  avg-sale-price-job.ts                          [10B]
  __tests__/lw-price-parser.test.ts
  __tests__/avg-sale-price-job.test.ts

api/src/routes/
  economics.ts                                   [10A — GET routes for v_fg_economics + drilldown]
  cost-drafts.ts                                 [10A — POST approve/reject + GET list]
  supplier-costs.ts                              [10A — inline supplier_items edit]
  __tests__/economics.test.ts
  __tests__/cost-drafts.test.ts
  __tests__/supplier-costs.test.ts
```

### Portal (`window2-portal-sandbox` repo — sole canonical Window 2)

```
app/economics/
  page.tsx                                       [10A — Dashboard, 5 KPIs]
  products/
    page.tsx                                     [10A — Product Economics table]
    [item_id]/
      page.tsx                                   [10A — Product drilldown]

app/admin/cost-data/
  page.tsx                                       [10A — Cost Data Admin host w/ tabs]
  drafts/
    page.tsx                                     [10A — deep link to GI drafts tab]

components/economics/
  kpi-tile.tsx                                   [10A]
  dashboard-grid.tsx                             [10A]
  product-economics-table.tsx                    [10A]
  cost-breakdown-table.tsx                       [10A]
  cost-history-strip.tsx                         [10A]
  source-attribution.tsx                         [10A]
  reliability-badge.tsx                          [10A]
  material-margin-footnote.tsx                   [10A]
  data-quality-pill.tsx                          [10A]

components/cost-admin/
  cost-admin-tabs.tsx                            [10A]
  supplier-costs-table.tsx                       [10A]
  cost-drafts-table.tsx                          [10A]
  price-history-list.tsx                         [10A]
  inline-cost-editor.tsx                         [10A]
  draft-approval-dialog.tsx                      [10A]

lib/queries/
  use-economics-dashboard.ts                     [10A]
  use-product-economics.ts                       [10A]
  use-product-drilldown.ts                       [10A]
  use-cost-drafts.ts                             [10A]
  use-supplier-costs.ts                          [10A]
  use-approve-cost-draft.ts                      [10A — mutation]
  use-reject-cost-draft.ts                       [10A — mutation]
  use-edit-supplier-cost.ts                      [10A — mutation]

lib/economics/
  labels.ts                                      [10A — English + Hebrew label constants]
```

---

# WAVE 10A — Cost Foundation

## Section 1: Schema migrations (M1–M3) + cron

### Task 1.1: Migration 0187 — `fg_cogs_snapshots`

**Files:**
- Create: `gt-factory-os/db/migrations/0187_fg_cogs_snapshots.sql`
- Test: `gt-factory-os/db/tests/0187_fg_cogs_snapshots.test.sql`

- [ ] **Step 1.1.1: Write the failing pgTAP test**

Create `db/tests/0187_fg_cogs_snapshots.test.sql`:

```sql
begin;
select plan(14);

-- Existence
select has_table('private_core','fg_cogs_snapshots','table exists');
select has_pk('private_core','fg_cogs_snapshots','PK exists');

-- Columns + types
select col_type_is('private_core','fg_cogs_snapshots','fg_cogs_snapshot_id','uuid','PK column type');
select col_type_is('private_core','fg_cogs_snapshots','item_id','text','item_id is text');
select col_type_is('private_core','fg_cogs_snapshots','cogs_complete','boolean','cogs_complete is boolean');
select col_type_is('private_core','fg_cogs_snapshots','missing_cost_components','jsonb','missing_cost_components is jsonb');
select col_type_is('private_core','fg_cogs_snapshots','cost_breakdown','jsonb','cost_breakdown is jsonb');

-- FK
select fk_ok('private_core','fg_cogs_snapshots','item_id','private_core','items','item_id');

-- Append-only enforcement
select trigger_is('private_core','fg_cogs_snapshots','trg_fg_cogs_snapshots_no_update','private_core','change_log_append_only_guard');
select trigger_is('private_core','fg_cogs_snapshots','trg_fg_cogs_snapshots_no_delete','private_core','change_log_append_only_guard');

-- supply_method_snapshot CHECK
prepare bad_sm as
  insert into private_core.fg_cogs_snapshots(item_id,cogs_complete,supply_method_snapshot,source,actor_snapshot)
  values ('FG-TEST',true,'INVALID','nightly_job','<system:test>');
select throws_ok('bad_sm',NULL,'CHECK rejects invalid supply_method_snapshot');

-- source CHECK
prepare bad_src as
  insert into private_core.fg_cogs_snapshots(item_id,cogs_complete,supply_method_snapshot,source,actor_snapshot)
  values ('FG-TEST',true,'MANUFACTURED','bogus_source','<system:test>');
select throws_ok('bad_src',NULL,'CHECK rejects invalid source');

-- UPDATE forbidden
select lives_ok($$
  insert into private_core.fg_cogs_snapshots(item_id,cogs_complete,supply_method_snapshot,source,actor_snapshot)
  values ('FG-FIXTURE',true,'MANUFACTURED','nightly_job','<system:test>')
$$,'insert OK');
prepare bad_upd as update private_core.fg_cogs_snapshots set cogs_complete=false where item_id='FG-FIXTURE';
select throws_ok('bad_upd','42501','UPDATE forbidden');

-- DELETE forbidden
prepare bad_del as delete from private_core.fg_cogs_snapshots where item_id='FG-FIXTURE';
select throws_ok('bad_del','42501','DELETE forbidden');

select * from finish();
rollback;
```

- [ ] **Step 1.1.2: Run pgTAP — verify it fails with "table does not exist"**

```bash
cd gt-factory-os
pg_prove -d "$DATABASE_URL" db/tests/0187_fg_cogs_snapshots.test.sql
# Expected: ERROR — relation "private_core.fg_cogs_snapshots" does not exist
```

- [ ] **Step 1.1.3: Write migration 0187**

Create `db/migrations/0187_fg_cogs_snapshots.sql`:

```sql
-- ===========================================================================
-- 0187_fg_cogs_snapshots.sql
-- ===========================================================================
-- Phase 10 Wave 10A — append-only nightly COGS snapshot per FG item.
--
-- Spec: docs/superpowers/specs/2026-05-13-phase10-economics-design.md §3.1.1
-- Plan: docs/superpowers/plans/2026-05-13-phase10-economics-layer.md §1.1
--
-- Depends on:
--   0002 (items, supply_method enum values)
--   0005 (app_users — FK target for actor_user_id)
--   0025 (change_log_append_only_guard() — reused trigger function)
--   0041 (fn_explode_bom_to_components — invoked by the snapshot job, not by DDL)
--
-- Append-only via trg_fg_cogs_snapshots_no_update / _no_delete (same pattern
-- as price_history). UPDATE/DELETE raise 42501.
-- ===========================================================================

begin;

set search_path to private_core, public;

create table private_core.fg_cogs_snapshots (
  fg_cogs_snapshot_id      uuid primary key default gen_random_uuid(),
  item_id                  text not null references private_core.items(item_id),
  cogs_per_unit_ils        private_core.money_4dp,
  cogs_complete            boolean not null,
  missing_cost_components  jsonb not null default '[]'::jsonb,
  cost_breakdown           jsonb not null default '[]'::jsonb,
  supply_method_snapshot   text not null
                           check (supply_method_snapshot in
                                  ('MANUFACTURED','BOUGHT_FINISHED','REPACK')),
  event_at                 timestamptz not null default now(),
  posted_at                timestamptz not null default now(),
  run_id                   uuid,
  source                   text not null
                           check (source in ('nightly_job','manual_verification','backfill')),
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

comment on table private_core.fg_cogs_snapshots is
  'Phase 10 Wave 10A. Append-only nightly per-FG COGS snapshot. Append-only enforced by trigger; never UPDATE/DELETE. Spec §3.1.1.';

commit;
```

- [ ] **Step 1.1.4: Apply migration on dev DB**

```bash
psql "$DATABASE_URL" -f db/migrations/0187_fg_cogs_snapshots.sql
# Expected: BEGIN ... CREATE TABLE ... CREATE INDEX (x2) ... CREATE TRIGGER (x2) ... COMMIT
```

- [ ] **Step 1.1.5: Re-run pgTAP — verify 14/14 PASS**

```bash
pg_prove -d "$DATABASE_URL" db/tests/0187_fg_cogs_snapshots.test.sql
# Expected: ok 1 .. ok 14 — All tests successful.
```

- [ ] **Step 1.1.6: Commit**

```bash
git add db/migrations/0187_fg_cogs_snapshots.sql db/tests/0187_fg_cogs_snapshots.test.sql
git commit -m "feat(phase10): 0187 fg_cogs_snapshots append-only table"
git push
```

---

### Task 1.2: Migration 0188 — `supplier_cost_drafts`

**Files:**
- Create: `gt-factory-os/db/migrations/0188_supplier_cost_drafts.sql`
- Test: `gt-factory-os/db/tests/0188_supplier_cost_drafts.test.sql`

- [ ] **Step 1.2.1: Write failing pgTAP test**

Create `db/tests/0188_supplier_cost_drafts.test.sql`:

```sql
begin;
select plan(11);

select has_table('private_core','supplier_cost_drafts','table exists');
select has_pk('private_core','supplier_cost_drafts','PK exists');
select col_type_is('private_core','supplier_cost_drafts','suggested_cost_ils','numeric(18,4)','cost is money_4dp');
select col_type_is('private_core','supplier_cost_drafts','status','text','status is text');
select fk_ok('private_core','supplier_cost_drafts','supplier_item_id','private_core','supplier_items','supplier_item_id');
select fk_ok('private_core','supplier_cost_drafts','resulting_price_history_id','private_core','price_history','price_history_id');

-- status CHECK
prepare bad_status as
  insert into private_core.supplier_cost_drafts(supplier_item_id,suggested_cost_ils,status)
  select supplier_item_id, 1.0, 'invalid' from private_core.supplier_items limit 1;
select throws_ok('bad_status',NULL,'CHECK rejects invalid status');

-- non-negative cost CHECK
prepare neg_cost as
  insert into private_core.supplier_cost_drafts(supplier_item_id,suggested_cost_ils)
  select supplier_item_id, -1.0 from private_core.supplier_items limit 1;
select throws_ok('neg_cost',NULL,'CHECK rejects negative suggested_cost_ils');

-- updated_at trigger
select trigger_is('private_core','supplier_cost_drafts','trg_supplier_cost_drafts_touch_updated_at','private_core','touch_updated_at');

-- UPDATE allowed (this is the mutable-pre-approval table)
prepare ins as
  insert into private_core.supplier_cost_drafts(supplier_item_id,suggested_cost_ils)
  select supplier_item_id, 5.50 from private_core.supplier_items limit 1
  returning supplier_cost_draft_id;
select lives_ok('ins','insert lives');
-- (Manual UPDATE check happens at handler-test level, not DDL.)

-- Indexes exist
select has_index('private_core','supplier_cost_drafts','idx_supplier_cost_drafts_status','status index');

select * from finish();
rollback;
```

- [ ] **Step 1.2.2: Run pgTAP — verify it fails ("table does not exist")**

```bash
pg_prove -d "$DATABASE_URL" db/tests/0188_supplier_cost_drafts.test.sql
```

- [ ] **Step 1.2.3: Write migration 0188**

Create `db/migrations/0188_supplier_cost_drafts.sql`:

```sql
-- ===========================================================================
-- 0188_supplier_cost_drafts.sql
-- ===========================================================================
-- Phase 10 Wave 10A — GI prefill staging. Mutable (UPDATE allowed) because
-- admin can edit before approval. Approval is one-way: pending → approved
-- (atomic transaction writes supplier_items + price_history + change_log)
-- or pending → rejected. State-machine semantics enforced in the application
-- handler, not in DDL (see api/src/cost-drafts/approve-cost-draft.ts).
--
-- Spec §3.1.3; plan §1.2.
-- ===========================================================================

begin;

set search_path to private_core, public;

create table private_core.supplier_cost_drafts (
  supplier_cost_draft_id     uuid primary key default gen_random_uuid(),
  supplier_item_id           uuid not null
                             references private_core.supplier_items(supplier_item_id),
  suggested_cost_ils         private_core.money_4dp not null check (suggested_cost_ils >= 0),
  source_invoice_id          text,
  source_invoice_date        date,
  source_line_ref            text,
  reviewer_note              text,
  status                     text not null default 'pending'
                             check (status in ('pending','approved','rejected','superseded')),
  approved_at                timestamptz,
  approved_by_user_id        uuid references private_core.app_users(user_id),
  approved_actor_snapshot    text,
  resulting_price_history_id uuid references private_core.price_history(price_history_id),
  rejected_at                timestamptz,
  rejected_by_user_id        uuid references private_core.app_users(user_id),
  rejected_actor_snapshot    text,
  rejection_reason           text,
  created_at                 timestamptz not null default now(),
  updated_at                 timestamptz not null default now()
);

create trigger trg_supplier_cost_drafts_touch_updated_at
  before update on private_core.supplier_cost_drafts
  for each row execute function private_core.touch_updated_at();

create index idx_supplier_cost_drafts_status
  on private_core.supplier_cost_drafts(status, created_at desc);

create index idx_supplier_cost_drafts_supplier_item
  on private_core.supplier_cost_drafts(supplier_item_id);

comment on table private_core.supplier_cost_drafts is
  'Phase 10 Wave 10A. Mutable draft suggestions from GI cost prefill. Approval handler (api/src/cost-drafts/approve-cost-draft.ts) atomically writes supplier_items + price_history + change_log and flips status to approved. Spec §3.1.3.';

commit;
```

> **Note on `status='superseded'`:** the CHECK enum includes `'superseded'` as a reserved value for a future supersede-older-pending-draft flow. **Not written by Wave 10A or Wave 10B** — no handler, ingest, or UI in this plan produces or consumes it. The value is in the enum now to avoid a future ALTER TABLE migration when the supersede flow is added. See spec §3.1.3 for the full reserved-status paragraph. Any code in 10A or 10B that writes or reads `'superseded'` is a defect and should be flagged in review.

- [ ] **Step 1.2.4: Apply migration on dev DB**

```bash
psql "$DATABASE_URL" -f db/migrations/0188_supplier_cost_drafts.sql
```

- [ ] **Step 1.2.5: Re-run pgTAP — verify 11/11 PASS**

```bash
pg_prove -d "$DATABASE_URL" db/tests/0188_supplier_cost_drafts.test.sql
```

- [ ] **Step 1.2.6: Commit**

```bash
git add db/migrations/0188_supplier_cost_drafts.sql db/tests/0188_supplier_cost_drafts.test.sql
git commit -m "feat(phase10): 0188 supplier_cost_drafts staging table"
git push
```

---

### Task 1.3: Migration 0189 — `v_fg_economics` v1 (10A — sale-price columns NULL-only)

**Files:**
- Create: `gt-factory-os/db/migrations/0189_v_fg_economics_v1.sql`
- Test: `gt-factory-os/db/tests/0189_v_fg_economics_v1.test.sql`

- [ ] **Step 1.3.1: Pre-flight — confirm `current_balances` column shape (resolve A10-9)**

```bash
psql "$DATABASE_URL" -c "\d+ private_core.current_balances"
```

Document the actual column name for FG quantity-on-hand and the entity discriminator in a comment at the top of the migration. If the spec's draft assumption (`entity_kind = 'item'`) is wrong, adjust the view's `fg_qty` CTE accordingly. **Do not proceed to 1.3.2 until this is resolved and documented.**

- [ ] **Step 1.3.2: Write failing pgTAP test**

Create `db/tests/0189_v_fg_economics_v1.test.sql`:

```sql
begin;
select plan(20);

-- Existence
select has_view('private_core','v_fg_economics','view exists');

-- 18 columns from spec §3.2
select has_column('private_core','v_fg_economics','item_id','col 1');
select has_column('private_core','v_fg_economics','item_name','col 2');
select has_column('private_core','v_fg_economics','cogs_per_unit_ils','col 3');
select has_column('private_core','v_fg_economics','cogs_complete','col 4');
select has_column('private_core','v_fg_economics','missing_cost_components','col 5');
select has_column('private_core','v_fg_economics','cogs_snapshot_at','col 6');
select has_column('private_core','v_fg_economics','avg_sale_price_ils','col 7');
select has_column('private_core','v_fg_economics','avg_sale_price_period','col 8');
select has_column('private_core','v_fg_economics','transaction_count','col 9');
select has_column('private_core','v_fg_economics','total_qty_sold','col 10');
select has_column('private_core','v_fg_economics','reliability_flag','col 11');
select has_column('private_core','v_fg_economics','avg_sale_price_snapshot_at','col 12');
select has_column('private_core','v_fg_economics','material_margin_ils','col 13');
select has_column('private_core','v_fg_economics','material_margin_pct','col 14');
select has_column('private_core','v_fg_economics','qty_on_hand','col 15');
select has_column('private_core','v_fg_economics','fg_inventory_value_at_cost','col 16');
select has_column('private_core','v_fg_economics','fg_inventory_value_at_sale_price','col 17');
select has_column('private_core','v_fg_economics','embedded_material_margin_in_stock','col 18');

-- 10A invariant: until 10B, all sale-price columns are NULL
select is_empty($$
  select 1 from private_core.v_fg_economics where avg_sale_price_ils is not null
$$, '10A: avg_sale_price_ils is NULL for every row');

select * from finish();
rollback;
```

- [ ] **Step 1.3.3: Run pgTAP — verify it fails ("view does not exist")**

```bash
pg_prove -d "$DATABASE_URL" db/tests/0189_v_fg_economics_v1.test.sql
```

- [ ] **Step 1.3.4: Write migration 0189**

Create `db/migrations/0189_v_fg_economics_v1.sql` based on spec §3.2 view definition, replacing the `current_balances` column references with the actual names resolved in Step 1.3.1. **Full SQL body matches spec §3.2; reproduce verbatim** with the only adjustment being `current_balances` column names. Append-only sale-price snapshot table does not exist in 10A, so `latest_asp` CTE is replaced with a stub:

```sql
-- ===========================================================================
-- 0189_v_fg_economics_v1.sql
-- ===========================================================================
-- Phase 10 Wave 10A — v_fg_economics view, v1. Sale-price columns return
-- NULL until Wave 10B lands fg_avg_sale_price_snapshots and rebuilds the
-- view (migration 0193). This v1 keeps the column SHAPE stable so the
-- portal can ship against the final contract — only the values change in 10B.
--
-- Spec §3.2; plan §1.3.
-- ===========================================================================

begin;

set search_path to private_core, public;

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
fg_qty as (
  -- Adjust column names here based on Step 1.3.1 resolution of A10-9.
  -- Placeholder uses the spec's draft assumption; correct before applying.
  select item_id, qty_on_hand
  from private_core.current_balances
  where entity_kind = 'item'
)
select
  i.item_id,
  i.item_name,
  c.cogs_per_unit_ils,
  coalesce(c.cogs_complete, false)                          as cogs_complete,
  coalesce(c.missing_cost_components, '[]'::jsonb)          as missing_cost_components,
  c.cogs_snapshot_at,
  -- 10A: sale-price columns are NULL-only until 10B
  null::private_core.money_4dp                              as avg_sale_price_ils,
  null::text                                                as avg_sale_price_period,
  0::integer                                                as transaction_count,
  0::private_core.qty_8dp                                   as total_qty_sold,
  'NONE'::text                                              as reliability_flag,
  null::timestamptz                                         as avg_sale_price_snapshot_at,
  null::private_core.money_4dp                              as material_margin_ils,
  null::numeric(6,2)                                        as material_margin_pct,
  coalesce(q.qty_on_hand, 0)                                as qty_on_hand,
  case
    when c.cogs_per_unit_ils is not null and q.qty_on_hand is not null
    then c.cogs_per_unit_ils * q.qty_on_hand
    else null
  end                                                       as fg_inventory_value_at_cost,
  null::private_core.money_4dp                              as fg_inventory_value_at_sale_price,
  null::private_core.money_4dp                              as embedded_material_margin_in_stock
from private_core.items i
left join latest_cogs c on c.item_id = i.item_id
left join fg_qty     q on q.item_id = i.item_id
where i.status = 'ACTIVE';

comment on view private_core.v_fg_economics is
  'Phase 10 Wave 10A. Single read surface for the economics dashboard. Sale-price columns return NULL until Wave 10B (migration 0193 replaces this view). Spec §3.2.';

commit;
```

- [ ] **Step 1.3.5: Apply migration**

```bash
psql "$DATABASE_URL" -f db/migrations/0189_v_fg_economics_v1.sql
```

- [ ] **Step 1.3.6: Re-run pgTAP — verify 20/20 PASS**

```bash
pg_prove -d "$DATABASE_URL" db/tests/0189_v_fg_economics_v1.test.sql
```

- [ ] **Step 1.3.7: Commit**

```bash
git add db/migrations/0189_v_fg_economics_v1.sql db/tests/0189_v_fg_economics_v1.test.sql
git commit -m "feat(phase10): 0189 v_fg_economics v1 (10A — sale-price NULL-only)"
git push
```

---

### Task 1.4: Migration 0190 — pg_cron nightly COGS schedule (gated; do NOT enable yet)

The job runs only after Section 2 lands the actual orchestrator. Migration 0190 only **defines** the schedule entry, **disabled by default**, so Section 2 can flip it on after the snapshot job code is deployed.

**Files:**
- Create: `gt-factory-os/db/migrations/0190_pg_cron_cogs_nightly.sql`

- [ ] **Step 1.4.1: Write migration 0190**

```sql
-- ===========================================================================
-- 0190_pg_cron_cogs_nightly.sql
-- ===========================================================================
-- Phase 10 Wave 10A — pg_cron schedule entry for the nightly COGS snapshot
-- job. INSERTS the entry with active=false so the entry exists at deploy
-- time but does NOT run until the application orchestrator is deployed and
-- the entry is explicitly enabled in Section 2 / Task 2.6.
--
-- Spec §4.4; plan §1.4.
-- ===========================================================================

begin;

set search_path to cron, public;

-- Idempotent: only insert if no row exists for this jobname.
insert into cron.job (schedule, command, jobname, active)
select '0 2 * * *',
       $$select 1 /* phase10:cogs:nightly placeholder — replaced by orchestrator HTTP trigger in 0190b */$$,
       'phase10-cogs-nightly',
       false
where not exists (select 1 from cron.job where jobname = 'phase10-cogs-nightly');

commit;
```

- [ ] **Step 1.4.2: Apply migration**

```bash
psql "$DATABASE_URL" -f db/migrations/0190_pg_cron_cogs_nightly.sql
psql "$DATABASE_URL" -c "select jobname,schedule,active from cron.job where jobname='phase10-cogs-nightly'"
# Expected: row exists, active=false
```

- [ ] **Step 1.4.3: Commit**

```bash
git add db/migrations/0190_pg_cron_cogs_nightly.sql
git commit -m "feat(phase10): 0190 pg_cron nightly COGS placeholder (disabled)"
git push
```

---

## Section 2: COGS rollup + snapshot job

### Task 2.1: `cogs-rollup.ts` — single-item compute

**Files:**
- Create: `gt-factory-os/api/src/cogs/cogs-rollup.ts`
- Test: `gt-factory-os/api/src/cogs/__tests__/cogs-rollup.test.ts`

- [ ] **Step 2.1.1: Write failing test for `computeCogsForItem`**

Create `api/src/cogs/__tests__/cogs-rollup.test.ts`:

```typescript
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { getDb } from '../../db/connection';
import { computeCogsForItem } from '../cogs-rollup';

describe('computeCogsForItem', () => {
  const db = getDb();

  it('returns cogs_complete=true and full breakdown for a MANUFACTURED item with all supplier costs present', async () => {
    // Fixture: a MANUFACTURED item with a 2-line BOM, both components
    // having std_cost_per_inv_uom on supplier_items.
    const result = await computeCogsForItem(db, 'FG-FIXTURE-MFG-COMPLETE');
    expect(result.cogs_complete).toBe(true);
    expect(result.cogs_per_unit_ils).not.toBeNull();
    expect(result.missing_cost_components).toEqual([]);
    expect(result.cost_breakdown.length).toBeGreaterThan(0);
    expect(result.supply_method_snapshot).toBe('MANUFACTURED');
  });

  it('returns cogs_complete=false with missing_cost_components populated when any input lacks cost', async () => {
    const result = await computeCogsForItem(db, 'FG-FIXTURE-MFG-MISSING-COST');
    expect(result.cogs_complete).toBe(false);
    expect(result.cogs_per_unit_ils).toBeNull();
    expect(result.missing_cost_components.length).toBeGreaterThan(0);
  });

  it('handles BOUGHT_FINISHED by reading supplier_items.std_cost_per_inv_uom on primary supplier', async () => {
    const result = await computeCogsForItem(db, 'FG-FIXTURE-BF');
    expect(result.supply_method_snapshot).toBe('BOUGHT_FINISHED');
    expect(result.cogs_complete).toBe(true);
    expect(result.cogs_per_unit_ils).not.toBeNull();
  });

  it('handles MANUFACTURED two-stage (base + pack) via fn_explode_bom_to_components', async () => {
    const result = await computeCogsForItem(db, 'FG-FIXTURE-TWO-STAGE');
    expect(result.cogs_complete).toBe(true);
    // The breakdown should include components from BOTH the base BOM and the pack BOM
    const componentIds = result.cost_breakdown.map(b => b.component_id);
    expect(componentIds.length).toBeGreaterThan(1);
  });

  it('falls back to components.std_cost_per_inv_uom when no primary supplier_items cost exists', async () => {
    const result = await computeCogsForItem(db, 'FG-FIXTURE-COMP-FALLBACK');
    expect(result.cogs_complete).toBe(true);
    // breakdown rows for fallback components should be tagged
    expect(result.cost_breakdown.some(b => b.cost_source === 'components_fallback')).toBe(true);
  });

  it('returns null cogs and supply_method_snapshot from items at compute time', async () => {
    const result = await computeCogsForItem(db, 'FG-FIXTURE-MFG-COMPLETE');
    expect(['MANUFACTURED','BOUGHT_FINISHED','REPACK']).toContain(result.supply_method_snapshot);
  });
});
```

- [ ] **Step 2.1.2: Run test — verify all 6 fail with module-not-found**

```bash
cd api && pnpm vitest run src/cogs/__tests__/cogs-rollup.test.ts
# Expected: Cannot find module '../cogs-rollup'
```

- [ ] **Step 2.1.3: Write `cogs-rollup.ts`**

Create `api/src/cogs/cogs-rollup.ts`:

```typescript
// COGS rollup for a single FG item.
//
// Strategy (spec §4):
//   1. Look up items.supply_method.
//   2a. MANUFACTURED:
//       - Call private_core.fn_explode_bom_to_components(p_item_id, p_qty)
//         — per-item overload landed in MIGRATION 0191 during this task as
//         an architectural fix (commit e2ed3a2). Migration 0041 defined only
//         the (p_run_id uuid) variant used by the planning engine; the two
//         overloads coexist via PostgreSQL overload resolution. The per-item
//         function is pure (LANGUAGE sql STABLE) and returns one row per
//         leaf component with columns (component_id, qty_per_unit, source_layer)
//         where source_layer ∈ ('PACK', 'BASE', NULL). It already handles
//         two-stage base+pack BOMs internally.
//       - For each row, resolve unit cost (Step 4 Path B logic), preserve
//         source_layer in the breakdown line (surfaced as
//         CostBreakdownLine.source_layer for the Product drilldown §16.4).
//       - Sum line costs.
//   2b. BOUGHT_FINISHED:
//       - Read supplier_items.std_cost_per_inv_uom where item_id=$item AND is_primary=true.
//       - cogs = that cost; breakdown = single line.
//   2c. REPACK:
//       - Same path as MANUFACTURED if a single-line BOM exists on the item
//         (spec §4.1 A10-4 unresolved — verify shape against any existing
//         REPACK item before broad rollout). If no BOM lines, cogs_complete=false.
//
// Per-component unit cost (Path B, spec §4.2):
//   primary supplier_items.std_cost_per_inv_uom > components.std_cost_per_inv_uom fallback.
//
// Returns CogsResult — never throws on missing cost; reports it in
// cogs_complete=false + missing_cost_components.
//
// Landed evidence (post-Task 2.1):
//   - Migration: commit e2ed3a2 on feat/phase10-economics-wave10a
//     (db/migrations/0191_fn_explode_bom_per_item.sql)
//   - Refactor: commit 134fb6c — this file replaced a 487-line inline CTE
//     with a call to the new function.

import type { Kysely } from 'kysely';
import type { Database } from '../db/schema';

export type CostBreakdownLine = {
  component_id: string | null;
  item_id_inline: string | null; // for BOUGHT_FINISHED, the self-item
  qty_per_fg_unit: string;       // numeric serialized as string (preserves precision)
  unit_cost_ils: string | null;
  line_cost_ils: string | null;
  cost_source: 'supplier_items_primary' | 'components_fallback' | 'self_supplier_items_primary' | 'missing';
  // Sourced from fn_explode_bom_to_components.source_layer (migration 0191):
  //   'PACK' = component from the pack-BOM layer of a two-stage item
  //   'BASE' = component from the base-BOM layer of a two-stage item
  //   null   = single-stage MANUFACTURED, BOUGHT_FINISHED, or REPACK (no layering)
  // Surfaced in the Product drilldown §16.4 so operators see which layer
  // contributes which fraction of total cost.
  source_layer: 'PACK' | 'BASE' | null;
};

export type MissingCostComponent = {
  component_id?: string;
  item_id?: string;
  reason: 'no_primary_supplier_cost'
        | 'primary_supplier_cost_null'
        | 'bought_finished_no_primary_supplier_cost'
        | 'no_bom_lines'
        | 'unknown_supply_method';
};

export type CogsResult = {
  item_id: string;
  cogs_per_unit_ils: string | null;
  cogs_complete: boolean;
  missing_cost_components: MissingCostComponent[];
  cost_breakdown: CostBreakdownLine[];
  supply_method_snapshot: 'MANUFACTURED' | 'BOUGHT_FINISHED' | 'REPACK';
};

export async function computeCogsForItem(
  db: Kysely<Database>,
  itemId: string
): Promise<CogsResult> {
  const item = await db
    .selectFrom('private_core.items')
    .select(['item_id', 'supply_method'])
    .where('item_id', '=', itemId)
    .executeTakeFirst();

  if (!item) {
    throw new Error(`Item not found: ${itemId}`);
  }

  const supplyMethod = item.supply_method as CogsResult['supply_method_snapshot'];

  if (supplyMethod === 'BOUGHT_FINISHED') {
    return computeBoughtFinishedCogs(db, itemId);
  }

  if (supplyMethod === 'MANUFACTURED' || supplyMethod === 'REPACK') {
    return computeBomBasedCogs(db, itemId, supplyMethod);
  }

  return {
    item_id: itemId,
    cogs_per_unit_ils: null,
    cogs_complete: false,
    missing_cost_components: [{ reason: 'unknown_supply_method' }],
    cost_breakdown: [],
    supply_method_snapshot: supplyMethod,
  };
}

async function computeBoughtFinishedCogs(
  db: Kysely<Database>,
  itemId: string
): Promise<CogsResult> {
  const row = await db
    .selectFrom('private_core.supplier_items')
    .select('std_cost_per_inv_uom')
    .where('item_id', '=', itemId)
    .where('is_primary', '=', true)
    .executeTakeFirst();

  const cost = row?.std_cost_per_inv_uom ?? null;

  if (cost === null) {
    return {
      item_id: itemId,
      cogs_per_unit_ils: null,
      cogs_complete: false,
      missing_cost_components: [{ item_id: itemId, reason: 'bought_finished_no_primary_supplier_cost' }],
      cost_breakdown: [{
        component_id: null,
        item_id_inline: itemId,
        qty_per_fg_unit: '1',
        unit_cost_ils: null,
        line_cost_ils: null,
        cost_source: 'missing',
      }],
      supply_method_snapshot: 'BOUGHT_FINISHED',
    };
  }

  return {
    item_id: itemId,
    cogs_per_unit_ils: cost.toString(),
    cogs_complete: true,
    missing_cost_components: [],
    cost_breakdown: [{
      component_id: null,
      item_id_inline: itemId,
      qty_per_fg_unit: '1',
      unit_cost_ils: cost.toString(),
      line_cost_ils: cost.toString(),
      cost_source: 'self_supplier_items_primary',
    }],
    supply_method_snapshot: 'BOUGHT_FINISHED',
  };
}

async function computeBomBasedCogs(
  db: Kysely<Database>,
  itemId: string,
  supplyMethod: 'MANUFACTURED' | 'REPACK'
): Promise<CogsResult> {
  // Existing function (migration 0041) returns leaf components flattened
  // across base+pack BOMs with qty_per_fg_unit pre-scaled.
  const explosion = await db
    .selectFrom(db.fn<any>('private_core.fn_explode_bom_to_components', [itemId, 1.0]).as('e'))
    .selectAll()
    .execute();

  if (explosion.length === 0) {
    return {
      item_id: itemId,
      cogs_per_unit_ils: null,
      cogs_complete: false,
      missing_cost_components: [{ reason: 'no_bom_lines' }],
      cost_breakdown: [],
      supply_method_snapshot: supplyMethod,
    };
  }

  const breakdown: CostBreakdownLine[] = [];
  const missing: MissingCostComponent[] = [];
  let total = 0n; // use bigint for precise sum, scaled by 1e8 (qty 8dp) * 1e4 (money 4dp) = 1e12

  for (const row of explosion) {
    const componentId: string = row.component_id;
    const qtyPerUnit: string = row.qty_per_unit;

    const supplierCost = await db
      .selectFrom('private_core.supplier_items')
      .select('std_cost_per_inv_uom')
      .where('component_id', '=', componentId)
      .where('is_primary', '=', true)
      .executeTakeFirst();

    let unitCost: string | null = supplierCost?.std_cost_per_inv_uom?.toString() ?? null;
    let source: CostBreakdownLine['cost_source'] = 'supplier_items_primary';

    if (unitCost === null) {
      const compRow = await db
        .selectFrom('private_core.components')
        .select('std_cost_per_inv_uom')
        .where('component_id', '=', componentId)
        .executeTakeFirst();
      unitCost = compRow?.std_cost_per_inv_uom?.toString() ?? null;
      source = unitCost === null ? 'missing' : 'components_fallback';
    }

    if (unitCost === null) {
      missing.push({
        component_id: componentId,
        reason: supplierCost ? 'primary_supplier_cost_null' : 'no_primary_supplier_cost',
      });
      breakdown.push({
        component_id: componentId,
        item_id_inline: null,
        qty_per_fg_unit: qtyPerUnit,
        unit_cost_ils: null,
        line_cost_ils: null,
        cost_source: 'missing',
      });
    } else {
      const lineCost = (parseFloat(qtyPerUnit) * parseFloat(unitCost)).toFixed(4);
      breakdown.push({
        component_id: componentId,
        item_id_inline: null,
        qty_per_fg_unit: qtyPerUnit,
        unit_cost_ils: unitCost,
        line_cost_ils: lineCost,
        cost_source: source,
      });
      total += BigInt(Math.round(parseFloat(lineCost) * 10000));
    }
  }

  const isComplete = missing.length === 0;

  return {
    item_id: itemId,
    cogs_per_unit_ils: isComplete ? (Number(total) / 10000).toFixed(4) : null,
    cogs_complete: isComplete,
    missing_cost_components: missing,
    cost_breakdown: breakdown,
    supply_method_snapshot: supplyMethod,
  };
}
```

- [ ] **Step 2.1.4: Create test fixtures**

Before running the tests, ensure the fixtures `FG-FIXTURE-MFG-COMPLETE`, `FG-FIXTURE-MFG-MISSING-COST`, `FG-FIXTURE-BF`, `FG-FIXTURE-TWO-STAGE`, `FG-FIXTURE-COMP-FALLBACK` exist in the dev DB. Add to `db/fixtures/phase10_cogs_fixtures.sql`:

```sql
-- Fixtures for cogs-rollup tests. Run only on dev/test DBs.
begin;

-- Suppliers + items + components needed for the 5 fixture FGs.
insert into private_core.suppliers(supplier_id, supplier_name_official) values ('SUP-FIX1','Fix Supplier 1') on conflict do nothing;

-- ... (full fixture rows — concrete, no placeholders. Reproduce the
-- structure of an existing fixtures file like db/fixtures/test_seed.sql
-- to match conventions. See existing fixture files for the canonical
-- shape; replicate them with these 5 item ids and their BOM lines.)

commit;
```

- [ ] **Step 2.1.5: Run cogs-rollup tests — verify all 6 PASS**

```bash
cd api && pnpm vitest run src/cogs/__tests__/cogs-rollup.test.ts
# Expected: 6 passed
```

- [ ] **Step 2.1.6: Commit**

```bash
git add api/src/cogs/cogs-rollup.ts api/src/cogs/__tests__/cogs-rollup.test.ts db/fixtures/phase10_cogs_fixtures.sql
git commit -m "feat(phase10): cogs-rollup single-item compute"
git push
```

---

### Task 2.2: `cogs-snapshot-job.ts` — orchestrator

**Files:**
- Create: `gt-factory-os/api/src/cogs/cogs-snapshot-job.ts`
- Test: `gt-factory-os/api/src/cogs/__tests__/cogs-snapshot-job.test.ts`

- [ ] **Step 2.2.1: Write failing tests**

Create `api/src/cogs/__tests__/cogs-snapshot-job.test.ts`:

```typescript
import { describe, it, expect } from 'vitest';
import { getDb } from '../../db/connection';
import { runCogsSnapshotJob } from '../cogs-snapshot-job';

describe('runCogsSnapshotJob', () => {
  const db = getDb();

  it('writes one row per active FG item with a shared run_id', async () => {
    const summary = await runCogsSnapshotJob(db, { source: 'manual_verification' });
    expect(summary.run_id).toMatch(/^[0-9a-f-]{36}$/);
    expect(summary.items_processed).toBeGreaterThan(0);

    const rowCount = await db
      .selectFrom('private_core.fg_cogs_snapshots')
      .select(db.fn.count('fg_cogs_snapshot_id').as('n'))
      .where('run_id', '=', summary.run_id)
      .executeTakeFirstOrThrow();
    expect(Number(rowCount.n)).toBe(summary.items_processed);
  });

  it('continues on per-item errors and reports them in summary.errors', async () => {
    // (Create one fixture FG with deliberately broken BOM linkage; assert
    // the job completes with summary.errors.length === 1 and other items
    // still got snapshot rows.)
    const summary = await runCogsSnapshotJob(db, { source: 'manual_verification' });
    expect(summary).toHaveProperty('errors');
    expect(Array.isArray(summary.errors)).toBe(true);
  });

  it('writes cogs_complete=true for fixtures with all costs', async () => {
    const summary = await runCogsSnapshotJob(db, { source: 'manual_verification' });
    const row = await db
      .selectFrom('private_core.fg_cogs_snapshots')
      .selectAll()
      .where('run_id', '=', summary.run_id)
      .where('item_id', '=', 'FG-FIXTURE-MFG-COMPLETE')
      .executeTakeFirstOrThrow();
    expect(row.cogs_complete).toBe(true);
    expect(row.cogs_per_unit_ils).not.toBeNull();
  });
});
```

- [ ] **Step 2.2.2: Run tests — verify they fail (module-not-found)**

```bash
cd api && pnpm vitest run src/cogs/__tests__/cogs-snapshot-job.test.ts
```

- [ ] **Step 2.2.3: Write `cogs-snapshot-job.ts`**

```typescript
// Nightly orchestrator. Iterates every ACTIVE item, computes COGS via
// computeCogsForItem, and inserts one fg_cogs_snapshots row per item with
// a shared run_id. Per-item errors are logged but do not abort the run.
//
// Spec §4.4. Plan §2.2.

import { v4 as uuidv4 } from 'uuid';
import type { Kysely } from 'kysely';
import type { Database } from '../db/schema';
import { computeCogsForItem } from './cogs-rollup';

export type CogsSnapshotJobOptions = {
  source: 'nightly_job' | 'manual_verification' | 'backfill';
  actor_user_id?: string | null;
  actor_snapshot?: string;
};

export type CogsSnapshotJobSummary = {
  run_id: string;
  started_at: string;
  finished_at: string;
  items_processed: number;
  items_complete: number;
  items_missing_cost: number;
  errors: Array<{ item_id: string; error: string }>;
};

export async function runCogsSnapshotJob(
  db: Kysely<Database>,
  opts: CogsSnapshotJobOptions
): Promise<CogsSnapshotJobSummary> {
  const runId = uuidv4();
  const startedAt = new Date().toISOString();
  const actorSnapshot = opts.actor_snapshot ?? '<system:cogs-snapshot-job>';

  const items = await db
    .selectFrom('private_core.items')
    .select('item_id')
    .where('status', '=', 'ACTIVE')
    .execute();

  let complete = 0;
  let missing = 0;
  const errors: Array<{ item_id: string; error: string }> = [];

  for (const { item_id } of items) {
    try {
      const result = await computeCogsForItem(db, item_id);
      await db
        .insertInto('private_core.fg_cogs_snapshots')
        .values({
          item_id: result.item_id,
          cogs_per_unit_ils: result.cogs_per_unit_ils,
          cogs_complete: result.cogs_complete,
          missing_cost_components: JSON.stringify(result.missing_cost_components),
          cost_breakdown: JSON.stringify(result.cost_breakdown),
          supply_method_snapshot: result.supply_method_snapshot,
          run_id: runId,
          source: opts.source,
          actor_user_id: opts.actor_user_id ?? null,
          actor_snapshot: actorSnapshot,
        })
        .execute();

      if (result.cogs_complete) complete += 1;
      else missing += 1;
    } catch (err: unknown) {
      errors.push({ item_id, error: err instanceof Error ? err.message : String(err) });
    }
  }

  return {
    run_id: runId,
    started_at: startedAt,
    finished_at: new Date().toISOString(),
    items_processed: items.length,
    items_complete: complete,
    items_missing_cost: missing,
    errors,
  };
}
```

- [ ] **Step 2.2.4: Run tests — verify all PASS**

```bash
cd api && pnpm vitest run src/cogs/__tests__/cogs-snapshot-job.test.ts
```

- [ ] **Step 2.2.5: Commit**

```bash
git add api/src/cogs/cogs-snapshot-job.ts api/src/cogs/__tests__/cogs-snapshot-job.test.ts
git commit -m "feat(phase10): cogs-snapshot-job nightly orchestrator"
git push
```

---

### Task 2.3: Wire orchestrator into the Fastify trigger endpoint + enable pg_cron entry

The orchestrator runs via an HTTP trigger so pg_cron can invoke it through the existing job-runner pattern. **Do not enable the cron entry until Section 10 G3 verification passes** — until then run the job on demand via the endpoint.

**Files:**
- Modify: `gt-factory-os/api/src/routes/internal-jobs.ts` (add `POST /internal/jobs/cogs-snapshot-nightly`)
- Test: `gt-factory-os/api/src/routes/__tests__/internal-jobs-cogs.test.ts`

- [ ] **Step 2.3.1: Add route + test (TDD as above)**

Same TDD pattern: failing test → minimal route handler → passing test → commit. Route handler validates `JOB_RUNNER_TOKEN` then invokes `runCogsSnapshotJob(db, { source: 'nightly_job' })`.

- [ ] **Step 2.3.2: Commit**

```bash
git commit -m "feat(phase10): /internal/jobs/cogs-snapshot-nightly endpoint"
git push
```

---

## Section 3: GI prefill ingest

### Task 3.1: `cost-prefill-ingest.ts` — turn recent GI invoice lines into draft rows

**Files:**
- Create: `gt-factory-os/api/src/integrations/greeninvoice/cost-prefill-ingest.ts`
- Test: `gt-factory-os/api/src/integrations/greeninvoice/__tests__/cost-prefill-ingest.test.ts`

- [ ] **Step 3.1.1: Pre-flight — verify A10-3 (GI invoice line → supplier_items mapping)**

Run `psql "$DATABASE_URL" -c "select count(*) from private_core.supplier_items where status='ACTIVE'"` and sample 20 recent GI invoice lines against current `supplier_items` rows. Document match rate in a top-of-file comment. **If match rate <50%, halt and escalate** — the prefill flow is not useful below that threshold without an additional supplier-mapping enrichment step.

- [ ] **Step 3.1.2: Write failing test**

Test creates a fake GI client returning canned invoice lines, runs the ingest, asserts:
1. Draft rows created in `supplier_cost_drafts` with `status='pending'`.
2. Net-of-VAT calculation correct (divides gross by 1.17 if GI line is gross — or whatever A10-5 verified semantics dictate).
3. **No writes** to `supplier_items` or `price_history`.

- [ ] **Step 3.1.3: Implement `cost-prefill-ingest.ts`**

Mirrors the existing pattern in `api/src/integrations/greeninvoice/credit_draft_creator.ts`. Reads invoices via the existing client, maps lines to `supplier_items`, inserts `supplier_cost_drafts` rows.

- [ ] **Step 3.1.4: Run tests — PASS**

- [ ] **Step 3.1.5: Commit**

```bash
git commit -m "feat(phase10): GI cost-prefill ingest (drafts only, no auto-write)"
git push
```

---

## Section 4: Cost draft approval handler + routes

### Task 4.1: `approve-cost-draft.ts` — atomic 4-step handler

**Files:**
- Create: `gt-factory-os/api/src/cost-drafts/approve-cost-draft.ts`
- Test: `gt-factory-os/api/src/cost-drafts/__tests__/approve-cost-draft.test.ts`

- [ ] **Step 4.1.1: Write failing tests covering the 4-step atomic transaction (spec §3.1.3)**

Test cases:
1. Happy path: pending draft → approved; `supplier_items.std_cost_per_inv_uom` updated, `price_history` row inserted, `change_log` row with `action='SUPPLIER_PRICE_UPDATE_MANUAL'` inserted, draft status flipped to `approved` with `resulting_price_history_id` populated, all visible in single transaction.
2. Already-approved draft: throws; no side effects.
3. Already-rejected draft: throws; no side effects.
4. If `price_history` INSERT fails (simulate FK violation): the entire transaction rolls back — `supplier_items` unchanged, draft still `pending`, no `change_log` row.
5. If `change_log` INSERT fails: same rollback semantics.

- [ ] **Step 4.1.2: Run tests — FAIL (module missing)**

- [ ] **Step 4.1.3: Implement handler**

```typescript
// Atomic 4-step approval per spec §3.1.3:
//   1. UPDATE private_core.supplier_items SET std_cost_per_inv_uom = …
//   2. INSERT INTO private_core.price_history (…) RETURNING price_history_id
//   3. UPDATE private_core.supplier_cost_drafts SET status='approved', resulting_price_history_id = …
//   4. INSERT INTO private_core.change_log (… action='SUPPLIER_PRICE_UPDATE_MANUAL' …)
//
// All four wrapped in db.transaction(). Any failure rolls back the whole thing.

import type { Kysely, Transaction } from 'kysely';
import type { Database } from '../db/schema';

export type ApproveCostDraftInput = {
  draftId: string;
  approver: { user_id: string; display_name: string };
  finalCost?: string;   // optional edit-then-approve override
  note?: string;
};

export type ApproveCostDraftResult = {
  draft_id: string;
  supplier_item_id: string;
  applied_cost_ils: string;
  price_history_id: string;
  change_log_id: string;
};

export async function approveCostDraft(
  db: Kysely<Database>,
  input: ApproveCostDraftInput
): Promise<ApproveCostDraftResult> {
  return db.transaction().execute(async (trx) => {
    const draft = await trx
      .selectFrom('private_core.supplier_cost_drafts')
      .selectAll()
      .where('supplier_cost_draft_id', '=', input.draftId)
      .forUpdate()
      .executeTakeFirstOrThrow();

    if (draft.status !== 'pending') {
      throw new Error(`Draft ${input.draftId} is ${draft.status}, not pending`);
    }

    const finalCost = input.finalCost ?? draft.suggested_cost_ils.toString();

    // Step 1: update supplier_items
    await trx
      .updateTable('private_core.supplier_items')
      .set({ std_cost_per_inv_uom: finalCost, updated_at: new Date() })
      .where('supplier_item_id', '=', draft.supplier_item_id)
      .execute();

    // Step 2: append price_history
    const phRow = await trx
      .insertInto('private_core.price_history')
      .values({
        supplier_item_id: draft.supplier_item_id,
        unit_price_net: finalCost,
        source: 'manual',
        event_at: draft.source_invoice_date ?? new Date(),
        actor_user_id: input.approver.user_id,
        actor_snapshot: input.approver.display_name,
        source_document_id: draft.source_invoice_id ?? null,
        notes: input.note ?? `Approved from GI prefill draft ${input.draftId}`,
      })
      .returning('price_history_id')
      .executeTakeFirstOrThrow();

    // Step 3: flip draft status
    await trx
      .updateTable('private_core.supplier_cost_drafts')
      .set({
        status: 'approved',
        approved_at: new Date(),
        approved_by_user_id: input.approver.user_id,
        approved_actor_snapshot: input.approver.display_name,
        resulting_price_history_id: phRow.price_history_id,
      })
      .where('supplier_cost_draft_id', '=', input.draftId)
      .execute();

    // Step 4: emit change_log
    const clRow = await trx
      .insertInto('private_core.change_log')
      .values({
        entity_table: 'supplier_items',
        entity_id: draft.supplier_item_id,
        action: 'SUPPLIER_PRICE_UPDATE_MANUAL',
        changed_fields: JSON.stringify(['std_cost_per_inv_uom']),
        old_values: null,
        new_values: JSON.stringify({ std_cost_per_inv_uom: finalCost }),
        actor_user_id: input.approver.user_id,
        actor_snapshot: input.approver.display_name,
      })
      .returning('change_log_id')
      .executeTakeFirstOrThrow();

    return {
      draft_id: input.draftId,
      supplier_item_id: draft.supplier_item_id,
      applied_cost_ils: finalCost,
      price_history_id: phRow.price_history_id,
      change_log_id: clRow.change_log_id,
    };
  });
}
```

- [ ] **Step 4.1.4: Run tests — PASS all 5**

- [ ] **Step 4.1.5: Commit**

```bash
git commit -m "feat(phase10): atomic cost-draft approval handler"
git push
```

---

### Task 4.2: `reject-cost-draft.ts`

Simple UPDATE of status to `'rejected'` with reason. TDD pattern; 2 tests (happy path + already-rejected rejection).

- [ ] **Step 4.2.1: Test + implement + commit**

---

### Task 4.3: Routes — `POST /api/cost-drafts/:id/approve`, `POST /api/cost-drafts/:id/reject`, `GET /api/cost-drafts`

**Files:**
- Create: `gt-factory-os/api/src/routes/cost-drafts.ts`
- Test: `gt-factory-os/api/src/routes/__tests__/cost-drafts.test.ts`

- [ ] **Step 4.3.1: TDD all three routes**

Routes use existing Zod validation + Fastify pattern. Approval requires `admin` role (use existing auth middleware). Return shapes match the handlers' result types.

- [ ] **Step 4.3.2: Commit**

```bash
git commit -m "feat(phase10): cost-drafts approve/reject/list routes"
git push
```

---

### Task 4.4: Route — `PATCH /api/supplier-costs/:supplier_item_id` (inline edit)

The inline-edit path in Cost Data Admin Tab 1 uses the **same** approval handler internally — it constructs a synthetic draft (status='approved' inline) and emits the same 4-step transaction with source='manual', source_document_id=null.

- [ ] **Step 4.4.1: TDD**

```bash
git commit -m "feat(phase10): inline supplier-cost edit route"
git push
```

---

## Section 5: Read routes — `GET /api/economics/*`

### Task 5.1: `GET /api/economics/dashboard` — aggregated 5 KPIs

**Files:**
- Create: `gt-factory-os/api/src/routes/economics.ts`
- Test: `gt-factory-os/api/src/routes/__tests__/economics.test.ts`

- [ ] **Step 5.1.1: Write failing test for KPI shape**

```typescript
it('returns 5 KPIs with the locked shape', async () => {
  const res = await app.inject({ method: 'GET', url: '/api/economics/dashboard',
    headers: { authorization: `Bearer ${plannerToken}` } });
  expect(res.statusCode).toBe(200);
  const body = res.json();
  expect(body).toHaveProperty('kpi_fg_sales_value_estimate');
  expect(body).toHaveProperty('kpi_fg_inventory_at_cost');
  expect(body).toHaveProperty('kpi_embedded_material_margin');
  expect(body).toHaveProperty('kpi_avg_material_margin_pct');
  expect(body).toHaveProperty('kpi_data_quality_issues_count');
});
```

- [ ] **Step 5.1.2: Implement route**

Single SQL aggregation over `v_fg_economics`. Returns NULL-tolerant aggregates (10A returns NULLs for KPIs 1/3/4 — empty-state copy is rendered by the portal).

- [ ] **Step 5.1.3: PASS + commit**

---

### Task 5.2: `GET /api/economics/products` — table data, sortable, filterable

- [ ] **Step 5.2.1: TDD route returning rows from `v_fg_economics` with optional `?filter=missing-cost|missing-sale-price|low-reliability` and `?sort=embedded_margin|sales_value|alphabetical`**

- [ ] **Step 5.2.2: Commit**

---

### Task 5.3: `GET /api/economics/products/:item_id` — drilldown (current snapshot + cost breakdown + last 12 COGS snapshots)

- [ ] **Step 5.3.1: TDD route**

Returns: latest row from `v_fg_economics` for the item + latest `cost_breakdown` JSONB + last 12 COGS snapshots (event_at desc) for the history strip.

- [ ] **Step 5.3.2: Commit**

---

## Section 6: Portal — Economics Dashboard

### Task 6.1: Label constants + footnote component

**Files:**
- Create: `window2-portal-sandbox/lib/economics/labels.ts`
- Create: `window2-portal-sandbox/components/economics/material-margin-footnote.tsx`

- [ ] **Step 6.1.1: Write `labels.ts` — English + Hebrew label map per spec §7**

```typescript
export const ECON_LABELS = {
  en: {
    cogs_per_unit_ils: 'Material cost per unit (net of VAT, before labor & overhead)',
    avg_sale_price_ils: 'Average sale price (last 30 days, net of VAT)',
    material_margin_ils: 'Material margin per unit (before labor & overhead)',
    material_margin_pct: 'Material margin %',
    fg_inventory_value_at_cost: 'FG inventory value at standard cost',
    fg_inventory_value_at_sale_price: 'FG sales-value estimate (at avg sale price)',
    embedded_material_margin_in_stock: 'Embedded material margin in current stock',
    rm_pkg_inventory_at_cost: 'RM/PKG inventory at standard cost',
    margin_footnote: 'Margins shown are material-only, before labor and overhead. Operational profitability requires adding direct labor and allocated overhead.',
  },
  he: {
    cogs_per_unit_ils: 'עלות חומרים ליחידה (ללא מע״מ, לפני עבודה ותקורות)',
    avg_sale_price_ils: 'מחיר מכירה ממוצע (30 ימים אחרונים, ללא מע״מ)',
    material_margin_ils: 'מרווח חומרי ליחידה (לפני עבודה ותקורות)',
    material_margin_pct: 'מרווח חומרי %',
    fg_inventory_value_at_cost: 'שווי מלאי תוצרת מוגמרת בעלות תקן',
    fg_inventory_value_at_sale_price: 'אומדן שווי מכירה למלאי תוצרת (במחיר מכירה ממוצע)',
    embedded_material_margin_in_stock: 'מרווח חומרי טמון במלאי הנוכחי',
    rm_pkg_inventory_at_cost: 'שווי חומרי גלם ואריזות בעלות תקן',
    margin_footnote: 'המרווחים המוצגים הם חומרי בלבד, לפני עבודה ותקורות. רווחיות תפעולית מחייבת הוספת עבודה ישירה ותקורה מוקצית.',
  },
} as const;
```

- [ ] **Step 6.1.2: Write the footnote component**

```tsx
import { ECON_LABELS } from '@/lib/economics/labels';

export function MaterialMarginFootnote({ locale = 'en' }: { locale?: 'en' | 'he' }) {
  return (
    <p className="text-xs text-muted-foreground border-t pt-3 mt-6">
      {ECON_LABELS[locale].margin_footnote}
    </p>
  );
}
```

- [ ] **Step 6.1.3: Commit**

```bash
git commit -m "feat(phase10): econ labels + material margin footnote"
git push
```

---

### Task 6.2: `KpiTile` component + `DashboardGrid` (5 tiles)

**Files:**
- Create: `window2-portal-sandbox/components/economics/kpi-tile.tsx`
- Create: `window2-portal-sandbox/components/economics/dashboard-grid.tsx`

- [ ] **Step 6.2.1: Component test for empty-state behavior**

Vitest + Testing Library: when `value` is null, renders the empty-state copy and the link to remediation route.

- [ ] **Step 6.2.2: Implement tile + grid**

Tile shows: title, value (formatted ILS), subtitle (optional), empty-state copy when value is null. Grid composes the 5 tiles.

- [ ] **Step 6.2.3: Test PASS + commit**

---

### Task 6.3: TanStack Query hook — `use-economics-dashboard.ts`

- [ ] **Step 6.3.1: Write hook calling `GET /api/economics/dashboard`**
- [ ] **Step 6.3.2: Hook test (msw-mocked fetch)**
- [ ] **Step 6.3.3: Commit**

---

### Task 6.4: Page `app/economics/page.tsx`

- [ ] **Step 6.4.1: RLS check — page is `admin` or `planner` only**

Use the existing auth gate component (same one Inbox uses per memory `project_inbox_audience_planner_admin_only`).

- [ ] **Step 6.4.2: Compose `DashboardGrid` + `MaterialMarginFootnote`**
- [ ] **Step 6.4.3: Playwright smoke — operator role gets 403; planner gets 200; KPI tiles render**
- [ ] **Step 6.4.4: Commit**

```bash
git commit -m "feat(phase10): /economics dashboard with 5 KPIs"
git push
```

---

## Section 7: Portal — Product Economics table

### Task 7.1: `ProductEconomicsTable` component + reliability badge

**Files:**
- Create: `window2-portal-sandbox/components/economics/product-economics-table.tsx`
- Create: `window2-portal-sandbox/components/economics/reliability-badge.tsx`
- Create: `window2-portal-sandbox/components/economics/data-quality-pill.tsx`

- [ ] **Step 7.1.1: TDD component**

Render test asserts:
1. 10 columns present.
2. Default sort = `embedded_material_margin_in_stock DESC` (rows with NULL fall back to `fg_inventory_value_at_sale_price DESC`; in 10A all are NULL → fallback ordering).
3. Reliability badge shows **both** `transaction_count` and `total_qty_sold` literally (per spec §16.7).
4. Item-name column is sticky-left.
5. Filter chips: All / Missing cost / Missing sale-price / Low-reliability — default "All".

- [ ] **Step 7.1.2: Implement components**

ReliabilityBadge — always renders count + qty even when flag=NONE: shows "No transactions" instead of leaving the box blank.

- [ ] **Step 7.1.3: Commit**

---

### Task 7.2: Route `app/economics/products/page.tsx`

- [ ] **Step 7.2.1: Wire table to `use-product-economics.ts` hook**
- [ ] **Step 7.2.2: RLS gate + Playwright smoke**
- [ ] **Step 7.2.3: Commit**

---

## Section 8: Portal — Product drilldown

### Task 8.1: `CostBreakdownTable` + `CostHistoryStrip` + `SourceAttribution`

- [ ] **Step 8.1.1: TDD each component**

- [ ] **Step 8.1.2: Implement**

- [ ] **Step 8.1.3: Commit**

---

### Task 8.2: Route `app/economics/products/[item_id]/page.tsx`

- [ ] **Step 8.2.1: Compose sections A/B/C/D per spec §16.4**
- [ ] **Step 8.2.2: Component-missing cost rows render "MISSING — fix in Master Maintenance" with deep link**
- [ ] **Step 8.2.3: Commit**

---

## Section 9: Portal — Cost Data Admin

### Task 9.1: `CostAdminTabs` + Tab 1 `SupplierCostsTable`

- [ ] **Step 9.1.1: TDD tabs component**
- [ ] **Step 9.1.2: TDD `SupplierCostsTable` — default sort "stalest first"**
- [ ] **Step 9.1.3: Implement + commit**

---

### Task 9.2: Tab 2 `CostDraftsTable` + `DraftApprovalDialog`

- [ ] **Step 9.2.1: TDD draft table — flag deltas >5% visually but never auto-approve**
- [ ] **Step 9.2.2: Approval dialog — confirm copy, calls `use-approve-cost-draft.ts` mutation**
- [ ] **Step 9.2.3: Bulk action: "Approve all where delta ≤ X%" — sends N individual approvals; confirm dialog says exactly how many drafts will be approved**
- [ ] **Step 9.2.4: Commit**

---

### Task 9.3: Tab 3 `PriceHistoryList` (read-only)

- [ ] **Step 9.3.1: TDD list filtered by `supplier_item_id`**
- [ ] **Step 9.3.2: Commit**

---

### Task 9.4: Route `app/admin/cost-data/page.tsx` + `/drafts` deep link

- [ ] **Step 9.4.1: RLS — `admin` only (planner does NOT see Cost Data Admin)**
- [ ] **Step 9.4.2: Compose tabs**
- [ ] **Step 9.4.3: Playwright smoke**
- [ ] **Step 9.4.4: Commit**

---

## Section 10: G3 verification + Wave 10A closure

### Task 10.1: G3 — pick 3 verification items and run manual reconciliation

- [ ] **Step 10.1.1: With Tom, pick 3 items per spec §9 criteria:**
  - 1 single-stage MANUFACTURED with non-trivial BOM
  - 1 two-stage MANUFACTURED (base + pack with `base_fill_qty_per_unit`)
  - 1 BOUGHT_FINISHED or REPACK if any exist

- [ ] **Step 10.1.2: Run `runCogsSnapshotJob` with `source: 'manual_verification'` on dev DB**

```bash
curl -X POST -H "Authorization: Bearer $JOB_RUNNER_TOKEN" \
     https://api-dev/internal/jobs/cogs-snapshot-nightly
```

- [ ] **Step 10.1.3: Build the reconciliation table — for each of the 3 items:**

```
| item_id | expected_cogs_ils | computed_cogs_ils | delta_ils | delta_pct | cost_breakdown |
|---------|------------------:|------------------:|----------:|----------:|----------------|
| FG-...  |             14.20 |             14.27 |      0.07 |     0.49% | (full JSONB)   |
```

Tom signs the table; delta_pct must be ≤ 1% on every row.

- [ ] **Step 10.1.4: Attach the table to the Wave 10A closure record**

---

### Task 10.2: Enable pg_cron nightly entry

- [ ] **Step 10.2.1: After G3 PASS, enable the cron entry**

```sql
update cron.job set active = true where jobname = 'phase10-cogs-nightly';
```

- [ ] **Step 10.2.2: Confirm 3 consecutive nights produce one row per active item with no DEGRADED states**

```sql
select date_trunc('day', posted_at) as day, count(*) as rows_written, count(distinct item_id) as distinct_items
  from private_core.fg_cogs_snapshots
 where source = 'nightly_job'
 group by 1 order by 1 desc limit 5;
```

---

### Task 10.3: AC1–AC10 evidence pack + Wave 10A closure

- [ ] **Step 10.3.1: Author closure record at `PRODUCTION/docs/phase10/wave10a-closure.md`**

Document each of AC1–AC10 with the evidence required (spec §8 Wave 10A table). Include:
- AC7: reconciliation table from Task 10.1.3
- AC8: ux-content-state-designer label review report
- AC9: screenshots of dashboard, table, drilldown, admin (all four surfaces)
- AC10: screenshot of mandatory footnote

- [ ] **Step 10.3.2: Tom signs the closure record**

- [ ] **Step 10.3.3: Update `PRODUCTION/CURRENT_STATE.md` — mark Phase 10 Wave 10A as DONE**

- [ ] **Step 10.3.4: Commit closure record to PRODUCTION**

```bash
cd "PRODUCTION" && git add docs/phase10/wave10a-closure.md CURRENT_STATE.md
git commit -m "docs(phase10): Wave 10A closure — AC1-AC10 evidenced"
git push
```

---

# WAVE 10B — Sale-price + margin

> **Hard gate:** Wave 10B does not start until Wave 10A closure record is signed. Three preflight resolutions must land before any 10B migration: A10-1 (`lw_price_raw` currency), A10-10 (business-date column), A10-2 (returns/cancellations status filter).

## Section 11: Pre-flight resolutions (A10-1, A10-2, A10-10)

### Task 11.1: A10-1 resolution — `lw_price_raw` currency disambiguation

**Files:**
- Create: `gt-factory-os/docs/integrations/lw_price_raw_currency_resolution.md`

- [ ] **Step 11.1.1: Pull 5+ live LionWheel orders with non-null `lw_price_raw`**

```bash
psql "$DATABASE_URL" -c "
  select o.lw_order_id, l.lw_sku, l.lw_qty_ordered_raw, l.lw_price_raw, o.created_at
    from private_core.orders_mirror_lines l
    join private_core.orders_mirror o using (lw_order_id)
   where l.lw_price_raw is not null
   order by o.created_at desc
   limit 20;
"
```

- [ ] **Step 11.1.2: For each, locate the corresponding invoice (Green Invoice / Shopify confirmation) and reconcile**

Hypothesis 1: `lw_price_raw` is **gross** of VAT in ILS — divide by 1.17 for net.
Hypothesis 2: `lw_price_raw` is **net** in ILS.
Hypothesis 3: `lw_price_raw` is per-unit, not line-total.

Document the verified semantics in the resolution doc. **Tom signs.**

- [ ] **Step 11.1.3: Commit resolution doc**

---

### Task 11.2: A10-10 resolution — business-date column

**Files:**
- Modify: `gt-factory-os/docs/integrations/orders_mirror_business_date.md` (new)

- [ ] **Step 11.2.1: List candidate date columns on `orders_mirror`**

```bash
psql "$DATABASE_URL" -c "\d+ private_core.orders_mirror"
```

- [ ] **Step 11.2.2: Per Tom's locked answer — prefer delivery date if present; else invoice date; else created_at**

Test each candidate against 20 known orders: does the date match when the operator considers the sale "happened"?

- [ ] **Step 11.2.3: Tom selects the column. Document in resolution doc. Commit.**

---

### Task 11.3: A10-2 resolution — orders_mirror status values

- [ ] **Step 11.3.1: `select distinct status from private_core.orders_mirror`**
- [ ] **Step 11.3.2: Map each to keep/exclude. Tom signs. Document. Commit.**

---

## Section 12: Migration 0191 — `orders_mirror_lines.lw_price_net_ils`

### Task 12.1: Add parsed-net column + backfill

**Files:**
- Create: `gt-factory-os/db/migrations/0191_lw_price_parsed.sql`
- Test: `gt-factory-os/db/tests/0191_lw_price_parsed.test.sql`

- [ ] **Step 12.1.1: Write failing test asserting the new column exists with type `money_4dp`**

- [ ] **Step 12.1.2: Write migration**

```sql
-- ===========================================================================
-- 0191_lw_price_parsed.sql
-- ===========================================================================
-- Phase 10 Wave 10B — add parsed net-of-VAT price column on
-- orders_mirror_lines. Parser logic in api/src/sale-price/lw-price-parser.ts;
-- the poller (api/src/integrations/lionwheel/poller.ts) writes this column
-- on every upsert from now on. Migration is additive; old NULL rows backfilled
-- by Task 13.2.
--
-- Currency / VAT semantics fixed by A10-1 (see docs/integrations/lw_price_raw_currency_resolution.md).
-- ===========================================================================

begin;
set search_path to private_core, public;

alter table private_core.orders_mirror_lines
  add column lw_price_net_ils private_core.money_4dp;

comment on column private_core.orders_mirror_lines.lw_price_net_ils is
  'Parsed net-of-VAT unit price in ILS. Semantics fixed by A10-1 resolution doc. Written by poller after parser lands; backfilled in Task 13.2.';

commit;
```

- [ ] **Step 12.1.3: Apply, re-test PASS, commit**

---

## Section 13: `lw-price-parser.ts` + poller wiring + backfill

### Task 13.1: `lw-price-parser.ts`

**Files:**
- Create: `gt-factory-os/api/src/sale-price/lw-price-parser.ts`
- Test: `gt-factory-os/api/src/sale-price/__tests__/lw-price-parser.test.ts`

- [ ] **Step 13.1.1: TDD — at least 8 cases including: gross-VAT inputs, edge precision, malformed strings (return null), known reconciled invoices**

- [ ] **Step 13.1.2: Implement parser per A10-1 resolution**

- [ ] **Step 13.1.3: Wire into poller — write `lw_price_net_ils` alongside existing `lw_price_raw` capture**

- [ ] **Step 13.1.4: Commit**

---

### Task 13.2: Backfill existing rows

- [ ] **Step 13.2.1: Backfill script reads all non-null `lw_price_raw` rows, parses, writes `lw_price_net_ils`**

Idempotent: only updates rows where `lw_price_net_ils IS NULL`.

- [ ] **Step 13.2.2: Run on dev. Spot-check 10 rows. Tom sign-off.**

- [ ] **Step 13.2.3: Run on prod (Tom executes; integration-boundary-executor authors). Commit script.**

---

## Section 14: Migration 0192 — `fg_avg_sale_price_snapshots`

### Task 14.1: Migration + pgTAP

**Files:**
- Create: `gt-factory-os/db/migrations/0192_fg_avg_sale_price_snapshots.sql`
- Test: `gt-factory-os/db/tests/0192_fg_avg_sale_price_snapshots.test.sql`

- [ ] **Step 14.1.1: TDD per spec §3.1.2 — 12 assertions covering existence, types, append-only triggers, period_end >= period_start CHECK, reliability_flag CHECK, source CHECK**

- [ ] **Step 14.1.2: Write migration (full DDL copied from spec §3.1.2)**

- [ ] **Step 14.1.3: Apply, PASS, commit**

---

## Section 15: Monthly avg-sale-price job

### Task 15.1: `avg-sale-price-job.ts`

**Files:**
- Create: `gt-factory-os/api/src/sale-price/avg-sale-price-job.ts`
- Test: `gt-factory-os/api/src/sale-price/__tests__/avg-sale-price-job.test.ts`

- [ ] **Step 15.1.1: TDD — at minimum these cases**

1. Item with 0 mappable transactions in window → snapshot written with `avg_sale_price_ils=NULL`, `transaction_count=0`, `reliability_flag='NONE'`.
2. Item with 1 transaction → `LOW` flag.
3. Item with 6 transactions covering multiple unit counts → qty-weighted average matches manual calculation.
4. Returns/cancelled orders excluded.
5. SKU not in `integration_sku_map` (or status `pending`/`rejected`) → not counted.
6. Run produces shared `run_id`; window uses the column resolved in A10-10.

- [ ] **Step 15.1.2: Implement**

```typescript
// Monthly aggregator: writes one fg_avg_sale_price_snapshots row per active
// FG item. Window = last 30 days ending on run date. Business-date column
// = <resolved via A10-10>. SKU resolver = existing
// api/src/integrations/lionwheel/sku_resolver.ts.
//
// Spec §5; plan §15.

import { v4 as uuidv4 } from 'uuid';
import type { Kysely } from 'kysely';
import type { Database } from '../db/schema';

const RELIABILITY_THRESHOLDS = { LOW_MIN: 1, HIGH_MIN: 5 } as const;

export async function runAvgSalePriceJob(
  db: Kysely<Database>,
  opts: { source: 'monthly_job' | 'manual_verification' | 'backfill'; actor_user_id?: string | null; actor_snapshot?: string }
) {
  const runId = uuidv4();
  const periodEnd = new Date();
  const periodStart = new Date(periodEnd.getTime() - 30 * 24 * 60 * 60 * 1000);
  const actorSnapshot = opts.actor_snapshot ?? '<system:avg-sale-price-job>';

  // Aggregate via single SQL — qty-weighted average, filter by status,
  // SKU map join. Replace <business_date_column> with A10-10 result.
  const rows = await db
    .selectFrom('private_core.orders_mirror_lines as l')
    .innerJoin('private_core.orders_mirror as o', 'o.lw_order_id', 'l.lw_order_id')
    .innerJoin('private_core.integration_sku_map as m', join =>
      join.onRef('m.external_sku', '=', 'l.lw_sku')
          .on('m.source_channel', '=', 'lionwheel')
          .on('m.approval_status', '=', 'approved'))
    .select([
      'm.item_id',
      // qty-weighted: sum(qty*price) / sum(qty)
      db.fn.sum<string>(db.dynamic.ref('l.lw_qty_ordered * l.lw_price_net_ils')).as('weighted_total'),
      db.fn.sum<string>('l.lw_qty_ordered').as('qty_sum'),
      db.fn.count<number>('l.lw_order_item_id').as('tx_count'),
    ])
    .where(/* A10-10 column */ 'o.created_at', '>=', periodStart)
    .where(/* A10-10 column */ 'o.created_at', '<', periodEnd)
    .where('o.status', 'not in', /* A10-2 excluded values */ ['cancelled','returned'])
    .where('l.lw_price_net_ils', 'is not', null)
    .where('l.lw_qty_ordered', '>', '0')
    .groupBy('m.item_id')
    .execute();

  // Also write NONE-rows for active items with no transactions.
  const allActive = await db
    .selectFrom('private_core.items')
    .select('item_id')
    .where('status', '=', 'ACTIVE')
    .execute();
  const seen = new Set(rows.map(r => r.item_id));

  const inserts: any[] = [];
  for (const r of rows) {
    const qtySum = parseFloat(r.qty_sum);
    const weighted = parseFloat(r.weighted_total);
    const avg = qtySum > 0 ? (weighted / qtySum).toFixed(4) : null;
    const txCount = Number(r.tx_count);
    const flag = txCount >= RELIABILITY_THRESHOLDS.HIGH_MIN ? 'HIGH'
              : txCount >= RELIABILITY_THRESHOLDS.LOW_MIN  ? 'LOW'
              : 'NONE';
    inserts.push({
      item_id: r.item_id,
      avg_sale_price_ils: avg,
      period_start: periodStart, period_end: periodEnd,
      transaction_count: txCount, total_qty_sold: qtySum.toString(),
      reliability_flag: flag, run_id: runId, source: opts.source,
      actor_user_id: opts.actor_user_id ?? null, actor_snapshot: actorSnapshot,
      filter_meta: JSON.stringify({
        excluded_statuses: ['cancelled','returned'],
        business_date_column: '<resolved A10-10>',
        lw_price_parser_version: 'v1',
        currency_assumption: 'ILS-net-of-VAT',
      }),
    });
  }
  for (const i of allActive) {
    if (seen.has(i.item_id)) continue;
    inserts.push({
      item_id: i.item_id, avg_sale_price_ils: null,
      period_start: periodStart, period_end: periodEnd,
      transaction_count: 0, total_qty_sold: '0', reliability_flag: 'NONE',
      run_id: runId, source: opts.source, actor_snapshot: actorSnapshot,
      filter_meta: JSON.stringify({}),
    });
  }

  if (inserts.length > 0) {
    await db.insertInto('private_core.fg_avg_sale_price_snapshots').values(inserts).execute();
  }
  return { run_id: runId, items_processed: inserts.length };
}
```

- [ ] **Step 15.1.3: Run tests — PASS all 6**

- [ ] **Step 15.1.4: Commit**

---

### Task 15.2: pg_cron entry (monthly, disabled until G10)

Same pattern as Task 1.4. Migration 0194 inserts `phase10-avg-sale-price-monthly` with schedule `0 3 1 * *` (1st of month at 03:00) and `active=false`.

- [ ] **Step 15.2.1: Write + commit**

---

## Section 16: Migration 0193 — `v_fg_economics` v2 (sale-price live)

### Task 16.1: Rebuild view with sale-price + margin columns populated

**Files:**
- Create: `gt-factory-os/db/migrations/0193_v_fg_economics_v2.sql`
- Test: `gt-factory-os/db/tests/0193_v_fg_economics_v2.test.sql`

- [ ] **Step 16.1.1: Test — same 18 columns; new invariants**

- Rows with `transaction_count > 0` and `cogs_complete=true` and `cogs_per_unit_ils IS NOT NULL` MUST produce non-null `material_margin_ils` and `material_margin_pct`.
- Rows with `transaction_count = 0` MUST still have `avg_sale_price_ils IS NULL` and all sale-price-derived fields NULL.
- "Fabrication guard": no row should have `avg_sale_price_ils IS NOT NULL` while `transaction_count = 0` (spec §5.6).

- [ ] **Step 16.1.2: Write migration**

```sql
-- ===========================================================================
-- 0193_v_fg_economics_v2.sql
-- ===========================================================================
-- Phase 10 Wave 10B — replace v_fg_economics with the full sale-price-aware
-- version. Column SHAPE unchanged from v1 (migration 0189) so all consumer
-- code keeps working — only values change.
--
-- Spec §3.2; plan §16.
-- ===========================================================================

begin;
set search_path to private_core, public;

create or replace view private_core.v_fg_economics as
-- Full body from spec §3.2, this time with the latest_asp CTE joined.
-- (Reproduce the full SQL from spec §3.2 here.)
...;

commit;
```

(Full body matches spec §3.2 verbatim — reproduce when writing the migration; do not abbreviate.)

- [ ] **Step 16.1.3: Apply, PASS, commit**

---

## Section 17: Portal — enable sale-price/margin surfaces

### Task 17.1: KPIs 1/3/4 populate; Product Economics margin columns populate; drilldown sale-price history appears

No new components — the existing components already read the column shape. The values just stop being NULL.

- [ ] **Step 17.1.1: Verify on dev — open `/economics`, see all 5 KPIs populated**
- [ ] **Step 17.1.2: Open Product Economics table — sale-price and margin columns populated; reliability badges show both numbers**
- [ ] **Step 17.1.3: Open a drilldown — history strip shows ~6 monthly avg sale-price snapshots in addition to the COGS history**
- [ ] **Step 17.1.4: Playwright smoke against all three surfaces**
- [ ] **Step 17.1.5: Commit any small tweaks needed**

---

## Section 18: Reconciliation + Wave 10B closure

### Task 18.1: Reconcile ≥5 known invoice prices vs `avg_sale_price_ils`

- [ ] **Step 18.1.1: Pick 5 SKUs with high transaction count (`reliability_flag='HIGH'`)**

- [ ] **Step 18.1.2: For each, compute the qty-weighted average manually from the underlying invoices for the same 30-day window**

- [ ] **Step 18.1.3: Build reconciliation table — delta_pct ≤ 1% required**

- [ ] **Step 18.1.4: Tom signs**

---

### Task 18.2: Enable the monthly cron entry

```sql
update cron.job set active = true where jobname = 'phase10-avg-sale-price-monthly';
```

- [ ] **Step 18.2.1: Confirm next scheduled run, then verify on day-of**

---

### Task 18.3: Wave 10B closure record + Phase 10 full-closure

- [ ] **Step 18.3.1: Author `PRODUCTION/docs/phase10/wave10b-closure.md`** — AC11–AC17 with evidence

- [ ] **Step 18.3.2: Tom signs**

- [ ] **Step 18.3.3: Author `PRODUCTION/docs/phase10/phase10-full-closure.md`** — references both wave records, marks Phase 10 fully closed

- [ ] **Step 18.3.4: Update `PRODUCTION/CURRENT_STATE.md` — Phase 10 status → DONE**

- [ ] **Step 18.3.5: Commit + push**

```bash
git commit -m "docs(phase10): Wave 10B + full Phase 10 closure"
git push
```

---

# Validation gates summary

| Gate | Wave | Trigger | Pass criteria | Fail action |
|---|---|---|---|---|
| G1 | — | Spec ready | Tom signs spec G1 | Stop — revise spec |
| G2 | 10A | Migrations 0187–0189 + 0190 applied | All pgTAP PASS, all columns/triggers verified | Drop & re-author migration (forward-only — no rollback DDL written, but dev DB can be reseeded) |
| G3 | 10A | COGS snapshot job runs on dev | Reconciliation table ≤1% delta on 3 items, Tom signs | Root-cause: usually missing supplier_items row, wrong pack_conversion, stale purchase_to_inv_factor. Fix master data, rerun. Do NOT modify cogs-rollup.ts to compensate. |
| G4 | 10A | Portal dashboard + table + drilldown + admin live on dev | Playwright smokes PASS; RLS gates verified; labels match spec §7 | Fix portal; do not relax spec §7 labels |
| G5 | 10A | GI prefill draft → admin approval E2E test PASSes | One transaction observably writes `supplier_items` + `price_history` + `change_log` + draft flips status | Test handler in isolation; never bypass atomicity |
| G6 | 10A | Wave 10A closure record | AC1–AC10 evidenced; Tom signs | Address gaps before claiming closure |
| G7 | 10B-gate | A10-1 resolved | Resolution doc signed by Tom | Halt 10B until resolved — do NOT proceed with assumed semantics |
| G8 | 10B-gate | A10-10 resolved | Resolution doc signed | Halt 10B |
| G9 | 10B | Migrations 0191–0193 applied | pgTAP PASS | Drop & re-author |
| G10 | 10B | Monthly job + reconciliation | ≤1% delta on ≥5 SKUs, Tom signs | Root-cause parser or filter; do not fudge |
| G11 | 10B | Portal sale-price/margin surfaces live | Playwright PASS | Fix portal |
| G12 | 10B | Phase 10 full closure | AC11–AC17 evidenced + both wave records cited | Address gaps |

---

# Rollback points

Forward-only schema policy (per CLAUDE.md). Rollback at each gate means **stop and fix, do not rollback the migration**. Specific recoverability:

| Gate | If failed, the safe state is | How to recover |
|---|---|---|
| After G2 | Tables exist but unused | Forward fix or drop+re-add via additive migration |
| After G3 | Snapshot rows written but cron disabled | Truncate dev fg_cogs_snapshots; re-run after master-data fix. Prod has no snapshots yet because cron stays off until G3 PASS. |
| After G4 | UI live but only reads existing data | Hide route via feature flag; fix; re-enable |
| After G5 | Draft approval broken | Disable Cost Data Admin Tab 2 route; fix handler tests; re-enable. Inline supplier-cost editing (Tab 1) shares the handler so it's gated by the same fix. |
| After G6 (Wave 10A closed) | Stable cost-only experience | Permanent stable state until Wave 10B starts |
| After G9 | Column on `orders_mirror_lines` exists, view rebuilt | Forward-only — view can be reverted to v1 by re-applying 0189 if needed (additive replacement via `create or replace view`) |
| After G10 | Snapshots written but cron disabled | Same as G3 — truncate dev avg-sale-price snapshots; fix parser/filter; rerun |
| After G11 | UI surfaces toggleable | Same as G4 |

**No `DROP TABLE` is ever appropriate for prod recovery on Phase 10 tables** — they are append-only audit surfaces. If a Phase 10 table needs to be reset on prod, the operation is `TRUNCATE` with Tom approval + audit trail; never `DROP`.

---

# Owner per gate

| Gate | Primary owner | Secondary | Tom action |
|---|---|---|---|
| G1 | factory-os-governor (gating) | (spec author) | Sign |
| G2 | backend-db-executor | verifier | — |
| G3 | backend-db-executor | (Tom for reconciliation review) | Sign reconciliation table |
| G4 | portal-production-executor | accessibility-usability-auditor + ux-content-state-designer | — |
| G5 | integration-boundary-executor (GI ingest) + backend-db-executor (approval handler) + portal-production-executor (UI) | verifier | — |
| G6 | factory-os-governor | release-verifier | Sign closure record |
| G7 | integration-boundary-executor | (Tom validates samples) | Sign A10-1 doc |
| G8 | integration-boundary-executor | (Tom validates samples) | Sign A10-10 doc |
| G9 | backend-db-executor | verifier | — |
| G10 | backend-db-executor | (Tom for reconciliation review) | Sign reconciliation table |
| G11 | portal-production-executor | accessibility-usability-auditor | — |
| G12 | factory-os-governor | release-verifier | Sign full closure |

---

# Evidence per AC

| AC | Wave | Evidence artifact location |
|---|---|---|
| AC1 | 10A | pgTAP output `db/tests/0187_fg_cogs_snapshots.test.sql` — 14/14 |
| AC2 | 10A | pgTAP output `db/tests/0188_supplier_cost_drafts.test.sql` — 11/11 |
| AC3 | 10A | pgTAP `db/tests/0189_v_fg_economics_v1.test.sql` — 20/20 + handler tests `api/src/cost-drafts/__tests__/approve-cost-draft.test.ts` PASS 5/5 |
| AC4 | 10A | `\d+ private_core.v_fg_economics` output attached to closure |
| AC5 | 10A | 3 consecutive nightly cron run summaries from `audit_runs` table |
| AC6 | 10A | E2E test transcript: ingest → admin approve → 4-step atomic write verified |
| AC7 | 10A | Reconciliation table from Task 10.1.3 + Tom signature |
| AC8 | 10A | ux-content-state-designer review report at `docs/phase10/ux-labels-audit.md` |
| AC9 | 10A | Playwright artifacts + screenshots of all 4 surfaces at `docs/phase10/wave10a-screenshots/` |
| AC10 | 10A | Screenshot of mandatory footnote on Dashboard, Product Economics, Drilldown |
| AC11 | 10B | pgTAP output `db/tests/0192_fg_avg_sale_price_snapshots.test.sql` |
| AC12 | 10B | `docs/integrations/lw_price_raw_currency_resolution.md` signed; parser tests PASS |
| AC13 | 10B | `docs/integrations/orders_mirror_business_date.md` signed |
| AC14 | 10B | Monthly job run summary; ≥1 SKU HIGH + ≥1 SKU LOW |
| AC15 | 10B | Reconciliation table from Task 18.1 + Tom signature |
| AC16 | 10B | Playwright artifacts of dashboard + table + drilldown with sale-price populated |
| AC17 | 10B | Screenshot of reliability badge showing both `transaction_count` and `total_qty_sold` |

---

# Self-review

**Spec coverage check:**

| Spec section | Plan task |
|---|---|
| §2 Architecture decision (B primary) | All Wave 10A snapshot tables are append-only — confirmed §1.1, §1.2; Approach A as verification only — supported by `runCogsSnapshotJob({ source: 'manual_verification' })` in Task 10.1.2 |
| §3.1.1 `fg_cogs_snapshots` | Task 1.1 |
| §3.1.2 `fg_avg_sale_price_snapshots` | Task 14.1 |
| §3.1.3 `supplier_cost_drafts` | Task 1.2 |
| §3.2 `v_fg_economics` (18 cols) | Tasks 1.3 (v1) + 16.1 (v2) |
| §4 COGS computation | Task 2.1 (rollup) + Task 2.2 (job) |
| §5 Avg sale price computation | Task 15.1 |
| §6 GI prefill flow | Tasks 3.1 + 4.1 + 9.2 |
| §7 Financial labeling | Task 6.1 (labels.ts) + Task 6.2 (footnote) + AC10 evidence |
| §8 AC1–AC17 | "Evidence per AC" table above |
| §9 Verification gate | Task 10.1 |
| §10 Migration sequence | Tasks 1.1–1.4, 12.1, 14.1, 15.2, 16.1 |
| §11 A10-1..A10-10 open assumptions | Tasks 11.1–11.3 (resolutions); A10-3 verified at Task 3.1.1; A10-4 carry-forward documented in Task 2.1.3 comment; A10-5 implicitly handled via Path B reuse; A10-6 thresholds in Task 15.1.2 constants; A10-7 covered by §10 cron tasks; A10-8 pre-resolved via existing sku_resolver.ts; A10-9 verified at Task 1.3.1 |
| §12 Out of scope | (No plan task — out of scope by design) |
| §13 Gates G1–G12 | "Validation gates summary" table |
| §14 Stop conditions | Embedded throughout — §1.1.1 trigger tests assert UPDATE/DELETE forbidden; §4.1.1 tests assert no partial state ever; §16.1.1 fabrication-guard test |
| §15 Open Qs | All 4 answered above (Tom's locked answers) |
| §16 UX Contract — 4 surfaces | Sections 6, 7, 8, 9 |
| §16.6 material margin naming | Task 6.1 labels.ts + all view/test references use `material_margin_*` |
| §16.7 both numbers in reliability | Task 7.1.1 test assertion #3 |
| §16.8 Wave 10A / 10B split | Entire plan structure |

No gaps. No placeholders below the "TODO" line.

**Placeholder scan:** plan body contains explicit `<business_date_column>` markers in §5.3 SQL and Task 15.1.2 — these are deliberately marked open until G8 unblocks them and resolves to a concrete column name. The plan **does not** instruct anyone to ship code with those markers in place; Task 15.1.2 explicitly says "Replace `<business_date_column>` with A10-10 result."

**Type consistency:** `material_margin_ils` / `material_margin_pct` / `embedded_material_margin_in_stock` used uniformly across labels.ts (Task 6.1), view (Task 1.3 + Task 16.1), test assertions (Task 1.3.2), and AC table. `cogs_complete` / `cogs_per_unit_ils` / `missing_cost_components` / `cost_breakdown` / `supply_method_snapshot` / `run_id` / `source` used uniformly. `transaction_count` / `total_qty_sold` / `reliability_flag` used uniformly.

---

# Execution handoff

**Plan complete and saved to `docs/superpowers/plans/2026-05-13-phase10-economics-layer.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration. Best fit for this plan because Phase 10 has ~40 discrete tasks across backend/portal/DB with mostly-independent verification gates.

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints. Reasonable if Tom wants to watch every step land in real time.

**Which approach?**

Reminder: nothing executes until you sign off the plan itself.
