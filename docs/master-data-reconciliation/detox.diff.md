# Detox — Layer 2 Diff Document (proposed change set)

**Status:** DRAFT — awaiting Tom approval. No DB changes yet.
**Generated:** 2026-05-07
**Source decisions:** Tom answered Q1–Q6 in `detox.md` Layer 1 review.
**Approach:** Each affected BOM gets a NEW `bom_version` (DRAFT → ACTIVE); old version → ARCHIVED. Single transaction per BOM head.

---

## Decisions locked from Q1–Q6

| Q | Decision |
|---|---|
| Q1 — Lime vs Lemon Puree | **Lime** is correct (file). Swap `RAW-LEMON-PUREE` → `RAW-LIME-PUREE` in both BASE BOMs. |
| Q2 — Filters | Stay PROCESS_SUPPLY. **No BOM change.** |
| Q3 — Sugar (REG) | **180 KG** (was 190 KG). |
| Q4 — Lemon acid (REG) | **1.5 KG** (was 1.55 KG). |
| Q5 — BASE-DET-NS batch | **Adopt file: 385L output** with full file recipe (was 210L half-batch). |
| Q6 — Carton qty | Keep 1/6 (= 0.16667). **No PACK change.** |

Plus implicit: BASE-DET-REG output qty changes from **500L → 515L** to keep file's absolute ingredient values consistent (file's 180 KG sugar yields 515L, not 500L).

---

## Change 1: `BOM-BASE-DET-REG` — new active version

**Head update:** `final_bom_output_qty: 500 → 515` (UOM unchanged: L)

**Lines (after change, 7 total):**

| line_no | component_id | qty | UOM | Δ vs current | Source |
|---|---|---|---|---|---|
| 1 | `RAW-GREEN-TEA` | 11.5 | KG | unchanged | file |
| 2 | `RAW-LUISA` | 12.5 | KG | unchanged | file |
| 3 | `RAW-NANA` | 3.5 | KG | unchanged | file |
| 4 | **`RAW-LIME-PUREE`** | 15 | KG | **component swapped** (was `RAW-LEMON-PUREE`) | Q1 |
| 5 | `RAW-LEMON-ACID` | **1.5** | KG | qty: 1.55 → 1.5 | Q4 |
| 6 | `RAW-SUGAR` | **180** | KG | qty: 190 → 180 | Q3 |
| 7 | `RAW-WATER` | 420 | L | unchanged | file |

**Per-liter sanity check (vs file 29.07.2025, 515L basis):**
- Water 420/515 = 0.8155 L/L (file ✓)
- Green tea 11.5/515 = 0.02233 KG/L (file ✓)
- Sugar 180/515 = 0.34951 KG/L (file ✓)
- Lemon acid 1.5/515 = 0.002913 KG/L (file ✓)
- Lime puree 15/515 = 0.02913 KG/L (file ✓)

**Math: matches file exactly. ✓**

---

## Change 2: `BOM-BASE-DET-NS` — new active version

**Head update:** `final_bom_output_qty: 210 → 385` (UOM unchanged: L)

**Lines (after change, 6 total — no sugar):**

| line_no | component_id | qty | UOM | Δ vs current | Source |
|---|---|---|---|---|---|
| 1 | `RAW-GREEN-TEA` | **11.5** | KG | qty: 6 → 11.5 | Q5 (full recipe) |
| 2 | `RAW-LUISA` | **12.5** | KG | qty: 6 → 12.5 | Q5 |
| 3 | `RAW-NANA` | **3.5** | KG | qty: 1.75 → 3.5 | Q5 |
| 4 | **`RAW-LIME-PUREE`** | **15** | KG | **component swapped** (was `RAW-LEMON-PUREE` 7.5) | Q1 + Q5 |
| 5 | `RAW-LEMON-ACID` | **1.5** | KG | qty: 0.75 → 1.5 | Q5 |
| 6 | `RAW-WATER` | **420** | L | qty: 210 → 420 | Q5 |

**Per-liter sanity check (vs file SF 10.12.2024, 385L basis):**
- Water 420/385 = 1.0909 L/L water-input — wait, file says yield = 385L from 420L water (35L process loss). So water-per-output-liter = 420/385 = 1.0909.
- Green tea 11.5/385 = 0.02987 KG/L
- Lime puree 15/385 = 0.03896 KG/L
- Lemon acid 1.5/385 = 0.003896 KG/L
- Louisa 12.5/385 = 0.03247 KG/L
- Nana 3.5/385 = 0.009091 KG/L

**Math: matches file exactly. ✓**

**Note on water input vs output:** the file says water input is 420L but yield is 385L (10L bottled loss + 25L "before bottling" loss to herbs/process). System BASE BOM has water as a line item (input). Output qty = 385L (yield). This is consistent with how `BASE-DET-REG` is being aligned (water 420 input, 515 output).

---

## Change 3 & 4: PACK BOMs — **NO CHANGE**

`BOM-PACK-DET-1L`, `BOM-PACK-DET-500ML`, `BOM-PACK-DET-1L-NS`, `BOM-PACK-DET-500ML-NS` all stay as-is. Q6 confirmed 1/6 carton qty.

(They will continue pointing to the same `linked_base_bom_head_id` — the BASE head ID didn't change, only its active version changed. No PACK migration needed.)

---

## SQL execution sequence (per BASE head)

For each of `BOM-BASE-DET-REG` and `BOM-BASE-DET-NS`, in a single transaction:

```sql
BEGIN;

-- 1. Insert new bom_version (DRAFT)
INSERT INTO private_core.bom_version (bom_head_id, version_label, status, source_basis, notes)
VALUES ('BOM-BASE-DET-REG', 'V_2026_05_07_FILE_ALIGN', 'DRAFT',
        'COST_FILE_AUG2025_29JUL_COL', 'Aligned to cost-file 29.07.2025 column. Lime puree (Q1), sugar 180 (Q3), lemon acid 1.5 (Q4), output 500→515 (consistency).')
RETURNING bom_version_id;  -- → :new_version_id

-- 2. Update bom_head output qty
UPDATE private_core.bom_head SET final_bom_output_qty = 515 WHERE bom_head_id = 'BOM-BASE-DET-REG';

-- 3. Insert 7 new bom_lines for new version (using :new_version_id)
INSERT INTO private_core.bom_lines (...) VALUES (...);  -- 7 rows

-- 4. ARCHIVE old version (must come BEFORE activating new — partial unique idx)
UPDATE private_core.bom_version
   SET status = 'ARCHIVED', archived_at = now()
 WHERE bom_head_id = 'BOM-BASE-DET-REG' AND status = 'ACTIVE';

-- 5. ACTIVATE new version
UPDATE private_core.bom_version
   SET status = 'ACTIVE', activated_at = now()
 WHERE bom_version_id = :new_version_id;

-- 6. Point bom_head at new active version
UPDATE private_core.bom_head
   SET active_version_id = :new_version_id
 WHERE bom_head_id = 'BOM-BASE-DET-REG';

COMMIT;
```

Same pattern for `BOM-BASE-DET-NS` (output 385, 6 lines).

**Old version stays in DB as ARCHIVED — historical Production Actuals pinned to it remain valid for audit. Reversal possible by re-activating the archived version.**

---

## Operational risks (must surface to Tom before Layer 4)

1. **In-flight Production Actual:** any Production Actual form **opened before** the migration applies and **submitted after** will fail with `STALE_BASE_BOM_VERSION` 409. Need to coordinate timing — best applied during off-hours, or coordinated with the production team to close any open forms first.

2. **RAW-LIME-PUREE on-hand:** the new BASE recipe consumes Lime Puree instead of Lemon Puree. If `RAW-LIME-PUREE` has zero stock in `current_balances`, the next Detox production run will:
   - succeed at form submission (BOM allows negative if planning_policy permits),
   - or emit a stock exception via the Exceptions Inbox,
   - or fail validation depending on policy.
   **Tom must confirm `RAW-LIME-PUREE` is on-hand.** I'll check stock as part of Layer 5 verification.

3. **Sugar reduction (190→180):** purchase recommendations will reduce sugar demand by ~5%. Open POs for sugar based on old recipe might over-order slightly. Cost rollup will drop. Verify in Layer 5.

4. **NS batch size doubling (210→385):** **major change**. Production planning will compute differently — fewer larger batches instead of more smaller ones. Production team / planner must be aware. Verify forecast assumptions don't break.

5. **Excel file (`GT_Master_Data.xlsx`):** out of scope per Tom 2026-05-07 ("המערכת היא מקור האמת ולא האקסל"). No update.

---

## Cost rollup forecast (rough estimate, before Layer 5 actual computation)

Assuming approximate raw prices: Sugar ~3.68 ILS/KG, Lemon acid ~10 ILS/KG, Lime puree ~34.2 ILS/KG, Lemon puree ~ similar to lime, Green tea ~45 ILS/KG, etc.

**BASE-DET-REG (per liter):**
- Old (500L): 190×3.68 + 1.55×10 + 15×~34 (lemon puree) + 11.5×45 + 12.5×75 + 3.5×28 = 699.2 + 15.5 + 510 + 517.5 + 937.5 + 98 = **2777.7 / 500 = 5.555 ILS/L**
- New (515L): 180×3.68 + 1.5×10 + 15×34.2 + 11.5×45 + 12.5×75 + 3.5×28 = 662.4 + 15 + 513 + 517.5 + 937.5 + 98 = **2743.4 / 515 = 5.327 ILS/L**
- **Δ: −4.1% per liter** (lower cost — file has cheaper sugar amount + lime puree similar to lemon)

Layer 5 will compute the real rollup using `private_core.std_cost_per_uom` actuals.

---

## What Tom approves with "yes" to Layer 2

- The two `bom_head` output qty changes (500→515, 210→385).
- The two new `bom_version` rows (DRAFT → ACTIVE) replacing existing ones.
- 13 line changes total (7 lines REG + 6 lines NS) with the exact qtys and component IDs above.
- The execution sequence (transaction ordering).
- Acknowledging operational risks 1–4.

If Tom approves, I write the migration file (Layer 4: `0157_realign_detox_bom_to_cost_file.sql`), submit for review **before** applying, then apply, then run Layer 5 verification.
