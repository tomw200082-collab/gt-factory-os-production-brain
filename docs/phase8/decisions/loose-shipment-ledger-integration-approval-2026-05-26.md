# Decision Packet — Loose-Shipment Ledger Integration

**Date:** 2026-05-26
**Approved by:** Tom (in-session conversation; explicit per-decision approval recorded below)
**Mission:** loose-shipment ledger integration
**Governor verdict:** PROCEED_WITH_CONSTRAINTS (factory-os-governor, 2026-05-26)
**Skill plan reference:** `C:\Users\tomw2\.claude\skills\lionwheel-route-invoices\PLAN_loose_shipment_expansion.md`

## Background

The `lionwheel-route-invoices` skill currently captures `confirmed_loose_shipments[]` in its manifest (W1, complete) and documents the Claude-driven inference workflow (W2', complete). W3 builds the backend API endpoint that lets the skill commit confirmed loose shipments to `stock_ledger` after Gate 2 (per-row Tom approval at evening commit time).

Loose shipments are stock movements with no Green Invoice (sample shipments OUT, customer pickups IN). They currently cause silent ledger drift. Today's reference case (Maxim's 2026-05-26 route) has 18 ledger lines waiting to commit: 17 cartons OUT to Sugat sampling + 312 matcha bags IN from Amita.

## Approved decisions

### A. New `event_type` enum values
- `LOOSE_SHIPMENT_OUT` (qty_delta < 0)
- `LOOSE_SHIPMENT_IN`  (qty_delta > 0)

Additive only; no rename or removal of existing values. Per `EXECUTION_POLICY.md` approval-thresholds row "Adding a new movement_type to stock_ledger", this packet is the Tom-written approval.

### B. New API endpoint
- `POST /api/stock-events/loose-shipment`
- Body carries `lines[]` array (multi-SKU per shipment; e.g., Sugat 17 cartons = 1 request, 17 ledger rows on success).

### C. Idempotency formula
`sha256(driver_id + delivery_date + task_id + item_id)`

Supersedes the earlier `sha256(route_dir + task_id + sku + sequence)` formula in `PLAN_loose_shipment_expansion.md`. The new formula is pure data (no filesystem dependency), server-portable, deterministic across machines.

### D. Auth
- **Transport:** existing dev-shim (matches other endpoints in gt-factory-os).
- **App-layer (server-enforced):** reject with HTTP 400 unless ALL of:
  - `confirmed_by === "tom"`
  - `tom_approval_session_id` non-empty
  - `inference_status === "confirmed_by_tom"`

These are server-side validation guards, not client hints. Each rejection has a dedicated e2e test.

## Phase D amendment (Tom-locked)

The future cron commit job (W4) will NOT auto-commit. It builds a "pending commits" batch from `confirmed_loose_shipments[]` + LW delivery status, presents to Tom, and only Tom-approved rows reach the API.

Tom quote (2026-05-26): "אני צריך לאשר סופית מה שיורד או מתווסף למלאי!"

Two gates total:
- **Gate 1 (W2'/Phase C, daytime):** Tom confirms what is *intended* to ship. Result: `confirmed_loose_shipments[]` in route manifest.
- **Gate 2 (W4/Phase D, evening):** Tom confirms the delivery actually happened before each ledger write. The `tom_approval_session_id` in the API call captures this gate.

## Governor constraints (must hold for W3 to ship)

11 constraints from `factory-os-governor` verdict 2026-05-26:

1. Tom-approval packet pinned to disk before migration commit (this file).
2. Mission "loose-shipment ledger integration" recorded in `ACTIVE_NOW.md`.
3. Migration is additive-only; pgTAP asserts new values exist AND all pre-existing values are unchanged.
4. Idempotency formula = Decision C above; contract doc explicitly marks the older formula as superseded.
5. App-layer guards are server-enforced (Decision D); e2e covers each rejection independently.
6. Contract doc documents the reversal path NOW (sibling event with opposite sign + `corrected_by` ref; never UPDATE/DELETE).
7. No silent direct ledger writes — skill writes go through the API endpoint only.
8. `delivery_date` window validation: reject >7 days past or >1 day future.
9. This file is operational evidence, not authority tier.
10. `stock_event_idempotency_keys` table has PK on `idempotency_key` + FK to `stock_ledger.event_id`; 409 returns original event_ids via JOIN.
11. Evidence pack at PASS: files changed, pgTAP N/N, Fastify e2e N/N, contracts referenced, `RUNTIME_READY(LooseShipmentLedger)` signal, rollback plan, next handoff.

## Dispatch order

1. **`backend-db-executor`** — migration (event_type addition + `stock_event_idempotency_keys`), endpoint, Zod validator, pgTAP, Fastify e2e.
2. **`integration-boundary-executor`** — `docs/contracts/stock-events.md` with approved idempotency formula, app-layer guards, reversal path.
3. **`release-verifier`** — pre-merge gate.

## Authority hierarchy

This file is operational evidence, not an authority doc. Lives under `docs/phase8/decisions/` (consistent with prior decision packets per `WORKSPACE_MAP.md`).
