#!/usr/bin/env python3
"""
Email the finished route pack to production@gteveryday.com via Resend.

Usage: send_email.py route_pack_out/summary.json
Reads the summary + attaches summary["file"]. Short Hebrew body.

Env: RESEND_API_KEY (required), ALERT_EMAIL_FROM (optional; a verified
gteveryday.com sender is recommended, else falls back to onboarding@resend.dev).
"""
import os, sys, json, base64, urllib.request

TO = "production@gteveryday.com"


def main(summary_path):
    s = json.load(open(summary_path))
    pdf = s["file"]
    key = os.environ["RESEND_API_KEY"]
    sender = os.environ.get("ALERT_EMAIL_FROM", "onboarding@resend.dev")

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
    body = "\n".join(lines)

    with open(pdf, "rb") as f:
        content = base64.b64encode(f.read()).decode()

    payload = {
        "from": f"GT Factory OS <{sender}>",
        "to": [TO],
        "subject": f"מסלול הפצה {s['driver']} · {s['date']}",
        "text": body,
        "attachments": [{"filename": os.path.basename(pdf), "content": content}],
    }
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as r:
        print(r.status, r.read().decode())


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "route_pack_out/summary.json")
