# Green Invoice Supplier-Price Evidence — Contract-Requirements Spec

**Owner:** W4 (Integrations / Jobs / Exports / Dashboard Contracts)
**Kind:** requirements-only. No schema DDL, no migration SQL, no runtime code, no handler implementations.
**Authored:** 2026-04-23 by executor-w4 (W4 rolling backlog item 2).
**Evidence consumed:**
- `CURRENT_STATE.md` (calibrated 2026-04-23) — runtime state, UNRESOLVED items, GreenInvoice signal evidence
- `runtime_ready.json` — `RUNTIME_READY(GreenInvoice)` emitted 2026-04-21T18:45
- `docs/production_endgame_phase_e4_runtime_checkpoint.md` (executor-w1, 2026-04-21) — live smoke evidence, A13 decisions, residuals (via runtime_ready.json note)
- `docs/integrations/green_invoice_supplier_price_contract.md` (executor-w4, 2026-04-21, commit `ac7c579`) — full field-level requirements spec with live API inspection evidence; this spec builds the requirements-layer view on top of that contract's evidence
- `db/migrations/0063_green_invoice_ingest_state.sql` — confirmed `gi_ingest_state` and `gi_expense_mirror` schemas
- `db/migrations/0071_suppliers_green_invoice_supplier_id.sql` — confirmed `suppliers.green_invoice_supplier_id` column exists (applied 2026-04-22)
- `db/migrations/0025_change_log_and_price_history.sql` — confirmed `price_history` table schema
- `db/migrations/0075_supplier_items_std_cost.sql` — confirmed `supplier_items.std_cost_per_inv_uom` column (added 2026-04-23 as Path B fix; this migration landed DURING the W4 write window; FR2 race detected — see FR2 note at end of Evidence section)
- `supabase/functions/factory_os_jobs/index.ts` — confirmed deployed handler fields: `giResolveSupplier`, `runGreenInvoicePoll`, actual fields read from GI API (`exp.amountExcludeVat`, `exp.documentType`, `exp.currency`, `exp.supplier.id`, `exp.supplier.name`, `exp.date`, `exp.lastUpdateDate`)

**FR2 race note (2026-04-23):** Migration `0075_supplier_items_std_cost.sql` appeared in the migrations directory between FR1 (pre-write scan) and FR2 (post-write scan). This migration adds `supplier_items.std_cost_per_inv_uom` as the Path B fix (column was previously on `components` only, not on `supplier_items`). The spec's requirements about this column are substantively correct — the column now exists after `0075` lands. The citation in the original draft (referencing `0002_masters.sql`) has been corrected to reference `0075`. W4 is flagging this as a `contract_failure` per EXECUTION_POLICY.md §FR1→write→FR2 protocol: Tom must review the spec and confirm that the corrected citation does not alter any requirement. No silent renumber substitution was performed.

**Locked upstream decisions honored (CLAUDE.md):**
- Green Invoice is authoritative for supplier invoice evidence; not authoritative for active prices without validation rules.
- Feed `price_history`; do not auto-create components from invoice lines; do not auto-update active prices unless mapping is unambiguous and threshold passes.
- Net-of-VAT cost semantics.
- Active supplier price auto-updates only when mapping is unambiguous and the price change is within threshold.

**Tom-locked decisions honored (from task brief, 2026-04-23):**
- Threshold rule: price change < 3% = auto-accept; >= 3% = review queue.
- Normal safeguards around mapping quality and anomaly detection.
- Net-of-VAT cost semantics.
- No auto-creation of components from GI invoice lines.
- No auto-update of active prices unless mapping unambiguous + threshold passes.

---

## Status at time of authoring

`RUNTIME_READY(GreenInvoice)` was emitted 2026-04-21T18:45. The Green Invoice ingest infrastructure is deployed and running on an hourly `pg_cron` cadence. **Evidence-only mode is live**: the ingest polls, mirrors raw expense rows into `gi_expense_mirror`, and emits `gi_unmapped_supplier` exceptions, but makes **zero `price_history` writes**. The reason: supplier mapping is incomplete (101 of approximately 101 distinct GI suppliers are unmapped) and the price-signal-to-`std_cost_per_inv_uom` path is not yet active. This spec defines the full requirements the ingest must satisfy before it can be declared operationally live at the price-evidence layer.

**Current live state (from runtime_ready.json note):**
- `gi_expense_mirror`: 378 rows (`documentType` 305=228, 320=150; currency ILS=378)
- `gi_ingest_state`: watermark advanced from `2024-01-01` to `2026-04-21T10:06:17Z`
- Open exceptions: 101 `gi_unmapped_supplier` (distinct GI suppliers), 4 `gi_non_ils_currency`
- `price_history` writes from GI: 0 (evidence-only mode)

---

## 1. Purpose and scope

### 1.1 What this spec governs

This spec governs the path from the Green Invoice (GI) raw expense mirror into supplier price signals and from those signals into cost updates on the platform. Specifically:

- `gi_expense_mirror` → supplier mapping resolution → `price_history` write (evidence feed)
- `price_history` → threshold evaluation → `supplier_items.std_cost_per_inv_uom` update (active cost)
- Admin visibility of unmapped suppliers, pending price review items, and price history audit trail
- Exception surface for mapping failures, threshold violations, anomaly alerts, and review-queue items
- Exit criteria for the GI price-evidence feature being considered operationally live

### 1.2 What is out of scope

- GI authentication mechanics: these are already live (two-step JWT exchange per `green_invoice_supplier_price_contract.md` §2.2; token handling deployed in Edge Function).
- Raw ingest from GI API: already live (hourly `pg_cron` poll, `gi_expense_mirror` and `gi_ingest_state` tables deployed per migration 0063, 378 rows present as of 2026-04-21).
- Component creation from GI invoice lines: hard-forbidden per CLAUDE.md. Not in scope at any future date without an explicit Tom-locked decision.
- Per-line price extraction: GI exposes no structured line items at the expense-envelope level (confirmed by live inspection 2026-04-21, `green_invoice_supplier_price_contract.md` §4). This remains an architectural constraint; per-line price feed is impossible without out-of-band quantity data.
- GI write-back: the platform never writes to GI. Pull-only.
- Multi-currency handling beyond the ILS-only v1 default (see UNRESOLVED DR-3).

---

## 2. Source data model

### 2.1 `gi_expense_mirror` table (migration 0063, applied live)

The raw-evidence table keyed on GI's own expense `id`. Schema confirmed from `0063_green_invoice_ingest_state.sql`:

| Column | Type | Semantics |
|---|---|---|
| `gi_expense_id` | `text` PK | GI expense UUID (verbatim from GI). Idempotency key. |
| `captured_at` | `timestamptz` | Platform-side ingest timestamp. |
| `amount_excl_vat` | `money_4dp` (nullable) | Net-of-VAT invoice total. Source: `exp.amountExcludeVat`. This is the CLAUDE.md-required net value. |
| `amount_incl_vat` | `money_4dp` (nullable) | Gross invoice total. Source: `exp.amount`. |
| `vat_amount` | `money_4dp` (nullable) | VAT component. Source: `exp.vat`. |
| `currency` | `text NOT NULL` default `'ILS'` | ISO 4217. All 378 live rows = `'ILS'`. |
| `gi_supplier_id` | `text` (nullable) | GI supplier UUID (from `exp.supplier.id`). No FK — mapping is at handler layer. |
| `gi_supplier_name` | `text` (nullable) | GI supplier display name (often Hebrew). Logged for admin review. |
| `gi_document_type` | `integer` (nullable) | GI document type code. Live values: 305 (228 rows), 320 (150 rows). Filter set locked U-DT1. |
| `gi_status` | `integer` (nullable) | GI status code. Live value: 10 on all sampled rows. |
| `gi_document_date` | `date` (nullable) | Invoice date from `exp.date` (YYYY-MM-DD). Maps to `price_history.event_at`. |
| `gi_last_update_at` | `timestamptz` (nullable) | GI `lastUpdateDate` converted from unix epoch. Used as watermark. |
| `raw_jsonb` | `jsonb` (nullable) | Full GI response for audit. `data.fileKey` is read from here at audit time. |
| `ingested_by_job_run_id` | `uuid` FK to `job_runs` (nullable) | Run that inserted this row. |

**Load-bearing constraint: no price-signal columns are missing.** The `amount_excl_vat` field is the only signal available per-invoice. GI carries no structured line-item array; per-item quantity is not present in the mirror row (see §4.2 for implication).

### 2.2 `gi_ingest_state` table (migration 0063, applied live)

Singleton watermark table, one row (`job_name='green_invoice_poll'`):

| Column | Type | Semantics |
|---|---|---|
| `job_name` | `text` PK | `'green_invoice_poll'` — the only row in v1. |
| `last_ingested_at` | `timestamptz` (nullable) | Client-side watermark: max `gi_last_update_at` seen across all prior cycles. Seeded `2024-01-01`. Advanced to `2026-04-21T10:06:17Z` after first backfill. |
| `last_run_at` | `timestamptz` | Timestamp of the most recent poll attempt. |
| `last_successful_run_at` | `timestamptz` | Timestamp of the most recent successful poll. |
| `total_rows_ingested_lifetime` | `bigint` | Monotonically increasing count of mirror rows inserted across all cycles. Currently 378. |

### 2.3 Price-signal fields in `gi_expense_mirror`

The price signal available per mirror row is:
- `amount_excl_vat`: the net-of-VAT invoice total for the entire expense document (CLAUDE.md mandated net-of-VAT value)
- `gi_supplier_id` + `gi_supplier_name`: supplier identity for mapping resolution
- `gi_document_date`: the invoice date — used as `price_history.event_at`
- `gi_document_type`: 305 or 320 (per U-DT1 filter applied at ingest)

**Critical constraint:** the expense envelope contains no per-item quantity or per-line breakdown. The `amount_excl_vat` is the total invoice amount, not a per-unit price. Deriving a unit price requires knowing the quantity purchased, which is not present in the GI API response (see §4 for the full implication).

### 2.4 `gi_unmapped_supplier` exception category

Currently 101 open exceptions with category `gi_unmapped_supplier`, dedupe key `gi_unmapped_supplier:<gi_supplier_id>` (one per distinct GI supplier UUID). These represent GI suppliers whose `id` has not been matched to a `private_core.suppliers.supplier_id` via the `suppliers.green_invoice_supplier_id` column.

The exception fires when the ingest handler calls `giResolveSupplier()` (confirmed from handler source at `supabase/functions/factory_os_jobs/index.ts` lines 1379-1392) and gets back `supplier_id: null`. The handler still inserts the mirror row for audit purposes — mapping failure does not block evidence capture.

---

## 3. Supplier mapping

### 3.1 Mapping column (migration 0071, applied 2026-04-22)

`private_core.suppliers.green_invoice_supplier_id` — confirmed from migration 0071:
- Type: `text NULL`
- Uniqueness: partial unique index (`WHERE green_invoice_supplier_id IS NOT NULL`) — one-to-one GI supplier to platform supplier constraint
- Semantics: stores GI's `supplier.id` UUID as text. When non-null, the handler resolves the mirror row to a `supplier_id` via exact match

The column was added after the initial smoke run. The handler probes for it via `information_schema.columns` before attempting a lookup (confirmed from handler source, lines 1148-1157). When the column was absent (pre-0071), every row emitted `gi_unmapped_supplier` with `column_present=false`. Now that the column is present, exceptions emit with `column_present=true` and detail `"suppliers.green_invoice_supplier_id = <uuid> not found"` for the 101 GI suppliers not yet seeded.

### 3.2 Mapping quality levels

Three quality levels govern whether a mirror row can produce a `price_history` row:

| Level | Condition | Outcome |
|---|---|---|
| **Unresolved** | `suppliers.green_invoice_supplier_id` has no match for this GI supplier UUID | Emit `gi_unmapped_supplier`; no `price_history` write; mirror row still stored |
| **Ambiguous** | Resolved `supplier_id` has more than one active `supplier_items` row | Emit `gi_ambiguous_line_mapping`; no `price_history` write |
| **Unambiguous** | Resolved `supplier_id` has exactly one active `supplier_items` row | Proceed to price extraction per §4 |

Only the **unambiguous** path produces a `price_history` row. This is the CLAUDE.md-locked constraint: "active supplier price auto-updates only when mapping is unambiguous."

### 3.3 Admin workflow to resolve 101 unmapped suppliers

**Requirement R-M1:** The admin must be able to see a list of 101 open `gi_unmapped_supplier` exceptions from the Exceptions Inbox, each showing the GI supplier UUID and display name (`gi_supplier_name` from the mirror row, logged for this purpose).

**Requirement R-M2:** For each unmapped GI supplier, the admin resolves the exception by updating the corresponding `private_core.suppliers` row's `green_invoice_supplier_id` column to the GI supplier's UUID. This is an admin-authoring action on the supplier master, performed via the admin supplier management interface.

**Requirement R-M3:** The admin mapping interface for GI suppliers MUST display at minimum:
- The GI supplier UUID and display name (from `gi_supplier_name` in the mirror rows)
- The number of `gi_expense_mirror` rows for that GI supplier (total invoice count)
- The total invoice value (`SUM(amount_excl_vat)`) for that GI supplier (helps identify high-value suppliers for prioritization)
- The candidate platform supplier matches from `private_core.suppliers` (for admin selection)

**Requirement R-M4:** Matching strategies available to the admin:
- **Exact UUID match:** admin knows both the GI supplier UUID and the platform `supplier_id` and enters a direct mapping.
- **Name heuristic:** the admin interface MAY offer name-similarity candidates (fuzzy match between `gi_supplier_name` and `suppliers.supplier_name`) as non-binding suggestions. The admin must confirm; suggestions are never auto-accepted.
- **Tax ID secondary key:** UNRESOLVED — see DR-1.

**Requirement R-M5:** Once a `suppliers.green_invoice_supplier_id` value is set, the next ingest cycle will auto-resolve existing mirror rows for that GI supplier and evaluate them for `price_history` write eligibility. No migration or rescan job is needed — the next hourly poll picks up the mapping.

**Requirement R-M6:** A resolved `gi_unmapped_supplier` exception MUST auto-close when the GI supplier is successfully mapped and the next ingest cycle processes at least one expense row from that supplier without error. The auto-close pattern mirrors the LionWheel freshness exception auto-resolution confirmed in Gate 4.

### 3.4 Mapping completeness goal

**Requirement R-M7:** The GI price-evidence feature is not operationally live until the `gi_unmapped_supplier` exception count reaches zero. The current state is 101 open. This is the primary worklist for GT Everyday operations before GI-sourced `price_history` rows accumulate.

---

## 4. Price signal extraction

### 4.1 Document types carrying price signal (GI types 305 and 320)

Per `RUNTIME_READY(GreenInvoice)` note and `green_invoice_supplier_price_contract.md` §6.3, the U-DT1 Tom-locked filter applies at ingest time: `documentType IN (305, 320)`. All 378 mirror rows passed this filter. Documents of type 305 (majority, 228 rows) and 320 (150 rows) represent price-bearing supplier invoices in GI's classification scheme.

- **Type 305:** the predominant observed type. Represents supplier invoices as received and entered into GI.
- **Type 320:** observed in the live backfill. Specific semantic distinction between 305 and 320 is UNRESOLVED at the contract layer (see DR-2).

### 4.2 GI exposes no line items — load-bearing constraint

**This constraint shapes the entire price extraction architecture.**

Live inspection 2026-04-21 (confirmed by two probe families — `expenses/search` and `expenses/{id}` detail) found no structured line-items array in the GI expense envelope. The only monetary signal is the invoice-aggregate total `amountExcludeVat`. Compare: GT's outgoing sales invoices in GI DO carry per-line `income[]` arrays, but incoming supplier expenses do not.

Implication: per-item price extraction is impossible from GI data alone. Each expense produces at most one `price_history` row, and that row's `unit_price_net` is the invoice-aggregate total, not a per-unit price.

### 4.3 Expense-level vs. line-level precision

**Available:** invoice-aggregate net total (`amount_excl_vat`), invoice date (`gi_document_date`), supplier identity.

**Not available from GI:** per-item SKU, per-item quantity, per-item unit price.

### 4.4 Unit cost derivation from invoice total

Because no per-item quantity exists in the GI data, `unit_price_net` for the `price_history` row must be derived under an explicit assumption. Two options:

**Option Q-A (v1 default — Tom-locked per anti-stall defaults 2026-04-21):**
```
unit_price_net = amount_excl_vat / 1
                 (quantity_assumed = 1; invoice treated as aggregate purchase evidence)
```
The resulting `price_history` row represents the whole-invoice net total, not a per-unit price. The row is price-evidence, not a per-unit cost signal.

**Option Q-B (post-v1):** correlate with the corresponding GR/PO to get actual received quantity, divide `amount_excl_vat` by that quantity to get a true unit price. This requires cross-stream correlation and is explicitly deferred.

**Requirement R-PE1:** In v1, `price_history.unit_price_net = amount_excl_vat` from the mirror row. The `notes` field on the `price_history` row MUST contain the string `"invoice-aggregate; quantity=1; needs manual derivation"` so the audit trail is clear that this is not a per-unit price.

**Requirement R-PE2:** The `price_history.source` field MUST be `'green_invoice'` for all GI-sourced rows.

**Requirement R-PE3:** The `price_history.event_at` field MUST be set to `gi_document_date::timestamptz` (the invoice date, not the ingest timestamp). Per CLAUDE.md ledger semantics: `event_at` is authoritative for time-series math; `posted_at` is ingest time.

**Requirement R-PE4:** The `price_history.source_document_id` MUST be set to the `gi_expense_id` (GI's expense UUID). This provides the audit back-reference to the raw mirror row.

---

## 5. Price update conditions (the 3% threshold rule)

### 5.1 Gate: when does a mirror row produce a `price_history` row

**Requirement R-AP1:** a `gi_expense_mirror` row produces a `price_history` row when ALL of the following pass:
1. GI supplier maps unambiguously to exactly one platform `supplier_id` via `suppliers.green_invoice_supplier_id` (§3.2 mapping level = "unambiguous").
2. That `supplier_id` has exactly one active `supplier_items` row — giving the target `supplier_item_id` for `price_history`.
3. `gi_document_type IN (305, 320)` (already filtered at ingest; all rows in the mirror pass this).
4. `currency = 'ILS'` (already filtered at ingest; all 378 live rows pass this).
5. `amount_excl_vat` is non-null and > 0 (anomaly check — see §5.4).

If any condition fails, no `price_history` row is written. The appropriate exception is emitted. The mirror row is retained for audit.

### 5.2 Auto-accept path (< 3% change)

**Requirement R-AA1:** when a `price_history` row passes gate R-AP1 AND the price change from the most recent prior `price_history` row for the same `supplier_item_id` is less than 3% in absolute relative terms:

```
price_change_pct = abs(unit_price_net_new - unit_price_net_prior) / unit_price_net_prior
if price_change_pct < 0.03:  auto-accept path
```

Auto-accept behavior:
1. Write the `price_history` row (append-only; no update of existing rows per migration 0025 append-only triggers).
2. Update `supplier_items.std_cost_per_inv_uom` to the new `unit_price_net`.
3. Emit a `change_log` row with `action='SUPPLIER_PRICE_UPDATE_AUTO'`, `entity_table='supplier_items'`, `entity_id=<supplier_item_id>`, `changed_fields=["std_cost_per_inv_uom"]`, `old_values={"std_cost_per_inv_uom": <prior>}`, `new_values={"std_cost_per_inv_uom": <new>}`, `actor_snapshot='<system:green_invoice_poll>'` (system-emitted row per `change_log_contract.md` §4.4).
4. No exception is emitted on auto-accept. The change is silent but fully auditable via `change_log` and `price_history`.

**Requirement R-AA2:** "most recent prior `price_history` row" is defined as the row with the highest `event_at` for the same `supplier_item_id` with `source` IN (`'green_invoice'`, `'manual'`, `'seed'`) — i.e., the most recent price assertion from any source, not just from GI. This prevents a GI-sourced row from auto-accepting against stale price history while a recent manual update was already present.

**Requirement R-AA3:** when no prior `price_history` row exists for the `supplier_item_id` (first-ever price assertion), the auto-accept path applies unconditionally — there is no prior price to compare against, so the 3% rule has no reference point. Write the `price_history` row and update `std_cost_per_inv_uom` without threshold comparison. Emit a `change_log` row with action `'PRICE_HISTORY_INSERT'` instead of `'SUPPLIER_PRICE_UPDATE_AUTO'` to distinguish a "first record" from an "update under threshold."

### 5.3 Review queue path (>= 3% change)

**Requirement R-RQ1:** when `price_change_pct >= 0.03`, the auto-accept path does NOT fire. Instead:
1. Write the `price_history` row (evidence is always written regardless of threshold outcome).
2. Do NOT update `supplier_items.std_cost_per_inv_uom`.
3. Emit a `gi_price_change_exceeds_threshold` exception with:
   - `category = 'gi_price_change_exceeds_threshold'`
   - `severity = 'warning'` (default; `'critical'` when `price_change_pct >= 0.20` per anomaly detection §5.4)
   - `dedupe_key = 'gi_price_change_exceeds_threshold:<supplier_item_id>:<gi_document_date>'`
   - `detail` containing: `{supplier_item_id, gi_expense_id, unit_price_net_new, unit_price_net_prior, price_change_pct, event_date}`

**Requirement R-RQ2:** the review queue exception surfaces in the Exceptions Inbox. An admin or planner can resolve it by one of two actions:
- **Approve:** mark the exception resolved; the system then writes the pending `price_history.unit_price_net` to `supplier_items.std_cost_per_inv_uom` and emits a `change_log` row with action `'SUPPLIER_PRICE_UPDATE_MANUAL'` (indicating human-approved GI update).
- **Reject:** mark the exception rejected; `std_cost_per_inv_uom` remains unchanged; the `price_history` row is retained as evidence.

**Requirement R-RQ3:** the review approval action MUST be idempotent — submitting the same approval twice returns the same result without double-updating.

**Requirement R-RQ4:** the `change_log` row on a manual approval MUST record the approving user's `actor_user_id` and `actor_snapshot` (not `'<system:...>'`) — the human took a deliberate action.

### 5.4 Mapping quality requirements before any price update fires

**Requirement R-MQ1:** no `std_cost_per_inv_uom` update (auto or manual) may fire unless:
- Exactly one `supplier_id` maps to the GI supplier UUID (one-to-one via unique index on `suppliers.green_invoice_supplier_id`)
- Exactly one `active` `supplier_items` row exists for that `supplier_id` (count = 1 at time of evaluation)

If either condition fails after the `price_history` row is written (race condition: a new `supplier_items` row was added between mirror write and threshold evaluation), emit `gi_ambiguous_line_mapping` and defer to the review queue rather than auto-accepting.

### 5.5 Anomaly detection

**Requirement R-AN1:** The following price signals are anomalous and MUST NOT write to `std_cost_per_inv_uom` or trigger the 3% threshold comparison. They produce a `price_history` row (evidence feed) plus an anomaly exception:

| Anomaly | Condition | Exception category | Severity |
|---|---|---|---|
| Zero price | `amount_excl_vat = 0` | `gi_zero_price` | `warning` |
| Negative price | `amount_excl_vat < 0` (credit note) | `gi_negative_price` | `warning` |
| Implausibly large price | `unit_price_net_new > 10 * unit_price_net_prior` AND `unit_price_net_prior > 0` | `gi_price_change_exceeds_threshold` | `critical` |
| No prior price AND unit_price_net > UNRESOLVED absolute ceiling | see DR-4 | `gi_price_anomaly_no_prior` | `warning` |

**Requirement R-AN2:** Anomaly exceptions are distinct from the normal threshold review queue but surface in the same Exceptions Inbox. An admin must explicitly resolve anomaly exceptions.

**Requirement R-AN3:** A zero-price mirror row MUST still be stored in `gi_expense_mirror` — the mirror is raw evidence and must not filter out anomalous rows. The anomaly detection fires at the `price_history` write gate, not at the mirror gate.

---

## 6. `price_history` table contract

### 6.1 Table exists (confirmed from migration 0025)

`private_core.price_history` is live in migration `0025_change_log_and_price_history.sql`. The table was authored as part of Gate 4 audit substrate. Schema confirmed:

| Column | Type | Semantics |
|---|---|---|
| `price_history_id` | `uuid` PK default `gen_random_uuid()` | System-generated. |
| `supplier_item_id` | `uuid NOT NULL` FK to `supplier_items(supplier_item_id)` | The subject supplier-item. |
| `unit_price_net` | `money_4dp NOT NULL CHECK >= 0` | Net-of-VAT unit price per CLAUDE.md. For GI-sourced v1 rows: invoice aggregate total (see §4.4). |
| `source` | `text NOT NULL` | `'green_invoice'` for GI ingest rows; `'manual'` for admin edits; `'seed'` for import-time rows. No CHECK constraint — new sources land without migration. |
| `event_at` | `timestamptz NOT NULL` | Invoice date (from `gi_document_date`) for GI rows; `now()` for manual edits. |
| `posted_at` | `timestamptz NOT NULL` default `now()` | Platform ingest timestamp. Audit-only. |
| `actor_user_id` | `uuid` FK to `app_users` (nullable) | NULL for system-emitted GI ingest rows. |
| `actor_snapshot` | `text NOT NULL` | `'<system:green_invoice_poll>'` for GI ingest; display name for manual edits. |
| `source_document_id` | `text` (nullable) | `gi_expense_id` for GI rows; PO or GR reference for other sources. |
| `notes` | `text` (nullable) | `'invoice-aggregate; quantity=1; needs manual derivation'` for v1 GI rows. |

**Append-only enforcement:** confirmed — migration 0025 installs `BEFORE UPDATE OR DELETE` triggers on `price_history` raising exception `'change_log is append-only'`. No UPDATE or DELETE is possible. Corrections are made by writing a new row.

### 6.2 What a row represents

Each `price_history` row represents one price assertion: at `event_at`, the net-of-VAT cost of one unit of `supplier_item_id` was observed to be `unit_price_net` according to `source`. For GI-sourced v1 rows, the "unit" is the entire invoice amount (quantity=1 assumption); this is explicitly noted in `notes`.

The time-series semantics: the current operative price is the `unit_price_net` from the row with the maximum `event_at` for a given `supplier_item_id`. This is the same `event_at`-authoritative pattern as the stock ledger (CLAUDE.md §Ledger semantics: "`event_at` is authoritative for balance math").

### 6.3 Relationship to `supplier_items.std_cost_per_inv_uom`

`price_history` is the append-only audit log. `supplier_items.std_cost_per_inv_uom` is the current operative value used by the planning engine.

**Requirement R-PH1:** `std_cost_per_inv_uom` MUST only be updated by the price-update path described in §5. It MUST NOT be updated directly from `gi_expense_mirror` without going through the `price_history` write gate.

**Requirement R-PH2:** `std_cost_per_inv_uom` and the most recent `price_history.unit_price_net` for the same `supplier_item_id` MUST be equal at steady state. If they diverge (e.g., a direct DB edit), this is a data integrity issue surfaced by the nightly rebuild-verifier (future enhancement, not v1 blocking).

**Requirement R-PH3:** The planning engine reads `supplier_items.std_cost_per_inv_uom` for cost computations (Phase 10 cost rollup, post-closure stretch). The `price_history` table is the audit surface; it does not drive planning directly.

### 6.4 Retention

`price_history` is append-only with no expiry. Rows accumulate indefinitely. At GT's scale (one expense per supplier per month, ~40 active suppliers), the lifetime row count is negligible. No archiving policy is required in v1.

---

## 7. Admin visibility requirements

### 7.1 What an admin needs to see about GI-sourced price signals

**Requirement R-AV1:** The portal's admin/integrations view MUST surface for the GI price ingest:

| Display element | Source | Notes |
|---|---|---|
| Last successful ingest timestamp | `gi_ingest_state.last_successful_run_at` | Flag stale if > 120 minutes (warn threshold) |
| Total rows mirrored (lifetime) | `gi_ingest_state.total_rows_ingested_lifetime` | Displayed as "378 expenses mirrored" |
| Open unmapped supplier count | `COUNT(DISTINCT gi_supplier_id) WHERE exceptions.category='gi_unmapped_supplier' AND status='open'` | Link to unmapped supplier worklist |
| Open price-review exceptions | `COUNT(*) WHERE exceptions.category='gi_price_change_exceeds_threshold' AND status='open'` | Link to review queue in Exceptions Inbox |
| Integration status badge | Derived from `last_successful_run_at` and open `gi_auth_failure` exceptions | `broken` / `stale` / `fresh` per standard freshness thresholds |
| Link to price history table | Filtered view of `price_history WHERE source='green_invoice'` | Enables admin to inspect GI-sourced price evidence |

**Requirement R-AV2:** The admin MUST be able to browse `price_history` for any `supplier_item_id` and see:
- Event date, net price, source, source document reference
- Whether the row drove a `std_cost_per_inv_uom` update (derivable from `change_log` query — look for `SUPPLIER_PRICE_UPDATE_AUTO` or `SUPPLIER_PRICE_UPDATE_MANUAL` rows with matching `entity_id`)
- Whether the row triggered a review-queue exception

**Requirement R-AV3:** The admin MUST be able to see the full `change_log` trail for `std_cost_per_inv_uom` updates — who approved each change (or `'<system:green_invoice_poll>'` for auto-accepted), when, and from what prior value.

### 7.2 Unmapped supplier worklist

**Requirement R-UW1:** The unmapped supplier worklist surfaces the 101 open `gi_unmapped_supplier` exceptions as an admin-manageable list showing:
- GI supplier UUID and display name
- Number of mirror rows (invoices) for that GI supplier
- Total invoice value (`SUM(amount_excl_vat)`) for prioritization
- A search/select to match this GI supplier to a platform `suppliers` row
- A confirm-mapping action that writes `suppliers.green_invoice_supplier_id = <gi_supplier_uuid>` and acknowledges/resolves the exception

**Requirement R-UW2:** The worklist MUST be prioritizable by total invoice value — admins should resolve high-value suppliers first so the price-evidence feed captures the most economically significant supplier costs first.

**Requirement R-UW3:** The mapping UI MUST surface name-heuristic suggestions (non-binding, admin-confirmed only) to reduce manual lookup effort.

### 7.3 Price-review queue in Exceptions Inbox

**Requirement R-PRQ1:** The Exceptions Inbox MUST filter and display `gi_price_change_exceeds_threshold` exceptions. Each item shows:
- Supplier and component name
- Prior price and new observed price
- Price change percent
- Invoice date of the triggering expense
- The GI expense ID (with link to audit trace)
- Action buttons: Approve (update `std_cost_per_inv_uom`) or Reject (keep current price)

**Requirement R-PRQ2:** The portal MUST NOT allow an operator-role user to approve price updates. Only `admin` and `planner` roles may approve. Operators may view.

**Requirement R-PRQ3:** An approved price update from the review queue emits `action='SUPPLIER_PRICE_UPDATE_MANUAL'` in `change_log`. The approver's identity is recorded (`actor_user_id` + `actor_snapshot`).

---

## 8. Exit criteria

The GI price-evidence feature is operationally live when ALL of the following are simultaneously true:

**EC-1 — Mapping complete:** zero open `gi_unmapped_supplier` exceptions in the Exceptions Inbox. (Current state: 101 open. This is the primary operational worklist.)

**EC-2 — First auto-accept fires:** at least one `price_history` row from source `'green_invoice'` exists with `notes` NOT containing `'invoice-aggregate'` (post-Option-Q-B implementation) OR with `notes` containing `'invoice-aggregate'` AND a corresponding `SUPPLIER_PRICE_UPDATE_AUTO` `change_log` row exists for a `supplier_items.std_cost_per_inv_uom` update. In v1 with Option Q-A, this means an auto-accept with `unit_price_net = amount_excl_vat` (invoice total) fired end-to-end.

**EC-3 — Review queue cycles end-to-end:** at least one `gi_price_change_exceeds_threshold` exception was raised, surfaced in the Exceptions Inbox, and resolved by a planner/admin either approving (writes `std_cost_per_inv_uom` + `SUPPLIER_PRICE_UPDATE_MANUAL` in `change_log`) or rejecting (exception closed, `std_cost_per_inv_uom` unchanged).

**EC-4 — Price history accumulates:** `price_history` table contains at least 10 rows from source `'green_invoice'` spanning at least 3 distinct `supplier_item_id` values and 2 distinct `event_at` dates.

**EC-5 — Admin visibility works:** an admin can view supplier price history without running SQL — using the portal's admin surface to navigate from a `gi_unmapped_supplier` exception through to its resolution, and from a `supplier_items` row to its `price_history` trail.

**EC-6 — No blocking exceptions:** zero open `gi_auth_failure` or `gi_rate_limit_stuck` exceptions at the time of verification.

Note: the 3% threshold and anomaly rules (§5) are implementation requirements; EC-2 and EC-3 verify they fire correctly. The threshold values themselves are Tom-locked and MUST NOT be modified without an explicit Tom decision.

---

## 9. UNRESOLVED items

Each item below cannot be silently filled. Cited reason and owner.

**DR-1 — Tax ID secondary mapping key.** `green_invoice_supplier_price_contract.md` §5.1.4 recommends adding `suppliers.tax_id text NULL` as a secondary resolution fallback (match GI `supplier.taxId` against platform `suppliers.tax_id`). This column does NOT currently exist in migration 0002 or any applied migration. Adding it requires a W1 migration. The admin mapping workflow (§3.3) can function without it (UUID match is the primary path), but name-heuristic matching would be improved with tax ID secondary. Reason cannot be filled: whether to add the column and when is a W1 schema decision, and whether GT's supplier records carry tax IDs is a data quality question not verified by W4. Owner: W1 schema decision; Tom confirm data availability.

**DR-2 — GI document type 305 vs. 320 semantic distinction.** Both types 305 and 320 are captured in the live mirror (305=228 rows, 320=150 rows). Their precise GI-side semantic distinction (invoice vs. receipt? purchase invoice vs. credit note?) was not resolved in the 2026-04-21 live inspection. The U-DT1 Tom-locked default treats both as price-bearing. If 320 turns out to represent credit notes or returns (which carry negative `amount_excl_vat`), the anomaly check at R-AN1 will handle it. However, if the two types warrant different `price_history.notes` values or different processing logic, that requires Tom ratification. Reason cannot be filled: GI API documentation on document type semantics was not available during inspection.

**DR-3 — Non-ILS currency path.** The live mirror contains 378 ILS rows and 4 `gi_non_ils_currency` exceptions (4 skipped non-ILS rows). The v1 ingest skips non-ILS rows. If GT has USD- or EUR-denominated supplier invoices, those will never produce `price_history` rows in v1. Multi-currency handling (FX conversion via `currencyRate`, native-currency storage) is deferred. Reason cannot be filled: whether any non-ILS suppliers are operationally significant is Tom's operational judgment.

**DR-4 — Absolute price ceiling for anomaly detection when no prior price exists.** Requirement R-AN1 references an "UNRESOLVED absolute ceiling" for `gi_price_anomaly_no_prior`. When a supplier_item has no prior `price_history` row and the first GI-sourced invoice is large (e.g., a one-time bulk purchase totaling 50,000 ILS for a single supplier_item), the system has no reference to detect whether 50,000 ILS is reasonable. An absolute ceiling prevents accidental auto-update of `std_cost_per_inv_uom` to an implausibly large value on a first-ever assertion. The ceiling value depends on GT's component cost ranges and is not known to W4. Reason cannot be filled: requires Tom's operational knowledge of component cost magnitudes. Owner: Tom ratify per-component range or a single universal ceiling.

**DR-5 — Review approval endpoint path.** Requirement R-RQ2 specifies an Exceptions Inbox action (Approve / Reject) for `gi_price_change_exceeds_threshold` review items. The specific API endpoint that handles this approval action (analogous to `POST /api/v1/mutations/exceptions/:id/resolve` with a price-update side effect) does not exist in the currently deployed API. This is a new handler requirement, not covered by the existing `exceptions` handler stack. Reason cannot be filled: the endpoint path, request schema, and approval form_type are W1-owned implementation decisions. The requirement is stated; the implementation is open.

**DR-6 — `feature_flags.green_invoice_ingest_paused` flag existence.** The `green_invoice_supplier_price_contract.md` §11 references a GI-specific pause flag `feature_flags.green_invoice_ingest_paused`. Whether this flag exists in the live `feature_flags` table has not been verified by W4 (the signal note references it as a residual). If the flag is absent, the auto-accept path may not respect the GI-specific pause mechanism. Reason cannot be filled: requires W1 to confirm flag presence in the `feature_flags` table and author a migration if absent.

---

## Cross-references

- `docs/integrations/green_invoice_supplier_price_contract.md` (2026-04-21, executor-w4, commit `ac7c579`) — full field-level requirements spec with live API inspection evidence. This spec builds the operational-requirements view on top of that contract. The prior contract governs: GI API field names, incremental sync strategy, rate limit handling, and the original UNRESOLVED item list (U-T1 through U-LI1). This spec ADDS the 3% threshold Tom-lock and the `std_cost_per_inv_uom` update path.
- `docs/integrations/green_invoice_ingest_contract.md` (2026-04-14) — higher-level Tranche-6 business-rules sketch; superseded on field-name specifics by the 2026-04-21 contract.
- `db/migrations/0063_green_invoice_ingest_state.sql` — `gi_ingest_state` and `gi_expense_mirror` schemas (confirmed in §2).
- `db/migrations/0071_suppliers_green_invoice_supplier_id.sql` — `suppliers.green_invoice_supplier_id` column (confirmed in §3.1).
- `db/migrations/0025_change_log_and_price_history.sql` — `price_history` schema (confirmed in §6.1) and `change_log` schema (action enum in §5.2 / §5.3).
- `db/migrations/0075_supplier_items_std_cost.sql` — `supplier_items.std_cost_per_inv_uom` column added 2026-04-23 as Path B fix (confirmed in §5.2 / §6.3). NOTE: `0002_masters.sql` carries `std_cost_per_inv_uom` on `components` (not `supplier_items`); the `supplier_items` version is the `0075` landing.
- `supabase/functions/factory_os_jobs/index.ts` — deployed GI handler: `runGreenInvoicePoll`, `giResolveSupplier` (confirmed field access in §2, §3.1).
- `CLAUDE.md` §"Locked decisions — Orders and integrations" + §"Source-of-truth map" + §"Integration guidance — Green Invoice" — binding upstream rules honored throughout.
- `CURRENT_STATE.md` §"Open UNRESOLVED items" — GI line-item UNRESOLVED resolved directionally (no line items); auto-price threshold previously open, now Tom-locked at 3%.

---

**End of spec.**
