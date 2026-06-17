# Delete production-plan records — design decision record

> **Status:** Tom-approved 2026-06-17 (brainstorming → design gate passed).
> **Owner:** Tom. **Author:** Claude (brainstorming flow).
> **Scope:** `/planning/production-plan` board — add the ability to permanently delete a production-plan record.
> **Surface:** GT Factory OS core (`production-plan` module). Not a new module; no `MODULE_TEMPLATE` required.

---

## 1. Problem

On the production-plan board (`https://gt-factory-os-portal.vercel.app/planning/production-plan`) a planner can **cancel** a record but cannot **remove** it. Cancel is a soft status-flip (`planned → cancelled`) that keeps the card on the board — greyed, struck-through, with the cancel reason and counted in an "N cancelled" footer chip. Tom needs cancelled (and mistaken) records to be **deletable**, so the board isn't permanently cluttered with records that will never be made.

There is no delete capability anywhere in the system today.

## 2. Decision

Two forks, both Tom-decided on 2026-06-17:

1. **Delete semantics = full hard delete.** The record is permanently removed from the database and disappears from the board. There is no undo button. A complete copy (actor + old values) is automatically preserved in the change-log, so the action is traceable and an admin can recover the data if ever needed.
2. **Deletable scope = any not-yet-produced record.** Both `planned` (live) and `cancelled` records can be deleted directly, in one click, without a cancel-first step. A `done` record (one linked to a real production report / actual) can **never** be deleted.

Cancel is retained unchanged. Cancel and delete now serve distinct purposes:
- **Cancel** = "we planned this but decided not to make it" — keeps a visible, reasoned record.
- **Delete** = "remove this entirely" — clutter cleanup / mistake removal.

## 3. Why this is safe (verified against the code, 2026-06-17)

- **No stock-truth impact.** A `production_plan` row never writes to `stock_ledger` or any balance/projection table — by explicit design (migration `0115_production_plan.sql` lines 9–11, 38–39; `api/src/production-plan/handler.ts` lines 7–8). Stock truth flows only through `production_actual`. Deleting a plan changes **zero** inventory.
- **No referential integrity risk.** No table holds a foreign key referencing `production_plan` (zero inbound FKs). A delete cannot orphan a child row or be blocked by one. Precedent: migration `0139` hard-deleted 5 cancelled rows cleanly.
- **No locked decision violated.** The append-only / never-delete rule (`LOCKED_DECISIONS.md` lines 113, 139; `SCHEMA_GUIDANCE.md` lines 40, 115) is scoped to the **stock ledger and audit tables** — not to planning artifacts. The "prefer soft-delete/archive" guidance (`SCHEMA_GUIDANCE.md` line 116) is scoped to **masters**, not plans. `production_plan` is mutable planning data.
- **Never silent.** The `fn_production_plan_audit` trigger has a `DELETE → PRODUCTION_PLAN_DELETED` branch (migration `0115` lines 385–394; action value declared line 150) that writes the full old row into the change-log. A hard delete is fully audited.

## 4. Architecture

No database migration is required — the table and its audit trigger already support `DELETE`. This feature is **pure API + portal code**.

### 4.1 Backend API — `gt-factory-os/api/src/production-plan/`
- **Route** (`route.ts`): new `DELETE /api/v1/mutations/production-plan/:id`, mirroring the existing PATCH route scaffolding: UUID-format validation → `extractOrFail` authentication → break-glass (`is_break_glass()`) 503 check → handler dispatch → `AuthError`→HTTP mapping in the catch block.
- **Handler** (`handler.ts`): new `handleDeleteProductionPlan`:
  1. Role gate `roleAllowsPlanWrite(session.role)` (planner + admin) → else `403`.
  2. Break-glass active → `503`.
  3. Load the row `FOR UPDATE`; not found → `404`.
  4. `completed_submission_id IS NOT NULL` (done / linked to an actual) → `409 PLAN_NOT_DELETABLE`.
  5. `DELETE FROM private_core.production_plan WHERE plan_id = $id AND completed_submission_id IS NULL` (race-safe: a record that becomes linked mid-request is not deleted; 0 rows affected → `409`).
  6. Set the audit GUCs (`audit.actor_user_id` / `audit.actor_snapshot`) in the same transaction before the DELETE, exactly as the cancel path does, so the `PRODUCTION_PLAN_DELETED` change-log row records the real actor.
  7. Return `200 { deleted: true, plan_id }`.
- **Schema** (`schemas.ts`): path-param schema (UUID) + response schema for the delete.
- Applies to both `plan_type` values — production jobs **and** notes.

### 4.2 Portal proxy — `window2-portal-sandbox/src/app/api/production-plan/[plan_id]/route.ts`
- Add a `DELETE` export calling `proxyRequest(req, { method: "DELETE", upstreamPath: \`/api/v1/mutations/production-plan/${encodeURIComponent(plan_id)}\` })`. `proxyRequest` already accepts `"DELETE"` and forwards auth (dev-shim admin header or Supabase bearer). Mirrors the existing `PATCH` export.

### 4.3 Portal UI — `window2-portal-sandbox/src/app/(planning)/planning/production-plan/`
- **`useDeletePlan`** hook (`_lib/usePlans.ts`): clone of `usePatchPlan` — `method: "DELETE"`, same error-status→message mapping, same `qc.invalidateQueries({ queryKey: ["production-plan"] })` on success.
- **Delete affordance** (Trash2 icon button) on `ProductionJobCard` and `ProductionNoteCard`:
  - Visible when `canAct` (planner/admin) **and** `rendered_state !== "done"`.
  - On **live `planned` cards**: appears alongside the existing Cancel (Ban) button.
  - On **`cancelled` cards**: appears as the card's action (cancelled cards currently expose no actions at all — this is the core gap being closed).
  - `done` cards never expose it.
- **`DeleteModal`** (mirrors `CancelModal`, but **no reason field** — confirm only): destructive-styled confirm button, because hard delete is irreversible. On success: success toast, modal closes, card disappears via cache invalidation.

## 5. Error-handling matrix

| Case | Result |
|---|---|
| planner/admin deletes a `planned` or `cancelled` record | `200`, row removed, `PRODUCTION_PLAN_DELETED` written to change-log |
| operator / viewer | `403` |
| record is `done` (linked to an actual) | `409 PLAN_NOT_DELETABLE` |
| record already deleted / unknown id | `404` |
| break-glass active | `503` |
| record becomes linked mid-request (race) | `409` (WHERE guard yields 0 rows) |

## 6. UX copy (English / LTR, per portal standard)

- Delete button `aria-label`: **"Delete record"**
- Modal title: **"Delete this record?"**
- Modal body: **"This permanently removes the record from the production plan. It won't change any inventory, and it can't be undone."**
- Confirm button (danger): **"Delete"**
- Dismiss button: **"Keep record"**
- Success toast: **"Record deleted"**

## 7. Testing (correctness-first)

- **Backend** (mirror existing production-plan test harness): cover every row of the error-handling matrix — planned-delete `200`, cancelled-delete `200`, done-delete `409`, operator/viewer `403`, unknown-id `404`, break-glass `503`, delete-again `404` (idempotency). Assert a `PRODUCTION_PLAN_DELETED` change-log row is written with the correct actor on a successful delete.
- **Portal**: add `data-testid` to the delete button (`plan-row-delete` / `note-card-delete`) and the delete modal; cover both the planned-card and cancelled-card delete paths.

## 8. Out of scope (YAGNI)

- No bulk "delete all cancelled" action — per-record only.
- No optional delete reason — the change-log already records who/what/when.
- No un-delete / restore UI — the change-log copy is the admin recovery path.
- No database migration, no new column, no soft-delete flag.

## 9. Delivery

- **No migration.** Two PRs, each cut from a **worktree off `origin/main`** (local checkouts are ~40 migrations / 63 commits stale, per project memory):
  - Backend PR (`gt-factory-os`): `route.ts` + `handler.ts` + `schemas.ts` + tests. Deploys to Railway from `main`.
  - Portal PR (`window2-portal-sandbox` / `gt-factory-os-portal`): proxy `DELETE` + `useDeletePlan` + card buttons + `DeleteModal` + tests. Deploys to Vercel from `main`.
- No frozen flags touched, no external-system writes, no stock-truth impact, no hard stop gate — fits the mission-scoped git/deploy authority.

## 10. Verification items to confirm during implementation (not design blockers)

- Confirm the `fn_production_plan_audit` trigger's `DELETE` branch reads `audit.actor_user_id` / `audit.actor_snapshot` GUCs the same way the cancel path sets them, so the actor is captured (read migration `0115` lines 385–394 + the handler's GUC-setting pattern).
- Confirm the exact `reason_code` enum/shape used by the production-plan handler so `PLAN_NOT_DELETABLE` is added consistently (or reuse `PLAN_NOT_EDITABLE` if the schema constrains the set).
- Confirm the production-plan backend test harness (file + runner) and the portal test harness for the board.
