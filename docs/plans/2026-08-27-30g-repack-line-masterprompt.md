# MASTERPROMPT — the three small-can REPACK products, live and reconciled end to end

**STATUS: LIVE — not yet executed**

> **Usage:** paste this entire file as the first message of a fresh session with
> `gt-factory-os`, `gt-factory-os-production-brain` and the Shopify + Supabase MCP
> servers attached. It takes GT's three small-can powders from "one exists in Shopify
> with no system record, two exist nowhere" to "three REPACK items, three BOMs, three
> mappings, two new Shopify products, every layer cross-checked."
> It halts for Tom only where §6 says so. §6 is that complete list.
>
> **Provenance:** written 2026-08-27 from live measurement — Supabase project
> `rvadsozabmxkkrktwgnv` (`private_core` schema, read-only queries in §2.5) and the live
> Shopify Admin API (`greenteaeveryday.myshopify.com`). Tom supplied the packaging
> decision and the Elita ruling in conversation the same day.
> Authority: `gt-factory-os-production-brain/CLAUDE.md`, then
> `gt-factory-os/CLAUDE.md` — cited by section below, never copied.
>
> **Shelf life:** §2 is presumed wrong if pasted after 2026-09-10. Re-run §2.5 first.
> If reality no longer matches §2, **halt and surface** — do not adapt silently. Stock
> and mappings move daily; a stale assumption here writes a wrong BOM.

## 0. How to work

- **Who you are here:** one agent session, end to end. You hold Supabase MCP (read +
  `apply_migration`), Shopify Admin MCP (read + write), and both repos. You may decide
  modelling details that follow the existing pattern. You may **not** decide price,
  publication channels, initial stock, or product status — those are §6.
- **Read first, in order:** `gt-factory-os-production-brain/CLAUDE.md` ·
  `gt-factory-os/CLAUDE.md` · `gt-factory-os-production-brain/CURRENT_STATE.md`.
- **Authority:** where this document and an authority doc disagree, the authority doc
  wins and this document is wrong. Say so and stop.
- **Halt conditions, evidence standard, git discipline, migration numbering:** inherited
  from `gt-factory-os-production-brain/CLAUDE.md` §Stop conditions and §Evidence, and
  `gt-factory-os/CLAUDE.md` §Migrations. Deltas specific to this work are in §8 only.
- **Migrations:** every `private_core` write goes through a numbered migration under
  `gt-factory-os/db/migrations/`, with its pgTAP test in `db/tests/NNNN_name.test.sql`.
  The test must assert, at minimum: the three items exist with `supply_method='REPACK'`
  · each has an ACTIVE bom_head whose `active_version_id` resolves to an ACTIVE version
  · each active version has exactly 4 lines, all `status='ACTIVE'` · the shared can
  appears once per BOM · each item has an approved+active `shopify` mapping row. Report
  N/N. Obey the FR1/FR2 bracket in
  `gt-factory-os/CLAUDE.md` §Migrations: list `db/migrations/` immediately before
  writing a numbered file, and again after. A new file appeared in between →
  HALT, `contract_failure`.
- **The standard (Tom's words, 2026-08-27):** `למפות ולהצליב הכל ברמה הגבוהה ביותר`
  — map and cross-check everything at the highest level. Translated into checkable
  prohibitions:
  **no item may exist without an active Shopify mapping** · **no BOM line may be left
  `PENDING`** · **no Shopify variant in scope may carry a `TEMP-` barcode or a negative
  inventory quantity when you finish**.
- **Language:** this document is in English because that is the register the executor
  reasons best in. Data literals — SKUs, item ids, Hebrew product titles and
  descriptions — stay in their own script, in backticks, and are never translated.
  **Output language: concise English.** Short sentences. No preamble, no restating the
  task, no summary of what you are about to do.

## 1. Mission and definition of done

**One testable sentence:** three REPACK items — GT matcha 30 g, hojicha 30 g, ube 50 g —
exist in `private_core` with an active BOM built on the shared black can plus their own
labels, each mapped to a live Shopify variant, with stock truth intact.

| # | Condition | The observation that would prove it false |
|---|---|---|
| D1 | Three items exist, `supply_method='REPACK'`, `status='ACTIVE'` | `select item_id,supply_method,status from private_core.items where item_id in ('FG-MAT-CAN-30','FG-HOJ-CAN-30','FG-UBE-CAN-50');` returns fewer than 3 rows, or any row not REPACK/ACTIVE |
| D2 | Each item has an ACTIVE BOM head whose active version has **zero** non-ACTIVE lines | run the D2 query in §2.5 — any row with `bad_lines > 0`, or fewer than 3 rows |
| D3 | All three BOMs consume the same can component on exactly one line each | `select final_component_id,count(distinct bom_head_id) from private_core.bom_lines where final_component_id like 'PKG-CAN-%BLACK%' group by 1;` returns count < 3 |
| D4 | Each item has an approved+active `shopify` mapping, and the coverage query is clean | the canonical coverage query in `gt-factory-os/CLAUDE.md` §Shopify writes returns any of the three item ids |
| D5 | Both new Shopify products exist with the assigned barcodes, one variant each | `productVariants(query:"barcode:0693493237901 OR barcode:0693493238137")` returns fewer than 2 nodes |
| D6 | No variant in scope has negative inventory at `gid://shopify/Location/54802612384` | any of the three variants reports `inventoryQuantity < 0` after the run |
| D7 | `rebuild_verifier()` is 0 and no ledger row was written by this work | `select rebuild_verifier();` ≠ 0, or the ledger gained rows attributable to this session |

Anything not on this list is out of scope unless Tom asks.

### 1.1 Settled — do not reopen

- **The GT matcha 30 g can is an ADDITIONAL product, separate from Elita's.** Tom,
  2026-08-27, verbatim: `זה מוצר נוסף מזה של אליטה!`. `FG-MAT-30G` and Shopify
  `GT-SHI-CER-30` belong to Elita and are untouched. See landmine 1.
- **One black can, shared by all three; each product gets its own label.** Tom,
  2026-08-27: `הפחית שנארוז את שלושתם היא שחורה - יש לנו מלא במלאי`.
- **The modelling pattern is the existing REPACK pattern**, not a new design. §2.1.
- **Barcodes are already assigned and verified** (Tom, 2026-08-27). Do not mint new ones,
  do not draw from the pool — the pool is empty. See landmine 4.

## 2. Ground truth — measured 2026-08-27; re-verify at boot

### 2.1 The canonical REPACK pattern, from the two BOMs that are actually ACTIVE

`BOM-REPACK-UBE-500G` and `BOM-REPACK-HOJ-500G` are the reference. Both are
`bom_kind='REPACK'`, `parent_ref_type='ITEM'`, `final_bom_output_qty=1`,
`final_bom_output_uom='PCS'`, `status='ACTIVE'`, `production_track='other'`. Every line
carries `component_ref_type='RAW_NAME'`, `scaling_method='RATIO'`, `final_item_id=null`:

| line | what | qty | uom |
|---|---|---|---|
| 1 | bulk powder — `RAW-UBE-BULK` / `RAW-HOJICHA-BULK` | fill weight in KG | `KG` |
| 2 | package — `PKG-BAG-UBE-500G` / `PKG-BAG-HOJ-500G` | 1 | `UNIT` |
| 3 | front label — `PKG-LABEL-UBE-500G` | 1 | `UNIT` |
| 4 | back label — `PKG-LABEL-UBE-500G-BACK` | 1 | `UNIT` |

Build the three new BOMs to this shape. Line 2 is the shared black can for all three.

The `bom_version` row follows the same two ACTIVE references, measured 2026-08-27:
`version_label='V1_REPACK'` · `status='ACTIVE'` · `min_run_l=null` · `buffer_pct=null` ·
`content_hash=null` · `source_basis` a short provenance string in the house style, e.g.
`tom_chat_dedicated_powder_bags_2026_08_10` on `BOM-REPACK-UBE-500G`. Use
`tom_chat_black_can_repack_2026_08_27` for all three. `bom_version_id` values in this
table are structured, not random (`0be50000-0000-4000-8000-000000000002`); keep
`bom_head.active_version_id` pointing at the row you create. Versions supersede by
archiving the old one (`status='ARCHIVED'`), never by deletion.

Suggested head ids, matching the existing naming: `BOM-REPACK-MAT-CAN-30G`,
`BOM-REPACK-HOJ-30G`, `BOM-REPACK-UBE-CAN-50G`. Note `BOM-REPACK-MAT-30G` is taken —
it is Elita's.

### 2.2 What exists, measured

**Components — all ACTIVE, all already present:**

| component_id | name | class | std cost |
|---|---|---|---|
| `PKG-CAN-MAT-30G-BLACK` | `Matcha 30G Black Can (GT)` | PACKAGING / TIN | null |
| `RAW-MATCHA-BULK` | `Matcha bulk` | INGREDIENT | ₪505 / KG |
| `RAW-HOJICHA-BULK` | `Hojicha bulk (black matcha)` | INGREDIENT | ₪310 / KG |
| `RAW-UBE-BULK` | `Ube bulk` | INGREDIENT | ₪110 / KG |
| `PKG-LABEL-MAT-30G` | `Sticker: Matcha 30G` | PACKAGING / LABEL | ₪0.40 |

`PKG-CAN-MAT-30G-BLACK` is **used in zero BOM lines today** — verified. It is free to
adopt as the shared can. Its id says `MAT-30G` but it will serve all three; see §4 W1.

**Shopify, live:**

| SKU | product gid | barcode | price | inventory |
|---|---|---|---|---|
| `GT-UBE-CAN-50` | `gid://shopify/Product/9783837163761` | `0693493237802` | ₪30 | **−100** |
| `GT-SHI-CER-30` (Elita — do not touch) | `gid://shopify/Product/9531677901041` | `0724133176639` | ₪38 | — |
| `GT-HOJ-BLK-1000` | `gid://shopify/Product/9772813484273` | `TEMP-GT-HOJ-BLK-1000` | ₪750 | — |

**Shopify environment, verified 2026-08-27:** store `greenteaeveryday.myshopify.com`
(ILS) · stock location `gid://shopify/Location/54802612384` (`הלהב 15, חולון`) ·
publications — Online Store `gid://shopify/Publication/65046184096`, Facebook &
Instagram `gid://shopify/Publication/67101819040`, Google & YouTube
`gid://shopify/Publication/67379724448`.

`GT-UBE-CAN-50` is the **structural template** for the two new products: vendor
`Greentea Everyday - גרינטי`, `productType` `Powder`, tags `["Powder","Ube"]`, single
variant, two-paragraph Hebrew description ending `<p>אריזה: 50 גרם.</p>`.

**Barcodes and SKUs for the two new products — both confirmed free 2026-08-27:**

| product | SKU | barcode |
|---|---|---|
| GT matcha 30 g | `GT-MAT-CAN-30` | `0693493237901` |
| hojicha 30 g | `GT-HOJ-BLK-30` | `0693493238137` |

### 2.3 What is NOT built

- **No item, no BOM, no mapping for ube 50 g** — yet `GT-UBE-CAN-50` is live and
  sellable in Shopify. Every ube-50 g order today is invisible to stock truth. This is
  the largest open hole and W3 closes it.
- No item, no BOM, no Shopify product for **hojicha 30 g**.
- No item, no BOM, no Shopify product for **GT matcha 30 g** (Elita's is a different
  product — §1.1).
- No back-label components for any of the three new products.

### 2.4 Known-broken, adjacent, OUT of scope — do not fix

- `GT-HOJ-BLK-1000` carries the placeholder barcode `TEMP-GT-HOJ-BLK-1000` and has no
  item and no mapping. Real defect, not this work. Report it, do not fix it.
- `GT-UBE-CAN-50` inventory is **−100** and `ADD-UBE-500G` is negative too
  (`docs/gap_registry.md` GAP-027). You must not leave the *new* items negative (D6),
  but correcting existing negatives needs the approved count-correction path and Tom.
- `BOM-REPACK-MAT-30G` (Elita's) has three `PENDING` lines and no label lines. Elita's
  problem. Do not repurpose it and do not "tidy" it.
- `items.sku` is `null` for nearly every item. That is by design; see landmine 2.

### 2.5 Re-verification block — run this first, it regenerates §2.2 in one paste

```sql
-- Supabase project rvadsozabmxkkrktwgnv, run 2026-08-27; re-run at boot
select item_id, item_name, supply_method, status, barcode, primary_bom_head_id
  from private_core.items
 where item_id in ('FG-MAT-30G','ADD-HOJ-500G','ADD-UBE-500G',
                   'FG-MAT-CAN-30','FG-HOJ-CAN-30','FG-UBE-CAN-50');

select component_id, component_name, status, inventory_uom, std_cost_per_inv_uom
  from private_core.components
 where component_id in ('PKG-CAN-MAT-30G-BLACK','RAW-MATCHA-BULK',
                        'RAW-HOJICHA-BULK','RAW-UBE-BULK');

select count(*) as black_can_bom_lines
  from private_core.bom_lines where final_component_id = 'PKG-CAN-MAT-30G-BLACK';

select external_sku, item_id, source_channel, approval_status, mapping_status
  from private_core.integration_sku_map
 where external_sku in ('GT-UBE-CAN-50','GT-MAT-CAN-30','GT-HOJ-BLK-30','GT-SHI-CER-30');

-- D2, runnable as-is: expect 3 rows, every bad_lines = 0
select h.bom_head_id,
       count(*) filter (where l.status <> 'ACTIVE') as bad_lines,
       count(*)                                     as total_lines
  from private_core.bom_head h
  join private_core.bom_lines l
    on l.bom_head_id = h.bom_head_id and l.bom_version_id = h.active_version_id
 where h.parent_ref_id in ('FG-MAT-CAN-30','FG-HOJ-CAN-30','FG-UBE-CAN-50')
 group by 1;
```

```graphql
# Shopify, run 2026-08-27 — both must return zero nodes before you create anything
query {
  b: productVariants(first: 20, query: "barcode:0693493237901 OR barcode:693493237901 OR barcode:0693493238137 OR barcode:693493238137") {
    edges { node { id sku barcode product { id title status } } } }
  s: productVariants(first: 20, query: "sku:GT-MAT-CAN-30 OR sku:GT-HOJ-BLK-30") {
    edges { node { id sku product { title status } } } }
}
```

## 3. What the hard part actually is

**The visible deliverable is two Shopify products. The actual work is in our own system,
and it is three times larger.** Shopify needs two creations. `private_core` needs three
items, three BOMs, new label components, and three mappings — plus the ube 50 g backfill
for a product that has been sellable for a while with no system record behind it.

**Ube 50 g is not a "create" — it is a reconciliation.** The storefront has been ahead of
the system. You are not introducing a product; you are giving an already-selling product
the record it should have had, without disturbing the sales that already happened.

**The riskiest keystroke is the one that looks most helpful.** `FG-MAT-30G` is named
`MATCHA 30G`, is REPACK, is ACTIVE, and has a 30 g BOM sitting in PENDING. Every signal
says "this is the row you came to finish." It is Elita's. Finishing it is the one
irreversible mistake available here.

**"Same can" is a modelling claim before it is a physical one.** One component id will
now be referenced by three BOMs with two different fill weights. Get the component
naming right at the start; renaming a `component_id` later is a primary-key change, and
the ledger will already point at it.

## 4. Workstreams

Run W1 before W2–W4. W2, W3, W4 are independent of each other. W5 is last.

### W1 — Adopt the shared black can, and create the missing labels

`PKG-CAN-MAT-30G-BLACK` is used in zero BOMs, so it is safe to adopt. **Keep the
`component_id` exactly as it is** — it is a primary key and changing it rewrites every
future ledger reference for no gain. Update `component_name` only, to something that
reads true for three products, e.g. `Black Can 30G/50G (GT, shared)`.

Create exactly these label components — do not invent ids. All are
`component_class='PACKAGING'`, `component_group='LABEL'`, `inventory_uom='UNIT'`,
`bom_uom='UNIT'`, `status='ACTIVE'`:

| component_id | component_name |
|---|---|
| `PKG-LABEL-MAT-CAN-30G` | `Sticker: GT Matcha Can 30G` |
| `PKG-LABEL-MAT-CAN-30G-BACK` | `Back Sticker: GT Matcha Can 30G` |
| `PKG-LABEL-HOJ-30G` | `Sticker: Hojicha 30G` |
| `PKG-LABEL-HOJ-30G-BACK` | `Back Sticker: Hojicha 30G` |
| `PKG-LABEL-UBE-CAN-50G` | `Sticker: Ube Can 50G` |
| `PKG-LABEL-UBE-CAN-50G-BACK` | `Back Sticker: Ube Can 50G` |

`PKG-LABEL-MAT-30G` (`Sticker: Matcha 30G`, ₪0.40) already exists and belongs to
Elita's line. Use it for the GT can **only** if Tom answers §6 F with "same sticker";
otherwise `PKG-LABEL-MAT-CAN-30G` above stays distinct. Leave costs null — Tom has not
priced these labels, and an invented cost propagates into FOOD COST.

**Acceptance:** D3 becomes reachable.

### W2 — GT matcha 30 g: item + BOM

New item, **do not touch `FG-MAT-30G`**. Suggested `item_id` `FG-MAT-CAN-30` — distinct
from Elita's row and from the SKU. Follow the field pattern of `FG-MAT-30G` for
`family`, `pack_size` (`30G`), `sales_uom` (`TIN`), `item_type` (`POWDER`),
`product_group` (`GT MATCHA`), `sub_type` (`Matcha`), `is_stock_managed=true`;
`barcode` = `0693493237901`; `supply_method='REPACK'`.

BOM to the §2.1 shape: `RAW-MATCHA-BULK` 0.030 `KG` · shared black can 1 `UNIT` ·
front label 1 `UNIT` · back label 1 `UNIT`. `production_track='matcha_repack'` to match
the other matcha REPACKs. Ask Tom whether a lid line is needed (§6 D).

**Acceptance:** D1, D2, D3 for this item.

### W3 — Ube 50 g: item + BOM + mapping for a product already selling

New item `FG-UBE-CAN-50`, `barcode` = `0693493237802` (already on the live variant).
Mirror `ADD-UBE-500G` for `family` (`NONOMIMI`), `product_group`
(`NONO MIMI PRODUCTS`), `sub_type` (`Ube`), `item_type` (`POWDER`).

BOM: `RAW-UBE-BULK` 0.050 `KG` · shared black can 1 `UNIT` · front + back label.
`production_track='other'`.

Map `GT-UBE-CAN-50` → `FG-UBE-CAN-50` for `source_channel='shopify'` **and**
`'lionwheel'`, `approval_status='approved'`, `mapping_status='active'`,
`internal_units_per_shopify_unit=1`. Both channels — every comparable item in §2.2
carries both, and a missing lionwheel row silently breaks delivery reconciliation.

**Acceptance:** D1, D2, D3, D4 for this item.

### W4 — Hojicha 30 g: item + BOM + new Shopify product

New item `FG-HOJ-CAN-30`, `barcode` = `0693493238137`, mirroring `ADD-HOJ-500G`'s
family fields. BOM: `RAW-HOJICHA-BULK` 0.030 `KG` · shared can · front + back label.

Shopify product, built from the `GT-UBE-CAN-50` template in §2.2:

```
title:        הוג'יצ'ה מאצ'ה שחורה 30 גרם | Hojicha Black Matcha 30g
vendor:       Greentea Everyday - גרינטי
productType:  Matcha
tags:         ["Hojicha","Matcha"]
options:      [{ name: "גודל", values: ["30 גרם"] }]
sku:          GT-HOJ-BLK-30
barcode:      0693493238137
taxable:      true
inventoryPolicy: DENY
inventoryItem: { tracked: true, requiresShipping: true,
                 measurement: { weight: { value: 30, unit: GRAMS } } }
```

Description: the hojicha family uses one description across every size and changes only
the packaging line. Copy `gid://shopify/Product/9682783699185` verbatim and replace the
second paragraph with `<p>אריזה: 30 גרם.</p>`.

The GT matcha 30 g Shopify product follows the same shape with `GT-MAT-CAN-30` /
`0693493237901` / `productType: Matcha` / tags `["Matcha"]` / title
`מאצ'ה 30 גרם | GT Matcha Can 30g`. **Write no cultivar or grade word** —
`Shizuoka`, `Ceremonial`, `Maruei` — into that description until Tom answers §6 B.

Price, status, publications and stock are §6 — set stock explicitly either way (D6).

**Acceptance:** D1–D6 for these items.

### W5 — Cross-check every layer, then report

Run all seven D-conditions as queries, not as claims. Run the canonical coverage query
from `gt-factory-os/CLAUDE.md` §Shopify writes. Run `select rebuild_verifier();` and
confirm 0. Re-read each of the three Shopify variants and confirm barcode, SKU and a
non-negative inventory quantity at `gid://shopify/Location/54802612384`.

**Acceptance:** D4, D6, D7.

## 5. Scope

**IN:** everything in §4.

**OUT — do not touch, do not "improve":**
- `FG-MAT-30G`, `BOM-REPACK-MAT-30G`, Shopify `GT-SHI-CER-30` /
  `gid://shopify/Product/9531677901041`, barcode `0724133176639` — all Elita's.
- The `TEMP-GT-HOJ-BLK-1000` barcode and the missing `GT-HOJ-BLK-1000` item.
- Existing negative balances on `ADD-UBE-500G`, `GT-UBE-CAN-50`, `GT-MAT-KIT`.
- `stock_ledger`, `balance_anchors`, any projection — read only, always.
- `docs/warehouses/catalog-truth.md`. Tom's instruction 2026-08-27: `אל תתעסק בזה עכשיו`.
  The three products belong there eventually; that is a separate pass.
- The two deliberate barcode conflicts on the Muza line (`693493237819`, `693493237826`).

## 6. Tom's part — the complete list, nothing else is his

**A. Price for each of the three.** Anchors from the live catalog 2026-08-27: hojicha
₪750/kg bulk-equivalent → ₪22.50 linear for 30 g, but the ube can sold at ×1.71 of
linear, which would put it near ₪38. Elita's 30 g matcha sits at ₪38. Ube 50 g is
already ₪30 and may simply stay. One decision per product.

**B. Which matcha is actually in the GT black can.** This gates the description wording
and confirms the SKU choice. `GT-MAT-CAN-30` is deliberately grade-neutral so the item
can be built before this lands — but the customer-facing text cannot.

**C. Initial stock quantity per product**, and whether ube 50 g's −100 is corrected in
the same pass or left for the count-correction path.

**D. Does the black can take a separate lid line in the BOM?** `PKG-LID-MAT-30G` exists.
One word: yes or no.

**E. `DRAFT` or `ACTIVE`, and which publications.** Ube and the hojicha family are Online
Store only (`gid://shopify/Publication/65046184096`); Elita is on three channels. Do not
infer from Elita.

**F. Is the GT black-can label the existing `PKG-LABEL-MAT-30G` sticker, or a new one?**

If Tom is unreachable: build everything, set `status='DRAFT'` in Shopify, stock `0`
explicitly, Online Store only, no final price, and report exactly what is unset. The
`private_core` side does not need him — build it fully.

## 7. Landmines — do not rediscover these

1. **`FG-MAT-30G` looks exactly like the row you came to finish. It is Elita's.**
   It is `MATCHA 30G`, REPACK, ACTIVE, and its BOM `BOM-REPACK-MAT-30G` has three
   `PENDING` lines waiting to be completed. It is mapped to Shopify `GT-SHI-CER-30` on
   both the `shopify` and `lionwheel` channels, and it carries barcode
   `0724133176639` — Elita's. It has also shipped recently (`docs/gap_registry.md`
   GAP-027 records 30 units in 40 days). → Create a **new** item. Never edit this one.

2. **`items.sku` is `null` for almost every item — this is not missing data.**
   The join to Shopify is `integration_sku_map.external_sku`, per
   `gt-factory-os/CLAUDE.md` §Shopify writes: *"Resolves SKUs from
   `integration_sku_map.external_sku` only"*. Populating `items.sku` and expecting the
   reconciler to notice repeats the 0303→0305 error. → Write the mapping row.

3. **A mapping on `shopify` alone looks complete and is not.** Every comparable item
   carries a `lionwheel` row too. The gap is silent until a delivery fails to reconcile.

4. **`FREE_BARCODES.txt` is stale and will hand you a used number.** `0693493237802`
   is listed there as free and is already live on `GT-UBE-CAN-50`. The pool is empty.
   → Use only the three barcodes in §2.2. Never edit that file by hand; the fix is to
   run the audit script.

5. **A leading zero does not create a new barcode.** `0693493237901` and
   `693493237901` are the same identity. Query both forms, and never filter by product
   status — an `ARCHIVED` or `DRAFT` variant holds a barcode exactly like an `ACTIVE` one.

6. **A `productCreate` that returns `200 OK` proves layer one only.** Per
   `gt-factory-os-production-brain/CLAUDE.md` §Evidence. Re-read every object you write
   and assert its fields. A variant can be created with the barcode silently dropped.

7. **Negative inventory with `inventoryPolicy: DENY` is a live order-taking fault**,
   not a cosmetic number. `GT-UBE-CAN-50` sits at −100 today. Set the new items'
   quantities explicitly — leaving them unset is how the existing ones got this way.

8. **Renaming `component_id` is a primary-key change.** The pull to rename
   `PKG-CAN-MAT-30G-BLACK` into something generic is strong and wrong. Change
   `component_name`; leave the id.

## 8. Halt conditions

Inherited set cited in §0. Additions specific to this work:

- Either barcode or either SKU comes back **non-empty** in §2.5 → **STOP.** Someone got
  here first. Report what exists; create nothing.
- Any operation would write, update or delete a row in `stock_ledger`,
  `balance_anchors`, or a projection → **STOP.** Nothing in this work needs one.
- `PKG-CAN-MAT-30G-BLACK` turns out to be referenced by a BOM line at boot (it is not
  today) → **STOP** and re-derive; the shared-can assumption has changed underneath you.
- `select rebuild_verifier();` returns non-zero at any point → **STOP** immediately,
  before the next write.
- The migration slot you claimed is taken when you re-list → **STOP**,
  `contract_failure`, per `gt-factory-os/CLAUDE.md` §Migrations.

## 9. Final report

Use the handoff shape in `gt-factory-os-production-brain/AGENT_TEMPLATE.md`, with tokens
matching `VERDICT_GLOSSARY.md`. Cover, in order:

1. What a stranger can now watch working, end to end — one sentence per product.
2. Each of D1–D7, ✅ or ❌, with the query output that proves it. No partial credit.
3. The numbers: items created, BOM lines by status, mappings by channel, coverage-query
   row count, `rebuild_verifier()`.
4. The artifacts: migration files, product gids, handles, BOM head ids.
5. What is still Tom's from §6, and what remains genuinely unfinished.
6. The single next action.

Then change the STATUS line at the top of this file to `SHIPPED` with evidence
pointers, or `ABANDONED — <why>`. A spent masterprompt that still reads LIVE will be
re-run by the next session.

If anything is not ready, say so first and plainly.
