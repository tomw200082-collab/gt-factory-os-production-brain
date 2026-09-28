# MASTERPROMPT — A lead who writes to GT's lead line gets the right menu, three clear choices and a personal ordering link; a lead who spoke with sales is woken up before every follow-up; and gteveryday.com goes live with it. Built, proven on Tom's phone, and one written go from switching on

**STATUS: LIVE — not yet executed**
<!-- The executing session's last act is to change this line to SHIPPED / SUPERSEDED by <path> /
ABANDONED — why, with evidence pointers (merged PRs, the migration, wa_event_log ids, the draft id,
the live theme check, the soak start time, the report). -->

> **Usage:** paste this entire file as the first message of a fresh Claude Code session. Attach
> `gt-factory-os`, `gt-factory-os-production-brain`, `gt-factory-os-portal`, `Sales-Machine` and
> `gt-site`. Before pasting, allow the Canva connector for the whole session (§6-A). The sources it
> cites are on `main` once brain #239 and gt-factory-os #319 and #320 are merged; §2.5 checks that.
>
> **What it does:** takes the WhatsApp lead journey from "decided and documented" to:
> - built and deployed;
> - proven end to end on Tom's phone;
> - running as a dry run for every other lead;
> - live on gteveryday.com.
>
> It stops at the one step Sales-Machine D-005 reserves for Tom: the written go to send to real
> leads, after a 24-hour soak (Sales-Machine `D-005`). §4-W11 says what happens when he gives it.
>
> **Tom's standing authorization for this run.** Pasting this file gives it, and only this:
> - push `gt-site` `main` to the live theme `166730072305` once every W8 gate is green;
> - apply this work's migration to production, then merge its API code (Railway deploys on merge),
>   under the gates of `gt-factory-os` `CLAUDE.md` §Migrations;
> - submit the five WhatsApp templates of W6 with the texts he approves at checkpoint C1.
>
> It does **not** authorize any of these:
> - opening the outreach gate (`SALES_CUSTOMER_OUTREACH_WRITE_ENABLED`);
> - sending to any phone outside the test allowlist;
> - completing a lead's draft order.
>
> **Provenance:** written 2026-09-28 by the session that designed the journey with Tom. Sources:
> - live reads the same day of Supabase `rvadsozabmxkkrktwgnv` (queries in §2.5) and of the API's
>   public health route;
> - the five repos, read at their `main` heads;
> - Meta's WhatsApp documentation, read at source (Sales-Machine
>   `evidence/2026-09-28-follow-up-cadence-research.md`);
> - an independent red-team read of this document against the code, the same day, whose findings
>   are folded in;
> - Tom's messages of 2026-09-28, quoted in §1.1.
>
> **Authority, highest first**, cited below and never copied:
> 1. brain `CLAUDE.md`;
> 2. brain `EXECUTION_POLICY.md`;
> 3. each repo's `CLAUDE.md`;
> 4. Sales-Machine `doctrine/decisions.md`;
> 5. Sales-Machine `doctrine/playbooks/whatsapp-lead-journey.md` (*the playbook*);
> 6. `gt-factory-os` `docs/superpowers/specs/2026-09-28-lead-journey-design.md` (*the spec*);
> 7. this document.
>
> Where this document and a higher one disagree, the higher one wins and this one is wrong.
>
> **Shelf life:** §2 is presumed wrong if you paste this after 2026-10-12. Run §2.5 first either way.
> - When reality differs from §2 in a way that removes work (for example, the lead line already
>   delivers), **adapt**.
> - When it changes the basis of a §1.1 decision (for example, completed orders are no longer
>   invoiced automatically, or a decision was amended), **halt and surface**.

## 0. How to work

- **Who you are here:** one long Claude Code session, run end to end. You have:
  - the five repos, on the branch your session instructions name;
  - the Supabase, Shopify, GitHub and Canva connectors.

  **You do not have:**
  - the WhatsApp provider's dashboard (Dualhook);
  - Meta's WhatsApp Manager;
  - Supabase function secrets;
  - Tom's phone.

  Railway variables are set through a `workflow_dispatch` workflow on the pattern of `gt-factory-os`
  `.github/workflows/railway-gi-env.yml`, which pipes each value to `railway variable set --stdin`
  and never prints it. You decide implementation details inside the spec alone.
- **Read first, in order:**
  1. brain `CLAUDE.md`;
  2. `gt-factory-os` `CLAUDE.md`;
  3. Sales-Machine `CLAUDE.md`;
  4. the playbook;
  5. the spec, all of it, including §3.5a and §4;
  6. Sales-Machine `evidence/2026-09-28-lead-journey-ground-truth.md`;
  7. brain `docs/plans/2026-09-28-lead-reply-menus-masterprompt.md` (you run it as W7);
  8. brain `docs/plans/2026-09-27-brand-site-lead-modal-masterprompt.md` §1.1, D6, D8, D10 and W7
     (you finish it in W8).
- **Inherited rules.** Halt conditions, evidence standard, lanes, migrations and git discipline come
  from:
  - brain `CLAUDE.md` §Stop conditions, §Evidence and §Handoff;
  - brain `EXECUTION_POLICY.md`;
  - `gt-factory-os` `CLAUDE.md` §Migrations and §⊥ do.

  §8 lists only the additions specific to this work.
- **Watching:** brain `CLAUDE.md` §Watching binds you. After every `create_pull_request`, call
  `unsubscribe_pr_activity` at once. Schedule no check-in and create no Routine.
- **The standard.** Tom: `אנחנו לא מתפשרים על כלום ואני רוצה שהביצוע הזה יהיה מושלם מהרגע הראשון`.
  In checkable terms:
  - no automated message reaches a real lead before Tom's written go;
  - no lead's order is completed or invoiced by the system;
  - no customer-facing Hebrew text differs by a byte from the text Tom approved;
  - nothing on the live site is dead or false.
- **How to build:**
  - Write the test first for each component (`test-driven-development`), and prove it before
    claiming it (`verification-before-completion`).
  - **Tests never touch production.** In this container **both** `DATABASE_URL` and
    `DATABASE_URL_POOLED` point at the production project. 25 of the 135 files in
    `gt-factory-os/api/test` never load the production guard, and some write `stock_ledger`.
    Before **every** test command:
    1. Point both variables at a throwaway database, loaded with the migration chain, on this
       container's local Postgres 16 server.
    2. Check that neither variable contains `rvadsozabmxkkrktwgnv`. If one does, do not run.

    The rest of the rule:
    - Never set `TEST_ALLOW_PRODUCTION_DB`.
    - Never run the repo's `pg_prove -d "$DATABASE_URL"` line here.
    - pgTAP is not installed. Install it locally, or report the pgTAP tests as not run. Never report
      them as passed (spec §4).
  - One subagent may work on Canva while you work elsewhere. **Never two Canva actors at once.**
- **Language.** This document is in English; Hebrew literals stay in their script, in backticks.
  **Output language: Hebrew to Tom** — short, direct, no recap, and every message ends with at most
  one action for him (his standing preference). English for code, commits, PR bodies and repo docs.
- **First action:** run §2.5, then read the files above, then W0.

## 1. Mission and definition of done

**One testable sentence:** a lead who writes to `054-758-8132` gets the journey of Sales-Machine D-027
to D-032 exactly as the playbook specifies. It is proven on Tom's phone and runs dry for everyone
else. gteveryday.com is live with it, and the only step left is Tom's written go after a 24-hour
soak.

| # | Condition | The observation that would prove it false |
|---|---|---|
| D1 | The lead line delivers | `select count(*) from order_intake.wa_event_log where raw_payload->>'phone_number_id' = '217553368116155'` returns 0, or has no row from the test phone |
| D2 | Every automated text is the one Tom approved | Sales-Machine `U-051` still open; or the test that parses the playbook **at the pinned commit of Tom's approval** and compares it with every send body and template body finds a difference |
| D3 | First messages are right, for all five menus and for no menu | a dry-run body (or the real one on the test phone) with the wrong PDF, a missing footer, other than three buttons; or a general reply sent twice to one phone within 30 days, or after a staff message to it within 24 h on either line (`D-030`) |
| D4 | Every button and the text `הסר` route as the playbook §4–§5 say | a tap whose `lead_event` row is missing or wrong, or `לא כרגע` not setting `lost` and `opt_out_at` |
| D5 | A lead's order is a draft and nothing more | 60 s after the test order the Shopify draft (tag `lead`) is not `OPEN`, or its `order` is not null, or a Shopify order tagged `lead` exists; or the test that fails when `draftOrderComplete` is reachable from the lead path, **including the stale-replay path** (`orders.ts:141-153`), is missing or red |
| D6 | The order confirmation arrives, both ways | no free-form confirmation on the test phone after the test order; or no `delivered` status on the test phone for the utility template, sent through the forced template path |
| D7 | The wake-up sequence obeys every rule | a scheduler test missing for any rule of playbook §5, eligibility included; a message to a lead that never received the D-024 notice; or on the test phone, no `delivered` status for each of the four marketing templates through the forced template path, or a send after a reply or `הסר` |
| D8 | The gate holds | `select count(*) from order_intake.wa_event_log where direction = 'outbound' and raw_payload->>'phone_number_id' = '217553368116155' and coalesce(status,'') not like 'dry_run:%' and wa_phone <> all (<the phones in sales_core.app_setting lead_journey_test_phones>)` returns more than 0 while `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` is false |
| D9 | Echoes are keyed by number | the order bot defers a phone only because of a lead-line echo (test) |
| D10 | Menus are built, checked, hosted and approved | any copy fails the menus masterprompt's D1–D9; `app_setting` `lead_menus` lacks a Shopify CDN URL that returns 200 with a PDF for a menu; or Tom did not approve the menus at C2 |
| D11 | The site is live, with the grown FAQ | `python3 tools/theme_ship.py check 166730072305` reports drift; the FAQ lacks the questions Tom approved; a W8 gate was skipped; or the site masterprompt's D6, D8 and D10 are unmet |
| D12 | Ready, soaking, stamped and reported | the gate is not false; no recorded soak start; the test lead of W9 not closed; this document, the site and the menus masterprompts not stamped; or no Hebrew report reached Tom |

Anything not on this list is out of scope unless Tom asks.

### 1.1 Settled — do not reopen

Tom decided all of this on 2026-09-28, in writing. The record is Sales-Machine `doctrine/decisions.md`.
- **No bot** (D-027): `אין בוט, יש רק הודעות אוטומטיות. תבטל אותו לחלוטין.`
  - Only automated messages, each fired by one event.
  - Free text gets no automated answer.
  - Nothing runs on Airtable, Make logic or OpenAI.
- **Three buttons and their paths** (D-028). The labels are `אני רוצה להזמין`, `רוצה לשמוע עוד` and
  `תודה, לא כרגע`, in that order.
- **A lead's order is a Shopify draft the system never completes** (D-029).
- **The general reply** (D-030): once per phone in 30 days, never within 24 h of a staff message.
- **The wake-up sequence** (D-031, playbook §5):
  - eligibility needs the delivered D-024 notice;
  - at most four messages per lead, each ahead of a human follow-up;
  - the stop rules read both lines;
  - the time slots, holidays from `private_core.holidays_il` and the 48 h spacing (`D-031`);
  - `פרסומת`, the salesperson's signature and a free way to stop.
- **Site and campaign leads are one journey** (D-032).
- **The menus** (D-025, D-026): one menu per reply, at most eight drinks, FOOD COST stays.
- **What the system never states** (D-018, D-012): a food cost or the opening menu's price is never
  stated; every price is ex-VAT and says so.
- **The legal lines** (D-024): the notice line in every first message, and the `§30א` lines in every
  wake-up message.
- **Parked:** the AI module for Instagram Direct and Messenger (U-054).
- **The site:**
  - the landing pages are set aside;
  - the fifth line reads `בניית תפריט משקאות עשיר ורווחי לעסק`;
  - there are no prices anywhere on it (Tom 2026-09-24, `gt-site` `tools/strip_prices.py`);
  - the rest of the site masterprompt's §1.1 stands.

## 2. Ground truth — measured 2026-09-28; re-verify at boot

### 2.1 What is built and live
- **The order line works end to end** through the provider:
  - inbound, logged in `order_intake.wa_event_log`;
  - outbound: the portal sent links on 2026-09-26 and 2026-09-28.
- **Nothing logs a send.** `wa_event_log` held zero outbound rows on 2026-09-28. Statuses reach the
  worker without `phone_number_id` or error codes, and the worker ignores them (spec §2). Until W3
  lands, a leak past the gate would be invisible.
- **Health route.** `GET https://gt-factory-os-api-production.up.railway.app/webhooks/wa-order-bot/health`
  returned `{"intake_enabled":true,"auto_commit_enabled":false,"inbound_auth":"waba-id","missing_secrets":[]}`
  on 2026-09-28. Its `missing_secrets` ignores the lead-capture variables (`config.ts:88-101`).
- **The ordering portal is live.** Flag `customer_portal_live` is on, allowlist `*`, since 2026-09-25.
  Every portal order is **completed** today, including on the stale-replay path (spec §2).
- **The CRM.** `sales_core` records outcomes, including `answered_progressing` with a
  `next_touch_at`.
- **Holidays.** `private_core.holidays_il` exists. It marks Sukkot through 2026-10-03, so no real-clock
  send can happen that week.
- **The site.** `gt-site` `main` is `6b067e8` (#29). It was verified on preview `186698334449` with
  drift 0 on 2026-09-28. The live theme `166730072305` does not have it yet: the push was refused by
  Claude Code's permission layer that day.
- **Deploys.** Railway deploys the API on every merge to `main` (brain
  `docs/plans/2026-07-24-production-picking-rollout.md`, Phase 3).
- **This container (2026-09-28):**
  - `DATABASE_URL` and `DATABASE_URL_POOLED` both point at production;
  - a Postgres 16 server is installed locally;
  - pgTAP and `pg_prove` are not.
- **Statuses.** Every status after a message's first is dropped today: they are de-duplicated on
  the message id alone (spec §3.5a).
- **Phone formats differ.** `wa_event_log.wa_phone` is `972…`, while `sales_core.lead.phone_e164`
  is `+972…` (spec §3.8).

### 2.2 The numbers (2026-09-28, about 15:00 UTC)
- `wa_event_log`, last 30 days:
  - order line `185509261301816`: 6,441 events, of them 3,488 messages;
  - lead line `217553368116155`: **0, ever**.
- `sales_core.lead` by status: new 145, lost 61, working 30, won 5.
- The six leads marked `answered_progressing` came from `facebook` (5) and `import_meta_export` (1).
  None came from the lead line, and none received the notice. **They must never be messaged.**
- In the 60 days to 2026-09-28, 6 lead phones got staff echoes and 7 wrote in, all on the order
  line.
- Reply-button taps received ever: 17, the last on 2026-07-12.
- Highest migration: `0359_planning_demand_open_orders_only.sql`.

### 2.3 What is NOT built
- Every component of spec §3.
- The five WhatsApp templates.
- `app_setting` `lead_menus` and `lead_journey_test_phones`, and the opt-out column and event.
- The grown FAQ.
- The finished menus. Their Canva state is only partly edited and partly unknown; see the menus
  masterprompt §2.2.

### 2.4 Known-broken, adjacent, out of scope
- **Fixed here:**
  - echoes keyed by chat phone only (`worker.ts:128-148`, spec §3.9);
  - lead capture sending neither the text nor the menu (`lead_capture.ts:67-94`);
  - `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` read by no code;
  - no send log, and statuses without error codes (spec §3.5a).
- **Not this work:**
  - the CRM's manual WhatsApp templates signed with Tom's name (Sales-Machine U-026);
  - email alerts from `sales-leads-poll` (Sales-Machine U-033-a).

### 2.5 Re-verification block
```sql
-- 2026-09-28: events per receiving number, last 30 days (lead line = 217553368116155)
select raw_payload->>'phone_number_id' as pnid, count(*) as events,
       count(*) filter (where type='message') as msgs, max(created_at) as last_event
from order_intake.wa_event_log where created_at > now() - interval '30 days' group by 1 order by 2 desc;
-- 2026-09-28: outbound rows (0 that day), flags, CRM shape, the six ineligible leads
select count(*) from order_intake.wa_event_log where direction = 'outbound';
select flag_key, enabled, value, updated_at from private_core.feature_flags where flag_key = 'customer_portal_live';
select status, count(*) from sales_core.lead group by 1 order by 2 desc;
select l.source, count(*) from sales_core.lead l where exists (select 1 from sales_core.lead_event e
  where e.lead_id = l.id and e.event_type = 'outcome' and e.payload->>'result' = 'answered_progressing') group by 1;
select holiday_date, holiday_name from private_core.holidays_il
  where holiday_date between current_date and current_date + 21 and archived_at is null order by 1;
```
```bash
# 2026-09-28: health, heads, migrations, live theme
curl -sS https://gt-factory-os-api-production.up.railway.app/webhooks/wa-order-bot/health
for r in gt-factory-os gt-factory-os-production-brain gt-factory-os-portal Sales-Machine gt-site; do git -C $r log --oneline -1 origin/main; done
ls gt-factory-os/db/migrations | tail -3
git -C gt-factory-os show origin/main:docs/superpowers/specs/2026-09-28-lead-journey-design.md | grep -c "3.5a Send log"   # 0 = HALT: the spec on main is stale
for v in DATABASE_URL DATABASE_URL_POOLED; do printf '%s ' $v; printf %s "${!v}" | grep -q rvadsozabmxkkrktwgnv && echo production || echo other; done
(cd gt-site && python3 tools/theme_ship.py check 166730072305)
```

## 3. What the hard part actually is

1. **It looks like a messaging feature. It is a pipe that has never carried water.** The lead line
   has never delivered one event to GT (§2.2). Prove delivery first (W2). Build the rest in parallel
   against tests, and claim no end-to-end result until D1 holds.
2. **It looks like ordering. It is an invoicing trap.** Every completed Shopify order is invoiced by
   Green Invoice within seconds and opens a LionWheel task. The portal completes every order today,
   including when it replays a stale submission. The lead path must stop at the draft on every
   route, and a test must prove it.
3. **It looks like a scheduler. It is a set of stop rules and one eligibility rule.** Two bugs are
   expensive:
   - a nudge to someone who ordered, replied on either line or said stop;
   - a nudge to one of the six leads who never got the notice.

   Write those tests before the send code.
4. **It looks like copy. It is Tom's voice, the law and Meta at once.**
   - Every text is his, verbatim.
   - D-018 and `§30א` bind.
   - The site shows no prices.
   - A Meta template cannot be edited after approval without another review.

   So nothing is submitted before C1.
5. **It looks like proof. Most of it would be invisible.** Today no send is logged and no error code
   survives. Until the send log (spec §3.5a) exists, D7 and D8 cannot be observed at all. Build it
   first in W3.
6. **It looks like one build. It is five repos that ship in an order.**
   - The order: backend (migration first, then merge) → portal lead mode → templates → menus →
     site (FAQ, live push).
   - Only two stops: C1 and C2.

## 4. Workstreams, in order

### W0 — Boot and baseline
- Run §2.5 and record the output.
- Establish the test baseline on `gt-factory-os` `main`. First point both database variables at
  the throwaway database (§0). Record every pre-existing failure, so it is not later mistaken for
  yours:
  - `npm run typecheck`;
  - the `test:order-intake` and `test:portal` suites;
  - `cd api && npm test`;
  - pgTAP.
- Draft, for C1:
  - the portal lead-mode strings: reuse approved rows of the UX gate §5 register wherever one fits;
    the registration form already carries business name, city and contact name;
  - the grown FAQ list, from `מאושר` rows of Sales-Machine `knowledge/answers/answer-bank.yaml`
    only, never a D-018 row, each through `stop-slop`. Three approved answers contain a `₪` price,
    and the site shows no prices: drop them, or propose a price-free wording for Tom to approve at
    C1. Never reword an approved answer without his approval.

### W1 — Checkpoint C1 with Tom: the only stop at the start
Send Tom **one** Hebrew message that asks for everything at once:
1. Approve the playbook texts (§2–§5) or rewrite them, the portal strings and the FAQ.
2. Send, from his phone, the text `בדיקת מסע GT` to `054-758-8132` now.
3. Write, in the same reply, the last four digits of that phone.
4. Optionally, name a real customer who agreed to be the example in wake-up message 3.

Then record his answers:
- **Approvals.** Write any rewrite he gives into the playbook first. Then close U-051 in
  Sales-Machine, quoting him, and note the playbook commit his approval covers (D2 pins it). Add UX
  gate §5 rows for new portal strings and §5.5 rows for the FAQ.
- **His test text arrives before W3 deploys**, so it produces no reply and no reply row. His later
  `היי, אני מעוניין במאצ׳ה` is therefore still a first message (spec §3.3).
- **Test phone.** Identify it as the sender of `בדיקת מסע GT` whose number ends in his four digits.
  Write it into `sales_core.app_setting` `lead_journey_test_phones` only after W3's migration has
  created the key. It never goes into a repo, a document, a commit or a log line.

Then keep working to C2.

**Acceptance:** D2, and D1's first half.

### W2 — The lead line delivers (spec §3.1; Sales-Machine U-050)
- Find `בדיקת מסע GT` in `wa_event_log`. If it is there, D1's first half holds.
- If it is not:
  - diagnose: the provider's webhook for that number, or coexistence lapsed (Sales-Machine D-023);
  - give Tom the exact steps (§6-B), and keep working on W3–W7 against tests meanwhile.
- Add lead-capture booleans (configured, enabled; never values) to the health route.
- Make sure production carries the four lead-capture variables (spec §3.1), through the workflow
  pattern of §0.
- **`LEAD_INGEST_TOKEN` is never rotated.** Make posts every live Facebook lead with it. If Railway
  lacks it, copying it is Tom's (§6-C).

### W3 — Backend (spec §3.2, 3.3, 3.5, 3.5a, 3.6, 3.9, 3.10)
- **Build the send log and the status fields first** (spec §3.5a). Every later proof depends on them:
  - the send row is written before the send, with `phone_number_id`, `kind` and `dry_run` at the
    top level;
  - statuses are de-duplicated on message id plus status;
  - tests: `sent` → `delivered` → `failed` on one message, and D8's query returning 1 on a planted
    leak.
- **Migration.** List `db/migrations/` immediately before writing the file and again after. It
  carries:
  - the opt-out column and the new event types;
  - the unique send index;
  - `lost_reasons` + `לא כרגע`;
  - `lead_menus`, and `lead_journey_test_phones` seeded empty **with `on conflict do nothing`**.

  Add its pgTAP test and run it on the throwaway database.
- **Code:**
  - the lead-line port and its message kinds;
  - menu recognition, and the general reply's 30-day and 24-hour rules (`D-030`);
  - button routing;
  - the gate, the dry run and the allowlist;
  - echo keying;
  - lead capture carrying the text and the menu;
  - the health booleans.
- **Where the gate check lives:** inside the lead-line port's send, not in its callers.
- **Ship, in this order**, because Railway deploys on merge:
  1. Open the PR; CI goes green.
  2. Pre-flight: `rebuild_verifier() = 0`.
  3. Announce one line, then apply the migration to production with the Supabase connector's
     `apply_migration`.
  4. Merge.
  5. Check the health route and `rebuild_verifier() = 0` again.

**Acceptance:** D3, D4, D8, D9 (their unit halves).

### W4 — Ordering from a lead link (spec §3.7)
- Build the lead token and the page.
- Submission is **draft only**, tags `lead` and `pk-<idem>`. Write the test that fails if
  `draftOrderComplete` is reachable from the lead path, the stale-replay path included.
- Then the confirmation (free-form inside the window, else the utility template), the draft-order
  event and the owner alert. For allowlisted phones, a switch forces the template path (spec §3.7).
- **Copy:** add every new file to `api/scripts/portal_copy_check.mjs`'s lists, then run it and its
  `--self-test`.
- **Ship** as in W3.

**Acceptance:** D5, D6 (unit halves).

### W5 — The wake-up scheduler (spec §3.8)
- A pg_cron job every 15 minutes, calling a Railway route on the `stock_exceptions_sweep` pattern.
- Put every rule of playbook §5 under an injected clock before the send code exists:
  - eligibility; include a test that the six leads of §2.2 are never picked;
  - each stop rule, on both lines;
  - the 48 h spacing, the slots, Friday–Saturday, and a date in `holidays_il`;
  - the error codes `131049` and `131050`, read from statuses.
- Join the CRM and the event log through one phone normalizer (spec §3.8). Build the stop-rule test
  data with both real normalizers, or every stop rule passes its test and misses in production.
- Sign each message with the first name of the person who logged the outcome.
- **Forced run:** for allowlisted phones only. It may skip the slots, holidays, due times and the
  48 h spacing, and force the template path. It never skips opt-out, `lost` or eligibility.
- **Ship** as in W3.

**Acceptance:** D7 (unit half).

### W6 — Templates (spec §3.11)
- After C1, submit the four marketing templates and the one utility template, language `he`, on
  the lead line's account, with the approved texts byte for byte.
- Use the provider's template API if it has one (read its documentation, never guess). Otherwise
  hand Tom the exact texts (§6-D).
- Meta's review runs in the background. A template still in review at the end leaves D6 or D7 ❌,
  and the report says so.

### W7 — The menus
- Run brain `docs/plans/2026-09-28-lead-reply-menus-masterprompt.md` W1 to W4 as written; its W3
  checks the playbook §2 texts against the finished copies. Its landmines hold, above all
  transactions that vanish unless committed every two or three pages.
- **Hosting.** Export each copy to PDF with Canva's `export-design`. The export link expires and this
  container cannot download from Canva, so pass the link to Shopify's `fileCreate` as
  `originalSource`; Shopify fetches it and serves it from its CDN.
- Write each CDN URL into `lead_menus`, and check that each returns 200 with a PDF.
- Tom approves the menus at C2, before any first message may use them.

**Acceptance:** D10.

### W8 — The site
Grow `section#faq` through the site's own generation path (spec §3.12).

**Every one of these gates, in order, before the live push:**
1. The §5.5 copy rows for the FAQ exist and the site masterprompt's copy check (its D8) passes.
2. `./tools/build.sh`, `verify_figures.py`, `sync_figures.py --check` and `build_theme.py` pass.
3. Push to preview `186698334449`; `theme_ship.py check 186698334449` reports drift 0.
4. The site harness passes on preview, on a phone and a desktop viewport.
5. `/site-gate` returns `SHIP` on preview, or `CONDITIONAL_SHIP` with Tom's written approval of its
   conditions.

**Then the live push**, under the standing authorization:
- back up the live theme first;
- use `--nodelete` and the GT set only;
- reach drift 0 on `166730072305`.

**Then finish the site masterprompt:** its D6 real lead (with the identity it prescribes),
`PUBLISH.md`, and its stamp.

**Acceptance:** D11.

### W9 — Checkpoint C2: end to end on Tom's phone
**First, without Tom:** render the bodies for all five ready texts and a no-menu text through the
dry-run path, and compare each with the playbook. This proves D3 for every menu with nothing sent,
no webhook and no CRM lead. Menu recognition itself is covered by W3's unit tests.

**Then one Hebrew message to Tom, asking him, in this order:**
1. approve the five menus (links);
2. on his phone, send `היי, אני מעוניין במאצ׳ה` (the first message arrives);
3. tap `אני רוצה להזמין` (the link arrives). **Do not order yet.**

**Then, before any order exists:**
- log an `answered_progressing` outcome on his test lead;
- force-run the scheduler for the test phone through the template path, once per marketing template;
- record a `delivered` status for each.

The order must come after this, because an existing order stops the sequence.

**Then ask him to:**
4. submit a small order on the link. It is a draft, so it invoices nothing. The free-form
   confirmation arrives; force the utility template once and record its `delivered` status;
5. reply to the confirmation;
6. send `הסר`. Show that nothing automated follows.

Evidence for every step: a `wa_event_log` id, a `lead_event` id or the draft id.

Afterwards:
- delete the test draft in Shopify; it was never completed;
- close his test lead as `lost`, reason `אחר`, note `בדיקת מערכת`.

**Acceptance:** D1, D3–D8 (live halves), and D10's approval.

### W10 — Soak, stamp, report
- Leave the gate false. Record the soak start in the report.
- Run D8's query at the end of the run.
- Stamp this document, the site masterprompt and the menus masterprompt.
- Close U-049 to U-053 in Sales-Machine where done, with pointers.
- Send the §9 report. Its single action for Tom is the written go of §6-G, after at least 24 hours.

**Acceptance:** D12.

### W11 — When Tom writes the go
The go arrives in this same session as his message. Nothing is scheduled; you wake on it.

1. **Check that the soak passed. Every item below must hold, or you do not flip:**
   - at least 24 h since the recorded start;
   - D8's query returns 0;
   - every lead-line event that the journey answers (a first message, a button, a submitted order)
     has its dry-run row, while free text has none (D-027);
   - no `failed` status without an explanation.
2. **Emit RUNTIME_READY for the lead journey.** Append to brain `.claude/state/runtime_ready.json`,
   never overwriting it. Brain `docs/decisions/modules/sales-declaration.md` §11 requires this
   before the flag flips.
3. **Flip** `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` to true through the Railway-variable workflow.
   If you cannot, give Tom the one variable to set.
4. **Prove the live path on a phone that never opted out.** The test phone did, in W9. Use a
   second phone of Tom's if he has one at hand. Otherwise use the next real lead: verify its first
   message reached `delivered` when Tom next writes. Report in one Hebrew line.

Leads from the soak got only dry runs, so they never received the notice. They stay ineligible for
the sequence, and people follow up with them.

## 5. Scope

**IN:** §4.

**OUT — do not touch, and do not "improve":**
- the AI module for Instagram Direct and Messenger (U-054);
- the landing pages' design;
- the order bot's order flow, beyond echo keying;
- every frozen flag and code sentinel in brain `CLAUDE.md`;
- `stock_ledger`, `balance_anchors` and every projection;
- messages to anyone who did not write first, any imported list, and the six leads of §2.2;
- prices, products and the catalog in Shopify;
- the manual CRM templates (U-026) and the email alerts (U-033-a).

## 6. Tom's part — the complete list. Nothing else is his.

**A. Before pasting:** allow the Canva connector for the whole session.
- **How:** add `mcp__Canva` to `permissions.allow`, or answer «always allow» at the first prompt.
- **Time:** about 2 minutes.
- **Why only he can:** only he grants permissions in his session.

**B. Only if W2 finds the lead line silent:** fix the number's webhook or coexistence in the
provider's dashboard, with the steps the session gives.
- **Time:** about 10 minutes.
- **Why only he can:** only he holds that dashboard.

**C. Only if Railway lacks a secret the lead line needs.** Two cases:
- `LEAD_INGEST_TOKEN`: copy it from the `sales-leads-poll` function's secrets to Railway.
- The provider's key does not serve the lead line: create one for the lead connection and set it on
  Railway under the name the session gives.

About 5 minutes each. Only he can: these are secrets, and no session may hold them.

**D. Only if the provider has no template API:** submit the five templates in WhatsApp Manager, with
the texts the session hands over.
- **Time:** about 15 minutes.

**E. Checkpoint C1** (W1). One reply:
- the approvals;
- the text `בדיקת מסע GT` sent from his phone;
- the last four digits of that phone;
- optionally, a customer example.

About 20 minutes.

**F. Checkpoint C2** (W9): approving the menus, and the taps on his phone. About 15 minutes.

**G. After at least 24 hours of soak (`D-005`):** the written go to open the gate:
`מאשר פתיחת השליחה ללידים`. Until he writes it, nothing reaches a real lead.

## 7. Landmines — do not rediscover these

1. **"The lead line is set up, and nothing arrives."** The provider does not forward the number, or
   coexistence lapsed. GT's route and worker drop nothing (spec §2). → W2, and §6-B.
2. **"A test order produced an invoice."** The portal completes drafts in `settle`
   (`api/src/portal/orders.ts:225-247`), reached from the normal path and from the stale-replay path
   (`orders.ts:141-153`). → The lead path reaches neither, and a test proves it.
3. **"The tests passed, and production changed."** Here both `DATABASE_URL` and
   `DATABASE_URL_POOLED` are production, and 25 test files skip the guard; some write
   `stock_ledger`. → Both variables point at the local throwaway database before every run, checked
   for `rvadsozabmxkkrktwgnv`. Never `TEST_ALLOW_PRODUCTION_DB`, never `pg_prove -d "$DATABASE_URL"`.
4. **"The migration broke the API."** Railway deploys on merge, and the code met the old schema. →
   Apply the migration before merging (W3).
5. **"Facebook leads stopped arriving."** `LEAD_INGEST_TOKEN` was rotated; Make still sends the old
   one. → Never rotate it.
6. **"A wake-up message went to a Facebook lead."** An eligibility check was missing. → A delivered
   notice from the lead line is required (spec §3.5).
7. **"The order bot went quiet for a customer."** A lead-line echo marked the chat human-handled
   (`worker.ts:128-148`). → Key echoes by number (spec §3.9).
8. **"The gate held, but nobody can prove it."** No send was logged. → The send log comes first (W3).
9. **"Error `131049` or `131050` never reached the code."** Statuses were normalized without errors.
   → spec §3.5a; then `131049` means retry no sooner than 24 h, and `131050` means opt-out.
10. **"Template rejected, invalid parameter."** A parameter held a newline, a tab or four spaces. →
    Join the order lines on one line.
11. **"Health says nothing is missing, but no lead is captured."** `missingSecrets` ignores the lead
    variables. → Add the booleans (W2).
12. **"The test phone vanished."** A seed with `on conflict do update` overwrote it. → Seed with
    `on conflict do nothing`, and write the phone after the migration.
13. **"The scheduler sent nothing this week."** `holidays_il` marks Sukkot through 2026-10-03. →
    Expected. Test with a forced run for the allowlist.
14. **"The live push was refused."** Claude Code's permission layer calls `theme_ship.py push --allow-live` a production deploy. →
    The standing authorization covers it. If it is still refused, ask Tom to approve it in the
    session, and never work around it.
15. **"`git checkout -B` was refused."** The same layer calls it irreversible. → On a branch whose PR
    was squash-merged, `git merge --no-edit origin/main`.
16. **"The Canva edits vanished."** An open `edit-design` transaction dies when another opens or it
    idles. → Commit every two or three pages, with one Canva actor at a time.
17. **"The PDF link died."** Canva export links expire. → Host through Shopify `fileCreate` (W7).
18. **"`portal_copy_check` passed a file it never read."** Its file lists are fixed. → Add new files
    to them, and run `--self-test`.
19. **"My FAQ edit disappeared."** `gt-site` `src/index.html` is generated. → Edit the source and the
    Hebrew strings, then build (spec §2).
20. **"The site build rejected an FAQ answer."** It contains a `₪` price, and the site shows none. →
    Drop it, or use the price-free wording Tom approved at C1.
21. **"A migration number clashed."** Another session wrote a file in `db/migrations/` meanwhile. →
    List before and after writing. A new file in between means **HALT**, `contract_failure`; never
    renumber silently.
22. **"A PR subscription arrived."** Opening a PR subscribes the session server-side (`subscription.created`). →
    `unsubscribe_pr_activity` at once.
23. **"A secret or a phone number is in the transcript."** It was read or printed (`env`, a log
    line). → Never print an environment value. Test presence with `test -n`, and keep phones in the
    database only.
24. **"`delivered` never arrived."** It did; the pipeline dropped it as a duplicate of `sent`
    (`worker.ts:369-375`). → De-duplicate statuses on id plus status (W3).
25. **"The stop rule passed its test and missed a real reply."** The test used one phone format, and
    production has two (`972…` and `+972…`). → One normalizer; test data from both (W5).
26. **"The forced test run messaged an opted-out phone."** The force skipped too much. → It skips
    only slots, holidays, due times and spacing (W5).

## 8. Halt conditions (additions to the inherited set)

- **A real send reached a phone outside the allowlist before Tom's go.** STOP: it is an incident.
  Report it first, before anything else.
- **A lead's draft was completed, or a Shopify order tagged `lead` exists.** STOP.
- **An approved message text must change to fit Meta or a limit.** STOP and ask Tom; do not edit it.
- **A §1.1 decision would be broken.** STOP.
- **A test is about to run while `DATABASE_URL` or `DATABASE_URL_POOLED` contains
  `rvadsozabmxkkrktwgnv`.** STOP.
- **The lead line is still silent after §6-B.** STOP W9 only; finish everything else.

## 9. Final report (to Tom, in Hebrew; PR bodies in English)

Use the handoff shape of brain `CLAUDE.md` §Handoff: STATUS and the eight PASS fields. Then:

1. What Tom can now watch working: what a lead sees, step by step.
2. D1 to D12, each ✅ or ❌, with its evidence pointer. No partial credit.
3. The numbers:
   - events on the lead line;
   - dry-run rows, and D8's query result;
   - each template's review status.
4. The artifacts, with links: PRs, the migration, the menus, the live site.
5. What is still Tom's (§6-G), and anything unfinished, plainly.
6. Whether done was reached: yes or no.
7. The single next action.

If anything is not ready, say so first and plainly.
