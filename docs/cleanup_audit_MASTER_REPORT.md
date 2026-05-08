# Cleanup Audit — Master Report
**Date:** 2026-05-02
**Scope:** Surface every non-real (test / fixture / smoke / synthetic) record in live Supabase Postgres so Tom can purge it.
**Method:** 6 parallel READ-ONLY audit agents ran against `private_core.*`. No DDL, no DML executed.

> **Bottom line:** The live database is currently dominated by synthetic test data. There is essentially **no real operational data** in any planning, forecasting, or production table. Of the items table, 30 of 98 rows are test fixtures. Of the forecast versions feeding the planning engine, **100% are test-authored**. Of the 62 POs, only **1 is confirmed real** (and it's CANCELLED). Stock ledger has ~2,449 of 2,471 movements as test/synthetic.

---

## 1. Items table (`private_core.items`)

| Class | Count |
|---|--:|
| Total | 98 |
| REAL | 54 |
| **SUSPECT (purge)** | **30** |
| DORMANT-BUT-REAL (no BOM/supplier wiring) | 14 |

**Headline:** CURRENT_STATE.md said "5 T2DET fixtures still open" → actually **9 T2DET items** survive (5 older + 4 leaked on 2026-05-01). **5 brand-new `TEST-*` items were created today (2026-05-02)** — likely from in-flight test runs.

**Suspect item_ids (30):**
- `ammc-slice2-1777199392560-ITM-1/2/3/BOM` (4)
- `FG-PA-TEST-BF-STUB`
- `T1REG-BF-1777205442687`, `T1REG-BF-NOSI-1777205442687`
- `T2DET-1777209889185-MFR`, `T2DET-1777210102536-{BF,MFR}`, `T2DET-1777210369167-{BF,MFR}`, `T2DET-1777672490925-MFR`, `T2DET-1777672523274-{BF,MFR}`, `T2DET-1777672599087-{BF,MFR}` (9 — note 4 created today)
- `T3BLK-1777276453154-FG`, `T3BLK-1777276834406-FG`
- `TEST-LW-PHASE2-FG-1`, `TEST-LW-PHASE2-RM-1`, `TEST-LW-PROBE-FG-1`, `TEST-LWBF-T5-ITEM`
- `TEST-PARITY-FCM-1777733022613/047761/086512/417728` (4 — all created today)
- `TEST-SKU-RESOLVER-FG-{APPROVED,PENDING,REJECTED}` (3)

**Cascade implication:** 9 of these have a `primary_bom_head_id` (need bom_head + bom_version + bom_lines purged); 8 have `supplier_items` links.

**Detail:** [cleanup_audit_items.md](./cleanup_audit_items.md)

---

## 2. Master data — suppliers / components / BOMs / supplier_items

| Table | Baseline | Live | Δ | Test rows |
|---|--:|--:|--:|--:|
| suppliers | 43 | 104 | +61 | **~58** |
| components | 145 | 213 | +68 | **26** (name) / 29 (orphan superset) |
| bom_head | 68 | 85 | +17 | 5 (rest = real MUZA from 0087/0088) |
| bom_version | 68 | 99 | +31 | 5 test heads (+15 real DRAFT, +6 real ARCHIVED) |
| bom_lines | 420 | 603 | +183 | **10 legacy `'BOM'` ref-type + 5 test-head** |
| supplier_items | 185 | 231 | +46 | ~13 |
| planning_policy | 5 | 15 | +10 | 0 (all real Gate 5 keys — bump baseline) |

**Critical finding — gap left by migration 0131:** **10 legacy `'BOM'` ref-type bom_lines on PACK heads survive on non-active versions**. Migration 0131's CHECK constraint only fires on active versions, so inactive versions kept the bad rows. Affected heads: `BOM-PACK-MAR-CLA-300ML`, `BOM-PACK-MAR-PEA-300ML`, `BOM-PACK-MAR-STR-300ML`, `BOM-PACK-SAN-RED-3850ML`, `BOM-PACK-SAN-WHI-3850ML` (2 lines each on different inactive bom_versions).

**Test supplier patterns:** `T2DET-*-SUP`, `T3BLK-*-SUP`, `T1REG-SUP-*`, `SUP-{POC,POL,POH,LU,LCC,GRR,E2E}-*`, `ammc-slice2-*-SUP-*`, `SUP-MANUALPG-*`, `SUP-PH9-BRIDGE-*`, `SUP-MPGS-*`, `SUP-PLS-*`.

**Test component patterns:** `COMP-{POC,POL,POH,GRR,LCC,LU,E2E,PLS}-*`, `T2DET-*-COMP`, `T1REG-COMP-PO-*`, `T3BLK-*-COMP*`, `RAW-PEACH-PUREE` (race-test fixture).

**False positives to NOT delete:** `RAW-LUISA` (real Lemon Verbena), `PKG-CARTON-MAT-30G` / `PKG-PACK-MAT-30G` (real seed, just unused).

**Detail:** [cleanup_audit_masters.md](./cleanup_audit_masters.md)

---

## 3. Stock ledger / anchors / form_submissions / app_users / change_log

| Table | Total | Suspect | Real |
|---|--:|--:|--:|
| `stock_ledger` | 2,471 | **2,449** | **2** (Tom RAW-WHISKEY waste 2026-04-23 + Tom ADD-GAR-ORA-DRY GR 2026-05-02) |
| `balance_anchors_current` | 212 | 3 | 209 |
| `form_submissions` | 1,048 | **702** | rest |
| `app_users` | 151 | **150** (3 official fixtures + 147 stray test users) | 1 (Tom) |
| `change_log` test/T13/T3A | 1,813 | 1,813 | — |
| `production_actual` (form table) | 0 | 0 | 0 |
| `exceptions` | 514 (366 open) | 22 reference TEST-* | rest |

**Critical drift:** CURRENT_STATE.md said 262 ledger movements → actual **2,471**. Drift of ~2,200 movements written by tests since.

**147 stray test users** in namespaces beyond the 3 official 0059 fixtures: `dddddddd-…` (35), `eeeeeeee-…` (66), `cccccccc-…` (19), `bbbbbbbb-…` (7).

**Critical classifier gap:** 20 GR/GR_REVERSAL rows on synthetic `COMP-PH9-BRIDGE-…` / `COMP-GRR-…` components have **no test marker in their idempotency keys** but reference fake components — they were initially classified "real-shape" by the script. Real cleanup planning **must intersect ledger with the items audit** (any movement on a fake item is a fake movement).

**Append-only constraints:**
- `stock_ledger` and `change_log` cannot be DELETEd (append-only by contract). Cleanup requires REVERSAL rows, not delete.
- `balance_anchors`, `form_submissions`, `app_users`, `exceptions` ARE deletable but only by Tom's explicit DML.

**Two pending form_submissions:**
1. Test race fixture (delete-candidate)
2. Tom's intentional RAW-VODKA +50 L exception-flow test (notes: "CHECK-NOT-RERAL") — Tom decides

**Detail:** [cleanup_audit_stock.md](./cleanup_audit_stock.md)

---

## 4. Forecasts (`forecast_versions` / `forecast_lines`) — **100% TEST DATA**

| Metric | Value |
|---|--:|
| `forecast_versions` total | **510** |
| Status breakdown | 415 discarded / 77 published / 11 superseded / 7 draft |
| `forecast_lines` total | **30,728** (CURRENT_STATE.md's 12,057 was stale) |
| Distinct items in forecasts | 82 |
| Horizon | 2026-04-12 → 2027-09-05 |
| **Suspect classified** | **506 of 510** |
| Real authored by Tom | 4 (all empty drafts: 0/0/1/12 lines, no notes — never published) |

**Headline:** Tom (`tom@gteveryday.com`) authored 4 versions / 13 lines total — all drafts, all empty. **Every other version was created by fixture/test users.** Top offenders: `fctest-planner@fctest.gt` (242 versions / 14,806 lines), `fcm-planner@fcm.gt` (140 / 235), `fctest-admin@fctest.gt` (58 / 8,997).

**Currently published versions feeding planning** — **every one is suspect**. Labels: `FC-TEST-seed`, `FCM-TEST-Chunk3`, `FCSEED-TEST-seed`, `FCM-TEST-weekly-regression`, `parity-1777733...`. Authors: `Test admin` / `Test planner` / `FCM planner` / `FCSEED T6 publish`. None published by Tom.

**Planning engine pollution — confirmed:**
`planning_runs.demand_snapshot_forecast_version_id` references 6 distinct forecast versions across 65 runs. **5 of those 6 are suspect test versions Tom never authored:**

| Forecast version | Author | Runs | Latest run |
|---|---|--:|---|
| `6e2b2226-…` | Test admin | 27 | 2026-04-21 |
| `4a9438b3-…` | Test planner / FC-TEST-seed | 14 | — |
| `74a14e91-…` | Test planner / FC-TEST-seed | 8 | — |
| `d54262f6-…` | Test admin | 6 | **2026-05-02 (today)** |
| `ee61d61f-…` | Test admin | 5 | — |

52 additional runs have `forecast_ref=NULL` (no demand snapshot at all).

**Operational consequence:** **There is no real forecast in the system.** The planning engine is currently quoting recommendations off `Test admin` fixture data; the most recent planning run was today.

**Constraint:** `forecast_versions` DELETE is forbidden by contract §A.3. Purge requires a separately authored migration with Tom approval, plus reconciliation of the 65 planning_runs that pin those version_ids.

**Detail:** [cleanup_audit_forecasts.md](./cleanup_audit_forecasts.md)

---

## 5. Planning runs / recommendations / production_plan / production_actual

| Table | Total | REAL | SUSPECT |
|---|--:|--:|--:|
| `planning_runs` | 112 | 15 | **97** |
| `planning_run_recommendations` | 23,244 (23,220 draft / 24 approved) | 22 converted to PO | rest |
| `planning_run_exceptions` | 2,756 (append-only) | — | 2,378 missing_supplier_mapping + 353 missing_bom + 22 PO-substrate |
| `production_plan` | **1** (Tom-authored, FG-DET-1L-NS, 500, planned) | 0 | 1 (suspect pending Tom check) |
| `production_actual` (form table) | **0** | — | — |

**Stock_ledger orphans from deleted test production submissions:**
- 662 `production_consumption` rows
- 78 `production_output` rows
- 17 `production_scrap` rows

All by `dddddddd-…0a01` (PA test operator). They're balanced by 757 reversal rows. **Cannot delete (append-only).**

Pre vs post 2026-05-02 two-head fix: 112 CONSUME pre-fix / 550 post-fix (the 550 came from the two-head verification submissions whose parent `production_actual` rows were already deleted — leaving orphans).

**Sentinel confirmation:** T3A test plan `875718c3-a95a-4e69-a158-a1fc8f868bd0` already deleted (3 audit-log rows remain in change_log per CURRENT_STATE.md note — those are inert).

**Cleanup plan:** All 97 SUSPECT planning_runs are safely cascade-deletable in one batch — none of their recs are referenced by the lone production_plan. CASCADE will sweep recommendations, exceptions, inputs, demand, netting, fg_coverage. `purchase_orders.source_run_id` becomes SET NULL (no real PO is dropped).

**DO NOT TOUCH** the 15 REAL planning_runs — they parent the 22 converted-to-PO recommendations for live POs `PO-2026-00106..00155`.

**Detail:** [cleanup_audit_planning.md](./cleanup_audit_planning.md)

---

## 6. Purchase orders / PO lines / orders_mirror / LionWheel integration

| Table | Total |
|---|--:|
| `purchase_orders` | 62 (28 OPEN / 29 CANCELLED / 3 PARTIAL / 2 RECEIVED) |
| Per source_type | 38 manual / 24 recommendation |
| `purchase_order_lines` | 67 (zero orphan refs to fake items/components) |
| `orders_mirror` | 269 (164 captured_at >7 days old) |
| `orders_mirror_lines` | 714 |
| LionWheel `integration_runs` (30d) | 1,336 success / 1 unknown / 0 failures (healthy) |

**PO classification:**
- **REAL: 1** — `PO-2026-00145` (Tom, supplier SUP-017 צבר אריזות, CANCELLED, manual_reason "cycle 9 post-deploy portal-shape verify")
- **TOM-AUTHORED-CHECK: 1** — `PO-2026-00138` (Tom, supplier SUP-017, reason mentions "P0 triage probe (real supplier+component)")
- **SUSPECT: 60** — every other PO. None have `created_by_user_id` set (clear fixture-API bypass). Authors: PLS Planner (9), Manual PO test planner (12), Manual PO test admin (6), POC Planner (6), LCC Planner (6), POH Planner (3), POL Planner (3), T2 Det (4), T1 Reg (2), E2E planner (2), LU Planner (2), GRR Planner (2), MPGS planner (2), MPGS admin (1).
- Suppliers used by suspect POs: `E2E Supplier`, `POC Test Supplier`, `MPGT Supplier`, `LCC Test Supplier`, `LU Test Supplier`, `POL Test Supplier`, `GRR Test Supplier`, `POH Test Supplier`, `T1 Reg Supplier`, `T2 Det Supplier`, `PLS Test Supplier`.

**No POs have linked Goods Receipts** — `goods_receipts.po_id` returned zero rows. The 2 RECEIVED + 3 PARTIAL POs were status-bumped without a real GR; their lines may still have `received_qty > 0` — worth deeper inspection before deletion.

**orders_mirror:** without LionWheel API cross-check from this audit, fake mirror rows can only be inferred from stale `captured_at` + non-retired status.

**Detail:** [cleanup_audit_pos.md](./cleanup_audit_pos.md)

---

## What's REAL right now (don't delete)

- **Items:** 54 canonical seeds (FG-*, RAW-*, PKG-*, ADD-*, BOM-*) + the real MAR/SAN/MUZA additions from migrations 0087/0088/0130
- **Suppliers:** 43 baseline + the real ones added since (e.g. SUP-017 צבר אריזות)
- **Stock ledger:** 2 movements
  - `429b94d5-…` Tom WASTE_POSTED RAW-WHISKEY -0.01 (2026-04-23)
  - 1 Tom GR_POSTED ADD-GAR-ORA-DRY (2026-05-02)
- **POs:** 1 confirmed (PO-2026-00145, CANCELLED) + 1 needing Tom decision (PO-2026-00138)
- **Production plan:** 1 row (Tom, FG-DET-1L-NS, 500) — Tom should confirm if real or test
- **Planning runs:** 15 (parent the 22 converted-to-PO recs)
- **Forecast versions:** 4 Tom-authored empty drafts (effectively zero real forecast data)

---

## Cleanup priorities (recommended sequence)

1. **First — confirm scope with Tom.** Some "suspect" rows may be intentional smoke probes Tom wants to keep. Get explicit go/no-go on each major bucket before any DML.
2. **Cleanly cascade-deletable (low risk):**
   - 30 SUSPECT items (cascade BOMs/supplier_items)
   - 26 SUSPECT components (verify zero bom_lines refs after item delete)
   - ~58 SUSPECT suppliers
   - 13 SUSPECT supplier_items
   - 5 test bom_heads + 5 test bom_versions
   - 60 SUSPECT POs (zero linked GRs — safe)
   - 97 SUSPECT planning_runs + their 23k+ recommendations + exceptions
3. **Migration-required (forbidden by contract or schema rules):**
   - 506 SUSPECT forecast_versions + 30k+ forecast_lines (DELETE forbidden by §A.3 — needs an explicit Tom-approved migration with planning_run reconciliation)
   - 10 legacy `'BOM'` ref-type bom_lines on inactive PACK versions (migration 0131 didn't catch these — needs a 0132 cleanup migration)
4. **Append-only — surface only, do not delete:**
   - 2,449 SUSPECT stock_ledger rows (would need a synthetic-marker reversal sweep, but the cleaner option is to just trust them as historical noise post-launch)
   - 1,813 test change_log rows
   - 757 production reversal rows
5. **Decide-then-delete:**
   - 147 stray test app_users (low risk to delete after FK cascade analysis)
   - 22 exceptions referencing TEST-* items
   - 1 production_plan row (Tom authorship — confirm real vs test)
   - PO-2026-00138 (Tom + real supplier, but reason text says "probe" — Tom's call)

---

## Files produced by this audit

All under `c:/Users/tomw2/GTeveryday Dropbox/Data Center/Tom/AI Agents & Projects/Code Agents/PRODUCTION/docs/`:

- `cleanup_audit_MASTER_REPORT.md` — this file
- `cleanup_audit_items.md` + `cleanup_audit_items_raw.txt`
- `cleanup_audit_masters.md` + `cleanup_audit_masters_raw.txt`
- `cleanup_audit_stock.md` + `cleanup_audit_stock_raw.txt` + `cleanup_audit_stock_supplemental.txt`
- `cleanup_audit_forecasts.md` + `cleanup_audit_forecasts_raw.txt`
- `cleanup_audit_planning.md` + `cleanup_audit_planning_raw.txt`
- `cleanup_audit_pos.md` + `cleanup_audit_pos_raw.txt`

Re-runnable READ-ONLY scripts under `c:/Users/tomw2/Projects/gt-factory-os/scripts/`:
- `_audit_fake_items.mjs`
- `_audit_fake_masters.mjs` (+ v2/v3 column-corrected variants)
- `_audit_fake_stock.mjs` + `_audit_supplemental.mjs`
- `_audit_fake_forecasts.mjs`
- `_audit_fake_planning.mjs`
- `_audit_fake_pos.mjs`
