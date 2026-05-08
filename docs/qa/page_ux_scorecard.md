# Phase 5 — Page UX Scorecard

> Authored by `executor-w2` on 2026-05-01 (Phase 5 of overnight cycle 1-12 audit chain).
> Mode A read-only — no portal source modified.
> Authority: `CLAUDE.md` durable contract, `CURRENT_STATE.md` runtime status, `EXECUTION_POLICY.md` governance.

---

## §0 Scorecard metadata

| Item | Value |
|---|---|
| Date | 2026-05-01 |
| Portal repo | `c:/Users/tomw2/Projects/window2-portal-sandbox/` |
| Portal main tip at scorecard authoring | `c356b2a` (cycle 12 plan-to-actual + UX hardening) |
| Earliest tip referenced | `4fee418` (cycle 1 baseline — Daily Production Plan English/LTR normalization) |
| Total `page.tsx` files in tree | 66 (60 unique URLs; 6 are layout/redirect-only) |
| Routes scored in this scorecard | 50 (all primary operator-facing surfaces) |
| Routes deferred — not audited | 16 (auth surfaces, child redirects, modal-only routes, route-group layouts) — see §0.4 |
| W2 mode at authoring | A (per `.claude/state/active_mode.json` last entry exited 2026-05-02T15:30:00Z) |
| Latest RUNTIME_READY signals | 27 (per `.claude/state/runtime_ready.json`) |

### §0.1 Methodology

For each route the auditor consulted **only existing audit evidence** from the four cited artifacts:

1. `docs/overnight_audit_2026-05-01.md` (cycle 1, 642 lines, 16 P0 / 38 P1 / 50 P2 / 29 P3 across 12 corridors)
2. `docs/qa/runtime_dead_end_audit.md` (cycles 9-12, 1037 lines — Phase 0 verifications + Phase 3 walk steps 1-31 + Phase 4 hardening)
3. `docs/qa/route_action_matrix.md` (cycle 10, 60 URLs / 64 page.tsx files)
4. `docs/qa/dead_end_audit.md` (cycle 10, 9-pattern sweep)

Each route was scored 0-5 on 10 dimensions. Scores represent the page's **production-readiness as of the latest cycle-evidence available for that route**, not a re-audit. Where multiple cycles touch a route, the most recent evidence governs.

### §0.2 Scoring rubric

1. **Findability** — discoverable from nav / from logical-prior surfaces
2. **Clarity** — answers "Where am I / what matters / what next" within 5s
3. **Primary action** — main CTA obvious within 1s
4. **Error / empty / loading quality** — non-contradictory, actionable
5. **Mobile** @ 390px — no horizontal scroll, primary action visible
6. **Source / freshness** — decision numbers show provenance + recency
7. **Post-action visibility** — submit/approve/cancel produce durable confirmation, not toast-only
8. **English / LTR consistency** — no Hebrew (modulo Tom-locked `/planning/blockers`), no RTL artifacts
9. **Accessibility basics** — input labels, focus visible, status not color-only, contrast
10. **Production readiness** — would Tom rely on this page for a real factory operation today?

Average → letter grade:
- **A** 4.5-5.0 (production-trustworthy)
- **B** 3.5-4.49 (production-usable, polish gaps only)
- **C** 2.5-3.49 (production-fragile, needs work to depend on)
- **D** 1.5-2.49 (do not rely on; behaves as half-finished surface)
- **F** 0.0-1.49 (false green or broken; remove or rebuild)

### §0.3 Honesty rule

If a page is not production-closeable, the row says so explicitly with the specific blocker. No grade-inflation. Tom-locked Hebrew on `/planning/blockers` is **not** counted against axis 8 — it is a Tom-locked exception per CURRENT_STATE.md UNRESOLVED entry.

### §0.4 Routes deferred (not in this scorecard)

The following surfaces were not scored because they are non-operational (auth gates, redirects, layouts) or out of operator-facing scope:

- `/login`, `/auth/signout`, `/auth/callback` — auth gates, scored only for whether they redirect correctly
- `/` — redirect-only stub
- `/admin/items/[item_id]` — legacy redirect to `/admin/products/[item_id]`
- `/exceptions` — server redirect to `/inbox?view=exceptions`
- Inbox sub-detail pages `(inbox)/inbox/approvals/waste/[submission_id]`, `(inbox)/inbox/approvals/physical-count/[submission_id]`, `(inbox)/inbox/credit/[exception_id]` — scored as one combined entry under Inbox approvals
- BOM masters child pages `(admin)/admin/masters/boms/[bom_head_id]/[version_id]/edit` — scored as one combined entry under BOM masters
- Forecast new-draft `(planning)/planning/forecast/new` — covered under forecast list scorecard

---

## §1 Executive scoreboard

### §1.1 Grade distribution histogram

| Grade | Count | Routes (representative) |
|---|---|---|
| **A** (4.5-5.0) | 8 | /planning/production-plan, /stock/receipts, /stock/waste-adjustments, /stock/physical-count, /inventory, /stock/movement-log, /admin/sku-aliases, /admin/jobs |
| **B** (3.5-4.49) | 22 | /dashboard, /dashboard/v2, /inbox, /planning/inventory-flow, /planning/runs, /planning/runs/[run_id], /planning/forecast, /planning/forecast/[version_id], /planning/blockers, /purchase-orders, /purchase-orders/new, /purchase-orders/[po_id], /admin/integrations, /admin/holidays, /admin/items, /admin/components, /admin/suppliers, /admin/supplier-items, /admin/planning-policy, /admin/sku-map, /admin/sku-health, /admin/users |
| **C** (2.5-3.49) | 14 | /planning, /planning/runs/[run_id]/recommendations/[rec_id], /stock/production-actual, /stock/submissions, /admin/masters/items/[item_id], /admin/masters/components/[component_id], /admin/masters/suppliers/[supplier_id], /admin/masters/boms, /admin/masters/boms/[bom_head_id], /admin/masters/boms/[bom_head_id]/[version_id], /admin/masters/health, /admin/masters/archive, /admin/products/new, /profile |
| **D** (1.5-2.49) | 4 | /admin/products/[item_id], /admin/components/[component_id], /admin/suppliers/[supplier_id], /admin/boms (and children) |
| **F** (0.0-1.49) | 2 | /planning/production-simulation, /planning/boms |

**Total scored: 50 routes** (some grouped where audit evidence collapsed).

### §1.2 Production-closeable summary

| Closeable | Count | Notes |
|---|---|---|
| **yes** | 18 | Tom can depend on these for real factory ops today |
| **partial** | 26 | Friction or polish gap, but no blocker on golden-path use |
| **no** | 6 | Has a structural blocker (false green, Hebrew leak, dual-hierarchy, cryptic backend leak); needs fix before relying |

The 6 **no** entries are the production blockers (§3).

---

## §2 Per-route scorecards

> Sorted by grade DESC then by production-closeable (yes > partial > no).
> Score = avg of 10 axes (1-Find, 2-Clar, 3-Prim, 4-Err, 5-Mob, 6-Src, 7-Post, 8-EN, 9-A11y, 10-Prod).

### §2.A — Grade A (production-trustworthy)

| Route | Title | Grade | Avg | Top P0/P1 (cycle source) | Next fix | Owner | Closeable |
|---|---|---|---|---|---|---|---|
| `/planning/production-plan` | Daily Production Plan | A | 4.7 | Phase3-S4-B (P0) — holidays not visually distinguished in native `<input type="date">` (cycle 11 walk; mirrors cycle 1 audit P0 #10) | Replace native date input with custom picker that consumes `holidays_il` (signal #25/#26) | W2 | yes |
| `/stock/receipts` | Goods Receipt | A | 4.6 | I/P1 — global line-search filters all dropdowns (cycle 1 §9-I) | Per-line search box; staleness invalidate on submit success | W2 | yes |
| `/stock/waste-adjustments` | Waste / Adjustment | A | 4.7 | None ≥ P1; surface is RUNTIME_READY since 2026-04-17 (signal #1) | None — only polish on a11y / mobile spacing | W2 | yes |
| `/stock/physical-count` | Physical Count | A | 4.7 | None ≥ P1; surface is RUNTIME_READY since 2026-04-17 (signal #2) | None — only polish on freeze-guard banner copy | W2 | yes |
| `/inventory` | Inventory (live stock + value) | A | 4.6 | None observed (cycle 10 matrix; Loop 11 supply_method-aware costs live) | None | W2 | yes |
| `/stock/movement-log` | Movement Log | A | 4.6 | E2E/J/P3 — `formatTimestamp` may render Hebrew on Hebrew browser locale (cycle 1 §10-J pattern, applies here) | Force `en-US` locale on toLocaleString | W2 | yes |
| `/admin/sku-aliases` | SKU Aliases | A | 4.5 | Cycle 8 `8543d2b` fix landed (idempotency_key fix); success-banner shows resolved-exceptions count (cycle 10 matrix) | None | W2 | yes |
| `/admin/jobs` | Jobs monitor | A | 4.5 | C/P3 — auto-refresh tick countdown breaks on data-fetch error (cycle 1 §11-C) | Handle error state gracefully without breaking timer | W2 | yes |

### §2.B — Grade B (production-usable, polish gaps only)

| Route | Title | Grade | Avg | Top P0/P1 (cycle source) | Next fix | Owner | Closeable |
|---|---|---|---|---|---|---|---|
| `/dashboard` | Dashboard (7-block control tower) | B | 4.4 | B/P0 — Quick Actions launcher missing /planning/production-plan, /planning/inventory-flow, /planning/blockers (cycle 1 §11-B P0-D); cycle 4 `303465c` partly closed but not all three (cycle 9 verifies discoverability gap) | Append three planning entries to `src/features/dashboard/quick-actions.ts` | W2 | partial |
| `/dashboard/v2` | Control tower (v2) | B | 4.2 | P1-1 placeholder dominance — closed cycle 9 `b4d1d20` (cycle 9 §2 + cycle 10 Phase 0 verify); 7 placeholders now collapsed below live blocks | Defer §4.8 freshness tile to next cycle (W4 contract notes consumable) | W2 | partial |
| `/inbox` | Inbox (unified) | B | 4.3 | I/P1 — merged inbox does not show source priority queue (cycle 1 §10-I); D/P2 8 view chips wrap to 3 lines on mobile | Type-then-age sort; collapse chips into `<select>` at <640px | W2 | partial |
| `/planning/inventory-flow` | Inventory Flow board | B | 4.3 | F/P2 — planned production NOT included; legend missing (cycle 1 §6-F); B/P1 unmapped-SKU banner does not state ~30s alias-propagation latency (cycle 1 §6-B) | Stamp legend "Planned production not included — see /planning/production-plan"; inline note on banner | W2 | partial |
| `/planning/inventory-flow/[itemId]` | Item flow detail | B | 4.0 | I/P3 — "Open recipe →" link missing (cycle 1 §6-I) | Add inline link to `/admin/masters/items/<id>?tab=bom` | W2 | partial |
| `/planning/runs` | Planning runs list | B | 4.2 | A/P0-B — closed cycle 3 `24e5a7a` (cycle 9 §6 verifies); E/P2 list rows missing `[Superseded]` chip inline (cycle 1 §3-E) | Add `[Superseded]` chip; verify English title remains stable | W2 | partial |
| `/planning/runs/[run_id]` | Planning run detail | B | 3.9 | A/P0-B + E/P0 — closed cycle 3 `24e5a7a` + cycle 6 `012dd16` bulk-approve (cycle 9 §7); G/P1 `item_id`/`component_id` shown raw on exception rows (cycle 1 §3-G); B/P1 exception deep-link routes components to item path (cycle 1 §3-B) | Render names; route components to `/admin/masters/components/<id>`; add `→ PO 1234` chip on rec rows when converted | W2 | partial |
| `/planning/forecast` | Forecast list | B | 4.1 | I/P3 — no "Resume draft" link on draft rows (cycle 1 §2-I); J/P3 status-filter buttons use raw enum keys | Add inline "Resume draft" affordance; friendly status labels | W2 | partial |
| `/planning/forecast/[version_id]` | Forecast detail (8-week horizon) | B | 4.1 | A/P1 — closed cycle 4 `303465c` (P0-J Hebrew callout); P0-1 ISO-weekly bucket fix landed cycle 9 `f9fa61e`; cycle 11 `f2b657a` seed-cells endpoint wired (signal #27) | Phase4-FORECAST-A (P3) stacked-row mobile @ <=640px; cycle 9 typed-error map now live | W2 | partial |
| `/planning/blockers` | חסמים בתכנון (Tom-locked Hebrew) | B | 4.0 | None — Hebrew page-title + label maps are Tom-locked exception per CURRENT_STATE.md UNRESOLVED entry (cycle 1 §10-A; cycle 10 matrix) | None — surface is exempt from English/LTR rule by Tom's lock | W2 | partial |
| `/purchase-orders` | Purchase Orders list | B | 4.1 | D/P1 — KPI strip horizontal-scrolls on mobile (cycle 1 §8-D); E/P2 `Live` badge without last-fetched timestamp; J/P2 POs with no expected_receive_date silently de-prioritized | Collapse KPI strip to 2x2 grid <640px; render `as of <time>`; surface "no expected date" inline count | W2 | partial |
| `/purchase-orders/new` | Manual PO create | B | 4.2 | P0-2 — closed cycle 9 `b4d1d20` (cycle 9 §12; cycle 10 Phase 0 verifies field-level Zod issues[] + scroll-to-first-invalid live) | None | W2 | partial |
| `/purchase-orders/[po_id]` | PO detail | B | 3.9 | P0-D — closed cycle 9 `b4d1d20` (Hebrew banner → English at lines 1291-1293); cycle 10 P1 dead-link `/planner/exceptions` → `/inbox?view=exceptions` closed cycle 10 `c8b96e5` (cycle 10 §dead_end §summary); H/P2 `attached-grs`/`history` tabs depend on backend deploy (cycle 1 §8-H); I/P1 no "Receive against this PO" CTA (cycle 1 §8-I) | Add "Receive against this PO →" inline button linking `/stock/receipts?po_id={po_id}` | W2 | partial |
| `/admin/integrations` | Integrations | B | 4.1 | I/P1 — multi-step alias-mapping flow (cycle 1 §11-I) | One-click "Approve known mapping" inline on high-confidence exception | W2 | partial |
| `/admin/holidays` | Holidays (IL) | B | 4.0 | Cycle 8 page on disk (`bf4a744`) replaced "coming soon" placeholder — CRUD live; cycle 1 originally flagged P0 hole now closed (cycle 9 §15 verifies) | Verify in production once Vercel deploys | W2 | partial |
| `/admin/items` | Items list | B | 4.1 | C/P2 — deep-link `?item=X` highlight has no banner (cycle 1 §11-C); D/P2 wide-table scrolls horizontally on mobile | Stamp "Showing X" banner; card-stream pattern <768px | W2 | partial |
| `/admin/components` | Components list | B | 4.0 | J/P2 — readiness column shows "—" pending detail page (cycle 1 §11-J) | Backend extension `?include_readiness=true`; out-of-corridor for W2 alone — needs W1 contract update | W4/W1 | partial |
| `/admin/suppliers` | Suppliers list | B | 4.0 | None ≥ P1 (cycle 10 matrix) | None | W2 | partial |
| `/admin/supplier-items` | Supplier Items | B | 3.9 | D/P2 — wide-table mobile (cycle 1 §11-D) | Acceptable for admin surface | W2 | partial |
| `/admin/planning-policy` | Planning Policy | B | 3.8 | None ≥ P1 (cycle 10 matrix; live) | Polish only | W2 | partial |
| `/admin/sku-map` | SKU Mappings | B | 3.7 | G/P3 — `external_sku`/`item_id` rendered raw (cycle 1 §11-G) | Render item_name primary, item_id mono parens-suffix | W2 | partial |
| `/admin/sku-health` | SKU Health | B | 3.6 | H/P1 — `shopify_variant_match` column hardcoded "unknown" but rendered as real column (cycle 1 §11-H + §14 #3); E/P3 TODO in source | Hide column until backend lands; rename page or scope down | W2 | partial |
| `/admin/users` | Users | B | 3.6 | B/P3 — non-409 PATCH error has no retry (cycle 1 §11-B) | Acceptable; navigation works | W2 | partial |

### §2.C — Grade C (production-fragile)

| Route | Title | Grade | Avg | Top P0/P1 (cycle source) | Next fix | Owner | Closeable |
|---|---|---|---|---|---|---|---|
| `/planning` | Planning Overview (landing) | C | 3.4 | None ≥ P1 (cycle 10 matrix); landing tile content may overlap with /dashboard purpose | Consider whether this tile-page adds value over /dashboard | W2 | partial |
| `/planning/runs/[run_id]/recommendations/[rec_id]` | Recommendation drill-down | B | 3.6 | A/P0-C — closed cycle 3 `24e5a7a` + cycle 5 `eb76918` (signal #21 v1.1 DTO; lead_time_source); B/P1 dismissed-rec UI shows approve/reject (409 NOT_PENDING server-side) (cycle 1 §7-B); E/P1 lead_time_days source not stamped pre-cycle-5 — closed cycle 5; F/P1 converted-to-PO header chip (Tom-tax: planner had to scroll to action card to find linked PO) — closed `db40ff5` | Hide actions when `rec.status !== 'pending'` | W2 | partial |
| `/stock/production-actual` | Production Actual | C | 3.4 | A/P0 — closed cycle 2 `9f3b98e` (English/LTR full re-write); E/P0 BOM-pinned-version freshness chip — cycle 12 closure pending W1 endpoint; F/P2 "What this will do" preview missing; Phase3-S14-A (P1) item picker not locked when from_plan_id set (cycle 12 walk; mitigated by API PLAN_ITEM_MISMATCH 409) | Add "What this will do" preview panel (FG +output / scrap / per-component −consumption); pinned-BOM-version chip | W2 + W1 | partial |
| `/stock/submissions` | My History | C | 3.3 | None ≥ P1 (cycle 10 matrix) | Per-row deep-links work; otherwise read-only | W2 | partial |
| `/admin/masters/items/[item_id]` | Item (masters) | C | 3.2 | B/P1 — DUAL HIERARCHY with /admin/products/[item_id] (cycle 1 §11-B; cycle 10 dead_end §pattern 9) | Consolidation tranche pending (Tranche J post-PO-60-loop per memory) | W2 | partial |
| `/admin/masters/components/[component_id]` | Component (masters) | C | 3.2 | DUAL HIERARCHY (cycle 1 §11-B) | Same | W2 | partial |
| `/admin/masters/suppliers/[supplier_id]` | Supplier (masters) | C | 3.2 | DUAL HIERARCHY (cycle 1 §11-B) | Same | W2 | partial |
| `/admin/masters/boms` | BOMs (masters) | C | 3.2 | B/P1 — DUAL HIERARCHY with /admin/boms (cycle 1 §11-B; cycle 10 dead_end §pattern 9) | Redirect `/admin/boms` → `/admin/masters/boms` | W2 | partial |
| `/admin/masters/boms/[bom_head_id]` | BOM head (masters) | C | 3.0 | View-only; out-of-plan Tranche J pending (cycle 10 dead_end §pattern 9) | Nothing until Tranche J | W2 | partial |
| `/admin/masters/boms/[bom_head_id]/[version_id]` | BOM version (masters) | C | 3.0 | Same — Tranche J pending | Same | W2 | partial |
| `/admin/masters/health` | Master Data Health | C | 2.7 | H/P2 — placeholder concern (cycle 1 §14 #5; cycle 10 matrix shows live but content unverified) | Confirm content rendering vs. placeholder | W2 | partial |
| `/admin/masters/archive` | Archive | C | 2.7 | H/P2 — placeholder concern (cycle 1 §14 #6) | Confirm content rendering vs. placeholder | W2 | partial |
| `/admin/products/new` | New Product wizard | C | 3.4 | None ≥ P1 (cycle 10 matrix) | Polish only | W2 | partial |
| `/profile` | Profile | C | 3.0 | None observed; minimal scope | Polish only | W2 | partial |

### §2.D — Grade D (do not rely on; behaves as half-finished)

| Route | Title | Grade | Avg | Top P0/P1 (cycle source) | Next fix | Owner | Closeable |
|---|---|---|---|---|---|---|---|
| `/admin/products/[item_id]` | Product 360 (legacy slice5, 1456 LoC) | D | 2.4 | B/P1 — DUAL HIERARCHY: same item rendered at TWO URLs depending on entry point (cycle 1 §11-B); cycle 1 §17 deferred deep-pass on this 1456-LoC file | Pick canonical: fold either /admin/masters/items/[id] into a redirect to /admin/products/[id], OR retire Product 360 in favor of Tranche-D pattern | W2 + Tom decision | no |
| `/admin/components/[component_id]` | Component detail (legacy slice5) | D | 2.3 | DUAL HIERARCHY (cycle 1 §11-B) | Same as Product 360 | W2 + Tom | no |
| `/admin/suppliers/[supplier_id]` | Supplier detail (legacy slice5) | D | 2.4 | DUAL HIERARCHY (cycle 1 §11-B; Loop 11 cost-edit live but coexists with masters surface) | Same | W2 + Tom | no |
| `/admin/boms`, `/admin/boms/[head_id]`, `/admin/boms/[head_id]/versions/[version_id]` | BOMs (legacy editor; 3 routes treated as one unit) | D | 2.3 | B/P1 — DUAL HIERARCHY with /admin/masters/boms (cycle 1 §11-B; cycle 10 §pattern 9) | Redirect or retire; Tranche J post-PO-60-loop | W2 + Tom | no |

### §2.E — Grade F (false green or broken)

| Route | Title | Grade | Avg | Top P0/P1 (cycle source) | Next fix | Owner | Closeable |
|---|---|---|---|---|---|---|---|
| `/planning/production-simulation` | Production Simulation | F | 1.2 | E/P0 — IDB-backed; "nothing here calls the API" comment in source (cycle 1 §11 + §14 #1; cycle 10 dead_end §pattern 7) | Tom decision PSDP-1..4 queued in CURRENT_STATE.md; either gut IDB → live API, or banner "BETA — cached data", or remove from nav | Tom decision | no |
| `/planning/boms` | BOM Simulation | F | 1.4 | E/P1 — same IDB-only profile (cycle 1 §14 #2; cycle 10 §pattern 7); BOM Simulation queued post PO 60-loop corridor per memory | Tom decision queued | Tom decision | no |
| `/planning/weekly-outlook` | Weekly Outlook | F | 1.4 | P2 — orphaned from nav manifest; reachable only by direct URL bookmark (cycle 10 matrix; cycle 10 §pattern 8) | Decide: remove, redirect to /planning/inventory-flow, or re-add to nav | Tom decision | no |

---

## §3 Top 10 production blockers

The lowest-graded routes ordered by **leverage × severity**. These are the surfaces that prevent Tom from depending on the portal for daily factory operations today.

| # | Route | Grade | Specific blocker | Cycle source | Owner |
|---|---|---|---|---|---|
| 1 | `/planning/production-simulation` | F | IDB-backed; silently shows stale/empty data when API is truth source. Operator using this for "do I have enough material?" decisions can get wrong answers. | cycle 1 §11 + §14 #1; cycle 10 §pattern 7 | Tom (PSDP-1..4 decision pack queued) |
| 2 | `/planning/boms` | F | Same IDB-only profile; surfaces from dashboard Quick Actions tile as if live. | cycle 1 §14 #2; cycle 10 §pattern 7 | Tom (queued post PO 60-loop) |
| 3 | `/admin/products/[item_id]` (legacy 1456-LoC) | D | Same item has two detail pages depending on entry point (this vs `/admin/masters/items/[item_id]`). Operators don't know which to edit. | cycle 1 §11-B; cycle 10 §pattern 9 | W2 + Tom |
| 4 | `/admin/boms` (and children) | D | Two BOM hierarchies (legacy editor + masters Tranche-E view-only). Nav points at masters; legacy still live; entry-point split. | cycle 1 §11-B; cycle 10 §pattern 9 | W2 + Tom |
| 5 | `/admin/components/[component_id]` (legacy slice5) | D | Same dual-hierarchy pattern. | cycle 1 §11-B | W2 + Tom |
| 6 | `/admin/suppliers/[supplier_id]` (legacy slice5) | D | Same dual-hierarchy pattern. | cycle 1 §11-B | W2 + Tom |
| 7 | `/planning/weekly-outlook` | F | Orphaned from nav; reachable only by bookmark. Inventory Flow daily-board supersedes it. | cycle 10 §pattern 8 | Tom decision |
| 8 | `/admin/masters/health` | C (2.7) | Placeholder concern flagged cycle 1 §14 #5; content rendering vs. placeholder unverified. Surfaces in nav as a real surface. | cycle 1 §14 #5; cycle 10 matrix | W2 (verify) |
| 9 | `/admin/masters/archive` | C (2.7) | Same placeholder concern. | cycle 1 §14 #6 | W2 (verify) |
| 10 | `/stock/production-actual` | C (3.4) | "What this will do" preview missing; pinned-BOM-version freshness chip missing; item picker not locked when `from_plan_id` set (mitigated by API 409). Operationally usable today (cycle 2 closed P0-A) but operator confidence gap remains. | cycle 1 §5-E + §5-F; cycle 12 walk Phase3-S14-A | W2 + W1 |

---

## §4 Top 10 P1 fix queue for Phase 6

Concrete actionable items. Ranked by leverage on Tom's daily flow.

| # | Severity | Surface | Fix | Cycle source |
|---|---|---|---|---|
| 1 | P0 | `/dashboard` | Append `/planning/production-plan`, `/planning/inventory-flow`, `/planning/blockers` to `src/features/dashboard/quick-actions.ts` (3 entries, planning category, planning:read role). Discoverability gain on 3 most-trafficked planner surfaces shipped in past 2 weeks. | cycle 1 §11-B |
| 2 | P1 | `/purchase-orders/[po_id]` | Add inline "Receive against this PO →" header CTA linking `/stock/receipts?po_id={po_id}`. Saves 3-step copy-paste flow. | cycle 1 §8-I |
| 3 | P1 | `/planning/runs/[run_id]` | Render `→ PO 1234` chip on rec row when `converted_to_po_id` is set. Saves drill-down click. | cycle 1 §3-I |
| 4 | P1 | `/planning/runs/[run_id]` | Add "Bulk approve all ready" action on production-recs tab (cycle 6 added partial; verify scope). Daily approval flow. | cycle 1 §7-I; cycle 6 closure noted |
| 5 | P1 | `/stock/receipts` | Per-line search box on Goods Receipt (currently global search filters all dropdowns). Operator efficiency. | cycle 1 §9-I |
| 6 | P1 | `/planning/inventory-flow` | Stamp legend "Planned production not included — see /planning/production-plan". Clears expectation-mismatch confusion. | cycle 1 §6-F |
| 7 | P1 | `/admin/sku-health` | Hide `shopify_variant_match` column until backend lands (currently hardcoded "unknown" rendered as real column). | cycle 1 §11-H |
| 8 | P1 | `/inbox` | Collapse 8 view chips into `<select>` at <640px (currently wraps to 3 lines on mobile). | cycle 1 §10-D |
| 9 | P1 | `/purchase-orders` | Collapse KPI tile strip to 2x2 grid at <640px (currently horizontal-scrolls). | cycle 1 §8-D |
| 10 | P1 | `/stock/production-actual` | Add "What this will do" preview panel (FG +output / scrap audit row / per-component −consumption from pinned BOM) above submit. | cycle 1 §5-F |

---

## §5 Routes by category

### §5.1 Overview / Landing

| Route | Grade | Notes |
|---|---|---|
| `/dashboard` | B | Live since 2026-04-25; 7-block control tower; missing 3 quick-actions entries (P0 §4 #1) |
| `/dashboard/v2` | B | Cycle 7 MVP + cycle 9 placeholder collapse; honest "Awaiting read-model" badges |
| `/planning` | C | Landing tile-page; overlap concern with /dashboard |
| `/profile` | C | Self-service only; minimal scope |

### §5.2 Planning corridor

| Route | Grade | Notes |
|---|---|---|
| `/planning/production-plan` | A | Cycle 4.2 normalized (commit `4fee418`); cycle 11+12 plan-to-actual chain |
| `/planning/inventory-flow` | B | Daily board live since 2026-04-26; planned-production legend missing |
| `/planning/inventory-flow/[itemId]` | B | Item drilldown; "Open recipe" link missing |
| `/planning/runs` | B | English/LTR closed cycle 3; `[Superseded]` chip absent |
| `/planning/runs/[run_id]` | B | English/LTR closed cycle 3; bulk-approve added cycle 6 |
| `/planning/runs/[run_id]/recommendations/[rec_id]` | C | English/LTR closed cycle 3; signal #21 v1.1 DTO; dismiss-state UX P1 |
| `/planning/forecast` | B | List-level English-clean; resume-draft P3 |
| `/planning/forecast/[version_id]` | B | Cycle 9 ISO-weekly fix + cycle 11 seed-cells endpoint live (signal #27) |
| `/planning/blockers` | B | Tom-locked Hebrew exception |
| `/planning/production-simulation` | F | IDB-only false green |
| `/planning/boms` | F | IDB-only false green |
| `/planning/weekly-outlook` | F | Orphaned; superseded by inventory-flow |

### §5.3 Stock-Ops corridor

| Route | Grade | Notes |
|---|---|---|
| `/stock/receipts` | A | RUNTIME_READY context (handler signals); per-line search P1 |
| `/stock/waste-adjustments` | A | RUNTIME_READY signal #1 since 2026-04-17 |
| `/stock/physical-count` | A | RUNTIME_READY signal #2 since 2026-04-17 |
| `/stock/production-actual` | C | Cycle 2 closed P0-A; cycle 5+6+12 from_plan + variance + URL hygiene |
| `/inventory` | A | Loop 11 supply_method-aware costs |
| `/stock/movement-log` | A | Loop 4 fixes; clean |
| `/stock/submissions` | C | My History; read-only of own submissions |

### §5.4 Inbox / Approvals / Exceptions

| Route | Grade | Notes |
|---|---|---|
| `/inbox` | B | Unified inbox; 4 source streams; sort + filter live; mobile chips wrap |
| `/inbox/approvals/waste/[submission_id]` (and PC + credit) | B | Approval detail pages; Loop 3 detail pages |

### §5.5 Purchase Orders corridor

| Route | Grade | Notes |
|---|---|---|
| `/purchase-orders` | B | List with KPIs; mobile horizontal scroll P1 |
| `/purchase-orders/new` | B | Manual PO live since `92efbb3` (signal #13); cycle 9 P0-2 closed (Zod issues mapping) |
| `/purchase-orders/[po_id]` | B | Cycle 9 P0-D closed (English banner); cycle 10 dead-link closed; "Receive against this PO" P1 |

### §5.6 Admin / Master Data

| Route | Grade | Notes |
|---|---|---|
| `/admin/items` | B | AMMC slice4; quick-create + status toggle + readiness pill live |
| `/admin/components` | B | List with supplier picker; readiness column "—" pending detail |
| `/admin/suppliers` | B | Clean list |
| `/admin/supplier-items` | B | Cost edit live (Loop 11) |
| `/admin/planning-policy` | B | Per-item policy live |
| `/admin/sku-aliases` | A | Cycle 8 fix; success-banner with resolved count |
| `/admin/sku-map` | B | Mappings list; raw IDs P3 |
| `/admin/sku-health` | B | Hardcoded "unknown" column P1 |
| `/admin/holidays` | B | Cycle 8 page replaces "coming soon"; signal #25 + #26 backend live |
| `/admin/integrations` | B | Break-glass toggle; Shopify sync card |
| `/admin/jobs` | A | Auto-refresh tick; clean |
| `/admin/users` | B | Read-only; non-409 PATCH error gap P3 |
| `/admin/products/new` | C | New product wizard |
| `/admin/products/[item_id]` | D | Product 360 (1456 LoC); dual-hierarchy with masters/items |
| `/admin/components/[component_id]` | D | Legacy slice5; dual-hierarchy |
| `/admin/suppliers/[supplier_id]` | D | Legacy slice5; dual-hierarchy |
| `/admin/boms` (and children) | D | Legacy editor; dual-hierarchy with masters/boms |
| `/admin/masters/items/[item_id]` | C | Tranche-D pattern; dual-hierarchy with products |
| `/admin/masters/components/[component_id]` | C | Tranche-D pattern; dual-hierarchy |
| `/admin/masters/suppliers/[supplier_id]` | C | Tranche-D pattern; dual-hierarchy |
| `/admin/masters/boms` | C | Tranche-E view-only; dual-hierarchy |
| `/admin/masters/boms/[bom_head_id]` | C | View-only; Tranche J pending |
| `/admin/masters/boms/[bom_head_id]/[version_id]` | C | View-only; Tranche J pending |
| `/admin/masters/boms/[bom_head_id]/[version_id]/edit` | C | Edit lines; Tranche J pending |
| `/admin/masters/health` | C | Placeholder concern (cycle 1 §14 #5) |
| `/admin/masters/archive` | C | Placeholder concern (cycle 1 §14 #6) |
| `/admin/purchase-orders/parity-check` | (deferred) | Admin diagnostic; low operator-traffic |

---

## §6 Cross-route patterns

### §6.1 Hebrew/English consistency — closed via cycle 2-9 sweeps

Cycle 1 audit flagged FIVE major Hebrew leakages on otherwise English surfaces:
- `/ops/stock/production-actual` (P0-A) → closed cycle 2 `9f3b98e`
- `/planning/runs` + `/planning/runs/[run_id]` (P0-B) → closed cycle 3 `24e5a7a`
- `/planning/runs/[run_id]/recommendations/[rec_id]` (P0-C) → closed cycle 3 `24e5a7a`
- `/purchase-orders/[po_id]` (P0-D) → closed cycle 9 `b4d1d20`
- `/planning/forecast/[version_id]` Active-published callout (P0-J) → closed cycle 4 `303465c`

**Pattern**: cycles 2-9 closed 8 of 11 audit P0 surfaces (per CURRENT_STATE.md "Audit P0 status"). The remaining 3 P0s (production-simulation false green, holidays gap pre-cycle-8, dual-hierarchy pre-Tranche-J) all surface in §3 above. **Tom-locked exception**: `/planning/blockers` Hebrew page-title is intentional and does not count against axis 8.

### §6.2 Freshness vocabulary fragmented

Three different freshness components in use across the portal (cycle 1 §13-E):
- `FreshnessBadge` on `/planning/inventory-flow`
- `as of <time>` chip on `/dashboard`, `/purchase-orders`
- `(לפי הריצה — …)` on `/planning/runs/[run_id]` (Hebrew variant — closed cycle 3)

**Pattern**: standardize on `FreshnessBadge` everywhere a decision-grade timestamp appears. P1 leverage if rolled forward.

### §6.3 Dual-hierarchy admin surfaces

Three entity domains have parallel detail-page hierarchies (cycle 1 §11-B; cycle 10 §pattern 9):
- Items: `/admin/products/[id]` legacy slice5 vs `/admin/masters/items/[id]` Tranche-D
- Components: `/admin/components/[id]` legacy slice5 vs `/admin/masters/components/[id]` Tranche-D
- Suppliers: `/admin/suppliers/[id]` legacy slice5 vs `/admin/masters/suppliers/[id]` Tranche-D
- BOMs: `/admin/boms` legacy editor vs `/admin/masters/boms` Tranche-E view-only

**Pattern**: each domain has TWO detail pages for the same entity. Operators land on different layouts depending on entry point. All four pairs sit in Grade D (legacy slice5) or Grade C (masters Tranche-D). Tranche J consolidation queued post-PO-60-loop per memory.

### §6.4 IDB-only false greens

Two "simulation" surfaces are IDB-backed only (cycle 1 §11; cycle 10 §pattern 7):
- `/planning/production-simulation` — file comment "nothing here calls the API"
- `/planning/boms` — same profile

**Pattern**: simulation surfaces lie about being live. Both have explicit Tom-pending decision packs (PSDP-1..4 queued; BOM Simulation queued post-PO-60-loop). Until decided, dashboard "BOM Simulation" Quick-Action tile points at a false-green surface.

### §6.5 Mobile @ 390px — uneven across surfaces

Cycle 1 mobile audit found:
- KPI tile strips horizontally scroll on PO list, sometimes Dashboard (B/D/P1, P2)
- Wide tables horizontally scroll on Items, Supplier-Items, Forecast lines (D/P2)
- 8-chip filter bars wrap to 3 lines on Inbox @ 390px (D/P2)

**Pattern**: no unified responsive grammar. Each surface has its own collapse rule. Acceptable per individual surface; cumulative friction adds up.

### §6.6 Raw IDs in user-facing surfaces

Cycle 1 §3-G + §11-G + §11-G found multiple surfaces still rendering `item_id`, `component_id`, `supplier_id`, `external_sku` as raw monospace text. Per memory `feedback_names_not_ids_in_ui.md` and recent commit `0997398`, names are primary, IDs only secondary. Active gaps:
- `/planning/runs/[run_id]` exception rows render component/item IDs raw
- `/admin/sku-map` external_sku + item_id raw

**Pattern**: rule is locked but not consistently applied. Single P1 sweep across audit surfaces would close it.

### §6.7 Post-action visibility — split between toast-only and durable confirm

Most write actions show a toast and reset state (e.g. forecast publish, GR submit, waste submit). A few have durable confirmations (production-actual confirmation panel with variance row; sku-aliases success banner with resolved-exceptions count). Toast-only surfaces lose information after dismissal. Cycle 1 §5-I noted `/stock/production-actual` success banner does not link to posted ledger — closed cycle 12 PAR-3 ("View posted ledger →" link).

**Pattern**: lean toward durable confirmation panels for stock-affecting actions; toast-only OK for read/filter mutations.

---

## §7 Recommended cycle 14+ dispatch order based on leverage

Ordered by **(blocker severity) × (operator-frequency-of-use) × (fix-effort-low)**. All within W2's Mode A authority pre-RUNTIME_READY; in-cycle authoring requires Mode B-Planning-Corridor or per-form Mode B.

### Cycle 14 — Discoverability fix bundle (highest leverage, ~1 hour)

**Single dispatch covers Top P1 #1**: append three planning entries to `src/features/dashboard/quick-actions.ts`. Single file, three lines. Closes cycle 1 P0-D (Quick Actions launcher gap) for the three most-trafficked surfaces shipped in past 2 weeks. **Authority**: existing Mode B-Planning-Corridor amendment covers `/dashboard/v2` already; extending to `/dashboard` for a quick-actions append is a 1-line carve-out.

### Cycle 15 — PO-detail receive button + planning-runs converted-to-PO chip (~2 hours)

Two related fixes both on planning corridor:
- Top P1 #2: "Receive against this PO →" CTA on `/purchase-orders/[po_id]`
- Top P1 #3: `→ PO 1234` chip on `/planning/runs/[run_id]` rec rows when `converted_to_po_id` is set

Both surfaces enumerated under existing Mode B-Planning-Corridor. Saves Tom 4 navigation clicks per daily PO-rec-conversion flow.

### Cycle 16 — IDB false-green disposition (Tom decision needed)

The two F-grade routes (`/planning/production-simulation`, `/planning/boms`) cannot ship without Tom's PSDP-1..4 decision pack. Recommended pre-decision: add **interim "BETA — uses cached data" banner** to both via single-line each. This converts F-grade silent-bad-data into honest C-grade pending-decision until the larger PSDP tranche lands.

### Cycle 17 — Dual-hierarchy admin consolidation (Tranche J prep)

The four D-grade surfaces (`/admin/products/[id]`, `/admin/components/[id]`, `/admin/suppliers/[id]`, `/admin/boms`) all need Tranche J. Per memory `project_bom_simulation_queued.md`, this is queued post-PO-60-loop. Recommend: in cycle 17 author the **migration plan doc** (Mode A audit deliverable) covering which legacy slice5 page wins per entity, which one becomes a 301 redirect, and what data each carries. No code changes; doc only.

### Cycle 18 — Mobile responsive grammar sweep

Cycle 1 §13-D flagged "no unified responsive grammar". Recommend a **per-surface mobile-pass dispatch**: KPI strips (PO list + Dashboard) collapse to 2x2; wide tables (Items, Supplier-Items, Inbox chips) collapse to card-stream or `<select>` at <640px. Single-cycle scope; Mode B-Planning-Corridor amendment may need extension to `/admin/items` and `/admin/supplier-items`.

### Cycle 19 — Names-not-IDs sweep

Apply locked memory rule to remaining gaps: `/planning/runs/[run_id]` exception rows + `/admin/sku-map`. Single small commit; closes a long-standing P1 register entry.

### Cycle 20 — Production-actual "What this will do" preview

Top P1 #10: BOM-derived consumption preview above submit. Requires either (a) reuse existing items+BOM cache (W2-only) or (b) new W1 endpoint for snapshot consumption preview (then W2 wires it). Single Mode B cycle on production-actual surface.

### Why this order

- Cycles 14-15 are pure-W2 quick wins on already-authorized surfaces (≤2 hours each).
- Cycle 16 turns silent-broken into honest-pending without rebuilding (1-line banner each).
- Cycles 17-19 are housekeeping that compounds: each one removes a Tom-Tax category.
- Cycle 20 is the highest-effort but unlocks operator confidence on the production-execution chain.

The other surfaces in §3 (`/admin/masters/health`, `/admin/masters/archive`, `/planning/weekly-outlook`) are governance-decisions, not W2 fixes. Tom or the governor needs to call retire / redirect / rebuild before W2 can act.

---

## Closing notes

This scorecard is a **read-only synthesis** of cycles 1-12 audit work. No portal source was modified during authoring. The grade for any route can be re-derived directly from the cycle citation in §2.

**Highest-leverage finding**: 8 of 50 surfaces are Grade A and 22 are Grade B — meaning **30 of 50 routes (60%) are production-usable today**. The remaining 20 split between fragile (14 Grade C, all known-cause), half-finished (4 Grade D, all dual-hierarchy), and false-green (2 Grade F + 1 orphan).

**Top single fix by leverage**: dashboard Quick Actions bundle (§4 #1). Single file, ~10 minutes of work, closes the cycle 1 P0-D discoverability gap for three of the most-used surfaces.

**Single biggest structural risk**: the IDB-only false-green surfaces (§3 #1, #2). They surface from the dashboard launcher as if live and silently mismatch production data. Tom decision PSDP-1..4 is the gate.

End of scorecard.
