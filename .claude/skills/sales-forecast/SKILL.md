---
name: sales-forecast
description: "Builds GT's Sales forecast: monthly units per finished good, six months ahead, from Shopify sales, backtested against naive methods, then opened as a draft revision in Factory OS for Tom's approval. Every two weeks, or on \"תחזית מכירות\", \"תעדכן תחזית\", \"sales forecast\"."
---

# Sales forecast

The Sales forecast drives purchasing whenever there is no Production plan (D25, D26). It is monthly per finished good, six months ahead, updated every two weeks (D39). A skill run finishes end to end in one session: pulled, built, checked, drafted, reported. It leaves no Open ends (D38).

Method, research and evidence: `references/method.md`. Code: `scripts/engine.py`, `scripts/run_forecast.py`.

## Rules

- **Demand is Shopify net units, never `FG_OUT_PICK`.** The ledger misses 25–40% of picks (2026-09-06 check).
- **Out of the forecast:**
  - MTO and private-label items (`planning.demand.mto.*`, Tom 2026-07-23);
  - inactive items;
  - unmapped Shopify SKUs, which the run's report lists.
- **Every refresh is a revision.** The draft's `supersedes_version_id` is the current published version, and the current month is copied unchanged. Publishing then retires the old version, and no month counts twice (D32).
- **No draft if the method loses its test.** The combo must beat both naive methods on item WAPE in this run's backtest. If it does not, stop and report the numbers.
- **Publishing is Tom's.** The skill opens a draft. `publish.sql` runs only after his yes.

## Steps

1. **Session scratch dir** `$SP`. Install once: `pip install -q numpy pandas statsforecast holidays`.

2. **Shopify demand.** Run Shopify MCP `run-analytics-query`:
   ```
   FROM sales SHOW net_items_sold GROUP BY product_variant_sku TIMESERIES month SINCE 2024-07-01 UNTIL today ORDER BY month ASC LIMIT 5000
   ```
   The result is too large for the context, so the tool saves it to a file. Copy that file to `$SP/sku_month.json`.

3. **SKU map.** Run Supabase `execute_sql`, then write the single returned cell to `$SP/sku_map.psv`, one row per line:
   ```sql
   select string_agg(m.external_sku||'|'||m.item_id||'|'||coalesce(m.internal_units_per_shopify_unit,1)::float::text||'|'||
     i.supply_method||'|'||i.status||'|'||coalesce(i.family,'')||'|'||
     case when exists (select 1 from private_core.planning_policy p where p.key='planning.demand.mto.'||i.item_id
       and p.value::text='true') then 'MTO' else '' end, E'\n' order by m.external_sku)
   from private_core.integration_sku_map m join private_core.items i on i.item_id=m.item_id
   where m.source_channel='shopify' and m.approval_status='approved' and m.mapping_status='active';
   ```

4. **The version to revise.** Take the newest published monthly version that covers the current month:
   ```sql
   select version_id, horizon_start_at, published_at from private_core.forecast_versions
   where status='published' and cadence='monthly' order by published_at desc nulls last;
   ```

5. **Run.** `--last-full` is the last complete month. `--partial` is the current month, and `--partial-frac` is the days gone divided by the days in the month.
   ```
   python3 scripts/run_forecast.py --shopify $SP/sku_month.json --skumap $SP/sku_map.psv \
     --last-full <YYYY-MM> --partial <YYYY-MM> --partial-frac <0..1> --start <next month> --months 6 \
     --supersedes <version_id> --copy-months <current month> --actor 0db008a9-05e3-4521-8b30-42e5d444818d \
     --out $SP/run
   ```
   It writes `forecast.csv`, `report.md`, `draft.sql` and `publish.sql`.

6. **Check.**
   - The backtest table in `report.md` shows the combo beating both naive methods.
   - Every "needs a judgement" line gets a sentence in the report to Tom.

7. **Changes against the published version.** Compare `forecast.csv` with the published lines for the overlapping months. List every item whose month moved by more than 30% and more than 50 units.

8. **Draft.** Run Supabase `apply_migration` with the name `data_forecast_<start>_<end>_draft` and the SQL `draft.sql`. Then verify with a read:
   - the version exists with status `draft`;
   - its line count and per-month totals equal `forecast.csv`, plus the copied month.

9. **Report to Tom**, one message:
   - totals per month;
   - the step 7 list;
   - the judgement lines;
   - the backtest line (combo against both naive methods);
   - the portal link to the draft;
   - one ask: approve or change.

10. **After his yes:**
    - Run `publish.sql` through `apply_migration`, named `data_forecast_<start>_<end>_publish_tom_approved`.
    - Verify: the new version is `published`, the old one is `superseded`, and `fn_forecast_daily_demand` reads only the new version for the horizon.
    - Save `report.md` under `docs/planning/` in the brain as `<date>-forecast-<start>-<end>.md`.

## Stops

- The Shopify query fails, or returns under 20 months: stop and report.
- The backtest fails the rule above: no draft, report the numbers.
- An unmapped SKU sold over 1,000 units in the last 6 months: draft anyway, and put it first in the report. It is demand the forecast cannot see.
