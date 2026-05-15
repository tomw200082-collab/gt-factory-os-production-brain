# RM Planning Parameters — Implementation Plan

**Spec:** `docs/superpowers/specs/2026-05-14-rm-planning-params-design.md`
**Date:** 2026-05-14
**Portal repo:** `c:/Users/tomw2/Projects/window2-portal-sandbox/`
**Branch:** to be created from main portal branch

---

## Context

Two UI-only changes in the portal. No backend changes required — the PATCH API already accepts `safety_days` for supplier_items.

---

## Task 1: Add `safety_days` inline-edit column to `/admin/supplier-items`

**File:** `src/app/(admin)/admin/supplier-items/page.tsx`

### What to add

1. **Extend `fieldMutation` union type** (line ~267): add `"safety_days"` to the `field` union:
   ```ts
   field: "lead_time_days" | "moq" | "pack_conversion" | "std_cost_per_inv_uom" | "order_uom" | "safety_days";
   ```

2. **Add column header** in `<thead>` (after "Min. order qty", before "Std cost"):
   ```jsx
   <Th align="right">Safety days</Th>
   ```

3. **Add cell JSX** in the row body (same position, after moq cell):
   ```jsx
   <td className="px-3 py-2 text-right tabular-nums text-sm">
     {isAdmin ? (
       <InlineEditCell
         value={r.safety_days ?? 0}
         type="number"
         inputMode="numeric"
         ifMatchUpdatedAt={r.updated_at}
         onSave={async (newValue) => {
           await fieldMutation.mutateAsync({
             supplier_item_id: r.supplier_item_id,
             field: "safety_days",
             value: newValue,
             updated_at: r.updated_at,
           });
         }}
         ariaLabel={`Edit safety days for ${r.component_id ?? r.item_id ?? r.supplier_item_id}`}
       />
     ) : (
       <SafetyDaysChip days={r.safety_days} />
     )}
   </td>
   ```

4. **Add `SafetyDaysChip` component** (inline, near bottom of file alongside `LeadTimeChip`):
   ```tsx
   function SafetyDaysChip({ days }: { days: number }) {
     if (days === 0) return <span className="text-muted-foreground text-xs">0d</span>;
     if (days <= 6) return <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800">{days}d</span>;
     return <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-800">{days}d</span>;
   }
   ```

5. **Check portal proxy route** `src/app/api/supplier-items/[supplier_item_id]/route.ts` — verify it passes `safety_days` through to the backend PATCH. If it has an allowlist, add `safety_days`.

### Acceptance
- Safety days column visible in table
- 0 shows gray, 1-6 amber, ≥7 green
- Admin can inline-edit and save
- Non-admin sees chip (read-only)

---

## Task 2: Add "Planning Parameters" card to component detail page

**File:** `src/app/(admin)/admin/masters/components/[component_id]/page.tsx`

### What to add

1. **Extend local `SupplierItemRow` interface** (line ~72): add `safety_days: number` if not already present.

2. **Check if `ComponentRow`** (the shape of `componentQuery.data?.rows[0]`) includes `lead_time_days`. If yes, use it. If the field is not in the type, add it (it exists in the DB and the API returns it).

3. **Compute planning params** (derive from existing `primarySi` and `row`):
   ```ts
   const primarySupplierItem = primarySi[0] ?? null;

   const effectiveLeadTime =
     primarySupplierItem?.lead_time_days ??
     (row as { lead_time_days?: number | null })?.lead_time_days ??
     14; // global policy fallback

   const leadTimeSource =
     primarySupplierItem?.lead_time_days != null
       ? "Primary supplier"
       : (row as { lead_time_days?: number | null })?.lead_time_days != null
       ? "Supplier default"
       : "Global policy (14d)";

   const effectiveMoq = primarySupplierItem?.moq ?? null;
   const moqSource = effectiveMoq != null ? "Primary supplier" : null;

   const effectiveSafetyDays = primarySupplierItem?.safety_days ?? 0;
   const safetyDaysSource =
     (primarySupplierItem?.safety_days ?? 0) > 0 ? "Primary supplier" : "Default (0d)";

   const effectiveReorderLead = effectiveLeadTime + effectiveSafetyDays;
   ```

4. **Add `planningParamsCard`** in the `overviewTab` content (after "Units & procurement" SectionCard, before "Technical details"):
   ```tsx
   <SectionCard title="Planning parameters">
     <table className="w-full text-sm">
       <tbody className="divide-y divide-border/50">
         <tr>
           <td className="py-2 pr-4 text-muted-foreground w-1/2">Lead time</td>
           <td className="py-2 font-medium">{effectiveLeadTime}d</td>
           <td className="py-2 pl-4 text-xs text-muted-foreground">{leadTimeSource}</td>
         </tr>
         <tr>
           <td className="py-2 pr-4 text-muted-foreground">MOQ</td>
           <td className="py-2 font-medium">
             {effectiveMoq != null
               ? formatQty(Number(effectiveMoq), row?.purchase_uom ?? "UNIT")
               : "—"}
           </td>
           <td className="py-2 pl-4 text-xs text-muted-foreground">{moqSource ?? "—"}</td>
         </tr>
         <tr>
           <td className="py-2 pr-4 text-muted-foreground">Safety days</td>
           <td className="py-2 font-medium">{effectiveSafetyDays}d</td>
           <td className="py-2 pl-4 text-xs text-muted-foreground">{safetyDaysSource}</td>
         </tr>
         <tr className="font-semibold">
           <td className="py-2 pr-4 text-muted-foreground">Effective reorder lead</td>
           <td className="py-2">{effectiveReorderLead}d</td>
           <td className="py-2 pl-4 text-xs text-muted-foreground">lead + safety</td>
         </tr>
       </tbody>
     </table>
     <p className="mt-3 text-xs text-muted-foreground">
       Edit in{" "}
       <button
         className="underline"
         onClick={() => setActiveTab("supplier-items")}
       >
         Supplier items →
       </button>
     </p>
   </SectionCard>
   ```
   Replace `setActiveTab("supplier-items")` with whatever the actual tab-switch mechanism is (check how the existing page switches tabs — likely a URL param or state setter).

### Acceptance
- Planning Parameters card visible in overview tab
- Shows correct values from primary supplier_item
- Source labels are accurate
- "Supplier items →" link switches to supplier-items tab
- When no primary supplier_item: shows fallback values with source "Global policy"

---

## Notes for implementer

- Portal branch: create from portal's current branch (not PRODUCTION branch)
- No backend changes required
- Check portal proxy route for safety_days passthrough (Task 1, step 5)
- The `primarySi` variable already exists in component detail page (line ~334)
- `formatQty` is already imported in the component detail page
- Use existing `SectionCard` pattern from the same file
- TypeScript strict — cast carefully if `lead_time_days` is not in the type
