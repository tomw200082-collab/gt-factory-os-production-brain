#!/usr/bin/env python3
"""
Email the finished route pack to production@gteveryday.com.

The build sandbox cannot reach api.resend.com (Cloudflare 1010), so we relay
through the Supabase Edge Function `email_route_pack` (Supabase's network reaches
Resend). The function attaches the PDF and sends via Resend.

Usage: send_email.py route_pack_out/summary.json
Env: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY (to invoke the relay).

NOTE: Resend verifies the SENDER domain, never the recipient. The relay sends from
the verified greentea-everyday.com, so production@gteveryday.com receives normally
and gteveryday.com needs no DNS records. If a send ever 403s with "you can only
send testing emails to your own email address", the relay has fallen back to
Resend's test sender — check ALERT_EMAIL_FROM and the relay's default, not DNS.
"""
import os, sys, json, base64, urllib.request

# Target recipient. production@gteveryday.com since 2026-09-06: Resend verifies
# the SENDER domain only, and the relay now sends from the verified
# greentea-everyday.com, so the recipient domain needs nothing. (The old
# tom@-only interim existed because the relay defaulted to Resend's test sender,
# which delivers to the account owner alone.) Override with ROUTE_PACK_EMAIL_TO.
TO = os.environ.get("ROUTE_PACK_EMAIL_TO", "production@gteveryday.com")


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
    if disc:
        lines.append(f"הפרשי ליקוט ({len(disc)}):")
        for d in disc:
            lines.append(f"  עצירה {d['stop']} · {d['recipient']} · {d['item']} · לוקט {d['picked']}/{d['ordered']}")
    else:
        lines.append("אין הפרשי ליקוט.")
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
