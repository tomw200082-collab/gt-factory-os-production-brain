# MASTERPROMPT — an existing GT customer logs in on gteveryday.com and reorders in under a minute, straight into Shopify

**STATUS: LIVE — not yet executed**
<!-- The executing session's last act is to change this line to SHIPPED / SUPERSEDED by
<path> / ABANDONED — why, with evidence pointers (D1–D11 below). -->

> **Usage:** paste this entire file as the first message of a fresh Claude Code session
> with `gt-site`, `gt-factory-os`, `gt-factory-os-production-brain` and `Sales-Machine`
> attached, plus the Shopify, Supabase and GitHub connectors. It takes GT's ordering from
> "every order is a WhatsApp message or a call that Doreen types into Shopify" to "a
> logged-in customer places the order himself and nobody re-keys it". The work runs in
> two phases: a deep brainstorm with Tom (Phase A) that ends in a design he approves in
> writing, then the build (Phase B). You stop for Tom only where §6 says so.
>
> **Provenance:** written 2026-09-24 by the session that took the brand site live. Tom's
> decisions in §1.1 were given in that conversation, one question at a time, on
> 2026-09-24. The numbers in §2 were measured the same day: ShopifyQL and the Admin API on
> the live store, read-only SQL on Supabase project `rvadsozabmxkkrktwgnv`, and a
> repository read of the five GT repos. Authority, in order: `gt-factory-os-production-brain/CLAUDE.md`,
> `Sales-Machine/CLAUDE.md`, `gt-factory-os/CLAUDE.md`, the documents in §0 — cited, never copied.
>
> **Shelf life:** §2 is presumed wrong if pasted after 2026-10-08. Run §2.5 first. If the
> numbers moved, adapt and say so in your first message. If a **settled decision in §1.1**
> looks contradicted by what you find (for example, Ice Dream is no longer the
> distributor), halt and ask Tom before building on it.

## 0. How to work

- **Who you are here:** a Claude Code session in a cloud container. You hold the repos
  above and three connectors:
  - **Shopify Admin:** reads, and theme-file writes **to unpublished themes only**. It
    refuses writes to the live theme and refuses `themePublish`.
  - **Supabase:** `execute_sql` runs **read-only**. `deploy_edge_function` works.
  - **GitHub:** commits, PRs, merges.

  You decide technical design alone inside §1.1. Everything a customer sees or receives,
  and every product decision, is Tom's.
- **Your first action:** run §2.5 and W0 (recon). Then open Phase A with one question to
  Tom. Write no code before Tom approves the design in writing (D1).
- **Read first, in this order:**
  1. `gt-factory-os-production-brain/CLAUDE.md`: §Authorization, §New modules, §Watching,
     §Stop conditions, §Evidence.
  2. `gt-factory-os-production-brain/MODULE_TEMPLATE.md`. The portal is a new module, so
     no code is written until this template is filled and Tom approves it.
  3. `gt-factory-os-production-brain/docs/decisions/LOCKED_DECISIONS.md` §"Orders and
     integrations", which includes `System does not own customer orders` and
     `Do not add customer pricing unless explicitly confirmed`. Tom confirmed customer
     pricing for this portal on 2026-09-24 (§1.1 S4). Record that confirmation in the
     module declaration.
  4. `gt-factory-os-production-brain/docs/decisions/modules/sales-declaration.md` §11
     (customer-facing writes) and A.4/A.6.
  5. `Sales-Machine/CLAUDE.md` (the seven truth rules) and
     `Sales-Machine/doctrine/decisions.md` (D-010, D-015).
  6. `gt-factory-os/api/src/order-intake/README.md` and its `engine/`: the tested pricer
     that already prices WhatsApp carts.
  7. `gt-factory-os/.claude/skills/shopify-draft-order-from-po/SKILL.md` and
     `gt-factory-os/.claude/skills/customer-setup-shopify-gi/SKILL.md`.
  8. `gt-factory-os-production-brain/docs/playbook/operator-playbook-he.md`: Doreen's
     day. Approved by Tom on 2026-07-23.
  9. `gt-factory-os-production-brain/docs/ceo/reports/2026-08-09-shopify-catalog-order.md`
     §"staged plan" and `gt-factory-os/docs/integrations/whatsapp_order_intake_payment_link_design.md`:
     earlier attempts at this problem, never decided.
  10. `gt-site/README.md`, `gt-site/PUBLISH.md`, and
      `gt-factory-os-production-brain/.claude/skills/shopify-theme/SKILL.md`.
- **Authority:** where this document and an authority document disagree, the authority
  document wins and this document is wrong. Say so when you find it.
- **Halt conditions, evidence standard, git discipline:** inherited from
  `gt-factory-os-production-brain/CLAUDE.md` §Stop conditions, §Evidence, §Watching. The
  §Watching line binds you: after you open a PR, call `unsubscribe_pr_activity` at once
  unless Tom asked for that PR to be watched. The additions specific to this work are
  in §8.
- **Phase A method (the brainstorm):**
  - Ask one question per message, and give your recommended answer with a one-sentence
    reason.
  - If a question can be answered from the repos or live systems, answer it yourself;
    do not ask Tom.
  - Tom decides fast and dislikes option menus: recommend, do not list.
  - Record every answer in the design doc with the date and his words in backticks.
- **The standard:** Tom's words for this work are `שיהיה להם קל`, `לשדר רצינות ומקצועיות`,
  and `לתת ללקוחות לגיטימציה להזמין יותר` (2026-09-24). For the site he said
  `אסור שיהיו בו טעויות`. As checkable prohibitions:
  1. A customer never sees a price different from the one on the order it creates.
  2. A clean portal order is never re-typed by anyone.
  3. No customer price, phone number or customer identifier appears on a logged-out page
     or in a public repository.
- **Language:** this document is in English because that is the register the executor
  reasons best in. Data literals and Tom's words stay in Hebrew, in backticks, and are
  never translated. **Output language: Hebrew when talking to Tom** — short, direct, no
  preamble, one question per message. Code, commits, PR bodies and docs are in English.
  Customer-facing copy is Hebrew and needs Tom's approval (§6).

## 1. Mission and definition of done

**One testable sentence:** an existing GT business customer opens gteveryday.com and taps
the customer entry. They log in with their phone number and a code sent by WhatsApp, and
order at their own category prices. A clean order lands in Shopify as a real order that
nobody re-keys, and any other order lands as a draft for Doreen with its reason written on it.

| # | Condition | The observation that would prove it false |
|---|---|---|
| D1 | The design spec and the filled module declaration (`docs/decisions/modules/customer-portal-declaration.md`, from `MODULE_TEMPLATE.md`) are approved by Tom in writing | No message from Tom approving them, quoted with its date in the PR that adds them |
| D2 | A test phone in the reserved fake range `+97250000000N`, mapped to a GT-internal test Shopify customer, receives a WhatsApp code and logs in. A phone mapped to no customer receives no code and is sent to the lead form or WhatsApp | The provider log shows no message to the test phone, or shows a message to the unmapped phone |
| D3 | For three real customers Tom names, every category price the portal shows equals that customer's most recent paid unit price in that category. A category the customer never bought shows the list price | A query comparing portal prices against Shopify order history returns ≥1 mismatch |
| D4 | A clean order from the test account appears in Shopify as a **real order**, not a draft. Its line prices equal D3, it carries a tag that identifies the portal, and its financial status matches today's orders (`PENDING`, §2.2) | Admin API `orders` does not show it, or shows it as a draft, or its prices differ |
| D5 | An order under the ₪800 ex-VAT minimum (D-015), and an order from an account under credit block, each become a **draft** with the reason in the note, and no order | Admin API shows an order created for either, or a draft with no reason |
| D6 | Every portal order sends the order email to Ice Dream in the format agreed in Phase A. It goes to a test address until Tom approves the real one | The provider log has no message for an order, or its body lacks a field the agreed format names |
| D7 | Invoicing of portal orders does exactly what Tom decides in Phase A about the Green Invoice → Ice Dream switch (§3.4) | Green Invoice holds a document for a portal order that Tom's decision says must not exist, or lacks one it says must exist |
| D8 | Logged out, no price appears anywhere. The portal's price and catalog endpoints return 401 without a session, and the `gt-site` CI price guard passes | `curl` without a session returns prices, or CI step `No price reaches a served page while prices are off` fails |
| D9 | The four v1 features in §1.1 S8 work at 390 px width: usual order, catalog, minimum-order gap, and history with reorder | A Playwright run at 390 px cannot complete one of the four on the test account |
| D10 | gteveryday.com carries a customer entry, with a label Tom approved, that leads to login. This holds on the live theme after Tom publishes it | The live home page has no such entry, or it leads to a 404 |
| D11 | This file's status line is stamped `SHIPPED` / `SUPERSEDED` / `ABANDONED` with evidence pointers | The line still reads `LIVE` after the work ends |

Anything not on this list is out of scope unless Tom asks.

### 1.1 Settled — do not reopen

All of these are Tom's decisions, given 2026-09-24, one question at a time.

- **S1 — Goals:** less operational load on Doreen, fewer errors, more automation, easier
  for customers, look serious and professional, and give customers legitimacy to order
  more. In his words: `זה מאוד רוחבי ולא בגלל מטרה אחת`. Promotions come later, but the
  design must leave room for them: `נוכל לעשות משם מבצעים וכו'. אבל זה לאחרי זה`.
- **S2 — Audience and rollout:** existing customers. Open to all of them and move
  everyone over gradually: `פותחים לכולם- ולאט לאט מעבירים את כולם`. There is no pilot
  cohort. KPIs come later (`זה KPI שנבין אחרי זה`), so do not block on them.
- **S3 — A clean order is a real Shopify order, placed without Doreen.** A clean order
  meets two rules: it is at or above the ₪800 ex-VAT minimum (D-015), and the account is
  not under credit block.
  - After the cutoff it is still valid and goes to the next day. Leave the details for
    later: `פשוט יהיה ליום אחרי זה- אל תתעסק בזה עכשיו`.
  - Any catalog product may be ordered, including one this customer never bought.
  - Carton quantities are **open**. Do not hard-code them: `נשאיר את הכמויות בקרטונים כרגע כדבר פתוח`.
- **S4 — Prices:** a logged-in customer sees only their own prices, ex-VAT, with the
  total before sending. Prices are per customer × category. Tom:
  `המחירים הם לפי קטגוריות- למשל בקבוקי 1 ליטר הם באותו המחיר`.
  - A category the customer has bought: their last paid price in that category.
  - A category they never bought: the list price.
  - Logged-out visitors see no prices. That is Tom's rule of the same morning,
    `gt-site/data/site_flags.json` `show_prices: false`.
- **S5 — Login:** phone number plus a one-time code sent by WhatsApp. No password and no
  email. Several numbers may belong to one customer, the device stays logged in, and
  personal links in GT's messages open the portal already logged in.
- **S6 — No payment step.** Tom: `אף לקוח לא משלם מיד`. Every mapped customer is on terms (§2.2).
- **S7 — Billing moves to the distributor.** GT stops issuing the invoice directly:
  - Each order becomes a structured email with the order details, sent straight to Ice
    Dream (`אייס דרים`), the distributor that already delivers
    (`Sales-Machine/knowledge/claims/public-claims.yaml` `distributor_ice_dream`,
    2026-08-31).
  - At month end GT totals the sales, and Ice Dream pays GT on the terms agreed between
    them.
  - Tom: `לא נוציא ישר חשבונית- פשוט יצא מייל מסודר עם פרטי ההזמנה ישירות לאייסדרים`.
- **S8 — v1 is four features:**
  1. The usual order: the last order prefilled, quantities editable.
  2. The catalog by category, with photos and the customer's own prices.
  3. Before sending, how far the order is from the minimum.
  4. Order history with reorder.

  **Not** a delivery date: `אל תוסיף מתי ההזמנה תגיע`.
- **S9 — Orders land in Shopify:** `הוא צריך לאפשר הזמנה ישירות בשופיפיי כמובן`.

## 2. Ground truth — measured 2026-09-24; re-verify at boot

### 2.1 What is built and live

- **Brand site:** Shopify theme `162206646513`, named `GT 2026 Site`, has been MAIN since
  2026-09-24 13:52Z (Tom published it). It is built from the public repo `gt-site`.
- **Pending theme copy:** a copy, `166708576497` (`GT 2026 Site — טפסים למערכת המכירות`),
  waits for Tom's publish. It carries the landing-page lead forms (`gt-site` 69a1cdd,
  `gt-factory-os` #284).
- **Order-intake bot:** `gt-factory-os/api/src/order-intake/`, status "ON, drafts-only"
  per its README.
  - A WhatsApp catalog cart is priced from the customer's own purchase history by the
    tested `engine/`, which also holds the double-VAT guard.
  - The result is a Shopify **draft**. `WHATSAPP_AUTO_COMMIT_ENABLED` is off, and
    flipping it is Tom's call.
  - The phone → customer map lives in `order_intake.wa_customer_map`.
- **Operator process** (`operator-playbook-he.md`, Tom-approved 2026-07-23): an order
  arrives by Shopify, WhatsApp or phone. Doreen enters it into Shopify the same day, and
  an invoice is issued automatically. Intake cuts off at 14:00, and LionWheel locks at 15:00.
- **Lead pipeline**, which is separate from ordering: the site forms feed
  `website_lead_intake` (v8, 2026-09-24), then `sales-leads-poll` `/ingest`, then
  `sales_core`. It carries **new** enquiries. Do not route existing customers' orders
  through it.

### 2.2 The numbers

- **Orders by sales channel**, last 90 days to 2026-09-24 (ShopifyQL, §2.5):
  - `Inventory & OS System` 765
  - `Draft Orders` 382
  - `Shopify Claude Connector App` 51
  - **Online Store 0**

  The storefront had 3,432 sessions (ShopifyQL, 2026-09-24), 23 with a cart addition,
  and **0 completed checkouts** (same query and date).
- **The latest 100 orders**, created from 2026-09-14 to 2026-09-24 (Admin API, §2.5): every
  one has `sourceName: shopify_draft_order` and financial status `PENDING`. That is 28
  orders on 2026-09-22 and 20 on 2026-09-23.
- **Shop:** plan `Shopify`, not Plus. Customer accounts are `CLASSIC`, and there are 0
  B2B companies (Admin API, 2026-09-24).
- **`order_intake.wa_customer_map`:** 210 phones mapped to 209 customers. All 210 have
  `bot_enabled = true` and `payment_mode = 'terms'`, with 0 `pay_now` (SQL, 2026-09-24).
- **Customer base:** 599 customers and 4,088 orders in the 12 months to 2026-08-31
  (`Sales-Machine/recipes/customer-count.md`). A median of about 39 days between
  reorders is **inferred** from
  `gt-factory-os-production-brain/docs/analytics/customer-product-tracker-2026-08-06.json`
  and was not re-measured.
- **Minimum order:** ₪800 ex-VAT, per order, not per month (`Sales-Machine/doctrine/decisions.md` D-015, 2026-08-31).
- **Delivery days:** centre on Sunday, Monday and Thursday, north on Tuesday, south on
  Wednesday. The distributor is Ice Dream (`distributor_ice_dream`, Tom 2026-08-31).

### 2.3 What is NOT built

None of these exists:
- a customer login, of any kind;
- a customer-facing price display;
- the category pricing rule (the engine prices **per product**, from the last paid line);
- a phone one-time-code sender;
- the Ice Dream order email;
- the portal UI;
- the site entry for customers.

### 2.4 Known-broken or adjacent — not yours unless it blocks you

- **GitHub deploy is broken.** The `deploy-edge-function` workflow fails with `401
  Unauthorized` because the `SUPABASE_ACCESS_TOKEN` secret is rejected (2026-09-24). Edge
  Functions deploy through the Supabase connector instead.
- **The landing pages are unpublished.** `chai`, `matcha`, `iced-tea` and `ube` are
  unpublished page records, so the `עוד מ־GT` links on those pages return 404
  (2026-09-24).
- **Tax setting.** The store setting `taxesIncluded=true` contradicts ex-VAT pricing. It
  was flagged `WRONG` on 2026-08-05 in `docs/pricing/SESSION_HANDOFF_MASTER_PROMPT.md` and
  was still true on 2026-08-27. Re-check it before you compute any total.
- **Four orderable leftovers.** Four SKUs taken off the customer price list stay
  orderable on the store by Tom's choice (`D-010(י)`, 2026-08-31).
- **Unidentified channel.** The `Inventory & OS System` channel has not been identified,
  and it created 765 orders in 90 days (§2.2).

### 2.5 Re-verification block

```text
# ShopifyQL — run 2026-09-24 (run-analytics-query)
FROM sales SHOW orders, customers GROUP BY sales_channel SINCE -90d UNTIL today
FROM sessions SHOW sessions, sessions_with_cart_additions, sessions_that_completed_checkout SINCE -90d UNTIL today
```
```graphql
# Admin GraphQL — run 2026-09-24
query { shop { plan { displayName shopifyPlus } customerAccountsV2 { customerAccountsVersion } }
        companies(first: 1) { nodes { id } }
        themes(first: 20) { nodes { id name role updatedAt } }
        orders(first: 100, reverse: true, sortKey: CREATED_AT) { nodes { createdAt sourceName app { name } displayFinancialStatus } } }
```
```sql
-- Supabase rvadsozabmxkkrktwgnv, read-only — run 2026-09-24
select count(*) phones, count(distinct shopify_customer_id) customers,
       count(*) filter (where bot_enabled) bot_enabled,
       count(*) filter (where payment_mode = 'pay_now') pay_now
from order_intake.wa_customer_map;
```

## 3. What the hard part actually is

1. **The competitor is a WhatsApp message to Doreen.** Zero customers ordered alone in
   90 days (§2.2). Typing "the same as last time" to Doreen costs the customer five
   seconds, so the portal wins only if it is faster than that. Judge every screen against
   that message, not against other B2B portals.
2. **Identity is the product, and Shopify does not hold it.** Most B2B customer records
   deliberately have no email, because a chain's branches share one accounting address
   (`customer-setup-shopify-gi` SKILL.md). Some older records carry placeholder addresses.
   The real identity layer is `order_intake.wa_customer_map` (210 phones, §2.2).
   Classic Shopify accounts (email and password) are the wrong base; build the login on
   the phone map.
3. **One pricer, not two.** The engine that prices WhatsApp carts from purchase history
   is tested, and it carries the double-VAT guard. Extend it with the category rule (S4)
   and call it from the portal. A second pricer means two prices for the same customer
   within a week.
4. **The billing chain is being replaced under you.** Today the Green Invoice app issues
   an invoice for every Shopify order automatically (`operator-playbook-he.md`: `→ חשבונית אוטומטית`).
   From the first real portal order, that is exactly what S7 says must stop. The switch to
   Ice Dream (its timing, the email format, and what the customer receives as a document)
   has to be decided with Tom in Phase A. Invoices must not be produced by default.
5. **"Real order" means every downstream reader must accept it.** Every current order is a
   completed draft with status `PENDING` (§2.2). Before the first real portal order,
   trace where a Shopify order goes today: LionWheel, the Green Invoice app, factory-os
   planning and reports. Create portal orders so they look the same to all of them. The
   order-intake bot's auto-commit path already does this conversion (README), so reuse it.

## 4. Workstreams

### W0 — Recon (first, before Phase A questions)
Run §2.5. Then answer these from the systems, without asking Tom:
- What is `Inventory & OS System`?
- How does a Shopify order reach LionWheel?
- Is the Green Invoice Shopify app active, and what triggers it?
- What is the category list? Start from
  `gt-factory-os-production-brain/docs/warehouses/catalog-truth.md` and the engine's
  product model.
- Do customers exist who paid two different prices in one category?
- Which WhatsApp number and template path can send an authentication code? The order
  line runs in coexistence (`Sales-Machine/CURRENT_STATE.md` U-031).

**Acceptance:** each answer written in the design doc with its source and date.

### W1 — Phase A: the deep brainstorm, then the design
Grill Tom on these, in roughly this order. Each question carries your recommendation.
1. **Where the portal runs:** a route group on the `gt-factory-os` API behind a
   subdomain, a separate small app, or a theme page with an app proxy. Include hosting
   cost and the §0 constraint that public repos never hold prices.
2. **Chains and branches:** one login per branch, or a head office ordering for its
   branches.
3. **Unknown phone at login:** where it goes. The lead form? A WhatsApp handoff?
4. **The code sender:** the number, the Meta authentication template, an SMS fallback,
   and the coexistence risk.
5. **The Ice Dream email:** recipient, format, fields, one email per order or batched,
   the go-live date, and what the customer receives as a document.
6. **Green Invoice:** when automatic invoicing stops, and whether that is for portal
   orders only or for all orders.
7. **Credit block:** the data source, and who sets it.
8. **Category-price edge cases** found in W0.
9. **Order confirmation to the customer:** does the customer get a WhatsApp receipt?
   This is a customer-facing write, so it is gated (§8).
10. **Doreen's new job:** the exceptions queue, and how she sees it.
11. **The hook left for promotions** (S1), without building them.
12. **Every Hebrew label** the customer will read.

**Acceptance:** D1 — the spec in
`gt-factory-os-production-brain/docs/superpowers/specs/<date you write it>-customer-portal-design.md`
and the filled module declaration, approved by Tom in writing.

### W2 — Identity
- Login is a phone number plus a WhatsApp one-time code, built on `wa_customer_map`.
- Sessions persist on the device. Personal links are signed and expiring.
- A number maps to exactly one customer, and a customer may have many numbers.
- An unmapped number never receives a code.

**Acceptance:** D2.

### W3 — Catalog and pricing API
Both endpoints are auth-only. Prices come from the extended engine (§3.3). No price is
cached in the browser beyond the session.

**Acceptance:** D3, D8.

### W4 — Order submission
- A clean order becomes a real order and an exception becomes a draft with its reason.
- The same pipeline shape as the bot's auto-commit.
- Idempotent, so a double tap makes one order.
- Tagged as a portal order.

**Acceptance:** D4, D5.

### W5 — Ice Dream email and invoicing switch
Build what Phase A decided. Use a test recipient until Tom approves the real one.

**Acceptance:** D6, D7.

### W6 — Portal UI
Hebrew, RTL and mobile-first, carrying the four v1 features (S8) and nothing else. The
`gt-site` house RTL traps are in the `shopify-theme` skill §RTL.

**Acceptance:** D9.

### W7 — The site entry
Add the customer entry to `gt-site` with the label Tom approves. Ship it through a theme
copy (landmine 1) and Tom's publish.

**Acceptance:** D10.

### W8 — Close
Stamp this file (D11) and give the §9 report.

## 5. Scope

**IN:** everything in §4.

**OUT — do not build, do not "improve":**
- a delivery date on the order (S8);
- shipment tracking;
- invoices or statements shown in the portal;
- promotions, recommendations and automated reminders (S1 says later);
- a payment step (S6);
- changing any customer's commercial terms;
- KPIs and dashboards (S2);
- a pilot cohort (S2);
- native Shopify B2B, Plus or a paid B2B app, unless W1 shows the chosen design needs it
  and Tom approves the cost;
- the site's lead forms and the `sales_core` lead pipeline;
- the frozen flags in `gt-factory-os/CLAUDE.md`;
- flipping `WHATSAPP_AUTO_COMMIT_ENABLED` for the WhatsApp bot. The portal has its own
  path.

## 6. Tom's part — the complete list, nothing else is his

- **A. Phase A answers:** about a dozen questions, a few minutes each.
- **B. Written approval of the design and the module declaration (D1).** The house rule
  makes this his alone.
- **C. The Ice Dream contact:** the address the order emails go to, and agreement on the
  format. Only he holds that relationship.
- **D. The Green Invoice switch date** (S7, §3.4). It is a financial-process change.
- **E. Approval to send codes to real customers,** and any Meta template approval that
  needs the Business Manager admin. It is a customer-facing write (§8).
- **F. The three customers for D3,** and approval of every customer-facing Hebrew string
  (house rule, `EXECUTION_POLICY.md`).
- **G. Publishing the theme that carries the site entry.** Only Tom can publish
  (`gt-site/PUBLISH.md`); the connector refuses.
- **H. The first real customer login.** He names who goes first, since S2 means everyone
  eventually.

## 7. Landmines — do not rediscover these

1. **"Upload to the live theme failed."** The Shopify connector refuses writes to the
   MAIN theme by design.
   - Fix: `themeDuplicate` the live theme, wait until `processing: false`, upload to the
     copy, and ask Tom to publish.
   - Duplication **re-serializes JSON templates**. On 2026-09-24 it dropped a removed
     section setting and two app blocks of an uninstalled app from
     `templates/product.json`.
   - Before asking Tom to publish, diff `templates/*.json` and `config/*.json` between
     the live theme and the copy, and explain every difference.
2. **"`execute_sql` failed on a write."** The Supabase connector runs read-only
   transactions. On 2026-09-24 even `sales_core.set_lead_status` failed with `25006`.
   Writes go through the API, a migration, or an Edge Function, never through `execute_sql`.
3. **"The deploy workflow is red."** The `deploy-edge-function` GitHub workflow fails
   with a 401 on a rejected token (2026-09-24). Deploy with the Supabase connector's
   `deploy_edge_function`, and copy `verify_jwt` from the deployed function.
4. **"I'll store the price table in the repo."** `gt-site`,
   `gt-factory-os-production-brain`, `Sales-Machine` and `gt-factory-os-portal` are
   **public**; only `gt-factory-os` is private (repo listing, 2026-09-24). Customer prices
   and phones live only in the database, and are served at runtime to an authenticated
   session. The `gt-site` CI fails on any ₪ in theme files
   (`tools/strip_prices.py` `PRICE_TOKENS`).
5. **"Shopify customer accounts will handle login."** The accounts are `CLASSIC` and
   email-based, and most B2B customers have no email by design (§3.2). The login is on
   the phone map. Do not collect or invent emails to make Shopify accounts work.
6. **"Totals are off by 18%."** Check the store's `taxesIncluded` flag (§2.4) and the
   engine's double-VAT guard before you show any total. Prices to a business owner are
   always ex-VAT (`D-010(ח)`, 2026-08-31).
7. **"Last paid price" means two different things.** The draft-order skill and the
   engine price **per product**, but Tom's rule is **per category** (S4). If a customer
   paid two prices within one category, the category price is the most recent paid unit
   price in that category. Show Tom the affected customers found in W0 before building.
8. **"Real order" breaks something downstream.** A portal order that looks different from
   today's completed drafts can skip LionWheel or picking. Trace the path (W0, §3.5)
   before the first real order.
9. **"Codes stopped arriving."** The order line runs in WhatsApp coexistence. If the
   phone app is not opened for 13 days, the Cloud API link dies silently
   (`Sales-Machine/CURRENT_STATE.md` U-031). Build a fallback and a loud monitor.
10. **"The distributor is in the old docs as delivery only."** Billing through Ice Dream
    is Tom's decision of 2026-09-24 (S7) and is written nowhere else yet. Record it in
    `Sales-Machine/doctrine/decisions.md`; Sales-Machine truth rule 5 means Tom approves
    the entry.
11. **"Test with a real customer's phone."** Use the fake range `+97250000000N`. The
    lead pipeline's test leads already use `+972500000001` to `+972500000004`
    (`sales_core.lead`, 2026-09-24), so start the portal's tests at `+972500000010`.

## 8. Halt conditions

These add to the inherited set in `gt-factory-os-production-brain/CLAUDE.md` §Stop
conditions. When one applies, **STOP**, surface it to Tom, and do not improvise.
- Before any code: D1 is not yet approved.
- Before sending any WhatsApp message or code to a phone outside the fake test range.
- Before the first real order from a real customer's login.
- Before changing anything in the Green Invoice app, or sending a real email to Ice Dream.
- When a price the portal would show differs from the customer's last paid price in that
  category, and the case is not already settled in the spec.
- When any step needs a setting, secret or approval only Tom holds. Name the secret;
  never ask for its value in chat.

## 9. Final report

Use the house handoff: `gt-factory-os-production-brain/CLAUDE.md` §Handoff. That means a
STATUS token from `VERDICT_GLOSSARY.md` plus the eight PASS fields. Then add:
1. What a stranger can watch working now, end to end, with a link.
2. D1–D11, each ✅/❌ with its evidence pointer. No partial credit.
3. The numbers: orders placed through the portal, drafts sent to Doreen and their
   reasons, and mismatches found in D3.
4. The artifacts, and where they are: PRs, the spec, the declaration, and the deployed
   function versions.
5. What is still Tom's, and what remains genuinely unfinished.
6. The single next action.

If anything is not ready, say so first and plainly.
