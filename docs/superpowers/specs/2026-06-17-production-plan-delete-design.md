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
2. **Deletable scope = any not-yet-produced record.** Both `planned` (live) and `cancelled` records can be deleted directly, in one click, without a cancel-first step. **Real production can never be deleted** — that means not only a `done` record (linked to a production actual) but also an `in_production` record and a `completed` base-batch record (the tea-tank `close_batch` path sets `status='completed'` with `completed_submission_id` still NULL). Deletable lifecycle states are exactly `draft` / `planned` / `cancelled`.

> **Implementation correction (review-found, 2026-06-17):** the first cut guarded only on `completed_submission_id IS NOT NULL`. A code review caught that closed base-batch (`status='completed'`, NULL submission) and `in_production` rows both derive to `rendered_state='planned'`, appear on the board, and would have been deletable. The guard now keys on lifecycle **status** (`status IN ('in_production','completed') OR completed_submission_id IS NOT NULL → 409`), in both the handler check and the DELETE `WHERE` clause, and the UI hides the button for those states.

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
  4. `completed_submission_id IS NOT NULL` **OR** `status IN ('in_production','completed')` (real / active production — incl. closed base batches) → `409 PLAN_NOT_DELETABLE`.
  5. `DELETE FROM private_core.production_plan WHERE plan_id = $id AND completed_submission_id IS NULL AND status NOT IN ('in_production','completed')` (race-safe: a record that becomes linked / advances mid-request is not deleted; 0 rows affected → `409`).
  6. Set the audit GUCs (`audit.actor_user_id` / `audit.actor_snapshot`) in the same transaction before the DELETE, exactly as the cancel path does, so the `PRODUCTION_PLAN_DELETED` change-log row records the real actor.
  7. Return `200 { deleted: true, plan_id }`.
- **Schema** (`schemas.ts`): path-param schema (UUID) + response schema for the delete.
- Applies to both `plan_type` values — production jobs **and** notes.

### 4.2 Portal proxy — `window2-portal-sandbox/src/app/api/production-plan/[plan_id]/route.ts`
- Add a `DELETE` export calling `proxyRequest(req, { method: "DELETE", upstreamPath: \`/api/v1/mutations/production-plan/${encodeURIComponent(plan_id)}\` })`. `proxyRequest` already accepts `"DELETE"` and forwards auth (dev-shim admin header or Supabase bearer). Mirrors the existing `PATCH` export.

### 4.3 Portal UI — `window2-portal-sandbox/src/app/(planning)/planning/production-plan/`
- **`useDeletePlan`** hook (`_lib/usePlans.ts`): clone of `usePatchPlan` — `method: "DELETE"`, same error-status→message mapping, same `qc.invalidateQueries({ queryKey: ["production-plan"] })` on success.
- **Delete affordance** (Trash2 icon button) on `ProductionJobCard` and `ProductionNoteCard`:
  - Visible when `canAct` (planner/admin) **and** the row is not produced/active — i.e. `rendered_state !== "done"` **and** `status NOT IN ('in_production','completed')` (a `canDelete` predicate).
  - On **live `planned` cards**: appears alongside the existing Cancel (Ban) button.
  - On **`cancelled` cards**: appears as the card's action (cancelled cards currently expose no actions at all — this is the core gap being closed).
  - `done` / `in_production` / `completed` (base-batch) cards never expose it — they mirror the backend 409.
- **`DeleteModal`** (mirrors `CancelModal`, but **no reason field** — confirm only): destructive-styled confirm button, because hard delete is irreversible. On success: success toast, modal closes, card disappears via cache invalidation.

## 5. Error-handling matrix

| Case | Result |
|---|---|
| planner/admin deletes a `planned`/`draft`/`cancelled` record | `200`, row removed, `PRODUCTION_PLAN_DELETED` written to change-log |
| operator / viewer | `403` |
| record is `done` (linked to an actual) | `409 PLAN_NOT_DELETABLE` |
| record is `in_production` or `completed` (closed base batch) | `409 PLAN_NOT_DELETABLE` |
| record already deleted / unknown id | `404` |
| break-glass active | `503` |
| record becomes linked / advances mid-request (race) | `409` (WHERE guard yields 0 rows) |

## 6. UX copy (English / LTR, per portal standard)

- Delete button `aria-label`: **"Delete record"**
- Modal title: **"Delete this record?"**
- Modal body: **"This permanently removes the record from the production plan. It won't change any inventory, and it can't be undone."**
- Confirm button (danger): **"Delete"**
- Dismiss button: **"Keep record"**
- Success toast: **"Record deleted"**

## 7. Testing (correctness-first) — as built

- **Backend** `api/test/production_plan_delete.test.ts` — **12/12 green** against the live pooled DB (self-cleaning rows; Tom-approved `TEST_ALLOW_PRODUCTION_DB=confirmed` run): missing-auth `401`, viewer/operator `403`, bad-uuid `422`, unknown-id `404`, planned-delete `200` (+ `PRODUCTION_PLAN_DELETED` change-log row asserts the planner actor), cancelled-delete `200`, done-linked `409`, **in_production `409`**, **real closed base-batch `409`** (read-only borrow — confirmed against a live closed-batch row), second-delete `404`, zero-`stock_ledger` invariant.
- **Portal** `_components/card-delete.test.tsx` — **9/9 green** (happy-dom + RTL): delete present on planned + cancelled cards (fires `onDelete`), absent on done / `in_production` / `completed` base-batch / non-actor. Plus `tsc` clean, `eslint` clean, `next build` green.

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

## 10. Verification items — resolved during implementation

- ✅ The `fn_production_plan_audit` trigger's `DELETE` branch reads `audit.actor_user_id` / `audit.actor_snapshot` (migration `0115` lines 385–400); the handler calls `setAuditContext` before the DELETE, exactly as the cancel path does. Test D06 asserts the `PRODUCTION_PLAN_DELETED` row carries the planner actor.
- ✅ `reason_code` is a free-form `string` (`ProductionPlanConflictResponse`), so `PLAN_NOT_DELETABLE` is used (clearer than reusing `PLAN_NOT_EDITABLE`).
- ✅ Harnesses: backend `node:test` + live pooled DB via `app.inject`; portal vitest + happy-dom + RTL.

## 11. Shipped (2026-06-17)

- Backend PR **gt-factory-os#78** → merged to `main` (`26e9275`); live on Railway (`gt-factory-os-api-production.up.railway.app` — unauth `DELETE` returns `401`, route registered).
- Portal PR **gt-factory-os-portal#101** → merged to `main` (`684f019`); Vercel production deploy `dpl_52bPim9Rg…` **READY** (`gt-factory-os-portal.vercel.app`).
- **Follow-up for Tom:** two pre-existing stale branches/worktrees `feat/production-plan-hard-delete` (backend + portal) took a divergent "drop cancel, replace with delete" approach that this work supersedes — safe to delete. Also `production_plan_api.test.ts` has 10 pre-existing failures unrelated to this change (stale POST bodies omit the now-required `plan_type` discriminator from migration 0195).
