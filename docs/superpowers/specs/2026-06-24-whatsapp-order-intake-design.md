# WhatsApp B2B Order-Intake Agent — Design

**Date:** 2026-06-24
**Owner:** Tom
**Status:** Design approved (brainstorm). Pending: spec review → implementation plan.
**Module:** `order-intake` (NEW customer-facing module — blocked on `MODULE_TEMPLATE.md` + Tom written approval before build).

---

## 1. Purpose

Let GT's B2B customers (cafes/bakeries) place orders by **texting WhatsApp in natural Hebrew**, exactly
the way Doreen relays them today. An AI agent recognises the message as an order, identifies the
customer, builds a priced cart in the chat, lets the customer approve it, and turns it into a Shopify
order — auto when confident, with a human checkpoint when not.

It is the always-on, customer-facing version of the `shopify-draft-order-from-po` skill proven on
2026-06-23 (9 real orders entered correctly). The reasoning layer already exists; this project makes
it a service and adds the WhatsApp transport, cart UX, and commit/payment paths.

**Success:** a customer texts "12 צ'אי ליטר, 6 היביסקוס" → gets a correct Hebrew cart → taps ✅ →
a correct Shopify order exists, priced at their last-paid, with the same accuracy a careful human
achieves today, and **zero wrong-branch / wrong-price / wrong-product orders auto-shipped**.

## 2. Locked decisions (from brainstorm)

| Decision | Choice |
|---|---|
| WhatsApp channel | **Coexistence** — connect the existing number to the **Cloud API alongside** the WhatsApp Business app (NOT a migration). The app keeps working; the bot runs in parallel on the same number. **Hard constraint (Tom 2026-06-25): the number must never be disconnected, not for a second** — migration/mode-A is permanently off the table |
| Customers | **B2B known accounts only.** Cafes text for themselves. Identity = the **saved WhatsApp contact** (incoming number → `wa_customer_map`, seeded from GT's saved WhatsApp contacts × Shopify). Unrecognised number → hold + alert **Doreen** to map → resume |
| Branch model | **One number = one branch** (confirmed — no shared chain numbers). No branch-selection step |
| Commit model | **Hybrid by confidence:** clean → auto-commit; any flag → human checkpoint |
| Human checkpoint surface | **Shopify itself** (flagged order = Shopify draft tagged `needs-review`); **no Telegram** |
| Payment | **Per-customer flag:** `terms` (Green Invoice on terms) or `pay_now` (GI payment link in chat) |
| Front gate | Bot acts **only** for a known, opted-in number **and** an order-intent message |
| Reasoning runtime | **Anthropic API server-side** (NOT Claude Code/MCP — `CLAUDE.md` forbids MCP in the live path) |
| Engine | Port `lookup.mjs` / `create_draft.mjs` logic to a shared TS module used by bot + skill |
| Architecture | A — Cloud API webhook → Supabase Edge receiver → factory-os intake worker |

## 3. Architecture & components

1. **WhatsApp Cloud API (Meta)** — transport. Inbound webhook; outbound via Graph API.
2. **Webhook receiver** — Supabase Edge Function. Verifies Meta signature, ACKs <5s, writes raw event
   to `wa_event_log`. No business logic.
3. **Intake worker** — new `order-intake` module in the gt-factory-os Fastify API. Consumes events,
   runs the pipeline, reuses existing Shopify / Green Invoice clients.
4. **Reasoning** — Anthropic API for (a) order-intent classification, (b) free-text → line-item parse
   and edit-delta interpretation. Deterministic resolve/price/VAT-guard ported from the skill.
5. **State** — isolated `order_intake` Postgres schema (must not touch factory-os core schema).

External systems: WhatsApp (r/w), Shopify (draft/order — built), Green Invoice (invoice/pay link —
client exists), no Telegram.

Receiver/worker split: the webhook must answer Meta instantly and survive restarts; the worker takes
its time, retries, reuses integration clients. Decoupled by the queue table.

## 4. Pipeline (message → committed order)

```
[1] Edge receiver: verify signature → wa_event_log → ACK Meta (<5s)
[2] Worker consumes event
[3] FRONT GATE
    a. Known customer?  wa_phone → wa_customer_map → Shopify customer + branch (+ bot_enabled)
       unmapped / not enabled → do nothing (optional one-time enroll ping to Tom)
    b. Order intent?    Claude: ORDER / NOT_ORDER / AMBIGUOUS
       not order → silent / route to human;  ambiguous → one clarifier
[4] PARSE (ported engine)
    Claude: Hebrew free-text → line items (qty, phrasing, size)
    deterministic: phrasing → barcode/SKU → ACTIVE Shopify variant
    price each line by THIS customer's last-paid (catalog fallback)
    VAT guard + collect FLAGS
[5] CART REPLY: interactive WhatsApp msg (Hebrew names) + [אישור][עריכה][ביטול]
    edit → free-text delta → re-parse → re-show (loop);  cancel → close
[6] CONFIDENCE GATE on אישור
    no flags  → auto-commit
    has flags → Shopify DRAFT tagged needs-review, flags in note; customer told "נחזור אליך"
[7] COMMIT
    create Shopify order; payment branch by customer flag (terms | pay_now)
[8] CONFIRM to customer (order # + summary, + pay link if pay_now). All logged.
```

The left spine [3]→[4]→[6] is the 2026-06-23 session encoded: gate → resolve/price/guard → flags
decide auto-vs-human.

## 5. Front gate (the explicit requirement)

**A. Known customer? (deterministic)** — sender E.164 → `wa_customer_map` → exact Shopify customer +
branch + flags. The map mirrors GT's **saved WhatsApp contacts** (GT already keeps every customer saved
as number→name) cross-referenced to Shopify customers. No fuzzy match. **One number = one branch**
(confirmed — solves the multi-branch trap directly). `bot_enabled` per customer → only opted-in
customers get replies (staged rollout).

**Unrecognised number → the bot does NOT process the order.** It **holds the session** and alerts
**Doreen** (the enrollment human): "מספר לא מזוהה ביקש להזמין — למפות?". Doreen maps the number → Shopify
customer; the **held session then resumes automatically** from where it paused. Never an auto-order for
an unmapped number. (This is the explicit requirement: identify the customer via the chat, else stop
and let Doreen map.)

**B. Order intent? (Claude)** — ORDER (product names + quantities) → parse. NOT_ORDER (logistics,
thanks, complaint) → silent / human inbox. AMBIGUOUS → one clarifier or human. Never guesses.

**Burst aggregation:** orders arrive in fragments. Session buffers for a ~10–15s quiet window (or an
explicit "סיימתי"/אישור) before parsing the whole thing — one cart per order, not per message.

**C. Coexistence — defer to humans (NEW, from the Coexistence decision).** The bot shares the number
with Doreen/staff who still use the WhatsApp Business app. Coexistence mirrors **both** sides to the
webhook: customer messages arrive normally, and **anything a human sends from the app arrives as an
`smb_message_echoes` event**. The bot uses this to stay out of a human's way:
- If a staff member has already replied to this customer from the app (an `smb_message_echoes` seen in
  the session window), the bot treats the conversation as **human-handled** and does **not** send a
  cart — no double-replies.
- A human can take over mid-flow at any time; their first app-message closes the bot's session for that
  chat. The bot is always the *fallback*, never competing with a person.
- Throughput on a coexistence number is capped by Meta at **5 messages/second** — irrelevant at GT's
  volume, noted so we never design around higher.
- Onboarding caveat: existing 1:1 chats stay in the app; only messages from Coexistence-enablement
  onward are mirrored. The bot only ever acts on messages it actually receives.

## 6. Confidence gate + human handoff (via Shopify)

**Flags (each is a real 2026-06-23 miss):** no last-paid → catalog fallback; last-paid ≠ catalog;
product not in active catalog; barcode → multiple active variants; size missing + no habit; archived/
discontinued SKU; qty anomaly; zero-price line; low-confidence parse.

**Hard stops** (never auto-commit, even when thresholds later loosen): VAT-guard fail, unknown product,
archived SKU.

**Outcomes:** zero flags → committed Shopify order. Any flag → **Shopify draft** tagged `needs-review`
with flags in the note (exactly today's draft-with-notes pattern). Tom opens it in the Shopify admin
(web/mobile he already uses), fixes the one thing, hits Send/Complete — that tap is the approval.

**Loop closes via Shopify webhook** (`draft_order` completed / `orders/create`): on completion the bot
sends the customer their confirmation (+ pay link if pay_now). Review queue = a pinned Shopify admin
filter "drafts tagged `needs-review`"; Shopify mobile push covers notification. Optional single
WhatsApp nudge to Tom with a deep link. **No Telegram.**

**Trust dial:** thresholds are config. Start strict; loosen low-risk flags for trusted customers over
time; the three hard stops stay human forever.

## 7. Cart & conversation UX + session state

Cart = one interactive WhatsApp message, **Hebrew product names** (from the lexicon `he`/aliases, not
the English Shopify titles), itemised `qty × name @ price = subtotal`, total marked "כולל מע"מ", with
`[אישור ✅] [עריכה ✏️] [ביטול ❌]`. Long carts (18-line Babka) exceed the button-body limit → send the
list as text, then a short button message.

Edit loop is free-text: "תוסיף 6 היביסקוס" / "תוריד מאצה" / "תשנה צ'אי ל-12" → Claude reads it as a
delta against the current cart → re-price → re-show.

`wa_session` states: `COLLECTING → CART_SHOWN → PENDING_REVIEW → COMMITTED → CLOSED`. One open session
per customer. Abandoned CART_SHOWN → one reminder then CLOSED. After COMMITTED a new message = a new
order (fresh session). Idempotency on `wa_message_id`.

## 8. Payment branch

`payment_mode ∈ {terms, pay_now}` per customer, applied after commit.
- **terms** (established B2B default): Shopify order → Green Invoice invoice on terms → existing AR.
  Confirmation: "ההזמנה נקלטה ✅ #1234. חשבונית תישלח כרגיל."
- **pay_now** (new/cash): Shopify order (pending-payment) → Green Invoice payment-request link (אשראי/
  bit) in WhatsApp → GI payment webhook → mark paid, release, "התקבל תשלום ✅". Unpaid after X →
  reminder then hold.

GI for the link (not Shopify checkout) keeps one financial source of truth. New accounts default
`pay_now`, established `terms`.

## 9. Data model (`order_intake` schema)

**wa_customer_map** — `wa_phone` (E.164 UNIQUE) · `shopify_customer_id` · `display_name` · `branch` ·
`payment_mode` · `bot_enabled` · `default_pack` · `notes` · timestamps. One row per branch number.

**wa_session** — `customer_map_id` · `state` · `cart_json` `[{phrasing, variant_id, sku, qty,
unit_price, flags}]` · `collecting_until` · `shopify_draft_id`/`shopify_order_id` · `flags_json` ·
`expires_at` · timestamps.

**wa_event_log** — `wa_message_id` (UNIQUE → idempotency) · `direction` · `wa_phone` · `session_id` ·
`type` · `raw_payload` jsonb · `processed_at` · `status`. Shopify/GI webhook events logged + deduped
here too.

**Catalog**: read live from Shopify (no copy). **Lexicon** (phrasing→variant): single versioned repo
config shared by bot + skill (optional config table later).

**Seeding:** (1) bootstrap by importing **GT's saved WhatsApp contacts** (number→name) and matching
them to Shopify customers (`bot_enabled=false`); (2) any unrecognised number at order time → hold +
**Doreen maps it**, held session resumes; (3) flip `bot_enabled` per cafe to roll out.

## 10. Error handling & invariants

Meta retries → idempotent on `wa_message_id`. WhatsApp send fail → retry/outbox → escalate, never drop.
Claude parse fail/low confidence → route to draft, never auto-commit. Shopify commit fail → retry with
idempotency key (one order per session), keep pending, don't tell customer "done". GI fail → order
stands, invoice retried + alerted. Double ✅ / re-sent order → session idempotency + today's duplicate
scan. Out-of-order webhooks → state-machine guards.

**Five hard invariants (code, not config):** (1) never auto-commit with any flag; (2) never
double-create an order; (3) never message an unmapped/disabled number; (4) never say "confirmed"
before Shopify confirms; (5) every inbound + outbound + commit is logged.

## 11. Testing

1. **Unit** — ported resolve/price/guard; **replay 2026-06-23's 9 real orders** as fixtures, assert
   exact carts/totals/flags (incl. Jasmin collision, Maruei→Shizuoka, ₪0 cup, Babka 490-vs-600).
2. **Parse/intent eval set** — labeled real Hebrew messages → expected line items + intent; track
   precision/recall; regression-gated; traps included (bursts, sizeless, sugar-free, non-orders).
3. **Integration (sandbox)** — receiver + worker vs Shopify dev store + GI sandbox, fed recorded Meta
   webhook payloads.
4. **Contract** — VAT guard, Meta signature verify, idempotency.
5. **E2E** — real test WhatsApp number, full loop incl. a flagged order → draft → complete → confirm.

**Evidence gate (per `CLAUDE.md`):** N/N tests green, replay parity, guard PASS — RUNTIME_READY-style
signal before live.

## 12. Roadmap, gates & rollout

**Finish design:** write this spec → Tom review → writing-plans.

**Gates before build:** G1 module approval (`MODULE_TEMPLATE.md` filled + Tom written OK). G2 Tom
enables **Coexistence** for the number (Cloud API alongside the Business app — never a disconnect;
the app-side link is a QR Tom scans in the WhatsApp Business app; ~1–2 days incl. business
verification; Tom-only). Mode-A migration is forbidden (hard constraint).

**Staged build (Claude writes code/tests):**
| Phase | What | External dep |
|---|---|---|
| 0 | Module scaffold, `order_intake` schema, secrets wiring | secrets |
| 1 | Port engine + replay today's 9 orders (offline) | none |
| 2 | Shopify draft/order + GI commit + webhooks (dev store) | none |
| 3 | WhatsApp receiver + send + cart UX (test number) | Meta migration |
| 4 | Front gate + intent + sessions; E2E | test number |
| 5 | Soak: one pilot cafe, **drafts-only** (Phase-1 trust) | pilot pick |
| 6 | Auto-commit clean orders; widen customers | go-live OK |

**Trust phasing:** Phase 1 = bot drafts everything, Tom reviews all (= today). Phase 2 = auto-commit
clean orders once accuracy proven. Hard stops never auto.

Tom acts at: MODULE_TEMPLATE approval · Meta migration · secrets · pilot pick · go-live per step.
Phases 0–2 are offline and reuse today's work — buildable while Meta verification runs.

## 13. Open questions

**Resolved (Tom, 2026-06-24):**
- ~~Q1 Doreen relay vs self-order~~ → **Cafes text for themselves**; identity via the saved WhatsApp
  contact (number → customer). Unrecognised number → hold + **Doreen maps** → resume.
- ~~Q2 One number, many branches~~ → **No** — one number per branch. No branch-selection step.
- ~~Q4 New-number verification~~ → **Doreen** maps/verifies the held session; no code flow.

**Resolved (Tom, 2026-06-24 round 2):**
- ~~Q5 Delivery date~~ → **No** — cart does not ask; delivery/routing handled downstream (LionWheel) as today.
- ~~Q6 Bot hours~~ → **24/7**; orders placed after hours are tagged for the next working day. Customer never hits a wall.
- Q3 Green Invoice payment links → Tom: **verify via the GI API directly** (read-only capability probe, no real document). Finding recorded below.

**Q3 finding (GI payment-link capability), 2026-06-24:**
- **API capability: YES.** Morning/Green Invoice advertises "סליקה ותשלומים דיגיטליים — אשראי, ביט
  וארנקים דיגיטליים" and its API exposes a payment-request / payment-form endpoint that returns a
  payable URL — exactly what `pay_now` needs.
- **Account dependency:** it works **only if a clearing provider (סליקה) is connected** to GT's Morning
  account. Could not confirm that live here — a direct probe needs the account secret (correctly blocked
  by the secrets guard) and the apidocs host refused. **Tom to confirm in Morning → settings → סליקה.**
- **Repo gap:** today's `greeninvoice/client.ts` only creates type-305 invoices (no payment link wired).
  The client must be **extended** with a `createPaymentLink` method for `pay_now` (Phase 2 work).
- **Fallback stands:** if clearing isn't enabled, `pay_now` uses Shopify's `invoiceUrl` checkout; `terms`
  customers are unaffected (invoice-only, already wired).
```
