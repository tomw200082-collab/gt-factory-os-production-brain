# Production Plan Hard-Delete Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace soft-cancel of production plans with a hard delete — the plan row is removed from the database and disappears from the board, with a one-click delete + undo-toast flow.

**Architecture:** Three layers. (1) DB migration `0202` purges existing `status='cancelled'` rows and retires the soft-cancel schema. (2) Backend adds `DELETE /api/v1/mutations/production-plan/:id` and removes the PATCH `cancel` action. (3) Portal replaces the Cancel button + modal with a delete button + undo toast and removes all cancelled-state UI. Deleting a plan has zero stock-ledger impact; the existing audit trigger already emits a `PRODUCTION_PLAN_DELETED` `change_log` row on every `DELETE`.

**Tech Stack:** PostgreSQL + pgTAP, Fastify + Kysely + Zod (TypeScript, `gt-factory-os/api`), Next.js 15 App Router + TanStack Query (`window2-portal-sandbox`).

**Spec:** `docs/superpowers/specs/2026-05-17-production-plan-hard-delete-design.md`

**Repos:**
- `gt-factory-os` at `C:/Users/tomw2/Projects/gt-factory-os` — Tasks 1–7.
- `window2-portal-sandbox` at `C:/Users/tomw2/Projects/window2-portal-sandbox` — Tasks 8–14.
- Task 15 is cross-repo verification.

**Pre-req for DB/API tasks:** `DATABASE_URL` (and `DATABASE_URL_POOLED` in `gt-factory-os/.env`) must point at the working Postgres. The API test reads `DATABASE_URL_POOLED` from `gt-factory-os/.env`.

---

## File Structure

**`gt-factory-os` (create):**
- `db/migrations/0202_production_plan_hard_delete.sql` — purge cancelled rows + retire soft-cancel schema.

**`gt-factory-os` (modify):**
- `db/tests/0115_production_plan.test.sql` — adjust T07/T08/T12/T14 for the new schema.
- `api/src/production-plan/schemas.ts` — drop the `cancel` PATCH variant + cancelled fields; add delete types.
- `api/src/production-plan/handler.reads.ts` — drop cancelled columns from query + row mapping.
- `api/src/production-plan/handler.ts` — drop the cancel branch; add `handleDeleteProductionPlan`.
- `api/src/production-plan/route.ts` — register the `DELETE` route.
- `api/test/production_plan_api.test.ts` — replace the cancel test with delete tests.

**`window2-portal-sandbox` (modify):**
- `src/app/api/production-plan/[plan_id]/route.ts` — add `DELETE` proxy export.
- `src/app/(planning)/planning/production-plan/_lib/types.ts` — narrow types; drop cancelled fields + cancel variant.
- `src/app/(planning)/planning/production-plan/_lib/usePlans.ts` — add `useDeletePlan`.
- `src/app/(planning)/planning/production-plan/_components/ProductionJobCard.tsx` — delete button; remove cancelled rendering.
- `src/app/(planning)/planning/production-plan/_components/ProductionNoteCard.tsx` — delete button; remove cancelled rendering.
- `src/app/(planning)/planning/production-plan/_components/ProductionDayLane.tsx` — rename `onCancel` → `onDelete`.
- `src/app/(planning)/planning/production-plan/page.tsx` — remove CancelModal + cancelled UI; add delete + undo flow.

---

## Task 1: DB migration — purge cancelled rows + retire soft-cancel schema

**Files:**
- Create: `gt-factory-os/db/migrations/0202_production_plan_hard_delete.sql`

- [ ] **Step 1: Write the migration**

Create `gt-factory-os/db/migrations/0202_production_plan_hard_delete.sql`:

```sql
-- ===========================================================================
-- 0202_production_plan_hard_delete.sql
-- ===========================================================================
-- Production plans are now hard-deleted (DELETE), never soft-cancelled.
-- Spec: docs/superpowers/specs/2026-05-17-production-plan-hard-delete-design.md
--
-- This migration:
--   1. Purges every existing status='cancelled' plan row. Each DELETE fires
--      the existing trg_production_plan_audit trigger, which emits one
--      PRODUCTION_PLAN_DELETED change_log row per purged plan (actor falls
--      back to the plan's original created_by_user_id — acceptable for a
--      one-time system migration).
--   2. Retires the soft-cancel schema: drops the cancellation-consistency
--      CHECK, drops the three cancellation columns, and narrows the status
--      CHECK so 'cancelled' is no longer a legal value.
--
-- The change_log action enum keeps PRODUCTION_PLAN_CANCELLED (historical rows
-- may reference it). The fn_production_plan_audit() UPDATE branch that maps
-- planned->cancelled is now unreachable dead code but is harmless and is left
-- in place to keep this migration minimal.
--
-- Zero stock_ledger impact: production_plan has no ledger trigger.
-- ===========================================================================

begin;

set search_path to private_core, public;

-- 1. Purge existing cancelled plans (audit trigger emits PRODUCTION_PLAN_DELETED).
delete from private_core.production_plan
 where status = 'cancelled';

-- 2a. Drop the cancellation-consistency CHECK (references the columns dropped next).
alter table private_core.production_plan
  drop constraint production_plan_cancellation_consistency;

-- 2b. Drop the three cancellation columns.
alter table private_core.production_plan
  drop column cancelled_at,
  drop column cancelled_by_user_id,
  drop column cancel_reason;

-- 2c. Narrow the status CHECK: 'planned' is now the only legal value.
--     'done' remains DERIVED from completed_submission_id IS NOT NULL.
alter table private_core.production_plan
  drop constraint production_plan_status_check;
alter table private_core.production_plan
  add constraint production_plan_status_check
  check (status in ('planned'));

commit;

-- ===========================================================================
-- End of 0202_production_plan_hard_delete.sql
-- ===========================================================================
```

- [ ] **Step 2: Apply the migration**

Run from `gt-factory-os`:
```
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/migrations/0202_production_plan_hard_delete.sql
```
Expected: `BEGIN ... DELETE <n> ... ALTER TABLE ... COMMIT` with no error.

If Step 2 fails with `constraint "production_plan_status_check" does not exist`, the inline status CHECK was auto-named differently. Find the real name:
```
psql "$DATABASE_URL" -c "\d private_core.production_plan"
```
Use the printed CHECK name (the one whose definition is `status IN (...)`) in Step 1's `drop constraint` line, then re-apply.

- [ ] **Step 3: Verify schema state**

Run:
```
psql "$DATABASE_URL" -c "\d private_core.production_plan" -c "select count(*) from private_core.production_plan where status='cancelled'"
```
Expected: no `cancelled_at` / `cancelled_by_user_id` / `cancel_reason` columns; the status CHECK reads `status = ANY (ARRAY['planned'])` (or `status IN ('planned')`); the count query returns `0`.

- [ ] **Step 4: Commit**

```
git add db/migrations/0202_production_plan_hard_delete.sql
git commit -m "feat(db): hard-delete production plans, retire soft-cancel schema"
```

---

## Task 2: Update pgTAP test 0115 for the new schema

The `0115_production_plan.test.sql` test runs against the migrated DB. After Task 1, three of its assertions reference a schema that no longer exists. Rewrite them in place so the file stays at `plan(15)` and all green.

**Files:**
- Modify: `gt-factory-os/db/tests/0115_production_plan.test.sql`

- [ ] **Step 1: Update the T07 comment**

Replace:
```sql
-- T07 — status enum only accepts 'planned' | 'cancelled'
```
with:
```sql
-- T07 — status enum only accepts 'planned' (0202 narrowed it from planned|cancelled)
```
And in the same `throws_ok` call replace the description string:
```sql
  'T07 status=''in_progress'' rejected (only planned|cancelled allowed)'
```
with:
```sql
  'T07 status=''in_progress'' rejected (only planned allowed)'
```

- [ ] **Step 2: Replace T08 (cancellation-consistency CHECK is gone)**

Replace the entire T08 block:
```sql
-- T08 — cancelled row with completed_submission_id NOT NULL rejected by
-- the cancellation_consistency CHECK
select throws_ok(
  $$insert into private_core.production_plan
      (plan_date, item_id, planned_qty, uom, status,
       cancelled_at, cancelled_by_user_id, cancel_reason,
       completed_submission_id,
       created_by_user_id, created_by_snapshot)
    values
      (current_date + 1, 'FG-PP114-FIXTURE', 100, 'LTR-PP114', 'cancelled',
       now(), '00000000-0000-0000-0000-000000000114', 'tester',
       gen_random_uuid(),
       '00000000-0000-0000-0000-000000000114', 'pp114-fix')$$,
  '23514',
  null,
  'T08 cancelled row with completed_submission_id rejected by consistency CHECK'
);
```
with:
```sql
-- T08 — status='cancelled' rejected by the narrowed status CHECK (0202).
select throws_ok(
  $$insert into private_core.production_plan
      (plan_date, item_id, planned_qty, uom, status,
       created_by_user_id, created_by_snapshot)
    values
      (current_date + 1, 'FG-PP114-FIXTURE', 100, 'LTR-PP114', 'cancelled',
       '00000000-0000-0000-0000-000000000114', 'pp114-fix')$$,
  '23514',
  null,
  'T08 status=''cancelled'' rejected by narrowed status CHECK'
);
```

- [ ] **Step 3: Replace T12 (planned->cancelled UPDATE no longer possible)**

Replace the entire T12 block:
```sql
-- T12 — UPDATE planned→cancelled emits PRODUCTION_PLAN_CANCELLED
do $$
declare
  v_pa_actor uuid := '00000000-0000-0000-0000-000000000114';
  v_id uuid;
  v_action_count int;
begin
  insert into private_core.production_plan
    (plan_date, item_id, planned_qty, uom,
     created_by_user_id, created_by_snapshot)
  values
    (current_date + 11, 'FG-PP114-FIXTURE', 60, 'LTR-PP114',
     v_pa_actor, 'pp114-fix')
  returning plan_id into v_id;

  update private_core.production_plan
     set status              = 'cancelled',
         cancelled_at        = now(),
         cancelled_by_user_id = v_pa_actor,
         cancel_reason       = 'pp114-test-T12'
   where plan_id = v_id;

  select count(*) into v_action_count
    from private_core.change_log
   where entity_table = 'production_plan'
     and entity_id    = v_id::text
     and action       = 'PRODUCTION_PLAN_CANCELLED';

  perform ok(v_action_count = 1,
    'T12 UPDATE planned→cancelled emits PRODUCTION_PLAN_CANCELLED');
end $$;
```
with:
```sql
-- T12 — DELETE emits PRODUCTION_PLAN_DELETED in change_log
do $$
declare
  v_pa_actor uuid := '00000000-0000-0000-0000-000000000114';
  v_id uuid;
  v_action_count int;
begin
  insert into private_core.production_plan
    (plan_date, item_id, planned_qty, uom,
     created_by_user_id, created_by_snapshot)
  values
    (current_date + 11, 'FG-PP114-FIXTURE', 60, 'LTR-PP114',
     v_pa_actor, 'pp114-fix')
  returning plan_id into v_id;

  delete from private_core.production_plan where plan_id = v_id;

  select count(*) into v_action_count
    from private_core.change_log
   where entity_table = 'production_plan'
     and entity_id    = v_id::text
     and action       = 'PRODUCTION_PLAN_DELETED';

  perform ok(v_action_count = 1,
    'T12 DELETE emits exactly one PRODUCTION_PLAN_DELETED change_log row');
end $$;
```

- [ ] **Step 4: Update T14 (replace the cancel UPDATE with a DELETE)**

In the T14 block, replace:
```sql
  update private_core.production_plan
     set status               = 'cancelled',
         cancelled_at         = now(),
         cancelled_by_user_id = v_pa_actor,
         cancel_reason        = 'pp114-test-T14 cancelled'
   where plan_id = v_id;

  select count(*) into v_ledger_after from private_core.stock_ledger;

  perform ok(v_ledger_after = v_ledger_before,
    'T14 no stock_ledger row written by plan INSERT/UPDATE/CANCEL');
```
with:
```sql
  delete from private_core.production_plan where plan_id = v_id;

  select count(*) into v_ledger_after from private_core.stock_ledger;

  perform ok(v_ledger_after = v_ledger_before,
    'T14 no stock_ledger row written by plan INSERT/UPDATE/DELETE');
```

- [ ] **Step 5: Update the assertion-inventory header comment**

Near the top of the file, replace these three header lines:
```sql
--     T07  status='in_progress' rejected (only 'planned' | 'cancelled' allowed)
--     T08  cancelled row with completed_submission_id NOT NULL rejected
```
```sql
--     T12  UPDATE planned→cancelled emits PRODUCTION_PLAN_CANCELLED
```
with:
```sql
--     T07  status='in_progress' rejected (only 'planned' allowed)
--     T08  status='cancelled' rejected by narrowed status CHECK
```
```sql
--     T12  DELETE emits PRODUCTION_PLAN_DELETED
```

- [ ] **Step 6: Run the test**

Run from `gt-factory-os`:
```
pg_prove -d "$DATABASE_URL" db/tests/0115_production_plan.test.sql
```
Expected: `ok` for all 15 assertions, `Result: PASS`.

- [ ] **Step 7: Commit**

```
git add db/tests/0115_production_plan.test.sql
git commit -m "test(db): update production_plan pgTAP for hard-delete schema"
```

---

## Task 3: Backend schemas — drop cancel variant, add delete types

**Files:**
- Modify: `gt-factory-os/api/src/production-plan/schemas.ts`

- [ ] **Step 1: Narrow the status query enum**

Replace:
```typescript
    status: z.enum(['planned', 'cancelled']).optional(),
```
with:
```typescript
    status: z.enum(['planned']).optional(),
```

- [ ] **Step 2: Replace the PATCH request schema with edit-only**

Replace the whole `PatchProductionPlanRequestSchema` block:
```typescript
// ---------------------------------------------------------------------------
// PATCH /api/v1/mutations/production-plan/:id — request schema
// Two modes: "edit" (default) or "cancel" (if action: 'cancel' supplied).
// ---------------------------------------------------------------------------
export const PatchProductionPlanRequestSchema = z.union([
  // Cancel mode
  z.object({
    action: z.literal('cancel'),
    cancel_reason: NotesSchema.min(1, 'cancel_reason required'),
  }),
  // Edit mode (no action field; at least one editable field required)
  z
    .object({
      action: z.undefined().optional(),
      plan_date: IsoDateSchema.optional(),
      planned_qty: QtySchema.optional(),
      uom: UomSchema.optional(),
      notes: NotesSchema.optional(),
      bom_version_id_pinned: UuidSchema.optional(),
    })
    .refine(
      (b) =>
        b.plan_date !== undefined ||
        b.planned_qty !== undefined ||
        b.uom !== undefined ||
        b.notes !== undefined ||
        b.bom_version_id_pinned !== undefined,
      { message: 'at least one editable field required' },
    ),
]);
```
with:
```typescript
// ---------------------------------------------------------------------------
// PATCH /api/v1/mutations/production-plan/:id — request schema
// Edit only. Removal of a plan is a hard DELETE (see route.ts), not a PATCH.
// ---------------------------------------------------------------------------
export const PatchProductionPlanRequestSchema = z
  .object({
    plan_date: IsoDateSchema.optional(),
    planned_qty: QtySchema.optional(),
    uom: UomSchema.optional(),
    notes: NotesSchema.optional(),
    bom_version_id_pinned: UuidSchema.optional(),
  })
  .refine(
    (b) =>
      b.plan_date !== undefined ||
      b.planned_qty !== undefined ||
      b.uom !== undefined ||
      b.notes !== undefined ||
      b.bom_version_id_pinned !== undefined,
    { message: 'at least one editable field required' },
  );
```

- [ ] **Step 3: Narrow `RenderedState` and the `ProductionPlanRow` status field**

Replace:
```typescript
// Rendered state — derived in the API layer. The DB only stores planned|cancelled.
export type RenderedState = 'planned' | 'done' | 'cancelled';
```
with:
```typescript
// Rendered state — derived in the API layer. 'done' is derived from
// completed_submission_id; the DB status column is always 'planned'.
export type RenderedState = 'planned' | 'done';
```

In `interface ProductionPlanRow`, replace:
```typescript
  status: 'planned' | 'cancelled';
```
with:
```typescript
  status: 'planned';
```

- [ ] **Step 4: Remove the cancelled fields from `ProductionPlanRow`**

In `interface ProductionPlanRow`, delete these three lines:
```typescript

  cancelled_at: string | null;
  cancelled_by_user_id: string | null;
  cancel_reason: string | null;
```

- [ ] **Step 5: Add the delete result type**

After the `export type PatchProductionPlanResponse = ProductionPlanRow;` line, add:
```typescript

export interface DeleteProductionPlanResponse {
  deleted: true;
  plan_id: string;
}
```

- [ ] **Step 6: Update the file header comment**

Replace:
```typescript
//   PATCH /api/v1/mutations/production-plan/:id    (edit OR cancel)
```
with:
```typescript
//   PATCH  /api/v1/mutations/production-plan/:id   (edit only)
//   DELETE /api/v1/mutations/production-plan/:id   (hard delete)
```
And replace:
```typescript
//   - "done" is DERIVED from completed_submission_id IS NOT NULL (contract §3.1).
//     The status enum stored in DB is { 'planned' | 'cancelled' } only.
//     The API exposes a derived rendered_state field: 'planned' | 'done' | 'cancelled'.
```
with:
```typescript
//   - "done" is DERIVED from completed_submission_id IS NOT NULL (contract §3.1).
//     The DB status column is always 'planned' (migration 0202).
//     The API exposes a derived rendered_state field: 'planned' | 'done'.
```

- [ ] **Step 7: Typecheck**

Run from `gt-factory-os/api`:
```
npm run typecheck
```
Expected: errors only in `handler.ts`, `handler.reads.ts`, and `route.ts` (fixed in Tasks 4–6). No errors in `schemas.ts`. If `schemas.ts` itself has an error, fix it before continuing.

- [ ] **Step 8: Commit**

```
git add api/src/production-plan/schemas.ts
git commit -m "feat(api): production-plan schemas — edit-only PATCH, add delete type"
```

---

## Task 4: Backend read handler — drop cancelled columns

**Files:**
- Modify: `gt-factory-os/api/src/production-plan/handler.reads.ts`

- [ ] **Step 1: Narrow the `RawRow` status field**

Replace:
```typescript
  status: 'planned' | 'cancelled';
```
with:
```typescript
  status: 'planned';
```

- [ ] **Step 2: Remove the cancelled fields from `RawRow`**

Delete these three lines from `interface RawRow`:
```typescript

  cancelled_at: Date | null;
  cancelled_by_user_id: string | null;
  cancel_reason: string | null;
```

- [ ] **Step 3: Simplify `deriveRenderedState`**

Replace:
```typescript
function deriveRenderedState(row: RawRow): RenderedState {
  if (row.status === 'cancelled') return 'cancelled';
  if (row.completed_submission_id !== null) return 'done';
  return 'planned';
}
```
with:
```typescript
function deriveRenderedState(row: RawRow): RenderedState {
  if (row.completed_submission_id !== null) return 'done';
  return 'planned';
}
```

- [ ] **Step 4: Remove the cancelled fields from `toResponseRow`**

Delete these four lines from the returned object in `toResponseRow`:
```typescript

    cancelled_at: row.cancelled_at ? row.cancelled_at.toISOString() : null,
    cancelled_by_user_id: row.cancelled_by_user_id,
    cancel_reason: row.cancel_reason,
```

- [ ] **Step 5: Remove the cancelled columns from both SQL queries**

The cancelled columns appear in BOTH the `handleListProductionPlan` query and the `loadPlanById` query. In each, delete this 3-line `select` fragment:
```sql

      pp.cancelled_at,
      pp.cancelled_by_user_id::text as cancelled_by_user_id,
      pp.cancel_reason,
```

- [ ] **Step 6: Typecheck**

Run from `gt-factory-os/api`:
```
npm run typecheck
```
Expected: no errors in `handler.reads.ts` (errors may remain in `handler.ts` / `route.ts` until Tasks 5–6).

- [ ] **Step 7: Commit**

```
git add api/src/production-plan/handler.reads.ts
git commit -m "feat(api): production-plan reads — drop cancelled columns"
```

---

## Task 5: Backend mutation handler — drop cancel, add delete

**Files:**
- Modify: `gt-factory-os/api/src/production-plan/handler.ts`

- [ ] **Step 1: Update imports and the file header**

In the import block, replace:
```typescript
import type {
  CreateProductionPlanRequest,
  CreateProductionPlanResponse,
  PatchProductionPlanRequest,
  PatchProductionPlanResponse,
  ProductionPlanConflictResponse,
  BreakGlassSkippedResponse,
} from './schemas.js';
```
with:
```typescript
import type {
  CreateProductionPlanRequest,
  CreateProductionPlanResponse,
  PatchProductionPlanRequest,
  PatchProductionPlanResponse,
  DeleteProductionPlanResponse,
  ProductionPlanConflictResponse,
  BreakGlassSkippedResponse,
} from './schemas.js';
```
In the file header comment, replace:
```typescript
// PATCH /api/v1/mutations/production-plan/:id      — edit OR cancel
```
with:
```typescript
// PATCH  /api/v1/mutations/production-plan/:id     — edit
// DELETE /api/v1/mutations/production-plan/:id     — hard delete
```
And replace:
```typescript
//   - "done" is derived; the DB status enum is { 'planned' | 'cancelled' }.
```
with:
```typescript
//   - "done" is derived; the DB status column is always 'planned'.
```

- [ ] **Step 2: Add the delete result envelope**

After the `PatchProductionPlanResult` type, add:
```typescript

export type DeleteProductionPlanResult =
  | { status: 200; body: DeleteProductionPlanResponse }
  | { status: 404; body: ProductionPlanConflictResponse }
  | { status: 409; body: ProductionPlanConflictResponse }
  | { status: 503; body: BreakGlassSkippedResponse };
```

- [ ] **Step 3: Narrow the PATCH `cur` query type**

In `handlePatchProductionPlan`, replace:
```typescript
    const cur = await sql<{
      plan_id: string;
      status: 'planned' | 'cancelled';
      completed_submission_id: string | null;
      item_id: string;
      plan_type: string;
    }>`
```
with:
```typescript
    const cur = await sql<{
      plan_id: string;
      status: 'planned';
      completed_submission_id: string | null;
      item_id: string;
      plan_type: string;
    }>`
```

- [ ] **Step 4: Remove the cancelled-status 409 check**

In `handlePatchProductionPlan`, delete this block (the `completed_submission_id` 409 check immediately above it stays):
```typescript
    if (row.status === 'cancelled') {
      return {
        status: 409,
        body: {
          reason_code: 'PLAN_NOT_EDITABLE',
          detail: `plan_id=${planId} is cancelled`,
        },
      };
    }
```

- [ ] **Step 5: Replace the cancel/edit branch with edit-only**

In `handlePatchProductionPlan`, replace:
```typescript
    // Branch: cancel mode vs edit mode (discriminated by `action`).
    if ('action' in request && request.action === 'cancel') {
      // Cancel.
      await sql`
        update private_core.production_plan
           set status               = 'cancelled',
               cancelled_at         = now(),
               cancelled_by_user_id = ${session.user_id}::uuid,
               cancel_reason        = ${request.cancel_reason}::text,
               updated_by_user_id   = ${session.user_id}::uuid,
               updated_by_snapshot  = ${session.display_name || session.email}::text,
               updated_at           = now()
         where plan_id = ${planId}::uuid
      `.execute(trx);
    } else {
      // Edit.
      const editReq = request as Exclude<typeof request, { action: 'cancel' }>;

      // Note rows: only plan_date and notes are editable.
      if (row.plan_type === 'note') {
```
with:
```typescript
    // Edit. (Removal of a plan is a hard DELETE, not a PATCH.)
    {
      const editReq = request;

      // Note rows: only plan_date and notes are editable.
      if (row.plan_type === 'note') {
```

> Note: the closing `}` of the original `else` block stays — it now closes the new `{ ... }` edit block. No brace count changes.

- [ ] **Step 6: Add the delete handler**

At the end of the file (after `handlePatchProductionPlan`), add:
```typescript

// ===========================================================================
// DELETE /api/v1/mutations/production-plan/:id
// ===========================================================================
// Hard-deletes a plan row. The existing trg_production_plan_audit trigger
// emits a PRODUCTION_PLAN_DELETED change_log row. Zero stock_ledger impact.
// Only 'planned' rows not linked to a completed production_actual are
// deletable; a completed plan returns 409.
export async function handleDeleteProductionPlan(
  db: Db,
  session: Session,
  planId: string,
): Promise<DeleteProductionPlanResult> {
  if (!roleAllowsPlanWrite(session.role)) {
    throw new AuthError('Role not permitted for production-plan delete', 403);
  }

  if (await checkBreakGlass(db)) {
    return {
      status: 503,
      body: { skipped: true, reason: 'break_glass' },
    };
  }

  return await db.transaction().execute(async (trx): Promise<DeleteProductionPlanResult> => {
    await setAuditContext(trx, session.user_id, session.display_name || session.email);

    const cur = await sql<{
      plan_id: string;
      completed_submission_id: string | null;
    }>`
      select plan_id, completed_submission_id
        from private_core.production_plan
       where plan_id = ${planId}::uuid
       for update
    `.execute(trx);

    const row = cur.rows[0];
    if (!row) {
      return {
        status: 404,
        body: {
          reason_code: 'PLAN_NOT_FOUND',
          detail: `plan_id=${planId} not found`,
        },
      };
    }
    if (row.completed_submission_id !== null) {
      return {
        status: 409,
        body: {
          reason_code: 'PLAN_NOT_DELETABLE',
          detail: `plan_id=${planId} is linked to production_actual ${row.completed_submission_id} and cannot be deleted`,
        },
      };
    }

    await sql`
      delete from private_core.production_plan
       where plan_id = ${planId}::uuid
    `.execute(trx);

    return {
      status: 200,
      body: { deleted: true, plan_id: planId },
    };
  });
}
```

- [ ] **Step 7: Typecheck**

Run from `gt-factory-os/api`:
```
npm run typecheck
```
Expected: no errors in `handler.ts` (errors may remain only in `route.ts` until Task 6).

- [ ] **Step 8: Commit**

```
git add api/src/production-plan/handler.ts
git commit -m "feat(api): production-plan — drop cancel, add hard-delete handler"
```

---

## Task 6: Backend route — register the DELETE endpoint

**Files:**
- Modify: `gt-factory-os/api/src/production-plan/route.ts`

- [ ] **Step 1: Import the delete handler**

Replace:
```typescript
import {
  handleCreateProductionPlan,
  handlePatchProductionPlan,
} from './handler.js';
```
with:
```typescript
import {
  handleCreateProductionPlan,
  handlePatchProductionPlan,
  handleDeleteProductionPlan,
} from './handler.js';
```

- [ ] **Step 2: Update the route list header comment**

Replace:
```typescript
// Four endpoints:
//   GET   /api/v1/queries/production-plan?from=&to=&item_id=&status=&include_completed=
//   POST  /api/v1/mutations/production-plan   — plan_type: 'production' | 'note'
//   PATCH /api/v1/mutations/production-plan/:id
```
with:
```typescript
// Endpoints:
//   GET    /api/v1/queries/production-plan?from=&to=&item_id=&status=&include_completed=
//   GET    /api/v1/queries/production-plan/recommendation-candidates
//   POST   /api/v1/mutations/production-plan   — plan_type: 'production' | 'note'
//   PATCH  /api/v1/mutations/production-plan/:id
//   DELETE /api/v1/mutations/production-plan/:id
```

- [ ] **Step 3: Register the DELETE route**

Immediately after the closing `);` of the `app.patch('/api/v1/mutations/production-plan/:id', ...)` block (the last route in `registerProductionPlanRoutes`), add:
```typescript

  // =========================================================================
  // DELETE /api/v1/mutations/production-plan/:id
  // =========================================================================
  app.delete(
    '/api/v1/mutations/production-plan/:id',
    async (req: FastifyRequest, reply: FastifyReply) => {
      const session = await extractOrFail(deps, req, reply);
      if (!session) return;

      const { id } = req.params as { id: string };
      if (!id || !UUID_RX.test(id)) {
        return reply.code(422).send({
          validation_errors: [
            { path: ['id'], code: 'invalid_uuid', message: 'id must be UUID' },
          ],
        });
      }
      try {
        const result = await handleDeleteProductionPlan(deps.db, session, id);
        return reply.code(result.status).send(result.body);
      } catch (err) {
        if (err instanceof AuthError) {
          return reply.code(err.statusCode).send({ error: err.message });
        }
        throw err;
      }
    },
  );
```

- [ ] **Step 4: Typecheck**

Run from `gt-factory-os/api`:
```
npm run typecheck
```
Expected: PASS — no errors anywhere.

- [ ] **Step 5: Commit**

```
git add api/src/production-plan/route.ts
git commit -m "feat(api): register DELETE /production-plan/:id route"
```

---

## Task 7: Backend integration test — delete endpoint

**Files:**
- Modify: `gt-factory-os/api/test/production_plan_api.test.ts`

- [ ] **Step 1: Add `DELETE` to the `req` helper**

Replace:
```typescript
async function req(
  userId: string | null,
  role: AppRole | null,
  method: 'GET' | 'POST' | 'PATCH',
  url: string,
  body?: unknown,
) {
```
with:
```typescript
async function req(
  userId: string | null,
  role: AppRole | null,
  method: 'GET' | 'POST' | 'PATCH' | 'DELETE',
  url: string,
  body?: unknown,
) {
```

- [ ] **Step 2: Update the test inventory header**

Replace:
```typescript
//   PATCH /api/v1/mutations/production-plan/:id
```
with:
```typescript
//   PATCH  /api/v1/mutations/production-plan/:id
//   DELETE /api/v1/mutations/production-plan/:id
```
And replace:
```typescript
// T12  409 PATCH cancel-with-reason; subsequent PATCH returns 409 PLAN_NOT_EDITABLE
```
with:
```typescript
// T12  200 DELETE planned plan; row gone + PRODUCTION_PLAN_DELETED change_log row
// T15  404 DELETE non-existent plan_id
// T16  no stock_ledger row written by DELETE
```

- [ ] **Step 3: Locate and replace the T12 test**

Find the test whose name begins with `'T12'` (the cancel-with-reason test). Replace that entire `test('T12 ...', async () => { ... });` block with the two tests below. If the test uses a previously-created `createdPlanIds` entry, these replacements create their own fixture plans instead.

```typescript
test('T12 DELETE planned plan — row gone + PRODUCTION_PLAN_DELETED change_log', async () => {
  // Create a plan to delete.
  const created = await req(PLANNER_USER_ID, 'planner', 'POST', '/api/v1/mutations/production-plan', {
    plan_type: 'production',
    plan_date: new Date(Date.now() + 86400000).toISOString().slice(0, 10),
    item_id: pickedItemId,
    planned_qty: 12,
    uom: pickedUom,
  });
  assert.equal(created.status, 201);
  const planId = (created.body as { plan_id: string }).plan_id;

  // Delete it.
  const del = await req(PLANNER_USER_ID, 'planner', 'DELETE', `/api/v1/mutations/production-plan/${planId}`);
  assert.equal(del.status, 200);
  assert.deepEqual(del.body, { deleted: true, plan_id: planId });

  // Row is gone.
  const after = await sql<{ n: string }>`
    select count(*)::text as n from private_core.production_plan
     where plan_id = ${planId}::uuid
  `.execute(db);
  assert.equal(after.rows[0].n, '0');

  // change_log has exactly one PRODUCTION_PLAN_DELETED row for it.
  const log = await sql<{ n: string }>`
    select count(*)::text as n from private_core.change_log
     where entity_table = 'production_plan'
       and entity_id    = ${planId}
       and action       = 'PRODUCTION_PLAN_DELETED'
  `.execute(db);
  assert.equal(log.rows[0].n, '1');
});

test('T15 DELETE non-existent plan_id returns 404', async () => {
  const res = await req(
    PLANNER_USER_ID, 'planner', 'DELETE',
    '/api/v1/mutations/production-plan/00000000-0000-0000-0000-0000000000ff',
  );
  assert.equal(res.status, 404);
  assert.equal((res.body as { reason_code: string }).reason_code, 'PLAN_NOT_FOUND');
});
```

- [ ] **Step 4: Add the ledger-isolation test for DELETE**

Append a new test at the end of the file (before nothing — it is the last `test(...)` call):
```typescript
test('T16 DELETE writes no stock_ledger row', async () => {
  const before = await sql<{ n: string }>`
    select count(*)::text as n from private_core.stock_ledger
  `.execute(db);

  const created = await req(PLANNER_USER_ID, 'planner', 'POST', '/api/v1/mutations/production-plan', {
    plan_type: 'production',
    plan_date: new Date(Date.now() + 86400000).toISOString().slice(0, 10),
    item_id: pickedItemId,
    planned_qty: 7,
    uom: pickedUom,
  });
  assert.equal(created.status, 201);
  const planId = (created.body as { plan_id: string }).plan_id;

  const del = await req(PLANNER_USER_ID, 'planner', 'DELETE', `/api/v1/mutations/production-plan/${planId}`);
  assert.equal(del.status, 200);

  const after = await sql<{ n: string }>`
    select count(*)::text as n from private_core.stock_ledger
  `.execute(db);
  assert.equal(Number(after.rows[0].n), Number(before.rows[0].n));
});
```

- [ ] **Step 5: Run the test file**

Run from `gt-factory-os/api`:
```
npm test -- test/production_plan_api.test.ts
```
(or, if the runner does not accept a file arg: `npx tsx --test --test-concurrency=1 test/production_plan_api.test.ts`)
Expected: all tests pass, including T12, T15, T16.

- [ ] **Step 6: Commit**

```
git add api/test/production_plan_api.test.ts
git commit -m "test(api): production-plan delete endpoint coverage"
```

---

## Task 8: Portal proxy — add DELETE export

**Files:**
- Modify: `window2-portal-sandbox/src/app/api/production-plan/[plan_id]/route.ts`

- [ ] **Step 1: Replace the file with PATCH + DELETE exports**

Replace the whole file with:
```typescript
import { proxyRequest } from "@/lib/api-proxy";

// PATCH  /api/production-plan/[plan_id] → /api/v1/mutations/production-plan/:id
//   Edit a plan.
// DELETE /api/production-plan/[plan_id] → /api/v1/mutations/production-plan/:id
//   Hard-delete a plan.

export async function PATCH(
  req: Request,
  { params }: { params: Promise<{ plan_id: string }> },
): Promise<Response> {
  const { plan_id } = await params;
  return proxyRequest(req, {
    method: "PATCH",
    upstreamPath: `/api/v1/mutations/production-plan/${encodeURIComponent(plan_id)}`,
    errorLabel: "production plan patch",
  });
}

export async function DELETE(
  req: Request,
  { params }: { params: Promise<{ plan_id: string }> },
): Promise<Response> {
  const { plan_id } = await params;
  return proxyRequest(req, {
    method: "DELETE",
    upstreamPath: `/api/v1/mutations/production-plan/${encodeURIComponent(plan_id)}`,
    errorLabel: "production plan delete",
  });
}
```

- [ ] **Step 2: Commit**

```
git add "src/app/api/production-plan/[plan_id]/route.ts"
git commit -m "feat(portal): production-plan proxy — add DELETE"
```

---

## Task 9: Portal types — narrow types, drop cancelled fields

**Files:**
- Modify: `window2-portal-sandbox/src/app/(planning)/planning/production-plan/_lib/types.ts`

- [ ] **Step 1: Narrow `RenderedState`**

Replace:
```typescript
export type RenderedState = "planned" | "done" | "cancelled";
```
with:
```typescript
export type RenderedState = "planned" | "done";
```

- [ ] **Step 2: Narrow `ProductionPlanRow.status` and drop cancelled fields**

In `interface ProductionPlanRow`, replace:
```typescript
  status: "planned" | "cancelled";
```
with:
```typescript
  status: "planned";
```
And delete these three lines from the same interface:
```typescript

  cancelled_at: string | null;
  cancelled_by_user_id: string | null;
  cancel_reason: string | null;
```

- [ ] **Step 3: Replace `PatchProductionPlanRequest` with edit-only + add delete response**

Replace:
```typescript
export type PatchProductionPlanRequest =
  | { action: "cancel"; cancel_reason: string }
  | {
      action?: undefined;
      plan_date?: string;
      planned_qty?: number;
      uom?: string;
      notes?: string;
      bom_version_id_pinned?: string;
    };
```
with:
```typescript
export interface PatchProductionPlanRequest {
  plan_date?: string;
  planned_qty?: number;
  uom?: string;
  notes?: string;
  bom_version_id_pinned?: string;
}

export interface DeleteProductionPlanResponse {
  deleted: true;
  plan_id: string;
}
```

- [ ] **Step 4: Commit**

```
git add "src/app/(planning)/planning/production-plan/_lib/types.ts"
git commit -m "feat(portal): production-plan types — edit-only PATCH, delete type"
```

---

## Task 10: Portal data hook — add useDeletePlan

**Files:**
- Modify: `window2-portal-sandbox/src/app/(planning)/planning/production-plan/_lib/usePlans.ts`

- [ ] **Step 1: Add `DeleteProductionPlanResponse` to the type import**

Replace:
```typescript
import type {
  CreatePlanOrNoteRequest,
  CreateProductionPlanResponse,
  ListProductionPlanResponse,
  PatchProductionPlanRequest,
  ProductionPlanRow,
  RecommendationCandidatesResponse,
} from "./types";
```
with:
```typescript
import type {
  CreatePlanOrNoteRequest,
  CreateProductionPlanResponse,
  DeleteProductionPlanResponse,
  ListProductionPlanResponse,
  PatchProductionPlanRequest,
  ProductionPlanRow,
  RecommendationCandidatesResponse,
} from "./types";
```

- [ ] **Step 2: Add the `useDeletePlan` hook**

Immediately after the `usePatchPlan` function (before `function mapStatusToHebrew`), add:
```typescript

export function useDeletePlan() {
  const qc = useQueryClient();
  return useMutation<DeleteProductionPlanResponse, Error, { plan_id: string }>({
    mutationFn: async ({ plan_id }) => {
      const res = await fetch(
        `/api/production-plan/${encodeURIComponent(plan_id)}`,
        { method: "DELETE" },
      );
      if (!res.ok) {
        const text = await res.text().catch(() => "");
        let detail = "";
        try {
          detail = (JSON.parse(text) as { detail?: string }).detail ?? "";
        } catch {
          /* ignore */
        }
        throw new Error(mapStatusToHebrew(res.status) + (detail && res.status === 409 ? ` (${detail})` : ""));
      }
      return (await res.json()) as DeleteProductionPlanResponse;
    },
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["production-plan"] });
    },
  });
}
```

- [ ] **Step 3: Update the 409 copy in `mapStatusToHebrew`**

Replace:
```typescript
  if (status === 409) return "This plan is already completed or cancelled and cannot be edited.";
```
with:
```typescript
  if (status === 409) return "This plan is already completed and can't be changed.";
```

- [ ] **Step 4: Commit**

```
git add "src/app/(planning)/planning/production-plan/_lib/usePlans.ts"
git commit -m "feat(portal): add useDeletePlan mutation hook"
```

---

## Task 11: Portal — ProductionJobCard delete button

**Files:**
- Modify: `window2-portal-sandbox/src/app/(planning)/planning/production-plan/_components/ProductionJobCard.tsx`

- [ ] **Step 1: Swap the `Ban` icon import for `Trash2`**

In the `lucide-react` import block, replace `Ban,` with `Trash2,`.

- [ ] **Step 2: Rename the `onCancel` prop to `onDelete`**

Replace:
```typescript
  onEdit,
  onCancel,
}: {
  plan: ProductionPlanRow;
  canAct: boolean;
  isToday: boolean;
  onEdit: (p: ProductionPlanRow) => void;
  onCancel: (p: ProductionPlanRow) => void;
}) {
  const isLive = plan.rendered_state === "planned";
  const isDone = plan.rendered_state === "done";
  const isCancelled = plan.rendered_state === "cancelled";
  const isRec = !!plan.source_recommendation_id;
```
with:
```typescript
  onEdit,
  onDelete,
}: {
  plan: ProductionPlanRow;
  canAct: boolean;
  isToday: boolean;
  onEdit: (p: ProductionPlanRow) => void;
  onDelete: (p: ProductionPlanRow) => void;
}) {
  const isLive = plan.rendered_state === "planned";
  const isDone = plan.rendered_state === "done";
  const isRec = !!plan.source_recommendation_id;
```

- [ ] **Step 3: Remove cancelled styling from the outer card div**

Replace:
```typescript
        isLive && !isCancelled && "border-l-warning bg-bg-raised border-warning/20",
        isDone && "border-l-success bg-bg-raised border-success/20",
        isCancelled && "border-l-border/40 bg-bg-subtle/60 opacity-70",
```
with:
```typescript
        isLive && "border-l-warning bg-bg-raised border-warning/20",
        isDone && "border-l-success bg-bg-raised border-success/20",
```

- [ ] **Step 4: Remove cancelled styling from the quantity block**

Replace:
```typescript
              isLive && "text-warning-fg",
              isDone && "text-success-fg",
              isCancelled && "text-fg-muted line-through",
```
with:
```typescript
              isLive && "text-warning-fg",
              isDone && "text-success-fg",
```
And replace:
```typescript
                isLive && "text-warning-fg/80",
                isDone && "text-success-fg/80",
                isCancelled && "text-fg-muted",
```
with:
```typescript
                isLive && "text-warning-fg/80",
                isDone && "text-success-fg/80",
```

- [ ] **Step 5: Remove the cancelled status icon**

Replace:
```typescript
            {isDone && (
              <CheckCircle2
                className="h-3.5 w-3.5 text-success"
                strokeWidth={2}
              />
            )}
            {isCancelled && (
              <Ban className="h-3.5 w-3.5 text-fg-faint" strokeWidth={2} />
            )}
```
with:
```typescript
            {isDone && (
              <CheckCircle2
                className="h-3.5 w-3.5 text-success"
                strokeWidth={2}
              />
            )}
```

- [ ] **Step 6: Remove cancelled styling from the item name**

Replace:
```typescript
          className={cn(
            "text-sm font-semibold leading-tight truncate mb-2",
            isCancelled ? "text-fg-muted" : "text-fg-strong",
          )}
```
with:
```typescript
          className="text-sm font-semibold leading-tight truncate mb-2 text-fg-strong"
```

- [ ] **Step 7: Always show the inventory-impact toggle**

Replace:
```typescript
          {/* Inventory impact toggle */}
          {!isCancelled && (
            <button
              type="button"
              className={cn(
                "chip gap-1 text-[10px] transition-colors",
                impactOpen
                  ? "bg-info-softer/60 border-info/40 text-info-fg"
                  : "hover:bg-info-softer/40 hover:border-info/30 hover:text-info-fg",
              )}
              onClick={toggleImpact}
              aria-expanded={impactOpen}
              aria-label="Toggle inventory impact"
              data-testid="chip-impact-toggle"
            >
              <Boxes className="h-2.5 w-2.5" strokeWidth={2.5} />
              {impactOpen ? (
                <ChevronUp className="h-2 w-2" strokeWidth={2.5} />
              ) : (
                <ChevronDown className="h-2 w-2" strokeWidth={2.5} />
              )}
            </button>
          )}
```
with:
```typescript
          {/* Inventory impact toggle */}
          <button
            type="button"
            className={cn(
              "chip gap-1 text-[10px] transition-colors",
              impactOpen
                ? "bg-info-softer/60 border-info/40 text-info-fg"
                : "hover:bg-info-softer/40 hover:border-info/30 hover:text-info-fg",
            )}
            onClick={toggleImpact}
            aria-expanded={impactOpen}
            aria-label="Toggle inventory impact"
            data-testid="chip-impact-toggle"
          >
            <Boxes className="h-2.5 w-2.5" strokeWidth={2.5} />
            {impactOpen ? (
              <ChevronUp className="h-2 w-2" strokeWidth={2.5} />
            ) : (
              <ChevronDown className="h-2 w-2" strokeWidth={2.5} />
            )}
          </button>
```

- [ ] **Step 8: Remove the cancelled-reason chip**

Delete this block:
```typescript

          {/* Cancelled reason */}
          {isCancelled && plan.cancel_reason && (
            <span
              className="text-[10px] text-fg-faint truncate max-w-[14ch]"
              title={plan.cancel_reason}
            >
              {plan.cancel_reason}
            </span>
          )}
```

- [ ] **Step 9: Replace the cancel button with a delete button**

Replace:
```typescript
            <button
              type="button"
              className="btn btn-ghost btn-xs text-danger"
              onClick={() => onCancel(plan)}
              title="Cancel plan"
              aria-label="Cancel plan"
              data-testid="plan-row-cancel"
            >
              <Ban className="h-2.5 w-2.5" strokeWidth={2.5} />
            </button>
```
with:
```typescript
            <button
              type="button"
              className="btn btn-ghost btn-xs text-danger"
              onClick={() => onDelete(plan)}
              title="Delete plan"
              aria-label="Delete plan"
              data-testid="plan-row-delete"
            >
              <Trash2 className="h-2.5 w-2.5" strokeWidth={2.5} />
            </button>
```

- [ ] **Step 10: Commit**

```
git add "src/app/(planning)/planning/production-plan/_components/ProductionJobCard.tsx"
git commit -m "feat(portal): ProductionJobCard — delete button, drop cancelled UI"
```

---

## Task 12: Portal — ProductionNoteCard delete button

**Files:**
- Modify: `window2-portal-sandbox/src/app/(planning)/planning/production-plan/_components/ProductionNoteCard.tsx`

- [ ] **Step 1: Replace the whole component**

Replace the entire file with:
```typescript
"use client";

import { StickyNote, Pencil, Trash2 } from "lucide-react";
import { cn } from "@/lib/cn";
import type { ProductionPlanRow } from "../_lib/types";

export function ProductionNoteCard({
  plan,
  canAct,
  onEdit,
  onDelete,
}: {
  plan: ProductionPlanRow;
  canAct: boolean;
  onEdit: (p: ProductionPlanRow) => void;
  onDelete: (p: ProductionPlanRow) => void;
}) {
  return (
    <div
      className={cn(
        "rounded-lg border border-border/40 bg-bg-raised",
        "border-l-[3px] border-l-fg-subtle/40",
        "transition-all duration-150",
        "hover:shadow-sm hover:border-border/60",
      )}
      data-testid="production-note-card"
      data-plan-id={plan.plan_id}
    >
      {/* Header row */}
      <div className="flex items-center justify-between gap-2 px-3 pt-2.5 pb-2">
        {/* Left: icon + label */}
        <div className="flex items-center gap-1.5">
          <StickyNote className="h-3 w-3 text-fg-muted shrink-0" strokeWidth={2} />
          <span className="text-[10px] font-semibold uppercase tracking-[0.06em] text-fg-subtle">
            Note
          </span>
        </div>

        {/* Right: actions */}
        {canAct ? (
          <div className="flex items-center gap-1">
            <button
              type="button"
              className="btn btn-ghost btn-xs"
              onClick={() => onEdit(plan)}
              aria-label="Edit note"
              data-testid="note-card-edit"
            >
              <Pencil className="h-2.5 w-2.5" strokeWidth={2.5} />
            </button>
            <button
              type="button"
              className="btn btn-ghost btn-xs text-danger"
              onClick={() => onDelete(plan)}
              aria-label="Delete note"
              data-testid="note-card-delete"
            >
              <Trash2 className="h-2.5 w-2.5" strokeWidth={2.5} />
            </button>
          </div>
        ) : null}
      </div>

      {/* Divider */}
      <div className="border-t border-border/20" />

      {/* Content */}
      <div className="px-3 pb-3 pt-2">
        <p className="text-sm leading-snug line-clamp-5 text-fg">
          {plan.notes ?? <span className="italic text-fg-faint">No note text</span>}
        </p>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```
git add "src/app/(planning)/planning/production-plan/_components/ProductionNoteCard.tsx"
git commit -m "feat(portal): ProductionNoteCard — delete button, drop cancelled UI"
```

---

## Task 13: Portal — ProductionDayLane prop rename

**Files:**
- Modify: `window2-portal-sandbox/src/app/(planning)/planning/production-plan/_components/ProductionDayLane.tsx`

- [ ] **Step 1: Rename the `onCancel` prop to `onDelete`**

In the destructured params list, replace `onCancel,` with `onDelete,`.
In the props type block, replace:
```typescript
  onEdit: (p: ProductionPlanRow) => void;
  onCancel: (p: ProductionPlanRow) => void;
}) {
```
with:
```typescript
  onEdit: (p: ProductionPlanRow) => void;
  onDelete: (p: ProductionPlanRow) => void;
}) {
```

- [ ] **Step 2: Pass `onDelete` to both card components**

In the `ProductionNoteCard` JSX, replace `onCancel={onCancel}` with `onDelete={onDelete}`.
In the `ProductionJobCard` JSX, replace `onCancel={onCancel}` with `onDelete={onDelete}`.

- [ ] **Step 3: Commit**

```
git add "src/app/(planning)/planning/production-plan/_components/ProductionDayLane.tsx"
git commit -m "feat(portal): ProductionDayLane — onCancel → onDelete"
```

---

## Task 14: Portal page — delete + undo flow, remove cancel UI

**Files:**
- Modify: `window2-portal-sandbox/src/app/(planning)/planning/production-plan/page.tsx`

- [ ] **Step 1: Update the data-hook import**

Replace:
```typescript
import {
  usePlans,
  useCreatePlan,
  usePatchPlan,
  useRecommendationCandidates,
  FetchError,
} from "./_lib/usePlans";
```
with:
```typescript
import {
  usePlans,
  useCreatePlan,
  usePatchPlan,
  useDeletePlan,
  useRecommendationCandidates,
  FetchError,
} from "./_lib/usePlans";
```

- [ ] **Step 2: Add `CreatePlanOrNoteRequest` to the type import**

Replace:
```typescript
import type {
  ProductionPlanRow,
  RecommendationCandidate,
} from "./_lib/types";
```
with:
```typescript
import type {
  CreatePlanOrNoteRequest,
  ProductionPlanRow,
  RecommendationCandidate,
} from "./_lib/types";
```

- [ ] **Step 3: Delete the `CancelModal` component**

Delete the entire `function CancelModal({ ... }) { ... }` block (it spans from `function CancelModal({` to its closing `}` before `function Toast({`).

- [ ] **Step 4: Extend the `Toast` component to support an action button**

Replace the whole `function Toast({ ... }) { ... }` block with:
```typescript
function Toast({
  kind,
  message,
  action,
  onClose,
}: {
  kind: "success" | "error";
  message: string;
  action?: { label: string; onClick: () => void };
  onClose: () => void;
}) {
  return (
    <div
      dir="ltr"
      className={cn(
        "fixed bottom-4 left-4 right-4 z-40 mx-auto max-w-md rounded-md border px-4 py-3 text-sm shadow-lg",
        kind === "success"
          ? "border-success/40 bg-success-softer text-success-fg"
          : "border-danger/40 bg-danger-softer text-danger-fg",
      )}
      role="status"
      data-testid="production-plan-toast"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-2">
          {kind === "success" ? (
            <CheckCircle2 className="h-4 w-4 shrink-0 mt-0.5" strokeWidth={2} />
          ) : (
            <XCircle className="h-4 w-4 shrink-0 mt-0.5" strokeWidth={2} />
          )}
          <span>{message}</span>
        </div>
        <div className="flex items-center gap-3 shrink-0">
          {action ? (
            <button
              type="button"
              onClick={action.onClick}
              className="text-xs font-semibold underline hover:no-underline"
              data-testid="production-plan-toast-action"
            >
              {action.label}
            </button>
          ) : null}
          <button
            type="button"
            onClick={onClose}
            className="text-3xs underline hover:no-underline"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 5: Replace the toast state + `flashToast` + add delete state**

Replace:
```typescript
  const [cancellingPlan, setCancellingPlan] = useState<ProductionPlanRow | null>(null);
  const [showMaterialsDrawer, setShowMaterialsDrawer] = useState(false);
  const [toast, setToast] = useState<{ kind: "success" | "error"; message: string } | null>(null);

  const plansQuery = usePlans(toIsoDate(weekStart), toIsoDate(weekEnd));
  const createMut = useCreatePlan();
  const patchMut = usePatchPlan();

  function flashToast(kind: "success" | "error", message: string) {
    setToast({ kind, message });
    window.setTimeout(() => setToast(null), 4500);
  }
```
with:
```typescript
  const [showMaterialsDrawer, setShowMaterialsDrawer] = useState(false);
  const [toast, setToast] = useState<{
    kind: "success" | "error";
    message: string;
    action?: { label: string; onClick: () => void };
  } | null>(null);

  const plansQuery = usePlans(toIsoDate(weekStart), toIsoDate(weekEnd));
  const createMut = useCreatePlan();
  const patchMut = usePatchPlan();
  const deleteMut = useDeletePlan();

  function flashToast(
    kind: "success" | "error",
    message: string,
    action?: { label: string; onClick: () => void },
    durationMs = 4500,
  ) {
    setToast({ kind, message, action });
    window.setTimeout(() => setToast(null), durationMs);
  }
```

- [ ] **Step 6: Replace `handleCancel` with `handleDelete` + `handleUndoDelete`**

Replace:
```typescript
  function handleCancel(reason: string) {
    if (!cancellingPlan) return;
    patchMut.mutate(
      { plan_id: cancellingPlan.plan_id, body: { action: "cancel", cancel_reason: reason } },
      {
        onSuccess: () => {
          flashToast("success", "Plan cancelled. Inventory has not changed.");
          setCancellingPlan(null);
        },
        onError: (err) => { flashToast("error", err.message); },
      },
    );
  }
```
with:
```typescript
  function recreatePayload(plan: ProductionPlanRow): CreatePlanOrNoteRequest {
    if (plan.plan_type === "note") {
      return { plan_type: "note", plan_date: plan.plan_date, notes: plan.notes ?? "" };
    }
    return {
      plan_type: "production",
      plan_date: plan.plan_date,
      item_id: plan.item_id ?? "",
      planned_qty: parseFloat(plan.planned_qty ?? "0"),
      uom: plan.uom ?? "",
      notes: plan.notes ?? undefined,
      source_recommendation_id: plan.source_recommendation_id ?? undefined,
    };
  }

  function handleUndoDelete(payload: CreatePlanOrNoteRequest) {
    setToast(null);
    createMut.mutate(payload, {
      onSuccess: () => { flashToast("success", "Plan restored."); },
      onError: (err) => { flashToast("error", err.message); },
    });
  }

  function handleDelete(plan: ProductionPlanRow) {
    const payload = recreatePayload(plan);
    const label = plan.plan_type === "note" ? "Note" : "Plan";
    deleteMut.mutate(
      { plan_id: plan.plan_id },
      {
        onSuccess: () => {
          flashToast(
            "success",
            `${label} deleted.`,
            { label: "Undo", onClick: () => handleUndoDelete(payload) },
            7000,
          );
        },
        onError: (err) => { flashToast("error", err.message); },
      },
    );
  }
```

- [ ] **Step 7: Remove `cancelledCount` and the now-invalid cancelled filters**

After Task 9 narrows `RenderedState` to `"planned" | "done"`, every `rendered_state === "cancelled"` / `!== "cancelled"` comparison is a TypeScript error (TS2367 — no type overlap). Remove all of them:

Delete this line:
```typescript
  const cancelledCount = productionPlans.filter((p) => p.rendered_state === "cancelled").length;
```

In the `totalQty` derivation, replace:
```typescript
  const totalQty = productionPlans
    .filter((p) => p.rendered_state !== "cancelled")
    .reduce((s, p) => s + (parseFloat(p.planned_qty ?? "0") || 0), 0);
```
with:
```typescript
  const totalQty = productionPlans
    .reduce((s, p) => s + (parseFloat(p.planned_qty ?? "0") || 0), 0);
```

In the `dominantUom` derivation, replace:
```typescript
    const uoms = productionPlans
      .filter((p) => p.rendered_state !== "cancelled")
      .map((p) => p.uom);
```
with:
```typescript
    const uoms = productionPlans.map((p) => p.uom);
```

In the `dayTotals` `useMemo`, replace:
```typescript
      const total = plans
        .filter((p) => p.rendered_state !== "cancelled")
        .reduce((s, p) => s + (parseFloat(p.planned_qty ?? "0") || 0), 0);
      const liveOrDone = plans.filter((p) => p.rendered_state !== "cancelled");
```
with:
```typescript
      const total = plans
        .reduce((s, p) => s + (parseFloat(p.planned_qty ?? "0") || 0), 0);
      const liveOrDone = plans;
```

- [ ] **Step 8: Wire the lanes to `handleDelete`**

In the `ProductionDayLane` JSX, replace:
```typescript
                      onEdit={setEditingPlan}
                      onCancel={setCancellingPlan}
```
with:
```typescript
                      onEdit={setEditingPlan}
                      onDelete={handleDelete}
```

- [ ] **Step 9: Remove the "cancelled" count from the week summary footer**

Delete this block:
```typescript
              {cancelledCount > 0 && (
                <>
                  <span className="text-fg-faint">·</span>
                  <span>
                    <span className="font-semibold text-danger-fg tabular-nums">{cancelledCount}</span>{" "}
                    cancelled
                  </span>
                </>
              )}
```

- [ ] **Step 10: Remove the `CancelModal` render block**

Delete this block:
```typescript
      {cancellingPlan ? (
        <CancelModal
          plan={cancellingPlan}
          onClose={() => setCancellingPlan(null)}
          onSubmit={handleCancel}
          isSubmitting={patchMut.isPending}
        />
      ) : null}
```

- [ ] **Step 11: Render the toast with its action**

Replace:
```typescript
      {toast ? (
        <Toast kind={toast.kind} message={toast.message} onClose={() => setToast(null)} />
      ) : null}
```
with:
```typescript
      {toast ? (
        <Toast
          kind={toast.kind}
          message={toast.message}
          action={toast.action}
          onClose={() => setToast(null)}
        />
      ) : null}
```

- [ ] **Step 12: Remove now-unused imports**

Run from `window2-portal-sandbox`:
```
npx tsc --noEmit
```
The compiler will flag unused imports in `page.tsx` (expected: `Ban` from `lucide-react`, and `fmtQty` from `./_lib/helpers` — both were only used by the deleted `CancelModal`). Remove each name the compiler flags as unused from its import statement. Re-run `npx tsc --noEmit` until it passes with no errors.

- [ ] **Step 13: Commit**

```
git add "src/app/(planning)/planning/production-plan/page.tsx"
git commit -m "feat(portal): production-plan — delete + undo flow, remove cancel UI"
```

---

## Task 15: Cross-repo verification

**Files:** none (verification only).

- [ ] **Step 1: Backend typecheck + full test suite**

Run from `gt-factory-os/api`:
```
npm run typecheck
npm test
```
Expected: typecheck clean; all test files pass, including `production_plan_api.test.ts`.

- [ ] **Step 2: Backend pgTAP — production_plan**

Run from `gt-factory-os`:
```
pg_prove -d "$DATABASE_URL" db/tests/0115_production_plan.test.sql
```
Expected: 15/15 `ok`, `Result: PASS`.

- [ ] **Step 3: Portal typecheck + build**

Run from `window2-portal-sandbox`:
```
npx tsc --noEmit
npm run build
```
Expected: both succeed with no errors.

- [ ] **Step 4: Manual UI smoke test**

Start the portal dev server (`npm run dev` in `window2-portal-sandbox`, with the API reachable) and on `/planning/production-plan`:
1. Add a manual production plan. Confirm the card appears.
2. Click the delete (trash) button on the card. Confirm: the card disappears and a toast `Plan deleted.` with an `Undo` link shows.
3. Click `Undo`. Confirm the plan reappears (a fresh card) and a `Plan restored.` toast shows.
4. Delete the plan again and let the toast expire (~7s) without clicking Undo. Confirm the card stays gone after a refresh.
5. Add a note, delete it the same way, confirm `Note deleted.` toast + Undo works.
6. Confirm there is no "X cancelled" entry in the week-summary footer and no greyed-out struck-through cards anywhere.

Report any discrepancy. If the dev server or API cannot be run in this environment, state that explicitly instead of claiming the smoke test passed.

- [ ] **Step 5: Final commit (only if Step 4 required fixes)**

If the smoke test surfaced fixes, commit them with a clear message. Otherwise nothing to commit — the task commits already cover all changes.

---

## Notes for the implementer

- **Order matters.** Tasks 1–2 (DB) must land before Tasks 3–7 (API) because the API typecheck and tests run against the migrated schema. Tasks 8–14 (portal) depend only on the API contract, not on a running API, but the manual smoke test (Task 15 Step 4) needs both.
- **Zero stock-ledger impact** is the core safety property — `production_plan` has no ledger trigger. Tasks 2 (T14) and 7 (T16) assert it explicitly. Do not weaken those tests.
- **The audit trail survives deletion.** The existing `trg_production_plan_audit` trigger emits a `PRODUCTION_PLAN_DELETED` `change_log` row on every `DELETE`, including the one-time purge in Task 1. This is intentional — the plan vanishes from the board but not from the forensic log.
- **Undo re-creates** the plan via the normal POST path, producing a new `plan_id`. This is correct: `production_plan` is an intent calendar with no ledger identity to preserve.
- The `cancelled` value remains in the `change_log` action enum (`PRODUCTION_PLAN_CANCELLED`) for historical rows — do not remove it.
