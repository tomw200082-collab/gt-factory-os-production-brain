# Forecast Workspace v2 Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the canonical Forecast Workspace at `/planning/forecast/[version_id]/v2` — Anaplan-style stacked-measure pivot grid with Stripe/Vercel-light aesthetic. Tom (sole planner) enters 8-week forecast across 68 FG items in a single screen with keyboard-first interaction, baseline/override visual, in-cell freeze, decomposition popover, side-panel sparkline, version compare overlay.

**Architecture:** New route `(planning)/planning/forecast/[version_id]/v2/page.tsx` coexisting with the MVP page at `[version_id]/page.tsx`. One new backend endpoint `/api/v1/queries/orders/by-item-and-period` for the open-orders sub-row. All other writes reuse existing endpoints (`/api/forecasts/save-lines`, `/api/forecasts/publish`). Grid uses `@tanstack/react-virtual` for virtualization. Hebrew strings inlined per Tom-locked register from spec §B.1; numbers stay LTR via `<bdi>` wrappers in cells.

**Tech Stack:** Next.js 15 App Router · React 18 · TypeScript · TanStack Query · TanStack Virtual · Tailwind · shadcn/ui · Radix UI Popover · lucide-react · Heebo + Inter font stack. Backend: Node 20 + Fastify + Zod + Kysely + PostgreSQL.

**Spec source:** `PRODUCTION/docs/superpowers/specs/2026-04-30-day1-cutover-and-forecast-workspace-v2-design.md` Part B.

**Effort estimate:** ~33 hours of W1+W2 work spread across 4–5 days.

**Dependencies on other plans:**
- None blocking. Day-1 backend prep plan (sibling file `2026-04-30-day1-backend-prep.md`) is independent. The Workspace v2 ships AFTER Day-1 cutover so the platform is in steady-state when this lands.

**One UNRESOLVED:** "Copy from last year" quick action depends on a `historical_sales` view. **Before W2 starts the side-panel quick-actions task (Chunk 5)**, W1 must confirm whether a `v_historical_sales` or `historical_sales_mirror` exists and document its shape. If it doesn't, defer the quick action to v3 and ship Workspace v2 without it.

---

## File Structure

**New backend (W1):**
- `api/src/orders/handler.byItemAndPeriod.ts` — read-only handler
- `api/src/orders/route.ts` — register the new GET route (or extend existing)
- `api/src/orders/schemas.ts` — Zod schema for query params + response
- `db/tests/orders_by_item_and_period.test.sql` — pgTAP for the underlying SQL (if any view-layer SQL is added)
- `api/test/orders_by_item_and_period.test.ts` — node:test for handler

**New portal (W2):**
- `src/app/(planning)/planning/forecast/[version_id]/v2/page.tsx` — entry route (Suspense wrapper)
- `src/app/(planning)/planning/forecast/[version_id]/v2/_components/Workspace.tsx` — top-level grid component
- `src/app/(planning)/planning/forecast/[version_id]/v2/_components/Header.tsx` — version dropdown · bucket toggle · horizon picker · freshness chip · Publish button
- `src/app/(planning)/planning/forecast/[version_id]/v2/_components/SkuRail.tsx` — left rail with 68 SKUs · search · sort
- `src/app/(planning)/planning/forecast/[version_id]/v2/_components/Grid.tsx` — main pivot grid · 68 rows × 8 cols · virtualization
- `src/app/(planning)/planning/forecast/[version_id]/v2/_components/SkuRow.tsx` — single SKU's 3 stacked sub-rows (forecast / orders / total)
- `src/app/(planning)/planning/forecast/[version_id]/v2/_components/ForecastCell.tsx` — editable cell (baseline grey-faint, override blue-bold, ⭐ changed, 🔒 frozen)
- `src/app/(planning)/planning/forecast/[version_id]/v2/_components/OrdersCell.tsx` — read-only orders cell with click → orders drill
- `src/app/(planning)/planning/forecast/[version_id]/v2/_components/TotalCell.tsx` — computed total · click → decomposition popover
- `src/app/(planning)/planning/forecast/[version_id]/v2/_components/SidePanel.tsx` — collapsible right panel · sparkline · YoY compare · quick actions
- `src/app/(planning)/planning/forecast/[version_id]/v2/_components/BottomBar.tsx` — "X cells changed since last publish · Review · Discard · Publish"
- `src/app/(planning)/planning/forecast/[version_id]/v2/_lib/types.ts` — shared types
- `src/app/(planning)/planning/forecast/[version_id]/v2/_lib/useWorkspace.ts` — orchestration hook (combines forecast + orders queries)
- `src/app/(planning)/planning/forecast/[version_id]/v2/_lib/useKeyboardNav.ts` — keyboard navigation hook
- `src/app/(planning)/planning/forecast/[version_id]/v2/_lib/buckets.ts` — bucket generation + monthly/weekly toggle helpers
- `src/app/(planning)/planning/forecast/[version_id]/v2/_lib/hebrew-labels.ts` — Tom-locked Hebrew strings (single source per spec §B.1)
- `src/app/api/v1/queries/orders/by-item-and-period/route.ts` — portal API proxy for the new W1 endpoint

**Tests:**
- `tests/e2e/forecast-workspace-v2.spec.ts` — Playwright real-HTTP E2E
- `src/app/(planning)/planning/forecast/[version_id]/v2/_components/__tests__/Grid.test.tsx` — Vitest unit tests for grid math
- `src/app/(planning)/planning/forecast/[version_id]/v2/_components/__tests__/ForecastCell.test.tsx` — Vitest for cell render states (baseline/override/frozen)

**Touched (existing files extended):**
- `src/lib/nav/manifest.ts` — add link to `/planning/forecast` (already there) + ensure v2 is reachable via the version-detail page
- `src/app/(planning)/planning/forecast/[version_id]/page.tsx` — add a small "Open in v2" button at the top of MVP detail (smooth migration path)

---

## Chunk 1: Backend endpoint — open orders by item + period

### Task 1: Define and document the contract

**Files:**
- Modify or create: `api/src/orders/schemas.ts`

- [ ] **Step 1: Read the existing orders mirror schema**

  Run: `ls api/src/orders/`. If no orders module exists, decide between extending `api/src/integrations/lionwheel/` or creating a new `api/src/orders/` module. The contract is to query the **existing** `orders_mirror_lines` table — no new table.

- [ ] **Step 2: Write the Zod schema for the request and response**

  ```typescript
  // api/src/orders/schemas.ts
  import { z } from "zod";

  export const ordersByItemAndPeriodQuery = z.object({
    from: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
    to: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
    items: z.string().optional(),  // comma-separated item_id list; empty = all
  });

  export const ordersByItemAndPeriodResponse = z.object({
    rows: z.array(z.object({
      item_id: z.string(),
      period_bucket_key: z.string(),  // YYYY-MM-DD (Monday for weekly, first-of-month for monthly)
      qty_total: z.string(),  // numeric(20,8) preserved as string
      order_count: z.number().int(),
      // Sample of the underlying mirror rows for the decomposition popover (max 5).
      sample_orders: z.array(z.object({
        lw_task_id: z.string(),
        customer_name: z.string().nullable(),
        pickup_at: z.string().nullable(),
        qty: z.string(),
      })).max(5),
    })),
    bucket_cadence: z.enum(["weekly", "monthly"]),
  });
  ```

- [ ] **Step 3: Document the contract in `docs/integrations/orders_by_item_and_period_contract.md`**

  Mirror the format of existing W4 contracts (`docs/integrations/inventory_flow_contract.md` is a good template). Specify input → output, bucketing semantics (use `om.pickup_at AT TIME ZONE 'Asia/Jerusalem'` per migration 0099), retired-row exclusion, item filter.

### Task 2: Write a failing handler test

**Files:**
- Create: `api/test/orders_by_item_and_period.test.ts`

- [ ] **Step 1: Mirror an existing handler-test shape**

  Find a test that fixtures `orders_mirror_lines` (look in `api/test/lionwheel_*.test.ts`) and copy the fixture pattern.

- [ ] **Step 2: Write three cases**

  ```typescript
  test("aggregates resolved non-retired orders by item × monthly bucket", ...);
  test("filters by items list when provided", ...);
  test("returns sample_orders[5] cap on the decomposition payload", ...);
  ```

- [ ] **Step 3: Run, verify all 3 fail (handler doesn't exist yet)**

  Run: `cd api && npm test -- test/orders_by_item_and_period.test.ts`
  Expected: FAIL `Cannot GET /api/v1/queries/orders/by-item-and-period`.

### Task 3: Implement the handler

**Files:**
- Create: `api/src/orders/handler.byItemAndPeriod.ts`
- Modify: `api/src/orders/route.ts` (or wire into the existing routes file)

- [ ] **Step 1: Write the SQL aggregation**

  Single query against `orders_mirror_lines` joined to `orders_mirror`:
  ```sql
  SELECT
    oml.item_id,
    -- monthly bucket: first-of-month in Asia/Jerusalem
    date_trunc('month', (om.pickup_at AT TIME ZONE 'Asia/Jerusalem'))::date AS period_bucket_key,
    SUM(oml.lw_qty_ordered)::text AS qty_total,
    COUNT(*)::int AS order_count,
    -- sample for decomposition popover
    (array_agg(jsonb_build_object(
      'lw_task_id', om.lw_task_id,
      'customer_name', om.customer_name,
      'pickup_at', om.pickup_at,
      'qty', oml.lw_qty_ordered::text
    ) ORDER BY om.pickup_at DESC))[1:5] AS sample_orders
  FROM private_core.orders_mirror om
  JOIN private_core.orders_mirror_lines oml ON oml.mirror_id = om.mirror_id
  WHERE om.retired_at IS NULL
    AND oml.resolution_status = 'resolved'
    AND oml.item_id IS NOT NULL
    AND (om.pickup_at AT TIME ZONE 'Asia/Jerusalem')::date BETWEEN $1::date AND $2::date
    AND ($3::text[] IS NULL OR oml.item_id = ANY($3))
  GROUP BY 1, 2
  ORDER BY 1, 2;
  ```

  *Note: cadence param toggles `date_trunc('month', …)` vs `date_trunc('week', …)` — implement both.*

- [ ] **Step 2: Wire into Fastify**

  Register at GET `/api/v1/queries/orders/by-item-and-period`. Apply role gate `viewer:read` (anyone with portal access can read order aggregates).

- [ ] **Step 3: Run the test to verify pass**

  Run: `cd api && npm test -- test/orders_by_item_and_period.test.ts`
  Expected: all 3 cases PASS.

- [ ] **Step 4: Commit**

  ```bash
  git add api/src/orders/ api/test/orders_by_item_and_period.test.ts docs/integrations/orders_by_item_and_period_contract.md
  git commit -m "feat(orders): GET /api/v1/queries/orders/by-item-and-period for Forecast Workspace v2"
  git push
  ```

### Task 4: Add portal proxy

**Files:**
- Create: `src/app/api/v1/queries/orders/by-item-and-period/route.ts` (in window2-portal-sandbox)

- [ ] **Step 1: Mirror an existing read-only proxy** (e.g. `src/app/api/inventory/flow/route.ts`)

- [ ] **Step 2: Forward query, role-gate at viewer:read**

- [ ] **Step 3: Verify with curl** against the deployed Railway endpoint:

  Run: `curl -i "https://gt-factory-os-portal.vercel.app/api/v1/queries/orders/by-item-and-period?from=2026-04-01&to=2026-06-01"` (with cookie / JWT)
  Expected: 200 + JSON.

- [ ] **Step 4: Commit + push**

---

## Chunk 2: Portal foundation — route + types + state hook

### Task 5: Create the route shell

**Files:**
- Create: `src/app/(planning)/planning/forecast/[version_id]/v2/page.tsx`

- [ ] **Step 1: Write the entry page**

  ```tsx
  "use client";
  import { Suspense, use } from "react";
  import { Workspace } from "./_components/Workspace";

  export default function ForecastWorkspaceV2Page({ params }: { params: Promise<{ version_id: string }> }) {
    const { version_id } = use(params);
    return (
      <Suspense fallback={<div className="p-5">Loading workspace…</div>}>
        <Workspace versionId={version_id} />
      </Suspense>
    );
  }
  ```

- [ ] **Step 2: Stub Workspace.tsx that just renders the version_id**

  ```tsx
  export function Workspace({ versionId }: { versionId: string }) {
    return <div className="p-5">v2 workspace for version {versionId}</div>;
  }
  ```

- [ ] **Step 3: Verify the route loads**

  Open `https://…/planning/forecast/<known-version-id>/v2` — should show the stub.

- [ ] **Step 4: Commit**

### Task 6: Define types + Hebrew label registry

**Files:**
- Create: `_lib/types.ts`
- Create: `_lib/hebrew-labels.ts`

- [ ] **Step 1: types.ts** — define `WorkspaceData`, `BucketCadence`, `EditedCellMap`, `SkuRow`, etc.

- [ ] **Step 2: hebrew-labels.ts**

  Locked verbatim from spec §B.1:
  ```typescript
  export const HE = {
    forecast: "תחזית",
    openOrders: "הזמנות פתוחות",
    totalDemand: "סה״כ ביקוש",
    publishVersion: "פרסם גרסה",
    draft: "טיוטה",
    published: "פורסם",
    changedSinceLastPublish: "שונה מאז פרסום אחרון",
    frozen: "מוקפא",
    review: "סקור",
    discard: "בטל",
    publish: "פרסם",
    copyFromLastYear: "העתק מאשתקד",
    splitEvenly: "חלק שווה",
    plus10Percent: "+10% צמיחה",
    resetRow: "אפס שורה",
  } as const;
  ```

- [ ] **Step 3: Commit** (no test needed; pure type/constant definitions).

### Task 7: Implement `useWorkspace` orchestration hook

**Files:**
- Create: `_lib/useWorkspace.ts`

- [ ] **Step 1: Compose existing forecast detail query + new orders query + items query**

  ```typescript
  export function useWorkspace(versionId: string) {
    const versionQ = useQuery({ queryKey: ['forecast-version', versionId], queryFn: () => fetchVersion(versionId) });
    const itemsQ = useQuery({ queryKey: ['items-active'], queryFn: () => fetchItems() });
    const ordersQ = useQuery({
      queryKey: ['orders-by-period', versionQ.data?.version.horizon_start_at, versionQ.data?.version.horizon_weeks, versionQ.data?.version.cadence],
      queryFn: () => fetchOrdersByPeriod(/* derived from horizon */),
      enabled: !!versionQ.data,
    });
    return { versionQ, itemsQ, ordersQ };
  }
  ```

- [ ] **Step 2: Add reducer for in-flight edits**

  `useReducer` keyed by `(item_id, bucket)` → `{ value: string; touched: boolean }`.

- [ ] **Step 3: Add debounced autosave** — fires 800ms after the last edit; calls existing `/api/forecasts/save-lines`. Survives network errors with retry.

- [ ] **Step 4: Unit test the reducer** (Vitest, no DOM):

  Test cases:
  - "typing in a cell sets touched=true and stores value"
  - "Esc reverts to baseline"
  - "shift-drag fill copies value across range"

- [ ] **Step 5: Commit**

---

## Chunk 3: Grid + cells (forecast / orders / total)

### Task 8: Stub the Grid component shape (no data, just layout)

- [ ] **Step 1: 68 rows × 8 cols rendered** as plain table to verify layout, no real data
- [ ] **Step 2: Add tier strip + sticky left rail (SkuRail)**
- [ ] **Step 3: Verify column widths + sticky behavior in Chrome DevTools**
- [ ] **Step 4: Commit**

### Task 9: Wire useWorkspace data into Grid

- [ ] **Step 1: Replace stub data with real items + buckets**
- [ ] **Step 2: For each (item, bucket), look up the existing forecast value**
- [ ] **Step 3: Verify all 68 rows render with correct labels**

### Task 10: Implement ForecastCell (baseline / override / changed / frozen)

**Files:**
- Create: `_components/ForecastCell.tsx`
- Create: `_components/__tests__/ForecastCell.test.tsx`

- [ ] **Step 1: Vitest cases for each visual state**

  ```tsx
  test("baseline renders with grey-faint italic style", ...);
  test("override renders with blue-bold style", ...);
  test("changed-since-publish shows ⭐ icon", ...);
  test("frozen renders 🔒 + read-only", ...);
  ```

- [ ] **Step 2: Run tests, watch them FAIL**

- [ ] **Step 3: Implement** the cell component with Tailwind class switches based on `{ touched, isOverride, isFrozen, changedSincePublish }` props

- [ ] **Step 4: Run tests, watch them PASS**

- [ ] **Step 5: Commit**

### Task 11: Implement OrdersCell (read-only)

- [ ] **Step 1: Render qty_total + count badge**
- [ ] **Step 2: Click → drill to `/inventory?item=<id>&from=<bucket>&to=<bucket+7d>`** (or wherever the orders drill belongs)
- [ ] **Step 3: Commit**

### Task 12: Implement TotalCell + decomposition popover

- [ ] **Step 1: Use Radix UI Popover** (already in package.json)
- [ ] **Step 2: On click, render** "1,200 = 800 forecast + 400 orders (3 orders)" with sample order list
- [ ] **Step 3: Esc closes popover** (Radix default)
- [ ] **Step 4: Commit**

---

## Chunk 4: Side panel + quick actions

### Task 13: Build SidePanel shell

- [ ] **Step 1: Collapsible drawer** on the right side, takes selected SKU as prop
- [ ] **Step 2: Show item name + family + last-edited timestamp**
- [ ] **Step 3: Render placeholder for sparkline**
- [ ] **Step 4: Commit**

### Task 14: Add 12-week historical sparkline

- [ ] **Step 1: ⚠️ FIRST, verify `historical_sales` data source exists per design doc UNRESOLVED in §B.7**
  - Run: `psql -c "\dv private_core.v_historical*; \dt private_core.*sales*"` against live DB
  - If nothing → defer this task and Task 15 quick action "Copy from last year" to v3; emit `assumption_failure` and surface to Tom for decision
  - If found → document the view name + shape in the task notes
- [ ] **Step 2: Fetch via new query hook**
- [ ] **Step 3: Render with `recharts` or hand-rolled SVG (lighter)**
- [ ] **Step 4: Commit**

### Task 15: Add quick-action buttons

- [ ] **Step 1: "Copy from last year"** — uses sparkline data; auto-fills the row's 8 cells
  - SKIP this button if Task 14 was skipped
- [ ] **Step 2: "Split evenly"** — sums current row total, divides evenly across 8 buckets
- [ ] **Step 3: "+10% growth"** — multiplies each cell by 1.10
- [ ] **Step 4: "Reset row"** — clears all overrides for this row
- [ ] **Step 5: Vitest cases for each action's math**
- [ ] **Step 6: Commit**

---

## Chunk 5: Header + bottom bar + version compare

### Task 16: Header — version dropdown + bucket toggle + horizon picker

- [ ] Single-line layout · uses Radix DropdownMenu · current values from `useWorkspace`

### Task 17: Header — Publish button + freshness chip

- [ ] Reuse existing `/api/forecasts/publish` endpoint
- [ ] Disabled when zero changes; disabled while publishing
- [ ] Confirmation dialog on click (Radix Dialog)
- [ ] Freshness chip via the `FreshnessBadge` component (already enhanced in earlier loops)

### Task 18: BottomBar — "X cells changed since last publish · Review · Discard · Publish"

- [ ] Sticky to bottom of viewport
- [ ] Pulls dirty count from useWorkspace state
- [ ] "Review" toggles a filter showing only changed rows; "Discard" resets all edits with confirmation; "Publish" same as Header.Publish

### Task 19: Compare overlay (previous published version as delta)

- [ ] **Step 1: Add second query for compare-target version** (default = previous published)
- [ ] **Step 2: For each cell, compute `delta = current - compareTarget`**
- [ ] **Step 3: Show delta as a small subscript badge: `+12` green / `−5` red / blank if 0**
- [ ] **Step 4: Toggle on/off via header dropdown**
- [ ] **Step 5: Commit**

---

## Chunk 6: Keyboard navigation + Excel paste

### Task 20: Keyboard nav hook

**Files:**
- Create: `_lib/useKeyboardNav.ts`

- [ ] **Step 1: Track focused cell `(itemIdx, bucketIdx, subRowKind)`**
- [ ] **Step 2: Arrow keys move focus** (skip read-only orders sub-row)
- [ ] **Step 3: Tab/Shift+Tab same as right/left arrows**
- [ ] **Step 4: Enter commits + moves down**
- [ ] **Step 5: Esc reverts current cell + blurs**
- [ ] **Step 6: Ctrl+Z undoes last commit (LRU stack of last 50 edits)**

### Task 21: Shift-drag fill

- [ ] **Step 1: Detect mousedown on a cell + drag while shift held**
- [ ] **Step 2: Visual range highlight**
- [ ] **Step 3: On mouseup, copy source value to all cells in range**

### Task 22: Excel paste (Ctrl+V)

- [ ] **Step 1: Capture paste event on focused cell**
- [ ] **Step 2: Parse clipboard as TSV (tab-separated rows)**
- [ ] **Step 3: Fill cells starting from focus, expanding right + down**
- [ ] **Step 4: Validate qty values (numeric, ≥ 0); reject row on bad data with toast**

---

## Chunk 7: Virtualization

### Task 23: Add `@tanstack/react-virtual`

- [ ] **Step 1: Install** the package (`npm i @tanstack/react-virtual`)
- [ ] **Step 2: Replace the table body with a virtualized window**
- [ ] **Step 3: Verify scroll behavior** (sticky left rail still works)
- [ ] **Step 4: Verify keyboard nav still works** (focus-into-virtualized requires manual scroll-into-view on focus change)

### Task 24: Performance test

- [ ] **Step 1: Render at 68 items × 8 cells × 3 sub-rows = 1,632 cells**
- [ ] **Step 2: Measure paint time with Chrome DevTools Performance panel**
- [ ] **Step 3: Verify <100ms initial paint** + <16ms per scroll frame

---

## Chunk 8: RTL + Hebrew

### Task 25: RTL layout pass

- [ ] **Step 1: Wrap workspace in `<div dir="rtl">`** (or set `<html dir="rtl">` for the route only via `(planning)/layout.tsx` if Tom-locked)
- [ ] **Step 2: Verify sticky rail moves to right edge**
- [ ] **Step 3: Verify chevron/arrow icons mirror correctly** via `:dir(rtl)` CSS

### Task 26: Number cells stay LTR

- [ ] **Step 1: Wrap every numeric value in `<bdi dir="ltr">`**
- [ ] **Step 2: Verify mixed Hebrew label + LTR number renders correctly**

### Task 27: Wire Hebrew strings

- [ ] **Step 1: Replace every English string** with `HE.<key>` from `_lib/hebrew-labels.ts`
- [ ] **Step 2: Visual review** — every operator-facing string is Hebrew except numbers, dates (DD/MM/YYYY), and IDs (font-mono)

---

## Chunk 9: Tests + ship

### Task 28: Playwright real-HTTP E2E spec

**Files:**
- Create: `tests/e2e/forecast-workspace-v2.spec.ts`

- [ ] **Step 1: Login flow + navigate to a draft version v2 URL**
- [ ] **Step 2: Click "Seed all" (reused from MVP)** → 68 items appear
- [ ] **Step 3: Type qty in a cell**
- [ ] **Step 4: Press Tab + type next cell**
- [ ] **Step 5: Click Publish** → confirm dialog → verify version flips to published in DB

### Task 29: Visual regression

- [ ] **Step 1: Use Playwright `toHaveScreenshot` against the workspace at a known fixture state**
- [ ] **Step 2: Run in light mode**
- [ ] **Step 3: Run in dark mode**

### Task 30: a11y pass

- [ ] **Step 1: Tab through every interactive element** with keyboard only
- [ ] **Step 2: Verify focus rings visible**
- [ ] **Step 3: Verify aria-labels on icon-only buttons**
- [ ] **Step 4: Run axe-core via Playwright** → 0 critical violations

### Task 31: RTL pass

- [ ] **Step 1: Take screenshots in RTL mode**
- [ ] **Step 2: Verify no overflow, no flipped icons that shouldn't flip, no broken numeric input rendering**

### Task 32: Idempotency + conflict path

- [ ] **Step 1: Publish twice quickly with same idempotency key** → second returns idempotent_replay
- [ ] **Step 2: Edit a frozen cell (force via DevTools)** → verify 409 + UI rolls back the local edit + shows freeze tooltip

### Task 33: Final integration

- [ ] **Step 1: Add "Open in v2" button on MVP detail page** (`[version_id]/page.tsx`)
- [ ] **Step 2: Document migration path** in `docs/forecast_workspace_v2_release_notes.md` (where to find it, when to use v2 vs MVP, deprecation timeline for MVP)
- [ ] **Step 3: Final commit + push**

---

## Stop conditions / handoff

**Per chunk:**
- Validation gate must pass before next chunk dispatches: typecheck + build + relevant tests + visual smoke.
- `assumption_failure` (e.g. Task 14 historical_sales data not found) halts the chunk and surfaces to Tom.

**Per plan:**
- 5 retry ceiling on any task → escalate to Tom.
- contract_failure on any backend dependency (e.g. orders endpoint shape mismatch) → halt and arbitrate.

---

## Rollback

Per-task rollback: each commit can be `git revert`-ed independently.

Whole-feature rollback: the v2 route lives at a NEW path (`[version_id]/v2`) and the MVP at `[version_id]` is unchanged. Removing the v2 route is just deleting `(planning)/planning/forecast/[version_id]/v2/` and its proxy route. No DB schema changes required.

The new backend endpoint (`/api/v1/queries/orders/by-item-and-period`) is purely additive and read-only; reverting just removes the route.
