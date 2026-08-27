# MASTERPROMPT ADDENDUM — hojicha 1 KG, the gold-bag product, reconciled end to end

**STATUS: LIVE — not yet executed**

> **Usage:** paste this after
> `docs/plans/2026-08-27-30g-repack-line-masterprompt.md` in the same session, or on its
> own in a fresh session with `gt-factory-os`, `gt-factory-os-production-brain` and the
> Shopify + Supabase MCP servers attached. It is a **fourth product, not a fourth
> member of the black-can family** — hojicha 1 KG is packed in a large gold bag with its
> own label, and shares no packaging component with the three small cans.
>
> **Inherits from the main masterprompt, cited not copied:** §0 How to work (authority
> order, migration discipline, the standard, output language) · §7 landmines 2, 3, 5, 6,
> 8 — all five apply here unchanged · §8 halt conditions. Read it first. Where the two
> documents disagree, the main masterprompt wins.
>
> **Provenance:** written 2026-08-27 from live measurement — Supabase project
> `rvadsozabmxkkrktwgnv` (`private_core`) and the live Shopify Admin API.
>
> **Shelf life:** §2 is presumed wrong if pasted after 2026-09-10. Re-run §2.4 first.
> If reality no longer matches §2, **halt and surface**.

## 1. Mission and definition of done

**One testable sentence:** hojicha 1 KG exists in `private_core` as a REPACK item with an
active gold-bag BOM and mappings on both channels, and its Shopify variant no longer
carries a placeholder barcode.

| # | Condition | The observation that would prove it false |
|---|---|---|
| H1 | `ADD-HOJ-1KG` exists, `supply_method='REPACK'`, `status='ACTIVE'` | the item query in §2.4 returns no row, or a row that is not REPACK/ACTIVE |
| H2 | `BOM-REPACK-HOJ-1KG` is ACTIVE with exactly 4 ACTIVE lines on its active version | the BOM query in §2.4 returns `bad_lines > 0` or `total_lines <> 4` |
| H3 | The BOM consumes 1.000 `KG` of hojicha bulk — not 0.5, not 1000 | `select final_component_qty, component_uom from private_core.bom_lines where bom_head_id='BOM-REPACK-HOJ-1KG' and final_component_id like 'RAW-HOJICHA%';` ≠ `1.00000000 / KG` |
| H4 | The BOM uses a **1 KG** bag component, and does **not** reference `PKG-BAG-HOJ-500G` | `select 1 from private_core.bom_lines where bom_head_id='BOM-REPACK-HOJ-1KG' and final_component_id='PKG-BAG-HOJ-500G';` returns a row |
| H5 | `GT-HOJ-BLK-1000` is mapped to `ADD-HOJ-1KG`, approved+active, on `shopify` **and** `lionwheel` | the mapping query in §2.4 returns fewer than 2 rows |
| H6 | The Shopify variant carries a real GTIN-13, or Tom's decision to keep the placeholder is recorded in the final report | `productVariants(query:"barcode:TEMP*")` still returns `GT-HOJ-BLK-1000` **and** the report does not name Tom's ruling |
| H7 | `rebuild_verifier()` is 0 and this work wrote no ledger row | `select rebuild_verifier();` ≠ 0 |

### 1.1 Settled — do not reopen

- **Gold bag, its own label.** Tom, 2026-08-27: `הוא יהיה עם שקית שהב גדולה ומדבקה משלו`.
- **This product shares nothing with the black can.** `PKG-CAN-MAT-30G-BLACK` must not
  appear in this BOM.

## 2. Ground truth — measured 2026-08-27

### 2.1 The reorganizing fact: the Shopify product is already finished

The Shopify side is **not** a build. `gid://shopify/Product/9772813484273` is complete
and correct: title `הוג'יצ'ה מאצ'ה שחורה 1 ק"ג | Hojicha Black Matcha 1KG`, handle
`הוגיצה-מאצה-שחורה-1-קג-hojicha-black-matcha-1kg`, vendor `Greentea Everyday - גרינטי`,
`productType` `Matcha`, tags `["Hojicha","Matcha"]`, option `גודל` = `1 ק"ג (1000 גרם)`,
the family description ending `<p>אריזה: 1 ק"ג (1000 גרם).</p>`, `status: ACTIVE`,
published to Online Store `gid://shopify/Publication/65046184096`. Its single variant
`gid://shopify/ProductVariant/48602591887601` carries SKU `GT-HOJ-BLK-1000`, ₪750,
`taxable: true`, `inventoryPolicy: DENY`, `tracked: true`, weight 1000 `GRAMS`,
`inventoryQuantity: 0`.

**Exactly one field is wrong: `barcode` is `TEMP-GT-HOJ-BLK-1000`.** Do not recreate,
duplicate or "rebuild" this product. Touch that one field, and only when §5 A is answered.

**All the real work is on our side, where the product does not exist at all.**

### 2.2 What is NOT built

- No item. `ADD-HOJ-500G` is the only hojicha item in `private_core`.
- No BOM.
- No mapping on either channel. `GT-HOJ-BLK-500` is mapped; `GT-HOJ-BLK-1000` is not —
  so every 1 KG order sold so far has been invisible to stock truth.
- No 1 KG gold bag component. `PKG-BAG-HOJ-500G` (`Hojicha 500G Bag (gold)`) is the
  only gold bag that exists, and it is the wrong size.
- No 1 KG labels.

### 2.3 What exists and is reusable

| component_id | name | note |
|---|---|---|
| `RAW-HOJICHA-BULK` | `Hojicha bulk (black matcha)` | ₪310 / KG — what `BOM-REPACK-HOJ-500G` consumes |
| `RAW-HOJICHA-AT-AMITEA` | `Hojicha bulk — held at AMITEA (external packer)` | a **different** component; see §5 B |

Reference BOM: `BOM-REPACK-HOJ-500G`, active version `40510000-0000-4000-8000-000000000324`,
`version_label='V1_REPACK'`, 4 lines — bulk `KG` · bag `UNIT` · front label `UNIT` ·
back label `UNIT`, every line `component_ref_type='RAW_NAME'`, `scaling_method='RATIO'`,
`final_item_id=null`, head `production_track='other'`, output 1 `PCS`.

Reference item: `ADD-HOJ-500G` — `family='NONOMIMI'`, `product_group='NONO MIMI PRODUCTS'`,
`sub_type='Hojicha'`, `item_type='POWDER'`, `sales_uom='BAG'`, `pack_size='0.5KG'`,
`case_pack=1`, `is_stock_managed=true`.

**Barcode candidates, checked live 2026-08-27.** Four numbers returned **zero** Shopify
variants, in both leading-zero forms: `0726529648140`, `0726529648164`, `0726529648225`,
`0726529648263`. Clean in Shopify is only half the check — the registry half is §5 A.
Separately: `GT-HOJ-BLK-1000` is the **only** variant in the entire store with a `TEMP-`
barcode, so this is one isolated defect, not a pattern.

### 2.4 Re-verification block — start here, before any write

This is your first action. Run both blocks and compare against §2.1–§2.3 before you
create anything. A mismatch is a halt, not a puzzle to solve.

```sql
-- Supabase rvadsozabmxkkrktwgnv, measured 2026-08-27
select item_id, item_name, supply_method, status, barcode, primary_bom_head_id
  from private_core.items where item_id in ('ADD-HOJ-500G','ADD-HOJ-1KG');

select external_sku, item_id, source_channel, approval_status, mapping_status
  from private_core.integration_sku_map where external_sku in ('GT-HOJ-BLK-500','GT-HOJ-BLK-1000');

select component_id, component_name, status from private_core.components
 where component_id in ('PKG-BAG-HOJ-500G','PKG-BAG-HOJ-1KG','RAW-HOJICHA-BULK',
                        'PKG-LABEL-HOJ-1KG','PKG-LABEL-HOJ-1KG-BACK');

-- H2, runnable as-is: expect 1 row, bad_lines = 0, total_lines = 4
select h.bom_head_id,
       count(*) filter (where l.status <> 'ACTIVE') as bad_lines,
       count(*)                                     as total_lines
  from private_core.bom_head h
  join private_core.bom_lines l
    on l.bom_head_id = h.bom_head_id and l.bom_version_id = h.active_version_id
 where h.bom_head_id = 'BOM-REPACK-HOJ-1KG' group by 1;
```

```graphql
# Shopify, 2026-08-27 — the barcode candidates must all return zero nodes
query {
  productVariants(first: 30, query: "barcode:0726529648140 OR barcode:726529648140 OR barcode:0726529648164 OR barcode:726529648164 OR barcode:0726529648225 OR barcode:726529648225 OR barcode:0726529648263 OR barcode:726529648263") {
    edges { node { id sku barcode product { title status } } } }
}
```

## 3. Workstreams

Run W1 → W2 → W3 → W4 → W6. W5 is gated on Tom and may finish after the rest.

### W1 — The gold bag and its labels

Create three components, `status='ACTIVE'`, `inventory_uom='UNIT'`, `bom_uom='UNIT'`:

| component_id | component_name | component_class | component_group |
|---|---|---|---|
| `PKG-BAG-HOJ-1KG` | `Hojicha 1KG Bag (gold, large)` | `PACKAGING` | `BAG` |
| `PKG-LABEL-HOJ-1KG` | `Sticker: Hojicha 1KG` | `PACKAGING` | `LABEL` |
| `PKG-LABEL-HOJ-1KG-BACK` | `Back Sticker: Hojicha 1KG` | `PACKAGING` | `LABEL` |

Leave `std_cost_per_inv_uom` null — Tom has not priced them, and an invented cost
propagates into FOOD COST. **Acceptance:** H4 becomes reachable.

### W2 — The item

`item_id` `ADD-HOJ-1KG`, mirroring `ADD-HOJ-500G` field for field except
`pack_size='1KG'`. `supply_method='REPACK'` — see landmine 1. `barcode`: leave null until
§5 A resolves; `items.barcode` is documentation, the mapping is what the reconciler
reads. **Acceptance:** H1.

### W3 — The BOM

`BOM-REPACK-HOJ-1KG`, built to the `BOM-REPACK-HOJ-500G` shape in §2.3.
`bom_version`: `version_label='V1_REPACK'`, `status='ACTIVE'`,
`source_basis='tom_chat_hojicha_1kg_gold_bag_2026_08_27'`, `min_run_l`/`buffer_pct`/
`content_hash` null. Point `bom_head.active_version_id` at it.

| line | component | qty | uom |
|---|---|---|---|
| 1 | hojicha bulk — see §5 B | `1.000` | `KG` |
| 2 | `PKG-BAG-HOJ-1KG` | `1` | `UNIT` |
| 3 | `PKG-LABEL-HOJ-1KG` | `1` | `UNIT` |
| 4 | `PKG-LABEL-HOJ-1KG-BACK` | `1` | `UNIT` |

**Acceptance:** H2, H3, H4.

### W4 — The mapping, both channels

`GT-HOJ-BLK-1000` → `ADD-HOJ-1KG`, `approval_status='approved'`,
`mapping_status='active'`, `internal_units_per_shopify_unit=1`, once for
`source_channel='shopify'` and once for `'lionwheel'`. **Acceptance:** H5.

### W5 — The barcode, gated on §5 A

When Tom names the number: set it on `gid://shopify/ProductVariant/48602591887601`
only. Re-read the variant afterwards and assert the barcode came back — a variant update
can silently drop the field. Then update `items.barcode` on `ADD-HOJ-1KG` to match.
If Tom rules that the placeholder stays for now, write that ruling into the final report
and leave the field alone. **Acceptance:** H6.

### W6 — Cross-check

Run H1–H7 as queries, not claims. Run the canonical coverage query from
`gt-factory-os/CLAUDE.md` §Shopify writes and confirm `ADD-HOJ-1KG` is absent from it.
`select rebuild_verifier();` = 0. Re-read the Shopify variant.

## 4. Scope

**IN:** everything in §3.

**OUT — do not touch:**
- The Shopify product's title, handle, description, tags, vendor, price, weight,
  publications or status. Only the barcode field is in scope, and only under W5.
- `ADD-HOJ-500G`, `BOM-REPACK-HOJ-500G`, `PKG-BAG-HOJ-500G`, `PKG-LABEL-HOJ-500G*` —
  the 500 g line is correct and finished.
- `PKG-CAN-MAT-30G-BLACK` and everything in the main masterprompt's scope.
- `stock_ledger`, `balance_anchors`, projections — read only.
- `docs/warehouses/catalog-truth.md`.

## 5. Tom's part — the complete list

**A. The barcode.** `TEMP-GT-HOJ-BLK-1000` is not a GTIN. Four numbers are clean on the
Shopify side, verified 2026-08-27: `0726529648140`, `0726529648164`, `0726529648225`,
`0726529648263`. What is unverified is the registry half — these four sit in the `08`
pool as candidates but do not appear in `FREE_BARCODES.txt`, an unexplained mismatch
Tom flagged himself. Either confirm one of the four against
`Barcodes_Registry_2025-10-10.xlsx` and the GS1 block, or supply a number from a new
block, or rule that the placeholder stays for now. **Do not mint one.**

**B. Which hojicha bulk the 1 KG consumes.** `RAW-HOJICHA-BULK` (in-house, what the
500 g uses) or `RAW-HOJICHA-AT-AMITEA` (external packer). If AMITEA, the BOM also needs a
filling-service line, the way `BOM-REPACK-MAT-18G` carries `SRV-FILL-MAT-18G`. Default
to `RAW-HOJICHA-BULK` if unanswered, and say so in the report.

**C. Is the 1 KG label artwork ready**, or is `PKG-LABEL-HOJ-1KG` a placeholder awaiting
design? Affects nothing structural; affects whether the product can actually be packed.

**D. Bag and label costs**, if he wants FOOD COST to be complete for this SKU.

If Tom is unreachable: build W1–W4 and W6 in full, default B to `RAW-HOJICHA-BULK`,
leave the barcode alone, and report exactly what is unset. The system side does not need
him.

## 6. Landmines specific to this product

Landmines 2, 3, 5, 6 and 8 from the main masterprompt apply here unchanged. Additionally:

1. **`ADD-UBE-1KG` is the closest-looking 1 KG sibling and it is `BOUGHT_FINISHED` with
   no BOM.** Copying its shape produces an item that looks complete and consumes
   nothing — no bag, no label, no bulk — so packing it would never decrement stock.
   Hojicha 1 KG is repacked here from bulk, so it is `REPACK` with a BOM. Mirror
   `ADD-HOJ-500G`, not `ADD-UBE-1KG`.

2. **`PKG-BAG-HOJ-500G` is named `(gold)` and will match a search for the gold bag.**
   It is the 500 g bag. Using it gives a 1 KG product a half-size bag in its BOM, and
   the error is invisible until someone packs it. H4 exists to catch exactly this.

3. **The bulk line is `1.000 KG`, not `1000`.** The component's `inventory_uom` is `KG`.
   A line of `1000 KG` passes every constraint and understates yield by a thousandfold
   the first time anyone plans production from it.

4. **The Shopify product already exists and is correct.** The instinct on reading
   "set it up in Shopify" is to run `productCreate`. That would produce a duplicate
   product competing for the same SKU. Verify before you write — the SKU query in §2.4
   will return the existing variant.

5. **Two hojicha bulk components exist and differ only by suffix.** `RAW-HOJICHA-BULK`
   and `RAW-HOJICHA-AT-AMITEA` represent stock in two physical places. Picking the wrong
   one plans a purchase against inventory that is sitting at someone else's factory.

## 7. Halt conditions

Inherited set cited in the main masterprompt §8. Additions:

- A second variant anywhere in the store carries SKU `GT-HOJ-BLK-1000` → **STOP**,
  a duplicate already exists.
- Any of the four barcode candidates comes back non-empty at boot → **STOP**, that
  number is spent; report which.
- A write would modify any field of `gid://shopify/Product/9772813484273` other than the
  variant barcode → **STOP**.

## 8. Final report

Use the handoff shape in `gt-factory-os-production-brain/AGENT_TEMPLATE.md`, tokens per
`VERDICT_GLOSSARY.md`. H1–H7 each ✅ or ❌ with the query output that proves it. State
plainly which of §5 A–D are still open and what each blocks. Then stamp the STATUS line
at the top of this file `SHIPPED` or `ABANDONED — <why>`.
