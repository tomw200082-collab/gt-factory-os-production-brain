# MASTERPROMPT — GT leads: one system that answers, from ad click to first order

**STATUS: LIVE — not yet executed**

> **Usage (Tom):** paste this whole file as the first message of a fresh Claude Code
> session with `gt-factory-os`, `gt-factory-os-portal`, `gt-factory-os-production-brain`
> and `Sales-Machine` attached, and the Supabase, Make and Google connectors on. It takes
> lead handling from "199 leads sitting in a database nobody answers" (§2.2, measured) to "every inbound
> enquiry is routed, answered and measured through one system." It halts for you only
> where §6 says.
>
> **Provenance:** written 2026-08-31. Live state queried against Supabase
> `rvadsozabmxkkrktwgnv` on 2026-08-31 — output pasted verbatim in §2.2. The setup plan
> artifact `הקמת מערכת הלידים`
> (`https://claude.ai/code/artifact/86a3d629-4de2-4255-8503-d72d240019dc`, 36 tasks,
> 0 marked done) was read in full. Governing decisions:
> `Sales-Machine/doctrine/decisions.md` **D-006**;
> `docs/decisions/modules/sales-declaration.md`. Prior masterprompt whose work landed:
> `docs/plans/2026-08-24-sales-production-readiness-masterprompt.md`.
>
> **Shelf life:** §2 is presumed stale after 2026-09-14 — lead counts move daily. Re-run
> §2.5 before planning. If the numbers have moved materially, **adapt**; if the *intake
> has stopped*, halt and surface it first.

---

## 0. How to work

- **Who you are here:** one Claude Code session, frontier model. You hold Supabase (read
  and, via migrations, write), the four repos, Make, Google, Shopify. You may design,
  build, migrate and deploy inside the lanes those repos allow. You may **not** message a
  lead or a customer, choose a paid vendor, or set a commercial term.
- **Read first, in order:** `gt-factory-os-production-brain/CLAUDE.md` ·
  `gt-factory-os/CLAUDE.md` · `Sales-Machine/CLAUDE.md` → `CURRENT_STATE.md` →
  `doctrine/decisions.md` (**D-006 especially**) ·
  `docs/superpowers/specs/2026-08-10-sales-leads-pipeline-design.md` in full ·
  `Sales-Machine/evidence/2026-08-24-make-intake-handover.md` ·
  `Sales-Machine/recipes/intake-monitoring.md` · then both artifacts (the setup plan
  above, and `ספר העבודה` at
  `https://claude.ai/code/artifact/f0457ed1-6e3a-4180-9101-4fc7451d863a`).
- **Authority:** the repos' `CLAUDE.md` files win over this document. Halt conditions,
  evidence standard, git discipline and the frozen-flag rules are inherited from
  `gt-factory-os-production-brain/CLAUDE.md` — §8 lists only the additions.
  **`SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` is `false` and stays `false` in this work.**
- **The standard.** Tom asked for `מערכת של מענה ללידים` — a system that answers.
  Three prohibitions:
  1. **No lead is answered by a machine with a sentence a human did not approve.** The
     book's own rule: the system reproduces an approved answer or it transfers.
  2. **No second CRM.** If a lead's state ends up living in a WhatsApp vendor's inbox
     instead of `sales_core`, the system has failed regardless of how well it replies.
  3. **Nothing is automated that has not been done manually first and measured.**
- **Language:** this document is English; data literals stay in their own script in
  backticks. Customer-facing copy is and stays Hebrew. **Output language: concise Hebrew
  for Tom, concise English otherwise.**

---

## 1. Mission and definition of done

**One testable sentence:** every inbound enquiry — from any campaign, on any channel —
lands in `sales_core`, gets a first response inside the agreed SLA, and its outcome is
visible in one place.

| # | Condition | The observation that would prove it false |
|---|---|---|
| D1 | The CTWA-vs-lead-form architecture is decided, written down, and the chosen transport writes into `sales_core` | A lead exists on a channel whose record is not in `sales_core.lead` |
| D2 | `sales_core.lead where status='new'` is **under 30**, down from 141 | `select count(*) from sales_core.lead where status='new'` returns ≥30 |
| D3 | Every lead ever received has at least one `lead_event` that is not `imported`/`created` | `leads_ever_touched < leads_total` in the §2.5 query |
| D4 | The answer bank is live as data, shared with the knowledge book, and every `לא מוגדר` topic is a transfer row rather than a missing row | A topic from §2.4 with no row in the bank |
| D5 | First-response time is measured from real events, and the median for the last 20 leads is reported | The dashboard cannot produce the number from `lead_event` |
| D6 | A category-routed content kit is sent on request, and which kit was sent is recorded on the lead | A lead marked as having received a kit with no record of which one |
| D7 | The intake heartbeat proves itself: an induced silence raises an alarm within 24h | Stop the feed in a test window; no alarm = fail |
| D8 | The setup artifact's 36 tasks each carry a real status: done with evidence, superseded with a pointer, or open with an owner | A task still at the default with no note |

Anything not on this list is out of scope unless Tom asks.

### 1.1 Settled — do not reopen

- **D-006 stands: Make carries Facebook leads as transport only.** Storage, phone
  normalisation, org matching, dedup, alerting, conversion and heartbeat stay in
  `sales-leads-poll`. Make holds no data and makes no decisions. Do not re-litigate; the
  objection is already on the record in `doctrine/decisions.md` with its full reasoning.
- **`sales_core` is the system of record.** Not a spreadsheet, not a vendor inbox.
- **`convert_lead()` is the sole writer of `won`.** Do not add a second path.
- **The manual pilot is mandatory before automation** (artifact stage 6.4). Automating a
  broken sequence produces a broken sequence faster, at scale, while burning the
  WhatsApp quality rating that the account cannot easily earn back.

---

## 2. Ground truth — measured 2026-08-31; re-verify at boot

### 2.1 What is built and live — the artifact does not know this exists

The setup artifact shows `0 מתוך 36` and describes building a lead system from nothing.
That is not the state. Landed and running in production:

- `sales_core` schema — org, lead, append-only `lead_event`, phone normalisation, one
  `ingest_lead` write path. Migrations `0318`–`0329`, plus `0336`/`0337`. pgTAP green at
  landing.
- Portal `(sales)` route group — Today queue with a one-tap outcome loop, leads list and
  drawer, orgs, quick-add, `⌘K` search, PWA, Hebrew RTL, admin-gated.
- `sales-leads-poll` Edge Function; Make → `/ingest` transport (D-006); daily heartbeat,
  proven firing `2026-08-24 04:00Z`; hourly pulse route live.
- Conversion job: a first Shopify order at or after a lead writes `won` with evidence.
- `sales_rep` and `sales_planner` roles; per-assignee callback digest; a new lead reaches
  the whole desk rather than one inbox (`gt-factory-os` #240).

### 2.2 The numbers that define the work — live, 2026-08-31

```
leads_total 199 · leads_new 141 · leads_won 3 · events_total 359
leads_ever_touched 69 · orgs 196
oldest_lead 2023-06-18 · newest_lead 2026-08-29
```
Arrivals, trailing 30 days: `08-24: 5 · 08-25: 1 · 08-26: 1 · 08-27: 2 · 08-28: 1 ·
08-29: 1` — and nothing between `08-09` and `08-24`. **The intake is alive and carrying
roughly one to two leads a day.**

Read the §2.2 output together and the picture is unambiguous: **141 of 199 leads have
never been answered, and 130 of them (`199 − 69 ever-touched`) have never been touched at
all.** Three converted. The
constraint is not intake and it is not automation.

### 2.3 What is NOT built

No WhatsApp Business API account. No provider. No dedicated number in the API. No
approved message templates. No CTWA campaigns. No content kits as sendable media. No
answer bank as data. No first-response automation. No follow-up scheduler. No measurement
dashboard beyond the portal queue.

### 2.4 The gaps the book itself declares — all four are Tom's, all four block copy

Package contents and prices · delivery time in days · discount tiers by consumption ·
commitment and exclusivity. Each must exist in the answer bank as a **transfer row**, not
as a missing row, before any automation goes live. A missing row makes a machine guess at
a restaurant owner; a transfer row makes it hand over. That distinction is the whole
safety model.

### 2.5 Re-verification block — run before planning

```sql
select
  (select count(*) from sales_core.lead)                                   as leads_total,
  (select count(*) from sales_core.lead where status='new')                as leads_new,
  (select count(*) from sales_core.lead where status='won')                as leads_won,
  (select count(*) from sales_core.lead_event)                             as events_total,
  (select count(distinct lead_id) from sales_core.lead_event
     where event_type not in ('imported','created'))                       as leads_ever_touched,
  (select max(created_at) from sales_core.lead)                            as newest_lead;

-- has the intake stopped? a gap of >48h on a working day is the 2026-06-07 failure again
select date_trunc('day',created_at)::date d, count(*)
from sales_core.lead where created_at > now() - interval '30 days'
group by 1 order by 1 desc;
```

---

## 3. What the hard part actually is

**Reframe 1 — there are two lead systems and nobody has connected them.** The artifact
plans a Click-to-WhatsApp system in nine stages. Production runs a Meta lead-form system
through Make into Postgres. They were designed independently, they assume different
transports, and neither document mentions the other. Build the artifact's plan literally
and GT ends up with two intakes, two inboxes and two truths. **The first deliverable is
not stage 0 — it is the architecture decision (§W1), and until it is made everything
downstream is guesswork.**

**Reframe 2 — the bottleneck is answering, not intake.** 141 unanswered leads with a live
feed adding one to two a day. Every stage of the artifact's plan is designed to *get more
leads*. None of them is the constraint. Fix response before you widen the funnel;
otherwise the automation's most measurable achievement is a bigger unanswered pile.

**Reframe 3 — stage 6's "pilot on 30 leads" already exists, for free.** The artifact
proposes running campaigns to generate 30 leads to work by hand. There are 141 sitting
there, real, already paid for. **Work the backlog and it *is* the pilot** — same learning,
same question log, same baseline metrics, zero media spend and no dependency on the
WhatsApp API. This collapses weeks 3–4 of the artifact's timetable into something that
can start the day this is read.

**Reframe 4 — the WhatsApp API is a two-to-three-week wait, not a build.** Business
verification, number provisioning, provider onboarding and template approval are all
queueing time, and the long pole (Meta Business admin, `docs/plans/2026-08-31-social-
foundation-masterprompt.md` §6.E) is not even started. Start the queue on day one and do
the human work in parallel. Do not sequence the manual pilot behind it.

**Reframe 5 — the answer bank is not this system's asset.** It is the knowledge book's,
and both documents currently specify building it. One of you owns the write path. It
should be the knowledge book (`docs/plans/2026-08-31-knowledge-book-masterprompt.md` §W3),
because that repo has the grading and expiry discipline this content needs. Consume it;
do not fork it.

---

## 4. Workstreams

### W1 — The architecture decision (blocks everything; produce it in the first hour)

Write `docs/decisions/2026-08-31-lead-intake-architecture.md`. It answers, with reasoning
and a recommendation:

1. Does CTWA **replace** the Meta lead form, or run beside it?
2. If a WhatsApp conversation is the entry point, what writes the lead into `sales_core`,
   and when — on first inbound message, or on qualification?
3. Which `source_id` taxonomy identifies a campaign across both paths, so a landing-page
   lead, a CTWA lead and a form lead are all attributable in one table?
4. Where does conversation history live, and what does `sales_core` store as a pointer?
5. What happens to the 199 records already there?

State a recommendation, do not just enumerate. Tom decides (§6.A) — your job is to make
that decision cheap and obviously-right, not to defer it upward unshaped.

**Note the landing pages:** `docs/plans/2026-08-31-category-menus-masterprompt.md` builds
four category landing pages with forms. Those forms must post to the same `/ingest` with a
campaign-carrying `source_id`. Agree the contract with that session; do not let a third
intake appear.

**Acceptance:** D1.

### W2 — Work the backlog (this is the pilot)

141 `new` leads. Triage them into: contactable now · needs enrichment · dead. Then build
the daily working list in the existing portal queue — not a new tool. `U-011` in
`Sales-Machine/CURRENT_STATE.md` is exactly this question and Tom deferred it
deliberately; §6.B closes it.

Every conversation feeds the question log (artifact task 6.2), which is the most valuable
output of this stage: what customers *actually* ask, as opposed to what the book guessed
they would.

**Acceptance:** D2, D3, and the baseline for D5.

### W3 — Measurement, from events not spreadsheets

The artifact's stage 8 proposes a dashboard of six metrics. Build them as queries over
`sales_core.lead_event`, surfaced in the portal:
first-response time · qualification rate · kit-request rate · first-order rate · cost per
order · conversion by category.

**Measure to the order, never to the lead.** A campaign that produces many cheap leads and
zero orders will look like the winner on any lead-level metric, and the budget will follow
it. The artifact says this and it is right.

Targets are set **after** the backlog gives a baseline, not before. A target invented now
is a number nobody will believe in November.

**Acceptance:** D5.

### W4 — The content kits

Three kits, one per campaign category. **The assets are the category menus** being built
in `docs/plans/2026-08-31-category-menus-masterprompt.md` — do not commission a second set
of images. Your job here is the delivery layer: Dropbox structure with a version file,
upload to the provider's media library, the `file → media_id → category` table, and the
record on the lead of which kit went out and when.

Format constraints that will otherwise be discovered the hard way: images `PNG`, `1:1` or
`4:5`, ≤5 MB; video 15–30 s, ≤16 MB — beyond that WhatsApp re-compresses to unusable or
rejects outright.

**Send by `media_id`, never by URL.** URL sends are slower and depend on Dropbox link
permissions that will silently change.

**Acceptance:** D6.

### W5 — WhatsApp Business API — start the queue on day one

In this order, because each step gates the next: Meta business verification → provider
selection → number provisioning → profile → template submission.

Provider evaluation: shortlist three, score them on shared inbox for ≥2 agents · full
Hebrew and RTL · visual flow builder · open API or Sheets connector · template management
in-product · Israeli invoicing. Then ask each the question the artifact correctly
identifies as the one they avoid: **is Meta's per-message fee passed through at cost or
with a markup, and what is the monthly subscription separately from it?** Two numbers.
Get both in writing.

Pull the current Israel marketing-template rate from Meta's own pricing page and compute
`rate × monthly leads × 2 follow-ups` = the true monthly operating cost. Tom approves the
number before anything runs (§6.D).

Only two messages in the whole sequence need a paid template: day-5 and day-12. Everything
else is inside a free window. Say that in the cost note — it is the difference between a
scary number and a real one.

**Acceptance:** feeds D1; Tom's approval is §6.

### W6 — Automation, strictly in this order, and only after W2 reports

1. Automatic first response, routed by `source_id`.
2. Kit send on an affirmative reply.
3. Question-and-answer layer, answering **only** from approved rows.
4. Human handover, which must **stop the automation for that lead**.
5. The follow-up scheduler.

**The scheduler's expensive bug, stated in advance:** any customer reply, and any order,
must cancel every future follow-up for that lead. Test it explicitly before go-live. A
day-12 "just checking in" sent to a customer who ordered on day 3 undoes the whole
system's credibility in one message.

**Acceptance:** D7 and the automation half of D1.

### W7 — Reconcile the artifact

Every one of the 36 tasks gets a real status: done with evidence · superseded by
production, with a pointer to what replaced it · open with an owner and a date. Republish
to the same URL.

**Acceptance:** D8.

---

## 5. Scope

**IN:** everything in §4.

**OUT — do not touch, do not "improve":**
- Any customer-facing send. `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` is `false`; drafts and
  dry runs only, per `Sales-Machine/doctrine/decisions.md` D-005.
- factory-os core — `stock_ledger`, `balance_anchors`, `bom_*`, `items`, `components`.
  Not read directly, not written. `gt-factory-os/CLAUDE.md`.
- The frozen Shopify and LionWheel flags.
- The website and the social accounts — separate documents.
- Building an answer bank from scratch. Consume the knowledge book's.
- Buying anything. Provider selection is a recommendation with numbers; Tom signs.

---

## 6. Tom's part — the complete list, nothing else is yours

**A. The architecture decision** (§W1). The session hands you a recommendation with the
trade-offs costed. You choose. Everything else waits on it. ~20 minutes with the document
in front of you.

**B. Decide `U-011`** — work the 141 backlog down, or cap the daily queue. This is a
product decision that was deliberately not taken during the build. ~10 minutes.

**C. The four commercial decisions.** Same four as the knowledge book §6.A: packages,
delivery days, discount tiers, commitment. **They gate every customer-facing sentence in
this system.** Until they land, the answer bank carries four transfer rows and every one
of those conversations goes to Alex by hand.

**D. Approve the monthly message budget** once §W5 produces the real number.

**E. Choose the provider and pay for it.** The session ranks three with real quotes; the
contract is yours.

**F. The dedicated phone number.** Depends on
`docs/plans/2026-08-31-social-foundation-masterprompt.md` §6.A — what `054-758-8132` is
for. A number that enters the API leaves the phone app permanently.

**G. Meta business verification.** Requires company documents and admin access — see the
social document §6.E, which is the same blocker. **Start it this week; it is the longest
queue in the plan.**

**H. Legal check on the Israeli spam law** for the day-5 and day-12 marketing templates.
A lead who opened the conversation initiated contact; a marketing message days later to
someone who did not order is a different question. The artifact flags this correctly and
it is not a question a session can answer. One call to a lawyer.

**I. Decide `U-013` with Alex** — should the Facebook lead form ask for the business name
again? The live form is name/phone/email, so every org is inferred. Not blocking; it
directly improves data quality on every future lead.

---

## 7. Landmines — do not rediscover these

1. **A silently-expired Make OAuth token stopped the entire lead flow on `2026-06-07` and
   nobody noticed for two months.** Connection `gteveryday` (id `6309050`) expired
   `2026-06-07T20:37:12Z` — the exact hour leads stopped. The current authorisation is
   valid until **`2026-10-23`**. The heartbeat now catches it within 24 h; the heartbeat
   is therefore not optional infrastructure, it is the thing that makes D-006 acceptable
   at all. Never disable it, never let it go untested (D7).
2. **A quiet day and a dead pipe look identical from the database.** That is why the
   hourly pulse exists — an affirmative "I am alive" signal, not an absence of leads.
   Any redesign that drops the pulse re-creates the 2026-06-07 blind spot.
3. **Meta's Graph API is unreachable for Tom.** No developer access, the existing Business
   app is WhatsApp-only and he is not its admin, and developer registration blocks at SMS
   verification. Proven by token diagnostic: the token he produced is valid and
   non-expiring and carries none of `ads_management`, `leads_retrieval`,
   `pages_show_list`, `pages_read_engagement`. **Do not plan around direct Graph access.**
4. **Bulk-sending from the WhatsApp Business *app* gets the number banned**, permanently
   and without appeal. So does any unofficial automation library. Every proactive message
   goes through the official API.
5. **A new API account starts inside a messaging tier and a quality rating.** Good early
   conversations raise it; a blast burns it. Another reason W2 precedes W6.
6. **`customer.amountSpent` and ShopifyQL `average_order_value` are banned** for any
   conversion metric — documented anomalies, one account shows 58 orders at ₪0.00. Use
   the fact table (`Sales-Machine/recipes/sales-report.md`).
7. **Grep proves what is in the repo, not what is live.** Deployed Edge Functions, cron
   jobs and DB flags leave no source trace — this cost GT twice (`0302`). Use
   `list_edge_functions` and read the tables before claiming anything is or is not wired.
8. **153 customers have no phone number in Shopify** (stated in the growth board's own
   footer, `2026-08-30`). Lead enrichment and the Q4 customer
   plan hit the same wall. Whatever you build to capture a phone, build it once and share
   it with `docs/plans/2026-08-31-existing-customers-q4-masterprompt.md`.
9. **The artifact reports `0 מתוך 36` and is wrong.** Roughly a third of its content is
   already built in production under a different architecture. Reconciling it (W7) is not
   bookkeeping — leaving it stale guarantees the next person rebuilds `sales_core`.

---

## 8. Halt conditions

Inherited from `gt-factory-os-production-brain/CLAUDE.md` §Stop conditions and
`gt-factory-os/CLAUDE.md`. Additions:

- Any message would reach a real lead or customer → **STOP**. The flag is `false`.
- The intake shows no lead for more than two working days → **STOP** other work, diagnose the
  transport first. That is the 2026-06-07 signature.
- A design would put lead state anywhere other than `sales_core` → **STOP**.
- A template or automated answer would state a price, a delivery date, an allergen fact or
  a discount that is not an approved row → **STOP**.
- Anything touches factory-os core → **STOP**.

---

## 9. Final report — Hebrew, short, honest

Use `AGENT_TEMPLATE.md` §Output format, tokens matching `VERDICT_GLOSSARY.md`. Cover:

1. What a stranger can now watch working, from ad click to a record in `sales_core`.
2. D1–D8 ✅/❌ with evidence pointers. No partial credit.
3. The numbers: `leads_new` before and after · `leads_ever_touched` · median first
   response · questions logged that had no answer.
4. The artifacts, and where they are.
5. What is still Tom's, and what is genuinely unfinished.
6. The single next action.

Then stamp this file `STATUS: SHIPPED — <date>` with evidence pointers, and commit.
