#!/usr/bin/env python3
"""
D1, D4, D5, D6, D7, D8 — prove the built PDF and page satisfy the conditions.

    python3 verify.py --geometry     D1  page count and 9:16 MediaBox
    python3 verify.py --type-scale   D4  nothing readable is below 36px
    python3 verify.py --no-wholesale D5+D6  no wholesale price, no dead product
    python3 verify.py --offline      D7  no network reference, only Rubik/Heebo
    python3 verify.py --closing      D8  S15 leads with the promise
    python3 verify.py --all          every check; exits non-zero on any failure
"""
import re, sys, zlib
from pathlib import Path

D = Path(__file__).parent
PDF = D / "lead-menu.pdf"
PAGE = D / "lead-menu.html"

WHOLESALE = ["₪65", "₪33", "₪590", "₪375", "₪340", "₪175", "₪170", "₪118",
             "₪60", "₪37", "₪36", "₪30", "₪25", "₪20", "₪11", "₪10"]
DEAD = ["GT Elita", "מאצ׳ה 50", "מאצ'ה 50", "מקציף קוקטיילים", "קנקן נפוליטן"]
FLOOR = 36


# ---------------------------------------------------------------- PDF helpers
def streams(b):
    """Every stream in the file, inflated where it is FlateDecode."""
    out = []
    for m in re.finditer(rb"stream\r?\n", b):
        s = m.end()
        e = b.find(b"endstream", s)
        if e < 0:
            continue
        raw = b[s:e].rstrip(b"\r\n")
        try:
            out.append(zlib.decompress(raw))
        except zlib.error:
            out.append(raw)
    return out


def cmaps(chunks):
    """Per-font code->unicode maps parsed from every ToUnicode CMap."""
    maps = []
    for c in chunks:
        if b"beginbfchar" not in c and b"beginbfrange" not in c:
            continue
        m = {}
        for blk in re.findall(rb"beginbfchar(.*?)endbfchar", c, re.S):
            for src, dst in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", blk):
                m[int(src, 16)] = "".join(chr(int(dst[i:i + 4], 16))
                                          for i in range(0, len(dst), 4))
        for blk in re.findall(rb"beginbfrange(.*?)endbfrange", c, re.S):
            for lo, hi, dst in re.findall(
                    rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", blk):
                base = int(dst, 16)
                for i in range(int(lo, 16), int(hi, 16) + 1):
                    m[i] = chr(base + i - int(lo, 16))
        if m:
            maps.append(m)
    return maps


def pdf_text(chunks, maps):
    """Every text-showing string, decoded through each font map in turn.
    Decoding under every map is deliberate: for a gate that must find ZERO
    forbidden strings, over-decoding risks a false alarm, never a miss."""
    codes = []
    for c in chunks:
        if b"TJ" not in c and b"Tj" not in c:
            continue
        for s in re.findall(rb"<([0-9A-Fa-f\s]+)>\s*(?:Tj|TJ|\])", c):
            h = re.sub(rb"\s", b"", s)
            codes.append([int(h[i:i + 4], 16) for i in range(0, len(h) - 3, 4)])
    texts = []
    for m in maps:
        texts.append("".join("".join(m.get(c, "�") for c in run) for run in codes))
    return texts


def html_text():
    body = PAGE.read_text(encoding="utf-8").split("</style>", 1)[1]
    return re.sub(r"<[^>]+>", " ", body)


# ------------------------------------------------------------------- D1
def geometry():
    b = PDF.read_bytes()
    pages = len(re.findall(rb"/Type\s*/Page(?![s])", b))   # (?![s]) — /Pages is the tree node
    mb = re.search(rb"/MediaBox\s*\[\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", b)
    w, h = float(mb.group(3)), float(mb.group(4))
    r = w / h
    print(f"pages {pages}")
    print(f"MediaBox {w} x {h} pt")
    print(f"ratio {r:.4f}")
    print(f"bytes {len(b)}  (WhatsApp limit 4194304)")
    ok = pages == 15 and abs(r - 0.5625) <= 0.001 and len(b) <= 4194304
    return ok


# ------------------------------------------------------------------- D4
def type_scale():
    html = PAGE.read_text(encoding="utf-8")
    css = html.split("<style>", 1)[1].split("</style>", 1)[0]
    sizes = []
    for rule in re.finditer(r"([^{}]+)\{([^}]*)\}", css):
        sel, body = rule.group(1).strip(), rule.group(2)
        for fs in re.findall(r"font-size:\s*(\d+(?:\.\d+)?)px", body):
            sizes.append((float(fs), sel, "legal" in sel))
    for m in re.finditer(r'<([a-z]+)([^>]*?)style="([^"]*font-size:\s*(\d+(?:\.\d+)?)px[^"]*)"', html):
        attrs, size = m.group(2) + m.group(3), float(m.group(4))
        sizes.append((size, f"inline <{m.group(1)}>", "legal" in attrs))
    content = [(s, sel) for s, sel, is_legal in sizes if not is_legal]
    legal = [(s, sel) for s, sel, is_legal in sizes if is_legal]
    lo = min(content)
    print(f"declarations scanned {len(sizes)}  (content {len(content)}, .legal {len(legal)})")
    print(f"min content font-size {lo[0]:.0f}px   [{lo[1]}]")
    print(f"min .legal font-size {min(legal)[0]:.0f}px   [exempt by D4]")
    for s, sel in sorted(content)[:3]:
        print(f"  smallest content sizes: {s:.0f}px  {sel}")
    return lo[0] >= FLOOR


# --------------------------------------------------------------- D5 and D6
def no_wholesale():
    chunks = streams(PDF.read_bytes())
    maps = cmaps(chunks)
    layers = pdf_text(chunks, maps)
    hay = html_text()
    print(f"PDF font maps parsed {len(maps)}; text layer decoded under each")
    hits = []
    for term in WHOLESALE:
        # a wholesale price must not appear as a standalone figure
        if re.search(re.escape(term) + r"(?!\d)", hay):
            hits.append(("html", term))
        for i, t in enumerate(layers):
            if re.search(re.escape(term) + r"(?!\d)", t):
                hits.append((f"pdf-font{i}", term))
    dead_hits = []
    for term in DEAD:
        if term in hay:
            dead_hits.append(("html", term))
        for i, t in enumerate(layers):
            if term in t:
                dead_hits.append((f"pdf-font{i}", term))
    for where, t in hits + dead_hits:
        print(f"  HIT {t!r} in {where}")
    print(f"wholesale prices checked {len(WHOLESALE)} -> matches {len(hits)}")
    print(f"discontinued products checked {len(DEAD)} -> matches {len(dead_hits)}")
    return not hits and not dead_hits


# ------------------------------------------------------------------- D7
def offline():
    html = PAGE.read_text(encoding="utf-8")
    net = re.findall(r"https?://[^\s\"')]+", html)
    fonts = sorted({f.decode() for f in
                    re.findall(rb"/BaseFont\s*/([A-Za-z0-9+\-]+)", PDF.read_bytes())})
    bad = [f for f in fonts if not re.match(r"^[A-Z]{6}\+(Rubik|Heebo)", f)]
    print(f"network references in the page: {len(net)}  {net[:3]}")
    print(f"embedded faces: {fonts}")
    print(f"faces outside Rubik*/Heebo*: {bad or 'none'}")
    return not net and not bad


# ------------------------------------------------------------------- D8
def closing():
    html = PAGE.read_text(encoding="utf-8")
    css = html.split("<style>", 1)[1].split("</style>", 1)[0]

    def size_of(cls):
        m = re.search(r"\." + cls + r"\s*\{[^}]*font-size:\s*(\d+(?:\.\d+)?)px", css)
        return float(m.group(1)) if m else None

    s15 = re.findall(r'<section class="screen close".*?</section>', html, re.S)[0]
    classes = set(re.findall(r'class="([^"]+)"', s15))
    inline = [float(x) for x in re.findall(r"font-size:\s*(\d+(?:\.\d+)?)px", s15)]
    sized = {c: size_of(c) for c in
             {x for cl in classes for x in cl.split()} if size_of(c)}
    promise = sized.get("promise")
    contact = sized.get("contact")
    body = size_of("body")
    largest = max(list(sized.values()) + inline)
    i_p, i_c = s15.find('class="promise"'), s15.find('class="contact"')
    print(f"S15 sized elements: {sorted(sized.items(), key=lambda kv: -kv[1])}")
    print(f"largest on S15 {largest:.0f}px · promise {promise:.0f}px · "
          f"contact {contact:.0f}px · body scale {body:.0f}px")
    print(f"document order: promise at {i_p}, contact at {i_c} -> "
          f"{'promise first' if i_p < i_c else 'CONTACT FIRST'}")
    return (promise == largest) and (contact <= body) and (0 <= i_p < i_c)


CHECKS = {"--geometry": ("D1", geometry), "--type-scale": ("D4", type_scale),
          "--no-wholesale": ("D5+D6", no_wholesale), "--offline": ("D7", offline),
          "--closing": ("D8", closing)}

if __name__ == "__main__":
    args = sys.argv[1:] or ["--all"]
    todo = list(CHECKS) if args == ["--all"] else args
    bad = 0
    for a in todo:
        cond, fn = CHECKS[a]
        print(f"\n=== {cond}  {a} ===")
        ok = fn()
        print(f"--> {cond} {'PASS' if ok else 'FAIL'}")
        bad += not ok
    sys.exit(1 if bad else 0)
