# Window 2 — Portal Frontend Specification (Skeleton Only)

_Last updated: 2026-04-14_
_Owner: Window 2 (Portal, Forms, Auth, Roles, Approval Flows)_
_Status: Specification and shell architecture only — no connected UI, no backend-final assumptions._

This document defines the portal at the contract and skeleton level. It is not an implementation plan. It is the surface Window 5 will reconcile against Window 1 (schema) and Window 3/4 (planning, jobs, integrations). Everywhere I would otherwise have to invent a backend fact, I leave an explicit `TODO-WINDOW1` or `TODO-WINDOW5` marker rather than guessing.

---

## 0. Scope and non-goals

### In scope
- Portal module layout and shell architecture (Next.js app-router conventions — proposed, not locked).
- Role-based route map.
- Screen inventory with strict classification.
- Per-screen field lists, validation UX rules, and state catalogs.
- Proposed API contract per screen (read models + mutation intents + idempotency expectations).
- Cross-cutting concerns: outbox envelope, idempotency model, approval UX surface.

### Out of scope (deliberately)
- Visual design, component library selection, styling system.
- Any connected implementation or network code.
- Backend contract finalization (proposals only; Window 1 owns final shapes).
- Invented stock-mutation semantics (ledger posting, anchor vs adjustment, approval thresholds). These are surfaced as explicit open questions.
- Production Actual workflow implementation (inventoried for completeness; not in Window 2's immediate build scope per brief).

### Explicit constraints honored
- Forms submit into **API contracts**, not into DB tables.
- Browser **never** reads core tables directly; all reads go through defined read models.
- **Form vs Planning Screen** is a strict classification, not a UX style choice.
- Stock-affecting workflows define **inputs only**; write path, ledger semantics, and approval triggers are deferred to Window 1.
- Positive stock adjustments must feel exceptional, not routine.
- Physical Count is blind by default.

---

## 1. Portal module map

### 1.1 Monorepo assumption — PROPOSAL

I do not lock a monorepo shape unilaterally. Window 5 should confirm. My working assumption for this spec is:

```
apps/
  portal/                     Next.js (app router) — the portal itself
packages/
  shared-contracts/           TypeScript types for API envelopes (read models + mutations)
  shared-ui/                  primitive UI components (optional; may be folded into portal)
```

`shared-contracts/` is the boundary Window 1 and Window 2 both write against. Types live there; nothing else crosses.

**TODO-WINDOW5**: confirm layout, workspace tool (pnpm/turbo/npm workspaces), shared package naming, whether `shared-ui` exists or collapses into `portal`.

### 1.2 Top-level route groups (Next.js app router)

```
apps/portal/src/app/
  (auth)/
    login/
    callback/
  (shared)/                   visible to all authenticated roles
    dashboard/
    profile/
  (operator)/
    home/
    goods-receipt/
    waste-adjustment/
    physical-count/
    my-submissions/           outbox visibility + history
  (planner)/
    forecast/
    recommendations/
      purchasing/
      production/
    exceptions/
    approvals/
  (admin)/
    master-data/
      items/
      components/
      boms/
      suppliers/
      planning-policy/
    users/
    jobs/
    integrations/
```

Route groups (`(auth)`, `(operator)`, …) are Next.js app-router parentheses groups — they affect layout composition and route guards but not URL shape. Actual URLs follow the inner segments.

### 1.3 Shared modules inside the portal

```
apps/portal/src/
  lib/
    auth/                     session bootstrap, role claim decoding, guard helpers
    api/                      typed client stubs against shared-contracts (no fetch logic yet)
    outbox/                   local persistence + replay for failed form submits
    form/                     validation helpers, field primitives, error mapping
    idempotency/              client key generation + persistence per logical submit
  components/
    layout/                   shell chrome, top bar, queued-submissions indicator
    form-fields/              input primitives used by forms and planning screens
    data-display/             tables, grids, status pills, empty states
    feedback/                 toasts, banners, modal confirms (for exceptional actions)
  features/
    goods-receipt/
    waste-adjustment/
    physical-count/
    production-actual/        (scoped out for Window 2 build, but slice reserved)
    forecast/
    recommendations/
    exceptions/
    approvals/
    master-data/
    jobs-monitor/
```

Feature slices own their page components, local state, and feature-specific form schemas. Cross-feature primitives live in `lib/` or `components/`.

### 1.4 Shell architecture

One root layout. Three nested layouts keyed to route groups:

- `(auth)` — no chrome. Redirects to `/dashboard` on successful session.
- `(shared|operator|planner|admin)` — shared authenticated chrome: top bar, role-aware nav, outbox indicator, profile menu. Nav contents vary per role but layout is one component.
- A single `RoleGate` wrapper per route group enforces minimum role. See §2.3.

The shell deliberately does **not** render global modals, dialogs, or side panels at the root. Feature slices own their own overlays to keep the shell boring.

---

## 2. Role-based route map

### 2.1 Roles (from foundation brief)
- `operator` — submits operational forms
- `planner` — reviews recommendations, edits forecast, handles exceptions
- `admin` — manages master data, users, jobs, integrations
- `viewer` — dashboard-only

Roles are **not** hierarchical. An admin is not automatically a planner. Route access is checked explicitly against each role.

**TODO-WINDOW5**: confirm whether roles are hierarchical or disjoint. This spec assumes disjoint with per-route allow-lists.

### 2.2 Route × role access matrix

`R` = can view, `W` = can mutate, `—` = no access.

| Route                                         | operator | planner | admin | viewer |
|-----------------------------------------------|----------|---------|-------|--------|
| `/login`, `/callback`                         | R        | R       | R     | R      |
| `/dashboard`                                  | R        | R       | R     | R      |
| `/profile`                                    | R        | R       | R     | R      |
| `/home` (operator landing)                    | R        | —       | —     | —      |
| `/goods-receipt`                              | W        | —       | —     | —      |
| `/waste-adjustment`                           | W        | —       | —     | —      |
| `/physical-count`                             | W        | —       | —     | —      |
| `/my-submissions`                             | R        | —       | —     | —      |
| `/forecast`                                   | —        | W       | R     | R      |
| `/recommendations/purchasing`                 | —        | W       | R     | R      |
| `/recommendations/production`                 | —        | W       | R     | R      |
| `/exceptions`                                 | —        | W       | R     | —      |
| `/approvals`                                  | —        | W       | R     | —      |
| `/master-data/*`                              | —        | R       | W     | —      |
| `/users`                                      | —        | —       | W     | —      |
| `/jobs`                                       | —        | R       | W     | —      |
| `/integrations`                               | —        | —       | W     | —      |

Notes:
- Viewers see dashboard + read-only planning surfaces but no inboxes or master data.
- Planners can read master data for context but cannot mutate it.
- Admins can see planning outputs but are not in the planner workflow path by default.

**TODO-WINDOW5**: confirm whether admins should also have planner write access, or whether the matrix above is final.

### 2.3 Role gating mechanism — PROPOSAL

Gating lives in two places:

1. **Route-group layout wrapper** (`RoleGate`) — server component that decodes session role claim, compares to declared allow-list for the route group, and returns 404 on mismatch (never 403 — we do not confirm route existence to wrong roles).
2. **Link/button suppression** — role-aware nav and action buttons never render for roles that lack access. Redundant with server gate, but removes dead affordances from the UI.

There is no client-side-only gating. Client checks are UX, not security.

**TODO-WINDOW1**: session shape. Where does the role claim live (JWT custom claim? `user_metadata`?)? How is it read server-side in Next.js? This affects `lib/auth/` entirely.

---

## 3. Screen inventory by workflow

| ID    | Screen                             | Workflow                    | Classification            | Phase  |
|-------|------------------------------------|-----------------------------|---------------------------|--------|
| S-01  | Login                              | Auth                        | Form (auth)               | v1     |
| S-02  | Dashboard                          | Read-only                   | Read-only Dashboard       | v1     |
| S-03  | Operator Home                      | Operator landing            | Read-only Dashboard       | v1     |
| S-04  | Goods Receipt                      | Receiving                   | **Form**                  | v1     |
| S-05  | Waste / Adjustment                 | Stock correction            | **Form**                  | v1     |
| S-06  | Physical Count                     | Count posting (blind)       | **Form**                  | v1     |
| S-07  | Production Actual                  | Production reporting        | **Form**                  | v1.1   |
| S-08  | My Submissions / Outbox            | Operator self-service       | Read-only Inbox           | v1     |
| S-09  | Forecast Workspace                 | Forecast editing            | **Planning Screen**       | v1     |
| S-10  | Purchase Recommendations Review    | Purchasing judgment         | **Planning Screen**       | v1     |
| S-11  | Production Recommendations Review  | Production judgment         | **Planning Screen**       | v1.1   |
| S-12  | PO Form                            | PO creation from approved rec| Form (downstream of S-10) | v1     |
| S-13  | Exceptions Inbox                   | Exception triage            | Read-only Inbox + actions | v1     |
| S-14  | Approvals Inbox                    | Pending-approval triage     | Read-only Inbox + actions | v1     |
| S-15  | Jobs Monitor                       | Scheduled-job health        | Read-only Dashboard       | v1     |
| S-16  | Items Admin                        | FG/component master         | Admin CRUD                | v1     |
| S-17  | Components Admin                   | Component master            | Admin CRUD                | v1     |
| S-18  | BOMs Admin                         | BOM editing                 | Admin CRUD (nested)       | v1     |
| S-19  | Suppliers Admin                    | Supplier + mapping          | Admin CRUD                | v1     |
| S-20  | Planning Policy Admin              | Policy thresholds & params  | Admin CRUD                | v1     |
| S-21  | Users Admin                        | Role assignment             | Admin CRUD                | v1     |
| S-22  | Integrations Admin                 | LionWheel / Shopify / GI config | Admin CRUD (partial)  | v1.1   |

"Phase v1.1" = not in Window 2's first implementation sweep; slice reserved but not specified in full below.

---

## 4. Screen classification — strict definitions

These distinctions are load-bearing. Blurring them reintroduces workbook-style multi-purpose screens.

### Form
- Represents **one discrete real-world event** the operator is reporting (a receipt happened; a count happened; a production run finished).
- Has **one submit intent** producing **one mutation envelope**.
- Must be fast to complete — sub-60-seconds for common path.
- Must integrate with the outbox (submission may fail offline; operator must not lose work).
- Must carry a client idempotency key.
- May require server-side approval before the event becomes a committed ledger posting — but from the operator's perspective, the form was submitted.
- **No draft persistence in v1.** A form is filled in and submitted; it is not a workspace.

### Planning Screen
- Represents **judgment work over a versioned dataset** (forecast edits, recommendation reviews).
- Has **persistent draft state** on the server (versioning, not local drafting).
- Edits are **multi-cell / multi-row**, not a single submit intent.
- Has a distinct **commit / publish** action separate from editing.
- May have optimistic concurrency and stale-version detection.
- Never touches the ledger directly. Outputs flow through other systems (planning engine, PO creation).

### Admin CRUD
- Master data maintenance. Standard list → detail → edit pattern.
- Low frequency. No outbox. No approval chain by default.
- Optimistic concurrency via row version / etag.
- Never stock-affecting.

### Read-only Dashboard / Inbox
- Consumes read models only.
- **May** surface actions (resolve exception, approve recommendation), but those actions are distinct mutation envelopes — the screen itself is not a form.
- Never writes master data, never posts to the ledger directly.

### Why this matters
Goods Receipt is a Form even though it has many line items, because it reports one physical event. Forecast is a Planning Screen even though each cell edit looks form-like, because there is no single "the forecast happened" moment. The classification drives outbox behavior, state management, persistence strategy, and approval UX — not visual style.

---

## 5. Per-screen specifications

Each screen below specifies: purpose, classification, field list, validation UX rules, state catalog, and API contract draft. Stock-affecting screens (S-04, S-05, S-06, S-07) describe **inputs and client-side validation only**; the write path, ledger posting shape, and approval triggers are explicit open questions for Window 1.

### 5.1 S-04 Goods Receipt — **Form**

**Purpose:** operator reports that physical goods arrived. Supports linking to an open PO or recording an unlinked receipt. Partial receipts are valid (foundation §10).

**Fields:**

| Field              | Required | Type                             | Notes                                                                 |
|--------------------|----------|----------------------------------|-----------------------------------------------------------------------|
| `event_at`         | yes      | datetime (date + time)           | Defaults to now. Physical time authoritative (foundation §3C).        |
| `supplier_id`      | yes      | picker → read model              | Required even if no PO linked.                                        |
| `po_id`            | no       | picker → open-PO read model      | Filtered by supplier once supplier chosen.                            |
| `lines[]`          | yes, ≥1  | repeating group                  | Each line: `item_id`, `quantity`, `unit`, optional `po_line_id`, optional `notes`. |
| `notes`            | no       | text                             | Free-form header-level note.                                          |
| `attachments[]`    | no       | file refs                        | **TODO-WINDOW1**: storage target, upload envelope.                    |

**Validation UX rules:**
- `quantity > 0` per line; zero is not a "no receipt" — it's a validation error.
- Unit defaults from item master; operator may override only if item allows multi-unit receipts. **TODO-WINDOW1**: is multi-unit receipt allowed?
- When `po_id` is set, each line must match a line on the PO or be explicitly flagged as "extra line". Extra lines prompt a single confirm dialog — not silent.
- Partial receipts: if `sum(line.quantity) < sum(po_line.ordered_quantity)`, no warning. This is normal.
- Over-receipts: if any line quantity > remaining on matching PO line, inline warning + required confirm, not hard block (real receipts sometimes exceed order).
- `event_at` may be backdated up to N days; beyond that, inline warning. **TODO-WINDOW1**: backdate threshold from policy.
- Supplier and PO cannot both be free-text — always pickers from read models.

**Screen states:**
- **empty** — fresh form; one empty line row rendered.
- **loading** — masters (supplier list, open POs, items) still fetching; inputs disabled with skeleton.
- **validation error** — inline per-field errors; top-of-form summary listing each invalid line by row number; first error scrolled into view; submit button disabled.
- **submission pending** — form locked; submit button in loading state; after ~2s, a "submitting…" banner appears; if network fails, transitions to queued-in-outbox state without data loss.
- **success** — compact confirmation card: receipt id, supplier, total lines, total quantity, linked PO state ("PO-1234 now 60% received"). Primary action: "Record another receipt". Secondary: "View submission".
- **approval required** — shown if server returns "pending approval" envelope. Banner: "This receipt is held for review because <reason>." Submission is visible in `/my-submissions` with `pending_approval` state. **TODO-WINDOW1**: under what conditions does a receipt require approval? Over-receipt? Backdate beyond threshold? Extra line?
- **stale / conflict** — e.g. PO closed between form open and submit. Banner explains the conflict, offers "Refresh PO state" (re-fetches read model, attempts to keep line inputs) or "Submit as unlinked receipt".

**API contract draft (PROPOSAL):**

Read models needed:
- `GET /read/suppliers?q=…` → `{ id, name, active }[]`
- `GET /read/open-purchase-orders?supplier_id=…` → `{ id, supplier_id, po_number, status, lines: [{ id, item_id, item_name, ordered_qty, received_qty, remaining_qty, unit }] }[]`
- `GET /read/items?q=…&kind=receivable` → `{ id, sku, name, default_unit, allowed_units }[]`

Mutation intent:
- `POST /mutations/goods-receipts`
- Request envelope (Window 2 proposal):
  ```
  {
    idempotency_key: string,       // client-generated, stable across retries
    event_at: ISO8601,
    supplier_id: string,
    po_id: string | null,
    lines: [
      { item_id, quantity, unit, po_line_id: string | null, notes?: string }
    ],
    notes?: string,
    attachments?: [{ storage_ref: string }]
  }
  ```
- Response states (expected, not invented):
  - `201 committed` → receipt posted; ledger effect flagged server-side; response includes read-model projection for success card.
  - `202 pending_approval` → receipt recorded but not yet posted to ledger.
  - `409 conflict` → PO state changed; response includes conflict reason code.
  - `422 validation` → server-side validation beyond client rules.
- **Idempotency:** client key required. Server must dedup retries with same key.

**TODO-WINDOW1**:
- Does "committed" mean ledger row exists, or is it a two-phase post?
- Exact conflict reason codes.
- Whether attachments are part of the mutation envelope or a separate upload-first step.

---

### 5.2 S-05 Waste / Adjustment — **Form**

**Purpose:** operator reports a stock correction: loss, breakage, found inventory, or administrative correction. Positive adjustments must feel exceptional.

**Fields:**

| Field          | Required | Type                             | Notes                                                   |
|----------------|----------|----------------------------------|---------------------------------------------------------|
| `event_at`     | yes      | datetime                         | Defaults to now.                                        |
| `direction`    | yes      | enum {`loss`, `positive`}        | Default `loss`. See UX rules.                           |
| `item_id`      | yes      | picker                           | Single-item form in v1 (keeps it simple).               |
| `quantity`     | yes      | number > 0                       | Always positive; direction field carries the sign.      |
| `unit`         | yes      | enum from item master            |                                                         |
| `reason_code`  | yes      | enum                             | **TODO-WINDOW1**: canonical reason code list.           |
| `notes`        | sometimes| text                             | Required when direction is `positive` or reason is `other`. |
| `attachments`  | no       | file refs                        | Same as Goods Receipt.                                  |

**Validation UX rules:**
- Direction toggle is prominent and visually asymmetric: `loss` is the default path; `positive` is a second tab labeled "Positive correction" with a cautionary hint ("Positive adjustments increase system stock. These should be rare.").
- Selecting `positive` enables a required confirm step at submit time — a modal naming the item and quantity and requiring an explicit "Yes, I am adding stock" click. This is the only modal confirm in the Form screens.
- Quantity: zero blocked, negative input blocked (sign comes from `direction`).
- Notes required when `direction = positive` OR `reason_code = other`.
- Reason code must be selected before submit enables.
- **Threshold-based approval routing:** if quantity exceeds policy threshold for the item/reason, form displays a banner at submit time: "This adjustment exceeds the auto-post threshold and will be held for planner approval." Submit proceeds as normal; the submission lands in approval queue, not ledger. **TODO-WINDOW1**: threshold source (`planning_policy`?), threshold shape (per item? per reason?), whether the client can know the threshold pre-submit or only learns from server response.

**Screen states:**
- **empty** — direction defaulted to `loss`, other fields empty.
- **loading** — item master loading.
- **validation error** — inline + submit disabled; positive-direction missing notes highlighted specifically.
- **submission pending** — locked; confirm modal was already dismissed before reaching this state.
- **success** — confirmation card: item, direction arrow, quantity, current projected stock after adjustment (from response read model). Primary: "Record another". Secondary: "View submission".
- **approval required** — banner: "Held for planner approval. You do not need to do anything further." Submission visible in `/my-submissions` and `/approvals` (planner side).
- **stale / conflict** — rare for adjustments; possible if item is deactivated mid-form. Inline banner + block submit.

**API contract draft (PROPOSAL):**

Read models:
- `GET /read/items?q=…&kind=adjustable`
- `GET /read/adjustment-reasons` → `{ code, label, requires_notes: boolean }[]`
- **Optional**: `GET /read/adjustment-thresholds?item_id=…&reason_code=…` → `{ threshold_quantity, unit, applies_to_direction }` — would let client pre-warn about approval routing. **TODO-WINDOW1**: should this read model exist, or should the server always decide silently?

Mutation intent:
- `POST /mutations/waste-adjustments`
- Envelope:
  ```
  {
    idempotency_key: string,
    event_at: ISO8601,
    direction: "loss" | "positive",
    item_id: string,
    quantity: number,              // always > 0
    unit: string,
    reason_code: string,
    notes?: string,
    attachments?: [...]
  }
  ```
- Response states: same four as Goods Receipt (`201 committed`, `202 pending_approval`, `409 conflict`, `422 validation`).
- **Idempotency:** required. Same client-key rules.

**TODO-WINDOW1**:
- Reason code canonical list.
- Threshold source and whether it is readable to the client.
- Whether "positive correction" has a stricter approval rule than loss at the same quantity.

---

### 5.3 S-06 Physical Count — **Form** (blind count UX)

**Purpose:** operator posts a counted quantity for an item. Blind by default — operator never sees system quantity before entering count. Full monthly count is the base process (foundation §9); ad-hoc counts supported but not featured in nav.

**Fields (single-item variant — see session variant below):**

| Field              | Required | Type                        | Notes                                                       |
|--------------------|----------|-----------------------------|-------------------------------------------------------------|
| `event_at`         | yes      | datetime                    | Defaults to now.                                            |
| `item_id`          | yes      | picker / barcode            | Barcode entry supported if item master has codes.           |
| `counted_quantity` | yes      | number ≥ 0                  | Zero is valid — "nothing on hand" is a legitimate count.    |
| `unit`             | yes      | enum from item master       |                                                             |
| `location`         | no       | picker                      | **TODO-WINDOW1**: are locations modeled in v1? Foundation is silent. |
| `notes`            | no       | text                        |                                                             |

**Session variant (monthly count run):**
- A **count session** is opened (by planner or admin) against a defined scope (all FG? all components? everything?).
- Operator sees a list of items in the session with a progress indicator and counts one at a time. Blind UX preserved per item.
- Session ends when all items are counted or the session is explicitly closed (closing with uncounted items prompts a confirm).

**TODO-WINDOW1**: does v1 model a `count_session` server-side, or is every count an independent posting? The foundation says "balance_anchors and/or stock_ledger" for counts — the decision between these affects whether a session exists server-side at all. I am deliberately **not** inventing session shape.

**Validation UX rules — blind count:**
- System quantity is **never** shown before `counted_quantity` is entered and submit is attempted. This is enforced in the UI; there is no "reveal system" button pre-submit.
- After submit, the success state reveals system quantity, counted quantity, and variance. Variance triggers different downstream behavior (see below).
- Counted quantity accepts decimals where the item unit supports it; integer-only otherwise.
- Zero counts require no special confirmation (explicitly — zero is common and must not feel exceptional).
- Negative counts blocked (physical impossibility).

**Variance handling — inputs only, no semantics invented:**

After submit, the server response drives one of four outcomes. The client does not compute variance locally; it renders whatever the server returned.

1. **No variance** → green success card, "Count matches system. Posted."
2. **Small variance (auto-post)** → amber success card showing system vs counted vs delta. Operator informed that an auto-adjustment was posted.
3. **Large variance (held for approval)** → amber banner: "Variance exceeds auto-post threshold. Held for planner approval." Operator's job is done.
4. **Conflict** → rare; e.g. item deactivated mid-count.

**TODO-WINDOW1 (critical):**
- Does a count post as an **anchor** that replaces the stock projection, or as an **adjustment** ledger row that reconciles to the system qty?
- Where does the variance threshold live (`planning_policy`?), and is it per-item or global?
- Does "large variance auto-post" exist, or is it "small auto, large approval" binary?
- Does the server need to know the operator's intended mode (anchor vs adjustment), or does it decide?

I will not ship a submit path until these four questions are answered.

**Screen states:**
- **empty** — item picker focused, counted_quantity empty.
- **loading** — item master / session loading.
- **validation error** — inline; submit disabled.
- **submission pending** — locked.
- **success (no variance)** — see above.
- **success (variance, auto-posted)** — see above.
- **approval required (variance, held)** — see above.
- **stale / conflict** — item deactivated mid-count or session closed by another user.

**API contract draft (PROPOSAL):**

Read models:
- `GET /read/items?q=…&kind=countable` (or `?session_id=…` in session mode)
- `GET /read/count-sessions?state=open` — **TODO-WINDOW1** whether sessions exist.

Mutation intent:
- `POST /mutations/physical-counts`
- Envelope (single-count variant):
  ```
  {
    idempotency_key: string,
    event_at: ISO8601,
    item_id: string,
    counted_quantity: number,      // >= 0
    unit: string,
    location_id?: string,
    session_id?: string,
    notes?: string
  }
  ```
- Response states:
  - `201 committed_no_variance`
  - `201 committed_auto_adjusted` → response includes `system_quantity`, `counted_quantity`, `delta`, `adjustment_reference`.
  - `202 variance_pending_approval` → response includes same variance breakdown + approval reference.
  - `409 conflict` → item deactivated / session closed / etc.
  - `422 validation`.
- **Idempotency:** required. Replays must not re-post a count.

**TODO-WINDOW1**: exact response shape for variance breakdown; whether client can ever see `system_quantity` before submit (answer from brief: no, blind UX is mandatory).

---

### 5.4 S-07 Production Actual — **Form** (v1.1 — slice reserved, full spec deferred)

**Purpose:** operator reports finished-goods production. Foundation §8 locks the simple version: operator reports output + scrap; server computes standard consumption from BOM.

**Field skeleton only:**
- `event_at`
- `produced_item_id` (FG)
- `produced_quantity`
- `scrap_quantity`
- `unit`
- optional `shift`, `operator_name`, `notes`

**No manual component consumption in v1.** This is a foundation lock, not a Window 2 choice.

**API contract, ledger semantics, and approval rules:** deferred to Window 1 for v1.1 spec sweep. Slice `features/production-actual/` is reserved but not implemented in Window 2's first build.

---

### 5.5 S-12 PO Form — **Form** (downstream of approved purchase recommendation)

**Purpose:** create a committed PO from an approved purchase recommendation. Never directly from scratch in v1 (foundation §10 step sequence: recommendation → review/approve → PO form → OPEN state). Ad-hoc POs outside the recommendation flow are explicitly out of v1 scope unless Window 5 says otherwise.

**Fields:**

| Field              | Required | Type              | Notes                                                         |
|--------------------|----------|-------------------|---------------------------------------------------------------|
| `recommendation_id`| yes      | hidden / prefilled| Source of truth for prefill.                                  |
| `supplier_id`      | yes      | locked prefill    | Editable only under explicit override flow.                   |
| `expected_date`    | yes      | date              | Defaults from recommendation lead time.                       |
| `currency`         | yes      | from supplier     | Read-only.                                                    |
| `lines[]`          | yes, ≥1  | repeating group   | Prefilled from recommendation; qty/unit editable with reason. |
| `notes`            | no       | text              |                                                               |

**Validation UX rules:**
- Line edits that deviate from the recommended quantity require a reason note on that line.
- Deleting a line requires a confirm.
- Adding a line outside the original recommendation is blocked in v1. **TODO-WINDOW5**: confirm.

**Screen states:** same catalog as other forms, with one addition — **"source recommendation stale"** banner if the underlying recommendation was regenerated since PO form was opened. Operator is offered "Refresh from latest" or "Cancel".

**API contract draft:**
- Read: `GET /read/purchase-recommendations/:id` (full detail with lines).
- Mutate: `POST /mutations/purchase-orders`
- Envelope includes `source_recommendation_id` + `source_recommendation_version` for staleness detection.
- Response states: `201 created`, `409 source_stale`, `422 validation`.
- **Idempotency:** required.

---

### 5.6 S-09 Forecast Workspace — **Planning Screen**

**Purpose:** Tom and Alex build and edit the forecast. Monthly-first, translated to weekly and daily operationally. 8-week horizon. SKU-level and family-level visibility (foundation §8).

**This is not a form.** It is a versioned editing workspace backed by `forecast_versions` / `forecast_lines` (foundation §6 source-of-truth map). It does not post to the ledger.

**Structure:**
- **Grid:** rows = SKUs (filterable to families), columns = time buckets (monthly default, toggle to weekly).
- **Version selector:** draft, published, prior published. Edits only allowed against a draft version.
- **Bucket granularity toggle:** monthly ↔ weekly. Daily view in v1 is read-only (computed from weekly).
- **Family rollup:** expand/collapse family → SKUs. Family row shows sum; editing at family level is **out of v1 scope** unless Window 5 says otherwise.
- **Edit affordance:** click cell, type value, move. Standard grid pattern.
- **No mandatory reason field per edit in v1** (foundation §8).

**Top-level actions:**
- `Save draft` — persists current draft version.
- `Publish version` — commits the draft as a new published version. Triggers approvals if Window 5/1 decides. **TODO-WINDOW5**: does publishing require approval?
- `Discard draft` — confirm, then revert.
- `Compare versions` — read-only diff between two versions. v1.1.

**Validation UX rules:**
- Negative forecast values: blocked inline.
- Empty cells: treated as zero, displayed as muted "—". Operator can explicitly enter 0.
- Family-total overrides by SKU-sum are shown as a hint, not an error (family is derived).
- Stale-version detection: if the draft was modified by another user, local edits are held; operator sees a "Draft changed by <user> at <time>" banner and must choose merge/discard/reload. **TODO-WINDOW1**: does backend support per-cell optimistic concurrency, or is the unit of locking the whole version?

**Screen states:**
- **empty** — no draft exists; CTA: "Start new draft from latest published".
- **loading** — grid skeleton.
- **validation error** — inline on the offending cell; top banner lists count of invalid cells.
- **save pending** — save button in loading state; grid remains editable (debounced autosave may come later).
- **save success** — toast only ("Draft saved at HH:MM"). No modal.
- **publish pending / success** — distinct from save. Publish is a deliberate action, confirmed with a modal summarizing what changed.
- **approval required** — if publishing routes through approval, a banner surfaces it.
- **stale / conflict** — as above.

**API contract draft (PROPOSAL):**

Read models:
- `GET /read/forecast-versions?status=draft|published`
- `GET /read/forecast-version/:id` → dense cell payload + metadata (family structure, bucket definitions).
- `GET /read/items?kind=forecastable` (for adding new rows).

Mutations:
- `POST /mutations/forecast/draft` — create a new draft from latest published.
- `PATCH /mutations/forecast/:draft_id/cells` — batch cell updates. Envelope: `{ version_etag, updates: [{ item_id, bucket, value }] }`. Response: updated cells + new `version_etag` or `409 stale`.
- `POST /mutations/forecast/:draft_id/publish` — commit draft. Response: new published version id, or `202 pending_approval`.
- `DELETE /mutations/forecast/:draft_id` — discard.
- **Idempotency:** less critical at cell-update level (batch updates are naturally replayable with etag). Required on `publish`.

**TODO-WINDOW1**:
- Cell payload shape (per SKU × bucket dense matrix vs sparse list).
- Whether draft editing is per-user or global (single draft per period vs parallel drafts).
- Whether publish requires approval.

---

### 5.7 S-10 Purchase Recommendations Review — **Planning Screen**

**Purpose:** planner reviews the latest planning-run output, approves/rejects/edits recommendations. Approved lines flow into PO Form (S-12). Recommendations are **not autonomous orders** (foundation §8).

**Structure:**
- Table of recommendations from the most recent `planning_runs` output.
- Columns: supplier, item, recommended qty, unit, target receive date, urgency, reason/trigger, current on-hand, open-PO qty, projected stockout date.
- Row-level actions: `Approve`, `Edit quantity`, `Hold`, `Reject`.
- Bulk actions: `Approve selected`, `Reject selected`.
- Filters: supplier, urgency, item family, stockout proximity.
- Grouping: by supplier (default) or by item family.

**Validation UX rules:**
- Edit quantity requires a reason note.
- Reject requires a reason note from a fixed enum.
- Bulk approve of >N lines triggers a confirm modal listing affected suppliers and total committed value. **TODO-WINDOW5**: threshold N.
- Approving across multiple suppliers generates one PO per supplier at the PO Form stage, not one mega-PO.
- Stale-run detection: if a new planning_run lands while planner is reviewing, a banner surfaces "Newer run available. Current view is from <time>." with actions to reload or continue on stale run. Continuing is allowed; the planner owns the judgment.

**Screen states:**
- **empty** — no planning run yet / no recommendations.
- **loading** — table skeleton.
- **row-action pending** — row dims; spinner on the action.
- **success** — inline row state change; toast for bulk actions.
- **approval required** — if an approval is itself a queued item (rare here — planner approval is the approval), banner explains.
- **stale / conflict** — as above.

**API contract draft (PROPOSAL):**

Read models:
- `GET /read/planning-runs/latest?kind=purchase` → metadata.
- `GET /read/purchase-recommendations?planning_run_id=…` → rich list.

Mutations:
- `POST /mutations/purchase-recommendations/:id/approve` — body: optional `adjusted_quantity`, optional `note`.
- `POST /mutations/purchase-recommendations/:id/reject` — body: `reason_code`, `note?`.
- `POST /mutations/purchase-recommendations/:id/hold` — body: `note?`.
- `POST /mutations/purchase-recommendations/batch-approve` — body: `{ ids: [...], note? }`.
- **Idempotency:** required on bulk batches. Individual row actions should also tolerate replay.

**TODO-WINDOW1**: whether approving a recommendation creates a PO directly or stages a queue item for S-12.

---

### 5.8 S-11 Production Recommendations Review — **Planning Screen (v1.1)**

**Purpose:** same pattern as S-10 but for production. Foundation §8 allows this to be lighter in early phases.

Slice reserved. Not fully specified in Window 2's first sweep. Shares the row-action pattern from S-10.

---

### 5.9 S-02 Dashboard — **Read-only Dashboard**

**Purpose:** highest-trust rolled-up decision-grade view. Never an editing surface (foundation §13).

**Tiles (v1):**
- Stock health summary (total items, items in shortage, items in overstock) — links to a filtered stock read model.
- Shortage risk list (top N items with projected stockout within horizon).
- Latest planning run: time, recommendation counts, flagged items.
- Exceptions summary (open exceptions by severity).
- Data freshness: last ledger posting, last planning run, last LionWheel sync, last Shopify sync, last Green Invoice pull.
- Readiness indicators: ledger integrity, projection lag, job health.

**All tiles are read-only.** Clicking drills into the appropriate inbox or filtered list; no direct mutations from the dashboard.

**API contract draft:**
- `GET /read/dashboard` → dense composite read model, single request.
- **TODO-WINDOW1**: whether to expose one composite read model or one per tile. Composite is proposed for v1 to minimize chatter.

**States:** empty (no data yet — first-run state), loading (per-tile skeletons), partial-failure (a tile shows a small error chip without breaking the whole dashboard).

---

### 5.10 S-03 Operator Home — **Read-only Dashboard**

**Purpose:** operator landing page. Minimal. Shows:
- Big action buttons: Goods Receipt, Waste/Adjustment, Physical Count.
- My recent submissions (last 5).
- Queued submissions in outbox (if any).
- Any approval states the operator should know about ("Your adjustment from yesterday was approved" / "Your count is awaiting review").

No filters, no tables, no drill-downs. The operator home is a launchpad, not a workspace.

**API:** `GET /read/operator-home` → composite payload.

---

### 5.11 S-08 My Submissions / Outbox — **Read-only Inbox**

**Purpose:** operator sees what they submitted, what state it is in, and what is queued offline.

**List columns:** time, form type, brief summary, state (`queued`, `submitting`, `committed`, `pending_approval`, `approved`, `rejected`, `failed`).

**Row actions:**
- For `queued` / `failed`: `Retry now`, `Discard`.
- For `committed` / others: `View details`.

**Sources:**
- Local outbox (IndexedDB via `lib/outbox/`).
- Server submissions list: `GET /read/my-submissions?limit=…`.
- Merge rule: queued items appear at the top, committed below, sorted by time.

**States:** standard read-only states + per-row action pending.

---

### 5.12 S-13 Exceptions Inbox — **Read-only Inbox + actions**

**Purpose:** planner triages exceptions emitted by scheduled jobs (stock integrity, price anomalies, integration failures, etc.).

**Structure:**
- List view with filters: severity, source, status, age.
- Row expand shows detail + recommended action.
- Actions: `Acknowledge`, `Resolve` (with note), `Reassign`. **TODO-WINDOW5**: is reassignment in v1?

**API:**
- `GET /read/exceptions?filter=…`
- `POST /mutations/exceptions/:id/acknowledge`
- `POST /mutations/exceptions/:id/resolve` — body: `{ note }`.
- **Idempotency:** not critical for acks; required for resolution.

**States:** standard read-only + row action states.

---

### 5.13 S-14 Approvals Inbox — **Read-only Inbox + actions**

**Purpose:** planner sees items pending approval: large waste adjustments, large count variances, possibly forecast publishes and PO issues. This is the other side of the "approval required" success state from the operator forms.

**Structure:**
- Grouped by approval type.
- Row shows: submitter, time, summary, why it requires approval (policy trigger).
- Row expand shows full submission detail.
- Actions: `Approve`, `Reject with reason`, `Request changes` (if Window 5 confirms this exists in v1).

**API:**
- `GET /read/approvals?status=pending`
- `POST /mutations/approvals/:id/approve` — body: `{ note? }`.
- `POST /mutations/approvals/:id/reject` — body: `{ reason_code, note? }`.
- **Idempotency:** required.

**TODO-WINDOW1**: the approval queue is one table server-side or per-domain? This spec assumes one uniform queue with a `kind` discriminator.

---

### 5.14 S-15 Jobs Monitor — **Read-only Dashboard (admin)**

**Purpose:** admin sees scheduled jobs, last run, next run, status, errors.

**List columns:** job name, schedule, last run start/end, last run status, next run, last error.

**Row actions (admin):** `Run now`, `Disable`, `View logs`. Last-run log body is a read model; portal does not shell into infrastructure.

**API:**
- `GET /read/jobs` → list with status.
- `GET /read/jobs/:id/runs?limit=…`
- `POST /mutations/jobs/:id/trigger` — idempotency key advisable since "run now" retries are annoying otherwise.
- `POST /mutations/jobs/:id/set-enabled` — body: `{ enabled: boolean }`.

---

### 5.15 S-16–S-20 Master Data Admin — **Admin CRUD**

**Shared pattern:**
- List view with search and basic filters.
- Detail view with edit form.
- Create flow from list.
- Soft delete / deactivate only — never hard delete. (Master data is referenced by historical events; hard delete breaks audit.)
- Optimistic concurrency: every detail payload carries a `version` / `etag`; mutations require it; `409` on mismatch.

**Per-domain notes:**

- **S-16 Items** — FG, components, packaging all viewed here, filterable by kind. Fields per foundation §6 master map. No BOM editing here (BOM editor is its own slice, S-18).
- **S-17 Components** — may be merged into S-16 depending on how the schema separates them. **TODO-WINDOW1**: is `components` a separate table or a filter over `items`?
- **S-18 BOMs** — nested editor: BOM header + ordered lines. Each line is `component_id`, `quantity_per`, `unit`, `scrap_factor`. Changing a BOM must be versioned; new versions do not rewrite historical production postings.
- **S-19 Suppliers** — supplier detail + supplier-item mapping submodule. Mapping is where Green Invoice price-update gets its authority (foundation §14). Mapping quality affects whether active prices auto-update.
- **S-20 Planning Policy** — policy keys and values. Includes the thresholds Window 2's forms reference (approval thresholds, backdate windows, variance auto-post thresholds).

**API:** standard CRUD verbs. `GET /read/<domain>`, `GET /read/<domain>/:id`, `POST /mutations/<domain>`, `PATCH /mutations/<domain>/:id` with etag, `POST /mutations/<domain>/:id/deactivate`.

**Idempotency:** not required on PATCH (etag gives the same guarantee). Required on create (prevent double-create).

---

### 5.16 S-21 Users Admin — **Admin CRUD**

Minimal in v1: list users, assign role, deactivate. No custom permission grid (only the four roles).

**TODO-WINDOW1**: is user creation done in the portal or in Supabase console? Spec assumes: invite flow creates a Supabase auth user + assigns role.

---

### 5.17 S-22 Integrations Admin — **Admin CRUD (v1.1)**

Configuration views for LionWheel, Shopify, Green Invoice: connection health, last sync time, manual resync action. Foundation doesn't fully lock shape; reserved as v1.1.

---

## 6. Cross-cutting: screen state catalog

Seven canonical states. Every screen declares which states it supports; a state the screen does not support is explicitly N/A, not quietly absent.

| State                  | Trigger                                             | Visual rule                                                                 | Recovery rule                                                    |
|------------------------|-----------------------------------------------------|------------------------------------------------------------------------------|------------------------------------------------------------------|
| `empty`                | No data / fresh screen                              | Short, specific copy. Avoid generic "nothing to see here."                   | CTA to the primary next step.                                    |
| `loading`              | Awaiting read model                                 | Skeleton, not spinner overlay. Inputs disabled on forms.                     | Auto-recovers.                                                   |
| `validation error`     | Client-side rule failed                             | Inline per-field + top summary listing invalid items.                        | User edits; errors clear as fixed.                               |
| `submission pending`   | Mutation in flight                                  | Submit locked, inputs locked, banner after ~2s, transition to queued if offline. | Auto-recovers or transitions to `success` / `queued` / `failed`. |
| `success`              | Mutation committed                                  | Confirmation card with: what was submitted, what happened next, next action. | User navigates.                                                  |
| `approval required`    | Mutation accepted but pending                       | Banner naming the approval path. Submission listed in `/my-submissions`.     | User navigates; system notifies on resolution.                   |
| `stale / conflict`     | Server state changed beneath the user               | Banner + explicit choice: reload, merge, discard.                            | User picks a path; no silent overwrites.                         |

**Rule:** screens must never silently discard user input on conflict. Either the server payload wins with an explicit banner and the user confirms, or the user's draft is preserved.

---

## 7. Cross-cutting: outbox / retry envelope

### Purpose
Operator network instability must not cost submissions. Applies to **Forms only** (S-04, S-05, S-06, S-07, S-12). Planning screens have their own server-side draft/version model and do not use the outbox.

### Storage
IndexedDB (via a small wrapper in `lib/outbox/`), keyed by `outbox_id`.

### Envelope

```
OutboxEntry {
  outbox_id: string            // local uuid
  form_type: "goods_receipt" | "waste_adjustment" | "physical_count" | "production_actual" | "purchase_order"
  payload: object              // exactly the mutation envelope the API expects
  idempotency_key: string      // stable; reused on every retry of this logical submission
  created_at: ISO8601
  attempts: number
  last_attempt_at: ISO8601 | null
  last_error: { code, message, retriable: boolean } | null
  state: "queued" | "submitting" | "committed" | "pending_approval" | "failed_retriable" | "failed_terminal" | "discarded"
}
```

### Behavior rules
- On submit, the form creates the envelope with `state=queued` **before** dispatching the network request. If the network request succeeds, the envelope state advances in place; if it fails, the envelope remains in the queue and the UI shows a "queued — will retry" chip.
- Retries use the same `idempotency_key`. Server must dedup.
- `failed_terminal` (e.g. 422 validation) requires operator action: the entry is highlighted in `/my-submissions`, operator can `Discard` or `Edit and resubmit` (which generates a **new** idempotency key and a new envelope).
- Discard is always explicit. The outbox never drops an entry on its own.
- The top bar of the portal shows a persistent "queued submissions: N" chip when the outbox is non-empty. Clicking routes to `/my-submissions`.
- Outbox is per-device. No cross-device sync.

### What the outbox does **not** do
- It does not invent server semantics. A `failed_retriable` entry is retried but the server is the judge of dedup.
- It does not merge entries.
- It does not auto-submit forms the user didn't explicitly submit.

---

## 8. Cross-cutting: idempotency model

- Every stock-affecting mutation carries a client-generated idempotency key.
- Keys are stable across retries of the same logical submission.
- A new key is generated only when the operator explicitly starts a new submission (new form, or "Edit and resubmit" from outbox).
- The server is responsible for deduplication; the client does not attempt to determine whether a retry "already succeeded."

**TODO-WINDOW1:** confirm server idempotency implementation (table? TTL? scope per-endpoint vs global?). This spec assumes: per-endpoint idempotency table with ≥ 24h TTL, lookup on `(endpoint, idempotency_key)`.

---

## 9. Open coordination items

### Blocking for Window 1 (schema / API surface)
1. Session shape and role claim placement in Supabase Auth.
2. Goods receipt: over-receipt / backdate / extra-line semantics. Attachment upload envelope.
3. Waste / adjustment: reason code canonical list; threshold source and read-model availability; whether positive-direction rule is stricter.
4. Physical count: anchor vs adjustment posting model; variance threshold source; session vs single-count server model; blind-UX enforcement (server must not return system qty in pre-submit read models).
5. Approval queue: one uniform queue with `kind` discriminator, or per-domain queues.
6. Forecast: cell payload shape; draft scope (global vs per-user); publish-approval policy.
7. Purchase recommendations: does approve directly create a PO or stage S-12 input?
8. Idempotency table shape and TTL.
9. Read-model shape for dashboard (composite vs per-tile).
10. Whether `components` is a separate admin surface from `items` or a filter.
11. User creation flow (portal vs Supabase console).

### Blocking for Window 5 (coordination)
1. Monorepo layout + workspace tool.
2. Role hierarchy (disjoint vs hierarchical).
3. Role × route matrix final confirmation.
4. Whether planning approval routing applies to forecast publish.
5. PO Form: whether ad-hoc POs outside the recommendation flow are v1.
6. Bulk-approve threshold for confirmation modal.
7. Reassignment action on Exceptions Inbox.
8. Recommendations: approval-to-PO staging shape.

### Not blocking — can proceed to shell scaffolding once Window 5 confirms §1.1
Once the monorepo layout and Supabase Auth session shape are locked, Window 2 can scaffold:
- `apps/portal/` with app-router tree from §1.2.
- `lib/auth/RoleGate` against real session decoding.
- `lib/outbox/` against the envelope in §7.
- Shared form primitives and state catalog wiring.
- Route-group layouts with role-aware nav.

Connected form submission requires the API contracts in §5 to be accepted or revised by Window 1. Until then, form submit handlers remain `TODO-WINDOW1` stubs.

---

## 10. What this spec does not do

- It does not freeze the API. Every `POST /mutations/*` shape in §5 is a Window 2 proposal for Window 1 to accept, revise, or reject.
- It does not pick a form library, validation library, styling system, or test runner. Those are Window 5 coordination calls. _(Superseded in the build round: Tom approved RHF + zod + Tailwind + shadcn-style primitives, and the review round 2026-04-14 added Vitest + Playwright as the test runner pair. See `window2-acceptance-note.md`.)_
- It does not describe visual design. It describes behavior and state rules only.
- It does not invent ledger semantics, approval-threshold values, or stock-posting rules.
- It does not touch Excel. The portal has no Excel surface by design.

---

_End of Window 2 portal specification (skeleton)._
