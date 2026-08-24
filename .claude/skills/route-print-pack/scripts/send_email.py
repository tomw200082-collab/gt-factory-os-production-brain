#!/usr/bin/env python3
"""
Email the finished route pack to production@gteveryday.com.

The build sandbox cannot reach api.resend.com (Cloudflare 1010), so we relay
through the Supabase Edge Function `email_route_pack` (Supabase's network reaches
Resend). The function attaches the PDF and sends via Resend.

Usage: send_email.py route_pack_out/summary.json
Env: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY (to invoke the relay).

NOTE: delivery to production@gteveryday.com requires the gteveryday.com domain to
be verified at resend.com/domains, after which ALERT_EMAIL_FROM (an edge secret)
must be a @gteveryday.com sender. Until then Resend (test mode) only delivers to
the account owner; the relay returns the Resend error and the caller should hand
the PDF to Tom in chat instead.
"""
import os, sys, json, base64, urllib.request

# Target recipient. Interim = tom@gteveryday.com (the Resend account owner, the
# only address deliverable in test mode). Flip to production@gteveryday.com once
# gteveryday.com is verified at resend.com/domains (and ALERT_EMAIL_FROM is set to
# a @gteveryday.com sender). Override anytime with ROUTE_PACK_EMAIL_TO.
TO = os.environ.get("ROUTE_PACK_EMAIL_TO", "tom@gteveryday.com")


def main(summary_path):
    s = json.load(open(summary_path))
    pdf = s["file"]
    base = os.environ["SUPABASE_URL"].rstrip("/")
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

    disc = s.get("discrepancies", [])
    lines = [
        f"מסלול הפצה — {s['driver']} — {s['date']}",
        f"{s['stops']} עצירות · {s['invoices']} חשבוניות (×{s['copies']}) · {s['waybills']} תעודות משלוח",
        "",
    ]
    if not s.get("picking_recorded", True):
        lines.append("שים לב: הליקוט עוד לא דווח כשהקובץ נבנה — החשבוניות יצאו "
                     "בלי סימוני ליקוט, בכוונה. לבנות שוב אחרי נעילת הליקוט.")
    elif disc:
        lines.append(f"הפרשי ליקוט ({len(disc)}):")
        for d in disc:
            lines.append(f"  עצירה {d['stop']} · {d['recipient']} · {d['item']} · לוקט {d['picked']}/{d['ordered']}")
    else:
        lines.append("אין הפרשי ליקוט.")
    um = s.get("unmarked_lines") or []
    if um:
        lines.append("")
        lines.append("שורות שלא ניתן היה לסמן על החשבונית — לבדוק ידנית:")
        for u in um:
            lines.append(f"  עצירה {u['stop']} · {u['recipient']} · {', '.join(u['items'])}")
    ck = s.get("check_pickups_skipped") or []
    if ck:
        lines.append("")
        lines.append("איסופי צ'קים שהושמטו מהקובץ (אין סחורה, אין ניירת): "
                     + ", ".join(c["recipient"] or "?" for c in ck))
    if s.get("inventory_proposals"):
        lines.append("")
        lines.append(f"תזוזות מלאי לא-רגילות שממתינות לאישור ב-inbox: {s['inventory_proposals']}")

    payload = {
        "pdf_base64": base64.b64encode(open(pdf, "rb").read()).decode(),
        "filename": os.path.basename(pdf),
        "subject": f"מסלול הפצה {s['driver']} · {s['date']}",
        "text": "\n".join(lines),
        "to": TO,
    }
    req = urllib.request.Request(
        base + "/functions/v1/email_route_pack",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        out = json.loads(r.read().decode())
    print(json.dumps(out, ensure_ascii=False))
    if not out.get("ok"):
        sys.exit("email relay reported failure (see Resend error above) — hand the PDF to Tom in chat")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "route_pack_out/summary.json")
