# Inventory Flow — Hide / Focus / Reset rows

**Date:** 2026-06-18
**Surface:** `/planning/inventory-flow` (portal — `window2-portal-sandbox`)
**Author:** Claude (brainstormed with Tom, approved 2026-06-18)
**Type:** Portal-only, client-side. No backend, no API, no DB, no migration.

---

## Problem

Tom wants to declutter the Inventory Flow grid so he can focus. He needs to:
1. Hide individual product rows (dismiss ones he has already handled / does not care about today).
2. Isolate a handful of rows out of 60+ (focus mode).
3. Bring hidden rows back — one at a time, or all at once ("reset the page").

Today the grid only offers risk/family/search filters (URL-backed). None of them lets him hand-pick which rows to drop or keep.

## Approved decisions (Tom, 2026-06-18)

- **Hide model:** Both — per-row hide (declutter) AND focus/isolate mode.
- **Restore:** Hidden tray (per-item restore) + "Show all" (reset).
- **Persistence:** Ephemeral. Survives the 60s auto-refresh and force-refresh; a full browser reload clears it. "Reset the page" = reload, or the "Show all" button.

## Out of scope (YAGNI)

- No persistence across reloads (no localStorage, no URL params).
- No backend/API/DB/contract change.
- No change to the existing risk/family/search URL filters.
- No change to other callers of the grid (supply view etc.) — new props default off.

---

## Architecture

Single source of truth: **`hiddenIds: Set<string>`** (item_id) held in `InventoryFlowClient` via `useState`. Two writers, one tray of removers.

```
InventoryFlowClient (owns state)
  ├─ hiddenIds: Set<string>          // what is hidden
  ├─ focusMode: boolean              // select-mode on/off
  ├─ selected: Set<string>           // tick-set while in focus mode
  │
  ├─ filteredItems  (existing: q + family + at_risk)
  └─ visibleItems = filteredItems.filter(it => !hiddenIds.has(it.item_id))
        │
        ├─ RowFocusControls   (NEW)  — Focus toggle + Hidden(N) tray + Show all
        ├─ FlowGridDesktop    — receives visibleItems + hide/select props
        └─ MobileCardStream   — receives visibleItems + hide/select props
```

`hiddenIds` is applied **after** the existing filters — it is the last filter. An item that is both hidden and filtered out by risk/family/search is simply absent; no conflict.

State lives in `InventoryFlowClient` (not URL, not FilterBar) so it is ephemeral by construction and survives TanStack background refetch (the component does not remount on refetch; only a full reload resets `useState`).

## Components

### NEW — `_components/RowFocusControls.tsx`
Rendered directly under `<FilterBar>`. Keeps `FilterBar` untouched (single responsibility). Props:
- `focusMode: boolean`, `onToggleFocus()`
- `hiddenItems: { item_id: string; item_name: string }[]` (already resolved to current items, names not ids)
- `onRestore(itemId)`, `onShowAll()`
- focus-mode action props: `selectedCount: number`, `onConfirmFocus()`, `onCancelFocus()`

Renders:
- A **Focus** toggle button (chip style, matches `FilterBar` `ChipButton`).
- When `hiddenItems.length > 0`: a **`Hidden (N) ▾`** pill → popover listing each hidden item by **name** with a restore (↩) button, and a **Show all** button in the popover footer. Always present while N>0 so hidden rows are never silently lost.
- When `focusMode`: a sticky action bar — `Hide the other {N} · Cancel`.

### CHANGED — `FlowGridDesktop.tsx` / `ItemRow`
New optional props (default off, so supply view unchanged):
- `onHide?(itemId)` — when set, render an eye-off button in the sticky panel wrapper (top-right, hover-revealed, mirrors the existing detail-chevron pattern). `aria-label="Hide {item_name}"`.
- `selectMode?: boolean`, `selectedIds?: Set<string>`, `onToggleSelect?(itemId)` — when `selectMode`, render a checkbox in the sticky panel wrapper (replaces/sits beside the hide button); checkbox reflects `selectedIds.has(id)`; toggles via `onToggleSelect`.

### CHANGED — `MobileCardStream.tsx` / `MobileItemCard.tsx`
Same prop set as desktop; hide button + select checkbox rendered on each card. Touch targets ≥44px (lesson from `/inventory` audit FLOW-014).

### CHANGED — `InventoryFlowClient.tsx`
- Add the three state atoms.
- Compute `visibleItems`; pass to grid/mobile in place of `filteredItems`.
- Resolve `hiddenItems` = `data.items` whose id ∈ `hiddenIds` (drops stale ids from display; `Show all` still clears the whole set).
- Wire handlers; render `<RowFocusControls>`.

## Interaction flows

**Hide one (declutter):** hover row → click eye-off → `hiddenIds.add(id)` → row drops out → `Hidden (N)` pill appears/increments.

**Focus / isolate:** click **Focus** → select mode on, hide buttons swap to checkboxes → tick the keepers → click **Hide the other N** → every un-ticked *visible* item added to `hiddenIds`, select mode exits, `selected` cleared. **Cancel** exits with no change.

**Restore one:** open `Hidden (N) ▾` → click ↩ next to an item → `hiddenIds.delete(id)`.

**Reset (Show all):** click **Show all** → `hiddenIds.clear()` → full grid returns. This is Tom's "reset the page" button (no reload needed).

## Edge cases

- **Hide everything visible:** if `visibleItems.length === 0` because of hiding (not because of filters), show an `EmptyState` "All rows hidden" with a **Show all** action inline — never a dead end. (Distinguish from the existing "No items match your filters" empty state.)
- **Stale ids:** an item that leaves the projection stays in `hiddenIds` harmlessly (filter never matches). Tray shows only `hiddenIds ∩ data.items`. `Show all` clears the full set.
- **Focus mode + filters:** "Hide the other N" only hides currently-*visible* items (post-filter). Items already filtered out are untouched.
- **Focus mode with 0 ticked:** "Hide the other N" would hide everything → guard: confirm hides all visible → lands on the "All rows hidden" empty state (recoverable via Show all). Acceptable; optionally disable the confirm button when `selectedCount === 0`.
- **Background refetch:** `hiddenIds` must NOT reset when `data` changes — it is independent `useState`, not derived from data.

## Global constraints (reviewer attention lens)

1. No backend/API/DB/URL-param/contract change. Portal client state only.
2. New grid/mobile props default off — supply view and any other caller render unchanged.
3. `hiddenIds` ephemeral: `useState`, resets only on full reload; must survive background refetch (do not key it off `data`).
4. Tray lists items by **name, not id** (system rule).
5. UI copy English / LTR.
6. Mobile hide/checkbox touch targets ≥44px.
7. `Hidden (N)` pill + tray always rendered when N>0 (no silent hidden loss).
8. Existing risk/family/search filters keep working unchanged.
9. Accessibility: hide button + checkbox + tray buttons have aria-labels; keyboard operable; focus visible.

## Testing

- Unit: `visibleItems` derivation (filters out hidden); `Show all` clears; restore removes one id; focus confirm moves all un-ticked visible ids into hidden.
- Component: hide → `Hidden (1)` appears → open tray → restore → row back. Focus → tick 2 → Hide the other N → only 2 remain → Show all → full grid. Hide-all → "All rows hidden" empty state → Show all recovers.
- Regression: existing filter tests still pass; supply view renders without hide controls.

## Rollback

Pure portal React change, no contract dependency. Revert the PR. No migration, no data effect.
