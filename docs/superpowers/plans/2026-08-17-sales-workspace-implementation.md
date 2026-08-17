# GT Sales Workspace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `executing-plans` (bare name — it lives
> in `gt-factory-os-production-brain/.claude/skills/`) to implement this plan task-by-task.
> Steps use checkbox (`- [ ]`) syntax for tracking. Per the 2026-08-17 masterprompt this
> plan is executed by a non-frontier model: **make zero product decisions** — every
> decision is already made here. If a task cannot proceed as written, STOP and report;
> do not improvise.
>
> **Session prerequisites (addendum §5):** all four repos attached
> (`gt-factory-os-portal`, `gt-factory-os`, `gt-factory-os-production-brain`,
> `Sales-Machine`) — the UX-gate commands (`/screen-scorecard`, `/design-system-check`,
> `/ux-release-gate`, `/portal-regression-guard`) and the superpowers skills live in the
> brain repo. Branch: `claude/caveman-mode-oenfxl` in every repo. Portal tranche **162**
> is active (`docs/portal-os/tranches/_active.txt` = `162`); every portal file you touch
> is either in its manifest or in a hook-exempt class (`.claude/*`, `docs/portal-os/*`,
> `.github/*`, `tests/e2e/*.spec.ts`, `tests/unit/*`).

**Goal:** Build the GT Sales Workspace — `/apps` switchboard + Hebrew-RTL `(sales)` route
group (Today queue with one-tap outcome loop, Leads table + drawer, Orgs, quick-add,
global search, PWA, minimal settings) on the live `sales_core` data (188 real leads), with
the data layer (2 migrations + pgTAP), Fastify endpoints, and portal proxy stubs.

**Architecture:** Postgres `sales_core` (already live) gains mutation functions + an
`app_setting` table (migration 0322) and five `api_read.v_sales_*` views (0323, granted to
`service_role` ONLY — PII lock). Fastify exposes `/api/v1/queries/sales/*` +
`/api/v1/mutations/sales/*` (admin-gated). The portal reaches them exclusively through
`src/app/api/sales/**` proxy stubs (`proxyRequest`) — the portal never queries Supabase
data directly. UI is a self-contained `(sales)` route group with its own chrome, scoped
tokens (`[data-app="sales"]`), Rubik font, and mobile bottom tabs.

**Tech Stack:** Next.js 15 App Router · React 18 · Tailwind 3.4 (CSS logical utilities) ·
TanStack Query 5 · Supabase SSR auth (unchanged) · Zod · Fastify 4 + Kysely ·
pgTAP 1.3.3 · Playwright (`@mocked`) · vitest 2 · impeccable 3.6.0 (dev tooling only).

## Global Constraints

- **Never edit:** `globals.css`, `tailwind.config.ts`, `portal_ux_standard.md`,
  `portal_language_direction_audit.md`, factory route groups, public `/` page
  (Tranche 018), `baseline.json`, `quarantine.json`.
- **Language:** every user-visible string in `/apps` + `(sales)` is Hebrew (authorized
  CLAUDE.md exception row, 2026-08-17). Code, comments, commits, PR bodies: English.
  Schema values (`new`/`working`/`won`/`lost`) never translated — display mapping only.
- **RTL:** `dir="rtl"` + CSS **logical** properties/utilities only (`ps-*`, `pe-*`,
  `ms-*`, `me-*`, `text-start`, `start-*`, `end-*`) — no `left`/`right` physical
  properties in new code.
- **Color rule (addendum-2 §14, exact):** color = status pills + SLA badges + the ONE
  primary-action accent per screen. Nothing else gets color.
- **PII lock (addendum-2 §8):** `v_sales_*` views + sales mutation functions granted to
  `service_role` ONLY — never `authenticated` (deliberate divergence from the repo's
  view-grant convention, recorded in the migration headers). No lead names/phones in
  commits, PR bodies, or uncropped screenshots. No CSV in git.
- **`won` is never a button.** `sales_core.set_lead_status` rejects it; the UI shows won
  as an evidence banner only.
- **Frozen flags stay frozen.** `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` stays `false`.
  Nothing is ever sent to a lead or customer. No Meta intake / Resend work here.
- **No new runtime deps.** No UI libraries (Vibe/MUI/AntD/…). impeccable is dev tooling.
  No AGPL/GPL code copying.
- **Git:** never `git add -A` / `git add .` — add files by name. Draft PRs only. No model
  names in commits/PRs. Backend migrations: list `db/migrations/` immediately before AND
  after writing a numbered file; a new file appearing in between → HALT `contract_failure`.
- **TDD per task** (`test-driven-development` skill): failing test first. Before any
  "done" claim: `verification-before-completion`. Report N/N counts.
- **Skills are bare names** (addendum-2 §5): `executing-plans`,
  `test-driven-development`, `verification-before-completion` — no `superpowers:` prefix
  needed in this workspace.
- **Prod DB applies** are autonomous when gates are green, but post a one-line
  announcement in the session immediately before each apply (brain CLAUDE.md deploy
  autonomy). pgTAP is transaction-wrapped (begin/rollback) — safe against prod.

---

## Discovered facts (Phase A evidence — Phase B receives zero discovery)

| # | Fact | Evidence |
|---|---|---|
| F1 | Portal data access is ONLY `component → TanStack hook → fetch("/api/…") → src/app/api/**/route.ts → proxyRequest() → Fastify Bearer JWT`. All 168 route.ts files use `proxyRequest`; Supabase client is auth-only. | `src/lib/api-proxy.ts:82-101`; `src/app/api/dashboard/critical-today/route.ts` |
| F2 | Roles are exactly `operator, planner, admin, viewer`. No bookkeeper/sales role exists. | `src/lib/contracts/enums.ts:22` |
| F3 | The middleware role block is a documented NO-OP (role not projected into JWT `app_metadata`). Live gate = `SessionProvider` (`GET /api/me` → `app_users`) + `<RoleGate>` in the group layout. | `src/middleware.ts:140-164`; `src/lib/auth/session-provider.tsx:60` |
| F4 | Post-login default destination is `/home`, decided at `login/page.tsx:294` (`redirectTo ?? "/home"`), `auth/callback/page.tsx:44`, plus the hard-coded landing CTA `page.tsx:103` (`/dashboard` — do not touch, Tranche 018 protects `/`). | `src/app/(auth)/login/page.tsx:294`; `src/app/auth/callback/page.tsx:44` |
| F5 | Canonical group layout = server component wrapping `AppShellChrome → RoleGate → SeedGate → AppPageShell`. The `(sales)` group deliberately does NOT reuse `AppShellChrome`/`SeedGate` (own chrome; no IndexedDB dependency). | `src/app/(shared)/layout.tsx` |
| F6 | RTL convention: `dir="rtl"` (+ `lang="he"`) on the surface's root div, chrome stays LTR; zero `[dir="rtl"]` selectors in `globals.css`. The `(sales)` group intentionally extends this to the whole group via its layout wrapper (authorized). | `src/app/(po)/purchase-orders/placement-queue/page.tsx:279`; `src/app/(shared)/home/page.tsx:84-89` |
| F7 | Portal tokens are bare-HSL CSS vars (`--bg`, `--fg`, `--accent`…) consumed via `hsl(var(--x) / <alpha-value>)`; NOT shadcn names. No Hebrew webfont loaded (`Public_Sans`+`IBM_Plex_Mono`, latin only). | `src/app/globals.css:44-175`; `tailwind.config.ts:25-124`; `src/app/layout.tsx:12-24` |
| F8 | No PWA manifest, no icons, no service worker exist anywhere. `public/` holds only `brand/logo.png` (971×960). | portal-wide file search, 2026-08-17 |
| F9 | Playwright: dev-shim auth (`NEXT_PUBLIC_ENABLE_DEV_SHIM_AUTH=true` + `setFakeRole(page, role)` writing `gt.fakeauth.v1`), `@mocked` specs stub `page.route("**/api/…")`; CI runs `--grep @mocked`; device projects by filename prefix (`mobile-*.spec.ts` → iPhone 14). | `tests/e2e/helpers.ts:11`; `playwright.config.ts`; `.github/workflows/portal-pr-guard.yml` |
| F10 | Vitest: `globals:false` (import `describe/it/expect`), happy-dom, `tests/unit/**` + colocated both live. This tranche's unit tests go under `tests/unit/sales/` (hook-exempt). | `vitest.config.ts` |
| F11 | Backend: next migration slot **0322** (0318–0321 = sales_core, merged in PR #219). Test files named exactly `NNNN_<same-name>.test.sql`. Root package.json carries `db:apply:NNNN`/`db:test:NNNN` pairs. | `db/migrations/` listing 2026-08-17; root `package.json` |
| F12 | api_read view style: `create or replace view` + `comment on view` + grants guarded by `pg_roles` existence check (0255 form). No `security_invoker` anywhere. API connects as `postgres`; grants are documentation. | `db/migrations/0221`, `0255:145-160` |
| F13 | sales_core exact shapes: `lead.status CHECK (new/working/won/lost)`; `lead_won_requires_evidence`; `lead_lost_requires_reason`; `lead_event.event_type` CHECK with 9 values, auto-named `lead_event_event_type_check`; append-only trigger raises errcode `P0001`; `ingest_lead(p_source, p_external_id, p_contact_name, p_phone_raw, p_email, p_display_name, p_created_at, p_meta, p_shopify_customer_id) returns table (lead_id uuid, org_id uuid, was_new boolean)` — 9 args, no defaults. Phone normalisation via trigger on `phone_raw`. | `db/migrations/0318-0321` |
| F14 | Fastify handler idiom: `register<X>Route(app, {db, extractSession})`; Zod parse → 422 `{error:'Invalid …', issues}`; `AuthError` → `err.statusCode`; `Session = {user_id, email, role, display_name}`. | `api/src/activity_log/route.ts`; `api/src/auth/session.ts:11-21` |
| F15 | api tests: node:test serial (`tsx --test --test-concurrency=1`), real `DATABASE_URL(_POOLED)` from env or `../.env`, `createDb` from `../src/db/connection.ts`. | `api/test/activity_log_builders.test.ts:1-35` |
| F16 | pgTAP 1.3.3: schema-qualified assertions take one extra arg (`has_column('sales_core','org','x')` = table `sales_core`); `has_table` needs `::name` casts; `throws_ok(sql, sqlstate, null, desc)`; files wrap `begin;…rollback;`, distinct fixture UUID prefixes per file. | `db/tests/0318_sales_core_leads.test.sql` header |
| F17 | impeccable 3.6.0 (Apache-2.0) verified in a scratch install: CLI is `npx --yes impeccable@3.6.0 install -y --providers=claude --scope=project` (`skills install` is the legacy namespace); it writes `.claude/skills/impeccable/**` (~150 files: SKILL.md, reference/*.md, scripts/**) + `.claude/settings.local.json` (PostToolUse/Stop hooks). Commands table contains exactly: `shape`, `init`, `audit`, `polish`, `harden`, `onboard` (+ others). `/impeccable init` writes PRODUCT.md. | scratch install 2026-08-17 |
| F18 | Portal `.gitignore:26` ignores `.claude/skills/` — committing the vendored skill requires a committed negation line, never `git add -f` (brain stop-condition 5 forbids gitignore bypass). | `.gitignore:26` |
| F19 | `scripts/check-no-persona-in-urls.mjs` hard-codes persona groups in THREE places (`PERSONA_GROUPS` + two regexes at :71, :76-79); `sales` must be added to all three. | that file |
| F20 | Nav manifest: `NavItem {href,label,icon,min_role,roles?,placement?}`; `placement:"command"` = ⌘K only, no rail row. `tests/unit/nav/manifest-visibility.test.ts` asserts per-role sidebar hrefs (command items excluded from rails). `route-manifest.json` needs a row per new route. | `src/lib/nav/manifest.ts:71-115`; `docs/portal-os/route-manifest.json` |
| F21 | sharp-cli icon generation verified live: `npx --yes sharp-cli@5.2.0 resize 192 192 --fit contain --background "#ffffff" -i public/brand/logo.png -o <out>` produces a correct 192×192 PNG. | scratch run 2026-08-17 |
| F22 | Tranche numbering: `_active.txt` read `161` and `161-placement-queue-write-failures.md` exists (built), so this build is tranche **162** — addendum-2 item 2's "160 active / next = 161" was stale against the repo; primary truth wins. | `docs/portal-os/tranches/` listing 2026-08-17 |

## Locked decisions made in this plan (Phase B re-decides nothing)

| ID | Decision |
|---|---|
| P1 | Bulk multi-select on the leads table: **OUT** (deferred, recorded in tranche 162). Not trivially cheap (selection state, bulk bar, partial-failure UX). |
| P2 | Org detail = **drawer** over the list (same interaction as leads). The future churn radar gets its seam from the `OrgCard` component, not a page. |
| P3 | `lead.assignee` stores the **app_users email**. Queue filter: `assignee = session.email OR assignee IS NULL`; admins see everything (+ `?assignee=` param exists but no UI in v1 — single user). `lead_event.actor` = `session.display_name`. |
| P4 | Sales access = role `admin` (v1). Gate = `<RoleGate minimum="admin:execute">` in `(sales)/layout.tsx` + server-side `session.role !== 'admin' → 403` on every sales endpoint. Middleware `ROLE_GATES` gains dormant `/sales` + `/apps` rows for defense-in-depth (F3: no-op today). |
| P5 | Post-login default becomes `/apps` (login + callback defaults only). `/apps` itself instantly forwards non-admin roles to `/home`, and honors the remembered-app cookie (`gt.app.v1`: `sales` → `/sales/today`, `factory` → `/home`) with a visible "switch" affordance. Factory users see one extra client hop, same destination. |
| P6 | `/apps` reachability from factory chrome: one `NAV_MANIFEST` entry `{href:"/apps", roles:["admin"], placement:"command"}` (⌘K only, zero rail change). Sales chrome carries a "מעבר לייצור" link back. |
| P7 | Search = client-side filter over the already-fetched 188-row lead list + org list (one dataset, no server search endpoint). ⌘K opens it on desktop; a search screen/overlay on mobile. Phone queries are normalised with the same digit-stripping the DB uses before matching. |
| P8 | SLA + queue maths computed **in the views** (one truth): `sla_state` = `'within'`/`'overdue'`/`null after first touch`; `v_sales_today.item_type` ∈ `conversion` (won ≤7 days) / `returning_customer` / `new_lead` / `due_follow_up`. Client renders, never re-derives. |
| P9 | Outcome defaults (server-side, in `record_outcome`): `no_answer` → tomorrow 09:00 IL (06:00 UTC), `whatsapp_sent` → +2 days 09:00 IL; explicit `p_next_touch_at` always wins. `answered_progressing` requires an explicit next touch (the UI's one-tap picker supplies it). |
| P10 | impeccable hook wiring: after install, merge the `settings.local.json` hook block into the committed `.claude/settings.json` and delete `settings.local.json` (one committed hook manifest). Commit the vendored skill via a `.gitignore` negation (F18). |
| P11 | Dark mode: sales tokens define a `:root.dark [data-app="sales"]` override block so the portal's existing theme toggle doesn't break the surface; the design target is the light theme (white surfaces per masterprompt §5.8). |
| P12 | The five `v_sales_*` views + all 0322 functions: grants to `service_role` only, `do $$ pg_roles $$`-guarded; each migration header carries the PII-exception note (addendum-2 §8). |

## Execution order

Task 1 impeccable → 2 DB writes (0322) → 3 DB views (0323) → 4 Fastify → 5 proxy stubs →
6 tokens+fonts → 7 (sales) shell + libs → 8 /apps + redirects → 9 shape+build Today →
10 outcome loop → 11 GATE(Today) → 12 shape+build Leads → 13 GATE(Leads) →
14 shape+build Orgs → 15 GATE(Orgs) → 16 quick-add+search+settings → 17 PWA →
18 impeccable audit/polish/harden → 19 Playwright+screenshots → 20 regression-guard +
ux-release-gate loop → 21 route-manifest/registry/scorecard + verifier → 22 PRs + state.

Commit after every task (messages given per task). Portal commits on
`claude/caveman-mode-oenfxl` in `gt-factory-os-portal`; backend commits on the same
branch name in `gt-factory-os`.

---

### Task 1: Vendor impeccable + init

**Files:**
- Create: `.claude/skills/impeccable/**` (installer output, ~150 files under `gt-factory-os-portal/.claude/`)
- Create: `docs/third-party/impeccable-NOTICE.md`
- Create: `PRODUCT.md` (via `/impeccable init`)
- Modify: `.gitignore` (negation line under line 26)
- Modify: `.claude/settings.json` (merge hook block), delete `.claude/settings.local.json` after merge

**Interfaces:**
- Produces: `/impeccable <command>` runnable in-session; `PRODUCT.md` design context for every later `shape`/`audit` call.

- [ ] **Step 1: Install (exact command, version pinned — F17)**

```bash
cd /home/user/gt-factory-os-portal
npx --yes impeccable@3.6.0 install -y --providers=claude --scope=project
```

Expected output ends: `Done! Now type /impeccable init …`. Verify:
`find .claude/skills/impeccable -type f | wc -l` → ≥140, and
`.claude/skills/impeccable/SKILL.md` exists with a `## Commands` table containing `shape`,
`audit`, `polish`, `harden`, `onboard`, `init` (F17). If any of those five names is
missing from the table, STOP and report (addendum-2 §16).

- [ ] **Step 2: Unignore + commit-enable the vendored skill (F18 — no force-add ever)**

Append to `.gitignore` directly under the existing `.claude/skills/` line:

```gitignore
!.claude/skills/impeccable/
```

- [ ] **Step 3: Merge hooks into the committed settings**

Open `.claude/settings.local.json` (created by the installer). Copy its `hooks.PostToolUse`
and `hooks.Stop` entries into `.claude/settings.json`'s existing `hooks` object (create the
keys if absent, append to arrays if present). Delete `.claude/settings.local.json`.

- [ ] **Step 4: Write the third-party notice**

Create `docs/third-party/impeccable-NOTICE.md`:

```markdown
# Third-party notice — impeccable

- Package: `impeccable` v3.6.0 (npm)
- License: Apache-2.0
- Vendored: 2026-08-17 into `.claude/skills/impeccable/` via
  `npx --yes impeccable@3.6.0 install -y --providers=claude --scope=project`
- Role: development-time design tooling only. Not a runtime dependency; nothing from it
  ships in the portal bundle.
- Upstream: https://www.npmjs.com/package/impeccable
```

- [ ] **Step 5: Run `/impeccable init`** (writes `PRODUCT.md`). When it asks about the
product, the durable context is: GT Sales Workspace inside the GT factory portal —
Hebrew-RTL mobile-first CRM surface for one heavy user (Tom); monday.com's structure,
GT's quieter identity; color reserved for status/SLA + one accent; Rubik; 8px grid;
white surfaces, hairline borders; motion 150–200ms.

- [ ] **Step 6: Commit**

```bash
git add .gitignore .claude/settings.json .claude/skills/impeccable docs/third-party/impeccable-NOTICE.md PRODUCT.md
git rm --cached .claude/settings.local.json 2>/dev/null; rm -f .claude/settings.local.json
git commit -m "chore(sales): vendor impeccable 3.6.0 design skill + product context"
```

### Task 2: Migration 0322 — workspace write layer

**Files:**
- Create: `gt-factory-os/db/migrations/0322_sales_core_workspace_writes.sql`
- Create: `gt-factory-os/db/tests/0322_sales_core_workspace_writes.test.sql`
- Modify: `gt-factory-os/package.json` (script pair)

**Interfaces:**
- Produces (SQL, consumed by Task 4):
  `sales_core.set_lead_status(p_lead_id uuid, p_status text, p_reason text, p_actor text) returns table (lead_id uuid, status text)` — raises `P0001` `SALES_WON_IS_EVIDENCE_ONLY` on `'won'`;
  `sales_core.add_lead_note(p_lead_id uuid, p_note text, p_actor text) returns table (lead_id uuid, event_id uuid)`;
  `sales_core.set_next_touch(p_lead_id uuid, p_at timestamptz, p_actor text) returns table (lead_id uuid, next_touch_at timestamptz)`;
  `sales_core.assign_lead(p_lead_id uuid, p_assignee text, p_actor text) returns table (lead_id uuid, assignee text)`;
  `sales_core.record_outreach(p_lead_id uuid, p_channel text, p_actor text) returns table (lead_id uuid, event_id uuid)` — channel ∈ call/whatsapp/email;
  `sales_core.record_outcome(p_lead_id uuid, p_result text, p_next_touch_at timestamptz, p_reason text, p_actor text) returns table (lead_id uuid, status text, next_touch_at timestamptz, first_touch_at timestamptz)`;
  `sales_core.set_app_setting(p_key text, p_value jsonb) returns void`;
  table `sales_core.app_setting(key text pk, value jsonb, updated_at)` seeded with `sla_hours` + `whatsapp_templates`;
  `lead_event.event_type` CHECK extended with `'outreach'`, `'outcome'`.
  Error convention: every business rejection raises errcode `P0001` with a message
  starting `SALES_<CODE>:`-style token (Task 4 maps it to HTTP 422).

- [ ] **Step 1: FR bracket — list the migrations directory**

```bash
ls /home/user/gt-factory-os/db/migrations/ | tail -3
```
Expected: `0321_sales_core_ingest.sql` is the highest. If a `0322_*` exists → HALT,
`contract_failure` (F11).

- [ ] **Step 2: Write the failing pgTAP test**

Create `db/tests/0322_sales_core_workspace_writes.test.sql` — full content:

```sql
-- ===========================================================================
-- 0322_sales_core_workspace_writes.test.sql
--   pg_prove -d "$DATABASE_URL" db/tests/0322_sales_core_workspace_writes.test.sql
-- ===========================================================================
-- pgTAP for the sales-workspace write layer (0322).
-- Note on pgTAP overloads (1.3.3): schema-qualified forms take the extra
-- argument — has_column('sales_core','app_setting','key','desc') is 4-arg.
-- Fixture UUID prefix for this file: 55555555-*.
-- Self-contained: begin/rollback.

begin;
create extension if not exists pgtap;
select plan(24);

-- structure ---------------------------------------------------------------
select has_table('sales_core'::name, 'app_setting'::name);
select has_column('sales_core','app_setting','value','app_setting.value exists');
select col_type_is('sales_core','app_setting','value','jsonb','app_setting.value is jsonb');
select is((select value->>'hours' from sales_core.app_setting where key='sla_hours'),
  '24', 'sla_hours seeded at 24');
select is((select count(*) from sales_core.app_setting
  where key='whatsapp_templates'
    and value ? 'new_lead' and value ? 'reminder' and value ? 'returning_customer'),
  1::bigint, 'whatsapp_templates seeded with all three contexts');

-- fixtures ----------------------------------------------------------------
insert into sales_core.org (id, display_name)
values ('55555555-1111-1111-1111-111111111111', 'T162 fixture org');
insert into sales_core.lead (id, org_id, source, external_id, contact_name, status)
values ('55555555-2222-2222-2222-222222222222',
        '55555555-1111-1111-1111-111111111111', 'test', 't162-a', 'A', 'new');

-- event_type extension ----------------------------------------------------
select lives_ok(
  $$insert into sales_core.lead_event (lead_id, event_type, payload, actor)
    values ('55555555-2222-2222-2222-222222222222','outreach','{"channel":"call"}','t')$$,
  'event_type outreach accepted');
select lives_ok(
  $$insert into sales_core.lead_event (lead_id, event_type, payload, actor)
    values ('55555555-2222-2222-2222-222222222222','outcome','{"result":"no_answer"}','t')$$,
  'event_type outcome accepted');
select throws_ok(
  $$insert into sales_core.lead_event (lead_id, event_type, payload, actor)
    values ('55555555-2222-2222-2222-222222222222','bogus','{}','t')$$,
  '23514', null, 'unknown event_type still rejected');

-- set_lead_status ---------------------------------------------------------
select throws_ok(
  $$select * from sales_core.set_lead_status('55555555-2222-2222-2222-222222222222','won',null,'t')$$,
  'P0001', null, 'set_lead_status rejects won (evidence-only)');
select throws_ok(
  $$select * from sales_core.set_lead_status('55555555-2222-2222-2222-222222222222','lost',null,'t')$$,
  'P0001', null, 'lost without reason rejected');
select is(
  (select s.status from sales_core.set_lead_status(
     '55555555-2222-2222-2222-222222222222','working',null,'t') s),
  'working', 'status moves to working');
select is(
  (select count(*) from sales_core.lead_event
    where lead_id='55555555-2222-2222-2222-222222222222' and event_type='status_change'),
  1::bigint, 'status_change event written');
select isnt(
  (select first_touch_at from sales_core.lead where id='55555555-2222-2222-2222-222222222222'),
  null, 'first status change set first_touch_at');

-- add_lead_note / set_next_touch / assign_lead ---------------------------
select lives_ok(
  $$select * from sales_core.add_lead_note('55555555-2222-2222-2222-222222222222','note','t')$$,
  'add_lead_note lives');
select lives_ok(
  $$select * from sales_core.set_next_touch('55555555-2222-2222-2222-222222222222', now() + interval '1 day','t')$$,
  'set_next_touch lives');
select lives_ok(
  $$select * from sales_core.assign_lead('55555555-2222-2222-2222-222222222222','tom@gteveryday.com','t')$$,
  'assign_lead lives');
select is(
  (select assignee from sales_core.lead where id='55555555-2222-2222-2222-222222222222'),
  'tom@gteveryday.com', 'assignee stored as email');

-- record_outreach ---------------------------------------------------------
select throws_ok(
  $$select * from sales_core.record_outreach('55555555-2222-2222-2222-222222222222','fax','t')$$,
  'P0001', null, 'invalid channel rejected');

-- record_outcome ----------------------------------------------------------
insert into sales_core.lead (id, org_id, source, external_id, contact_name, status)
values ('55555555-3333-3333-3333-333333333333',
        '55555555-1111-1111-1111-111111111111', 'test', 't162-b', 'B', 'new');
select is(
  (select o.status from sales_core.record_outcome(
    '55555555-3333-3333-3333-333333333333','answered_progressing',
    now() + interval '3 days', null, 't') o),
  'working', 'answered_progressing promotes new to working');
select isnt(
  (select next_touch_at from sales_core.lead where id='55555555-3333-3333-3333-333333333333'),
  null, 'outcome always leaves a next touch on an open lead');
select is(
  (select count(*) from sales_core.lead_event
    where lead_id='55555555-3333-3333-3333-333333333333' and event_type='outcome'),
  1::bigint, 'outcome event written');
select throws_ok(
  $$select * from sales_core.record_outcome('55555555-3333-3333-3333-333333333333','lost',null,null,'t')$$,
  'P0001', null, 'lost outcome without reason rejected');
select lives_ok(
  $$select * from sales_core.record_outcome('55555555-3333-3333-3333-333333333333','no_answer',null,null,'t')$$,
  'no_answer with null next_touch defaults server-side');
select is(
  (select o.status from sales_core.record_outcome(
    '55555555-3333-3333-3333-333333333333','lost',null,'לא רלוונטי','t') o),
  'lost', 'lost outcome closes the lead');

select * from finish();
rollback;
```

- [ ] **Step 3: Run it — must FAIL** (functions/table absent):
`cd /home/user/gt-factory-os && pg_prove -d "$DATABASE_URL" db/tests/0322_sales_core_workspace_writes.test.sql`

- [ ] **Step 4: Write the migration.** Full SQL (this is the implementation — copy
verbatim into `db/migrations/0322_sales_core_workspace_writes.sql`):

```sql
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
-- ACCESS EXCEPTION (deliberate, Tom addendum-2 2026-08-17 §8):
--   Functions here are granted to service_role ONLY — never `authenticated` —
--   because lead rows are PII of non-customers. All access flows through the
--   server-side API (which connects as postgres); the guarded grants document
--   intent without widening exposure.
--
-- SHAPE
--   1. lead_event.event_type CHECK extended additively (+outreach, +outcome).
--   2. sales_core.app_setting — key/value jsonb settings, seeded.
--   3. Mutation functions (see masterprompt §6.2), all P0001 on rejection.
--
-- Depends on: 0318 (tables), 0320 (append-only), 0321 (ingest_lead).
-- Rollback posture: additive; functions replaceable; app_setting droppable.
-- ===========================================================================
```

…followed by the `begin; … commit;` body exactly as drafted in Phase A — the canonical
copy of the full body (constraint swap, `app_setting` + seeds, `set_app_setting`,
`lock_lead`, `touch_first`, `set_lead_status`, `add_lead_note`, `set_next_touch`,
`assign_lead`, `record_outreach`, `record_outcome`) is committed alongside this plan at
**`docs/superpowers/plans/2026-08-17-sales-workspace-sql/0322_sales_core_workspace_writes.sql`**
in this repo. Copy that file's content byte-for-byte (header above included), then append
this grants block immediately before the final `commit;`:

```sql
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
```

- [ ] **Step 5: FR bracket close** — `ls db/migrations/ | tail -3` again: `0322` must be
the only new file. Register the script pair in root `package.json` next to `db:test:0321`:

```json
"db:apply:0322": "psql \"$DATABASE_URL\" -v ON_ERROR_STOP=1 -f db/migrations/0322_sales_core_workspace_writes.sql",
"db:test:0322": "pg_prove -d \"$DATABASE_URL\" db/tests/0322_sales_core_workspace_writes.test.sql",
```

- [ ] **Step 6: Apply + test.** Announce one line in-session (deploy autonomy), then:

```bash
npm run db:apply:0322 && npm run db:test:0322
```
Expected: `24/24`. Then re-run the neighbours (they must stay green):
`pg_prove -d "$DATABASE_URL" db/tests/0318*.test.sql db/tests/0319*.test.sql db/tests/0320*.test.sql db/tests/0321*.test.sql` → 43/43.

- [ ] **Step 7: Commit** (in `gt-factory-os`):

```bash
git add db/migrations/0322_sales_core_workspace_writes.sql db/tests/0322_sales_core_workspace_writes.test.sql package.json
git commit -m "feat(sales): workspace write layer — outcome loop functions, app_setting, event types (0322)"
```

### Task 3: Migration 0323 — api_read views

**Files:**
- Create: `gt-factory-os/db/migrations/0323_sales_api_read_views.sql`
- Create: `gt-factory-os/db/tests/0323_sales_api_read_views.test.sql`
- Modify: `gt-factory-os/package.json` (script pair `db:apply:0323` / `db:test:0323`, same shape as Task 2 Step 5)

**Interfaces:**
- Produces (consumed by Task 4): `api_read.v_sales_leads` (all lead columns + `org_name`,
  `is_existing_customer`, `shopify_snapshot`, `shopify_snapshot_at`, `age_days int`,
  `sla_deadline_at timestamptz`, `sla_state text|null` ∈ within/overdue/null,
  `next_touch_overdue bool`); `api_read.v_sales_lead_events`; `api_read.v_sales_orgs`
  (+`lead_count bigint`, `last_activity_at`); `api_read.v_sales_today` (queue rows +
  `item_type` ∈ conversion/returning_customer/new_lead/due_follow_up, `converted_at`);
  `api_read.v_sales_week_stats` (single row: `week_new_leads`, `working_now`,
  `week_converted`); helper `sales_core.sla_hours() returns integer`.

- [ ] **Step 1: FR bracket** — `ls db/migrations/ | tail -3` → highest must be `0322_…`.
- [ ] **Step 2: Failing test.** Create `db/tests/0323_sales_api_read_views.test.sql`
(fixture prefix `66666666-*`), full content:

```sql
-- ===========================================================================
-- 0323_sales_api_read_views.test.sql
--   pg_prove -d "$DATABASE_URL" db/tests/0323_sales_api_read_views.test.sql
-- ===========================================================================
-- pgTAP for the sales api_read views (0323). Fixture prefix 66666666-*.

begin;
create extension if not exists pgtap;
select plan(14);

select has_view('api_read'::name, 'v_sales_leads'::name, 'v_sales_leads exists');
select has_view('api_read'::name, 'v_sales_lead_events'::name, 'v_sales_lead_events exists');
select has_view('api_read'::name, 'v_sales_orgs'::name, 'v_sales_orgs exists');
select has_view('api_read'::name, 'v_sales_today'::name, 'v_sales_today exists');
select has_view('api_read'::name, 'v_sales_week_stats'::name, 'v_sales_week_stats exists');

insert into sales_core.org (id, display_name, shopify_customer_id)
values ('66666666-1111-1111-1111-111111111111', 'T163 customer org', 'gid://shopify/Customer/163');
insert into sales_core.lead (id, org_id, source, external_id, contact_name, status, created_at)
values ('66666666-2222-2222-2222-222222222222',
        '66666666-1111-1111-1111-111111111111', 'test', 't163-new', 'N', 'new',
        now() - interval '2 hours');

select is(
  (select item_type from api_read.v_sales_today where lead_id='66666666-2222-2222-2222-222222222222'),
  'returning_customer',
  'new lead on a customer org classifies returning_customer');
select is(
  (select sla_state from api_read.v_sales_leads where id='66666666-2222-2222-2222-222222222222'),
  'within', '2h-old untouched lead is within a 24h SLA');
select is(
  (select is_existing_customer from api_read.v_sales_leads where id='66666666-2222-2222-2222-222222222222'),
  true, 'customer badge derives from org.shopify_customer_id');

-- overdue follow-up classification
insert into sales_core.lead (id, org_id, source, external_id, contact_name, status,
                             first_touch_at, next_touch_at)
values ('66666666-3333-3333-3333-333333333333',
        '66666666-1111-1111-1111-111111111111', 'test', 't163-due', 'D', 'working',
        now() - interval '1 day', now() - interval '1 hour');
select is(
  (select item_type from api_read.v_sales_today where lead_id='66666666-3333-3333-3333-333333333333'),
  'due_follow_up', 'due next_touch classifies due_follow_up');
select is(
  (select sla_state from api_read.v_sales_leads where id='66666666-3333-3333-3333-333333333333'),
  null, 'sla_state null after first touch (badge disappears)');
select is(
  (select next_touch_overdue from api_read.v_sales_leads where id='66666666-3333-3333-3333-333333333333'),
  true, 'next_touch_overdue derives');

-- future follow-up stays OUT of today
insert into sales_core.lead (id, org_id, source, external_id, contact_name, status,
                             first_touch_at, next_touch_at)
values ('66666666-4444-4444-4444-444444444444',
        '66666666-1111-1111-1111-111111111111', 'test', 't163-future', 'F', 'working',
        now() - interval '1 day', now() + interval '3 days');
select is(
  (select count(*) from api_read.v_sales_today where lead_id='66666666-4444-4444-4444-444444444444'),
  0::bigint, 'future next_touch not in today queue');

select is(
  (select lead_count from api_read.v_sales_orgs where id='66666666-1111-1111-1111-111111111111'),
  3::bigint, 'org lead_count aggregates');
select ok(
  (select week_new_leads >= 3 from api_read.v_sales_week_stats),
  'week stats count this week''s fixtures');

select * from finish();
rollback;
```

- [ ] **Step 3: Run — must FAIL** (`has_view` 5× fail).
- [ ] **Step 4: Write the migration.** Header must carry the same ACCESS EXCEPTION note as
0322. The canonical full SQL is committed at
**`docs/superpowers/plans/2026-08-17-sales-workspace-sql/0323_sales_api_read_views.sql`**
(this repo) — `sales_core.sla_hours()`, the five views exactly as specified in
Interfaces, comments on every view, and the final guarded grant block granting the five
views to **`service_role` only**. Copy byte-for-byte.
- [ ] **Step 5: FR bracket close + package.json pair.**
- [ ] **Step 6: Announce + `npm run db:apply:0323 && npm run db:test:0323`** → 14/14, then
`npm run db:test:0322` again (24/24 — the constraint swap must not have regressed).
- [ ] **Step 7: Commit:** `feat(sales): api_read views for the sales workspace (0323)`.

### Task 4: Fastify sales endpoints

**Files:**
- Create: `gt-factory-os/api/src/sales/schemas.ts`, `api/src/sales/queries_handler.ts`,
  `api/src/sales/mutations_handler.ts`, `api/src/sales/route.ts`
- Modify: `gt-factory-os/api/src/server.ts` (import + one `registerSalesRoutes(app, { db, extractSession })` call beside `registerActivityLogRoute`)
- Create: `gt-factory-os/api/test/sales_workspace.test.ts`

**Interfaces:**
- Consumes: Task 2 functions, Task 3 views, `Session {user_id,email,role,display_name}` (F14).
- Produces (HTTP, consumed by Task 5): under `/api/v1/queries/sales/`: `today`
  (`{rows: TodayRow[]}` — handler filters `assignee = session.email OR assignee IS NULL`
  unless role=admin; `?assignee=` param overrides for admin), `leads` (`{rows}`),
  `leads/:lead_id/events` (`{rows}`), `orgs` (`{rows}`), `week-stats` (`{stats}`),
  `settings` (`{sla_hours:number, whatsapp_templates:{new_lead,reminder,returning_customer}}`).
  Under `/api/v1/mutations/sales/`: `leads/:lead_id/status` `{status, reason?}`,
  `…/note` `{note}`, `…/next-touch` `{at}`, `…/assign` `{assignee}`, `…/outreach`
  `{channel}`, `…/outcome` `{result, next_touch_at?, reason?}`, `quick-add`
  `{contact_name, phone?, business_name?, source_note?}` → `{lead_id, org_id, was_new}`,
  `settings` PUT `{sla_hours?, whatsapp_templates?}`.
  Every endpoint: non-admin session → 403 `{error:"Not authorised"}`. DB `P0001` with a
  `SALES_`-prefixed message → 422 `{error:"<full message>", code:"<SALES_TOKEN>"}`.

- [ ] **Step 1: Failing test.** `api/test/sales_workspace.test.ts` — node:test serial,
live DB, **every mutation wrapped in a rolled-back transaction** (the append-only trigger
makes delete-cleanup impossible; residue on prod is forbidden). Skeleton to implement in
full:

```ts
import './_test_env.ts';
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { sql } from 'kysely';
import { createDb, type Db } from '../src/db/connection.ts';
import type { Session } from '../src/auth/session.ts';
import { handleSalesToday, handleSalesLeads, handleSalesSettings } from '../src/sales/queries_handler.ts';
import { handleOutcome, handleQuickAdd } from '../src/sales/mutations_handler.ts';

const db: Db = createDb(process.env.DATABASE_URL_POOLED ?? process.env.DATABASE_URL!);
const admin: Session = { user_id: '00000000-0000-0000-0000-000000000001',
  email: 'tom@gteveryday.com', role: 'admin', display_name: 'Tom' };
const viewer: Session = { ...admin, role: 'viewer' };
class Rollback extends Error {}

test('sales queries: viewer is 403, admin reads rows', async () => {
  await assert.rejects(handleSalesLeads(db, viewer), /Not authorised/);
  const res = await handleSalesLeads(db, admin);
  assert.ok(Array.isArray(res.body.rows));
  assert.ok(res.body.rows.length >= 180); // 188 live leads
});

test('settings round out of app_setting', async () => {
  const res = await handleSalesSettings(db, admin);
  assert.equal(typeof res.body.sla_hours, 'number');
  assert.ok(res.body.whatsapp_templates.new_lead.length > 0);
});

test('outcome mutation writes lead_event transactionally (rolled back)', async () => {
  await assert.rejects(
    db.transaction().execute(async (trx) => {
      const org = await sql<{ id: string }>`
        insert into sales_core.org (display_name) values ('api-test-org') returning id
      `.execute(trx);
      const lead = await sql<{ id: string }>`
        insert into sales_core.lead (org_id, source, external_id, contact_name)
        values (${org.rows[0].id}, 'test', ${'api-' + crypto.randomUUID()}, 'API T')
        returning id
      `.execute(trx);
      const out = await handleOutcome(trx as unknown as Db, admin,
        lead.rows[0].id, { result: 'no_answer' });
      assert.equal(out.body.status, 'new');
      assert.ok(out.body.next_touch_at !== null);
      const ev = await sql<{ n: string }>`
        select count(*) as n from sales_core.lead_event
        where lead_id = ${lead.rows[0].id} and event_type = 'outcome'
      `.execute(trx);
      assert.equal(Number(ev.rows[0].n), 1);
      throw new Rollback();
    }),
    Rollback,
  );
});

test('quick-add flows through ingest_lead idempotently (rolled back)', async () => {
  await assert.rejects(
    db.transaction().execute(async (trx) => {
      const r = await handleQuickAdd(trx as unknown as Db, admin, {
        contact_name: 'בדיקה', phone: '052-1234567',
        business_name: 'קפה בדיקה', source_note: 'טלפון נכנס',
      });
      assert.ok(r.body.lead_id);
      assert.ok(r.body.org_id);
      assert.equal(r.body.was_new, true);
      throw new Rollback();
    }),
    Rollback,
  );
});
```

Run `cd api && npm test` → the new file FAILS (modules missing). Existing suites stay green.

- [ ] **Step 2: `schemas.ts`** — Zod: `statusBody {status: z.enum(['working','lost']), reason: z.string().optional()}`,
`noteBody {note: z.string().min(1)}`, `nextTouchBody {at: z.string().datetime({offset:true})}`,
`assignBody {assignee: z.string()}`, `outreachBody {channel: z.enum(['call','whatsapp','email'])}`,
`outcomeBody {result: z.enum(['answered_progressing','no_answer','whatsapp_sent','lost']), next_touch_at: z.string().datetime({offset:true}).nullable().optional(), reason: z.string().nullable().optional()}`,
`quickAddBody {contact_name: z.string().min(1), phone: z.string().optional(), business_name: z.string().optional(), source_note: z.string().optional()}`,
`settingsPutBody {sla_hours: z.number().int().min(1).max(168).optional(), whatsapp_templates: z.object({new_lead: z.string(), reminder: z.string(), returning_customer: z.string()}).optional()}`.
Also define here the business-rejection error the route maps to 422:

```ts
export class SalesRuleError extends Error {
  constructor(message: string, public readonly code: string) {
    super(message);
    this.name = 'SalesRuleError';
  }
}
```

- [ ] **Step 3: `queries_handler.ts`.** Each handler: `if (session.role !== 'admin') throw new AuthError('Not authorised', 403);`
then plain `sql` selects. Today (P3 assignee lock):

```ts
export async function handleSalesToday(db: Db, session: Session, assigneeParam?: string) {
  if (session.role !== 'admin') throw new AuthError('Not authorised', 403);
  const filter = assigneeParam
    ? sql` where (assignee = ${assigneeParam} or assignee is null)`
    : sql``; // admins see everything by default (P3)
  const r = await sql`
    select * from api_read.v_sales_today
    ${filter}
    order by case item_type
      when 'conversion' then 0 when 'returning_customer' then 1
      when 'new_lead' then 2 else 3 end,
      coalesce(next_touch_at, created_at) asc
  `.execute(db);
  return { kind: 'ok' as const, status: 200 as const, body: { rows: r.rows } };
}
```
`handleSalesLeads` (`select * from api_read.v_sales_leads order by (status='new') desc, next_touch_overdue desc, created_at desc`),
`handleSalesLeadEvents(db, session, leadId)` (`… v_sales_lead_events where lead_id=… order by created_at desc`),
`handleSalesOrgs` (`… v_sales_orgs order by last_activity_at desc nulls last`),
`handleSalesWeekStats` (single row), `handleSalesSettings` (two `app_setting` reads folded
to `{sla_hours, whatsapp_templates}`).

- [ ] **Step 4: `mutations_handler.ts`.** Each calls its 0322 function with named args and
maps `P0001`:

```ts
function mapSalesDbError(err: unknown): never {
  const e = err as { code?: string; message?: string };
  if (e?.code === 'P0001' && e.message?.includes('SALES_')) {
    const token = e.message.match(/SALES_[A-Z_]+/)?.[0] ?? 'SALES_REJECTED';
    throw new SalesRuleError(e.message ?? token, token); // route maps → 422
  }
  throw err;
}

export async function handleOutcome(db: Db, session: Session, leadId: string,
  body: { result: string; next_touch_at?: string | null; reason?: string | null }) {
  if (session.role !== 'admin') throw new AuthError('Not authorised', 403);
  try {
    const r = await sql<{ lead_id: string; status: string; next_touch_at: string | null; first_touch_at: string | null }>`
      select * from sales_core.record_outcome(
        p_lead_id       => ${leadId}::uuid,
        p_result        => ${body.result},
        p_next_touch_at => ${body.next_touch_at ?? null}::timestamptz,
        p_reason        => ${body.reason ?? null},
        p_actor         => ${session.display_name})
    `.execute(db);
    return { kind: 'ok' as const, status: 200 as const, body: r.rows[0] };
  } catch (err) { mapSalesDbError(err); }
}
```
Quick-add — the exact nine-named-arg `ingest_lead` call (addendum-2 §9):

```ts
export async function handleQuickAdd(db: Db, session: Session,
  body: { contact_name: string; phone?: string; business_name?: string; source_note?: string }) {
  if (session.role !== 'admin') throw new AuthError('Not authorised', 403);
  const meta = body.source_note ? { manual_note: body.source_note } : {};
  const r = await sql<{ lead_id: string; org_id: string; was_new: boolean }>`
    select * from sales_core.ingest_lead(
      p_source              => 'manual',
      p_external_id         => ${'manual-' + crypto.randomUUID()},
      p_contact_name        => ${body.contact_name},
      p_phone_raw           => ${body.phone ?? null},
      p_email               => ${null},
      p_display_name        => ${body.business_name ?? null},
      p_created_at          => now(),
      p_meta                => ${JSON.stringify(meta)}::jsonb,
      p_shopify_customer_id => ${null})
  `.execute(db);
  return { kind: 'ok' as const, status: 201 as const, body: r.rows[0] };
}
```
Plus `handleSetStatus`, `handleAddNote`, `handleSetNextTouch`, `handleAssign`,
`handleOutreach` (same pattern, their respective 0322 functions), `handlePutSettings`
(calls `sales_core.set_app_setting` per provided key; merges `whatsapp_templates` as a
whole object).

- [ ] **Step 5: `route.ts`** — `registerSalesRoutes(app, deps)` in the exact
activity_log idiom (F14): extractSession → Zod parse (422 `{error:'Invalid body', issues}`)
→ handler → `SalesRuleError` → 422 `{error, code}`; `AuthError` → statusCode. Register all
14 endpoints (6 queries + 8 mutations; the portal mirrors them in 13 stub files — the
settings stub carries GET and PUT). Wire into `server.ts` beside `registerActivityLogRoute`.

- [ ] **Step 6: Run.** `cd api && npm test` → all green including 4 new; `npm run typecheck`
(root + api) → 0. Report N/N.
- [ ] **Step 7: Commit:** `feat(sales): admin-gated sales workspace endpoints (queries + mutations)`.

### Task 5: Portal proxy stubs

**Files:** Create 13 files under `gt-factory-os-portal/src/app/api/sales/` exactly as
listed in the tranche manifest (today, leads, leads/[lead_id]/{events,status,note,next-touch,assign,outreach,outcome}, orgs, week-stats, settings, quick-add).

**Interfaces:**
- Consumes: Task 4 URLs. Produces: same-shape portal URLs `/api/sales/*` for Task 7's hooks.

- [ ] **Step 1: Failing unit test** `tests/unit/sales/api-stubs.test.ts`: reads each stub
file as text (like `globals-css-mobile-zoom.test.ts` does) and asserts it contains
`proxyRequest` and the correct `upstreamPath`. Run → fails (files missing).
- [ ] **Step 2: Write the stubs.** Template (F1) — e.g.
`src/app/api/sales/today/route.ts`:

```ts
import { proxyRequest } from "@/lib/api-proxy";

// GET /api/sales/today → GET /api/v1/queries/sales/today
// Source view: api_read.v_sales_today (db/migrations/0323). Admin-only upstream.
export async function GET(req: Request): Promise<Response> {
  return proxyRequest(req, {
    method: "GET",
    upstreamPath: "/api/v1/queries/sales/today",
    forwardQuery: true,
    errorLabel: "sales today",
  });
}
```
Mutation stubs use `method: "POST"` (settings route also exports `PUT`). Dynamic-segment
stub template (Next 15 async params — complete code, e.g.
`src/app/api/sales/leads/[lead_id]/outcome/route.ts`):

```ts
import { proxyRequest } from "@/lib/api-proxy";

// POST /api/sales/leads/:lead_id/outcome → POST /api/v1/mutations/sales/leads/:lead_id/outcome
export async function POST(
  req: Request,
  { params }: { params: Promise<{ lead_id: string }> },
): Promise<Response> {
  const { lead_id } = await params;
  return proxyRequest(req, {
    method: "POST",
    upstreamPath: `/api/v1/mutations/sales/leads/${lead_id}/outcome`,
    forwardQuery: false,
    errorLabel: "sales outcome",
  });
}
```
- [ ] **Step 3: Test green** (`npx vitest run tests/unit/sales/api-stubs.test.ts`), typecheck 0.
- [ ] **Step 4: Commit:** `feat(sales): api proxy stubs for the sales workspace`.

### Task 6: Sales tokens + Rubik

**Files:**
- Create: `src/app/(sales)/sales-tokens.css`
- Test: `tests/unit/sales/sales-tokens.test.ts`

**Interfaces:**
- Produces CSS vars scoped to `[data-app="sales"]`: `--s-bg`, `--s-surface`, `--s-border`,
  `--s-border-strong`, `--s-fg`, `--s-fg-muted`, `--s-fg-faint`, `--s-accent`,
  `--s-accent-fg`, `--s-accent-soft`, `--s-status-new`, `--s-status-working`,
  `--s-status-won`, `--s-status-lost`, `--s-sla-ok`, `--s-sla-overdue`, `--s-radius`,
  `--s-font` — plus component classes `.s-card`, `.s-pill`, `.s-pill-new`,
  `.s-pill-working`, `.s-pill-won`, `.s-pill-lost`, `.s-badge-sla-ok`,
  `.s-badge-sla-overdue`, `.s-badge-customer`, `.s-btn-primary`, `.s-btn-ghost`,
  `.s-input`, `.s-tab`, `.s-tab-active`, `.s-sheet`. All colors bare-HSL triplets
  consumed as `hsl(var(--s-x))` (F7 convention). 8px spacing grid; motion 150–200ms
  `ease-out`; `font-variant-numeric: tabular-nums` utility class `.s-nums`.
- Dark block (P11): `:root.dark [data-app="sales"]` remaps surface/ink/border vars only.
- Color discipline (Global Constraints): only pills, SLA badges, and `--s-accent` carry
  chroma; every other var is neutral.

- [ ] **Step 1: Failing test** — text-contract test asserting: file exists, every selector
block is scoped under `[data-app="sales"]` (regex: no top-level `:root {` without the
`.dark` prefix form; no `left:`/`right:` physical properties; contains
`font-variant-numeric: tabular-nums` and `--s-accent`).
- [ ] **Step 2: Write the file.** Palette (locked): bg `0 0% 100%`; surface `40 20% 99%`;
border `40 10% 90%`; fg `220 15% 16%`; accent (the one action color, GT deep teal)
`186 42% 24%`; status-new `217 85% 45%` · working `35 90% 42%` · won `152 55% 34%` ·
lost `220 8% 55%`; sla-ok `152 55% 34%` · sla-overdue `0 72% 46%`. Radius 8px. Import
Rubik NOT here — the font loads via `next/font` in the layout (Task 7) and lands in
`--s-font`.
- [ ] **Step 3: Test green; commit:** `feat(sales): scoped sales token system`.

### Task 7: (sales) layout, shell, client libs

**Files:**
- Create: `src/app/(sales)/layout.tsx`, `src/app/(sales)/sales/page.tsx` (redirect),
  `src/app/(sales)/_components/SalesShell.tsx`,
  `src/app/(sales)/_lib/{types.ts,labels.ts,format.ts,wa.ts,api.ts,useOutcomeCapture.ts}`
- Test: `tests/unit/sales/{labels.test.ts,format.test.ts,wa.test.ts,useOutcomeCapture.test.tsx,sales-shell.test.tsx}`

**Interfaces:**
- Produces for every screen task: `types.ts` mirrors Task 3/4 payloads —
  `LeadStatus = "new"|"working"|"won"|"lost"`,
  `TodayItemType = "conversion"|"returning_customer"|"new_lead"|"due_follow_up"`,
  `OutcomeResult = "answered_progressing"|"no_answer"|"whatsapp_sent"|"lost"`,
  `SalesLeadRow`, `TodayRow`, `LeadEventRow`, `OrgRow`, `WeekStats`, `SalesSettings`
  (fields exactly as the Task 3 Interfaces block).
  `labels.ts`: `STATUS_LABELS: Record<LeadStatus,string>` = חדש/בטיפול/הומר ✓/אבוד;
  `EVENT_LABELS: Record<string,string>` (created ליד נוצר · status_change שינוי סטטוס ·
  note הערה · assignment שיוך · next_touch_set נקבע מגע הבא · alert_sent התראה נשלחה ·
  converted הומר מהזמנה · matched_existing_customer זוהה כלקוח קיים · imported יובא ·
  outreach פנייה יצאה · outcome תוצאת שיחה); `TAB_LABELS`, `NAV_LABELS`
  (היום/לידים/עסקים/הגדרות), `UI` (all button/empty-state strings — every user-visible
  string in the group imports from here, nothing inline).
  `format.ts`: `fmtDate`, `fmtRelative` (Hebrew: "לפני שעתיים", "מחר"), `fmtMoney`
  (₪, tabular), `fmtPhone` (display `05X-XXXXXXX` from E.164).
  `wa.ts`: `fillTemplate(tpl: string, name: string): string` ({{name}} replacement),
  `waHref(phoneE164: string, text: string): string` (`https://wa.me/<digits>?text=<enc>`),
  `telHref`, `mailtoHref`.
  `api.ts`: TanStack hooks — `useToday()`, `useLeads()`, `useLeadEvents(leadId)`,
  `useOrgs()`, `useWeekStats()`, `useSettings()` (all `queryKey: ["sales", …]`,
  `fetchJson` transport — F1) and mutations `useOutcome(leadId)`, `useSetStatus(leadId)`,
  `useAddNote(leadId)`, `useSetNextTouch(leadId)`, `useAssign(leadId)`, `useOutreach(leadId)`,
  `useQuickAdd()`, `useSaveSettings()` — every mutation `onSuccess` invalidates
  `["sales"]`; `useOutcome` is optimistic on the today queue (snapshot → remove card →
  rollback on error), the masterprompt §6.2 requirement.
  `useOutcomeCapture.ts`: `useOutcomeCapture()` → `{ pending, arm(leadId, channel), clear() }`;
  `arm` stores `{leadId, channel, at: Date.now()}` in `sessionStorage["gt.sales.outreach"]`
  + fires `useOutreach`; a `visibilitychange`/`focus` listener sets `pending` when the tab
  returns after ≥5s. SSR-safe (guards on `typeof window`).
- `SalesShell` (client): wrapper `<div dir="rtl" lang="he" data-app="sales">`; sticky
  header (screen title, ⌘K button, settings link, "מעבר לייצור" link to `/home`); desktop
  ≥md: start-side slim sidebar (three items + settings); mobile <md: fixed bottom tab bar
  (היום · לידים · עסקים, `env(safe-area-inset-bottom)` padding, 44px+ targets) + FAB
  "+ ליד חדש" slot; active tab from `usePathname()`.
- `(sales)/layout.tsx` (server): loads Rubik via
  `next/font/google` (`Rubik({ subsets: ["hebrew","latin"], variable: "--s-font", display: "swap" })`),
  imports `./sales-tokens.css`, wraps
  `<RoleGate minimum="admin:execute"><div className={rubik.variable}><SalesShell>{children}</SalesShell></div></RoleGate>`.
  No `AppShellChrome`, no `SeedGate` (F5 — deliberate). Exports
  `metadata = { title: "GT Sales", manifest: "/sales-manifest.webmanifest" }` (Task 17
  creates the file; the reference is inert until then).
- `sales/page.tsx`: `redirect("/sales/today")` (next/navigation, server).

- [ ] **Step 1: Failing tests** — `labels.test.ts` (every `LeadStatus` has a Hebrew label;
no English letters in `UI` values via `/[A-Za-z]/` scan except the allowed literals
"WhatsApp" — decide: allowed, brand name), `format.test.ts` (E.164 → display, relative
strings), `wa.test.ts` (`waHref("+972521234567","הי")` →
`https://wa.me/972521234567?text=%D7%94%D7%99`; `fillTemplate` replaces `{{name}}`),
`useOutcomeCapture.test.tsx` (arm → hidden → visible ⇒ pending set; clear() empties
sessionStorage), `sales-shell.test.tsx` (renders `dir="rtl"` wrapper + three tab labels;
active tab carries `.s-tab-active`).
- [ ] **Step 2: Implement all files. Step 3: green + typecheck.**
- [ ] **Step 4: Commit:** `feat(sales): route-group shell, Hebrew labels, client data layer`.

### Task 8: /apps switchboard + login redirect + gates

**Files:**
- Create: `src/app/apps/layout.tsx` (bare: `<RoleGate minimum="viewer:read">` only),
  `src/app/apps/page.tsx`
- Modify: `src/app/(auth)/login/page.tsx:294` (`"/home"` → `"/apps"`),
  `src/app/auth/callback/page.tsx:44` (same), `src/middleware.ts` (two ROLE_GATES rows),
  `src/lib/nav/manifest.ts` (one command-placement item), `scripts/check-no-persona-in-urls.mjs`
  (add `"sales"` in all three places — F19)
- Test: `tests/unit/sales/apps-switchboard.test.tsx`, extend `tests/unit/middleware.test.ts`,
  update `tests/unit/nav/manifest-visibility.test.ts` if it snapshots hrefs

**Interfaces:**
- Produces: `/apps` — client page; reads `useSession()`; while loading → neutral spinner
  (`GTLoader`); role ≠ admin → `router.replace("/home")`; admin → two large cards
  **ייצור** (→ `/home`) / **מכירות** (→ `/sales/today`), each tap sets cookie
  `gt.app.v1=<factory|sales>; path=/; max-age=31536000; SameSite=Lax`; if the cookie
  already names an app on mount → auto-forward with a visible "החלפה" escape link for
  1.2s? **No — locked:** auto-forward immediately; the OTHER app stays one tap away
  inside each shell ("מעבר לייצור" in sales, `/apps` ⌘K entry in factory — P6), simpler
  than a timed interstitial.
- Middleware rows (dormant, P4), FIRST in the table (specific before general):
  `{ prefix: "/sales", allow: ["admin"] }`, `{ prefix: "/apps", allow: ["operator","planner","admin","viewer"] }`.
- NAV_MANIFEST Overview group gains
  `{ href: "/apps", label: "Apps", icon: LayoutGrid, min_role: "viewer", roles: ["admin"], placement: "command" }`.

- [ ] **Step 1: Failing tests** — switchboard: renders both cards for admin (fake session
provider wrapper — mimic an existing session-provider test double under `tests/unit/`),
non-admin replaced to `/home` (mock `next/navigation` router), tap writes cookie;
middleware: `/sales` blocked for operator when claim present, `/apps` public-authed;
persona-script: run `node scripts/check-no-persona-in-urls.mjs` → must still pass after
adding `sales`.
- [ ] **Step 2: Implement. Step 3: green + typecheck + `npx eslint .`.**
- [ ] **Step 4: Commit:** `feat(sales): /apps switchboard, post-login default, dormant role gates`.

### Task 9: Today screen

**Files:**
- Create: `src/app/(sales)/sales/today/page.tsx`,
  `_components/{TodayQueue.tsx,TodayCard.tsx,StatsStrip.tsx,EmptyStates.tsx}`
- Test: `tests/unit/sales/{today-queue.test.tsx,today-card.test.tsx,stats-strip.test.tsx}`

**Interfaces:**
- Consumes: `useToday()`, `useWeekStats()`, labels, `useOutcomeCapture` (armed by Task 10's
  sheet; the card's action row calls `arm`).
- Produces: `TodayQueue` groups by `item_type` in order conversion → returning_customer →
  new_lead → due_follow_up (display order is the VIEW's order — render as delivered, P8);
  section headers 🎉 הומרו / לקוח חוזר / לידים חדשים / מעקבים להיום.
  `TodayCard` variants: conversion (celebration: org, order ref, `fmtMoney(converted_amount)`,
  no actions); returning_customer (distinct accent border-start, customer context line:
  `₪{snapshot yearly}/שנה · הזמנה אחרונה {date}` from `shopify_snapshot` keys
  `total_spent`/`last_order_at` — render only keys present, never invent); new_lead (SLA
  badge from `sla_state`); due_follow_up (next-touch relative time, overdue red).
  Action row (all except conversion): התקשר (`telHref`) · וואטסאפ (`waHref` with template
  per context: returning_customer → `returning_customer`, else `new_lead`) · דחה (opens
  inline next-touch picker: מחר / עוד 3 ימים / עוד שבוע / תאריך → `useSetNextTouch`) ·
  אבוד (reason sheet → `useOutcome` result=lost).
  `StatsStrip`: one line `השבוע: {X} לידים · {Y} בטיפול · {Z} הומרו`, `.s-nums`.
  `EmptyStates`: `QueueDone` ("סיימת להיום ✓" designed state), `QueueError` (network error
  + "נסה שוב" retry button calling `refetch`), `QueueLoading` (3 skeleton cards).

- [ ] **Step 1: `/impeccable shape /sales/today`** — run it, follow its UX-plan output for
this screen (queue card anatomy, section rhythm, celebration treatment). Its plan
constrains layout ONLY — data contract and Hebrew strings stay as specified here.
- [ ] **Step 2: Failing component tests** (queue ordering by item_type; conversion card
shows no action row; SLA badge hidden when `sla_state` null; empty → "סיימת להיום";
error → retry visible).
- [ ] **Step 3: Implement. Step 4: green + typecheck. Step 5: Commit:**
`feat(sales): today queue — the work screen`.

### Task 10: Outcome loop

**Files:**
- Create: `_components/OutcomeSheet.tsx`
- Modify: `_components/TodayCard.tsx` (arm on התקשר/וואטסאפ tap),
  `sales/today/page.tsx` (mount sheet on `pending`)
- Test: `tests/unit/sales/outcome-sheet.test.tsx`

**Interfaces:**
- Consumes: `useOutcomeCapture` (`pending {leadId, channel}`), `useOutcome(leadId)`.
- Produces: bottom sheet (`role="dialog"`, focus-trapped like `MobileNav.tsx:70-96` —
  reuse that trap pattern, not the component), four large buttons (≥56px):
  **ענה, מתקדם** → inline next-touch quick-pick (מחר/עוד 3 ימים/עוד שבוע/תאריך input) →
  `mutate({result:'answered_progressing', next_touch_at})`;
  **לא ענה** → `mutate({result:'no_answer'})` (server defaults tomorrow — P9);
  **וואטסאפ נשלח** → `mutate({result:'whatsapp_sent'})`;
  **אבוד** → required reason picker (לא רלוונטי / אין תקציב / הלך למתחרה / לא עונה ממושך /
  אחר+טקסט) → `mutate({result:'lost', reason})`.
  Dismissal (backdrop/escape) keeps `pending` armed — the sheet re-offers on next return;
  clearing happens ONLY on a captured outcome (masterprompt §5.3 "cleared only by a
  captured outcome"). Success → `clear()`, toast "נרשם ✓", optimistic card removal.

- [ ] **Step 1: Failing tests** (four buttons render; אבוד requires reason before mutate;
dismiss does NOT clear pending; success clears).
- [ ] **Step 2: Implement. Step 3: green. Step 4: Commit:**
`feat(sales): one-tap outcome capture loop`.

### Task 11: GATE — Today surface

- [ ] **Step 1:** Run `/screen-scorecard --scope /sales/today`, then `/design-system-check`.
- [ ] **Step 2:** Fix EVERY finding classified decision-grade-now or flow-completion-next
(files stay within tranche manifest; if a fix needs a file outside it → STOP, report).
Re-run until those two classes are empty. Log polish-later items verbatim into
`docs/portal-os/tranches/162-sales-workspace.md` under a new `## Deferred polish-later`
heading (create it).
- [ ] **Step 3:** Commit: `fix(sales): today-surface gate findings`.

### Task 12: Leads screen + drawer

**Files:**
- Create: `sales/leads/page.tsx`, `_components/{LeadsTable.tsx,LeadDrawer.tsx,EventTimeline.tsx,StatusPill.tsx,SlaBadge.tsx,CustomerBadge.tsx}`
- Test: `tests/unit/sales/{leads-table.test.tsx,lead-drawer.test.tsx,event-timeline.test.tsx,status-pill.test.tsx}`

**Interfaces:**
- Consumes: `useLeads()`, `useLeadEvents(leadId)`, mutations, labels, `wa.ts`, P1 (no bulk).
- Produces: status tabs חדש/בטיפול/הומר ✓/אבוד with live counts; always-visible search
  input filtering client-side on `contact_name`/`org_name`/`phone_e164` (query digits
  normalised: strip non-digits, `0…`→`+972…` before matching — P7); default sort = view
  order (new + overdue on top); row: org_name (sticky start column, anchor) · contact ·
  phone (`fmtPhone`, `.s-nums`) · campaign/platform · age (`{age_days} ימים`) · SlaBadge
  (renders null when `sla_state` null) · CustomerBadge (₪/yr when snapshot has
  `total_spent`) · next-touch date · subtle "כפול?" chip when `possible_duplicate_of`.
  Row click → LeadDrawer from inline-end (logical `end-0` positioning, translate-x
  animation 200ms): all fields · EventTimeline (Hebrew labels via `EVENT_LABELS`, payload
  rendering per type: note text, status from→to, outcome result label) · actions: status
  select (בטיפול; אבוד opens reason modal), add-note textarea, next-touch date input,
  assignee free-text input (P3: stores email), `tel:`/`wa.me`/`mailto:` links · when
  status=won: evidence banner "הומר — הזמנה {converted_order_ref}" and NO status controls.
  Mobile: drawer becomes full-screen sheet.
  Deep link: on mount the page reads `useSearchParams().get("lead")` and, when the id
  exists in the loaded rows, opens the drawer on it (CommandK and OrgCard navigate with
  `/sales/leads?lead=<id>`).

- [ ] **Step 1: `/impeccable shape /sales/leads`** (table density, drawer anatomy, tab
treatment — layout only).
- [ ] **Step 2: Failing tests** (tab counts; search matches phone typed as `052…`; drawer
shows timeline; won lead shows banner and no status select; lost requires reason).
- [ ] **Step 3: Implement. Step 4: green + typecheck. Step 5: Commit:**
`feat(sales): leads table + drawer`.

### Task 13: GATE — Leads surface

Same three steps as Task 11 with `--scope /sales/leads`. Commit:
`fix(sales): leads-surface gate findings`.

### Task 14: Orgs screen

**Files:**
- Create: `sales/orgs/page.tsx`, `_components/{OrgList.tsx,OrgCard.tsx}`
- Test: `tests/unit/sales/{org-list.test.tsx,org-card.test.tsx}`

**Interfaces:**
- Consumes: `useOrgs()`, `useLeads()` (drawer's per-org lead slice), `useLeadEvents`.
- Produces: list rows (name · phone · CustomerBadge · `{lead_count} לידים` ·
  `fmtRelative(last_activity_at)`), same search box semantics as leads; row → OrgCard
  **drawer** (P2): identity fields · dated Shopify context when snapshot exists
  ("נכון ל-{fmtDate(shopify_snapshot_at)}: ₪{total_spent}…" — only present keys) · its
  leads (mini-rows linking into `/sales/leads?lead=<id>` — the Task 12 deep link) ·
  merged event timeline (events of all its leads, newest first, reusing `EventTimeline`).
  Deep link: the page reads `useSearchParams().get("org")` on mount and opens the drawer
  (CommandK navigates with `/sales/orgs?org=<id>`).

- [ ] **Step 1: `/impeccable shape /sales/orgs`. Step 2: failing tests** (customer badge;
snapshot renders dated; no snapshot → no invented numbers). **Step 3: implement.
Step 4: green. Step 5: Commit:** `feat(sales): org account pages`.

### Task 15: GATE — Orgs surface

Same as Task 11 with `--scope /sales/orgs`. Commit: `fix(sales): orgs-surface gate findings`.

### Task 16: Quick-add, search, settings

**Files:**
- Create: `_components/{QuickAddSheet.tsx,CommandK.tsx,SettingsForm.tsx}`,
  `sales/settings/page.tsx`
- Modify: `SalesShell.tsx` (FAB opens QuickAddSheet; ⌘K/search button opens CommandK)
- Test: `tests/unit/sales/{quick-add.test.tsx,command-k.test.tsx,settings-form.test.tsx}`

**Interfaces:**
- QuickAddSheet: three fields — שם איש קשר (required) · טלפון · שם העסק — plus free-text
  מקור/הערה; submit → `useQuickAdd()` → success toast "ליד נוצר ✓" + invalidate; ten-second
  flow, autofocus first field.
- CommandK: overlay (desktop ⌘K/Ctrl+K via keydown listener in SalesShell; mobile search
  icon) searching leads + orgs client-side (P7, same normalisation); result rows navigate
  to the matching drawer (`/sales/leads?lead=` / `/sales/orgs?org=`); Esc closes; paste a
  phone number → answers "מי זה?" instantly.
- SettingsForm (`/sales/settings`, via header/menu link — NOT a bottom tab, addendum-2 §13):
  exactly two blocks — WhatsApp templates (three labeled textareas: ליד חדש / תזכורת /
  לקוח חוזר, `{{name}}` hint line) and SLA hours (numeric input, default 24, S-01) —
  `useSaveSettings()`; nothing else on this screen.

- [ ] **Step 1: `/impeccable shape` for the quick-add sheet + settings screen (one run,
`--scope /sales/settings` argument form: `/impeccable shape /sales/settings`).**
- [ ] **Step 2: failing tests** (quick-add requires contact name; ⌘K filters by pasted
phone; settings saves both keys). **Step 3: implement. Step 4: green. Step 5: Commit:**
`feat(sales): quick-add, global search, settings`.

### Task 17: PWA

**Files:**
- Create: `public/sales-manifest.webmanifest`, `public/sales-icons/icon-192.png`,
  `public/sales-icons/icon-512.png`, `public/sales-icons/maskable-512.png`,
  `public/sales-icons/apple-touch-icon.png`
- Test: `tests/unit/sales/manifest.test.ts` (parses the webmanifest JSON: name "GT Sales",
  start_url "/sales/today", display "standalone", 4 icons exist on disk)

- [ ] **Step 1: Generate icons (F21 — commands verified live in Phase A):**

```bash
cd /home/user/gt-factory-os-portal && mkdir -p public/sales-icons
npx --yes sharp-cli@5.2.0 resize 192 192 --fit contain --background "#ffffff" -i public/brand/logo.png -o public/sales-icons/icon-192.png
npx --yes sharp-cli@5.2.0 resize 512 512 --fit contain --background "#ffffff" -i public/brand/logo.png -o public/sales-icons/icon-512.png
npx --yes sharp-cli@5.2.0 resize 512 512 --fit contain --background "#1c5a5a" -i public/brand/logo.png -o public/sales-icons/maskable-512.png
npx --yes sharp-cli@5.2.0 resize 180 180 --fit contain --background "#ffffff" -i public/brand/logo.png -o public/sales-icons/apple-touch-icon.png
```

- [ ] **Step 2: Write `public/sales-manifest.webmanifest`:**

```json
{
  "name": "GT Sales",
  "short_name": "GT Sales",
  "start_url": "/sales/today",
  "scope": "/sales/",
  "display": "standalone",
  "dir": "rtl",
  "lang": "he",
  "background_color": "#ffffff",
  "theme_color": "#1c5a5a",
  "icons": [
    { "src": "/sales-icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/sales-icons/icon-512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "/sales-icons/maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ]
}
```

The `(sales)/layout.tsx` metadata from Task 7 already links it (scoped: only sales pages
carry the `<link rel="manifest">` — factory surfaces untouched, F8). Add
`<link rel="apple-touch-icon" href="/sales-icons/apple-touch-icon.png">` via the same
metadata export (`icons: { apple: "/sales-icons/apple-touch-icon.png" }`).
- [ ] **Step 3: manifest.test.ts green. Step 4: Commit:** `feat(sales): installable PWA (scoped manifest + icons)`.

### Task 18: impeccable quality floor

- [ ] **Step 1:** `/impeccable audit /sales` — fix every finding it can auto-classify;
a11y (labels, focus order, contrast on pills/badges), responsive, perf.
- [ ] **Step 2:** `/impeccable onboard /sales/today` — first-run/empty-state pass over the
designed empty states (per-tab empties on leads, queue-done, error+retry).
- [ ] **Step 3:** `/impeccable polish /sales` then `/impeccable harden /sales` — error
states, edge cases (long Hebrew names, missing phone, null snapshot), i18n edge (bidi:
Latin order refs inside Hebrew → wrap in `<bdi dir="ltr">`, F6 convention).
- [ ] **Step 4:** vitest + typecheck + eslint all green. Commit:
`fix(sales): impeccable audit/onboard/polish/harden pass`.

### Task 19: Playwright + real-data evidence

**Files:**
- Create: `tests/e2e/sales-today.spec.ts`, `tests/e2e/sales-leads.spec.ts`,
  `tests/e2e/mobile-sales-today.spec.ts` (all `@mocked` — F9)

- [ ] **Step 1: Write the three specs (failing first — routes exist but stubs unrouted).**
Pattern (F9): `setFakeRole(page, "admin")`; `page.route("**/api/sales/**", …)` with a
mutable stub state object (procurement-focus.spec.ts style). Critical paths, drafted:

```ts
// tests/e2e/sales-today.spec.ts  @mocked
import { test, expect } from "@playwright/test";
import { setFakeRole } from "./helpers";

const lead = {
  lead_id: "L1", item_type: "new_lead", org_id: "O1", org_name: "קפה בדיקה",
  contact_name: "דנה", phone_e164: "+972521234567", email: null,
  campaign_name: "קמפיין קיץ", platform: "fb", status: "new", assignee: null,
  next_touch_at: null, first_touch_at: null, created_at: new Date().toISOString(),
  is_existing_customer: false, shopify_snapshot: null, shopify_snapshot_at: null,
  converted_order_ref: null, converted_amount: null, converted_at: null,
  sla_deadline_at: new Date(Date.now() + 20 * 3600e3).toISOString(), sla_state: "within",
};
const posted: Array<{ url: string; body: unknown }> = [];

test("queue renders, outcome captured, event written @mocked", async ({ page }) => {
  await setFakeRole(page, "admin");
  let rows = [lead];
  await page.route("**/api/sales/week-stats**", (r) =>
    r.fulfill({ json: { stats: { week_new_leads: 1, working_now: 0, week_converted: 0 } } }));
  await page.route("**/api/sales/today**", (r) => r.fulfill({ json: { rows } }));
  await page.route("**/api/sales/leads/L1/outreach", (r) => {
    posted.push({ url: r.request().url(), body: r.request().postDataJSON() });
    return r.fulfill({ json: { lead_id: "L1", event_id: "E1" } });
  });
  await page.route("**/api/sales/leads/L1/outcome", (r) => {
    posted.push({ url: r.request().url(), body: r.request().postDataJSON() });
    rows = []; // captured outcome clears the queue
    return r.fulfill({ json: { lead_id: "L1", status: "working",
      next_touch_at: new Date(Date.now() + 86400e3).toISOString(),
      first_touch_at: new Date().toISOString() } });
  });

  await page.goto("/sales/today");
  await expect(page.getByText("קפה בדיקה")).toBeVisible();
  await expect(page.getByText("השבוע: 1 לידים · 0 בטיפול · 0 הומרו")).toBeVisible();

  await page.getByRole("link", { name: "התקשר" }).click(); // tel: is a no-op in chromium
  await page.evaluate(() => document.dispatchEvent(new Event("visibilitychange")));
  await expect(page.getByRole("dialog")).toBeVisible(); // outcome sheet

  await page.getByRole("button", { name: "ענה, מתקדם" }).click();
  await page.getByRole("button", { name: "מחר" }).click();
  await expect(page.getByText("סיימת להיום ✓")).toBeVisible();
  expect(posted.some((p) => p.url.includes("/outreach"))).toBeTruthy();
  const outcome = posted.find((p) => p.url.includes("/outcome"));
  expect((outcome?.body as { result: string }).result).toBe("answered_progressing");
});
```
`sales-leads.spec.ts`: stub 3 leads across statuses; assert tab counts; switch tab; open
drawer; choose status בטיפול; assert POST `/status` body `{status:"working"}`; timeline
stub shows the event row after invalidation. `mobile-sales-today.spec.ts` (iPhone 14
project via filename — F9): bottom tab bar visible, three tabs, FAB present, tap לידים
navigates.
NOTE (arm-before-return): the outreach tap must set the `useOutcomeCapture` arm even when
`tel:` navigation is inert in the test browser — arm on pointerdown/click BEFORE the
default anchor action; the spec's `visibilitychange` dispatch then triggers the sheet.
The ≥5s return-delay guard must read a constant that the test can lower via
`window.__GT_SALES_OUTCOME_DELAY_MS__ ?? 5000` — implement that hook in
`useOutcomeCapture.ts` (test sets it to 0 in an init script).
- [ ] **Step 2:** `npx playwright test --grep @mocked` → all green (existing 14 files +
3 new).
- [ ] **Step 3: Real-data screenshots** (Phase B session runs the dev server against the
live API): desktop + mobile viewports of `/sales/today` (real queue), `/sales/leads`
(188 rows), open drawer, org card, an empty state. Crop or pick non-sensitive rows (PII
lock). Save under the session workspace, attach to the PR body (Task 22). Then one SQL
paste: `select event_type, actor, created_at from sales_core.lead_event order by created_at desc limit 3`
after performing one real outcome tap — the row a UI action created.
- [ ] **Step 4: Commit:** `test(sales): e2e critical paths + evidence pack`.

### Task 20: Regression guard + UX release gate loop

- [ ] **Step 1:** `/portal-regression-guard` → must be green (shell/nav/middleware were
touched in Task 8). Any drift finding → fix before proceeding.
- [ ] **Step 2 (addendum §2–§3):** Run `/ux-release-gate --scope /apps /sales/today
/sales/leads /sales/orgs /sales/settings`. Record the verdict.
- [ ] **Step 3:** If verdict < SHIP: fix ALL named blockers + conditional items, re-run.
Maximum **3 total iterations**. If run 3 is still below SHIP → STOP, report the remaining
blockers to Tom verbatim, do not loop further.
- [ ] **Step 4:** Commit fixes per iteration: `fix(sales): ux-release-gate iteration N`.

### Task 21: Portal-OS bookkeeping + verifier

- [ ] **Step 1:** `docs/portal-os/route-manifest.json`: add rows (status `live`,
group `sales`, `roles:["admin"]`) for `/apps`, `/sales`, `/sales/today`, `/sales/leads`,
`/sales/orgs`, `/sales/settings` (follow the existing row shape exactly; `/sales` gets
`status:"redirect"`).
- [ ] **Step 2:** `docs/portal-os/registry.md`: append tranche line
`- docs/portal-os/tranches/162-sales-workspace.md — GT Sales Workspace: /apps + (sales) group (Today queue, outcome loop, leads, orgs, quick-add, PWA)`.
- [ ] **Step 3:** `/portal-scorecard` — factory categories must be unchanged; record a
`_notes` entry naming tranche 162 as out-of-rubric (new module surface). Any factory
regression → HALT and fix.
- [ ] **Step 4:** Dispatch `portal-tranche-verifier` for tranche 162 (manifest compliance,
typecheck, vitest, playwright @mocked, no baseline regressions). Paste its evidence into
`162-sales-workspace.md` under `## Actual evidence`.
- [ ] **Step 5:** Commit: `docs(sales): tranche 162 bookkeeping + verification evidence`.

### Task 22: PRs + state updates + final report

- [ ] **Step 1:** Push both repos (`git push -u origin claude/caveman-mode-oenfxl`,
retry ×4 backoff on network failure). Open/refresh **draft** PRs:
portal (base main) and gt-factory-os (base main). Bodies include: what shipped per §5 of
the masterprompt, screenshots (cropped), the SQL evidence paste, pgTAP 24/24 + 14/14,
api tests N/N, vitest N/N, playwright N/N, **the ux-release-gate verdict + iteration
count + deferred polish-later list (addendum §4)**, rollback line. No lead PII.
- [ ] **Step 2:** `Sales-Machine/CURRENT_STATE.md`: update the build status — portal
workspace shipped (PR links), settings store live (`sales_core.app_setting`), close/annotate
U-010 (SLA now a live parameter, default 24) — dated 2026-08-17+, and keep S-04/U-011 open.
Commit + push on `claude/caveman-mode-oenfxl`, draft PR.
- [ ] **Step 3:** production-brain: tick the build-record row in
`docs/decisions/modules/sales-declaration.md` (add PR numbers), commit, push, update the
existing draft PR.
- [ ] **Step 4: Final report** with the 8 PASS fields: files changed · tests N/N (pgTAP,
api, vitest, playwright) · contracts referenced (masterprompt §5–§6, addenda 1+2,
tranche 162) · signals emitted · stop conditions tripped (none, or listed) · Tom
approvals required (merge of the 3 draft PRs) · rollback plan (revert PRs; views/functions
droppable; event-type extension stays) · next handoff (Meta intake track blocked on
credentials; S-04; U-011). End with `Next action: …`.

---

## Self-review record (Phase A)

- Spec coverage: §5.1 IA (T7/T8/T9/T12/T14/T16) · §5.2 queue+stats (T3/T9) · §5.3 loop
  incl. event-type extension + first-touch + no-open-lead-without-next-touch (T2/T10) ·
  §5.4 table+drawer (T12) · §5.5 orgs (T14) · §5.6 quick-add/search/PWA (T16/T17) ·
  §5.7 settings (T2/T16) · §5.8 visual language (T6 + impeccable) · §5.9 deferrals
  (P1 + tranche out-of-scope) · §6.1 shell (T6/T7/T8) · §6.2 data layer (T2–T5) ·
  §6.3 gates (T11/T13/T15/T18–T21) · addendum 1 (T11/T13/T15/T18/T20/T22 evidence) ·
  addendum 2 items 1–16 (F-table + P-locks; item 2's stale tranche number corrected by
  F22).
- Placeholder scan: no TBD/TODO/"similar to"; the two full SQL bodies live as sibling
  files (next section) to keep them byte-exact rather than paraphrased.
- Type consistency: `SalesLeadRow`/`TodayRow` field lists match the 0323 view columns;
  handler names in T4 match the T5 stubs and T7 hooks; `useOutcomeCapture` API matches
  T9/T10 consumers.

## Sibling SQL files (canonical, copy byte-for-byte in Tasks 2/3)

- `docs/superpowers/plans/2026-08-17-sales-workspace-sql/0322_sales_core_workspace_writes.sql`
- `docs/superpowers/plans/2026-08-17-sales-workspace-sql/0323_sales_api_read_views.sql`
