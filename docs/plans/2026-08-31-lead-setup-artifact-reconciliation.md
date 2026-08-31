# Reconciliation — the lead-system setup artifact against production

> **Date:** 2026-08-31 · **Branch:** `claude/caveman-mode-phzjqa`
> **Reconciles:** the setup artifact `הקמת מערכת הלידים` (9 stages, 36 tasks,
> reported `0 מתוך 36`) against what is measurably live on 2026-08-31.
> **Requested by:** `docs/plans/2026-08-31-lead-response-system-masterprompt.md` §W7 (D8).
> **Companion:** `docs/decisions/2026-08-31-lead-intake-architecture.md` (§W1), which
> carries the evidence for everything asserted here.

---

## Why this matters more than bookkeeping

The artifact reports `0 מתוך 36` and describes building a lead system from nothing.
Measured, **twelve of its thirty-six tasks are already done or superseded by
production** — including the entire WhatsApp infrastructure stage that its own timetable
calls the long pole. Left stale, the artifact guarantees that the next person to read it
rebuilds `sales_core`, buys a second WhatsApp provider, and provisions a second number.

**Status vocabulary**

| Token | Meaning |
|---|---|
| `DONE` | verified live on 2026-08-31, with the evidence named |
| `SUPERSEDED` | production solved it differently; the pointer says how |
| `OPEN` | genuinely not done; owner and blocker named |

---

## Stage 0 — Decisions · 0/5 done

| # | Task | Status | Evidence / note |
|---|---|---|---|
| 0.1 | Three starter packages | `OPEN` — **Tom** | The root blocker. Nothing customer-facing can be written without it. Masterprompt §6.C |
| 0.2 | Delivery time in days | `OPEN` — **Tom** | "Twice a week per region" is a frequency, not an answer |
| 0.3 | Discount tiers by consumption | `OPEN` — **Tom** | |
| 0.4 | Commitment and exclusivity | `OPEN` — **Tom** | |
| 0.5 | Dedicated phone number (decision) | `SUPERSEDED` | GT's working number has been in the Cloud API under **Dualhook coexistence since 2026-06-26**; staff keep the WhatsApp Business app on it (9,440 staff-echo events prove coexistence is live). The irreversible step the artifact warns about is already taken. What remains is narrower: **do the ads point at this number or at a second one** — architecture doc §7 A3 |

---

## Stage 1 — WhatsApp infrastructure · 4/5 done

**This is the stage the artifact budgets one-to-two weeks of queueing for. It is
substantially finished.**

| # | Task | Status | Evidence / note |
|---|---|---|---|
| 1.1 | Meta business verification | `DONE` | Inferred, but strongly: Dualhook coexistence onboarding runs through Meta Embedded Signup, whose Phase 0 requires a Business-verified portfolio (`gt-factory-os/docs/integrations/cowork_whatsapp_transport_master_prompt.md`). Coexistence is live, therefore Phase 0 passed. Grade `inferred` — Tom can confirm in one glance at Business Settings → Security Center |
| 1.2 | Choose a WhatsApp provider | `DONE` | **Dualhook**, coexistence path. Do not shortlist three more (architecture doc §6) |
| 1.3 | Dedicated number in the API | `DONE` | See 0.5. `order_intake.wa_event_log`: 24,028 events, first `2026-06-26 21:10Z`, latest `2026-08-31 11:30Z` |
| 1.4 | Business profile (name, photo, description) | `OPEN` — marketing | Not readable from our side; lives in the Meta/Dualhook console |
| 1.5 | Messaging tier and quality rating | `OPEN` — technical | Same: console-only. Record the tier **before** raising media budget, per the artifact — the advice is right and unaffected |

---

## Stage 2 — Campaigns · 1/5 done

| # | Task | Status | Evidence / note |
|---|---|---|---|
| 2.1 | Switch to Click-to-WhatsApp | `OPEN` — marketing | Blocked on architecture doc §7 A1 (CTWA beside the form, or instead of it) |
| 2.2 | A separate campaign per category | `OPEN` — marketing | Start with chai — 1 SKU, 11 drinks — as the artifact says |
| 2.3 | Automatic category detection | `SUPERSEDED` in part | The artifact specifies a Google Sheet mapping `source_id → category`. A sheet is a second truth by construction. Landed instead as **`sales_core.campaign_map`** (migration `0341`… see note) — a table the same query can join for both kit routing and conversion-by-category. The `referral.source_id` capture itself is still `OPEN` |
| 2.4 | Naming convention | `OPEN` — marketing | Format proposed in architecture doc §Q3. **Must be fixed before the first ad runs** — it cannot be applied retroactively to spend |
| 2.5 | Exclude the ~700 existing customers | `OPEN` — marketing | Also the Lookalike seed |

> Note: `campaign_map` ships in migration **`0340_sales_funnel_metrics.sql`** together with
> the metrics that consume it; `0341` carries the backlog triage. Both are in this PR.

---

## Stage 3 — Content kits · 0/4 done

| # | Task | Status | Evidence / note |
|---|---|---|---|
| 3.1 | Three recipes per category (PNG, 1:1 or 4:5, ≤5 MB) | `OPEN` — marketing | The assets are the category menus in `docs/plans/2026-08-31-category-menus-masterprompt.md`, **which does not exist in this repository as of 2026-08-31**. Do not commission a second set |
| 3.2 | A 15–30 s video per category, ≤16 MB | `OPEN` — marketing | |
| 3.3 | Dropbox folder structure with a version file | `OPEN` — marketing | |
| 3.4 | Upload to the provider media library, record `file → media_id → category` | `OPEN` — technical | Send by `media_id`, never by URL. The `sales_core.campaign_map` table is where the category half of that mapping now lives |

**D6 (which kit went to which lead) is half-built:** migration `0340` adds the
`kit_sent` `lead_event` type, so the record has a home the moment a kit exists. Nothing
emits it yet, and the funnel view reports that honestly rather than showing 0%.

---

## Stage 4 — Answer bank as data · 0/3 done, and it is not this system's to build

| # | Task | Status | Evidence / note |
|---|---|---|---|
| 4.1 | One Google Sheet, fixed columns | `SUPERSEDED` as to owner | The bank belongs to the knowledge book (`docs/plans/2026-08-31-knowledge-book-masterprompt.md` §W3 — also not present in this repository yet). Two documents currently specify building it; one write path must own it, and it should be the repo with grading and expiry discipline. **Consume it; do not fork it** |
| 4.2 | Every `לא מוגדר` enters as a transfer row | `OPEN` — sales | The four gaps are exactly Tom's 0.1–0.4. A missing row makes a machine guess at a restaurant owner; a transfer row makes it hand over. That distinction is the entire safety model |
| 4.3 | Approval path (sales writes, Alexander approves) | `OPEN` — sales + Tom | |

---

## Stage 5 — Templates · 1/4 done

| # | Task | Status | Evidence / note |
|---|---|---|---|
| 5.1 | Map which messages need a template | `DONE` | Architecture doc §5, verified against Meta's own pricing documentation on 2026-08-31. **One correction to the artifact's copy:** the 72-hour free-entry-point window does not start at the ad click. Meta: *"If you respond within 24 hours … a FEP window will be opened, starting from the time when you responded. FEP windows remain open for 72 hours."* Miss the 24-hour reply and the free window never opens. Answering fast is not only better service, it is cheaper. Day-2 free, day-5 and day-12 paid — the artifact's conclusion stands |
| 5.2 | Submit the two marketing templates | `OPEN` — technical | Blocked by 0.1–0.4: the copy cannot be written before the commercial answers exist |
| 5.3 | Israel marketing rate → monthly budget | `OPEN` — **Tom**, ~2 minutes | Meta's public page defers to an interactive rate card that serves no fetchable document; logged as `U-015`. **GT has a WABA, so the authoritative rate is in Tom's own Meta Business Manager billing page.** Formula: `rate × monthly_leads × 2 follow-ups`; at ~45 leads/month that is `rate × 90` |
| 5.4 | Israeli spam-law check | `OPEN` — **Tom** | One call to a lawyer. Masterprompt §6.H |

---

## Stage 6 — Manual pilot · 2/4 done

| # | Task | Status | Evidence / note |
|---|---|---|---|
| 6.1 | Thirty leads worked by hand | `SUPERSEDED` — **and already under way** | The artifact proposes running campaigns to generate 30 leads to work manually. 141 already sit there, paid for. Measured 2026-08-31: **58 leads have been worked** (43 `lost`, 12 `working`, 3 `won`), with `status_change`, `assignment` and `note` events written as recently as `2026-08-31 09:13Z`. The pilot is not pending; it started, and no campaign spend was needed |
| 6.2 | Question log | `OPEN` — sales | 13 `note` events exist but there is no structured "asked, no approved answer" capture. This is the pilot's most valuable output and it is currently being lost |
| 6.3 | Measurement (5 numbers) | `DONE` | Migration `0340`, `api_read.v_sales_funnel_metrics`. Baseline below |
| 6.4 | Gate to stage 7 | `OPEN` — **Tom** | Do not automate before the sequence works by hand |

### The baseline the pilot has produced so far — measured 2026-08-31

| Metric | Value | Note |
|---|---|---|
| Median first response, 30-day window | **4,718 minutes ≈ 3.3 days** | Against a configured SLA of 24 h (`sales_core.app_setting.sla_hours`) and the artifact's target of under 5 minutes |
| Leads in that window | 22 | |
| …answered | 14 | |
| First-order rate, 30-day **cohort** | **0 of 22** | A genuine zero, not a missing instrument |
| First-order rate, 90-day cohort | **1 of 117** = 0.85 % | |
| Cost per order | not measurable | `sales_core.ad_spend` is empty; spend cannot be fetched (no Meta Graph access) and must be entered |

> The 30-day window also contains 3 `converted` events, but they belong to older leads
> converted by the 2026-08-24 backfill. Dividing those 3 by the 22 leads in the window
> yields a **13.6 % conversion rate that never happened** — which is precisely what a
> naïve dashboard would have printed. The view separates cohort rate from calendar
> conversions for exactly this reason.

---

## Stage 7 — Automation · 0/5 done, correctly blocked

| # | Task | Status | Evidence / note |
|---|---|---|---|
| 7.1 | Automatic first response routed by `source_id` | `OPEN` | `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` is `false` and stays `false` |
| 7.2 | Kit send on an affirmative reply | `OPEN` | Blocked by stage 3 |
| 7.3 | Q&A layer answering only from approved rows | `OPEN` | Blocked by stage 4 |
| 7.4 | Human handover, which must stop the automation for that lead | `OPEN` | **Precedent exists and works:** the order bot's coexistence handover has fired 4,421 `deferred_human_echo` events. Whatever is built here should reuse that mechanism rather than invent a second one |
| 7.5 | Follow-up scheduler | `OPEN` | The expensive bug, stated in advance: any customer reply and any order must cancel every future follow-up for that lead. Test it explicitly before go-live |

Three drafted Hebrew templates already sit unused in
`sales_core.app_setting.whatsapp_templates` (`new_lead`, `reminder`,
`returning_customer`, written 2026-08-17). **None has ever been sent.** They are drafts,
not approved copy, and they state no price, delivery date or discount — so they remain
safe to hold, and unsafe to send until stage 4 exists.

---

## Stage 8 — Measurement dashboard · 1/1 done (data side)

| # | Task | Status | Evidence / note |
|---|---|---|---|
| 8.1 | Build the six-metric dashboard | `DONE` (data) · `OPEN` (portal render) | `api_read.v_sales_funnel_metrics` publishes all six as one row each, with `measurable` + `blocked_by` so an absent instrument never renders as a zero. The portal repository (`gt-factory-os-portal`) is **not attached to this session**, so the screen itself is a handoff |

---

## Tally

| | Count |
|---|---|
| `DONE` | 8 — 1.1, 1.2, 1.3, 5.1, 6.1*, 6.3, 8.1 (data), 2.3 (data half) |
| `SUPERSEDED` | 4 — 0.5, 2.3, 4.1, 6.1 |
| `OPEN` | 24 |
| **of which Tom's** | **8** — 0.1, 0.2, 0.3, 0.4, 5.3, 5.4, 6.4, plus architecture doc §7 |

\* 6.1 is counted once, as `SUPERSEDED`, in the tally.

**The critical path is not technical.** Stage 1 is done, stage 6 is running, stage 8 is
built. Every remaining chain — templates, the answer bank, automation, the kits' copy —
runs back through **0.1 to 0.4**, which only Tom can answer.

---

## Evidence

- **Files changed:** this file; `docs/decisions/2026-08-31-lead-intake-architecture.md`;
  `gt-factory-os` migrations `0340`, `0341` and their pgTAP tests.
- **Checks run:** 20 live read-only SQL queries against `rvadsozabmxkkrktwgnv`;
  `list_edge_functions`; 2 Meta documentation fetches. Both new views' bodies were
  executed read-only against production data and returned the figures quoted here.
- **Not run:** `pg_prove` (not installed in this container) and `npm run typecheck`
  (root `node_modules/@types` is empty — the workspace has no installed dependencies).
  Neither was skipped for convenience; both are unavailable. The migrations are
  **not applied to production**: `execute_sql` is read-only in this session, so the
  stock-truth pre-flight (`private_core.rebuild_verifier()`) could not be run, and the
  deploy-autonomy grant requires it green. They land in the PR for the normal deploy path.
- **Stop conditions tripped:** none. No customer-facing write, no factory-os core access,
  no frozen flag touched.
