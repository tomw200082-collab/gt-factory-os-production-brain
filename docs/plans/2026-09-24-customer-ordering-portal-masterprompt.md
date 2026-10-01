# MASTERPROMPT — an existing GT customer logs in on gteveryday.com and reorders in under a minute, straight into Shopify

**STATUS: LIVE — not yet executed**
<!-- The executing session's last act is to change this line to SHIPPED / SUPERSEDED by
<path> / ABANDONED — why, with evidence pointers (D1–D11 below). -->

> **Usage:** paste this entire file as the first message of a fresh Claude Code session
> with `gt-site`, `gt-factory-os`, `gt-factory-os-production-brain` and `Sales-Machine`
> attached, plus the Shopify, Supabase and GitHub connectors. It takes GT's ordering from
> "every order is a WhatsApp message or a call that Doreen types into Shopify" to "a
> logged-in customer places the order himself and nobody re-keys it". It runs in two
> phases: a deep brainstorm with Tom (Phase A) that ends in a design he approves in
> writing, then the build (Phase B). You stop for Tom only where §6 and §8 say so.
>
> **Provenance:** written 2026-09-24 by the session that took the brand site live. Tom's
> decisions in §1.1 were given in that conversation, one question at a time, on
> 2026-09-24. The numbers in §2 were measured the same day: ShopifyQL and the Admin API on
> the live store, read-only SQL on Supabase project `rvadsozabmxkkrktwgnv`, and a
> repository read of the five GT repos. The draft was red-teamed by an independent
> reviewer on 2026-09-24, and its 12 findings are folded in. Authority, in order:
> `gt-factory-os-production-brain/CLAUDE.md`, `Sales-Machine/CLAUDE.md`,
> `gt-factory-os/CLAUDE.md`, the documents in §0 — cited, never copied.
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
- **Your first action:** run §2.5 and W0 (recon). Then open Phase A with W1 question 1,
  the VAT basis. Write no code before D1.
- **Read first, in this order:**
  1. `gt-factory-os-production-brain/CLAUDE.md`: §Authorization, §New modules, §Watching,
     §Stop conditions, §Evidence, §Forbidden assumptions.
  2. `gt-factory-os-production-brain/MODULE_TEMPLATE.md`. The portal is a new module, so
     no code is written until the declaration is filled and Tom approves it.
  3. `gt-factory-os-production-brain/docs/decisions/LOCKED_DECISIONS.md` §"Orders and
     integrations", `gt-factory-os-production-brain/EXECUTION_POLICY.md` (the approvals
     table), and `gt-factory-os-production-brain/docs/decisions/modules/sales-declaration.md`
     §11 and A.4/A.6.
  4. `Sales-Machine/CLAUDE.md` (the seven truth rules), `Sales-Machine/doctrine/decisions.md`
     (D-010, D-015), and `Sales-Machine/recipes/sales-report.md` (the ex-VAT statement,
     Tom 2026-08-05).
  5. `gt-factory-os/api/src/order-intake/README.md`, then `engine/pricing.ts`,
     `engine/build-cart.ts`, `engine/ports.ts`, `worker.ts` and `store.ts`. This is the
     tested pricer, marked `(do not edit)` in the README.
  6. `gt-factory-os/.claude/skills/shopify-draft-order-from-po/SKILL.md`,
     `gt-factory-os/.claude/skills/customer-setup-shopify-gi/SKILL.md`, and
     `gt-factory-os-production-brain/.claude/skills/route-print-pack/SKILL.md`.
  7. `gt-factory-os-production-brain/docs/playbook/operator-playbook-he.md`: Doreen's
     day. Approved by Tom on 2026-07-23.
  8. Earlier attempts at this problem, never decided:
     `gt-factory-os-production-brain/docs/ceo/reports/2026-08-09-shopify-catalog-order.md`
     §"staged plan" and `gt-factory-os/docs/integrations/whatsapp_order_intake_payment_link_design.md`.
  9. `gt-site/README.md`, `gt-site/PUBLISH.md` (stale — see §1.2), and
     `gt-factory-os-production-brain/.claude/skills/shopify-theme/SKILL.md`.
  10. How code ships: `gt-factory-os/.github/workflows/deploy-production.yml` (API and
      migrations) and `gt-factory-os/CLAUDE.md` §Migrations.
- **Authority:** where this document and an authority document disagree, the authority
  document wins and this document is wrong. Say so when you find it. The conflicts
  already known are listed in §1.2. They are **not** resolved by this document, and each
  is resolved only by Tom's written approval in the module declaration (D1).
- **Privacy:** four of the five repos are **public**; only `gt-factory-os` is private
  (repo listing, 2026-09-24). Anything that identifies a customer stays in chat or in
  `gt-factory-os`, never in a public repo. That covers a name, a phone number, a price
  paid, a W0 finding about a customer, the D3 customers, and the Ice Dream address.
  Public documents cite counts and opaque IDs only.
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
  - Record every answer with its date and his words in backticks, in the private spec (D1).
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
| D1 | Three documents exist and Tom approves them in writing: the design spec (`gt-factory-os/docs/superpowers/specs/<date>-customer-portal-design.md`, private); the module declaration (`gt-factory-os-production-brain/docs/decisions/modules/customer-portal-declaration.md`, from `MODULE_TEMPLATE.md`, with no customer data); and, inside the declaration, every §1.2 conflict with Tom's approval of the exception | No written approval from Tom, quoted with its date in the PR, or a §1.2 conflict that the declaration does not name |
| D2 | On a **real internal handset Tom names** (§6), the phone receives a WhatsApp code and logs in. A second real internal handset that is not in the map receives no code and is sent to the lead form or WhatsApp. Numbers in the `+97250000000N` fixture range appear only in tests where the sender is stubbed | The provider log shows no message to the named handset, shows a message to the unmapped one, or shows any live send to a fixture number |
| D3 | For three real customers Tom names, every category price the portal shows equals that customer's most recent paid unit price in that category. The category list is the one Tom approved in W1, and a category the customer never bought shows the list price. Report counts in public, details in private | A comparison query against Shopify order history returns ≥1 mismatch |
| D4 | **D4a (dry-run):** for the test account, the order payload the portal would send carries the D3 prices on the VAT basis Tom fixed in W1 question 1, and it is logged with no write. **D4b:** only after Tom's written go (§8), one real order from the test account appears in Shopify as a real order, not a draft, tagged as a portal order and handled by the cleanup plan agreed beforehand | D4a's logged payload differs from D3 on any line; D4b is placed without Tom's go, or leaves an invoice, LionWheel task or planning demand the cleanup plan does not reverse |
| D5 | An order under the minimum (D-015, on the W1 VAT basis) and an order from an account under credit block each become a **draft** with the reason in the note, and no order | Admin API shows an order created for either, or a draft with no reason |
| D6 | Every **portal order** sends the order email to Ice Dream in the format agreed in W1, through the sender named in W1. Each send has the provider's message id stored against the order. A test recipient is used until Tom approves the real one | A portal order with no stored provider message id, or a body missing a field the agreed format names |
| D7 | Invoicing of portal orders does exactly what Tom decided in W1 about the Green Invoice → Ice Dream switch, and delivery paperwork still prints for those orders (§3.4) | Green Invoice holds a document Tom's decision says must not exist, lacks one it says must exist, or `route-print-pack` has no paperwork for a portal stop |
| D8 | Logged out, no price appears anywhere. The portal's price and catalog endpoints return 401 without a session. The `gt-site` CI price guard lists every new served file the portal adds, and passes | `curl` without a session returns prices, a portal-served file is missing from the guard's list, or the guard fails |
| D9 | The four v1 features in §1.1 S8 work at 390 px width on the test account: usual order, catalog, minimum-order gap, and history with reorder. The Playwright run gets its code through a stubbed sender in a non-production environment | A Playwright run at 390 px cannot complete one of the four |
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
  meets two rules: it is at or above the minimum (D-015), and the account is not under
  credit block.
  - After the cutoff it is still valid and goes to the next day. Leave the details for
    later: `פשוט יהיה ליום אחרי זה- אל תתעסק בזה עכשיו`.
  - Any catalog product may be ordered, including one this customer never bought.
  - Carton quantities are **open**. Do not hard-code them: `נשאיר את הכמויות בקרטונים כרגע כדבר פתוח`.
    `default_pack = 6` in the bot's map (§2.2) is not a portal rule.
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

### 1.2 Conflicts with authority documents — surface them, do not resolve them yourself

Tom's 2026-09-24 decisions collide with these written rules. The module declaration (D1)
names each one, and records Tom's written approval of the exception (or his change of mind):
1. **Customer pricing.** `gt-factory-os-production-brain/CLAUDE.md` §Forbidden
   assumptions forbids `customer pricing in v1`. `LOCKED_DECISIONS.md` says
   `Do not add customer pricing unless explicitly confirmed`, and sales-declaration A.4
   says v1 uses public Shopify pricing. All three are overridden by S4 only once Tom
   approves the exception in the declaration. The CLAUDE.md line is Tom's alone to amend.
2. **Order ownership.** `System does not own customer orders` (`LOCKED_DECISIONS.md`).
   The portal creates orders **in Shopify**, and Shopify stays the owner. The declaration
   states that the portal keeps no order store of its own, only sessions and logs.
3. **Codes as outreach.** It is unknown whether a login code counts as outreach under
   `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` (sales-declaration §11). Tom decides in W1.
   Until he does, treat every send to a real customer as gated.
4. **The pricer is do-not-edit.** The `engine/` is marked `(do not edit)` in
   `gt-factory-os/api/src/order-intake/README.md`, while S3 and S4 need outcomes it does
   not produce today (§3.3). Wrap it. Any change inside `engine/` needs Tom's approval,
   because it also prices WhatsApp orders.
5. **PUBLISH.md is stale.** `gt-site/PUBLISH.md` still records theme `162206646513` as
   UNPUBLISHED and says to stop if that changed. Tom published it on 2026-09-24 at 13:52Z.
   Do not stop: make your first `gt-site` commit update PUBLISH.md to the live state.

## 2. Ground truth — measured 2026-09-24; re-verify at boot

### 2.1 What is built and live

- **Brand site:** Shopify theme `162206646513`, named `GT 2026 Site`, has been MAIN since
  2026-09-24 13:52Z (Tom published it). It is built from the public repo `gt-site`.
- **Pending theme copy:** a copy, `166708576497` (`GT 2026 Site — טפסים למערכת המכירות`),
  waits for Tom's publish. It carries the landing-page lead forms (`gt-site` 69a1cdd,
  `gt-factory-os` #284).
- **Order-intake bot:** `gt-factory-os/api/src/order-intake/`, status "ON, drafts-only"
  per its README.
  - A WhatsApp catalog cart is priced from the customer's purchase history by `engine/`.
  - `buildCart` is ready to commit only when it raises no flag (`engine/build-cart.ts`).
  - The result is a Shopify **draft**. `WHATSAPP_AUTO_COMMIT_ENABLED` is off, and
    flipping it is Tom's call.
  - The phone → customer map lives in `order_intake.wa_customer_map`.
- **Operator process** (`operator-playbook-he.md`, Tom-approved 2026-07-23): an order
  arrives by Shopify, WhatsApp or phone. Doreen enters it into Shopify the same day, and
  an invoice is issued automatically (`→ חשבונית אוטומטית`). Intake cuts off at 14:00,
  and LionWheel locks at 15:00.
- **Delivery paperwork:** `route-print-pack` prints each stop's real Green Invoice
  invoice, and uses a LionWheel waybill only as a last resort (its SKILL.md).
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
- **`order_intake.wa_customer_map`** (SQL, 2026-09-24):
  - 210 phones mapped to 209 customers;
  - all 210 have `bot_enabled = true`, `payment_mode = 'terms'` and `default_pack = 6`;
  - 209 have `pricing_mode = 'special'` and 1 has `'full'`;
  - 15 rows carry a self-map note, meaning the branch awaits human verification (`worker.ts`).
- **Coverage:** those 209 mapped customers compare with 599 customers who ordered in the
  12 months to 2026-08-31 (`Sales-Machine/recipes/customer-count.md`).
  A median of about 39 days between reorders (`customer-product-tracker-2026-08-06.json`)
  is **inferred** from that file in `gt-factory-os-production-brain/docs/analytics/`
  and was not re-measured.
- **The minimum on two bases:** ₪800 ex-VAT per order (`Sales-Machine/doctrine/decisions.md`
  D-015, 2026-08-31). The engine enforces the same floor as ₪944 including VAT
  (`engine/build-cart.ts:23`, `MIN_ORDER_INCL_VAT`).
- **Delivery days:** centre on Sunday, Monday and Thursday, north on Tuesday, south on
  Wednesday. The distributor is Ice Dream (`distributor_ice_dream`, Tom 2026-08-31).

### 2.3 What is NOT built

None of these exists:
- a customer login, of any kind;
- a customer-facing price display;
- a phone one-time-code sender;
- the Ice Dream order email;
- the portal UI;
- the site entry for customers.

Partly built: the category rule. `engine/ports.ts` already falls back to a same-price-tier
"sibling" variant the customer bought (for example, any 0.5 L tea). That fallback raises
`PRICE_INFERRED`, which forces a draft (§3.3).

### 2.4 Known-broken or adjacent — not yours unless it blocks you

- **GitHub deploy is broken.** The `deploy-edge-function` workflow fails with `401
  Unauthorized` because the `SUPABASE_ACCESS_TOKEN` secret is rejected (2026-09-24). Edge
  Functions deploy through the Supabase connector instead.
- **The landing pages are unpublished.** `chai`, `matcha`, `iced-tea` and `ube` are
  unpublished page records, so the `עוד מ־GT` links on those pages return 404
  (2026-09-24).
- **Tax setting.** The store setting `taxesIncluded=true` contradicts ex-VAT pricing. It
  was flagged `WRONG` on 2026-08-05 in
  `gt-factory-os-production-brain/docs/pricing/SESSION_HANDOFF_MASTER_PROMPT.md` and was
  still true on 2026-08-27. W1 question 1 settles which basis the portal uses.
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
query { shop { taxesIncluded plan { displayName shopifyPlus } customerAccountsV2 { customerAccountsVersion } }
        companies(first: 1) { nodes { id } }
        themes(first: 20) { nodes { id name role updatedAt } }
        orders(first: 100, reverse: true, sortKey: CREATED_AT) { nodes { createdAt sourceName app { name } displayFinancialStatus } } }
```
```sql
-- Supabase rvadsozabmxkkrktwgnv, read-only — run 2026-09-24
select pricing_mode, default_pack, payment_mode, bot_enabled,
       (notes ilike '%verify%' or notes ilike '%self%') as self_mapped_note,
       count(*) as phones, count(distinct shopify_customer_id) as customers
from order_intake.wa_customer_map group by 1,2,3,4,5;
```

## 3. What the hard part actually is

1. **The competitor is a WhatsApp message to Doreen.** Zero customers ordered alone in
   90 days (§2.2). Typing "the same as last time" to Doreen costs the customer five
   seconds, so the portal wins only if it is faster than that. Judge every screen against
   that message, not against other B2B portals.
2. **Identity is the product, and Shopify does not hold it.** Most B2B customer records
   deliberately have no email or phone, because a chain's branches share one accounting
   address (`customer-setup-shopify-gi` SKILL.md). The real identity layer is
   `order_intake.wa_customer_map`, but it covers 209 of the 599 ordering customers, and
   15 of its rows are unverified self-maps (§2.2).
   - Build the login on the map.
   - Keep unverified rows out of the portal until someone verifies them. A self-map
     picks the branch with the most orders, so a real order can land on the wrong branch.
   - Ask Tom in W1 how the other customers get mapped.
3. **One pricer — wrapped, not edited.** The engine is tested and marked `(do not edit)`.
   As it stands it contradicts S3 and S4 in four places:
   - `PRICE_GAP` (last paid differs from list) forces a draft.
   - `NO_HISTORY_CATALOG` (a product never bought) forces a draft, while S3 allows it.
   - `PRICE_INFERRED` (the sibling fallback) forces a draft.
   - `pricing_mode = 'special'`, set on 209 of 210 rows, withholds the list price when
     there is no history, while S4 shows it.

   Write a portal wrapper that calls the engine and maps each flag to the S3/S4 outcome
   Tom approves. Start the category model from the engine's same-price-tier sibling, and
   have Tom approve the category list in W1. A second, independent pricer would give the
   same customer two prices within a week.
4. **The billing chain is being replaced under you.** Today the Green Invoice app issues
   an invoice for every Shopify order automatically, and `route-print-pack` prints that
   invoice as each stop's delivery paperwork. From the first real portal order, S7 says
   GT stops invoicing, so both the invoice and the paperwork need a replacement decided
   in W1 before any real order. Invoices must not be produced by default, and stops must
   not go out without paperwork.
5. **"Real order" means every downstream reader must accept it.** Every current order is a
   completed draft with status `PENDING` (§2.2). A real order creates:
   - a numbered Green Invoice document;
   - a LionWheel task;
   - planning demand in factory-os;
   - a stop for `route-print-pack`.

   Trace each path in W0. Create portal orders so they look the same to all of them, and
   agree the cleanup for a test order before placing one (§8).

## 4. Workstreams

### W0 — Recon (first, before Phase A questions)
Run §2.5. Then answer these from the systems, without asking Tom:
- What is `Inventory & OS System`?
- How does a Shopify order reach LionWheel, and what does `route-print-pack` read?
- Is the Green Invoice Shopify app active, and what triggers it?
- Which engine flags fire, and how often, on the last 90 days of orders? (Counts only.)
- Do customers exist who paid two different prices in one category? Give a count; the
  names stay in chat or private.
- Which WhatsApp number and template path can send an authentication code? The order
  line runs in coexistence (`Sales-Machine/CURRENT_STATE.md` U-031).
- Which email sender exists and delivers? Resend's history is in `Sales-Machine/CURRENT_STATE.md`
  U-033 and U-033-a.

**Acceptance:** each answer is written in the private spec with its source and date.

### W1 — Phase A: the deep brainstorm, then the design
Grill Tom on these, in this order. Each question carries your recommendation.
1. **The VAT basis.** Are Shopify line prices entered ex-VAT or tax-inclusive, and what
   does the portal write? The sources disagree: `recipes/sales-report.md` says ex-VAT,
   while `engine/build-cart.ts` and the draft-order skill work tax-inclusive, and the
   store has `taxesIncluded=true`. Everything else depends on this answer.
2. **The category list,** built from the engine's sibling tiers and approved by Tom. D3 is
   checked against it.
3. **The engine flags:** for each of the four in §3.3, the outcome Tom wants in the portal.
4. **Where the portal runs:** a route group on the `gt-factory-os` API behind a
   subdomain, a separate small app, or a theme page with an app proxy. Include the
   hosting cost for Tom to approve, and the public-repo rule from §0.
5. **Chains, branches and mapping:** one login per branch or a head office for many
   branches; how the unmapped customers get mapped; and who verifies the 15 self-maps.
6. **Unknown phone at login:** where it goes. The lead form? A WhatsApp handoff?
7. **The code sender:** the number, the Meta authentication template, an SMS fallback,
   and the coexistence risk. Does a login code count as outreach (§1.2 #3)? Which real
   internal handsets are used for D2?
8. **The Ice Dream email:**
   - the sender and its secret, named in §6;
   - recipient, format and fields;
   - one email per order, or batched;
   - scope: portal orders only, or all orders;
   - the go-live date.
9. **Green Invoice and paperwork:**
   - when automatic invoicing stops, and whether for portal orders only or for all;
   - what `route-print-pack` prints instead;
   - what the customer receives as a document.
10. **Credit block:** the data source, and who sets it.
11. **Order confirmation to the customer:** does the customer get a WhatsApp receipt?
    This is a customer-facing write, so it is gated (§8).
12. **Doreen's new job:** the exceptions queue, and how she sees it.
13. **The hook left for promotions** (S1), without building them.
14. **Every Hebrew label** the customer will read.

**Acceptance:** D1.

### W2 — Identity
- Login is a phone number plus a WhatsApp one-time code, built on `wa_customer_map`.
- Only verified rows can log in.
- Sessions persist on the device. Personal links are signed and expiring.
- A number maps to exactly one customer, and a customer may have many numbers.
- An unmapped number never receives a code. Tests stub the sender.

**Acceptance:** D2.

### W3 — Catalog and pricing API
Both endpoints are auth-only. Prices come from the engine through the wrapper (§3.3). No
price is cached in the browser beyond the session.

**Acceptance:** D3, D8.

### W4 — Order submission
- Dry-run first, and a real order only after §8.
- A clean order becomes a real order, and an exception becomes a draft with its reason.
- It looks like today's completed drafts to every downstream reader (§3.5).
- Idempotent, so a double tap makes one order.
- Tagged as a portal order.

**Acceptance:** D4, D5.

### W5 — Ice Dream email, invoicing and paperwork
Build what W1 decided. Use a test recipient until Tom approves the real one, and store
the provider message id against every send.

**Acceptance:** D6, D7.

### W6 — Portal UI
Hebrew, RTL and mobile-first, carrying the four v1 features (S8) and nothing else. The
`gt-site` house RTL traps are in the `shopify-theme` skill §RTL.

**Acceptance:** D9.

### W7 — The site entry
- Update `gt-site/PUBLISH.md` first (§1.2 #5).
- Add the customer entry with the label Tom approves.
- Add every new served file to the price-guard list in `gt-site/.github/workflows/build.yml`.
- Ship it through a theme copy (landmine 1) and Tom's publish.

**Acceptance:** D8, D10.

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
- edits inside `engine/` without Tom's approval (§1.2 #4);
- native Shopify B2B, Plus or a paid B2B app, unless W1 shows the chosen design needs it
  and Tom approves the cost;
- the site's lead forms and the `sales_core` lead pipeline;
- the frozen flags in `gt-factory-os/CLAUDE.md`;
- flipping `WHATSAPP_AUTO_COMMIT_ENABLED` for the WhatsApp bot. The portal has its own
  path.

## 6. Tom's part — the complete list, nothing else is his

Every approval that §8 halts for is on this list. You ask for each at the moment §8 names.

- **A. Phase A answers.** That includes the VAT basis, the category list, the flag
  outcomes, the credit-block source, and how unmapped customers get mapped (or whether
  Doreen does it).
- **B. Written approval of the design and the module declaration,** including each §1.2
  exception (D1).
- **C. Hosting cost** for the chosen architecture.
- **D. Two real internal handsets for D2:** one mapped, one not.
- **E. Approval to send codes to real customers,** his ruling on whether codes count as
  outreach, and any Meta template approval that needs the Business Manager admin.
- **F. The email sender and its secret.** He sets the secret directly; you verify through
  a delivered test message and never see its value.
- **G. Ice Dream:** the address the order emails go to, and the agreed format.
- **H. The Green Invoice switch date** and the replacement delivery paperwork (§3.4).
- **I. Approval before any real order,** the test account's included, with its cleanup
  plan (§8).
- **J. The three customers for D3,** and approval of every customer-facing Hebrew string
  (the `EXECUTION_POLICY.md` approvals table).
- **K. Publishing** the theme that carries the site entry. Only Tom can publish
  (`gt-site/PUBLISH.md`); the connector refuses.
- **L. The first real customers** to log in (S2 means everyone, eventually).

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
   Writes ship as:
   - migrations through `deploy-production.yml`;
   - API routes through the same workflow;
   - Edge Functions through `deploy_edge_function`.

   Never write through `execute_sql`.
3. **"The deploy workflow is red."** The `deploy-edge-function` GitHub workflow fails
   with a 401 on a rejected token (2026-09-24). Deploy with the Supabase connector's
   `deploy_edge_function`, and copy `verify_jwt` from the deployed function.
4. **"The price guard passed, so nothing leaks."** The `gt-site` CI guard (step
   `No price reaches a served page while prices are off` in `.github/workflows/build.yml`)
   checks **only the files it names**, against `tools/strip_prices.py` `PRICE_TOKENS`. A
   new portal file is unguarded until you add it. Customer prices and phones live only in
   the database and reach an authenticated session at runtime.
5. **"Shopify customer accounts will handle login."** The accounts are `CLASSIC` and
   email-based, and most B2B customers have no email by design (§3.2). The login is on
   the phone map. Do not collect or invent emails to make Shopify accounts work.
6. **"Totals are off by 18%."** VAT is 18% (`0338_repack_small_cans_matcha_hojicha_ube.sql`, 2026-08-27). Two bases are live at once (§2.2, §2.4). Settle W1
   question 1 before showing any total, and state the basis in D3, D4 and D5. Prices to a
   business owner are always quoted ex-VAT (`D-010(ח)`, 2026-08-31).
7. **"Every portal order became a draft."** Those are the engine flags of §3.3. Map them
   in the wrapper; do not loosen them inside `engine/`.
8. **"A real test order is harmless."** It is not. It creates a numbered tax document, a
   LionWheel task and planning demand (§3.5). Dry-run first (D4a), and place a real one
   only with Tom's go and a cleanup plan (D4b).
9. **"Codes stopped arriving."** The order line runs in WhatsApp coexistence. If the
   phone app is not opened for 13 days, the Cloud API link dies silently
   (`Sales-Machine/CURRENT_STATE.md` U-031). Build a fallback and a loud monitor.
10. **"The email was sent."** The house sender once delivered only to Tom and logged the
    failed sends as delivered (`Sales-Machine/CURRENT_STATE.md` U-033). Count a send only
    when the provider returns a message id (D6).
11. **"The distributor is in the old docs as delivery only."** Billing through Ice Dream
    is Tom's decision of 2026-09-24 (S7) and is written nowhere else yet. Record it in
    `Sales-Machine/doctrine/decisions.md`; Sales-Machine truth rule 5 means Tom approves
    the entry.
12. **"Test with a fake number."** `+97250000000N` is a test-fixture convention
    (`gt-factory-os/db/tests/0265_*`, `0321_*`), not a reserved range. It has a valid
    Israeli mobile format and no WhatsApp behind it. Use it only where the sender is
    stubbed. Live code tests use the real internal handsets from §6 D.

## 8. Halt conditions

These add to the inherited set in `gt-factory-os-production-brain/CLAUDE.md` §Stop
conditions. When one applies, **STOP**, surface it to Tom, and do not improvise.
- Before any code: D1 is not yet approved.
- Before any real Shopify order, the test account's included. Tom's written go and a
  cleanup plan come first (`EXECUTION_POLICY.md`: money- and customer-facing writes need
  written approval and a dry-run).
- Before sending any WhatsApp message or code to a phone that is not one of Tom's named
  internal handsets.
- Before any change inside `engine/`.
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
   reasons, and mismatches found in D3 (counts only).
4. The artifacts, and where they are: PRs, the spec, the declaration, and the deployed
   function versions.
5. What is still Tom's, and what remains genuinely unfinished.
6. The single next action.

If anything is not ready, say so first and plainly.
