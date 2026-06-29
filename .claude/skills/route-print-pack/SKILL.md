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

## Page 1 — the REAL LionWheel work order (Tom, 2026-06-21)
Page 1 is LionWheel's own "סידור עבודה" print (the **הדפסת סידור עבודה** button =
`GET /visits/print_labels?date=DD/MM/YYYY&driver_id={id}`), **not** a page we
generate. It carries LionWheel's header/branding and full columns. LionWheel's
print view stacks the `יעד` column one Hebrew letter per line (~13 pages); we inject
compact print CSS (`white-space:nowrap`, tight cells), scale to fit **both** width
and natural height (so no stop is ever clipped), then stretch the route table to
fill the full page height, so all stops land on **one A4 portrait page**, spread
optimally — layout tightened only, nothing invented. `build_workorder()` stays as a
last-resort fallback if LionWheel does not return the page.

**Sandbox rendering (2026-06-29).** Chromium in the execution sandbox cannot reach
`members.lionwheel.com` (ERR_CONNECTION_CLOSED), but `urllib` (proxy-aware) can. So
`lw_fetch_inlined()` pulls the real LW page over `urllib` with the web-login
cookies, inlines its stylesheets, strips `<script>`, and inlines `<img>` as data
URIs; Chromium then renders that self-contained HTML via `set_content` with **no
network**. The same path renders the waybills. Output = the genuine LionWheel page
(header/columns/branding), rendered locally.

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
4. **Inventory inbox — submit as an APPROVAL (not a plain exception).** For each
   item in `inventory_proposals.json` (returns, exchanges, tastings, goods received
   — anything that moves stock outside normal picking), create a **pending
   inventory-movement approval** so it renders in the inbox with **Approve / Reject**
   (like physical count), not Acknowledge / Resolve.

   `inventory_proposals.json` now carries three `kind`s:
   - **pickup / exchange / return / tasting** — supplier/customer non-pick moves. A
     supplier goods pickup ("איסוף סחורה") is an **RM goods-receipt** candidate:
     anchor on the **component** (RM item), supplier is secondary; component + qty
     are confirmed by the approver in the inbox (never invented).
   - **`fg_out`** — a delivery-note stop with **0 LW order_items** bound to an
     outbound Green Invoice doc (`gi_doc_number`): goods shipped without the
     Shopify/LW link, so FG was never decremented. **At filing**: fetch the GI doc
     lines, map each barcode → FG `item_id` and convert qty **deterministically**
     from the item master (`case_pack`/`sales_uom` — e.g. matcha 50 cases × 22 =
     1100 bags), then file the FG-OUT approval with the lines pre-filled.
     **Idempotency = `gi_doc_number`** (never double-post vs a future LW FG-out
     bridge). Exclude credit/quote GI doc types. Any barcode that doesn't map, or a
     GI-vs-master pack conflict → render that line as **needs-decision** inside the
     same approval, never silently dropped, never guessed. (Filed exactly as the
     2026-06-29 GI-20269 approval: `form_submissions` + `inventory_movements` +
     `inventory_movement_lines` + `exceptions(category=inventory_movement_pending)`
     in `private_core`, via the Supabase MCP.)
   - **HARD LAW:** the skill only proposes; the stock move posts to `stock_ledger`
     **only** when the human approves in the inbox. Never write the ledger directly.

   The shared mechanics below apply to every kind: Preferred path: POST to the
   backend `POST /api/v1/mutations/inventory-movements`
   (`{idempotency_key, event_at, kind, source_ref:<lw_task_id>, recipient, note,
   summary}`). **Prefer this endpoint** — it owns the contract (idempotency, category,
   exception wiring). Only as a **last-resort fallback** (no backend session
   reachable), write the same rows directly via the Supabase MCP, mirroring the
   submit handler (`api/src/inventory-movements/handler.ts`) — and keep them in sync
   with it, or the portal's `inventory_movement_pending` filter won't pick them up:
   1. `form_submissions` (`form_type='inventory_movement'`, `status='pending'`,
      `submitted_by=<Tom's app_users.user_id>`, unique `idempotency_key`,
      `raw_payload`=the proposal incl. `summary`).
   2. `inventory_movements` (`submission_id`, `kind`, `source_ref`, `recipient`, `note`).
   3. `exceptions` (`category='inventory_movement_pending'`, `status='open'`,
      `source='form.inventory_movement'`, `title`=the concise `summary`,
      `related_entity_type='form_submission'`, `related_entity_id=<submission_id>`,
      `recommended_action`). The portal maps this category to
      `approval:inventory_movement` → `/inbox/approvals/inventory-movement/<id>`.
   Surface the concise summaries to Tom.
   - **Depends on migration `0259_inventory_movements.sql`** being applied (adds the
     `inventory_movement` form_type + `INVENTORY_MOVEMENT` ledger type + the two
     tables). Until applied, fall back to the prior plain-exception insert.
   - **Stock truth is sacred (CLAUDE.md).** This skill only **proposes**. The stock
     move (add/subtract, RM/FG) posts to `stock_ledger` **only when the approver
     enters the confirmed line(s) and approves** in the inbox, through the
     inventory-movement approve mutation (the sanctioned append path) — never written
     directly here, and never guessed.
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
   customers, picking shortfalls, inventory-movement proposals). Feed **that digest**
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
  **work order print** (the "הדפסת סידור עבודה" button) =
  `GET /visits/print_labels?date=DD/MM/YYYY&driver_id={id}` — this is the printable
  סידור עבודה (use this for page 1; the `/drivers/{id}/daily_route_plan` SPA renders
  app chrome + only the on-screen rows, do not print it directly);
  waybill `GET /tasks/{id}/print_waybill`.
- Green Invoice: token `POST /account/token {id,secret}`; fallback document match
  `POST /documents/search` then `GET /documents/{id}` for the PDF link.
