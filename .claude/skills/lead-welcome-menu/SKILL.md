---
name: lead-welcome-menu
description: >-
  Rebuild GT's opening menu for a new lead — one Hebrew, right-to-left, 9:16
  mobile-native PDF of 15 screens that presents four products and twelve costed
  drinks to a business lead who just left their details. Use when a drink's
  approved figure changes, when a product photograph is added or replaced, when
  the contact block changes, or when the PDF simply has to be regenerated.
---

# Lead-welcome menu

One PDF, sent on WhatsApp to a café or bakery owner about two minutes after they
leave their name and phone number. It shows FOOD COST, recommended price, margin
and profit per cup for twelve drinks. It shows **no wholesale price** — what GT
charges is not on this page, by Tom's ruling.

Nothing here computes a price, a margin or a profit. If a number is wrong it is
wrong in `drinks-pricelist/drinks_final_figures.json`, and that is where it gets
fixed. `build.py` asserts the twelve keys against that file on every build and
halts with `contract_failure` on any mismatch rather than adapting.

## Files

| File | What it is |
|---|---|
| `copy.md` | Every screen's Hebrew copy, with the source of each line. Read this before changing wording. |
| `DIRECTION.md` | The committed design direction — purpose, aesthetic, the one unforgettable thing, and what this must not look like. |
| `SYSTEM.md` | The type and spacing scale, computed from the 0.361× phone collapse. |
| `tokens.css` | Colour tokens, each with the record it came from and why it holds that value. |
| `build.py` | figures + copy → `lead-menu.html` |
| `shot.py` | `lead-menu.html` → `lead-menu.pdf` via the bundled headless Chromium |
| `shot_png.py` | every screen → `shots/` at full size and at 390px phone scale |
| `validate.py` | D3 — the figures |
| `verify.py` | D1, D4, D5, D6, D7, D8 — geometry, type scale, no wholesale price, offline, closing screen |
| `assets/` | Three packshots, three prepared-glass photographs, the black GT logo. 1.6 MB. |

## Build

```bash
python3 build.py && python3 shot.py       # → lead-menu.html, lead-menu.pdf
python3 validate.py && python3 verify.py --all
python3 shot_png.py                       # → shots/, for looking at
```

15 screens at 1080×1920, MediaBox 810×1440 pt, ratio 0.5625. Rubik and Heebo
embed from the repo's own WOFFs; **no network is used or permitted** — a
`<link>` to Google Fonts fails behind the egress proxy, Chromium falls back
silently, and the Hebrew ships in the wrong face. `verify.py --offline` exists
to catch exactly that.

## Judge it at phone scale, never at 1080px

A 1080px page read fit-to-width on a ~390px phone shrinks by **0.361×**. A 16px
caption lands at 5.8 effective pixels and is gone. That single fact drives the
whole type system: content type starts at 36px, a product name is ~130px, a hero
figure is 180px. `shot_png.py` writes `shots/phoneNN.png` at true phone width —
look at those. Looking at the 1080px source is how this deliverable fails.

The same arithmetic applies to rules: a 1px hairline becomes 0.36px. Rules are
3px and `--line` is darkened from the registered swatch for that reason.

## The four answers

Set once, in `DIRECTION.md`, so a rebuild inherits them:

1. **Purpose** — the reader should feel respected, not seduced. Showing the cost
   next to the profit *is* the sales asset; a deck that shows only profit is one
   the buyer has already seen through.
2. **Direction** — Editorial, at phone scale. GT's own registered grammar
   (full-bleed photo with type over it, hairline instead of boxes, spaced
   capitals) taken to 9:16 and made louder.
3. **The one unforgettable thing** — S03, the mapping. Four coloured spines,
   twelve drinks, and exactly one hairline that crosses.
4. **What it must not be** — not a spreadsheet, not a Canva template, not a SaaS
   pricing page, not a restaurant menu, not an A4 brochure squeezed onto a phone.

## Changing something

- **A figure changed** → change `drinks_final_figures.json`, rebuild. If
  `build.py` halts, the approved figures moved and that is a business decision,
  not a build problem. Surface it.
- **Wording** → `copy.md` first, then `build.py`. Preparation steps, drink
  descriptions and ingredient panels are verbatim from Canva `DAHPi9gpfts`;
  product blurbs from `DAHQrpThEBE`. Do not invent replacements for language
  that already shipped. Where the catalog carries no description, this deck
  carries none.
- **A product list** → `docs/warehouses/catalog-truth.md` beats the Canva
  catalog, which still lists four products GT does not sell. `verify.py
  --no-wholesale` checks all four.
- **A photograph** → drop it in `assets/`, keep the folder under 2.5 MB, and add
  a dated row to `docs/warehouses/marketing-assets.md`.

## Still open

- **No MATCHA packshot exists** at bottle quality. S11 and S12 are deliberately
  typographic. When Tom picks one, add it as `assets/bottle-matcha.png` and set
  `shot=` on the MATCHA entry in `build.py`.
- The asterisk `* כולל הערכת עלות גרניש/קצף` is carried on eleven of the twelve,
  exactly as the drinks catalog has it. The figures file marks only key `12`.
  The two disagree; neither was changed. See `copy.md` §Open.
