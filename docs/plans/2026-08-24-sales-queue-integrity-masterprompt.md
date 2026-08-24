# MASTERPROMPT — the sales workspace becomes usable by a team, and stops hiding commitments

**STATUS: LIVE — not yet executed**

> **Usage:** paste this entire file as the first message of a fresh session with
> `gt-factory-os`, `gt-factory-os-portal` and `gt-factory-os-production-brain` attached.
> It takes the sales workspace from "one admin, and a queue that hides the callbacks he
> promised" to "four people can work it, and a promise made is a promise shown."
> It halts for you only where a human must genuinely act — §6 is that complete list.
>
> **Provenance:** written 2026-08-24, from live measurement of Postgres
> `rvadsozabmxkkrktwgnv`, the Shopify Admin API, the Make API, and code executed in this
> repo (not read — executed; see §7.1). Authority, in order:
> `gt-factory-os-production-brain/CLAUDE.md` → `EXECUTION_POLICY.md` → `CURRENT_STATE.md`
> → each repo's own `CLAUDE.md`. Cited below, never copied.
>
> **Shelf life:** §2 is presumed wrong if pasted after 2026-09-07. Run §2.5 first.
> **Divergence protocol:** if §2.5 disagrees with §2 on lead counts or user rows, adapt
> and note it. If it disagrees on the §3.1 reorganizing fact — if follow-ups are no
> longer starved — **halt and surface**: someone else fixed it and this document's
> ordering is wrong.

---

## 0. How to work

- **Who you are here:** a Claude Code session with write access to both product repos,
  admin on Supabase (project `rvadsozabmxkkrktwgnv`), Shopify, Make and GitHub. You may
  decide implementation freely. You may **not** decide anything in §1.1 or §6.
- **Read first, in order:** `gt-factory-os-production-brain/CLAUDE.md` ·
  `gt-factory-os/CLAUDE.md` · `gt-factory-os-portal/CLAUDE.md` ·
  `gt-factory-os-portal/docs/portal-os/tranches/164-queue-triage-and-cap.md` (the
  tranche that specified the bug you are fixing — read it before you argue with §3.1).
- **Authority:** where this document and an authority doc disagree, the authority doc
  wins and this document is wrong.
- **Halt conditions, evidence standard, git discipline, lane boundaries:** inherited from
  `gt-factory-os-production-brain/CLAUDE.md` §Stop conditions and §Evidence. Deltas for
  this work only are in §8.
- **The standard.** Tom's words: *"אני רוצה שתהיה מקצוען"* and *"מערכת באמת מקצועית
  וישימה לעבודה בפרודקשן"*. Translated into three checkable prohibitions:
  1. **Nothing on screen may be false.** A count, a date or a status the UI shows must
     match what the database holds. §3.2 exists because this was violated.
  2. **Nothing may be silently deferred.** If the UI declines to show a row, it says so
     and says how many — and it may never decline to show a commitment.
  3. **No done-claim without a run.** Not a passing type-check, not a code read. The
     command, and its output. `gt-factory-os-production-brain/CLAUDE.md` §Evidence binds.
- **Language:** reason in English. All operator-facing strings in the `(sales)` route
  group are **Hebrew + `dir="rtl"`** — authorized in `gt-factory-os-portal/CLAUDE.md`
  §UI language, row `/apps + route group (sales)`, 2026-08-17. Report to Tom in Hebrew.

---

## 1. Mission and definition of done

**One testable sentence:** a callback Tom promised is the first thing he sees on the day
he promised it, and Erik, Avi and Alex can each work their own queue without being made
system administrators.

| # | Condition | The observation that would prove it false |
|---|---|---|
| **D1** | A due follow-up is never suppressed by the daily cap | With ≥ 20 `new_lead` rows, cap 15, and ≥ 1 `due_follow_up` row, the rendered follow-up section contains ≥ 1 card. Assert it in `tests/unit/sales/today-queue.test.tsx`; the existing test at that file's *"spends one daily budget across the queue"* asserts the opposite and **must be rewritten, not deleted** — see §7.2 |
| **D2** | Due follow-ups sort above new leads | `api_read.v_sales_today` ordered by the handler's `ORDER BY` returns every `due_follow_up` row before every `new_lead` row. Run the query, paste the rows |
| **D3** | "אבוד" is reversible from every path that can set it | Three paths (card button, outcome sheet after a call, lead drawer). Each shows an undo action. Grep for `setUndo` and find three call sites, then exercise each in a test |
| **D4** | An outcome is never recorded that the user did not choose | Submitting a custom date after "לא ענה" writes `result:'no_answer'`. Query `sales_core.lead_event` for the `outcome` payload after the interaction — `answered_progressing` must not appear |
| **D5** | A non-admin sales user can load their queue and record an outcome | `GET /api/sales/today` and `POST /api/sales/leads/:id/outcome` both return 2xx for a session whose role is `sales_rep`. Currently both return 403 |
| **D6** | There is exactly one roster | `sales_core.app_setting` has no `assignees` key, and the assignee list served to the portal derives from `private_core.app_users` |
| **D7** | A due callback reaches the person who owns it, outside the app | A row in `sales_core.lead_event` with `event_type='reminder_sent'` whose payload names a recipient that is not hardcoded |
| **D8** | A phone-closed deal can be recorded as won | `sales_core.set_lead_status(p_status => 'won', ...)` succeeds when given a Green Invoice document number and fails without one. pgTAP proves both branches |
| **D9** | The status of this document is stamped | This file's status line reads `SHIPPED` or `ABANDONED — <why>` with evidence pointers |

Anything not on this list is out of scope unless Tom asks.

### 1.1 Settled — do not reopen

| Decision | Who, when |
|---|---|
| Backlog is worked by **mass personalised outreach first, then call only responders** — not 15 calls/day for 10 days | Tom, 2026-08-24 |
| That outreach is **blocked** on the product catalogue being finished. Do not build the send | Tom, 2026-08-24 |
| Won is proven by a **Green Invoice document number**. Free text was rejected | Tom, 2026-08-24 |
| Multi-user is done with a **`sales` axis on the existing capability lattice**, not a fourth registry and not by widening `admin\|planner` | Tom, 2026-08-24 |
| `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` stays `false`. No message ever leaves the product to a lead or customer | brain `CLAUDE.md`; Sales-Machine `CLAUDE.md` §7 |
| `newest_first` inside the `new_lead` section is correct and stays | tranche 164 D3; re-confirmed by §2.2 age distribution |

---

## 2. Ground truth — measured 2026-08-24, re-verify at boot

### 2.1 What is built and live

Lead intake works end to end. A real lead landed today at 16:15:43Z (Arabic business
name), was mapped correctly, and alerted Tom within 5 seconds. The Make webhook is
page-level on page `1939072889681856` — all forms on the page, not a per-form
subscription. `/ingest` is idempotent on `unique (source, external_id)`. A
`builtin:Break` retry handler (10 attempts, 10-minute interval) was added to Make
scenario `7075235` on 2026-08-24 16:50Z, so a transient `/ingest` failure no longer
loses the lead.

The portal `(sales)` route group has five screens and real machinery behind all of them:
`AssigneePicker`, `bulk-assign`, `next-touch`, `OutcomeSheet`, `EventTimeline`, a
capability-gated shell. Tranches 162–172 built it. `_active.txt` reads `172`.

### 2.2 The numbers

```
sales_core.lead        187 new · 0 working · 3 won
assignee set             0 of 187
next_touch_at set        1 of 187
first_touch_at set       4 of 187
api_read.v_sales_today   150 rows      (cap is 15 → 10 working days)
uncontactable            39  (no phone AND no email; excluded from the queue,
                              but stay status='new' forever — no exit path)
campaign_name empty    186 of 187      (the CSV import carried no campaign/ad/city;
                              only the live Make lead carries "MACHA Leads")
org.shopify_customer_id  13 of 187

age of the 187:  <7d: 2 · 7-30d: 22 · 2026-06-07→07-24: 80 (all callable) ·
                 2-12mo: 45 · >1yr: 38 (0 callable — these ARE the uncontactable)

private_core.app_users, active:
  tom@gteveryday.com          admin     Tom
  alex.berov@gmail.com        planner   Alex      ← in the system, 403 on all sales
  adi@gteveryday.com          viewer    Adi
  denispotehin@gmail.com      operator  Denis
  production@gteveryday.com   operator  Maxim
  accounting@greentea-...     planner   Doreen
  demo@gteveryday.com         admin     GT Sales Demo   ← created today, see §7.5

sales_core.app_setting:
  assignees   [{ name: "תום", email: tom@…, active: true }]     ← one name
  queue       { order: "newest_first", daily_cap: 15 }
  sla_hours   { hours: 24 }
```

**Erik and Avi do not exist in `app_users`.** Tom believes he added them; he added Alex.

### 2.3 What is NOT built

- No `sales` axis in `ROLE_CAPABILITY_LATTICE` (`gt-factory-os-portal/src/lib/auth/authorize.ts:32`).
  Axes are `stock | planning | admin` only. The sales workspace bypassed the lattice and
  hardcoded `session.role !== 'admin'`.
- No `sales_rep` role. `private_core.app_users` constraint `app_users_role_check` allows
  `admin|planner|operator|viewer` only — a migration is required.
- Nothing reads `next_touch_at` outside the queue's `ORDER BY` and two views. The daily
  heartbeat (`cron.job` 28, `0 4 * * *`) selects leads/poll/rejects counts and does not
  select due follow-ups.
- `ALERT_RECIPIENT` is a module constant, `tom@gteveryday.com`
  (`gt-factory-os/supabase/functions/sales-leads-poll/_lib/email.ts:20`), deliberately.

### 2.4 Known-broken, adjacent, out of scope

These pre-date you. Do not fix them; do not let them read as your fault.

- 2 stuck bundles in Make scenario `7075235` (`dlqCount: 2`) from 13:44 and 13:47Z. They
  are Tom's own Facebook test submissions. Retry will not recover them — the stored body
  has `field_data: null` and no `data` key. There is no API to clear them.
- 3 `ACTIVE` items unmapped to Shopify: `ADD-ODK-ACB-1L`, `ADD-ODK-RED-1L`, and
  `EXCLUDED-NONSTOCK` (a placeholder that is not a sellable item and arguably should not
  be `ACTIVE`+`BOUGHT_FINISHED`).
- One test lead sits in the production queue: `sales_core.lead` id
  `82783652-6536-4dd9-aa67-3a899fcc11e9`, org display name contains
  `<test lead: dummy data …>`. Clear it via the portal's own status control, not SQL.
- The Make Facebook connection (`6309050`) **expires 2026-10-23T10:49Z**. A calendar
  reminder exists for 2026-10-16. When it lapses, Meta stops delivering and leads
  submitted in that window are lost permanently — no queue, nothing to retry.

### 2.5 Re-verification block

```sql
-- regenerates the load-bearing half of §2.2 in one paste
select
  (select count(*) from sales_core.lead where status='new')                    as new_leads,
  (select count(*) from sales_core.lead where assignee is not null)            as assigned,
  (select count(*) from sales_core.lead where next_touch_at is not null)       as with_next_touch,
  (select count(*) from api_read.v_sales_today)                                as queue_today,
  (select value from sales_core.app_setting where key='queue')                 as queue_settings,
  (select count(*) from sales_core.app_setting where key='assignees')          as roster_key_still_exists,
  (select count(*) from private_core.app_users
     where status='active' and role='sales_rep')                               as sales_reps;
```

```bash
# D1 must fail before you fix it. This is the red half of red-green.
cd gt-factory-os-portal && npx vitest run "src/app/(sales)/_lib/queue.test.ts" \
  tests/unit/sales/today-queue.test.tsx
```

---

## 3. What the hard part actually is

**3.1 — The reorganizing fact. The queue does not have a bug; it has a wrong
requirement, and the requirement passed review.**

`CAPPED_SECTIONS = ['new_lead', 'due_follow_up']` share one budget, drained in render
order. Executed against the live shape:

```
CAPPED_SECTIONS = [ 'new_lead', 'due_follow_up' ]
cards rendered  = { new_lead: 15, due_follow_up: 0 }
```

Tranche 164 **specified** this. Its prose reasons it out — *"conversions and returning
customers are never capped: they are news and the one case that must never go quiet, not
workload"* — and classifies `due_follow_up` as backlog. Its checklist ticks
`[x] The new-lead and follow-up sections cap at daily_cap`. A unit test asserts
`UI.dailyCommitment(0, 20)` for the follow-up section. The Hebrew copy explains the
behaviour to the user: *"which is also why a later section can read 0 while an earlier
one is full."*

So: implementation, test, checklist, copy and release gate all agree with each other and
all are wrong together. **You cannot find this class of defect by reviewing an
implementation against its spec.** The doctrine error is the one sentence to overturn:
*a callback you promised is not discretionary workload; it is a commitment already made,
and it belongs with conversions and returning customers on the never-capped side.*

The test comment records how it happened: an earlier bug made a cap of 15 mean 15 + 15 =
30 calls; the release gate flagged it P1; the fix over-corrected from "two budgets" to
"one budget, and follow-ups lose."

**3.2 — It is not hypothetical, and it is dated.** At 16:44Z today Tom called Ido
Lokmish, got no answer, and scheduled a callback for 2026-08-25 06:00Z. That is the only
`next_touch_at` in the database. Tomorrow at 09:00 Israel time it becomes
`due_follow_up` and renders zero cards. It is also invisible *today* — it has a
`first_touch_at`, so it is filtered out of `new_lead`, and its `next_touch_at` is still
future. The one lead ever worked in this system fell into a hole in both windows.

**3.3 — "Can leads be assigned to agents" is an identity problem, not a UI problem.**
Three registries must agree and nothing checks that they do: `private_core.app_users`
(who logs in), `requireSalesAccess` (admin only), and `app_setting('assignees')` (one
name). Alex is in the first, excluded by the second, absent from the third. The fix is to
delete a registry, not add a screen.

**3.4 — The backlog and the live flow are two different problems.** 186 of 187 leads
carry no campaign, ad or city. Any value scoring over the backlog would be invented.
Live leads via Make carry all of it. Do not build one queue-scoring mechanism for both.

**3.5 — The unlinked leads are not missed matches; they are prospects.** 20 unlinked
lead phones were checked against Shopify with a control proving the search indexes
address phones (`0525610052` → a real customer). **0 of 20 matched.** Migration
`0330_sales_org_shopify_backfill.sql:46` explains the structural half: the customer-setup
convention deliberately keeps phone and email *off* the Shopify customer record, so the
properly-created B2B customers are exactly the ones matching cannot find. A fourth
matching layer would be wasted work.

---

## 4. Workstreams

Order matters: W1 is the smallest diff and the one that bites tomorrow.

### W1 — a commitment is never deferred *(portal only)*

Remove `'due_follow_up'` from `CAPPED_SECTIONS` in
`gt-factory-os-portal/src/app/(sales)/_lib/queue.ts:22`. Move `due_follow_up` above
`new_lead` in `SECTION_ORDER`, and make the server agree —
`gt-factory-os/api/src/sales/queries_handler.ts:75-80`, the `ORDER BY CASE`. Inside the
follow-up section, oldest `next_touch_at` first: the most overdue promise leads.

Update the `dailyCapRule` copy — it currently teaches the user the wrong rule.

**Acceptance:** D1, D2.

### W2 — every destructive path is reversible; no outcome is invented *(portal only)*

`setUndo` in `submitOutcome` when `result === 'lost'`
(`sales/today/page.tsx:127`), and the same in the drawer path
(`sales/leads/page.tsx:282`). The working pattern is at `today/page.tsx:249` — copy it.

In `OutcomeSheet.tsx`, the root-step "שנה תאריך" button reaches the date step without an
outcome having been declared, and every date button submits `{...progressing}` where
`progressing = { result: 'answered_progressing' }` (line 147). Restructure so the outcome
is declared first and the date step is a disclosure under it. A no-answer with a custom
date must write `no_answer`.

**Acceptance:** D3, D4.

### W3 — one roster, four people *(portal + backend + migration)*

1. **Migration** (next free slot; list `db/migrations/` immediately before and after
   writing — brain `EXECUTION_POLICY.md` FR1/FR2): extend `app_users_role_check` to
   include `sales_rep`. `ALTER … DROP CONSTRAINT … ADD CONSTRAINT`. No `DROP COLUMN`.
2. **Portal:** add `"sales"` to `CapabilityAxis`, `CapabilityGrants`,
   `ROLE_CAPABILITY_LATTICE` and `CapabilityRequirement`
   (`src/lib/auth/authorize.ts`). Grants: `sales_rep` → `sales: "execute"`, everything
   else `null`; `admin` → `sales: "execute+override"`; `planner`/`operator`/`viewer` →
   `null`. Alex is a `planner` today — Tom decides in §6.B whether he becomes
   `sales_rep` or the `planner` row gains `sales: "execute"`.
3. **Backend:** `requireSalesAccess` (`api/src/sales/queries_handler.ts:14`,
   `mutations_handler.ts:26`) checks the capability, not `role === 'admin'`.
4. **Roster:** `handleSalesSettings` derives assignees from `private_core.app_users`
   where the sales capability is granted and `status='active'`. Then remove the
   `assignees` key from `sales_core.app_setting` and the settings-screen editor for it.
5. Nav and middleware admit `sales_rep` to `/sales/*` and to nothing else.

**Acceptance:** D5, D6.

### W4 — the promise reaches the person *(backend / Edge Function)*

A morning digest, per assignee, of callbacks due today. Reuse
`supabase/functions/sales-leads-poll/_lib/email.ts` (same Resend path, same Hebrew
register, same table-based HTML) and add a `route: 'reminders'` beside the existing
`daily`. Schedule it with `pg_cron` at 06:00 Israel time. Recipient comes from the lead's
`assignee`, falling back to Tom when null. Write one `lead_event` per send so D7 is
observable and so a second run the same day does not double-send.

**Acceptance:** D7.

### W5 — a phone close is a real close *(migration + backend + portal)*

Extend `sales_core.set_lead_status` to accept `p_status => 'won'` when — and only when —
a Green Invoice document number is supplied, recording it in `converted_order_ref` with
an event whose actor is the rep, distinct from the Shopify-sourced
`system:sales-leads-poll`. The `SALES_WON_IS_EVIDENCE_ONLY` rule is **extended, not
removed**: won still requires evidence; Green Invoice is now admissible evidence.
pgTAP must prove both branches. Surface it in `OutcomeSheet` as a fourth outcome.

Do **not** call the Green Invoice API to validate the number in this workstream. Storing
it is enough; verification is a later decision.

**Acceptance:** D8.

---

## 5. Scope

**IN:** everything in §4.

**OUT — do not touch, do not "improve":**

- The mass-outreach send. §1.1 blocks it on the catalogue. You may not build a sender.
- `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` and every frozen flag in
  `gt-factory-os/CLAUDE.md` §Frozen.
- Shopify matching. §3.5 closed it.
- The Make scenario. It was changed today and is working; leave `7075235` alone.
- The 3 unmapped items and the `EXCLUDED-NONSTOCK` placeholder (§2.4).
- `stock_ledger`, `current_balances`, `balance_anchors`, projections — brain `CLAUDE.md`
  §Source of truth. Nothing in this masterprompt touches stock.
- The 18 P1/P2 copy findings and the visual/a11y findings. They are real and they are a
  later tranche; the report is at the artifact linked in §9.

---

## 6. Tom's part — the complete list, nothing else is his

**A. Erik's and Avi's email addresses.** They are not in `app_users` (§2.2) and you
cannot invent them. Ask once, in Hebrew, and continue with the rest of W3 while waiting —
the migration and the lattice do not depend on the addresses.

**B. One decision: does Alex become `sales_rep`, or does `planner` gain `sales:
execute`?** Alex is `planner` today. Making `planner` a sales role also gives Doreen
(accounting) the sales workspace, which nobody asked for. Recommend `sales_rep` and say
why; Tom decides.

**C. Deactivate `demo@gteveryday.com`** (§7.5) once the demo is no longer needed. It is a
live `admin` account created 2026-08-24. You may not decide when the demo is finished.

**D. The 38 leads with no phone and no email** (§2.2) have no exit path and never will.
Tom decides: bulk-mark them `lost` with a reason, or leave them. Do not decide this.

Everything not listed here is yours.

---

## 7. Landmines — do not rediscover these

1. **The Bash tool keeps its working directory between calls.** A `cd` into
   `gt-factory-os` persists, and a later `ls tests/e2e/` silently searches the wrong repo.
   This produced a confident, wrong finding in the session that wrote this document —
   "the portal has no E2E tests" — when it has 43 files and `@playwright/test ^1.59.1`.
   **Always pass absolute paths, or `cd` in the same command.**
2. **The test that locks the bug in is not a regression you caused.**
   `tests/unit/sales/today-queue.test.tsx`, *"spends one daily budget across the queue"*,
   asserts `UI.dailyCommitment(0, 20)` for the starved follow-up section. Rewriting it is
   part of W1. Rewrite it to assert the corrected doctrine and say so in the commit —
   deleting it loses the guard against the original 15+15=30 bug it was written for.
3. **The Supabase MCP `execute_sql` runs read-only.** `SELECT FOR UPDATE`, `TRUNCATE` and
   any write fail with `25006`. `sales_core.set_lead_status` and
   `private_core.rebuild_verifier()` both fail through it. Use `apply_migration` for DDL
   only; do data changes through the product's own API.
4. **This environment has no `DATABASE_URL`.** `cd api && npm test` cannot run the
   DB-backed suites. The DB-free sales tests do run: 57/57 as of 2026-08-24 across
   `sales_leads_make_intake`, `sales_leads_poll_mapping`, `sales_leads_poll_alerts`,
   `sales_leads_token_diag`. Report which suites you could not run rather than implying
   coverage you do not have.
5. **`demo@gteveryday.com` is `role='admin'`, `status='active'`, created today.** Every
   other test account in `app_users` is `inactive`. It will show up in any user list you
   build in W3. Do not silently deactivate it — §6.C.
6. **Only `typecheck` runs on `pull_request`.** `phase10-node-tests` is
   `workflow_dispatch` only and its explicit file list contains no `sales_*` test. A
   green PR check means the types compile and nothing else. Say that plainly when you
   report.
7. **The Playwright browser needs an explicit path.** This image ships Chromium 1194;
   Playwright 1.59.1 expects 1217. Use `PW_CHROME_PATH=/opt/pw-browsers/chromium`
   (precedent: portal PR #212). "Browser missing" is the wrong diagnosis — it is present
   at `/opt/pw-browsers/`.
8. **A lead can be invisible in both windows.** `v_sales_today` admits `new_lead` only
   when `first_touch_at IS NULL`, and `due_follow_up` only when `next_touch_at <= now()`.
   A touched lead with a future callback is in neither. Check this when W1 looks done and
   a lead you expected is still missing.

---

## 8. Halt conditions

Inherited set cited in §0. Additions specific to this work:

- A change would make a lead **less** visible than it is today → **STOP**. The entire
  point of W1 is the opposite direction.
- The migration slot you claimed appears in `db/migrations/` under another name when you
  re-list → **STOP**, `contract_failure`, do not renumber silently (brain
  `EXECUTION_POLICY.md` FR1/FR2).
- W5 tempts you to relax `SALES_WON_IS_EVIDENCE_ONLY` rather than extend it → **STOP**.
  Extending it keeps every won provable; relaxing it makes won a claim.
- §2.5 shows follow-ups are already un-starved → **STOP and surface**. Someone else moved;
  re-plan before writing.
- Any work would touch `stock_ledger` or a projection → **STOP**. Nothing here should.

---

## 9. Final report

Follow `gt-factory-os-production-brain/AGENT_TEMPLATE.md` §Output format, tokens per
`VERDICT_GLOSSARY.md`. Beyond that shape, state:

1. What a stranger can now watch working, end to end — name the screen and the click.
2. Each of D1–D9 ✅/❌ with its evidence pointer. No partial credit.
3. The numbers, re-run from §2.5, beside the §2.2 values.
4. Which test suites ran and which could not, and why (§7.4, §7.6).
5. What is still Tom's from §6, and what is genuinely unfinished.
6. The single next action.

Then stamp this file's status line. That is D9 and it is the last thing you do.

**Audit that produced this document:** https://claude.ai/code/artifact/8a720deb-bd36-4966-8cd7-49d80609d036

If anything is not ready, say so first and plainly.
