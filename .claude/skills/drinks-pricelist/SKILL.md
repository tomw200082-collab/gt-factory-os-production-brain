---
name: drinks-pricelist
description: >-
  Rebuild the GT Everyday drinks cost sheet (the "what you keep from every cup"
  PDF) from the approved FOOD COST figures, and validate the SUMMER 2026 Canva
  catalog against those same figures. Use when a drink's cost, price, margin or
  profit-per-cup changes, when the catalog and the pricelist need to be proven
  identical, or when the pricelist PDF has to be regenerated.
---

# Drinks pricelist

Two jobs, one source of truth.

1. **Build** the cost-sheet PDF from `drinks_final_figures.json`.
2. **Validate** that the Canva catalog still says exactly what that file says.

The figures file is the authority for both. Nothing here recomputes a price, a
margin or a profit — if a number is wrong, it is wrong in the figures file and
that is where it gets fixed.

## Current figures — read this before quoting any price

**`drinks_final_figures.json` in this directory is the only live figures file.**
48 drinks, every margin ≥81%, Tom-approved 2026-08-26. Whole-shekel prices; cost
ex-VAT, price VAT-inclusive; 44 of 48 costs carry `*`.

Both live designs were brought into exact agreement with it on 2026-08-26 and
verified by direct read — catalog `DAHPi9gpfts` (all 48 drink pages, 0 deviations)
and opening menu `DAHTXqsXzDg` (pages 3–14, 48/48 fields).

The pre-2026-08-26 figures (₪19-era prices, 77% margins) are **superseded** and live
in `docs/archive/2026-08-05_drinks_final_figures.superseded-2026-08-26.json`. Do not
quote them, and do not run
`docs/archive/RESUME_PROMPT_finish_catalog.spent-2026-08-26.md`, which points at them.

## Files

| File | What it is |
|---|---|
| `drinks_final_figures.json` | The 48 approved drinks: name, cost, price, margin, profit, asterisk. Authority. |
| `foodcost_proposal.csv` | The costing run the figures came from (Tom, 2026-08-05). Carries the pre-change costs too, so provenance is checkable. |
| `build.py` | figures → `pricelist.html` |
| `style.css` | The sheet's design. See "Design" below before changing it. |
| `shot.py` | `pricelist.html` → `pricelist.pdf` via the bundled headless Chromium |
| `validate.py` | on-page catalog values vs the figures file, plus an independent VAT re-derivation |

Outside this directory:

| File | What it is |
|---|---|
| `scripts/build_drinks_pricing_xlsx.py` | figures → the customer-facing xlsx. Re-derives margin and profit as a self-check and refuses to write on any disagreement. |
| `docs/pricing/2026-08-26_drinks_pricing_81pct.xlsx` | The current customer-facing costing sheet. Regenerate it, never hand-edit it. Carries no wholesale price, no landed cost, no supplier name. |

## Build

```bash
python3 build.py && python3 shot.py     # → pricelist.html, pricelist.pdf
```

Three A4 pages, Hebrew RTL, DejaVu Sans + FreeSerif embedded. No network needed;
the Chromium path is resolved inside `shot.py`.

## Validate against the catalog

Canva design `DAHPi9gpfts` — 64 pages, 48 of them drinks:

```
8-14 · 16-18 · 20-23 · 25-27 · 29-34 · 36-40 · 42-46 · 48-53 · 55-58 · 60-64
```

Read them back with the Canva MCP `read-design` (no transaction — you want the
saved state, and the plain read returns just the text, which is far cheaper than
the full CDF). Transcribe the five figures per page into `observed.json` in the
shape `validate.py` expects, then:

```bash
python3 validate.py                      # expect: deviations 0
```

`validate.py` checks page count, cost string, asterisk placement, both labels,
margin, profit, and sale price — then re-derives margin and profit from
`price ÷ 1.18 − cost` on its own. That second pass matters: it means a wrong
figure cannot pass just because the reference file is wrong in the same way.

## The VAT rule — the thing that goes wrong

- **FOOD COST is ex-VAT.** Ingredient cost, no VAT.
- **The recommended price includes VAT (18%).** It is the consumer price.
- **Margin and profit are computed ex-VAT**, on `price ÷ 1.18`, because VAT is
  not the café's income — they collect it and hand it to the state.

So: `profit = price ÷ 1.18 − cost` and `margin % = profit ÷ (price ÷ 1.18)`.

Computing margin as `(price − cost) ÷ price` instead — mixing an ex-VAT cost
against a VAT-inclusive price — overstates it by 2 to 5 points on every drink.
The `שוליים מוצע` column in `foodcost_proposal.csv` does exactly that, so **do
not** copy figures out of that column. It is kept only for provenance.

The catalog's contents page (Canva page 2) states this rule in prose. If the
rule ever changes, that page changes too — it contradicted the drink pages once
already, and a café owner reading it priced against the wrong basis.

## Editing the catalog

Per drink page, five text elements carry the block. Find them by content, never
by a stored element id — ids do not survive between sessions:

| Element | Match on | Becomes |
|---|---|---|
| cost value | `^₪\d+\.\d\d\*?$`, fontSize 56 | new cost — **keep the `*` if the page has one** |
| cost label | starts `FOOD COST` | `FOOD COST · ללא מע״מ` |
| price label | starts `מחיר מומלץ` | `מחיר מומלץ · כולל מע״מ` |
| margin | `^\d\d%$`, fontSize 56 | new margin |
| profit | `^₪\d+\.\d\d לכוס$` | new profit |

Never touched: the sale price itself, the `רווח` label, the garnish footnote.

The asterisk is **not** uniform — pages 8, 16, 17 and 18 have none, the other 44
do. Read each page's current cost text and preserve what is there rather than
assuming.

`edit-design` needs `is_editable: true, is_responsive: false, is_empty: false`,
one page per call. Edits stay uncommitted until an explicit `finalize: "commit"`
with empty operations; commit is irreversible and a committed transaction cannot
be reused. Commit every few pages and keep a ledger on disk — a lost transaction
costs every uncommitted page in it.

### Building a NEW page — the line-metrics trap (2026-08-06)

The connector cannot set fonts, so every `add_text` lands in Canva's default
`YACgEZ1cb1Q`. That font's line box depends on the **scripts present in the
line**, which breaks any multi-column layout built from separate text blocks:

| Line contains | Rendered pitch |
|---|---|
| Latin letters, digits, or `₪` | `1.96 × font_size × line_height` |
| Hebrew only | `1.00 × font_size × line_height` |

Two blocks stay row-aligned **only if every line in both uses the same script
mix**. A names column of `ENGLISH · עברית` lines aligns with a `₪NN` price
column at equal `line_height`; a Hebrew-only names column drifts, and the drift
is *per line*, so no single `line_height` fixes it. The fix that works is to
make every row the same shape — give each Hebrew row a real Latin token (the
product's actual English name, never an invented one), not to tune leading.

Measure, don't eyeball: the edit response returns a thumbnail URL. `curl` it and
scan dark-pixel row bands with Pillow to get true pitch and per-row offsets. CDF
`size` heights are *nominal* and disagree with the render — they cannot be used
to verify alignment.

Also: `pos: A,B` is `top,left` (confirmed live). `insert_shape` returns no
reusable id in the same batch. `add_page` gives no page id — re-read
`design_content` with the open `transaction_id` to get it. A brand-new page has
no thumbnail until committed, so the transaction thumbnail is the only preview.

## Design

The sheet is deliberately not a spreadsheet dump. Two structural facts drive it,
and both are load-bearing:

- **Every family has exactly one price**, so the price sits on the family band
  once instead of repeating down 48 rows. `build.py` asserts this and stops if a
  family ever gets mixed prices.
- **The bar is the signature.** Full width is one cup's net revenue; the clay
  segment is what the drink costs to make. Every bar is the same length, so only
  the split point moves and the eye can run down the column. It is explained
  once in the masthead and never repeated.

Palette and type are lifted off the catalog pages, not invented: ink `#26221a`,
GT green `#123b39`, clay `#a8562f`, sand `#6b6455`, cream `#fbf8f2`; Latin serif
display + Hebrew sans, matching the deck.

## Evidence to report

Files changed · rows rendered · fields compared vs the figures file **and** vs
the CSV · deviations · asterisk count (expect 44) · PDF page count and size.
"It should work" is not evidence.
