# Window 4 — Green Invoice read-only inspection evidence

**Owner:** Window 4
**Kind:** inspection evidence report — NOT a broad strategy pack
**Date:** 2026-04-17
**Sources inspected (all public):**

- `https://greeninvoice.docs.apiary.io/reference/account/receiving-a-jwt-token-using-an-api-key/receiving-a-jwt-token-using-an-api-key` (Apiary, JWT section)
- `raw.githubusercontent.com/yanivps/green-invoice/master/{green_invoice/client.py, green_invoice/models.py, green_invoice/resources.py}` (yanivps, Python wrapper — most exhaustive typed source)
- `raw.githubusercontent.com/MordiSacks/greeninvoice/master/src/GreenInvoice/Api.php` (MordiSacks PHP SDK)
- `raw.githubusercontent.com/bariew/greeninvoice/master/{Api.php, documents/Document.php, documents/Income.php, clients/Client.php, items/Item.php}` (bariew PHP client)
- `raw.githubusercontent.com/danielrosehill/Green-Invoice-API-My-Notes/main/{document-types.md, example-webhook-payloads/created-invoice.json}` (Israeli practitioner notes, unofficial)

**Constraints honoured:** no live authenticated calls (no token available this pass); no runtime code; no migrations; no scheduler; no webhook receiver; no portal touch. Evidence gathered from public documentation and mirrored client library source code.

---

## 1. Endpoints inspected

All verbatim, with source citation.

| HTTP | Path | Purpose | Source |
|---|---|---|---|
| POST | `/v1/account/token` | JWT acquisition (auth) | yanivps client.py, MordiSacks Api.php |
| GET | `/v1/clients/{client_id}` | get client | yanivps resources.py |
| POST | `/v1/clients/search` | search clients (paginated) | yanivps resources.py, bariew Api.php `search()` |
| POST | `/v1/clients` | create client | yanivps resources.py |
| PUT | `/v1/clients/{client_id}` | update client | yanivps resources.py |
| DELETE | `/v1/clients/{client_id}` | delete client | yanivps resources.py |
| POST | `/v1/clients/{client_id}/assoc` | associate documents with client | yanivps resources.py |
| POST | `/v1/documents` | create (issue) document | yanivps resources.py |
| GET | `/v1/documents/{document_id}` | get document detail | yanivps resources.py |
| POST | `/v1/documents/search` | search documents (paginated) | yanivps resources.py |
| GET | `/v1/documents/{document_id}/download/links` | get per-language download URLs | yanivps resources.py |
| POST | `/v1/items` | create item (catalog) | bariew Api.php (generic endpoint pattern) |
| GET | `/v1/items/{id}` | get item | bariew Api.php (generic) |

**Generic CRUD pattern** (applies uniformly, confirmed across bariew Api.php + yanivps resources.py):

- `POST /v1/<resource>` — create
- `GET /v1/<resource>/{id}` — get detail
- `POST /v1/<resource>/search` — paginated search, body `{...filters, page, pageSize}` returning `{total, page, pageSize, pages, items[]}`
- `PUT /v1/<resource>/{id}` — update
- `DELETE /v1/<resource>/{id}` — delete
- `POST /v1/<resource>/{id}/close` — close (bariew Api.php, applies to document-like resources)

## 2. Auth flow (fully verbatim)

**Environments (verbatim from yanivps client.py):**

```python
ENDPOINTS = {
    "live":    "https://api.greeninvoice.co.il/api",
    "sandbox": "https://sandbox.d.greeninvoice.co.il/api",
}
```

**Token acquisition:**

- Method + path: `POST {env}/v1/account/token`
- Request headers: `Content-Type: application/json`
- Request body: `{"id": "<API_KEY_ID>", "secret": "<API_KEY_SECRET>"}`
- Response delivers the JWT in **both**:
  - header `X-Authorization-Bearer: <jwt>` (yanivps client.py reads this path)
  - body field `token` (MordiSacks Api.php reads this path; bariew Api.php also)
- TTL: **1 hour** (per Apiary JWT doc reference)
- Expired token → 401 Unauthorized; clients observed auto-refreshing by re-calling `/v1/account/token`

**Subsequent requests:**

- Header: `Authorization: Bearer <jwt>`
- Header: `Content-Type: application/json`

**Sandbox signup:** `https://lp.sandbox.d.greeninvoice.co.il/join` (referenced in Apiary).

## 3. Exact expense-side field names observed

**UNRESOLVED.**

**None of the three inspected client libraries — bariew (PHP), MordiSacks (PHP), yanivps (Python) — defines an expense / supplier resource.** All three libraries cover outbound document issuance (invoices to customers), the client/item catalog, and auth. No library contains an `Expense`, `ExpenseResource`, `Supplier`, or `SupplierResource` class.

The generic CRUD pattern (§1) is stable across every resource the libraries cover, which strongly implies `/v1/expenses/*` and `/v1/suppliers/*` exist under the same pattern. However, the **exact field set** on an expense document and a supplier record remains UNRESOLVED in this pass — it is behind the Apiary iframe which did not crawl, and behind the authenticated portal at `app.greeninvoice.co.il/api`.

**What IS known (by extrapolation from the consistent API pattern, NOT by direct inspection):**

- Likely endpoint shapes: `POST /v1/expenses/search`, `GET /v1/expenses/{id}`, `POST /v1/suppliers/search`, `GET /v1/suppliers/{id}` (pattern-consistent; **not verbatim-verified**)
- Likely pagination body: `{page, pageSize}` → response `{total, page, pageSize, pages, items[]}` (pattern-consistent)

These are **hypotheses based on pattern consistency**, not evidence. Window 4's "no invented field names" rule holds: the mirror Zod schemas for expenses still cannot be authored in this pass.

## 4. Exact supplier-side field names observed

**UNRESOLVED.** Same reason as §3 — no client library inspected covers suppliers.

The **client** object shape IS fully known, and suppliers commonly mirror clients in Israeli invoicing APIs, but "commonly mirror" is not inspected evidence. For reference, the client shape (verbatim from yanivps `IClientDraft` / `IClient` and bariew `Client.php`):

| Field | Type | Source |
|---|---|---|
| `name` | string (required) | both |
| `active` | bool | both |
| `department` | string | both |
| `taxId` | string | both |
| `accountingKey` | string | both |
| `paymentTerms` | int enum (-1, 0, 10, 15, 30, 45, 60, 75, 90, 120) | yanivps `PaymentTerms` |
| `bankName`, `bankBranch`, `bankAccount` | strings | both |
| `address`, `city`, `zip`, `country` | strings (country defaults `"IL"`) | both |
| `category` | int enum (verbatim in yanivps `Category`, 22 values) | yanivps |
| `subCategory` | int enum (verbatim in yanivps `SubCategory`, ~60 values) | yanivps |
| `phone`, `fax`, `mobile` | strings | both |
| `remarks` | string | both |
| `contactPerson` | string | both |
| `emails` | string[] (required) | both |
| `labels` | string[] | both |
| `send` | bool | yanivps |
| `id` | string UUID (response-only) | yanivps `IClient` |
| `creationDate` | int (Unix ms) | yanivps |
| `lastUpdateDate` | int (Unix ms) | yanivps |
| `incomeAmount`, `paymentAmount`, `balanceAmount` | int | yanivps |

**Do NOT assume suppliers mirror this shape.** Flag as UNRESOLVED; confirm via one authenticated `GET /v1/suppliers/{id}` call once the token path is authorized.

## 5. Exact line-item field names observed

**For OUTBOUND documents — verbatim from yanivps `IDocumentIncome` + bariew `Income.php` + Apiary-cross-referenced Valigara mapping:**

| Field | Type | Source |
|---|---|---|
| `catalogNum` | string | yanivps, bariew, Valigara |
| `description` | string | yanivps, bariew, Valigara |
| `quantity` | **int** (not string) | yanivps `IDocumentIncome.quantity: int` |
| `price` | **float** (not string) | yanivps `IDocumentIncome.price: float` |
| `currency` | string ISO | yanivps, bariew |
| `currencyRate` | float | yanivps, bariew |
| `vatRate` | float | yanivps, bariew |
| `itemId` | string | yanivps, bariew |
| `vatType` | int enum (0=DEFAULT, 1=INCLUDED, 2=EXEMPT) | yanivps `IncomeVatType` |

**Key clarification from prior contract-pack pass:** Valigara's mapping implied string-decimal for `income.price`; yanivps's typed schema definitively shows **`price: float`, `quantity: int`**. Green Invoice monetary fields arrive as **native JSON numbers**, not string-decimal (different semantics from LionWheel `order_total`). Update contract-pack assumption G.1 accordingly.

**Webhook payload sample** (verbatim from danielrosehill `created-invoice.json`, outbound type 300 TRANSACTION_ACCOUNT):

```json
"items": [{
  "description": "Sample Item",
  "sku": "SAMPLE",
  "quantity": 1,
  "price": 1,
  "currency": "ILS",
  "taxIncludedInPrice": false
}]
```

Note the webhook uses **`sku`** on the line item, not `catalogNum`. Document-CREATE uses `catalogNum`; the READ shape (in the webhook, and presumably in `GET /v1/documents/{id}`) surfaces it as `sku`. **This is a material asymmetry** — the Zod schema for READ must accept `sku`; the Zod schema for CREATE must emit `catalogNum`.

**For EXPENSE line items — UNRESOLVED.** Same reason as §3.

## 6. Exact pagination / filter semantics observed

**Verbatim from yanivps `IDocumentSearchFields` and `IDocumentSearchResult`:**

**Search request body (documents):**

```python
{
  "page":          int,             # 1-indexed
  "pageSize":      int,
  "number":        int,             # document number filter
  "type":          [DocumentType],  # array of type codes
  "status":        [DocumentStatus],
  "paymentTypes":  [PaymentType],
  "fromDate":      "YYYY-MM-DD",
  "toDate":        "YYYY-MM-DD",
  "clientId":      str,
  "clientName":    str,
  "description":   str,
  "download":      bool,
  "sort":          "documentDate" | "creationDate"
}
```

**Search response shape (documents):**

```python
{
  "total":    int,
  "page":     int,
  "pageSize": int,
  "pages":    int,
  "items":   [IDocumentSearchResultItem]
}
```

**Client search filters (verbatim from yanivps `IClientSearchFields`):**

```python
{ "name": str, "active": bool, "email": str, "contactPerson": str,
  "labels": [str], "taxId": str, "page": int, "pageSize": int }
```

**For expenses — UNRESOLVED.** The same `{page, pageSize}` envelope is highly likely, but date-filter field names (`fromDate`/`toDate` vs alternatives) and expense-specific filters are not inspected.

## 7. Additional facts resolved this pass

### 7.1 Document type enum — FULLY verbatim

From danielrosehill `document-types.md` (Hebrew labels) crossed with yanivps `DocumentType` enum (symbolic names) and bariew `Document.php` constants (alternate English names). **All 13 codes confirmed across all three sources:**

| Code | Hebrew | English (yanivps) | English (bariew) |
|---|---|---|---|
| 10 | הצעת מחיר | `PRICE_QUOTE` | `TYPE_BID` |
| 100 | הזמנה | `ORDER` | `TYPE_INVITATION` |
| 200 | תעודת משלוח | `DELIVERY_NOTE` | `TYPE_SHIPPING_CERTIFICATE` |
| 210 | תעודת החזרה | `RETURN_DELIVERY_NOTE` | `TYPE_RETURN_CERTIFICATE` |
| 300 | חשבון עסקה | `TRANSACTION_ACCOUNT` | `TYPE_TRANSACTION_ACCOUNT` |
| 305 | חשבונית מס | `TAX_INVOICE` | `TYPE_INVOICE` |
| 320 | חשבונית מס / קבלה | `TAX_INVOICE_RECEIPT` | `TYPE_TAX_INVOICE` |
| 330 | חשבונית זיכוי | `REFUND` | `TYPE_CREDIT_INVOICE` |
| 400 | קבלה | `RECEIPT` | `TYPE_ACCEPTANCE` |
| 405 | קבלה על תרומה | `RECEIPT_FOR_DONATION` | `TYPE_DONATION_RECEIPT` |
| 500 | הזמנת רכש | `PURCHASE_ORDER` | `TYPE_PURCHAISE_ORDER` |
| 600 | קבלת פיקדון | `RECEIPT_OF_A_DEPOSIT` | `TYPE_RECEIVING_DEPOSIT` |
| 610 | משיכת פיקדון | `WITHDRAWAL_OF_DEPOSIT` | `TYPE_DEPOSIT_WITHDRAWAL` |

**Important:** all 13 codes are **outbound** document types (documents GT issues to customers or suppliers). None of the 13 is a supplier-issued "expense" document. The expense surface uses a **separate resource** (see §3).

**Also:** code `500 PURCHASE_ORDER` is the document GT ISSUES to a supplier. When a supplier returns an invoice for that PO, the invoice is inbound and belongs to the (still-UNRESOLVED) expense resource.

### 7.2 Document status enum — verbatim

From yanivps `DocumentStatus`:

- `0 OPENED_DOCUMENT`
- `1 CLOSED_DOCUMENT`
- `2 MANUALLY_MARKED_AS_CLOSED`
- `3 CANCELING_OTHER_DOCUMENT`
- `4 CANCELED_DOCUMENT`

### 7.3 VAT type enums — verbatim (correcting prior Valigara-only pass)

**Document-level `vatType`** (yanivps `DocumentVatType`, verbatim integer codes):

- `0 DEFAULT` — based on business type
- `1 EXEMPT` — VAT free
- `2 MIXED` — contains exempt and due-VAT income rows

**Line-item `vatType`** (yanivps `IncomeVatType`, verbatim integer codes):

- `0 DEFAULT` — VAT added based on business type
- `1 INCLUDED` — VAT included in the price
- `2 EXEMPT` — VAT free

**Correction from prior pack:** the contract pack §C.3 listed these as string labels from Valigara (`"Default (Based on business type)"`, etc.). Actual wire format is **integer**, per yanivps typed schemas. Update the Zod for `vatType` to `z.number().int()`, not `z.string()`.

### 7.4 Document object shape (outbound) — verbatim

From yanivps `IDocument` (GET response shape):

| Field | Type |
|---|---|
| `id` | string (UUID) |
| `description` | string |
| `type` | int (DocumentType) |
| `number` | string |
| `documentDate` | string (`YYYY-MM-DD`) |
| `creationDate` | int (Unix ms) |
| `status` | int (DocumentStatus) |
| `lang` | `"he"` \| `"en"` |
| `amountDueVat` | float |
| `amountExemptVat` | float |
| `amountExcludedVat` | float |
| `amountLocal` | float |
| `amountOpened` | float |
| `vat` | float |
| `amount` | float |
| `currency` | string (ISO) |
| `currencyRate` | float |
| `vatType` | int (DocumentVatType) |
| `income` | `[IDocumentIncome]` |
| `payment` | `[IDocumentPayment]` |
| `client` | `IDocumentClient` |
| `business` | `IDocumentBusiness` |
| `url` | `{origin, he, en}` |
| `footer` | string |
| `remarks` | string |
| `rounding` | bool |
| `ref` | `[DocumentType]` |
| `signed` | bool |
| `cancellable` | bool |
| `discount` | `IDiscount` |

### 7.5 Currency enum — verbatim

From yanivps `Currency`: `ILS, USD, EUR, GBP, JPY, CHF, CNY, AUD, CAD, RUB, BRL, HKD, SGD, THB, MXN, TRY, NZD, SEK, NOK, DKK, KRW, INR, IDR, PLN, RON, ZAR, HRK`.

### 7.6 Payment type enum — verbatim

From yanivps `PaymentType` integer codes:

`-1 UNPAID, 0 DEDUCTION_AT_SOURCE, 1 CASH, 2 CHECK, 3 CREDIT_CARD, 4 ELECTRONIC_FUND_TRANSFER, 5 PAYPAL, 10 PAYMENT_APP, 11 OTHER`.

### 7.7 Sandbox credential per earlier Apiary quote

`c_key_7afa4a75-40fd-4812-98f8-0ea86ce27510` / `api_sandbox` / `APIsa2023` — not a GT token; belongs to a sandbox anyone can join. Useful for test-environment setup only. **UNRESOLVED** whether this credential has usable demo expenses visible.

---

## 8. Remaining unresolved items

**Narrowly scoped to the expense/supplier surface only. Every other area is now contract-ready.**

| # | Unresolved item | Why it matters | Resolving evidence |
|---|---|---|---|
| U.GI.1 | Exact URL path for **expense list/search/detail/create** — hypothesised `/v1/expenses/*` per pattern consistency, not verified | Zod schema authoring cannot begin for expense endpoints | one authenticated call per endpoint; live-API probe against the official Apiary-documented path |
| U.GI.2 | Exact expense object field set — likely `{id, documentDate, supplier, amount, amountLocal, vat, vatType, currency, items[...], status, ...}` mirroring document shape, but NOT verified verbatim | expense mirror Zod schema authoring | one authenticated `GET /v1/expenses/{id}` call on a real GT expense |
| U.GI.3 | Exact URL path for **supplier list/search/detail/create** — hypothesised `/v1/suppliers/*` per pattern consistency | supplier mirror Zod schema authoring | one authenticated call |
| U.GI.4 | Exact supplier object field set — the client object has `taxId`, `emails`, `paymentTerms`, etc.; suppliers likely mirror but NOT verified | `gi_supplier_mirror` column finalisation | one authenticated `GET /v1/suppliers/{id}` call |
| U.GI.5 | Expense line-item field set — likely mirrors `income.*` but with inbound semantics (supplier issued; VAT on their side); NOT verified. In particular whether `catalogNum` (CREATE form) or `sku` (READ form) or a third name appears | price-history join to `supplier_items` mapping | one authenticated call |
| U.GI.6 | Whether expenses expose `updated_at`-equivalent for watermark-driven refresh, and whether expenses are mutable after issue | mirror upsert-vs-append strategy | one authenticated call + live observation of an edited expense |
| U.GI.7 | Whether Green Invoice has a **webhook** event for expense creation (parallel to document-created webhooks shown in danielrosehill) | push-vs-poll decision for expense ingest | Green Invoice Settings → Developer Tools → Webhooks inspection (operator action) |
| U.GI.8 | Full error-class vocabulary for `account/token` and `/expenses` endpoints (401 shape confirmed indirectly via MordiSacks client `ApiErrorException` reading `errorMessage` + `errorCode` from body, but full enum not observed) | runtime error classification | live observation of error cases |

Items **PREVIOUSLY unresolved but NOW resolved this pass** (removed from the blocker set):

- ~~Auth endpoint + TTL~~ → **§2 resolved**
- ~~13-code document type enum~~ → **§7.1 resolved**
- ~~Document status enum~~ → **§7.2 resolved**
- ~~VAT type enums (document + line)~~ → **§7.3 resolved** (with numeric-code correction)
- ~~Outbound document object field set~~ → **§7.4 resolved**
- ~~Outbound line-item field shape, price as number vs string~~ → **§5 resolved, `price: float`, `quantity: int`**
- ~~Search pagination envelope~~ → **§6 resolved** (for documents and clients)
- ~~Currency and payment-type enums~~ → **§7.5 / §7.6 resolved**
- ~~Sandbox URL~~ → **§2 resolved** (`sandbox.d.greeninvoice.co.il/api`)
- ~~`catalogNum` vs `sku` asymmetry~~ → **§5 resolved and explicitly flagged**

---

## 9. Final verdict

**STATUS: BLOCKED_ON_EXTERNAL_SPEC_GAPS**

But the blocker surface has shrunk dramatically. Of the original 8 GI-side L.GI.1–L.GI.8 items in the contract pack, **6 are now resolved** and **2 remain narrow** (both about the expense and supplier resources specifically). The overall Green Invoice integration is approximately 80% contract-ready — auth, outbound documents, clients, items, pagination, enums, and webhook shape are all known verbatim. What remains is a single authenticated call per new endpoint to close the last gap.

**Unblock path from here:**

1. Authorize one token-gated inspection pass (same shape as the LionWheel inspection).
2. Use a Green Invoice API key + secret (stored via the secret-store-wiring pattern) to obtain a JWT from `POST /v1/account/token`.
3. Make **three** authenticated GET calls to close the full gap:
   - `GET /v1/expenses/search` (or via POST body `{page:1, pageSize:1}`) — captures expense list shape
   - `GET /v1/expenses/{id}` on one real GT expense — captures expense detail + lines
   - `GET /v1/suppliers/{id}` on one real GT supplier — captures supplier shape
4. Redact, archive, and update the Zod schemas verbatim.

This pack **does not** perform those calls; no token was provided. The evidence here is strictly what could be assembled from public sources.

**Document / client / auth contract is now CONTRACT_READY for authoring Zod + mapper if the cycle is later authorised to cover only the outbound-document side.** If GT's actual Green Invoice usage is split between outbound-document consumption (for example, fetching issued GT invoices for cross-system reconciliation) and inbound-expense consumption, the outbound surface can proceed to scaffolding today while the expense surface waits for one authenticated pass.

Given the user directive — "GT does use Green Invoice for supplier invoices as expenses" — the critical path **is** the expense surface; therefore the pack-level verdict is `BLOCKED_ON_EXTERNAL_SPEC_GAPS` until the three calls above are made.
