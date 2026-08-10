# Design — `sales` module foundation: leads pipeline, org spine, portal surface

> **Status:** DRAFT — awaiting Tom's review. Not authority until approved.
> **Date:** 2026-08-10 · **Branch:** `claude/sales-system-planning-th2gna`
> **Supersedes in part:** `docs/plans/2026-08-07-leads-pipeline-masterprompt.md` (branch
> `claude/auto-email-leads-updates-1ojqwa`). The masterprompt's architecture survives; its
> field mapping, its account of how the old pipeline died, and its source spreadsheet are
> corrected here against evidence gathered 2026-08-10.
> **Module governance:** `docs/decisions/modules/sales-declaration.md`.

---

## 1. Purpose and definition of success

Build the foundation of GT's sales system, starting with the one motion that is bleeding
money today: inbound Facebook leads.

**Success, stated as one testable sentence:** a lead submits the Facebook form; within
minutes Tom gets an email that already says whether this is a stranger or an existing
customer; the lead appears in the portal with status, next-touch date and SLA badge; and
if the pipeline ever breaks again, Tom learns within a day instead of two months.

The build is deliberately narrow (leads only) but the foundation is deliberately wider
(a business entity that later carries churn radar, account value and white-space) so the
next layer does not begin with a migration.

## 2. Evidence base

Everything in this section was verified on 2026-08-10 unless stated otherwise. Facts that
are volatile are dated, per the Sales-Machine truth rules.

### 2.1 How the old pipeline died — `system_verified`

- The intake was Make scenario **5174396 "GT Leads — Instant"**, created by Tom
  2026-04-07: Facebook Lead Ads webhook (hook 2797155) → `GetLeadgen` → Google Sheets
  `addRow`. It was Tom's own build, not an unknown third-party integration.
- Its Facebook connection (`gteveryday`, connection id 6309050) **expired
  2026-06-07T20:37Z**. The last lead to reach the sheet is dated 2026-06-07. The
  expiry is the cause, not a coincidence.
- The scenario is currently **inactive** (`isActive: false`), as are
  5176271 ("GT Leads — Health Check") and 5195363 ("GT — התראת ליד חדש", also
  `isinvalid: true`).
- The destination sheet is **`GT Sales Pipeline CRM`**, tab `LEADS_RAW`, spreadsheet
  `1oXC9CeQL3Fj-Ka9TbiCNqxzEgiR-05tdl4y_oua3uFo` — **not** the `לידים GT` spreadsheet
  named in the masterprompt. Both may hold leads; §8 resolves this at import time.
- The Gmail connection `new leads` (6308857) remains valid to 2027-02 and is the one
  proven-alive Make credential (Guardian daily uses it).

### 2.2 What is actually flowing — `system_verified` (Meta Leads Center export, 2026-08-10)

- 188 rows. Most recent lead: **2026-08-09** — leads arrive daily.
- Roughly 150 paid-source leads since 2026-05-12, about 1.6 per day.
- **About 60 paid leads arrived after 2026-06-07 and were never seen by anyone.**
- The export reaches back to 2023 for organic Instagram/Messenger leads; those rows carry
  a name only, no phone or email, so their value is historical.

### 2.3 The live form — `system_verified`, corrects the masterprompt

The active form is `0205.2025-2question-new`, a **two-question form**. The export carries
name, email and phone. It carries **no business name, no city and no owner/manager
question**. The field names encoded in the old Make mapping
(`מה_שם_המסעדה/בית_הקפה/בר_שלך?`, `האם_את.ה_מנהל.ת_או_בעלים_בתחום_המסעדנות?`, `city`)
belong to an earlier form version and must not be assumed present.

Consequence: an incoming lead is close to anonymous — a personal name and a phone. Whether
it is a new café, an existing customer or a branch of a chain can only be established by
matching against what we already know. This is the strongest argument for the org spine in
§5, and it makes the enrichment step (§6.4) part of the core value, not a nicety.

Business identity is nonetheless recoverable from the data in many cases: email domains
(`kobi.a@cafecafe.co.il` → Cafe Cafe, a chain; `ori@prusot.com` → Prusot Factory) and
business-shaped display names (`lunabarcaffee@`, `mikigregcafe@`, `cafe.aviv555@`,
`newyorkbagels20@`, `boulangz@`).

### 2.4 Two data defects that become ingestion rules — `system_verified`

1. **Phone formats are inconsistent.** Both `+972526380055` and `+9720526380055` (an extra
   zero after the country code) appear, roughly half the rows in the malformed shape.
   Without normalisation to E.164, duplicate detection fails and `tel:` links break.
2. **Duplicates already exist.** `+972502177217` appears twice — "אילן מימון" (2026-06-06)
   and "דולצ'ה פרו מימון" (2026-06-09). One person, two leads, three days apart. This is
   the case the `possible_duplicate` flag exists for; it must flag, never block.

### 2.5 Meta platform mechanics — `doc_confirmed`

- The `leadgen` webhook carries only identifiers (`leadgen_id`, `page_id`, `form_id`,
  `ad_id`, `created_time`). Lead content requires `GET /{leadgen_id}` with a page token.
- A page is subscribed with `POST /{page_id}/subscribed_apps` and
  `subscribed_fields=leadgen`. Without it, no events arrive and no error is raised.
- Permissions: `leads_retrieval`, `ads_management`, `pages_show_list`,
  `pages_read_engagement`, `pages_manage_metadata`.
- **Standard Access is granted automatically to Business apps and covers any user holding a
  role on the app.** Tom is Admin of the GTeveryday business portfolio (`user_confirmed`,
  2026-08-10). App Review and Business Verification are therefore not required; they gate
  Advanced Access, which serves other people's pages.
- Failed webhook deliveries are retried with decreasing frequency **for 36 hours**, then
  dropped. There is no automatic backfill.
- **Meta retains leads for 90 days.** After that they cannot be downloaded from Ads
  Manager, Business Suite or the API. The 2026-08-10 export captured the backlog inside
  this window.

Sources: Meta *Retrieving Leads*, *Webhooks — Getting Started*, *Graph API Access Levels*,
*System Users — install apps and generate tokens*.

### 2.6 Evidence handling note

The lead export contains personal data (names, phone numbers, email addresses) of people
who are not yet customers. It is **not** committed to any repository. It is imported
directly into `sales_core` and the file is then discarded. Only aggregate counts appear in
documentation.

## 3. Locked decisions

Confirmed by Tom in this session, 2026-08-10.

| # | Decision | Rationale |
|---|---|---|
| D1 | Build the leads pipeline narrowly, but design the `sales` module skeleton to carry accounts, churn radar and tasks later | Avoids paying twice, including for the visual design |
| D2 | Single user (Tom). No role-gating work now; `assignee` exists in the schema from day one | Erik's role (U-011) is still open; a schema column is cheap, a permission system is not |
| D3 | **Spine is the business (`org`); a lead is an entry event pointing at an org.** `sales_core` never copies Shopify customer master — it stores an external reference only | Churn, account value and white-space are all questions about a business; §2.3 makes matching essential |
| D4 | Closure is **system-verified**: the first Shopify order for the linked org converts the lead and records the evidence. "Lost" stays manual with a reason. Every open lead carries a next-touch date. The SLA badge applies only before first touch | Matches the repo doctrine: what can be checked against a live system is checked, not declared. Prevents the screen decaying into a dead list |
| D5 | Build order: schema → historical import → intake + alert → portal. Visual design is a separate phase, run on real data | The import blocks on nobody; intake blocks on Tom. An empty screen cannot be designed |
| D6 | The module lives **inside the portal** as route group `/sales`, on the existing auth and database, with an isolated `sales_core` schema | One login, one navigation, one design system, and the lead sits next to Shopify and factory truth |
| D7 | Reliability is **webhook + reconciliation poll + heartbeat**, never webhook alone | 36-hour retry then permanent loss; and the real failure of the old pipeline was silence, not breakage |
| D8 | Only MIT/Apache-licensed open source may be copied. AGPL (Twenty, EspoCRM, Odoo) and GPL (Frappe) are excluded. Visual inspiration is unrestricted | AGPL network copyleft is incompatible with a closed portal |

Added 2026-08-10 after a second pass whose brief was: does this design drag us into
a programming project instead of something good that works from day one?

| # | Decision | What it removes |
|---|---|---|
| D9 | **Polling only. No Meta webhook.** One scheduled function reads `GET /{form_id}/leads` by time cursor every ~10 minutes | The verification endpoint, HMAC signature validation, `subscribed_apps` setup, Meta webhook configuration and 36-hour retry semantics. The poll *is* the reconciliation layer, so resilience stops being a separate component. Cost: lead latency ≤10 min instead of ~1 min, which is nothing for a lead called back within hours |
| D10 | **No Make anywhere in this module** (Tom, 2026-08-10). Email is sent directly from our function via **Resend** — one HTTPS POST with a non-expiring API key | The third party in the middle of the alert path, and with it the whole class of failure that killed the pipeline on 2026-06-07: a silently dying OAuth token. Verified: the repository has no other mail sender today, so something had to replace Make either way. Free tier covers ~3,000/month against our ~2/day. Sending *from* `gteveryday.com` needs one-time SPF/DKIM DNS records; until then Resend permits sending to the account owner's address, which is our only recipient |
| D11 | **The heartbeat rides the same daily job and the same sender** — one short email: leads in the last 24h, age of the most recent lead, poll status | A separate alerting mechanism, its schedule and its delivery path. (The existing daily-ops-guardian email keeps using Make for now — different lane. If Resend proves out, that is the natural next thing to migrate) |
| D12 | **Statuses are `new` / `working` / `lost` (+reason). "Won" is not clickable** — it is written only by Shopify order evidence | A status transition users can fake, and the UI to fake it with |
| D13 | **Import the Meta export only in v1.** The spreadsheets are deferred | Drive access work and cross-source deduplication. The sheets' human columns are stale anyway — that task list stood at 237 overdue items nobody worked |

## 4. Architecture

```
Meta Graph API ◄──poll every ~10 min──  Edge Function: sales-leads-poll
  GET /{form_id}/leads?filtering=time            │
                                                 │   (same function, POST route:
Any other source ──POST /ingest──────────────────┤    manual entry, website, WhatsApp)
                                                 ▼
                       ingest core: normalise → match org (Shopify lookup) → write
                                                 │
                                  Postgres schema sales_core
                                  org · lead · lead_event (append-only)
                        ┌────────────────────────┼────────────────────────┐
                        ▼                        ▼                        ▼
                 Resend API                portal /sales/leads     daily close-the-loop job
             → tom@gteveryday.com                                  (open leads → Shopify orders)
                                                                     + heartbeat, same sender
```

One function, one write path, one sender, no third party in the middle. Every entry point —
poll, generic POST, import — passes through the same ingest core, so normalisation,
matching, deduplication and event writing cannot drift apart.

**Where customer truth lives.** Shopify customers are not stored in our Postgres; the
customer/product tracker computes them live from Shopify into dated snapshots
(`docs/analytics/README.md`). That confirms D3's reference-not-copy rule and dictates the
mechanics: matching is a live Shopify lookup at ingest, and the org stores the customer id
plus a dated context snapshot, never a mirrored customer record.

## 5. Data model — schema `sales_core`

Isolated schema. No foreign key, view or trigger reaches into factory-os core
(`stock_ledger`, `balance_anchors`, `bom_*`, `items`, `components`). Catalog or customer
reads happen through curated views only.

### 5.1 `org` — the business

| Column | Notes |
|---|---|
| `id uuid pk` | |
| `display_name text` | Best known name; starts as the lead's own text, improves with enrichment |
| `phone_e164 text` | Normalised, indexed |
| `email text`, `email_domain text` | Domain drives business identification |
| `city text null` | Not supplied by the current form |
| `shopify_customer_id text null` | Reference only. Never a copy of customer master |
| `is_customer boolean` | Derived from the reference above |
| `created_at`, `updated_at` | |

Chain/parent hierarchy is explicitly **not** modelled yet (open in Sales-Machine as U-001/
U-002). `org` is a branch-level business.

### 5.2 `lead` — the entry event

| Column | Notes |
|---|---|
| `id uuid pk` | |
| `org_id uuid fk → org` | |
| `source text` | `facebook` · `manual` · `import_meta_export` · `import_sheets` · … |
| `external_id text` | `leadgen_id` where available; otherwise a stable hash (§8) |
| `contact_name`, `phone_e164`, `email` | As submitted, phone normalised |
| `campaign_name`, `ad_name`, `form_id`, `form_name`, `platform`, `is_organic` | Populated when the source provides them |
| `status text` | `new` · `working` · `lost`. **`won` is not settable by a user** — it is written only by the close-the-loop job from order evidence (D12) |
| `lost_reason text null` | Required when status is `lost` |
| `assignee text null` | Exists now, unused until a second person joins |
| `next_touch_at timestamptz null` | D4: an open lead without one floats to the top |
| `first_touch_at timestamptz null` | Stops the SLA timer |
| `possible_duplicate_of uuid null` | Flag, never a block |
| `converted_order_ref text null` | Shopify order that proved conversion |
| `created_at` | |

`unique (source, external_id)` gives idempotency across every entry path.

### 5.3 `lead_event` — append-only history

`id`, `lead_id fk`, `event_type` (`created` · `status_change` · `note` · `assignment` ·
`next_touch_set` · `alert_sent` · `converted` · `matched_existing_customer`),
`payload jsonb`, `actor text`, `created_at`.

A database trigger blocks `UPDATE` and `DELETE`, mirroring ledger doctrine: corrections are
new, opposite events. Every mutation of `lead` writes its `lead_event` in the same
transaction.

### 5.4 Normalisation and matching rules

1. **Phone → E.164.** Strip the `p:` prefix, strip spaces and dashes, collapse the
   `+9720…` double-zero defect, reject anything that will not normalise (recorded, not
   silently dropped).
2. **Org matching, in order:** exact `shopify_customer_id` → exact `phone_e164` → exact
   `email` → business email domain. First hit wins; no fuzzy name matching in v1.
3. **No match** creates a new `org`.
4. **A repeat lead from a known phone** attaches to the existing org and sets
   `possible_duplicate_of` on the newer lead.
5. **A match against a Shopify customer** writes `matched_existing_customer` and changes
   the alert's framing (§7).

## 6. Ingestion

### 6.1 `sales-leads-poll` (Supabase Edge Function, scheduled ~every 10 minutes)

Reads `GET /{form_id}/leads` filtered on `created_time` greater than the stored cursor,
maps each lead, and calls the ingest core. The cursor is advanced only after a successful
write, so a failed run re-reads rather than skips. Idempotent on `leadgen_id` via
`unique (source, external_id)`, which makes overlap harmless and lets the window overlap
deliberately.

This single mechanism replaces both the webhook and the separate reconciliation job (D9).
An outage of any length self-heals on the next run, bounded only by Meta's 90-day
retention. Meta's rate limit — 200 × 24 × leads in the past 90 days, per page, per 24h —
is orders of magnitude above a 10-minute poll at GT's volume.

Field mapping is derived from one real fetched lead before any mapping is written — §2.3
is the reason. No field name is assumed.

### 6.2 `POST /ingest` (same function, second route)

Bearer `LEAD_INGEST_TOKEN`, same ingest core. Covers manual entry from the portal, a future
website form and WhatsApp. Sharing the function keeps one deployment and one code path.

### 6.3 Close-the-loop job and heartbeat (daily)

One job, two jobs' worth of value:

1. **Conversion check.** For **open leads only**, ask Shopify whether the matched customer
   has ordered. If yes: status `won`, `converted_order_ref` set, `lead_event(converted)`
   written with the order and amount as evidence. Scanning only open leads keeps this a
   small query set no matter how the lead table grows.
2. **Heartbeat.** If the poll has not run, or campaigns are active and no lead has arrived
   for N days (default 3), email Tom. The old pipeline's real failure was that nobody
   knew for two months — this line is the fix, and it costs one `if`.

What this unlocks with no further code, and the reason the loop is worth closing:
lead-to-customer conversion rate, days from lead to first order, and revenue per campaign
against ad spend. It is also the seam the churn radar attaches to later, using the
own-rhythm methodology already documented in `docs/analytics/README.md`.

### 6.4 Enrichment

At ingest, derive what can be derived without guessing: business email domain, business
keywords in the display name (קפה / בר / מסעדה / בייקרי and similar), and the Shopify match.
Anything uncertain is surfaced in the portal for Tom to confirm, never written as fact.

### 6.5 Secrets (Tom provides; the build stops here and asks)

- `META_PAGE_ACCESS_TOKEN` — from a Business Manager **System User**, non-expiring. This is
  the single credential that prevents a repeat of 2026-06-07. Tom is Admin of the
  GTeveryday portfolio, so he can create it. Polling needs no verify token and no app
  secret, which is two fewer secrets than the webhook design.
- `LEAD_INGEST_TOKEN` — bearer for the generic route.
- `RESEND_API_KEY` — non-expiring.

## 7. Alerting

The ingest core sends directly through **Resend**, recipient `tom@gteveryday.com`. No Make,
no OAuth, no scenario to maintain (D10). All the old lead scenarios stay retired.

After a successful insert of a genuinely new lead (not an import, not a duplicate), the
core sends the email and writes `lead_event(alert_sent)`. At most one alert per lead; the
event is what enforces it.

Subject: `🟢 ליד חדש: {business_or_contact_name}`, or, when the org is a known customer,
`🔁 ליד מלקוח קיים: {name}`. The body is Hebrew RTL, based on the corrected template from
scenario 5195363, with `tel:` / `wa.me` / `mailto:` links, the campaign, and — when matched
— the customer context that changes how Tom opens the call. The button links to the portal,
not to a spreadsheet.

**No message is ever sent to a lead or a customer.**
`SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` stays `false`.

## 8. Historical import

**v1 imports one source** (D13): the **Meta Leads Center export of 2026-08-10** — 188 rows,
`source='import_meta_export'`. It recovers the ~60 unseen leads and carries history back to
2023.

The spreadsheets are deferred. Their only advantage is the human columns the export lacks
(status, notes, owner), and those are stale: the sheet's own task list stood at 237 overdue
items nobody worked. If Tom says those notes matter, importing them later is another import
run tagged `source='import_sheets'`, not an architectural change.

`external_id` is the `leadgen_id` when present, otherwise a stable hash of
(normalised phone + submission date). **Imports never send email.** The import reports:
accepted X, merged as duplicates Y, rejected Z with reasons.

Rows without a phone and without an email (the 2023–2024 organic Instagram/Messenger rows)
are imported as history and marked uncontactable rather than discarded.

## 9. Portal surface — `/sales`

Scope is the minimum that is genuinely usable. **Visual design is out of scope here and is
decided in its own phase, on real data.** This section fixes behaviour and information
architecture only.

**One route in v1** — `/sales/leads`. Detail opens as a drawer over the list, not a second
page. This removes a route, a layout and a navigation level, and it matches how the screen
is actually used: scan, open, act, close, next.

- **The list** — tabs by status; a row shows business (or contact), city when known,
  campaign, lead age, SLA badge before first touch only, next-touch date, and a customer
  badge when the org is already a Shopify customer. New and overdue-next-touch sort to the
  top.
- **The drawer** — all fields, the `lead_event` timeline, and the actions: set status
  (`working` / `lost` + reason), set next touch, add note, and `tel:` / `wa.me` /
  `mailto:` links. Every action is a mutation that writes a `lead_event`. `won` appears
  here as evidence, never as a button.
- **Org context** — shown inline as a badge with the customer's dated snapshot and a link
  out to Shopify. A dedicated `/sales/orgs/[id]` page waits until the churn radar needs it;
  the `org` table exists from day one either way, which is the part that would have been
  expensive to add late.

Hebrew, RTL, per `portal_ux_standard.md`, and the Hebrew register must be registered in the
portal's authorised-surface table before any string ships.
`tailwind.config.ts`, `globals.css` and the UX standard files are not edited.

Open-source reuse, per D8: harvest patterns (not wholesale adoption) from **Atomic CRM**
(marmelab, MIT — React + shadcn/ui + Supabase; its org/contact/deal separation, Kanban, CSV
importer and activity log) and from MIT Next.js + shadcn dashboards
(`next-shadcn-dashboard-starter`, `next-shadcn-admin-dashboard`) for TanStack table and
board patterns. Visual inspiration from Twenty, Attio and Linear is unrestricted because no
code is taken.

## 10. Failure modes

| Failure | Detection | Response |
|---|---|---|
| Token expires or is revoked | Poll returns an auth error; heartbeat sees silence | Alert naming the credential. A System User token makes this unlikely by construction |
| Function or database down | Cursor is not advanced | Next run re-reads the same window. Self-healing up to Meta's 90-day retention |
| Poll itself stops running | Heartbeat: no poll run recorded | Daily email to Tom |
| Meta form fields change again (it already happened once) | Ingest records unmapped field names instead of discarding them | Alert on the first unknown field |
| Same lead read twice by overlapping windows | `unique (source, external_id)` | Insert ignored, no second email |
| Malformed payload | Rejected and logged with the raw body | Never a silent drop |
| Resend call fails | `alert_sent` event absent | Retried next run; the lead is already safely stored, so the email is never the thing that loses data |

## 11. Evidence plan

- **pgTAP:** ingest, dedupe, phone normalisation including the double-zero defect,
  `UPDATE`/`DELETE` blocked on `lead_event`, status transitions, org matching order.
  Reported N/N.
- **Six-layer proof** per `CLAUDE.md`: row in `lead` → `lead_event(created)` → email
  actually received by Tom → lead visible in the portal → a status change in the portal
  written as an event → exception paths exercised (duplicate payload produces no second
  lead and no second email; malformed payload rejected and logged; simulated outage
  recovered by the reconciliation poll). A 200 OK proves layer one only.

## 12. Phases, each standing alone

| Phase | Delivers on its own | Exit evidence |
|---|---|---|
| 0 · Governance | Amendment A approval recorded; lane confirmed | Declaration updated; PR #98 noted |
| 1 · Schema | `sales_core` exists with append-only guarantees | pgTAP N/N on the five rules that can break: dedupe, phone normalisation, append-only, match order, one alert per lead |
| 2 · Import | Every lead GT ever received sits in one place, matched against Shopify — including the ~60 nobody saw | Import report: accepted / merged / rejected, with reasons |
| 3 · Poll + alert | No future lead is lost, and Tom is told within ~10 minutes with customer context attached | A real test lead through Meta's testing tool, all six layers |
| 4 · Close the loop | Conversion is recorded from order evidence; the pipeline can no longer die quietly | Induced silence fires the heartbeat; a real order converts its lead |
| 5 · Portal | Leads are workable, not merely stored | Playwright on the critical path |
| 6 · Design | The surface is worth looking at | Separate phase, own gate, real data |

Phases 1–2 block on nobody and can start immediately. Phase 3 blocks on Tom for two
credentials. Phases 1–4 are small: one migration, one function, one import script, one
daily job.

## 13. Open questions

| ID | Question | Route |
|---|---|---|
| S-01 | SLA hours before first touch (default 24) | Tom; parameter, not a constant |
| S-02 | Erik's role in assignment (masterprompt U-011) | Tom, when a second person joins |
| S-03 | Which spreadsheet(s) carry the human columns worth importing | Resolved during phase 2 by reading both |
| S-04 | Should the form be changed to ask for business name again | Tom + Alex — a marketing decision with a direct data consequence |
| S-05 | Hebrew status labels for display | Display mapping only; never schema values |
| S-06 | Chain/parent hierarchy | Deferred until Sales-Machine U-001/U-002 resolve |

## 14. Out of scope

Chain hierarchy · contacts as a separate entity · churn radar · white-space mapping ·
quotes and pricing · any outbound message to a lead or customer · any write to factory-os
core · role and permission work · visual design (its own phase).
