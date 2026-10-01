# MASTERPROMPT — a measured yes/no, per operational report, on whether Tom can report it from a Claude Code cloud session

**STATUS: LIVE — not yet executed**
<!-- The executing session's last act is to change this to SHIPPED / SUPERSEDED by <path> /
ABANDONED — why, with evidence pointers. See D10 and §4 W8. -->

> **Usage:** paste this entire file as the first message of a fresh Claude Code **cloud**
> session, started in the environment Tom reports from, with `gt-factory-os-production-brain`
> and `gt-factory-os` attached and the Supabase connector enabled. Optional: attach one
> supplier-invoice photo or PDF to the same message. It tests whether an invoice reaches the
> session. Nothing gets posted.
> This session **checks; it does not fix**. It stops for Tom only where §6 and §8 say so.
>
> **The fact that reorganizes the question:** every production report ever posted through the
> path the `report-production` skill uses (`form_type = production_run_report`, 57 rows,
> events 2026-07-25 → 2026-09-02) was posted by an **admin** account. The reporting bot
> (`bot@gteveryday.com`, role `operator`) has posted **zero** of them. Its only two
> submissions went through the legacy `production-actuals` endpoint, which the script never
> calls. Three steps of the skill's chain are planner/admin-only. So "the skill works" has so far
> only ever been true under an admin identity. The skill being listed in the session is not the
> question. The question is what the bot identity and this session's DB access can actually do.
>
> **Provenance:** written 2026-09-23 from a live check in a cloud session, 13:50–14:35 UTC.
> Measured at source: API `/health`, bot sign-in, `GET /api/v1/queries/me`, Supabase privileges,
> Postgres reachability, `form_submissions` history, and handler code at `gt-factory-os` commit
> `d88e42f` (2026-09-17). That session did not finish. Its mutation-gate probes were denied by the
> auto-mode classifier because no user authorization existed, and one history query was cancelled.
> This file carries that authorization (§4 W4, W5) and the unfinished checks. A read-only review
> pass on 2026-09-23 re-checked the §2.2 citations, the probe bodies and the §2.5 queries against
> code and DB.
> Authority, highest first: deployed API behaviour · code at your checkout HEAD, which stands in
> for the deployed commit because the API does not expose its version (`/health` returns only
> `{"ok":true}`) ·
> `gt-factory-os-production-brain/CLAUDE.md` · `gt-factory-os/CLAUDE.md` · the two skill files ·
> this document. They are cited below, never copied. Where this document disagrees with any of
> them, this document is wrong. Say so in the report.
>
> **Shelf life:** §2 is presumed wrong after **2026-09-30**. §4 re-measures every §2 fact anyway.
> When reality differs from §2, **adapt**: the new measurement is the answer. Add one line per
> divergence to the report.

## 0. How to work

- **Who you are here:** one fresh Claude Code session. You hold both repos, the Supabase MCP
  tools (project `rvadsozabmxkkrktwgnv`), the GitHub MCP tools, and the environment variables
  `GT_API_EMAIL` / `GT_API_PASSWORD` (the bot's sign-in; `report-production/SKILL.md` §Step 1).
  You may read anything, sign in as the bot (`POST /auth/v1/token`), call `GET` endpoints, and
  make exactly the three probe calls P1–P3 in §4. You may not post a report, change a role or setting, or edit any skill or code.
  You measure and you report.
- **Read first, in order:** this file · `.claude/skills/report-production/SKILL.md` ·
  `.claude/skills/report-production/scripts/report_production.mjs` lines 1–40 ·
  `.claude/skills/goods-receipt-from-invoice/SKILL.md` §Posting pattern ·
  `gt-factory-os/api/src/auth/session.ts` lines 32–34.
- **First action:** run W0 (§4). Record `T0` before any other call.
- **Halt conditions, evidence standard, git discipline:** inherited from
  `gt-factory-os-production-brain/CLAUDE.md` §Stop conditions, §Evidence, §Watching. The
  deltas for this work are in §8.
- **The standard, in Tom's words:** `המשימה שלך היא לוודא שאני יכול לדווח מפה ייצור מלא, קבלת סחורה וכו'`
  ("make sure I can report full production, goods receipt, etc. from here"). As checkable
  prohibitions:
  1. No verdict without an observation made in this session: a status line, a query row, or a
     cited `file:line`. Every row states which kind.
  2. Nothing gets written to the ledger, plans, runs, receipts or submissions while you check.
     D8 proves it.
  3. ✅ means Claude can take the report from Tom's message to the end state the portal form
     reaches, from this session today, with no pasted token and no step left for the portal. An
     approval by a second person that the API always requires does not count against ✅, but say
     that it exists. Anything less is ❌, and the missing step is named.
- **Language:** this document is in English because that is the register the executor reasons
  best in. Data literals stay in their own script, in backticks, never translated.
  **Output language: Hebrew, concise and direct.** Short lines, no preamble, no restating the
  question, no recap. End every reply with at most one action for Tom, or the line
  `לא נדרש ממך כלום`.

## 1. Mission and definition of done

**One testable sentence:** for each of six operational reports (production as the full chain,
goods receipt, waste adjustment, physical count, inventory movement, stock transfer), establish
from this session whether Tom can report it end to end today. If not, name the exact missing
permission or path and who can supply it.

| # | Condition | The observation that would prove it false |
|---|---|---|
| D1 | Environment fingerprint recorded: `CLAUDE_CODE_REMOTE`, which W1 variable names exist, whether `report-production` and `goods-receipt-from-invoice` are in your skill list | the list is missing, or any variable's value is printed |
| D2 | Bot identity observed live | role taken from SQL or memory instead of `GET /api/v1/queries/me` |
| D3 | DB write capability measured with §2.5 C, `psql` reachability tested with `timeout 20`, and every other write-capable tool in the session (`apply_migration`, `deploy_edge_function`) named as not a reporting path and left unused | write access inferred from the tool's existence, tested with a real `INSERT`, or any of those tools called |
| D4 | Every production step in the W4 table has a verdict and an evidence kind. P1 and P2 are observed live, or marked `code-only: probe denied` with the denial reason quoted | a step with no verdict, or a "live" verdict with no captured status line |
| D5 | `report_production.mjs` dry run executed here on a date with zero plan rows, with status line and exit code captured | not run, or run on a date that had plan rows |
| D6 | Goods receipt: a verdict for the skill's SQL path, for the API path (P3), and for invoice attachment | any of the three missing |
| D7 | Waste, count, movement and transfer each get a verdict from gates re-grepped at your HEAD, the submit behaviour (posts / pending / auto-post), and which skill (if any) calls the endpoint | a verdict with no `file:line` read at HEAD, or one copied from §2.2 |
| D8 | Zero business writes: §2.5 B returns 0 in every column. The bot sign-in writes a Supabase Auth session row; that write is expected and exempt | any column above 0 |
| D9 | Final report per §9, in Hebrew | an unmet D-row goes unmentioned, or there is more than one action for Tom |
| D10 | STATUS line handled per W8 | the file is in your checkout and still says `LIVE` |

Anything not on this list is out of scope unless Tom asks.

### 1.1 Settled — do not reopen

- Production posts only through the live API, never SQL (`report-production/SKILL.md` §The one
  rule about how to write).
- `stock_ledger` is append-only. Corrections are reversal rows (`gt-factory-os/CLAUDE.md` §Stock truth).
- The reporting identity is `bot@gteveryday.com` (`report-production/SKILL.md` §Step 1).
- "Operational report" means the six stock-moving forms in §1. This was decided 2026-09-23 from Tom's
  `וכו'`. Dispatch, route packs, batch-sheet printing, planning and procurement are not reports.
- No PR watching, no check-ins, no Routines (`gt-factory-os-production-brain/CLAUDE.md` §Watching).

## 2. Ground truth — measured 2026-09-23 in a cloud session; re-verify at boot

### 2.1 What is built and live

- Skills: brain `.claude/skills/report-production/` (SKILL.md + `scripts/report_production.mjs`)
  and `.claude/skills/goods-receipt-from-invoice/` (SKILL.md only). The backend `.claude/skills/` holds
  `production-order`, `customer-setup-shopify-gi` and `shopify-draft-order-from-po`. None of them reports stock.
  **No dedicated reporting skill exists** for waste, physical count or stock transfer. `route-print-pack`
  submits pending inventory-movement approvals, but only for movements found while building a delivery
  route pack (`route-print-pack/SKILL.md` step 4). There is no general inventory-movement skill.
- `GET https://gt-factory-os-api-production.up.railway.app/health` returned HTTP 200 `{"ok":true}`.
- Bot sign-in (the Supabase password grant in the script's `resolveToken()`) returned 200 and issued a token.
- `GET /api/v1/queries/me` returned `"email":"bot@gteveryday.com"`, `"role":"operator"`,
  `"user_id":"d6e1f08e-13c8-4205-8d80-6a7b31f25857"`.
- `mcp__Supabase__execute_sql` runs with `current_user = supabase_read_only_user` and
  `transaction_read_only = on`. `INSERT` is false on `stock_ledger`, `form_submissions`,
  `goods_receipts`, `goods_receipt_lines`, `component_procurement_specs` and `price_history`.
  `UPDATE` is false on `components`.
- `psql "$DATABASE_URL_POOLED"` (host `aws-1-eu-central-1.pooler.supabase.com`, port `5432`)
  hung until it was killed. A `CONNECT` to the same host and port through the session proxy
  returned `curl: (28) Time-out`. The proxy status listed no relay failure.

### 2.2 Role gates in code — commit `d88e42f`

"operator+" means operator, planner or admin.

| Step | Endpoint | Roles allowed | Where |
|---|---|---|---|
| Plan create / patch / delete | `POST`/`PATCH`/`DELETE /api/v1/mutations/production-plan[/:id]` | planner, admin | `api/src/production-plan/handler.ts:58-59`, used at `:94`, `:545`, `:805` |
| Close a base batch | `POST /api/v1/mutations/production-plan/:plan_id/close-batch` | planner, admin | `api/src/production-plan/handler.close_batch.ts:63`, `:78` |
| Runs today, pick list, preview, report | `/api/v1/…/production-runs/…` | operator+ | `api/src/production-runs/handler.ts:52` |
| Unplanned run (not used by the skill) | `POST /api/v1/mutations/production-runs` | operator+ | `api/src/production-runs/handler.ts:724` |
| Legacy production submit (not used by the skill) | `POST /api/v1/mutations/production-actuals` | operator+ | `api/src/production-actuals/handler.ts:84-92` |
| Goods receipt | `POST /api/v1/mutations/goods-receipts` | operator+; `final_delivery` planner, admin | `api/src/auth/session.ts:32-34`; `api/src/goods-receipts/handler.ts:57-65` |
| Waste | submit (a loss at or under `waste_auto_post_threshold` auto-posts with 201; anything else goes pending with 202) / approve | operator+ / planner, admin | `api/src/waste-adjustments/handler.ts:9-11`, `:78`, `:82`, `:260` |
| Physical count | open, submit / approve | operator+ / planner, admin | `api/src/physical-counts/handler.ts:88`, `:91`, `:94` |
| Inventory movement | submit / approve | operator+ / planner, admin | `api/src/inventory-movements/handler.ts:64`, `:67` |
| Stock transfer | submit posts at once (201 `posted`, no approval step) | operator+ | `api/src/stock-transfers/handler.ts:54`, `:286-291` |
| PO placement (context for any role change) | `POST /api/v1/mutations/purchase-orders/:po_id/place` | planner, admin | `api/src/purchase-orders/place_order_handler.ts:31-32` |
| Change a user's role | `PATCH /api/v1/mutations/admin/users/:user_id` | admin | `api/src/users/route.ts:64`, `api/src/users/update_handler.ts:66` |

These are the gates at `d88e42f`. Re-grep them at your HEAD (W4, W6) rather than copying this table.
The order was verified for plan PATCH, close-batch and goods receipt: body validation (422), then
role gate (403), then lookups, then writes. A plan PATCH or close-batch on an unknown `plan_id` returns
404 `PLAN_NOT_FOUND` before any write (`api/src/production-plan/handler.ts:577-581`;
`api/src/production-plan/handler.close_batch.ts:115-119`). The goods-receipt supplier lookup (`handler.ts:88`)
runs before the first `insertInto` (`handler.ts:258`).

### 2.3 History (read-only SQL, 2026-09-23)

- `production_run_report` (the skill's report path): 57 rows, **all by an admin-role account**,
  events 2026-07-25 → 2026-09-02. Bot: 0.
- `production_actual_submit` (legacy path): the bot has 2 rows (events 2026-09-06, 2026-09-07). The rest
  are admin (80, to 2026-07-23) and one other operator account (5, 2026-06-15 → 2026-07-22).
- `goods_receipt`: admin 89 (2026-05-12 → 2026-09-17), another operator 6 (to 2026-08-06), bot 0.
  The goods-receipt skill writes `submitted_by` = Tom's account, so SQL-posted and portal-posted
  receipts cannot be told apart here.
- Plans carrying the script's create key (`idempotency_key like 'PRODPLAN:%'`): 5, latest
  `created_at` 2026-08-31 08:14Z. The bot's `app_users.created_at` is 2026-09-01 07:36Z. A read-only
  check on 2026-09-23 confirmed all 5 were created by an admin account, not the bot. That is
  consistent with the script's `GT_API_TOKEN` path used with a pasted admin token. W0 re-runs §2.5 A.
- `production_plan` rows dated 2026-09-18 → 2026-09-30: 0. The latest plan date is 2026-09-17. Any batch
  made on or after 2026-09-18 therefore needs a plan **create** (planner/admin) before it can be reported.

### 2.4 What is NOT built, and what is adjacent

- The goods-receipt skill posts by direct SQL (§Posting pattern: one CTE into `form_submissions`,
  `goods_receipts`, `goods_receipt_lines` and `stock_ledger`, plus price and spec-store writes). The
  production skill forbids SQL posting. The two skills contradict each other on write path.
  Report it. Do not resolve it.
- The API takes `actual_unit_price_net` per receipt line and returns `cost_drafts_created`
  (`api/src/goods-receipts/schemas.ts`). That is an API-native price path the skill does not use.
  `component_procurement_specs` appears in the API only under `api/src/purchase-session/` (`schemas.ts`,
  `queries.ts`). *Inferred:* no API writer exists for the spec store.
- Production has gone unreported since 2026-09-07 (legacy) and 2026-09-02 (run path). This is out of
  scope. Give it one line in the report.

### 2.5 Re-verification block

Substitute the `<…>` placeholders. The Supabase tool takes no psql variables.

```sql
-- A. who created the script-keyed plans (confirms or kills the 2.3 inference) — 2026-09-23
select plan_date, created_at, created_by_snapshot, created_by_user_id, status
  from private_core.production_plan
 where idempotency_key like 'PRODPLAN:%'
 order by created_at;

-- B. zero-write proof — run at the end; <T0> from W0, <BOT> = user_id from /queries/me, <D> = dry-run date
select
  (select count(*) from private_core.form_submissions
    where submitted_by = '<BOT>' and submitted_at >= '<T0>')                        as bot_submissions,
  (select count(*) from private_core.production_plan
    where created_by_user_id = '<BOT>' and created_at >= '<T0>')                    as bot_plans,
  (select count(*) from private_core.production_plan
    where notes like 'readiness-probe%')                                            as probe_plans,
  (select count(*) from private_core.production_run r
     join private_core.production_plan p using (plan_id) where p.plan_date = '<D>') as runs_on_dry_run_date;

-- C. DB write capability for the goods-receipt skill's SQL path — 2026-09-23 baseline in 2.1
select current_user, current_setting('transaction_read_only') as tx_read_only,
       has_table_privilege('private_core.stock_ledger','INSERT')                as ledger_insert,
       has_table_privilege('private_core.form_submissions','INSERT')            as fs_insert,
       has_table_privilege('private_core.goods_receipts','INSERT')              as gr_insert,
       has_table_privilege('private_core.goods_receipt_lines','INSERT')         as grl_insert,
       has_table_privilege('private_core.price_history','INSERT')               as price_insert,
       has_table_privilege('private_core.component_procurement_specs','INSERT') as spec_insert,
       has_table_privilege('private_core.components','UPDATE')                  as comp_update;

-- D. who has used each reporting path — 2026-09-23 baseline in 2.3
select fs.form_type, au.role, (au.email = 'bot@gteveryday.com') as is_bot, count(*) as n,
       min(fs.event_at)::date as first_event, max(fs.event_at)::date as last_event
  from private_core.form_submissions fs
  left join private_core.app_users au on au.user_id = fs.submitted_by
 where fs.form_type in ('production_run_report','production_actual_submit','goods_receipt')
 group by 1,2,3 order by 1,2;
```

The API caller: one Node process that signs in exactly like the script, calls, and never prints
or stores the token. Run it from the brain repo root. Arguments are `METHOD PATH [JSON_BODY]`.
It was tested 2026-09-23 with `GET` calls only.

```bash
NODE_USE_ENV_PROXY=1 node --no-warnings --input-type=module -e '
import { readFileSync } from "node:fs";
const S = readFileSync(".claude/skills/report-production/scripts/report_production.mjs", "utf8");
const ANON = S.match(/GT_API_ANON_KEY\s*\?\?\s*\x27([^\x27]+)\x27/)[1];   // public anon key, read from the script
const BASE = process.env.GT_API_BASE ?? "https://gt-factory-os-api-production.up.railway.app";
const auth = await fetch("https://rvadsozabmxkkrktwgnv.supabase.co/auth/v1/token?grant_type=password", {
  method: "POST", headers: { apikey: ANON, "Content-Type": "application/json" },
  body: JSON.stringify({ email: process.env.GT_API_EMAIL, password: process.env.GT_API_PASSWORD }) });
console.log("sign-in", auth.status);
const H = { Authorization: "Bearer " + (await auth.json()).access_token, "Content-Type": "application/json" };
const [M, P, B] = process.argv.slice(1);
const r = await fetch(BASE + P, { method: M, headers: H, ...(B ? { body: B } : {}) });
console.log(M, P, r.status, (await r.text()).slice(0, 300));
' GET /api/v1/queries/me
```

## 3. What the hard part actually is

1. **"Is the skill listed?" is the wrong test.** Both skills load. Readiness depends on the identity
   the skill signs in as and on the write path it uses once it runs.
2. **A dry run cannot prove the production chain.** Dry runs refuse to create plans
   (`report_production.mjs`, `ensurePlans`). So the step most likely to fail, plan create, is exactly
   the step a dry run skips. That step is planner-only and is needed for every batch dated on or after
   2026-09-18. Only P1 shows it.
3. **Bot history proves nothing about the skill's path.** The bot's two reports used the legacy
   endpoint. Every `production_run_report` was made under admin.
4. **The Supabase connector looks writable and is not.** Its tool description warns that destructive
   statements may need confirmation, yet the session user is read-only. Measure the privileges.
5. **A classifier denial is an unmeasured row, not a ❌ for Tom.** Fall back to code evidence and
   label it as code evidence.

## 4. Workstreams

### W0 — Boot
`select now()` via Supabase gives `T0`. Run §2.5 A and §2.5 D.
**Acceptance:** feeds D8, and the §2.3 inference is confirmed or ruled out.

### W1 — Environment fingerprint
`echo "$CLAUDE_CODE_REMOTE"`, then
`env | cut -d= -f1 | grep -E '^(GT_API_EMAIL|GT_API_PASSWORD|GT_API_TOKEN|DATABASE_URL_POOLED|SUPABASE_URL|SUPABASE_SERVICE_ROLE_KEY|HTTPS_PROXY)$'`.
Print names only. Note whether `report-production` and `goods-receipt-from-invoice` appear in your skill
list, and whether `GT_API_TOKEN` is set (if it is, the script uses that token instead of the bot).
**Acceptance:** D1.

### W2 — Identity and reachability
With the §2.5 API caller: `GET /health`, `GET /api/v1/queries/me`, `GET /api/v1/queries/goods-receipts?limit=1`.
Then pick `<D>`, the dry-run date: the most recent past date for which
`GET /api/v1/queries/production-plan?from=<D>&to=<D>&include_completed=true` returns `"count":0`
(`2026-09-22` qualified at 2026-09-23T14:32Z).
**Acceptance:** D2.

### W3 — DB write capability
Run §2.5 C. Then `timeout 20 psql "$DATABASE_URL_POOLED" -Atc 'select 1'; echo "exit=$?"`.
Exit 124 means no Postgres egress. Never print the URL. The Supabase MCP also exposes
`apply_migration` and `deploy_edge_function`. Neither is a reporting path: record that they exist,
and never call them.
**Acceptance:** D3.

### W4 — Production chain
By pasting this document, Tom authorizes P1 and P2 below, once each, exactly as written. Both
target a `plan_id` you prove absent first, and both return before any write (§2.2). First re-grep
`roleAllowsPlanWrite` and `CLOSE_ALLOWED_ROLES` at your HEAD, and confirm that the lookup still
returns 404 before the first write.

| # | Step | Needed when | Verdict from |
|---|---|---|---|
| 1 | Read the day's plans | always | W2, live |
| 2 | Create a plan row | no open plan for that date and item. True for every batch dated 2026-09-18 or later | P1, live |
| 3 | Patch a base batch's split | a reported SKU is missing from the split | P1, live |
| 4 | Materialize runs + consumption preview | always | `production-runs/handler.ts:52` (code) |
| 5 | Report the run | always | same (code). No bot history exists on this path |
| 6 | Close the base batch | a base-batch plan is fully reported | P2, live |
| 7 | Verify the ledger (reads) | always | reads work (W3). `rebuild_verifier()` truncates and refills `current_balances_shadow`, so it runs only in a writable session. The skill makes it conditional (`report-production/SKILL.md` §Step 5). Record whether it can run here; it does **not** gate ✅ |

**P1:** `U = crypto.randomUUID()`. Confirm
`select count(*) from private_core.production_plan where plan_id = '<U>'` returns 0. Then
`PATCH /api/v1/mutations/production-plan/<U>` with `{"notes":"readiness-probe 2026-09-23"}`.
A 403 with `Role not permitted for production-plan patch` means the bot cannot create, patch or delete plans
(one gate, `roleAllowsPlanWrite`). A 404 `PLAN_NOT_FOUND` means it can. A 503 `break_glass` also
means it can, because that check runs after the role gate; say that break-glass is on. A 401 means
sign-in failed: fix it and retry once. A 422 means the body is wrong: fix it from
`PatchProductionPlanRequestSchema` (`api/src/production-plan/schemas.ts:139`) and do not guess.
A 2xx means §8.

**P2:** `POST /api/v1/mutations/production-plan/<U>/close-batch` with
`{"closure_note":"readiness-probe 2026-09-23"}`. A 403 means the bot cannot close batches. A 404 or
503 `break_glass` means it can. A 401 means fix sign-in and retry once. A 2xx means §8.

**Dry run (D5):** use the `<D>` picked in W2. Confirm `FG-NAM-1L` is still `ACTIVE` with
`sales_uom = BOTTLE`, `base_bom_head_id = BOM-BASE-NAM-REG` and `base_fill_qty_per_unit = 1`
(all observed 2026-09-23). Then, from the brain repo root:

```bash
echo '{"date":"<D>","dry_run":true,"lines":[{"item_id":"FG-NAM-1L","qty":1,"uom":"BOTTLE","base_bom_head_id":"BOM-BASE-NAM-REG","fill_l_per_unit":1}]}' \
  | NODE_USE_ENV_PROXY=1 node --no-warnings .claude/skills/report-production/scripts/report_production.mjs -; echo "exit=$?"
```

Expected output: `DRY RUN — <D>`, `⚠ NOT CHECKED: FG-NAM-1L`, `"status": "dry_run_incomplete"`,
`plan_would_be_created`, and `exit=0`. This proves the script runs here (Node, proxy, sign-in, reads).
It proves nothing about steps 2–6.
**Acceptance:** D4, D5. Production is ✅ only if steps 1–7 are all ✅.

### W5 — Goods receipt
By pasting this document, Tom authorizes P3, once, exactly as written.

- **(a) The skill's path.** From D3: the skill's §Posting pattern needs `INSERT` on the four receipt and
  ledger tables, plus the price and spec writes. If any flag is false, this path is ❌ from this session.
- **(b) The API path, P3.** Confirm
  `select count(*) from private_core.suppliers where supplier_id = 'READINESS-PROBE-NONEXISTENT'`
  returns 0. Re-read `api/src/goods-receipts/handler.ts` lines 57–95 at your commit to confirm the
  supplier lookup still precedes the first insert. Then
  `POST /api/v1/mutations/goods-receipts` with
  `{"idempotency_key":"readiness-probe-<U>","event_at":"<now, ISO 8601 with Z>","supplier_id":"READINESS-PROBE-NONEXISTENT","lines":[{"item_type":"RM","item_id":"READINESS-PROBE-NONEXISTENT","quantity":1,"unit":"KG"}]}`.
  A 409 with `"reason_code":"SUPPLIER_INACTIVE"` means the bot passes the role gate and the route is live.
  A 403 means the role is blocked. A 401 means fix sign-in and retry once. A 422 means the body is
  wrong: fix it from `schemas.ts`. A 2xx means §8.
- **(c) Attachment.** If Tom's message carries an image or PDF, read it and extract the supplier name and
  document number only. Post nothing. With no attachment, mark the row `not tested — no attachment`.

The goods-receipt verdict is ✅ only if (a) is ✅: that is the path the skill actually uses. (b) is the
evidence for the fix, not a substitute for (a).
**Acceptance:** D6.

### W6 — Waste, physical count, inventory movement, stock transfer
1. At your HEAD, re-grep each form's role helpers in `gt-factory-os/api/src/<form>/handler.ts`, and read
   what a successful submit does: posts, goes pending, or auto-posts under a threshold.
2. Grep both repos' `.claude/skills/` for `mutations/waste-adjustments`, `mutations/physical-counts`,
   `mutations/inventory-movements` and `mutations/stock-transfers`. On 2026-09-23 only `route-print-pack`
   matched (inventory movements, route-pack context only).
3. For each report record: the skill that calls it and for what (or none), the submit behaviour, and who
   approves. The verdict is ✅ only if a skill lets Tom report that event from this session by the §0 ✅
   rule. A route-pack-only path does not make a general inventory-movement report ✅.

These get no live probes, because none is authorized.
**Acceptance:** D7.

### W7 — Zero-write proof
Run §2.5 B with `T0`, the bot's `user_id` and `<D>`. Every column must be 0.
**Acceptance:** D8.

### W8 — Report and stamp
Report per §9. Then, if `docs/plans/2026-09-23-operational-reporting-readiness-masterprompt.md` is in
your checkout, change its STATUS line to `SHIPPED — <date>: <one-line verdict>`, commit on your designated
branch, push, open a draft PR, and immediately call `unsubscribe_pr_activity` for it
(`gt-factory-os-production-brain/CLAUDE.md` §Watching). If the file is absent because its PR is not merged,
skip the stamp and say so in one line.
**Acceptance:** D9, D10.

## 5. Scope

**IN:** everything in §4.

**OUT — do not touch, do not "improve":**
- Posting anything real, even when Tom's message carries a real batch or a real invoice. Say that it will
  be reported in a normal session after this check.
- Changing the bot's role, the Supabase connector, the environment's network access, or any env var.
- Editing `report-production` or `goods-receipt-from-invoice`, or writing a new skill. Findings only.
- Any write with `SUPABASE_SERVICE_ROLE_KEY` (PostgREST or otherwise), any call to `apply_migration`,
  `deploy_edge_function` or another Supabase write tool, or any other path around the API.
- The unreported production backlog, the portal, LionWheel, Green Invoice, Shopify.
- Any `GET /api/v1/queries/production-runs/today` for a date that has plan rows (§7.4).

## 6. Tom's part — the complete list, nothing else is his

**A.** Paste this file as the first message of a new cloud session in the environment you report from.
Optional: attach one invoice photo or PDF to that message. This takes about a minute. It is Tom's
because only he starts sessions.

Nothing else in this check is Tom's. The fixes it surfaces are decisions for after the report. A role
change, for example, can only be made by an admin (§2.2). The report names exactly one fix.

## 7. Landmines — do not rediscover these

1. **Token written to a file.** Auto-mode denies it with `[Credential Materialization]`. Sign in and call
   inside one Node process (the §2.5 caller), and print statuses and trimmed bodies only. List env vars
   with `env | cut -d= -f1`, never `env | sed`: a prefix of a secret is still a leak.
2. **Mutation-endpoint calls.** Auto-mode denies them with `[Modify Shared Resources]`, even when they
   cannot write. This document authorizes P1–P3 only. If a call is still denied, do not retry it, rephrase
   it or route around it. Mark the row `code-only (probe denied: <quoted reason>)`.
3. **`GET /api/v1/me` returns 404.** The route is `/api/v1/queries/me`.
4. **`GET /api/v1/queries/production-runs/today?date=` writes.** It materializes runs for plans on that
   date (the comment in `resolveRuns`, `report_production.mjs`). Never call it for a date with plan rows.
5. **`psql` hangs instead of failing.** Always use `timeout 20`. Exit 124 means no Postgres egress from
   this session. Do not retry with other ports or hosts.
6. **The Supabase tool implies writes, but the session is read-only.** Measure with §2.5 C. Never test with a
   real `INSERT`, not even inside a transaction you roll back.
7. **Guessed schema costs a round trip.** `private_core.production_actuals` does not exist.
   `production_plan` has no `is_base_batch` (the API derives it) and no `created_by`: the columns are
   `created_by_user_id` and `created_by_snapshot`. Check `information_schema.columns` before any new query.
8. **`[UNDICI-EHPA] Warning: EnvHttpProxyAgent is experimental`** is noise; `--no-warnings` silences it.
   Keep `NODE_USE_ENV_PROXY=1` (`report-production/SKILL.md` §Step 1).
9. **`⚠ NOT CHECKED` / `dry_run_incomplete` is the expected dry-run output** on a date without plans,
   not a failure.
10. **Empty plan reads for 2026-09-18 onward are real.** No plans exist. It is not an API fault.
11. **`SUPABASE_SERVICE_ROLE_KEY` is in the environment.** It bypasses the API's handlers (BOM explosion,
    PO line updates, cost drafts). It is not a reporting path: report that it is present, and never use it.
12. **Two form types mean two production paths.** `production_run_report` is the skill's path.
    `production_actual_submit` is legacy. Evidence for one says nothing about the other.
13. **`rebuild_verifier()` is a write.** It truncates and refills `current_balances_shadow`, so it fails on
    the read-only connector. That failure is expected and gates nothing. Record it and move on.
14. **A `ls` of `.claude/skills/` misses skills that post a form as a side job.** `route-print-pack`
    posts inventory movements. Grep for endpoint paths instead (W6).

## 8. Halt conditions (additions to the inherited set)

- P1, P2 or P3 returns 2xx → **STOP.** Report the response verbatim. Do not try to undo it; Tom decides.
- Any non-`GET` call other than P1–P3 and the bot sign-in
  (`POST https://rvadsozabmxkkrktwgnv.supabase.co/auth/v1/token`), or `report_production.mjs` with
  `dry_run:false` → **STOP.** Do not make the call.
- §2.5 B shows any column above 0 → **STOP** and report exactly which rows.
- The dry-run date has plan rows → pick another date. If no date in the last two weeks qualifies, skip D5
  and say why.

## 9. Final report — Hebrew, concise

If any D-row was not met, say so first.

1. **First line:** the direct answer. For each report, can Tom report it from here today: ✅ or ❌.
2. **Table:** report · ✅/❌ · missing step · evidence (live / code / history + pointer) · fix · who.
3. **Numbers:** bot role · DB user and `tx_read_only` · privilege flags · P1–P3 statuses · dry-run status
   and exit code · §2.5 A result · §2.5 B counts.
4. **Divergences from §2**, one line each.
5. **Out-of-scope findings**, one line each.
6. **Handoff block** (`gt-factory-os-production-brain/CLAUDE.md` §Handoff): a STATUS token from
   `VERDICT_GLOSSARY.md` and the 8 PASS fields, one short line each. STATUS describes this check, not
   Tom's readiness: PASS means every D-row was met, even when every answer in the table is ❌.
7. **One action for Tom, last:** the single fix that unblocks the most reports, who makes it, and where.
   If two fixes each unblock one report, pick the production fix: Tom named production first, and its fix
   keeps writes on the API (§1.1). The other fix stays in the table's fix column. If the action is a role
   change, add one line on what else that role can do (the PO placement row in §2.2). If no action is
   needed, write `לא נדרש ממך כלום`.
