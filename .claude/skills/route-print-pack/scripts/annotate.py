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
HEB = fitz.Font(fontfile=FONTB)

# muted, intentional palette (not garish)
GREEN = (0.14, 0.47, 0.36)   # teal-green check
RED   = (0.74, 0.22, 0.16)   # terracotta cross
AMBER = (0.78, 0.52, 0.12)   # partial fraction
NAVY  = (0.20, 0.28, 0.46)   # order-id chip
HAIR  = (0.80, 0.83, 0.89)   # hairline


def _reg(pg):
    pg.insert_font(fontname="djv", fontfile=FONTB)


def _check(pg, cx, cy, s, color):
    sh = pg.new_shape()
    sh.draw_polyline([(cx - s * 0.55, cy + s * 0.02),
                      (cx - s * 0.14, cy + s * 0.44),
                      (cx + s * 0.60, cy - s * 0.50)])
    sh.finish(color=color, width=1.7, lineCap=1, lineJoin=1)
    sh.commit()


def _cross(pg, cx, cy, s, color):
    sh = pg.new_shape()
    sh.draw_line((cx - s * 0.5, cy - s * 0.5), (cx + s * 0.5, cy + s * 0.5))
    sh.draw_line((cx - s * 0.5, cy + s * 0.5), (cx + s * 0.5, cy - s * 0.5))
    sh.finish(color=color, width=1.6, lineCap=1)
    sh.commit()


def _line_mark(pg, ycen, kind, label):
    cx, s = 569, 6.5
    if kind == "V":
        _check(pg, cx, ycen, s, GREEN)
    elif kind == "X":
        _cross(pg, cx, ycen, s, RED)
    else:  # partial
        fs = 8.5
        w = HEB.text_length(label, fs)
        pg.insert_text((cx - w / 2 - 3, ycen + fs * 0.34), label,
                       fontname="djv", fontsize=fs, color=AMBER)


def _order_id_chip(pg, last3):
    W = pg.rect.width
    box = fitz.Rect(W - 116, 24, W - 28, 72)
    pg.draw_rect(box, color=HAIR, fill=None, width=1, radius=0.18)
    fs = 32
    w = HEB.text_length(last3, fs)
    pg.insert_text((box.x0 + (box.width - w) / 2, 59), last3,
                   fontname="djv", fontsize=fs, color=NAVY)


def _package_count(doc, pkg):
    """Black, no colour/box, centered directly under the word 'מקור'."""
    pg = doc[0]
    W = pg.rect.width
    rs = pg.search_for("מקור")
    if rs:
        ybot = max(r.y1 for r in rs)
        cx = sum((r.x0 + r.x1) / 2 for r in rs) / len(rs)
    else:
        ybot, cx = 205, W / 2
    s = str(pkg)
    fs = 38
    w = HEB.text_length(s, fs)
    ny = ybot + 12 + fs
    pg.insert_text((cx - w / 2, ny), s, fontname="djv", fontsize=fs, color=(0, 0, 0))
    lab = get_display("חבילות")
    lw = HEB.text_length(lab, 10)
    pg.insert_text((cx - lw / 2, ny + 15), lab, fontname="djv", fontsize=10, color=(0.4, 0.4, 0.4))


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
