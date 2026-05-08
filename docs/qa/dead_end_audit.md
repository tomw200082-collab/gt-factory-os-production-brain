# Portal Dead-End Audit — running log

> Authored / extended by `executor-w2`. Tracks every dead-end pattern found
> across the canonical portal at `c:/Users/tomw2/Projects/window2-portal-sandbox`.
>
> Companion docs:
> - `runtime_dead_end_audit.md` — cycle 9 P0 triage report
> - `route_action_matrix.md` — full route × action matrix
> - `../overnight_audit_2026-05-01.md` — cycle 1 cross-corridor audit
>
> Authority: `CLAUDE.md` durable contract, `EXECUTION_POLICY.md` Mode
> B-Planning-Corridor amendment 2026-05-02.

---

## Cycle 10 dead-end sweep (2026-05-02)

> Method: `Grep` on canonical sandbox at `origin/main` tip `f9fa61e` for the
> known dead-end patterns:
>
> 1. `router.push('...')` to non-existent routes
> 2. `<Link href='...'>` to non-existent routes
> 3. buttons with empty / TODO / "coming soon" `onClick`
> 4. disabled buttons that should be enabled
> 5. "Coming next" / "Coming soon" text without owner cycle reference
> 6. approve / convert / create / submit buttons that don't actually run
>
> Followed by route-existence cross-check against the filesystem-derived URL
> registry.

### Patterns 1 + 2 — `router.push` and `<Link>` href targets

All `router.push` and `Link` href targets enumerated in
`route_action_matrix.md`. Cross-checked against the route registry produced
by `Glob` on `src/app/**/page.tsx`. Every target except the one listed below
resolves to a real page.

| Severity | File:line | Symptom | Fix-as-task | In-scope? |
|---|---|---|---|---|
| **P1** | `src/app/(po)/purchase-orders/[po_id]/page.tsx:885` | `<a href="/planner/exceptions">⚠ Over-received</a>` on the over-receipt warning chip in the line-status cell. The route `/planner/exceptions` does NOT exist — the canonical URL is `/exceptions`, which itself is a redirect to `/inbox?view=exceptions`. Operator clicking the chip lands on the auth page (because middleware redirects every unmatched URL to `/login`), or, after authenticating, the unmatched URL becomes a hard 404. | Replace `href="/planner/exceptions"` with `href="/inbox?view=exceptions"` (the canonical inbox URL with the exceptions filter). Skip the redirect hop entirely. Optionally append `&category=over_receipt` filter to scope the inbox to the relevant exception (only if the inbox view supports the `category` query param — confirmed via `src/app/(inbox)/inbox/page.tsx`). | NO — `/purchase-orders/[po_id]` is not enumerated under Mode B-Planning-Corridor §Allowed surfaces beyond what cycle 9 P0-D opened (Hebrew banner only). The dispatch instruction says "Do NOT fix dead ends OUTSIDE Mode B-Planning-Corridor scope". This finding is logged as a fix-as-task for next cycle's PO-scoped Mode B (or a single-line carve-out from Tom). |

### Pattern 3 — empty / TODO / "coming soon" `onClick`

`Grep` for `onClick={() => {}}`, `onClick={undefined}`, `onClick={null}`,
`onClick={() => null}`, plus a wide search for `coming soon`, `TODO`, `tbd`
within `src/app/`.

Findings: ZERO empty `onClick` handlers across the entire canonical portal.

`Coming next` / `Coming soon` text appears in:
- `src/app/(shared)/dashboard/v2/page.tsx:606,789` — intentional placeholder
  copy on the §4.2/§4.3/§4.5/§4.6/§4.7/§4.8/§4.9 placeholder cards. Each
  placeholder is owned by an explicit "Awaiting read-model" badge and is
  collapsed below the live blocks (cycle 9 P1-1 closure). NOT a dead end.
- `src/app/(admin)/admin/holidays/page.tsx:6` — comment block referencing the
  PRIOR "coming soon" EmptyState that was REPLACED by this page in cycle 8.
  NOT a dead end.
- `src/app/(admin)/admin/sku-health/page.tsx:15,29` — TODO comments for a
  future shopify_variant_match column. Code is functional today; comments
  flag a follow-up enhancement. NOT a dead end.

**Verdict:** zero new findings on pattern 3.

### Pattern 4 — disabled buttons that should be enabled

`Grep` for `disabled=` across `src/app/`. 30 files matched. Spot-checked
each: every `disabled` is correctly gated by a real submit/loading/role
condition (e.g. `disabled={mutation.isPending}` or
`disabled={!hasUnsavedChanges}` or `disabled={!canApprove}`). No
permanently-disabled buttons that should be enabled.

**Verdict:** zero new findings on pattern 4.

### Pattern 5 — "Coming next" / "Coming soon" text without owner cycle reference

Already covered under pattern 3. All 3 distinct sources have an explicit
owner / cycle reference.

**Verdict:** zero new findings on pattern 5.

### Pattern 6 — approve / convert / create / submit buttons that don't actually run

Spot-checked all the highest-traffic write actions in the portal:

| Surface | Action | Implementation | Status |
|---|---|---|---|
| `/planning/runs/[run_id]` | Approve recommendation (per-row) | POST `/api/v1/mutations/planning/recommendations/:id/approve` via approveMutation | OK |
| `/planning/runs/[run_id]` | Bulk-approve production recs (cycle 6) | sequential per-rec POST | OK |
| `/planning/runs/[run_id]` | Dismiss recommendation | POST dismiss endpoint | OK |
| `/planning/runs/[run_id]/recommendations/[rec_id]` | Convert to PO | POST + router.push to PO detail on success | OK |
| `/planning/forecast/[version_id]` | Save lines | POST save endpoint | OK |
| `/planning/forecast/[version_id]` | Publish | POST publish endpoint | OK |
| `/planning/forecast/[version_id]` | Discard / Revise | POST status endpoint | OK |
| `/planning/forecast/[version_id]` | Seed all active items | POST seed endpoint | OK |
| `/planning/production-plan` | Add Manually | POST `/api/production-plan` | OK |
| `/planning/production-plan` | Add from Recommendations (cycle 4) | POST with source_recommendation_id | OK |
| `/planning/production-plan` | Edit / Cancel / Mark done | per-row PATCH | OK |
| `/planning/inventory-flow` | Resolve unmapped SKU | deep-link to `/admin/sku-aliases` | OK (link, not in-page action) |
| `/stock/production-actual` | Submit actual | POST `/api/production-actuals` | OK |
| `/stock/production-actual` | Retry without link (PLAN_NOT_FOUND recovery) | re-POST with `from_plan_id: null` | OK |
| `/stock/receipts` | Submit GR | POST `/api/goods-receipts` | OK |
| `/stock/waste-adjustments` | Submit waste/adjust | POST `/api/waste-adjustments` | OK |
| `/stock/physical-count` | Open count → Submit | open + submit endpoints | OK |
| `/purchase-orders/new` | Create PO | POST `/api/purchase-orders` + router.push to detail | OK |
| `/purchase-orders/[po_id]` | Cancel PO | POST cancel endpoint | OK |
| `/purchase-orders/[po_id]` | Edit lines | per-line PATCH | OK |
| `/inbox` | Acknowledge exception | POST acknowledge endpoint | OK |
| `/inbox` | Resolve exception | POST resolve endpoint | OK |
| `/admin/sku-aliases` | Approve aliases | POST aliases endpoint | OK |
| `/admin/holidays` | Create / Edit / Archive / Bulk-import | CRUD endpoints | OK |
| `/admin/integrations` | Break-glass toggle | POST toggle endpoint | OK |

Spot-checked actions: 25/25 wired to real endpoints. No silent-no-op
write actions found.

**Verdict:** zero new findings on pattern 6.

### Pattern 7 — false greens (IDB-only / mock-data surfaces masquerading as live)

Two surfaces flagged in cycle 1 audit (P0-E + P0-G in `overnight_audit_2026-05-01.md`):

| Severity | File | Symptom | Fix-as-task | In-scope? |
|---|---|---|---|---|
| **P0** | `src/app/(planning)/planning/production-simulation/page.tsx:13-14` | Comment: "The page intentionally fetches everything client-side from the IDB-backed repos used by the rest of the planner sandbox; nothing here calls the API." When the API is the source of truth, this surface silently shows stale or empty data. | Tom decision pending — PSDP-1..4 decision pack queued in CURRENT_STATE.md §"Audit P0 status (cycles 2-7)". Either: (a) gut the IDB layer and re-implement against the live BOM / item / current_balances API; (b) add a banner stating the surface is local-only and not authoritative; (c) remove from nav until a backend exists. | NO — Tom-pending decision; not a W2 portal-only fix. |
| **P0** | `src/app/(planning)/planning/boms/page.tsx` (BOM Simulation, Quick Action target) | Same IDB-only profile per cycle 1 audit §1 + §10. | Same as above; queued post PO 60-loop corridor per memory `project_bom_simulation_queued.md`. | NO — Tom-pending decision; queued. |

### Pattern 8 — orphan files (file exists, not in nav, low-traffic discoverability)

| Severity | File | Symptom | Fix-as-task | In-scope? |
|---|---|---|---|---|
| **P2** | `src/app/(planning)/planning/weekly-outlook/page.tsx` | Page exists at `/planning/weekly-outlook` but is NOT in `src/lib/nav/manifest.ts`. Reachable only by direct URL bookmark. The `/planning/inventory-flow` "Daily" view supersedes it (per cycle 1 audit §11 the inventory-flow daily control tower replaced weekly-outlook 2026-04-26). | Decide whether to (a) remove `/planning/weekly-outlook/page.tsx` outright (deprecation), (b) redirect to `/planning/inventory-flow`, or (c) re-add to nav under a different label if the surface still has unique content. Static-analysis only confirms file exists; no judgment of whether the page renders meaningfully. | NO — out of corridor scope; deprecation decision is governance-level. |

### Pattern 9 — duplicate / dual-hierarchy admin surfaces

| Severity | Files | Symptom | Fix-as-task | In-scope? |
|---|---|---|---|---|
| **P3** | `/admin/items` (list) + `/admin/items/[item_id]` (redirect to legacy) + `/admin/products/[item_id]` (legacy slice5 1456 LoC) + `/admin/masters/items/[item_id]` (Tranche D pattern, read-only with tabs) | Three parallel item-detail surfaces. Operator clicking from a list page may land on different layouts depending on which list link they used. Per cycle 1 audit §11. | Tom-locked plan tranche; Mode B-AMMC + Mode B-Portal-Refactor jointly cover the eventual consolidation (`/admin/products/[id]` legacy may eventually fold into `/admin/masters/items/[id]`). Today both surfaces are kept live for backward-compat. | NO — out of corridor scope; consolidation tranche pending. |
| **P3** | `/admin/components` ↔ `/admin/components/[component_id]` ↔ `/admin/masters/components/[component_id]` | Same pattern as items. | Same. | NO. |
| **P3** | `/admin/suppliers` ↔ `/admin/suppliers/[supplier_id]` ↔ `/admin/masters/suppliers/[supplier_id]` | Same pattern as items. | Same. | NO. |
| **P3** | `/admin/boms` (legacy editor) ↔ `/admin/masters/boms` (Tranche E view-only) | Two BOM hierarchies (editor and read-only). Nav points at `/admin/masters/boms` (Tranche E); legacy editor remains live for direct URL bookmarks per Tranche E §G ("BOM editing surface at /admin/boms/* preserved entirely untouched — out-of-plan §'Tranche J' BOM-deep-logic window will consume that surface"). | Same as above; out-of-plan Tranche J pending. | NO. |

---

## Cycle 10 dead-end sweep summary

| Severity | Count | In-scope to fix this cycle | Logged for next cycle |
|---|---|---|---|
| P0 | 2 | 0 | 2 (production-simulation, boms — Tom-pending decisions) |
| P1 | 1 | 0 | 1 (PO detail `/planner/exceptions` dead-link) |
| P2 | 1 | 0 | 1 (`/planning/weekly-outlook` orphan) |
| P3 | 4 | 0 | 4 (dual admin hierarchies; one TODO comment) |

**No safe fixes found within Mode B-Planning-Corridor scope this cycle.**

The single P1 (`/planner/exceptions` on PO detail) is on a surface that is
NOT enumerated under Mode B-Planning-Corridor §Allowed (the cycle 9 P0-D
fix on the same file was a per-finding carve-out). Per the dispatch's
explicit rule "Do NOT fix dead ends OUTSIDE Mode B-Planning-Corridor scope
(admin pages, purchasing pages outside what cycle 9 already opened)", this
fix is logged as a fix-as-task and NOT applied this cycle. To close it, Tom
needs either a per-finding carve-out, or a per-form Mode B for PO surfaces.

The two P0 false-greens (`/planning/production-simulation` and
`/planning/boms`) are blocked by Tom's pending PSDP-1..4 decision and the
queued BOM Simulation post-PO-60-loop corridor.

---

## Tom's directive reconciliation

> "Do not turn this into only documentation"
> "Do not stop after finding issues without fixing safe P0/P1"

**This cycle yields zero in-scope safe fixes.** The dead-end sweep on the
canonical portal is — encouragingly — **almost completely clean** after
cycles 2-9. The single P1 found is on a surface explicitly excluded from
Mode B-Planning-Corridor scope. The two P0s are owner-pending decisions,
not portal-source defects.

If Tom wants in-cycle action on the `/planner/exceptions` dead-link, the
governance options are:

1. **Per-finding carve-out** added to the dispatch (precedent: cycle 9 P0-D
   on the same file).
2. **Per-form Mode B** for `/purchase-orders/[po_id]` (consumes signal #8
   PurchaseOrders or #13 PurchaseOrders-manual — both already emitted, so
   activation is one dispatch line away).
3. **Defer** to the next pure-PO Mode B cycle and accept that operators
   clicking the over-receipt warning chip currently land on /login or 404.

The portal is in a healthier dead-end state than cycle 1 audit suggested.
Cycles 2-9 closed the bulk of the corridor dead-ends (12 P0s in
`overnight_audit_2026-05-01.md` §16 → 4 still open per CURRENT_STATE.md
"Audit P0 status").

---

## History

- **Cycle 10 (2026-05-02)** — comprehensive sweep (this section).
- Earlier dead-end findings live in `runtime_dead_end_audit.md` (cycle 9
  triage) and `../overnight_audit_2026-05-01.md` (cycle 1 cross-corridor).
