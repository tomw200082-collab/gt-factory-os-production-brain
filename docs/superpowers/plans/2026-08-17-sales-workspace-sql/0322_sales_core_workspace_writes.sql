-- ===========================================================================
-- 0322_sales_core_workspace_writes.sql
-- ===========================================================================
-- Sales workspace (portal UI) write layer. Masterprompt 2026-08-17 §5.3/§5.7/§6.2.
--
-- WHY
--   The Today-queue outcome loop needs server-side transactional writes: every
--   mutation writes its lead_event(s) in the same transaction, the first touch
--   stops the SLA clock, and an open lead can never be left without a next
--   touch after an outcome. `won` is never writable by a user — only the future
--   conversion job writes it with order evidence.
--
-- SHAPE
--   1. lead_event.event_type CHECK extended additively: + 'outreach', + 'outcome'.
--   2. sales_core.app_setting — key/value jsonb settings (whatsapp templates, SLA hours).
--   3. Mutation functions, all writing lead + lead_event transactionally:
--        set_lead_status(lead_id, status, reason, actor)   — rejects 'won'
--        add_lead_note(lead_id, note, actor)
--        set_next_touch(lead_id, at, actor)
--        assign_lead(lead_id, assignee, actor)
--        record_outreach(lead_id, channel, actor)
--        record_outcome(lead_id, result, next_touch_at, reason, actor)
--
-- Depends on: 0318 (tables), 0320 (append-only), 0321 (ingest_lead).
-- Rollback posture: additive; functions replaceable; app_setting droppable.
--
-- ACCESS EXCEPTION (deliberate, Tom addendum-2 2026-08-17 §8):
--   Grants here are service_role ONLY - never `authenticated` - because lead
--   rows are PII of non-customers. All access flows through the server-side
--   API (which connects as postgres); the guarded grants document intent
--   without widening exposure.
-- ===========================================================================

begin;

-- 1 ── extend lead_event.event_type additively (never remove a value) ------
alter table sales_core.lead_event
  drop constraint lead_event_event_type_check;
alter table sales_core.lead_event
  add constraint lead_event_event_type_check check (event_type in (
    'created','status_change','note','assignment','next_touch_set',
    'alert_sent','converted','matched_existing_customer','imported',
    'outreach','outcome'));

-- 2 ── app_setting ---------------------------------------------------------
create table if not exists sales_core.app_setting (
  key         text primary key,
  value       jsonb not null,
  updated_at  timestamptz not null default now()
);

comment on table sales_core.app_setting is
  'Sales-workspace settings (key/value jsonb). Keys: sla_hours {"hours":24}; whatsapp_templates {"new_lead":..,"reminder":..,"returning_customer":..}. Masterprompt 2026-08-17 §5.7.';

insert into sales_core.app_setting (key, value) values
  ('sla_hours', '{"hours": 24}'::jsonb),
  ('whatsapp_templates', jsonb_build_object(
    'new_lead',           'היי {{name}}, כאן תום מ-GT Everyday 🍃 ראיתי שהשארת פרטים אצלנו — מתי נוח לדבר קצר על בסיסי המשקאות שלנו לעסק שלך?',
    'reminder',           'היי {{name}}, תום מ-GT Everyday 🍃 רק מוודא שקיבלת את הפרטים — אשמח לקדם אם זה עדיין רלוונטי.',
    'returning_customer', 'היי {{name}}, תום מ-GT Everyday 🍃 איזה כיף לראות אותך שוב! ראיתי שהשארת פרטים — מה נוכל לשפר או לחדש אצלכם?'
  ))
on conflict (key) do nothing;

create or replace function sales_core.set_app_setting(p_key text, p_value jsonb)
returns void
language plpgsql
as $fn$
begin
  insert into sales_core.app_setting (key, value, updated_at)
  values (p_key, p_value, now())
  on conflict (key) do update set value = excluded.value, updated_at = now();
end;
$fn$;

-- 3 ── shared guard --------------------------------------------------------
-- Locks the lead row, raises SALES_LEAD_NOT_FOUND when absent.
create or replace function sales_core.lock_lead(p_lead_id uuid)
returns sales_core.lead
language plpgsql
as $fn$
declare
  v_lead sales_core.lead;
begin
  select * into v_lead from sales_core.lead where id = p_lead_id for update;
  if not found then
    raise exception 'SALES_LEAD_NOT_FOUND: %', p_lead_id using errcode = 'P0001';
  end if;
  return v_lead;
end;
$fn$;

-- Sets first_touch_at once (the SLA stop). Returns true when this call set it.
create or replace function sales_core.touch_first(p_lead_id uuid)
returns boolean
language plpgsql
as $fn$
declare
  v_set boolean := false;
begin
  update sales_core.lead
     set first_touch_at = now()
   where id = p_lead_id and first_touch_at is null;
  v_set := found;
  return v_set;
end;
$fn$;

-- 4 ── mutation functions --------------------------------------------------

-- set_lead_status: 'working' or 'lost' (+reason) only. 'won' is evidence-only
-- (masterprompt §5.3/D12) — the conversion job writes it, never a user.
create or replace function sales_core.set_lead_status(
  p_lead_id uuid,
  p_status  text,
  p_reason  text,
  p_actor   text
) returns table (lead_id uuid, status text)
language plpgsql
as $fn$
declare
  v_lead sales_core.lead;
begin
  v_lead := sales_core.lock_lead(p_lead_id);

  if p_status = 'won' then
    raise exception 'SALES_WON_IS_EVIDENCE_ONLY: won is written by the conversion job, never by a user'
      using errcode = 'P0001';
  end if;
  if p_status not in ('working','lost') then
    raise exception 'SALES_INVALID_STATUS: %', p_status using errcode = 'P0001';
  end if;
  if p_status = 'lost' and (p_reason is null or p_reason = '') then
    raise exception 'SALES_LOST_REQUIRES_REASON' using errcode = 'P0001';
  end if;

  update sales_core.lead
     set status      = p_status,
         lost_reason = case when p_status = 'lost' then p_reason else lost_reason end
   where id = p_lead_id;

  insert into sales_core.lead_event (lead_id, event_type, payload, actor)
  values (p_lead_id, 'status_change',
          jsonb_build_object('from', v_lead.status, 'to', p_status, 'reason', p_reason),
          p_actor);

  perform sales_core.touch_first(p_lead_id);

  return query select l.id, l.status from sales_core.lead l where l.id = p_lead_id;
end;
$fn$;

create or replace function sales_core.add_lead_note(
  p_lead_id uuid,
  p_note    text,
  p_actor   text
) returns table (lead_id uuid, event_id uuid)
language plpgsql
as $fn$
declare
  v_event_id uuid;
begin
  perform sales_core.lock_lead(p_lead_id);
  if p_note is null or p_note = '' then
    raise exception 'SALES_NOTE_EMPTY' using errcode = 'P0001';
  end if;

  insert into sales_core.lead_event (lead_id, event_type, payload, actor)
  values (p_lead_id, 'note', jsonb_build_object('note', p_note), p_actor)
  returning id into v_event_id;

  perform sales_core.touch_first(p_lead_id);
  return query select p_lead_id, v_event_id;
end;
$fn$;

create or replace function sales_core.set_next_touch(
  p_lead_id uuid,
  p_at      timestamptz,
  p_actor   text
) returns table (lead_id uuid, next_touch_at timestamptz)
language plpgsql
as $fn$
begin
  perform sales_core.lock_lead(p_lead_id);
  if p_at is null then
    raise exception 'SALES_NEXT_TOUCH_REQUIRED' using errcode = 'P0001';
  end if;

  update sales_core.lead set next_touch_at = p_at where id = p_lead_id;

  insert into sales_core.lead_event (lead_id, event_type, payload, actor)
  values (p_lead_id, 'next_touch_set', jsonb_build_object('at', p_at), p_actor);

  return query select l.id, l.next_touch_at from sales_core.lead l where l.id = p_lead_id;
end;
$fn$;

create or replace function sales_core.assign_lead(
  p_lead_id  uuid,
  p_assignee text,
  p_actor    text
) returns table (lead_id uuid, assignee text)
language plpgsql
as $fn$
begin
  perform sales_core.lock_lead(p_lead_id);

  update sales_core.lead set assignee = nullif(p_assignee, '') where id = p_lead_id;

  insert into sales_core.lead_event (lead_id, event_type, payload, actor)
  values (p_lead_id, 'assignment', jsonb_build_object('assignee', nullif(p_assignee, '')), p_actor);

  return query select l.id, l.assignee from sales_core.lead l where l.id = p_lead_id;
end;
$fn$;

-- record_outreach: the user tapped call / WhatsApp. Intent only — does NOT
-- stop the SLA clock (only an outcome / note / status change does, §5.3).
create or replace function sales_core.record_outreach(
  p_lead_id uuid,
  p_channel text,
  p_actor   text
) returns table (lead_id uuid, event_id uuid)
language plpgsql
as $fn$
declare
  v_event_id uuid;
begin
  perform sales_core.lock_lead(p_lead_id);
  if p_channel not in ('call','whatsapp','email') then
    raise exception 'SALES_INVALID_CHANNEL: %', p_channel using errcode = 'P0001';
  end if;

  insert into sales_core.lead_event (lead_id, event_type, payload, actor)
  values (p_lead_id, 'outreach', jsonb_build_object('channel', p_channel), p_actor)
  returning id into v_event_id;

  return query select p_lead_id, v_event_id;
end;
$fn$;

-- record_outcome: the whole §5.3 loop, server-side, one transaction.
--   result ∈ answered_progressing | no_answer | whatsapp_sent | lost
--   - answered_progressing: new→working; p_next_touch_at required.
--   - no_answer:            next touch = coalesce(p_next_touch_at, tomorrow 09:00 IL).
--   - whatsapp_sent:        next touch = coalesce(p_next_touch_at, +2 days 09:00 IL).
--   - lost:                 p_reason required; status→lost; leaves the queue.
--   Every path writes 'outcome'; touches first_touch_at; and an OPEN lead can
--   never be left without next_touch_at (raised, not hoped).
create or replace function sales_core.record_outcome(
  p_lead_id       uuid,
  p_result        text,
  p_next_touch_at timestamptz,
  p_reason        text,
  p_actor         text
) returns table (lead_id uuid, status text, next_touch_at timestamptz, first_touch_at timestamptz)
language plpgsql
as $fn$
declare
  v_lead  sales_core.lead;
  v_next  timestamptz;
begin
  v_lead := sales_core.lock_lead(p_lead_id);

  if p_result not in ('answered_progressing','no_answer','whatsapp_sent','lost') then
    raise exception 'SALES_INVALID_OUTCOME: %', p_result using errcode = 'P0001';
  end if;

  if p_result = 'lost' then
    if p_reason is null or p_reason = '' then
      raise exception 'SALES_LOST_REQUIRES_REASON' using errcode = 'P0001';
    end if;
    update sales_core.lead set status = 'lost', lost_reason = p_reason where id = p_lead_id;
    insert into sales_core.lead_event (lead_id, event_type, payload, actor)
    values (p_lead_id, 'status_change',
            jsonb_build_object('from', v_lead.status, 'to', 'lost', 'reason', p_reason),
            p_actor);
  else
    -- next-touch date: explicit wins; defaults tomorrow (no_answer) / +2d (whatsapp_sent).
    -- 06:00 UTC = 09:00 Israel (IDT) — a morning queue slot, not midnight.
    v_next := coalesce(
      p_next_touch_at,
      case p_result
        when 'no_answer'     then date_trunc('day', now()) + interval '1 day 6 hours'
        when 'whatsapp_sent' then date_trunc('day', now()) + interval '2 days 6 hours'
      end);
    if v_next is null then
      raise exception 'SALES_NEXT_TOUCH_REQUIRED: open lead cannot be left without a next touch'
        using errcode = 'P0001';
    end if;

    if p_result = 'answered_progressing' and v_lead.status = 'new' then
      update sales_core.lead set status = 'working' where id = p_lead_id;
      insert into sales_core.lead_event (lead_id, event_type, payload, actor)
      values (p_lead_id, 'status_change',
              jsonb_build_object('from', 'new', 'to', 'working', 'reason', null),
              p_actor);
    end if;

    update sales_core.lead set next_touch_at = v_next where id = p_lead_id;
    insert into sales_core.lead_event (lead_id, event_type, payload, actor)
    values (p_lead_id, 'next_touch_set', jsonb_build_object('at', v_next), p_actor);
  end if;

  insert into sales_core.lead_event (lead_id, event_type, payload, actor)
  values (p_lead_id, 'outcome',
          jsonb_build_object('result', p_result, 'reason', p_reason, 'next_touch_at', p_next_touch_at),
          p_actor);

  perform sales_core.touch_first(p_lead_id);

  -- invariant: open lead after any outcome carries a next touch
  if exists (select 1 from sales_core.lead l
             where l.id = p_lead_id and l.status in ('new','working') and l.next_touch_at is null) then
    raise exception 'SALES_OPEN_LEAD_WITHOUT_NEXT_TOUCH' using errcode = 'P0001';
  end if;

  return query
    select l.id, l.status, l.next_touch_at, l.first_touch_at
    from sales_core.lead l where l.id = p_lead_id;
end;
$fn$;

-- grants: service_role ONLY (PII exception — see header) --------------------
do $$
begin
  if exists (select 1 from pg_roles where rolname = 'service_role') then
    grant usage on schema sales_core to service_role;
    grant execute on function sales_core.set_lead_status(uuid, text, text, text) to service_role;
    grant execute on function sales_core.add_lead_note(uuid, text, text) to service_role;
    grant execute on function sales_core.set_next_touch(uuid, timestamptz, text) to service_role;
    grant execute on function sales_core.assign_lead(uuid, text, text) to service_role;
    grant execute on function sales_core.record_outreach(uuid, text, text) to service_role;
    grant execute on function sales_core.record_outcome(uuid, text, timestamptz, text, text) to service_role;
    grant execute on function sales_core.set_app_setting(text, jsonb) to service_role;
  end if;
end $$;

commit;
