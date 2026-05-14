# RM Planning Parameters — Design Spec

**Date:** 2026-05-14
**Status:** Tom-approved
**Scope:** Raw materials (components / supplier_items) only. FG safety stock excluded.
**Goal:** Surface per-component planning parameters in the portal so procurement planning is accurate per item, not global-default-only.

---

## Problem

The planning engine already reads `supplier_items.lead_time_days`, `moq`, and `safety_days` per component. The cascade is: supplier_items → components → global policy fallback (14 days). However:

1. `safety_days` exists in the DB schema and PATCH API but is **not shown or editable anywhere in the portal**.
2. There is no surface that shows a component's **effective planning parameters** (including which level the value comes from: supplier-item, supplier default, or global policy).

`lead_time_days` and `moq` are already editable in `/admin/supplier-items`. The gap is `safety_days` + visibility of the full planning picture per component.

---

## What Is Not Changing

- Backend schema — no migrations required.
- PATCH API for `supplier_items` — already accepts `safety_days`.
- Planning engine — reads from existing cascade; no engine changes.
- FG safety stock — out of scope for this spec.
- Global planning policy keys — not modified.

---

## Surface 1: `/admin/supplier-items` — Add `safety_days` Column

### What changes

Add a **"Safety Days"** column to the supplier-items table, alongside the existing `lead_time_days` and `moq` columns.

### Behavior

- **Inline editable** (admin only) — same pattern as the existing `lead_time_days` inline edit cell.
- **Read-only** for non-admin roles.
- Default display value: `0` (the DB default).
- On save: `PATCH /api/supplier-items/:supplier_item_id` with `{ safety_days, idempotency_key, if_match_updated_at }`.

### Visual treatment

| Value | Color |
|---|---|
| 0 | neutral (gray) |
| 1–6 | amber |
| ≥ 7 | green |

Rationale: inverse of lead time chip (higher safety = more buffer = safer).

### Column placement

Between `moq` and `pack_conversion`. The three planning columns (`lead_time_days`, `moq`, `safety_days`) should be visually grouped.

### Tooltip

> "Days of buffer to hold above the planned need. Added on top of lead time when computing reorder point."

---

## Surface 2: Component Detail Page — "Planning Parameters" Card

**Route:** `/admin/masters/components/[component_id]`

### What changes

Add a read-only **"Planning Parameters"** section (card or collapsible panel) to the component detail page. Placement: below the master data fields, above or alongside supplier-items list.

### Content

| Parameter | Value | Source label |
|---|---|---|
| Lead Time | N days | "Primary supplier" / "Supplier default" / "Global policy (14d)" |
| MOQ | N units (purchase UoM) | "Primary supplier" / "—" |
| Safety Days | N days | "Primary supplier" / "Global policy (0d)" |
| **Effective Reorder Lead** | **N days** | lead_time_days + safety_days |

**Source label logic:**

- If the primary `supplier_item.lead_time_days` is set → "Primary supplier"
- Else if `suppliers.default_lead_time_days` is set → "Supplier default"
- Else → "Global policy (14d)"

Same cascade logic applies to `safety_days` (supplier_item value or "Global policy (0d)").

### Why read-only here

Editing is done on `/admin/supplier-items`. The component detail card is a planning **summary** — helps Tom understand why the engine recommends what it recommends, without duplicating edit surfaces.

### Link

The card includes an anchor link: "Edit in supplier items ↓" that scrolls to the supplier-items section on the same component detail page (which already lists all supplier-items for this component).

---

## Data Flow Summary

```
supplier_items.lead_time_days  ─┐
supplier_items.moq             ─┤─→ Component detail "Planning Parameters" card (read)
supplier_items.safety_days     ─┘         (editable via /admin/supplier-items)
        ↓ cascade trigger
components.lead_time_days  →  planning engine  →  purchase recommendations
planning.supplier.default_lead_time_days (fallback)
planning.safety.stock_days_default = 0 (fallback)
```

---

## Not Included (Deferred)

- `order_multiple` — not in `supplier_items` PATCH schema; deferred.
- FG safety stock per finished good — separate spec, separate lane.
- Per-component `planning_policy` KV keys — not needed; supplier_items columns are sufficient.
- Bulk-edit of planning params across all components — deferred.

---

## Acceptance Criteria

1. Admin can view `safety_days` in `/admin/supplier-items` table with correct color coding.
2. Admin can inline-edit `safety_days` and save; change is persisted and reflected immediately.
3. Non-admin roles see `safety_days` as read-only.
4. Component detail page shows Planning Parameters card with effective values and source labels.
5. "Effective Reorder Lead" = `lead_time_days + safety_days` displayed correctly.
6. Source label correctly identifies whether value comes from supplier_item, supplier default, or global policy.
7. Anchor link in Planning Parameters card scrolls to the supplier-items section on the same page.
8. No backend changes required (all via existing PATCH API).
