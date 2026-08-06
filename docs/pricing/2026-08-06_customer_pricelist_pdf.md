# Customer-facing pricelist PDF (ex-VAT)

**Date:** 2026-08-06
**Deliverable:** `docs/pricing/pricelist_pdf/GT_pricelist_2026-08-06.pdf` — 4 pages, A4 210×297 mm, 8.47 MB, fully self-contained (fonts + images embedded base64, no network needed to view).
**Purpose:** a pricelist Tom can send directly to a HoReCa customer, with a product photo beside every priced row.
**Direction chosen by Tom:** "ב" — *המדף*, quiet/classic. Prices stay **ללא מע״מ**.

## Structure

| Page | Content |
|---|---|
| Cover | deep green `#0E2622`, gold GT monogram, "תמציות, מאצ׳ה ומוצרים משלימים", pill `כל המחירים ללא מע״מ`, six bottle cutouts standing on a hairline shelf |
| 1/3 | `01 תמציות תה` — 11 flavours, two price columns (`1 ליטר` · `500 מ״ל`) |
| 2/3 | `02 מאצ׳ה ואבקות` (8) + `03 מחיות פרי` (3) |
| 3/3 | `04 מוצרים משלימים` (10) |

32 rows, 43 priced figures. Same scope and the same numbers as Canva page 26 of
`DAHQrpThEBE` (see `2026-08-05_products_pricelist_page.md`).

## Price sources — unchanged from the Canva page

- 40 of 43 figures: `docs/pricing/2026-08-05_shopify_products_exvat.tsv`, column
  `price_ils_exvat`, matched by SKU. No conversion, no rounding.
- 3 figures supplied by Tom on 2026-08-05 (no active Shopify SKU):
  `AMERICAN` ₪65 / 1 L and ₪33 / 500 ml · `HOJICHA` ₪375 / 500 g.

Verification run against the TSV after the final build:

```
priced rows checked: 43  TSV-backed: 40  Tom-supplied: 3
PRICE MISMATCHES: NONE
figures in PDF vs expected: MATCH
  contains "ללא מע״מ": True
  contains "מחירון סיטונאי": True
  contains "054-398-2444": True
pages: 4 | size mm: 210 x 297
overflow guard: text blocks below the footer band = 0 on all 4 pages
```

## Photography

21 of 32 rows carry a real photograph; 11 fall back to a GT-monogram tile.

**Bottle cutouts (10)** — Dropbox `/Data Center/Data Center GT/03_MARKETING_BRAND/תמונות בקבוקים חדשים.zip`.
File → product, established by opening each image:

| Source file | Product |
|---|---|
| `…5588` | FRESH |
| `…5610` | CALM |
| `…5616` | DESERTEA |
| `…5627` | ENERGY |
| `…5636` | DETOX |
| `…5645` | REVIVE |
| `…5656` | NAMASTEA |
| `…5671` | FRESH ללא סוכר |
| `…5688` | DETOX ללא סוכר |
| `…5699` | CONSCIOUSNESS |

**Packshots (11)** — Shopify CDN, URLs listed in `pricelist_pdf/fetch.py`.

Logos: `/Data Center/PRODUCTION 2/B-BAGEL-Tea-Programme/assets/gt-logo-black.png`
and `/New/ARCHIVE/…/Logos/GT_Logo_White.png`.

### The 11 rows with no photograph anywhere

AMERICAN · מאצ׳ה 50 גרם · GT Elita 30 גרם · HOJICHA · UBE 500 גרם ·
ערכת מאצ׳ה · מקציף מאצ׳ה חשמלי · מקציף קוקטיילים · קנקן זכוכית עם מסננת ·
כוס מדידה · בקבוק מאצ׳ה 500 מ״ל.

Neither Dropbox nor Shopify carries an image for these. They render the
monogram tile, which reads as deliberate rather than missing — but a photo of
each is the one thing between this and a fully photographed pricelist.

## Build kit — `docs/pricing/pricelist_pdf/`

| File | Job |
|---|---|
| `getfonts.py` | Heebo 400/500/700/900 + Frank Ruhl Libre 400/500/700 as full-charset WOFF |
| `fetch.py` | Shopify CDN packshots → `raw/` |
| `prep3.py` / `prep4.py` | white-background cutout extraction → `assets/` |
| `build.py` | data tables + HTML/CSS → `pricelist.html` |
| `fonts/` | the seven WOFF files, committed (Google Fonts is UA-dependent, see below) |

`assets/` and `raw/` are **not** committed — they are regenerable byte-for-byte
from `fetch.py` + `prep4.py` plus the Dropbox zip named above.

```bash
python3 getfonts.py && python3 fetch.py && python3 prep4.py && python3 build.py
/opt/pw-browsers/chromium-1194/chrome-linux/chrome --headless --disable-gpu \
  --no-sandbox --no-pdf-header-footer --virtual-time-budget=20000 \
  --print-to-pdf=GT_pricelist.pdf pricelist.html
```

## Three findings worth keeping

**Google Fonts serves a different file per User-Agent.** A modern Chrome UA
returns Latin-only subset woff2 — Hebrew renders as tofu. An IE UA returns EOT,
unusable. `Mozilla/5.0 (Windows NT 6.1; rv:27.0) Gecko/20100101 Firefox/27.0`
returns a **single full-charset WOFF per weight**; each file verified to carry
50–53 Hebrew glyphs plus `₪` before use.

**Cutting a product out of a white background without a halo.** Thresholding
luminance alone eats the cream labels; thresholding saturation alone keeps the
grey drop-shadow. Keeping *dark OR colourful* does both:

```python
dark = L.point(lambda v: 255 if v < 205 else 0)
col  = sat.point(lambda v: 255 if v > 14 else 0)
m = ImageChops.lighter(dark, col)
m = m.filter(MaxFilter(5)).filter(MinFilter(5)).filter(GaussianBlur(0.6))
```

**RTL flips column order, not glyph order.** In `direction: rtl` the first flex
child renders rightmost, so the header array must be written
`["1 ליטר", "500 מ״ל"]` to appear as `500 מ״ל | 1 ליטר`. Price cells need
`direction: ltr` of their own or `₪` lands on the wrong side of the digits.

## Left for Tom

- Photograph the 11 products above (or confirm the monogram tile is fine).
- The pricelist carries **ex-VAT** prices — matches the Canva page and Tom's
  instruction. If it ever goes to a consumer rather than a business, the basis
  changes and the footnote must change with it.
