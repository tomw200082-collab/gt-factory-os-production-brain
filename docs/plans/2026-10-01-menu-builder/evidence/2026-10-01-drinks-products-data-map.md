# Evidence — where the drink and product data actually lives (read-only check, 2026-10-01)

> Read-only reconstruction by a Session 1 exploration agent, verbatim in substance; repos on `main` only, no live Shopify/DB/Canva query. "Brain" = `gt-factory-os-production-brain`. Authority: `system_verified` where a file:line is cited; the figures are **estimates** by the file's own `_meta.status`.

## 0. Bottom line

1. **One file is the authority for drink economics:** brain `.claude/skills/drinks-pricelist/drinks_final_figures.json`, `_meta.date: "2026-09-29"` (commit `283566b`, Tom Witt, "Sync GT ice-aware beverage pricing and workbook"). `docs/pricing/2026-09-29_cost_model.py` reproduces all 48 costs exactly; `docs/pricing/GT_FOOD_COST_2026-09-29.xlsx` matches all 48 cost/price pairs. `_meta.status`: *"estimated ingredient cost based on a standardized ice-filled serving"*.
2. **Every copy downstream of that file is stale:** Sales-Machine cards, the gt-site copy, the site's drink data and the drive-pack hold the 2026-08-27 figures; the English site holds 2026-08-05 figures. 38 of 48 drinks differ from the current file. `scripts/knowledge/reconcile.py:52-53` and `build_drinks_card.py:63-64` only accept a figures file dated `2026-08-27`.
3. **No structured list says which GT SKU each drink uses.** Sales-Machine cards only say `base: tea_concentrate | tea_concentrate (NAMASTEA) | powder`. The only per-flavour mapping is inside recipe text: gt-site `tools/landing-pages/drinks.json` `steps` (e.g. "הוסיפו 50 מ״ל תמצית Fresh") and brain `docs/pricing/canva_workfiles/recipes.json` `eng` slugs.
4. **gt-factory-os models factory production only.** BOMs go from a factory base mix (e.g. `BOM-BASE-FRE-REG`, 510 L) to a packed bottle. None of the 342 migrations has a table or column for drinks, servings, ml per serving, RRP or café food cost. Only `items.base_fill_qty_per_unit` (1 or 0.5 L).
5. **What GT sells:** brain `docs/warehouses/catalog-truth.md` (40 sellable SKUs + 4 "not sold"); prices from the TSV snapshot `docs/pricing/2026-08-05_shopify_products_exvat.tsv` (ex-VAT); at runtime the portal prices live from Shopify (`api/src/portal/pricing.ts`).
6. **Ordering rules exist only in code:** pairs for tea 1 L, tea 500 ml, ODK (`catalog.ts:63-64`); ₪800 ex-VAT minimum (`build-cart.ts:21`); 8 SKUs never shown (`catalog.ts:57-60`); carton of 6 (`items.case_pack`, portal "+6 · ארגז", not enforced).
7. **No rule yet covers what a self-serve screen may show:** D-018 (never state food cost / opening price) vs D-025 (menus print FOOD COST) vs `show_prices:false` on the site vs U-047 (margin % reveals cost).

## A. Drinks — sources

| # | Path | Shape | Date | Status |
|---|---|---|---|---|
| S1 | brain `.claude/skills/drinks-pricelist/drinks_final_figures.json` | `pages{"8"…"64"}` × 48: `name, cost:"₪3.25", price:"₪20", marg:"81%", prof:"₪13.70 לכוס", star:false`; `_meta{design_id:"DAHTYkRvEnM", vat_rate:0.18, formulas, labels, assumptions{cup_ml:350, milk_base_ml:145, matcha_masala_milk_ml:120, coconut_water_ml:110, tonic_ml:120, orange_juice_ml:145, milk_ils_per_l_exvat_reference:5.43, cream_38…:25.9}}` | 2026-09-29 | **CANONICAL** |
| S2 | brain `docs/pricing/2026-09-29_cost_model.py` | `M[name]=(cost,[(item,₪)])`, 48 drinks | 2026-09-29 | **CANONICAL** (how S1 is computed) |
| S3 | brain `docs/pricing/GT_FOOD_COST_2026-09-29.xlsx` | sheet `FOOD COST` rows 5–52: `# · משפחה · משקה · FOOD COST ללא מע״מ · מחיר מומלץ כולל מע״מ · מחיר ללא מע״מ · רווח לכוס · מרווח % · פירוט עלות`; sheet `מחירון רכיבים` | 2026-09-29 | **CANONICAL** (per-drink doses) |
| S4 | Sales-Machine `knowledge/drinks/catalog.yaml` | 48 × `canva_page, name, category, family, cost, price, margin_pct, profit_per_cup, base, …` | 2026-08-27, `review_30d` (overdue since 2026-09-26) | **DEPRECATED** (stale) |
| S5 | Sales-Machine `knowledge/drinks/recipes.yaml` ("the 48 recipes") | 48 × `doses[{item,cost}], doses_total, approved_cost, serve[]` | doses 2026-08-27; serve 2026-08-05 | doses **DEPRECATED**; serve text **DERIVED** |
| S6 | gt-site `tools/landing-pages/drinks.json` + `catalog.py` | 48 × `he, en, group, page, family, steps[], note, cost, price, marg` | figures 08-27; transcribed from Canva 08-31 | steps **DERIVED**; figures **DEPRECATED** |
| S7 | gt-site `theme/assets/gt-site.js` `COLS` (Hebrew) and `src/index.en.html:1488` (English) | 10 families × drinks `en, he, d, st, ing, m` | Hebrew margins 08-27; English 08-05 | **DEPRECATED** figures |
| S8 | gt-site `tools/landing-pages/photos.json` | Hebrew name → Canva id; images `https://cdn.shopify.com/s/files/1/0484/4319/5552/files/gtd-<id>.webp` 925×1052 | 2026-09-02/03 | **DERIVED** (the only drink image source) |
| S9 | brain `docs/pricing/canva_workfiles/recipes.json` | 48 × `pg, fam, heb, eng, cost, price, chips` | 2026-08-05 | **DEPRECATED** figures |
| S10 | brain `docs/pricing/2026-08-05_drinks_final_figures.json` | list-shaped | 2026-08-05 | **DEPRECATED** (CL-1) |
| S11 | brain `docs/pricing/2026-08-27_*` | — | 2026-08-27 | **DEPRECATED** (superseded) |
| S12 | Canva `DAHTYkRvEnM` (60-page main database); five final lead menus in folder `FAHWjugERyQ`; opening menu `DAHTY5nfDxo`; `DAHPi9gpfts` (64 pages) retired | external | Canonical for printed preparation steps; not in any repo |

Field map: Hebrew name S1 (48/48, names drift C9); English name **none canonical**; category/family S4 + `build.py:32-43` FAMILIES (S1 has none); GT product(s) S6 `steps` / S9 `eng` only; dose per cup S3/S2 (concentrate 50 ml in 21 drinks, 40 ml in 8; matcha 1.8 g; ube 2 g; purée 40 ml); cup 350 ml (one global assumption); yield per bottle not stored per drink (per SKU `servings_per_unit` in Sales-Machine `knowledge/products/catalog.yaml`); other ingredients S3/S2 (milk 145 ml, 120 in matcha masala; milk foam 70 ml; lemonade 145 ml; coconut water 110 ml; coconut-cream foam 70 ml; tonic 120 ml; orange juice 145 ml; apple juice 40 ml; lychee water 40 ml; agave 15 ml; espresso 1 shot; flat-cost flavours) — ice, water, soda, garnish not costed; food cost S1 `cost` (ex-VAT, ingredients only, estimate); RRP S1 `price` (incl. 18% VAT); margin/profit S1 (formula); image S8 only; season none (whole set "SUMMER 2026", all cold); authority/freshness only on S4/S5.

Completeness (S1): 48 drinks, 10 families, all cold; economics complete 48/48; 9 drinks carry flat flavour add-ins without quantity (vanilla ₪0.30, pistachio ₪1.20, black sesame ₪0.80, coffee ₪1.00, banana ₪0.50; p36–40, p50, p55, p56, p58); milk/cream prices "not verified wholesale invoices"; pours "await real cup measurement". Ranges now: cost ₪2.88–5.82, price ₪20–32, margin 78–86% (08-27: ₪2.85–6.86, ₪20–44, 76–87%). Unchanged since 08-27: p8–14, p23, p25, p27; 38 changed (24 price cuts, no raises).

| Family (page keys) | n | Cost ₪ ex-VAT | Price ₪ incl. VAT | Margin |
|---|---|---|---|---|
| 01 Iced tea (8–14) | 7 | 3.25 | 20 | 81% |
| 02 Lemonade (16–18) | 3 | 3.69 | 20 | 78% |
| 03 Signature (20–23) | 4 | 5.00 ×3; 2.88 | 27 ×3; 24 | 78%; 86% |
| 04 Gazoz (25–27) | 3 | 3.08; 5.00; 2.88 | 25; 27; 22 | 85; 78; 85% |
| 05 Iced matcha (29–34) | 6 | 3.35; 5.75 ×3; 5.82; 3.01 | 26; 31 ×3; 32; 26 | 85; 78; 79; 86% |
| 06 Matcha specials (36–40) | 5 | 3.65–4.55 | 28–29 | 81–85% |
| 07 Matcha coconut (42–46) | 5 | 3.82; 3.85; 5.77 ×3 | 29; 29; 31 ×3 | 84; 84; 78% |
| 08 Chai masala (48–53) | 6 | 3.69–5.48 | 24–30 | 78–82% |
| 09 Cold foam (55–58) | 4 | 3.99–4.89 | 28–29 | 80–83% |
| 10 Ube (60–64) | 5 | 4.03–5.16 | 27–29 | 79–83% |

Drink → GT product, derived from S6 `steps` (matches S9 `eng`): FRESH `GT-HIB-LOW-*` 8:50, 16:50, 23:40, 27:40 · CALM `GT-CHA-LOW-*` 9:50 · DESERTEA `GT-INF-DES-*` 10:50, 17:50, 20:40, 26:40 · REVIVE `GT-SEN-LOW-*` 11:50, 22:40 · DETOX `GT-LUI-LOW-*` 12:50, 21:40 · ENERGY `GT-LEM-LOW-*` 13:50 · CONSCIOUSNESS `GT-JAS-LOW-*` 14:50, 25:40 · NAMASTEA `GT-MAS-CHA-*` 18, 48–53, 55–58, 63 at 50 ml, 33 at 40 ml (13) · MATCHA `GT-SHI-CER-500` / `-18*22` 29–34, 36–40, 42–46, 64 at 1.8 g (17) · UBE `UBE-POWDER-*` 60–64 at 2 g (5) · ODK mango 22, 30, 45, 61 · strawberry 21, 31, 44, 60 · peach 20, 26, 32, 46, 62 (40 ml) · AMERICAN, HOJICHA, sugar-free FRESH/DETOX: none. **32 drinks need one GT product, 16 need two.**

## B. The `drinks-pricelist` skill

Only copy: brain `.claude/skills/drinks-pricelist/` (`SKILL.md`, `drinks_final_figures.json`, `foodcost_proposal.csv`, `build.py`, `shot.py`, `style.css`, `validate.py`, `check_menu.py`). Chain: Tom's `GT_Summer_Menu_2026.xls` (in no repo) → 08-27 model → 09-29 ice-aware model. 09-29 ingredient prices (`מחירון רכיבים`): concentrate ₪65/L, ODK ₪60/L, matcha ₪1,180/kg (₪590/500 g), ube ₪340/kg; milk ₪5.43/L (retail ÷1.18, no invoice), cream 38% ₪25.90/L, lemonade ₪3/L, coconut cream ₪14/L, coconut water ₪10/L, tonic ₪1.20/120 ml, orange juice ₪1.93/145 ml, apple juice ₪7/L, lychee water ₪12/L, agave ₪30/L, espresso ₪1.00, milk foam ₪6.30/L (whipping doubles volume), coconut foam ₪2.10/L. Prices set by a 78% margin floor, cut never raised (rule only in the candidate doc). Formulas: `profit = price/1.18 − cost`; `margin_pct = round((price/1.18 − cost)/(price/1.18)×100)`; FOOD COST ex-VAT; RRP incl. 18% VAT; never use CSV `שוליים מוצע` (overstates 2–5 pts). Drift inside the skill: `SKILL.md:40-44` names `DAHPi9gpfts`; S1 `_meta.design_id` is `DAHTYkRvEnM`; page keys 8–64 are old `DAHPi9gpfts` page numbers usable as IDs only; `validate.py` expects 44 asterisks and `LEGAL_PRICES {₪19,₪22,₪24,₪26,₪28}`; `build.py:65-68` stops on mixed family prices (8 of 10 families mixed) so the "מה נשאר לך מכל כוס" PDF cannot be regenerated as written.

## C. Products GT sells

Sources: brain `docs/warehouses/catalog-truth.md` (teas lines 8–22, powders 24–34, purées 36–42, accessories 44–55, "not sold" 57–64) + `docs/pricing/2026-08-05_shopify_products_exvat.tsv` (121 rows, `sku, title, type, price_ils_exvat`, edits 08-30/31). Teas 11 flavours (FRESH `GT-HIB-LOW`, FRESH SF `GT-HIB-FRE`, DETOX `GT-LUI-LOW`, DETOX SF `GT-LUI-FRE`, ENERGY `GT-LEM-LOW`, CALM `GT-CHA-LOW`, CONSCIOUSNESS `GT-JAS-LOW`, REVIVE `GT-SEN-LOW`, DESERTEA `GT-INF-DES`, NAMASTEA `GT-MAS-CHA`, AMERICAN `GT-AME-LOW`) `-1L` ₪65 / `-0.5L` ₪33; yield 20 / 10 servings of 50 ml (₪3.25 / ₪3.30). Matcha 500 g `GT-SHI-CER-500` ₪590 (277 × 1.8 g, ₪2.13); 22 sachets × 18 g `GT-SHI-CER-18*22` ₪590 (one Shopify unit = carton of 22, migration 0263). Hojicha `GT-HOJ-BLK-500` ₪375 / `-1000` ₪750 (no recipes). Ube `UBE-POWDER-0.5-KG` ₪175 / `-1-KG` ₪340 (250 / 500 × 2 g, ₪0.70 / ₪0.68). Matcha kit `GT-MAT-KIT` ₪170 (contents unrecorded). ODK 1 L mango/strawberry/peach `GT-ODK-MAN-1`, `-STR-1`, `-PEA-1` ₪60 (25 × 40 ml, ₪2.40). Accessories `AP-BWL-MAT` 118, `AP-FRO-MAT` 100, `AP-WHK-MAT` 37, `AP-CUP-MAT-600` 30, `AP-STA-MAT` 25, `GT-GLA-CUP` 20, `AP-SCO-MAT` 11, `GT-MAT-BTL-RU` 10. Not sold: `GT-SHI-CER-30` (38), `GT-SHI-CER-50` (65), `GTCFR-GTCOC-FRO` (75), `AP-JUG-NEA` (36); the four 0.3 L teas ₪13.50 special-order only. Product attributes (`ingredients_he`, `caffeine_free`, `sugar`, `requires_equipment`, `requires_second_product`, `customer_facing`) in Sales-Machine `knowledge/products/catalog.yaml` (48 entries, `doc_confirmed`).

## D. gt-factory-os BOM model — factory only

`private_core.bom_head` (`bom_kind ∈ {BASE, PACK, REPACK}`, `pack_size`, `final_bom_output_qty/uom`, `production_track`), `bom_version`, `bom_lines` (`component_ref_type, final_component_id, final_component_qty, component_uom, scaling_method, qty_per_l_output, std_cost_per_uom`). Example `BOM-PACK-FRE-1L` = `BASE_BOM BOM-BASE-FRE-REG` (510 L) + bottle + cap + label + carton. `plan-recipe`, `cogs`, `economics`, `v_fg_unit_economics` (0283) are GT's internal cost/margin per bottle — never customer-facing. No serving-side data anywhere.

## E. items, SKU map, portal catalog

`private_core.items` (0002:59 + 0149/0207/0231/0255): `item_id, item_name (English), family, pack_size, sales_uom, sweetness, supply_method, item_type, status, barcode, legacy_sku, shelf_life_days, storage, case_pack, primary_bom_head_id, base_bom_head_id, base_fill_qty_per_unit, sub_type, product_group, notes, site_id, is_stock_managed, manual_avg_sale_price_ils, product_group_key, fg_twin_item_id`; **missing** Hebrew name, image, order multiple, pairs flag; `items.sku` used in prod but no DDL in the repo — do not join on it; internal IDs ≠ Shopify SKUs (`FG-FRE-1L` vs `GT-HIB-LOW-1L`). `integration_sku_map` (0033/0149): `source_channel ∈ {lionwheel, shopify, green_invoice}, external_sku, item_id, approval_status, mapping_status, internal_units_per_shopify_unit`, unique `(source_channel, external_sku)`; no variant id, no price — the only valid Shopify SKU ↔ item link. Portal catalog: no DB view; `api/src/portal/catalog.ts` 40 entries keyed `<page id>:<variant>` → SKU, category `tea|matcha|odk|acc`, family `TEA_1L|TEA_05|ODK_1L`; availability `customer_portal.item_availability_current`; on-hand via `integration_sku_map` → `private_core.current_balances` (`store.ts:356-364`); display data in `index.html:645-690` (names, colours, images `img/l-<id>`, `h-<id>`, `p-matcha|hojicha|ube`, `o-mango|strawberry|peach`, `a-<accessory>`, `INGR`, `ALIAS`).

## F. Shopify as a data source

Prices never stored in the DB: `pricing.ts` reads live (variants cached 10 min; per-customer snapshot 5 min); rule (Tom 2026-09-24): family SKU → customer's last paid family price; other SKU → own last paid; else list `variant.price`; leads list prices, drafts only. Local caches: `private_core.shopify_sales_90d` (internal), `order-intake/config/lexicon.json` prices/barcodes (reference only, verified 2026-06-15/27). Images: no backend reads Shopify product images; drink photos are Shopify **Files** (`gtd-*.webp`) uploaded by gt-site tooling; bottle images are static portal files; the rest are Dropbox paths in brain `docs/warehouses/marketing-assets.md`. VAT: TSV header "configured taxesIncluded=true at 17% — WRONG"; stored numbers are ex-VAT (Tom 2026-08-05).

## G. gt-site data

`data/drinks_final_figures.json` = S1 copy dated 2026-08-27 (sha256 `5d38f6…`; brain now `937946…`; `provenance.json` synced 2026-08-31). `data/site_flags.json` `show_prices:false` (Tom 2026-09-24). `tools/landing-pages/{drinks.json, catalog.py, photos.json, bottles.json (11 bottle colours, Canva folder FAHUB2UNItA), seo.json}`. Live theme `166730072305` pushed 2026-09-29 at `73c302e` carries 08-27 margins.

## H. Spreadsheets

CANONICAL: `GT_FOOD_COST_2026-09-29.xlsx`; `2026-08-05_shopify_products_exvat.tsv` (dated list-price snapshot). DEPRECATED: `GT_FOOD_COST_2026-08-27.xlsx`, `2026-08-05_foodcost_correction.csv` (= skill `foodcost_proposal.csv`, wrong margin column), `2026-08-05_foodcost_audit_raw.csv`. Not recipe data: `docs/analytics/customer-product-tracker-2026-08-06.xlsx`. `GT_Summer_Menu_2026.xls` in no repo.

## 1. Classification

| Data element | Source | Status |
|---|---|---|
| Drink list and stable ID | S1 page keys "8"…"64" (retired `DAHPi9gpfts` page numbers; names are not safe join keys) | CANONICAL |
| Food cost per cup | S1 `cost` via S2/S3 | CANONICAL (estimate) |
| Recommended price incl. VAT | S1 `price` (≥78% margin rule, candidate doc only) | CANONICAL |
| Margin %, profit per cup | S1 `marg`, `prof` | DERIVED |
| Per-drink doses | S3 `פירוט עלות` / S2 (pours unmeasured) | CANONICAL |
| Preparation steps | Canva `DAHTYkRvEnM`; S6 / S5 `serve` transcriptions | CANONICAL external / DERIVED |
| Drink → GT SKU | none; derived from S6 / S9 | UNKNOWN / DERIVED |
| Category / family | S4 / `build.py` FAMILIES | DERIVED (five taxonomies, C19) |
| Cup size | `assumptions.cup_ml: 350` | DERIVED (assumption) |
| Yield per pack | products card `servings_per_unit` (`doc_confirmed`; 22×18 g, hojicha, kit null) | DERIVED |
| Drink images | S8 | DERIVED |
| English drink names | — | UNKNOWN |
| What is sold | `catalog-truth.md`; mirrored in `catalog.ts` | CANONICAL |
| List price ex-VAT | Shopify `variant.price` live; TSV snapshot | CANONICAL (runtime) / dated |
| Per-customer price | `pricing.ts` last-paid rule | CANONICAL (runtime) |
| Order rules | `catalog.ts`, `build-cart.ts` | CANONICAL (code) |
| Availability | `customer_portal.item_availability_current` | CANONICAL |
| SKU ↔ item | `integration_sku_map` | CANONICAL |
| VAT presentation | `commercial-terms.md` §1; `claims#vat_presentation` | CANONICAL (`user_confirmed`) |
| Shelf life | `claims#shelf_life` (concentrate 1 year closed, 3 months open; powders 2 years) | CANONICAL (`user_confirmed`) |
| GT internal COGS/margin | `v_fg_economics`, `v_fg_unit_economics` | Not for the Builder |

## 2. Conflicts

C1 three generations of figures (38/48 differ; e.g. p16 lemonade ₪3.69/₪20/78% now vs 3.95/22/79 on 08-27 vs family `₪19` on the English site; p30 5.75/31/78% vs 6.46/39/80%; p44 5.77/31/78% vs 5.79/44/84%). C2 ingredient price basis 08-27 vs 09-29 (matcha 1,080→1,180; ODK 55→60; ube 350→340; milk 8→5.43; cream 22→25.90) — Sales-Machine `recipes.yaml` (1.94 / 2.2 / 0.7) disagrees with `products/catalog.yaml` (2.13 / 2.4 / 0.68). C3 pours: `recipes.yaml` 233 ml milk / 233 ml lemonade / 150 ml coconut water / 150 ml tonic vs 09-29 145 / 145 / 110 / 120. C4 cups per bottle: answer bank "20 at 50 ml" (draft) vs site "20–25" vs chai page "20" vs U-021 "33 / 30 / 13"; data supports 20 at 50 ml (21 drinks), 25 at 40 ml (8), half for 500 ml. C5 drinks per NAMASTEA bottle: 11 (claims, products card, chai page) vs 13 (home page; the extra two need a powder). C6 matcha masala concentrate dose 40 ml (model, workbook, S6) vs Canva page 50 ml. C7 matcha vanilla page (p36) shows the agave recipe verbatim. C8 matcha per serving ₪2.13 (products card, claim) vs ₪2.12 (09-29) vs "278" cups (menu copy; fix to 277) vs ₪1.94 (08-27); matcha page advertises "50 גרם ≈ 27 כוסות" for a pack not sold. C9 names: p12 "חליטת תה ירוק וליים" (S1, S4) vs "חליטת תה ירוק לואיזה וליים" (S6, S8, gt-site.js, commercial-terms §2, menus masterprompt); opening menu "משקה תפוח היביסקוס" / "משקה תות לואיזה" vs S1 "חליטת …"; ASCII `'` vs Hebrew `׳` breaks exact joins. C10 `commercial-terms.md` §2 opening-menu prices stale (₪31/₪39/₪37 → S1 ₪27/₪31/₪32). C11 food-cost disclosure: D-018 and the DB answer row `food_cost` (0342:193-199) hand over vs `knowledge/drinks/catalog.yaml` holding every cost, the approved answer `is_it_profitable` ("חליטה קרה עולה ₪3.25"), and D-025; D-018 says RRP "stays public" while `site_flags.json` hides it. C12 the skill contradicts its data (`DAHPi9gpfts`, 44 asterisks, ₪19–28 only). C13 card checks pinned to 08-27. C14 live site "עד 87%" / "מ־₪2.85" vs current max 86% / min ₪2.88. C15 site product list shows "מאצ׳ה טקסי · 50 גרם ₪65" and "GT Elita · 30 גרם ₪38" (not sold) and omits Hojicha 1 kg. C16 `lexicon.json` UBE 0.5 kg `catalog: 130` vs ₪175. C17 `legacy_sku` unreliable (`FG-DES-500ML` → `GT-DES-LOW-0.5L` vs Shopify `GT-INF-DES-0.5L`). C18 Shopify `taxesIncluded=true` at 17% while prices are ex-VAT and the portal uses 0.18. C19 five taxonomies (Sales-Machine {תה, צ'אי, אבקות}; 10 catalog families; gt-site 9 groups + 4 landing pages; 5 lead menus; `campaign_map` {tea, chai, powder, general}). C20 duplicate U-018 / U-021 IDs in Sales-Machine CURRENT_STATE (D-013's "open as U-018" points at the wrong item). C21 ODK `SALES_UOM 'BAG'` in the item master vs bottles sold in pairs in the portal.

## 3. Gaps — data that exists nowhere (the Builder must not invent it)

1. Consumption volume: no cups per day/week, no stock levels per café; pack counts cannot be computed without asking the customer.
2. Opening-order quantities and starter packages open (D-013; refusal `starter_packages`, TOM-A.1); discount tiers deliberately open (`commercial-terms.md` §6).
3. No hot or winter drinks; no per-drink season field (Summer 2026 cold set only).
4. No recipes for HOJICHA, AMERICAN, the 22×18 g sachets or the kit; no drink names a sugar-free variant (substitution undocumented); kit contents unrecorded.
5. No quantities for flavour add-ins (site steps mention 20 ml sesame paste, 15 ml pistachio paste, 40 ml banana purée; not in the model).
6. No measured cup or ice displacement; no costs for garnish, ice, water, soda, packaging, labour; non-GT ingredient prices are assumptions.
7. No per-customer food cost (model uses list prices for 1 L / 1 kg; real buyers pay last-paid; 500 ml costs ₪3.30/serving); no price book on `main` (`sales_core.list_price` / `customer_price` in no migration file on main).
8. No canonical English names, no stable drink IDs beyond the legacy page key, no drink→SKU table, no drink/product image field in any database.
9. No allergen or nutrition data (refusal topics; 17 kcal claim `unsourced`).
10. No one approved yield number per product (U-021); no rule from Tom on which economics a self-serve Builder may show; customer-specific pricing "⊥ modeled" (brain CURRENT_STATE).
11. Unclassifiable from the repos: `GT-ELT-STR-0.5L` (₪24, neither sold nor not-sold in catalog-truth); garnish SKUs `AP-DRI-ORA` (₪17), `AP-STI-CIN` (₪60) used in p51/p48 serving text; whether the five lead-menu PDFs carry the 09-29 figures (candidate doc says "applied", not verified).

Files to open first: brain `.claude/skills/drinks-pricelist/drinks_final_figures.json`, `docs/pricing/GT_FOOD_COST_2026-09-29.xlsx`, `docs/warehouses/catalog-truth.md`, `gt-factory-os/api/src/portal/catalog.ts`, `gt-site/tools/landing-pages/drinks.json`.
