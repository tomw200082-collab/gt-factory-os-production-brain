# Frozen Operator Form Field Definitions — v1

> **Status:** FROZEN for Window 1 implementation of ticket 0012.
> **Date frozen:** 2026-04-16
> **Last sync with W1 runtime contract:** 2026-04-16 — added `item_type` per GR line; revised AMB-2 unit rule per W1 override.
> **Source artifacts:**
> - `window2-portal-spec.md` §5.1 (lines 263-330), §5.2 (lines 333-397), §5.3 (lines 400-486)
> - `window2-frontend-package.md` §6 (lines 294-316)
> - `CLAUDE.md` (foundation constraints)
> - **`docs/window1_to_window2_gr_handoff.md` — W1 runtime contract, operative for GR submit wiring**
> - **`api/src/goods-receipts/schemas.ts` — authoritative Zod for GR request/response**
>
> **Scope:** Field-level truth for 3 operator forms: Goods Receipt, Waste/Adjustment, Physical Count.
> This artifact defines what data each form collects and validates. It does NOT define UI layout, screen states, API routes, or DB triggers.
>
> **Precedence rule:** where this artifact disagrees with the W1 runtime contract or the Zod schema, **the W1 runtime contract wins for the submit-wiring phase.** Mismatches must be reconciled back into this artifact, not silently patched in code.

---

## 1. Shared Envelope Fields

Every operator form submission carries these fields. They are not form-specific.

| Field              | Required | Type         | Source        | Notes                                                                 |
|--------------------|----------|--------------|---------------|-----------------------------------------------------------------------|
| `idempotency_key`  | yes      | string (UUID)| system-derived| Client-generated, stable across retries. Server deduplicates.         |
| `event_at`         | yes      | datetime     | operator      | Defaults to now. Physical time is authoritative for balance math (CLAUDE.md §Ledger). May be backdated — see validation V-ENV-1. |
| `submitted_by`     | yes      | user FK      | system-derived| From auth context. Not operator-entered.                              |
| `notes`            | no       | text         | operator      | Free-form header-level note. Nullable.                                |
| ~~`attachments[]`~~| —        | —            | —             | **v1-DEFER (AMB-1).** Removed from v1 scope. Re-evaluate in v1.1. |

---

## 2. Goods Receipt (S-04) — Per-Form Fields

### 2A. Header Fields

| Field          | Required | Type                    | Source   | Notes                                                                |
|----------------|----------|-------------------------|----------|----------------------------------------------------------------------|
| `supplier_id`  | yes      | FK → suppliers          | operator | Always a picker from read model. Never free-text.                    |
| `po_id`        | no       | FK → purchase_orders    | operator | Picker filtered by `supplier_id`. Null = unlinked receipt.           |

### 2B. Line Fields (repeating group, min 1 line)

| Field          | Required | Type                       | Source   | Notes                                                                |
|----------------|----------|----------------------------|----------|----------------------------------------------------------------------|
| `item_type`    | yes      | enum: `FG`, `RM`, `PKG`    | operator | Determines which table `item_id` resolves against. `FG` → `items`; `RM`/`PKG` → `components`. Server returns 409 `ITEM_TYPE_MISMATCH` if the `item_id` does not belong to the declared type. Added per W1 runtime contract 2026-04-16. |
| `item_id`      | yes      | FK → items OR components   | operator | Resolution table depends on `item_type`. Client does NOT validate type-vs-id — server authoritative. |
| `quantity`     | yes      | numeric > 0                | operator | Zero is a validation error, not "no receipt". Precision: `numeric(24,8)`. Server returns this as a STRING in responses — client must not coerce to JS number. |
| `unit`         | yes      | string, must exist in `uom`| operator | Defaults from item master for UX (still the right default). **Not locked** to `items.default_uom` — W1 accepts any unit that exists in the `uom` table. Server returns 409 `UNIT_NOT_FOUND` if unknown. Supersedes AMB-2 adopt-default. |
| `po_line_id`   | no       | FK → po_lines              | operator | Only when `po_id` is set. Lines not matching a PO line are "extra lines" — see V-GR-3. |
| `notes`        | no       | text                       | operator | Per-line note. Nullable.                                             |

---

## 3. Waste / Adjustment (S-05) — Per-Form Fields

Single-item form. No line repeater in v1.

| Field          | Required    | Type                    | Source   | Notes                                                                |
|----------------|-------------|-------------------------|----------|----------------------------------------------------------------------|
| `direction`    | yes         | enum: `loss`, `positive`| operator | Default: `loss`. `positive` triggers confirm modal + stricter rules. |
| `item_id`      | yes         | FK → items              | operator | Picker. Items filtered to adjustable kind.                           |
| `quantity`     | yes         | numeric > 0             | operator | Always positive. Sign comes from `direction`. Zero and negative blocked. |
| `unit`         | yes         | enum from item master   | operator | Defaults from `items.default_uom`.                                   |
| `reason_code`  | yes         | enum                    | operator | **UNRESOLVED** — canonical list not defined. See AMB-3.              |
| `notes`        | conditional | text                    | operator | **Required** when `direction = positive` OR `reason_code = other`. Nullable otherwise. |

---

## 4. Physical Count (S-06) — Per-Form Fields

Single-item form. No session variant in v1 (AMB-6: v1-DEFER).

| Field              | Required | Type                  | Source   | Notes                                                                |
|--------------------|----------|-----------------------|----------|----------------------------------------------------------------------|
| `item_id`          | yes      | FK → items            | operator | Picker or barcode entry. Items filtered to countable kind.           |
| `counted_quantity` | yes      | numeric >= 0          | operator | Zero is valid ("nothing on hand"). Negative blocked. Decimals allowed where item unit supports it; integer-only otherwise. |
| `unit`             | yes      | enum from item master | operator | Defaults from `items.default_uom`.                                   |
| ~~`location_id`~~  | —        | —                     | —        | **v1-DEFER (AMB-4).** Dropped. No location/bin tracking in v1 per CLAUDE.md. |
| ~~`session_id`~~   | —        | —                     | —        | **v1-DEFER (AMB-6).** Dropped. No count sessions in v1. Single-count posting only. |

**Blind-count invariant:** system quantity is NEVER shown to the operator before `counted_quantity` is entered and submit is attempted. This is a hard UX and API contract — the read model must not expose system qty to the count form pre-submit.

---

## 5. Validation Rules

### Shared Envelope Validations

| ID      | Rule                                                                                     | Severity     | Resolution          |
|---------|------------------------------------------------------------------------------------------|--------------|---------------------|
| V-ENV-1 | `event_at` backdated beyond N days → inline warning.                                    | warning      | **UNRESOLVED**: backdate threshold source (`planning_policy`?) and value not defined. See AMB-5. |
| V-ENV-2 | `idempotency_key` must be present and non-empty.                                        | hard block   | Resolved.           |
| V-ENV-3 | `event_at` must not be in the future (beyond a small clock-skew tolerance).             | hard block   | Resolved. Tolerance TBD but non-controversial. |

### Goods Receipt Validations

| ID      | Rule                                                                                     | Severity     | Resolution          |
|---------|------------------------------------------------------------------------------------------|--------------|---------------------|
| V-GR-1  | At least 1 line required.                                                                | hard block   | Resolved.           |
| V-GR-2  | Each line `quantity > 0`.                                                                | hard block   | Resolved.           |
| V-GR-3  | When `po_id` is set, lines not matching any PO line are "extra lines" → single confirm dialog. | confirm      | Resolved (client). Server enforcement TBD. |
| V-GR-4  | Over-receipt: line qty > remaining on matching PO line → inline warning + required confirm. Not a hard block. | confirm      | Resolved (client). |
| V-GR-5  | `supplier_id` is required. Must be picker, never free-text.                              | hard block   | Resolved.           |
| V-GR-6  | Unit must exist in `uom` table. Default from item master for UX; any valid uom accepted.  | server-enforced | **RESOLVED (AMB-2 superseded by W1 runtime contract 2026-04-16).** Server returns 409 `UNIT_NOT_FOUND` if unknown. |

### Waste / Adjustment Validations

| ID      | Rule                                                                                     | Severity     | Resolution          |
|---------|------------------------------------------------------------------------------------------|--------------|---------------------|
| V-WA-1  | `quantity > 0`. Zero blocked. Negative input blocked (sign from `direction`).            | hard block   | Resolved.           |
| V-WA-2  | `reason_code` must be selected before submit enables.                                    | hard block   | Resolved (pending AMB-3 for the enum). |
| V-WA-3  | `notes` required when `direction = positive` OR `reason_code = other`.                   | hard block   | Resolved.           |
| V-WA-4  | `direction = positive` → confirm modal at submit: "Yes, I am adding stock".              | confirm      | Resolved.           |
| V-WA-5  | Quantity exceeds policy threshold → held for planner approval (server decides).           | approval     | **UNRESOLVED**: threshold source, shape, per-item vs per-reason. See AMB-7. |
| V-WA-6  | Whether `positive` has a stricter approval rule than `loss` at same quantity.             | approval     | **UNRESOLVED**: See AMB-8. |

### Physical Count Validations

| ID      | Rule                                                                                     | Severity     | Resolution          |
|---------|------------------------------------------------------------------------------------------|--------------|---------------------|
| V-PC-1  | `counted_quantity >= 0`. Negative blocked.                                               | hard block   | Resolved.           |
| V-PC-2  | Zero counts require NO special confirmation. Zero is common and must not feel exceptional.| —            | Resolved (explicitly). |
| V-PC-3  | Decimals allowed only where item unit supports it; integer-only otherwise.               | hard block   | Resolved.           |
| V-PC-4  | System quantity never exposed pre-submit (blind count invariant).                        | hard invariant| Resolved.           |
| V-PC-5  | Variance handling is entirely server-driven. Client does not compute variance.           | contract     | Resolved.           |

---

## 6. Enums

| Enum               | Values                                  | Status       | Notes                                                  |
|--------------------|-----------------------------------------|--------------|--------------------------------------------------------|
| `direction`        | `loss`, `positive`                      | **FROZEN**   | Used by Waste/Adjustment. Default: `loss`.             |
| `reason_code`      | TBD                                     | **UNRESOLVED**| See AMB-3. Window 1 must define canonical list.       |
| `unit`             | per item master (`items.default_uom`, `items.allowed_units`) | **RESOLVED** | Not a global enum; item-scoped.            |
| `item_kind_filter` | `receivable`, `adjustable`, `countable` | **PROPOSAL** | Used in read model queries. May map to item.kind + item.active. Window 1 decides if these are real DB enums or query logic. |

---

## 7. Field Origin Classification

Every field is classified as exactly one of:

- **operator-entered**: operator provides the value via the form
- **system-derived**: system computes or injects the value (not editable by operator)
- **system-defaulted**: system provides a default, operator may override

| Field              | Form(s)         | Origin            |
|--------------------|-----------------|-------------------|
| `idempotency_key`  | all             | system-derived    |
| `event_at`         | all             | system-defaulted  |
| `submitted_by`     | all             | system-derived    |
| `notes`            | all             | operator-entered  |
| ~~`attachments[]`~~| ~~all~~         | ~~operator-entered~~ | *v1-DEFER (AMB-1)* |
| `supplier_id`      | GR              | operator-entered  |
| `po_id`            | GR              | operator-entered  |
| `item_type`        | GR lines        | operator-entered  |
| `item_id`          | GR lines, WA, PC| operator-entered  |
| `quantity`         | GR lines, WA    | operator-entered  |
| `counted_quantity` | PC              | operator-entered  |
| `unit`             | GR lines, WA, PC| operator-entered, defaulted from item master (GR: any valid uom accepted per W1) |
| `po_line_id`       | GR lines        | operator-entered  |
| `line.notes`       | GR lines        | operator-entered  |
| `direction`        | WA              | system-defaulted  |
| `reason_code`      | WA              | operator-entered  |
| ~~`location_id`~~  | ~~PC~~          | —                 | *v1-DEFER (AMB-4)* |
| ~~`session_id`~~   | ~~PC~~          | —                 | *v1-DEFER (AMB-6)* |

---

## 8. Ambiguities, Contradictions, and Unresolved Items

Every item below is classified into one of four statuses:
- **BLOCKING** — must be resolved by Window 1 before 0012 or form implementation can proceed. No defaults may be assumed.
- **v1-ADOPT-DEFAULT** — a safe default exists; Window 1 may adopt the stated recommendation without further discussion unless they disagree.
- **v1-DEFER** — drop from v1 scope entirely. Re-evaluate in v1.1.
- **STILL-BLOCKING** — no safe default, no clear defer path. Requires explicit decision.

### BLOCKING (must resolve before 0012)

| ID    | Form | Issue                                                                                                                                   | Impact                                      | Recommendation                                    |
|-------|------|-----------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------|----------------------------------------------------|
| AMB-3 | WA   | `reason_code` canonical list is undefined. The portal spec says "TODO-WINDOW1: canonical reason code list." Mock uses placeholder. | **Blocks entire WA form.** Cannot build the enum, the picker, or the conditional-notes rule for `other`. | Window 1 must define the list. Recommend: `breakage`, `spillage`, `expired`, `found`, `correction`, `other`. Minimum viable. |
| AMB-7 | WA   | Approval threshold — source (`planning_policy`?), shape (per-item? per-reason? global?), and whether the client can know the threshold pre-submit. | **Blocks WA approval routing.** Cannot implement threshold-based approval without this. | Window 1 must define. Recommend: `planning_policy` key per `(item_id, reason_code)` with global fallback. Client should NOT pre-compute; server decides. |
| AMB-8 | WA   | Whether `direction = positive` has a stricter approval rule than `loss` at the same quantity. Portal spec asks but does not answer. | **Blocks WA approval routing.** Coupled to AMB-7. | Window 1 must decide. CLAUDE.md says "Positive 'found stock' adjustments require stronger control" — but Window 2 will not collapse this into a default. |
| AMB-9 | PC   | Does a count post as an **anchor** (replaces projection) or as an **adjustment** ledger row (reconciles to system qty)? Portal spec explicitly refuses to decide. | **Blocks PC ledger write path.** Fundamental architectural decision. | Window 1 must decide. CLAUDE.md says counts "may create a new anchor" after approval. Recommend: approved counts create anchors; auto-posted small variances create adjustment ledger rows. But this is a ledger-semantics decision, not a field-definition default. |

### v1-ADOPT-DEFAULT (safe default exists)

| ID     | Form | Issue                                                                                                                                   | Default adopted                                | Rationale                                         |
|--------|------|-----------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------|----------------------------------------------------|
| AMB-2  | GR   | Multi-unit receipt: unit override behavior.                                                | **SUPERSEDED by W1 runtime contract 2026-04-16.** Any unit present in the `uom` table is accepted; server returns 409 `UNIT_NOT_FOUND` otherwise. Client still defaults from item master for UX but does not block non-default units. | W1 chose server-side uom-table validation over per-item allowed_units. Simpler schema, no `items.allowed_units` needed. |
| AMB-5  | all  | Backdate threshold for `event_at` warning — source, value, and scope undefined. | **Global `planning_policy` key `backdate_warning_days`, default 7.** | Non-controversial. Warning only (not a hard block). Any reasonable value works; 7 days is operationally safe. |
| AMB-10 | GR   | Under what conditions does a receipt require approval? Over-receipt? Backdate beyond threshold? Extra line? | **No approval routing for GR in v1.** All receipts auto-post. | Simplest path. CLAUDE.md does not mandate GR approval. Receipts are the most routine operator action — adding approval friction without a confirmed need creates operator friction for no gain. Add in v1.1 if needed. |

### v1-DEFER (drop from v1 scope)

| ID     | Form | Issue                                                                                                                                   | Deferral rationale                             |
|--------|------|-----------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------|
| AMB-1  | all  | `attachments[]` — storage target, upload envelope, and mutation integration all undefined. | No confirmed operator need for attachments in v1. Storage infra decision is orthogonal to form field truth. Defer to v1.1. **Remove `attachments[]` from v1 mutation envelopes.** |
| AMB-4  | PC   | `location_id` — locations not modeled in v1.                                                | CLAUDE.md explicitly says no bin/location tracking in v1. **Drop `location_id` field entirely.** |
| AMB-6  | PC   | `count_session` server-side model — sessions vs independent posting.                        | CLAUDE.md says "do not overbuild cycle counting in v1." Single-count posting is sufficient. **Drop `session_id` field. No session model in v1.** |

---

## 9. Mutation Envelope Shapes (Reference)

These are the proposed v1 mutation envelopes, updated to reflect AMB deferrals and adopt-defaults. Window 1 owns the final API shape.

### Goods Receipt
```json
{
  "idempotency_key": "string (1..255)",
  "event_at": "ISO8601 (not future)",
  "supplier_id": "string",
  "po_id": "string | null",
  "lines": [
    {
      "item_type": "FG | RM | PKG",
      "item_id": "string",
      "quantity": "number > 0",
      "unit": "string (must exist in uom table)",
      "po_line_id": "string | null",
      "notes": "string | null"
    }
  ],
  "notes": "string | null"
}
```
> Synced with W1 runtime contract 2026-04-16. `attachments` removed (AMB-1 v1-DEFER). `item_type` added per-line (required). `unit` validated against `uom` table, not locked to `items.default_uom` (supersedes AMB-2). Authoritative Zod: `api/src/goods-receipts/schemas.ts`.
>
> **Response note:** server returns `quantity` as a STRING to preserve `numeric(24,8)` precision. Client must not coerce to JS number.

### Waste / Adjustment
```json
{
  "idempotency_key": "string",
  "event_at": "ISO8601",
  "direction": "loss | positive",
  "item_id": "string",
  "quantity": "number",
  "unit": "string",
  "reason_code": "string",
  "notes": "string | null"
}
```
> `attachments` removed (AMB-1 v1-DEFER). `reason_code` values are BLOCKING (AMB-3).

### Physical Count
```json
{
  "idempotency_key": "string",
  "event_at": "ISO8601",
  "item_id": "string",
  "counted_quantity": "number",
  "unit": "string",
  "notes": "string | null"
}
```
> `location_id` and `session_id` removed (AMB-4, AMB-6 v1-DEFER).

---

## 10. Server Response States (Reference)

All three forms expect these response patterns from the server. Window 1 owns exact shapes.

| Code | Meaning                   | Forms     | Notes                                                    |
|------|---------------------------|-----------|----------------------------------------------------------|
| 201  | Committed                 | GR, WA    | Ledger row posted. Response includes read-model projection. |
| 201  | Committed, no variance    | PC        | Count matches system.                                    |
| 201  | Committed, auto-adjusted  | PC        | Small variance auto-posted. Response includes variance breakdown. |
| 202  | Pending approval          | GR, WA, PC| Not yet posted to ledger. Visible in approval queue.     |
| 409  | Conflict                  | all       | State changed between form open and submit (PO closed, item deactivated, session closed). |
| 422  | Validation error          | all       | Server-side validation beyond client rules.              |

---

*End of frozen artifact.*
