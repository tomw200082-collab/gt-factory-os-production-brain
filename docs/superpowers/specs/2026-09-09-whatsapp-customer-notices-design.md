# WhatsApp Customer Notices — Design Spec ("מה אני מקבל?")

> **Date:** 2026-09-09 · **Status:** DRAFT — pending Tom written approval via PR review
> **Origin:** `/brainstorming` session 2026-09-08/09 with Tom; research memo
> `2026-09-09-whatsapp-customer-notices-research.md` (same PR).
> **Builds on:** the catalog-cart bot live since 2026-09-08 (gt-factory-os#272): carts → Shopify draft, fixed receipt, no LLM, no prices.
> **Lanes:** `backend-db` (schema + API + jobs) · `integration` (LionWheel reads, WhatsApp templates) · `portal` (one tab on `/credit-tracking`, own tranche).
> **Stock truth:** untouched. Every notice is a *read* over `orders_mirror`, `credit_tasks` and Shopify. No ledger write, no projection write.

---

## §G — Goal (one line)

A customer who orders from the WhatsApp catalog hears from GT automatically at the three moments that matter — *we got it*, *this is what is coming and when*, *it arrived* — with the "what is coming" message sent only after picking, automatically when the pick is complete and only after a human approves it when the pick is short.

## Done / observable

- A full-pick order sends "יוצא אליכם מחר: …" with no human touch, within one poll cycle of LionWheel reaching `ASSIGNED` + `pick_status = PICKED`.
- A short-pick order never reaches the customer unapproved: it appears on `/credit-tracking` → tab "אישורי ליקוט חלקי", Tom gets a reminder email at 16:30, and the message goes out only after "אשר ושלח".
- A delivered order sends "נמסר ✅" with the proof-of-delivery photo when LionWheel has one, and a one-line path to complain.
- Every notice is one row in `order_intake.customer_notices` with state, template, WhatsApp message id and who approved it. Nothing is sent twice (unique dedupe key).
- Shadow mode proves the trigger logic on real orders for ≥1 week before a single customer receives anything.

---

## §C — Decisions (Tom, in writing, 2026-09-08/09)

| # | Decision | Where |
|---|---|---|
| 1 | Systematic ordering via the WhatsApp catalog with **fixed automatic messages, no AI agent** talking to customers | 2026-09-08 |
| 2 | Catalog carries **no prices**; each customer billed their last-paid price | 2026-09-08 |
| 3 | Stations: 3 merged into 4 (delivery day told once), 6 dropped; v1 includes 0 (announcement), 7 (delivered + invoice by email), 8 (payment reminders), 9 (reorder nudge) | 2026-09-08 |
| 4 | "Approved" = LionWheel status **ASSIGNED** (normally the day before delivery) | 2026-09-08 |
| 5 | **Stock truth is not stable → orders are confirmed only after picking.** Full pick → automatic message. Partial pick → message only after human approval. The customer's question is "what am I getting?" | 2026-09-09 |
| 6 | Partial-pick approval queue lives in the **portal, on the existing `/credit-tracking` screen, with an email reminder**. For now the reminder goes **only to `tom@gteveryday.com`** | 2026-09-09 |

Everything else below is the proposed design and is open until Tom approves this spec.

---

## §1 — The three promises

The whole system is three promises to the customer. Everything else is plumbing.

| Promise | Message | When | Who sends |
|---|---|---|---|
| **1. We got it** | קיבלנו + list of what they asked for + *"נעדכן עד 17:00 ביום שלפני האספקה מה יוצא אליכם"* | seconds after the cart | bot (exists; wording updated) |
| **2. This is what is coming, and when** | יוצא אליכם ב-{day}: + list of what was **picked** (+ what is not coming and what we do about it) | after picking, before delivery, by 17:00 day-before | auto when full · human-approved when short |
| **3. It arrived** | נמסר ✅ + POD photo + "משהו חסר? השיבו כאן" + invoice by email | on LionWheel COMPLETED | auto |

Promise 2 is the one nobody in the market does honestly: everyone confirms *the order*; we confirm *the pick*. That is the direct consequence of decision 5 and of GT's inventory reality.

---

## §2 — Hard fact that shapes the design (verified in code, 2026-09-09)

**LionWheel no longer tells us *which lines* were short.** Between 2026-08-13 and 2026-08-16 LionWheel removed `picked_quantity` and `status` from `order_items[]` (see `api/src/integrations/lionwheel/reconciliation.ts` "Task-level pick fallback (2026-08-24)"). What survives is one task-level field, `pick_status`, and it arrives **only on `/api/v1/tasks/show/<id>`**, not on `/tasks/index` (verified live 2026-08-24, `schemas.ts`).

- `pick_status = 'PICKED'` ⇒ the task was picked in full ⇒ every line ships at ordered quantity. **Automatic message is safe.**
- Any other value (`PARTIALLY_PICKED`, `NEW`, absent) ⇒ we know it is short but **not which lines or by how much**. A human must enter that from the LionWheel app or the picker.

This is exactly the split Tom asked for, and it means the partial-approval screen is not a rubber stamp: the human *supplies the truth* (what is going out per line), then approves the message. It also means `credit_tasks` today are created only after delivery (terminal status) and often land as `lw_pick_data_missing` exceptions rather than rows — the day-before review is *better* shortage data than the system has now. Feeding it back into `credit_tasks` / `FG_OUT_PICK` touches stock truth and is **out of scope here**; listed under §11 for a separate Tom decision.

Second fact: **LionWheel reaches us by polling, not webhooks.** `lionwheel_poll` runs every 15 min (pg_cron, migration 0030/0031). A 15-minute lag is fine for a day-before message and for "delivered". v1 therefore adds **zero LionWheel configuration**; the LionWheel webhook (org settings → API tab, `github.com/lionwheel/api`) is a later latency improvement, not a dependency.

---

## §3 — Stations, end to end

Numbering keeps the brainstorm's labels so the history reads.

### Station 1 — קיבלנו (exists; wording change only)

Reply to the cart, inside the 24-hour customer window (free-form text, no template, no cost). Change the closing lines of `buildOrderReceipt`:

```
קיבלנו את ההזמנה 🙏
• DETOX 1000ml — 12 יח'
• LUI LOW 1L — 6 יח'
עד 17:00 ביום שלפני האספקה נשלח לכם מה יוצא בפועל ואת יום האספקה.
לשינוי — שלחו עגלה מעודכנת עד 14:00 היום.
```

- After 14:00 the last line becomes: `ההזמנה נכנסה לסבב הבא. לשינוי — שלחו עגלה מעודכנת עד 14:00 מחר.`
- **Second cart before 14:00 from the same customer = update** (research gap E): the bot updates the open draft instead of creating a second one, and replies `עדכנו את ההזמנה 👍` + the new list. One draft per customer per intake day.
- The old closing line `מאשרים אצלנו ונחזור אליכם לאישור סופי` is dropped — the promise above replaces it. Unresolved item codes still show `(לא זוהה — נבדוק)`.

### Station 2א — יוצא אליכם (full pick, automatic)

**Trigger:** poll sees `orders_mirror.lw_status = 'ASSIGNED'` for a task whose `wp_order_id` maps to a WhatsApp-notified customer (§5), and `/tasks/show` returns `pick_status = 'PICKED'`, and `pickup_at` is not null.

**Template `gt_order_confirmed_full` (Utility, he):**
```
ההזמנה שלכם מוכנה ויוצאת אליכם ב{{1}} 🚚
יוצא: {{2}}
נראה משהו לא נכון? השיבו כאן.
```
`{{1}}` = day word + date from `pickup_at` ("מחר, יום שלישי 10.9" / "יום חמישי 12.9"). `{{2}}` = ordered lines rendered on one line: `DETOX 1000ml ×12 · LUI LOW 1L ×6` (Meta forbids newlines inside a template variable; body variable ≤1024 chars is far above GT's line counts).

**Timing:** send immediately when both conditions hold, inside quiet hours (§6). ASSIGNED usually lands the day before; if the pick completes on delivery morning the message goes at 07:00.

### Station 2ב — יוצא אליכם (short pick, human-approved)

**Trigger:** `ASSIGNED` and `pick_status ≠ 'PICKED'` (or `/show` fails twice) → create a notice in state `pending_approval` with one line per ordered line, `qty_delivering` prefilled = `qty_ordered`. No message yet.

**Screen:** `/credit-tracking` → new tab **"אישורי ליקוט חלקי"** (Hebrew RTL like the rest of that screen; portal tranche). One card per pending notice:
- header: customer, Shopify order #, delivery day, LionWheel task link
- per line: item · הוזמן · **יוצא** (editable number) · when short → **מה עושים**: `יזוכה בחשבונית` / `יישלח בסבב הבא` / `הוחלף ב-…` (free text)
- live preview of the exact message
- buttons: **אשר ושלח** · **לא לשלוח** (state `suppressed`, reason required — the human calls instead)
- audit: `approved_by`, `approved_at`, `change_log` row `CUSTOMER_NOTICE_APPROVED` / `_SUPPRESSED`. Roles = the roles allowed on the existing resolution mutation (admin + viewer); extend to Avi's role in the tranche if it differs.

**Template `gt_order_confirmed_partial` (Utility, he, two quick-reply buttons):**
```
ההזמנה שלכם יוצאת אליכם ב{{1}} 🚚
יוצא: {{2}}
לא זמין הפעם: {{3}}
{{4}}
[בסדר]  [רוצה לדבר]
```
`{{3}}` = short lines `LUI LOW 1L ×2 מתוך 6` · `{{4}}` = the resolution sentence per line, e.g. `החסר יזוכה בחשבונית.` / `החסר יישלח בסבב הבא.` / `במקום X נשלח Y.`
A tap on **רוצה לדבר** opens the 24-hour window and is logged as `wants_call`; a staff alert (§8) goes out; a human calls. **בסדר** is logged as `acked`. No further automation on either.

**Reminder emails (Tom only, for now):** Resend via `factory_os_jobs`, same transport as `missing_picks_daily_email`. Recipient env `CUSTOMER_NOTICE_REMINDER_TO`, default `tom@gteveryday.com`. Two daily ticks, Asia/Jerusalem:
- **16:30** — "N אישורי ליקוט חלקי ממתינים" + one line per order + link to the tab. Sent only if N > 0.
- **07:30 delivery day** — same, for anything still pending whose `pickup_at` is today (the 17:00 promise was missed; say so in the subject).
Both no-op when the queue is empty. One `alert_deliveries` row per cycle, marker `customer_notice_reminder`.

**Safety net:** an `ASSIGNED` task with **no** notice by 17:00 (no mapping, `/show` failing, `pickup_at` null) is listed in the 16:30 email under "לא ניתן לאשר אוטומטית" so nothing goes silent.

### Station 3 — נמסר (automatic)

**Trigger:** `lw_status` becomes `COMPLETED` (or `ROUNDTRIP_DELIVERED`) for a task that had a station-2 notice sent (or suppressed by a human — delivery still happened).

**Template `gt_order_delivered` (Utility, he, optional image header):**
```
ההזמנה נמסרה ✅ ({{1}})
החשבונית נשלחת למייל.
משהו חסר או לא תקין? השיבו כאן ונטפל.
```
`{{1}}` = delivery time "היום 11:20". Image header = `orders_mirror.lw_photo_url` when present **and fetchable** (assumption A2, §10); otherwise the text-only variant `gt_order_delivered_nophoto`.
A reply within the window is routed to a human (existing `deferred_human` path) and raises a staff alert `customer_reply_after_delivery`.
Invoice by email: Green Invoice sends the document email itself on issue (assumption A3). This station does **not** attach the invoice.

### Station 3ב — זיכוי יצא (automatic, after the bookkeeper's action)

**Trigger:** `credit_tasks.status` → `CREDITED` (existing resolution mutation on `/credit-tracking`) and `gi_document_id` set.
**Template `gt_credit_issued` (Utility, he):**
```
הזיכוי על {{1}} (הזמנה {{2}}) יצא ונשלח למייל 🙏
```
No amounts in the message (invoice carries them). `SUPPLIED` / `DEFERRED` send nothing — the "next route" promise was already made in 2ב.

### Station 8 — תזכורות תשלום (Phase 2)

Reads open Green Invoice documents per client. **Field names and the "open/paid" semantics must be inspected live before any code** (brain rule; `assumption_failure` otherwise). Rules already decided in the brainstorm (research gap J):
- `gt_payment_due_soon` 3 days before due date; `gt_payment_overdue` 7 days after; **never on Saturday or a holiday**; **max 2 automatic messages per invoice, then Doreen**; one message per customer per day even with several invoices (grouped).
- Amounts and invoice numbers appear here (this is a bill, not a catalog).
```
תזכורת ידידותית 🙂 חשבונית {{1}} על סך {{2}} ₪ לתשלום עד {{3}}.
אם כבר שולם — אפשר להתעלם. לשאלות השיבו כאן.
```
```
חשבונית {{1}} על סך {{2}} ₪ הייתה לתשלום ב-{{3}}. נשמח לעדכון על התשלום.
```

### Station 9 — מזמן לא הזמנתם (Phase 2, Marketing template)

- Only customers with ≥1 prior order and no order in the last 30 days (their own cadence when we have ≥3 orders: 1.5× their median gap, floor 14 days).
- **≤1 marketing message per customer per 30 days**, opt-out respected forever, not on Saturday. Meta's marketing cap (~2/day/user across all businesses, error 131049) is irrelevant at this rate but the sender must treat 131049 as "skip, not fail".
- Text ends with the "usual order" and the catalog link; `הסר` opts out (§7).
```
היי 🙂 כאן GT Everyday. מזמן לא הזמנתם.
ההזמנה הרגילה שלכם: {{1}}
להזמנה — שולחים עגלה מהקטלוג: {{2}}
להסרה מהודעות כאלה השיבו "הסר".
```

### Station 0 — הודעת מעבר לקטלוג (manual, no code)

One-time broadcast from the WhatsApp Business app by Avi/Tom (GT has far fewer than the 256-recipient broadcast limit; recipients must have the number saved — the ones who don't are called). Text:
```
היי, כאן GT Everyday 🙂
מהיום הזמנות נקלטות אוטומטית מהקטלוג בוואטסאפ: לוחצים על הקישור, בוחרים מוצרים וכמויות ושולחים את העגלה 🛒
https://wa.me/c/972543982444
תוך שניות תקבלו אישור שההזמנה נקלטה, יום לפני האספקה — מה יוצא אליכם, וביום האספקה — שההזמנה נמסרה.
לכל שאלה עונים כאן כרגיל. תודה 🙏
```

### Cross-cutting v1 extras (from the research)

- **"ההזמנה הרגילה שלכם" reply to free text** (gap B): instead of only a catalog link, the nudge sends a WhatsApp multi-product message (≤30 items) built from the customer's last 90 days of Shopify lines, in their order of frequency; `catalog_id` is captured from the customer's first cart webhook. Inside the 24-hour window ⇒ free. Ships once the catalog Item codes are set (operational prerequisite P1).
- **LionWheel "on the way" alerts stay native** (gap G): zero code; Tom checks the customer-notification toggle in LionWheel.

---

## §4 — Data model (`order_intake` schema; migration `NNNN_customer_notices.sql`, slot bracketed per FR1/FR2)

```sql
create table order_intake.customer_notices (
  notice_id        uuid primary key default gen_random_uuid(),
  kind             text not null check (kind in (
                     'confirmed_full','confirmed_partial','delivered','credit_issued',
                     'payment_due_soon','payment_overdue','reorder_nudge')),
  state            text not null default 'draft' check (state in (
                     'draft','pending_approval','approved','sent','delivered','read',
                     'failed','suppressed','expired','shadow')),
  wa_phone         text not null,                      -- E.164 digits, FK-by-convention to wa_customer_map
  shopify_customer_id text,
  shopify_order_name  text,                            -- '#1777'
  mirror_id        uuid references private_core.orders_mirror(mirror_id),
  lw_task_id       text,
  credit_task_id   uuid references private_core.credit_tasks(credit_task_id),
  dedupe_key       text not null unique,               -- e.g. 'confirmed:<mirror_id>' / 'delivered:<mirror_id>' / 'credit:<credit_task_id>' / 'nudge:<phone>:<yyyy-mm>'
  template_name    text,
  template_params  jsonb not null default '{}'::jsonb, -- rendered variables, for audit + resend
  send_not_before  timestamptz,                        -- quiet-hours gate
  approved_by      uuid, approved_at timestamptz, suppress_reason text,
  wa_message_id    text, sent_at timestamptz, delivered_at timestamptz, read_at timestamptz,
  fail_code        text, fail_detail text, attempts int not null default 0,
  created_at       timestamptz not null default now(), updated_at timestamptz not null default now()
);
create table order_intake.customer_notice_lines (
  notice_id        uuid not null references order_intake.customer_notices(notice_id) on delete cascade,
  line_mirror_id   uuid references private_core.orders_mirror_lines(line_mirror_id),
  item_id          text, item_label text not null,
  qty_ordered      numeric(24,8) not null,
  qty_delivering   numeric(24,8) not null,              -- human-entered on partial; = ordered on full
  resolution       text check (resolution in ('credit','next_route','substitute')),
  substitute_label text,
  primary key (notice_id, item_label)
);
alter table order_intake.wa_customer_map
  add column notices_enabled      boolean not null default true,   -- staff kill switch per customer (utility)
  add column notices_opt_in_at    timestamptz,                     -- first cart or explicit yes
  add column marketing_opt_out_at timestamptz;                     -- 'הסר'
```
Plus `order_intake.customer_notice_events` (append-only: state transitions with actor + WhatsApp status webhooks `sent/delivered/read/failed`) and a view `order_intake.v_customer_notice_stats` (§9). pgTAP test in `db/tests/` of the same slot.

**Customer ↔ order join:** `orders_mirror.wp_order_id` = Shopify order name → Shopify order → `customer.id` → `wa_customer_map.shopify_customer_id` → `wa_phone`. The bot already fills this map by phone on first contact (self-map) so every catalog customer is reachable. LionWheel `destination_phone` is deliberately **not** used (PII not mirrored, Tom ratification) — and it is the delivery contact, not the orderer.

---

## §5 — Triggers and jobs

One new job in the existing Node API, `customer_notices_tick`, invoked by pg_cron every 5 minutes via `factory_os_jobs` (same wiring as `lionwheel_poll`). Each tick, in order:

1. **Detect** — mirror rows in `ASSIGNED` without a `confirmed:*` notice → fetch `/tasks/show/<id>` (`pick_status`) → create `confirmed_full` (state `approved`, `send_not_before` per quiet hours) or `confirmed_partial` (state `pending_approval`). Mirror rows newly `COMPLETED` with a `confirmed:*` notice → create `delivered`. `credit_tasks` newly `CREDITED` with `gi_document_id` → create `credit_issued`.
2. **Send** — every `approved` notice with `send_not_before <= now()` → WhatsApp template send (`whatsapp/send.ts` gains `sendTemplate(to, name, lang, components)`) → `sent` + `wa_message_id`, or `failed` + code. Retry 3× with backoff on 5xx/429; `131049` and `131026` (not a WhatsApp user) → `failed`, no retry, staff alert.
3. **Expire** — `pending_approval` older than the delivery's `pickup_at` + 12h → `expired` (a "what's coming" message after delivery is noise). Listed in the next reminder email as missed.
4. **Reminder emails** at 16:30 and 07:30 (§3, 2ב); gated on Israel local time like `missing_picks_daily_email`.

**Feature flags** (`private_core.feature_flags`, same shape as the Shopify reconciler: `enabled` + `value.allowlist`):
- `customer_notices_live` — master. `enabled=false` ⇒ tick creates rows in state `shadow`, sends nothing. `enabled=true` + `allowlist=['9725…']` ⇒ sends only to listed phones. `'*'` ⇒ all.
- `customer_notices_kinds` — `value.kinds` list; a kind not listed stays `shadow`.
Env `WHATSAPP_NOTICES_ENABLED` (default `false`) is the hard off-switch in front of both flags.

**Status webhooks:** the existing `/webhooks/wa-order-bot` already receives `statuses[]`; map `sent/delivered/read/failed` by `wa_message_id` onto the notice row. `failed` with error → staff alert.

---

## §6 — Rules

- **Quiet hours:** proactive sends only 07:00–21:00 Asia/Jerusalem; earlier/later ⇒ `send_not_before` = next 07:00. Never on Saturday or Israeli holidays for stations 8 and 9 (`private_core` already carries the working calendar for planning; reuse it — verify the table name in the plan, do not assume).
- **One promise per order:** exactly one `confirmed:*` and one `delivered:*` notice per mirror row (unique dedupe key). A pickup_at change **after** a confirmed send, or a `CANCELLED` status after one, creates a staff item (§8), never an automatic correction message in v1.
- **Never a price** in stations 1–3ב. Amounts only in station 8.
- **Language:** Hebrew only.
- **Idempotent ticks:** every step keyed on dedupe_key or on `state` transitions; a tick can be re-run at any time.
- **Templates are versioned:** `template_name` includes a suffix (`_v1`); a wording change is a new template, old rows keep their name.

---

## §7 — Consent and opt-out

- Sending a cart = existing business relationship; `notices_opt_in_at` is stamped on first cart (or by staff import for the announcement cohort). Utility messages (stations 2, 3, 3ב, 8) ride on that.
- Station 9 (marketing) additionally requires `marketing_opt_out_at is null`.
- Inbound `הסר` / `הסירו` / `stop` from a mapped phone: worker sets `marketing_opt_out_at`, replies once (inside the window) `הוסרתם מהודעות שיווקיות 👍 עדכונים על ההזמנות שלכם ימשיכו להגיע.`, logs `marketing_opt_out`. Utility notices continue; a customer who wants total silence is handled by staff via `notices_enabled=false`.

---

## §8 — Staff side

- **Staff alerts** (`alert.ts`, today pointing at an empty `ORDER_INTAKE_ALERT_WEBHOOK_URL`): switch to the proven Resend email path, recipients env `ORDER_INTAKE_ALERT_TO`, default `tom@gteveryday.com`. Kinds added: `wants_call`, `customer_reply_after_delivery`, `notice_send_failed`, `confirmed_then_changed`, `commit_failed` (existing).
- **Avi/Doreen day, unchanged in shape:** 14:00 intake close (drafts already in Shopify) → 15:00 LionWheel lock → picking → 16:30 email if anything is short → approve on the tab before 17:00 → deliveries → credits on `/credit-tracking` as today.
- **What they stop doing:** typing "קיבלנו", answering "מתי מגיע?", answering "הגיע?"; and — once station 8 ships — the first two payment nudges.

---

## §9 — Metrics (view `order_intake.v_customer_notice_stats`, weekly line in the sales report)

- notices per kind per state · % confirmed automatically vs approved vs suppressed vs expired
- median minutes ASSIGNED → sent (full) · median minutes pending → approved (partial)
- % delivered notices followed by a customer reply within 24h (the "something wrong" rate)
- template failures per code · marketing opt-outs
- Health: `GET /webhooks/wa-order-bot/health` gains `notices: { enabled, pending_approval, failed_24h, oldest_pending_minutes }`.

---

## §10 — Assumptions to verify before build (halt on failure, brain rule)

| # | Assumption | How verified | Owner |
|---|---|---|---|
| A1 | `pick_status = 'PICKED'` is already set when the task is `ASSIGNED` the day before (picking precedes or accompanies driver assignment) | Shadow week: log (`lw_status`, `pick_status`, `pickup_at`, poll time) per task; count how many reach PICKED before 17:00 day-before | tick, shadow mode |
| A2 | `lw_photo_url` is fetchable by Meta for an image header (public or signed URL) | one manual template send with a real URL to Tom's phone | integration lane |
| A3 | Green Invoice emails the invoice to the client on issue (so station 3 may say "נשלחת למייל") | Tom confirms or GI settings inspected | Tom |
| A4 | Dualhook lets us **create and submit templates** for WABA `159609277238189` (Meta WhatsApp Manager access) — otherwise Tom/Cowork submits the six texts above by hand | try in WhatsApp Manager | Tom/Cowork |
| A5 | Template approval turnaround (Meta usually minutes–hours for Utility; Marketing can take longer) | submit early, in parallel with the build | Tom/Cowork |
| A6 | The working-day / holiday calendar table exists in `private_core` and is maintained | inspect before the plan | backend-db |
| A7 | Every catalog-ordering customer is in `wa_customer_map` with a `shopify_customer_id` (self-map succeeds) | query the map vs last 60 days of Shopify orders | backend-db |

---

## §11 — Out of scope (explicitly)

- Writing shortage data from 2ב into `credit_tasks` / `FG_OUT_PICK` (stock truth; separate Tom decision — the day-before review is the best shortage data we have and this is worth deciding soon).
- LionWheel webhooks (latency only; add later, org settings API tab).
- Standing orders, cut-off reminders, substitution buttons for the customer, monthly statement (research gaps C, D, F, I — v2).
- Catalog synced from Shopify (research §3 option 1). Tom's standing decision is a manual catalog with no prices; revisit if item-code upkeep hurts.
- Any AI-generated text to customers. All copy is fixed and versioned here.
- Auto-commit of drafts (`WHATSAPP_AUTO_COMMIT_ENABLED` stays Tom's call).

---

## §12 — Rollout

| Phase | Ships | Gate to next |
|---|---|---|
| **P0 prerequisites** | catalog Item codes = SKU (57 items, list sent 2026-09-08), prices removed, station-0 broadcast, six templates submitted | codes verified by one real cart per product family; templates approved |
| **P1 shadow** | schema, tick, detection, portal tab (approval works but sends are `shadow`), reminder emails to Tom, staff alerts by email | ≥1 week, A1 measured, A7 clean, `rebuild_verifier()=0` untouched (no ledger change, but stated) |
| **P2 live, allowlist** | `customer_notices_live` enabled for Tom's phone + 2–3 friendly customers; kinds `confirmed_full`, `confirmed_partial`, `delivered` | 1 week, zero wrong-content incidents, approval latency < 60 min median |
| **P3 all customers** | allowlist `*`; `credit_issued`; "usual order" reply | — |
| **P4** | station 8 (after GI inspection), station 9 (marketing rules) | Tom go per station |

Each phase = one PR set in `gt-factory-os` (+ one portal tranche for the tab), tests N/N reported, health endpoint checked after deploy. Sends to real customers begin only at P2 and only per Tom's go (customer-facing writes rule).

---

## §13 — What Tom is asked to approve here

1. The three-promise framing and the station set above (1, 2א, 2ב, 3, 3ב, 8, 9, 0 manual).
2. Hebrew copy of the six templates + the new receipt wording (edits welcome, then locked as `_v1`).
3. The data model in §4 and the flag/shadow rollout in §5/§12.
4. That day-before shortage data does **not** feed stock truth in this spec (§11 first bullet stays open as its own decision).

References: research memo (same folder) · gt-factory-os#272 · `api/src/order-intake/README.md` · `api/src/integrations/lionwheel/reconciliation.ts` · migrations 0089, 0240, 0241, 0265 · portal `/credit-tracking` (Hebrew RTL, authorized 2026-06-17) · Meta template rules (research §5) · `github.com/lionwheel/api`.
