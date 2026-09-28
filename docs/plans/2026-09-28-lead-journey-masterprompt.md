# MASTERPROMPT — A lead who writes to GT's lead line gets the right menu, three clear choices and a personal ordering link, a lead who spoke with sales is woken up before every follow-up, and gteveryday.com goes live with it: built, proven on Tom's phone, and one written go from switching on

**STATUS: LIVE — not yet executed**
<!-- The executing session's last act is to change this line to SHIPPED / SUPERSEDED by <path> /
ABANDONED — why, with evidence pointers (merged PRs, deploy run ids, wa_event_log ids, the draft id,
the live theme check, the soak start time, the report). -->

> **Usage:** paste this entire file as the first message of a fresh Claude Code session. Attach
> `gt-factory-os`, `gt-factory-os-production-brain`, `gt-factory-os-portal`, `Sales-Machine` and
> `gt-site`. Before pasting, allow the Canva connector for the whole session (§6-A).
>
> **What it does:** takes the WhatsApp lead journey from "decided and documented" to:
> - built and deployed;
> - proven end to end on Tom's phone;
> - running as a dry run for every other lead;
> - live on gteveryday.com.
>
> It stops at the one step Sales-Machine D-005 reserves for Tom: the written go to send to real
> leads, after a 24-hour soak (Sales-Machine `D-005`).
>
> **Tom's standing authorization for this run.** Pasting this file gives it, and only this:
> - push `gt-site` `main` to the live theme `166730072305` once the site gates in W8 are green;
> - apply this work's migration and deploy the API through `deploy-production.yml` once CI is green;
> - submit the five WhatsApp templates of W6 with the texts he approves at checkpoint C1.
>
> It does **not** authorize opening the outreach gate (`SALES_CUSTOMER_OUTREACH_WRITE_ENABLED`),
> sending to any phone outside the test allowlist, or completing a lead's draft order.
>
> **Provenance:** written 2026-09-28 by the session that designed the journey with Tom. Sources:
> - live reads the same day of Supabase `rvadsozabmxkkrktwgnv` (the queries are in §2.5) and of the
>   API's public health route;
> - the five repos, read at their `main` heads;
> - Meta's WhatsApp documentation, read at source (cited in the Sales-Machine research evidence);
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
  - Tom's phone.

  Railway variables are set through a `workflow_dispatch` workflow on the pattern of `gt-factory-os`
  `.github/workflows/railway-gi-env.yml`, which pipes each value to `railway variable set --stdin`
  and never prints it. You decide implementation details inside the spec alone.
- **Read first, in order:**
  1. brain `CLAUDE.md`;
  2. `gt-factory-os` `CLAUDE.md`;
  3. Sales-Machine `CLAUDE.md`;
  4. the playbook;
  5. the spec;
  6. Sales-Machine `evidence/2026-09-28-lead-journey-ground-truth.md`;
  7. brain `docs/plans/2026-09-28-lead-reply-menus-masterprompt.md` (you run it as W7);
  8. brain `docs/plans/2026-09-27-brand-site-lead-modal-masterprompt.md` §1.1, D6, D10 and its W7
     (you finish it in W8).
- **Halt conditions, evidence standard, lanes, migrations and git discipline** are inherited from:
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
  - Write the test first for each component (`test-driven-development`).
  - Prove it before you claim it (`verification-before-completion`).
  - One subagent may work on Canva while you work elsewhere. **Never two Canva actors at once.**
- **Language.** This document is in English; Hebrew literals stay in their script, in backticks.
  **Output language: Hebrew to Tom** — short, direct, no recap, and every message ends with at most
  one action for him (his standing preference). English for code, commits, PR bodies and repo docs.
- **First action:** run §2.5, then read the files above, then W0.

## 1. Mission and definition of done

**One testable sentence:** a lead who writes to `054-758-8132` gets the journey of Sales-Machine D-027
to D-032 exactly as the playbook specifies, proven on Tom's phone and dry for everyone else;
gteveryday.com is live with it; and the only step left is Tom's written go after a 24-hour soak.

| # | Condition | The observation that would prove it false |
|---|---|---|
| D1 | The lead line delivers | `select count(*) from order_intake.wa_event_log where raw_payload->>'phone_number_id' = '217553368116155'` returns 0, or has no row from the test phone |
| D2 | Every automated text is the one Tom approved | Sales-Machine `U-051` still open, or a unit test that compares each send body and template with the playbook text finds a difference |
| D3 | First messages are right for all five menus and for no menu | a dry-run body (or the real one on the test phone) with the wrong PDF, a missing footer, other than three buttons, or a second general reply to one phone within 30 days |
| D4 | Every button and the text `הסר` route as the playbook §4–§5 say | a tap whose `lead_event` row is missing or wrong, or `לא כרגע` not setting `lost` and `opt_out_at` |
| D5 | A lead's order is a draft and nothing more | the test order's draft (tag `lead`) is completed; or 60 s after creation Green Invoice holds a document for it or LionWheel a task; or the test that fails when `draftOrderComplete` is reachable from the lead path is missing or red |
| D6 | The order confirmation arrives | no confirmation on the test phone after the test order; no unit test of the utility-template body |
| D7 | The wake-up sequence obeys every rule | a scheduler test missing for any rule of playbook §5; or on the test phone, message 1 absent after an `answered_progressing` outcome, or sent after a reply or a `הסר` |
| D8 | The gate holds | any phone outside the test allowlist received a real send while `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` is false (an outbound row that is not `dry_run:*`, or a Meta `sent` status for that phone) |
| D9 | Echoes are keyed by number | the order bot defers a phone only because of a lead-line echo (test) |
| D10 | Menus are built, checked and hosted | any copy fails the menus masterprompt's D1–D9, or `app_setting` `lead_menus` lacks a working public PDF URL for a menu |
| D11 | The site is live, with the grown FAQ | `python3 tools/theme_ship.py check 166730072305` reports drift; the FAQ lacks the Tom-approved questions; the harness fails against live; or the site masterprompt's D6 and D10 are unmet |
| D12 | Ready, soaking, stamped and reported | the gate is not false; no recorded soak start; this document, the site and the menus masterprompts are not stamped; or no Hebrew report reached Tom |

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
- **The general reply** (D-030), once per phone in 30 days.
- **The wake-up sequence** (D-031):
  - at most four messages per lead, each ahead of a human follow-up;
  - every stop rule, the time slots and the 48 h spacing (`D-031`);
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
  - the rest of the site masterprompt's §1.1 stands.

## 2. Ground truth — measured 2026-09-28; re-verify at boot

### 2.1 What is built and live
- **The order line works end to end** through the provider:
  - inbound, logged in `order_intake.wa_event_log`;
  - outbound: the portal sent links on 2026-09-26 and 2026-09-28.
- **Health route.** `GET https://gt-factory-os-api-production.up.railway.app/webhooks/wa-order-bot/health`
  returned `{"intake_enabled":true,"auto_commit_enabled":false,"inbound_auth":"waba-id","missing_secrets":[]}`
  on 2026-09-28. Its `missing_secrets` ignores the lead-capture variables (config.ts:88-101), so it
  cannot tell you whether lead capture is configured.
- **The ordering portal is live.** Flag `customer_portal_live` is on, allowlist `*`, since 2026-09-25.
  Every portal order is **completed** today (spec §2).
- **The CRM** (`sales_core`) records outcomes, including `answered_progressing` with a `next_touch_at`.
- **The site.** `gt-site` `main` is `6b067e8` (#29). It was verified on preview `186698334449` with
  drift 0 on 2026-09-28. The live theme `166730072305` does not have it yet: the push was refused by
  Claude Code's permission layer that day.

### 2.2 The numbers (2026-09-28, about 15:00 UTC)
- `wa_event_log`, last 30 days:
  - order line `185509261301816`: 6,441 events, of them 3,488 messages;
  - lead line `217553368116155`: **0, ever**.
- `sales_core.lead` by status: new 145, lost 61, working 30, won 5.
- `lead_event` outcomes seen: `answered_progressing`, `no_answer`, `whatsapp_sent`.
- Reply-button taps received ever: 17, the last on 2026-07-12.
- Highest migration: `0359_planning_demand_open_orders_only.sql`.

### 2.3 What is NOT built
- Every component of spec §3.
- The five WhatsApp templates.
- `app_setting` `lead_menus`, an opt-out column and event, the no-send dates.
- The grown FAQ.
- The finished menus. Their Canva state is only partly edited and partly unknown; see the menus
  masterprompt §2.2.

### 2.4 Known-broken, adjacent, out of scope
- **Echoes are keyed by chat phone only** (`worker.ts:128-148`). Fixed here (spec §3.9).
- **Lead capture sends neither the message text nor the menu** (`lead_capture.ts:67-94`). Fixed here.
- **`SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` is read by no code** (spec §2). Made real here.
- **Not this work:**
  - the CRM's manual WhatsApp templates signed with Tom's name (Sales-Machine U-026);
  - email alerts from `sales-leads-poll` (Sales-Machine U-033-a).

### 2.5 Re-verification block
```sql
-- 2026-09-28: events per receiving number, last 30 days (lead line = 217553368116155)
select raw_payload->>'phone_number_id' as pnid, count(*) as events,
       count(*) filter (where type='message') as msgs, max(created_at) as last_event
from order_intake.wa_event_log where created_at > now() - interval '30 days' group by 1 order by 2 desc;
-- 2026-09-28: flags and CRM shape
select flag_key, enabled, value, updated_at from private_core.feature_flags where flag_key = 'customer_portal_live';
select status, count(*) from sales_core.lead group by 1 order by 2 desc;
select payload->>'result' as result, count(*) from sales_core.lead_event where event_type = 'outcome' group by 1;
```
```bash
# 2026-09-28: health, heads, migrations, live theme
curl -sS https://gt-factory-os-api-production.up.railway.app/webhooks/wa-order-bot/health
for r in gt-factory-os gt-factory-os-production-brain gt-factory-os-portal Sales-Machine gt-site; do git -C $r log --oneline -1 origin/main; done
ls gt-factory-os/db/migrations | tail -3
(cd gt-site && python3 tools/theme_ship.py check 166730072305)
```

## 3. What the hard part actually is

1. **It looks like a messaging feature. It is a pipe that has never carried water.** The lead line
   has never delivered one event to GT (§2.2). Prove delivery first (W2). Build the rest in parallel
   against tests, and claim no end-to-end result until D1 holds.
2. **It looks like ordering. It is an invoicing trap.** Every completed Shopify order is invoiced
   by Green Invoice within seconds and opens a LionWheel task. The portal completes every order
   today. The lead path must stop at the draft, and a test must prove it can never go further.
3. **It looks like a scheduler. It is a set of stop rules.** The expensive bug is a nudge to someone
   who ordered, replied or said stop. Write the stop-rule tests before the send code.
4. **It looks like copy. It is Tom's voice, the law and Meta at once.**
   - Every text is his, verbatim.
   - D-018 and `§30א` bind.
   - A Meta template cannot be edited after approval without another review.

   So nothing is submitted before C1.
5. **It looks like one build. It is five repos that ship in an order:**
   1. backend: migration, API deploy;
   2. portal lead mode;
   3. templates;
   4. menus;
   5. site: FAQ, live push.

   Stop after C1 and C2 only.

## 4. Workstreams, in order

### W0 — Boot and baseline
- Run §2.5 and record the output.
- Establish the CI baseline on `gt-factory-os` `main`: `npm run typecheck`, `cd api && npm test`, the
  `test:order-intake` and `test:portal` suites, and pgTAP. Record every pre-existing failure, so it
  is not later mistaken for yours.
- Draft, before C1:
  - the portal lead-mode strings: reuse approved rows of the UX gate §5 register wherever one fits;
    the registration form already carries business name, city and contact name;
  - the grown FAQ list: questions and answers from `מאושר` rows of Sales-Machine
    `knowledge/answers/answer-bank.yaml` only, never a D-018 row, each through `stop-slop`.

### W1 — Checkpoint C1 with Tom: the only stop at the start
Send Tom **one** Hebrew message that asks for everything at once:
1. Approve the playbook texts (§2–§5) or rewrite them, the portal strings and the FAQ.
2. Send one WhatsApp message now, from his phone, to `054-758-8132`.
3. Confirm the test phone: show him only the last four digits of the sender you saw.
4. Optionally, name a real customer who agreed to be the example in wake-up message 3.

Record his answers:
- close U-051 in Sales-Machine, quoting him, and add UX gate §5 rows for any new portal string;
- store the test phone in `sales_core.app_setting` key `lead_journey_test_phones`, never in a repo,
  document, commit or log line.

The spec's §3.10 names an env var for the allowlist; the database setting replaces it, so update
the spec in your backend PR.

Then keep working to C2.

**Acceptance:** D2, and D1's first half.

### W2 — The lead line delivers (spec §3.1; Sales-Machine U-050)
- Find Tom's test message in `wa_event_log`. If it is there, D1's first half holds.
- If it is not:
  - diagnose: the provider's webhook for that number, or coexistence lapsed (Sales-Machine D-023);
  - give Tom the exact steps (§6-B), and continue W3–W7 against tests meanwhile.
- Add lead-capture booleans (configured, enabled — never values) to the health route.
- Make sure production carries the four lead-capture variables (spec §2), through the workflow
  pattern of §0. If `LEAD_INGEST_TOKEN` must be set, rotate it in both places rather than read the
  live value.

### W3 — Backend (spec §3.2, 3.3, 3.5, 3.6, 3.9, 3.10)
- **Migration.** List `db/migrations/` immediately before writing the file and again after. It
  carries the opt-out column, the event types, the unique send index, `lost_reasons` + `לא כרגע`,
  `lead_menus`, `lead_journey_test_phones` and the no-send dates. Seed the dates from a verified
  Israeli holiday calendar and cite it. Add its pgTAP test.
- **Code:** the lead-line port and its message kinds; menu recognition; button routing; the gate,
  the dry run and the allowlist; echo keying; lead capture carrying the text and the menu.
- **Where the gate check lives:** inside the lead-line port's send, not in its callers.
- **Ship:** PR, CI green, merge. Announce one line, then dispatch `deploy-production.yml` with
  `confirm=APPLY` and the migration's glob. Pass the post-deploy health check and
  `rebuild_verifier() = 0`.

**Acceptance:** D3, D4, D8, D9 (their unit halves).

### W4 — Ordering from a lead link (spec §3.7)
- Build the lead token and the page.
- Submission is **draft only**, tags `lead` and `pk-<idem>`. Write the test that fails if
  `draftOrderComplete` is reachable.
- Then the confirmation (free-form inside the window, else the utility template), the draft-order
  event and the owner alert.
- **Copy:** every string is in the register, and `api/scripts/portal_copy_check.mjs` passes.

**Acceptance:** D5, D6 (unit halves).

### W5 — The wake-up scheduler (spec §3.8)
- A pg_cron job every 15 minutes, calling a Railway route on the `stock_exceptions_sweep` pattern.
- Put every rule of playbook §5 under an injected clock before the send code exists: each stop rule,
  the 48 h spacing, the slots, Friday–Saturday, a holiday, 131049 and 131050.
- Sign each message with the first name of the person who logged the outcome.

**Acceptance:** D7 (unit half).

### W6 — Templates (spec §3.11)
- After C1, submit the four marketing templates and the one utility template, language `he`, on
  the lead line's account, with the approved texts byte for byte.
- Use the provider's template API if it has one (read its documentation, never guess). Otherwise
  hand Tom the exact texts (§6-D).
- Meta's review runs in the background. Record each template's status in the report.

### W7 — The menus
- Run brain `docs/plans/2026-09-28-lead-reply-menus-masterprompt.md` W1 to W4 as written; its W3
  checks the playbook §2 texts against the finished copies.
- Then export each copy to PDF, host it at a stable public HTTPS URL, and write `lead_menus`.
- Its landmines hold, above all transactions that vanish unless committed every two or three pages.

**Acceptance:** D10.

### W8 — The site
- Grow `section#faq` through the site's own generation path (spec §3.12).
- Build, verify, push to preview `186698334449`, run the site gate and the harness.
- Then the live push under the standing authorization:
  - back up the live theme first;
  - use `--nodelete` and the GT set only;
  - reach drift 0 on `166730072305`.
- Then finish the site masterprompt: its D6 real lead (the identity it prescribes), `PUBLISH.md`,
  and its stamp.

**Acceptance:** D11.

### W9 — Checkpoint C2: end to end on Tom's phone
- **Prove the other paths first:** all five ready texts and a no-menu text, as signed webhook
  payloads from a phone outside the allowlist. The dry-run bodies prove D3 for every menu with
  nothing sent.
- **Then ask Tom, in one Hebrew message, to do on his phone:**
  1. send `היי, אני מעוניין במאצ׳ה`;
  2. tap `אני רוצה להזמין`;
  3. submit a small order on the link (a draft, so it invoices nothing);
  4. reply to the confirmation.
- **Then:**
  - log an `answered_progressing` outcome on his test lead;
  - run the scheduler with the real clock, or force-run it for the test phone only;
  - have him send `הסר`.
- **Evidence:** a `wa_event_log` id, a `lead_event` id or the draft id per step. After the test,
  delete the test draft in Shopify; it was never completed.

**Acceptance:** D1, D3–D8, live halves.

### W10 — Soak, stamp, report
- Leave the gate false. Record the soak start in the report.
- Check that no phone outside the allowlist got a real send.
- Stamp this document, the site masterprompt and the menus masterprompt.
- Close U-049 to U-053 in Sales-Machine where done, with pointers.
- Send the §9 report. Its single action for Tom is the written go of §6-G, after the soak.

**Acceptance:** D12.

## 5. Scope

**IN:** §4.

**OUT — do not touch, and do not "improve":**
- the AI module for Instagram Direct and Messenger (U-054);
- the landing pages' design;
- the order bot's order flow, beyond echo keying;
- every frozen flag and code sentinel in brain `CLAUDE.md`;
- `stock_ledger`, `balance_anchors` and every projection;
- messages to anyone who did not write first, and any imported list;
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

**C. Only if the provider's key does not serve the lead line:** create a key for the lead connection
and set it on Railway under the name the session gives.
- **Time:** about 5 minutes.
- **Why only he can:** it is a secret, and no session may hold it.

**D. Only if the provider has no template API:** submit the five templates in WhatsApp Manager, with
the texts the session hands over.
- **Time:** about 15 minutes.

**E. Checkpoint C1** (W1). One reply:
- the approvals;
- one WhatsApp message;
- the last four digits confirmed;
- optionally, a customer example.

About 20 minutes.

**F. Checkpoint C2** (W9): the taps on his phone. About 10 minutes.

**G. After at least 24 hours of soak (`D-005`):** the written go to open the gate:
`מאשר פתיחת השליחה ללידים`. Until he writes it, nothing reaches a real lead.

## 7. Landmines — do not rediscover these

1. **"The lead line is set up, and nothing arrives."** The provider does not forward the number, or
   coexistence lapsed. GT's route and worker drop nothing (spec §2). → W2, and §6-B.
2. **"A test order produced an invoice."** The portal path calls `draftOrderComplete`
   (`api/src/portal/orders.ts:225-247`). → The lead path never does, and a test proves it.
3. **"The order bot went quiet for a customer."** A lead-line echo marked the chat human-handled
   (worker.ts:128-148). → Key echoes by number (spec §3.9).
4. **"Template rejected, invalid parameter."** A parameter held a newline, a tab or four spaces. →
   Join the order lines on one line.
5. **Error `131049`.** Meta's per-user marketing cap. → The step stays unsent; retry no sooner than
   24 h.
6. **Error `131050`.** The person stopped marketing messages. → Set the opt-out.
7. **"Health says nothing is missing, but no lead is captured."** `missingSecrets` ignores the lead
   variables. → Add the booleans (W2).
8. **"The gate is false, and a lead still got a message."** A caller sent around the gate. → The
   check lives in the port's send.
9. **"The live push was refused."** Claude Code's permission layer calls it a production deploy. →
   The standing authorization above covers it. If it is still refused, ask Tom to approve it in
   the session, and never work around it.
10. **"`git checkout -B` was refused."** The same layer calls it irreversible. → On a branch whose PR
    was squash-merged, `git merge --no-edit origin/main`.
11. **"The Canva edits vanished."** An open `edit-design` transaction dies when another opens or it idles. → Commit
    every two or three pages, with one Canva actor at a time.
12. **"`portal_copy_check` fails."** A new Hebrew string is not in the UX gate register. → Add the
    row with Tom's approval from C1.
13. **"My FAQ edit disappeared."** `gt-site` `src/index.html` is generated. → Edit the source and
    the Hebrew strings, then build (spec §2).
14. **"A migration number clashed."** Another session wrote a file in `db/migrations/` meanwhile. → List before and
    after writing. A new file in between means **HALT**, `contract_failure`; never renumber
    silently.
15. **"A PR subscription arrived."** Opening a PR subscribes the session server-side. →
    `unsubscribe_pr_activity` at once.
16. **"A secret or a phone number is in the transcript."** It was read or printed (`env`, a log line). → Never print an
    environment value. Test presence with `test -n`, and keep phones in the database only.

## 8. Halt conditions (additions to the inherited set)

- **A real send reached a phone outside the allowlist before Tom's go.** STOP: it is an incident.
  Report it first, before anything else.
- **A lead's draft was completed, or an invoice or LionWheel task exists for it.** STOP.
- **An approved text must change to fit Meta or a limit.** STOP and ask Tom; do not edit it.
- **A §1.1 decision would be broken.** STOP.
- **The lead line is still silent after §6-B.** STOP W9 only; finish everything else.

## 9. Final report (to Tom, in Hebrew; PR bodies in English)

Use the handoff shape of brain `CLAUDE.md` §Handoff: STATUS and the eight PASS fields. Then:

1. What Tom can now watch working: what a lead sees, step by step.
2. D1 to D12, each ✅ or ❌, with its evidence pointer. No partial credit.
3. The numbers: events on the lead line, dry-run rows, and the templates' review status.
4. The artifacts, with links: PRs, deploy runs, menus, the live site.
5. What is still Tom's (§6-G), and anything unfinished, plainly.
6. Whether done was reached: yes or no.
7. The single next action.

If anything is not ready, say so first and plainly.
