#!/usr/bin/env python3
"""
route-print-pack — build the daily delivery print pack for ONE driver + date.

Input (the only things a human supplies): --driver "<name>"  --date YYYY-MM-DD
Optional: --from-stop N (only when explicitly requested).

Everything else is default and automatic:
  page 1   : LionWheel work order (daily_route_plan), fitted to one A4 portrait
  then     : every stop in driving order (visits.daily_order)
               - stop with a Green Invoice  -> real GI invoice, annotated, x2 copies
               - stop without an invoice     -> official LionWheel waybill, x2 copies
  marks    : per line V / X / partial (see annotate.py); package count under "מקור";
             last-3 order-id digits top-right
  output   : one merged print-ready PDF
  side car : non-standard inventory movements (returns / exchanges / tastings /
             goods received) written to route_pack_out/inventory_proposals.json
             -> SKILL.md posts these to the Factory OS `exceptions` inbox; stock
                moves ONLY after approval. The skill never touches stock_ledger.
  email    : the SKILL.md emails the final PDF + short summary to
             production@gteveryday.com (Resend).

Secrets (env): LIONWHEEL_API_KEY, LIONWHEEL_BASE_URL, GREENINVOICE_API_BASE_URL,
GREENINVOICE_KEY_ID, GREENINVOICE_SECRET, LIONWHEEL_WEB_USER, LIONWHEEL_WEB_PASSWORD,
RESEND_API_KEY. The two LIONWHEEL_WEB_* must be stored as environment secrets
(needed for waybills + work order). Never hard-code them.
"""
import os, re, sys, json, argparse, datetime, http.cookiejar, urllib.request, urllib.parse

OUT = "route_pack_out"
LW_BASE = os.environ.get("LIONWHEEL_BASE_URL", "https://members.lionwheel.com").rstrip("/")
LW_KEY = os.environ.get("LIONWHEEL_API_KEY", "")
GI_BASE = os.environ.get("GREENINVOICE_API_BASE_URL", "https://api.greeninvoice.co.il/api/v1/")
GI_ID = os.environ.get("GREENINVOICE_KEY_ID", "")
GI_SECRET = os.environ.get("GREENINVOICE_SECRET", "")


# --------------------------------------------------------------------------- #
# small http helpers (stdlib only, so the script has no hard deps to fetch)
# LionWheel's edge blocks the default urllib User-Agent, so send a browser one.
# --------------------------------------------------------------------------- #
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def _get(url, headers=None):
    h = {"User-Agent": UA, "Accept": "application/json,*/*"}
    h.update(headers or {})
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def _get_json(url):
    return json.loads(_get(url).decode("utf-8"))


def _post_json(url, payload, headers=None):
    data = json.dumps(payload).encode("utf-8")
    h = {"Content-Type": "application/json", "User-Agent": UA}
    h.update(headers or {})
    req = urllib.request.Request(url, data=data, headers=h, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


# --------------------------------------------------------------------------- #
# LionWheel REST (route + picked quantities + invoice links)
# --------------------------------------------------------------------------- #
def lw_list_assigned():
    url = f"{LW_BASE}/api/v1/tasks.json?key={urllib.parse.quote(LW_KEY)}&limit=1000"
    d = _get_json(url)
    tasks = d.get("tasks", d) if isinstance(d, dict) else d
    return [t["id"] for t in tasks if t.get("status") == "ASSIGNED"]


def lw_task(tid):
    url = f"{LW_BASE}/api/v1/tasks/show/{tid}.json?key={urllib.parse.quote(LW_KEY)}"
    return _get_json(url).get("task")


def gi_link(task):
    for s in (task.get("driver_note"), task.get("notes")):
        if isinstance(s, str) and "greeninvoice.co.il" in s:
            m = re.search(r"https://\S+greeninvoice\.co\.il/\S+", s)
            if m:
                return m.group(0)
    return None


def fetch_route(driver, date):
    """Return (driver_id, [stop,...]) sorted by daily_order for driver+date."""
    stops, driver_id = [], None
    for tid in lw_list_assigned():
        t = lw_task(tid)
        if not t:
            continue
        if t.get("driver_str") != driver:
            continue
        if not (t.get("pickup_at") or "").startswith(date):
            continue
        if t.get("status") != "ASSIGNED":
            continue
        v = (t.get("visits") or [{}])[0]
        # Skip stops the driver has ALREADY completed: LionWheel marks the visit
        # done via is_done / delivered_at (task.status stays ASSIGNED all day, so it
        # cannot be the signal). Only stops still pending belong on the new route.
        if v.get("is_done") or v.get("delivered_at"):
            continue
        driver_id = driver_id or t.get("driver_id")
        eta = (v.get("eta_at") or "")[11:16]
        stops.append({
            "tid": str(t["id"]),
            "do": v.get("daily_order"),
            "eta": eta,
            "recipient": v.get("recipient_name"),
            "city": v.get("city"),
            "wp": t.get("wp_order_id"),
            "packages": t.get("packages_quantity"),
            "items": len(t.get("order_items") or []),
            "gi": gi_link(t),
            "task": t,
        })
    stops.sort(key=lambda s: (s["do"] is None, s["do"]))
    return driver_id, stops


# --------------------------------------------------------------------------- #
# Green Invoice — primary = link on the task; fallback = API match on the order
# --------------------------------------------------------------------------- #
def gi_token():
    return _post_json(GI_BASE.rstrip("/") + "/account/token",
                      {"id": GI_ID, "secret": GI_SECRET}).get("token")


def gi_fetch_invoice(stop, out_path):
    """Download the real GI invoice for a stop. Returns True on success."""
    link = stop.get("gi")
    if link:
        with open(out_path, "wb") as f:
            f.write(_get(link))
        return True
    # fallback: locate the document in Green Invoice that matches the order 100%
    wp = (stop.get("wp") or "").lstrip("#")
    if not wp:
        return False
    tok = gi_token()
    hdr = {"Authorization": f"Bearer {tok}"}
    res = _post_json(GI_BASE.rstrip("/") + "/documents/search",
                     {"pageSize": 50, "page": 1, "sort": "documentDate"}, hdr)
    for doc in res.get("items", []):
        blob = json.dumps(doc, ensure_ascii=False)
        if wp and wp in blob:                       # order id stamped on the doc
            did = doc.get("id")
            meta = json.loads(_get(GI_BASE.rstrip("/") + f"/documents/{did}", hdr).decode("utf-8"))
            pdf = (((meta.get("url") or {}).get("origin"))
                   or ((meta.get("files") or {}).get("origin")))
            if pdf:
                with open(out_path, "wb") as f:
                    f.write(_get(pdf))
                return True
    return False


# --------------------------------------------------------------------------- #
# LionWheel web (Playwright) — waybills + work-order, rendered to PDF
# --------------------------------------------------------------------------- #
def lw_web_opener():
    """Authenticated urllib opener for LionWheel's web UI (session cookie).
    urllib honours HTTPS_PROXY and reaches members.lionwheel.com fine; the
    sandboxed Chromium does NOT (ERR_CONNECTION_CLOSED), so we fetch every LW web
    page through this opener and hand Chromium self-contained HTML to render."""
    jar = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    op.addheaders = [("User-Agent", UA)]
    html = op.open(f"{LW_BASE}/users/sign_in", timeout=60).read().decode("utf-8", "ignore")
    tok = re.search(r'name="authenticity_token"[^>]*value="([^"]+)"', html).group(1)
    body = urllib.parse.urlencode({
        "authenticity_token": tok,
        "user[username]": os.environ["LIONWHEEL_WEB_USER"],
        "user[password]": os.environ["LIONWHEEL_WEB_PASSWORD"],
        "user[remember_me]": "1",
    }).encode()
    op.open(urllib.request.Request(f"{LW_BASE}/users/sign_in", data=body), timeout=60).read()
    return op


def lw_fetch_inlined(url, opener):
    """Fetch a LionWheel web page and return a self-contained HTML string:
    linked stylesheets inlined, <script> stripped, <img> inlined as data URIs.
    Chromium then renders it via set_content with NO network — the real LionWheel
    page (its own header/columns/branding), not a page we invent."""
    import base64
    html = opener.open(url, timeout=60).read().decode("utf-8", "ignore")
    html = re.sub(r"<script\b[^>]*>.*?</script>", "", html, flags=re.I | re.S)

    def _abs(href):
        return href if href.startswith("http") else LW_BASE + "/" + href.lstrip("/")

    for link in re.findall(r'<link\b[^>]*rel=["\']stylesheet["\'][^>]*>', html, flags=re.I):
        hm = re.search(r'href=["\']([^"\']+)["\']', link)
        if not hm:
            continue
        try:
            css = opener.open(_abs(hm.group(1)), timeout=60).read().decode("utf-8", "ignore")
        except Exception:
            css = ""
        html = html.replace(link, f"<style>{css}</style>")

    for img in re.findall(r'<img\b[^>]*>', html, flags=re.I):
        sm = re.search(r'src=["\']([^"\']+)["\']', img)
        if not sm or sm.group(1).startswith("data:"):
            continue
        try:
            raw = opener.open(_abs(sm.group(1)), timeout=60).read()
            ext = sm.group(1).rsplit(".", 1)[-1].split("?")[0].lower()
            mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
                    "gif": "image/gif", "svg": "image/svg+xml", "webp": "image/webp"}.get(ext, "image/png")
            uri = "data:%s;base64,%s" % (mime, base64.b64encode(raw).decode())
            html = html.replace(img, img.replace(sm.group(1), uri))
        except Exception:
            pass
    return html


# Compact print CSS for the LionWheel work order ("הדפסת סידור עבודה" =
# /visits/print_labels). Their print view renders the יעד column so narrow that
# each Hebrew letter stacks on its own line, blowing the route up to ~13 pages.
# nowrap + tight cells collapses it back to single-line rows so all stops fit one
# A4 page. We keep LionWheel's own header/columns/branding — only the layout is
# tightened, nothing is invented.
WORKORDER_FIT_CSS = """
@page { size: A4 portrait; margin: 5mm; }
* { box-sizing: border-box; }
table { font-size: 9.5px !important; width: 100% !important; border-collapse: collapse !important; }
td, th { white-space: nowrap !important; padding: 2px 4px !important;
         line-height: 1.2 !important; overflow: hidden !important;
         vertical-align: middle !important; }
img { max-height: 48px !important; }
"""


def render_pages(jobs):
    """jobs = [(html, out_pdf, fit_one_page_bool), ...]. Each `html` is already a
    self-contained LionWheel page (lw_fetch_inlined): CSS inlined, scripts gone,
    images data-URI'd. We render it via set_content so Chromium needs NO network
    (it cannot reach members.lionwheel.com in this sandbox).

    Each job is isolated: one bad page must NOT abort the batch — the other
    waybills still render, and a missing work-order PDF lets build()'s
    build_workorder() fallback produce page 1 rather than the driver getting none."""
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        import glob as _glob
        _cands = sorted(_glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome"))
        _exe = os.environ.get("PW_CHROMIUM_EXE") or (_cands[-1] if _cands else None)
        b = p.chromium.launch(executable_path=_exe, args=["--no-sandbox", "--disable-dev-shm-usage"])
        ctx = b.new_context()
        for html, out, fit_one in jobs:
            pg = ctx.new_page()
            try:
                _render_one(pg, html, out, fit_one)
            except Exception as e:
                print(f"render_pages: skipping failed job -> {out}: {e}")
            finally:
                pg.close()
        b.close()


def _render_one(pg, html, out, fit_one):
    pg.set_content(html, wait_until="domcontentloaded", timeout=60000)
    pg.wait_for_timeout(200)
    opts = dict(format="A4", print_background=True,
                margin={"top": "5mm", "bottom": "5mm", "left": "5mm", "right": "5mm"})
    if fit_one:
        # Real LionWheel work order, fitted to ONE A4 page AND spread to fill its
        # full height: tighten layout (nowrap), scale to fit width, then stretch
        # the route table so its rows distribute the remaining vertical space
        # (no dead whitespace at the bottom).
        try:
            pg.add_style_tag(content=WORKORDER_FIT_CSS)
            pg.wait_for_timeout(400)
            usable_w, usable_h = 754.0, 1080.0  # A4 @96dpi minus 5mm margins

            def _dims():
                return (pg.evaluate("document.body.scrollWidth") or 800,
                        pg.evaluate("document.body.scrollHeight") or 1100)

            # 1. scale to fit BOTH width AND natural height — guarantees every row
            #    is on the page before we stretch anything (no clipped stops).
            w, h = _dims()
            scale = max(0.3, min(1.0, round(min(usable_w / max(w, 1),
                                                usable_h / max(h, 1)), 3)))
            # 2. spread the route table to fill the page height at that scale, so
            #    rows distribute the remaining vertical space (no dead bottom gap).
            avail = usable_h / scale
            m = pg.evaluate(
                "(() => { const ts=[...document.querySelectorAll('table')]"
                ".sort((a,b)=>b.offsetHeight-a.offsetHeight); const t=ts[0];"
                " return { nonTable: document.body.scrollHeight - (t?t.offsetHeight:0),"
                " tableH: t?t.offsetHeight:0 }; })()"
            ) or {}
            non_table = float(m.get("nonTable", 0))
            table_h0 = float(m.get("tableH", 0))
            target_table = int(max(table_h0, avail - non_table))
            pg.evaluate(
                "(h)=>{const ts=[...document.querySelectorAll('table')]"
                ".sort((a,b)=>b.offsetHeight-a.offsetHeight);"
                " if(ts[0]) ts[0].style.height=h+'px';}",
                target_table,
            )
            pg.wait_for_timeout(300)
            # 3. FINAL guard: re-measure and re-scale so the (possibly taller after
            #    reflow) content still fits exactly one page — never clip a stop.
            w2, h2 = _dims()
            scale = max(0.3, min(scale, round(usable_h / max(h2, 1), 3),
                                 round(usable_w / max(w2, 1), 3)))
        except Exception:
            scale = 0.6
        opts["scale"] = scale
        opts["page_ranges"] = "1"
    pg.pdf(path=out, **opts)


# --------------------------------------------------------------------------- #
# non-standard inventory movements -> proposals for the Factory OS inbox
# --------------------------------------------------------------------------- #
MOVE_HINTS = ["החלפ", "החזר", "טעימ", "איסוף סחורה", "קבל", "מתנה", "דגימ"]

# note-text hint → (kind, Hebrew action label for the concise approval summary)
KIND_HINTS = [
    ("החלפ", "exchange", "החלפת סחורה"),
    ("איסוף", "pickup", "איסוף סחורה"),
    ("החזר", "return", "החזרת סחורה"),
    ("טעימ", "tasting", "טעימה"),
    ("דגימ", "tasting", "דגימה"),
    ("קבל", "goods_receipt", "קבלת סחורה"),
    ("מתנה", "other", "מתנה"),
]


def classify_move(text):
    for hint, kind, label in KIND_HINTS:
        if hint in text:
            return kind, label
    return "other", "תזוזת מלאי"


def detect_inventory_moves(stops):
    """Conservative: flag stops whose note implies a non-pick stock move.
    We do NOT guess quantities — the proposal carries the verbatim note + a
    concise summary for human approval in the inbox (as an APPROVAL, not an
    exception) before any stock_ledger entry is posted."""
    out = []
    for s in stops:
        t = s["task"]
        note = (t.get("notes") or "").strip()
        recip = s.get("recipient") or ""
        text = f"{recip} {note}"
        if any(h in text for h in MOVE_HINTS) and not s.get("gi"):
            kind, label = classify_move(text)
            recip_short = recip.split("(")[0].strip() or recip
            summary = f"{label} — {recip_short}" if recip_short else label
            out.append({
                "lw_task_id": s["tid"],
                "daily_order": s["do"],
                "recipient": recip,
                "note": note,
                "kind": kind,
                "summary": summary,
                "form_type": "inventory_movement",
                "status": "open",
                "needs": "item_id + qty + direction(+/-) confirmed by the approver in the inbox",
            })
    return out


# A LionWheel delivery-note stop carries 0 order_items but ships real goods that
# are billed on a Green Invoice document — the order went out without the
# Shopify/LW line link, so stock was never decremented. We detect the bound GI
# doc number from the stop title/note ("תעודת משלוח NNNNN" / "חשבונית NNNNN") and
# emit an FG-OUT proposal. We deliberately do NOT resolve barcode->FG/case_pack
# here (that needs the item master / DB): the SKILL.md filing step (Claude via the
# Supabase MCP) fetches the GI lines, maps them deterministically, and files the
# pending inbox approval keyed on the GI doc id. v1 NARROW: only 0-item stops with
# a bound doc number; credits/quotes are excluded at the filing step by doc type.
GI_DOC_RE = re.compile(
    r"(?:תעוד[הת]\s*(?:משלוח|תשלוח|שילוח)|חשבונית(?:\s*מס)?)\s*#?\s*(\d{3,})")


def detect_fg_out_stops(stops):
    out = []
    for s in stops:
        if s.get("items"):                       # has LW order_items → normal pick
            continue
        t = s["task"]
        text = " ".join(str(t.get(k) or "") for k in ("notes", "driver_note"))
        text = f"{s.get('recipient') or ''} {text}"
        if "איסוף" in text or "החזר" in text:    # pickup/return → not an FG-OUT
            continue
        m = GI_DOC_RE.search(text)
        if not m:
            continue
        recip = (s.get("recipient") or "").strip()
        doc = m.group(1)
        out.append({
            "lw_task_id": s["tid"],
            "daily_order": s["do"],
            "recipient": recip,
            "kind": "fg_out",
            "gi_doc_number": doc,
            "summary": f"הורדת מלאי FG — {recip.split('-')[0].strip()} (מסמך {doc})",
            "form_type": "inventory_movement",
            "status": "open",
            "needs": ("resolve GI doc lines barcode->FG with case_pack/UOM, then "
                      "file a pending FG-OUT inbox approval; idempotency = gi_doc_number"),
        })
    return out


# --------------------------------------------------------------------------- #
# work order (page 1) — the driving day as a single-page A4 timeline.
# Signature: a green spine of numbered stop-discs in driving order, time in mono
# beside each. Structure carries truth: pickup/exchange stops show a terracotta
# disc + the action word in place of the city; picking-shortfall stops carry an
# amber dot. The driver reads the day top-to-bottom and sees attention-stops at a
# glance. (The LionWheel SPA route view can't be forced to one clean page and its
# print_summary is aggregate-only, so we reproduce the route ourselves.)
#
# Palette is brand-aligned to GT Everyday (a green-tea / beverage maker), off the
# generic corporate navy; type is one family used deliberately — DejaVu Sans for
# names/structure, DejaVu Sans Mono for times and counts (dispatch-board numerals).
# --------------------------------------------------------------------------- #
def build_workorder(driver, date, stops, out_pdf, flags=None):
    import fitz
    from bidi.algorithm import get_display
    flags = flags or {}
    fb = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    fr = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    fm = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
    HB = fitz.Font(fontfile=fb)
    HR = fitz.Font(fontfile=fr)
    HM = fitz.Font(fontfile=fm)

    INK   = (0.086, 0.141, 0.110)   # #16241C deep evergreen, primary text
    GREEN = (0.118, 0.431, 0.282)   # #1E6E48 GT green — header, spine, discs
    MUTE  = (0.416, 0.455, 0.424)   # #6A746C secondary labels
    HAIR  = (0.863, 0.886, 0.867)   # #DCE2DD hairline
    TERRA = (0.741, 0.220, 0.161)   # #BD3829 special-handling (pickup/exchange)
    AMBER = (0.780, 0.518, 0.122)   # #C7841F picking shortfall
    PALE  = (0.910, 0.945, 0.922)   # #E8F1EC disc wash on green band

    dmy = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%d/%m/%Y")
    pkgs = sum(int(s["packages"] or 0) for s in stops)
    etas = sorted(s["eta"] for s in stops if s.get("eta"))
    window = f"{etas[0]}–{etas[-1]}" if etas else ""

    doc = fitz.open()
    pg = doc.new_page(width=595, height=842)
    pg.insert_font(fontname="db", fontfile=fb)
    pg.insert_font(fontname="dr", fontfile=fr)
    pg.insert_font(fontname="dm", fontfile=fm)

    def _f(font):
        return {"db": HB, "dr": HR, "dm": HM}[font]

    def rt(x_right, y, text, fs, font="dr", color=INK):
        """right-anchored (RTL): text ends at x_right."""
        disp = get_display(str(text))
        pg.insert_text((x_right - _f(font).text_length(disp, fs), y), disp,
                       fontname=font, fontsize=fs, color=color)

    def disc(cx, cy, r, num, fill, ring=False, numcolor=(1, 1, 1)):
        sh = pg.new_shape()
        sh.draw_circle((cx, cy), r)
        if ring:
            sh.finish(color=fill, width=1.8, fill=(1, 1, 1))
        else:
            sh.finish(color=fill, width=0, fill=fill)
        sh.commit()
        s = str(num)
        fs = 9.5 if len(s) >= 2 else 10.5
        w = HB.text_length(s, fs)
        pg.insert_text((cx - w / 2, cy + fs * 0.36), s,
                       fontname="db", fontsize=fs,
                       color=(fill if ring else numcolor))

    # ---- header band -------------------------------------------------------- #
    pg.draw_rect(fitz.Rect(0, 0, 595, 92), fill=GREEN, color=GREEN)
    rt(575, 30, "סידור עבודה", 10, "dr", PALE)
    rt(575, 60, driver, 27, "db", (1, 1, 1))
    # totals strip, mono numerals on the band
    rt(575, 80, f"{dmy}", 10.5, "dm", PALE)
    bits = [(f"{len(stops)}", "עצירות"), (f"{pkgs}", "חבילות")]
    if window:
        bits.append((window, "חלון"))
    x = 360
    for num, lab in bits:
        rt(x, 80, lab, 9, "dr", PALE)
        x -= HR.text_length(get_display(lab), 9) + 5
        rt(x, 80, num, 10.5, "dm", (1, 1, 1))
        x -= HM.text_length(num, 10.5) + 16

    # ---- column hints (light, set once) ------------------------------------- #
    SPINE = 556                     # x of the timeline spine
    DISC_R = 10
    TIME_XR = 524                   # right edge of the mono time
    NAME_XR = 506                   # right edge of customer / action line
    NAME_XMIN = 150                 # left limit for the name (truncate before)
    ITEM_XR = 116                   # right edge of items count
    PKG_XR = 56                     # right edge of packages count
    yh = 116
    rt(TIME_XR, yh, "שעה", 8, "db", MUTE)
    rt(NAME_XR, yh, "יעד", 8, "db", MUTE)
    rt(ITEM_XR, yh, "פריטים", 8, "db", MUTE)
    rt(PKG_XR, yh, "חב׳", 8, "db", MUTE)
    pg.draw_line(fitz.Point(20, yh + 6), fitz.Point(575, yh + 6), color=HAIR, width=1)

    # ---- the timeline ------------------------------------------------------- #
    y0 = yh + 18
    bottom = 812
    n = max(len(stops), 1)
    rowh = min((bottom - y0) / n, 30)
    two_line = rowh >= 24
    disc_r = DISC_R if rowh >= 22 else 8

    # spine behind the discs (first centre -> last centre)
    first_c = y0 + rowh / 2
    last_c = y0 + rowh * (len(stops) - 1) + rowh / 2
    pg.draw_line(fitz.Point(SPINE, first_c), fitz.Point(SPINE, last_c),
                 color=HAIR, width=2)

    ACTION = {"איסוף": "איסוף סחורה", "החלפה": "החלפת סחורה"}

    def fit(text, font, fs, max_w):
        disp = str(text)
        while disp and _f(font).text_length(get_display(disp), fs) > max_w:
            disp = disp[:-1]
        return disp

    for i, s in enumerate(stops):
        cy = y0 + rowh * i + rowh / 2
        fl = flags.get(s["tid"], {})
        special = fl.get("special")            # "איסוף" / "החלפה" / None
        short = fl.get("short")
        # left attention bar
        if special:
            pg.draw_rect(fitz.Rect(20, cy - rowh / 2 + 3, 23, cy + rowh / 2 - 3),
                         fill=TERRA, color=TERRA)
        elif short:
            pg.draw_rect(fitz.Rect(20, cy - rowh / 2 + 3, 23, cy + rowh / 2 - 3),
                         fill=AMBER, color=AMBER)
        # stop disc on the spine
        disc(SPINE, cy, disc_r, s.get("do") if s.get("do") is not None else "·",
             TERRA if special else GREEN)
        # time (mono)
        if s.get("eta"):
            rt(TIME_XR, cy + 3, s["eta"], 10, "dm", INK)
        # customer (primary) + secondary line (city, or the action for specials)
        max_w = NAME_XR - NAME_XMIN
        name = fit(s.get("recipient") or "", "db", 9.8, max_w)
        if two_line:
            rt(NAME_XR, cy - 1, name, 9.8, "db", INK)
            if special:
                rt(NAME_XR, cy + 10, ACTION.get(special, special), 8.5, "db", TERRA)
            else:
                rt(NAME_XR, cy + 10, fit(s.get("city") or "", "dr", 8.5, max_w),
                   8.5, "dr", MUTE)
        else:
            sec = ACTION.get(special, special) if special else (s.get("city") or "")
            rt(NAME_XR, cy + 3, fit(f"{name}  ·  {sec}", "db", 9.2, max_w),
               9.2, "db", INK)
        # shortfall dot, just right of the spine-side of the name row
        if short and not special:
            sh = pg.new_shape()
            sh.draw_circle((NAME_XR + 8, cy - 2), 2.2)
            sh.finish(fill=AMBER, color=AMBER)
            sh.commit()
        # data columns (mono numerals)
        if s.get("items") is not None:
            rt(ITEM_XR, cy + 3, s["items"], 9.5, "dm", MUTE)
        if s.get("packages") is not None:
            rt(PKG_XR, cy + 3, s["packages"], 9.5, "dm", INK)
        # hairline between rows
        if i < len(stops) - 1:
            pg.draw_line(fitz.Point(20, cy + rowh / 2),
                         fitz.Point(575, cy + rowh / 2), color=HAIR, width=0.4)

    # ---- footer legend ------------------------------------------------------ #
    def dot(x, color):
        sh = pg.new_shape()
        sh.draw_circle((x, 828), 3)
        sh.finish(fill=color, color=color)
        sh.commit()
    fx = 575
    for color, lab in ((GREEN, "מסירה"), (TERRA, "איסוף / החלפה"), (AMBER, "חוסר ליקוט")):
        dot(fx, color)
        rt(fx - 8, 831, lab, 8, "dr", MUTE)
        fx -= HR.text_length(get_display(lab), 8) + 26
    rt(120, 831, "GT Everyday · LionWheel", 8, "dr", MUTE)
    doc.save(out_pdf)
    doc.close()


# --------------------------------------------------------------------------- #
# assemble
# --------------------------------------------------------------------------- #
def assemble(workorder_pdf, ordered_parts, out_pdf):
    from pypdf import PdfReader, PdfWriter
    w = PdfWriter()
    if workorder_pdf and os.path.exists(workorder_pdf):
        for p in PdfReader(workorder_pdf).pages:
            w.add_page(p)
    for path, copies in ordered_parts:
        rd = PdfReader(path)
        for _ in range(copies):
            for p in rd.pages:
                w.add_page(p)
    tmp = out_pdf + ".tmp"
    with open(tmp, "wb") as f:
        w.write(f)
    # compress (the x2 duplication + embedded GI PDFs balloon the file ~10x)
    import fitz
    d = fitz.open(tmp)
    d.save(out_pdf, garbage=4, deflate=True, deflate_images=True, deflate_fonts=True)
    d.close()
    os.remove(tmp)


def build(driver, date, from_stop=None, copies=2):
    os.makedirs(OUT, exist_ok=True)
    import annotate

    driver_id, stops = fetch_route(driver, date)
    if not stops:
        raise SystemExit(f"No ASSIGNED stops for driver={driver!r} date={date}")
    if from_stop:
        stops = [s for s in stops if s["do"] and s["do"] >= from_stop]

    # per-stop flags for the work-order timeline: special handling (pickup /
    # exchange, derived from the same note hints used for the inbox proposals)
    # and picking shortfalls (any ordered > picked). Structure carries truth.
    flags = {}
    for s in stops:
        t = s["task"]
        text = f"{s.get('recipient') or ''} {(t.get('notes') or '')}"
        special = None
        if not s.get("gi"):
            if "איסוף" in text:
                special = "איסוף"
            elif "החלפ" in text:
                special = "החלפה"
        short = False
        for it in (t.get("order_items") or []):
            try:
                if float(it["picked_quantity"]) < float(it["quantity"]):
                    short = True
                    break
            except (TypeError, ValueError, KeyError):
                continue
        if special or short:
            flags[s["tid"]] = {"special": special, "short": short}

    # 1. Resolve each stop to an invoice (download + annotate) or mark it as
    #    needing a LionWheel waybill. Doing the GI fetch FIRST means we only
    #    render the waybills we actually use — an invoice stop never pays for a
    #    waybill render that is then discarded.
    invoice_part = {}     # tid -> annotated invoice path
    waybill_stops = []
    for s in stops:
        if s["gi"] or s["task"].get("order_items"):   # invoice candidate
            src = f"{OUT}/inv_{s['tid']}.pdf"
            try:
                ok = gi_fetch_invoice(s, src)
            except Exception as e:                    # one bad GI lookup must not
                print(f"gi_fetch_invoice: stop {s['tid']} failed: {e}")
                ok = False                            # abort the whole pack
            if ok:
                ann = f"{OUT}/ann_{s['tid']}.pdf"
                annotate.annotate(s["task"], src, ann)
                invoice_part[s["tid"]] = ann
                continue
        waybill_stops.append(s)                       # no invoice → needs waybill

    # 2. ONE Playwright session: the REAL LionWheel work order (page 1, fitted to
    #    one A4) + a waybill for each stop that has no invoice. build_workorder()
    #    is kept only as a fallback if LionWheel doesn't return the work order.
    wo = None
    jobs = []          # [(inlined_html, out_pdf, fit_one)]
    opener = None
    if (not from_stop and driver_id) or waybill_stops:
        try:
            opener = lw_web_opener()
        except Exception as e:
            print(f"lw_web_opener failed: {e}")
    if not from_stop and driver_id and opener:
        wo = f"{OUT}/_workorder.pdf"
        dmy = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%d/%m/%Y")
        wo_url = (f"{LW_BASE}/visits/print_labels"
                  f"?date={urllib.parse.quote(dmy)}&driver_id={driver_id}")
        try:
            jobs.append((lw_fetch_inlined(wo_url, opener), wo, True))
        except Exception as e:
            print(f"work-order fetch failed: {e}")
    if opener:
        for s in waybill_stops:
            try:
                html = lw_fetch_inlined(f"{LW_BASE}/tasks/{s['tid']}/print_waybill", opener)
                jobs.append((html, f"{OUT}/wb_{s['tid']}.pdf", False))
            except Exception as e:
                print(f"waybill fetch failed for {s['tid']}: {e}")
    # Remove any stale target files from a prior run BEFORE rendering: a failed
    # render must leave the target ABSENT so the fallback (page 1) / a real gap
    # (waybill) is detected, never a leftover from a different date silently reused.
    for _html, _out, _fit in jobs:
        try:
            if os.path.exists(_out):
                os.remove(_out)
        except OSError:
            pass
    if jobs:
        render_pages(jobs)

    # 3. fallback: if the real LionWheel work order didn't render, generate one so
    #    the pack always has a page 1.
    if not from_stop and (not wo or not os.path.exists(wo) or os.path.getsize(wo) == 0):
        wo = f"{OUT}/_workorder.pdf"
        build_workorder(driver, date, stops, wo, flags)

    # 4. assemble in driving order: invoice if present, else its waybill.
    ordered_parts = []
    for s in stops:
        ann = invoice_part.get(s["tid"])
        if ann:
            ordered_parts.append((ann, copies))
            continue
        wb = f"{OUT}/wb_{s['tid']}.pdf"
        if os.path.exists(wb):
            ordered_parts.append((wb, copies))

    final = f"{OUT}/route_{driver}_{date}.pdf".replace(" ", "_")
    assemble(wo, ordered_parts, final)

    # inbox proposals: non-pick stock moves (returns/exchanges/tastings/pickups →
    # RM goods-receipt) + delivery-note FG-OUT stops (0 items but a bound GI doc).
    # Dedupe by (task, kind) so a stop is never proposed twice.
    proposals = detect_inventory_moves(stops) + detect_fg_out_stops(stops)
    seen, deduped = set(), []
    for p in proposals:
        k = (p["lw_task_id"], p["kind"])
        if k in seen:
            continue
        seen.add(k)
        deduped.append(p)
    proposals = deduped
    json.dump(proposals, open(f"{OUT}/inventory_proposals.json", "w"),
              ensure_ascii=False, indent=2)

    # discrepancy summary (for the email body / cover-of-record)
    disc = []
    for s in stops:
        for it in (s["task"].get("order_items") or []):
            try:
                q, pq = float(it["quantity"]), float(it["picked_quantity"])
            except (TypeError, ValueError, KeyError):
                continue
            if pq < q:
                disc.append({"stop": s["do"], "recipient": s["recipient"],
                             "item": it["name"], "ordered": int(q), "picked": int(pq)})

    summary = {
        "driver": driver, "date": date,
        "stops": len(stops),
        "invoices": sum(1 for p, _ in ordered_parts if "ann_" in p),
        "waybills": sum(1 for p, _ in ordered_parts if "wb_" in p),
        "copies": copies,
        "discrepancies": disc,
        "inventory_proposals": len(proposals),
        "file": final,
    }
    json.dump(summary, open(f"{OUT}/summary.json", "w"), ensure_ascii=False, indent=2)

    # markdown digest of the run — the graphify auto-step (SKILL.md step 7) reads
    # THIS (graphify can't ingest raw JSON). One queryable record per dispatch:
    # stops, customers, picking shortfalls, inventory-movement proposals.
    write_digest(driver, date, stops, disc, proposals, summary,
                 f"{OUT}/summary.md")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def write_digest(driver, date, stops, disc, proposals, summary, path):
    L = []
    L.append(f"# Route pack — {driver} — {date}")
    L.append("")
    L.append(f"Driver **{driver}** ran {summary['stops']} stops on {date}: "
             f"{summary['invoices']} Green Invoices and {summary['waybills']} "
             f"LionWheel waybills (×{summary['copies']} each).")
    L.append("")
    L.append("## Stops (driving order)")
    for s in stops:
        recip = (s.get("recipient") or "").strip()
        city = (s.get("city") or "").strip()
        tags = []
        if any(p["lw_task_id"] == s["tid"] for p in proposals):
            tags.append("special-handling")
        if any(d["stop"] == s["do"] for d in disc):
            tags.append("picking-shortfall")
        tag = f" — {', '.join(tags)}" if tags else ""
        L.append(f"- Stop {s.get('do')} at {s.get('eta') or '?'}: **{recip}** "
                 f"({city}) — {s.get('items')} items, {s.get('packages')} "
                 f"packages{tag}")
    L.append("")
    L.append("## Picking shortfalls")
    if disc:
        for d in disc:
            L.append(f"- Stop {d['stop']} **{d['recipient']}**: {d['item']} — "
                     f"picked {d['picked']} of {d['ordered']}")
    else:
        L.append("- None.")
    L.append("")
    L.append("## Inventory-movement proposals (await inbox approval)")
    if proposals:
        for p in proposals:
            what = p.get("summary") or p.get("note") or "goods pickup"
            L.append(f"- [{p.get('kind','move')}] {p['recipient']} "
                     f"(task {p['lw_task_id']}): {what}")
    else:
        L.append("- None.")
    L.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--driver", required=True)
    ap.add_argument("--date", help="YYYY-MM-DD; default tomorrow")
    ap.add_argument("--from-stop", type=int, default=None)
    ap.add_argument("--copies", type=int, default=2)
    a = ap.parse_args()
    date = a.date or (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
    build(a.driver, date, a.from_stop, a.copies)


if __name__ == "__main__":
    main()
