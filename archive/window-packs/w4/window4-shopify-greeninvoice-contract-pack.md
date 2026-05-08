# Window 4 — Shopify FG-Sync + Green Invoice Ingest Contract Pack

**Owner:** Window 4 (Integrations / Jobs / Exports / Dashboard Contracts)
**Status:** contract-only. NO live calls, NO runtime, NO DDL, NO portal, NO scheduler wiring, NO token work. Gate 4 precursor — parallel-safe with Gate 3.
**Authored:** 2026-04-17
**Superseding evidence for Green Invoice sections:** [window4-greeninvoice-inspection-report.md](window4-greeninvoice-inspection-report.md) is the **authoritative evidence source** for Green Invoice auth, endpoints, enums, and field shapes. Where this pack's Phase C statements conflict with the inspection report (e.g., VAT type as string vs integer; income `price`/`quantity` as string-decimal vs float/int), the inspection report wins. Supplier/expense surface remains narrowly unresolved at U.GI.1–U.GI.8 per the report.
**Sibling packs:**
- [window4-lionwheel-contract-pack.md](window4-lionwheel-contract-pack.md)
- [window4-lionwheel-runtime-handoff.md](window4-lionwheel-runtime-handoff.md)
- [window4-integrations-sandbox/](window4-integrations-sandbox/)

Doc sources (public; no credentials used in this pass):

- **Shopify Admin GraphQL:** `shopify.dev/docs/api/admin-graphql/latest/mutations/inventorySetQuantities`, `/objects/InventoryLevel`, `/mutations/inventoryAdjustQuantities`, `/input-objects/InventoryLevelInput`
- **Green Invoice:** `api.greeninvoice.co.il/api/v1` (declared by the `bariew/greeninvoice` PHP client README); public Valigara field-mapping doc `help.valigara.com` for outbound document shapes; Apiary reference `greeninvoice.docs.apiary.io` (iframe-heavy — raw text not crawlable; shape-level claims below rely on the rendered sections and publicly mirrored client libraries, with every unresolved field explicitly flagged)

The pack holds two boundary contracts in one document per the lane-switch directive. Each boundary is independently self-consistent; each has its own blocker register and first-slice definition. The shared `integration_run` contract stays reused from the LionWheel pack — no new jobs-log contract is introduced.

---

# Phase A — Source-of-truth restatement

Per `CLAUDE.md` §3.4 / §3.5 (the locked source-of-truth map):

## Shopify

- **Authoritative for:** nothing operationally critical inside the factory.
- **Role:** FG stock sync target. The platform computes FG stock truth from the ledger and pushes levels out to Shopify.
- **Conflict rule:** if Shopify and the platform disagree on FG stock for a SKU, **the platform wins**. Shopify is eventually consistent with the platform; never the reverse.
- **Reconciliation:** periodic exception-based drift review. Drift → exception in the Exceptions Inbox (Gate 3 surface); the platform re-pushes authoritative values.

## Green Invoice

- **Authoritative for:** supplier invoice **evidence** (the document + its line items) and **price history** (each observed per-SKU supplier price at invoice time).
- **NOT authoritative for:** active supplier prices. Active prices update only when mapping is unambiguous AND the price delta is within threshold. Outside that guardrail, the platform continues to use its current active price.
- **Never:** auto-create a `component` row from a line item on an invoice. Unmapped line items route to an exception, not to a new master.
- **Semantics:** net-of-VAT for cost values stored as active price / price history; VAT preserved separately on the evidence mirror for audit.

## Observed cross-integration context (not contract definitions; inputs to the packs below)

- `task.wp_order_key` on a LionWheel task with `creation_origin="shopify"` is the **Shopify order id**. The Shopify → LionWheel task auto-creation path already exists. Platform **does not** re-ingest customer orders from Shopify; it reads them from the LionWheel mirror. Shopify is therefore **outbound FG-only** from the platform's perspective.
- `task.driver_note` on a LionWheel task has been observed to contain a Green Invoice signed-document URL. This is a GT-side existing cross-link (shipment invoice attached to a delivery). Does **not** define the Green Invoice ingest boundary; the ingest boundary concerns supplier invoices, not shipment invoices.

---

# Phase B — Shopify FG-sync boundary contract

## B.1 Direction and role

- **Direction:** **outbound** platform → Shopify.
- **Purpose:** keep Shopify's `available` (and optionally `on_hand`) inventory levels aligned with the platform's FG stock projection, per SKU, per authoritative location.
- **Explicit non-goals:** reading customer orders from Shopify, reading product catalog from Shopify, reading prices from Shopify, writing anything other than inventory quantities.

## B.2 API surface (Shopify Admin GraphQL, verbatim)

**Primary mutation:** `inventorySetQuantities(input: InventorySetQuantitiesInput!)`

**`InventorySetQuantitiesInput` fields (verbatim):**

| Field | Required | Purpose |
|---|---|---|
| `name` | yes | quantity-name enum; GT uses `"available"` and possibly `"on_hand"` |
| `reason` | yes | free-form-ish string; documented example `"correction"`; enum **UNRESOLVED** beyond this |
| `referenceDocumentUri` | no | URI the platform supplies for audit cross-link (e.g. back-ref to `integration_run.trace_id`) |
| `ignoreCompareQuantity` | no | default false; when false, mutation refuses the change unless persisted quantity == compareQuantity |
| `quantities` | yes | array of `InventoryQuantityInput` |

**`InventoryQuantityInput` fields (verbatim):**

| Field | Required | Purpose |
|---|---|---|
| `inventoryItemId` | yes | Shopify inventory item GID |
| `locationId` | yes | Shopify location GID |
| `quantity` | yes | absolute quantity (this is **set**, not delta) |
| `compareQuantity` | yes (when `ignoreCompareQuantity=false`) | last quantity the platform saw — enables optimistic concurrency |
| `changeFromQuantity` | optional from API version `2026-01+` | alternative to `compareQuantity` |

**Idempotency:** as of API version `2026-04+`, idempotency is **required** via the `@idempotent` directive. Platform runtime must generate and persist an idempotency key per push attempt; the key is bound to a single `integration_run`.

**Alternate mutation (delta form):** `inventoryAdjustQuantities` — relative change. **Not chosen for v1**; platform authoritativeness requires absolute-set semantics with compare-and-set, not deltas.

**Required OAuth scope:** `write_inventory`.

## B.3 Read surface (for reconciliation, outbound sync needs no reads)

**Object:** `InventoryLevel` — quantities of one `InventoryItem` at one `Location`.

**`InventoryLevel` fields (verbatim):**

| Field | Type | Purpose |
|---|---|---|
| `id` | `ID!` | GID |
| `canDeactivate` | `Boolean!` | reconciliation hint |
| `createdAt` | `DateTime!` | |
| `deactivationAlert` | `String` | |
| `isActive` | `Boolean!` | skip inactive levels during reconciliation |
| `item` | `InventoryItem!` | join to SKU |
| `location` | `Location!` | join to physical location |
| `quantities` | `[InventoryQuantity!]!` | per-name quantities; accepts `names` argument to filter |
| `updatedAt` | `DateTime!` | watermark candidate |
| `scheduledChanges` | `InventoryScheduledChangeConnection!` | **UNRESOLVED** whether GT uses scheduled changes; mirror-persist only if observed |

**Quantity name enum (partially enumerated in public docs):** `available`, `on_hand`, `incoming`, `committed`, plus additional names referenced as "inventory states" in Shopify fulfillment docs (`reserved`, `damaged`, `safety_stock`, `quality_control` appear in some docs but were not verified verbatim this pass — **UNRESOLVED**).

## B.4 Fields actively required on the GT side

**Required for v1 per SKU push:**

- **platform SKU** → maps to Shopify `InventoryItem.sku` (join key; must match exactly, including casing).
- **Shopify `inventoryItemId`** — resolved at mapping time by SKU lookup; persisted in a Window-1-owned mapping table (see B.9).
- **Shopify `locationId`** — the authoritative location for GT's FG stock. GT has **one authoritative FG location** in v1 (UNRESOLVED — operator confirmation).
- **platform-computed quantity** — from the FG projection, net of platform-internal allocations.
- **compareQuantity** — the previous quantity the platform sent in the last successful push for this SKU + location. Maintained in the `shopify_sku_sync_state` row (B.9).

**NOT required for v1:** variants, cost-of-goods, product titles, images, prices.

## B.5 Update cadence

- **Event-driven:** when a stock-truth event lands in `stock_ledger` for an FG SKU, enqueue a sync task for that SKU.
- **Periodic reconciliation:** once per N minutes (UNRESOLVED, operator-set, proposed 30 min during business hours), read all `InventoryLevel`s for GT's location via paginated query, diff against projection, emit exceptions for mismatches and trigger re-push.
- **Scheduler wiring is out of this pack.**

## B.6 Conflict / drift rules (Shopify side)

| Situation | Resolution |
|---|---|
| Shopify `available` ≠ platform projection for SKU at location | **platform wins**; re-push absolute `quantity` with current `compareQuantity` = Shopify's value (so the set succeeds on first try); emit reconciliation exception |
| Shopify SKU exists with no platform `items` row | **exception**; never auto-create an `items` row from Shopify; route to Exceptions Inbox for manual mapping or exclusion |
| Platform SKU exists with no Shopify `inventoryItemId` mapping | **exception**; SKU is not synced until mapping is resolved (either manually added or marked "no-sync") |
| Compare-and-set failure (`compareQuantity` mismatch) | retry once with refreshed `compareQuantity`; if still mismatching after one refresh, **escalate** as `shopify_concurrent_update` exception |
| Shopify `Location.isActive = false` for the target location | halt sync, emit `shopify_location_inactive` alert |
| Shopify SKU exists for multiple `inventoryItemId` rows | **exception**; the platform does not auto-pick; operator resolves |

## B.7 Cancellation / refund reconciliation

**UNRESOLVED — Shopify cancellation/refund path in GT's specific order flow** (per `CLAUDE.md` §14 knowledge gap).

Pending that resolution, the Shopify FG-sync boundary **only pushes authoritative levels**. It does not attempt to consume cancellation or refund signals from Shopify. If refunds affect FG stock operationally, that adjustment enters the platform via the Waste / Adjustment form (Gate 3 surface), not via Shopify.

## B.8 Direction-of-truth summary

| Information | Authoritative | Mirrored | Derived | Not tracked here |
|---|---|---|---|---|
| FG quantity at GT's location | **platform (projection over ledger)** | Shopify (write target) | — | — |
| SKU catalog | **platform `items`** | — | — | Shopify's product catalog (platform does not read it) |
| Customer orders | **LionWheel** (commerce-channel origin: Shopify, mirrored into LionWheel) | — | — | Shopify order objects (platform does not read them) |
| Pricing / product metadata | out of this boundary | — | — | — |
| `inventoryItemId` ↔ SKU mapping | **platform-side mapping table** (Window 1) | — | — | — |
| `locationId` for GT's FG | **platform-side config / mapping** | — | — | — |

## B.9 Window 1 mirror-side shape (proposals; Window 1 finalizes)

No DDL authored. Proposed entities:

### `shopify_sku_map` (proposal — Window 1 owns)
| Proposed column | Proposed type | Purpose |
|---|---|---|
| `items_sku` | `text` PK | platform `items.sku` |
| `shopify_inventory_item_id` | `text` | Shopify GID, e.g. `"gid://shopify/InventoryItem/12345"` |
| `shopify_variant_id` | `text` nullable | for audit |
| `sync_enabled` | `boolean` | operator kill-switch per SKU |
| `last_resolved_at` | `timestamptz` | when the mapping was last confirmed |
| `notes` | `text` nullable | |

### `shopify_sku_sync_state` (proposal — Window 1 owns)
| Proposed column | Proposed type | Purpose |
|---|---|---|
| `items_sku` | `text` | FK to items |
| `shopify_location_id` | `text` | the authoritative location |
| `last_pushed_available` | `integer` | `compareQuantity` for the next push |
| `last_pushed_on_hand` | `integer` nullable | if GT also syncs on_hand |
| `last_pushed_at` | `timestamptz` | |
| `last_pushed_run_id` | `uuid` | FK to `integration_run` |
| `last_reconciliation_at` | `timestamptz` | |
| `last_reconciliation_delta` | `integer` | 0 on clean reconciliation |
| (PK: composite `(items_sku, shopify_location_id)`) | | |

### `integration_run` extension
**No new table.** The existing `integration_run` contract (runtime handoff §B.5) extends by allowing:
- `integration` enum gains `"shopify"` and `"green_invoice"` alongside `"lionwheel"`
- `run_kind` enum gains `"shopify_sku_push"`, `"shopify_sku_reconciliation"`, `"green_invoice_expense_refresh"`, `"green_invoice_expense_sweep"`, `"green_invoice_supplier_refresh"`
- `error_class` vocabulary adds `"shopify_compare_mismatch"`, `"shopify_location_inactive"`, `"green_invoice_unmapped_supplier"`, `"green_invoice_unmapped_line_item"`, `"green_invoice_active_price_threshold_breach"`

Window 1 applies these as CHECK-constraint extensions when authoring the `integration_run` migration.

---

# Phase C — Green Invoice ingest boundary contract

## C.1 Direction and role

- **Direction:** **inbound** Green Invoice → platform.
- **Purpose:** feed two platform concerns:
  1. **supplier invoice evidence** — full document metadata + line items as observed at ingest time, immutable in the mirror
  2. **price history** — per-SKU supplier price observations, each tagged with the evidence document they came from
- **Explicit non-goals:** issuing outbound invoices from the platform, writing back to Green Invoice, reading customer-side income documents (those exist in Green Invoice but are not what GT consumes through this boundary), ingesting shipment-side invoices linked from LionWheel `driver_note` (that is a separate cross-link topic, not this pack).

## C.2 API surface

**Base URL:** `https://api.greeninvoice.co.il/api/v1` (declared in the public `bariew/greeninvoice` PHP client README).

**Authentication:** API ID + API secret obtained from the Green Invoice business account; exchanged for a short-lived JWT via a login endpoint. The exact endpoint path and TTL **UNRESOLVED** in this pass (Apiary rendering blocked); the pattern — ID+secret → JWT bearer — is the documented pattern across mirrored client libraries. The runtime auth wiring belongs in the secret-store-wiring doc when the token workflow is unblocked; this pack does not touch token workflow per scope.

**Expense and document endpoints:** Green Invoice distinguishes **income** documents (outbound) from **expense** documents (inbound — supplier-originated). GT's use case is **expense only**. Common endpoint shapes per the Apiary reference structure: list/search expenses, fetch expense by id, fetch supplier by id, download document file. **Exact endpoint paths UNRESOLVED** in this pass.

## C.3 Document-level fields (verbatim where sourced)

**Outbound-document fields observed in the public Valigara mapping (reference for shape, not all applicable to expenses):**

| Field | Source | Notes |
|---|---|---|
| `type` | Valigara mapping | document type; Hebrew strings observed in mapping doc (`קבלה`, `חשבונית מס`, `חשבונית מס / קבלה`, `חשבונית זיכוי`) |
| `vatType` | Valigara mapping | values observed: `"Default (Based on business type)"`, `"Included - Mixed (...)"`, `"Exempt - Exempt (VAT free)"` |
| `description` | Valigara mapping | free text |
| `lang` | Valigara mapping | document display language |
| `currency` | Valigara mapping | ISO currency code |

**Numeric document type codes:** one data point observed in a Green Invoice skill description — `320 = "Tax Invoice-Receipt"`. The **full 13-code enum is UNRESOLVED**; the apparent range is in the low-hundreds. Mirror stores type as `integer` AND `text` label to survive enum evolution.

**Expense-side field names (the critical gap):**

**UNRESOLVED — expense document schema.** The Apiary reference and the Valigara mapping document **outbound** income-document shapes; they do **not** document the expense (supplier-invoice) shape GT actually needs to ingest. The mirror table shape is proposed at the logical level below; column names that would require knowing specific Green Invoice field names are explicitly marked UNRESOLVED.

## C.4 Supplier-side fields

**Outbound-document analogue from Valigara mapping** (GT will be reading supplier-documents, so the supplier fields should mirror the client-side field set reversed):

| Observed on `client.*` (outbound) | Analogous expected on `supplier.*` (inbound) |
|---|---|
| `client.name` | `supplier.name` (plausible; **UNRESOLVED verbatim**) |
| `client.emails` | `supplier.emails` (UNRESOLVED) |
| `client.phone` | `supplier.phone` (UNRESOLVED) |
| `client.address` | `supplier.address` (UNRESOLVED) |
| `client.country` | `supplier.country` (UNRESOLVED) |

**Israel-specific supplier identifiers:** `taxId` / `businessNumber` — observed as common Green Invoice fields in PHP client libraries but not verbatim-verifiable in this pass. **UNRESOLVED** for exact field names.

## C.5 Line-item fields

**Outbound income lines (verbatim from Valigara mapping):**

| Field | Source | Purpose in GT context |
|---|---|---|
| `income.catalogNum` | Valigara | **SKU-shaped** — the likeliest join key to platform `items.sku` or `components.component_code` |
| `income.currency` | Valigara | currency on the line |
| `income.description` | Valigara | free text |
| `income.price` | Valigara | per-line price |
| `income.quantity` | Valigara | quantity |
| `income.vatType` | Valigara | `"Default"` / `"Included"` / `"Exempt"` |

**Expense lines:** by symmetry the likely field path is `expense.lines[*].catalogNum` / `.price` / `.quantity` / `.vatType` — but this is **UNRESOLVED verbatim**.

## C.6 VAT / net-of-VAT semantics

Per `CLAUDE.md` §3.5: **net-of-VAT cost semantics**. The mirror must separate:

- `gross_price` (what appears on the invoice, may include VAT depending on `vatType`)
- `vat_amount` (derived from `vatType` and Israeli VAT rate at `documentDate`)
- `net_price` (authoritative for `price_history` and any active-price consideration)

**Unresolved:** Israeli VAT rate schedule over time. **Not in this pack.** Platform must carry a versioned VAT-rate table (Window 1 authoring). Proposal: `vat_rate_history(effective_from, effective_to, rate)`; current rate as of 2026 is 18% but the history table must support backdated documents.

## C.7 Mirror-side shape (proposals; Window 1 owns)

### `gi_expense_mirror` (proposal)
| Proposed column | Proposed type | Source | Notes |
|---|---|---|---|
| `id` | `text` PK | Green Invoice expense id | **UNRESOLVED** exact GI field name; proposed placeholder `id` |
| `type_code` | `integer` | GI document `type` numeric code | `320` observed; full enum UNRESOLVED |
| `type_label` | `text` | GI document `type` display (Hebrew) | observed labels from Valigara |
| `number` | `text` | GI document number | UNRESOLVED exact field |
| `status` | `text` | GI document status | UNRESOLVED enum |
| `document_date` | `date` | GI `documentDate` | UNRESOLVED verbatim |
| `due_date` | `date` nullable | | UNRESOLVED |
| `currency` | `text` | GI `currency` | verbatim |
| `vat_type` | `text` | GI `vatType` | verbatim |
| `supplier_id_upstream` | `text` | GI supplier id | UNRESOLVED |
| `amount` | `text` | gross total | string-decimal preservation — same rule as LionWheel `order_total` |
| `amount_net` | `text` | computed from `amount` + `vat_type` + VAT rate at `document_date` | derived, not mirrored |
| `vat_amount` | `text` | derived | |
| `raw_payload` | `jsonb` | full GI expense body | schema-drift resilience |
| `mirror_ingested_at` | `timestamptz` | runtime | |
| `mirror_source_run_id` | `uuid` | FK to `integration_run` | |
| `mirror_source_watermark` | `timestamptz` | upstream `updated_at` equivalent | **UNRESOLVED** whether GI exposes `updated_at` on expenses |

### `gi_expense_line_mirror` (proposal)
| Proposed column | Proposed type | Source |
|---|---|---|
| `id` | `text` PK | GI line id (UNRESOLVED whether GI exposes a stable line id) |
| `expense_id` | `text` | FK to `gi_expense_mirror.id` |
| `line_no` | `integer` | ordinal within document |
| `catalog_num` | `text` | GI `catalogNum` — join key to platform `items.sku` / `components.component_code` |
| `description` | `text` | |
| `quantity` | `text` | string-decimal |
| `price_gross` | `text` | string-decimal |
| `price_net` | `text` | derived net-of-VAT |
| `currency` | `text` | |
| `vat_type` | `text` | |
| `raw_payload` | `jsonb` | |
| `mirror_ingested_at` | `timestamptz` | |
| `mirror_source_run_id` | `uuid` | FK |

### `gi_supplier_mirror` (proposal)
| Proposed column | Proposed type | Notes |
|---|---|---|
| `id` | `text` PK | upstream GI supplier id |
| `name` | `text` | |
| `tax_id` | `text` nullable | UNRESOLVED verbatim field name |
| `business_number` | `text` nullable | UNRESOLVED |
| `country` | `text` nullable | |
| `email` | `text` nullable | |
| `phone` | `text` nullable | |
| `address` | `text` nullable | |
| `raw_payload` | `jsonb` | |
| `mirror_ingested_at` | `timestamptz` | |
| `mirror_source_run_id` | `uuid` | FK |

### `price_history` (proposal)
Not a Green Invoice mirror; this is a **derived** platform table that gets a new row per line-item ingest where mapping is confident.

| Proposed column | Proposed type | Notes |
|---|---|---|
| `id` | `uuid` PK | |
| `items_sku` | `text` FK | or `components.component_code` — join ambiguity per §C.9 |
| `supplier_id` | `text` FK to platform `suppliers`, **NOT** `gi_supplier_mirror` | platform-side supplier is authoritative; GI mirror is evidence only |
| `observed_at` | `date` | = `gi_expense_mirror.document_date` |
| `unit_price_net` | `text` | string-decimal, net-of-VAT |
| `currency` | `text` | |
| `evidence_expense_id` | `text` | FK to `gi_expense_mirror.id` |
| `evidence_line_id` | `text` | FK to `gi_expense_line_mirror.id` |
| `mapping_confidence` | `text` | `"exact_sku"` / `"exact_supplier_sku"` / `"fuzzy"` / `"operator_confirmed"` |

### `supplier_item_mapping` (proposal — extends existing Window 1 `supplier_items` concept)
Adds a **supplier-scoped SKU** column if not already present, so a Green Invoice `catalogNum` observed from Supplier X can be joined to platform `components` without requiring the global `items.sku` to match.

| Proposed column | Proposed type | Notes |
|---|---|---|
| `supplier_id` | FK to `suppliers` | |
| `supplier_sku` | `text` | observed from `gi_expense_line_mirror.catalog_num` |
| `items_sku` OR `component_code` | FK | the platform's canonical identifier |
| `confidence` | `text` | `"confirmed"` / `"proposed"` |
| `first_observed_at` | `date` | |
| `last_observed_at` | `date` | |

## C.8 Active-price update guardrails

Per `CLAUDE.md` §3.5 — active supplier prices auto-update **only** when mapping is **unambiguous** AND price change is **within threshold**.

**Unambiguous mapping** means:
1. `gi_expense_line_mirror.catalog_num` resolves to **exactly one** platform identifier via `supplier_item_mapping` for that supplier, AND
2. the resolution is marked `confidence='confirmed'`.

**Within threshold** means (proposal; operator locks the numbers):
- price delta vs current active price is ≤ `price_drift_threshold_pct` (proposed: 15%), AND
- the observation is the Nth consecutive observation from the same supplier at the same price level (proposed: N = 2 — one data point could be a clerical error; two in a row establishes signal), OR the operator has manually pre-approved the change.

**Outside guardrails:** emit `green_invoice_active_price_threshold_breach` exception; current active price stays; `price_history` still records the observation.

## C.9 Field join ambiguity (explicit)

The central ambiguity on the Green Invoice side is **which platform identifier `catalog_num` joins to**:

- For `BOUGHT_FINISHED` items: joins to `items.sku` (supplier sells a finished good directly)
- For `MANUFACTURED` / `REPACK` inputs: joins to `components.component_code` via `supplier_items` (supplier sells a component, not a finished good)

The mirror cannot disambiguate; the `supplier_item_mapping` / `supplier_items` table disambiguates. The ingest path:

1. persist to `gi_expense_line_mirror.catalog_num` verbatim
2. attempt join via `(supplier_id_platform, catalog_num)` → platform identifier in `supplier_item_mapping`
3. if unambiguous → record `price_history` row + (if within threshold) propose active-price update
4. if ambiguous or missing → emit `green_invoice_unmapped_line_item` exception; operator resolves

**Never auto-create** a `components` or `items` row from the mirror side.

## C.10 Conflict / drift rules (Green Invoice side)

| Situation | Resolution |
|---|---|
| `catalog_num` not in `supplier_item_mapping` | exception, no price-history write, no active-price change |
| Multiple platform identifiers for one `(supplier_id, catalog_num)` | exception, operator disambiguates |
| `price_history` observation outside threshold | record observation, **no** active-price update, emit threshold exception |
| VAT rate for `document_date` not in `vat_rate_history` | halt ingest for that expense, emit `vat_rate_unknown` exception, **do not guess** |
| Supplier in mirror without a matching platform `suppliers` row | record `gi_supplier_mirror` row, emit `green_invoice_unmapped_supplier` exception, do **not** auto-create a platform supplier |
| Upstream expense document is edited (observed via a later `updated_at`) | upsert under the same `id`; raw_payload updates; `price_history` does **not** mutate past rows — new observation row appended if the line changed |

---

# Phase D — Authoritative vs mirrored vs derived field map (cross-integration)

Single table covering the two boundaries in this pack plus the already-published LionWheel boundary, so consumers reading any of the three packs have the same map.

| Information | Authoritative | Mirrored (read-only on platform) | Derived on platform | Not tracked |
|---|---|---|---|---|
| FG stock quantity per SKU | platform projection (over `stock_ledger` + `balance_anchors`) | Shopify (as sync target, not source) | — | — |
| FG SKU catalog | platform `items` | — | — | Shopify product catalog |
| Customer orders | LionWheel (commerce-origin Shopify flows through LionWheel) | `lw_task` mirror | `open_orders_view` | Shopify order objects |
| Delivery / visit state | LionWheel | `lw_visit` mirror | `shipment_status_view` | — |
| Supplier catalog | platform `suppliers` | `gi_supplier_mirror` (evidence only) | — | — |
| Supplier-SKU mapping | platform `supplier_items` / `supplier_item_mapping` | — | — | — |
| Supplier invoice evidence | Green Invoice | `gi_expense_mirror` + `gi_expense_line_mirror` | — | — |
| Supplier price observation | — | evidence rows in GI mirror | `price_history` (per observation) | — |
| Active supplier price | platform `supplier_items.current_price` (or equivalent) | — | updated from `price_history` under §C.8 guardrails only | — |
| VAT rate at a given date | platform `vat_rate_history` | — | — | — |
| Component / BOM master | platform `components` + `bom_head`/`bom_version`/`bom_lines` | — | — | — |
| Physical stock events | platform `stock_ledger` (forms + integrations) | — | — | — |
| `wp_order_id` ↔ Shopify order | LionWheel `task.wp_order_key` (commerce context only) | `lw_task.wp_order_key` | — | — |

---

# Phase E — Conflict / drift rules (consolidated)

Restated with consistent emit vocabulary so the Exceptions Inbox has one taxonomy:

| Exception code (proposed) | Source | Trigger |
|---|---|---|
| `shopify_sku_unmapped` | Shopify | SKU present on Shopify with no `shopify_sku_map` row |
| `shopify_inventory_drift` | Shopify | reconciliation read shows Shopify qty ≠ platform projection beyond tolerance |
| `shopify_compare_mismatch` | Shopify | two consecutive push attempts fail compare-and-set |
| `shopify_location_inactive` | Shopify | authoritative location's `isActive=false` |
| `green_invoice_unmapped_supplier` | GI | supplier on expense has no platform `suppliers` row |
| `green_invoice_unmapped_line_item` | GI | line `catalog_num` has no unambiguous platform identifier |
| `green_invoice_active_price_threshold_breach` | GI | observation outside `price_drift_threshold_pct` |
| `green_invoice_vat_rate_unknown` | GI | `document_date` falls outside `vat_rate_history` coverage |
| `green_invoice_line_mapping_ambiguous` | GI | `(supplier, catalog_num)` resolves to multiple platform identifiers |

Every exception routes to the Exceptions Inbox (Gate 3 concept). None auto-heals. None writes to masters silently.

---

# Phase F — Blocker register by owner

## F.1 Tom (operator)

| # | Blocker | Resolving evidence |
|---|---|---|
| T.SG.1 | Which Shopify Location GID represents GT's authoritative FG location? (assumed single) | operator confirms the GID; if multiple, which is primary |
| T.SG.2 | Does GT want `on_hand` synced or only `available`? | operator choice |
| T.SG.3 | Reconciliation cadence (proposed 30 min during business hours) | operator locks number |
| T.GI.1 | Does GT currently enter supplier invoices into Green Invoice as expenses, or is the flow different? | operator confirms the GI usage model |
| T.GI.2 | `price_drift_threshold_pct` (proposed 15%) | operator locks number |
| T.GI.3 | Number of consecutive observations required to promote to active price (proposed 2) | operator locks number |
| T.GI.4 | Which platform identifier table is used for supplier-SKU mapping — existing `supplier_items` table, or a new `supplier_item_mapping`? | operator confirms the naming; Window 1 implements |
| T.GI.5 | Is `vat_rate_history` already seeded for Israel's historical rates, or does Window 4 need to supply a seed? | operator / Window 1 check |

## F.2 Window 1 (DB / DDL)

| # | Blocker | Resolving evidence |
|---|---|---|
| W1.SG.1 | Extend `integration_run` CHECK constraints to include `"shopify"` as a valid `integration` and new `run_kind` / `error_class` values (§B.9) | CHECK-constraint migration |
| W1.SG.2 | Migration for `shopify_sku_map` and `shopify_sku_sync_state` | migration + pgTAP covering round-trip, compare-and-set state |
| W1.GI.1 | Extend `integration_run` CHECK for Green Invoice run_kinds / error_classes | CHECK-constraint migration |
| W1.GI.2 | Migrations for `gi_expense_mirror`, `gi_expense_line_mirror`, `gi_supplier_mirror`, `price_history`, `vat_rate_history`, and the `supplier_items` extension per §C.9 | migrations + pgTAP covering join paths |

## F.3 Window 4 (this lane)

| # | Blocker | Status | Resolving evidence |
|---|---|---|---|
| W4.SG.1 | Zod schemas for Shopify `InventorySetQuantitiesInput`, `InventoryQuantityInput`, `InventoryLevel` read shape | not started; **independently authorable now** in `window4-integrations-sandbox/src/shopify/` | |
| W4.SG.2 | Shopify push mapper: platform FG projection row → `InventoryQuantityInput` | depends on W4.SG.1; **parallel-safe** | |
| W4.SG.3 | Shopify fetcher interface (push + read for reconciliation) | depends on W4.SG.1; **parallel-safe** | |
| W4.GI.1 | Zod schemas for Green Invoice expense / line / supplier | **blocked on L.GI.1 through L.GI.3 inspection gaps below**; cannot author verbatim field names without them |
| W4.GI.2 | Green Invoice ingest mapper (expense → `gi_expense_mirror` + lines → `gi_expense_line_mirror` + supplier handling) | blocked on W4.GI.1 |
| W4.GI.3 | VAT net-of-VAT computation helper (given `vatType`, `document_date`, gross `amount`) | **independently authorable now**; pure function, no upstream schema dependency |
| W4.GI.4 | Active-price threshold evaluator (given prior active price + new observation + threshold config → decision + exception code) | **independently authorable now**; pure function |
| W4.GI.5 | Fetcher interface for GI (auth flow, expense endpoints, supplier endpoints) | blocked on L.GI.1 (auth details) + L.GI.2 (endpoint paths) |

## F.4 Later inspection blockers (external spec gaps)

| # | Blocker | Why it blocks |
|---|---|---|
| L.SG.1 | Full quantity-name enum beyond `available` / `on_hand` / `incoming` / `committed` | read-reconciliation may need to filter by additional names |
| L.SG.2 | `inventorySetQuantities.reason` accepted enum beyond `"correction"` | required field; platform must supply a valid value per push |
| L.SG.3 | Rate-limit cost of `inventorySetQuantities` and paginated `InventoryLevel` read | cadence and retry-backoff design |
| L.SG.4 | Shopify cancellation / refund behaviour in GT's order flow | `CLAUDE.md` §14 UNRESOLVED |
| L.GI.1 | Green Invoice JWT login endpoint path, field names, TTL | runtime auth wiring |
| L.GI.2 | Green Invoice expense list/search/detail endpoint paths, query-filter field names, pagination | fetcher implementation |
| L.GI.3 | Green Invoice expense object field names (the expense counterpart to the Valigara-documented income shape) | Zod schema authoring, mirror shape finalization |
| L.GI.4 | Green Invoice full 13-code document type enum | mirror `type_code` CHECK constraint, reporting UX |
| L.GI.5 | Green Invoice supplier object verbatim field names (tax_id, business_number, etc.) | `gi_supplier_mirror` column finalization |
| L.GI.6 | Whether Green Invoice exposes a stable `updated_at`-equivalent on expenses, and whether expense documents are mutable after issue | watermark-driven refresh strategy |
| L.GI.7 | Israeli VAT rate history needed by `vat_rate_history` table | seed data |
| L.GI.8 | Whether the sandbox / staging environment documented for LionWheel has an equivalent for Green Invoice | test-environment setup |

---

# Phase G — Smallest future runtime slice per integration

## G.1 Shopify — first slice

**Slice S1: single-SKU absolute push via `inventorySetQuantities` with compare-and-set, driven by CLI (one SKU per invocation).**

Why first: exercises the full write path (auth, compose mutation with idempotency key, compare-and-set, post-success update of `shopify_sku_sync_state.last_pushed_available` and `last_pushed_run_id`). No scheduler. No webhook. No bulk operation.

Prerequisites before S1 can run:
- W1.SG.1 + W1.SG.2 complete
- W4.SG.1–W4.SG.3 complete (parallel-safe; start now)
- token workflow for Shopify Admin API (deferred per scope)
- operator confirmation of T.SG.1 (authoritative location) and T.SG.2 (available vs on_hand)

Success evidence:
- one `integration_run` row with `integration='shopify'`, `run_kind='shopify_sku_push'`, `status='succeeded'`
- `shopify_sku_sync_state.last_pushed_available` matches the value the platform sent
- second invocation with unchanged projection is a no-op (compare-quantity equal → mutation accepts but diffs zero)
- invocation with intervening Shopify change produces `shopify_compare_mismatch`, retries once, succeeds or escalates cleanly

## G.2 Green Invoice — first slice

**Slice GI1: single-expense fetch by id (operator supplies the GI expense id), parse, mirror into `gi_expense_mirror` + child lines + supplier, evaluate each line against `supplier_item_mapping`, emit exceptions for unmapped lines, DO NOT write to `price_history` or update active prices on first slice.**

Why first: exercises auth, parse, embedded-child upsert, supplier handling, and the mapping-join exception path — without yet enabling the price-history derivative flow. Keeps the blast radius minimal while surfacing the most common failure mode (unmapped `catalog_num`).

Prerequisites before GI1 can run:
- L.GI.1 (auth), L.GI.2 (endpoint paths), L.GI.3 (expense field names) resolved — **these are hard prerequisites** because Zod schemas cannot be authored verbatim without them
- W1.GI.1 + W1.GI.2 complete
- W4.GI.1 + W4.GI.2 complete
- T.GI.1, T.GI.4 confirmed

Follow-on slices (not in this pack):
- GI2: expense sweep over a date range (`/expenses?from=...&to=...` — endpoint UNRESOLVED)
- GI3: `price_history` write enabled
- GI4: threshold-evaluator gated active-price update
- GI5: supplier refresh + reconciliation against platform `suppliers`

---

# Phase H — Final required outputs checklist

- [x] Boundary contract for Shopify FG sync (Phase B)
- [x] Boundary contract for Green Invoice ingest (Phase C)
- [x] Authoritative vs mirrored vs derived field map (Phase D)
- [x] Conflict / drift rules (Phase E)
- [x] Blocker register by owner (Phase F)
- [x] Smallest future runtime slice per integration (Phase G)

# Phase I — Self-check

- [x] No live Shopify or Green Invoice HTTP calls performed this pass
- [x] No DDL authored — every mirror entity is a **proposed** shape, Window 1 owns finalisation
- [x] No runtime / scheduler / webhook / portal code authored
- [x] No token workflow changes (per scope)
- [x] No planning logic authored
- [x] No invented external field names — every verbatim field traces to a cited public doc; every unresolved field is explicitly flagged UNRESOLVED
- [x] Source-of-truth rules preserved: Shopify = FG sync target (platform wins); Green Invoice = evidence + history (never auto-create components, net-of-VAT, threshold gate for active prices)
- [x] Cross-integration field-ownership map consistent with LionWheel pack
- [x] `integration_run` reused, not duplicated
- [x] Exceptions vocabulary uniform; every exception routes to Exceptions Inbox, none auto-heals
- [x] Gate 3 not regressed — this pack produces zero runtime state

---

# Final verdict

**STATUS: BLOCKED_ON_EXTERNAL_SPEC_GAPS**

Honest verdict because the two boundaries differ materially in readiness:

- **Shopify FG-sync section is contract-ready.** Field names are authoritative and verbatim from Shopify's public GraphQL docs. The remaining Shopify items (§F.1 T.SG.*, §F.4 L.SG.*) are operator-set numbers and optional enum breadth — they do not block Slice S1 authoring; Slice S1 can start as soon as W1.SG.* and W4.SG.* are done.
- **Green Invoice ingest section has real spec gaps.** The expense-side schema was not crawlable in this pass (Apiary reference did not render; client-library sources did not expose expense fields). Three blockers — L.GI.1 (auth endpoint), L.GI.2 (endpoint paths), L.GI.3 (expense field names) — must be resolved via live-doc-inspection-with-token before Zod schemas can be authored without invented field names. Until then, the Green Invoice fetcher interface and mirror Zod shapes cannot be finalised without violating the "no invented external field names" rule.

The pack-as-a-whole is therefore `BLOCKED_ON_EXTERNAL_SPEC_GAPS` — with the blockers named precisely at L.GI.1–L.GI.3 and every other deliverable complete.

**Unblock path:** a future Window 4 pass with Green Invoice credentials and read-only inspection authorization (same shape as the LionWheel inspection pass) fetches expense / supplier / line shapes directly, at which point the Green Invoice sections upgrade from logical-placeholder to verbatim contract. Shopify side does not need such a pass — its public docs are sufficient; it only waits for Window 1.
