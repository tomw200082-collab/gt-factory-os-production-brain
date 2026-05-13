# Display Clamp for Physical Stock Truth — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make operator-facing portal surfaces clamp `calculated_on_hand` to `>= 0`, surface the negative as an actionable `Reconcile` badge that opens an inline drawer with the last 10 ledger events for the item, and keep all truth-layer code paths unchanged.

**Architecture:** Additive backend (4 derived fields appended to the existing `/api/v1/queries/stock` response). Three new portal primitives (`lib/stock-display.ts`, `<ReconcileBadge>`, `<StockTruthDrawer>`). Migrate the canonical `/inventory` page as the reference surface. Other surfaces (dashboard, item detail, form previews, movement log) are tracked as follow-up plans.

**Tech Stack:** Fastify + Kysely + Postgres (backend); Next.js 15 App Router + TanStack Query + Radix Dialog + Tailwind (portal); vitest + @testing-library/react + Playwright (tests).

**Spec:** [`docs/superpowers/specs/2026-05-13-display-clamp-physical-stock-truth-design.md`](../specs/2026-05-13-display-clamp-physical-stock-truth-design.md)

**Prerequisites NOT covered by this plan:**
- ~~UX handoff packet~~ — **delivered 2026-05-13** by `interaction-design-specialist` (INTER-001 through INTER-008) and `visual-system-designer` (VISUAL-001 through VISUAL-004). All decision-grade and flow-completion findings are incorporated into the task bodies below. See **Revision history** for the diff.
- Tom written approval of the spec — **already granted** 2026-05-13.

## Revision history

**2026-05-13 — handoff-packet revisions (this plan is v2):**

- **VISUAL-001 (decision-grade):** Task 6 rewritten — `StockTruthDrawer` composes the canonical `<Drawer>` primitive from `@/components/overlays/Drawer` instead of rolling a raw `Dialog.Root`. The portal already has a stack-aware drawer with built-in focus management, close button, and Esc/backdrop handling. Composing it eliminates the four divergences flagged in the audit and inherits the stack-context behavior for future drawer-within-drawer flows.
- **INTER-005 (decision-grade):** Task 7 Step 9 rewritten — `InventoryCardMobile` no longer uses `<Link>` as its outer wrapper (button-inside-link is invalid HTML). The item-name block becomes its own `<Link>` child; the `ReconcileBadge` is a sibling.
- **INTER-001 (flow-completion):** Task 5 updated — `ReconcileBadge` uses Radix Tooltip (`@radix-ui/react-tooltip`) instead of the `title` attribute (which is unreachable on touch and keyboard). Adds `disabled?: boolean` prop for role-gated cases.
- **INTER-002 (flow-completion):** Task 6 CTA `Link` carries `target="_blank" rel="noopener"`; the drawer stays open while the GR form opens in a new tab.
- **INTER-003 (flow-completion):** Task 6 error state renders prose + a Retry button that calls `refetch()`; raw API error code is hidden behind a `<details>` disclosure.
- **INTER-004 (flow-completion):** Task 6 empty-state CTA conditional on `data.rows.length === 0` — disabled "Post corrective count (coming soon)" when there are no events, since the count route may not yet exist. Executor confirms route availability before activating.
- **INTER-006 (polish):** Task 7 Step 8 — `negativeCount` useMemo scopes to `allRows` (active tab) instead of merged `[...fgRows, ...rmRows]`. One-line change.
- **VISUAL-002:** Task 5 — `ReconcileBadge` uses `ring-warning/50` (not `/40`) to match the `TierBadge.reconcile` entry and complete the ring-weight ladder (Low/30, Critical/40, Reconcile/50).
- **VISUAL-003:** Task 7 Step 3 — `TierBadge.reconcile` glyph is `◈` (diamond) instead of `⚠` to avoid collision with `CostBadge.missing_cost` which already uses `⚠`. The standalone `ReconcileBadge` (a button) keeps `⚠` — it never co-renders with a CostBadge.
- **VISUAL-004:** Task 6 — ledger event list rows use `bg-bg-subtle/60` (not `/30`) for visibility in compact mode.
- **INTER-007 (polish):** Inherited by composing `<Drawer>` (which has its own focus-management semantics). No separate focus sentinel needed.
- **New Task 4.5:** Add `@radix-ui/react-tooltip` to portal dependencies.

The acceptance criteria for each finding live next to the affected task step.

**Out of scope (explicit, deferred to follow-up plans):**
- Migration of: `/(shared)/dashboard`, `/(shared)/dashboard/v2`, `/(admin)/admin/items/[item_id]`, `/(shared)/stock/movement-log`, GR / Waste / Production Actual form previews, `/(planning)/planning/inventory-flow/*`.
- Backend `negative_on_hand_observed` exception emission (Change 3 of the four-change program).
- Explicit ATS / over-commitment view (Change 2).
- Shopify `committed` verification (Change 4).

---

## File Structure

### Backend (`gt-factory-os` repo, branch off `main`)

| File | Action | Responsibility |
|---|---|---|
| `api/src/stock/schemas.ts` | modify | Extend `StockRow` interface with 4 derived fields |
| `api/src/stock/handler.ts` | modify | Compute the 4 derived fields in SQL |
| `api/test/stock_handler_derived_fields.test.ts` | create | Integration test: hit stock handler with a fixture, assert 4 fields shape + math |

### Portal (`window2-portal-sandbox` repo, branch off `main`)

| File | Action | Responsibility |
|---|---|---|
| `src/lib/stock-display.ts` | create | Pure functions: `clampedOnHand`, `isBelowFloor`, `floorGap` |
| `src/lib/stock-display.test.ts` | create | vitest unit tests for the three pure functions |
| `src/components/stock/ReconcileBadge.tsx` | create | Standalone amber badge with tooltip |
| `src/components/stock/ReconcileBadge.test.tsx` | create | RTL render test: label, tooltip, accessibility |
| `src/components/stock/StockTruthDrawer.tsx` | create | Radix Dialog drawer; loads last 10 ledger events via TanStack Query against `/api/stock/ledger` |
| `src/components/stock/StockTruthDrawer.test.tsx` | create | RTL render test with mocked query |
| `src/app/(shared)/inventory/page.tsx` | modify | Update `OnHandCell`, `deriveTier`, `TierBadge`, filter chip, page-level alert; wire drawer |
| `tests/e2e/inventory-reconcile.spec.ts` | create | Playwright smoke against the canonical surface |

---

## Phase 1 — Backend: append derived fields to stock list response

### Task 1: Extend `StockRow` interface with derived fields

**Files:**
- Modify: `gt-factory-os/api/src/stock/schemas.ts:9-17`

- [ ] **Step 1: Edit the `StockRow` interface to declare the 4 derived fields**

In `gt-factory-os/api/src/stock/schemas.ts`, replace the existing `StockRow` interface with:

```typescript
export interface StockRow {
  site_id: string;
  item_type: string;
  item_id: string;
  display_name: string | null;
  base_uom: string | null;
  /** Raw signed projection from current_balances. May be negative when ledger sequencing produces a transient gap. */
  calculated_on_hand: string;
  /** Same as calculated_on_hand. Truth-surface alias for clarity at call sites. */
  on_hand_raw: string;
  /** GREATEST(0, calculated_on_hand) — the display value for operator-facing surfaces. */
  on_hand_display: string;
  /** True when calculated_on_hand < 0. Drives the Reconcile badge. */
  is_below_floor: boolean;
  /** GREATEST(0, -calculated_on_hand) — magnitude of the gap. Always >= 0. */
  floor_gap: string;
  last_event_at: string | null;
}
```

- [ ] **Step 2: Save the file. No test command yet; types are checked downstream.**

### Task 2: Compute the 4 derived fields in the stock handler

**Files:**
- Modify: `gt-factory-os/api/src/stock/handler.ts:14-31` and `:38-57`

- [ ] **Step 1: Update the RM_PKG SQL select clause**

In `handler.ts`, find the `if (query.item_type === 'RM_PKG')` block and replace its `select` columns with:

```typescript
const rows = await sql<StockRow>`
  select
    cb.site_id,
    cb.item_type,
    cb.item_id,
    c.component_name as display_name,
    c.inventory_uom as base_uom,
    cb.calculated_on_hand::text as calculated_on_hand,
    cb.calculated_on_hand::text as on_hand_raw,
    greatest(0, cb.calculated_on_hand)::text as on_hand_display,
    (cb.calculated_on_hand < 0) as is_below_floor,
    greatest(0, -cb.calculated_on_hand)::text as floor_gap,
    cb.last_event_at::text as last_event_at
  from private_core.current_balances cb
  left join private_core.components c
    on cb.item_type in ('RM', 'PKG') and c.component_id = cb.item_id
  where cb.site_id = 'GT-MAIN'
    and cb.item_type in ('RM', 'PKG')
    and (${itemId}::text is null or cb.item_id = ${itemId}::text)
  order by cb.item_type, cb.item_id
  limit 500
`.execute(db);
```

- [ ] **Step 2: Update the default (FG-inclusive) SQL select clause**

In the same file, find the second `sql` block (default path) and replace its `select` columns with:

```typescript
const rows = await sql<StockRow>`
  select
    cb.site_id,
    cb.item_type,
    cb.item_id,
    coalesce(i.item_name, c.component_name) as display_name,
    coalesce(i.sales_uom, c.inventory_uom) as base_uom,
    cb.calculated_on_hand::text as calculated_on_hand,
    cb.calculated_on_hand::text as on_hand_raw,
    greatest(0, cb.calculated_on_hand)::text as on_hand_display,
    (cb.calculated_on_hand < 0) as is_below_floor,
    greatest(0, -cb.calculated_on_hand)::text as floor_gap,
    cb.last_event_at::text as last_event_at
  from private_core.current_balances cb
  left join private_core.items i
    on cb.item_type = 'FG' and i.item_id = cb.item_id
  left join private_core.components c
    on cb.item_type in ('RM', 'PKG') and c.component_id = cb.item_id
  where cb.site_id = 'GT-MAIN'
    and (${itemType}::text is null or cb.item_type = ${itemType}::text)
    and (${itemId}::text is null or cb.item_id = ${itemId}::text)
  order by cb.item_type, cb.item_id
  limit 500
`.execute(db);
```

- [ ] **Step 3: Run typecheck**

```bash
cd C:/Users/tomw2/Projects/gt-factory-os/api && npx tsc --noEmit
```

Expected: 0 errors.

### Task 3: Write the integration test for derived fields

**Files:**
- Create: `gt-factory-os/api/test/stock_handler_derived_fields.test.ts`

- [ ] **Step 1: Write the failing test**

Create `gt-factory-os/api/test/stock_handler_derived_fields.test.ts`:

```typescript
import test from 'node:test';
import assert from 'node:assert/strict';
import { sql } from 'kysely';
import { getTestDb, runInTx, type TestSession } from './_test_env.js';
import { handleStockList } from '../src/stock/handler.js';

const session: TestSession = {
  user_id: '00000000-0000-0000-0000-000000000001',
  user_role: 'admin',
  display_name: 'Test Admin',
} as unknown as TestSession;

test('handleStockList — derived fields shape (all four present)', async (t) => {
  const db = await getTestDb();
  await runInTx(db, async () => {
    const result = await handleStockList(db, session, {});
    assert.equal(result.status, 200);
    const sample = result.body.rows[0];
    assert.ok(sample, 'expected at least one current_balances row');
    assert.ok('on_hand_raw' in sample);
    assert.ok('on_hand_display' in sample);
    assert.ok('is_below_floor' in sample);
    assert.ok('floor_gap' in sample);
    assert.ok('calculated_on_hand' in sample, 'backwards-compat alias preserved');
  });
});

test('handleStockList — clamp math on synthetic negative balance', async (t) => {
  const db = await getTestDb();
  await runInTx(db, async () => {
    // Seed a synthetic FG balance row directly into private_core.current_balances
    // for an isolated test item that does not exist in production data.
    const testItemId = `__TEST_NEG_${Date.now()}__`;
    await sql`
      insert into private_core.items (item_id, item_name, item_type, status, sales_uom, supply_method)
      values (${testItemId}, 'Test Negative Item', 'FG', 'ACTIVE', 'unit', 'BOUGHT_FINISHED')
      on conflict (item_id) do nothing
    `.execute(db);
    await sql`
      insert into private_core.current_balances
        (site_id, item_type, item_id, batch_id_or_empty, anchor_qty, posted_delta_sum, calculated_on_hand, last_event_at)
      values
        ('GT-MAIN', 'FG', ${testItemId}, '', 0, -5, -5, now())
      on conflict do nothing
    `.execute(db);

    const result = await handleStockList(db, session, { item_id: testItemId });
    assert.equal(result.status, 200);
    const row = result.body.rows.find((r) => r.item_id === testItemId);
    assert.ok(row, 'expected the seeded negative row to be returned');
    assert.equal(row.calculated_on_hand, '-5');
    assert.equal(row.on_hand_raw, '-5');
    assert.equal(row.on_hand_display, '0');
    assert.equal(row.is_below_floor, true);
    assert.equal(row.floor_gap, '5');
  });
});

test('handleStockList — non-negative balance produces is_below_floor=false', async (t) => {
  const db = await getTestDb();
  await runInTx(db, async () => {
    const testItemId = `__TEST_POS_${Date.now()}__`;
    await sql`
      insert into private_core.items (item_id, item_name, item_type, status, sales_uom, supply_method)
      values (${testItemId}, 'Test Positive Item', 'FG', 'ACTIVE', 'unit', 'BOUGHT_FINISHED')
      on conflict (item_id) do nothing
    `.execute(db);
    await sql`
      insert into private_core.current_balances
        (site_id, item_type, item_id, batch_id_or_empty, anchor_qty, posted_delta_sum, calculated_on_hand, last_event_at)
      values
        ('GT-MAIN', 'FG', ${testItemId}, '', 10, 0, 10, now())
      on conflict do nothing
    `.execute(db);

    const result = await handleStockList(db, session, { item_id: testItemId });
    const row = result.body.rows.find((r) => r.item_id === testItemId);
    assert.ok(row);
    assert.equal(row.is_below_floor, false);
    assert.equal(row.on_hand_display, '10');
    assert.equal(row.floor_gap, '0');
  });
});
```

- [ ] **Step 2: Run the test**

```bash
cd C:/Users/tomw2/Projects/gt-factory-os/api && npx tsx --test test/stock_handler_derived_fields.test.ts
```

Expected: 3 pass, 0 fail.

If the test environment helpers (`_test_env.ts`) do not export `getTestDb` / `runInTx` exactly, inspect `api/test/_test_env.ts` for the actual API and adjust the imports. The other tests in the directory (e.g., `goods_receipts.test.ts`) use the canonical pattern — match that exactly.

- [ ] **Step 3: Commit**

```bash
cd C:/Users/tomw2/Projects/gt-factory-os && git add api/src/stock/schemas.ts api/src/stock/handler.ts api/test/stock_handler_derived_fields.test.ts
git commit -m "$(cat <<'EOF'
feat(stock): append derived fields for display clamp

Adds on_hand_raw / on_hand_display / is_below_floor / floor_gap to the
stock list response. Pure SQL projection; no schema change; no ledger
change. Backwards compatible — calculated_on_hand preserved.

3/3 node:test green.

Spec: PRODUCTION/docs/superpowers/specs/2026-05-13-display-clamp-physical-stock-truth-design.md

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase 2 — Portal: shared primitives

### Task 4: Create the `stock-display` utility module with unit tests

**Files:**
- Create: `window2-portal-sandbox/src/lib/stock-display.ts`
- Create: `window2-portal-sandbox/src/lib/stock-display.test.ts`

- [ ] **Step 1: Write the failing test**

Create `src/lib/stock-display.test.ts`:

```typescript
import { describe, it, expect } from 'vitest';
import { clampedOnHand, isBelowFloor, floorGap } from './stock-display';

describe('clampedOnHand', () => {
  it('returns 0 for negative', () => {
    expect(clampedOnHand(-5)).toBe(0);
    expect(clampedOnHand(-0.0001)).toBe(0);
  });
  it('returns the value for zero or positive', () => {
    expect(clampedOnHand(0)).toBe(0);
    expect(clampedOnHand(0.5)).toBe(0.5);
    expect(clampedOnHand(100)).toBe(100);
  });
  it('handles string inputs', () => {
    expect(clampedOnHand('-5')).toBe(0);
    expect(clampedOnHand('10.5')).toBe(10.5);
    expect(clampedOnHand('0')).toBe(0);
  });
  it('returns NaN for non-numeric strings', () => {
    expect(Number.isNaN(clampedOnHand('not a number'))).toBe(true);
  });
});

describe('isBelowFloor', () => {
  it('is true for strictly negative', () => {
    expect(isBelowFloor(-1)).toBe(true);
    expect(isBelowFloor(-0.0001)).toBe(true);
    expect(isBelowFloor('-5')).toBe(true);
  });
  it('is false for zero and positive', () => {
    expect(isBelowFloor(0)).toBe(false);
    expect(isBelowFloor(0.5)).toBe(false);
    expect(isBelowFloor('10')).toBe(false);
  });
  it('is false for non-numeric inputs', () => {
    expect(isBelowFloor('xyz')).toBe(false);
  });
});

describe('floorGap', () => {
  it('returns magnitude for negative', () => {
    expect(floorGap(-5)).toBe(5);
    expect(floorGap(-0.5)).toBe(0.5);
    expect(floorGap('-12.3')).toBe(12.3);
  });
  it('returns 0 for zero and positive', () => {
    expect(floorGap(0)).toBe(0);
    expect(floorGap(100)).toBe(0);
  });
  it('returns 0 for non-numeric inputs', () => {
    expect(floorGap('xyz')).toBe(0);
  });
});
```

- [ ] **Step 2: Run test — expect FAIL**

```bash
cd C:/Users/tomw2/Projects/window2-portal-sandbox && npx vitest run src/lib/stock-display.test.ts
```

Expected: FAIL with "Cannot find module './stock-display'".

- [ ] **Step 3: Implement the module**

Create `src/lib/stock-display.ts`:

```typescript
/**
 * Stock display helpers.
 *
 * Backbone of the "clamp on_hand to >= 0 in operator-facing surfaces"
 * rule. Truth surfaces (audit, exceptions, parity) keep the raw value;
 * these helpers exist for the display surfaces.
 *
 * Spec: PRODUCTION/docs/superpowers/specs/2026-05-13-display-clamp-physical-stock-truth-design.md
 */

function toNumber(val: number | string): number {
  return typeof val === 'number' ? val : Number(val);
}

export function clampedOnHand(val: number | string): number {
  const n = toNumber(val);
  if (Number.isNaN(n)) return NaN;
  return Math.max(0, n);
}

export function isBelowFloor(val: number | string): boolean {
  const n = toNumber(val);
  if (Number.isNaN(n)) return false;
  return n < 0;
}

export function floorGap(val: number | string): number {
  const n = toNumber(val);
  if (Number.isNaN(n)) return 0;
  return Math.max(0, -n);
}
```

- [ ] **Step 4: Run test — expect PASS**

```bash
cd C:/Users/tomw2/Projects/window2-portal-sandbox && npx vitest run src/lib/stock-display.test.ts
```

Expected: 3 describe blocks, all `it` passing.

- [ ] **Step 5: Commit**

```bash
cd C:/Users/tomw2/Projects/window2-portal-sandbox && git add src/lib/stock-display.ts src/lib/stock-display.test.ts
git commit -m "$(cat <<'EOF'
feat(stock-display): clampedOnHand / isBelowFloor / floorGap helpers

Pure functions consumed by the upcoming ReconcileBadge and
StockTruthDrawer primitives. Strict less-than-zero rule, no precision
threshold.

Spec: PRODUCTION/docs/superpowers/specs/2026-05-13-display-clamp-physical-stock-truth-design.md

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 4.5: Add `@radix-ui/react-tooltip` dependency

**Reason:** INTER-001 requires a tooltip reachable on keyboard focus and touch, not just hover. The `title` attribute does not satisfy this.

- [ ] **Step 1: Add the package**

```bash
cd C:/Users/tomw2/Projects/window2-portal-sandbox && npm install @radix-ui/react-tooltip
```

- [ ] **Step 2: Verify it appears in package.json under `dependencies`** alongside the other `@radix-ui/*` entries.

- [ ] **Step 3: Commit the lockfile + manifest only**

```bash
cd C:/Users/tomw2/Projects/window2-portal-sandbox && git add package.json package-lock.json
git commit -m "$(cat <<'EOF'
chore(deps): add @radix-ui/react-tooltip

Required by ReconcileBadge (INTER-001) for keyboard- and touch-reachable
tooltip semantics. Existing badges that rely on the title attribute alone
will be revisited in a follow-up audit.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 5: Create the `<ReconcileBadge>` component

**Handoff-packet findings incorporated:** INTER-001 (Radix Tooltip + disabled prop), VISUAL-002 (`ring-warning/50`).

**Files:**
- Create: `window2-portal-sandbox/src/components/stock/ReconcileBadge.tsx`
- Create: `window2-portal-sandbox/src/components/stock/ReconcileBadge.test.tsx`

- [ ] **Step 1: Write the failing test**

Create `src/components/stock/ReconcileBadge.test.tsx`:

```tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom/vitest';
import * as Tooltip from '@radix-ui/react-tooltip';
import { ReconcileBadge } from './ReconcileBadge';

function renderWithTooltipProvider(ui: React.ReactNode) {
  return render(<Tooltip.Provider>{ui}</Tooltip.Provider>);
}

describe('ReconcileBadge', () => {
  it('renders a button with the label "Reconcile"', () => {
    renderWithTooltipProvider(
      <ReconcileBadge floorGap={5} uom="unit" onClick={() => {}} />,
    );
    expect(
      screen.getByRole('button', { name: /reconcile/i }),
    ).toBeInTheDocument();
  });

  it('carries a short aria-label including the gap magnitude', () => {
    renderWithTooltipProvider(
      <ReconcileBadge floorGap={5} uom="unit" onClick={() => {}} />,
    );
    const btn = screen.getByRole('button', { name: /reconcile/i });
    expect(btn).toHaveAttribute(
      'aria-label',
      expect.stringMatching(/reconcile.*5.*unit/i),
    );
  });

  it('shows tooltip content on focus', async () => {
    const user = userEvent.setup();
    renderWithTooltipProvider(
      <ReconcileBadge floorGap={5} uom="unit" onClick={() => {}} />,
    );
    await user.tab(); // focus the badge
    // Radix renders the tooltip in a portal; assert by text content.
    expect(
      await screen.findByText(/recorded outflows exceed receipts by 5\b.*unit/i),
    ).toBeInTheDocument();
  });

  it('calls onClick when activated', async () => {
    const handler = vi.fn();
    const user = userEvent.setup();
    renderWithTooltipProvider(
      <ReconcileBadge floorGap={5} uom="unit" onClick={handler} />,
    );
    await user.click(screen.getByRole('button', { name: /reconcile/i }));
    expect(handler).toHaveBeenCalledTimes(1);
  });

  it('renders as a non-interactive span when disabled', () => {
    renderWithTooltipProvider(
      <ReconcileBadge
        floorGap={5}
        uom="unit"
        onClick={() => {}}
        disabled
      />,
    );
    expect(screen.queryByRole('button', { name: /reconcile/i })).toBeNull();
    expect(screen.getByText(/reconcile/i)).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test — expect FAIL**

```bash
cd C:/Users/tomw2/Projects/window2-portal-sandbox && npx vitest run src/components/stock/ReconcileBadge.test.tsx
```

Expected: FAIL "Cannot find module './ReconcileBadge'".

- [ ] **Step 3: Implement the component**

Create `src/components/stock/ReconcileBadge.tsx`:

```tsx
"use client";

import * as Tooltip from '@radix-ui/react-tooltip';
import { cn } from '@/lib/cn';

export interface ReconcileBadgeProps {
  /** Magnitude of how far calculated_on_hand is below zero. Always >= 0. */
  floorGap: number | string;
  /** Display uom (e.g. "unit", "bottle"). */
  uom: string | null;
  /** Click handler — opens the StockTruthDrawer at the call site. */
  onClick: () => void;
  /** When true, render as a non-interactive span (role-gated case). */
  disabled?: boolean;
  /** Optional className for surface-specific positioning. */
  className?: string;
}

/**
 * Amber "Reconcile" badge surfaced when calculated_on_hand < 0.
 *
 * Spec: PRODUCTION/docs/superpowers/specs/2026-05-13-display-clamp-physical-stock-truth-design.md §4
 * Handoff: INTER-001 (Radix Tooltip + disabled prop), VISUAL-002 (ring-warning/50)
 */
export function ReconcileBadge({
  floorGap,
  uom,
  onClick,
  disabled,
  className,
}: ReconcileBadgeProps) {
  const gapDisplay = typeof floorGap === 'number' ? floorGap : Number(floorGap);
  const gapText = Number.isNaN(gapDisplay) ? '?' : String(gapDisplay);
  const uomText = uom ?? 'units';
  const tooltipBody = `Recorded outflows exceed receipts by ${gapText} ${uomText}. Click to review.`;
  const ariaShort = `Reconcile — ${gapText} ${uomText} below floor`;

  const visualBody = (
    <>
      <span aria-hidden className="font-mono">⚠</span>
      Reconcile
    </>
  );

  const sharedClass = cn(
    'inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-2xs font-medium ring-1',
    'bg-warning-softer text-warning-fg ring-warning/50',
    className,
  );

  return (
    <Tooltip.Root delayDuration={300}>
      <Tooltip.Trigger asChild>
        {disabled ? (
          <span
            role="status"
            aria-label={`${ariaShort} (action unavailable)`}
            className={cn(sharedClass, 'opacity-70 cursor-not-allowed')}
          >
            {visualBody}
          </span>
        ) : (
          <button
            type="button"
            onClick={onClick}
            aria-label={ariaShort}
            className={cn(
              sharedClass,
              'transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/50',
              'hover:bg-warning-softer/80',
            )}
          >
            {visualBody}
          </button>
        )}
      </Tooltip.Trigger>
      <Tooltip.Portal>
        <Tooltip.Content
          side="top"
          sideOffset={6}
          className="z-50 rounded border border-border bg-bg-raised px-2 py-1 text-2xs text-fg shadow-md"
        >
          {tooltipBody}
          <Tooltip.Arrow className="fill-bg-raised" />
        </Tooltip.Content>
      </Tooltip.Portal>
    </Tooltip.Root>
  );
}
```

**Important:** Every call site that mounts `<ReconcileBadge>` MUST be inside a `<Tooltip.Provider>`. The inventory page (Task 7) wraps the entire page in `<Tooltip.Provider>` once, near the outermost return.

- [ ] **Step 4: Run test — expect PASS**

```bash
cd C:/Users/tomw2/Projects/window2-portal-sandbox && npx vitest run src/components/stock/ReconcileBadge.test.tsx
```

Expected: 3/3 pass.

- [ ] **Step 5: Commit**

```bash
cd C:/Users/tomw2/Projects/window2-portal-sandbox && git add src/components/stock/ReconcileBadge.tsx src/components/stock/ReconcileBadge.test.tsx
git commit -m "$(cat <<'EOF'
feat(stock-display): ReconcileBadge component

Amber-toned warning badge with tooltip describing the floor_gap.
Click handler delegated to the call site (opens StockTruthDrawer).

3/3 vitest green.

Spec: PRODUCTION/docs/superpowers/specs/2026-05-13-display-clamp-physical-stock-truth-design.md §4

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Task 6: Create the `<StockTruthDrawer>` component

**Handoff-packet findings incorporated:** VISUAL-001 (compose canonical `<Drawer>`), INTER-002 (`target="_blank"` CTA), INTER-003 (Retry button), INTER-004 (conditional empty-state CTA), VISUAL-004 (`bg-bg-subtle/60` row alpha).

**Files:**
- Create: `window2-portal-sandbox/src/components/stock/StockTruthDrawer.tsx`
- Create: `window2-portal-sandbox/src/components/stock/StockTruthDrawer.test.tsx`

- [ ] **Step 1: Write the failing test**

Create `src/components/stock/StockTruthDrawer.test.tsx`:

```tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import '@testing-library/jest-dom/vitest';
import { StockTruthDrawer } from './StockTruthDrawer';

function renderWithQuery(ui: React.ReactNode) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(<QueryClientProvider client={client}>{ui}</QueryClientProvider>);
}

const baseProps = {
  itemId: 'X-001',
  itemType: 'FG',
  displayName: 'Test Beverage',
  onHandRaw: '-5',
  floorGap: '5',
  uom: 'unit',
};

describe('StockTruthDrawer', () => {
  it('does not render when closed', () => {
    renderWithQuery(
      <StockTruthDrawer {...baseProps} open={false} onClose={() => {}} />,
    );
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('renders math summary, title, and ledger event when open', async () => {
    const fetchSpy = vi.spyOn(global, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({
        rows: [
          {
            movement_id: 'm1',
            movement_type: 'WASTE_POSTED',
            item_type: 'FG',
            item_id: 'X-001',
            qty_delta: '-5',
            uom: 'unit',
            event_at: '2026-05-10T10:00:00Z',
            posted_at: '2026-05-10T10:00:00Z',
            post_status: 'POSTED',
            reported_by_snapshot: 'Alex',
          },
        ],
        count: 1,
        total_matching: 1,
      }),
    } as Response);

    renderWithQuery(
      <StockTruthDrawer {...baseProps} open={true} onClose={() => {}} />,
    );

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });
    // Title in the canonical Drawer header.
    expect(screen.getByText('Test Beverage')).toBeInTheDocument();
    expect(screen.getByText(/Below physical floor by 5/i)).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText('WASTE_POSTED')).toBeInTheDocument();
    });
    // CTA opens in a new tab (INTER-002).
    const cta = screen.getByRole('link', { name: /Post corrective Goods Receipt/i });
    expect(cta).toHaveAttribute('target', '_blank');
    expect(cta).toHaveAttribute('rel', expect.stringContaining('noopener'));

    fetchSpy.mockRestore();
  });

  it('renders Try again button on error and calls refetch (INTER-003)', async () => {
    const fetchSpy = vi
      .spyOn(global, 'fetch')
      .mockResolvedValueOnce({ ok: false, status: 500, json: async () => ({}) } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ rows: [], count: 0, total_matching: 0 }),
      } as Response);

    renderWithQuery(
      <StockTruthDrawer {...baseProps} open={true} onClose={() => {}} />,
    );

    const retry = await screen.findByRole('button', { name: /try again/i });
    expect(retry).toBeInTheDocument();
    // Raw API code is not surfaced in the default error state.
    expect(screen.queryByText(/LEDGER_FETCH_500/)).toBeNull();

    fetchSpy.mockRestore();
  });

  it('renders the no-events disabled CTA when ledger is empty (INTER-004)', async () => {
    const fetchSpy = vi.spyOn(global, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({ rows: [], count: 0, total_matching: 0 }),
    } as Response);

    renderWithQuery(
      <StockTruthDrawer {...baseProps} open={true} onClose={() => {}} />,
    );

    // GR link should not be present.
    await waitFor(() => {
      expect(
        screen.queryByRole('link', { name: /Post corrective Goods Receipt/i }),
      ).toBeNull();
    });
    // Disabled count-corrective span should be present.
    expect(screen.getByText(/Post corrective count/i)).toBeInTheDocument();
    expect(screen.getByText(/Post corrective count/i)).toHaveAttribute(
      'aria-disabled',
      'true',
    );

    fetchSpy.mockRestore();
  });
});
```

- [ ] **Step 2: Run test — expect FAIL**

```bash
cd C:/Users/tomw2/Projects/window2-portal-sandbox && npx vitest run src/components/stock/StockTruthDrawer.test.tsx
```

Expected: FAIL "Cannot find module './StockTruthDrawer'".

- [ ] **Step 3: Implement the component**

Create `src/components/stock/StockTruthDrawer.tsx`:

```tsx
"use client";

import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { Drawer } from '@/components/overlays/Drawer';
import { cn } from '@/lib/cn';

interface LedgerEvent {
  movement_id: string;
  movement_type: string;
  qty_delta: string;
  uom: string;
  event_at: string;
  posted_at: string;
  post_status: string;
  reported_by_snapshot: string | null;
  po_number?: string | null;
  supplier_name?: string | null;
  lw_destination_city?: string | null;
}

interface LedgerResponse {
  rows: LedgerEvent[];
  count: number;
  total_matching: number;
}

async function fetchRecentLedger(itemId: string): Promise<LedgerResponse> {
  const url = `/api/stock/ledger?item_id=${encodeURIComponent(itemId)}&limit=10`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`LEDGER_FETCH_${res.status}`);
  return res.json() as Promise<LedgerResponse>;
}

export interface StockTruthDrawerProps {
  itemId: string;
  itemType: string;
  displayName: string | null;
  /** Raw signed on-hand (string form from the API). */
  onHandRaw: string;
  /** Magnitude of the gap below floor (string form). */
  floorGap: string;
  uom: string | null;
  open: boolean;
  onClose: () => void;
}

/**
 * Stock Truth Drawer — opens from a Reconcile badge click.
 *
 * Shows:
 *   - Header (delegated to <Drawer>): item name + itemId · itemType
 *   - Math summary block: floor gap, calculated vs display value, prose explanation
 *   - Recent ledger events (last 10) for the item
 *   - CTA: Post corrective Goods Receipt (opens in new tab; drawer stays open)
 *
 * Composes the canonical <Drawer> primitive (VISUAL-001).
 *
 * Spec: PRODUCTION/docs/superpowers/specs/2026-05-13-display-clamp-physical-stock-truth-design.md §4.2
 */
export function StockTruthDrawer({
  itemId,
  itemType,
  displayName,
  onHandRaw,
  floorGap,
  uom,
  open,
  onClose,
}: StockTruthDrawerProps) {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['stock-truth-drawer', itemId],
    queryFn: () => fetchRecentLedger(itemId),
    enabled: open,
    staleTime: 30_000,
  });

  const hasEvents = data ? data.rows.length > 0 : false;

  return (
    <Drawer
      open={open}
      onClose={onClose}
      title={displayName ?? itemId}
      description={`${itemId} · ${itemType}`}
      width="md"
    >
      {/* Math summary */}
      <div className="rounded-md border border-warning/30 bg-warning-softer/40 p-3 text-sm">
        <div className="font-medium text-warning-fg">
          Below physical floor by {floorGap} {uom ?? 'units'}
        </div>
        <div className="mt-2 space-y-0.5 font-mono text-xs text-fg-muted">
          <div>Calculated on-hand : {onHandRaw}</div>
          <div>Display value      : 0</div>
        </div>
        <p className="mt-2 text-2xs text-fg-muted">
          The system has recorded more outflow events than offsetting
          receipts. Likely causes: a missing Goods Receipt, an
          out-of-sequence shipment post, or an under-counted physical
          count. Investigate below.
        </p>
      </div>

      {/* Recent ledger events */}
      <h3 className="mt-5 text-2xs font-semibold uppercase tracking-wider text-fg-subtle">
        Recent ledger events
      </h3>
      {isLoading && (
        <div className="mt-2 space-y-1.5" aria-busy="true">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-7 animate-pulse rounded bg-bg-subtle" />
          ))}
        </div>
      )}
      {isError && (
        <div
          className="mt-2 rounded-md border border-danger/40 bg-danger-softer/40 p-3 text-xs text-danger-fg"
          role="alert"
        >
          <p>Could not load ledger events.</p>
          <button
            type="button"
            onClick={() => refetch()}
            className="mt-2 inline-flex items-center gap-1 rounded border border-danger/40 bg-bg px-2 py-0.5 text-2xs font-medium text-danger-fg hover:bg-danger-softer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/50"
          >
            Try again
          </button>
        </div>
      )}
      {data && data.rows.length === 0 && (
        <p className="mt-2 text-xs text-fg-muted">
          No ledger events found for this item. The anchor itself may be wrong — a corrective physical count will repair the projection.
        </p>
      )}
      {data && data.rows.length > 0 && (
        <ul className="mt-2 space-y-1.5">
          {data.rows.map((ev) => (
            <li
              key={ev.movement_id}
              className="flex items-center justify-between gap-2 rounded border border-border/50 bg-bg-subtle/60 px-2 py-1 text-2xs"
            >
              <div className="min-w-0 flex-1">
                <div className="truncate font-medium text-fg">{ev.movement_type}</div>
                <div className="truncate text-fg-muted">
                  {new Date(ev.event_at).toLocaleString('en-GB', {
                    day: '2-digit',
                    month: 'short',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                  {ev.reported_by_snapshot ? ` · ${ev.reported_by_snapshot}` : ''}
                  {ev.po_number ? ` · PO ${ev.po_number}` : ''}
                  {ev.lw_destination_city ? ` · → ${ev.lw_destination_city}` : ''}
                </div>
              </div>
              <div className={cn(
                'shrink-0 font-mono tabular-nums',
                Number(ev.qty_delta) < 0 ? 'text-danger-fg' : 'text-success-fg',
              )}>
                {Number(ev.qty_delta) > 0 ? '+' : ''}{ev.qty_delta} {ev.uom}
              </div>
            </li>
          ))}
        </ul>
      )}

      {/* CTA — opens in a new tab to preserve drawer context (INTER-002).
          When there are no ledger events, the CTA is gated to a count-corrective
          path (INTER-004). Until the count form route is confirmed by the
          executor, render the no-events case as a disabled span. */}
      <div className="mt-6 flex items-center justify-between gap-2">
        {hasEvents ? (
          <Link
            href={`/stock/receipts?item_id=${encodeURIComponent(itemId)}`}
            target="_blank"
            rel="noopener"
            className="btn btn-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/50"
          >
            Post corrective Goods Receipt
          </Link>
        ) : (
          <span
            aria-disabled="true"
            title="Physical-count form route pending — see follow-up plan."
            className="btn btn-sm cursor-not-allowed opacity-50"
          >
            Post corrective count (coming soon)
          </span>
        )}
      </div>
    </Drawer>
  );
}
```

**Executor note on INTER-004 fallback:** before merging, verify whether the portal already exposes a physical-count form route reachable from `/stock/counts` (or equivalent). If yes, swap the disabled `<span>` for an enabled `<Link href="/stock/counts?item_id=...">`. If no, leave the disabled fallback in place and open a follow-up issue.

- [ ] **Step 4: Run test — expect PASS**

```bash
cd C:/Users/tomw2/Projects/window2-portal-sandbox && npx vitest run src/components/stock/StockTruthDrawer.test.tsx
```

Expected: 2/2 pass. If the Radix Dialog requires polyfilled `ResizeObserver` or `IntersectionObserver` under happy-dom, the test may need a `vi.stubGlobal` shim — check `vitest.config.ts` for the configured setup file and add stubs there if missing.

- [ ] **Step 5: Commit**

```bash
cd C:/Users/tomw2/Projects/window2-portal-sandbox && git add src/components/stock/StockTruthDrawer.tsx src/components/stock/StockTruthDrawer.test.tsx
git commit -m "$(cat <<'EOF'
feat(stock-display): StockTruthDrawer component

Radix Dialog right-side drawer triggered from ReconcileBadge clicks.
Loads last 10 ledger events for the item via TanStack Query. Shows
ledger math summary + corrective-receipt CTA.

2/2 vitest green.

Spec: PRODUCTION/docs/superpowers/specs/2026-05-13-display-clamp-physical-stock-truth-design.md §4.2

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase 3 — Migrate `/inventory` page

The current `/(shared)/inventory/page.tsx` displays negatives in parentheses with a "Negative" tier badge (50-iteration UX work). This task replaces that semantics with the clamp + Reconcile model, while preserving the existing surrounding UX (KPIs, filters, sorting, density toggle, mobile cards).

### Task 7: Migrate `OnHandCell` and `deriveTier` to clamp + Reconcile

**Files:**
- Modify: `window2-portal-sandbox/src/app/(shared)/inventory/page.tsx`

- [ ] **Step 1: Update the `StockRow` type at the top of the file to include the new fields**

Find the `StockRow` interface (around line 82) and replace with:

```typescript
interface StockRow {
  site_id: string;
  item_type: string;
  item_id: string;
  display_name: string | null;
  base_uom: string | null;
  calculated_on_hand: string;
  on_hand_raw: string;
  on_hand_display: string;
  is_below_floor: boolean;
  floor_gap: string;
  last_event_at: string | null;
}
```

- [ ] **Step 2: Replace `deriveTier` to emit `reconcile` instead of `negative`**

Find the `Tier` type and `deriveTier` function (around lines 110 and 210). Replace with:

```typescript
type Tier = "healthy" | "low" | "critical" | "out" | "reconcile" | "unknown";

function deriveTier(onHandRaw: string): Tier {
  const n = Number(onHandRaw);
  if (isNaN(n)) return "unknown";
  if (n < 0) return "reconcile";
  if (n === 0) return "out";
  if (n < CRITICAL_STOCK_THRESHOLD) return "critical";
  if (n < LOW_STOCK_THRESHOLD) return "low";
  return "healthy";
}
```

- [ ] **Step 3: Update `TierBadge` to render Reconcile instead of Negative**

**VISUAL-003 finding:** the `TierBadge.reconcile` glyph must NOT be `⚠` because `CostBadge.missing_cost` already uses `⚠` on the same row. Use `◈` (diamond) for `TierBadge.reconcile`.

Find the `TierBadge` component (around line 293) and update its `meta` table:

```tsx
function TierBadge({ tier }: { tier: Tier }) {
  const meta: Record<Tier, { label: string; cls: string; glyph: string }> = {
    healthy:    { label: "Healthy",    cls: "bg-success-softer text-success-fg ring-success/20", glyph: "●" },
    low:        { label: "Low",        cls: "bg-warning-softer text-warning-fg ring-warning/30", glyph: "◐" },
    critical:   { label: "Critical",   cls: "bg-warning-softer text-warning-fg ring-warning/40", glyph: "◑" },
    out:        { label: "Out",        cls: "bg-danger-softer text-danger-fg ring-danger/30",    glyph: "◯" },
    reconcile:  { label: "Reconcile",  cls: "bg-warning-softer text-warning-fg ring-warning/50", glyph: "◈" },
    unknown:    { label: "Unknown",    cls: "bg-bg-subtle text-fg-subtle ring-border",            glyph: "?" },
  };
  const m = meta[tier];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-2xs font-medium ring-1",
        m.cls,
      )}
    >
      <span aria-hidden className="font-mono">{m.glyph}</span>
      {m.label}
    </span>
  );
}
```

- [ ] **Step 4: Replace `OnHandCell` to clamp display and emit the Reconcile badge**

Find the `OnHandCell` component (around line 376). Replace with:

```tsx
function OnHandCell({
  row,
  onReconcileClick,
}: {
  row: StockRow;
  onReconcileClick: (row: StockRow) => void;
}) {
  const tier = deriveTier(row.on_hand_raw);
  const displayN = Number(row.on_hand_display);
  return (
    <span className="inline-flex items-baseline justify-end gap-1.5 tabular-nums">
      <span
        className={cn(
          "font-medium",
          tier === "reconcile"
            ? "text-warning-fg"
            : tier === "out"
            ? "text-fg-muted"
            : tier === "critical" || tier === "low"
            ? "text-warning-fg"
            : displayN === 0
            ? "text-fg-subtle"
            : "text-fg",
        )}
      >
        {isNaN(displayN) ? row.on_hand_display : displayN.toFixed(2)}
      </span>
      {row.base_uom ? (
        <span className="text-2xs uppercase text-fg-subtle">{row.base_uom}</span>
      ) : null}
      {row.is_below_floor ? (
        <ReconcileBadge
          floorGap={row.floor_gap}
          uom={row.base_uom}
          onClick={() => onReconcileClick(row)}
        />
      ) : null}
    </span>
  );
}
```

- [ ] **Step 5: Add the imports for the new primitives**

At the top of the file, alongside the other imports:

```tsx
import { useState } from "react"; // ensure useState is in the existing react import
import * as Tooltip from "@radix-ui/react-tooltip";
import { ReconcileBadge } from "@/components/stock/ReconcileBadge";
import { StockTruthDrawer } from "@/components/stock/StockTruthDrawer";
```

(If `useState` is already imported, leave it.)

**Tooltip provider wrap:** in the page's final return statement, wrap the entire `<div className="space-y-5 sm:space-y-6">…</div>` in `<Tooltip.Provider>…</Tooltip.Provider>`. The provider does not render visible DOM; it scopes Radix tooltip portals to this page. Without it, the `ReconcileBadge` tooltips will throw a console warning.

- [ ] **Step 6: Add drawer state and handler inside `InventoryPage`**

Inside `InventoryPage()` (around line 642), add after the existing state declarations:

```tsx
const [drawerRow, setDrawerRow] = useState<StockRow | null>(null);

function handleReconcileClick(row: StockRow) {
  setDrawerRow(row);
}
```

- [ ] **Step 7: Update the filter chip "Negative" → "Reconcile"**

Find the filter chip list (around line 1073) and update the entry:

```tsx
{ value: "reconcile", label: "Reconcile" },
```

…replacing the `{ value: "negative", label: "Negative" }` entry. Also update the `tierFilter === "negative"` branch in the filter logic (around line 745) to `tierFilter === "reconcile"`.

- [ ] **Step 8: Update the page-level alert and its trigger**

Find the negative-stock alert block (around line 936) and replace with:

```tsx
{negativeCount > 0 ? (
  <div
    className="flex items-start gap-2 rounded-md border border-warning/40 bg-warning-softer/40 px-3 py-2 text-sm text-warning-fg"
    role="alert"
  >
    <span aria-hidden>⚠</span>
    <span>
      <strong className="font-semibold">{negativeCount}</strong> item
      {negativeCount === 1 ? "" : "s"} below physical floor. Recorded outflow
      events exceed receipts. Each item shown clamped to zero with a Reconcile
      badge — click the badge for the offending ledger events.{" "}
      <button
        type="button"
        onClick={() => setTierFilter("reconcile")}
        className="underline hover:no-underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/50"
      >
        Show only these →
      </button>
    </span>
  </div>
) : null}
```

**INTER-006 fix — also update the `negativeCount` useMemo (around line 814) to scope to the active tab:**

```tsx
const negativeCount = useMemo(() => {
  return allRows.filter((r) => Number(r.calculated_on_hand) < 0).length;
}, [allRows]);
```

Previously this merged `[...fgRows, ...rmRows]` and fired the alert even when the active tab had no reconcile rows. Scoping to `allRows` (which is already tab-scoped at line 706) eliminates the alert / list mismatch.

The variable name `negativeCount` is preserved to keep this commit small; rename to `reconcileCount` later if desired.

- [ ] **Step 9: Update desktop table + restructure `InventoryCardMobile`**

**Desktop table** (around line 1339). Replace:

```tsx
<OnHandCell value={row.calculated_on_hand} uom={row.base_uom} />
```

with:

```tsx
<OnHandCell row={row} onReconcileClick={handleReconcileClick} />
```

Update the negative-row left-border accent on the `<tr>` (line ~1310): replace the `tier === "negative"` branch with `tier === "reconcile"`. Keep `/60` alpha; switch family from `danger` to `warning`:

```tsx
tier === "reconcile"
  ? "border-l-4 border-l-warning/60"
  : tier === "out"
  ? "border-l-4 border-l-warning/30"
  : "",
```

**`InventoryCardMobile` — STRUCTURAL CHANGE per INTER-005.** The current `InventoryCardMobile` uses `<Link>` as its outer wrapper. The new `ReconcileBadge` is a `<button>`. Nesting a button inside a link is invalid HTML and breaks the badge click on most browsers. Restructure:

```tsx
function InventoryCardMobile({
  row,
  value,
  onReconcileClick,
}: {
  row: StockRow;
  value: ValueMeta | null;
  onReconcileClick: (row: StockRow) => void;
}) {
  const tier = deriveTier(row.on_hand_raw);
  const cost = deriveCostStatus(row.item_type, value);
  const date = smartRelativeDate(row.last_event_at);
  const totalVal = fmtIlsAccountancy(value?.total_value ?? null);
  return (
    <article
      className={cn(
        "flex flex-col gap-2 rounded-lg border bg-bg px-3 py-3 transition hover:bg-bg-subtle/40",
        tier === "reconcile"
          ? "border-l-4 border-l-warning/60 border-y-border/70 border-r-border/70"
          : tier === "out"
          ? "border-l-4 border-l-warning/30 border-y-border/70 border-r-border/70"
          : "border-border/70",
      )}
    >
      <div className="flex items-start justify-between gap-2">
        <Link
          href={`/admin/masters/items/${encodeURIComponent(row.item_id)}`}
          className="min-w-0 flex-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/50"
          title={row.display_name ?? row.item_id}
        >
          <div className="truncate text-sm font-medium text-fg">
            {row.display_name ?? row.item_id}
          </div>
          <div className="mt-0.5 flex items-center gap-1.5 font-mono text-2xs text-fg-subtle">
            <span className="truncate">{row.item_id}</span>
            <SupplyMethodBadge method={value?.supply_method ?? null} />
          </div>
        </Link>
        <div className="text-right tabular-nums">
          <OnHandCell row={row} onReconcileClick={onReconcileClick} />
        </div>
      </div>
      <div className="flex flex-wrap items-center gap-1.5">
        <TierBadge tier={tier} />
        {cost === "has_cost" ? (
          <span className="text-2xs font-medium tabular-nums text-fg-muted">
            {totalVal.display}
          </span>
        ) : (
          <CostBadge status={cost} />
        )}
        <StaleBadge daysAgo={date.daysAgo} />
        <span className="ml-auto text-2xs text-fg-subtle" title={date.aria}>
          {date.label}
        </span>
      </div>
    </article>
  );
}
```

Key changes vs the existing component:
- Outer wrapper: `<Link>` → `<article>`. No interactive nesting.
- Item name + SKU block: own `<Link>` child. Operator can tap to navigate.
- `OnHandCell` is a sibling, not a descendant of the Link. The badge click works.
- New `onReconcileClick` prop, forwarded to `OnHandCell`.
- Tier branch updated: `negative` → `reconcile`; family `danger` → `warning` at `/60`.

In the mobile card list usage (around line 1387), pass `onReconcileClick={handleReconcileClick}` down to `InventoryCardMobile`.

- [ ] **Step 10: Mount the drawer at the bottom of the page**

At the very end of `InventoryPage`'s return statement (just before the closing `</div>` that wraps the page), add:

```tsx
{drawerRow ? (
  <StockTruthDrawer
    itemId={drawerRow.item_id}
    itemType={drawerRow.item_type}
    displayName={drawerRow.display_name}
    onHandRaw={drawerRow.on_hand_raw}
    floorGap={drawerRow.floor_gap}
    uom={drawerRow.base_uom}
    open={true}
    onClose={() => setDrawerRow(null)}
  />
) : null}
```

- [ ] **Step 11: Run typecheck**

```bash
cd C:/Users/tomw2/Projects/window2-portal-sandbox && npx tsc --noEmit
```

Expected: 0 errors related to the inventory page or new components.

- [ ] **Step 12: Run vitest to confirm shared primitives still pass**

```bash
cd C:/Users/tomw2/Projects/window2-portal-sandbox && npx vitest run src/lib/stock-display.test.ts src/components/stock
```

Expected: all previously green tests still green.

### Task 8: Playwright smoke for the migrated `/inventory` surface

**Files:**
- Create: `window2-portal-sandbox/tests/e2e/inventory-reconcile.spec.ts`

- [ ] **Step 1: Inspect the existing Playwright test config + fixture conventions**

```bash
cd C:/Users/tomw2/Projects/window2-portal-sandbox && ls tests/e2e
```

Look for an existing spec that already authenticates a fake session and queries the stock list (e.g., a spec that touches `/stock` or `/inventory`). Match its fixture / auth pattern.

- [ ] **Step 2: Write the Playwright spec**

Create `tests/e2e/inventory-reconcile.spec.ts`. The exact auth setup depends on the project's existing test pattern; mirror it. The assertions are:

```typescript
import { test, expect } from '@playwright/test';

test.describe('Inventory — Reconcile (display clamp)', () => {
  test('rows with calculated_on_hand < 0 show 0 + Reconcile badge', async ({ page }) => {
    // Mirror the project's existing auth/login helper.
    // ... (e.g., await loginAsAdmin(page))

    await page.goto('/inventory');
    await page.waitForLoadState('networkidle');

    // Filter to the Reconcile tier to isolate the rows under test.
    await page.getByRole('button', { name: /^Reconcile$/ }).click();

    // The first listed row must show "0.00" as its numeric and a Reconcile badge.
    const firstRow = page.locator('[data-testid="inventory-desktop"] tbody tr').first();
    await expect(firstRow).toBeVisible();
    await expect(firstRow.getByText('0.00').first()).toBeVisible();
    await expect(firstRow.getByRole('button', { name: /reconcile/i })).toBeVisible();
  });

  test('clicking the Reconcile badge opens the StockTruthDrawer', async ({ page }) => {
    // (auth helper)
    await page.goto('/inventory');
    await page.waitForLoadState('networkidle');
    await page.getByRole('button', { name: /^Reconcile$/ }).click();

    const firstReconcileBadge = page.getByRole('button', { name: /reconcile/i }).first();
    await firstReconcileBadge.click();

    await expect(page.getByRole('dialog')).toBeVisible();
    await expect(page.getByText(/Below physical floor by/i)).toBeVisible();
    await expect(page.getByRole('link', { name: /Post corrective Goods Receipt/i })).toBeVisible();
  });

  test('rows with non-negative balance do NOT show Reconcile badge', async ({ page }) => {
    await page.goto('/inventory');
    await page.waitForLoadState('networkidle');
    // Filter to Healthy or All; assert at least one row exists without a Reconcile badge.
    await page.getByRole('button', { name: /^All$/ }).click();
    const anyRow = page.locator('[data-testid="inventory-desktop"] tbody tr').first();
    await expect(anyRow).toBeVisible();
    // Use locator filter to find a row that does NOT contain the Reconcile badge.
    const cleanRow = page.locator('[data-testid="inventory-desktop"] tbody tr', {
      hasNot: page.getByRole('button', { name: /reconcile/i }),
    }).first();
    await expect(cleanRow).toBeVisible();
  });
});
```

**Important:** the auth setup is intentionally a comment-only placeholder because each project's helper differs. Replace the `// (auth helper)` lines with the project's actual login helper (look at an existing spec that already runs against `/inventory` or any authenticated route).

- [ ] **Step 3: Run the spec**

```bash
cd C:/Users/tomw2/Projects/window2-portal-sandbox && npx playwright test tests/e2e/inventory-reconcile.spec.ts
```

Expected: 3/3 pass.

If the spec fails because there are no `calculated_on_hand < 0` rows in the test DB, either: (a) seed a synthetic negative row at spec setup using the same technique as the backend test (Task 3), or (b) downgrade the assertion to "if at least one Reconcile row exists, the rules hold" and document the test is data-dependent.

- [ ] **Step 4: Commit**

```bash
cd C:/Users/tomw2/Projects/window2-portal-sandbox && git add src/app/'(shared)'/inventory/page.tsx tests/e2e/inventory-reconcile.spec.ts
git commit -m "$(cat <<'EOF'
feat(inventory): clamp on_hand display + Reconcile badge + drawer

Replaces the "Negative" tier semantics on /inventory with the clamp +
Reconcile model. Negative rows render as 0 plus an amber Reconcile
badge; clicking opens StockTruthDrawer with the last 10 ledger events
and a corrective-GR CTA. Page-level alert language updated.

Truth-surface code paths (rebuild_verifier, planning inputs, audit)
unchanged. Backend response is backwards-compatible.

Playwright smoke: 3/3 green.

Spec: PRODUCTION/docs/superpowers/specs/2026-05-13-display-clamp-physical-stock-truth-design.md

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase 4 — Final verification

### Task 9: Run full backend test suite

- [ ] **Step 1: Run all backend tests**

```bash
cd C:/Users/tomw2/Projects/gt-factory-os/api && npm test
```

Expected: all tests green. If any previously-passing test fails because it expected the old `StockRow` shape, update it to assert against the additive fields without removing the legacy `calculated_on_hand` assertion.

### Task 10: Run full portal test suite

- [ ] **Step 1: Run vitest unit tests**

```bash
cd C:/Users/tomw2/Projects/window2-portal-sandbox && npm test
```

Expected: all tests green.

- [ ] **Step 2: Run typecheck**

```bash
cd C:/Users/tomw2/Projects/window2-portal-sandbox && npm run typecheck
```

Expected: 0 errors.

- [ ] **Step 3: Run lint**

```bash
cd C:/Users/tomw2/Projects/window2-portal-sandbox && npm run lint
```

Expected: 0 errors. Warnings may exist; address them only if they touch files modified by this plan.

### Task 11: Final summary commit on PRODUCTION

- [ ] **Step 1: Update CURRENT_STATE.md with the closed milestone**

In `PRODUCTION/CURRENT_STATE.md` §"What is complete / partial / missing" → "Complete", add a one-line entry:

```
- Stock Truth Layering Change 1 — display clamp + Reconcile badge + StockTruthDrawer on /inventory (spec 2026-05-13, plan 2026-05-13)
```

- [ ] **Step 2: Commit the state update**

```bash
cd "c:/Users/tomw2/GTeveryday Dropbox/Data Center/Tom/AI Agents & Projects/Code Agents/PRODUCTION" && git add CURRENT_STATE.md
git commit -m "$(cat <<'EOF'
chore(state): mark Stock Truth Layering Change 1 complete

Plan landed on portal main + gt-factory-os main (or whichever branch
the executor used; update the message accordingly). /inventory page is
the canonical surface; other surface migrations tracked as follow-up.

Spec:  PRODUCTION/docs/superpowers/specs/2026-05-13-display-clamp-physical-stock-truth-design.md
Plan:  PRODUCTION/docs/superpowers/plans/2026-05-13-display-clamp-physical-stock-truth.md

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Follow-up plans (out of scope for this plan)

| Plan | Trigger |
|---|---|
| Migration of remaining surfaces (dashboard, item detail, GR/Waste/Production-Actual previews, movement-log) | After this plan ships and the pattern is validated on `/inventory` |
| Change 3 — `negative_on_hand_observed` exception emission + repair workflow | After this plan ships |
| Change 2 — explicit ATS / over-commitment view in `v_fg_availability` | After `orders_mirror` lands (Tranche 4) |
| Change 4 — Shopify `committed` field verification in drift detector | After Shopify v2 flips to live (Gate E close) |

---

## Spec-coverage self-review

| Spec section | Covered by |
|---|---|
| §1 problem statement | All tasks |
| §2 non-goals | Explicitly preserved — no CHECK constraint, no exception (Change 3), no Shopify change |
| §3.1 display rule (`on_hand_raw`, `on_hand_display`, `is_below_floor`, `floor_gap`) | Tasks 1, 2, 4 (backend SQL + portal util) |
| §3.2 surface map (clamp surfaces) | Task 7 (inventory page) + follow-up plan for the rest |
| §3.3 truth-surface preservation | Backend keeps `calculated_on_hand`; no truth-surface code touched |
| §3.4 integration boundary (Shopify push) | Untouched, as required |
| §4.1 badge anatomy | Task 5 (`<ReconcileBadge>`) |
| §4.2 drawer anatomy | Task 6 (`<StockTruthDrawer>`) |
| §4.3 what the drawer does not do | Drawer body has no edit affordance, no force-balance, no auto-suggest qty — Task 6 |
| §5.1 backend additive fields | Tasks 1–3 |
| §5.2 portal utility + components | Tasks 4–6 |
| §5.3 new endpoint | **Resolved as no-op** — existing `/api/v1/queries/stock/ledger` covers the need |
| §6 empty / edge states | Task 6 (drawer handles "no events" path) + the badge fires strictly on `< 0` (Task 5) |
| §7 accessibility | Task 5 (badge `aria-label`, focus ring) + Task 6 (Radix Dialog focus trap) |
| §8 test posture | Task 3 (backend) + Tasks 4-6 (vitest) + Task 8 (Playwright) |
| §9 rollback | All commits are atomic; revert per commit |
| §10 dependency map | Reflected in Phase ordering and out-of-scope list |
| §11 UNRESOLVED carry-forward | Inherited, not invented |
| §12 what this spec is NOT | Mirrored in "out of scope" |
| §13 approval gates | UX handoff flagged as **[UX-GATED]** on Tasks 5, 6 |

---

**End of plan.**
