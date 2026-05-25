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
