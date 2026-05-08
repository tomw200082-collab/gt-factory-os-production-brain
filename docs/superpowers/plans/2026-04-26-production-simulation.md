# Production Simulation Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the per-BOM simulation with a product-first Production Simulation page that automatically combines BASE (liquid) and PACK (packaging) BOMs into one unified material requirements view.

**Architecture:** New planner page at `/planning/production-simulation`. Requires extending `ItemDto` with `primary_bom_head_id` and `base_bom_head_id`, updating the boms repository with a product-level fetch, and building the page from scratch with a product selector, merged results table, and stock coverage panel.

**Tech Stack:** Next.js 15 App Router, TypeScript, TanStack Query, react-hook-form, Zod, Tailwind, shadcn/ui, existing portal component library.

**Spec:** `docs/superpowers/specs/2026-04-26-master-data-ux-overhaul-design.md` — Stream 1

**Runs in parallel with:** `2026-04-26-admin-master-data-ux.md`

---

## Chunk 1: Data Model Prerequisites

### Task 1: Verify DB columns and extend ItemDto

**Files:**
- Read: `portal/src/lib/contracts/dto.ts`
- Modify: `portal/src/lib/contracts/dto.ts`

- [ ] **Step 1: Read the current `ItemDto` definition**

Open `portal/src/lib/contracts/dto.ts` and find `ItemDto`. Confirm the current BOM-related fields (likely `active_bom_id?: string`).

- [ ] **Step 2: Check the real database schema for `items` table**

Connect to Supabase (or check migration files under `supabase/migrations/`) and confirm whether `primary_bom_head_id` and `base_bom_head_id` columns exist on the `items` table.

If they do NOT exist, add a migration:
```sql
-- supabase/migrations/<timestamp>_add_product_bom_fields.sql
ALTER TABLE items
  ADD COLUMN IF NOT EXISTS primary_bom_head_id uuid REFERENCES bom_head(id),
  ADD COLUMN IF NOT EXISTS base_bom_head_id    uuid REFERENCES bom_head(id);

COMMENT ON COLUMN items.primary_bom_head_id IS 'PACK BOM head — packaging components';
COMMENT ON COLUMN items.base_bom_head_id    IS 'BASE BOM head — liquid/ingredient components';
```

Apply the migration and confirm columns exist before continuing.

- [ ] **Step 3: Add fields to `ItemDto`**

In `portal/src/lib/contracts/dto.ts`, add to `ItemDto`:

```ts
primary_bom_head_id?: string  // PACK BOM head id
base_bom_head_id?: string     // BASE BOM head id
```

- [ ] **Step 4: Check the items API route**

Find the API route that returns items (likely `/api/items` or similar). Confirm it SELECTs both new columns. If not, add them to the SELECT.

- [ ] **Step 5: Verify TypeScript compiles cleanly**

```bash
cd portal && npx tsc --noEmit
```

Expected: no errors on the new fields.

- [ ] **Step 6: Commit**

```bash
git add portal/src/lib/contracts/dto.ts supabase/migrations/
git commit -m "feat: add primary_bom_head_id and base_bom_head_id to ItemDto and items table"
```

---

### Task 2: Add product-level BOM fetch to repository

**Files:**
- Modify: `portal/src/lib/repositories/boms-repo.ts`

- [ ] **Step 1: Read the current `IdbBomsRepo`**

Open `portal/src/lib/repositories/boms-repo.ts`. Find the exact method name used to fetch a single BOM head by ID — it is `get(id)`, NOT `getById(id)`. Confirm the exact signature before continuing.

- [ ] **Step 2: Add `getProductBoms` method**

Add this method to `IdbBomsRepo` (uses `this.get()`, not `this.getById()`):

```ts
/**
 * Fetch both BASE and PACK BOM heads for a product item.
 * Returns { pack: BomHeadDto | null, base: BomHeadDto | null }.
 * Either may be null if that BOM type is not linked on the item.
 */
async getProductBoms(item: ItemDto): Promise<{
  pack: BomHeadDto | null
  base: BomHeadDto | null
}> {
  const [pack, base] = await Promise.all([
    item.primary_bom_head_id
      ? this.get(item.primary_bom_head_id)
      : Promise.resolve(null),
    item.base_bom_head_id
      ? this.get(item.base_bom_head_id)
      : Promise.resolve(null),
  ])
  return { pack: pack ?? null, base: base ?? null }
}
```

- [ ] **Step 3: TypeScript check**

```bash
cd portal && npx tsc --noEmit
```

Expected: no errors.

- [ ] **Step 4: Commit**

```bash
git add portal/src/lib/repositories/boms-repo.ts
git commit -m "feat: add getProductBoms to IdbBomsRepo"
```

---

## Chunk 2: Production Simulation Page

### Task 3: Create page skeleton and product selector

**Files:**
- Create: `portal/src/app/(planner)/planning/production-simulation/page.tsx`
- Create: `portal/src/app/(planner)/planning/production-simulation/_components/ProductSelector.tsx`

- [ ] **Step 1: Confirm the correct route path**

Check `portal/src/app/(planner)/` — the existing planner pages are at `(planner)/planning/forecast/`, `(planner)/planning/production-recommendations/`, etc. The new page goes at the same level: `portal/src/app/(planner)/planning/production-simulation/page.tsx`. Do NOT use `(planner)/planner/` — that path does not exist.

- [ ] **Step 2: Check `Uom` enum values before writing `formatQty`**

Open `portal/src/lib/contracts/enums.ts`. Find the `Uom` enum (or `UOM_VALUES` constant). Confirm the exact string values used for liquid volume (e.g., `'L'`, `'ML'`), weight, and discrete units. Update the `formatQty` utility in `portal/src/lib/utils/format-quantity.ts` to match those exact values — the comparisons in `formatQty` (`['L', 'ML', 'KG', 'G']`) must match the enum's actual string literals.

- [ ] **Step 3: Create the page file**

Create `portal/src/app/(planner)/planning/production-simulation/page.tsx`:

```tsx
import { Suspense } from 'react'
import { WorkflowHeader } from '@/components/workflow/WorkflowHeader'
import { ProductionSimulatorShell } from './_components/ProductionSimulatorShell'

export const metadata = { title: 'Production simulation' }

export default function ProductionSimulationPage() {
  return (
    <div className="space-y-6">
      <WorkflowHeader
        eyebrow="Planning"
        title="Production simulation"
        description="Select a product to simulate production quantities and check material coverage."
      />
      <Suspense fallback={<div className="p-4 text-muted-foreground">Loading…</div>}>
        <ProductionSimulatorShell />
      </Suspense>
    </div>
  )
}
```

- [ ] **Step 2: Create the shell component**

Create `portal/src/app/(planner)/planning/production-simulation/_components/ProductionSimulatorShell.tsx`:

```tsx
'use client'

import { useState } from 'react'
import { ProductSelector } from './ProductSelector'
import { SimulationResults } from './SimulationResults'
import type { ItemDto } from '@/lib/contracts/dto'

export function ProductionSimulatorShell() {
  const [selectedProduct, setSelectedProduct] = useState<ItemDto | null>(null)

  return (
    <div className="space-y-6">
      <ProductSelector
        selectedProduct={selectedProduct}
        onSelect={setSelectedProduct}
      />
      {selectedProduct && (
        <SimulationResults product={selectedProduct} />
      )}
    </div>
  )
}
```

- [ ] **Step 3: Create the ProductSelector component**

Create `portal/src/app/(planner)/planning/production-simulation/_components/ProductSelector.tsx`:

```tsx
'use client'

import { useQuery } from '@tanstack/react-query'
import { SectionCard } from '@/components/workflow/SectionCard'
import type { ItemDto } from '@/lib/contracts/dto'

interface Props {
  selectedProduct: ItemDto | null
  onSelect: (item: ItemDto) => void
}

export function ProductSelector({ selectedProduct, onSelect }: Props) {
  const { data: items = [], isLoading } = useQuery<ItemDto[]>({
    queryKey: ['items'],
    queryFn: () => fetch('/api/items').then(r => r.json()),
  })

  // Only show MAKE items that have at least one BOM linked
  const products = items.filter(
    item =>
      item.supply_method === 'MAKE' &&
      (item.primary_bom_head_id || item.base_bom_head_id)
  )

  if (isLoading) return <div className="text-muted-foreground text-sm">Loading products…</div>

  return (
    <SectionCard title={selectedProduct ? 'Simulating' : 'Select a product'}>
      {selectedProduct ? (
        <div className="flex items-center justify-between">
          <div>
            <div className="font-medium">{selectedProduct.name}</div>
            <div className="text-sm text-muted-foreground">
              {selectedProduct.primary_bom_head_id ? 'Pack recipe linked' : 'No pack recipe'} ·{' '}
              {selectedProduct.base_bom_head_id ? 'Liquid recipe linked' : 'No liquid recipe'}
            </div>
          </div>
          <button
            className="btn-secondary text-sm"
            onClick={() => onSelect(null!)}
          >
            Change product
          </button>
        </div>
      ) : (
        <div className="space-y-2">
          <label className="text-sm font-medium text-foreground">Product</label>
          <select
            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            defaultValue=""
            onChange={e => {
              const item = products.find(p => p.id === e.target.value)
              if (item) onSelect(item)
            }}
          >
            <option value="" disabled>Select a product…</option>
            {products.map(p => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
          <p className="text-xs text-muted-foreground">
            {products.length} products with active recipes
          </p>
        </div>
      )}
    </SectionCard>
  )
}
```

- [ ] **Step 4: TypeScript check**

```bash
cd portal && npx tsc --noEmit
```

Fix any type errors.

- [ ] **Step 5: Commit**

```bash
git add portal/src/app/(planner)/planning/production-simulation/
git commit -m "feat: add production simulation page skeleton and product selector"
```

---

### Task 4: Quantity input and simulation trigger

**Files:**
- Create: `portal/src/app/(planner)/planning/production-simulation/_components/QuantityInput.tsx`

- [ ] **Step 1: Create QuantityInput component**

Create `portal/src/app/(planner)/planning/production-simulation/_components/QuantityInput.tsx`:

```tsx
'use client'

import { useState } from 'react'
import { SectionCard } from '@/components/workflow/SectionCard'

interface Props {
  onSimulate: (qty: number) => void
  isLoading: boolean
}

export function QuantityInput({ onSimulate, isLoading }: Props) {
  const [qty, setQty] = useState<string>('100')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const n = parseFloat(qty)
    if (!isNaN(n) && n > 0) onSimulate(n)
  }

  return (
    <SectionCard title="Target quantity">
      <form onSubmit={handleSubmit} className="flex items-end gap-3">
        <div className="space-y-1">
          <label className="text-sm font-medium">Units to produce (PCS)</label>
          <input
            type="number"
            min="0.001"
            step="1"
            value={qty}
            onChange={e => setQty(e.target.value)}
            className="w-40 rounded-md border border-input bg-background px-3 py-2 text-sm"
          />
        </div>
        <button
          type="submit"
          disabled={isLoading}
          className="btn-primary"
        >
          {isLoading ? 'Calculating…' : 'Simulate'}
        </button>
      </form>
    </SectionCard>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add portal/src/app/(planner)/planning/production-simulation/_components/QuantityInput.tsx
git commit -m "feat: add quantity input for production simulation"
```

---

### Task 5: Simulation results table (BASE + PACK combined)

**Files:**
- Create: `portal/src/app/(planner)/planning/production-simulation/_components/SimulationResults.tsx`
- Create: `portal/src/app/(planner)/planning/production-simulation/_components/SimulationTable.tsx`
- Create: `portal/src/lib/utils/format-quantity.ts`

- [ ] **Step 1: Create the quantity formatting utility**

Create `portal/src/lib/utils/format-quantity.ts`:

```ts
/**
 * Format a numeric quantity for display, based on UOM type.
 * Hard rule: never more than 4 decimal places in the portal UI.
 */
export function formatQty(value: number, uom: string): string {
  const u = uom.toUpperCase()
  if (['UNIT', 'PCS', 'EA', 'EACH'].includes(u)) {
    return Math.round(value).toLocaleString()
  }
  if (['L', 'ML', 'KG', 'G'].includes(u)) {
    return value.toFixed(3)
  }
  // ratio / conversion factor
  return value.toFixed(4)
}

export function formatPrice(value: number): string {
  return `₪${value.toFixed(2)}`
}

export function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`
}
```

- [ ] **Step 2: Create SimulationTable**

Create `portal/src/app/(planner)/planning/production-simulation/_components/SimulationTable.tsx`:

```tsx
import { formatQty } from '@/lib/utils/format-quantity'

export interface SimulationLine {
  id: string           // unique row key (e.g. "base-<bomLineId>")
  componentId: string  // the actual component_id — used for stock lookup
  componentName: string
  type: 'BASE' | 'PACK'
  qtyPerUnit: number
  requiredQty: number
  uom: string
}

interface Props {
  lines: SimulationLine[]
  targetQty: number
}

export function SimulationTable({ lines, targetQty }: Props) {
  return (
    <div className="overflow-x-auto">
      <table className="table-base w-full text-sm">
        <thead>
          <tr>
            <th className="text-left py-2 px-3">#</th>
            <th className="text-left py-2 px-3">Component</th>
            <th className="text-left py-2 px-3">Type</th>
            <th className="text-right py-2 px-3">Qty per unit</th>
            <th className="text-right py-2 px-3">Required qty</th>
            <th className="text-left py-2 px-3">Unit</th>
          </tr>
        </thead>
        <tbody>
          {lines.map((line, i) => (
            <tr key={line.id} className="border-t border-border">
              <td className="py-2 px-3 text-muted-foreground">{i + 1}</td>
              <td className="py-2 px-3 font-medium">{line.componentName}</td>
              <td className="py-2 px-3">
                <span
                  className={
                    line.type === 'BASE'
                      ? 'badge-blue text-xs'
                      : 'badge-gray text-xs'
                  }
                >
                  {line.type}
                </span>
              </td>
              <td className="py-2 px-3 text-right font-mono">
                {formatQty(line.qtyPerUnit, line.uom)}
              </td>
              <td className="py-2 px-3 text-right font-mono font-semibold">
                {formatQty(line.requiredQty, line.uom)}
              </td>
              <td className="py-2 px-3 text-muted-foreground uppercase text-xs">
                {line.uom}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
```

- [ ] **Step 3: Create SimulationResults**

Create `portal/src/app/(planner)/planning/production-simulation/_components/SimulationResults.tsx`:

```tsx
'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { SectionCard } from '@/components/workflow/SectionCard'
import { QuantityInput } from './QuantityInput'
import { SimulationTable, type SimulationLine } from './SimulationTable'
import { IdbBomsRepo } from '@/lib/repositories/boms-repo'
import type { ItemDto, BomLineDto } from '@/lib/contracts/dto'

interface Props {
  product: ItemDto
}

const bomsRepo = new IdbBomsRepo()

export function SimulationResults({ product }: Props) {
  const [targetQty, setTargetQty] = useState<number | null>(null)

  const { data: productBoms, isLoading: bomsLoading } = useQuery({
    queryKey: ['product-boms', product.id],
    queryFn: () => bomsRepo.getProductBoms(product),
  })

  const hasPackBom = !!productBoms?.pack
  const hasBaseBom = !!productBoms?.base
  const hasNeither = !hasPackBom && !hasBaseBom

  const buildLines = (qty: number): SimulationLine[] => {
    if (!productBoms) return []
    const lines: SimulationLine[] = []

    const packLines: BomLineDto[] =
      productBoms.pack?.versions.find(v => v.id === productBoms.pack?.active_version_id)?.lines ?? []
    const baseLines: BomLineDto[] =
      productBoms.base?.versions.find(v => v.id === productBoms.base?.active_version_id)?.lines ?? []

    for (const line of baseLines) {
      lines.push({
        id: `base-${line.id}`,
        componentId: line.component_id,  // actual component ID for stock lookup
        componentName: line.component_name,
        type: 'BASE',
        qtyPerUnit: Number(line.quantity_per),
        requiredQty: Number(line.quantity_per) * qty,
        uom: line.unit,
      })
    }
    for (const line of packLines) {
      lines.push({
        id: `pack-${line.id}`,
        componentId: line.component_id,  // actual component ID for stock lookup
        componentName: line.component_name,
        type: 'PACK',
        qtyPerUnit: Number(line.quantity_per),
        requiredQty: Number(line.quantity_per) * qty,
        uom: line.unit,
      })
    }
    return lines
  }

  if (bomsLoading) return <div className="text-muted-foreground text-sm p-4">Loading recipes…</div>

  return (
    <div className="space-y-4">
      {/* Notices for missing BOM types */}
      {!hasBaseBom && hasPackBom && (
        <div className="rounded-md border border-amber-200 bg-amber-50 px-4 py-2 text-sm text-amber-800">
          No liquid recipe linked to this product. Showing packaging components only.
        </div>
      )}
      {!hasPackBom && hasBaseBom && (
        <div className="rounded-md border border-amber-200 bg-amber-50 px-4 py-2 text-sm text-amber-800">
          No packaging recipe linked. Showing liquid components only.
        </div>
      )}
      {hasNeither && (
        <div className="rounded-md border border-destructive/30 bg-destructive/5 px-4 py-2 text-sm text-destructive">
          No active recipes found for this product.
        </div>
      )}

      <QuantityInput onSimulate={setTargetQty} isLoading={false} />

      {targetQty !== null && (
        <SectionCard title={`Material requirements — ${product.name}`}>
          <SimulationTable lines={buildLines(targetQty)} targetQty={targetQty} />
        </SectionCard>
      )}
    </div>
  )
}
```

- [ ] **Step 4: Wire QuantityInput into SimulatorShell**

Update `ProductionSimulatorShell.tsx` to pass `SimulationResults` the `product` prop (it already does — verify the import chain is correct).

- [ ] **Step 5: TypeScript check**

```bash
cd portal && npx tsc --noEmit
```

Fix any errors (field names, import paths, missing types).

- [ ] **Step 6: Commit**

```bash
git add portal/src/app/(planner)/planning/production-simulation/ portal/src/lib/utils/format-quantity.ts
git commit -m "feat: production simulation results table with BASE+PACK combined view"
```

---

### Task 6: Add navigation link and verify end-to-end

**Files:**
- Modify: portal navigation/sidebar (find the planner nav component)

- [ ] **Step 1: Find the planner nav**

Search for the sidebar/nav component that lists planner menu items (grep for "production-recommendations" or "forecast" in nav files under `portal/src/components/layout/`).

- [ ] **Step 2: Add "Production simulation" link**

Add entry alongside the other planning pages:

```tsx
{ href: '/planning/production-simulation', label: 'Production simulation' }
```

- [ ] **Step 3: Manual E2E verification**

Start the dev server:
```bash
cd portal && npm run dev
```

Verify:
1. "Production simulation" appears in the planner navigation
2. Selecting a product populates the selector correctly
3. Products without `primary_bom_head_id` or `base_bom_head_id` are excluded
4. Entering a quantity and clicking Simulate shows the table
5. BASE lines show blue TYPE badge; PACK lines show gray TYPE badge
6. Numbers show correct decimal places (L → 3dp, UNIT → 0dp)
7. "Change product" button resets the selector
8. If a product has only PACK BOM, the amber notice appears
9. No internal IDs (BOM-*, PKG-*) appear anywhere on the page

- [ ] **Step 4: Commit**

```bash
git add portal/src/components/layout/
git commit -m "feat: add production simulation to planner navigation"
```

---

## Chunk 3: Stock Coverage Integration

### Task 7: Wire stock coverage panel

**Files:**
- Modify: `portal/src/app/(planner)/planning/production-simulation/_components/SimulationResults.tsx`

- [ ] **Step 1: Search for existing stock coverage panel**

Grep for "coverage" and "stock" in `portal/src/app/(planner)/` and `portal/src/features/`. If a reusable coverage component already exists, import and use it (skip to Step 3).

- [ ] **Step 2: If no coverage panel exists — create one**

Create `portal/src/app/(planner)/planning/production-simulation/_components/StockCoveragePanel.tsx`:

```tsx
'use client'

import { useQuery } from '@tanstack/react-query'
import { SectionCard } from '@/components/workflow/SectionCard'
import { formatQty } from '@/lib/utils/format-quantity'
import type { SimulationLine } from './SimulationTable'

interface Props {
  lines: SimulationLine[]
}

interface StockRow {
  componentId: string
  currentStock: number
  uom: string
}

export function StockCoveragePanel({ lines }: Props) {
  // Fetch current stock for each component in the simulation
  const componentIds = lines.map(l => l.componentId)  // use componentId, not the row id

  const { data: stockRows = [] } = useQuery<StockRow[]>({
    queryKey: ['stock-coverage', componentIds],
    queryFn: async () => {
      // Use the stock projection repo — find the method that returns current
      // projected stock per component. Adapt to whichever repo/method exists.
      // Common pattern: stockRepo.getProjections() then filter by component_id.
      // Read portal/src/lib/repositories/ to find the correct method.
      return []  // replace with actual repo call
    },
    enabled: lines.length > 0,
  })

  const stockByComponentId = new Map(stockRows.map(r => [r.componentId, r]))

  return (
    <SectionCard title="Stock coverage">
      <table className="table-base w-full text-sm">
        <thead>
          <tr>
            <th className="text-left py-2 px-3">Component</th>
            <th className="text-right py-2 px-3">Required</th>
            <th className="text-right py-2 px-3">In stock</th>
            <th className="text-right py-2 px-3">Shortfall</th>
          </tr>
        </thead>
        <tbody>
          {lines.map(line => {
            const stock = stockByComponentId.get(line.componentId)  // use componentId directly
            const inStock = stock?.currentStock ?? 0
            const shortfall = inStock - line.requiredQty
            return (
              <tr key={line.id} className="border-t border-border">
                <td className="py-2 px-3">{line.componentName}</td>
                <td className="py-2 px-3 text-right font-mono">
                  {formatQty(line.requiredQty, line.uom)}
                </td>
                <td className="py-2 px-3 text-right font-mono">
                  {formatQty(inStock, line.uom)}
                </td>
                <td className={`py-2 px-3 text-right font-mono font-semibold ${shortfall < 0 ? 'text-destructive' : 'text-green-600'}`}>
                  {shortfall >= 0 ? '+' : ''}{formatQty(shortfall, line.uom)}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </SectionCard>
  )
}
```

The `queryFn` body must be completed by reading the stock projection repository to find the correct method. Do not leave it returning `[]` in production.

- [ ] **Step 2b: Wire the stock repo call**

Open `portal/src/lib/repositories/` and find the stock projection repository (grep for "projection" or "stock"). Use its list/get method to fetch current projected stock per component, then filter to the component IDs in `lines`.

- [ ] **Step 3: Position the coverage panel**

Render the coverage panel below the `SimulationTable` inside the `SectionCard`, or as its own `SectionCard` below — matching the existing visual pattern from the old BOM simulation.

- [ ] **Step 4: E2E verify coverage panel**

Start dev server and confirm:
1. Coverage panel shows after Simulate is clicked
2. Data reflects current stock vs required qty per component
3. Shortfalls are highlighted correctly

- [ ] **Step 5: Commit**

```bash
git add portal/src/app/(planner)/planning/production-simulation/
git commit -m "feat: integrate stock coverage panel into production simulation"
```

---

## Success Criteria

Before marking this plan complete, confirm ALL of the following:

- [ ] Product selector lists only `MAKE` items with at least one active BOM linked
- [ ] Simulation combines BASE and PACK lines in a single table, each tagged BASE/PACK
- [ ] Formula shown: `required = target × qty_per_unit` (no `base_output_qty` complexity)
- [ ] Numbers: liquids show 3dp, discrete units show 0dp, ratios show 4dp
- [ ] No internal codes (BOM-*, PKG-*, version codes) appear anywhere on the page
- [ ] Amber notice shown when only one BOM type is linked
- [ ] Stock coverage panel appears below results
- [ ] "Change product" resets the selector
- [ ] TypeScript compiles with zero errors
- [ ] Navigation link appears in planner sidebar
