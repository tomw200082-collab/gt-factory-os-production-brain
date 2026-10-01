---
name: sales-forecast
description: "Builds GT's Sales forecast: monthly units per finished good, six months ahead, from Shopify sales, backtested against naive methods. Publishes itself unless a line moves past its limit. Every two weeks, or on \"תחזית מכירות\", \"תעדכן תחזית\", \"sales forecast\"."
---

# Sales forecast

The Sales forecast drives purchasing whenever there is no Production plan (D25, D26). It is monthly per finished good, six months ahead, updated every two weeks (D39). A skill run finishes end to end in one session: pulled, built, checked, drafted, then published or put to Tom. It leaves no Open ends (D38).

Method, research and evidence: `references/method.md`. Code: `scripts/engine.py`, `scripts/run_forecast.py`.

## Rules

- **Demand is Shopify net units, never `FG_OUT_PICK`.** The ledger misses 25–40% of picks (2026-09-06 check).
- **Out of the forecast:**
  - MTO and private-label items (`planning.demand.mto.*`, Tom 2026-07-23);
  - the 0.3 L teas, which are made to order (Tom 2026-09-28);
  - inactive items;
  - unmapped Shopify SKUs, which the run's report lists.
  `KNOWN_OUT` in `run_forecast.py` holds Tom's rulings; the report lists them apart, so they never read as gaps. A ruling changes only on his word.
- **No launch until Tom dates it.** The American line and new NS variants stay at zero until he gives a date and a volume (D41). No manual override on matcha.
- **Every refresh is a revision.** The draft's `supersedes_version_id` is the current published version, and the current month is copied unchanged. Publishing then retires the old version, and no month counts twice (D32).
- **No draft if the method loses its test.** The combo must beat both naive methods on item WAPE in this run's backtest. If it does not, stop and report the numbers.
- **Tom approves only flagged lines (D40, Tom 2026-09-28).** Items are ranked A, B and C by their share of the new forecast (A to 80%, B to 95%). A line is flagged when it moves more than 50 units and more than 15% (A), 25% (B) or 40% (C) from the published version over the overlapping months, or is new. `run_forecast.py` writes the list to `flags.json`.
  - Nothing flagged: the skill publishes.
  - Anything flagged: the whole draft waits for Tom's yes, and each flagged line reaches him as a Decision. The published version stays in force meanwhile.
- **The database is the record.** The open-draft submission carries the flagged lines and the full report, so an unattended run leaves no files to commit.

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

4. **The version to revise, and the skill's stale drafts.**
   ```sql
   select version_id, status, horizon_start_at, created_at, published_at from private_core.forecast_versions
   where cadence='monthly' and (status='published' or (status='draft' and created_by_snapshot='Claude (sales-forecast)'))
   order by created_at desc;
   ```
   - The newest `published` row is the version to revise.
   - Any `draft` row is an earlier run Tom never approved. Pass its id to `--discard`, and name it in the report.
   - Write the revised version's lines from the first forecast month on to `$SP/published.psv`, one `item|YYYY-MM|qty` per line (the single returned cell):
   ```sql
   select string_agg(item_id||'|'||to_char(period_bucket_key,'YYYY-MM')||'|'||forecast_quantity::int, E'\n' order by item_id, period_bucket_key)
   from private_core.forecast_lines where version_id='<version to revise>' and period_bucket_key >= '<first forecast month>-01';
   ```

5. **Run.** `--last-full` is the last complete month. `--partial` is the current month, and `--partial-frac` is the days gone divided by the days in the month.
   ```
   python3 scripts/run_forecast.py --shopify $SP/sku_month.json --skumap $SP/sku_map.psv \
     --last-full <YYYY-MM> --partial <YYYY-MM> --partial-frac <0..1> --start <next month> --months 6 \
     --supersedes <version_id> --copy-months <current month> --published $SP/published.psv \
     --discard <stale draft ids, comma-separated, or empty> --actor 0db008a9-05e3-4521-8b30-42e5d444818d \
     --out $SP/run
   ```
   It writes `forecast.csv`, `report.md`, `flags.json`, `draft.sql` and `publish.sql`.

6. **Check.** The backtest table in `report.md` shows the combo beating both naive methods.

7. **Draft.** Run Supabase `apply_migration` with the name `data_forecast_<start>_<end>_draft` and the SQL `draft.sql`. Then verify with a read:
   - the version exists with status `draft`, and any `--discard` id is `discarded`;
   - its line count and per-month totals equal `forecast.csv`, plus the copied month.

8. **Publish or ask.** Read `flags.json`.
   - `auto_publish` true: run `publish.sql` through `apply_migration`, named `data_forecast_<start>_<end>_publish_auto`.
   - Otherwise: keep the draft, and go to step 9.

   After a publish, verify:
   - the new version is `published` and the old one `superseded`;
   - `fn_forecast_daily_demand` reads only the new version for the horizon.

9. **Report to Tom**, one message:
   - Published: one line, with the monthly totals, the backtest line, and any unmapped SKU over 1,000 units.
   - Waiting: the flagged lines first, each one with the old and new numbers and one sentence on why it moved. Then the new items, the backtest line, the portal link to the draft, and one ask: approve or change.

10. **After his yes:** run `publish.sql` through `apply_migration`, named `data_forecast_<start>_<end>_publish_tom_approved`, and verify as in step 8.

## Stops

- The Shopify query fails, or returns under 20 months: stop and report.
- The backtest fails the rule above: no draft, report the numbers.
- An unmapped SKU sold over 1,000 units in the last 6 months: publish anyway, and name it in the report. It is demand the forecast cannot see.
