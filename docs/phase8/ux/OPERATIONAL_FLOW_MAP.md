# Operational Flow Map — GT Factory OS Portal

**Owner agent:** `ux-flow-architect`
**Authoritative status:** DRAFT — surfaces and signals accurate as of 2026-05-08.
**Update rule:** Updated whenever a new RUNTIME_READY signal is emitted or a new portal route lands.
**Release-gate relevance:** New route must appear in this map before /ux-release-gate may audit it.

---

## What belongs here

- Map of every portal surface to its operational workflow, RUNTIME_READY signal, and flow stage.
- Entry/exit conditions for each surface.
- Known flow gaps (ARCH_REQUIRED escalations).

## What must never go here

- Source code or implementation details.
- DB schema or migration specifics.
- Backend contract content (those live in gt-factory-os/docs/contracts/).

---

## Surface map (as of 2026-05-08)

### Operations surfaces (`/(ops)/`)

| Route | Workflow | RUNTIME_READY signal | Flow stage | UX status |
|---|---|---|---|---|
| `/(ops)/goods-receipt` | Receive goods against PO or without PO | `GoodsReceipt-FromPO` (#35) | LANDED | NOT YET AUDITED |
| `/(ops)/waste-adjustment` | Post waste/scrap or positive adjustment | `WasteAdjustment` (#1) | LANDED | NOT YET AUDITED |
| `/(ops)/physical-count` | Blind count → submit → approve/auto-post | `PhysicalCount` (#2) | LANDED | NOT YET AUDITED |
| `/(ops)/production-actual` | File production report from plan or standalone | `ProductionActual` (#9), `ProductionActual-TwoHead` (#32) | LANDED | NOT YET AUDITED |

### Planning surfaces (`/planning/`)

| Route | Workflow | Signal | Flow stage | UX status |
|---|---|---|---|---|
| `/planning/production-plan` | View/manage daily production plan | `Planning-Tranche1` (#15) | LANDED | NOT YET AUDITED |
| `/planning/blockers` | View and resolve planning blockers | `Planning-Tranche3-Blockers` (#17) | LANDED | NOT YET AUDITED |
| `/planning/runs` | View planning run history | `PlanningRun` (#7) | LANDED | NOT YET AUDITED |
| `/planning/forecast` | Edit monthly forecast | `Forecast` (#4), `Forecast-Monthly` (#34) | LANDED | NOT YET AUDITED |
| `/planning/inventory-flow` | View inventory flow with planned overlay | `InventoryFlow` (#14), `InventoryFlowPlannedInflowEndpoint` (#33) | LANDED | NOT YET AUDITED |

### PO and procurement surfaces

| Route | Workflow | Signal | Flow stage | UX status |
|---|---|---|---|---|
| `/po` | List and manage purchase orders | `PurchaseOrders` (#8) | LANDED | NOT YET AUDITED |
| `/po/[id]` | PO detail view | `PurchaseOrders` (#8) | LANDED | NOT YET AUDITED |
| `/po/[id]/edit` | Edit/add lines to an open PO | `PurchaseOrders` (#8) | LANDED | NOT YET AUDITED |
| `/po/new` | Create manual PO | `PurchaseOrders-manual` (#13) | LANDED | NOT YET AUDITED |

### Dashboard

| Route | Workflow | Signal | Flow stage | UX status |
|---|---|---|---|---|
| `/dashboard` | Stock truth control tower | `DashboardCriticalToday` (#23), `DashboardSlippedPlans` (#24) | LANDED | NOT YET AUDITED |

---

## Operational flow stage definitions

| Stage | Meaning |
|-------|---------|
| `LANDED` | Backend contract complete; portal route exists; RUNTIME_READY signal emitted |
| `BACKEND_READY` | Backend done; portal not yet started |
| `PLANNED` | In backlog; no backend yet |
| `NOT_APPLICABLE` | Route does not have an operational workflow (admin/settings) |

---

## Known flow gaps (ARCH_REQUIRED escalations awaiting backend work)

| Gap ID | Surface | Description | Depends on |
|--------|---------|-------------|-----------|
| GAP-001 | `/(ops)/goods-receipt` | Partial receipt history not surfaced on GR form | Backend endpoint TBD |
| GAP-002 | `/planning/blockers` | No reversal path for a manually resolved blocker | Backend enum extension |
| GAP-003 | `/dashboard` | Exceptions Inbox link from critical-today card not yet wired | Portal routing |

---

## Priority audit order (recommended)

1. `/(ops)/goods-receipt` — highest operator frequency, most complex PO-link flow
2. `/(ops)/waste-adjustment` — earliest RUNTIME_READY; likely has drift
3. `/(ops)/physical-count` — count freeze semantics require careful flow audit
4. `/planning/blockers` — known Hebrew audit P0 findings
5. `/po/[id]/edit` — complex action surface (add lines, approve, close)
