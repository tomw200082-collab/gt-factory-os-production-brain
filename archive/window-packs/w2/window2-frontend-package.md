# Window 2 — Frontend Package

_Last updated: 2026-04-14_
_Scope: contract/skeleton only. No connected backend. No ledger mutations. No real auth._

This document accompanies the portal code at `PRODUCTION/portal/`. It follows the ordered output format requested in §10 of the Window 2 brief. The portal code already implements everything described here at shell depth; the backend hookup surface is explicitly flagged wherever it applies.

> To run the portal: `cd PRODUCTION/portal && npm install && npm run dev`. No backend required. First-run seeds a local IndexedDB store with realistic factory fixtures. Use the **FAKE SESSION** chip in the top bar to swap roles, and the **Review mode** button to force any screen into any of the seven canonical states.

---

## 1. Portal module map

### Monorepo shape (confirmed by Window 5 as of this session)
Single Next.js 15 App Router app at `PRODUCTION/portal/`. No monorepo workspace tool yet. Shared types live inside the app at `src/lib/contracts/`. If Window 1 needs to share types across a server package later, this folder is the extraction target.

### Route tree

```
src/app/
  (auth)/
    login/                            public, fake-session continue
  (shared)/
    dashboard/                        all authenticated roles
    profile/                          all authenticated roles
  (operator)/
    home/                             operator landing
    ops/
      receipts/                       Goods Receipt form
      waste-adjustments/              Waste / Adjustment form
      counts/                         Physical Count form (blind UX)
      production-actual/              v1.1 shell
    my-submissions/                   operator outbox + history
  (planner)/
    planning/
      forecast/                       forecast workspace
      purchase-recommendations/       purchase recs review workspace
      production-recommendations/     v1.1 slice
    exceptions/                       exceptions inbox
    approvals/                        approvals inbox
    purchasing/po/                    PO form (downstream of rec)
  (admin)/
    admin/
      items/
      components/
      boms/
      suppliers/
      supplier-items/
      planning-policy/
      users/
      jobs/
      integrations/
```

### Shared modules

```
src/components/
  layout/           AppShellChrome, TopBar, SideNav, AppPageShell
  workflow/         WorkflowHeader, SectionCard, FieldGrid/Field, FormActionsBar,
                    ValidationSummary, ApprovalBanner, DiffNotice
  badges/           StatusBadge, Badge, FreshnessBadge, ReadinessBadge
  fields/           QuantityInput, UomDisplay, DateTimeInput, NotesBox,
                    EntitySearchSelect
  line-editor/      LineEditorTable
  data/             SearchFilterBar, AuditSnippet
  feedback/         EmptyState, LoadingState, ErrorState, SuccessState, StaleNotice
  review/           ReviewModePanel

src/lib/
  auth/             fake-auth, session-provider, role-gate
  review-mode/      store + useForcedOr hook + StatePreviewChip
  query/            TanStack Query provider
  repositories/     IndexedDB persistence (generic + BOM specialised)
  contracts/        enums.ts + dto.ts (shared types)
  fixtures/         seed data (real factory-shape fixtures, Hebrew data values)

src/features/
  master-data/      SplitListLayout
  ops/              StatePreviewChip
```

---

## 2. Role-based route map

Roles are **disjoint** (an admin is not automatically a planner). The matrix below is enforced by `RoleGate` server-side in each route-group layout, and by nav-link suppression in `SideNav`.

| Route                                         | operator | planner | admin | viewer |
|-----------------------------------------------|----------|---------|-------|--------|
| `/login`                                      | R        | R       | R     | R      |
| `/dashboard`                                  | R        | R       | R     | R      |
| `/profile`                                    | R        | R       | R     | R      |
| `/home`                                       | R        | —       | —     | —      |
| `/ops/receipts`                               | W        | —       | —     | —      |
| `/ops/waste-adjustments`                      | W        | —       | —     | —      |
| `/ops/counts`                                 | W        | —       | —     | —      |
| `/ops/production-actual`                      | W        | —       | —     | —      |
| `/my-submissions`                             | R        | —       | —     | —      |
| `/planning/forecast`                          | —        | W       | R     | R      |
| `/planning/purchase-recommendations`          | —        | W       | R     | R      |
| `/planning/production-recommendations`        | —        | W       | R     | R      |
| `/exceptions`                                 | —        | W       | R     | —      |
| `/approvals`                                  | —        | W       | R     | —      |
| `/purchasing/po`                              | —        | W       | R     | —      |
| `/admin/items`                                | —        | R       | W     | —      |
| `/admin/components`                           | —        | R       | W     | —      |
| `/admin/boms`                                 | —        | R       | W     | —      |
| `/admin/suppliers`                            | —        | R       | W     | —      |
| `/admin/supplier-items`                       | —        | R       | W     | —      |
| `/admin/planning-policy`                      | —        | R       | W     | —      |
| `/admin/users`                                | —        | —       | W     | —      |
| `/admin/jobs`                                 | —        | R       | W     | —      |
| `/admin/integrations`                         | —        | —       | W     | —      |

---

## 3. Screen inventory

| ID    | Screen                             | Archetype                     | Phase  | Path                                              |
|-------|------------------------------------|-------------------------------|--------|---------------------------------------------------|
| S-01  | Login                              | Form (auth placeholder)       | v1     | `/login`                                          |
| S-02  | Dashboard                          | Read-only Decision Surface    | v1     | `/dashboard`                                      |
| S-03  | Operator Home                      | Read-only Decision Surface    | v1     | `/home`                                           |
| S-04  | Goods Receipt                      | **Operational Form**          | v1     | `/ops/receipts`                                   |
| S-05  | Waste / Adjustment                 | **Operational Form**          | v1     | `/ops/waste-adjustments`                          |
| S-06  | Physical Count                     | **Operational Form**          | v1     | `/ops/counts`                                     |
| S-07  | Production Actual                  | Operational Form (v1.1 slice) | v1.1   | `/ops/production-actual`                          |
| S-08  | My Submissions                     | Read-only Decision Surface    | v1     | `/my-submissions`                                 |
| S-09  | Forecast Workspace                 | **Planning Workspace**        | v1     | `/planning/forecast`                              |
| S-10  | Purchase Recommendations Review    | **Planning Workspace**        | v1     | `/planning/purchase-recommendations`              |
| S-11  | Production Recommendations Review  | Planning Workspace (v1.1)     | v1.1   | `/planning/production-recommendations`            |
| S-12  | PO Form                            | Operational Form              | v1     | `/purchasing/po`                                  |
| S-13  | Exceptions Inbox                   | Read-only Decision Surface    | v1     | `/exceptions`                                     |
| S-14  | Approvals Inbox                    | Read-only Decision Surface    | v1     | `/approvals`                                      |
| S-15  | Jobs Monitor                       | Read-only Decision Surface    | v1     | `/admin/jobs`                                     |
| S-16  | Items Admin                        | **Admin Maintenance**         | v1     | `/admin/items`                                    |
| S-17  | Components Admin                   | **Admin Maintenance**         | v1     | `/admin/components`                               |
| S-18  | BOMs Admin                         | **Admin Maintenance** (nested)| v1     | `/admin/boms`                                     |
| S-19  | Suppliers Admin                    | **Admin Maintenance**         | v1     | `/admin/suppliers`                                |
| S-20  | Supplier-Items Mapping             | **Admin Maintenance**         | v1     | `/admin/supplier-items`                           |
| S-21  | Planning Policy Admin              | **Admin Maintenance**         | v1     | `/admin/planning-policy`                          |
| S-22  | Users Admin                        | Admin Maintenance             | v1     | `/admin/users`                                    |
| S-23  | Integrations Admin                 | Admin Maintenance (v1.1)      | v1.1   | `/admin/integrations`                             |

---

## 4. Archetype definitions

### A. Operational Form page

**Belongs to:** S-04, S-05, S-06, S-07, S-12.
**Core contract:** one discrete real-world event per submission. Exactly one mutation envelope. Fast to complete. Carries an idempotency key. May route through approval, but from the operator's perspective it was submitted.

**Standard anatomy (implemented in `components/workflow/*`):**
- `WorkflowHeader` — eyebrow, title, description, meta chips.
- optional `StatePreviewChip` — surfaces when review mode forces a state.
- `ValidationSummary` — blocker/warning stack, surfaces above the form.
- optional `ApprovalBanner` — informs the operator when the current inputs will route to approval.
- one or more `SectionCard` blocks containing field groups (`FieldGrid` + `Field`).
- optional `LineEditorTable` for line-item entry (Goods Receipt, PO Form).
- `FormActionsBar` (sticky) — primary submit + secondary reset/cancel, plus a hint slot.
- post-submit view swap → `SuccessState` / `StaleNotice` / `LoadingState` (submission pending).

**Blind-UX rule:** S-06 (Physical Count) never renders system quantity in pre-submit read models. The reveal is explicit in the post-submit success card.

**Positive-adjustment rule:** S-05 uses an asymmetric direction toggle and a required modal confirm on submit. Notes are required when direction is positive.

### B. Planning Workspace

**Belongs to:** S-09, S-10, (S-11 reserved).
**Core contract:** versioned judgment editing over server-side drafts. Multi-row/multi-cell edits with a separate commit/publish action. Optimistic concurrency via version etags. Never touches the ledger.

**Standard anatomy:**
- `WorkflowHeader` with version badge (`draft vN`) and freshness metadata.
- optional `DiffNotice` at the top — surfaces stale-version banners with reload/dismiss.
- optional `ApprovalBanner` — e.g. "publish requires approval".
- filter toolbar — chips for families, suppliers, urgency, etc.
- central grid/list with inline editors (S-09 grid) or row-action table (S-10).
- `FormActionsBar` with save/publish/discard, dirty-count leading, selection info.
- right-hand drawer/detail panel is reserved but not needed in v1.

**Distinction from operational forms:** no single "submit this event" intent. Edits persist to a versioned draft; publish is a distinct act.

### C. Admin Maintenance page

**Belongs to:** S-16 through S-23.
**Core contract:** master data CRUD with optimistic concurrency, soft-deactivate only, audit snippet, and a strict split between safe edits (simple attributes) and structural changes (BOM versioning, mapping quality).

**Standard anatomy (`features/master-data/SplitListLayout`):**
- `WorkflowHeader` with "+ New …" action.
- list/table with `SearchFilterBar` (chips for kind/status filters, archive toggle).
- right-hand `SectionCard` detail panel on selection or create (`SplitListLayout` grid).
- detail panel uses `FieldGrid` + RHF + zod + server-side version concurrency.
- audit collapse at the bottom of the edit panel.
- archive/reactivate is a distinct secondary action; hard delete never appears.

**BOM-specific nesting (S-18):** head → version → lines. Only DRAFT versions are editable. "New draft from latest" clones, "Activate" retires current active. Optimistic concurrency is on the head.

### D. Read-only Decision Surface

**Belongs to:** S-02, S-03, S-08, S-13, S-14, S-15.
**Core contract:** consumes read models. May surface actions (acknowledge, resolve, approve, reject) as distinct mutations, but the surface itself is not a form. Never persists draft state.

**Standard anatomy:**
- `WorkflowHeader`.
- tiles (`card` class) with fixed numeric displays and `Badge` status pills.
- `FreshnessBadge` / `ReadinessBadge` clusters for data-age signals.
- list views with `SearchFilterBar` and row-expand details.
- action surfaces are inline per row (acknowledge, resolve, approve, reject).

---

## 5. Shared component system

Every primitive listed in the brief exists at `src/components/`:

| Component             | Path                                     | Role                                                       |
|-----------------------|------------------------------------------|------------------------------------------------------------|
| `AppPageShell`        | `layout/AppPageShell.tsx`                | Vertical flow wrapper.                                     |
| `AppShellChrome`      | `layout/AppShellChrome.tsx`              | Top bar + side nav + main content frame.                   |
| `TopBar`              | `layout/TopBar.tsx`                      | Brand, review-mode trigger, FAKE SESSION role chip.        |
| `SideNav`             | `layout/SideNav.tsx`                     | Role-aware nav with "blocked" chip for deferred routes.    |
| `WorkflowHeader`      | `workflow/WorkflowHeader.tsx`            | Eyebrow + title + description + meta + actions.            |
| `SectionCard`         | `workflow/SectionCard.tsx`               | Titled content block, optional tone + footer.              |
| `FieldGrid` / `Field` | `workflow/FieldGrid.tsx`                 | 1–4 column grid + label/required/error/hint wrapper.       |
| `FormActionsBar`      | `workflow/FormActionsBar.tsx`            | Sticky primary/secondary action footer with hint slot.     |
| `ValidationSummary`   | `workflow/ValidationSummary.tsx`         | Blocker/warning summary with top-of-form stacking.         |
| `ApprovalBanner`      | `workflow/ApprovalBanner.tsx`            | "Held for approval" and policy-trigger banner.             |
| `DiffNotice`          | `workflow/DiffNotice.tsx`                | Stale-data banner with reload/dismiss.                     |
| `StatusBadge`/`Badge` | `badges/StatusBadge.tsx`                 | Submission-state badge + neutral tone badge.               |
| `FreshnessBadge`      | `badges/FreshnessBadge.tsx`              | Time-since-X with warn/fail thresholds.                    |
| `ReadinessBadge`      | `badges/ReadinessBadge.tsx`              | OK/warn/fail indicator with optional detail.               |
| `AuditSnippet`        | `data/AuditSnippet.tsx`                  | Created/updated/version/status dl.                         |
| `SearchFilterBar`     | `data/SearchFilterBar.tsx`               | Search input + toggle chips + trailing slot.               |
| `LineEditorTable`     | `line-editor/LineEditorTable.tsx`        | Generic repeating-row editor with add/remove.              |
| `EntitySearchSelect`  | `fields/EntitySearchSelect.tsx`          | Search-and-pick dropdown over id-labelled options.         |
| `UomDisplay`          | `fields/UomDisplay.tsx`                  | Consistent UoM symbol rendering.                           |
| `QuantityInput`       | `fields/QuantityInput.tsx`               | Tabular-numeric number input with trailing unit.           |
| `DateTimeInput`       | `fields/DateTimeInput.tsx`               | Datetime-local wrapper with error state.                   |
| `NotesBox`            | `fields/NotesBox.tsx`                    | Styled textarea wrapper.                                   |
| `EmptyState`          | `feedback/states.tsx`                    | Empty placeholder.                                         |
| `LoadingState`        | `feedback/states.tsx`                    | Spinner card.                                              |
| `ErrorState`          | `feedback/states.tsx`                    | Error card with danger border.                             |
| `SuccessState`        | `feedback/states.tsx`                    | Post-submit confirmation with tone variants.               |
| `StaleNotice`         | `feedback/states.tsx`                    | Inline stale/conflict banner.                              |
| `ReviewModePanel`     | `review/ReviewModePanel.tsx`             | Dev panel forcing screen state + fixture set.              |
| `StatePreviewChip`    | `features/ops/StatePreviewChip.tsx`      | Shows when review mode is forcing a state on this screen.  |

Visual language: Tailwind with a small custom palette (`bg`, `fg`, `border`, `accent`, `success`, `warning`, `danger`, `info`) and a handful of component classes (`card`, `chip`, `btn`, `input`, `textarea`, `label`, `table-base`) exposed from `globals.css`. No shadcn CLI dependency; primitives are hand-rolled to stay portable.

---

## 6. Per-screen field contracts

The full per-screen specification is already in `window2-portal-spec.md` (written in a prior session). This section records the **deltas** the current build adds and **what is actually rendered** per screen. Read this alongside `window2-portal-spec.md`, not instead of it.

### S-16 Items Admin (Admin Maintenance)

- **Mode:** list + split-panel create/edit.
- **Fields:** sku, name, name_local (Hebrew allowed, `dir="auto"`), kind, supply_method, default_uom, min_stock, reorder_point, target_stock, lead_time_days, notes.
- **Validation (zod):** sku ≥ 2, name ≥ 2, numeric fields nonnegative, enums strict.
- **Approval-relevant fields:** none (master data).
- **States:** empty (filtered-out view), loading, validation_error inline + summary, success (panel remains open with fresh audit), stale_conflict (optimistic concurrency via `audit.version`).
- **Backend dependencies:** `GET/POST/PATCH /admin/items` + concurrency. Today all reads/writes go through `itemsRepo` (IndexedDB).

### S-17 Components Admin

- **Fields:** code, name, name_local, kind (component/raw_material/packaging), default_uom, density_kg_per_l, primary_supplier_id, lead_time_days, notes. `active_price` is read-only here; it lives on supplier-items and price history.
- **Validation:** density > 0 when provided; supplier reference optional.
- **Structural-change split:** Supply method and unit-of-measure changes are safe in v1 (components have no BOM-like versioning), but a planner prompt should appear if a unit change would orphan BOM lines. Currently not enforced in the shell. **TODO-WINDOW1**.

### S-18 BOMs Admin

- **Nested editor:** head → versions → lines.
- **Safe edits:** switching to a different version pill is free.
- **Structural edits:** only DRAFT versions are editable. "New draft from latest" clones lines. "Activate version" retires current active.
- **Fields per line:** component (select), quantity_per, unit, scrap_factor, sort_order (implicit).
- **Validation:** line quantity > 0 on save (checked at server; client allows transient 0 while editing). Scrap factor in [0, 1].
- **Approval-relevant fields:** none at client. Server decides if BOM activation routes through approval — **TODO-WINDOW1**.

### S-19 Suppliers Admin & S-20 Supplier-Items

- Supplier fields: code, name, name_local, contact_person/phone/email (Hebrew allowed), address, currency (3 chars), payment_terms, lead_time_days.
- Supplier-item (mapping) fields: supplier_id, component_id, supplier_sku, pack_size, pack_unit, price { amount, currency, unit }, preferred, mapping_quality (confirmed/probable/unmapped).
- **Mapping-quality rule:** only "confirmed" should allow Green Invoice auto-update. The shell stores quality; enforcement lives on the server. **TODO-WINDOW1**.

### S-21 Planning Policy Admin

- Fields: key, description, value_type (number/string/boolean), value, scope (global/item/supplier/reason), scope_ref.
- Value input adapts to value_type.
- **Live seeding:** real thresholds used by Goods Receipt and Waste/Adjustment shells (approval threshold, positive-always-approve, count variance, backdate window, price auto-update threshold). Today these are mock-read by the form components directly; **TODO-WINDOW1** to switch to server-provided planning-policy lookup once the API exists.

### S-04 Goods Receipt (Operational Form)

- **Fields:** event_at, supplier_id, po_id (optional), lines[] (item, quantity, unit, notes), header notes.
- **Validation:** quantities strictly positive, ≥1 line required, supplier required, event_at present.
- **States (all rendered):** empty, loading, validation_error, submission_pending, success, approval_required, stale_conflict. Operator can force each via review-mode panel.
- **Approval-relevant fields:** backdate window, over-receipt, extra line — all **TODO-WINDOW1**.
- **Submit behavior:** mock only. Handler is a no-op that swaps view to `success`. Real envelope is `POST /mutations/goods-receipts` per `window2-portal-spec.md` §5.1.

### S-05 Waste / Adjustment

- **Fields:** event_at, direction (loss/positive), item_id, quantity (always > 0), unit, reason_code, notes.
- **Validation:** positive-direction requires notes. `reason_code = other` requires notes.
- **Asymmetric direction:** `loss` is the default path. `positive` is visually flagged and prompts a confirm modal on submit.
- **Threshold preview:** client computes a mock threshold (25) for large losses. Actual threshold lives in planning_policy — **TODO-WINDOW1**.
- **States:** all seven, forceable via review mode.

### S-06 Physical Count

- **Blind UX:** system quantity is never rendered pre-submit. Success card reveals counted vs system vs delta.
- **Outcomes:** matched, auto (small variance), approval (large variance), conflict.
- **Fields:** event_at, item_id, counted_quantity (≥ 0), unit, notes.
- **Validation:** zero counts allowed; negative blocked.
- **Session mode:** **TODO-WINDOW1** — not rendered yet; single-count UX only.

### S-07 Production Actual (shell only)

- Thin form with fields stubbed in the visual layout. Submit button is disabled. Matches the v1.1 phase marker.

### S-08 My Submissions

- Merges fake local outbox entries with fake committed submissions. Retry/Discard buttons are shown on `queued` and `failed_retriable` rows; click handlers are stubs. Full envelope shape in `SubmissionDto` + `window2-portal-spec.md` §7.

### S-09 Forecast Workspace (Planning)

- Grid: rows × weekly buckets.
- **Features implemented:** family filtering (chips), cell edit, dirty-count tracking, family rollup totals.
- **Features flagged:** save, publish, discard, compare-versions — all buttons render but are not wired.
- **Stale banner:** a `DiffNotice` example renders when `staleDismissed = false` to show the pattern.
- **Concurrency:** **TODO-WINDOW1** — whether drafts are single global or per-user.

### S-10 Purchase Recommendations Review (Planning)

- Grouping by supplier. Per-row selection + bulk approve with confirm modal above N (mock N=10).
- Approve is local-only; a real approve/reject/hold triggers `POST /mutations/purchase-recommendations/:id/...` per `window2-portal-spec.md` §5.7.
- Staleness notice renders when a newer run lands.

### S-12 PO Form

- Prefilled from an approved recommendation (mock). Quantity edits require a per-line reason. Submit is disabled — **TODO-WINDOW5** whether the PO form goes through an API mutation or is split from rec approval in v1.

### S-02 Dashboard

- Four tiles + two read-only sections (shortage risk + freshness).
- Every number is from `SEED_DASHBOARD`. No drilldowns wired — clicking is safe but does not filter.

### S-03 Operator Home

- Three large action cards + recent submissions list.

### S-13 Exceptions Inbox

- Grouped by severity chip. Row expand shows detail + recommended action.
- Inline actions: acknowledge, resolve (prompts for note). Local-only state.

### S-14 Approvals Inbox

- Grouped by `ApprovalKind`. Row shows submitter, trigger reason, payload JSON preview. Approve/reject inline.

### S-15 Jobs Monitor

- Table with freshness, status, next run, enabled. Run-now button is disabled.

### S-22 Users Admin

- Search, role switcher, deactivate toggle. Immediate persistence via `usersRepo` (IndexedDB).

### S-23 Integrations Admin

- Three tiles (LionWheel, Shopify, Green Invoice) with resync/logs buttons disabled. Configuration UI deferred.

---

## 7. Validation UX rules

All forms follow the same pattern:

- **Inline field errors** — rendered under the field by `<Field error=… />`.
- **Top summary** — `ValidationSummary` aggregates all blockers and warnings. Renders above the first `SectionCard` when present. Shows blockers dominant → red, warnings dominant → yellow.
- **Blocker vs warning** — blockers disable submit and are highlighted red. Warnings allow submit but surface a visual cue (used for backdate warnings, over-receipt, large quantities).
- **Approval-needed banner** — `ApprovalBanner` renders when the current input *will* route the submission to approval. Reason and policy trigger are named explicitly. Shown *before* submit, so the operator is never surprised.
- **Stale / refresh-needed** — `DiffNotice` for version conflicts on planning screens and admin edits; `StaleNotice` for operator forms.
- **Duplicate / idempotency** — the outbox envelope carries a stable client idempotency key. Replay of a terminal submission renders `failed_terminal` with explicit Discard / Edit-and-resubmit choices. See `window2-portal-spec.md` §7.
- **Warning vs blocker policy:** backdate beyond the policy window is a warning, not a blocker — the operator may still post a back-dated receipt. Over-receipt is a warning with required confirm. Negative quantity is a blocker.
- **Positive-adjustment confirm modal:** native `window.confirm` for now. Replace with a custom modal when a shared dialog primitive lands.

---

## 8. Readiness matrix

| Screen                              | Shell now | Mock deep | Blocked on           | Notes                                                                 |
|-------------------------------------|-----------|-----------|----------------------|-----------------------------------------------------------------------|
| Login                               | ✓         | ✓         | Window 5 auth        | Fake-continue button routes to dashboard.                             |
| Dashboard                           | ✓         | ✓         | —                    | All tiles render from fixture; drilldowns not wired.                  |
| Operator Home                       | ✓         | ✓         | —                    | Quick actions + recent submissions.                                   |
| Goods Receipt                       | ✓         | ✓         | Ledger phase + API   | All 7 states forceable. Submit is mock.                               |
| Waste / Adjustment                  | ✓         | ✓         | Ledger phase + API   | Approval routing preview works off mock threshold.                    |
| Physical Count                      | ✓         | ✓         | Ledger phase + API   | Blind UX + variance branching work end to end in mock.                |
| Production Actual                   | ✓         | —         | Ledger phase (v1.1)  | Thin shell only. Submit disabled.                                     |
| My Submissions                      | ✓         | ✓         | —                    | Static fixture list with row actions stubbed.                         |
| Forecast Workspace                  | ✓         | ✓         | Planning/API         | Local cell edits work. Save/publish not wired.                        |
| Purchase Recommendations Review     | ✓         | ✓         | Planning/API         | Local approve works. Staleness banner pattern wired.                  |
| Production Recommendations Review   | ✓         | —         | Planning engine      | v1.1 placeholder only.                                                |
| PO Form                             | ✓         | —         | Planning/API         | Prefill shown. Submit disabled.                                       |
| Exceptions Inbox                    | ✓         | ✓         | —                    | Mock fixtures, local acknowledge/resolve.                             |
| Approvals Inbox                     | ✓         | ✓         | —                    | Mock fixtures, local approve/reject.                                  |
| Jobs Monitor                        | ✓         | ✓         | —                    | Read-only shell over fixture.                                         |
| Items Admin                         | ✓         | ✓         | —                    | Full CRUD against IndexedDB. Optimistic concurrency.                  |
| Components Admin                    | ✓         | ✓         | —                    | Full CRUD.                                                            |
| BOMs Admin                          | ✓         | ✓         | —                    | Nested versions + lines. Activate/retire flow.                        |
| Suppliers Admin                     | ✓         | ✓         | —                    | Full CRUD. Hebrew contact fields.                                     |
| Supplier-Items Mapping              | ✓         | ✓         | —                    | Quality gate for Green Invoice auto-update lives here.                |
| Planning Policy Admin               | ✓         | ✓         | —                    | Seed values match the thresholds the form shells reference.          |
| Users Admin                         | ✓         | ✓         | Window 5 auth        | Invitation flow deferred.                                             |
| Integrations Admin                  | ✓         | —         | Windows 3/5          | Three-card shell, buttons disabled.                                   |

Legend — Shell now: route + layout + skeleton renders. Mock deep: fully navigable with realistic fixtures and interactions (where applicable).

---

## 9. Implementation sequence for frontend-only work

> **Note (review round 2026-04-14):** this section described the build-time sequence. The runnable path, the test commands, and the pass results now live in `window2-acceptance-note.md`. Treat that note as the current source of truth for how to run and test this package; the list below is historical.

This is the order the current build was actually executed in, and the order to follow for any further frontend-only expansion before backend hookup:

1. **Install dependencies.** `cd portal && npm install`. No backend required.
2. **Run.** `npm run dev`. First visit seeds IndexedDB with fixtures in `SEED_*`. Reset via browser DevTools → IndexedDB → `gt-factory-os-portal` → delete, then reload.
3. **Review role-gating.** Use the top-bar FAKE SESSION chip to switch between operator, planner, admin, viewer. Nav shrinks appropriately. Protected routes render a "Not available for your role" card for wrong roles.
4. **Review shells state-by-state.** Open any operator form (`/ops/receipts`, `/ops/waste-adjustments`, `/ops/counts`), click the **Review mode** button in the top bar, and cycle the forced state through all seven values. The selected form re-renders the banner/card/form variant.
5. **Exercise master maintenance.** Add/edit/archive items, components, suppliers, supplier-items, policies. Navigate to BOMs and create a new draft, add lines, activate the version.
6. **Work the planning workspaces.** Forecast: edit cells, watch totals update, see the stale banner pattern. Purchase recs: select rows, try the bulk-approve confirm.
7. **Inboxes.** Exceptions and approvals both support local acknowledge/approve/reject. Nothing persists beyond the session.
8. **Next expansion work (no backend required):**
   - Add more per-item granularity to planning policy (per-item thresholds).
   - Add a stress-fixture variant for the forecast grid (more rows).
   - Add the Compare-versions dialog on the forecast workspace.
   - Add a hotkey binding for the review-mode panel.
   - Extract a shared Modal primitive and replace `window.confirm`/`window.prompt` usage.
9. **When backend hookup begins (Window 1 API):**
   - Replace `src/lib/repositories/*` with an `ApiRepo` implementation keyed to the same `Repository<T>` interface. The page code is already indirected through repositories.
   - Replace the mock submit handlers in operator forms with TanStack Query mutations against the confirmed API contracts in `window2-portal-spec.md` §5.
   - Swap `FakeSession` in `src/lib/auth/*` for a Supabase Auth session adapter. `RoleGate` and `useHasRole` stay identical.
   - Swap `SEED_DASHBOARD` / `SEED_FORECAST_DRAFT` / `SEED_PURCHASE_RECS` etc. for real read-model calls.

---

## 10. Explicit "not building yet" list

The following are deliberately not in this shell and require coordinated input before being built:

- **Any real network call, ever.** The portal is fully offline-capable in this build.
- **Real authentication.** No Supabase, no magic link, no JWT. Fake session only.
- **Any ledger posting, projection write, or planning computation.** Operator form submits are mock view swaps.
- **Real outbox replay.** The outbox envelope is specified in `window2-portal-spec.md` §7 and in `SubmissionDto`, but the portal does not yet run a reconciler loop against a server. Retry/Discard buttons on `/my-submissions` are stubs.
- **Real attachment upload.** Attachment fields are called out in the spec but not rendered in forms yet.
- **Ad-hoc PO creation.** PO form is downstream of recommendation approval only.
- **Cycle counting.** Only single-item counts render. Count-session orchestration is deferred.
- **Customer pricing, FEFO, location/bin tracking, RM batch workflows.** Explicitly out per the foundation doc.
- **Real-time concurrency (websockets, supabase realtime).** Concurrency is optimistic via version etags.
- **Visual design polish.** Functional layouts and consistent language, not brand design.
- **I18n infrastructure.** English-first UI is hard-coded. Hebrew appears only in fixture data values.
- **Tests.** ~~No unit/e2e/integration tests in this pass. Add vitest + Playwright when contracts are locked.~~ **Superseded 2026-04-14 (review round):** a minimum review-credibility test layer has since been added — Vitest unit tests for repositories and form validators, plus Playwright smoke tests for role switching, admin CRUD, form success state, forecast dirty edits, and review-mode state forcing. See the acceptance note (`window2-acceptance-note.md`) for commands and pass results. This package intentionally did not ship a test runner; the review round added one on top.
- **Error boundaries / global toast system.** Feedback states cover the important cases; a global toast provider lands when we have a real mutation surface to attach it to.
- **Forecast publish workflow with approval routing.** Button renders; no handler.
- **Production engine, production recommendations, production actual consumption backfill.** All v1.1 placeholders.

---

## 11. Cross-references

- `window2-portal-spec.md` — specification artifact from the previous session. Contains the per-screen field contract rigor, API contract proposals, outbox envelope, idempotency model, and full list of open coordination items for Windows 1 and 5.
- `GT_FACTORY_OS_PROJECT_FOUNDATION.md` — the authoritative locked-decision source.
- `CLAUDE.md` — project-level memory; stack locks and non-negotiables.

---

_End of Window 2 frontend package._
