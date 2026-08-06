# Customer & Product Tracker — method

Recipe for recomputing the customer/product tracker. Dated snapshots in this
directory are evidence as of their date; they are never edited after the fact.
Live numbers must always be recomputed from source, never quoted from an old
snapshot as current.

- Snapshot: `customer-product-tracker-<YYYY-MM-DD>.json`
- Excel: `customer-product-tracker-<YYYY-MM-DD>.xlsx`
- Artifact: <https://claude.ai/code/artifact/f7c03c2f-81d1-47a8-b90f-9656bec58ab7>

## Sources

| Domain | Source | Notes |
|---|---|---|
| Revenue | Green Invoice (Morning) | Source of truth. Includes manual invoices that never went through Shopify. |
| Order detail, channel, customer | Shopify | Cross-check only. Not the revenue total. |
| Items, families, SKU map | Postgres `private_core` | Read-only. |

Client code already solving auth/token refresh:
`gt-factory-os/api/src/integrations/greeninvoice/client.ts`.

## Green Invoice extraction

`POST /v1/documents/search` with `{page, pageSize:100, fromDate, toDate, sort:'documentDate'}`.

Two API constraints that will silently truncate results if ignored:

1. **`page * pageSize` is capped at 10,000.** Beyond that the API returns
   `errorCode 1129`. Query month by month, and assert `got == total` per window.
2. `pageSize` above 100 was not exercised; 100 paginates reliably.

The response carries fields absent from the repo's Zod schema — notably
`amountExcludeVat`, `amountLocal`, `client.taxId`, `client.phone`, `discount`.
`amountExcludeVat` is Green Invoice's own net-of-VAT figure and was verified to
equal the sum of `income[].amount` on every financial document pulled.

## Document types — what counts as revenue

Counted over 2025-01-01 → 2026-08-06 (10,456 documents):

| type | Meaning | Docs | Revenue? |
|---|---|---:|---|
| 10 | הצעת מחיר | 1 | No — quote |
| 200 | תעודת החזרה | 44 | No — logistics doc |
| 210 | ביטול תעודת משלוח | 17 | No — logistics doc |
| 305 | חשבונית מס | 5,942 | **Yes, positive** |
| 320 | חשבונית מס/קבלה | 9 | **Yes, positive** |
| 330 | חשבונית זיכוי | 904 | **Yes, negative** |
| 400 | קבלה | 3,539 | No — payment, would double-count |

**Net revenue = Σ(305 + 320) − Σ(330).**

### Why status is not used to filter cancellations

Every `305` with `status = 4` (384 documents) is credited by a full-value credit
note, and exactly 384 credit notes are full-value cancellations — a 1:1 match with
zero exceptions. `status = 4` therefore means "fully credited", not a separate
cancellation state. Subtracting type 330 already nets these to zero, and also
handles the 399 *partial* credits whose source invoices stay at status 0/1/2.
Filtering on status in addition would double-subtract.

Credit notes link to their source via `remarks`
(`חשבונית זיכוי עבור חשבונית מס <number>`); 93 of 904 have no parseable
reference. They still subtract correctly by amount and by customer — only the
per-invoice attribution is lost. Logged as an exception.

## Normalization traps

- **Barcodes**: the same product appears with and without a leading zero
  (`693493238205` / `0693493238205`). Strip non-digits, then strip leading zeros,
  or one product splits into two rows.
- **Currency**: one USD invoice exists. Multiply by `currencyRate` for ILS.
- **Shipping**: barely invoiced (₪830 over 20 months, 2 lines). Excluded by
  description to honour the "מחזור excludes shipping" definition.
- **VAT**: never multiply or divide by 1.18 to reconcile the two systems.
  Shopify `net_sales` and Green Invoice `amountExcludeVat` are both already
  net of VAT.

## Customer identity

Grouped by `taxId` when present, else by normalized name. Normalization strips
`בע"מ`, `(ח.פ …)`, quote variants, and punctuation. Shopify↔Green Invoice matching
also tries each half of a `שם מסחרי (חברה בע״מ)` pair.

**Matches below full certainty are not merged.** A wrong merge hides real churn
behind another customer's orders. Ambiguous pairs go to the exceptions list for
Tom to decide.

## Definitions (locked)

| Term | Definition |
|---|---|
| מרווח טיפוסי | Median of day-gaps between consecutive order days, last 12 months |
| פעיל | Ordered within 1.5× their own typical interval |
| בסכנה | 1.5–3× |
| נטש | Over 3×, or over 120 days — whichever comes first |
| חדש | First order within the last 90 days |
| צומח / מתכווץ | Last 3 months vs the 3 before, change beyond ±20% |
| מחזור | Net revenue, excluding VAT and shipping |

Customers with fewer than 3 orders ever have no reliable interval. They are
classified `אין מספיק היסטוריה` and never declared churned — missing a churn is
cheaper than raising a false alarm.

Churn is measured against each customer's **own** rhythm, never a flat day
threshold: a customer who orders weekly and has been silent 3 weeks is in more
trouble than one who orders quarterly and has been silent 5 weeks.

## Known divergence between sources — open

Over 20 months Green Invoice recorded ₪7,900,911 and Shopify ₪6,909,257 — a
₪991,654 (14.4%) gap. The steady month-to-month portion (12–15%) is manual
invoices that never went through the website, which is expected.

**April 2026 does not fit that pattern.** Shopify booked ₪269,006 of returns
against ₪138,604 of Green Invoice credit notes — roughly ₪130,000 unexplained.
Shopify gross sales for April were normal (₪476,479, against ₪481,820 in February
and ₪466,169 in May), so the collapse in April `net_sales` is entirely the return
spike. This is reported as a finding and has **not** been reconciled in code.
