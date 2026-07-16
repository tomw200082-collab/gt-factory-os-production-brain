# Procurement SQL Library

Ready-to-run SQL for the skill, written against the live `private_core` schema (project
`rvadsozabmxkkrktwgnv`). Run via the Supabase MCP `execute_sql` (reads/compute) or `apply_migration`
is NOT used here — these are queries and a couple of explicitly-gated writes. If a column name errors,
the schema evolved: re-introspect with `information_schema.columns` and adjust.

Conventions: `:HORIZON_START` = a date (usually next Sunday or today); replace `:COMPONENT_ID`,
`:ACTOR_UUID`, `:SUPPLIER_ID`, `:WINDOW_DAYS` etc. before running.

## Table of contents
0. Resolve actor & site
1. Pre-flight integrity gates (run all before trusting numbers)
2. ABC / spend ranking (where to focus)
3. ADU + demand variability (per component, from history)
4. Lead-time + lead-time variability (per component, from receipts)
5. Scoped master-data health (only the components in this run)
6. Run the engine (drafts)
7. Read back the latest planning run + recommendations
8. Read back the latest purchase session + POs + lines
9. Buffer recommendation (suggested component_cover_days)
10. GATED writes — buffer override, line edits (Tom approval required)

---

## 0. Resolve actor & site

```sql
select id, display_name, role, status
from private_core.app_users
where status='active' and role in ('admin','owner','planner')
order by role;
-- Confirm with Tom which id to act as; use it as :ACTOR_UUID. site_id defaults to 'GT-MAIN'.
```

---

## 1. Pre-flight integrity gates

### 1-fast. Read the gate off the session itself (backend 0284+)
```sql
select session_id, session_type, session_date, status, created_at,
       rebuild_verifier_drift, input_integrity, warnings
from private_core.purchase_session
where session_type = 'weekly'   -- match the run's scope (verified live 2026-07-16:
                                -- a bare LIMIT 1 returned an off_cycle check session)
order by created_at desc limit 1;
-- input_integrity = forecast{age_days, coverage_end, horizon_end, uncovered_days}
--                  · counts{targets, fresh, stale, never_counted, threshold_days, oldest_age_days}
--                  · verifier_drift — the whole gate, computed at generation time.
-- A fresh session covering this run's scope → §1a–§1c below are redundant.
-- Traces freeze at generation: if a count/receipt/plan change landed since
-- created_at, regenerate before trusting quantities.
```

### 1a. Forecast freshness — is there a published forecast covering the horizon?
```sql
select version_id, cadence, horizon_start_at, horizon_weeks, status,
       published_at, (now()::date - published_at::date) as days_since_published
from private_core.forecast_versions
where status='published'
order by published_at desc nulls last
limit 3;
-- No published row, or horizon_start_at + horizon_weeks not covering the plan window → demand is stale/missing.
```

### 1b. Stock-truth — verifier drift and stale physical counts (stale_count_days = 7)
```sql
-- Most recent planning run's drift (expect 0):
select run_id, executed_at, rebuild_verifier_drift_at_run, status
from private_core.planning_runs order by executed_at desc limit 1;

-- Components whose last physical count is older than the staleness threshold:
-- NOTE (verified 2026-06-25): private_core.physical_counts has NO site_id / created_at.
-- The count timestamp is `snapshot_at`; the dimension is (item_type, item_id). Joined accordingly.
-- TAXONOMY (verified live 2026-07-16): item_type in current_balances,
-- physical_counts AND stock_ledger is 'RM' / 'PKG' / 'FG' — there is NO
-- 'COMPONENT' value anywhere. A previous revision of this file filtered
-- item_type='COMPONENT', which returns ZERO rows and silently passes the
-- staleness gate green. Components = RM + PKG.
with thr as (select (value)::int as d from private_core.planning_policy where key='stale_count_days')
select cb.item_id,
       max(pc.snapshot_at) as last_count_at,
       (now()::date - max(pc.snapshot_at)::date) as age_days
from private_core.current_balances cb
left join private_core.physical_counts pc
       on pc.item_id = cb.item_id and pc.item_type = cb.item_type
where cb.item_type in ('RM','PKG')
group by cb.item_id
having max(pc.snapshot_at) is null
    or (now()::date - max(pc.snapshot_at)::date) > (select d from thr)
order by age_days desc nulls first;
-- Since backend 0284 the session itself snapshots this: read
-- purchase_session.input_integrity (forecast age/coverage + counts summary)
-- instead of recomputing when a fresh session exists (§1-fast).

-- CONTROL — empty ≠ green. Zero rows above proves nothing until this shows
-- the query actually saw components; 0 here means the filter/taxonomy is
-- wrong, NOT that every count is fresh:
select count(*) as components_seen
from private_core.current_balances where item_type in ('RM','PKG');
```

### 1c. Open-PO supply not netted (the double-order trap)
```sql
-- Open PO lines with no expected_receive_date → NOT counted as incoming supply by the engine.
select pol.po_id, pol.component_id, pol.item_id, pol.open_qty, pol.line_status,
       pol.expected_receive_date, po.order_date, po.supplier_id
from private_core.purchase_order_lines pol
join private_core.purchase_orders po on po.po_id = pol.po_id
where pol.line_status='OPEN' and pol.open_qty > 0 and pol.expected_receive_date is null
order by po.order_date;
-- Also read the latest session's own warnings (1c-bis):
select session_id, session_date, status, warnings
from private_core.purchase_session order by created_at desc limit 1;
```

---

## 2. ABC / spend ranking (Pareto — where to spend judgment)

```sql
-- Annualised spend proxy per component = ADU(28d history) × std cost × 365.
-- ADU subquery mirrors §3; std cost from components (fallback to supplier_items).
with usage as (
  select sl.item_id,
         -1.0 * sum(sl.qty_delta) as used_28d
  from private_core.stock_ledger sl
  where sl.item_type in ('RM','PKG')   -- components; ledger has no 'COMPONENT' value
    and sl.post_status='POSTED'
    and sl.qty_delta < 0
    and sl.event_at >= now() - interval '28 days'
  group by sl.item_id
)
select c.component_id, c.component_name, c.criticality,
       coalesce(u.used_28d,0)/28.0 as adu_inv_uom,
       coalesce(c.std_cost_per_inv_uom,0) as unit_cost,
       round( (coalesce(u.used_28d,0)/28.0) * coalesce(c.std_cost_per_inv_uom,0) * 365, 0) as annual_spend_proxy
from private_core.components c
left join usage u on u.item_id = c.component_id
where c.status='ACTIVE' and c.planned_flag=true
order by annual_spend_proxy desc nulls last;
-- Top rows ≈ A items. Concentrate the interview here + on high-CoV (Z) items from §3.
```

---

## 3. ADU + demand variability (per component, from posted history)

Include zero-consumption days so variability isn't understated. `:WINDOW_DAYS` e.g. 56 or 90.

```sql
with days as (
  select generate_series((now()::date - (:WINDOW_DAYS||' days')::interval)::date,
                         now()::date, interval '1 day')::date as d
),
daily as (
  select date(sl.event_at) as d, -1.0*sum(sl.qty_delta) as used
  from private_core.stock_ledger sl
  where sl.item_type in ('RM','PKG') and sl.item_id = :COMPONENT_ID
    and sl.post_status='POSTED' and sl.qty_delta < 0
    and sl.event_at >= now() - (:WINDOW_DAYS||' days')::interval
  group by 1
),
series as (
  select days.d, coalesce(daily.used,0) as used
  from days left join daily on daily.d = days.d
)
select :COMPONENT_ID as component_id,
       round(avg(used),3)                          as adu,
       round(stddev_samp(used),3)                  as sigma_d,
       case when avg(used) > 0
            then round(stddev_samp(used)/avg(used),3) end as cov,   -- <0.5 X, 0.5-1 Y, >=1 Z
       count(*) filter (where used>0)              as active_days,
       count(*)                                    as window_days
from series;
-- To classify the whole catalogue at once, drop the :COMPONENT_ID filter, group by item_id.
```

---

## 4. Lead-time + lead-time variability (per component, from receipts)

```sql
-- Actual lead time and slippage from received PO lines.
select pol.component_id,
       count(*)                                                   as n_receipts,
       round(avg( (pol.actual_first_receipt_at::date - po.order_date) ),2) as avg_lead_days,
       round(stddev_samp( (pol.actual_first_receipt_at::date - po.order_date) ),2) as sigma_lt_days,
       round(avg( (pol.actual_first_receipt_at::date - pol.expected_receive_date) ),2) as avg_slippage_days
from private_core.purchase_order_lines pol
join private_core.purchase_orders po on po.po_id = pol.po_id
where pol.actual_first_receipt_at is not null and pol.component_id is not null
group by pol.component_id
order by n_receipts desc;
-- GT has few placed POs → n_receipts is small. When absent, assume sigma_lt by criticality/supplier
-- (reliable ≈ 10-20% of DLT; unproven/import ≈ 30-50% of DLT) per methodology §3.
```

---

## 5. Scoped master-data health (only the components in THIS run)

Pass the in-scope component ids as an array.

```sql
with scope as (select unnest(array[:COMPONENT_IDS]::text[]) as component_id)
select c.component_id, c.component_name,
       (c.lead_time_days is null)              as missing_lead_time,
       (c.moq_purchase_uom is null)            as missing_moq,
       (c.order_multiple_purchase_uom is null) as missing_order_multiple,
       (c.std_cost_per_inv_uom is null)        as missing_cost,
       (c.primary_supplier_id is null)         as missing_primary_supplier,
       (c.criticality is null)                 as missing_criticality,
       not exists (select 1 from private_core.supplier_items si
                   where si.component_id=c.component_id) as no_supplier_mapping
from private_core.components c
join scope on scope.component_id = c.component_id
order by no_supplier_mapping desc, missing_cost desc;
-- Any TRUE among the scoped rows weakens THIS run's recommendation for that component — surface it.
```

---

## 6. Run the engine (creates DRAFTS — safe; confirm with Tom first, nothing is ordered)

```sql
-- 6a. Fresh planning run (FG net req → component netting → purchase recs):
select * from private_core.fn_execute_planning_run(
  :ACTOR_UUID,                       -- p_actor_user_id
  'skill:procurement-planning',      -- p_trigger_source
  'proc-' || to_char(now(),'YYYYMMDD-HH24MISS'),  -- p_idempotency_key
  :HORIZON_START::date,              -- p_horizon_start_at (e.g. next Sunday)
  (select (value)::int from private_core.planning_policy where key='planning.horizon_weeks')  -- 8
);

-- 6b. Consolidated weekly purchase session (per-supplier draft POs):
select * from private_core.fn_generate_purchase_session(
  :ACTOR_UUID, :HORIZON_START::date, 'weekly'
);
```

---

## 7. Read back the latest planning run + recommendations

```sql
with r as (select run_id from private_core.planning_runs order by executed_at desc limit 1)
select rec.recommendation_type, rec.component_id, rec.item_id, rec.supplier_id,
       rec.required_qty, rec.recommended_qty,
       rec.order_by_date, rec.due_date, rec.shortage_date,
       rec.feasibility_status, rec.recommendation_status,
       rec.blocking_issues, rec.moq_rounding_trace, rec.logic_trace
from private_core.planning_run_recommendations rec, r
where rec.run_id = r.run_id
order by rec.recommendation_type, rec.order_by_date nulls last;

-- Netting detail for one component (why this qty?):
with r as (select run_id from private_core.planning_runs order by executed_at desc limit 1)
select n.component_id, n.period_bucket_key, n.demand_qty, n.on_hand_qty,
       n.open_po_qty, n.net_purchase_qty, n.po_substrate_present
from private_core.planning_run_component_netting n, r
where n.run_id=r.run_id and n.component_id = :COMPONENT_ID
order by n.period_bucket_key;
```

---

## 8. Read back the latest purchase session + POs + lines

```sql
-- 8a. Session header + warnings:
select session_id, session_date, status, horizon_days, consolidation_window_days,
       demand_model_version, warnings
from private_core.purchase_session order by created_at desc limit 1;

-- 8b. Per-supplier draft POs in that session (cash exposure, coverage, ordering deadline):
with s as (select session_id from private_core.purchase_session order by created_at desc limit 1)
select po.session_po_id, po.supplier_id, po.supplier_snapshot, po.tier, po.status,
       po.order_by_date, po.earliest_need_date, po.covered_through_date,
       po.total_cost, po.currency, po.blocking_issues
from private_core.purchase_session_po po, s
where po.session_id = s.session_id
order by po.order_by_date nulls last, po.total_cost desc;

-- 8c. Lines for one draft PO (recommended vs final, coverage trace).
-- Trace v3 (0284) also carries: lt_source, criticality, last_count_age_days
-- (null = never counted), moq, order_multiple, qty_purchase_before_rounding —
-- the trust flags Stage 5's interview triggers read.
select l.session_po_line_id, l.line_label, l.component_id, l.item_id,
       l.recommended_qty, l.final_qty, l.uom, l.unit_cost, l.line_cost,
       l.earliest_need_date, l.is_user_added, l.is_dropped,
       l.coverage_trace->>'lt_source'           as lt_source,
       l.coverage_trace->>'last_count_age_days' as count_age_days,
       l.coverage_trace->>'trace_version'       as trace_v,
       l.coverage_trace
from private_core.purchase_session_po_line l
where l.session_po_id = :SESSION_PO_ID
order by l.line_label;

-- 8d. The paste-ready supplier order message (Hebrew) the engine generated:
select supplier_id, order_document_text
from private_core.purchase_session_po
where session_po_id = :SESSION_PO_ID;
```

---

## 9. Buffer recommendation (suggested component_cover_days per component)

Combine §3 (ADU, σ_D, CoV) and §4 (DLT, σ_LT) with a service-level Z to produce a statistically grounded
cover-days suggestion vs the flat current value. Compute the inputs in SQL, then apply the formula in
methodology §6 in code (so Z and the criticality tier are explicit and reviewable). Skeleton:

```sql
-- Inputs for the buffer formula, one row per in-scope component:
with scope as (select unnest(array[:COMPONENT_IDS]::text[]) as component_id),
days as (select generate_series((now()::date - interval '56 days')::date, now()::date, interval '1 day')::date d),
daily as (
  select sl.item_id, date(sl.event_at) d, -1.0*sum(sl.qty_delta) used
  from private_core.stock_ledger sl
  where sl.item_type in ('RM','PKG') and sl.post_status='POSTED' and sl.qty_delta<0
    and sl.event_at >= now() - interval '56 days'
  group by 1,2),
series as (
  select s.component_id, d.d, coalesce(dd.used,0) used
  from scope s cross join days d
  left join daily dd on dd.item_id=s.component_id and dd.d=d.d),
demand as (
  select component_id, avg(used) adu, stddev_samp(used) sigma_d
  from series group by component_id),
lt as (
  select pol.component_id,
         avg(pol.actual_first_receipt_at::date - po.order_date) avg_lt,
         coalesce(stddev_samp(pol.actual_first_receipt_at::date - po.order_date),0) sigma_lt
  from private_core.purchase_order_lines pol
  join private_core.purchase_orders po on po.po_id=pol.po_id
  where pol.actual_first_receipt_at is not null and pol.component_id is not null
  group by pol.component_id)
select c.component_id, c.component_name, c.criticality,
       d.adu, d.sigma_d,
       case when d.adu>0 then d.sigma_d/d.adu end as cov,
       coalesce(lt.avg_lt, c.lead_time_days,
                (select default_lead_time_days from private_core.suppliers su where su.supplier_id=c.primary_supplier_id),
                14) as dlt_days,
       coalesce(lt.sigma_lt, 0) as sigma_lt_days,
       coalesce((select value from private_core.planning_policy
                 where key='planning.safety.component_cover_days.'||c.component_id),
                (select value from private_core.planning_policy
                 where key='planning.safety.component_cover_days_default')) as current_cover_days
from private_core.components c
join scope sc on sc.component_id=c.component_id
left join demand d on d.component_id=c.component_id
left join lt on lt.component_id=c.component_id
order by c.criticality nulls last;
-- Then in code:  SS = Z × sqrt(DLT×sigma_d² + adu²×sigma_lt²);  suggested_cover_days = ceil(SS/adu).
-- Choose Z from the criticality tier (A:2.05-2.58, B:1.65-1.96, C:1.28-1.48). Compare to current_cover_days.
```

---

## 10. GATED writes — require explicit Tom approval before running

> These mutate policy or the draft session. Present the diff, get a clear "yes", then run. Never auto-run.

### 10a. Set a per-component buffer override
```sql
insert into private_core.planning_policy (key, value, uom, description)
values ('planning.safety.component_cover_days.' || :COMPONENT_ID, :DAYS::text, 'days',
        'Per-component cover override set via procurement-planning skill on '||now()::date||': '||:RATIONALE)
on conflict (key) do update set value=excluded.value, description=excluded.description, updated_at=now();
-- Re-run the planning engine (§6) afterwards so recommendations reflect the new buffer.
```

### 10b. Edit a draft session line (final qty, add, drop)
```sql
update private_core.purchase_session_po_line
set final_qty = :FINAL_QTY, edited_by_user_id = :ACTOR_UUID, edited_at = now()
where session_po_line_id = :SESSION_PO_LINE_ID;

-- Drop a line:   set is_dropped = true, ...
-- Add a line:    insert (..., is_user_added=true) — match the column set in §8c.
```

### 10c. Placement (COMMITTING — real PO). Only after Tom explicitly approves a specific PO.
```sql
select * from private_core.fn_place_purchase_order(
  :PO_ID, :ACTOR_UUID, :ACTOR_SNAPSHOT,
  :PAYMENT_TERMS, :PAYMENT_TERMS_NET_DAYS::int, :PAYMENT_TERMS_EOM::bool,
  :LINE_PRICES::jsonb, :CONFIRM_PRICE_UPDATE::bool
);
-- This is the only step that creates a committed order. The skill stops and asks before this, every time.
```
