# Products catalog — ex-VAT pricelist page (task 2)

**Date:** 2026-08-05
**Canva design:** `DAHQrpThEBE` — "קטלוג מוצרים 2026"
**Page added:** 26 (`PB9NT0QBlZhqMS2V`), A4 794×1123, background `#f5efe4`
**Status:** built, verified, committed to Canva.

## What the page contains

43 priced rows in 4 sections, names on the right (RTL), prices in fixed columns on the left.

| Section | Rows | Price columns |
|---|---|---|
| תמציות תה | 11 flavours | `1 ליטר` and `500 מ״ל` |
| מאצ׳ה ואבקות | 8 | single |
| מחיות פרי · SMOOTHIE | 3 | single |
| מוצרים משלימים | 10 | single |

Footnote, verbatim as requested: `כל המחירים בש״ח, ללא מע״מ`

## Price sources

- 40 of 43 prices come from `docs/pricing/2026-08-05_shopify_products_exvat.tsv`,
  column `price_ils_exvat`, matched by SKU. No conversion, no rounding.
- 3 prices supplied by Tom on 2026-08-05 because they have no active Shopify SKU:
  - `AMERICAN` — ₪65 / 1 L and ₪33 / 500 ml ("same as all the tea extracts")
  - `HOJICHA` (מאצ׳ה שחורה) — ₪375 / 500 g

## Scope decisions (Tom, 2026-08-05)

- Accessories: "all accessories from Shopify" → all 10 SKUs of Shopify type
  `Accessories` are on the page. `GT-GLA-MAT-PRINT` (printed cup with lid, ₪0.44)
  is type `Packaging`, not `Accessories`, and is not included.
- Cans, cardboard boxes, tapioca, garnish, cocktails, mixers and the sealing machine
  do not appear in the products catalog and are not on the page.

## Verification evidence

- Price check: script comparison of every row against the TSV — **40/40 exact match,
  0 mismatches**; 3 rows Tom-supplied and flagged.
- Accessories coverage: **10/10** Shopify `Accessories` SKUs present, 0 missing.
- Column alignment: page exported to PNG and measured per pixel row.
  **All 32 name↔price row pairs align to ≤0.7 px** across the 4 sections.
- Overflow: ink bounding box `x 55–738`, `y 50–1052` inside the 794×1123 page —
  no bleed, no clipping, no overlap.
- Render checked at full resolution (794 px wide export of the committed page).

## Connector notes worth keeping

The Canva connector cannot set fonts, so every new text element lands in the default
font `YACgEZ1cb1Q`. That font's line box differs by script:

- a line containing **Latin letters or `₪`** renders at pitch ≈ `1.96 × font_size × line_height`
- a line of **Hebrew only** renders at pitch ≈ `1.0 × font_size × line_height`

Two text blocks only stay row-aligned if their lines use the same mix. Blocks of
Hebrew-only rows drift per line and cannot be rescued by `line_height` alone —
the fix was to give every row the same `ENGLISH · עברית` form, using the real
Shopify product names.

## Left for Tom

- **18 text elements on page 26 need the brand font applied manually**
  (Hebrew `YAFdJqqaebw`, English `YACgESME5ew`). The connector cannot set fonts.
  Select all on the page and set the font — sizes, colours and positions stay.
