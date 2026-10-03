> Evidence — read-only reconstruction by a Session 1 exploration agent, verbatim (2026-10-01). Authority: `system_verified` where a file:line is cited; re-read the file before relying on a value.

# Sales / Lead / CRM backend: current shape (gt-factory-os @ main `04cb0f6`, read 2026-10-01)

Inline paths are relative to `/home/user/gt-factory-os` unless marked otherwise. Absolute paths are listed in §11. I also made read-only checks of sibling repos `/home/user/gt-site` (for `?c=`) and `/home/user/Sales-Machine` (decisions and status), because the spec points into both.

---

## 0. Key facts for a Menu Builder

- **A "menu" already exists in the lead flow.** It is a **per-category PDF drinks menu**: Canva-designed, at most 8 drinks, FOOD COST printed (Sales-Machine D-025/D-026). It is *not* a WhatsApp list message. There are 5 menu keys: `matcha | ube | chai | tea | opening` (`api/src/order-intake/sales/lead_texts.ts:11-17`).
- The `opening` key is triggered by the ready text **`בניית תפריט משקאות עשיר ורווחי לעסק`** ("build a rich and profitable drinks menu for the business"). This is the existing "menu-building" entry point. Today it answers with a fixed recommended opening-menu PDF.
- The PDFs are referenced from `sales_core.app_setting['lead_menus']` = `{menu_key: {pdf_url, filename, label?}}`. Migration 0360:77 seeds it as `{}`. With no PDF configured, the lead gets the general reply instead.
- **There is exactly one write path for leads: `sales_core.ingest_lead()`.** Code calls it directly (quick-add, poll) or through the Edge route `/ingest`. "One open lead per phone" is enforced **only inside that function** (0361), using an advisory lock. There is no DB constraint.
- **`sales_core.lead_event` is append-only** (0320) with a **closed `event_type` vocabulary** (19 values after 0360). A new event type needs a migration that widens the CHECK. `qualified`, `kit_sent` and `question_logged` exist but nothing emits them.
- **Identities:**
  - lead = `sales_core.lead.id` (uuid), plus idempotency key `(source, external_id)`. The person is keyed by normalised phone (`phone_e164`, `+972…`).
  - business = `sales_core.org.id`.
  - customer = Shopify GID `gid://shopify/Customer/<n>` (Shopify is the customer master; `org` holds a reference plus a dated snapshot).
  - Two separate phone→customer maps exist: `order_intake.wa_customer_map` and `customer_portal.access`. Both store phones as digits-only `972…`.
- **A lead never becomes a customer in this system.** Staff create the customer in Shopify and Green Invoice by hand, then complete the lead's Shopify **draft**. A daily job then proves `won` from the Shopify order via `convert_lead()`.
- **Live state:** every automated lead-line send is a **dry run**. `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED=false`; only phones in `lead_journey_test_phones` get real sends.

---

## 1. Spec: `docs/superpowers/specs/2026-09-28-lead-journey-design.md` (382 lines)

**Status line (L3-6):** "DESIGN — decisions CONFIRMED (Tom, 2026-09-28); message texts PROPOSED until Tom approves". Every send is gated by D-005 (`SALES_CUSTOMER_OUTREACH_WRITE_ENABLED`, Tom's written approval, a dry run and a ≥24 h soak). The texts were later APPROVED: pinned playbook `api/src/order-intake/sales/__fixtures__/whatsapp-lead-journey@7fd25f8.md:3-4`, and UX gate rows U-27..U-39 in `docs/superpowers/plans/2026-09-25-customer-portal-ux-gate.md` §5.6.

**Sections**
- **§1 What the system does (L21-38).** The lead line is `054-758-8132`, `phone_number_id 217553368116155`. One automated message per event (D-027); free text is never answered by the machine. Site leads and campaign leads follow the same journey (D-032). The event → message table:

  | Event | Message | Effect |
  |---|---|---|
  | First message, menu recognised | menu PDF + body + footer + 3 buttons | lead ingested |
  | First message, no menu | general reply | at most once per phone per 30 days |
  | `«אני רוצה להזמין»` | personal ordering link | |
  | Order submitted | confirmation | Shopify **draft only** (D-029), owner alerted |
  | `«רוצה לשמוע עוד»` | "we'll call" + FAQ link | owner alerted |
  | `«תודה, לא כרגע»` | thanks | `lost` with reason `לא כרגע`, opt-out |
  | Salesperson logs `answered_progressing` | wake-up sequence, at most 4 | |
  | `הסר` | one-line confirmation | opt-out |

- **§2 What already exists (L42-128).** Inventory as of 2026-09-28: inbound path, lead capture, sending, staff echoes, the ordering portal (tokens, draft vs complete), the CRM function list, schedulers, the outreach gate, FAQ. Several statements here are now outdated; see §10.
- **§3 Components (L132-320):**
  - 3.1: the lead line must deliver, plus the Railway env.
  - 3.2: a second send port, and new kinds: document header + footer, CTA URL, template.
  - 3.3: menu recognition by exact match on 5 ready texts. The "first message" rule is 30 days.
  - 3.4: menu PDFs hosted on the Shopify CDN via `fileCreate`; config `lead_menus`; "No approved PDF, no first message".
  - 3.5: `opt_out_at`, new event types, a unique `(lead, kind, step)`, `lead_journey_test_phones`. Wake **eligibility = a first/general message was *delivered***.
  - 3.5a: send log; statuses de-duplicated by `wamid:status`.
  - 3.6: button ids, `הסר`, known customers.
  - 3.7: lead ordering link: 14 days, reusable until one order; never `draftOrderComplete`.
  - 3.8: wake scheduler: slots, holidays, stop rules, one phone normaliser, forced test runs, 131049/131050 handling.
  - 3.9: echoes keyed by number.
  - 3.10: the outreach gate (dry run, test-phone exception).
  - 3.11: 4 MARKETING + 1 UTILITY templates.
  - 3.12: the site FAQ.
- **§4 Tests and acceptance (L324-372).** No shadow DB; tests must use a local throwaway Postgres. Lists the unit and pgTAP lists and a 9-step end-to-end test with an allowlisted phone.
- **§5 Out of scope (L377-382).** Instagram/Messenger AI (U-054); menu design; messaging anyone who did not write first; any stock change.

**States.** There is no separate journey-state column. Lead status is `new → working → won | lost`. Journey state is derived from:
- `lead_event` (`auto_message`, `button_tap`, `opt_out`, `draft_order`, `outcome`);
- `order_intake.wa_event_log` outbound rows;
- `customer_portal.lead_link` / `lead_submission`.

**Message sequence as implemented** (`journey.ts`, `wake.ts`, `lead_texts.ts`):
1. **First message** (per phone, nothing sent in the last 30 days):
   - Menu recognised and PDF present → `first_menu`: interactive `button` with a document header, `TEXT.firstType(label)` or `TEXT.firstOpening`, footer `TEXT.firstFooter`, and buttons `lj.order` "אני רוצה להזמין", `lj.more` "רוצה לשמוע עוד", `lj.not_now` "תודה, לא כרגע".
   - Otherwise → `general_reply`: `cta_url` "שאלות ותשובות" → `https://gteveryday.com/#faq`.
2. **Any later message** (PR #328) → desk task: a note `kind:'lead_wrote'` plus `set_next_touch(now())`. The lead also gets `free_text_reply` (`TEXT.moreInfo` + FAQ CTA), **at most once per 24 h**. Nothing is sent if staff wrote to the phone in the last 24 h or the phone is opted out.
3. **Taps:**
   - `lj.order` → `order_link` CTA "להזמנה" with a minted token URL. A known customer (in `wa_customer_map`) gets `customer_link` → `/portal/`.
   - `lj.more` → `more_info` + Telegram alert to the owner.
   - `lj.not_now` → `not_now` text + `set_lead_status(lost, 'לא כרגע')` + `opt_out_phone`.
4. **Order submitted** → `order_confirm`: free-form text inside 23.5 h of the lead's last inbound message, otherwise utility template `gt_lead_order_confirmation`.
5. **Wake 1–4** (templates `gt_lead_wake_1..4`):
   - Message 1 goes ≥2 h after the `answered_progressing` anchor, with the menu PDF header and order-link suffix.
   - Message 2: morning of the first follow-up, FAQ link.
   - Messages 3 and 4: mornings of later follow-ups, order link.
   - A lead that only got the general reply skips message 1.
6. **`הסר`** (exact text, quotes and punctuation tolerated) → `opt_out_phone`, plus `optout_confirm` once.

**Stop rules** (`wake.ts:84-92`, spec §3.8):
- Final: not eligible; opted out; status not `new`/`working`; ordered (`converted_order_ref` set or a `draft_order` event exists); the lead replied after the anchor on either line; 4 steps already sent.
- Defer: staff echo in the last 24 h on either line; less than 48 h since the last automated message; outside the slots (Sun–Thu 10:00–11:30 and 15:00–17:00 Israel, never a `private_core.holidays_il` date). Steps 2–4 are morning-only.
- Errors: 131049 → retry after ≥24 h as a new attempt; 131050 → opt-out (`journey.ts:204`).

**Identity rules in the spec:**
- `wa_event_log.wa_phone` is digits-only `972…`; `sales_core.lead.phone_e164` is `+972…`. Joins must go through one normaliser (§3.8 L279-282).
- The lead link is bound to the lead and the phone (§3.7).
- A known customer = phone present in `order_intake.wa_customer_map` (§3.6).

**Order handoff (D-029, §3.7):**
- Shopify `draftOrderCreate`: tags `['lead','pk-<idem>']`, no customer, `visibleToCustomer:false`, note plus `customAttributes` (`lead_id`, `business_name`, `city`, `contact_name`, `wa_phone`). **Never completed**, on any path.
- Staff run skill `customer-setup-shopify-gi`, attach the customer, and complete the draft. The daily conversion then marks the lead won.

**Implemented vs planned:**
- Implemented in code (PRs #321, #323, #326, #327, #328): 3.2, 3.3, 3.5, 3.5a, 3.6, 3.7, 3.8, 3.9, 3.10, the 3.11 submission route, and the 3.1 health booleans.
- Pending, all outside code:
  - approved menu PDFs in `lead_menus` (3.4);
  - Meta template approval (U-052);
  - `WA_LEAD_SEND_TOKEN` on Railway (Tom's step);
  - Tom's written approval to flip the gate, after the dry run and ≥24 h soak.

---

## 2. Schema

### 2.1 `sales_core` (service_role only; lead rows are treated as PII, 0322:27-31)

**`sales_core.org`** (0318:49-62): `id uuid`, `display_name` (not null), `phone_raw`, `phone_e164`, `email`, `email_domain`, `city`, `shopify_customer_id` (text GID), `shopify_snapshot jsonb`, `shopify_snapshot_at`, `created_at`, `updated_at`.
- Unique `org_shopify_customer_id_key` where not null (0318:64-66).
- Index on `phone_e164`; index on `lower(email)`.
- The phone trigger `org_normalize_phone` (0319:64-67) sets `phone_e164 = normalize_phone_il(phone_raw)`.
- "Existing customer" means `shopify_customer_id is not null OR shopify_snapshot_at is not null` (0323:64-65).

**`sales_core.lead`** (0318:70-101, plus 0348:43, 0360:37):
- Columns: `id uuid`, `org_id` (FK org, not null), `source` (not null), `external_id` (not null), `contact_name`, `phone_raw`, `phone_e164`, `email`, `campaign_name`, `ad_name`, `form_id`, `form_name`, `platform`, `is_organic`, `status`, `lost_reason`, `assignee` (text email), `next_touch_at`, `first_touch_at`, `possible_duplicate_of` (FK lead), `converted_order_ref`, `converted_amount`, `created_at`, **`converted_order_placed_at`** (0348), **`opt_out_at`** (0360).
- **`status` enum:** `'new','working','won','lost'` (CHECK, default `new`).
- Constraints:
  - `lead_won_requires_evidence`: `status<>'won' or converted_order_ref is not null`.
  - `lead_lost_requires_reason`.
  - **`lead_source_external_id_key unique(source, external_id)`**.
- Indexes: org, status, `phone_e164`, partial `lead_open_idx` where status in (new, working).
- Trigger `lead_normalize_phone` (0319:59-62).
- **One open lead per phone (0361):** enforced *only* in `ingest_lead`, via `pg_advisory_xact_lock(hashtext('sales_core.lead_phone:'||phone))` (0361:76-78). A repeat contact joins the **oldest** open lead and becomes a `note` event with `kind:'repeat_contact'` (0361:102-161). There is **no unique index on phone**. Seven older phones still carry two open leads (0361:234-236).
- **Source values in use:**
  - `facebook` (Make → `/ingest`; also the Meta poll);
  - `website_form`;
  - `whatsapp_ctwa` / `whatsapp_unattributed` (lead line, `lead_capture.ts:39-40`);
  - `manual` (quick-add, and the `/ingest` default, `ingest_body.ts:55`);
  - `import_meta_export` (the 2026-08-10 historical import).

**`sales_core.lead_event`** (0318:109-118): `id`, `lead_id` (FK), `event_type`, `payload jsonb`, `actor text` (default `'system'`), `created_at`.
- **Append-only:** triggers `lead_event_no_update` / `lead_event_no_delete` raise P0001 (0320:10-28).
- **`event_type` CHECK, current at 0360:43-53:**
  - original: `created`, `status_change`, `note`, `assignment`, `next_touch_set`, `alert_sent`, `converted`, `matched_existing_customer`, `imported`;
  - 0322: `outreach`, `outcome`;
  - 0334: `reminder_sent`;
  - 0340: `qualified`, `kit_sent`;
  - 0342: `question_logged`;
  - 0360: `auto_message`, `button_tap`, `opt_out`, `draft_order`.
- **Partial unique indexes (used as "claims"):**
  - `lead_event_reminder_once_per_day` on `(lead_id, (created_at at time zone 'Asia/Jerusalem')::date)` where `reminder_sent` (0334:108-110).
  - `lead_event_auto_message_once` on `(lead_id, payload->>'kind', payload->>'step')` where `auto_message` (0360:56-58).
  - `lead_event_repeat_contact_once` on `(payload->>'source', payload->>'external_id')` where `note` and `kind='repeat_contact'` (0361:55-57).
- **Outcome results:** `answered_progressing | no_answer | whatsapp_sent | lost` (0324:131).
- **Outreach channels:** `call | whatsapp | email` (0322:230).
- **Convert evidence kinds:** `shopify_order | green_invoice` (0348:67).

**`sales_core.app_setting`** (`key` PK, `value jsonb`, `updated_at`; 0322:46-50). Keys:

| Key | Set in | Notes |
|---|---|---|
| `sla_hours` | 0322 | `{"hours":24}` |
| `whatsapp_templates` | 0322 | `{new_lead, reminder, returning_customer}`: the salesperson's manual templates |
| `queue` | 0326 | `{daily_cap:15, order:'newest_first'}` |
| `lost_reasons` | 0326, 0360 | `['לא רלוונטי','אין תקציב','הלך למתחרה','לא עונה לאורך זמן','לא כרגע','אחר']`; the last entry opens free text |
| `meta_poll` | 0328 | `enabled:false` |
| `intake_mode` | 0329 | `{mode:'make'}` |
| `lead_menus` | 0360 | `{}` |
| `lead_journey_test_phones` | 0360 | `[]` |
| `lead_journey_signers` | 0360 | `{"Avi":"אבי","Tom":"תום"}` |
| `lead_journey_force_template` | none | read in `portal/lead.ts:317`, **never seeded**, defaults false |
| `assignees` | 0325 | **deleted** by 0333:111 |

- Writes go through `set_app_setting(key, value, actor)`, which audits into append-only `sales_core.setting_event` (0326:41-100).

**Other `sales_core` tables:**
- `poll_run`: `route ∈ poll|daily|ingest|probe|backfill|reminders` (0328:61-69, 0334:101-103).
- `lead_reject` (0328:78-84).
- `campaign_map`: `path ∈ ctwa|form|landing_page`, `category ∈ tea|chai|powder|general`, unique `(path, source_id)` (0340:93-104). Seeded by 0343 (form `1165807205227331` → powder) and 0344 (`landing-site-{chai,matcha,iced-tea,ube}`).
- `ad_spend` (0340:116-128).
- `answer`: `status ∈ approved|transfer|draft`; `category ∈ product|commercial|objection|logistics` (0342:53-75).
- `question_log`: `resolution ∈ answered|transferred|unanswered` (0342:95-111).
- `sleeping_radar_run`: `flag ∈ active|off_pace|silent|insufficient_history` (0346:34-49).

**Functions (latest definitions):**

| Function | Defined in | Behaviour |
|---|---|---|
| `normalize_phone_il` | 0319:15-47 | IL phone → `+972…` |
| `is_business_domain` | 0321:32-46 | excludes free-mail domains |
| `match_org(phone, email, shopify_id)` | 0321:48-74 | rank: shopify id > phone > exact email > business email domain |
| `ingest_lead(p_source, p_external_id, p_contact_name, p_phone_raw, p_email, p_display_name, p_created_at, p_meta, p_shopify_customer_id, p_city default null)` | 0361:62-226 | returns `(lead_id, org_id, was_new, merged)`; reads `p_meta` keys `campaign_name`, `ad_name`, `form_id`, `form_name`, `platform`, `is_organic`, `notes`, `manual_note` |
| `lock_lead`, `touch_first` | 0322:77-106 | |
| `set_lead_status(lead, status∈{working,lost}, reason, actor, next_touch_at default null)` | 0324:59-109 | rejects `won`; `working` needs a next touch |
| `add_lead_note` | 0322:152-174 | sets `first_touch_at` |
| `set_next_touch` | 0322:176-196 | |
| `assign_lead(lead, assignee, actor, next_touch_at default null)` / `bulk_assign(uuid[] ≤200, …)` | 0325:59-117 | |
| `assert_assignee` | 0337:80-99 | active `private_core.app_users` with role in `sales_rep`, `planner`, `admin` |
| `record_outreach` | 0322:219-240 | does **not** set `first_touch_at` |
| `record_outcome` | 0324:116-188 | always writes `outcome {result, reason, next_touch_at}` |
| `next_business_touch(days)` | 0324:28-45 | 09:00 Israel; Fri/Sat move to Sunday |
| `convert_lead(lead, order_ref, amount, currency, actor default 'system:sales-leads-poll', evidence_kind default 'shopify_order', order_placed_at default null)` | 0348:51-112 | **the sole writer of `won`**; only an open lead converts; writes `converted` + `status_change` |
| `opt_out_phone(phone, reason, actor default 'system:lead-journey')` | 0360:83-111 | sets `opt_out_at` on every lead with that phone; one `opt_out` event each |
| `sla_hours()` | 0323:27-34 | |
| `set_app_setting` | 0326:81-100 | |

**Views (`api_read`, service_role only):**

| View | Defined in | Read by an API route? |
|---|---|---|
| `v_sales_leads` | 0326:106-149 (adds `uncontactable`) | yes |
| `v_sales_lead_events` | 0323:88-96 | yes |
| `v_sales_orgs` | 0323:102-125 | yes |
| `v_sales_today` (item_type `conversion`, `returning_customer`, `new_lead`, `due_follow_up`) | 0326:161-218 | yes |
| `v_sales_week_stats` | 0326:226-246 | yes |
| `v_sales_attention` (buckets `overdue`, `unowned`, `stalled`) | 0326:258-311 | yes |
| `v_sales_activity` | 0327:14-27 | yes |
| `v_sales_first_response` | 0340:143-161 | **no** |
| `v_sales_funnel_metrics` (7 rows incl. `fast_win_rate_24h`) | 0348:122-227 | **no** |
| `v_sales_category_funnel` | 0340:280-298 | **no** |
| `v_sales_backlog_triage` / `_summary` | 0341 | **no** |
| `v_sales_answer_bank`, `v_sales_question_gaps` | 0342 | **no** |
| `v_sales_sleeping_radar_latest` | 0346:65-83 | **no** |

- "No" means nothing in `api/src` or `supabase/functions` reads the view (grepped).
- `opt_out_at` and `converted_order_placed_at` appear in no view. Staff see opt-outs only as `opt_out` events.

**Cron jobs:**
- `sales_leads_poll` every 10 min, `sales_leads_daily` at `0 4` (0328:190-224);
- `sales_leads_reminders` at `0 3,4` (0334:134-147);
- `sales_sleeping_radar_nightly` at `30 1` (0347);
- `portal_registration_notify` every 5 min (0356);
- **`lead_wake_sequence` every 15 min → Railway `/api/v1/internal/jobs/lead-wake`** (0360:154-174).

### 2.2 `order_intake` (0265, 0266, 0273, 0274, 0275)

- **`wa_customer_map`** (0265:46-65): `wa_phone` (unique, digits-only), `shopify_customer_id` (GID), `display_name`, `branch`, `payment_mode ∈ terms|pay_now`, `bot_enabled` (default false), `default_pack`, `notes`, plus `pricing_mode ∈ special|full` (0266) and `intro_sent` (0273).
- **`wa_session`**: `state ∈ collecting, cart_proposed, editing, committed, cancelled, human_handled, clarifying, handed_off, committing, commit_failed` (0275).
- **`wa_event_log`** (0265:130-148): `wa_message_id` (unique), `direction ∈ inbound|outbound`, `wa_phone`, `session_id`, `type`, `raw_payload`, `processed_at`, `status`.
  - Inbound `type` is `message | echo | status`. A status is logged under the id `<wamid>:<status>` (`worker.ts:390`).
  - Outbound lead-line rows (`lead_line.ts:89-96`):
    - id `out:<uuid>`;
    - `type` = the send kind;
    - `raw_payload` top-level keys `{phone_number_id, to, kind, dry_run, lead_id, step, request}`, later `wamid`, `last_status`, `errors`;
    - `status` ∈ `sending | sent | dry_run:<kind> | send_failed:<code>`, then advanced to `delivered`/`read`/`failed` (`journey.ts:303-313`).

### 2.3 `customer_portal` (0355-0360; RLS on, no policies; only the API's pool can read or write)

- `access`: `wa_phone` (unique, digits), `shopify_customer_id` (not null), `display_name`, `branch`, `approved_at`, `approved_by`, `source ∈ backfill|registration`, `revoked_at`.
- `session`: `token_hash` (unique), `access_id`, `expires_at`, `revoked_at`.
- `link`: `token_hash`, `purpose ∈ login|register`, `wa_phone`, `access_id`, `created_by`, `expires_at`, `used_at`.
- `registration`: `status ∈ pending|approved|rejected`; unique pending per `wa_phone`; `staff_emailed_at` (0356).
- `order_submission`: `status ∈ submitting|created|failed`.
- `item_availability` (append-only) and `restock_request` (0357, 0358).
- **`lead_link`** (0360:117-126): `token_hash` (unique, sha256), `lead_id` (FK `sales_core.lead`), `wa_phone`, `created_at`, `expires_at` (14 days), `used_at`.
- **`lead_submission`** (0360:128-145): `idem_key` (unique), `link_id`, `lead_id`, `wa_phone`, `business_name`, `branch_city`, `contact_name`, `lines jsonb`, `subtotal_ex_vat`, `status ∈ submitting|drafted|failed`, `shopify_draft_id`, `shopify_draft_name`, `error`.

---

## 3. Routes

### 3.1 Sales workspace: `api/src/sales/route.ts`

The staff portal (`gt-factory-os-portal/src/app/api/sales/**`) proxies each of these. Every handler requires `roleAllowsSales(role)`, i.e. `sales_rep | planner | admin` (`api/src/auth/session.ts:65-67`). A DB rule refusal (P0001 with a `SALES_*` token) is returned as **422 `{code}`**. The actor recorded on events is `session.display_name || email` (`mutations_handler.ts:57-59`).

| Method | Path | Line | Purpose → DB |
|---|---|---|---|
| GET | `/api/v1/queries/sales/today?assignee=` | 124 | Today queue from `v_sales_today`; `?assignee` scopes to "mine or unassigned" (`queries_handler.ts:63-65`); returns `queue` settings |
| GET | `/api/v1/queries/sales/leads` | 132 | `v_sales_leads` |
| GET | `/api/v1/queries/sales/leads/:lead_id/events` | 136 | timeline from `v_sales_lead_events` |
| GET | `/api/v1/queries/sales/orgs` | 144 | `v_sales_orgs` |
| GET | `/api/v1/queries/sales/week-stats` | 148 | `v_sales_week_stats` |
| GET | `/api/v1/queries/sales/settings` | 152 | `app_setting` (sla, templates, lost_reasons, queue); roster derived from `private_core.app_users` (`queries_handler.ts:222-227`); `setting_event` history |
| GET | `/api/v1/queries/sales/attention` | 156 | `v_sales_attention` |
| GET | `/api/v1/queries/sales/activity?limit=` | 160 | `v_sales_activity` |
| POST | `/api/v1/mutations/sales/leads/:id/status` | 169 | `set_lead_status` (`working`/`lost` only) |
| POST | `…/:id/note` | 179 | `add_lead_note` |
| POST | `…/:id/next-touch` | 189 | `set_next_touch` |
| POST | `…/:id/assign` | 199 | `assign_lead` (+ optional `next_touch_at`) |
| POST | `…/:id/outreach` | 209 | `record_outreach` |
| POST | `…/:id/outcome` | 219 | `record_outcome` (the portal's `OutcomeSheet.tsx`) |
| POST | `…/:id/convert` | 232 | `convert_lead(..., 'green_invoice')`; body `{document_number, amount?, currency?}` (`schemas.ts:81-85`) |
| POST | `/api/v1/mutations/sales/leads/bulk-assign` | 242 | `bulk_assign` (≤200) |
| POST | `/api/v1/mutations/sales/quick-add` | 250 | `ingest_lead('manual', 'manual-<uuid>', …)` (`mutations_handler.ts:248-272`) |
| PUT | `/api/v1/mutations/sales/settings` | 258 | `set_app_setting` for `sla_hours`, `whatsapp_templates`, `lost_reasons`, `queue` |

The header comment (route.ts:3-14) omits `/convert`.

### 3.2 Internal jobs (Bearer `JOB_RUNNER_TOKEN`)

- `POST /api/v1/internal/jobs/lead-wake` (`api/src/internal/jobs/lead_wake_route.ts:50-71`).
  - Body `{}` for the scheduled run, or `{force:true, phone, step?}` for a test run.
  - A forced run is allowed only for a phone in `lead_journey_test_phones` (`wake.ts:182-184`).
- `POST /api/v1/internal/jobs/lead-templates` (`lead_templates_route.ts:38-131`).
  - Actions: `health | status | submit`.
  - `submit` creates one template per call; `sample_pdf_url` must be a Shopify CDN PDF.

### 3.3 Portal routes (`api/src/portal/routes.ts`)

**Customers (cookie `gtp_sid`):**
- `GET /portal/`, `GET /portal/login`
- `GET /portal/l/:token` (page only), then `POST /portal/api/login/consume` (226-235)
- `GET /portal/register/:token`, `POST /portal/api/register` (237-252)
- `GET /portal/api/bootstrap` (254)
- `POST /portal/api/orders` (276)
- `POST /portal/api/restock-request`, `POST /portal/api/logout`

**Lead routes (306-326):**
- `GET /portal/lead/:token`: the same `index.html` in lead mode (`leadPage` 152-159).
- `GET /portal/api/lead/:token`: bootstrap with list prices. Returns 503 when the `customer_portal_live` flag is off, 410 when the link is not live.
- `POST /portal/api/lead/:token/orders`: `submitLeadOrder`.

**Staff (planner or admin) (352-421):**
- `GET /api/v1/queries/portal/registrations`, `…/customer-search`, `…/approved`, `…/catalog`
- `POST /api/v1/mutations/portal/registrations/:id/decide`, `…/login-link`, `…/access/:id/revoke`, `…/catalog/:sku`, `…/catalog/:sku/requests/:id/notified`

### 3.4 Webhook (`api/src/order-intake/route.ts`)

- `GET /webhooks/wa-order-bot` (verify), `POST /webhooks/wa-order-bot`.
- `GET /webhooks/wa-order-bot/health` (78-86) includes a `lead_line` block of booleans (`config.ts:115-125`) and `foreign_waba_dropped`.
- `supabase/functions/wa-order-bot` is a thin receiver that forwards to `WA_WORKER_URL`.

---

## 4. Inbound WhatsApp → lead (order-intake)

- **Two numbers share one webhook and are told apart only by `metadata.phone_number_id`:**
  - order line `972543982444` (`WA_PHONE_NUMBER_ID`, `portal/login.ts:15`);
  - lead line `972547588132` / id `217553368116155` (`WA_LEAD_PHONE_NUMBER_ID`, `portal/lead.ts:29`).
- **Worker front gate** (`worker.ts:205-213`) sits *above* `intakeEnabled`:
  - When `leadJourney` is configured, it owns the lead line (messages, taps, statuses). It is configured whenever `WA_LEAD_PHONE_NUMBER_ID` is set (`worker.ts:447-465`).
  - Older path: `leadCapture.capture` only.
- Lead-line statuses go to `leadJourney.handleStatus` (`worker.ts:131-134`). Lead-line echoes return `lead_line_echo` and never mark the order bot human-handled (`worker.ts:146`).
- **Capture** (`sales/lead_capture.ts`):
  - It POSTs `{route:'ingest', source, external_id: wamid, contact_name: profile_name, phone:'+'+from, created_at, platform:'whatsapp', campaign_name: referral.source_id, ad_name: referral.headline, message}` to `SALES_LEAD_INGEST_URL` (70-98, 128-139).
  - Headers: `Authorization: Bearer <service role>` and `x-lead-ingest-token`; 10 s timeout.
  - It is skipped when disabled or unconfigured, for content type `other`, or with no sender.
  - The journey captures only text messages and appends `\n(תפריט מזוהה: <label>)` to the note (`journey.ts:103-107`).
- **Journey decisions:**
  - `firstMessage` (92-122): under a per-phone advisory lock (216-226), "first" = no non-failed `first_menu`/`general_reply` outbound row for this phone on the lead line in 30 days (227-239). Dry-run rows count unless the phone is on the test allowlist.
  - `followUp` (128-144), `tap` (153-185), `stop` (146-151).
  - `latestLead` (267-278) = the phone's oldest open lead, otherwise its newest closed one.
  - `knownCustomer` = `wa_customer_map` has the phone with a `shopify_customer_id` (283-287).
- **"The menu" / PR #328** (`git show 04cb0f6`):
  - Each menu PDF ends with a button: a wa.me link prefilled with e.g. `"היי, ראיתי את תפריט תמציות התה של GT ואשמח לשמוע איך מתחילים"`.
  - Before #328 that message hit the 30-day silence rule. Now any post-first message gets a desk task plus `TEXT.moreInfo` with the FAQ CTA, at most once per day.
  - The PDF itself is delivered as the `document` header of the first interactive message (`lead_texts.ts:89-100`) and as the header of wake template 1 (`wake.ts:150-153`).
- **Send port** (`whatsapp/send.ts`): POST `{WA_API_BASE_URL}/{WA_GRAPH_VERSION}/{phone_number_id}/messages` via Dualhook. `sendRaw` (99-101) carries any Cloud-API body. The lead line uses its own key, `WA_LEAD_SEND_TOKEN`.
- **The lead line's only exit, `lead_line.ts:81-112`:**
  - refuses opted-out phones, writing no row;
  - writes the outbound log row **first**;
  - live only if the gate is open or the phone is on the allowlist (86);
  - otherwise the status is `dry_run:<kind>`;
  - with no key, the status is `send_failed:no_lead_send_token`.
- **Send kinds:** `first_menu`, `general_reply`, `free_text_reply`, `customer_link`, `order_link`, `more_info`, `not_now`, `optout_confirm`, `order_confirm`, `wake`. Each is mirrored as `lead_event auto_message {kind, step, send_id, dry_run, wamid, …}`, with step = triggering wamid, idem_key, or `"n:attempt"` for wake.
- **Button ids:** `lj.order`, `lj.more`, `lj.not_now` (`lead_texts.ts:26-30`). Spec §3.6 also listed `lj.order_now`, `lj.remind_30`, `lj.not_for_us` and `lj.stop`; these were retired by D-033 and the tests treat them as unknown.
- **Templates** (`lead_templates.ts:34-61`), language `he`:

  | Template | Category | Content |
  |---|---|---|
  | `gt_lead_wake_1` | MARKETING | document header; body {{1}} name, {{2}} menu label, {{3}} signer; footer; URL button `LEAD_LINK_BASE{{1}}` |
  | `gt_lead_wake_2` | MARKETING | body name + signer; FAQ URL button |
  | `gt_lead_wake_3` | MARKETING | order URL button |
  | `gt_lead_wake_4` | MARKETING | order URL button |
  | `gt_lead_order_confirmation` | UTILITY | {{1}} lines on one line, {{2}} total |

  - `LEAD_LINK_BASE = https://gt-factory-os-api-production.up.railway.app/portal/lead/`, because `order.gteveryday.com` had no DNS record (`lead_templates.ts:14-17`).
  - The wake signer is `lead_journey_signers[lead_event.actor of the anchor outcome]`. The wake step is skipped (`no_signer`) when the actor has no entry, and (`no_name`) when the lead's `contact_name` has no usable first name.
- **Draft-only lead orders** (`portal/lead.ts:137-225`):
  - pricing via `pricer.listPrices()` minus planner switches;
  - the price must match what the page showed (otherwise 409 `PRICE_CHANGED`);
  - bottles in pairs; ₪800 ex-VAT minimum;
  - `checkTotal` guard → `draftOrderCreate`, never complete (tested in `portal/__tests__/lead.test.ts:124`).
  - `drafted()` then: marks the submission drafted → `closeLinks(lead)` (every link for the lead gets `used_at`) → `lead_event draft_order {draft_id, draft_name, total_ex_vat, idem_key}` → confirmation → Telegram to the owner.

---

## 5. What feeds leads in (`supabase/functions`)

- **`sales-leads-poll`** (`index.ts`): routes `health`, `probe`, `poll`, `backfill`, `daily`, `reminders`, `ingest`, `pulse`, `resend_domain_status` (18-28, 1414-1461).
  - **`/ingest`** (948-1088): requires the `x-lead-ingest-token` header to equal `LEAD_INGEST_TOKEN`, plus platform JWT verification.
  - It hydrates Make bundles from Graph when it can, and normalises the raw or flat shape (`_lib/ingest_body.ts`). In the flat shape, `message`/`notes` become `meta.notes`.
  - `lookupShopifyCustomer(phone, email)` makes one Shopify search, `email:X OR phone:Y`, and takes the first hit (385-409). It then calls `ingest_lead(…, match?.id, lead.city)` and emails an alert **only when `was_new`**, recording `alert_sent`.
  - It returns `{lead_id, was_new, alerted, …, org_id}`. **`merged` is not returned yet** (0361:41-44).
  - Unmappable payloads go to `lead_reject`.
- **Sources feeding `/ingest`:**
  - Make (all live Facebook Lead Ads, `intake_mode='make'`, D-006). An hourly `pulse` is the liveness check.
  - `website_lead_intake` (`source:'website_form'`).
  - The WhatsApp lead line (`whatsapp_ctwa` / `whatsapp_unattributed`).
  - The Meta poll (`facebook`) exists but `meta_poll.enabled=false`.
  - **No Instagram/Messenger intake** (U-054 parked).
- **`website_lead_intake`** (`index.ts`): public (verify_jwt false); CORS allows gteveryday.com and greenteaeveryday.myshopify.com (70-74).
  - Honeypot `company_website`; rejects submissions under 3 s.
  - Required fields: `contact_name`, `venue`, `city`, `phone`.
  - `form_name ∈ partner_enquiry | landing-site-{chai,matcha,iced-tea,ube}` (81-87).
  - **`external_id = web-<YYYY-MM-DD>-<last 9 digits>`**, i.e. one lead per phone per day (207-209).
  - It POSTs to `/ingest` with `display_name:venue`, `city`, `message`, `platform:'website'`, `is_organic:true`, and no `campaign_name`.
  - When `was_new`, it writes a `note` event directly (actor `system:website_form`) carrying role, interest, page and referrer. This is a direct insert so `first_touch_at` is not set (264-303). The note is lost when the submission joins an existing open lead (0361:41-44).
- **Dedup / matching:**
  - `(source, external_id)` idempotency;
  - one open lead per phone (0361);
  - org matching by shopify id > phone > email > business domain;
  - `possible_duplicate_of` set when the phone's only earlier leads are closed;
  - `matched_existing_customer` events with `matched_by` = `shopify_lookup` (ingest), `daily_backfill` (routeDaily), or `phone_e164`/`email` (0330 backfill).
- **City:** `org.city` is written since 0345, gap-fill only (`coalesce`).
- **Assignment:** **no intake path sets `assignee`.** It stays null until staff assign.
- **Daily** (718-830):
  1. Backfill `org.shopify_customer_id` for open leads by Shopify search.
  2. Convert open leads whose org has a Shopify id, using the earliest non-cancelled order with `createdAt >= lead.created_at` (`_lib/convert.ts:52-72`), via `convert_lead(..., 'shopify_order', order.created_at)`. `converted_order_ref` is the order **name**.
  3. Send the heartbeat email.
- **Reminders:** at 06:00 Israel, one digest per assignee of due `next_touch_at` callbacks. An unowned or inactive assignee falls back to Tom (1181-1300). The claim is a `reminder_sent` row.
- **Staff deep link in alerts:** `${PORTAL_BASE_URL}/sales/leads?lead=<lead_id>` (`_lib/email.ts:169`). Staff-auth only.

---

## 6. Link / token machinery

All tokens are `randomBytes(32).base64url` and only the `sha256` hex is stored (`portal/session.ts:11-12`).

| Link | URL | Identifies | TTL | Use |
|---|---|---|---|---|
| Customer login | `/portal/l/<token>` | `customer_portal.link{purpose:'login', wa_phone, access_id}` | **10 min** when the customer sends A1 to the order line; **24 h** from a staff/invite link (`login.ts:28-30,153`) | single use: GET never consumes; POST `/consume` sets `used_at` atomically (`store.ts:136-137,183-185`); then a session cookie `gtp_sid` for **180 days** (`session.ts:9`); rate limit 5 per phone per hour |
| Registration | `/portal/register/<token>` | `link{purpose:'register', wa_phone}` | 24 h | single use; creates a pending `registration`; staff approve against a Shopify GID → `access` |
| **Lead ordering link** | `/portal/lead/<token>` (base `publicUrl()` = `PORTAL_PUBLIC_URL` or the Railway host) | `customer_portal.lead_link{lead_id, wa_phone}` | **14 days** (`LEAD_LINK_DAYS`, `lead.ts:30`) | **reusable until an order is drafted**, then every link of that lead closes (`closeLinks`); a dead link still answers a replay of its own order; a new link is minted on every `lj.order` tap and every wake step except step 2 |
| Campaign link | `gteveryday.com/?c=matcha|ube|chai|tea|menu` (in `/home/user/gt-site`, `src/index.html:2439-2449`, PR gt-site#34) | **nothing**: no token, no identity | n/a | opens the site lead dialog; after the form it offers one wa.me button to `972547588132` with the prepared text `היי, אני מעוניין ב<line>`; `?c=` survives only as the page URL stored in the website-form note and the `interest` field |

**Gate:**
- Customer data routes require `customer_portal_live.enabled` plus the allowlist (`login.ts:56-60`).
- Lead routes check only `enabled` (`routes.ts:308, 319`).

---

## 7. Flags and gates

**`private_core.feature_flags`:**
- The only sales/portal key is **`customer_portal_live`**, seeded `enabled:false, allowlist:""` (0355:104-107). The spec (L89-90) reports it **live with allowlist `*`**.
- The other keys are core or Shopify keys (`global_readonly`, `jobs_paused`, `shopify_*`) and are not relevant here.

**Env vars (Railway API):**
- `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED`: the D-005 gate, read at every send (`config.ts:109-110`). Set to **`false`** by `.github/workflows/railway-lead-env.yml:94`.
- `SALES_LEAD_CAPTURE_ENABLED` (set `true` by the same workflow).
- `WA_LEAD_PHONE_NUMBER_ID`, `SALES_LEAD_INGEST_URL`, `LEAD_INGEST_TOKEN` ("never rotate"), `WA_LEAD_SEND_TOKEN`.
- `WHATSAPP_ORDER_INTAKE_ENABLED`, `WHATSAPP_AUTO_COMMIT_ENABLED`.
- `WA_PHONE_NUMBER_ID`, `WA_SEND_TOKEN`, `WA_WABA_ID` (comma list), `WA_API_BASE_URL`, `WA_GRAPH_VERSION`.
- `PORTAL_PUBLIC_URL`, `JOB_RUNNER_TOKEN`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_TOM_CHAT_ID` (owner notices, `portal/deps.ts:30-37`), `ORDER_INTAKE_ALERT_WEBHOOK_URL`.

**Env vars (Edge functions):** `LEAD_INGEST_TOKEN`, `META_PAGE_ACCESS_TOKEN`, `META_PAGE_ID`, `META_GRAPH_VERSION`, `RESEND_API_KEY`, `RESEND_FROM`, `PORTAL_BASE_URL`, `DATABASE_URL_POOLED`.

**Data gates (`sales_core.app_setting`):** `meta_poll.enabled`, `intake_mode.mode`, `lead_menus`, `lead_journey_test_phones`, `lead_journey_force_template`.

---

## 8. Test invariants

**`api/test/sales_leads_*.test.ts`:**
- **convert:**
  - S50 the first order at or after the lead converts it.
  - S51 an earlier order never converts.
  - S52 an order at the same instant counts.
  - S53 a cancelled order is not evidence.
  - S54 no linked Shopify customer means no automatic conversion.
  - S55 junk input means "no".
  - S56/S57 the snapshot shape equals 0330's.
- **ingest_route:**
  - S90/S91 raw `field_data` goes through the poll's mapper; unknown fields raise an alarm.
  - S92 a flat body works (manual entry, website).
  - S93 no identity → rejected.
  - S94 a manual lead gets a stable id (idempotent).
  - S95 malformed input is rejected with a reason.
  - S96 the source defaults to `manual`, never `facebook`.
  - S97 a name-only lead is kept as history.
  - S99–S101 the website message is kept as `notes`; `notes` is a synonym of `message`; no message → `null`.
  - S102 two submissions on the same day = one lead.
  - S103 a Meta message question maps.
- **make_intake:**
  - S80–S88 under Make, a disabled poll is normal; a stale or absent pulse is an alarm; pulse staleness is ignored in poll mode.
  - S90–S92 a reject is an alarm even with a healthy pulse.
  - S93–S98 Make bundles map, including camelCase metadata and unknown questions.
- **poll_alerts:**
  - S11–S11c alert recipients are staff only; the heartbeat goes to Tom only.
  - S12–S21c subject framing (new vs 🔁 known customer); working tel/wa.me links; **"S21 the alert never addresses the lead — no outreach, ever"**.
  - S22–S28 heartbeat logic.
  - Digest: addressed to the assignee; a lead is never a recipient.
  - S104–S108 enquiry text present, clamped, escaped.
  - S109–S111 an unalerted lead is an alarm.
- **poll_flow:**
  - S30 a lead is written and alerted exactly once.
  - S31/S32 the cursor advances only after success.
  - S33/S34 overlapping windows cause no duplicates.
  - S35 a malformed lead is rejected without stopping the batch.
  - S36/S37 backfill emails nothing; an empty cursor covers 90 days.
  - S40 a failed email leaves no `alert_sent`, so it retries.
  - S41 a disabled poll does nothing.
- **poll_mapping:** S01–S10 field registry; phone normalisation mirrors the SQL (`+9720` defect); S60 a lead with no id dedupes on identity + day.
- **token_diag:** S70–S76 never leaks a token.

**Workspace (`sales_workspace.test.ts`, `sales_v2.test.ts`):**
- Non-sales roles are refused. The test names still say "non-admin".
- An outcome always leaves a next touch.
- `answered_progressing` moves `new` → `working`.
- `lost` without a reason is a 422.
- `won` is never settable via status.
- Outreach does not stop the SLA clock; a note is a first touch.
- Quick-add goes through `ingest_lead`.
- `working` without a next touch is refused.
- Assignment: off-roster is refused; the due date travels in the same transaction; bulk assign is atomic.
- Queue order comes from settings.
- Uncontactable leads stay out of the queue.
- Settings writes are audited.

**Journey (`api/src/order-intake/sales/__tests__`):**
- `journey`: menu vs general reply; the post-first-message desk task once per day; the 24 h staff rule; opt-out; buttons; 131050 opts out.
- `lead_db`: gate closed → a dry-run row and nothing sent; the gate is read at send time; allowlist phones get real sends; opted-out phones get no row; sent→delivered→failed; wake candidates read both lines through one normaliser; the 0361 tap ownership.
- `wake`: slots, holidays, 48 h spacing, 4 messages maximum, 131049 retry, forced run allowlist-only.
- `lead_playbook` / `lead_texts` / `lead_templates`: byte-equal to the pinned playbook; WhatsApp length limits; one link button per wake message.
- Portal `lead.test.ts`: **"the source cannot reach a completion"**; replay and stale paths stay drafts.

**pgTAP:** `db/tests/0360_lead_journey.test.sql` (22 assertions) and `db/tests/0361_sales_one_open_lead_per_phone.test.sql` (27), among them "one phone, one lead", "the Shopify id stays with the org that holds it", "after a lost lead, the same phone starts a new lead".

---

## 9. Answers

**A. Canonical identity**
- **Lead:** `sales_core.lead.id` (uuid) is the record key. `unique(source, external_id)` makes intake idempotent. Within an open lead, the **person key is `phone_e164`** (`+972…` from `normalize_phone_il`). Email-only leads never merge (0361 test).
- **Business:** `sales_core.org.id`.
- **Customer:** Shopify customer GID (`gid://shopify/Customer/<n>`). It is stored as a reference in `org.shopify_customer_id` (unique), `order_intake.wa_customer_map.shopify_customer_id` and `customer_portal.access.shopify_customer_id`.
  - No Green Invoice id is stored anywhere. A GI *document number* appears only as `converted_order_ref` with `evidence:'green_invoice'`.
  - A "portal account" is a `customer_portal.access` row (`access_id`, `wa_phone` unique) plus sessions.
  - Phone formats differ: `sales_core` uses `+972…`; `order_intake` and `customer_portal` use digits-only `972…` (`types.ts:78-81`). `wake.ts` bridges them with `substr(phone_e164, 2)`.
- **Lead → customer:** there is no in-system "create customer" step.
  1. Staff create the customer in Shopify and GI (skill `customer-setup-shopify-gi`) and complete the lead's draft. For a phone close, staff instead POST `/convert` with the GI document number.
  2. `routeDaily` back-fills `org.shopify_customer_id` by phone/email search.
  3. `convert_lead` sets `status='won'`, `converted_order_ref` (Shopify order name), `converted_amount`, `converted_order_placed_at`, and writes `converted` + `status_change` events.
- `won` is only reachable through `convert_lead`. The CHECK requires `converted_order_ref`, and `set_lead_status` rejects `won`.
- A `draft_order` event does **not** convert a lead, but it stops the wake sequence.

**B. Events a new product can append to**
- The only extensible activity log is `sales_core.lead_event`:
  - append-only, enforced by triggers (0320);
  - closed vocabulary; widening means replacing the CHECK with a superset, additive only (0334:59-60, 0340:71-73);
  - `payload` is free jsonb;
  - `actor` is a free string. Conventions: staff `display_name`/email, or `system:<component>` (`system:lead-journey`, `system:website_form`, `system:sales-leads-poll`, `system:ingest`, `system:migration_NNNN`).
- **Writing rules seen in code:**
  1. Prefer the `sales_core` functions: they lock the lead and write the row change and the event in one transaction, and they hold the invariants (`won` = evidence only; `lost` needs a reason; an open lead keeps a next touch).
  2. Automated or system notes are inserted **directly** so they do not set `first_touch_at`. `add_lead_note`, `set_lead_status` and `record_outcome` all call `touch_first` (`journey.ts:247-255`, `website_lead_intake:286-291`).
  3. Use a partial unique index as an idempotency claim, with `insert … on conflict do nothing` (`reminder_sent`, `auto_message` by `(kind, step)`, `repeat_contact`).
  4. The spec says the worker should reuse `api/src/sales` for CRM writes (§3.5 L208-209). The journey code still issues direct SQL for events.
- **Side effects to know:**
  - `v_sales_attention.stalled` counts **any** event as activity, so automated events reset the 14-day stall clock.
  - `v_sales_first_response` counts only `outreach`, `outcome` and `status_change`.
  - `v_sales_today`'s conversion row keys off the `converted` event.
- **Unused, existing types:** `qualified`, `kit_sent` (both feed "measurable=false" funnel metrics) and `question_logged`.

**C. Ownership and next touch**
- Both live on `sales_core.lead`: `assignee` (text email) and `next_touch_at`.
- **Assignee** is set only by staff with the sales capability, via `/assign` and `/bulk-assign` → `assign_lead`/`bulk_assign`. It is validated by `assert_assignee` against active `private_core.app_users` with role in `sales_rep`, `planner`, `admin`. The picker roster uses the same predicate (`queries_handler.ts:222-227`). Unassign with `''`. No intake path auto-assigns.
- **`next_touch_at`** is set by:
  - `/next-touch` → `set_next_touch`;
  - `/outcome` → `record_outcome`: explicit value, otherwise `no_answer` = +1 business day 09:00 Israel, `whatsapp_sent` = +2; `answered_progressing` requires an explicit date;
  - `/status working` with `next_touch_at`;
  - `/assign` with `next_touch_at`;
  - the system: the journey desk task sets `set_next_touch(now(), 'system:lead-journey')`.
- Consumers: the Today queue, the 06:00 reminder digest per assignee, and the wake sequence (messages 2–4 are timed to the follow-up dates).

**D. Deployment status** (as far as the repo shows; I did not query production)
- **Live (merged on main; per the spec, Railway auto-deploys on merge; migrations up to 0361 present):**
  - the `sales_core` CRM and staff workspace API;
  - Make → `/ingest`; the website form → `/ingest`;
  - lead-line capture: a WhatsApp lead was captured in production on 2026-09-29 (0361 header);
  - the lead-journey code (#321, #323, #327, #328);
  - the `lead_wake_sequence` cron;
  - the customer portal (spec says flag on, allowlist `*`);
  - the daily conversion, reminders and sleeping-radar crons;
  - the order bot ("Status: ON, drafts-only", `order-intake/README.md`).
- **Merged but gated / dry-run:**
  - every automated lead-line send is a dry run (`SALES_CUSTOMER_OUTREACH_WRITE_ENABLED=false`) except allowlisted test phones;
  - first messages fall back to the general reply until `lead_menus` holds approved PDFs (seeded `{}`);
  - the wake job is effectively a no-op, because eligibility needs a *delivered real* first message;
  - the lead order page works but its confirmation is dry-run;
  - the Meta poll is disabled (`intake_mode='make'`);
  - the landing pages' `campaign_map` rows are prep only; the pages were unpublished as of 0344 (2026-09-03).
- **Specified or pending, outside code:**
  - Tom's approval of the menu PDFs (spec §3.4);
  - Meta approval of the 5 templates (U-052); the first submit failed, the cause was fixed in #326, and the current status is unknown;
  - `WA_LEAD_SEND_TOKEN` on Railway (Tom);
  - flipping the gate: Tom's written approval plus a ≥24 h soak.
- **Not built:**
  - Instagram/Messenger intake (U-054);
  - `/ingest` returning a `merged` flag; the website form keeping its note on a join;
  - emitters for `qualified`, `kit_sent`, `question_logged`;
  - any API or UI for the funnel, triage, answer bank or radar views;
  - radar chain roll-up.

---

## 10. Discrepancies and gotchas

1. The spec's §2 is outdated in several places:
   - `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` *is* now read (`config.ts:109-110`);
   - sends are now logged;
   - statuses keep `phone_number_id` and error codes;
   - login links are **10 min** (customer-requested) or 24 h (staff), not a flat 24 h.
2. "One open lead per phone" is function-level only. Any direct `INSERT INTO sales_core.lead` bypasses it, and older duplicate open pairs still exist.
3. `set_lead_status` has no from-status guard. A `won` or `lost` lead can be moved back to `working` (or a `won` lead to `lost`) through `/status`. `converted_order_ref` is left in place.
4. `opt_out_at` is invisible in every `api_read` view.
5. `lead_journey_force_template` is read but never seeded.
6. `customer_portal.lead_link.wa_phone` is digits-only while `sales_core.lead.phone_e164` is `+972…`.
7. There are three phone→customer maps (`wa_customer_map`, `customer_portal.access`, `org.shopify_customer_id`), and no table reconciles them.
8. A lead order's draft has no Shopify customer. Conversion therefore depends on staff attaching a customer whose phone or email Shopify's search can find. Per GT convention the phone is often only on the address (0330:43-51).

---

## 11. File index (absolute paths)

**Spec and docs**
- /home/user/gt-factory-os/docs/superpowers/specs/2026-09-28-lead-journey-design.md
- /home/user/gt-factory-os/docs/superpowers/specs/2026-09-24-customer-portal-design.md
- /home/user/gt-factory-os/docs/superpowers/plans/2026-09-25-customer-portal-ux-gate.md (§5.5 U-16..U-26 lead dialog; §5.6 U-27..U-39 approved journey and FAQ copy)

**Migrations** — /home/user/gt-factory-os/db/migrations/
- 0265_order_intake.sql, 0266_order_intake_pricing_mode.sql, 0273_order_intake_intro_sent.sql, 0274_order_intake_session_states.sql, 0275_order_intake_commit_states.sql
- 0318_sales_core_leads.sql, 0319_sales_core_phone_normalisation.sql, 0320_sales_core_lead_event_append_only.sql, 0321_sales_core_ingest.sql
- 0322_sales_core_workspace_writes.sql, 0323_sales_api_read_views.sql, 0324_sales_next_touch_integrity.sql, 0325_sales_assignment_v2.sql, 0326_sales_queue_shape_and_attention.sql, 0327_sales_activity_feed.sql
- 0328_sales_leads_poll_runtime.sql, 0329_sales_intake_mode.sql, 0330_sales_org_shopify_backfill.sql, 0332_sales_ingest_lead_matched_by.sql
- 0333_app_users_sales_rep_role.sql, 0334_sales_reminder_sent_event.sql, 0335_sales_convert_evidence_kind.sql, 0336_app_users_sales_planner_role.sql, 0337_planner_holds_sales.sql
- 0340_sales_funnel_metrics.sql, 0341_sales_backlog_triage.sql, 0342_sales_answer_bank.sql, 0343_campaign_map_matcha.sql, 0344_campaign_map_landing_pages.sql
- 0345_sales_ingest_lead_city.sql, 0346_sales_sleeping_radar.sql, 0347_sales_sleeping_radar_cron.sql, 0348_sales_convert_order_timing.sql, 0349_suppress_test_lead_fixtures.sql
- 0355_customer_portal.sql, 0356_portal_registration_email.sql, 0357_customer_portal_item_availability.sql, 0358_customer_portal_item_availability_upcoming.sql
- 0360_lead_journey.sql, 0361_sales_one_open_lead_per_phone.sql

**pgTAP tests**
- /home/user/gt-factory-os/db/tests/0360_lead_journey.test.sql
- /home/user/gt-factory-os/db/tests/0361_sales_one_open_lead_per_phone.test.sql

**API**
- /home/user/gt-factory-os/api/src/sales/{route.ts, mutations_handler.ts, queries_handler.ts, schemas.ts}
- /home/user/gt-factory-os/api/src/auth/session.ts (roleAllowsSales :65-67)
- /home/user/gt-factory-os/api/src/order-intake/{route.ts, worker.ts, webhook.ts, types.ts, config.ts, store.ts, README.md}
- /home/user/gt-factory-os/api/src/order-intake/whatsapp/send.ts
- /home/user/gt-factory-os/api/src/order-intake/sales/{lead_capture.ts, journey.ts, lead_line.ts, lead_texts.ts, lead_templates.ts, wake.ts}
- /home/user/gt-factory-os/api/src/order-intake/sales/__fixtures__/whatsapp-lead-journey@7fd25f8.md
- /home/user/gt-factory-os/api/src/order-intake/sales/__tests__/ (journey, lead_db, lead_capture, lead_playbook, lead_templates, lead_texts, wake)
- /home/user/gt-factory-os/api/src/internal/jobs/lead_wake_route.ts
- /home/user/gt-factory-os/api/src/internal/jobs/lead_templates_route.ts
- /home/user/gt-factory-os/api/src/portal/{lead.ts, routes.ts, login.ts, session.ts, store.ts, deps.ts, catalog.ts, pricing.ts, orders.ts}
- /home/user/gt-factory-os/api/src/portal/public/index.html (lead mode :593, :1343-1352)
- /home/user/gt-factory-os/api/src/portal/__tests__/{lead.test.ts, lead_routes.test.ts}
- /home/user/gt-factory-os/api/test/sales_leads_{convert, ingest_route, make_intake, poll_alerts, poll_flow, poll_mapping, token_diag}.test.ts
- /home/user/gt-factory-os/api/test/sales_workspace.test.ts
- /home/user/gt-factory-os/api/test/sales_v2.test.ts

**Edge functions**
- /home/user/gt-factory-os/supabase/functions/sales-leads-poll/index.ts
- /home/user/gt-factory-os/supabase/functions/sales-leads-poll/_lib/{ingest_body.ts, mapping.ts, convert.ts, email.ts, ingest.ts}
- /home/user/gt-factory-os/supabase/functions/website_lead_intake/index.ts
- /home/user/gt-factory-os/supabase/functions/wa-order-bot/index.ts
- /home/user/gt-factory-os/supabase/functions/sales-sleeping-radar/index.ts
- /home/user/gt-factory-os/supabase/functions/portal-registration-notify/index.ts

**CI**
- /home/user/gt-factory-os/.github/workflows/railway-lead-env.yml

**Sibling repos (read-only context)**
- /home/user/gt-site/src/index.html:2439-2449 (`?c=` campaign links)
- /home/user/gt-site/tools/patch_lead_dialog.py:133-142 (wa.me lead line and the five ready lines)
- /home/user/Sales-Machine/doctrine/decisions.md (D-024..D-034)
- /home/user/Sales-Machine/CURRENT_STATE.md:91-101 (U-049..U-054 status)
