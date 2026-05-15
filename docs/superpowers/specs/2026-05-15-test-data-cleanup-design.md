# Test Data Cleanup — Design Spec

**Date:** 2026-05-15  
**Status:** Approved by Tom — executing  
**Migration:** `db/migrations/0197_cleanup_test_data.sql`

---

## Problem

Test-fixture rows from Phases 1–10 development leaked into the production Supabase database.
They pollute dropdowns, planning views, inventory flows, and economics dashboards.

**Census (production DB, 2026-05-15):**

| Table | Test rows |
|---|---|
| `items` | 30 |
| `components` | 35 + 1 (`RAW-PEACH-PUREE`) |
| `suppliers` | 14 (`ammc-*`) |
| `app_users` | ~60+ |
| `forecast_lines` | 1,683 |
| `shopify_available_write_attempts` | ~1,650 |
| `planning_run_exceptions` | ~125 |
| `fg_cogs_snapshots` | 1,072 (already excluded by migration 0192 view filter) |
| `stock_ledger` | 5 (append-only — untouched) |

---

## Approach: Approach B — DELETE what's safe, INACTIVE the rest

### Why not hard-DELETE all items

`fg_cogs_snapshots` has a real FK to `items` and is append-only (locked decision: no DELETE/UPDATE on append-only tables). 18 of 30 test items are referenced there. Rather than split items into two groups, all 30 go INACTIVE uniformly.

### INACTIVE vs DELETE decision table

| Entity | Action | Reason |
|---|---|---|
| 30 test `items` | SET INACTIVE | fg_cogs_snapshots FK (append-only) |
| 2 test `components` (COMP-GRR-*) | SET INACTIVE | stock_ledger rows (append-only) |
| 33 other test `components` + `RAW-PEACH-PUREE` | DELETE | No append-only FK refs |
| 14 test `suppliers` (ammc-*) | DELETE | No FK refs |
| 60+ test `app_users` | SET INACTIVE | form_submissions FK |
| 1,683 `forecast_lines` | DELETE | Child of items; no append-only constraint |
| Child planning/shopify rows | DELETE | Safe to delete |
| 5 `stock_ledger` rows | Untouched | Append-only locked decision |
| 1,072 `fg_cogs_snapshots` rows | Untouched | Append-only; already view-filtered (migration 0192) |

---

## What is NOT touched

- `FG-MAT-100G` — real product (PENDING), stays as-is
- `stock_ledger` — 5 test rows stay (append-only)
- `fg_cogs_snapshots` — 1,072 test rows stay (append-only, filtered by view)
- All real users: `tom@gteveryday.com`, `production@gteveryday.com`, `adi@gteveryday.com`, `denispotehin@gmail.com`, `alex.berov@gmail.com`

---

## Execution order (FK-safe)

1. DELETE child rows of test items (forecast_lines, shopify, planning_run_*, current_balances, etc.)
2. UPDATE items SET INACTIVE (all 30 test items)
3. DELETE child rows of test components (planning_run_component_*, bom_lines, etc.)
4. NULL `components.primary_supplier_id` where it references ammc-* suppliers
5. UPDATE 2 components SET INACTIVE (ledger refs); DELETE 33 others
6. DELETE planning_run_recommendations where supplier_id is ammc-* 
7. DELETE suppliers (ammc-*)
8. UPDATE app_users SET INACTIVE (all non-real users)

---

## Idempotency

Each statement uses `WHERE ... LIKE` or exact IDs. Running twice deletes 0 rows / updates 0 rows on second pass. Safe to re-run.

---

## Rollback

None — these are confirmed test fixtures. The locked decision doc confirms:  
`stock_ledger` rows cannot be deleted; all other test data has no operational value.
