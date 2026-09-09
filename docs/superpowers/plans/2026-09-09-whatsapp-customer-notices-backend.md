# WhatsApp Customer Notices — Backend Implementation Plan (Plan 1 of 3)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the backend of the customer-notices system in `gt-factory-os` so that, in shadow mode, every picked order produces a `confirmed_*` notice row, every delivery a `delivered` row, and every credit a `credit_issued` row, with the send path, approval API, reminder email and staff alerts working end to end behind flags that default to "send nothing".

**Architecture:** A 15-minute tick (Fastify internal job route, pg_cron caller) observes open LionWheel tasks via `/tasks/show`, records each observation, and turns `pick_status` into notice rows in `order_intake.customer_notices`; a second pass sends `approved` rows as Meta template messages when flags allow, else marks them `shadow`. Approval of partial picks is an authenticated API the portal tab (Plan 2) will call. Reminder emails run in the existing `factory_os_jobs` Edge Function next to `missing_picks_daily_email`. Everything is a read over `orders_mirror` / `credit_tasks`; no ledger or projection write.

**Tech Stack:** Node 20 + TypeScript + Fastify (existing `api/`), `pg` Pool (order-intake convention, not Kysely), Zod, vitest (`npx vitest run api/src/order-intake`), Postgres 17 + pgTAP (`pg_prove`), Deno Edge Function (`supabase/functions/factory_os_jobs`), WhatsApp Cloud API templates, LionWheel REST (`/api/v1/tasks/show/<id>.json?key=`), Shopify Admin GraphQL (`orders` query).

**Spec:** `gt-factory-os-production-brain/docs/superpowers/specs/2026-09-09-whatsapp-customer-notices-design.md` (Tom-approved 2026-09-09). This plan implements §3 stations 1, 2א, 2ב, 3, 3ב (backend side), §4, §5, §6, §8 (alerts + reminder), §9 (stats view), and the P1 shadow rollout. **Plan 2** (portal tab on `/credit-tracking`, portal repo, own tranche) and **Plan 3** (opt-out handling, second-cart-as-update, "usual order" reply, stations 8/9) follow separately.

## Global Constraints

- Repo: `gt-factory-os`, branch `claude/father-order-entry-permissions-i8q3ud`. Never `git add -A` / `git add .`; add files by name. No `.env*`, no secrets in code, tests or docs.
- Migration slot: **list `db/migrations/` immediately before writing the numbered file and again after** (FR1/FR2). At plan time the highest is `0349_suppress_test_lead_fixtures.sql`, so the file is `db/migrations/0350_customer_notices.sql` + `db/tests/0350_customer_notices.test.sql`. If a `0350_*` appears in between → HALT, `contract_failure`, do not renumber silently.
- Stock truth untouched: no write to `stock_ledger`, `balance_anchors`, `current_balances`, `credit_tasks`, `orders_mirror*`. The locked LionWheel chain modules (`api/src/integrations/lionwheel/poller.ts`, `reconciliation.ts`, `schemas.ts`) are **not modified**; the new `/tasks/show` reader is a separate file.
- Frozen flags untouched. New flags default OFF: env `WHATSAPP_NOTICES_ENABLED` (default `false`), `private_core.feature_flags` rows `customer_notices_live` (`enabled=false`, `{"allowlist":[]}`) and `customer_notices_kinds` (`{"kinds":["confirmed_full","confirmed_partial","delivered"]}`).
- Template names (exact): `gt_order_confirmed_full_v1`, `gt_order_confirmed_partial_v1`, `gt_order_delivered_v1`, `gt_order_delivered_nophoto_v1`, `gt_credit_issued_v1`; language code `he`. Template variables must not contain `\n`, `\t`, or 4+ consecutive spaces; ≤1000 chars.
- Quiet hours: proactive sends 07:00–21:00 Asia/Jerusalem. Never a price in stations 1–3ב. Hebrew only.
- Live LionWheel status spelling is `CANCELED`; the code enum says `CANCELLED`. Terminal-success set = `COMPLETED`, `ROUNDTRIP_DELIVERED`, `DELIVERED`; terminal-fail set = `CANCELED`, `CANCELLED`, `FAILED`.
- Reminder / alert recipients default to `tom@gteveryday.com` only (Tom 2026-09-09).
- Tests report N/N. Run `npx vitest run api/src/order-intake` after every task; root `npm run typecheck` before every commit. pgTAP: `pg_prove -d "$DATABASE_URL" db/tests/0350_customer_notices.test.sql` (needs a DB with 0001…0349 applied; if `DATABASE_URL` is not set in the container, say so in the commit message and run it before deploy).
- Commit after every task with the attribution footer from the session (Co-Authored-By + Claude-Session lines). No model identifiers in code, comments, commits or PR text.

---

## File structure

**Create (all under `api/src/order-intake/notices/`)** — the notices module lives inside the order-intake module because it shares the WhatsApp port, config, pool and Shopify client:

| File | Responsibility |
|---|---|
| `types.ts` | notice kinds/states, row shapes, `TaskShow`, `OpenTask`, `NoticeFlags` |
| `time.ts` | Asia/Jerusalem helpers: parts, offset, `sendNotBefore`, weekday names |
| `render.ts` | pure template-parameter builders (Hebrew copy lives here) |
| `decide.ts` | pure decisions: observation → notice, `canSend`, terminal sets, permanent error codes |
| `lionwheel_show.ts` | `/tasks/show/<id>.json` reader → `TaskShow` |
| `shopify_order.ts` | Shopify order name → numeric customer id |
| `store.ts` | `NoticeStore` interface + `createPgNoticeStore(pool)` (all SQL) |
| `pool.ts` | one cached `pg.Pool` for the notices routes |
| `tick.ts` | `runNoticesTick(deps)` orchestrator |
| `approve.ts` | approval/suppress handlers (validation + template rendering) |
| `routes.ts` | Fastify: tick job route, health, list/approve/suppress |
| `__tests__/fake_store.ts` | in-memory `NoticeStore` for tests |
| `__tests__/*.test.ts` | one test file per module |

**Modify:** `whatsapp/send.ts` (template send + typed error), `webhook.ts` (status error codes), `types.ts` (status `error_code`), `worker.ts` (status → notice, button taps, reply-after-notice), `alert.ts` (email transport + kinds), `config.ts` (notices + alerts config), `route.ts` (health), `whatsapp/messages.ts` (receipt wording), `api/src/server.ts` (register routes), `supabase/functions/factory_os_jobs/index.ts` (reminder job), `db/migrations/0350_customer_notices.sql`, `db/tests/0350_customer_notices.test.sql`, `.env.example`, `api/src/order-intake/README.md`.

---

### Task 1: Migration 0350 — tables, consent columns, change_log actions, flags, cron

**Files:**
- Create: `db/migrations/0350_customer_notices.sql`
- Create: `db/tests/0350_customer_notices.test.sql`

**Interfaces:**
- Produces: tables `order_intake.customer_notices`, `order_intake.customer_notice_lines`, `order_intake.customer_notice_events`, `order_intake.lw_pick_observations`; columns `wa_customer_map.notices_enabled/notices_opt_in_at/marketing_opt_out_at`; view `order_intake.v_customer_notice_stats`; feature-flag rows; pg_cron jobs `customer_notices_tick` (calls the route from Task 11) and `customer_notice_reminder` (calls the Edge job from Task 13); change_log actions `CUSTOMER_NOTICE_APPROVED`, `CUSTOMER_NOTICE_SUPPRESSED`.

- [ ] **Step 1: Bracket the slot (FR1)**

Run: `ls db/migrations | tail -3`
Expected: last line `0349_suppress_test_lead_fixtures.sql`. Anything `0350_*` present → HALT.

- [ ] **Step 2: Write the pgTAP test first**

`db/tests/0350_customer_notices.test.sql`:

```sql
-- 0350_customer_notices.test.sql — pgTAP for the WhatsApp customer-notices schema.
-- Assumes 0001..0350 applied to $DATABASE_URL. Behavioral checks run inside a
-- transaction that is rolled back.
begin;
create extension if not exists pgtap;
select plan(16);
set search_path to order_intake, public;

-- structural
select has_table('order_intake', 'customer_notices', 'customer_notices exists');
select has_table('order_intake', 'customer_notice_lines', 'customer_notice_lines exists');
select has_table('order_intake', 'customer_notice_events', 'customer_notice_events exists');
select has_table('order_intake', 'lw_pick_observations', 'lw_pick_observations exists');
select col_is_unique('order_intake', 'customer_notices', 'dedupe_key', 'dedupe_key is UNIQUE');
select has_column('order_intake', 'wa_customer_map', 'notices_enabled', 'wa_customer_map.notices_enabled exists');
select has_column('order_intake', 'wa_customer_map', 'marketing_opt_out_at', 'wa_customer_map.marketing_opt_out_at exists');
select has_view('order_intake', 'v_customer_notice_stats', 'stats view exists');

-- flags seeded OFF
select is((select enabled from private_core.feature_flags where flag_key = 'customer_notices_live'), false,
  'customer_notices_live seeded disabled');
select is((select value->'kinds' ? 'confirmed_full' from private_core.feature_flags where flag_key = 'customer_notices_kinds'), true,
  'customer_notices_kinds lists confirmed_full');

-- change_log CHECK accepts the two new actions
select ok((select pg_get_constraintdef(oid) like '%CUSTOMER_NOTICE_APPROVED%'
             from pg_constraint where conrelid = 'private_core.change_log'::regclass and conname = 'change_log_action_check'),
  'change_log_action_check includes CUSTOMER_NOTICE_APPROVED');

-- behavioral
insert into order_intake.customer_notices (kind, state, wa_phone, dedupe_key)
values ('confirmed_full', 'approved', '972500000001', 'confirmed:test-1');
select throws_ok(
  $$insert into order_intake.customer_notices (kind, state, wa_phone, dedupe_key)
    values ('confirmed_full', 'approved', '972500000001', 'confirmed:test-1')$$,
  '23505', null, 'duplicate dedupe_key is rejected');
select throws_ok(
  $$insert into order_intake.customer_notices (kind, state, wa_phone, dedupe_key)
    values ('confirmed_full', 'bogus', '972500000001', 'confirmed:test-2')$$,
  '23514', null, 'unknown state is rejected');
select lives_ok(
  $$insert into order_intake.customer_notice_lines (notice_id, item_label, qty_ordered, qty_delivering)
    select notice_id, 'DETOX 1000ml', 12, 12 from order_intake.customer_notices where dedupe_key = 'confirmed:test-1'$$,
  'a full line needs no resolution');
select throws_ok(
  $$insert into order_intake.customer_notice_lines (notice_id, item_label, qty_ordered, qty_delivering)
    select notice_id, 'FRESH 1000ml', 6, 4 from order_intake.customer_notices where dedupe_key = 'confirmed:test-1'$$,
  '23514', null, 'a short line without a resolution is rejected');
select lives_ok(
  $$insert into order_intake.customer_notice_lines (notice_id, item_label, qty_ordered, qty_delivering, resolution)
    select notice_id, 'FRESH 1000ml', 6, 4, 'credit' from order_intake.customer_notices where dedupe_key = 'confirmed:test-1'$$,
  'a short line with a resolution is accepted');

select * from finish();
rollback;
```

- [ ] **Step 3: Run the test to verify it fails**

Run: `pg_prove -d "$DATABASE_URL" db/tests/0350_customer_notices.test.sql`
Expected: FAIL on `has_table` (tables do not exist). If `DATABASE_URL` is unset, note "pgTAP deferred to pre-deploy" and continue.

- [ ] **Step 4: Write the migration**

`db/migrations/0350_customer_notices.sql`:

```sql
-- 0350_customer_notices.sql
--
-- WhatsApp customer notices — schema, consent, audit actions, flags, cron.
-- Spec (Tom-approved 2026-09-09):
--   gt-factory-os-production-brain/docs/superpowers/specs/2026-09-09-whatsapp-customer-notices-design.md
--
-- What this adds
--   order_intake.lw_pick_observations  append-only /tasks/show observations (evidence for A1)
--   order_intake.customer_notices      one row per intended outbound message
--   order_intake.customer_notice_lines what ships per line (human-entered on a short pick)
--   order_intake.customer_notice_events append-only state transitions + staff-alert markers
--   wa_customer_map.notices_enabled / notices_opt_in_at / marketing_opt_out_at
--   change_log actions CUSTOMER_NOTICE_APPROVED / CUSTOMER_NOTICE_SUPPRESSED
--   feature_flags customer_notices_live (OFF) + customer_notices_kinds
--   pg_cron customer_notices_tick (Railway route, every 15 min) +
--           customer_notice_reminder (Edge job, 16:30 + 07:30 Israel; the job gates on local hour)
--
-- Stock truth: untouched. No ledger, projection, movement_type or credit_tasks write.
-- Rollback: cron.unschedule('customer_notices_tick'); cron.unschedule('customer_notice_reminder');
--   flags stay OFF so the tables have no writer.

begin;

-- ---------------------------------------------------------------------------
-- 1. Observations (append-only)
-- ---------------------------------------------------------------------------
create table if not exists order_intake.lw_pick_observations (
  observation_id bigserial primary key,
  mirror_id      uuid not null references private_core.orders_mirror(mirror_id),
  lw_task_id     text not null,
  lw_status      text,
  pick_status    text,
  pickup_at      timestamptz,
  photo_url      text,
  observed_at    timestamptz not null default now()
);
create index if not exists idx_lw_pick_obs_task
  on order_intake.lw_pick_observations (lw_task_id, observed_at desc);
comment on table order_intake.lw_pick_observations is
  'Append-only. One row per /tasks/show observation made by the customer-notices tick. Never updated or deleted; the shadow-week evidence for spec assumption A1.';

-- ---------------------------------------------------------------------------
-- 2. Notices
-- ---------------------------------------------------------------------------
create table if not exists order_intake.customer_notices (
  notice_id           uuid primary key default gen_random_uuid(),
  kind                text not null check (kind in (
                        'confirmed_full','confirmed_partial','delivered','credit_issued',
                        'payment_due_soon','payment_overdue','reorder_nudge')),
  state               text not null default 'draft' check (state in (
                        'draft','pending_approval','approved','sent','delivered','read',
                        'failed','suppressed','expired','shadow')),
  wa_phone            text not null,
  shopify_customer_id text,
  shopify_order_name  text,
  mirror_id           uuid references private_core.orders_mirror(mirror_id),
  lw_task_id          text,
  credit_task_id      uuid references private_core.credit_tasks(credit_task_id),
  dedupe_key          text not null unique,
  template_name       text,
  template_params     jsonb not null default '[]'::jsonb,
  header_image_url    text,
  delivery_date       date,
  send_not_before     timestamptz,
  approved_by         uuid references private_core.app_users(user_id),
  approved_at         timestamptz,
  suppress_reason     text,
  wa_message_id       text,
  sent_at             timestamptz,
  delivered_at        timestamptz,
  read_at             timestamptz,
  fail_code           text,
  fail_detail         text,
  attempts            int not null default 0,
  created_at          timestamptz not null default now(),
  updated_at          timestamptz not null default now()
);
create index if not exists idx_customer_notices_state
  on order_intake.customer_notices (state, send_not_before);
create index if not exists idx_customer_notices_mirror
  on order_intake.customer_notices (mirror_id);
create unique index if not exists idx_customer_notices_wa_message
  on order_intake.customer_notices (wa_message_id) where wa_message_id is not null;
comment on table order_intake.customer_notices is
  'One row per intended outbound WhatsApp notice. dedupe_key = confirmed:<mirror_id> | delivered:<mirror_id> | credit:<credit_task_id>. state=shadow means "would have sent" while flags are off.';

create table if not exists order_intake.customer_notice_lines (
  notice_id        uuid not null references order_intake.customer_notices(notice_id) on delete cascade,
  line_mirror_id   uuid references private_core.orders_mirror_lines(line_mirror_id),
  item_id          text,
  item_label       text not null,
  qty_ordered      numeric(24,8) not null check (qty_ordered >= 0),
  qty_delivering   numeric(24,8) not null check (qty_delivering >= 0),
  resolution       text check (resolution in ('credit','next_route','substitute')),
  substitute_label text,
  primary key (notice_id, item_label),
  constraint customer_notice_lines_qty_check check (qty_delivering <= qty_ordered),
  -- a short line must say what happens to the shortfall
  constraint customer_notice_lines_resolution_check
    check (resolution is not null or qty_delivering = qty_ordered)
);

create table if not exists order_intake.customer_notice_events (
  event_id   bigserial primary key,
  notice_id  uuid not null references order_intake.customer_notices(notice_id) on delete cascade,
  event      text not null,
  actor      text,
  meta       jsonb,
  created_at timestamptz not null default now()
);
create index if not exists idx_customer_notice_events_notice
  on order_intake.customer_notice_events (notice_id, event);

create or replace function order_intake.fn_customer_notices_touch()
returns trigger language plpgsql as $$
begin
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists trg_customer_notices_touch on order_intake.customer_notices;
create trigger trg_customer_notices_touch
  before update on order_intake.customer_notices
  for each row execute function order_intake.fn_customer_notices_touch();

-- ---------------------------------------------------------------------------
-- 3. Consent columns
-- ---------------------------------------------------------------------------
alter table order_intake.wa_customer_map
  add column if not exists notices_enabled      boolean not null default true,
  add column if not exists notices_opt_in_at    timestamptz,
  add column if not exists marketing_opt_out_at timestamptz;
comment on column order_intake.wa_customer_map.notices_enabled is
  'Staff kill switch for utility notices to this customer (default true). Marketing additionally requires marketing_opt_out_at IS NULL.';

-- ---------------------------------------------------------------------------
-- 4. change_log actions (same DO-block form as 0241)
-- ---------------------------------------------------------------------------
do $$
declare def text;
begin
  select pg_get_constraintdef(oid) into def
    from pg_constraint
   where conrelid = 'private_core.change_log'::regclass and conname = 'change_log_action_check';
  if def is null then raise exception '0350: change_log_action_check not found'; end if;
  if def like '%CUSTOMER_NOTICE_APPROVED%' then return; end if;
  def := replace(def, 'ARRAY[',
    'ARRAY[''CUSTOMER_NOTICE_APPROVED''::text, ''CUSTOMER_NOTICE_SUPPRESSED''::text, ');
  execute 'alter table private_core.change_log drop constraint change_log_action_check';
  execute 'alter table private_core.change_log add constraint change_log_action_check ' || def;
end $$;

-- ---------------------------------------------------------------------------
-- 5. Flags (OFF)
-- ---------------------------------------------------------------------------
insert into private_core.feature_flags (flag_key, enabled, value, description, updated_by)
values
  ('customer_notices_live', false, '{"allowlist":[]}'::jsonb,
   'WhatsApp customer notices. enabled=false => shadow mode (rows created, nothing sent). value.allowlist = ["9725..."] or "*".',
   'migration 0350'),
  ('customer_notices_kinds', true, '{"kinds":["confirmed_full","confirmed_partial","delivered"]}'::jsonb,
   'Notice kinds allowed to leave shadow when customer_notices_live is enabled.',
   'migration 0350')
on conflict (flag_key) do nothing;

-- ---------------------------------------------------------------------------
-- 6. Stats view (spec §9)
-- ---------------------------------------------------------------------------
create or replace view order_intake.v_customer_notice_stats as
select kind, state, count(*)::int as n,
       percentile_cont(0.5) within group (order by extract(epoch from (sent_at - created_at)) / 60)
         filter (where sent_at is not null)     as median_min_to_sent,
       percentile_cont(0.5) within group (order by extract(epoch from (approved_at - created_at)) / 60)
         filter (where approved_at is not null) as median_min_to_approved
  from order_intake.customer_notices
 where created_at > now() - interval '30 days'
 group by kind, state;

-- ---------------------------------------------------------------------------
-- 7. Cron (same form as 0330; unschedule guarded by existence)
-- ---------------------------------------------------------------------------
select cron.unschedule('customer_notices_tick')
 where exists (select 1 from cron.job where jobname = 'customer_notices_tick');
select cron.schedule(
  'customer_notices_tick',
  '2,17,32,47 * * * *',
  $job$
    select net.http_post(
      url := 'https://gt-factory-os-api-production.up.railway.app/api/v1/internal/jobs/customer-notices-tick',
      headers := jsonb_build_object(
        'Content-Type', 'application/json',
        'Authorization', 'Bearer ' || (
          select decrypted_secret from vault.decrypted_secrets
           where name = 'factory_os_job_runner_token')),
      body := '{}'::jsonb,
      timeout_milliseconds := 240000);
  $job$);

select cron.unschedule('customer_notice_reminder')
 where exists (select 1 from cron.job where jobname = 'customer_notice_reminder');
-- 16:30 Israel = 13:30 UTC (IDT) / 14:30 UTC (IST); 07:30 Israel = 04:30 / 05:30 UTC.
select cron.schedule(
  'customer_notice_reminder',
  '30 4,5,13,14 * * *',
  $job$
    select net.http_post(
      url := 'https://rvadsozabmxkkrktwgnv.supabase.co/functions/v1/factory_os_jobs',
      headers := jsonb_build_object(
        'Content-Type', 'application/json',
        'Authorization', 'Bearer ' || (
          select decrypted_secret from vault.decrypted_secrets
           where name = 'factory_os_service_role_jwt')),
      body := jsonb_build_object('job', 'customer_notice_reminder'),
      timeout_milliseconds := 60000);
  $job$);

commit;
```

- [ ] **Step 5: Bracket again (FR2), then run the test**

Run: `ls db/migrations | tail -3` — expected: `0349_…`, `0350_customer_notices.sql` and nothing else at 0350.
Run: `psql "$DATABASE_URL" -f db/migrations/0350_customer_notices.sql && pg_prove -d "$DATABASE_URL" db/tests/0350_customer_notices.test.sql`
Expected: `16/16` (or "deferred" when no DB).

- [ ] **Step 6: Commit**

```bash
git add db/migrations/0350_customer_notices.sql db/tests/0350_customer_notices.test.sql
git commit -m "feat(notices): schema, consent, audit actions, flags and cron for WhatsApp customer notices (0350)"
```

---

### Task 2: `notices/types.ts` + `notices/time.ts` (Asia/Jerusalem helpers)

**Files:**
- Create: `api/src/order-intake/notices/types.ts`
- Create: `api/src/order-intake/notices/time.ts`
- Test: `api/src/order-intake/notices/__tests__/time.test.ts`

**Interfaces:**
- Produces: every type below (used by all later tasks) and `ilParts`, `ilOffsetMinutes`, `ilDateTimeToUtc`, `addDays`, `sendNotBefore`, `ilDate`, `ilWeekdayName`, `ilTimeHm`.

- [ ] **Step 1: Write `types.ts`** (no test — types only)

```ts
// Shared shapes for the customer-notices module. No logic here.

export const NOTICE_KINDS = [
  'confirmed_full', 'confirmed_partial', 'delivered', 'credit_issued',
  'payment_due_soon', 'payment_overdue', 'reorder_nudge',
] as const;
export type NoticeKind = (typeof NOTICE_KINDS)[number];

export const NOTICE_STATES = [
  'draft', 'pending_approval', 'approved', 'sent', 'delivered', 'read',
  'failed', 'suppressed', 'expired', 'shadow',
] as const;
export type NoticeState = (typeof NOTICE_STATES)[number];

export type LineResolution = 'credit' | 'next_route' | 'substitute';

export interface NoticeLine {
  item_label: string;
  item_id: string | null;
  line_mirror_id: string | null;
  qty_ordered: number;
  qty_delivering: number;
  resolution: LineResolution | null;
  substitute_label: string | null;
}

export interface NoticeRow {
  notice_id: string;
  kind: NoticeKind;
  state: NoticeState;
  wa_phone: string;
  shopify_customer_id: string | null;
  shopify_order_name: string | null;
  mirror_id: string | null;
  lw_task_id: string | null;
  credit_task_id: string | null;
  dedupe_key: string;
  template_name: string | null;
  template_params: string[];
  header_image_url: string | null;
  delivery_date: string | null;      // 'YYYY-MM-DD'
  send_not_before: string | null;    // ISO
  wa_message_id: string | null;
  attempts: number;
  created_at: string;
  recipient_name?: string | null;    // orders_mirror.lw_destination_recipient_name (list endpoints)
  lines: NoticeLine[];
}

export interface NewNotice {
  kind: NoticeKind;
  state: NoticeState;
  wa_phone: string;
  shopify_customer_id: string | null;
  shopify_order_name: string | null;
  mirror_id: string | null;
  lw_task_id: string | null;
  credit_task_id?: string | null;
  dedupe_key: string;
  template_name: string | null;
  template_params: string[];
  header_image_url: string | null;
  delivery_date: string | null;
  send_not_before: string | null;
  lines: NoticeLine[];
}

// What /tasks/show tells us (strings trimmed, empty => null).
export interface TaskShow {
  status: string | null;
  pick_status: string | null;
  pickup_at: string | null;
  photo_url: string | null;
}

export interface Observation extends TaskShow {
  mirror_id: string;
  lw_task_id: string;
  observed_at: string;
}

export interface OpenTaskLine {
  line_mirror_id: string;
  item_id: string | null;
  lw_sku: string;
  lw_name: string | null;
  qty_ordered: number;
}

export interface OpenTask {
  mirror_id: string;
  lw_task_id: string;
  wp_order_id: string | null;
  lw_status: string;
  recipient_name: string | null;
  created_at: string;
  lines: OpenTaskLine[];
}

export interface DeliveredTask {
  mirror_id: string;
  lw_task_id: string;
  lw_status: string;
  lw_completed_at: string | null;
  lw_photo_url: string | null;
  wp_order_id: string | null;
  wa_phone: string;
  shopify_customer_id: string | null;
}

export interface CreditedTask {
  credit_task_id: string;
  mirror_id: string;
  wp_order_id: string | null;
  item_id: string;
  item_label: string;
  gi_document_id: string;
  wa_phone: string;
  shopify_customer_id: string | null;
}

export interface CancelledAfterConfirm {
  notice_id: string;
  wa_phone: string;
  shopify_order_name: string | null;
  lw_status: string;
}

export interface NoticeFlags {
  masterEnabled: boolean;          // env WHATSAPP_NOTICES_ENABLED
  live: boolean;                   // feature_flags.customer_notices_live.enabled
  allowlist: string[] | '*';       // value.allowlist
  kinds: NoticeKind[];             // customer_notices_kinds value.kinds
}

export interface Actor { user_id: string; display_name: string }
```

- [ ] **Step 2: Write the failing time tests**

`api/src/order-intake/notices/__tests__/time.test.ts`:

```ts
import { describe, it, expect } from 'vitest';
import { ilParts, ilOffsetMinutes, ilDateTimeToUtc, addDays, sendNotBefore, ilDate, ilWeekdayName, ilTimeHm } from '../time.js';

describe('Asia/Jerusalem helpers', () => {
  it('reads local parts and the DST offset', () => {
    const summer = new Date('2026-09-09T11:04:00Z'); // IDT = UTC+3
    expect(ilParts(summer)).toEqual({ ymd: '2026-09-09', hour: 14, minute: 4 });
    expect(ilOffsetMinutes(summer)).toBe(180);
    const winter = new Date('2026-01-15T11:04:00Z'); // IST = UTC+2
    expect(ilParts(winter)).toEqual({ ymd: '2026-01-15', hour: 13, minute: 4 });
    expect(ilOffsetMinutes(winter)).toBe(120);
  });

  it('converts a local date+hour back to UTC', () => {
    expect(ilDateTimeToUtc('2026-09-10', 7).toISOString()).toBe('2026-09-10T04:00:00.000Z');
    expect(ilDateTimeToUtc('2026-01-15', 7).toISOString()).toBe('2026-01-15T05:00:00.000Z');
  });

  it('adds days on the calendar', () => {
    expect(addDays('2026-09-30', 1)).toBe('2026-10-01');
    expect(addDays('2026-01-01', -1)).toBe('2025-12-31');
  });

  it('sendNotBefore: inside 07:00–21:00 returns now; outside returns the next 07:00', () => {
    const noon = new Date('2026-09-09T09:00:00Z'); // 12:00 IDT
    expect(sendNotBefore(noon)).toBe(noon);
    const late = new Date('2026-09-09T19:30:00Z'); // 22:30 IDT
    expect(sendNotBefore(late).toISOString()).toBe('2026-09-10T04:00:00.000Z');
    const early = new Date('2026-09-10T02:15:00Z'); // 05:15 IDT
    expect(sendNotBefore(early).toISOString()).toBe('2026-09-10T04:00:00.000Z');
  });

  it('formats dates, weekdays and times in Hebrew', () => {
    expect(ilDate('2026-09-09T22:30:00Z')).toBe('2026-09-10'); // 01:30 next day IDT
    expect(ilWeekdayName('2026-09-10')).toBe('יום חמישי');
    expect(ilWeekdayName('2026-09-12')).toBe('שבת');
    expect(ilTimeHm('2026-09-09T08:20:00Z')).toBe('11:20');
  });
});
```

- [ ] **Step 3: Run to verify it fails**

Run: `npx vitest run api/src/order-intake/notices/__tests__/time.test.ts`
Expected: FAIL — cannot resolve `../time.js`.

- [ ] **Step 4: Write `time.ts`**

```ts
// Asia/Jerusalem time helpers for the notices module. Pure; Intl only.
// The API runs on Node 20 (Intl 'longOffset' available).

export const IL_TZ = 'Asia/Jerusalem';

const PARTS_FMT = new Intl.DateTimeFormat('en-CA', {
  timeZone: IL_TZ, year: 'numeric', month: '2-digit', day: '2-digit',
  hour: '2-digit', minute: '2-digit', hour12: false,
});

export interface IlParts { ymd: string; hour: number; minute: number }

export function ilParts(d: Date): IlParts {
  const p: Record<string, string> = {};
  for (const x of PARTS_FMT.formatToParts(d)) p[x.type] = x.value;
  return { ymd: `${p.year}-${p.month}-${p.day}`, hour: Number(p.hour) % 24, minute: Number(p.minute) };
}

export function ilOffsetMinutes(d: Date): number {
  const name = new Intl.DateTimeFormat('en-US', { timeZone: IL_TZ, timeZoneName: 'longOffset' })
    .formatToParts(d).find((x) => x.type === 'timeZoneName')?.value ?? 'GMT+00:00';
  const m = /GMT([+-])(\d{2}):(\d{2})/.exec(name);
  if (!m) return 0;
  return (m[1] === '-' ? -1 : 1) * (Number(m[2]) * 60 + Number(m[3]));
}

// Local wall-clock (ymd, hour, minute) in Israel -> UTC instant.
export function ilDateTimeToUtc(ymd: string, hour: number, minute = 0): Date {
  const [y, mo, d] = ymd.split('-').map(Number);
  const naive = Date.UTC(y, mo - 1, d, hour, minute);
  return new Date(naive - ilOffsetMinutes(new Date(naive)) * 60_000);
}

export function addDays(ymd: string, n: number): string {
  const [y, mo, d] = ymd.split('-').map(Number);
  return new Date(Date.UTC(y, mo - 1, d + n)).toISOString().slice(0, 10);
}

// Quiet hours: proactive sends only between openHour and closeHour local time.
export function sendNotBefore(now: Date, openHour = 7, closeHour = 21): Date {
  const { ymd, hour } = ilParts(now);
  if (hour >= openHour && hour < closeHour) return now;
  return ilDateTimeToUtc(hour < openHour ? ymd : addDays(ymd, 1), openHour);
}

export function ilDate(iso: string): string {
  return ilParts(new Date(iso)).ymd;
}

export function ilWeekdayName(ymd: string): string {
  return new Intl.DateTimeFormat('he-IL', { timeZone: IL_TZ, weekday: 'long' }).format(ilDateTimeToUtc(ymd, 12));
}

export function ilTimeHm(iso: string): string {
  const { hour, minute } = ilParts(new Date(iso));
  return `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`;
}
```

- [ ] **Step 5: Run to verify it passes**

Run: `npx vitest run api/src/order-intake/notices/__tests__/time.test.ts`
Expected: 5 passed. If `ilWeekdayName` returns `יום חמישי` with a different Unicode form on this ICU, adjust the expected string to what Node prints, never the function.

- [ ] **Step 6: Commit**

```bash
git add api/src/order-intake/notices/types.ts api/src/order-intake/notices/time.ts api/src/order-intake/notices/__tests__/time.test.ts
git commit -m "feat(notices): shared types and Asia/Jerusalem time helpers"
```

---

### Task 3: `notices/render.ts` — template parameters (the Hebrew copy)

**Files:**
- Create: `api/src/order-intake/notices/render.ts`
- Test: `api/src/order-intake/notices/__tests__/render.test.ts`

**Interfaces:**
- Consumes: `NoticeLine` (Task 2), `ilDate`, `addDays`, `ilWeekdayName`, `ilTimeHm`, `ilParts` (Task 2).
- Produces: `TEMPLATES`, `TEMPLATE_LANG`, `cleanParam(s)`, `renderDeliveryDay(ymd, now)`, `buildConfirmedTemplate(lines, ymd, now) → { template_name, params }`, `buildDeliveredTemplate(completedAtIso, now, photoUrl) → { template_name, params, header_image_url }`, `buildCreditTemplate(itemLabel, orderName) → { template_name, params }`.

- [ ] **Step 1: Write the failing tests**

```ts
import { describe, it, expect } from 'vitest';
import { buildConfirmedTemplate, buildDeliveredTemplate, buildCreditTemplate, cleanParam, renderDeliveryDay, TEMPLATES } from '../render.js';
import type { NoticeLine } from '../types.js';

const NOW = new Date('2026-09-09T12:00:00Z'); // Wed 15:00 IDT
const line = (label: string, ordered: number, delivering: number, resolution: NoticeLine['resolution'] = null, sub: string | null = null): NoticeLine =>
  ({ item_label: label, item_id: null, line_mirror_id: null, qty_ordered: ordered, qty_delivering: delivering, resolution, substitute_label: sub });

describe('cleanParam', () => {
  it('strips newlines/tabs and runs of spaces, trims, caps length', () => {
    expect(cleanParam(' a\nb\tc     d ')).toBe('a b c   d');
    expect(cleanParam('x'.repeat(1200))).toHaveLength(1000);
  });
});

describe('renderDeliveryDay', () => {
  it('says today / tomorrow / weekday', () => {
    expect(renderDeliveryDay('2026-09-09', NOW)).toBe('היום, יום רביעי 9.9');
    expect(renderDeliveryDay('2026-09-10', NOW)).toBe('מחר, יום חמישי 10.9');
    expect(renderDeliveryDay('2026-09-13', NOW)).toBe('יום ראשון 13.9');
  });
});

describe('buildConfirmedTemplate', () => {
  it('full pick → the full template with day + one-line list', () => {
    const t = buildConfirmedTemplate([line('DETOX 1000ml', 12, 12), line('FRESH 1000ml', 6, 6)], '2026-09-10', NOW);
    expect(t.template_name).toBe(TEMPLATES.confirmed_full);
    expect(t.params).toEqual(['מחר, יום חמישי 10.9', 'DETOX 1000ml ×12 · FRESH 1000ml ×6']);
    for (const p of t.params) expect(p).not.toMatch(/\n/);
  });

  it('short pick → the partial template with shipping, short and resolution lines', () => {
    const t = buildConfirmedTemplate(
      [line('DETOX 1000ml', 12, 12), line('FRESH 1000ml', 6, 4, 'credit'), line('MINT 500ml', 6, 0, 'substitute', 'MINT 1000ml ×3')],
      '2026-09-10', NOW,
    );
    expect(t.template_name).toBe(TEMPLATES.confirmed_partial);
    expect(t.params[1]).toBe('DETOX 1000ml ×12 · FRESH 1000ml ×4');
    expect(t.params[2]).toBe('FRESH 1000ml ×2 מתוך 6 · MINT 500ml ×6');
    expect(t.params[3]).toBe('FRESH 1000ml — יזוכה בחשבונית · במקום MINT 500ml נשלח MINT 1000ml ×3.');
  });

  it('never carries a price or currency sign', () => {
    const t = buildConfirmedTemplate([line('DETOX 1000ml', 12, 12)], '2026-09-10', NOW);
    expect(t.params.join(' ')).not.toMatch(/₪|\d+\.\d\d/);
  });
});

describe('buildDeliveredTemplate', () => {
  it('with a photo → image-header template; without → nophoto variant', () => {
    const a = buildDeliveredTemplate('2026-09-09T08:20:00Z', NOW, 'https://x/pod.jpg');
    expect(a).toEqual({ template_name: TEMPLATES.delivered, params: ['היום 11:20'], header_image_url: 'https://x/pod.jpg' });
    const b = buildDeliveredTemplate(null, NOW, null);
    expect(b).toEqual({ template_name: TEMPLATES.delivered_nophoto, params: ['היום'], header_image_url: null });
    const c = buildDeliveredTemplate('2026-09-08T08:20:00Z', NOW, null);
    expect(c.params).toEqual(['8.9 11:20']);
  });
});

describe('buildCreditTemplate', () => {
  it('names the item and the order', () => {
    expect(buildCreditTemplate('FRESH 1000ml', '#GT14512')).toEqual({ template_name: TEMPLATES.credit_issued, params: ['FRESH 1000ml', '#GT14512'] });
  });
});
```

- [ ] **Step 2: Run to verify it fails** — `npx vitest run api/src/order-intake/notices/__tests__/render.test.ts` → FAIL (module missing).

- [ ] **Step 3: Write `render.ts`**

```ts
// Template parameters for the customer notices. Pure. The Hebrew copy of every
// template body lives in Meta (WhatsApp Manager) under the names below; this
// file only produces the {{n}} values, so a wording change is a new template
// (_v2), never an edit to a live one.

import type { NoticeLine } from './types.js';
import { ilDate, addDays, ilWeekdayName, ilTimeHm, ilParts } from './time.js';

export const TEMPLATES = {
  confirmed_full: 'gt_order_confirmed_full_v1',
  confirmed_partial: 'gt_order_confirmed_partial_v1',
  delivered: 'gt_order_delivered_v1',
  delivered_nophoto: 'gt_order_delivered_nophoto_v1',
  credit_issued: 'gt_credit_issued_v1',
} as const;
export const TEMPLATE_LANG = 'he';

const MAX_PARAM = 1000;

// Meta rejects template variables with newlines, tabs or 4+ consecutive spaces.
export function cleanParam(s: string): string {
  return s.replace(/[\r\n\t]+/g, ' ').replace(/ {4,}/g, '   ').trim().slice(0, MAX_PARAM);
}

function qty(n: number): string {
  return Number.isInteger(n) ? String(n) : String(Number(n.toFixed(2)));
}

function dayMonth(ymd: string): string {
  const [, m, d] = ymd.split('-').map(Number);
  return `${d}.${m}`;
}

export function renderDeliveryDay(deliveryYmd: string, now: Date): string {
  const today = ilDate(now.toISOString());
  const label = `${ilWeekdayName(deliveryYmd)} ${dayMonth(deliveryYmd)}`;
  if (deliveryYmd === today) return `היום, ${label}`;
  if (deliveryYmd === addDays(today, 1)) return `מחר, ${label}`;
  return label;
}

function renderDeliveringLines(lines: NoticeLine[]): string {
  return cleanParam(lines.filter((l) => l.qty_delivering > 0).map((l) => `${l.item_label} ×${qty(l.qty_delivering)}`).join(' · '));
}

function renderShortLines(lines: NoticeLine[]): string {
  return cleanParam(lines.filter((l) => l.qty_delivering < l.qty_ordered).map((l) =>
    l.qty_delivering === 0
      ? `${l.item_label} ×${qty(l.qty_ordered)}`
      : `${l.item_label} ×${qty(l.qty_ordered - l.qty_delivering)} מתוך ${qty(l.qty_ordered)}`,
  ).join(' · '));
}

function renderResolutions(lines: NoticeLine[]): string {
  const words = lines.filter((l) => l.qty_delivering < l.qty_ordered).map((l) => {
    if (l.resolution === 'substitute') return `במקום ${l.item_label} נשלח ${l.substitute_label ?? ''}`.trim();
    if (l.resolution === 'next_route') return `${l.item_label} — יישלח בסבב הבא`;
    return `${l.item_label} — יזוכה בחשבונית`;
  });
  return cleanParam(words.join(' · ') + '.');
}

export function buildConfirmedTemplate(lines: NoticeLine[], deliveryYmd: string, now: Date): { template_name: string; params: string[] } {
  const day = renderDeliveryDay(deliveryYmd, now);
  const delivering = renderDeliveringLines(lines);
  const isShort = lines.some((l) => l.qty_delivering < l.qty_ordered);
  if (!isShort) return { template_name: TEMPLATES.confirmed_full, params: [day, delivering] };
  return { template_name: TEMPLATES.confirmed_partial, params: [day, delivering || '—', renderShortLines(lines), renderResolutions(lines)] };
}

export function buildDeliveredTemplate(completedAtIso: string | null, now: Date, photoUrl: string | null): { template_name: string; params: string[]; header_image_url: string | null } {
  let when = 'היום';
  if (completedAtIso) {
    const ymd = ilDate(completedAtIso);
    const hm = ilTimeHm(completedAtIso);
    when = ymd === ilParts(now).ymd ? `היום ${hm}` : `${dayMonth(ymd)} ${hm}`;
  }
  return photoUrl
    ? { template_name: TEMPLATES.delivered, params: [when], header_image_url: photoUrl }
    : { template_name: TEMPLATES.delivered_nophoto, params: [when], header_image_url: null };
}

export function buildCreditTemplate(itemLabel: string, orderName: string | null): { template_name: string; params: string[] } {
  return { template_name: TEMPLATES.credit_issued, params: [cleanParam(itemLabel), cleanParam(orderName ?? '')] };
}
```

- [ ] **Step 4: Run to verify it passes** — expected 7 passed.

- [ ] **Step 5: Commit**

```bash
git add api/src/order-intake/notices/render.ts api/src/order-intake/notices/__tests__/render.test.ts
git commit -m "feat(notices): template parameter builders with the locked Hebrew copy"
```

---

### Task 4: `whatsapp/send.ts` — template send + typed send error

**Files:**
- Modify: `api/src/order-intake/whatsapp/send.ts`
- Test: `api/src/order-intake/whatsapp/__tests__/send.test.ts` (new)

**Interfaces:**
- Produces: `WhatsAppPort.sendTemplate(to, tpl: TemplateMessage): Promise<SendResult>`; `class WhatsAppSendError extends Error { status: number; code: number | null }`; `interface TemplateMessage { name: string; language?: string; bodyParams: string[]; headerImageUrl?: string | null }`.

- [ ] **Step 1: Write the failing test**

```ts
import { describe, it, expect } from 'vitest';
import { createWhatsAppPort, WhatsAppSendError } from '../send.js';

function fakeFetch(status: number, body: unknown) {
  const calls: Array<{ url: string; init: any }> = [];
  const fetchFn = async (url: string, init: any) => {
    calls.push({ url, init });
    return { ok: status >= 200 && status < 300, status, text: async () => JSON.stringify(body) } as any;
  };
  return { fetchFn, calls };
}

describe('sendTemplate', () => {
  it('posts a template payload with body params and an optional image header', async () => {
    const { fetchFn, calls } = fakeFetch(200, { messages: [{ id: 'wamid.T1' }] });
    const port = createWhatsAppPort({ phoneNumberId: 'PNID', sendToken: 'tok', fetchFn });
    const res = await port.sendTemplate('972500000001', { name: 'gt_order_delivered_v1', bodyParams: ['היום 11:20'], headerImageUrl: 'https://x/pod.jpg' });
    expect(res.messageId).toBe('wamid.T1');
    const payload = JSON.parse(calls[0].init.body);
    expect(calls[0].url).toBe('https://graph.facebook.com/v21.0/PNID/messages');
    expect(payload).toEqual({
      messaging_product: 'whatsapp', to: '972500000001', type: 'template',
      template: {
        name: 'gt_order_delivered_v1', language: { code: 'he' },
        components: [
          { type: 'header', parameters: [{ type: 'image', image: { link: 'https://x/pod.jpg' } }] },
          { type: 'body', parameters: [{ type: 'text', text: 'היום 11:20' }] },
        ],
      },
    });
  });

  it('omits the header component and empty body when there are no params', async () => {
    const { fetchFn, calls } = fakeFetch(200, { messages: [{ id: 'wamid.T2' }] });
    const port = createWhatsAppPort({ phoneNumberId: 'PNID', sendToken: 'tok', fetchFn });
    await port.sendTemplate('972500000001', { name: 'x_v1', bodyParams: [] });
    expect(JSON.parse(calls[0].init.body).template.components).toEqual([]);
  });

  it('throws WhatsAppSendError carrying Meta error code on a non-2xx', async () => {
    const { fetchFn } = fakeFetch(400, { error: { code: 131049, message: 'frequency cap' } });
    const port = createWhatsAppPort({ phoneNumberId: 'PNID', sendToken: 'tok', fetchFn });
    await expect(port.sendTemplate('972500000001', { name: 'x_v1', bodyParams: [] })).rejects.toMatchObject({ status: 400, code: 131049 });
    await expect(port.sendText('972500000001', 'hi')).rejects.toBeInstanceOf(WhatsAppSendError);
  });
});
```

- [ ] **Step 2: Run to verify it fails** — `npx vitest run api/src/order-intake/whatsapp/__tests__/send.test.ts` → FAIL (`sendTemplate` not a function).

- [ ] **Step 3: Modify `send.ts`**

Add after the imports:

```ts
export interface TemplateMessage {
  name: string;
  language?: string;            // default 'he'
  bodyParams: string[];
  headerImageUrl?: string | null;
}

export class WhatsAppSendError extends Error {
  constructor(public readonly status: number, public readonly code: number | null, body: string) {
    super(`WhatsApp send failed status=${status} code=${code ?? 'n/a'} body=${body.slice(0, 300)}`);
    this.name = 'WhatsAppSendError';
  }
}
```

Add to `WhatsAppPort`:

```ts
  sendTemplate(to: string, tpl: TemplateMessage): Promise<SendResult>;
```

Replace the `if (!res.ok) throw new Error(...)` line inside `post` with:

```ts
      if (!res.ok) {
        let code: number | null = null;
        try { code = Number((JSON.parse(text) as { error?: { code?: number } }).error?.code ?? null) || null; } catch { /* non-JSON */ }
        throw new WhatsAppSendError(res.status, code, text);
      }
```

Add to the returned object, before `send(to, msg)`:

```ts
    sendTemplate(to, tpl) {
      const components: Array<Record<string, unknown>> = [];
      if (tpl.headerImageUrl) {
        components.push({ type: 'header', parameters: [{ type: 'image', image: { link: tpl.headerImageUrl } }] });
      }
      if (tpl.bodyParams.length > 0) {
        components.push({ type: 'body', parameters: tpl.bodyParams.map((text) => ({ type: 'text', text })) });
      }
      return post({
        to,
        type: 'template',
        template: { name: tpl.name, language: { code: tpl.language ?? 'he' }, components },
      });
    },
```

- [ ] **Step 4: Run all order-intake tests** — `npx vitest run api/src/order-intake` → expected all green (the existing 143 + 3 new + Task 2/3 tests). The `route.test.ts` deps object types `WorkerDeps` loosely (`as unknown as WorkerDeps`), so the new port method needs no fixture change.

- [ ] **Step 5: Commit**

```bash
git add api/src/order-intake/whatsapp/send.ts api/src/order-intake/whatsapp/__tests__/send.test.ts
git commit -m "feat(notices): WhatsApp template send with typed Meta error codes"
```

---

### Task 5: `notices/lionwheel_show.ts` — read `/tasks/show/<id>.json`

**Files:**
- Create: `api/src/order-intake/notices/lionwheel_show.ts`
- Test: `api/src/order-intake/notices/__tests__/lionwheel_show.test.ts`

**Interfaces:**
- Consumes: `TaskShow` (Task 2), `FetchFn` from `../shopify/graphql.js` (`(url: string, init?: RequestInit) => Promise<Response>`).
- Produces: `type LwShowFn = (lwTaskId: string) => Promise<TaskShow | null>`; `createLwShow({ baseUrl, apiKey, fetchFn?, timeoutMs? }): LwShowFn`.

The locked chain's `fetchTaskDetail` is not exported and must not be touched; this is a separate, smaller reader. Field names come from the live payload the chain already reads (`task.status`, `task.pick_status`, `task.pickup_at`, `task.photo_url`), no new guesses.

- [ ] **Step 1: Write the failing test**

```ts
import { describe, it, expect } from 'vitest';
import { createLwShow } from '../lionwheel_show.js';

function fetchOk(task: unknown) {
  const calls: string[] = [];
  const fetchFn = async (url: string) => { calls.push(url); return { ok: true, status: 200, json: async () => ({ task }) } as any; };
  return { fetchFn, calls };
}

describe('createLwShow', () => {
  it('builds the keyed URL and maps the four fields, trimming and nulling empties', async () => {
    const { fetchFn, calls } = fetchOk({ id: 27818514, status: 'ASSIGNED', pick_status: ' PICKED ', pickup_at: '2026-09-10T00:00:00.000+03:00', photo_url: '' });
    const show = createLwShow({ baseUrl: 'https://members.lionwheel.com/', apiKey: 'k 1', fetchFn });
    const res = await show('27818514');
    expect(calls[0]).toBe('https://members.lionwheel.com/api/v1/tasks/show/27818514.json?key=k%201');
    expect(res).toEqual({ status: 'ASSIGNED', pick_status: 'PICKED', pickup_at: '2026-09-10T00:00:00.000+03:00', photo_url: null });
  });

  it('returns null on non-2xx, malformed body, or a thrown fetch', async () => {
    const bad = createLwShow({ baseUrl: 'https://x', apiKey: 'k', fetchFn: async () => ({ ok: false, status: 500, json: async () => ({}) } as any) });
    expect(await bad('1')).toBeNull();
    const noTask = createLwShow({ baseUrl: 'https://x', apiKey: 'k', fetchFn: async () => ({ ok: true, status: 200, json: async () => ({}) } as any) });
    expect(await noTask('1')).toBeNull();
    const boom = createLwShow({ baseUrl: 'https://x', apiKey: 'k', fetchFn: async () => { throw new Error('net'); } });
    expect(await boom('1')).toBeNull();
  });
});
```

- [ ] **Step 2: Run to verify it fails** — module missing.

- [ ] **Step 3: Write `lionwheel_show.ts`**

```ts
// Reads one LionWheel task via /api/v1/tasks/show/<id>.json — the only endpoint
// that carries pick_status and pickup_at (verified live 2026-08-24 / 2026-09-09).
// Separate from the locked chain modules on purpose. Never throws.

import type { FetchFn } from '../shopify/graphql.js';
import type { TaskShow } from './types.js';

export interface LwShowConfig {
  baseUrl: string;      // LIONWHEEL_BASE_URL, default https://members.lionwheel.com
  apiKey: string;       // LIONWHEEL_API_KEY
  fetchFn?: FetchFn;
  timeoutMs?: number;   // default 15_000
}

export type LwShowFn = (lwTaskId: string) => Promise<TaskShow | null>;

function str(v: unknown): string | null {
  return typeof v === 'string' && v.trim() ? v.trim() : null;
}

export function createLwShow(cfg: LwShowConfig): LwShowFn {
  const fetchFn = cfg.fetchFn ?? (globalThis.fetch as FetchFn);
  const base = cfg.baseUrl.replace(/\/+$/, '');
  return async (lwTaskId) => {
    const url = `${base}/api/v1/tasks/show/${encodeURIComponent(lwTaskId)}.json?key=${encodeURIComponent(cfg.apiKey)}`;
    try {
      const res = await fetchFn(url, {
        headers: { 'User-Agent': 'GTFactoryOS/1.0', Accept: 'application/json' },
        signal: AbortSignal.timeout(cfg.timeoutMs ?? 15_000),
      });
      if (!res.ok) return null;
      const body = (await res.json()) as { task?: Record<string, unknown> };
      const t = body?.task;
      if (!t || typeof t !== 'object') return null;
      return { status: str(t.status), pick_status: str(t.pick_status), pickup_at: str(t.pickup_at), photo_url: str(t.photo_url) };
    } catch {
      return null;
    }
  };
}
```

- [ ] **Step 4: Run to verify it passes** — 2 passed.

- [ ] **Step 5: Commit**

```bash
git add api/src/order-intake/notices/lionwheel_show.ts api/src/order-intake/notices/__tests__/lionwheel_show.test.ts
git commit -m "feat(notices): LionWheel /tasks/show reader for pick_status and pickup_at"
```

---

### Task 6: `notices/shopify_order.ts` — order name → customer id

**Files:**
- Create: `api/src/order-intake/notices/shopify_order.ts`
- Test: `api/src/order-intake/notices/__tests__/shopify_order.test.ts`

**Interfaces:**
- Consumes: `GqlFn` from `../shopify/graphql.js`.
- Produces: `type OrderCustomerLookup = (orderName: string) => Promise<string | null>` (numeric Shopify customer id, e.g. `'7123456789'`); `createOrderCustomerLookup(gql): OrderCustomerLookup`.

`orders_mirror.wp_order_id` holds the Shopify order **name** (`#GT14519`, live sample 2026-09-09). Shopify's `orders(query: "name:GT14519")` filter matches the name without the `#`.

- [ ] **Step 1: Write the failing test**

```ts
import { describe, it, expect } from 'vitest';
import { createOrderCustomerLookup } from '../shopify_order.js';
import type { GqlFn } from '../../shopify/graphql.js';

function gqlReturning(edges: unknown[]) {
  const calls: Array<{ query: string; variables: any }> = [];
  const gql: GqlFn = async (query, variables) => { calls.push({ query, variables }); return { status: 200, data: { orders: { edges } } as any, errors: null }; };
  return { gql, calls };
}

describe('createOrderCustomerLookup', () => {
  it('queries by bare name and returns the numeric customer id', async () => {
    const { gql, calls } = gqlReturning([{ node: { name: '#GT14519', customer: { id: 'gid://shopify/Customer/7123456789' } } }]);
    const lookup = createOrderCustomerLookup(gql);
    expect(await lookup('#GT14519')).toBe('7123456789');
    expect(calls[0].variables).toEqual({ q: 'name:GT14519' });
  });

  it('rejects a near-miss name, a missing customer, and an empty name', async () => {
    expect(await createOrderCustomerLookup(gqlReturning([{ node: { name: '#GT145190', customer: { id: 'gid://shopify/Customer/1' } } }]).gql)('#GT14519')).toBeNull();
    expect(await createOrderCustomerLookup(gqlReturning([{ node: { name: '#GT14519', customer: null } }]).gql)('#GT14519')).toBeNull();
    expect(await createOrderCustomerLookup(gqlReturning([]).gql)('')).toBeNull();
  });
});
```

- [ ] **Step 2: Run to verify it fails.**

- [ ] **Step 3: Write `shopify_order.ts`**

```ts
// Resolve a Shopify order name (orders_mirror.wp_order_id, e.g. '#GT14519') to
// the numeric id of the customer who placed it. Read-only; one call per task.

import type { GqlFn } from '../shopify/graphql.js';

const ORDER_CUSTOMER_QUERY = `
  query OrderCustomer($q: String!) {
    orders(first: 1, query: $q) { edges { node { name customer { id } } } }
  }`;

export type OrderCustomerLookup = (orderName: string) => Promise<string | null>;

export function createOrderCustomerLookup(gql: GqlFn): OrderCustomerLookup {
  return async (orderName) => {
    const bare = (orderName ?? '').replace(/^#/, '').trim();
    if (!bare) return null;
    const res = await gql<{ orders: { edges: Array<{ node: { name: string; customer: { id: string } | null } }> } }>(
      ORDER_CUSTOMER_QUERY, { q: `name:${bare}` },
    );
    const node = res.data?.orders?.edges?.[0]?.node;
    if (!node) return null;
    if (node.name.replace(/^#/, '').toLowerCase() !== bare.toLowerCase()) return null;
    const id = node.customer?.id ?? null;
    return id ? id.replace(/^.*\//, '') : null;
  };
}
```

- [ ] **Step 4: Run to verify it passes** — 2 passed. Then verify the filter live once (read-only): from the repo root run

```bash
node --input-type=module -e "
import { createShopifyGraphQL } from './api/src/order-intake/shopify/graphql.ts';
" 2>/dev/null || echo 'live check: run via a tsx one-liner or skip if no Shopify env in this container'
```
If `SHOPIFY_STORE_DOMAIN`/`SHOPIFY_ADMIN_API_TOKEN` are available, query `name:GT14519` and confirm one edge with that name comes back; if the store's name filter needs the `#`, change the variable to `` `name:#${bare}` `` and the test expectation together. Record the outcome in the commit body.

- [ ] **Step 5: Commit**

```bash
git add api/src/order-intake/notices/shopify_order.ts api/src/order-intake/notices/__tests__/shopify_order.test.ts
git commit -m "feat(notices): Shopify order name to customer id lookup"
```

---

### Task 7: `notices/store.ts` (pg) + `__tests__/fake_store.ts`

**Files:**
- Create: `api/src/order-intake/notices/store.ts`
- Create: `api/src/order-intake/notices/__tests__/fake_store.ts`
- Test: `api/src/order-intake/notices/__tests__/fake_store.test.ts` (proves the fake honours the contract the tick relies on: dedupe, state filters)

**Interfaces:**
- Consumes: all types from Task 2; `pg.Pool`.
- Produces:

```ts
export interface NoticeStore {
  getFlags(): Promise<NoticeFlags>;
  listOpenTasks(sinceDays: number): Promise<OpenTask[]>;
  recordObservation(o: Observation): Promise<void>;
  resolvePhoneByShopifyCustomerId(customerId: string): Promise<{ wa_phone: string; notices_enabled: boolean } | null>;
  createNotice(n: NewNotice): Promise<NoticeRow | null>;          // null = dedupe_key already exists
  listNewlyDelivered(): Promise<DeliveredTask[]>;
  listNewlyCredited(): Promise<CreditedTask[]>;
  listConfirmedThenCancelled(): Promise<CancelledAfterConfirm[]>;
  appendEvent(noticeId: string, event: string, actor: string | null, meta?: unknown): Promise<void>;
  expireStale(): Promise<number>;
  listSendable(nowIso: string): Promise<NoticeRow[]>;
  markSent(noticeId: string, waMessageId: string | null): Promise<void>;
  markRetry(noticeId: string, nextAtIso: string, code: string, detail: string): Promise<void>;
  markFailed(noticeId: string, code: string, detail: string): Promise<void>;
  markShadow(noticeId: string): Promise<void>;
  findByWaMessageId(waMessageId: string): Promise<NoticeRow | null>;
  applyStatus(noticeId: string, status: 'sent' | 'delivered' | 'read' | 'failed', errorCode?: number | null): Promise<void>;
  latestNoticeForPhone(phone: string, kinds: NoticeKind[], sinceHours: number): Promise<NoticeRow | null>;
  getNotice(noticeId: string): Promise<NoticeRow | null>;
  listPending(): Promise<NoticeRow[]>;
  approve(noticeId: string, patch: ApprovePatch, actor: Actor): Promise<NoticeRow | null>;   // null = not pending_approval
  suppress(noticeId: string, reason: string, actor: Actor): Promise<NoticeRow | null>;
}
export interface ApprovePatch { delivery_date: string; lines: NoticeLine[]; template_name: string; template_params: string[]; send_not_before: string }
export function createPgNoticeStore(pool: Pool, opts: { masterEnabled: boolean }): NoticeStore
```

- [ ] **Step 1: Write the fake store + its test first**

`__tests__/fake_store.ts`:

```ts
// In-memory NoticeStore for tick/route tests. Mirrors the SQL semantics that
// matter: dedupe_key uniqueness, state filters, terminal sets.
import type {
  NoticeStore, ApprovePatch,
} from '../store.js';
import type {
  NoticeRow, NewNotice, OpenTask, Observation, DeliveredTask, CreditedTask, CancelledAfterConfirm, NoticeFlags, NoticeKind, Actor,
} from '../types.js';

export function fakeStore(init: {
  flags?: Partial<NoticeFlags>;
  openTasks?: OpenTask[];
  phones?: Record<string, { wa_phone: string; notices_enabled: boolean }>; // by numeric shopify customer id
  delivered?: DeliveredTask[];
  credited?: CreditedTask[];
  cancelled?: CancelledAfterConfirm[];
  now?: () => Date;
} = {}) {
  const now = init.now ?? (() => new Date());
  const notices = new Map<string, NoticeRow>();
  const observations: Observation[] = [];
  const events: Array<{ notice_id: string; event: string; actor: string | null; meta?: unknown }> = [];
  let seq = 0;
  const flags: NoticeFlags = { masterEnabled: false, live: false, allowlist: [], kinds: ['confirmed_full', 'confirmed_partial', 'delivered'], ...init.flags };
  const byDedupe = () => new Set([...notices.values()].map((n) => n.dedupe_key));
  const withLines = (n: NoticeRow) => ({ ...n, lines: n.lines.map((l) => ({ ...l })) });

  const store: NoticeStore = {
    async getFlags() { return { ...flags }; },
    async listOpenTasks() {
      return (init.openTasks ?? []).filter((t) => ![...notices.values()].some((n) => n.mirror_id === t.mirror_id && n.kind.startsWith('confirmed')));
    },
    async recordObservation(o) { observations.push(o); },
    async resolvePhoneByShopifyCustomerId(id) { return init.phones?.[id] ?? null; },
    async createNotice(n) {
      if (byDedupe().has(n.dedupe_key)) return null;
      const row: NoticeRow = { notice_id: `n-${++seq}`, wa_message_id: null, attempts: 0, created_at: now().toISOString(), credit_task_id: n.credit_task_id ?? null, ...n, lines: n.lines.map((l) => ({ ...l })) };
      notices.set(row.notice_id, row);
      return withLines(row);
    },
    async listNewlyDelivered() {
      return (init.delivered ?? []).filter((d) => [...notices.values()].some((n) => n.mirror_id === d.mirror_id && n.kind.startsWith('confirmed')) && !byDedupe().has(`delivered:${d.mirror_id}`));
    },
    async listNewlyCredited() { return (init.credited ?? []).filter((c) => !byDedupe().has(`credit:${c.credit_task_id}`)); },
    async listConfirmedThenCancelled() {
      return (init.cancelled ?? []).filter((c) => !events.some((e) => e.notice_id === c.notice_id && e.event === 'staff_alerted_cancel'));
    },
    async appendEvent(notice_id, event, actor, meta) { events.push({ notice_id, event, actor, meta }); },
    async expireStale() { return 0; },
    async listSendable(nowIso) {
      return [...notices.values()].filter((n) => n.state === 'approved' && (!n.send_not_before || n.send_not_before <= nowIso)).map(withLines);
    },
    async markSent(id, waMessageId) { const n = notices.get(id)!; n.state = 'sent'; n.wa_message_id = waMessageId; n.attempts++; },
    async markRetry(id, nextAt) { const n = notices.get(id)!; n.attempts++; n.send_not_before = nextAt; },
    async markFailed(id) { const n = notices.get(id)!; n.state = 'failed'; n.attempts++; },
    async markShadow(id) { notices.get(id)!.state = 'shadow'; },
    async findByWaMessageId(waId) { return [...notices.values()].find((n) => n.wa_message_id === waId) ?? null; },
    async applyStatus(id, status) { const n = notices.get(id)!; if (status === 'delivered' || status === 'read' || status === 'failed') n.state = status; },
    async latestNoticeForPhone(phone, kinds: NoticeKind[]) {
      return [...notices.values()].reverse().find((n) => n.wa_phone === phone && kinds.includes(n.kind) && ['sent', 'delivered', 'read'].includes(n.state)) ?? null;
    },
    async getNotice(id) { const n = notices.get(id); return n ? withLines(n) : null; },
    async listPending() { return [...notices.values()].filter((n) => n.state === 'pending_approval').map(withLines); },
    async approve(id, patch: ApprovePatch, actor: Actor) {
      const n = notices.get(id); if (!n || n.state !== 'pending_approval') return null;
      Object.assign(n, { state: 'approved', delivery_date: patch.delivery_date, lines: patch.lines.map((l) => ({ ...l })), template_name: patch.template_name, template_params: patch.template_params, send_not_before: patch.send_not_before });
      events.push({ notice_id: id, event: 'approved', actor: actor.display_name });
      return withLines(n);
    },
    async suppress(id, reason, actor) {
      const n = notices.get(id); if (!n || n.state !== 'pending_approval') return null;
      n.state = 'suppressed'; events.push({ notice_id: id, event: 'suppressed', actor: actor.display_name, meta: { reason } });
      return withLines(n);
    },
  };
  return { store, notices, observations, events, flags };
}
```

`__tests__/fake_store.test.ts`:

```ts
import { describe, it, expect } from 'vitest';
import { fakeStore } from './fake_store.js';

describe('fakeStore contract', () => {
  it('dedupes on dedupe_key and filters sendable by state and time', async () => {
    const { store } = fakeStore();
    const base = { kind: 'confirmed_full' as const, state: 'approved' as const, wa_phone: '9725', shopify_customer_id: '1', shopify_order_name: '#GT1', mirror_id: 'm1', lw_task_id: '1', dedupe_key: 'confirmed:m1', template_name: 't', template_params: [], header_image_url: null, delivery_date: null, send_not_before: '2026-09-10T04:00:00.000Z', lines: [] };
    expect(await store.createNotice(base)).not.toBeNull();
    expect(await store.createNotice(base)).toBeNull();
    expect(await store.listSendable('2026-09-10T03:00:00.000Z')).toHaveLength(0);
    expect(await store.listSendable('2026-09-10T04:00:00.000Z')).toHaveLength(1);
  });
});
```

- [ ] **Step 2: Run** — `npx vitest run api/src/order-intake/notices/__tests__/fake_store.test.ts` → FAIL (`../store.js` missing).

- [ ] **Step 3: Write `store.ts`**

```ts
// Durable state for the customer-notices module, over order_intake.* +
// read-only joins to private_core.orders_mirror / credit_tasks. No business
// logic; typed reads/writes only. The tick and routes depend on the interface;
// tests inject the in-memory fake.

import type { Pool, PoolClient } from 'pg';
import type {
  NoticeRow, NewNotice, NoticeLine, NoticeKind, NoticeFlags, OpenTask, Observation,
  DeliveredTask, CreditedTask, CancelledAfterConfirm, Actor,
} from './types.js';
import { NOTICE_KINDS } from './types.js';

export const TERMINAL_SUCCESS = ['COMPLETED', 'ROUNDTRIP_DELIVERED', 'DELIVERED'] as const;
export const TERMINAL_FAIL = ['CANCELED', 'CANCELLED', 'FAILED'] as const;
const TERMINAL_ALL = [...TERMINAL_SUCCESS, ...TERMINAL_FAIL];

export interface ApprovePatch {
  delivery_date: string;
  lines: NoticeLine[];
  template_name: string;
  template_params: string[];
  send_not_before: string;
}

export interface NoticeStore {
  getFlags(): Promise<NoticeFlags>;
  listOpenTasks(sinceDays: number): Promise<OpenTask[]>;
  recordObservation(o: Observation): Promise<void>;
  resolvePhoneByShopifyCustomerId(customerId: string): Promise<{ wa_phone: string; notices_enabled: boolean } | null>;
  createNotice(n: NewNotice): Promise<NoticeRow | null>;
  listNewlyDelivered(): Promise<DeliveredTask[]>;
  listNewlyCredited(): Promise<CreditedTask[]>;
  listConfirmedThenCancelled(): Promise<CancelledAfterConfirm[]>;
  appendEvent(noticeId: string, event: string, actor: string | null, meta?: unknown): Promise<void>;
  expireStale(): Promise<number>;
  listSendable(nowIso: string): Promise<NoticeRow[]>;
  markSent(noticeId: string, waMessageId: string | null): Promise<void>;
  markRetry(noticeId: string, nextAtIso: string, code: string, detail: string): Promise<void>;
  markFailed(noticeId: string, code: string, detail: string): Promise<void>;
  markShadow(noticeId: string): Promise<void>;
  findByWaMessageId(waMessageId: string): Promise<NoticeRow | null>;
  applyStatus(noticeId: string, status: 'sent' | 'delivered' | 'read' | 'failed', errorCode?: number | null): Promise<void>;
  latestNoticeForPhone(phone: string, kinds: NoticeKind[], sinceHours: number): Promise<NoticeRow | null>;
  getNotice(noticeId: string): Promise<NoticeRow | null>;
  listPending(): Promise<NoticeRow[]>;
  approve(noticeId: string, patch: ApprovePatch, actor: Actor): Promise<NoticeRow | null>;
  suppress(noticeId: string, reason: string, actor: Actor): Promise<NoticeRow | null>;
}

const NOTICE_SELECT = `
  n.notice_id, n.kind, n.state, n.wa_phone, n.shopify_customer_id, n.shopify_order_name,
  n.mirror_id, n.lw_task_id, n.credit_task_id, n.dedupe_key, n.template_name,
  n.template_params, n.header_image_url, n.delivery_date::text as delivery_date,
  n.send_not_before, n.wa_message_id, n.attempts, n.created_at,
  om.lw_destination_recipient_name as recipient_name,
  coalesce((select json_agg(json_build_object(
      'item_label', l.item_label, 'item_id', l.item_id, 'line_mirror_id', l.line_mirror_id,
      'qty_ordered', l.qty_ordered::float8, 'qty_delivering', l.qty_delivering::float8,
      'resolution', l.resolution, 'substitute_label', l.substitute_label) order by l.item_label)
    from order_intake.customer_notice_lines l where l.notice_id = n.notice_id), '[]'::json) as lines
  from order_intake.customer_notices n
  left join private_core.orders_mirror om on om.mirror_id = n.mirror_id`;

function rowToNotice(r: any): NoticeRow {
  return {
    ...r,
    template_params: Array.isArray(r.template_params) ? r.template_params : [],
    send_not_before: r.send_not_before ? new Date(r.send_not_before).toISOString() : null,
    created_at: new Date(r.created_at).toISOString(),
    lines: (r.lines ?? []) as NoticeLine[],
  };
}

async function insertChangeLog(c: PoolClient, actor: Actor, action: string, noticeId: string, before: unknown, after: unknown): Promise<void> {
  await c.query(
    `insert into private_core.change_log
       (entity_table, entity_id, action, changed_fields, old_values, new_values, actor_user_id, actor_snapshot)
     values ('customer_notices', $1, $2, '["state"]'::jsonb, $3::jsonb, $4::jsonb, $5::uuid, $6)`,
    [noticeId, action, JSON.stringify(before), JSON.stringify(after), actor.user_id, actor.display_name],
  );
}

export function createPgNoticeStore(pool: Pool, opts: { masterEnabled: boolean }): NoticeStore {
  async function one(sql: string, params: unknown[]): Promise<NoticeRow | null> {
    const { rows } = await pool.query(sql, params);
    return rows[0] ? rowToNotice(rows[0]) : null;
  }
  async function many(sql: string, params: unknown[]): Promise<NoticeRow[]> {
    const { rows } = await pool.query(sql, params);
    return rows.map(rowToNotice);
  }

  return {
    async getFlags() {
      const { rows } = await pool.query(
        `select flag_key, enabled, value from private_core.feature_flags
          where flag_key in ('customer_notices_live','customer_notices_kinds')`);
      const live = rows.find((r) => r.flag_key === 'customer_notices_live');
      const kindsRow = rows.find((r) => r.flag_key === 'customer_notices_kinds');
      const rawAllow = live?.value?.allowlist;
      const allowlist: string[] | '*' = rawAllow === '*' ? '*' : Array.isArray(rawAllow) ? rawAllow.map(String) : [];
      const kinds = Array.isArray(kindsRow?.value?.kinds)
        ? (kindsRow.value.kinds as string[]).filter((k): k is NoticeKind => (NOTICE_KINDS as readonly string[]).includes(k))
        : [];
      return { masterEnabled: opts.masterEnabled, live: live?.enabled === true, allowlist, kinds: kindsRow?.enabled === false ? [] : kinds };
    },

    async listOpenTasks(sinceDays) {
      const { rows } = await pool.query(
        `select om.mirror_id, om.lw_task_id::text as lw_task_id, om.wp_order_id, om.lw_status,
                om.lw_destination_recipient_name as recipient_name, om.created_at,
                coalesce(json_agg(json_build_object(
                    'line_mirror_id', l.line_mirror_id, 'item_id', l.item_id, 'lw_sku', l.lw_sku,
                    'lw_name', l.lw_name, 'qty_ordered', l.lw_qty_ordered::float8) order by l.lw_order_item_id)
                  filter (where l.line_mirror_id is not null), '[]'::json) as lines
           from private_core.orders_mirror om
           left join private_core.orders_mirror_lines l on l.mirror_id = om.mirror_id
          where om.retired_at is null
            and om.lw_status <> all($2::text[])
            and om.created_at > now() - make_interval(days => $1)
            and not exists (select 1 from order_intake.customer_notices n
                             where n.mirror_id = om.mirror_id and n.kind in ('confirmed_full','confirmed_partial'))
          group by om.mirror_id
          order by om.created_at`,
        [sinceDays, TERMINAL_ALL]);
      return rows.map((r) => ({ ...r, created_at: new Date(r.created_at).toISOString() }));
    },

    async recordObservation(o) {
      await pool.query(
        `insert into order_intake.lw_pick_observations (mirror_id, lw_task_id, lw_status, pick_status, pickup_at, photo_url, observed_at)
         values ($1,$2,$3,$4,$5,$6,$7)`,
        [o.mirror_id, o.lw_task_id, o.status, o.pick_status, o.pickup_at, o.photo_url, o.observed_at]);
    },

    async resolvePhoneByShopifyCustomerId(customerId) {
      const { rows } = await pool.query(
        `select wa_phone, notices_enabled from order_intake.wa_customer_map
          where regexp_replace(coalesce(shopify_customer_id, ''), '^.*/', '') = $1
          order by updated_at desc limit 1`, [customerId]);
      return rows[0] ?? null;
    },

    async createNotice(n) {
      const c = await pool.connect();
      try {
        await c.query('begin');
        const { rows } = await c.query(
          `insert into order_intake.customer_notices
             (kind, state, wa_phone, shopify_customer_id, shopify_order_name, mirror_id, lw_task_id, credit_task_id,
              dedupe_key, template_name, template_params, header_image_url, delivery_date, send_not_before)
           values ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11::jsonb,$12,$13::date,$14)
           on conflict (dedupe_key) do nothing
           returning notice_id`,
          [n.kind, n.state, n.wa_phone, n.shopify_customer_id, n.shopify_order_name, n.mirror_id, n.lw_task_id,
           n.credit_task_id ?? null, n.dedupe_key, n.template_name, JSON.stringify(n.template_params), n.header_image_url,
           n.delivery_date, n.send_not_before]);
        if (!rows[0]) { await c.query('rollback'); return null; }
        const id: string = rows[0].notice_id;
        for (const l of n.lines) {
          await c.query(
            `insert into order_intake.customer_notice_lines
               (notice_id, line_mirror_id, item_id, item_label, qty_ordered, qty_delivering, resolution, substitute_label)
             values ($1,$2,$3,$4,$5,$6,$7,$8) on conflict (notice_id, item_label) do nothing`,
            [id, l.line_mirror_id, l.item_id, l.item_label, l.qty_ordered, l.qty_delivering, l.resolution, l.substitute_label]);
        }
        await c.query(`insert into order_intake.customer_notice_events (notice_id, event, actor) values ($1, 'created', 'tick')`, [id]);
        await c.query('commit');
        return one(`select ${NOTICE_SELECT} where n.notice_id = $1`, [id]);
      } catch (err) {
        await c.query('rollback'); throw err;
      } finally { c.release(); }
    },

    async listNewlyDelivered() {
      const { rows } = await pool.query(
        `select om.mirror_id, om.lw_task_id::text as lw_task_id, om.lw_status, om.lw_completed_at, om.lw_photo_url,
                om.wp_order_id, c.wa_phone, c.shopify_customer_id
           from private_core.orders_mirror om
           join lateral (select wa_phone, shopify_customer_id from order_intake.customer_notices
                          where mirror_id = om.mirror_id and kind in ('confirmed_full','confirmed_partial')
                          order by created_at desc limit 1) c on true
          where om.lw_status = any($1::text[]) and om.updated_at > now() - interval '7 days'
            and not exists (select 1 from order_intake.customer_notices d where d.mirror_id = om.mirror_id and d.kind = 'delivered')`,
        [[...TERMINAL_SUCCESS]]);
      return rows.map((r) => ({ ...r, lw_completed_at: r.lw_completed_at ? new Date(r.lw_completed_at).toISOString() : null }));
    },

    async listNewlyCredited() {
      const { rows } = await pool.query(
        `select ct.credit_task_id, ct.mirror_id, ct.wp_order_id, ct.item_id, coalesce(i.item_name, ct.item_id) as item_label,
                ct.gi_document_id, c.wa_phone, c.shopify_customer_id
           from private_core.credit_tasks ct
           join lateral (select wa_phone, shopify_customer_id from order_intake.customer_notices
                          where mirror_id = ct.mirror_id and kind in ('confirmed_full','confirmed_partial')
                          order by created_at desc limit 1) c on true
           left join private_core.items i on i.item_id = ct.item_id
          where ct.status = 'CREDITED' and ct.gi_document_id is not null and ct.closed_at > now() - interval '30 days'
            and not exists (select 1 from order_intake.customer_notices d where d.credit_task_id = ct.credit_task_id)`);
      return rows;
    },

    async listConfirmedThenCancelled() {
      const { rows } = await pool.query(
        `select n.notice_id, n.wa_phone, n.shopify_order_name, om.lw_status
           from order_intake.customer_notices n
           join private_core.orders_mirror om on om.mirror_id = n.mirror_id
          where n.kind in ('confirmed_full','confirmed_partial') and n.state in ('sent','delivered','read')
            and om.lw_status = any($1::text[])
            and not exists (select 1 from order_intake.customer_notice_events e
                             where e.notice_id = n.notice_id and e.event = 'staff_alerted_cancel')`,
        [[...TERMINAL_FAIL]]);
      return rows;
    },

    async appendEvent(noticeId, event, actor, meta) {
      await pool.query(
        `insert into order_intake.customer_notice_events (notice_id, event, actor, meta) values ($1,$2,$3,$4::jsonb)`,
        [noticeId, event, actor, meta === undefined ? null : JSON.stringify(meta)]);
    },

    async expireStale() {
      const { rowCount } = await pool.query(
        `update order_intake.customer_notices n set state = 'expired'
          where n.state = 'pending_approval'
            and exists (select 1 from private_core.orders_mirror om
                         where om.mirror_id = n.mirror_id and om.lw_status = any($1::text[])
                           and om.updated_at < now() - interval '12 hours')`,
        [TERMINAL_ALL]);
      return rowCount ?? 0;
    },

    async listSendable(nowIso) {
      return many(`select ${NOTICE_SELECT}
                    where n.state = 'approved' and (n.send_not_before is null or n.send_not_before <= $1::timestamptz)
                    order by n.created_at limit 50`, [nowIso]);
    },

    async markSent(id, waMessageId) {
      await pool.query(`update order_intake.customer_notices set state='sent', wa_message_id=$2, sent_at=now(), attempts=attempts+1, fail_code=null, fail_detail=null where notice_id=$1`, [id, waMessageId]);
      await this.appendEvent(id, 'sent', 'tick', { wa_message_id: waMessageId });
    },
    async markRetry(id, nextAtIso, code, detail) {
      await pool.query(`update order_intake.customer_notices set attempts=attempts+1, send_not_before=$2::timestamptz, fail_code=$3, fail_detail=$4 where notice_id=$1`, [id, nextAtIso, code, detail.slice(0, 500)]);
    },
    async markFailed(id, code, detail) {
      await pool.query(`update order_intake.customer_notices set state='failed', attempts=attempts+1, fail_code=$2, fail_detail=$3 where notice_id=$1`, [id, code, detail.slice(0, 500)]);
      await this.appendEvent(id, 'failed', 'tick', { code });
    },
    async markShadow(id) {
      await pool.query(`update order_intake.customer_notices set state='shadow' where notice_id=$1 and state='approved'`, [id]);
      await this.appendEvent(id, 'shadow', 'tick');
    },

    async findByWaMessageId(waMessageId) {
      return one(`select ${NOTICE_SELECT} where n.wa_message_id = $1`, [waMessageId]);
    },
    async applyStatus(id, status, errorCode) {
      if (status === 'delivered') await pool.query(`update order_intake.customer_notices set state='delivered', delivered_at=coalesce(delivered_at, now()) where notice_id=$1 and state in ('sent')`, [id]);
      else if (status === 'read') await pool.query(`update order_intake.customer_notices set state='read', read_at=coalesce(read_at, now()), delivered_at=coalesce(delivered_at, now()) where notice_id=$1 and state in ('sent','delivered')`, [id]);
      else if (status === 'failed') await pool.query(`update order_intake.customer_notices set state='failed', fail_code=$2 where notice_id=$1 and state in ('sent','delivered')`, [id, errorCode == null ? 'status_failed' : String(errorCode)]);
      await this.appendEvent(id, `status_${status}`, 'webhook', errorCode == null ? undefined : { code: errorCode });
    },

    async latestNoticeForPhone(phone, kinds, sinceHours) {
      return one(`select ${NOTICE_SELECT}
                   where n.wa_phone = $1 and n.kind = any($2::text[]) and n.state in ('sent','delivered','read')
                     and n.sent_at > now() - make_interval(hours => $3)
                   order by n.sent_at desc limit 1`, [phone, kinds, sinceHours]);
    },
    async getNotice(id) { return one(`select ${NOTICE_SELECT} where n.notice_id = $1`, [id]); },
    async listPending() { return many(`select ${NOTICE_SELECT} where n.state = 'pending_approval' order by n.created_at`, []); },

    async approve(id, patch, actor) {
      const c = await pool.connect();
      try {
        await c.query('begin');
        const before = await c.query(`select state, delivery_date::text as delivery_date from order_intake.customer_notices where notice_id=$1 for update`, [id]);
        if (!before.rows[0] || before.rows[0].state !== 'pending_approval') { await c.query('rollback'); return null; }
        await c.query(
          `update order_intake.customer_notices
              set state='approved', delivery_date=$2::date, template_name=$3, template_params=$4::jsonb,
                  send_not_before=$5::timestamptz, approved_by=$6::uuid, approved_at=now()
            where notice_id=$1`,
          [id, patch.delivery_date, patch.template_name, JSON.stringify(patch.template_params), patch.send_not_before, actor.user_id]);
        for (const l of patch.lines) {
          await c.query(
            `update order_intake.customer_notice_lines set qty_delivering=$3, resolution=$4, substitute_label=$5
              where notice_id=$1 and item_label=$2`,
            [id, l.item_label, l.qty_delivering, l.resolution, l.substitute_label]);
        }
        await insertChangeLog(c, actor, 'CUSTOMER_NOTICE_APPROVED', id, before.rows[0], { state: 'approved', delivery_date: patch.delivery_date });
        await c.query(`insert into order_intake.customer_notice_events (notice_id, event, actor, meta) values ($1,'approved',$2,$3::jsonb)`,
          [id, actor.display_name, JSON.stringify({ lines: patch.lines })]);
        await c.query('commit');
      } catch (err) { await c.query('rollback'); throw err; } finally { c.release(); }
      return this.getNotice(id);
    },

    async suppress(id, reason, actor) {
      const c = await pool.connect();
      try {
        await c.query('begin');
        const before = await c.query(`select state from order_intake.customer_notices where notice_id=$1 for update`, [id]);
        if (!before.rows[0] || before.rows[0].state !== 'pending_approval') { await c.query('rollback'); return null; }
        await c.query(`update order_intake.customer_notices set state='suppressed', suppress_reason=$2, approved_by=$3::uuid, approved_at=now() where notice_id=$1`, [id, reason, actor.user_id]);
        await insertChangeLog(c, actor, 'CUSTOMER_NOTICE_SUPPRESSED', id, before.rows[0], { state: 'suppressed', reason });
        await c.query(`insert into order_intake.customer_notice_events (notice_id, event, actor, meta) values ($1,'suppressed',$2,$3::jsonb)`, [id, actor.display_name, JSON.stringify({ reason })]);
        await c.query('commit');
      } catch (err) { await c.query('rollback'); throw err; } finally { c.release(); }
      return this.getNotice(id);
    },
  };
}
```

- [ ] **Step 4: Run** — `npx vitest run api/src/order-intake/notices` → fake_store test passes; `npm run typecheck` clean.

- [ ] **Step 5: Commit**

```bash
git add api/src/order-intake/notices/store.ts api/src/order-intake/notices/__tests__/fake_store.ts api/src/order-intake/notices/__tests__/fake_store.test.ts
git commit -m "feat(notices): pg NoticeStore over order_intake.customer_notices + in-memory fake"
```

---

### Task 8: `notices/decide.ts` — pure decisions

**Files:**
- Create: `api/src/order-intake/notices/decide.ts`
- Test: `api/src/order-intake/notices/__tests__/decide.test.ts`

**Interfaces:**
- Consumes: `TaskShow`, `NoticeFlags`, `NoticeKind` (Task 2).
- Produces: `decideFromObservation(show): { kind: 'confirmed_full' | 'confirmed_partial'; state: 'approved' | 'pending_approval' } | null`; `canSend(flags, kind, phone): boolean`; `isPermanentSendError(code: number | null): boolean`; `PERMANENT_META_CODES`.

- [ ] **Step 1: Write the failing test**

```ts
import { describe, it, expect } from 'vitest';
import { decideFromObservation, canSend, isPermanentSendError } from '../decide.js';

const show = (pick_status: string | null, pickup_at: string | null = '2026-09-10T00:00:00.000+03:00') => ({ status: 'ASSIGNED', pick_status, pickup_at, photo_url: null });

describe('decideFromObservation', () => {
  it('PICKED + pickup_at → full/approved', () => expect(decideFromObservation(show('PICKED'))).toEqual({ kind: 'confirmed_full', state: 'approved' }));
  it('PICKED without pickup_at → partial/pending (human sets the day)', () => expect(decideFromObservation(show('PICKED', null))).toEqual({ kind: 'confirmed_partial', state: 'pending_approval' }));
  it('PARTIALLY_PICKED → partial/pending', () => expect(decideFromObservation(show('PARTIALLY_PICKED'))).toEqual({ kind: 'confirmed_partial', state: 'pending_approval' }));
  it('NEW / null / unknown → nothing', () => {
    expect(decideFromObservation(show('NEW'))).toBeNull();
    expect(decideFromObservation(show(null))).toBeNull();
    expect(decideFromObservation(show('WHATEVER'))).toBeNull();
  });
});

describe('canSend', () => {
  const base = { masterEnabled: true, live: true, allowlist: '*' as const, kinds: ['confirmed_full' as const] };
  it('requires master + live + kind + allowlist', () => {
    expect(canSend(base, 'confirmed_full', '9725')).toBe(true);
    expect(canSend({ ...base, masterEnabled: false }, 'confirmed_full', '9725')).toBe(false);
    expect(canSend({ ...base, live: false }, 'confirmed_full', '9725')).toBe(false);
    expect(canSend(base, 'delivered', '9725')).toBe(false);
    expect(canSend({ ...base, allowlist: ['9720'] }, 'confirmed_full', '9725')).toBe(false);
    expect(canSend({ ...base, allowlist: ['9725'] }, 'confirmed_full', '9725')).toBe(true);
  });
});

describe('isPermanentSendError', () => {
  it('knows the Meta codes that must not be retried', () => {
    expect(isPermanentSendError(131049)).toBe(true);   // marketing frequency cap
    expect(isPermanentSendError(131026)).toBe(true);   // not a WhatsApp user / undeliverable
    expect(isPermanentSendError(132001)).toBe(true);   // template does not exist
    expect(isPermanentSendError(131047)).toBe(true);   // re-engagement / 24h window (only for non-template)
    expect(isPermanentSendError(130429)).toBe(false);  // rate limit → retry
    expect(isPermanentSendError(null)).toBe(false);
  });
});
```

- [ ] **Step 2: Run to verify it fails.**

- [ ] **Step 3: Write `decide.ts`**

```ts
// Pure decisions for the notices tick. No I/O.
import type { TaskShow, NoticeFlags, NoticeKind } from './types.js';

export type ObservationDecision = { kind: 'confirmed_full' | 'confirmed_partial'; state: 'approved' | 'pending_approval' } | null;

// LionWheel task-level pick_status (the only pick signal since 2026-08-13..16):
//   PICKED            → every line ships at ordered qty → automatic, if we know the day.
//   PARTIALLY_PICKED  → short, but the API no longer says which lines → a human decides.
//   anything else     → not ready; keep observing.
export function decideFromObservation(show: TaskShow): ObservationDecision {
  const ps = (show.pick_status ?? '').toUpperCase();
  if (ps === 'PICKED') {
    return show.pickup_at ? { kind: 'confirmed_full', state: 'approved' } : { kind: 'confirmed_partial', state: 'pending_approval' };
  }
  if (ps === 'PARTIALLY_PICKED') return { kind: 'confirmed_partial', state: 'pending_approval' };
  return null;
}

export function canSend(flags: NoticeFlags, kind: NoticeKind, phone: string): boolean {
  if (!flags.masterEnabled || !flags.live) return false;
  if (!flags.kinds.includes(kind)) return false;
  return flags.allowlist === '*' || flags.allowlist.includes(phone);
}

// Meta error codes where a retry cannot succeed. Everything else (5xx, 429,
// 130429 rate limit, network) is retried with backoff up to MAX_ATTEMPTS.
export const PERMANENT_META_CODES = new Set([131049, 131026, 131047, 131051, 132000, 132001, 132005, 132007, 132012, 132015, 132016, 133010]);

export function isPermanentSendError(code: number | null): boolean {
  return code != null && PERMANENT_META_CODES.has(code);
}

export const MAX_ATTEMPTS = 3;
export const RETRY_BACKOFF_MINUTES = [5, 15, 30];
```

- [ ] **Step 4: Run to verify it passes** — 6 passed.

- [ ] **Step 5: Commit**

```bash
git add api/src/order-intake/notices/decide.ts api/src/order-intake/notices/__tests__/decide.test.ts
git commit -m "feat(notices): pure observation and send-gate decisions"
```

---

### Task 9: `notices/tick.ts` — the orchestrator

**Files:**
- Create: `api/src/order-intake/notices/tick.ts`
- Test: `api/src/order-intake/notices/__tests__/tick.test.ts`

**Interfaces:**
- Consumes: `NoticeStore` (Task 7), `LwShowFn` (Task 5), `OrderCustomerLookup` (Task 6), `WhatsAppPort.sendTemplate` + `WhatsAppSendError` (Task 4), `decideFromObservation`/`canSend`/`isPermanentSendError`/`MAX_ATTEMPTS`/`RETRY_BACKOFF_MINUTES` (Task 8), `buildConfirmedTemplate`/`buildDeliveredTemplate`/`buildCreditTemplate`/`TEMPLATE_LANG` (Task 3), `sendNotBefore`/`ilDate` (Task 2), `AlertPort` (existing `alert.ts`; kinds extended in Task 14 — until then pass `kind` as `any` in this task's test only if the type complains, and remove the cast in Task 14).
- Produces: `interface TickDeps { store; lwShow; orderCustomer; whatsapp; alert?; now?; observeWindowDays? }`, `interface TickResult`, `runNoticesTick(deps): Promise<TickResult>`.

- [ ] **Step 1: Write the failing tests**

```ts
import { describe, it, expect } from 'vitest';
import { runNoticesTick, type TickDeps } from '../tick.js';
import { fakeStore } from './fake_store.js';
import { WhatsAppSendError, type WhatsAppPort } from '../../whatsapp/send.js';
import type { OpenTask, TaskShow } from '../types.js';

const NOW = new Date('2026-09-09T12:00:00Z'); // Wed 15:00 IDT
const task: OpenTask = {
  mirror_id: 'm1', lw_task_id: '27818514', wp_order_id: '#GT14512', lw_status: 'ASSIGNED', recipient_name: 'קפה גן סיפור', created_at: '2026-09-09T09:45:00Z',
  lines: [{ line_mirror_id: 'l1', item_id: 'DETOX-1L', lw_sku: 'GT-LUI-LOW-1L', lw_name: 'DETOX 1000ml', qty_ordered: 12 }, { line_mirror_id: 'l2', item_id: 'FRESH-1L', lw_sku: 'GT-HIB-LOW-1L', lw_name: 'FRESH 1000ml', qty_ordered: 6 }],
};
function whatsapp(fail?: WhatsAppSendError) {
  const sent: Array<{ to: string; tpl: any }> = [];
  const port = {
    async sendTemplate(to: string, tpl: any) { if (fail) throw fail; sent.push({ to, tpl }); return { messageId: `wamid.${sent.length}` }; },
    async sendText() { return { messageId: null }; }, async sendButtons() { return { messageId: null }; }, async send() { return { messageId: null }; },
  } as unknown as WhatsAppPort;
  return { port, sent };
}
function deps(over: Partial<TickDeps> & { show?: TaskShow | null; storeInit?: Parameters<typeof fakeStore>[0] }) {
  const fs = fakeStore({ openTasks: [task], phones: { '7123': { wa_phone: '972500000001', notices_enabled: true } }, now: () => NOW, ...over.storeInit });
  const wa = whatsapp();
  const d: TickDeps = {
    store: fs.store, lwShow: async () => over.show ?? null, orderCustomer: async () => '7123', whatsapp: wa.port, now: () => NOW,
    alert: { send: async () => {} }, ...over,
  };
  return { d, fs, wa };
}

describe('observe → notice', () => {
  it('PICKED + pickup_at → confirmed_full approved with rendered params, and an observation row', async () => {
    const { d, fs } = deps({ show: { status: 'ASSIGNED', pick_status: 'PICKED', pickup_at: '2026-09-10T00:00:00.000+03:00', photo_url: null } });
    const r = await runNoticesTick(d);
    expect(r.observed).toBe(1);
    expect(fs.observations[0]).toMatchObject({ mirror_id: 'm1', pick_status: 'PICKED' });
    const n = [...fs.notices.values()][0];
    expect(n).toMatchObject({ kind: 'confirmed_full', state: 'shadow', wa_phone: '972500000001', dedupe_key: 'confirmed:m1', delivery_date: '2026-09-10', template_name: 'gt_order_confirmed_full_v1' });
    expect(n.template_params).toEqual(['מחר, יום חמישי 10.9', 'DETOX 1000ml ×12 · FRESH 1000ml ×6']);
    expect(n.lines.map((l) => l.qty_delivering)).toEqual([12, 6]);
  });

  it('PARTIALLY_PICKED → confirmed_partial pending_approval, no template yet, nothing sent', async () => {
    const { d, fs, wa } = deps({ show: { status: 'ASSIGNED', pick_status: 'PARTIALLY_PICKED', pickup_at: null, photo_url: null } });
    const r = await runNoticesTick(d);
    expect(r.created.confirmed_partial).toBe(1);
    expect([...fs.notices.values()][0]).toMatchObject({ state: 'pending_approval', template_name: null, delivery_date: null });
    expect(wa.sent).toHaveLength(0);
  });

  it('NEW → observation recorded, no notice; /show failure → counted, no notice', async () => {
    const a = deps({ show: { status: 'ASSIGNED', pick_status: 'NEW', pickup_at: null, photo_url: null } });
    expect((await runNoticesTick(a.d)).created).toEqual({});
    expect(a.fs.observations).toHaveLength(1);
    const b = deps({ show: null });
    expect((await runNoticesTick(b.d)).show_failed).toBe(1);
  });

  it('unmapped customer or notices_enabled=false → skipped', async () => {
    const a = deps({ show: { status: 'ASSIGNED', pick_status: 'PICKED', pickup_at: '2026-09-10T00:00:00.000+03:00', photo_url: null }, orderCustomer: async () => null });
    expect((await runNoticesTick(a.d)).skipped_unmapped).toBe(1);
    const b = deps({ show: { status: 'ASSIGNED', pick_status: 'PICKED', pickup_at: '2026-09-10T00:00:00.000+03:00', photo_url: null }, storeInit: { phones: { '7123': { wa_phone: '972500000001', notices_enabled: false } } } });
    expect((await runNoticesTick(b.d)).skipped_unmapped).toBe(1);
  });

  it('is idempotent: a second tick creates nothing new', async () => {
    const { d, fs } = deps({ show: { status: 'ASSIGNED', pick_status: 'PICKED', pickup_at: '2026-09-10T00:00:00.000+03:00', photo_url: null } });
    await runNoticesTick(d); await runNoticesTick(d);
    expect(fs.notices.size).toBe(1);
  });
});

describe('send gate', () => {
  const show: TaskShow = { status: 'ASSIGNED', pick_status: 'PICKED', pickup_at: '2026-09-10T00:00:00.000+03:00', photo_url: null };
  it('flags off → shadow; live + allowlist match → template sent with he language', async () => {
    const off = deps({ show });
    expect((await runNoticesTick(off.d)).shadow).toBe(1);
    const on = deps({ show, storeInit: { flags: { masterEnabled: true, live: true, allowlist: ['972500000001'], kinds: ['confirmed_full'] } } });
    const r = await runNoticesTick(on.d);
    expect(r.sent).toBe(1);
    expect(on.wa.sent[0]).toEqual({ to: '972500000001', tpl: { name: 'gt_order_confirmed_full_v1', language: 'he', bodyParams: ['מחר, יום חמישי 10.9', 'DETOX 1000ml ×12 · FRESH 1000ml ×6'], headerImageUrl: null } });
    expect([...on.fs.notices.values()][0]).toMatchObject({ state: 'sent', wa_message_id: 'wamid.1' });
  });

  it('quiet hours: created at 22:30 → send_not_before next 07:00, not sent now', async () => {
    const late = new Date('2026-09-09T19:30:00Z');
    const x = deps({ show, now: () => late, storeInit: { now: () => late, flags: { masterEnabled: true, live: true, allowlist: '*', kinds: ['confirmed_full'] } } });
    const r = await runNoticesTick(x.d);
    expect(r.sent).toBe(0);
    expect([...x.fs.notices.values()][0].send_not_before).toBe('2026-09-10T04:00:00.000Z');
  });

  it('permanent Meta error → failed + alert; transient → retry with backoff', async () => {
    const live = { flags: { masterEnabled: true, live: true, allowlist: '*' as const, kinds: ['confirmed_full' as const] } };
    const alerts: any[] = [];
    const perm = deps({ show, storeInit: live, whatsapp: whatsapp(new WhatsAppSendError(400, 131026, 'x')).port, alert: { send: async (a) => { alerts.push(a); } } });
    const r1 = await runNoticesTick(perm.d);
    expect(r1.failed).toBe(1);
    expect([...perm.fs.notices.values()][0].state).toBe('failed');
    expect(alerts[0].kind).toBe('notice_send_failed');
    const tmp = deps({ show, storeInit: live, whatsapp: whatsapp(new WhatsAppSendError(500, null, 'boom')).port });
    const r2 = await runNoticesTick(tmp.d);
    expect(r2.retried).toBe(1);
    expect([...tmp.fs.notices.values()][0]).toMatchObject({ state: 'approved', attempts: 1, send_not_before: '2026-09-09T12:05:00.000Z' });
  });
});

describe('delivered, credited, cancelled', () => {
  it('a completed task with a confirmed notice → delivered notice with photo header', async () => {
    const { d, fs } = deps({ show: { status: 'ASSIGNED', pick_status: 'PICKED', pickup_at: '2026-09-10T00:00:00.000+03:00', photo_url: null },
      storeInit: { delivered: [{ mirror_id: 'm1', lw_task_id: '27818514', lw_status: 'COMPLETED', lw_completed_at: '2026-09-09T08:20:00Z', lw_photo_url: 'https://x/pod.jpg', wp_order_id: '#GT14512', wa_phone: '972500000001', shopify_customer_id: '7123' }] } });
    await runNoticesTick(d);
    const del = [...fs.notices.values()].find((n) => n.kind === 'delivered')!;
    expect(del).toMatchObject({ dedupe_key: 'delivered:m1', template_name: 'gt_order_delivered_v1', header_image_url: 'https://x/pod.jpg', template_params: ['היום 11:20'] });
  });

  it('a CREDITED credit_task with a GI document → credit_issued notice', async () => {
    const { d, fs } = deps({ show: null, storeInit: { openTasks: [], credited: [{ credit_task_id: 'c1', mirror_id: 'm1', wp_order_id: '#GT14512', item_id: 'FRESH-1L', item_label: 'FRESH 1000ml', gi_document_id: 'gi-1', wa_phone: '972500000001', shopify_customer_id: '7123' }] } });
    await runNoticesTick(d);
    expect([...fs.notices.values()][0]).toMatchObject({ kind: 'credit_issued', dedupe_key: 'credit:c1', template_params: ['FRESH 1000ml', '#GT14512'] });
  });

  it('a cancelled task after a sent confirmation → one staff alert, once', async () => {
    const alerts: any[] = [];
    const { d } = deps({ show: null, storeInit: { openTasks: [], cancelled: [{ notice_id: 'n-9', wa_phone: '972500000001', shopify_order_name: '#GT14512', lw_status: 'CANCELED' }] }, alert: { send: async (a) => { alerts.push(a); } } });
    await runNoticesTick(d); await runNoticesTick(d);
    expect(alerts).toHaveLength(1);
    expect(alerts[0].kind).toBe('confirmed_then_changed');
  });
});
```

- [ ] **Step 2: Run to verify it fails.**

- [ ] **Step 3: Write `tick.ts`**

```ts
// The customer-notices tick. Runs every 15 minutes from pg_cron via the
// internal job route. Pure orchestration over injected ports — every branch
// here is covered by __tests__/tick.test.ts with fakes.
//
//   1. observe   open tasks → /tasks/show → observation row → confirmed_* notice
//   2. delivered terminal-success tasks with a confirmed notice → delivered notice
//   3. credited  CREDITED credit_tasks with a GI document → credit_issued notice
//   4. cancelled a sent confirmation whose task was cancelled → staff alert (once)
//   5. expire    pending approvals for tasks already terminal
//   6. send      approved rows past send_not_before → template, or shadow when flags say no

import type { NoticeStore } from './store.js';
import type { LwShowFn } from './lionwheel_show.js';
import type { OrderCustomerLookup } from './shopify_order.js';
import type { WhatsAppPort } from '../whatsapp/send.js';
import { WhatsAppSendError } from '../whatsapp/send.js';
import type { AlertPort } from '../alert.js';
import type { NoticeLine, NoticeRow, OpenTask, TaskShow } from './types.js';
import { decideFromObservation, canSend, isPermanentSendError, MAX_ATTEMPTS, RETRY_BACKOFF_MINUTES } from './decide.js';
import { buildConfirmedTemplate, buildDeliveredTemplate, buildCreditTemplate, TEMPLATE_LANG } from './render.js';
import { sendNotBefore, ilDate } from './time.js';

export interface TickDeps {
  store: NoticeStore;
  lwShow: LwShowFn;
  orderCustomer: OrderCustomerLookup;
  whatsapp: WhatsAppPort;
  alert?: AlertPort;
  now?: () => Date;
  observeWindowDays?: number;   // default 4
}

export interface TickResult {
  observed: number;
  show_failed: number;
  skipped_unmapped: number;
  created: Partial<Record<string, number>>;
  sent: number;
  shadow: number;
  retried: number;
  failed: number;
  expired: number;
  alerts: number;
  errors: string[];
}

function linesFromTask(task: OpenTask): NoticeLine[] {
  return task.lines.map((l) => ({
    item_label: l.lw_name || l.lw_sku, item_id: l.item_id, line_mirror_id: l.line_mirror_id,
    qty_ordered: l.qty_ordered, qty_delivering: l.qty_ordered, resolution: null, substitute_label: null,
  }));
}

export async function runNoticesTick(deps: TickDeps): Promise<TickResult> {
  const now = deps.now ? deps.now() : new Date();
  const nowIso = now.toISOString();
  const r: TickResult = { observed: 0, show_failed: 0, skipped_unmapped: 0, created: {}, sent: 0, shadow: 0, retried: 0, failed: 0, expired: 0, alerts: 0, errors: [] };
  const bump = (k: string) => { r.created[k] = (r.created[k] ?? 0) + 1; };
  const flags = await deps.store.getFlags();

  // 1. observe
  for (const task of await deps.store.listOpenTasks(deps.observeWindowDays ?? 4)) {
    try {
      const show: TaskShow | null = await deps.lwShow(task.lw_task_id);
      if (!show) { r.show_failed++; continue; }
      r.observed++;
      await deps.store.recordObservation({ ...show, mirror_id: task.mirror_id, lw_task_id: task.lw_task_id, observed_at: nowIso });
      const decision = decideFromObservation(show);
      if (!decision) continue;
      const customerId = task.wp_order_id ? await deps.orderCustomer(task.wp_order_id) : null;
      const mapped = customerId ? await deps.store.resolvePhoneByShopifyCustomerId(customerId) : null;
      if (!mapped || !mapped.notices_enabled) { r.skipped_unmapped++; continue; }
      const lines = linesFromTask(task);
      const deliveryDate = show.pickup_at ? ilDate(show.pickup_at) : null;
      const tpl = decision.kind === 'confirmed_full' && deliveryDate ? buildConfirmedTemplate(lines, deliveryDate, now) : null;
      const created = await deps.store.createNotice({
        kind: decision.kind, state: decision.state, wa_phone: mapped.wa_phone, shopify_customer_id: customerId,
        shopify_order_name: task.wp_order_id, mirror_id: task.mirror_id, lw_task_id: task.lw_task_id,
        dedupe_key: `confirmed:${task.mirror_id}`, template_name: tpl?.template_name ?? null, template_params: tpl?.params ?? [],
        header_image_url: null, delivery_date: deliveryDate, send_not_before: sendNotBefore(now).toISOString(), lines,
      });
      if (created) bump(decision.kind);
    } catch (err) { r.errors.push(`observe ${task.lw_task_id}: ${(err as Error).message}`); }
  }

  // 2. delivered
  for (const d of await deps.store.listNewlyDelivered()) {
    try {
      const tpl = buildDeliveredTemplate(d.lw_completed_at, now, d.lw_photo_url);
      const created = await deps.store.createNotice({
        kind: 'delivered', state: 'approved', wa_phone: d.wa_phone, shopify_customer_id: d.shopify_customer_id, shopify_order_name: d.wp_order_id,
        mirror_id: d.mirror_id, lw_task_id: d.lw_task_id, dedupe_key: `delivered:${d.mirror_id}`, template_name: tpl.template_name,
        template_params: tpl.params, header_image_url: tpl.header_image_url, delivery_date: d.lw_completed_at ? ilDate(d.lw_completed_at) : null,
        send_not_before: sendNotBefore(now).toISOString(), lines: [],
      });
      if (created) bump('delivered');
    } catch (err) { r.errors.push(`delivered ${d.lw_task_id}: ${(err as Error).message}`); }
  }

  // 3. credited
  for (const c of await deps.store.listNewlyCredited()) {
    try {
      const tpl = buildCreditTemplate(c.item_label, c.wp_order_id);
      const created = await deps.store.createNotice({
        kind: 'credit_issued', state: 'approved', wa_phone: c.wa_phone, shopify_customer_id: c.shopify_customer_id, shopify_order_name: c.wp_order_id,
        mirror_id: c.mirror_id, lw_task_id: null, credit_task_id: c.credit_task_id, dedupe_key: `credit:${c.credit_task_id}`,
        template_name: tpl.template_name, template_params: tpl.params, header_image_url: null, delivery_date: null,
        send_not_before: sendNotBefore(now).toISOString(), lines: [],
      });
      if (created) bump('credit_issued');
    } catch (err) { r.errors.push(`credited ${c.credit_task_id}: ${(err as Error).message}`); }
  }

  // 4. cancelled after a sent confirmation → one staff alert
  for (const c of await deps.store.listConfirmedThenCancelled()) {
    await deps.alert?.send({ kind: 'confirmed_then_changed', customer: { display_name: null, wa_phone: c.wa_phone }, notice_id: c.notice_id, order_name: c.shopify_order_name, error: `LionWheel status ${c.lw_status} after the confirmation was sent` });
    await deps.store.appendEvent(c.notice_id, 'staff_alerted_cancel', 'tick', { lw_status: c.lw_status });
    r.alerts++;
  }

  // 5. expire
  r.expired = await deps.store.expireStale();

  // 6. send
  for (const n of await deps.store.listSendable(nowIso)) {
    if (!n.template_name) { r.errors.push(`send ${n.notice_id}: approved without template`); continue; }
    if (!canSend(flags, n.kind, n.wa_phone)) { await deps.store.markShadow(n.notice_id); r.shadow++; continue; }
    try {
      const res = await deps.whatsapp.sendTemplate(n.wa_phone, { name: n.template_name, language: TEMPLATE_LANG, bodyParams: n.template_params, headerImageUrl: n.header_image_url });
      await deps.store.markSent(n.notice_id, res.messageId);
      r.sent++;
    } catch (err) {
      const e = err as WhatsAppSendError;
      const code = e instanceof WhatsAppSendError ? e.code : null;
      const attempt = n.attempts + 1;
      if (isPermanentSendError(code) || attempt >= MAX_ATTEMPTS) {
        await deps.store.markFailed(n.notice_id, code == null ? 'send_error' : String(code), e.message);
        await deps.alert?.send({ kind: 'notice_send_failed', customer: { display_name: null, wa_phone: n.wa_phone }, notice_id: n.notice_id, order_name: n.shopify_order_name, error: e.message });
        r.failed++; r.alerts++;
      } else {
        const minutes = RETRY_BACKOFF_MINUTES[Math.min(attempt - 1, RETRY_BACKOFF_MINUTES.length - 1)];
        await deps.store.markRetry(n.notice_id, new Date(now.getTime() + minutes * 60_000).toISOString(), code == null ? 'send_error' : String(code), e.message);
        r.retried++;
      }
    }
  }
  return r;
}

export type { NoticeRow };
```

- [ ] **Step 4: Run to verify it passes** — `npx vitest run api/src/order-intake/notices` → 12 tick tests pass (if the `alert.send` kind types fail typecheck before Task 14, cast the alert objects `as any` in tick.ts with a `// removed in Task 14` comment; Task 14 removes it).

- [ ] **Step 5: Commit**

```bash
git add api/src/order-intake/notices/tick.ts api/src/order-intake/notices/__tests__/tick.test.ts
git commit -m "feat(notices): tick — observe picks, create notices, send or shadow"
```

---

### Task 10: status receipts and customer replies → the notices module

**Files:**
- Modify: `api/src/order-intake/types.ts` (`NormalizedStatus.error_code`)
- Modify: `api/src/order-intake/webhook.ts` (capture `statuses[].errors[0].code`)
- Modify: `api/src/order-intake/worker.ts` (status → `applyStatus`; template button taps; free text after a notice → hand to human + alert; status idempotency key)
- Test: `api/src/order-intake/__tests__/worker.test.ts` (append cases), `api/src/order-intake/__tests__/webhook.test.ts` (append one case)

**Interfaces:**
- Consumes: `NoticeStore.findByWaMessageId/applyStatus/latestNoticeForPhone/appendEvent` (Task 7).
- Produces: `WorkerDeps.notices?: Pick<NoticeStore, 'findByWaMessageId' | 'applyStatus' | 'latestNoticeForPhone' | 'appendEvent'>`; new `WorkerAction`s `'notice_status' | 'notice_button' | 'handed_to_human'`.

- [ ] **Step 1: Write the failing tests** — append to `webhook.test.ts`:

```ts
it('carries the Meta error code on a failed status', () => {
  const ev = normalizeWebhook({ entry: [{ changes: [{ value: { metadata: { phone_number_id: 'PNID' }, statuses: [{ id: 'wamid.S1', status: 'failed', recipient_id: '972500000001', errors: [{ code: 131026, title: 'undeliverable' }] }] } }] }] });
  expect(ev[0]).toEqual({ kind: 'status', wa_message_id: 'wamid.S1', status: 'failed', recipient: '972500000001', error_code: 131026 });
});
```

Append to `worker.test.ts` (reuse its `memStore`, `catalogPort`, and the existing `run`/`deps` helpers exactly as the other cases do; the fake below is the notices port):

```ts
function fakeNotices(rows: any[] = []) {
  const applied: any[] = []; const events: any[] = [];
  return {
    applied, events,
    port: {
      async findByWaMessageId(id: string) { return rows.find((r) => r.wa_message_id === id) ?? null; },
      async applyStatus(id: string, status: string, code?: number | null) { applied.push({ id, status, code }); },
      async latestNoticeForPhone(phone: string, kinds: string[]) { return rows.find((r) => r.wa_phone === phone && kinds.includes(r.kind)) ?? null; },
      async appendEvent(id: string, event: string, actor: string | null, meta?: unknown) { events.push({ id, event, actor, meta }); },
    },
  };
}

describe('notices integration', () => {
  it('a delivery/read status for a notice message updates the notice; unknown ids stay ignored', async () => {
    const n = fakeNotices([{ notice_id: 'n1', wa_message_id: 'wamid.T1', wa_phone: '972500000001', kind: 'confirmed_full' }]);
    const { store } = memStore([CUSTOMER]);
    const d = deps({ store, notices: n.port });
    const statuses = (id: string, status: string) => normalizeWebhook({ entry: [{ changes: [{ value: { metadata: { phone_number_id: 'PNID' }, statuses: [{ id, status, recipient_id: '972500000001' }] }] }] });
    const r1 = await runPipeline(statuses('wamid.T1', 'delivered'), d);
    const r2 = await runPipeline(statuses('wamid.T1', 'read'), d);      // same message id, different status → not a duplicate
    const r3 = await runPipeline(statuses('wamid.ZZ', 'delivered'), d);
    expect(r1[0].action).toBe('notice_status'); expect(r2[0].action).toBe('notice_status'); expect(r3[0].action).toBe('ignored_status');
    expect(n.applied).toEqual([{ id: 'n1', status: 'delivered', code: undefined }, { id: 'n1', status: 'read', code: undefined }]);
  });

  it('a template quick-reply tap is logged on the latest confirmed notice; "wants_call" alerts', async () => {
    const n = fakeNotices([{ notice_id: 'n1', wa_message_id: 'wamid.T1', wa_phone: '972500000001', kind: 'confirmed_partial' }]);
    const alerts: any[] = [];
    const { store } = memStore([CUSTOMER]);
    const d = deps({ store, notices: n.port, alert: { send: async (a: any) => { alerts.push(a); } } });
    const tap = (payload: string) => normalizeWebhook({ entry: [{ changes: [{ value: { metadata: { phone_number_id: 'PNID' }, messages: [{ from: '972500000001', id: `wamid.${payload}`, type: 'button', button: { payload, text: 'x' } }] } }] }] });
    expect((await runPipeline(tap('ack'), d))[0].action).toBe('notice_button');
    expect((await runPipeline(tap('wants_call'), d))[0].action).toBe('notice_button');
    expect(n.events.map((e) => e.event)).toEqual(['button_ack', 'button_wants_call']);
    expect(alerts.map((a) => a.kind)).toEqual(['wants_call']);
    expect(sentTexts(d)).toHaveLength(0); // no catalog nudge for a button tap on a notice
  });

  it('free text within 24h of a sent notice is handed to a human (no nudge) and alerts once', async () => {
    const n = fakeNotices([{ notice_id: 'n1', wa_message_id: 'wamid.T1', wa_phone: '972500000001', kind: 'delivered' }]);
    const alerts: any[] = [];
    const { store } = memStore([CUSTOMER]);
    const d = deps({ store, notices: n.port, alert: { send: async (a: any) => { alerts.push(a); } } });
    const r = await runPipeline(text('חסר לי קרטון'), d);
    expect(r[0].action).toBe('handed_to_human');
    expect(alerts[0]).toMatchObject({ kind: 'customer_reply_after_notice', notice_id: 'n1' });
    expect(sentTexts(d)).toHaveLength(0);
    const r2 = await runPipeline(text('הלו?', 'wamid.X2'), d);
    expect(r2[0].action).toBe('deferred_human');
  });
});
```

(`CUSTOMER`, `text(body, id?)`, `sentTexts(deps)`, `deps(overrides)` are the helpers already used by `worker.test.ts`; if a name differs there, use that file's existing helper — do not add a second copy.)

- [ ] **Step 2: Run to verify it fails.**

- [ ] **Step 3: Implement**

`types.ts` — in `NormalizedStatus` add `error_code?: number | null;`.

`webhook.ts` — replace the statuses loop body with:

```ts
      for (const s of statuses) {
        const code = Array.isArray(s?.errors) && s.errors[0]?.code != null ? Number(s.errors[0].code) : undefined;
        out.push({ kind: 'status', wa_message_id: s?.id, status: s?.status ?? 'unknown', recipient: normalizePhone(s?.recipient_id), ...(code !== undefined ? { error_code: code } : {}) });
      }
```

`worker.ts`:

1. Extend `WorkerAction` with `| 'notice_status' | 'notice_button' | 'handed_to_human'`.
2. Add to `WorkerDeps`:
```ts
  // The notices module (status receipts, template button taps, replies to a
  // notice). Optional: absent => statuses are ignored as before.
  notices?: Pick<NoticeStore, 'findByWaMessageId' | 'applyStatus' | 'latestNoticeForPhone' | 'appendEvent'>;
```
with `import type { NoticeStore } from './notices/store.js';` and `import { createPgNoticeStore } from './notices/store.js';`.
3. Replace `if (ev.kind === 'status') return { action: 'ignored_status' };` in `handleEvent` with:
```ts
  if (ev.kind === 'status') return handleStatus(ev, deps);
```
and add:
```ts
const NOTICE_REPLY_WINDOW_HOURS = 24;
const NOTICE_HANDOFF_MS = 24 * 60 * 60 * 1000;
const NOTICE_KINDS_WITH_REPLY = ['confirmed_full', 'confirmed_partial', 'delivered', 'credit_issued'] as const;

async function handleStatus(ev: NormalizedStatus, deps: WorkerDeps): Promise<WorkerResult> {
  if (!deps.notices || !ev.wa_message_id) return { action: 'ignored_status' };
  const s = ev.status;
  if (s !== 'sent' && s !== 'delivered' && s !== 'read' && s !== 'failed') return { action: 'ignored_status' };
  const notice = await deps.notices.findByWaMessageId(ev.wa_message_id);
  if (!notice) return { action: 'ignored_status' };
  await deps.notices.applyStatus(notice.notice_id, s, ev.error_code);
  return { action: 'notice_status', detail: { notice_id: notice.notice_id, status: s } };
}
```
(import `NormalizedStatus` from `./types.js`.)
4. In `handleMessage`, right after the `if (ev.content.type === 'order') …` line, before `const session = …`, add:
```ts
  // A reply to one of our notices belongs to a human, not to the catalog nudge.
  if (deps.notices) {
    const latest = await deps.notices.latestNoticeForPhone(phone, [...NOTICE_KINDS_WITH_REPLY], NOTICE_REPLY_WINDOW_HOURS);
    if (latest && ev.content.type === 'interactive' && (ev.content.button_id === 'ack' || ev.content.button_id === 'wants_call')) {
      await deps.notices.appendEvent(latest.notice_id, `button_${ev.content.button_id}`, 'customer');
      if (ev.content.button_id === 'wants_call') {
        await deps.alert?.send({ kind: 'wants_call', customer: { display_name: customer.display_name, wa_phone: phone }, notice_id: latest.notice_id, order_name: latest.shopify_order_name, error: 'customer tapped "רוצה לדבר"' });
      }
      return { action: 'notice_button', detail: { notice_id: latest.notice_id, button: ev.content.button_id } };
    }
    if (latest && ev.content.type === 'text' && ev.content.text.trim()) {
      const active = await deps.store.getActiveSession(customer.id);
      if (!active?.human_handled) {
        const t = nowDate(deps);
        const patch: Partial<SessionRow> = { state: 'handed_off', human_handled: true, human_handled_at: t.toISOString(), expires_at: new Date(t.getTime() + NOTICE_HANDOFF_MS).toISOString() };
        if (active) await deps.store.updateSession(active.id, patch); else await deps.store.createSession(customer.id, patch);
        await deps.notices.appendEvent(latest.notice_id, 'customer_reply', 'customer', { text: ev.content.text.slice(0, 500) });
        await deps.alert?.send({ kind: 'customer_reply_after_notice', customer: { display_name: customer.display_name, wa_phone: phone }, notice_id: latest.notice_id, order_name: latest.shopify_order_name, error: ev.content.text.slice(0, 300) });
        return { action: 'handed_to_human', detail: { notice_id: latest.notice_id } };
      }
    }
  }
```
5. In `runPipeline`, change the id line so statuses dedupe per (message, status):
```ts
    const waId = ev.kind === 'status' ? (ev.wa_message_id ? `${ev.wa_message_id}:${ev.status}` : null) : ev.wa_message_id;
```
6. In `buildLiveDeps`, add `notices: createPgNoticeStore(pool, { masterEnabled: config.notices.masterEnabled }),` (the `config.notices` field arrives in Task 11; until then use `{ masterEnabled: false }` with a `// wired in Task 11` comment).

- [ ] **Step 4: Run** — `npx vitest run api/src/order-intake` → all green (existing 23 worker tests unchanged; 3 new + 1 webhook).

- [ ] **Step 5: Commit**

```bash
git add api/src/order-intake/types.ts api/src/order-intake/webhook.ts api/src/order-intake/worker.ts api/src/order-intake/__tests__/worker.test.ts api/src/order-intake/__tests__/webhook.test.ts
git commit -m "feat(notices): status receipts, template button taps and replies routed to the notices module"
```

---

### Task 11: config, pool, tick route, health, server registration

**Files:**
- Modify: `api/src/order-intake/config.ts`
- Create: `api/src/order-intake/notices/pool.ts`
- Create: `api/src/order-intake/notices/routes.ts` (tick + health here; list/approve/suppress added in Task 12)
- Modify: `api/src/order-intake/route.ts` (health gains `notices_master_enabled`)
- Modify: `api/src/server.ts`
- Modify: `api/src/order-intake/__tests__/route.test.ts` (config fixtures)
- Test: `api/src/order-intake/notices/__tests__/routes.test.ts`

**Interfaces:**
- Produces: `OrderIntakeConfig.notices: { masterEnabled: boolean; lionwheelBaseUrl: string; lionwheelApiKey: string; observeWindowDays: number }`, `OrderIntakeConfig.alerts: { emailTo: string[]; emailFrom: string; resendApiKey: string }`; `getNoticesPool(config)`; `registerCustomerNoticesRoutes(app, opts)`; routes `POST /api/v1/internal/jobs/customer-notices-tick` and `GET /api/v1/internal/jobs/customer-notices-health` (both bearer `JOB_RUNNER_TOKEN`).

- [ ] **Step 1: Write the failing route test**

```ts
import { describe, it, expect } from 'vitest';
import Fastify from 'fastify';
import { registerCustomerNoticesRoutes } from '../routes.js';
import { fakeStore } from './fake_store.js';
import type { TickDeps } from '../tick.js';

function app(tickDeps: Partial<TickDeps> = {}) {
  const fs = fakeStore();
  const f = Fastify();
  registerCustomerNoticesRoutes(f, {
    jobToken: 'JOBTOK',
    store: fs.store,
    tickDeps: { store: fs.store, lwShow: async () => null, orderCustomer: async () => null, whatsapp: {} as any, ...tickDeps },
    extractSession: async () => ({ user_id: '00000000-0000-0000-0000-000000000001', email: 't@x', role: 'admin', display_name: 'Tom' }),
  });
  return { f, fs };
}

describe('tick route', () => {
  it('401 without the job token; 200 with a TickResult', async () => {
    const { f } = app();
    await f.ready();
    expect((await f.inject({ method: 'POST', url: '/api/v1/internal/jobs/customer-notices-tick' })).statusCode).toBe(401);
    const ok = await f.inject({ method: 'POST', url: '/api/v1/internal/jobs/customer-notices-tick', headers: { authorization: 'Bearer JOBTOK' } });
    expect(ok.statusCode).toBe(200);
    expect(ok.json()).toMatchObject({ ok: true, result: { observed: 0, sent: 0, shadow: 0 } });
    await f.close();
  });

  it('health reports counts', async () => {
    const { f } = app();
    await f.ready();
    const res = await f.inject({ method: 'GET', url: '/api/v1/internal/jobs/customer-notices-health', headers: { authorization: 'Bearer JOBTOK' } });
    expect(res.json()).toMatchObject({ ok: true, pending_approval: 0, flags: { masterEnabled: false, live: false } });
    await f.close();
  });
});
```

- [ ] **Step 2: Run to verify it fails.**

- [ ] **Step 3: Implement**

`config.ts` — add to `OrderIntakeConfig`:
```ts
  notices: {
    masterEnabled: boolean;        // WHATSAPP_NOTICES_ENABLED (default false) — hard off-switch in front of the DB flags
    lionwheelBaseUrl: string;      // LIONWHEEL_BASE_URL
    lionwheelApiKey: string;       // LIONWHEEL_API_KEY
    observeWindowDays: number;     // NOTICES_OBSERVE_WINDOW_DAYS, default 4
  };
  alerts: {
    emailTo: string[];             // ORDER_INTAKE_ALERT_TO, default tom@gteveryday.com
    emailFrom: string;             // ALERT_EMAIL_FROM, default onboarding@resend.dev
    resendApiKey: string;          // RESEND_API_KEY ('' => log only)
  };
```
and in `loadConfig`:
```ts
    notices: {
      masterEnabled: bool(env.WHATSAPP_NOTICES_ENABLED),
      lionwheelBaseUrl: env.LIONWHEEL_BASE_URL ?? 'https://members.lionwheel.com',
      lionwheelApiKey: env.LIONWHEEL_API_KEY ?? '',
      observeWindowDays: Math.max(1, Number(env.NOTICES_OBSERVE_WINDOW_DAYS ?? 4) || 4),
    },
    alerts: {
      emailTo: (env.ORDER_INTAKE_ALERT_TO ?? 'tom@gteveryday.com').split(',').map((s) => s.trim()).filter(Boolean),
      emailFrom: env.ALERT_EMAIL_FROM ?? 'onboarding@resend.dev',
      resendApiKey: env.RESEND_API_KEY ?? '',
    },
```
In `route.test.ts` add to both config fixtures: `notices: { masterEnabled: false, lionwheelBaseUrl: 'https://x', lionwheelApiKey: '', observeWindowDays: 4 }, alerts: { emailTo: [], emailFrom: 'x@y', resendApiKey: '' },`. In `route.ts` health add `notices_master_enabled: config.notices.masterEnabled,`. In `worker.ts` `buildLiveDeps` replace the Task 10 placeholder with `config.notices.masterEnabled`.

`notices/pool.ts`:
```ts
import pg from 'pg';
import type { OrderIntakeConfig } from '../config.js';
let cached: pg.Pool | null = null;
export function getNoticesPool(config: OrderIntakeConfig): pg.Pool {
  if (!cached) cached = new pg.Pool({ connectionString: config.databaseUrl, max: 4 });
  return cached;
}
```

`notices/routes.ts`:
```ts
// Fastify routes for the notices module.
//   POST /api/v1/internal/jobs/customer-notices-tick    (bearer JOB_RUNNER_TOKEN; pg_cron caller)
//   GET  /api/v1/internal/jobs/customer-notices-health  (bearer JOB_RUNNER_TOKEN)
//   GET  /api/v1/queries/customer-notices?state=pending_approval          (session; Task 12)
//   POST /api/v1/mutations/customer-notices/:notice_id/approve|suppress   (session; Task 12)
import type { FastifyInstance, FastifyRequest } from 'fastify';
import type { Session } from '../../auth/session.js';
import type { NoticeStore } from './store.js';
import { runNoticesTick, type TickDeps } from './tick.js';

export interface NoticesRouteOpts {
  jobToken: string | undefined;             // JOB_RUNNER_TOKEN
  store: NoticeStore;
  tickDeps: TickDeps;
  extractSession: (req: FastifyRequest) => Promise<Session>;
  now?: () => Date;
}

function bearerOk(req: FastifyRequest, token: string | undefined): boolean {
  return !!token && (req.headers['authorization'] ?? '') === `Bearer ${token}`;
}

export function registerCustomerNoticesRoutes(app: FastifyInstance, opts: NoticesRouteOpts): void {
  app.post('/api/v1/internal/jobs/customer-notices-tick', async (req, reply) => {
    if (!opts.jobToken) return reply.code(503).send({ ok: false, error: 'JOB_RUNNER_TOKEN not configured' });
    if (!bearerOk(req, opts.jobToken)) return reply.code(401).send({ ok: false, error: 'unauthorized' });
    try {
      const result = await runNoticesTick(opts.tickDeps);
      return reply.code(200).send({ ok: true, result });
    } catch (err) {
      return reply.code(500).send({ ok: false, error: (err as Error).message });
    }
  });

  app.get('/api/v1/internal/jobs/customer-notices-health', async (req, reply) => {
    if (!bearerOk(req, opts.jobToken)) return reply.code(401).send({ ok: false, error: 'unauthorized' });
    const [flags, pending] = await Promise.all([opts.store.getFlags(), opts.store.listPending()]);
    const oldest = pending[0]?.created_at ?? null;
    return reply.code(200).send({
      ok: true, flags, pending_approval: pending.length,
      oldest_pending_minutes: oldest ? Math.round(((opts.now?.() ?? new Date()).getTime() - new Date(oldest).getTime()) / 60_000) : null,
    });
  });
}
```

`server.ts` — next to `registerWaOrderBotRoute(app);` add:
```ts
  // Customer notices (spec 2026-09-09): tick + approval API. Same pool
  // discipline as the internal job routes; flags default to shadow.
  {
    const cfg = loadOrderIntakeConfig();
    const pool = getNoticesPool(cfg);
    const store = createPgNoticeStore(pool, { masterEnabled: cfg.notices.masterEnabled });
    const gql = createShopifyGraphQL({ storeDomain: cfg.shopify.storeDomain, adminToken: cfg.shopify.adminToken, apiVersion: cfg.shopify.apiVersion });
    registerCustomerNoticesRoutes(app, {
      jobToken: process.env.JOB_RUNNER_TOKEN,
      store,
      tickDeps: {
        store,
        lwShow: createLwShow({ baseUrl: cfg.notices.lionwheelBaseUrl, apiKey: cfg.notices.lionwheelApiKey }),
        orderCustomer: createOrderCustomerLookup(gql),
        whatsapp: createWhatsAppPort({ phoneNumberId: cfg.whatsapp.phoneNumberId, sendToken: cfg.whatsapp.sendToken, apiBaseUrl: cfg.whatsapp.apiBaseUrl, graphVersion: cfg.whatsapp.graphVersion }),
        alert: createAlertPort({ webhookUrl: cfg.alertWebhookUrl, resendApiKey: cfg.alerts.resendApiKey, emailTo: cfg.alerts.emailTo, emailFrom: cfg.alerts.emailFrom }),
        observeWindowDays: cfg.notices.observeWindowDays,
      },
      extractSession,
    });
  }
```
with imports `import { loadConfig as loadOrderIntakeConfig } from './order-intake/config.js'; import { getNoticesPool } from './order-intake/notices/pool.js'; import { createPgNoticeStore } from './order-intake/notices/store.js'; import { createLwShow } from './order-intake/notices/lionwheel_show.js'; import { createOrderCustomerLookup } from './order-intake/notices/shopify_order.js'; import { createShopifyGraphQL } from './order-intake/shopify/graphql.js'; import { createWhatsAppPort } from './order-intake/whatsapp/send.js'; import { createAlertPort } from './order-intake/alert.js'; import { registerCustomerNoticesRoutes } from './order-intake/notices/routes.js';`. (`createAlertPort`'s new options land in Task 14; until then pass only `{ webhookUrl }`.)

- [ ] **Step 4: Run** — `npx vitest run api/src/order-intake` all green; `npm run typecheck` clean; `node -e "require('./api/dist/server.js')"` is not needed — the API is started by Railway; a local `npm run dev` boot (if available) must not throw on registration.

- [ ] **Step 5: Commit**

```bash
git add api/src/order-intake/config.ts api/src/order-intake/route.ts api/src/order-intake/notices/pool.ts api/src/order-intake/notices/routes.ts api/src/order-intake/notices/__tests__/routes.test.ts api/src/order-intake/__tests__/route.test.ts api/src/server.ts api/src/order-intake/worker.ts
git commit -m "feat(notices): config, pool, tick + health job routes, server wiring"
```

---

### Task 12: approval API — list, approve, suppress

**Files:**
- Create: `api/src/order-intake/notices/approve.ts`
- Modify: `api/src/order-intake/notices/routes.ts` (three session routes)
- Test: `api/src/order-intake/notices/__tests__/approve.test.ts`, extend `__tests__/routes.test.ts`

**Interfaces:**
- Consumes: `NoticeStore.getNotice/listPending/approve/suppress` (Task 7), `buildConfirmedTemplate` (Task 3), `sendNotBefore` (Task 2), `Session` (`api/src/auth/session.ts`: `user_id`, `role`, `display_name`).
- Produces:
```ts
export const ApproveRequestSchema: z.ZodType<{ delivery_date: string; lines: Array<{ item_label: string; qty_delivering: number; resolution?: LineResolution | null; substitute_label?: string | null }> }>;
export const SuppressRequestSchema: z.ZodType<{ reason: string }>;
export type ApproveOutcome = { status: 200; body: { row: NoticeRow } } | { status: 404 | 409 | 422; body: { error: string } };
export function roleMayApprove(role: string): boolean;                      // admin | viewer | planner
export async function handleApprove(store, session, noticeId, req, now): Promise<ApproveOutcome>;
export async function handleSuppress(store, session, noticeId, req): Promise<ApproveOutcome>;
```
Routes: `GET /api/v1/queries/customer-notices?state=pending_approval` → `{ rows, pending_count }`; `POST /api/v1/mutations/customer-notices/:notice_id/approve`; `POST /api/v1/mutations/customer-notices/:notice_id/suppress`. Roles: `admin`, `viewer` (bookkeeper, same exception as credit-tracking), `planner` (Avi). Others → 403.

- [ ] **Step 1: Write the failing tests**

`approve.test.ts`:
```ts
import { describe, it, expect } from 'vitest';
import { handleApprove, handleSuppress, roleMayApprove } from '../approve.js';
import { fakeStore } from './fake_store.js';

const NOW = new Date('2026-09-09T12:00:00Z');
const tom = { user_id: '00000000-0000-0000-0000-000000000001', email: 't@x', role: 'admin' as const, display_name: 'Tom' };
async function pending() {
  const fs = fakeStore({ now: () => NOW });
  const row = (await fs.store.createNotice({
    kind: 'confirmed_partial', state: 'pending_approval', wa_phone: '972500000001', shopify_customer_id: '7123', shopify_order_name: '#GT14512',
    mirror_id: 'm1', lw_task_id: '1', dedupe_key: 'confirmed:m1', template_name: null, template_params: [], header_image_url: null, delivery_date: null, send_not_before: null,
    lines: [
      { item_label: 'DETOX 1000ml', item_id: null, line_mirror_id: 'l1', qty_ordered: 12, qty_delivering: 12, resolution: null, substitute_label: null },
      { item_label: 'FRESH 1000ml', item_id: null, line_mirror_id: 'l2', qty_ordered: 6, qty_delivering: 6, resolution: null, substitute_label: null },
    ],
  }))!;
  return { fs, row };
}

describe('roleMayApprove', () => {
  it('admin, viewer, planner yes; operator, sales_rep no', () => {
    expect(['admin', 'viewer', 'planner'].every(roleMayApprove)).toBe(true);
    expect(['operator', 'sales_rep'].some(roleMayApprove)).toBe(false);
  });
});

describe('handleApprove', () => {
  it('short line with resolution → approved, partial template rendered, send window set', async () => {
    const { fs, row } = await pending();
    const out = await handleApprove(fs.store, tom, row.notice_id, { delivery_date: '2026-09-10', lines: [{ item_label: 'FRESH 1000ml', qty_delivering: 4, resolution: 'credit' }] }, NOW);
    expect(out.status).toBe(200);
    const n = fs.notices.get(row.notice_id)!;
    expect(n).toMatchObject({ state: 'approved', delivery_date: '2026-09-10', template_name: 'gt_order_confirmed_partial_v1', send_not_before: NOW.toISOString() });
    expect(n.template_params).toEqual(['מחר, יום חמישי 10.9', 'DETOX 1000ml ×12 · FRESH 1000ml ×4', 'FRESH 1000ml ×2 מתוך 6', 'FRESH 1000ml — יזוכה בחשבונית.']);
    expect(n.lines.find((l) => l.item_label === 'DETOX 1000ml')!.qty_delivering).toBe(12); // untouched lines keep ordered qty
  });

  it('all lines full (human only set the day) → the FULL template', async () => {
    const { fs, row } = await pending();
    await handleApprove(fs.store, tom, row.notice_id, { delivery_date: '2026-09-10', lines: [] }, NOW);
    expect(fs.notices.get(row.notice_id)!.template_name).toBe('gt_order_confirmed_full_v1');
  });

  it('422 on a short line without resolution, substitute without label, qty above ordered, unknown label; 403 on role; 404 unknown; 409 not pending', async () => {
    const { fs, row } = await pending();
    const bad = (lines: any[]) => handleApprove(fs.store, tom, row.notice_id, { delivery_date: '2026-09-10', lines }, NOW);
    expect((await bad([{ item_label: 'FRESH 1000ml', qty_delivering: 4 }])).status).toBe(422);
    expect((await bad([{ item_label: 'FRESH 1000ml', qty_delivering: 0, resolution: 'substitute' }])).status).toBe(422);
    expect((await bad([{ item_label: 'FRESH 1000ml', qty_delivering: 7, resolution: 'credit' }])).status).toBe(422);
    expect((await bad([{ item_label: 'NOPE', qty_delivering: 1, resolution: 'credit' }])).status).toBe(422);
    expect((await handleApprove(fs.store, { ...tom, role: 'operator' as any }, row.notice_id, { delivery_date: '2026-09-10', lines: [] }, NOW)).status).toBe(403);
    expect((await handleApprove(fs.store, tom, 'missing', { delivery_date: '2026-09-10', lines: [] }, NOW)).status).toBe(404);
    await handleApprove(fs.store, tom, row.notice_id, { delivery_date: '2026-09-10', lines: [] }, NOW);
    expect((await handleApprove(fs.store, tom, row.notice_id, { delivery_date: '2026-09-10', lines: [] }, NOW)).status).toBe(409);
  });
});

describe('handleSuppress', () => {
  it('suppresses a pending notice with a reason; requires a reason', async () => {
    const { fs, row } = await pending();
    expect((await handleSuppress(fs.store, tom, row.notice_id, { reason: 'התקשרתי ללקוח' })).status).toBe(200);
    expect(fs.notices.get(row.notice_id)!.state).toBe('suppressed');
  });
});
```

Extend `routes.test.ts`:
```ts
describe('approval routes', () => {
  it('lists pending, approves, then 409s on a second approve', async () => {
    const { f, fs } = app();
    await fs.store.createNotice({ kind: 'confirmed_partial', state: 'pending_approval', wa_phone: '9725', shopify_customer_id: null, shopify_order_name: '#GT1', mirror_id: 'm1', lw_task_id: '1', dedupe_key: 'confirmed:m1', template_name: null, template_params: [], header_image_url: null, delivery_date: null, send_not_before: null, lines: [{ item_label: 'A', item_id: null, line_mirror_id: null, qty_ordered: 6, qty_delivering: 6, resolution: null, substitute_label: null }] });
    await f.ready();
    const list = await f.inject({ method: 'GET', url: '/api/v1/queries/customer-notices?state=pending_approval' });
    expect(list.json()).toMatchObject({ pending_count: 1 });
    const id = list.json().rows[0].notice_id;
    const ok = await f.inject({ method: 'POST', url: `/api/v1/mutations/customer-notices/${id}/approve`, payload: { delivery_date: '2026-09-10', lines: [] } });
    expect(ok.statusCode).toBe(200);
    expect((await f.inject({ method: 'POST', url: `/api/v1/mutations/customer-notices/${id}/approve`, payload: { delivery_date: '2026-09-10', lines: [] } })).statusCode).toBe(409);
    expect((await f.inject({ method: 'POST', url: `/api/v1/mutations/customer-notices/${id}/suppress`, payload: {} })).statusCode).toBe(422);
    await f.close();
  });
});
```

- [ ] **Step 2: Run to verify it fails.**

- [ ] **Step 3: Write `approve.ts`**

```ts
// Approval / suppression of a pending partial-pick notice. Validation and
// template rendering live here; persistence + audit in the store.
import { z } from 'zod';
import type { Session } from '../../auth/session.js';
import type { NoticeStore } from './store.js';
import type { NoticeLine, NoticeRow, Actor } from './types.js';
import { buildConfirmedTemplate } from './render.js';
import { sendNotBefore } from './time.js';

export const ApproveRequestSchema = z.object({
  delivery_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  lines: z.array(z.object({
    item_label: z.string().min(1),
    qty_delivering: z.number().min(0),
    resolution: z.enum(['credit', 'next_route', 'substitute']).nullable().optional(),
    substitute_label: z.string().nullable().optional(),
  })).default([]),
});
export type ApproveRequest = z.infer<typeof ApproveRequestSchema>;
export const SuppressRequestSchema = z.object({ reason: z.string().trim().min(1) });

export type ApproveOutcome = { status: 200; body: { row: NoticeRow } } | { status: 403 | 404 | 409 | 422; body: { error: string } };

export function roleMayApprove(role: string): boolean {
  return role === 'admin' || role === 'viewer' || role === 'planner';
}

function actorOf(s: Session): Actor { return { user_id: s.user_id, display_name: s.display_name }; }

export function mergeLines(stored: NoticeLine[], input: ApproveRequest['lines']): { lines: NoticeLine[] } | { error: string } {
  const byLabel = new Map(stored.map((l) => [l.item_label, { ...l }]));
  for (const i of input) {
    const l = byLabel.get(i.item_label);
    if (!l) return { error: `unknown line "${i.item_label}"` };
    if (i.qty_delivering > l.qty_ordered) return { error: `"${i.item_label}": qty_delivering above ordered` };
    l.qty_delivering = i.qty_delivering;
    l.resolution = i.resolution ?? null;
    l.substitute_label = i.substitute_label ?? null;
    if (l.qty_delivering < l.qty_ordered && !l.resolution) return { error: `"${i.item_label}": a short line needs a resolution` };
    if (l.resolution === 'substitute' && !l.substitute_label) return { error: `"${i.item_label}": substitute needs a label` };
    if (l.qty_delivering === l.qty_ordered) { l.resolution = null; l.substitute_label = null; }
  }
  return { lines: [...byLabel.values()] };
}

export async function handleApprove(store: NoticeStore, session: Session, noticeId: string, req: ApproveRequest, now: Date): Promise<ApproveOutcome> {
  if (!roleMayApprove(session.role)) return { status: 403, body: { error: 'role not permitted to approve customer notices' } };
  const notice = await store.getNotice(noticeId);
  if (!notice) return { status: 404, body: { error: 'notice not found' } };
  if (notice.state !== 'pending_approval') return { status: 409, body: { error: `notice is ${notice.state}` } };
  const merged = mergeLines(notice.lines, req.lines);
  if ('error' in merged) return { status: 422, body: { error: merged.error } };
  const tpl = buildConfirmedTemplate(merged.lines, req.delivery_date, now);
  const row = await store.approve(noticeId, {
    delivery_date: req.delivery_date, lines: merged.lines, template_name: tpl.template_name, template_params: tpl.params,
    send_not_before: sendNotBefore(now).toISOString(),
  }, actorOf(session));
  if (!row) return { status: 409, body: { error: 'notice is no longer pending' } };
  return { status: 200, body: { row } };
}

export async function handleSuppress(store: NoticeStore, session: Session, noticeId: string, req: { reason: string }): Promise<ApproveOutcome> {
  if (!roleMayApprove(session.role)) return { status: 403, body: { error: 'role not permitted to suppress customer notices' } };
  const notice = await store.getNotice(noticeId);
  if (!notice) return { status: 404, body: { error: 'notice not found' } };
  if (notice.state !== 'pending_approval') return { status: 409, body: { error: `notice is ${notice.state}` } };
  const row = await store.suppress(noticeId, req.reason, actorOf(session));
  if (!row) return { status: 409, body: { error: 'notice is no longer pending' } };
  return { status: 200, body: { row } };
}
```

Add to `routes.ts` (inside `registerCustomerNoticesRoutes`, after the health route; import `AuthError` from `../../auth/session.js`, and the three symbols from `./approve.js`):

```ts
  async function session(req: FastifyRequest, reply: FastifyReply): Promise<Session | null> {
    try { return await opts.extractSession(req); } catch (err) {
      if (err instanceof AuthError) { reply.code(err.statusCode).send({ error: err.message }); return null; }
      throw err;
    }
  }

  app.get<{ Querystring: { state?: string } }>('/api/v1/queries/customer-notices', async (req, reply) => {
    const s = await session(req, reply); if (!s) return;
    if (req.query.state && req.query.state !== 'pending_approval') return reply.code(422).send({ error: 'only state=pending_approval is supported' });
    const rows = await opts.store.listPending();
    return reply.code(200).send({ rows, pending_count: rows.length });
  });

  app.post<{ Params: { notice_id: string } }>('/api/v1/mutations/customer-notices/:notice_id/approve', async (req, reply) => {
    const s = await session(req, reply); if (!s) return;
    const parsed = ApproveRequestSchema.safeParse(req.body ?? {});
    if (!parsed.success) return reply.code(422).send({ validation_errors: parsed.error.issues.map((i) => ({ path: i.path, code: i.code, message: i.message })) });
    const out = await handleApprove(opts.store, s, req.params.notice_id, parsed.data, opts.now?.() ?? new Date());
    return reply.code(out.status).send(out.body);
  });

  app.post<{ Params: { notice_id: string } }>('/api/v1/mutations/customer-notices/:notice_id/suppress', async (req, reply) => {
    const s = await session(req, reply); if (!s) return;
    const parsed = SuppressRequestSchema.safeParse(req.body ?? {});
    if (!parsed.success) return reply.code(422).send({ validation_errors: parsed.error.issues.map((i) => ({ path: i.path, code: i.code, message: i.message })) });
    const out = await handleSuppress(opts.store, s, req.params.notice_id, parsed.data);
    return reply.code(out.status).send(out.body);
  });
```
(`FastifyReply` and `Session` types imported at the top.)

- [ ] **Step 4: Run** — `npx vitest run api/src/order-intake` all green; `npm run typecheck` clean.

- [ ] **Step 5: Commit**

```bash
git add api/src/order-intake/notices/approve.ts api/src/order-intake/notices/routes.ts api/src/order-intake/notices/__tests__/approve.test.ts api/src/order-intake/notices/__tests__/routes.test.ts
git commit -m "feat(notices): list / approve / suppress API for partial-pick notices"
```

---

### Task 13: Edge job `customer_notice_reminder` (16:30 + 07:30 Israel, Tom only)

**Files:**
- Modify: `supabase/functions/factory_os_jobs/index.ts` (new job next to `runMissingPicksDailyEmail`; dispatch branch)

**Interfaces:**
- Consumes (existing in the file): `getPool()`, `israelNowParts(d)`, `israelTimestamp(iso)`, `escapeHtml(s)`, `fetchWithTimeout(url, init, ms)`, `checkBreakGlass(client)`, `logBreakGlassAbort(...)`, `private_core.job_runs`, `private_core.alert_deliveries`.
- Produces: `runCustomerNoticeReminder(force: boolean)`; `POST {"job":"customer_notice_reminder"}` (+ `"force":true` bypasses the hour gate for a manual verification send).

- [ ] **Step 1: Add the job** (place after `runMissingPicksDailyEmail`)

```ts
// ---------------------------------------------------------------------------
// Job: customer_notice_reminder
//
// Twice a day (16:30 + 07:30 Asia/Jerusalem; pg_cron fires 04:30/05:30/13:30/
// 14:30 UTC and this gate keeps exactly one tick per slot regardless of DST)
// email the partial-pick approvals still waiting in order_intake.customer_notices
// to CUSTOMER_NOTICE_REMINDER_TO (default tom@gteveryday.com — Tom 2026-09-09),
// plus, as information only, open tasks older than a day that are not picked yet.
// Empty queue => no email, one 'no_pending' audit row.
// Spec: brain docs/superpowers/specs/2026-09-09-whatsapp-customer-notices-design.md §3 (2ב)
// ---------------------------------------------------------------------------
const CUSTOMER_NOTICE_MARKER = 'customer_notice_reminder';
const CUSTOMER_NOTICE_DEFAULT_TO = 'tom@gteveryday.com';
const CUSTOMER_NOTICE_HOURS_IL = [16, 7];
const CUSTOMER_NOTICE_PORTAL_URL = 'https://gt-factory-os-portal.vercel.app/credit-tracking?tab=partial-picks';

interface PendingNoticeRow {
  notice_id: string; created_at: string; shopify_order_name: string | null; customer_name: string | null;
  wa_phone: string; delivery_date: string | null; lines: Array<{ item_label: string; qty_ordered: number; qty_delivering: number }>;
}
interface NotReadyRow { lw_task_id: string; wp_order_id: string | null; customer_name: string | null; created_at: string; pick_status: string | null }

function buildCustomerNoticeReminderEmail(pending: PendingNoticeRow[], notReady: NotReadyRow[], il: { date: string; hour: number }): { subject: string; text: string; html: string } {
  const missed = il.hour < 12;
  const subject = `[GT] ${pending.length} אישורי ליקוט חלקי ממתינים — ${il.date} ${String(il.hour).padStart(2, '0')}:30${missed ? ' (הבטחת 17:00 פוספסה)' : ''}`;
  const lineTxt = (n: PendingNoticeRow) => n.lines.map((l) => `${l.item_label} ${l.qty_delivering}/${l.qty_ordered}`).join(', ');
  const text = [
    `אישורי ליקוט חלקי ממתינים: ${pending.length}`,
    ...pending.map((n) => `• ${n.customer_name ?? n.wa_phone} · ${n.shopify_order_name ?? ''} · אספקה: ${n.delivery_date ?? 'לא נקבע'} · ${lineTxt(n)} · ממתין מאז ${israelTimestamp(n.created_at)}`),
    '', `לאישור: ${CUSTOMER_NOTICE_PORTAL_URL}`,
    ...(notReady.length ? ['', 'לא ניתן לאשר אוטומטית (טרם לוקט, מידע בלבד):', ...notReady.map((t) => `• ${t.customer_name ?? ''} · ${t.wp_order_id ?? ''} · LionWheel ${t.lw_task_id} · pick_status=${t.pick_status ?? '—'} · נוצר ${israelTimestamp(t.created_at)}`)] : []),
  ].join('\n');
  const row = (n: PendingNoticeRow) => `<tr><td>${escapeHtml(n.customer_name ?? n.wa_phone)}</td><td>${escapeHtml(n.shopify_order_name ?? '')}</td><td>${escapeHtml(n.delivery_date ?? 'לא נקבע')}</td><td>${escapeHtml(lineTxt(n))}</td><td>${escapeHtml(israelTimestamp(n.created_at))}</td></tr>`;
  const html = `<div dir="rtl" style="font-family:Arial,sans-serif;font-size:14px">
<h2>אישורי ליקוט חלקי ממתינים: ${pending.length}</h2>
<table border="1" cellpadding="6" style="border-collapse:collapse"><tr><th>לקוח</th><th>הזמנה</th><th>יום אספקה</th><th>שורות (יוצא/הוזמן)</th><th>ממתין מאז</th></tr>${pending.map(row).join('')}</table>
<p><a href="${CUSTOMER_NOTICE_PORTAL_URL}" style="display:inline-block;padding:10px 16px;background:#1a7f5a;color:#fff;text-decoration:none;border-radius:6px">לאישור בפורטל</a></p>
${notReady.length ? `<h3>לא ניתן לאשר אוטומטית (טרם לוקט, מידע בלבד)</h3><ul>${notReady.map((t) => `<li>${escapeHtml(t.customer_name ?? '')} · ${escapeHtml(t.wp_order_id ?? '')} · LionWheel ${escapeHtml(t.lw_task_id)} · pick_status=${escapeHtml(t.pick_status ?? '—')}</li>`).join('')}</ul>` : ''}
</div>`;
  return { subject, text, html };
}

async function runCustomerNoticeReminder(force = false): Promise<any> {
  const pool = getPool();
  const client = await pool.connect();
  const now = new Date();
  const cycleAt = now.toISOString();
  const il = israelNowParts(now);
  const result: any = { job_run_id: '', cycle_at: cycleAt, israel_date: il.date, israel_hour: il.hour, delivery_status: 'unknown', pending_count: 0, not_ready_count: 0 };
  try {
    const bg = await checkBreakGlass(client);
    if (bg.active) {
      result.job_run_id = await logBreakGlassAbort(client, 'customer_notice_reminder', bg.reason ?? 'unknown', now);
      result.delivery_status = 'break_glass';
      return result;
    }
    const jr = await client.query(`INSERT INTO private_core.job_runs (job_name, status, started_at, triggered_by) VALUES ('customer_notice_reminder','running',$1,$2) RETURNING run_id`, [cycleAt, force ? 'manual' : 'cron']);
    const jobRunId: string = jr.rows[0].run_id; result.job_run_id = jobRunId;
    const finishRun = async (status: string, error: string | null = null) => {
      await client.query(`UPDATE private_core.job_runs SET status=$2, ended_at=$3, error=$4 WHERE run_id=$1`, [jobRunId, status, new Date().toISOString(), error]);
    };

    if (!force && !CUSTOMER_NOTICE_HOURS_IL.includes(il.hour)) { await finishRun('succeeded'); result.delivery_status = 'skipped_off_window'; return result; }
    if (!force) {
      const already = await client.query(
        `SELECT 1 FROM private_core.alert_deliveries
          WHERE $1 = ANY(categories_seen) AND delivery_status IN ('sent','no_pending')
            AND (cycle_at AT TIME ZONE 'Asia/Jerusalem')::date = $2::date
            AND EXTRACT(HOUR FROM cycle_at AT TIME ZONE 'Asia/Jerusalem') = $3 LIMIT 1`,
        [CUSTOMER_NOTICE_MARKER, il.date, il.hour]);
      if ((already.rowCount ?? 0) > 0) { await finishRun('succeeded'); result.delivery_status = 'skipped_already_sent'; return result; }
    }

    const pending = await client.query(
      `SELECT n.notice_id, n.created_at, n.shopify_order_name, om.lw_destination_recipient_name AS customer_name, n.wa_phone,
              n.delivery_date::text AS delivery_date,
              COALESCE((SELECT json_agg(json_build_object('item_label', l.item_label, 'qty_ordered', l.qty_ordered::float8, 'qty_delivering', l.qty_delivering::float8) ORDER BY l.item_label)
                          FROM order_intake.customer_notice_lines l WHERE l.notice_id = n.notice_id), '[]'::json) AS lines
         FROM order_intake.customer_notices n
         LEFT JOIN private_core.orders_mirror om ON om.mirror_id = n.mirror_id
        WHERE n.state = 'pending_approval'
        ORDER BY n.created_at`);
    const notReady = await client.query(
      `SELECT om.lw_task_id::text AS lw_task_id, om.wp_order_id, om.lw_destination_recipient_name AS customer_name, om.created_at,
              (SELECT o.pick_status FROM order_intake.lw_pick_observations o WHERE o.mirror_id = om.mirror_id ORDER BY o.observed_at DESC LIMIT 1) AS pick_status
         FROM private_core.orders_mirror om
        WHERE om.retired_at IS NULL
          AND om.lw_status NOT IN ('COMPLETED','ROUNDTRIP_DELIVERED','DELIVERED','CANCELED','CANCELLED','FAILED')
          AND om.created_at BETWEEN now() - interval '4 days' AND now() - interval '1 day'
          AND NOT EXISTS (SELECT 1 FROM order_intake.customer_notices n WHERE n.mirror_id = om.mirror_id AND n.kind IN ('confirmed_full','confirmed_partial'))
        ORDER BY om.created_at`);
    result.pending_count = pending.rows.length; result.not_ready_count = notReady.rows.length;

    const recipients = (Deno.env.get('CUSTOMER_NOTICE_REMINDER_TO') ?? CUSTOMER_NOTICE_DEFAULT_TO).split(',').map((s: string) => s.trim()).filter((s: string) => s.length > 0);
    const sender = Deno.env.get('ALERT_EMAIL_FROM') ?? 'onboarding@resend.dev';
    const resendKey = Deno.env.get('RESEND_API_KEY');

    if (pending.rows.length === 0) {
      await client.query(`INSERT INTO private_core.alert_deliveries (cycle_at, delivery_status, recipient, sender, categories_seen, job_run_id) VALUES ($1,'no_pending',$2,$3,$4,$5)`,
        [cycleAt, recipients.join(','), sender, [CUSTOMER_NOTICE_MARKER], jobRunId]);
      await finishRun('succeeded'); result.delivery_status = 'no_pending'; return result;
    }
    const { subject, text, html } = buildCustomerNoticeReminderEmail(pending.rows as PendingNoticeRow[], notReady.rows as NotReadyRow[], il);
    const noticeIds = pending.rows.map((r: any) => r.notice_id);
    if (!resendKey) {
      await client.query(`INSERT INTO private_core.alert_deliveries (cycle_at, delivery_status, recipient, sender, subject, categories_seen, exception_ids, job_run_id, error) VALUES ($1,'failed',$2,$3,$4,$5,$6,$7,'RESEND_API_KEY unset')`,
        [cycleAt, recipients.join(','), sender, subject, [CUSTOMER_NOTICE_MARKER], noticeIds, jobRunId]);
      await finishRun('failed', 'RESEND_API_KEY unset'); result.delivery_status = 'failed'; return result;
    }
    const resp = await fetchWithTimeout('https://api.resend.com/emails', {
      method: 'POST', headers: { Authorization: `Bearer ${resendKey}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ from: `GT Factory OS <${sender}>`, to: recipients, subject, text, html }),
    }, 30_000);
    let respBody: any = null; try { respBody = await resp.json(); } catch { /* keep null */ }
    const ok = resp.ok;
    await client.query(
      `INSERT INTO private_core.alert_deliveries (cycle_at, delivery_status, recipient, sender, subject, categories_seen, exception_ids, provider, provider_message_id, http_status, job_run_id, sent_at, error)
       VALUES ($1,$2,$3,$4,$5,$6,$7,'resend',$8,$9,$10,$11,$12)`,
      [cycleAt, ok ? 'sent' : 'failed', recipients.join(','), sender, subject, [CUSTOMER_NOTICE_MARKER], noticeIds, respBody?.id ?? null, resp.status, jobRunId, ok ? new Date().toISOString() : null, ok ? null : JSON.stringify(respBody).slice(0, 500)]);
    await finishRun(ok ? 'succeeded' : 'failed', ok ? null : `resend http ${resp.status}`);
    result.delivery_status = ok ? 'sent' : 'failed'; result.http_status = resp.status;
    return result;
  } finally { client.release(); }
}
```

Dispatch: next to `else if (job === 'missing_picks_daily_email')` add
```ts
    } else if (job === 'customer_notice_reminder') {
      result = await runCustomerNoticeReminder(body?.force === true);
```
where `body` is the parsed request JSON the handler already reads `job` from (if the handler destructures only `job`, keep a reference to the parsed object and read `force` from it).

- [ ] **Step 2: Verify**

```bash
cd supabase/functions/factory_os_jobs && deno check index.ts
```
Expected: no type errors. Deploy is part of the release (Task 15 §Deploy); after deploy, verify with a manual forced run (sends a real email to Tom only):
```bash
curl -s -X POST https://rvadsozabmxkkrktwgnv.supabase.co/functions/v1/factory_os_jobs -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_JWT" -H 'Content-Type: application/json' -d '{"job":"customer_notice_reminder","force":true}'
```
Expected JSON: `delivery_status` = `no_pending` (empty queue) or `sent`, and one `alert_deliveries` row with `categories_seen = {customer_notice_reminder}`.

- [ ] **Step 3: Commit**

```bash
git add supabase/functions/factory_os_jobs/index.ts
git commit -m "feat(notices): customer_notice_reminder Edge job — pending approvals to Tom at 16:30 and 07:30"
```

---

### Task 14: `alert.ts` — email transport + new alert kinds

**Files:**
- Modify: `api/src/order-intake/alert.ts`
- Test: `api/src/order-intake/__tests__/alert.test.ts` (new)

**Interfaces:**
- Produces: `OrderIntakeAlert.kind` union extended with `'wants_call' | 'customer_reply_after_notice' | 'notice_send_failed' | 'confirmed_then_changed'`; `session_id` becomes optional; new optional `notice_id`, `order_name`; `createAlertPort({ webhookUrl?, resendApiKey?, emailTo?, emailFrom?, fetchFn? })`.

- [ ] **Step 1: Write the failing test**

```ts
import { describe, it, expect } from 'vitest';
import { createAlertPort } from '../alert.js';

describe('createAlertPort email transport', () => {
  it('posts to Resend when a key and recipients are set; subject carries kind + customer', async () => {
    const calls: any[] = [];
    const port = createAlertPort({ resendApiKey: 'rk', emailTo: ['tom@gteveryday.com'], emailFrom: 'gt@x', fetchFn: (async (url: string, init: any) => { calls.push({ url, init }); return { ok: true, status: 200, text: async () => '{}' }; }) as any });
    await port.send({ kind: 'wants_call', customer: { display_name: 'קפה גן סיפור', wa_phone: '972500000001' }, notice_id: 'n1', order_name: '#GT14512', error: 'customer tapped "רוצה לדבר"' });
    expect(calls[0].url).toBe('https://api.resend.com/emails');
    const body = JSON.parse(calls[0].init.body);
    expect(body.to).toEqual(['tom@gteveryday.com']);
    expect(body.subject).toContain('wants_call');
    expect(body.subject).toContain('קפה גן סיפור');
    expect(body.text).toContain('#GT14512');
  });

  it('never throws: a failing transport is swallowed', async () => {
    const port = createAlertPort({ resendApiKey: 'rk', emailTo: ['t@x'], fetchFn: (async () => { throw new Error('net'); }) as any });
    await expect(port.send({ kind: 'notice_send_failed', customer: { display_name: null, wa_phone: '9725' }, error: 'x' })).resolves.toBeUndefined();
  });

  it('without a key it only logs (no fetch)', async () => {
    let called = 0;
    const port = createAlertPort({ fetchFn: (async () => { called++; return { ok: true }; }) as any });
    await port.send({ kind: 'commit_failed', customer: { display_name: null, wa_phone: '9725' }, session_id: 's1', error: 'x' });
    expect(called).toBe(0);
  });
});
```

- [ ] **Step 2: Run to verify it fails.**

- [ ] **Step 3: Rewrite `alert.ts`**

```ts
// Operational alerts for the order-intake bot and the notices module.
//
// Always logs loudly (Railway logs, greppable by kind). Optionally POSTs JSON to
// ORDER_INTAKE_ALERT_WEBHOOK_URL and/or emails via Resend (RESEND_API_KEY +
// ORDER_INTAKE_ALERT_TO, default tom@gteveryday.com). Delivery must never
// break the pipeline — failures are swallowed + logged.

export interface AlertPort {
  send(alert: OrderIntakeAlert): Promise<void>;
}

export type AlertKind =
  | 'commit_failed' | 'complete_failed' | 'session_update_failed'
  | 'wants_call' | 'customer_reply_after_notice' | 'notice_send_failed' | 'confirmed_then_changed';

export interface OrderIntakeAlert {
  kind: AlertKind;
  customer: { display_name: string | null; wa_phone: string };
  session_id?: string;
  notice_id?: string;
  order_name?: string | null;
  error: string;
  cart_lines?: Array<{ name: string; bottles: number; unit_price: number | null }>;
  draft_name?: string | null;
}

export interface AlertPortOptions {
  webhookUrl?: string;
  resendApiKey?: string;
  emailTo?: string[];
  emailFrom?: string;
  fetchFn?: typeof fetch;
}

const SUBJECT_HE: Record<AlertKind, string> = {
  commit_failed: 'הזמנת וואטסאפ לא נקלטה בשופיפיי',
  complete_failed: 'דראפט נוצר אבל לא הושלם',
  session_update_failed: 'שגיאת מצב בבוט',
  wants_call: 'לקוח מבקש שיחה',
  customer_reply_after_notice: 'לקוח הגיב להודעת עדכון',
  notice_send_failed: 'הודעת עדכון ללקוח נכשלה',
  confirmed_then_changed: 'משלוח בוטל אחרי שנשלח אישור',
};

export function createAlertPort(opts: AlertPortOptions): AlertPort {
  const doFetch = opts.fetchFn ?? fetch;
  const emailTo = (opts.emailTo ?? []).filter(Boolean);
  return {
    async send(alert) {
      const who = alert.customer.display_name ?? alert.customer.wa_phone;
      console.error(`[order-intake ALERT] ${alert.kind} customer=${who} session=${alert.session_id ?? '-'} notice=${alert.notice_id ?? '-'} error=${alert.error}`);
      const payload = { source: 'wa-order-bot', at: new Date().toISOString(), ...alert };
      if (opts.webhookUrl) {
        try {
          await doFetch(opts.webhookUrl, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(payload) });
        } catch (err) { console.error(`[order-intake ALERT] webhook delivery failed: ${(err as Error).message}`); }
      }
      if (opts.resendApiKey && emailTo.length > 0) {
        const text = [
          `${SUBJECT_HE[alert.kind]} (${alert.kind})`,
          `לקוח: ${who} (${alert.customer.wa_phone})`,
          alert.order_name ? `הזמנה: ${alert.order_name}` : null,
          alert.notice_id ? `notice: ${alert.notice_id}` : null,
          alert.draft_name ? `draft: ${alert.draft_name}` : null,
          `פרטים: ${alert.error}`,
          alert.cart_lines?.length ? 'שורות: ' + alert.cart_lines.map((l) => `${l.name} ×${l.bottles}`).join(' · ') : null,
        ].filter(Boolean).join('\n');
        try {
          await doFetch('https://api.resend.com/emails', {
            method: 'POST',
            headers: { Authorization: `Bearer ${opts.resendApiKey}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ from: `GT Factory OS <${opts.emailFrom ?? 'onboarding@resend.dev'}>`, to: emailTo, subject: `[wa-order-bot] ${alert.kind} — ${who}: ${SUBJECT_HE[alert.kind]}`, text }),
          });
        } catch (err) { console.error(`[order-intake ALERT] email delivery failed: ${(err as Error).message}`); }
      }
    },
  };
}
```
Then remove any `as any` casts left in `tick.ts` / `worker.ts` from Tasks 9–10 and pass the full alert options in `server.ts` (Task 11 code already does).

- [ ] **Step 4: Run** — `npx vitest run api/src/order-intake` all green; `npm run typecheck` clean.

- [ ] **Step 5: Commit**

```bash
git add api/src/order-intake/alert.ts api/src/order-intake/__tests__/alert.test.ts api/src/order-intake/notices/tick.ts api/src/order-intake/worker.ts api/src/server.ts
git commit -m "feat(notices): staff alerts by email (Resend) with the new alert kinds"
```

---

### Task 15: receipt wording, docs, env example, release

**Files:**
- Modify: `api/src/order-intake/whatsapp/messages.ts`, `api/src/order-intake/whatsapp/__tests__/messages.test.ts`, `api/src/order-intake/worker.ts` (pass `now`)
- Modify: `.env.example`, `api/src/order-intake/README.md`

- [ ] **Step 1: Write the failing receipt tests** (replace the two draft/committed cases in `messages.test.ts`)

```ts
const BEFORE_CUTOFF = new Date('2026-09-09T08:00:00Z'); // 11:00 IDT
const AFTER_CUTOFF = new Date('2026-09-09T12:30:00Z');  // 15:30 IDT

it('supervised draft before 14:00: lists lines, promises the day-before update, invites an updated cart today; never a price', () => {
  const m = buildOrderReceipt({ cart, committed: false, now: BEFORE_CUTOFF });
  expect(m.body).toContain('קיבלנו את ההזמנה 🙏');
  expect(m.body).toContain("• DETOX 1000ml — 12 יח'");
  expect(m.body).toContain("• MYSTERY-42 — 3 יח' (לא זוהה — נבדוק)");
  expect(m.body).toContain('עד 17:00 ביום שלפני האספקה נשלח לכם מה יוצא בפועל ואת יום האספקה.');
  expect(m.body).toContain('לשינוי — שלחו עגלה מעודכנת עד 14:00 היום.');
  expect(m.body).not.toContain('מאשרים אצלנו');
  expect(m.body).not.toContain('₪');
});

it('after 14:00 the cart goes to the next round', () => {
  const m = buildOrderReceipt({ cart, committed: false, now: AFTER_CUTOFF });
  expect(m.body).toContain('ההזמנה נכנסה לסבב הבא. לשינוי — שלחו עגלה מעודכנת עד 14:00 מחר.');
});

it('committed order: carries the order number and the same promise', () => {
  const m = buildOrderReceipt({ cart: { ...cart, flags: [], ready: true }, committed: true, orderName: '#1777', now: BEFORE_CUTOFF });
  expect(m.body).toContain('#1777');
  expect(m.body).toContain('עד 17:00 ביום שלפני האספקה');
});
```

- [ ] **Step 2: Run to verify it fails.**

- [ ] **Step 3: Implement** — in `messages.ts` replace `buildOrderReceipt`:

```ts
import { ilParts } from '../notices/time.js';

export const INTAKE_CUTOFF_HOUR_IL = 14;

// Receipt for a catalog cart (station 1). The closing lines are the promise the
// notices system keeps: what ships and when, by 17:00 the day before.
export function buildOrderReceipt(args: { cart: Cart; committed: boolean; orderName?: string | null; now?: Date }): OutgoingMessage {
  const rows = args.cart.lines.map((l) => {
    const unresolved = l.resolve_status !== 'OK';
    return `• ${displayName(l)} — ${l.bottles} יח'${unresolved ? ' (לא זוהה — נבדוק)' : ''}`;
  });
  const head = args.committed && args.orderName
    ? `ההזמנה נקלטה ✅ מספר הזמנה ${args.orderName}`
    : 'קיבלנו את ההזמנה 🙏';
  const afterCutoff = ilParts(args.now ?? new Date()).hour >= INTAKE_CUTOFF_HOUR_IL;
  const promise = 'עד 17:00 ביום שלפני האספקה נשלח לכם מה יוצא בפועל ואת יום האספקה.';
  const change = afterCutoff
    ? 'ההזמנה נכנסה לסבב הבא. לשינוי — שלחו עגלה מעודכנת עד 14:00 מחר.'
    : 'לשינוי — שלחו עגלה מעודכנת עד 14:00 היום.';
  return { kind: 'text', body: [head, ...rows, promise, change].join('\n') };
}
```
In `worker.ts`, the three `buildOrderReceipt({ cart, committed… })` calls gain `now: nowDate(deps)`.

- [ ] **Step 4: Docs**

`.env.example` — after `WHATSAPP_AUTO_COMMIT_ENABLED=false` add:
```
# --- Customer notices (spec 2026-09-09). Master switch; DB flags customer_notices_live /
# customer_notices_kinds gate the rest. false => shadow mode (rows, no sends).
WHATSAPP_NOTICES_ENABLED=false
# NOTICES_OBSERVE_WINDOW_DAYS=4
# Staff alerts by email (Resend). Empty key => log only. Default recipient tom@gteveryday.com.
ORDER_INTAKE_ALERT_TO=tom@gteveryday.com
# RESEND_API_KEY=            # same secret the Edge Function uses
# ALERT_EMAIL_FROM=onboarding@resend.dev
# LIONWHEEL_API_KEY / LIONWHEEL_BASE_URL are shared with the poll route.
```
`api/src/order-intake/README.md` — add a section:
```
## Customer notices (shadow since <deploy date>)

`notices/` turns picked orders into WhatsApp template messages: `confirmed_full` (auto when LionWheel `/tasks/show` says `pick_status=PICKED` and `pickup_at` is set), `confirmed_partial` (human approval via `POST /api/v1/mutations/customer-notices/:id/approve`, listed by `GET /api/v1/queries/customer-notices?state=pending_approval`), `delivered` (task COMPLETED, POD photo header when present), `credit_issued` (credit_task CREDITED with a GI document).
Tick: `POST /api/v1/internal/jobs/customer-notices-tick` every 15 min (pg_cron `customer_notices_tick`). Health: `GET /api/v1/internal/jobs/customer-notices-health`.
Gates: env `WHATSAPP_NOTICES_ENABLED` (master, default false) → `feature_flags.customer_notices_live` (`enabled` + `value.allowlist`) → `customer_notices_kinds`. Off ⇒ rows land in state `shadow`; nothing reaches a customer.
Evidence for the shadow week: `order_intake.lw_pick_observations`; stats: `order_intake.v_customer_notice_stats`.
Reminder email to Tom 16:30 + 07:30 (Edge job `customer_notice_reminder`). Spec: brain `docs/superpowers/specs/2026-09-09-whatsapp-customer-notices-design.md`.
```
Also update the "What the bot says" table row for the catalog cart: reply = receipt with the day-before promise (no more "מאשרים אצלנו").

- [ ] **Step 5: Full verification**

```bash
npx vitest run api/src/order-intake        # expect all green; report N/N
npm run typecheck                          # clean
cd supabase/functions/factory_os_jobs && deno check index.ts && cd -
```

- [ ] **Step 6: Commit and push**

```bash
git add api/src/order-intake/whatsapp/messages.ts api/src/order-intake/whatsapp/__tests__/messages.test.ts api/src/order-intake/worker.ts .env.example api/src/order-intake/README.md
git commit -m "feat(notices): receipt carries the day-before promise; docs and env example"
git push -u origin claude/father-order-entry-permissions-i8q3ud
```
Open a **draft PR** to `main` titled `feat(notices): WhatsApp customer notices — backend, shadow mode` (body: spec link, what ships, flags default off, tests N/N, pgTAP result, rollback = unschedule the two cron jobs), then call `unsubscribe_pr_activity` immediately (brain §Watching).

- [ ] **Step 7: Release (autonomous when gates are green; announce one line first)**

1. CI green on the PR; `pg_prove` 16/16 against prod-like DB (or the migration applied cleanly by the deploy workflow).
2. Merge (squash), then dispatch `deploy-production.yml` with `confirm=APPLY`, `migrations=db/migrations/0350_*.sql`.
3. Supabase: `supabase functions deploy factory_os_jobs` (Edge reminder job) — or via the MCP `deploy_edge_function` with the file content.
4. Railway env: confirm `JOB_RUNNER_TOKEN`, `LIONWHEEL_API_KEY` present; add `RESEND_API_KEY` (same value as the Supabase secret) and `ORDER_INTAKE_ALERT_TO=tom@gteveryday.com`. `WHATSAPP_NOTICES_ENABLED` stays unset.
5. Post-deploy health: `GET /webhooks/wa-order-bot/health` shows `notices_master_enabled:false`; `GET /api/v1/internal/jobs/customer-notices-health` (bearer) returns `ok:true`; within 20 min `select count(*) from order_intake.lw_pick_observations` > 0 and `select kind, state, count(*) from order_intake.customer_notices group by 1,2` shows `shadow` / `pending_approval` rows only; `select cron.jobname from cron.job where jobname like 'customer_notice%'` returns both jobs.
6. Forced reminder run (Task 13 §Verify) → one email to Tom.

---

## Self-review (done at plan time)

**Spec coverage.** §1 promises → receipt (T15), confirmed (T9/T12), delivered (T9). §2 facts → T5 `/show` reader, T8 decisions, observations table (T1/T9). §3 station 1 → T15; 2א → T8/T9; 2ב → T1 lines constraint, T12 API, T13 email (portal tab = Plan 2); 3 → T9 delivered + photo header (T3/T4); 3ב → T9 credited; 8/9 → Plan 3; "usual order" → Plan 3; LionWheel native alerts → no code. §4 data model → T1 (+ `header_image_url`, `delivery_date` columns the spec implied). §5 tick order, flags, status webhooks → T9, T1 flags, T10. §6 quiet hours (T2), one promise per order (dedupe T1/T7), cancel after confirm (T9 alert), no price (T3 test), Hebrew, idempotent ticks (T9 test), versioned templates (`_v1`). §7 consent columns (T1); opt-out handling → Plan 3. §8 staff alerts (T14), kinds `wants_call`, `customer_reply_after_notice` (renamed from the spec's `customer_reply_after_delivery` because the confirmed message invites replies too), `notice_send_failed`, `confirmed_then_changed` (T9/T10). §9 stats view (T1), health (T11). §10 A1 evidence (observations), A7 checked live 2026-09-09 (205/205 mapped rows carry a Shopify id). §12 P0 prerequisites (templates in Meta, catalog codes) are Tom/Cowork tasks outside this plan; P1 shadow is this plan's release.

**Placeholder scan.** No TBD/TODO. Every code step carries the code. The one "verify live" (Shopify `name:` filter, T6) has a stated fallback and test change.

**Type consistency.** `NoticeStore` methods used in T9/T10/T11/T12 all exist in T7's interface; `TickDeps` fields in T11's server wiring match T9; `AlertKind` values used in T9/T10 exist in T14; `buildConfirmedTemplate(lines, ymd, now)` signature identical in T3/T9/T12; `sendTemplate(to, { name, language, bodyParams, headerImageUrl })` identical in T4/T9; `NormalizedStatus.error_code` (T10) consumed by `applyStatus(id, status, errorCode)` (T7).

**Not in this plan (deliberate):** portal tab (Plan 2); `הסר` opt-out, second-cart-as-update, "usual order" multi-product reply, stations 8/9 (Plan 3); feeding day-before shortages into `credit_tasks` (separate Tom decision); LionWheel webhooks; pickup_at-change detection after a confirmed send (observing stops once confirmed — v1.1).
