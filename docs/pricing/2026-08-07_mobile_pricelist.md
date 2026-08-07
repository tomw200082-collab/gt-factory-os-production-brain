# Customer-facing pricelist — mobile edition

**Date:** 2026-08-07
**Deliverable:** `docs/pricing/pricelist_mobile/GT_pricelist_mobile.html` — one
self-contained page, ~1.0 MB, Hebrew RTL, fonts and photography embedded
base64. No network calls, so it opens the same from a link, a WhatsApp forward
or a saved file.

The A4 sheet in `pricelist_pdf/` stays exactly as it is. This is the same
catalogue rebuilt for a buyer holding a phone behind their bar, and it is the
version to send when the recipient will read it on a phone.

## Figures — unchanged

Prices, product names, sub-lines and section copy are copied from
`pricelist_pdf/build.py`. `build_mobile.py` recomputes nothing and introduces no
figure the print sheet does not carry.

```
28 rows · 39 priced figures     (identical to the print V3 count)
```

Photography is lifted out of the approved print PDF itself, so the image set is
provably the one Tom signed off on 2026-08-06.

## What the phone changes, and why

| Print | Mobile | Reason |
|---|---|---|
| Folios 01 / 02 / 03 | Dropped | There are no pages to number, so the marker carried no information |
| — | Section states its product count and price range | Replaces the folio with something a buyer scanning a catalogue actually uses |
| Price column | Filled tint panel, one per row | The price is why the page exists; it is the only surface allowed to leave the paper colour, so the panels become the scroll's rhythm |
| Bottle above each price column | Both bottles inside the row at true relative height, each over its own price | Size-to-price is a picture before it is a label, and it survives a 320 px screen |
| Page-top photograph | Same photograph, full-bleed, as a section marker | Keeps the catalog's own structure while scrolling |
| Phone number in the footer | Fixed bar: WhatsApp thread + tap-to-call | A buyer who has found their price wants to order |
| — | Sticky header: brand, title, **ללא מע״מ**, four category chips | The ex-VAT fact and the jump-to-section never scroll away |

Structure is carried by hairlines and never by filled cards: the print cutouts
were composited onto the paper colour, so any card fill would show their boxes.

## Colour

Palette sampled from the print sheet — `#EFE6D6` paper, `#241C15` ink,
`#263B18` green, `#FA6E4D` coral. Two additions, both forced by the screen:

- `#C6421F` — coral at text contrast. `#FA6E4D` on paper is 2.3:1 and fails
  WCAG AA, so the ₪ mark uses the darker coral (4.0:1) while the flat coral
  stays for fills that carry ink-coloured text on top (5.9:1).
- `#E4D7BE` — the price panel tint.

Sub-line grey was moved from the print's `#7C6E58` (4.0:1) to `#6A5D48`
(5.2:1) for the same reason.

The page commits to the brand's cream world in both host themes rather than
inverting to a dark palette — every colour is painted explicitly, so it holds on
either ground.

## Checked

- iPhone 13 (390 px), 320 px, and 768 px: no horizontal overflow at any width.
- Focus ring visible on both bar actions and all four chips.
- `prefers-reduced-motion` disables the hero entrance, the scroll reveal and
  smooth scrolling.
- Reveal stagger caps at the 6th row, so a fast thumb never outruns the
  animation on the 11-row tea list.

## Build

```bash
cd docs/pricing/pricelist_mobile
python3 build_mobile.py     # → GT_pricelist_mobile.html + artifact.html
```

`artifact.html` is the same page with the document wrapper stripped, for hosts
that supply their own `<head>`. It is generated, not tracked.

## Open for Tom

- The four category chips are shortened to **תמציות תה · מאצ׳ה · מחיות פרי ·
  ציוד** so all four fit one thumb-width without scrolling. The full names still
  head each section.
- The fixed bar opens a WhatsApp thread to 054-398-2444. If orders should go to
  a different number or to a form, that is a one-line change in
  `build_mobile.py`.

## Hosting — pricelist.gteveryday.com

Tom's call, 2026-08-07: own subdomain, served from this repo through Vercel.

`site/` is the deploy root. Vercel project settings:

| Setting | Value |
|---|---|
| Repository | `tomw200082-collab/gt-factory-os-production-brain` |
| Root Directory | `docs/pricing/pricelist_mobile/site` |
| Framework Preset | Other |
| Build Command | *(none — the folder is already built)* |
| Domain | `pricelist.gteveryday.com` |

DNS is GoDaddy (`ns27/ns28.domaincontrol.com`). The `pricelist` record is added
there, with the exact target Vercel prints after the domain is attached — do not
assume it, Vercel varies the value.

Every later `python3 build_site.py` that is committed and pushed redeploys
itself, because Vercel builds from git and `index.html` is `must-revalidate`.

### Not indexed, on purpose

These are ex-VAT wholesale prices, and the same catalogue sells at retail on the
Shopify store. A shopper who finds this sheet through Google is comparing a
trade price to a shelf price. The page therefore ships `noindex,nofollow` plus a
`robots.txt` disallow: anyone with the link reads it, search engines do not
carry it.

`build_mobile.INDEXABLE` flips both together. Nothing else needs touching.

### Link preview

`og.jpg` (1200×630) is built by `build_og.py` from the same photograph, palette
and faces as the page, because the link will mostly be opened out of a WhatsApp
message and the card is the first thing a buyer sees. `icon-180.png` covers
add-to-home-screen; `icon-32.png` the browser tab.
