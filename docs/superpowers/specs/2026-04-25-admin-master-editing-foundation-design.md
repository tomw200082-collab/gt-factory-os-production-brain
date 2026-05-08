# Admin Master Editing Foundation — Design

**Date:** 2026-04-25
**Author:** Claude (with Tom)
**Corridor:** Slice A+C of "Admin Master Self-Sufficiency" program
**Status:** Draft for review
**Supersedes:** N/A
**Successors planned:** Slice B (BOM/recipe versioning), Slice D (hard-delete workflows)

---

## 1. Goal

Make `/admin/masters/*` a real master-data control center. An admin opens any master record and immediately understands:

1. What is this record?
2. Is it complete or missing something?
3. What is it connected to / what depends on it?
4. What can I edit safely here?
5. What's my next action?

…without DevTools, SQL, or asking Claude.

## 2. Non-goals (this corridor)

- BOM line/version editing UX → **Slice B** (separate corridor; this corridor only adds *visibility* of recipes)
- Hard-delete workflows → **Slice D** (this corridor: archive only)
- Production quantity calculator by finished product → planning corridor (this corridor only ensures admins can *verify* recipe completeness)
- Stock ledger / planning engine semantics — untouched
- Backend API building — if a contract is missing, this corridor produces a **contract spec** to hand off, not a backend implementation

## 3. Hard guardrails

| Rule | Why |
|---|---|
| Active BOM versions are never mutated from this corridor | Production traceability; that's what BOM versioning protects |
| Stock truth, ledger, anchors are never touched | The whole platform's reason to exist |
| Default destructive action is **archive** (status → INACTIVE), not delete | Reversibility |
| Every save persists durably (saved → reload shows the new value) | "Route exists" is not green; persistence is |
| No raw DB column names as primary UI labels | Operational language, not database UI |
| Locked fields stay locked, with explanation | Stock-uom and PK changes corrupt the system silently |

---

## 3.5 Existing routes + URL inventory (factual baseline)

Before any tranche begins, T1 must verify this inventory matches reality. Reviewer caught a dual-tree problem and a verb error — this section is the source of truth.

### 3.5.1 PATCH endpoints (field updates)

All accept `{ if_match_updated_at, idempotency_key, ...fields }` and return the updated row.

| Endpoint | Verb | File |
|---|---|---|
| `/api/items/:item_id` | PATCH | `src/app/api/items/[item_id]/route.ts` |
| `/api/components/:component_id` | PATCH | `src/app/api/components/[component_id]/route.ts` |
| `/api/suppliers/:supplier_id` | PATCH | `src/app/api/suppliers/[supplier_id]/route.ts` |
| `/api/supplier-items/:supplier_item_id` | PATCH | `src/app/api/supplier-items/[supplier_item_id]/route.ts` |

### 3.5.2 Status endpoints (archive / activate)

**Verb is POST (not PATCH).** Body: `{ status, if_match_updated_at, idempotency_key }`.

| Endpoint | Verb |
|---|---|
| `/api/items/:item_id/status` | POST |
| `/api/components/:component_id/status` | POST |
| `/api/suppliers/:supplier_id/status` | POST |
| `/api/supplier-items/:supplier_item_id/status` | POST |

The portal helper `postStatus()` in `src/lib/admin/mutations.ts` already wraps this. Restore (INACTIVE → ACTIVE) reuses the same endpoint with `status: "ACTIVE"`.

### 3.5.3 Dual detail-page tree (must resolve in T1)

There are **two** detail-page implementations per entity:

| Entity | Path A (older, richer) | Path B (newer, viewer-style) |
|---|---|---|
| Component | `/admin/components/[component_id]` | `/admin/masters/components/[component_id]` |
| Item | `/admin/items/[item_id]` (verify) | `/admin/masters/items/[item_id]` |
| Supplier | `/admin/suppliers/[supplier_id]` (verify) | `/admin/masters/suppliers/[supplier_id]` |

**Path A (`/admin/[entity]/[id]`):** has working inline edit on many fields including some that this spec wants to **lock** (e.g. `inventory_uom`, `purchase_uom`, `bom_uom`). Has `ReadinessCard` + supplier coverage with `QuickCreateSupplierItem`.

**Path B (`/admin/masters/[entity]/[id]`):** uses the unified `DetailPage` primitive, has tabs (Overview / BOM / Supplier-items / Anchors / Policy / Exceptions), is mostly view-only.

**Today's list pages link to Path B.** Path A is reachable only by direct URL, but it still ships and Tom may have it bookmarked.

**Decision required in T1:**
- **Option 1 — Consolidate to B (recommended):** port the good parts of A (inline edit on Class S fields, ReadinessCard, supplier coverage section) into B; redirect A → B; delete A.
- **Option 2 — Consolidate to A:** keep the simpler one-page layout; rip out B; rewire list pages.
- **Option 3 — Keep both:** rejected. Drift continues; admin gets two truths.

The matrix audit (T1) must explicitly resolve this. **Default recommendation is Option 1** because B is what the navigation already targets and it has the extensible primitive (`DetailPage`).

### 3.5.4 Concurrency model (existing)

All PATCH/POST mutations use **`if_match_updated_at`** = the row's `updated_at` at read time. On conflict, upstream returns 409. Idempotency: every mutation requires a fresh `idempotency_key` (UUID v4) per logical save attempt. `patchEntity()` and `postStatus()` in `mutations.ts` already accept these.

**This corridor's UI must:**
- Read `updated_at` at the time of opening an edit drawer (not at page load — that's stale by the time the drawer opens).
- Generate a fresh idempotency key per save attempt; reuse only on auto-retry of the same logical action.
- Handle 409 with a clear message: "This record changed under you. [Reload]" — and reload the row, not silently overwrite.

### 3.5.5 Audit history surface (existing)

Each entity exposes `created_at` + `updated_at`. The `change_log` table exists but no portal endpoint exposes it as a list. **Decision for this corridor:** in-scope to surface `updated_at` (already done) + `last_modified_by_snapshot` if the API returns it; full change-log timeline is **deferred to a later corridor** and is removed from the matrix's "audit/history visible" criterion.

---

## 4. Editability matrix (Phase 1 deliverable)

The matrix audits the current state and defines the target state. It lives at:
**`window2-portal-sandbox/docs/admin/master-editability-matrix.md`** (committed at corridor start; updated as tranches land).

**Rows:** Items / Components / Suppliers / Supplier-items / BOM heads (read-only) / BOM versions (read-only) / BOM lines (read-only) / Planning policy

**Columns:**
- list page exists
- canonical detail page (Path A or Path B; T1 picks one per §3.5.3)
- create available
- edit safe fields (Class S)
- edit warn fields (Class W) with impact preview
- relationship management available
- dependency visibility available (real data, not "not available")
- archive available
- restore available (from archive page)
- mobile usable at 375px
- real persistence verified (saved → reload → still there)
- updated_at + last_modified_by visible (full change-log timeline deferred — see §3.5.5)

Each cell: ✅ DONE / ⚠️ PARTIAL / ❌ MISSING / 🔒 LOCKED-BY-DESIGN / 🚧 CONTRACT-GAP

This matrix is the corridor's contract. A tranche is "done" only when its matrix cells flip to ✅.

---

## 5. Field safety taxonomy (the central design decision)

Every editable field falls into exactly one class.

### Class S — Safe (inline edit)

**Definition:** changing this field has zero impact on stock balances, planning math, ledger integrity, or production traceability. Other entities don't break. Reversible without consequence.

**UX:** click value → input → Enter saves → durable confirmation row. PATCH with `if_match_updated_at`.

**Examples by entity:**

| Entity | Class S fields |
|---|---|
| Item | `item_name`, `family`, `product_group`, `item_type`, `pack_size`, `case_pack` |
| Component | `component_name`, `component_class`, `component_group`, `criticality`, `planned_flag`, `notes` |
| Supplier | `supplier_name_official`, `supplier_name_short`, `supplier_type`, `primary_contact_name`, `primary_contact_phone`, `notes` |
| Supplier-item | (see Class W) |

**Note on supplier-items:** the existing inline-edit on `lead_time_days`, `moq`, `pack_conversion`, `std_cost_per_inv_uom` is already shipped (corridor-7 work). These are Class W by impact, but they were shipped without the warning banner / preview. T6 will add the warning UI without breaking the existing inline-edit interaction (warning appears in a small popover above the inline cell on first edit per session, dismissible).

### Class W — Warn-before-save (drawer with impact preview)

**Definition:** changing this field can cause planning misalignment, supplier mapping breakage, or status downstream effects. Reversible without data corruption, but admin needs to understand impact before saving.

**UX:** "Edit" button or pencil icon → drawer opens with the field, an **impact warning banner**, and (where computable) a **preview of what will change**. Save / Cancel.

**Examples + impact text:**

| Entity.field | Impact warning |
|---|---|
| `item.status`, `component.status`, `supplier.status` toggle | "This will hide the record from active lists and exclude it from planning. Set to INACTIVE = archive." |
| `component.primary_supplier_id` | "Planning will use this supplier's lead time and pricing for purchase recommendations of this component." |
| `component.planning_policy_code` | "Changes safety stock and lot-size logic in the next planning run." |
| `supplier_items.is_primary` (promote) | "This will demote the current primary supplier-item for the same component/item." |
| `supplier_items.std_cost_per_inv_uom` (already done — Class W today) | "Updates the standard cost used in BOM costing rollups." |
| `supplier_items.lead_time_days`, `.moq` | "Affects planning recommendations starting from the next run." |
| `supplier_items.pack_conversion`, `.order_uom` | "Affects how PO quantities are converted to stock units." |
| `supplier.currency` | "Existing prices remain in their original currency. New supplier-items will default to this currency. Don't change mid-flight if PO conversions are in progress." |
| `supplier.default_lead_time_days`, `.default_moq` | "Defaults applied to new supplier-items only; existing rows keep their values." |
| `item.supply_method` | **Strong warning:** "Changes how this item is sourced. MANUFACTURED requires a recipe. BOUGHT_FINISHED requires a supplier-item. REPACK has its own input mapping. Existing recipes/supplier-items may become invalid. Don't change unless the underlying business model changed." |

### Class L — Locked (read-only, "Technical details" section)

**Definition:** editing would break stock truth, ledger integrity, or FK references across the system.

**UX:** displayed inside a collapsed "פרטים טכניים / Technical details" section. Read-only with explanation hover.

| Entity.field | Why locked |
|---|---|
| `item_id`, `component_id`, `supplier_id` (PKs) | Renaming breaks every FK; not changeable, period |
| `component.inventory_uom`, `.purchase_uom`, `.bom_uom` | All historical stock balances are denominated in the current UoM; changing it silently corrupts every balance |
| `component.purchase_to_inv_factor` | Same — historical PO-to-stock conversions assumed this factor |
| `supplier_items.inventory_uom` | Same. **Note:** `supplier_items.order_uom` is **not** locked — it's a per-supplier order-pack UoM, not a stock UoM, and is Class W. |
| `bom_head_id`, `bom_version_id` | Identifier immutability |
| `bom_lines.line_id` for ACTIVE / SUPERSEDED versions | Production traceability. **DRAFT versions allow line edits via the Slice B BOM workflow** — not in this corridor. |
| Audit columns: `created_at`, `updated_at`, `change_log` references | Append-only audit |
| `site_id` | Multi-site mode is not in v1 scope; lock until a multi-site corridor exists. |

**Important note about Path A's existing inline-edits on Class L fields:** the older `/admin/components/[id]/page.tsx` page currently inline-edits `inventory_uom`, `purchase_uom`, `bom_uom`. These edits are dangerous (see §3.5.3 dual-tree resolution). T1 must remove these inline-edit handlers from Path A — either by deprecating Path A entirely (Option 1) or by replacing the inputs with locked displays (Option 2). **No mid-corridor compromise on Class L.**

### Class C — Custom workflow (deferred to other slices)

| Field | Slice |
|---|---|
| `item.primary_bom_head_id`, `.base_bom_head_id` (re-link recipe) | Slice B (BOM corridor) — for now: lock with hint "Use the recipe workflow to change recipe linkage" |
| BOM head/version/line direct editing | Slice B |
| Hard delete | Slice D |

---

## 6. Archive mechanism

**Decision:** reuse existing `status` enum. No schema change.

| status | Meaning | Visible in default lists? | Included in planning? |
|---|---|---|---|
| `ACTIVE` | In use | ✅ Yes | ✅ Yes |
| `PENDING` | Under review, not yet activated | ⚠️ Yes (with badge) | ❌ No |
| `INACTIVE` | **Archived** | ❌ No (hidden) | ❌ No |

**Restore = POST `/api/[entity]/:id/status` with `{status: "ACTIVE", if_match_updated_at, idempotency_key}`.** No new endpoint needed.

**Effect on `change_log` append-only guard:** the trigger only forbids UPDATE/DELETE on the change_log table itself; status changes write status events as new rows, which is its append-only invariant. Cycling INACTIVE ↔ ACTIVE produces multiple log rows. T1 should add a smoke-test fixture: archive → restore → archive → confirm change_log has 3 status events and the row's final state is INACTIVE.

### Pre-archive guards

Before allowing `status → INACTIVE`, run a dependency precheck:

| Entity | Blocked when |
|---|---|
| Component | used in any **ACTIVE** BOM version's lines (DRAFT does not block — it can be discarded). Needs Contract Gap #1 (gate-mode query: ACTIVE only). |
| Item | has any ACTIVE BOM version with non-empty lines |
| Item | is referenced in any open PO line (`status` IN ('OPEN','PARTIAL')) |
| Supplier | has any supplier-items with status ACTIVE **on a non-archived component/item** (don't block winding down a supplier whose only ties are to records you've already archived — see §6.1 below) |
| Supplier | has open POs |
| Supplier-item | is the primary for an ACTIVE component/item |

**UX when blocked:**
> "Can't archive yet. This raw material is used in 3 active recipes. Open a recipe or substitute the material before archiving."

with links to the blocking dependencies.

**No override in this corridor.** Override = hard-delete = Slice D.

### 6.1 Edge case: winding down a supplier

Scenario: supplier SUP-X has 5 supplier_items, but the components they map to are all already INACTIVE (archived). Today's gate "any supplier-items with status ACTIVE" would block this supplier from being archived even though nothing operationally depends on it.

**Rule:** the gate joins through to the parent entity's status. Supplier archive is blocked only when at least one of its supplier-items maps to an **ACTIVE** component or item. If all linked components/items are INACTIVE, supplier archive proceeds (and the dangling supplier-items are not archived — they remain in their existing state, which is fine because their parents are already archived too).

T1's matrix must capture this rule explicitly so the gate logic is implemented once.

### 6.2 Bulk archive

**Out of scope for this corridor.** Tom may want "archive 14 stale components" in the future. That's a separate UX (multi-select on list pages + bulk action bar). Document as a follow-up; do not build now.

### Archive page

New page: `/admin/masters/archive`

- Tabs by type: Items / Components / Suppliers / Supplier-items
- Each tab: filtered list `WHERE status = 'INACTIVE'`
- Per row: name, code, status badge, archived_at (from `updated_at`), [Restore] button (admin only — see §9.6)
- Restore opens a confirmation: "Set this record back to ACTIVE? It will reappear in active lists and may be included in the next planning run."
- Restore is a status toggle: **POST** `/api/[entity]/:id/status` with `{status: "ACTIVE", ...}` (per §3.5.2 — not PATCH)
- **Read-only role rendering (planner/viewer):** the [Restore] button is hidden entirely. The list is visible (so they can see what's been archived) but no actions appear.

Nav entry under Admin: "Archive" (icon: `Archive` from lucide).

**Orphan supplier-items handling (per §6.1 edge case):** the supplier-items archive tab includes rows where the supplier is INACTIVE but the supplier-item itself is still ACTIVE (orphans created when a supplier is archived without archiving every linked supplier-item). These rows display with a small "orphan — parent supplier archived" badge and a one-click "Archive this too" button. The active supplier-items list (`/admin/supplier-items`) hides these orphans by default (filter joins through to supplier status); a toggle "Show orphans" reveals them.

---

## 7. Dependency visibility

This is the heart of "edit safely." Before any edit, the admin sees what depends on this record.

### 7.1 Component detail — "Used in recipes" tab (currently broken — P0 fix)

**Current state:** the tab shows `PendingTabPlaceholder` saying "BOM usage lookup is not yet available here." This is a **false-green / dead-end card**.

**Target state:** the tab shows real data:

| Recipe (parent name) | Code | Version | Status | Qty / L output | UoM | |
|---|---|---|---|---|---|---|
| Base Americano Regular | BASE-AME-REG | V4_COST_FILE | ACTIVE | 0.0042 | UNIT | [Open] |
| Base Calmer NS | BASE-CAL-NS | V4_USER_LOCK | ACTIVE | 0.0035 | UNIT | [Open] |
| (Draft on Base Americano) | BASE-AME-REG | DRAFT-2026-04-22 | DRAFT | 0.0042 | UNIT | [Open draft] |

Plus: count badge in tab label ("Used in recipes (14)"), warning copy if count > 0:

> "This raw material is used in **14 active recipes**. Changes affect production planning. Open a recipe before modifying."

**Backend gap (Contract Gap #1):** `/api/boms/lines` requires `bom_version_id`; no filter by `final_component_id`. New endpoint needed.

```
GET /api/components/:component_id/used-in-recipes?mode=ui|gate

Query params:
  mode = "ui"   → returns ACTIVE + DRAFT versions (for visibility tab)
  mode = "gate" → returns ACTIVE only (for archive precheck)

Response 200:
{
  "rows": [
    {
      "bom_head_id": "BOM-BASE-AME-REG",
      "parent_ref_id": "BASE-AME-REG",
      "parent_ref_type": "component",  // or "item"
      "parent_name": "Base Americano Regular",  // resolved server-side
      "bom_version_id": "uuid",
      "version_label": "V4_COST_FILE",
      "version_status": "ACTIVE",  // or DRAFT
      "line_id": "uuid",
      "qty_per_l_output": "0.0042",
      "component_uom": "UNIT"
    }
  ],
  "count": 14,
  "active_count": 12,
  "draft_count": 2  // omitted in gate mode
}
```

**SQL (UI mode):**
```sql
SELECT bh.bom_head_id, bh.parent_ref_id, bh.parent_ref_type,
       COALESCE(i.item_name, c.component_name) AS parent_name,
       bv.bom_version_id, bv.version_label, bv.status AS version_status,
       bl.line_id, bl.qty_per_l_output, bl.component_uom
FROM private_core.bom_lines bl
JOIN private_core.bom_version bv ON bv.bom_version_id = bl.bom_version_id
JOIN private_core.bom_head  bh ON bh.bom_head_id = bv.bom_head_id
LEFT JOIN private_core.items i
  ON bh.parent_ref_type = 'item' AND i.item_id = bh.parent_ref_id
LEFT JOIN private_core.components c
  ON bh.parent_ref_type = 'component' AND c.component_id = bh.parent_ref_id
WHERE bl.final_component_id = :component_id
  AND bv.status IN ('ACTIVE','DRAFT')
ORDER BY bv.status, bh.parent_ref_id;
```

For **gate mode**, change the `IN` clause to `bv.status = 'ACTIVE'` and drop the `draft_count` field from the response.

The polymorphic `parent_name` resolution (LEFT JOIN both items and components, COALESCE) is mandatory — the response promises a name, and clients MUST NOT have to do a second-round lookup.

**RBAC:** admin / planner / viewer (read-only on this endpoint).

**If the backend isn't extended in time:** the portal **must not** ship the tab as "not available." Two acceptable fallbacks:

1. **Client-side aggregation** (the v1 default if backend slips):
   - Fetch all `bom_heads` once (cached 60s).
   - For each head with `active_version_id` set, fetch `/api/boms/lines?bom_version_id=X`.
   - Use TanStack Query parallel mode with **max 6 concurrent fetches** (browser limit), **8s timeout per fetch**, **partial-load tolerance** (show what loaded with a "[N sections failed to load]" warning).
   - **Hard fail** when active BOM count > 50 — at that scale client-side aggregation is no longer acceptable; show a yellow banner with the contract-gap explanation and a link to the backend ticket.
   - DRAFT versions: skip entirely in the fallback (would require a separate `/api/boms/versions?bom_head_id=X&status=DRAFT` round-trip per head, doubling the cost). In fallback mode the table renders with **no DRAFT column header at all** (do not show empty/placeholder draft columns) and the section title becomes "Recipes (active versions only)". When the real backend endpoint lands, the swap re-adds the column header.
   - Cache the result keyed by `component_id` for 60 seconds.

2. **Yellow contract-gap banner** when fallback can't run (>50 active BOMs): "This view depends on a backend lookup that's being built. Tracking ticket: [link]." — only acceptable if the ticket exists.

**Decision for this corridor:** ship the new backend endpoint as a contract-handoff to the backend window. Portal ships fallback #1 first to unblock T3. Switch to the real endpoint when the backend lands; the swap is a one-line change in the React Query hook.

### 7.2 Component detail — Suppliers section

Already exists in this session's work (`/admin/masters/components/[component_id]` supplier-items tab). Keep + add:
- Summary card "N suppliers, primary: [name]" or "❌ No suppliers"
- Action: "+ Add supplier" already wired to `QuickCreateSupplierItem` with `defaultComponentId` pre-fill ✓

### 7.3 Item detail — Recipe completeness verification

For MANUFACTURED / REPACK items, the admin needs to see:
- Pack BOM lines (what's in the package: bottle, cap, label, base reference)
- Base BOM lines (the formula: ingredients)
- **Verification flag: is the active pack version actually referencing the base?**

For BOUGHT_FINISHED items:
- Suppliers (already exists)

**Summary card flag:**
- ✅ "Recipe is complete" (active pack version exists, lines exist, references base if applicable)
- ⚠️ "Pack recipe exists but no base linked" (pack has no reference to a base BOM)
- ❌ "No active recipe" (no `primary_bom_head_id` or no active version)
- ❌ "No supplier" (BOUGHT_FINISHED only)

**Computation (client-side from existing endpoints):**
1. From `/api/items?limit=1000`, get the row → read `primary_bom_head_id` (pack), `base_bom_head_id` (base).
2. If `primary_bom_head_id` is null → "❌ No active recipe."
3. From `/api/boms/heads?limit=1000`, get the pack head → read `active_version_id`.
4. If pack `active_version_id` is null → "❌ No active recipe."
5. From `/api/boms/lines?bom_version_id=<pack active>`, count rows.
6. If count = 0 → "❌ Active recipe is empty."
7. **Pack-references-base check (verify before relying on this rule):** scan the pack's lines for any line whose `final_component_id` equals the `parent_ref_id` of the row in `bom_head` whose `bom_head_id` = `item.base_bom_head_id` (i.e. the base item/component the base BOM produces). If the item has a `base_bom_head_id` but no pack line references it → "⚠️ Pack recipe exists but no base linked."
   - **Caveat:** the BOM model in this codebase represents pack→base linkage in a way that hasn't been confirmed against a fixture in this spec. T5 must validate against at least 3 real items (one MANUFACTURED with base, one REPACK, one MANUFACTURED without base) before the ✅ flag is shown. **A wrong "✅ Recipe is complete" is worse than no flag** — if the rule can't be confirmed in T5, ship as ⚠️ "Recipe completeness check unavailable" with a link to the recipe rather than a misleading green.
8. Otherwise → "✅ Recipe is complete."

For BOUGHT_FINISHED: skip steps 2-7; check `/api/supplier-items?item_id=X` count + primary status. No backend gap.

### 7.4 Supplier detail — Items supplied + Components sourced

Already exists. Add to summary card: "N items supplied", "Primary supplier of N items", "M open POs", "Default lead time / payment terms / currency."

### 7.5 Supplier-items list — Source page (already mostly done)

Existing inline edits on cost / lead / MOQ stay. Add archive flow per row.

---

## 8. UX patterns (cross-cutting simplification)

### 8.1 Summary card (top of every detail page)

```
┌──────────────────────────────────────────────────────────────┐
│ [Status: ACTIVE]   [Type badge]                              │
│ Bareket Tea Bags 100/250                                     │ ← name large
│ COMP-BARE-TEA-100  ·  Raw material                           │ ← code mono + entity type
│                                                              │
│ Completeness:                                                │
│   ✅ Primary supplier: Bareket Tea Co. (SUP-BARE)           │
│   ⚠️  Used in 14 active recipes                              │
│   ✅ Standard cost set: 12.50 ILS / KG                       │
│                                                              │
│ Next actions:  [Edit details]  [Open recipes]  [Add supplier]│
└──────────────────────────────────────────────────────────────┘
```

Implementation: a new shared component `<MasterSummaryCard />` consumed by Item / Component / Supplier / Supplier-item detail pages. Per-entity adapter computes the completeness checks.

Completeness rules per entity:

**Component**
- Primary supplier set ✅/❌
- Standard cost set (latest supplier-item.std_cost_per_inv_uom) ✅/❌
- Used-in-recipes count + warning (⚠️ if > 0, info if = 0)
- Status (ACTIVE/PENDING/INACTIVE)

**Item (MANUFACTURED/REPACK)**
- Active pack recipe ✅/❌
- Active base recipe (where applicable) ✅/❌
- Pack-references-base verification ✅/❌/N/A
- Status

**Item (BOUGHT_FINISHED)**
- Has at least one supplier-item ✅/❌
- Primary supplier-item ✅/❌
- Standard cost on primary ✅/❌
- Status

**Supplier**
- Has supplier-items ✅/❌
- Default currency / payment_terms / lead_time set ✅/⚠️
- Open POs count
- Open exceptions count

### 8.2 Field display order (information architecture)

Top → bottom on every detail page:
1. **Summary card** (status + completeness + next actions)
2. **Identity** — Name, Code, Status (Class S inline edit, Class W status drawer)
3. **Operational** — the safe fields admins edit most (Class S inline, grid layout)
4. **Relationships** — sections for suppliers / recipes / etc. with manage buttons
5. **Lifecycle** — Created, Last updated, history (read-only)
6. **Technical details** — collapsed by default — IDs, FK references, raw enum values, locked Class L fields with explanation

Tabs become sections only when justified (multiple distinct datasets like Recipes / Suppliers / POs / Exceptions). No tab is allowed to ship saying "not available."

### 8.3 Edit interaction patterns

**Inline edit cell (Class S):**
```
[ Bareket Tea Bags 100/250 ] ✏️    ← click to edit
```
Click → input field, Enter saves, Esc cancels. After save: small "Saved 2s ago" indicator, then fades.

**Concurrency + idempotency on inline edits:**
- Inline saves use the `updated_at` from the latest TanStack Query cache fetch (typically <60s old). Acceptable staleness for fast edits.
- Each save generates a fresh `idempotency_key`. On auto-retry of the same save (network blip), reuse the key.
- 409 → revert to the previous value, show tooltip "Changed by someone else — refreshing", re-fetch the row.

**Edit drawer (Class W):**
```
[Edit primary supplier ▾]
```
Click → drawer slides in with:
- Field input
- Yellow banner: "Changing the primary supplier affects planning..."
- Preview (when computable): "Current: SUP-BARE, lead 7d. New: SUP-OFR, lead 14d. Next planning run will use the new values."
- [Cancel] [Save change]

**Drawer concurrency rules (mandatory):**
- On drawer open: re-fetch the row (don't trust the page's cached `updated_at` — minutes may have passed since page load). Use `staleTime: 0` for the read on drawer open.
- Generate a fresh `idempotency_key` (UUID v4) on save click; if the user retries after a network error, reuse the same key for that one logical save attempt.
- On 409 conflict response: replace the drawer body with: "This record was changed by someone else while you had it open. [Reload and edit again]." — do NOT silently overwrite. The reload button re-fetches the row, recomputes the diff, and reopens the drawer with the latest values; the user re-applies their change manually.
- On any other error: keep the drawer open, show error inline, allow retry (which generates a new idempotency key).

**Status toggle (Class W special):**
```
[ Active ▾ ]   ← click
```
Opens dialog:
> "Change status from Active to Inactive (archive)?
> This will hide it from active lists and exclude it from planning.
>
> ⚠️ Used in 14 active recipes. Archive is **blocked** until the recipes no longer reference it."

When blocked: only [Close] button.
When clear: [Cancel] [Archive] buttons.

### 8.4 Mobile (375px) requirements

- Summary card: stacks vertically, full width
- Identity / Operational: single-column field grid, labels on top of values
- Inline edit: tap → native input → done button
- Tables → cards on screens <640px (already a design system primitive in the codebase)
- Action buttons: full-width primary first, secondary as icon menu
- No horizontal scroll for the main edit/action

### 8.5 Language

UI is **English-first** (per CLAUDE.md). Hebrew labels appear as:
- Tooltips / sub-labels
- Warning copy for operational concepts (Tom's exact strings translated where relevant)

Forbidden as primary labels:
- `item_id`, `component_id`, `supplier_id`, `bom_head_id`, `bom_version_id`, `bom_lines`, `supplier_items` (table names)
- `mutation`, `route`, `API`, `endpoint`
- Raw enum values (e.g. show "Manufactured" not `MANUFACTURED`; the `fmtSupplyMethod` helper already does this)

Required as primary labels:
- "Item code" / "Code" / "SKU" (not item_id)
- "Raw material" / "Packaging" (not component)
- "Recipe" / "Production recipe" (not BOM)
- "Active recipe" / "Draft recipe" / "Previous recipe" (not version)
- "Primary supplier" (not is_primary)
- "Used in recipes" (not bom_lines references)
- "Archived" (not INACTIVE in status filter UI)

### 8.6 Error / empty / loading states

Every section that fetches data:
- **Loading:** shimmer / spinner with "Loading [thing]…"
- **Error:** "Could not load [thing] — [reason]. [Retry]"
- **Empty:** the operational copy from Tom's spec, e.g. "This raw material is not currently used in any recipe."
- **Partial:** when one of N parallel queries fails, show what loaded + a small "[1 section failed to load]" warning, not a hard error

---

## 9. Backend contract gaps (handoff specs)

### Contract Gap #1: Components-used-in-recipes lookup

**Endpoint:** `GET /api/v1/queries/components/:component_id/used-in-recipes`
**Auth:** admin / planner / viewer (read-only)
**Status filter:** ACTIVE + DRAFT (skip SUPERSEDED to keep response focused)
**Response:** as in §7.1 above
**SQL:** as in §7.1 above

Owned by: backend (W1). Window 2 portal will consume.

### Contract Gap #2: Pre-archive dependency precheck (optional, can be client-side)

For v1, computed client-side by aggregating existing endpoints + Contract Gap #1.

If volumes grow, a server-side endpoint becomes warranted:
`GET /api/v1/queries/[entity]/:id/archive-precheck` returning `{ blocked: boolean, reasons: [...] }`.

### Contract Gap #3: Audit history visibility — **deferred to a later corridor** (see §3.5.5)

The `change_log` table exists. To surface "last edited by user X at time Y" on detail pages, the API would expose:
`GET /api/v1/queries/change-log?entity_type=[items|components|suppliers]&entity_id=:id&limit=10`

This corridor surfaces only the existing `updated_at` and any `*_by_snapshot` columns the API already returns. The full change-log timeline is **not** a corridor-exit criterion.

---

## 9.5 Create flow (existing)

All four Quick-Create drawers already ship at `src/components/admin/quick-create/`:
- `<QuickCreateComponent>` — humanized in corridor-7 ✓
- `<QuickCreateSupplier>` — humanized in corridor-7 ✓
- `<QuickCreateSupplierItem>` — humanized in corridor-7 ✓ (with `defaultSupplierId` / `defaultComponentId` / `defaultItemId` prefill props)
- `<QuickCreateItem>` — **exists but ships with DB-style labels and a minimal field set** (`item_id`, `item_name`, `supply_method`, `sales_uom`)

**T2's create-flow deliverable** is therefore an *extension*, not a build:
1. Humanize labels (Item code, Name, Supply method, Sales unit, Family, Case pack)
2. Add fields to match the corridor's "minimum complete record" target: `family`, `case_pack`
3. Default `status: PENDING` so newly created items land in PENDING and have to be deliberately activated (so a half-configured product doesn't immediately appear in active planning)
4. Add a post-create info banner: "Created [name]. Open the detail page to set up the recipe and supplier before activating."

The matrix's "Create available" column is ✅ for all four entities (drawers exist); the "matches the editability standard" sub-criterion is the bar T2 must meet.

---

## 9.6 RBAC matrix (per action)

The portal already exposes `useSession()` with `session.role`. Roles are: `admin`, `planner`, `operator`, `viewer`.

| Action | admin | planner | operator | viewer |
|---|---|---|---|---|
| Read any master detail page | ✅ | ✅ | ✅ | ✅ |
| Inline-edit Class S field | ✅ | ❌ | ❌ | ❌ |
| Edit Class W field (via drawer) | ✅ | ❌ | ❌ | ❌ |
| Toggle status (archive / restore) | ✅ | ❌ | ❌ | ❌ |
| Promote primary supplier-item | ✅ | ❌ | ❌ | ❌ |
| Create master record | ✅ | ❌ | ❌ | ❌ |
| Open BOM workflow (Slice B — read-only here) | ✅ | ✅ | ❌ | ✅ (read) |
| View archive page | ✅ | ✅ | ❌ | ✅ (read) |
| Restore from archive | ✅ | ❌ | ❌ | ❌ |

In the UI, action affordances (buttons, edit pencils) are hidden when not allowed. The page's existing `useSession()` + `session.role === "admin"` gate (already in `/admin/components/page.tsx`) is the pattern to extend.

---

## 10. Implementation tranches (ordered)

| # | Tranche | Output | Depends on |
|---|---|---|---|
| T1 | Audit + Editability matrix + **dual-tree resolution decision** (§3.5.3) | `master-editability-matrix.md` committed; chosen Path (A or B) per entity; baseline of every cell | — |
| T2 | Canonical component detail: summary card + Class S inline + Class W drawer + Class L "Technical details" + new `<QuickCreateItem>` | New patterns shipped on highest-traffic admin page; old Path is redirected or has Class L inline-edits removed | T1 |
| T3 | Component detail: dependency visibility (Used in recipes) + archive guard | Contract Gap #1 spec emitted; portal consumes once available; client-side fallback if not | T2 + backend |
| T4 | Supplier detail: same patterns | Mirror T2 | T2 patterns |
| T5 | Item detail: same patterns + recipe completeness verification flag | Mirror T2 + recipe-readiness check | T2, T3 |
| T6 | Supplier-items list: warning UX on existing inline edits + archive flow | Already partial; add warning popover for Class W inline cells | T2 |
| T7 | Archive page at `/admin/masters/archive` + nav entry + restore flow | New page across entity types | T2-T6 |
| T8 | Cross-cutting validation pass | Mobile, persistence, language, empty/error/loading, concurrency, RBAC audits across every touched page | All |

**Each tranche ends with:**
- Matrix cells flipped to ✅
- TypeScript clean
- Build green
- Manual smoke: edit → reload → still saved
- Mobile: 375px screenshot pass

---

## 11. Validation checklist (the corridor's "done")

A non-technical admin must be able to:
- [ ] Open any master record and understand state at a glance (summary card)
- [ ] See what depends on the record (real data, not "not available")
- [ ] Edit safe fields with one click + Enter (Class S)
- [ ] Edit risky fields with a clear impact warning (Class W)
- [ ] See locked fields with an explanation, not silently fail
- [ ] Archive a record when safe; see a clear reason when blocked
- [ ] Restore a record from the archive page
- [ ] Create a new record of every entity (item / component / supplier / supplier-item) from the portal
- [ ] Do all of the above on mobile (375px)
- [ ] Trust that any save persisted (reload still shows it)
- [ ] Never see raw DB column names as primary UI
- [ ] Get a clear "this record changed under you, reload" message instead of silent overwrite on concurrent edits

…all without DevTools, SQL, or asking Claude.

---

## 12. Risks + mitigations

| Risk | Mitigation |
|---|---|
| Contract Gap #1 not delivered → "Used in recipes" stays broken | Client-side aggregation fallback shipped first; spec emitted to backend immediately |
| Admin clicks Edit on Class L field expecting it to work | Move all Class L fields into a collapsed "Technical details" section with explanation |
| Admin archives a record that's actively in use | Pre-archive guard with dependency check; no override in this corridor |
| Admin changes `supply_method` on an item with active recipe linked → recipe orphans | Strong warning in drawer + prevent the change when active recipe exists; show "Substitute or archive recipe first" |
| Page becomes a maze again with new sections | Strict information architecture in §8.2; tabs only when justified; section card pattern reused |
| Mobile regression on existing pages | Validation tranche T8 hits every touched page at 375px |

---

## 13. Out-of-scope reminders (Slice B / D / planning)

- Recipe (BOM) line editing UX — Slice B
- Hard-delete with override — Slice D
- Production quantity calculator by finished product — planning corridor
- New schema migrations — none in this corridor
- Backend implementation of Contract Gap #1 — handed off to backend window
