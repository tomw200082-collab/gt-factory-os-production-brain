# Customer & Product Tracker — method

Recipe for recomputing the customer/product tracker. Dated snapshots in this
directory are evidence as of their date; they are never edited after the fact.
Live numbers must always be recomputed from source, never quoted from an old
snapshot as current.

- Snapshot: `customer-product-tracker-<YYYY-MM-DD>.json`
- Excel: `customer-product-tracker-<YYYY-MM-DD>.xlsx`
- Artifact: <https://claude.ai/code/artifact/f7c03c2f-81d1-47a8-b90f-9656bec58ab7>
  (one page, republished in place — the URL never changes)

Snapshots to date: `2026-08-06`, `2026-08-25`.

## Rebuild verification (do this every time)

A rebuild is only trustworthy if it can reproduce the previous snapshot from the
same source. Run the pipeline at the previous `as_of` first and diff:

| Check | 2026-08-25 rebuild vs the 2026-08-06 snapshot |
|---|---|
| Monthly net revenue | identical to the agora for 17 of 20 months |
| `2025-07`, `2025-08` | +40, +750 — invoices back-dated into those months since |
| `2026-06`, `2026-07` | −2,804, −32,204 — credit notes issued against them since |
| Customer status | 554 / 560 identical; all 6 differ only where `days` or `med` moved on new data |
| `exceptions.april_gap` | identical (269,006 / 138,604 / 130,402) |

Anything that differs and is *not* explained by new documents is a pipeline bug,
not a data change.

## Sources

| Domain | Source | Notes |
|---|---|---|
| Revenue | Green Invoice (Morning) | Source of truth. Includes manual invoices that never went through Shopify. |
| Order detail, channel, customer | Shopify | Cross-check only. Not the revenue total. |
| Items, families, SKU map | Postgres `private_core` | Read-only. |

Client code already solving auth/token refresh:
`gt-factory-os/api/src/integrations/greeninvoice/client.ts`.

## Customer notes — living memory (read this BEFORE rebuilding)

`Sales-Machine/knowledge/accounts/customer-notes.yaml` is the tracker's memory
between rebuilds: identity decisions, closed businesses, churn reasons, ops
notes. Append-only; every entry carries key, date, by, grade.

The loop:

1. **Rebuild reads the file first.** Identity answers (tag `identity`) decide
   merges/splits before customer grouping; `closed` suppresses rescue-call
   moves; everything else is context. Apply judgment — the notes are input,
   not decoration.
2. **Every note is baked into the payload** (`notes` map, keyed `tax:<ח.פ>` /
   `nm:<name>` / `prod:<product name>`) and rendered on the customer/product
   card, with a dot on radar rows.
3. **Tom writes new notes in the dashboard.** They persist in the device's
   localStorage and queue behind the cloud chip in the top bar. The sync panel
   produces a paste-ready block (or a downloadable file via the artifact
   `downloads` capability); any Claude session appends it to the YAML —
   append-only, `grade: user_confirmed`, bump `updated:` — then rebuilds.
4. On the next load the page auto-clears pending entries that now exist in the
   baked payload (matched by key + text hash).

Never edit or delete existing entries; corrections are newer entries.

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

Counted over 2025-01-01 -> 2026-08-25 (10,909 documents, every monthly window
asserted `got == total`):

| type | Meaning | Docs | Revenue? |
|---|---|---:|---|
| 10 | הצעת מחיר | 1 | No — quote |
| 200 | תעודת החזרה | 57 | No — logistics doc |
| 210 | ביטול תעודת משלוח | 22 | No — logistics doc |
| 305 | חשבונית מס | 6,201 | **Yes, positive** |
| 320 | חשבונית מס/קבלה | 9 | **Yes, positive** |
| 330 | חשבונית זיכוי | 958 | **Yes, negative** |
| 400 | קבלה | 3,661 | No — payment, would double-count |

**Net revenue = Σ(305 + 320) − Σ(330).**

### Why status is not used to filter cancellations

`status = 4` means "fully credited", not a separate cancellation state. Re-verified
on the 2026-08-25 window: 412 invoices carry `status = 4`, and every one of them is
fully offset by credit notes — 404 by a single full-value note, the other 8 by two
or more partial notes against the same invoice. Residual across all 412, after
netting, is 122 over 20 months and 8.38M of revenue (0.001%).

Subtracting type 330 therefore nets these to zero on its own, and also handles the
457 *partial* credits whose source invoices stay at status 0/1/2. Filtering on
status in addition would double-subtract.

Credit notes link to their source via `remarks`
(`חשבונית זיכוי עבור חשבונית מס <number>`); 95 of 958 carry no parseable reference.
They still subtract correctly by amount and by customer — only the per-invoice
attribution is lost. Reported on the page under חריגים.

## Normalization traps

- **Barcodes**: the same product appears with and without a leading zero
  (`693493238205` / `0693493238205`). Strip non-digits, then strip leading zeros,
  or one product splits into two rows.
- **Currency**: three USD invoices exist (2026-03-08, 2026-04-15, 2026-08-11).
  Multiply by `currencyRate` for ILS.
- **Shipping**: barely invoiced (₪830 over 20 months, 2 lines). Excluded by
  description to honour the "מחזור excludes shipping" definition.
- **Product families are classified from the invoice description**, because the
  Green Invoice `catalogNum` is a barcode and does not join to `items.sku`. The
  classifier must match Hebrew descriptions, not just English: matcha is sold as
  `Maruei טקסית, שקית אלומיניום 500 גרם` and `Shizuoka טקסית…`, and DESERTEA
  ships as `Desert Infusion 1000ml`. Matching only on the English family names
  stranded ₪354K in an "אחר" bucket, ₪202K of it matcha. Non-product lines
  (`התחשבנות`, `שירותי צילום`, `עלות מיקסר`) are classified separately rather
  than counted as products. Classification regroups revenue only — it never
  changes any total.
- **VAT**: never multiply or divide by 1.18 to reconcile the two systems.
  Shopify `net_sales` and Green Invoice `amountExcludeVat` are both already
  net of VAT.

## Products — basis (changed 2026-08-25)

Product rows are computed from **Green Invoice invoice lines**: grouped by the
normalized barcode (`catalogNum`, non-digits stripped, then leading zeros; a value
outside 6-14 digits is a concatenation artifact and falls back to the normalized
description), summed net of credit notes, quantities signed the same way. The
display name is the highest-revenue Latin-script description for that barcode, so
the Hebrew, English and parenthesised spellings of one product collapse into one row.

This means the product table now **ties to the headline revenue**. The 2026-08-06
product table did not: its figures reconcile to neither Green Invoice nor Shopify
(DETOX 1000ml: 616,317 / 21,259 units there, against 666,883 / 13,206 from the
Green Invoice lines and 578,620 from Shopify `net_sales` over the same window).
Product revenue and quantity therefore move between the two snapshots. Nothing else
in the payload is affected — customer and revenue figures reproduce exactly.

## Opportunities — peer definition

A customer's peers are the customers whose trailing-365-day revenue is within
**0.5x to 2x of theirs**. A family becomes a gap when at least 8 peers exist, over
40% of them buy that family, and the estimate clears 500. The estimate is the
customer's own 12-month revenue times the **median share of wallet** that family
takes among the peers who buy it.

Peer bands, not deciles or quartiles: a revenue quartile puts a matcha distributor
in the same bucket as a cafe chain and then projects the distributor's matcha share
onto the chain. Verified against the previous snapshot — the same customer/family
pair lands on peer_rate 86 and 12,949 where the 2026-08-06 snapshot recorded 84 and
13,165.

## Customer identity

**Read the Shopify side from `customer.displayName`, never `billingAddress.company`.**
The company field carries delivery instructions on some orders
(`לספק משלוח עד 17:30` on 16 of them, which then presents as an 11,840 "customer"),
and at least one record is stored double-escaped
(`נונומימי נס ציונה בעamp;quot;מ`), which silently breaks the name match and
files a real, matched customer under "no Green Invoice counterpart". Decode HTML
entities either way. `displayName` reproduces ShopifyQL `customer_name` exactly.

Grouped by `taxId` when present, else by normalized name. Normalization strips
`בע"מ`, `(ח.פ …)`, quote variants, and punctuation. Shopify↔Green Invoice matching
also tries every parenthetical part and the name with the parentheses stripped,
in either order — Shopify writes `Mamie (לאט לאט מהר מהר בע"מ)` where Green Invoice
writes `(לאט לאט מהר מהר בע"מ) Mamie`. Matching only the trailing half left 49
customers falsely unmatched; matching parts in either order brings that to 26.

**Matches below full certainty are not merged.** A wrong merge hides real churn
behind another customer's orders. Ambiguous pairs go to the exceptions list for
Tom to decide.

## Definitions (locked)

| Term | Definition |
|---|---|
| Customer base | Anyone with at least one order in the trailing 365 days. Every count, rate and total on the page uses this set |
| Order day | The date of an **invoice** (305/320). A credit note is not an order — counting one shortens the median interval and manufactures fake churn |
| מחזור 12ח׳ | Trailing 365 days from `as_of` |
| Monthly sparkline | The last 12 **calendar** months (`m12`) — a slightly different window from `rev12` by design |
| רבעון מול רבעון | Rolling 90-day windows: `r3` = (`as_of`−90, `as_of`], `p3` = (`as_of`−180, `as_of`−90] |
| מרווח טיפוסי | Median of day-gaps between consecutive order days, last 12 months |
| פעיל | Ordered within 1.5× their own typical interval |
| בסכנה | 1.5–3× |
| נטש | Over 3×, or over 120 days — whichever comes first |
| חדש | First order within the last 90 days |
| צומח / מתכווץ | Last 3 months vs the 3 before, change beyond ±20% |
| מחזור | Net revenue, excluding VAT and shipping |

Customers with fewer than 3 orders ever — or any customer whose interval cannot be
computed — have no reliable rhythm. They are classified `אין מספיק היסטוריה` and
never declared churned: missing a churn is cheaper than raising a false alarm.
`חדש` is decided first: a customer whose first-ever order is inside the last 90 days
is new, whatever the order count.

Churn is measured against each customer's **own** rhythm, never a flat day
threshold: a customer who orders weekly and has been silent 3 weeks is in more
trouble than one who orders quarterly and has been silent 5 weeks.

## Known divergence between sources — open

Over 20 months (2025-01-01 -> 2026-08-25) Green Invoice recorded 8,384,407 and
Shopify 7,353,951 — a 1,030,455 (14.0%) gap. The steady month-to-month portion
(12-15%) is manual invoices that never went through the website, and it has a face:
`Med Cuisine (EU/UK) LTD`, 45,187 over 12 months in Green Invoice with zero Shopify
orders, is an export account billed by hand. That part is expected, not a defect.

**April 2026 still does not fit that pattern, and is still unreconciled.** Shopify
booked 269,006 of returns against 138,604 of Green Invoice credit notes — roughly
130,402 unexplained. Shopify gross sales for April were normal (476,479, against
481,820 in February and 466,169 in May), so the collapse in April `net_sales` is
entirely the return spike. Reported as a finding; **not** reconciled in code.

**August 2026 looks like a second April, and is not.** Shopify shows 448,004 of
reversals — the largest month in the series. All of it is one event: on 2026-08-09
the 300ml order for `מימי ואזה חנויות` was invoiced three times (63891 for 270,000
and 63900 for 243,000, both credited in full the same day by 72397 and 72403; 63911
for 229,500 stands). Both systems describe the same correction. Net of it, August
is a record month: 668,008 through the 25th, above July's full 634,305.

The lesson for the next rebuild: a reversal spike is only a source divergence when
the two systems disagree about it. Compare Shopify `sales_reversals` against Green
Invoice type-330 totals for the *same date window* — comparing a full month of one
against a partial month of the other invents a 407,274 gap that does not exist.

## What is deliberately not merged

The identity questions live in `Sales-Machine/knowledge/accounts/customer-notes.yaml`
and surface on the page under חריגים. As of 2026-08-25: 26 Shopify customers with no
Green Invoice counterpart (10 of them אר.טו.אם branches that Green Invoice bills
through one central account), 19 ambiguous pairs, 16 Green Invoice customers with no
Shopify account, 95 credit notes with no parseable source-invoice reference, 8
customers with no phone number, and 122 customers too thin to judge for churn.

A wrong merge hides real churn behind another customer's orders. These stay open
until Tom decides.
