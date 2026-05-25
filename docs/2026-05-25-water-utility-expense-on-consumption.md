# Water → Utility (Expense on Consumption)

**Date:** 2026-05-25
**Scope:** RAW-WATER reclassified as a utility component. Generic pattern for any future utility (CO2, electricity-per-batch, etc.).
**Lanes touched:** `backend-db` (gt-factory-os: migration + handler), `portal` (gt-factory-os-portal: types + /inventory section + dashboard tile).
**Status:** Implemented going-forward on branch `claude/dashboard-visual-polish-77wrL` across all three repos. No historical recompute. No PR yet (Tom-only push gate).

## Problem

RAW-WATER was modelled as a normal `INGREDIENT` component in `private_core.components` with `std_cost_per_inv_uom = 1.35 ILS/L`. Operationally it behaves nothing like a stocked raw material:

1. Supply is effectively infinite (municipal water + plant tap). We do not GR it, we do not count it, we do not waste it.
2. We pay only when it is **consumed by production** — never for "on-hand stock".
3. It MUST appear as a cost line in finished-goods COGS / FOODCOST, otherwise the margin model lies (Muza 0.45L is mostly water — its COGS without water would be wrong).
4. It MUST NOT appear in the RM inventory value rollup, otherwise the dashboard "RM Inventory Value" and `/inventory` totals are inflated by an arbitrary water on-hand that nobody tracks anyway.

Today the stock-value handler reads `current_balances × std_cost` and includes RAW-WATER alongside real raw materials, which is wrong on the inventory-value side. The COGS side (BOM → fn_explode_bom_to_components → fg_cogs_snapshots) was already correct and is preserved.

## Decision

Introduce a generic boolean `private_core.components.is_utility_expense_on_consumption`. Set true for RAW-WATER; default false for everything else. The flag is read by:

- **Stock value handler** (`api/src/stock/value-handler.ts`) — utility components are filtered out of the per-item `rows` and the per-`item_type` rollup. They are surfaced separately in a new `utilities` array on the response, carrying `component_id`, `component_name`, `uom`, `unit_cost_ils` (no quantity, no value).
- **Stock list handler** (`api/src/stock/handler.ts`, both branches) — utility components are filtered out of `/api/stock?type=RM_PKG` and the generic list. They never appear next to real RM/PKG SKUs.
- **Portal `/inventory`** — adds a small "Utilities (expense on consumption)" section between the KPI strip and the Current Stock card. Renders each utility with its unit cost and UOM. The "Total inventory value" KPI's subtitle names the excluded utilities when any are present.
- **Portal dashboard `/dashboard`** — the "RM Inventory Value" tile's subtitle appends "excludes water" (or whatever utility names) so the tile stays honest.

Nothing changes on the COGS / FOODCOST side. `fn_explode_bom_to_components` still walks every BOM line including water; `computeBomBasedCogs` still multiplies by `std_cost_per_inv_uom`; nightly `fg_cogs_snapshots` still embeds water cost into every cocktail's `cogs_per_unit_ils`. The `v_fg_economics` view's `fg_inventory_value_at_cost = cogs_per_unit_ils × qty_on_hand` therefore still reflects the water cost that was paid when each bottle was produced — which is the correct "expense on consumption" semantic.

### Interpretation chosen: A — standard "expense on consumption"

| Interpretation | Treatment of water cost embedded in finished goods | Pick |
|---|---|---|
| **A** (chosen) | FG inventory value INCLUDES the water cost that was paid when the bottle was made. RM inventory value EXCLUDES water (the tap, not the embedded cost). | ✅ |
| B | Subtract water cost from FG cost_per_unit so no inventory-value surface contains any water cost at all. | ✗ — invasive, conflicts with COGS truth |

A matches standard manufacturing accounting (utilities flow into cost-of-goods-produced at consumption time, becoming part of finished-goods value). It is also what Tom asked for in plain language ("we pay for water only when it is used").

## Schema change

Migration `gt-factory-os/db/migrations/0210_water_expense_on_consumption.sql`:

```sql
ALTER TABLE private_core.components
  ADD COLUMN IF NOT EXISTS is_utility_expense_on_consumption boolean
    NOT NULL DEFAULT false;
UPDATE private_core.components
   SET is_utility_expense_on_consumption = true, updated_at = now()
 WHERE component_id = 'RAW-WATER';
```

Default false → existing components are untouched. Idempotent — `IF NOT EXISTS` + UPDATE WHERE. Loader (`scripts/import_masters.ts`) extended to upsert the new field from `IS_UTILITY_EXPENSE_ON_CONSUMPTION` in `fixtures/masters/components.json`. RAW-WATER's fixture row sets it true.

## API contract change

`StockValueResponse` gains one optional field:

```ts
utilities: Array<{
  component_id: string;
  component_name: string | null;
  uom: string | null;
  unit_cost_ils: string | null;
}>;
```

`StockValueRow` gains `is_utility_expense_on_consumption: boolean` — always false in the response today (utilities don't appear in `rows`), but typed for future use if we ever surface them inline.

This is additive. Existing portal pages that ignore `utilities` continue to work; pages that consume it (this commit's `/inventory` and `/dashboard`) light up.

## What did NOT change

- `fn_explode_bom_to_components` (migration 0191) — still walks water as a BOM leaf.
- `cogs-rollup.ts` `computeBomBasedCogs` — still includes water in the per-component breakdown.
- `fg_cogs_snapshots` nightly job — water cost stays in `cogs_per_unit_ils`.
- `v_fg_economics` view (migration 0189) — `fg_inventory_value_at_cost` formula untouched; interpretation A means it should keep the embedded water cost.
- Historical `current_balances` — no backfill, no recompute. Going-forward only. If anyone manually injects a ledger movement for RAW-WATER it will be ignored by the value handler (filtered out) but accepted by the ledger (append-only invariant).

## Verification

- `gt-factory-os/api` TypeScript: `npm run typecheck` clean for stock surfaces.
- `gt-factory-os-portal` TypeScript: `npm run typecheck` clean.
- New test cases in `api/test/stock_value_handler_by_type.test.ts`: assert RAW-WATER is in `utilities` with a positive unit cost, is NOT in `rows`, and the rollup totals stay non-negative after utility exclusion.
- Manual: refresh `/inventory` — Utilities section visible, KPI excludes water; refresh `/dashboard` — RM tile subtitle names water.

## Reversibility

The flag can be cleared per-component (`UPDATE ... SET is_utility_expense_on_consumption = false WHERE component_id = 'RAW-WATER'`) and the component immediately reverts to a normal RM. The column can be dropped if the model is abandoned (no other table references it).

## Forward path

When the next utility appears (CO2 cylinders charged per cocktail batch, kWh per cook), the flag carries it. No new schema, no new handler, no new UI section — just `UPDATE components SET is_utility_expense_on_consumption = true WHERE component_id = '<new-id>'` and a fixture row. The /inventory utilities section grows by one row.

---

## Addendum — 2026-05-25 (later same day)

A CFO + MRP critique exposed that the initial RAW-WATER `std_cost_per_inv_uom = 1.35 ILS/L` was approximately **100× the real Israeli municipal commercial rate**. At that rate the water cost embedded in every cocktail's FG COGS was inflated and silently distorting margins. The first refactor (this document above) correctly excluded water from inventory value but had not addressed the underlying unit-cost error.

### Correction applied

| What | Where | Value |
|---|---|---|
| Israeli commercial water tariff (Rashut HaMayim, 1 Jan 2026 update) | https://www.gov.il/he/pages/rates_general1 | 15.26 ILS / m³ incl. VAT |
| Rounded per-liter rate now in the system | migration 0211 + fixture | **0.015 ILS / L** |
| Old (erroneous) rate | prior fixture / pre-0211 state | 1.35 ILS / L |
| Impact on a 0.4 L Muza | water cost in COGS | from 0.54 ILS → 0.006 ILS |

### What was added going beyond the rate fix

1. **`migration 0212` — `v_cogs_breakdown_per_item` view.** Per-FG decomposition of `cogs_per_unit_ils` into seven buckets (utilities, packaging, sweeteners, bases, ingredients, self, other). Replaces the prior single-blob `cogs_per_unit_ils`. Pricing decisions now have a real surface: "this Muza's COGS is X, of which Y is packaging, Z is sweetener, W is water".
2. **`scripts/audit_water_in_boms.ts` — one-shot water audit.** For every ACTIVE MANUFACTURED FG, reports: beverages with no water (BOM gap), recipes with water > 1.5× pack size (yield error), FGs with incomplete cost rollups, top-20 FG by utility cost share. Read-only, safe to run against production.
3. **`api/test/cogs_multi_level_utility.test.ts` — 3-level walk test (T7a/b/c).** Asserts that FG → PACK → BASE → SEMI → water flows correctly when a finished good's BASE MIX uses a SEMI component (e.g. cocktails on top of `SEMI-FRE-BASE`). The two-level `fn_explode_bom_to_components` alone would silently swallow water inside SEMI recipes; the test guards the SEMI-rollup path added in migration 0209.

### Acknowledged limitations (NOT fixed here)

The deeper CFO concern — that we have **standard cost absorption without matching credit-side journal entries**, which means the same water can be expensed twice (once as utility bill in P&L, once as part of COGS at FG sale) — is not addressed. That is a separate, larger conversation about whether GT wants accounting-grade or management-grade COGS, and it requires the accountant of record. Until that is decided:

- Water cost in FG COGS = standard-utility-absorbed-cost. **Not a GL-grade material cost.**
- The 0.015 ILS / L is the bulk-buy rate; it does NOT include losses, cleaning, evaporation, or RO/treatment overhead. Realised absorbed water cost ≈ municipal bill ± variance, with no formal true-up yet.
- For management decisions (pricing, margin ranking, FOODCOST percentage) the numbers are now correct to a degree that comfortably exceeds the materiality bar.
- For audited financial statements: see the accountant. Don't reuse `cogs_per_unit_ils` for balance sheet inventory valuation without a sanity overlay.
