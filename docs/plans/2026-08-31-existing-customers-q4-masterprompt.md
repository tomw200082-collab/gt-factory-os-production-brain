# MASTERPROMPT — the Q4 growth plan: 153 customers, named owners, one action a day

**STATUS: SHIPPED — 2026-08-31**

> **Usage (Tom):** paste this whole file as the first message of a fresh Claude Code
> session with `gt-factory-os-production-brain`, `Sales-Machine` and `gt-factory-os`
> attached, and the Supabase, Shopify, Google Calendar and Gmail connectors on. It turns
> the growth board from a list of 153 opportunities nobody owns into a dated plan running
> to 2026-12-31, with a named person on every account and a number on every week. It halts
> for you only where §6 says.
>
> **Provenance:** written 2026-08-31 from the artifact `לוח הצמיחה — לקוחות קיימים`
> (`https://claude.ai/code/artifact/196e8803-7c72-4c83-8637-e4d821d03f44`, built
> 2026-08-30), whose 153 rows were parsed directly and re-aggregated — every figure in §2
> is computed, not quoted. Method and correctness gates: the artifact's own
> `שיטה` section. Fact-table method: `Sales-Machine/recipes/sales-report.md`. Churn
> definitions: `Sales-Machine/recipes/sleeping-radar.md`. People and weekly rhythm:
> `docs/ceo/reference/people_rhythm.md`.
>
> **Shelf life:** §2 is presumed stale after 2026-09-30 — the underlying window is a
> trailing twelve months and it rolls. Re-run §2.5. If the totals have moved more than
> ~5%, **rebuild the fact table before planning**; the plan is only as good as its base.

---

## 0. How to work

- **Who you are here:** one Claude Code session, frontier model. You hold Supabase (read),
  Shopify (read), Google Calendar and Gmail, and the repos. You may build the plan, the
  scoreboard, the calendar and the collateral briefs. You may **not** contact a customer,
  offer a discount, or commit anyone's time without saying so plainly to Tom first.
- **Read first, in order:** `gt-factory-os-production-brain/CLAUDE.md` ·
  `Sales-Machine/CLAUDE.md` → `CURRENT_STATE.md` → `doctrine/decisions.md` ·
  `Sales-Machine/recipes/sleeping-radar.md` and `recipes/account-value.md` — **their
  definitions govern; do not invent a churn or value rule** · the artifact in full,
  including its `שיטה` section · `docs/ceo/reference/people_rhythm.md`.
- **Authority:** the repos' `CLAUDE.md` files win. Halt conditions, evidence standard and
  git discipline are inherited — §8 lists only the additions.
  **`SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` is `false`.** Nothing in this plan is sent by
  a machine. People send; the plan tells them who, when and what.
- **The standard.** Tom asked, on 2026-08-31, for a serious Gantt running to year-end with
  tasks assigned to named people and clear targets — his words:
  `רשימת משימות מדהימה עם גנט, ממש ממש ממש רציני, עד סוף השנה, לפי משימות לאנשים עם יעדים ברורים`
  — and he gave a full mandate to decide who does what. Three prohibitions:
  1. **No task without a named person and a date.** "The team will follow up" is not a task.
  2. **No target without the arithmetic that produced it**, and without the assumption that
     would make it wrong.
  3. **No customer-facing play without the collateral it needs already listed**, with a
     status. A plan that assumes a document that does not exist is a plan that stalls in
     week two.
- **Language:** this document is English; data literals stay in their own script in
  backticks. The plan Tom and the team read is **Hebrew**. **Output language: concise
  Hebrew for Tom, concise English otherwise.**

---

## 1. Mission and definition of done

**One testable sentence:** every one of the 153 customers has an owner, a play, a dated
first touch and a follow-up rule between 2026-09-01 and 2026-12-31 — and on any given
morning each of Tom, Alex and Avi can open one screen and see exactly who they contact
today and what they say.

| # | Condition | The observation that would prove it false |
|---|---|---|
| D1 | All 153 customers are assigned; the assignment rule is written and mechanically reproducible | Re-run the rule; any customer unassigned or assigned differently = fail |
| D2 | A dated task list exists covering every working day 2026-09-01 → 2026-12-31, with a named owner per task | Pick any working day; if it has no tasks or a task has no owner = fail |
| D3 | A Gantt view exists showing phases, dependencies and the collateral each phase needs | Any phase whose blocking collateral is not named with a status |
| D4 | Targets exist at company, person and month level, each with its arithmetic and its stated assumption | A target with no derivation = fail |
| D5 | Every play type has its collateral listed with a status: exists / being built / **does not exist** | A play whose material is unlisted, or listed as existing when it does not |
| D6 | The scoreboard is a live query over the fact table, not a hand-maintained sheet | The weekly number cannot be regenerated from source in one command |
| D7 | Phone coverage is measured and a capture plan exists for the gap | `153 customers have no phone in Shopify` is still true at the end with no plan against it |
| D8 | Tom, Alex and Avi each have recurring calendar blocks that match the plan's daily volumes | Open the calendar; a person carrying 19 accounts with no block = fail |

Anything not on this list is out of scope unless Tom asks.

### 1.1 Settled — do not reopen

- **The growth board's numbers are the base.** They passed five correctness gates on
  2026-08-30: monthly reconciliation `−0.150%` against ShopifyQL `total_sales` (threshold
  `±0.5%`), order counts exact `24/24` months, SKU coverage `203/203`, five anchors
  identical to the `2026-08-24` evidence, manual sanity `3/3`. **Do not rebuild the fact
  table to "check".** Re-run it only if §2.5 shows material drift.
- **Alex and Avi take the large accounts; Tom takes the small ones.** Tom's instruction,
  2026-08-31. The threshold is decided in §2.3; the split is not.
- **The board's opportunity model.** Depth = under-buying a family they already buy, versus
  the median share among comparable buyers. Breadth = not buying at all where ≥30% of
  comparable businesses do, capped at the 90th percentile of what the strongest comparable
  actually pays. Replacement = their own `MUZA` spend, which is the only line that is the
  customer's own money rather than an estimate. Comparison groups are **menu archetypes,
  not size** — `TEA-ONLY`, `SPECIALTY-LED`, `MIXED`, `BAR-LED`.
- **The scoring weights are `inferred`, not measured** — depth `1.0`, breadth with mutual
  pull `0.7`, other breadth `0.4`. The board says so itself. **Correct them from real
  outcomes after week 4**; that is a task in this plan, not a caveat.
- **Gross margin factor `0.809`** — the mean across the 48 drinks under the `2026-08-27`
  cost model.

---

## 2. Ground truth — computed 2026-08-31 from the board's own rows

### 2.1 The whole book

Source for every figure in §2.1–§2.3: the 153 `data-rev` / `data-ev` / `data-hole`
attributes on the growth board's own rows, parsed and re-aggregated 2026-08-31. The board
was built 2026-08-30 from `build_facts.py` over a Shopify Bulk export of 33,606 objects.

| | Customers | 12-month revenue | Identified opportunity/yr | `MUZA` hole |
|---|---|---|---|---|
| **All** | **153** | **₪2,886,079** | **₪776,534** | **₪192,147** |

By play type: `replacement` 19 accounts / **₪292,807** · `depth` 58 / **₪191,960** ·
`breadth` 76 / **₪291,767**.
By archetype: `TEA-ONLY` 81 · `SPECIALTY-LED` 44 · `MIXED` 25 · `BAR-LED` 3.
Chains: **29**. Revenue distribution: 4 accounts above `₪100k`, 11 above `₪50k`, 22 above
`₪25k`, 63 above `₪10k`; **median `₪8,045`**.

### 2.2 The `MUZA` hole — the most time-sensitive money in the company

GT withdrew the `MUZA` cocktail line. **20 customers, 21 replacement lines, ₪192,147/year**
of spend that has simply stopped, leaving a hole in a live menu. This is the only category
where the number is the customer's own historical spend rather than a comparison estimate,
and the only one where the customer has a problem **right now** whether or not GT calls.

`79%` of it (**₪151,189**) sits inside the large-account bucket. The largest single line is
`נונומימי` at `₪27,705` across 11 branches.

**And it has no collateral.** `UNRESOLVED U-014`: no drink page, no documented preparation
spec exists for any cocktail base at GT — the catalog deliberately excludes cocktails (Tom,
`05/08`). Twenty conversations worth `₪192k` currently happen with nothing to send. **This
is the binding constraint on the highest-value play in the plan**, and closing it is
§6.B / `docs/plans/2026-08-31-category-menus-masterprompt.md` §6.E.

### 2.3 The split — decided here, reproducible in code

**Rule: an account is `גדול` if it is a chain (`data-chain=1`) OR its trailing-twelve-month
revenue is `≥ ₪25,000`. Everything else is `קטן`.**

| Bucket | Accounts | 12m revenue | Opportunity | `MUZA` hole | Owner |
|---|---|---|---|---|---|
| `גדול` | **37** | ₪1,959,803 (68%) | ₪480,829 (62%) | ₪151,189 (79%) | Alex + Avi |
| `קטן` | **116** | ₪926,276 | ₪295,705 | ₪40,958 | Tom |

Why revenue **or** chain, rather than revenue alone: a chain is a multi-branch decision
with a purchasing process, and it is worth a partner's time even when one branch is small —
`סטקיית הבוקרים` bought `₪1,284` and carries a `₪24,728` opportunity; `מנדרין` bought
`₪16,007` and carries `₪18,671`. Both are chains, and neither is a WhatsApp message.
Why `₪25,000`: it sits just above the 75th percentile (`₪15,528`), it captures 68% of
revenue in 24% of accounts, and it leaves each partner **18–19 accounts** — a book a person
can actually hold in their head.

**Asymmetric accounts to flag by name** — opportunity far exceeding current revenue, which
is where the plan's upside actually lives: `גאפן גאפן` (`₪30,419` → `₪57,774`) ·
`סטקיית הבוקרים` (`₪1,284` → `₪24,728`) · `מנדרין` (`₪16,007` → `₪18,671`) ·
`ויוינו` (`₪86,056` → `₪30,202`).

### 2.4 What does not exist yet

No owner on any account. No dates. No targets. No scoreboard. No follow-up rule. No
cocktail collateral (§2.2). **No phone numbers for 153 customers in Shopify** — the board's
own footer; a call plan that does not solve this stalls on day one. `Avi` does not appear in
`docs/ceo/reference/people_rhythm.md` at all — his hours, contact and capacity are unknown
(§6.A). `UNRESOLVED U-015`: 19 brand groupings await Tom's approval, which changes whether
some rows are one conversation or several.

### 2.5 Re-verification block

```sql
-- has the trailing-12m base moved materially since 2026-08-30?
-- rebuild via gt-factory-os/scripts/sales-report/build_facts.py, then compare the three
-- headline figures to §2.1. >5% drift on any of them ⇒ rebuild before planning.

-- phone coverage, the constraint on the call plan
select count(*) filter (where phone is null or phone = '') as no_phone, count(*) as total
from sales_core.org;
```
Also re-read the artifact — Tom may have annotated rows since 2026-08-30.

---

## 3. What the hard part actually is

**Reframe 1 — the analysis is finished and that is the trap.** The board is genuinely
excellent: 153 accounts, each with an opening line, a close, objection handling and a
fallback, all built on a fact table that passed five gates. It has produced exactly zero
revenue, because **there is no calendar**. Nobody owns an account, no day has a list, no
week has a number. Every hour spent improving the analysis is an hour not spent on the only
missing artifact. If you find yourself refining the opportunity model before a single day
has an owner, stop — that is the failure mode this document exists to prevent.

**Reframe 2 — this is a logistics plan wearing a sales plan's clothes.** The board's own
closing move is `אני מוסיף … למשלוח הקרוב. אותה עגלה, אותו מקרר` — add it to a delivery
that is already going. That makes the delivery calendar the spine of the plan, not the
sales calendar. Routes run **Sun / Mon / Thu — centre · Tue — north · Wed — south**
(`people_rhythm.md`). A northern customer contacted on Wednesday waits six days for a
truck; contacted on Sunday, they are served on Tuesday. **Sequence contacts by route day.**
This one change is worth more than any script rewrite and costs nothing.

**Reframe 3 — September is the wrong month for the pitch this plan wants to make, and the
right month for a different one.** The Jewish holidays fall in September–October 2026 and
HoReCa runs at peak through them. A café owner does not redesign a menu in their busiest
fortnight. **Verify the exact 2026 dates against a calendar — do not assume them** — then
split the season: through the holidays the message is *stock up, do not run out*; after
Sukkot it becomes *let us add a line*. The `MUZA` replacement is the exception and runs
immediately, because those customers have a hole in their menu **during** the peak, which
is precisely when it hurts most and when they will act.

**Reframe 4 — capacity is smaller than it looks.** `דורין`, who handles customers and the
office, is going on maternity leave and Tom is covering her (`people_rhythm.md`, and the
digital roadmap's `wa1` note). Tom is therefore taking on 116 accounts *and* Doreen's desk.
Wednesday is already consumed by planning (13:00 Alex, 15:00 production lock). Build the
plan against **realistic daily volumes**, not aspirational ones, and put Tom's block
somewhere it survives a bad day. A plan that needs a good week to work is a plan that dies
in the first bad one.

**Reframe 5 — measure to the order, and correct the model.** The scoring weights are the
board's own admitted `inferred` assumption. After four weeks there will be real outcomes:
which play type actually converted, in which archetype, at what rate. Feed that back and
re-rank. A plan that cannot learn from its first month is a forecast, not a plan.

---

## 4. Workstreams

### W1 — Assign, and make the assignment reproducible

Apply §2.3 in code against the board's rows. Emit
`Sales-Machine/evidence/2026-09-01-q4-assignment.md`: every account with owner, bucket,
play type, archetype, opportunity, current revenue, chain flag, days since last order, and
its route day derived from its city.

Split the 37 large accounts between Alex and Avi. Split by **archetype and geography**, not
alphabetically — one person who owns all `SPECIALTY-LED` accounts gets fluent in that
conversation by the fifth call, and a person driving one route in a day beats two people
crossing paths. Balance to within ~10% on opportunity value so neither book is obviously
the good one.

**Acceptance:** D1.

### W2 — Close the phone gap (a prerequisite, not a footnote)

153 customers have no phone in Shopify. Before any call plan is credible:
1. Cross-reference Green Invoice, LionWheel delivery records and the customer-notes store —
   the number very likely exists in one of them already.
2. For what remains, produce a capture list `דורין`/the office can fill from order history
   and delivery contacts.
3. Write what you find back through the proper path — **never by editing customer records
   by hand in two systems** — and record coverage before and after.

Share whatever you build with
`docs/plans/2026-08-31-lead-response-system-masterprompt.md` §W2, which hits the identical
wall. Build the enrichment once.

**Acceptance:** D7.

### W3 — Collateral, per play type, with honest status

The table Tom asked for. Fill it, and mark `לא קיים` where that is the truth:

| Play | Accounts | ₪/yr | Material needed | Where it comes from | Status |
|---|---|---|---|---|---|
| `MUZA` replacement | 20 | 192,147 | `סנגריה` drink page · prep spec · a one-page `החלפת מוזה` sheet per branch | **`U-014` — no cocktail spec exists at GT** | **`לא קיים` — blocking** |
| Depth | 58 | 191,960 | the family's category menu | `2026-08-31-category-menus-masterprompt.md` | being built |
| Breadth | 76 | 291,767 | category menu + recipe card + "what the bar already needs to own" | same | being built |
| Powder plays (`מאצ'ה`/`אובה`) | — | — | equipment bundle sheet — powders need a whisk or frother and milk | **does not exist** | to build |
| Chains (29) | — | — | a one-page multi-branch proposal template | **does not exist** | to build |
| All | 153 | — | wholesale price list | artifact `b11dd7cf` | exists |
| All | 153 | — | per-customer script | the growth board itself | exists |

Then **build the two that are yours** (the equipment bundle sheet and the chain proposal
template) and escalate the cocktail gap as §6.B. Do not start a `MUZA` conversation with
nothing to send.

**Acceptance:** D5.

### W4 — The plan itself: phases, then days

Five phases, sequenced by value and by season. Verify the holiday dates first.

| Phase | Window | Who | What | Why then |
|---|---|---|---|---|
| **A — Pre-flight** | Sep 1–10 | all | assignment, phones, collateral, calendar blocks, `U-015` groupings | nothing outbound starts without an owner and something to send |
| **B — `MUZA` blitz** | Sep 7 – Oct 15 | Alex + Avi (16), Tom (4) | all 20 replacement accounts, `₪192k` | they have a hole now, in their peak season. Every week is spend going to a competitor |
| **C — Holiday stock-up** | mid-Sep – post-Sukkot | Tom (bulk), partners on chains | *do not run out* on what they already buy | the only message that lands in peak. Cheap, high-yield, warms every account for phase D |
| **D — Depth** | Oct 15 – Nov 30 | Alex + Avi big, Tom small | 58 accounts under-buying a family they already stock | no new SKU, no new equipment, no new decision — the shortest sell in the book |
| **E — Breadth** | Nov 1 – Dec 24 | Tom bulk, partners on the top 15 | 76 accounts, `₪292k` | the longest sell; it needs the menus finished and a calmer season |
| **F — Year-end close** | Dec 1–31 | all | reorders, unclosed follow-ups, next-year openers | the last delivery slots and the annual budget conversation |

Then explode it to days. Working days are **Sunday–Thursday** — never set a date on Friday
or Saturday. Sequence every contact against its **route day** (§3, reframe 2).

**Daily volumes — deliberately conservative:**

| Person | Daily | Slot | Weekly reach |
|---|---|---|---|
| **Tom** | 10 WhatsApp | one 30-min block, before 09:30 or after 16:00 — not mid-day, and not Wednesday | 50 |
| **Alex** | 3 calls | his own time; Wednesday's 13:00 meeting is already booked | 15 |
| **Avi** | 3 calls | to be set once §6.A answers his hours | 15 |

At that rate a first pass over Tom's 116 accounts takes ~12 working days, and the partners
cover 37 accounts in ~7. Both fit inside phase B/C with room for follow-ups — which is the
point of picking volumes that survive a bad week.

**Follow-up rule, one rule, no exceptions:** touch 1 → +3 working days → touch 2 (different
content, never a repeat) → +7 working days → touch 3, the closing-the-loop message. Then
stop and mark the outcome. Three touches, then the account moves to the next phase's list
or to `לא עכשיו` with a date to revisit. **Any customer reply or order cancels all
remaining scheduled touches** — the same expensive bug the lead system has to avoid, and it
is worse here because these are people who already pay GT.

**Acceptance:** D2, D3.

### W5 — Targets, with their arithmetic exposed

Model — opportunity per play type is summed from the board's rows (§2.1); every
conversion rate is `inferred` by this document and labelled as such, to be corrected in W7.
Won run-rate is `opportunity × rate`, and the total `₪200,125` is the sum of that column:

| Play | Opportunity/yr | Assumed conversion | Won run-rate |
|---|---|---|---|
| replacement | ₪292,807 | 40% — they have a hole, GT has the substitute, it rides an existing delivery | ₪117,123 |
| depth | ₪191,960 | 25% — no new decision, just more of what they buy | ₪47,990 |
| breadth | ₪291,767 | 12% — a new line is a real decision | ₪35,012 |
| **Total** | **₪776,534** | | **₪200,125/yr** |

Stated two ways, because they answer different questions:
- **New annualised run-rate secured by 2026-12-31: `₪200,125`.** That is what the year
  gains going forward.
- **Revenue actually invoiced Sep 1 – Dec 31: `₪33,000` – `₪67,000`.** Four months is
  `4/12` of a year, and closes land through the period rather than on day one — so the
  band runs from a 50%-ramped `₪33k` to a full-period `₪67k`. Gross margin at `0.809` puts
  that at roughly **`₪27k`–`₪54k` of gross profit**.

**The assumption that would make this wrong:** the conversion rates. They are a model, not
a measurement. If replacement converts at 15% rather than 40%, the run-rate figure falls by
about `₪73k`. Say that out loud in the plan — a target nobody believes is worse than no
target.

Break it down per person (Alex/Avi share `₪480,829` of opportunity; Tom `₪295,705`) and per
month, weighted to the phases rather than spread flat.

**Acceptance:** D4.

### W6 — The scoreboard

A query, not a spreadsheet. Weekly, over the fact table plus `sales_core` events:
accounts touched · replies · orders containing a target SKU · new run-rate won ·
`MUZA` accounts closed of 20 · conversion by play type and by archetype.

Surface it where the week already stops: the **Sunday** cash-and-budget picture Tom and
Alex already receive, and the **Wednesday 13:00** meeting with Alex. Do not create a new
meeting. A plan that needs a new recurring meeting to survive will not survive.

**Acceptance:** D6.

### W7 — Correct the model after week 4

Around 2026-10-05, recompute the weights from real outcomes and re-rank the remaining
accounts. The board itself asks for this, in its own method section:
`המשקלים הם הנחת מודל (inferred), לא מדידה — הם מוצגים כאן כדי שסשן עתידי יתקן אותם מתוצאות אמת.`
Put the date in the calendar as a task with an owner.

### W8 — Calendar and delivery

Create the recurring blocks (§6.C to confirm), the phase milestones, the week-4 correction,
and the year-end close. Publish the plan as an artifact in the same idiom as the growth
board so Tom, Alex and Avi open one link and see today.

**Acceptance:** D8.

---

## 5. Scope

**IN:** everything in §4.

**OUT — do not touch, do not "improve":**
- **Contacting any customer.** The flag is `false`. You produce lists, scripts, dates and
  materials. People send.
- Rebuilding the fact table, unless §2.5 shows material drift. Five gates passed on
  2026-08-30.
- Redefining churn or account value — `Sales-Machine/recipes/` owns those.
- Discounts and pricing. Alex approves discounts (`people_rhythm.md`); nothing in this plan
  offers one, and the board's own framing is deliberate:
  `אין הנחה, אין דוגמית, אין מחיר ניסיון.` The close is adding to a delivery already going out.
- New lead acquisition — a different document.
- Building the category menus — you specify what is needed and consume them.
- factory-os core.

---

## 6. Tom's part — the complete list, nothing else is yours

**A. `Avi` — who he is, in the system.** He is not in `people_rhythm.md` at all: no hours,
no email, no portal user, no capacity. He is being handed ~19 accounts worth roughly
`₪240k` of opportunity. Give: hours, contact, whether he has portal access, and how many
calls a day is realistic. **The plan cannot be dated for him without this.** ~5 minutes,
and it blocks W1.

**B. The cocktail collateral — the `₪192,147` decision.** `סנגריה` is the `MUZA`
replacement for 20 customers and GT has **no drink page, no preparation spec, nothing to
send**, because the catalog excludes cocktails by your decision of `05/08` (`U-014`).
Either commission it (it belongs in
`docs/plans/2026-08-31-category-menus-masterprompt.md` §6.E) or accept that phase B runs on
a phone call and a price. **This is the single highest-value unblock in the whole war
room.** ~10 minutes to decide, days to produce — so decide first.

**C. Confirm the daily volumes and the blocks.** 10 WhatsApp messages a day for you, 3
calls a day each for Alex and Avi, Sunday–Thursday. If that is wrong, say so now — every
date in the Gantt derives from it. And confirm you are willing to hold a 30-minute block
while also covering `דורין`'s desk.

**D. Approve the split rule** — chain **or** `≥ ₪25,000` = large. It puts 37 accounts with
the partners and 116 with you. If you would rather draw it at `₪15k` or `₪50k`, say the
number and the plan recomputes.

**E. Decide `U-015`** — the 19 brand groupings. It changes whether some rows are one
conversation or five, which changes both the workload and the script.

**F. Tell Alex and Avi.** No plan survives a person discovering on Sunday that they own 19
accounts. One conversation each, before Sep 1.

**G. Confirm the conversion assumptions**, or replace them with your own. You have sold to
these customers for years; your instinct on "how many of the 20 `MUZA` accounts will
actually take sangria" is better data than any model.

---

## 7. Landmines — do not rediscover these

1. **The `MUZA` hole is a decaying asset.** Twenty customers have a gap in a live menu
   during their busiest season. Every week without a call is a week they find someone
   else's product — and once a competitor's bottle is on that shelf, the `₪192,147`
   becomes a switching sale instead of a replacement, at a fraction of the conversion rate.
   Phase B before phase D, always.
2. **`customer.amountSpent` and ShopifyQL `average_order_value` are banned** — documented
   anomalies, and one account shows 58 orders against `₪0.00`. Every number comes from the
   fact table. `Sales-Machine/recipes/sales-report.md`.
3. **Shopify is misconfigured as `taxesIncluded=true @17%`**, so its tax/net/gross columns
   subtract a fictional tax. The stored line price is ex-VAT and that is the base the board
   uses. A margin computed off the wrong base looks plausible and is wrong by ~17%.
4. **Month attribution is `Asia/Jerusalem`, not UTC.** Get this wrong and the scoreboard
   will not tie to ShopifyQL and you will spend a day proving the fact table is broken when
   it is not.
5. **Route days are the close.** Sun/Mon/Thu centre · Tue north · Wed south. Contacting a
   northern account on Wednesday costs six days of momentum. Sequence to the truck.
6. **Wednesday is gone.** Counts in the morning, Alex at 13:00, production lock at 15:00.
   Do not schedule outbound work into it.
7. **`דורין` is going on maternity leave** and Tom is covering her desk. Any plan that
   assumes Tom's normal capacity is already wrong on the day it ships.
8. **A chain is not one conversation and it is not `N` conversations.** `נונומימי` is 11
   branches; the board flags which branches lag the chain's own cadence. A chain call is
   about the chain, and then a branch-level list — and `U-015` decides where that line
   falls for 19 of them.
9. **`אובה` never stands alone.** All five of its drinks need a second GT product, so an
   `אובה` breadth play at an account that buys nothing else is not a sale, it is a returned
   box. It is an expansion after matcha, or a bundle.
10. **The board's opportunity figures for depth and breadth are *estimates* from comparison
    groups; only replacement is the customer's own money.** Never quote a depth or breadth
    number to a customer as if it were their spend. The board is careful about this in its
    own wording; the plan must stay as careful.
11. **153 customers have no phone.** Any plan that starts with "call them" fails on the
    first morning unless W2 ran first.

---

## 8. Halt conditions

Inherited from `gt-factory-os-production-brain/CLAUDE.md` §Stop conditions and
`Sales-Machine/CLAUDE.md`. Additions:

- Any message would reach a real customer → **STOP**. The flag is `false`.
- A plan step would offer a discount or a special price → **STOP**. Alex's, not the plan's.
- The fact table would be rebuilt without §2.5 showing drift → **STOP**; you are about to
  spend a day re-proving something that passed five gates last week.
- A customer would be told a depth or breadth figure as though it were their own spend →
  **STOP**.
- A date lands on a Friday or Saturday → **STOP** and reschedule.

---

## 9. Final report — Hebrew, short, honest

1. What Tom, Alex and Avi each open on Sunday morning, and what it tells them to do.
2. D1–D8 ✅/❌ with evidence pointers. No partial credit.
3. The numbers: accounts assigned per person · working days planned · run-rate target and
   in-period band with their assumptions · collateral ready vs missing.
4. The artifacts, and where they are.
5. What is still Tom's, and what is genuinely unfinished — lead with §6.B if it is still
   open, because it is the largest number in the document.
6. The single next action.

Then stamp this file `STATUS: SHIPPED — <date>` with evidence pointers, and commit.

---

## 10. Execution record — 2026-08-31

Executed in one session. Every §2 figure was recomputed from the board's own 153 rows
before planning; **10/10 reproduced exactly** (`153` accounts · `₪2,886,079` revenue ·
`₪776,534` opportunity · `₪192,147` hole · the `37`/`116` split with its three sub-totals ·
`29` chains). §2.5 showed no drift — the board was one day old — so the fact table was
**not** rebuilt, per §8.

### D1–D8

| # | Verdict | Evidence |
|---|---|---|
| D1 | ✅ | `Sales-Machine/evidence/2026-08-31-q4-assignment.md` — all 153 assigned by a rule stated in code; re-running `plan.py` on the same inputs reproduces it byte for byte |
| D2 | ✅ | `evidence/2026-08-31-q4-daily-plan.csv` — 740 dated tasks over all 84 working days; 0 empty days, 0 tasks without an owner, 0 on Fri/Sat/holiday/eve |
| D3 | ✅ | Gantt in the artifact: 6 phases, blocked days hatched, each phase's blocking collateral named with status |
| D4 | ✅ | §W5 targets reproduced (`₪117,123` + `₪47,990` + `₪35,012` = `₪200,125`); in-period `₪40,341` derived per-close-date, inside the stated `₪33k`–`₪67k` band; sensitivity `−₪73,202` |
| D5 | ✅ | Collateral table with honest status; the two owed pieces built — `evidence/2026-08-31-q4-collateral/` |
| D6 | ✅ | `gt-factory-os/scripts/sales-report/q4_scoreboard.py` — one command, live-verified against Shopify 2026-08-31, `--selfcheck` 9/9. Method: `Sales-Machine/recipes/q4-scoreboard.md` |
| D7 | ⚠️ **partial** | Coverage measured (`0/153` in the board; `156/196` in `sales_core.org`, a different population). Capture plan is dated in phase A (06/09, 07/09) but **not yet executed** — no phone was written anywhere |
| D8 | ⚠️ **partial** | 8 events created on `tom@gteveryday.com` (daily block, Sunday scoreboard, §6 gate, B/D/E starts, W7, year-end). **Alex and Avi have none** — no calendar access, and Avi's address is unknown (§6.A) |

### Corrections to this document, made by the work

1. **Tom's weekly reach is 40, not 50.** §W4 assumed five days and its own landmine 6 says
   Wednesday is gone. Four days × 10 = 40. The "~12 working days for a first pass" figure
   still holds — 12 is days, not weeks.
2. **Route day is now measured, not assumed.** 1,776 LionWheel deliveries since 2026-05-10
   (`private_core.orders_mirror`) matched **151 of 153** accounts to a real delivery weekday.
   The largest surprise: **Jerusalem rides the Wednesday (south) run** — 40 of 46 deliveries —
   not the centre run.
3. **2026-10-27 is Election Day, a public holiday**, and falls on a Tuesday. It was not in
   §W4 and would have put a full northern route day on a closed country.
4. **Hanukkah 2026-12-05 → 12-12 is not a block.** Observances, not public holidays, and a
   HoReCa peak. Phase E and F run straight through it.
5. **The scoreboard needed a semantic fix §W6 did not anticipate.** "Ordered the target SKU"
   is a *signal*, not a win — a depth account already buys that family. The run-rate is
   booked only from an outcome a human marked `זכה`. Without this every depth account would
   have counted as won in week one.
6. **The split lands 21/16, not 18/19.** §W4 asked for balance within ~10% *on opportunity
   value*; that rule gives `₪239,446` / `₪241,383` — a **0.8%** gap. Account counts were not
   the stated criterion, and equalising them would unbalance the money.
7. **The sleeping radar comes back clean:** 0 silent accounts, 13 off-pace. These 153 are
   buying. This is a growth plan, not a churn-recovery plan.

### Opened as UNRESOLVED

`U-016` `פתאל` and `ליאוני` have no LionWheel delivery since 2026-05-10 — route day defaulted,
not measured (`₪71,582` combined revenue) · `U-017` Avi is absent from `people_rhythm.md`;
his 16 accounts are dated on an assumed 3 calls/day · `U-018` chains spanning regions
(`גאפן גאפן`: Ashkelon, Jerusalem, Netanya) carry one dominant route day, which is wrong at
branch level.

### Still Tom's, in order of money

**§6.B first — `₪192,147`.** Phase B opens 2026-09-07 and there is still no `סנגריה` drink
page and no preparation spec (`U-014`). Then §6.A (Avi, blocks every date he owns), then
§6.C/D/E/G, then §6.F before 2026-09-01.

### Not done, and why

Nothing was sent to a customer — `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` is `false`.
No phone number was written to any system: W2 produced the measurement and the dated capture
plan, not the enrichment, because writing contact data back is a task with an owner and a
path, not a side effect of planning. The two sibling masterprompts this document leans on
(`2026-08-31-category-menus-masterprompt.md`, `2026-08-31-lead-response-system-masterprompt.md`)
**do not exist in `docs/plans/`** — the depth and breadth collateral has no written source yet.

### Artifacts

`https://claude.ai/code/artifact/39c9dc45-7e50-487e-8013-f255f1b84de7` — the one screen.
`Sales-Machine/evidence/2026-08-31-q4-plan.md` · `-q4-assignment.md` · `-q4-daily-plan.csv` ·
`-q4-collateral/` · `Sales-Machine/recipes/q4-scoreboard.md` ·
`gt-factory-os/scripts/sales-report/q4_scoreboard.py`.

---

## 11. Revision 2 — 2026-08-31, after Tom's corrections

Tom returned four corrections and a mandate. All four landed; the plan was rebuilt,
not patched.

### What he corrected

1. **Avi has no defined role or hours, and he is already in the system.** Found:
   `private_core.app_users` → `avi@gteveryday.com`, display_name `Avi`, role `planner`,
   active since 2026-08-25, portal password set. 3–4 calls a day. `U-017` closed.
2. **GT no longer produces cocktails or mixers.** The only alcohol GT markets that is
   not another customer's private label is GT Pink and GT White Sangria. White was then
   dropped (zero stock, Tom's call). §W3 and §2.2 of this document were written on the
   assumption that "sangria" was a single available answer; it was not.
3. **§6.D approved** — chain or ≥ ₪25,000. §6.C, §6.E approved. §6.B given to Claude on
   mandate. §6.G deferred. §6.F becomes: build the artifact, Tom sends it.
4. **All MUZA is gone** — mixers included — so the replacement is GT's sangrias *or*
   tea extracts as a mixer, and deciding which was explicitly a commercial judgement.

### The judgement, and the arithmetic behind it

The extract leads; the sangria is the fallback. MUZA averaged **₪81.60/L**. Pink Sangria
is ₪45, a tea extract ₪65 — so a like-for-like litre swap can return **₪143,891** of the
₪192,147, never the whole of it, and it reaches that ceiling only if the extract carries
the play. On GT's own documented 50 ml build (`docs/pricing/canva_workfiles/recipes.json`)
a ₪65 litre is **20 serves**: ₪3.25 of GT plus ~₪7 of the venue's own spirit is ₪10.25 of
pour cost against MUZA's ₪13.10 — **23% food cost against 29%**. The venue keeps more per
glass than MUZA left them, and one bottle now serves the iced-tea menu, the bar, and the
zero-proof list. MUZA served one. Tom named FRESH and CALM specifically because both are
caffeine-free, which is what lets the same bottle work at eight in the evening.

Three motions, ordered by how short the sell is — M1 same bottle, evening menu (zero new
SKU, the shortest sell in the whole plan) · M2 extract as the cocktail base · M3 Pink
Sangria for whoever wants nothing to prepare.

### The defect this uncovered

The growth board pointed **37 opportunity lines across 35 accounts — ₪168,418 —** at
`GTCC-NON-SAN-1L` and `GTCC-NON-SAN-3.85L` (Nonomimi's own branded sangria),
`GTEL-BAB-RED-0.75L` (Babka's), and the unruled `GTCC-NM-SAN-3.85L`. Seven of the twenty
MUZA accounts, worth ₪90,553, would have been offered another customer's product by name.

Fixing the SKU field was not enough: the first render showed the WhatsApp copy for
`גאפן גאפן` still reading *"GT Nonomimi Sangria Cocktail 1000ml"*. Twenty-four script
lines were scrubbed and all twenty MUZA accounts given purpose-written openings. Two
gates in `q4_plan_v2.py` now assert both surfaces are clean.

### Structure

`עם כמה ואיזה לקוחות אלכס נפגש עם אבי` was read as joint meetings, and the plan is built
on that reading: **Alex only appears in the room with Avi.**

| | channel | accounts | 12m revenue | opportunity | target | cadence |
|---|---|---|---|---|---|---|
| T1 | joint meeting, Alex + Avi | 15 | ₪1,450,872 | ₪356,537 | **₪86,465** | one a week |
| T2 | call, Avi | 22 | ₪508,931 | ₪124,292 | ₪21,123 | 3–4 a day |
| T3 | WhatsApp, Tom | 116 | ₪926,276 | ₪295,705 | ₪40,057 | 10 a day, no Wednesday |

**₪147,644 run-rate · ₪119,444 gross profit · 755 dated tasks · 84 working days, none empty.**
Down 26% from v1, and the first figure that survives its own arithmetic.

### Newly blocking

`U-020` — **FRESH and DETOX are both at zero stock** (Shopify, verified 2026-08-31).
**79 accounts and ₪490,702 of opportunity** depend on one of them. CALM 340, NAMASTEA 353,
ENERGY 251, REVIVE 259 are ready. A production order is the first task in the plan.

`U-021` — `sales-leads-poll` `routeDaily()` selects conversion candidates with
`status in (new,working) and shopify_customer_id is not null`. Every one of the 153 is a
Shopify customer ordering every nine days on average, so loading the plan as leads would
mark all of them `won` on their next **routine** order and the target would read as met the
week it shipped. The load stays dry-run until `and l.source <> 'q4_existing_2026'` lands.

`U-019` — `GTCC-NM-SAN-3.85L` is titled "GT Sangria" but its SKU carries `NM` and
`GTCC-NON-SAN-3.85L` exists beside it. Offered to nobody until Tom rules.

### Artifacts

Dashboard (this is the one Tom sends): `https://claude.ai/code/artifact/9267cc69-a432-43d5-8e18-94b6057db483`
· `Sales-Machine/evidence/2026-08-31-q4-plan.md` · `-q4-assignment.md` · `-q4-daily-plan.csv`
· `-q4-collateral/mixer-serve-cards.md` · `-q4-collateral/muza-migration-map.md`
· `gt-factory-os/scripts/sales-report/q4_plan_v2.py` · `q4_sales_system_load.py` · `q4_scoreboard.py`

---

## 12. Revision 3 — 2026-08-31, the focus was wrong

Tom: *switching a customer off MUZA is less likely than adding matcha or ube to them.*
He was right, and this document is part of why the plan got it wrong twice.

### The document's own bias

§2.2 named the `MUZA` hole **"the most time-sensitive money in the company"** and §7 landmine 1
called it **"a decaying asset"**. Both are true about urgency and neither is true about size,
and the plan inherited the emphasis without ever testing it. §W4 sequenced `MUZA` as phase B,
ahead of everything; §W5 modelled the whole target off the board's play types — replacement,
depth, breadth — and **never once aggregated opportunity by product family**. Doing that takes
one query and it is what finally exposed the problem.

### The model was circular

Every version until now trusted the growth board's opportunity model, which prices a family
from the median of a comparison group capped at a percentile. That is sound for a family most
customers already buy, and **circular for one they do not**: matcha is under-penetrated, so
most of the comparison group does not buy it, so the model reads "few buy it" and concludes
"small opportunity". It priced matcha at **₪43,942** across the 153 accounts.

Twelve months of real orders — 3,872 of them, matched to 151 of the 153 — say otherwise:

| | buying | ₪ over 12m | the model | gap |
|---|---|---|---|---|
| tea extracts | 142 · 94% | 1,894,224 | 432,738 | ×4.4 |
| **matcha** | **73 · 48%** | **423,949** | 43,942 | **×9.6** |
| fruit purée | 45 · 30% | 94,056 | 44,494 | ×2.1 |
| ube | 23 · 15% | 19,965 | 2,537 | ×7.9 |

**Matcha is already GT's second-largest category.** 74 accounts buy tea and no matcha —
**₪351,270** priced at the median comparable buyer in the same revenue band. Six are A-band,
hold **₪202,860**, and were already in the joint-meeting lane. `R2M` alone is ₪120,726 of
revenue, entirely tea, zero matcha.

### What changed

The plan now leads with catalog expansion. **Changing a product is a decision; adding one is
an order.** MUZA is a second sentence for the 15 accounts that still buy tea, and the opening
line only for the **5 that stopped buying tea as well** — for those the account is the prize,
not a line item, which is exactly the narrowing Tom asked for.

Two gates make it mechanical rather than a matter of judgement:
`MUZA never leads a live account` — **it caught one that had slipped through** — and
`ube never a first product`, which holds §7 landmine 9.

Target: **₪147,644 → ₪262,661** run-rate, ₪212,492 gross. **No customer was added.**

### The lesson for the next masterprompt

This document supplied the plan's numbers, its phases and its emphasis, and the emphasis was
the one thing it never asked anyone to verify. §1.1 froze the board's play types as *settled —
do not reopen*, and that freeze is what kept three versions inside a model that could not see
its own blind spot. **A masterprompt should name what it wants checked, not only what it wants
left alone.** The check that would have caught this — *aggregate opportunity by product family,
then measure penetration against it* — belongs in §2.5 next to the drift query.

### Newly blocking

`U-022` — **80 matcha bags in stock against 74 target accounts.** Enough for one wave, not a
quarter. It now blocks the plan's lead motion, and it is the first task, 2026-09-01.
`U-023` — `GT-MAT-KIT` (₪170) contents are undocumented; not offered until they are.

### Artifacts

Dashboard: `https://claude.ai/code/artifact/9267cc69-a432-43d5-8e18-94b6057db483` ·
`Sales-Machine/evidence/2026-08-31-q4-plan.md` · `-q4-assignment.md` · `-q4-daily-plan.csv` ·
`-q4-collateral/matcha-business-case.md` ·
`gt-factory-os/scripts/sales-report/q4_penetration.py` · `q4_plan_v3.py`
