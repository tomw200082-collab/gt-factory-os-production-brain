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

## 4. Architecture

```
Facebook Lead Ads ──webhook──► Edge Function: meta-leads-webhook
                                  │ (verify signature, fetch GET /{leadgen_id})
Any other source ────POST─────► Edge Function: sales-lead-ingest
                                  │ (bearer token, same write path)
Scheduled job ──poll /{form_id}/leads──┤   reconciliation + heartbeat
                                       ▼
                    ingest core: normalise → match org → write
                                       │
                         Postgres schema sales_core
                         org · lead · lead_event (append-only)
                                  │                │
                    POST webhook  │                │  read models
                                  ▼                ▼
              Make "GT — Lead Alert" (Gmail)   portal /sales/leads
                     → tom@gteveryday.com
```

Every write path — webhook, generic endpoint, reconciliation poll, CSV import — passes
through one shared ingest core so normalisation, matching, deduplication and event writing
cannot drift between entry points.

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
| `status text` | `new` · `contacted` · `in_progress` · `won` · `lost` |
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

### 6.1 `meta-leads-webhook` (Supabase Edge Function)

`GET` answers Meta's verification challenge using `META_VERIFY_TOKEN`. `POST` validates
`X-Hub-Signature-256` against the app secret, acknowledges quickly with 200, then for each
`leadgen` entry fetches `GET /{leadgen_id}`, maps `field_data`, and calls the ingest core.
Idempotent on `leadgen_id`.

Field mapping is derived from a real fetched lead before any mapping is written — §2.3 is
the reason. No field name is assumed.

### 6.2 `sales-lead-ingest` (Supabase Edge Function)

Generic `POST`, bearer `LEAD_INGEST_TOKEN`, same ingest core. Covers manual entry, a future
website form and WhatsApp, and serves as the fallback target if the Make Facebook module is
ever needed as Plan B.

### 6.3 Reconciliation poll and heartbeat

A scheduled job reads `GET /{form_id}/leads` filtered by time and inserts anything missing.
It closes the 36-hour retry gap, any Edge Function outage, and any silently unsubscribed
page. The heartbeat is the other half: if campaigns are active and no lead has arrived for
N days (N configurable, default 3), Tom gets an email. The old pipeline's real failure was
that nobody knew — this is the fix.

### 6.4 Enrichment

At ingest, derive what can be derived without guessing: business email domain, business
keywords in the display name (קפה / בר / מסעדה / בייקרי and similar), and the Shopify match.
Anything uncertain is surfaced in the portal for Tom to confirm, never written as fact.

### 6.5 Secrets (Tom provides; the build stops here and asks)

`META_VERIFY_TOKEN`, `META_APP_SECRET`, `META_PAGE_ACCESS_TOKEN` (from a Business Manager
**System User**, non-expiring — this is what prevents a repeat of 2026-06-07),
`LEAD_INGEST_TOKEN`, `MAKE_LEAD_ALERT_WEBHOOK_URL`.

## 7. Alerting

A new Make scenario "GT — Lead Alert": CustomWebHook → Gmail `sendAnEmail` on connection
6308857, recipient `tom@gteveryday.com`. Same proven pattern as Guardian daily. The old
lead scenarios stay retired.

After a successful insert of a genuinely new lead (not an import, not a duplicate), the
ingest core posts to the hook and writes `lead_event(alert_sent)`. At most one alert per
lead.

Subject: `🟢 ליד חדש: {business_or_contact_name}`, or, when the org is a known customer,
`🔁 ליד מלקוח קיים: {name}`. The body is Hebrew RTL, based on the corrected template from
scenario 5195363, with `tel:` / `wa.me` / `mailto:` links, the campaign, and — when matched
— the customer context that changes how Tom opens the call. The button links to the portal,
not to a spreadsheet.

**No message is ever sent to a lead or a customer.**
`SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` stays `false`.

## 8. Historical import

Two sources, both `source`-tagged so provenance is never lost:

1. **Meta Leads Center export, 2026-08-10** — 188 rows, `source='import_meta_export'`.
   This is the authoritative recovery of the ~60 unseen leads plus history back to 2023.
2. **The spreadsheets** — `GT Sales Pipeline CRM` / `LEADS_RAW` (the live destination of
   the dead scenario) and the `לידים GT` sheet named in the masterprompt.
   `source='import_sheets'`. Their added value over source 1 is the human columns the
   export lacks: status, notes, owner. Rows that duplicate source 1 merge into the same
   org and are flagged, not duplicated.

`external_id` is the `leadgen_id` when present, otherwise a stable hash of
(normalised phone + submission date). **Imports never send email.** The import reports:
accepted X, merged as duplicates Y, rejected Z with reasons.

Rows without a phone and without an email (the 2023–2024 organic Instagram/Messenger rows)
are imported as history and marked uncontactable rather than discarded.

## 9. Portal surface — `/sales`

Scope is the minimum that is genuinely usable. **Visual design is out of scope here and is
decided in its own phase, on real data.** This section fixes behaviour and information
architecture only.

- **`/sales/leads`** — inbox. Tabs by status; a row shows business (or contact), city when
  known, campaign, lead age, SLA badge before first touch only, next-touch date, and a
  customer badge when the org is already a Shopify customer. Default sort puts new and
  overdue-next-touch at the top.
- **`/sales/leads/[id]`** — lead detail. All fields, the `lead_event` timeline, and the
  actions: change status, set next touch, add note, assign, and `tel:` / `wa.me` /
  `mailto:` links. Every action is a mutation that writes a `lead_event`.
- **`/sales/orgs/[id]`** — thin business view: the org's leads, its Shopify link when
  present. This is the seam the churn radar and account value plug into later.

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
| Token expires or is revoked | Reconciliation poll returns auth error; heartbeat sees silence | Alert to Tom naming the credential. System User token makes this unlikely |
| Edge Function down | Meta retries 36h; poll backfills afterwards | No lead lost inside the 90-day window |
| Page subscription silently removed | Heartbeat: campaigns active, zero leads | Alert; re-subscribe |
| Meta form fields change again | Ingest records unmapped field names instead of discarding them | Alert on first unknown field |
| Duplicate webhook delivery | `unique (source, external_id)` | Insert ignored, no second email |
| Malformed payload | Rejected and logged with the raw body | Never a silent drop |
| Alert webhook fails | `alert_sent` event absent | Retry, then surface in the portal |

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
| 1 · Schema | `sales_core` exists with append-only guarantees | pgTAP N/N |
| 2 · Import | Every lead ever received is visible in one place, including the ~60 lost ones | Import report: accepted / merged / rejected |
| 3 · Intake + alert | No future lead is lost; Tom is notified within minutes | Real test lead through Meta's testing tool, all six layers |
| 4 · Reliability | The pipeline cannot die silently again | Simulated outage recovered by poll; heartbeat fires on induced silence |
| 5 · Portal | Leads are workable, not just stored | Playwright on the critical path |
| 6 · Design | The surface is worth looking at | Separate phase, own gate, real data |

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
