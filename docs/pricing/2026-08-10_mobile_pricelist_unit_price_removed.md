# Mobile pricelist — unit price removed, 500 ml bottle added to every tea row

**Date:** 2026-08-10. Two changes from Tom, in order:
1. "תוריד פה את המחיר לכוס — שפשוט לא יהיה כתוב את זה. תשאיר את כל השאר."
2. "להוסיף את כל הבקבוקי 500ML ליד הבקבוקי 1 ליטר לפי כל סוג."

**Deliverable:** `docs/pricing/pricelist_pdf/mobile/GT_pricelist_mobile_2026-08-10.pdf`
— 8 pages, 256.08 × 454.08 pt (mobile), 560 KB.

Both edits are made on the PDF, in two scripts run in order
(`strip_unit_prices.py` → `add_500ml_bottles.py`); §How below explains why that is
sound here rather than a rebuild.

## What changed

| Page | Removed |
|---|---|
| 02 | `₪2.60–3.25 לכוס`, and the `·` that separated it from the rest of its row |
| 03 | same |
| 04 | `₪2.12 למנה` · `₪2.68 למנה` · `₪1.35 למנה` · `₪0.68 למנה` · `₪0.70 למנה` |

Seven runs in total. Nothing else on any page moved.

## What deliberately stayed

- `20–25 כוסות מבקבוק ליטר` (pages 2–3) — a yield, not a price. It shared a row
  with the per-cup figure; the row now carries only the yield.
- `מנת מאצ׳ה והודג׳יצ׳ה 1.8 גרם · מנת אובה 2 גרם` (page 4) — a dosage, not a
  price. It reads as product information on its own once the per-serving figures
  are gone.

Tom's instruction named the per-cup price. The per-serving figures on page 4 are
the same fact under a different label — a unit price per drink — so they came out
with it. If only the tea pages were meant, page 4 is one re-run away.

## Change 2 — the 500 ml bottle beside the litre bottle

Every tea row on pages 2–3 carried one photograph, the 1 L bottle. It now carries
the pair, the 500 ml standing to the left of the litre — the same order as the
price band above it (`₪33 500 מ״ל` left, `₪65 1 ליטר` right), so size → price reads
the same way down the page.

| Page | Rows |
|---|---|
| 02 | FRESH · FRESH ללא סוכר · DETOX · DETOX ללא סוכר · ENERGY |
| 03 | CALM · CONSCIOUSNESS · REVIVE · DESERTEA · NAMASTEA · AMERICAN |

Eleven rows, eleven cutouts, one per flavour.

- **Source:** Canva design `DAHR5IzII6w` — "all 500ml bottles no background", 11
  pages, Tom's link. Exported as transparent PNG and trimmed to the bottle;
  committed under `pricelist_pdf/mobile/cutouts_500ml/`, named by flavour.
- **Sizing:** height is 72% of the litre bottle (their real-world ratio), width
  follows each cutout's own aspect. Both are expressed as ratios of the existing
  litre-bottle box, so the pair inherits whatever transform its row sits in.
- **Baseline:** `w 0 0 -h x y cm` puts the image's foot at `y`, so the two bottles
  share `y` and stand on the same line.
- **Fit:** the litre bottle does not move. The pair grows leftward into the gap
  between the text and the photo — measured, not assumed: text ends at 557 px and
  the bottle starts at 626 px at 220 dpi on every row, and the 500 ml occupies
  about half of that 69 px gap.
- **Matching row to cutout was done by eye, off the labels.** A colour-signature
  match was tried first and rejected: it separated first from second place by 3–9
  units on the FRESH and DETOX pairs — noise, and those are exactly the pairs where
  a swap would be invisible to the script and obvious to a customer.

## How

The mobile PDF has **no build source in this repo** (the A4 pricelist in
`pricelist_pdf/` is a different, 4-page artifact and does not produce it), so the
removal was made on the PDF itself:
`docs/pricing/pricelist_pdf/mobile/strip_unit_prices.py`.

That is safe on this file because Chrome placed every glyph absolutely — each
text run is its own `BT ... ET` block with an explicit `Tm` — so removing a run
shifts nothing around it. The rows are right-aligned and the removed text sat at
the left end of each row, so no re-centring was needed. Right-alignment was
measured off the render, not assumed: the per-cup row and the bottle-price row
above it both end at the same right margin (x = 349 px at 110 dpi).

The pre-edit file is kept beside it as `…_pre-edit.pdf`.

Adding the bottles is the same kind of edit in the other direction: a new image
XObject per row plus one `cm … Do` after the litre bottle's, inside its own `q…Q`.

```bash
python3 strip_unit_prices.py GT_pricelist_mobile_2026-08-10_pre-edit.pdf step1_no_unit_prices.pdf
python3 add_500ml_bottles.py          # reads step1_no_unit_prices.pdf + cutouts_500ml/
```

## Evidence

```
change 1 — runs removed:  7  (2 per-cup + 5 per-serving, + 2 separators)
change 2 — bottles added: 11 (5 on page 2, 6 on page 3)
                          page 2 images 6 -> 11 · page 3 images 6 -> 12
pages:               8 in, 8 out
render diff @100dpi: pages 1, 5, 6, 7, 8 pixel-identical to the ORIGINAL input
                     pages 2, 3 (price + bottles) and 4 (per-serving) changed
text search:         "לכוס" absent · "למנה" absent · "2.60" absent · "2.12" absent
                     "כוסות מבקבוק" still present
the two scripts reproduce the committed PDF: 8/8 pages render identical
size:                488,071 B -> 560,280 B  (+11 embedded bottle JPEGs)
```

Prices themselves are untouched — no figure in this PDF was changed, only
deleted. The ex-VAT bottle, powder and accessory prices still match
`docs/pricing/2026-08-05_shopify_products_exvat.tsv` exactly as they did before.
