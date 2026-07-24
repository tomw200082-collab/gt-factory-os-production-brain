# Production Rollout Plan — "מעגל פקודת הייצור" → Full Production for Denis

> **Executor:** NEW session, Sonnet 5, autonomous end-to-end. Written to leave ZERO room for
> judgment: exact commands, exact paths, a verification gate after every phase, explicit
> failure branches. Master prompt for the new session at the end.
> **Handoff mechanics:** after Tom approves this plan, THIS session commits it to
> `gt-factory-os-production-brain/docs/plans/2026-07-24-production-picking-rollout.md` on the
> designated branch and pushes, so the new session can read it (the local plan file does not
> exist in a fresh container).

## Context — why

Tom approved (brain PR #62 **MERGED** 2026-07-24 = written approval; LOCKED_DECISIONS v2
authoritative) the picking-based production cycle: Denis opens today's runs at `/production`,
collects materials per BOM with prefilled editable quantities, **stock decrements at pick
confirmation** (`PICK_CONSUMPTION`), corrections are append-only deltas, end-of-run report
posts output + scrap + optional QC. Code is COMPLETE and 4-auditor-reviewed on branch
`claude/production-materials-collection-page-mbqh7k` in both code repos. Remaining: merge →
migrate → deploy → cutover → floor names → Denis's account → **2 polish iterations**
(/ux-release-gate + /frontend-design + /ui-ux-pro-max) → dry run → **flawless workday for
Denis on the next production day (Sunday)**.

## Tom's locked decisions (2026-07-24, in writing — do not re-ask)

1. Denis's login: **`production@gteveryday.com` + password** (generated; Tom types it into
   Denis's phone once). Role `operator`, display name `Denis`.
2. Cutover of `/stock/production-actual`: **immediately with the deploy** (old page stays
   reachable by direct URL for 30 days; only nav/tiles/links move).
3. Autonomous merges AND autonomous production deploy + prod-DB migration are both standing
   policy (CLAUDE.md, amended 2026-07-24): announce in chat right before dispatch, then proceed
   immediately — never wait for a reply. This is now permanent, project-wide, not specific to
   this rollout.
4. Floor names: generate draft → post to Tom in chat for one-pass approval → if no reply by
   the time everything else is done, SHIP WITHOUT (Hebrew fallback works; coverage flag shows)
   and leave the draft pending in chat.

## Current state (verified 2026-07-24 by the authoring session)

| Piece | Where | State |
|---|---|---|
| Governance | brain PR #62 | **MERGED**. Do not touch LOCKED_DECISIONS again. |
| Backend | `gt-factory-os` PR #183, branch `claude/production-materials-collection-page-mbqh7k` | Complete: migration `db/migrations/0295_production_run_picking.sql`, pgTAP `db/tests/0295_production_run_picking.test.sql` (plan(30), NEVER RUN — no DB in sandbox), module `api/src/production-runs/*`, wired in `api/src/server.ts` (~line 145). Local `npm run typecheck` clean (verified incl. fresh `npm ci`). CI check `typecheck` failing at RUNNER level (proven not-code: one failure was on a commit that only renamed .sql files). |
| Portal | `gt-factory-os-portal` PR #183, same branch | Tranches 141+142 complete (list + picking + report + 4-auditor UX fixes). `portal-pr-guard / ci` **green**. Vercel preview deployed. Active tranche: `142`. |
| Not built (tranche 143) | — | Old-screen cutover, `components.floor_name`, Denis's account, double-consumption guard. Phase 1/2 below. |

## Infrastructure facts (verified — trust these)

- **Backend deploy:** manual `workflow_dispatch` of `.github/workflows/deploy-production.yml`
  (repo `gt-factory-os`). Inputs: `confirm` (must be `APPLY`), `migrations` (bash glob, e.g.
  `db/migrations/029[5-8]_*.sql`), `skip_deploy` (default false). Job `migrate`: pre-flight
  `rebuild_verifier()` → `psql -v ON_ERROR_STOP=1` per file → post-checks. Job `deploy`:
  Railway `railway up --service gt-factory-os-api` → polls
  `https://gt-factory-os-api-production.up.railway.app/health` for `"ok":true` (30×10s).
  Secrets: `DATABASE_URL_POOLED` (Supabase pooler), `RAILWAY_TOKEN`.
- **Portal deploy:** Vercel, auto on merge to `main`. No staging; preview per-PR.
- **Auth/provisioning:** `private_core.app_users` (role CHECK admin/planner/operator/viewer);
  PK = `auth.users.id` by convention; `api/src/auth/session.ts` back-fills `user_id` by EMAIL
  match on first login; unprovisioned → 403. No self-service signup. Seed patterns:
  `0058_app_users_tom_admin_seed.sql` (app_users row) and `0059_fixture_auth_users_non_admin.sql`
  (**creates `auth.users` + `auth.identities` rows directly in SQL** — the model to copy;
  add `encrypted_password = crypt('<pw>', gen_salt('bf'))` for password login, pgcrypto).
  Portal login page supports password mode (`signInWithPassword`).
- **Cutover touchpoints (complete list, file:line verified):**
  1. `src/lib/nav/manifest.ts:241` — old nav entry (remove; `/production` entry already exists)
  2. `src/features/dashboard/quick-actions.ts:87` — quick action → `/production`
  3. `src/features/home/cockpit.ts:263` — old home tile (remove; new tile exists) + test `cockpit.test.ts:137`
  4. `src/app/(planning)/planning/production-plan/page.tsx:2295` — "Open Production Report" → `/production`
  5. `src/app/(planning)/planning/production-plan/_components/ProductionJobCard.tsx:99,100` — `?from_plan_id=` links → `/production`; **line 564 `?submission_id=` history-detail link STAYS on the old page** (history detail has no new equivalent)
  6. `src/app/(planning)/planning/runs/[run_id]/recommendations/[rec_id]/page.tsx:288` — link → `/production`
  7. `src/app/(planning)/planning/inventory-flow/_components/PlannedItemSection.tsx:138` — `?item_id=` link → `/production`
  - Old page route + `/api/production-actuals/*` proxies + dashboard/today-board consumers STAY (data layer unchanged).
- **TANK derivation verified safe:** `production_plan.batch_size_l numeric NOT NULL DEFAULT 500`
  (0133); for base-batch rows `planned_qty = batch_size_l, uom='L'` (0139 CHECK). Handler reads
  `batch_size_l ?? planned_qty` — correct. `pack_manifest` = jsonb array of `{item_id, qty}`.
- **Portal hooks (WILL block):** PreToolUse manifest gate (any `src/**` write must be listed in
  the ACTIVE tranche's `manifest:` block — author tranche doc + registry line + `_active.txt`
  FIRST); SubagentStop (subagent "done" claims need `Evidence: <path>`); Stop hook (every final
  message needs a `Next action: …` line).
- Backend health: `GET /health` → `{ok:true}` (server.ts:99).
- Supabase MCP tools are available in-session (list_projects, create_branch, execute_sql,
  apply_migration, delete_branch, confirm_cost). GitHub MCP available (actions_run_trigger,
  merge_pull_request, etc.).

## Guardrails (absolute)

1. `stock_ledger` append-only — NEVER UPDATE/DELETE; corrections = reversal/delta rows.
2. Prod-DB migration apply + prod deploy = autonomous, standing policy (CLAUDE.md, 2026-07-24):
   post a chat message immediately before each dispatch, then proceed without waiting for a reply.
3. NEVER edit `tailwind.config.ts`, `globals.css`, `baseline.json`, `quarantine.json`,
   UX-standard docs, `CLAUDE.md` (any repo), `LOCKED_DECISIONS.md`.
4. Only branch `claude/production-materials-collection-page-mbqh7k` (all repos). `git add`
   explicit paths only. `git push -u origin <branch>`; retry ×4 exponential on network fail.
5. Merge PRs only with green checks — EXCEPT the documented backend `typecheck` runner failure:
   protocol in Phase 1 Step 5.
6. Frozen flags untouched. No new authority docs. No Excel writes.
7. Gate failed and unfixable within the phase → STOP, report exact error to Tom, do NOT skip.
8. All new user-facing strings: simple English (weak reader), via `_lib/copy.ts` only.

---

# PHASES

## Phase 0 — Boot & sanity (~10 min)

1. Verify repos + branch: for each of `/home/user/gt-factory-os`, `/home/user/gt-factory-os-portal`,
   `/home/user/gt-factory-os-production-brain`: `git fetch origin && git checkout claude/production-materials-collection-page-mbqh7k && git pull origin claude/production-materials-collection-page-mbqh7k` (create from origin if absent).
2. Read the committed plan: `gt-factory-os-production-brain/docs/plans/2026-07-24-production-picking-rollout.md` (this file).
3. Sanity gates (must all pass before continuing):
   - Backend: `cd /home/user/gt-factory-os && npm ci && npm run typecheck` → exit 0.
   - Portal: `cd /home/user/gt-factory-os-portal && npm ci && npx tsc --noEmit && npx eslint .`
     → tsc 0, eslint **0 errors** (≈281 pre-existing warnings are FINE).
   - Portal tests: `npx vitest run` → all green (~1050+).
4. Merge latest `main` into the branch in BOTH code repos (`git merge --no-edit origin/main`),
   re-run the gates above. If a NEW migration number ≥0295 appeared on main, renumber ours
   (see Phase 1 Step 1).
   **Gate 0:** all green. FAIL → fix type/test breakage from the merge before continuing.

## Phase 1 — Backend complete + validated + merged

### Step 1 — Renumber check
`ls /home/user/gt-factory-os/db/migrations/ | sort | tail -8`. Our migration must hold the
next free number. If main took `0295`, `git mv` ours (+ its test) to the next free NNNN and
`sed -i 's/0295/NNNN/g'` inside both files. All references below assume 0295/0296/0297/0298 —
shift consistently if renumbered.

### Step 2 — Author the three new migrations (on the branch)

**0296_components_floor_name.sql** (pattern: copy header style of 0295):
```sql
begin;
set search_path to private_core, public;
alter table private_core.components
  add column if not exists floor_name text null;
comment on column private_core.components.floor_name is
  '0296 — optional Latin-script display name for the production floor (operator is a weak Hebrew/English reader). Shown big on /production pick rows; component_name (Hebrew) shown small as fallback/cross-check. NULL = fall back to component_name.';
commit;
```
Paired test `db/tests/0296_components_floor_name.test.sql` (pgTAP, plan(2): `has_column`,
column is nullable — copy assertion style from `0060_production_actual.test.sql`).

**0297_app_users_denis_operator_seed.sql** — model EXACTLY on
`0059_fixture_auth_users_non_admin.sql` (read it first; copy its INSERT shapes for
`auth.users` + `auth.identities`, idempotent `on conflict do nothing` / where-not-exists):
- Email `production@gteveryday.com`, fixed uuid (generate one, hardcode it), `role='operator'`,
  `display_name='Denis'`, `status='active'`, `site_id='GT-MAIN'` in `private_core.app_users`.
- `auth.users.encrypted_password = crypt('<GENERATED_PW>', gen_salt('bf'))` — generate the
  password as 3 lowercase words + 2 digits (e.g. `mango-tiger-42…`), easy to type on a phone.
  **Write the chosen password into the chat handoff message for Tom (Phase 6) — nowhere else.
  Never commit it in plaintext anywhere except this seed migration** (acceptable: repo is
  private and this mirrors 0059's approach; note it in the PR body).
- Guard: if an auth.users row with that email already exists, only upsert app_users.
Paired test `0297_….test.sql` (plan(3): app_users row exists with role operator; auth user
exists; email matches).

**0298_component_floor_names_backfill.sql** — ONLY IF Tom approves the draft (Phase 3 Step 3).
Idempotent `update private_core.components set floor_name='…' where component_id='…' and floor_name is null;` per row.

### Step 3 — Double-consumption guard (backend code)
File: `api/src/production-actuals/handler.ts` (the OLD submit handler — minimal addition,
INSIDE `handleProductionActualSubmit` after item validation, before consumption planning):
query `private_core.production_run` for `item_id = <submitted item>` AND
`status in ('IN_PRODUCTION','REPORTED')` AND `created_at::date = (event_at)::date`; if found →
return `conflictResult('PICKING_RUN_EXISTS', 'This item was produced via the picking flow today (run <run_id>); report it from /production instead', 'item_id')`.
Add `'PICKING_RUN_EXISTS'` to the conflict-reason union in `api/src/production-actuals/schemas.ts`.
Also: backend pick-list/today handlers (`api/src/production-runs/handler.ts`): add
`c.floor_name` to the components SELECTs and include `floor_name: string | null` in
`PickListLine` (`api/src/production-runs/schemas.ts`) — the portal types already tolerate it.
**Gate:** `npm run typecheck` → 0.

### Step 4 — Validate migrations on a Supabase branch (ANNOUNCE in chat first: read-only-risk, isolated branch)
1. `mcp__Supabase__list_projects` → find the GT project id (the one whose name matches
   gt-factory-os / GT Everyday).
2. `mcp__Supabase__create_branch` (confirm cost first via `confirm_cost` if prompted).
3. Apply IN ORDER via `mcp__Supabase__apply_migration` (branch id!): 0295, 0296, 0297.
4. Structural asserts via `mcp__Supabase__execute_sql` on the branch (each must return true):
   - `select count(*)=2 from information_schema.tables where table_schema='private_core' and table_name in ('production_run','production_run_pick');`
   - `select count(*)=4 from information_schema.columns where table_schema='private_core' and table_name='production_actual' and column_name in ('qc_brix','qc_ph','qc_sample_taken','qc_note');`
   - `select pg_get_constraintdef(oid) like '%PICK_CONSUMPTION%' from pg_constraint where conname='stock_ledger_movement_type_chk';`
   - `select exists(select 1 from information_schema.columns where table_schema='private_core' and table_name='components' and column_name='floor_name');`
   - `select exists(select 1 from private_core.app_users where email='production@gteveryday.com' and role='operator');`
   - `select private_core.rebuild_verifier() = 0;`  *(column name/shape per 0009 — if the function returns rows, assert zero mismatch rows as `select count(*)=0 from private_core.rebuild_verifier() …` matching how deploy-production.yml calls it — READ that workflow's post-check SQL and copy it verbatim.)*
   - Write-path smoke (branch only!): insert one `form_submissions` envelope + one
     `PICK_CONSUMPTION` ledger row against an existing component id (pick any:
     `select component_id, inventory_uom from private_core.components limit 1`), then assert
     the row exists and `current_balances` moved by the delta; then insert the SAME
     idempotency_key again and assert it RAISES unique_violation (wrap in DO block with
     exception handler returning 'DUPLICATE_BLOCKED').
5. `mcp__Supabase__delete_branch`. **Gate 1a:** every assert true. FAIL → fix the migration on
   the branch repo-side, recreate branch, repeat. Never proceed with a failing assert.

### Step 5 — CI + merge backend PR #183
1. Commit + push everything from Steps 1–3 (explicit paths).
2. Check PR #183 checks (`mcp__github__pull_request_read` method get_check_runs). If
   `typecheck` fails: re-trigger once (`mcp__github__actions_run_trigger` on
   `typecheck.yml`, ref = the branch) and/or push-triggered rerun already happened.
3. If it PASSES → `mcp__github__merge_pull_request` (squash).
4. If it STILL fails: reproduce locally `npm ci && npm run typecheck` → if exit 0, this is the
   DOCUMENTED runner/infra failure (see PR comment from 2026-07-24). Tom pre-approved the
   merge in writing ("אני מאשר הכל. תמזג ותמשיך", 2026-07-24). Post a PR comment stating:
   local `npm ci`+`tsc` clean at <sha>, failure reproduced as infra (attach the evidence
   summary), merging per Tom's written approval → then merge (squash). If local typecheck
   FAILS → it IS a code error: fix it first. **Gate 1b:** backend PR merged.

## Phase 2 — Portal tranche 143 (cutover) + merge

1. **Author tranche 143 FIRST** (hooks): create
   `docs/portal-os/tranches/143-production-cutover.md` copying the exact format of
   `142-production-run-report.md`, with `manifest:` listing EXACTLY:
   ```
   - src/lib/nav/manifest.ts
   - src/features/dashboard/quick-actions.ts
   - src/features/home/cockpit.ts
   - src/features/home/cockpit.test.ts
   - src/app/(planning)/planning/production-plan/page.tsx
   - src/app/(planning)/planning/production-plan/_components/ProductionJobCard.tsx
   - src/app/(planning)/planning/runs/[run_id]/recommendations/[rec_id]/page.tsx
   - src/app/(planning)/planning/inventory-flow/_components/PlannedItemSection.tsx
   - src/app/(production)/production/_lib/types.ts
   - src/app/(production)/production/runs/[run_id]/_components/PickRow.tsx
   - tests/e2e/production-picking.spec.ts
   ```
   Append one-line entry to `docs/portal-os/registry.md` under `## Tranches`; set
   `docs/portal-os/tranches/_active.txt` to `143`.
2. Apply the 7 cutover re-points (facts list above; keep ProductionJobCard's `?submission_id=`
   history link on the old page). Remove the old nav entry + old cockpit tile (new `/production`
   entries exist); fix `cockpit.test.ts:137`. If `tests/unit/nav/manifest-visibility.test.ts`
   snapshot breaks, update it AND add that path to the tranche manifest block first.
3. `floor_name` display: in `_lib/types.ts` confirm `floor_name?: string|null` on
   `PickListLine`; in `PickRow.tsx` render `line.floor_name ?? line.component_name` as the big
   name and, when `floor_name` is present, the Hebrew `component_name` small under it in
   `<bdi>` (the `name_he` slot pattern already exists — reuse it).
4. Gates: `npx tsc --noEmit` (0) → `npx eslint .` (0 errors) → `npx vitest run` (all green;
   update any test asserting the old links) → e2e:
   `NEXT_PUBLIC_ENABLE_DEV_SHIM_AUTH=true npm run dev` (background) then
   `npx playwright test --grep @mocked` → all green (Chromium at `/opt/pw-browsers`; do NOT
   `playwright install` — set `executablePath`/env per repo config if needed).
5. Commit (explicit paths) + push. Wait for `portal-pr-guard / ci` green on PR #183 →
   **merge portal PR #183** (squash). **Gate 2:** merged + `ci` green. NOTE: production Vercel
   will now deploy a portal calling endpoints that go live in Phase 3 — acceptable ONLY because
   Phase 3 runs immediately next (same session, minutes later). Do not pause between 2 and 3.

## Phase 3 — THE production deploy (announce, then IMMEDIATELY proceed — no pause)

> **✅ Resolved (2026-07-24):** deploy autonomy is now PERMANENT, project-wide policy — not
> just for this rollout. `gt-factory-os-production-brain/CLAUDE.md` has been amended (Write
> boundaries + External-action authorization §5, footer dated 2026-07-24): Claude may dispatch
> production deploys (migrations + Railway) autonomously whenever the deploy's own gates are
> green, mirroring the existing autonomous-merge grant. The ONE thing that does not change:
> still POST a one-line chat announcement immediately before dispatching — visibility, not
> permission; never wait for a reply. Ledger append-only / reversal-only semantics are
> completely untouched by this — only deploy mechanics moved from "ask first" to "announce and
> proceed." Any future deploy task (not just this rollout) inherits this policy directly from
> CLAUDE.md — no need to re-derive or re-confirm it.

1. Post in chat (Hebrew, one line): applying migrations 0295–0297(+0298 if approved) to the
   production DB + deploying the API to Railway. **Do not wait for a reply — proceed
   immediately to the dispatch below in the same turn.** Then dispatch:
   `mcp__github__actions_run_trigger` on repo `gt-factory-os`, workflow `deploy-production.yml`,
   ref `main`, inputs: `confirm=APPLY`, `migrations=db/migrations/029[5-7]_*.sql`
   (adjust glob if renumbered / 0298 exists → `029[5-8]`).
2. Poll the run (`mcp__github__actions_get` / job status) until success. If the `migrate` job
   fails: READ its logs; a failed CHECK-superset apply on live rows means a value list drifted —
   fix the migration (superset must include every live value), push to main via the branch+PR
   flow, re-dispatch. If logs unavailable (the 404 infra issue), run the same post-check SQL
   directly on PROD via `mcp__Supabase__execute_sql` (read-only asserts from Phase 1 Step 4,
   items 1–6) to determine whether migrations applied; act accordingly.
3. Verify: `curl -s https://gt-factory-os-api-production.up.railway.app/health` → `{"ok":true}`.
   Prod SQL asserts (read-only, Supabase MCP on PROD project): the 6 asserts from Phase 1
   Step 4 + `select count(*) from private_core.production_run` (expect 0 or few).
4. Portal is already deploying via Vercel (Phase 2 merge). Verify prod URL loads: WebFetch the
   portal production domain `/login` (find domain via `mcp__Vercel__list_projects` /
   `get_project` if unknown) → 200.
   **Gate 3:** health ok + all prod asserts true + portal live. FAIL → fix forward (never
   rollback ledger-bearing migrations); if API down >15 min, redeploy previous Railway build
   via `railway` and STOP + report.

## Phase 4 — Polish iteration 1 (the flow + design made perfect)

1. In the PORTAL repo, invoke skill `/ux-release-gate` scoped to the `/production` surfaces
   (list + picking + report + cutover touchpoints). Additionally spawn the two design skills'
   guidance: read `.claude/skills/frontend-design/SKILL.md` + `.claude/skills/ui-ux-pro-max/SKILL.md`
   and run their checklists against rendered screenshots: light+dark × 390px+1440px ×
   (/production, a TANK run pick screen, a PACK run, the report screen, empty state) using the
   dev server + dev-shim auth + Playwright screenshots.
2. Collect findings → author tranche `144-ux-gate-iteration-1.md` (same mechanics: manifest,
   registry, `_active.txt`) covering ONLY files with P0/P1 + cheap P2 fixes. FIX them.
   Rules: never weaken the resolve-gate; never add mandatory fields; simple-English only;
   no token/global edits.
3. Gates (tsc/eslint/vitest/@mocked) green → commit → push → wait `ci` green → merge → Vercel
   auto-deploys. **Gate 4:** merged green; the gate's P0 list is EMPTY (fix-verified).

## Phase 5 — Polish iteration 2 (verification of perfection)

Repeat Phase 4 as tranche `145-ux-gate-iteration-2.md` against the NEWLY deployed build.
Expected: near-zero findings. Any P0 → fix + merge as before. **Gate 5:** a re-run of
/ux-release-gate reports ZERO P0 and ZERO P1 on the /production corridor. Save the final
verdict + screenshots into the tranche doc as exit evidence.

## Phase 6 — Real-data dry run + handoff (zero stock impact)

1. **Read-only prod rehearsal:** with an admin/planner session against PROD API (or via
   `mcp__Supabase__execute_sql` reads + `curl` to the Railway API with a valid token if
   available; otherwise verify through the portal UI on the Vercel prod URL as Tom's account):
   - `GET /api/v1/queries/production-runs/today?date=<next Sunday>` → runs materialize from the
     plan in correct order (tank → fills). This writes ONLY `production_run` rows (no ledger) —
     these are the REAL runs Denis will open Sunday. Verify each run's `target_qty`/`uom`
     against `production_plan` (`batch_size_l` for TANK).
   - Open one pick-list (`GET …/pick-list`) → lines present, `required_qty` sane vs BOM,
     `on_hand` populated, pins non-null. **DO NOT call pick-confirm on prod.**
2. **Coverage checks (prod, read-only SQL):** every item on Sunday's plan has an ACTIVE
   pinned BOM (else fix data with Tom); floor-name coverage % for the components appearing in
   Sunday's pick-lists (report the % in the handoff).
3. **Sunday-morning safety net:** create a one-shot reminder (send_later, Sunday 06:30 IL) —
   "check /production loads + today's runs materialized; report to Tom" — so a human-visible
   check happens before Denis starts.
4. **Handoff message to Tom (Hebrew, in chat):** Denis's login (email + the generated
   password — Tom types it on Denis's phone at `<portal prod URL>/login`, password mode);
   bookmark `/production` to the home screen; what Denis sees step-by-step (Today list → tap
   run → collect → Done collecting → later Finish run); the floor-name draft table for
   one-pass approval (if not yet approved); the 30-day old-screen window; who to call if a
   material is missing (the flow flags automatically — he just keeps working).
5. Update `gt-factory-os-production-brain` docs: `CURRENT_STATE.md` is ops-docs-curator-lane —
   do NOT edit; instead append a completion note to
   `docs/plans/2026-07-24-production-picking-rollout.md` (STATUS: SHIPPED + evidence) on the
   branch, push, open/merge the brain PR for it.
   **Gate 6:** rehearsal verified + reminder armed + handoff posted. DONE.

## Verification summary (the definition of "perfect")

- Prod DB: migrations applied, all 6 asserts true, `rebuild_verifier` parity clean.
- API `/health` ok; portal prod serving `/production`; operator cockpit lands there.
- Denis's account works (password login → operator role → sees Today).
- Sunday's runs materialize correctly with sane quantities; one pick-list opens clean.
- Old screen: out of nav, direct-URL alive, guard blocks double-consumption (409
  `PICKING_RUN_EXISTS` — verified by unit/e2e, not on prod).
- /ux-release-gate iteration 2: ZERO P0/P1 on the corridor.
- tsc/eslint/vitest/@mocked green on `main` of the portal; backend typecheck clean locally +
  merged.
- Handoff message posted; Sunday 06:30 safety-net reminder armed.

## Failure escalation

Any gate unfixable within its phase → STOP; post to Tom (Hebrew): phase, exact command, exact
error, what was tried, options. Never skip a gate; never touch stock truth to "make it work";
never disable a portal hook or CI check to pass.

---

# MASTER PROMPT (paste into the NEW Sonnet 5 session, verbatim)

```
אתה מבצע rollout מלא לפרודקשן של פיצ'ר "מעגל פקודת הייצור" (production order picking) עבור GT Factory OS. עבודה אוטונומית מקצה לקצה. אני (Tom) כבר אישרתי בכתב: מיזוגים אוטונומיים, ההחלטות הנעולות, חשבון דניס (production@gteveryday.com + סיסמה), ו-cutover מיידי. אל תשאל אותי שאלות שכבר הוכרעו בתוכנית.

הצעד הראשון שלך, לפני הכל:
1. git fetch + checkout branch claude/production-materials-collection-page-mbqh7k בשלושת הריפוזיטוריז (gt-factory-os, gt-factory-os-portal, gt-factory-os-production-brain).
2. קרא במלואו את קובץ התוכנית: gt-factory-os-production-brain/docs/plans/2026-07-24-production-picking-rollout.md — הוא המקור המחייב היחיד שלך. הוא נכתב על-ידי הסשן שבנה את הפיצ'ר, עם עובדות תשתית מאומתות, פקודות מדויקות, שערי אימות לכל פאזה, וענפי כשל. בצע אותו פאזה-אחר-פאזה, לפי הסדר, בלי לדלג על אף שער (Gate).

חוקים מוחלטים (חוזרים גם בתוכנית):
- stock_ledger הוא append-only. לעולם אל תעדכן/תמחק שורות ledger.
- migration לפרודקשן ו-deploy הם כבר מדיניות קבועה אוטונומית (CLAUDE.md עודכן ב-24.7.2026): הודעה בצ'אט מיד לפני הדיפלוי, ואז ממשיכים מיד בלי לחכות לתשובה. זו לא חריגה חד-פעמית — זו המדיניות הרגילה מעכשיו.
- אסור לערוך: tailwind.config.ts, globals.css, baseline.json, quarantine.json, מסמכי UX-standard, CLAUDE.md, LOCKED_DECISIONS.md.
- עבודה רק על ה-branch הנ"ל. git add לנתיבים מפורשים בלבד (לעולם לא -A או .).
- בפורטל יש hooks חיים: כל כתיבה ל-src/** חייבת להיות במניפסט של ה-tranche הפעיל (קודם כותבים את מסמך ה-tranche + registry + _active.txt), וכל הודעת סיום חייבת שורת "Next action: ...".
- שער שנכשל ולא ניתן לתיקון בתוך הפאזה → עצור ודווח לי בעברית: פאזה, פקודה מדויקת, שגיאה מדויקת, מה ניסית. לעולם אל תדלג קדימה.
- כל טקסט למשתמש: אנגלית פשוטה לקורא חלש, דרך קובץ המילון _lib/copy.ts בלבד.

מפת הפאזות (הפירוט המלא בקובץ התוכנית):
Phase 0 בדיקות שפיות → Phase 1 השלמת backend (מיגרציות 0296/0297, שם-רצפה, seed של דניס, שומר כפל-צריכה) + ולידציה על Supabase branch + מיזוג PR → Phase 2 פורטל tranche 143 (cutover של המסך הישן, 7 נקודות מגע מדויקות בתוכנית) + מיזוג → Phase 3 deploy מוצהר (workflow_dispatch של deploy-production.yml עם confirm=APPLY) + אימותי פרודקשן → Phase 4 איטרציית ליטוש 1: /ux-release-gate + צ'קליסטים של frontend-design + ui-ux-pro-max על screenshots אמיתיים (2 ערכות נושא × 2 רוחבים), תיקון כל P0/P1 כ-tranche 144 → Phase 5 איטרציית ליטוש 2 (tranche 145) עד אפס P0/P1 → Phase 6 חזרה גנרלית על דאטה אמיתי בפרודקשן (קריאה בלבד! לעולם לא pick-confirm על פרוד), תזכורת ראשון 06:30, והודעת מסירה אליי בעברית עם הסיסמה של דניס וצעדי ההגדרה בטלפון שלו.

המטרה הסופית: ביום העבודה הבא דניס נכנס ל-/production בטלפון, רואה את הריצות של היום, מלקט, מאשר, מדווח — בלי תקלה אחת. לך.
```
