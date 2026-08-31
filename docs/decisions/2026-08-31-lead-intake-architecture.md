# Decision — lead intake architecture: CTWA, the lead form, and the number GT already runs

> **Status: PARTLY DECIDED.** §7 **A3 is answered** (Tom, 2026-08-31 — a second dedicated
> number, `054-758-8132`; `Sales-Machine/doctrine/decisions.md` D-014). A1, A2 and A4 remain
> recommendations awaiting Tom and are not authority until he answers.
> **Date:** 2026-08-31 · **Branch:** `claude/caveman-mode-phzjqa`
> **Requested by:** `docs/plans/2026-08-31-lead-response-system-masterprompt.md` §W1 (D1).
> **Governing:** `docs/decisions/modules/sales-declaration.md` (APPROVED, Amendment A) ·
> `Sales-Machine/doctrine/decisions.md` **D-006** ·
> `docs/superpowers/specs/2026-08-10-sales-leads-pipeline-design.md`.
> **Every number below was measured live against Supabase `rvadsozabmxkkrktwgnv` on
> 2026-08-31 between 11:32Z and 11:55Z.** Nothing here is quoted from a prior document
> without being re-checked.

---

## 1. Why this document exists

Two plans describe GT's lead handling and neither mentions the other.

- The setup artifact (`הקמת מערכת הלידים`, 36 tasks, 0 marked done) plans a
  **Click-to-WhatsApp** system in nine stages, starting from nothing.
- Production runs a **Meta lead-form** system: Make → `/ingest` → `sales_core`, live under
  D-006 since 2026-08-24.

Build the artifact literally and GT ends up with two intakes and two truths. That was the
question this document was commissioned to settle.

**The measurement changed the question.** There are not two intakes. There are three, and
the third is the largest.

---

## 2. Ground truth, measured 2026-08-31

### 2.1 Intake A — the Meta lead form (the one everybody knows about)

```
leads_total 199 · leads_new 141 · leads_won 3 · events_total 359
leads_ever_touched 69 · orgs 196
oldest_lead 2023-06-18 · newest_lead 2026-08-29 20:16Z
```

Arrivals, trailing 30 days: `08-01: 1 · 08-03: 1 · 08-06: 1 · 08-07: 4 · 08-08: 3 ·
08-09: 1 · 08-24: 5 · 08-25: 1 · 08-26: 1 · 08-27: 2 · 08-28: 1 · 08-29: 1`.
Roughly **one to two leads a day** when the transport is up.

Transport health at 11:32Z: last hourly pulse `2026-08-31 11:11:17Z`, age 21 minutes,
`forms_visible: 1`. **The Make connection is alive.** The `08-10`→`08-23` gap is the
pre-D-006 outage, already on the record; the `08-30`→`08-31` gap is one working day and
the pulse is affirmative, so it is a quiet day, not the 2026-06-07 signature.

### 2.2 Intake B — GT's live WhatsApp number. This is the finding.

The masterprompt's §2.3 states: *"No WhatsApp Business API account. No provider. No
dedicated number in the API."* **All three are false.** Measured:

| Fact | Value | Source |
|---|---|---|
| WhatsApp Cloud API in production since | **2026-06-26 21:10Z** | `order_intake.wa_event_log`, earliest row |
| Events logged | **24,028** | same |
| Most recent event at time of writing | **2026-08-31 11:30:05Z** | same |
| Inbound volume, last full week | **~300–500 events/day** | same, grouped by day |
| Conversation sessions | **805** | `order_intake.wa_session` |
| Phone numbers mapped to a customer | **195** | `order_intake.wa_customer_map` |
| Provider / onboarding path | **Dualhook Coexistence** (BSP), staff keep the WhatsApp Business app on the same number | `docs/integrations/cowork_whatsapp_transport_master_prompt.md` |
| Coexistence staff echoes | **9,440 echo events** (`deferred_human_echo` 4,421 + `ignored_echo_unknown` 5,019) | `wa_event_log` |

Staff echoes flowing at that volume is the proof that coexistence is live and working: the
bot sees a human reply and stands down. That was the hard part of the WhatsApp build and it
is **done, in production, for two months**.

### 2.3 The un-captured stream

Of that inbound traffic, one status dominates and it is the one that matters here:

```
inbound · message · ignored_unknown_or_disabled   5,707 messages
```

Those are messages from phone numbers that are **not in `wa_customer_map`**. Distinct
senders:

| Measure | Value |
|---|---|
| Distinct unknown senders, all time (since 2026-06-28) | **275** |
| Distinct unknown senders, last 30 days | **163** |
| Distinct unknown senders, last 7 days | **58** |
| Of the 275, how many match a row in `sales_core.lead` | **1** |
| Of the 275, how many match a `sales_core.lead` with `status='new'` | **0** |
| Of the 275, how many match `sales_core.org` | **1** |
| Of the 275, how many match `order_bot.customer` (93 rows) | **1** |

**163 distinct people wrote to GT's WhatsApp in the last 30 days without being recognised
by anything, and essentially none of them exist in `sales_core`.** For comparison, the
Facebook form delivered roughly 12 leads in the same window.

### 2.4 What that stream is NOT — stated so the number is not over-read

`unknown sender` means *"no row in `wa_customer_map`"*. It does not mean *"new lead"*.
The shape of those conversations argues against reading it as a lead pile:

| Measure over the 275 senders | Value |
|---|---|
| Average inbound messages per sender | **20.8** |
| Senders with exactly one message ever | **36** |
| …of which in the last 30 days | **11** |
| Senders with more than 5 messages | **131** |
| Senders whose conversation spans more than 7 days | **117** |

A 20-message, multi-week conversation is a working relationship — an existing customer, a
supplier, a courier, a staff member — not an enquiry. `wa_customer_map` holds 195 numbers
against roughly 700 Shopify customers, so most real customers are simply unmapped and
land in this bucket. **The honest statement is: GT's largest inbound channel has no
identification layer, so the number of real leads inside it is unknown.** The
one-message-in-30-days tail (11) is the only lead-shaped population we can currently
name, and even that is a floor, not an estimate.

That unknown is itself the argument for this decision. It is also `U-014` (§8).

### 2.5 Intake C — the category landing pages

`docs/plans/2026-08-31-category-menus-masterprompt.md` is planned but **not present in
this repository** as of 2026-08-31 (`docs/plans/` last entry: `2026-08-30-weekly-sales-report-routine`).
Four category landing pages with forms are described there. They are a third intake unless
their forms post to the same `/ingest`.

### 2.6 Two live defects found while measuring

1. **Two Facebook form ids are in play, not one.** `sales_core.lead_reject` carries
   rejects from form `1771287887148857` as well as the documented `1165807205227331`,
   while the pulse reports `forms_visible: 1`. Any `source_id` taxonomy must cover both.
2. **Two real Facebook leads were lost on 2026-08-24** — leadgen ids
   `1807021066847822` (13:44:20Z) and `1469012341930658` (13:47:45Z). Both sit in
   `lead_reject` with `field_data: null` and the reason *"the Meta lookup … returned no
   field_data (check META_PAGE_ACCESS_TOKEN and its Leads Access on the page)"*, retried
   and re-rejected on 2026-08-28. Meta retains lead content for 90 days, so they are
   recoverable **until 2026-11-22** and not after.
3. **The order bot is erroring on Anthropic billing in production.** Seven
   `error: … credit balance is too low …` rows in `wa_event_log`, from 2026-07-27 to
   **2026-08-31 08:11Z**. Out of scope for this decision; flagged because it is live and
   nobody has surfaced it.

---

## 3. What the measurement does to the plan

**The artifact's stage 1 — the two-to-three-week queue that the masterprompt calls the
long pole (Reframe 4) — is already served.** Business verification, provider onboarding,
number provisioning and coexistence are done. What remains of stage 1 is template
submission (5.2) and reading the rate card (5.3).

That collapses the timetable, and it changes the CTWA question from *"should GT build a
WhatsApp lead system"* to *"should GT point ads at the WhatsApp number it already runs"*.

It also raises the risk the artifact could not have known about: **CTWA leads would land
in the same inbox as live customer orders**, on the same number, alongside 300–500
events a day. Without an identification layer that is not a lead system; it is a lead
disappearing into a busy inbox — which, measurably, is what already happens 163 times a
month.

---

## 4. The five questions

### Q1 — Does CTWA replace the lead form, or run beside it?

**Recommendation: run beside it, with CTWA as the growth path and the form kept as the
fallback. Do not switch off the form.**

| | CTWA | Meta lead form (today) |
|---|---|---|
| Time to first response | seconds; the customer is already in a chat | minutes to days; someone must open the queue |
| Cost of the first 72 h | free (see §5) | free (phone/email, no WhatsApp charge) |
| Data captured | name + WhatsApp number + `referral.source_id` | name, phone, email — no business name (`U-013`) |
| Failure mode | message lands in a 500-event/day inbox unidentified | lead lands in `sales_core` and is not called |
| Transport dependency | Meta → our webhook, direct | Meta → **Make** → our `/ingest` (D-006, third party) |
| Already built | the transport, yes; the lead capture, no | end to end, yes |

Reasons to keep both rather than switch:

1. The form's transport is the one D-006 explicitly accepted a third party for. Replacing
   it with CTWA would **remove** GT's dependence on a Make OAuth token that expires
   `2026-10-23` — a real prize — but only once CTWA capture is proven. Switching before
   that trades a known, monitored risk for an unknown one.
2. CTWA yields no email address. Email is the only channel that survives a phone change
   and the only one the Q4 existing-customer work can use.
3. Two paths into one table cost almost nothing once §Q3 is in place. Two paths into two
   tables cost everything. The expensive thing is the second store, not the second source.

**Reversal trigger:** if CTWA's measured first-order rate beats the form's over one full
month at comparable spend, retire the form and with it the Make dependency.

### Q2 — What writes the lead into `sales_core`, and when?

**Recommendation: on the first inbound WhatsApp message from a number that is not a known
customer — not on qualification.**

Write early, for three reasons: a lead written only at qualification is invisible while it
is being lost, which is precisely today's failure; `lead_event` cannot measure a
first-response time whose start it never recorded (D5); and `ingest_lead` is already
idempotent, so an early write costs one row and no risk.

Mechanically, the smallest change that does it:

```
Meta webhook ──> wa-order-bot ingress (live) ──> Node worker
                                                   │
                        status = ignored_unknown_or_disabled  ← today: dropped
                                                   │
                                                   └──> POST /ingest  (source='whatsapp')
                                                          → sales_core.lead + lead_event
```

The branch is one call at the point where the worker already decides the sender is
unknown. No new transport, no new webhook, no second provider.

**Guard, non-negotiable:** the write is a *record*, never a *reply*.
`SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` is `false`; nothing in this path sends anything.

**Two qualifiers before it ships,** because §2.4 says most unknown senders are not leads:
1. Only write for a sender with **no prior inbound history** — a genuinely first contact.
2. Carry `referral.source_id` when present. A message with a CTWA referral is a lead by
   construction; a bare message is a candidate and should be written with
   `source='whatsapp_unattributed'` so the two are never mixed in a metric.

### Q3 — The campaign taxonomy

> **Corrected 2026-08-31, after `docs/plans/2026-08-31-category-landing-pages-spec.md`
> merged.** That spec read this section as claiming a `source_id` column on
> `sales_core.lead` and corrected it. The correction is right about the schema and this
> section was ambiguous enough to earn it, so the two things are now named apart:
>
> | Name | What it is | Where it lives |
> |---|---|---|
> | `referral.source_id` | **Meta's** ad id, arriving in the CTWA webhook payload | nowhere in `sales_core` — it is an *input* |
> | `campaign_map.source_id` | the key of GT's own ad → category map | `sales_core.campaign_map` (0340) |
> | `lead.source` | the **channel** a lead arrived through | `sales_core.lead`, `not null`, half of `unique (source, external_id)` |
>
> There is no `lead.source_id` and this document never proposed one. Verified
> 2026-08-31 against `information_schema.columns`: `lead` carries `source`,
> `external_id`, `campaign_name`, `ad_name`, `form_id`, `form_name`, `platform`.

One column already exists and is unused for this: `sales_core.lead.campaign_name`, with
`ad_name`, `form_id`, `form_name`, `platform` beside it. No migration is needed for the
taxonomy itself; what is needed is that all three paths populate the same fields the same
way.

Proposed canonical string, one format for every path:

```
GT_<year>_<path>_<category>_<audience>_<version>
      path     ∈ CTWA | FORM | LP          (LP = landing page)
      category ∈ TEA | CHAI | POWDER | GEN
```

| Path | What carries it | Lands in |
|---|---|---|
| CTWA | `referral.source_id` (the ad id) + `referral.headline`, resolved through a mapping table | `campaign_name`, `ad_name` |
| Meta lead form | `form_id` (**both** ids per §2.6) + campaign fields from Make | `form_id`, `campaign_name` |
| Landing page | the page slug, posted to `/ingest` as `form_name` | `form_name` (+ `campaign_name` from `utm_campaign` when there is one) |

The ad-id → category mapping must live **in the database**, not in a spreadsheet
(artifact task 2.3 proposes a sheet). A sheet is a second truth by definition; a
`sales_core.campaign_map` table is one row per ad and is readable by the same query that
computes conversion by category (D5/W3).

Naming convention (artifact 2.4) is agreed and should be fixed **before the first ad
goes live**, because it cannot be applied retroactively to spend.

#### Q3.1 — `U-L6` answered: the landing pages keep `source = website_form`

`docs/plans/2026-08-31-category-landing-pages-spec.md` §7 asks the intake owner to agree
`site-chai` · `site-matcha` · `site-iced-tea` · `site-ube` as `sales_core.lead.source`,
and marks it blocking. **Answer: no — keep `source` as the channel, put the category in
`form_name`.** Not a style preference; three specific things break.

**1. `source` is channel-shaped today, and one existing row already proves the pattern.**
Measured 2026-08-31:

| `source` | leads | `form_name` | `campaign_name` | `form_id` |
|---|---|---|---|---|
| `import_meta_export` | 188 | 150 | 0 | 0 |
| `facebook` | 12 | 0 | 12 | 12 |
| `website_form` | 1 | **1** | **0** | 0 |

The single website lead that exists — written 2026-08-31, the only one the path has ever
produced — already carries its identity in `form_name` and has a null `campaign_name`.
The convention is not hypothetical; it is the one data point there is.

**2. It splits website history on day one.** `website_form` already exists. Adding
`site-*` beside it means every "how many leads from the site?" question has to know both
schemes, and silently under-counts the moment a fifth page is added — a page should not
need a migration and a dashboard edit to be counted.

**3. It breaks deduplication, which is what `source` is structurally for.**
`lead` carries `unique (source, external_id)` (0318). One café owner who fills the chai
form and then the matcha form is two rows under two *different* sources, and no query can
collapse them without enumerating the whole `site-*` family. Under one `website_form`
source, dedupe by phone within source is a one-line query.

**What the pages should send** — all of it already in the accepted `/ingest` body, so this
costs the landing-page work nothing:

```json
{ "source": "website_form", "form_name": "landing-chai", "campaign_name": "<utm_campaign, or omitted>" }
```

`form_name` ∈ `landing-chai` · `landing-matcha` · `landing-iced-tea` · `landing-ube`.
Category attribution is then one `campaign_map` row per page, `path='landing_page'`,
`source_id = form_name`.

**A defect this answer found in our own migration, now fixed.** `0340`'s
`v_sales_category_funnel` joined `path='landing_page'` on `l.campaign_name`. Since
`campaign_name` is populated from `utm_campaign`, it is null on direct traffic, a typed
URL or an organic share — so paid visits would have attributed and free ones would have
fallen into `unmapped`, giving a category breakdown that looked populated while
under-reporting exactly the traffic the pages exist to earn. Run against live data with a
stub map, on the one real `website_form` lead:

| join | result |
|---|---|
| `landing_page` → `campaign_name` (old) | `unmapped`, 1 lead |
| `landing_page` → `form_name` (new) | `tea`, 1 lead |

Fixed in `gt-factory-os#253`. Each path now joins the field that identifies it:
`form → form_id`, `landing_page → form_name`, `ctwa → campaign_name`.

**Reversible.** If Tom prefers category-shaped sources later, it is an `update` over a
handful of rows plus one `campaign_map` edit — no schema change either way. Recorded here
rather than decided silently, because the spec asked the owner and this is the owner's
answer.

### Q4 — Where does conversation history live, and what does `sales_core` store?

**Recommendation: history stays where it already is — `order_intake.wa_event_log`, which
holds 24,028 rows and is append-only in practice. `sales_core` stores a pointer, not a
copy.**

Add to `sales_core.lead`: `wa_phone text` (E.164) and `wa_first_message_at timestamptz`.
That is enough to join to the log, and it keeps two properties that matter: personal
message content is not duplicated into a second store (spec §2.6), and there is exactly
one place a conversation can be read from.

Explicitly rejected: storing conversation state in a vendor inbox. That is the
masterprompt's prohibition 2 and it is the failure this whole document exists to prevent.

### Q5 — What happens to the 199 records already there?

**Nothing structural. They stay, they are the pilot (§W2), and they are not re-imported,
re-keyed or migrated.** All 199 already carry `org_id`, and **all 141 `new` leads have a
phone number** — measured; there is no dead-by-missing-contact bucket to sweep. The only
change they need is the one Tom owes: `U-011`.

---

## 5. What this costs to run

Verified against Meta's own documentation on 2026-08-31
(`https://developers.facebook.com/docs/whatsapp/pricing/`):

- Pricing has been **per-message, not per-conversation, since 2025-07-01**.
- A Click-to-WhatsApp ad opens a **Free Entry Point window of 72 hours** — but the exact
  rule is narrower than the artifact's copy suggests: *"If you respond within 24 hours …
  the message will be free, and a FEP window will be opened, **starting from the time when
  you responded**. FEP windows remain open for 72 hours."* Inside it, **any** message
  type is free, templates included.
- A user message opens a **24-hour customer service window**; replies inside it are free.

Two consequences worth stating plainly:

1. **Answering fast is not only better, it is cheaper.** Miss the 24-hour reply and the
   free 72-hour window never opens at all.
2. The artifact's sequence is right: day-2 follow-up is free inside the FEP window; only
   **day-5 and day-12** need paid marketing templates.

**The Israel marketing rate could not be verified and is therefore not stated here.**
Meta's public pricing page defers to an interactive rate card
(`business.whatsapp.com/products/platform-pricing#rates`) which does not serve a fetchable
document. It is logged as `U-015`. The formula, ready for the number:

```
monthly operating cost = IL_marketing_rate × monthly_leads × 2 follow-ups
```

At the current form volume (~1.5 leads/day ≈ 45/month) that is `rate × 90`. Note the
authoritative rate is visible to Tom in **GT's own Meta Business Manager billing page** —
GT has a WABA, so this is not a research question, it is a two-minute look.

---

## 6. What is NOT recommended

- **Do not shortlist and buy a WhatsApp provider** (artifact 1.2, masterprompt W5). GT has
  one. Buying a second BSP interface would put lead state in a vendor inbox — prohibition 2.
- **Do not provision a second dedicated number** (artifact 1.3, §6.F) *for leads* until
  Q1 is decided. The number in the API is already GT's working number under coexistence;
  a second number splits the conversation history the whole design depends on. The
  irreversibility warning in the artifact is real but already spent.
- **Do not build the answer bank here.** It belongs to the knowledge book (Reframe 5).
- **Do not automate first response before §W2 reports.** Artifact 6.4, and the messaging
  quality rating is the reason.

---

## 7. What Tom decides — **A1 and A3 ANSWERED 2026-08-31**

| # | Question | Status |
|---|---|---|
| A1 | CTWA **beside** the form, or **instead of** it? | **ANSWERED — beside, with a switch trigger.** See below |
| A2 | Write an unknown WhatsApp sender into `sales_core` as a lead on first message? | open — default: yes, with the two qualifiers in §Q2 |
| A3 | Is the working WhatsApp number the one ads point at, or is a second number provisioned? | **ANSWERED — a second, dedicated number.** See below |
| A4 | Recover the two lost 2026-08-24 leads from Meta before 2026-11-22? | open — default: yes |

### A1 — answered: beside, and the switch is a measurement, not a meeting

**Tom, 2026-08-31.** Recorded as `Sales-Machine/doctrine/decisions.md` **D-016**.

Both paths write into `sales_core` carrying a campaign-bearing `source_id`. The form is
**not** switched off on the strength of an argument. It is switched off by a number:

> After one full month in which both run at comparable budget — **if CTWA's first-order
> rate matches or beats the form's, the form is retired, and the Make dependency goes with
> it.**

Three conditions keep that trigger honest, and each one exists because its absence is a
known way to decide wrongly:

| Condition | Why |
|---|---|
| **Orders, not leads** | A campaign can buy many cheap leads and produce zero orders, and it wins every lead-level metric while doing it |
| **Cohort, not calendar** | Leads that *arrived* in the window and have since ordered — not conversions *recorded* in it. §2 of the funnel work shows the calendar reading printing a 13.6 % rate that never happened |
| **≥30 leads per path**, or extend | Otherwise a 1-versus-0 month decides the architecture |

**No new build is needed for the trigger.** `sales_core.campaign_map` and
`api_read.v_sales_category_funnel` (migration `0340`) compute exactly this. What they need
is only that campaigns carry `source_id` — which is task 2.3, and which is why the naming
convention (2.4) must be fixed before the first ad runs.

**Execution split, agreed with Tom the same day and recorded so it is not re-litigated:**

| Link | Owner |
|---|---|
| The write branch — CTWA message → `sales_core` row with `source_id` | Claude |
| `campaign_map` populated once ad ids exist | Claude |
| The measurement and the verdict | Claude — already written |
| **Embedded Signup for the number** | **Tom** — an interactive Meta login |
| **Creating the campaigns in Ads Manager** | **Tom** — no Graph access exists, per D-006 |

The last two are not a gap that can be closed in code. They are the reason the setup plan
names "טכני" and "שיווק" as separate owners.

**Reversal, stated so it is not forgotten:** retiring the form removes GT's only source of
lead **email addresses**. That cost is accepted knowingly if the trigger fires.

### A3 — answered: `054-758-8132` is the lead number

**Tom, 2026-08-31, in writing.** Recorded as `Sales-Machine/doctrine/decisions.md` **D-014**.
This also answers the masterprompt's §6.F, which asked what that number is for.

`054-758-8132` becomes the single destination for every inbound enquiry reaching GT from any
Meta platform, carrying automated first responses and, later, a basic AI agent. The number
already in the Cloud API — GT's working order/customer line under Dualhook coexistence since
2026-06-26 — **stays exactly as it is.**

**What this decision buys.** §3 of this document names the risk in pointing ads at the
working number: a lead landing unidentified in an inbox that already carries 300–500 order
events a day, which is measurably what happens to 163 unknown senders a month. A separate
number removes that risk structurally rather than by classification. It costs the
conversation-history unification §Q4 assumed — two numbers means two `wa_phone` streams —
but `order_intake.wa_event_log` already keys on the phone, so the pointer design survives
unchanged.

**Two consequences, recorded now rather than discovered later.**

1. **`054-758-8132` joins the API via coexistence, and stays in the WhatsApp app.** Tom
   confirmed on 2026-08-31 that the number is in active use. Under **classic** onboarding
   that would have been a hard blocker — there, a number entering the API leaves the app
   permanently and cannot be handed back. **Coexistence removes the conflict rather than
   trading one loss for another:** the number stays live in the app for whoever uses it
   today while the Cloud API reads and sends on the same number alongside. GT is not
   guessing that this works — the order line has run exactly this way since 2026-06-26,
   with 9,440 staff-echo events proving the bot sees a human reply and stands down.
   Recorded as `Sales-Machine/doctrine/decisions.md` **D-015**; `U-022` closes as a
   non-blocker. **The standing requirement this creates needs a named owner:** the app must
   be opened at least once every 13 days and never uninstalled, or coexistence lapses
   silently and the integration dies with it.
2. **Automated messages to leads are exactly what `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED`
   gates** (`Sales-Machine/doctrine/decisions.md` D-005). Provisioning, webhook wiring,
   template submission and dry-runs may all proceed. **Sending may not** — that needs Tom's
   written approval plus a dry-run plus a ≥24 h soak. The AI agent Tom wants "later" sits
   behind the same gate and behind the answer bank, per the masterprompt's first
   prohibition: no lead is answered by a machine with a sentence a human did not approve.

**What §Q1 and §Q2 now mean in practice.** A dedicated lead number makes A2 easier, not
harder: on that number an unknown sender is a lead by construction, so the "no prior inbound
history" qualifier in §Q2 stops being a heuristic and becomes the normal case. The
`whatsapp_unattributed` source distinction still matters — a message with a CTWA
`referral.source_id` is attributable and a bare one is not.

## 8. UNRESOLVED opened by this document

| ID | Question | Route |
|---|---|---|
| U-014 | Of the 275 unknown WhatsApp senders (163/30d), how many are leads rather than unmapped customers, suppliers or staff? No identification layer exists to answer it | build the §Q2 write, then measure for 30 days |
| U-015 | Meta's current marketing-template rate for Israel | Tom, from GT's Meta Business Manager billing page |
| U-016 | `META_PAGE_ACCESS_TOKEN` has no Leads Access on the page — the cause of the two lost leads. Related to but distinct from D-006 (Make carries leads; this token is used for the *content* lookup) | technical, next intake session |
| U-017 | Second Facebook form id `1771287887148857` — live, or a stale test form? The pulse sees one form; rejects came from two | Alex / Meta Ads Manager |
| ~~U-022~~ | **CLOSED 2026-08-31.** The number is in use, and coexistence makes that a non-blocker (D-015) — it keeps the app and gains the API. Residual, and it is real: the 13-day open-the-app requirement has no owner | closed; the 13-day owner is open |

---

## 9. Evidence

- **Files changed:** this file only. No code, no schema, no migration.
- **Checks run:** 11 live SQL queries against `rvadsozabmxkkrktwgnv`; 1 `list_edge_functions`
  call; 2 documentation fetches. Every table figure in §2 is a query result pasted from
  this session, not a restatement.
- **Live-vs-repo checks (landmine 7):** `sales-lead-fanout` is **deployed and ACTIVE** with
  **no source in this repository or on `origin/main`**; `wa-order-bot` **exists in the
  repository and is NOT deployed** (the Node route is the live ingress). Both were
  established with `list_edge_functions`, not grep.
- **Sources cited:** Meta *WhatsApp Business Platform Pricing*, fetched 2026-08-31.
- **Authority grades:** §2 `system_verified` · §5 `doc_confirmed` · §4 and §6
  `inferred` — recommendations, not policy, per truth rule 1.
- **Stop conditions tripped:** none. No customer-facing write; no factory-os core access;
  no frozen flag touched.
- **Tom approvals required:** §7 A1–A4.
