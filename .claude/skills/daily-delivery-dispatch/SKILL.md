---
name: daily-delivery-dispatch
description: Use when Tom gives a delivery zone + a driver name + a date to dispatch LionWheel orders — e.g. "מרכז, מקסים, מחר", "South David 2026-06-23", "צפון ירוק מקסים 24/6". Pulls the open orders in that zone, checks unified stock truth, and on the in-stock ones sets the driver + delivery date in LionWheel (driver_id + pickup_at ONLY — NEVER status). Returns a consolidated list of everything that is NOT in stock. Always presents the exact plan for Tom's approval before any LionWheel write, and never touches a driver's already-in-progress route for another day.
---

# Daily Delivery Dispatch

## Purpose
Tom queues intent ("zone + driver + date"); this skill does what he did by hand today,
correctly and the same way every time: take every open delivery in a LionWheel delivery
zone, decide which are actually in stock, put the in-stock ones on the named driver for the
named day, and hand Tom one clean shortage list of what is missing. The skill must know the
work well enough that Tom only has to name the zone, the driver, and the day.

This skill writes to the LIVE LionWheel account. It is reversible (assignments can be
re-set) but it is customer-facing and mass-scale, so it always shows the exact plan and
waits for Tom's go before writing (per CLAUDE.md "External-action authorization" §2).

## Trigger
Tom writes, in any order / Hebrew or English: **zone + driver name + date.**
- Zone ∈ { Center / מרכז (purple), North / צפון (green), South / דרום (red) }.
- Driver = a name → resolve to a LionWheel `driver_id`.
- Date = the delivery day (Tom always supplies it; do not infer it).

If any of the three is missing or ambiguous → ask Tom, do not guess.

## Non-negotiable workflow
1. **Resolve inputs.** Driver name → `driver_id` (see Driver resolution). Zone → city set
   (`zones.json`). Date → `YYYY-MM-DD`.
2. **Pull open orders.** GET LionWheel tasks (status `UNASSIGNED` or `ASSIGNED`); for each,
   GET task detail for `driver_id`, `pickup_at`, `status`. (`destination_city` is on the
   LIST item, not the detail — read it from the list.)
3. **Filter to the zone** by `destination_city` via `zones.json`. **Unknown city → HALT,
   ask Tom which zone, then append it to `zones.json`** (learning). Never guess a city's zone.
4. **Protect live routes.** NEVER modify: (a) any task assigned to a *different* driver;
   (b) the target driver's tasks already dated to a *different* day (his in-progress / other-day
   route). Reserve those orders' stock before allocating. (Tom 2026-06-21: "be careful not to
   harm his route for today.")
5. **Classify stock** (see Stock classification) for each remaining zone order: READY or SHORT.
6. **Allocate** limited stock oldest-first (task id ascending). Only whole READY orders
   consume the pool; no partial fulfilment.
7. **Present the plan to Tom** (approval gate): the ASSIGN list (order → driver + date), the
   SHORTAGE list (what is not in stock, aggregated), and any flags (unknown city / unmapped
   SKU / empty SKU / unresolved driver). Wait for explicit go.
8. **Write (post-approval only).** Per READY order: `PUT /tasks/<id>/update` with
   `driver_id` + `pickup_at` **only — never `status`**. Skip true no-ops (already that
   driver+date). Verify each by re-read.
9. **Report.** N assigned (verified), the shortage list, anything skipped/flagged.

## Hard rules
- **NEVER set `status`.** Only `driver_id` + `pickup_at`. (Tom, 2026-06-21.)
- **NEVER touch another driver's orders, or the target driver's orders for a different day.**
  Do not disturb an in-progress route.
- **NEVER guess.** Unknown city → ask + learn. Unmapped SKU → ask. Ambiguous/zero driver
  match → ask. (CLAUDE.md no-guess rule for LionWheel.)
- **Stock truth:** `current_balances` is authority for manufactured beverages. A short,
  Tom-maintained `AVAILABLE_OVERRIDE` list covers specialty bought-finished items the ledger
  is blind to but that are physically stocked; everything else is gated on ledger on-hand.
- **Confirm before acting:** mass customer-facing writes always get Tom's go on the exact
  list first. Each write is verified; assignments are reversible.
- **Idempotent:** re-running with the same inputs is safe; writing the same driver+date is a
  no-op and is skipped.

## Zone → city mapping
Source: Tom's LionWheel delivery-zones map (🟣 purple = Center, 🟢 green = North,
🔴 red = South), captured 2026-06-21. The editable source of truth is **`zones.json`**
(this is the "knowledge" that grows). Match on normalized `destination_city`
(lowercase, trimmed; Hebrew and English variants included). A city not in `zones.json`
is a hard stop: ask Tom, then add it.

> Boundary cities were assigned decisively from the map + Israeli geography (Tom delegated
> the call 2026-06-21, "decide what's best and most accurate"): Hadera/Binyamina → North;
> Netanya, Rishon LeZion, Ness Ziona, Rehovot, Modi'in, Shoham, Rosh Haayin, Netzer Sereni
> → Center; Jerusalem, Beit Shemesh → South. To go sub-city exact later, load LionWheel's
> zone GeoJSON polygons and geocode each order's street address (the read API exposes no
> per-order GPS, only city/street/zip).

## Driver resolution
`GET https://members.lionwheel.com/api/v1/drivers.json?key=$LIONWHEEL_API_KEY` → array of
`{id, first_name, last_name, nick_name, phone, ...}` (≈26 drivers). Match Tom's name
(Hebrew or English; check first_name / last_name / nick_name; the per-task `driver_str`
field also shows the display name, e.g. "מקסים"). Confirmed: **Maxim / מקסים = 28174.**
Zero or multiple matches → ask Tom. Cache confirmed name→id in `drivers.json` (learning).

## Stock classification (live — Supabase project `rvadsozabmxkkrktwgnv`, schema `private_core`)
1. **Resolve SKUs.** For each order line `sku`:
   ```sql
   select external_sku, item_id, internal_units_per_shopify_unit
   from private_core.integration_sku_map
   where external_sku = any(:skus) and approval_status = 'approved';
   ```
   Fall back to `items.sku` / `items.legacy_sku` if not in the map. Multiply required qty by
   `internal_units_per_shopify_unit` (today all = 1).
2. **On-hand.**
   ```sql
   select item_id, sum(calculated_on_hand) on_hand
   from private_core.current_balances
   where item_id = any(:item_ids) group by 1;
   ```
3. **Per line:** if `item_id ∈ AVAILABLE_OVERRIDE` → treat as available (do not gate).
   Else require `on_hand >= qty` (cumulative across orders, oldest-first).
4. **Order is READY** iff every gated line is satisfiable; otherwise **SHORT** (record the
   short lines: sku, need, have).

### AVAILABLE_OVERRIDE (ledger-blind specialty items, physically stocked — Tom 2026-06-21)
- `FG-MAT-500G` — matcha (`GT-SHI-CER-500`)
- `ADD-UBE-1KG` — ube (`UBE-POWDER-1-KG`)
- `ADD-GAR-ORA-DRY` — dried orange (`AP-DRI-ORA`)
- `EXCLUDED-NONSTOCK` — non-stock sentinel (e.g. measuring cup `GT-GLA-CUP`)

Everything else is gated on the ledger — including Muza cocktails/mixers (`FG-MUZ-*`,
`ADD-MUZ-*`), dried roses (`ADD-GAR-ROSE-DRY`), ODK (`ADD-ODK-*`), and ELT-STR
(`FG-DET-STR-500ML`). **The durable fix is to receive specialty stock via the
`goods-receipt-from-invoice` skill so the ledger is true; prune an item from this list the
moment it becomes ledger-tracked.**

## LionWheel write pattern
`PUT https://members.lionwheel.com/api/v1/tasks/<task_id>/update?key=$LIONWHEEL_API_KEY`
Body (JSON): `{ "driver_id": <int>, "pickup_at": "YYYY-MM-DD" }`  — **no `status` field.**
- Assign: `driver_id` = resolved id, `pickup_at` = Tom's date.
- Unassign (only if Tom explicitly asks): `driver_id: null`.
- Success: `200 {"message":"Saved Successfully"}`. **Verify** with
  `GET /tasks/show/<id>.json` → `driver_id` and `pickup_at` match.
- Status enum (reference only — the skill never sets it): UNASSIGNED 0, ASSIGNED 1,
  ACTIVE 2, COMPLETED 3, CANCELED 4, ROUNDTRIP_DELIVERED 5, IN_INVENTORY 6, OUT_INVENTORY 7,
  FAILED 8, FINAL_FAILED 9, IN_TRANSFER 10.

## Shortage report (the deliverable Tom reads)
Aggregate gated shortfalls across the zone: per item (`sku → item_id`): total needed vs
on-hand vs short, and which orders contain it. Plus any unknown-city / unmapped-SKU /
empty-SKU flags. This is what Tom uses to close production/procurement gaps.

## Learning (so it ends up knowing the work better than Tom)
Every correction is made durable:
- New city → zone: append to `zones.json`.
- New driver name → id: append to `drivers.json`.
- SKU mapping is owned by `integration_sku_map` (DB), not this skill — if a SKU is unmapped,
  flag it for the sku-map process; never hardcode a mapping here.
- An item becomes ledger-tracked → remove it from `AVAILABLE_OVERRIDE`.
Target: the approval step's "please confirm" list shrinks toward zero over time.

## Scripts (in this skill dir)
- `scripts/lw_orders.mjs <zone>` — fetch open LionWheel orders, filter to the zone via
  `zones.json`, print each order's lines + current driver/pickup + any unknown-city flags.
  **Read-only.** Uses `$LIONWHEEL_BASE_URL` / `$LIONWHEEL_API_KEY`.
- `scripts/lw_apply.mjs <YYYY-MM-DD> <driver_id> <task_id...>` — set `driver_id` + `pickup_at`
  on the given tasks and verify each. **Run only after Tom approves the plan. Never sets status.**

## Provenance
Built 2026-06-21 from a live run Tom directed end-to-end: full API surface inspected
(read + write), 17 live writes executed and verified, zone map supplied by Tom, "no status"
and "protect today's route" and "all regions" rules set by Tom. LionWheel API total surface
is 14 endpoints (no zones/areas API — zone membership is by `destination_city`).
