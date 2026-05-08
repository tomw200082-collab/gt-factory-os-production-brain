# Production Simulation — Recipe Discrepancy Audit
**Generated:** 2026-04-27
**Source data:** `gt-factory-os/fixtures/masters/{items,bom_head,bom_lines}.json`
**Audit script:** `gt-factory-os/scripts/_audit_recipes.mjs`
**Full machine-readable report:** `gt-factory-os/fixtures/recipe_audit_report.json`

---

## TL;DR

You found one symptom (White Sangria 3.85L liters wrong). The audit shows the
problem is **systemic across 16 BASE BOMs**, not a single bad recipe. There is
also a **separate, structural ID-mismatch** issue affecting 33 items that
breaks the simulator's auto-resolution path — and 5 finished MUZA cocktails
have no recipe linked at all.

| Category | Count | Severity |
|---|---|---|
| **BASE BOM declared output ≠ sum of component lines** | 16 / 23 | HIGH — every per-unit qty in simulation is wrong by the gap % |
| **PACK BOM line points at BASE head id but BASE head's parent_ref_id is different** | 33 / 41 items | HIGH — auto-resolution of `base_fill_qty_per_unit` falls back to other paths or fails |
| **Manufactured item has no BOM linked** | 5 (all MUZA cocktails) | HIGH — cannot simulate at all |
| BASE BOM with positive volume gap and **no water line** | 1 (White Sangria Elita) | HIGH — almost certainly missing a water row |
| `BASE_FILL_QTY_PER_UNIT` ≠ `PACK_SIZE` on item | 0 | OK |
| PACK BOM base-mix line qty ≠ item `BASE_FILL_QTY_PER_UNIT` | 0 | OK |
| Base-mix line in non-volume UOM | 0 | OK |

**Items audited:** 50 manufactured/repack
**BASE BOMs audited:** 23 active
**PACK BOMs audited:** 41 active

---

## 1. The user-reported case: WHITE SANGRIA 3.85L

**Item:** `FG-SAN-WHI-3850ML`  ·  **PACK BOM:** `BOM-PACK-SAN-WHI-3850ML`
**BASE BOM:** `BOM-BASE-SAN-WHI-ELI-REG` ("WHITE SANGRIA ELITA BASE MIX")

The BASE BOM declares it produces **282 L** per batch. Its 7 component lines
sum to only **240.4 L**:

| # | Component | Qty | UOM | Notes |
|---|---|---:|---|---|
| L01 | BOM-BASE-CAL-REG (Calm base mix) | 20 | L | nested base |
| L02 | RAW-WINE-WHITE (White wine) | 192 | L |  |
| L03 | RAW-LEMON-ACID (Lemon acid) | 0.26 | KG | non-volume |
| L04 | RAW-PRESERVATIVE | 0.4 | L |  |
| L05 | RAW-ELDERFLOWER-SYRUP (ODK Elderflower) | 12 | L |  |
| L06 | RAW-VODKA | 8 | L |  |
| L07 | RAW-MARTINI-BIANCO | 8 | L |  |
| | **Sum of liquid (L) lines** | **240.4** | **L** | (KG ignored) |
| | **Declared batch output** | **282** | **L** | (locked by Andrey, per `owner_notes`) |
| | **Gap** | **+41.6** | **L** | **14.75% of batch** |

**No water line is present**, even though the head's `owner_notes` says the
282 L figure is the "Direct Andrey recipe result, locked". The 41.6 L gap is
almost certainly a missing `RAW-WATER` line of ~41.6 L (or whatever Andrey
adds — possibly more wine, more vodka, etc.).

**What the simulator computes today (1 unit @ 3.85 L):**
- White wine: 192 / 282 × 3.85 = **2.621 L** per unit
- Calm base: 20 / 282 × 3.85 = **0.273 L** per unit
- Vodka: 8 / 282 × 3.85 = **0.109 L** per unit
- Martini Bianco: 8 / 282 × 3.85 = **0.109 L** per unit
- Elderflower Syrup: 12 / 282 × 3.85 = **0.164 L** per unit
- Preservative: 0.4 / 282 × 3.85 = **0.0055 L** per unit
- Lemon acid: 0.26 / 282 × 3.85 = **0.00355 KG** per unit
- (Water — silently zero, but the recipe actually consumes some)

**Why the operator sees a wrong liter quantity:** every visible liquid line
is scaled against 282 L, but the actual base batch only contains 240.4 L of
declared liquids. Two possible truths:

- **(A)** 282 L is correct and a water line is missing from the BOM. Fix: add
  a `RAW-WATER` line of ~41.6 L.
- **(B)** The component lines are complete and 282 L is wrong. Fix: change
  `final_bom_output_qty` to 240.4 L (which, importantly, would scale every
  per-unit qty UP by 282 / 240.4 = **17.3%** — wine becomes 3.074 L per
  3.85 L bottle, which exceeds the bottle volume and is physically
  impossible). **(A) is the only credible fix.**

---

## 2. ALL 16 BASE BOMs WHERE DECLARED OUTPUT ≠ COMPONENT SUM

Tolerance: 0.5% or 0.5 L, whichever is larger. KG components ignored
(treating as solute, not volume contributor).

| BOM head | Display | Declared (L) | Sum of L lines | Gap (L) | Gap % | Has water line? | Direction |
|---|---|---:|---:|---:|---:|:---:|---|
| `BOM-BASE-FRE-REG` | FRESH / REGULAR | 510 | 400 | **+110** | **+21.6%** | yes | declared > components |
| `BOM-BASE-REV-REG` | REVIVE / REGULAR | 521 | 420 | **+101** | **+19.4%** | yes | declared > components |
| `BOM-BASE-DET-REG` | DETOX / REGULAR | 500 | 420 | **+80** | **+16.0%** | yes | declared > components |
| `BOM-BASE-CON-REG` | CONSCIOUSNESS / REG | 273 | 200 | **+73** | **+26.7%** | yes | declared > components |
| `BOM-BASE-AME-REG` | AMERICAN / REGULAR | 492 | 420 | **+72** | **+14.6%** | yes | declared > components |
| `BOM-BASE-NAM-REG` | NAMASTEA / REGULAR | 492 | 420.5 | **+71.5** | **+14.5%** | yes | declared > components |
| `BOM-BASE-SAN-WHI-ELI-REG` | WHITE SANGRIA / REG | 282 | 240.4 | **+41.6** | **+14.8%** | **NO** | **declared > components, no water** |
| `BOM-BASE-ENE-REG` | ENERGY / REGULAR | 453 | 420 | +33 | +7.3% | yes | declared > components |
| `BOM-BASE-COS-LYC-REG` | COSMO / REGULAR | 409.5 | 403.2 | +6.3 | +1.5% | yes | declared > components |
| `BOM-BASE-SAN-RED-ELI-REG` | RED SANGRIA / REG | 471 | 486.5 | −15.5 | −3.3% | yes | components > declared |
| `BOM-BASE-NM-REG` | NONOMIMI / REGULAR | 490 | 504.73 | −14.73 | −3.0% | yes | components > declared |
| `BOM-BASE-CAL-NS` | CALM / NO_SUGAR | 394 | 420 | **−26** | **−6.6%** | yes | components > declared |
| `BOM-BASE-CAL-REG` | CALM / REGULAR | 394 | 420 | **−26** | **−6.6%** | yes | components > declared |
| `BOM-BASE-FRE-NS` | FRESH / NO_SUGAR | 372.5 | 400 | **−27.5** | **−7.4%** | yes | components > declared |
| `BOM-BASE-DES-NS` | DESERTEA / NO_SUGAR | 430 | 470 | **−40** | **−9.3%** | yes | components > declared |
| `BOM-BASE-DES-REG` | DESERTEA / REGULAR | 430 | 470 | **−40** | **−9.3%** | yes | components > declared |

### What "declared > components" means
The BOM says the batch makes (e.g.) 510 L of FRESH but only 400 L of
ingredients are listed. The simulator divides each line by 510, so per-unit
quantities are **understated by `gap_pct`**. The operator will **mix
short** by that percentage.

### What "components > declared" means
The BOM says the batch makes (e.g.) 394 L of CALM but its component lines
already sum to 420 L. Either the declared output is too low (most likely
add ~26 L of water line wasn't tracked, or a measured loss/evaporation
factor was already baked in) or one of the component qtys is wrong. The
simulator divides each line by 394, so per-unit quantities are
**overstated by `gap_pct`**. The operator will **over-pour** by that
percentage.

### Three BOMs are within tolerance and look healthy
- `BOM-BASE-DET-NS` (DETOX NS): declared 210 L, components 210 L exact ✓
- `BOM-BASE-MAR-CLA`, `BOM-BASE-MAR-STR`, `BOM-BASE-MAR-PEA` — see §3.

### Margaritas — large declared/sum gaps but `BASE_FILL_QTY_PER_UNIT = null`
| BOM head | Display | Declared (L) | Sum of L | Gap | Item field |
|---|---|---:|---:|---:|---|
| `BOM-BASE-MAR-CLA` | MARGARITA CLASSIC | 275 | 190 | +85 (30.9%) | item `BASE_FILL_QTY_PER_UNIT` missing |
| `BOM-BASE-MAR-STR` | MARGARITA STRAWBERRY | 300 | 240 | +60 (20.0%) | item `BASE_FILL_QTY_PER_UNIT` missing |
| `BOM-BASE-MAR-PEA` | MARGARITA PEAR | 300 | 240 | +60 (20.0%) | item `BASE_FILL_QTY_PER_UNIT` missing |

These didn't make the audit's "BASE BOM volume gap" list because of how the
audit groups them, but they show the same pattern AND they're missing the
item-level fill qty. *These need explicit values for `BASE_FILL_QTY_PER_UNIT`
or the simulator will fall back to PACK-line resolution only.*

---

## 3. STRUCTURAL ID MISMATCH — 33 items

Every PACK BOM that nests a BASE BOM points at the **BASE head id**
(`final_component_id = "BOM-BASE-SAN-WHI-ELI-REG"`) instead of the BASE
head's **`parent_ref_id`** (`"BASE-SAN-WHI-ELI-REG"`).

The simulator's `derived_from_bom` resolution path (in
`ProductionSimulatorShell.tsx`) does:
```
packLines.find(l => l.component_id === baseHead.parent_ref_id)
```
which silently fails to match because the ids don't agree. The simulator
then falls back to `derived_from_pack_size` or `derived_from_name`. For
items where `BASE_FILL_QTY_PER_UNIT` is set explicitly on the item, this
isn't fatal — but the operator sees the wrong "source" notice ("derived
from pack size" instead of "read from PACK recipe"), and any item where
*all* of these fallbacks fail (e.g., `sales_uom = BOTTLE` + missing pack
size) cannot be simulated at all.

### Affected items (33)
CALM 1L · CALM 0.5L · CONSCIOUSNESS 1L · CONSCIOUSNESS 0.5L ·
COSMO LYCHEE 0.3L · DESERTEA 1L · DESERTEA 0.5L · DESERTEA 0.5L NS ·
DETOX 1L · DETOX 1L NS · DETOX 0.5L · DETOX 0.5L NS · ENERGY 1L ·
ENERGY 0.5L · FRESH 1L · FRESH 1L NS · FRESH 0.5L · FRESH 0.5L NS ·
NAMASTEA 1L · NAMASTEA 0.5L · NONOMIMI SANGRIA 1L · NONOMIMI SANGRIA 3.85L ·
REVIVE 1L · REVIVE 0.5L · PINK SANGRIA 1L · RED SANGRIA ELITA 0.75L ·
WHITE SANGRIA 1L · WHITE SANGRIA ELITA 0.75L · MARGARITA CLASSIC 0.3L ·
MARGARITA STRAWBERRY 0.3L · MARGARITA PEAR 0.3L · RED SANGRIA 3.85L ·
WHITE SANGRIA 3.85L

### Two equivalent fixes (pick one, do everywhere)
- **(A)** Change PACK BOM line `final_component_id` from
  `"BOM-BASE-XXX"` → `"BASE-XXX"` (the parent_ref_id form). Net SQL touch:
  33 PACK BOM line rows.
- **(B)** Change BASE BOM head `parent_ref_id` from `"BASE-XXX"` →
  `"BOM-BASE-XXX"` (the BOM head id form). Net SQL touch: 23 BASE BOM head
  rows. Caveat: 3 margarita BASE heads use a different convention
  (`parent_ref_id = FG-MAR-XXX-300ML`), so the fix isn't uniform.

**(A) is preferred** — it touches more rows but the convention "PACK lines
reference the BASE's `parent_ref_id` (its public-facing "BASE-MIX" id), not
the internal head id" is what the simulator was written against.

---

## 4. ITEMS WITH NO BOMs LINKED (5)

All MUZA cocktails are MANUFACTURED but have neither `PRIMARY_BOM_ID` nor
`BASE_BOM_ID`. They cannot be simulated.

| Item ID | Item name |
|---|---|
| `FG-MUZ-NEG-200ML` | MUZA NEGRONI COCKTAIL 0.2L |
| `FG-MUZ-PSC-200ML` | MUZA PASSION SPRITZ COCKTAIL 0.2L |
| `FG-MUZ-JAS-200ML` | MUZA JASMINE COCKTAIL 0.2L |
| `FG-MUZ-QUE-200ML` | MUZA QUEEN VIOLET COCKTAIL 0.2L |
| `FG-MUZ-HER-200ML` | MUZA HERBAL MULE BLISS COCKTAIL 0.2L |

Either author the BOMs, or change `SUPPLY_METHOD` to `BOUGHT_FINISHED` (if
they're actually resold MUZA-made finished bottles).

---

## 5. RECOMMENDED FIX SEQUENCE

Do these in order. None is the simulator's fault — they are master-data
gaps surfaced by the simulator.

1. **Decide the model interpretation** for §2: is `final_bom_output_qty`
   the **post-water** real total volume (and any gap = missing water/loss
   line), or is it the sum of declared lines (and "+gap" cases mean a
   typo in declared qty)? Tom + Andrey decision per BOM. Probably:
   - Positive-gap cases (declared > sum) → add a `RAW-WATER` (or specific
     diluent) line of size = `gap_L`.
   - Negative-gap cases (sum > declared) → raise `final_bom_output_qty`
     to the sum, OR find which component qty is wrong.

2. **Fix the 33 ID mismatches** (§3). Single SQL update per the chosen
   convention. After this fix, `derived_from_bom` resolution kicks in and
   the simulator becomes more robust to missing item-level fill qtys.

3. **Add BOMs (or re-classify) the 5 MUZA cocktails** (§4).

4. **Set `BASE_FILL_QTY_PER_UNIT`** on the 3 Margarita items
   (`FG-MAR-CLA-300ML`, `FG-MAR-STR-300ML`, `FG-MAR-PEA-300ML`) to `0.3L`.

5. **Re-run the audit script** after each batch:
   ```
   node gt-factory-os/scripts/_audit_recipes.mjs
   ```
   Target: zero rows in `baseBomVolumeGap`, `baseRefIdMismatch`,
   `itemMissingBoms`.

---

## 6. NUMBERS THE SIMULATOR PRODUCES TODAY (per-unit, in L)

These are what the operator sees on `/planning/production-simulation` for
target qty = 1 unit. Use them to spot-check what each fix changes.

(Selected liquid-only lines from §2's troubled BOMs; full per-unit table
for all 50 items lives in `recipe_audit_report.json` →
`product_audit_rows`.)

| Item | Pack | BASE_FILL | Wine/main | Water | Sugar |
|---|---:|---:|---|---|---|
| WHITE SANGRIA 3.85L | 3.85 L | 3.85 L | 2.6213 L (wine) | (none in BOM) | (none in BOM) |
| WHITE SANGRIA ELITA 0.75L | 0.75 L | 0.75 L | 0.5106 L (wine) | (none in BOM) | (none in BOM) |
| RED SANGRIA 3.85L | 3.85 L | 3.85 L | 2.346 L (wine) | 0.7357 L | 0.1144 L |
| NONOMIMI SANGRIA 3.85L | 3.85 L | 3.85 L | 2.357 L (wine) | 0.770 L | 0.1139 L |
| FRESH 1L | 1.0 L | 1.0 L | — (hibiscus 0.0549 L) | 0.7843 L | 0.3490 L |
| FRESH 1L NO SUGAR | 1.0 L | 1.0 L | — (hibiscus 0.0752 L) | 1.0738 L | — |
| DETOX 1L | 1.0 L | 1.0 L | — (greentea 0.023 L) | 0.84 L | 0.38 L |
| DETOX 1L NO SUGAR | 1.0 L | 1.0 L | — (greentea 0.0286 L) | 1.0 L | — |
| CONSCIOUSNESS 1L | 1.0 L | 1.0 L | — (jasmin 0.0440 L) | 0.7326 L | 0.3187 L |
| REVIVE 1L | 1.0 L | 1.0 L | — (sencha 0.0518 L) | 0.8061 L | 0.3551 L |

Note especially the NS variants of FRESH/DETOX showing **water > 1.0 L
per 1.0 L pack**. That's the "components > declared" overstatement (§2,
negative gap rows). The simulator is mathematically consistent with the
data, but the data is internally inconsistent.

---

## Appendix — How the audit was built

- Input: `gt-factory-os/fixtures/masters/items.json`,
  `bom_head.json`, `bom_lines.json`, `components.json`.
- Active rows only (`STATUS = 'ACTIVE'`).
- Volume sum = sum of `final_component_qty` for lines with
  `component_uom IN ('L','ML')` (ML normalized to L).
- KG lines ignored for volume (treated as solute), reported separately as
  `sum_components_L_plus_KG` for cross-check.
- Tolerance: `max(declared * 0.5%, 0.5 L)`.
- Per-unit calculation: `qty_per_unit = (line_qty / declared_output) ×
  pack_base_mix_line_L`, mirroring the simulator's `simulate?qty=…`
  endpoint behavior.
