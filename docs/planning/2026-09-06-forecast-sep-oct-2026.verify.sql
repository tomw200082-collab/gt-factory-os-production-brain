-- Post-publish verification (read-only). Expected: 1 row published 9a1c6f2e..., old c7e9db2a superseded;
-- Sep sum 11541, Oct sum 12421 (Aug sum 10287 unchanged); daily-demand Sep 7-30 ~= 0.8 x Sep bucket; 0 correction factors.
select version_id, status, published_at, superseded_at from private_core.forecast_versions
 where version_id in ('9a1c6f2e-5b3d-4e8a-9f70-2026090601aa','c7e9db2a-f81f-4903-94de-613d8da571e4');
select period_bucket_key, count(*) lines, round(sum(forecast_quantity)) qty from private_core.forecast_lines
 where version_id='9a1c6f2e-5b3d-4e8a-9f70-2026090601aa' group by 1 order by 1;
select date_trunc('month', day)::date m, round(sum(forecast_qty)) qty, count(distinct item_id) items
  from private_core.fn_forecast_daily_demand('2026-09-07','2026-10-31') group by 1 order by 1;
select count(*) as corr_factors from private_core.planning_policy where key like 'planning.demand.correction_factor.%';
select item_id, min(day) first_short, round(min(projected_on_hand_eod)) worst
  from private_core.fn_compute_daily_fg_projection(current_date, '2026-10-06') where risk_tier='stockout'
 group by 1 order by 2, 1;
