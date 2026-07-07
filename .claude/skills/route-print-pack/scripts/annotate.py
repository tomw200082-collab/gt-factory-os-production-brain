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
    cx, r = 568, 6.6
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


def annotate(task, src_pdf, out_pdf):
    """Stamp marks onto a real GI invoice PDF. Lines matched by product name."""
    doc = fitz.open(src_pdf)
    for pno in range(len(doc)):
        _reg(doc[pno])
    for it in (task.get("order_items") or []):
        name = it.get("name") or ""
        try:
            q = float(it["quantity"])
            pq = float(it["picked_quantity"])
        except (TypeError, ValueError, KeyError):
            continue
        kind, label = mark_kind(q, pq)
        for pno in range(len(doc)):
            pg = doc[pno]
            rs = pg.search_for(name) or pg.search_for(" ".join(name.split()[:2]))
            if rs:
                _line_mark(pg, (rs[0].y0 + rs[0].y1) / 2, kind, label)
                break
    wp = task.get("wp_order_id") or ""
    last3 = "".join(c for c in wp if c.isdigit())[-3:]
    if last3:
        _order_id_chip(doc[0], last3)
    if task.get("packages_quantity"):
        _package_count(doc, task["packages_quantity"])
    _drop_trailing_blank_pages(doc)   # save paper: no signature-only / empty tail pages
    doc.save(out_pdf)
    doc.close()
