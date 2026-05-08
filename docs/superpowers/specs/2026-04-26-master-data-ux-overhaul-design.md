# Master Data UX Overhaul — Design Spec
**Date:** 2026-04-26
**Approach:** Big Bang / Parallel Streams (Approach C)
**Scope:** Production Simulation redesign + systemic UX cleanup across the entire GT Factory OS portal

---

## Context

The portal has accumulated several UX problems across master data admin pages and planning screens:
- Internal technical IDs exposed as page titles and labels
- No clear edit affordance on many pages
- Cross-entity navigation is broken or missing
- BOM Simulation operates on individual BOMs rather than whole products
- Excessive decimal precision throughout
- No breadcrumbs or back navigation in detail panels

This spec covers all five parallel streams of work to fix these issues in a single coordinated release.

---

## Global Design Principle

> **Admin pages:** technical detail is acceptable (IDs visible in sub-text, version codes in URL).
> **All other portal pages (operator, planning, simulation, dashboard):** plain business language only. Zero internal codes. Zero technical jargon. UX must match the vocabulary of daily factory work.

---

## Stream 1 — Production Simulation

### Problem
The current "BOM simulation" page selects by individual BOM head (either PACK or BASE), so a user simulating production of American 0.5L must run two separate simulations — one for liquid ingredients, one for packaging. The simulator also omits the BASE MIX component from the results even when it is present as a BOM line.

### Required data model changes (prerequisite for Stream 1)

`ItemDto` currently has only `active_bom_id?: string`. This must be extended:

```ts
// contracts/dto.ts — ItemDto additions
primary_bom_head_id?: string   // PACK BOM (packaging components)
base_bom_head_id?: string      // BASE BOM (liquid/ingredient components)
```

The API and repository layer must expose both fields. The DB schema equivalent fields must also be confirmed or added. This is a required prerequisite — Stream 1 cannot be built without both fields populated.

**Supply method enum clarification:** The portal currently uses `["MAKE", "BOUGHT_FINISHED"]` (not `MANUFACTURED`/`REPACK`). All references in this stream use `MAKE` as the value for manufactured/produced items. The product selector filters to items with `supply_method === "MAKE"`.

### Design

**Page:** New page — `/app/(planner)/planner/production-simulation/page.tsx` (does not currently exist; must be created).

**Page title:** `Production simulation`
**Description:** `Select a product to simulate production quantities and check material coverage.`

**Product selector:**
- Dropdown lists `MAKE` items only that have at least one active BOM (`primary_bom_head_id` OR `base_bom_head_id` is set and active)
- Label: "Select a product" (not "Select a BOM")
- Button after selection: "Change product"

**On product selection — data fetched:**
- `primary_bom_head_id` → PACK BOM lines (packaging components); fetch active version lines
- `base_bom_head_id` → BASE BOM lines (liquid/ingredient components); fetch active version lines
- Both merged into a single component list, tagged by source

**Edge case — product has PACK BOM but no BASE BOM:**
- Render only PACK rows
- Show notice above table: "No liquid recipe linked to this product. Showing packaging components only."

**Edge case — product has BASE BOM but no PACK BOM:**
- Render only BASE rows
- Show notice: "No packaging recipe linked. Showing liquid components only."

**Results table columns:**

| # | COMPONENT | TYPE | QTY PER UNIT | REQUIRED QTY | UNIT |
|---|-----------|------|-------------|-------------|------|
| 1 | American Base Mix | BASE | 0.500 | 50.000 | L |
| 2 | Dark Glass Bottle 500ml | PACK | 1 | 100 | UNIT |
| 3 | Black Cap 28mm | PACK | 1 | 100 | UNIT |
| 4 | Label American 0.5L | PACK | 1 | 100 | UNIT |
| 5 | Cardboard Box 500ml | PACK | 0.167 | 16.7 | UNIT |

**TYPE column:** `BASE` (blue badge) or `PACK` (gray badge). Rows sortable/groupable by type.

**Formula display:** `required = target × qty_per_unit` — no `base_output_qty` complexity shown.

**Decimal precision:** follows Stream 5 rules (L → 3dp, UNIT → 0dp).

**Internal IDs removed:** No `VV4_PACK_RULE`, no `BOM-PACK-AME-500ML`, no `PKG-*` codes in any visible UI element.

**Stock coverage panel:** unchanged — remains as the secondary panel below the results table, showing current stock vs. required qty per component.

---

## Stream 2 — Naming & Labels

### Problem
Page titles, badges, and panel headings expose internal technical codes (e.g., `BOM vV4_PACK_RULE`, `BOM-PACK-AME-500ML`, `FG-AME-500ML`, `PKG-BOTTLE-500ML`). BOM versions have only numeric names (v1, v2).

### Design

**BOM version page title:**
- Before: `BOM vV4_PACK_RULE`
- After: `American 0.5L — Pack Recipe` with `ACTIVE` status badge

**BOM version name field (on create/edit):**
- New optional text field: "Version name" (e.g., "Initial release", "Post supplier change Q2 2026")
- If blank: display as `Version 1`, `Version 2` (not raw `v1`, `v2`)

**Right panel "LINKED" section:**
- `LINKED: BOM head` → `Pack recipe`
- `LINKED: Linked item` → `Finished product`

**IDs removed from all visible UI:**
- `BOM-PACK-AME-500ML` — not shown to user (kept in URL only)
- `FG-AME-500ML` — not shown
- `PKG-BOTTLE-500ML`, `PKG-CAP-*`, `PKG-LABEL-*` — not shown beneath component names
- `VV4_PACK_RULE` badge in simulation tab — removed

**`MANUFACTURED` badge on Pack BOM page:** removed (misleading; the item's supply method badge belongs on the item page, not the BOM version page).

**Scope:** applies to BOM admin pages. On non-admin pages (planning, simulation, operator forms), zero technical codes or IDs may appear anywhere — this is a hard rule.

---

## Stream 3 — Edit Discoverability + Supplier Assignment

### Problem
It is unclear which fields are editable and how to initiate editing. Changing the primary supplier for a component has no discoverable path.

### Design

**Universal edit pattern for all admin detail panels:**
- Every detail panel has a visible `Edit` button in the panel header (top-right)
- Clicking `Edit` switches the panel to edit mode (fields become inputs)
- Edit mode shows `Save` (primary) and `Cancel` (secondary) in `FormActionsBar`
- Read-only mode is the default; edit mode is explicit opt-in

**BOM version state actions:**
- Active version: prominent `Create new draft` button (replaces needing to discover the versioning flow)
- Draft version: `Edit lines` button visible + `Publish` button when ready
- Retired version: read-only, no actions

**Changing supplier for a component:**
- Component detail panel: dedicated section "Primary supplier"
- Displays current supplier name (if set) with a `Change` button beside it
- `Change` opens a supplier picker (searchable dropdown of existing suppliers)
- **On save — write semantics:** soft-delete the existing `supplier_items` row (set `archived_at`) and insert a new row with the new supplier. This preserves audit history. Do not update the existing row in place.
- If no supplier set: shows "No supplier assigned" with `Assign supplier` button (creates new `supplier_items` row)

---

## Stream 4 — Cross-Entity Navigation

### Problem
"Used in recipes" is non-functional for components. Navigation between related entities (BOM line → component, component → supplier, supplier → components) does not exist.

### Design

**Component detail panel — "Used in" section:**
- New section: `Used in X products`
- Lists each finished good that references this component in any active BOM line
- Each row shows: product name + qty per unit + UOM
- Each row is clickable → navigates to that product's BOM detail page
- If used in 0 products: shows "Not used in any active recipe"

**BOM lines table — component name as link:**
- Component name column: rendered as a clickable link (blue, underlined on hover)
- Click → opens component detail panel (or navigates to component page)
- Applies in: BOM version detail page, Production simulation results table

**Component detail panel — supplier link:**
- "Primary supplier" section: supplier name is a clickable link → navigates to supplier detail page

**Supplier detail page — "Components supplied" section:**
- New section listing all components where this supplier is `primary_supplier`
- Each component name is a clickable link → navigates to component detail

**Supplier-items page — bidirectional links:**
- Supplier name column: clickable → supplier detail
- Component name column: clickable → component detail

**Implementation notes:**
- All cross-entity links open in the same tab (no new tabs)
- Links use the existing split-panel pattern where applicable; full page navigation where not
- "Used in" data is computed at page load from `bom_lines` JOIN `bom_versions` WHERE status = 'active'
- **When a component appears in both BASE and PACK BOMs of the same product:** show two rows, one per BOM type, each with its own qty and UOM. Label each row with the BOM type (BASE / PACK) so the user understands the context. Do not collapse or sum across types.

---

## Stream 5 — Decimal Precision + Breadcrumbs + Navigation

### Problem
Numbers display with 6–8 decimal places throughout. No breadcrumbs in detail panels. Back navigation is unreliable.

### Design

**Universal decimal precision rules (applied everywhere in the portal):**

| UOM type | Max decimal places | Example |
|----------|--------------------|---------|
| L, ml (liquid volume) | 3 | `0.500 L` |
| kg, g (weight) | 3 | `0.025 kg` |
| UNIT, PCS (discrete) | 0 | `100 UNIT` |
| % (percentage) | 1 | `98.5%` |
| Price / cost (ILS) | 2 | `₪12.50` |
| Ratio / conversion factor | 4 | `0.1667` |

Hard rule: **no number in the portal UI may show more than 4 decimal places**, regardless of stored precision.

**Breadcrumbs — all detail pages and deep panels:**
- Format: `Admin › BOMs › American 0.5L › Pack Recipe`
- Each segment is a clickable link to that level
- **Placement in split-panel pages:** breadcrumb renders inside the detail panel header, above the panel title — not as a page-level element. On full-page sub-routes (e.g., BOM version detail page), breadcrumb renders at the top of the page content area.
- Applies to: all `/admin/*` sub-pages, BOM version pages, and any detail page more than 1 level deep

**Back navigation:**
- Every detail page and deep panel has a `← Back` button in the top-left (or top of panel)
- `← Back` returns to the parent list (not browser history — explicit target)
- ESC key closes any open detail panel
- Browser back button does not break application state (URL reflects panel state)

---

## Affected Files (approximate)

**Stream 1:**
- `/app/(planner)/planner/production-simulation/page.tsx` — **new file** (page does not currently exist)
- `/lib/contracts/dto.ts` — add `primary_bom_head_id` and `base_bom_head_id` to `ItemDto`
- `/lib/repositories/boms-repo.ts` — add product-level BOM fetch (BASE + PACK by item)
- DB schema — confirm or add `primary_bom_head_id` / `base_bom_head_id` columns on items table

**Stream 2:**
- `/app/(admin)/admin/boms/[id]/page.tsx` — title, badges, linked panel labels
- `/app/(admin)/admin/boms/page.tsx` — list display cleanup
- All planning/operator pages — remove any internal ID display

**Stream 3:**
- `/app/(admin)/admin/components/page.tsx` — add Edit button, supplier section
- `/app/(admin)/admin/boms/[id]/page.tsx` — add Create new draft / Edit lines / Publish buttons
- All admin detail panels — add universal Edit button pattern

**Stream 4:**
- `/app/(admin)/admin/components/page.tsx` — add "Used in" section
- `/app/(admin)/admin/boms/[id]/page.tsx` — component names as links
- `/app/(admin)/admin/suppliers/page.tsx` — add "Components supplied" section
- `/app/(admin)/admin/supplier-items/page.tsx` — bidirectional links

**Stream 5:**
- `/lib/utils/format.ts` (or equivalent) — centralized number formatting utility
- All pages/components displaying numeric values — apply formatting utility
- All admin detail pages — add breadcrumbs component
- All split-panel layouts — add back button + ESC handler

---

## Success Criteria

1. Production simulation selects by product and shows BASE + PACK lines combined, with TYPE badge per row
2. Zero internal codes (BOM-*, PKG-*, FG-*, version codes) visible on any non-admin page
3. BOM version pages display human-readable titles and linked panel labels
4. Every admin detail panel has a visible Edit button
5. "Change supplier" is findable within 2 clicks from any component
6. "Used in X products" is populated and clickable for every component
7. BOM line component names are clickable links
8. No number in the portal shows more than 4 decimal places
9. All deep detail pages have breadcrumbs and a Back button
10. ESC closes panels
