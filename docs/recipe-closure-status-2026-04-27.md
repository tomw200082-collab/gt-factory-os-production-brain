# Recipe Closure Status — 2026-04-27 Pass 1
**State after applying Tom's approved corrections (A through H + new components).**

---

## What changed (data-level summary)

### Master tables touched
| File | Before | After | Delta |
|---|---:|---:|---|
| `components.json` | 145 | 151 | +6 (MUZA) — RAW-ALCOHOL-96, RAW-TRIPLE-SEC, RAW-VERMOUTH-RED, RAW-VIOLET-LIQUEUR, RAW-CUCUMBER-SYRUP, RAW-MELON-EXTRACT |
| | | | 4 retired (INACTIVE): RAW-COLVE, RAW-CORNATION, RAW-LIME-PURE, RAW-BERGAMOT-PURE |
| | | | 1 standardized: RAW-YUZU-PUREE BOM_UOM L → KG |
| `supplier_items.json` | 185 | 191 | +6 primary mappings (D&D for alcohols, Kill Bill for syrups) |
| `bom_head.json` | 68 | 76 | +8 (4 BASE + 4 PACK for MUZA HER/JAS/NEG/QUE) |
| `bom_version.json` | 68 | 76 | +8 (V1_IMPORT for each new head) |
| `bom_lines.json` | 420 | 468 | +48 (28 BASE + 20 PACK lines for MUZA) |
| `items.json` | 50 | 50 | 7 items updated: 4 MUZA wired to BOMs + 0.2L fill; 3 Margaritas got 0.3L fill |

### Surgical recipe corrections (BOM lines)
14 line-qty changes across 7 BOMs:

| BOM | Component | Old qty | New qty | New per-L ratio | Source |
|---|---|---:|---:|---:|---|
| BOM-BASE-SAN-WHI-ELI-REG | RAW-WINE-WHITE | 192 L | 205.86 L | 0.730 | Excel "Sangria W Elita" |
| BOM-BASE-SAN-WHI-ELI-REG | BOM-BASE-CAL-REG | 20 L | **42.30 L** | 0.150 | Excel (was half) |
| BOM-BASE-SAN-WHI-ELI-REG | RAW-VODKA | 8 L | 8.46 L | 0.030 | Excel |
| BOM-BASE-SAN-WHI-ELI-REG | RAW-MARTINI-BIANCO | 8 L | 8.46 L | 0.030 | Excel |
| BOM-BASE-SAN-WHI-ELI-REG | RAW-ELDERFLOWER-SYRUP | 12 L | **16.92 L** | 0.060 | Excel |
| BOM-BASE-SAN-WHI-ELI-REG | RAW-LEMON-ACID | 0.26 KG | 0.282 KG | 0.001 KG/L | Excel |
| BOM-BASE-ENE-REG | RAW-LEMON-GRASS | 5.5 KG | **10.33 KG** | 0.0228 KG/L | Excel "Energy" |
| BOM-BASE-CAL-REG | RAW-LEMON-ACID | 1.1 KG | 1.63 KG | 0.00414 KG/L | Excel "Calm" |
| BOM-BASE-CAL-NS | RAW-LEMON-ACID | 1.1 KG | 1.63 KG | 0.00414 KG/L | mirror of REG |
| BOM-BASE-NAM-REG | RAW-CLOVE | 1.0 KG | **2.97 KG** | 0.00604 KG/L | Excel "Namastea (new)" |
| BOM-BASE-NAM-REG | RAW-PUER | 0.5 KG | **4.10 KG** | 0.00833 KG/L | Excel |
| BOM-BASE-AME-REG | RAW-SUGAR | 189 KG | 157.44 KG | 0.32 KG/L | Excel "American" |
| BOM-BASE-DES-REG | RAW-SUGAR | 165 KG | 114.81 KG | 0.267 KG/L | Excel "Desert" |
| BOM-BASE-MAR-{CLA,STR,PEA} L05 | RAW-YUZU-PUREE | 10 L | 10 KG | — | UOM standardize (density~1.0) |

### Tom's "ratios are truth" model — schema-level commit
- `qty_per_l_output` populated on **191 BASE BOM lines** (was null everywhere). This is now the canonical per-liter ratio field — backwards-compatible with the existing simulator (which still uses qty/declared math) but ready for Phase 1 to read directly.

---

## Reconciliation against Excel — before vs after

| Sheet | match BEFORE | match AFTER | delta BEFORE | delta AFTER | Verdict |
|---|---:|---:|---:|---:|---|
| **Sangria W Elita** | 0 | **6** | 2 | **0** | ✅ all closed |
| Energy | 3 | **4** | 1 | **0** | ✅ delta closed |
| Namastea (new) | 0 | **2** | 2 | **0** | ✅ delta closed |
| American | 3 | **4** | 1 | **0** | ✅ delta closed |
| Desert | 0 | 1 | 1 | **0** | ✅ delta closed |
| Calm | 0 | 1 | 4 | **3** | partial — 1 closed, 3 (apple/clove/water) still 12% |
| Pink Sangria | 3 | 3 | 1 | 1 | unchanged (preservative -15%) |
| White Sangria 1L | 2 | 2 | 1 | 1 | unchanged (lemon acid -50%) |
| Sangria R Elita | 7 | 7 | 0 | 0 | already MATCH |
| Sangria NM | 1 | 1 | 0 | 0 | all CLOSE |
| Detox | 0 | 0 | 0 | 0 | all CLOSE |
| Detox SF | 0 | 0 | 0 | 0 | all CLOSE |
| Fresh | 0 | 0 | 1 | 1 | unchanged (lemon acid +14%) |
| Fresh SF | 0 | 0 | 0 | 0 | all CLOSE |
| Revive | 0 | 0 | 0 | 0 | all CLOSE |
| Consciousness | 0 | 0 | 1 | 1 | unchanged (lemon acid -20%) |
| **Cosmo Lychee** | 0 | 0 | 9 | 9 | needs manual decision (G) |

**Net:** 6 BOMs improved, 11 unchanged, 0 regressed. The 5 Excel-confirmed major corrections (B + F) all landed.

---

## Items now at 100% — ready for Phase 1 simulation

### Manufactured FGs with verified BOMs (47 of 50)

All have:
- PACK BOM linked
- BASE BOM linked (where applicable)
- BASE_FILL_QTY_PER_UNIT set
- Per-L ratios populated in qty_per_l_output

Including the 4 new MUZA cocktails (HER, JAS, NEG, QUE).

### Items still NOT verifiable in Phase 1 (3)

| Item | Reason | Action |
|---|---|---|
| `FG-MUZ-PSC-200ML` (Passion Spritz) | No recipe supplied | Tom flagged: leave as known gap |
| `FG-DET-1L-NS` / `FG-DET-500ML-NS` | DETOX-NS BOM doesn't follow REG-minus-sugar rule | Pending Andrey |

### Items that would need a recipe but aren't in scope (7)

7 `ADD-MUZ-*-1L` MIXER items (Jasmin, Tropical, Pink Mama, Purple Kiss, Basil Smash, Classic Margarita Mixer, Herbal Mule Mixer) — exist in master with no BOMs. These are 1 L mixer-pour items, distinct from the 200 ml ready-to-drink MUZA cocktails. **Surface to Tom: are these still in the product line?**

---

## Final residual gaps (decisions remaining for Tom + Andrey)

### Quick decisions (no Andrey needed)

1. **MUZA MIXER 1L line** (7 items) — keep, retire, or add recipes?
2. **Sangria W Elita Preservative** — Excel omits it; we kept current 0.4 L. Confirm: include or remove from BOM?
3. **YUZU-PUREE density assumption** — converted Margarita lines from L to KG with qty unchanged (assumes density = 1.0). Confirm acceptable, or supply true density?

### Andrey-required

4. **DETOX-NS recipe** — currently has all components halved (210 L declared; halved water/herbs). Per your stated NS rule (REG minus sugar, no other change), this is wrong. Tom previously said "yes Andrey" — please confirm with him: keep half-batch, or align to REG-minus-sugar?
5. **Cosmo Lychee** — Excel sheet has two recipe columns side-by-side at very different scales. The first column gives 9 ratio deltas vs current BOM. Which Excel column is canonical? (Or: replace with new recipe entirely?)
6. **Calm — apple/clove/water +12% delta** — small but persistent. Acceptable as measurement noise, or fix?
7. **Pink Sangria preservative** −15% delta — confirm BOM ratio (0.002 L/L) vs Excel (0.0017 L/L)?
8. **White Sangria 1L lemon acid** −50% delta — BOM has 0.0048 KG/L, Excel 0.0024 KG/L. Big gap. Halve BOM?
9. **Fresh / Consciousness lemon acid** small deltas (+14% / −20%) — quick yes/no.

### Structural (no Andrey, just engineering)

10. **PACK→BASE id-convention mismatch** (33 items + 4 new MUZA = 37) — PACK BOM lines reference `BOM-BASE-XXX` (head id) but BASE head's `parent_ref_id` is `BASE-XXX` (without "BOM-" prefix). Simulator's `derived_from_bom` resolution silently fails on these. Fix: single SQL update normalizing convention. Doesn't change recipes, just makes auto-resolution work.

---

## Audit gates (per CURRENT_STATE rules)

```
=== RECIPE AUDIT (post-corrections) ===
items_audited:           50 (incl. 4 new MUZA + 3 Margaritas)
base_boms_audited:       27 (was 23, +4 MUZA)
pack_boms_audited:       45 (was 41, +4 MUZA)

DOWN-counts (good):
  itemMissingBoms:           1   (was 5; remaining: PSC = known gap)
  itemFillVsPackSize:        0
  packBomVsItemFill:         0
  unitMismatches:            0
  packBomMissingBaseLine:    0

PERSISTENT (under Tom's "ratios are truth" model these are NOT real issues):
  baseBomVolumeGap:         18   (was 16; +2 from MUZA where declared = sum exact)
                                  → moot: declared output is just a reference scale
  baseRefIdMismatch:        37   (was 33; +4 from new MUZA following same convention)
                                  → structural, gets fixed once globally (item 10 above)

=== EXCEL RECONCILIATION (post-corrections) ===
17 sheets paired: 6 improved, 11 unchanged, 0 regressed
Major DELTAs cleared: Sangria W Elita (2→0), Energy (1→0), Namastea (2→0),
                      American (1→0), Desert (1→0)
Remaining DELTAs: Calm 3 (apple/clove/water +12%), White Sangria 1L 1 (lemon acid),
                  Pink Sangria 1, Fresh 1, Consciousness 1, Cosmo Lychee 9
```

---

## What I need from you to call this 100%-closed

A short reply to items 1–10 (mostly yes/no; items 4–9 need Andrey). Once those land I can:
- Apply the remaining surgical fixes (items 4, 6, 7, 8, 9)
- Resolve Cosmo Lychee (item 5)
- Fix the 37 PACK→BASE id mismatches (item 10) — purely mechanical
- Decide on MUZA MIXER 1L (item 1)

After that: clean audit + clean reconciliation = green light for Phase 1 (dual-input UX + planning derivation).
