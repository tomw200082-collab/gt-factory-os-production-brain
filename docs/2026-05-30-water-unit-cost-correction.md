# Water unit cost correction (2026-05-30)

Round-4 inventory/COGS pass. Decision record for the work delivered on
branch `claude/water-cost-fix-and-breakdown` (PR pending).

## Problem

PR #45 (round 3) excluded water from RM/PKG inventory valuation via the
`planned_flag = false` discriminator (migration 0212). That fixed the
*inventory side*. What remained: the unit cost of `RAW-WATER` itself was
still **1.3500 ILS/L** in both `components.std_cost_per_inv_uom` and
`supplier_items.std_cost_per_inv_uom` (SUP-009, primary). That is
approximately **100× the real Israeli commercial water tariff** and has
no documented derivation in the repo — it looks like an unchecked
placeholder from the original fixture extract.

Because of the inflated cost:

- Every FG that has water in its BOM was carrying an over-large water
  cost inside `cogs_per_unit_ils`. A 1L CALM tea (FG-CAL-1L) was
  attributed ~1.36 ILS of water cost (~10% of COGS).
- The same was true for `SEMI-CAL-BASE`, `SEMI-FRE-BASE`,
  `SEMI-NAM-BASE` — and through them, every cocktail that uses those
  bases.
- Margins, FOODCOST percentages, and the per-FG pricing decisions on
  /economics were all distorted by the same inflated factor.

## Decision

Apply the real Israeli commercial water tariff as the standard cost.

| Source | Value |
|---|---|
| Rashut HaMayim (1 Jan 2026 update) | **15.26 ILS / m³ incl. VAT** |
| Per liter | 0.01526 ILS / L |
| Adopted in DB (rounded) | **0.0150 ILS / L** (= 15 ILS / m³) |
| Authoritative source | https://www.gov.il/he/pages/rates_general1 |

Precision past the cubic-meter level is not material at this magnitude.
The cost is "negligible anyway" — what matters is getting the order of
magnitude right.

## What changed in production (`rvadsozabmxkkrktwgnv`)

Applied via Supabase MCP, not via the deployed nightly job (the
`phase10-cogs-nightly` pg_cron entry is a placeholder; the real
mechanism is an HTTP-triggered job that requires the `JOB_RUNNER_TOKEN`
secret).

### Master data

1. `private_core.components.std_cost_per_inv_uom` for RAW-WATER:
   `1.3500 → 0.0150`. Recorded as migration **0222** in the repo.
2. `private_core.supplier_items.std_cost_per_inv_uom` for SUP-009 +
   RAW-WATER primary row: `1.3500 → 0.0150`. Same migration — done as
   a direct UPDATE since the cogs-rollup prefers the supplier_items
   primary over components.std_cost.
3. SEMI base costs re-rolled from their recipes against the corrected
   water cost. New values:
   - `SEMI-CAL-BASE` → 7.6223 ILS / L (was NULL on master)
   - `SEMI-FRE-BASE` → 4.1409 ILS / L (was NULL on master)
   - `SEMI-NAM-BASE` → 3.4544 ILS / L (was NULL on master)

### Snapshots

`fg_cogs_snapshots` is append-only. A backfill batch (`source = 'backfill'`,
`actor_snapshot = '<system:water-cost-correction-2026-05-30-final>'`)
inserted **42 corrected snapshots** — one per FG whose previous breakdown
referenced RAW-WATER or a SEMI base. Of those: 24 complete, 18 carry
pre-existing `missing_cost_components` from non-water gaps (these were
incomplete before this fix, still incomplete after — out of scope).

A first backfill batch (`<system:water-cost-correction-2026-05-30>`)
was written with stale SEMI costs (the SEMI rollup ran *before* I
realised the supplier_items row also needed updating). Those 42 rows
stay in the table — the append-only guard blocks `DELETE` — but the
final batch's `event_at` is later, so the latest-snapshot view picks
the correct row. No consumer is affected.

### View + API

`private_core.v_cogs_breakdown_per_item` (migration **0223**) — per-FG
COGS decomposed into seven buckets:

  - `utilities_cost_ils`   ← `planned_flag = false` (same semantic as
                             `v_rm_pkg_economics`, migration 0212)
  - `packaging_cost_ils`   ← `component_class IN ('PACKAGING','PACKAGING_SET')`
  - `bases_cost_ils`       ← `component_group = 'BASES'`
  - `sweeteners_cost_ils`  ← `component_group ILIKE '%SYRUP%'` OR id
                             matches `SUGAR`/`SWEET`
  - `ingredients_cost_ils` ← any other `INGREDIENT`
  - `self_cost_ils`        ← BOUGHT_FINISHED inline cost
  - `other_cost_ils`       ← catch-all

`GET /api/v1/queries/economics/cogs-breakdown` exposes the view.

## Verification (post-rollout)

| Metric | Before | After |
|---|---|---|
| RAW-WATER `std_cost_per_inv_uom` (components + supplier_items primary) | 1.3500 | **0.0150** |
| FG-CAL-1L `cogs_per_unit_ils` | 15.0938 | **13.7493** (−1.34) |
| FG-FRE-1L `cogs_per_unit_ils` | ~11.61 | **10.2678** |
| Max utility share of any FG's COGS | 14.84% | **0.19%** |
| Average utility share | 7.10% | **0.09%** |

The "negligible" outcome we expected. Water now reads as a rounding
error in margins, which is the correct economic picture for a small
beverage factory paying a municipal water bill.

## Audit findings (read-only, not in scope for this PR)

`scripts/audit_water_in_boms.ts` flagged five ACTIVE items as
"beverages with no water in BOM walk" — four `ADD-MUZ-*` mixer
placeholders without a `primary_bom_head_id` at all (fixture rows
never wired up) plus `FG-MUZ-PSC-200ML` (same — no BOM). These are
not water bugs; they are inactive-by-omission items that the
catalog shows as ACTIVE. Worth a separate cleanup pass.

One real anomaly: **FG-CAL-500ML** has `fn_explode_bom_to_components`
returning 0 L of water, but its persisted `cost_breakdown` JSONB
contains a 0.5036 L RAW-WATER line. The numbers don't agree. This is
a separate gap — either the SQL function and the TS cogs-rollup diverge
on how they walk PACK→BASE for this FG, or the snapshot is stale in a
way the audit script doesn't detect. Flagged for follow-up.

## Acknowledged limitations (NOT fixed here)

The CFO concern about **standard cost absorption without matching
credit-side journal entries** is unchanged. The same water can still be
expensed twice — once as utility bill in P&L (when the bi-monthly water
bill posts) and once as part of COGS at FG sale. That is a separate,
larger conversation about whether GT wants accounting-grade or
management-grade COGS, and it requires the accountant of record. Until
that is decided:

- Water cost in FG COGS = standard-utility-absorbed-cost.
- **Not a GL-grade material cost.** For audited financial statements
  see the accountant; don't reuse `cogs_per_unit_ils` for balance sheet
  inventory valuation without a sanity overlay.
- `0.0150 ILS / L` is the bulk-buy rate; it does NOT include losses,
  cleaning, evaporation, or RO/treatment overhead. Realised absorbed
  water cost ≈ municipal bill ± variance, with no formal true-up yet.
- For management decisions (pricing, margin ranking, FOODCOST
  percentage) the numbers are now correct to a degree that comfortably
  exceeds the materiality bar.
