# daily-ops-guardian — SQL library (verified live 2026-07-24)

Guardian-owned, read-only queries. Every query here was run against the live project
`rvadsozabmxkkrktwgnv` (schema `private_core`, site `GT-MAIN`) and returned real rows on
2026-07-24. Run via Supabase MCP `execute_sql`. **Reuse these verbatim** instead of
re-deriving from sibling skills — a headless trigger session must run the same verified SQL.

Taxonomy (verified): `item_type` is `RM` / `PKG` / `FG` (no `COMPONENT`). Components = RM + PKG.
Committed demand = `demand_lionwheel_qty` (dated LionWheel pickups). Forecast demand =
`demand_forecast_qty`. If a column errors, the schema evolved — re-introspect and adjust.

---

## Stage 0 pre-flight — connector reachability (V9)
```sql
select 1 as supabase_ok;   -- errors / tool disabled => connectors off => fail loudly per V9
```

## Stage 0 — integrity gate + freshness
```sql
select private_core.rebuild_verifier() as verifier_drift;   -- MUST be 0; else 🔴 + HALT drafts
```
```sql
select
  (now() at time zone 'Asia/Jerusalem')::date               as today_il,
  ((now() at time zone 'Asia/Jerusalem')::date - 1)         as yesterday_il,
  to_char(((now() at time zone 'Asia/Jerusalem')::date-1),'Dy') as yday_dow,
  exists(select 1 from private_core.holidays_il h
         where h.holiday_date=((now() at time zone 'Asia/Jerusalem')::date-1)
           and h.blocks_pickup)                              as yday_blocked_holiday,
  (select max(updated_at)  from private_core.orders_mirror)  as mirror_last_update,   -- LionWheel freshness (15-min poll)
  (select max(last_refreshed_at) from private_core.current_balances) as balances_refreshed,
  (select json_build_object('run_id',run_id,'status',status,'drift',rebuild_verifier_drift_at_run,
            'executed_at',executed_at,'fv',demand_snapshot_forecast_version_id)
     from private_core.planning_runs order by executed_at desc limit 1) as latest_run,
  (select count(*) from private_core.exceptions
     where status in ('open','new') and severity in ('critical','high'))  as open_hi_exceptions;
```

## Stage 0.5 — yesterday plan vs actual (skip if yesterday ∉ Sun–Thu)
Replace `:YDAY` with the yesterday date (Israel).
```sql
select
 (select count(*) from private_core.production_plan
    where plan_date=:YDAY and status='planned')                                   as planned_batches,
 (select coalesce(round(sum(planned_qty)::numeric,1),0) from private_core.production_plan
    where plan_date=:YDAY and status='planned')                                   as planned_qty,
 (select count(*) from private_core.production_actual
    where (event_at at time zone 'Asia/Jerusalem')::date=:YDAY and reversed_at is null) as actual_reports,
 (select coalesce(round(sum(output_qty)::numeric,1),0) from private_core.production_actual
    where (event_at at time zone 'Asia/Jerusalem')::date=:YDAY and reversed_at is null) as actual_output,
 (select json_agg(t) from (
    select pp.item_id, i.item_name, pp.planned_qty, (pp.completed_submission_id is not null) done
    from private_core.production_plan pp left join private_core.items i on i.item_id=pp.item_id
    where pp.plan_date=:YDAY and pp.status='planned' order by pp.item_id) t)        as plan_rows;
-- V7: planned_batches>0 AND actual_reports=0  =>  🔴 rendered FIRST in the email. Else 🟢/🟡.
```

## Stage 1 — FG sell-coverage (14d) via the live engine
Replace `:START` = today (IL), `:END` = today+13.
```sql
with proj as (select * from private_core.fn_compute_daily_fg_projection(:START::date, :END::date))
select
 (select count(distinct item_id) from proj)                                        as items_projected,
 (select count(distinct item_id) from proj p
    where exists(select 1 from proj p2 where p2.item_id=p.item_id and p2.shortfall_qty>0)) as items_short,
 (select json_agg(t) from (
    select p.item_id, i.item_name,
      min(p.day) filter (where p.shortfall_qty>0)        as first_short_day,
      round(max(p.shortfall_qty)::numeric,1)             as max_short,
      round(sum(p.demand_lionwheel_qty)::numeric,1)      as committed_14d,   -- committed (dated) demand
      round(sum(p.demand_forecast_qty)::numeric,1)       as forecast_14d
    from proj p left join private_core.items i on i.item_id=p.item_id
    group by p.item_id, i.item_name
    having count(*) filter (where p.shortfall_qty>0)>0
    order by min(p.day) filter (where p.shortfall_qty>0), max(p.shortfall_qty) desc
    limit 30) t)                                                                    as short_items;
-- Severity: committed_14d>0 on a short item => committed shortage => 🔴 (a dated order at risk).
--           committed_14d=0 => forecast-only gap => 🟡 (production-planning territory).
-- G1_FILL_PCT = round(100 * (items_projected - items_short) / items_projected).
```

## Stage 2 — RM/PKG coverage from the latest completed planning run
Replace `:RUN_ID` with the latest completed `planning_runs.run_id` (from Stage 0).
```sql
with n as (select component_id, period_bucket_key, net_purchase_qty
           from private_core.planning_run_component_netting where run_id=:RUN_ID)
select
 (select count(distinct component_id) from n)                       as comps_in_netting,
 (select count(distinct component_id) from n where net_purchase_qty>0) as comps_short,
 (select min(period_bucket_key) from n where net_purchase_qty>0)    as earliest_short_bucket,
 (select json_agg(t) from (
    select nn.component_id, c.component_name, min(nn.period_bucket_key) first_bucket,
           round(sum(nn.net_purchase_qty)::numeric,1) total_net
    from n nn left join private_core.components c on c.component_id=nn.component_id
    where nn.net_purchase_qty>0
    group by nn.component_id, c.component_name
    order by min(nn.period_bucket_key), sum(nn.net_purchase_qty) desc limit 25) t) as short_components;
-- G2_FILL_PCT = round(100 * (comps_in_netting - comps_short) / comps_in_netting).
```
Latest open purchase-session — warnings + input_integrity + PO drafts (the buy-side story):
```sql
select session_id, session_date, status, rebuild_verifier_drift,
       jsonb_pretty(warnings) as warnings, jsonb_pretty(input_integrity) as input_integrity
from private_core.purchase_session order by created_at desc limit 1;
-- warnings surfaces po_overdue_receipt / po_missing_expected_delivery (real, actionable finds).
-- input_integrity.counts => stale/never-counted RM/PKG (stock-truth trust).
```
```sql
with s as (select session_id from private_core.purchase_session order by created_at desc limit 1)
select count(*) as po_count, round(coalesce(sum(total_cost),0)::numeric,0) as total_cost
from private_core.purchase_session_po po, s where po.session_id=s.session_id;
```

## Committed-demand context (why FG committed=0 is normal, not a bug)
```sql
select
 (select count(*) from private_core.orders_mirror
    where retired_at is null and pickup_at is not null
      and pickup_at>=now() and pickup_at<now()+interval '14 days')  as dated_pickups_next14d,
 (select count(*) from private_core.orders_mirror
    where retired_at is null and pickup_at is null)                 as dateless_open_backlog,  -- staged, invisible to engine demand by design
 (select count(*) from private_core.purchase_orders
    where status='APPROVED_TO_ORDER')                              as approved_to_order_pos;   -- queue-guard input
```

## Gauge fill / severity summary (for Stage 5)
- **G3_FILL_PCT** = round(100 × yesterday actual_output / planned_qty) — 100 if no firmed plan yesterday.
- Overall verdict badge = worst severity across G1/G2/G3 that ran this session.
