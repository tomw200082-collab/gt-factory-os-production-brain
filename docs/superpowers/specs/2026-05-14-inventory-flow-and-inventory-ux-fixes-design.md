# Design Spec — Inventory Flow Display Fix + /inventory FLOW Items

**Date:** 2026-05-14
**Author:** Tom (approved) / brainstorming session
**Status:** Approved — ready for implementation plan
**Surfaces:** `/planning/inventory-flow` (PR #1) · `/inventory` (PR #2)

---

## Precise Goal

By end of session:

1. `/planning/inventory-flow` day cells never show raw negative numbers. Railway deploy of backend PR #26 verified. DayPopover updated with a "Without this production: −N" row when production inflow > 0. Chip tooltip updated to say "already included in EOD value."

2. `/inventory` — seven FLOW_COMPLETION items closed (FLOW-005, FLOW-006, FLOW-007, FLOW-008, FLOW-010, FLOW-011, FLOW-014) plus FLOW-016 (free — count bubble on Reconcile chip).

3. Both surfaces shipped as two separate PRs, merged, verified deployed.

---

## Context: Production Planning and the Broken Display

The production-aware projection (`inflow_from_production`, `projected_on_hand_eod_with_production`) already exists and is correctly computed in the backend. When a production plan schedules X units of product Y on day D, the `inflow_from_production` field on day D+1 carries X, and `projected_on_hand_eod_with_production` on D+1 already incorporates that inflow.

What is currently broken is display only: Railway has not yet deployed the backend clamp (PR #26), so `projected_on_hand_eod_with_production` is still returned as a raw signed value. The portal's defensive fallback returns `shortfall_qty = 0` (field doesn't exist yet), so the raw negative renders directly in the cell. Operator sees `↓200` chip + `−13` EOD and concludes the production didn't help. In reality, without the +200 production inflow, the EOD would be −213.

The design fixes both the display (deploy verification) and the comprehension (popover "without production" row).

---

## PR #1 — `/planning/inventory-flow`

**Files touched:**
- `window2-portal-sandbox/src/app/(planning)/planning/inventory-flow/_components/DayPopover.tsx`
- `window2-portal-sandbox/src/app/(planning)/planning/inventory-flow/_components/DayCell.tsx`

**No backend change. No contract change.**

### P0 — Deploy verification gate

Before any code change: verify Railway deploy of `gt-factory-os` backend PR #26.

Verification: call the live inventory flow API for one item and inspect JSON response. Presence of `shortfall_qty_with_production` field = deployed. Absence = not yet deployed.

If not deployed: wait or trigger redeploy before proceeding. Do not ship portal changes that depend on the clamped field until backend is live.

### P1a — DayPopover: "Without this production" row

**What changes in DayPopover.tsx:**

1. Compute `withoutProduction` inline when `day.inflow_from_production > 0`:
   ```ts
   // shortfall_qty_with_production = max(0, -(rawEodProd)).
   // rawEodProd = projected_on_hand_eod_with_production - shortfall_qty_with_production
   // (clamped value minus the gap that was clipped = original signed value).
   // withoutProduction = rawEodProd - inflow_from_production.
   const rawEodProd =
     day.projected_on_hand_eod_with_production - (day.shortfall_qty_with_production ?? 0);
   const withoutProduction = rawEodProd - day.inflow_from_production;
   ```
   Using `rawEodProd` (the pre-clamp signed value, reconstructed from the clamped EOD minus the shortfall) ensures the counterfactual is mathematically correct. If `rawEodProd = −13` and `inflow = 200`, then `withoutProduction = −213`, not `−200`. This value is the honest counterfactual — it can be negative, and that negativity is the key information the operator needs.

2. Add a row in the `<dl>` block, directly below "Projected on-hand (eod)", rendered only when `day.inflow_from_production > 0`:
   - Label: `"Without this production"`
   - Value: `withoutProduction`, formatted with `formatCompact`. Prepend `−` when negative.
   - Value class: `text-danger-fg` when negative, `text-fg-muted` when ≥0.

3. Remove the dead `< 0` check on the "Projected on-hand (eod)" row's `valueClassName`. After backend deploys, `projected_on_hand_eod_with_production` is always ≥0 — the `text-danger-fg` branch will never fire. The danger signal now lives in the shortfall row below and in the new "Without this production" row.

**Result for operator:**
```
From planned production:       +200
Projected on-hand (eod):          6   ← bold, always ≥0
Without this production:       −194   ← red, shows the counterfactual
```

### P1b — DayCell: chip tooltip update

**What changes in DayCell.tsx:**

Change the `title` attribute on the production chip `<span>` from:
```
+N bottles arriving from planned production
```
to:
```
+N from planned production · already included in the EOD value shown
```

Change `aria-label` on the chip span to match.

No structural change to the chip layout or the number row.

---

## PR #2 — `/inventory` FLOW items

**Files touched:**
- `window2-portal-sandbox/src/app/(shared)/inventory/page.tsx`
- `window2-portal-sandbox/src/components/stock/StockTruthDrawer.tsx`

**No backend change. No contract change. Each change independently revertable.**

### FLOW-005 — Dismissable warning alert

**page.tsx**

Add `const [alertDismissed, setAlertDismissed] = useState(false)`.

Wrap the alert render in `!alertDismissed && tierFilter !== "reconcile"`. The auto-suppress on `tierFilter === "reconcile"` means the alert disappears when the operator is already in the corrective workflow — exactly when they no longer need the nudge.

Add an `×` close button inside the alert that calls `setAlertDismissed(true)`. Dismiss is session-only (state, not localStorage).

### FLOW-006 — Alert link names the chip

**page.tsx**

Change alert link text from `"Show only these →"` to `"Filter to Reconcile items →"`.

After the filter activates, call `scrollIntoView({ behavior: "smooth" })` on the chip row element via a `ref`. This makes the activated chip visible without the operator having to find it.

### FLOW-007 — Plain language for floor breach

**page.tsx** (alert copy) + **StockTruthDrawer.tsx** (drawer header)

Replace every operator-visible instance of `"below physical floor"` with `"More outflows recorded than receipts"`. Internal variable names (`floor_gap`, `is_below_floor`) are unchanged.

### FLOW-008 — "Refresh now" button in drawer

**StockTruthDrawer.tsx**

After the corrective GR link (`Link target="_blank"`), add a `<button>` that calls `refetch()` on the ledger query.

- Label: `"I posted the receipt — refresh"`
- Rendered only when `hasEvents` (same condition as the GR CTA)
- Style: secondary/ghost variant, not primary — it's a follow-up action, not the main CTA

### FLOW-010 — Show total_matching in drawer

**StockTruthDrawer.tsx**

Below the ledger event list, when `data.total_matching > 10`, render:
```
Showing 10 of N events · View full ledger for this item →
```
Link goes to the per-item detail route. When `total_matching ≤ 10`, render nothing extra.

`total_matching` is already returned by the ledger API endpoint — this is a display-only addition.

### FLOW-011 — Gate drawer CTA on !isError

**StockTruthDrawer.tsx**

Add `!isError && data !== undefined` to the condition controlling CTA render. When `isError`, hide all CTA variants; show only the existing error block + retry button. Prevents operator from posting a corrective GR without having seen the existing ledger.

### FLOW-014 — Mobile ReconcileBadge touch target

**page.tsx** (InventoryCardMobile section)

Add `min-h-[44px]` to the ReconcileBadge wrapper `div`. Add `≥8px` separation between the item `Link` div and the `OnHandCell` div to prevent fat-finger navigation. Tailwind class addition only.

### FLOW-016 — Reconcile chip count bubble (free)

**page.tsx**

`negativeCount` is already computed in scope. Change chip label from `"Reconcile"` to `` `Reconcile (${negativeCount})` `` when `negativeCount > 0`. Zero-cost addition.

---

## Acceptance Criteria

### PR #1 — inventory-flow
- [ ] Live API JSON for any item shows `shortfall_qty_with_production` field (Railway deployed)
- [ ] Day cells never show negative numbers (raw value or formatted)
- [ ] Day cells with shortfall show `0` main number + `−N` hint below
- [ ] Production chip tooltip reads "already included in the EOD value shown"
- [ ] Popover "Without this production" row appears when `inflow_from_production > 0`
- [ ] "Without this production" value is negative (red) when it would have been a shortfall
- [ ] DayPopover "Projected on-hand (eod)" row never shows red (it's always ≥0 after clamp)

### PR #2 — /inventory
- [ ] FLOW-005: Alert has `×` button; dismiss is session-persistent; alert absent when Reconcile chip active
- [ ] FLOW-006: Alert link says "Filter to Reconcile items →"; chip row scrolls into view on click
- [ ] FLOW-007: "below physical floor" absent from all operator-visible copy
- [ ] FLOW-008: "I posted the receipt — refresh" button appears below GR link; clicking it calls refetch
- [ ] FLOW-010: "Showing 10 of N events" appears when `total_matching > 10`; link goes to per-item detail
- [ ] FLOW-011: No CTA renders when `isError`; retry button visible
- [ ] FLOW-014: ReconcileBadge wrapper height ≥44px on 390px viewport
- [ ] FLOW-016: Reconcile chip shows count when `negativeCount > 0`

---

## Rollback Plan

Both PRs are portal-only (no DB migration, no API contract change). Each is independently revertable via `git revert`. No downstream consumers of the changed components outside these two surfaces.

---

## References

- UX audit (18 findings, /inventory): `PRODUCTION/docs/phase8/ux/inventory-flow-audit-2026-05-14.md`
- Stock Truth Change 2 design: `PRODUCTION/docs/superpowers/specs/2026-05-13-display-clamp-physical-stock-truth-design.md`
- Backend PR #26 (clamp pass §5c): `gt-factory-os/api/src/inventory/handler.flow.ts` lines 732–781
- Portal PR #20 (DayCell shortfall): `window2-portal-sandbox/src/app/(planning)/planning/inventory-flow/_components/DayCell.tsx`
