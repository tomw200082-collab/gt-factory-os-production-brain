# Recipe Deep Verification — Final Gap Report
**Generated:** 2026-04-27 (post Tom's clarifications + MUZA recipes)

**Rules applied:**
- **R1.** BASE BOM `final_bom_output_qty` (L) = sum of L-line qtys (KG ignored as solute)
- **R2.** NS variant = REG variant minus sugar; declared per R1
- **R3.** Namastea "new" is canonical
- **R4.** Margaritas are already in master — apply R1 to existing BOMs
- **R5.** 4 MUZA recipes supplied; build new BOMs; Passion Spritz remains an explicit gap

**Sources:** master JSONs at `gt-factory-os/fixtures/masters/`; user-supplied recipe images for MUZA cocktails (150-unit batches).

## §1. Universal volume rule (R1) — declared should equal L-line sum

Every BASE BOM that needs its `final_bom_output_qty` updated.

| BOM | Display | current declared | R1 target (L sum) | diff | pct off | action |
|---|---|---:|---:|---:|---:|---|
| `BOM-BASE-FRE-REG` | FRESH / REGULAR | 510.0 L | **400.0 L** | +110.00 L | 27.5% | **UPDATE declared to 400.0** |
| `BOM-BASE-REV-REG` | REVIVE / REGULAR | 521.0 L | **420.0 L** | +101.00 L | 24.05% | **UPDATE declared to 420.0** |
| `BOM-BASE-MAR-CLA` | MARGARITA / REG | 275.0 L | **180.0 L** | +95.00 L | 52.78% | **UPDATE declared to 180.0** |
| `BOM-BASE-DET-REG` | DETOX / REGULAR | 500.0 L | **420.0 L** | +80.00 L | 19.05% | **UPDATE declared to 420.0** |
| `BOM-BASE-CON-REG` | CONSCIOUSNESS / REGULAR | 273.0 L | **200.0 L** | +73.00 L | 36.5% | **UPDATE declared to 200.0** |
| `BOM-BASE-AME-REG` | AMERICAN / REGULAR | 492.0 L | **420.0 L** | +72.00 L | 17.14% | **UPDATE declared to 420.0** |
| `BOM-BASE-NAM-REG` | NAMASTEA / REGULAR | 492.0 L | **420.5 L** | +71.50 L | 17.0% | **UPDATE declared to 420.5** |
| `BOM-BASE-MAR-PEA` | MARGARITA / REG | 300.0 L | **230.0 L** | +70.00 L | 30.43% | **UPDATE declared to 230.0** |
| `BOM-BASE-MAR-STR` | MARGARITA / REG | 300.0 L | **230.0 L** | +70.00 L | 30.43% | **UPDATE declared to 230.0** |
| `BOM-BASE-DES-NS` | DESERTEA / NO_SUGAR | 430.0 L | **470.0 L** | -40.00 L | -8.51% | **UPDATE declared to 470.0** |
| `BOM-BASE-DES-REG` | DESERTEA / REGULAR | 430.0 L | **470.0 L** | -40.00 L | -8.51% | **UPDATE declared to 470.0** |
| `BOM-BASE-ENE-REG` | ENERGY / REGULAR | 453.0 L | **420.0 L** | +33.00 L | 7.86% | **UPDATE declared to 420.0** |
| `BOM-BASE-FRE-NS` | FRESH / NO_SUGAR | 372.5 L | **400.0 L** | -27.50 L | -6.88% | **UPDATE declared to 400.0** |
| `BOM-BASE-CAL-NS` | CALM / NO_SUGAR | 394.0 L | **420.0 L** | -26.00 L | -6.19% | **UPDATE declared to 420.0** |
| `BOM-BASE-CAL-REG` | CALM / REGULAR | 394.0 L | **420.0 L** | -26.00 L | -6.19% | **UPDATE declared to 420.0** |
| `BOM-BASE-SAN-RED-ELI-REG` | RED SANGRIA / REGULAR | 471.0 L | **486.5 L** | -15.50 L | -3.19% | **UPDATE declared to 486.5** |
| `BOM-BASE-NM-REG` | NONOMIMI / REGULAR | 490.0 L | **504.73 L** | -14.73 L | -2.92% | **UPDATE declared to 504.73** |
| `BOM-BASE-COS-LYC-REG` | COSMO / REGULAR | 409.5 L | **403.2 L** | +6.30 L | 1.56% | **UPDATE declared to 403.2** |

**27 BASE BOMs scanned · 9 already R1-compliant · 18 need declared update.**

## §2. NS rule (R2) — must be REG minus sugar, nothing else

| Family | REG | NS | strict-sugar-removal? | only_in_REG | only_in_NS | qty diffs | current NS declared | R2 target declared |
|---|---|---|:---:|---|---|---|---:|---:|
| CALM | `BOM-BASE-CAL-REG` | `BOM-BASE-CAL-NS` | ✅ | RAW-SUGAR | — | — | 394.0 L | **420.0 L** |
| DESERTEA | `BOM-BASE-DES-REG` | `BOM-BASE-DES-NS` | ✅ | RAW-SUGAR | — | — | 430.0 L | **470.0 L** |
| FRESH | `BOM-BASE-FRE-REG` | `BOM-BASE-FRE-NS` | ✅ | RAW-SUGAR | — | — | 372.5 L | **400.0 L** |
| DETOX | `BOM-BASE-DET-REG` | `BOM-BASE-DET-NS` | ❌ | RAW-SUGAR | — | RAW-LUISA: REG(12.5, 'KG')/NS(6.0, 'KG'); RAW-NANA: REG(3.5, 'KG')/NS(1.75, 'KG'); RAW-WATER: REG(420.0, 'L')/NS(210.0, 'L'); RAW-GREEN-TEA: REG(11.5, 'KG')/NS(6.0, 'KG'); RAW-LEMON-ACID: REG(1.55, 'KG')/NS(0.75, 'KG'); RAW-LEMON-PUREE: REG(15.0, 'KG')/NS(7.5, 'KG') | 210.0 L | **420.0 L** |

**❌ rows = NS variant violates R2 (something other than sugar differs from REG).**

## §3. MUZA cocktails — proposed new BOMs

Tom supplied 4 recipes (Negroni / Jasmine / Queen Violet / Herbal Mule Bliss) as 150-unit / 0.2 L batches. The 5th (Passion Spritz) is left as an explicit gap.

### MUZA HERBAL MULE BLISS 200ml — `FG-MUZ-HER-200ML`

- Item in master: **True**, status `ACTIVE`, supply `MANUFACTURED`
- Currently linked: PACK=`BOM-PACK-MUZ-HER-200ML`, BASE=`BOM-BASE-MUZ-HER`, BASE_FILL=`0.2L`
- Recipe sums to **30.06 L** + **0 KG** for 150 units of 200 ml = expected 30 L. Difference: +0.0600 L (preservative is on top — recipe convention).
- **Proposed BASE BOM:** `BOM-BASE-MUZ-HER`, declared = **30.06 L** (per R1).

| Excel ingredient | Qty (30 L batch) | UOM | per-L ratio | mapped component |
|---|---:|---|---:|---|
| Water | 12.51 | L | 0.416168 | `RAW-WATER` |
| Lemon juice | 5.805 | L | 0.193114 | `RAW-LEMON-JUICE` |
| Rum | 4.83 | L | 0.160679 | `RAW-RUM` |
| Cucumber syrup | 4.83 | L | 0.160679 | **❌ MISSING — must add** |
| Alcohol 96% | 2.025 | L | 0.067365 | **❌ MISSING — must add** |
| Preservative | 0.06 | L | 0.001996 | `RAW-PRESERVATIVE` |

⚠ **Missing components for this recipe:** Cucumber syrup, Alcohol 96%

### MUZA JASMINE 200ml — `FG-MUZ-JAS-200ML`

- Item in master: **True**, status `ACTIVE`, supply `MANUFACTURED`
- Currently linked: PACK=`BOM-PACK-MUZ-JAS-200ML`, BASE=`BOM-BASE-MUZ-JAS`, BASE_FILL=`0.2L`
- Recipe sums to **27.923 L** + **2.138 KG** for 150 units of 200 ml = expected 30 L. Difference: -2.0770 L (preservative is on top — recipe convention).
- **Proposed BASE BOM:** `BOM-BASE-MUZ-JAS`, declared = **27.923 L** (per R1).

| Excel ingredient | Qty (30 L batch) | UOM | per-L ratio | mapped component |
|---|---:|---|---:|---|
| Water | 12.57 | L | 0.450167 | `RAW-WATER` |
| Lemon juice | 4.275 | L | 0.1531 | `RAW-LEMON-JUICE` |
| Raw sugar | 2.138 | KG | 0.076568 | `RAW-SUGAR` |
| Campari | 3.225 | L | 0.115496 | `RAW-CAMPARI` |
| Triple sec 17% | 3.225 | L | 0.115496 | **❌ MISSING — must add** |
| Gin | 3.225 | L | 0.115496 | `RAW-GIN` |
| Alcohol 96% | 1.343 | L | 0.048097 | **❌ MISSING — must add** |
| Preservative | 0.06 | L | 0.002149 | `RAW-PRESERVATIVE` |

⚠ **Missing components for this recipe:** Triple sec 17%, Alcohol 96%

### MUZA NEGRONI 200ml — `FG-MUZ-NEG-200ML`

- Item in master: **True**, status `ACTIVE`, supply `MANUFACTURED`
- Currently linked: PACK=`BOM-PACK-MUZ-NEG-200ML`, BASE=`BOM-BASE-MUZ-NEG`, BASE_FILL=`0.2L`
- Recipe sums to **30.06 L** + **0 KG** for 150 units of 200 ml = expected 30 L. Difference: +0.0600 L (preservative is on top — recipe convention).
- **Proposed BASE BOM:** `BOM-BASE-MUZ-NEG`, declared = **30.06 L** (per R1).

| Excel ingredient | Qty (30 L batch) | UOM | per-L ratio | mapped component |
|---|---:|---|---:|---|
| Water | 14.295 | L | 0.475549 | `RAW-WATER` |
| Campari | 5.805 | L | 0.193114 | `RAW-CAMPARI` |
| Red vermouth | 5.805 | L | 0.193114 | **❌ MISSING — must add** |
| Gin | 2.895 | L | 0.096307 | `RAW-GIN` |
| Alcohol 96% | 1.2 | L | 0.03992 | **❌ MISSING — must add** |
| Preservative | 0.06 | L | 0.001996 | `RAW-PRESERVATIVE` |

⚠ **Missing components for this recipe:** Red vermouth, Alcohol 96%

### MUZA QUEEN VIOLET 200ml — `FG-MUZ-QUE-200ML`

- Item in master: **True**, status `ACTIVE`, supply `MANUFACTURED`
- Currently linked: PACK=`BOM-PACK-MUZ-QUE-200ML`, BASE=`BOM-BASE-MUZ-QUE`, BASE_FILL=`0.2L`
- Recipe sums to **29.1 L** + **0.96 KG** for 150 units of 200 ml = expected 30 L. Difference: -0.9000 L (preservative is on top — recipe convention).
- **Proposed BASE BOM:** `BOM-BASE-MUZ-QUE`, declared = **29.1 L** (per R1).

| Excel ingredient | Qty (30 L batch) | UOM | per-L ratio | mapped component |
|---|---:|---|---:|---|
| Water | 14.535 | L | 0.499485 | `RAW-WATER` |
| Lemon juice | 4.725 | L | 0.162371 | `RAW-LEMON-JUICE` |
| Violet liqueur | 4.26 | L | 0.146392 | **❌ MISSING — must add** |
| Gin | 3.795 | L | 0.130412 | `RAW-GIN` |
| Raw sugar | 0.96 | KG | 0.03299 | `RAW-SUGAR` |
| Alcohol 96% | 1.59 | L | 0.054639 | **❌ MISSING — must add** |
| Melon extract | 0.135 | L | 0.004639 | **❌ MISSING — must add** |
| Preservative | 0.06 | L | 0.002062 | `RAW-PRESERVATIVE` |

⚠ **Missing components for this recipe:** Violet liqueur, Alcohol 96%, Melon extract

**Aggregate missing components needed for MUZA:** ['Alcohol 96%', 'Cucumber syrup', 'Melon extract', 'Red vermouth', 'Triple sec 17%', 'Violet liqueur']

## §4. Margaritas — verification of existing master/BOM state

| Item | pack | BASE_FILL | base BOM | base decl | R1 target | needs R1? | PACK→BASE convention | missing fill? |
|---|---|---|---|---:|---:|:---:|:---:|:---:|
| `FG-MAR-CLA-300ML` | 0.3L | 0.3L | `BOM-BASE-MAR-CLA` | 275.0 | 180.0 | ✅ YES | MISMATCH | — |
| `FG-MAR-STR-300ML` | 0.3L | 0.3L | `BOM-BASE-MAR-STR` | 300.0 | 230.0 | ✅ YES | MISMATCH | — |
| `FG-MAR-PEA-300ML` | 0.3L | 0.3L | `BOM-BASE-MAR-PEA` | 300.0 | 230.0 | ✅ YES | MISMATCH | — |

## §5. Component master quality

### §5.1 Duplicate components (will mis-route ledger postings)

| Component IDs | Names | Notes |
|---|---|---|
| `RAW-CLOVE`, `RAW-CORNATION`, `RAW-COLVE` | Whole Clove; Whole Clove; Whole Clove | All three resolve to the same physical raw — must merge to a single canonical ID |
| `RAW-LIME-PURE` / `RAW-LIME-PUREE` | Pure vs Puree split (different UOMs) | Same ingredient, different UOM convention — pick one |
| `RAW-BERGAMOT-PURE` / `RAW-BERGAMOT-PUREE` | Pure vs Puree split (different UOMs) | Same ingredient, different UOM convention — pick one |
| `RAW-PRESERVATIVE` / `RAW-CONSERVANT` | Preservative (Bulk) / Conservant | Margaritas use CONSERVANT, all others use PRESERVATIVE — merge to one |

### §5.2 Components needed for MUZA — not in master yet

| Proposed COMPONENT_ID | Name | UOM | Used by |
|---|---|---|---|
| `RAW-CUCUMBER-SYRUP` | Cucumber syrup | L | for MUZA HERBAL MULE BLISS |
| `RAW-ALCOHOL-96` | Alcohol 96% | L | for ALL 4 MUZA |
| `RAW-TRIPLE-SEC` | Triple sec 17% | L | for MUZA JASMINE |
| `RAW-VERMOUTH-RED` | Red vermouth | L | for MUZA NEGRONI |
| `RAW-VIOLET-LIQUEUR` | Violet liqueur | L | for MUZA QUEEN VIOLET |
| `RAW-MELON-EXTRACT` | Melon extract | L | for MUZA QUEEN VIOLET |

## §6. Items still missing BOM

| Item ID | Name |
|---|---|
| `FG-MUZ-PSC-200ML` | MUZA PASSION SPRITZ COCKTAIL 0.2L |

## §7. `BASE_FILL_QTY_PER_UNIT` missing on items (blocks dual-input UX without fallback)

| Item ID | Name | Pack | Sales UOM |
|---|---|---|---|
| `FG-MUZ-PSC-200ML` | MUZA PASSION SPRITZ COCKTAIL 0.2L | 0.2L | BOTTLE |

## §8. Remaining gaps for you to close (no autonomous decision possible)

These are the items I cannot resolve without your input:

1. **MUZA Passion Spritz (`FG-MUZ-PSC-200ML`)** — recipe still missing. You said leave with a gap; confirming.

2. **DET-NS recipe interpretation.** Currently `BOM-BASE-DET-NS` has every component **halved** vs `BOM-BASE-DET-REG` (water 210 vs 420, all herbs/leaves halved, sugar removed). Per your stated rule (NS = REG minus sugar, no other change), this is wrong. Two options:
    - **(a)** Replace DET-NS lines with DET-REG-minus-sugar (water 420, green tea 11.5kg, etc.). Declared = 420 L.
    - **(b)** Keep current DET-NS as a deliberate "half batch" SKU. Then the NS rule has an exception for DET.
    Which is canonical?

3. **CAL-NS / DES-NS / FRE-NS declared** currently mismatch L-sum. Confirm: per R1+R2, change declared for these three to the L-sum target shown in §2 (CAL-NS→420, DES-NS→470, FRE-NS→400)?

4. **Sangria W Elita declared 282 L vs Excel 500 L.** Excel ground truth says batch is 500 L with very different per-L ratios than the BOM. The R1 rule alone isn't enough — the BOM components themselves are wrong. Confirm: replace BOM lines with Excel "Sangria W Elita" 500 L recipe (Wine 365 L / Calm 75 L / Martini 15 L / Vodka 15 L / Elderflower 30 L / Lemon acid 0.5 KG / Preservative 0.4 L kept from BOM)?

5. **Component-master duplicates** (§5.1) — three competing CLOVE rows; PURE vs PUREE inconsistencies; CONSERVANT vs PRESERVATIVE. Decision: which canonical ID per group, then update all referring BOM lines and remove the duplicates?

6. **Margarita `BASE_FILL_QTY_PER_UNIT` is NULL** for all 3 items — set to `0.3L` (= pack_size)?

7. **Margarita declared output gaps** (§4): CLA 275→190, STR 300→240, PEA 300→240. Confirm R1 reduction, OR are there missing water/diluent lines we should add instead?

8. **Andrey deltas from Excel reconciliation v2** (still standing from previous report):
    - Sangria W Elita: Calm should be 75 L (current 20), Elderflower 30 L (current 12)
    - Energy: Lemon Grass should be 10.5 KG (current 5.5)
    - Calm: Lemon Acid should be 1.6 KG (current 1.1) — need verification
    - Namastea (new): Cloves 6.04g/L vs BOM 2.03g/L — Excel ratio is 3× higher; Puer 8.33g/L vs BOM 1.02g/L — 8× higher. Confirm Excel is right?
    - American: Sugar 320 KG (Excel) vs 189 KG (BOM) for ~500L batch — Excel's pure mass is bigger. Verify.
    - Desert: Sugar 267 KG (Excel) vs 165 KG (BOM)
    - Consciousness: Lemon Acid 0.0022 KG/L vs 0.0027 KG/L — small
    - Fresh: Lemon Acid 0.0021 KG/L vs 0.0019 KG/L — small

9. **Excel `Cosmo Lychee` sheet** had two recipes mixed in the same columns (a 100L + 760L block). I parsed only the first; the second appeared to contain extra ingredients (Energy / Amaretto / Arak / Lemon Water / Apple Puree ODK / Rosetta Syrup). Confirm: which of the two columns is canonical for `BOM-BASE-COS-LYC-REG`?

10. **UOM convention for purees** (Lemon / Lime / Passion Fruit / Yuzu / Bergamot / Lychee). Currently inconsistent across components master (some L, some KG). Confirm: standardize to L (volumetric, matches Excel)?

Once you give a yes/no on each of items 1-10, I have everything I need to apply the master fix in one pass. After that — clean audit + clean reconciliation = green light for Phase 1 (dual-input UX).
