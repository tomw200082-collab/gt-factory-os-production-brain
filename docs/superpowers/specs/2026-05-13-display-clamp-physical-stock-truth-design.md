# Display Clamp for Physical Stock Truth — Design Spec

**Authored:** 2026-05-13
**Owner:** portal-operator-ux desk (proposes); backend-db-truth desk (advises on view shape).
**Status:** spec-only. No code authored. No migrations authored. No portal source touched.
**Scope of this spec:** Change 1 of the four-change Stock Truth Layering program. Changes 2–4 (ATS view, repair workflow, Shopify `committed` verification) are out of scope.

---

## 1. Problem statement

`private_core.current_balances.calculated_on_hand` is `qty_8dp numeric(24,8)` with no CHECK constraint preventing negative values. When ledger event sequencing produces a transient negative balance (a shipment posted before its corresponding receipt, a back-dated waste event, a count-anchor replacement that exposes a prior gap), the operator-facing portal currently shows the raw signed value — for example, "−5 bottles" on a stock card.

This is physically meaningless. The warehouse cannot contain less than zero bottles. The negative value is **a tracking-data observation**, not a stock fact. Showing it unmodified misleads operators, creates spurious operator anxiety, and trains the eye to accept impossible-physical numbers as legitimate.

This spec defines the smallest correct change: clamp the display, surface the discrepancy as an actionable cue, never mutate truth.

---

## 2. Non-goals

This spec deliberately does NOT:

- Add a CHECK constraint preventing negative `calculated_on_hand`. The projection must still reflect the ledger faithfully; suppressing the negative at storage would hide real evidence of sequencing problems.
- Block ledger inserts that would drive `calculated_on_hand` negative. Ledger immutability and append-only semantics (`CLAUDE.md` §non-negotiables) win; bad ordering is a data-quality issue, not a write-blocker.
- Emit a new exception type. Exception emission for negative physical stock is Change 3 of the program; this spec is presentation-only.
- Change the Shopify push behavior. Per `shopify_boundary_contract.md` §4.2 and `shopify_fg_sync_contract_v2.md` §1, Shopify push already clamps to zero. No change there.
- Change planning engine inputs. The planning engine reads truth; truth carries the negative when negative.
- Touch the `rebuild_verifier()` math. It must continue to operate on the raw signed projection.
- Introduce a separate badge for `available_to_promise < 0`. That is Change 2 (ATS view); different visual, different copy.

---

## 3. Display rule

### 3.1 Two derived display values

For any portal surface rendering FG or RM/PKG stock to an operator, two values exist downstream of `calculated_on_hand`:

```
on_hand_raw       = current_balances.calculated_on_hand                 -- unchanged, never hidden
on_hand_display   = GREATEST(0, current_balances.calculated_on_hand)    -- what the operator sees as a number
is_below_floor    = (current_balances.calculated_on_hand < 0)           -- triggers the Reconcile badge
floor_gap         = GREATEST(0, -current_balances.calculated_on_hand)   -- magnitude of the gap (always ≥ 0)
```

`is_below_floor` is `true` strictly when `calculated_on_hand < 0`. The value `0` is a legitimate out-of-stock state and does NOT trigger the badge.

### 3.2 Where `on_hand_display` is used (clamp surfaces)

| Surface | Render |
|---|---|
| `/items/[id]` item card | `on_hand_display` + Reconcile badge when `is_below_floor` |
| `/stock` balance list | `on_hand_display` + Reconcile badge when `is_below_floor` |
| Dashboard / control-tower stock panel | `on_hand_display` + Reconcile badge when `is_below_floor` |
| Goods Receipt form pre-fill ("current on-hand") | `on_hand_display`, no badge (input, not output) |
| Waste / Adjustment form preview | `on_hand_display` + inline warning text when `is_below_floor`: "System currently records {floor_gap} units below physical floor. Verify this action will not deepen the gap." |
| Production Actual form preview | same as Waste |
| Physical Count blind / open form | unchanged (blind-count semantics already hide the value) |
| Planning blockers list | unchanged (planning operates on truth) |

### 3.3 Where `on_hand_raw` continues to be used (truth surfaces)

| Surface | Render |
|---|---|
| Inbox / exception detail | `on_hand_raw` with sign |
| Stock truth audit pages | `on_hand_raw` with sign |
| `rebuild_verifier()` and parity gates | `on_hand_raw` |
| Planning engine inputs (`planning_run_lines`, BOM explosion) | `on_hand_raw` |
| Stock event accuracy audit reports | `on_hand_raw` |
| Future "Stock Truth Repair" drawer (this spec, §4) | both — shows `on_hand_raw` and the math |

### 3.4 Where the integration boundary already clamps (no change)

| Surface | Current behavior | After this spec |
|---|---|---|
| `shopify_fg_sync` v2 push | `inventoryAdjustQuantities` writes deltas; `inventorySetOnHandQuantities` for absolute events clamped to `GREATEST(0, FLOOR(on_hand))` per existing contract | unchanged |
| Excel nightly export | reads `on_hand_raw` | unchanged (audit artifact, raw is correct here) |

---

## 4. The Reconcile badge

### 4.1 Badge anatomy

| Property | Value |
|---|---|
| **Label** | `Reconcile` |
| **Tone** | amber / warning (not red / critical) |
| **Tooltip** | `Recorded outflows exceed receipts by {floor_gap} {uom}. Click to review.` |
| **Click target** | inline right-side drawer (§4.2) |
| **Live region** | aria-live polite — announce on first appearance, not on every render |
| **Repetition** | one badge per item per surface; do not stack |

### 4.2 The Stock Truth drawer (inline, no new route)

Triggered from the badge click. Right-side drawer (matches existing portal drawer pattern). Sections:

1. **Header** — item name (per `feedback_names_not_ids_in_ui`), supply method, current state line:
   `Calculated: −5  ·  Below physical floor by 5  ·  Anchor 2026-04-30: 50`

2. **Ledger math reconciliation**
   ```
   Anchor at 2026-04-30 19:21:41Z          : 50
   Posted ledger deltas since anchor       : −55
   ─────────────────────────────────────────────
   Calculated on-hand                      : −5
   ```

3. **Recent ledger events table** — 10 most recent rows for the item:
   `event_at  ·  movement_type  ·  qty_delta  ·  posted_by  ·  reference`

4. **Single CTA** — `Post corrective Goods Receipt`
   - Opens the GR form in the same drawer (or new page if the form does not yet support drawer mode).
   - Pre-fills `item_id`. Operator selects PO context or chooses ad-hoc, enters qty, posts.
   - On successful post, the drawer refreshes; if `calculated_on_hand >= 0` after refresh, the badge disappears.

5. **Footer** (future) — when Change 3 lands and the `negative_on_hand_observed` exception exists for this item, render a secondary link: `View in Inbox`. Until Change 3 lands, this slot is hidden.

### 4.3 What the drawer does NOT do

- Does not allow editing of past ledger events.
- Does not offer "force balance to zero" or any other ledger-bypass repair. All corrections go through canonical forms.
- Does not auto-suggest the corrective quantity. The operator decides.

---

## 5. Implementation surface map

This is portal-only authoring under `portal-operator-ux` desk. Backend exposes one new derived field in the existing FG availability read view; no migration to the ledger or projection.

### 5.1 Backend (additive, no schema change)

Extend the existing or planned `api_read.v_fg_availability` and `api_read.v_rm_availability` views (per `availability_semantics_contract.md` §9):

```sql
SELECT
  ...,
  current_balances.calculated_on_hand          AS on_hand_raw,
  GREATEST(0, current_balances.calculated_on_hand) AS on_hand_display,
  (current_balances.calculated_on_hand < 0)    AS is_below_floor,
  GREATEST(0, -current_balances.calculated_on_hand) AS floor_gap,
  ...
FROM current_balances
...
```

If the views do not yet exist, add `on_hand_raw`, `on_hand_display`, `is_below_floor`, `floor_gap` to the existing `/api/items/[id]` and `/api/stock` response shapes. The portal consumes via TanStack Query.

Returning all four fields is deliberate. The portal chooses which to render per surface (per §3.2/§3.3). Backend never decides display semantics.

### 5.2 Portal (`gt-factory-os-portal` / `window2-portal-sandbox`)

A single shared utility module:

```
src/lib/stock-display.ts

  export function clampedOnHand(raw: number): number       // returns Math.max(0, raw)
  export function isBelowFloor(raw: number): boolean       // returns raw < 0
  export function floorGap(raw: number): number            // returns Math.max(0, -raw)
```

A single shared component:

```
src/components/stock/StockValueWithReconcile.tsx

  props: { raw: number, uom: string, itemId: string, surface: 'card' | 'list' | 'preview' }
  renders: <numeric value> + <ReconcileBadge> conditionally
```

A single shared drawer component:

```
src/components/stock/StockTruthDrawer.tsx

  props: { itemId: string, open: boolean, onClose: () => void }
  data: TanStack Query against /api/items/[id]/ledger-recent?limit=10
```

Every surface listed in §3.2 imports `<StockValueWithReconcile>` and replaces the current raw render. No surface implements its own clamp.

### 5.3 New API endpoint (one)

`GET /api/items/[item_id]/ledger-recent?limit=10`

Returns the last N ledger events for the item, in descending event_at order, with display fields resolved (movement_type human label, posted_by display name per `feedback_names_not_ids_in_ui`). Read-only. No mutation. No new migration needed if the view-side handling is done in the route handler against `private_core.stock_ledger`.

---

## 6. Empty / edge states

| State | Display |
|---|---|
| `on_hand_raw = 0` | numeric "0", no badge, no drawer |
| `on_hand_raw > 0` | numeric raw, no badge, no drawer |
| `on_hand_raw < 0`, item has ledger events | numeric "0", Reconcile badge, drawer shows events |
| `on_hand_raw < 0`, item has no ledger events since anchor | numeric "0", Reconcile badge, drawer shows "No ledger events since anchor — anchor itself may be wrong"; CTA changes to `Post corrective count` |
| Item not yet seeded | "—" (em-dash), no badge |
| Item with mixed-batch entries (future) | aggregated `on_hand_raw` across batches; per-batch display deferred to v2 of this spec |

---

## 7. Accessibility

| Concern | Treatment |
|---|---|
| Badge color carrying meaning alone | No — label `Reconcile` carries meaning; color is decoration |
| Focus order | Badge is a button after the numeric value; tab order matches reading order |
| Screen reader announcement | `aria-live=polite` region announces "Stock value 0, reconciliation needed, 5 units below floor" on first render |
| Drawer focus trap | Standard portal drawer trap; ESC closes; first focusable is the CTA |
| Tooltip on hover-only inputs | Avoided — tooltip content also reachable via long-press / focus / drawer header |

---

## 8. Test posture

| Test | Surface | Assertion |
|---|---|---|
| Playwright smoke — clamped display | `/items/[id]` with fixture `on_hand_raw = -5` | numeric reads "0"; badge with label "Reconcile" present |
| Playwright smoke — no badge at zero | `/items/[id]` with fixture `on_hand_raw = 0` | numeric reads "0"; no badge |
| Playwright smoke — no badge at positive | `/items/[id]` with fixture `on_hand_raw = 50` | numeric reads "50"; no badge |
| Playwright smoke — drawer opens | click on badge | drawer visible; recent-events table populated; CTA enabled |
| Playwright smoke — drawer refresh after corrective post | inside drawer, post a GR that brings raw to +5 | on close + refresh, badge gone; numeric reads "5" |
| Backend test — view exposes both fields | unit test on `v_fg_availability` | `on_hand_raw` and `on_hand_display` both present and self-consistent for fixture rows |
| Audit surface unchanged — inbox exception detail | open an exception thread referencing the item | numeric reads "−5" with sign; no badge (truth surface) |
| `rebuild_verifier()` unaffected | DB-level test | returns 0 with same fixtures before and after the spec |

---

## 9. Rollback

| Trigger | Action |
|---|---|
| Operators report the badge is noisy / wrong tone | Edit the badge tone / copy in `<ReconcileBadge>`; no data change |
| The drawer shows wrong ledger events | Fix the API handler; no data change |
| The clamp itself is wrong (rare) | Revert the `<StockValueWithReconcile>` to render `raw` directly; one commit revert |

There is no DB rollback. Nothing in this spec mutates DB state.

---

## 10. Dependencies, sequencing, and the four-change program

This spec is Change 1 of four. It is the only one that touches only the portal and one read view.

| Change | Owner desk | Touches | Depends on |
|---|---|---|---|
| **1. Display clamp + Reconcile badge** (this spec) | portal-operator-ux + backend-db-truth (view only) | view, portal | none |
| 2. Explicit ATS / over-commitment view | backend-db-truth + portal-operator-ux | view (or new view), portal | `orders_mirror` (Tranche 4) |
| 3. `negative_on_hand_observed` exception + repair workflow | backend-db-truth + portal-operator-ux | trigger or projection-time emit, exceptions table, inbox surface | Change 1 |
| 4. Shopify `committed` verification | integration-boundary | drift detector v2 extension | Shopify v2 live (Gate E) |

Change 1 standing alone is useful: it stops the misleading negative display today and offers the operator a corrective path. Change 3 strengthens it by adding asynchronous exception emission and inbox surfacing; Change 1's drawer adds the inbox link once Change 3 lands.

---

## 11. UNRESOLVED (carried, not invented)

| Item | Carried from | Effect on this spec |
|---|---|---|
| Exact precision/scale values for `qty_8dp` | `CURRENT_STATE.md` UNRESOLVED list | None. We use `< 0` strictly. If precision noise produces spurious badges, tighten in a follow-up. |
| Concrete tolerance thresholds for count / parity | `CURRENT_STATE.md` UNRESOLVED list | None. Display clamp does not interact with tolerance. |
| Whether Hebrew register entries are needed for new portal copy | `feedback_portal_ui_english_ltr` | Resolved here: English default, no register entry needed for `Reconcile` / tooltip / drawer headings. |

---

## 12. What this spec is NOT

- Not a contract change to `availability_semantics_contract.md` (the spec extends `v_fg_availability` shape; no semantic change).
- Not a Shopify boundary change (Shopify push already clamps).
- Not an exception-emission change (Change 3).
- Not an ATS / over-commitment surface (Change 2).
- Not a planning-engine change.
- Not an admin-CRUD change.
- Not a Hebrew-register pinning request.

---

## 13. Approval gates

| Gate | Owner | Resolution |
|---|---|---|
| Spec text approval | Tom | pending — this document |
| UX handoff packet for `<ReconcileBadge>` and `<StockTruthDrawer>` | `interaction-design-specialist` + `visual-system-designer` | required before portal authoring per portal-production-executor allowed-paths |
| Backend view change PR review | backend-db-truth desk | required before portal consumes the new fields |
| Portal authoring PR review | portal-production-executor + `/portal-pr-review` | required before merge |
| Release gate | `release-verifier` via `/release-check` | required before deploy |

---

**End of spec.**
