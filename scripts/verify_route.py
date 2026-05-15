import json, os, sys
from pathlib import Path

route_dir = Path(r'C:\Users\tomw2\GTeveryday Dropbox\Data Center\Tom\AI Agents & Projects\Code Agents\PRODUCTION\.lionwheel-prints\2026-05-14-maksim')
pdf_dir = route_dir / "pdfs"

with open(route_dir / "manifest.json", encoding="utf-8") as f:
    manifest = json.load(f)

ok = 0
missing = 0

for task in manifest["tasks"]:
    order = task["route_order"]
    name = task["recipient_name"]
    wpid = task.get("wp_order_id") or "no-order-id"
    tid = task["task_id"]
    has_url = bool(task["green_invoice_urls"])

    if has_url:
        pdf_path = pdf_dir / f"{tid}.pdf"
        if pdf_path.exists():
            size = pdf_path.stat().st_size
            print(f"OK   [{order:02d}] {name} ({wpid}) - {size} bytes")
            ok += 1
        else:
            print(f"MISS [{order:02d}] {name} ({wpid}) - PDF MISSING!")
            missing += 1
    else:
        print(f"SKIP [{order:02d}] {name} ({wpid}) - no invoice")

print()
print(f"Result: {ok} OK, {missing} MISSING")
if missing > 0:
    sys.exit(1)
