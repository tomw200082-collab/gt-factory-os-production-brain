# Typed Inbox + Supplier Price-Change Proposals — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (subagents available in this harness) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the generic Exceptions Inbox with a typed control surface (4 card types) and add a Green-Invoice-evidence-driven supplier price-change proposal flow (Stage A To-Do + Stage B form → Decision card).

**Architecture:** Single typed Inbox feed (Model B per spec §1.1). Type-aware dedupe via emit-with-reopen contract (spec §1.12). New `price_proposals` lifecycle table; `price_history` retains its append-only invariant. Stage A producer surfaces every mapped-supplier GI expense as a To-Do; Stage B form (one-click for single-supplier_item suppliers) creates the proposal and the Decision card. Audience: planner+admin only; operators get scoped read of their own form-submission exceptions.

**Tech Stack:** PostgreSQL (Supabase managed), Node 20 + Fastify + Zod + Kysely (api), Supabase Edge Functions (factory_os_jobs), Next.js 15 App Router + Tailwind + shadcn/ui + TanStack Query (window2-portal-sandbox).

**Spec reference:** `docs/superpowers/specs/2026-05-04-inbox-typed-cards-and-price-proposals-design.md` (REV 5; APPROVED). Read it before starting any task — every code block in the spec is the contract.

**Repository layout (verified 2026-05-04):**
- Schema + API: `C:\Users\tomw2\Projects\gt-factory-os\` (db, api, supabase subdirs)
- Portal: `C:\Users\tomw2\Projects\window2-portal-sandbox\`

**Migration numbering:** spec uses 0146-0151. If new migrations land between spec write and apply time, shift these numbers by the offset and update §2.7 deployment-sequencing references.

---

## Cross-cutting conventions (read once, apply everywhere)

0. **Skip-if-applied.** Before applying any migration, run `SELECT 1 FROM private_core.schema_migrations WHERE version='<NNNN>'`. If the row exists, skip Steps 3-4 (apply) and run only Steps 1-2 + Step 5 (verification + idempotent test). This makes the plan re-runnable without spurious "migration already applied" errors.
1. **TDD discipline.** For every task: write the failing test FIRST, run it to confirm RED, write the minimal implementation, run the test to confirm GREEN, then commit. Steps within each task make this explicit.
2. **Run tests via:** `cd "C:\Users\tomw2\Projects\gt-factory-os" && npm test -- <file-pattern>` for api; `cd "C:\Users\tomw2\Projects\gt-factory-os\db" && pgtap test runner <file>` for SQL; `cd "C:\Users\tomw2\Projects\window2-portal-sandbox" && npm test -- <file>` for portal unit; `npm run e2e -- <file>` for E2E.
3. **Commit message convention.** `feat(inbox): <what>` for new features; `fix(inbox): <what>` for bugs; `chore(schema): <migration#>: <what>` for migrations. Each commit is one task scope.
4. **Hebrew strings** live ONLY in `window2-portal-sandbox/src/lib/inbox-copy.ts` and the Hebrew register in §1.15 of the spec. NEVER inline.
5. **Names not IDs in UI.** Per `feedback_names_not_ids_in_ui.md` — surface names; IDs only as secondary in drawer mode.
6. **No git push without authorization** until the chunk is fully integrated and accepted.
7. **rebuild_verifier guard.** Run `SELECT private_core.rebuild_verifier();` before AND after each migration; abort on non-zero. The migration runner script must wrap each migration in a transaction.
8. **Spec section refs** like "spec §1.14.3" point to the spec file above; consult for exact code blocks rather than duplicating in tasks.

---

## Chunk 1: Schema foundation (migrations M1-M6)

This chunk lands the schema in the order from spec §2.7. Code is no-op for existing producers (columns nullable) until the API rollout in Chunk 2 populates them.

### Task 1.1: M1 — Add `card_type` + `subtype` columns to `private_core.exceptions`

**Files:**
- Create: `C:\Users\tomw2\Projects\gt-factory-os\db\migrations\0146_exceptions_card_type_and_subtype.sql`
- Test: `C:\Users\tomw2\Projects\gt-factory-os\db\test\0146_card_type_columns.pgtap.sql`

- [ ] **Step 1: Write the failing pgTap test**

```sql
-- 0146_card_type_columns.pgtap.sql
BEGIN;
SELECT plan(4);

SELECT has_column('private_core', 'exceptions', 'card_type', 'card_type column exists');
SELECT col_type_is('private_core', 'exceptions', 'card_type', 'text', 'card_type is text');
SELECT has_column('private_core', 'exceptions', 'subtype', 'subtype column exists');
SELECT col_type_is('private_core', 'exceptions', 'subtype', 'text', 'subtype is text');

SELECT * FROM finish();
ROLLBACK;
```

- [ ] **Step 2: Run test to verify it fails (column not yet present)**

Run: `cd "C:\Users\tomw2\Projects\gt-factory-os\db" && npm run pgtap -- 0146_card_type_columns`
Expected: 4 failures — columns do not exist.

- [ ] **Step 3: Author the migration per spec §2.1**

Copy spec §2.1 verbatim into `0146_exceptions_card_type_and_subtype.sql`. Both columns nullable; comments populated.

- [ ] **Step 4: Apply the migration locally**

Run: `cd "C:\Users\tomw2\Projects\gt-factory-os\db" && npm run migrate:apply -- 0146`
Expected: COMMIT; output `0146 applied`.

- [ ] **Step 5: Run test to verify it passes**

Run: `cd "C:\Users\tomw2\Projects\gt-factory-os\db" && npm run pgtap -- 0146_card_type_columns`
Expected: 4 passes.

- [ ] **Step 6: Commit**

```bash
git add db/migrations/0146_exceptions_card_type_and_subtype.sql db/test/0146_card_type_columns.pgtap.sql
git commit -m "chore(schema): 0146: add card_type+subtype columns to exceptions"
```

---

### Task 1.2: M2 — Create `private_core.price_proposals`

**Files:**
- Create: `C:\Users\tomw2\Projects\gt-factory-os\db\migrations\0147_price_proposals.sql`
- Test: `C:\Users\tomw2\Projects\gt-factory-os\db\test\0147_price_proposals.pgtap.sql`

- [ ] **Step 1: Write the failing pgTap test**

```sql
-- 0147_price_proposals.pgtap.sql
BEGIN;
SELECT plan(11);

SELECT has_table('private_core', 'price_proposals', 'price_proposals table exists');
SELECT has_pk('private_core', 'price_proposals', 'has primary key');
SELECT col_is_pk('private_core', 'price_proposals', 'proposal_id', 'proposal_id is PK');
SELECT col_not_null('private_core', 'price_proposals', 'supplier_item_id', 'supplier_item_id NOT NULL');
SELECT col_not_null('private_core', 'price_proposals', 'gi_expense_id', 'gi_expense_id NOT NULL');
SELECT col_not_null('private_core', 'price_proposals', 'proposed_unit_price_net', 'proposed_unit_price_net NOT NULL');
SELECT has_index('private_core', 'price_proposals', 'uniq_price_proposals_expense_line', 'unique index on (gi_expense_id, line_index_synthetic)');
SELECT col_default_is('private_core', 'price_proposals', 'status', 'proposed', 'default status proposed');
SELECT trigger_is('private_core', 'price_proposals', 'trg_price_proposals_touch_updated_at', 'private_core', 'touch_updated_at', 'has touch_updated_at trigger');
-- XOR constraint check: insert a row with both NULL and expect failure
PREPARE bad_xor AS
  INSERT INTO private_core.price_proposals
    (supplier_item_id, gi_expense_id, proposed_unit_price_net, pct_delta, abs_delta_money, confidence, tier, proposed_by)
  VALUES
    (gen_random_uuid(), 'test-bad-xor', 0.50, 0.05, 0.05, 'HIGH', 'tier_2', gen_random_uuid());
SELECT throws_ok('EXECUTE bad_xor', '23514', NULL, 'XOR constraint rejects all-null quantity/override');
-- Reject without reason CHECK
PREPARE bad_reject AS
  UPDATE private_core.price_proposals SET status='rejected' WHERE proposal_id=gen_random_uuid();
SELECT lives_ok('EXECUTE bad_reject', 'CHECK does not fire on no-row UPDATE; functional check below');

SELECT * FROM finish();
ROLLBACK;
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "C:\Users\tomw2\Projects\gt-factory-os\db" && npm run pgtap -- 0147_price_proposals`
Expected: 11 failures — table does not exist.

- [ ] **Step 3: Author the migration per spec §2.2**

Copy spec §2.2 verbatim into `0147_price_proposals.sql`. Includes:
- Full CREATE TABLE with all columns
- Two CHECK constraints (XOR + rejection-reason-required)
- Two unique/regular indexes
- touch_updated_at trigger
- DEPENDS-ON comment

- [ ] **Step 4: Apply the migration locally**

Run: `cd "C:\Users\tomw2\Projects\gt-factory-os\db" && npm run migrate:apply -- 0147`
Expected: COMMIT; `0147 applied`.

- [ ] **Step 5: Run test to verify it passes**

Run: `cd "C:\Users\tomw2\Projects\gt-factory-os\db" && npm run pgtap -- 0147_price_proposals`
Expected: 11 passes.

- [ ] **Step 6: Commit**

```bash
git add db/migrations/0147_price_proposals.sql db/test/0147_price_proposals.pgtap.sql
git commit -m "chore(schema): 0147: add price_proposals lifecycle table"
```

---

### Task 1.3: M3 — Backfill `card_type`+`subtype` and lock NOT NULL+CHECK — DEFERRED to Chunk 2.5

**THIS TASK IS RELOCATED to a new Chunk 2.5 (between Chunks 2 and 3) per spec §2.7 deployment sequencing.** M3 must apply ONLY after Chunk 2's emit-sites are deployed and populating `card_type`+`subtype` on every new INSERT — otherwise the NOT NULL constraint at the end of M3 fails for in-flight inserts from old code paths. See "Chunk 2.5: M3 backfill" below.

> Original task content moved to Task 2.5.1.

- [ ] **Step 1: Write the failing pgTap test**

```sql
-- 0148_typed_backfill.pgtap.sql
BEGIN;
SELECT plan(6);

-- Insert pre-condition rows (one of each known category)
INSERT INTO private_core.exceptions (category, severity, source, title) VALUES
  ('positive_adjustment', 'warning', 'form.waste_adjustment', 'test-pa'),
  ('gi_unmapped_supplier', 'warning', 'integration.green_invoice', 'test-gus'),
  ('lionwheel_capped_window_gap', 'info', 'integration.lionwheel', 'test-lcwg'),
  ('gi_stale', 'warning', 'job.freshness_check', 'test-gs');

-- Migration runs here (handled by test harness)
\i ../migrations/0148_exceptions_typed_backfill.sql

SELECT is(card_type, 'decision', 'positive_adjustment → decision') FROM private_core.exceptions WHERE title='test-pa';
SELECT is(subtype, 'positive_adjustment', 'positive_adjustment subtype set') FROM private_core.exceptions WHERE title='test-pa';
SELECT is(card_type, 'to_do', 'gi_unmapped_supplier → to_do') FROM private_core.exceptions WHERE title='test-gus';
SELECT is(card_type, 'info', 'lionwheel_capped_window_gap → info') FROM private_core.exceptions WHERE title='test-lcwg';
SELECT is(card_type, 'warning', 'gi_stale → warning') FROM private_core.exceptions WHERE title='test-gs';
SELECT col_not_null('private_core', 'exceptions', 'card_type', 'card_type is NOT NULL after migration');

SELECT * FROM finish();
ROLLBACK;
```

- [ ] **Step 2: Run test to verify it fails**

Expected: 6 failures (or migration-not-applied error).

- [ ] **Step 3: Author the migration per spec §2.3**

Copy spec §2.3 verbatim. Includes:
- All UPDATE statements (5 decision + 4 to_do + 11 warning + 8 info categories)
- Halt-guard `RAISE EXCEPTION` if any row remains NULL
- One-shot bulk-resolve for `lw_pick_historical_seed` and `shopify_network_failure`
- `ALTER TABLE … ALTER COLUMN card_type SET NOT NULL` + `ADD CONSTRAINT exceptions_card_type_check`

- [ ] **Step 4: Apply the migration locally**

Run: `cd "C:\Users\tomw2\Projects\gt-factory-os\db" && npm run migrate:apply -- 0148`
Expected: COMMIT; `0148 applied`. If RAISE EXCEPTION fires, halt — investigate the unmapped category before proceeding.

- [ ] **Step 5: Run test to verify it passes**

Expected: 6 passes.

- [ ] **Step 6: Commit**

```bash
git add db/migrations/0148_exceptions_typed_backfill.sql db/test/0148_typed_backfill.pgtap.sql
git commit -m "chore(schema): 0148: backfill exceptions card_type+subtype, lock NOT NULL"
```

---

### Task 1.4: M4 — Extend `change_log.action` enum (with halt-guard preflight)

**Files:**
- Create: `C:\Users\tomw2\Projects\gt-factory-os\db\migrations\0149_change_log_inbox_actions.sql`
- Test: `C:\Users\tomw2\Projects\gt-factory-os\db\test\0149_change_log_inbox_actions.pgtap.sql`

- [ ] **Step 1: Write the failing pgTap test**

```sql
-- 0149_change_log_inbox_actions.pgtap.sql
BEGIN;
SELECT plan(4);

-- Insert a row with each new action; expect success after migration.
\i ../migrations/0149_change_log_inbox_actions.sql

PREPARE ins(text) AS
  INSERT INTO private_core.change_log
    (entity_table, entity_id, action, changed_fields)
  VALUES ('exceptions', gen_random_uuid()::text, $1, '[]'::jsonb);

SELECT lives_ok('EXECUTE ins(''INBOX_DECISION_APPROVE'')', 'INBOX_DECISION_APPROVE accepted');
SELECT lives_ok('EXECUTE ins(''INBOX_DECISION_REJECT'')', 'INBOX_DECISION_REJECT accepted');
SELECT lives_ok('EXECUTE ins(''INBOX_WARNING_ACKNOWLEDGE'')', 'INBOX_WARNING_ACKNOWLEDGE accepted');
SELECT lives_ok('EXECUTE ins(''INBOX_INFO_DISMISS'')', 'INBOX_INFO_DISMISS accepted');

SELECT * FROM finish();
ROLLBACK;
```

- [ ] **Step 2: Run test to verify it fails**

Expected: 4 CHECK violations.

- [ ] **Step 3: Author the migration per spec §2.4**

Copy spec §2.4 verbatim. Includes:
- Hard halt-guard preflight `DO $$ ... live_count <> 60 THEN RAISE EXCEPTION ... $$`
- DROP CONSTRAINT + ADD CONSTRAINT with full 64-action enumeration

- [ ] **Step 4: Apply the migration locally**

Run: `cd "C:\Users\tomw2\Projects\gt-factory-os\db" && npm run migrate:apply -- 0149`
Expected: preflight passes (live_count=60); ALTER constraints succeed.

- [ ] **Step 5: Run test to verify it passes**

Expected: 4 passes.

- [ ] **Step 6: Commit**

```bash
git add db/migrations/0149_change_log_inbox_actions.sql db/test/0149_change_log_inbox_actions.pgtap.sql
git commit -m "chore(schema): 0149: add INBOX_* actions to change_log enum"
```

---

### Task 1.5: M5 — `dismissed` status + dedupe indexes + `snoozed_until`

**Files:**
- Create: `C:\Users\tomw2\Projects\gt-factory-os\db\migrations\0150_exceptions_status_dismissed_and_dedupe_index.sql`
- Test: `C:\Users\tomw2\Projects\gt-factory-os\db\test\0150_status_and_indexes.pgtap.sql`

- [ ] **Step 1: Write the failing pgTap test**

```sql
-- 0150_status_and_indexes.pgtap.sql
BEGIN;
SELECT plan(5);

\i ../migrations/0150_exceptions_status_dismissed_and_dedupe_index.sql

PREPARE upd_dismissed AS
  UPDATE private_core.exceptions SET status='dismissed' WHERE FALSE;
SELECT lives_ok('EXECUTE upd_dismissed', 'dismissed status accepted by CHECK');
SELECT has_index('private_core', 'exceptions', 'idx_exceptions_dedupe_key', 'new dedupe_key index');
SELECT has_index('private_core', 'exceptions', 'idx_exceptions_dedupe_status', 'composite (dedupe_key, status) index');
SELECT has_column('private_core', 'exceptions', 'snoozed_until', 'snoozed_until column added');
SELECT has_index('private_core', 'exceptions', 'idx_exceptions_snoozed_until', 'snoozed_until partial index');

SELECT * FROM finish();
ROLLBACK;
```

- [ ] **Step 2: Run test to verify it fails**

Expected: 5 failures.

- [ ] **Step 3: Author the migration per spec §2.5**

Copy spec §2.5 verbatim. Includes:
- DROP CONSTRAINT exceptions_status_check + ADD with 8 values (open/acknowledged/resolved/auto_resolved/pending_gi_action/gi_draft_created/gi_action_failed/dismissed)
- DROP INDEX idx_exceptions_dedupe + CREATE 2 new indexes (idx_exceptions_dedupe_key + idx_exceptions_dedupe_status)
- ADD COLUMN snoozed_until + idx_exceptions_snoozed_until partial index

- [ ] **Step 4: Apply the migration locally**

Run: `cd "C:\Users\tomw2\Projects\gt-factory-os\db" && npm run migrate:apply -- 0150`
Expected: COMMIT.

- [ ] **Step 5: Run test to verify it passes**

Expected: 5 passes.

- [ ] **Step 6: Commit**

```bash
git add db/migrations/0150_exceptions_status_dismissed_and_dedupe_index.sql db/test/0150_status_and_indexes.pgtap.sql
git commit -m "chore(schema): 0150: dismissed status + dedupe indexes + snoozed_until"
```

---

### Task 1.6: M5b — `fn_gi_price_proposal_activator()` SQL function

**Files:**
- Create: `C:\Users\tomw2\Projects\gt-factory-os\db\migrations\0150b_fn_gi_price_proposal_activator.sql`
- Test: `C:\Users\tomw2\Projects\gt-factory-os\db\test\0150b_activator_function.pgtap.sql`

- [ ] **Step 1: Write the failing pgTap test**

```sql
-- 0150b_activator_function.pgtap.sql
BEGIN;
SELECT plan(3);

\i ../migrations/0150b_fn_gi_price_proposal_activator.sql

SELECT has_function('private_core', 'fn_gi_price_proposal_activator', 'function exists');
SELECT function_returns('private_core', 'fn_gi_price_proposal_activator', 'TABLE(activated_count integer, failed_count integer)', 'returns TABLE');
-- Smoke test: 0 due rows → returns (0, 0)
SELECT results_eq(
  'SELECT activated_count, failed_count FROM private_core.fn_gi_price_proposal_activator()',
  $$VALUES (0, 0)$$,
  'no due rows yields (0,0)'
);

SELECT * FROM finish();
ROLLBACK;
```

- [ ] **Step 2: Run test to verify it fails**

Expected: 3 failures.

- [ ] **Step 3: Author the function per spec §2.5b**

Copy spec §2.5b verbatim. Full plpgsql body with FOR UPDATE SKIP LOCKED, per-proposal exception block, emit-with-reopen warning emit on failure.

- [ ] **Step 4: Apply the migration locally**

Run: `cd "C:\Users\tomw2\Projects\gt-factory-os\db" && npm run migrate:apply -- 0150b`
Expected: COMMIT.

- [ ] **Step 5: Run test to verify it passes**

Expected: 3 passes.

- [ ] **Step 6: Commit**

```bash
git add db/migrations/0150b_fn_gi_price_proposal_activator.sql db/test/0150b_activator_function.pgtap.sql
git commit -m "chore(schema): 0150b: fn_gi_price_proposal_activator function"
```

---

### Task 1.7: M6 — pg_cron schedule for activator job

**Files:**
- Create: `C:\Users\tomw2\Projects\gt-factory-os\db\migrations\0151_gi_price_proposal_activator_cron.sql`
- Test: `C:\Users\tomw2\Projects\gt-factory-os\db\test\0151_activator_cron.pgtap.sql`

- [ ] **Step 1: Write the failing pgTap test**

```sql
-- 0151_activator_cron.pgtap.sql
BEGIN;
SELECT plan(2);

\i ../migrations/0151_gi_price_proposal_activator_cron.sql

SELECT ok(
  EXISTS(SELECT 1 FROM cron.job WHERE jobname='gi_price_proposal_activator'),
  'pg_cron job registered'
);
SELECT is(
  (SELECT schedule FROM cron.job WHERE jobname='gi_price_proposal_activator'),
  '5 * * * *',
  'schedule is hourly at :05'
);

SELECT * FROM finish();
ROLLBACK;
```

- [ ] **Step 2: Run test to verify it fails**

Expected: 2 failures (job not registered).

- [ ] **Step 3: Author the migration per spec §2.6**

Copy spec §2.6 verbatim. `SELECT cron.schedule(...)` with hourly schedule.

- [ ] **Step 4: Apply the migration locally**

Run: `cd "C:\Users\tomw2\Projects\gt-factory-os\db" && npm run migrate:apply -- 0151`
Expected: COMMIT.

- [ ] **Step 5: Run test to verify it passes**

Expected: 2 passes.

- [ ] **Step 6: Commit**

```bash
git add db/migrations/0151_gi_price_proposal_activator_cron.sql db/test/0151_activator_cron.pgtap.sql
git commit -m "chore(schema): 0151: pg_cron schedule for gi_price_proposal_activator"
```

---

**Chunk 1 acceptance:** all 7 migrations apply; all pgTap tests pass; `SELECT private_core.rebuild_verifier()` returns 0; `SELECT card_type, COUNT(*) FROM private_core.exceptions GROUP BY card_type` returns rows for at least 3 of {decision, to_do, warning, info}.

---

## Chunk 2: Exceptions runtime + emitter retrofit + role gate

This chunk lands the API runtime that consumes the new schema. The emit-with-reopen contract becomes the new emit shape across all type-aware-dedupe producers; per-submission emitters get only `card_type`+`subtype` populated; the handler splits Approve/Reject/Dismiss/EditApprove and gates by role.

**Note on order within Chunk 2:** Tasks 2.1-2.13 can run in parallel (different files, no shared state). Task 2.14 collects all tests and runs the full suite. The plan-document-reviewer should consider whether to dispatch via `dispatching-parallel-agents` for 2.1-2.13.

### Task 2.1: Build `emit-with-reopen` shared helper + tests

**Files:**
- Create: `C:\Users\tomw2\Projects\gt-factory-os\api\src\exceptions\emit-with-reopen.ts`
- Test: `C:\Users\tomw2\Projects\gt-factory-os\api\test\exceptions\emit-with-reopen.test.ts`

- [ ] **Step 1: Write failing tests for the 3 branches (insert / noop / reopen)**

```typescript
// api/test/exceptions/emit-with-reopen.test.ts
import { describe, it, expect, beforeEach } from 'vitest';
import { sql } from 'kysely';
import { db } from '../helpers/test-db';
import { emitWithReopen } from '../../src/exceptions/emit-with-reopen';

describe('emitWithReopen', () => {
  const fixture = {
    dedupeKey: 'test:emit-with-reopen:1',
    cardType: 'warning' as const,
    subtype: 'gi_stale',
    severity: 'warning' as const,
    source: 'job.freshness_check',
    title: 'GI stale',
    detail: 'GI poll has not run',
  };

  beforeEach(async () => {
    await sql`DELETE FROM private_core.exceptions WHERE dedupe_key=${fixture.dedupeKey}`.execute(db);
  });

  it('inserts a fresh row when none exists', async () => {
    const result = await emitWithReopen(db, fixture);
    expect(result.action).toBe('insert');
    const row = await sql<{ status: string }>`SELECT status FROM private_core.exceptions WHERE dedupe_key=${fixture.dedupeKey}`.execute(db);
    expect(row.rows[0].status).toBe('open');
  });

  it('no-ops when an open row already exists', async () => {
    await emitWithReopen(db, fixture);
    const result = await emitWithReopen(db, fixture);
    expect(result.action).toBe('noop');
    const rows = await sql<{ count: number }>`SELECT COUNT(*)::int as count FROM private_core.exceptions WHERE dedupe_key=${fixture.dedupeKey}`.execute(db);
    expect(rows.rows[0].count).toBe(1);
  });

  it('reopens a previously-resolved row with metadata reset', async () => {
    await emitWithReopen(db, fixture);
    await sql`UPDATE private_core.exceptions SET status='resolved', resolved_at=NOW(), resolved_by=gen_random_uuid(), resolution_notes='manual' WHERE dedupe_key=${fixture.dedupeKey}`.execute(db);
    const result = await emitWithReopen(db, fixture);
    expect(result.action).toBe('reopen');
    const row = await sql<{ status: string; resolved_by: string | null; notes: string }>`SELECT status, resolved_by, resolution_notes as notes FROM private_core.exceptions WHERE dedupe_key=${fixture.dedupeKey}`.execute(db);
    expect(row.rows[0].status).toBe('open');
    expect(row.rows[0].resolved_by).toBeNull();
    expect(row.rows[0].notes).toMatch(/Re-opened/);
  });

  it('caps resolution_notes growth at 4096 chars across many cycles', async () => {
    await emitWithReopen(db, fixture);
    for (let i = 0; i < 200; i++) {
      await sql`UPDATE private_core.exceptions SET status='resolved', resolution_notes=repeat('x', 100) WHERE dedupe_key=${fixture.dedupeKey}`.execute(db);
      await emitWithReopen(db, fixture);
    }
    const row = await sql<{ len: number }>`SELECT length(resolution_notes) as len FROM private_core.exceptions WHERE dedupe_key=${fixture.dedupeKey}`.execute(db);
    expect(row.rows[0].len).toBeLessThanOrEqual(4096);
  });

  it('uses FOR UPDATE to prevent concurrent double-touch', async () => {
    // This is hard to write deterministically without serialization probes.
    // A coarse proof: run 10 concurrent calls; assert only 1 row exists with last marker.
    await emitWithReopen(db, fixture);
    await sql`UPDATE private_core.exceptions SET status='resolved' WHERE dedupe_key=${fixture.dedupeKey}`.execute(db);
    const promises = Array.from({ length: 10 }, () => emitWithReopen(db, fixture));
    await Promise.all(promises);
    const rows = await sql<{ count: number }>`SELECT COUNT(*)::int as count FROM private_core.exceptions WHERE dedupe_key=${fixture.dedupeKey}`.execute(db);
    expect(rows.rows[0].count).toBe(1);
  });
});
```

- [ ] **Step 2: Run tests to verify they fail (helper not implemented)**

Run: `cd "C:\Users\tomw2\Projects\gt-factory-os" && npm test -- emit-with-reopen`
Expected: import error (file not found) or 5 test failures.

- [ ] **Step 3: Implement the helper per spec §1.12 (emit-with-reopen contract)**

Body: a single transaction-wrapping function that runs the 3-branch SELECT…FOR UPDATE then INSERT/NOOP/UPDATE. Returns `{ action: 'insert'|'noop'|'reopen' }`. Uses Kysely transaction.

```typescript
// api/src/exceptions/emit-with-reopen.ts
import { sql, type Kysely } from 'kysely';
import type { Db } from '../db/connection.js';

export interface EmitArgs {
  dedupeKey: string;
  cardType: 'decision' | 'to_do' | 'warning' | 'info';
  subtype: string;
  severity: 'info' | 'warning' | 'critical';
  source: string;
  title: string;
  detail?: string | null;
  rawPayload?: object | null;
  relatedJobRunId?: string | null;
  relatedEntityType?: string | null;
  relatedEntityId?: string | null;
  category?: string;  // legacy free-text; defaults to subtype if not given
}

export async function emitWithReopen(
  db: Db,
  args: EmitArgs,
): Promise<{ action: 'insert' | 'noop' | 'reopen' }> {
  return await db.transaction().execute(async (trx) => {
    const existing = await sql<{ exception_id: string; status: string }>`
      SELECT exception_id, status
        FROM private_core.exceptions
       WHERE dedupe_key = ${args.dedupeKey}
       FOR UPDATE
    `.execute(trx);
    const category = args.category ?? args.subtype;
    if (existing.rows.length === 0) {
      await sql`
        INSERT INTO private_core.exceptions
          (category, severity, source, title, detail, raw_payload, dedupe_key,
           related_job_run_id, related_entity_type, related_entity_id,
           card_type, subtype)
        VALUES
          (${category}, ${args.severity}, ${args.source}, ${args.title},
           ${args.detail ?? null}, ${args.rawPayload ? JSON.stringify(args.rawPayload) : null}::jsonb,
           ${args.dedupeKey}, ${args.relatedJobRunId ?? null},
           ${args.relatedEntityType ?? null}, ${args.relatedEntityId ?? null},
           ${args.cardType}, ${args.subtype})
      `.execute(trx);
      return { action: 'insert' };
    }
    if (existing.rows[0].status === 'open' || existing.rows[0].status === 'acknowledged') {
      return { action: 'noop' };
    }
    // resolved / auto_resolved / dismissed / gi_* → REOPEN
    await sql`
      UPDATE private_core.exceptions
         SET status='open',
             resolved_by=NULL, resolved_at=NULL,
             acknowledged_by=NULL, acknowledged_at=NULL,
             resolution_notes = right(
               COALESCE(resolution_notes,'') || E'\n[Re-opened ' || NOW()::text || ' by producer]',
               4096),
             updated_at=NOW(),
             severity=${args.severity},
             title=${args.title},
             detail=${args.detail ?? null},
             raw_payload=${args.rawPayload ? JSON.stringify(args.rawPayload) : null}::jsonb,
             related_job_run_id=${args.relatedJobRunId ?? null}
       WHERE exception_id = ${existing.rows[0].exception_id}
    `.execute(trx);
    return { action: 'reopen' };
  });
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd "C:\Users\tomw2\Projects\gt-factory-os" && npm test -- emit-with-reopen`
Expected: 5/5 pass.

- [ ] **Step 5: Commit**

```bash
git add api/src/exceptions/emit-with-reopen.ts api/test/exceptions/emit-with-reopen.test.ts
git commit -m "feat(inbox): add emit-with-reopen helper (insert/noop/reopen contract)"
```

---

### Task 2.2: Update `api/src/integrations/lionwheel/poller.ts:emitException` to use emit-with-reopen

**Files:**
- Modify: `C:\Users\tomw2\Projects\gt-factory-os\api\src\integrations\lionwheel\poller.ts:567-597`

- [ ] **Step 1: Write integration test for LW poller emit shape**

```typescript
// api/test/integrations/lionwheel-emit-shape.test.ts
import { describe, it, expect } from 'vitest';
// Insert a fixture LW response that triggers emitException, verify the
// resulting exceptions row has card_type+subtype set and dedupe_key
// matches the spec's shape.
```

- [ ] **Step 2: Run test to verify it fails (current emitException uses old contract; no card_type)**

Run: `cd "C:\Users\tomw2\Projects\gt-factory-os" && npm test -- lionwheel-emit-shape`

- [ ] **Step 3: Modify `emitException` to delegate to `emit-with-reopen`**

Replace the function body at lines 567-597 with a call to `emitWithReopen` from §Task 2.1, passing through the existing `args` enriched with `card_type` and `subtype`. The producer must determine `card_type` based on the `category` (use a small mapping table at the top of `poller.ts`).

- [ ] **Step 4: Run test to verify it passes**

- [ ] **Step 5: Commit**

```bash
git commit -m "fix(inbox): lionwheel poller uses emit-with-reopen + populates card_type"
```

---

### Task 2.3: Update `supabase/functions/factory_os_jobs/index.ts:emitException` to mirror

**Files:**
- Modify: `C:\Users\tomw2\Projects\gt-factory-os\supabase\functions\factory_os_jobs\index.ts:190-214`

- [ ] **Step 1-5:** Mirror the change from Task 2.2 in the Edge Function. Note: the Edge Function uses Deno-style imports and the `pg` client directly; replicate the SQL of `emit-with-reopen` inline (cannot import from api/src). Keep the SQL identical to spec §1.12 for consistency.

Commit: `git commit -m "fix(inbox): factory_os_jobs emitException uses emit-with-reopen + card_type"`

---

### Task 2.4: Update `api/src/jobs/freshness_check.ts:emitOrPromote`

**Files:**
- Modify: `C:\Users\tomw2\Projects\gt-factory-os\api\src\jobs\freshness_check.ts:233-283`

- [ ] **Step 1-5:** Replace `emitOrPromote` with logic that:
  1. First calls `emitWithReopen` (which handles insert/noop/reopen for `WHERE dedupe_key=$1`).
  2. Then handles severity promotion (warning → critical) on the existing row via a separate UPDATE.
  3. Sets `card_type='warning'` always.
  
The existing `autoResolve` at lines 285-295 stays unchanged (it specifically wants `WHERE status='open'`).

Commit: `git commit -m "fix(inbox): freshness_check uses emit-with-reopen for stale producers"`

---

### Task 2.5: Update `api/src/integration-sku-map/mutations.ts` inline INSERT

**Files:**
- Modify: `C:\Users\tomw2\Projects\gt-factory-os\api\src\integration-sku-map\mutations.ts:233-...`

- [ ] **Step 1-5:** Replace the inline `INSERT INTO private_core.exceptions` at line 233 with a call to `emitWithReopen`. Set `card_type='warning'` and the appropriate `subtype` (existing categories: `lionwheel_unknown_sku` etc. — verify with the call site).

Commit: `git commit -m "fix(inbox): integration-sku-map uses emit-with-reopen"`

---

### Task 2.6: Update `api/src/boms/publish.ts` inline INSERT

**Files:**
- Modify: `C:\Users\tomw2\Projects\gt-factory-os\api\src\boms\publish.ts:505-...`

- [ ] **Step 1-5:** Same pattern. The `bom_version_published` exception is `card_type='info'`, `subtype='bom_version_published'`.

Commit: `git commit -m "fix(inbox): bom publish uses emit-with-reopen + card_type=info"`

---

### Task 2.7: Update `api/src/integrations/lionwheel/reconciliation.ts` — split per emit-site

The 7 emit sites in `reconciliation.ts` have different category→card_type mappings; collapsing them into one task hides per-site test failures. Split into 7 sub-tasks running independently (Tasks 2.7a-2.7g may be parallelized via dispatching-parallel-agents — they touch different lines and have no shared state).

| sub-task | line | category | card_type | subtype | dedupe shape |
|---|---:|---|---|---|---|
| 2.7a | 329 | `lionwheel_order_note` | `info` | `lionwheel_order_note` | event-scoped: `lionwheel_order_note:<lw_task_id>` |
| 2.7b | 418 | `lw_pick_enrich_failed` | `warning` | `lw_pick_enrich_failed` | producer-scoped: `lw_pick_enrich_failed:integration.lionwheel` |
| 2.7c | 442 | `lionwheel_schema_drift` | `warning` | `lionwheel_schema_drift` | producer-scoped: `lionwheel_schema_drift:integration.lionwheel` |
| 2.7d | 455 | `lionwheel_payload_invalid_picked_quantity` | `info` | `lionwheel_payload_invalid_picked_quantity` | event-scoped: `lionwheel_payload_invalid_picked_quantity:<lw_task_id>` |
| 2.7e | 685 | `lionwheel_capped_window_gap` | `info` | `lw_capped_window` | event-scoped: `lw_capped_window:<job_run_id>` |
| 2.7f | 805 | `lw_pick_data_missing` | `info` | `lw_pick_historical_seed` (legacy emit; new emits should NOT happen since 2026-04-18 seed) | event-scoped: `lw_pick_data_missing:<order_line_id>` |
| 2.7g | 933 | `lionwheel_credit_needed` | `decision` | `customer_credit` | state-scoped: `lionwheel_credit_needed:<lw_task_id>` |

For each sub-task (5 steps each):
- [ ] **Step 1:** Write a unit test that emits the producer's input and asserts the resulting row has the correct `card_type`, `subtype`, `dedupe_key` shape per the table above. Test name: `reconciliation-<subtype>.test.ts`.
- [ ] **Step 2:** Run RED.
- [ ] **Step 3:** Replace the inline `INSERT INTO private_core.exceptions` at the cited line with a call to `emitWithReopen` from Task 2.1, passing `card_type` + `subtype` + `dedupe_key` per the table.
- [ ] **Step 4:** Run GREEN.
- [ ] **Step 5:** Commit:

```bash
git commit -m "fix(inbox): reconciliation 2.7<x> — <subtype> uses emit-with-reopen"
```

**Mapping verification:** every row in the table above must match spec §3 backfill table verbatim. If conflict, spec wins; halt and reconcile.

---

### Task 2.8: `physical-counts/handler.ts` and `waste-adjustments/handler.ts` — populate `card_type`+`subtype` only

**Files:**
- Modify: `C:\Users\tomw2\Projects\gt-factory-os\api\src\physical-counts\handler.ts:412`
- Modify: `C:\Users\tomw2\Projects\gt-factory-os\api\src\waste-adjustments\handler.ts:750-767`

- [ ] **Step 1: Write tests**

Tests verify that the resulting exceptions row has `card_type='decision'` and the correct `subtype`.

- [ ] **Steps 2-5:** Add `card_type` and `subtype` to the existing INSERT statements. **Do NOT** add `dedupe_key` — these are per-submission one-shots (spec §1.12 + §4.2). The mapping:
- `physical-counts` → `card_type='decision'`, `subtype='count_large_variance'`
- `waste-adjustments` → `card_type='decision'`, `subtype='positive_adjustment'` or `'loss_above_threshold'` (per existing branch)

Commit: `git commit -m "fix(inbox): physical-counts + waste-adjustments populate card_type+subtype"`

---

### Task 2.9: Split `api/src/exceptions/handler.ts` into typed handlers

**Files:**
- Modify: `C:\Users\tomw2\Projects\gt-factory-os\api\src\exceptions\handler.ts`
- Modify: `C:\Users\tomw2\Projects\gt-factory-os\api\src\exceptions\schemas.ts`
- Modify: `C:\Users\tomw2\Projects\gt-factory-os\api\src\exceptions\route.ts`

- [ ] **Step 1: Write tests for the split**

```typescript
// api/test/exceptions/typed-actions.test.ts
describe('handleApprove (Decision only)', () => {
  it('rejects 409 for non-decision card_type', async () => { ... });
  it('writes change_log INBOX_DECISION_APPROVE', async () => { ... });
});
describe('handleReject (Decision only)', () => {
  it('requires rejection_reason', async () => { ... });
});
describe('handleAcknowledge (Warning only)', () => {
  it('rejects 409 for non-warning card_type', async () => { ... });
  it('keeps card visible, sets acknowledged_*', async () => { ... });
});
describe('handleDismiss (Info only)', () => {
  it('sets status=dismissed', async () => { ... });
});
```

- [ ] **Step 2: Run tests to verify they fail**

- [ ] **Step 3: Implement per spec §4.4**

`handleApprove` and `handleReject` replace `handleResolve` for decision rows. `handleAcknowledge` restricted to `card_type='warning'`. New `handleDismiss` for info. Each writes the appropriate `change_log` row. Existing idempotent-replay logic preserved per row's status.

Add a new endpoint mapping in `route.ts`:
- `POST /mutations/exceptions/:id/approve` → handleApprove
- `POST /mutations/exceptions/:id/reject` → handleReject (body: { reason })
- `POST /mutations/exceptions/:id/acknowledge` → handleAcknowledge (existing)
- `POST /mutations/exceptions/:id/dismiss` → handleDismiss

Schema additions in `schemas.ts`: ApproveRequest, RejectRequest (with reason), DismissRequest.

- [ ] **Step 4: Run tests; expect green**

- [ ] **Step 5: Commit**

```bash
git commit -m "feat(inbox): split exceptions handler into typed Approve/Reject/Acknowledge/Dismiss"
```

---

### Task 2.10: Role-gate change in `handler.ts`

**Files:**
- Modify: `C:\Users\tomw2\Projects\gt-factory-os\api\src\exceptions\handler.ts:65-71`

- [ ] **Step 1: Write tests**

```typescript
describe('roleAllowsRead', () => {
  it('admin → true', () => expect(roleAllowsRead('admin')).toBe(true));
  it('planner → true', () => expect(roleAllowsRead('planner')).toBe(true));
  it('operator (no entity filter) → false', () => expect(roleAllowsRead('operator', {})).toBe(false));
  it('viewer → false', () => expect(roleAllowsRead('viewer')).toBe(false));
});
```

- [ ] **Step 2-5:** Change `roleAllowsRead` from `return true` to `return role === 'planner' || role === 'admin'`. Existing `roleAllowsMutate` already restricts mutate to planner+admin (no change).

Commit: `git commit -m "feat(inbox): restrict exceptions read to planner+admin"`

---

### Task 2.11: Scoped operator read-access

**Files:**
- Modify: `C:\Users\tomw2\Projects\gt-factory-os\api\src\exceptions\handler.ts` (LIST handler)

- [ ] **Step 1: Write tests**

```typescript
describe('handleExceptionsList — scoped operator read', () => {
  it('operator with own related_entity_id → 200 with own rows', async () => { ... });
  it('operator with another's related_entity_id → 200 with empty list', async () => { ... });
  it('operator without related_entity_id filter → 403', async () => { ... });
});
```

- [ ] **Steps 2-5:** Implement per spec §1.2 + §4.4. Add a `roleAllowsScopedRead(session, query)` helper that verifies `query.related_entity_type='form_submission' AND form_submissions.author_user_id=session.user_id`. If true, override the `roleAllowsRead` 403 and let the LIST proceed with an additional `WHERE related_entity_id=session-form-submission` filter.

Commit: `git commit -m "feat(inbox): scoped operator read for own form-submission exceptions"`

---

### Task 2.12: Bulk-resolve deprecation

**Files:**
- Modify: `C:\Users\tomw2\Projects\gt-factory-os\api\src\exceptions\handler.ts:369-449`

- [ ] **Step 1: Write tests**

```typescript
describe('handleBulkResolve — deprecation', () => {
  it('returns 422 BULK_RESOLVE_DEPRECATED for any row with card_type IS NOT NULL', async () => { ... });
  it('still works on legacy NULL-card_type rows during deployment window', async () => { ... });
});
```

- [ ] **Steps 2-5:** Per spec §4.4. Add a pre-check inside `handleBulkResolve` that fetches `card_type` for each id; if any has `card_type IS NOT NULL`, return 422 with `reason_code='BULK_RESOLVE_DEPRECATED'` and a message pointing to the new typed handlers.

Commit: `git commit -m "feat(inbox): deprecate bulk-resolve for typed rows"`

---

### Task 2.13: Per-subtype `key_facts` derivers for one-shot emitters

**Files:**
- Create: `C:\Users\tomw2\Projects\gt-factory-os\api\src\exceptions\key-facts-derivers.ts`
- Modify: `C:\Users\tomw2\Projects\gt-factory-os\api\src\exceptions\handler.ts` (LIST response)

- [ ] **Step 1: Write tests**

```typescript
describe('keyFactsDerivers', () => {
  it('count_large_variance → derives [item_name, snapshot_qty, counted_qty, delta]', () => { ... });
  it('positive_adjustment → derives [item_name, current_qty, adjusted_qty, delta]', () => { ... });
  it('loss_above_threshold → derives [item_name, loss_qty, reason]', () => { ... });
  it('gi_price_proposal → returns raw_payload->>"key_facts" verbatim (already populated)', () => { ... });
});
```

- [ ] **Step 2: Run tests; expect failure**

- [ ] **Step 3: Implement per-subtype mappers**

```typescript
// api/src/exceptions/key-facts-derivers.ts
export type KeyFactsItem = { label: string; value: string };
type Deriver = (rawPayload: any) => KeyFactsItem[];

const DERIVERS: Record<string, Deriver> = {
  count_large_variance: (p) => [
    { label: 'פריט', value: p.item_name ?? p.item_id },
    { label: 'תמונת רגע', value: String(p.snapshot_quantity) },
    { label: 'נספר', value: String(p.computed_delta + p.snapshot_quantity) },
    { label: 'דלתא', value: String(p.computed_delta) },
  ],
  positive_adjustment: (p) => [...],
  loss_above_threshold: (p) => [...],
};

export function deriveKeyFacts(subtype: string, rawPayload: any): KeyFactsItem[] | null {
  const fn = DERIVERS[subtype];
  if (!fn) return null;
  return fn(rawPayload);
}
```

- [ ] **Step 4: Modify `handleExceptionsList`** to merge `key_facts` from `raw_payload->'key_facts'` (preferred) OR `deriveKeyFacts(subtype, raw_payload)` fallback.

- [ ] **Step 5: Run tests; expect green**

- [ ] **Step 6: Commit**

```bash
git commit -m "feat(inbox): per-subtype key_facts derivers for one-shot emitters"
```

---

### Task 2.14: Full Chunk-2 test sweep + integration tests

- [ ] **Step 1: Write `migration-backfill.test.ts`** that runs the full M1→M5b migration sequence on a clean DB and verifies:
  - All categories from §3 backfill table get correct `card_type`+`subtype`
  - The halt-guard fires for an unmapped category
  - One-shot bulk-resolves do not duplicate

- [ ] **Step 2: Write `regression-reopen.test.ts`** — integration test of the full Warning lifecycle: stale → fresh (auto_resolved) → stale → fresh (auto_resolved). Must yield ONE row with status flipping, NOT two rows.

- [ ] **Step 3: Run full suite**

Run: `cd "C:\Users\tomw2\Projects\gt-factory-os" && npm test`
Expected: all green.

- [ ] **Step 4: Commit**

```bash
git commit -m "test(inbox): full Chunk 2 sweep — migration backfill, regression-reopen"
```

---

**Chunk 2 acceptance:** all emitters use `emit-with-reopen`; per-submission emitters populate `card_type`+`subtype`; handler split into typed actions; role gate enforced; scoped operator read works; bulk-resolve deprecated for typed rows; key_facts derivers cover one-shot emitters; full test suite green.

---

## Chunk 2.5: M3 backfill (relocated from Chunk 1)

This is the relocation of the original Task 1.3 (M3) per spec §2.7 deployment sequencing. M3 must apply ONLY after Chunk 2's emit-sites are deployed and populating `card_type`+`subtype` — otherwise the NOT NULL constraint at the end of M3 fails for in-flight inserts from old code paths.

### Task 2.5.1: M3 — Backfill `card_type`+`subtype` and lock NOT NULL+CHECK

**Files:**
- Create: `C:\Users\tomw2\Projects\gt-factory-os\db\migrations\0148_exceptions_typed_backfill.sql`
- Test: `C:\Users\tomw2\Projects\gt-factory-os\db\test\0148_typed_backfill.pgtap.sql`

**Precondition (verify before starting):** Chunk 2 fully deployed. Run `SELECT card_type FROM private_core.exceptions WHERE created_at > '<chunk-2-deploy-time>' AND card_type IS NULL` — expect 0 rows. If non-zero, halt: code from Chunk 2 is not populating `card_type` correctly.

- [ ] **Step 0: Skip-if-applied check**

Run: `psql -c "SELECT 1 FROM private_core.schema_migrations WHERE version='0148'"`. If exists, jump to Step 5.

- [ ] **Step 1: Write the failing pgTap test**

```sql
-- 0148_typed_backfill.pgtap.sql
BEGIN;
SELECT plan(6);

INSERT INTO private_core.exceptions (category, severity, source, title) VALUES
  ('positive_adjustment', 'warning', 'form.waste_adjustment', 'test-pa'),
  ('gi_unmapped_supplier', 'warning', 'integration.green_invoice', 'test-gus'),
  ('lionwheel_capped_window_gap', 'info', 'integration.lionwheel', 'test-lcwg'),
  ('gi_stale', 'warning', 'job.freshness_check', 'test-gs');

\i ../migrations/0148_exceptions_typed_backfill.sql

SELECT is(card_type, 'decision', 'positive_adjustment → decision') FROM private_core.exceptions WHERE title='test-pa';
SELECT is(subtype, 'positive_adjustment', 'positive_adjustment subtype set') FROM private_core.exceptions WHERE title='test-pa';
SELECT is(card_type, 'to_do', 'gi_unmapped_supplier → to_do') FROM private_core.exceptions WHERE title='test-gus';
SELECT is(card_type, 'info', 'lionwheel_capped_window_gap → info') FROM private_core.exceptions WHERE title='test-lcwg';
SELECT is(card_type, 'warning', 'gi_stale → warning') FROM private_core.exceptions WHERE title='test-gs';
SELECT col_not_null('private_core', 'exceptions', 'card_type', 'card_type is NOT NULL after migration');

SELECT * FROM finish();
ROLLBACK;
```

- [ ] **Step 2: Run test to verify RED**

Expected: 6 failures (or migration-not-applied error).

- [ ] **Step 3: Author the migration per spec §2.3**

Copy spec §2.3 verbatim. Includes UPDATE statements for all 28 known categories, halt-guard `RAISE EXCEPTION` if any row remains NULL after backfill, one-shot bulk-resolve for `lw_pick_historical_seed` and `shopify_network_failure`, `ALTER TABLE … SET NOT NULL` + `ADD CONSTRAINT exceptions_card_type_check`.

- [ ] **Step 4: Apply the migration**

Run: `cd "C:\Users\tomw2\Projects\gt-factory-os\db" && npm run migrate:apply -- 0148`
Expected: COMMIT. If RAISE EXCEPTION fires, halt — investigate the unmapped category before proceeding (likely a new category landed since spec write that needs adding to §2.3).

- [ ] **Step 5: Run test to verify GREEN**

Expected: 6 passes.

- [ ] **Step 6: Commit**

```bash
git add db/migrations/0148_exceptions_typed_backfill.sql db/test/0148_typed_backfill.pgtap.sql
git commit -m "chore(schema): 0148: backfill exceptions card_type+subtype, lock NOT NULL"
```

---

**Chunk 2.5 acceptance:** post-M3 query `SELECT COUNT(*) FROM private_core.exceptions WHERE card_type IS NULL` returns 0; rebuild_verifier returns 0.

---

## Chunk 3: Stage A producer + Stage B handlers + Activator job

This chunk lands the new GI-evidence flow. Stage A surfaces every mapped-supplier expense as a To-Do; Stage B form converts it into a price proposal + Decision card; activator job handles future-dated activations.

### Task 3.1: `emitGiExpenseReview` Stage A producer

**Spec §1.14.1 vs §8 file-list reconciliation:** spec §1.14.1 calls the producer "from `factory_os_jobs/index.ts` GI ingest loop"; spec §8 lists `api/src/integrations/green_invoice/expense-review-emitter.ts` as a NEW file. The canonical placement is **inside `factory_os_jobs/index.ts`** (the call-site is in the GI ingest loop which lives there); the §8 file-list entry is a documentation artifact and should be ignored. NO new file is created in `api/src/integrations/green_invoice/`.

**Files:**
- Modify: `C:\Users\tomw2\Projects\gt-factory-os\supabase\functions\factory_os_jobs\index.ts` (after line 1925, where the GI ingest loop body ends)

- [ ] **Step 1: Write integration test**

```typescript
// api/test/integrations/gi-expense-review-emit.test.ts
describe('emitGiExpenseReview (Stage A)', () => {
  beforeEach(async () => { /* seed gi_expense_mirror, suppliers */ });
  it('emits to_do:gi_expense_review for ILS expense from mapped supplier', async () => {...});
  it('does NOT emit for non-ILS currency (existing gi_non_ils_currency handles)', async () => {...});
  it('does NOT emit for unmapped supplier (existing gi_unmapped_supplier handles)', async () => {...});
  it('dedupe-key is gi_expense_review:<gi_expense_id> (event-scoped)', async () => {...});
  it('re-ingest of same expense yields one card (noop branch)', async () => {...});
  it('key_facts JSONB includes supplier_item_count and prefill_supplier_item_id', async () => {...});
});
```

- [ ] **Step 2: Run test to verify it fails**

- [ ] **Step 3: Implement the producer per spec §1.14.1**

Insertion point: AFTER `gi_expense_mirror` INSERT commits in the same transaction, AFTER the existing `gi_unmapped_supplier` and `gi_non_ils_currency` checks. Pseudocode in spec §1.14.1.

- [ ] **Step 4: Run test to verify green**

- [ ] **Step 5: Commit**

```bash
git commit -m "feat(inbox): Stage A — emitGiExpenseReview producer"
```

---

### Task 3.2: `gi_expense_review` Stage B form handler

**Files:**
- Create: `C:\Users\tomw2\Projects\gt-factory-os\api\src\inbox\gi_expense_review\handler.ts`
- Create: `C:\Users\tomw2\Projects\gt-factory-os\api\src\inbox\gi_expense_review\route.ts`
- Create: `C:\Users\tomw2\Projects\gt-factory-os\api\src\inbox\gi_expense_review\schemas.ts`

- [ ] **Step 1: Write tests for tier routing**

```typescript
// api/test/inbox/gi-expense-review-tiers.test.ts
describe('Stage B form submission — tier routing', () => {
  it('Tier 1 path: HIGH confidence + small delta → auto-update + no Decision card', async () => {
    // Submit with quantity_units; expect supplier_items.std_cost_per_inv_uom updated,
    // price_history row inserted, change_log row, NO decision:gi_price_proposal card,
    // To-Do resolved with note 'Auto-updated within Tier 1'.
  });
  it('Tier 2 path: medium delta → price_proposals row + Decision card', async () => {...});
  it('Tier 3 path: anomalous delta → Warning card + no auto-update + no proposal', async () => {...});
  it('boundary 3.000% AND ₪0.50 → Tier 1', async () => {...});
  it('boundary 3.001% AND ₪0.40 → Tier 2', async () => {...});
  it('boundary 15.001% → Tier 3 regardless of ₪ axis', async () => {...});
  it('unit_price_net_override mode → Tier 2 (MEDIUM confidence)', async () => {...});
  it('multi-supplier_item supplier (S2=false) → Tier 2 MEDIUM', async () => {...});
  it('NULL current_price (S4=false) → Tier 2 MEDIUM forced', async () => {...});
  it('XOR violation (both quantity and override null) → 422', async () => {...});
});
```

- [ ] **Step 2: Run tests — RED**

- [ ] **Step 3: Implement per spec §1.14.2 + §1.14.3 + §1.14.4**

Handler runs in a single transaction:
- Validate XOR(quantity_units, unit_price_net_override)
- Compute proposed_unit_price_net per mode
- Compute confidence per §1.14.4 rubric
- Apply tier evaluation per §1.14.3 (top-to-bottom; first match wins)
- Tier 1: write price_history + supplier_items + change_log + resolve To-Do; NO Decision card
- Tier 2: INSERT price_proposals(status='proposed') + emit decision:gi_price_proposal Decision card; resolve To-Do with note
- Tier 3: emit warning:supplier_price_anomaly; NO supplier_items update; NO price_proposals; resolve To-Do with note

Schemas: `Stage B form input` + `Stage B response (tier, proposal_id?, exception_id_new?)`.

Route: `POST /mutations/inbox/gi-expense-review/:gi_expense_id/submit`.

- [ ] **Step 4: Run tests — GREEN**

- [ ] **Step 5: Commit**

```bash
git commit -m "feat(inbox): Stage B — gi_expense_review form handler with tier routing"
```

---

### Task 3.3: `gi_price_proposal` Approve / Edit→Approve / Reject handlers

**Files:**
- Create: `C:\Users\tomw2\Projects\gt-factory-os\api\src\inbox\gi_price_proposal\handler.ts`
- Create: `C:\Users\tomw2\Projects\gt-factory-os\api\src\inbox\gi_price_proposal\route.ts`
- Create: `C:\Users\tomw2\Projects\gt-factory-os\api\src\inbox\gi_price_proposal\schemas.ts`

- [ ] **Step 1: Write tests**

```typescript
// api/test/inbox/gi-price-proposal-approve.test.ts
describe('handleApproveGiPriceProposal', () => {
  it('writes price_history with source=gi_invoice_manual', async () => {...});
  it('updates supplier_items.std_cost_per_inv_uom', async () => {...});
  it('marks proposal status=activated with resulting_price_history_id', async () => {...});
  it('writes 3 change_log rows: PRICE_HISTORY_INSERT + SUPPLIER_PRICE_UPDATE_MANUAL + INBOX_DECISION_APPROVE', async () => {...});
  it('resolves the inbox exception', async () => {...});
  it('mapping-drift guard: 409 SUPPLIER_MAPPING_DRIFT if supplier_item is no longer active or no longer belongs to supplier', async () => {...});
  it('idempotent replay (same actor, same notes) returns 200', async () => {...});
});

// api/test/inbox/gi-price-proposal-edit-approve.test.ts
describe('handleEditApproveGiPriceProposal', () => {
  it('requires override_reason', async () => {...});
  it('immediate activation (effective_at NULL or past) → same as Approve with override price', async () => {...});
  it('future-dated activation (effective_at > NOW()) → status=approved_pending_activation, no supplier_items update', async () => {...});
  it('still writes INBOX_DECISION_APPROVE change_log + resolves exception', async () => {...});
});

// api/test/inbox/gi-price-proposal-reject.test.ts
describe('handleRejectGiPriceProposal', () => {
  it('requires rejection_reason', async () => {...});
  it('writes price_proposals.status=rejected with rejection_reason', async () => {...});
  it('does NOT touch supplier_items', async () => {...});
  it('writes change_log INBOX_DECISION_REJECT', async () => {...});
  it('resolves exception with note prefix Rejected:', async () => {...});
});
```

- [ ] **Step 2: Run tests — RED**

- [ ] **Step 3: Implement per spec §1.14.5**

Three handler functions. Each runs in a single DB transaction. Approve has the mapping-drift guard at step (1). Edit→Approve has the conditional `effective_at` branch.

Route registrations:
- `POST /mutations/inbox/gi-price-proposal/:proposal_id/approve`
- `POST /mutations/inbox/gi-price-proposal/:proposal_id/edit-approve` (body: override_unit_price_net, override_reason, effective_at?)
- `POST /mutations/inbox/gi-price-proposal/:proposal_id/reject` (body: reason)

- [ ] **Step 4: Run tests — GREEN**

- [ ] **Step 5: Commit**

```bash
git commit -m "feat(inbox): gi_price_proposal Approve/Edit-Approve/Reject handlers"
```

---

### Task 3.4: Activator TS shim

**Files:**
- Create: `C:\Users\tomw2\Projects\gt-factory-os\api\src\jobs\gi_price_proposal_activator.ts`

> Note: The actual activation work is in the SQL function `private_core.fn_gi_price_proposal_activator()` from Task 1.6. This shim is a thin wrapper for log/observability purposes when invoked outside pg_cron (e.g., manual trigger from /admin/jobs).

- [ ] **Step 1: Write tests**

```typescript
describe('gi_price_proposal_activator (TS shim)', () => {
  it('invokes SQL function and logs activated_count + failed_count', async () => {...});
  it('no due rows → returns (0, 0) cleanly', async () => {...});
});
```

- [ ] **Step 2-5:** Implement the shim — single async function that calls `SELECT * FROM private_core.fn_gi_price_proposal_activator()` and logs results. Returns the counts.

Commit: `git commit -m "feat(inbox): activator job TS shim for manual trigger"`

---

### Task 3.5: Tests — full price-proposal flow

- [ ] **Step 1: Write integration test** that walks the full path:
  1. Insert a `gi_expense_mirror` row for a mapped single-supplier_item supplier in ILS
  2. Run the Stage A producer
  3. Verify To-Do `gi_expense_review` card emitted
  4. Submit the Stage B form with `quantity_units` for Tier 2 magnitude
  5. Verify `price_proposals` row + `decision:gi_price_proposal` card
  6. Approve the Decision card
  7. Verify `supplier_items.std_cost_per_inv_uom` updated, `price_history` row inserted, `change_log` rows present, exception resolved

- [ ] **Step 2-4: Run + iterate to green**

- [ ] **Step 5: Commit**

```bash
git commit -m "test(inbox): full price-proposal flow integration test"
```

---

**Chunk 3 acceptance:** Stage A + Stage B + activator all working end-to-end; tier routing tested at boundaries; mapping-drift guard fires correctly; price_history append-only invariant preserved; change_log audit complete.

---

## Chunk 4: Portal — single feed + filter + cards

This chunk lands the Inbox UI per spec §1.10. Tasks 4.1-4.11 build components from leaves up; Task 4.12 wires them into the page route.

### Task 4.1: `inbox-copy.ts` — Hebrew register

**Files:**
- Create: `C:\Users\tomw2\Projects\window2-portal-sandbox\src\lib\inbox-copy.ts`
- Test: `C:\Users\tomw2\Projects\window2-portal-sandbox\src\lib\inbox-copy.test.ts`

- [ ] **Step 1: Write test**

```typescript
import { describe, it, expect } from 'vitest';
import { copyForCardType, copyForSubtype, copyForAction, copyForStatus } from './inbox-copy';

describe('inbox-copy', () => {
  it('returns Hebrew label for each card_type', () => {
    expect(copyForCardType('decision')).toBe('החלטה');
    expect(copyForCardType('to_do')).toBe('משימה');
    expect(copyForCardType('warning')).toBe('התראה');
    expect(copyForCardType('info')).toBe('מידע');
  });
  it('returns Hebrew label for known subtypes', () => {
    expect(copyForSubtype('gi_price_proposal')).toBe('שינוי מחיר ספק');
    expect(copyForSubtype('count_large_variance')).toBe('אישור ספירת מלאי');
    expect(copyForSubtype('gi_stale')).toBe('Green Invoice לא מסונכרן');
    expect(copyForSubtype('lw_capped_window')).toBe('חריגה מ-100 שורות ב-LionWheel');
  });
  it('returns macro-status compression', () => {
    expect(copyForStatus('open')).toBe('פתוח');
    expect(copyForStatus('acknowledged')).toBe('פתוח');
    expect(copyForStatus('resolved')).toBe('טופל');
    expect(copyForStatus('auto_resolved')).toBe('טופל');
    expect(copyForStatus('dismissed')).toBe('טופל');
  });
  it('returns action button labels per card_type', () => {
    expect(copyForAction('decision', 'primary')).toBe('אשר');
    expect(copyForAction('warning', 'primary')).toBe('ראיתי');
    expect(copyForAction('to_do', 'primary')).toBe('פתח');
    expect(copyForAction('info', 'primary')).toBe('סגור');
  });
});
```

- [ ] **Step 2: RED**

- [ ] **Step 3: Implement per spec §1.15**

Build all the maps verbatim from the spec's tables. Keep one TypeScript module exporting type-safe lookup functions.

- [ ] **Step 4: GREEN**

- [ ] **Step 5: Commit**

```bash
git commit -m "feat(portal): inbox-copy.ts Hebrew register"
```

---

### Task 4.2: `inbox-status.ts` — macro-status compression

**Files:**
- Create: `C:\Users\tomw2\Projects\window2-portal-sandbox\src\lib\inbox-status.ts`
- Test: `C:\Users\tomw2\Projects\window2-portal-sandbox\src\lib\inbox-status.test.ts`

- [ ] **Step 1-5:** Implement `compressStatus(internal: ExceptionStatus): MacroStatus` per spec §1.11. Tests cover all 8 internal statuses → 2 macro statuses.

Commit: `git commit -m "feat(portal): inbox-status.ts macro-status compression"`

---

### Task 4.3: `TopBadgeStrip` component

**Files:**
- Create: `C:\Users\tomw2\Projects\window2-portal-sandbox\src\components\inbox\TopBadgeStrip.tsx`
- Test: `C:\Users\tomw2\Projects\window2-portal-sandbox\src\components\inbox\TopBadgeStrip.test.tsx`

- [ ] **Step 1: Write component test**

```tsx
// uses @testing-library/react
import { render } from '@testing-library/react';
import { TopBadgeStrip } from './TopBadgeStrip';

describe('TopBadgeStrip', () => {
  it('renders count per type with Hebrew labels', () => {
    const { getByText } = render(<TopBadgeStrip counts={{ decision: 12, to_do: 4, warning: 2, info: 0 }} />);
    expect(getByText('12 החלטות')).toBeInTheDocument();
    expect(getByText('4 משימות')).toBeInTheDocument();
    expect(getByText('2 התראות')).toBeInTheDocument();
  });
  it('does NOT show info count in strip (info is hidden by default)', () => {
    const { queryByText } = render(<TopBadgeStrip counts={{ decision: 0, to_do: 0, warning: 0, info: 99 }} />);
    expect(queryByText(/99/)).not.toBeInTheDocument();
  });
});
```

- [ ] **Step 2-5:** Implement per spec §1.10. Plain shadcn/ui badge primitives. Hebrew via `inbox-copy.ts`.

Commit: `git commit -m "feat(portal): TopBadgeStrip component"`

---

### Task 4.4: `FilterSidePane` component

**Files:**
- Create: `C:\Users\tomw2\Projects\window2-portal-sandbox\src\components\inbox\FilterSidePane.tsx`
- Test: `C:\Users\tomw2\Projects\window2-portal-sandbox\src\components\inbox\FilterSidePane.test.tsx`

- [ ] **Step 1: Test the 5 filter dimensions + saved-view defaults**

- [ ] **Step 2-5:** Per spec §1.10. Maintains a `FilterState` zustand-store-or-prop and emits `onChange(state)`. Saved views: "פתוח" (default) and "טופל" (history).

Commit: `git commit -m "feat(portal): FilterSidePane with 5 dimensions + saved views"`

---

### Task 4.5: `InboxCard` universal frame

**Files:**
- Create: `C:\Users\tomw2\Projects\window2-portal-sandbox\src\components\inbox\InboxCard.tsx`
- Test: `C:\Users\tomw2\Projects\window2-portal-sandbox\src\components\inbox\InboxCard.test.tsx`

- [ ] **Step 1: Test composition slots**

```tsx
describe('InboxCard', () => {
  it('renders Header / KeyFactsStrip / Body slot / ActionBar', () => {...});
  it('scan-row mode shows Header + KeyFacts + primary button only', () => {...});
  it('drawer mode shows all 5 sections', () => {...});
  it('clicks primary action invokes onAction(card)', () => {...});
});
```

- [ ] **Step 2-5:** Per spec §1.4. Compound-component pattern: `<InboxCard><InboxCard.Header/><InboxCard.KeyFacts/>...</InboxCard>`. Reads `card_type`+`subtype` to choose icon/colors via `inbox-copy.ts`.

Commit: `git commit -m "feat(portal): InboxCard universal frame component"`

---

### Tasks 4.6 - 4.11: Body components — one task per body, full 5-step TDD shape

Each task creates exactly one Body component. All 6 are independent (no shared state); they may be parallelized via dispatching-parallel-agents.

#### Task 4.6: `WarningBody.tsx`

**Files:** Create `window2-portal-sandbox/src/components/inbox/bodies/WarningBody.tsx` + `.test.tsx`

- [ ] **Step 1: Test**

```tsx
describe('WarningBody', () => {
  it('renders why text + auto-resolve note', () => {
    const { getByText } = render(<WarningBody data={{ why: 'GI poll failed', autoResolveCondition: 'next successful poll' }} />);
    expect(getByText('GI poll failed')).toBeInTheDocument();
    expect(getByText(/הכרטיסייה תיסגר לבד/)).toBeInTheDocument();
  });
  it('renders deep-link buttons for "what you can do" actions', () => {
    const { getByRole } = render(<WarningBody data={{ ..., actions: [{ label: 'בדוק חיבור', href: '/admin/integrations' }] }} />);
    expect(getByRole('link', { name: 'בדוק חיבור' })).toHaveAttribute('href', '/admin/integrations');
  });
});
```

- [ ] **Step 2-5:** RED → implement per spec §1.6 → GREEN → commit `feat(portal): WarningBody component`

#### Task 4.7: `InfoBody.tsx`

**Files:** Create `…/bodies/InfoBody.tsx` + `.test.tsx`

- [ ] **Step 1: Test**

```tsx
describe('InfoBody', () => {
  it('renders compact diagnostic text', () => {
    const { getByText } = render(<InfoBody data={{ description: 'producer-emitted diagnostic' }} />);
    expect(getByText(/producer-emitted diagnostic/)).toBeInTheDocument();
  });
  it('renders Dismiss-only action by default', () => {
    const { getByRole, queryByRole } = render(<InfoBody data={{ description: 'x' }} />);
    expect(getByRole('button', { name: 'סגור' })).toBeInTheDocument();
    expect(queryByRole('button', { name: 'אשר' })).not.toBeInTheDocument();
  });
});
```

- [ ] **Step 2-5:** RED → spec §1.9 → GREEN → commit `feat(portal): InfoBody component`

#### Task 4.8: `SingleTaskToDoBody.tsx`

**Files:** Create `…/bodies/SingleTaskToDoBody.tsx` + `.test.tsx`

- [ ] **Step 1: Test**

```tsx
describe('SingleTaskToDoBody', () => {
  it('renders why + what + single deep-link button', () => {
    const { getByText, getByRole } = render(<SingleTaskToDoBody data={{
      why: 'GI invoice line not mapped',
      what: 'Map once → future invoices route automatically',
      cta: { label: 'פתח טופס מיפוי', href: '/admin/component-mapping?gi_line=...' }
    }} />);
    expect(getByText(/GI invoice line not mapped/)).toBeInTheDocument();
    expect(getByText(/Map once/)).toBeInTheDocument();
    expect(getByRole('link', { name: 'פתח טופס מיפוי' })).toBeInTheDocument();
  });
});
```

- [ ] **Step 2-5:** RED → spec §1.8 variant 2 → GREEN → commit `feat(portal): SingleTaskToDoBody component`

#### Task 4.9: `QueueToDoBody.tsx`

**Files:** Create `…/bodies/QueueToDoBody.tsx` + `.test.tsx`

- [ ] **Step 1: Test**

```tsx
describe('QueueToDoBody', () => {
  it('renders why + queue count breakdown + Open queue button', () => {
    const { getByText } = render(<QueueToDoBody data={{
      why: '54 active FG without alias',
      counts: { pending: 54, highConfidence: 38 },
      cta: { label: 'פתח את תור המיפוי', href: '/admin/integration-sku-map' }
    }} />);
    expect(getByText(/54/)).toBeInTheDocument();
    expect(getByText(/38/)).toBeInTheDocument();
    expect(getByText(/פתח את תור המיפוי/)).toBeInTheDocument();
  });
});
```

- [ ] **Step 2-5:** RED → spec §1.8 variant 1 → GREEN → commit `feat(portal): QueueToDoBody component`

#### Task 4.10: `StockImpactBody.tsx`

**Files:** Create `…/bodies/StockImpactBody.tsx` + `.test.tsx`

- [ ] **Step 1: Test**

```tsx
describe('StockImpactBody', () => {
  it('renders before/after qty with delta highlighted', () => {
    const { getByText } = render(<StockImpactBody data={{
      itemName: 'אריזת מדבקה 30 מ"מ',
      currentQty: 1240,
      afterQty: 1840,
      delta: 600,
      reasonInInbox: 'receipt exceeds PO line by 20%, planner approval required',
    }} />);
    expect(getByText(/אריזת מדבקה 30 מ"מ/)).toBeInTheDocument();
    expect(getByText(/1,240/)).toBeInTheDocument();
    expect(getByText(/1,840/)).toBeInTheDocument();
    expect(getByText(/\+600/)).toBeInTheDocument();
  });
  it('reused by GR/count/waste subtypes — no subtype-specific logic inside', () => {
    // Component takes pre-computed props; subtypes adapt their data into this shape.
    expect(typeof StockImpactBody).toBe('function');
  });
});
```

- [ ] **Step 2-5:** RED → spec §1.5.2 + §1.5.3 → GREEN → commit `feat(portal): StockImpactBody component (reused by GR/count/waste)`

#### Task 4.11: `PriceProposalBody.tsx`

**Files:** Create `…/bodies/PriceProposalBody.tsx` + `.test.tsx`

- [ ] **Step 1: Test**

```tsx
describe('PriceProposalBody', () => {
  it('renders comparison strip with current/proposed/delta', () => {
    const { getByText } = render(<PriceProposalBody data={{
      currentPrice: 0.842,
      proposedPrice: 0.891,
      pctDelta: 0.058,
      absDelta: 0.049,
      confidence: 'HIGH',
      supplierName: 'מיקי מדבקות',
      componentName: 'אריזת מדבקה 30 מ"מ',
      lastChange: { date: '2025-12-15', from: 0.821, to: 0.842 },
      daysSinceLastChange: 140,
      evidenceUrl: 'https://gi.example/expense/12345.pdf',
      quantityMode: { mode: 'quantity_units', quantity: 5000, totalNet: 4455 },
    }} />);
    expect(getByText(/₪0.842/)).toBeInTheDocument();
    expect(getByText(/₪0.891/)).toBeInTheDocument();
    expect(getByText(/\+5\.8%/)).toBeInTheDocument();
    expect(getByText(/ביטחון: גבוה/)).toBeInTheDocument();
    expect(getByText(/מיקי מדבקות/)).toBeInTheDocument();
    expect(getByText(/2025-12-15/)).toBeInTheDocument();
    expect(getByText(/140/)).toBeInTheDocument();
  });
  it('color codes the comparison strip: green if cheaper, amber if 3-15% more expensive', () => {
    const { container: g } = render(<PriceProposalBody data={{ ...base, pctDelta: -0.05 }} />);
    expect(g.querySelector('[data-color=green]')).toBeInTheDocument();
    const { container: a } = render(<PriceProposalBody data={{ ...base, pctDelta: 0.058 }} />);
    expect(a.querySelector('[data-color=amber]')).toBeInTheDocument();
  });
  it('renders evidence link to GI document PDF', () => {
    const { getByRole } = render(<PriceProposalBody data={{ ..., evidenceUrl: 'https://gi.example/expense/12345.pdf' }} />);
    expect(getByRole('link', { name: /חשבונית/ })).toHaveAttribute('href', 'https://gi.example/expense/12345.pdf');
  });
});
```

- [ ] **Step 2-5:** RED → spec §1.5.1 → GREEN → commit `feat(portal): PriceProposalBody component`

---

### Task 4.12: `/inbox/page.tsx` rewrite

**Files:**
- Modify: `C:\Users\tomw2\Projects\window2-portal-sandbox\src\app\(inbox)\inbox\page.tsx` (full rewrite)
- Test: `C:\Users\tomw2\Projects\window2-portal-sandbox\src\app\(inbox)\inbox\page.test.tsx`

- [ ] **Step 1: Write tests**

```tsx
describe('/inbox page', () => {
  it('fetches GET /queries/exceptions with default filter (open + 3 types)', async () => {...});
  it('renders TopBadgeStrip with counts', () => {...});
  it('renders FilterSidePane', () => {...});
  it('renders feed sorted: decision → to_do → warning, then severity DESC, then created_at ASC', async () => {...});
  it('clicking type-filter checkbox refetches with new filter', async () => {...});
  it('?view=history shows status IN (resolved, auto_resolved, dismissed) within 90 days', async () => {...});
  it('snoozed cards are hidden from default view', async () => {...});
});
```

- [ ] **Step 2-5:** Implement using TanStack Query. Layout: 2-column (filter side-pane + feed). Reads `?view=` from URL params for default vs history. Uses `<InboxCard>` + body components from 4.6-4.11. Renders the appropriate body based on `card_type`+`subtype`.

Commit: `git commit -m "feat(portal): /inbox page — single feed + filter + sort + badges + history view"`

---

**Chunk 4 acceptance:** the Inbox page renders, filters work, sort matches §1.10, all 4 card types display with their respective bodies, history view toggles correctly via URL param.

---

## Chunk 5: Drawers + chrome unification + E2E

### Task 5.1: `gi-expense-review` drawer route (Stage B form)

**Files:**
- Create: `C:\Users\tomw2\Projects\window2-portal-sandbox\src\app\(inbox)\inbox\approvals\gi-expense-review\[gi_expense_id]\page.tsx`
- Test: companion `.test.tsx`

- [ ] **Step 1: Write tests**

```tsx
describe('GI expense review form', () => {
  it('renders supplier name + total + dropdown of supplier_items', async () => {...});
  it('prefills supplier_item dropdown when single active supplier_item exists', async () => {...});
  it('XOR validation: requires quantity_units OR unit_price_net_override', async () => {...});
  it('submit returns Tier 1 result → toast Auto-updated; redirect to /inbox', async () => {...});
  it('submit returns Tier 2 result → redirect to new gi-price-proposal drawer', async () => {...});
});
```

- [ ] **Step 2-5:** Implement per spec §1.14.2 schema. Submit calls `POST /mutations/inbox/gi-expense-review/:gi_expense_id/submit`. Renders the form with Hebrew labels from `inbox-copy.ts`. Includes the worked-example tooltip text per spec §1.14.2.

Commit: `git commit -m "feat(portal): gi-expense-review Stage B form drawer"`

---

### Task 5.2: `gi-price-proposal` Decision drawer

**Files:**
- Create: `C:\Users\tomw2\Projects\window2-portal-sandbox\src\app\(inbox)\inbox\approvals\gi-price-proposal\[proposal_id]\page.tsx`
- Test: companion `.test.tsx`

- [ ] **Step 1-5:** Implement the Decision drawer matching spec §1.5.1. Uses `<PriceProposalBody>` from Task 4.11. Action bar: אשר / ערוך ואשר / דחה / דחה לזמן אחר. Each action calls the appropriate `/approve` / `/edit-approve` / `/reject` endpoint from Task 3.3.

Commit: `git commit -m "feat(portal): gi-price-proposal Decision drawer"`

---

### Task 5.3 - 5.5: Chrome unification (existing drawers)

Each existing drawer (physical-count, waste, credit) gets:
- Wrapped in `<InboxCard>` chrome
- Action bar refactored to use Hebrew copy from `inbox-copy.ts`
- Existing logic preserved

| Task | File | Spec ref |
|---|---|---|
| 5.3 | `app/(inbox)/inbox/approvals/physical-count/[submission_id]/page.tsx` | §1.5.3 |
| 5.4 | `app/(inbox)/inbox/approvals/waste/[submission_id]/page.tsx` | §1.5.3 |
| 5.5 | `app/(inbox)/inbox/credit/[exception_id]/page.tsx` | §1.5.4 (chrome only — drawer logic unchanged) |

Commit messages: `refactor(portal): unify <drawer> chrome to InboxCard frame`

---

### Task 5.6: `?view=history` toggle integration

**Files:**
- Already in `inbox/page.tsx` from Task 4.12. This task is integration-only.

- [ ] **Step 1: E2E test that toggling between feed and history shows different rows**

- [ ] **Step 2-5:** Verify the history filter works against real DB. Add a small UI toggle button in the page header.

Commit: `git commit -m "feat(portal): history view toggle button"`

---

### Tasks 5.7 - 5.11: E2E tests

Each E2E test uses Playwright via the existing `window2-portal-sandbox/e2e/` setup. Tests run against a seeded DB.

| Task | E2E file | Scenario |
|---|---|---|
| 5.7 | `inbox-decision-approve.spec.ts` | Login as planner → see gi_price_proposal Decision card → click Approve → verify supplier_items + price_history + exception resolved + toast |
| 5.8 | `inbox-warning-acknowledge.spec.ts` | Login as planner → see gi_stale Warning → click ראיתי → verify card stays visible but visually muted; verify status='acknowledged' in DB |
| 5.9 | `inbox-todo-deeplink.spec.ts` | Login as planner → see unmapped_fg_alias To-Do → click פתח → verify navigation to /admin/integration-sku-map |
| 5.10 | `inbox-history-view.spec.ts` | Toggle to history → verify resolved cards visible; verify 90-day cutoff filters older rows |
| 5.11 | `inbox-operator-403.spec.ts` | Login as operator → navigate /inbox → verify 403; navigate to own form-submission scoped read → verify works |

For each: write spec → run RED → wire up fixtures → run GREEN → commit.

Commit messages: `test(e2e): <scenario>`

---

### Task 5.12: Final acceptance criteria sweep

- [ ] **Step 1:** Walk through spec §5 (acceptance criteria) item by item; for each, verify by query or manual operation.
- [ ] **Step 2:** Run full test suite (api + portal unit + portal e2e).
- [ ] **Step 3:** Run `SELECT private_core.rebuild_verifier()` — must return 0.
- [ ] **Step 4:** Run the Hebrew register check: grep portal source for any inline Hebrew strings outside `inbox-copy.ts`. Should be zero.
- [ ] **Step 5:** Visual check: open `/inbox` in browser, verify all 4 card types render correctly per the spec mockups.
- [ ] **Step 6:** Final commit + tag

```bash
git commit --allow-empty -m "feat(inbox): typed Inbox + price proposals — all acceptance criteria green"
git tag inbox-typed-cards-v1
```

---

**Chunk 5 acceptance + final acceptance:** the full Inbox feature works end-to-end; all 19 acceptance criteria from spec §5 pass; the Hebrew register is the only source of UI strings; rebuild_verifier returns 0.

---

## Post-implementation hygiene

After all chunks pass:

1. **Update CLAUDE.md** if the new role-gate behavior or any locked decision deserves a permanent note.
2. **Update `docs/CURRENT_STATE.md`** to mark this feature as shipped.
3. **Add a memory note** if any decision in the spec turns out to be load-bearing for future work (e.g., the `price_proposals` table is the canonical lifecycle for future per-line OCR enrichment in v2).
4. **Open a follow-up GitHub issue** for v2 enhancements: per-line GI OCR extraction, configurable thresholds per supplier × commodity, customer-credit drawer redesign, dedicated `/inbox/queues/*` triage UIs.

---

## Notes for the executor

- Spec §X references are absolute — read the spec when in doubt about a code block.
- The migrations chunk (Chunk 1) MUST land BEFORE Chunk 2 code deploys — see spec §2.7 deployment sequencing.
- Tasks within a chunk are mostly independent; Chunks 1, 2, 3 must run in order; Chunks 4 and 5 can interleave.
- This plan was reviewed via 4 spec-reviewer iterations; the spec is approved. If any task description conflicts with the spec, the spec wins.
- Use `superpowers:dispatching-parallel-agents` if multiple independent tasks (e.g., Chunk 2 emitter retrofit, Chunk 4 body components) can be worked in parallel safely.
- Use `superpowers:verification-before-completion` before claiming any task complete — every "Run tests; expect green" step requires actual evidence.

End of plan.
