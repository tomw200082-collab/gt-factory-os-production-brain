# Mobile pricelist — per-cup / per-serving price removed

**Date:** 2026-08-10 (Tom: "תוריד פה את המחיר לכוס — שפשוט לא יהיה כתוב את זה. תשאיר את כל השאר.")
**Deliverable:** `docs/pricing/pricelist_pdf/mobile/GT_pricelist_mobile_2026-08-10.pdf`
— 8 pages, 256.08 × 454.08 pt (mobile), 485 KB.

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

```bash
python3 strip_unit_prices.py GT_pricelist_mobile_2026-08-10_pre-edit.pdf out.pdf
```

## Evidence

```
runs removed:        7  (2 per-cup + 5 per-serving, + 2 separators)
pages:               8 in, 8 out
render diff @100dpi: pages 1, 5, 6, 7, 8 pixel-identical to the input
                     pages 2, 3, 4 changed
text search:         "לכוס"  absent · "למנה" absent · "2.60" absent · "2.12" absent
                     "כוסות מבקבוק" still present
script reproduces the delivered PDF byte-for-byte on re-run (8/8 pages match)
size:                488,071 B -> 485,200 B
```

Prices themselves are untouched — no figure in this PDF was changed, only
deleted. The ex-VAT bottle, powder and accessory prices still match
`docs/pricing/2026-08-05_shopify_products_exvat.tsv` exactly as they did before.
