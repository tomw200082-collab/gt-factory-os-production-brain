# Historical state snapshot — Ralph Loop corridor RE-AUDIT (2026-04-25)

> **Origin:** migrated verbatim from `CURRENT_STATE.md` §"Ralph Loop corridor status (2026-04-25 — RE-AUDIT COMPLETE)" during Phase 8 Run F Wave 4 Hole 2 cleanup (2026-05-09). The corresponding section in CURRENT_STATE.md was removed; this snapshot is the audit-trail preservation.
>
> **Type:** historical state snapshot. Not authoritative on current state. For current corridor status, read `CURRENT_STATE.md` §Active corridor and `ACTIVE_NOW.md`.
>
> **Date:** 2026-04-25.

---

## Ralph Loop corridor status (2026-04-25 — RE-AUDIT COMPLETE)

**Portal main tip (at audit time):** `92efbb3` (2026-04-26 — merge of feature/master-data-ux-overhaul into main; brings manual PO creation portal `/purchase-orders/new` live on Vercel; nav conflict resolved with main's Inventory Flow state). Portal deployed to Vercel automatically on push.

**Backend Railway tip (at audit time):** `1209596` (deployed 2026-04-27 as Railway deployment `ef03b588-5da9-4e8a-909d-b081b65746a9`; adds Tranche 3 blockers endpoint on top of Tranche 2 rec-detail + Tranche 1a time-aware PO netting). `GET /health → {"ok":true}` confirmed; `GET /api/v1/queries/planning/blockers` HTTP 401 without auth confirmed; HTTP 200 with real Supabase JWT confirmed 2026-04-27.

**Re-audit findings (2026-04-25):**
- All exception deep links (`resolveExceptionDeepLink()`) verified to route to real pages: `/admin/sku-aliases`, `/admin/integrations`, `/purchase-orders`, `/admin/sku-map` all exist and are API-wired.
- Tom Tax: all 5 daily operations (open POs, GR, FG shortage projection, exceptions inbox, production actual) doable from portal without SQL. CLEAN.
- Gap found + fixed: `/planning/weekly-outlook` was missing from sidebar nav manifest. Added (`81d6c7f`).
- Admin screens: all 9 screens (items, components, boms, suppliers, supplier-items, planning-policy, sku-aliases, sku-map, jobs, integrations) are API-wired with real fetch calls. No mock data.
- Cross-corridor: PO data feeds weekly outlook via `purchase_order_lines.item_id` FK (FG BOUGHT_FINISHED items only); A4 locked (engine uses zero FG inbound; PO is informational overlay only). No regression.
- Production actual uses BOM pinned version at snapshot time; weekly outlook uses planning run data. No overlap or conflict.

**Completed corridors (post-Gate-5 hardening + re-audit) at the time of the snapshot:**

| Corridor | Status | Portal tip | Backend evidence |
|----------|--------|------------|-----------------|
| PO | CLOSED | d73199b | migrations 0049-0057, 0082, 0083, 0084; 58+pgTAP; 14/14 node:test |
| Production Execution | CLOSED | bd93ec4 | 13/13 backend tests; form live-wired; 7 E2E specs |
| Calendar / Gantt | DONE | f4aca4f + dfd2c6b (portal main) / 9ae6683 (backend main) | `/planning/inventory-flow` daily control tower live on Vercel (redirects weekly-outlook); backend-db handler stack `api/src/inventory/handler.flow.ts` deployed Railway; sidebar nav entry "Inventory Flow" |
| PurchaseOrders-manual portal | DONE (feature/master-data-ux-overhaul — pending merge to main) | 47de463 | backend-db migrations 0093-0096 on gt-factory-os/main; backend node:test 12/12; portal: /purchase-orders/new, source column, detail banner |
| Planning Tranche 1 + Tranche 2 portal | DONE | backend `4b0f5eb` (gt-factory-os/main); portal `2146b84` (window2-portal-sandbox/main) | backend-db: E1/E2/E6/E5 fixed + time-aware PO netting (migrations 0101–0110); rec-detail endpoint 9/9 node:test; RUNTIME_READY(Planning-Tranche1) + RUNTIME_READY(Planning-Tranche2-RecommendationDetail) emitted 2026-04-26. portal: RecommendationDrillDown surface (Hebrew labels, mobile cards, 9 files) PASS — HTTP 200 against live endpoint verified 2026-04-26. |
| Planning Tranche 3 — Unresolved Demand / Blockers | DONE (2026-04-27) | backend `1209596` (gt-factory-os/main); portal `e7dce27` (window2-portal-sandbox/main) | backend-db: `GET /api/v1/queries/planning/blockers` — 12/12 node:test against live pooled PG17; deployed Railway `ef03b588`; HTTP 401 without auth + HTTP 200 with JWT both confirmed; PBR-1/2/3/4 all resolved (PBR-1 Tom-locked total horizon + urgency fields; PBR-4 backend-db-resolved 95% via live DB inspection — two live shapes normalized via display_id/display_name/display_kind). portal: 13 files / 1446 insertions; route `/planning/blockers` (Tom-locked); page title "חסמים בתכנון"; Hebrew label maps exhaustive Tom-locked verbatim; validation 3/3 PASS (tsc/build/lint:urls); Vercel 307→/login confirmed live. RUNTIME_READY(Planning-Tranche3-Blockers) emitted as signal #17. Manual-PO sync-closure follow-on now unblocked. |
| External Boundaries | DONE | be57fb0 | exception deep links; "Fix this →" button; 17-category explanations |
| Exceptions / Control Tower | DONE | be57fb0 | dashboard 7/7 blocks live; inline Acknowledge/Resolve actions |
| Admin Self-Sufficiency | DONE | be57fb0 | all admin screens real-API-wired |
