#!/usr/bin/env python3
"""GT Everyday — tea collection, phone-shaped PDF. No prices.

Eleven infusions, two to a page: a framed studio photograph, the name, the
infusion type, and what is in the bottle. Nothing else — no selling lines, no
cups-per-bottle, no prices (those live in GT_pricelist_mobile.pdf). Tom,
2026-08-07: "אל תהיה שיווקי בכלל. תכתוב רק את המרכיבים לכל בקבוק."

The wording is frozen. What this file designs is how it *looks*:

  * Every flavour brings its own colour, taken from its own label — a soft wash
    across the block, a glow behind the frame, the folio number and the
    ornaments. The label art is already loud; the page stays paper and lets one
    hue per bottle do the work.
  * Each ingredient gets a minimal drawn mark — hibiscus and a lime wheel for
    FRESH, chamomile and clove for CALM, and so on — set in that flavour's
    colour under the line that names them. Ornament follows content: the marks
    are declared per flavour, never guessed from the string.
  * The mark sits on every page, and every page carries a live WhatsApp link
    to Tom, so a reader can order from wherever they stopped reading.
  * The cover opens on the collection itself: the eleven label colours as one
    band across the foot of the photograph.

Photography is the original studio set (Dropbox `AI YASTREBOVA/all bottles`,
2026-07-17), cropped to a uniform 3:4 around the bottle and kept on its own
clean backdrop — framed, not cut out (Tom, 2026-08-07).

INGREDIENTS is the botanical composition already published on the pricelist's
own origin lines. It is deliberately not a regulated ingredient declaration —
water, sugar and acidity regulators are not listed, because no verified source
for them exists in this repo.

AMERICAN is not yet on sale — its page carries a coming-soon badge.

Pages: cover · 5 × pairs (base + sugar-free share a page) · AMERICAN solo
finale · order page = 8, at 90 × 160 mm (9:16, the phone's own shape).

Build:  python3 build_tea.py   →  GT_tea_collection.pdf
"""
import base64
import pathlib
import subprocess

import build_mobile as bm

HERE = pathlib.Path(__file__).parent
NODE_PW = '/opt/node22/lib/node_modules/playwright/index.mjs'
PAGE_W, PAGE_H = '90mm', '160mm'

TEL_TOM = '053-725-2858'                       # Tom's own line (Tom, 2026-08-07)
WA_TOM = 'https://wa.me/972537252858'          # same number, international form

# ─── copy — frozen, do not edit ─────────────────────────────────────────────
INGREDIENTS = {
    'FRESH':          'היביסקוס · ליים',
    'FRESH ללא סוכר': 'היביסקוס · ליים · ללא תוספת סוכר',
    'DETOX':          'תה ירוק · לואיזה · נענע',
    'DETOX ללא סוכר': 'תה ירוק · לואיזה · נענע · ללא תוספת סוכר',
    'ENERGY':         'תה ירוק · למון גראס',
    'CALM':           'קמומיל · תפוח · ציפורן',
    'CONSCIOUSNESS':  'יסמין · ליצ׳י',
    'REVIVE':         'סנצ׳ה · פסיפלורה',
    'DESERTEA':       'חמישה צמחי בר',
    'NAMASTEA':       'צ׳אי מסאלה',
    'AMERICAN':       'תה שחור · יוזו · הדרים',
}

# ─── colour — one hue per bottle, read off its own label ────────────────────
# (accent, deep). Sampled from `assets/tea/ph_*.jpg` and then chosen by eye:
# k-means on a botanical illustration returns mud, so the numbers below are the
# label's signature hue, not its average.
PALETTE = {
    'fresh':      ('#C2566A', '#1F3A40'),   # rose hibiscus on teal
    'fresh_sf':   ('#7E9159', '#3E4A2E'),   # sage foliage on ivory
    'detox':      ('#C0392B', '#5E1F18'),   # red ground
    'detox_sf':   ('#C9A22B', '#4E5B33'),   # lemon and green on ivory
    'energy':     ('#5B4A94', '#2A2245'),   # indigo, toucan
    'calm':       ('#6B5C9E', '#332C52'),   # violet, white daisies
    'conscious':  ('#C21A63', '#7A0E3E'),   # magenta, flamingo
    'revive':     ('#6FA5BC', '#22362F'),   # hydrangea blue on dark green
    'desertea':   ('#C9A81F', '#5A4E13'),   # desert yellow
    'namastea':   ('#A96A32', '#4E2E1C'),   # amber, camel
    'american':   ('#C0392F', '#5E1C16'),   # red, citrus
}

# ─── ornament — declared per flavour, never parsed out of the string ────────
GLYPHS = {
    'FRESH':          ('hibiscus', 'lime'),
    'FRESH ללא סוכר': ('hibiscus', 'lime'),
    'DETOX':          ('tea', 'verbena', 'mint'),
    'DETOX ללא סוכר': ('tea', 'verbena', 'mint'),
    'ENERGY':         ('tea', 'lemongrass'),
    'CALM':           ('chamomile', 'apple', 'clove'),
    'CONSCIOUSNESS':  ('jasmine', 'lychee'),
    'REVIVE':         ('tea', 'passion'),
    'DESERTEA':       ('sprig',),
    'NAMASTEA':       ('anise',),
    'AMERICAN':       ('blacktea', 'citrus'),
}

# One representative mark per flavour for the cover row — chosen so no two
# repeat, which a first-glyph rule would not give (four flavours start on tea).
COVER_MARK = {
    'FRESH': 'hibiscus', 'FRESH ללא סוכר': 'lime', 'DETOX': 'mint',
    'DETOX ללא סוכר': 'verbena', 'ENERGY': 'lemongrass', 'CALM': 'chamomile',
    'CONSCIOUSNESS': 'jasmine', 'REVIVE': 'passion', 'DESERTEA': 'sprig',
    'NAMASTEA': 'anise', 'AMERICAN': 'citrus',
}
assert len(set(COVER_MARK.values())) == len(COVER_MARK), 'cover marks repeat'

_names = {n for n, _, _ in bm.TEAS}
_keys = {k for _, _, k in bm.TEAS}
assert set(INGREDIENTS) == _names, f'INGREDIENTS out of sync: {set(INGREDIENTS) ^ _names}'
assert set(GLYPHS) == _names, f'GLYPHS out of sync: {set(GLYPHS) ^ _names}'
assert set(COVER_MARK) == _names, f'COVER_MARK out of sync: {set(COVER_MARK) ^ _names}'
assert set(PALETTE) == _keys, f'PALETTE out of sync: {set(PALETTE) ^ _keys}'

# Minimal single-colour marks, 24×24, drawn in the flavour's accent.
MARK = {
    'hibiscus': '<circle cx="12" cy="12" r="2.3"/>'
                '<g opacity=".92"><ellipse cx="12" cy="5.7" rx="2.9" ry="4.1"/>'
                '<ellipse cx="17.9" cy="9.9" rx="2.9" ry="4.1" transform="rotate(72 17.9 9.9)"/>'
                '<ellipse cx="15.7" cy="17.1" rx="2.9" ry="4.1" transform="rotate(144 15.7 17.1)"/>'
                '<ellipse cx="8.3" cy="17.1" rx="2.9" ry="4.1" transform="rotate(216 8.3 17.1)"/>'
                '<ellipse cx="6.1" cy="9.9" rx="2.9" ry="4.1" transform="rotate(288 6.1 9.9)"/></g>',
    'jasmine':  '<g opacity=".9"><ellipse cx="12" cy="6.2" rx="2.2" ry="3.7"/>'
                '<ellipse cx="17.5" cy="10.2" rx="2.2" ry="3.7" transform="rotate(72 17.5 10.2)"/>'
                '<ellipse cx="15.4" cy="16.8" rx="2.2" ry="3.7" transform="rotate(144 15.4 16.8)"/>'
                '<ellipse cx="8.6" cy="16.8" rx="2.2" ry="3.7" transform="rotate(216 8.6 16.8)"/>'
                '<ellipse cx="6.5" cy="10.2" rx="2.2" ry="3.7" transform="rotate(288 6.5 10.2)"/></g>'
                '<circle cx="12" cy="12" r="1.7" fill="#EFE6D6"/>',
    'chamomile': '<g opacity=".9"><ellipse cx="12" cy="5.4" rx="1.5" ry="3.5"/>'
                 '<ellipse cx="12" cy="18.6" rx="1.5" ry="3.5"/>'
                 '<ellipse cx="5.4" cy="12" rx="3.5" ry="1.5"/>'
                 '<ellipse cx="18.6" cy="12" rx="3.5" ry="1.5"/>'
                 '<ellipse cx="7.3" cy="7.3" rx="3.3" ry="1.4" transform="rotate(-45 7.3 7.3)"/>'
                 '<ellipse cx="16.7" cy="16.7" rx="3.3" ry="1.4" transform="rotate(-45 16.7 16.7)"/>'
                 '<ellipse cx="16.7" cy="7.3" rx="1.4" ry="3.3" transform="rotate(-45 16.7 7.3)"/>'
                 '<ellipse cx="7.3" cy="16.7" rx="1.4" ry="3.3" transform="rotate(-45 7.3 16.7)"/></g>'
                 '<circle cx="12" cy="12" r="2.6"/>',
    'lime':     '<g fill="none" stroke="currentColor" stroke-width="1.5">'
                '<circle cx="12" cy="12" r="8.6"/><circle cx="12" cy="12" r="6.2" stroke-width="1"/>'
                '<g stroke-width="1"><path d="M12 5.8v12.4M5.8 12h12.4M7.6 7.6l8.8 8.8M16.4 7.6l-8.8 8.8"/>'
                '</g></g>',
    'citrus':   '<g fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round">'
                '<path d="M3.2 13.2a8.8 8.8 0 0 1 17.6 0Z"/>'
                '<path d="M5.8 13.2a6.2 6.2 0 0 1 12.4 0" stroke-width="1"/>'
                '<g stroke-width="1"><path d="M12 13.2V7M12 13.2 7.6 8.8M12 13.2l4.4-4.4'
                'M12 13.2H5.8M12 13.2h6.2"/></g></g>',
    'tea':      '<g fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" '
                'stroke-linejoin="round"><path d="M20 4.2c0 8.2-5.5 13.2-11.7 13.2-2.6 0-4.5-1.4-4.5-1.4'
                'C3.8 8.2 9.3 4.2 20 4.2Z"/><path d="M4.4 20.2c3-5.7 7.7-9.3 13.3-12.9"/></g>',
    'blacktea': '<g fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" '
                'stroke-linejoin="round"><path d="M12 21V10.4"/>'
                '<path d="M12 13.4c-3.4 0-6.1-2.5-6.1-5.6 3.4 0 6.1 2.5 6.1 5.6Z"/>'
                '<path d="M12 13.4c3.4 0 6.1-2.5 6.1-5.6-3.4 0-6.1 2.5-6.1 5.6Z"/>'
                '<path d="M12 10.4c0-2.3 1.1-4.2 2.7-4.8C14.7 7.9 13.6 9.8 12 10.4Z"/></g>',
    'mint':     '<g fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" '
                'stroke-linejoin="round"><path d="M12 21V9.6"/>'
                '<path d="M12 12.6c0-3.4-2.5-6.2-5.7-6.2C6.3 9.8 8.8 12.6 12 12.6Z"/>'
                '<path d="M12 9.6c0-3.4 2.5-6.2 5.7-6.2C17.7 6.8 15.2 9.6 12 9.6Z"/></g>',
    'verbena':  '<g fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" '
                'stroke-linejoin="round"><path d="M12 21V3.4"/>'
                '<path d="M12 9.2c-2.7 0-4.7-1.7-5-4.2 2.7.4 4.7 2.1 5 4.2Z"/>'
                '<path d="M12 9.2c2.7 0 4.7-1.7 5-4.2-2.7.4-4.7 2.1-5 4.2Z"/>'
                '<path d="M12 15.2c-2.7 0-4.7-1.7-5-4.2 2.7.4 4.7 2.1 5 4.2Z"/>'
                '<path d="M12 15.2c2.7 0 4.7-1.7 5-4.2-2.7.4-4.7 2.1-5 4.2Z"/></g>',
    'lemongrass': '<g fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round">'
                  '<path d="M12 21.2c0-7.3 1.6-12.6 5.2-17.6"/>'
                  '<path d="M12 21.2C12 13.9 10.4 8.6 6.8 3.6"/>'
                  '<path d="M12 21.2c0-5.2 4.2-9.4 8.4-11.6"/>'
                  '<path d="M12 21.2c0-5.2-4.2-9.4-8.4-11.6"/></g>',
    'passion':  '<circle cx="12" cy="12" r="2.4"/>'
                '<g fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round">'
                '<path d="M12 2.6v6M12 21.4v-6M2.6 12h6M21.4 12h-6M5.3 5.3 9.6 9.6'
                'M18.7 18.7l-4.3-4.3M18.7 5.3l-4.3 4.3M5.3 18.7l4.3-4.3"/>'
                '<circle cx="12" cy="12" r="6.6" opacity=".5"/></g>',
    'apple':    '<g fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round">'
                '<path d="M12 8.4c1.3-1.1 3.2-1.5 4.7-.6 2.1 1.2 2.8 4.1 1.7 7.1-1.1 2.8-3.2 5.1-4.9 5.1'
                '-.7 0-1.1-.3-1.5-.3s-.8.3-1.5.3c-1.7 0-3.8-2.3-4.9-5.1-1.1-3-.4-5.9 1.7-7.1'
                '1.5-.9 3.4-.5 4.7.6Z"/>'
                '<path d="M12 8.4V5.2" stroke-linecap="round"/>'
                '<path d="M12 5.2c1.7 0 3.1-1.2 3.3-2.8-1.8-.2-3.3 1.1-3.3 2.8Z"/></g>',
    'clove':    '<g fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">'
                '<path d="M12 20.6V9.4"/><circle cx="12" cy="6.6" r="2.5"/>'
                '<path d="M12 6.6 9.2 3.6M12 6.6l2.8-3M9.5 6.6H6.2M17.8 6.6h-3.3"/></g>',
    'sprig':    '<g fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round">'
                '<path d="M12 21.2V7.6"/><path d="M12 12.6 7.2 8.4M12 12.6l4.8-4.2'
                'M12 17 8.3 14M12 17l3.7-3M12 8.8 9.3 5.6M12 8.8l2.7-3.2"/></g>'
                '<circle cx="12" cy="5" r="1.5"/>',
    'lychee':   '<g fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">'
                '<circle cx="12" cy="13.6" r="6.9"/>'
                '<path d="M12 6.7V4.4"/>'
                '<path d="M12 4.4c1.5-.3 2.4-1.4 2.5-2.8-1.5.1-2.5 1.3-2.5 2.8Z"/>'
                '<g stroke-width=".95"><path d="M8.5 10.4 10 11.9M15.5 10.4 14 11.9'
                'M8.5 16.8 10 15.3M15.5 16.8 14 15.3M12 9.6v1.8M12 17.6v-1.8"/></g></g>',
    'anise':    '<g opacity=".94"><path d="M12 2.2 14.1 9.5 12 12.2 9.9 9.5Z"/>'
                '<path d="m21.3 8.9-5.8 4.8-3.1-1.7 1.7-3.3Z"/>'
                '<path d="m17.8 20.2-5.6-4.8v-3.5l3.3 1.1Z"/>'
                '<path d="M6.2 20.2 11.8 15.4v-3.5l-3.3 1.1Z"/>'
                '<path d="M2.7 8.9l5.8 4.8 3.1-1.7-1.7-3.3Z"/></g>'
                '<circle cx="12" cy="12" r="1.5" fill="#EFE6D6"/>',
}
_tokens = {t for tokens in GLYPHS.values() for t in tokens}
assert _tokens <= set(MARK), f'GLYPHS token with no MARK: {sorted(_tokens - set(MARK))}'

PAIRS = [bm.TEAS[0:2], bm.TEAS[2:4], bm.TEAS[4:6], bm.TEAS[6:8], bm.TEAS[8:10]]
FINALE = bm.TEAS[10]
SPECTRUM = [PALETTE[k][0] for _, _, k in bm.TEAS]

WA_MARK = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2C6.6 2 2.2 '
           '6.4 2.2 11.8c0 1.8.5 3.4 1.3 4.9L2 22l5.4-1.4a9.8 9.8 0 0 0 4.6 1.2c5.4 0 9.8-4.4 '
           '9.8-9.8S17.4 2 12 2Zm0 17.9c-1.5 0-2.9-.4-4.1-1.1l-.3-.2-3.1.8.8-3-.2-.3a8.1 8.1 0 0 '
           '1-1.2-4.3c0-4.5 3.7-8.2 8.1-8.2 4.5 0 8.2 3.7 8.2 8.2s-3.7 8.1-8.2 8.1Zm4.5-6.1c-.2-.1'
           '-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1-.2.2-.6.8-.8 1-.1.2-.3.2-.5.1-.2-.1-1-.4-2-1.2-.7-.7'
           '-1.2-1.5-1.4-1.7-.1-.2 0-.4.1-.5l.4-.4c.1-.2.2-.3.2-.4.1-.2 0-.3 0-.4 0-.1-.6-1.3-.8'
           '-1.8-.2-.5-.4-.4-.5-.4h-.5c-.2 0-.4.1-.6.3-.2.2-.9.9-.9 2.1s.9 2.4 1 2.5c.1.2 1.7 2.7 '
           '4.2 3.7 2.1.8 2.5.7 3 .6.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.1-1.2 0-.1-.2-.2-.4-.3Z"/></svg>')


# ─── helpers ────────────────────────────────────────────────────────────────
def rgba(hex_colour, alpha):
    h = hex_colour.lstrip('#')
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f'rgba({r},{g},{b},{alpha})'


def photo(key):
    return 'data:image/jpeg;base64,' + base64.b64encode(
        (HERE / 'assets' / 'tea' / f'ph_{key}.jpg').read_bytes()).decode()


def marks(name):
    return "".join(f'<svg viewBox="0 0 24 24" fill="currentColor">{MARK[g]}</svg>'
                   for g in GLYPHS[name])


def kind(origin):
    """'חליטה תאילנדית · היביסקוס וליים' → 'חליטה תאילנדית'."""
    return origin.split(' · ')[0]


def show(name):
    """'FRESH ללא סוכר' stacks badly at display size — the qualifier drops a line.
    CONSCIOUSNESS is one unbreakable word — long names take a smaller size."""
    qual = ''
    if name.endswith(' ללא סוכר'):
        name = name[:-len(' ללא סוכר')]
        qual = '<span class="q">ללא סוכר</span>'
    size = '' if len(name) <= 9 else ' style="font-size:10pt;letter-spacing:.04em"'
    return f'<span{size}>{name}</span>{qual}'


def css():
    bands = "".join(
        f'.sp i:nth-child({i + 1}){{background:{c}}}' for i, c in enumerate(SPECTRUM))
    return f"""
{bm.font_faces()}
*,*::before,*::after{{margin:0;padding:0;box-sizing:border-box}}
@page{{size:{PAGE_W} {PAGE_H};margin:0}}
html,body{{background:{bm.PAPER}}}
body{{font-family:'Heebo',sans-serif;color:{bm.INK};-webkit-font-smoothing:antialiased}}
a{{color:inherit;text-decoration:none}}

.p{{position:relative;width:{PAGE_W};height:{PAGE_H};overflow:hidden;background:{bm.PAPER};
   direction:rtl;page-break-after:always}}
.p:last-child{{page-break-after:auto}}

/* ── cover ────────────────────────────────────────────────────────────── */
.cover>img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;
  object-position:50% 100%}}
.cover::after{{content:'';position:absolute;inset:0;background:linear-gradient(180deg,
  rgba(239,230,214,.92) 0%,rgba(239,230,214,.62) 30%,rgba(239,230,214,.10) 52%,
  rgba(239,230,214,0) 66%)}}
.cv{{position:absolute;inset:0;z-index:2;padding:15mm 9mm 0;display:flex;
  flex-direction:column;align-items:center;text-align:center}}
.cv .mark{{width:27mm}}
.cv .hair{{width:14mm;height:.5px;background:{bm.INK};opacity:.3;margin:7mm 0 6mm}}
.cv h1{{font-family:'Rubik',sans-serif;font-weight:700;font-size:33pt;line-height:1.06;
  letter-spacing:-.012em}}
.cv .sub{{margin-top:4.4mm;font-size:8.8pt;line-height:1.9;color:{bm.MUTED};letter-spacing:.02em}}
.cv .idx{{margin-top:9mm;padding-top:6mm;border-top:.5px solid {rgba(bm.INK, .16)};
  width:100%;display:flex;direction:ltr;justify-content:space-between;align-items:center}}
.cv .idx svg{{width:4.7mm;height:4.7mm;display:block}}
.cover .yr{{position:absolute;z-index:3;top:9mm;right:9mm;font-family:'Rubik',sans-serif;
  font-weight:600;font-size:7.4pt;letter-spacing:.42em;opacity:.5}}
/* the collection itself, as a band of its own eleven label colours */
.sp{{position:absolute;z-index:3;left:0;right:0;bottom:0;height:9mm;display:flex;
  direction:ltr}}
.sp i{{flex:1 1 0}}
.sp::before{{content:'';position:absolute;left:0;right:0;bottom:9mm;height:11mm;
  background:linear-gradient(180deg,rgba(20,14,8,0),rgba(20,14,8,.26))}}
{bands}

/* ── flavour blocks ───────────────────────────────────────────────────── */
.half{{position:absolute;right:0;left:0;height:69mm;display:flex;align-items:center;
  gap:7mm;padding:0 9mm;color:var(--c)}}
.half.a{{top:6mm}}
.half.b{{top:80mm}}
.half.b::after{{content:'';position:absolute;top:-5.5mm;right:9mm;left:9mm;height:.5px;
  background:{bm.RULE}}}
.half>*{{position:relative;z-index:1}}

/* the colour runs off the page edge as a card; the photograph sits on it in a
   white matte, and one botanical mark is blown up inside it as a watermark */
.phw{{flex:0 0 37mm;position:relative}}
.card{{position:absolute;top:-5mm;bottom:-5mm;left:-4.5mm;right:-9mm;overflow:hidden;
  background:linear-gradient(160deg,var(--card1),var(--card2))}}
.card .wm{{position:absolute;bottom:-11mm;left:-10mm;width:36mm;height:36mm;
  color:var(--c);opacity:.15;transform:rotate(-8deg)}}
.ph{{position:relative;display:block;background:#fff;border:.5px solid var(--frame);
  padding:1.4mm;box-shadow:0 1mm 3mm rgba(36,28,21,.16)}}
.ph img{{display:block;width:100%;height:auto}}

.tx{{flex:1 1 auto;min-width:0;color:{bm.INK}}}
.no{{font-family:'Rubik',sans-serif;font-weight:700;font-size:6.4pt;letter-spacing:.3em;
  color:var(--c)}}
.tx h2{{margin-top:1.6mm;font-family:'Rubik',sans-serif;font-weight:700;font-size:13pt;
  line-height:1.12;letter-spacing:.01em;white-space:nowrap}}
.tx h2 .q{{display:block;font-size:.62em;margin-top:.8mm}}
.or{{margin-top:1.6mm;font-family:'Rubik',sans-serif;font-weight:500;font-size:6.8pt;
  letter-spacing:.04em;color:{bm.MUTED}}}
.ing{{margin-top:3.4mm;font-size:10pt;line-height:1.55;color:{bm.INK}}}
.gl{{margin-top:3.4mm;display:flex;gap:3.2mm;color:var(--c)}}
.gl svg{{width:6.6mm;height:6.6mm;display:block}}
.sz{{margin-top:3mm;font-family:'Rubik',sans-serif;font-weight:600;font-size:6.6pt;
  letter-spacing:.14em;color:{bm.MUTED};white-space:nowrap}}

/* ── finale ───────────────────────────────────────────────────────────── */
.solo{{position:absolute;inset:0;padding:0 11mm;display:flex;flex-direction:column;
  justify-content:center;align-items:center;text-align:center;color:var(--c)}}
.solo::before{{content:'';position:absolute;inset:0;z-index:0;
  background:radial-gradient(72% 38% at 50% 33%,var(--card1),rgba(0,0,0,0) 100%)}}
.solo>*{{position:relative;z-index:1}}
.solo .ph{{width:52mm;padding:1.6mm;box-shadow:0 1mm 3.4mm rgba(36,28,21,.14)}}
.soon{{position:absolute;top:4mm;left:-3mm;z-index:2;background:var(--c);color:#fff;
  font-family:'Rubik',sans-serif;font-weight:700;font-size:7.6pt;letter-spacing:.16em;
  padding:2mm 4.4mm;box-shadow:0 .6mm 2mm rgba(36,28,21,.20)}}
.solo .no{{margin-top:7mm;font-size:7pt;letter-spacing:.34em}}
.solo h2{{margin-top:2mm;font-family:'Rubik',sans-serif;font-weight:700;font-size:22pt;
  color:{bm.INK}}}
.solo .or{{margin-top:2mm;font-size:7.6pt;letter-spacing:.06em}}
.solo .ing{{margin-top:4mm;max-width:58mm;font-size:11.5pt;line-height:1.6}}
.solo .gl{{margin-top:5mm;justify-content:center;gap:4mm}}
.solo .gl svg{{width:7mm;height:7mm}}

/* ── order page ───────────────────────────────────────────────────────── */
.order{{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;
  align-items:center;text-align:center;padding:0 11mm}}
.order .mark{{width:30mm}}
.order h2{{margin-top:11mm;font-family:'Rubik',sans-serif;font-weight:700;font-size:27pt;
  line-height:1.14}}
.order h2 span{{display:block;font-size:.74em;margin-top:1.6mm}}
.order .cta{{margin-top:11mm;width:100%;background:{bm.GREEN};color:{bm.PAPER};padding:5mm 0;
  font-family:'Rubik',sans-serif;font-weight:700;font-size:15pt;direction:ltr;
  display:block;box-shadow:0 1mm 3mm rgba(38,59,24,.22)}}
.order .cta small{{display:block;font-weight:500;font-size:6.8pt;letter-spacing:.22em;
  opacity:.85;margin-bottom:1.6mm;direction:rtl}}
.band{{position:absolute;z-index:2;left:0;right:0;bottom:0;height:6mm;display:flex;
  direction:ltr}}
.band i{{flex:1 1 0}}

/* ── page furniture ───────────────────────────────────────────────────── */
.foot{{position:absolute;bottom:5.4mm;right:9mm;left:9mm;z-index:3;display:flex;
  align-items:center;justify-content:space-between;font-size:5.6pt;letter-spacing:.12em;
  color:{bm.MUTED}}}
.foot .id{{display:flex;align-items:center;gap:2mm}}
.foot .id img{{width:8.4mm;height:auto;opacity:.88}}
.foot .end{{display:flex;align-items:center;gap:2.6mm}}
.foot .wa{{display:flex;align-items:center;justify-content:center;width:5.6mm;height:5.6mm;
  border-radius:50%;background:{bm.GREEN};color:{bm.PAPER}}}
.foot .wa svg{{width:3.6mm;height:3.6mm;display:block}}
.foot .pg{{font-family:'Rubik',sans-serif;font-weight:600;letter-spacing:.24em;opacity:.85}}
"""


def foot(n):
    return f"""<div class="foot">
  <span class="id"><img src="{bm.img('logo_green.png')}" alt="GT EVERYDAY">gteveryday.com</span>
  <span class="end"><a class="wa" href="{WA_TOM}">{WA_MARK}</a>
    <span class="pg">{n:02d}</span></span>
</div>"""


def block(pos, idx, name, origin, key):
    accent, deep = PALETTE[key]
    style = (f'--c:{accent};--card1:{rgba(accent, .26)};--card2:{rgba(accent, .11)};'
             f'--frame:{rgba(deep, .28)}')
    big = f'<svg class="wm" viewBox="0 0 24 24" fill="currentColor">{MARK[GLYPHS[name][0]]}</svg>'
    return f"""<div class="half {pos}" style="{style}">
  <span class="phw"><span class="card">{big}</span>
    <span class="ph"><img src="{photo(key)}" alt="{name}"></span></span>
  <span class="tx">
    <span class="no">N°{idx:02d}</span>
    <h2>{show(name)}</h2>
    <span class="or">{kind(origin)}</span>
    <p class="ing">{INGREDIENTS[name]}</p>
    <span class="gl">{marks(name)}</span>
    <span class="sz">1 ליטר · 500 מ״ל</span>
  </span>
</div>"""


def build():
    bm.MODE, bm.FONT_EXT = 'inline', 'woff'

    index_row = "".join(
        f'<svg viewBox="0 0 24 24" fill="currentColor" style="color:{PALETTE[k][0]}">'
        f'{MARK[COVER_MARK[n]]}</svg>' for n, _, k in bm.TEAS)
    cover = f"""<div class="p cover">
  <img src="{bm.img('cover.jpg')}" alt="">
  <span class="yr">2026</span>
  <div class="cv">
    <img class="mark" src="{bm.img('logo_ink.png')}" alt="GT EVERYDAY">
    <span class="hair"></span>
    <h1>תמציות תה</h1>
    <p class="sub">אחד עשר טעמים<br>1 ליטר · 500 מ״ל</p>
    <span class="idx">{index_row}</span>
  </div>
  <span class="sp">{''.join('<i></i>' for _ in SPECTRUM)}</span>
</div>"""

    pages, n = [], 0
    for pi, pair in enumerate(PAIRS):
        halves = []
        for hi, (name, origin, key) in enumerate(pair):
            n += 1
            halves.append(block('a' if hi == 0 else 'b', n, name, origin, key))
        pages.append(f'<div class="p">{"".join(halves)}{foot(pi + 2)}</div>')

    name, origin, key = FINALE
    accent, deep = PALETTE[key]
    finale = f"""<div class="p">
  <div class="solo" style="--c:{accent};--card1:{rgba(accent, .20)};--frame:{rgba(deep, .30)}">
    <span class="ph" style="position:relative"><img src="{photo(key)}" alt="{name}">
      <span class="soon">בקרוב</span></span>
    <span class="no">N°11 · COMING&nbsp;SOON</span>
    <h2>{name}</h2>
    <span class="or">{kind(origin)}</span>
    <p class="ing">{INGREDIENTS[name]}</p>
    <span class="gl">{marks(name)}</span>
  </div>
  {foot(7)}
</div>"""

    order = f"""<div class="p">
  <div class="order">
    <img class="mark" src="{bm.img('logo_green.png')}" alt="GT EVERYDAY">
    <h2>להזמנות<span>תום</span></h2>
    <a class="cta" href="{WA_TOM}"><small>בוואטסאפ או בטלפון</small>{TEL_TOM}</a>
  </div>
  <span class="band">{''.join(f'<i style="background:{c}"></i>' for c in SPECTRUM)}</span>
</div>"""

    html = (f'<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8">'
            f'<title>GT Everyday — תמציות תה</title><style>{css()}</style></head>'
            f'<body>{cover}{"".join(pages)}{finale}{order}</body></html>')

    src = HERE / '.tea-src.html'
    src.write_text(html, encoding='utf-8')
    out = HERE / 'GT_tea_collection.pdf'
    shot = HERE / '.tea-shot.mjs'
    shot.write_text(f"""
import {{ chromium }} from '{NODE_PW}';
const b = await chromium.launch();
const p = await b.newPage();
await p.goto('file://{src}', {{ waitUntil: 'load' }});
await p.evaluate(() => document.fonts.ready);
await p.pdf({{ path: '{out}', width: '{PAGE_W}', height: '{PAGE_H}',
  printBackground: true, margin: {{ top: 0, right: 0, bottom: 0, left: 0 }} }});
await b.close();
""", encoding='utf-8')
    subprocess.run(['node', str(shot)], check=True, capture_output=True)
    src.unlink()
    shot.unlink()
    print(f'{out.name}  {out.stat().st_size / 1e6:.2f} MB  ·  8 pages  ·  {PAGE_W}×{PAGE_H}')


if __name__ == '__main__':
    build()
