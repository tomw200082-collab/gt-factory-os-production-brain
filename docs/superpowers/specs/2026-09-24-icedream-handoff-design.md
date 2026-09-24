# Design — Ice Dream handoff: customer book, price book, distributor package

> **Status:** DRAFT — awaiting Tom's review. Not authority until approved.
> **Date:** 2026-09-24 · **Branch:** `claude/shopify-customer-identifier-cwm1j1`
> **Decisions in this spec:** Tom, in session, 2026-09-24 (approach + all three design sections approved).
> **Governance note:** this design introduces a customer-specific price list. That changes
> `docs/decisions/modules/sales-declaration.md` Amendment A.4 ("No customer-specific price list is
> modeled in v1"). Tom approved the change in session on 2026-09-24; the amendment text is part of the
> build (§11), and Tom remains the sole approver of it.

---

## 1. Purpose and definition of success

GT is moving almost all of its business customers to a distributor, **Ice Dream (אייס דרים)**. Ice Dream
buys from GT, picks, delivers, and **issues the invoice to the customer at GT's prices**. Orders keep
arriving through GT. Ice Dream's team is not technical ("a bit old-fashioned" — Tom).

**Success, as one testable sentence:** Ice Dream loads every transferred customer into its own system
and serves them — right address, right contact, right price on every product — without asking GT a
single question, and every later change reaches them in the next weekly update.

This spec covers **sub-project A** only: the customer book, the price book, and the package handed to
Ice Dream. **Sub-project B** — a simple order page where each customer logs in and sees their own
prices — gets its own spec later and reads the same price book (§12).

## 2. Evidence base

Verified live on 2026-09-24 unless stated otherwise. Numbers are dated snapshots, not standing facts.

### 2.1 Identity

- Every Shopify customer has a unique ID (`gid://shopify/Customer/<n>`): 5,492 of 5,492.
- ח.פ (`custom.id_nomber`) is **not** unique — 44 numbers are shared by several customers (up to 18):
  chain branches under one company. ∴ one row = one branch, keyed by Shopify customer ID.
- `custom.client_key` = the Green Invoice client ID (UUID). All 584 active customers carry one; 583
  resolve in Green Invoice and one is malformed.
- Green Invoice `accountingKey` is filled but mixed in format (409 six-digit, the rest 7–8 digits or
  letter-prefixed) — unusable as a short, human customer number.

### 2.2 Scope

- **584 business customers** ordered between 2025-09-24 and 2026-09-24. This is the handoff population.

### 2.3 Prices

Source: one Shopify bulk export, orders created from 2024-09-23 (7,045 orders, 25,449 lines).

- **Shopify line prices are before VAT.** On 5 September orders with a matching Green Invoice tax
  invoice, every line price was identical and Green Invoice added 18% VAT on top. Shopify's
  `taxesIncluded=true` setting is misleading (already documented in `Sales-Machine/recipes/sales-report.md`).
- **58% of lines carry a discount allocation** (14,743 of 25,449). The customer's price is therefore the
  unit price **after all discounts** (`discountedUnitPriceAfterAllDiscountsSet`), never the line's list price.
- **Tea family rule holds for 95% of customers.** 1L teas: 455 customers, 24 paid different prices across
  flavors in the last 12 months. 0.5L teas: 175 customers, 6 conflicts.
- **75% of tea customers pay below list.** 1L family price vs ₪65 list: 115 equal, 339 below, 1 above.
- **Declared price fields are unreliable.** `custom.price_list` (178 spellings, e.g. `65-10%`, `61`,
  `65.33`) matches the price actually paid for 202 of 455 tea customers (77 mismatch, 94 unparseable,
  82 empty). Pricing tags (`wh65`, `wh65off10`, `10off`, `52-26`) match 8 times out of 82.
- Per (active customer × product) pairs: 5,024. Versus list price: 1,506 equal, 3,155 below, 13 above,
  350 on SKUs no longer in the catalog. 315 pairs changed price within the last 12 months. 524 lines
  had a zero price (samples / free goods).
- Shopify plan is **Grow**: no B2B companies, no price lists. Per-customer prices cannot live in Shopify.
- `order_bot.price_book` exists (50 rows, 7 customers, 2026-06-21/22, no references in `gt-factory-os`
  code). It is superseded by this design and left untouched.

### 2.4 Customer data coverage (584 active customers)

| Field | Coverage | Source |
|---|---|---|
| ח.פ valid (check digit) | 583 | Shopify metafield + Green Invoice |
| ח.פ equal in Green Invoice and Shopify | 571 (12 to reconcile) | both |
| Accounting email | 455 (129 missing) | Green Invoice `emails` |
| Payment terms code | 583 | Green Invoice `paymentTerms` |
| Street address | 574 | Shopify default address |
| House number present | 491 (93 to check) | Shopify default address |
| Business type | 507 | Shopify `custom.client_type` |
| Receiving hours | **none** | LionWheel `earliest`/`latest` empty on 40 of 40 sampled tasks |
| Open balance with GT | 44 customers | Green Invoice `balanceAmount` |

Green Invoice payment-term codes across the 583: `30`→240, `-1`→174, `45`→60, `0`→57, `10`→19,
`15`→19, `60`→13, `90`→1. **The meaning of `-1` is not yet verified** (§8, item 5).

### 2.5 What Ice Dream collects (Dana, Ice Dream project manager, relayed by Alex 2026-09-24)

- Place name, address, ח.פ / עוסק מורשה, contacts.
- For credit terms (שוטף): owner's full name, ID number + copy, private address — **collected by Dana by phone**.
- Kashrut of the customer: not kosher / rabbinate / Badatz.
- They deliver all day with no restrictions.
- Payment: credit card or bank transfer; שוטף 30 only with signed forms; first order paid in advance.

GT products: "all products are kosher Badatz Beit Yosef, under Holon Rabbinate supervision"
(`Sales-Machine/knowledge/claims/public-claims.yaml#kashrut_badatz`, Tom-confirmed 2026-08-31).
No certificate document exists (`Sales-Machine/CURRENT_STATE.md` U-020).

## 3. Decisions (Tom, 2026-09-24)

1. Ice Dream buys and invoices the customer at GT's prices; orders mostly arrive through GT.
2. **Tea extracts 1L and 0.5L have one fixed price per customer per size**, across all flavors.
3. **A brand-new customer pays full list price** by default.
4. One price book in GT's database is the single price truth. The Ice Dream package, the future order
   page and GT's own order entry all read it.
5. From go-live the book decides the price; the last price paid is only how the book is first filled.
6. Scope, customer-book fields, package format, checks and update rhythm as in §§4–9.

## 4. Architecture

```
Shopify (orders, customers) ─┐
Green Invoice (clients, invoices) ─┼─► build scripts ─► sales_core.customer_book
LionWheel (delivery notes)  ─┤                    ─► sales_core.customer_price (append-only)
catalog-truth + price TSV   ─┘                    ─► sales_core.list_price
customer form (Google Sheet) ──────────────────►        │
                                                         ▼
                                          sales_core.v_customer_price  (resolved, complete matrix)
                                                         │
                     ┌───────────────────────────────────┼─────────────────────────┐
                     ▼                                   ▼                         ▼
          Ice Dream package (Excel + PDF)      weekly update file        order page (sub-project B)
```

- **Database:** new tables in the module-owned `sales_core` schema (migrations + pgTAP in
  `gt-factory-os/db/`). No factory core table is read or written by the new code except through
  existing curated views.
- **Scripts:** `gt-factory-os/scripts/distributor-handoff/` (pattern: `scripts/sales-report/`). Raw pulls are
  saved once per run and never re-fetched mid-run.
- **Outputs** (customer data + prices) go to a private Google Drive folder. **Never committed to git.**

## 5. The price book

### 5.1 Tables

- `sales_core.list_price` — one row per product GT sells: `sku` (PK), Hebrew name as on the label, size,
  `family` (`TEA_1L`, `TEA_05L` or null), barcode, `price_ex_vat`, `active`, source, verified date.
  Seeded from `docs/warehouses/catalog-truth.md` + `docs/pricing/2026-08-05_shopify_products_exvat.tsv`;
  barcodes from Shopify variants.
- `sales_core.customer_price` — **append-only** (trigger, like `lead_event`): `shopify_customer_id`,
  `price_key` (a SKU or a family code), `price_ex_vat`, `basis`, `evidence` (order name + date, or the
  decision note), `effective_from`, `recorded_by`. The current price is the latest row per
  (customer, price_key). History answers "which price applied on date X".
- `sales_core.v_customer_price` — for every customer in the book × every active `list_price` SKU:
  customer SKU row → customer family row → list price. Returns `price_ex_vat`, `price_inc_vat`
  (×1.18, rounded to agorot) and a basis label. **Never returns a null price.**

### 5.2 Seeding rules (first fill only)

Applied in order; the first that applies wins.

1. **Tea family** (`TEA_1L` = the 11 GT tea SKUs ending `-1L` in catalog-truth's tea table; `TEA_05L` = the
   same 11 flavors in 0.5L): the net unit price of the customer's most recent purchase of any SKU in the
   family. Private-label SKUs (e.g. `GT-ELT-STR-0.5L`) are not in a family. 0.3L teas are priced per SKU.
   For family SKUs seeding writes only the family row, never a per-SKU row; a per-SKU row for a tea
   flavor can exist only as an explicit Tom decision.
2. **Per SKU:** the net unit price (after all discounts) of the customer's most recent purchase of that SKU.
   Excluded: cancelled and test orders, zero-price lines.
3. **Discontinued SKUs** carry to their current equivalent only through the existing map
   (Maruei / Kogamo / XP matcha → Shizuoka, as in `shopify-draft-order-from-po/scripts/lookup.mjs`);
   the row is flagged. Other SKUs no longer sold are not carried.
4. **No history** (new customer, or a product the customer never bought): list price. No row is written;
   the view falls through to `list_price`.

### 5.3 Exceptions (the only rows Tom reviews)

| Code | Rule | Expected volume |
|---|---|---|
| E1 | Customer paid different prices across flavors of one tea family in the last 12 months | 30 (24 + 6) |
| E2 | Last price is ≥10% below the previous price for the same price key — the SKU, or for tea the size family — within 12 months (possible one-off) | computed at build |
| E3 | Customer price above list price | 13 pairs |
| E4 | Branches with the same ח.פ pay different prices for the same SKU or family | computed at build |
| E5 | Book price ≠ the line price on the customer's latest Green Invoice tax invoice (gate G1) | computed at build |

Each exception gets a proposed price. Tom's decision is written as a new `customer_price` row with
`basis = tom_decision`, so the decision itself is on record.

### 5.4 After go-live

A price changes only by a new append-only row with an approver. The last-paid rule stops being the
source of truth; `shopify-draft-order-from-po` and the WhatsApp order bot move to reading
`v_customer_price` as follow-ups (§13).

## 6. The customer book

`sales_core.customer_book` — one row per branch (Shopify customer), for the 584 active customers.
Each field stores its value and its source; a field filled by the customer form or by Doreen is never
overwritten by a later rebuild.

| Group | Fields | Source (first wins) |
|---|---|---|
| Identity | GT customer number (4 digits; first build assigns them sorted region → city → name, later customers get the next free number, a number is never reused), place name as on the sign, legal name, ח.פ / עוסק מורשה, chain, business type | GT number: assigned by build · legal name, ח.פ: Green Invoice · place name: Shopify · chain, type: Shopify `client_type` + chain tags |
| Invoicing | legal name, ח.פ, invoice address, accounting email, current GT payment terms (in words) | Green Invoice → form |
| Delivery | street, house number, city, floor / delivery notes, region, delivery days | Shopify default address → LionWheel notes → form · region/days: `zones.json` + `route_calendar.json` |
| On site | contact name and phone, receiving restrictions if any (optional — Ice Dream delivers all day) | form → LionWheel recipient → Green Invoice `contactPerson`/`phone` |
| Kashrut | not kosher / rabbinate / Badatz | form |
| For planning | last order date, average orders per month (last 6 months) | Shopify orders |

Not included: ordering contacts (orders come through GT), open balances (the 44 debts stay with GT),
owner ID data (Ice Dream collects it by phone for its own credit forms).

**Required for handoff:** place name, legal name, valid ח.פ, invoice address, accounting email,
street + house number + city, region, on-site contact + phone, kashrut, price resolution (§5).
Receiving restrictions are optional.

### 6.1 Closing the gaps — one contact per customer

- One message to every customer: from date X invoices come from Ice Dream, prices unchanged, Dana from
  Ice Dream may call about payment terms. It links to a 30-second Google Form: on-site contact,
  kashrut, address confirmation, accounting email, receiving restrictions (optional).
- Tom approves the text and the send. It is sent **by a person** (Doreen or Alex) from GT's WhatsApp, not
  by automation, so `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` stays `false`.
- Form answers land in a Google Sheet; the build imports them with source `form`.
- After 3 business days Doreen calls only the customers who did not answer or whose answers conflict.

## 7. The package for Ice Dream

Hebrew, right-to-left, large font, no abbreviations, no formulas, no hidden cells. Each version carries
a version number and date on every page.

1. **Excel workbook — 5 tabs**
   - `קרא אותי` — one page: prices are before VAT and a with-VAT column is given · the tea rule ·
     "a product not listed for a customer = general price list" · kashrut of GT products · the switch
     date · who at GT to call about what.
   - `לקוחות` — one row per branch, grouped headers: זיהוי · חשבונית · משלוח · בסניף · כשרות.
   - `מחירים מיוחדים ללקוח` — one row per customer × product whose price differs from the list. Each tea
     flavor is its own row: nothing to interpret. (Base list + per-customer special prices is the
     structure every invoicing system uses.)
   - `מחירון כללי` — every product: barcode, SKU, name as on the label, size, price before and with VAT.
   - `ימי חלוקה` — city → region → delivery days.
2. **Printed binder (PDF)** — one A4 page per customer, sorted region → city → name: delivery box,
   invoicing box, their special prices, and the line "כל שאר המוצרים — לפי המחירון הכללי".
   Plus a product catalog with photos (11 tea flavors share similar bottles; a photo prevents picking
   errors).
3. **CSV copies** of the three data tabs (UTF-8 with BOM), for importing once Ice Dream's system is known.

## 8. Checks (gates) — nothing leaves GT until all pass

1. **G1 — invoice match.** For every active customer, every line on their latest Green Invoice tax invoice
   (barcode → SKU) equals `v_customer_price`. Target 100%; each miss becomes E5 and is resolved.
2. **G2 — completeness.** `v_customer_price` resolves a price for every customer × active SKU; every
   required customer-book field is filled.
3. **G3 — exceptions closed.** Every E1–E5 row has a recorded decision.
4. **G4 — package integrity.** Every customer appears exactly once in the Excel and once in the PDF;
   counts equal the database; 3 random customers per region are checked by hand, field by field,
   against Shopify and Green Invoice — 3/3 or stop.
5. **Payment-term wording.** Each Green Invoice code is printed in words only after its meaning is
   confirmed from real invoices (document date vs due date). `-1` (174 customers) is unresolved until then.

## 9. Handoff and updates

- **Region by region, center first.** Tom or Doreen sits with Ice Dream's clerk for the first
  10 customers of the center region. Every point where the clerk stops to ask becomes a fix in the package
  before the rest ships. Then north, then south — each region only when all its customers pass G2.
- **Weekly update** every Sunday morning, same format: only what changed, a "היה ← עכשיו" column,
  and reprinted binder pages for changed customers. A new customer placing a first order gets an
  update the same day.
- Tom sends the package (external send).

## 10. Go-live conditions outside this spec

Tracked as separate items; none is built here.

- Stop Green Invoice's automatic invoice for Ice Dream customers from the switch date — otherwise the
  customer gets two invoices.
- How an order travels from GT to Ice Dream.
- Stock held at Ice Dream: GT's or theirs (the ledger has no locations in v1).
- Confidentiality and data-processing terms in the Ice Dream agreement.
- Payment terms for existing customers: Ice Dream offers card/transfer, שוטף 30 with signed forms, first
  order prepaid; 314 GT customers have 30+ days today (74 of them more than 30).
- Kashrut certificate: none exists as a document (U-020); Badatz customers may ask for it.

## 11. Governance

- **Sales declaration A.4** is amended: a customer-specific price list is now modeled, in
  `sales_core`, as the single price truth. Text drafted in the build; Tom approves it.
- The tea-family rule and the new-customer rule are recorded in `Sales-Machine/doctrine/decisions.md`
  with Tom's words and today's date.
- Migrations follow the gt-factory-os migration rules (list `db/migrations/` before and after writing,
  pgTAP per migration). No stock-ledger or projection object is touched.
- Customer data and prices never enter git; the Drive folder is private.

## 12. Sub-project B — order page (not in this spec)

A simple, good-looking order page where each customer logs in and sees their own prices. It is a new
customer-facing surface: it needs its own spec, Tom's approval and the portal/sales governance
(sales-declaration A.3). It reads `v_customer_price`; nothing in this spec has to be rebuilt for it.

## 13. Follow-ups after go-live

- `shopify-draft-order-from-po` reads `v_customer_price` instead of computing last-paid.
- The WhatsApp order bot reads `v_customer_price`; `order_bot.price_book` is retired by its owner.
- `customer-setup-shopify-gi` writes a new customer into the customer book (list price by default).

## 14. Open items

| Item | Resolved by | Before |
|---|---|---|
| Ice Dream's invoicing software | Tom | CSV column mapping (the Excel does not depend on it) |
| Meaning of Green Invoice payment-term `-1` | build, from invoice due dates | G4 |
| Access to LionWheel delivery history (only open tasks inspected) | build, live inspection | customer-book seeding |
| Switch date | Tom | the customer message |
