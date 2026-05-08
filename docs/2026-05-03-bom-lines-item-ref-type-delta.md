# Contract delta: `bom_lines.component_ref_type='ITEM'` (sub-item REPACK assembly)

**Authored:** 2026-05-03
**Driver:** Trio FG (Margarita 0.3L Pear+Strawberry+Classic, supplier SUP-005 Elita Ofek). REPACK item that consumes 3 single-flavor FG items as inputs; no current ref_type can express that.
**Approved option:** (a) — extend the contract. Tom-locked 2026-05-03.
**Status:** proposal awaiting audit before implementation.

---

## 1. Why this is a contract change, not a master-data add

Migration `0131_retire_legacy_bom_ref_on_pack_heads.sql` already records the explicit forward-looking note:

> "sub-pack assembly is a future v2+ feature requiring its own ref-type"

The current enum `(RAW_NAME, BASE_BOM, COMPONENT, BOM)` cannot encode "this line consumes one unit of a referenced FG item from item-stock". The `'BOM'` value was retired on PACK/REPACK heads in 0131 and is not a workaround.

`final_component_id` carries an FK to `components(component_id)` (`0003_bom_three_table.sql:362`); writing an item_id into that column would violate the FK.

## 2. Locked semantic for `ref_type='ITEM'`

A line with `component_ref_type='ITEM'` means: **consume one unit of the referenced item from item stock.** Specifically:

- `final_component_id` is **NULL**.
- `final_item_id` (NEW column) references `items.item_id`.
- `final_component_qty` = sub-item units per parent output unit.
- **Production Actual posts a leaf consumption against the sub-item.** It does **NOT** recurse into the sub-item's BOM, because the sub-item's components were already consumed when the sub-item was produced. Recursing would double-count.
- **Planning** uses a different semantic — it must propagate demand up the chain (trio → singles → components). Not all of that lands in v1; see §6.

## 3. Schema delta (new migration `0138_bom_lines_add_item_ref_type.sql`)

```sql
begin;
set search_path to private_core, public;

-- 3.1. Extend ref_type enum
alter table private_core.bom_lines
  drop constraint bom_lines_component_ref_type_check;
alter table private_core.bom_lines
  add constraint bom_lines_component_ref_type_check
  check (component_ref_type in ('RAW_NAME','BASE_BOM','COMPONENT','BOM','ITEM'));

-- 3.2. New typed pointer for item refs (separate from final_component_id
--      to preserve existing FK integrity for component lines)
alter table private_core.bom_lines
  add column final_item_id text
  references private_core.items(item_id);

create index idx_bom_lines_item
  on private_core.bom_lines(final_item_id)
  where final_item_id is not null;

-- 3.3. Mutual-exclusion + presence rules
alter table private_core.bom_lines
  add constraint bom_lines_item_ref_pointer_consistency check (
    case component_ref_type
      when 'ITEM' then final_item_id is not null
                  and  final_component_id is null
      else            final_item_id is null
    end
  );

-- 3.4. Comment refresh
comment on column private_core.bom_lines.component_ref_type is
  'Workbook import provenance + structural ref kind. Values: RAW_NAME (legacy name lookup), COMPONENT (FK to components via final_component_id), BASE_BOM (sub-BOM into a BASE head; ref via items.base_bom_head_id), BOM (legacy, retired on PACK/REPACK in 0131), ITEM (sub-item consumption for REPACK assembly; FK to items via final_item_id, added 0138).';
comment on column private_core.bom_lines.final_item_id is
  'FK to items.item_id. Populated only when component_ref_type=ITEM. Indicates a leaf consumption of one finished sub-item per parent output unit. Mutually exclusive with final_component_id (constraint bom_lines_item_ref_pointer_consistency).';

commit;
```

Rollback: drop `bom_lines_item_ref_pointer_consistency`, drop column `final_item_id`, restore prior enum constraint with the four-value list.

## 4. Production Actual handler delta

**File:** `api/src/production-actuals/handler.ts`
**Function:** `loadTwoHeadBomContext` (line ~139), partition loop (line ~212–227)

### 4.1. Read shape

Extend the SQL projection in the PACK lines query (line ~187–206) to include `final_item_id`:

```ts
const packLineRows = await sql<{
  line_id: string;
  component_ref_type: string;
  final_component_id: string | null;
  final_item_id: string | null;        // NEW
  component_name: string | null;
  item_name: string | null;            // NEW (joined from items)
  final_component_qty: string | null;
  component_uom: string | null;
}>`
  select bl.line_id::text,
         bl.component_ref_type,
         bl.final_component_id,
         bl.final_item_id,
         c.component_name,
         it.item_name,
         bl.final_component_qty::text as final_component_qty,
         bl.component_uom
    from private_core.bom_lines bl
    left join private_core.components c on c.component_id = bl.final_component_id
    left join private_core.items     it on it.item_id     = bl.final_item_id
   where bl.bom_version_id = ${packVersionId}::uuid
     and bl.status in ('ACTIVE', 'PENDING')
   order by bl.line_no
`.execute(exec);
```

### 4.2. Partition

Add an ITEM branch alongside the existing BASE_BOM and COMPONENT/RAW_NAME branches:

```ts
for (const row of packLineRows.rows) {
  if (row.component_ref_type === 'BASE_BOM') {
    // ... unchanged
  } else if (row.component_ref_type === 'ITEM') {
    if (!row.final_item_id || !row.item_name || !row.final_component_qty) {
      // schema CHECK guarantees final_item_id is non-null when ref_type=ITEM,
      // but item_name absence means the FK target was deleted — surface it.
      return { kind: 'conflict', reason: 'ITEM_REF_MISSING', detail: `line ${row.line_id} component_ref_type=ITEM but item lookup returned no row` };
    }
    packLeafLines.push({
      line_id:             row.line_id,
      component_id:        row.final_item_id,    // see §4.3 on field reuse
      component_name:      row.item_name,
      final_component_qty: row.final_component_qty,
      component_uom:       row.component_uom,
      source:              'pack-item',          // NEW source tag
    });
  } else if (row.final_component_id && row.component_name && row.final_component_qty) {
    // ... unchanged COMPONENT/RAW_NAME branch
  }
}
```

### 4.3. Field reuse vs split

Two options for the in-memory `TwoHeadBomLine` shape:
- **(α)** Reuse the `component_id` field for both component and item refs (as in the snippet above), and rely on `source` tag (`pack` | `pack-item` | `base`) to disambiguate at posting time. Lighter touch; less type safety.
- **(β)** Add a discriminated union: `{kind:'component', component_id} | {kind:'item', item_id}`. Cleaner; touches more sites.

Recommendation: **(α)** for this delta. The `source` tag already exists and the posting layer already branches on it.

### 4.4. Idempotency-key namespace

The existing per-row idempotency key format is `PA:<idem>:CONSUME:<source>:<id>` (locked in CLAUDE.md "Production reporting v1"). Extend the source vocabulary:
- `pack` → component consumption from a leaf PACK line
- `base` → component consumption from a BASE-recipe leaf
- `pack-item` → **NEW**: sub-item consumption from an ITEM-typed PACK line

Per-row keys for trio production then look like:
- `PA:<idem>:CONSUME:pack-item:FG-MAR-CLA-300ML`
- `PA:<idem>:CONSUME:pack-item:FG-MAR-STR-300ML`
- `PA:<idem>:CONSUME:pack-item:FG-MAR-PEA-300ML`
- `PA:<idem>:CONSUME:pack:PKG-MARGARITA-TRIO-HOLDER`

### 4.5. Stock ledger row

`stock_ledger` rows for `pack-item` consumption debit `item_id` (not `component_id`). The existing ledger schema must already support item-level entries (Goods Receipt of bought-finished items posts to items, not components). **Verification step before implementation:** confirm `stock_ledger` accepts `item_id` and that the projection-rebuild logic handles it for FG balance.

## 5. Planning explosion delta (deferred — see §6)

The planning function `private_core.fn_explode_bom_to_components` (`0126_fn_explode_bom_to_components_v2.sql`) currently has branches for RAW_NAME/COMPONENT, BASE_BOM, and BOM (raises `unsupported_bom_ref`). Adding an ITEM branch is a **separate** ECP because it implies a multi-pass MRP cascade (trio demand → single demand → component demand). v1 without this branch will silently emit zero component demand for trio's ITEM lines — that is acceptable for the trio's master-data registration but **must** be addressed before trios enter the planning pipeline (Gate 5).

## 6. Out of scope (this delta)

- **Multi-pass MRP cascade** in `fn_explode_bom_to_components`. Will be its own ECP at Gate 5 timeline.
- **BOM list/read Zod** (`api/src/boms/schemas.ts`): already accepts `component_ref_type: string` with no enum constraint; no change needed.
- **BOM line write mutations** (`api/src/boms/line_mutations.ts`): currently hardcodes `'COMPONENT'` (line ~322). Adding parameter exposure is a follow-on; the trio's BOM lines load via the fixture-import SQL path, not through the mutation API.
- **Recursive depth guard.** Trio is 1 level deep (REPACK → MANUFACTURED leaves). Deeper trees (sub-REPACKs of REPACKs) are not authorized in v1; the existing `unsupported_recursive_depth` exception path can be added later if needed.

## 7. Tests (pgTAP)

New file `db/tests/0138_bom_lines_item_ref_type.sql`:

1. CHECK accepts `'ITEM'`; rejects unknown `'XYZ'`.
2. Insert with `ref_type='ITEM'`, `final_item_id` non-null, `final_component_id` NULL → succeeds.
3. Insert with `ref_type='ITEM'`, `final_component_id` non-null → fails (`bom_lines_item_ref_pointer_consistency`).
4. Insert with `ref_type='ITEM'`, `final_item_id` NULL → fails.
5. Insert with `ref_type='COMPONENT'`, `final_item_id` non-null → fails.
6. FK on `final_item_id`: insert with bogus item_id → fails.
7. Existing rows (RAW_NAME/COMPONENT/BASE_BOM) with `final_item_id` NULL still pass (regression).

Integration test (handler): trio production posts 3 stock_ledger rows debiting `FG-MAR-CLA-300ML` / `FG-MAR-STR-300ML` / `FG-MAR-PEA-300ML` and 1 row debiting `PKG-MARGARITA-TRIO-HOLDER`. No rows debit the singles' bottle/cap/label/base components.

## 8. Master-data adds tied to this delta

These fixture entries are **gated on the migration landing** (rows 4–6) or **independent** (rows 1–3):

| # | File | Entry | Schema-dep? |
|---|------|-------|-------------|
| 1 | `fixtures/masters/components.json` | `PKG-MARGARITA-TRIO-HOLDER` (group=PACK_SET, supplier=SUP-005) | No |
| 2 | `fixtures/masters/supplier_items.json` | SUP-005 ↔ PKG-MARGARITA-TRIO-HOLDER | No |
| 3 | `fixtures/masters/items.json` | `FG-MAR-TRIO-300ML` (REPACK, primary_bom=BOM-PACK-MAR-TRIO-300ML) | No (item record itself; PRIMARY_BOM is forward-ref) |
| 4 | `fixtures/masters/bom_head.json` | `BOM-PACK-MAR-TRIO-300ML` (kind=PACK, output_qty=1, output_uom=UNIT) | No |
| 5 | `fixtures/masters/bom_version.json` | `BOM-PACK-MAR-TRIO-300ML::V1_INITIAL` (status=ACTIVE) | No |
| 6 | `fixtures/masters/bom_lines.json` | 4 lines: 3 ITEM (CLA/STR/PEA at qty=1) + 1 COMPONENT (TRIO-HOLDER at qty=1) | **Yes — blocked on migration 0138** |

Carton (`PKG-CARTON-MARGARITA-TRIO`) is **explicitly excluded** per Tom 2026-05-03 (carton ships in/out with the holder; not modeled).

## 9. Routing

This delta touches:
- DB schema + migration (W1)
- pgTAP tests (W1)
- API handler logic (W1 or backend lane)
- No portal changes (W2 unaffected)
- No integrations changes (W4 unaffected)

Recommended: single W1 dispatch covering migration `0138` + handler edit + pgTAP file. Master-data fixture entries 1–5 can land before the dispatch (no contract dependency). Entry 6 (bom_lines) lands with or after the migration.
