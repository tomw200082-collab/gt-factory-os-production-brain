# Data model & exact write templates

Live project: **`gt-ops-prod` = `rvadsozabmxkkrktwgnv`** (Postgres 17, schema
`private_core`). Re-derive with `list_projects` if unsure. All SQL via the
Supabase MCP `execute_sql` (reads) / the GR transaction below (writes, after
confirmation).

## Tables you touch

**Master / read:**
- `suppliers(supplier_id text PK, supplier_name_official, supplier_name_short,
  status, supplier_type, currency, payment_terms, green_invoice_supplier_id, …)`
- `components(component_id text PK, component_name, component_class
  [INGREDIENT|PROCESS_SUPPLY|PACKAGING|PACKAGING_SET], status, inventory_uom,
  purchase_uom, purchase_to_inv_factor numeric, primary_supplier_id,
  std_cost_per_purchase_uom, std_cost_per_inv_uom, moq_purchase_uom, …)`
- `items(item_id text PK, item_name, item_type, status, barcode, sku, …)` — FG only.
- `supplier_items(supplier_item_id uuid, supplier_id, component_id, item_id,
  is_primary, order_uom, inventory_uom, pack_conversion numeric,
  std_cost_per_inv_uom numeric, approval_status, notes, …)` — supplier↔item link
  + supplier-scoped cost. **No supplier-SKU column** — map by name/price/crossref.
- `uom(uom_code text PK, uom_name, uom_family, factor_to_base, …)` — known codes
  include `L`, `KG`, `BOTTLE`, `EACH`. Confirm the line's unit exists here.
- `purchase_orders(po_id text PK, po_number, supplier_id, status, source_type, …)`
  and `purchase_order_lines(po_line_id uuid, po_id, line_number, component_id XOR
  item_id, ordered_qty, uom, unit_price_net, line_status, …)`.

**Write (the receipt, in one transaction — mirrors `goods-receipts/handler.ts`):**
- `form_submissions(submission_id uuid, form_type, idempotency_key UNIQUE,
  submitted_by uuid, event_at, status, posted_at, posted_by, raw_payload jsonb
  NOT NULL, site_id default 'GT-MAIN')`
- `goods_receipts(submission_id uuid, supplier_id, po_id, notes)`
- `goods_receipt_lines(line_id uuid, submission_id, item_type [FG|RM|PKG],
  item_id, quantity numeric, unit, po_line_id uuid, notes)`
- `stock_ledger(movement_id uuid, idempotency_key NOT NULL, movement_type,
  item_type, item_id, qty_delta, uom, event_at, post_status default 'POSTED',
  reported_at, reported_by_user_id, reported_by_snapshot, posted_by_user_id,
  source_channel, source_event_id, source_id, related_po_line_id, site_id)` —
  **append-only**; an `AFTER INSERT` trigger updates current balances and rolls
  up PO `received_qty` when `related_po_line_id` is set.

## Pre-write reads (always run)

```sql
-- Tom's user id for submitted_by / posted_by / reported_by_user_id
select user_id, display_name from private_core.app_users
where lower(email) = 'tom@gteveryday.com';

-- supplier's catalog to match lines against (also detects price)
select c.component_id, c.component_name, c.component_class, c.status,
       c.inventory_uom, c.purchase_uom, c.purchase_to_inv_factor,
       c.std_cost_per_inv_uom, si.supplier_item_id, si.std_cost_per_inv_uom si_cost,
       si.pack_conversion, si.order_uom, si.inventory_uom si_inv_uom, si.notes
from private_core.components c
left join private_core.supplier_items si
       on si.component_id = c.component_id and si.supplier_id = :supplier_id
where c.primary_supplier_id = :supplier_id or si.supplier_id = :supplier_id
order by c.component_name;

-- open POs to (maybe) attach to
select po.po_id, po.status, l.po_line_id, l.component_id, l.item_id,
       l.ordered_qty, l.uom, l.line_status
from private_core.purchase_orders po
join private_core.purchase_order_lines l on l.po_id = po.po_id
where po.supplier_id = :supplier_id and po.status = 'OPEN'
order by po.po_id, l.line_number;

-- on-hand BEFORE (per mapped component) — capture for the before/after proof
select item_id, sum(qty_delta) as on_hand
from private_core.stock_ledger
where item_id = any(:component_ids) and post_status = 'POSTED'
group by item_id;
```

## The Goods Receipt write — single atomic, idempotent statement

Fill the `VALUES` line list (one row per **mapped, confirmed** inventory line;
quantities already converted to **inventory UOM**). Deposit/delivery/fee lines
are NOT included. `:key = GRINV:<supplier_id>:<document_no>`.

```sql
with sub as (
  insert into private_core.form_submissions
    (form_type, idempotency_key, submitted_by, event_at, status, posted_at, posted_by, raw_payload)
  values
    ('goods_receipt', :key, :uid, :event_at, 'posted', now(), :uid, :raw_payload::jsonb)
  returning submission_id
),
hdr as (
  insert into private_core.goods_receipts (submission_id, supplier_id, po_id, notes)
  select submission_id, :supplier_id, :po_id, :hdr_notes from sub
  returning submission_id
),
ln as (
  insert into private_core.goods_receipt_lines
    (submission_id, item_type, item_id, quantity, unit, po_line_id, notes)
  select sub.submission_id, x.item_type, x.item_id, x.quantity, x.unit, x.po_line_id, x.notes
  from sub cross join (values
    -- (item_type, item_id, qty_inv_uom, unit, po_line_id, note)
    ('RM','RAW-EXAMPLE', 30.0, 'L', null::uuid, 'KillBill INV <doc> line N')
  ) as x(item_type, item_id, quantity, unit, po_line_id, notes)
  returning line_id, submission_id, item_type, item_id, quantity, unit, po_line_id
)
insert into private_core.stock_ledger
  (idempotency_key, movement_type, item_type, item_id, qty_delta, uom, event_at,
   reported_at, reported_by_user_id, reported_by_snapshot, post_status,
   posted_by_user_id, source_channel, source_event_id, source_id, related_po_line_id)
select 'GR:'||:key||':'||ln.line_id, 'GR_POSTED', ln.item_type, ln.item_id,
       ln.quantity, ln.unit, :event_at, now(), :uid, :uname, 'POSTED',
       :uid, 'FORM', ln.submission_id::text, ln.line_id::text, ln.po_line_id
from ln
returning movement_id, item_id, qty_delta;
```

**Idempotency:** the `form_submissions.idempotency_key` UNIQUE constraint raises
SQLSTATE 23505 on a re-send; the whole statement rolls back → nothing posts.
To confirm a prior post, read `form_submissions` by `idempotency_key` and join
through `goods_receipt_lines` to `stock_ledger`.

**Verify AFTER:** re-run the on-hand read above; `after − before` must equal the
posted `qty_delta` per component.

## Price update (guarded — planner/admin; only on confirmation)

Before writing, read the exact audit-table shapes (locked 11-col `change_log`,
`price_history`) — they are introspected, not assumed:

```sql
select column_name, data_type, is_nullable from information_schema.columns
where table_schema='private_core' and table_name in ('price_history','change_log')
order by table_name, ordinal_position;
```

Then, in one transaction: `update private_core.supplier_items
set std_cost_per_inv_uom = :new_cost, updated_at = now() where supplier_item_id = :sii;`
plus an insert into `price_history` and a `change_log` row with action
`SUPPLIER_PRICE_UPDATE_MANUAL` (see `gt-factory-os/db/migrations/0025_change_log_and_price_history.sql`
for the exact column list and the allowed action enum). If no `supplier_items`
row exists for this supplier+component, create it first (this sets the first cost).

## Back-create a manual PO (optional, for full audit chain)

Use the existing function rather than hand-inserting:
`select * from private_core.fn_create_manual_po(...);` — read the signature in
`gt-factory-os/db/migrations/0095_fn_create_manual_po.sql` and the request shape
in `gt-factory-os/api/src/purchase-orders/schemas.ts` before calling. Set
`source_type='manual'`, reason = "retroactive — arrived without an open PO".
Then put the returned `po_id` on the GR header and the line `po_line_id`s on the
matching GR lines so the trigger rolls up `received_qty`.

## Create a new component (round-4 flow — only after Tom approves the draft)

First introspect required columns (don't assume NOT NULLs):
```sql
select column_name, data_type, is_nullable, column_default
from information_schema.columns
where table_schema='private_core' and table_name='components' order by ordinal_position;
```
Then, in one transaction, insert the component and its supplier link:
```sql
insert into private_core.components
  (component_id, component_name, component_class, status, inventory_uom,
   purchase_uom, purchase_to_inv_factor, primary_supplier_id,
   std_cost_per_purchase_uom, std_cost_per_inv_uom, planned_flag, notes)
values
  (:component_id, :name, :class /* INGREDIENT|PROCESS_SUPPLY|PACKAGING|PACKAGING_SET */,
   'ACTIVE', :inv_uom, :purchase_uom, :purch_to_inv, :supplier_id,
   :cost_per_purchase_uom, :cost_per_inv_uom, true,
   'Created from <supplier> invoice <doc> on <date>');

insert into private_core.supplier_items
  (supplier_id, component_id, is_primary, order_uom, inventory_uom,
   pack_conversion, std_cost_per_inv_uom, approval_status, notes)
values
  (:supplier_id, :component_id, true, :purchase_uom, :inv_uom,
   :purch_to_inv, :cost_per_inv_uom, 'approved',
   'Created from invoice <doc>');
```
Component id convention: `RAW-<SHORT-NAME>` for ingredients, mirroring existing
ids (e.g. `RAW-VODKA`, `RAW-BLUEBERRY-SYRUP-VEDRENNE`). Use UPPER-KEBAB. After
creating, also append the supplier-SKU mapping to `crossref.json`.

## Roles
- Goods Receipt: operator and above.
- Manual PO create + price update: planner/admin only.
- Tom is admin → can do all of the above.
