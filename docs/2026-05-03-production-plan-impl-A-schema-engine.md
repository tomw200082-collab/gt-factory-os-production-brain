# Daily Production Plan — Implementation Plan A: Schema + Engine SQL (REVISION 2)

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land the database foundation that turns approved per-FG production recommendations into a base-grouped weekly schedule respecting the 500 L batch cap, 1-batch-per-day default, and reorder-point projection.

**Architecture:** Two consolidated migrations extend `production_plan` (new columns + new status enum + rewritten cancellation-consistency check + new column on `planning_run_recommendations`) and seed the key-value `planning_policy` with new policy keys. A third migration adds the SQL engine function (`fn_propose_weekly_production_plan`) that reads policy by key, schedules base batches, and logs `planning_run_exceptions` for any rec whose item lacks `base_bom_head_id` / `base_fill_qty_per_unit`. A fourth migration exposes the daily projection view (`api_read.v_daily_inventory_projection`). All implementation is **SQL-only** — no API or portal work in this plan. Existing per-FG recommendation flow (`fn_generate_production_recommendations`) is untouched and keeps working in parallel.

**Tech Stack:** PostgreSQL 17 (Supabase managed), pgTAP for tests, plain `psql` via `node` `pg` driver for canonical apply (Tom's convention; no Supabase migration tooling). Migrations are forward-only, hand-numbered, applied to `private_core` schema.

**Reference spec:** `PRODUCTION/docs/2026-05-03-daily-production-plan-design.md` — sections 2 (data model), 3 (engine policy), 7 (state machine), 9 (schema changes).

**Repo:** `c:/Users/tomw2/Projects/gt-factory-os` (canonical SQL + tests live in `db/migrations/` and `db/tests/`).

**Last applied migration on live DB:** `0132_pre_launch_cleanup.sql`. This plan starts at `0133`.

---

## Revision history

- **REV 2 (2026-05-03):** Rewrite after executor-w1 contract_failure on REV 1 pre-flight. Changes:
  - **Chunk 1** consolidated to one migration (0133) that adds the 6 new columns AND extends the `status` enum to `('draft','planned','in_production','completed','cancelled')` AND rewrites `production_plan_cancellation_consistency` for the new lifecycle AND adds `planning_run_recommendations.consumed_by_proposal_id`.
  - **Chunk 2** rewritten for the **key-value** `planning_policy` (Tom Decision-1: A). Previous "wide-column ALTER" approach abandoned. Now an INSERT/UPDATE seed of 4 new namespaced keys.
  - **Chunk 3** engine SQL revised: reads policy by key from key-value table; uses uppercase `'UNIT'` for `uom_code`; logs `planning_run_exception` (category `engine_missing_base_metadata`) for any approved rec whose item has NULL `base_bom_head_id` or `base_fill_qty_per_unit`; inserts production_plan rows with `status='draft'`.
  - **Chunk 4** unchanged.
  - **Chunk 5** unchanged.
  - **Pre-flight P1-P5** already executed by executor-w1 in REV 1 attempt; inspector output preserved at `scripts/_inspect_production_plan_schema.out.txt`. Engineer can re-run if state has shifted.

---

## Live schema baseline (verified by inspector — REV 1 pre-flight)

The plan's migrations are written against this exact state. If anything has shifted, re-run `node scripts/_inspect_production_plan_schema.mjs` and reconcile before proceeding.

### `private_core.production_plan` (20 columns, 0 rows post-cleanup)

```
plan_id uuid PK default gen_random_uuid()
plan_date date NOT NULL
item_id text NOT NULL
planned_qty numeric NOT NULL  -- CHECK > 0
uom text NOT NULL  -- FK to private_core.uom(uom_code), uppercase only
status text NOT NULL DEFAULT 'planned'  -- CHECK ('planned','cancelled')
source_recommendation_id uuid NULL
bom_version_id_pinned uuid NULL
notes text NULL
idempotency_key text NULL
created_by_user_id uuid NOT NULL
created_by_snapshot text NOT NULL
created_at timestamptz NOT NULL DEFAULT now()
updated_at timestamptz NOT NULL DEFAULT now()
updated_by_user_id uuid NULL
updated_by_snapshot text NULL
cancelled_at timestamptz NULL
cancelled_by_user_id uuid NULL
cancel_reason text NULL
completed_submission_id uuid NULL
```

CHECK constraints:
```
production_plan_status_check:
  CHECK (status = ANY (ARRAY['planned','cancelled']))

production_plan_cancellation_consistency:
  CHECK (
    (status='cancelled' AND cancelled_at IS NOT NULL AND cancelled_by_user_id IS NOT NULL AND completed_submission_id IS NULL)
    OR
    (status='planned' AND cancelled_at IS NULL AND cancelled_by_user_id IS NULL AND cancel_reason IS NULL)
  )

production_plan_qty_positive:
  CHECK (planned_qty > 0)
```

### `private_core.planning_policy` (5 columns, 15 rows, KEY-VALUE)

```
key text NOT NULL  (PK)
value text NOT NULL
uom text NULL
description text NULL
updated_at timestamptz NOT NULL DEFAULT now()
```

Existing relevant keys (sample):
- `EXTRACTS_MAX_BATCH_L = '500'` (uom='L')  ← already what we want for `batch_size_l`
- `COCKTAILS_MAX_BATCH_L = '500'` (uom='L')
- `stale_count_days = '7'`
- `count_freeze_open_expiry_minutes = '60'`
- `dataentry_correction_window_days = '7'`

### `private_core.planning_run_recommendations` (30 columns)

Of interest: `recommendation_id, recommendation_type, recommendation_status, item_id, recommended_qty, target_period_bucket_key, shortage_date, approved_by_user_id, approved_at`. **Does NOT have `consumed_by_proposal_id`** — Plan A (this REV) adds it.

### `private_core.items` (24 columns)

Of interest: `item_id, supply_method, base_bom_head_id, base_fill_qty_per_unit`. Coverage gaps from REV 1 P4: 47 of 200 approved recs reference items with NULL `base_bom_head_id`; 50 with NULL `base_fill_qty_per_unit`. Total affected ≈ 59 of 200 (30%). The engine in Chunk 3 logs these as exceptions instead of silently skipping.

### `private_core.uom` (FK target for production_plan.uom)

Valid `uom_code` values are **uppercase**: `BAG, BOTTLE, BOX, CASE, G, KG, L, MG, ML, PCS, TIN, TON, UNIT`.

---

## Chunk 1: Migration 0133 — production_plan extensions + status lifecycle + recommendations.consumed_by_proposal_id

**Purpose:** One consolidated migration that does all the schema groundwork for the base-batch flow. Combined to avoid in-flight schema states (e.g., function in Chunk 3 references `consumed_by_proposal_id` so it must exist before Chunk 3 lands; we keep them adjacent).

**Files:**
- Create: `db/migrations/0133_production_plan_base_batch_extensions.sql`
- Create: `db/tests/0133_production_plan_base_batch_extensions.test.sql`

### Test first (TDD)

- [ ] **Step 1.1: Write the failing pgTAP test**

```sql
-- db/tests/0133_production_plan_base_batch_extensions.test.sql
BEGIN;
SELECT plan(28);

-- ===========================================================
-- A. New columns on production_plan
-- ===========================================================
SELECT has_column('private_core', 'production_plan', 'base_bom_head_id',
  'production_plan.base_bom_head_id exists');
SELECT has_column('private_core', 'production_plan', 'pack_manifest',
  'production_plan.pack_manifest exists');
SELECT has_column('private_core', 'production_plan', 'linked_recommendation_ids',
  'production_plan.linked_recommendation_ids exists');
SELECT has_column('private_core', 'production_plan', 'proposal_id',
  'production_plan.proposal_id exists');
SELECT has_column('private_core', 'production_plan', 'is_user_modified',
  'production_plan.is_user_modified exists');
SELECT has_column('private_core', 'production_plan', 'batch_size_l',
  'production_plan.batch_size_l exists');

SELECT col_type_is('private_core', 'production_plan', 'base_bom_head_id', 'text',
  'base_bom_head_id is text');
SELECT col_type_is('private_core', 'production_plan', 'pack_manifest', 'jsonb',
  'pack_manifest is jsonb');
SELECT col_type_is('private_core', 'production_plan', 'linked_recommendation_ids', 'uuid[]',
  'linked_recommendation_ids is uuid[]');
SELECT col_type_is('private_core', 'production_plan', 'is_user_modified', 'boolean',
  'is_user_modified is boolean');
SELECT col_type_is('private_core', 'production_plan', 'batch_size_l', 'numeric',
  'batch_size_l is numeric');

SELECT col_default_is('private_core', 'production_plan', 'pack_manifest', '''[]''::jsonb',
  'pack_manifest defaults to []');
SELECT col_default_is('private_core', 'production_plan', 'is_user_modified', 'false',
  'is_user_modified defaults to false');
SELECT col_default_is('private_core', 'production_plan', 'batch_size_l', '500',
  'batch_size_l defaults to 500');

SELECT col_is_fk('private_core', 'production_plan', 'base_bom_head_id',
  'base_bom_head_id is FK');

-- ===========================================================
-- B. Extended status enum
-- ===========================================================
SELECT lives_ok(
  $$ INSERT INTO private_core.production_plan
       (plan_date, item_id, planned_qty, uom, status,
        created_by_user_id, created_by_snapshot)
     SELECT '2030-01-01', i.item_id, 1, 'UNIT', 'draft',
            (SELECT user_id FROM private_core.app_users WHERE email='tom@gteveryday.com'),
            'pgTAP fixture'
       FROM private_core.items i WHERE i.supply_method='MANUFACTURED' LIMIT 1 $$,
  'status=draft is now accepted');

SELECT lives_ok(
  $$ INSERT INTO private_core.production_plan
       (plan_date, item_id, planned_qty, uom, status,
        created_by_user_id, created_by_snapshot)
     SELECT '2030-01-02', i.item_id, 1, 'UNIT', 'in_production',
            (SELECT user_id FROM private_core.app_users WHERE email='tom@gteveryday.com'),
            'pgTAP fixture'
       FROM private_core.items i WHERE i.supply_method='MANUFACTURED' LIMIT 1 $$,
  'status=in_production is now accepted');

SELECT lives_ok(
  $$ INSERT INTO private_core.production_plan
       (plan_date, item_id, planned_qty, uom, status, completed_submission_id,
        created_by_user_id, created_by_snapshot)
     SELECT '2030-01-03', i.item_id, 1, 'UNIT', 'completed',
            gen_random_uuid(),
            (SELECT user_id FROM private_core.app_users WHERE email='tom@gteveryday.com'),
            'pgTAP fixture'
       FROM private_core.items i WHERE i.supply_method='MANUFACTURED' LIMIT 1 $$,
  'status=completed (with completed_submission_id) is accepted');

SELECT throws_ok(
  $$ INSERT INTO private_core.production_plan
       (plan_date, item_id, planned_qty, uom, status,
        created_by_user_id, created_by_snapshot)
     SELECT '2030-01-04', i.item_id, 1, 'UNIT', 'completed',
            (SELECT user_id FROM private_core.app_users WHERE email='tom@gteveryday.com'),
            'pgTAP fixture'
       FROM private_core.items i WHERE i.supply_method='MANUFACTURED' LIMIT 1 $$,
  '23514',
  NULL,
  'status=completed without completed_submission_id is rejected');

SELECT throws_ok(
  $$ INSERT INTO private_core.production_plan
       (plan_date, item_id, planned_qty, uom, status,
        created_by_user_id, created_by_snapshot)
     SELECT '2030-01-05', i.item_id, 1, 'UNIT', 'bogus',
            (SELECT user_id FROM private_core.app_users WHERE email='tom@gteveryday.com'),
            'pgTAP fixture'
       FROM private_core.items i WHERE i.supply_method='MANUFACTURED' LIMIT 1 $$,
  '23514',
  NULL,
  'unknown status is rejected');

-- ===========================================================
-- C. Cancellation-consistency under new lifecycle
-- ===========================================================
SELECT throws_ok(
  $$ INSERT INTO private_core.production_plan
       (plan_date, item_id, planned_qty, uom, status,
        cancelled_at,
        created_by_user_id, created_by_snapshot)
     SELECT '2030-01-06', i.item_id, 1, 'UNIT', 'draft',
            now(),
            (SELECT user_id FROM private_core.app_users WHERE email='tom@gteveryday.com'),
            'pgTAP fixture'
       FROM private_core.items i WHERE i.supply_method='MANUFACTURED' LIMIT 1 $$,
  '23514',
  NULL,
  'draft with cancelled_at populated is rejected');

SELECT throws_ok(
  $$ INSERT INTO private_core.production_plan
       (plan_date, item_id, planned_qty, uom, status,
        created_by_user_id, created_by_snapshot)
     SELECT '2030-01-07', i.item_id, 1, 'UNIT', 'cancelled',
            (SELECT user_id FROM private_core.app_users WHERE email='tom@gteveryday.com'),
            'pgTAP fixture'
       FROM private_core.items i WHERE i.supply_method='MANUFACTURED' LIMIT 1 $$,
  '23514',
  NULL,
  'cancelled without cancelled_at + cancelled_by_user_id is rejected');

-- ===========================================================
-- D. pack_manifest array constraint
-- ===========================================================
SELECT throws_ok(
  $$ INSERT INTO private_core.production_plan
       (plan_date, item_id, planned_qty, uom, status, pack_manifest,
        created_by_user_id, created_by_snapshot)
     SELECT '2030-01-08', i.item_id, 1, 'UNIT', 'draft',
            '{"not": "an array"}'::jsonb,
            (SELECT user_id FROM private_core.app_users WHERE email='tom@gteveryday.com'),
            'pgTAP fixture'
       FROM private_core.items i WHERE i.supply_method='MANUFACTURED' LIMIT 1 $$,
  '23514',
  NULL,
  'pack_manifest must be a JSON array');

-- ===========================================================
-- E. planning_run_recommendations.consumed_by_proposal_id
-- ===========================================================
SELECT has_column('private_core', 'planning_run_recommendations', 'consumed_by_proposal_id',
  'planning_run_recommendations.consumed_by_proposal_id exists');
SELECT col_type_is('private_core', 'planning_run_recommendations', 'consumed_by_proposal_id', 'uuid',
  'consumed_by_proposal_id is uuid');

-- ===========================================================
-- F. Indexes
-- ===========================================================
SELECT has_index('private_core', 'production_plan', 'idx_production_plan_base_date',
  'idx_production_plan_base_date exists');
SELECT has_index('private_core', 'production_plan', 'idx_production_plan_proposal',
  'idx_production_plan_proposal exists');
SELECT has_index('private_core', 'planning_run_recommendations', 'idx_planning_run_recs_consumed_proposal',
  'idx_planning_run_recs_consumed_proposal exists');

SELECT * FROM finish();
ROLLBACK;
```

- [ ] **Step 1.2: Run pgTAP, expect failures**

```bash
node scripts/_run_pgtap.mjs db/tests/0133_production_plan_base_batch_extensions.test.sql
```

(If `_run_pgtap.mjs` doesn't exist, model after `scripts/_apply_0132.mjs`: open one transaction, execute the test SQL, capture the test plan output. The pgTAP `finish()` returns rows; success = no FAIL lines.)

Expected: many failures (columns missing, status enum still rejects new values, consumed_by_proposal_id missing, etc.).

### Implementation

- [ ] **Step 1.3: Write the migration**

```sql
-- db/migrations/0133_production_plan_base_batch_extensions.sql
--
-- Single consolidated migration that:
--   A. Adds 6 new columns to production_plan (per spec §2.1 / §9)
--   B. Extends the status enum to support the full base-batch lifecycle
--      (per spec §7): draft → planned → in_production → completed | cancelled
--   C. Rewrites production_plan_cancellation_consistency to govern all 5 statuses
--   D. Adds an array-shape CHECK on pack_manifest
--   E. Adds planning_run_recommendations.consumed_by_proposal_id (per spec §9)
--   F. Adds supporting indexes
--
-- Backward compatible: 0 existing production_plan rows; default status flips
-- from 'planned' to 'draft' for newly-created proposal rows but the column
-- default itself stays 'planned' (existing handlers that don't set status
-- continue to write 'planned'); the engine in 0135 explicitly sets 'draft'.

BEGIN;

-- =====================================================================
-- A. New columns
-- =====================================================================
ALTER TABLE private_core.production_plan
  ADD COLUMN base_bom_head_id text NULL,
  ADD COLUMN pack_manifest jsonb NOT NULL DEFAULT '[]'::jsonb,
  ADD COLUMN linked_recommendation_ids uuid[] NULL,
  ADD COLUMN proposal_id uuid NULL,
  ADD COLUMN is_user_modified boolean NOT NULL DEFAULT false,
  ADD COLUMN batch_size_l numeric NOT NULL DEFAULT 500;

ALTER TABLE private_core.production_plan
  ADD CONSTRAINT production_plan_base_bom_head_fk
    FOREIGN KEY (base_bom_head_id)
    REFERENCES private_core.bom_head(bom_head_id)
    ON DELETE RESTRICT;

ALTER TABLE private_core.production_plan
  ADD CONSTRAINT production_plan_pack_manifest_is_array
    CHECK (jsonb_typeof(pack_manifest) = 'array');

-- =====================================================================
-- B+C. Replace status enum + cancellation_consistency together
-- (must drop old constraints first; both reference status)
-- =====================================================================
ALTER TABLE private_core.production_plan
  DROP CONSTRAINT IF EXISTS production_plan_status_check;

ALTER TABLE private_core.production_plan
  DROP CONSTRAINT IF EXISTS production_plan_cancellation_consistency;

ALTER TABLE private_core.production_plan
  ADD CONSTRAINT production_plan_status_check
    CHECK (status = ANY (ARRAY['draft','planned','in_production','completed','cancelled']));

-- New consistency check: each status has its own required-field shape.
-- draft / planned / in_production: cancelled_* MUST be NULL; completed_submission_id MAY be NULL
-- completed: completed_submission_id MUST NOT be NULL; cancelled_* MUST be NULL
-- cancelled: cancelled_at + cancelled_by_user_id MUST NOT be NULL; completed_submission_id MUST be NULL
ALTER TABLE private_core.production_plan
  ADD CONSTRAINT production_plan_cancellation_consistency
    CHECK (
      (status IN ('draft','planned','in_production')
        AND cancelled_at IS NULL
        AND cancelled_by_user_id IS NULL
        AND cancel_reason IS NULL)
      OR
      (status = 'completed'
        AND completed_submission_id IS NOT NULL
        AND cancelled_at IS NULL
        AND cancelled_by_user_id IS NULL
        AND cancel_reason IS NULL)
      OR
      (status = 'cancelled'
        AND cancelled_at IS NOT NULL
        AND cancelled_by_user_id IS NOT NULL
        AND completed_submission_id IS NULL)
    );

-- =====================================================================
-- E. planning_run_recommendations.consumed_by_proposal_id
-- =====================================================================
ALTER TABLE private_core.planning_run_recommendations
  ADD COLUMN consumed_by_proposal_id uuid NULL;

-- (No FK to a proposals table — proposal_id is a logical grouping id we
-- generate per Recompute call, not a row in its own table. Plan B can
-- formalize a planning_proposals table if useful.)

-- =====================================================================
-- F. Indexes
-- =====================================================================
CREATE INDEX idx_production_plan_base_date
  ON private_core.production_plan(base_bom_head_id, plan_date)
  WHERE base_bom_head_id IS NOT NULL;

CREATE INDEX idx_production_plan_proposal
  ON private_core.production_plan(proposal_id)
  WHERE proposal_id IS NOT NULL;

CREATE INDEX idx_planning_run_recs_consumed_proposal
  ON private_core.planning_run_recommendations(consumed_by_proposal_id)
  WHERE consumed_by_proposal_id IS NOT NULL;

COMMIT;
```

- [ ] **Step 1.4: Apply + run pgTAP, expect 28/28 pass**

```bash
node scripts/_apply_migration.mjs db/migrations/0133_production_plan_base_batch_extensions.sql
node scripts/_run_pgtap.mjs db/tests/0133_production_plan_base_batch_extensions.test.sql
```

Expected: `28/28 pass`.

If `_apply_migration.mjs` doesn't exist as a generic runner, model it after `scripts/_apply_0132.mjs` (one transaction, NOTICE handler, COMMIT/ROLLBACK on error).

- [ ] **Step 1.5: Commit**

```bash
git add db/migrations/0133_production_plan_base_batch_extensions.sql db/tests/0133_production_plan_base_batch_extensions.test.sql
git commit -m "schema(production-plan): base-batch extensions + new lifecycle (migration 0133)

Consolidated migration:
  A. Adds 6 columns to production_plan: base_bom_head_id (FK→bom_head),
     pack_manifest (jsonb default '[]'), linked_recommendation_ids (uuid[]),
     proposal_id (uuid), is_user_modified (bool), batch_size_l (numeric=500).
  B. Extends status enum: planned/cancelled →
     draft/planned/in_production/completed/cancelled (per spec §7).
  C. Rewrites production_plan_cancellation_consistency to govern all 5
     statuses with per-status field requirements.
  D. CHECK pack_manifest is a jsonb array.
  E. Adds planning_run_recommendations.consumed_by_proposal_id (uuid NULL).
  F. Three new indexes (base+date, proposal, consumed_proposal).

Per spec PRODUCTION/docs/2026-05-03-daily-production-plan-design.md §2 / §7 / §9.
0 existing production_plan rows post-cleanup; default status column unchanged
('planned'); engine (0135) sets 'draft' explicitly.

pgTAP: 28/28 (db/tests/0133_*.test.sql)."
```

---

## Chunk 2: Migration 0134 — planning_policy key-value seed for proposal engine

**Purpose:** Seed the four policy values the engine needs into the existing key-value `planning_policy` table. Per Tom Decision-1: A (key-value, not wide columns).

**Files:**
- Create: `db/migrations/0134_planning_policy_proposal_seed.sql`
- Create: `db/tests/0134_planning_policy_proposal_seed.test.sql`

### Test first

- [ ] **Step 2.1: Write the failing pgTAP test**

```sql
-- db/tests/0134_planning_policy_proposal_seed.test.sql
BEGIN;
SELECT plan(8);

SELECT is(
  (SELECT value FROM private_core.planning_policy WHERE key='planning.production.batch_size_l'),
  '500',
  'batch_size_l key seeded with default 500');

SELECT is(
  (SELECT uom FROM private_core.planning_policy WHERE key='planning.production.batch_size_l'),
  'L',
  'batch_size_l carries L uom');

SELECT is(
  (SELECT value FROM private_core.planning_policy WHERE key='planning.production.safety_days_per_base'),
  '5',
  'safety_days_per_base key seeded with default 5');

SELECT is(
  (SELECT uom FROM private_core.planning_policy WHERE key='planning.production.safety_days_per_base'),
  'days',
  'safety_days_per_base carries days uom');

SELECT is(
  (SELECT value FROM private_core.planning_policy WHERE key='planning.production.work_days_of_week'),
  '0,1,2,3,4',
  'work_days_of_week key seeded as comma list Sun-Thu');

SELECT is(
  (SELECT value FROM private_core.planning_policy WHERE key='planning.production.max_batches_per_day'),
  '1',
  'max_batches_per_day key seeded with default 1');

-- Existing keys stay unchanged
SELECT is(
  (SELECT value FROM private_core.planning_policy WHERE key='EXTRACTS_MAX_BATCH_L'),
  '500',
  'EXTRACTS_MAX_BATCH_L preserved (unchanged)');

SELECT is(
  (SELECT value FROM private_core.planning_policy WHERE key='COCKTAILS_MAX_BATCH_L'),
  '500',
  'COCKTAILS_MAX_BATCH_L preserved (unchanged)');

SELECT * FROM finish();
ROLLBACK;
```

- [ ] **Step 2.2: Run pgTAP, expect 6 failures (last 2 pass already)**

Expected: 6 failures (the 4 new keys missing — 2 keys × 2 assertions each for batch_size_l and safety_days), 2 pass (existing keys present).

### Implementation

- [ ] **Step 2.3: Write the migration**

```sql
-- db/migrations/0134_planning_policy_proposal_seed.sql
--
-- Seed 4 new namespaced policy keys for the smart-proposal engine.
-- Per Tom Decision-1 (2026-05-03): planning_policy stays key-value;
-- new policy values are added as namespaced rows under planning.production.*
--
-- Rationale (spec §3.3): the engine reads (s, Q) policy + work-day calendar
-- + per-day capacity. v1 reads ONE global value per key; v2 may add per-base
-- override rows like planning.production.safety_days_per_base.BOM-BASE-DET-REG.

BEGIN;

INSERT INTO private_core.planning_policy (key, value, uom, description)
VALUES
  ('planning.production.batch_size_l',
   '500',
   'L',
   'Fixed Q for production lots — default 500 L per Tom (matches EXTRACTS_MAX_BATCH_L). Used by fn_propose_weekly_production_plan as the base-batch unit. Per-base override later via planning.production.batch_size_l.<base_bom_head_id>.'),
  ('planning.production.safety_days_per_base',
   '5',
   'days',
   'Reorder-point safety horizon: s_base = N × avg_daily_demand_liters. Default 5 days. Per-base override later via planning.production.safety_days_per_base.<base_bom_head_id>. Per spec PRODUCTION/docs/2026-05-03-daily-production-plan-design.md §3.3.'),
  ('planning.production.work_days_of_week',
   '0,1,2,3,4',
   NULL,
   'Production-day calendar as a comma-separated list of PostgreSQL DOW integers (0=Sun..6=Sat). Default Sun-Thu = 0,1,2,3,4. Engine treats other days as no-capacity. Per-week override not in v1.'),
  ('planning.production.max_batches_per_day',
   '1',
   NULL,
   'Default capacity per work day. Tom-locked at 1 (single physical tank). Tom can override per-day via the portal Add Batch action; this is the engine''s scheduling default.')
ON CONFLICT (key) DO UPDATE
  SET value = EXCLUDED.value,
      uom = EXCLUDED.uom,
      description = EXCLUDED.description,
      updated_at = now();

-- Note: we do NOT touch the existing 'planning.safety.stock_days_default'
-- key (currently 0). It governs a different surface (the older per-FG
-- recommender). The new 'planning.production.safety_days_per_base' is
-- specific to the base-batch engine. Keeping them separate avoids
-- surprising the existing per-FG flow.

COMMIT;
```

- [ ] **Step 2.4: Apply + run pgTAP, expect 8/8 pass**

```bash
node scripts/_apply_migration.mjs db/migrations/0134_planning_policy_proposal_seed.sql
node scripts/_run_pgtap.mjs db/tests/0134_planning_policy_proposal_seed.test.sql
```

Expected: `8/8 pass`.

- [ ] **Step 2.5: Commit**

```bash
git add db/migrations/0134_planning_policy_proposal_seed.sql db/tests/0134_planning_policy_proposal_seed.test.sql
git commit -m "policy(planning): seed 4 production-engine keys in planning_policy (migration 0134)

Adds key-value rows under planning.production.* namespace for the smart-
proposal engine: batch_size_l=500 (L), safety_days_per_base=5 (days),
work_days_of_week=0,1,2,3,4 (Sun-Thu DOW), max_batches_per_day=1.

Per Tom Decision-1 (2026-05-03 brainstorm response 'A'): planning_policy
stays key-value; per-base override path is namespaced subkeys later.

Existing keys preserved (EXTRACTS_MAX_BATCH_L, COCKTAILS_MAX_BATCH_L,
planning.safety.stock_days_default, etc. all untouched).

ON CONFLICT DO UPDATE so re-running the migration is idempotent.

pgTAP: 8/8 (db/tests/0134_*.test.sql)."
```

---

## Chunk 3: Migration 0135 — `fn_propose_weekly_production_plan`

**Purpose:** The smart-proposal engine. Reads policy by key from key-value `planning_policy`. Groups approved-unconsumed production recs by base. Subtracts current stock. Schedules fixed-Q (500 L) batches across work days within capacity. Logs `planning_run_exception` for any rec whose item lacks `base_bom_head_id` / `base_fill_qty_per_unit`. Uses uppercase `'UNIT'` for `uom_code`. Inserts `production_plan` rows with `status='draft'`.

**Files:**
- Create: `db/migrations/0135_fn_propose_weekly_production_plan.sql`
- Create: `db/tests/0135_fn_propose_weekly_production_plan.test.sql`

### Pre-write check — read current planning_run_exceptions schema

- [ ] **Step 3.0a: Inspect `planning_run_exceptions`**

```bash
node -e "
import('pg').then(async pg => {
  process.env.NODE_TLS_REJECT_UNAUTHORIZED='0';
  const fs = await import('node:fs');
  const env = fs.readFileSync('.env','utf-8');
  const url = env.split('\n').find(l => l.startsWith('DATABASE_URL_POOLED=')).slice(20).trim();
  const c = new pg.default.Client({connectionString:url, ssl:{rejectUnauthorized:false}});
  await c.connect();
  const r = await c.query(\"SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_schema='private_core' AND table_name='planning_run_exceptions' ORDER BY ordinal_position\");
  console.table(r.rows);
  const r2 = await c.query(\"SELECT con.conname, pg_get_constraintdef(con.oid) AS def FROM pg_constraint con JOIN pg_class rel ON rel.oid = con.conrelid WHERE rel.relname='planning_run_exceptions' AND con.contype='c'\");
  console.table(r2.rows);
  await c.end();
});
"
```

The exception INSERT in the engine below ASSUMES the exception table has `(run_id, exception_category, severity, payload jsonb)` plus standard audit. If the live shape differs, **adapt the INSERT to match real columns** — do NOT invent column names. If `run_id` is mandatory and we don't have one (the proposal isn't a planning_run), either:
  a) Pick the latest planning_run as parent (look up by max created_at), or
  b) Make `run_id` NULLable via this migration (only if Tom approves — that's a contract change).

If unclear, halt with `assumption_failure` listing the column gap and the two paths.

### Test first

- [ ] **Step 3.1: Write the failing pgTAP test**

```sql
-- db/tests/0135_fn_propose_weekly_production_plan.test.sql
BEGIN;
SELECT plan(10);

-- Function shape
SELECT has_function('private_core', 'fn_propose_weekly_production_plan',
  ARRAY['date', 'uuid'],
  'fn_propose_weekly_production_plan(date, uuid) exists');

SELECT function_returns('private_core', 'fn_propose_weekly_production_plan',
  ARRAY['date', 'uuid'],
  'uuid',
  'function returns proposal_id uuid');

-- Functional: empty input → returns a uuid, inserts 0 production_plan rows
DO $$
DECLARE
  v_actor uuid;
  v_proposal uuid;
  v_count int;
BEGIN
  SELECT user_id INTO v_actor FROM private_core.app_users WHERE email='tom@gteveryday.com';
  -- Move all current approved recs out of the way for an empty-input test
  UPDATE private_core.planning_run_recommendations
     SET consumed_by_proposal_id = '00000000-0000-0000-0000-000000000001'::uuid
   WHERE recommendation_status = 'approved'
     AND recommendation_type = 'production'
     AND consumed_by_proposal_id IS NULL;

  v_proposal := private_core.fn_propose_weekly_production_plan('2030-06-04'::date, v_actor);

  SELECT COUNT(*) INTO v_count FROM private_core.production_plan WHERE proposal_id = v_proposal;
  PERFORM is(v_count, 0, 'empty input produces 0 production_plan rows');
  PERFORM isnt(v_proposal::text, NULL, 'proposal_id is non-null');

  -- restore
  UPDATE private_core.planning_run_recommendations
     SET consumed_by_proposal_id = NULL
   WHERE consumed_by_proposal_id = '00000000-0000-0000-0000-000000000001'::uuid;
END $$;

-- Functional: a single approved rec for a properly-mapped FG produces one batch
DO $$
DECLARE
  v_actor uuid;
  v_proposal uuid;
  v_rec_id uuid;
  v_item_id text;
BEGIN
  SELECT user_id INTO v_actor FROM private_core.app_users WHERE email='tom@gteveryday.com';

  -- Find an approved production rec whose item has base_bom_head_id AND base_fill_qty_per_unit
  SELECT prr.recommendation_id, prr.item_id INTO v_rec_id, v_item_id
    FROM private_core.planning_run_recommendations prr
    JOIN private_core.items i ON i.item_id = prr.item_id
   WHERE prr.recommendation_type = 'production'
     AND prr.recommendation_status = 'approved'
     AND prr.consumed_by_proposal_id IS NULL
     AND i.base_bom_head_id IS NOT NULL
     AND i.base_fill_qty_per_unit IS NOT NULL
     AND i.base_fill_qty_per_unit > 0
   ORDER BY prr.recommended_qty DESC NULLS LAST
   LIMIT 1;

  IF v_rec_id IS NULL THEN
    PERFORM skip(5, 'No suitable approved rec available for happy-path test');
    RETURN;
  END IF;

  -- Park all other approved recs so this test isolates the one rec
  UPDATE private_core.planning_run_recommendations
     SET consumed_by_proposal_id = '00000000-0000-0000-0000-000000000002'::uuid
   WHERE recommendation_status = 'approved'
     AND recommendation_type = 'production'
     AND consumed_by_proposal_id IS NULL
     AND recommendation_id <> v_rec_id;

  v_proposal := private_core.fn_propose_weekly_production_plan('2030-06-04'::date, v_actor);

  PERFORM ok(
    (SELECT COUNT(*) > 0 FROM private_core.production_plan WHERE proposal_id = v_proposal),
    'at least one production_plan row created');

  PERFORM is(
    (SELECT base_bom_head_id FROM private_core.production_plan WHERE proposal_id = v_proposal LIMIT 1),
    (SELECT base_bom_head_id FROM private_core.items WHERE item_id = v_item_id),
    'production_plan row carries the base_bom_head_id of the source item');

  PERFORM is(
    (SELECT batch_size_l FROM private_core.production_plan WHERE proposal_id = v_proposal LIMIT 1),
    500::numeric,
    'batch_size_l = 500 (read from planning.production.batch_size_l)');

  PERFORM is(
    (SELECT status FROM private_core.production_plan WHERE proposal_id = v_proposal LIMIT 1),
    'draft',
    'new batch row is draft');

  PERFORM is(
    (SELECT uom FROM private_core.production_plan WHERE proposal_id = v_proposal LIMIT 1),
    'UNIT',
    'uom is uppercase UNIT (matches uom_code FK)');

  -- restore
  UPDATE private_core.planning_run_recommendations
     SET consumed_by_proposal_id = NULL
   WHERE consumed_by_proposal_id = '00000000-0000-0000-0000-000000000002'::uuid;
END $$;

SELECT * FROM finish();
ROLLBACK;
```

- [ ] **Step 3.2: Run pgTAP, expect failures (function doesn't exist)**

Expected: function-shape assertions fail with `function does not exist`.

### Implementation

- [ ] **Step 3.3: Write the migration**

```sql
-- db/migrations/0135_fn_propose_weekly_production_plan.sql
--
-- Smart proposal engine per spec PRODUCTION/docs/2026-05-03-daily-production-plan-design.md §3.
--
-- Inputs:
--   p_week_start date  : first day of the target work week
--   p_actor      uuid  : user triggering the proposal
--
-- Returns: uuid (proposal_id) — every batch row this run inserts carries this id
--
-- Algorithm (reference: spec §3):
--   1. Read policy by key from key-value private_core.planning_policy:
--        planning.production.batch_size_l           (default 500)
--        planning.production.safety_days_per_base   (default 5)
--        planning.production.work_days_of_week      (default 0,1,2,3,4)
--        planning.production.max_batches_per_day    (default 1)
--   2. Identify approved + unconsumed production recs.
--   3. For each rec whose item lacks base_bom_head_id OR base_fill_qty_per_unit:
--        emit a planning_run_exception (category='engine_missing_base_metadata')
--        and skip the rec. (See spec §6.10 / Chunk 3 step 3.0a for exception
--        table shape.)
--   4. Group surviving recs by base_bom_head_id; sum demanded liters.
--   5. Subtract current_stock_in_liters per base.
--   6. Sort bases by earliest shortage_date (NULLS last); deterministic by id.
--   7. For each base, fire CEIL(net_l / batch_size_l) batches; assign one per
--      available work-day slot in the target week; overflow batches NOT inserted
--      (logged separately as 'capacity_overflow' exception in v2 — for v1 they
--      simply don't appear in the proposal, and the controller surfaces the gap
--      via deferred_count returned in the response payload).
--   8. Per scheduled batch, build pack_manifest greedily by FG urgency.
--   9. Insert production_plan rows with status='draft', uom='UNIT', linked recs.
--  10. Mark consumed recs: UPDATE planning_run_recommendations.consumed_by_proposal_id.

CREATE OR REPLACE FUNCTION private_core.fn_propose_weekly_production_plan(
  p_week_start date,
  p_actor uuid
) RETURNS uuid
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = private_core, public
AS $$
DECLARE
  v_proposal uuid := gen_random_uuid();
  v_actor_snapshot text;
  v_batch_size_l numeric;
  v_safety_days int;
  v_work_days int[];
  v_max_per_day int;
  v_week_end date := p_week_start + 6;
BEGIN
  -- Snapshot actor display name for audit
  SELECT COALESCE(display_name, email) INTO v_actor_snapshot
    FROM private_core.app_users WHERE user_id = p_actor;
  IF v_actor_snapshot IS NULL THEN
    RAISE EXCEPTION 'unknown actor %', p_actor USING ERRCODE = '22023';
  END IF;

  -- ===========================================================
  -- STEP 1: Read policy by key from planning_policy
  -- ===========================================================
  SELECT NULLIF(value, '')::numeric INTO v_batch_size_l
    FROM private_core.planning_policy
   WHERE key = 'planning.production.batch_size_l';
  v_batch_size_l := COALESCE(v_batch_size_l, 500);

  SELECT NULLIF(value, '')::int INTO v_safety_days
    FROM private_core.planning_policy
   WHERE key = 'planning.production.safety_days_per_base';
  v_safety_days := COALESCE(v_safety_days, 5);

  SELECT string_to_array(value, ',')::int[] INTO v_work_days
    FROM private_core.planning_policy
   WHERE key = 'planning.production.work_days_of_week';
  v_work_days := COALESCE(v_work_days, ARRAY[0,1,2,3,4]);

  SELECT NULLIF(value, '')::int INTO v_max_per_day
    FROM private_core.planning_policy
   WHERE key = 'planning.production.max_batches_per_day';
  v_max_per_day := COALESCE(v_max_per_day, 1);

  -- ===========================================================
  -- STEP 3: Log exception per rec missing base metadata, then exclude
  -- ===========================================================
  -- (Engineer: implement per the planning_run_exceptions shape discovered
  --  in Chunk 3 Step 3.0a. The pattern below is a placeholder; adapt the
  --  column list and parent run_id strategy to match real schema.)
  --
  -- For each approved-unconsumed production rec whose item is missing
  -- base_bom_head_id or base_fill_qty_per_unit, INSERT one row into
  -- planning_run_exceptions with category='engine_missing_base_metadata'
  -- and a payload jsonb identifying the rec_id, item_id, and which field
  -- was missing. Do NOT mark the rec consumed_by_proposal_id (so it
  -- remains visible for future fixes).

  -- ===========================================================
  -- STEP 4-5: Gather + group surviving recs by base, subtract stock
  -- ===========================================================
  CREATE TEMP TABLE _bases_to_propose ON COMMIT DROP AS
  SELECT
    i.base_bom_head_id,
    SUM(prr.recommended_qty * i.base_fill_qty_per_unit)::numeric AS demanded_liters_gross,
    array_agg(prr.recommendation_id) AS rec_ids,
    MIN(prr.shortage_date) AS earliest_shortage,
    jsonb_agg(jsonb_build_object(
      'item_id', prr.item_id,
      'qty', prr.recommended_qty,
      'shortage_date', prr.shortage_date
    ) ORDER BY prr.shortage_date NULLS LAST) AS rec_packs
  FROM private_core.planning_run_recommendations prr
  JOIN private_core.items i ON i.item_id = prr.item_id
  WHERE prr.recommendation_type = 'production'
    AND prr.recommendation_status = 'approved'
    AND prr.consumed_by_proposal_id IS NULL
    AND i.base_bom_head_id IS NOT NULL
    AND i.base_fill_qty_per_unit IS NOT NULL
    AND i.base_fill_qty_per_unit > 0
  GROUP BY i.base_bom_head_id;

  -- Subtract current stock (in liters) per base
  WITH stock_l AS (
    SELECT i.base_bom_head_id,
           SUM(GREATEST(cb.calculated_on_hand, 0) * i.base_fill_qty_per_unit)::numeric AS stock_l
      FROM private_core.current_balances cb
      JOIN private_core.items i ON i.item_id = cb.item_id
     WHERE i.base_bom_head_id IS NOT NULL
       AND i.base_fill_qty_per_unit IS NOT NULL
     GROUP BY i.base_bom_head_id
  )
  UPDATE _bases_to_propose b
     SET demanded_liters_gross = GREATEST(b.demanded_liters_gross - COALESCE(s.stock_l, 0), 0)
    FROM stock_l s
   WHERE s.base_bom_head_id = b.base_bom_head_id;

  -- ===========================================================
  -- STEP 6-9: Walk bases by urgency; assign batches to work days; insert.
  -- (Procedural; v1 simple.)
  -- ===========================================================
  DECLARE
    r record;
    batches_needed int;
    day_cursor date;
    batches_today int;
    bv_id uuid;
  BEGIN
    -- Reset cursor at the start of the week
    day_cursor := p_week_start;
    batches_today := 0;

    FOR r IN
      SELECT * FROM _bases_to_propose
       WHERE demanded_liters_gross > 0
       ORDER BY earliest_shortage NULLS LAST, base_bom_head_id
    LOOP
      batches_needed := CEIL(r.demanded_liters_gross / v_batch_size_l)::int;

      -- Pin BASE BOM active version for this base
      SELECT bh.active_version_id INTO bv_id
        FROM private_core.bom_head bh
       WHERE bh.bom_head_id = r.base_bom_head_id;

      FOR i IN 1..batches_needed LOOP
        -- advance day_cursor to next valid work day with capacity
        WHILE day_cursor <= v_week_end LOOP
          IF EXTRACT(DOW FROM day_cursor)::int = ANY(v_work_days)
             AND batches_today < v_max_per_day THEN
            EXIT;  -- valid slot
          END IF;
          day_cursor := day_cursor + 1;
          batches_today := 0;
        END LOOP;

        EXIT WHEN day_cursor > v_week_end;  -- overflow; rest of base's batches dropped

        -- Insert one production_plan row for this batch
        INSERT INTO private_core.production_plan (
          plan_date, item_id, planned_qty, uom, status,
          base_bom_head_id, bom_version_id_pinned, batch_size_l,
          pack_manifest, linked_recommendation_ids, proposal_id,
          created_by_user_id, created_by_snapshot, idempotency_key
        )
        VALUES (
          day_cursor,
          (r.rec_packs->0->>'item_id')::text,            -- legacy item_id = first FG by urgency
          GREATEST(((r.rec_packs->0->>'qty')::numeric), 1), -- legacy planned_qty (must be > 0)
          'UNIT',
          'draft',
          r.base_bom_head_id,
          bv_id,
          v_batch_size_l,
          r.rec_packs,
          r.rec_ids,
          v_proposal,
          p_actor,
          v_actor_snapshot,
          'PROPOSAL:' || v_proposal::text || ':' || r.base_bom_head_id || ':' || day_cursor::text || ':' || i::text
        );

        batches_today := batches_today + 1;
        IF batches_today >= v_max_per_day THEN
          day_cursor := day_cursor + 1;
          batches_today := 0;
        END IF;
      END LOOP;
    END LOOP;
  END;

  -- ===========================================================
  -- STEP 10: Mark recommendations as consumed
  -- ===========================================================
  UPDATE private_core.planning_run_recommendations prr
     SET consumed_by_proposal_id = v_proposal
   WHERE prr.recommendation_id IN (
     SELECT unnest(b.rec_ids) FROM _bases_to_propose b
   )
     AND prr.consumed_by_proposal_id IS NULL;

  RETURN v_proposal;
END;
$$;

GRANT EXECUTE ON FUNCTION private_core.fn_propose_weekly_production_plan(date, uuid)
  TO authenticated, service_role;
```

**Note on `pack_manifest`-distribution-per-batch:** v1 stores the *full* base demand `rec_packs` on every batch row of that base. That's not strictly correct (each 500 L batch should only carry its share of the FGs). v1 ships this simplification because the per-batch greedy fill (spec §3.6) is deferred to Plan B (the API will do the per-batch split when Tom edits a batch's pack_manifest in the drawer). Document this in the commit message; the function's contract is "all linked recs are surfaced on the batches" — exact distribution is computed at edit-time.

- [ ] **Step 3.4: Apply + run pgTAP, expect 10/10 pass**

```bash
node scripts/_apply_migration.mjs db/migrations/0135_fn_propose_weekly_production_plan.sql
node scripts/_run_pgtap.mjs db/tests/0135_fn_propose_weekly_production_plan.test.sql
```

If skip() fired (no suitable approved rec for the happy-path test), still expect the rest of the assertions to pass.

- [ ] **Step 3.5: Manual end-to-end smoke against live data**

```bash
node -e "
import('pg').then(async pg => {
  process.env.NODE_TLS_REJECT_UNAUTHORIZED='0';
  const fs = await import('node:fs');
  const env = fs.readFileSync('.env','utf-8');
  const url = env.split('\n').find(l => l.startsWith('DATABASE_URL_POOLED=')).slice(20).trim();
  const c = new pg.default.Client({connectionString:url, ssl:{rejectUnauthorized:false}});
  await c.connect();
  const tom = (await c.query(\"SELECT user_id FROM private_core.app_users WHERE email='tom@gteveryday.com'\")).rows[0].user_id;
  const r = await c.query('SELECT private_core.fn_propose_weekly_production_plan(\\$1::date, \\$2::uuid) AS proposal_id', ['2026-05-04', tom]);
  console.log('proposal_id:', r.rows[0].proposal_id);
  const rows = await c.query(\"SELECT plan_date, base_bom_head_id, jsonb_array_length(pack_manifest) AS pack_count, batch_size_l, status FROM private_core.production_plan WHERE proposal_id = \\$1::uuid ORDER BY plan_date, base_bom_head_id\", [r.rows[0].proposal_id]);
  console.table(rows.rows);
  await c.end();
});
"
```

Expected: `proposal_id` returned. `console.table` shows N rows for the new proposal, one per (work day × base), each with `status='draft'` and a non-zero `pack_count`.

If proposal returns 0 rows: the base-coverage gap is the cause (P4 found 59/200 affected). Check `planning_run_exceptions` for `engine_missing_base_metadata` rows — they should explain the skip.

- [ ] **Step 3.6: Commit**

```bash
git add db/migrations/0135_fn_propose_weekly_production_plan.sql db/tests/0135_fn_propose_weekly_production_plan.test.sql
git commit -m "engine(planning): fn_propose_weekly_production_plan key-value-policy + UNIT (migration 0135)

Reads policy by namespaced key from planning_policy (key-value table per
Tom Decision-1):
  planning.production.batch_size_l         (default 500)
  planning.production.safety_days_per_base (default 5)
  planning.production.work_days_of_week    (default 0,1,2,3,4 = Sun-Thu)
  planning.production.max_batches_per_day  (default 1)

Groups approved + unconsumed production recs by items.base_bom_head_id;
subtracts current stock (in liters) per base; schedules CEIL(net_l/500)
batches across work days within the target week; inserts production_plan
rows with status='draft', uom='UNIT' (uppercase per uom_code FK), full
pack_manifest (per-batch greedy split deferred to Plan B); marks
consumed recommendations.

Per spec PRODUCTION/docs/2026-05-03-daily-production-plan-design.md §3.

Logs planning_run_exception (engine_missing_base_metadata) for any
approved rec whose item lacks base_bom_head_id or base_fill_qty_per_unit.
The 59/200 affected recs (mostly Muza cocktails + 3.85L sangrias) thus
surface in the Inbox instead of silently disappearing.

pgTAP: 10/10 (db/tests/0135_*.test.sql)."
```

---

## Chunk 4: Migration 0136 — `v_daily_inventory_projection` view

**Purpose:** Power the 8-week overflow drill-down (spec §4.4). Per-base, per-day liters projection that anyone (engine, API, portal) can read.

**Files:**
- Create: `db/migrations/0136_v_daily_inventory_projection.sql`
- Create: `db/tests/0136_v_daily_inventory_projection.test.sql`

### Test first

- [ ] **Step 4.1: Write the failing pgTAP test**

```sql
-- db/tests/0136_v_daily_inventory_projection.test.sql
BEGIN;
SELECT plan(5);

SELECT has_view('api_read', 'v_daily_inventory_projection',
  'api_read.v_daily_inventory_projection exists');

SELECT has_column('api_read', 'v_daily_inventory_projection', 'site_id', 'site_id');
SELECT has_column('api_read', 'v_daily_inventory_projection', 'base_bom_head_id', 'base_bom_head_id');
SELECT has_column('api_read', 'v_daily_inventory_projection', 'projection_day', 'projection_day');
SELECT has_column('api_read', 'v_daily_inventory_projection', 'projected_liters', 'projected_liters');

SELECT * FROM finish();
ROLLBACK;
```

- [ ] **Step 4.2: Run pgTAP, expect 5 failures**

### Implementation

- [ ] **Step 4.3: Write the migration**

```sql
-- db/migrations/0136_v_daily_inventory_projection.sql
--
-- Per-base daily liters projection for the next 56 days (8 weeks).
-- Powers the spec §4.4 8-week overflow drill-down and the engine's
-- reorder-point sweep audit.
--
-- For each base × each day:
--   projected_liters = current_stock_l
--                    + scheduled_inflow_l_through(day)
--                    - daily_demand_l_cumulative_through(day)
--
-- Daily demand draws from api_read.v_planning_demand (forecast + open orders),
-- spread evenly across the 7 days of each weekly bucket.

CREATE OR REPLACE VIEW api_read.v_daily_inventory_projection AS
WITH bases AS (
  SELECT DISTINCT i.base_bom_head_id, COALESCE(cb.site_id, 'GT-MAIN') AS site_id
    FROM private_core.items i
    LEFT JOIN private_core.current_balances cb ON cb.item_id = i.item_id
   WHERE i.base_bom_head_id IS NOT NULL
),
days AS (
  SELECT generate_series(CURRENT_DATE, CURRENT_DATE + 55, INTERVAL '1 day')::date AS d
),
current_stock AS (
  SELECT i.base_bom_head_id,
         COALESCE(cb.site_id, 'GT-MAIN') AS site_id,
         SUM(COALESCE(cb.calculated_on_hand, 0) * COALESCE(i.base_fill_qty_per_unit, 0))::numeric AS stock_l
    FROM private_core.items i
    LEFT JOIN private_core.current_balances cb ON cb.item_id = i.item_id
   WHERE i.base_bom_head_id IS NOT NULL
   GROUP BY i.base_bom_head_id, cb.site_id
),
demand_per_day AS (
  -- Spread weekly-bucketed demand evenly across 7 days starting at the bucket
  SELECT i.base_bom_head_id,
         vpd.site_id,
         vpd.period_bucket_key + (gs - 1) AS demand_day,
         (vpd.demand_qty * COALESCE(i.base_fill_qty_per_unit, 0)) / 7.0 AS demand_l
    FROM api_read.v_planning_demand vpd
    JOIN private_core.items i ON i.item_id = vpd.item_id
    CROSS JOIN generate_series(1, 7) gs
   WHERE i.base_bom_head_id IS NOT NULL
),
scheduled_inflow AS (
  SELECT pp.base_bom_head_id,
         COALESCE(NULLIF(pp.site_id, ''), 'GT-MAIN') AS site_id,
         pp.plan_date AS inflow_day,
         pp.batch_size_l AS inflow_l
    FROM private_core.production_plan pp
   WHERE pp.base_bom_head_id IS NOT NULL
     AND pp.status IN ('draft', 'planned', 'in_production')
)
SELECT
  b.site_id,
  b.base_bom_head_id,
  d.d AS projection_day,
  COALESCE(cs.stock_l, 0)
    + COALESCE((SELECT SUM(inflow_l) FROM scheduled_inflow si
                 WHERE si.base_bom_head_id = b.base_bom_head_id
                   AND si.site_id = b.site_id
                   AND si.inflow_day <= d.d), 0)
    - COALESCE((SELECT SUM(demand_l) FROM demand_per_day dp
                 WHERE dp.base_bom_head_id = b.base_bom_head_id
                   AND dp.site_id = b.site_id
                   AND dp.demand_day <= d.d), 0)
    AS projected_liters,
  COALESCE((SELECT SUM(inflow_l) FROM scheduled_inflow si
             WHERE si.base_bom_head_id = b.base_bom_head_id
               AND si.site_id = b.site_id
               AND si.inflow_day = d.d), 0) AS scheduled_inflow_today_l,
  COALESCE((SELECT SUM(demand_l) FROM demand_per_day dp
             WHERE dp.base_bom_head_id = b.base_bom_head_id
               AND dp.site_id = b.site_id
               AND dp.demand_day = d.d), 0) AS demand_today_l
FROM bases b
CROSS JOIN days d
LEFT JOIN current_stock cs
  ON cs.base_bom_head_id = b.base_bom_head_id AND cs.site_id = b.site_id;

GRANT SELECT ON api_read.v_daily_inventory_projection TO authenticated, service_role;
```

**Note:** `production_plan.site_id` doesn't exist in the live schema (verified by REV 1 inspector). The view above defaults to `'GT-MAIN'` when joining; if Plan B adds `site_id` to production_plan, the view picks it up automatically thanks to the `COALESCE(NULLIF(...), 'GT-MAIN')` pattern.

Wait — the inspector confirmed `production_plan` does NOT have `site_id`. Adjust the `scheduled_inflow` CTE to drop the `pp.site_id` reference:

```sql
scheduled_inflow AS (
  SELECT pp.base_bom_head_id,
         'GT-MAIN'::text AS site_id,
         pp.plan_date AS inflow_day,
         pp.batch_size_l AS inflow_l
    FROM private_core.production_plan pp
   WHERE pp.base_bom_head_id IS NOT NULL
     AND pp.status IN ('draft', 'planned', 'in_production')
)
```

Use this corrected version.

- [ ] **Step 4.4: Apply + run pgTAP, expect 5/5 pass**

```bash
node scripts/_apply_migration.mjs db/migrations/0136_v_daily_inventory_projection.sql
node scripts/_run_pgtap.mjs db/tests/0136_v_daily_inventory_projection.test.sql
```

- [ ] **Step 4.5: Manual smoke — query for one base**

```bash
node -e "
import('pg').then(async pg => {
  process.env.NODE_TLS_REJECT_UNAUTHORIZED='0';
  const fs = await import('node:fs');
  const env = fs.readFileSync('.env','utf-8');
  const url = env.split('\n').find(l => l.startsWith('DATABASE_URL_POOLED=')).slice(20).trim();
  const c = new pg.default.Client({connectionString:url, ssl:{rejectUnauthorized:false}});
  await c.connect();
  const r = await c.query(\"SELECT projection_day, projected_liters, scheduled_inflow_today_l, demand_today_l FROM api_read.v_daily_inventory_projection WHERE base_bom_head_id = (SELECT base_bom_head_id FROM private_core.items WHERE item_id='FG-DET-1L') ORDER BY projection_day LIMIT 14\");
  console.table(r.rows);
  await c.end();
});
"
```

Expected: 14 rows showing daily projected liters for DETOX base over the next 2 weeks.

- [ ] **Step 4.6: Commit**

```bash
git add db/migrations/0136_v_daily_inventory_projection.sql db/tests/0136_v_daily_inventory_projection.test.sql
git commit -m "view(planning): v_daily_inventory_projection per-base 56-day liters (migration 0136)

Per-base per-day projection of liquid stock = current_stock + scheduled_inflow
- cumulative_demand. Powers the 8-week overflow drill-down (spec §4.4) and
the engine's reorder-point sweep (spec §3.4).

site_id hardcoded to GT-MAIN in scheduled_inflow CTE (production_plan has no
site_id column today; view picks it up automatically via NULLIF if added later).

Read-on-demand v1; materialization deferred to follow-up if perf demands.

Per spec PRODUCTION/docs/2026-05-03-daily-production-plan-design.md §4.4 / §6.

pgTAP: 5/5 (db/tests/0136_*.test.sql)."
```

---

## Chunk 5: Push to canonical main

- [ ] **Step 5.1: Confirm everything is committed locally**

```bash
git status
```

Expected: `working tree clean`.

- [ ] **Step 5.2: Push**

```bash
git push origin main
```

Expected: 4 commits pushed (0133 + 0134 + 0135 + 0136). Per Tom's standing memory `feedback_push_autonomously.md`: push autonomously after commits, no confirmation needed.

- [ ] **Step 5.3: Verify Railway redeploy is unaffected**

```bash
curl -s -w "\nHTTP=%{http_code}\n" https://gt-factory-os-api-production.up.railway.app/health
```

Expected: `{"ok":true}` and `HTTP=200`. (Migrations don't change served code; Railway shouldn't redeploy.)

---

## Acceptance criteria for Plan A (REV 2)

Plan A is **DONE** when all of these hold (verifier independently checks each):

- [ ] All 4 migrations (0133, 0134, 0135, 0136) applied to canonical Supabase Postgres.
- [ ] All pgTAP suites pass: 28 + 8 + 10 + 5 = **51/51 assertions green**.
- [ ] Manual end-to-end smoke (Chunk 3 step 3.5) successfully creates a proposal for the next work week, returning `proposal_id` and N `production_plan` rows with `status='draft'`, `uom='UNIT'`, non-empty `pack_manifest`, correct `base_bom_head_id`.
- [ ] `api_read.v_daily_inventory_projection` returns sensible rows for at least one base (Chunk 4 step 4.5).
- [ ] All 4 commits pushed to `gt-factory-os/main`. Railway health endpoint still 200.
- [ ] No regression: `private_core.rebuild_verifier()` still returns 0.
- [ ] `planning_run_exceptions` contains `engine_missing_base_metadata` rows for the 59 affected recs (verifies the gap-logging works); these surface for Tom's data-fix backlog without blocking the proposal.

---

## Polish iteration #A (per Tom's mandate, spec §12)

After functional acceptance, **stop**. Plan A's polish iteration is brief because there's no UI:

- [ ] **Polish A.1:** Tom + engineer review the proposal's resulting plan rows:
  - Are batches placed on the right days?
  - Is the pack_manifest sensible for each base?
  - Are linked_recommendation_ids the ones Tom expected?
  - Did the 59 base-metadata gaps surface as Inbox exceptions?
  - Anything missing or surprising?
- [ ] **Polish A.2:** Each finding from A.1 becomes a fix-task before declaring Plan A complete. Don't move to Plan B until Tom signs off on A.1.

---

## Handoff

Once Plan A is signed off, next plan in series is **Plan B — API endpoints** (spec §10), which consumes the SQL function and view this plan delivered. Plan B is written in a separate doc when Plan A is verified.

**Open follow-ups (tracked, not blocking Plan A acceptance):**
1. Per-batch greedy pack distribution (spec §3.6) — currently every batch carries full `rec_packs`; distribution decided at edit time.
2. Capacity-overflow as `planning_run_exception` row (engine returns the count via response payload only in v1).
3. Per-base policy lookup (override via `planning.production.<key>.<base_bom_head_id>`) — spec §3.3 mentions; v1 reads global only.
4. Smarter multi-base interleaving (spec §3.5).
5. Materialization of `v_daily_inventory_projection` if perf demands.
6. **Items-master gap audit (data hygiene):** 59/200 approved recs reference items missing `base_bom_head_id` or `base_fill_qty_per_unit`. Mostly Muza cocktail variants + 3.85L sangrias. Needs a one-off data-fix migration after Tom decides per-item resolutions.

---

**End of Plan A REV 2.**
