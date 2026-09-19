# UX release gate — planning → production → procurement → receipt chain (2026-09-19)

> **Invocation:** manual `/ux-release-gate --scope <chain>` inside the planning-chain deep review (`docs/audits/2026-09-19-planning-chain-deep-review.md`).
> **Mode:** render-grade. Dev-shim auth (`NEXT_PUBLIC_ENABLE_DEV_SHIM_AUTH=true`), browser-stubbed APIs via `tests/e2e/ux-shot.spec.ts` + JSON fixtures transcribed from the committed `@mocked` specs. No `X-Fake-Session` / `X-Test-Session`. No portal source touched.
> **Write policy:** read-only gate. Saved here (default). After Tom approval → `gt-factory-os-portal/docs/ux/`.

## Scope

| Route | Role | Fixture | Desktop shot | Mobile shot |
|---|---|---|---|---|
| `/production` | operator | `production-today.json` (TANK planned · PACK planned · PACK done) | `/tmp/ux-shots/production-operator-desktop.png` | `…/production-operator-mobile.png` |
| `/production` (empty API) | operator | — | `…/production-empty-1-operator-desktop.png` | `…/production-empty-1-operator-mobile.png` |
| `/production/runs/RUN1` | operator | `production-run.json` (pick list, PLANNED) | `…/production-runs-RUN1-operator-desktop.png` | `…/production-runs-RUN1-operator-mobile.png` |
| `/production/runs/RUN1/report` | operator | `production-report.json` (IN_PRODUCTION, PACK) | `…/production-runs-RUN1-report-operator-desktop.png` | `…/production-runs-RUN1-report-operator-mobile.png` |
| `/stock/production-actual` (legacy) | operator | empty | `…/stock-production-actual-operator-desktop.png` | `…/stock-production-actual-operator-mobile.png` |
| `/stock/receipts` | operator | `receipts.json` (1 open PO expected today) | `…/stock-receipts-operator-desktop.png` | `…/stock-receipts-operator-mobile.png` |
| `/home` (Today board) | operator | `home.json` | `…/home-operator-desktop.png` | `…/home-operator-mobile.png` |
| `/planning/forecast` | planner | empty | `…/planning-forecast-planner-desktop.png` | `…/planning-forecast-planner-mobile.png` |
| `/planning/meeting` | planner | `meeting.json` | `…/planning-meeting-planner-desktop.png` | `…/planning-meeting-planner-mobile.png` |
| `/planning/production-plan` | planner | `production-plan.json` | `…/planning-production-plan-planner-desktop.png` | `…/planning-production-plan-planner-mobile.png` |
| `/planning/procurement` | planner | `procurement.json` (session, 3 POs) | `…/planning-procurement-planner-desktop.png` | `…/planning-procurement-planner-mobile.png` |
| `/purchase-orders/placement-queue` | planner | `placement-queue.json` | `…/purchase-orders-placement-queue-planner-desktop.png` | `…/purchase-orders-placement-queue-planner-mobile.png` |

Empty-API variants were also rendered for `/production/runs/RUN1`, `/production/runs/RUN1/report`, `/stock/receipts`, `/planning/procurement` (`*-empty-1-*`). Fixtures live in `/tmp/ux-fixtures/` (session-scoped; regenerate from the specs named in each file's header).

**Audit lens (from the deep review):** production has not been reported since 2026-09-07 (15 finished goods negative, Shopify shows them sold out); the last purchase session was 2026-08-23; September receipts are mostly PO-less. The gate therefore weighs the operator end-of-day report path and the door receipt path above everything else.

