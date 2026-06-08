# GT Factory OS — Current State

> **Authority layer:** current state. Volatile. Expected to change at every gate transition and on significant runtime events.
>
> **Sibling docs (in this directory):**
> - `claude.md` (CLAUDE.md) — durable contract. Wins on every conflict with this file on locked decisions.
> - `EXECUTION_POLICY.md` — operational governance.
> - `ACTIVE_NOW.md` — short, fast-moving operator context (today's dispatch context only).
>
> **Authority rules:**
> 1. **This file is the sole authority on live runtime gate status, completion %, active critical path, UX release gate status, active corridor pointer, open UNRESOLVED items, and likely failure modes.** Other docs must point to this file, never restate it.
> 2. This file cannot relax a locked decision in CLAUDE.md. If a runtime fact here contradicts a locked rule there, CLAUDE.md wins and this file must be corrected.
> 3. On operational signals and portal mode, the harness state files (`.claude/state/runtime_ready.json`, `.claude/state/active_mode.json`) are authoritative. This file is reconciled from them and must not override them.
>
> **Allowed sections (closed list, Phase 8 Run F Wave 4 Hole 2 cleanup, 2026-05-09):**
> 1. Active corridor pointer (one-line link to `ACTIVE_NOW.md`)
> 2. UX release gate status
> 3. Overall completion
> 4. Gate-by-gate runtime status
> 5. What is complete / partial / missing
> 6. Current critical path
> 7. Open UNRESOLVED items
> 8. Likely failure modes
>
> **Sections not allowed here (with their migrated targets):**
> - Phase / Run history → `archive/historical-state-snapshots/2026-05-08-phase8-ai-brain-rewrite-snapshot.md`
> - Calibration / Layer 0 / Ralph Loop snapshots → `archive/historical-state-snapshots/2026-04-23-layer-0-snapshot.md` and `2026-04-25-ralph-loop-snapshot.md`
> - DB ops log → `docs/operations/db-ops-log.md`
> - Three corrective commits during Gate 3 DB run → `docs/operations/incidents/2026-04-23-gate3-corrective-commits.md`
> - Live DB connectivity note → `docs/contracts/SCHEMA_GUIDANCE.md` §Live DB connectivity
> - Canonical paths → `WORKSPACE_MAP.md`
> - RUNTIME_READY signal full enumeration → `.claude/state/runtime_ready.json` (live source) + `archive/historical-state-snapshots/2026-05-08-planning-corridor-detailed-state.md` (snapshot of the inline #1..#17 list)
> - Detailed Planning Corridor v1 evidence chain → `archive/historical-state-snapshots/2026-05-08-planning-corridor-detailed-state.md`

---

## Active corridor pointer

For active corridor identity, active lane(s), today's dispatch context, what must NOT be touched, and open Tom decisions blocking next dispatch — read `ACTIVE_NOW.md`. The current high-level corridor set as of 2026-05-09: (1) Shopify External Boundary v2 (Gate E in execution; bridge frozen); (2) Planning Corridor v1 (Tranche 3 CLOSED; Tranche 4+ Forecast Workspace queued); (3) Professional Stock-Truth Monitoring (Sunday 2026-05-10 cutover); (4) AI Brain Run G governance closure (in flight on branch `run-g-final-brain-closure`).

For the full evidence chain of the planning corridor as of the cleanup, see `archive/historical-state-snapshots/2026-05-08-planning-corridor-detailed-state.md`.

---

## UX release gate (2026-05-08, post-Run-C)

**Aggregate verdict:** **CONDITIONAL_SHIP** (was HOLD pre-Run-C).

**Per-surface verdicts:**
- `/(ops)/stock/waste-adjustments` — CONDITIONAL_SHIP (A11Y-001 form-label gap pending; A11Y-002 cleared)
- `/(ops)/stock/goods-receipt` — CONDITIONAL_SHIP
- `/(po)/purchase-orders/[po_id]` — CONDITIONAL_SHIP (INTER-001 confirmed P1)
- `/planning/blockers` — CONDITIONAL_SHIP (FLOW-003 closed in Run C; P1 polish remains)
- `/(ops)/stock/physical-count` — NOT_AUDITED at source level

Aggregate gate is not yet SHIP because:
- Physical count surface is still NOT_AUDITED at source level.
- Multiple surfaces carry P1 polish items.
- `DEV_TEAM_EMAIL` is not yet configured (clipboard action remains universal).

Evidence: `PRODUCTION/docs/phase8/dry-runs/DR-017-flow-003-closure-and-ux-release-gate-recheck.md`.

---

## Overall completion

**Overall runtime platform: ~60–70%.**

> **Stale-calibration note (2026-05-08, Phase 8 Wave 0):** This range was last set in the 2026-04-23 calibration. It does NOT yet reflect the Shopify External Boundary v2 phase progression (Phase 0+1+2+3+4 landed 2026-04-30…2026-05-08; Gate E in execution at backend tip `bcb2d0f`), nor the Professional Stock-Truth Monitoring corridor pre-cutover prep (2026-05-07 plans), nor the post-count cutover scheduled for 2026-05-10. Refresh deferred to a Phase 8 Wave 5 calibration step where Tom sets the new range based on evidence; Phase 8 Wave 0 only stamps the staleness, not the value.

Gate 3 is currently PARTIAL (Tom-locked 2026-04-30; LionWheel pick-reconciliation chain repair corridor in flight; corridor is bug-fix within Gate 3, not a ledger-semantics change; Gate 3 returns to CLOSED only when the chain repair lands and parity holds). The 2026-04-18 Gate 3 closure interpretation calibration is preserved as audit trail in `archive/historical-state-snapshots/2026-05-08-planning-corridor-detailed-state.md`.

**Per-gate ranges (Tom-authoritative, override governance defaults):**
- Gate 1 — Alignment / Contracts: ~95–100%
- Gate 2 — Foundation / Masters / Admin: ~70–85%
- Gate 3 — Stock Truth: ~95–100%
- Gate 4 — Operational Mirrors / Forecasting: ~10–20%
- Gate 5 — Planning / Recommendations: ~0–5%

---

## Gate-by-gate runtime status

### Gate 1 — Alignment / Contracts — LIVE_VERIFIED (artifacts exist, internally consistent)

Architecture map, schema map, portal module map, form definitions, integration contracts, migration phases, validation gates, rollback logic — all written and reconciled. Runtime contracts locked for Goods Receipt, Waste / Adjustment, and Physical Count. `freeze_guard_contract.md` added alongside Physical Count to govern count-freeze cross-form interactions.

### Gate 2 — Foundation / Masters / Admin — LIVE_VERIFIED (DB side)

- Migrations 0001 / 0002 / 0003 / 0005 applied to live DB
- 93 / 93 pgTAP assertions green on original masters pack
- 1,002 rows imported across 8 tables (suppliers = 43, bom_head = 68, items = 68, components = 145, bom_version = 68, bom_lines = 420, planning_policy = 5, supplier_items = 185)
- Idempotency confirmed
- `app_users` table live via 0005 + 0015 late-FK wire-up

**Runtime admin CRUD:** D4 Master Maintenance 5 admin screens committed as mocked + reconciled against locked SQL schema (Waves 1–5b). Admin runtime wiring resolved 2026-04-25: all admin screens (items, components, boms, suppliers, supplier-items, planning-policy, sku-aliases, sku-map, jobs, integrations) wired to real API endpoints. No mock data.

### Gate 3 — Stock Truth — PARTIAL

**Status:** PARTIAL. Tom-locked 2026-04-30. LionWheel pick-reconciliation chain repair corridor in flight; corridor is a bug-fix within Gate 3, not a ledger-semantics change. Gate 3 returns to CLOSED only when the chain repair lands and parity holds.

**DB layer (LIVE_VERIFIED):**
- Migrations 0006 / 0007 / 0008 / 0009 / 0010 / 0011 / 0012 / 0013 / 0014 / 0015 / 0016 applied to live DB
- 76 / 76 pgTAP assertions green on 0007–0009
- 22 / 22 pgTAP green on 0013 (`rebuild_verifier` wrapper)
- 44 / 44 pgTAP green on 0014 (`count_freezes`)
- 0015 (`app_users` late FK wires) + 0016 (projection boundary fix) applied and tested
- 209 anchors imported (68 FG + 141 RM)
- V1 count ✓; V2 projection parity 209 = 209 ✓; `rebuild_verifier()` = 0 ✓; parity gate 5/5 green; smoke test `drift_count = 0` across 209 balance keys

**Form runtime (per-form status, authoritative source: `.claude/state/runtime_ready.json`):**

| Form | Signal | Status on disk |
|---|---|---|
| **Goods Receipt** | `RUNTIME_READY(GR)` not emitted; Gate 3 closure path used direct handler evidence + live smoke probe per `gate3_closure_decision_pack.md` rather than a GR signal | Handlers (`api/src/goods-receipts/{handler,route,schemas}.ts`), runtime contract, pgTAP `goods_receipt_runtime.test.sql`, live-verification pack (`gate3_gr_live_verification_pack.md`), and preflight script (`verify_gr_preflight.ts`, 14/14 probes pass) all present and cited in closure pack |
| **Waste / Adjustment** | `RUNTIME_READY(WasteAdjustment)` emitted **2026-04-17T16:54:13Z** by executor-w1 | Evidence: `waste_adjustment_runtime.test.sql` (33/33 pgTAP green); pass-3 smoke matrix (7 cases); pass-3b follow-up matrix (13 cases). `rebuild_verifier()` = 0 after all 20 cases. All six §3.3 items of `waste_adjustment_runtime_contract.md` closed |
| **Physical Count** | `RUNTIME_READY(PhysicalCount)` emitted **2026-04-17T19:21:41Z** by executor-w1 | Evidence: `physical_count_runtime.test.sql` (31/31 pgTAP); PC HTTP matrix (18 cases + 1 bug-fix re-verification). All five `count_freezes` terminal states exercised. Anchor history integrity: 4 rows for 4 replacements. Blind-count invariant: snapshot_quantity never exposed in GET /open. `rebuild_verifier()` = 0 after all cases. Bug found+fixed during verification: handler now short-circuits to idempotent replay via top-of-handler `form_submissions` lookup before the snapshot SELECT |

**Minimal Exceptions Inbox (Gate 3 literal criterion #4):** 16 named node:test E1–E16 green in `api/test/exceptions.test.ts`; portal sandbox Playwright real-harness spec `exceptions-inbox-real.spec.ts` exists at `c:/Users/tomw2/Projects/window2-portal-sandbox/tests/e2e/`. `RUNTIME_READY(ExceptionsInbox)` signal emitted 2026-04-18T00:00:00Z; evidence pack at `docs/gate3_exceptions_inbox_evidence.md`.

**Portal mode (authoritative source: `.claude/state/active_mode.json`):** portal current mode = **A** as of 2026-04-27T08:18:00Z. Most recent Mode B exit: Planning-Tranche3-Blockers (commit `e7dce27` on window2-portal-sandbox/main, 2026-04-27). Per `EXECUTION_POLICY.md`, only one form may be in Mode B at a time. Prior Mode B exits are recorded in `.claude/state/active_mode.json`; the snapshot of the prior-exit list is preserved at `archive/historical-state-snapshots/2026-04-25-ralph-loop-snapshot.md`.

**RUNTIME_READY signal count:** 40 (latest: LooseShipmentLedger 2026-05-26). Authoritative source: `.claude/state/runtime_ready.json`.

### Gate 4 — Operational Mirrors / Forecasting — CLOSED

Gate 4 closure tip on main: `422e146` (2026-04-18). Contract pack: 12+ files in `docs/integrations/`. Runtime layer CLOSED on:

- **EC-1 LionWheel mirror** — Option B ratified: Supabase Edge Function `factory_os_jobs` (Deno, `npm:pg` + `npm:zod`) + `pg_cron` → `pg_net` invocation; migrations 0030/0031/0032; break-glass respected; 29/29 pgTAP green. `RUNTIME_READY(LionWheel)` emitted 2026-04-18T20:33Z; evidence at `docs/gate4_option_b_closure_checkpoint.md`.
- **EC-3 freshness_check** — 7-producer state map with self-silence path pgTAP green (5/5); heartbeat producer added (warn_min=10 / crit_min=25); auto-resolution path observed end-to-end. `RUNTIME_READY(freshness_check)` emitted 2026-04-18T20:33Z.
- **Forecast runtime** — G-08 FULLY CLEAR: 4 writes + G.4 open-cold-start + 5 reads + F11 cross-version drift at handler layer; pgTAP 0022 10/10, forecasts_handler 27/27, forecasts_reads 13/13 green. `RUNTIME_READY(Forecast)` emitted 2026-04-18T19:30Z.

Follow-on Gate 4 items (NOT runtime blockers, carried forward):
- G-07 forecast audit-trigger implementation against `change_log_contract.md`
- G-10 forecast.publication integration wiring
- LionWheel demand model: hybrid resolver live (2026-04-23, `rows_unknown_sku=0`); 330/404 lines (81.7%) resolved; 74 unresolved lines remain (bundles 44 + held 5 + non-catalog ~23 + malformed 2). Excluded demand is a planning-completeness gap, not a system failure. Bundle policy tranche pending. JASM/PNMM held for Tom.
- MC-U2 FG_OUT bridge enablement — contingent on SKU alias saturation

### Gate 5 — Planning / Recommendations — FULLY CLOSED AT PHASES 0–9

Per `docs/gate5_closure_decision_pack.md` (2026-04-19 updated post-Phase-9, executor-w1) at repo tip `8c22ce9`:

- **Closure disposition:** FULLY CLOSED at Phases 0–9 per plan amendment A11 + CLAUDE.md §"Gate model" literal exit criteria. Prior A10 fallback path no longer operative. Phase 10 cost rollup is post-closure stretch per A11.
- **Phases 0–9 complete:** Phase 0 (entry contracts) → Phase 1 (canonical demand layer; migrations 0033/0034/0035; 35/35 pgTAP) → Phase 2 (policy readiness; migration 0036; 14/14 pgTAP) → Phase 3 (planning run substrate; migrations 0037/0038/0039; 53/53 pgTAP) → Phase 4 (net requirements engine; migrations 0040/0041/0042; 35/35 pgTAP) → Phase 5 (purchase recs; migration 0043; 17/17 pgTAP) → Phase 6 (production recs; migration 0044; 16/16 pgTAP) → Phase 7 (planning run orchestration; migrations 0045/0046; 16/16 pgTAP + 3/3 pgTAP + 8/8 node:test + 1/1 byte-equal reproducibility proof) → Phase 7.5 (planning review backend; migrations 0047/0048; 23/23 node:test) → Phase 8 (portal MVP `/planner/runs`; 8/8 Playwright real-HTTP E2E green) → Phase 9 (recommendation → PO bridge; migrations 0049–0057; 58/58 pgTAP; 14/14 node:test; `RUNTIME_READY(PurchaseOrders)` emitted 2026-04-19T08:00:00Z).
- **Phase 10 NOT ATTEMPTED:** post-closure stretch per A11. Cost rollup matches manual reconciliation remains for a future cycle. Reserved migrations `0058+`.
- **EC disposition (CLAUDE.md §Gate model Gate 5):** EC-1 reproducibility CLOSED (Phase 7C byte-equal); EC-2 human approval before PO FULLY CLOSED (Phase 7.5 + Phase 8 + Phase 9 programmatic enforcement via `fn_convert_recommendation_to_po` NOT_APPROVED 409 gate); EC-3 Production Actual NOT-IN-GATE-5-V1-SCOPE (A13 judgment); EC-4 cost rollup DEFERRED under A11.
- **integration contract pack consumed verbatim (commit `a63bf99`):** 4 PO substrate contracts. Zero invented contract values; zero silent healing.

> Gate 5 commit-by-commit tranche listing and main-tip progression are preserved at `archive/historical-state-snapshots/2026-05-08-planning-corridor-detailed-state.md` §"Gate 5 commit log".

---

## What is complete / partial / missing

**Complete (LIVE_VERIFIED):**
- Gate 1 artifact set (incl. GR / Waste / PC runtime contracts + freeze_guard_contract)
- Gate 2 DB-side foundation (schema, migrations, imports, app_users)
- Gate 3 DB-side stock-truth layer (ledger, anchors, projection, rebuild_verifier, parity gate, exceptions, count_freezes, projection boundary fix)
- Gate 3 form-runtime evidence on CLAUDE.md literal exit criteria — parity, idempotency, race, minimal Exceptions Inbox
- Gate 4 runtime layer — LionWheel mirror (Option B Supabase Edge Function + pg_cron + pg_net), freshness_check with self-silence, forecast API handler stack (4 writes + 5 reads + F11), forecast.publication producer
- Gate 5 planning engine Phases 0–9 — canonical demand layer, policy readiness, planning run substrate, net requirements (FG netting + BOM explosion + supply netting), purchase recommendations, production recommendations, planning run orchestration with reproducibility proof, planning review backend, portal MVP `/planner/runs`, recommendation → PO bridge with end-to-end approve→convert→receive proof
- integration contract pack (12 Gate-4 files + 5 Gate-5 files + 4 Phase-9 PO contract files; requirements-only)
- Stock Truth Layering Change 1 — display clamp + Reconcile badge + StockTruthDrawer on `/inventory`. MERGED 2026-05-14. Backend additive (`on_hand_raw` / `on_hand_display` / `is_below_floor` / `floor_gap` on `/api/v1/queries/stock`; merged to `gt-factory-os:main`). Portal: display clamp + Reconcile badge + Drawer merged to `window2-portal-sandbox:main`; version-skew fallback hotfix (PR #17 `dc8f514`); copy-honest FLOW-002/003/009 fixes (PR #18 `16e5dfb` — removed `private_core.current_balances` schema name from trust strip, replaced `BOM cost not set` badge copy, `missingCostOnly` filter now includes `pending_rollup`, `Post physical count` link live). Truth surfaces (rebuild_verifier, planning inputs, audit, ledger) untouched. Spec: `docs/superpowers/specs/2026-05-13-display-clamp-physical-stock-truth-design.md`.
- Stock Truth Layering Change 2 — inventory-flow projection clamp + shortfall indicator on `/planning/inventory-flow`. MERGED 2026-05-14. Backend (PR #26 `40693e7`): inner CTE retains signed values for tier/stockout detection; outermost SELECT emits `GREATEST(0, projected_on_hand_eod)` + `shortfall_qty` gap; mirrored for supply flow and `current_on_hand` seed. Contracts (`contracts.flow.ts`): `FlowDay.shortfall_qty` / `shortfall_qty_with_production` and `FlowWeek.max_shortfall_qty` / `max_shortfall_qty_with_production` (all ≥ 0). Portal (PR #20 `709f3ac`): `DayCell` and `WeekCell` render `−N` shortfall hint when shortfall > 0; defensive `??` fallback for API version skew. 7/7 parser tests + T8–T15 integration tests added. Change 3 (exception emission) deferred.
- Stock Truth Layering Change 4 — Shopify available-for-sale write. AW-G1 (payload shape) CLOSED. AW-G2 (migration 0187, 28/28 smoke) CLOSED. AW-G3 shadow soak IN PROGRESS — first clean cycle 2026-05-14T16:30Z; 186 audit rows (108 shadow_would_set_available, 78 shadow_skip_unmapped). Bug fixed: `i.name` → `i.item_name` in source query (`017ef14`). AW-G4 CLOSED — `SHOPIFY_GRAPHQL_SYNC_ENABLED=true` set 2026-05-14; v2 on_hand sync already running (410+ cycles). **48h soak window: 2026-05-14T16:30Z → 2026-05-16T16:30Z.** `SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED` remains `false` until AW-G5/G6/G8/G9 closed post-soak. Gate packet: `docs/phase8/decisions/shopify-available-aw-g1-approval-2026-05-14.md`.

**Partial:**
- Gate 3 follow-on operational items (NOT exit blockers): (a) GR `RUNTIME_READY` signal; (b) portal Mode B exit finalization for WasteAdjustment
- Gate 4 follow-on items (NOT runtime blockers): G-07 forecast audit-trigger; G-10 forecast.publication integration wiring
- Portal canonical surfaces — Mode B for Waste, Forecast MVP, PlanningRun MVP authored; cross-run purchase/production list views deferred; Convert-to-PO button surface on `/planner/runs/[id]` deferred to optional follow-on Mode B dispatch

**Missing:**
- LionWheel demand completeness gap — 74 unresolved lines / 24 distinct SKUs remain outside planning: bundles (GTSET-*, 9 SKUs, 44 lines), held aliases (GTCC-MUZ-JASM-1L + GTCC-MUZ-PNMM-1L), non-catalog (~13 SKUs, ~25 lines), malformed/test (2). UNRESOLVED-7 CLOSED: 37 exact legacy_sku direct matches confirmed by live DB.
- Gate 5 Phase 10 cost rollup (post-closure stretch per A11; reserved migrations `0058+`)
- MC-U2 FG_OUT bridge enablement (contingent on SKU alias saturation)
- `RUNTIME_READY(GR)` signal (harness-durability improvement; not a gate exit blocker)
- Phase 9.1 rebuild-verifier for PO header parity (deferred per UNRESOLVED-LC-5)
- Portal minimal Convert-to-PO button surface on `/planner/runs/[id]` (optional follow-on Mode B dispatch)
- Shopify sync runtime
- Green Invoice ingest runtime
- Dashboard KPI aggregation endpoints (runs-today, last-movement) — backend-blocked; new API endpoints needed

---

## Current critical path

**All v1 gates CLOSED at Phases 0–9 per A11 + CLAUDE.md §"Gate model" literal exit criteria** (main tip `8c22ce9`, 2026-04-19). No further v1 gates are unlocked by this closure.

**Post-Gate-5 priorities (not gate-blocking):**
- Phase 10 cost rollup (stretch per A11) — post-closure economics layer; reserved migrations `0058+`
- SKU alias seeding workflow (operational; unblocks MC-U2 FG_OUT bridge enable)
- MC-U2 FG_OUT bridge enable (contingent on SKU alias saturation)
- portal_universe fake-session seed on pooled DB
- `.mcp.json` disposition (Tom-pending)
- Portal minimal Convert-to-PO button surface (optional follow-on Mode B dispatch cycle)
- Phase 9.1 rebuild-verifier for PO header parity (UNRESOLVED-LC-5)

---

## Open UNRESOLVED items (must not be silently healed)

Any activation that would otherwise touch one of these items must emit `assumption_failure` and surface the gap.

- **LionWheel order line schema, stable identifiers, and status lifecycle** — requires live API inspection; no field name may be guessed
- **Green Invoice line-item schema and supplier-SKU availability** — requires live API inspection; auto-creation of components forbidden until resolved
- **Shopify cancellation / refund path in GT's specific order flow** — reconciliation behavior undefined until inspected
- **Whether customer-specific pricing exists in current operations** — until confirmed, customer pricing is not modeled
- **PBR-1 — RESOLVED 2026-04-27 by Tom:** `demand_qty` = SUM across all planning horizon buckets (Option 1, "total horizon", scale of risk view). DTO must ALSO include separate urgency fields when available: `earliest_shortage_at` / `earliest_bucket_date`, `earliest_bucket_required_qty`, `affected_bucket_count`. UI shows total demand as main scale metric + earliest shortage as urgency cue.
- **PBR-2 — DELEGATED to backend-db (A13):** Run-level exception handling with `?item_id=` filter — backend-db autonomous decision at implementation time.
- **PBR-3 — DELEGATED to backend-db (A13):** `blocker_detail` key schema stability — backend-db autonomous decision (integration recommends opaque).
- **PBR-4 — DELEGATED to backend-db (A13) 2026-04-27 by Tom:** `missing_supplier_mapping` `component_id` semantics — backend-db must inspect `fn_generate_bf_purchase_recommendations` (migration 0102) and live schema; if exception payload is ambiguous/inconsistent, backend-db normalizes in the backend DTO and documents the source mapping. Do NOT guess. Do NOT let portal invent field semantics.
- **Planning Tranche 3 route LOCKED:** `/planning/blockers` (Tom 2026-04-27). Page title "חסמים בתכנון", subtitle "פריטים עם ביקוש שלא הפכו להמלצת רכש או ייצור שמישה".
- **Concrete tolerance thresholds** for (a) count discrepancy auto-post vs approval; (b) Green Invoice price-change auto-update; (c) rebuild-from-ledger parity check
- **Exact precision/scale values** for the quantity domain and the money domain (CLAUDE.md locks the principle; current working values `qty_8dp = numeric(24,8)`, `ratio_8dp = numeric(24,8)`, `money_4dp = numeric(18,4)`, `pct_4dp = numeric(9,4)` are not yet formally pinned)
- **On-prem read-only replica refresh cadence and failover rules** — CLAUDE.md locks "read-only fallback only"; cadence and failover not specified
- **Auth method** — CLAUDE.md locks Supabase magic-link email auth; wiring mechanics and first-user bootstrap still open; dev-shim fake-auth still in use in sandbox
- **The `.claude/agents/` executor / verifier / governor files** — the skill defines target architecture; production agent set (Phase 8 Run B + Run F) is on disk but the legacy / production transition is governed by `docs/phase8/deprecation/ACTIVE_SURFACE_REDUCTION_PLAN.md` and Wave 6 evidence

---

## Likely failure modes from here

The shapes most likely to fail or mislead over the next gate transition:

1. **Treating `RUNTIME_READY(form)` as Gate 3 exit.** It is a precursor, not exit evidence. Gate 3 exit = parity-after-live-production-form-traffic. Two signals emitted ≠ Gate 3 closed.
2. **Backend-db runtime tree remaining uncommitted on `main`.** Harness state + local evidence are real, but source that is not on `main` cannot be rolled forward, reviewed, or rolled back. Treat uncommitted production-path code as an outage risk.
3. **Portal drifting into Mode B for a second form before exiting Mode B for Waste.** `EXECUTION_POLICY.md` allows only one scoped form at a time. Parallel Mode B for Waste + PhysicalCount is a policy violation.
4. **Form submits that look green but do not produce posted ledger events.** UI rendering is not evidence. Gate 3 exit requires parity-after-live-traffic on production data, not 200 OK on a submit button.
5. **LionWheel mirror built against guessed field names.** UNRESOLVED Gate-4 items remain. Any runtime built against assumptions will reconcile incorrectly at the first real split/merge/cancel.
6. **Shopify disagreement resolved in the wrong direction.** The platform is authoritative. Any reconciler that defers to Shopify on drift is broken.
7. **Green Invoice auto-creating components or auto-updating prices.** Forbidden until mapping quality and threshold rules pass. A price feed that "just updates" corrupts the pricing audit trail.
8. **Planning begun before Gate 3 closes.** "Stock truth ships before planning cutover" is non-negotiable (CLAUDE.md §non-negotiables #1). Beginning Gate 5 work while Gate 3 is PARTIAL is a contract_failure.
9. **Admin CRUD mass-edits to BOM or supplier mapping without approval gates.** CLAUDE.md Gate 2 / Gate 3 evidence rules forbid this; the admin screens today are mocked precisely because wiring them to writes is not yet safe.
10. **Excel round-trip creeping back in.** Any operator-facing workflow that edits the workbook re-introduces the system being rebuilt out of.
11. **LionWheel pick-reconciliation chain blocked by operator discipline + code defects + soak verification, NOT by missing API capability.** Live evidence 2026-04-30: LionWheel populates `body.task.order_items[].picked_quantity` when pickers explicitly enter quantities in the UI; Tom-edited shipment 24328405 confirms the field path matches production code expectations. The 11/11-null finding from the prior capture reflects pickers not entering quantities, not API gap. Open blockers: (a) operational soak — 5-10 real Day-1 orders required; (b) Phase 1 code defects (`task.status='COMPLETED'` enum drift, type asymmetry, per-line `status` field schema drift); (c) Phase 2 code defect — premature `reconciledMirrorIds.add(row.mirror_id)` inside the `!fg_out_bridge_enabled` short-circuit. Zero LionWheel-derived `FG_OUT_PICK` rows in production history; FG `current_balances` overstated by cumulative delivered volume since cutover. Path forward: see `docs/lionwheel_chain_repair_plan_2026-04-30.md`.
