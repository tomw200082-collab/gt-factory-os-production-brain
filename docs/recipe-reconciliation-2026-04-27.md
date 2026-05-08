# Recipe Reconciliation — Excel (Aug 2025) vs current BASE BOMs
**Generated:** 2026-04-27
**Excel source:** `cost of production August 2025.xlsx`
**Machine-readable JSON:** `gt-factory-os/fixtures/recipe_reconciliation_report.json`

Methodology: each recipe is paired ingredient-by-ingredient against the matching BASE BOM. The BOM's declared output (in L) is taken as the canonical batch size; Excel ingredient volumes are scaled by `BOM_declared_output_L / Excel_total_L` so the two recipes are compared on the same base. Per-line agreement: MATCH ≤2%, CLOSE ≤10%, DELTA >10%. KG lines are reported but not compared (need density).

## Per-recipe summary

| Sheet | BOM | Decl. (L) | BOM sum L | Excel sum L | Scale | Pairs | match | close | delta | BOM-only | Excel-only | Unmapped |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Cosmo Lychee | `BOM-BASE-COS-LYC-REG` | 409.5 | 403.2 | 647.3 | 0.6326 | 12 | 0 | 0 | 10 | 0 | 3 | 6 |
| Pink Sangria | `BOM-BASE-SAN-PIN-REG` | 50.0 | 50.1 | 58.0 | 0.8621 | 4 | 0 | 0 | 3 | 0 | 0 | 2 |
| White Sangria | `BOM-BASE-SAN-WHI-REG` | 50.0 | 50.1 | 65.0 | 0.7692 | 4 | 0 | 0 | 3 | 0 | 0 | 2 |
| Sangria R Elita | `BOM-BASE-SAN-RED-ELI-REG` | 471.0 | 486.5 | 418.0 | 1.1268 | 8 | 0 | 1 | 6 | 0 | 0 | 2 |
| Sangria W Elita | `BOM-BASE-SAN-WHI-ELI-REG` | 282.0 | 240.4 | 395.0 | 0.7139 | 6 | 0 | 0 | 5 | 1 | 0 | 2 |
| Sangria NM | `BOM-BASE-NM-REG` | 490.0 | 504.73 | 436.01 | 1.1238 | 14 | 0 | 2 | 5 | 3 | 0 | 6 |
| American | `BOM-BASE-AME-REG` | 492.0 | 420.0 | 444.1 | 1.1079 | 8 | 0 | 0 | 1 | 3 | 0 | 5 |
| Desert | `BOM-BASE-DES-REG` | 430.0 | 470.0 | 438.0 | 0.9817 | 12 | 0 | 0 | 1 | 4 | 0 | 6 |
| Detox | `BOM-BASE-DET-REG` | 500.0 | 420.0 | 435.0 | 1.1494 | 5 | 0 | 0 | 1 | 4 | 1 | 6 |
| Energy | `BOM-BASE-ENE-REG` | 453.0 | 420.0 | 433.0 | 1.0462 | 8 | 0 | 1 | 0 | 2 | 0 | 8 |
| Fresh | `BOM-BASE-FRE-REG` | 510.0 | 400.0 | 411.0 | 1.2409 | 4 | 0 | 0 | 1 | 3 | 0 | 7 |
| Calm | `BOM-BASE-CAL-REG` | 394.0 | 420.0 | 217.0 | 1.8157 | 6 | 0 | 1 | 0 | 3 | 1 | 6 |
| Revive | `BOM-BASE-REV-REG` | 521.0 | 420.0 | 453.0 | 1.1501 | 6 | 0 | 0 | 1 | 2 | 0 | 6 |
| Namastea (new) | `BOM-BASE-NAM-REG` | 492.0 | 420.5 | 420.0 | 1.1714 | 8 | 0 | 0 | 2 | 4 | 1 | 9 |
| Detox SF | `BOM-BASE-DET-NS` | 210.0 | 210.0 | 435.0 | 0.4828 | 4 | 0 | 1 | 0 | 4 | 2 | 6 |
| Consciousness | `BOM-BASE-CON-REG` | 273.0 | 200.0 | 433.0 | 0.6305 | 5 | 0 | 0 | 1 | 3 | 1 | 6 |
| Fresh SF | `BOM-BASE-FRE-NS` | 372.5 | 400.0 | 410.0 | 0.9085 | 2 | 0 | 1 | 0 | 4 | 1 | 7 |

## Cosmo Lychee — `BOM-BASE-COS-LYC-REG`

- BOM declared output: **409.5 L**
- BOM component L sum: **403.2 L** (KG sum 1.6 KG)
- Excel total L (classified): **647.3 L**
- Scale factor (BOM/Excel): **0.6326**

| Excel ingredient | Excel vol | scaled→BOM size | BOM line | BOM qty | BOM UOM | Δ% | status |
|---|---:|---:|---|---:|---|---:|---|
| Water | 270.0 | 170.8095 | Water | 144.0 | L | +18.6% | DELTA |
| vodka | 253.0 | 160.0548 | Vodka | 135.0 | L | +18.6% | DELTA |
| Raspberry syrup | 8.0 | 5.061 | Raspberry Syrup | 4.3 | L | +17.7% | DELTA |
| Cranberry puree ODK | 8.0 | 5.061 | ODK Cranberry Puree | 4.3 | L | +17.7% | DELTA |
| Lychee syrup | 45.0 | 28.4683 | Lychee Syrup | 24.0 | L | +18.6% | DELTA |
| Fresh | 140.0 | 88.5679 | BOM-BASE-FRE-REG | 74.7 | L | +18.6% | DELTA |
| Sugar water | 31.0 | 19.6115 | Sugar water | 16.4 | L | +19.6% | DELTA |
| Preservative | 1.0 | 0.6326 | Preservative (Bulk) | 0.5 | L | +26.5% | DELTA |
| Lemon acid | 3.0 | 1.8979 | Lemon acid | 1.6 | KG |  | KG_LINE |
| before bottling | 737.3 |  |  |  |  |  | EXCEL_UNMAPPED |
| 0.3 l bottles | 2457.6666666666665 |  |  |  |  |  | EXCEL_UNMAPPED |
| Water | 10.0 | 6.3263 | Water | 144.0 | L | -95.6% | DELTA |
| Lemon water | 17.5 |  | RAW-LEMON-WATER |  |  |  | EXCEL_HAS_EXTRA |
| Rosetta syrup | 0.5 |  |  |  |  |  | EXCEL_UNMAPPED |
| Apple puree ODK | 7.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| Arak | 25.0 |  | RAW-ARAK |  |  |  | EXCEL_HAS_EXTRA |
| Amaretto | 3.3 |  | RAW-AMARETTO |  |  |  | EXCEL_HAS_EXTRA |
| Preservative | 0.2 | 0.1265 | Preservative (Bulk) | 0.5 | L | -74.7% | DELTA |
| lemon acid | 0.05 | 0.0316 | Lemon acid | 1.6 | KG |  | KG_LINE |
| Energy | 37.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| before bottling | 100.55 |  |  |  |  |  | EXCEL_UNMAPPED |

## Pink Sangria — `BOM-BASE-SAN-PIN-REG`

- BOM declared output: **50.0 L**
- BOM component L sum: **50.1 L** (KG sum 0.11 KG)
- Excel total L (classified): **58.0 L**
- Scale factor (BOM/Excel): **0.8621**

| Excel ingredient | Excel vol | scaled→BOM size | BOM line | BOM qty | BOM UOM | Δ% | status |
|---|---:|---:|---|---:|---|---:|---|
| Wine (white) Symphony | 58.0 | 50.0 | White wine | 29.0 | L | +72.4% | DELTA |
| Fresh | 42.0 | 36.2069 | BOM-BASE-FRE-REG | 21.0 | L | +72.4% | DELTA |
| Preservative | 0.17 | 0.1466 | Preservative (Bulk) | 0.1 | L | +46.5% | DELTA |
| Lemon acid | 0.22 | 0.1897 | Lemon acid | 0.11 | KG |  | KG_LINE |
| before bottling | 100.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| 1 l bottles | 100.0 |  |  |  |  |  | EXCEL_UNMAPPED |

## White Sangria — `BOM-BASE-SAN-WHI-REG`

- BOM declared output: **50.0 L**
- BOM component L sum: **50.1 L** (KG sum 0.24 KG)
- Excel total L (classified): **65.0 L**
- Scale factor (BOM/Excel): **0.7692**

| Excel ingredient | Excel vol | scaled→BOM size | BOM line | BOM qty | BOM UOM | Δ% | status |
|---|---:|---:|---|---:|---|---:|---|
| Wine (white) Symphony | 65.0 | 50.0 | White wine | 32.5 | L | +53.9% | DELTA |
| Calm | 35.0 | 26.9231 | BOM-BASE-CAL-REG | 17.5 | L | +53.9% | DELTA |
| Preservative | 0.19 | 0.1462 | Preservative (Bulk) | 0.1 | L | +46.1% | DELTA |
| Lemon acid | 0.24 | 0.1846 | Lemon acid | 0.24 | KG |  | KG_LINE |
| before bottling | 100.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| 1 l bottles | 100.0 |  |  |  |  |  | EXCEL_UNMAPPED |

## Sangria R Elita — `BOM-BASE-SAN-RED-ELI-REG`

- BOM declared output: **471.0 L**
- BOM component L sum: **486.5 L** (KG sum 14.0 KG)
- Excel total L (classified): **418.0 L**
- Scale factor (BOM/Excel): **1.1268**

| Excel ingredient | Excel vol | scaled→BOM size | BOM line | BOM qty | BOM UOM | Δ% | status |
|---|---:|---:|---|---:|---|---:|---|
| Wine (red) Symphony | 287.0 | 323.39 | Red wine | 287.0 | L | +12.7% | DELTA |
| Orange juice concentrate | 25.0 | 28.1699 | Orange Concentrate | 26.0 | L | +8.3% | CLOSE |
| Water | 90.0 | 101.4115 | Water | 90.0 | L | +12.7% | DELTA |
| Rum | 16.0 | 18.0287 | Rum | 16.0 | L | +12.7% | DELTA |
| Fresh | 38.0 | 42.8182 | BOM-BASE-FRE-REG | 38.0 | L | +12.7% | DELTA |
| Namastea | 29.0 | 32.677 | BOM-BASE-NAM-REG | 29.0 | L | +12.7% | DELTA |
| Preservative | 0.5 | 0.5634 | Preservative (Bulk) | 0.5 | L | +12.7% | DELTA |
| Sugar | 14.0 | 15.7751 | Sugar | 14.0 | KG |  | KG_LINE |
| before bottling | 480.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| 0.75 l bottles | 628.0 |  |  |  |  |  | EXCEL_UNMAPPED |

## Sangria W Elita — `BOM-BASE-SAN-WHI-ELI-REG`

- BOM declared output: **282.0 L**
- BOM component L sum: **240.4 L** (KG sum 0.26 KG)
- Excel total L (classified): **395.0 L**
- Scale factor (BOM/Excel): **0.7139**

| Excel ingredient | Excel vol | scaled→BOM size | BOM line | BOM qty | BOM UOM | Δ% | status |
|---|---:|---:|---|---:|---|---:|---|
| Wine (white) Symphony | 365.0 | 260.5823 | White wine | 192.0 | L | +35.7% | DELTA |
| Martini bianco | 15.0 | 10.7089 | Martini Bianco | 8.0 | L | +33.9% | DELTA |
| Vodka | 15.0 | 10.7089 | Vodka | 8.0 | L | +33.9% | DELTA |
| Elderflower syrup | 30.0 | 21.4177 | ODK Elderflower Syrup | 12.0 | L | +78.5% | DELTA |
| Calm | 75.0 | 53.5443 | BOM-BASE-CAL-REG | 20.0 | L | +167.7% | DELTA |
| Lemon acid | 0.5 | 0.357 | Lemon acid | 0.26 | KG |  | KG_LINE |
| before bottling | 500.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| 0.75 l (white) bottles | 625.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| — |  |  | Preservative (Bulk) | 0.4 | L |  | BOM_HAS_EXTRA |

## Sangria NM — `BOM-BASE-NM-REG`

- BOM declared output: **490.0 L**
- BOM component L sum: **504.73 L** (KG sum 18.92 KG)
- Excel total L (classified): **436.01 L**
- Scale factor (BOM/Excel): **1.1238**

| Excel ingredient | Excel vol | scaled→BOM size | BOM line | BOM qty | BOM UOM | Δ% | status |
|---|---:|---:|---|---:|---|---:|---|
| Wine (red) Symphony | 300.0 | 337.1482 | Red wine | 300.0 | L | +12.4% | DELTA |
| Orange juice concentrate | 25.86 | 29.0622 | Orange Concentrate | 26.0 | L | +11.8% | DELTA |
| Water | 90.51 | 101.7176 | Water | 98.0 | L | +3.8% | CLOSE |
| Amaretto | 12.37 | 13.9017 | Amaretto | 12.73 | L | +9.2% | CLOSE |
| Fresh | 67.5 | 75.8584 | BOM-BASE-FRE-REG | 67.5 | L | +12.4% | DELTA |
| water | 7.27 | 8.1702 | Water | 98.0 | L | -91.7% | DELTA |
| Preservative | 0.5 | 0.5619 | Preservative (Bulk) | 0.5 | L | +12.4% | DELTA |
| Cloves | 0.18 | 0.2023 | Whole Clove | 0.18 | KG |  | KG_LINE |
| Anise | 0.73 | 0.8204 | Anise | 0.73 | KG |  | KG_LINE |
| Black pepper | 0.15 |  |  |  |  |  | EXCEL_UNMAPPED |
| El/Cardamom | 0.18 | 0.2023 | Green Cardamom Pods | 0.18 | KG |  | KG_LINE |
| Cinnamon | 2.55 | 2.8658 | Cinnamon | 2.5 | KG |  | KG_LINE |
| Dried orange | 0.34 | 0.3821 | Dried Orange approx. 30 pcs, 100g | 0.34 | KG |  | KG_LINE |
| Dried lemon | 0.34 | 0.3821 | Dried Lemon approx. 30 pcs, 100g | 0.34 | KG |  | KG_LINE |
| Sugar | 14.55 | 16.3517 | Sugar | 14.5 | KG |  | KG_LINE |
| single length 100 micron | 1.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| double length 200 micron | 1.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| before bottling | 475.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| 1 l bottles | 73.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| jerrican 3.85 l | 102.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| — |  |  | Black Pepper | 0.15 | KG |  | BOM_HAS_EXTRA |
| — |  |  | Single Length Filter 100 micron | 1.0 | UNIT |  | BOM_HAS_EXTRA |
| — |  |  | Double Length Filter 200 micron | 1.0 | UNIT |  | BOM_HAS_EXTRA |

## American — `BOM-BASE-AME-REG`

- BOM declared output: **492.0 L**
- BOM component L sum: **420.0 L** (KG sum 244.3 KG)
- Excel total L (classified): **444.1 L**
- Scale factor (BOM/Excel): **1.1079**

| Excel ingredient | Excel vol | scaled→BOM size | BOM line | BOM qty | BOM UOM | Δ% | status |
|---|---:|---:|---|---:|---|---:|---|
| Water | 420.0 | 465.3006 | Water | 420.0 | L | +10.8% | DELTA |
| Black tea | 18.9 |  |  |  |  |  | EXCEL_UNMAPPED |
| Puer tea | 6.3 | 6.9795 | Puerh Tea | 6.3 | KG |  | KG_LINE |
| Sugar | 160.0 | 177.2574 | Sugar | 189.0 | KG |  | KG_LINE |
| Lime puree | 8.4 | 9.306 | Lime Puree (Ristretto) | 8.4 | KG |  | KG_LINE |
| Lemon puree | 8.4 | 9.306 | Lemon Puree (Ristretto) | 8.4 | KG |  | KG_LINE |
| Yuzu puree | 1.0 | 1.1079 | Yuzu puree | 1.0 | KG |  | KG_LINE |
| Bergamot puree | 6.3 | 6.9795 | Bergamot puree | 6.3 | KG |  | KG_LINE |
| Dried Orange | 6.0 | 6.6472 | Dried Orange approx. 30 pcs, 100g | 6.0 | KG |  | KG_LINE |
| single length 100 micron | 1.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| double length 200 micron | 1.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| before bottling | 500.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| 1 l bottles | 492.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| — |  |  | Black Tea | 18.9 | KG |  | BOM_HAS_EXTRA |
| — |  |  | Single Length Filter 100 micron | 1.0 | UNIT |  | BOM_HAS_EXTRA |
| — |  |  | Double Length Filter 200 micron | 1.0 | UNIT |  | BOM_HAS_EXTRA |

## Desert — `BOM-BASE-DES-REG`

- BOM declared output: **430.0 L**
- BOM component L sum: **470.0 L** (KG sum 239.3 KG)
- Excel total L (classified): **438.0 L**
- Scale factor (BOM/Excel): **0.9817**

| Excel ingredient | Excel vol | scaled→BOM size | BOM line | BOM qty | BOM UOM | Δ% | status |
|---|---:|---:|---|---:|---|---:|---|
| Water | 420.0 | 412.3288 | Water | 470.0 | L | -12.3% | DELTA |
| Louisa | 5.75 |  |  |  |  |  | EXCEL_UNMAPPED |
| Nana | 6.3 | 6.1849 | Spearmint (Nana) | 6.3 | KG |  | KG_LINE |
| Lemon grass | 10.5 | 10.3082 | Lemongrass | 10.5 | KG |  | KG_LINE |
| Melisa | 2.1 | 2.0616 | Lemon Balm (Melissa) | 2.1 | KG |  | KG_LINE |
| Oregano | 2.1 | 2.0616 | Oregano | 2.1 | KG |  | KG_LINE |
| White zuta | 2.1 | 2.0616 | White-Leaved Savory (Zuta) | 2.1 | KG |  | KG_LINE |
| Marva | 2.1 | 2.0616 | Marva | 2.1 | KG |  | KG_LINE |
| menta | 2.1 | 2.0616 | Peppermint (Menta) | 2.1 | KG |  | KG_LINE |
| Sugar | 111.67 | 109.6304 | Sugar | 165.0 | KG |  | KG_LINE |
| Lime puree | 8.0 | 7.8539 | Lime Puree (Ristretto) | 8.0 | KG |  | KG_LINE |
| Lemon puree | 10.0 | 9.8174 | Lemon Puree (Ristretto) | 10.0 | KG |  | KG_LINE |
| Lemon acid | 1.25 | 1.2272 | Lemon acid | 1.25 | KG |  | KG_LINE |
| single length 100 micron | 1.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| double length 200 micron | 1.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| before bottling | 419.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| 1 l bottles new | 450.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| Price per 1 lt bottle | 9.664668 |  |  |  |  |  | EXCEL_UNMAPPED |
| — |  |  | Passion Fruit | 22.0 | KG |  | BOM_HAS_EXTRA |
| — |  |  | Lemon Verbena (Luiza) | 5.75 | KG |  | BOM_HAS_EXTRA |
| — |  |  | Single Length Filter 100 micron | 1.0 | UNIT |  | BOM_HAS_EXTRA |
| — |  |  | Double Length Filter 200 micron | 1.0 | UNIT |  | BOM_HAS_EXTRA |

## Detox — `BOM-BASE-DET-REG`

- BOM declared output: **500.0 L**
- BOM component L sum: **420.0 L** (KG sum 234.05 KG)
- Excel total L (classified): **435.0 L**
- Scale factor (BOM/Excel): **1.1494**

| Excel ingredient | Excel vol | scaled→BOM size | BOM line | BOM qty | BOM UOM | Δ% | status |
|---|---:|---:|---|---:|---|---:|---|
| Water | 420.0 | 482.7586 | Water | 420.0 | L | +14.9% | DELTA |
| Green tea | 11.5 | 13.2184 | Green tea | 11.5 | KG |  | KG_LINE |
| Louisa | 12.5 |  |  |  |  |  | EXCEL_UNMAPPED |
| Nana | 3.5 | 4.023 | Spearmint (Nana) | 3.5 | KG |  | KG_LINE |
| Lemon acid | 1.5 | 1.7241 | Lemon acid | 1.55 | KG |  | KG_LINE |
| Sugar | 180.0 | 206.8966 | Sugar | 190.0 | KG |  | KG_LINE |
| Lime puree | 15.0 |  | RAW-LIME-PUREE |  |  |  | EXCEL_HAS_EXTRA |
| single length 100 micron | 1.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| double length 200 micron | 1.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| before bottling | 515.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| 1 l bottles new | 515.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| Price per 1 lt bottle | 9.733987378640776 |  |  |  |  |  | EXCEL_UNMAPPED |
| — |  |  | Lemon Verbena (Luiza) | 12.5 | KG |  | BOM_HAS_EXTRA |
| — |  |  | Lemon Puree (Ristretto) | 15.0 | KG |  | BOM_HAS_EXTRA |
| — |  |  | Single Length Filter 100 micron | 1.0 | UNIT |  | BOM_HAS_EXTRA |
| — |  |  | Double Length Filter 200 micron | 1.0 | UNIT |  | BOM_HAS_EXTRA |

## Energy — `BOM-BASE-ENE-REG`

- BOM declared output: **453.0 L**
- BOM component L sum: **420.0 L** (KG sum 227.7 KG)
- Excel total L (classified): **433.0 L**
- Scale factor (BOM/Excel): **1.0462**

| Excel ingredient | Excel vol | scaled→BOM size | BOM line | BOM qty | BOM UOM | Δ% | status |
|---|---:|---:|---|---:|---|---:|---|
| water | 420.0 | 439.3995 | Water | 420.0 | L | +4.6% | CLOSE |
| green tea | 25.2 | 26.364 | Green tea | 25.0 | KG |  | KG_LINE |
| menta | 1.7 | 1.7785 | Peppermint (Menta) | 1.7 | KG |  | KG_LINE |
| lemon grass | 10.5 | 10.985 | Lemongrass | 5.5 | KG |  | KG_LINE |
| Nana | 4.2 | 4.394 | Spearmint (Nana) | 4.0 | KG |  | KG_LINE |
| lemon acid | 1.4 | 1.4647 | Lemon acid | 1.5 | KG |  | KG_LINE |
| lemon puree | 13.0 | 13.6005 | Lemon Puree (Ristretto) | 15.0 | KG |  | KG_LINE |
| sugar | 170.0 | 177.8522 | Sugar | 175.0 | KG |  | KG_LINE |
| single length 100 micron | 1.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| double length 200 micron | 1.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| before bottling | 460.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| 1 l bottles | 97.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| 0.5 l bottles | 672.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| jerrican 20 l | 1.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| jerrican 23 l | 0.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| Price per 1 lt bottle | 11.706070640176602 |  |  |  |  |  | EXCEL_UNMAPPED |
| — |  |  | Single Length Filter 100 micron | 1.0 | UNIT |  | BOM_HAS_EXTRA |
| — |  |  | Double Length Filter 200 micron | 1.0 | UNIT |  | BOM_HAS_EXTRA |

## Fresh — `BOM-BASE-FRE-REG`

- BOM declared output: **510.0 L**
- BOM component L sum: **400.0 L** (KG sum 216.95 KG)
- Excel total L (classified): **411.0 L**
- Scale factor (BOM/Excel): **1.2409**

| Excel ingredient | Excel vol | scaled→BOM size | BOM line | BOM qty | BOM UOM | Δ% | status |
|---|---:|---:|---|---:|---|---:|---|
| water | 400.0 | 496.3504 | Water | 400.0 | L | +24.1% | DELTA |
| karkade | 28.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| lemon acid | 1.0 | 1.2409 | Lemon acid | 0.95 | KG |  | KG_LINE |
| lime puree | 11.0 | 13.6496 | Lime Puree (Ristretto) | 10.0 | KG |  | KG_LINE |
| sugar | 175.0 | 217.1533 | Sugar | 178.0 | KG |  | KG_LINE |
| single length 100 micron | 1.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| double length 200 micron | 1.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| before bottling | 470.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| 1 l bottles | 424.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| jerrican 23 l | 2.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| Price per 1 lt bottle | 8.563191489361703 |  |  |  |  |  | EXCEL_UNMAPPED |
| — |  |  | Hibiscus | 28.0 | KG |  | BOM_HAS_EXTRA |
| — |  |  | Single Length Filter 100 micron | 1.0 | UNIT |  | BOM_HAS_EXTRA |
| — |  |  | Double Length Filter 200 micron | 1.0 | UNIT |  | BOM_HAS_EXTRA |

## Calm — `BOM-BASE-CAL-REG`

- BOM declared output: **394.0 L**
- BOM component L sum: **420.0 L** (KG sum 234.1 KG)
- Excel total L (classified): **217.0 L**
- Scale factor (BOM/Excel): **1.8157**

| Excel ingredient | Excel vol | scaled→BOM size | BOM line | BOM qty | BOM UOM | Δ% | status |
|---|---:|---:|---|---:|---|---:|---|
| water | 210.0 | 381.2903 | Water | 420.0 | L | -9.2% | CLOSE |
| Dried apple | 12.5 | 22.6959 | Dried Apple 300g | 25.0 | KG |  | KG_LINE |
| camomile | 9.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| lemon puree | 5.0 | 9.0783 | Lemon Puree (Ristretto) | 14.0 | KG |  | KG_LINE |
| Lime puree | 2.0 |  | RAW-LIME-PUREE |  |  |  | EXCEL_HAS_EXTRA |
| lemon acid | 0.725 | 1.3164 | Lemon acid | 1.1 | KG |  | KG_LINE |
| cloves | 0.5 | 0.9078 | Whole Clove | 1.0 | KG |  | KG_LINE |
| sugar | 75.0 | 136.1751 | Sugar | 175.0 | KG |  | KG_LINE |
| single length 100 micron | 1.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| double length 200 micron | 1.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| before bottling | 175.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| 1 l bottles | 169.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| Price per 1 lt bottle | 11.118934911242604 |  |  |  |  |  | EXCEL_UNMAPPED |
| — |  |  | Chamomile | 18.0 | KG |  | BOM_HAS_EXTRA |
| — |  |  | Single Length Filter 100 micron | 1.0 | UNIT |  | BOM_HAS_EXTRA |
| — |  |  | Double Length Filter 200 micron | 1.0 | UNIT |  | BOM_HAS_EXTRA |

## Revive — `BOM-BASE-REV-REG`

- BOM declared output: **521.0 L**
- BOM component L sum: **420.0 L** (KG sum 246.0 KG)
- Excel total L (classified): **453.0 L**
- Scale factor (BOM/Excel): **1.1501**

| Excel ingredient | Excel vol | scaled→BOM size | BOM line | BOM qty | BOM UOM | Δ% | status |
|---|---:|---:|---|---:|---|---:|---|
| Water | 420.0 | 483.0464 | Water | 420.0 | L | +15.0% | DELTA |
| Sencha tea | 27.0 | 31.053 | Sencha Tea | 27.0 | KG |  | KG_LINE |
| Passion fruit puree | 22.0 | 25.3024 | Passion Fruit | 22.0 | KG |  | KG_LINE |
| Lemon puree | 11.0 | 12.6512 | Lemon Puree (Ristretto) | 11.0 | KG |  | KG_LINE |
| Lemon acid | 1.0 | 1.1501 | Lemon acid | 1.0 | KG |  | KG_LINE |
| Sugar | 187.5 | 215.6457 | Sugar | 185.0 | KG |  | KG_LINE |
| single length 100 micron | 1.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| double length 200 micron | 1.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| before bottling | 500.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| 1 l bottles | 400.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| jerrican 23 l | 46.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| Price per 1 lt bottle | 12.812995515695068 |  |  |  |  |  | EXCEL_UNMAPPED |
| — |  |  | Single Length Filter 100 micron | 1.0 | UNIT |  | BOM_HAS_EXTRA |
| — |  |  | Double Length Filter 200 micron | 1.0 | UNIT |  | BOM_HAS_EXTRA |

## Namastea (new) — `BOM-BASE-NAM-REG`

- BOM declared output: **492.0 L**
- BOM component L sum: **420.5 L** (KG sum 178.6 KG)
- Excel total L (classified): **420.0 L**
- Scale factor (BOM/Excel): **1.1714**

| Excel ingredient | Excel vol | scaled→BOM size | BOM line | BOM qty | BOM UOM | Δ% | status |
|---|---:|---:|---|---:|---|---:|---|
| Water | 420.0 | 492.0 | Water | 420.0 | L | +17.1% | DELTA |
| Cloves | 2.9 | 3.3971 | Whole Clove | 1.0 | KG |  | KG_LINE |
| Black pepper | 2.4 |  |  |  |  |  | EXCEL_UNMAPPED |
| El/Cardamom | 2.21 | 2.5889 | Green Cardamom Pods | 0.5 | KG |  | KG_LINE |
| Crushed ginger | 0.95 |  | RAW-GIN |  |  |  | EXCEL_HAS_EXTRA |
| Crushed cinnamon | 13.54 | 15.8611 | Cinnamon | 1.0 | KG |  | KG_LINE |
| Black tea | 6.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| Puer tea | 4.0 | 4.6857 | Puerh Tea | 0.5 | KG |  | KG_LINE |
| Sugar | 150.0 | 175.7143 | Sugar | 150.0 | KG |  | KG_LINE |
| Preservative | 0.5 | 0.5857 | Preservative (Bulk) | 0.5 | L | +17.1% | DELTA |
| Stabilizer | 0.1 | 0.1171 | Stabilizer | 0.1 | KG |  | KG_LINE |
| single length 100 micron | 1.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| double length 200 micron | 1.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| before bottling | 480.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| 1 l bottles new | 480.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| Price per litre w/o package | 4.2635 |  |  |  |  |  | EXCEL_UNMAPPED |
| Price per 1 lt bottle | 8.9504 |  |  |  |  |  | EXCEL_UNMAPPED |
| Price per 500 ml bottle | 6.2034166666666675 |  |  |  |  |  | EXCEL_UNMAPPED |
| — |  |  | Chai Masala | 25.0 | KG |  | BOM_HAS_EXTRA |
| — |  |  | Black Pepper | 0.5 | KG |  | BOM_HAS_EXTRA |
| — |  |  | Single Length Filter 100 micron | 1.0 | UNIT |  | BOM_HAS_EXTRA |
| — |  |  | Double Length Filter 200 micron | 1.0 | UNIT |  | BOM_HAS_EXTRA |

## Detox SF — `BOM-BASE-DET-NS`

- BOM declared output: **210.0 L**
- BOM component L sum: **210.0 L** (KG sum 22.0 KG)
- Excel total L (classified): **435.0 L**
- Scale factor (BOM/Excel): **0.4828**

| Excel ingredient | Excel vol | scaled→BOM size | BOM line | BOM qty | BOM UOM | Δ% | status |
|---|---:|---:|---|---:|---|---:|---|
| Water | 420.0 | 202.7586 | Water | 210.0 | L | -3.5% | CLOSE |
| Green tea | 11.5 | 5.5517 | Green tea | 6.0 | KG |  | KG_LINE |
| Louisa | 12.5 |  |  |  |  |  | EXCEL_UNMAPPED |
| Nana | 3.5 | 1.6897 | Spearmint (Nana) | 1.75 | KG |  | KG_LINE |
| Lemon acid | 1.5 | 0.7241 | Lemon acid | 0.75 | KG |  | KG_LINE |
| Sugar | 0.0 |  | RAW-SUGAR |  |  |  | EXCEL_HAS_EXTRA |
| Lime puree | 15.0 |  | RAW-LIME-PUREE |  |  |  | EXCEL_HAS_EXTRA |
| single length 100 micron | 1.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| double length 200 micron | 1.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| before bottling | 385.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| 1 l bottles | 375.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| Price per 1 lt bottle | 10.335333333333335 |  |  |  |  |  | EXCEL_UNMAPPED |
| — |  |  | Lemon Verbena (Luiza) | 6.0 | KG |  | BOM_HAS_EXTRA |
| — |  |  | Lemon Puree (Ristretto) | 7.5 | KG |  | BOM_HAS_EXTRA |
| — |  |  | Single Length Filter 100 micron | 1.0 | UNIT |  | BOM_HAS_EXTRA |
| — |  |  | Double Length Filter 200 micron | 1.0 | UNIT |  | BOM_HAS_EXTRA |

## Consciousness — `BOM-BASE-CON-REG`

- BOM declared output: **273.0 L**
- BOM component L sum: **200.0 L** (KG sum 116.75 KG)
- Excel total L (classified): **433.0 L**
- Scale factor (BOM/Excel): **0.6305**

| Excel ingredient | Excel vol | scaled→BOM size | BOM line | BOM qty | BOM UOM | Δ% | status |
|---|---:|---:|---|---:|---|---:|---|
| Water | 400.0 | 252.194 | Water | 200.0 | L | +26.1% | DELTA |
| Jasmine green tea | 24.0 |  | RAW-GREEN-TEA |  |  |  | EXCEL_HAS_EXTRA |
| Lychee puree | 22.0 | 13.8707 | Lychee puree | 11.0 | KG |  | KG_LINE |
| Lemon puree | 11.0 | 6.9353 | Lemon Puree (Ristretto) | 6.0 | KG |  | KG_LINE |
| Lemon acid | 1.1 | 0.6935 | Lemon acid | 0.75 | KG |  | KG_LINE |
| Sugar | 175.0 | 110.3349 | Sugar | 87.0 | KG |  | KG_LINE |
| single length 100 micron | 1.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| double length 200 micron | 1.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| before bottling | 500.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| 1 l bottles | 420.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| 0.5 l bottles | 153.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| Price per 1 lt bottle | 11.347079556898288 |  |  |  |  |  | EXCEL_UNMAPPED |
| — |  |  | Jasmine Green Tea | 12.0 | KG |  | BOM_HAS_EXTRA |
| — |  |  | Single Length Filter 100 micron | 1.0 | UNIT |  | BOM_HAS_EXTRA |
| — |  |  | Double Length Filter 200 micron | 1.0 | UNIT |  | BOM_HAS_EXTRA |

## Fresh SF — `BOM-BASE-FRE-NS`

- BOM declared output: **372.5 L**
- BOM component L sum: **400.0 L** (KG sum 38.95 KG)
- Excel total L (classified): **410.0 L**
- Scale factor (BOM/Excel): **0.9085**

| Excel ingredient | Excel vol | scaled→BOM size | BOM line | BOM qty | BOM UOM | Δ% | status |
|---|---:|---:|---|---:|---|---:|---|
| Water | 400.0 | 363.4146 | Water | 400.0 | L | -9.2% | CLOSE |
| Karkade | 28.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| Lemon puree | 10.0 |  | RAW-LEMON-PUREE |  |  |  | EXCEL_HAS_EXTRA |
| Lemon acid | 0.95 | 0.8631 | Lemon acid | 0.95 | KG |  | KG_LINE |
| single length 100 micron | 1.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| double length 200 micron | 1.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| before bottling | 365.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| 1 l bottles | 240.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| 0.5 l bottles | 259.0 |  |  |  |  |  | EXCEL_UNMAPPED |
| Price per 1 lt bottle | 9.06082543978349 |  |  |  |  |  | EXCEL_UNMAPPED |
| — |  |  | Hibiscus | 28.0 | KG |  | BOM_HAS_EXTRA |
| — |  |  | Lime Puree (Ristretto) | 10.0 | KG |  | BOM_HAS_EXTRA |
| — |  |  | Single Length Filter 100 micron | 1.0 | UNIT |  | BOM_HAS_EXTRA |
| — |  |  | Double Length Filter 200 micron | 1.0 | UNIT |  | BOM_HAS_EXTRA |

## Sheets with no matching BOM

- **Almond joy (Migd)** — 7 ingredients, BOM ref: `None`
- **Lady Sandy (Migd)** — 9 ingredients, BOM ref: `None`
- **Friling (Migdaler)** — 9 ingredients, BOM ref: `None`
- **Namastea (old)** — 13 ingredients, BOM ref: `None`
