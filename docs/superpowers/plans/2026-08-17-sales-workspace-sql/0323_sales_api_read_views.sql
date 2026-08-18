-- ===========================================================================
-- 0323_sales_api_read_views.sql
-- ===========================================================================
-- Read layer for the sales workspace portal UI. Masterprompt 2026-08-17 §6.2.
--
-- WHY
--   The portal reads through Fastify against api_read views only. Five views:
--   the full lead table, the event timeline, orgs, the Today queue, and the
--   week stats strip. Derivations (age, SLA state, overdue) live here so every
--   consumer shares one truth. Per-assignee filtering is bound in the API
--   handler (portal repo doctrine: the API is the permission boundary; the
--   view exposes `assignee` as a column and stays unfiltered).
--
-- Depends on: 0318, 0322 (app_setting for sla_hours).
-- Rollback posture: views only — drop-and-recreate safe, no data.
--
-- ACCESS EXCEPTION (deliberate, Tom addendum-2 2026-08-17 §8):
--   These views are granted to service_role ONLY — never `authenticated`,
--   diverging from the repo's usual view-grant convention — because lead rows
--   are PII of non-customers and `authenticated` would expose names/phones to
--   every factory user. All reads flow through the server-side API.
-- ===========================================================================

begin;

-- helper: current SLA hours (default 24) --------------------------------
create or replace function sales_core.sla_hours()
returns integer
language sql
stable
as $fn$
  select coalesce((value ->> 'hours')::int, 24)
  from sales_core.app_setting where key = 'sla_hours';
$fn$;

-- 1 ── v_sales_leads ------------------------------------------------------
create or replace view api_read.v_sales_leads as
select
  l.id,
  l.org_id,
  o.display_name                                   as org_name,
  l.contact_name,
  l.phone_e164,
  l.email,
  l.source,
  l.campaign_name,
  l.ad_name,
  l.platform,
  l.is_organic,
  l.status,
  l.lost_reason,
  l.assignee,
  l.next_touch_at,
  l.first_touch_at,
  l.possible_duplicate_of,
  l.converted_order_ref,
  l.converted_amount,
  l.created_at,
  -- An org counts as an existing customer when it carries either a Shopify
  -- customer reference (set by ingest_lead when a live match is made) or a
  -- dated tracker snapshot. The 2026-08-10 import matched its three customers
  -- by the tracker's customer_key and set only the snapshot, so keying this on
  -- shopify_customer_id alone would leave the returning-customer card dead.
  (o.shopify_customer_id is not null
     or o.shopify_snapshot_at is not null)         as is_existing_customer,
  o.shopify_customer_id,
  o.shopify_snapshot,
  o.shopify_snapshot_at,
  greatest(0, floor(extract(epoch from (now() - l.created_at)) / 86400))::int
                                                   as age_days,
  l.created_at + make_interval(hours => sales_core.sla_hours())
                                                   as sla_deadline_at,
  case
    when l.first_touch_at is not null then null    -- badge disappears after first touch (§5.3)
    when now() > l.created_at + make_interval(hours => sales_core.sla_hours()) then 'overdue'
    else 'within'
  end                                              as sla_state,
  (l.status in ('new','working')
     and l.next_touch_at is not null
     and l.next_touch_at <= now())                 as next_touch_overdue
from sales_core.lead l
join sales_core.org  o on o.id = l.org_id;

comment on view api_read.v_sales_leads is
  'Sales workspace lead table (0323). One row per lead, org context joined, with derived age_days, sla_deadline_at, sla_state (null after first touch — §5.3), next_touch_overdue. Unfiltered: assignee scoping is bound in the API handler. Masterprompt 2026-08-17 §5.4.';

-- 2 ── v_sales_lead_events ------------------------------------------------
create or replace view api_read.v_sales_lead_events as
select
  e.id,
  e.lead_id,
  e.event_type,
  e.payload,
  e.actor,
  e.created_at
from sales_core.lead_event e;

comment on view api_read.v_sales_lead_events is
  'Sales lead event timeline (0323). Append-only history; order by created_at in the consumer. Masterprompt 2026-08-17 §5.4.';

-- 3 ── v_sales_orgs -------------------------------------------------------
create or replace view api_read.v_sales_orgs as
select
  o.id,
  o.display_name,
  o.phone_e164,
  o.email,
  o.email_domain,
  o.city,
  o.shopify_customer_id,
  (o.shopify_customer_id is not null
     or o.shopify_snapshot_at is not null)     as is_existing_customer,
  o.shopify_snapshot,
  o.shopify_snapshot_at,
  o.created_at,
  count(l.id)                                  as lead_count,
  max(coalesce(e.last_event_at, l.created_at)) as last_activity_at
from sales_core.org o
left join sales_core.lead l on l.org_id = o.id
left join lateral (
  select max(ev.created_at) as last_event_at
  from sales_core.lead_event ev
  where ev.lead_id = l.id
) e on true
group by o.id;

comment on view api_read.v_sales_orgs is
  'Sales workspace org list (0323). One row per business: identity, customer badge, lead_count, last_activity_at. Masterprompt 2026-08-17 §5.5.';

-- 4 ── v_sales_today ------------------------------------------------------
-- The Today queue (§5.2). Item types in display order:
--   1 conversion        — won, converted event within the last 7 days (celebration)
--   2 returning_customer— new lead on an org that is an existing customer
--   3 new_lead          — status=new, no first touch yet
--   4 due_follow_up     — open lead, next_touch_at <= now
-- Per-assignee scoping (assignee = X or assignee is null) binds in the handler.
create or replace view api_read.v_sales_today as
select
  l.id                                             as lead_id,
  case
    when l.status = 'won'
     and c.converted_at >= now() - interval '7 days' then 'conversion'
    when l.status = 'new' and l.first_touch_at is null
     and (o.shopify_customer_id is not null
          or o.shopify_snapshot_at is not null)       then 'returning_customer'
    when l.status = 'new' and l.first_touch_at is null then 'new_lead'
    else 'due_follow_up'
  end                                              as item_type,
  l.org_id,
  o.display_name                                   as org_name,
  l.contact_name,
  l.phone_e164,
  l.email,
  l.campaign_name,
  l.platform,
  l.status,
  l.assignee,
  l.next_touch_at,
  l.first_touch_at,
  l.created_at,
  -- An org counts as an existing customer when it carries either a Shopify
  -- customer reference (set by ingest_lead when a live match is made) or a
  -- dated tracker snapshot. The 2026-08-10 import matched its three customers
  -- by the tracker's customer_key and set only the snapshot, so keying this on
  -- shopify_customer_id alone would leave the returning-customer card dead.
  (o.shopify_customer_id is not null
     or o.shopify_snapshot_at is not null)         as is_existing_customer,
  o.shopify_snapshot,
  o.shopify_snapshot_at,
  l.converted_order_ref,
  l.converted_amount,
  c.converted_at,
  l.created_at + make_interval(hours => sales_core.sla_hours())
                                                   as sla_deadline_at,
  case
    when l.first_touch_at is not null then null
    when now() > l.created_at + make_interval(hours => sales_core.sla_hours()) then 'overdue'
    else 'within'
  end                                              as sla_state
from sales_core.lead l
join sales_core.org o on o.id = l.org_id
left join lateral (
  select max(ev.created_at) as converted_at
  from sales_core.lead_event ev
  where ev.lead_id = l.id and ev.event_type = 'converted'
) c on true
where
  (l.status = 'won' and c.converted_at >= now() - interval '7 days')
  or (l.status = 'new' and l.first_touch_at is null)
  or (l.status in ('new','working') and l.next_touch_at is not null and l.next_touch_at <= now());

comment on view api_read.v_sales_today is
  'The Today queue (0323). Rows only while actionable: recent conversions (7d celebration window), returning-customer new leads, untouched new leads, due follow-ups. item_type drives display order in the portal. Unfiltered — assignee scoping binds in the API handler. Masterprompt 2026-08-17 §5.2.';

-- 5 ── v_sales_week_stats -------------------------------------------------
create or replace view api_read.v_sales_week_stats as
select
  count(*) filter (where l.created_at >= date_trunc('week', now()))                as week_new_leads,
  count(*) filter (where l.status = 'working')                                     as working_now,
  count(*) filter (where l.status = 'won'
                     and c.converted_at >= date_trunc('week', now()))              as week_converted
from sales_core.lead l
left join lateral (
  select max(ev.created_at) as converted_at
  from sales_core.lead_event ev
  where ev.lead_id = l.id and ev.event_type = 'converted'
) c on true;

comment on view api_read.v_sales_week_stats is
  'Today-screen stats strip (0323): leads created this ISO week, leads in working now, conversions this ISO week. One row. Masterprompt 2026-08-17 §5.2.';

-- grants: service_role ONLY (PII exception — see header). Guarded so local
-- vanilla Postgres pgTAP runs pass. Deliberately NOT granted to authenticated.
do $$
begin
  if exists (select 1 from pg_roles where rolname = 'service_role') then
    grant select on api_read.v_sales_leads,
                    api_read.v_sales_lead_events,
                    api_read.v_sales_orgs,
                    api_read.v_sales_today,
                    api_read.v_sales_week_stats to service_role;
  end if;
end $$;

commit;
