#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rollback tooling for the Canva drinks catalog DAHTYkRvEnM.

Canva exposes no undo through the MCP API. The only rollback that exists after
the first write is the one captured before it. This script owns both halves of
that: emitting the restore operations, and proving that nothing outside the
in-scope elements moved.

    canva_catalog_backup.py --emit-restore [BACKUP] [--figures FIGURES]
        Print the ordered edit-design operations that put every original string
        back. find_and_replace_text for the drink-page money elements (they
        carry two textRegions and replace_text would flatten the shekel sign),
        replace_text for the three summary-table columns. The digits currently
        on the page are read from the figures file, so the operations are
        runnable as printed.

    canva_catalog_backup.py --verify BEFORE.json AFTER.json
        Diff two raw structured dumps element by element and report every
        element whose characters differ.

Elements are re-located by content pattern and font size, never by a stored id:
Canva element ids are per session and are not stable between them.
"""
import argparse
import json
import re
import sys

DESIGN_ID = "DAHTYkRvEnM"

COST_RE = re.compile(r"^₪\d+\.\d\d$")
PRICE_RE = re.compile(r"^₪\d+$")
MARGIN_RE = re.compile(r"^\d\d%$")
FS_LO, FS_HI = 40, 80

DIVIDERS = {2, 10, 14, 19, 23, 30, 36, 42, 49, 54}
COVER, SUMMARY = 1, 60
DRINK_PAGES = [n for n in range(1, 61) if n not in DIVIDERS and n not in (COVER, SUMMARY)]

FIGURE_KEYS = ([8, 9, 10, 11, 12, 13, 14] + [16, 17, 18] + [20, 21, 22, 23]
               + [25, 26, 27] + [29, 30, 31, 32, 33, 34] + [36, 37, 38, 39, 40]
               + [42, 43, 44, 45, 46] + [48, 49, 50, 51, 52, 53] + [55, 56, 57, 58]
               + [60, 61, 62, 63, 64])
PAGE_MAP = dict(zip(DRINK_PAGES, FIGURE_KEYS))

# Group sizes of the summary table, in family order. Sums to 48.
GROUPS = [7, 3, 4, 3, 6, 5, 5, 6, 4, 5]


def text_of(element):
    return "".join(r.get("characters", "") for r in element.get("textRegions", []))


def font_size(element):
    regions = element.get("textRegions") or [{}]
    return regions[0].get("formatting", {}).get("fontSize") or 0


def figure_elements(page):
    """Match the three figure elements on a drink page by content and font size.

    The cost element stores '₪' and the digits as separate textRegions, so the
    regions are concatenated before the pattern is applied. Font size is banded
    rather than compared for equality: the money elements measure 48.0002 and
    the margin 50.6668, and sibling pages vary in the last decimals.
    """
    found = {}
    for element in page["elements"]:
        if element.get("type") != "text":
            continue
        text, size = text_of(element).strip(), font_size(element)
        if not FS_LO <= size <= FS_HI:
            continue
        for field, pattern in (("cost", COST_RE), ("price", PRICE_RE), ("margin", MARGIN_RE)):
            if pattern.match(text):
                found.setdefault(field, []).append(element)
    return found


def summary_columns(page):
    """The four table-body elements on page 60, keyed by what they hold."""
    columns = [e for e in page["elements"]
               if e.get("type") == "text" and text_of(e).count("\n") >= 40]
    out = {}
    for element in columns:
        text = text_of(element)
        if COST_RE.match(text.split("\n")[1].rstrip("*")):
            out["cost"] = element
        elif PRICE_RE.match(text.split("\n")[1]):
            out["price"] = element
        elif MARGIN_RE.match(text.split("\n")[1]):
            out["margin"] = element
        else:
            out["names"] = element
    return out


def column(values):
    """Rebuild one summary column exactly as page 60 stores it."""
    out, i = [], 0
    for n in GROUPS:
        out.append("\n".join(values[i:i + n]))
        i += n
    return "\n" + "\n\n".join(out)


def emit_restore(backup, figures):
    """Ordered edit-design operations that restore the captured state.

    `figures` is the approved-figures file: what the page says now. Its digits
    become find_text, the backup's become replace_text.
    """
    operations = []
    for page_number, record in sorted(backup["drink_pages"].items(), key=lambda kv: int(kv[0])):
        current = figures["pages"][str(record["figures_page"])]
        for field, key in (("cost", "cost"), ("price", "price")):
            entry = record[field]
            operations.append({
                "page_index": int(page_number),
                "type": "find_and_replace_text",
                "locator_id": entry["element"],
                # digits only: replace_text would collapse the two textRegions
                "find_text": current[key].lstrip("₪").rstrip("*"),
                "replace_text": entry["text"].lstrip("₪"),
            })
        operations.append({
            "page_index": int(page_number),
            "type": "replace_text",
            "locator_id": record["margin"]["element"],
            "text": record["margin"]["text"],
        })
    for name, entry in backup["summary_page"]["columns"].items():
        if name == "names":
            continue  # read-only column, never written
        operations.append({
            "page_index": backup["summary_page"]["page_index"],
            "type": "replace_text",
            "locator_id": entry["element"],
            "text": entry["text"],
        })
    return operations


def verify(before_path, after_path):
    """Report every element whose characters differ between two raw dumps."""
    before = json.load(open(before_path, encoding="utf-8"))["design_content"]["pages"]
    after = json.load(open(after_path, encoding="utf-8"))["design_content"]["pages"]
    if len(before) != len(after):
        print("PAGE COUNT CHANGED: %d -> %d" % (len(before), len(after)))
        return 1

    differences = []
    for index, (page_before, page_after) in enumerate(zip(before, after), start=1):
        texts_before = {e["id"]: text_of(e) for e in page_before["elements"] if e.get("type") == "text"}
        texts_after = {e["id"]: text_of(e) for e in page_after["elements"] if e.get("type") == "text"}
        if set(texts_before) != set(texts_after):
            differences.append((index, "ELEMENT SET CHANGED", "", ""))
            continue
        for element_id, text in texts_before.items():
            if texts_after[element_id] != text:
                differences.append((index, element_id, text, texts_after[element_id]))

    for index, element_id, was, now in differences:
        print("page %2d  %s  %r -> %r" % (index, element_id, was, now))
    print("differing elements: %d" % len(differences))
    return differences


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--emit-restore", nargs="?", const="docs/pricing/backups/"
                        "2026-08-26_DAHTYkRvEnM_pre-repricing.json", metavar="BACKUP")
    parser.add_argument("--verify", nargs=2, metavar=("BEFORE", "AFTER"))
    parser.add_argument("--figures", default=".claude/skills/drinks-pricelist/"
                        "drinks_final_figures.json", metavar="FIGURES")
    args = parser.parse_args()

    if args.verify:
        verify(*args.verify)
    elif args.emit_restore:
        backup = json.load(open(args.emit_restore, encoding="utf-8"))
        figures = json.load(open(args.figures, encoding="utf-8"))
        print(json.dumps(emit_restore(backup, figures), ensure_ascii=False, indent=2))
    else:
        parser.print_help()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
