# Customer Credit Automation (Order-to-Delivery Variance) — Contract-Requirements Spec

**Owner:** W4 (Integrations / Jobs / Exports / Dashboard Contracts)
**Kind:** requirements-only. No schema DDL, no migration SQL, no runtime code, no handler implementations.
**Authored:** 2026-04-27.
**Status:** **DESIGN — NOT PRODUCTION-READY. Live Morning issuance is forbidden until the sandbox verification checklist (§10) passes end-to-end with documented evidence.**

**Evidence consumed:**
- `CLAUDE.md` — locked architecture, source-of-truth boundaries (Green Invoice scoped only for supplier invoices in current locked architecture; this spec proposes the customer-side extension).
- `docs/operational_dataflow_blueprint.md` (2026-04-23) — event/object dataflow map.
- Tom-led discovery dialogue (2026-04-27) — current human flow, role assignments (Dorin / Andrei / Maxim), 14:00 cutoff, 16:00 picking, "אישור" / "בוצע" / "בוטל" semantics in LionWheel.
- Tom-led independent verification of Morning (Green Invoice) API (2026-04-27) — confirmed document types 305 / 320 / 330, document/created webhook payload shape, sandbox availability, type-320 two-step credit rule.
- Reference: official Morning API docs at `https://www.greeninvoice.co.il/api-docs/` and `https://greeninvoice.docs.apiary.io/`.

**Locked upstream decisions honored (CLAUDE.md):**
- "Forms and integrations create events" — LionWheel and Morning are integrations, not authoring surfaces.
- "Postgres stores truth" — Factory OS owns the credit *draft*. Morning owns only the *signed accounting document* after Dorin approval.
- "No round-trip editing" — once issued in Morning, corrections happen via new documents (e.g., a credit on a credit), never by editing the prior document.
- "Prefer clear failure over silent drift" — every API attempt is logged with idempotent retry semantics; ambiguous outcomes route to a manual reconciliation lane, not a silent retry.
- Customer-side Morning integration is **outside the current locked architecture** (CLAUDE.md scopes Green Invoice to supplier invoices only). This spec is the formal proposal to extend it to customer credits. Tom must explicitly accept the extension before production cutover.

**Tom-locked decisions honored (this dialogue, 2026-04-27):**
- B2B only. Single driver (Maxim). Single picker (Andrei). Order intake operator: Dorin.
- Production is OUT OF SCOPE for this spec. Picking is from existing FG only.
- No substitutions allowed at picking time. Out-of-stock items are picked at qty = 0.
- Customer rejecting part of an order at the door is OUT of automation scope (Maxim → Dorin manual flow).
- Customer complaints after delivery are OUT of automation scope (Dorin manual flow).
- "Morning" and "Green Invoice" refer to the same product (חשבונית ירוקה / morning by Green Invoice). Used interchangeably in this spec.

---

## 1. Purpose and scope

### 1.1 What this spec governs

The automation of customer credit notes (חשבוניות זיכוי) issued to B2B customers when the actually-delivered quantity is less than the originally-invoiced quantity. The original invoice is auto-issued by Shopify → Morning at the moment of order receipt, before picking; the credit reflects the difference.

Specifically:
- Detection of variance via LionWheel events ("בוצע" / "בוטל").
- Construction of a credit *draft* held in Factory OS.
- Dorin's review surface (single screen, single approval action).
- Issuance to Morning **only after Dorin approval**, branched by original document type.
- Idempotent retry, ambiguous-outcome reconciliation, and manual fallback.
- Sandbox-first verification before any production claim.

### 1.2 What is out of scope

- Production reporting, BOM consumption, RM ordering — covered elsewhere; not relevant to order-to-delivery flow.
- Manual partial-rejection-at-door flow (Maxim phones Dorin; Dorin issues credit fully manually in Morning UI). The automation does **not** attempt to detect or auto-draft this case. Surfaced only as a known exception lane (§9).
- Post-delivery customer complaints (received via WhatsApp/phone). Same — manual lane only.
- Cancellation before 14:00 cutoff (handled by Shopify deletion + manual credit, not auto). The auto path covers cancellations after the LionWheel line is closed.
- D2C (Shopify direct-to-consumer) — Tom confirmed B2B only; no D2C handling required.

### 1.3 Why this exists

Morning auto-issues a tax invoice or invoice/receipt at Shopify order receipt, on the **full ordered quantity**. From that moment, the business is financially committed for the full amount. Any underpicking creates a regulatory liability — the customer is owed a refund/credit. Today this is reconciled manually by Dorin, which is slow, error-prone, and tightly coupled to Dorin's availability. This spec automates the variance-to-credit-draft path and reduces Dorin's role from authoring to approving.

---

## 2. Source triggers

### 2.1 LionWheel events (variance source)

| Event | Trigger | Variance basis | Result if successful |
|---|---|---|---|
| `lionwheel.order.delivered` ("בוצע") | Driver Maxim marks order as delivered | `variance_qty = ordered_qty − picked_qty` per line | Auto-draft credit if any line has `variance_qty > 0` |
| `lionwheel.order.cancelled` ("בוטל") | Order cancelled at any stage before delivery completion | Full ordered quantity | Auto-draft full credit; no stock decrement |
| `lionwheel.order.cancelled` after `lionwheel.order.delivered` | Atypical: cancellation marked after delivery already completed | Full ordered quantity | Manual review — atypical sequence must not be auto-issued |

**Picked quantity source:** LionWheel order line `picked_qty` field, locked when Andrei presses "אישור" on the picking page. Once locked, the field is treated as final. (Open question — see §11 — whether LionWheel allows un-locking after "אישור".)

### 2.2 Morning `document/created` webhook (original document source)

The Shopify → Morning auto-issue flow produces a document of either type 305 (חשבונית מס) or type 320 (חשבונית מס/קבלה). The Factory OS subscribes to Morning's `document/created` webhook and mirrors the relevant fields locally so the credit draft has a stable, queryable source for amounts, prices, and customer mapping — independent of Morning availability at the moment of credit construction.

**Webhook events to subscribe:** `document/created`, filtered by `type ∈ {305, 320}`.

**Mirrored fields per document (from confirmed payload shape):**
- `id` (Morning UUID), `number`, `type` (305 / 320), `businessId`
- `recipient.id` (Morning customer UUID — the credit's `linkedDocumentIds` target customer; **must not** be re-derived from Shopify)
- `recipient.name`, `recipient.emails`
- `date`, `currency`, `subtotal`, `total`, `tax[]`
- `items[]` per line: `description`, `sku`, `quantity`, `price`, `currency`, `taxIncludedInPrice`
- `files.downloadLinks` (he/en/origin PDFs)
- The full raw payload (jsonb, for debugging and future field discovery)

**Linking to Shopify order:** the webhook payload may or may not include a Shopify order reference. If absent, the linkage must be reconstructed via a separate strategy (see §11). Until that linkage is reliable, drafts cannot be auto-built and must route to NEEDS_MANUAL_REVIEW.

---

## 3. Two issuance branches (CRITICAL)

This is the core architectural correction from Tom's verification on 2026-04-27.

### 3.1 Branch A — Original document is type 305 (חשבונית מס)

A pure tax invoice with no payment record attached. Crediting it requires **one document**:
- Type 330 credit invoice, linked to the original 305.

Partial credit is supported by Morning's UI; API support is assumed but **not verified** (see §11).

### 3.2 Branch B — Original document is type 320 (חשבונית מס/קבלה)

A combined tax-invoice + receipt. The document has both *invoice* meaning (the sale) and *payment* meaning (the receipt). Crediting it requires **two linked documents**:
- Type 330 credit invoice — to credit the invoice/sale leg.
- A negative receipt (likely type 400 with negative amount, or a dedicated mechanism) — to unwind the payment leg.

Both documents must be issued, both must reference the original 320, and both must succeed for the credit to be considered complete. Partial completion (one succeeds, the other fails) is an error state requiring reconciliation.

The API path for the negative receipt is **not yet officially verified** (see §11). Until sandbox proof exists for the full 305+320 paths, drafts whose original is type 320 must route to **NEEDS_MANUAL_REVIEW** (Dorin handles entirely in Morning UI). The state machine reflects this constraint.

### 3.3 Why this matters

A naive design that issues only a type 330 against an original 320 would produce a Morning state where the invoice is marked credited but the receipt remains posted. The customer would appear to have paid for goods they did not receive, with no offsetting receipt reversal — violating both Israeli accounting requirements and the customer's expectation of a clean refund. This is not recoverable by retry; it is a structural error.

Therefore: **`requires_two_step_issuance` is determined by the original document's type, computed at draft-construction time, and persisted on the draft. The state machine routes accordingly.**

---

## 4. Architectural position in Factory OS

### 4.1 Layer placement

This automation sits in the **Jobs / Integrations** layer (per CLAUDE.md core architectural model §9). It is:
- Triggered by integration events (LionWheel + Morning webhook).
- Writes to its own canonical tables (§5).
- Does not mutate `stock_ledger` directly; the existing "בוצע" → stock decrement path remains intact and unaffected.
- Does not mutate `master data`.
- Does not mutate `planning_runs`.
- Exposes a single read-model surface for Dorin's review screen.

### 4.2 Source of truth split

| Owns | Owner |
|---|---|
| Credit *draft* (pending Dorin approval) | Factory OS |
| Original invoice mirror (cache for variance computation) | Factory OS (cache); Morning is upstream |
| Issued credit document (signed, in customer accounting record) | Morning |
| Issuance attempt log + retry state | Factory OS |
| Stock decrement on "בוצע" | Factory OS (unchanged) |

**Rule:** Until Dorin approves a draft, no Morning POST occurs. There is no "draft document in Morning" representation; if API draft creation turns out to be supported (§11), that is an optimization, not a correctness requirement.

---

## 5. State machine

### 5.1 States

| State | Meaning | Terminal? |
|---|---|---|
| `DETECTED` | LionWheel event received; variance computed; draft construction in progress | no |
| `PENDING_DORIN_REVIEW` | Draft fully built, all guards passed, awaiting Dorin's decision | no |
| `NEEDS_MANUAL_REVIEW` | Draft cannot be auto-built or auto-issued; Dorin handles entirely in Morning UI | semi-terminal (closed by Dorin tagging the case as resolved) |
| `APPROVED_PENDING_ISSUE` | Dorin approved; original is type 305; single-document issuance queued | no |
| `APPROVED_PENDING_TWO_STEP_ISSUE` | Dorin approved; original is type 320; two-document issuance queued; only reachable once §10 sandbox checklist for type-320 has passed | no |
| `ISSUE_IN_PROGRESS` | Worker actively calling Morning API | no |
| `ISSUED_CREDIT_ONLY` | Type 330 credit invoice successfully issued (Branch A success) | terminal |
| `ISSUED_CREDIT_AND_NEGATIVE_RECEIPT` | Both type 330 + negative receipt successfully issued (Branch B success) | terminal |
| `ISSUE_FAILED_RETRYABLE` | Transient API failure (timeout, 5xx); will retry per backoff policy | no |
| `ISSUE_UNKNOWN_NEEDS_RECONCILIATION` | API call sent but response not received or ambiguous; cannot determine if Morning accepted | no |
| `ISSUE_FAILED_MANUAL` | Permanent failure or retries exhausted; Dorin must resolve in Morning UI | terminal-with-action |
| `REJECTED` | Dorin rejected the draft (with reason) | terminal |

### 5.2 Allowed transitions

```
DETECTED
  → PENDING_DORIN_REVIEW          (all guards passed; original is type 305 OR type 320 with sandbox proven)
  → NEEDS_MANUAL_REVIEW           (any guard failed: missing original, ambiguous customer mapping, substitution detected,
                                   or original is type 320 and sandbox not yet proven)

PENDING_DORIN_REVIEW
  → APPROVED_PENDING_ISSUE        (Dorin approves; original type 305)
  → APPROVED_PENDING_TWO_STEP_ISSUE (Dorin approves; original type 320; sandbox proven)
  → REJECTED                      (Dorin rejects with reason)
  → NEEDS_MANUAL_REVIEW           (Dorin sends to manual)

APPROVED_PENDING_ISSUE              → ISSUE_IN_PROGRESS
APPROVED_PENDING_TWO_STEP_ISSUE     → ISSUE_IN_PROGRESS

ISSUE_IN_PROGRESS
  → ISSUED_CREDIT_ONLY               (Branch A success — single doc issued)
  → ISSUED_CREDIT_AND_NEGATIVE_RECEIPT (Branch B success — both docs issued)
  → ISSUE_FAILED_RETRYABLE           (transient: HTTP 5xx, network timeout that returned before response sent)
  → ISSUE_UNKNOWN_NEEDS_RECONCILIATION (request sent but response unknown — cannot determine if Morning created the document)
  → ISSUE_FAILED_MANUAL              (permanent: HTTP 4xx not retryable, validation rejection, etc.)

ISSUE_FAILED_RETRYABLE
  → ISSUE_IN_PROGRESS                (retry attempt within backoff envelope)
  → ISSUE_FAILED_MANUAL              (max retries exhausted)

ISSUE_UNKNOWN_NEEDS_RECONCILIATION
  → ISSUED_CREDIT_ONLY               (reconciliation finds the document was created in Morning — Branch A)
  → ISSUED_CREDIT_AND_NEGATIVE_RECEIPT (reconciliation finds both docs created — Branch B)
  → ISSUE_IN_PROGRESS                (reconciliation finds nothing was created; safe to retry)
  → ISSUE_FAILED_MANUAL              (reconciliation cannot determine state OR finds partial creation in Branch B)

NEEDS_MANUAL_REVIEW                  → semi-terminal; Dorin marks resolved with optional Morning document references
ISSUED_CREDIT_ONLY                   → terminal
ISSUED_CREDIT_AND_NEGATIVE_RECEIPT   → terminal
ISSUE_FAILED_MANUAL                  → terminal-with-action
REJECTED                             → terminal
```

### 5.3 Branch B partial-success handling

For `APPROVED_PENDING_TWO_STEP_ISSUE`:
1. Issue the type 330 credit invoice first.
2. On success, capture the credit invoice's Morning document id.
3. Issue the negative receipt second, referencing both the original 320 and the just-issued 330.
4. Only when both succeed → `ISSUED_CREDIT_AND_NEGATIVE_RECEIPT`.
5. If step 1 fails: standard retry / failure path.
6. If step 2 fails after step 1 succeeded: state moves to `ISSUE_FAILED_MANUAL` with explicit reason `partial_two_step_completion` — the customer accounting record is in an inconsistent state (credit issued, receipt unreversed). Dorin must resolve in Morning UI. The credit invoice id is preserved so Dorin sees what was already issued.

---

## 6. Data model (logical — DDL is a separate authoring step)

Five canonical tables. All in private schema (per CLAUDE.md security rule). Primary keys are UUIDs unless otherwise noted.

### 6.1 `green_invoice_documents` — local mirror of relevant Morning documents

| Column | Type | Notes |
|---|---|---|
| `id` | UUID PK | Internal |
| `gi_document_id` | UUID UNIQUE | Morning's document UUID |
| `gi_document_number` | text | Morning's human-readable number |
| `gi_document_type` | int | 305, 320, 330, 400, etc. |
| `gi_recipient_id` | UUID | Morning customer UUID — authoritative for credit linkage |
| `gi_recipient_name` | text | Snapshot |
| `gi_recipient_emails` | jsonb | Snapshot — array of strings |
| `document_date` | date | From payload |
| `currency` | text | ILS expected |
| `subtotal` | numeric | High-precision quantity standard |
| `total` | numeric | High-precision |
| `tax_breakdown` | jsonb | From payload's `tax[]` array |
| `pdf_he_url`, `pdf_en_url`, `pdf_origin_url` | text | From payload's `files.downloadLinks` |
| `linked_document_ids` | jsonb | Empty for originals; populated for credits |
| `linked_to_originals` | jsonb | For credits/negative-receipts: array of original doc UUIDs being linked |
| `shopify_order_id` | text NULL | Linkage strategy may take time to populate (see §11) |
| `raw_payload` | jsonb | Full webhook payload for debugging / future field discovery |
| `received_at` | timestamptz | Webhook receipt time |
| `created_at`, `updated_at` | timestamptz | Standard |

**Constraints:** `gi_document_id` UNIQUE; `gi_document_type` CHECK in known set; `(received_at, gi_document_type)` indexed for freshness queries.

### 6.2 `green_invoice_document_lines` — line items mirror

| Column | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `gi_document_id_fk` | UUID FK → `green_invoice_documents.id` | |
| `line_number` | int | 1-based, preserves original line order |
| `sku` | text | Required for variance matching; if missing on the original, draft auto-build is blocked → NEEDS_MANUAL_REVIEW |
| `description` | text | Snapshot |
| `quantity` | numeric | High-precision quantity |
| `unit_price` | numeric | Money standard scale (per CLAUDE.md) — authoritative for credit pricing |
| `currency` | text | |
| `vat_included_in_price` | boolean | Mirror of `taxIncludedInPrice` |
| `raw` | jsonb | Anything else from the line |

### 6.3 `customer_credit_drafts` — internal draft, the heart of the automation

| Column | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `lionwheel_order_id` | text | The LionWheel order this credit relates to |
| `shopify_order_id` | text NULL | Linkage; required to find the original GI document |
| `gi_original_document_id_fk` | UUID FK → `green_invoice_documents.id` | The original invoice being credited |
| `gi_original_document_type` | int | 305 or 320 — authoritative for branching; persisted at draft-build time, not re-read at issuance |
| `requires_two_step_issuance` | boolean | Derived from `gi_original_document_type`: `true` if 320, `false` if 305 |
| `trigger_event` | text | `lionwheel_delivered_with_variance` \| `lionwheel_cancelled` \| `lionwheel_cancelled_after_delivered` |
| `variance_total_amount` | numeric | Money standard |
| `currency` | text | |
| `state` | text | One of the §5.1 states |
| `state_reason` | text NULL | Free-text explanation of the current state (especially useful for NEEDS_MANUAL_REVIEW and ISSUE_FAILED_MANUAL) |
| `idempotency_key` | text UNIQUE | Format: `lionwheel_order_${id}_${trigger_event}` — prevents duplicate drafts from webhook retries |
| `auto_build_guards_passed` | jsonb | Audit of which guards passed/failed at draft-construction time |
| `created_at`, `updated_at` | timestamptz | |
| `approved_at` | timestamptz NULL | |
| `approved_by_user_id` | UUID NULL | |
| `approved_by_display_name` | text NULL | Audit snapshot per CLAUDE.md schema guidance |
| `rejected_at` | timestamptz NULL | |
| `rejected_by_user_id` | UUID NULL | |
| `rejected_reason` | text NULL | |
| `gi_credit_document_id_fk` | UUID FK → `green_invoice_documents.id` NULL | Populated post-issuance, Branch A and Branch B |
| `gi_negative_receipt_document_id_fk` | UUID FK → `green_invoice_documents.id` NULL | Populated post-issuance, Branch B only |

**Constraints:**
- `idempotency_key` UNIQUE — single most important constraint; prevents double-drafts.
- `state` CHECK in the §5.1 set.
- `(state, updated_at)` indexed for Dorin's review queue and for the retry worker.
- When `state` enters `ISSUED_CREDIT_AND_NEGATIVE_RECEIPT`, both `gi_credit_document_id_fk` and `gi_negative_receipt_document_id_fk` MUST be non-null (DB constraint).

### 6.4 `customer_credit_draft_lines` — variance breakdown per line

| Column | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `draft_id_fk` | UUID FK → `customer_credit_drafts.id` | |
| `line_number` | int | Matches the original GI document's `line_number` |
| `sku` | text | |
| `description` | text | Snapshot from original |
| `ordered_quantity` | numeric | From the original GI document line — authoritative |
| `picked_quantity` | numeric | From LionWheel; 0 for full cancellation |
| `variance_quantity` | numeric | `ordered − picked`; always ≥ 0 (negative variance = picked more than ordered = process violation, routes to NEEDS_MANUAL_REVIEW) |
| `unit_price` | numeric | From original GI document line — used for credit pricing |
| `vat_included_in_price` | boolean | Mirror |
| `variance_amount` | numeric | `variance_quantity × unit_price`, plus VAT handling consistent with original |

**Constraints:** `(draft_id_fk, line_number)` UNIQUE.

### 6.5 `customer_credit_issue_attempts` — every API call attempt

| Column | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `draft_id_fk` | UUID FK → `customer_credit_drafts.id` | |
| `step` | text | `credit_invoice` \| `negative_receipt` \| `reconciliation_check` |
| `attempt_number` | int | Per-draft, per-step counter starting at 1 |
| `attempted_at` | timestamptz | |
| `request_idempotency_key` | text | Sent to Morning if their API supports idempotency keys (verify in §10); otherwise `(draft_id, step, attempt_number)` deterministic key |
| `request_payload` | jsonb | Snapshot of what we sent |
| `response_status` | text | HTTP code (`200`, `400`, `500`...) OR `TIMEOUT` OR `NETWORK_ERROR` OR `UNKNOWN` |
| `response_body` | jsonb | Snapshot of what we got back, if anything |
| `gi_document_id_returned` | UUID NULL | If the call succeeded |
| `error_class` | text NULL | `transient` \| `permanent` \| `unknown` — derived classification |
| `error_message` | text NULL | Human-readable |
| `next_action` | text | `retry` \| `proceed_next_step` \| `fail_manual` \| `reconcile` \| `success` |

**Append-only.** No update of past attempts. Reconciliation findings are written as new attempt rows with `step = 'reconciliation_check'`.

### 6.6 `customer_credit_events` — append-only event log

| Column | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `draft_id_fk` | UUID FK → `customer_credit_drafts.id` | |
| `event_type` | text | `state_transition` \| `dorin_action` \| `gi_webhook_received` \| `lionwheel_event_received` \| `api_call_attempted` \| `reconciliation_attempt` |
| `event_data` | jsonb | Type-specific payload (e.g., `{from: 'PENDING_DORIN_REVIEW', to: 'APPROVED_PENDING_ISSUE'}` for state_transition) |
| `actor` | text | `system` OR `user:<uuid>` |
| `occurred_at` | timestamptz | |

Append-only. Backbone of audit trail and timeline rendering on Dorin's screen.

---

## 7. Dorin UX requirements

### 7.1 Surface

Single screen in the Factory OS portal: **"זיכויים ממתינים לאישור"** (Pending Credit Approvals). Hebrew operator UI per CLAUDE.md.

Default view: list of drafts in `PENDING_DORIN_REVIEW`, sorted by `updated_at` ascending (oldest first — fairness).

Filters: state (default = pending), date range, customer, draft type (simple credit vs. two-step), source freshness flags.

### 7.2 List row — minimum fields per draft

- **Customer name** (`gi_recipient_name`)
- **Original invoice number** + type badge (`חשבונית מס #1234` or `חשבונית מס/קבלה #1234` — Hebrew label by type)
- **Total credit amount** in NIS
- **Issuance complexity badge:**
  - `פשוט` (simple — type 305 path)
  - `כפול: זיכוי + קבלה שלילית` (two-step — type 320 path; until sandbox proven, this badge is shown alongside a banner "טרם אומת ב-sandbox — יש לטפל ידנית")
- **Reason summary** (e.g., "חוסר במלאי על 2 מוצרים בעת מסירה", "ביטול מלא של ההזמנה")
- **Source freshness:** two indicators — when LionWheel "בוצע" was received; when the Morning original was mirrored. Stale if either > 24 hours; flagged if mismatched relative to today's cutoff.

### 7.3 Detail view — full draft

When Dorin opens a draft:

- **Header:** customer, original invoice (clickable to PDF in Morning), LionWheel order id (clickable to LionWheel UI).
- **Variance table — one row per line:**
  - SKU, description, ordered qty, picked/delivered qty, variance qty, unit price (from original), variance amount.
  - Lines with `variance_quantity = 0` shown collapsed/dimmed.
- **Total credit amount.**
- **Reason text** (auto-generated, editable by Dorin before approval — edit captured in `state_reason`).
- **Source freshness panel:** timestamps for original webhook, LionWheel event, last system attempt (if any).
- **Issuance plan preview:**
  - Branch A: "יוצר חשבונית זיכוי (type 330) המקושרת לחשבונית מקור #1234"
  - Branch B: "יוצר חשבונית זיכוי + קבלה שלילית, שניהם מקושרים לחשבונית מקור #1234. **שני המסמכים חייבים להצליח כדי שהזיכוי ייחשב לסגור.**"
- **Timeline:** `customer_credit_events` rendered as a chronological list.

### 7.4 Actions

| Button | Hebrew label | Resulting transition | Pre-conditions |
|---|---|---|---|
| Approve and issue (single) | אישור והפקה | `PENDING_DORIN_REVIEW → APPROVED_PENDING_ISSUE` | Original is type 305 |
| Approve and issue (two-step) | אישור והפקה כפולה | `PENDING_DORIN_REVIEW → APPROVED_PENDING_TWO_STEP_ISSUE` | Original is type 320 AND sandbox checklist §10 has passed (system flag) |
| Send to manual | שליחה לטיפול ידני ב-Morning | `PENDING_DORIN_REVIEW → NEEDS_MANUAL_REVIEW` | Always available |
| Reject | דחייה | `PENDING_DORIN_REVIEW → REJECTED` | Reason text required |

**Constraint until sandbox-§10-pass:** If the original is type 320 and the sandbox checklist has not yet passed, the "אישור והפקה כפולה" button is disabled and replaced with "אישור והעבר לטיפול ידני ב-Morning" — the only way to close a type-320 draft until proven sandbox-safe.

### 7.5 Read model freshness contract

Dorin's screen reads from a curated read model, not directly from the canonical tables. The read model must reflect any state change within ≤ 5 seconds of the canonical write (subscription or short-poll). Stale > 60 seconds is a freshness exception.

---

## 8. Idempotency, retry, reconciliation

### 8.1 Webhook idempotency

LionWheel may deliver the same event twice (network retry). Each draft's `idempotency_key = lionwheel_order_${id}_${trigger_event}` is UNIQUE; a duplicate webhook is a no-op insert that returns the existing draft.

Morning `document/created` webhooks may also be redelivered. The `gi_document_id` UNIQUE constraint on `green_invoice_documents` makes redelivery a no-op upsert.

### 8.2 API retry policy

For `ISSUE_FAILED_RETRYABLE` (HTTP 5xx, network timeout that returned before request was sent):
- Exponential backoff: 30s, 2m, 10m, 30m, 2h, 8h.
- Max 6 attempts, then transition to `ISSUE_FAILED_MANUAL`.
- Each attempt is a new row in `customer_credit_issue_attempts`.

### 8.3 Ambiguous outcome reconciliation

When an API call returns no clear response (timeout *after* request was sent, broken connection mid-write, etc.), the state is `ISSUE_UNKNOWN_NEEDS_RECONCILIATION`. The system must NOT retry the original POST — that risks duplicate creation. Instead, a reconciliation worker:
1. Queries Morning for documents created in the last N minutes for this customer matching the draft's expected fingerprint (linked-to original, total amount, line count).
2. If found: capture the document id, transition to `ISSUED_*`.
3. If not found: safe to retry — transition to `ISSUE_IN_PROGRESS`.
4. If reconciliation itself errors or finds ambiguous results: transition to `ISSUE_FAILED_MANUAL` with reason `reconciliation_inconclusive`.

For Branch B (two-step), reconciliation must check both expected documents independently and may find a partial-completion state — which always routes to `ISSUE_FAILED_MANUAL`.

### 8.4 Morning idempotency support (open question)

If Morning's API supports an `Idempotency-Key` header (or equivalent), use it on every POST — keyed by `(draft_id, step, attempt_number)`. This converts ambiguous-outcome cases from "we don't know if it was created" to "we can safely retry and Morning will dedupe". This is one of the highest-value items in §10's sandbox checklist.

---

## 9. Manual lanes (out of automation scope, surfaced for Dorin)

These are real exception flows in the playbook but are NOT auto-handled. They appear on Dorin's screen as separate banners or in a separate manual-tracking surface.

| Scenario | Detection | Dorin action |
|---|---|---|
| Customer rejects part of order at the door | Maxim phones Dorin (no LionWheel event) | Dorin issues credit fully manually in Morning UI; manually updates FG stock to reflect returned items |
| Post-delivery customer complaint (damage, missing) | WhatsApp / phone | Dorin issues credit fully manually; investigates root cause |
| Cancellation before 14:00 cutoff | Shopify order deleted | Original auto-invoice already issued → Dorin must issue manual credit (Morning will not auto-credit a Shopify deletion) |
| `NEEDS_MANUAL_REVIEW` from automation | Automation flagged | Dorin handles in Morning UI; optionally records resulting Morning document IDs back in Factory OS for audit linkage |
| `ISSUE_FAILED_MANUAL` from automation | Automation exhausted retries | Dorin completes the issuance in Morning UI; system marks as resolved-with-manual-intervention |
| Driver forgot to mark "בוצע" | No event 24h after route close | Stale-route alert fires; Dorin investigates; manual stock + document reconciliation |
| Andrei forgot to press "אישור" | No event by 17:00 daily threshold | Late-picking alert; Andrei completes; downstream automation resumes |

These manual lanes do **not** route through the state machine. They are surfaced to Dorin via separate banners + a "פעולות ידניות נדרשות" tray.

---

## 10. Sandbox verification checklist (REQUIRED before production claim)

No `ISSUED_CREDIT_ONLY` or `ISSUED_CREDIT_AND_NEGATIVE_RECEIPT` transition is permitted in production until every check below has documented evidence: (a) the exact request payload sent, (b) the exact response received, (c) the resulting Morning document id (if any), and (d) a screenshot or fetched view of the Morning UI showing the documents and their linkage status.

### 10.1 Branch A (type 305) checklist

1. **Create type 305 original in sandbox.** Verify document is created; capture `id`, `number`, `recipient.id`, line items.
2. **POST a partial credit (type 330) referencing the 305.** Use `linkedDocumentIds: ["<305_id>"]` and a single `linkType` value at a time — try `cancel`, `cancellation`, `refund`, `partial_cancel` in separate test runs and log which the API accepts.
3. **Verify the credit only includes the variant lines** (not the full invoice). Confirm Morning UI shows the original 305 status as "מבוטל חלקית" or equivalent.
4. **Verify pricing on credit lines** matches the original 305's prices (not current price list).
5. **Verify customer linkage:** the credit is issued to the same `recipient.id` as the original.

### 10.2 Branch B (type 320) checklist

6. **Create type 320 original + payment in sandbox.** Verify document is created with both invoice and receipt semantics.
7. **POST credit (type 330) referencing the 320 — observe alone.** Confirm whether Morning treats this as sufficient or as half-complete. Document the resulting state in the Morning UI.
8. **Identify the negative-receipt API path.** This is unverified — investigate in the Morning sandbox docs and/or by trial:
   - Type 400 (קבלה) with negative qty/amount?
   - A dedicated cancellation endpoint?
   - A separate document type not yet listed?
9. **POST the negative receipt linked to the original 320 (and possibly to the 330 issued in step 7).** Capture exact payload.
10. **Verify Morning UI shows the original 320 as fully credited** — both invoice leg and receipt leg unwound. Take screenshots.
11. **Test partial-amount on Branch B:** repeat steps 6–10 but credit only some lines, not the full invoice.

### 10.3 Cross-cutting checklist

12. **Linked document field — singular vs. array.** Test `linkedDocumentIds: [...]` and `linkedDocumentId: "..."`. Document which is correct.
13. **`linkType` enum exhaustive test.** Test every plausible value; document the accepted set and the resulting Morning UI behavior for each.
14. **Email suppression.** POST with any plausible flag (`email: { send: false }`, `notifyClient: false`, `sendEmail: false`) — verify no email is sent. If no flag works, document that emails always fire and adjust Dorin UX accordingly (warn before approve).
15. **Idempotency on duplicate POST.** Send the same payload twice with the same `Idempotency-Key` header (if supported) and once without. Document Morning's deduplication behavior.
16. **Timeout / unknown result.** Simulate a sent-but-no-response scenario (kill connection mid-call). Wait. Then list documents created in the last 5 minutes for this customer. Verify whether Morning persisted the request. This is the basis for §8.3 reconciliation.
17. **Draft creation via API.** Test whether a payload with no payment, no signature, or with `status: 'draft'` (or whatever Morning's API accepts) creates a *non-final* document. If yes, this becomes an architectural option — but the chosen architecture (Factory OS owns the draft, Morning owns only signed) does not depend on this. Document the result either way.
18. **Document numbering.** Verify the credit's number is auto-assigned by Morning, sequential, and visible in the response. (Morning may reserve number ranges per document type — relevant for audit.)
19. **Tax / VAT recomputation.** Verify the credit's VAT is computed correctly relative to the original (not double-counted, not zero).
20. **Currency.** Confirm ILS is supported; flag any non-ILS handling (some original invoices may be in non-ILS — see existing `gi_non_ils_currency` exception in supplier-side feed).

### 10.4 Production cutover gate

The system may transition any draft to `ISSUED_*` in production **only when** all 20 checks above have:
- (a) a documented test run with payload/response captured;
- (b) a positive outcome OR an explicit, accepted workaround;
- (c) Tom's sign-off recorded in the Factory OS audit log.

Until then:
- Drafts with original type 305 may run end-to-end in **sandbox only**, with a feature flag `customer_credit_auto_issue.305.production = false` blocking production POSTs.
- Drafts with original type 320 may not auto-issue at all; they route to `NEEDS_MANUAL_REVIEW`. Feature flag `customer_credit_auto_issue.320.production = false` is the default and cannot be set to `true` until §10.2 and §10.3 are complete.

---

## 11. Open API questions (must be answered before §10 can proceed)

These are the precise technical questions that need verification against Morning's API — not from public docs, but from sandbox testing or direct vendor support. They are listed here so that whoever runs §10 has a clear question list.

1. **POST /documents payload for type 330 — exact field set.**
   - Q: What is the minimum required payload for a credit invoice that includes (a) lines, (b) a link to the original document, and (c) the original document's customer? Is `recipient.id` re-asserted, or inherited from the linked document?

2. **`linkedDocumentIds` vs. `linkedDocumentId`.**
   - Q: Which field name does Morning's API accept for linking a credit to its original? Is it always an array? Can it link to multiple originals (a credit covering two prior invoices)?

3. **`linkType` enum.**
   - Q: What are the supported values? At minimum, is `cancel` valid? Are there separate values for partial credit vs. full cancellation?

4. **API draft support.**
   - Q: Is there any way via the API to create a non-final, editable document that is not yet visible to the customer? If yes, what parameter triggers it? If no, all POSTs must be treated as final.

5. **`signed: false` semantics.**
   - Q: If `signed: false` is sent on a POST, does Morning create a draft, an unsigned final document, or reject the request as invalid?

6. **Email suppression on POST.**
   - Q: Is there a parameter that prevents Morning from emailing the customer at the moment of document creation? If not, the only path is to never POST until Dorin has approved — which is the chosen architecture.

7. **Idempotency / duplicate POST behavior.**
   - Q: Does Morning support an `Idempotency-Key` header (or equivalent body field)? If yes, what's the dedup window? If no, what happens on a duplicate POST — does Morning create two documents, return the existing, or reject?

8. **Negative-receipt API path (Branch B linchpin).**
   - Q: How does the API issue a receipt-cancellation that unwinds a type 320's payment leg? Is it a type 400 with negative amount? A dedicated endpoint? A specific `linkType` on a 330 that cascades? **This is the highest-priority question — Branch B cannot ship without a verified answer.**

9. **Shopify order id linkage on auto-issued documents.**
   - Q: When Shopify auto-issues a tax invoice via Morning, is there a stable field in the Morning document that captures the Shopify order id? (Sometimes stored in the `description` or a custom field.) If not, the system needs a heuristic linkage strategy (customer + date + total + lines fingerprint) — which is fragile and should be flagged.

10. **Webhook payload completeness.**
    - Q: Does the `document/created` webhook include the full `items[]` array with SKU, qty, price per line? Or only summary fields? If only summary, the system must do a follow-up GET on the document to fetch lines.

---

## 12. Acceptance criteria for production cutover

This automation is considered production-ready only when:

1. All 20 sandbox checks in §10 have documented evidence, captured in a verification report stored at `docs/integrations/customer_credit_sandbox_verification_report.md`.
2. All 10 open questions in §11 have documented answers in the same report.
3. Tom has explicitly accepted the extension of Morning integration to customer-side credits (CLAUDE.md amendment: source-of-truth map updated to include "Morning is authoritative for issued customer credits"; locked architecture amendment: Green Invoice scope extended to customer-side documents).
4. The customer mapping (Shopify customer ↔ Morning customer) has been audited at least once for accuracy across all active B2B customers (Tom-driven sample audit; `gi_recipient_id` per draft must always match the customer the original invoice was issued to).
5. The Dorin UX surface has been reviewed by Dorin in person and her workflow questions answered.
6. Feature flags `customer_credit_auto_issue.305.production` and `customer_credit_auto_issue.320.production` can be flipped to `true` and at least one production credit has issued cleanly end-to-end with Dorin's approval.
7. Rollback path is documented: how to stop new auto-issuances, how to reconcile drafts in flight, how to revert to fully-manual flow if the integration misbehaves in production.

Until all seven criteria are met, the spec status remains DESIGN — NOT PRODUCTION-READY.

---

## 13. Out-of-spec dependencies

This spec does not implement, but assumes the existence of:

- A working Shopify → Morning auto-invoice flow (already operational; Tom-confirmed).
- A working LionWheel mirror in Factory OS (already operational; per `operational_dataflow_blueprint.md`).
- A working stock-decrement-on-"בוצע" path (already operational; same source).
- An admin UI for managing the Shopify ↔ Morning ↔ LionWheel customer mapping (open dependency — must exist before the automation auto-builds drafts; otherwise drafts route to NEEDS_MANUAL_REVIEW for any customer not 1:1 mapped).
- A feature-flag mechanism for the `customer_credit_auto_issue.*` flags.

---

## 14. Document change log

| Date | Author | Change |
|---|---|---|
| 2026-04-27 | brainstorming dialogue with Tom | Initial spec authored after Tom's independent verification of Morning API and discovery of the type-320 two-step rule. Status: DESIGN — sandbox proof outstanding. |
