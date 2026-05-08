# Recipe Reconciliation v2 — per-liter ratios
**Generated:** 2026-04-27
**Excel:** `cost of production August 2025.xlsx`
**Method:** ratios per 1 L of finished base. MATCH ≤2%, CLOSE ≤10%, DELTA >10%.

## Summary

| Sheet | BOM | Excel batch L | BOM declared L | pairs | match | close | delta | UOM-mis | BOM-only | Excel-only | Unmapped |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Cosmo Lychee | `BOM-BASE-COS-LYC-REG` | 100.55 | 409.5 | 13 | 0 | 0 | 9 | 0 | 0 | 4 | 5 |
| Pink Sangria | `BOM-BASE-SAN-PIN-REG` | 100.0 | 50.0 | 4 | 3 | 0 | 1 | 0 | 0 | 0 | 0 |
| White Sangria | `BOM-BASE-SAN-WHI-REG` | 100.0 | 50.0 | 4 | 2 | 1 | 1 | 0 | 0 | 0 | 0 |
| Sangria R Elita | `BOM-BASE-SAN-RED-ELI-REG` | 480.0 | 471.0 | 8 | 7 | 1 | 0 | 0 | 0 | 0 | 4 |
| Sangria W Elita | `BOM-BASE-SAN-WHI-ELI-REG` | 500.0 | 282.0 | 6 | 6 | 0 | 0 | 0 | 1 | 0 | 0 |
| Sangria NM | `BOM-BASE-NM-REG` | 475.0 | 490.0 | 12 | 1 | 11 | 0 | 0 | 4 | 0 | 6 |
| American | `BOM-BASE-AME-REG` | 500.0 | 492.0 | 8 | 4 | 0 | 0 | 4 | 3 | 0 | 3 |
| Desert | `BOM-BASE-DES-REG` | 419.0 | 430.0 | 11 | 1 | 8 | 0 | 2 | 5 | 0 | 4 |
| Detox | `BOM-BASE-DET-REG` | 515.0 | 500.0 | 6 | 0 | 5 | 0 | 0 | 4 | 1 | 3 |
| Energy | `BOM-BASE-ENE-REG` | 460.0 | 453.0 | 8 | 4 | 3 | 0 | 1 | 2 | 0 | 3 |
| Fresh | `BOM-BASE-FRE-REG` | 470.0 | 510.0 | 4 | 0 | 2 | 1 | 1 | 3 | 0 | 4 |
| Calm | `BOM-BASE-CAL-REG` | 175.0 | 394.0 | 7 | 1 | 1 | 3 | 1 | 3 | 1 | 3 |
| Revive | `BOM-BASE-REV-REG` | 500.0 | 521.0 | 6 | 0 | 4 | 0 | 2 | 2 | 0 | 3 |
| Namastea (new) | `BOM-BASE-NAM-REG` | 480.0 | 492.0 | 6 | 2 | 4 | 0 | 0 | 6 | 0 | 8 |
| Detox SF | `BOM-BASE-DET-NS` | 385.0 | 210.0 | 5 | 0 | 4 | 0 | 0 | 4 | 1 | 3 |
| Consciousness | `BOM-BASE-CON-REG` | 500.0 | 273.0 | 5 | 0 | 2 | 1 | 2 | 3 | 0 | 3 |
| Fresh SF | `BOM-BASE-FRE-NS` | 365.0 | 372.5 | 3 | 0 | 2 | 0 | 0 | 4 | 1 | 3 |

## Cosmo Lychee — `BOM-BASE-COS-LYC-REG`

- Excel batch (L used): **100.55** (L lines sum 904.2425573343018, KG lines sum 3.05)
- BOM declared L: **409.5**

### Paired ingredients (per 1 L of finished base)

| Component | Excel name | Excel /L | UOM | BOM qty | BOM /L | UOM | Δ% | status |
|---|---|---:|---|---:|---:|---|---:|---|
| `BOM-BASE-FRE-REG` | Fresh | 1.392342 | L | 74.7 | 0.182418 | L | +663.3% | **DELTA** |
| `RAW-CRANBERRY-PUREE-ODK` | Cranberry puree ODK | 0.079562 | L | 4.3 | 0.010501 | L | +657.7% | **DELTA** |
| `RAW-LEMON-ACID` | Lemon acid; lemon acid | 0.030333 | KG | 1.6 | 0.003907 | KG | +676.3% | **DELTA** |
| `RAW-LYCHEE-SYRUP` | Lychee syrup | 0.447539 | L | 24.0 | 0.058608 | L | +663.6% | **DELTA** |
| `RAW-PRESERVATIVE` | Preservative; Preservative | 0.011934 | L | 0.5 | 0.001221 | L | +877.4% | **DELTA** |
| `RAW-RASPBERRY-SYRUP` | Raspberry syrup | 0.079562 | L | 4.3 | 0.010501 | L | +657.7% | **DELTA** |
| `RAW-SUGAR-WATER` | Sugar water | 0.308304 | L | 16.4 | 0.040049 | L | +669.8% | **DELTA** |
| `RAW-VODKA` | vodka | 2.516161 | L | 135.0 | 0.32967 | L | +663.2% | **DELTA** |
| `RAW-WATER` | Water; Water | 2.784684 | L | 144.0 | 0.351648 | L | +691.9% | **DELTA** |
| `BOM-BASE-ENE-REG` | Energy | 0.367976 | L | — | — | — | — | **EXCEL_HAS_EXTRA** |
| `RAW-AMARETTO` | Amaretto | 0.032819 | L | — | — | — | — | **EXCEL_HAS_EXTRA** |
| `RAW-ARAK` | Arak | 0.248633 | L | — | — | — | — | **EXCEL_HAS_EXTRA** |
| `RAW-LEMON-WATER` | Lemon water | 0.174043 | L | — | — | — | — | **EXCEL_HAS_EXTRA** |

### Excel rows that could not be mapped to a known component

| Excel name | Vol | UOM guess |
|---|---:|---|
| cost per liter | 33.659202495592034 | L |
| Rosetta syrup | 0.5 | L |
| Apple puree ODK | 7.0 | L |
| cost per liter | 6.791677419354839 | L |
| cost per liter incl package | 7.291677419354839 | L |

## Pink Sangria — `BOM-BASE-SAN-PIN-REG`

- Excel batch (L used): **100.0** (L lines sum 100.17, KG lines sum 0.22)
- BOM declared L: **50.0**

### Paired ingredients (per 1 L of finished base)

| Component | Excel name | Excel /L | UOM | BOM qty | BOM /L | UOM | Δ% | status |
|---|---|---:|---|---:|---:|---|---:|---|
| `RAW-PRESERVATIVE` | Preservative | 0.0017 | L | 0.1 | 0.002 | L | -15.0% | **DELTA** |
| `BOM-BASE-FRE-REG` | Fresh | 0.42 | L | 21.0 | 0.42 | L | +0.0% | **MATCH** |
| `RAW-LEMON-ACID` | Lemon acid | 0.0022 | KG | 0.11 | 0.0022 | KG | +0.0% | **MATCH** |
| `RAW-WINE-WHITE` | Wine (white) Symphony | 0.58 | L | 29.0 | 0.58 | L | +0.0% | **MATCH** |

## White Sangria — `BOM-BASE-SAN-WHI-REG`

- Excel batch (L used): **100.0** (L lines sum 100.19, KG lines sum 0.24)
- BOM declared L: **50.0**

### Paired ingredients (per 1 L of finished base)

| Component | Excel name | Excel /L | UOM | BOM qty | BOM /L | UOM | Δ% | status |
|---|---|---:|---|---:|---:|---|---:|---|
| `RAW-PRESERVATIVE` | Preservative | 0.0019 | L | 0.1 | 0.002 | L | -5.0% | **CLOSE** |
| `RAW-LEMON-ACID` | Lemon acid | 0.0024 | KG | 0.24 | 0.0048 | KG | -50.0% | **DELTA** |
| `BOM-BASE-CAL-REG` | Calm | 0.35 | L | 17.5 | 0.35 | L | +0.0% | **MATCH** |
| `RAW-WINE-WHITE` | Wine (white) Symphony | 0.65 | L | 32.5 | 0.65 | L | +0.0% | **MATCH** |

## Sangria R Elita — `BOM-BASE-SAN-RED-ELI-REG`

- Excel batch (L used): **480.0** (L lines sum 536.9334074309979, KG lines sum 14.0)
- BOM declared L: **471.0**

### Paired ingredients (per 1 L of finished base)

| Component | Excel name | Excel /L | UOM | BOM qty | BOM /L | UOM | Δ% | status |
|---|---|---:|---|---:|---:|---|---:|---|
| `RAW-ORANGE-JUICE-CONCENTRATE` | Orange juice concentrate | 0.052083 | L | 26.0 | 0.055202 | L | -5.7% | **CLOSE** |
| `BOM-BASE-FRE-REG` | Fresh | 0.079167 | L | 38.0 | 0.080679 | L | -1.9% | **MATCH** |
| `BOM-BASE-NAM-REG` | Namastea | 0.060417 | L | 29.0 | 0.061571 | L | -1.9% | **MATCH** |
| `RAW-PRESERVATIVE` | Preservative | 0.001042 | L | 0.5 | 0.001062 | L | -1.9% | **MATCH** |
| `RAW-RUM` | Rum | 0.033333 | L | 16.0 | 0.03397 | L | -1.9% | **MATCH** |
| `RAW-SUGAR` | Sugar | 0.029167 | KG | 14.0 | 0.029724 | KG | -1.9% | **MATCH** |
| `RAW-WATER` | Water | 0.1875 | L | 90.0 | 0.191083 | L | -1.9% | **MATCH** |
| `RAW-WINE-RED` | Wine (red) Symphony | 0.597917 | L | 287.0 | 0.609342 | L | -1.9% | **MATCH** |

### Excel rows that could not be mapped to a known component

| Excel name | Vol | UOM guess |
|---|---:|---|
| cost per liter w/o package | 11.885668789808918 | L |
| cost per liter with package | 17.93566878980892 | L |
| cost per 0.7 liter w/o package | 8.914251592356688 | L |
| cost per 0.7 liter with package | 12.697818259023354 | L |

## Sangria W Elita — `BOM-BASE-SAN-WHI-ELI-REG`

- Excel batch (L used): **500.0** (L lines sum 500.0, KG lines sum 0.5)
- BOM declared L: **282.0**

### Paired ingredients (per 1 L of finished base)

| Component | Excel name | Excel /L | UOM | BOM qty | BOM /L | UOM | Δ% | status |
|---|---|---:|---|---:|---:|---|---:|---|
| `BOM-BASE-CAL-REG` | Calm | 0.15 | L | 42.3 | 0.15 | L | +0.0% | **MATCH** |
| `RAW-ELDERFLOWER-SYRUP` | Elderflower syrup | 0.06 | L | 16.92 | 0.06 | L | -0.0% | **MATCH** |
| `RAW-LEMON-ACID` | Lemon acid | 0.001 | KG | 0.282 | 0.001 | KG | +0.0% | **MATCH** |
| `RAW-MARTINI-BIANCO` | Martini bianco | 0.03 | L | 8.46 | 0.03 | L | -0.0% | **MATCH** |
| `RAW-VODKA` | Vodka | 0.03 | L | 8.46 | 0.03 | L | -0.0% | **MATCH** |
| `RAW-WINE-WHITE` | Wine (white) Symphony | 0.73 | L | 205.86 | 0.73 | L | -0.0% | **MATCH** |

### Components in BOM but NOT in Excel recipe

| Component | BOM name | BOM qty | UOM | BOM /L |
|---|---|---:|---|---:|
| `RAW-PRESERVATIVE` | Preservative (Bulk) | 0.4 | L | 0.001418 |

## Sangria NM — `BOM-BASE-NM-REG`

- Excel batch (L used): **475.0** (L lines sum 626.7621475198625, KG lines sum 18.69)
- BOM declared L: **490.0**

### Paired ingredients (per 1 L of finished base)

| Component | Excel name | Excel /L | UOM | BOM qty | BOM /L | UOM | Δ% | status |
|---|---|---:|---|---:|---:|---|---:|---|
| `BOM-BASE-FRE-REG` | Fresh | 0.142105 | L | 67.5 | 0.137755 | L | +3.2% | **CLOSE** |
| `RAW-ANISE` | Anise | 0.001537 | KG | 0.73 | 0.00149 | KG | +3.2% | **CLOSE** |
| `RAW-CINNAMON` | Cinnamon | 0.005368 | KG | 2.5 | 0.005102 | KG | +5.2% | **CLOSE** |
| `RAW-CLOVE` | Cloves | 0.000379 | KG | 0.18 | 0.000367 | KG | +3.2% | **CLOSE** |
| `RAW-DRIED-LEMON` | Dried lemon | 0.000716 | KG | 0.34 | 0.000694 | KG | +3.2% | **CLOSE** |
| `RAW-DRIED-ORANGE` | Dried orange | 0.000716 | KG | 0.34 | 0.000694 | KG | +3.2% | **CLOSE** |
| `RAW-ORANGE-JUICE-CONCENTRATE` | Orange juice concentrate | 0.054442 | L | 26.0 | 0.053061 | L | +2.6% | **CLOSE** |
| `RAW-PRESERVATIVE` | Preservative | 0.001053 | L | 0.5 | 0.00102 | L | +3.2% | **CLOSE** |
| `RAW-SUGAR` | Sugar | 0.030632 | KG | 14.5 | 0.029592 | KG | +3.5% | **CLOSE** |
| `RAW-WATER` | Water; water | 0.205853 | L | 98.0 | 0.2 | L | +2.9% | **CLOSE** |
| `RAW-WINE-RED` | Wine (red) Symphony | 0.631579 | L | 300.0 | 0.612245 | L | +3.2% | **CLOSE** |
| `RAW-AMARETTO` | Amaretto | 0.026042 | L | 12.73 | 0.02598 | L | +0.2% | **MATCH** |

### Components in BOM but NOT in Excel recipe

| Component | BOM name | BOM qty | UOM | BOM /L |
|---|---|---:|---|---:|
| `RAW-EL` | Green Cardamom Pods | 0.18 | KG | 0.000367 |
| `RAW-PAPER` | Black Pepper | 0.15 | KG | 0.000306 |
| `PKG-FILTER-100MICRON` | Single Length Filter 100 micron | 1.0 | UNIT | 0.002041 |
| `PKG-FILTER-200MICRON` | Double Length Filter 200 micron | 1.0 | UNIT | 0.002041 |

### Excel rows that could not be mapped to a known component

| Excel name | Vol | UOM guess |
|---|---:|---|
| Black pepper | 0.15 | L |
| El/Cardamom | 0.18 | L |
| single length 100 micron | 1.0 | L |
| double length 200 micron | 1.0 | L |
| jerrican 3.85 l | 102.0 | L |
| Cost per 1000 ml | 18.42214751986257 | L |

## American — `BOM-BASE-AME-REG`

- Excel batch (L used): **500.0** (L lines sum 465.0, KG lines sum 172.3)
- BOM declared L: **492.0**

### Paired ingredients (per 1 L of finished base)

| Component | Excel name | Excel /L | UOM | BOM qty | BOM /L | UOM | Δ% | status |
|---|---|---:|---|---:|---:|---|---:|---|
| `RAW-DRIED-ORANGE` | Dried Orange | 0.012 | KG | 6.0 | 0.012195 | KG | -1.6% | **MATCH** |
| `RAW-PUER` | Puer tea | 0.0126 | KG | 6.3 | 0.012805 | KG | -1.6% | **MATCH** |
| `RAW-SUGAR` | Sugar | 0.32 | KG | 157.44 | 0.32 | KG | +0.0% | **MATCH** |
| `RAW-WATER` | Water | 0.84 | L | 420.0 | 0.853659 | L | -1.6% | **MATCH** |
| `RAW-BERGAMOT-PUREE` | Bergamot puree | 0.0126 | L | 6.3 | 0.012805 | KG | — | **UOM_MISMATCH** |
| `RAW-LEMON-PUREE` | Lemon puree | 0.0168 | L | 8.4 | 0.017073 | KG | — | **UOM_MISMATCH** |
| `RAW-LIME-PUREE` | Lime puree | 0.0168 | L | 8.4 | 0.017073 | KG | — | **UOM_MISMATCH** |
| `RAW-YUZU-PUREE` | Yuzu puree | 0.002 | L | 1.0 | 0.002033 | KG | — | **UOM_MISMATCH** |

### Components in BOM but NOT in Excel recipe

| Component | BOM name | BOM qty | UOM | BOM /L |
|---|---|---:|---|---:|
| `RAW-BLACK-TEA` | Black Tea | 18.9 | KG | 0.038415 |
| `PKG-FILTER-100MICRON` | Single Length Filter 100 micron | 1.0 | UNIT | 0.002033 |
| `PKG-FILTER-200MICRON` | Double Length Filter 200 micron | 1.0 | UNIT | 0.002033 |

### Excel rows that could not be mapped to a known component

| Excel name | Vol | UOM guess |
|---|---:|---|
| Black tea | 18.9 | L |
| single length 100 micron | 1.0 | L |
| double length 200 micron | 1.0 | L |

## Desert — `BOM-BASE-DES-REG`

- Excel batch (L used): **419.0** (L lines sum 447.85, KG lines sum 138.12)
- BOM declared L: **430.0**

### Paired ingredients (per 1 L of finished base)

| Component | Excel name | Excel /L | UOM | BOM qty | BOM /L | UOM | Δ% | status |
|---|---|---:|---|---:|---:|---|---:|---|
| `RAW-LEMON-ACID` | Lemon acid | 0.002983 | KG | 1.25 | 0.002907 | KG | +2.6% | **CLOSE** |
| `RAW-LEMON-GRASS` | Lemon grass | 0.02506 | KG | 10.5 | 0.024419 | KG | +2.6% | **CLOSE** |
| `RAW-MARVA` | Marva | 0.005012 | KG | 2.1 | 0.004884 | KG | +2.6% | **CLOSE** |
| `RAW-MELISA` | Melisa | 0.005012 | KG | 2.1 | 0.004884 | KG | +2.6% | **CLOSE** |
| `RAW-MENTA` | menta | 0.005012 | KG | 2.1 | 0.004884 | KG | +2.6% | **CLOSE** |
| `RAW-NANA` | Nana | 0.015036 | KG | 6.3 | 0.014651 | KG | +2.6% | **CLOSE** |
| `RAW-OREGANO` | Oregano | 0.005012 | KG | 2.1 | 0.004884 | KG | +2.6% | **CLOSE** |
| `RAW-WATER` | Water | 1.002387 | L | 470.0 | 1.093023 | L | -8.3% | **CLOSE** |
| `RAW-SUGAR` | Sugar | 0.266516 | KG | 114.81 | 0.267 | KG | -0.2% | **MATCH** |
| `RAW-LEMON-PUREE` | Lemon puree | 0.023866 | L | 10.0 | 0.023256 | KG | — | **UOM_MISMATCH** |
| `RAW-LIME-PUREE` | Lime puree | 0.019093 | L | 8.0 | 0.018605 | KG | — | **UOM_MISMATCH** |

### Components in BOM but NOT in Excel recipe

| Component | BOM name | BOM qty | UOM | BOM /L |
|---|---|---:|---|---:|
| `RAW-PASSION-FRUIT-PUREE` | Passion Fruit | 22.0 | KG | 0.051163 |
| `RAW-LUISA` | Lemon Verbena (Luiza) | 5.75 | KG | 0.013372 |
| `RAW-ZUTA` | White-Leaved Savory (Zuta) | 2.1 | KG | 0.004884 |
| `PKG-FILTER-100MICRON` | Single Length Filter 100 micron | 1.0 | UNIT | 0.002326 |
| `PKG-FILTER-200MICRON` | Double Length Filter 200 micron | 1.0 | UNIT | 0.002326 |

### Excel rows that could not be mapped to a known component

| Excel name | Vol | UOM guess |
|---|---:|---|
| Louisa | 5.75 | L |
| White zuta | 2.1 | L |
| single length 100 micron | 1.0 | L |
| double length 200 micron | 1.0 | L |

## Detox — `BOM-BASE-DET-REG`

- Excel batch (L used): **515.0** (L lines sum 449.5, KG lines sum 196.5)
- BOM declared L: **500.0**

### Paired ingredients (per 1 L of finished base)

| Component | Excel name | Excel /L | UOM | BOM qty | BOM /L | UOM | Δ% | status |
|---|---|---:|---|---:|---:|---|---:|---|
| `RAW-GREEN-TEA` | Green tea | 0.02233 | KG | 11.5 | 0.023 | KG | -2.9% | **CLOSE** |
| `RAW-LEMON-ACID` | Lemon acid | 0.002913 | KG | 1.55 | 0.0031 | KG | -6.0% | **CLOSE** |
| `RAW-NANA` | Nana | 0.006796 | KG | 3.5 | 0.007 | KG | -2.9% | **CLOSE** |
| `RAW-SUGAR` | Sugar | 0.349515 | KG | 190.0 | 0.38 | KG | -8.0% | **CLOSE** |
| `RAW-WATER` | Water | 0.815534 | L | 420.0 | 0.84 | L | -2.9% | **CLOSE** |
| `RAW-LIME-PUREE` | Lime puree | 0.029126 | L | — | — | — | — | **EXCEL_HAS_EXTRA** |

### Components in BOM but NOT in Excel recipe

| Component | BOM name | BOM qty | UOM | BOM /L |
|---|---|---:|---|---:|
| `RAW-LUISA` | Lemon Verbena (Luiza) | 12.5 | KG | 0.025 |
| `RAW-LEMON-PUREE` | Lemon Puree (Ristretto) | 15.0 | KG | 0.03 |
| `PKG-FILTER-100MICRON` | Single Length Filter 100 micron | 1.0 | UNIT | 0.002 |
| `PKG-FILTER-200MICRON` | Double Length Filter 200 micron | 1.0 | UNIT | 0.002 |

### Excel rows that could not be mapped to a known component

| Excel name | Vol | UOM guess |
|---|---:|---|
| Louisa | 12.5 | L |
| single length 100 micron | 1.0 | L |
| double length 200 micron | 1.0 | L |

## Energy — `BOM-BASE-ENE-REG`

- Excel batch (L used): **460.0** (L lines sum 436.0, KG lines sum 213.0)
- BOM declared L: **453.0**

### Paired ingredients (per 1 L of finished base)

| Component | Excel name | Excel /L | UOM | BOM qty | BOM /L | UOM | Δ% | status |
|---|---|---:|---|---:|---:|---|---:|---|
| `RAW-LEMON-ACID` | lemon acid | 0.003043 | KG | 1.5 | 0.003311 | KG | -8.1% | **CLOSE** |
| `RAW-NANA` | Nana | 0.00913 | KG | 4.0 | 0.00883 | KG | +3.4% | **CLOSE** |
| `RAW-SUGAR` | sugar | 0.369565 | KG | 175.0 | 0.386313 | KG | -4.3% | **CLOSE** |
| `RAW-GREEN-TEA` | green tea | 0.054783 | KG | 25.0 | 0.055188 | KG | -0.7% | **MATCH** |
| `RAW-LEMON-GRASS` | lemon grass | 0.022826 | KG | 10.3284 | 0.0228 | KG | +0.1% | **MATCH** |
| `RAW-MENTA` | menta | 0.003696 | KG | 1.7 | 0.003753 | KG | -1.5% | **MATCH** |
| `RAW-WATER` | water | 0.913043 | L | 420.0 | 0.927152 | L | -1.5% | **MATCH** |
| `RAW-LEMON-PUREE` | lemon puree | 0.028261 | L | 15.0 | 0.033113 | KG | — | **UOM_MISMATCH** |

### Components in BOM but NOT in Excel recipe

| Component | BOM name | BOM qty | UOM | BOM /L |
|---|---|---:|---|---:|
| `PKG-FILTER-100MICRON` | Single Length Filter 100 micron | 1.0 | UNIT | 0.002208 |
| `PKG-FILTER-200MICRON` | Double Length Filter 200 micron | 1.0 | UNIT | 0.002208 |

### Excel rows that could not be mapped to a known component

| Excel name | Vol | UOM guess |
|---|---:|---|
| single length 100 micron | 1.0 | L |
| double length 200 micron | 1.0 | L |
| jerrican 20 l | 1.0 | L |

## Fresh — `BOM-BASE-FRE-REG`

- Excel batch (L used): **470.0** (L lines sum 443.0, KG lines sum 176.0)
- BOM declared L: **510.0**

### Paired ingredients (per 1 L of finished base)

| Component | Excel name | Excel /L | UOM | BOM qty | BOM /L | UOM | Δ% | status |
|---|---|---:|---|---:|---:|---|---:|---|
| `RAW-SUGAR` | sugar | 0.37234 | KG | 178.0 | 0.34902 | KG | +6.7% | **CLOSE** |
| `RAW-WATER` | water | 0.851064 | L | 400.0 | 0.784314 | L | +8.5% | **CLOSE** |
| `RAW-LEMON-ACID` | lemon acid | 0.002128 | KG | 0.95 | 0.001863 | KG | +14.2% | **DELTA** |
| `RAW-LIME-PUREE` | lime puree | 0.023404 | L | 10.0 | 0.019608 | KG | — | **UOM_MISMATCH** |

### Components in BOM but NOT in Excel recipe

| Component | BOM name | BOM qty | UOM | BOM /L |
|---|---|---:|---|---:|
| `RAW-HIBISCUS` | Hibiscus | 28.0 | KG | 0.054902 |
| `PKG-FILTER-100MICRON` | Single Length Filter 100 micron | 1.0 | UNIT | 0.001961 |
| `PKG-FILTER-200MICRON` | Double Length Filter 200 micron | 1.0 | UNIT | 0.001961 |

### Excel rows that could not be mapped to a known component

| Excel name | Vol | UOM guess |
|---|---:|---|
| karkade | 28.0 | L |
| single length 100 micron | 1.0 | L |
| double length 200 micron | 1.0 | L |
| jerrican 23 l | 2.0 | L |

## Calm — `BOM-BASE-CAL-REG`

- Excel batch (L used): **175.0** (L lines sum 228.0, KG lines sum 88.725)
- BOM declared L: **394.0**

### Paired ingredients (per 1 L of finished base)

| Component | Excel name | Excel /L | UOM | BOM qty | BOM /L | UOM | Δ% | status |
|---|---|---:|---|---:|---:|---|---:|---|
| `RAW-SUGAR` | sugar | 0.428571 | KG | 175.0 | 0.444162 | KG | -3.5% | **CLOSE** |
| `RAW-APPLE-DRY` | Dried apple | 0.071429 | KG | 25.0 | 0.063452 | KG | +12.6% | **DELTA** |
| `RAW-CLOVE` | cloves | 0.002857 | KG | 1.0 | 0.002538 | KG | +12.6% | **DELTA** |
| `RAW-WATER` | water | 1.2 | L | 420.0 | 1.06599 | L | +12.6% | **DELTA** |
| `RAW-LIME-PUREE` | Lime puree | 0.011429 | L | — | — | — | — | **EXCEL_HAS_EXTRA** |
| `RAW-LEMON-ACID` | lemon acid | 0.004143 | KG | 1.6312 | 0.00414 | KG | +0.1% | **MATCH** |
| `RAW-LEMON-PUREE` | lemon puree | 0.028571 | L | 14.0 | 0.035533 | KG | — | **UOM_MISMATCH** |

### Components in BOM but NOT in Excel recipe

| Component | BOM name | BOM qty | UOM | BOM /L |
|---|---|---:|---|---:|
| `RAW-CALM` | Chamomile | 18.0 | KG | 0.045685 |
| `PKG-FILTER-100MICRON` | Single Length Filter 100 micron | 1.0 | UNIT | 0.002538 |
| `PKG-FILTER-200MICRON` | Double Length Filter 200 micron | 1.0 | UNIT | 0.002538 |

### Excel rows that could not be mapped to a known component

| Excel name | Vol | UOM guess |
|---|---:|---|
| camomile | 9.0 | L |
| single length 100 micron | 1.0 | L |
| double length 200 micron | 1.0 | L |

## Revive — `BOM-BASE-REV-REG`

- Excel batch (L used): **500.0** (L lines sum 501.0, KG lines sum 215.5)
- BOM declared L: **521.0**

### Paired ingredients (per 1 L of finished base)

| Component | Excel name | Excel /L | UOM | BOM qty | BOM /L | UOM | Δ% | status |
|---|---|---:|---|---:|---:|---|---:|---|
| `RAW-LEMON-ACID` | Lemon acid | 0.002 | KG | 1.0 | 0.001919 | KG | +4.2% | **CLOSE** |
| `RAW-SENCHA` | Sencha tea | 0.054 | KG | 27.0 | 0.051823 | KG | +4.2% | **CLOSE** |
| `RAW-SUGAR` | Sugar | 0.375 | KG | 185.0 | 0.355086 | KG | +5.6% | **CLOSE** |
| `RAW-WATER` | Water | 0.84 | L | 420.0 | 0.806142 | L | +4.2% | **CLOSE** |
| `RAW-LEMON-PUREE` | Lemon puree | 0.022 | L | 11.0 | 0.021113 | KG | — | **UOM_MISMATCH** |
| `RAW-PASSION-FRUIT-PUREE` | Passion fruit puree | 0.044 | L | 22.0 | 0.042226 | KG | — | **UOM_MISMATCH** |

### Components in BOM but NOT in Excel recipe

| Component | BOM name | BOM qty | UOM | BOM /L |
|---|---|---:|---|---:|
| `PKG-FILTER-100MICRON` | Single Length Filter 100 micron | 1.0 | UNIT | 0.001919 |
| `PKG-FILTER-200MICRON` | Double Length Filter 200 micron | 1.0 | UNIT | 0.001919 |

### Excel rows that could not be mapped to a known component

| Excel name | Vol | UOM guess |
|---|---:|---|
| single length 100 micron | 1.0 | L |
| double length 200 micron | 1.0 | L |
| jerrican 23 l | 46.0 | L |

## Namastea (new) — `BOM-BASE-NAM-REG`

- Excel batch (L used): **480.0** (L lines sum 451.8635, KG lines sum 157.0)
- BOM declared L: **492.0**

### Paired ingredients (per 1 L of finished base)

| Component | Excel name | Excel /L | UOM | BOM qty | BOM /L | UOM | Δ% | status |
|---|---|---:|---|---:|---:|---|---:|---|
| `RAW-PRESERVATIVE` | Preservative | 0.001042 | L | 0.5 | 0.001016 | L | +2.5% | **CLOSE** |
| `RAW-STABILISER` | Stabilizer | 0.000208 | KG | 0.1 | 0.000203 | KG | +2.5% | **CLOSE** |
| `RAW-SUGAR` | Sugar | 0.3125 | KG | 150.0 | 0.304878 | KG | +2.5% | **CLOSE** |
| `RAW-WATER` | Water | 0.875 | L | 420.0 | 0.853659 | L | +2.5% | **CLOSE** |
| `RAW-CLOVE` | Cloves | 0.006042 | KG | 2.9717 | 0.00604 | KG | +0.0% | **MATCH** |
| `RAW-PUER` | Puer tea | 0.008333 | KG | 4.0984 | 0.00833 | KG | +0.0% | **MATCH** |

### Components in BOM but NOT in Excel recipe

| Component | BOM name | BOM qty | UOM | BOM /L |
|---|---|---:|---|---:|
| `RAW-MASALA` | Chai Masala | 25.0 | KG | 0.050813 |
| `RAW-CINNAMON` | Cinnamon | 1.0 | KG | 0.002033 |
| `RAW-PAPER` | Black Pepper | 0.5 | KG | 0.001016 |
| `RAW-EL` | Green Cardamom Pods | 0.5 | KG | 0.001016 |
| `PKG-FILTER-100MICRON` | Single Length Filter 100 micron | 1.0 | UNIT | 0.002033 |
| `PKG-FILTER-200MICRON` | Double Length Filter 200 micron | 1.0 | UNIT | 0.002033 |

### Excel rows that could not be mapped to a known component

| Excel name | Vol | UOM guess |
|---|---:|---|
| Black pepper | 2.4 | L |
| El/Cardamom | 2.21 | L |
| Crushed ginger | 0.95 | L |
| Crushed cinnamon | 13.54 | L |
| Black tea | 6.0 | L |
| single length 100 micron | 1.0 | L |
| double length 200 micron | 1.0 | L |
| Price per litre w/o package | 4.2635 | L |

## Detox SF — `BOM-BASE-DET-NS`

- Excel batch (L used): **385.0** (L lines sum 449.5, KG lines sum 16.5)
- BOM declared L: **210.0**

### Paired ingredients (per 1 L of finished base)

| Component | Excel name | Excel /L | UOM | BOM qty | BOM /L | UOM | Δ% | status |
|---|---|---:|---|---:|---:|---|---:|---|
| `RAW-GREEN-TEA` | Green tea | 0.02987 | KG | 6.0 | 0.028571 | KG | +4.5% | **CLOSE** |
| `RAW-LEMON-ACID` | Lemon acid | 0.003896 | KG | 0.75 | 0.003571 | KG | +9.1% | **CLOSE** |
| `RAW-NANA` | Nana | 0.009091 | KG | 1.75 | 0.008333 | KG | +9.1% | **CLOSE** |
| `RAW-WATER` | Water | 1.090909 | L | 210.0 | 1.0 | L | +9.1% | **CLOSE** |
| `RAW-LIME-PUREE` | Lime puree | 0.038961 | L | — | — | — | — | **EXCEL_HAS_EXTRA** |

### Components in BOM but NOT in Excel recipe

| Component | BOM name | BOM qty | UOM | BOM /L |
|---|---|---:|---|---:|
| `RAW-LUISA` | Lemon Verbena (Luiza) | 6.0 | KG | 0.028571 |
| `RAW-LEMON-PUREE` | Lemon Puree (Ristretto) | 7.5 | KG | 0.035714 |
| `PKG-FILTER-100MICRON` | Single Length Filter 100 micron | 1.0 | UNIT | 0.004762 |
| `PKG-FILTER-200MICRON` | Double Length Filter 200 micron | 1.0 | UNIT | 0.004762 |

### Excel rows that could not be mapped to a known component

| Excel name | Vol | UOM guess |
|---|---:|---|
| Louisa | 12.5 | L |
| single length 100 micron | 1.0 | L |
| double length 200 micron | 1.0 | L |

## Consciousness — `BOM-BASE-CON-REG`

- Excel batch (L used): **500.0** (L lines sum 459.0, KG lines sum 176.1)
- BOM declared L: **273.0**

### Paired ingredients (per 1 L of finished base)

| Component | Excel name | Excel /L | UOM | BOM qty | BOM /L | UOM | Δ% | status |
|---|---|---:|---|---:|---:|---|---:|---|
| `RAW-SUGAR` | Sugar | 0.35 | KG | 87.0 | 0.318681 | KG | +9.8% | **CLOSE** |
| `RAW-WATER` | Water | 0.8 | L | 200.0 | 0.732601 | L | +9.2% | **CLOSE** |
| `RAW-LEMON-ACID` | Lemon acid | 0.0022 | KG | 0.75 | 0.002747 | KG | -19.9% | **DELTA** |
| `RAW-LEMON-PUREE` | Lemon puree | 0.022 | L | 6.0 | 0.021978 | KG | — | **UOM_MISMATCH** |
| `RAW-LYCHEE-PUREE` | Lychee puree | 0.044 | L | 11.0 | 0.040293 | KG | — | **UOM_MISMATCH** |

### Components in BOM but NOT in Excel recipe

| Component | BOM name | BOM qty | UOM | BOM /L |
|---|---|---:|---|---:|
| `RAW-JASMIN` | Jasmine Green Tea | 12.0 | KG | 0.043956 |
| `PKG-FILTER-100MICRON` | Single Length Filter 100 micron | 1.0 | UNIT | 0.003663 |
| `PKG-FILTER-200MICRON` | Double Length Filter 200 micron | 1.0 | UNIT | 0.003663 |

### Excel rows that could not be mapped to a known component

| Excel name | Vol | UOM guess |
|---|---:|---|
| Jasmine green tea | 24.0 | L |
| single length 100 micron | 1.0 | L |
| double length 200 micron | 1.0 | L |

## Fresh SF — `BOM-BASE-FRE-NS`

- Excel batch (L used): **365.0** (L lines sum 440.0, KG lines sum 0.95)
- BOM declared L: **372.5**

### Paired ingredients (per 1 L of finished base)

| Component | Excel name | Excel /L | UOM | BOM qty | BOM /L | UOM | Δ% | status |
|---|---|---:|---|---:|---:|---|---:|---|
| `RAW-LEMON-ACID` | Lemon acid | 0.002603 | KG | 0.95 | 0.00255 | KG | +2.0% | **CLOSE** |
| `RAW-WATER` | Water | 1.09589 | L | 400.0 | 1.073826 | L | +2.0% | **CLOSE** |
| `RAW-LEMON-PUREE` | Lemon puree | 0.027397 | L | — | — | — | — | **EXCEL_HAS_EXTRA** |

### Components in BOM but NOT in Excel recipe

| Component | BOM name | BOM qty | UOM | BOM /L |
|---|---|---:|---|---:|
| `RAW-HIBISCUS` | Hibiscus | 28.0 | KG | 0.075168 |
| `RAW-LIME-PUREE` | Lime Puree (Ristretto) | 10.0 | KG | 0.026846 |
| `PKG-FILTER-100MICRON` | Single Length Filter 100 micron | 1.0 | UNIT | 0.002685 |
| `PKG-FILTER-200MICRON` | Double Length Filter 200 micron | 1.0 | UNIT | 0.002685 |

### Excel rows that could not be mapped to a known component

| Excel name | Vol | UOM guess |
|---|---:|---|
| Karkade | 28.0 | L |
| single length 100 micron | 1.0 | L |
| double length 200 micron | 1.0 | L |
