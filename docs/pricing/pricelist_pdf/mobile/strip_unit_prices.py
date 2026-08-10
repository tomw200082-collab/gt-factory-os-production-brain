"""Remove the per-cup / per-serving prices from the mobile pricelist PDF.

Tom, 2026-08-10: the mobile pricelist must not print a unit price per drink.

The mobile PDF has no build source in this repo, so the removal is done on the
PDF itself. That is safe here because Chrome laid every glyph out absolutely:
each text run is its own `BT ... ET` block with an explicit `Tm`, so dropping a
run moves nothing else on the page.

Three things come out:

  pages 2-3   "₪2.60-3.25 לכוס"  and the "·" that separated it from the
              "20-25 כוסות מבקבוק ליטר" line it shared a row with
  page 4      "₪2.12 למנה" and the four other per-serving prices

Everything else stays, including the cups-per-bottle line and the serving-size
line at the top of page 4 ("מנת מאצ'ה והודג'יצ'ה 1.8 גרם · מנת אובה 2 גרם"),
which describes the product rather than its price.

The rows are right-aligned (verified against the render: the per-cup row and the
bottle-price row above it both end at the same right margin), and the removed
text sits at the left end of each row, so nothing needs re-centring afterwards.

    python3 strip_unit_prices.py in.pdf out.pdf

Verification: 8 pages in, 8 out; pages 1 and 5-8 render pixel-identical to the
input at 100 dpi, pages 2-4 carry only the removals above.
"""

import re
import sys

from pypdf import PdfReader, PdfWriter
from pypdf.generic import DecodedStreamObject

# The labels as they sit in the content stream. These pages are marked
# /ReversedChars, so the glyphs are stored in visual order — לכוס reads back
# as 'סוכל ' and למנה as 'הנמל '.
LABEL_PER_CUP = "סוכל "
LABEL_PER_SERVING = "הנמל "

PRICE = re.compile(r"^[\d.]+(–[\d.]+)?$")
TEXT_BLOCK = re.compile(r"BT\n.*?\nET", re.S)

# A run's opening: font, then the Tm that places it, then its first three
# glyphs — enough to drop the leading " · " and re-place what follows.
RUN_HEAD = re.compile(
    r"(BT\n(?:/\w+ BMC\n)?/\w+ [\d.]+ Tf\n1 0 0 -1 )([\d.]+)( [\d.]+ Tm\n)"
    r"<\w{4}> Tj\n([\d.]+) 0 Td <\w{4}> Tj\n([\d.]+) 0 Td <\w{4}> Tj\n([\d.]+) 0 Td "
)


def to_unicode_maps(page):
    """glyph code -> character, per font on the page."""
    maps = {}
    fonts = page["/Resources"].get("/Font")
    if not fonts:
        return maps
    for name, ref in fonts.get_object().items():
        cmap = {}
        to_unicode = ref.get_object().get("/ToUnicode")
        if to_unicode is not None:
            data = to_unicode.get_object().get_data().decode("latin-1")
            for section in re.finditer(r"beginbfchar(.*?)endbfchar", data, re.S):
                for src, dst in re.findall(r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", section.group(1)):
                    cmap[int(src, 16)] = "".join(
                        chr(int(dst[i : i + 4], 16)) for i in range(0, len(dst), 4)
                    )
            for section in re.finditer(r"beginbfrange(.*?)endbfrange", data, re.S):
                for lo, hi, dst in re.findall(
                    r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", section.group(1)
                ):
                    lo, hi, base = int(lo, 16), int(hi, 16), int(dst, 16)
                    for code in range(lo, hi + 1):
                        cmap[code] = chr(base + code - lo)
        maps[name] = cmap
    return maps


def read_block(block, maps):
    """The text a BT...ET block draws."""
    font, text = None, ""
    for token in re.finditer(r"/(\w+)\s+[\d.]+\s+Tf|<([0-9A-Fa-f]+)>\s*Tj", block):
        if token.group(1):
            font = "/" + token.group(1)
        else:
            glyphs = token.group(2)
            for i in range(0, len(glyphs), 4):
                text += maps.get(font, {}).get(int(glyphs[i : i + 4], 16), "?")
    return text


def strip(src, out):
    writer = PdfWriter(clone_from=src)
    removed = []

    for number, page in enumerate(writer.pages, 1):
        maps = to_unicode_maps(page)
        stream = page.get_contents().get_data().decode("latin-1")
        blocks = [(m.start(), m.end(), m.group(0)) for m in TEXT_BLOCK.finditer(stream)]
        texts = [read_block(b, maps) for _, _, b in blocks]

        edits = []
        i = 0
        while i < len(blocks):
            label = texts[i]
            if label not in (LABEL_PER_CUP, LABEL_PER_SERVING):
                i += 1
                continue

            # The label is always followed by its ₪ mark and then the figure.
            assert texts[i + 1] == "₪", (number, i, texts[i + 1])
            assert PRICE.match(texts[i + 2]), (number, i, texts[i + 2])
            for k in (i, i + 1, i + 2):
                edits.append((blocks[k][0], blocks[k][1], ""))
            removed.append(f"p{number}: {label.strip()[::-1]} ₪{texts[i + 2]}")

            if label == LABEL_PER_CUP:
                # The cups-per-bottle run that shares the row opens with " · ";
                # drop those three glyphs and start the run where the ר begins.
                start, end, block = blocks[i + 3]
                assert texts[i + 3].startswith(" · "), (number, texts[i + 3])
                head = RUN_HEAD.match(block)
                assert head, block[:200]
                x = sum(float(head.group(g)) for g in (2, 4, 5, 6))
                edits.append(
                    (start, end, head.group(1) + f"{x:.7f}" + head.group(3) + block[head.end() :])
                )
                removed.append(f"p{number}: separator, run starts {head.group(2)} -> {x:.4f}")

            i += 3

        if edits:
            for start, end, replacement in sorted(edits, reverse=True):
                stream = stream[:start] + replacement + stream[end:]
            content = DecodedStreamObject()
            content.set_data(stream.encode("latin-1"))
            page.replace_contents(content)
        page.compress_content_streams()

    writer.compress_identical_objects()
    writer.write(out)
    return removed


if __name__ == "__main__":
    source, target = sys.argv[1], sys.argv[2]
    for line in strip(source, target):
        print(line)
    print(f"pages: {len(PdfReader(target).pages)}")
