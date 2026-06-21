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
            meta = _get_json(GI_BASE.rstrip("/") + f"/documents/{did}")
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


def render_pages(jobs):
    """jobs = [(url, out_pdf, fit_one_page_bool), ...] rendered with the LW session."""
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
    from playwright.sync_api import sync_playwright
    cookies = lw_login_cookies()
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
        ctx = b.new_context(ignore_https_errors=True)
        ctx.add_cookies(cookies)
        for url, out, fit_one in jobs:
            pg = ctx.new_page()
            pg.goto(url, wait_until="networkidle", timeout=60000)
            opts = dict(format="A4", print_background=True,
                        margin={"top": "6mm", "bottom": "6mm", "left": "6mm", "right": "6mm"})
            if fit_one:
                # work order: portrait, scaled so the route table lands on one page
                try:
                    pg.add_style_tag(content="@page{size:A4 portrait} body{zoom:.72}")
                except Exception:
                    pass
                opts["scale"] = 0.72
                opts["page_ranges"] = "1"
            pg.pdf(path=out, **opts)
            pg.close()
        b.close()


# --------------------------------------------------------------------------- #
# non-standard inventory movements -> proposals for the Factory OS inbox
# --------------------------------------------------------------------------- #
MOVE_HINTS = ["החלפ", "החזר", "טעימ", "איסוף סחורה", "קבל", "מתנה", "דגימ"]


def detect_inventory_moves(stops):
    """Conservative: flag stops whose note implies a non-pick stock move.
    We do NOT guess quantities — the proposal carries the verbatim note for
    human approval in the inbox before any stock_ledger entry is posted."""
    out = []
    for s in stops:
        t = s["task"]
        note = (t.get("notes") or "").strip()
        recip = s.get("recipient") or ""
        text = f"{recip} {note}"
        if any(h in text for h in MOVE_HINTS) and not s.get("gi"):
            out.append({
                "lw_task_id": s["tid"],
                "daily_order": s["do"],
                "recipient": recip,
                "note": note,
                "category": "inventory_movement_proposal",
                "status": "open",
                "needs": "item_id + qty + direction(+/-) + ledger type; confirm in inbox",
            })
    return out


# --------------------------------------------------------------------------- #
# work order (page 1) — clean one-page A4 manifest built from the route data
# (the LionWheel SPA route view cannot be forced to a clean single page, and its
#  print_summary is aggregate-only; this reproduces the route, in driving order,
#  arranged to one optimal portrait page).
# --------------------------------------------------------------------------- #
def build_workorder(driver, date, stops, out_pdf):
    import fitz
    from bidi.algorithm import get_display
    fb = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    fr = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    HB = fitz.Font(fontfile=fb)
    HR = fitz.Font(fontfile=fr)
    NAVY = (0.16, 0.27, 0.46)
    GREY = (0.45, 0.48, 0.55)
    LINE = (0.85, 0.87, 0.91)
    dmy = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%d/%m/%Y")
    pkgs = sum(int(s["packages"] or 0) for s in stops)

    doc = fitz.open()
    pg = doc.new_page(width=595, height=842)
    pg.insert_font(fontname="db", fontfile=fb)
    pg.insert_font(fontname="dr", fontfile=fr)

    def rt(x_right, y, text, fs, font="dr", color=(0, 0, 0)):
        disp = get_display(str(text))
        f = HB if font == "db" else HR
        pg.insert_text((x_right - f.text_length(disp, fs), y), disp,
                       fontname=font, fontsize=fs, color=color)

    # header band
    pg.draw_rect(fitz.Rect(0, 0, 595, 70), fill=NAVY, color=NAVY)
    rt(575, 34, f"סידור עבודה — {driver}", 20, "db", (1, 1, 1))
    rt(575, 56, f"{dmy}   ·   {len(stops)} עצירות   ·   {pkgs} חבילות", 11, "dr", (0.85, 0.88, 0.96))

    # column right-edges (RTL): #, שעה, לקוח, עיר, פריטים, חבילות
    COLS = [(578, "#", "do"), (548, "שעה", "eta"), (505, "לקוח", "recipient"),
            (235, "עיר", "city"), (120, "פריטים", "items"), (62, "חב'", "packages")]
    y = 92
    for xr, head, _ in COLS:
        rt(xr, y, head, 9.5, "db", GREY)
    y += 6
    pg.draw_line(fitz.Point(20, y), fitz.Point(578, y), color=LINE, width=1)
    y += 16
    rowh = (812 - y) / max(len(stops), 1)
    rowh = min(rowh, 27)
    for s in stops:
        for xr, _, key in COLS:
            val = s.get(key)
            if key == "recipient":
                val = (val or "")[:34]
            rt(xr, y, "" if val is None else val, 9.5,
               "db" if key == "do" else "dr",
               NAVY if key == "do" else (0.12, 0.14, 0.18))
        pg.draw_line(fitz.Point(20, y + 5), fitz.Point(578, y + 5), color=LINE, width=0.5)
        y += rowh
    rt(575, 832, "LionWheel · route order", 8, "dr", GREY)
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

    # page 1: clean one-page work order built from the route data
    wo = None
    if not from_stop:
        wo = f"{OUT}/_workorder.pdf"
        build_workorder(driver, date, stops, wo)

    # waybills for stops without an invoice, rendered from the LionWheel session
    jobs = [(f"{LW_BASE}/tasks/{s['tid']}/print_waybill", f"{OUT}/wb_{s['tid']}.pdf", False)
            for s in stops if not s["gi"]]
    if jobs:
        render_pages(jobs)

    # invoices: download (link or API) + annotate
    ordered_parts = []
    for s in stops:
        if s["gi"] or (s["task"].get("order_items")):  # invoice stop
            src = f"{OUT}/inv_{s['tid']}.pdf"
            if gi_fetch_invoice(s, src):
                ann = f"{OUT}/ann_{s['tid']}.pdf"
                annotate.annotate(s["task"], src, ann)
                ordered_parts.append((ann, copies))
                continue
        # otherwise: waybill stop
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
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


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
