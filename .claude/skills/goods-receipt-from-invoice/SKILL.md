---
name: goods-receipt-from-invoice
description: >-
  Turn a photo of a supplier document (tax invoice / חשבונית מס, delivery note /
  תעודת משלוח, invoice-receipt / חשבונית מס קבלה, credit note / חשבונית זיכוי)
  into the correct GT Factory OS actions: identify the supplier, map every line
  to the internal component/item, detect price changes, reconcile against any
  open purchase order (or post a PO-less receipt when none was opened), post the
  Goods Receipt to live stock truth, and update supplier prices — all behind one
  human confirmation. Use whenever Tom sends an image of a purchase that arrived,
  an invoice, a delivery, or a supplier price document, even if he writes only a
  short note like "הזמנת רכש שהגיעה" or "תקלוט את זה".
---

# Goods Receipt from a Supplier Invoice

You receive a photo (sometimes several) of a supplier document and a short note.
Your job is to do the full back-office job a careful purchasing clerk would do,
**without ever guessing on stock truth**, and post it into GT Factory OS.

This skill operates against the **live production database** `gt-ops-prod`
(`rvadsozabmxkkrktwgnv`). Reads are free. **Writes to stock truth, prices, POs,
or master data require Tom's explicit "post it" confirmation on the resolved
package** (see §6 Governance). Re-sending the same document never double-posts
(idempotency, §5).

---

## The one rule that governs everything

> **Stock truth is the product.** A wrong receipt corrupts on-hand balances,
> which corrupts planning, which corrupts purchasing. So: extract precisely,
> map with evidence, **show Tom the resolved package, get one confirmation,
> then post.** Never post a line you could not map with confidence.

If the photo is too low-resolution to read a line's description, quantity, or
price — **say so and ask for a sharper photo of that line.** Do not infer.

---

## Pipeline (run in order)

### 1. Extract the document (vision)
Read the image(s) and produce a structured extraction. Hebrew is RTL; numbers
are LTR. Capture:

- **Document type** — חשבונית מס (tax invoice) · תעודת משלוח (delivery note) ·
  חשבונית מס/קבלה (invoice-receipt) · חשבונית זיכוי (credit note → *negative*
  quantities, a return/reversal) · הצעת מחיר (quote → **price only, never a
  receipt**).
- **Supplier** — name (Hebrew + Latin), ח.פ / ע.מ (company id), contact, email.
- **Document number** (e.g. `IN264001590`), **document date**, **order ref** if any.
- **Currency** (default ILS) and **VAT rate** (Israel = 18% in 2026).
- **Line items**, each: supplier catalog no. (מק"ט), description (תיאור),
  quantity (כמות), unit, **unit price net** (מחיר יח׳), line total (סה"כ),
  per-line discount (הנחה).
- **Totals**: subtotal (סה"כ), document discount, VAT (מע"מ), grand total
  (סה"כ כולל מע"מ). **Deposit / פיקדon** and **delivery / משלוח** lines are
  charges, *not* stock — flag them separately, never receive them as inventory.
- Mark a **confidence** (high / medium / low) on every field you had to read off
  a blurry area.

Sanity-check the arithmetic: `Σ line_total − discount + VAT ≈ grand_total`. If it
doesn't reconcile, surface the discrepancy — it usually means a misread line.

### 2. Resolve the supplier
Query `private_core.suppliers` by name (official + short, Hebrew & Latin), by
`ח.פ`, and by `green_invoice_supplier_id`. Confirm `status = 'ACTIVE'`.
- **Not found** → propose creating the supplier (planner/admin action) and stop
  for confirmation. Do not invent a supplier_id.
- Record the matched `supplier_id`.

### 3. Map each line to an internal component / item — *the hard part*
**There is no supplier-SKU column in the schema.** The supplier's catalog
numbers (מק"ט) are not stored. So map by, in order:

1. **Learned cross-reference** — `reference/crossref.json` in this skill folder.
   Keyed by `supplier_id` + supplier catalog no. (and/or normalized description).
   If a confirmed mapping exists, use it (high confidence).
2. **Description match** — fuzzy match the Hebrew/English description against
   `private_core.components.component_name` (and `items.item_name` for FG).
3. **Price corroboration** — implied unit price (net, ex-VAT, per purchase UOM)
   vs `supplier_items.std_cost_per_inv_uom` / `components.std_cost_per_*`.
   An exact price match strongly confirms a description match.
4. **UOM reconciliation** — invoice unit vs `components.purchase_uom` /
   `inventory_uom` with `purchase_to_inv_factor` (and `supplier_items.pack_conversion`).
   You must post the Goods Receipt **in inventory UOM**, so convert:
   `inv_qty = invoice_qty_in_purchase_uom × purchase_to_inv_factor`.

Pull the supplier's catalog once to match against (see `reference/data-model.md`
for the query). Output a **mapping table** with per-line confidence and the
evidence used. Any line below high confidence is **held for Tom**, not posted.

- **No internal component matches** → propose creating the component (admin) or
  ask Tom which existing component it is. Never receive into a guessed component.

### 4. Detect price changes & propose updates
For each mapped line compute the invoice **net unit price per inventory UOM** and
compare to the current `supplier_items.std_cost_per_inv_uom` (fallback
`components.std_cost_per_inv_uom`). If it differs beyond ±1 %:
- Propose a **SUPPLIER_PRICE_UPDATE** (writes `supplier_items.std_cost_per_inv_uom`
  + a `price_history` row + a `change_log` row — see `reference/data-model.md`).
- Show old → new, and the % change. This is a **guarded write** (planner/admin),
  separate from the receipt; Tom approves it in the same confirmation step but it
  is listed distinctly.
- If `supplier_items` has no cost yet (NULL / "Price TBD"), this *sets the first
  real cost* — call that out, it's high-value.

### 5. Reconcile against the purchase order ("was it open?")
Search open POs for this supplier (`purchase_orders.status = 'OPEN'` + lines).
- **Matching open PO line found** → attach: set `po_id` on the GR header and
  `po_line_id` on the matching line. The DB triggers roll up `received_qty` and
  advance PO/line status. This is the happy path.
- **No open PO** (the common real case — *"היא לא הייתה פתוחה"*): a **PO-less
  receipt is explicitly allowed** (LOCKED_DECISIONS.md §Goods Receipt). Offer Tom
  two options:
  - **(a) PO-less GR** — receive with `po_id = null`. Fastest, fully legitimate.
  - **(b) Back-create a PO then receive** — create a `source_type='manual'` PO
    (reason: "retroactive — goods/invoice arrived without an open PO"), then GR
    against it, for a complete paper trail. Recommend (b) when the amount is
    material or Tom wants the audit chain; (a) otherwise.

### 6. Governance gate — STOP and confirm
Before any write, present **one consolidated package**:
- supplier (id + name), document no., date;
- the mapping table (line → component_id, qty in inv UOM, confidence);
- price updates (old → new), if any;
- new master data to create (supplier/component), if any;
- PO decision (attach / PO-less / back-create);
- the exact stock delta this will cause (component → +qty inv UOM);
- the idempotency key.

Then ask Tom to confirm. **Only on explicit "post it" / "תקלוט" do you write.**
- Reads: always allowed. Writes to stock_ledger / prices / POs / masters: only
  after confirmation.
- This respects the kernel principle that Claude tooling is not an autonomous
  runtime path — the human stays in the loop on every stock-truth mutation.

### 7. Post (idempotent, single transaction)
Resolve Tom's `app_users.user_id` (by email `tom@gteveryday.com`) for
`submitted_by` / `posted_by` / `reported_by_user_id`. Build a deterministic
idempotency key: **`GRINV:<supplier_id>:<document_no>`** (e.g.
`GRINV:SUP-010:IN264001590`). Re-running the same document replays, never
double-posts.

Post via the canonical path. From a Claude session that path is a **single SQL
transaction** that mirrors the production handler
(`gt-factory-os/api/src/goods-receipts/handler.ts`) exactly:
`form_submissions` → `goods_receipts` → `goods_receipt_lines` → `stock_ledger`
(`movement_type='GR_POSTED'`, `source_channel='FORM'`). The full, exact
transaction template (and the price-update + manual-PO templates) is in
`reference/data-model.md`. Use `BEGIN … COMMIT`; the `form_submissions`
idempotency UNIQUE constraint is the double-post guard.

### 8. Verify & learn
- Re-read the new `stock_ledger` rows and the affected balances; show Tom
  **before → after on-hand** per component. Stock projection must equal the
  ledger sum.
- Append every **confirmed** line mapping to `reference/crossref.json`
  (supplier_id + supplier SKU + normalized description → component_id) so the
  next invoice from this supplier maps automatically.
- Commit the crossref update on the working branch (skill state is durable;
  receipts are in the DB, not git).

---

## Quick reference

| Thing | Where |
|---|---|
| Live prod project | `gt-ops-prod` = `rvadsozabmxkkrktwgnv` (re-derive via `list_projects`) |
| Schema, exact write SQL, price + PO templates | `reference/data-model.md` |
| Learned supplier-SKU → component map | `reference/crossref.json` |
| GR handler being mirrored | `gt-factory-os/api/src/goods-receipts/handler.ts` |
| Locked rules (PO-less receipt, append-only ledger) | `gt-factory-os-production-brain/docs/decisions/LOCKED_DECISIONS.md` §Receipts/Goods Receipt |

## Hard guardrails (never violate)
- Never post a line you mapped with low confidence — hold it for Tom.
- Never receive deposit / delivery / fee lines as inventory.
- `stock_ledger` is **append-only** — corrections are *reversal rows*, never
  UPDATE/DELETE. A wrong receipt is fixed by a `GR_REVERSAL`, not an edit.
- Receive in **inventory UOM**, after applying the purchase→inv conversion.
- A credit note (חשבונית זיכוי) is a **return** → negative movement, different
  movement semantics; confirm with Tom before posting.
- No autonomous write without the §6 confirmation. Idempotency key is mandatory.
