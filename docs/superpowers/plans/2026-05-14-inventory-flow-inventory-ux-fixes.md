# Implementation Plan — inventory-flow Display Fix + /inventory FLOW Items

**Date:** 2026-05-14
**Spec:** `docs/superpowers/specs/2026-05-14-inventory-flow-and-inventory-ux-fixes-design.md`
**Repo:** `window2-portal-sandbox` (Next.js 15 portal)
**Approach:** Two PRs — PR #1 for `/planning/inventory-flow`, PR #2 for `/inventory`

---

## Phase 1 — PR #1: `/planning/inventory-flow`

Branch: `fix/inventory-flow-display-2026-05-14`

### Task 1: Verify Railway deploy (P0 gate)

**Type:** Verification (no code change)

Check whether the `gt-factory-os` backend has deployed PR #26 (the clamp pass). Hit the live Railway API at `https://gt-factory-os-production.up.railway.app/api/v1/queries/inventory/flow?horizon_weeks=2` (or equivalent) and inspect one item's day JSON. If `shortfall_qty_with_production` field exists → PASS. If absent → BLOCKED, report to Tom.

No file changes. Report PASS or BLOCKED.

---

### Task 2: DayPopover.tsx — "Without this production" row

**File:** `window2-portal-sandbox/src/app/(planning)/planning/inventory-flow/_components/DayPopover.tsx`

**Changes:**
1. Compute `withoutProduction` when `day.inflow_from_production > 0`:
   ```ts
   const rawEodProd =
     day.projected_on_hand_eod_with_production - (day.shortfall_qty_with_production ?? 0);
   const withoutProduction = rawEodProd - day.inflow_from_production;
   ```
   `rawEodProd` reconstructs the pre-clamp signed value. `withoutProduction` is the honest counterfactual (can be negative).

2. In the `<dl>` block, after the "Projected on-hand (eod)" row, add a new row when `day.inflow_from_production > 0`:
   - Label: `"Without this production"`
   - Value: formatted with `formatCompact`. Prepend `"−"` when negative. Use `text-danger-fg` when negative, `text-fg-muted` when ≥0.

3. Remove the dead `< 0` condition on the "Projected on-hand (eod)" `valueClassName`. After backend deploy, this value is always ≥0. Replace with just `"font-semibold text-fg-strong"`.

**Acceptance:**
- Popover for a day with production inflow > 0 shows "Without this production: −N" row in red
- Popover "Projected on-hand (eod)" row is never styled red (value is always ≥0 post-clamp)
- Commit on `fix/inventory-flow-display-2026-05-14`

---

### Task 3: DayCell.tsx — chip tooltip update

**File:** `window2-portal-sandbox/src/app/(planning)/planning/inventory-flow/_components/DayCell.tsx`

**Changes:**
1. Update the production chip `title` attribute (currently: `"+N bottles arriving from planned production"` or similar). New value:
   ```
   +N from planned production · already included in the EOD value shown
   ```
2. Update `aria-label` on the chip `<span>` to match.

No layout change. No logic change. Copy only.

**Acceptance:**
- Chip hover tooltip reads "already included in the EOD value shown"
- aria-label matches
- Commit on `fix/inventory-flow-display-2026-05-14`

---

## Phase 2 — PR #2: `/inventory`

Branch: `fix/inventory-ux-flow-items-2026-05-14` (from main)

### Task 4: page.tsx — FLOW-005, FLOW-006, FLOW-007, FLOW-014, FLOW-016

**File:** `window2-portal-sandbox/src/app/(shared)/inventory/page.tsx`

**FLOW-005 — Dismissable warning alert:**
- Add `const [alertDismissed, setAlertDismissed] = useState(false)`
- Wrap alert render in `!alertDismissed && tierFilter !== "reconcile"`
- Add `×` close button inside alert calling `setAlertDismissed(true)`

**FLOW-006 — Alert link names the chip:**
- Change link text from `"Show only these →"` to `"Filter to Reconcile items →"`
- After activating the filter, call `scrollIntoView({ behavior: "smooth" })` on the chip row via a ref

**FLOW-007 — Plain language for floor breach:**
- Replace every operator-visible instance of `"below physical floor"` with `"More outflows recorded than receipts"` in this file
- Internal variable names (`floor_gap`, `is_below_floor`) stay unchanged

**FLOW-014 — Mobile touch target:**
- In the `InventoryCardMobile` section, find the ReconcileBadge wrapper `div`
- Add `min-h-[44px]` to that wrapper
- Add ≥8px separation between the item `Link` div and the `OnHandCell` div

**FLOW-016 — Reconcile chip count (free):**
- `negativeCount` is already computed in scope
- Change chip label from `"Reconcile"` to `` `Reconcile (${negativeCount})` `` when `negativeCount > 0`

**Acceptance:** All 5 FLOW items pass their acceptance criteria (from spec). Commit on `fix/inventory-ux-flow-items-2026-05-14`.

---

### Task 5: StockTruthDrawer.tsx — FLOW-008, FLOW-010, FLOW-011

**File:** `window2-portal-sandbox/src/components/stock/StockTruthDrawer.tsx`

**FLOW-007 (continued) — plain language in drawer:**
- Replace `"below physical floor"` with `"More outflows recorded than receipts"` in drawer header/copy

**FLOW-008 — "Refresh now" button:**
- After the corrective GR `<Link target="_blank">`, add a secondary `<button>` calling `refetch()` on the ledger query
- Label: `"I posted the receipt — refresh"`
- Rendered only when `hasEvents` (same condition as GR CTA)
- Style: secondary/ghost — not primary

**FLOW-010 — Show total_matching:**
- Below the ledger event list, when `data.total_matching > 10`, render:
  `"Showing 10 of N events · View full ledger for this item →"`
- Link goes to the per-item detail route
- `total_matching` already exists in the API response — display only

**FLOW-011 — Gate CTA on !isError:**
- Add `!isError && data !== undefined` to CTA render condition
- When `isError`: hide all CTA variants, show only error block + retry button

**Acceptance:** All 4 items pass spec acceptance criteria. Commit on `fix/inventory-ux-flow-items-2026-05-14`.
