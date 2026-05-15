# Implementation Plan: Free-Text Notes on Production Plan
Date: 2026-05-14  
Branch: feat/production-plan-notes (both repos)  
Feature: Standalone note cards on the daily production plan board

## Context
User wants to add free-text "note" entries to the production plan weekly board — not tied to any product/quantity, no inventory impact. Example: "Organize the warehouse", "Technician arriving at 2pm". These appear as distinct cards on the day lane alongside production cards.

Approach: Add `plan_type TEXT NOT NULL DEFAULT 'production' CHECK (plan_type IN ('production', 'note'))` to `production_plan`. Note rows have `item_id`/`planned_qty`/`uom` = NULL; `notes` is the sole content field.

---

## Task 1: DB Migration (backend — gt-factory-os)
**File:** `db/migrations/0188_production_plan_note_type.sql`

```sql
-- Add plan_type discriminator to production_plan
ALTER TABLE private_core.production_plan
  ADD COLUMN plan_type TEXT NOT NULL DEFAULT 'production'
    CHECK (plan_type IN ('production', 'note'));

-- Relax NOT NULL on fields that are null for note rows
ALTER TABLE private_core.production_plan
  ALTER COLUMN item_id DROP NOT NULL,
  ALTER COLUMN planned_qty DROP NOT NULL,
  ALTER COLUMN uom DROP NOT NULL;

-- Enforce field completeness per type
ALTER TABLE private_core.production_plan
  ADD CONSTRAINT chk_production_plan_type_fields CHECK (
    (plan_type = 'production' AND item_id IS NOT NULL AND planned_qty IS NOT NULL AND uom IS NOT NULL)
    OR
    (plan_type = 'note' AND notes IS NOT NULL AND item_id IS NULL AND planned_qty IS NULL AND uom IS NULL)
  );
```

Commit to `feat/production-plan-notes` in gt-factory-os.

---

## Task 2: Backend Schemas (backend — gt-factory-os)
**File:** `api/src/production-plan/schemas.ts`

Changes:
1. `ProductionPlanRow`: add `plan_type: 'production' | 'note'`; make `item_id: string | null`, `planned_qty: string | null`, `uom: string | null`
2. `CreateProductionPlanRequestSchema`: change to `z.discriminatedUnion('plan_type', [...])`:
   - `plan_type: 'production'` → existing fields (item_id, planned_qty, uom required)
   - `plan_type: 'note'` → only `plan_date` + `notes` (required, min 1)
   - Backward compat: `plan_type` optional default 'production' is handled at the union level; if plan_type absent, server returns 422 (client always sends it)

Commit to `feat/production-plan-notes` in gt-factory-os.

---

## Task 3: Backend Handlers (backend — gt-factory-os)
**Files:** `api/src/production-plan/handler.ts`, `api/src/production-plan/handler.reads.ts`

**handler.reads.ts:**
- Add `plan_type: string` to `RawRow`
- Add `pp.plan_type` to both SELECT queries
- Add `plan_type` to `toResponseRow` output

**handler.ts (`handleCreateProductionPlan`):**
- Discriminate by `request.plan_type`:
  - `'production'`: existing logic unchanged
  - `'note'`: skip item/uom/bom checks; insert with `item_id=NULL`, `planned_qty=NULL`, `uom=NULL`, `notes=request.notes`

**handler.ts (`handlePatchProductionPlan`):**
- For note rows: edit mode should allow only `plan_date` and `notes`; reject `planned_qty`/`uom` changes via 422 if somehow supplied (schema prevents it but add a guard)

Commit to `feat/production-plan-notes` in gt-factory-os.

---

## Task 4: Portal Types (portal — window2-portal-sandbox)
**File:** `src/app/(planning)/planning/production-plan/_lib/types.ts`

Changes:
- `ProductionPlanRow`: add `plan_type: 'production' | 'note'`; make `item_id: string | null`, `planned_qty: string | null`, `uom: string | null`
- `CreateProductionPlanRequest`: add `plan_type: 'production'` (explicit); add new `CreateNoteRequest` type: `{ plan_type: 'note'; plan_date: string; notes: string }`
- Export union: `export type CreatePlanOrNoteRequest = CreateProductionPlanRequest | CreateNoteRequest`

Commit to `feat/production-plan-notes` in window2-portal-sandbox.

---

## Task 5: ProductionNoteCard Component (portal — window2-portal-sandbox)
**File:** `src/app/(planning)/planning/production-plan/_components/ProductionNoteCard.tsx`

Design spec:
- Left border: `border-l-fg-subtle` (neutral, not the production warning yellow)
- Background: `bg-bg-raised border-border/30` (clean, light)
- Top section: `StickyNote` icon (lucide) + "Note" label in small caps tracking-sops
- Main content: note text, up to 4 lines, `text-sm text-fg leading-snug`
- If truncated (>4 lines), show full text on hover via `title` attr
- Action strip (canAct + status=planned): Edit (Pencil icon) + Delete/Cancel (Trash2 icon, danger color)
- Cancelled state: opacity-60, strikethrough on note text
- No quantity, no item name, no BOM panel, no Report button

Props: `{ plan: ProductionPlanRow; canAct: boolean; onEdit: (p) => void; onCancel: (p) => void }`

Commit to `feat/production-plan-notes` in window2-portal-sandbox.

---

## Task 6: ProductionDayLane Update (portal — window2-portal-sandbox)
**File:** `src/app/(planning)/planning/production-plan/_components/ProductionDayLane.tsx`

Changes:
1. Add `onAddNote: (date: Date) => void` to props
2. In card stack: render `ProductionNoteCard` when `plan.plan_type === 'note'`, else `ProductionJobCard`
3. Empty day lane (canAct): two options — "Add production" (existing) + small secondary "Add note" link below
4. Footer add strip (when cards exist): replace single "Add" button with two: `Add production` + `Add note` (side by side, both btn-ghost btn-xs)

Commit to `feat/production-plan-notes` in window2-portal-sandbox.

---

## Task 7: page.tsx Update (portal — window2-portal-sandbox)
**File:** `src/app/(planning)/planning/production-plan/page.tsx`

Changes:
1. **`AddNoteModal`** component (new, in same file):
   - Title: "Add a note"
   - Subtitle: "Notes appear on the plan but don't affect inventory."
   - Day field (pre-filled from day lane)
   - Textarea (required, min 1 char, placeholder: "e.g. Organize the warehouse, technician visit...")
   - Buttons: Cancel | Add note (StickyNote icon, btn-primary)

2. **`EditNoteModal`** component (new):
   - Title: "Edit note"
   - Day field + textarea (pre-filled from plan)
   - Save changes button

3. **State additions:**
   - `showAddNote: { defaultDate: string } | null`
   - `editingNote: ProductionPlanRow | null`

4. **Handlers:**
   - `handleAddNote(req)` → calls `createMut.mutate({ plan_type: 'note', ...req })`
   - `handleEditNote(body)` → calls `patchMut.mutate(...)` (only `plan_date` + `notes`)
   - Cancel note reuses `handleCancel` (same PATCH endpoint)

5. **KPI filter:** `allPlans.filter(p => p.plan_type === 'production')` for all KPI calculations (plannedCount, doneCount, cancelledCount, totalQty, completionPct). Notes are excluded from all KPIs.

6. **Header buttons:** Add "Add note" button (FileText icon, btn-sm, positioned before "Add production")

7. **Thread `onAddNote`** to all `ProductionDayLane` instances

8. **Modal rendering:** Add `AddNoteModal` and `EditNoteModal` to modal section

9. **Edit dispatch:** When `setEditingPlan(p)` is called, check `p.plan_type`:
   - `'production'` → existing `EditModal`
   - `'note'` → new `EditNoteModal`
   - Simplest: combine into single edit state `editingPlan`, dispatch to right modal in JSX

Commit to `feat/production-plan-notes` in window2-portal-sandbox.

---

## Dependency Order
1. Task 1 (migration) → Tasks 2, 3 can proceed
2. Tasks 2, 3 → independent but share the same file in Task 2/3 (schemas + handler)
3. Task 4 (portal types) → independent of backend tasks
4. Tasks 5, 6 → depend on Task 4
5. Task 7 → depends on Tasks 4, 5, 6
6. Final review → after all tasks

## Success criteria
- Note cards appear on the weekly board, visually distinct from production cards
- Adding a note via modal creates a row with `plan_type='note'` in DB
- KPI strip counts exclude note rows
- Note cards can be edited (date + text) and cancelled
- Production cards unaffected
- No stock_ledger writes ever (unchanged invariant)
