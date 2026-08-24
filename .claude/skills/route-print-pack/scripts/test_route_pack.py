#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Self-check for the two pieces of route-print-pack logic that can silently
lie: which invoice line a picking mark lands on, and which stops are dropped
from the pack. Run it after touching annotate.py or route_pack.py:

    python3 test_route_pack.py        # prints "N/N ok" or raises
"""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fitz
import annotate
import route_pack

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# Four catalogue lines, three of them sharing the "בסיס לימונדה" prefix — the
# exact shape that made the old two-word fallback stamp the wrong line.
LINES = [
    "בסיס לימונדה נענע 1 ליטר",
    "בסיס לימונדה תות 1 ליטר",
    "בסיס לימונדה 1 ליטר",
    "סירופ ג'ינג'ר 700 מל",
    "סה\"כ לתשלום 486.00 ₪",
]


def _invoice(lines, reverse_words=False):
    """A stand-in Green Invoice PDF. reverse_words=True mimics the GI exports
    whose Hebrew comes out of the text layer visually reversed."""
    doc = fitz.open()
    pg = doc.new_page(width=595, height=842)
    pg.insert_font(fontname="dj", fontfile=FONT)
    for i, ln in enumerate(lines):
        text = " ".join(w[::-1] for w in ln.split()) if reverse_words else ln
        pg.insert_text((60, 200 + i * 24), text, fontname="dj", fontsize=11)
    path = os.path.join(tempfile.mkdtemp(), "inv.pdf")
    doc.save(path)
    doc.close()
    return path


def _y_of(row):
    return 200 + row * 24


def _stop(recipient="", notes="", gi=None, items=None, driver_note=None):
    return {"tid": "1", "do": 1, "recipient": recipient, "gi": gi,
            "task": {"notes": notes, "driver_note": driver_note,
                     "order_items": items or []}}


CHECKS = []


def check(name, cond):
    CHECKS.append(name)
    assert cond, f"FAILED: {name}"


def main():
    doc = fitz.open(_invoice(LINES))

    # --- the mark lands on the right line ---------------------------------- #
    hit = annotate._find_line(doc, "בסיס לימונדה תות 1 ליטר", set())
    check("distinguishing word wins over a shared prefix",
          hit and abs(hit[1] - _y_of(1)) < 12)

    hit = annotate._find_line(doc, "בסיס לימונדה נענע 1 ליטר", set())
    check("the sibling flavour matches its own line",
          hit and abs(hit[1] - _y_of(0)) < 12)

    # --- refuse rather than guess ------------------------------------------ #
    check("a flavour that is not on the invoice never lands on a sibling line",
          annotate._find_line(doc, "בסיס לימונדה אשכוליות 1 ליטר", set()) is None)
    check("agreement on generic words alone is not a match",
          annotate._find_line(doc, "בסיס לימונדה 1 ליטר", set()) is None)
    check("a product absent from the invoice is unmatched",
          annotate._find_line(doc, "מיץ אשכוליות 250 מל", set()) is None)
    twin = fitz.open(_invoice(["מיץ תפוזים 1 ליטר", "מיץ תפוזים 1 ליטר"]))
    check("two indistinguishable lines are reported, never stamped at random",
          annotate._find_line(twin, "מיץ תפוזים 1 ליטר", set()) is None)
    sized = fitz.open(_invoice(["מיץ תפוזים 1 ליטר", "מיץ תפוזים 2 ליטר"]))
    hit = annotate._find_line(sized, "מיץ תפוזים 2 ליטר", set())
    check("size digits keep 2 ליטר off the 1 ליטר line",
          hit and abs(hit[1] - _y_of(1)) < 12)

    # --- wording drift between LionWheel and Green Invoice ------------------ #
    hit = annotate._find_line(doc, 'סירופ ג׳ינג׳ר 700 מ"ל', set())
    check("geresh/quote variants still match the same line",
          hit and abs(hit[1] - _y_of(3)) < 12)

    # --- one line carries one mark ----------------------------------------- #
    used = set()
    annotate._find_line(doc, "בסיס לימונדה תות 1 ליטר", used)
    check("a line already marked is not marked twice",
          annotate._find_line(doc, "בסיס לימונדה תות 1 ליטר", used) is None)

    # --- visually reversed text layer -------------------------------------- #
    rdoc = fitz.open(_invoice(LINES, reverse_words=True))
    hit = annotate._find_line(rdoc, "בסיס לימונדה תות 1 ליטר", set())
    check("a reversed-extraction invoice still matches",
          hit and abs(hit[1] - _y_of(1)) < 12)

    # --- annotate() reports what it could not mark -------------------------- #
    task = {"wp_order_id": "#GT13483", "packages_quantity": 3, "order_items": [
        {"name": "בסיס לימונדה תות 1 ליטר", "quantity": 6, "picked_quantity": 2},
        {"name": "מיץ אשכוליות 250 מל", "quantity": 4, "picked_quantity": 0},
        {"name": "בסיס לימונדה נענע 1 ליטר", "quantity": 3, "picked_quantity": 3},
    ]}
    out = os.path.join(tempfile.mkdtemp(), "ann.pdf")
    missed = annotate.annotate(task, _invoice(LINES), out, shortfall_only=True)
    check("the shortfall that cannot be placed is handed back",
          missed == ["מיץ אשכוליות 250 מל"])
    check("the annotated invoice is written", os.path.getsize(out) > 0)

    # --- check collections leave the pack, deliveries never do -------------- #
    cp = route_pack.is_check_pickup
    check("a check errand is dropped",
          cp(_stop(recipient="איסוף צ'קים — קפה ליבה")))
    check("the geresh variant is dropped too",
          cp(_stop(recipient="איסוף צ׳קים", notes="")))
    check("the formal wording is dropped too",
          cp(_stop(notes="לאסוף המחאות מהלקוח")))
    check("a delivery to a customer named like a check is KEPT",
          not cp(_stop(recipient="צ'ק פוינט קפה",
                       items=[{"name": "בסיס לימונדה תות 1 ליטר"}])))
    check("a check note on a stop that has an invoice is KEPT",
          not cp(_stop(recipient="איסוף צ'קים", gi="https://greeninvoice.co.il/x")))
    check("a goods pickup is not a check pickup",
          not cp(_stop(recipient="לקוח", notes="איסוף סחורה")))
    check("an ordinary delivery is untouched",
          not cp(_stop(recipient="קפה נמרוד", notes="")))

    # --- marks are never built on picking that was not reported ------------- #
    pr = route_pack.picking_recorded
    unreported = [_stop(items=[{"name": "x", "quantity": 6, "picked_quantity": 0},
                               {"name": "y", "quantity": 3, "picked_quantity": None}])]
    check("a route with nothing picked anywhere is treated as unreported",
          not pr(unreported))
    check("one recorded pick is enough to trust the numbers",
          pr(unreported + [_stop(items=[{"name": "z", "quantity": 2,
                                         "picked_quantity": 2}])]))

    print(f"{len(CHECKS)}/{len(CHECKS)} ok")


if __name__ == "__main__":
    main()
