# Admin Master Data UX Overhaul Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix four systemic UX problems across all admin master data pages: confusing technical labels, invisible edit affordances, broken cross-entity navigation, and excessive decimal precision — plus add breadcrumbs and back navigation throughout.

**Architecture:** Shared utilities first (formatting, breadcrumbs), then page-by-page fixes. All changes are additive to existing pages; no page is rebuilt from scratch. The `SplitListLayout` pattern is preserved; improvements are applied within it.

**Tech Stack:** Next.js 15 App Router, TypeScript, TanStack Query, Tailwind, shadcn/ui, react-hook-form + Zod.

**CRITICAL ARCHITECTURE NOTE:** This portal uses **IndexedDB (IDB) directly** — there are NO Next.js API routes (`/api/*`). Every data operation uses IDB repository instances (`IdbBomsRepo`, `IdbSuppliersRepo`, `IdbComponentsRepo`, `IdbSupplierItemsRepo`, etc.) called directly in client components via TanStack Query. Never write `fetch('/api/...')` — always use the appropriate repo instance.

**Spec:** `docs/superpowers/specs/2026-04-26-master-data-ux-overhaul-design.md` — Streams 2, 3, 4, 5

**Runs in parallel with:** `2026-04-26-production-simulation.md`

---

## Chunk 1: Foundation Utilities

### Task 1: Quantity formatting utility

**Files:**
- Create: `portal/src/lib/utils/format-quantity.ts`

> Note: If `2026-04-26-production-simulation.md` has already created this file, skip creation and just verify the utility matches the spec below.

- [ ] **Step 1: Create the utility**

Create `portal/src/lib/utils/format-quantity.ts`:

```ts
/**
 * Format a numeric quantity for display, based on UOM.
 * Hard rule: never more than 4 decimal places anywhere in the portal UI.
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

- [ ] **Step 2: Find every numeric display in admin pages**

Search for `.toFixed(`, `toLocaleString(`, and raw numeric renders in:
- `portal/src/app/(admin)/admin/boms/page.tsx`
- `portal/src/app/(admin)/admin/components/page.tsx`
- `portal/src/app/(admin)/admin/supplier-items/page.tsx`
- `portal/src/app/(admin)/admin/planning-policy/page.tsx`

List all occurrences.

- [ ] **Step 3: Replace with `formatQty` / `formatPrice`**

For each occurrence, replace with the appropriate `formatQty(value, uom)` or `formatPrice(value)` call. Where UOM is unknown, default to `formatQty(value, 'UNIT')`.

- [ ] **Step 4: TypeScript check**

```bash
cd portal && npx tsc --noEmit
```

- [ ] **Step 5: Commit**

```bash
git add portal/src/lib/utils/format-quantity.ts portal/src/app/(admin)/
git commit -m "feat: add formatQty utility and apply to all admin numeric displays"
```

---

### Task 2: Breadcrumbs component

**Files:**
- Create: `portal/src/components/layout/Breadcrumbs.tsx`

- [ ] **Step 1: Create the component**

Create `portal/src/components/layout/Breadcrumbs.tsx`:

```tsx
import Link from 'next/link'

export interface BreadcrumbItem {
  label: string
  href?: string  // if omitted, renders as plain text (current page)
}

interface Props {
  items: BreadcrumbItem[]
}

export function Breadcrumbs({ items }: Props) {
  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-1 text-xs text-muted-foreground mb-1">
      {items.map((item, i) => (
        <span key={i} className="flex items-center gap-1">
          {i > 0 && <span className="text-muted-foreground/50">›</span>}
          {item.href ? (
            <Link href={item.href} className="hover:text-foreground transition-colors">
              {item.label}
            </Link>
          ) : (
            <span className="text-foreground font-medium">{item.label}</span>
          )}
        </span>
      ))}
    </nav>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add portal/src/components/layout/Breadcrumbs.tsx
git commit -m "feat: add Breadcrumbs layout component"
```

---

## Chunk 2: Stream 2 — Naming & Labels (BOM pages)

### Task 3: Fix BOM version page title and internal ID exposure

**Files:**
- Modify: `portal/src/app/(admin)/admin/boms/page.tsx`

- [ ] **Step 1: Read the BOM admin page**

Open `portal/src/app/(admin)/admin/boms/page.tsx` completely. Find:
1. Where the BOM version page title is rendered (the heading that shows "BOM vV4_PACK_RULE")
2. Where `BOM-PACK-AME-500ML` or similar BOM head IDs are shown
3. Where `FG-AME-500ML` item IDs are shown
4. Where `PKG-*` component IDs are shown under component names
5. The "LINKED: BOM head" and "LINKED: Linked item" panel labels
6. The `MANUFACTURED` badge on BOM version pages

- [ ] **Step 2: Fix the BOM version page title**

Find the heading that renders the version identifier (e.g., `BOM v{version.version_number}` or the version name). Change to:

```tsx
// Before (approximately):
<h1>{`BOM v${version.version_number}`}</h1>

// After:
<h1>
  {bomHead.item_name} — {bomHead.bom_type === 'pack' ? 'Pack recipe' : 'Liquid recipe'}
</h1>
```

**`bom_type` does not exist on `BomHeadDto` yet.** Add it to the DTO as an optional field:
```ts
// In portal/src/lib/contracts/dto.ts — BomHeadDto:
bom_type?: 'pack' | 'base'
```
IDB is schemaless so no migration is needed — just the DTO. The value is set when seeding/importing BOM data. For now, if `bom_type` is not yet set on existing records, fall back to: if `item_name` includes "PACK" → 'pack', if includes "BASE" → 'base', else show just `{bomHead.item_name} — Recipe`.

- [ ] **Step 3: Add version name field**

Find where BOM versions are created or displayed. Add an optional `display_name` field input:

```tsx
<Field label="Version name (optional)">
  <input
    type="text"
    placeholder="e.g. Initial release, Post supplier change Q2"
    {...register('display_name')}
    className="input-base"
  />
</Field>
```

Display: if `display_name` is set, show it; otherwise show `Version {version_number}`.

**Add `display_name` to the DTO only — no SQL migration, IDB is schemaless:**
```ts
// In portal/src/lib/contracts/dto.ts — BomVersionDto:
display_name?: string
```

- [ ] **Step 4: Remove internal IDs from display**

In the BOM lines table, remove the sub-text that shows component IDs like `PKG-BOTTLE-500ML` beneath component names. Only the component name should be visible.

In the right panel "LINKED" section, change labels:
- `LINKED: BOM head` → remove the "LINKED:" prefix, replace with section title `Pack recipe` or `Liquid recipe`
- `LINKED: Linked item` → section title `Finished product`

Remove `BOM-PACK-AME-500ML` from being shown as the BOM head display value; show only the human-readable name (`{item_name} · PACK` → just `{item_name}`).

- [ ] **Step 5: Remove `MANUFACTURED` badge from BOM version page**

Find where the `MANUFACTURED` supply method badge is rendered on the BOM detail/version view. Remove it — this badge belongs on the item page, not the BOM page.

- [ ] **Step 6: Remove `VV4_PACK_RULE` from simulation tab**

Find where version names (like `VV4_PACK_RULE`) are rendered as tab labels or badges in the simulation area. Replace with `Version {n}` or the `display_name` if set.

- [ ] **Step 7: TypeScript check + manual verify**

```bash
cd portal && npx tsc --noEmit && npm run dev
```

Navigate to Admin › BOMs › any product › active version. Confirm:
- Page title shows product name + recipe type (not "BOM vV4_PACK_RULE")
- No `BOM-*`, `FG-*`, `PKG-*` IDs visible in body text
- Panel section labels are human-readable
- `MANUFACTURED` badge is gone from BOM version page

- [ ] **Step 8: Commit**

```bash
git add portal/src/app/(admin)/admin/boms/
git commit -m "fix: remove internal IDs from BOM pages, human-readable titles and labels"
```

---

## Chunk 3: Stream 3 — Edit Discoverability

### Task 4: Universal Edit button pattern

**Files:**
- Modify: `portal/src/features/master-data/SplitListLayout.tsx`
- Modify: `portal/src/app/(admin)/admin/items/page.tsx`
- Modify: `portal/src/app/(admin)/admin/components/page.tsx`
- Modify: `portal/src/app/(admin)/admin/suppliers/page.tsx`
- Modify: `portal/src/app/(admin)/admin/supplier-items/page.tsx`

- [ ] **Step 1: Understand the current edit pattern**

Read `portal/src/features/master-data/SplitListLayout.tsx`. Understand how the detail panel currently works — is there already an edit mode toggle? If so, understand the existing pattern before changing it.

Read one admin page (e.g., `admin/components/page.tsx`) to see how edit state is managed.

- [ ] **Step 2: Add Edit button to every detail panel header**

For each admin page that uses a detail panel (items, components, suppliers, BOMs, supplier-items):

If there is NO explicit edit button, add one to the panel header. Pattern:

```tsx
// In the detail panel header area:
{!isEditing && (
  <button
    onClick={() => setIsEditing(true)}
    className="btn-secondary text-sm"
  >
    Edit
  </button>
)}
{isEditing && (
  <button
    onClick={() => { setIsEditing(false); reset() }}
    className="btn-ghost text-sm"
  >
    Cancel
  </button>
)}
```

`isEditing` state is local to each page component. When `isEditing` is false, form fields render as read-only (`<span>` or `disabled` inputs). When `isEditing` is true, fields become interactive inputs.

If pages already have an edit pattern, make the `Edit` button visible (not hidden behind a hover state or only accessible by clicking a row).

- [ ] **Step 3: Verify on each admin page**

For each page, manually confirm:
1. Opening a detail panel shows a visible `Edit` button
2. Clicking `Edit` makes fields editable
3. `Save` / `Cancel` appear clearly
4. Cancelling restores original values (call `reset()` from react-hook-form)

- [ ] **Step 4: Commit**

```bash
git add portal/src/app/(admin)/ portal/src/features/master-data/
git commit -m "feat: add visible Edit button to all admin detail panels"
```

---

### Task 5: Supplier assignment for components

**Files:**
- Modify: `portal/src/app/(admin)/admin/components/page.tsx`

- [ ] **Step 1: Read the current component detail panel**

Open `portal/src/app/(admin)/admin/components/page.tsx`. Find where the component detail panel renders. Check what's currently shown for supplier information.

- [ ] **Step 2: Add "Primary supplier" section**

In the component detail panel (read-only mode), add a section below the main fields:

```tsx
<div className="border-t border-border pt-4 mt-4">
  <div className="flex items-center justify-between mb-2">
    <span className="text-sm font-medium">Primary supplier</span>
    {!isEditing && (
      <button
        onClick={() => setShowSupplierPicker(true)}
        className="btn-ghost text-xs"
      >
        {primarySupplier ? 'Change' : 'Assign supplier'}
      </button>
    )}
  </div>
  {primarySupplier ? (
    <span className="text-sm">{primarySupplier.supplier_name}</span>
  ) : (
    <span className="text-sm text-muted-foreground">No supplier assigned</span>
  )}
</div>
```

- [ ] **Step 3: Add supplier picker**

When "Change" or "Assign supplier" is clicked, show a searchable supplier dropdown:

```tsx
{showSupplierPicker && (
  <div className="mt-2 space-y-2">
    <label className="text-xs text-muted-foreground">Select supplier</label>
    <select
      className="w-full rounded border border-input bg-background px-2 py-1.5 text-sm"
      defaultValue={primarySupplier?.supplier_id ?? ''}
      onChange={e => setPendingSupplier(e.target.value)}
    >
      <option value="" disabled>Choose a supplier…</option>
      {suppliers.map(s => (
        <option key={s.id} value={s.id}>{s.name}</option>
      ))}
    </select>
    <div className="flex gap-2">
      <button onClick={handleSaveSupplier} className="btn-primary text-xs">Save</button>
      <button onClick={() => setShowSupplierPicker(false)} className="btn-ghost text-xs">Cancel</button>
    </div>
  </div>
)}
```

- [ ] **Step 4: Implement `handleSaveSupplier`**

**Important:** This portal uses IDB repos directly — no fetch/API calls. Use the supplier-items repo.
First read `portal/src/lib/repositories/supplier-items-repo.ts` to find the exact method names.
`preferred` is the correct field name (not `is_primary`). Soft-delete uses `setActive(id, false)` (not `archived_at`).

```ts
async function handleSaveSupplier() {
  if (!pendingSupplier || !selectedComponent) return

  // Soft-delete the existing primary supplier_items row (if any)
  if (primarySupplierItem) {
    await supplierItemsRepo.setActive(primarySupplierItem.id, false)
  }

  // Insert new supplier_items row — use the repo's create method
  // Read the repo to find the exact create signature and required fields
  await supplierItemsRepo.create({
    supplier_id: pendingSupplier,
    component_id: selectedComponent.id,
    preferred: true,
    // include any other required fields shown in SupplierItemDto
  })

  await queryClient.invalidateQueries({ queryKey: ['supplier-items'] })
  setShowSupplierPicker(false)
}
```

- [ ] **Step 5: Load `primarySupplier` for selected component**

Use the repo directly — no fetch:

```ts
const { data: primarySupplierItem } = useQuery({
  queryKey: ['supplier-items', 'primary', selectedComponent?.id],
  queryFn: async () => {
    if (!selectedComponent) return null
    const all = await supplierItemsRepo.list()
    return all.find(
      s => s.component_id === selectedComponent.id && s.preferred === true && s.active !== false
    ) ?? null
  },
  enabled: !!selectedComponent,
})
```

- [ ] **Step 6: TypeScript check + manual verify**

```bash
cd portal && npx tsc --noEmit && npm run dev
```

Navigate to Admin › Components › any component. Confirm:
1. "Primary supplier" section visible in panel
2. "Assign supplier" / "Change" button present
3. Clicking "Change" opens supplier picker
4. Saving a supplier shows the new supplier name immediately
5. Old `supplier_items` row is soft-deleted (verify `active = false` on old row in IDB)
6. New row created with correct `supplier_id` + `component_id`

- [ ] **Step 7: Commit**

```bash
git add portal/src/app/(admin)/admin/components/
git commit -m "feat: add primary supplier section with change/assign flow to component detail panel"
```

---

## Chunk 4: Stream 4 — Cross-Entity Navigation

### Task 6: "Used in" section on component detail

**Files:**
- Modify: `portal/src/app/(admin)/admin/components/page.tsx`

- [ ] **Step 1: Add `usedInProducts` query**

**No API routes exist — use the boms repo directly.** Read `portal/src/lib/repositories/boms-repo.ts` to find the list/getAll method. Then filter in-memory:

```ts
interface UsedInRow {
  productName: string
  itemId: string
  qtyPerUnit: number
  uom: string
  bomType: 'BASE' | 'PACK' | 'UNKNOWN'
}

const { data: usedInProducts = [] } = useQuery<UsedInRow[]>({
  queryKey: ['used-in', selectedComponent?.id],
  queryFn: async () => {
    if (!selectedComponent) return []
    // Fetch all BOM heads from IDB
    const allBomHeads = await bomsRepo.list()  // use the correct method name from the repo
    const results: UsedInRow[] = []
    for (const head of allBomHeads) {
      // Find the active version
      const activeVersion = head.versions.find(v => v.id === head.active_version_id)
      if (!activeVersion) continue
      // Check if any line references this component
      for (const line of activeVersion.lines) {
        if (line.component_id === selectedComponent.id) {
          results.push({
            productName: head.item_name,
            itemId: head.item_id,
            qtyPerUnit: Number(line.quantity_per),
            uom: line.unit,
            // Derive bomType from bom_type field if available, else UNKNOWN
            bomType: (head as any).bom_type === 'pack' ? 'PACK'
                   : (head as any).bom_type === 'base' ? 'BASE'
                   : 'UNKNOWN',
          })
        }
      }
    }
    return results
  },
  enabled: !!selectedComponent,
})

- [ ] **Step 2: Render "Used in" section**

Add below the "Primary supplier" section:

```tsx
<div className="border-t border-border pt-4 mt-4">
  <div className="text-sm font-medium mb-2">
    Used in {usedInProducts.length} {usedInProducts.length === 1 ? 'product' : 'products'}
  </div>
  {usedInProducts.length === 0 ? (
    <p className="text-sm text-muted-foreground">Not used in any active recipe.</p>
  ) : (
    <ul className="space-y-1">
      {usedInProducts.map(row => (
        <li key={`${row.itemId}-${row.bomType}`} className="flex items-center justify-between text-sm">
          <button
            className="text-primary hover:underline text-left"
            onClick={() => router.push(`/admin/boms?item=${row.itemId}`)}
          >
            {row.productName}
          </button>
          <span className="text-muted-foreground text-xs ml-2">
            {formatQty(row.qtyPerUnit, row.uom)} {row.uom}
            {' · '}
            <span className={row.bomType === 'BASE' ? 'text-blue-600' : 'text-gray-500'}>
              {row.bomType}
            </span>
          </span>
        </li>
      ))}
    </ul>
  )}
</div>
```

**When a component appears in both BASE and PACK BOMs of the same product:** show two rows, each labelled BASE or PACK with its own qty. Do not collapse.

- [ ] **Step 3: Commit**

```bash
git add portal/src/app/(admin)/admin/components/
git commit -m "feat: add 'Used in X products' section to component detail panel"
```

---

### Task 7: Clickable component names in BOM lines

**Files:**
- Modify: `portal/src/app/(admin)/admin/boms/page.tsx`

- [ ] **Step 1: Find the BOM lines table**

In `portal/src/app/(admin)/admin/boms/page.tsx`, find where BOM lines are rendered in a table (the component name column).

- [ ] **Step 2: Make component names clickable**

Change the component name cell from plain text to a link:

```tsx
// Before:
<td>{line.component_name}</td>

// After:
<td>
  <Link
    href={`/admin/components?component=${line.component_id}`}
    className="text-primary hover:underline"
  >
    {line.component_name}
  </Link>
</td>
```

Verify that `/admin/components?component=X` will open the components page with that component pre-selected. If not (the page doesn't read URL params to pre-select), add that behavior to the components page:

```ts
// In components page — on mount:
const searchParams = useSearchParams()
const preSelectId = searchParams.get('component')
// If preSelectId is set, find matching component in list and setSelectedComponent
```

- [ ] **Step 3: Commit**

```bash
git add portal/src/app/(admin)/admin/boms/
git commit -m "feat: component names in BOM lines are now clickable links to component detail"
```

---

### Task 8: Supplier link from component, and "Components supplied" on supplier page

**Files:**
- Modify: `portal/src/app/(admin)/admin/components/page.tsx`
- Modify: `portal/src/app/(admin)/admin/suppliers/page.tsx`
- Modify: `portal/src/app/(admin)/admin/supplier-items/page.tsx`

- [ ] **Step 1: Make supplier name a link in component panel**

In the "Primary supplier" section of the component detail (added in Task 5), wrap the supplier name in a link:

```tsx
// Before:
<span className="text-sm">{primarySupplier.supplier_name}</span>

// After:
<Link
  href={`/admin/suppliers?supplier=${primarySupplierItem.supplier_id}`}
  className="text-sm text-primary hover:underline"
>
  {primarySupplier.supplier_name}
</Link>
```

- [ ] **Step 2: Add "Components supplied" section to supplier detail**

In `portal/src/app/(admin)/admin/suppliers/page.tsx`, find the supplier detail panel. Add a section below existing fields. **Use the repo directly — no fetch:**

```tsx
const { data: suppliedComponents = [] } = useQuery({
  queryKey: ['supplier-components', selectedSupplier?.id],
  queryFn: async () => {
    if (!selectedSupplier) return []
    const all = await supplierItemsRepo.list()
    return all.filter(
      si => si.supplier_id === selectedSupplier.id && si.preferred === true && si.active !== false
    )
  },
  enabled: !!selectedSupplier,
})

// In render:
<div className="border-t border-border pt-4 mt-4">
  <div className="text-sm font-medium mb-2">
    Components supplied ({suppliedComponents.length})
  </div>
  {suppliedComponents.length === 0 ? (
    <p className="text-sm text-muted-foreground">No components linked to this supplier.</p>
  ) : (
    <ul className="space-y-1">
      {suppliedComponents.map(sc => (
        <li key={sc.component_id}>
          <Link
            href={`/admin/components?component=${sc.component_id}`}
            className="text-sm text-primary hover:underline"
          >
            {sc.component_name}
          </Link>
        </li>
      ))}
    </ul>
  )}
</div>
```

- [ ] **Step 3: Bidirectional links in supplier-items page**

In `portal/src/app/(admin)/admin/supplier-items/page.tsx`, find the supplier name and component name columns/fields. Make each a link:

```tsx
// Supplier name → supplier detail
<Link href={`/admin/suppliers?supplier=${row.supplier_id}`} className="text-primary hover:underline">
  {row.supplier_name}
</Link>

// Component name → component detail
<Link href={`/admin/components?component=${row.component_id}`} className="text-primary hover:underline">
  {row.component_name}
</Link>
```

- [ ] **Step 4: Verify URL param pre-selection works**

For each target page (`/admin/suppliers?supplier=X`, `/admin/components?component=X`), confirm the page reads the URL param and opens that entity's detail panel on mount. Add this behavior if missing.

- [ ] **Step 5: TypeScript check + manual verify**

```bash
cd portal && npx tsc --noEmit && npm run dev
```

Verify the full navigation chain:
1. Admin › Components › [component] → click supplier name → lands on supplier page with that supplier selected
2. Admin › Suppliers › [supplier] → "Components supplied" → click component → lands on components page with that component selected
3. Admin › BOMs › [product] → click component name in lines table → lands on components page with that component selected
4. Admin › Supplier-items → click supplier or component name → navigates correctly

- [ ] **Step 6: Commit**

```bash
git add portal/src/app/(admin)/admin/
git commit -m "feat: cross-entity navigation — supplier links, 'components supplied', bidirectional supplier-items links"
```

---

## Chunk 5: Stream 5 — Breadcrumbs + Navigation

### Task 9: Add breadcrumbs to BOM admin pages

**Files:**
- Modify: `portal/src/app/(admin)/admin/boms/page.tsx`

- [ ] **Step 1: Import Breadcrumbs**

In `portal/src/app/(admin)/admin/boms/page.tsx`:

```tsx
import { Breadcrumbs } from '@/components/layout/Breadcrumbs'
```

- [ ] **Step 2: Add breadcrumbs inside the BOM version detail area**

When a BOM version is selected/shown, render the breadcrumbs inside the detail panel header, above the page title:

```tsx
<Breadcrumbs
  items={[
    { label: 'Admin', href: '/admin' },
    { label: 'BOMs', href: '/admin/boms' },
    { label: selectedBomHead?.item_name ?? 'Product', href: `/admin/boms?item=${selectedBomHead?.item_id}` },
    { label: selectedVersion?.display_name ?? `Version ${selectedVersion?.version_number}` },
  ]}
/>
```

- [ ] **Step 3: Add breadcrumbs to other admin detail panels**

Repeat for: `admin/components`, `admin/suppliers`, `admin/supplier-items`, `admin/items`. Each panel header gets:

```tsx
// Components:
<Breadcrumbs items={[
  { label: 'Admin', href: '/admin' },
  { label: 'Components', href: '/admin/components' },
  { label: selectedComponent?.name ?? 'Component' },
]} />

// Suppliers:
<Breadcrumbs items={[
  { label: 'Admin', href: '/admin' },
  { label: 'Suppliers', href: '/admin/suppliers' },
  { label: selectedSupplier?.name ?? 'Supplier' },
]} />
```

- [ ] **Step 4: Commit**

```bash
git add portal/src/app/(admin)/admin/ portal/src/components/layout/Breadcrumbs.tsx
git commit -m "feat: add breadcrumbs to all admin detail panels"
```

---

### Task 10: Back buttons and ESC handler

**Files:**
- Modify: `portal/src/features/master-data/SplitListLayout.tsx`
- Modify: `portal/src/app/(admin)/admin/boms/page.tsx` (and others as needed)

- [ ] **Step 1: Add `← Back` button to BOM version detail**

In the BOM admin page, where the version detail view is shown (if it's a separate view or deeply nested panel), add:

```tsx
<button
  onClick={() => setSelectedVersion(null)}
  className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground mb-3"
>
  ← Back
</button>
```

This returns the user to the BOM list or the BOM head view.

- [ ] **Step 2: Add ESC key handler to close detail panels**

In `SplitListLayout.tsx` (or in each admin page that manages a `selectedItem` state), add:

```tsx
useEffect(() => {
  const handler = (e: KeyboardEvent) => {
    if (e.key === 'Escape') setSelectedItem(null)
  }
  document.addEventListener('keydown', handler)
  return () => document.removeEventListener('keydown', handler)
}, [])
```

Alternatively, add this to `SplitListLayout` as a prop: `closeOnEsc?: boolean` defaulting to `true`.

- [ ] **Step 3: Verify browser back does not break state**

Navigate to an admin page, open a detail panel, then use browser back. The page should return to the list view (empty panel) — not break or show a 404.

If the panel state is not reflected in the URL (so browser back navigates away from the page entirely), that's acceptable — the ESC key and Back button cover the in-page case.

- [ ] **Step 4: TypeScript check + full manual pass**

```bash
cd portal && npx tsc --noEmit && npm run dev
```

Final manual verification across all admin pages:
1. Every detail panel shows breadcrumbs in the header
2. ESC closes the detail panel
3. "← Back" button visible on BOM version detail pages
4. All numbers obey the precision rules (no 6-8 decimal places anywhere)
5. No internal IDs visible in any admin page body text

- [ ] **Step 5: Final commit**

```bash
git add portal/src/app/(admin)/ portal/src/features/master-data/SplitListLayout.tsx portal/src/components/layout/
git commit -m "feat: back buttons, ESC to close panels, breadcrumbs complete across all admin pages"
```

---

## Success Criteria

Before marking this plan complete, confirm ALL of the following:

- [ ] `formatQty` / `formatPrice` used everywhere numeric values display — no raw `.toFixed(6)` or 8dp numbers
- [ ] BOM version page title shows `{Product name} — Pack/Liquid recipe` (not "BOM vVERSION")
- [ ] No `BOM-*`, `PKG-*`, `FG-*` codes visible in any admin page body or heading
- [ ] "LINKED:" prefix removed from BOM panel labels; replaced with plain English
- [ ] Every admin detail panel has a visible `Edit` button (not hover-only)
- [ ] "Primary supplier" section visible on component detail with `Change`/`Assign` button
- [ ] Saving a supplier change soft-deletes old row + creates new (verify in DB)
- [ ] "Used in X products" section populated and clickable on every component
- [ ] Component appears twice if used in both BASE and PACK BOM of same product
- [ ] BOM line component names are clickable → navigate to component detail
- [ ] Supplier name in component panel → navigates to supplier page
- [ ] Supplier page shows "Components supplied" list with clickable links
- [ ] Supplier-items page: supplier name and component name both link correctly
- [ ] Breadcrumbs visible in all admin detail panels
- [ ] ESC closes detail panels
- [ ] TypeScript compiles with zero errors
