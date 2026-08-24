# MASTERPROMPT — GT Sales: the last mile to a production system Tom can demo

> **Usage (Tom):** paste this entire file as the first message of a fresh Claude Code
> session on a frontier model, with all four repos attached (`gt-factory-os`,
> `gt-factory-os-portal`, `gt-factory-os-production-brain`, `Sales-Machine`).
> The session takes the sales module from "the code is built" to "a stranger can watch
> it work and find nothing broken." It halts for you only where a human genuinely must
> act — §6 is that complete list.
>
> **Provenance:** written 2026-08-24 from live-verified state (Supabase
> `rvadsozabmxkkrktwgnv` queried 2026-08-24 11:0x; Make team 1240098 inspected;
> GitHub Actions history read). Design authority: `docs/superpowers/specs/
> 2026-08-10-sales-leads-pipeline-design.md`. Governance:
> `docs/decisions/modules/sales-declaration.md`. Decision log that overrides the spec
> where they disagree: `Sales-Machine/doctrine/decisions.md` (see **D-006**).

---

## 0. How to work — read before anything else

### 0.1 Boot order (mandatory, in order)

1. `gt-factory-os-production-brain/CLAUDE.md`
2. `gt-factory-os/CLAUDE.md`
3. `gt-factory-os-portal/CLAUDE.md`
4. `Sales-Machine/CLAUDE.md` → `CURRENT_STATE.md` → `doctrine/decisions.md`
5. `docs/superpowers/specs/2026-08-10-sales-leads-pipeline-design.md` — **in full.**
6. `Sales-Machine/evidence/2026-08-24-make-intake-handover.md` — what changed on the
   last day and why. Read it before forming any plan about Meta.
7. This file's remaining sections.

**Authority order:** production-brain `CLAUDE.md` → `gt-factory-os/CLAUDE.md` →
portal `CLAUDE.md` → `Sales-Machine/CLAUDE.md` → `doctrine/decisions.md` → the
2026-08-10 spec → this file. On conflict, higher wins. **`doctrine/decisions.md`
outranks the spec**: D-006 already reversed the spec's D10.

### 0.2 The standard this work is held to

Tom is demonstrating this to his boss. His words: *"0 mistakes and no embarrassments
will be accepted."* Translate that into engineering terms and it means exactly three
things, in priority order:

1. **Nothing on screen may be false.** Every number, badge, status and timestamp must
   be defensible if someone asks "where does that come from?"
2. **Nothing may be dead.** No button that does nothing, no route that 404s, no empty
   state that reads like a bug, no spinner that never resolves.
3. **Nothing may depend on luck.** The demo must not require a lead to arrive during
   it, a network call to be fast, or a cache to be warm.

A feature that is impressive but occasionally wrong is worth **less than zero** here.
When forced to choose, cut scope and keep truth.

### 0.3 Skills are mandatory, not suggestions

| Moment | Skill |
|---|---|
| Session start | `using-superpowers` |
| Before writing any code | `superpowers:writing-plans` — a task-level plan from §4, then execute it |
| Every implementation task | `superpowers:test-driven-development` |
| Any failure, surprise, or "that's odd" | `superpowers:systematic-debugging` |
| Before any "done" / "ready" / "works" claim | `superpowers:verification-before-completion` |
| Any portal UI change | `portal-audit`, then the relevant UX agents |
| Before declaring demo-ready | `ux-release-gate` and `production-go-no-go` |

Do **not** use `brainstorming`. The design is settled and Tom approved it. Do not
re-litigate anything LOCKED in the spec or CONFIRMED in `doctrine/decisions.md`.

### 0.4 Evidence standard — the thing that separates this from theatre

Every claim of completion carries a path, a paste, or a count. `200 OK` proves layer
one and nothing else. The six-layer proof from production-brain `CLAUDE.md` is the
bar for anything touching data:

> ledger/table write posted → projection updates → operator-visible output →
> downstream consumer reads the new value → integrity check passes → **exception path
> exercised, not just the happy path**

"It should work" is not evidence. "I tested it" without output is not evidence.
**Screenshots of your own reasoning are not evidence.** Rows, counts, and recorded
runs are.

### 0.5 Git

Work on the branch each repo designates for this session. `git push -u origin <branch>`.
Open PRs. **Never `git add -A` or `git add .`** — stage explicit paths. Merge
autonomously only when checks are green *and* the change is verified (production-brain
authorisation, Tom 2026-06-20). Prod deploy + migration apply autonomy of 2026-07-24
applies, with its one-line announcement immediately before dispatch — announcement is
visibility, not permission; do not wait for a reply.

### 0.6 Language

Code, comments, commits, PR bodies, docs: **English**. Anything a user sees, and every
email: **Hebrew**, per the portal's authorised-surface table. The `/apps` + `(sales)`
route group is Hebrew-first and RTL by Tom's explicit UX target — that is already
authorised, do not re-ask.

### 0.7 First message back to Tom, before any code

Repeat §6 — his checklist — so he can act in parallel. Then work without waiting.

---

## 1. Mission and definition of done

**One testable sentence:** a lead submitted on the GT Facebook form appears in Tom's
inbox and in `/sales/today` within minutes, unattended, every day; Tom can run an
entire sales day from the portal without hitting a dead end; the system tells him
within one day if any part of it breaks; and there is a **recorded, narrated
walkthrough** that proves all of the above to someone who has never seen the system.

**Done means all nine of these are true and evidenced:**

| # | Condition | Evidence required |
|---|---|---|
| D1 | A real lead submitted through Meta's testing tool lands in `sales_core.lead` within 10 minutes | row + `lead_event(created)` + timestamps |
| D2 | That lead produced exactly one Hebrew email in Tom's inbox, with a working portal link | Tom confirms receipt; one `alert_sent` event, not two |
| D3 | That lead is visible and workable in `/sales/today`, and an outcome tap writes an event | row + `lead_event` + recorded in the video |
| D4 | A duplicate submission produces no second lead and no second email | counts before/after |
| D5 | A malformed payload is rejected **and logged**, never silently dropped | `sales_core.lead_reject` row |
| D6 | Killing the transport is detected within 24h | induced-silence test → heartbeat alarms |
| D7 | Every org that can be matched to a Shopify customer is matched | before/after counts; conversion job fires on a real order |
| D8 | `/sales/today` presents a workable queue, not the entire table | count on screen + the rule that produced it |
| D9 | A recorded walkthrough exists covering every screen and every state | video file + written script |

Anything not on this list is out of scope unless Tom asks.

---

## 2. Ground truth — verified 2026-08-24, **re-verify at boot, trust nothing here blindly**

### 2.1 What is built and live

| Piece | State | Evidence |
|---|---|---|
| `sales_core` schema (org / lead / append-only lead_event, phone normalisation, one `ingest_lead` write path) | LIVE | migrations 0318–0321 |
| Workspace data layer, mutation functions, `api_read.v_sales_*` views, admin-gated Fastify endpoints | LIVE | 0322–0327 |
| Portal `/apps` + `(sales)` route group — today / leads / orgs / attention / settings, Hebrew RTL, admin-only | LIVE | portal PRs #213–#215, tranches 162–172 |
| `sales-leads-poll` Edge Function — routes `poll` / `backfill` / `daily` / `probe` / `ingest` / `pulse` / `health` | LIVE, `verify_jwt=true` | gt-factory-os #226, #227 |
| Runtime tables `poll_run`, `lead_reject`; `convert_lead()` — sole writer of `won` | LIVE | migration 0328 |
| `intake_mode` setting; heartbeat judges the live path and watches a pulse | LIVE | migration 0329 |
| cron 27 (`*/10` poll) + cron 28 (`0 4 * * *` daily) | ACTIVE, vault-authenticated | 0328 |
| `RESEND_API_KEY` | **PROVEN** — heartbeat sent 2026-08-24 04:00:09Z, severity `alarm`, correctly | `poll_run` route=daily |
| Make Facebook connection `gteveryday` (6309050) | reauthorised 2026-08-24, **valid to 2026-10-23** | Make API |

### 2.2 The numbers that define the work (live SQL, 2026-08-24)

```
leads                 188        orgs                  186
orgs matched Shopify    0   ← conversion loop cannot fire for ANY existing lead
uncontactable          39   ← no phone AND no email; real history, but unworkable
flagged duplicates      2
status = 'new'        188   ← every single lead
leads ever touched      0   ← NOBODY HAS EVER USED THE WORKSPACE
leads from source='facebook'  0   ← NO LIVE LEAD HAS EVER ARRIVED
```

**Read those last two lines carefully.** The system has never carried a real lead and
no human has ever worked a lead in it. Everything about "it works" is, at this moment,
theoretical. That is the gap this session closes.

### 2.3 What is NOT built

- **The two Make scenarios.** Nothing is transporting leads. This is the blocker.
- **Any Shopify↔org matching for the 188 imported leads.**
- **Any resolution of the queue problem** — `/sales/today` holds all 188.
- **The demo walkthrough.**

### 2.4 Known-broken, adjacent, not yet triaged

- `lionwheel_poll` intermittently fails: `date/time field value out of range:
  "23/08/2026 14:36"` — a DD/MM date parsed as MM/DD. Fires only when day-of-month
  > 12, so it looks random. Real bug, unfixed, **not part of the sales module** —
  raise with Tom, do not silently absorb.
- `dispatch-alerts-cron` has failed every run for days, with 7–10s durations that
  predate the 2026-08-23 Actions outage. Separate root cause, uninvestigated.

---

## 3. What "last mile" actually means here

Most of the remaining work is **not** feature work. It is the difference between a
system that is built and a system that is trustworthy. Think about it in these terms
and the priorities fall out:

**The intake is a pipe with no water in it.** Everything downstream — the queue, the
alerts, the conversion loop, the heartbeat — has been tested against imported history
and mocks. None of it has ever processed a lead that arrived on its own.

**The conversion loop is architecturally complete and functionally dead.** `won` can
only be written from a Shopify order for a matched org. Zero orgs are matched. So the
one claim the design makes about closing its own loop is, today, false for 100% of the
data.

**A queue containing everything is not a queue.** 188 untouched leads in "today" is
honest and useless. On a demo screen it reads as either "nobody works here" or "this
tool doesn't help." Both are worse than showing five.

**Nobody has ever used it.** Zero first-touches means every interaction path — the
outcome tap, the drawer, the status change, the next-touch — has only ever been
exercised by tests. First real use during a demo is how demos die.

**Silence is still the enemy.** The original failure was two months of quiet nobody
noticed. The pulse design fixes the detection, but the pulse does not exist yet.

---

## 4. Workstreams

Do them in this order. W1 unblocks everything; W6 cannot start until W1–W4 are real.

### W1 — Make the intake actually flow

**Build two Make scenarios** (team 1240098, org 6913249). You have Make MCP write
access; build them yourself, then have Tom verify visually.

*Scenario A — lead transport (instant):*
```
facebook-lead-ads:NewEvent  (hook 2797155, or a fresh hook)
  → facebook-lead-ads:GetLeadgen  (connection 6309050)
  → HTTP POST https://rvadsozabmxkkrktwgnv.supabase.co/functions/v1/sales-leads-poll
```
Headers: `Authorization: Bearer <SUPABASE_ANON_KEY>` (satisfies platform `verify_jwt`),
`X-Lead-Ingest-Token: <LEAD_INGEST_TOKEN>`, `Content-Type: application/json`.

Body — **send `field_data` RAW; do not map fields inside Make**:
```json
{"route":"ingest","source":"facebook","external_id":"{{2.id}}",
 "created_at":"{{2.created_time}}","campaign_name":"{{2.campaign_name}}",
 "ad_name":"{{2.ad_name}}","form_id":"{{2.form_id}}","form_name":"{{2.form_name}}",
 "platform":"{{2.platform}}","field_data": <raw field_data array from module 2>}
```
**Why raw matters:** the old scenario `GT Leads — Instant` is still on disk mapping
`מה_שם_המסעדה/בית_הקפה/בר_שלך?` and `city` — questions the live form stopped asking.
It would have written half-empty rows even if its connection had never expired. A
mapping hand-written inside a Make module is invisible, untested and drifts silently.
`/ingest` runs raw `field_data` through the same tested mapper the poll uses, and
alarms on unknown fields (spec §10).

*Scenario B — the pulse (hourly):*
A Facebook module that **exercises the connection** (e.g. list forms on the page) →
HTTP POST, same URL and headers, body
`{"route":"pulse","from":"make","forms_visible":<count>}`.

It must genuinely touch Facebook. A ping that only proves Make is running would pass
happily while the Facebook token is dead — which is the exact failure being defended
against.

**Then prove it end to end (D1–D6).** Tom submits a test lead via
`developers.facebook.com/tools/lead-ads-testing`. Verify every layer. Then deliberately
break it: disable Scenario B, confirm the next heartbeat alarms. Re-enable.

**Acceptance:** D1–D6 all evidenced. `sales_core.lead` contains at least one row with
`source='facebook'` that arrived on its own.

### W2 — Make the conversion loop real

Match the 186 orgs against Shopify customers, one-off, then verify the daily job fires.

- Match order per spec §5.4: `shopify_customer_id` → `phone_e164` → exact `email` →
  business email domain. **`sales_core.is_business_domain` already excludes free
  providers — do not bypass it.** Folding every gmail.com lead into one fictional
  business is a data catastrophe that looks like a feature.
- Write `shopify_customer_id` and a dated `shopify_snapshot`. Never copy customer
  master (D3 — reference, not replica).
- Report matched / unmatched / ambiguous. **Ambiguous means ambiguous** — leave it
  unmatched and list it; do not pick the first hit to make a number look better.
- Then confirm `convert_lead()` fires for at least one real order, writing `won`,
  `converted_order_ref` and both events.

**Acceptance:** D7. A stated, defensible match rate, and at least one lead genuinely
converted from order evidence.

### W3 — Turn the queue into a queue (U-011)

This is a **product decision Tom owns** (§6). Prepare both options, implement the one
he picks, and make the rule visible on screen so the number is explainable:

- **(a) Triage sprint** — work the backlog down in-app; `/sales/today` shows what is
  genuinely due today by SLA and next-touch.
- **(b) Daily cap** — `app_setting.queue.daily_cap` already exists (currently 15).
  Enforce it, and show *why* these N were chosen.

Whichever ships: the screen must answer "why these?" without a human explaining.

**Acceptance:** D8.

### W4 — Data quality, so nothing on screen embarrasses anyone

- **39 uncontactable leads.** They are real history (§8) and must not be deleted. They
  are already excluded from the Today queue (0326) and findable behind a chip. Verify
  that holds, and that the chip reads as deliberate rather than as a bug.
- **2 flagged duplicates.** Confirm they render as *flagged*, never as blockers, and
  that the drawer explains the flag.
- **Org display names.** Currently zero are `ללא שם`, which is good — verify none
  regress once live leads arrive with only a personal name.
- Sweep every list/detail surface for `null`, `undefined`, `NaN`, `Invalid Date`,
  raw enum values (`working`, `lost`) leaking instead of Hebrew labels, and untranslated
  developer strings.

**Acceptance:** a written pass over every `(sales)` screen in all states — empty,
one item, many items, error, loading — with no defect above cosmetic.

### W5 — Monitoring that tells the truth

- Confirm the heartbeat under `intake_mode='make'` alarms on a stale pulse and stays
  calm on a quiet day with a live pulse (this logic is tested; verify it in production).
- Confirm exactly one alert per lead under the Make path.
- Raise `lionwheel_poll` and `dispatch-alerts-cron` (§2.4) with Tom as separate,
  named items. **Do not fix them inside this scope without his go-ahead** — they are
  outside the sales lane, and widening scope silently is its own kind of failure.

**Acceptance:** D6, plus a one-page "what breaks, how you find out" summary.

### W6 — The recorded walkthrough

**This is a named deliverable, not documentation.** Tom must be able to send it, or
play it, and have a stranger understand the system without narration from him.

**Produce:**
1. **A video** covering the complete flow: a lead arrives → the email → open from the
   email into the portal → the Today queue → the drawer → an outcome tap → the event
   appearing in the timeline → leads list, filters, the uncontactable chip → orgs →
   attention → settings. Include at least one **empty state** and one **error state**
   deliberately, because hiding them is what makes demos brittle.
2. **A written script** — a numbered shot list mapping each moment to what is on
   screen and what claim it proves. This is what makes the video re-recordable.

**Mechanics.** Chromium and Playwright are pre-installed
(`PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`; never run `playwright install`).
Use Playwright's `recordVideo`. Record at a fixed viewport, RTL, Hebrew.

**Real risks — solve them, do not discover them at the end:**
- **Auth.** The portal uses Supabase SSR and `/sales` is admin-gated. You need a
  session. Prefer a dedicated demo login with `storageState`. **Never** reintroduce
  `X-Fake-Session` / `X-Test-Session` — the portal `CLAUDE.md` forbids it and
  cleaned files must stay clean.
- **Hebrew font rendering** in a headless container. Verify glyphs render before
  recording a full take; a video full of tofu boxes is worse than no video.
- **Determinism.** The run must not depend on a lead arriving mid-recording. Seed the
  state first, then record.

**Acceptance:** D9. A playable file plus the script, both committed or delivered.

### W7 — Rehearsal and the go/no-go

Run `ux-release-gate` and `production-go-no-go`. Then do a **full dry run of the exact
demo**, in order, and write down every stumble. Fix the stumbles. Run it again.

Produce a **one-page demo runbook** for Tom: what to open, in what order, what to say,
what to do if a lead does not arrive live, and what to avoid clicking.

**Acceptance:** two consecutive clean dry runs.

---

## 5. Scope

**IN:** everything in §4.

**OUT — do not touch, do not "improve":**
- Any outbound message to a lead or customer. `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED`
  stays `false`. Imports and backfills never email; only genuinely new live leads do.
- factory-os core: `stock_ledger`, `balance_anchors`, `bom_*`, `items`, `components`.
  Not read directly, not written. Catalog/customer reads via curated views only.
- Frozen flags and code sentinels (production-brain `CLAUDE.md`).
- `factory_os_jobs/index.ts`.
- Green Invoice; the spreadsheets import (D13); the churn radar; Klaviyo; any new vendor.
- `tailwind.config.ts`, `globals.css`, `portal_ux_standard.md`,
  `portal_language_direction_audit.md`.
- The direct Meta Graph API path. It is closed (see §7) and is a separate task for
  whoever administers the `Green Tea` app.

---

## 6. Tom's part — the complete list, nothing else is his

**A. Approve the two Make scenarios being built in his account** (or build them from
the §W1 spec). They live in his Make workspace; the session will not create them
without a go-ahead.

**B. Submit one test lead** — `developers.facebook.com/tools/lead-ads-testing`, GT page,
live form. ~2 minutes, after the session says the transport is up.

**C. Confirm two emails actually arrived** — the lead alert and a daily heartbeat.
Resend returning `200` proves delivery was accepted, not that it landed. This is the
one layer the session genuinely cannot verify alone.

**D. Decide U-011** (§W3): triage the 188-lead backlog down, or cap the daily queue.
Blocking for W3 only.

**E. Decide U-013, with Alex:** should the Facebook form ask for the business name
again? The live form is name/phone/email, so every org is inferred. Not blocking;
directly improves data quality.

**F. Optional, unblocks a better long-term path:** get admin on the `Green Tea` Meta
app, or have its admin add `ads_management`, `leads_retrieval`, `pages_show_list`,
`pages_read_engagement`. That restores the direct API and removes Make from the path.
Not needed for the demo.

---

## 7. Landmines — discovered the hard way, do not rediscover them

1. **The Meta token has no lead permissions.** `/debug_token` on 2026-08-24 proved it:
   valid, non-expiring, app `Green Tea`, scopes `business_management`,
   `whatsapp_business_*`, `manage_app_solution`, `public_profile` — **none** of the
   four needed. It was never the Page assignment. Do not send Tom back to Business
   Settings; that path is closed until §6F happens.
2. **Tom has no Meta developer access.** Registration blocks at SMS verification, in
   both local and international format. Do not plan around Graph API access.
3. **`(#100) ... requires pages_read_engagement` has two causes** that look identical.
   `granular_scopes.target_ids` from `/debug_token` is the only thing that separates
   them. The diagnostic is already built and wired into the poll's failure path.
4. **Never map Meta fields inside Make.** §W1 explains why. The live form is
   `0205.2025-2question-new` and asks two questions; assume nothing else.
5. **Migration bracket rule.** List `db/migrations/` immediately before writing a
   numbered file, and again after. New file appeared in between → HALT,
   `contract_failure`. Next free slot at time of writing: **0330**.
6. **`verify_jwt=true` on every Edge Function.** The deploy workflow refuses
   unauthenticated deploys. `/ingest` and `/pulse` therefore need the platform JWT
   *plus* `X-Lead-Ingest-Token`.
7. **The `typecheck` CI workflow only covers `scripts/**`.** Root `tsconfig.json` has
   `"include": ["scripts/**/*.ts"]`. A green check says nothing about `api/`,
   `supabase/functions/` or the portal. Run the real checks locally.
8. **`api/node_modules` is not installed** in a fresh container. `npm install` in
   `api/` before trusting `tsc --noEmit` there. Two pre-existing errors in
   `src/purchase-session/handler.actions.ts` and
   `test/production_plan_base_batch.test.ts` are baseline, not yours.
9. **GitHub Actions went fully dark for ~19h on 2026-08-23–24** — every workflow
   instant-failing in 3–10s with zero logs. It recovered on its own. If you see that
   signature, it is infrastructure, not your diff; do not burn re-runs.
10. **Israeli phone defect.** Both `+972526380055` and `+9720526380055` appear in real
    data. `sales_core.normalize_phone_il` handles it; `_lib/phone.ts` is a faithful
    port. Do not write a third implementation.
11. **`won` has exactly one door** — `sales_core.convert_lead()`. Not settable by a
    user, by CHECK constraint and by the API. Keep it that way.
12. **Deno lint** reports one `no-import-prefix` error on `npm:` imports. That is the
    repo-wide Edge Function convention (`shopify_available_reconcile` shares it).
    Expected; not a defect.

---

## 8. Halt conditions — stop, do not improvise

- Any path would email a lead or customer, or flip a frozen flag → **STOP**.
- Meta or Make returns a shape the spec did not predict → `assumption_failure`: record
  the raw response, halt that path, surface it.
- A migration slot conflict → `contract_failure`, halt.
- The work would touch factory-os core, or portal files outside the sales surface → stop.
- A number cannot be explained from primary data → do not put it on screen. Escalate.
- **You cannot verify something Tom must verify** (email delivery) → say so plainly and
  ask. Do not mark it done.

---

## 9. Final report to Tom — Hebrew, short, honest

State, in this order:

1. **What a stranger can now watch working**, end to end.
2. **The nine done-conditions (D1–D9)**, each ✅ / ❌ with its evidence pointer.
   No partial credit — a condition is met or it is not.
3. **Numbers:** leads in, matched orgs, queue size and the rule behind it, alerts sent,
   conversion count.
4. **The video** — where it is, how long, what it covers.
5. **What is still his** (§6 leftovers) and what remains genuinely unfinished.
6. **The single next action.**

If anything is not ready, say so first and plainly. Tom's stated bar is zero
embarrassments in front of his boss — a surprise on the day is far more expensive than
a caveat now.
