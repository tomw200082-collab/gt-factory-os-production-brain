# Sales leads — Phase 1 (schema) + Phase 2 (import) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up the isolated `sales_core` schema and load every lead GT has ever received — 188 rows including the ~60 that arrived after the old pipeline died on 2026-06-07 and were never seen — each matched against Shopify so Tom can tell a stranger from a sleeping customer.

**Architecture:** One migration creates three tables (`org`, `lead`, `lead_event`) plus the shared logic every write path depends on: an Israeli phone normaliser, an append-only guard on the event log, and an org-matching function. Correctness lives in the database as functions, triggers and CHECK constraints, so the poller (Phase 3), the generic ingest route and this import script cannot drift apart or bypass a rule. One `tsx` script then parses the Meta Leads Center export, fetches Shopify customers once, and writes leads through that shared logic.

**Tech Stack:** Postgres (Supabase), pgTAP + `pg_prove`, TypeScript run via `tsx`, `pg` client, Shopify Admin GraphQL `2025-07`, vitest.

**Repos and branch:** implementation lands in `gt-factory-os` on branch `claude/sales-system-planning-th2gna`. The spec lives in `gt-factory-os-production-brain` at `docs/superpowers/specs/2026-08-10-sales-leads-pipeline-design.md`.

## Global Constraints

- **Module isolation.** Everything lives in schema `sales_core`. No foreign key, view, trigger or query may reference `private_core.stock_ledger`, `balance_anchors`, `bom_*`, `items` or `components`. Violating this is a stop condition, not a code review comment.
- **Never copy Shopify customer master.** `org.shopify_customer_id` is a reference. Names, spend and order history are read live or stored as an explicitly dated snapshot — never as an undated fact.
- **No email to anyone but Tom.** Phase 1–2 send no email at all. Imports never trigger alerts.
- **`SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` stays `false`.** Nothing here touches it.
- **`lead_event` is append-only.** Corrections are new, opposite events. Enforced by trigger.
- **Personal data does not enter git.** The export CSV is read from a path outside the repo and is never committed. `.gitignore` covers `*.csv` at repo root by the end of Task 5.
- **Migration numbering:** next free number is `0318`. Follow the existing header style — a `WHY` section explaining the failure the change prevents, as in `0308_shopify_sync_health_monitor.sql`.
- **pgTAP tests are self-contained:** fixtures inlined, everything inside `begin; … rollback;`.

---

### Task 1: Migration 0318 — schema, tables, constraints

**Files:**
- Create: `db/migrations/0318_sales_core_leads.sql`
- Create: `db/tests/0318_sales_core_leads.test.sql`
- Modify: `package.json` (add `db:apply:0318` and `db:test:0318` scripts)

**Interfaces:**
- Consumes: nothing.
- Produces: schema `sales_core` with tables `org(id uuid, display_name text, phone_e164 text, phone_raw text, email text, email_domain text, city text, shopify_customer_id text, shopify_snapshot jsonb, shopify_snapshot_at timestamptz, created_at timestamptz, updated_at timestamptz)`, `lead(id uuid, org_id uuid, source text, external_id text, contact_name text, phone_raw text, phone_e164 text, email text, campaign_name text, ad_name text, form_id text, form_name text, platform text, is_organic boolean, status text, lost_reason text, assignee text, next_touch_at timestamptz, first_touch_at timestamptz, possible_duplicate_of uuid, converted_order_ref text, converted_amount numeric, created_at timestamptz)`, `lead_event(id uuid, lead_id uuid, event_type text, payload jsonb, actor text, created_at timestamptz)`.

- [ ] **Step 1: Write the failing structural test**

Create `db/tests/0318_sales_core_leads.test.sql`:

```sql
-- ===========================================================================
-- 0318_sales_core_leads.test.sql
-- ===========================================================================
-- pgTAP tests for 0318_sales_core_leads.sql.
--
-- Structural block — schema / tables / columns / constraints / indexes
-- S-tests          — behavioural tests for the invariants that can break
--
--   S1  won requires order evidence          -> S1a, S1b
--   S2  lost requires a reason               -> S2a, S2b
--   S3  (source, external_id) is unique      -> S3a
--   S4  status CHECK locked                  -> S4a
--   S5  sales_core references no factory core-> S5a
--
-- Run with:
--   pg_prove -d "$DATABASE_URL" db/tests/0318_sales_core_leads.test.sql
--
-- Self-contained: fixtures inlined, everything inside begin/rollback.
-- ===========================================================================

begin;

create extension if not exists pgtap;

select plan(18);

-- ---------------------------------------------------------------- structural
select has_schema('sales_core');
select has_table('sales_core', 'org');
select has_table('sales_core', 'lead');
select has_table('sales_core', 'lead_event');

select has_column('sales_core', 'org', 'shopify_customer_id');
select has_column('sales_core', 'org', 'shopify_snapshot_at');
select has_column('sales_core', 'lead', 'phone_e164');
select has_column('sales_core', 'lead', 'next_touch_at');
select has_column('sales_core', 'lead', 'converted_order_ref');

select col_type_is('sales_core', 'org', 'shopify_snapshot', 'jsonb');
select col_type_is('sales_core', 'lead_event', 'payload', 'jsonb');

-- ------------------------------------------------------------------- S-tests
insert into sales_core.org (id, display_name)
values ('11111111-1111-1111-1111-111111111111', 'Test Cafe');

-- S1a: won without order evidence is rejected
select throws_ok(
  $$insert into sales_core.lead (org_id, source, external_id, contact_name, status)
    values ('11111111-1111-1111-1111-111111111111','test','s1a','A','won')$$,
  '23514',
  null,
  'S1a: status won without converted_order_ref is rejected'
);

-- S1b: won with order evidence is accepted
select lives_ok(
  $$insert into sales_core.lead (org_id, source, external_id, contact_name, status, converted_order_ref)
    values ('11111111-1111-1111-1111-111111111111','test','s1b','B','won','#1001')$$,
  'S1b: status won with converted_order_ref is accepted'
);

-- S2a: lost without a reason is rejected
select throws_ok(
  $$insert into sales_core.lead (org_id, source, external_id, contact_name, status)
    values ('11111111-1111-1111-1111-111111111111','test','s2a','C','lost')$$,
  '23514',
  null,
  'S2a: status lost without lost_reason is rejected'
);

-- S2b: lost with a reason is accepted
select lives_ok(
  $$insert into sales_core.lead (org_id, source, external_id, contact_name, status, lost_reason)
    values ('11111111-1111-1111-1111-111111111111','test','s2b','D','lost','too expensive')$$,
  'S2b: status lost with lost_reason is accepted'
);

-- S3a: duplicate (source, external_id) is rejected
insert into sales_core.lead (org_id, source, external_id, contact_name)
values ('11111111-1111-1111-1111-111111111111','facebook','dup-1','E');
select throws_ok(
  $$insert into sales_core.lead (org_id, source, external_id, contact_name)
    values ('11111111-1111-1111-1111-111111111111','facebook','dup-1','F')$$,
  '23505',
  null,
  'S3a: (source, external_id) is unique'
);

-- S4a: unknown status is rejected
select throws_ok(
  $$insert into sales_core.lead (org_id, source, external_id, contact_name, status)
    values ('11111111-1111-1111-1111-111111111111','test','s4a','G','maybe')$$,
  '23514',
  null,
  'S4a: status CHECK rejects unknown values'
);

-- S5a: no foreign key from sales_core reaches factory core
select is_empty(
  $$select 1
    from pg_constraint c
    join pg_class child on child.oid = c.conrelid
    join pg_namespace cn on cn.oid = child.relnamespace
    join pg_class parent on parent.oid = c.confrelid
    join pg_namespace pn on pn.oid = parent.relnamespace
    where c.contype = 'f'
      and cn.nspname = 'sales_core'
      and pn.nspname <> 'sales_core'$$,
  'S5a: sales_core has no foreign key outside its own schema'
);

select * from finish();
rollback;
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pg_prove -d "$DATABASE_URL" db/tests/0318_sales_core_leads.test.sql`
Expected: FAIL — `schema "sales_core" does not exist`.

- [ ] **Step 3: Write the migration**

Create `db/migrations/0318_sales_core_leads.sql`:

```sql
-- 0318_sales_core_leads.sql
--
-- The sales module's foundation: businesses, leads, and an append-only history.
--
-- WHY
--
-- On 2026-06-07 at 20:37Z a Facebook OAuth token in Make expired. The lead
-- pipeline stopped that instant, wrote nothing further, and told no one. By the
-- time anyone noticed, two months and roughly sixty paid leads had gone by,
-- retrievable only because Meta happens to keep leads for ninety days. The
-- leads were never lost because the system was complex. They were lost because
-- there was no system — only a spreadsheet at the end of a credential that
-- could die quietly.
--
-- This migration gives leads a home that outlives any credential, and puts the
-- rules where no future caller can skip them.
--
-- SHAPE
--
--   org        — the business. A lead is an event that happens TO a business;
--                churn, account value and white-space are all questions about
--                the business, not about the form submission. The live form
--                asks only for a name and a phone, so who is calling can only
--                be established by matching — which is what org exists for.
--                shopify_customer_id is a REFERENCE. Customer master stays in
--                Shopify; we never mirror it. Any Shopify context we cache is
--                stamped with the moment it was read.
--
--   lead       — one entry event. unique (source, external_id) makes every
--                write path idempotent, which is what lets the Phase 3 poller
--                overlap its time windows without fear of duplicates.
--
--   lead_event — append-only history, same doctrine as stock_ledger:
--                corrections are new, opposite events, never edits.
--
-- TWO RULES ENCODED AS CONSTRAINTS RATHER THAN AS UI
--
--   1. status='won' REQUIRES converted_order_ref. Winning is not something a
--      person remembers to click; it is something Shopify proves. A pipeline
--      whose success metric can be typed in is a pipeline that lies.
--   2. status='lost' REQUIRES lost_reason. A lost lead with no reason teaches
--      nothing and is indistinguishable from a forgotten one.
--
-- Isolated by construction: no foreign key leaves this schema, and nothing here
-- reads or writes the ledger, balances, items or BOMs.

create schema if not exists sales_core;

create table sales_core.org (
  id                    uuid primary key default gen_random_uuid(),
  display_name          text not null,
  phone_raw             text,
  phone_e164            text,
  email                 text,
  email_domain          text,
  city                  text,
  shopify_customer_id   text,
  shopify_snapshot      jsonb,
  shopify_snapshot_at   timestamptz,
  created_at            timestamptz not null default now(),
  updated_at            timestamptz not null default now()
);

create unique index org_shopify_customer_id_key
  on sales_core.org (shopify_customer_id)
  where shopify_customer_id is not null;
create index org_phone_e164_idx on sales_core.org (phone_e164);
create index org_email_idx      on sales_core.org (lower(email));

create table sales_core.lead (
  id                    uuid primary key default gen_random_uuid(),
  org_id                uuid not null references sales_core.org (id),
  source                text not null,
  external_id           text not null,
  contact_name          text,
  phone_raw             text,
  phone_e164            text,
  email                 text,
  campaign_name         text,
  ad_name               text,
  form_id               text,
  form_name             text,
  platform              text,
  is_organic            boolean,
  status                text not null default 'new'
                          check (status in ('new','working','won','lost')),
  lost_reason           text,
  assignee              text,
  next_touch_at         timestamptz,
  first_touch_at        timestamptz,
  possible_duplicate_of uuid references sales_core.lead (id),
  converted_order_ref   text,
  converted_amount      numeric,
  created_at            timestamptz not null default now(),

  constraint lead_won_requires_evidence
    check (status <> 'won' or converted_order_ref is not null),
  constraint lead_lost_requires_reason
    check (status <> 'lost' or (lost_reason is not null and lost_reason <> '')),
  constraint lead_source_external_id_key unique (source, external_id)
);

create index lead_org_id_idx     on sales_core.lead (org_id);
create index lead_status_idx     on sales_core.lead (status);
create index lead_phone_e164_idx on sales_core.lead (phone_e164);
create index lead_open_idx       on sales_core.lead (status)
  where status in ('new','working');

create table sales_core.lead_event (
  id          uuid primary key default gen_random_uuid(),
  lead_id     uuid not null references sales_core.lead (id),
  event_type  text not null check (event_type in (
                'created','status_change','note','assignment','next_touch_set',
                'alert_sent','converted','matched_existing_customer','imported')),
  payload     jsonb not null default '{}'::jsonb,
  actor       text not null default 'system',
  created_at  timestamptz not null default now()
);

create index lead_event_lead_id_idx on sales_core.lead_event (lead_id, created_at);
```

- [ ] **Step 4: Add the npm scripts**

In `package.json`, next to the other `db:apply:*` / `db:test:*` entries:

```json
"db:apply:0318": "psql \"$DATABASE_URL\" -v ON_ERROR_STOP=1 -f db/migrations/0318_sales_core_leads.sql",
"db:test:0318": "pg_prove -d \"$DATABASE_URL\" db/tests/0318_sales_core_leads.test.sql",
```

- [ ] **Step 5: Apply and run the test to verify it passes**

Run: `npm run db:apply:0318 && npm run db:test:0318`
Expected: PASS, 18/18.

- [ ] **Step 6: Commit**

```bash
git add db/migrations/0318_sales_core_leads.sql db/tests/0318_sales_core_leads.test.sql package.json
git commit -m "feat(sales): sales_core schema — org, lead, append-only lead_event

Won requires order evidence and lost requires a reason, both as CHECK
constraints rather than UI conventions, so the pipeline's success metric
cannot be typed in by hand."
```

---

### Task 2: Phone normalisation, in the database

**Files:**
- Create: `db/migrations/0319_sales_core_phone_normalisation.sql`
- Create: `db/tests/0319_sales_core_phone_normalisation.test.sql`
- Modify: `package.json`

**Interfaces:**
- Consumes: schema from Task 1.
- Produces: `sales_core.normalize_phone_il(raw text) returns text` and BEFORE INSERT/UPDATE triggers on `sales_core.lead` and `sales_core.org` that populate `phone_e164` from `phone_raw`.

Why in SQL and not in the import script: the poller, the generic ingest route, the portal's manual-entry form and this script all write phones. One normaliser in the database is the only version that cannot be forgotten by the third caller.

- [ ] **Step 1: Write the failing test**

Create `db/tests/0319_sales_core_phone_normalisation.test.sql`. Every case below is taken from the real 2026-08-10 export:

```sql
begin;
create extension if not exists pgtap;
select plan(12);

select is(sales_core.normalize_phone_il('+972526380055'), '+972526380055',
  'already correct E.164 is unchanged');

-- The defect in roughly half the export: an extra zero after the country code.
select is(sales_core.normalize_phone_il('+9720526380055'), '+972526380055',
  'the +9720 double-zero defect is collapsed');

select is(sales_core.normalize_phone_il('p:+972526380055'), '+972526380055',
  'the Meta p: prefix is stripped');

select is(sales_core.normalize_phone_il('052-638-0055'), '+972526380055',
  'local format with dashes is converted');

select is(sales_core.normalize_phone_il('052 638 0055'), '+972526380055',
  'local format with spaces is converted');

select is(sales_core.normalize_phone_il('0526380055'), '+972526380055',
  'bare local format is converted');

select is(sales_core.normalize_phone_il('972526380055'), '+972526380055',
  'country code without plus is converted');

select is(sales_core.normalize_phone_il('+972512668913'), '+972512668913',
  'an unusual but valid IL prefix is preserved');

select is(sales_core.normalize_phone_il('+13125550123'), '+13125550123',
  'a non-IL number is kept as-is');

select is(sales_core.normalize_phone_il(''), null,
  'empty string yields null, not a bogus number');

select is(sales_core.normalize_phone_il('not a phone'), null,
  'unparseable input yields null rather than garbage');

-- The trigger must apply the same rule on the way in.
insert into sales_core.org (id, display_name) values
  ('22222222-2222-2222-2222-222222222222','Trigger Test');
insert into sales_core.lead (org_id, source, external_id, contact_name, phone_raw)
values ('22222222-2222-2222-2222-222222222222','test','phone-1','H','+9720526380055');
select is(
  (select phone_e164 from sales_core.lead where source='test' and external_id='phone-1'),
  '+972526380055',
  'the insert trigger normalises phone_raw into phone_e164'
);

select * from finish();
rollback;
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pg_prove -d "$DATABASE_URL" db/tests/0319_sales_core_phone_normalisation.test.sql`
Expected: FAIL — `function sales_core.normalize_phone_il(text) does not exist`.

- [ ] **Step 3: Write the migration**

Create `db/migrations/0319_sales_core_phone_normalisation.sql`:

```sql
-- 0319_sales_core_phone_normalisation.sql
--
-- WHY
--
-- The 2026-08-10 Meta export carries the same phone in two shapes:
-- +972526380055 and +9720526380055 — an extra zero after the country code, in
-- roughly half the rows. Meta also prefixes lead phones with 'p:'. Left alone,
-- the same person arrives as two different people, duplicate detection silently
-- fails, and every tel: link in the portal dials a wrong number.
--
-- The rule lives in the database because four callers write phones — the
-- poller, the generic ingest route, the portal's manual form and the import
-- script. A normaliser in one of them is a normaliser the other three forget.

create or replace function sales_core.normalize_phone_il(raw text)
returns text
language plpgsql
immutable
as $$
declare
  s text;
  national text;
begin
  if raw is null then return null; end if;

  -- Strip Meta's p: prefix and every separator.
  s := regexp_replace(raw, '^p:', '');
  s := regexp_replace(s, '[^0-9+]', '', 'g');
  if s = '' then return null; end if;

  -- A non-Israeli international number passes through untouched.
  if s ~ '^\+' and s !~ '^\+972' then
    return case when s ~ '^\+[0-9]{8,15}$' then s else null end;
  end if;

  -- Reduce every Israeli shape to the national part.
  national := regexp_replace(s, '^\+?972', '');
  national := regexp_replace(national, '^0+', '');

  -- Israeli national numbers are 8 or 9 digits once the leading zero is gone.
  if national !~ '^[1-9][0-9]{7,8}$' then
    return null;
  end if;

  return '+972' || national;
end;
$$;

create or replace function sales_core.tg_normalize_phone()
returns trigger
language plpgsql
as $$
begin
  new.phone_e164 := sales_core.normalize_phone_il(new.phone_raw);
  return new;
end;
$$;

create trigger lead_normalize_phone
  before insert or update of phone_raw on sales_core.lead
  for each row execute function sales_core.tg_normalize_phone();

create trigger org_normalize_phone
  before insert or update of phone_raw on sales_core.org
  for each row execute function sales_core.tg_normalize_phone();
```

- [ ] **Step 4: Add the npm scripts**

```json
"db:apply:0319": "psql \"$DATABASE_URL\" -v ON_ERROR_STOP=1 -f db/migrations/0319_sales_core_phone_normalisation.sql",
"db:test:0319": "pg_prove -d \"$DATABASE_URL\" db/tests/0319_sales_core_phone_normalisation.test.sql",
```

- [ ] **Step 5: Apply and run the test to verify it passes**

Run: `npm run db:apply:0319 && npm run db:test:0319`
Expected: PASS, 12/12.

- [ ] **Step 6: Commit**

```bash
git add db/migrations/0319_sales_core_phone_normalisation.sql db/tests/0319_sales_core_phone_normalisation.test.sql package.json
git commit -m "feat(sales): normalise Israeli phones at the database boundary

Half the Meta export carries an extra zero after the country code, and Meta
prefixes lead phones with p:. Both shapes now collapse to E.164 on the way
in, so the same person cannot arrive as two people."
```

---

### Task 3: Append-only guard on `lead_event`

**Files:**
- Create: `db/migrations/0320_sales_core_lead_event_append_only.sql`
- Create: `db/tests/0320_sales_core_lead_event_append_only.test.sql`
- Modify: `package.json`

**Interfaces:**
- Consumes: Tasks 1–2.
- Produces: a trigger that raises on UPDATE or DELETE of `sales_core.lead_event`.

- [ ] **Step 1: Write the failing test**

Create `db/tests/0320_sales_core_lead_event_append_only.test.sql`:

```sql
begin;
create extension if not exists pgtap;
select plan(3);

insert into sales_core.org (id, display_name)
values ('33333333-3333-3333-3333-333333333333','Append Test');
insert into sales_core.lead (id, org_id, source, external_id, contact_name)
values ('44444444-4444-4444-4444-444444444444',
        '33333333-3333-3333-3333-333333333333','test','append-1','I');
insert into sales_core.lead_event (lead_id, event_type, payload)
values ('44444444-4444-4444-4444-444444444444','created','{}'::jsonb);

select throws_ok(
  $$update sales_core.lead_event set actor = 'tampered'
    where lead_id = '44444444-4444-4444-4444-444444444444'$$,
  'P0001',
  'sales_core.lead_event is append-only: UPDATE is not permitted',
  'UPDATE on lead_event is blocked'
);

select throws_ok(
  $$delete from sales_core.lead_event
    where lead_id = '44444444-4444-4444-4444-444444444444'$$,
  'P0001',
  'sales_core.lead_event is append-only: DELETE is not permitted',
  'DELETE on lead_event is blocked'
);

select lives_ok(
  $$insert into sales_core.lead_event (lead_id, event_type, payload)
    values ('44444444-4444-4444-4444-444444444444','note','{"text":"ok"}'::jsonb)$$,
  'INSERT on lead_event still works'
);

select * from finish();
rollback;
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pg_prove -d "$DATABASE_URL" db/tests/0320_sales_core_lead_event_append_only.test.sql`
Expected: FAIL — the UPDATE succeeds instead of raising.

- [ ] **Step 3: Write the migration**

Create `db/migrations/0320_sales_core_lead_event_append_only.sql`:

```sql
-- 0320_sales_core_lead_event_append_only.sql
--
-- WHY
--
-- Same doctrine as stock_ledger: history that can be edited is not history.
-- A lead's timeline is the evidence for every claim the sales system will make
-- — when it arrived, when it was first touched, why it was lost, what proved it
-- won. Corrections are new, opposite events.

create or replace function sales_core.tg_lead_event_append_only()
returns trigger
language plpgsql
as $$
begin
  raise exception 'sales_core.lead_event is append-only: % is not permitted', tg_op
    using errcode = 'P0001';
end;
$$;

create trigger lead_event_no_update
  before update on sales_core.lead_event
  for each row execute function sales_core.tg_lead_event_append_only();

create trigger lead_event_no_delete
  before delete on sales_core.lead_event
  for each row execute function sales_core.tg_lead_event_append_only();
```

- [ ] **Step 4: Add the npm scripts**

```json
"db:apply:0320": "psql \"$DATABASE_URL\" -v ON_ERROR_STOP=1 -f db/migrations/0320_sales_core_lead_event_append_only.sql",
"db:test:0320": "pg_prove -d \"$DATABASE_URL\" db/tests/0320_sales_core_lead_event_append_only.test.sql",
```

- [ ] **Step 5: Apply and run the test to verify it passes**

Run: `npm run db:apply:0320 && npm run db:test:0320`
Expected: PASS, 3/3.

- [ ] **Step 6: Commit**

```bash
git add db/migrations/0320_sales_core_lead_event_append_only.sql db/tests/0320_sales_core_lead_event_append_only.test.sql package.json
git commit -m "feat(sales): make lead_event append-only

History that can be edited is not history. Corrections are opposite events."
```

---

### Task 4: Org matching and the ingest function

**Files:**
- Create: `db/migrations/0321_sales_core_ingest.sql`
- Create: `db/tests/0321_sales_core_ingest.test.sql`
- Modify: `package.json`

**Interfaces:**
- Consumes: Tasks 1–3.
- Produces:
  - `sales_core.is_business_domain(email text) returns boolean`
  - `sales_core.match_org(p_phone text, p_email text, p_shopify_customer_id text) returns uuid`
  - `sales_core.ingest_lead(p_source text, p_external_id text, p_contact_name text, p_phone_raw text, p_email text, p_display_name text, p_created_at timestamptz, p_meta jsonb, p_shopify_customer_id text) returns table (lead_id uuid, org_id uuid, was_new boolean)`

`ingest_lead` is the single write path. The poller, the generic route and the import script all call it, so matching, deduplication and event writing happen in exactly one place.

The freemail exclusion matters more than it looks: most leads in the export use gmail.com. Matching on email domain without a blocklist would collapse every Gmail lead into one giant "org" — one bug that would quietly destroy the whole dataset.

- [ ] **Step 1: Write the failing test**

Create `db/tests/0321_sales_core_ingest.test.sql`:

```sql
begin;
create extension if not exists pgtap;
select plan(10);

select ok(not sales_core.is_business_domain('someone@gmail.com'),
  'gmail is not a business domain');
select ok(not sales_core.is_business_domain('someone@walla.com'),
  'walla is not a business domain');
select ok(sales_core.is_business_domain('kobi.a@cafecafe.co.il'),
  'a company domain is a business domain');

-- First ingest creates a new org.
select ok(
  (select was_new from sales_core.ingest_lead(
     'test','m-1','Kobi','+9720544787437','kobi.a@cafecafe.co.il',
     'Cafe Cafe', now(), '{}'::jsonb, null)),
  'first ingest reports a new lead'
);

-- Same phone in a different shape attaches to the same org.
select is(
  (select org_id from sales_core.ingest_lead(
     'test','m-2','Kobi again','054-478-7437','other@gmail.com',
     'Kobi again', now(), '{}'::jsonb, null)),
  (select org_id from sales_core.lead where source='test' and external_id='m-1'),
  'a repeat phone in another format attaches to the same org'
);

-- ...and the newer lead is flagged as a possible duplicate.
select isnt(
  (select possible_duplicate_of from sales_core.lead
    where source='test' and external_id='m-2'),
  null,
  'the repeat lead is flagged as a possible duplicate'
);

-- Two different people on gmail must NOT be merged.
select isnt(
  (select org_id from sales_core.ingest_lead(
     'test','m-3','Person A','+972500000001','a@gmail.com',
     'Person A', now(), '{}'::jsonb, null)),
  (select org_id from sales_core.ingest_lead(
     'test','m-4','Person B','+972500000002','b@gmail.com',
     'Person B', now(), '{}'::jsonb, null)),
  'two gmail leads with different phones stay separate orgs'
);

-- Re-ingesting the same external id is idempotent.
select ok(
  not (select was_new from sales_core.ingest_lead(
     'test','m-1','Kobi','+9720544787437','kobi.a@cafecafe.co.il',
     'Cafe Cafe', now(), '{}'::jsonb, null)),
  're-ingesting the same external_id reports was_new = false'
);
select is(
  (select count(*) from sales_core.lead where source='test' and external_id='m-1'),
  1::bigint,
  're-ingesting the same external_id creates no second row'
);

-- Every ingested lead gets a created event.
select is(
  (select count(*) from sales_core.lead_event e
     join sales_core.lead l on l.id = e.lead_id
    where l.source='test' and l.external_id='m-1' and e.event_type='created'),
  1::bigint,
  'ingest writes exactly one created event'
);

select * from finish();
rollback;
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pg_prove -d "$DATABASE_URL" db/tests/0321_sales_core_ingest.test.sql`
Expected: FAIL — `function sales_core.is_business_domain(text) does not exist`.

- [ ] **Step 3: Write the migration**

Create `db/migrations/0321_sales_core_ingest.sql`:

```sql
-- 0321_sales_core_ingest.sql
--
-- WHY
--
-- Four callers will write leads: the Meta poller, the generic ingest route, the
-- portal's manual form, and the historical import. Every one of them must
-- normalise the phone, find or create the business, flag duplicates and write
-- the created event. Four implementations of that is four chances to drift, and
-- the drift shows up months later as a customer nobody recognised.
--
-- So there is one write path: ingest_lead. Callers supply raw fields; the
-- database decides identity.
--
-- MATCH ORDER
--
--   1. shopify_customer_id — strongest, supplied by the caller after a Shopify
--      lookup.
--   2. phone_e164          — the only field the live two-question form reliably
--      collects.
--   3. exact email
--   4. business email domain
--
-- Step 4 carries the trap worth naming: most leads in the 2026-08-10 export use
-- gmail.com. Matching on domain without excluding free providers would fold
-- every unrelated Gmail lead into a single fictional business — a data
-- catastrophe that looks like a feature until someone reads it. Hence
-- is_business_domain.
--
-- Duplicates are flagged, never blocked: a real person filling the form twice
-- is a signal about interest, not an error to discard.

create or replace function sales_core.is_business_domain(email text)
returns boolean
language sql
immutable
as $$
  select case
    when email is null or position('@' in email) = 0 then false
    else lower(split_part(email, '@', 2)) not in (
      'gmail.com','googlemail.com','walla.com','walla.co.il','yahoo.com',
      'hotmail.com','outlook.com','live.com','windowslive.com','icloud.com',
      'me.com','aol.com','protonmail.com','proton.me','mail.ru','yandex.com',
      '013.net','012.net.il','bezeqint.net','nana10.co.il','zahav.net.il'
    )
  end;
$$;

create or replace function sales_core.match_org(
  p_phone text,
  p_email text,
  p_shopify_customer_id text
) returns uuid
language sql
stable
as $$
  select id from sales_core.org
   where p_shopify_customer_id is not null
     and shopify_customer_id = p_shopify_customer_id
   union all
  select id from sales_core.org
   where p_phone is not null and phone_e164 = p_phone
   union all
  select id from sales_core.org
   where p_email is not null and lower(email) = lower(p_email)
   union all
  select id from sales_core.org
   where p_email is not null
     and sales_core.is_business_domain(p_email)
     and email_domain = lower(split_part(p_email, '@', 2))
   limit 1;
$$;

create or replace function sales_core.ingest_lead(
  p_source text,
  p_external_id text,
  p_contact_name text,
  p_phone_raw text,
  p_email text,
  p_display_name text,
  p_created_at timestamptz,
  p_meta jsonb,
  p_shopify_customer_id text
) returns table (lead_id uuid, org_id uuid, was_new boolean)
language plpgsql
as $$
declare
  v_phone   text := sales_core.normalize_phone_il(p_phone_raw);
  v_org     uuid;
  v_lead    uuid;
  v_dup     uuid;
begin
  -- Idempotency first: an already-known lead returns unchanged.
  select l.id, l.org_id into v_lead, v_org
    from sales_core.lead l
   where l.source = p_source and l.external_id = p_external_id;
  if found then
    return query select v_lead, v_org, false;
    return;
  end if;

  v_org := sales_core.match_org(v_phone, p_email, p_shopify_customer_id);

  if v_org is null then
    insert into sales_core.org (display_name, phone_raw, email, email_domain,
                                shopify_customer_id)
    values (coalesce(nullif(p_display_name,''), nullif(p_contact_name,''), 'ללא שם'),
            p_phone_raw,
            p_email,
            case when sales_core.is_business_domain(p_email)
                 then lower(split_part(p_email,'@',2)) end,
            p_shopify_customer_id)
    returning id into v_org;
  else
    -- An existing business: an earlier lead from the same phone means this one
    -- is probably the same person asking again.
    select l.id into v_dup
      from sales_core.lead l
     where l.org_id = v_org
       and v_phone is not null
       and l.phone_e164 = v_phone
     order by l.created_at
     limit 1;

    -- Fill gaps we did not previously know, without overwriting what we have.
    update sales_core.org o
       set shopify_customer_id = coalesce(o.shopify_customer_id, p_shopify_customer_id),
           email               = coalesce(o.email, p_email),
           phone_raw           = coalesce(o.phone_raw, p_phone_raw),
           updated_at          = now()
     where o.id = v_org;
  end if;

  insert into sales_core.lead (
    org_id, source, external_id, contact_name, phone_raw, email,
    campaign_name, ad_name, form_id, form_name, platform, is_organic,
    possible_duplicate_of, created_at
  ) values (
    v_org, p_source, p_external_id, p_contact_name, p_phone_raw, p_email,
    p_meta->>'campaign_name', p_meta->>'ad_name', p_meta->>'form_id',
    p_meta->>'form_name', p_meta->>'platform',
    (p_meta->>'is_organic')::boolean,
    v_dup, coalesce(p_created_at, now())
  ) returning id into v_lead;

  insert into sales_core.lead_event (lead_id, event_type, payload, actor)
  values (v_lead, 'created',
          jsonb_build_object('source', p_source, 'meta', p_meta), 'system');

  if p_shopify_customer_id is not null then
    insert into sales_core.lead_event (lead_id, event_type, payload, actor)
    values (v_lead, 'matched_existing_customer',
            jsonb_build_object('shopify_customer_id', p_shopify_customer_id),
            'system');
  end if;

  return query select v_lead, v_org, true;
end;
$$;
```

- [ ] **Step 4: Add the npm scripts**

```json
"db:apply:0321": "psql \"$DATABASE_URL\" -v ON_ERROR_STOP=1 -f db/migrations/0321_sales_core_ingest.sql",
"db:test:0321": "pg_prove -d \"$DATABASE_URL\" db/tests/0321_sales_core_ingest.test.sql",
```

- [ ] **Step 5: Apply and run the test to verify it passes**

Run: `npm run db:apply:0321 && npm run db:test:0321`
Expected: PASS, 10/10.

- [ ] **Step 6: Commit**

```bash
git add db/migrations/0321_sales_core_ingest.sql db/tests/0321_sales_core_ingest.test.sql package.json
git commit -m "feat(sales): one ingest path with org matching

Domain matching excludes free providers. Without that, every gmail lead in
the export would have folded into a single fictional business."
```

---

### Task 5: Parse the Meta export

**Files:**
- Create: `scripts/import_meta_leads.ts`
- Create: `scripts/import_meta_leads.test.ts`
- Modify: `.gitignore` (add `/*.csv`)
- Modify: `package.json`

**Interfaces:**
- Consumes: nothing from earlier tasks (pure parsing).
- Produces: `export type MetaLeadRow = { createdAt: Date; contactName: string; email: string | null; phoneRaw: string | null; source: string; formName: string | null; channel: string | null; stage: string | null }` and `export function parseMetaExport(csv: string): { rows: MetaLeadRow[]; rejected: { line: number; reason: string }[] }` and `export function externalIdFor(row: MetaLeadRow): string`.

The export's header is Hebrew and column order is not guaranteed, so the parser maps by header name. Rows without both a phone and an email are kept — the 2023–2024 Instagram rows are real history — but they are marked uncontactable by carrying nulls.

- [ ] **Step 1: Write the failing test**

Create `scripts/import_meta_leads.test.ts`:

```ts
import { describe, it, expect } from 'vitest';
import { parseMetaExport, externalIdFor } from './import_meta_leads.js';

const HEADER =
  'נוצר,שם,דוא"ל,מקור,טופס,ערוץ,שלב,בעלים,תוויות,טלפון,מספר הטלפון המשני,מספר הטלפון ב-WhatsApp';

describe('parseMetaExport', () => {
  it('parses a paid lead row', () => {
    const csv = [
      HEADER,
      '08/09/2026 5:33am,רפאל שי דיין,uurrmm85@gmail.com,בתשלום,0205.2025-2question-new,דוא"ל,קליטה,Unassigned,,+972527332344,,',
    ].join('\n');

    const { rows, rejected } = parseMetaExport(csv);

    expect(rejected).toHaveLength(0);
    expect(rows).toHaveLength(1);
    expect(rows[0].contactName).toBe('רפאל שי דיין');
    expect(rows[0].email).toBe('uurrmm85@gmail.com');
    expect(rows[0].phoneRaw).toBe('+972527332344');
    // US month/day ordering: this is 9 August 2026, not 8 September.
    expect(rows[0].createdAt.toISOString().slice(0, 10)).toBe('2026-08-09');
  });

  it('keeps organic rows that have neither phone nor email', () => {
    const csv = [
      HEADER,
      '01/13/2024 3:05pm,שניאור בן ארוש,,אורגני,,אינסטגרם,קליטה,Unassigned,,,,',
    ].join('\n');

    const { rows } = parseMetaExport(csv);

    expect(rows).toHaveLength(1);
    expect(rows[0].phoneRaw).toBeNull();
    expect(rows[0].email).toBeNull();
    expect(rows[0].channel).toBe('אינסטגרם');
  });

  it('handles a quoted field containing a comma', () => {
    const csv = [
      HEADER,
      '09/12/2023 10:52am,"עבד אלראזק ח\'ליליה ,עו\'\'ד ונוטריון",,אורגני,,אינסטגרם,קליטה,Unassigned,,,,',
    ].join('\n');

    const { rows } = parseMetaExport(csv);

    expect(rows).toHaveLength(1);
    expect(rows[0].contactName).toContain('עבד אלראזק');
  });

  it('rejects a row with an unparseable date, with its line number', () => {
    const csv = [HEADER, 'not-a-date,Someone,,אורגני,,,,,,,,'].join('\n');

    const { rows, rejected } = parseMetaExport(csv);

    expect(rows).toHaveLength(0);
    expect(rejected[0].line).toBe(2);
    expect(rejected[0].reason).toMatch(/date/i);
  });
});

describe('externalIdFor', () => {
  it('is stable for the same phone and day', () => {
    const a = externalIdFor({
      createdAt: new Date('2026-08-09T05:33:00Z'), contactName: 'A',
      email: null, phoneRaw: '+972527332344', source: 'בתשלום',
      formName: null, channel: null, stage: null,
    });
    const b = externalIdFor({
      createdAt: new Date('2026-08-09T21:00:00Z'), contactName: 'A copy',
      email: null, phoneRaw: '+972527332344', source: 'בתשלום',
      formName: null, channel: null, stage: null,
    });
    expect(a).toBe(b);
  });

  it('differs for the same phone on a different day', () => {
    const a = externalIdFor({
      createdAt: new Date('2026-06-06T05:33:00Z'), contactName: 'אילן מימון',
      email: null, phoneRaw: '+972502177217', source: 'בתשלום',
      formName: null, channel: null, stage: null,
    });
    const b = externalIdFor({
      createdAt: new Date('2026-06-09T05:33:00Z'), contactName: 'דולצ\'ה פרו מימון',
      email: null, phoneRaw: '+972502177217', source: 'בתשלום',
      formName: null, channel: null, stage: null,
    });
    expect(a).not.toBe(b);
  });
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `npx vitest run scripts/import_meta_leads.test.ts`
Expected: FAIL — cannot resolve `./import_meta_leads.js`.

- [ ] **Step 3: Write the parser**

Create `scripts/import_meta_leads.ts` (parsing half only; the database half arrives in Task 6):

```ts
// Imports the Meta Leads Center export into sales_core.
//
// The export is the recovery path for every lead that arrived after the old
// pipeline died on 2026-06-07 — about sixty of them — plus organic history back
// to 2023. Meta deletes leads after ninety days, so this file is a rescue, not
// a convenience.
//
// Usage:
//   npx tsx scripts/import_meta_leads.ts --file /path/to/leads.csv --dry-run
//   npx tsx scripts/import_meta_leads.ts --file /path/to/leads.csv
//
// The CSV holds personal data of people who are not customers. Keep it outside
// the repository; never commit it.
import { createHash } from 'node:crypto';

export type MetaLeadRow = {
  createdAt: Date;
  contactName: string;
  email: string | null;
  phoneRaw: string | null;
  source: string;
  formName: string | null;
  channel: string | null;
  stage: string | null;
};

const COL = {
  created: 'נוצר',
  name: 'שם',
  email: 'דוא"ל',
  source: 'מקור',
  form: 'טופס',
  channel: 'ערוץ',
  stage: 'שלב',
  phone: 'טלפון',
} as const;

// Minimal RFC-4180 splitter: quoted fields may contain commas; "" is a literal quote.
function splitCsvLine(line: string): string[] {
  const out: string[] = [];
  let field = '';
  let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    const c = line[i];
    if (inQuotes) {
      if (c === '"' && line[i + 1] === '"') { field += '"'; i++; }
      else if (c === '"') inQuotes = false;
      else field += c;
    } else if (c === '"') inQuotes = true;
    else if (c === ',') { out.push(field); field = ''; }
    else field += c;
  }
  out.push(field);
  return out;
}

// Meta exports US ordering: MM/DD/YYYY h:mma.
function parseMetaDate(raw: string): Date | null {
  const m = raw.trim().match(/^(\d{2})\/(\d{2})\/(\d{4})\s+(\d{1,2}):(\d{2})(am|pm)$/i);
  if (!m) return null;
  const [, mm, dd, yyyy, hh, min, ampm] = m;
  let hour = Number(hh) % 12;
  if (ampm.toLowerCase() === 'pm') hour += 12;
  const d = new Date(Date.UTC(Number(yyyy), Number(mm) - 1, Number(dd), hour, Number(min)));
  return Number.isNaN(d.getTime()) ? null : d;
}

const clean = (v: string | undefined): string | null => {
  const t = (v ?? '').trim();
  return t === '' ? null : t;
};

export function parseMetaExport(csv: string): {
  rows: MetaLeadRow[];
  rejected: { line: number; reason: string }[];
} {
  const lines = csv.split(/\r?\n/).filter((l) => l.trim() !== '');
  const header = splitCsvLine(lines[0]).map((h) => h.trim());
  const idx = (name: string) => header.indexOf(name);

  const rows: MetaLeadRow[] = [];
  const rejected: { line: number; reason: string }[] = [];

  for (let i = 1; i < lines.length; i++) {
    const f = splitCsvLine(lines[i]);
    const createdAt = parseMetaDate(f[idx(COL.created)] ?? '');
    if (!createdAt) {
      rejected.push({ line: i + 1, reason: `unparseable date: ${f[idx(COL.created)] ?? ''}` });
      continue;
    }
    rows.push({
      createdAt,
      contactName: (f[idx(COL.name)] ?? '').trim(),
      email: clean(f[idx(COL.email)]),
      phoneRaw: clean(f[idx(COL.phone)]),
      source: (f[idx(COL.source)] ?? '').trim(),
      formName: clean(f[idx(COL.form)]),
      channel: clean(f[idx(COL.channel)]),
      stage: clean(f[idx(COL.stage)]),
    });
  }

  return { rows, rejected };
}

// Meta's export carries no leadgen_id, so identity is (contact point + day).
// Same person, same day = same lead. Same person three days later = a second
// lead, which is exactly what happened with +972502177217 in June.
export function externalIdFor(row: MetaLeadRow): string {
  const contact = row.phoneRaw ?? row.email ?? row.contactName;
  const day = row.createdAt.toISOString().slice(0, 10);
  return createHash('sha256').update(`${contact}|${day}`).digest('hex').slice(0, 32);
}
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `npx vitest run scripts/import_meta_leads.test.ts`
Expected: PASS, 6 tests.

- [ ] **Step 5: Keep the data out of git**

Append to `.gitignore`:

```
# Lead exports carry personal data of non-customers. Never commit them.
/*.csv
```

- [ ] **Step 6: Commit**

```bash
git add scripts/import_meta_leads.ts scripts/import_meta_leads.test.ts .gitignore
git commit -m "feat(sales): parse the Meta Leads Center export

Header-name mapping rather than column order, US date ordering, and a stable
(contact point + day) identity so a genuine second enquiry stays a second
lead instead of collapsing into the first."
```

---

### Task 6: Match against Shopify and write the leads

**Files:**
- Modify: `scripts/import_meta_leads.ts`
- Modify: `scripts/import_meta_leads.test.ts`
- Modify: `package.json`

**Interfaces:**
- Consumes: `parseMetaExport`, `externalIdFor` (Task 5); `sales_core.ingest_lead` (Task 4).
- Produces: `export function buildCustomerIndex(customers: ShopifyCustomer[]): CustomerIndex` and `export function findCustomer(index: CustomerIndex, phoneE164: string | null, email: string | null): ShopifyCustomer | null`, plus a `main()` that runs the import and prints a report.

Shopify customers are fetched once into memory rather than queried per lead: a few hundred B2B customers against 188 leads makes one paged read obviously cheaper than 188 round trips, and it keeps the script re-runnable offline in dry-run mode.

- [ ] **Step 1: Write the failing test**

Append to `scripts/import_meta_leads.test.ts`:

```ts
import { buildCustomerIndex, findCustomer } from './import_meta_leads.js';

describe('shopify matching', () => {
  const customers = [
    { id: 'gid://shopify/Customer/1', displayName: 'קפה קפה',
      email: 'kobi.a@cafecafe.co.il', phone: '+972544787437',
      amountSpent: '46108.00', lastOrderAt: '2025-12-01T00:00:00Z' },
    { id: 'gid://shopify/Customer/2', displayName: 'פרוסות',
      email: 'ori@prusot.com', phone: null,
      amountSpent: '161689.00', lastOrderAt: '2023-10-01T00:00:00Z' },
  ];

  it('matches on normalised phone', () => {
    const index = buildCustomerIndex(customers);
    expect(findCustomer(index, '+972544787437', null)?.id)
      .toBe('gid://shopify/Customer/1');
  });

  it('matches on email when the phone is absent', () => {
    const index = buildCustomerIndex(customers);
    expect(findCustomer(index, null, 'ORI@prusot.com')?.id)
      .toBe('gid://shopify/Customer/2');
  });

  it('returns null when nothing matches', () => {
    const index = buildCustomerIndex(customers);
    expect(findCustomer(index, '+972500000000', 'nobody@gmail.com')).toBeNull();
  });
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `npx vitest run scripts/import_meta_leads.test.ts`
Expected: FAIL — `buildCustomerIndex` is not exported.

- [ ] **Step 3: Implement matching and the import run**

Append to `scripts/import_meta_leads.ts`:

```ts
import { readFileSync } from 'node:fs';
import pg from 'pg';

export type ShopifyCustomer = {
  id: string;
  displayName: string;
  email: string | null;
  phone: string | null;
  amountSpent: string | null;
  lastOrderAt: string | null;
};

export type CustomerIndex = {
  byPhone: Map<string, ShopifyCustomer>;
  byEmail: Map<string, ShopifyCustomer>;
};

// Mirrors sales_core.normalize_phone_il for the in-memory index. The database
// stays the authority; this only has to agree with it well enough to match.
function normalizePhoneIl(raw: string | null): string | null {
  if (!raw) return null;
  const s = raw.replace(/^p:/, '').replace(/[^0-9+]/g, '');
  if (s === '') return null;
  if (s.startsWith('+') && !s.startsWith('+972')) {
    return /^\+[0-9]{8,15}$/.test(s) ? s : null;
  }
  const national = s.replace(/^\+?972/, '').replace(/^0+/, '');
  return /^[1-9][0-9]{7,8}$/.test(national) ? `+972${national}` : null;
}

export function buildCustomerIndex(customers: ShopifyCustomer[]): CustomerIndex {
  const byPhone = new Map<string, ShopifyCustomer>();
  const byEmail = new Map<string, ShopifyCustomer>();
  for (const c of customers) {
    const p = normalizePhoneIl(c.phone);
    if (p && !byPhone.has(p)) byPhone.set(p, c);
    if (c.email && !byEmail.has(c.email.toLowerCase())) {
      byEmail.set(c.email.toLowerCase(), c);
    }
  }
  return { byPhone, byEmail };
}

export function findCustomer(
  index: CustomerIndex,
  phoneE164: string | null,
  email: string | null,
): ShopifyCustomer | null {
  if (phoneE164 && index.byPhone.has(phoneE164)) return index.byPhone.get(phoneE164)!;
  if (email && index.byEmail.has(email.toLowerCase())) return index.byEmail.get(email.toLowerCase())!;
  return null;
}

const CUSTOMERS_QUERY = `query($cursor:String){
  customers(first:250, after:$cursor){
    edges{ node{ id displayName email phone amountSpent{ amount }
                 lastOrder{ createdAt } } }
    pageInfo{ hasNextPage endCursor }
  }
}`;

async function fetchAllCustomers(domain: string, token: string): Promise<ShopifyCustomer[]> {
  const out: ShopifyCustomer[] = [];
  let cursor: string | null = null;
  for (;;) {
    const r = await fetch(`https://${domain}/admin/api/2025-07/graphql.json`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Shopify-Access-Token': token },
      body: JSON.stringify({ query: CUSTOMERS_QUERY, variables: { cursor } }),
      signal: AbortSignal.timeout(25000),
    });
    if (!r.ok) throw new Error(`Shopify customers query failed: HTTP ${r.status}`);
    const body: any = await r.json();
    if (body.errors) throw new Error(`Shopify GraphQL errors: ${JSON.stringify(body.errors)}`);
    for (const e of body.data.customers.edges) {
      out.push({
        id: e.node.id,
        displayName: e.node.displayName,
        email: e.node.email,
        phone: e.node.phone,
        amountSpent: e.node.amountSpent?.amount ?? null,
        lastOrderAt: e.node.lastOrder?.createdAt ?? null,
      });
    }
    if (!body.data.customers.pageInfo.hasNextPage) return out;
    cursor = body.data.customers.pageInfo.endCursor;
  }
}

async function main() {
  const args = process.argv.slice(2);
  const fileArg = args.indexOf('--file');
  if (fileArg === -1 || !args[fileArg + 1]) {
    throw new Error('usage: tsx scripts/import_meta_leads.ts --file <path.csv> [--dry-run]');
  }
  const dryRun = args.includes('--dry-run');

  const { rows, rejected } = parseMetaExport(readFileSync(args[fileArg + 1], 'utf8'));

  const domain = process.env.SHOPIFY_STORE_DOMAIN;
  const token = process.env.SHOPIFY_ADMIN_TOKEN;
  let index: CustomerIndex = { byPhone: new Map(), byEmail: new Map() };
  if (domain && token) {
    index = buildCustomerIndex(await fetchAllCustomers(domain, token));
    console.log(`Shopify customers indexed: ${index.byPhone.size} by phone, ${index.byEmail.size} by email`);
  } else {
    console.log('SHOPIFY_STORE_DOMAIN / SHOPIFY_ADMIN_TOKEN unset — importing without customer matching');
  }

  const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL });
  let accepted = 0, merged = 0, matchedCustomers = 0;

  try {
    for (const row of rows) {
      const phone = normalizePhoneIl(row.phoneRaw);
      const customer = findCustomer(index, phone, row.email);
      if (customer) matchedCustomers++;

      if (dryRun) { accepted++; continue; }

      const res = await pool.query(
        `select * from sales_core.ingest_lead($1,$2,$3,$4,$5,$6,$7,$8,$9)`,
        [
          'import_meta_export',
          externalIdFor(row),
          row.contactName,
          row.phoneRaw,
          row.email,
          customer?.displayName ?? row.contactName,
          row.createdAt.toISOString(),
          JSON.stringify({
            form_name: row.formName,
            platform: row.channel,
            is_organic: row.source === 'אורגני',
            meta_stage: row.stage,
          }),
          customer?.id ?? null,
        ],
      );
      if (res.rows[0].was_new) accepted++; else merged++;
    }
  } finally {
    await pool.end();
  }

  console.log(`\n${dryRun ? 'DRY RUN' : 'IMPORT'} complete`);
  console.log(`  parsed:            ${rows.length}`);
  console.log(`  accepted:          ${accepted}`);
  console.log(`  already present:   ${merged}`);
  console.log(`  matched a Shopify customer: ${matchedCustomers}`);
  console.log(`  rejected:          ${rejected.length}`);
  for (const r of rejected) console.log(`    line ${r.line}: ${r.reason}`);
}

// Only run main() when executed directly, so the test file can import safely.
if (process.argv[1]?.endsWith('import_meta_leads.ts')) {
  main().catch((e) => { console.error(e); process.exit(1); });
}
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `npx vitest run scripts/import_meta_leads.test.ts`
Expected: PASS, 9 tests.

- [ ] **Step 5: Add the npm scripts**

```json
"import:meta-leads": "tsx scripts/import_meta_leads.ts",
"import:meta-leads:dry-run": "tsx scripts/import_meta_leads.ts --dry-run",
```

- [ ] **Step 6: Commit**

```bash
git add scripts/import_meta_leads.ts scripts/import_meta_leads.test.ts package.json
git commit -m "feat(sales): match imported leads against Shopify customers

Customers are paged once into memory rather than queried per lead. The point
of the match is the moment it pays off: a lead who is already a sleeping
customer is a rescue call, not a cold call."
```

---

### Task 7: Run the import and record the evidence

**Files:**
- Create: `docs/integrations/sales-leads-import-2026-08-10.md` (in `gt-factory-os`)

**Interfaces:**
- Consumes: everything above.
- Produces: the evidence record for Phase 2's exit gate.

- [ ] **Step 1: Dry run**

Run: `npx tsx scripts/import_meta_leads.ts --file /path/to/leads.csv --dry-run`
Expected: `parsed: 188`, rejected 0 or a short list with line numbers and reasons. Investigate any rejection before continuing — a rejected row is a lead nobody will ever see again.

- [ ] **Step 2: Real run**

Run: `npx tsx scripts/import_meta_leads.ts --file /path/to/leads.csv`
Expected: accepted + already-present = parsed.

- [ ] **Step 3: Verify against the database**

```sql
-- Totals by source and status.
select source, status, count(*) from sales_core.lead group by 1,2 order by 1,2;

-- Leads that arrived after the pipeline died — the ones nobody saw.
select count(*) from sales_core.lead where created_at > '2026-06-07';

-- Businesses that turned out to be existing customers.
select count(*) from sales_core.org where shopify_customer_id is not null;

-- Duplicate flags, including the known +972502177217 case.
select l.contact_name, l.phone_e164, l.created_at
  from sales_core.lead l
 where l.possible_duplicate_of is not null
 order by l.created_at;

-- Every lead has exactly one created event.
select count(*) from sales_core.lead l
 where (select count(*) from sales_core.lead_event e
         where e.lead_id = l.id and e.event_type = 'created') <> 1;
```

Expected: the count after 2026-06-07 is roughly 60; the last query returns 0.

- [ ] **Step 4: Write the evidence record**

Create `docs/integrations/sales-leads-import-2026-08-10.md` with: the counts from Step 3, the rejected rows and why, how many leads matched an existing Shopify customer, and the named duplicate case. No lead names, phones or emails — counts and the two already-public business examples only.

- [ ] **Step 5: Commit and open the pull request**

```bash
git add docs/integrations/sales-leads-import-2026-08-10.md
git commit -m "docs(sales): evidence for the historical lead import

Every lead GT has received is now in one place, including the ones that
arrived after the pipeline died and were never seen."
git push -u origin claude/sales-system-planning-th2gna
```

Open a draft PR summarising phases 1–2 and linking the spec.

---

## Self-review

**Spec coverage.** §5.1 `org` → Task 1. §5.2 `lead` with the D12 constraint → Task 1. §5.3 `lead_event` append-only → Tasks 1 and 3. §5.4 normalisation and match order → Tasks 2 and 4. §8 import, single source, no email → Tasks 5–7. §11 pgTAP on the five rules that can break → Tasks 1–4 (dedupe S3a, phone normalisation 0319, append-only 0320, match order 0321, one-alert-per-lead deferred to Phase 3 where alerting exists). §12 phases 1–2 exit evidence → Task 7.

**Not covered here, by design:** the poller, the Resend alert, the close-the-loop job and the portal are Phases 3–5 and need Tom's two credentials first.

**Type consistency.** `ingest_lead` is called with nine positional arguments in Task 6 in the same order it is declared in Task 4. `MetaLeadRow` is produced in Task 5 and consumed unchanged in Task 6. `normalizePhoneIl` in TypeScript deliberately mirrors `sales_core.normalize_phone_il`; the database remains the authority, and Task 6's copy exists only to build the in-memory index.

**One deliberate simplification.** `ponytail:` the TypeScript phone normaliser duplicates the SQL one. Two implementations of one rule is a drift risk; it is accepted here because the alternative — a database round trip per row to normalise before matching — buys nothing at 188 rows. If a third caller ever needs it, expose the SQL function over the API instead of copying it again.
