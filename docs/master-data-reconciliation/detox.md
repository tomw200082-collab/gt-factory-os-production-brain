# Detox — Master Data Reconciliation (Layer 1: Mapping Document)

**Status:** DRAFT — awaiting Tom's review. Read-only artifact. No DB changes proposed yet.
**Generated:** 2026-05-07
**Cost file source:** `cost of production August 2025.xlsx` → sheets `Detox` and `Detox SF`
**Latest cost-file column used:** `29.07.2025` (most recent)
**System state:** snapshot from Supabase production at time of generation.

---

## 1. SKUs in scope (4 items, 6 BOM heads)

| ITEM_ID | Name | Pack | Sweetness | PRIMARY_BOM (PACK) | BASE_BOM |
|---|---|---|---|---|---|
| `FG-DET-1L` | DETOX 1L | 1L | REGULAR | `BOM-PACK-DET-1L` | `BOM-BASE-DET-REG` (500L output) |
| `FG-DET-500ML` | DETOX 0.5L | 0.5L | REGULAR | `BOM-PACK-DET-500ML` | `BOM-BASE-DET-REG` |
| `FG-DET-1L-NS` | DETOX 1L NO SUGAR | 1L | NO_SUGAR | `BOM-PACK-DET-1L-NS` | `BOM-BASE-DET-NS` (210L output) |
| `FG-DET-500ML-NS` | DETOX 0.5L NO SUGAR | 0.5L | NO_SUGAR | `BOM-PACK-DET-500ML-NS` | `BOM-BASE-DET-NS` |

---

## 2. BASE-DET-REG (Regular) — file vs system

**Cost file** (`Detox` sheet, 29.07.2025): batch yield = 515L "before bottling"
**System** (`BOM-BASE-DET-REG`): batch yield = 500L

Normalized **per liter of yield**:

| Cost-file ingredient | File qty | File qty/L | System component_id | System name | System qty | System qty/L | Δ (system − file) | Confidence |
|---|---|---|---|---|---|---|---|---|
| Water | 420 | 0.8155 L/L | `RAW-WATER` | Water | 420 L | 0.8400 L/L | **+3.0%** | EXACT |
| Green tea | 11.5 | 0.02233 KG/L | `RAW-GREEN-TEA` | Green tea | 11.5 KG | 0.02300 KG/L | **+3.0%** | EXACT |
| Louisa | 12.5 | 0.02427 KG/L | `RAW-LUISA` | Lemon Verbena (Luiza) | 12.5 KG | 0.02500 KG/L | **+3.0%** | EXACT |
| Nana | 3.5 | 0.006796 KG/L | `RAW-NANA` | Spearmint (Nana) | 3.5 KG | 0.00700 KG/L | **+3.0%** | EXACT |
| Lemon acid | 1.5 | 0.002913 KG/L | `RAW-LEMON-ACID` | Lemon acid | **1.55 KG** | 0.00310 KG/L | **+6.4%** | EXACT |
| Sugar | 180 | 0.34951 KG/L | `RAW-SUGAR` | Sugar | **190 KG** | 0.38000 KG/L | **+8.7%** | EXACT |
| **Lime puree** | 15 | 0.02913 KG/L | **— (not in BOM!)** | — | — | — | **MISSING in system** | **AMBIGUOUS — see Q1** |
| — (file shows none) | — | — | `RAW-LEMON-PUREE` | Lemon Puree (Ristretto) | **15 KG** | 0.03000 KG/L | **EXTRA in system** | **AMBIGUOUS — see Q1** |
| single length 100 micron | 1 | — | `PKG-FILTER-100MICRON` | Single Length Filter 100 micron | — | — | not in BOM | **see Q2** |
| double length 200 micron | 1 | — | `PKG-FILTER-200MICRON` | Double Length Filter 200 micron | — | — | not in BOM | **see Q2** |

**Δ explanation:** the +3% on most lines is exactly the 515 vs 500 batch-size convention difference (file yields 515L from 420L water; system declares yield as 500L). When normalized to "per liter of water input," all those +3% deltas vanish — they are a **measurement convention** not a recipe difference.

**Real recipe deltas after correcting for batch convention:**
- **Sugar:** file 180 KG / 420 L water = 0.4286 KG/L water; system 190 KG / 420 L water = 0.4524 KG/L water → **+5.6% real difference**
- **Lemon acid:** file 1.5 / 420 = 0.00357 KG/L water; system 1.55 / 420 = 0.00369 → **+3.3% real difference**
- **Lemon vs Lime Puree:** **product-identity mismatch**, not a quantity delta

Sugar trend in cost file:
| Column | Date | Sugar KG | Δ vs prior |
|---|---|---|---|
| 11.12.2024 | 185 | — |
| 18.12.2024 | 187 | +1.1% |
| 12.01.2025 | 187.5 | +0.3% |
| 28.01.2025 | 187.5 | 0% |
| 1.03.2025 | 180 | **−4.0%** |
| 29.07.2025 | 180 | 0% |

System (190 KG) is **higher than every historical column** in the file. The recipe in the system was either (a) imported from a pre-Dec-2024 source, or (b) deliberately re-specified higher. Tom's call.

---

## 3. BASE-DET-NS (No Sugar) — file vs system

**Cost file** (`Detox SF` sheet, 10.12.2024 column): batch yield = 385L "before bottling," 375L "Total"
**System** (`BOM-BASE-DET-NS`): batch yield = 210L

These are **different batch sizes** (file ~385L, system 210L). Normalized **per liter of water input**:

| Cost-file ingredient | File qty | File qty/L water | System component_id | System name | System qty | System qty/L water | Δ |
|---|---|---|---|---|---|---|---|
| Water | 420 | 1.0 | `RAW-WATER` | Water | **210** | 1.0 | batch size differs |
| Green tea | 11.5 | 0.02738 | `RAW-GREEN-TEA` | Green tea | 6 | 0.02857 | **+4.3%** |
| Louisa | 12.5 | 0.02976 | `RAW-LUISA` | Lemon Verbena (Luiza) | 6 | 0.02857 | **−4.0%** |
| Nana | 3.5 | 0.00833 | `RAW-NANA` | Spearmint (Nana) | 1.75 | 0.00833 | **0%** |
| Lemon acid | 1.5 | 0.00357 | `RAW-LEMON-ACID` | Lemon acid | 0.75 | 0.00357 | **0%** |
| Sugar | 0 | 0 | — (not present) | — | — | — | NS confirmed |
| **Lime puree** | 15 | 0.03571 | **— (not in BOM!)** | — | — | — | **MISSING in system — Q1** |
| — | — | — | `RAW-LEMON-PUREE` | Lemon Puree (Ristretto) | **7.5** | 0.03571 | **EXTRA in system — Q1** |
| single length 100 micron | 1 | — | `PKG-FILTER-100MICRON` | — | — | — | **see Q2** |
| double length 200 micron | 1 | — | `PKG-FILTER-200MICRON` | — | — | — | **see Q2** |

System NS recipe = **roughly half the file's NS recipe**, but not perfectly halved (green tea +4.3%, louisa −4.0%). Probably a hand-tuned half-batch that diverged.

---

## 4. PACK BOMs (4 heads) — file vs system

The cost file `Detox` sheet does not break out per-pack-size packaging the way the system does. File has these packaging entries:
- `1 l bottles | 6.05 (price) | (cost varies historically)`
- `1 l bottles new | 4.2769 | (newer SKU, used 29.07.2025 col)`
- `0.5 l bottles | 3.6617 | (rarely populated)`
- `Carton per bottle | 0.41 | (per-bottle carton allocation)`

System PACK BOM lines (all 4 PACK heads identical structure, label only changes):

| line_no | system component | qty | UOM | file equivalent? |
|---|---|---|---|---|
| 1 | (BASE_BOM ref) | 1 L (1L) or 0.5 L (500ML) | L | — (not a packaging line) |
| 2 | `PKG-BOTTLE-1L` or `PKG-BOTTLE-500ML` | 1 | UNIT | ≈ "1 l bottles new" or "0.5 l bottles" |
| 3 | `PKG-CAP-BLACK-METAL-28` | 1 | UNIT | NOT priced in file directly |
| 4 | `PKG-LABEL-DET-{size}-{NS?}` | 1 | UNIT | NOT priced in file |
| 5 | `PKG-CARTON-{1L\|500ML}` | 0.16667 (=1/6) | UNIT | "Carton per bottle 0.41" — file uses cost basis, system uses qty (1 carton holds 6 bottles) |

**PACK BOM observations:**
- System uses qty 0.16667 = 1/6 cartons per bottle. File assumes price 0.41 ILS per bottle for carton allocation. If 1/6 carton has cost 0.41, full carton cost = 2.46 ILS. (Reasonable for cardboard.)
- System has no separate filter consumption line — filters are NOT in BASE BOM either. **Probable conclusion:** filters are tracked as PROCESS_SUPPLY consumables, not standard BOM components. **Q2 confirms.**
- System carton qty is hard-coded 0.16667 — that's 1/6 = 6 bottles per carton, regardless of bottle size. Confirmed by both `PKG-CARTON-1L` and `PKG-CARTON-500ML`. **Reasonable.**

**Possible PACK gaps:**
- File "1 l bottles new" entry (cost 4.2769) suggests there's a NEW 1L bottle SKU. System has `PKG-BOTTLE-1L` "New Dark Glass Bottle (1000ml)". Single component — **this matches.** The file's older "1 l bottles" (6.05) probably refers to a deprecated/legacy bottle. **OK.**

**No structural change required to PACK BOMs.** Numbers in file are cost-tracking historical, not recipe specs. But validate Tom agrees.

---

## 5. Component name → ID mapping (confidence)

| File text | System component_id | Confidence | Notes |
|---|---|---|---|
| Water | `RAW-WATER` | EXACT | trivial |
| Green tea | `RAW-GREEN-TEA` | EXACT | unambiguous |
| Louisa | `RAW-LUISA` | EXACT | "Lemon Verbena (Luiza)" — Hebrew "לואיזה" |
| Nana | `RAW-NANA` | EXACT | "Spearmint (Nana)" — Hebrew "נענע" |
| Lemon acid | `RAW-LEMON-ACID` | EXACT | unambiguous |
| Sugar | `RAW-SUGAR` | EXACT | unambiguous |
| **Lime puree** | `RAW-LIME-PUREE` ("Lime Puree (Ristretto)") **OR** `RAW-LEMON-PUREE` ("Lemon Puree (Ristretto)") | **AMBIGUOUS** | **CRITICAL — Q1**. Both exist as separate components. System BOM uses LEMON puree, file says LIME puree. |
| single length 100 micron | `PKG-FILTER-100MICRON` | EXACT (if used in BOM at all) | not currently in BOM — Q2 |
| double length 200 micron | `PKG-FILTER-200MICRON` | EXACT (if used in BOM at all) | not currently in BOM — Q2 |
| 1 l bottles new | `PKG-BOTTLE-1L` | EXACT | "New Dark Glass Bottle (1000ml)" |
| 0.5 l bottles | `PKG-BOTTLE-500ML` | EXACT | "Dark Glass Bottle (500ml)" |
| (no entry) | `PKG-CAP-BLACK-METAL-28` | n/a | exists in system, not in file directly |
| (no entry) | `PKG-LABEL-DET-{size}{-NS?}` | n/a | exists in system, not in file directly |
| Carton per bottle | `PKG-CARTON-1L` / `PKG-CARTON-500ML` | EXACT (allocation 1/6 = 0.16667) | matches |

---

## 6. Open questions for Tom (BLOCK Layer 2 until answered)

### Q1 — **CRITICAL** — Lime Puree vs Lemon Puree

**Cost file says:** "Lime puree" 15 KG (REG) / 15 KG (NS).
**System has:** `RAW-LEMON-PUREE` ("Lemon Puree (Ristretto)") 15 KG (REG) / 7.5 KG (NS).
**Both `RAW-LIME-PUREE` and `RAW-LEMON-PUREE` exist as distinct components in the system.**

What's actually used in production?

- **Option A:** File is authoritative → system BOM is wrong → swap `RAW-LEMON-PUREE` → `RAW-LIME-PUREE` in BASE-DET-REG and BASE-DET-NS.
- **Option B:** System is correct → file label is sloppy ("Lime" used loosely for "Lemon") → no change needed; consider correcting cost-file copy in next refresh.
- **Option C:** Either has been used historically → which is the current production reality? (Tom needs to ask production team.)

### Q2 — Filters in BASE BOM?

Cost file lists **single length 100 micron** (1 unit) and **double length 200 micron** (1 unit) as line items in the Detox recipe. Components `PKG-FILTER-100MICRON` and `PKG-FILTER-200MICRON` exist in the system but are NOT lines in any DETOX BASE BOM.

- **Option A:** Filters ARE consumed per BASE batch → add as BOM lines (qty 1 per batch).
- **Option B:** Filters are PROCESS_SUPPLY consumables, tracked outside BOM → leave system as-is.
- **Option C:** Filters are reusable / multi-batch → not BOM material, not consumable.

### Q3 — Sugar discrepancy (REG)

File 29.07.2025: **180 KG** sugar / 515L yield.
System: **190 KG** sugar / 500L yield.
File trend has been **trending DOWN** (185 → 180). System has 190 — higher than ANY historical file column.

- **Option A:** System is the "old" recipe, file 29.07.2025 is the "current" recipe → align system to file (180 KG / 515L → 0.3495 KG/L for the new BASE volume basis).
- **Option B:** System recipe is intentionally higher than file → no change.

### Q4 — Lemon acid discrepancy (REG)

File: 1.5 KG. System: 1.55 KG. Small (3.3%) but real.
- **Option A:** Adopt file → 1.5 KG.
- **Option B:** Keep system value.

### Q5 — BASE-DET-NS batch size

System BASE-DET-NS output is 210L; file shows 385L "before bottling" / 375L "Total." System ratios (per L water) are NOT exactly half of file ratios (green tea: +4.3%, louisa: −4.0%). The system NS recipe drifted from the file.
- **Option A:** Re-derive system NS as 0.5 × (file values) → uniform half-batch.
- **Option B:** Re-derive system NS as 1.0 × (file values, scale yield to 385L).
- **Option C:** Keep system as-is (it works in production, do not destabilize).

### Q6 — Carton qty methodology

System uses 0.16667 (= 1/6) as fractional carton consumption. File uses cost-allocation methodology ("Carton per bottle 0.41 ILS"). They are different mathematical models for the same physical fact: 6 bottles per carton.
- **Option A:** Confirm system 1/6 is correct (6 bottles per `PKG-CARTON-1L` and `PKG-CARTON-500ML`).
- **Option B:** Different bottle sizes use different cartons-per-pack count.

---

## 7. Provisional change set (LOCKED OFF — requires Q1–Q6 resolution)

**No DB changes are proposed in this document.**

If Tom answers all 6 questions, the resulting plan goes into a separate **Layer 3 diff document** (`docs/master-data-reconciliation/detox.diff.md`) showing exactly which `bom_version` rows get archived, which new ones get inserted, and which lines change. Tom approves that diff before any migration is written.

---

## 8. Risks identified, not yet addressed

- **In-flight production:** changing an ACTIVE BOM version archives it. Any open Production Actual form pinned to the old version will fail with `STALE_BOM_VERSION` 409 on submit. Need to coordinate with production timing.
- **Cost rollup downstream:** changing `final_component_qty` ripples into purchase recommendations and cost rollups. We will compute before/after cost rollup as Layer 5 verification.
- **Forecast assumptions:** demand forecasts are SKU-level and unaffected, but if recipe yields change (515 → 500 or vice versa), batch sizing for production planning may shift. Layer 5 also verifies.
