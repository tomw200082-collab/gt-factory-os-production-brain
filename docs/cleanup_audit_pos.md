# GT Factory OS — Cleanup Audit: Purchase Orders + Orders Mirror

Generated: 2026-05-02T17:30:46.706Z

Read-only audit. No DDL or DML executed. Sources:
- `private_core.purchase_orders`
- `private_core.purchase_order_lines`
- `private_core.orders_mirror`
- `private_core.orders_mirror_lines`
- `private_core.integration_runs`
- `private_core.goods_receipts` (linkage check)

## Totals

| Table | Count |
|---|---|
| purchase_orders | 62 |
| purchase_order_lines | 67 |
| orders_mirror | 269 |
| orders_mirror_lines | 714 |

### purchase_orders per status

| status | n |
|---|---|
| RECEIVED | 2 |
| CANCELLED | 29 |
| OPEN | 28 |
| PARTIAL | 3 |

### purchase_orders per source_type

| source_type | n |
|---|---|
| recommendation | 24 |
| manual | 38 |

### Classification buckets

| bucket | n |
|---|---|
| SUSPECT | 60 |
| TOM-AUTHORED-CHECK | 1 |
| REAL | 1 |

## SUSPECT POs (need cleanup review)

| po_id | po_number | supplier | status | source_type | created_by_email | created_at | lines | bucket | reasons |
|---|---|---|---|---|---|---|---|---|---|
| PO-2026-00101 | PO-2026-00101 | E2E Supplier | RECEIVED | recommendation |  | 2026-04-26T10:34:18.476Z | 1 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator looks test: email= snapshot=e2e planner; creator is NOT Tom (snapshot="E2E planner") |
| PO-2026-00106 | PO-2026-00106 | POC Test Supplier | CANCELLED | recommendation |  | 2026-04-26T10:35:13.428Z | 1 | SUSPECT | creator is NOT Tom (snapshot="POC Planner") |
| PO-2026-00107 | PO-2026-00107 | POC Test Supplier | CANCELLED | recommendation |  | 2026-04-26T10:35:13.586Z | 1 | SUSPECT | creator is NOT Tom (snapshot="POC Planner") |
| PO-2026-00108 | PO-2026-00108 | MPGT Supplier | CANCELLED | manual |  | 2026-04-26T10:35:14.455Z | 1 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator looks test: email= snapshot=manual po test planner; creator is NOT Tom (snapshot="Manual PO test planner") |
| PO-2026-00109 | PO-2026-00109 | MPGT Supplier | CANCELLED | manual |  | 2026-04-26T10:35:15.088Z | 1 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator looks test: email= snapshot=manual po test admin; creator is NOT Tom (snapshot="Manual PO test admin") |
| PO-2026-00110 | PO-2026-00110 | MPGT Supplier | CANCELLED | manual |  | 2026-04-26T10:35:15.696Z | 1 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator looks test: email= snapshot=manual po test planner; creator is NOT Tom (snapshot="Manual PO test planner") |
| PO-2026-00111 | PO-2026-00111 | GRR Test Supplier | CANCELLED | recommendation |  | 2026-04-26T10:35:17.468Z | 1 | SUSPECT | creator is NOT Tom (snapshot="GRR Planner") |
| PO-2026-00112 | PO-2026-00112 | POH Test Supplier | CANCELLED | recommendation |  | 2026-04-26T10:35:23.167Z | 1 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator is NOT Tom (snapshot="POH Planner") |
| PO-2026-00113 | PO-2026-00113 | LCC Test Supplier | OPEN | recommendation |  | 2026-04-26T10:35:27.518Z | 2 | SUSPECT | creator is NOT Tom (snapshot="LCC Planner") |
| PO-2026-00114 | PO-2026-00114 | LCC Test Supplier | OPEN | recommendation |  | 2026-04-26T10:35:27.843Z | 1 | SUSPECT | creator is NOT Tom (snapshot="LCC Planner") |
| PO-2026-00115 | PO-2026-00115 | LCC Test Supplier | OPEN | recommendation |  | 2026-04-26T10:35:28.142Z | 1 | SUSPECT | creator is NOT Tom (snapshot="LCC Planner") |
| PO-2026-00116 | PO-2026-00116 | LU Test Supplier | OPEN | recommendation |  | 2026-04-26T10:35:32.815Z | 4 | SUSPECT | creator is NOT Tom (snapshot="LU Planner") |
| PO-2026-00117 | PO-2026-00117 | POL Test Supplier | OPEN | recommendation |  | 2026-04-26T10:35:38.190Z | 1 | SUSPECT | creator is NOT Tom (snapshot="POL Planner") |
| PO-2026-00118 | PO-2026-00118 | MPGT Supplier | CANCELLED | manual |  | 2026-04-26T10:35:44.152Z | 1 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator looks test: email= snapshot=manual po test planner; creator is NOT Tom (snapshot="Manual PO test planner") |
| PO-2026-00119 | PO-2026-00119 | MPGT Supplier | CANCELLED | manual |  | 2026-04-26T10:35:44.762Z | 1 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator looks test: email= snapshot=manual po test admin; creator is NOT Tom (snapshot="Manual PO test admin") |
| PO-2026-00120 | PO-2026-00120 | MPGT Supplier | CANCELLED | manual |  | 2026-04-26T10:35:45.347Z | 1 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator looks test: email= snapshot=manual po test planner; creator is NOT Tom (snapshot="Manual PO test planner") |
| PO-2026-00121 | PO-2026-00121 | E2E Supplier | RECEIVED | recommendation |  | 2026-04-26T10:37:19.253Z | 1 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator looks test: email= snapshot=e2e planner; creator is NOT Tom (snapshot="E2E planner") |
| PO-2026-00126 | PO-2026-00126 | POC Test Supplier | CANCELLED | recommendation |  | 2026-04-26T10:38:11.815Z | 1 | SUSPECT | creator is NOT Tom (snapshot="POC Planner") |
| PO-2026-00127 | PO-2026-00127 | POC Test Supplier | CANCELLED | recommendation |  | 2026-04-26T10:38:11.971Z | 1 | SUSPECT | creator is NOT Tom (snapshot="POC Planner") |
| PO-2026-00128 | PO-2026-00128 | GRR Test Supplier | CANCELLED | recommendation |  | 2026-04-26T10:38:16.390Z | 1 | SUSPECT | creator is NOT Tom (snapshot="GRR Planner") |
| PO-2026-00129 | PO-2026-00129 | POH Test Supplier | CANCELLED | recommendation |  | 2026-04-26T10:38:22.107Z | 1 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator is NOT Tom (snapshot="POH Planner") |
| PO-2026-00130 | PO-2026-00130 | LCC Test Supplier | OPEN | recommendation |  | 2026-04-26T10:38:26.471Z | 2 | SUSPECT | creator is NOT Tom (snapshot="LCC Planner") |
| PO-2026-00131 | PO-2026-00131 | LCC Test Supplier | OPEN | recommendation |  | 2026-04-26T10:38:26.780Z | 1 | SUSPECT | creator is NOT Tom (snapshot="LCC Planner") |
| PO-2026-00132 | PO-2026-00132 | LCC Test Supplier | OPEN | recommendation |  | 2026-04-26T10:38:27.163Z | 1 | SUSPECT | creator is NOT Tom (snapshot="LCC Planner") |
| PO-2026-00133 | PO-2026-00133 | LU Test Supplier | OPEN | recommendation |  | 2026-04-26T10:38:32.238Z | 4 | SUSPECT | creator is NOT Tom (snapshot="LU Planner") |
| PO-2026-00134 | PO-2026-00134 | POL Test Supplier | OPEN | recommendation |  | 2026-04-26T10:38:37.300Z | 1 | SUSPECT | creator is NOT Tom (snapshot="POL Planner") |
| PO-2026-00135 | PO-2026-00135 | MPGT Supplier | CANCELLED | manual |  | 2026-04-26T10:38:42.669Z | 1 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator looks test: email= snapshot=manual po test planner; creator is NOT Tom (snapshot="Manual PO test planner") |
| PO-2026-00136 | PO-2026-00136 | MPGT Supplier | CANCELLED | manual |  | 2026-04-26T10:38:43.305Z | 1 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator looks test: email= snapshot=manual po test admin; creator is NOT Tom (snapshot="Manual PO test admin") |
| PO-2026-00137 | PO-2026-00137 | MPGT Supplier | CANCELLED | manual |  | 2026-04-26T10:38:44.078Z | 1 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator looks test: email= snapshot=manual po test planner; creator is NOT Tom (snapshot="Manual PO test planner") |
| T1REG-1777205442687-PO1 | T1REG-1777205442687-PO1 | T1 Reg Supplier | OPEN | manual |  | 2026-04-26T12:10:44.030Z | 1 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator is NOT Tom (snapshot="T1 Reg") |
| T1REG-1777205442687-PO-CAN | T1REG-1777205442687-PO-CAN | T1 Reg Supplier | CANCELLED | manual |  | 2026-04-26T12:10:44.488Z | 1 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator is NOT Tom (snapshot="T1 Reg") |
| T2DET-1777210102536-PO | T2DET-1777210102536-PO | T2 Det Supplier | OPEN | manual |  | 2026-04-26T13:28:25.330Z | 1 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator is NOT Tom (snapshot="T2 Det") |
| T2DET-1777210369167-PO | T2DET-1777210369167-PO | T2 Det Supplier | OPEN | manual |  | 2026-04-26T13:32:51.945Z | 1 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator is NOT Tom (snapshot="T2 Det") |
| T2DET-1777672523274-PO | T2DET-1777672523274-PO | T2 Det Supplier | OPEN | manual |  | 2026-05-01T21:55:25.972Z | 1 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator is NOT Tom (snapshot="T2 Det") |
| T2DET-1777672599087-PO | T2DET-1777672599087-PO | T2 Det Supplier | OPEN | manual |  | 2026-05-01T21:56:42.181Z | 1 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator is NOT Tom (snapshot="T2 Det") |
| PO-2026-00139 | PO-2026-00139 | MPGS Supplier | CANCELLED | manual |  | 2026-05-02T06:37:46.546Z | 1 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator is NOT Tom (snapshot="MPGS planner") |
| PO-2026-00140 | PO-2026-00140 | MPGS Supplier | CANCELLED | manual |  | 2026-05-02T06:37:47.117Z | 1 | SUSPECT | creator is NOT Tom (snapshot="MPGS planner") |
| PO-2026-00141 | PO-2026-00141 | MPGS Supplier | CANCELLED | manual |  | 2026-05-02T06:37:47.811Z | 1 | SUSPECT | creator is NOT Tom (snapshot="MPGS admin") |
| PO-2026-00142 | PO-2026-00142 | MPGT Supplier | CANCELLED | manual |  | 2026-05-02T06:38:49.265Z | 1 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator looks test: email= snapshot=manual po test planner; creator is NOT Tom (snapshot="Manual PO test planner") |
| PO-2026-00143 | PO-2026-00143 | MPGT Supplier | CANCELLED | manual |  | 2026-05-02T06:38:49.824Z | 1 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator looks test: email= snapshot=manual po test admin; creator is NOT Tom (snapshot="Manual PO test admin") |
| PO-2026-00144 | PO-2026-00144 | MPGT Supplier | CANCELLED | manual |  | 2026-05-02T06:38:50.463Z | 1 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator looks test: email= snapshot=manual po test planner; creator is NOT Tom (snapshot="Manual PO test planner") |
| PO-PLS-EMPTY-1777707847241 | PON-PLS-E-1777707847241 | PLS Test Supplier | OPEN | manual |  | 2026-05-02T07:44:08.781Z | 0 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; no PO lines; creator is NOT Tom (snapshot="PLS Planner") |
| PO-PLS-FULL-1777707847241 | PON-PLS-F-1777707847241 | PLS Test Supplier | OPEN | manual |  | 2026-05-02T07:44:08.781Z | 0 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; no PO lines; creator is NOT Tom (snapshot="PLS Planner") |
| PO-PLS-PARTIAL-1777707847241 | PON-PLS-P-1777707847241 | PLS Test Supplier | PARTIAL | manual |  | 2026-05-02T07:44:08.781Z | 0 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; no PO lines; creator is NOT Tom (snapshot="PLS Planner") |
| PO-PLS-EMPTY-1777707877067 | PON-PLS-E-1777707877067 | PLS Test Supplier | OPEN | manual |  | 2026-05-02T07:44:38.478Z | 0 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; no PO lines; creator is NOT Tom (snapshot="PLS Planner") |
| PO-PLS-FULL-1777707877067 | PON-PLS-F-1777707877067 | PLS Test Supplier | OPEN | manual |  | 2026-05-02T07:44:38.478Z | 2 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator is NOT Tom (snapshot="PLS Planner") |
| PO-PLS-PARTIAL-1777707877067 | PON-PLS-P-1777707877067 | PLS Test Supplier | PARTIAL | manual |  | 2026-05-02T07:44:38.478Z | 1 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator is NOT Tom (snapshot="PLS Planner") |
| PO-2026-00146 | PO-2026-00146 | MPGT Supplier | OPEN | manual |  | 2026-05-02T07:44:47.761Z | 1 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator looks test: email= snapshot=manual po test planner; creator is NOT Tom (snapshot="Manual PO test planner") |
| PO-2026-00147 | PO-2026-00147 | MPGT Supplier | OPEN | manual |  | 2026-05-02T07:44:48.513Z | 1 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator looks test: email= snapshot=manual po test admin; creator is NOT Tom (snapshot="Manual PO test admin") |
| PO-2026-00148 | PO-2026-00148 | MPGT Supplier | OPEN | manual |  | 2026-05-02T07:44:49.334Z | 1 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator looks test: email= snapshot=manual po test planner; creator is NOT Tom (snapshot="Manual PO test planner") |
| PO-2026-00149 | PO-2026-00149 | MPGT Supplier | OPEN | manual |  | 2026-05-02T07:44:58.505Z | 1 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator looks test: email= snapshot=manual po test planner; creator is NOT Tom (snapshot="Manual PO test planner") |
| PO-2026-00150 | PO-2026-00150 | MPGT Supplier | OPEN | manual |  | 2026-05-02T07:44:59.297Z | 1 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator looks test: email= snapshot=manual po test admin; creator is NOT Tom (snapshot="Manual PO test admin") |
| PO-2026-00151 | PO-2026-00151 | MPGT Supplier | OPEN | manual |  | 2026-05-02T07:45:00.188Z | 1 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator looks test: email= snapshot=manual po test planner; creator is NOT Tom (snapshot="Manual PO test planner") |
| PO-PLS-EMPTY-1777707932674 | PON-PLS-E-1777707932674 | PLS Test Supplier | OPEN | manual |  | 2026-05-02T07:45:33.634Z | 0 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; no PO lines; creator is NOT Tom (snapshot="PLS Planner") |
| PO-PLS-FULL-1777707932674 | PON-PLS-F-1777707932674 | PLS Test Supplier | OPEN | manual |  | 2026-05-02T07:45:33.634Z | 2 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator is NOT Tom (snapshot="PLS Planner") |
| PO-PLS-PARTIAL-1777707932674 | PON-PLS-P-1777707932674 | PLS Test Supplier | PARTIAL | manual |  | 2026-05-02T07:45:33.634Z | 1 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator is NOT Tom (snapshot="PLS Planner") |
| PO-2026-00152 | PO-2026-00152 | POH Test Supplier | CANCELLED | recommendation |  | 2026-05-02T07:45:54.108Z | 1 | SUSPECT | test marker in notes/reason/idem/po_number/created_by_snapshot; creator is NOT Tom (snapshot="POH Planner") |
| PO-2026-00153 | PO-2026-00153 | POL Test Supplier | OPEN | recommendation |  | 2026-05-02T07:45:54.249Z | 1 | SUSPECT | creator is NOT Tom (snapshot="POL Planner") |
| PO-2026-00154 | PO-2026-00154 | POC Test Supplier | CANCELLED | recommendation |  | 2026-05-02T07:45:54.299Z | 1 | SUSPECT | creator is NOT Tom (snapshot="POC Planner") |
| PO-2026-00155 | PO-2026-00155 | POC Test Supplier | CANCELLED | recommendation |  | 2026-05-02T07:45:54.449Z | 1 | SUSPECT | creator is NOT Tom (snapshot="POC Planner") |

## POs with attached Goods Receipts (DO NOT BLIND DELETE)

_None._

## REAL POs

| po_id | po_number | supplier | status | source_type | created_by_email | created_at | lines |
|---|---|---|---|---|---|---|---|
| PO-2026-00145 | PO-2026-00145 | צבר אריזות | CANCELLED | manual | tom@gteveryday.com | 2026-05-02T06:41:35.818Z | 1 |

## orders_mirror staleness

- Total orders_mirror rows: 269
- Total orders_mirror_lines: 714
- Oldest captured_at: Sat Apr 18 2026 20:30:47 GMT+0300 (שעון ישראל (קיץ))
- Newest captured_at: Sat May 02 2026 19:00:04 GMT+0300 (שעון ישראל (קיץ))
- Rows with captured_at older than 7 days: 164
- Rows with captured_at older than 30 days: 0
- Rows with retired_at set: 0

Schema note: this mirror has no `last_synced_at`; freshness is best read off `captured_at` (last poll that re-saw the order). Without LionWheel API access from this audit, "fake" mirror rows can only be inferred via stale `captured_at` + non-retired status (rows that polling stopped re-seeing but were never retired). Real cleanup needs an authoritative LionWheel set for cross-check, or a sweep job that retires anything missed N polls in a row.

## LionWheel integration_runs (last 30 days)

See raw audit sections 8b-8e for per-day status counts. High-level: success/unknown/failure split is in 8e.

## Notes

- A PO is REAL when: created_by is Tom (admin), supplier_id is in canonical suppliers, all line component_id/item_id refs resolve, and no test/fixture/smoke markers in notes/reason/idempotency_key/po_number.
- A PO is SUSPECT when any of: orphan supplier/component/item ref, test marker present, creator email matches test pattern, or no lines.
- LINKED-GR POs have stock_ledger consequences. Cleanup must reverse the ledger first or risk parity drift.
- Full per-section query output (column shapes, row dumps, integration run counts, etc.) lives in `cleanup_audit_pos_raw.txt`.
