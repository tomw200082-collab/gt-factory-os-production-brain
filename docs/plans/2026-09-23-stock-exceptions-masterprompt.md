# MASTERPROMPT — Every non-pick stock movement from delivery reaches the inbox pre-filled, and ends posted or rejected

**STATUS: LIVE — not yet executed**
The executing session's last act is to change this line to `SHIPPED <date> — <PR links>` / `SUPERSEDED by <path>` / `ABANDONED — why`, with evidence pointers.

> **Usage:** paste this entire file as the first message of a fresh Claude Code session with `tomw200082-collab/gt-factory-os-production-brain`, `tomw200082-collab/gt-factory-os` and `tomw200082-collab/gt-factory-os-portal` attached. It takes the inventory-movement flow from "empty proposals, most movements never detected" to "every completed non-pick LionWheel movement becomes a filled, evidenced, approvable inbox item", merged, deployed and verified. It halts for Tom only where §6 says so.
>
> **Provenance:** written 2026-09-23 from a live diagnosis session: Supabase project `rvadsozabmxkkrktwgnv` queried read-only via the Supabase MCP, `gt-factory-os` at commit `d88e42f`, `route_pack.py` on branch `claude/wizardly-pascal-vu4yrf` (PR #206 of the brain repo). Numbers in §2 are observed on that date unless marked otherwise.
> Authority, in order: `CLAUDE.md` (brain repo) → `EXECUTION_POLICY.md` → `CURRENT_STATE.md` → `gt-factory-os/CLAUDE.md`. Cited below, never copied.
>
> **Shelf life:** §2 is presumed wrong if pasted after 2026-10-07. Run §2.5 first either way. If reality no longer matches §2 (e.g. someone already added `proposed_lines`), **adapt**: rebuild on what exists, do not duplicate it; record the divergence in the final report.

## 0. How to work

- **Who you are here:** one autonomous Claude Code session, owner of the whole change across three repos. You may write code, migrations, tests, open PRs, merge on green, dispatch the production deploy, and submit inventory-movement *proposals* through the API. You may not approve inventory movements: approval is the human step that posts to `stock_ledger`, and it stays human.
- **Read first:** `CLAUDE.md` (all), `gt-factory-os/CLAUDE.md`, `.claude/skills/route-print-pack/SKILL.md` "How to run" step 4, `gt-factory-os/db/migrations/0259_inventory_movements.sql`, `gt-factory-os/api/src/inventory-movements/{schemas,handler,route}.ts`, `gt-factory-os/api/test/inventory_movements.test.ts`, `gt-factory-os/api/src/integrations/lionwheel/reconciliation.ts` (Phase 2, where `credit_tasks` are created), `.claude/skills/daily-ops-guardian/SKILL.md` (§C, §V), `REGISTRY.md` (skills list), `gt-factory-os/api/src/auth/session.ts`, `gt-factory-os/api/src/credit_tracking/handler.ts`, `gt-factory-os/db/migrations/0241_credit_tasks.sql`, `gt-factory-os/db/migrations/0023*` (mirror column semantics).
- **Authority:** where this document and an authority doc disagree, the authority doc wins and this document is wrong — say so in the report.
- **Halt conditions, evidence standard (the 6 layers), git discipline, deploy gates, handoff format:** inherited from `CLAUDE.md` §Stop conditions, §Evidence, §Authorization, §Handoff. Deltas for this work are in §8.
- **Watching:** `CLAUDE.md` §Watching forbids PR subscriptions and self check-ins. Verify CI by reading check runs directly in-turn (GitHub MCP `pull_request_read` / `get_check_run`), and wait with bounded in-turn polling. After every `create_pull_request`, call `unsubscribe_pr_activity` immediately.
- **The standard (Tom, 2026-09-23):** "end to end, no open ends at all, merged and green, so I don't have to verify it." Translated into checkable bans:
  - nothing may reach the inbox without at least one proposed line or an explicit open question explaining why a line could not be derived;
  - nothing may be reported done that was not observed live (§1 lists the observation for each row);
  - no PR may be left open, red, or unmerged at the end; no branch you created may be left with unmerged commits.
- **Required skills, in this order at the end:** `simplify` on each repo's diff, then `verification-before-completion` before any "done" claim. Use `test-driven-development` for backend changes.
- **Language:** this document is in English; data literals stay in Hebrew, in backticks, never translated. **Output language to Tom: concise Hebrew** (Tom writes Hebrew). Short sentences, no preamble, one action at most at the end, or `לא נדרש ממך כלום`.

## 1. Mission and definition of done

**One testable sentence:** every LionWheel task that completes with a physical stock movement outside the pick bridge produces, within one daily sweep, a pending inventory-movement approval whose lines, rationale and evidence are already filled, and the portal shows those lines pre-filled and editable before Approve.

| # | Condition | The observation that would prove it false |
|---|---|---|
| D1 | Submit contract accepts `proposed_lines[]`, `rationale`, `open_questions[]`, `evidence[]`, `credit_task_ids[]`; the detail query returns them | vitest round-trip fails; and in production the live sweep proposal of D9 read back through `GET /api/v1/queries/inventory-movements/:id` omits them. No separate production probe. |
| D2 | Proposed lines are validated at submit (item exists and is active, unit exists, `item_type` matches) — without the count-freeze check or advisory lock | vitest: unknown `item_id` in `proposed_lines` gets 202, or a valid proposal gets `COUNT_FREEZE_ACTIVE` during an active freeze |
| D3 | Approving a supplement moves linked `credit_tasks` to `SUPPLIED` only when status is `PENDING`/`DEFERRED`, same `item_id`, approved qty ≥ `qty_missing`; emits `emitChangeLog` like `credit_tracking/handler.ts` | vitest: a full match stays `PENDING`; or a partial supplement moves to `SUPPLIED`; or a `CREDITED` task changes; or no change-log row is emitted |
| D4 | The real cause of the `GI-20269` duplicates (8 lines vs 4 ledger rows) is found, reproduced in a test that fails on current code, and fixed; migration adds `unique (stock_ledger_movement_id)` after de-duplicating exact copies | the new test passes on unfixed `handler.ts`; or `select stock_ledger_movement_id, count(*) from private_core.inventory_movement_lines group by 1 having count(*)>1` returns rows after deploy |
| D5 | The daily sweep covers all drivers and only `COMPLETED` tasks; cheques and canceled tasks produce nothing; no stock task is misclassified as cheque | backtest dry-run (`lw_completed_at` 2026-06-15..2026-09-22) proposes for a cheque or `CANCELED` task; or its printed cheque list contains a stock task |
| D6 | On the §2.2 backtest set, the sweep classifies every no-line task and derives lines for every supplement that names a Green Invoice document number | dry-run output: any of the 32 supplement-class tasks with a 5-digit doc number in its title has zero proposed lines and no open question |
| D7 | Route-print-pack no longer produces or submits proposals; it only flags stops on the print | `route_pack.py` still writes `inventory_proposals.json`, or `grep -nE 'inventory_proposals|mutations/inventory-movements|form_submissions|inventory_movement_pending' .claude/skills/route-print-pack/SKILL.md` returns anything |
| D8 | Portal approval page pre-fills the proposed lines, shows rationale, evidence and open questions | the portal component test against a fixture detail payload with 2 proposed lines renders empty rows; plus, if a Playwright-usable portal login exists (§6.B), a screenshot of the live D9 proposal shows empty rows |
| D9 | One live sweep ran in production and created ≥1 filled proposal from real data | `select count(*) from private_core.form_submissions where form_type='inventory_movement' and raw_payload ? 'proposed_lines' and submitted_by = <sweep user id> and submitted_at > <deploy time>` returns 0. If the live window truly has no candidate, D9 is ❌ `BLOCKED — no candidate` and the next guardian run closes it — never widen the window before 2026-09-22 to manufacture one. |
| D10 | The 4 stale pending proposals (oldest 2026-06-23) are each rejected with one of the two W5 reasons and listed in the report | §2.5 query 1 still shows a pending row from before 2026-09-01 with no `proposed_lines` |
| D11 | All PRs merged, CI green on each merge commit, production deploy workflow succeeded with `rebuild_verifier() = 0`, portal deployed | any PR from this work open; any required check red on a merge commit; the deploy run not `success`; `curl https://gt-factory-os-api-production.up.railway.app/health` not OK; the Vercel deployment for the portal merge SHA not `READY` |
| D12 | Skills and docs updated: route-print-pack `SKILL.md` "How to run" step 4 rewritten, new sweep skill documented, `daily-ops-guardian` C1/V2 amended with the §1.1 quote and calls the sweep, `REGISTRY.md` skills list + count updated | route-print-pack `SKILL.md` still describes submitting proposals, or `REGISTRY.md` lacks `stock-exceptions-sweep` |
| D13 | This file's STATUS line stamped `SHIPPED` with PR links | the first bold line still reads `LIVE` |

Anything not on this list is out of scope unless Tom asks.

### 1.1 Settled — do not reopen

- **Tom's written approval for this work (2026-09-23, verbatim):** `תכתוב לי מאסטרפרומפט שאדביק בסשן חדש והוא יבצע הכל מקצה לקצה כולל SIMPLIFY וVERIFICATION BEFORE COMPLITION בסוף כך שאני לא אצטרך לוודא אותו. שימזג והכל ויוודא שירוק. עבודה מקצה לקצה ללא השארת קצוות פתוחים בכלל.` It was given in reply to the diagnosis that the proposals must move to a daily sweep that submits filled proposals. Treat it as the written approval to (a) extend `daily-ops-guardian` §C C1 / §V V2 with one new allowed write — submitting *pending* inventory-movement proposals through the API (never approving, never ledger) — and (b) create the skill `stock-exceptions-sweep`. Paste this quote into both skill headers and `REGISTRY.md`.

- **Humans approve, the ledger posts only on approval.** Proposals never write `stock_ledger`. (`CLAUDE.md` §Source of truth, stock truth sacred; `0259` design.)
- **Detection moves out of the print skill** into a daily sweep over completed tasks (diagnosis 2026-09-23, Tom asked for the fix end to end).
- **Evidence priority for filling lines:** Green Invoice document named in the task title → open `credit_tasks` of the same customer → open purchase order of the supplier → free-text note mapped through `docs/warehouses/catalog-truth.md` and aliases → otherwise an open question. Never a guessed quantity.
- **Supplier / 3PL pickups are goods receipts, not inventory movements.** The sweep does not create inventory-movement proposals for them; it reports any such completed pickup with no goods-receipt submission for that supplier within ±2 days in the guardian email.
- **Cheque pattern:** `(^|[\s\-])צ['׳]?ק(ים)?($|[\s\-])` — never `צ.?ק`, which also matches `יצחק`.
- **Date windows use `lw_completed_at`** (backtests: `coalesce(lw_completed_at, captured_at)`). `captured_at` is the last poll time and moves every poll.
- **Customer→customer transfers** (e.g. `איסוף סחורה מהם ואספקה ל...`) are net zero for our stock: no proposal, one line in the guardian email.
- **No historical backfill posting.** Physical counts since June (47 FG `COUNT_ADJUST` rows, observed) may already have absorbed old drift; approving old movements would double-correct. History is reported, not proposed. Only the 4 already-pending items are handled (D10).
- **The sweep runs inside the existing 06:30 `daily-ops-guardian` run.** Do not create a new Routine or trigger (`CLAUDE.md` §Watching).

## 2. Ground truth — measured 2026-09-23; re-verify at boot

### 2.1 What is built and live
- Migration `0259_inventory_movements.sql` is applied: form type `inventory_movement`, ledger types `INVENTORY_MOVEMENT` / `_REVERSAL`, tables `inventory_movements` (context) and `inventory_movement_lines` (confirmed lines, written at approve).
- API routes (from `route.ts`): `POST /api/v1/mutations/inventory-movements`, `.../:id/approve`, `.../:id/reject`, `GET /api/v1/queries/inventory-movements/:id`.
- Submit schema has **no lines** by design (`schemas.ts`: "No structured lines at submit"). Approve requires `lines[]` typed by the approver. This is the root cause of "arrives empty".
- Portal maps exception category `inventory_movement_pending` to `/inbox/approvals/inventory-movement/<id>` (per `route-print-pack/SKILL.md` §4; the portal repo was not readable in the diagnosis session, so its current page is unverified).
- `route_pack.py` `detect_inventory_moves()` reads only `task.notes` + recipient, requires a keyword from `MOVE_HINTS`, and skips any stop with a Green Invoice link (`not s.get("gi")`). `MOVE_HINTS` lacks `השלמת`, `תעודת משלוח`, `ללא חיוב`.
- `credit_tasks` are created by the LionWheel reconciliation Phase 2 when `qty_picked < qty_ordered` on the terminal status.

### 2.2 The numbers (observed 2026-09-23)
- `inventory_movement` submissions ever: 8. Posted 2 (both hand-entered, not from the skill), rejected 2 (`כבר סופק`, `לא נכון` — the latter a false positive on `קבלת סחורה בין 7:00-12:00`, delivery hours), pending 4 (from 2026-06-23, 2026-08-11, 2026-08-18, 2026-08-19), none with lines.
- `orders_mirror` tasks captured since 2026-06-15 with zero `orders_mirror_lines`: 127. Classified by recipient name:
  - cheque pickup (loose `צ.?ק` match on 2026-09-23; re-baseline with the §1.1 pattern) 32 · supplement / delivery note / free goods (`השלמת|תעודת משלוח|ללא חיוב`) 32 (4 canceled) · exchange (`החלפ`) 6 (1 canceled) · subcontractor matcha (`עמיתה`) 7 · supplier / 3PL pickup 15 · customer pickup / return / transfer 19 · unclear 16 (1 canceled).
- Of the 38 supplement / delivery-note / exchange / free-goods tasks, **0 have a `stock_ledger` row** by task id or document number. Finished goods left the building and never came off stock.
- `credit_tasks`: 220 `PENDING`, 2 `SUPPLIED`. Supplements never close them.
- `inventory_movement_lines` for submission of source_ref `GI-20269`: 8 rows vs 4 `stock_ledger` rows — duplicated audit lines, ledger correct.
- `orders_mirror` stores no notes, driver notes or task type; `pickup_at` is null on all rows. Notes must be read live via LionWheel `GET /api/v1/tasks/show/{id}.json`.

### 2.3 What is NOT built
- Proposed lines, rationale, evidence, open questions in the contract and the portal.
- Any detection over completed tasks or over drivers other than the route driver.
- Any link from a supplement to the `credit_tasks` it fulfils.
- Kinds for supplement, free goods, subcontract (current CHECK: `pickup, exchange, return, tasting, goods_receipt, other`).

### 2.4 Known-broken, adjacent, out of scope
- 8 picking shortfalls on the 2026-09-24 Maiden route (FRESH 500ml) — operational, not this work.
- `graphify` capture in route-print-pack fails for lack of an LLM API key — not this work.
- `reason_code` canonical list is not enforced by zod (a non-canonical `FG_OUT_UNSYNCED_DELIVERY` was stored). Enforce it for proposed lines only; do not migrate old rows.

### 2.5 Re-verification block (read-only, Supabase MCP `execute_sql`, project `rvadsozabmxkkrktwgnv`)
```sql
-- 1. inventory-movement history (expect 8 rows as of 2026-09-23)
select fs.submitted_at::date, fs.status, im.kind, im.source_ref, fs.raw_payload ? 'proposed_lines' has_proposed,
 (select count(*) from private_core.inventory_movement_lines l where l.submission_id=fs.submission_id) lines
from private_core.form_submissions fs join private_core.inventory_movements im using(submission_id)
where fs.form_type='inventory_movement' order by 1;

-- 2. no-line tasks by class since 2026-06-15 (127 total on 2026-09-23 under the old captured_at filter; re-baseline)
with t as (select lw_status, lw_destination_recipient_name n from private_core.orders_mirror o
 where coalesce(lw_completed_at, captured_at)>='2026-06-15' and not exists (select 1 from private_core.orders_mirror_lines l where l.mirror_id=o.mirror_id))
select case when n ~ '(^|[[:space:]-])צ[''׳]?ק(ים)?($|[[:space:]-])' then 'cheque' when n ~ '(השלמת|תעודת משלוח|ללא חיוב)' then 'supplement'
 when n ~ 'החלפ' then 'exchange' when n ~ '(עמיתה|מדבקות מאצה)' then 'subcontract'
 when n ~ '(צבר|תבלינ|כימיקל|מדבקות|תוויות|גומיות|פרי הבוסתן|בקבוקים|יקבים|רומיכל)' then 'supplier'
 when n ~ 'איסוף' then 'customer_pickup' else 'unclear' end cls, count(*), count(*) filter (where lw_status='CANCELED') canceled
from t group by 1 order by 1;

-- 3. credit tasks (expect 220 PENDING / 2 SUPPLIED)
select status, count(*) from private_core.credit_tasks group by 1;
```

## 3. What the hard part actually is

1. **It looks like an LLM-quality problem; it is a contract problem.** The API cannot carry a proposed line, so no amount of understanding reaches the inbox. Fix the contract first, then the detector, then the reasoning.
2. **The biggest leak is not returns, it is supplements.** 32 of the no-line tasks are finished goods going out with no order lines, usually after a picking shortfall. The pick bridge never sees them, and the matching `credit_task` stays `PENDING`. The document number in the task title (`השלמת סחורה 63810`, `תעודת משלוח 20286`) makes most of these deterministic: fetch the Green Invoice document, map barcodes to `item_id`, done.
3. **The proposal is born on the wrong day.** Creating it while printing the route, before delivery, proposes movements that get canceled (7 canceled tasks in the relevant classes). Trigger on `COMPLETED`, all drivers.
4. **The signal lives in the task title, not in `notes`.** Read recipient name, `notes`, `driver_note`, `org_note` and visit notes together.
5. **The LLM is the last evidence source, not the first.** Deterministic sources fill most lines. Free text fills the rest with a stated confidence. Anything underivable becomes an explicit open question, never a number.

## 4. Workstreams

Order: W1 → W2 → W3 → W4 → W5 → W6. W4 can start once W1's contract is merged.

### W1 — Backend contract (`gt-factory-os`, lane `backend-db`)
- Extend `InventoryMovementSubmitSchema` with optional `proposed_lines[]` (same shape as `InventoryMovementLineSchema` plus `source` ∈ `gi_document | credit_task | purchase_order | note_parse | manual`, `evidence_ref`, `confidence` ∈ `high | medium | low`), `rationale` (Hebrew text: what happened, what goes out, what comes in, why), `open_questions[]`, `evidence[]` (`{type, ref, url?}`), `credit_task_ids[]`.
- Validate proposed lines at submit: split `validateLine` so submit runs only the item-active, item-type and uom checks — **no advisory lock and no `COUNT_FREEZE_ACTIVE` check at submit** (both stay on approve), or proposals would fail on count days. Reject 409 with `offending_field`.
- Enforce the canonical `reason_code` list for proposed lines. Mapping, no new codes: supplement → `goods_out`; free_goods → `goods_out`; exchange → `exchange_in` + `exchange_out`; return → `return_in`; tasting → `tasting`; subcontract → `goods_out` (PKG/RM to subcontractor) and `goods_pickup` (FG collected).
- Add a non-interactive auth path for the sweep: production accepts only a Supabase user JWT (`api/src/auth/session.ts`; `X-Test-Session` works only with `ENABLE_DEV_SHIM_AUTH`). Add a service-token check (header, compared constant-time to env secret `INVENTORY_SWEEP_TOKEN`) that maps to a dedicated `app_users` row `inventory-sweep` with role `operator`, allowed **only** on `POST /api/v1/mutations/inventory-movements`. Never `admin`. Tom sets the secret (§6.A).
- Store them in `raw_payload` (no new table needed); return them from the detail query.
- Add kinds `supplement`, `free_goods`, `subcontract` via a new migration. The `inventory_movements.kind` CHECK was created inline with an auto-generated name: find it by definition in `pg_constraint` (as `0241` does), never `drop constraint if exists <guessed name>`. Next free number: check `db/migrations/` at boot (last observed `0349`).
- Approve: for each `credit_task_ids` entry, move to `SUPPLIED` (with `closed_by`, `closed_at`, and `emitChangeLog` exactly as `credit_tracking/handler.ts` does) only if its status is `PENDING` or `DEFERRED`, its `item_id` equals an approved line's `item_id`, and that line's quantity ≥ `qty_missing`. Otherwise leave it and list it in the approve response. `credit_tasks.status` is the bookkeeper's (`0241`) — never overwrite `CREDITED`.
- Duplicates (D4): first find how `GI-20269` got 8 lines — `select stock_ledger_movement_id, count(*) from private_core.inventory_movement_lines where submission_id=(select submission_id from private_core.inventory_movements where source_ref='GI-20269') group by 1;` plus `git log -p api/src/inventory-movements/handler.ts`. Write a test reproducing that cause, then fix. The migration de-duplicates only rows that are exact copies (same submission, direction, item, qty, unit, reason, ledger id), `raise notice` their `line_id`s, then adds `unique (stock_ledger_movement_id)`. This is the audit table, not the ledger. Not exact copies → STOP (§8).
- Tests first (vitest, `api/test/inventory_movements.test.ts`): D1–D4 cases plus the exception path (invalid proposed item → 409).
**Acceptance:** D1, D2, D3, D4.

### W2 — Daily sweep skill (brain repo, new skill `.claude/skills/stock-exceptions-sweep/`)
- Input: `orders_mirror` rows with `lw_status='COMPLETED' and lw_completed_at >= now() - interval '3 days'`, all drivers. No state file — each run is a fresh container; the idempotency key below makes the overlap harmless. Read each task live via LionWheel `tasks/show`.
- Candidates: tasks with zero order lines, plus tasks of any kind whose title or notes carry an exchange / return / tasting / free-goods signal.
- Classify (cheque pattern from §1.1; the dry-run prints every task it classified as cheque): cheque → skip; customer→customer transfer → email line only; supplier / 3PL → goods-receipt check (§1.1) → email line only; supplement / free goods / exchange / return / tasting / subcontract / unclear → proposal.
- Fill lines by the §1.1 evidence priority. Green Invoice fields are **not yet verified** (`CLAUDE.md` Forbidden assumptions): before writing the mapper, fetch one known invoice (`63810`) and one delivery note (`20286`), record the real search filter for number and document type and the real item fields in route-print-pack `SKILL.md` Data contracts, and map using only fields seen in those responses. The rendered invoices show a barcode column; confirm which API field carries it. Map to `item_id` via the DB item / alias tables and `docs/warehouses/catalog-truth.md`.
- Exchange: two lines (in returned, out replacement) unless the replacement already appears in picked order lines. Return: in-line plus the open question `האם הסחורה חוזרת למלאי או לפחת?`. Subcontract: lines per the note (PKG out on delivery to subcontractor, FG in on collection) plus an open question confirming the rule.
- Submit via `POST https://gt-factory-os-api-production.up.railway.app/api/v1/mutations/inventory-movements` with the W1 service token and a deterministic `idempotency_key` = `sweep:<lw_task_id>`. Writing rows directly into `form_submissions`, `inventory_movements` or `exceptions` (e.g. via Supabase MCP) is forbidden — it bypasses every W1 check.
- Output: counts per class + list of email lines, consumed by `daily-ops-guardian`.
- `--dry-run --from --to` mode (window on `coalesce(lw_completed_at, captured_at)`) that prints proposals without submitting; used for D5/D6. Re-baseline the §2.2 counts with this filter at boot; differences from §2.2 are expected, not a failed boot check.
**Acceptance:** D5, D6.

### W3 — Route-print-pack cleanup (brain repo)
- Stop writing `inventory_proposals.json` in `route_pack.py`; delete the submit instructions and the Supabase-MCP "last-resort fallback" from `SKILL.md` "How to run" step 4; keep `detect_inventory_moves` only as a print flag, fixed to read the title and all note fields, including stops that have an invoice.
- Rewrite that step to point at the sweep.
**Acceptance:** D7, part of D12.

### W4 — Portal (`gt-factory-os-portal`, lane `portal`)
- On `/inbox/approvals/inventory-movement/<id>`: pre-fill editable line rows from `proposed_lines`; show `rationale`, evidence links, confidence badges and `open_questions` above the lines; Approve submits the (possibly edited) lines as today.
- Hebrew copy follows the portal's locked register; if a needed string has no approved register entry, the `portal-production-executor` stop condition applies (§6.B).
**Acceptance:** D8.

### W5 — Wire into the guardian and handle stale items
- Amend `daily-ops-guardian` C1/V2 with the §1.1 quote and add a sweep stage (email section: new proposals, supplier pickups without receipt, transfers).
- D10: for each of the 4 stale pending items, exactly one of: (a) every involved item has a `COUNT_ADJUST` after the task date → reject with reason `נספג בספירת מלאי <date>`; (b) otherwise → reject with reason `ישן מחלון התיקון — דווח במייל` and list it in the report. Never resubmit history (§1.1; submit also enforces `dataentry_correction_window_days`, `handler.ts:113`). Reject through the API as Tom's portal session is not available to you: use the sweep token only if W1 allows reject for it; otherwise reject is a §6 item.
**Acceptance:** D10, D12.

### W6 — Ship
- PR per repo, draft → ready when local checks pass. `npm run typecheck` and the vitest suite locally before every push. Merge on green (`CLAUDE.md` §Authorization).
- Migration + API deploy: dispatch `deploy-production.yml` with `confirm=APPLY` after posting the one-line announcement the authorization section requires. Confirm the run's `rebuild_verifier() = 0` step passed. Portal deploys on merge via Vercel; confirm the deployment is live.
- Run the sweep once live (D9); verify D1 by reading that proposal back; D8 per its row; do **not** approve it.
- Run `simplify`, then `verification-before-completion`, then stamp this file (D13) in the brain PR before merging it.
**Acceptance:** D9, D11, D13.

## 5. Scope

**IN:** everything in §4.
**OUT — do not touch, do not "improve":** the pick bridge's posting logic in `reconciliation.ts` (read it, do not change it) · Shopify sync and its frozen flags · `stock_ledger` rows directly (never insert, update or delete) · approving any live proposal · historical backfill proposals (§1.1) · the route-pack PDF layout · `tailwind.config.ts`, `globals.css`, `portal_ux_standard.md`.

## 6. Tom's part — the complete list, nothing else is his

**A. Portal repo access — only if `add_repo` for `tomw200082-collab/gt-factory-os-portal` is denied.** On 2026-09-23 `list_repos` did not return that repo for this account. If denied, relay the tool's exact reason and the remedy it names; continue W1–W3 and W5 meanwhile. Nothing else in this list blocks until then.
**A2. Set the sweep secret.** Tom generates a random value and sets `INVENTORY_SWEEP_TOKEN` in Railway (API service) and in this Claude environment's secrets. Nobody pastes it in chat. You verify it through the side effect: a sweep submit returns 202. Ask once W1 is merged; ~5 minutes.
**A3. Reject rights for D10** — only if W1 does not grant reject to the sweep user (keep it submit-only by default): Tom rejects the 4 stale items in the portal with the reasons you give him.
**B. A portal login usable by Playwright** — only if none exists; otherwise D8 rests on the component test.
**C. A Hebrew UI string with no approved register entry** — only if W4 needs one. Ask once, batched, with the exact proposed strings.

Everything else — including merge, deploy, and the stale-item rejections — is yours.

## 7. Landmines — do not rediscover these

1. **Sweep finds no candidates in `notes`** — the signal is the task title (`lw_destination_recipient_name`, e.g. `... - השלמת סחורה 63810`) → read title + `notes` + `driver_note` + `org_note` + visit notes.
2. **`צק` / `צ'ק` / `צ'קים` look like pickups** — they are cheques, no stock → skip before classifying `איסוף`.
3. **`קבלת סחורה בין 7:00-12:00`** is delivery hours, not a goods receipt → never classify on `קבל`.
4. **A 5-digit number in the title can be an invoice (`6xxxx`) or a delivery note (`2xxxx`)**, and substring-matching ledger notes produces false hits (`20286` matched an unrelated `420286864`) → match Green Invoice documents by exact number and type.
5. **LionWheel formats changed 2026-09-23:** `driver_str` empty on the task (it is on `visits[0]`), `pickup_at` is `DD/MM/YYYY`, `eta_at` is bare `HH:MM`, `daily_order` is gone. Already fixed in `route_pack.py` (PR #206) — reuse those helpers, do not re-derive.
6. **`orders_mirror.pickup_at` is null on every row, and `captured_at` is the last poll time** → windows on `lw_completed_at` only (backtests: `coalesce(lw_completed_at, captured_at)`).
7. **The system `cryptography` package in the container panics (`_cffi_backend`)** when `pypdf` imports it → `python3 -m pip install --ignore-installed cffi cryptography`.
8. **Approving old movements double-corrects** stock already fixed by a physical count → never propose history (§1.1).
9. **Self-approval**: the handler allows it only for `admin` / `planner`. The sweep submits as the `operator` service user, so Tom (admin) approves normally; do not change that rule.
11. **`2. "Validate with validateLine"` pulls in the count-freeze lock** → split it (W1).
12. **Guardian §C C1 is Tom-locked** — amend it only with the §1.1 quote, nothing wider.
10. **Opening a PR subscribes the session server-side** even with the hook live → `unsubscribe_pr_activity` right after every `create_pull_request`.

## 8. Halt conditions

Inherited from `CLAUDE.md` §Stop conditions. Additions for this work:
- A change would write `stock_ledger` outside the existing approve handler → **STOP**.
- A proposed line cannot be tied to evidence and you are tempted to put a quantity anyway → **STOP** for that item; make it an open question instead.
- The deploy workflow's `rebuild_verifier()` step is non-zero → **STOP**, do not retry, report.

## 9. Final report

Use `CLAUDE.md` §Handoff (STATUS + the 8 PASS fields, tokens from `VERDICT_GLOSSARY.md`), in Hebrew, plus:
1. What Tom can now watch working: one live proposal id and its portal URL.
2. D1–D13 each ✅/❌ with its evidence pointer (query output, test N/N, run URL, screenshot path). No partial credit.
3. Backtest numbers per class from the D5/D6 dry-run.
4. PR links (all merged), deploy run URL.
5. What is still Tom's (only §6 items, if they happened) and anything genuinely unfinished.
6. The single next action, or `לא נדרש ממך כלום`.

If anything is not ready, say so first and plainly.
