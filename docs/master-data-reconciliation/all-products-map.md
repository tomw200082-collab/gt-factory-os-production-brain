# All Products — Master Data Reconciliation (Layer 1: Consolidated Mapping)

**Status:** DRAFT — awaiting Tom approval. Read-only artifact. No DB changes proposed.
**Generated:** 2026-05-07
**Cost file source:** `cost of production August 2025.xlsx` (22 sheets)
**Method:** For each sheet, the LATEST date column (leftmost populated date) is used as the reference.
**Framework:** 5-layer reconciliation. This is Layer 1 for all remaining products after Detox (already completed).

---

## Summary Table: Sheet → System Mapping

| Cost File Sheet | System BASE BOM | File Output | System Output | Status |
|---|---|---|---|---|
| ✅ Detox | BOM-BASE-DET-REG | 515L | 515L | **DONE** |
| ✅ Detox SF | BOM-BASE-DET-NS | 385L | 385L | **DONE** |
| American | BOM-BASE-AME-REG | 500L / 492L net | 492L | NEEDS REVIEW — 1 delta |
| Desert | BOM-BASE-DES-REG | 419L (20.07.2025) | 430L | NEEDS REVIEW — 3 deltas + 1 MISSING ingredient |
| Energy | BOM-BASE-ENE-REG | 460L / 453L net | 453L | NEEDS REVIEW — 5 deltas |
| Fresh | BOM-BASE-FRE-REG | 470L | 510L | NEEDS REVIEW — output + 2 deltas |
| Fresh SF | BOM-BASE-FRE-NS | 365L | 372.5L | NEEDS REVIEW — Lime/Lemon puree Q + output |
| Calm | BOM-BASE-CAL-REG | 417L (22.12.2024) | 394L | NEEDS REVIEW — 5 deltas + 1 MISSING ingredient |
| Revive | BOM-BASE-REV-REG | 500L | 521L | NEEDS REVIEW — output + sugar delta |
| Namastea | BOM-BASE-NAM-REG | 480L | 492L | NEEDS REVIEW — clean 2.5% scale only |
| Consciousness | BOM-BASE-CON-REG | 500L | 273L | NEEDS REVIEW — system is ~half-batch |
| Pink Sangria | BOM-BASE-SAN-PIN-REG | 100L | 50L | NEEDS REVIEW — MISSING Fresh tea ingredient |
| White Sangria | BOM-BASE-SAN-WHI-REG | 100L | 50L | NEEDS REVIEW — MISSING Calm tea ingredient |
| Sangria R Elita | BOM-BASE-SAN-RED-ELI-REG | 480L | 471L | NEEDS REVIEW — MISSING Fresh + Namastea |
| Sangria W Elita | BOM-BASE-SAN-WHI-ELI-REG | 500L | 282L | NEEDS REVIEW — clean 56.4% scale, Calm present |
| Sangria NM | BOM-BASE-NM-REG | 475L | 490L | NEEDS REVIEW — MISSING Fresh tea + water delta |
| Cosmo Lychee | BOM-BASE-COS-LYC-REG | 737L | 410L | NEEDS REVIEW — clean 55.5% scale, Fresh ref = null |
| Cocktails (Tropical) | **NONE** | 131L | — | **NOT IN SYSTEM** |
| Cocktails (Jasmin Jazz) | **NONE** | — | — | **NOT IN SYSTEM** |
| Almond Joy (Migd) | **NONE** | 19.8L | — | **NOT IN SYSTEM** |
| Lady Sandy (Migd) | **NONE** | 20L | — | **NOT IN SYSTEM** |
| Friling (Migdaler) | **NONE** | 20.2L | — | **NOT IN SYSTEM** |

**Pattern: 6 products in the cost file have NO BASE BOM in the system.**
**Pattern: 4 sangria/cosmo products are missing GT tea ingredients from their BOMs (structural gap, not a number error).**
**Pattern: 5 products are clean batch-size differences with no per-ingredient recipe delta (Namastea, Cosmo, W Elita, Consciousness, Pink/White Sangria simple).**

---

## Category 1: Products in cost file NOT in system

These sheets exist in the cost file but have no corresponding ITEM or BASE BOM in the system. No DB changes can be made until Tom clarifies scope.

### Cocktails sheet (Tropical + Jasmin Jazz)

The "Cocktails" sheet contains **two separate recipes** side-by-side:

**Tropical** (col A–F):
- Water: 18L
- Lemon water: 10L
- Pineapple puree ODK: 2L
- Passion fruit puree ODK: 3L
- Gin: 30L
- Preservative: 0.2L
- Revive: 34L ← uses Revive tea as ingredient
- Before bottling: 131.2L → 97L in 1L bottles

**Jasmin Jazz** (col H):
- Water: listed (qty in col H not captured in my read)
- Whiskey: listed
- Passion fruit puree ODK: listed
- Preservative: listed
- Consciousness: listed ← uses Consciousness tea as ingredient

Both cocktails use other GT products as ingredients (Revive, Consciousness). No ITEM or BOM exists for these in the system.

**Open Q-COC-1:** Are Tropical and Jasmin Jazz products currently being produced and sold? If yes, do they need system BOMs? If no, should this sheet be ignored?

### Almond Joy (Migd sheet)

Recipe:
- Water: 11.5L
- Arak: 5.2L
- Almond syrup: 3L
- Preservative: 0.02L
- Lemon acid: 0.17L
- Before bottling: 19.8L → 99 × 0.2L bottles

**Open Q-ALM-1:** Is Almond Joy still produced/sold? Does it need a system BOM? What's the ITEM_ID?

### Lady Sandy (Migd sheet)

Recipe:
- Water: 7.2L
- Cranberry juice: 2.5L
- Gin: 2.5L
- Cynar: 3.4L
- Sugar: 4.3 KG
- Preservative: 0.02L
- Lemon acid: 0.2L
- Before bottling: 20L → 100 × 0.2L bottles

**Open Q-LAD-1:** Is Lady Sandy still produced/sold? Does it need a system BOM? What's the ITEM_ID?

### Friling (Migdaler sheet)

Recipe:
- Water: 12.6L
- Rum: 4.2L
- Lychee puree: 1.3 KG
- Passion fruit puree: 1.4 KG
- Elderflower syrup: 0.7L
- Preservative: 0.02L
- Lemon acid: 0.25L
- Before bottling: 20.2L → 101 × 0.2L bottles

**Open Q-FRL-1:** Is Friling still produced/sold? Does it need a system BOM? What's the ITEM_ID?

---

## Category 2: Structural gap — GT tea ingredients missing from Sangria BOMs

The following products USE other GT tea products (Fresh, Calm, Namastea) as input ingredients per the cost file, but the system BOMs do NOT include them. This means the system does not track the consumption of Fresh/Calm/Namastea tea when producing Sangria.

| Product | GT Tea Used | Qty in file | In system BOM? |
|---|---|---|---|
| Pink Sangria | Fresh | 42L per 100L batch | **NO** |
| White Sangria | Calm | 35L per 100L batch | **NO** |
| Sangria R Elita | Fresh + Namastea | 38L + 29L per 480L batch | **NO** |
| Sangria NM | Fresh | 67.5L per 475L batch | **NO** |
| Sangria W Elita | Calm | 75L per 500L batch | present (null cid ref) |
| Cosmo Lychee | Fresh | 140L per 737L batch | present (null cid ref) |

**Open Q-SAN-1 (CRITICAL STRUCTURAL):** Should the GT tea inputs (Fresh, Calm, Namastea) be modeled as BOM line items in the Sangria BASE BOMs?

- **Option A (Full BOM):** Add them as BOM lines with `component_ref_type = 'BASE_BOM'` pointing to the respective BASE BOM. This would make the production chain explicit: when producing Pink Sangria, the system knows Fresh tea is consumed.
- **Option B (Flat cost):** Add them as a `RAW_NAME` component (effectively treating them as a raw-material input at a known cost/liter, not linking to the Fresh tea BOM). Simpler but loses chain traceability.
- **Option C (Out of scope):** Leave as-is. Tea inputs to Sangria are tracked manually or not at all in the BOM.

If **Option A or B** is chosen, all 4 products (Pink Sangria, White Sangria, Sangria R Elita, Sangria NM) need new BOM versions. Sangria W Elita and Cosmo Lychee need the null cid lines resolved.

**Note:** Sangria W Elita currently has a `null` cid line for Calm (42.3L). This line is present but has no component linkage — it would not drive purchase recommendations or consumption tracking. Same for Cosmo Lychee's null Fresh line (77.76L). Even if Option C is chosen for new products, these null lines should be resolved.

---

## Category 3: Clean batch-size scale (no per-ingredient recipe delta)

These products have every ingredient in a fixed ratio vs the file — the system used a different batch size but the recipe (ratios) are identical. The only question is: use file's batch size or keep system's?

### Namastea

File (latest, no date): output **480L**. System: output **492L** (scale factor 492/480 = **+2.5%** — all ingredients uniformly scaled up by 2.5%).

System vs file per ingredient:

| Ingredient | File qty | System qty | Δ | Δ% |
|---|---|---|---|---|
| Cloves | 2.9 KG | 2.972 KG | +0.072 | +2.5% |
| Cinnamon (crushed) | 13.54 KG | 13.879 KG | +0.339 | +2.5% |
| Black pepper | 2.4 KG | 2.46 KG | +0.06 | +2.5% |
| Cardamom (El) | 2.21 KG | 2.265 KG | +0.055 | +2.5% |
| Sugar | 150 KG | 153.75 KG | +3.75 | +2.5% |
| Water | 420 L | 430.5 L | +10.5 | +2.5% |
| Puer tea | 4 KG | 4.1 KG | +0.1 | +2.5% |
| Stabilizer | 0.1 KG | 0.1025 KG | +0.003 | +2.5% |
| Preservative | 0.5 L | 0.5125 L | +0.013 | +2.5% |
| Black tea | 6 KG | 6.15 KG | +0.15 | +2.5% |
| Crushed ginger | 0.95 KG | 0.974 KG | +0.024 | +2.5% |

**Conclusion:** Namastea has ZERO recipe delta. Only batch size differs (480L → 492L, +2.5%).

**Open Q-NAM-1:** Align to file's 480L batch (all absolute quantities drop 2.5%) or keep system's 492L batch? If keep 492L, mark CLEAN and no change needed.

### Cosmo Lychee

File (XX.XX.XX, no date): output **737.3L** (before bottling). System: output **409.5L** (scale factor 409.5/737.3 = **55.5%** — all ingredients uniformly at 55.5% of file).

| Ingredient | File qty | System qty | Δ% |
|---|---|---|---|
| Water | 270 L | 149.96 L | −55.5% |
| Vodka | 253 L | 140.54 L | −55.5% |
| Raspberry syrup | 8 L | 4.443 L | −55.5% |
| Cranberry puree ODK | 8 KG | 4.443 KG | −55.5% |
| Lychee syrup | 45 L | 24.99 L | −55.5% |
| Fresh tea | 140 L | 77.76 L (null cid) | −55.5% |
| Sugar water | 31 L | 17.22 L | −55.5% |
| Preservative | 1 L | 0.556 L | −55.5% |
| Lemon acid | 3 KG | 1.666 KG | −55.5% |

**Conclusion:** Cosmo Lychee has ZERO recipe delta. Only batch size differs (737L → 410L, 55.5% of file). But the Fresh tea reference is a null cid line.

**Open Q-COS-1:** Align to file's 737L batch or keep system's 410L? (If keep 410L, mark CLEAN.)
**Open Q-COS-2:** The Fresh tea line (77.76L) has no component ID. This needs resolution regardless of Q-SAN-1's answer — even if tea inputs are "out of scope" for BOM tracking, the null-cid line is a data quality issue.

### Sangria W Elita

File (no date): output **500L**. System: output **282L** (scale factor 282/500 = **56.4%** — all ingredients uniformly scaled).

| Ingredient | File qty | System qty | Δ% |
|---|---|---|---|
| White wine | 365 L | 205.86 L | −56.6% |
| Martini bianco | 15 L | 8.46 L | −56.4% |
| Vodka | 15 L | 8.46 L | −56.4% |
| Elderflower syrup | 30 L | 16.92 L | −56.4% |
| Calm tea | 75 L | 42.3 L (null cid) | −56.4% |
| Lemon acid | 0.5 KG | 0.282 KG | −56.4% |
| Preservative | — | 0.4 L | in system only |

**Conclusion:** Sangria W Elita is a clean 56.4% scale-down. Zero recipe delta. Calm tea is present but has null cid.

**Open Q-WELI-1:** Align to file's 500L batch or keep system's 282L?
**Open Q-WELI-2:** Resolve null cid for Calm tea line (same as Q-SAN-1 answer).

### Consciousness (half-batch)

File (22.01.2025 most recent): output **505L**. System: output **273L** (scale factor 273/505 = **54.1%** — approximately half-batch, with minor rounding deviations).

File (22.01.2025):
- Water: 400 L
- Jasmine green tea: 24 KG
- Lychee puree: 22 KG
- Lemon puree: 11 KG
- Lemon acid: 1.1 KG
- Sugar: 182.5 KG
- Before bottling: 505L

System (273L):
- Water: 200 L (= 400/2 ✓)
- Jasmine green tea: 12 KG (= 24/2 ✓)
- Lychee puree: 11 KG (= 22/2 ✓)
- Lemon puree: 6 KG (≈ 11/2 = 5.5, **not exact**)
- Lemon acid: 0.6006 KG (≈ 1.1/2 = 0.55, **not exact**)
- Sugar: 87 KG (≈ 182.5/2 = 91.25, **not exact**)
- Output: 273L (≈ 505/2 = 252.5, **not exact**)

So system is roughly half-batch but lemon puree, lemon acid, sugar, and output don't perfectly halve.

**Open Q-CON-1:** Should system adopt the full file recipe (505L batch)? Or keep the half-batch (273L)? If keep half-batch, should the deviating ingredients be corrected to exact halves?

- If adopt full file: output 505L, jasmine 24, lychee 22, lemon puree 11, lemon acid 1.1, sugar 182.5, water 400.
- If keep half-batch corrected: output 252.5L, jasmine 12, lychee 11, lemon puree 5.5, lemon acid 0.55, sugar 91.25, water 200.

**Note on most recent date:** The 04.11.2024 column shows sugar=175 KG for a 500L batch. The 22.01.2025 column shows sugar=182.5 KG for a 505L batch. The 22.01.2025 is most recent → 182.5 KG at 505L.

---

## Category 4: Real recipe deltas (ingredient ratios differ, not just batch size)

### American

File (undated): output **492L** (492 bottles 1L). Before bottling = 500L. System output = **492L** ✓.

| Ingredient | File qty | System qty | Δ | Δ% |
|---|---|---|---|---|
| Water | 420 L | 420 L | 0 | ✓ |
| Black tea | 18.9 KG | 18.9 KG | 0 | ✓ |
| Puer tea | 6.3 KG | 6.3 KG | 0 | ✓ |
| **Sugar** | **160 KG** | **157.44 KG** | **−2.56** | **−1.6%** |
| Lime puree | 8.4 KG | 8.4 KG | 0 | ✓ |
| Lemon puree | 8.4 KG | 8.4 KG | 0 | ✓ |
| Yuzu puree | 1 KG | 1 KG | 0 | ✓ |
| Bergamot puree | 6.3 KG | 6.3 KG | 0 | ✓ |
| Dried Orange | 6 KG | 6 KG | 0 | ✓ |

**Note:** 157.44 = 160 × (492/500) — the system sugar was scaled from 500L → 492L. All other ingredients were NOT scaled (they match the file absolute values for the 500L batch).

**Open Q-AME-1:** Should sugar be corrected to **160 KG** (file absolute value for this batch, consistent with all other ingredients), or stay at 157.44 KG?

### Energy

File (10.03.2025, most recent): before bottling = **460L**, bottles+jerricans total = **453L**. System output = **453L** ✓.

| Ingredient | File qty | System qty | Δ | Δ% |
|---|---|---|---|---|
| Water | 420 L | 420 L | 0 | ✓ |
| **Green tea** | **25.2 KG** | **25 KG** | **−0.2** | **−0.8%** |
| Menta | 1.7 KG | 1.7 KG | 0 | ✓ |
| Lemon grass | 10.5 KG | 10.328 KG | −0.172 | −1.6% |
| **Nana** | **4.2 KG** | **4.0 KG** | **−0.2** | **−4.8%** |
| **Lemon acid** | **1.4 KG** | **1.5 KG** | **+0.1** | **+7.1%** |
| **Lemon puree** | **13 KG** | **15 KG** | **+2** | **+15.4%** |
| **Sugar** | **170 KG** | **175 KG** | **+5** | **+2.9%** |

**Open Q-ENE-1:** Adopt file values for all 6 ingredients listed above? Or keep some system values?

Note: the Lemon puree delta (+2 KG, +15.4%) and sugar delta (+5 KG, +2.9%) are the largest and most significant.

Note: the file labels this "lemon puree" (not "lime puree"). System correctly has RAW-LEMON-PUREE (not lime). No ambiguity here.

### Fresh (Regular)

File (first col, latest date): before bottling = **470L**. System output = **510L** ← 40L more than file from same inputs.

File (all columns consistently ~470L):
- Water: 400 L
- Karkade (hibiscus): 28 KG
- Lemon acid: 1 KG
- **Lime puree: 11 KG** (note: file says "lime puree")
- Sugar: 175 KG
- Before bottling: 470L

System (510L):
- Water: 400 L ✓
- Hibiscus: 28 KG ✓
- Lemon acid: 1.085 KG (+0.085, +8.5%)
- **Lime puree: 10 KG** (file 11 KG, −1 KG, −9.1%)
- Sugar: 178 KG (file 175, +3 KG, +1.7%)
- Output: **510L vs 470L** ← +40L (8.5% more output from same inputs)

**Open Q-FRE-1:** The file consistently shows 470L output across all date columns. System has 510L. Should system output be corrected to **470L** (consistent with file), with ingredients also adjusted?
**Open Q-FRE-2:** Adopt file ingredient quantities (lime puree 11, lemon acid 1, sugar 175)?

### Fresh SF (No Sugar)

File (21.10.2024, most recent): before bottling = **365L**. System output = **372.5L** (Δ = +7.5L, +2.1%).

| Ingredient | File | System | Δ | Issue |
|---|---|---|---|---|
| Water | 400 L | 400 L | 0 | ✓ |
| Karkade | 28 KG | 28 KG | 0 | ✓ |
| **Puree** | **"Lemon puree" 10 KG** | **RAW-LIME-PUREE 10 KG** | qty=0 | **AMBIGUOUS** |
| Lemon acid | 0.95 KG | 0.95 KG | 0 | ✓ |
| Output | 365L | 372.5L | +7.5L | +2.1% |

File says **"Lemon puree"** for Fresh SF. System has **Lime Puree** (RAW-LIME-PUREE).
For Fresh Regular, the file correctly says "lime puree" and system also has Lime Puree. Only Fresh SF calls it "Lemon puree".

**Open Q-FRN-1 (CRITICAL):** For Fresh SF — is it **Lime Puree** or **Lemon Puree**? Options:
- **Option A:** File is authoritative → swap system RAW-LIME-PUREE → RAW-LEMON-PUREE in Fresh SF BOM.
- **Option B:** File label is inconsistent with Fresh Regular (which says lime) — Fresh SF also uses Lime Puree and file label is sloppy.

**Open Q-FRN-2:** Align output to **365L** (file) from 372.5L?

### Calm (Regular)

File (22.12.2024, most recent — larger batch at 417L): before bottling = **417L**. System output = **394L** (Δ = −23L, −5.5%).

File 22.12.2024:
- Water: 420 L
- Dried apple: 25 KG
- Chamomile: 18 KG
- Lemon puree: 10 KG
- **Lime puree: 4 KG** ← SEPARATE line item, not in system
- Lemon acid: 1.4 KG
- Cloves: 1 KG
- Sugar: 175 KG
- Before bottling: 417L

System (394L):
- Water: **472.8 L** (file 420 L, **+52.8L, +12.6%**)
- Dried apple: **28.13 KG** (file 25 KG, **+3.13, +12.5%**)
- Chamomile: 18 KG ✓
- Lemon puree: **14 KG** (file 10 KG, **+4 KG, +40%**)
- Lime puree: **0** (**MISSING** — file has 4 KG RAW-LIME-PUREE as separate ingredient)
- Lemon acid: **1.631 KG** (file 1.4 KG, **+0.231, +16.5%**)
- Cloves: **1.127 KG** (file 1 KG, **+0.127, +12.7%**)
- Sugar: 175 KG ✓
- Output: 394L (file 417L, **−23L, −5.5%**)

**Open Q-CAL-1:** Adopt file's 22.12.2024 column as the target recipe (417L output)?
**Open Q-CAL-2 (CRITICAL):** File lists **Lime puree (4 KG) as a separate ingredient** alongside Lemon puree (10 KG). System has only Lemon puree (14 KG total, which = 10+4). Is the system combining them into one? Or is Lime puree genuinely absent from production and the 14 KG system value was a deliberate total?
**Open Q-CAL-3:** Water discrepancy: system 472.8L vs file 420L. If we align to file recipe, use 420L?
**Open Q-CAL-4:** Dried apple: system 28.13 vs file 25 KG. Note: 28.13 ≈ 25 × 1.125. Adopt file 25 KG?
**Open Q-CAL-5:** Lemon acid: system 1.631 vs file 1.4 KG. Adopt file 1.4 KG?

**Note on Calm NS:** No "Calm SF/NS" sheet in cost file. BOM-BASE-CAL-NS (same structure as REG but without sugar) is system-defined only. No file comparison possible — leave as-is unless Tom has data.

### Revive

File (18.01.2025, most recent): before bottling = **500L**. System output = **521L** (Δ = +21L, +4.2%).

| Ingredient | File qty | System qty | Δ | Δ% |
|---|---|---|---|---|
| Water | 420 L | 420 L | 0 | ✓ |
| Sencha tea | 27 KG | 27 KG | 0 | ✓ |
| Passion fruit puree | 22 KG | 22 KG | 0 | ✓ |
| Lemon puree | 11 KG | 11 KG | 0 | ✓ |
| Lemon acid | 1 KG | 1 KG | 0 | ✓ |
| **Sugar** | **187.5 KG** | **185 KG** | **−2.5** | **−1.3%** |
| **Output** | **500L** | **521L** | **+21** | **+4.2%** |

All ingredients match except sugar (−2.5 KG) and the batch output (+21L).

**Open Q-REV-1:** Adopt **187.5 KG** sugar (file) vs keep 185 KG (system)?
**Open Q-REV-2:** Output 521L in system vs 500L in file. Should system be corrected to 500L?

### Desert (Regular)

Three date columns in file. **Most recent = 20.07.2025** (col D). Before bottling = **419L**. System output = **430L**.

File 20.07.2025:
- Water: 420 L
- Louisa: 5.75 KG
- Nana: 6.3 KG
- Lemon grass: 10.5 KG
- Melisa: 2.1 KG
- Oregano: 2.1 KG
- White zuta: 2.1 KG
- Marva: 2.1 KG
- Menta: 2.1 KG
- Sugar: 111.67 KG
- Lime puree: 8 KG
- Lemon puree: 10 KG
- Lemon acid: 1.25 KG
- Before bottling: 419L

System (430L):
- Lemongrass: 10.5 KG ✓
- Lime puree: 8 KG ✓
- Lemon puree: 10 KG ✓
- **Passion fruit puree: 22 KG** ← **NOT IN FILE at all!**
- Lemon acid: 1.25 KG ✓
- **Sugar: 114.81 KG** (file 111.67, +3.14, +2.8%)
- **Water: 470 L** (file 420L, **+50L, +11.9%**)
- Louisa: 5.75 KG ✓
- Nana: 6.3 KG ✓
- Menta: 2.1 KG ✓
- Melisa: 2.1 KG ✓
- Oregano: 2.1 KG ✓
- Zuta: 2.1 KG ✓
- Marva: 2.1 KG ✓

**Note:** The 08.05.2025 column (older) shows water = **470L** and sugar = 165 KG — matching the system's water (470L). The 20.07.2025 (most recent) has reduced water to 420L and sugar to 111.67 KG. The system was aligned to the May 2025 values, not the July 2025 ones.

**Open Q-DES-1 (CRITICAL):** Is **Passion Fruit Puree (22 KG)** actually used in Desert production? It is NOT in the cost file across any date column. If it's not used, the system BOM is incorrect and this line must be removed.
**Open Q-DES-2:** Should we align to the **20.07.2025 column** (420L water, 111.67 KG sugar, 419L output)? This is the most recent but differs significantly from the May 2025 version (470L water, 165 KG sugar).
**Open Q-DES-3:** If 20.07.2025 is correct: water 420 vs system 470 (−50L), sugar 111.67 vs system 114.81 (−3.14 KG), output 419L vs system 430L.

**Note on Desert NS:** File has no Desert SF sheet. System has BOM-BASE-DES-NS (430L, V4_USER_LOCK) with same herbs/acids/purees as REG but no sugar. If Passion Fruit is confirmed wrong in REG, same question applies to NS.

### Sangria NM (Nonomimi)

File (03.01.2025 / 06.12.2024 — two cols, same quantities): before bottling **475–482L** (varies by run). System output = **490L**.

System includes all file ingredients EXCEPT Fresh tea (67.5L). Water has two rows in file (90.51L + 7.27L = 97.78L total), system has 98L ≈ correct ✓.

| Ingredient | File qty | System qty | Δ | Δ% |
|---|---|---|---|---|
| Wine (red) | 300 L | 300 L | 0 | ✓ |
| OJ concentrate | 25.86 L | 26 L | +0.14 | ✓ (rounding) |
| **Water (total)** | **97.78 L** | **98 L** | +0.22 | ✓ |
| Amaretto | 12.37 L | 12.73 L | +0.36 | +2.9% |
| Cinnamon | 2.55 KG | 2.5 KG | −0.05 | −2.0% |
| Anise | 0.73 KG | 0.73 KG | 0 | ✓ |
| Cardamom | 0.18 KG | 0.18 KG | 0 | ✓ |
| Black pepper | 0.15 KG | 0.15 KG | 0 | ✓ |
| Cloves | 0.18 KG | 0.18 KG | 0 | ✓ |
| Sugar | 14.55 KG | 14.5 KG | −0.05 | ✓ (rounding) |
| Dried orange | 0.34 KG | 0.34 KG | 0 | ✓ |
| Dried lemon | 0.34 KG | 0.34 KG | 0 | ✓ |
| Preservative | 0.5 L | 0.5 L | 0 | ✓ |
| **Fresh tea** | **67.5 L** | **0** | **−67.5 L** | **MISSING** |
| **Output** | **475L** | **490L** | **+15L** | +3.2% |

Amaretto has a +2.9% delta (12.37 → 12.73). All other non-Fresh ingredients are essentially identical.

**Open Q-NM-1:** Adopt file Amaretto (12.37L) vs system (12.73L)?
**Open Q-NM-2:** This product is also subject to Q-SAN-1 (Fresh tea as BOM line).
**Open Q-NM-3:** Output 490L system vs 475L file. Correct to 475L?

### Sangria R Elita

File (04.01.2025): before bottling = **480L**. System output = **471L**.

| Ingredient | File qty | System qty | Δ | Δ% |
|---|---|---|---|---|
| Wine (red) | 287 L | 287 L | 0 | ✓ |
| OJ concentrate | 25 L | 26 L | +1 | +4% |
| Water | 90 L | 90 L | 0 | ✓ |
| Rum | 16 L | 16 L | 0 | ✓ |
| Sugar | 14 KG | 14 KG | 0 | ✓ |
| Preservative | 0.5 L | 0.5 L | 0 | ✓ |
| **Fresh tea** | **38 L** | **0** | **−38 L** | **MISSING** |
| **Namastea tea** | **29 L** | **0** | **−29 L** | **MISSING** |
| **Output** | **480L** | **471L** | **−9L** | −1.9% |

**Open Q-RED-1:** OJ concentrate: file 25L vs system 26L. Adopt file 25L?
**Open Q-RED-2:** Subject to Q-SAN-1 (Fresh + Namastea as BOM lines).
**Open Q-RED-3:** Output 471L system vs 480L file. Correct to 480L (or wait for Q-SAN-1 resolution)?

### Pink Sangria

File (undated): output **100L**. System output = **50L** (= half of file's wine-only portion).

File: Wine (white) 58L + Fresh tea 42L + Preservative 0.17L + Lemon acid 0.22 KG → 100L before bottling.

System: Wine (white) 29L (= 58/2) + Preservative 0.085L (= 0.17/2) + Lemon acid 0.11 KG (= 0.22/2) → 50L.

The system has exactly half of the wine/preservative/acid. **Fresh tea (42L) is entirely missing.**

**Open Q-PIN-1:** Subject to Q-SAN-1. If Fresh tea is added, system batch should become 100L with all file quantities (wine 58, Fresh 42, preservative 0.17, acid 0.22).

### White Sangria (Regular)

File (undated): output **100L**. System output = **50L**.

File: Wine (white) 65L + Calm tea 35L + Preservative 0.19L + Lemon acid 0.24 KG → 100L.

System: Wine (white) 32.5L + Preservative 0.10L + Lemon acid 0.12 KG → 50L.

Same pattern as Pink Sangria — system has half of wine-only portion, Calm tea (35L) entirely missing.

**Open Q-WHI-1:** Subject to Q-SAN-1. If Calm tea is added, batch becomes 100L.

---

## Consolidated Open Questions for Tom

Below are all open questions, grouped by type. Tom answers these; I then produce per-product diff docs (Layer 2) and migration files (Layer 4).

### STRUCTURAL questions (must answer before any work on affected products)

| Q# | Question | Products affected |
|---|---|---|
| **Q-SAN-1** | Should Fresh/Calm/Namastea teas be modeled as BOM line items when used in Sangria production? (Option A=full BOM link, B=flat component, C=omit) | Pink Sangria, White Sangria, Sangria R Elita, Sangria NM, Sangria W Elita, Cosmo Lychee |
| **Q-COC-1** | Are Tropical and Jasmin Jazz cocktails currently produced/sold? Need system BOMs? | Cocktails sheet |
| **Q-ALM-1** | Is Almond Joy still in production? Need system BOM? | Almond Joy (Migd) |
| **Q-LAD-1** | Is Lady Sandy still in production? Need system BOM? | Lady Sandy (Migd) |
| **Q-FRL-1** | Is Friling still in production? Need system BOM? | Friling (Migdaler) |
| **Q-DES-1** | Is Passion Fruit Puree (22 KG) actually used in Desert production? (File has no trace of it) | Desert REG + Desert NS |

### BATCH SIZE questions (all ingredients scale proportionally — only absolute quantities change)

| Q# | Question | Current → file → decision |
|---|---|---|
| **Q-NAM-1** | Align Namastea to 480L (−2.5% everything) or keep 492L? | 492L → 480L |
| **Q-CON-1** | Adopt full Consciousness recipe (505L, sugar 182.5) or keep half-batch (273L)? If keep, correct deviating ingredients? | 273L → 505L or corrected half |
| **Q-COS-1** | Align Cosmo Lychee to 737L or keep 410L? | 410L → 737L |
| **Q-WELI-1** | Align Sangria W Elita to 500L or keep 282L? | 282L → 500L |
| **Q-REV-2** | Align Revive output to 500L (file) from 521L (system)? | 521L → 500L |
| **Q-FRE-1** | Align Fresh output to 470L (file) from 510L (system)? | 510L → 470L |
| **Q-FRN-2** | Align Fresh SF output to 365L from 372.5L? | 372.5L → 365L |
| **Q-DES-2** | Use 20.07.2025 Desert recipe (420L water, 419L output) or May 2025 version (470L water, 505L output)? | 470L water/430L sys → 420L water/419L |
| **Q-NM-3** | Align NM output to 475L from 490L? | 490L → 475L |
| **Q-RED-3** | Align Red Sangria output to 480L from 471L? (depends on Q-SAN-1) | 471L → 480L |
| **Q-PIN-1** | (Depends on Q-SAN-1) | |
| **Q-WHI-1** | (Depends on Q-SAN-1) | |

### INGREDIENT QUANTITY questions (real recipe deltas)

| Q# | Product | Ingredient | File | System | Adopt file? |
|---|---|---|---|---|---|
| **Q-AME-1** | American | Sugar | 160 KG | 157.44 KG | ? |
| **Q-ENE-1a** | Energy | Lemon puree | 13 KG | 15 KG | ? |
| **Q-ENE-1b** | Energy | Sugar | 170 KG | 175 KG | ? |
| **Q-ENE-1c** | Energy | Lemon acid | 1.4 KG | 1.5 KG | ? |
| **Q-ENE-1d** | Energy | Green tea | 25.2 KG | 25 KG | ? |
| **Q-ENE-1e** | Energy | Nana | 4.2 KG | 4.0 KG | ? |
| **Q-ENE-1f** | Energy | Lemon grass | 10.5 KG | 10.33 KG | ? |
| **Q-FRE-2a** | Fresh REG | Lime puree | 11 KG | 10 KG | ? |
| **Q-FRE-2b** | Fresh REG | Lemon acid | 1 KG | 1.085 KG | ? |
| **Q-FRE-2c** | Fresh REG | Sugar | 175 KG | 178 KG | ? |
| **Q-REV-1** | Revive | Sugar | 187.5 KG | 185 KG | ? |
| **Q-CAL-3** | Calm REG | Water | 420 L | 472.8 L | ? |
| **Q-CAL-4** | Calm REG | Dried apple | 25 KG | 28.13 KG | ? |
| **Q-CAL-5** | Calm REG | Lemon acid | 1.4 KG | 1.631 KG | ? |
| **Q-NM-1** | Sangria NM | Amaretto | 12.37 L | 12.73 L | ? |
| **Q-RED-1** | Sangria R Elita | OJ concentrate | 25 L | 26 L | ? |

### LIME/LEMON PUREE ambiguity

| Q# | Product | File says | System has | Decision |
|---|---|---|---|---|
| **Q-FRN-1** | Fresh SF | "Lemon puree" | RAW-LIME-PUREE | Which is correct? |
| **Q-CAL-2** | Calm REG | Lemon puree 10 KG + Lime puree 4 KG separately | RAW-LEMON-PUREE 14 KG only (no lime) | Are they separate ingredients in production, or combined? |

---

## Products with NO CHANGES NEEDED (if Tom confirms)

These can be marked CLEAN once Tom confirms the batch-size convention is intentional:
- **Detox REG + NS:** ✅ DONE
- **Sangria W Elita:** Clean 56.4% scale (but needs Q-SAN-1 + null cid resolution)

---

## What NOT changing regardless of decisions above

- All **PACK BOMs** (4×Detox, 2×American, etc.) — structurally correct, file has no pack-BOM spec data
- **BOM-BASE-CAL-NS** — no file equivalent, system-defined, leave as-is
- **BOM-BASE-DES-NS** — no file equivalent, leave as-is unless Desert Passion Fruit question (Q-DES-1) changes it
- **MARGARITA, ARAK PASSION FRUIT, MATCHA, MUZA** families — not in cost file, out of scope

---

*Generated 2026-05-07. No DB changes until Tom answers the questions above.*
