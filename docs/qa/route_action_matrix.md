# Route / Action Matrix — 2026-05-02 (cycle 10)

> Authored by `executor-w2` under Mode A (audit-only) on behalf of Tom's Phase 1
> request. Extends `runtime_dead_end_audit.md` (cycle 9) and
> `overnight_audit_2026-05-01.md` (cycle 1) — does not duplicate them.
>
> Authority: `CLAUDE.md` durable contract, `CURRENT_STATE.md` runtime status,
> `EXECUTION_POLICY.md` governance.
>
> Scope: every `page.tsx` under `c:/Users/tomw2/Projects/window2-portal-sandbox/src/app/`
> at `origin/main` tip `f9fa61e`. 64 page files enumerated via Glob; route
> tree authoritatively read from the filesystem (Next.js route groups
> `(...)` removed from URL).
>
> Method: static React-tree analysis. Live authenticated end-to-end
> walkthrough is reserved for Tom; HTTP 307→/login confirms middleware is
> live but cannot distinguish a real route from a 404.

---

## Legend

- **Nav**: Y = entry in `src/lib/nav/manifest.ts`; N = file exists but only reachable by direct link.
- **Role**: `min_role` per nav manifest, OR layout-level RoleGate for non-nav routes.
- **Action implemented**: Y = code is wired, N = button shows a placeholder, P = partial / IDB-backed only.
- **Issues**: P0/P1/P2/P3 against the same severity scale as
  `overnight_audit_2026-05-01.md` §0.

---

## Overview

| Route | Page title | Nav | Role | Primary action | Secondary | hrefs / pushes | Targets exist | Action wired | Success state | Error state | Mobile | EN/LTR | Issues |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `/` | (redirect) | N | viewer | redirect to `/login?redirectTo=%2Fdashboard` | — | `/login?redirectTo=%2Fdashboard` | Y | Y | Y | — | OK | OK | — |
| `/dashboard` | Dashboard (7-block control tower) | Y | viewer:read | (read-only landing) | quick-actions launcher (15 tiles) | `/inbox`, `/inbox?view=exceptions&sort=…`, `/admin/jobs`, plus 15 quick-action hrefs (all canonical) | Y | Y | Y (live blocks) | per-block ErrorState | OK (>=md) | OK | — |
| `/dashboard/v2` | Control tower (v2) | Y | viewer:read | (morning view) | break-glass deep-link, Critical Today rows, Slipped Plans rows, "Hide/Show Coming next" disclosure | `/dashboard`, `/admin/integrations#break-glass`, `/inventory?item_id=`, `/exceptions?id=`, `/planning/production-plan?from=…&to=…` | Y | Y | live blocks render rows; placeholder block shows `Awaiting read-model` Badge | per-block ErrorState | OK | OK | — (cycle 9 P1-1 closed) |
| `/profile` | Profile | N | viewer | (user info display) | sign-out via TopBar | `/auth/signout` | Y | Y | Y | — | OK | OK | — |

## Inbox & exceptions

| Route | Page title | Nav | Role | Primary action | Secondary | hrefs / pushes | Targets exist | Action wired | Success state | Error state | Mobile | EN/LTR | Issues |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `/inbox` | Inbox (unified) | Y | viewer:read | acknowledge / resolve / Review deep-link | view filter chips | `/inbox?<view=…&sort=…>`, deep-link to approval pages, deep-link to credit-needed page | Y | Y | inline acknowledge + resolve toast | per-source error banner | OK | OK | — |
| `/inbox/approvals/waste/[submission_id]` | Review waste / adjustment approval | N | planner+admin | approve / reject | back to inbox | `/inbox` | Y | Y | toast + redirect | banner | OK | OK | — |
| `/inbox/approvals/physical-count/[submission_id]` | Review physical count approval | N | planner+admin | approve / reject | back to inbox | `/inbox` | Y | Y | toast + redirect | banner | OK | OK | — |
| `/inbox/credit/[exception_id]` | LionWheel credit-needed | N | planner+admin | mark credit / dismiss | back to inbox | `/inbox` | Y | Y | toast + redirect | banner | OK | OK | — |
| `/exceptions` | (redirect) | N | viewer | redirects to `/inbox?view=exceptions` | — | `/inbox?view=exceptions` | Y | Y | — | — | OK | OK | — |

## Stock / Operations

| Route | Page title | Nav | Role | Primary action | Secondary | hrefs / pushes | Targets exist | Action wired | Success state | Error state | Mobile | EN/LTR | Issues |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `/stock/receipts` | Goods Receipt | Y | stock:execute | submit GR (with or without PO) | retry | (none) | — | Y | Loop 4 success-context panel | category banner | OK | OK | — |
| `/stock/waste-adjustments` | Waste / Adjustment | Y | stock:execute | submit waste/adjust | retry | (none) | — | Y | toast + reset | banner | OK | OK | — |
| `/stock/physical-count` | Physical Count | Y | stock:execute | open count → submit | cancel | (none) | — | Y | toast + redirect | banner + freeze-guard | OK | OK | — |
| `/stock/production-actual` | Production Actual | Y | stock:execute | submit production actual (optional from_plan_id) | retry without link, edit, recover-without-link | `/planning/production-plan` (4 occurrences — recovery / Open plan deep-links) | Y | Y | confirmation panel with variance row | typed category banner | OK | OK | — (cycle 2/5/6 closed) |
| `/inventory` | Inventory (live stock + value) | Y | viewer:read | (read-only) | filter chips | (none) | — | Y | Y | banner | OK | OK | — (Loop 11 supply_method-aware costs) |
| `/stock/movement-log` | Movement Log | Y | viewer:read | (read-only) | filter | (none) | — | Y | Y | banner | OK | OK | — (Loop 4 fixes) |
| `/stock/submissions` | My History | Y | stock:execute | (read-only of user's own submissions) | — | per-row deep-link to submission detail | depends on submission type | Y | Y | banner | OK | OK | — |

## Planning corridor

| Route | Page title | Nav | Role | Primary action | Secondary | hrefs / pushes | Targets exist | Action wired | Success state | Error state | Mobile | EN/LTR | Issues |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `/planning` | Planning Overview | Y | planning:read | (landing) | links to forecast / runs / inventory-flow | `/planning/forecast` (3x), `/planning/runs` (3x) | Y | Y | tile content | banner | OK | OK | — |
| `/planning/forecast` | Forecast | Y | planning:read | (list) | New draft, open detail, run planning | `/planning/forecast/new`, `/planning/forecast/[version_id]`, `/planning/runs` | Y | Y | row drilldown | banner | OK | OK | — |
| `/planning/forecast/new` | New forecast draft | N | planning:execute | create draft + redirect | back to list | `/planning/forecast/[id]`, `/planning/forecast` | Y | Y | toast + redirect | banner | OK | OK | — |
| `/planning/forecast/[version_id]` | Forecast (8-week planning horizon) | N | planning:read (write=planning:execute) | edit cells / save / publish / discard / Run planning | back, "Active forecast" callout | `/planning/forecast` (3x), `/planning/runs` (1x — Run planning CTA) | Y | Y | actionSuccess banner + as_of chip | category-aware banner with "Seed all active items" CTA on INCOMPLETE_HORIZON | OK | OK (cycle 4 P0-J closed) | — (cycle 9 P0-1 closed) |
| `/planning/runs` | Planning runs | Y | planning:read | trigger run | filter, drilldown | `/planning/runs/[id]` (router.push on create) | Y | Y | redirect to detail | banner | OK | OK | — (cycle 3 P0-E closed) |
| `/planning/runs/[run_id]` | Planning run detail | N | planning:read | view recommendations + exceptions; bulk-approve production recs | tabs, deep-links to forecast / jobs / rec drilldown | `/planning/forecast`, `/admin/jobs`, `/planning/runs` (3x), `/planning/runs/[id]/recommendations/[rec_id]` (router.push) | Y | Y | toast + cache invalidate | per-tab banner | OK | OK | — (cycle 3 P0-B / cycle 6 bulk-approve closed) |
| `/planning/runs/[run_id]/recommendations/[rec_id]` | Recommendation detail | N | planning:read | approve, dismiss, convert-to-PO | back to run | `/planning/runs` (3x), `/purchase-orders/[po_id]` (router.push on convert), `/admin/masters/components/<id>` (Fix link), `/planning/forecast/<id>` (signal #21 forecast deep-link) | Y | Y | toast + cache invalidate | banner with category copy | OK | OK | — (cycle 3 P0-C / cycle 5 #21 closed) |
| `/planning/production-plan` | Daily Production Plan | Y | planning:read | Add Manually, Add from Recommendations, edit/cancel/done per row | quick-links | `/planning/runs` (3x), `/planning/forecast`, `/planning/inventory-flow`; modal POSTs to `/api/production-plan` | Y | Y | toast + cache invalidate, variance row on done | typed category banner (cycle 9) | OK | OK | — (cycle 4/5/9 closed) |
| `/planning/production-simulation` | Production Simulation | Y | planning:read | (simulator UI) | — | (none — IDB only) | — | P | local-only | local-only | OK | OK | **P0** false-green — IDB-backed; "nothing here calls the API" comment in source. CURRENT_STATE.md tracks Tom decision PSDP-1..4 as queued. |
| `/planning/inventory-flow` | Inventory Flow | Y | planning:read | (read-only board) | item drilldown, Unmapped SKU banner deep-link | `/planning/inventory-flow/[itemId]`, `/admin/sku-aliases` | Y | Y | filter persistence in URL | banner | OK | OK | — |
| `/planning/inventory-flow/[itemId]` | Item flow detail | N | planning:read | (read-only) | back to list | `/planning/inventory-flow` | Y | Y | Y | banner | OK | OK | — |
| `/planning/blockers` | חסמים בתכנון (Tom-locked Hebrew) | Y | planning:read | (worklist) | row drilldown | `/planning/runs` (1x in BlockersStates) | Y | Y | Y | banner | OK | **HE/RTL Tom-locked exception** | — |
| `/planning/boms` | BOM Simulation | N | planning:read (Quick action) | (simulator UI) | — | (none — IDB only) | — | P | local-only | local-only | OK | OK | **P0** false-green — IDB-backed (similar profile to production-simulation; queued post PO 60-loop corridor per memory). |
| `/planning/weekly-outlook` | Weekly Outlook | N | planning:read (orphaned from nav) | (forecast-by-week table) | — | depends on file | depends | depends | depends | depends | unknown | unknown | **P2** — file exists but not in nav manifest; reachable only by direct URL bookmark. Discoverability gap. |

## Purchase Orders

| Route | Page title | Nav | Role | Primary action | Secondary | hrefs / pushes | Targets exist | Action wired | Success state | Error state | Mobile | EN/LTR | Issues |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `/purchase-orders` | Purchase Orders | Y | viewer:read | (list) | New PO, drilldown, filter | `/purchase-orders/new` (router.push), `/purchase-orders/[id]` (router.push), `/planning/runs` | Y | Y | row click drilldown | banner | OK | OK | — |
| `/purchase-orders/new` | Manual PO create | N | planner+admin | create PO | back, idempotent existing-PO link | `/purchase-orders/[id]` (router.push on 201, 1.5s redirect on 409), `/purchase-orders` (Cancel) | Y | Y | redirect on 201, banner on 409 idempotent | field-level Zod issues[] mapping + scroll-to-first-invalid (cycle 9) | OK | OK | — (cycle 9 P0-2 closed) |
| `/purchase-orders/[po_id]` | Purchase Order detail | N | viewer:read (write=planner+admin) | cancel PO, edit lines | back to list, "Manual entry" callout, over-receipt warning chip | `/purchase-orders` (back), `/planner/exceptions` (over-receipt warning — **BROKEN**, see Issues) | partial | Y | toast + cache invalidate | banner | OK | OK | **P1** dead-link `href="/planner/exceptions"` at line 885 (over-receipt warning chip). `/planner/exceptions` is NOT a real route — the canonical route is `/exceptions` (which itself redirects to `/inbox?view=exceptions`). |

## Admin

| Route | Page title | Nav | Role | Primary action | Secondary | hrefs / pushes | Targets exist | Action wired | Success state | Error state | Mobile | EN/LTR | Issues |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `/admin/items` | Items | Y | admin:execute | (list) | New product, drilldown | `/admin/products/new`, `/admin/items/[item_id]` (legacy redirect to `/admin/products/[item_id]`) | Y | Y | row click drilldown | banner | OK | OK | **P3** Two parallel admin hierarchies: `/admin/items` (list) + `/admin/products/[item_id]` (legacy slice5 1456 LoC) + `/admin/masters/items/[item_id]` (Tranche D pattern). Operator does not know which is canonical. (cycle 1 audit §11) |
| `/admin/items/[item_id]` | Item redirect | N | admin:execute | redirect to `/admin/products/[item_id]` | — | `/admin/products/[item_id]` | Y | Y | — | — | OK | OK | (legacy compat) |
| `/admin/products/[item_id]` | Product 360 (legacy slice5) | N | admin:execute | edit master, BOM, supplier, anchors, policy | tab navigation | `/admin/items` (back), `/planning/boms` (BOM tab) | partial | Y | toast | banner | OK | OK | — (legacy; coexists with `/admin/masters/items/[item_id]`) |
| `/admin/products/new` | New Product wizard | N | admin:execute | create item with policy + BOM | save draft | `/admin/items` (back), `/admin/planning-policy`, `/admin/products/[id]` (router.push on create) | Y | Y | toast + redirect | banner | OK | OK | — |
| `/admin/components` | Components | Y | admin:execute | (list) | drilldown, supplier picker | `/admin/components/[component_id]` (file exists at slice5) and `/admin/masters/components/[component_id]` (Tranche D) | Y | Y | drilldown | banner | OK | OK | **P3** dual hierarchy (same as Items) |
| `/admin/components/[component_id]` | Component detail (legacy slice5) | N | admin:execute | edit master, supplier mapping | back | `/admin/components` | Y | Y | toast | banner | OK | OK | — |
| `/admin/masters/components/[component_id]` | Component (masters) | N | admin:execute | (read-only with tabs) | back to list | `/admin/components` | Y | Y | Y | banner | OK | OK | — |
| `/admin/suppliers` | Suppliers | Y | admin:execute | (list) | drilldown | `/admin/suppliers/[id]`, `/admin/masters/suppliers/[id]` (Tranche D) | Y | Y | drilldown | banner | OK | OK | **P3** dual hierarchy |
| `/admin/suppliers/[supplier_id]` | Supplier detail (legacy slice5) | N | admin:execute | edit, supplier-items table with cost edit | back to list | `/admin/suppliers` | Y | Y | toast on PATCH | banner | OK | OK | — (Loop 11 cost-edit live) |
| `/admin/masters/suppliers/[supplier_id]` | Supplier (masters) | N | admin:execute | (read-only with tabs) | back to list | `/admin/suppliers` | Y | Y | Y | banner | OK | OK | — |
| `/admin/supplier-items` | Supplier Items | Y | admin:execute | (list / mapping) | search, edit | (no router.push) | — | Y | Y | banner | OK | OK | — |
| `/admin/planning-policy` | Planning Policy | Y | admin:execute | (per-item policy) | search, edit | (no router.push) | — | Y | Y | banner | OK | OK | — |
| `/admin/sku-aliases` | SKU Aliases | Y | admin:execute | approve unmapped → alias | filter, search | URL-state via router.replace | (self) | Y | success banner with resolved-exceptions count | banner | OK | OK | — (cycle 8 fix landed) |
| `/admin/sku-map` | SKU Mappings | Y | admin:execute | (mapping list) | — | (no router.push) | — | Y | Y | banner | OK | OK | — |
| `/admin/sku-health` | SKU Health | Y | admin:execute | (read-only health board) | — | (no router.push) | — | Y | Y | banner | OK | OK | **P3** TODO comment in source for future shopify_variant_match column. |
| `/admin/holidays` | Holidays (IL) | Y | admin:execute | CRUD: create, edit, archive, bulk-import | filter | (no router.push) | — | Y | toast + cache invalidate | banner | OK | OK | — (cycle 8 closed) |
| `/admin/integrations` | Integrations | Y | admin:execute | break-glass toggle, freshness review | deep-links | `/admin/sku-aliases?channel=shopify` (3x), `/admin/jobs` | Y | Y | toast | banner | OK | OK | — |
| `/admin/jobs` | Jobs | Y | admin:execute | (read-only monitor) | — | (no router.push) | — | Y | Y | banner | OK | OK | — |
| `/admin/users` | Users | Y | admin:execute | (read-only) | role-context | (no router.push) | — | Y | Y | banner | OK | OK | — |
| `/admin/boms` | BOMs (legacy editor) | N | admin:execute | (BOM list) | drilldown | `/admin/boms/[head_id]` | Y | Y | Y | banner | OK | OK | — (legacy; nav points at `/admin/masters/boms`) |
| `/admin/boms/[head_id]` | BOM head detail (legacy) | N | admin:execute | edit lines, version | back | `/admin/boms`, `/admin/boms/[head_id]/versions/[version_id]` (router.push) | Y | Y | toast | banner | OK | OK | — |
| `/admin/boms/[head_id]/versions/[version_id]` | BOM version detail (legacy) | N | admin:execute | edit lines | back | `/admin/boms/[head_id]` (router.push) | Y | Y | toast | banner | OK | OK | — |
| `/admin/masters/boms` | BOMs (masters) | Y | admin:execute | (list) | drilldown | `/admin/masters/boms/[bom_head_id]` (router.push), legacy `/admin/boms/[head_id]` (preserved) | Y | Y | row click | banner | OK | OK | — |
| `/admin/masters/boms/[bom_head_id]` | BOM head (masters) | N | admin:execute | (view-only with 3 tabs) | back, version drilldown | `/admin/masters/boms`, `/admin/masters/boms/[id]/[version_id]` (router.push) | Y | Y | Y | banner | OK | OK | — |
| `/admin/masters/boms/[bom_head_id]/[version_id]` | BOM version (masters) | N | admin:execute | (view-only with 3 tabs incl. compare) | back, edit | `/admin/masters/boms/[id]/[version_id]/edit`, `/admin/masters/components/<id>` (router.push) | Y | Y | Y | banner | OK | OK | — |
| `/admin/masters/boms/[bom_head_id]/[version_id]/edit` | BOM version edit | N | admin:execute | edit lines | save / cancel | back to detail | Y | Y | toast | banner | OK | OK | — |
| `/admin/masters/items/[item_id]` | Item (masters) | N | admin:execute | (read-only with 6 tabs) | back, deep-links | `/admin/items`, `/admin/masters/boms` | Y | Y | Y | banner | OK | OK | — |
| `/admin/masters/archive` | Archive | Y | admin:execute | (read-only archive) | restore | (no router.push) | — | Y | Y | banner | OK | OK | — |
| `/admin/masters/health` | Master Data Health | Y | admin:execute | (read-only health board) | per-row resolve | (deep-link to master) | Y | Y | Y | banner | OK | OK | — |
| `/admin/purchase-orders/parity-check` | PO parity check | N | admin:execute | (parity check tool) | — | (no router.push) | — | Y | Y | banner | OK | OK | — |

## Auth

| Route | Page title | Nav | Role | Primary action | Secondary | hrefs / pushes | Targets exist | Action wired | Success state | Error state | Mobile | EN/LTR | Issues |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `/login` | Sign in | N | (public) | request magic link | redirectTo | `/auth/signout`, `/dashboard` | Y | Y | "check your inbox" banner | banner | OK | OK | — |
| `/auth/signout` | Signing out… | N | viewer | clears Supabase session, redirect | — | `/`, `/login` (router.replace) | Y | Y | — | — | OK | OK | — |

---

## Summary

- **Total routes enumerated:** 64 page.tsx files → 60 unique URLs (4 are layout-only).
- **All nav-manifest hrefs target existing routes:** YES.
- **Route groups (`(...)`) leak into URL strings:** 1 pre-existing in `src/app/(shared)/dashboard/page.tsx:66` — TypeScript import path, NOT a URL string. Repeatedly verified across cycles 4-9 lint:urls runs. Outside corridor scope to fix in a single-file commit.
- **Dead links found this cycle:** see `dead_end_audit.md` cycle 10 section.
- **False-green surfaces:** 2 — `/planning/production-simulation` + `/planning/boms` (both IDB-only, no API). CURRENT_STATE.md tracks decision pack PSDP-1..4 as queued post PO 60-loop corridor.
- **Dual-hierarchy admin surfaces:** 3 — `/admin/items` ↔ `/admin/products/[item_id]` ↔ `/admin/masters/items/[item_id]`; same for components and suppliers. P3 confusion debt (cycle 1 §11). Out of corridor scope.
- **Tom-locked exceptions:** `/planning/blockers` Hebrew page-title.

## Open follow-ups for next cycles

1. **P1** dead-link on `/purchase-orders/[po_id]:885` over-receipt warning chip — `/planner/exceptions` should be `/inbox?view=exceptions`. Logged as fix-as-task in `dead_end_audit.md`. Out-of-scope this cycle (purchase-orders surface, not pure planning corridor; needs governance carve-out for in-cycle fix or a per-form Mode B).
2. **P0** `/planning/production-simulation` IDB false-green (Tom decision PSDP-1..4 queued).
3. **P0** `/planning/boms` IDB false-green (BOM Simulation Queued post PO 60-loop corridor per memory).
4. **P2** `/planning/weekly-outlook` orphaned from nav manifest — only reachable by direct URL bookmark.
5. **P3** dual admin hierarchy confusion (items / components / suppliers under both `/admin/<entity>/[id]` legacy slice5 and `/admin/masters/<entity>/[id]` Tranche D).
