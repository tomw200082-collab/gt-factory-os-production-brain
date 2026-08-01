# Shopify — unmapped ACTIVE variants, triage evidence (2026-08-01)

> Read-only evidence pack. **No storefront change was made.** Decision is Tom's.
> Regenerate: `FROM sales SHOW gross_sales, orders GROUP BY product_variant_sku ORDER BY orders DESC LIMIT 250 SINCE -180d UNTIL today`
> plus the coverage query in `gt-factory-os/CLAUDE.md` §Shopify writes.

## Why this exists

The reconciler syncs the **53** sellable items that carry an approved+active
`integration_sku_map` shopify row. Shopify has **113 ACTIVE variants**. The other
~60 are not synced — nothing ours writes them, which is why they hold values our
zero-clamped formula could never produce (`GTMN-PIK-254` −2675, `GT-GLA-MAT-PRINT` −1400).

The initial read was "storefront junk, archive it". **That was wrong.** 180-day sales
show ~44 of them are actively selling, several among the top revenue lines in the shop.
Archiving on that assumption would have removed live products.

## The real pattern

The big unmapped sellers are the **Muzot / mixer line** (`GTCC-MUZ-*`, `GTMX-MUZ-*`) plus
merch/consumables (`GT-GLA-CUP`, `GTMN-PIK-254`, `AP-TAP-*`, `MM-DRI-CAN-*`).

Several of these are already mapped to `EXCLUDED-NONSTOCK` on the **lionwheel** channel
with `excluded_non_stock` / `excluded_legacy_bundle` — i.e. GT sells them but deliberately
does not stock-track them. That is a coherent business model, and it explains the deep
negatives: Shopify decrements on every sale and nothing ever replenishes.

∴ the question is **not** "archive or map". It is: **for each line, do we want stock tracking?**

## Decision menu (per SKU)

| If… | Do | Effect |
|---|---|---|
| We hold stock & want truth | add `integration_sku_map` row (shopify/approved/active) | joins the 5-min sync automatically, negative self-corrects next cycle |
| We sell it but don't stock-track (made-to-order, bundle, merch) | in Shopify set the variant to **not track inventory** | negatives stop accumulating & stop being meaningless; storefront unaffected |
| Genuinely retired | archive the Shopify product | leaves the ACTIVE set, disappears from this list |

## Selling but NOT synced — 180d, ordered by revenue

| SKU | ₪ gross 180d | orders | Shopify qty now |
|---|--:|--:|--:|
| `GTMX-MUZ-PRPL-1L` | 81,219 | 27 | 0 |
| `GTMX-MUZ-TRIL-1L` | 50,311 | 46 | 0 |
| `GTMX-MUZ-PNMM-1L` | 42,269 | 30 | 0 |
| `GTMX-MUZ-JASM-1L` | 35,608 | 11 | 0 |
| `GTCC-NM-SAN-3.85L` | 16,086 | 22 | −15 |
| `GTCC-MUZ-JAS-0.2L` | 13,725 | 52 | 0 |
| `GTCC-MUZ-PNMM-1L` | 11,799 | 46 | −653 |
| `GTCC-MUZ-NEG-0.2L` | 10,887 | 37 | 0 |
| `GTCC-MUZ-HER-0.2L` | 9,152 | 32 | 13 |
| `GTCC-MUZ-QUE-0.2L` | 8,780 | 27 | 4 |
| `GTCC-MUZ-SMAR-1L` | 6,047 | 30 | −16 |
| `GTCC-MUZ-APPZ-1L` | 5,146 | 22 | −10 |
| `GTCC-MUZ-PSSP-1L` | 4,805 | 17 | −19 |
| `GTCC-MUZ-PSC-0.2L` | 4,423 | 14 | 0 |
| `GTCC-MUZ-JASM-1L` | 4,181 | 23 | −96 |
| `GTMX-MUZ-HER-1L` | 3,925 | 22 | 0 |
| `GT-GLA-CUP` | 3,011 | 140 | −498 |
| `GTMX-MUZ-BZSM-1L` | 2,948 | 21 | 1 |
| `AP-TAP-MAN-3.4` | 2,712 | 7 | −4 |
| `GTCC-MUZ-CHRBL-1L` | 1,951 | 7 | −4 |
| `GTCC-MUZ-ANBL-1L` | 1,724 | 11 | −71 |
| `GTMX-MUZ-MRCL-1L` | 1,550 | 11 | 9 |
| `GTCC-MUZ-JASJ-1L` | 1,272 | 5 | 14 |
| `AP-TAP-PIN-3.4` | 1,142 | 3 | 0 |
| `GTCC-MUZ-TROJ-1L` | 9,574 | 20 | −261 |
| `MM-CAN-CLO-MACHI` | 4,274 | 1 | −23 |
| `GT-SHI-CER-50` | 551 | 1 | −10 |
| `AP-WHK-MAT` | 501 | 6 | −13 |
| `GTCC-JAS-JAZ-1L` | 373 | 1 | −424 |
| `GTCC-TRO-JAP-1L` | 373 | 1 | −1482 |
| `GTCFR-GTCOC-FRO` | 381 | 2 | −11 |
| `AP-JUG-NEA` | 185 | 1 | −126 |
| `GT-MAT-BTL-RU` | 157 | 6 | 28 |
| `AP-TAP-LYC-0.6` | 186 | 1 | 0 |
| `AP-TAP-STR` | 156 | 1 | −40 |
| `AP-TAP-LYC-3.4` | 143 | 1 | 0 |
| `MM-DRI-CAN-0.5L` | 141 | 1 | −29 |
| `AP-TAP-PIN-0.6` | 140 | 1 | 9 |
| `GTMN-PIK-254` | 222 | 38 | −2675 |
| `AP-PLA-STR-11` | 43 | 3 | −941 |
| `GT-GLA-MAT-PRINT` | 37 | 1 | −1400 |
| `AP-SCO-MAT` | 19 | 2 | −1 |
| `AP-TAP-MAN-0.6` | 466 | 2 | 0 |

## Zero sales in 180d — safe to archive if genuinely retired

`AP-DRI-APP` (−116) · `AP-DRI-MAN` (−4) · `AP-TAP-BER-3.3` (8) · `AP-TAP-BER-0.6` ·
`AP-TAP-SCR` (−26) · `AP-TAP-SCR-0.6` · `AP-STA-MAT` · `GT-INF-DES-0.5L` ·
`GTCC-MUZ-RSSP-1L` · `GTMX-MUZ-*` remainder · `MM-DRI-CAN-0.33L` (−145) ·
`MM-DRI-CAN-0.2L` · `PCKBX-CAR-BOX-0.2L` (−77) · `PCKBX-CAR-BOX-…-1L` (−54)

Zero sales ≠ retired — check seasonality before archiving.

## Not a sync defect

Coverage is measured **system → Shopify** (Tom 2026-08-01): every item sold in our system
is mapped. All 53 are. Nothing here is a gap in the sync; it is a question of which
storefront lines GT wants inside the stock model at all.
