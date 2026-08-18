# GT Sales Workspace v2 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (or superpowers:subagent-driven-development) to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Follow the plan exactly; if it is wrong, STOP and say so — do not improvise (masterprompt §7).

**Goal:** Turn the live v1 sales workspace (188 real leads, one heavy user) into a system three people can run daily: a queue with a shape Tom controls, assignment that actually delivers leads to a second person, an admin surface that controls instead of watches, and a visual pass that survives the 40th repetition — closing every CONFIRMED P0 of the Phase 0 audit.

**Architecture:** Additive-only on the v1 foundation. Four backend migrations (0324–0327: invariant closure + IL-time defaults, validated/bulk assignment, queue-shape + settings audit + attention views, cross-lead activity) feed extended admin-gated Fastify endpoints; six portal tranches (164–169) rebuild the Today queue as a capped, ranked commitment, wire per-agent scoping end to end, add the admin attention/people/controls surfaces inside the existing `(sales)` route group, then run the visual/a11y pass. All UI stays under `[data-app="sales"]` / `--s-*` tokens; PII lock (service_role-only) unchanged.

**Tech Stack:** Postgres 17 (Supabase) · pgTAP · Fastify + Zod + Kysely-style `sql` tag · Next.js 15 App Router · TanStack Query · shadcn/ui + Tailwind 3.4 · Playwright + vitest.

**Audit basis:** `docs/audits/2026-08-18-sales-workspace-v2-audit.md` (this repo). Finding IDs (P0-1…P0-7, P1-1…P1-19, INF-1…3) refer to it.

## Global Constraints

- `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` stays `false`. Nothing is ever sent to a lead or customer. Resend/Meta work is Phase 3 only (§9 of the masterprompt), with Tom, after this plan lands.
- `stock_ledger` / `balance_anchors` / factory-os core schema: never touched, not read, not written.
- PII lock: every new view granted to `service_role` only; every new function `grant execute … to service_role` only; never `to authenticated`. No lead names/phones in commits, PR bodies, or screenshots (crop or use fixture rows).
- Migrations: FR1/FR2 bracket mandatory (list `db/migrations/` immediately before AND after writing each numbered file; new file in between → HALT `contract_failure`). Numbers 0324–0327 are **expected next slots — re-verify at FR1 time**; if taken, take the next free and update every reference in the same commit.
- Portal invariant 1: one tranche per change; every `docs/portal-os/**` artifact registered in `docs/portal-os/registry.md` **in the same commit that creates it** (the guard runs last and burns a 6-min CI cycle otherwise).
- Never touch: `globals.css`, `tailwind.config.ts`, UX-standard files, factory route groups (exception: `src/components/layout/TopBar.tsx` in T169, precedent tranche 163), public `/`.
- RTL: logical properties only; numbers/phones in `<bdi dir="ltr">`. Hebrew UI copy authorized for `/apps` + `(sales)` (portal CLAUDE.md exception row, 2026-08-17).
- All Hebrew copy in this plan is final copy — do not rephrase during execution.
- No AGPL/GPL code. No `git add -A` / `git add .`. Draft PRs, one per repo, on branch `claude/fable-sonnet-planning-v991qw`.
- Backend deploys from `main` via Railway's own integration (lesson 2026-08-18); prod migration apply follows the brain deploy-gates (pre-flight stock-truth check untouched here — sales_core only; CI green; applies cleanly; post-deploy 401-probe health check). Announce one line before apply.
- pgTAP 1.3.3 gotcha: schema-qualified assertion forms take the extra argument (`has_column('sales_core','lead','x','desc')` = 4 args; `has_table('sales_core'::name,'lead'::name)` needs `::name` casts).
- Model: execution on Sonnet per Tom's instruction; this plan assumes zero discovery.

## Decision gates — Tom approves these BY approving this plan

Approving this plan approves the recommended option of each gate. To override, name the gate ID in the approval message.

| ID | Decision | Recommendation (what this plan implements) |
|---|---|---|
| **D1** | §6.1 assignment model A/B/C | **Option C** — `assignee` stays an email string, but writes are validated against an admin-editable roster stored in `sales_core.app_setting` key `assignees` (seeded: `tom@gteveryday.com`). No new role, no `MODULE_TEMPLATE` path, test accounts can never appear (the picker reads the roster, not `app_users`). Erik is added by Tom on the settings screen the day his Supabase account exists; until then his leads are assignable, visible, and filterable. Upgrade path to Option B (real `sales` role) stays open and is NOT built now. |
| **D2** | 39 uncontactable leads (no phone, no email) in the queue | **Exclude from the Today queue** (they cannot be called), keep them in `/sales/leads` under a dedicated filter chip "ללא פרטי קשר" so they are findable and fixable — not silently deleted, not dead weight. |
| **D3** | Queue default order | **`newest_first`** (speed-to-lead: the freshest lead is the most winnable; the 2023 backlog must not be the first card). Admin-flippable to `oldest_first` on the settings screen (queue-shape control, P0-1). |
| **D4** | Three token changes flagged by the visual audit | **Approve all three:** widen `--s-fg-faint` to `220 6% 60%` (light) / `220 6% 42%` (dark); new `--s-danger-quiet: 0 50% 44%` / `0 50% 62%`; `--s-shadow-card` → `0 1px 3px hsl(220 15% 16% / 0.08)`. F17 contrast suite extended, never weakened. |
| **D5** | Where the stuck/slipping view lives | **New 4th screen `/sales/attention`** (Hebrew: "מצב"), admin-only, added to the sales nav for admins. v1's "three screens, no more" was locked before §5 demanded this surface; the alternative (a tab inside /leads) buries Tom's daily question. |
| **D6** | Meta credential timing | **Pull the ask forward:** Tom can issue `META_PAGE_ACCESS_TOKEN` + `RESEND_API_KEY` in parallel with Phase 2 (instructions in §9 of the masterprompt); *wiring* them stays Phase 3. Rationale: the pipe has been empty since 2026-08-09 (P0-6) and Meta deletes at 90 days. |

## Sequencing (by what unblocks a human — masterprompt §4)

```
B1 governance unblock (merge v1 tail)          ── first, everything stacks on it
B2 0324 invariant + IL defaults ─┐
B3 0325 assignment v2            ├─ backend lane (gt-factory-os), serial FR1/FR2
B4 0326 queue shape + attention  │
B5 0327 activity feed            ┘
B6 API layer (schemas/handlers/routes/tests)   ── after B2–B5
B7 portal proxy routes                          ── with B6
T164 queue triage & cap        (U-011: 188 workable tomorrow)   ← needs B4
T165 outcome-loop integrity    (the discipline mechanic holds)  ← needs B2
T166 assignment & people       (U-012: hand leads to Erik)      ← needs B3, D1
T167 admin attention & controls(§5: control without SQL)        ← needs B4, B5
T168 visual + a11y pass        (§8)                             ← after T164–167
T169 shell & CI hygiene        (ops→sales switch P1-19, GAP-030)← independent
then: impeccable audit→polish→harden → /ux-release-gate (≤3 iterations)
```

Estimated effort: ~34 tasks ≈ 12 agent-hours.

---

### Task B1: Merge the v1 governance tail (INF-1)

**Files:** none created — GitHub merges only.

**Interfaces — Produces:** brain `main` contains `docs/gap_registry.md` (GAP-029/030), `docs/lessons_learned.md` (2026-08-18 entries), `docs/superpowers/plans/2026-08-17-sales-workspace-implementation.md`, updated `docs/decisions/modules/sales-declaration.md`; Sales-Machine `main` contains U-011/012/013.

- [ ] **Step 1: Verify and merge brain PR #139** — `tomw200082-collab/gt-factory-os-production-brain` #139 (branch `claude/caveman-mode-oenfxl`). Confirm `mergeable_state` is clean and required checks green, then squash-merge. Authorized: brain CLAUDE.md §Authorization (checks green + verified change) — the PR is docs-only and was verified by the Phase 0 audit (content matches every masterprompt citation).
- [ ] **Step 2: Verify and merge Sales-Machine PR #5** — same repo rules, docs-only (`CURRENT_STATE.md` + evidence).
- [ ] **Step 3: Rebase working branches** — in both repos: `git fetch origin main && git rebase origin/main` on `claude/fable-sonnet-planning-v991qw`. Resolve nothing silently; a conflict in an authority doc → STOP, `contract_failure`.
- [ ] **Step 4: Evidence** — paste both merge SHAs into the execution log; confirm `grep -c GAP-029 docs/gap_registry.md` = 1 on brain `main`.

---

### Task B2: Migration 0324 — close the working-status loophole + Israel-aware defaults (P0-3, P1-1)

**Files:**
- Create: `gt-factory-os/db/migrations/0324_sales_next_touch_integrity.sql`
- Create: `gt-factory-os/db/tests/0324_sales_next_touch_integrity.test.sql`

**Interfaces:**
- Consumes: 0322's `sales_core.lock_lead(uuid)`, `touch_first(uuid)`, `lead`, `lead_event`.
- Produces: `sales_core.next_business_touch(p_days integer) returns timestamptz` · `sales_core.set_lead_status(p_lead_id uuid, p_status text, p_reason text, p_actor text, p_next_touch_at timestamptz default null)` (old 4-arg signature DROPPED — B6 updates the one caller in the same deploy) · `record_outcome` defaults via `next_business_touch`.

- [ ] **Step 1: FR1** — `ls gt-factory-os/db/migrations/` ; confirm `0324_*` free and no unexpected new file. Collision → HALT `contract_failure`.
- [ ] **Step 2: Write the failing pgTAP test** — `db/tests/0324_sales_next_touch_integrity.test.sql` (fixture UUID prefix `66666666-*`, self-contained, begin/rollback):

```sql
-- ===========================================================================
-- 0324_sales_next_touch_integrity.test.sql
--   pg_prove -d "$DATABASE_URL" db/tests/0324_sales_next_touch_integrity.test.sql
-- ===========================================================================
begin;
create extension if not exists pgtap;
select plan(10);

-- structure
select has_function('sales_core'::name, 'next_business_touch'::name, array['integer']::name[]);

-- next_business_touch semantics (pin via explicit weekday math, not wall clock):
-- rolled result is never Fri/Sat in Israel time, and lands at 09:00 IL.
select ok(
  (select extract(isodow from (sales_core.next_business_touch(d) at time zone 'Asia/Jerusalem')) not in (5,6)
   from generate_series(0, 9) d
   group by 1 order by 1 limit 1),
  'next_business_touch never lands on Fri/Sat (IL) for offsets 0..9');
select is(
  (select to_char(sales_core.next_business_touch(1) at time zone 'Asia/Jerusalem', 'HH24:MI')),
  '09:00', 'next_business_touch is 09:00 Israel wall-clock regardless of DST');

-- fixtures
insert into sales_core.org  (id, display_name)
values ('66666666-1111-1111-1111-111111111111', 'T0324 fixture org');
insert into sales_core.lead (id, org_id, source, external_id, contact_name, status)
values ('66666666-2222-2222-2222-222222222222',
        '66666666-1111-1111-1111-111111111111', 'test', 't0324-a', 'A', 'new');

-- the loophole is closed: working without a next touch is refused
select throws_like(
  $$ select * from sales_core.set_lead_status(
       '66666666-2222-2222-2222-222222222222'::uuid, 'working', null, 'tester') $$,
  '%SALES_NEXT_TOUCH_REQUIRED%',
  'set_lead_status(working) without any next touch raises');

-- working + explicit next touch in one call succeeds and writes both events
select lives_ok(
  $$ select * from sales_core.set_lead_status(
       '66666666-2222-2222-2222-222222222222'::uuid, 'working', null, 'tester',
       now() + interval '1 day') $$,
  'set_lead_status(working, next_touch) succeeds');
select is(
  (select status from sales_core.lead where id = '66666666-2222-2222-2222-222222222222'),
  'working', 'status moved to working');
select isnt(
  (select next_touch_at from sales_core.lead where id = '66666666-2222-2222-2222-222222222222'),
  null, 'next_touch_at set atomically');
select is(
  (select count(*) from sales_core.lead_event
    where lead_id = '66666666-2222-2222-2222-222222222222'
      and event_type = 'next_touch_set')::int,
  1, 'next_touch_set event written by the combined call');

-- working when the lead ALREADY has a next touch needs no new date
insert into sales_core.lead (id, org_id, source, external_id, contact_name, status, next_touch_at)
values ('66666666-3333-3333-3333-333333333333',
        '66666666-1111-1111-1111-111111111111', 'test', 't0324-b', 'B', 'new', now() + interval '2 days');
select lives_ok(
  $$ select * from sales_core.set_lead_status(
       '66666666-3333-3333-3333-333333333333'::uuid, 'working', null, 'tester') $$,
  'working with a pre-existing next touch needs no new date');

-- lost path unchanged: no next touch needed
select lives_ok(
  $$ select * from sales_core.set_lead_status(
       '66666666-2222-2222-2222-222222222222'::uuid, 'lost', 'לא רלוונטי', 'tester') $$,
  'lost path unaffected');

select * from finish();
rollback;
```

- [ ] **Step 3: Run it, verify it fails** — `pg_prove -d "$DATABASE_URL" db/tests/0324_sales_next_touch_integrity.test.sql` → expected FAIL (`next_business_touch` does not exist; 4-arg throws test passes vacuously red on the 5-arg lives_ok).
- [ ] **Step 4: Write the migration** — `db/migrations/0324_sales_next_touch_integrity.sql`:

```sql
-- ===========================================================================
-- 0324 — sales: close the working-status loophole + Israel-aware touch defaults
-- Audit: docs/audits/2026-08-18-sales-workspace-v2-audit.md P0-3, P1-1 (brain).
-- The "no open lead without a next touch" invariant existed only in
-- record_outcome; set_lead_status('working') was a second, unguarded door.
-- Outcome defaults were 06:00 UTC fixed (DST-naive) and Shabbat-blind.
-- ===========================================================================
begin;

-- N business-days-ish default: N days from now, 09:00 Israel wall-clock,
-- rolled off Fri/Sat (IL weekend) forward to Sunday. DST-correct because the
-- arithmetic happens in the Asia/Jerusalem local frame.
create or replace function sales_core.next_business_touch(p_days integer)
returns timestamptz
language sql stable
as $fn$
  with base as (
    select date_trunc('day', (now() at time zone 'Asia/Jerusalem'))
           + make_interval(days => p_days, hours => 9) as il_naive
  ), rolled as (
    select case extract(isodow from il_naive)
             when 5 then il_naive + interval '2 days'   -- Friday  -> Sunday
             when 6 then il_naive + interval '1 day'    -- Saturday-> Sunday
             else il_naive
           end as il_final
    from base
  )
  select il_final at time zone 'Asia/Jerusalem' from rolled
$fn$;

-- set_lead_status v2: 'working' must leave the lead with a next touch —
-- either one it already has, or one passed in this call (set atomically,
-- with its own next_touch_set event). Old 4-arg signature dropped so the
-- default-arg call form stays unambiguous.
drop function if exists sales_core.set_lead_status(uuid, text, text, text);

create or replace function sales_core.set_lead_status(
  p_lead_id       uuid,
  p_status        text,
  p_reason        text,
  p_actor         text,
  p_next_touch_at timestamptz default null
) returns table (lead_id uuid, status text)
language plpgsql
as $fn$
declare
  v_lead sales_core.lead;
begin
  v_lead := sales_core.lock_lead(p_lead_id);

  if p_status = 'won' then
    raise exception 'SALES_WON_IS_EVIDENCE_ONLY' using errcode = 'P0001';
  end if;
  if p_status not in ('working','lost') then
    raise exception 'SALES_INVALID_STATUS: %', p_status using errcode = 'P0001';
  end if;
  if p_status = 'lost' and (p_reason is null or p_reason = '') then
    raise exception 'SALES_LOST_REQUIRES_REASON' using errcode = 'P0001';
  end if;
  if p_status = 'working' and v_lead.next_touch_at is null and p_next_touch_at is null then
    raise exception 'SALES_NEXT_TOUCH_REQUIRED: working lead needs a next touch'
      using errcode = 'P0001';
  end if;

  update sales_core.lead
     set status      = p_status,
         lost_reason = case when p_status = 'lost' then p_reason else lost_reason end
   where id = p_lead_id;

  insert into sales_core.lead_event (lead_id, event_type, payload, actor)
  values (p_lead_id, 'status_change',
          jsonb_build_object('from', v_lead.status, 'to', p_status, 'reason', p_reason),
          p_actor);

  if p_status = 'working' and p_next_touch_at is not null then
    update sales_core.lead set next_touch_at = p_next_touch_at where id = p_lead_id;
    insert into sales_core.lead_event (lead_id, event_type, payload, actor)
    values (p_lead_id, 'next_touch_set', jsonb_build_object('at', p_next_touch_at), p_actor);
  end if;

  perform sales_core.touch_first(p_lead_id);

  return query select l.id, l.status from sales_core.lead l where l.id = p_lead_id;
end;
$fn$;

-- record_outcome: same body as 0322 except the two default lines now read
-- (diff shown here in full for the executor — replace the v_next assignment):
--   v_next := coalesce(
--     p_next_touch_at,
--     case p_result
--       when 'no_answer'     then sales_core.next_business_touch(1)
--       when 'whatsapp_sent' then sales_core.next_business_touch(2)
--     end);
-- Re-CREATE OR REPLACE the full function with ONLY that change: copy the
-- 0322 body verbatim (db/migrations/0322_sales_core_workspace_writes.sql,
-- function record_outcome) and substitute the coalesce block. Do not alter
-- any other line — the invariant check and event writes stay byte-identical.

-- [EXECUTOR: paste the full record_outcome from 0322 here with the
--  substituted coalesce block. It is 70 lines; copying it into this plan
--  twice risks drift — the 0322 file is the source of truth for the body.]

do $$
begin
  if exists (select 1 from pg_roles where rolname = 'service_role') then
    grant execute on function sales_core.next_business_touch(integer) to service_role;
    grant execute on function sales_core.set_lead_status(uuid, text, text, text, timestamptz) to service_role;
  end if;
end $$;

commit;
```

  Note to executor: the `[EXECUTOR: …]` block above is an instruction, not a placeholder to ship — the migration is complete only when the full `record_outcome` body (copied from 0322, with the two-line default change) is inline. `grep -c 'next_business_touch' 0324_*.sql` must be ≥ 3 in the final file.
- [ ] **Step 5: Run pgTAP** — `pg_prove -d "$DATABASE_URL" db/tests/0324_sales_next_touch_integrity.test.sql` → 10/10. Also re-run 0322's suite (`pg_prove db/tests/0322_*.test.sql`) — the changed functions must keep it green (the 0322 test calls 4-arg `set_lead_status` positionally, which still resolves to the 5-arg function's defaults).
- [ ] **Step 6: FR2** — re-list `db/migrations/`; a new file appeared → HALT `contract_failure`.
- [ ] **Step 7: Commit** — `git add db/migrations/0324_sales_next_touch_integrity.sql db/tests/0324_sales_next_touch_integrity.test.sql && git commit -m "feat(sales): 0324 — working status requires a next touch; IL-aware outcome defaults"`

---

### Task B3: Migration 0325 — assignment v2: roster-validated, atomic due date, bulk (P0-2, P1-2, D1)

**Files:**
- Create: `gt-factory-os/db/migrations/0325_sales_assignment_v2.sql`
- Create: `gt-factory-os/db/tests/0325_sales_assignment_v2.test.sql`

**Interfaces:**
- Consumes: `lock_lead`, `lead_event`, `app_setting`, B2's conventions.
- Produces: `app_setting` key `assignees` (jsonb array of `{email, name, active}`) · `sales_core.assign_lead(p_lead_id uuid, p_assignee text, p_actor text, p_next_touch_at timestamptz default null)` (old 3-arg DROPPED; validates against active roster; `''`/null → unassign, always allowed) · `sales_core.bulk_assign(p_lead_ids uuid[], p_assignee text, p_actor text, p_next_touch_at timestamptz default null) returns table(lead_id uuid, assignee text)` (≤200 ids, one transaction).

- [ ] **Step 1: FR1** (as B2 Step 1; slot 0325).
- [ ] **Step 2: Failing pgTAP** — `db/tests/0325_sales_assignment_v2.test.sql`, prefix `77777777-*`, `plan(12)`; assertions: `assignees` seed exists containing `tom@gteveryday.com`; `throws_like` unknown assignee → `%SALES_UNKNOWN_ASSIGNEE%`; assign to roster member `lives_ok` + column set + `assignment` event payload carries assignee AND `next_touch_at` when given; assign with `p_next_touch_at` sets `lead.next_touch_at` + writes `next_touch_set`; unassign via `''` → null, allowed even though `''` is not in roster; `bulk_assign` over 3 fixture leads returns 3 rows, writes 3 assignment events, one shared timestamp transaction; `bulk_assign` with 201 ids → `%SALES_BULK_LIMIT%`; inactive roster member (`active:false`) → `%SALES_UNKNOWN_ASSIGNEE%`. Test code follows the 0324 template exactly (begin/pgtap/plan/fixtures/finish/rollback).
- [ ] **Step 3: Run → FAIL** (functions absent).
- [ ] **Step 4: Migration**:

```sql
-- ===========================================================================
-- 0325 — sales: assignment v2 — roster-validated, atomic due date, bulk
-- Audit P0-2 / P1-2; masterprompt §6.1 Option C (decision gate D1).
-- assignee stays a text email, but every write is validated against the
-- admin-editable roster in app_setting('assignees'). Test accounts can never
-- be assigned because the roster is curated, not derived from app_users.
-- ===========================================================================
begin;

insert into sales_core.app_setting (key, value, updated_at)
values ('assignees',
        jsonb_build_array(jsonb_build_object(
          'email', 'tom@gteveryday.com', 'name', 'תום', 'active', true)),
        now())
on conflict (key) do nothing;

create or replace function sales_core.assert_assignee(p_assignee text)
returns void
language plpgsql stable
as $fn$
begin
  if p_assignee is null or p_assignee = '' then
    return; -- unassign is always legal
  end if;
  if not exists (
    select 1
    from jsonb_array_elements(
           (select value from sales_core.app_setting where key = 'assignees')) a
    where a->>'email' = p_assignee and coalesce((a->>'active')::boolean, false)
  ) then
    raise exception 'SALES_UNKNOWN_ASSIGNEE: %', p_assignee using errcode = 'P0001';
  end if;
end;
$fn$;

drop function if exists sales_core.assign_lead(uuid, text, text);

create or replace function sales_core.assign_lead(
  p_lead_id       uuid,
  p_assignee      text,
  p_actor         text,
  p_next_touch_at timestamptz default null
) returns table (lead_id uuid, assignee text)
language plpgsql
as $fn$
begin
  perform sales_core.lock_lead(p_lead_id);
  perform sales_core.assert_assignee(p_assignee);

  update sales_core.lead set assignee = nullif(p_assignee, '') where id = p_lead_id;

  insert into sales_core.lead_event (lead_id, event_type, payload, actor)
  values (p_lead_id, 'assignment',
          jsonb_build_object('assignee', nullif(p_assignee, ''),
                             'next_touch_at', p_next_touch_at),
          p_actor);

  if p_next_touch_at is not null then
    update sales_core.lead set next_touch_at = p_next_touch_at where id = p_lead_id;
    insert into sales_core.lead_event (lead_id, event_type, payload, actor)
    values (p_lead_id, 'next_touch_set', jsonb_build_object('at', p_next_touch_at), p_actor);
  end if;

  return query select l.id, l.assignee from sales_core.lead l where l.id = p_lead_id;
end;
$fn$;

create or replace function sales_core.bulk_assign(
  p_lead_ids      uuid[],
  p_assignee      text,
  p_actor         text,
  p_next_touch_at timestamptz default null
) returns table (lead_id uuid, assignee text)
language plpgsql
as $fn$
declare
  v_id uuid;
begin
  if array_length(p_lead_ids, 1) is null then
    raise exception 'SALES_BULK_EMPTY' using errcode = 'P0001';
  end if;
  if array_length(p_lead_ids, 1) > 200 then
    raise exception 'SALES_BULK_LIMIT: max 200 leads per call' using errcode = 'P0001';
  end if;
  perform sales_core.assert_assignee(p_assignee);

  foreach v_id in array p_lead_ids loop
    perform sales_core.assign_lead(v_id, p_assignee, p_actor, p_next_touch_at);
  end loop;

  return query
    select l.id, l.assignee from sales_core.lead l where l.id = any(p_lead_ids);
end;
$fn$;

do $$
begin
  if exists (select 1 from pg_roles where rolname = 'service_role') then
    grant execute on function sales_core.assert_assignee(text) to service_role;
    grant execute on function sales_core.assign_lead(uuid, text, text, timestamptz) to service_role;
    grant execute on function sales_core.bulk_assign(uuid[], text, text, timestamptz) to service_role;
  end if;
end $$;

commit;
```

- [ ] **Step 5: pgTAP 12/12; re-run 0322 suite green.**
- [ ] **Step 6: FR2.**
- [ ] **Step 7: Commit** — `git commit -m "feat(sales): 0325 — roster-validated assignment, atomic due date, bulk (≤200)"` (add the two files explicitly).

---

### Task B4: Migration 0326 — queue shape, editable lost reasons, settings audit, attention views (P0-1, P0-5, P1-7, P1-8, D2, D3)

**Files:**
- Create: `gt-factory-os/db/migrations/0326_sales_queue_shape_and_attention.sql`
- Create: `gt-factory-os/db/tests/0326_sales_queue_shape_and_attention.test.sql`

**Interfaces:**
- Consumes: `app_setting`, `v_sales_today` / `v_sales_week_stats` definitions from 0323, `sales_core.sla_hours()`.
- Produces:
  - `app_setting` keys: `queue` = `{"daily_cap": 15, "order": "newest_first"}` · `lost_reasons` = the current `labels.ts` list as a jsonb string array `["אין מענה ממושך","לא רלוונטי","מחיר","עסק סגור","כפילות","אחר"]` **← executor: copy the array VERBATIM from `gt-factory-os-portal/src/app/(sales)/_lib/labels.ts:63-69` at execution time; the list here is illustrative and labels.ts wins.**
  - `sales_core.setting_event` (append-only audit: `id uuid pk default gen_random_uuid()`, `key text`, `old_value jsonb`, `new_value jsonb`, `actor text`, `created_at timestamptz default now()`; UPDATE/DELETE-blocking trigger copied from 0320's pattern).
  - `sales_core.set_app_setting(p_key text, p_value jsonb, p_actor text)` (old 2-arg DROPPED) — upserts AND writes `setting_event`.
  - `api_read.v_sales_today` v2: adds `age_days int`, `uncontactable boolean` (phone_e164 null AND email null); WHERE additionally excludes uncontactable rows from the `new_lead` branch (D2) — they stay visible in `v_sales_leads` which gains the same two columns.
  - `api_read.v_sales_week_stats` v2: adds `overdue_count` (open leads, `next_touch_at < now()`), `unassigned_open_count`, `never_contacted_count` (untouched new, contactable), `uncontactable_count`.
  - `api_read.v_sales_attention`: lead-level rows for the admin screen — every open lead that is (a) `next_touch_at < now()` (bucket `'overdue'`), or (b) unassigned & untouched ≥ 3 days (bucket `'unowned'`), or (c) `status='working'` with no event in 14 days (bucket `'stalled'`); columns `lead_id, org_name, contact_name, phone_e164, assignee, status, bucket, days_stuck int, next_touch_at, last_event_at`. Grant SELECT to service_role only.
- [ ] **Step 1: FR1.**
- [ ] **Step 2: Failing pgTAP** — `plan(16)`, prefix `88888888-*`: seeds exist (`queue`, `lost_reasons`); `setting_event` exists + `throws_like` on UPDATE (`%append%`); `set_app_setting('sla_hours', …, 'tester')` writes a `setting_event` row with old+new; `v_sales_today` has `age_days`/`uncontactable` columns (`has_column` 4-arg form); an uncontactable fixture lead (no phone/email) is absent from `v_sales_today` but present in `v_sales_leads` with `uncontactable=true`; `v_sales_week_stats` returns the four new counts with fixture-predicted values; `v_sales_attention` buckets one overdue fixture as `'overdue'`, one 4-day-old unassigned as `'unowned'`, and excludes a healthy lead.
- [ ] **Step 3: Run → FAIL.**
- [ ] **Step 4: Migration** — full SQL. View bodies: start from the 0323 file's `create or replace view` blocks (copy verbatim), then apply exactly these diffs — today: add `(now()::date - l.created_at::date) as age_days`, `(l.phone_e164 is null and l.email is null) as uncontactable`, and extend the WHERE's second branch to `l.status = 'new' and l.first_touch_at is null and not (l.phone_e164 is null and l.email is null)`; week_stats: append the four counts as scalar subselects following the existing three's style; attention: new view, one `union all` per bucket over `sales_core.lead` joined to `org` + a lateral `max(created_at) last_event_at` on `lead_event` (same lateral shape 0323 already uses for `converted_at`). `setting_event` trigger: copy 0320's `lead_event`-guard trigger block, rename to `setting_event_append_only`. Grants: `grant select on api_read.v_sales_attention to service_role;` and re-grant `execute` on the 3-arg `set_app_setting`.
- [ ] **Step 5: pgTAP 16/16; re-run 0322/0323 suites — 0323's view assertions must still pass (columns only added, none removed).**
- [ ] **Step 6: FR2.**
- [ ] **Step 7: Commit** — `git commit -m "feat(sales): 0326 — queue shape settings, editable lost reasons, settings audit, attention views"`.

---

### Task B5: Migration 0327 — cross-lead activity feed (admin-F7)

**Files:**
- Create: `gt-factory-os/db/migrations/0327_sales_activity_feed.sql`
- Create: `gt-factory-os/db/tests/0327_sales_activity_feed.test.sql`

**Interfaces — Produces:** `api_read.v_sales_activity`: last-events-across-all-leads — `event_id, lead_id, org_name, contact_name, event_type, payload, actor, created_at`, ordered `created_at desc`, no LIMIT (the handler limits). service_role SELECT only.

- [ ] **Step 1: FR1.** 
- [ ] **Step 2: Failing pgTAP** — `plan(5)`: view exists; returns fixture events newest-first; carries org_name join; excludes nothing (count matches `lead_event` fixture count); grant check via `has_table_privilege('service_role','api_read.v_sales_activity','select')`.
- [ ] **Step 3: FAIL → Step 4: Migration** (single `create or replace view` — `select e.id as event_id, e.lead_id, o.display_name as org_name, l.contact_name, e.event_type, e.payload, e.actor, e.created_at from sales_core.lead_event e join sales_core.lead l on l.id = e.lead_id join sales_core.org o on o.id = l.org_id order by e.created_at desc` + grant) → **Step 5: 5/5** → **Step 6: FR2** → **Step 7: Commit** `"feat(sales): 0327 — cross-lead activity feed for the admin audit trail"`.

---

### Task B6: API layer — schemas, handlers, routes, tests

**Files:**
- Modify: `gt-factory-os/api/src/sales/schemas.ts`
- Modify: `gt-factory-os/api/src/sales/queries_handler.ts`
- Modify: `gt-factory-os/api/src/sales/mutations_handler.ts`
- Modify: `gt-factory-os/api/src/sales/route.ts`
- Test: `gt-factory-os/api/test/sales_v2.test.ts` (new; pattern-match the existing `api/test/sales_*.test.ts` suite style — tsx --test, serial)

**Interfaces:**
- Consumes: B2–B5 functions/views by exact signature.
- Produces (portal relies on these paths and shapes):
  - `GET /api/v1/queries/sales/today` — unchanged path; now reads `app_setting.queue` and applies `order` (`newest_first` → `coalesce(next_touch_at, created_at) desc` inside each item_type group; `oldest_first` → current `asc`); still accepts `?assignee=`; response gains `queue: {daily_cap, order}` alongside `rows` (cap is applied by the portal, not the server — the server returns all rows so the "עוד X ממתינים" count is truthful).
  - `GET /api/v1/queries/sales/attention` → `{rows: AttentionRow[]}` from `v_sales_attention` (limit 500).
  - `GET /api/v1/queries/sales/activity?limit=` → `{rows: ActivityRow[]}` (default 100, max 300).
  - `POST /api/v1/mutations/sales/leads/bulk-assign` body `{lead_ids: string[] (1..200 uuids), assignee: string, next_touch_at?: iso}` → `sales_core.bulk_assign`.
  - `POST /api/v1/mutations/sales/leads/:lead_id/assign` body gains optional `next_touch_at` → 4-arg `assign_lead`.
  - `POST /api/v1/mutations/sales/leads/:lead_id/status` body gains optional `next_touch_at` → 5-arg `set_lead_status`.
  - `PUT /api/v1/mutations/sales/settings` accepts new optional keys `lost_reasons: string[] (1..30 items, each 1..60 chars)`, `queue: {daily_cap: int 1..100, order: enum}`, `assignees: {email: string.email, name: string 1..60, active: boolean}[] (≤20)`; every `set_app_setting` call passes `actorOf(session)`.
  - `GET /api/v1/queries/sales/settings` returns the new keys too, plus `last_changes: {key: string, actor: string, at: string}[]` — the newest `sales_core.setting_event` row per key (`select distinct on (key) key, actor, created_at as at from sales_core.setting_event order by key, created_at desc`). T167 renders it.
- Zod additions to `schemas.ts` (verbatim):

```ts
export const bulkAssignBodySchema = z.object({
  lead_ids: z.array(z.string().uuid()).min(1).max(200),
  assignee: z.string(),
  next_touch_at: isoDateTime.nullable().optional(),
});

export const assignBodySchema = z.object({
  assignee: z.string(),
  next_touch_at: isoDateTime.nullable().optional(),
});

export const statusBodySchema = z.object({
  status: z.enum(['working', 'lost']),
  reason: z.string().nullable().optional(),
  next_touch_at: isoDateTime.nullable().optional(),
});

export const assigneeEntrySchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(60),
  active: z.boolean(),
});

export const settingsPutBodySchema = z.object({
  sla_hours: z.number().int().min(1).max(168).optional(),
  whatsapp_templates: z
    .object({
      new_lead: z.string(),
      reminder: z.string(),
      returning_customer: z.string(),
    })
    .optional(),
  lost_reasons: z.array(z.string().min(1).max(60)).min(1).max(30).optional(),
  queue: z
    .object({
      daily_cap: z.number().int().min(1).max(100),
      order: z.enum(['newest_first', 'oldest_first']),
    })
    .optional(),
  assignees: z.array(assigneeEntrySchema).max(20).optional(),
});

export const activityQuerySchema = z.object({
  limit: z.coerce.number().int().min(1).max(300).default(100),
});
```

- [ ] **Step 1: Write failing tests** — `api/test/sales_v2.test.ts`, following the existing suite's harness (import pattern, db bootstrap, serial). Name every test:
  `bulk-assign rejects >200 ids (400)` · `bulk-assign unknown assignee → 422 SALES_UNKNOWN_ASSIGNEE` · `bulk-assign happy path assigns 3 and writes events` · `assign with next_touch_at sets both atomically` · `status working without next touch on untouched lead → 422 SALES_NEXT_TOUCH_REQUIRED` · `status working with next_touch_at succeeds` · `today response carries queue settings and honors order=newest_first` · `today?assignee= scopes to mine-or-unclaimed` · `attention buckets overdue/unowned/stalled` · `activity returns newest-first with limit` · `settings PUT lost_reasons round-trips and writes setting_event` · `settings PUT queue validates daily_cap bounds` · `settings PUT assignees rejects bad email` · `unauth → 401 on every new endpoint (attention, activity, bulk-assign)`.
- [ ] **Step 2: Run → FAIL** — `cd api && npm test` (new file red, existing suite green).
- [ ] **Step 3: Implement** — handlers follow `handleSetStatus`'s exact shape (`requireSalesAccess` → `sql\`select * from sales_core.fn(named => args)\`` → `mapSalesDbError`); queries follow `handleSalesToday`'s shape. `route.ts`: register `GET /queries/sales/attention`, `GET /queries/sales/activity`, `POST /mutations/sales/leads/bulk-assign` beside their siblings; update the header comment block (route.ts:3-11) to list them.
- [ ] **Step 4: Run → ALL green** — `cd api && npm test` (report N/N) and `npm run typecheck` at repo root → 0 errors.
- [ ] **Step 5: Commit** — `git add api/src/sales/schemas.ts api/src/sales/queries_handler.ts api/src/sales/mutations_handler.ts api/src/sales/route.ts api/test/sales_v2.test.ts && git commit -m "feat(sales): v2 API — bulk assign, attention + activity reads, queue-shape settings"`.

---

### Task B7: Portal proxy routes for the three new endpoints

**Files:**
- Create: `gt-factory-os-portal/src/app/api/sales/attention/route.ts`
- Create: `gt-factory-os-portal/src/app/api/sales/activity/route.ts`
- Create: `gt-factory-os-portal/src/app/api/sales/bulk-assign/route.ts`
- Test: covered by T164/T166/T167 Playwright + existing proxy vitest pattern if one exists (check `src/app/api/sales/today/route.test.ts` — if the repo has none, proxies are covered by e2e only, matching v1).

Each file copies the existing `src/app/api/sales/today/route.ts` pattern verbatim (the `apiProxy` helper from `src/lib/api-proxy.ts`), pointing at its backend path; `attention`/`activity` are GET with `forwardQuery: true`; `bulk-assign` is POST. **This task belongs to tranche 166's manifest (portal invariant 1) — commit it with T166.**

---


## Portal tranches — shared conventions

Every tranche below: (1) create `docs/portal-os/tranches/<NNN>-<slug>.md` with Status/Origin/sizing/manifest/checklist in tranche 163's exact format, register it in `docs/portal-os/registry.md`, and set `docs/portal-os/tranches/_active.txt` to `<NNN>` — **all in the tranche's first commit**; (2) the manifest lists every file the tranche touches (the PreToolUse hook rejects writes outside it); (3) per-surface gate before moving on: `npm run typecheck` → 0 · `npx vitest run` → green · the tranche's named Playwright spec → green; (4) final commit clears `_active.txt`. New TanStack hooks go in `_lib/api.ts` following `useToday`'s exact shape (`useQuery` + `fetchJson`); new labels go in `_lib/labels.ts` under the existing `UI` object. T164's first commit also clears the stale `163` from `_active.txt` (fold, per masterprompt §4).

### Task T164: Tranche 164 — queue triage & cap: 188 becomes a workable morning (P0-1, P0-5-strip, P1-3, P1-14, D2, D3)

**Files (the tranche manifest, verbatim):**
```
src/app/(sales)/_lib/api.ts
src/app/(sales)/_lib/labels.ts
src/app/(sales)/_lib/types.ts
src/app/(sales)/_components/TodayQueue.tsx
src/app/(sales)/_components/TodayCard.tsx
src/app/(sales)/_components/SlaBadge.tsx
src/app/(sales)/_components/StatsStrip.tsx
src/app/(sales)/_components/LeadsTable.tsx
src/app/(sales)/sales/leads/page.tsx
src/app/(sales)/_components/EmptyStates.tsx
tests/e2e/sales-queue-triage.spec.ts
src/app/(sales)/_lib/queue.test.ts
docs/portal-os/tranches/164-queue-triage-and-cap.md
docs/portal-os/tranches/_active.txt
docs/portal-os/registry.md
```

**Interfaces:**
- Consumes: B6's `GET /api/sales/today` → `{rows, queue: {daily_cap, order}}`; `v_sales_today.age_days`, `.uncontactable`; week-stats v2 counts.
- Produces: `_lib/queue.ts` logic lives inline in `TodayQueue.tsx` as exported pure helpers `capRows(rows, cap)` and `agedTone(age_days, sla_hours)` (unit-tested in `queue.test.ts`).

- [ ] **Step 1: Failing unit test** — `src/app/(sales)/_lib/queue.test.ts` (vitest):

```ts
import { describe, expect, it } from "vitest";
import { capRows, agedTone } from "../_components/TodayQueue";

describe("capRows", () => {
  it("caps the new_lead section at daily_cap and reports the remainder", () => {
    const rows = Array.from({ length: 40 }, (_, i) => ({ item_type: "new_lead", lead_id: String(i) }));
    const { visible, remaining } = capRows(rows as never, 15);
    expect(visible).toHaveLength(15);
    expect(remaining).toBe(25);
  });
  it("never caps conversions or returning customers", () => {
    const rows = [
      { item_type: "conversion", lead_id: "c1" },
      { item_type: "returning_customer", lead_id: "r1" },
      ...Array.from({ length: 20 }, (_, i) => ({ item_type: "new_lead", lead_id: String(i) })),
    ];
    const { visible } = capRows(rows as never, 5);
    expect(visible.filter(r => r.item_type !== "new_lead")).toHaveLength(2);
  });
});

describe("agedTone", () => {
  it("is muted inside the SLA window and overdue beyond it", () => {
    expect(agedTone(0, 24)).toBe("muted");
    expect(agedTone(3, 24)).toBe("overdue");
  });
});
```

- [ ] **Step 2: Run → FAIL** (`npx vitest run src/app/(sales)/_lib/queue.test.ts` — exports missing).
- [ ] **Step 3: Implement TodayQueue** — export the two helpers; consume `queue.daily_cap` from the `useToday()` response (extend the hook's return type in `_lib/api.ts` and `TodayRow` in `types.ts` with `age_days: number` and `uncontactable: boolean`); the `new_lead` + `due_follow_up` sections render `capRows(..., daily_cap)` and a single sticky footer line per capped section — Hebrew copy (final): `היום: {visible} שיחות · עוד {remaining} ממתינות בתור`. The existing `PAGE=12` show-more stays *inside* the capped set. Section count style: replace the `--s-fg-faint` span (TodayQueue.tsx:63) with `--s-fg-muted`, switching to `--s-sla-overdue` when `rows.length > 10` (named const `SECTION_ALARM_COUNT = 10`).
- [ ] **Step 4: Age & SLA recast** — `TodayCard.tsx`: age line gets `style={{ color: agedTone(row.age_days, slaHours) === "overdue" ? "hsl(var(--s-sla-overdue))" : "hsl(var(--s-fg-muted))" }}` and appends an explicit day count in `<bdi dir="ltr">` — copy (final): `בן {age_days} ימים`. `SlaBadge.tsx`: render **only** the overdue state; `state !== "overdue"` returns `null`; overdue label becomes (final) `עבר זמן · {days} ימים` where `days = age_days` passed as a new optional prop (default omits the suffix so LeadsTable keeps working until its line below).
- [ ] **Step 5: StatsStrip v2** — consume week-stats v2; render (final, one line, `<bdi>` on numbers): `בתור היום: {queue_today} · באיחור: {overdue_count} · ללא בעלים: {unassigned_open_count} · טרם נוצר קשר: {never_contacted_count}` — replacing the 0·0·0 steady-state line (P0-5's strip half; the screen half is T167). Reserve height while loading (`min-h-[20px]`, INTER-015).
- [ ] **Step 6: Leads page: uncontactable chip + sort** — `leads/page.tsx`: add filter chip row above the table with one chip (final copy) `ללא פרטי קשר ({uncontactable_count})` toggling a client filter `row.uncontactable === true`; `LeadsTable.tsx`: (a) mobile card list gets `PAGE=20` + show-more, copying TodayQueue's pattern verbatim (VISUAL-003); (b) age column header becomes a sort toggle (asc/desc on `age_days`, `aria-sort` reflected, RTL-safe — pattern-match the roving-tab logic already in leads/page.tsx:108-120) (INTER-010).
- [ ] **Step 7: Playwright** — `tests/e2e/sales-queue-triage.spec.ts`, provisioning data the same way the existing sales specs do (inspect `tests/e2e/sales-*.spec.ts` for the session/fixture helper and copy it). Named tests: `today caps the new-lead section and shows the remainder line` · `queue order honors newest_first` · `uncontactable leads are absent from today and filterable in leads` · `sla badge appears only on overdue leads` · `stats strip shows the four triage counts`.
- [ ] **Step 8: Gate & commit** — typecheck 0 · vitest green · this spec green. Two commits max: `feat(sales-portal): T164 — capped, ranked today queue + triage strip` then `chore(portal-os): close tranche 164`.

---

### Task T165: Tranche 165 — outcome-loop integrity: every call ends captured (P0-4, P1-4, P1-5, P1-6, P1-9, P1-10, P1-1-preview)

**Files (manifest, verbatim):**
```
src/app/(sales)/_lib/api.ts
src/app/(sales)/_lib/labels.ts
src/app/(sales)/_lib/useOutcomeCapture.ts
src/app/(sales)/_components/OutcomeSheet.tsx
src/app/(sales)/_components/LeadDrawer.tsx
src/app/(sales)/_components/Toast.tsx
src/app/(sales)/sales/leads/page.tsx
src/app/(sales)/sales/today/page.tsx
src/lib/api-proxy.ts
tests/e2e/sales-outcome-integrity.spec.ts
docs/portal-os/tranches/165-outcome-loop-integrity.md
docs/portal-os/tranches/_active.txt
docs/portal-os/registry.md
```

- [ ] **Step 1: Failing Playwright first** — `tests/e2e/sales-outcome-integrity.spec.ts`, named tests: `a call armed on the leads page raises the outcome sheet on the leads page` · `an off-queue lead's outcome is never silently dropped` · `backdrop tap during submit does not dismiss the sheet` · `no-answer shows the scheduled date before submit` · `lost from the drawer with "אחר" requires free text` · `escape with an unsaved note asks before discarding` · `mark-lost shows an undo toast that restores the lead`.
- [ ] **Step 2: OutcomeSheet everywhere it can be armed** — mount `<OutcomeSheet …/>` in `leads/page.tsx` exactly as `today/page.tsx` mounts it, fed by a `pendingRow` looked up from the leads list (`rows.find(r => r.lead_id === capture.pending?.leadId)`); in `today/page.tsx` REPLACE the silent `capture.clear()` branch (lines 59-63) with: keep the intent, resolve the row from `useLeads()` as fallback, and only clear after an outcome is recorded or explicitly dismissed. `useOutcomeCapture.ts`: add `resolveAnywhere: boolean` no — keep the hook API unchanged; the pages own row resolution. Dismissal (backdrop/Escape/close when NOT busy) now also clears the intent explicitly — dropping is allowed only as a visible user choice, never as a side effect of navigation.
- [ ] **Step 3: Busy-guard + optimistic + undo** — `OutcomeSheet.tsx` backdrop: `onClick={(e) => { if (e.target === e.currentTarget && !busy) onDismiss(); }}` (P1-4). `_lib/api.ts`: `useSetNextTouch` gains the same `onMutate` optimistic-remove + rollback the outcome mutation already has (copy that block) (P1-9b). Lost undo: after a `lost` outcome, `Toast` renders an action button (final copy: `בטל`) for 8s which calls `useSetStatus` back to `working` with `next_touch_at: <the lead's pre-lost next_touch_at ?? tomorrow via server default>` and shows (final) `שוחזר` (P1-9a; server-side nothing new — `set_lead_status` 5-arg covers it). `Toast.tsx` gains an optional `action?: {label: string; onAction: () => void}` prop rendered as an `.s-btn s-btn-ghost` 44px button.
- [ ] **Step 4: Date preview on the two quick paths** — `OutcomeSheet.tsx` no_answer / whatsapp_sent buttons: before submit, render under the tapped button one line (final): `המגע הבא: {fmtDate(preview)}` + secondary (final) `שנה תאריך` opening the existing custom-date step. Preview date computed client-side mirroring the server rule — `nextBusinessTouchLocal(days)` helper in `_lib/format.ts`? **No** — manifest excludes format.ts; put `nextBusinessTouchPreview(days: number): Date` inside `OutcomeSheet.tsx` (exported for test): Asia/Jerusalem via `Intl.DateTimeFormat` weekday math, 09:00, Fri/Sat→Sun, matching 0324's SQL semantics. The submitted body still omits `next_touch_at` unless the user changed it — the server remains the source of truth; the preview is a faithful mirror, asserted equal in the e2e test.
- [ ] **Step 5: Drawer parity** — `LeadDrawer.tsx`: (a) lost path becomes the OutcomeSheet's radio pattern incl. free-text for `אחר` (copy the JSX block from OutcomeSheet.tsx:287-311, adapting state names) — the literal string `אחר` must never reach the API (guard: submit disabled until `reason !== "אחר" || otherReason.trim()`); (b) the working-status button now opens an inline required next-touch picker when the lead has none (posting `{status:"working", next_touch_at}` — B6's extended body); (c) Escape/backdrop with dirty note/assignee → `window.confirm` (final copy: `יש שינויים שלא נשמרו — לצאת בכל זאת?`); (d) the three "שמור" buttons get final labels `שמור הערה` / `קבע תאריך` / `שייך`.
- [ ] **Step 6: Honest errors** — `_lib/api.ts` `fetchJson`: on network catch, throw `UI.saveFailed` (final: `השמירה נכשלה — נסה שוב`) when `init?.method && init.method !== "GET"`, else the existing queue error; map 401 → final copy `החיבור פג — רענן את הדף`; `src/lib/api-proxy.ts`: add `code: "AUTH_EXPIRED"` to the 401 JSON body (backward-compatible addition; factory surfaces ignore unknown fields — verify with `npx vitest run src/lib` before commit).
- [ ] **Step 7: Gate & commit** — spec green 7/7 · typecheck 0 · vitest green. Commits: `feat(sales-portal): T165 — outcome capture everywhere, previews, undo, honest errors` + close-tranche commit.

---

### Task T166: Tranche 166 — assignment & people: hand leads to a second person (P0-2, U-012, D1)

**Files (manifest, verbatim):**
```
src/app/(sales)/_lib/api.ts
src/app/(sales)/_lib/labels.ts
src/app/(sales)/_lib/types.ts
src/app/(sales)/_components/LeadDrawer.tsx
src/app/(sales)/_components/LeadsTable.tsx
src/app/(sales)/_components/TodayCard.tsx
src/app/(sales)/_components/SalesShell.tsx
src/app/(sales)/_components/SettingsForm.tsx
src/app/(sales)/_components/AssigneePicker.tsx
src/app/(sales)/_components/BulkBar.tsx
src/app/(sales)/sales/leads/page.tsx
src/app/(sales)/sales/today/page.tsx
src/app/api/sales/attention/route.ts
src/app/api/sales/activity/route.ts
src/app/api/sales/bulk-assign/route.ts
tests/e2e/sales-assignment.spec.ts
docs/portal-os/tranches/166-assignment-and-people.md
docs/portal-os/tranches/_active.txt
docs/portal-os/registry.md
```
(The three proxy routes are B7's files — they land in this tranche's commit; attention/activity proxies ship here dark and light up in T167, keeping B7 to one manifest.)

**Interfaces:**
- Consumes: B6 `bulk-assign`, 4-arg assign, settings `assignees` roster; `GET today?assignee=`.
- Produces: `AssigneePicker` — `({value, onChange, allowUnassign}: {value: string | null; onChange: (email: string | null, nextTouchAt?: string) => void; allowUnassign?: boolean})`, options = `settings.assignees.filter(a => a.active)`, rendered as a `<select className="s-input">` (44px) with a leading (final) `— ללא בעלים —` option when `allowUnassign`. `BulkBar` — sticky bottom bar shown when `selected.size > 0`, props `{count: number; onAssign: (email: string, nextTouchAt?: string) => void; onClear: () => void}`.

- [ ] **Step 1: Failing Playwright** — `tests/e2e/sales-assignment.spec.ts`: `assignee picker offers only the active roster, never test accounts` · `assigning from the drawer requires picking a due date` · `owner chip renders on table rows and today cards` · `my-queue toggle scopes today to my leads plus unclaimed` · `bulk select and assign 3 leads writes 3 events` · `unassigned filter chip shows only ownerless leads`.
- [ ] **Step 2: Roster plumbing** — `_lib/api.ts`: `useSettings` return type gains `assignees: {email: string; name: string; active: boolean}[]`, `queue`, `lost_reasons` (types in `types.ts`); new `useBulkAssign` mutation posting `/api/sales/bulk-assign`, invalidating `["sales","leads"]` + `["sales","today"]`; `useAssign` body gains `next_touch_at`.
- [ ] **Step 3: Picker replaces free text** — `LeadDrawer.tsx`: the bare assignee `<input>` (lines 384-407) is replaced by `<AssigneePicker allowUnassign value={lead.assignee} onChange={(email, at) => assign.mutate({leadId: lead.lead_id, assignee: email ?? "", next_touch_at: at})}/>`; choosing a person opens the same inline next-touch picker T165 added for working-status — due date REQUIRED on assign (final helper copy: `שיוך חייב תאריך מגע — ליד בלי תאריך נרקב`), unassign requires none.
- [ ] **Step 4: Ownership visible** — `LeadsTable.tsx`: new column (final header: `בעלים`) rendering `assigneeName(row.assignee, roster)` — helper in the component mapping email→roster name, falling back to the email's local part; empty → (final) `—` in `--s-fg-faint`. Same chip on `TodayCard.tsx` metadata line. `leads/page.tsx`: filter chips gain (final) `ללא בעלים ({unassigned_open_count})` and one chip per active roster member (name, count computed client-side). Search predicate: add `assignee` to `matchesQuery`'s haystack — **manifest note: that helper lives in `_lib/format.ts`, which is NOT in this manifest — instead filter in `leads/page.tsx` where the rows are already in hand** (`rows.filter(r => chip === "mine" ? r.assignee === session.email : …)`).
- [ ] **Step 5: My-queue toggle** — `SalesShell.tsx` header gains a 44px segmented toggle for admins (final copy: `הכל / שלי`), persisted in `localStorage("sales.queueScope")`; `useToday(scope)` appends `?assignee=${session.email}` when scope==="mine" (`_lib/api.ts`). Today's heading reflects it (final: `התור שלי` / `כל התור`).
- [ ] **Step 6: Bulk** — `LeadsTable.tsx`: leading checkbox column (44px targets, `aria-label` per row final: `בחר ליד`), header checkbox = select page; selection state lifts to `leads/page.tsx`; `BulkBar` renders (final) `{count} נבחרו · שייך ל־` + `AssigneePicker` + optional date + (final) `נקה`; submit calls `useBulkAssign` (≤200 guard client-side too), success toast (final) `שויכו {count} לידים ל{name}`.
- [ ] **Step 7: People on settings** — `SettingsForm.tsx`: new section (final title: `אנשי מכירות`) — list of roster rows (name, email, active switch) + add-row form (name + email inputs, both required, email `type="email"`); writes the whole array via the extended settings PUT; inline error surface reuses the SLA field's pattern. Warning line when deactivating a member who still owns open leads (final: `יש לו {n} לידים פתוחים — שייך אותם קודם`; count from `useLeads` client-side; warn only, do not block).
- [ ] **Step 8: Gate & commit** — spec 6/6 · typecheck 0 · vitest green. Commits: `feat(sales-portal): T166 — roster picker, ownership everywhere, my-queue, bulk assign` + close.

---

### Task T167: Tranche 167 — the admin console: attention, activity, queue shape, lost reasons (P0-5, P1-7, P1-8, D5)

**Files (manifest, verbatim):**
```
src/app/(sales)/_lib/api.ts
src/app/(sales)/_lib/labels.ts
src/app/(sales)/_lib/types.ts
src/app/(sales)/sales/attention/page.tsx
src/app/(sales)/sales/attention/layout.tsx
src/app/(sales)/_components/AttentionList.tsx
src/app/(sales)/_components/ActivityFeed.tsx
src/app/(sales)/_components/SalesShell.tsx
src/app/(sales)/_components/SettingsForm.tsx
src/app/(sales)/_components/OutcomeSheet.tsx
src/app/(sales)/_components/LeadDrawer.tsx
tests/e2e/sales-attention.spec.ts
docs/portal-os/tranches/167-admin-attention-console.md
docs/portal-os/tranches/_active.txt
docs/portal-os/registry.md
```

- [ ] **Step 1: Failing Playwright** — `tests/e2e/sales-attention.spec.ts`: `attention screen buckets overdue, unowned, stalled with counts` · `every attention row opens the lead drawer` · `activity feed shows cross-lead events newest first` · `lost reasons are editable and the outcome sheet reflects the change without redeploy` · `queue shape controls persist and change the today cap` · `settings changes are visibly attributed` (the strip below the form shows last change actor+time from `setting_event` — surfaced via the settings GET gaining `last_changes: {key, actor, at}[]`; **backend note: this needs one line in B6's settings GET handler joining `setting_event` — add it there, it is in B6's file list**).
- [ ] **Step 2: Route** — `sales/attention/page.tsx` + `layout.tsx` (title final: `מצב`), admin-only (the whole group already is), added to `SalesShell` nav arrays — mobile tab bar becomes 4 tabs (final label: `מצב`, icon `Activity` from lucide) and desktop rail likewise.
- [ ] **Step 3: AttentionList** — three collapsible sections (final headers: `באיחור ({n})`, `ללא בעלים ({n})`, `תקועים ({n})`), rows: org name · owner chip · days badge in `<bdi>` (final: `{days} ימ׳`) · one-tap actions `התקשר` + open-drawer; consumes `useAttention()` (`_lib/api.ts` → `/api/sales/attention`). Empty state (final, authored): `אין תקועים. ככה זה צריך להיראות.` Rows reuse the existing `LeadDrawer` by lifting the open-lead state to the page (pattern: leads/page.tsx).
- [ ] **Step 4: ActivityFeed** — bottom section (final header: `פעילות אחרונה`), `useActivity(limit=50)`, rows rendered with `EventTimeline`'s row visual language (timestamp `<bdi>`, actor, Hebrew event labels from the existing `EVENT_LABELS` map in labels.ts — extend it with any missing types, final: `assignment: "שויך"`, `outcome: "תוצאה"`, `outreach: "יצירת קשר"` if absent).
- [ ] **Step 5: Lost reasons + queue shape land in settings** — `SettingsForm.tsx`: section (final title: `סיבות אבוד`) — editable list (add/remove/rename rows) writing `lost_reasons` via settings PUT; `OutcomeSheet.tsx` + `LeadDrawer.tsx` switch from the `LOST_REASONS` const to `useSettings().lost_reasons` (keep the const as fallback while loading; the `"אחר"` free-text rule keys on the LAST list item rather than the literal — final rule: the last reason in the list always takes free text, labeled in settings UI (final hint): `הסיבה האחרונה תמיד פותחת שדה חופשי`). Queue-shape section (final title: `צורת התור`): daily-cap number input (1–100) + order radio (final labels: `חדשים קודם` / `ישנים קודם`), writing `queue` via PUT — this is P0-1's knob, Tom-owned.
- [ ] **Step 6: Gate & commit** — spec 6/6 · typecheck 0 · vitest green. Commits: `feat(sales-portal): T167 — attention console, activity feed, tom-owned queue shape + lost reasons` + close.

---

### Task T168: Tranche 168 — the visual & a11y pass (P0-7, P1-11..P1-18, VISUAL-*, A11Y-*, D4)

Load `/frontend-design` + `/ui-ux-pro-max` before this tranche's first edit; `impeccable` runs after it (execution protocol below). Scope: `sales-tokens.css` + `(sales)` components only; F17 suite extended, never weakened.

**Files (manifest, verbatim):**
```
src/app/(sales)/sales-tokens.css
src/app/(sales)/sales-tokens.test.ts
src/app/(sales)/_components/TodayCard.tsx
src/app/(sales)/_components/TodayQueue.tsx
src/app/(sales)/_components/OutcomeSheet.tsx
src/app/(sales)/_components/LeadDrawer.tsx
src/app/(sales)/_components/LeadsTable.tsx
src/app/(sales)/_components/OrgCard.tsx
src/app/(sales)/_components/SalesShell.tsx
src/app/(sales)/_components/SettingsForm.tsx
src/app/(sales)/_components/QuickAddSheet.tsx
src/app/(sales)/_components/EmptyStates.tsx
src/app/(sales)/_components/CustomerBadge.tsx
src/app/(sales)/_components/EventTimeline.tsx
src/app/(sales)/_components/StatsStrip.tsx
tests/e2e/sales-visual-a11y.spec.ts
docs/portal-os/tranches/168-visual-a11y-pass.md
docs/portal-os/tranches/_active.txt
docs/portal-os/registry.md
```

- [ ] **Step 1: Token changes first, tests in the same edit** (D4): `--s-fg-faint: 220 6% 60%` (light block) / `220 6% 42%` (dark block); add `--s-danger-quiet: 0 50% 44%` / `0 50% 62%` + point `.s-btn-danger-quiet { color: hsl(var(--s-danger-quiet)); }`; `--s-shadow-card: 0 1px 3px hsl(220 15% 16% / 0.08)`. `sales-tokens.test.ts`: add the `--s-danger-quiet` pair to the contrast matrix (≥4.5:1 vs surface, both themes) and adjust the `--s-fg-faint` expectation to its **new decorative floor of 3:1** with an inline comment naming D4 — run `npx vitest run src/app/(sales)/sales-tokens.test.ts` → green both themes.
- [ ] **Step 2: Card hierarchy** — `TodayCard.tsx`: primary row keeps `התקשר` + `וואטסאפ` full-width; `דחה` + `אבוד` demote to a text-link row below (`text-[13px]`, `--s-fg-faint`, min-height 44px via padding, separated by ` · `) (VISUAL-001); returning-customer WhatsApp button gets new class `s-btn-ghost-on-tint` added to tokens (`background: transparent; border-color: hsl(var(--s-accent) / 0.4);`) (VISUAL-005); ConversionCard gains `background: hsl(var(--s-status-won-soft))` (VISUAL-015); age line already toned (T164).
- [ ] **Step 3: Touch & focus floor** — all `h-10 w-10` icon controls → `h-11 w-11` (SalesShell ×3, LeadDrawer close, OrgCard close); `.s-tab { min-height: 44px; padding-block: 10px; }`; OrgCard lead links → `min-h-[44px] flex items-center px-2` (A11Y-001/002/004); `.s-tab-active` gains `font-weight: 600` (A11Y-005); OrgCard lead links join the focus-visible rule list in tokens (A11Y-006-adjacent); FAB `insetInlineEnd: 16` → `insetInlineStart: 16` with the ergonomics comment (P1-13); CommandK input: replace `border: 0` with `border-color: transparent; border-block-end: 1px solid hsl(var(--s-border-field));` (A11Y-006).
- [ ] **Step 4: ARIA & copy details** — OutcomeSheet lost radios: roving tabindex + Arrow keys, copying the leads-page tablist handler (A11Y-003/P1-12); SLA input error text (final: `בין 1 ל־168 שעות`) + `aria-describedby`, hint association (A11Y-007/008); QuickAdd contact name `required` + label suffix (final: `שם איש קשר (חובה)`) (A11Y-009); no-phone buttons → `aria-disabled` + sr-only reason (final: `אין מספר טלפון לליד הזה`) (A11Y-010); drawer events area wrapped in polite live region announcing (final sr-only) `{n} אירועים` (A11Y-011); all `text-[11px]` → `text-[12px]` (EventTimeline, CustomerBadge, `.s-badge` font-size 12px) (A11Y-012); `CustomerBadge.renderValue`: map `status` values `active → פעיל`, `disabled → לא פעיל` (VISUAL-017); table row hover `tbody tr:hover { background: hsl(var(--s-surface-sunken)); }` in tokens (VISUAL-007); skeleton height 132 → 188 (VISUAL-008); drawer timeline loading → 3 pulse lines (VISUAL-016); status column hidden on single-status tabs (`hidden` when `tab !== "all"` — today there is no "all" tab so it is always hidden; keep the prop so a future all-tab restores it) (VISUAL-009); save buttons render (final) `שומר…` while busy (INTER-005/016).
- [ ] **Step 5: Playwright** — `tests/e2e/sales-visual-a11y.spec.ts`: `all header controls measure ≥44px` · `outcome sheet radios move with arrow keys` · `active tab is bold, not color-only` · `fab sits at the physical bottom-right in rtl` · `no text renders below 12px in the sales tree` (computed-style walk).
- [ ] **Step 6: Gate & commit** — F17 suite green BOTH themes (report N/N) · spec 5/5 · typecheck 0. Commits: `feat(sales-portal): T168 — visual hierarchy, 44px floor, aria completeness, token pass (D4)` + close.

---

### Task T169: Tranche 169 — shell & CI hygiene: the switch Tom can find + GAP-030 (P1-19, INF-3)

**Files (manifest, verbatim):**
```
src/components/layout/TopBar.tsx
src/components/layout/TopBar.switch.test.tsx
tests/e2e/production-picking.spec.ts
docs/portal-os/tranches/169-shell-and-ci-hygiene.md
docs/portal-os/tranches/_active.txt
docs/portal-os/registry.md
```

- [ ] **Step 1: Failing vitest** — extend `TopBar.switch.test.tsx`: `sales switch shows a visible label on phone widths` (assert the label node is NOT hidden below `sm` — it renders text content `Sales` at all widths) and `sales switch carries the accent treatment` (class assertion).
- [ ] **Step 2: Make it findable** — `TopBar.tsx` `SalesSwitch`: label (English — factory shell rule): `Sales`, visible at ALL widths (remove the `hidden sm:inline` pattern; keep `btn btn-ghost` but add a persistent border `border border-[var(--border)]` so it reads as a control, not an icon); `aria-label` unchanged. Precedent: tranche 163 built it icon-only and Tom reported it missing the same day (`user_confirmed`, audit P1-19) — discoverability beats minimalism here.
- [ ] **Step 3: GAP-030** — `production-picking.spec.ts:95`: raise that one navigation's assertion to `await expect(page).toHaveURL(/\/production\/runs\//, { timeout: 15_000 });` with a comment naming GAP-030 and the on-demand-compile cause. No other timeout changes.
- [ ] **Step 4: Gate & commit** — `npx vitest run src/components/layout` green · `/portal-regression-guard` green (shell file touched) · typecheck 0. Commit: `fix(portal): T169 — findable sales switch; deflake picking e2e (GAP-030)` + close. Update `docs/gap_registry.md` (brain repo, separate commit there): GAP-030 → CLOSED with evidence path.

---

## Execution protocol (Phase 2, masterprompt §7)

1. **Order:** B1 → B2→B3→B4→B5 (serial, FR1/FR2 each) → B6 → prod-apply gate for 0324–0327 (announce one line; apply; post-deploy probe: unauth `GET /api/v1/queries/sales/attention` on the Railway host → expect 401, not 404) → T164 → T165 → T166 (+B7 files) → T167 → T168 → T169. T169 may run any time after B1.
2. **Per-surface gate** after each tranche: `npm run typecheck` 0 · `npx vitest run` green · the tranche's Playwright spec green. Do not proceed on red; a plan defect → STOP and report, do not improvise.
3. **After T164–T169:** run `impeccable` **audit → polish → harden** to completion over the `(sales)` surfaces (fixes land as tranche-170 if any file outside an open manifest needs touching — open it with the same conventions), **then** `/ux-release-gate`.
4. **Release-gate loop capped at 3 iterations.** Not SHIP by the 3rd → STOP and report remaining blockers to Tom.
5. **Evidence per PASS (brain standard):** files changed · tests N/N (pgTAP, vitest, Playwright, api) · contracts referenced · signals emitted · stop conditions tripped · Tom approvals required · rollback plan · next handoff. Real-data screenshots (desktop+mobile) of: Today capped, attention screen, bulk bar, settings people — cropped or fixture rows only (PII rule).
6. **PR bodies** (one draft PR per repo on `claude/fable-sonnet-planning-v991qw`): gate verdict + iteration count + deferred polish-later list + this plan's path.
7. **Rollback:** portal — revert the tranche commit(s); backend — migrations are additive (new functions/views/keys; two DROPped signatures restored by re-running the 0322 definitions, kept verbatim inside each migration's header comment for that purpose — executor: paste the dropped signature's original body into a `-- ROLLBACK REFERENCE` comment block at the foot of 0324 and 0325). `stock_ledger` untouched throughout — `rebuild_verifier()` not implicated, but run `select private_core.run_rebuild_verifier('manual')` once after prod apply anyway and report 0 drift.
8. **State updates at close:** Sales-Machine `CURRENT_STATE.md` — U-011/U-012 → resolved-by (this plan), U-013 stays open (Phase 3); brain `CURRENT_STATE.md` untouched except via close-session skill flow.

## Deferred (recorded so nobody helpfully builds them)

Round-robin/capacity auto-assignment rules (D1 keeps manual+bulk; revisit when two people actually work daily) · in-progress collision lock (P1-15 — needs schema, design when Erik is real) · per-stage WhatsApp templates (F16) · org edit/merge + duplicate resolution verbs (admin-F11/F12/F13 — v3 candidates) · Meta intake + Resend wiring (Phase 3, §9, D6 pulls only the credential ask forward) · reports screen · importing the 560-customer base · call-script cards.

## Phase 3 pointer (not in this plan's scope)

After Phase 2 lands and Tom has seen it: masterprompt §9 verbatim — META_PAGE_ACCESS_TOKEN walkthrough → intake Edge Function + dry-run against a test submission → prove a lead lands with an `imported` event; RESEND_API_KEY into BOTH stores (Supabase Auth SMTP + Edge secrets, `docs/runbooks/credential_rotation.md`); both inbound-only; `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` stays `false`. GAP-029 (Shopify token in git history) remains open and blocks making gt-factory-os public — not this session's work.
