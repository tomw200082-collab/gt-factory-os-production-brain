---
name: goods-receipt-from-invoice
description: Use when Tom sends a supplier tax invoice (photo or PDF) or describes goods that arrived (labels, bottles, raw materials, packaging, anything). Extracts every detail, presents for Tom's approval, then posts a goods receipt, updates prices with change alerts, and captures the exact procurement spec (dimensions, materials, grind, supplier catalog wording) into the procurement-spec store. Never posts before Tom approves the extraction.
---

# Goods Receipt from Invoice

## Purpose (why precision matters)

Every invoice Tom sends is a brick in the procurement-spec database. The long-term goal
(per Tom, 2026-06-12): when production planning runs, the system can auto-generate exact
supplier order messages — supplier's own wording, exact dimensions/materials, expected
cost, price-change detection. Ordering from suppliers (especially Miki Madbekot) is
error-prone if any detail is remembered wrong. Therefore: capture EVERYTHING, exactly.

## Non-negotiable workflow

1. **Extract** everything from the invoice/photo (see checklist below).
2. **Verify against live DB** (items exist, current balances, open POs, last prices).
3. **Present to Tom for approval** — table of lines, quantities, before/after balances,
   price comparison, any new components to create, any ambiguity flagged.
4. **Only after explicit approval: post.** One atomic transaction.
5. **Verify** post-insert (balances match expected) and report with evidence.

## Extraction checklist (per invoice)

- Supplier (match to `suppliers.supplier_id`), invoice number, invoice date,
  delivery note (תעודת משלוח), payment terms, payment due date.
- Per line: supplier's description **verbatim** (Hebrew), quantity, unit price net,
  line total. Cross-check: Σ lines = total before VAT; VAT (18%); grand total. If the
  math doesn't close, stop and ask.
- Physical spec from descriptions: dimensions (mm), shape, material (e.g. PP לבן /
  PP כסף), finish (למינציה מט), print method (פרוצס), color, design names, grind type
  (for raw materials), bag/carton spec.
- Anything Tom explains verbally about the goods → goes into the spec store too.

## Mapping rules

- Map each invoice line to `private_core.components` component_id(s).
- **Split combined lines**: suppliers bundle several designs into one line
  ("X סוגים"). Split by Tom's physical description (e.g. invoice 2026/261663 line 3:
  5,000 units "2 סוגים" = 4,000 × 18G-back + 1,000 × 500G-back).
- **Supplier catalog names can be misleading** (e.g. Miki calls the matcha carton
  sticker "מצ'ה 500"). Record their wording verbatim in the spec store with a WARNING,
  but name our component by what it actually is.
- If a component doesn't exist: propose creating it, cloning the closest sibling's
  template (class/group/UOM/policy/supplier/lead time), with full spec in `notes`.
  Also create its `supplier_items` row (relationship PRIMARY, is_primary true).
- Check open `purchase_order_lines` for the items; link `po_line_id` if one exists,
  otherwise PO-less receipt (po_id null).

## Posting pattern (live DB: Supabase project `rvadsozabmxkkrktwgnv`, schema `private_core`)

One atomic statement (CTE chain). Reference precedent: submissions
`295b34de` (Kill Bill IN264001590), `9f1471d5` (Miki 2026/261659), `a071ff77` (Miki 2026/261663).

1. `form_submissions`: form_type `goods_receipt`, idempotency_key
   `GRINV:<SUPPLIER_ID>:<doc-no>` (slashes → dashes), status `posted`,
   event_at = arrival date, submitted_by/posted_by = Tom
   (`0db008a9-05e3-4521-8b30-42e5d444818d`), site `GT-MAIN`.
   `raw_payload` = full structured evidence: document info, totals, vat_rate,
   payment terms/due, posted_lines (item_id, qty, unit_price_net, invoice_line),
   mapping_note for any line splits or naming discrepancies.
2. `goods_receipts`: submission_id, supplier_id, po_id, human-readable notes.
3. `goods_receipt_lines`: one per component (item_type e.g. `PKG`/`RM`, unit = inventory UOM).
4. `stock_ledger`: one `GR_POSTED` row per line. idempotency_key
   `GR:<fs_idempotency_key>:<line_id>`; source_id = line_id, source_event_id =
   submission_id, source_channel `FORM`, post_status `POSTED`. Do NOT write
   `balance_key` (generated column). The after-insert trigger updates
   `current_balances` automatically.
5. Verify: `current_balances.calculated_on_hand` equals expected for every item.

## Price handling (every invoice, every line)

- Compare invoice unit price to the component's `std_cost_per_inv_uom` and last
  `price_history` row. **If different → alert Tom immediately** (old → new, %).
- After approval: update `components.std_cost_per_purchase_uom` +
  `std_cost_per_inv_uom`, `supplier_items.std_cost_per_inv_uom`, and insert a
  `price_history` row (supplier_item_id + component_id, unit_price_net, source
  `manual`, source_document_id = invoice number, descriptive notes).
- If Tom approves applying a price to a wider family (identical spec), record that
  reasoning in the price_history notes.

## Procurement spec store (`private_core.component_procurement_specs`)

Upsert one row per component+supplier (UNIQUE constraint) on every invoice:

- `supplier_catalog_wording` — supplier's exact wording, verbatim Hebrew. This is
  what gets copied into future orders.
- `spec` (jsonb) — structured: type, product, shape, dimensions_mm
  (width/height or diameter), material, color, finish, print, design, grind,
  packaging. Machine-readable for future order automation.
- `ordering_notes` — quirks: combined-line tricks ("order both backs as one line
  '2 סוגים'"), misleading supplier names, roll sizes, MOQ behavior.
- `last_unit_price_net`, `last_price_invoice_ref`, `last_price_date`, `source`.

## Corrections

`stock_ledger` is append-only (UPDATE/DELETE rejected by trigger). Quantity fixes:

- Receipt qty wrong → `GR_REVERSAL` row (negative, related_movement_id set) and/or
  corrective `GR_POSTED` row; keep `goods_receipt_lines` + `raw_payload` consistent
  with notes explaining the correction.
- Tom states a true on-hand total → keep the receipt matching the invoice, post a
  `COUNT_ADJUST` (source_channel `MANUAL_ADJUSTMENT`) for the difference, with the
  arithmetic spelled out in notes.
- If receipt total diverges from invoice total, flag it explicitly to Tom.

## Future ordering support (the payoff)

When Tom asks "what do I order from <supplier>": pull specs + last prices from
`component_procurement_specs`, current stock from `current_balances`, produce a
ready-to-send order text in the supplier's own wording with expected cost. When the
matching invoice arrives, diff prices and alert.

## Hard rules

- Never post before Tom approves the extraction.
- Never UPDATE/DELETE ledger rows.
- Never guess: unreadable/ambiguous invoice text or unmatched lines → hold the line
  (precedent: Kill Bill held_lines) and ask.
- Invoice math must close (lines → net → VAT → total) before posting.
- All evidence (document numbers, splits, discrepancies) goes into `raw_payload`.

## LEARNED — append-only log

> Self-compaction: when this log passes 30 lines, distil it into the sections above,
> clear the log, and stamp "Last distilled &lt;date&gt;" here.

**2026-08-30 — how to actually write, from a Claude-Code-on-the-web session.**
The Supabase MCP `execute_sql` is **read-only** — any INSERT/UPDATE, and even
`rebuild_verifier()` (it truncates a shadow table), fails with
`25006: cannot execute ... in a read-only transaction`. Writes go through
`apply_migration`. Direct Postgres is also out: `psql` exists and `DATABASE_URL` /
`DATABASE_URL_POOLED` are set, but sandbox egress is HTTPS-only — the direct host
errors instantly and the pooler hangs until timeout. Do not burn minutes there.
Established naming precedent in `supabase_migrations.schema_migrations`, follow it:
`data_goods_receipt_<supplier>_inv_<number>` for the receipt, then a separate
`check_rebuild_verifier_after_gr_<number>`. A migration that raises an exception
rolls back cleanly and is not recorded — safe to use a deliberate `RAISE EXCEPTION`
as a read channel for a function that needs write access.

**2026-08-30 — `rebuild_verifier()` returns a scalar, not a row set.**
`SELECT count(*) FROM private_core.rebuild_verifier()` is **always 1** and looks like
one mismatch. Correct gate: `SELECT private_core.rebuild_verifier()` INTO a numeric
and compare to 0. This produced a false "STOCK TRUTH GATE FAILED" on a healthy DB.

**2026-08-30 — Neve HaTavlin (SUP-023) document shape,** invoice SI266009841.
Numbering series is `SI266xxxxxx`; note that a `supplier_items.source_basis` on the
**Tavlinei Bar** row cites "SI266008217", which is this series — that price basis is
probably mis-attributed between the two spice suppliers, verify before trusting it.
Document type `חשבונית מס מרכזת` (consolidating tax invoice) can cover several
delivery notes: **confirm with Tom it was one physical shipment before posting**, or
the receipt double-counts goods already received. Their totals block prints a
`הנחה כללית` line whose **sign is inverted** — the "-0.16 discount" was really a
+0.16 round-up to land the grand total on a round ₪3,752.00. Reconcile
lines → net → adjustment → VAT → total and record the adjustment as its own
rounding fact in `raw_payload`; never fold it into a unit price.
Line UOM trap: line 1 was `38.00 יח` of "היבסקוס מצרי 1 ק\"ג" — units, where each
unit is a 1 kg bag, so 38 units = 38 KG. Line 2 was priced per kg directly.

**2026-08-30 — check "first purchase from this supplier" against the data.**
Handwriting on the invoice said `קנייה ראשונה`; `SELECT count(*) FROM goods_receipts
WHERE supplier_id = ...` returned 0, which confirmed it. Cheap, and it catches both a
missed earlier receipt and a supplier record that is a duplicate of an existing one.

**2026-08-30 — `supplier_items` has a partial unique index
`uniq_supplier_items_component_primary` on `(component_id) WHERE is_primary`.**
Only one primary supplier per component. When switching primaries in bulk you must
**demote the incumbents first, then promote** — doing it in the other order fails with
`23505 duplicate key`. Note also that `relationship` (text) and `is_primary` (bool)
drift apart: rows exist with `relationship='PRIMARY', is_primary=false` and the
reverse. `is_primary` is the one the index enforces; treat `relationship` as a label
that needs repairing alongside it.
