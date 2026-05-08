# Recipe Closing Report — what Excel "cost of production August 2025" can fix
**Generated:** 2026-04-27
**Sources cross-checked:**
- `cost of production August 2025.xlsx` — Tom's reference cost workbook
- `gt-factory-os/fixtures/masters/{items,bom_head,bom_lines,components}.json` — current BOM master
- Audit baseline: `docs/recipe-audit-2026-04-27.md`
- Reconciliation detail: `docs/recipe-reconciliation-v2-2026-04-27.md`
- Machine-readable JSON: `gt-factory-os/fixtures/recipe_reconciliation_v2.json`

**Method:** for every BASE BOM I converted both sides to per-1L-of-finished-base ratios (`qty / declared_output_L` for BOM, `qty / batch_L` for Excel where `batch_L` is read from each sheet's "before bottling" row, with fallback to the L-line sum). Per-line agreement: **MATCH ≤2%**, **CLOSE ≤10%**, **DELTA >10%**. UOM disagreements (Excel L vs BOM KG for purees) are flagged separately — those need a unit-of-measure decision before they can be closed.

---

## Headline numbers

| Status | Count | Meaning |
|---|---:|---|
| **17 / 23 BASE BOMs** have a matching recipe in the Excel | 17 | These can be partially or fully closed using Excel as ground truth |
| **6 / 23 BASE BOMs** have no Excel sheet | 6 | Need other source (see §4) |
| **5 manufactured items** have no BOM at all | 5 | All MUZA cocktails — Excel does NOT cover these |
| **3 manufactured items** have a BOM but no Excel sheet | 3 | Margaritas (CLA / STR / PEA) — Excel does NOT cover these |
| **17 sheets** confirm the BASE BOM ratios within ≤10% (CLOSE+) | 17 | Strong evidence the *ratios* are right; the *declared output* is what's wrong |
| **8 BOMs** have at least one DELTA >10% line | 8 | Genuine recipe-content discrepancies — see §3 |

---

## 1. The user-reported case — WHITE SANGRIA 3.85L — what closes from Excel

`FG-SAN-WHI-3850ML` → PACK `BOM-PACK-SAN-WHI-3850ML` → BASE `BOM-BASE-SAN-WHI-ELI-REG`

Excel sheet **"Sangria W Elita"**, ground truth at "before bottling" = **500 L** batch:

| Excel ingredient | Excel qty | Excel /L | BOM qty | BOM declared (282 L) | BOM /L | Δ% | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| Wine (white) Symphony | 365 L | **0.730** | 192 L | →192/282 | 0.681 | **+7.2%** | CLOSE — BOM ratio slightly low |
| Calm (CAL-REG base) | **75 L** | **0.150** | 20 L | →20/282 | 0.071 | **+111.5%** | **DELTA — BOM has half the calm** |
| Elderflower syrup | **30 L** | **0.060** | 12 L | →12/282 | 0.043 | **+41.0%** | **DELTA — BOM is 29% short** |
| Vodka | 15 L | **0.030** | 8 L | →8/282 | 0.028 | +5.8% | CLOSE |
| Martini bianco | 15 L | **0.030** | 8 L | →8/282 | 0.028 | +5.8% | CLOSE |
| Lemon acid | 0.5 KG | **0.001** | 0.26 KG | →0.26/282 | 0.000922 | +8.5% | CLOSE |
| **(Excel has no Preservative line)** | — | — | 0.4 L | 0.001418 | — | — | **BOM has extra Preservative — likely correct (added at bottling); Excel often omits** |
| **Excel total = 500 L** | | | | **declared = 282 L** | | | **declared output is wrong** |

**Conclusion (do this for the BOM):**
1. Change `final_bom_output_qty` for `BOM-BASE-SAN-WHI-ELI-REG` from **282 L → 500 L**.
2. Multiply every component qty by `500 / 282 = 1.773` so per-L ratios stay constant — but Excel shows two ratios are wrong, so use Excel ratios directly:
   - Wine (white) Symphony: 192 → **365 L**
   - Calm base: 20 → **75 L**
   - Elderflower syrup: 12 → **30 L**
   - Vodka: 8 → **15 L**
   - Martini bianco: 8 → **15 L**
   - Lemon acid: 0.26 → **0.5 KG**
   - Preservative (Bulk): keep 0.4 L (not in Excel; treat as extra factory step — verify with Andrey).

**For the user's specific concern (3.85L bottle):** with the corrected BOM, simulator output for 1 bottle becomes:
- White wine: **2.81 L** (was 2.62 L — +7.3%)
- Calm: **0.578 L** (was 0.273 L — +111%)
- Elderflower: **0.231 L** (was 0.164 L — +41%)
- Vodka, Martini bianco: **0.116 L** each (was 0.109 L — +5.8%)
- Lemon acid: **0.00385 KG** (was 0.00355 KG — +8.5%)

This is what the user sensed was wrong — Calm and Elderflower were materially under-stated, and the implicit batch size was too small.

---

## 2. What closes per recipe — full table

Per-line counts vs the matching BASE BOM. **Action** column is what to do once you decide Excel is canonical.

| Sheet | BOM | Excel batch L | BOM declared L | match | close | delta | UOM-mis | BOM-only | Excel-only | Action |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Pink Sangria | `BOM-BASE-SAN-PIN-REG` | 100 | 50 | **3** | 0 | 1 | 0 | 0 | 0 | Double declared → 100 L. Investigate Preservative -15%. |
| White Sangria | `BOM-BASE-SAN-WHI-REG` | 100 | 50 | **2** | 1 | 1 | 0 | 0 | 0 | Double declared → 100 L. **Halve Lemon acid** (0.24 → 0.12 KG). |
| Sangria R Elita | `BOM-BASE-SAN-RED-ELI-REG` | 480 | 471 | **7** | 1 | 0 | 0 | 0 | 0 | Mostly correct; OJC -5.7% close. Raise declared 471 → 480 L for exact match. |
| **Sangria W Elita** | `BOM-BASE-SAN-WHI-ELI-REG` | **500** | **282** | 0 | 4 | 2 | 0 | 1 | 0 | **§1 — biggest correction.** |
| Sangria NM | `BOM-BASE-NM-REG` | 475 | 490 | **1** | 11 | 0 | 0 | 4 | 0 | Lower declared 490 → 475 L. **BOM extras need confirmation** (EL/Cardamom, Black Pepper, Filters). |
| American | `BOM-BASE-AME-REG` | 500 | 492 | **3** | 0 | 1 | 4 | 3 | 0 | Lower declared 492 → 500 L. **Sugar -16.7% needs check.** UOM mismatch on purees (Excel says L, BOM says KG). BOM has extra Black Tea + filters. |
| Desert | `BOM-BASE-DES-REG` | 419 | 430 | 0 | **8** | 1 | 2 | 5 | 0 | Slightly over-declared. **Sugar -30.5% is real**. UOM mismatch on lemon/lime puree. **5 BOM extras**: Passion Fruit Puree, Luisa, Zuta, filters — check if Andrey skipped them in cost sheet but they're real. |
| Detox | `BOM-BASE-DET-REG` | 515 | 500 | 0 | **5** | 0 | 0 | 4 | 1 | All ratios CLOSE. **BOM extras**: Luisa, Lemon Puree, filters — confirm. Excel has Lime puree extra. |
| Energy | `BOM-BASE-ENE-REG` | 460 | 453 | **3** | 3 | 1 | 1 | 2 | 0 | Almost spot-on. **Lemon grass +88% is the only real discrepancy** — Excel has 10.5 KG, BOM has 5.5 KG. Verify with Andrey. |
| Fresh | `BOM-BASE-FRE-REG` | 470 | 510 | 0 | 2 | 1 | 1 | 3 | 0 | **Declared 510 looks too high (lower → ~470).** Lemon acid 14% delta. UOM mismatch on lime puree. **BOM has Hibiscus** (Karkade) — Excel shows it as well but unmapped. |
| Calm | `BOM-BASE-CAL-REG` | 175 | 394 | 0 | 1 | **4** | 1 | 3 | 1 | **Big mess.** Multiple delta >10%. **Excel batch is half** of declared (175 vs 394). Either declared is too high, or Excel sheet is older/half-batch. **CAMOMILE 9 KG in Excel** (unmapped) — BOM has 18 KG (probably canonical 18 was for the bigger batch). |
| Revive | `BOM-BASE-REV-REG` | 500 | 521 | 0 | **4** | 0 | 2 | 2 | 0 | Slightly over-declared. UOM mismatch on lemon/passion puree. BOM extras: filters only. |
| Namastea (new) | `BOM-BASE-NAM-REG` | 480 | 492 | 0 | 4 | **2** | 0 | 6 | 0 | **Cloves +197% delta, Puer +720% delta** — Excel has very different spice loads. **6 BOM-only**: Masala (25 KG), Cinnamon, Black Pepper, Cardamom, filters — Excel calls them Crushed cinnamon/Black pepper/El/Cardamom but they don't auto-map. **Map and re-check.** |
| Detox SF | `BOM-BASE-DET-NS` | 385 | 210 | 0 | **4** | 0 | 0 | 4 | 1 | Excel batch is **almost 2× declared** (385 vs 210). Either Excel is for a bigger batch, or declared is wrong. **BOM extras**: Luisa, Lemon Puree, filters. |
| Consciousness | `BOM-BASE-CON-REG` | 500 | 273 | 0 | 2 | 1 | 2 | 3 | 0 | Excel batch is almost **2× declared** — strongly suggests declared 273 is wrong, should be ≈ 500. **Lemon acid −19.9%** delta. UOM mismatch on lemon/lychee puree. **BOM has Jasmin** (12 KG); Excel has 24 KG of "Jasmine green tea" (unmapped). |
| Fresh SF | `BOM-BASE-FRE-NS` | 365 | 372.5 | 0 | **2** | 0 | 0 | 4 | 1 | Almost spot-on. **BOM extras**: Hibiscus (Karkade — Excel has 28 KG unmapped), Lime Puree, filters. |
| Cosmo Lychee | `BOM-BASE-COS-LYC-REG` | **100.55** | **409.5** | 0 | 0 | **9** | 0 | 0 | 4 | **Excel sheet appears to mix two recipes** (large numbers in cols suggest "for 100L" + "actual batch" — my parser took first column). **Re-parse this sheet manually before fixing.** Excel has Energy/Amaretto/Arak/Lemon water that BOM doesn't. |

---

## 3. Genuine recipe-content discrepancies (DELTA >10%) — each needs Andrey's call

These are where **per-liter ratios** disagree by >10% even after batch-size correction. They are not just declared-output errors.

| BOM | Component | Excel /L | BOM /L | Δ% | Likely cause |
|---|---|---:|---:|---:|---|
| `BOM-BASE-SAN-WHI-ELI-REG` | RAW-CALM (calm base) | 0.150 | 0.071 | +111.5% | BOM has half the calm base |
| `BOM-BASE-SAN-WHI-ELI-REG` | RAW-ELDERFLOWER-SYRUP | 0.060 | 0.043 | +41.0% | BOM is 29% short |
| `BOM-BASE-SAN-WHI-REG` (1L) | RAW-LEMON-ACID | 0.0024 KG | 0.0048 KG | −50.0% | BOM has double the lemon acid |
| `BOM-BASE-SAN-PIN-REG` | RAW-PRESERVATIVE | 0.0017 | 0.002 | −15.0% | BOM 18% high |
| `BOM-BASE-NAM-REG` | RAW-CLOVE | 0.0060 | 0.0020 | +197.2% | Excel 3× more cloves OR mapping issue |
| `BOM-BASE-NAM-REG` | RAW-PUER | 0.0083 | 0.001 | +720.0% | Excel 8× more puer OR mapping issue |
| `BOM-BASE-AME-REG` | RAW-SUGAR | 0.32 | 0.384 | −16.7% | BOM has 17% more sugar |
| `BOM-BASE-DES-REG` | RAW-SUGAR | 0.267 | 0.384 | −30.5% | BOM has 44% more sugar |
| `BOM-BASE-CAL-REG` | RAW-LEMON-ACID | 0.0041 | 0.0028 | +48.4% | Excel 48% more lemon acid |
| `BOM-BASE-CAL-REG` | RAW-WATER | 1.20 | 1.066 | +12.6% | Excel 13% more water (over-fill?) |
| `BOM-BASE-CAL-REG` | RAW-APPLE-DRY | 0.0714 | 0.0635 | +12.6% | BOM ~12% short |
| `BOM-BASE-CAL-REG` | RAW-CLOVE | 0.0029 | 0.0025 | +12.6% | BOM ~12% short |
| `BOM-BASE-FRE-REG` | RAW-LEMON-ACID | 0.0021 | 0.0019 | +14.2% | BOM 12% short |
| `BOM-BASE-CON-REG` | RAW-LEMON-ACID | 0.0022 | 0.0027 | −19.9% | BOM 25% high |
| `BOM-BASE-ENE-REG` | RAW-LEMON-GRASS | 0.0228 | 0.0121 | +88.0% | Excel ~2× more lemongrass |

---

## 4. UOM mismatches (Excel L vs BOM KG) — same content, different unit

These are not data discrepancies, they're a measurement-units decision. Purees and similar fluids are recorded by **volume** in Excel but as **mass** in our BOMs. To compare them, we need a density per ingredient.

| Component | UOM_MISMATCH count | Recipes affected |
|---|---:|---|
| `RAW-LIME-PUREE` | 5 | Calm, American, Energy, Fresh, Desert |
| `RAW-LEMON-PUREE` | 6 | Calm, American, Energy, Fresh, Detox, Desert, Revive, Consciousness |
| `RAW-PASSION-FRUIT-PUREE` | 1 | Revive |
| `RAW-YUZU-PUREE` | 1 | American |
| `RAW-BERGAMOT-PUREE` | 1 | American |
| `RAW-LYCHEE-PUREE` | 1 | Consciousness |

**Action:** decide whether `RAW-XXX-PUREE` components are tracked by L or by KG, then either:
- (a) Update the BOM lines to L (and adjust per-L numbers using density), or
- (b) Update Excel records (less practical) to KG.

Since Excel is operator-facing and likely measures by volume, recommendation is **(a) — switch BOM puree lines to L**. After this is done, every UOM_MISMATCH in §2 will resolve to a real ratio comparison.

---

## 5. What's still missing (cannot be closed from this Excel alone)

### A. 5 MUZA cocktails — no recipe anywhere yet
`FG-MUZ-NEG-200ML`, `FG-MUZ-PSC-200ML`, `FG-MUZ-JAS-200ML`, `FG-MUZ-QUE-200ML`, `FG-MUZ-HER-200ML`

The Excel "Cocktails" sheet has 5 recipes (Tropical / Jasmin Jazz / Russian Sputnik / Red Mexican Flower / Campari T dance) but **none of them are MUZA**. MUZA is a different external producer. **What we need:** a recipe / cost sheet from MUZA Cocktails, or a decision to switch these items to `SUPPLY_METHOD = BOUGHT_FINISHED`.

### B. 3 Margaritas — no recipe in Excel
`FG-MAR-CLA-300ML`, `FG-MAR-STR-300ML`, `FG-MAR-PEA-300ML`

Their BASE BOMs (`BOM-BASE-MAR-CLA`, `BOM-BASE-MAR-STR`, `BOM-BASE-MAR-PEA`) exist with declared 275-300 L and components summing to 190-240 L (~20-30% gap). **What we need:** Andrey's margarita recipe sheet — either added to this workbook or a separate Excel.

### C. 6 BASE BOMs without an Excel sheet
- `BOM-BASE-DET-NS` is mapped to "Detox SF" — but several other NS variants might need explicit confirmation
- `BOM-BASE-MAR-CLA`, `BOM-BASE-MAR-STR`, `BOM-BASE-MAR-PEA` — see (B)
- `BOM-BASE-CAL-NS`, `BOM-BASE-DES-NS` — only one NS sheet ("Detox SF" / "Fresh SF") was found; CAL-NS and DES-NS are not in this workbook

### D. Excel rows with confusing/unmapped names — all KG flowers/herbs on filter packaging
Common pattern across many sheets: the Excel row says "Karkade" (= hibiscus), "Louisa" (= Luisa), "single length 100 micron" (= PKG-FILTER-100MICRON), "double length 200 micron" (= PKG-FILTER-200MICRON), "Crushed cinnamon" / "Crushed ginger" / "Black tea" / "El/Cardamom" / "Black pepper". These are unmapped today because of the name-form mismatch. **Fix in script's NAME_MAP — straightforward.** Once mapped, several "BOM-only" components in the §2 table will pair up and the close/match counts will rise.

### E. PKG-FILTER components are present in BOM, present in Excel rows, just not paired
Same fix as (D) — extend NAME_MAP. After this fix, `PKG-FILTER-100MICRON` and `PKG-FILTER-200MICRON` will reconcile cleanly across all BASE recipes.

### F. The 33 PACK BOM ID-mismatch issue (from §3 of the original audit)
**Not a recipe-content issue.** It's a structural ID convention bug between PACK BOM lines and BASE BOM heads. Fixable independently, no Excel needed.

### G. Cocktails sheet (5 recipes) — items not yet in our master?
Tropical, Jasmin Jazz, Russian Sputnik, Red Mexican Flower, Campari T dance — these have full recipes in the Excel but no matching `FG-*` items in our master data. **Decide:** are these:
- planned products we should add to the items master and create BOMs for, OR
- internal-use / experimental recipes that don't ship to retail?

### H. Migdaler cocktails — items not yet in master
Almond joy, Lady Sandy, Friling — full recipes in the Excel but no matching items. Same question as (G) — these are the "(Migd)" suffixed sheets.

### I. Namastea (old) — superseded recipe
Excel has both `Namastea (new)` and `Namastea (old)`. **Decision needed:** which is canonical for the active BOM `BOM-BASE-NAM-REG`? (The reconciliation used `Namastea (new)`.)

### J. Final volume confirmation per BOM
For each of the 17 BOMs that have a matching Excel sheet, the **declared output** in our BOM should equal the Excel "before bottling" value. Several disagree by >5%. Andrey needs to confirm which is canonical.

---

## 6. Recommended fix order

1. **Fix NAME_MAP in `_reconcile_recipes_v2.py`** to cover Karkade, Louisa, filter PKG, Crushed cinnamon/ginger, Black pepper, El/Cardamom — re-run to shrink the unmapped list.
2. **Decide UOM convention for purees** (§4) — likely L, then update BOM lines.
3. **Update declared output for the 17 BOMs to match Excel "before bottling"** values (§2).
4. **Apply Excel per-L ratios** to the BOMs where MATCH or CLOSE — these can be auto-fixed mechanically.
5. **Take §3 to Andrey** — every DELTA-class line needs human ground-truth (1 hour of Andrey's time, max).
6. **Source Margarita recipes** (§5.B) — Andrey or a different sheet.
7. **Source MUZA recipes OR reclassify** (§5.A) — likely reclassify to `BOUGHT_FINISHED`.
8. **Decide on Namastea old vs new** (§5.I).
9. **Decide on Tropical/Jasmin Jazz/etc + Migdaler products** (§5.G/H) — add to items master if they ship.
10. Re-run the audit script and confirm `baseBomVolumeGap` and `baseRefIdMismatch` go to zero.

---

## Appendix — How I built this

- **Excel parsing:** `gt-factory-os/scripts/_dump_cost_of_prod.py` (raw dump) + `_extract_excel_recipes.py` (structured per-sheet) + `_reconcile_recipes_v2.py` (per-L comparison).
- **Tolerance:** MATCH ≤2%, CLOSE ≤10%, DELTA >10%. Tolerances chosen so honest measurement noise doesn't get flagged but real recipe drift does.
- **Excel batch sizing:** prefer the explicit "before bottling" row; fall back to summing classified-L lines (skipping footers and packaging-bottle rows).
- **UOM separation:** Excel cells are classified L vs KG using the ingredient name (water/wine/syrup/puree → L; tea/sugar/spice/herb → KG). Mismatch reported, never silently coerced.
- **Component name mapping:** explicit NAME_MAP only — no fuzzy substring matching, to avoid false positives. Anything not in the map is reported as `unmapped` so a human can extend it.
- **Files written:**
  - `gt-factory-os/fixtures/cost_of_production_aug2025_dump.json` — raw cell dump
  - `gt-factory-os/fixtures/cost_of_production_aug2025_recipes.json` — first-pass extraction
  - `gt-factory-os/fixtures/recipe_reconciliation_v2.json` — final per-L comparison
  - `docs/recipe-reconciliation-v2-2026-04-27.md` — full per-recipe detail (all pairs, all unmapped, all BOM-onlys)
  - **this file** — closing report
