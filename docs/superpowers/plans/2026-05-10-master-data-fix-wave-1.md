# Master Data Fix — Wave 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land the master-data consistency hot-fix on the live DB so Physical Count form recognizes every BOM-referenced component by an operator-friendly name. Closes the immediate Chamomile-class blocker on `/(ops)/stock/physical-count`.

**Architecture:** One forward-only SQL migration (`0180`) in `gt-factory-os/db/migrations/` that (a) creates `private_core.component_aliases` table, (b) seeds 8 alias rows so renamed components stay searchable by their old name, (c) renames `RAW-CALM` and `RAW-WINE-WHITE` to floor-truth names, (d) normalizes `bom_lines.final_component_name` to canonical truth on active BOM versions, (e) sets the 3 duplicate component IDs to `STATUS='INACTIVE'`. Paired pgTAP test file (`0180_master_data_consistency.test.sql`) locks T1–T7 invariants so any future drift fails CI. Fixtures re-extracted from DB post-apply. RUNTIME_READY signal emitted to PRODUCTION harness state.

**Tech Stack:** PostgreSQL 15+ (Supabase Frankfurt Pro), pgTAP, psql, pg_prove, Node 22 (audit script), Python 3 (`extract_golden_fixtures.py`).

**Spec:** `PRODUCTION/docs/master-data-reconciliation/2026-05-10-master-data-fix-design.md` §3 Wave 1 + §4 Implementation plan rows #1–#2.

**Boundaries (hard):**
- This plan touches `gt-factory-os/db/**`, `gt-factory-os/fixtures/masters/**`, `gt-factory-os/package.json`, `gt-factory-os/scripts/bom_master_audit.mjs` (already exists, used read-only here), and `PRODUCTION/.claude/state/runtime_ready.json` (append-only).
- This plan does NOT touch portal source, integration handlers, schema beyond `component_aliases`, or any locked decision in `CLAUDE.md`.
- This plan does NOT push, merge, or deploy. Tom is the sole approval gate before merge.
- Frozen integration flags (`LIONWHEEL_FG_OUT_BRIDGE_ENABLED`, `SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED`) are not touched.
- Authoring agent: `backend-db-executor`.

---

## File Structure

| File | Status | Purpose |
|---|---|---|
| `gt-factory-os/db/migrations/0180_master_data_consistency_pass1.sql` | CREATE | The forward-only migration. Idempotent via marker check. Wraps the 6 logical sections (A.5 → A.1 → A.6 → A.2 → A.3 → A.4) in a single transaction. |
| `gt-factory-os/db/tests/0180_master_data_consistency.test.sql` | CREATE | pgTAP file with 7 assertions T1–T7. Self-contained `begin;…rollback;` so it doesn't pollute DB state. Extends per Wave 2 to T1–T13 later. |
| `gt-factory-os/package.json` | MODIFY | Add `db:apply:0180` and `db:test:0180` script entries, mirroring the pattern of existing entries (psql + pg_prove). |
| `gt-factory-os/fixtures/masters/components.json` | MODIFY (re-extract) | Re-generated from live DB via `npm run extract-fixtures` after migration applies. Hand-patching is forbidden (would diverge from DB truth). |
| `gt-factory-os/fixtures/masters/bom_lines.json` | MODIFY (re-extract) | Same — re-extracted, not hand-edited. |
| `PRODUCTION/.claude/state/runtime_ready.json` | MODIFY (append) | Append `RUNTIME_READY(MasterDataConsistency)` signal entry. Append-only; never overwrite or remove existing entries. |
| `PRODUCTION/docs/master-data-reconciliation/2026-05-10-master-data-fix-design.md` | MODIFY (3 spots) | Update migration number references from `0167…0171` to `0180…` (Wave 1 reality differs from spec assumption). Wave 2 numbers shift accordingly. |

---

## Pre-flight assumptions to verify before any writes

The spec was written against the *fixtures* state. The live DB has progressed through 0166–0179 since fixtures were last extracted. Some assumptions may have shifted. Verify them before writing the migration body.

### Task 0: Pre-flight — verify live DB state matches spec assumptions

**Files:**
- Read-only: live DB via `$DATABASE_URL` from `.env`
- No file writes in this task

- [ ] **Step 1: Connect to live DB and confirm baseline counts**

Run from `gt-factory-os/` repo root:
```bash
set -a; source .env; set +a
psql "$DATABASE_URL" -c "
  set search_path to private_core, public;
  select 'components' as table, count(*) from components
  union all select 'bom_lines', count(*) from bom_lines
  union all select 'bom_head', count(*) from bom_head;
"
```
Expected (within ±5 row drift from fixture-time): `components ≈ 145`, `bom_lines ≈ 420`, `bom_head ≈ 68`.

- [ ] **Step 2: Verify the 5 specific component IDs the migration touches still exist**

```bash
psql "$DATABASE_URL" -c "
  set search_path to private_core, public;
  select component_id, component_name, status
    from components
   where component_id in ('RAW-CALM','RAW-WINE-WHITE','RAW-CORNATION','RAW-COLVE','PKG-CAP-STD','RAW-CLOVE','PKG-CAP-BLACK-METAL-28')
   order by component_id;
"
```
Expected: 7 rows. If `RAW-CALM` already shows `Chamomile flowers (dried)` as the name, **HALT** — the migration was already applied; do not re-run. If any of the 5 deletion targets (`RAW-CORNATION`, `RAW-COLVE`, `PKG-CAP-STD`) is already `STATUS='INACTIVE'`, the migration's A.4 idempotency guard handles it.

- [ ] **Step 3: Verify there is no FK reference outside `bom_lines` blocking A.4 deprecation**

```bash
psql "$DATABASE_URL" -c "
  set search_path to private_core, public;
  -- supplier_items FK
  select 'supplier_items' as src, count(*) as refs
    from supplier_items where component_id in ('RAW-CORNATION','RAW-COLVE','PKG-CAP-STD')
  union all
  select 'stock_ledger', count(*) from stock_ledger
   where item_id in ('RAW-CORNATION','RAW-COLVE','PKG-CAP-STD')
  union all
  select 'balance_anchors', count(*) from balance_anchors
   where item_id in ('RAW-CORNATION','RAW-COLVE','PKG-CAP-STD');
"
```
Expected: 0 across all three sources. If any is non-zero, **HALT** and switch A.4 from `STATUS='INACTIVE'` to a softer "no-op + flag for Tom triage" — deletion or deprecation cannot proceed against a referenced master.

- [ ] **Step 4: Snapshot current pgTAP audit-script result for diff comparison post-apply**

```bash
node scripts/bom_master_audit.mjs > /tmp/audit-pre-0180.txt 2>&1
grep -E "^=== |^count: |^total:" /tmp/audit-pre-0180.txt
```
Save the pre-apply numbers (semantic mismatches, blank names, dup names) as evidence for the post-apply diff in Task 14.

- [ ] **Step 5: Confirm next free migration number is 0180**

```bash
ls db/migrations/ | grep -E "^[0-9]{4}_" | sort | tail -5
```
Expected: latest is `0179_planning_policy_audit_trail.sql`. If anything ≥ 0180 exists, **HALT** and rename to next free number consistently throughout this plan.

---

## Section A: Write the regression-locking pgTAP tests FIRST (TDD)

The pgTAP test file expresses the post-fix invariants. Run it against the live DB BEFORE writing the migration to confirm it fails (proving drift exists). Then write the migration. Then re-run; it passes.

### Task 1: pgTAP scaffold + extension + plan(7)

**Files:**
- Create: `gt-factory-os/db/tests/0180_master_data_consistency.test.sql`

- [ ] **Step 1: Create the pgTAP file with the standard header and plan(7)**

```sql
-- ===========================================================================
-- 0180_master_data_consistency.test.sql
-- ===========================================================================
-- pgTAP regression tests for master-data consistency across components,
-- bom_lines, bom_head, and component_aliases.
--
-- Locks the seven invariants from
--   docs/master-data-reconciliation/2026-05-10-master-data-fix-design.md §3 Wave 1.
--
-- Wave 1 covers T1-T7. Wave 2 extends to T1-T13.
--
-- Run with:
--   pg_prove -d "$DATABASE_URL" db/tests/0180_master_data_consistency.test.sql
--
-- Self-contained: every assertion runs against current DB state inside a
-- single rolled-back transaction. No fixtures inserted; tests assert
-- properties of the production master, not synthetic data.
-- ===========================================================================

begin;

create extension if not exists pgtap;

select plan(7);

set search_path to private_core, public;
```

- [ ] **Step 2: Add file footer (will be appended after T1-T7)**

Save the file with just the header for now. The footer (`select * from finish(); rollback;`) is added in Task 8.

- [ ] **Step 3: Commit scaffold**

```bash
git add db/tests/0180_master_data_consistency.test.sql
git commit -m "test(master-data): pgTAP scaffold for 0180 master-data consistency"
```

### Task 2: T1 — every RAW_NAME/COMPONENT bom_line ID resolves in components master

**Files:**
- Modify: `gt-factory-os/db/tests/0180_master_data_consistency.test.sql` (append)

- [ ] **Step 1: Append T1 assertion**

```sql
-- ===========================================================================
-- T1 — every active bom_line with ref_type IN ('RAW_NAME','COMPONENT')
--      points to a component_id that exists in components master.
-- ===========================================================================
select is(
  (select count(*)::int
     from bom_lines bl
    where bl.status = 'ACTIVE'
      and bl.component_ref_type in ('RAW_NAME','COMPONENT')
      and not exists (
        select 1 from components c where c.component_id = bl.final_component_id
      )),
  0,
  'T1: no active RAW/COMPONENT bom_line points to a missing component_id'
);
```

- [ ] **Step 2: Run against live DB to verify it ALREADY passes (no orphan IDs in current data)**

```bash
pg_prove -d "$DATABASE_URL" db/tests/0180_master_data_consistency.test.sql
```
Expected: `ok 1 - T1: ...` then a "Bad plan: planned 7 tests, ran 1" warning (we only have 1 of 7 written so far). The assertion itself passes because the audit script confirmed 0 ID orphans.

- [ ] **Step 3: Commit**

```bash
git add db/tests/0180_master_data_consistency.test.sql
git commit -m "test(master-data): T1 - every RAW/COMPONENT bom_line resolves in master"
```

### Task 3: T2 — every BASE_BOM/BOM bom_line ID resolves in bom_head

- [ ] **Step 1: Append T2 assertion**

```sql
-- ===========================================================================
-- T2 — every active bom_line with ref_type IN ('BASE_BOM','BOM')
--      points to a bom_head_id that exists.
-- ===========================================================================
select is(
  (select count(*)::int
     from bom_lines bl
    where bl.status = 'ACTIVE'
      and bl.component_ref_type in ('BASE_BOM','BOM')
      and not exists (
        select 1 from bom_head bh where bh.bom_head_id = bl.final_component_id
      )),
  0,
  'T2: no active BASE_BOM/BOM bom_line points to a missing bom_head_id'
);
```

- [ ] **Step 2: Re-run pg_prove. Expected: T1+T2 both pass.**

- [ ] **Step 3: Commit**

```bash
git add db/tests/0180_master_data_consistency.test.sql
git commit -m "test(master-data): T2 - every BASE_BOM/BOM bom_line resolves in bom_head"
```

### Task 4: T3 — no bom_line has NULL or blank final_component_name (this WILL fail pre-migration)

- [ ] **Step 1: Append T3 assertion**

```sql
-- ===========================================================================
-- T3 — every active bom_line has a non-blank final_component_name.
--      Pre-migration: 43 sub-BOM lines have blank names. Test must fail
--      before migration; pass after.
-- ===========================================================================
select is(
  (select count(*)::int
     from bom_lines bl
    where bl.status = 'ACTIVE'
      and (bl.final_component_name is null
        or btrim(bl.final_component_name) = '')),
  0,
  'T3: no active bom_line has a NULL or blank final_component_name'
);
```

- [ ] **Step 2: Run pg_prove against current DB. Expected: T3 FAILS.**

```bash
pg_prove -d "$DATABASE_URL" db/tests/0180_master_data_consistency.test.sql
```
Expected output includes `not ok 3 - T3: ...` with the failing count visible. **This proves the drift exists and the test catches it.** Save this output as evidence in `/tmp/audit-pre-0180.txt`.

- [ ] **Step 3: Commit (failing test is intentional in TDD — committing the regression-locking test is the goal)**

```bash
git add db/tests/0180_master_data_consistency.test.sql
git commit -m "test(master-data): T3 - no blank final_component_name (currently FAILS, locked for migration 0180 to fix)"
```

### Task 5: T4 — bom_line display name == master canonical (active versions only)

- [ ] **Step 1: Append T4 assertion**

```sql
-- ===========================================================================
-- T4 — every active RAW_NAME/COMPONENT bom_line has its final_component_name
--      equal to the master's canonical COMPONENT_NAME for the same id.
--      Pre-migration: at least RAW-CALM and RAW-WINE-WHITE diverge. Plus
--      Matcha re-orderings. Test must fail before migration; pass after.
-- ===========================================================================
select is(
  (select count(*)::int
     from bom_lines bl
     join components c on c.component_id = bl.final_component_id
    where bl.status = 'ACTIVE'
      and bl.component_ref_type in ('RAW_NAME','COMPONENT')
      and lower(btrim(bl.final_component_name)) is distinct from lower(btrim(c.component_name))),
  0,
  'T4: every active RAW/COMPONENT bom_line display name matches master canonical (case+trim insensitive)'
);
```

- [ ] **Step 2: Run pg_prove. Expected: T4 FAILS pre-migration.**

- [ ] **Step 3: Commit**

```bash
git add db/tests/0180_master_data_consistency.test.sql
git commit -m "test(master-data): T4 - bom_line display name matches master canonical (currently FAILS)"
```

### Task 6: T5 — components master has no duplicate canonical names among ACTIVE/PENDING

- [ ] **Step 1: Append T5 assertion**

```sql
-- ===========================================================================
-- T5 — among components with STATUS in ('ACTIVE','PENDING'),
--      lower(btrim(component_name)) is unique.
--      Pre-migration: 'whole clove' has 3 ids; 'black cap 28mm' has 2.
--      Test fails pre, passes post (after A.4 deprecates duplicates).
-- ===========================================================================
select is(
  (select count(*)::int from (
     select lower(btrim(component_name)) as norm_name
       from components
      where status in ('ACTIVE','PENDING')
      group by lower(btrim(component_name))
     having count(*) > 1
   ) dup),
  0,
  'T5: no two ACTIVE/PENDING components share a canonical name (case+trim insensitive)'
);
```

- [ ] **Step 2: Run pg_prove. Expected: T5 FAILS (returns 2 — Whole Clove and Black Cap).**

- [ ] **Step 3: Commit**

```bash
git add db/tests/0180_master_data_consistency.test.sql
git commit -m "test(master-data): T5 - no duplicate canonical names in ACTIVE/PENDING (currently FAILS)"
```

### Task 7: T6 — every component referenced by an ACTIVE bom_line has STATUS in ACTIVE/PENDING

- [ ] **Step 1: Append T6 assertion**

```sql
-- ===========================================================================
-- T6 — every component referenced by any active bom_line is itself
--      in an active-or-pending status. Catches the case where someone
--      deactivates a master row that BOMs still depend on.
-- ===========================================================================
select is(
  (select count(*)::int
     from bom_lines bl
     join components c on c.component_id = bl.final_component_id
    where bl.status = 'ACTIVE'
      and bl.component_ref_type in ('RAW_NAME','COMPONENT')
      and c.status not in ('ACTIVE','PENDING')),
  0,
  'T6: no ACTIVE bom_line references a non-ACTIVE/PENDING component'
);
```

- [ ] **Step 2: Run pg_prove. Expected: T6 PASSES (no current violations — the migration must preserve this).**

- [ ] **Step 3: Commit**

```bash
git add db/tests/0180_master_data_consistency.test.sql
git commit -m "test(master-data): T6 - active bom_lines reference only ACTIVE/PENDING components"
```

### Task 8: T7 — every BASE_BOM/BOM bom_line has display name = bom_head.label

- [ ] **Step 1: Append T7 assertion + pgTAP footer**

```sql
-- ===========================================================================
-- T7 — every active BASE_BOM/BOM bom_line has its display name equal to
--      the referenced bom_head's label. Pre-migration: 43 such lines have
--      NULL/blank display name. Same set caught by T3, but T7 enforces
--      the corrective value (label, not just non-blank).
-- ===========================================================================
select is(
  (select count(*)::int
     from bom_lines bl
     join bom_head bh on bh.bom_head_id = bl.final_component_id
    where bl.status = 'ACTIVE'
      and bl.component_ref_type in ('BASE_BOM','BOM')
      and lower(btrim(coalesce(bl.final_component_name,''))) is distinct from lower(btrim(coalesce(bh.label,'')))),
  0,
  'T7: every active BASE_BOM/BOM bom_line display name equals bom_head.label'
);

select * from finish();
rollback;
```

- [ ] **Step 2: Run pg_prove. Expected: T1, T2, T6 PASS; T3, T4, T5, T7 FAIL. 4 failures × 7 tests.**

```bash
pg_prove -d "$DATABASE_URL" db/tests/0180_master_data_consistency.test.sql 2>&1 | tee /tmp/pgtap-pre-0180.txt
```
Save this output. **This is the "test fails first" evidence required by TDD.** The migration is what makes them all pass.

- [ ] **Step 3: Commit**

```bash
git add db/tests/0180_master_data_consistency.test.sql
git commit -m "test(master-data): T7 - bom_line display name = bom_head.label (currently FAILS)

Pre-migration baseline: T3, T4, T5, T7 fail; T1, T2, T6 pass.
Migration 0180 must drive all 7 to PASS."
```

---

## Section B: Write the migration (sections A.5 → A.6 → A.1 → A.2 → A.3 → A.4)

The migration is one file, one transaction, idempotent via marker check. Each task adds one logical section.

### Task 9: Migration file scaffold + idempotency guard + transaction wrap

**Files:**
- Create: `gt-factory-os/db/migrations/0180_master_data_consistency_pass1.sql`

- [ ] **Step 1: Create the file with header, idempotency marker, and BEGIN/COMMIT shell**

```sql
-- ===========================================================================
-- 0180_master_data_consistency_pass1.sql
-- ===========================================================================
-- Master-data consistency hot-fix Wave 1.
--
-- Source: PRODUCTION/docs/master-data-reconciliation/2026-05-10-master-data-fix-design.md
--         §3 Wave 1, Tom approved 2026-05-10.
--
-- Closes the immediate Chamomile-class blocker on /(ops)/stock/physical-count
-- so operators can find every BOM-referenced component by an operator-friendly
-- name. Establishes the component_aliases table for Wave 2.
--
-- Sections (executed in this order to keep old names searchable through the
-- transaction window):
--   A.5  Create component_aliases table.
--   A.6  Seed 8 alias rows mapping old/floor names to current ids.
--   A.1  Rename RAW-CALM to "Chamomile flowers (dried)" and RAW-WINE-WHITE to "Wine — White (Symphony)".
--   A.2  Normalize bom_lines.final_component_name on ACTIVE versions to match master canonical.
--   A.3  Fill blank display name on ACTIVE BASE_BOM/BOM bom_lines using bom_head.label.
--   A.4  Set STATUS='INACTIVE' on the 3 unreferenced duplicate ids:
--        RAW-CORNATION, RAW-COLVE, PKG-CAP-STD.
--   A.7  Emit one change_log row summarising the operation.
--
-- Idempotency: marker check on component_aliases existence + canonical name
-- of RAW-CALM. If both already in their post-state, the migration logs and
-- returns.
--
-- Forward-only. Rollback is documented as inverse SQL in this header
-- (no separate down-migration file, per repo posture).
--
-- INVERSE OPERATIONS (if a true rollback is ever needed, executed in reverse
-- order, manually, with Tom approval):
--   A.7  Insert reversal change_log row.
--   A.4  Update components set status='ACTIVE' where component_id in
--        ('RAW-CORNATION','RAW-COLVE','PKG-CAP-STD').
--   A.3  No automated inverse — re-extract pre-migration snapshot from
--        change_log payload.
--   A.2  Same.
--   A.1  Update components set component_name = 'Calm (GT Tea Extract -
--        Chamomile blend)' where component_id='RAW-CALM'; update
--        components set component_name='Wine' where component_id='RAW-WINE-WHITE'.
--   A.6  Delete from component_aliases where source='import' and
--        alias in ('Calm (GT Tea Extract - Chamomile blend)','Chamomile',
--        'camomile','Wine','White wine','Wine (white) Symphony',
--        'Whole Clove','Black Cap 28mm').
--   A.5  Drop table component_aliases.
-- ===========================================================================

begin;

set search_path to private_core, public;

do $$
declare
  v_already_applied boolean;
  v_actor uuid := '00000000-0000-0000-0000-000000000000';  -- system migration actor
  v_renamed_count int := 0;
  v_normalized_count int := 0;
  v_blank_filled_count int := 0;
  v_deprecated_count int := 0;
begin

  -- =========================================================================
  -- Idempotency guard
  -- =========================================================================
  select (
    exists (select 1 from information_schema.tables
             where table_schema='private_core' and table_name='component_aliases')
    and exists (select 1 from components
                 where component_id='RAW-CALM'
                   and component_name='Chamomile flowers (dried)')
  ) into v_already_applied;

  if v_already_applied then
    raise notice 'Migration 0180 already applied (component_aliases exists and RAW-CALM is renamed). Skipping.';
    return;
  end if;

  -- (Sections A.5 through A.7 are appended in subsequent tasks)

end$$;

commit;
```

- [ ] **Step 2: Sanity-check the file parses**

```bash
psql --dry-run --no-psqlrc -f db/migrations/0180_master_data_consistency_pass1.sql 2>&1 || true
```
Note: psql doesn't have a real `--dry-run`; instead validate by checking syntax with a parser like `pgsanity` if installed, OR apply against a throwaway branch DB. For this scaffold step, just confirm the file exists and commits cleanly.

- [ ] **Step 3: Commit scaffold**

```bash
git add db/migrations/0180_master_data_consistency_pass1.sql
git commit -m "feat(master-data): 0180 migration scaffold + idempotency guard"
```

### Task 10: A.5 — create `component_aliases` table

- [ ] **Step 1: Insert A.5 SQL into the `do $$ … $$` block, before the `end$$;` line**

Replace the comment line `-- (Sections A.5 through A.7 are appended in subsequent tasks)` with:

```sql
  -- =========================================================================
  -- A.5  Create component_aliases table
  -- =========================================================================
  create table if not exists component_aliases (
    alias_id      bigserial primary key,
    component_id  text not null references components(component_id) on delete cascade,
    alias         text not null,
    alias_norm    text generated always as (lower(btrim(alias))) stored,
    source        text not null check (source in ('manual','import','operator_capture','planning_history')),
    created_at    timestamptz not null default now(),
    constraint component_aliases_unique_norm unique (alias_norm)
  );

  create index if not exists component_aliases_by_component
    on component_aliases(component_id);

  raise notice 'A.5 component_aliases table created (or already existed).';
```

- [ ] **Step 2: Apply migration to live DB to verify A.5 alone**

⚠️ Do NOT apply yet if Tom has not approved. For now, confirm syntax via:
```bash
psql "$DATABASE_URL" -c "begin; \i db/migrations/0180_master_data_consistency_pass1.sql ; rollback;"
```
Expected: notice messages emitted, no errors. The `rollback` undoes any DDL/DML.

If the dry-run rolls back cleanly, proceed. If errors, fix syntax and retry.

- [ ] **Step 3: Commit**

```bash
git add db/migrations/0180_master_data_consistency_pass1.sql
git commit -m "feat(master-data): 0180 A.5 - create component_aliases table"
```

### Task 11: A.6 — seed 8 alias rows

- [ ] **Step 1: Append A.6 to the `do $$` block (after A.5's `raise notice`)**

```sql
  -- =========================================================================
  -- A.6  Seed 8 alias rows. These keep the OLD canonical names and the
  --      operator floor terms searchable through the rename window in A.1.
  --      Idempotent via the unique constraint on alias_norm.
  -- =========================================================================
  insert into component_aliases (component_id, alias, source) values
    ('RAW-CALM',                'Calm (GT Tea Extract - Chamomile blend)', 'import'),
    ('RAW-CALM',                'Chamomile',                                'import'),
    ('RAW-CALM',                'camomile',                                 'import'),
    ('RAW-WINE-WHITE',          'Wine',                                     'import'),
    ('RAW-WINE-WHITE',          'White wine',                               'import'),
    ('RAW-WINE-WHITE',          'Wine (white) Symphony',                    'import'),
    ('RAW-CLOVE',               'Whole Clove',                              'import'),
    ('PKG-CAP-BLACK-METAL-28',  'Black Cap 28mm',                           'import')
  on conflict (alias_norm) do nothing;

  raise notice 'A.6 alias seed inserted (8 rows; conflicts skipped).';
```

- [ ] **Step 2: Dry-run again**

```bash
psql "$DATABASE_URL" -c "begin; \i db/migrations/0180_master_data_consistency_pass1.sql ; rollback;"
```

- [ ] **Step 3: Commit**

```bash
git add db/migrations/0180_master_data_consistency_pass1.sql
git commit -m "feat(master-data): 0180 A.6 - seed 8 alias rows for renamed/duplicate components"
```

### Task 12: A.1 — rename RAW-CALM and RAW-WINE-WHITE

- [ ] **Step 1: Append A.1 to the `do $$` block**

```sql
  -- =========================================================================
  -- A.1  Rename RAW-CALM and RAW-WINE-WHITE to floor-truth canonical names.
  --      Old names already preserved as aliases in A.6 — no search gap.
  --      WHERE clause guards against re-renaming if migration partially ran.
  -- =========================================================================
  update components
     set component_name = 'Chamomile flowers (dried)'
   where component_id = 'RAW-CALM'
     and component_name = 'Calm (GT Tea Extract - Chamomile blend)';
  get diagnostics v_renamed_count = row_count;

  update components
     set component_name = 'Wine — White (Symphony)'
   where component_id = 'RAW-WINE-WHITE'
     and component_name = 'Wine';
  get diagnostics v_renamed_count = v_renamed_count + row_count;

  raise notice 'A.1 components renamed: % rows', v_renamed_count;
```

- [ ] **Step 2: Dry-run**

```bash
psql "$DATABASE_URL" -c "begin; \i db/migrations/0180_master_data_consistency_pass1.sql ; rollback;"
```
Expected: notice `A.1 components renamed: 2 rows` (or fewer if RAW-WINE-WHITE master has different starting value — adjust WHERE if needed).

- [ ] **Step 3: Commit**

```bash
git add db/migrations/0180_master_data_consistency_pass1.sql
git commit -m "feat(master-data): 0180 A.1 - rename RAW-CALM and RAW-WINE-WHITE to floor truth"
```

### Task 13: A.2 — normalize bom_lines.final_component_name on ACTIVE versions

- [ ] **Step 1: Append A.2 to the `do $$` block**

```sql
  -- =========================================================================
  -- A.2  For ACTIVE bom_lines pointing to a master component, force
  --      final_component_name = master canonical. Operates on every
  --      version (active or otherwise) because the column is a denormalized
  --      cache that should reflect canonical truth, not historical phrasing.
  --      For ACTIVE-only behaviour, see filter on bl.status.
  -- =========================================================================
  update bom_lines bl
     set final_component_name = c.component_name
    from components c
   where bl.final_component_id = c.component_id
     and bl.component_ref_type in ('RAW_NAME','COMPONENT')
     and bl.status = 'ACTIVE'
     and bl.final_component_name is distinct from c.component_name;
  get diagnostics v_normalized_count = row_count;

  raise notice 'A.2 bom_lines display name normalized to canonical: % rows', v_normalized_count;
```

- [ ] **Step 2: Dry-run**

```bash
psql "$DATABASE_URL" -c "begin; \i db/migrations/0180_master_data_consistency_pass1.sql ; rollback;"
```
Expected: notice with row count > 0 (the audit found 9 non-trivial mismatches; expect 9–14 depending on case-sensitivity).

- [ ] **Step 3: Commit**

```bash
git add db/migrations/0180_master_data_consistency_pass1.sql
git commit -m "feat(master-data): 0180 A.2 - normalize bom_lines display name to master canonical"
```

### Task 14: A.3 — fill blank display name on ACTIVE BASE_BOM/BOM bom_lines

- [ ] **Step 1: Append A.3 to the `do $$` block**

```sql
  -- =========================================================================
  -- A.3  For ACTIVE bom_lines that reference a sub-BOM (BASE_BOM or BOM
  --      ref-type), copy bom_head.label into final_component_name when it
  --      is currently NULL or blank. Does NOT overwrite manually-set names.
  -- =========================================================================
  update bom_lines bl
     set final_component_name = bh.label
    from bom_head bh
   where bl.final_component_id = bh.bom_head_id
     and bl.component_ref_type in ('BASE_BOM','BOM')
     and bl.status = 'ACTIVE'
     and (bl.final_component_name is null or btrim(bl.final_component_name) = '');
  get diagnostics v_blank_filled_count = row_count;

  raise notice 'A.3 sub-BOM blank display names filled from bom_head.label: % rows', v_blank_filled_count;
```

- [ ] **Step 2: Dry-run**

```bash
psql "$DATABASE_URL" -c "begin; \i db/migrations/0180_master_data_consistency_pass1.sql ; rollback;"
```
Expected: notice with row count ≈ 43 (audit-time count of blank sub-BOM lines on ACTIVE versions).

- [ ] **Step 3: Commit**

```bash
git add db/migrations/0180_master_data_consistency_pass1.sql
git commit -m "feat(master-data): 0180 A.3 - fill blank sub-BOM display names from bom_head.label"
```

### Task 15: A.4 — set STATUS='INACTIVE' for 3 unreferenced duplicate IDs

- [ ] **Step 1: Append A.4 to the `do $$` block**

```sql
  -- =========================================================================
  -- A.4  Deprecate (NOT delete) the 3 unreferenced duplicate ids that
  --      collided on canonical name with a primary id:
  --        RAW-CORNATION   = duplicate of RAW-CLOVE             ("Whole Clove")
  --        RAW-COLVE       = duplicate of RAW-CLOVE             ("Whole Clove")
  --        PKG-CAP-STD     = duplicate of PKG-CAP-BLACK-METAL-28 ("Black Cap 28mm")
  --      Guarded by NOT EXISTS check on bom_lines, supplier_items,
  --      stock_ledger, balance_anchors. If any reference exists, the row
  --      is left untouched and a warning is raised — Tom triages manually.
  -- =========================================================================
  update components
     set status = 'INACTIVE'
   where component_id in ('RAW-CORNATION','RAW-COLVE','PKG-CAP-STD')
     and status <> 'INACTIVE'
     and not exists (select 1 from bom_lines      where final_component_id = component_id)
     and not exists (select 1 from supplier_items where component_id      = components.component_id)
     and not exists (select 1 from stock_ledger   where item_id            = components.component_id)
     and not exists (select 1 from balance_anchors where item_id           = components.component_id);
  get diagnostics v_deprecated_count = row_count;

  if v_deprecated_count < 3 then
    raise notice 'A.4 deprecation incomplete: % of 3 rows deprecated. Tom must triage references for the remaining ids.', v_deprecated_count;
  else
    raise notice 'A.4 deprecation complete: 3 of 3 rows set to INACTIVE.';
  end if;
```

- [ ] **Step 2: Dry-run**

```bash
psql "$DATABASE_URL" -c "begin; \i db/migrations/0180_master_data_consistency_pass1.sql ; rollback;"
```
Expected: notice `A.4 deprecation complete: 3 of 3 rows set to INACTIVE.` — confirms Pre-flight Task 0 Step 3 expectation that no FK references exist.

- [ ] **Step 3: Commit**

```bash
git add db/migrations/0180_master_data_consistency_pass1.sql
git commit -m "feat(master-data): 0180 A.4 - deprecate 3 unreferenced duplicate component ids"
```

### Task 16: A.7 — emit one summary change_log row

- [ ] **Step 1: Verify change_log table shape before writing the insert**

```bash
psql "$DATABASE_URL" -c "
  set search_path to private_core, public;
  select column_name, data_type, is_nullable
    from information_schema.columns
   where table_schema='private_core' and table_name='change_log'
   order by ordinal_position;
"
```
Capture the column list. Adapt the INSERT in Step 2 to match the actual column names. Common columns expected: `change_id`, `actor_user_id`, `entity_type`, `entity_id`, `operation`, `before_state`, `after_state`, `reason`, `created_at`. If the actual schema differs (e.g., `actor` vs `actor_user_id`), use the actual names.

- [ ] **Step 2: Append A.7 to the `do $$` block, replacing the placeholder column names with the actual schema from Step 1**

```sql
  -- =========================================================================
  -- A.7  Emit a single summary change_log row describing this migration's
  --      total impact. Per-row before/after captured in raw_payload jsonb.
  -- =========================================================================
  insert into change_log (
    actor_user_id, entity_type, entity_id, operation, reason, created_at,
    before_state, after_state
  ) values (
    v_actor,
    'master_data_consistency',
    '0180_master_data_consistency_pass1',
    'migration_apply',
    'Master-data Wave 1 hot-fix: 2 renames, ' || v_normalized_count ||
      ' bom_line normalizations, ' || v_blank_filled_count ||
      ' sub-BOM blank fills, ' || v_deprecated_count || ' deprecations, ' ||
      'aliases table created with 8 seed rows.',
    now(),
    jsonb_build_object('migration','0180','phase','before',
      'renamed_targets', jsonb_build_array('RAW-CALM','RAW-WINE-WHITE'),
      'deprecated_targets', jsonb_build_array('RAW-CORNATION','RAW-COLVE','PKG-CAP-STD')),
    jsonb_build_object('migration','0180','phase','after',
      'renamed_count', v_renamed_count,
      'normalized_count', v_normalized_count,
      'blank_filled_count', v_blank_filled_count,
      'deprecated_count', v_deprecated_count,
      'aliases_seeded', 8)
  );

  raise notice 'A.7 change_log summary row emitted.';
```

- [ ] **Step 3: Adjust column names if Step 1 revealed differences. Dry-run.**

```bash
psql "$DATABASE_URL" -c "begin; \i db/migrations/0180_master_data_consistency_pass1.sql ; rollback;"
```

- [ ] **Step 4: Commit**

```bash
git add db/migrations/0180_master_data_consistency_pass1.sql
git commit -m "feat(master-data): 0180 A.7 - change_log summary row"
```

---

## Section C: npm scripts + apply + verify

### Task 17: Add npm script entries

**Files:**
- Modify: `gt-factory-os/package.json`

- [ ] **Step 1: Add `db:apply:0180` and `db:test:0180` entries**

In `package.json`, in the `"scripts"` object, add (in numerically-sorted order, near the other 01xx entries):
```json
    "db:apply:0180": "psql \"$DATABASE_URL\" -v ON_ERROR_STOP=1 -f db/migrations/0180_master_data_consistency_pass1.sql",
    "db:test:0180":  "pg_prove -d \"$DATABASE_URL\" db/tests/0180_master_data_consistency.test.sql",
```

- [ ] **Step 2: Verify package.json still parses**

```bash
node -e "JSON.parse(require('fs').readFileSync('package.json','utf8')); console.log('package.json OK')"
```
Expected: `package.json OK`.

- [ ] **Step 3: Commit**

```bash
git add package.json
git commit -m "chore(master-data): npm scripts for 0180 apply + test"
```

### Task 18: STOP — Tom approval gate before applying to live DB

- [ ] **Step 1: Produce the approval packet**

The `backend-db-executor` MUST stop here and assemble for Tom:

1. The two new files: migration + pgTAP
2. Pre-flight Task 0 outputs (live DB baseline counts + audit pre-snapshot + pgTAP pre-fail evidence)
3. Diff URL or PR link if working through GitHub
4. Plain-language summary in Hebrew suitable for Tom's review (template):

> *Migration 0180 מוכנה ליישום. תיקון 7 שמות, מילוי 43 שורות BOM ריקות, יצירת טבלת aliases עם 8 שורות seed, השבתת 3 IDs כפולים. pgTAP T1-T7 נכשל היום (כצפוי) ויעבור אחרי היישום. Dry-run עבר ללא שגיאות. ממתין לאישור.*

- [ ] **Step 2: WAIT for Tom written approval before proceeding to Task 19.**

Do NOT execute `npm run db:apply:0180` until Tom replies with explicit approval.

### Task 19: Apply migration to live DB (after Tom approval)

- [ ] **Step 1: Apply**

```bash
set -a; source .env; set +a
npm run db:apply:0180
```
Expected: notices showing each section's row counts; final `COMMIT` line; exit code 0.

- [ ] **Step 2: Run pgTAP**

```bash
npm run db:test:0180
```
Expected: `7..7  ok` — all 7 assertions pass.

- [ ] **Step 3: Spot-check the data**

```bash
psql "$DATABASE_URL" -c "
  set search_path to private_core, public;
  select component_id, component_name, status from components
   where component_id in ('RAW-CALM','RAW-WINE-WHITE','RAW-CORNATION','RAW-COLVE','PKG-CAP-STD')
   order by component_id;
  select alias, component_id from component_aliases order by component_id, alias;
  select count(*) as blank_subbom from bom_lines
   where status='ACTIVE' and component_ref_type in ('BASE_BOM','BOM')
     and (final_component_name is null or btrim(final_component_name)='');
"
```
Expected:
- `RAW-CALM` → "Chamomile flowers (dried)", status ACTIVE
- `RAW-WINE-WHITE` → "Wine — White (Symphony)", status ACTIVE
- `RAW-CORNATION`, `RAW-COLVE`, `PKG-CAP-STD` → status INACTIVE
- 8 alias rows present
- `blank_subbom` = 0

- [ ] **Step 4: Re-run audit script**

```bash
node scripts/bom_master_audit.mjs > /tmp/audit-post-0180.txt 2>&1
diff /tmp/audit-pre-0180.txt /tmp/audit-post-0180.txt | head -100
```
Expected: post-snapshot shows `name_mismatches_semantic=0`, `blank_name_bom_lines=0`, `duplicate_names_in_master=0`.

### Task 20: Re-extract fixtures from live DB

- [ ] **Step 1: Run extractor**

```bash
npm run extract-fixtures
```
Expected: `fixtures/masters/components.json` and `fixtures/masters/bom_lines.json` updated. New file `fixtures/masters/component_aliases.json` may also appear (if extractor recognises new tables; if not, that's a Wave 2 follow-up).

- [ ] **Step 2: Diff sanity check**

```bash
git diff --stat fixtures/masters/
```
Expected: 2-3 files modified; line-count changes consistent with the migration's row impacts.

- [ ] **Step 3: Spot-check the diff for the Chamomile name change**

```bash
git diff fixtures/masters/components.json | grep -E "^\+.*Chamomile|^-.*Calm \(GT"
```
Expected: a `-` line with the old "Calm (GT Tea Extract - Chamomile blend)" and a `+` line with "Chamomile flowers (dried)".

- [ ] **Step 4: Commit**

```bash
git add fixtures/masters/components.json fixtures/masters/bom_lines.json
git add fixtures/masters/component_aliases.json 2>/dev/null || true
git commit -m "data(master-data): re-extract fixtures after 0180 apply"
```

### Task 21: Update the spec doc with the actual migration number

**Files:**
- Modify: `PRODUCTION/docs/master-data-reconciliation/2026-05-10-master-data-fix-design.md`

- [ ] **Step 1: Update three migration-number references**

Replace in the spec:
- `0167_master_data_consistency_pass1` → `0180_master_data_consistency_pass1`
- `0168_component_aliases_full_seed_and_index` → `0181_component_aliases_full_seed_and_index` (for Wave 2 visibility)
- `0169_bom_lines_display_name_lock` → `0182_bom_lines_display_name_lock`
- `0170_components_unique_canonical_name` → `0183_components_unique_canonical_name`
- `0171_components_rename_auto_alias` → `0184_components_rename_auto_alias`

The "next free sequence: 0167…0170" footer line near the bottom of the spec also needs to be updated to reflect the actual numbers.

- [ ] **Step 2: Commit**

```bash
# from PRODUCTION/ repo
git add docs/master-data-reconciliation/2026-05-10-master-data-fix-design.md
git commit -m "docs(spec): bump master-data-fix migration numbers to actual 0180-series"
```

---

## Section D: Emit RUNTIME_READY signal + handoff

### Task 22: Append RUNTIME_READY(MasterDataConsistency) to harness state

**Files:**
- Modify: `PRODUCTION/.claude/state/runtime_ready.json` (append, never overwrite)

- [ ] **Step 1: Read current file**

```bash
cat ".claude/state/runtime_ready.json"
```
Confirm shape (object with `signals` array, or array of signals — match existing pattern exactly).

- [ ] **Step 2: Append the new signal entry**

The new entry shape (adjust keys to match existing entries' schema):
```json
{
  "signal": "RUNTIME_READY(MasterDataConsistency)",
  "emitted_at": "<ISO 8601 UTC timestamp of Task 19 Step 1>",
  "emitted_by": "backend-db-executor",
  "evidence": {
    "migration": "gt-factory-os/db/migrations/0180_master_data_consistency_pass1.sql",
    "pgtap": "gt-factory-os/db/tests/0180_master_data_consistency.test.sql",
    "pgtap_result": "7/7 PASS",
    "audit_post": "gt-factory-os/docs/master-data-reconciliation/bom-master-audit-report.json (re-run shows zero violations)",
    "fixtures_re_extracted": true,
    "rows_renamed": "<from A.7 change_log>",
    "rows_normalized": "<from A.7 change_log>",
    "rows_blank_filled": "<from A.7 change_log>",
    "rows_deprecated": "<from A.7 change_log>",
    "aliases_seeded": 8
  }
}
```

- [ ] **Step 3: Append (never overwrite). Verify JSON still parses.**

```bash
node -e "JSON.parse(require('fs').readFileSync('.claude/state/runtime_ready.json','utf8')); console.log('runtime_ready.json OK')"
```

- [ ] **Step 4: Commit (in PRODUCTION repo)**

```bash
git add .claude/state/runtime_ready.json
git commit -m "state: emit RUNTIME_READY(MasterDataConsistency) for migration 0180"
```

### Task 23: Handoff to release-verifier

- [ ] **Step 1: Produce handoff packet for `release-verifier`**

```text
HANDOFF: Wave 1 Master Data Fix — release-verifier check requested

ARTIFACTS:
- gt-factory-os/db/migrations/0180_master_data_consistency_pass1.sql  (applied)
- gt-factory-os/db/tests/0180_master_data_consistency.test.sql        (7/7 PASS)
- gt-factory-os/fixtures/masters/components.json                       (re-extracted)
- gt-factory-os/fixtures/masters/bom_lines.json                        (re-extracted)
- gt-factory-os/fixtures/masters/component_aliases.json                (new)
- gt-factory-os/package.json                                           (npm scripts added)
- PRODUCTION/.claude/state/runtime_ready.json                          (RUNTIME_READY emitted)
- PRODUCTION/docs/master-data-reconciliation/2026-05-10-master-data-fix-design.md  (migration numbers updated)

EVIDENCE:
- Pre-apply pgTAP: 4/7 fail (T3, T4, T5, T7)
- Post-apply pgTAP: 7/7 pass
- bom_master_audit.mjs pre/post diff: shows semantic_mismatches=0, blank_name_bom_lines=0, duplicate_names_in_master=0
- change_log row inserted with full before/after payload
- All git commits pushed to feature branch (NOT main)
- Tom written approval recorded at <link>

REQUEST: pre-merge verification per release-verifier policy. Confirm:
1. All changed files within authoring boundary for backend-db-executor
2. No portal source touched
3. No frozen flag flipped
4. No locked-decision violation
5. Evidence pack complete

Awaiting verifier verdict before Tom merges to main.
```

- [ ] **Step 2: Mark plan complete in todo system; pass to release-verifier; do NOT merge.**

---

## Self-Review

After completing the plan above, the following checks must pass:

**Spec coverage:**
- §3 Wave 1 A.1 (RAW-CALM, RAW-WINE-WHITE renames) → Task 12 ✓
- §3 Wave 1 A.2 (bom_lines normalize) → Task 13 ✓
- §3 Wave 1 A.3 (sub-BOM blank fill) → Task 14 ✓
- §3 Wave 1 A.4 (3 duplicates) → Task 15 (changed from DELETE to INACTIVE) ✓
- §3 Wave 1 A.5 (component_aliases table) → Task 10 ✓
- §3 Wave 1 A.6 (8 alias seed rows) → Task 11 ✓
- §3 Wave 1 pgTAP T1–T7 → Tasks 2–8 ✓
- §3 Wave 1 fixtures patch → Task 20 (re-extract, not hand-patch — corrects spec) ✓
- §3 Wave 1 RUNTIME_READY emission → Task 22 ✓
- §3 Wave 1 evidence pack → Task 23 ✓
- Tom approval gate before merge → Task 18 ✓
- §3 Wave 1 change_log → Task 16 ✓

**Placeholder scan:** None. All file paths are exact, all SQL is complete, all assertions are concrete.

**Type/name consistency:**
- `component_aliases` table named consistently across A.5 / A.6 / A.7 / pgTAP T8+ (Wave 2)
- Column names: `alias_id`, `component_id`, `alias`, `alias_norm`, `source`, `created_at` — used identically in CREATE and INSERT
- `final_component_name` lowercase consistently (matches existing fixture & migration 0166 usage)
- Schema `private_core` referenced in every SQL block

**Deviations from spec (with reasoning, locked here):**
1. Migration numbers shifted `0167…0171` → `0180…0184`. Spec was authored against an outdated repo tip; live tip is `0179`. Plan Task 21 updates the spec to match.
2. A.4 changed from `DELETE FROM components` to `UPDATE … SET status='INACTIVE'`. Reason: aligns with repo's audit posture (no destructive operations on master data without verification trail) and protects against future FK additions that the migration's NOT EXISTS check might miss.
3. Rollback file removed (`0167_rollback.sql` not created). Reason: repo posture is forward-only per `db/README.md`. Inverse operations documented in the migration's header comment, executable manually if Tom ever requests it.
4. Fixtures updated via `npm run extract-fixtures`, not hand-patch. Reason: ensures DB is the truth and fixtures match without divergence risk.

---

## Execution Handoff

Plan complete and saved to `PRODUCTION/docs/superpowers/plans/2026-05-10-master-data-fix-wave-1.md`. Two execution options:

**1. Subagent-Driven (recommended)** — Dispatch a fresh `backend-db-executor` per task, with two-stage review between tasks. Especially important for Task 18 (Tom approval gate) and Task 19 (live DB write).

**2. Inline Execution** — A single `backend-db-executor` runs the full plan in one session with checkpoints at Task 18 (mandatory hold for Tom) and Task 23 (handoff to release-verifier).

For this plan, given a live DB write happens at Task 19, **subagent-driven is strongly recommended**: Task 18's Tom-approval gate becomes a natural pause point with full reviewable artifact context, and Task 19's apply runs with a clean fresh-context worker that has the approval evidence in hand.

Which approach?
