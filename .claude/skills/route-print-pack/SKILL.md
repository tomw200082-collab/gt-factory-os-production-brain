---
name: route-print-pack
description: >-
  Use when Tom asks to prepare or print the daily delivery route pack for a
  driver — e.g. "תכין את המסלול של מחר למקסים", "חבילת הדפסה למסלול",
  "route pack", or the slash command /route-print-pack. The ONLY input is a
  driver name + a date. Produces one print-ready PDF (LionWheel work order page 1,
  then every stop in driving order: real Green Invoice ×2 with picking marks, or
  official LionWheel waybill ×2), proposes any non-standard inventory movements to
  the Factory OS inbox for approval, and emails the file to production@gteveryday.com.
---

# Route Print Pack

Build the daily delivery print pack for **one driver on one date**. Tom gives only
the **driver name** and the **day**; everything else is default and automatic.

## Output (one merged, print-ready PDF)
1. **Page 1** — the LionWheel work order (`daily_route_plan`) for that driver/date,
   fitted to a single A4 portrait page.
2. **Then, every stop in driving order** (`visits.daily_order`):
   - stop **with** a Green Invoice → the **real GI invoice**, annotated, **×2 copies**.
   - stop **without** an invoice (pickup / exchange) → the **official LionWheel
     waybill** (`print_waybill`), **×2 copies**.

## Locked design (per the frontend-design skill — minimal, precise, no defaults)
- Per product line, at the **right margin, precise to the line**:
  **✓ green check** (picked in full) · **✗ terracotta cross** (not picked) ·
  **amber `picked/ordered`** (partial). Vector marks, never letters.
- **Package count** — black, no colour, no box — centered **directly under "מקור"**,
  on the invoice's own page.
- **Last 3 digits** of the order id — top-right, **first page only**.
- Touch **only the named driver's route**. Ignore every other stop.

## How to run
1. **Inputs.** Driver name + date (`YYYY-MM-DD`). If no date given, default = tomorrow.
   `--from-stop N` only when Tom explicitly asks to start mid-route.
2. **Environment.** Ensure deps (install if missing) and confirm secrets:
   ```bash
   python3 -m pip install -q pymupdf pypdf python-bidi playwright
   PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers python3 -m playwright install chromium
   ```
   Required secrets: `LIONWHEEL_API_KEY`, `LIONWHEEL_BASE_URL`,
   `GREENINVOICE_API_BASE_URL`, `GREENINVOICE_KEY_ID`, `GREENINVOICE_SECRET`,
   `LIONWHEEL_WEB_USER`, `LIONWHEEL_WEB_PASSWORD`, `RESEND_API_KEY`.
   If `LIONWHEEL_WEB_USER`/`LIONWHEEL_WEB_PASSWORD` are missing, ask Tom to add them
   as environment secrets (needed for the work order + waybills) — never hard-code.
3. **Build** (from this skill's `scripts/` dir):
   ```bash
   python3 route_pack.py --driver "מקסים" --date 2026-06-22
   ```
   Writes `route_pack_out/route_<driver>_<date>.pdf`, `summary.json`, and
   `inventory_proposals.json`. Sanity-check by rendering a page to PNG with PyMuPDF.
4. **Inventory inbox.** For each item in `inventory_proposals.json` (returns,
   exchanges, tastings, goods received — anything that moves stock outside normal
   picking), INSERT an **open** row into `private_core.exceptions` via the Supabase
   MCP (`category='inventory_movement_proposal'`, `status='open'`, the proposal in
   `raw_payload`, a clear `recommended_action`). Surface them to Tom.
   - **Stock truth is sacred (CLAUDE.md).** This skill only **proposes**. The stock
     move (add or subtract, RM or FG) is posted to `stock_ledger` **only after Tom
     approves in the inbox**, through the system's sanctioned adjustment path —
     never written directly here, and never guessed (quantities/items are confirmed
     by Tom at approval).
5. **Email.** The PDF is compressed on assembly (~3 MB). Send it + a short summary
   to **production@gteveryday.com**:
   ```bash
   python3 send_email.py route_pack_out/summary.json
   ```
   Requirements for delivery to land:
   - The environment must allow outbound egress to `api.resend.com` (it is
     currently blocked here — Cloudflare `error 1010`). If blocked, relay through a
     Supabase Edge Function (Supabase's network reaches Resend), or run where egress
     is allowed.
   - To reach an address other than the Resend account owner, a verified
     `gteveryday.com` sender must exist in Resend; set `ALERT_EMAIL_FROM` to it.
   If the send fails, deliver the PDF to Tom in chat and tell him which requirement
   is missing — do not silently drop it.
6. **Deliver** the PDF to Tom in chat as well.

## Picking discrepancies (credits)
Picking shortfalls are marked on the invoices and listed in the email summary.
**Do not** write credits to the DB — the system auto-creates `credit_tasks` after
the driver marks delivery. (Confirmed live: the pick-bridge creates them on the
terminal LionWheel status.)

## Boundaries
- Read-only on LionWheel, Green Invoice, and the Supabase mirror.
- Only the named driver's route; never other stops or drivers.
- Never write to `stock_ledger`. Inventory moves go to the inbox → human approval.
- The LionWheel web password lives only as an env secret; if it ever appears in
  chat, tell Tom to rotate it.

## Data contracts (discovered, do not guess)
- LionWheel list: `GET {LW_BASE}/api/v1/tasks.json?key=…&limit=…`
- LionWheel task: `GET {LW_BASE}/api/v1/tasks/show/{id}.json?key=…`
  → `driver_str`, `driver_id`, `pickup_at`, `visits[].daily_order`,
    `order_items[].quantity` vs `.picked_quantity`, `packages_quantity`,
    `wp_order_id`, and the GI link in `driver_note` or `notes`.
- LionWheel web (session login at `/users/sign_in`, field `user[username]`):
  work order `GET /drivers/{driver_id}/daily_route_plan?date=DD/MM/YYYY`;
  waybill `GET /tasks/{id}/print_waybill`.
- Green Invoice: token `POST /account/token {id,secret}`; fallback document match
  `POST /documents/search` then `GET /documents/{id}` for the PDF link.
