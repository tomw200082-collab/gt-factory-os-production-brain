"""
Invoice annotation for the route-print-pack skill.

Takes a real Green Invoice PDF + a LionWheel task (with order_items carrying
ordered vs picked quantities) and stamps, per the locked design:

  * elegant vector picking marks at the right margin, precise to each line:
      - V  -> green check  (picked in full)
      - X  -> terracotta cross (not picked)
      - 9/12 -> amber fraction (partially picked)
  * package count (black, no box) centered under the word "מקור"
  * last 3 digits of the order id, top-right, first page only

Design rationale follows the frontend-design skill: minimal direction =
precision in spacing/type/detail, one quiet system, no templated defaults.
"""
import fitz
from bidi.algorithm import get_display

FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONTR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
HEB = fitz.Font(fontfile=FONTB)
HEBR = fitz.Font(fontfile=FONTR)

# Status palette — two-tone (saturated glyph on a pale fill, thin same-hue ring).
# Reads as a formal, rounded status badge rather than a loose pen-stroke.
GREEN      = (0.106, 0.451, 0.290)   # picked in full
GREEN_FILL = (0.898, 0.953, 0.918)
RED        = (0.741, 0.220, 0.161)   # not picked
RED_FILL   = (0.973, 0.914, 0.898)
AMBER      = (0.706, 0.478, 0.094)   # partial
AMBER_FILL = (0.992, 0.953, 0.851)
GTGREEN    = (0.118, 0.431, 0.282)   # order pill / package badge — GT brand green
INK        = (0.086, 0.141, 0.110)
MUTE       = (0.416, 0.455, 0.424)
HAIR       = (0.80, 0.83, 0.89)


def _reg(pg):
    pg.insert_font(fontname="djv", fontfile=FONTB)
    pg.insert_font(fontname="djvr", fontfile=FONTR)


def _disc(pg, cx, cy, r, fill, ring):
    sh = pg.new_shape()
    sh.draw_circle((cx, cy), r)
    sh.finish(color=ring, fill=fill, width=1.1)
    sh.commit()


def _check(pg, cx, cy, g, color):
    sh = pg.new_shape()
    sh.draw_polyline([(cx - g * 0.52, cy + g * 0.04),
                      (cx - g * 0.14, cy + g * 0.42),
                      (cx + g * 0.56, cy - g * 0.44)])
    sh.finish(color=color, width=1.5, lineCap=1, lineJoin=1)
    sh.commit()


def _cross(pg, cx, cy, g, color):
    sh = pg.new_shape()
    sh.draw_line((cx - g * 0.46, cy - g * 0.46), (cx + g * 0.46, cy + g * 0.46))
    sh.draw_line((cx - g * 0.46, cy + g * 0.46), (cx + g * 0.46, cy - g * 0.46))
    sh.finish(color=color, width=1.5, lineCap=1)
    sh.commit()


def _line_mark(pg, ycen, kind, label):
    """Formal rounded status badge at the right margin, precise to the line."""
    cx, r = 568, 7.2
    if kind == "V":
        _disc(pg, cx, ycen, r, GREEN_FILL, GREEN)
        _check(pg, cx, ycen, r * 0.78, GREEN)
    elif kind == "X":
        _disc(pg, cx, ycen, r, RED_FILL, RED)
        _cross(pg, cx, ycen, r * 0.78, RED)
    else:  # partial — rounded pill sized to the fraction
        fs = 7.5
        tw = HEBR.text_length(label, fs)
        pad = 4.5
        w = tw + pad * 2
        box = fitz.Rect(cx - w / 2, ycen - 7, cx + w / 2, ycen + 7)
        pg.draw_rect(box, color=AMBER, fill=AMBER_FILL, width=1.1, radius=0.5)
        pg.insert_text((cx - tw / 2, ycen + fs * 0.36), label,
                       fontname="djv", fontsize=fs, color=AMBER)


def _order_id_chip(pg, last3):
    """Formal labeled order badge, top-right: a rounded GT-green pill with a small
    'מס׳ הזמנה' eyebrow over the last-three digits in white."""
    W = pg.rect.width
    box = fitz.Rect(W - 122, 26, W - 28, 80)
    pg.draw_rect(box, color=GTGREEN, fill=GTGREEN, width=0, radius=0.32)
    cx = (box.x0 + box.x1) / 2
    lab = get_display("מס׳ הזמנה")
    lf = 8
    lw = HEBR.text_length(lab, lf)
    pg.insert_text((cx - lw / 2, box.y0 + 15), lab,
                   fontname="djvr", fontsize=lf, color=(0.86, 0.93, 0.88))
    nf = 27
    nw = HEB.text_length(last3, nf)
    pg.insert_text((cx - nw / 2, box.y1 - 11), last3,
                   fontname="djv", fontsize=nf, color=(1, 1, 1))


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
    doc.save(out_pdf)
    doc.close()
