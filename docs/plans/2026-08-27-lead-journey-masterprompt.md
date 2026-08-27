# MASTERPROMPT — a campaign-matched WhatsApp reply reaches every new lead, and a human closes it

**STATUS: LIVE — not yet executed**

> **Usage:** paste this entire file as the first message of a fresh session with
> `gt-factory-os`, `gt-factory-os-production-brain`, `gt-factory-os-portal` and
> `Sales-Machine` attached. It takes GT's inbound-lead motion from "leads arrive and
> nobody answers" to "every lead gets the right catalog within seconds, and a person
> continues the conversation." It halts for Tom only where a human must genuinely act —
> §6 is that complete list.
>
> **Provenance:** written 2026-08-27, from live measurement of Supabase project
> `rvadsozabmxkkrktwgnv` (`sales_core.*`, `order_intake.*`), the deployed Edge Function
> list, and Tom's answers in the scoping session of the same day. Authority:
> `gt-factory-os-production-brain/CLAUDE.md` → `Sales-Machine/CLAUDE.md` →
> `gt-factory-os/CLAUDE.md` → `docs/decisions/modules/sales-declaration.md` — cited
> below, never copied.
>
> **Shelf life:** §2 is presumed wrong if pasted after 2026-09-10. Re-run §2.5 first.
> If the numbers have moved materially — leads worked, the bot silenced, the VAT config
> fixed — **adapt and say what changed**; do not halt. If a *decision* in §1.1 appears
> to have been reversed, **halt and ask Tom**; those are his, not yours.

---

## 0. How to work

- **Who you are here:** one agent session, chained across days. You hold the four repos
  above, Supabase MCP against `rvadsozabmxkkrktwgnv`, Shopify MCP, GitHub MCP, and Make
  MCP. You do **not** hold Meta Business Manager access, Green Invoice credentials, or
  the ability to flip a frozen flag. You may decide implementation shape, file layout,
  schema design and task order alone. You may not decide anything in §1.1 or §6.
- **Read first, in order:** `gt-factory-os-production-brain/CLAUDE.md` ·
  `Sales-Machine/CLAUDE.md` · `Sales-Machine/CURRENT_STATE.md` ·
  `Sales-Machine/doctrine/decisions.md` ·
  `gt-factory-os-production-brain/docs/decisions/modules/sales-declaration.md` §11 ·
  `gt-factory-os/CLAUDE.md` §Shopify writes.
- **Authority:** cited by path and section, never restated. Where this document and an
  authority doc disagree, **the authority doc wins and this document is wrong.**
- **Halt conditions, evidence standard, git discipline:** inherited from
  `gt-factory-os-production-brain/CLAUDE.md` §Stop conditions and §Evidence. Deltas for
  this work only are in §8.
- **The standard, in Tom's words** (2026-08-27):
  `אני לא רוצה שAI ידבר יותר עם לקוחות - זה פוגע בשירות שלנו.`
  Translated into checkable prohibitions:
  1. **No generated text ever reaches a customer.** Every outbound character is drawn
     from a stored, Tom-approved string. No model call sits on any outbound path.
  2. **No message is sent without a matching routing row.** No default, no fallback
     text, no "close enough" campaign match.
  3. **Nothing is sent twice** for the same lead and campaign, under any retry.
- **Language:** this document is English because that is the register you reason best
  in. Data literals stay in their own script, in backticks, and are never translated —
  `MACHA Leads`, `Matcha Tut`, `קטלוג וניצור קשר בהקדם` are keys and copy, not prose.
  **Output language: concise Hebrew when replying to Tom** (he works in Hebrew), English
  in code, commits and PRs. Short sentences. No preamble, no restating the question.

---

## 1. Mission and definition of done

**One testable sentence:** every new lead receives, within seconds and without a human,
the catalog that matches the campaign they came from — and lands in the sales queue with
that context attached.

| # | Condition | The observation that would prove it false |
|---|---|---|
| D1 | A routing table exists that Tom can edit without a deploy | `select count(*) from sales_core.campaign_playbook where active;` returns ≥1, and a new row added by SQL alone changes what the next lead receives — verified by a dry-run, not by reading code |
| D2 | Routing resolves most-specific-first and never guesses | Unit tests prove: (campaign+ad) beats (campaign); no row → `null` and a flagged event. A test that feeds `CHAI Leads` with no row and asserts "nothing sent" must pass |
| D3 | The dry-run reports what *would* go out, and sends nothing | Run against every live row returned by the campaign query in §2.5 (6 at baseline; the count moves); output names each lead id and the catalog it would receive; `order_intake.wa_event_log` and any send log gain **zero** outbound rows. Confirm by row count before and after |
| D4 | Every send attempt is logged and replayable | For any lead id, one query returns: which playbook row matched, what was sent, when, and the transport's response id |
| D5 | The lead card shows campaign context before the call | `/sales/today` renders campaign name, ad name, and what was auto-sent, on a lead that has them. Observed in the browser, not asserted in a test |
| D6 | Nothing customer-facing is live | `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` is still `false` at hand-off, and `grep` proves no code path sends without reading it |

Anything not on this list is out of scope unless Tom asks.

### 1.1 Settled — do not reopen

Decided by Tom in writing, 2026-08-27, during the scoping session:

1. **No AI converses with customers.** The automation sends fixed, pre-approved text.
   Conversation is human. This is the reason the WhatsApp order bot is being retired
   from the outbound path.
2. **The lead leaves details on a form, then receives an automatic WhatsApp message,
   and a human continues from there.** Tom's words:
   `הליד גם משאיר פרטים ואז מקבל הודעה אוטומטית בווצאפ וממשיכים משם.`
   The form is **not** being replaced by a click-to-WhatsApp ad. That option was put to him with its cost advantages and he
   chose this. **Do not re-argue it.**
3. **Message content:** the campaign's catalog, plus that we will be in touch shortly.
   Tom's words: `קטלוג וניצור קשר בהקדם`. **No qualifying question. No product picker.
   No price negotiation. No selection mechanism.** The automation warms; the human sells
   the whole range in conversation.
4. **Payment link comes from Green Invoice**, not Shopify.
5. **Every customer is a business.** Minimum order `₪800 + מע"מ`. Prices are always
   presented ex-VAT because the audience is businesses. There is no retail motion.
6. **A win is a new customer who chose and paid through a payment link within 24 hours
   of leaving their details.** Tom stated the 24-hour figure verbatim on 2026-08-27.
   Existing customers who buy are revenue, not wins.
7. **Nobody is dropped.** That same 24-hour figure is the KPI, not a routing rule.
   Every lead goes to the human queue regardless of what the automation did.

---

## 2. Ground truth — measured 2026-08-27; re-verify at boot

### 2.1 What is built and live

- **Lead intake works.** Make carries Facebook leads to `/ingest`; `sales-leads-poll`
  (Edge Function, ACTIVE) writes them. Campaign attribution arrives intact.
- **The sales workspace exists** — `/sales/today`, `/sales/leads`, `/sales/orgs`,
  `/sales/settings` in `gt-factory-os-portal`, Hebrew/RTL, phone-first.
- **A WhatsApp Business number is connected and reading**, via Dualhook coexistence. It
  has been ingesting for months.
- **A Green Invoice client exists** at
  `gt-factory-os/api/src/integrations/greeninvoice/client.ts` — three methods only:
  `searchByRemarks`, `getDocument`, `createDocument`, hitting `documents/search`,
  `documents/{id}`, `documents`.

### 2.2 The numbers

```
sales_core.lead        195 total · 190 still 'new' · 26 in last 30d
                       3 'won' · 1 'working' · 1 'lost'
                       39 with neither phone nor email — unreachable, no exit path
campaign attribution   6 leads carry campaign_name — all 'MACHA Leads'
                       ad_name splits them: 'Matcha Tut' (5) · 'Matcha Mango' (1)
                       arrived 24–26 Aug · all have a phone · all still 'new'
                       the other 189 are the historical import (form '0205.2025-2question-new')
the 3 'won'            ₪481 · ₪740 · ₪1554 (avg ₪925)
                       ALL carry event 'matched_existing_customer'
                       2 of 3 have NO human touch event at all
human activity 17–27.8 11 'outreach' · 1 'outcome' · 1 'next_touch_set' — all actor 'Tom'
sales_core.org         193 rows · 13 matched to Shopify · 0 with city
order_intake           186 customers mapped · 22,934 events · 759 sessions
                       last event 2026-08-27 07:45Z — still ingesting
last 30d               336 sessions · 336 human_handled (100%) · 0 drafts · 0 orders
                       median 71s to human takeover · 142 of 336 taken over under 5s
last bot-built draft   2026-07-12. Nine, ever.
```

### 2.3 What is NOT built

- No routing table. No sender. No outbound path of any kind for leads.
- No campaign context on the lead card.
- The matcha catalog is **not registered** in
  `gt-factory-os-production-brain/docs/warehouses/marketing-assets.md`. Tom says he has
  the file; it is not in the repo and has no stable address. See §6.A.
- No Green Invoice customer-payment-demand path. The existing client is used only for
  **supplier** invoices (`credit_draft_creator.ts`) — the opposite direction.

### 2.4 Known-broken, adjacent, out of scope

- **Shopify tax config is wrong on two counts.** Header of
  `gt-factory-os-production-brain/docs/pricing/2026-08-05_shopify_products_exvat.tsv`:
  `Shopify is currently configured taxesIncluded=true at 17% — WRONG on both counts.`
  Prices in that file are ex-VAT. This pre-dates you. It does not block §4 (the payment
  link is Green Invoice, not Shopify) but any figure you display must be checked against
  §6.B before a customer sees it.
- **The morning follow-up reminder is not deployed**, blocked on a missing repo secret
  `SUPABASE_ACCESS_TOKEN`. Pre-existing. Not yours.
- **The demo account appears in the sales-rep list** because it is an active admin.
  Pre-existing. Not yours.

### 2.5 Re-verification block

```sql
-- Regenerates every number in §2.2. Run at boot. Measured baseline: 2026-08-27.
select count(*) total,
       count(*) filter (where status='new')       still_new,
       count(*) filter (where status='won')       won,
       count(*) filter (where created_at > now()-interval '30 days') last_30d,
       count(*) filter (where phone_e164 is null and email is null)  unreachable
from sales_core.lead;

select campaign_name, ad_name, count(*), max(created_at)::date
from sales_core.lead where source='facebook' group by 1,2 order by 3 desc;

select count(*) sessions_30d,
       count(*) filter (where human_handled) human_handled,
       count(shopify_draft_id) drafts, count(shopify_order_id) orders
from order_intake.wa_session where created_at > now()-interval '30 days';

select max(created_at) last_wa_event from order_intake.wa_event_log;
```

---

## 3. What the hard part actually is

**Both pipes are live. Neither has ever delivered its purpose.** Lead intake has carried
195 records and produced zero new customers by Tom's definition — the three wins are
existing customers, two of whom bought without anyone contacting them. The WhatsApp bot
has carried 22,934 events and built nine drafts, none since 12 July. This is not a
half-built system to finish. It is two working conveyor belts with nothing on the far
end. **Build the far end, not more belt.**

**The automation's job is smaller than it looks, and the constraint is larger.** Tom
scoped the automation down to one act: send the right catalog, say we will be in touch.
That is a day of work. The binding constraint is that a lead who filled a *form* has
never messaged GT, so no conversation window is open, so the message is business-
initiated — see §7.1. The engineering is easy; the channel is the problem.

**Silence is a feature, and it is the part that will get argued away.** No matching
playbook row means nothing is sent. A matcha catalog to someone who asked about chai is
worse than silence: it proves nobody read the enquiry. Every reviewer will suggest a
default message. Do not add one.

**The queue is where this dies, not the sender.** The 190 untouched leads of §2.2 sit
there because nobody worked them; Tom recorded
one outcome in ten days. Warming a lead nobody calls converts a cold miss into a warm
miss. Meanwhile the same staff answer WhatsApp in a median of 71 seconds — the capacity
exists in one channel and not the other. §4 W4 exists because of this.

---

## 4. Workstreams

### W1 — The routing table
A table Tom edits, not code someone deploys. New campaign = new row.

Columns: match on `campaign_name` and optional `ad_name`; the asset to send; the message
body; `active`; who approved and when. Most-specific match wins: (campaign + ad) →
(campaign) → **nothing**.

Seed it from live data — `MACHA Leads` / `Matcha Tut`, `MACHA Leads` / `Matcha Mango`,
and `MACHA Leads` / any. Message body per §1.1.3, exact wording from §6.E.

Migration goes in `gt-factory-os/db/migrations/` — **list the directory immediately
before and after writing the numbered file** (`gt-factory-os/CLAUDE.md` §Migrations).
Schema is `sales_core`, never `private_core`.

**Acceptance:** D1, D2.

### W2 — The sender, dry-run first
Resolve the lead's campaign → find the row → render → **log what would be sent** →
return. Sending is behind `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED`, which stays `false`.

Dedupe on (lead, campaign) at the database level, not in application code — the same
lesson the intake already learned.

Do not write the transport until §7.1 is resolved. The dry-run does not need it.

**Acceptance:** D3, D4, D6.

### W3 — Campaign context on the lead card
`/sales/today` and the lead drawer show campaign name, ad name, and what was auto-sent.
Portal repo, Hebrew/RTL — the sales route group is on the Tom-approved Hebrew list
(`gt-factory-os-portal/CLAUDE.md` §UI language). One tranche, per that repo's invariants.

**Acceptance:** D5.

### W4 — Silence the bot's mouth, keep its ears
Tom wants the WhatsApp data kept and the bot stopped talking. **Verify these are two
separate settings before changing either.** If `WHATSAPP_ORDER_INTAKE_ENABLED=false`
also stops `order_intake.wa_event_log` from filling, that is data loss, and it is a
§6 decision, not yours. Report which it is; propose the change; do not apply it.

Also reconcile the naming mismatch in §7.2.

**Acceptance:** none — this is a report plus a proposal.

---

## 5. Scope

**IN:** everything in §4.

**OUT — do not touch, do not "improve":**
- **Any product picker, menu, quantity selector or price display in the automation.**
  Settled, §1.1.3.
- **Automating Green Invoice payment links.** v2 at the earliest. The client can create
  documents; whether a payment link returns is unverified and the existing usage is
  supplier-side.
- **Re-arguing form vs click-to-WhatsApp.** Settled, §1.1.2.
- Any frozen flag or code sentinel (`gt-factory-os/CLAUDE.md` §Frozen).
- `stock_ledger`, `balance_anchors`, `bom_*`, `items`, `components` — factory-os core.
- The Shopify tax misconfiguration (§2.4). Report it; it is not this PR's.
- The unreachable leads counted in §2.2 (no phone, no email) and the undeployed morning
  reminder of §2.4. Both pre-existing.

---

## 6. Tom's part — the complete list, nothing else is his

**A. Hand over the matcha catalog file.** He confirmed it exists. It has no address the
sender can reach. Needs: the file, a decision on where it lives, and a row in
`docs/warehouses/marketing-assets.md`. **W1 seeds and W2 dry-runs without it; nothing
sends until it lands.**

**B. Confirm the VAT rate shown to customers,** and whether the Shopify
`taxesIncluded=true at 17%` config is being fixed separately. Every price a lead sees
depends on this. One answer, one line.

**C. Written approval before `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` flips** — plus a
clean dry-run and ≥24h soak (`docs/decisions/modules/sales-declaration.md` §11).
Nothing reaches a customer before this.

**D. Decide who runs the conversation.** He answered `עוד לא יודע` on 2026-08-27. Build
for Tom alone; keep assignment extensible. Ask again once W1–W3 land — §3 says this is
where the work dies.

**E. Approve the exact message wording,** word for word, per campaign. The shape is
settled (`קטלוג וניצור קשר בהקדם`); the string is not. Note when asking: the word
`בהקדם` is vaguer than a named time, and a specific promise is what makes the
24-hour KPI (§1.1.6) measurable.

**F. Meta Business access** for whatever §7.1 turns out to require — template
submission, or a change to how the lead form hands off. He holds no Meta developer
access (`Sales-Machine/doctrine/decisions.md` D-006); this may need Alex or the agency.

---

## 7. Landmines — do not rediscover these

1. **A form lead has never messaged GT, so no conversation window is open.** Business-
   initiated WhatsApp messages to such a contact require a Meta-approved template plus
   opt-in, and are billed per message. Meta also documents adding a message step to a
   lead ad with an instant form — whether that opens a free entry-point window is
   **unverified**. `gt-factory-os/CLAUDE.md` forbids guessing external API semantics.
   → **Verify against Meta's own documentation and the live Business Manager before
   building any transport.** This decides template lead time and per-message cost. It is
   the first task, and it does not block W1 or the W2 dry-run.
2. **The deployed Edge Function is `gt-order-bot` (v15, updated 2026-06-23). The repo
   contains `supabase/functions/wa-order-bot/`.** Events still arrive, so an ingress is
   live — most likely the Node Fastify route, which the module README calls the primary.
   → Grepping the repo is not sufficient; check deployed functions with
   `list_edge_functions`. This is the exact failure `gt-factory-os/CLAUDE.md` warns about
   under §Shopify writes ("⊥ repeat the 0302 error").
3. **`status='won'` in the database is not a win by Tom's definition.** All three carry
   `matched_existing_customer`. If you report conversions from `status`, you will report
   three wins where Tom counts zero. Any success metric must exclude leads that matched
   an existing customer.
4. **`form_id` and `form_name` are NULL on the live Facebook leads** while the 189
   historical import rows have `form_name` populated. Route on `campaign_name` and
   `ad_name` only. A routing key built on `form_name` matches history and nothing live.
5. **One live lead arrived with empty-string `campaign_name` and `ad_name`, not NULL**
   (a Meta test lead, correctly marked `lost`). Treat `''` as no-match. A `is not null`
   check alone lets it through to the wrong row.
6. **The bot is not idle — it is silenced by design.** Every session in the 30-day window
   of §2.2 is `human_handled` because staff reply from the WhatsApp Business app first, which fires
   `smb_message_echoes` and mutes the bot permanently in that chat. Do not "fix" this as
   a bug; it is coexistence working. It is also why W4 is a report, not a switch.
7. **`git add -A` and `git add .` are stop conditions** in this workspace
   (`gt-factory-os-production-brain/CLAUDE.md` §Stop conditions). Stage explicit paths.

---

## 8. Halt conditions

Inherited set cited in §0. Additions specific to this work:

- **Any outbound message would reach a real phone number** while
  `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` is `false` → **STOP**.
- **The routing lookup finds no row** → send nothing, log the miss, surface it. Never
  substitute a default. This is a runtime rule *and* a design rule.
- **Silencing the bot would also stop ingestion** (§4 W4) → **STOP**, report, do not
  apply. Tom asked to keep that data.
- **A Green Invoice write of any kind** → **STOP**. Out of scope, and
  `gt-factory-os/CLAUDE.md` forbids guessing its semantics.
- **§1.1 appears to have been reversed** by anything you read → **STOP** and ask Tom.
  Those are his decisions, not the repo's.

---

## 9. Final report

Use `gt-factory-os-production-brain/AGENT_TEMPLATE.md` §Output format, with tokens
matching `VERDICT_GLOSSARY.md`. It must carry:

1. What a stranger can now watch working, end to end.
2. Each of D1–D6 ✅/❌ with its evidence pointer. No partial credit.
3. The numbers, re-run from §2.5, against the 2026-08-27 baseline.
4. The artifacts and where they are — migration numbers, PR links, tranche id.
5. What is still Tom's from §6, and what remains genuinely unfinished.
6. The single next action.

Then stamp this file `SHIPPED` / `SUPERSEDED by <path>` / `ABANDONED — why`, with
evidence pointers. A spent masterprompt that still reads LIVE will be re-run.

If anything is not ready, say so first and plainly. `"It should work"` is not evidence.
