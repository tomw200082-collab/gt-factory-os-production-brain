"""
Merge LionWheel route invoices into combined-Nx.pdf.
Each invoice appears N times consecutively before moving to the next task.
Stamps the last-3 digits of wp_order_id in large bold text at top-right of every page.
"""
import argparse
import json
import sys
from pathlib import Path

from pypdf import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io


def make_overlay(label: str, page_width: float, page_height: float) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(page_width, page_height))
    c.setFont("Helvetica-Bold", 48)
    c.setFillColorRGB(0, 0, 0)
    text_width = c.stringWidth(label, "Helvetica-Bold", 48)
    x = page_width - text_width - 20
    y = page_height - 65
    c.drawString(x, y, label)
    c.save()
    buf.seek(0)
    return buf.read()


def merge(route_dir: Path, copies: int) -> Path:
    manifest_path = route_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    pdf_dir = route_dir / "pdfs"
    writer = PdfWriter()
    expected_pages = 0

    for task in manifest["tasks"]:
        if not task.get("green_invoice_urls"):
            continue
        task_id = task["task_id"]
        pdf_path = pdf_dir / f"{task_id}.pdf"
        if not pdf_path.exists():
            print(f"  WARN: PDF missing for task {task_id}, skipping", file=sys.stderr)
            continue

        wp = task.get("wp_order_id") or ""
        digits = "".join(ch for ch in wp if ch.isdigit())
        label = digits[-3:] if len(digits) >= 3 else digits

        reader = PdfReader(str(pdf_path))
        n_pages = len(reader.pages)

        # Build overlay PDF once per task
        overlays = []
        for i, page in enumerate(reader.pages):
            pw = float(page.mediabox.width)
            ph = float(page.mediabox.height)
            if label:
                overlay_bytes = make_overlay(label, pw, ph)
                overlay_reader = PdfReader(io.BytesIO(overlay_bytes))
                page.merge_page(overlay_reader.pages[0])
            overlays.append(page)

        for _ in range(copies):
            for page in overlays:
                writer.add_page(page)
            expected_pages += n_pages

    out_path = route_dir / f"combined-{copies}x.pdf"
    with open(out_path, "wb") as f:
        writer.write(f)

    verify_reader = PdfReader(str(out_path))
    actual_pages = len(verify_reader.pages)

    if actual_pages != expected_pages:
        print(f"ERROR: page count mismatch — expected {expected_pages}, got {actual_pages}", file=sys.stderr)
        sys.exit(1)

    print(f"OK: {out_path} — {actual_pages} pages ({copies}x)")
    return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("route_dir")
    parser.add_argument("--copies", type=int, default=2)
    args = parser.parse_args()
    merge(Path(args.route_dir), args.copies)
