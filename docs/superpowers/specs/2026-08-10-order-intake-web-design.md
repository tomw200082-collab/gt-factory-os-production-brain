# Design — web order intake: catalog page → Shopify draft → approved payment link → tax invoice

**Date:** 2026-08-10 · **Status:** DESIGN, approved by Tom in chat 2026-08-10. Not built.
**Module declaration:** `docs/decisions/modules/order-intake-web-declaration.md`
**Predecessor design (the money rail this reuses):**
`gt-factory-os/docs/integrations/whatsapp_order_intake_payment_link_design.md`

## Goal

A HoReCa buyer — new or existing — opens a page, builds an order from the GT
catalog, and submits it. The order lands in Shopify as a **draft**. A human at GT
checks it and corrects the prices to that customer's agreed prices. On approval the
draft's payment link goes to the customer; PayPlus collects; the paid order triggers
the existing Green Invoice ↔ Shopify app, which issues the חשבונית מס/קבלה.

## What already exists — and is therefore not being built

This is the largest fact in the design. Three of the seven pieces are already live.

| Piece | State |
|---|---|
| Payment collection | **PayPlus is already the Shopify gateway.** A draft order's `invoiceUrl` already charges ₪ on gteveryday.com. |
| Tax document | **Green Invoice ↔ Shopify app already issues** the חשבונית מס/קבלה on a paid order. |
| Order → Shopify | `gt-factory-os/api/src/order-intake/shopify/commit.ts` already creates drafts, with the money guards below. |
| Customer prices | `order-intake/engine/pricing.ts` — real last-paid price, discount-aware, with same-tier sibling inference. |
| Live sellable stock | `shopify_available_reconcile` already holds Shopify `available` = `on_hand − committed`, refreshed every 5 min from our truth. |

**No PayPlus integration is written. No Green Invoice integration is written. No
Make scenario is involved anywhere on this path.**

The order-intake commit path carries scar tissue that must not be re-earned:
`placeCartLines` (every approved line becomes a real line item — the 2026-07-02
incident where 1 of 4 lines reached Shopify), the double-VAT guard, `claimSession`
CAS against double-submit, and the ₪944 tax-inclusive floor. **The web channel is a
second front door onto that same path, never a second implementation of it.**

## Flow

```
catalog page  (list prices, ex-VAT)
     │  buyer builds cart + business details
     ▼
POST /order-intake/web        → same engine, same guards
     ▼
Shopify draft order           tagged `web-order`, `needs-review`
     │                        NOT sent for payment
     ▼
human approval screen         lines checked · prices set to this customer's
     │                        agreed prices
     ▼
draft.invoiceUrl → customer   (email / WhatsApp)
     ▼
PayPlus collects  →  order paid  →  Green Invoice issues חשבונית מס/קבלה
```

**Manual approval is not only caution — it removes the build.** Every NO-GO finding
in the predecessor's money-safety review (C1 `orders/paid`→draft correlation, C2
link idempotency, C3 the ₪5,000 allocation-number gate, C4 ex-VAT threshold
comparison) applies to *auto-sending* a link. A human-approved rail is the fallback
path that design already specifies, so v1 ships without building any of them.

They come back the day anyone wants auto-send. That is a separate phase.

## Pricing

The page shows **one wholesale list price, ex-VAT, to everyone.** Customer-specific
prices are applied by a human at the approval step, from the existing last-paid
engine.

The page says so plainly, near the total — not in a footer, not as "subject to
approval":

> המחירים המוצגים הם מחירון סיטונאי, ללא מע״מ.
> ללקוחות עם מחירים מוסכמים — המחיר שלכם יופיע בלינק התשלום.

## Order composition — the carton rule

### The question

Tom's concern: single-bottle lines hurt the picker and invite mistakes, so should
there be a per-flavour minimum?

### The evidence

`private_core.orders_mirror` + `orders_mirror_lines` — 1,357 real orders, 5,085
lines, 2026-05-10 → 2026-08-10, carrying `lw_qty_picked` (what was actually picked)
alongside `lw_qty_ordered`. 4,151 lines have pick data; 193 disagree (4.65%).

**Finding 1 — small lines are the cleanest lines, not the dirtiest.**

| Line shape | Lines | Mismatch |
|---|---|---|
| whole carton(s), qty % 6 = 0 | 2,102 | **6.52%** |
| part carton, qty < 6 | 1,884 | **2.65%** |
| broken multiple, qty > 6 not % 6 | 165 | 3.64% |

**Finding 2 — the mismatches are stock-outs, not miscounts.** 192 of 193 are short
picks, 1 is over. Mean ordered 9.8 → mean picked 2.5, delta −7.25. A counting error
is ±1 and symmetric; −7.25 is "it wasn't there".

**Finding 3 — order breadth and order size both raise the miss rate, and neither
explains the other away.** Per-line mismatch %:

| units in order | 1–2 lines | 3–4 lines | 5+ lines |
|---|---|---|---|
| <12 | 0.53% | 1.51% | 3.23% |
| 12–23 | 2.07% | 2.34% | 3.92% |
| 24–47 | 4.17% | 4.87% | 6.64% |
| 48+ | 7.81% | 3.75% | 7.90% |

Since every miss is a shortage, both effects run through availability: more distinct
SKUs means more draws against a possibly-empty bin.

**What this data cannot show, and is not claimed:** picking *time*, and wrong-flavour
picks that shipped. The mirror has no timestamps and no item-level audit. The
handling cost of breaking a carton is real and remains unmeasured.

**Finding 4 — a whole-carton total is nearly free.**

| | |
|---|---|
| Orders containing tea | 1,052 |
| Already total a whole number of cartons | **67.0%** |
| Mean shortfall to the next carton | **1.08 bottles** |
| Tea-unit uplift if every order were rounded up | **+4.09%** |

### The rule (approved by Tom, 2026-08-10)

1. **No per-flavour minimum.** The data does not support one and it costs sales.
2. **Total tea bottles in an order must be a multiple of 6.** Mixed flavours in a
   carton are allowed — Tom confirmed the shipper takes mixed types. Two thirds of
   orders already comply; the rest are asked for 1–2 more bottles of a flavour they
   choose. In exchange no loose bottle leaves the factory and no opened carton goes
   back on the shelf.
3. **Nudge on breadth, never block it.** A live carton meter — "עוד 2 בקבוקים
   להשלמת ארגז" — offering completion from the flavours this customer already buys.
   Honest, because the constraint is real, and worth roughly +4% on tea units.
4. **Value floor ₪944 incl. VAT** — the same floor the WhatsApp engine already
   enforces as `BELOW_MINIMUM`. Not a second number.
5. **Everything else follows `items.case_pack`** — already correct in the DB: teas 6,
   powders 1, MATCHA 18G 22. No constraint where `case_pack` is 1.

The carton rule applies to `product_group in ('GT Extracts 1L','GT Extracts 500ml')`
— the two groups that share the 6-bottle shipper.

## Availability — the highest-value part, and it was not in the brief

100% of the measured order failures are shortages. **So the page sells only what is
sellable.** `shopify_available_reconcile` already keeps Shopify `available` equal to
`on_hand − committed` every 5 minutes from our own truth, so the page reads a number
that is already correct.

An out-of-stock flavour is shown as unavailable with its next date, not silently
accepted and apologised for after picking. This converts a 4.65% post-pick shortage
into a pre-sale conversation. No composition rule can achieve that.

Zero-clamp semantics are unchanged and Tom-locked: `available` is the sellable count;
oversell surfaces as an exception, never on the storefront.

## Page

One page, RTL Hebrew, mobile-first — the buyer is a café owner on a phone.
Built from the same catalog the mobile pricelist prints, so the two cannot drift.

- Hero: what GT is, in one line.
- Catalog by group: תמציות תה (1 ליטר / 500 מ״ל side by side per flavour) · מאצ׳ה
  ואבקות · מחיות פרי · מוצרים משלימים.
- Per row: photo, name, size, list price ex-VAT, quantity stepper, availability.
- Sticky cart: units, carton meter, order total ex-VAT, minimum-order state.
- Checkout: business name, ח.פ, ordering contact, bookkeeping email, delivery
  address, delivery-day note. Existing customer types the same details; the human
  step matches them to the Shopify customer.
- Confirmation: "קיבלנו. נעבור על ההזמנה ונשלח לינק לתשלום" — never "your order is
  confirmed", because it is not until a human says so.

The ח.פ check digit is validated before submit — the same validation the
`customer-setup-shopify-gi` skill already performs.

## Domain and hosting

`pricelist.gteveryday.com` is **already printed on the pricelist cover and back
page** and has **no A record today** — the link in a document being sent to
customers is dead right now.

`gteveryday.com` resolves to Shopify (23.227.38.65) and `www` is a CNAME to
`shops.myshopify.com`, so the apex is Shopify's and the subdomain is free to point
elsewhere. One CNAME at the registrar sends `pricelist` to the app host.

Two steps, in this order:
1. **Today:** point the subdomain at a static page carrying the current pricelist,
   so the printed link works.
2. **Later:** the same hostname becomes the order page. No reprint, no second URL.

## Out of scope for v1 — say it out loud

Auto-sending the payment link · payment reminders · refunds and cancellations
(a human handles them in Shopify) · customer login / order history · shipping-cost
calculation · a second catalog source of truth.

## Prerequisites

- `items.case_pack` is null on 17 active sellable items (ODK 1L smoothies, Elita
  Margarita 0.3L, 3.85L sangria, MATCHA 30G, and the tools). **Not blocking** — the
  rule constrains only the two tea groups, and everything else defaults to a step of
  1. `lexicon.json` already records ODK carton = 6, so those three are evidenced
  when someone wants to close the gap.

## Tests

- Carton rule: total tea % 6, mixed flavours, the boundary at exactly 6 and at 0.
- Floor: ₪944 tax-inclusive, unpriced lines, the interaction of floor and carton.
- Every submitted line reaches the draft as a real line item — the `placeCartLines`
  invariant, exercised from the web path.
- Double-submit produces one draft (the `claimSession` CAS, from the web path).
- An unavailable SKU cannot be added, and cannot survive a stale page.
- Draft total = displayed total ±₪0.05, and never ×1.18.
- ח.פ check digit accepts real numbers and rejects transposed ones.

## Roles and the approval screen — decided 2026-08-10

Tom: stand it up first, sort fine-grained permissions later. Admin is Tom; everyone
else on the commercial side wears the sales hat; operations keeps what it has.

The portal has four roles today (`admin`, `planner`, `operator`, `viewer`). **One new
role: `sales`.** No other role changes. Operations routes are untouched.

| Role | Web orders |
|---|---|
| `admin` (Tom) | everything |
| `sales` | see the queue, correct prices, release the payment link |
| `planner` / `operator` / `viewer` | no access to the queue; the resulting order appears in the normal pipeline as any order does |

**The approval screen is a portal route — `/sales/web-orders` — not Shopify admin.**
That is the whole point of it: the screen shows, per line, what this customer last
actually paid (`order-intake/engine/pricing.ts`, discount-aware, with same-tier
sibling inference) and applies it in one tap. In Shopify admin a human would have to
open order history by hand for every line, which is exactly the error the manual step
exists to prevent.

`/sales/*` becomes a new route group — the first-level sales / operations split Tom
asked for. English UI, per the portal standard; only the public page is Hebrew.

## New customers — decided 2026-08-10

A brand-new business may order without anyone at GT having spoken to them first. They
pay list price by definition, so there is nothing to correct.

**After payment everything is automatic**: the draft becomes a real paid order,
Shopify commits the stock through its own pipeline, and the Green Invoice app issues
the חשבונית מס/קבלה. No human touches it again. The page only ever sells what the
reconciler says is available, so a new customer cannot buy what is not there.

**Before payment, a human still releases the link in v1 — one tap, seconds.** Not
caution for its own sake; there is a specific legal unknown behind it:

> An invoice at or above **₪5,000 ex-VAT** requires a Tax Authority allocation number
> (מספר הקצאה), or the buyer cannot deduct the VAT. Whether the Green Invoice Shopify
> app fetches that number automatically is **recorded as unverified** in the
> predecessor design and has not been checked since. Auto-releasing links would let an
> over-threshold order pay before anyone confirms it.

Auto-release is phase 2 and is unblocked by exactly four things, all already specified
in the predecessor design: the `orders/paid` → session correlation token (C1), link
idempotency (C2), the ₪5,000 gate computed ex-VAT (C3, C4) — and verifying the
allocation-number behaviour. When those land, the hybrid gate can auto-release the
common case (new customer, list price, under threshold, everything priced and in
stock) and keep the rest human.

## Hosting — decided 2026-08-10

**Same Vercel account as the portal, two projects.**

- **Public page** — its own Vercel project on `pricelist.gteveryday.com`. No auth, no
  portal bundle, no session cookie on a public marketing surface. It can go live as
  the static pricelist today and grow into the order page without changing hostname.
- **Approval screen** — inside the existing portal app, behind portal auth.

One account keeps billing and access in one place; two projects keep a public
unauthenticated surface from sharing a deployment with the authenticated portal.

## Open decisions for Tom

1. DNS — GoDaddy holds `gteveryday.com` (`ns27/ns28.domaincontrol.com`). One CNAME
   `pricelist` → `cname.vercel-dns.com`. **Tom's task; a reminder now runs each
   weekday morning and stops itself once the record resolves.**
2. *(closed 2026-08-10 — roles and approval screen, above)*
3. *(closed 2026-08-10 — new customers, above)*
4. *(closed 2026-08-10 — hosting, above)*
5. Hebrew copy register entry for the public page — drafted with the build, Tom
   approves the wording.
6. `items.case_pack` for the 17 items missing it — batched separately, not on this
   rule's path.
