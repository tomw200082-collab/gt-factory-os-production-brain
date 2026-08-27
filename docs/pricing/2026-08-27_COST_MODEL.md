# FOOD COST — bottom-up cost model (2026-08-27)

Replaces the 2026-08-26 FOOD COST figures. **Sale prices are unchanged** — Tom's
instruction on 2026-08-27 was "ב. אל תעלה את המחירים המומלצים יותר" (keep today's
prices, do not raise them). Only FOOD COST and margin % were recomputed.

## Why it changed

The previous FOOD COSTs were carried over from the catalog and could not be
re-derived from any ingredient price list. Tom supplied
`GT_Summer_Menu_2026.xls` (ingredient prices + per-drink doses), so every cost is
now computed from that list instead of restated.

Net effect: the honest cost of the basket is **higher** than what the catalog
previously printed (e.g. iced tea concentrate alone is ₪3.25 for a 50 ml pour,
against a printed cost of ₪3.11 for the whole drink). Margins therefore move
down where the old figure was understated, and up where it was overstated.

## Inputs

From Tom's price list (`GT_Summer_Menu_2026.xls`):

| Ingredient | Price |
|---|---|
| GT concentrate (herbal infusions) | ₪65 / L |
| ODK fruit purée | ₪55 / L |
| Matcha powder | ₪1,080 / kg |
| Ube powder | ₪350 / kg |
| Lemonade | ₪3 / L |
| Coconut cream | ₪14 / L |
| Coconut water | ₪10 / L |
| Milk | ₪8 / L |
| Espresso shot | ₪1.00 |

Assumptions (agreed with Tom, marked as assumptions — not from the list):

| Assumption | Value | Basis |
|---|---|---|
| Cup | 350 ml | Tom: "קח את הקטן כדי שיהיה זול" |
| Base pour (⅔ cup) | 233 ml | derived |
| Foam serving | 70 ml | derived |
| Tonic water (150 ml) | ₪1.50 | cheapest on the market |
| Fresh orange juice (150 ml) | ₪2.00 | cheapest on the market |
| Apple juice | ₪7 / L | cheapest on the market |
| Lychee water | ₪12 / L | cheapest on the market |
| Agave syrup | ₪30 / L | assumption |
| 38% cream | ₪22 / L | assumption |
| Prepared milk foam | ₪6.45 / L | 350 ml cream + 650 ml milk, **÷2** |
| Prepared coconut foam | ₪2.10 / L | 300 ml coconut cream, **÷2** |

**Whipping doubles the foam volume** (Tom, 2026-08-27) — both foams are therefore
costed at half the mixed-liquid price per served litre.

Deliberately **excluded** from FOOD COST, per Tom's decision: garnish, ice, water,
soda, packaging and labour. The printed footnote on the catalog's summary page
says exactly that: `עלות רכיבי המשקה בלבד · ללא גרניש`.

## Formulas

```
profit  = price / 1.18 − cost
margin% = round(profit / (price / 1.18) × 100)
```

FOOD COST is ex-VAT; the recommended price is VAT-inclusive (18%).

## Results

- 48 drinks, prices unchanged (basket total ₪1,380).
- Cost basket: ₪222.05.
- Margin range **76%–87%**, average **80.9%**.
- 17 of 48 drinks sit below 80% — this is the honest consequence of not raising
  prices. Raising them was explicitly declined by Tom.

## Artifacts

- Model: `docs/pricing/2026-08-27_cost_model.py` (re-runnable; prints all 48 costs).
- Figures of record: `.claude/skills/drinks-pricelist/drinks_final_figures.json`.
- Workbook: `docs/pricing/GT_FOOD_COST_2026-08-27.xlsx` (sheet 2 = ingredient prices).
- Pre-edit snapshot of the catalog: `docs/pricing/backups/2026-08-27_DAHTYkRvEnM_pre-costmodel.json`.

## Verification (2026-08-27)

Catalog `DAHTYkRvEnM` (60 pages) — read fresh after commit:

- 48 drink pages: cost / price / margin match the figures file, **0 mismatches**.
- Summary page 60: 48 costs, 48 prices, 48 margins match, **0 mismatches**.
- Footnote replaced; the old `* כולל הערכת עלות גרניש/קצף` no longer appears.
- No price element was written — 95 write operations, 48 cost + 47 margin, 0 price.

Opening menu `DAHTY5nfDxo` (20 pages) — read fresh after commit:

- 12 drink pages: cost / price / margin match the figures file, **0 mismatches**.
- Prices unchanged on all 12.

## Data issues found in the source file

Two defects in `GT_Summer_Menu_2026.xls`, reported and worked around, not silently
"fixed":

1. Matcha rows carry an autofill drag (`50, 51, 52, 53, 54, 55 מ״ל`) instead of a
   constant dose. The model uses the intended 50 ml.
2. The ICE UBE block is shifted by one row against its column headers.

Its `מחיר ₪` column is present but **empty** — that is why the recommended prices
could not be taken from the file and were kept as-is.
