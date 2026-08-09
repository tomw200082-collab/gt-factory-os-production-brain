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
  marks    : X on the lines that fell short of the order, nothing on the rest
             (Tom, 2026-08-04 — supersedes the 2026-06-21 mark-every-line design;
             --mark-all-lines restores it); package count under "מקור";
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


def lw_list_open():
    """Every task not yet delivered — ASSIGNED *and* UNASSIGNED. A route being
    built the evening before often still has stops awaiting assignment; those are
    real stops on the driver's day, so a pack built with all_statuses must see
    them (a stop dropped here is an invoice the driver never gets)."""
    url = f"{LW_BASE}/api/v1/tasks.json?key={urllib.parse.quote(LW_KEY)}&limit=1000"
    d = _get_json(url)
    tasks = d.get("tasks", d) if isinstance(d, dict) else d
    return [t["id"] for t in tasks if t.get("status") in ("ASSIGNED", "UNASSIGNED")]


def fetch_route(driver, date, all_statuses=False):
    """Return (driver_id, [stop,...]) sorted by daily_order for driver+date.

    all_statuses=True also keeps UNASSIGNED stops — use when the whole day is to
    be treated as confirmed even though LionWheel has not finished assigning."""
    stops, driver_id = [], None
    for tid in (lw_list_open() if all_statuses else lw_list_assigned()):
        t = lw_task(tid)
        if not t:
            continue
        if t.get("driver_str") != driver:
            continue
        if not (t.get("pickup_at") or "").startswith(date):
            continue
        if not all_statuses and t.get("status") != "ASSIGNED":
            continue
        v = (t.get("visits") or [{}])[0]
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
_GI_TOK = None
_GI_PAGE_CACHE = {}


def gi_token():
    global _GI_TOK
    if _GI_TOK is None:
        _GI_TOK = _post_json(GI_BASE.rstrip("/") + "/account/token",
                             {"id": GI_ID, "secret": GI_SECRET}).get("token")
    return _GI_TOK


def _gi_page(page, hdr, page_size=100):
    """One page of the most-recent GI documents (newest first), cached module-wide
    so a whole route shares a single paginated scan instead of re-fetching."""
    if page not in _GI_PAGE_CACHE:
        res = _post_json(GI_BASE.rstrip("/") + "/documents/search",
                         {"pageSize": page_size, "page": page, "sort": "documentDate"}, hdr)
        _GI_PAGE_CACHE[page] = res.get("items", [])
    return _GI_PAGE_CACHE[page]


def gi_fetch_invoice(stop, out_path, max_pages=30):
    """Download the real GI invoice for a stop. Returns True on success.

    Primary: match the order id against the GI document list. The order id is
    stamped in each document's `remarks` ("מספר הזמנה באתר: #GT…"), so this is an
    exact identity match; the exact `#GT…` token is matched so GT13483 never
    collides with GT134830. A route can carry orders days-to-weeks old and Green
    Invoice holds >12k documents, so the newest page alone misses them (the old
    50-row window silently dropped older orders to waybills) — scan deeper,
    pages cached.

    Fallback: the direct greeninvoice link stamped on the LionWheel task. It is
    NOT the primary source: the stamped link is unverifiable (a GI PDF carries no
    order id) and has been observed pointing at another customer's invoice
    (2026-08-09, task 26822430 / #GT14056 served נונומימי's #63887 — wrong name,
    ח.פ, address and prices handed to the wrong customer). Used only when the
    order id finds nothing.

    When both resolve and disagree, the API document wins and the disagreement is
    recorded on the stop as `gi_link_mismatch` — the stamped link is what the
    driver's own LionWheel app shows him, so a mismatch is a live data bug that
    must reach Tom, not be silently papered over here."""
    link = stop.get("gi")
    wp = (stop.get("wp") or "").lstrip("#")
    base = GI_BASE.rstrip("/")

    if wp:
        hdr = {"Authorization": f"Bearer {gi_token()}"}
        needle = "#" + wp
        for page in range(1, max_pages + 1):
            items = _gi_page(page, hdr)
            if not items:
                break
            doc = next((d for d in items
                        if needle in json.dumps(d, ensure_ascii=False)), None)
            if not doc:
                continue
            meta = json.loads(_get(base + f"/documents/{doc.get('id')}", hdr).decode("utf-8"))
            pdf = (((meta.get("url") or {}).get("origin"))
                   or ((meta.get("files") or {}).get("origin")))
            if not pdf:
                break
            body = _get(pdf)
            with open(out_path, "wb") as f:
                f.write(body)
            stop["gi_source"] = f"api:{needle}"
            stop["gi_doc"] = doc.get("number")
            if link:
                try:
                    if _get(link) != body:
                        stop["gi_link_mismatch"] = {
                            "order": needle, "used": doc.get("number"),
                            "used_client": (doc.get("client") or {}).get("name"),
                            "link": link}
                except Exception:                      # link dead → nothing to compare
                    pass
            return True

    if link:
        with open(out_path, "wb") as f:
            f.write(_get(link))
        stop["gi_source"] = "task-link (unverified)"
        return True
    return False


# --------------------------------------------------------------------------- #
# LionWheel web (Playwright) — waybills + work-order, rendered to PDF
# --------------------------------------------------------------------------- #
def lw_login_cookies():
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
    return [{"name": c.name, "value": c.value, "domain": "members.lionwheel.com", "path": "/"}
            for c in jar]


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
    """jobs = [(url, out_pdf, fit_one_page_bool), ...] rendered with the LW session.

    Each job is isolated: one bad page (a flaky/changed work-order URL, a stalled
    networkidle) must NOT abort the whole batch. The other waybills still render,
    and a missing work-order PDF lets build()'s build_workorder() fallback produce
    page 1 rather than the driver getting no pack at all."""
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
    from playwright.sync_api import sync_playwright
    cookies = lw_login_cookies()
    # Egress-restricted sandboxes (Claude Code on the web) route outbound HTTPS
    # through a re-terminating proxy that headless Chromium's TLS stack cannot
    # complete (ERR_CONNECTION_RESET) — but urllib CAN (same path the API/login
    # calls already use). So Chromium makes ZERO direct network calls: every
    # request is intercepted and fulfilled from urllib. Same-origin LionWheel
    # assets (HTML, CSS, fonts, logo) are fetched with the session cookies;
    # third-party beacons (rollbar, analytics) are aborted — irrelevant to print.
    # This yields the REAL LionWheel work order + waybills, not a fallback.
    ck = "; ".join(f"{c['name']}={c['value']}" for c in cookies)

    def _urlfetch(u):
        req = urllib.request.Request(u, headers={"User-Agent": UA, "Cookie": ck})
        r = urllib.request.urlopen(req, timeout=60)
        return r.read(), r.headers.get("Content-Type", "application/octet-stream")

    def _route(route):
        u = route.request.url
        try:
            if "lionwheel.com" in urllib.parse.urlparse(u).netloc:
                body, ctype = _urlfetch(u)
                route.fulfill(status=200, body=body, headers={"Content-Type": ctype})
            else:
                route.abort()
        except Exception:
            try:
                route.abort()
            except Exception:
                pass

    with sync_playwright() as p:
        chromium_path = "/opt/pw-browsers/chromium"
        launch_kwargs = {"args": ["--no-sandbox", "--disable-dev-shm-usage"]}
        if os.path.exists(chromium_path):
            launch_kwargs["executable_path"] = chromium_path
        b = p.chromium.launch(**launch_kwargs)
        ctx = b.new_context(ignore_https_errors=True)
        ctx.add_cookies(cookies)
        for url, out, fit_one in jobs:
            pg = ctx.new_page()
            pg.route("**/*", _route)
            try:
                _render_one(pg, url, out, fit_one)
            except Exception as e:
                print(f"render_pages: skipping failed job {url}: {e}")
            finally:
                pg.close()
        b.close()


def _render_one(pg, url, out, fit_one):
    pg.goto(url, wait_until="networkidle", timeout=60000)
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
            w = pg.evaluate("document.body.scrollWidth") or 800
            scale = min(1.0, usable_w / max(w, 1))
            m = pg.evaluate(
                "(() => { const ts=[...document.querySelectorAll('table')]"
                ".sort((a,b)=>b.offsetHeight-a.offsetHeight); const t=ts[0];"
                " return { nonTable: document.body.scrollHeight - (t?t.offsetHeight:0),"
                " tableH: t?t.offsetHeight:0 }; })()"
            ) or {}
            non_table = float(m.get("nonTable", 0))
            table_h0 = float(m.get("tableH", 0))
            target_table = int(max(table_h0, usable_h / scale - non_table))
            pg.evaluate(
                "(h)=>{const ts=[...document.querySelectorAll('table')]"
                ".sort((a,b)=>b.offsetHeight-a.offsetHeight);"
                " if(ts[0]) ts[0].style.height=h+'px';}",
                target_table,
            )
            pg.wait_for_timeout(300)
            h = pg.evaluate("document.body.scrollHeight") or (target_table + non_table)
            scale = min(scale, usable_h / max(h, 1))
            scale = max(0.4, round(scale, 3))
        except Exception:
            scale = 0.62
        opts["scale"] = scale
        opts["page_ranges"] = "1"
    pg.pdf(path=out, **opts)


# --------------------------------------------------------------------------- #
# non-standard inventory movements -> proposals for the Factory OS inbox
# --------------------------------------------------------------------------- #
# Hints that a stop moves stock outside normal picking. STRONG hints stand on
# their own: a stop can be a normal invoiced delivery AND still carry goods back
# (2026-08-09, לה פרינה #GT14056 — "לאסוף מהם את ההזמנה מחמישי ולספק את זו" — a
# whole order returning, previously invisible because the stop had an invoice).
# WEAK hints only count when the stop has no invoice, or "קבלת סחורה עד 14:00" on
# an ordinary delivery would file a proposal for every second stop.
# "אסוף" is listed beside "איסוף" on purpose: the imperative Tom actually writes
# is "לאסוף מהם", which does NOT contain the noun "איסוף".
MOVE_HINTS_STRONG = ["החלפ", "החזר", "טעימ", "איסוף", "אסוף", "מתנה", "דגימ"]
MOVE_HINTS_WEAK = ["קבל"]

# A collection stop can be about money, not goods — "איסוף צ'קים", "לאסוף בבקשה
# צק". Those trip the pickup hint but move no stock, so they would file bogus
# approvals into Tom's inbox. Money words veto the hint UNLESS a goods word is
# also present (a stop can collect a cheque AND take back product).
MONEY_ONLY = ["צ'ק", "צ׳ק", "צק", "שיק", "המחאה", "מזומן"]
GOODS_WORDS = ["סחורה", "בקבוק", "ארגז", "מלאי", "מוצר", "הזמנה", "משטח"]

# note-text hint → (kind, Hebrew action label for the concise approval summary)
KIND_HINTS = [
    ("החלפ", "exchange", "החלפת סחורה"),
    ("איסוף", "pickup", "איסוף סחורה"),
    ("אסוף", "pickup", "איסוף סחורה"),
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
        money_only = (any(m in text for m in MONEY_ONLY)
                      and not any(g in text for g in GOODS_WORDS))
        strong = any(h in text for h in MOVE_HINTS_STRONG) and not money_only
        weak = (any(h in text for h in MOVE_HINTS_WEAK) and not s.get("gi")
                and not money_only)
        if strong or weak:
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


def _is_exempt(stop, missing_exempt):
    """True when this stop is excluded from the shortage list — the product IS
    on the shelf for this customer even though it is short elsewhere. Matched on
    the recipient name so the caller can name the customer, not a task id."""
    if not missing_exempt:
        return False
    rec = (stop.get("recipient") or "").lower()
    return any(e.lower() in rec for e in missing_exempt)


def build(driver, date, from_stop=None, copies=2, marks_only_short=False,
          missing_products=None, all_statuses=False, workorder=True,
          missing_exempt=None, show_packages=True, shortfall_only=True):
    os.makedirs(OUT, exist_ok=True)
    import annotate

    driver_id, stops = fetch_route(driver, date, all_statuses=all_statuses)
    if not stops:
        raise SystemExit(f"No stops for driver={driver!r} date={date}")
    if from_stop is not None:
        # `s["do"] is not None`, NOT truthiness — daily_order 0 is a real first
        # stop, and testing it as a boolean silently drops that whole invoice.
        stops = [s for s in stops if s["do"] is not None and s["do"] >= from_stop]

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
        if missing_products:
            # Shortage-list mode: picking is still running, so picked_quantity is
            # not yet truth. The known-missing products are.
            low = [m.lower() for m in missing_products]
            short = (not _is_exempt(s, missing_exempt)) and any(
                any(m in (it.get("name") or "").lower() for m in low)
                for it in (t.get("order_items") or []))
        else:
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
            if gi_fetch_invoice(s, src):
                ann = f"{OUT}/ann_{s['tid']}.pdf"
                # Default marks every line (the Tom-locked 2026-06-21 design).
                # --marks-only-short narrows marks to the orders that actually fell
                # short, so a re-run mid-route carries no column of identical ✓ for
                # the driver to read past. Opt-in: the locked design is the default.
                mark_lines = True
                mn = missing_products
                so = shortfall_only
                if missing_products:
                    so = False          # alternative modes, never both
                    # Shortage-list mode owns the marks outright: never fall back
                    # to picked_quantity, or an exempted stop would come out with
                    # every line marked instead of none.
                    mark_lines = False
                    if _is_exempt(s, missing_exempt):
                        mn = None
                elif marks_only_short:
                    mark_lines = bool(flags.get(s["tid"], {}).get("short"))
                if so:
                    mark_lines = False
                annotate.annotate(s["task"], src, ann, mark_lines=mark_lines,
                                  missing_names=mn, show_packages=show_packages,
                                  shortfall_only=so)
                invoice_part[s["tid"]] = ann
                continue
        waybill_stops.append(s)                       # no invoice → needs waybill

    # 2. ONE Playwright session: the REAL LionWheel work order (page 1, fitted to
    #    one A4) + a waybill for each stop that has no invoice. build_workorder()
    #    is kept only as a fallback if LionWheel doesn't return the work order.
    wo = None
    jobs = []
    if workorder and from_stop is None and driver_id:
        wo = f"{OUT}/_workorder.pdf"
        dmy = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%d/%m/%Y")
        wo_url = (f"{LW_BASE}/visits/print_labels"
                  f"?date={urllib.parse.quote(dmy)}&driver_id={driver_id}")
        jobs.append((wo_url, wo, True))
    jobs += [(f"{LW_BASE}/tasks/{s['tid']}/print_waybill", f"{OUT}/wb_{s['tid']}.pdf", False)
             for s in waybill_stops]
    if jobs:
        render_pages(jobs)

    # 3. fallback: if the real LionWheel work order didn't render, generate one so
    #    the pack always has a page 1.
    if workorder and from_stop is None and (not wo or not os.path.exists(wo) or os.path.getsize(wo) == 0):
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

    proposals = detect_inventory_moves(stops)
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

    # Stops whose LionWheel-stamped GI link served a different document than the
    # order id resolves to. The pack itself is correct (order id wins) — but the
    # driver's app shows him that same bad link, so this has to reach Tom.
    link_bugs = [{"stop": s["do"], "tid": s["tid"], "recipient": s["recipient"],
                  **s["gi_link_mismatch"]}
                 for s in stops if s.get("gi_link_mismatch")]

    summary = {
        "driver": driver, "date": date,
        "stops": len(stops),
        "invoices": sum(1 for p, _ in ordered_parts if "ann_" in p),
        "waybills": sum(1 for p, _ in ordered_parts if "wb_" in p),
        "copies": copies,
        "discrepancies": disc,
        "gi_link_mismatches": link_bugs,
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
    L.append("## Wrong Green Invoice link on the LionWheel task")
    if summary.get("gi_link_mismatches"):
        for m in summary["gi_link_mismatches"]:
            L.append(f"- Stop {m['stop']} **{m['recipient']}** (task {m['tid']}): "
                     f"the GI link stamped on the task serves a DIFFERENT document "
                     f"than {m['order']}. Pack used the order-id match — invoice "
                     f"{m['used']} ({m['used_client']}). The driver's own app still "
                     f"shows the stamped link: fix it in LionWheel.")
    else:
        L.append("- None.")
    L.append("")
    L.append("## Inventory-movement proposals (await inbox approval)")
    if proposals:
        for p in proposals:
            L.append(f"- {p['recipient']} (task {p['lw_task_id']}): "
                     f"{p.get('note') or 'goods pickup'}")
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
    ap.add_argument("--missing", default=None,
                    help="';'-separated product names known to be missing/partial. "
                         "Marks X on those lines only and ignores picked_quantity "
                         "(use while picking is still in progress).")
    ap.add_argument("--missing-exempt", default=None,
                    help="';'-separated customer-name substrings exempt from "
                         "--missing (they DO have the product on their invoice).")
    ap.add_argument("--mark-all-lines", action="store_true",
                    help="restore the original full marking: a mark on EVERY line "
                         "(green check / X / partial). Default since 2026-08-04 is "
                         "shortfall-only — X on the short lines, nothing elsewhere.")
    ap.add_argument("--no-packages", action="store_true",
                    help="omit the package-count badge (order id + marks only)")
    ap.add_argument("--all-statuses", action="store_true",
                    help="include UNASSIGNED stops — treat the whole day as confirmed")
    ap.add_argument("--no-workorder", action="store_true",
                    help="omit the LionWheel work-order page; invoices only")
    ap.add_argument("--marks-only-short", action="store_true",
                    help="with --mark-all-lines: full per-line marking, but only "
                         "on orders that fell short; fully-picked orders stay clean")
    a = ap.parse_args()
    date = a.date or (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
    missing = [m.strip() for m in a.missing.split(";") if m.strip()] if a.missing else None
    build(a.driver, date, a.from_stop, a.copies, a.marks_only_short,
          missing_products=missing,
          missing_exempt=[e.strip() for e in a.missing_exempt.split(";") if e.strip()]
                         if a.missing_exempt else None,
          all_statuses=a.all_statuses, show_packages=not a.no_packages,
          shortfall_only=not a.mark_all_lines,
          workorder=not a.no_workorder)


if __name__ == "__main__":
    main()
