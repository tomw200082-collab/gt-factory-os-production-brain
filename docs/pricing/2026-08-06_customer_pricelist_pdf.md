# Customer-facing pricelist PDF (ex-VAT) — V3

**Date:** 2026-08-06 (V3 — third pass the same day, after Tom's V2 notes)
**Deliverable:** `docs/pricing/pricelist_pdf/GT_pricelist_2026-08-06.pdf` — 4 pages,
A4 210×297 mm, **1.7 MB**, fully self-contained (fonts + images embedded base64).

## Tom's V3 corrections (2026-08-06, all applied)

1. **Bold type is now Rubik** (500/600) — rounded terminals, elegant; it carries
   the cover title, band titles, section titles, product names, prices, kickers
   and folios. Heebo 300 stays for the quiet sub-lines. Frank Ruhl dropped.
2. **MATCHA 50 g removed** — not sold.
3. **מקציף קוקטיילים removed** from the tools page.
4. **Powders band replaced** — the terracotta-arches crop is gone; the band is
   now the matcha still-life (whisks · iced matcha · MATCHA bag) from
   `CATALOG/MATCHA UBE HOJICHA/…135246…` — product-focused like the other pages.
5. **קנקן זכוכית עם מסננת (Neapolitan jug, ₪36) removed** — not relevant here
   (Tom, 2026-08-06). It was also one of the two rows with no photograph.

Designer's polish pass, same commit: pages 2–3 get taller tiles and looser row
leading (`.roomy`) now that they carry fewer rows; footer optically centred;
band scrim deepened .62→.68; sub-lines up 7.6→7.8 pt; price ₪ mark rebalanced.

**Size discipline:** every cutout sits on the flat paper colour, so alpha buys
nothing — cutouts are composited onto PAPER and embedded as JPEG (`b64png`),
and the cover PNG became JPEG q88. PDF: 11.2 MB → **1.7 MB**, no visible change.

## Superseded V2 record
**Purpose:** a pricelist Tom sends directly to a HoReCa customer, product photo
beside every priced row.

## Tom's V2 corrections (2026-08-06, all applied)

1. **Page tops are photographs, not compositions.** One lifestyle photo from
   Dropbox `AI YASTREBOVA/CATALOG/2 slide/` per price page — no more cutting
   products to build the header strip.
2. **GT Elita 30g can removed** — "זה לא אמור להיות שם".
3. **No shipping mention anywhere.**
4. **No "בש״ח"** — redundant; only "ללא מע״מ" stays.
5. **Half-liter bottle stands beside the liter bottle** in every tea row, and a
   bottle of each size stands above its own price column, so size→price is
   visible before any text is read.

## Structure

| Page | Band photo (`CATALOG/2 slide/`) | Content |
|---|---|---|
| Cover | `hf_20260717_103013…` (Tom's pick) | gt mark, מחירון סיטונאי, כל המחירים ללא מע״מ, 2026 |
| 01 | `hf…094541` terrace: NAMASTEA·FRESH·DETOX + drinks | תמציות תה — 11 flavours × (1 ליטר ₪65 · 500 מ״ל ₪33), pair tile per row |
| 02 | `hf…100249` terracotta arches | מאצ׳ה ואבקות (7) + מחיות פרי (3) |
| 03 | `hf…100640` travertine shelf | מוצרים משלימים (10) |

**V3 count: 28 rows, 39 priced figures** (V2 minus MATCHA 50 g, מקציף קוקטיילים and קנקן נפוליטן).

## Price sources

- TSV-backed: `docs/pricing/2026-08-05_shopify_products_exvat.tsv`,
  `price_ils_exvat`, matched by SKU — **0 mismatches** on every keyed row.
- Tom-supplied (2026-08-05, no active Shopify SKU): `AMERICAN` ₪65/1L + ₪33/500ml ·
  `HOJICHA` ₪375/500g.

Final verification output:

```
V3: figures checked: 39 | mismatches vs TSV: NONE | all present: True
removed absent — 50g · cocktail frother · Elita · Neapolitan jug: all True
ללא מע״מ: True · בש״ח: False · משלוח: False
pages: 4 | 210×297 mm | 1.70 MB | overflow guard: clean
```

## Photography

- **Band photos + cover:** Dropbox `CATALOG/2 slide/` (Tom's link, 2026-08-06).
- **1 L bottles (11):** `AI YASTREBOVA/all bottles/` — `fresh.jpg`, `fresh +.jpg`,
  `detox.jpg`, `detox +.jpg`, `energy.jpg`, `calm.jpg`, `consiusness.jpg`,
  `revive.jpg`, `desert tea.jpg`, `namastea.jpg`, `american.png`.
- **500 ml carafes (11):** same folder, the `* small` files — every flavour has one.
- **Powders (3):** `CATALOG/MATCHA UBE HOJICHA/` — matcha (black bag), hojicha
  (gold bag), ube (white bag).
- **ODK purées (3):** `CATALOG/ODK/` clean packshots.
- **Accessories (8):** `AI YASTREBOVA/small products/` — bowl, frother, whisk,
  beaker, stand, jigger, scoop; brown 500 ml bottle from the same set.
- **Monogram fallback (2 rows only):** מאצ׳ה 22 שקיות (only a 229 px thumbnail
  exists anywhere) · ערכת מאצ׳ה — no photo in Dropbox or Shopify.

## Build kit — `docs/pricing/pricelist_pdf/`

| File | Job |
|---|---|
| `getfonts.py` | Heebo + Frank Ruhl Libre full-charset WOFF (Firefox-27 UA trick) |
| `cut.py` | packshot → transparent cutout (see findings below) |
| `build.py` | data + HTML/CSS → `pricelist.html`; band crops from the source photos |
| `fonts/` | the seven WOFF files, committed |

Source photos are **not** committed (Dropbox is their home); `build.py` headers
name every path.

```bash
python3 getfonts.py            # once
python3 -c 'import cut; …'     # per-image calls are listed in build history
python3 build.py
chrome --headless --disable-gpu --no-sandbox --no-pdf-header-footer \
  --print-to-pdf=GT_pricelist.pdf pricelist.html
```

## Findings worth keeping (new in V2)

**`ImageDraw.floodfill` is a silent no-op in Pillow 12.3.0** (mode-L images).
Any mask cleanup built on it inverts or deletes nothing — replaced with numpy
label propagation (`keep_blobs`, `fill_holes` in `cut.py`).

**Two mask families, not one.** Bottles on a grey sweep: keep DARK∨SATURATED
pixels. White bags on a cream/white sweep: keep pixels far from a **separable
backdrop model** (horizontal lighting profile × per-row scale, sampled from the
frame's own margins) — a flat threshold either eats the bag or keeps the shadow.
Holes punched through white products are closed topologically: flood the
background from the frame edge; unreachable background = enclosed hole = object.

**Embed at print resolution.** A 24 mm tile at 300 dpi is 284 px; embedding
1400 px working files shipped a 28 MB PDF. Downscaling embeds (`b64png`) cut it
to 11.2 MB with zero visible change.

**RTL flex order** (unchanged from V1): first child renders rightmost; price
cells and column headers must be built inside their own `direction:ltr` context
or ₪ and column order flip.

## Left for Tom

- 1 row still has no photograph anywhere: ערכת מאצ׳ה
  (+ the 22-sachet box exists only as a 229 px thumbnail).
- Shopify infra/catalog task for מסי is in Notion (created 2026-08-06).
