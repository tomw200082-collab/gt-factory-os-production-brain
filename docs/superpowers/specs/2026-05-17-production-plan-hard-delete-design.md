# Production Plan — Hard Delete (replace soft-cancel)

**Date:** 2026-05-17
**Author:** Tom + Claude (brainstorming)
**Status:** Approved design — pending implementation plan
**Surface:** `/planning/production-plan` ("Production Plan" daily board)

---

## 1. Context & goal

The Production Plan board (`/planning/production-plan`) is a human-intent
calendar of planned production runs. Today, removing a plan is a **soft-cancel**:
the row stays in `private_core.production_plan` with `status='cancelled'` and
keeps rendering as a greyed-out, struck-through card plus an "X cancelled"
footer count.

Plans change frequently in real factory use, so cancelled cards accumulate and
clutter the board. Tom wants cancellation to **hard-delete** the plan — gone
from the board as if it never existed.

This is safe because **canceling/deleting a plan has zero stock-ledger and zero
projection footprint** — `production_plan` is intent-only; real stock truth
flows exclusively through `production_actual` submissions. There is no ledger
trigger on `production_plan`.

## 2. Decisions locked during brainstorming

- **Delete guard:** one-click delete + an "Undo" toast (~7s). No confirmation
  modal, no reason field.
- **Existing cancelled rows:** purged as part of the migration — clean board
  from day one.
- **Audit:** every delete still leaves one `change_log` row
  (`PRODUCTION_PLAN_DELETED`) — invisible on the board, kept as an internal
  forensic trace. The plan is gone from every operational view, not from the
  audit log.
- **Scope of deletable plans:** only `status='planned'` plans **not** linked to
  a completed `production_actual` (`completed_submission_id IS NULL`). A plan
  already reported as actual production cannot be deleted.

## 3. Scope

### In scope
- DB migration: purge cancelled rows + retire the soft-cancel schema.
- Backend: new `DELETE` endpoint; remove the `cancel` PATCH action.
- Portal: delete button + undo-toast flow; remove all cancelled-state UI.
- Tests: pgTAP, backend integration, portal flow.

### Out of scope
- No change to `production_actual`, the stock ledger, projections, or planning
  recommendations.
- No change to plan creation or plan editing (PATCH edit path stays).

## 4. Database changes (`gt-factory-os`)

New migration (next sequential number — `0202_*`; confirm at implementation
time) named e.g. `0202_production_plan_hard_delete.sql`:

1. **One-time purge:**
   `DELETE FROM private_core.production_plan WHERE status = 'cancelled';`
   The existing audit trigger `trg_production_plan_audit` already fires
   `AFTER ... DELETE` and emits one `PRODUCTION_PLAN_DELETED` `change_log` row
   per purged plan — no new trigger needed.

2. **Retire the soft-cancel schema** (no future writer after this change):
   - Drop the `production_plan_cancellation_consistency` CHECK constraint.
   - Drop columns `cancelled_at`, `cancelled_by_user_id`, `cancel_reason`.
   - Narrow the `status` CHECK from `('planned','cancelled')` to `('planned')`.
     (The column stays — `'done'` remains derived from
     `completed_submission_id IS NOT NULL`; `status` is now always `'planned'`
     for any live row.)
   - Optionally tidy `fn_production_plan_audit()`: the UPDATE branch
     `old.status='planned' and new.status='cancelled'` becomes unreachable.
     Harmless if left, but the comment on the function should be updated.

**Note:** The DELETE branch of `fn_production_plan_audit()` already exists and
works (resolves actor from `current_setting('audit.actor_user_id', true)` with
fallback to `old.created_by_user_id`). No trigger work required.

## 5. Backend changes (`gt-factory-os/api/src/production-plan/`)

- **`route.ts`** — add `DELETE /api/v1/mutations/production-plan/:id`.
- **`handler.ts`** — new delete handler:
  - `DELETE FROM private_core.production_plan
     WHERE plan_id = :id AND status = 'planned'
       AND completed_submission_id IS NULL`
  - Before the delete, set the audit actor context the same way the existing
    edit/cancel path does (`set local "audit.actor_user_id" = :session_user`,
    `audit.actor_snapshot`) so the `change_log` row records the deleter, not the
    original author.
  - `0 rows` deleted → distinguish: row missing → `404`; row exists but
    completed/non-planned → `409`.
  - Remove the `action: 'cancel'` branch from the PATCH handler.
- **`schemas.ts`** — remove the `cancel` variant from the PATCH discriminated
  union (`action: 'cancel'` + `cancel_reason`). PATCH keeps only the edit shape.

## 6. Portal changes (`window2-portal-sandbox`, `/planning/production-plan`)

- **`src/app/api/production-plan/[plan_id]/route.ts`** — add a `DELETE` export
  proxying to `/api/v1/mutations/production-plan/:id`. Update the file comment
  ("Edit OR cancel modes" → "Edit (PATCH) / Delete (DELETE)").
- **`_lib/usePlans.ts`** — add `useDeletePlan()` mutation hitting
  `DELETE /api/production-plan/:id`; on success invalidate `["production-plan"]`.
  Update the 409 copy in `mapStatusToHebrew` ("already completed or cancelled"
  → "already completed").
- **`_lib/types.ts`** — remove the `cancel` PATCH variant; remove `'cancelled'`
  from `rendered_state`; remove `cancel_reason` / `cancelled_*` from
  `ProductionPlanRow`.
- **`_components/ProductionJobCard.tsx`** — rename the `onCancel` prop/button to
  `onDelete`: "Cancel plan" + `Ban` icon → "Delete plan" + `Trash2` icon. Remove
  the entire `isCancelled` rendering branch (struck-through qty, `Ban` status
  icon, cancelled-reason chip, `opacity-70`).
- **`_components/ProductionNoteCard.tsx`** — same delete treatment for note
  cards (notes are deleted, not cancelled).
- **`_components/ProductionDayLane.tsx`** — remove any
  `rendered_state === 'cancelled'` filtering.
- **`page.tsx`** —
  - Remove the `CancelModal` component, the `cancellingPlan` state, and
    `handleCancel`.
  - Remove `cancelledCount` and the "X cancelled" footer row; remove all
    `rendered_state !== 'cancelled'` filters (no cancelled rows exist anymore).
  - New delete flow: on delete click, optimistically remove the card, fire
    `useDeletePlan`, and show a toast `Plan deleted — Undo`.

## 7. Undo behavior

- On delete, the portal keeps the deleted plan's re-create payload in memory
  (`plan_date`, `item_id`, `planned_qty`, `uom`, `notes`,
  `source_recommendation_id`).
- The toast exposes an **Undo** action for ~7s. Clicking Undo re-creates the
  plan via the existing `useCreatePlan()` POST path (fresh `plan_id` — fine, the
  board is intent-only with no ledger).
- If a recommendation-sourced plan is deleted, its `source_recommendation_id`
  link is freed; Undo re-creating with the same recommendation succeeds.
- If Undo is not clicked, the toast expires and the delete stands.

**Open implementation item:** confirm the existing `flashToast` helper supports
an action button; if not, a small toast-with-action variant is needed.

## 8. Testing

- **pgTAP:** the one-time purge leaves zero `status='cancelled'` rows; a manual
  `DELETE` of a planned row emits exactly one `PRODUCTION_PLAN_DELETED`
  `change_log` row with the correct `old_values` and actor.
- **Backend integration:** `DELETE` a `planned` plan → `200`, row gone,
  `change_log` row present; `DELETE` a completed plan → `409`; `DELETE` a
  missing id → `404`.
- **Portal:** delete a card → it disappears + toast shows; Undo re-creates the
  plan; toast expiry leaves the delete final.

## 9. Rollout order

1. DB migration (purge + schema retire).
2. Backend (`DELETE` endpoint; remove `cancel` action).
3. Portal (delete button + undo flow; remove cancelled UI).
4. Tests across all three layers.

Lanes: `backend-db` (DB + API), `portal` (portal). Run through the standard
executors per `EXECUTION_POLICY.md`.

## 10. Open implementation items

- Confirm next migration number (`0202` expected; `0201` is current head).
- Confirm `flashToast` supports an action button (Undo); add a variant if not.
- Decide whether to recreate `fn_production_plan_audit()` to drop the now-dead
  `cancelled` UPDATE branch, or leave it as harmless dead code (low priority).
