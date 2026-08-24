"""
Invoice annotation for the route-print-pack skill.

Takes a real Green Invoice PDF + a LionWheel task (with order_items carrying
ordered vs picked quantities) and stamps, per the locked design:

  * elegant vector picking marks at the right margin, precise to each line —
    each an open line glyph (no fill, never a filled triangle):
      - V  -> green line check inside a green ring (picked in full)
      - X  -> terracotta cross inside a terracotta ring (not picked)
      - 9/12 -> amber outlined pill carrying the picked/ordered fraction
  * package count centered under the word "מקור" (round outlined badge)
  * last 3 digits of the order id, top-right, first page only (outlined pill)

Design rationale follows the frontend-design skill: minimal direction =
precision in spacing/type/detail, one quiet outlined system, no fills.
"""
import fitz
from bidi.algorithm import get_display

FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONTR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
HEB = fitz.Font(fontfile=FONTB)
HEBR = fitz.Font(fontfile=FONTR)

# Status palette — saturated stroke colours; the marks are ring + open glyph
# (no fills), so only the line colours are used.
GREEN   = (0.106, 0.451, 0.290)   # picked in full
RED     = (0.741, 0.220, 0.161)   # not picked
AMBER   = (0.706, 0.478, 0.094)   # partial
GTGREEN = (0.118, 0.431, 0.282)   # order pill / package badge — GT brand green
INK     = (0.086, 0.141, 0.110)
MUTE    = (0.416, 0.455, 0.424)


def _reg(pg):
    pg.insert_font(fontname="djv", fontfile=FONTB)
    pg.insert_font(fontname="djvr", fontfile=FONTR)


def _ring(pg, cx, cy, r, color, width=0.8):
    """A clean hairline ring — no fill. The elegant, airy base for a status mark."""
    sh = pg.new_shape()
    sh.draw_circle((cx, cy), r)
    sh.finish(color=color, width=width)
    sh.commit()


def _check(pg, cx, cy, g, color, width=1.5):
    """Plain OPEN line check (✓): two rounded segments — short arm bottom-left,
    longer arm up to the right. closePath=False so it never closes into a filled
    triangle; no fill — just a stroke."""
    sh = pg.new_shape()
    sh.draw_polyline([(cx - g * 0.55, cy + g * 0.04),
                      (cx - g * 0.12, cy + g * 0.46),
                      (cx + g * 0.62, cy - g * 0.50)])
    sh.finish(color=color, width=width, lineCap=1, lineJoin=1,
              closePath=False, fill=None)
    sh.commit()


def _cross(pg, cx, cy, g, color):
    sh = pg.new_shape()
    sh.draw_line((cx - g * 0.46, cy - g * 0.46), (cx + g * 0.46, cy + g * 0.46))
    sh.draw_line((cx - g * 0.46, cy + g * 0.46), (cx + g * 0.46, cy - g * 0.46))
    sh.finish(color=color, width=1.05, lineCap=1, closePath=False, fill=None)
    sh.commit()


def _line_mark(pg, ycen, kind, label):
    """Elegant status mark at the right margin, precise to the line: a hairline
    ring + a finely drawn glyph. One quiet, airy system — no ink-heavy fills."""
    cx, r = pg.rect.width - 27, 6.6   # page-relative; 568 assumed A4
    if kind == "V":
        # success icon: a plain LINE check (open, rounded caps — no fill, no
        # triangle) centered inside a green ring, matching Tom's reference.
        _ring(pg, cx, ycen, r, GREEN, 1.4)
        _check(pg, cx, ycen + 0.3, r * 0.72, GREEN, width=1.2)
    elif kind == "X":
        _ring(pg, cx, ycen, r, RED, 0.8)
        _cross(pg, cx, ycen, r * 0.58, RED)
    else:  # partial — a slim outlined pill carries the picked/ordered fraction
        fs = 6.8
        tw = HEBR.text_length(label, fs)
        pad = 4.0
        w = max(tw + pad * 2, 2 * r)
        box = fitz.Rect(cx - w / 2, ycen - r, cx + w / 2, ycen + r)
        pg.draw_rect(box, color=AMBER, fill=None, width=0.8, radius=0.5)
        pg.insert_text((cx - tw / 2, ycen + fs * 0.36), label,
                       fontname="djvr", fontsize=fs, color=AMBER)


def _order_id_chip(pg, last3):
    """Elegant order badge, top-right: an OUTLINED pill (no ink fill) — a thin
    GT-green hairline, a small 'מס׳ הזמנה' eyebrow, and the last-three digits in
    GT green. Round, clean, light."""
    W = pg.rect.width
    box = fitz.Rect(W - 120, 27, W - 30, 75)
    # outline-only pill: thin border, transparent interior (radius 0.5 = full pill)
    pg.draw_rect(box, color=GTGREEN, fill=None, width=0.9, radius=0.5)
    cx = (box.x0 + box.x1) / 2
    lab = get_display("מס׳ הזמנה")
    lf = 7.5
    lw = HEBR.text_length(lab, lf)
    pg.insert_text((cx - lw / 2, box.y0 + 14), lab,
                   fontname="djvr", fontsize=lf, color=GTGREEN)
    nf = 25
    nw = HEB.text_length(last3, nf)
    pg.insert_text((cx - nw / 2, box.y1 - 11), last3,
                   fontname="djv", fontsize=nf, color=GTGREEN)


def _package_count(doc, pkg):
    """Round, formal package badge centered directly under the word 'מקור':
    a white disc with a GT-green ring (+ thin inner ring), the count inside, and
    a 'חבילות' label beneath."""
    pg = doc[0]
    W = pg.rect.width
    rs = pg.search_for("מקור")
    if rs:
        ybot = max(r.y1 for r in rs)
        cx = sum((r.x0 + r.x1) / 2 for r in rs) / len(rs)
    else:
        ybot, cx = 205, W / 2
    cy = ybot + 12 + 24
    R = 24
    sh = pg.new_shape()
    sh.draw_circle((cx, cy), R)
    sh.finish(color=GTGREEN, fill=(1, 1, 1), width=1.6)
    sh.commit()
    sh = pg.new_shape()
    sh.draw_circle((cx, cy), R - 3)
    sh.finish(color=GTGREEN, width=0.5)
    sh.commit()
    s = str(pkg)
    fs = 26 if len(s) <= 2 else 20
    w = HEB.text_length(s, fs)
    pg.insert_text((cx - w / 2, cy + fs * 0.36), s,
                   fontname="djv", fontsize=fs, color=INK)
    lab = get_display("חבילות")
    lw = HEBR.text_length(lab, 9.5)
    pg.insert_text((cx - lw / 2, cy + R + 11), lab,
                   fontname="djvr", fontsize=9.5, color=MUTE)


def mark_kind(ordered, picked):
    """Return ('V'|'X'|'P', label) from ordered vs picked quantities."""
    if picked >= ordered:
        return "V", "V"
    if picked <= 0:
        return "X", "X"
    return "P", f"{int(picked)}/{int(ordered)}"


def _drop_trailing_blank_pages(doc):
    """Green Invoice sometimes spills a last page that carries nothing essential —
    empty, or just a repeated header + a "חתימה:" signature label. Those waste two
    printed sheets per stop (×2 copies), so drop them. A trailing page is KEPT only
    when it carries real content: a ₪ amount, VAT ('מע"מ'), or a GT- SKU (line-item
    or totals spilled over). The first page is never dropped."""
    while doc.page_count > 1:
        text = doc[doc.page_count - 1].get_text()
        if ("₪" in text) or ('מע"מ' in text) or ("GT-" in text):
            break
        doc.delete_page(doc.page_count - 1)


# --------------------------------------------------------------------------- #
# product-line matching (Tom, 2026-08-24 — "ליישר קו סופית על הסימונים")
# Green Invoice does not word a line exactly the way LionWheel does, so the old
# search_for(name) exact-substring match missed lines outright — and its "first
# two words" fallback then stamped the WRONG line whenever two products share a
# prefix ("בסיס לימונדה …"), which is most of the catalogue. Match on shared
# words, make the winner beat the runner-up, and hand anything still unmatched
# back to the caller instead of printing a silently unmarked invoice.
# --------------------------------------------------------------------------- #
_PUNCT = str.maketrans({c: " " for c in "\"'`׳״’‘,.;:()[]{}/\\|*+-–—"})


def _tokens(s):
    """Comparable words. Punctuation and every geresh/quote variant out; single
    letters out — a lone letter (a preposition, a stray glyph) matches everything
    and decides nothing. Single DIGITS stay: "1 ליטר" vs "2 ליטר" is exactly the
    kind of difference a mark must not get wrong."""
    return [w for w in str(s or "").translate(_PUNCT).lower().split()
            if len(w) > 1 or w.isdigit()]


def _page_lines(pg):
    """[(words, y_center)] per text line, off the word layer. A mark points at a
    line, so it rides that line's own bbox — not a substring hit that may sit in
    a header or a totals row."""
    rows = {}
    for x0, y0, x1, y1, w, blk, ln, _ in pg.get_text("words"):
        r = rows.setdefault((blk, ln), [[], y0, y1])
        r[0].append(w)
        r[1] = min(r[1], y0)
        r[2] = max(r[2], y1)
    return [(ws, (top + bot) / 2) for ws, top, bot in rows.values()]


def _find_line(doc, name, used):
    """(page_no, y_center) of the invoice line for `name`, or None.

    Ranked by how many of the product's words the line carries, then by how few
    words the line adds. Some Green Invoice PDFs extract Hebrew visually reversed,
    so each line word counts in both directions.

    Three things must hold before a mark is placed, because a wrong mark is money
    thrown away (Tom, 2026-08-24) while an unplaced one is merely reported:
      * enough shared words to mean anything;
      * a STRICTLY better score than the runner-up — where two lines are equally
        likely, a mark is a coin toss;
      * at least one shared word that is RARE on this invoice. Generic words
        (בסיס, ליטר, מיץ) are carried by every sibling product, so agreement built
        only from them is a guess: "בסיס לימונדה אשכוליות 1 ליטר" would otherwise
        land on the plain "בסיס לימונדה 1 ליטר" line — four words of agreement and
        the wrong product. The rare word — the flavour, the size, the type — is
        what actually identifies a line."""
    toks = _tokens(name)
    if not toks:
        return None
    cands = []
    for pno in range(len(doc)):
        for words, ycen in _page_lines(doc[pno]):
            base = set(_tokens(" ".join(words)))
            lt = base | {w[::-1] for w in base}
            sc = sum(1 for t in toks if t in lt)
            cands.append(((sc, -max(0, len(base) - sc)), pno, ycen, lt))
    if not cands:
        return None
    cands.sort(key=lambda c: c[0], reverse=True)
    key, pno, ycen, lt = cands[0]
    if key[0] < min(2, len(toks)):
        return None                       # nothing on the invoice resembles it
    if len(cands) > 1 and cands[1][0] == key:
        return None                       # two lines equally likely — a coin toss
    df = {t: sum(1 for c in cands if t in c[3]) for t in toks}
    if not any(df[t] <= 1 for t in toks if t in lt):
        return None                       # agreement on generic words only
    spot = (pno, round(ycen, 1))
    if spot in used:
        # Its line already carries a mark. Scoring deliberately ignores `used`,
        # so a second item cannot be pushed onto the next-best line — which would
        # be some other product's.
        return None
    used.add(spot)
    return pno, ycen


def _stamp(doc, name, kind, label, used):
    """Draw one status mark on the invoice line for `name`. False = unmatched."""
    hit = _find_line(doc, name, used)
    if not hit:
        return False
    _line_mark(doc[hit[0]], hit[1], kind, label)
    return True


def annotate(task, src_pdf, out_pdf, mark_lines=True, missing_names=None,
             show_packages=True, shortfall_only=False):
    """Stamp marks onto a real GI invoice PDF. Lines matched by product name.

    Four modes, in precedence order:
      missing_names=[...]  shortage-list mode. Ignores picked_quantity entirely
                           and marks ✗ on the named products only — for when
                           picking is still in progress, so the per-line picked
                           counts are not yet trustworthy, but the shortages are
                           already known. Everything unmarked = in full.
      shortfall_only=True  picking is finished: mark ONLY the lines where
                           picked < ordered, leaving every complete line clean.
                           This is the DEFAULT (Tom, 2026-08-04).
      mark_lines=True      per-line ✓/✗/partial from ordered vs picked.
      mark_lines=False     no line marks (order picked in full).
    The order-id chip and package badge are always stamped.

    Returns the product names whose invoice line could not be matched — the
    caller surfaces them so an unmarkable shortfall is never mistaken for a
    fully-picked order."""
    doc = fitz.open(src_pdf)
    # Trim the tail page BEFORE stamping: a mark placed on a page that is then
    # deleted is a shortfall that silently never printed.
    _drop_trailing_blank_pages(doc)
    for pno in range(len(doc)):
        _reg(doc[pno])
    used, unmatched = set(), []

    def stamp(name, kind, label):
        """A mark that cannot be placed goes back to the caller, never dropped:
        an invoice missing its ✗ reads to the driver as picked in full."""
        if name and not _stamp(doc, name, kind, label, used):
            unmatched.append(name)

    if missing_names:
        # Explicit shortage list wins over picked_quantity: it is used precisely
        # when picking is unfinished and those counts are not yet truth.
        low = [m.lower() for m in missing_names]
        for it in (task.get("order_items") or []):
            name = it.get("name") or ""
            if any(m in name.lower() for m in low):
                stamp(name, "X", "X")
    elif shortfall_only:
        # Picking is finished, so picked_quantity IS truth — but mark only the
        # lines that fell short. A ✓ on every complete line is ink the driver has
        # to read past to find the one line that needs a conversation.
        for it in (task.get("order_items") or []):
            try:
                q, pq = float(it["quantity"]), float(it["picked_quantity"])
            except (TypeError, ValueError, KeyError):
                continue
            if pq < q:
                kind, label = mark_kind(q, pq)
                stamp(it.get("name") or "", kind, label)
    elif mark_lines:
        for it in (task.get("order_items") or []):
            name = it.get("name") or ""
            try:
                q = float(it["quantity"])
                pq = float(it["picked_quantity"])
            except (TypeError, ValueError, KeyError):
                continue
            kind, label = mark_kind(q, pq)
            stamp(name, kind, label)
    wp = task.get("wp_order_id") or ""
    last3 = "".join(c for c in wp if c.isdigit())[-3:]
    if last3:
        _order_id_chip(doc[0], last3)
    if show_packages and task.get("packages_quantity"):
        _package_count(doc, task["packages_quantity"])
    doc.save(out_pdf)
    doc.close()
    return unmatched
