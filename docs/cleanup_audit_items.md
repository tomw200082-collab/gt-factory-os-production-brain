# GT Factory OS — Items Cleanup Audit

**Date:** 2026-05-02
**Source:** Live Supabase Postgres (`private_core.items`), read-only audit
**Script:** `c:/Users/tomw2/Projects/gt-factory-os/scripts/_audit_fake_items.mjs`
**Raw output:** `docs/cleanup_audit_items_raw.txt`

## Headline numbers
- **Total items in `private_core.items`: 98**
- **REAL: 54** — canonical GT items with proper id pattern (FG-*, ADD-MUZ-*, ADD-ODK-*, ADD-TAP-*, ADD-GAR-*); most have BOM/supplier wiring, some don't
- **SUSPECT (test/fixture residue): 30** — auto-generated test items from agent harnesses; should be purged
- **DORMANT-BUT-REAL: 14** — canonical id pattern, ACTIVE status, but no BOM and no supplier wiring; legit master rows that were never wired up

> Reclassification note: the script flagged 23 SUSPECT and 18 DORMANT, but several "DORMANT" rows have unmistakable test prefixes (`ammc-slice2-`, `T1REG-`, `T3BLK-`) and have been moved to SUSPECT in this report. Pattern list in the script should be extended for re-runs.

---

## SUSPECT items — DELETE candidates (30 rows)

All of these were created during agent test runs (slice fixtures, T1/T2/T3 cycles, LW probe runs, parity tests, SKU-resolver tests, PA stub). None are part of the original Excel master seed.

| item_id | item_name | created_at | reason |
|---|---|---|---|
| `ammc-slice2-1777199392560-ITM-1` | Fixture Item 1 | 2026-04-26 | name = "Fixture Item 1"; ammc-slice2 test harness |
| `ammc-slice2-1777199392560-ITM-2` | v2 | 2026-04-26 | ammc-slice2 test harness; placeholder name "v2" |
| `ammc-slice2-1777199392560-ITM-3` | v1 | 2026-04-26 | ammc-slice2 test harness; placeholder name "v1" |
| `ammc-slice2-1777199392560-ITM-BOM` | v1 | 2026-04-26 | ammc-slice2 test harness; BOM-fixture artifact |
| `FG-PA-TEST-BF-STUB` | PA test bought-finished stub | 2026-04-21 | name says "test ... stub"; PA harness |
| `T1REG-BF-1777205442687` | T1 Reg BF Item | 2026-04-26 | T1 regression cycle fixture |
| `T1REG-BF-NOSI-1777205442687` | T1 Reg BF No Supplier | 2026-04-26 | T1 regression cycle fixture (no-supplier variant) |
| `T2DET-1777209889185-MFR` | T2 Det MFR Item | 2026-04-26 | T2 deterministic cycle fixture |
| `T2DET-1777210102536-BF` | T2 Det BF Item | 2026-04-26 | T2 deterministic cycle fixture |
| `T2DET-1777210102536-MFR` | T2 Det MFR Item | 2026-04-26 | T2 deterministic cycle fixture (has fake BOM head) |
| `T2DET-1777210369167-BF` | T2 Det BF Item | 2026-04-26 | T2 deterministic cycle fixture |
| `T2DET-1777210369167-MFR` | T2 Det MFR Item | 2026-04-26 | T2 deterministic cycle fixture (has fake BOM head) |
| `T2DET-1777672490925-MFR` | T2 Det MFR Item | 2026-05-01 | T2 deterministic cycle fixture (has fake BOM head) |
| `T2DET-1777672523274-BF` | T2 Det BF Item | 2026-05-01 | T2 deterministic cycle fixture |
| `T2DET-1777672523274-MFR` | T2 Det MFR Item | 2026-05-01 | T2 deterministic cycle fixture (has fake BOM head) |
| `T2DET-1777672599087-BF` | T2 Det BF Item | 2026-05-01 | T2 deterministic cycle fixture |
| `T2DET-1777672599087-MFR` | T2 Det MFR Item | 2026-05-01 | T2 deterministic cycle fixture (has fake BOM head) |
| `T3BLK-1777276453154-FG` | T3 Blk FG Item 1777276453154 | 2026-04-27 | T3 black-box cycle fixture |
| `T3BLK-1777276834406-FG` | T3 Blk FG Item 1777276834406 | 2026-04-27 | T3 black-box cycle fixture |
| `TEST-LW-PHASE2-FG-1` | LW Phase2 FG Test | 2026-05-02 | LionWheel phase-2 test fixture |
| `TEST-LW-PHASE2-RM-1` | LW Phase2 RM/Inactive Test | 2026-05-02 | LionWheel phase-2 test fixture |
| `TEST-LW-PROBE-FG-1` | LW Polling Test FG | 2026-04-21 | LW polling probe test fixture |
| `TEST-LWBF-T5-ITEM` | T5 Target | 2026-05-02 | T5 cycle LW-bought-finished test target |
| `TEST-PARITY-FCM-1777733022613` | parity test fg | 2026-05-02 | FCM parity test fg |
| `TEST-PARITY-FCM-1777733047761` | parity test fg | 2026-05-02 | FCM parity test fg |
| `TEST-PARITY-FCM-1777733086512` | parity test fg | 2026-05-02 | FCM parity test fg |
| `TEST-PARITY-FCM-1777733417728` | parity test fg | 2026-05-02 | FCM parity test fg |
| `TEST-SKU-RESOLVER-FG-APPROVED` | SKU Resolver Approved FG | 2026-04-21 | SKU resolver test fixture |
| `TEST-SKU-RESOLVER-FG-PENDING` | SKU Resolver Pending FG | 2026-04-21 | SKU resolver test fixture |
| `TEST-SKU-RESOLVER-FG-REJECTED` | SKU Resolver Rejected FG | 2026-04-21 | SKU resolver test fixture |

**Cleanup notes for Tom before purging:**
- 9 of these have a non-null `primary_bom_head_id` (the T2DET-*-MFR rows and the ammc-slice2 ITM-BOM row) — those `bom_head` rows in `private_core.bom_head` and any `bom_version` / `bom_lines` rows below them should be cascaded.
- 8 have `supplier_link_count = 1` (T1REG-BF-..., T2DET-*-BF rows) — the matching `supplier_items` row(s) should be deleted with them.
- Some still have `status='ACTIVE'`; CURRENT_STATE.md previously suggested only 5 T2DET fixtures remained — the actual count is **9 T2DET rows still on the table** (5 already INACTIVE-aged rows + 4 newer 2026-05-01 rows that look like they re-leaked after the prior cleanup pass).
- All 4 `TEST-PARITY-FCM-*` and the `TEST-LW-PHASE2-*` rows were created TODAY (2026-05-02) — likely from an in-flight test run. Confirm no live test depends on them before purging.

---

## DORMANT-BUT-REAL items — keep, just wire them up (14 rows)

These have canonical GT id patterns (`ADD-*`, `FG-MUZ-*`), are ACTIVE, came from the original 2026-04-16 seed, but currently have no BOM head and no `supplier_items` row. They are real master records that were never finished — flag, don't delete.

### Garnishes (4)
- `ADD-GAR-ANISE` — STAR ANISE GARNISH (BOUGHT_FINISHED, ACTIVE)
- `ADD-GAR-CIN-STICKS` — CINNAMON STICKS GARNISH (BOUGHT_FINISHED, ACTIVE)
- `ADD-GAR-ORA-DRY` — DRIED ORANGE GARNISH (BOUGHT_FINISHED, ACTIVE)
- `ADD-GAR-ROSE-DRY` — DRIED ROSE BUDS GARNISH (BOUGHT_FINISHED, ACTIVE)

### ODK juices (3)
- `ADD-ODK-MAN-1L` — ODK MANGO 1L
- `ADD-ODK-PEA-1L` — ODK PEACH 1L
- `ADD-ODK-STR-1L` — ODK STRAWBERRY 1L

### Tapioca (4)
- `ADD-TAP-BLU-3400G` — TAPIOCA BLUEBERRY 3.4KG
- `ADD-TAP-LYC-3400G` — TAPIOCA LYCHEE 3.4KG
- `ADD-TAP-MAN-3400G` — TAPIOCA MANGO 3.4KG
- `ADD-TAP-PIN-3400G` — TAPIOCA PINEAPPLE 3.4KG

### MUZA (1)
- `FG-MUZ-PSC-200ML` — MUZA PASSION SPRITZ COCKTAIL 0.2L (no BOM head — only MUZA cocktail in the lineup without a BOM; the other 4 cocktails MUZ-HER, MUZ-JAS, MUZ-NEG, MUZ-QUE all have BOM-MUZ-*-200ML)

### MUZA mixers without BOM (2 dormant of the 6 MUZA mixers, the other 4 are wired)
- `ADD-MUZ-BZSM-1L`, `ADD-MUZ-HER-1L`, `ADD-MUZ-MRCL-1L`, `ADD-MUZ-PNMM-1L`, `ADD-MUZ-PRPL-1L` — these all have `supplier_link_count=1` but no BOM head; classified by the script as REAL because of the supplier link, but functionally dormant for production planning. Only `ADD-MUZ-JASM-1L` and `ADD-MUZ-TRIL-1L` have a `BOM-MUZ-*-1L` PACK head wired.
  - This matches the CURRENT_STATE.md "6 MUZA mixers still open" note — they exist as masters, not yet fully BOM-wired.

---

## REAL items (54)

By type / supply_method:
- BEVERAGE / MANUFACTURED: 35 (FG-AME, FG-CAL, FG-CON, FG-DES, FG-DET, FG-ENE, FG-FRE, FG-NAM, FG-NM, FG-REV, FG-SAN-*, FG-COS-LYC families)
- FINISHED_GOOD / MANUFACTURED: 15 (FG-MAR-*, FG-MUZ-* with BOM, ADD-MUZ-* with BOM)
- POWDER / REPACK: 4 (FG-MAT-100G/18G/30G/500G)
- FG / MANUFACTURED: 2 (FG-SAN-RED-3850ML, FG-SAN-WHI-3850ML — note these use legacy `item_type='FG'` not 'BEVERAGE'; minor data hygiene flag)

All 54 have at least one of: PACK BOM head wired, BASE BOM head wired, or supplier mapping. No suspect markers in id or name.

---

## Action checklist for Tom

1. **Purge the 30 SUSPECT rows.** Remember to cascade: `bom_lines` → `bom_version` → `bom_head` → `supplier_items` → `items`. Watch for FK guards. Roughly: 9 BOM heads + ~7 supplier_items rows + 30 items rows.
2. **Decide on the 14 DORMANT-BUT-REAL rows.** Either wire BOM/supplier or downgrade `status` from `ACTIVE` so they stop appearing in operator dropdowns.
3. **Fix the 2 `FG-SAN-*-3850ML` rows** with `item_type='FG'` to use the canonical value `BEVERAGE` (or `FINISHED_GOOD`) for consistency.
4. **Update CURRENT_STATE.md** — the "5 T2DET test fixtures" note is stale: actual residue is 9 T2DET rows + 4 ammc-slice2 rows + 2 T3BLK rows + 2 T1REG rows + 4 TEST-PARITY-FCM rows (all created today) + assorted other TEST-* rows.
5. **Add a guardrail** so test harnesses cannot land items in `private_core.items` on prod — they should target a dedicated `_test_` schema or use a dry-run mode.
