# Route Builder Integration Plan — gt-factory-os Monorepo + Cloud Deployment

**Owner:** Tom (sole approver)
**Authored by:** AI brain governance routing
**Date:** 2026-05-08
**Status:** PROPOSAL — awaiting Tom approval before any execution dispatch
**Authority weight:** advisory. Does not override `CLAUDE.md`, `EXECUTION_POLICY.md`, `CURRENT_STATE.md`, or any locked decision. Does not authorize backend code change. Implementation requires per-phase dispatch.

---

## 0 — Why this document exists

Tom built a **route-builder Tranche 0 foundation** at `c:\Users\tomw2\Projects\.archive-route-builder-2026-05-06\` (currently archived, .archive-prefixed). The goal is to:

1. Resurrect and integrate it into `gt-factory-os` monorepo.
2. Deploy it to the cloud (Railway endpoint + GitHub Actions trigger).
3. Make it triggerable from mobile (GitHub Actions `workflow_dispatch`) so Tom can run it on Saturday morning to plan Sunday's route — even when his computer is off.

This document is the integration plan. It does not implement anything. No code changed. No migration applied. No deploy.

---

## 1 — Honest current-state assessment of Tranche 0

### What the foundation actually contains (verified 2026-05-08)

| Component | File | Status |
|---|---|---|
| Domain types | `src/core/domain.ts` | ✅ complete — `LwOrder`, `OrderDecision`, `RunPlan`, `AllocationSnapshotRow`, `AgentException` all defined |
| Status enums | `src/core/status.ts` | ✅ complete — `DeliveryArea`, `WorkdayCode`, `OrderDecisionStatus`, `LineStatus`, `ExceptionType`, `FreshnessConfidence`, `StockSource` |
| Area rules | `src/core/area-rules.ts` | ✅ complete — workday→area map, Israel TZ weekday detection, `AreaRuleViolation` exception class |
| Priority logic | `src/core/priority.ts` | ✅ complete — `computeOrderSize`, `compareForPriority`, `rankOrders` |
| Test fixtures | `fixtures/lionwheel/orders-2026-05-07-center.json` | ✅ 3 synthetic CENTER orders |
| DB infra | `src/persistence/db.ts` | ✅ SQLite migrations runner (Postgres-portable) |
| CLI scaffold | `src/cli/index.ts`, `src/cli/commands/migrate.ts` | ✅ `route-build migrate` works |
| Tests | `tests/core/area-rules.spec.ts`, `tests/core/priority.spec.ts` | ✅ pass under vitest |

### What is NOT built yet (the actual route-building engine)

| Missing component | What it would do |
|---|---|
| **Stock allocation engine** | For each ranked order, deducts required quantity from `available_to_allocate`. Determines `AVAILABLE` / `SHORT` / `STALE_STOCK` / `UNKNOWN_SKU` per line. Maintains running allocation snapshot. |
| **Decision engine** | Combines stock allocation result + area rules + priority + customer notes → `OrderDecisionStatus` per order. Produces `RunPlan`. |
| **LionWheel orders source** | Currently fixture-based. Needs to read live LionWheel orders. **Recommended:** use existing `orders_mirror` table (already populated by `lionwheel-poll-cron` every 15 min). No new external API call needed. |
| **Stock source** | Currently fixture-based. Needs to read from `gt-factory-os` Postgres — `balance_anchors` + projection table for FG items. |
| **Postgres persistence** | Currently SQLite. Needs schema change to fit existing `gt-factory-os` Postgres patterns (snake_case, `timestamptz`, FK to `app_users`). |
| **CLI build command** | `route-build build --target-date 2026-05-10` — runs the full pipeline against a target date. |
| **API endpoint** | `POST /api/v1/internal/jobs/route-build` — Fastify route, bearer-auth-protected, returns RunPlan as JSON. |
| **GitHub Actions workflow** | Cron + workflow_dispatch trigger for cloud execution. |

### Implication

**"סוכן שלם וחכם" is overstated for current state.** Foundation is excellent (tested types + area rules + priority), but the actual decision-making code does not exist yet. This plan is not just "wire it up to cloud" — it's "finish building the agent + wire it to cloud."

Estimated work: **5 phases, each 1–3 hours of focused executor work** (not counting Tom review time).

---

## 2 — Architecture (cloud-deployable end state)

```
┌─────────────────────────────────────────────────────────────┐
│  Tom's mobile (GitHub mobile app)                           │
│  → Actions tab → route-build-cron → "Run workflow" button   │
└─────────────────────┬───────────────────────────────────────┘
                      │ workflow_dispatch (target_weekday param)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  GitHub Actions runner (free tier, ubuntu-latest)           │
│  - reads ROUTE_BUILD_SHARED_SECRET from repo secrets        │
│  - curl POST to Railway API endpoint                        │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTPS bearer-authed POST
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  Railway: gt-factory-os-api (existing service)              │
│  POST /api/v1/internal/jobs/route-build                     │
│  Handler: api/src/routes/internal/route-build.ts            │
│   1. Read open orders from `orders_mirror` (LionWheel)      │
│   2. Read FG stock from `balance_anchors` + projections     │
│   3. Run agent: areaRules + priority + allocation + decide  │
│   4. Persist RunPlan to `route_runs` + children             │
│   5. Optional: Telegram alert (memory: bot planned)         │
│   6. Return JSON RunPlan                                    │
└─────────────────────┬───────────────────────────────────────┘
                      │ writes to existing Postgres
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  Supabase Postgres (existing)                               │
│  NEW tables: route_runs, route_decisions, route_exceptions  │
│  EXISTING tables read: orders_mirror, balance_anchors,      │
│                         items, item_aliases, stock_ledger   │
└─────────────────────────────────────────────────────────────┘
```

### Key architectural decisions

1. **Read-only against LionWheel in v1.** Agent produces RunPlan but does NOT push assignments back to LionWheel. v1 keeps `LIONWHEEL_FG_OUT_BRIDGE_ENABLED=false` and does not interact with frozen flags. v2 (later, separate Tom approval) adds write-back.

2. **No new external API calls.** Uses `orders_mirror` (already kept fresh by `lionwheel-poll-cron` every 15 min). No new LionWheel credentials needed. No new rate-limit risk.

3. **Stock source = `balance_anchors` + projections.** Per CLAUDE.md locked decisions, `balance_anchors` + ledger projection is the authoritative current-stock view. Same source `inventory-flow` portal screen reads.

4. **Postgres-only.** Drop SQLite from Tranche 0. The Postgres-portable comment in `db.ts` already anticipates this.

5. **Idempotency.** `route_runs.run_id` (UUID) is generated server-side. Re-running with same `target_date` produces a new run_id (audit trail), does NOT mutate prior runs.

---

## 3 — Schema additions (3 new tables)

### Migration: `00XX_route_runs.sql` (number TBD by backend-db-executor)

```sql
-- Route-builder agent runs
CREATE TABLE route_runs (
  run_id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  run_at              timestamptz NOT NULL DEFAULT now(),
  target_date         date NOT NULL,
  target_weekday      text NOT NULL CHECK (target_weekday IN ('SUN','MON','TUE','WED','THU')),
  target_area         text NOT NULL CHECK (target_area IN ('CENTER','NORTH','SOUTH')),
  driver_name         text NOT NULL,
  freshness_threshold_hours integer NOT NULL DEFAULT 24,
  triggered_by        text NOT NULL CHECK (triggered_by IN ('cron','manual','dispatch','test')),
  triggered_by_user   uuid NULL REFERENCES app_users(id),
  status              text NOT NULL DEFAULT 'DRAFT' CHECK (status IN ('DRAFT','REVIEWED','APPROVED','APPLIED','FAILED')),
  orders_checked      integer NOT NULL DEFAULT 0,
  approved_orders     integer NOT NULL DEFAULT 0,
  pending_orders      integer NOT NULL DEFAULT 0,
  blocked_orders      integer NOT NULL DEFAULT 0,
  exceptions_count    integer NOT NULL DEFAULT 0,
  raw_run_plan_json   jsonb NULL,  -- full RunPlan for audit
  notes               text NULL
);

CREATE INDEX route_runs_target_date_idx ON route_runs (target_date DESC);
CREATE INDEX route_runs_run_at_idx ON route_runs (run_at DESC);

-- Per-order decisions
CREATE TABLE route_decisions (
  decision_id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id              uuid NOT NULL REFERENCES route_runs(run_id) ON DELETE CASCADE,
  lw_order_id         text NOT NULL,
  customer_name       text NOT NULL,
  delivery_address    text NOT NULL,
  order_size          integer NOT NULL,
  decision_status     text NOT NULL CHECK (decision_status IN (
    'APPROVED_FOR_ROUTE','PENDING_APPROVAL_PARTIAL_STOCK','BLOCKED_NO_STOCK',
    'BLOCKED_SKU_MAPPING','BLOCKED_ROUTE_RULE','ALREADY_ASSIGNED','HUMAN_REVIEW_REQUIRED'
  )),
  priority_rank       integer NOT NULL,
  decision_reason     text NOT NULL,
  requires_tom_approval boolean NOT NULL DEFAULT false,
  was_applied_to_lionwheel boolean NOT NULL DEFAULT false,
  lines_json          jsonb NOT NULL,  -- LineCheck[]
  UNIQUE (run_id, lw_order_id)
);

CREATE INDEX route_decisions_run_id_idx ON route_decisions (run_id);
CREATE INDEX route_decisions_lw_order_id_idx ON route_decisions (lw_order_id);

-- Per-run exceptions
CREATE TABLE route_exceptions (
  exception_id        uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id              uuid NOT NULL REFERENCES route_runs(run_id) ON DELETE CASCADE,
  severity            text NOT NULL CHECK (severity IN ('INFO','WARN','CRITICAL')),
  exception_type      text NOT NULL,
  entity_type         text NOT NULL CHECK (entity_type IN ('ORDER','LINE','SKU','RUN')),
  entity_id           text NOT NULL,
  human_message_he    text NOT NULL,
  recommended_action_he text NOT NULL,
  resolved_at         timestamptz NULL,
  resolved_by         uuid NULL REFERENCES app_users(id)
);

CREATE INDEX route_exceptions_run_id_idx ON route_exceptions (run_id);
CREATE INDEX route_exceptions_unresolved_idx ON route_exceptions (run_id) WHERE resolved_at IS NULL;
```

### Schema review notes

- All tables additive only; no changes to existing tables.
- FK to existing `app_users(id)` for audit trail.
- `lw_order_id` is NOT a FK to `orders_mirror` — orders may be deleted/reissued in LionWheel; we keep the historical decision record regardless.
- `raw_run_plan_json` stores the full RunPlan as JSONB for reproducibility / audit / replay.
- `decision_status` enum exactly matches `OrderDecisionStatus` from Tranche 0 `domain.ts`.
- `exception_type` not constrained — Tranche 0 may add new types over time; emit-and-log new values.

---

## 4 — API contract

### `POST /api/v1/internal/jobs/route-build`

**Auth:** Bearer `ROUTE_BUILD_SHARED_SECRET` (new repo secret + Railway env var).

**Request:**
```typescript
{
  target_date: string,        // ISO date "2026-05-10" (Sunday)
  triggered_by: "cron" | "manual" | "dispatch" | "test",
  driver_name?: string,       // override default "Maksim"
  freshness_threshold_hours?: number  // override default 24
}
```

**Response 200:**
```typescript
{
  run_id: string,             // UUID
  status: "DRAFT",
  summary: {
    orders_checked: number,
    approved_orders: number,
    pending_orders: number,
    blocked_orders: number,
    exceptions_count: number
  },
  target: { date: string, weekday: string, area: string },
  decisions: OrderDecision[], // see domain.ts (allocates snapshot embedded)
  exceptions: AgentException[]
}
```

**Response 400:** target_date is FRI or SAT → `AreaRuleViolation`. Returned as JSON not thrown:
```json
{ "error": "AREA_RULE_VIOLATION", "weekday": "SAT", "message": "..." }
```

**Response 401:** missing/bad bearer.

**Response 503:** `ROUTE_BUILD_SHARED_SECRET` unset on API side.

**Response 5xx:** unexpected error (Railway logs visible in dashboard).

---

## 5 — GitHub Actions workflow

### File: `gt-factory-os/.github/workflows/route-build-cron.yml`

```yaml
name: route-build-cron

# Builds tomorrow's GT delivery route. Triggerable manually from mobile via
# GitHub Actions UI ("Run workflow" → choose target_weekday → Run).
#
# Cron: every Saturday 03:00 UTC (= 06:00 Israel) builds Sunday's route
# automatically. Output stored in route_runs table; JSON returned in workflow log.

on:
  workflow_dispatch:
    inputs:
      target_date:
        description: "Target delivery date (YYYY-MM-DD)"
        required: true
        type: string
      driver_name:
        description: "Driver override (default: Maksim)"
        required: false
        type: string
        default: ""
  schedule:
    # Saturday 03:00 UTC = Saturday 06:00 Asia/Jerusalem
    # Builds Sunday's route automatically.
    - cron: "0 3 * * 6"

concurrency:
  group: route-build-cron
  cancel-in-progress: false

jobs:
  build-route:
    name: build daily route
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - name: compute target_date for cron run
        id: target
        run: |
          if [ -n "${{ inputs.target_date }}" ]; then
            echo "date=${{ inputs.target_date }}" >> "$GITHUB_OUTPUT"
            echo "trigger=dispatch" >> "$GITHUB_OUTPUT"
          else
            # Cron run — target = tomorrow (Sunday)
            tomorrow=$(date -u -d "tomorrow" +%Y-%m-%d)
            echo "date=${tomorrow}" >> "$GITHUB_OUTPUT"
            echo "trigger=cron" >> "$GITHUB_OUTPUT"
          fi

      - name: invoke route-build endpoint
        env:
          API_URL: https://gt-factory-os-api-production.up.railway.app
          SECRET: ${{ secrets.ROUTE_BUILD_SHARED_SECRET }}
          TARGET_DATE: ${{ steps.target.outputs.date }}
          TRIGGER: ${{ steps.target.outputs.trigger }}
          DRIVER: ${{ inputs.driver_name }}
        run: |
          set -euo pipefail
          if [ -z "${SECRET:-}" ]; then
            echo "::error::ROUTE_BUILD_SHARED_SECRET secret not set"
            exit 1
          fi

          # Build request body
          if [ -n "${DRIVER}" ]; then
            body=$(jq -n --arg d "${TARGET_DATE}" --arg t "${TRIGGER}" --arg dr "${DRIVER}" \
              '{target_date: $d, triggered_by: $t, driver_name: $dr}')
          else
            body=$(jq -n --arg d "${TARGET_DATE}" --arg t "${TRIGGER}" \
              '{target_date: $d, triggered_by: $t}')
          fi

          response=$(curl -sS -m 240 \
            -X POST \
            -H "Authorization: Bearer ${SECRET}" \
            -H "Content-Type: application/json" \
            -d "${body}" \
            -w "\n__HTTP_STATUS__%{http_code}" \
            "${API_URL}/api/v1/internal/jobs/route-build")

          status="${response##*__HTTP_STATUS__}"
          response_body="${response%__HTTP_STATUS__*}"

          echo "::group::Response"
          echo "HTTP ${status}"
          echo "${response_body}" | jq '.' || echo "${response_body}"
          echo "::endgroup::"

          case "${status}" in
            200)
              run_id=$(echo "${response_body}" | jq -r '.run_id')
              approved=$(echo "${response_body}" | jq -r '.summary.approved_orders')
              blocked=$(echo "${response_body}" | jq -r '.summary.blocked_orders')
              echo "::notice::Route built: run_id=${run_id} approved=${approved} blocked=${blocked}"
              ;;
            400)
              echo "::error::Bad request — see response body"
              exit 1
              ;;
            401|403)
              echo "::error::Auth failure — check ROUTE_BUILD_SHARED_SECRET"
              exit 1
              ;;
            *)
              echo "::error::Unexpected HTTP ${status}"
              exit 1
              ;;
          esac
```

### Mobile UX walkthrough

1. Tom opens **GitHub mobile app** on phone.
2. Repo `gt-factory-os` → **Actions** tab → `route-build-cron` workflow.
3. Tap **Run workflow** → enters `target_date: 2026-05-10` → Run.
4. After ~30 seconds, workflow log shows the full RunPlan JSON.
5. (Optional v2) Telegram bot sends summary message: *"Route built for Sun 2026-05-10: 12 approved, 2 blocked. Tap to review."*

### Cron timing logic

- Cron `0 3 * * 6` = Saturday 03:00 UTC = Saturday 06:00 Israel.
- On Saturday morning, builds Sunday's route automatically.
- AreaRule note: the `target_date` is Sunday (workday), not Saturday. Tranche 0 area rules need a small adjustment to validate `target_weekday` not `run_at` weekday (see §6 below).

---

## 6 — Tranche 0 modifications needed

When migrating from `.archive-route-builder-2026-05-06` to `gt-factory-os/api/src/agents/route-builder/`, these changes are required:

### 6.1 Area rules — separate run_at from target_date

**Problem:** `areaForRunDate()` derives weekday from the date passed in. When run on Saturday for Sunday delivery, this throws `AreaRuleViolation`.

**Fix:** Rename `areaForRunDate(date)` → `areaForTargetDate(targetDate)`. Add separate validation that target is a workday. Run can happen any day.

```typescript
// New signature
export function areaForTargetDate(
  targetDate: Date,
  timeZone = 'Asia/Jerusalem'
): { weekday: WorkdayCode; area: DeliveryArea };
```

### 6.2 SQLite → Postgres

- Drop `src/persistence/db.ts` SQLite handle.
- Use existing `gt-factory-os` Kysely setup with PostgresDialect.
- Drop `data/route-builder.db` (no longer needed).

### 6.3 Migrate domain.ts as-is

`src/core/domain.ts`, `src/core/status.ts`, `src/core/area-rules.ts`, `src/core/priority.ts` — copy verbatim, only change file extensions (.js → .ts in imports per gt-factory-os convention).

### 6.4 Remove standalone CLI

- Drop `src/cli/index.ts` and `src/cli/commands/migrate.ts`.
- Migrations run via gt-factory-os existing migration tooling (`pnpm migrate:up`).
- Build trigger via API endpoint, not CLI.

### 6.5 Tests

- Move `tests/core/area-rules.spec.ts` and `tests/core/priority.spec.ts` to gt-factory-os test layout.
- Adjust imports for new path.
- Add new tests for stock-allocation and decision-engine (the new code).

---

## 7 — Phased rollout (governance-respecting)

### Phase A — Foundation migration (backend-db-executor)
**Scope:** Copy `core/*` files into `gt-factory-os/api/src/agents/route-builder/`. Add migration `00XX_route_runs.sql`. Run pgTAP test for new schema. No new behavior yet.

**Deliverables:**
- `api/src/agents/route-builder/core/{domain,status,area-rules,priority}.ts`
- `db/migrations/00XX_route_runs.sql`
- `db/tests/00XX_route_runs.test.sql` (pgTAP)
- Updated `api/test/agents/route-builder/*.test.ts`

**Tom approval:** schema approval (visual review of migration before apply).

**Acceptance:** all tests green; migration applies idempotently.

### Phase B — Stock allocation engine (backend-db-executor)
**Scope:** Build `stock-allocation.ts`. Pure function: `(rankedOrders, stockMap) → AllocationSnapshotRow[] + lineCheckByOrder`. No LionWheel, no DB writes. Fully unit-testable against fixtures.

**Deliverables:**
- `api/src/agents/route-builder/stock-allocation.ts`
- `api/test/agents/route-builder/stock-allocation.test.ts` (covers SHORT, AVAILABLE, STALE_STOCK, UNKNOWN_SKU, RESERVED_ELSEWHERE cases)

**Tom approval:** none (pure code, fixture-tested).

**Acceptance:** ≥10 test cases green; logic matches Tranche 0 contract types.

### Phase C — Decision engine (backend-db-executor)
**Scope:** Build `decision-engine.ts`. Combines area-rules + priority + stock-allocation → `RunPlan`. Pure function. Still no DB / external calls.

**Deliverables:**
- `api/src/agents/route-builder/decision-engine.ts`
- `api/src/agents/route-builder/route-build-runner.ts` (orchestrator)
- `api/test/agents/route-builder/decision-engine.test.ts`

**Tom approval:** none (pure code, fixture-tested).

**Acceptance:** end-to-end test against `orders-2026-05-07-center.json` fixture produces expected RunPlan.

### Phase D — API endpoint + DB integration (backend-db-executor)
**Scope:** Wire the engine to live data. Add Fastify route `/api/v1/internal/jobs/route-build`. Reads `orders_mirror` + `balance_anchors`. Writes `route_runs` + children. Bearer auth.

**Deliverables:**
- `api/src/routes/internal/route-build.ts`
- `api/src/services/route-build.ts` (service layer between route handler and engine)
- `api/test/routes/internal/route-build.integration.test.ts`
- Env var `ROUTE_BUILD_SHARED_SECRET` documented in `.env.example`

**Tom approval:**
- Confirm `ROUTE_BUILD_SHARED_SECRET` value (same pattern as `LIONWHEEL_POLL_SHARED_SECRET`).
- Confirm endpoint path acceptable.

**Acceptance:** integration test green against test DB; manual curl test green against local dev.

### Phase E — GitHub Actions workflow (manual write — no executor)
**Scope:** Add `route-build-cron.yml`. Tom adds `ROUTE_BUILD_SHARED_SECRET` to repo secrets. Tom adds same secret to Railway env.

**Deliverables:**
- `.github/workflows/route-build-cron.yml`

**Tom approval:**
- Confirm secret added to GH repo settings.
- Confirm secret added to Railway env.
- Approve cron schedule (Saturday 03:00 UTC).

**Acceptance:** manual `workflow_dispatch` from GitHub UI returns 200 with valid RunPlan.

### Phase F — End-to-end mobile test (Tom-driven)
**Scope:** Tom runs the workflow from his phone, verifies output, optionally Telegram.

**Acceptance:** Tom confirms workflow runs from mobile and produces a usable route plan.

### Future phases (NOT in this plan)

- **G:** Telegram bot integration (memory: bot infra planned).
- **H:** Apply route assignments to LionWheel (writes — requires Tom approval per CLAUDE.md, opens frozen-flag conversation).
- **I:** Portal UI for `/planning/routes/[run_id]` to review + approve route plan.

---

## 8 — Governance map

| Phase | Executor | Repo | Branch | Tom approval gate |
|---|---|---|---|---|
| A | `backend-db-executor` | `gt-factory-os` | `feat/route-builder-tranche-0-migration` | schema review |
| B | `backend-db-executor` | `gt-factory-os` | same as A | none (pure code) |
| C | `backend-db-executor` | `gt-factory-os` | same as A | none (pure code) |
| D | `backend-db-executor` | `gt-factory-os` | same as A | secret + endpoint approval |
| E | manual (this AI) | `gt-factory-os` | same as A | secret rotation + cron schedule approval |
| F | Tom | n/a | n/a | UAT |

**No `integration-boundary-executor` needed in v1** — no new LionWheel API calls; reuses `orders_mirror`.

**No portal change in v1** — `portal-production-executor` not invoked.

**No frozen-flag interaction** — `LIONWHEEL_FG_OUT_BRIDGE_ENABLED` stays `false`; route-builder is read-only against LionWheel.

**Push-to-main:** Tom only (per CLAUDE.md and memory `feedback_push_autonomously.md` — that memory is about post-commit push to current branch, not push-to-main; push to main remains Tom-only).

---

## 9 — Risk register

| Risk | Severity | Mitigation |
|---|---|---|
| `orders_mirror` data is stale beyond 15 min during Saturday cron run | LOW | `lionwheel-poll-cron` runs every 15 min including weekends; verify in `integration_freshness` view before run |
| Tom mobile triggers workflow with invalid target_date | LOW | API validates target_date is a workday; returns 400 with clear error |
| `balance_anchors` projection stale during Saturday morning | MEDIUM | Saturday morning is post-Friday close; projections should be fresh from Thursday close. Add freshness assertion: fail-fast if projection age > `freshness_threshold_hours` |
| Railway endpoint timeout on large order set | LOW | Set 4-min curl timeout; current order volume <50/day; engine is O(orders × items) which is trivial |
| Schema migration locks production briefly | LOW | All new tables; no ALTER on existing; sub-second lock |
| `ROUTE_BUILD_SHARED_SECRET` leak | MEDIUM | Standard pattern (same as `LIONWHEEL_POLL_SHARED_SECRET`); rotate quarterly; never echo in logs (per `feedback_env_display_allowlist.md`) |
| Workflow runs while DB migration in flight | LOW | Concurrency group + Railway zero-downtime deploy; worst case workflow returns 5xx, retried next cron tick |
| RunPlan logic disagrees with Tom's manual judgment | EXPECTED | v1 is advisory only; `was_applied_to_lionwheel=false` always; Tom reviews before any LW write |

---

## 10 — Decisions Tom needs to make

Before Phase A executes, Tom needs to confirm:

1. **Target repo:** `gt-factory-os` monorepo (selected ✅).
2. **Path:** `api/src/agents/route-builder/` — agree?
3. **Migration number:** backend-db-executor proposes next available number (currently `0149` is latest on main; next would be `0150` or higher depending on Window B state).
4. **Default driver name:** keep `Maksim` (Tranche 0 default) or change?
5. **Freshness threshold:** keep 24h default or tighten?
6. **Cron schedule:** Saturday 03:00 UTC (= Saturday 06:00 Israel). Adjust?
7. **Telegram integration:** in v1 (this plan) or v2 (separate)?
8. **Output format on success:** JSON in workflow log only, or also persist as Action artifact for later download?

---

## 11 — What this plan deliberately excludes

- Writing back to LionWheel (assigning routes, updating task statuses) — future Tranche, separate Tom approval.
- Portal UI for reviewing route plans — future Tranche.
- Telegram bot infrastructure — future Tranche if desired.
- Multi-driver support — v1 uses `driver_name` as a config string, not a multi-driver dispatch system.
- Multi-vehicle / multi-area same-day — v1 is single-area-per-day per Tranche 0 area rules.
- Historical comparison ("how did yesterday's plan compare to actual?") — future analytics.
- Customer-specific delivery windows beyond what Tranche 0 already models — future Tranche.

---

## 12 — Estimated effort

| Phase | Estimated time | Calendar realistic |
|---|---|---|
| A — foundation migration | 1.5 hr executor | 1 day with review |
| B — stock allocation | 2 hr executor | 1 day with review |
| C — decision engine | 2 hr executor | 1 day with review |
| D — API endpoint | 2 hr executor | 1 day with review |
| E — GH Actions workflow | 30 min manual | same day |
| F — Tom UAT | 30 min Tom | 1 day |
| **Total** | **~8 hr executor + manual** | **~1 work week** |

Realistic ship target: **2026-05-15** (next Friday) for Phase A–E ready, Tom UAT during the following weekend.

---

## 13 — Authority hierarchy reminder

This plan is advisory. It does NOT:
- Override `CLAUDE.md` locked decisions
- Authorize any code change
- Authorize any deploy
- Authorize any frozen-flag flip
- Authorize any LionWheel write
- Authorize any push to `main` on any repo

Each phase requires per-phase dispatch via `/factory-os-advance` or direct executor invocation, and respects every governance gate in `EXECUTION_POLICY.md`.

---

## 14 — Approval block

**Tom approves this plan to proceed to Phase A?**

- [ ] Yes — dispatch `backend-db-executor` with Phase A scope
- [ ] Yes with changes — see notes below
- [ ] No — needs revision

**Notes / changes requested:**

```
(Tom fills in)
```

**Approval timestamp:** ____________

---

**Owner:** Tom (sole approver).
**Plan author:** AI brain governance (this run, 2026-05-08).
**Pre-work artifact:** `c:\Users\tomw2\Projects\.archive-route-builder-2026-05-06\` — Tranche 0 foundation.
**Target repo:** `gt-factory-os`.
**Branch convention:** `feat/route-builder-tranche-X-Y` (one branch per phase or one branch for all phases — Tom decides).
