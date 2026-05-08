# Fake Masters Cleanup Audit

**Run:** 2026-05-02 (UTC)
**Database:** Supabase Postgres (DATABASE_URL_POOLED), schema `private_core`
**Mode:** READ-ONLY. SELECTs only. No DDL, no DML.
**Scripts:** `c:/Users/tomw2/Projects/gt-factory-os/scripts/_audit_fake_masters.mjs` (initial discovery), `_audit_fake_masters_v2.mjs` (column-corrected), `_audit_fake_masters_v3.mjs` (price_history join fix)
**Raw output:** `docs/cleanup_audit_masters_raw.txt`

## Reading guide

Two distinct buckets of "non-real" rows showed up. Treat them differently:

1. **Definitely test-fixture rows** — names match `TEST | FIXTURE | SMOKE | T1REG | T2DET | T3A | T3BLK | T13 | DEMO | E2E | POC | POH | POL | PLS | GRR | LCC | LU | ammc-slice | PH9-BRIDGE | MANUALPG | MPGS | PARITY | race-test`, or IDs carry the `-1777xxxxxxxxx` epoch-stamp pattern. **Safe to delete after FK cascade check.**
2. **Real seed rows with no usage yet** — e.g. seeded suppliers (SUP-NNN) or seed-imported `supplier_items` that simply have no PO history yet. **Do NOT delete; they are part of the canonical seed.** Listed for visibility only.

The "real but uncritically used" bucket needs Tom's eye, not Claude's hand.

---

## 1) suppliers — baseline 43, **current 104, delta +61**

### Definitely test rows (36 by name pattern, 31 also flagged by long IDs; overlap heavy)

All 30+ rows below are `INACTIVE` or `ACTIVE` test fixtures created during agent test runs. The IDs all carry the millisecond-epoch pattern `-1777xxxxxxxxx`.

**SUSPECT supplier_ids (35 unique, in cleanup priority order):**

```
SUP-POC-1777707953056          SUP-POL-1777707952974          SUP-POH-1777707952903
SUP-PLS-1777707932674          SUP-PLS-1777707877067          SUP-PLS-1777707847241
T2DET-1777672599087-SUP        T2DET-1777672523274-SUP        T2DET-1777672490925-SUP
T3BLK-1777276834406-SUP        T3BLK-1777276453154-SUP
T2DET-1777210369167-SUP        T2DET-1777210102536-SUP        T2DET-1777209889185-SUP
T1REG-SUP-1777205442687
SUP-POL-1777199916078          SUP-LU-1777199910957           SUP-LCC-1777199905261
SUP-POH-1777199900501          SUP-GRR-1777199894888          SUP-POC-1777199890616
SUP-E2E-1777199837665          SUP-POL-1777199736895          SUP-LU-1777199731523
SUP-LCC-1777199726175          SUP-POH-1777199722022          SUP-GRR-1777199716223
SUP-POC-1777199711907          SUP-E2E-1777199656857
ammc-slice2-1777199392560-SUP-1   ammc-slice2-1777199392560-SUP-2   ammc-slice2-1777199392560-SUP-3
ammc-slice2-1777199392560-SUP-SI-A   ammc-slice2-1777199392560-SUP-SI-B
ammc-slice2-1777199392560-SUP-SI2    ammc-slice2-1777199392560-SUP-SI3
```

Plus 18 manual-PG fixtures (also `-1777xxxxxxxxx`):
```
SUP-MANUALPG-1777199004404 / SUP-MANUALPG-NOMAP-1777199004404
SUP-MANUALPG-1777199094055 / SUP-MANUALPG-NOMAP-1777199094055
SUP-MANUALPG-1777199275260 / SUP-MANUALPG-NOMAP-1777199275260
SUP-MANUALPG-1777199283819 / SUP-MANUALPG-NOMAP-1777199283819
SUP-MANUALPG-1777199648931 / SUP-MANUALPG-NOMAP-1777199648931
SUP-MANUALPG-1777199713138 / SUP-MANUALPG-NOMAP-1777199713138
SUP-MANUALPG-1777199742840 / SUP-MANUALPG-NOMAP-1777199742840
SUP-MANUALPG-1777199921406 / SUP-MANUALPG-NOMAP-1777199921406
SUP-MANUALPG-1777703928014 / SUP-MANUALPG-NOMAP-1777703928014
SUP-MANUALPG-1777707886150 / SUP-MANUALPG-NOMAP-1777707886150
SUP-MANUALPG-1777707896837 / SUP-MANUALPG-NOMAP-1777707896837
SUP-MPGS-1777703864994
SUP-PH9-BRIDGE-1777199663446
SUP-PH9-BRIDGE-1777199844389
```

**Total clearly-test suppliers: ~58.** Subtracting from delta +61 means ~3 of the +61 are not obvious fixtures — most likely `SUP-001-MATCHA`, `SUP-ELIRAN-KARTONIM`, `SUP-TAVLINEI-BAR` (string-aliased duplicates of SUP-001/SUP-020/SUP-015 — see seed-time aliasing). Tom should decide whether those alias-IDs stay.

### Real seed rows with zero supplier_items + zero POs (NOT test, do not delete)

These are seed suppliers that have not yet been assigned components or POs. Listed for visibility:

```
SUP-001-MATCHA  SUP-019  SUP-028  SUP-030  SUP-031  SUP-034  SUP-035  SUP-037
SUP-038  SUP-040  SUP-043  SUP-045  SUP-ELIRAN-KARTONIM  SUP-TAVLINEI-BAR
```

---

## 2) components — baseline 145, **current 213, delta +68**

### Test-pattern by name (26 rows)

All match `*Test Component`, `T2 Det Component`, `T3 Blk Component*`, `E2E Component`, `T1 Reg Component`, `Raw Peach Puree (race-test fixture)`, etc.

**SUSPECT component_ids (26):**
```
COMP-POC-1777707953056   COMP-POL-1777707952974   COMP-POH-1777707952903
COMP-PLS-1777707932674   COMP-PLS-1777707877067
T2DET-1777672599087-COMP T2DET-1777672523274-COMP T2DET-1777672490925-COMP
T2DET-1777210369167-COMP T2DET-1777210102536-COMP T2DET-1777209889185-COMP
COMP-POL-1777199916078   COMP-LU-1777199910957    COMP-LCC-1777199905261
COMP-POH-1777199900501   COMP-GRR-1777199894888   COMP-POC-1777199890616
COMP-E2E-1777199837665
COMP-POL-1777199736895   COMP-LU-1777199731523    COMP-LCC-1777199726175
COMP-POH-1777199722022   COMP-GRR-1777199716223   COMP-POC-1777199711907
COMP-E2E-1777199656857
RAW-PEACH-PUREE
```

### Orphan: zero bom_lines refs AND zero supplier_items refs (29 rows)

Superset of the test-pattern list above, plus three additional rows that need Tom's review (not test names but unused):

```
T3BLK-1777276834406-COMP       T3BLK-1777276834406-COMP-INFO    T3BLK-1777276834406-COMP-OTHER
T3BLK-1777276453154-COMP       T3BLK-1777276453154-COMP-INFO    T3BLK-1777276453154-COMP-OTHER
T1REG-COMP-PO-1777205442687-CAN  T1REG-COMP-PO-1777205442687
PKG-CARTON-MAT-30G   ← seed import, not test, but unused. Review.
PKG-PACK-MAT-30G     ← seed import, not test, but unused. Review.
```

---

## 3) bom_head — baseline 68, **current 85, delta +17**

Breakdown by `bom_kind`: BASE=28, PACK=53, REPACK=4. The +17 = MUZA additions from migrations 0087/0088 (12 PACK heads `BOM-MUZ-*`, real) + 5 test BOM heads.

### Test rows (5)

All from T2DET test runs (BASE heads with NULL parent_ref_*):
```
T2DET-1777672599087-BOM-HEAD
T2DET-1777672523274-BOM-HEAD
T2DET-1777672490925-BOM-HEAD
T2DET-1777210369167-BOM-HEAD
T2DET-1777210102536-BOM-HEAD
```

No orphan parent_ref FKs (3f returned 0).

---

## 4) bom_version — baseline 68, **current 99, delta +31**

By status: ACTIVE=79, ARCHIVED=5, DRAFT=15.

### Test rows by linked head parent (5)

Same T2DET heads as section 3:
```
599231ba-9f67-44dd-84ac-a9c20e154f51   bom_head=T2DET-1777672599087-BOM-HEAD
cbf6cda6-8613-44eb-ab63-ae22c104d715   bom_head=T2DET-1777672523274-BOM-HEAD
8a9e728e-b86e-4edd-9d70-6c421fb21447   bom_head=T2DET-1777672490925-BOM-HEAD
46038a52-92a5-4609-b094-a5bf0a978c27   bom_head=T2DET-1777210369167-BOM-HEAD
6cfee0e5-b02b-482f-8edc-61458cf4ed89   bom_head=T2DET-1777210102536-BOM-HEAD
```

### DRAFT versions never activated (15) — REVIEW, not auto-delete

These are DRAFT rows on **real** PACK/BASE heads (likely planner sandboxing or 0087/0088 MUZA seeds left in DRAFT). They are not test fixtures, but they are clutter. Tom should decide whether to ARCHIVE them en masse:

```
4fab7d10  BOM-PACK-SAN-WHI-1L     WHITE SANGRIA 1L
6adf0d27  BOM-BASE-SAN-WHI-REG    WHITE SANGRIA BASE MIX
7e859095  BOM-PACK-AME-500ML      AMERICAN 0.5L
c36ad873  BOM-PACK-AME-1L         AMERICAN 1L
746a53fc  BOM-MUZ-QUE-200ML       MUZA QUEEN VIOLET COCKTAIL 0.2L
aaef9c71  BOM-PACK-CON-1L         CONSCIOUSNESS 1L
2d340347  BOM-BASE-CON-REG        CONSCIOUSNESS BASE MIX
6d0116d7  BOM-BASE-CAL-REG        CALM BASE MIX
d24d342b  BOM-MUZ-PNMM-1L         MUZA PINK MAMA MIXER 1L     (V1_SEED)
aed11018  BOM-MUZ-PSC-200ML       MUZA PASSION SPRITZ COCKTAIL 0.2L  (V1_SEED)
474ae387  BOM-MUZ-PRPL-1L         MUZA PURPLE KISS MIXER 1L   (V1_SEED)
083da732  BOM-MUZ-BZSM-1L         MUZA BASIL SMASH MIXER 1L   (V1_SEED)
1a91a97c  BOM-MUZ-MRCL-1L         MUZA CLASSIC MARGARITA MIXER 1L  (V1_SEED)
b06e17e1  BOM-MUZ-HER-1L          MUZA HERBAL MULE BLISS MIXER 1L  (V1_SEED)
3498e6d8  BOM-BASE-AME-REG        AMERICAN BASE MIX
```

The 7 with label `V1_SEED` are real but never activated — likely awaiting Tom's MUZA recipe review.

---

## 5) bom_lines — baseline 420, **current 603, delta +183**

By `component_ref_type`: BASE_BOM=53, **BOM=10**, COMPONENT=197, RAW_NAME=343.

### CRITICAL: 10 legacy `'BOM'` ref-type rows still present on PACK heads

Migration 0131 was supposed to clean these up. They survive on the three MARGARITA PACK heads and the two big SAN-RED/SAN-WHI 3850ML heads, **two rows each (different bom_versions)**:

```
line_id                                bom_head_id              parent_name
5a2c511a-4904-4e9c-a7c9-ebaff5175ca8   BOM-PACK-MAR-CLA-300ML   MARGARITA CLASSIC 0.3L
92ea0804-3aec-462f-a7a1-cc5daabbc433   BOM-PACK-MAR-CLA-300ML   MARGARITA CLASSIC 0.3L
a598e863-652e-484e-9a7e-b2062b0ee7fa   BOM-PACK-MAR-PEA-300ML   MARGARITA PEAR 0.3L
e2f5cd76-f565-4595-a3b7-c04fa4ecd608   BOM-PACK-MAR-PEA-300ML   MARGARITA PEAR 0.3L
5d498628-51ba-4545-b353-c4091b119dfb   BOM-PACK-MAR-STR-300ML   MARGARITA STRAWBERRY 0.3L
f621a3d6-fe12-4f94-bebd-0b2e16fc99e1   BOM-PACK-MAR-STR-300ML   MARGARITA STRAWBERRY 0.3L
5fffaffe-41ab-4e44-8367-d4956846d1cb   BOM-PACK-SAN-RED-3850ML  RED SANGRIA ELITA 3.85L
c4dbe04e-00c7-4c6f-b4d8-72bff23c4bdc   BOM-PACK-SAN-RED-3850ML  RED SANGRIA ELITA 3.85L
42fb9236-8fa2-4935-8e87-208845b8632d   BOM-PACK-SAN-WHI-3850ML  WHITE SANGRIA ELITA 3.85L
bf445b81-4e2a-40ea-8e39-9b7c8edadf89   BOM-PACK-SAN-WHI-3850ML  WHITE SANGRIA ELITA 3.85L
```

These survive on **non-active** versions (not blocked by `bom_lines_no_bom_ref_on_pack_active` because that constraint only fires on active versions). Still — they are legacy artifacts that 0131 should have caught, and a future activation of any of these versions would be blocked. Worth flagging.

No orphan-component-FK rows. 5 lines belong to test-pattern T2DET BOM heads.

---

## 6) supplier_items — baseline 185, **current 231, delta +46**

### Test rows by linked supplier/component (15) — DELETE candidates

```
bf241c9d  T2DET-1777672599087-SUP / NULL component
5de1ab45  T2DET-1777672599087-SUP / T2DET-1777672599087-COMP
22f4b8b7  T2DET-1777672523274-SUP / NULL component
4daaf6c9  T2DET-1777672523274-SUP / T2DET-1777672523274-COMP
80d2390c  T2DET-1777672490925-SUP / T2DET-1777672490925-COMP
07d4cbf6  T2DET-1777210369167-SUP / NULL component
5e5058dd  T2DET-1777210369167-SUP / T2DET-1777210369167-COMP
5f4ab954  T2DET-1777210102536-SUP / NULL component
015b53fc  T2DET-1777210102536-SUP / T2DET-1777210102536-COMP
8b4ea17d  T1REG-SUP-1777205442687 / T1REG-COMP-PO-1777205442687-E6
f243368d  T1REG-SUP-1777205442687 / NULL component
e1b5a1e3  SUP-E2E-1777199837665 / COMP-E2E-1777199837665
6607300a  SUP-E2E-1777199656857 / COMP-E2E-1777199656857
9fb5337c  SUP-015 / RAW-LUISA   ← false positive (RAW-LUISA is real, "luisa" matched LU regex)
64b3c0b1  SUP-023 / RAW-LUISA   ← false positive
```

Note: the last two (`RAW-LUISA`) are legitimate seed rows; the test-pattern regex caught `LU` substring. **Exclude them from delete.**

Plus PH9-BRIDGE / MANUALPG fixtures captured by the broader "no_po_no_price_history" query (12 more): `0848e20c, c52270be, 29b32283, 2035b63d, 96023863, b0aeb34d, 14b7edc8` and 5 from MUZA stickers `6897f5a2, 8ac6136b, af357ce9, 57039bf6, b2dcc9d7` (the MUZA stickers are likely real seed rows from 0087/0088 — REVIEW, not delete).

### Real seed supplier_items with no PO/price evidence yet (~33 rows) — DO NOT DELETE

55 rows total returned by the no_po_no_price_history check. After subtracting 13 test rows, ~42 remain. The bulk are seed rows for SUP-022 (Miki Madbekot stickers), SUP-020 (Eliran Kartonim cartons), SUP-003 (Propack matcha bags), SUP-008 (Holyland syrups), SUP-016 (Tempo), SUP-041 (Muza Cocktails), SUP-005 (Elita Ofek), SUP-018 (Ziv Chemically), SUP-004 (D&D Mashkaot). These are **real masters** — they simply haven't been ordered yet in the rebuilt platform. Listed in raw output for Tom's reference.

---

## 7) planning_policy — baseline 5, **current 15, delta +10**

All 15 keys are legitimate operational policy:

- 5 originals (count thresholds, waste threshold, capacity)
- +10 `planning.*` keys added by Gate 5 contract (FP-2, horizon, freeze, safety, supplier default lead time, run duration, etc.) — these are **REAL** and ratified per `gate5_policy_keys_contract.md`.

**No suspect rows.** Baseline expectation should be updated from 5 → 15.

---

## 8) items — baseline 68, **current 98, delta +30** (bonus, not in original ask)

Test-pattern items (23 ids):
```
TEST-PARITY-FCM-1777733417728   TEST-PARITY-FCM-1777733086512
TEST-PARITY-FCM-1777733047761   TEST-PARITY-FCM-1777733022613
TEST-LWBF-T5-ITEM
TEST-LW-PHASE2-RM-1   TEST-LW-PHASE2-FG-1
T2DET-1777672599087-BF   T2DET-1777672599087-MFR
T2DET-1777672523274-BF   T2DET-1777672523274-MFR
T2DET-1777672490925-MFR
T2DET-1777210369167-BF   T2DET-1777210369167-MFR
T2DET-1777210102536-BF   T2DET-1777210102536-MFR
T2DET-1777209889185-MFR
ammc-slice2-1777199392560-ITM-1
FG-PA-TEST-BF-STUB
TEST-SKU-RESOLVER-FG-APPROVED   TEST-SKU-RESOLVER-FG-PENDING   TEST-SKU-RESOLVER-FG-REJECTED
TEST-LW-PROBE-FG-1
```

The remaining +7 items above baseline = the 7 MUZA mixer/cocktail items added intentionally by 0087/0088. Real, do not flag.

---

## Cleanup priority (Tom's call)

1. **HIGH:** the 10 `'BOM'` ref-type bom_lines on PACK heads (5d) — migration 0131 missed these.
2. **HIGH:** delete the cleanly-test-pattern suppliers, components, items, supplier_items, bom_head, bom_version rows (~58 suppliers, ~26 components, ~23 items, ~13 supplier_items, ~5 bom_heads, ~5 bom_versions). All have epoch-stamped IDs, no PO history, no production usage.
3. **MEDIUM:** review the 15 DRAFT bom_versions (4d) — archive or retire the 7 V1_SEED MUZA drafts depending on Tom's MUZA recipe state.
4. **LOW:** review the 14 zero-link real seed suppliers (1f) — leave alone unless deprecating any.
5. **DOCUMENTATION:** update baselines in any seed-checking tooling: planning_policy 5 → 15 (Gate 5 keys are now part of canonical baseline).

## Raw counts — summary

| Table             | Baseline | Current | Delta | Suspect (test) | Notes                                       |
|-------------------|---------:|--------:|------:|---------------:|---------------------------------------------|
| suppliers         | 43       | 104     | +61   | ~58            | rest = 3 alias-id duplicates                |
| components        | 145      | 213     | +68   | 26 by name; 29 orphan (superset)        | includes 2 unused MAT-30G seed rows (PKG-CARTON-MAT-30G, PKG-PACK-MAT-30G) |
| bom_head          | 68       | 85      | +17   | 5              | +12 real MUZA from 0087/0088                |
| bom_version       | 68       | 99      | +31   | 5              | +15 DRAFT (review), +6 ARCHIVED real        |
| bom_lines         | 420      | 603     | +183  | 10 (legacy 'BOM'); 5 (on test heads)    | majority of +183 are real MUZA + repair     |
| supplier_items    | 185      | 231     | +46   | ~13            | rest are real seed rows w/o PO yet          |
| planning_policy   | 5        | 15      | +10   | 0              | all 10 new are real Gate 5 keys             |
| items (bonus)     | 68       | 98      | +30   | 23             | +7 real MUZA items                          |
