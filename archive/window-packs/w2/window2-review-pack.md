# Window 2 — Review Pack

_Built 2026-04-14. Scope: evidence package only — the shell is frozen. No further building in this round._

This document is for rigorous review of the Window 2 frontend shell. It does not add behavior. It confirms what exists, proves it compiles, and draws clean lines around what is safe to polish vs. what must wait for other windows.

---

## 1. Location + boundary clarification

**Absolute path of the Window 2 portal package:**

```
c:\Users\tomw2\GTeveryday Dropbox\Data Center\Tom\AI Agents & Projects\Code Agents\PRODUCTION\portal
```

**Is it outside `gt-factory-os`?** Yes.

> **Superseded 2026-04-14 (review round):** the paragraphs immediately below this note understated the situation. A second and canonical `gt-factory-os` exists as a working git repo at `C:/Users/tomw2/Projects/gt-factory-os/`, and that repo **already has an active `portal/`** at `C:/Users/tomw2/Projects/gt-factory-os/portal/` currently at D2 (shared primitives) stage and being built by a separate work stream. Per the portal coordination note committed in that repo, the two portals are intentional parallel work streams with no merge plan. The single paragraph in the original review pack that said "there is no `portal/` subdirectory anywhere inside `gt-factory-os`" was scoped to the Dropbox-mirrored copy and missed the canonical clone. See `window2-acceptance-note.md` §1 for the full corrected workspace truth.

A separate `gt-factory-os` docs-only snapshot exists at:

```
c:\Users\tomw2\GTeveryday Dropbox\Data Center\Tom\AI Agents & Projects\Cowork Projects\Production & Finance\gt-factory-os
```

That snapshot has only `README.md`, `docs/`, `supabase/` — no `portal/`, no `.git/`, no `node_modules/`. It is not the canonical working repo; it is a Dropbox-synced doc mirror.

**File-path collision with `gt-factory-os/portal`?** ~~None.~~ **In the Dropbox docs mirror: none. In the canonical working clone at `C:/Users/tomw2/Projects/gt-factory-os/portal/`: the directory exists and is actively being built.** The two portals are independent work streams and do not overwrite each other because Window 2 is in `PRODUCTION/portal/` and the canonical portal is in `C:/Users/tomw2/Projects/gt-factory-os/portal/` — different filesystem locations, no shared files.

**Temporary review sandbox or future portal source?** Today, **it is a review sandbox**. My recommendation is to treat it as such until UX review is accepted, then port cleanly into `gt-factory-os/portal` when Windows 1/5 have locked enough backend surface that the port is worth doing. Full recommendation in §8.

**Environment surprise — flag:** the Dropbox path `GTeveryday Dropbox\Data Center\Tom\...` contains spaces that break npm's `napi-postinstall` script on Windows. `npm install` **cannot currently complete in place**. The portal installs and builds cleanly when copied to any space-free path (e.g. `C:\temp\gt_portal_review`). This affects local dev-server usability today. The packaged spec/code is not affected — only the install step. Two ways forward:
1. Move the portal to a space-free path (e.g. `C:\Work\gt-portal-shell`) and re-link from Dropbox via a shortcut or git clone.
2. Accept the install-from-temp-copy workflow (described in §7).

---

## 2. File tree

The real top-level layout of `PRODUCTION/portal/`:

```
portal/
├── .gitignore
├── next.config.mjs
├── package.json
├── postcss.config.mjs
├── tailwind.config.ts
├── tsconfig.json
└── src/
    ├── app/
    │   ├── globals.css
    │   ├── layout.tsx
    │   ├── page.tsx                              (redirects to /dashboard)
    │   ├── (auth)/
    │   │   └── login/page.tsx
    │   ├── (shared)/
    │   │   ├── layout.tsx
    │   │   ├── dashboard/page.tsx
    │   │   └── profile/page.tsx
    │   ├── (operator)/
    │   │   ├── layout.tsx
    │   │   ├── home/page.tsx
    │   │   ├── my-submissions/page.tsx
    │   │   └── ops/
    │   │       ├── counts/page.tsx
    │   │       ├── production-actual/page.tsx
    │   │       ├── receipts/page.tsx
    │   │       └── waste-adjustments/page.tsx
    │   ├── (planner)/
    │   │   ├── layout.tsx
    │   │   ├── approvals/page.tsx
    │   │   ├── exceptions/page.tsx
    │   │   ├── planning/
    │   │   │   ├── forecast/page.tsx
    │   │   │   ├── production-recommendations/page.tsx
    │   │   │   └── purchase-recommendations/page.tsx
    │   │   └── purchasing/po/page.tsx
    │   └── (admin)/
    │       ├── layout.tsx
    │       └── admin/
    │           ├── boms/page.tsx
    │           ├── components/page.tsx
    │           ├── integrations/page.tsx
    │           ├── items/page.tsx
    │           ├── jobs/page.tsx
    │           ├── planning-policy/page.tsx
    │           ├── supplier-items/page.tsx
    │           ├── suppliers/page.tsx
    │           └── users/page.tsx
    ├── components/
    │   ├── badges/
    │   │   ├── FreshnessBadge.tsx
    │   │   ├── ReadinessBadge.tsx
    │   │   └── StatusBadge.tsx
    │   ├── data/
    │   │   ├── AuditSnippet.tsx
    │   │   └── SearchFilterBar.tsx
    │   ├── feedback/
    │   │   └── states.tsx          (EmptyState, LoadingState, ErrorState, SuccessState, StaleNotice)
    │   ├── fields/
    │   │   ├── DateTimeInput.tsx
    │   │   ├── EntitySearchSelect.tsx
    │   │   ├── NotesBox.tsx
    │   │   ├── QuantityInput.tsx
    │   │   └── UomDisplay.tsx
    │   ├── layout/
    │   │   ├── AppPageShell.tsx
    │   │   ├── AppShellChrome.tsx
    │   │   ├── SideNav.tsx
    │   │   └── TopBar.tsx
    │   ├── line-editor/
    │   │   └── LineEditorTable.tsx
    │   ├── review/
    │   │   └── ReviewModePanel.tsx
    │   └── workflow/
    │       ├── ApprovalBanner.tsx
    │       ├── DiffNotice.tsx
    │       ├── FieldGrid.tsx       (Field + FieldGrid)
    │       ├── FormActionsBar.tsx
    │       ├── SectionCard.tsx
    │       ├── ValidationSummary.tsx
    │       └── WorkflowHeader.tsx
    ├── features/
    │   ├── master-data/
    │   │   └── SplitListLayout.tsx
    │   └── ops/
    │       └── StatePreviewChip.tsx
    └── lib/
        ├── cn.ts
        ├── auth/
        │   ├── fake-auth.ts
        │   ├── role-gate.tsx
        │   └── session-provider.tsx
        ├── contracts/
        │   ├── dto.ts
        │   └── enums.ts
        ├── fixtures/                  (this is where "mocks" live — see note)
        │   ├── approvals.ts
        │   ├── audit.ts
        │   ├── boms.ts
        │   ├── components.ts
        │   ├── dashboard.ts
        │   ├── exceptions.ts
        │   ├── forecast.ts
        │   ├── items.ts
        │   ├── jobs.ts
        │   ├── planning-policy.ts
        │   ├── recommendations.ts
        │   ├── submissions.ts
        │   ├── suppliers.ts
        │   └── users.ts
        ├── query/
        │   └── query-provider.tsx
        ├── repositories/              (swappable repo interface = the data-adapter layer)
        │   ├── boms-repo.ts
        │   ├── generic-repo.ts
        │   ├── idb.ts
        │   ├── index.ts
        │   ├── seed-gate.tsx
        │   ├── types.ts
        │   └── users-repo.ts
        └── review-mode/
            ├── store.tsx
            └── use-forced-state.ts
```

86 source files total.

**What is intentionally missing from this tree (matching the brief's checklist but absent from reality):**

| Directory / file          | Present? | Rationale                                                                                           |
|---------------------------|----------|-----------------------------------------------------------------------------------------------------|
| `mocks/`                  | **No**   | Per our prior decision (mock adapter pattern `C`, not MSW), mocks live inside `lib/fixtures/` (seed data) and `lib/repositories/` (IndexedDB swappable repo implementation). Easier to swap for real API later — one class, not a network interceptor. |
| `tests/`                  | **No**   | No unit/integration/e2e tests were written this round. Reason: shells are for UX review, not production guarantees. See §7 for what should exist before the shell is considered production-reviewable. |
| `playwright.config.ts`    | **No**   | No Playwright scaffold. Would land with the first `tests/e2e/` suite.                               |
| `vitest.config.ts`        | **No**   | No Vitest scaffold. Would land with the first `tests/unit/` suite.                                  |
| `docs/`                   | **No (inside portal/)** | Docs for this package live one level up at `PRODUCTION/window2-*.md`. There are no portal-internal docs. |
| `README.md` (in portal/)  | **No**   | CLAUDE.md discourages unrequested doc files. Consumers read `PRODUCTION/window2-*.md` instead.      |

**Project-level documentation files in `PRODUCTION/`:**

```
PRODUCTION/
├── GT_Factory_OS.xlsx          (legacy workbook)
├── GT_Master_Data.xlsx         (legacy master data)
├── claude.md                   (project memory — see CLAUDE.md)
├── window2-portal-spec.md      (54 kB — original architectural spec from first session)
├── window2-frontend-package.md (36 kB — delivered-package spec from build session)
└── window2-review-pack.md      (this document)
```

---

## 3. Route inventory

All 28 routes compile cleanly (`next build` output in §7). Grouped as requested. Each route is marked with four independent flags:

- **Depth** — `shell only` · `mock-interactive` · `deep-mock`
- **Write path** — `no submit` · `mock submit (view swap)` · `persisted to IndexedDB`
- **Backend block** — none · `backend contract` · `ledger phase` · `planning engine` · `auth (Window 5)`
- **Notes**

### A. Admin Maintenance

| Route                             | Depth            | Write path                | Backend block | Notes                                                                 |
|-----------------------------------|------------------|---------------------------|---------------|-----------------------------------------------------------------------|
| `/admin/items`                    | deep-mock        | persisted to IndexedDB    | none          | Full CRUD, optimistic concurrency via `audit.version`, archive toggle |
| `/admin/components`               | deep-mock        | persisted to IndexedDB    | none          | Full CRUD, primary supplier pick                                      |
| `/admin/boms`                     | deep-mock        | persisted to IndexedDB    | none          | Nested head→version→lines. New-draft / activate / line-edit          |
| `/admin/suppliers`                | deep-mock        | persisted to IndexedDB    | none          | Full CRUD, Hebrew contact fields                                      |
| `/admin/supplier-items`           | deep-mock        | persisted to IndexedDB    | none          | Mapping quality gate; `confirmed` is the only state that would allow Green Invoice auto-update in production |
| `/admin/planning-policy`          | deep-mock        | persisted to IndexedDB    | none          | Seed values match thresholds referenced by operator form shells       |
| `/admin/users`                    | deep-mock        | persisted to IndexedDB    | auth (Window 5) | Role switcher + deactivate; invitation flow deferred to Supabase Auth |
| `/admin/jobs`                     | mock-interactive | no submit                 | backend contract | Read-only list of scheduled jobs; Run-now button disabled           |
| `/admin/integrations`             | shell only       | no submit                 | backend contract | Three-tile placeholder for LionWheel / Shopify / Green Invoice       |

### B. Operator Forms

| Route                             | Depth            | Write path        | Backend block              | Notes                                                                 |
|-----------------------------------|------------------|-------------------|----------------------------|-----------------------------------------------------------------------|
| `/ops/receipts`                   | mock-interactive | mock submit (view swap) | ledger phase + backend contract | All 7 screen states forceable via review mode. Submit is a view swap. |
| `/ops/waste-adjustments`          | mock-interactive | mock submit (view swap) | ledger phase + backend contract | Positive-direction confirm + approval-preview banner work offline     |
| `/ops/counts`                     | mock-interactive | mock submit (view swap) | ledger phase + backend contract | Blind UX enforced. Mock variance calculation decides outcome locally. |
| `/ops/production-actual`          | shell only       | no submit (disabled) | ledger phase (v1.1)        | Thin shell; submit disabled; slice reserved                           |
| `/purchasing/po`                  | shell only       | no submit (disabled) | backend contract           | Prefilled from mock recommendation; submit disabled                   |

### C. Planning Screens

| Route                                        | Depth            | Write path         | Backend block           | Notes                                                                 |
|----------------------------------------------|------------------|--------------------|-------------------------|-----------------------------------------------------------------------|
| `/planning/forecast`                         | mock-interactive | local cell edits (not persisted) | backend contract  | Grid editor with dirty tracking; save/publish/discard UI present but unwired |
| `/planning/purchase-recommendations`         | mock-interactive | local row actions (not persisted) | planning engine + backend contract | Bulk-approve confirm modal trips above mock threshold (10 lines) |
| `/planning/production-recommendations`       | shell only       | no submit          | planning engine         | v1.1 slice; empty-state card                                          |

### D. Dashboard / Exceptions / Approvals / Utilities

| Route                    | Depth            | Write path        | Backend block    | Notes                                                                 |
|--------------------------|------------------|-------------------|------------------|-----------------------------------------------------------------------|
| `/dashboard`             | deep-mock        | no submit         | none             | 4 tiles + shortage-risk list + freshness cluster                      |
| `/home` (operator home)  | mock-interactive | no submit         | none             | Quick actions + recent-submissions preview                            |
| `/my-submissions`        | mock-interactive | local row actions | backend contract | Fake outbox + committed merge; Retry/Discard stubs                    |
| `/exceptions`            | deep-mock        | local row actions | backend contract | Acknowledge/resolve locally; note-prompt uses `window.prompt`         |
| `/approvals`             | deep-mock        | local row actions | backend contract | Approve/reject locally; JSON payload preview                          |
| `/profile`               | shell only       | no submit         | auth (Window 5)  | Read-only fake session dump                                           |
| `/login`                 | shell only       | no submit         | auth (Window 5)  | "Continue with fake session" button                                   |
| `/`                      | shell only       | n/a (redirect)    | —                | Redirects to `/dashboard`                                             |
| `/_not-found`            | (built-in)       | n/a               | —                | Next default                                                          |

**Counts:** 28 routes total. 9 admin (6 full-CRUD + 1 user CRUD + 2 read-only), 5 operator forms (3 interactive, 2 thin), 3 planning (2 interactive, 1 thin), 8 dashboard/inbox/utility, 3 structural (root, login, not-found).

---

## 4. Screen evidence pack

Visual evidence is **structured visual summaries** — I did not take screenshots because that requires running a dev server with browser automation, which is out of scope for this freeze round. Each priority screen below has: visual layout summary, state coverage table, and role visibility notes.

The 13 priority screens follow. All layouts are inside the standard shell chrome (top bar with brand + FAKE SESSION chip; left side nav grouped Overview / Operations / Planning / Purchasing / Admin — Master Data / Admin — System).

---

### 4.1 Items (`/admin/items`) — Admin Maintenance

```
┌ Master data ─────────────────────────────────────────────────────┐
│ Items                                           [+ New item]    │
│ Finished goods, components, packaging, and raw materials.       │
│ Structural changes may affect planning.                         │
├──────────────────────────────────────────────────────────────────┤
│  LIST (1fr)                      │  DETAIL (420px, xl:sticky)    │
│ ┌──────────────────────────────┐│ ┌───────────────────────────┐  │
│ │ 8 items                      ││ │ New item / selected item  │  │
│ │ Click a row to edit.         ││ │                    [Close]│  │
│ │ [search] [finished_good]…    ││ │ ┌ ValidationSummary? ┐    │  │
│ │                              ││ │ FieldGrid columns=2:      │  │
│ │ ┌────────────────────────┐   ││ │  SKU*      Name*          │  │
│ │ │ SKU  Name  Kind …      │   ││ │  Local name (span 2)      │  │
│ │ │ FG-MOJ-450 Mojito 450 …│   ││ │  Kind*     Supply*        │  │
│ │ │ …                      │   ││ │  Default UoM*  Lead       │  │
│ │ └────────────────────────┘   ││ │  Min  Reorder  Target     │  │
│ └──────────────────────────────┘│ │  Notes (span 2)           │  │
│                                  │ │ [Audit details ▸]         │  │
│                                  │ │ ┌ FormActionsBar ────┐    │  │
│                                  │ │  [Archive] [Save chng]│   │  │
│                                  │ └───────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

**State coverage:**

| State               | Rendered? | How to see it                                                                                   |
|---------------------|-----------|-------------------------------------------------------------------------------------------------|
| empty               | yes       | Apply a filter that yields 0 rows → "No items match the current filters."                       |
| loading             | yes       | React Query loading → "Loading…" placeholder inside the SectionCard                              |
| validation error    | yes       | Open "New item", leave SKU/Name blank → inline field errors + top `ValidationSummary` (blockers) |
| submission pending  | partial   | No spinner on the button yet; the mutation is near-instant on IndexedDB                          |
| success             | yes       | Save succeeds → detail panel stays open with fresh `audit.version` bumped                        |
| approval required   | n/a       | Admin maintenance does not route through approval                                                |
| stale / conflict    | yes       | Concurrent update in another tab triggers `RepoError("stale")` from `GenericIdbRepo.update`      |

**Role visibility:** admin W, planner R (read-only — writes blocked at API boundary when the real backend lands; the current mock allows planner clicks since RoleGate is surface-level), operator/viewer —.

---

### 4.2 Components (`/admin/components`) — Admin Maintenance

```
┌ Master data ─────────────────────────────────────────────────────┐
│ Components                                  [+ New component]   │
│ Raw materials, packaging, and sub-components consumed by BOMs.   │
├──────────────────────────────────────────────────────────────────┤
│ LIST                              │ DETAIL                       │
│ [search] [component][raw_m][pkg]  │ Code*   Name*                │
│ Table: Code Name Kind UoM         │ Local name (Hebrew, dir=auto)│
│   Primary supplier  Price         │ Kind*   UoM*  Primary supp.  │
│ 20 seeded components              │ Lead days  Density (kg/L)    │
│ (rum/tequila/juices/bottles/caps/ │ Notes                        │
│  labels/cases)                    │ [Archive] [Save]             │
└──────────────────────────────────────────────────────────────────┘
```

**State coverage:** same pattern as Items (empty / loading / validation_error / success / stale). No approval path.

**Role visibility:** admin W, planner R. Others —.

---

### 4.3 BOMs (`/admin/boms`) — Admin Maintenance (nested)

```
┌ Master data ─────────────────────────────────────────────────────┐
│ Bills of materials                              [+ New BOM]      │
│ Versioned BOMs per finished-good item. New versions are drafted, │
│ edited, then activated. Historical production postings keep      │
│ their original pinning.                                          │
├──────────────────────────────────────────────────────────────────┤
│ LIST                              │ DETAIL (for selected BOM)    │
│ ┌─────────────────────────────┐  │ ┌─────────────────────────┐   │
│ │ Item  Active  Lines Versions│  │ │ Item name               │   │
│ │ Mojito cocktail  v1   7   [v1·active]│ │ Versions: [v1·draft]  │   │
│ │ Peach iced tea   v2   5   [v1·retired][v2·active] │       │   │
│ │ Margarita        v1   6   [v1·active]│ [+ New draft from latest]│   │
│ │ Mint iced tea    v1   4   [v1·active]│                         │   │
│ └─────────────────────────────┘  │ If viewing non-draft:        │   │
│                                    │   ApprovalBanner(tone=info)  │   │
│                                    │   "Lines are read-only…"     │   │
│                                    │                              │   │
│                                    │ LineEditorTable (draft: editable, else read) │
│                                    │  # Component  Qty per  UoM  Scrap │          │
│                                    │  [+ Add BOM line] (only on draft) │          │
│                                    │                                               │
│                                    │ Audit collapsed                              │
│                                    │ FormActionsBar:                              │
│                                    │  draft dirty?  [Save draft lines]            │
│                                    │  draft clean?  [Activate version]            │
│                                    │  non-draft     [Start new draft]             │
└──────────────────────────────────────────────────────────────────┘
```

**Structural-change invariant enforced in the mock:** only DRAFT versions allow line edits. Activating a version retires the current active. Creating a new draft clones lines from the latest version.

**State coverage:**

| State               | Rendered? | How                                                                                             |
|---------------------|-----------|-------------------------------------------------------------------------------------------------|
| empty               | yes       | List empty (fresh DB wipe) → empty table row                                                    |
| loading             | yes       | React Query                                                                                     |
| validation error    | partial   | Client blocks negative qty at input type level; a server-side line check is not yet enforced.   |
| success             | yes       | Save lines → toast-free; dirty flag clears; version bump visible in audit                       |
| approval required   | n/a       | Activation policy does not currently include an approval step — **TODO-WINDOW1** to confirm     |
| stale / conflict    | yes       | Concurrent update bumps head version → `RepoError("stale")` surfaces from the mutation hook     |

**Role visibility:** admin W, planner R, others —.

---

### 4.4 Suppliers (`/admin/suppliers`) — Admin Maintenance

```
┌ Master data ─────────────────────────────────────────────────────┐
│ Suppliers                                  [+ New supplier]     │
├──────────────────────────────────────────────────────────────────┤
│ LIST                              │ DETAIL                       │
│ [search]                          │ Code*   Name*                │
│ Code  Name  Contact  Terms  Lead  │ Local name (Hebrew)          │
│   Status                          │ Contact person/phone/email   │
│ 9 seed suppliers (Shikarei        │ Address  Currency*           │
│ Eliyahu, Prigat, Phoenicia, …     │ Terms  Lead days  Notes      │
│ all with Hebrew display strings)  │ [Archive] [Save]             │
└──────────────────────────────────────────────────────────────────┘
```

**Hebrew data invariant:** `name_local`, `contact_person`, `address` fields accept Hebrew with `dir="auto"`. UI chrome remains English. Per CLAUDE.md language rule.

**State coverage:** empty / loading / validation_error (email format) / success / stale — all wired.

**Role visibility:** admin W, planner R, others —.

---

### 4.5 Supplier-items mapping (`/admin/supplier-items`) — Admin Maintenance

```
┌ Master data ─────────────────────────────────────────────────────┐
│ Supplier ↔ Component mapping           [+ New mapping]          │
│ Mapping quality gates Green Invoice auto price updates.          │
│ Unmapped = no auto-update.                                       │
├──────────────────────────────────────────────────────────────────┤
│ LIST                              │ DETAIL                       │
│ [search] [confirmed][probable][unmapped] │ Supplier*  Component*  │
│ Supplier  Component  SKU  Pack    │ Supplier SKU  Pack / unit    │
│   Price  Preferred  Quality       │ Price amount / currency /    │
│                                    │  unit                        │
│ 13 seed mappings, mix of          │ Mapping quality*             │
│  confirmed / probable             │ Preferred (checkbox)         │
└──────────────────────────────────────────────────────────────────┘
```

**Key invariant enforced in the mock:** `mapping_quality` is captured but not yet referenced by any auto-update logic (logic lives server-side in production). The admin surface stores the gate.

**State coverage:** same CRUD pattern (empty, loading, validation_error, success, stale).

**Role visibility:** admin W, planner R, others —.

---

### 4.6 Planning policy (`/admin/planning-policy`) — Admin Maintenance

```
┌ Master data ─────────────────────────────────────────────────────┐
│ Planning policy                             [+ New policy]       │
│ Thresholds and behavior flags consumed by forms, planning        │
│ engine, and integrations.                                        │
├──────────────────────────────────────────────────────────────────┤
│ Key                         Description           Scope  Value   │
│ adjustment.auto_post.small  Small waste…         global  5 (num) │
│ adjustment.approval.large   Adjustment >= …      global  25 (num)│
│ adjustment.positive.always  Positive always app. global  true    │
│ count.variance.auto_post_pct Variance under…     global  5 (num) │
│ …                                                                │
│                                                                   │
│ Detail: Key, Description, value_type, Value (adapts to type),    │
│   Scope (global/item/supplier/reason), Scope ref                 │
└──────────────────────────────────────────────────────────────────┘
```

**Seeded values cross-reference:** these are the exact thresholds the operator form shells use for their approval-preview banners (25 for large losses, boolean true for positive-always-approve, 5% for count variance). Changing a policy value in the admin UI does NOT yet flow into the form shells at runtime — they read a hardcoded mock constant. **Rewire is a §6A polishing task once Window 1 confirms the policy-read API.**

**Role visibility:** admin W, planner R, others —.

---

### 4.7 Goods Receipt (`/ops/receipts`) — Operational Form shell

```
┌ Operator form ───────────────────────────────────────────────────┐
│ Goods Receipt                                                    │
│ Record physical goods arrival. Partial receipts are valid.       │
│ Submission behavior is mocked in this shell build.               │
│                                                                   │
│ [StatePreviewChip when review mode is forcing a state]           │
│                                                                   │
│ ┌ Receipt context ──────────────────────────────────────────┐    │
│ │ Event time*    Supplier*                                  │    │
│ │ Open PO         Header notes                              │    │
│ └───────────────────────────────────────────────────────────┘    │
│                                                                   │
│ ┌ Lines ────────────────────────────────────────────────────┐    │
│ │ LineEditorTable:                                          │    │
│ │  # Item       Quantity UoM  Notes  [✕]                    │    │
│ │ [+ Add receipt line]                                      │    │
│ └───────────────────────────────────────────────────────────┘    │
│                                                                   │
│ ┌ TODO-WINDOW1 DevNote ─────────────────────────────────────┐    │
│ │  • POST /mutations/goods-receipts envelope                │    │
│ │  • attachment storage model                               │    │
│ │  • over-receipt / extra-line semantics                    │    │
│ │  • backdate warning threshold                             │    │
│ └───────────────────────────────────────────────────────────┘    │
│                                                                   │
│ ┌ FormActionsBar ─────────────── [Reset] [Submit receipt] ──┐    │
└──────────────────────────────────────────────────────────────────┘
```

**State coverage — all seven forceable via the review-mode panel:**

| State               | Rendered as                                                                                          |
|---------------------|------------------------------------------------------------------------------------------------------|
| empty               | `EmptyState` card: "No goods to receive yet"                                                         |
| loading             | `LoadingState`: "Loading masters…"                                                                   |
| validation error    | `ValidationSummary` above form with blocker list + inline per-field errors                           |
| submission pending  | `LoadingState`: "Submitting…"                                                                        |
| success             | `SuccessState` (tone=success): mock confirmation card with "Record another receipt" action          |
| approval required   | `SuccessState` (tone=warning): "Held for review"                                                     |
| stale / conflict    | `StaleNotice`: "PO state changed" with "Back to form" button                                         |

**Submit invariant:** the handler is intentionally a no-op that only swaps `view` to `success`. No ledger contact. No network call. No `fetch` anywhere.

**Role visibility:** operator W. Planner/admin/viewer can open but see the "Not available for your role" card from `RoleGate`.

---

### 4.8 Waste / Adjustment (`/ops/waste-adjustments`) — Operational Form shell

```
┌ Operator form ───────────────────────────────────────────────────┐
│ Waste / Adjustment                                               │
│                                                                   │
│ ┌ Direction (asymmetric) ──────────────────────────────────┐     │
│ │ [●] Loss / write-down      [ ] Positive correction       │     │
│ │ Normal: breakage, …        Exceptional: always approval  │     │
│ │                            (warning border if selected)  │     │
│ └──────────────────────────────────────────────────────────┘     │
│                                                                   │
│ ┌ Adjustment ──────────────────────────────────────────────┐     │
│ │ Event time*   Item*                                      │     │
│ │ Quantity*     Unit                                       │     │
│ │ Reason*       Notes (required for positive / "other")    │     │
│ └──────────────────────────────────────────────────────────┘     │
│                                                                   │
│ [ApprovalBanner if quantity >= 25 or direction = positive]       │
│   "This adjustment will be held for planner approval"            │
│   reason + policy trigger key                                    │
│                                                                   │
│ ┌ FormActionsBar ────────────── [Reset] [Submit adjustment] ──┐  │
└──────────────────────────────────────────────────────────────────┘
```

**Key invariants enforced in the mock:**
1. Positive direction triggers a required `window.confirm` modal before view-swap.
2. Positive direction OR quantity above mock threshold (25) pre-shows `ApprovalBanner` before submit — operator is never surprised.
3. Notes required when `direction = positive` OR `reason = other` — enforced by the zod refine.

**State coverage:** all seven forceable.

**Role visibility:** operator W only.

---

### 4.9 Physical Count (`/ops/counts`) — Operational Form shell (blind UX)

```
┌ Operator form ───────────────────────────────────────────────────┐
│ Physical Count                                                   │
│ Blind full-count variant. System quantity is hidden until submit.│
│                                                                   │
│ [ApprovalBanner tone=info]                                       │
│ "Blind count: System qty is hidden until you submit."            │
│                                                                   │
│ ┌ Count ────────────────────────────────────────────────────┐    │
│ │ Event time*   Item*                                       │    │
│ │ Counted quantity* (zero is valid)   Unit                  │    │
│ │ Notes                                                     │    │
│ └───────────────────────────────────────────────────────────┘    │
│                                                                   │
│ ┌ FormActionsBar ────────────── [Reset] [Submit count] ────┐     │
└──────────────────────────────────────────────────────────────────┘
```

**After submit, outcome branches:**

| Outcome                       | Mock rule                           | Visual                                                    |
|-------------------------------|-------------------------------------|-----------------------------------------------------------|
| matched                       | `abs(delta) < 0.001`                | `SuccessState` (success tone): "Count matches system"     |
| small variance (auto-post)    | `pct <= 5%` or `abs(delta) <= 2`    | `SuccessState` (warning tone): counted vs system vs delta |
| large variance (approval)     | else                                | `SuccessState` (warning tone): "Variance held for approval" |
| conflict                      | (not wired; forceable)              | `StaleNotice`                                             |

**Blind-UX invariant enforced:** the component never reads `MOCK_SYSTEM_QTY` until the submit handler runs. Pre-submit rendering has no access to system quantity. The invariant is visible in the code — there is no expression in the JSX that references `MOCK_SYSTEM_QTY`.

**Role visibility:** operator W only.

---

### 4.10 Forecast workspace (`/planning/forecast`) — Planning Workspace shell

```
┌ Planning workspace ─────────────────────────────────────────────┐
│ Forecast                                                        │
│ Judgment workspace over forecast_versions. Multi-cell editing   │
│ with versioning. This is a planning surface — not a form.       │
│                                                                  │
│ meta: [draft v7] [horizon 8w] [week]  [Freshness: 10m ago]      │
│ actions: [Discard draft] [Save draft] [Publish version]         │
│                                                                  │
│ [DiffNotice: "Draft changed by another planner at 11:08"]       │
│ [ApprovalBanner: "Publish requires approval"]                   │
│                                                                  │
│ 8 rows · 8 weekly buckets                [all][Cocktails]…      │
│ ┌─ Cocktails ─────────────────────────────────────────┐         │
│ │ Item           W17  W18  W19  W20  W21  W22 W23 W24 Tot │     │
│ │ Mojito 450     240  260  300  320  360  380 420 440 … │     │
│ │ Margarita 450  180  200  220  240  260  280 300 320 … │     │
│ │ Piña colada    120  140  160  180  180  180 200 200 … │     │
│ │ (family total) 540  600  680  740  800  840 920 960 … │     │
│ └───────────────────────────────────────────────────────┘     │
│ (Teas / Smoothies / Lemonades similar)                        │
│                                                                  │
│ Zero cells render as "—" (muted). Editing is inline per cell.  │
│                                                                  │
│ ┌ FormActionsBar ─────────────────────────────────────────────┐ │
│ │ "3 local cell edits pending save"   [Save 3 changes]        │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**Workspace invariants enforced locally:**
1. Not a form — there is no single submit envelope. Dirty count tracks accumulated cell edits; save/publish are distinct actions.
2. Family totals are derived, not edited — family-level editing is out of v1.
3. Zero cells render as "—" but are still stored as `0`. Empty cells are forbidden (zero-or-positive numeric input).

**State coverage:**

| State               | Rendered as                                                                                         |
|---------------------|-----------------------------------------------------------------------------------------------------|
| empty               | If no draft exists: "Start new draft from latest published" CTA (not triggered in mock)             |
| loading             | `SeedGate` renders `LoadingState` before IDB seeds                                                   |
| validation error    | Negative cell blocked at input-level (html `min=0`)                                                  |
| save pending        | Toolbar button state; save handler is unwired                                                        |
| success             | Save handler unwired — lands as a no-op in the mock                                                  |
| approval required   | `ApprovalBanner` visible at all times as a pattern example                                           |
| stale / conflict    | `DiffNotice` with Reload / Dismiss; can be re-shown by clearing `staleDismissed`                     |

**Role visibility:** planner W, admin R, viewer R, operator —.

---

### 4.11 Purchase recommendations review (`/planning/purchase-recommendations`) — Planning Workspace shell

```
┌ Planning workspace ─────────────────────────────────────────────┐
│ Purchase recommendations                                        │
│ meta: [Freshness: 7h ago] [run 2026-04-14] [8 pending · 0 sel.] │
│                                                                  │
│ [SearchFilterBar]  [critical][high][normal][low]                │
│                                                                  │
│ Grouped by supplier, 7 groups visible in mock:                  │
│                                                                  │
│ ┌ Mishtalot HaGalil                           [1 line] ──┐      │
│ │ ☐  Component  Recommend  On hand  Target    Urgency … │      │
│ │ ☐ Fresh mint  8 kg       0.6 kg   2026-04-16 [crit]  … │      │
│ └─────────────────────────────────────────────────────────┘      │
│ ┌ Prigat Citrus Cooperative                  [1 line] ──┐       │
│ │ ☐ Fresh lime  40 L       9.4 L    2026-04-17 [high]  … │       │
│ └─────────────────────────────────────────────────────────┘      │
│ (Tovalim Press / Phoenicia x2 / Sugat / Shikarei / Carton Tamir)│
│                                                                  │
│ ┌ FormActionsBar ─────────────────────────────────────────────┐ │
│ │ [N selected]  [Reject selected…] [Hold]  [Approve selected] │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**Workspace invariants enforced locally:**
1. Bulk approve of more than 10 lines → `window.confirm` modal.
2. "Approve selected" optimistically updates local state; no server call.
3. Staleness-detection banner pattern wired (currently dismissed by default; toggle `staleDismissed = false` to see it).

**Role visibility:** planner W, admin R, viewer R, operator —.

---

### 4.12 Dashboard (`/dashboard`) — Read-only Decision Surface

```
┌ Control tower ──────────────────────────────────────────────────┐
│ Dashboard                                                       │
│ Read-only. Tiles drill into filtered read models. This surface  │
│ never writes.                                                   │
├─────────────────────────────────────────────────────────────────┤
│  ┌─ Stock health ─┐┌─ Planning run ┐┌─ Exceptions ─┐┌─ Ready ─┐│
│  │ 28             ││ 18            ││  6           ││ …       ││
│  │ [3 short][2 ov]││ recs latest   ││ [1 crit][3w] ││ Ledger W││
│  │ [23 healthy]   ││ [4 flagged]   ││ [2 info]     ││ Jobs W  ││
│  └────────────────┘└───────────────┘└──────────────┘└─────────┘│
│                                                                  │
│ ┌ Shortage risk (2fr) ────────────┐ ┌ Freshness (1fr) ───────┐ │
│ │  Fresh mint leaves   [1d]       │ │ Ledger: 5m ago         │ │
│ │  Fresh lime juice    [3d]       │ │ LionWheel: 1h warn     │ │
│ │  Label — Mojito      [5d]       │ │ Shopify: 32m           │ │
│ │  Mojito cocktail     [6d]       │ │ Green Invoice: 5h      │ │
│ └─────────────────────────────────┘ └────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**State coverage:** loading (before seed), success (current). No submit states — this is read-only. "Partial failure per-tile" is a spec rule but not yet wired; all tiles render from one synchronous fixture.

**Role visibility:** all authenticated roles R.

---

### 4.13 Exceptions inbox (`/exceptions`) — Read-only Decision Surface with actions

```
┌ Planner inbox ──────────────────────────────────────────────────┐
│ Exceptions                                                      │
│ Triage exceptions emitted by jobs, integrations, and integrity  │
│ checks.                                                          │
├─────────────────────────────────────────────────────────────────┤
│ [search] [critical][warning][info] [open only / all statuses]   │
│                                                                  │
│ Expandable row list (click to expand):                          │
│ ▸ [warning] integration.lionwheel [open]                        │
│   LionWheel sync stale                                          │
│   2026-04-14 11:00                                              │
│ ▸ [warning] price.greeninvoice [open]                           │
│   Price change above threshold — Cane sugar                    │
│ ▾ [critical] ledger.integrity [ack]                             │
│   Projection mismatch — Fresh lime juice                       │
│   ┌ expanded: detail + Recommended action card ──┐             │
│   │ Run projection verification job…              │             │
│   │ [Acknowledge] [Resolve with note]             │             │
│   └───────────────────────────────────────────────┘             │
│ ▸ [info] form.duplicate [resolved]                             │
│ ▸ [warning] job.scheduled [open]                                │
│ ▸ [info] planning.demand [open]                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Row actions:** Acknowledge (sets status to `acknowledged` locally), Resolve with note (uses `window.prompt` for note, sets `resolved`). Local-only.

**Role visibility:** planner W, admin R, operator/viewer —.

---

### 4.14 Approvals inbox (`/approvals`) — Read-only Decision Surface with actions

```
┌ Planner inbox ──────────────────────────────────────────────────┐
│ Approvals                                                       │
│ Items awaiting planner review. Each row expands to show the     │
│ full submission payload and policy trigger.                     │
├─────────────────────────────────────────────────────────────────┤
│ Grouped by ApprovalKind:                                        │
│                                                                  │
│ ┌ waste_adjustment (2 pending) ────────────────────────┐        │
│ │ operator Avi Cohen  2026-04-14 10:20                 │        │
│ │ Positive correction — White rum 37.5% +4 L (found)   │        │
│ │ Trigger: Policy: positive-direction always requires… │        │
│ │ [▸ Payload preview]                                  │        │
│ │                                    [Approve] [Reject]│        │
│ │                                                      │        │
│ │ operator Avi Cohen  2026-04-13 16:40                 │        │
│ │ Loss — Silver tequila 38% −30 L (shrinkage)          │        │
│ │ Trigger: Qty 30 L exceeds 25-unit threshold          │        │
│ └──────────────────────────────────────────────────────┘        │
│                                                                  │
│ ┌ physical_count_variance (1 pending) ────────────────┐         │
│ │ operator Noa Peled  Count variance — Cane sugar …   │         │
│ │ [Approve] [Reject]                                  │         │
│ └──────────────────────────────────────────────────────┘        │
│                                                                  │
│ ┌ forecast_publish (1 pending) ────────────────────────┐        │
│ │ planner Tom — Publish forecast draft v7              │        │
│ │ [Approve] [Reject]                                   │        │
│ └──────────────────────────────────────────────────────┘        │
│                                                                  │
│ [Session summary badges: N approved, N rejected]                │
└─────────────────────────────────────────────────────────────────┘
```

**Row actions:** Approve (sets local `approved`), Reject (prompts for reason, sets `rejected`). Local-only.

**Role visibility:** planner W, admin R, operator/viewer —.

---

## 5. Contract summary

For each feature area: **what is mocked** (local implementation), **what invariant the mock enforces** (rules the shell does not let you violate), **what backend contract is still assumed** (API surface Window 1 owes us), **what is deliberately deferred**.

### 5.1 Authentication

- **Mocked:** `FakeSession` + role switcher chip in top bar; localStorage-persisted choice; `SessionProvider` context; `RoleGate` component that renders a "Not available for your role" card on mismatch.
- **Invariant enforced:** role gate runs on every route-group layout (`(operator)/layout.tsx`, `(planner)/layout.tsx`, `(admin)/layout.tsx`, `(shared)/layout.tsx`). Nav items suppressed for wrong role. No silent bypass.
- **Backend contract assumed:** Supabase magic-link session; role claim location (`user_metadata.role` vs custom JWT claim) — `TODO-WINDOW1`/`TODO-WINDOW5`.
- **Deferred:** real sign-in, sign-out, password reset, invitation flow, MFA (explicitly out per foundation doc).

### 5.2 Master data (items, components, BOMs, suppliers, supplier-items, policy, users)

- **Mocked:** `GenericIdbRepo<T>` + `IdbBomsRepo` + `usersRepo` persisting to `gt-factory-os-portal` IndexedDB. Fixtures seed on first load via `SeedGate`. All CRUD flows work.
- **Invariants enforced in the mock:**
  - Optimistic concurrency: every update checks `audit.version` before writing; `RepoError("stale")` on mismatch.
  - Audit bump: every update increments `audit.version` and updates `audit.updated_at`/`audit.updated_by`.
  - Soft delete only: `setActive(id, false)` flips `audit.active`; rows never leave the store.
  - BOM versioning: only `draft` versions accept line edits; activation retires the previous active.
  - Supplier-item mapping quality is captured but not referenced by any auto-update logic (Green Invoice auto-update lives server-side).
- **Backend contract assumed:**
  - `GET/POST/PATCH /admin/<domain>` with `audit.version` etag.
  - Server-side uniqueness on SKU/code/key.
  - Server-side enforcement of the mapping-quality rule for price auto-updates.
  - BOM activation may require approval server-side — **TODO-WINDOW1**.
  - User creation/invitation flows through Supabase Auth API, not this repo.
- **Deferred:** bulk import, CSV export beyond the nightly XLSX job, supplier returns, FEFO/expiry, location/bin modelling.

### 5.3 Operator forms (Goods Receipt, Waste/Adjustment, Physical Count)

- **Mocked:** three RHF+zod forms, each with the full seven-state catalogue forceable via the review-mode panel. Submit is a client-side view swap; no network call.
- **Invariants enforced in the mock:**
  - **Receipts:** quantity > 0 per line; ≥1 line; supplier required.
  - **Waste/Adjustment:** positive-direction path is visually asymmetric; positive direction triggers a `window.confirm` before view-swap; notes required for positive or `reason = other`; approval-preview banner renders when quantity ≥ mock threshold or direction = positive.
  - **Physical Count:** blind UX — no code path in JSX references `MOCK_SYSTEM_QTY` pre-submit; outcome is computed only after submit.
  - Client-generated idempotency key per logical submission (stub at DTO level).
- **Backend contract assumed (from `window2-portal-spec.md` §5):**
  - `POST /mutations/goods-receipts`, `/mutations/waste-adjustments`, `/mutations/physical-counts`.
  - Idempotency key dedup at the server.
  - Response envelope states: `committed`, `pending_approval`, `conflict`, `validation`, variance sub-types for counts.
  - Policy-read surface (thresholds) — currently hardcoded constants in the form components.
- **Deferred:** real outbox replay, attachment uploads, count-session orchestration, RM batch capture on receipts.

### 5.4 Planning workspaces (forecast, purchase recs)

- **Mocked:** forecast grid with in-memory cell edits and family totals; purchase recs grouped by supplier with local approve/reject/hold and bulk-approve confirm.
- **Invariants enforced in the mock:**
  - Forecast is **not a form** — no single submit intent; save/publish are distinct actions.
  - Forecast cells are non-negative; zero renders as "—" but stores as `0`.
  - Family totals are derived, not editable.
  - Bulk-approve above N=10 triggers `window.confirm`.
  - Staleness detection renders `DiffNotice` when a newer version lands.
- **Backend contract assumed:**
  - `GET /read/forecast-versions`, `PATCH /mutations/forecast/:id/cells`, `POST /mutations/forecast/:id/publish`.
  - `GET /read/planning-runs/latest`, `POST /mutations/purchase-recommendations/:id/{approve,reject,hold}`, `POST /mutations/purchase-recommendations/batch-approve`.
  - Per-cell optimistic concurrency or whole-version locking — **TODO-WINDOW1**.
  - Whether approving a rec stages a PO draft or creates the PO directly — **TODO-WINDOW5**.
- **Deferred:** compare-versions diff, per-cell reason audit, daily bucket editing (v1 is weekly), production-recs UX (v1.1 slice only).

### 5.5 Read-only surfaces (dashboard, exceptions, approvals, my-submissions, jobs)

- **Mocked:** single synchronous fixture per surface; local-state actions on inbox rows (acknowledge, resolve, approve, reject).
- **Invariants enforced in the mock:**
  - Dashboard never writes.
  - Exception `resolve` requires a note (uses `window.prompt`; a modal is a polishing task).
  - Approval `reject` requires a reason.
  - Row-level actions use separate mutations, not a parent form.
- **Backend contract assumed:**
  - `GET /read/dashboard` (composite), `GET /read/exceptions`, `GET /read/approvals`, `GET /read/my-submissions`, `GET /read/jobs`.
  - `POST /mutations/exceptions/:id/{acknowledge,resolve}`, `/mutations/approvals/:id/{approve,reject}`, `/mutations/jobs/:id/{trigger,set-enabled}`.
- **Deferred:** per-tile loading/partial-failure on dashboard; digest-email preview; jobs log drill-through.

### 5.6 Shell infrastructure (layouts, primitives, review mode)

- **Mocked:** every primitive listed in the brief lives in `src/components/`. `ReviewModePanel` provides: state-forcing, fixture-set placeholder, reset.
- **Invariants enforced:**
  - Review mode is persisted per-device via localStorage (`gt.reviewmode.v1`). Always visibly labelled "Review mode" — never silent.
  - Side nav is role-aware; items the current role cannot see are not rendered.
  - FAKE SESSION chip is impossible to miss (warning-coloured).
- **Backend contract assumed:** none. The primitive layer is all client.
- **Deferred:** keyboard shortcut for review panel, dedicated toast provider, modal/dialog primitive (replaces `window.confirm`/`prompt`), i18n scaffolding.

---

## 6. Freeze scope list

### A. Safe to keep polishing now (no backend dependency, high reviewer value)

1. **Master Maintenance, depth polishing:**
   - Extract the duplicated list-panel-edit pattern into a shared `AdminCrudPage<T>` helper so items/components/suppliers/policy all render from one file each. Would cut ~400 lines.
   - Add better validation messages (e.g. SKU uniqueness check against existing rows in the repo before the mutation).
   - Add a "Revert" button on the edit panel to discard pending form changes without closing.
   - Add a clipboard "Copy ID" on detail panels for easier coordination with Window 1.

2. **BOM editor depth:**
   - Drag-to-reorder lines (`sort_order`).
   - Inline total-cost rollup per line using the seeded `active_price` on components.
   - Sticky header for the line editor on long BOMs.
   - "Revert draft" button.

3. **Dashboard / Exceptions shells:**
   - Replace `window.prompt` resolve note with an inline modal on exceptions.
   - Add a "jump to" click on dashboard shortage rows that filters the purchase-recs view.
   - Add per-tile loading skeletons and partial-failure chip (matches §5.5 invariant that is currently not wired).

4. **Review ergonomics:**
   - Keyboard shortcut (`Ctrl+Shift+R`) to open the review-mode panel.
   - URL query param `?forceState=validation_error` so reviewers can link directly to a forced state.
   - "Reset local IndexedDB" button inside the review panel (wipe + reseed without DevTools).

5. **Shared primitive extraction:**
   - Replace `window.confirm`/`window.prompt` everywhere with a shared Modal primitive.
   - Create a `Toast` provider for non-blocking success notices (dashboard, save-success, etc.).
   - Extract a `ThinPlaceholder` component for Tier 3 shells to remove duplicated "coming in v1.1" banners.

6. **Fixture realism:**
   - Mine `GT_Master_Data.xlsx` for real items/components not yet in fixtures (without writing any import code to the app — a one-off fixtures refresh from Tom's side).
   - Add a "stress" fixture variant with 80+ items / 40+ mappings for scroll testing.

7. **Spec/doc consistency:**
   - Cross-link `window2-portal-spec.md` screen specs with the actual implementation paths.
   - Add a short `portal/README.md` (explicitly requested by Tom if desired; CLAUDE.md discouraged it by default) covering install/run/reset.

### B. Do NOT touch until other windows advance

1. **Goods Receipt / Waste / Adjustment / Physical Count — submit path.** Mock view-swap is deliberate. Do not add any real network call, ledger posting, outbox replay, or attachment upload until Window 1 has locked the three `POST /mutations/*` envelopes and idempotency contract, and until Window 5 has confirmed the ledger phase is ready.

2. **Forecast workspace — save/publish handlers.** Do not wire `PATCH /mutations/forecast/:id/cells` or `POST /mutations/forecast/:id/publish` until Window 1 confirms cell payload shape, concurrency scope, and publish-approval policy.

3. **Purchase recommendations — approve/reject/hold actions.** Do not wire real mutations until Window 5 confirms whether approval stages a PO draft or creates the PO directly, and Window 1 names the endpoints and batch envelope.

4. **PO Form.** Do not build ad-hoc PO creation. The only valid path is recommendation → approve → PO form in v1.

5. **Production Actual.** Do not build the submit path. Ledger semantics for production consumption are a v1.1 item; BOM pinning and scrap handling belong to Window 1.

6. **Jobs Monitor — Run now / Disable.** Do not wire until Window 3/4 (jobs/integrations) confirm the run-trigger contract and auth boundary.

7. **Integrations Admin.** Do not build configuration forms. Field names for LionWheel / Shopify / Green Invoice require inspection of live credentials and responses; do not guess.

8. **Real Supabase auth.** Do not import `@supabase/supabase-js` anywhere in browser code until Window 5 has confirmed the session shape and which operations are client-direct vs. API-boundary. Per foundation doc: "Browser should not talk directly to core operational tables." Hold the line.

9. **Direct table access from browser.** Do not add any client-side RPC, `from("table")` calls, or service role usage. The boundary is the API, and the API does not yet exist.

10. **Real outbox replay / IndexedDB outbox queue.** The envelope is specified; the reconciler loop is not. Do not write it until a real endpoint exists to replay against.

11. **Users admin — invitation flow.** Do not wire. Real invitations go through Supabase Auth; this is Window 5's surface.

12. **PO ad-hoc creation, supplier returns, cycle counting, FEFO, location/bin, customer pricing, RM batch operational workflows.** Explicitly out per foundation doc; any creeping-in is a drift flag.

---

## 7. Testing evidence

> **Superseded 2026-04-14 (review round).** At the time this review pack was written, no test runner was installed and no test files existed. That has since been corrected: the sandbox now has a Vitest unit-test layer (repositories, form validators) and a Playwright smoke-test layer (role switch, admin CRUD, form success, forecast dirty state, review-mode state forcing). Current test commands and pass results live in `window2-acceptance-note.md` §4. Leaving the original §7 below for historical continuity — it is accurate to the time it was written, not to the current state.

### 7.1 Current test commands

```
npm run dev        — start the dev server (review only)
npm run build      — production build + static page generation
npm run lint       — next lint
npm run typecheck  — tsc --noEmit
```

**No unit test runner. No e2e runner.** `npm run test` is not defined. Vitest and Playwright are not installed.

### 7.2 What passes (verified this session)

I ran the following in a **disposable copy** of the portal at `C:\temp\gt_portal_review\` because the Dropbox path breaks npm postinstall on Windows (see §1 and §7.4 below). The copy is byte-identical to `PRODUCTION\portal\src\`.

**`npm install` — passes:**
```
added 371 packages in 52s
```

**`npx tsc --noEmit` — passes (exit 0):**
```
(no output)
exit=0
```
This is the **second** run. The first run surfaced three real type errors that I fixed in place and synced back to `PRODUCTION\portal\`:
- `src/lib/repositories/generic-repo.ts:4-7` — removed an over-broad `[k: string]: unknown` index signature on `WithIdAudit` that made all DTOs fail the generic constraint. Added a targeted cast in the sort comparator for the `name` fallback.
- `src/app/(operator)/ops/receipts/page.tsx:144` — removed an unreachable OR branch (`effective === "success" || (effective === "success" && view === "success")`).
- `src/app/(planner)/planning/purchase-recommendations/page.tsx:61` — replaced a clever `(on ? next.add : next.delete).call(next, id)` helper with a plain `if (on) next.add(id); else next.delete(id);` — the original tripped TS's `this`-context narrowing.

These fixes are already in `PRODUCTION\portal\`.

**`npx next build` — passes, 28 static routes prerendered:**
```
✓ Generating static pages (28/28)

Route (app)                               Size     First Load JS
┌ ○ /                                     136 B           100 kB
├ ○ /_not-found                           896 B           101 kB
├ ○ /admin/boms                           4.24 kB         131 kB
├ ○ /admin/components                     3.15 kB         153 kB
├ ○ /admin/integrations                   2.16 kB         109 kB
├ ○ /admin/items                          3.37 kB         153 kB
├ ○ /admin/jobs                           2.42 kB         109 kB
├ ○ /admin/planning-policy                2.64 kB         152 kB
├ ○ /admin/supplier-items                 3.32 kB         153 kB
├ ○ /admin/suppliers                      2.65 kB         152 kB
├ ○ /admin/users                          3.74 kB         127 kB
├ ○ /approvals                            3 kB            110 kB
├ ○ /dashboard                            2.87 kB         119 kB
├ ○ /exceptions                           3.52 kB         110 kB
├ ○ /home                                 2.39 kB         118 kB
├ ○ /login                                171 B           109 kB
├ ○ /my-submissions                       2.58 kB         109 kB
├ ○ /ops/counts                           2.68 kB         152 kB
├ ○ /ops/production-actual                2.33 kB         109 kB
├ ○ /ops/receipts                         3.69 kB         153 kB
├ ○ /ops/waste-adjustments                2.88 kB         152 kB
├ ○ /planning/forecast                    5.03 kB         112 kB
├ ○ /planning/production-recommendations  2.14 kB         109 kB
├ ○ /planning/purchase-recommendations    5.05 kB         112 kB
├ ○ /profile                              1.6 kB          108 kB
└ ○ /purchasing/po                        3.16 kB         110 kB
+ First Load JS shared by all             99.9 kB
```

**Interpretation:**
- Every route compiles. Every page renders as server-component during build. Zero blocking TypeScript errors.
- Full-CRUD admin pages and operator forms bundle in ~152 kB first-load — that is the RHF+zod+TanStack Query weight. Thin shells bundle in ~109 kB.

### 7.3 What is missing

| Category                    | State     | Notes                                                                                          |
|-----------------------------|-----------|------------------------------------------------------------------------------------------------|
| Unit tests (Vitest)         | **None**  | No vitest.config, no `tests/unit/`. Nothing is unit tested.                                    |
| Component tests             | **None**  | No React Testing Library, no component test files.                                             |
| E2E tests (Playwright)      | **None**  | **Scaffold does NOT exist.** No `playwright.config.ts`, no `tests/e2e/`. I did not scaffold.  |
| Accessibility audit         | **None**  | No axe/pa11y integration. Forms use semantic labels but haven't been audited.                  |
| Visual regression           | **None**  | No snapshot testing.                                                                            |
| Contract tests              | **None**  | Once real backend lands, each `POST /mutations/*` should have a contract test.                 |
| `npm run lint` result       | **Not run** | Skipped in this session — would surface unused-import warnings only (no blocking errors).    |

**What should exist before the portal is considered production-reviewable** (these are NOT in §6A — they are a separate tier of work):

1. **Vitest unit tests for the repositories:** optimistic concurrency, audit bump, soft delete, BOM draft-only edit rule, BOM activation retiring the previous active. These are pure functions + IDB; they can be tested headlessly.
2. **Vitest unit tests for form validation:** waste/adjustment's "positive requires notes" refine, count variance branching, receipts line validation.
3. **Playwright smoke tests for the golden paths:**
   - Log in as fake operator → open Goods Receipt → fill one line → submit → land on success card.
   - Log in as fake planner → open forecast → edit a cell → see dirty count bump.
   - Log in as fake admin → create an item → reopen and verify audit v2.
4. **A Playwright test per screen state,** using the review-mode panel to force each of the seven states and asserting the correct component renders. This is cheap and would catch regressions in the state catalog during future polishing.

### 7.4 Environment caveats

- Dev server cannot run from the Dropbox path on this Windows machine. `npm install` fails with a `MODULE_NOT_FOUND` in `napi-postinstall` because the space in `GTeveryday Dropbox` is misparsed as an argument separator. Workaround: run from a space-free path (`C:\Work\gt-portal-shell` or similar). This is a project-wide concern — every Node project under this Dropbox path will have the same issue.
- Typecheck and build were run against a byte-identical copy at `C:\temp\gt_portal_review\`. That copy was used **only** for verification and should be deleted after review (I'll clean it up in this session).

---

## 8. Migration path recommendation

> **Superseded 2026-04-14 (review round).** The recommendation below assumed `gt-factory-os/portal/` was empty and could be filled by porting Window 2's sandbox. That assumption is wrong: a different work stream is already building a different portal at `C:/Users/tomw2/Projects/gt-factory-os/portal/`, currently at D2 (shared primitives) stage, with its own architecture (radix/shadcn, `shared/` layout, `PermissionGuard` + `WriteContext`, mocked api-client layer). Per that repo's committed coordination note, the two portals are intentionally parallel with no merge plan. The corrected port-trigger statement is in `window2-acceptance-note.md` §6. Leaving the original text below for historical reference.

**Recommendation (historical, superseded):** Treat `PRODUCTION/portal/` as a **review sandbox only for now.** Do not port it into `gt-factory-os/portal` until Windows 1 and 5 lock the first concrete API surface (even one working endpoint, e.g. `GET /read/items`). Once that happens, port — don't rebuild.

**Reason:**

1. The portal has **real reuse value**. 28 routes, 86 source files, optimistic concurrency, the full seven-state catalogue, role gating, blind-UX on counts, BOM versioning, Hebrew-friendly inputs, and a seeded fixture set that reflects the real factory. Throwing this away would cost at least a week to re-do.
2. It has **zero backend coupling**. Every data path is indirected through `Repository<T>` interfaces (for master data) or a direct fixture read (for planning/inbox surfaces). When the real API exists, swapping the constructors in `src/lib/repositories/index.ts` from `GenericIdbRepo` to an `ApiRepo` is a one-file change per domain.
3. But it is also not yet in the **real repo** (`gt-factory-os`), which is where the Supabase migrations, docs, and secrets checklist already live. Porting now would mean dragging `node_modules`, review-mode scaffolding, and fake-auth into a repo that is trying to lock architectural discipline. The two should meet only once both sides have something load-bearing.
4. The Dropbox path is also actively hostile to Node dev workflows. `PRODUCTION/portal/` is, in practice, a **read-only reference sandbox** — not a place Tom can `npm run dev` from without moving first. This reinforces the "not the real repo yet" framing.

**Risk if ignored (port too early):**

- If we port into `gt-factory-os/portal` now, and Window 1 then changes a schema shape (very likely — they haven't started), the ported portal will drift from the real API. Two consequences:
  - wasted port work,
  - a false "we have a portal" signal that makes Windows 3/4 over-rely on it before it is wired.
- The fake-auth session provider will be easy to forget to delete during port, and will ship into a codebase that already has Supabase docs → dangerous cross-signal.
- Dropbox-path surprises bleed into the real repo's contributor experience.

**Risk if ignored (keep as sandbox forever):**

- We lose the value in §6A polishing work because it has nowhere to land.
- The spec and the code drift apart as Windows 1/5 evolve contracts.

**Mitigation — the port trigger:** port `PRODUCTION/portal/` → `gt-factory-os/portal/` on the day Window 1 produces ONE working read endpoint that matches any of the `GET /read/*` shapes in `window2-portal-spec.md` §5. That day, the port is a straightforward file move plus:
1. Delete `lib/auth/fake-auth.ts` + `session-provider.tsx` (the fake-auth pair), keep `role-gate.tsx`.
2. Add a real Supabase Auth session provider under the same `useSession` API surface.
3. Add an `ApiItemsRepo` (or whichever domain is live first) implementing `Repository<ItemDto>` and wire it in `lib/repositories/index.ts`.
4. Keep `GenericIdbRepo` as a `dev` variant if Tom wants offline review to keep working — or delete it.

**Test needed to validate the port when it happens:**

- **Pre-port:** the existing typecheck + build pass (we have that today).
- **Post-port:** the same typecheck + build pass from inside `gt-factory-os/portal/`, PLUS one Playwright smoke test that hits the live endpoint via the real `ApiItemsRepo` and renders the items list. That single test is the "port succeeded" gate.
- **Parity check:** the real backend response must satisfy the `ItemDto` in `src/lib/contracts/dto.ts` without changes. If it doesn't, **stop the port** and reconcile the DTO first — do not edit both ends to match.

**Secondary recommendation (not asked for, but important):** regardless of port timing, move the sandbox out of the Dropbox path today. Create `C:\Work\gt-portal-shell` (or similar) and either move the portal there or maintain a non-synced git clone. The current path cannot run `npm install` locally. If UX review depends on a running dev server, Tom will hit this immediately.

---

## Appendix A — Invariants summary (for fast reviewer spot-checks)

These are the behavioral invariants the shell claims to enforce. A reviewer should be able to break each one and fail fast.

| Invariant                                                         | Where it lives                                                           |
|-------------------------------------------------------------------|--------------------------------------------------------------------------|
| Role gate renders "not available" on role mismatch                | `src/lib/auth/role-gate.tsx`                                             |
| Nav suppresses items outside current role                         | `src/components/layout/SideNav.tsx`                                      |
| Optimistic concurrency on master data                             | `src/lib/repositories/generic-repo.ts` (update checks `audit.version`)   |
| Soft delete only                                                  | `src/lib/repositories/generic-repo.ts` (`setActive`, no delete method)   |
| BOM: only draft versions allow line edits                         | `src/lib/repositories/boms-repo.ts#updateLines`                          |
| BOM: activation retires the current active                        | `src/lib/repositories/boms-repo.ts#activateVersion`                      |
| Blind-UX on counts: system qty never rendered pre-submit          | `src/app/(operator)/ops/counts/page.tsx` — JSX never references `MOCK_SYSTEM_QTY` before the submit handler |
| Positive-adjustment confirm modal before view swap                | `src/app/(operator)/ops/waste-adjustments/page.tsx` (`window.confirm` in submit) |
| Notes required for positive or `reason = other`                   | `src/app/(operator)/ops/waste-adjustments/page.tsx` zod `superRefine`    |
| Approval preview banner before submit on waste/adjustment         | Same file — `willRequireApproval` drives `ApprovalBanner` visibility     |
| Receipt line qty > 0                                              | `src/app/(operator)/ops/receipts/page.tsx` zod schema                    |
| Receipt requires ≥1 line                                          | Same file — `z.array(lineSchema).min(1)`                                 |
| Forecast cells are non-negative                                   | `src/app/(planner)/planning/forecast/page.tsx` (`updateCell` gate)       |
| Forecast is not a form (no single submit)                         | Structural — there is no `handleSubmit`; save/publish are separate buttons |
| Bulk approve > 10 triggers confirm                                | `src/app/(planner)/planning/purchase-recommendations/page.tsx#approveSelected` |
| Review-mode state is always visibly labelled                      | `src/components/review/ReviewModePanel.tsx` + `StatePreviewChip.tsx`    |
| No Supabase SDK in browser                                        | Codebase grep: `@supabase/supabase-js` is not imported anywhere           |
| No `fetch` to core tables                                         | Codebase grep: `fetch(` does not appear in any feature or page file      |

---

_End of Window 2 review pack._
