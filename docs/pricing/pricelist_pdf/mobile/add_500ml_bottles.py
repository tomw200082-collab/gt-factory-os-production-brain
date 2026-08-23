"""Stand a 500 ml bottle beside the 1 L bottle in every tea row of the mobile pricelist.

The 1 L bottles are already placed absolutely — one `w 0 0 -h x y cm … /Xnn Do`
per row — so the 500 ml sibling is expressed entirely as a ratio of that box and
inherits whatever CTM the row sits in. Height is 72% of the litre bottle (their
real-world ratio), width follows each cutout's own aspect, and the pair is
bottom-aligned so they stand on the same line.

Row -> cutout was matched by eye off the labels, not by colour distance: the
nearest-colour match had margins of 3-9 units between first and second place on
the FRESH/DETOX pairs, which is noise.
"""

import io
import re

from PIL import Image
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (DecodedStreamObject, DictionaryObject, NameObject,
                           NumberObject)

SRC = "step1_no_unit_prices.pdf"
OUT = "GT_pricelist_mobile_v2.pdf"

# Page -> the flavours in row order, top to bottom, each with its cutout.
# Cutouts come from Canva design DAHR5IzII6w ("all 500ml bottles no background"),
# exported as transparent PNG and trimmed to the bottle.
ROWS = {
    2: [("FRESH", "fresh"), ("FRESH ללא סוכר", "fresh-no-sugar"), ("DETOX", "detox"),
        ("DETOX ללא סוכר", "detox-no-sugar"), ("ENERGY", "energy")],
    3: [("CALM", "calm"), ("CONSCIOUSNESS", "consciousness"), ("REVIVE", "revive"),
        ("DESERTEA", "desertea"), ("NAMASTEA", "namastea"), ("AMERICAN", "american")],
}

HEIGHT_RATIO = 0.72   # 500 ml bottle height as a fraction of the litre bottle
GAP = 10.0            # placement units between the two bottles
PX_PER_UNIT = 1.432   # matches the existing bottles (94 px across a 65.625-unit box)

PLACE = re.compile(
    r"([\d.]+) 0 0 (-[\d.]+) ([\d.]+) ([\d.]+) cm\n[^\n]*\n/(\w+) gs\n/(X\d+) Do"
)


def paper_colour(img):
    """The flat paper the cutouts are composited onto — read off a litre bottle's corner."""
    return img.convert("RGB").getpixel((0, 0))


def jpeg_xobject(path, colour, width_px):
    cut = Image.open(path).convert("RGBA")
    height_px = round(width_px * cut.height / cut.width)
    cut = cut.resize((width_px, height_px), Image.LANCZOS)
    flat = Image.new("RGB", cut.size, colour)
    flat.paste(cut, mask=cut.split()[3])
    buf = io.BytesIO()
    flat.save(buf, "JPEG", quality=88, optimize=True)
    stream = DecodedStreamObject()
    stream.set_data(buf.getvalue())
    stream[NameObject("/Type")] = NameObject("/XObject")
    stream[NameObject("/Subtype")] = NameObject("/Image")
    stream[NameObject("/Width")] = NumberObject(width_px)
    stream[NameObject("/Height")] = NumberObject(height_px)
    stream[NameObject("/ColorSpace")] = NameObject("/DeviceRGB")
    stream[NameObject("/BitsPerComponent")] = NumberObject(8)
    stream[NameObject("/Filter")] = NameObject("/DCTDecode")
    return stream, cut.width / cut.height


writer = PdfWriter(clone_from=SRC)
reader = PdfReader(SRC)
report = []

for page_number, rows in ROWS.items():
    page = writer.pages[page_number - 1]
    stream = page.get_contents().get_data().decode("latin-1")
    sizes = {im.name.rsplit(".", 1)[0]: im.image for im in reader.pages[page_number - 1].images}

    placements = sorted(
        (float(m.group(4)), m.start(), m.end(), float(m.group(1)), float(m.group(2)),
         float(m.group(3)), m.group(5), m.group(6))
        for m in PLACE.finditer(stream)
        if m.group(6) in sizes and sizes[m.group(6)].size[0] < 200
    )
    assert len(placements) == len(rows), (page_number, len(placements))

    resources = page["/Resources"]
    xobjects = resources[NameObject("/XObject")]
    if not isinstance(xobjects, DictionaryObject):
        xobjects = xobjects.get_object()

    inserts = []
    for (y, start, end, w, h, x, gs, name), (flavour, cutout) in zip(placements, rows):
        h = -h
        colour = paper_colour(sizes[name])
        new_h = h * HEIGHT_RATIO
        cutout_path = f"cutouts_500ml/{cutout}.png"
        probe = Image.open(cutout_path)
        new_w = new_h * probe.width / probe.height
        obj, _ = jpeg_xobject(cutout_path, colour, max(24, round(new_w * PX_PER_UNIT)))

        ref = writer._add_object(obj)
        new_name = f"X500_{page_number}_{cutout.replace(chr(45), chr(95))}"
        xobjects[NameObject("/" + new_name)] = ref

        # `w 0 0 -h x y cm` puts the image's foot at y and its shoulder at y-h,
        # so sharing y is what stands the two bottles on the same line.
        new_x = x - GAP - new_w
        new_y = y
        op = (f"\nQ\nq\n{new_w:.5f} 0 0 {-new_h:.5f} {new_x:.5f} {new_y:.5f} cm\n"
              f"0 0 0 RG 0 0 0 rg\n/{gs} gs\n/{new_name} Do")
        inserts.append((end, op))
        report.append(f"p{page_number} {flavour:16s} 500ml={cutout:16s} "
                      f"box {new_w:.1f}x{new_h:.1f} at x={new_x:.1f} (litre x={x:.1f})")

    for at, op in sorted(inserts, reverse=True):
        stream = stream[:at] + op + stream[at:]

    content = DecodedStreamObject()
    content.set_data(stream.encode("latin-1"))
    page.replace_contents(content)

writer.compress_identical_objects()
writer.write(OUT)
print("\n".join(report))
