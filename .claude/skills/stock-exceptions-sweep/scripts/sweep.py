#!/usr/bin/env python3
"""
stock-exceptions-sweep — every LionWheel task that COMPLETED with a physical
stock movement outside the pick bridge becomes a filled inventory-movement
proposal in the Factory OS inbox (pending approval). Proposals only: the
approver's click is what posts to stock_ledger. This script never writes the
database — reads run in read-only transactions, the one write is
POST /api/v1/mutations/inventory-movements as the operator bot.

Runs inside daily-ops-guardian (06:30). Two modes:
  live      tasks COMPLETED in the last 3 days (lw_completed_at), all drivers;
            submits with idempotency_key sweep:<lw_task_id>, so the 3-day
            overlap between runs is harmless.
  --dry-run [--from D --to D]
            backtest window on coalesce(lw_completed_at, captured_at), every
            status (a CANCELED task must produce nothing); prints, never submits.

Evidence order for proposed lines (masterprompt 2026-09-23 §1.1):
  1. the Green Invoice document the task names (title, notes, or its GI link)
  2. the open credit_tasks the supplement fills
  3. an explicit "N × product" in the task text (note_parse, medium)
  4. otherwise an open question — never a guessed quantity.

Env: SUPABASE_ACCESS_TOKEN (read-only Management API query), LIONWHEEL_API_KEY/_BASE_URL,
GREENINVOICE_API_BASE_URL/_KEY_ID/_SECRET, GT_API_EMAIL/GT_API_PASSWORD
(Claude Bot, operator role; or GT_API_TOKEN). Optional: pymupdf, to read a
document number off a GI link when the task names none.
"""
import argparse
import datetime
import json
import os
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "route-print-pack", "scripts"))
import route_pack as rp  # LionWheel + Green Invoice helpers, live-verified (brain PR #206)

API = os.environ.get("GT_API_BASE", "https://gt-factory-os-api-production.up.railway.app").rstrip("/")
SUPABASE_URL = os.environ.get("GT_SUPABASE_URL", "https://rvadsozabmxkkrktwgnv.supabase.co")
# Public anon key (identifies the project, not a secret) — same default as
# report-production/scripts/report_production.mjs.
ANON_KEY = os.environ.get("GT_API_ANON_KEY") or (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ2YWRzb3phYm14a2tya3R3Z252Iiwicm9sZSI6"
    "ImFub24iLCJpYXQiOjE3NzYyNjAwMzEsImV4cCI6MjA5MTgzNjAzMX0.8GV9b60f1sji6N3ZWmSclok6yBB5MkXHO1sJyKyda6Q")
PROJECT_REF = re.search(r"https://([a-z0-9]+)\.supabase\.co", SUPABASE_URL).group(1)
OUT = os.path.join(HERE, "sweep_out")

# Sold unit → stock unit, exactly as the pick bridge scales it
# (gt-factory-os api/src/integrations/lionwheel/reconciliation.ts
# CARTON_BAG_FACTOR, Tom 2026-05-17). Credit tasks and invoices count cartons.
SOLD_TO_STOCK = {"FG-MAT-18G": 22}

# --------------------------------------------------------------------------- #
# classification patterns (titles are Hebrew data — matched, never translated)
# --------------------------------------------------------------------------- #
# §1.1: never `צ.?ק` — that also matches יצחק.
CHEQUE = re.compile(r"(^|[\s\-])צ['׳]?ק(ים)?($|[\s\-])")
SUBCONTRACT = re.compile(r"עמיתה|מדבקות מאצה")
PICKUP = re.compile(r"איסוף|לאסוף")
# pick up here, hand over to someone else — never "…ומסירה למפעל" (that is ours)
HANDOVER = re.compile(r"(ומסירה|ומסירת|ואספקה|ולספק|ולמסור)\s+ל(?!מפעל)")
FREE_GOODS = re.compile(r"ללא חיוב")
SUPPLEMENT = re.compile(r"השלמ|תעודת\s*\S*שלוח")
EXCHANGE = re.compile(r"החלפ|להחליף")
RETURN = re.compile(r"החזר|להחזיר")
TASTING = re.compile(r"טעימ|דגימ")
# §2.5 supplier words + what the backtest showed (container, bottles, packaging)
SUPPLIER_WORDS = re.compile(r"צבר|תבלינ|כימיקל|מדבקות|תוויות|גומיות|פרי הבוסתן|בקבוקים|יקבים|רומיכל|מהמכולה|אריזות")
URL = re.compile(r"https?://\S+")
# 5-digit GI numbers: delivery notes 2xxxx, invoices 6xxxx. Not inside #GT…
# order ids, phone numbers or longer digit runs (landmine 4: exact match only).
DOC_NUMBER = re.compile(r"(?<![\d#A-Za-z])([26]\d{4})(?!\d)")
GI_DELIVERY_NOTE, GI_TAX_INVOICE = 200, 305
GI_TYPE_HE = {GI_DELIVERY_NOTE: "תעודת משלוח", GI_TAX_INVOICE: "חשבונית"}

KIND = {"supplement": "supplement", "free_goods": "free_goods", "exchange": "exchange",
        "return": "return", "tasting": "tasting", "subcontract": "subcontract",
        "delivery": "other", "unclear": "other"}
LABEL = {"supplement": "השלמת סחורה", "free_goods": "סחורה ללא חיוב", "exchange": "החלפת סחורה",
         "return": "החזרת סחורה", "tasting": "טעימה", "subcontract": "קבלנות משנה (עמיתה)",
         "delivery": "אספקה ללא שורות הזמנה", "unclear": "תזוזת מלאי לא מזוהה"}
RETURN_QUESTION = "האם הסחורה חוזרת למלאי או לפחת?"

# note_parse: product words → item family (FG-<FAM>-<size>[-NS]). Names from
# docs/warehouses/catalog-truth.md; the herbal words follow its SKU codes
# (GT-HIB = FRESH, GT-LUI = DETOX, GT-LEM = ENERGY, GT-CHA = CALM,
# GT-JAS = CONSCIOUSNESS, GT-INF-DES = DESERTEA, GT-MAS-CHA = NAMASTEA).
FAMILY_WORDS = [
    ("FRE", r"fresh|פרש|היביסקוס"), ("DET", r"detox|דיטוקס|לואיזה"),
    ("ENE", r"energy|אנרג'?י|אנרגיה"), ("CAL", r"calm|קאלם|קמומיל"),
    ("CON", r"consciousness|קונשס|יסמין"), ("REV", r"revive|ריוו?ייב"),
    ("DES", r"desert|דזרטי|מדברית"), ("NAM", r"namaste|נמסטי|נמסטה|מסאלה"),
]
NO_SUGAR = re.compile(r"ללא סוכר|sugar.?free|no sugar|\bns\b", re.I)
# a size: number + volume/weight unit, not glued to a following letter
SIZE = re.compile(r"(\d+(?:[.,]\d+)?)\s*(ml|מ\"?ל|liter|litre|ליטר|l|ל['׳]?|kg|ק\"?ג|קילו|gr|g|גרם|ג['׳])(?!\w)", re.I)
VOLUME_L = {"l", "ליטר", "liter", "litre", "ל", "ל'", "ל׳"}
WEIGHT_KG = {"kg", "ק\"ג", "קג", "קילו"}
CASES = re.compile(r"(\d+)\s*ארגז|ארגז(?:ים)?\s*(\d+)")
UNITS = re.compile(r"(\d+)\s*(?:[×xX*]|יח|בקבוק|bottle|unit|pcs|שקית|שקיות|פחית|פחיות)|[×xX*]\s*(\d+)", re.I)
BARE = re.compile(r"(?<![\d.,])(\d+)(?![\d.,])")
SINGULAR = re.compile(r"(?<!\w)(בקבוק|שקית|ארגז|יחידה|פחית|קופסא|קופסה)(?![\wי])")
NON_STOCK_DESC = re.compile(r"דמי משלוח|פיקדון")
# --------------------------------------------------------------------------- #
# read-only database access — Supabase Management API over HTTPS (the
# container has no route to the pooler's TCP 5432). read_only=true runs the
# statement in a read-only transaction; $1, $2… are bound parameters.
# --------------------------------------------------------------------------- #
def q(sql_text, *params):
    token = os.environ.get("SUPABASE_ACCESS_TOKEN") or os.environ.get("SUPABASE_MGMT_PAT")
    if not token:
        raise SystemExit("SUPABASE_ACCESS_TOKEN (or SUPABASE_MGMT_PAT) is not set")
    body = json.dumps({"query": sql_text, "parameters": list(params), "read_only": True}).encode()
    req = urllib.request.Request(f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query",
                                 data=body, method="POST",
                                 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json",
                                          "User-Agent": rp.UA})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"query failed: HTTP {e.code} {e.read()[:400]!r}") from None


def load_tasks(args):
    lines = "(select count(*) from private_core.orders_mirror_lines l where l.mirror_id = o.mirror_id)"
    cols = f"""o.mirror_id, o.lw_task_id, o.lw_status, o.wp_order_id, o.lw_destination_recipient_name as title,
               coalesce(o.lw_completed_at, o.captured_at) as at, {lines} as n_lines"""
    if args.dry_run and args.date_from:
        return q(f"""select {cols} from private_core.orders_mirror o
                      where coalesce(o.lw_completed_at, o.captured_at) >= $1::date
                        and coalesce(o.lw_completed_at, o.captured_at) < $2::date + 1
                      order by at""", args.date_from, args.date_to)
    return q(f"""select {cols} from private_core.orders_mirror o
                  where o.lw_status = 'COMPLETED' and o.lw_completed_at >= now() - interval '3 days'
                  order by at""")


class Master:
    """Everything the line derivation reads from the DB, loaded once."""

    def __init__(self):
        self.items = {r["item_id"]: r for r in q(
            "select item_id, item_name, status, coalesce(sales_uom, 'UNIT') as uom, case_pack, barcode "
            "from private_core.items")}
        self.by_barcode = {bare_code(r["barcode"]): r for r in self.items.values()
                           if r["barcode"] and r["status"] == "ACTIVE"}
        self.names = [{"item_id": i, "words": set(re.findall(r"[a-z]{3,}", r["item_name"].lower())) - {"elita"},
                       "size": size_of(r["item_name"])}
                      for i, r in self.items.items() if r["status"] == "ACTIVE" and r["item_name"]]
        self.gi_alias = {bare_code(r["external_sku"]): r for r in q(
            "select external_sku, item_id, mapping_status, internal_units_per_shopify_unit::float8 as units "
            "from private_core.integration_sku_map "
            "where source_channel = 'green_invoice' and approval_status = 'approved' "
            "  and mapping_status in ('active', 'excluded_non_stock')")}
        self.suppliers = q("select supplier_id, supplier_name_short as name from private_core.suppliers "
                           "where status = 'ACTIVE' and supplier_name_short is not null")
        self.open_credits = q("""
            select ct.credit_task_id, ct.item_id, ct.qty_missing::float8 as qty_missing, ct.status,
                   ct.wp_order_id, o.lw_destination_recipient_name as customer, ct.created_at::date as created
              from private_core.credit_tasks ct
              join private_core.orders_mirror o on o.mirror_id = ct.mirror_id
             where ct.status in ('PENDING', 'DEFERRED')
             order by ct.created_at""")

    def active(self, item_id):
        it = self.items.get(item_id)
        return it if it and it["status"] == "ACTIVE" else None

    def resolve(self, text):
        """Product words + size in free text → one active item id, or None.
        Family words first (FG-<FAM>-<size>[-NS]), then English item names
        (e.g. "Nonomimi Sangria 1000ml" → NONOMIMI SANGRIA 1L). Two sizes or no
        single match → None: ambiguity is a question, not a line."""
        sizes = {size_of(m.group(0)) for m in SIZE.finditer(text)} or {size_of(text)} - {None}
        if len(sizes) > 1:
            return None
        size = next(iter(sizes), None)
        fams = {f for f, rx in FAMILY_WORDS if re.search(rx, text, re.I)}
        if len(fams) == 1 and size in ("1000ML", "500ML"):
            item_id = f"FG-{fams.pop()}-{'1L' if size == '1000ML' else '500ML'}" + ("-NS" if NO_SUGAR.search(text) else "")
            return item_id if self.active(item_id) else None
        if fams:
            return None
        words = set(re.findall(r"[a-z]{3,}", text.lower()))
        hits = [n["item_id"] for n in self.names if n["words"] and n["words"] <= words and n["size"] == size]
        return hits[0] if len(hits) == 1 else None

    def fg_line(self, item_id, qty, direction, reason, source, ref, confidence):
        it = self.items[item_id]
        return {"direction": direction, "item_type": "FG", "item_id": item_id, "quantity": round(qty, 4),
                "unit": it["uom"], "reason_code": reason, "source": source,
                "evidence_ref": ref, "confidence": confidence}

    def supplier_for(self, title):
        words = set(tokens(title))
        for s in self.suppliers:
            first = tokens(s["name"])[:1]
            if first and len(first[0]) >= 3 and first[0] in words:
                return s
        return None

    def goods_receipt_near(self, supplier_id, at):
        return q("""select fs.submission_id from private_core.form_submissions fs
                      join private_core.goods_receipts gr using (submission_id)
                     where fs.form_type = 'goods_receipt' and fs.status in ('pending', 'posted')
                       and gr.supplier_id = $1
                       and fs.event_at between $2::timestamptz - interval '2 days'
                                           and $2::timestamptz + interval '2 days'""",
                 supplier_id, at)

    def order_picked(self, wp_order_id):
        return q("""select o.lw_task_id from private_core.orders_mirror o
                     where o.wp_order_id = $1
                       and exists (select 1 from private_core.orders_mirror_lines l where l.mirror_id = o.mirror_id)""",
                 wp_order_id)


# --------------------------------------------------------------------------- #
# text helpers
# --------------------------------------------------------------------------- #
def tokens(s):
    s = re.sub(r"בע[\"״']?מ", " ", s or "")
    return [w for w in re.sub(r"[^\w\s]", " ", s).split() if len(w) >= 2 and not w.isdigit()]


def bare_code(code):
    """GI catalog numbers drop the leading zero some barcodes carry."""
    return str(code or "").strip().lstrip("0")


def size_of(text):
    """'1L', '1000ml', '0.5 ליטר', 'חצי קילו', '18 גרם' → '1000ML' / '500G' …"""
    t = (text or "").lower()
    m = SIZE.search(t)
    if m:
        value, unit = float(m.group(1).replace(",", ".")), m.group(2)
        if unit in ("ml", "מ\"ל", "מל"):
            return f"{round(value)}ML"
        if unit in VOLUME_L:
            return f"{round(value * 1000)}ML"
        return f"{round(value * (1000 if unit in WEIGHT_KG else 1))}G"
    if "חצי ליטר" in t:
        return "500ML"
    if "חצי קילו" in t:
        return "500G"
    if re.search(r"(?<!\w)(ליטר|liter|litre)(?!\w)", t):
        return "1000ML"
    return None


def customer_part(title):
    return re.split(r"\s+[-–]\s*|\s*[-–]\s+", title or "", maxsplit=1)[0].strip()


def same_customer(a, b):
    """Same business AND branch: one name's words all appear in the other's
    (קפה גן סיפור אשדוד ≠ קפה גן סיפור רעננה)."""
    ka, kb = set(tokens(customer_part(a))), set(tokens(customer_part(b)))
    return bool(ka and kb) and (ka <= kb or kb <= ka)


def task_text(row, t):
    """(title, notes): the title is the visit's recipient name — that is where
    the signal lives (landmine 1); notes = every note field, URLs stripped."""
    visits = (t or {}).get("visits") or []
    title = (visits[0].get("recipient_name") if visits else None) or row["title"] or ""
    raw = [(t or {}).get("notes"), (t or {}).get("driver_note"), (t or {}).get("org_note")]
    raw += [v.get("notes") for v in visits]
    notes = [URL.sub("", n).strip() for n in raw if isinstance(n, str)]
    return title.strip(), " | ".join(n for n in notes if n)


def doc_refs(text):
    refs = []
    for m in DOC_NUMBER.finditer(text):
        num, before = m.group(1), text[max(0, m.start() - 30):m.start()]
        if "חשבונית" in before:
            types = [GI_TAX_INVOICE]
        elif re.search(r"תעודת\s*\S*שלוח", before):
            types = [GI_DELIVERY_NOTE]
        else:   # no word: the number range decides first, the other type second
            types = [GI_DELIVERY_NOTE, GI_TAX_INVOICE] if num[0] == "2" else [GI_TAX_INVOICE, GI_DELIVERY_NOTE]
        if all(r[0] != num for r in refs):
            refs.append((num, types))
    return refs


# --------------------------------------------------------------------------- #
# classification
# --------------------------------------------------------------------------- #
def classify(row, title, notes, master):
    if row["lw_status"] != "COMPLETED":
        return "not_completed"
    if CHEQUE.search(title):
        return "cheque"
    text = f"{title} | {notes}"
    if row["n_lines"] > 0:
        # The pick bridge already posted what the order carried; only a movement
        # the order does not carry is ours.
        for cls, rx in (("exchange", EXCHANGE), ("return", RETURN), ("tasting", TASTING), ("free_goods", FREE_GOODS)):
            if rx.search(text):
                return cls
        return "order"
    if SUBCONTRACT.search(title):
        return "subcontract"
    if PICKUP.search(text) and HANDOVER.search(text):
        return "transfer"
    if PICKUP.search(title) and (SUPPLIER_WORDS.search(title) or master.supplier_for(title)):
        return "supplier"   # a goods receipt, not an inventory movement (§1.1)
    if FREE_GOODS.search(text):
        return "free_goods"
    if SUPPLEMENT.search(title):
        return "supplement"
    if EXCHANGE.search(text):
        return "exchange"
    if RETURN.search(text):
        return "return"
    if TASTING.search(text):
        return "tasting"
    if PICKUP.search(title):
        return "return"     # collected from a customer
    if doc_refs(title):
        return "delivery"
    return "unclear"


# --------------------------------------------------------------------------- #
# Green Invoice (fields as seen live 2026-09-23 — route-print-pack SKILL.md
# Data contracts): search {number, type:[code]}, items[].income[].catalogNum
# = items.barcode, .quantity, .description; client.name; remarks "#GT…".
# --------------------------------------------------------------------------- #
_GI = {}


def gi_doc(num, types):
    for typ in types:
        key = (num, typ)
        if key not in _GI:
            hdr = {"Authorization": f"Bearer {rp.gi_token()}"}
            res = rp._post_json(rp.GI_BASE.rstrip("/") + "/documents/search",
                                {"number": num, "type": [typ], "page": 1, "pageSize": 5}, hdr)
            items = res.get("items") or []
            _GI[key] = items[0] if len(items) == 1 else None
        if _GI[key]:
            return _GI[key]
    return None


def doc_from_link(t):
    """The task names no number but carries a GI link: read the number off the
    PDF, then confirm it through the API (the API, not the PDF, gives lines)."""
    link = rp.gi_link(t or {})
    if not link:
        return None, None
    try:
        import pymupdf
        pdf = rp._get(link)
        with pymupdf.open(stream=pdf, filetype="pdf") as d:
            text = d[0].get_text()
    except Exception as e:  # no pymupdf / dead link — the caller asks instead
        return None, f"קישור Green Invoice במשימה לא נקרא ({type(e).__name__})"
    for m in re.finditer(r"(?<!\d)(\d{5})\s*(תעודת משלוח|חשבונית מס)", text):
        typ = GI_DELIVERY_NOTE if m.group(2) == "תעודת משלוח" else GI_TAX_INVOICE
        doc = gi_doc(m.group(1), [typ])
        if doc:
            return doc, None
    return None, "קישור Green Invoice במשימה — מספר המסמך לא זוהה"


def gi_evidence(doc):
    return {"type": "gi_document", "ref": f"{GI_TYPE_HE.get(doc.get('type'), doc.get('type'))} {doc.get('number')}",
            "url": ((doc.get("url") or {}).get("origin") or None)}


def gi_lines(doc, master, p, direction="out", reason="goods_out"):
    """Every stock line of the document → a proposed line; a line we cannot map
    becomes an open question, never a guess. Catalog number first (barcode or
    the approved green_invoice alias), then the line description."""
    lines, ref = [], f"GI:{doc.get('type')}:{doc.get('number')}"
    for it in doc.get("income") or []:
        code, desc = bare_code(it.get("catalogNum")), str(it.get("description") or "")
        qty = float(it.get("quantity") or 0)
        alias = master.gi_alias.get(code) if code else None
        if (alias and alias["mapping_status"] == "excluded_non_stock") or NON_STOCK_DESC.search(desc):
            continue
        item, factor, confidence = master.by_barcode.get(code) if code else None, 1, "high"
        if item:
            factor = SOLD_TO_STOCK.get(item["item_id"], 1)
        elif alias and master.active(alias["item_id"]):
            item, factor = master.items[alias["item_id"]], alias["units"] or 1
        elif master.resolve(desc):
            item = master.items[master.resolve(desc)]
            factor, confidence = SOLD_TO_STOCK.get(item["item_id"], 1), "medium"
        if not item or qty <= 0:
            p["open_questions"].append(
                f"שורה ב{GI_TYPE_HE.get(doc.get('type'), '')} {doc.get('number')} לא מופתה לפריט: "
                f"{desc} ×{qty:g} (קוד {it.get('catalogNum') or 'חסר'})")
            continue
        lines.append(master.fg_line(item["item_id"], qty * factor, direction, reason, "gi_document", ref, confidence))
    return lines


# --------------------------------------------------------------------------- #
# note_parse — explicit product, size and quantity only
# --------------------------------------------------------------------------- #
def note_lines(text, master, direction, reason):
    lines, unparsed = [], []
    for seg in re.split(r"[,;\n|+]|\.(?=\s|$)|\s+ו(?=\d|לאסוף|לספק|להחזיר|לקחת)", text):
        seg = seg.strip()
        if not seg:
            continue
        item_id = None if "מכל סוג" in seg else master.resolve(seg)
        if not item_id and not re.search(r"\d", seg):
            continue
        rest = SIZE.sub(" ", seg)
        cases, units, bare = CASES.search(rest), UNITS.search(rest), BARE.findall(rest)
        item = master.active(item_id) if item_id else None
        qty, confidence = None, "medium"
        if item and cases and not units and item["case_pack"]:
            qty = int(cases.group(1) or cases.group(2)) * float(item["case_pack"])
        elif item and units:
            qty = int(units.group(1) or units.group(2))
        elif item and not cases and len(bare) == 1:
            qty = int(bare[0])
        elif item and not bare and SINGULAR.search(rest):
            # "בקבוק דיטוקס 0.5 ליטר" — one, said in words
            one = SINGULAR.search(rest).group(1)
            qty = float(item["case_pack"]) if one == "ארגז" and item["case_pack"] else 1
            confidence = "low"
        if not item or not qty:
            if item or cases or units or any(rx and re.search(rx, seg, re.I) for _, rx in FAMILY_WORDS):
                unparsed.append(seg)
            continue
        lines.append(master.fg_line(item_id, qty, direction, reason, "note_parse", seg[:200], confidence))
    return lines, unparsed


# --------------------------------------------------------------------------- #
# per-class derivation
# --------------------------------------------------------------------------- #
def new_proposal(row, t, title, notes, cls):
    ev = [{"type": "lionwheel_task", "ref": str(row["lw_task_id"])}]
    if (t or {}).get("pod_link"):
        ev[0]["url"] = t["pod_link"]
    return {"class": cls, "lw_task_id": row["lw_task_id"], "kind": KIND[cls], "event_at": row["at"],
            "summary": f"{LABEL[cls]} — {customer_part(title) or title}"[:500],
            "recipient": title[:500], "note": notes[:4000] or None, "proposed_lines": [],
            "open_questions": [], "evidence": ev, "credit_task_ids": [], "rationale": ""}


def supplement_from_invoice(doc, p, master):
    """An invoice named on a supplement is the ORIGINAL order's invoice: the
    goods now going out are that order's open shortage, not the invoice."""
    m = re.search(r"#GT\d+", doc.get("remarks") or "")
    tasks = [c for c in master.open_credits if m and c["wp_order_id"] == m.group(0)]
    if not tasks:
        closed = q("select item_id, qty_missing::float8 as qty, status from private_core.credit_tasks "
                   "where wp_order_id = $1", m.group(0)) if m else []
        was = "; ".join(f"{c['item_id']} ×{c['qty']:g} {c['status']}" for c in closed)
        p["open_questions"].append(
            f"חשבונית {doc.get('number')}"
            + (f" (הזמנה {m.group(0)})" if m else "")
            + ": אין חוסר ליקוט פתוח"
            + (f" (החוסרים כבר סגורים: {was})" if was else "")
            + " — אילו פריטים ובאיזו כמות סופקו בהשלמה?")
        return []
    lines = []
    for c in tasks:
        if not master.active(c["item_id"]):
            p["open_questions"].append(f"חוסר {c['item_id']} ×{c['qty_missing']:g} ({c['wp_order_id']}): "
                                       "הפריט אינו פעיל — מה סופק במקומו?")
            continue
        p["credit_task_ids"].append(c["credit_task_id"])
        lines.append(master.fg_line(c["item_id"], c["qty_missing"] * SOLD_TO_STOCK.get(c["item_id"], 1), "out",
                                    "goods_out", "credit_task", c["credit_task_id"], "high"))
    return lines


def link_customer_credits(p, title, master):
    """Open shortages of the same customer whose item this supplement carries:
    approval closes them when the quantity covers them."""
    items = {line["item_id"] for line in p["proposed_lines"] if line["direction"] == "out"}
    for c in master.open_credits:
        if c["item_id"] in items and c["credit_task_id"] not in p["credit_task_ids"] and same_customer(c["customer"], title):
            p["credit_task_ids"].append(c["credit_task_id"])
            p["evidence"].append({"type": "credit_task", "ref": f"{c['credit_task_id']} ({c['wp_order_id']}, "
                                  f"{c['item_id']} ×{c['qty_missing']:g})"})


def derive(row, t, title, notes, cls, master):
    p = new_proposal(row, t, title, notes, cls)
    text = f"{title} | {notes}"
    docs, doc_errors = [], []
    refs = doc_refs(title + " | " + notes) if row["n_lines"] == 0 else []
    for num, types in refs:
        doc = gi_doc(num, types)
        if not doc:
            doc_errors.append(f"מסמך {num} לא נמצא ב-Green Invoice")
        elif not set(tokens(customer_part(title))) & set(tokens((doc.get("client") or {}).get("name"))):
            doc_errors.append(f"מסמך {num} שייך ל-{(doc.get('client') or {}).get('name')}, לא ל-{customer_part(title)}")
        else:
            docs.append(doc)
    if not docs and cls in ("supplement", "free_goods", "unclear") and row["n_lines"] == 0:
        doc, err = doc_from_link(t)
        if doc:
            docs.append(doc)
            cls = p["class"] = "delivery" if cls == "unclear" else cls
            p["kind"] = KIND[cls]
            p["summary"] = f"{LABEL[cls]} — {customer_part(title) or title}"[:500]
        elif err:
            doc_errors.append(err)
    for doc in docs:
        p["evidence"].append(gi_evidence(doc))
    p["open_questions"] += doc_errors

    if cls in ("supplement", "free_goods", "delivery", "unclear"):
        for doc in docs:
            if doc.get("type") == GI_TAX_INVOICE and cls == "supplement":
                p["proposed_lines"] += supplement_from_invoice(doc, p, master)
                continue
            m = re.search(r"#GT\d+", doc.get("remarks") or "")
            picked = master.order_picked(m.group(0)) if (m and doc.get("type") == GI_TAX_INVOICE) else []
            if picked:
                p["open_questions"].append(
                    f"החשבונית {doc.get('number')} היא של הזמנה {m.group(0)} שכבר לוקטה במשימה "
                    f"{picked[0]['lw_task_id']} — מה יצא במשימה הזו מעבר לליקוט?")
                continue
            p["proposed_lines"] += gi_lines(doc, master, p)
        if not docs:
            lines, unparsed = note_lines(text, master, "out", "goods_out")
            p["proposed_lines"] += lines
            for seg in unparsed:
                p["open_questions"].append(f"לא זוהו פריט וכמות מתוך: \"{seg}\"")
        if cls == "supplement" and not any(d.get("type") == GI_TAX_INVOICE for d in docs):
            link_customer_credits(p, title, master)
        if cls == "supplement":
            if not p["proposed_lines"] and not docs:
                cands = [c for c in master.open_credits if same_customer(c["customer"], title)]
                listing = ", ".join(f"{c['item_id']} ×{c['qty_missing']:g} ({c['wp_order_id']})" for c in cands[:12])
                p["open_questions"].append(
                    "השלמה בלי מסמך מזוהה — אילו פריטים ובאיזו כמות סופקו?"
                    + (f" חוסרים פתוחים של הלקוח: {listing}" if listing else " ללקוח אין חוסרים פתוחים."))
        if row["n_lines"] > 0 and not p["proposed_lines"]:
            p["open_questions"].append("אילו פריטים נוספו להזמנה ללא חיוב ובאיזו כמות? "
                                       "(פריט שכבר מופיע בשורות ההזמנה ירד בליקוט — לדחות.)")
        if not p["proposed_lines"] and not p["open_questions"]:
            p["open_questions"].append("מה יצא מהמלאי במשימה הזו ובאיזו כמות?")
    elif cls in ("return", "tasting", "exchange"):
        direction, reason = {"return": ("in", "return_in"), "tasting": ("out", "tasting"),
                             "exchange": ("in", "exchange_in")}[cls]
        lines, unparsed = note_lines(text, master, direction, reason)
        p["proposed_lines"] += lines
        if cls == "exchange" and row["n_lines"] == 0:
            # the replacement left too and no order line carried it
            p["proposed_lines"] += [dict(line, direction="out", reason_code="exchange_out") for line in lines]
        for seg in unparsed:
            p["open_questions"].append(f"לא זוהו פריט וכמות מתוך: \"{seg}\"")
        if not lines:
            p["open_questions"].append({
                "return": "מה נאסף מהלקוח ובאיזו כמות?",
                "tasting": "אילו פריטים יצאו לטעימה ובאיזו כמות?",
                "exchange": "מה הוחזר ומה סופק במקומו, ובאיזו כמות?",
            }[cls])
        if cls in ("return", "exchange"):
            p["open_questions"].append(RETURN_QUESTION)
    elif cls == "subcontract":
        # masterprompt W2: PKG out when delivering to the subcontractor, FG in
        # when collecting — the rule itself is confirmed by the approver.
        direction, reason = ("out", "goods_out") if re.search(r"מסירת", title) and not PICKUP.search(title) \
            else ("in", "goods_pickup")
        lines, unparsed = note_lines(text, master, direction, reason)
        p["proposed_lines"] += lines
        for seg in unparsed:
            p["open_questions"].append(f"לא זוהו פריט וכמות מתוך: \"{seg}\"")
        p["open_questions"].append(
            "קבלנות משנה (עמיתה): מה נאסף (מוצר מוגמר נכנס) ומה נמסר (אריזה/חומר גלם יוצא), ובאיזו כמות? "
            "לאשר שזה הכלל: אריזה יוצאת במסירה, מוצר מוגמר נכנס באיסוף.")

    p["rationale"] = rationale(row, title, cls, p)
    return p


def rationale(row, title, cls, p):
    when = str(row["at"])[:10]
    outs = [f"{l['quantity']:g} {l['item_id']}" for l in p["proposed_lines"] if l["direction"] == "out"]
    ins = [f"{l['quantity']:g} {l['item_id']}" for l in p["proposed_lines"] if l["direction"] == "in"]
    src = sorted({l["source"] for l in p["proposed_lines"]})
    parts = [
        f"משימת LionWheel {row['lw_task_id']} ({title}) הושלמה ב-{when} ללא שורות הזמנה שגשר הליקוט רואה"
        if row["n_lines"] == 0 else
        f"משימת LionWheel {row['lw_task_id']} ({title}) הושלמה ב-{when}; מעבר לשורות ההזמנה שכבר לוקטו",
        f"סוג: {LABEL[cls]}.",
        f"יוצא מהמלאי: {', '.join(outs)}." if outs else "יוצא מהמלאי: לא נגזר.",
        f"נכנס למלאי: {', '.join(ins)}." if ins else "נכנס למלאי: לא נגזר.",
        f"מקור השורות: {', '.join(src)}." if src else "לא נגזרו שורות — ראו שאלות פתוחות.",
        "למה: התנועה הפיזית קרתה מחוץ לגשר הליקוט, ולכן המלאי במערכת לא השתנה עד לאישור.",
    ]
    if p["credit_task_ids"]:
        parts.append(f"באישור ייסגרו כ'סופק' {len(p['credit_task_ids'])} חוסרי ליקוט מקושרים, רק אם הכמות מכסה אותם.")
    return " ".join(parts)[:4000]


def email_line(row, title, cls, master):
    if cls == "transfer":
        return f"איסוף ומסירה בין צדדים, לא דרך המפעל (ללא השפעה על המלאי): {title} — משימה {row['lw_task_id']}"
    if cls == "supplier":
        s = master.supplier_for(title)
        if s and master.goods_receipt_near(s["supplier_id"], row["at"]):
            return None
        who = f"{s['name']} ({s['supplier_id']})" if s else "ספק לא זוהה"
        return (f"איסוף מספק בלי קבלת סחורה ±2 ימים: {title} — משימה {row['lw_task_id']}, "
                f"{str(row['at'])[:10]}, {who}")
    return None


# --------------------------------------------------------------------------- #
# submit (live only) — the bot is an operator: it proposes, it never approves
# --------------------------------------------------------------------------- #
def bot_token():
    if os.environ.get("GT_API_TOKEN"):
        return os.environ["GT_API_TOKEN"]
    body = json.dumps({"email": os.environ["GT_API_EMAIL"], "password": os.environ["GT_API_PASSWORD"]}).encode()
    req = urllib.request.Request(f"{SUPABASE_URL}/auth/v1/token?grant_type=password", data=body, method="POST",
                                 headers={"apikey": ANON_KEY, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["access_token"]


SUBMIT_FIELDS = ("kind", "event_at", "summary", "recipient", "note", "proposed_lines", "rationale",
                 "open_questions", "evidence", "credit_task_ids")


def submit(p, token):
    body = {k: p[k] for k in SUBMIT_FIELDS if p.get(k) not in (None, "", [])}
    body["idempotency_key"] = f"sweep:{p['lw_task_id']}"
    body["source_ref"] = str(p["lw_task_id"])
    body["event_at"] = datetime.datetime.fromisoformat(str(p["event_at"])).astimezone(
        datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    req = urllib.request.Request(f"{API}/api/v1/mutations/inventory-movements", method="POST",
                                 data=json.dumps(body, ensure_ascii=False).encode(),
                                 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


# --------------------------------------------------------------------------- #
def run(args):
    os.makedirs(OUT, exist_ok=True)
    rows = load_tasks(args)
    master = Master()
    cache_path = os.path.join(OUT, "lw_cache.json")
    cache = json.load(open(cache_path)) if (args.dry_run and os.path.exists(cache_path)) else {}

    def fetch(tid):
        try:
            return rp.lw_task(tid)
        except Exception as e:
            return {"_error": f"{type(e).__name__}: {e}"}

    todo = [r["lw_task_id"] for r in rows if str(r["lw_task_id"]) not in cache]
    with ThreadPoolExecutor(8) as ex:
        for tid, t in zip(todo, ex.map(fetch, todo)):
            cache[str(tid)] = t
    if args.dry_run:
        json.dump(cache, open(cache_path, "w"), ensure_ascii=False)

    report = {"mode": "dry-run" if args.dry_run else "live",
              "window": [args.date_from, args.date_to] if args.date_from else "completed, last 3 days",
              "tasks": len(rows), "counts": {}, "proposals": [], "email_lines": [], "cheques": [],
              "errors": [], "submitted": []}
    for row in rows:
        t = cache.get(str(row["lw_task_id"]))
        if t and t.get("_error"):
            report["errors"].append({"lw_task_id": row["lw_task_id"], "error": t["_error"]})
            t = None
        title, notes = task_text(row, t)
        cls = classify(row, title, notes, master)
        report["counts"][cls] = report["counts"].get(cls, 0) + 1
        if cls in ("not_completed", "order"):
            continue
        if cls == "cheque":
            report["cheques"].append({"lw_task_id": row["lw_task_id"], "title": title})
            continue
        if cls in ("transfer", "supplier"):
            line = email_line(row, title, cls, master)
            if line:
                report["email_lines"].append({"class": cls, "lw_task_id": row["lw_task_id"], "text": line})
            continue
        try:
            p = derive(row, t, title, notes, cls, master)
        except Exception as e:
            report["errors"].append({"lw_task_id": row["lw_task_id"], "error": f"{type(e).__name__}: {e}"})
            continue
        assert p["proposed_lines"] or p["open_questions"], p["lw_task_id"]   # nothing reaches the inbox empty
        report["proposals"].append(p)

    if not args.dry_run and report["proposals"]:
        token = bot_token()
        for p in report["proposals"]:
            status, body = submit(p, token)
            report["submitted"].append({"lw_task_id": p["lw_task_id"], "status": status,
                                        "submission_id": body.get("submission_id"),
                                        "replay": body.get("idempotent_replay"),
                                        "reason": body.get("reason_code") or body.get("validation_errors")})
    json.dump(report, open(os.path.join(OUT, "sweep_report.json"), "w"), ensure_ascii=False, indent=1, default=str)
    print_summary(report)
    return report


def print_summary(r):
    print(f"stock-exceptions-sweep {r['mode']} — window {r['window']} — {r['tasks']} tasks")
    print("counts:", json.dumps(dict(sorted(r["counts"].items())), ensure_ascii=False))
    print(f"cheques skipped ({len(r['cheques'])}):")
    for c in r["cheques"]:
        print(f"  {c['lw_task_id']}  {c['title']}")
    print(f"proposals ({len(r['proposals'])}):")
    for p in r["proposals"]:
        lines = "; ".join(f"{l['direction']} {l['quantity']:g} {l['item_id']} [{l['source']}/{l['confidence']}]"
                          for l in p["proposed_lines"]) or "—"
        print(f"  {p['lw_task_id']} [{p['class']}] {p['summary']}")
        print(f"      lines: {lines}")
        for oq in p["open_questions"]:
            print(f"      ? {oq}")
        if p["credit_task_ids"]:
            print(f"      credit tasks: {len(p['credit_task_ids'])}")
    print(f"email lines ({len(r['email_lines'])}):")
    for e in r["email_lines"]:
        print(f"  - {e['text']}")
    if r["errors"]:
        print(f"errors ({len(r['errors'])}):")
        for e in r["errors"]:
            print(f"  ! {e['lw_task_id']}: {e['error']}")
    for s in r["submitted"]:
        print(f"  submitted {s['lw_task_id']}: HTTP {s['status']} {s.get('submission_id') or ''} "
              f"{'(replay)' if s.get('replay') else ''} {s.get('reason') or ''}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dry-run", action="store_true", help="print proposals, submit nothing")
    ap.add_argument("--from", dest="date_from", help="backtest window start YYYY-MM-DD (dry-run only)")
    ap.add_argument("--to", dest="date_to", help="backtest window end YYYY-MM-DD, inclusive (dry-run only)")
    a = ap.parse_args()
    if (a.date_from or a.date_to) and not (a.dry_run and a.date_from and a.date_to):
        ap.error("--from/--to need --dry-run and both dates")
    run(a)


if __name__ == "__main__":
    main()
