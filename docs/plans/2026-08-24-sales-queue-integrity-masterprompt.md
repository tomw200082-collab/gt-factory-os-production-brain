# MASTERPROMPT — the sales workspace becomes usable by a team, and stops hiding commitments

**STATUS: LIVE — not yet executed**

> **Usage:** paste this entire file as the first message of a fresh session with
> `gt-factory-os`, `gt-factory-os-portal` and `gt-factory-os-production-brain` attached.
> It takes the sales workspace from "one admin, and a queue that hides the callbacks he
> promised" to "four people can work it, and a promise made is a promise shown."
> It halts for you only where a human must genuinely act — §6 is that complete list.
>
> **Provenance:** written 2026-08-24, from live measurement of Postgres
> `rvadsozabmxkkrktwgnv`, the Shopify Admin API and the Make API, plus code **executed**
> in these repos (see §7.1). Revised the same day after an adversarial review that found
> four false statements in the first draft; each is now a landmine in §7.
> Authority, in order: `gt-factory-os-production-brain/CLAUDE.md` →
> `EXECUTION_POLICY.md` → `CURRENT_STATE.md` → each repo's own `CLAUDE.md`.
> Cited below, never copied.
>
> **Shelf life:** §2 is presumed wrong if pasted after 2026-09-07. Run §2.5 first.
> **Divergence protocol:** if §2.5 disagrees on counts, adapt and note it. If it shows
> follow-ups are **no longer starved** (§2.5 query `starved_followups` returns `f`),
> **halt and surface** — someone else moved and this document's ordering is wrong.

---

## 0. How to work

- **Who you are here:** a Claude Code session with write access to all three repos, admin
  on Supabase (project `rvadsozabmxkkrktwgnv`), Shopify, Make and GitHub. You may decide
  implementation freely. You may **not** decide anything in §1.1 or §6.
- **You hold two lanes at once.** `gt-factory-os-portal/CLAUDE.md` §Lane boundary says
  portal work must not author backend contracts or schema; S3 and S5 span portal +
  backend + migration deliberately. Split them into **one PR per repo**, cross-linked, so
  each repo's guards see a diff that respects its own lane. Say so in both PR bodies.
- **Open a portal tranche before touching portal source.**
  `gt-factory-os-portal/CLAUDE.md` §Invariants 1 and §⊥ do make this mandatory and a
  PreToolUse hook enforces it. `docs/portal-os/tranches/_active.txt` currently reads
  `172`. Open **173**, write its manifest listing every portal file you will touch, set
  `_active.txt`, and add it to `docs/portal-os/registry.md` **in the same commit** —
  `portal-pr-guard` fails the PR otherwise (§7.6).
- **Read first, in order:** `gt-factory-os-production-brain/CLAUDE.md` ·
  `EXECUTION_POLICY.md` §Window ownership and §Migration bracket ·
  `gt-factory-os/CLAUDE.md` · `gt-factory-os-portal/CLAUDE.md` ·
  `gt-factory-os-portal/docs/portal-os/tranches/164-queue-triage-and-cap.md` — the
  tranche that *specified* the defect you are fixing. Read it before you argue with §3.1.
- **Authority:** where this document and an authority doc disagree, the authority doc
  wins and this document is wrong.
- **Halt conditions, evidence standard, git discipline:** inherited from brain
  `CLAUDE.md` §Stop conditions and §Evidence. Deltas for this work only are in §8.
- **Workstreams here are `S1`–`S5`, not `W1`–`W5`.** `EXECUTION_POLICY.md` §Window
  ownership already binds `W1`–`W5` to different lanes (W1 = DB/migrations, W3 = sandbox
  UI and "⊥ ever canonical"). Using `W` numbers here would make your
  `AGENT_TEMPLATE.md` handoff declare the wrong lane.
- **Skills to run, and when.** Not optional decoration — each one closes a specific
  requirement below.

  | Skill | When | What it closes |
  |---|---|---|
  | `/caveman` + `/ponytail` | first message, before anything | Tom's standing modes. Ponytail matters here: S1 is a one-word change to an array and must stay one word — do not refactor the queue while you are in it |
  | `/portal-tranche-plan 173` | before touching any portal file | The portal invariant in §0. Produces the manifest, `_active.txt` and the `registry.md` entry that `portal-pr-guard` fails without (§7.6) |
  | `test-driven-development` | S1, before editing `queue.ts` | D1 **is** a red-green cycle. The three existing tests pass today and encode the wrong doctrine (§7.2); write the new assertion, watch it fail, then change the array |
  | `systematic-debugging` | any test that goes red you did not predict | §7.2 lists the three that should. A fourth means you broke something |
  | `verification-before-completion` | before every done-claim, and before each PR | §0's third prohibition, and the D1–D9 table |
  | `/code-review` | on each PR diff before leaving draft | Two repos, two lanes, three migrations |
  | `/ux-release-gate` | after S1+S2 land, before merge | The gate that produced this document. S1 changes what a rep sees first every morning |
  | `/close-session` | at the end | Unmerged PRs, live triggers, PR subscriptions, and stamping §D9 |

  Do **not** reach for `shopify-sync` — nothing here touches inventory. Do **not** reach
  for `brainstorming` — the design is settled in §1.1 and reopening it is out of scope.

- **The standard.** Tom's words: *"אני רוצה שתהיה מקצוען"*, *"מערכת באמת מקצועית וישימה
  לעבודה בפרודקשן"*. Three checkable prohibitions:
  1. **Nothing on screen may be false.** A count, date or status the UI shows must match
     what the database holds.
  2. **Nothing may be silently deferred** — and a commitment may not be deferred at all.
  3. **No done-claim without a run.** Not a type-check, not a code read. The command and
     its output. `200 OK` proves layer 1 only (brain `CLAUDE.md` §Evidence).
- **Language:** reason in English. Operator-facing strings in the `(sales)` route group
  are **Hebrew + `dir="rtl"`** (`gt-factory-os-portal/CLAUDE.md` §UI language, row
  `/apps + route group (sales)`, 2026-08-17). Write **commits, PR bodies and code
  comments in English**; the `AGENT_TEMPLATE.md` handoff keeps its English
  `VERDICT_GLOSSARY.md` tokens; the **chat summary to Tom is Hebrew**.

---

## 1. Mission and definition of done

**One testable sentence:** a callback the rep promised is the first thing they see on the
day they promised it, and three more people can each work their own queue without being
made system administrators.

Third column is **the observation that closes the condition** — run it, paste it.
A condition with no run is not met.

| # | Condition | The run that closes it |
|---|---|---|
| **D1** | A due follow-up is never suppressed by the daily cap | New assertion in `tests/unit/sales/today-queue.test.tsx`: 20 `new_lead` + 3 `due_follow_up`, cap 15 → the follow-up section renders 3 cards. **Write it first and watch it fail** (§7.2) |
| **D2** | Due follow-ups sort above new leads, most-overdue first | Insert ≥ 2 synthetic due rows via the portal (§6.E gives you the session), then run the handler's exact `ORDER BY` against `api_read.v_sales_today` and paste the rows. **Today this returns 0 rows and would pass vacuously** — a fixture is required, not optional |
| **D3** | "אבוד" is reversible from all three paths that set it | Exercise each path in a test and assert the undo action is present and restores prior status. A `setUndo` grep count proves nothing — there are already 4 occurrences, two of them teardowns |
| **D4** | An outcome is never recorded that the user did not choose | Drive the sheet: choose "לא ענה", then a custom date. Query the resulting `sales_core.lead_event` row — payload `result` must read `no_answer`, and `answered_progressing` must not appear |
| **D5** | A non-admin sales user can work a lead end to end | A session whose role is `sales_rep` loads `/sales/today`, records an outcome, and the resulting `lead_event` row exists. Backend paths are `/api/v1/queries/sales/today` and `/api/v1/mutations/sales/leads/:lead_id/outcome`; the portal BFF routes in front of them are `/api/sales/*`. 2xx alone does not close this |
| **D6** | There is exactly one roster | `sales_core.app_setting` has no `assignees` key **and** setting a user `status='inactive'` removes them from the next `GET /api/sales/settings` response |
| **D7** | A due callback reaches the person who owns it, outside the app | With two different assignees set on two due leads, two `reminder_sent` rows exist in `lead_event` carrying **two distinct recipients**. One row addressed to Tom proves nothing (§7.9) |
| **D8** | A phone-closed deal is recorded as won, and stays visible | A won-by-invoice lead has **both** a `converted` and a `status_change` event, and appears in `api_read.v_sales_today` as `item_type='conversion'`. Attempting it without an invoice number fails |
| **D9** | This document is stamped | Status line reads `SHIPPED` or `ABANDONED — <why>` with evidence pointers |

Anything not on this list is out of scope unless Tom asks.

### 1.1 Settled — do not reopen

| Decision | Who, when |
|---|---|
| Backlog worked by **mass personalised outreach first, then call only responders** | Tom, 2026-08-24 |
| That outreach is **blocked** on the product catalogue. Do not build a sender | Tom, 2026-08-24 |
| Won is proven by a **Green Invoice document number**. Free text rejected | Tom, 2026-08-24 |
| Multi-user via a **`sales` axis on the existing capability lattice** — not a fourth registry, not by widening `admin\|planner` | Tom, 2026-08-24 |
| `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` stays `false`. No message ever leaves the product to a lead or customer | brain `CLAUDE.md`; Sales-Machine `CLAUDE.md` §7 |
| `newest_first` inside the `new_lead` section is correct and stays | tranche 164 D3 |

---

## 2. Ground truth — measured 2026-08-24 ~17:40Z, re-verify at boot

### 2.1 What is built and live

Lead intake works end to end: a real lead landed at 16:15:43Z, mapped correctly, alerted
within 5 seconds. The Make webhook is **page-level** on page `1939072889681856` — all
forms, not per-form. `/ingest` is idempotent on `unique (source, external_id)`. A
`builtin:Break` retry handler (10 attempts × 10 min) was added to Make scenario `7075235`
at 16:50Z, so a transient `/ingest` failure no longer loses a lead.

The portal `(sales)` group has five screens with real machinery: `AssigneePicker`,
`bulk-assign`, `next-touch`, `OutcomeSheet`, `EventTimeline`. Tranches 162–172 built it.

### 2.2 The numbers

```
sales_core.lead          188 new · 0 working · 3 won   (191 total)
assignee set               0 of 188
next_touch_at set          1 of 188      ← the one commitment; §3.2
first_touch_at set         4
api_read.v_sales_today   151 rows        cap 15 → ~10 working days
uncontactable             39   no phone AND no email. Excluded from the queue,
                               but stay status='new' forever — no exit path
campaign_name empty      189 of 191      the CSV import carried no campaign/ad/city
org.shopify_customer_id   13 of 189 orgs

age of the backlog:  <7d 2 · 7-30d 22 · 2026-06-07→07-24 80 (all callable) ·
                     2-12mo 45 · >1yr 38 (0 callable — these ARE the uncontactable)

private_core.app_users, active: 7 rows — 2 admin, 2 planner, 2 operator, 1 viewer.
  One planner is the person Tom means when he says Alex; he is in the system and
  gets 403 on every sales endpoint. Erik and Avi are NOT present at all.
  One of the two admins is a demo account created 2026-08-24 — see §7.5.
  Regenerate the roster with §2.5 rather than reading names from here.

sales_core.app_setting:
  assignees   one entry                  ← the registry S3 deletes
  queue       { order: "newest_first", daily_cap: 15 }
  sla_hours   { hours: 24 }
```

### 2.3 What is NOT built

- No `sales` axis in `ROLE_CAPABILITY_LATTICE`
  (`gt-factory-os-portal/src/lib/auth/authorize.ts:32`). Axes are
  `stock | planning | admin`. The sales workspace bypassed the lattice and hardcoded
  `session.role !== 'admin'`.
- No `sales_rep` role anywhere. See §4/S3 for the eight places that must agree.
- Nothing reads `next_touch_at` outside the queue's `ORDER BY` and two views. The daily
  heartbeat (`cron.job` 28, `0 4 * * *` UTC) does not select due follow-ups.
- `reminder_sent` is **not** an allowed `lead_event.event_type` (§7.10).

### 2.4 Known-broken, adjacent, out of scope

These pre-date you. Do not fix them; do not let them read as your fault.

- 2 stuck bundles in Make `7075235` (`dlqCount: 2`), Tom's own test submissions. Retry
  cannot recover them — the stored body has `field_data: null` and no `data` key.
- 3 `ACTIVE` items unmapped to Shopify, one of which is a non-sellable placeholder.
- One test lead sits in the production queue; find it by
  `org.display_name like '%test lead%'`. Clear it via the portal's status control.
- The Make Facebook connection expires **2026-10-23T10:49Z**. Calendar reminder set for
  10-16. When it lapses, leads submitted in that window are lost permanently.

### 2.5 Re-verification block

```sql
-- regenerates every number §3 depends on, including the divergence trip-wire
select
  (select count(*) from sales_core.lead where status='new')                     as new_leads,
  (select count(*) from sales_core.lead where assignee is not null)             as assigned,
  (select count(*) from sales_core.lead where next_touch_at is not null)        as with_next_touch,
  (select count(*) from api_read.v_sales_today)                                 as queue_today,
  (select count(*) from api_read.v_sales_today
     where item_type='due_follow_up')                                           as due_now,
  (select count(*) from sales_core.lead
     where phone_e164 is null and email is null)                                as uncontactable,
  (select count(*) from sales_core.lead
     where coalesce(campaign_name,'')='')                                       as no_campaign,
  (select count(*) from sales_core.org where shopify_customer_id is not null)   as orgs_linked,
  (select value from sales_core.app_setting where key='queue')                  as queue_settings,
  (select count(*) from sales_core.app_setting where key='assignees')           as roster_key_exists,
  (select count(*) from private_core.app_users
     where status='active' and role='sales_rep')                                as sales_reps,
  -- the trip-wire: true while the defect stands
  (select count(*) from api_read.v_sales_today where item_type='new_lead')
     > (select (value->>'daily_cap')::int from sales_core.app_setting where key='queue')
                                                                                as starved_followups;
```

```bash
# These currently PASS and encode the wrong doctrine. Your first act in S1 is to add
# the D1 assertion that makes them red — the red half does not exist yet.
cd /home/user/gt-factory-os-portal && npx vitest run \
  "src/app/(sales)/_lib/queue.test.ts" tests/unit/sales/today-queue.test.tsx
# expected today: 2 files, 25 tests, all green
```

---

## 3. What the hard part actually is

**3.1 — The reorganizing fact. The queue does not have a bug; it has a wrong
requirement, and the requirement passed review.**

`CAPPED_SECTIONS = ['new_lead', 'due_follow_up']` share one budget, drained in render
order. Executed against the live shape (188 new leads, cap 15):

```
CAPPED_SECTIONS = [ 'new_lead', 'due_follow_up' ]
cards rendered  = { new_lead: 15, due_follow_up: 0 }
```

Tranche 164 **specified** this. Its prose reasons it out — *"conversions and returning
customers are never capped: they are news and the one case that must never go quiet, not
workload"* — and classifies `due_follow_up` as backlog. Its checklist ticks
`[x] The new-lead and follow-up sections cap at daily_cap`. A unit test asserts
`UI.dailyCommitment(0, 20)` for the starved section. A source comment at
`_lib/labels.ts:174-177` rationalises it: *"which is also why a later section can read 0
while an earlier one is full."*

Implementation, test, checklist and the author's own reasoning agree with each other and
are wrong together. **You cannot find this class of defect by reviewing an implementation
against its spec.** The one sentence to overturn: *a callback you promised is not
discretionary workload; it is a commitment already made, and it belongs on the
never-capped side with conversions and returning customers.*

The test comment records the origin: an earlier bug made a cap of 15 mean 15 + 15 = 30
calls; the release gate flagged it P1; the fix over-corrected from "two budgets" to "one
budget, and follow-ups lose."

**3.2 — Not hypothetical, and dated.** At 16:44Z on 2026-08-24 the rep called a lead, got
no answer, and scheduled a callback for 2026-08-25 06:00Z. That is the **only**
`next_touch_at` in the database. On the day it comes due it renders zero cards. It is
also invisible *today*: `v_sales_today` admits `new_lead` only when `first_touch_at IS
NULL`, and `due_follow_up` only when `next_touch_at <= now()`. A touched lead with a
future callback is in neither branch. The one lead ever worked here fell into a hole in
both windows.

**3.3 — "Assign leads to agents" is an identity problem, not a UI problem.** Three
registries must agree and nothing checks that they do: `private_core.app_users` (who logs
in), `requireSalesAccess` (admin only), `app_setting('assignees')` (one name). The fix is
to delete a registry, not add a screen.

**3.4 — The backlog and the live flow are two different problems.** 189 of 191 leads
carry no campaign, ad or city; live leads via Make carry all of it. Do not build one
scoring mechanism for both.

**3.5 — The unlinked leads are prospects, not missed matches.** 20 unlinked lead phones
checked against Shopify with a control proving the search indexes address phones: **0 of
20 matched.** `0330_sales_org_shopify_backfill.sql:46` gives the structural half — the
customer-setup convention deliberately keeps phone and email *off* the Shopify customer
record, so correctly-created B2B customers are exactly the ones matching cannot find. A
fourth matching layer would be wasted work.

---

## 4. Workstreams

Order matters. S1 is the smallest diff and the one that bites first.

### S1 — a commitment is never deferred *(portal + one backend sort)*

- Remove `'due_follow_up'` from `CAPPED_SECTIONS`,
  `gt-factory-os-portal/src/app/(sales)/_lib/queue.ts:22`.
- Move `due_follow_up` above `new_lead` in `SECTION_ORDER` — that constant lives in
  `_components/TodayQueue.tsx:22`, **not** in `queue.ts`.
- Make the server agree: `gt-factory-os/api/src/sales/queries_handler.ts:75-80`,
  the `ORDER BY CASE`.
- **Most-overdue first inside the follow-up section.** The handler applies one global
  direction from `app_setting('queue').order` (`queries_handler.ts:93-94`), locked to
  `newest_first` by §1.1. Add a section-scoped key **before** it:
  `case when item_type='due_follow_up' then next_touch_at end asc nulls last`. Do not
  change the global direction and do not sort client-side.
- Leave `dailyCapRule` alone. Its Hebrew string is *"מתוך מכסה יומית של N לכל התור"*,
  which stays true after this change. Only the English source comment above it is stale;
  correct that comment.

**Acceptance:** D1, D2.

### S2 — every destructive path is reversible; no outcome is invented *(portal)*

- `setUndo` when `result === 'lost'` in `submitOutcome` (`sales/today/page.tsx:127`).
  The working pattern is at **`today/page.tsx:259`**.
- The drawer path (`sales/leads/page.tsx:282`) has **no** undo state, no Toast action
  prop and no revert mutation. This is a build, not a copy — size it accordingly.
- `OutcomeSheet.tsx`: the root-step "שנה תאריך" reaches the date step with no outcome
  declared, and every date button submits `{...progressing}` where `progressing =
  { result: 'answered_progressing' }` (line 147). Restructure so the outcome is declared
  first and the date step is a disclosure under it. A no-answer with a custom date must
  write `no_answer`.

**Acceptance:** D3, D4.

### S3 — one roster, four people *(migration + backend + portal)*

**Eight surfaces must agree.** Four are commonly missed and D5 is unreachable without
them:

1. **Migration** (slot `0333`; see §7.11 for the FR1/FR2 bracket): extend
   `app_users_role_check` to include `sales_rep`. `DROP CONSTRAINT` + `ADD CONSTRAINT`.
   No `DROP COLUMN`.
2. `gt-factory-os/api/src/db/schema.ts:74` — `AppRole` union. **Without this
   `session.role` can never be `sales_rep`.**
3. `gt-factory-os/api/src/users/schemas.ts:10` and `:90` — the `z.enum` on user
   create/update. Without this nobody can be *assigned* the role.
4. `gt-factory-os-portal/src/lib/contracts/enums.ts:22` — `ROLES` / `Role`.
   `ROLE_CAPABILITY_LATTICE: Record<Role, …>` will not typecheck until this changes.
5. `gt-factory-os-portal/src/app/(admin)/admin/users/page.tsx:42` — a **second,
   duplicated** `ROLES` const. This is the only UI that assigns roles.
6. `gt-factory-os-portal/src/lib/auth/authorize.ts` — add `"sales"` to `CapabilityAxis`,
   `CapabilityGrants`, `ROLE_CAPABILITY_LATTICE`, `CapabilityRequirement`. Grants:
   `sales_rep` → `sales:"execute"`, all else `null`; `admin` → `"execute+override"`;
   `planner`/`operator`/`viewer` → `null`.
7. `gt-factory-os/api/src/sales/queries_handler.ts:14` and `mutations_handler.ts:26` —
   `requireSalesAccess` checks the capability, not `role === 'admin'`.
8. **`gt-factory-os-portal/src/app/(sales)/layout.tsx:40`** — `<RoleGate
   minimum="admin:execute">`. This is the gate that actually holds; its own comment says
   the middleware role table is a documented no-op until `app_users.role` is projected
   into the JWT. Change this one, or a `sales_rep` gets 2xx from the API and is still
   bounced off the screen.

Then: `handleSalesSettings` derives assignees from `private_core.app_users` where the
sales capability is granted and `status='active'`; remove the `assignees` key from
`sales_core.app_setting` and its settings-screen editor.

**On touching `private_core.app_users`:** brain `CLAUDE.md` §New modules bars module
agents from factory-os core schema. This is an **auth change, not a sales-module
change** — the sales module is a consumer of identity, not its owner. Proceed, and state
that reasoning in the migration header.

**Acceptance:** D5, D6.

### S4 — the promise reaches the person *(migration + Edge Function)*

A morning digest, per assignee, of callbacks due today.

- **A migration is required and is easy to miss.** `lead_event_event_type_check`
  (`0322:40-43`) permits 11 values and `reminder_sent` is not among them. Extend it in
  the same slot bracket as S3/S5 (§7.11).
- Reuse `supabase/functions/sales-leads-poll/_lib/email.ts` — same Resend path, same
  Hebrew register, same table-based HTML — and add `route: 'reminders'` beside `daily`.
- **"Due today" means the Jerusalem calendar day, not `<= now()`.** Next touches default
  to 09:00 Israel (`sales_core.next_business_touch`, `0324:22-40`). A 06:00 run using
  `v_sales_today`'s `<= now()` predicate returns an empty digest every morning — including
  the §3.2 callback this whole document is about. Query a day range.
- **`pg_cron` runs in UTC.** Israel is UTC+3; 06:00 Israel is `0 3 * * *`.
- **Recipient.** `sendViaResend` (`index.ts:208-212`) hard-refuses any address that is not
  `ALERT_RECIPIENT`, and the module header says there is deliberately no code path that
  could address anyone but Tom. That guard exists to make it impossible to mail a lead.
  **You are authorised to widen it from a single constant to an allowlist *set* built
  from `private_core.app_users` — staff addresses only — and you must keep the check.**
  Deleting the check, or sourcing a recipient from a `lead` row, violates brain Stop
  condition 1. `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` is untouched and stays `false`.
- Write one `lead_event` per send. `sales_core.lead_event` is **append-only** (triggers
  `lead_event_no_update` / `lead_event_no_delete`, migration `0320`), so same-day
  de-duplication must be a `NOT EXISTS` pre-check, never a marker updated after sending.

**Acceptance:** D7.

### S5 — a phone close is a real close *(migration + backend + portal)*

**Read this before designing.** `sales_core.convert_lead` already exists
(`0328:99-160`) and its `COMMENT ON FUNCTION` reads *"Sole writer of
lead.status='won' (D4/D12)"*. It writes **both** a `converted` event and a
`status_change` event, deliberately — `api_read.v_sales_today`'s `conversion` branch keys
off the `converted` event (`0326:207-210`), so a lead marked won without one has
`status='won'`, matches no WHERE branch, and **disappears from the queue entirely**.

Therefore: **extend `convert_lead` with an evidence-kind parameter** (it already writes
`'evidence','shopify_order'` into its payload — add a Green-Invoice kind beside it).
Do not make `set_lead_status` a second writer of `won`.

Two further traps:
- `set_lead_status`'s 4-argument form was explicitly `drop function`'d by `0324` so the
  default-argument call form stays unambiguous (`0324:53-55`). If you add a defaulted
  parameter to any of these functions, drop the old signature in the same migration and
  re-issue its `grant execute` (`0324:195` grants the exact 5-arg signature;
  `mutations_handler.ts:66-71` calls it with all five named).
- Do **not** call the Green Invoice API to validate the number here. Storing it is
  enough; verification is a later decision.

Surface it in `OutcomeSheet` as a fourth outcome requiring an invoice number.

**Acceptance:** D8.

---

## 5. Scope

**IN:** everything in §4.

**OUT — do not touch, do not "improve":**

- The mass-outreach send. §1.1 blocks it on the catalogue. You may not build a sender.
- Every frozen flag in `gt-factory-os/CLAUDE.md` §Frozen, and
  `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED`. Widening the *internal staff* allowlist in S4
  is explicitly authorised there and is not a flag change.
- Shopify matching. §3.5 closed it.
- Make scenario `7075235`. Changed today and working — leave it.
- The 3 unmapped items and the placeholder (§2.4).
- `stock_ledger`, `current_balances`, `balance_anchors`, projections. Nothing here
  touches stock.
- The 18 copy findings and the visual/a11y findings — a later tranche. Report link in §9.

---

## 6. Tom's part — the complete list, nothing else is his

**A. Erik's and Avi's email addresses.** Not in `app_users`; you cannot invent them. Ask
once, in Hebrew, and continue the rest of S3 while waiting — the migration and the
lattice do not depend on the addresses.

**B. One decision: does the existing planner become `sales_rep`, or does `planner` gain
`sales:execute`?** Making `planner` a sales role also hands the workspace to the
accounting planner, which nobody asked for. Recommend `sales_rep`, say why, let Tom
decide.

**C. Deactivate the demo admin account** (§7.5) once the demo is no longer needed. Live
`admin`, created 2026-08-24. You may not decide when the demo is finished.

**D. The 39 leads with no phone and no email** (§2.2 — the count is 39, and one of them
is not in the >1yr cohort) have no exit path and never will. Tom decides: bulk-mark
`lost` with a reason, or leave them.

**E. Create the Supabase `auth.users` row for each new sales user.** `private_core.app_users`
requires a matching `auth.users` row and `0331:23-25` states it plainly: creating one
needs the service key, so it is done by hand in Supabase Studio, and the migration raises
if it is absent. §7.3 forbids writes through the MCP. **D5 cannot close without this.**
Tell Tom exactly which emails need a Studio user, and verify by observing the row appear
— never by handling the service key.

Everything not listed here is yours.

---

## 7. Landmines — do not rediscover these

1. **The Bash tool keeps its working directory between calls.** A `cd` into one repo
   persists; a later relative `ls` silently searches the wrong repo. This produced a
   confident, wrong finding while this document was being written — "the portal has no
   E2E tests" — when it has 43 files and `@playwright/test ^1.59.1`. **Always use
   absolute paths, or `cd` in the same command.**
2. **S1 turns three tests red, not one.** All three are the old doctrine, none is your
   regression:
   - `tests/unit/sales/today-queue.test.tsx:266` "spends one daily budget…" — asserts
     `UI.dailyCommitment(0, 20)` on the starved section.
   - `tests/unit/sales/today-queue.test.tsx:72` "keeps the sections in the order the work
     should be done" — hard-asserts the old section order.
   - `src/app/(sales)/_lib/queue.test.ts:60` "treats a cap of zero as a cap" — builds its
     rows entirely from `due_follow_up`; `visible` flips 0→3.
   **Rewrite all three, delete none.** The first one guards the original 15+15=30 bug;
   losing it re-opens that. `tests/e2e/sales-queue-triage.spec.ts` uses only `new_lead`
   fixtures and survives.
3. **The Supabase MCP `execute_sql` runs read-only.** `SELECT FOR UPDATE`, `TRUNCATE` and
   every write fail with `25006` — including `set_lead_status` and `rebuild_verifier()`.
   Use `apply_migration` for DDL only; make data changes through the product's own API.
4. **You cannot run the DB-backed suites here.** `DATABASE_URL` is unset;
   `DATABASE_URL_POOLED` is set but does not connect (psql times out); **`pg_prove` is
   not installed**. Plan pgTAP as a deliverable to be run in CI or by Tom, and say
   plainly which suites you could not execute. The DB-free sales tests **do** run —
   57/57 across `sales_leads_make_intake`, `sales_leads_poll_mapping`,
   `sales_leads_poll_alerts`, `sales_leads_token_diag`.
5. **One of the two active admins is a demo account created 2026-08-24.** Every other
   test account is `inactive`. It will appear in any roster S3 builds. Do not silently
   deactivate it — §6.C.
6. **CI is asymmetric between the two repos, and the portal is the strict one.**
   `gt-factory-os`: only `typecheck` runs on `pull_request`; `phase10-node-tests` is
   `workflow_dispatch` and its file list contains no `sales_*` test.
   **`gt-factory-os-portal`: `portal-pr-guard.yml` runs on `pull_request` and executes
   `eslint .` → `tsc --noEmit` → `vitest run` (the whole unit suite) → `playwright
   --grep @mocked` → a registry-presence check that fails the PR if a new
   `docs/portal-os/**` file is missing from `registry.md`.** S1 breaks that vitest suite
   by design (§7.2) — land the rewritten tests in the same commit.
7. **Playwright needs an explicit browser path.** This image ships Chromium 1194;
   Playwright 1.59.1 expects 1217. Use `PW_CHROME_PATH=/opt/pw-browsers/chromium`
   (precedent: portal PR #212). "Browser missing" is the wrong diagnosis.
8. **A lead can be invisible in both queue windows** — see §3.2. Check this when S1 looks
   done and a lead you expected is still absent.
9. **`assignee` is null on all 188 leads.** Any S4 test that relies on the Tom fallback
   proves nothing, because the fallback and the old hardcoded constant produce identical
   rows. D7 requires two *distinct* recipients.
10. **`reminder_sent` is not an allowed `lead_event.event_type`.** The insert fails on
    `lead_event_event_type_check` (`0322:40-43`). S4 needs its own migration.
11. **The migration bracket is timed.** `EXECUTION_POLICY.md:80`: the write must complete
    **≤ 60s after FR1**; over 60s → abort, discard, restart from a fresh FR1. You have
    three migrations to write (S3, S4, S5) — do each as its own tight
    list → write → re-list cycle, never batched. Next free slot is **0333** (0330 is
    already doubled by two unrelated files; highest is 0332).

---

## 8. Halt conditions

Inherited set cited in §0. Additions specific to this work:

- A change would make a lead **less** visible than today → **STOP**. S1 is the opposite
  direction.
- Your claimed migration slot appears under another name when you re-list → **STOP**,
  `contract_failure`, do not renumber silently.
- S5 tempts you to make `set_lead_status` a second writer of `won`, or to drop the
  `converted` event → **STOP**. Both break `v_sales_today` (see S5).
- S4 tempts you to remove the `sendViaResend` recipient check rather than widen it to a
  staff allowlist → **STOP**. That guard is why no message can reach a lead.
- §2.5 shows `starved_followups = f` → **STOP and surface**. Someone else moved.
- Any work would touch `stock_ledger` or a projection → **STOP**.

---

## 9. Final report

Follow `gt-factory-os-production-brain/AGENT_TEMPLATE.md` §Output format, tokens per
`VERDICT_GLOSSARY.md` (English). Beyond that shape, state:

1. What a stranger can now watch working, end to end — name the screen and the click.
2. Each of D1–D9 ✅/❌ with its evidence pointer. No partial credit.
3. §2.5 re-run, beside the §2.2 values.
4. Which suites ran and which could not, and why (§7.4, §7.6).
5. What is still Tom's from §6, and what is genuinely unfinished.
6. The single next action.

Then stamp this file's status line — that is D9, and it is the last thing you do.
Summarise to Tom in Hebrew.

**Audit that produced this document:**
https://claude.ai/code/artifact/8a720deb-bd36-4966-8cd7-49d80609d036

If anything is not ready, say so first and plainly.
