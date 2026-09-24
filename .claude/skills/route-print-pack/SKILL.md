---
name: route-print-pack
description: >-
  Use when Tom asks to prepare or print the daily delivery route pack for a
  driver — e.g. "תכין את המסלול של מחר למקסים", "חבילת הדפסה למסלול",
  "route pack", or the slash command /route-print-pack. The ONLY input is a
  driver name + a date — and since 2026-07-22 both have defaults: driver = the
  route driver (מיידן, per ../daily-delivery-dispatch/drivers.json
  default_route_driver), date = the next working day ("מחר" on Thursday means
  Sunday). Produces one print-ready PDF (LionWheel work order page 1,
  then every stop in driving order: real Green Invoice ×2 with picking marks, or
  official LionWheel waybill ×2), flags stops that move stock outside picking
  (the inbox proposal for those is made after delivery by stock-exceptions-sweep),
  and emails the file to production@gteveryday.com.
---

# Route Print Pack

Build the daily delivery print pack for **one driver on one date**. Tom gives only
the **driver name** and the **day**; everything else is default and automatic.

## Output (one merged, print-ready PDF)
1. **Page 1** — the LionWheel work order (`daily_route_plan`) for that driver/date,
   fitted to a single A4 portrait page.
2. **Then, every stop in driving order** (`visits.daily_order`):
   - stop **with** a Green Invoice → the **real GI invoice**, annotated, **×2 copies**.
   - **Invoices are the rule — a waybill is a genuine last resort.** Every stop
     that has *any* Green Invoice document gets that invoice, even when the order
     is days/weeks old: the GI match scans the **full document history** (paginated,
     newest-first), not just the most recent page, and matches the exact `#GT…`
     order id stamped in the document `remarks`. A stop only falls back to the
     **official LionWheel waybill** (`print_waybill`, ×2) when the order genuinely
     has **no** Green Invoice document (true pickup / exchange). Never let a stock
     order that *does* have an invoice degrade to a waybill.
   - **Save paper — trim blank tail pages.** Green Invoice sometimes spills a last
     page that carries nothing essential (empty, or just a repeated header + a
     `חתימה:` signature label). `annotate.py` drops any such trailing page before
     the invoice enters the pack — a trailing page is **kept only** when it carries
     real content (a `₪` amount, `מע"מ`, or a `GT-` SKU: line items or totals that
     spilled over); the first page is never dropped. Saves two printed sheets per
     affected stop (×2 copies).

## Page 1 — the REAL LionWheel work order (Tom, 2026-06-21)
Page 1 is LionWheel's own "סידור עבודה" print (the **הדפסת סידור עבודה** button =
`GET /visits/print_labels?date=DD/MM/YYYY&driver_id={id}`), **not** a page we
generate. It carries LionWheel's header/branding and full columns. LionWheel's
print view stacks the `יעד` column one Hebrew letter per line (~13 pages); we inject
compact print CSS (`white-space:nowrap`, tight cells) and pick the largest scale
that still fits, so all stops land on **one A4 portrait page** — layout tightened
only, nothing invented. `build_workorder()` stays as a fallback if LionWheel does
not return the page.

## Invoice annotation design (formal, rounded — Tom, 2026-06-21)
Per product line, at the **right margin, precise to the line**, a formal rounded
status badge (two-tone: saturated glyph on a pale fill, thin same-hue ring):
- **✓ green disc** (picked in full) · **✗ terracotta disc** (not picked) ·
  **amber `picked/ordered` pill** (partial). Vector marks, never bare letters.
- **Order id** — top-right, **first page only**: a rounded GT-green pill with a
  `מס׳ הזמנה` eyebrow over the **last 3 digits** in white.
- **Package count** — centered **directly under "מקור"**: a round GT-green
  double-ring badge with the count and a `חבילות` label.
- Touch **only the named driver's route**. Ignore every other stop.

## How to run
1. **Inputs.** Driver name + date (`YYYY-MM-DD`) — both optional since 2026-07-22:
   - No driver named → the **route driver מיידן** (`../daily-delivery-dispatch/drivers.json`
     → `default_route_driver`; resolve/cache its LionWheel id per that file's instruction;
     מקסים 28174 = emergency driver only).
   - No date → **next working day** ("מחר" on Thursday/Friday/Saturday = Sunday; Friday and
     Saturday are not route days — `../daily-delivery-dispatch/route_calendar.json`).
   - Timing: build the pack **after the 15:00 line lock** (weekdays) or **after the Sunday
     ~10:15 final sweep** — never from a still-open line (two-wave picking, mapping v3).
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
   Writes `route_pack_out/route_<driver>_<date>.pdf`, `summary.json` and `summary.md`.
   Sanity-check by rendering a page to PNG with PyMuPDF.
4. **Stock moves outside picking: flag only, no submission.** `detect_inventory_moves()`
   marks stops whose title or any note field (invoice stops included) says exchange, pickup,
   return, tasting, supplement, free goods (`ללא חיוב`) or delivery note. Cheque pickups are
   not flagged. The flag lands on the work-order fallback and in `summary.md`, and
   `summary.json` carries `flagged_moves`. **This skill creates nothing in the inbox.** A
   route is printed before delivery, and a stop can still be canceled or changed. The
   filled proposal (lines, evidence, open questions) is made after delivery, from COMPLETED
   tasks of every driver, by the **`stock-exceptions-sweep`** skill inside the 06:30
   `daily-ops-guardian` run. Never write inbox, form or ledger rows from here, through the
   API or the Supabase MCP.
5. **Email.** The PDF is compressed on assembly (~3 MB). Send it + a short summary
   to **production@gteveryday.com** via the Supabase Edge Function relay
   `email_route_pack` (the sandbox cannot reach Resend directly — Cloudflare 1010 —
   but Supabase's network can):
   ```bash
   python3 send_email.py route_pack_out/summary.json   # needs SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY
   ```
   The relay is deployed and proven end-to-end. **One-time prerequisite for
   production@:** verify the `gteveryday.com` domain at resend.com/domains, then set
   the edge secret `ALERT_EMAIL_FROM` to a `@gteveryday.com` sender (or redeploy the
   function with that default). Until the domain is verified, Resend test mode only
   delivers to the account owner (tom@gteveryday.com); the relay returns the Resend
   error — when that happens, deliver the PDF to Tom in chat and say the domain
   still needs verifying. Never silently drop it.
6. **Deliver** the PDF to Tom in chat as well.
7. **Knowledge-graph capture (auto — Tom, 2026-06-21).** Every time this skill runs,
   `route_pack.py` also writes a markdown digest `route_pack_out/summary.md` (stops,
   customers, picking shortfalls, flagged stock moves). Feed **that digest**
   to `/graphify` so each dispatch becomes queryable history.
   - graphify reads `.md`, **not** raw JSON, so the digest is the input (never the
     PDF or the repo) — fast and additive.
   - **Run graphify in a local-only corpus dir OUTSIDE this repo** (e.g.
     `~/.route_pack_graph/`), copying the digest in as `route_<driver>_<date>.md` and
     using `graphify <dir> --update` to accumulate days. `route_pack_out/` is
     `.gitignore`d on purpose (real customer data) — graphify honors `.gitignore`, so
     it sees nothing there, **and the route graph must likewise never be committed.**
   - (`/caveman` was considered and rejected: it compresses spec/prose writes, of
     which a route-pack run has none. Tom chose graphify, 2026-06-21.)

## Picking discrepancies (credits)
Picking shortfalls are marked on the invoices and listed in the email summary.
**Do not** write credits to the DB — the system auto-creates `credit_tasks` after
the driver marks delivery. (Confirmed live: the pick-bridge creates them on the
terminal LionWheel status.)

## Boundaries
- Read-only on LionWheel, Green Invoice, and the Supabase mirror.
- Only the named driver's route; never other stops or drivers.
- Never write to `stock_ledger`, and never create inbox items: flagged moves are proposed
  after delivery by `stock-exceptions-sweep`, and a human approves.
- The LionWheel web password lives only as an env secret; if it ever appears in
  chat, tell Tom to rotate it.

## Data contracts (discovered, do not guess)
- LionWheel list: `GET {LW_BASE}/api/v1/tasks.json?key=…&limit=…`
- LionWheel task: `GET {LW_BASE}/api/v1/tasks/show/{id}.json?key=…`
  → `driver_str`, `driver_id`, `pickup_at`, `visits[].daily_order`,
    `order_items[].quantity` vs `.picked_quantity`, `packages_quantity`,
    `wp_order_id`, and the GI link in `driver_note` or `notes`.
- LionWheel web (session login at `/users/sign_in`, field `user[username]`):
  **work order print** (the "הדפסת סידור עבודה" button) =
  `GET /visits/print_labels?date=DD/MM/YYYY&driver_id={id}` — this is the printable
  סידור עבודה (use this for page 1; the `/drivers/{id}/daily_route_plan` SPA renders
  app chrome + only the on-screen rows, do not print it directly);
  waybill `GET /tasks/{id}/print_waybill`.
- Green Invoice (verified live 2026-09-23, delivery note 20286 + invoice 63810):
  `POST /documents/search {"number": "<n>", "type": [<code>], "page": 1, "pageSize": 5}`
  returns exactly that document (`number` as string or int). Codes seen: `200` = תעודת
  משלוח, `305` = חשבונית מס. The same number under the other type returns 0. Each search item
  already carries `income[]`: `catalogNum` (the barcode = `items.barcode`, sometimes without
  its leading 0), `description`, `quantity`, `price`, `itemId` (empty); plus `client.name`,
  `client.id`, `documentDate`, `remarks` (`"מספר הזמנה באתר: #GT13977"` on invoices,
  `"תעודת משלוח עבור חשבונית מס 63913"` on delivery notes), and `url.origin` (PDF).
  The task's GI link (`documents/download?d=…`) carries a different token than `url.origin`;
  match by number, never by link.
- Green Invoice: token `POST /account/token {id,secret}`; fallback document match
  `POST /documents/search` (paginate newest-first through the **full** history —
  ~12k+ docs — until the `#GT…` order id in `remarks` matches; do NOT stop at the
  first page or the order goes to a waybill by mistake) then `GET /documents/{id}`
  for the PDF link.
