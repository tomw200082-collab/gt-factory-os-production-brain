---
decision_id: SHOPIFY-AW-G1
date: 2026-05-14
author: Tom (written approval in Claude Code session)
status: CLOSED
---

# Shopify Available-for-Sale Write — AW-G1 Approval

## What is approved

Tom reviewed `shopify_available_write_contract.md` and the dry-run evidence pack
(`shopify_available_dry_run_evidence_pack.md`) and approved:

1. **AW-G1 (payload shape):** `available_for_sale = GREATEST(0, calculated_on_hand) − committed_qty`
   where `committed_qty` = sum of open LionWheel order lines. Written approval: Claude Code
   session 2026-05-14T (message: "approve AW-G1").

2. **AW-G7 (UNRESOLVED ratifications):** Tom accepted all 4 Tom-ratify defaults:
   - **U-AW-1:** 5-minute cadence acceptable. ≤20-minute end-to-end lag (LionWheel poll + loop)
     is within operational tolerance. Default: stay at 5 minutes.
   - **U-AW-2:** Shopify draft orders NOT included in `committed_qty`. LionWheel open-order
     aggregation is the authoritative committed source. Default: NO draft orders.
   - **U-AW-3:** No sales block. Negative `available` is a storefront SIGNAL, not a wall.
     `inventory_policy` remains `"continue"`. Default: keep as-is.
   - **U-AW-10:** Shadow soak duration = **48 hours** (not 24). This loop is novel; extra soak
     is warranted. Default: 48h recommended, Tom-accepted.

## What is NOT approved here

- Flag flip `SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED=true` — requires all 9 gates closed.
- Writing to Shopify in live mode — still gated.
- `SHOPIFY_GRAPHQL_SYNC_ENABLED=true` — v2 on_hand sync is in shadow mode (Gate E, bridge
  frozen). AW-G4 requires this flag to be live before the available-write goes live. These
  two flags must be flipped together or v2 first.

## Gate chain status as of 2026-05-14

| Gate | Status | Next action |
|---|---|---|
| AW-G1 | **CLOSED** | This doc |
| AW-G2 | **CLOSED** | Migration 0187 + 28/28 smoke assertions PASS, PR #28 merged `4a3d773` |
| AW-G3 | **SHADOW SOAK IN PROGRESS** | Handler merged PR #29 `a5d6505`. Migration 0187 applied to prod DB. Edge Function redeployed 2026-05-14. Cron `*/5 * * * *` registered. **48h soak window: 2026-05-14 → 2026-05-16.** Monitor: `SELECT status, COUNT(*) FROM private_core.shopify_available_write_attempts GROUP BY status ORDER BY COUNT(*) DESC;` |
| AW-G4 | BLOCKED | `SHOPIFY_GRAPHQL_SYNC_ENABLED` not yet live; v2 Gate E must close first or in parallel |
| AW-G5 | PENDING AW-G3 | end-to-end shadow smoke |
| AW-G6 | PENDING AW-G3 | rollback plan operational |
| AW-G7 | **CLOSED** | This doc (4 defaults ratified above) |
| AW-G8 | PENDING AW-G4 | ops-docs-curator EXECUTION_POLICY.md update |
| AW-G9 | PENDING AW-G3 | RUNTIME_READY signal from executor |
