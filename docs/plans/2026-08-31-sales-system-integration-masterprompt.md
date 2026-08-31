# MASTERPROMPT — the Q4 plan stops being a document and becomes the work Avi does tomorrow

**STATUS: LIVE — not yet executed**
The executing session's last act is to change this to `SHIPPED — <date>` with an execution
record appended, or `SUPERSEDED by <path>`, or `ABANDONED — <why>` with evidence pointers.

> **Usage:** paste this entire file as the first message of a fresh session with
> `gt-factory-os`, `gt-factory-os-production-brain`, `Sales-Machine` and
> `gt-factory-os-portal` attached, plus Supabase and Shopify access.
>
> **This document has two phases and a gate between them.** Phase A is a design
> conversation with Tom and produces no code. Phase B builds what Phase A decided.
> **Do not start Phase B until Tom has approved the Phase A design in writing.**
> Tom's words: `אל תבנה עדיין כלום, אני רוצה שנחשוב על זה לעומק ואז נכין משהו מושלם` —
> think first, then build something perfect.
>
> **Provenance:** written 2026-08-31, from live measurement — `sales_core` and
> `api_read` on Supabase `rvadsozabmxkkrktwgnv` queried directly, the deployed
> `sales-leads-poll` source read in `gt-factory-os/supabase/functions/`, the shipped
> plan CSV recomputed, and `q4_scoreboard.py` run against live Shopify. Every number in
> §2 carries how it was obtained. Nothing here is from memory.
>
> **Shelf life:** §2 is presumed wrong if pasted after **2026-09-14**. Run §2.6 first.
> The single most perishable fact is Avi's activity level — it is days old by
> construction. If reality no longer matches §2, **halt and surface**; do not adapt
> silently, because the whole design rests on Avi being a live daily user.

---

## 0. How to work

- **Who you are here:** one Claude session holding `gt-factory-os` (backend, Edge
  Functions, migrations), `gt-factory-os-production-brain` (governance),
  `Sales-Machine` (knowledge, evidence — **no runtime code, ever**),
  `gt-factory-os-portal` (Next.js 15), plus Supabase and Shopify Admin API. You may
  decide implementation detail alone. You may **not** decide anything in §6.
- **Read first, in order:** `gt-factory-os-production-brain/CLAUDE.md` ·
  `EXECUTION_POLICY.md` · `CURRENT_STATE.md` · `Sales-Machine/CLAUDE.md` ·
  `Sales-Machine/CURRENT_STATE.md` · this file's §2 and §3 ·
  `docs/plans/2026-08-31-existing-customers-q4-masterprompt.md` (the plan this one
  connects — read its §12 and its renumbering table, not its §1–§9 numbering).
- **Authority:** cited, never restated. Where this document and an authority doc
  disagree, **the authority doc wins and this document is wrong.** Report the conflict.
- **Halt conditions, evidence standard, lane discipline, git discipline:** inherited
  from `gt-factory-os-production-brain/CLAUDE.md §Stop conditions` and
  `EXECUTION_POLICY.md`. §8 lists **only** the additions specific to this work.
- **The standard, in Tom's words:** `בצורה ממש ממש יפה` — really, really beautiful.
  Translated into three checkable prohibitions:
  1. **No second place to look.** If a person has to check both the portal and a
     spreadsheet to know what to do today, the work failed.
  2. **No manual re-entry.** If closing the loop requires a human to retype something
     the system already knows, the work failed.
  3. **No number without provenance.** Every figure on every surface names its source
     and its date, or it does not ship.
- **Language:** this document is English because that is the register you reason best
  in. Data literals — Hebrew column names, statuses, `item_type` values, script text —
  stay in their own script, in backticks, and are **never** translated; a translated
  identifier matches nothing. **Output language: concise English.** Short sentences, no
  preamble, no restating the question. Anything Tom will read in the portal or in a
  message is Hebrew.

---

## 1. Mission and definition of done

**One testable sentence:** *A person opening the portal on any working day between
2026-09-01 and 2026-12-31 sees the day's growth work beside their existing lead work,
acts on it there, and the system records the outcome from the order stream without
anyone retyping it.*

### Phase A — the design (this is the first deliverable; it is not code)

| # | Condition | The observation that would prove it false |
|---|---|---|
| A1 | Every question in §5 has a written recommendation with its reasoning and its rejected alternative | A §5 question with no recommendation, or a recommendation with no stated cost |
| A2 | The win rule is specified per motion as a query, not as prose | Any motion whose win rule cannot be written as SQL over orders + a baseline |
| A3 | The design names what a human must still type, and the count is under 150 for the whole quarter | The design implies more than 150 manual entries, or does not say |
| A4 | Tom has approved it in writing, with each §5 answer recorded | Phase B started without a written approval naming the §5 answers |

### Phase B — the build

| # | Condition | The observation that would prove it false |
|---|---|---|
| D1 | The plan's tasks are queryable from Postgres with the same owner, date, motion and account as the shipped CSV | `select count(*) from <plan table>` ≠ the CSV's 716, or a row whose owner/date/motion differs from the CSV |
| D2 | The portal's Today surface shows a growth task to its owner on its date | Log in as `avi@gteveryday.com` on a date the CSV assigns him a task and see nothing |
| D3 | A win is recorded from the order stream with no human clicking `won` | Insert a qualifying test order and observe the status unchanged, or observe `won` set with `converted_order_ref is null` |
| D4 | The routine-reorder false positive is impossible, not merely avoided | A plan account places an order containing only what it already buys, and the system marks any win |
| D5 | The scoreboard reads the database, not the CSV, and reproduces the CSV's figures on day zero | `q4_scoreboard.py` against the DB differs from its CSV run on 2026-09-01 |
| D6 | Every agent that exists has a declaration in `Sales-Machine/agents/` naming its allowed paths, its writes and its stop conditions | An agent runs whose declaration is absent or whose behaviour exceeds it |
| D7 | No customer was contacted by any machine | `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` ≠ `false`, or any outbound message sent by code |
| D8 | The daily volume is capped and the cap is visible | A day renders more items than the owner's stated capacity with no indication of what was deferred |

Anything not on these lists is out of scope unless Tom asks.

### 1.1 Settled — do not reopen

- **The plan itself** (2026-08-31): 153 accounts, 716 tasks, 3 channels, 7 motions,
  target ₪262,661 run-rate — summed from the shipped CSV's `קצב צפוי` column and
  asserted by `q4_scoreboard.py --selfcheck`. Shipped 2026-08-31 after three revisions and Tom's explicit correction that
  matcha leads and MUZA does not. **Do not re-plan, re-price, or re-segment.** If you
  believe a figure is wrong, report it; do not act on it.
- **`won` is evidence-only.** `sales_core.lead` carries CHECK
  `lead_won_requires_evidence`, the workspace API rejects a human setting it, and
  `supabase/functions/sales-leads-poll/_lib/convert.ts` is the only code that decides.
  This is a good design and it stays. See §3.2 — the work is to make the *evidence*
  motion-aware, never to relax the constraint.
- **`Sales-Machine` holds no runtime code.** Ever. Knowledge, doctrine, recipes,
  evidence, agent declarations only.
- **Money basis.** `lineItems.discountedTotalSet.shopMoney` = the stored ex-VAT price.
  `customer.amountSpent` and ShopifyQL tax/net/gross columns are banned — the store is
  configured `taxesIncluded=true @17%` and those columns lie. Month attribution
  `Asia/Jerusalem`, never UTC.
- **Channels and owners.** T1 = Alex **with** Avi in the room (15 accounts) · T2 = Avi
  alone (22) · T3 = Tom on WhatsApp (116). Avi has no fixed hours; 3–4 calls a day.

---

## 2. Ground truth — measured 2026-08-31; re-verify at boot

### 2.1 The fact that reorganizes the question

**`sales_core` is not a dormant system. Avi is working in it right now.**

```
lead_event by actor        Avi 113 · Tom 16 · system 200 · system:* 31
Avi's events, last 7 days  113 of 113          <- he started this week
Avi's last event           2026-08-31 12:13 Asia/Jerusalem
leads with first_touch_at  58 of 200
```

Measured 2026-08-31 ~16:10Z from `sales_core.lead_event`. **The Q4 plan starts
2026-09-01 — tomorrow.** Avi learned this tool this week and gets 22 solo accounts plus
15 joint meetings tomorrow. If the plan does not arrive inside the tool he just learned,
he has two systems on day one. That is the entire reason this work is urgent, and it is
why the answer is *extend the live surface*, not *build a beautiful new one*.

An earlier record (`Sales-Machine` `U-011`) says every imported lead is untouched. **That
is now out of date** — it predates Avi's week. Do not inherit it.

### 2.2 What is built and live

| Thing | State |
|---|---|
| `sales_core` schema | `lead` 200 · `lead_event` 360 · `org` 197 · `poll_run` 1,224 · `app_setting` 6 · `lead_reject` 7 |
| `lead.status` | `new` 142 · `lost` 43 · `working` 12 · `won` 3 |
| `lead_event.event_type` | `created` 200 · `status_change` 62 · `next_touch_set` 20 · `outreach` 18 · `note` 13 · `matched_existing_customer` 13 · `assignment` 12 · `alert_sent` 12 · `outcome` 7 · `converted` 3 |
| Today queue `api_read.v_sales_today` | **already typed**: `new_lead` 132 · `returning_customer` 10 · `due_follow_up` 8 |
| Sales API | `queries/sales/{today,leads,orgs,activity,attention,week-stats,settings}` · `mutations/sales/{quick-add,bulk-assign,settings}` |
| `app_setting` keys | `sla_hours` · `whatsapp_templates` · `queue` · `lost_reasons` · `intake_mode` · `meta_poll` |
| Portal users | `avi@gteveryday.com` [planner] · `alex.berov@gmail.com` [planner] · `tom@gteveryday.com` [admin] · `denispotehin@gmail.com` [operator] |
| Conversion | `sales-leads-poll` cron; `pickConversionOrder()` = earliest non-cancelled order at or after the lead's `created_at`; writes via `sales_core.convert_lead(...)` |

**Alex already has a portal account.** The Q4 plan recorded that there is no calendar
access for Alex or Avi; that is about *calendar*, not the portal. Both are planners here.

### 2.3 The plan, as shipped

```
716 rows  = 642 customer touches (T1/T2/T3) + 74 internal tasks
153 accounts · 84 working days · none empty
base ₪1,202,176 · run-rate target ₪262,661
lead motion per account:
  מאצ'ה — קו חדש 73 · מאצ'ה — עומק 35 · מחית פרי — קו חדש 21
  תה — עומק ורוחב 11 · אובה — הרחבה על מאצ'ה 8 · החזרה 5   (MUZA leads none)
```
Source: `Sales-Machine/evidence/2026-08-31-q4-daily-plan.csv`, recomputed 2026-08-31.
Its outcome column is `תוצאה (זכה / לא עכשיו / לא ענה / סירב)` and the win value is `זכה`.

### 2.4 The tracking gap, measured

`q4_scoreboard.py --since 2026-08-24` against live Shopify, run 2026-08-31:

```
מגעים שתוכננו בחלון : 642
מגעים עם תוצאה רשומה: 0     <- nobody filled anything
הזמנות בחלון        : 87   (35/153 plan accounts ordered)
אותות               : 7    signals, of which 6 are מאצ'ה — עומק
זכיות מאושרות       : 0
```

Zero on day zero is expected. It is also the whole risk, and it is the number this work
exists to change. Note the 6 signals on `מאצ'ה — עומק`: those are accounts that **already
buy matcha**, which is exactly why a target SKU on an order is a signal and not a win.

### 2.5 What is NOT built

- No link between the plan and `sales_core`. `q4_sales_system_load.py` exists, is
  **dry-run by default, and is deliberately blocked** — see §3.2.
- **The plan's population is barely represented.** 197 `org` rows, of which **13** carry
  a `shopify_customer_id`. All 153 plan accounts are Shopify customers. The overlap is
  near zero, so this is a population to create and match, not to join.
- No per-motion win definition anywhere, in code or prose.
- No growth-task concept in the schema. `lead` is the only work object and it is
  terminal (`new → working → won|lost`).
- No agent declarations. `Sales-Machine/agents/` holds a `README.md` listing five
  **planned** agents and an explicit rule: *no agent without a declaration*, read-only
  first, anything that writes last and gated.
- Nothing to send. `Sales-Machine` `U-020`: the Drive folder `05 · מה שולחים ללקוח` is
  empty — no catalogue PDF, no customer price list, no training videos.
- Nowhere to escalate. `U-021`: all 17 rules in `knowledge/boundaries/refusals.yaml` end
  in `מעביר לאלכסנדר` and **no phone, email or group for him exists in any file**.

### 2.6 Re-verification block — run this before trusting §2

```sql
-- Is Avi still live? The design depends on it.
select max(created_at at time zone 'Asia/Jerusalem') last_event,
       count(*) filter (where created_at > now() - interval '7 days' and actor='Avi') avi_7d
from sales_core.lead_event;

-- Queue shape and population overlap.
select item_type, count(*) from api_read.v_sales_today group by 1;
select count(*) total, count(shopify_customer_id) with_shopify from sales_core.org;
select status, count(*) from sales_core.lead group by 1;
```
```bash
# The plan as shipped, and the tracking gap. Both must be re-run, not quoted.
python3 gt-factory-os/scripts/sales-report/q4_scoreboard.py --selfcheck      # expect 16/16
python3 gt-factory-os/scripts/sales-report/q4_scoreboard.py --since 2026-09-01
```

---

## 3. What the hard part actually is

### 3.1 It looks like loading a CSV. It is a lifecycle mismatch.

`sales_core.lead` models **acquisition**: a stranger arrives, you work them, they convert
once, and the record is finished. `won` is terminal and singular.

The Q4 plan is **expansion**: the account is already a customer, already ordering every
nine days on average, and will still be a customer whether the play lands or not. There
is no terminal state, the same account can carry several motions, and next quarter it
will carry different ones. An expansion play that "converts" does not stop existing.

Forcing one onto the other is where this work goes wrong. The reframe: **a lead is a
person you are trying to acquire; a play is a product you are trying to place.** They
share an `org`, a queue and an owner — and almost nothing else.

### 3.2 The conversion job is not buggy. It is correct code applied to the wrong population.

`pickConversionOrder()` takes the earliest non-cancelled order at or after the lead
arrived. The "at or after" guard exists precisely so that a business's purchase history
cannot inflate the conversion rate. **For a new lead that is exactly right.**

For an existing customer ordering every ~9 days, an order after the record was created is
guaranteed within days no matter what anyone did. **All 153 plan accounts would read
`won` on their next routine reorder.** That is `Sales-Machine` `U-029`.

The tempting fix — `and l.source <> 'q4_existing_2026'` — makes the plan invisible to the
one mechanism that closes loops without human typing. That trades a false positive for a
permanent blind spot.

The real fix: **the evidence must become motion-aware.** A win for `מאצ'ה — קו חדש` is not
"they ordered". It is *"a line item in the matcha family appeared on an order from this
account, and no such line item has ever appeared before."* That is still evidence, still
machine-decided, still no human clicking `won` — it preserves everything good about the
existing design. It needs `ORDERS_Q` in `sales-leads-poll/index.ts` extended to fetch
line items, which it does not do today (it takes only `total_price`).

### 3.3 Most wins are already machine-detectable. Design for that, and the human load collapses.

Per motion, against a pre-plan baseline frozen on 2026-08-31:

| motion | machine-decidable win | needs a human? |
|---|---|---|
| `מאצ'ה — קו חדש` | first-ever matcha line item | no |
| `מחית פרי — קו חדש` | first-ever purée line item | no |
| `אובה — הרחבה על מאצ'ה` | first-ever ube line item | no |
| `מאצ'ה — עומק` | matcha spend above baseline over a window | no, but the threshold is a decision |
| `תה — עומק ורוחב` | a tea flavour never previously ordered | no |
| `החזרה` | any order after N months of silence | no |

**What no order can ever show:** they said no · not this quarter · the manager left · they
went to a competitor · wrong contact. That — and only that — is what a person types.

Across a quarter that is **~100 entries** — a design target with no source; step `A-4`
is where you replace it — against 642 planned touches. The 642 is the `2026-08-31`
CSV's T1/T2/T3 row count
(§2.3). The 100 assumes roughly one refusal or blocker per account across 153 accounts,
most of which never need one — **re-derive it in A-4, do not inherit it.** State the
number in
the design and hold it; it is the difference between a system people use and a
spreadsheet nobody fills. §2.4 already shows what happens by default: 642 planned, 0
recorded.

### 3.4 The queue already anticipated this. It did not anticipate the volume.

`api_read.v_sales_today` is **already discriminated by `item_type`** and already carries
`returning_customer` and `is_existing_customer`. A growth play is a **fourth item type in
a view designed for heterogeneous work**, not a new surface. That is the strongest
argument in this document for extending rather than building.

But the queue already holds 150 items, and `U-011` records the open problem: *a queue
containing everything is not a queue.* Adding ~8.5 tasks a working day makes an unusable
queue worse. **The cap that was optional becomes mandatory here** — D8 exists for this.
Tom deliberately did not decide the cap; see §6.C.

### 3.5 "Agents" is the part most likely to overreach.

`Sales-Machine/CLAUDE.md` rule 7: an automation is built **only after its knowledge base
is verified**, and any customer-facing write sits behind
`SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` (`false`) plus Tom's written approval, a dry run
and a soak. `agents/README.md`: no agent without a declaration; read-only first.

The knowledge base is genuinely not ready: `U-020` there is nothing to send, `U-021` there
is nowhere to escalate. **An agent that drafts a message referring to a catalogue that
does not exist, and escalates to a person with no contact details, is worse than no
agent.** The honest ladder is: watch → prepare → (gated, later) send. Phase B stops at
prepare.

---

## 4. Phase A — the brainstorm, and what it must produce

Phase A is a conversation with Tom, run in Hebrew, that ends in a written design. It
produces **no schema, no migration, no portal code**.

Work in this order:

**A-1. Re-verify §2** with §2.6. If Avi's activity has stopped, say so before anything
else — the design changes completely.

**A-2. Answer every §5 question** with a recommendation, its reasoning, its cost, and the
alternative you rejected and why. Recommend; do not present a menu and wait.

**A-3. Write the win rules as SQL.** One query per motion, against the frozen baseline.
If a motion resists, that is a finding — surface it rather than inventing a threshold.

**A-4. Count the human load.** How many entries a person must type across the quarter,
per owner. If it exceeds 150, the design is wrong; change it before showing Tom.

**A-5. Draw the surface.** What Avi sees at 09:00. What Tom sees on Sunday. One page
each, described precisely enough to build without asking. Where a picture helps, build a
single artifact — this is the one visual permitted in Phase A, and it is a mock, not a
system.

**A-6. Put it to Tom in Hebrew** — short, with each §5 question, your recommendation, and
what it costs. Then **stop and wait**.

---

## 4B. WORKSTREAMS — Phase B, after Tom's approval

Shape only. §5's answers set the detail, and a §5 answer may delete a workstream
outright — W1 collapses if Tom picks the `lead`-row option. Do not start any of these
during Phase A.

### W1 — The play object and the plan load
Create whatever Q1 decided; load the 716 CSV rows into it with owner, date, motion,
account, lead product and script. Idempotent: re-running replaces, never duplicates.
Match the 153 accounts to `org`, creating what is missing — expect to create nearly all
of them (§2.5: 13 of 197 orgs carry a `shopify_customer_id`).
**Acceptance:** D1.

### W2 — The frozen baseline
Snapshot, per account and per family, what each of the 153 bought in the 12 months to
2026-08-31. This is the thing every win rule compares against, so it is written once and
never updated. It is a dated evidence snapshot in the `Sales-Machine` sense.
**Acceptance:** prerequisite for D3, D4.

### W3 — Motion-aware conversion
Extend `ORDERS_Q` in `sales-leads-poll/index.ts` to fetch line items — it does not today
(§3.2). Implement the per-motion win rules from A-3 as pure functions beside
`_lib/convert.ts`, tested the way `convert.ts` is. `won` stays evidence-backed and
machine-decided; the CHECK constraint is untouched.
**Acceptance:** D3, D4.

### W4 — The Today surface
Add the growth item type to `api_read.v_sales_today` and render it in the portal beside
the existing three. Apply the §6.C cap and show what was deferred. Portal work needs a UX
handoff packet per `EXECUTION_POLICY.md`; Hebrew copy needs a Tom-approved register entry.
**Acceptance:** D2, D8.

### W5 — The scoreboard moves to the database
Repoint `q4_scoreboard.py` from the CSV to the live tables, keeping both paths runnable
during changeover. It must reproduce the CSV's figures exactly on day zero.
**Acceptance:** D5.

### W6 — Agent declarations
Write the declaration before the agent, in `Sales-Machine/agents/`, per that directory's
README and the `AGENT_TEMPLATE.md` pattern: mission, allowed paths, writes, stop
conditions, evidence standard. Read-only only (§3.5, Q5).
**Acceptance:** D6, D7.

---

## 5. The open questions — decide these with Tom, not alone

Each carries a starting recommendation. They are genuine recommendations, not the answer;
Tom's call decides.

**Q1 — Where does a growth play live?**
*Recommendation:* a new `sales_core.play` table keyed to `org_id`, not a row in `lead`.
A lead is terminal and singular; a play is neither (§3.1). Cost: a second work object and
a Today view that unions two sources. The alternative — `lead` with `source =
'q4_existing_2026'` — is cheaper today and inherits the whole acquisition lifecycle,
including the `won` semantics that §3.2 shows are wrong for this population.

**Q2 — What exactly is a win, per motion?**
*Recommendation:* first-ever line item in the target family, measured against a baseline
frozen 2026-08-31 (§3.3). Open inside it: the depth threshold and its window. Do not
guess these — they set the reported conversion rate.

**Q3 — What stays the source of truth, the CSV or the database?**
*Recommendation:* the CSV remains the **immutable dated snapshot of the plan as
designed** (`Sales-Machine` truth rule 2: evidence is true as of its date and is
superseded, never edited). The database becomes the live state. The scoreboard then reads
the DB and must reproduce the CSV exactly on day zero — that is D5, and it is what stops
the two drifting apart silently.

**Q4 — What is the daily cap, and what happens to the overflow?**
No recommendation: this is Tom's, and it is §6.C. It cannot be skipped (§3.4, D8).

**Q5 — Which agents, at what autonomy?**
*Recommendation:* exactly two, both read-only, both declared before they run.
`retention-radar` — watches the order stream, proposes wins, writes evidence only.
`brief-composer` — the Sunday and Wednesday brief. **No drafting agent until `U-020` and
`U-021` close** (§3.5). Anything that sends stays behind the frozen flag.

**Q6 — Where does the beautiful surface live?**
*Recommendation:* the portal is the system of record and the daily surface — it is where
Avi already is (§2.1). The published artifact stays the read-only executive board for Tom
and Alex, regenerated from the DB. Two surfaces, one truth, and the artifact never
captures state.

**Q7 — What happens on 2027-01-01?** The plan ends. Does the structure survive into the
next quarter, or is this a fixed-term build? *Recommendation:* build the structure to
outlive the plan — a play is a general shape — but ship only Q4's content. Say which
parts are quarter-specific.

---

## 6. Tom's part — the complete list, nothing else is his

**A. Approve the Phase A design in writing**, naming his answer to each §5 question.
Phase B does not start without this. — 20 minutes of reading.

**B. Decide `U-021` — one contact detail for Alexander.** All 17 escalation rules end at
him and no phone, email or group exists anywhere. Until it does, every escalation path
dead-ends. — one line.

**C. Decide the daily cap per owner, and what happens to overflow** (§3.4, Q4). Avi is
3–4 calls a day; the plan averages ~8.5 items. Something is deferred every day — Tom
decides whether that is automatic and by what rule. — one decision, blocks D8.

**D. `U-020` — the materials to send.** He stated on 2026-08-31 he would upload them to
`06 · העלאות`. Until they exist, no agent drafts anything that references them.

**E. `U-030` — matcha stock: 80 bags against 74 target accounts.** Blocks the plan's lead
motion, first task 2026-09-01. Not this work's to solve, but this work should surface it
on the dashboard rather than let it be discovered account by account.

Everything else is yours to decide and do.

---

## 7. Landmines — do not rediscover these

1. **`U-011` says every lead is untouched.** It is out of date as of this week (§2.1).
   Verify state against the database, never against a status document — including this
   one, after its shelf life.
2. **Two sessions have already collided on unknown-ids in `Sales-Machine`.** The merge
   base held only `U-001`–`U-013`; parallel sessions each allocated `U-014`–`U-021`, and
   the plan's ids were renumbered to `U-022`–`U-031`. Before allocating a new `U-0xx`,
   pull `main` and take the next free number. A renumbering table sits in
   `docs/plans/2026-08-31-existing-customers-q4-masterprompt.md`.
3. **The scoreboard was silently broken for a full version.** Its offline `--selfcheck`
   passed while the report path held a `KeyError` on a key absent even in the prior
   version — because only the offline path was ever exercised. **Run both paths.** A
   green selfcheck is not evidence the tool works.
4. **`customer.amountSpent` and ShopifyQL tax columns lie** — the store is misconfigured
   `taxesIncluded=true @17%`. Only `discountedTotalSet.shopMoney`. One account shows 58
   orders and ₪0.00 spend (`U-009`).
5. **Private-label SKUs are not GT's to sell.** `GTCC-NON-SAN-*` is Nonomimi's,
   `GTEL-BAB-*` is Babka's. A previous revision offered ₪168,418 of other people's
   branded product to their competitors — in the SKU **and** in the script copy, and
   fixing the SKU did not fix the copy. Gate both surfaces.
6. **`psql` does not work from this environment** — egress is restricted to the agent
   proxy. Use the Supabase MCP `execute_sql`. Large results auto-save to a file.
7. **A win and a signal are different things**, and the plan's own data proves it: 6 of 7
   current signals are `מאצ'ה — עומק`, accounts that already buy matcha. Never book
   run-rate from a signal.
8. **The plan CSV's first column carries a BOM.** Read it `utf-8-sig` or `תאריך` will
   `KeyError`.
9. **Do not `git add -A` or `git add .`** — a stop condition, not a style note. Stage
   named paths.
10. **Jerusalem rides the Wednesday delivery run**, not the centre run — measured from
    1,776 LionWheel deliveries. Route day is measured, never inferred from geography.

---

## 8. Halt conditions — additions only

The inherited set is cited in §0. **In addition, HALT and surface to Tom when:**

- Phase B would begin without Tom's written §5 answers.
- Any change would let a human set `status = 'won'`, or would relax
  `lead_won_requires_evidence`.
- Any design would mark a plan account converted on an order that contains nothing new
  to that account (D4).
- An agent would send, schedule or queue anything a customer receives — regardless of
  the flag's value.
- The knowledge base is not verified and an automation is requested anyway
  (`Sales-Machine/CLAUDE.md` stop condition 3).
- Work would touch factory-os core: `stock_ledger`, `balance_anchors`, `bom_*`, `items`,
  `components`. Catalog reads go through curated views only.
- The 153 accounts would be written to Shopify, Green Invoice or LionWheel in bulk.

---

## 9. Final report — Hebrew, short, honest

1. What a stranger can now watch working, end to end — the actual click path.
2. Each condition `A1`–`A4` and `D1`–`D8`: ✅ or ❌ with its evidence pointer. **No
   partial credit.** A ❌ with a reason is a better report than a ✅ with a caveat.
3. The numbers: rows loaded, tasks visible, wins detected, human entries required.
4. The artifacts and where they are.
5. What is still Tom's, and what is genuinely unfinished.
6. The single next action.

If anything is not ready, say so first and plainly. `EXECUTION_POLICY.md` verdict tokens
apply; `"it should work"` is not evidence.
