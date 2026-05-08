# GT Factory OS — Current State

> **Authority layer:** current state. Volatile. Expected to change at every gate transition and on significant runtime events.
>
> **Sibling docs (in this directory):**
> - `claude.md` (CLAUDE.md) — durable contract. Wins on every conflict with this file on locked decisions.
> - `EXECUTION_POLICY.md` — operational governance.
> - `ACTIVE_NOW.md` — short, fast-moving operator context.
>
> **Authority rules:**
> 1. **This file is the sole authority on live gate status, completion range, active critical path, and major open gaps.** Memory files, ACTIVE_NOW.md, and all other docs must **point** to this file, never **restate** it.
> 2. This file cannot relax a locked decision in CLAUDE.md. If a runtime fact here contradicts a locked rule there, CLAUDE.md wins and this file must be corrected.
> 3. On operational signals and W2 mode, the harness state files (`.claude/state/runtime_ready.json`, `.claude/state/active_mode.json`) are authoritative. This file is reconciled from them and must not override them.

---

## Active corridor — Planning Corridor v1 (baseline 2026-04-30)

**Parallel corridor 2 — Shopify External Boundary v2 (in flight 2026-05-07):** plan authored at `gt-factory-os/docs/superpowers/plans/2026-05-07-shopify-lionwheel-external-boundary-v2.md`. **Phase 0 CLOSED 2026-05-07T11:55Z** — kill switch live (`SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED=false`); v1 blind `inventory_levels/set.json available=N` writes blocked end-to-end (10K+/day mutations stopped); migration `0152_shopify_fg_sync_history_disabled_status.sql` applied to live DB (CHECK expansion); evidence at `gt-factory-os/docs/superpowers/evidence/2026-05-07-shopify-phase0-bleeding-stopped.md` (PRs #6/#7/#8 merged). **Phase 1 CLOSED 2026-05-07T13:00:55Z** — 4 contracts + 3 W1 specs landed (PR #9, commit `e123276`): `shopify_fg_sync_contract_v2.md` (17 sections, 9 readiness gates G-1..G-9, blind-available-set forbidden, `ignoreCompareQuantity` restricted to repair-command-only); `shopify_fulfillment_bridge_contract.md` (15 sections, disjoint trigger from FG sync, idempotency `lw_fulfillment:<lw_task_id>`); `shopify_movement_policy.md` (live-DB enumeration of 18 movement_type values, default UNDECIDED for unknowns); `shopify_v2_phase2_implementation_plan.md` (full 15-scenario test matrix with given/when/then). v1 SUPERSEDED banner. Verifier PASS 10/10. **Phase 2+3+4 in flight** under Tom's 2026-05-07 end-to-end-with-hard-stop directive: W1 schema migrations (≥0153) + W4 pure modules in parallel, then W4 wiring + shadow logging. **Hard stop:** no live GraphQL inventory mutation, no live fulfillment bridge enablement until Phase 5 readiness report and explicit Tom approval. 13 historical `shopify_drift` exceptions remain untouched (REPORT/TRIAGE ONLY).

**Cycle-trail evidence files added 2026-05-07** (post-PR-#17 R2 real adapters merged 18:50:48Z; Edge Function v28 deployed; 52/52 tests pass; both `*_LIVE_ADAPTER_WIRED` sentinels remain `false`):
- `gt-factory-os/docs/superpowers/evidence/2026-05-07-shopify-pre-live-decision-pack-v2.md` (pre-live readiness decision pack)
- `gt-factory-os/docs/superpowers/evidence/2026-05-07-shopify-r2-adapter-run.md` (R2 real-adapter shadow-mode evidence)
- `gt-factory-os/docs/superpowers/evidence/2026-05-07-shopify-gate-e-preparation-and-drift-closure-plan.md` (PR #18 merged 19:27:20Z, commit `7f82ee1`, 5 deliverables: 8-blocker drift list, LW `lw_qty_picked` enrichment recovery post-key-rotation, Gate E execution pack on candidate test SKU `ADD-GAR-ANISE`, sentinel circularity options A/B/C/D, 7-blocker ordered list)
- **Open Tom decisions blocking next dispatch:** GE-1 (test SKU confirmation; recommended `ADD-GAR-ANISE`), GE-2 (sentinel strategy — Option C SKU-allowlist-scoped flag recommended; Option B time-bounded global flip as fallback). GE-4 (task 24442225 `wp_order_id`) resolved as `#GT12757` by W4 verifier.

**Parallel corridor — Professional Stock-Truth Monitoring (in flight 2026-05-07):** plan authored at `PRODUCTION/docs/superpowers/plans/2026-05-07-professional-monitoring.md`. Tom-locked Sunday 2026-05-10 as cutover day (post physical count). **Pre-cutover prep landed this session:** (1) 70 LionWheel SKU mappings written to `integration_sku_map` — coverage went 0→83% on terminal lines (558/683 in last 14d will post on bridge flip; 122 silently skip per excluded_legacy_bundle/excluded_non_stock; 3 → exception inbox). (2) 2 new master items created: `FG-SAN-BAB-RED-750ML` (RED SANGRIA BABA 0.75L, shares BOM with FG-SAN-RED-750ML), `AP-DRI-PIN-1KG` (PINEAPPLE DRIED 1KG, BOUGHT_FINISHED). (3) Typo fix on `AP-TAP-PIN-0.6` (was "MANGO", now "PINEAPPLE"). (4) Sentinel item `EXCLUDED-NONSTOCK` (`is_stock_managed=false`) created as the FK target for excluded mappings. (5) Sunday cutover runbook authored at `PRODUCTION/docs/superpowers/runbooks/2026-05-10-sunday-cutover-runbook.md`. **In flight:** B.1 (audit_runs migration 0151 + daily Railway cron, executor-w1) + B.2 (Telegram alert dispatcher, executor-w4) — both dispatched in background. **Bridge state:** `LIONWHEEL_FG_OUT_BRIDGE_ENABLED=false` — DO NOT FLIP until Sunday post-count per runbook §5. **Open Tom dependencies:** Telegram bot token + chat_id (runbook §10), JOB_RUNNER_TOKEN provisioning, app_users uuid for count import. Two SKUs intentionally left unmapped (`""` empty + `7290003803217` EAN, 5 lines/30d total — exception inbox).

**Active program:** Forecast → Planning Run → Production Recommendations → Daily Production Plan → Purchase Recommendations → Production Actual / PO. Driven by Tom's autonomous-program directive 2026-04-30.

**T1 status (planning corridor UX clarity):**
- T1 deployed green at portal commit `fde59c8` (Vercel + Railway portal-side both `state: success`, 2026-04-30T13:02:52Z / 13:03:37Z).
- T1 manual browser walkthrough (9-item checklist) NOT YET RUN.
- **T1 is CODE-COMPLETE / DEPLOYED, not production-verified.** Status A (production-verified) requires the manual click-through.
- Static verification: typecheck `EXIT=0`; no remaining `window.confirm` in `/planning/runs`; no remaining dead `/convert` portal navigation; `JSON.stringify(body)` admin-gated; reason_codes mapped before display.

**Active follow-ups:**
- `W1-FOLLOWUP-CONVERT-RACE` — RESOLVED 2026-04-30 (see Open UNRESOLVED items below; row-locked via `FOR UPDATE` in migration 0056).

**Daily Production Plan v1 — Gates 3A → 3B → 4 → 4.2 → 5 (from_plan) DONE on disk (2026-04-30 → 2026-05-01); cycle 1 of overnight Ralph Loop reconciled the state:**
- Table `private_core.production_plan` — **APPLIED** to live Supabase 2026-04-30 ~13:02. Migration file canonical filename: `db/migrations/0115_production_plan.sql` (renamed from 0114 to resolve slot collision with `0114_master_data_cleanup_phase1.sql`; live DB unchanged by rename — no migration tracking table exists in repo, verified by grep). Test file: `db/tests/0115_production_plan.test.sql`. 10/10 runtime functional assertions PASS via Node-based runner (formal `pg_prove` not run; pgTAP file ready). Contract: `gt-factory-os/docs/production_plan_contract.md`.
- API endpoints `/api/v1/queries/production-plan` + `/api/v1/mutations/production-plan` — **Gate 3B DONE** at canonical main `bafbcb0` (2026-04-30). 14/14 node:test PASS against live pooled Supabase PG17.
- Route `/planning/production-plan` — **Gate 4 DONE** at portal main `483ac66` (2026-04-30); **Gate 4.2 English/LTR + state hygiene DONE** at portal main `4fee418` (2026-05-01). Audit P0 surfaces remain open on OTHER planning surfaces — see `PRODUCTION/docs/overnight_audit_2026-05-01.md` (16 P0 / 38 P1 / 50 P2 / 29 P3 across 12 corridors).
- `production_actual` `from_plan_id` parameter — **Gate 5 additive linkage DONE** this cycle (overnight Ralph Loop cycle 1, 2026-05-01). Signal #18 `RUNTIME_READY(ProductionActual-FromPlan)` emitted 2026-05-01T16:35:00Z; Railway deployment `2edf9930-2164-4a1c-904a-259932ee68f4` healthy; 4 new conflict codes (`PLAN_NOT_FOUND` / `PLAN_ITEM_MISMATCH` / `PLAN_ALREADY_COMPLETED` / `PLAN_CANCELLED`); live-DB `PRODUCTION_PLAN_LINKED_ACTUAL` change_log_action already present from migration 0115. Evidence: `gt-factory-os/docs/production_actual_from_plan_checkpoint.md` + `api/test/production_actual_from_plan.test.ts` (8/8 PASS, independently re-run by verifier). **Committed and pushed: gt-factory-os/main `821dfd5` (W1 Gate 5 from_plan tranche) + `069f136` (W4 dashboard control-tower v2 spec).**
- Inventory-flow planned-inflow overlay — Gate 5b, NOT YET IMPLEMENTED.
- Dashboard control-tower v2 coverage requirements spec authored this cycle: `gt-factory-os/docs/integrations/dashboard_control_tower_v2_coverage_requirements.md` (W4, 721 lines, 7 GAPs, 8 UNRESOLVED items DCT2-1..DCT2-8). GAP-7 (production_actual.from_plan column) closed same cycle by W1 signal #18.
- **RUNTIME_READY signal count: 31** (was 17 → 18 ProductionActual-FromPlan → 19 CriticalToday → 20 AddFromRecommendations → 21 Planning-Tranche2-RecommendationDetail-v1.1 → 22 ProductionPlanSlippage → 23 DashboardCriticalToday → 24 DashboardSlippedPlans → 25 AdminHolidays → 26 HolidaysArchivedFilter → 27 LionWheelOrderNote → 28 LionWheelCreditDecisionBackend → 29 PlannedInflowByDay → 30 LionWheelRuntimeClosure → **31 ProductionActual-TwoHead** (Tom-screenshotted critical bug fix; 6 tranches landed 2026-05-02; verifier PASS; **FULL GO 2026-05-02** — Tom confirmed visual portal acceptance on FG-DES-1L; data-fix follow-on migration 0130 closed the 5 MAR/SAN `pack_no_base_bom_line` anomaly via version-bump path; see `PRODUCTION/docs/two_head_bom_repair_evidence.md` + `PRODUCTION/docs/2026-05-02-two-head-bom-explosion-repair-plan.md`)).

**Two-Head BOM Repair (2026-05-02) — closed end-to-end:**
- Bug: Production Actual handler did single-level BOM explosion on `items.primary_bom_head_id` (PACK) only; data model has TWO heads per MANUFACTURED item — PACK (packaging) + BASE (liquid recipe). Same blind spot in planning engine `fn_explode_bom_to_components`. Tom screenshotted FG-DES-1L showing only 4 packaging components, no liquid.
- Fix: 6 tranches in one day. Migration 0127 added `production_actual.base_bom_version_id_pinned`. Migration 0126 v2 of `fn_explode_bom_to_components` (recursive two-head walker; same signature, no caller change). Handler `loadTwoHeadBomContext` helper + 4 new node:tests; 7 new conflict reason codes. Portal page.tsx grouped sub-headings (`רכיבי אריזה` / `רכיבי נוזל`) + composition banner. CLAUDE.md §"Production reporting v1" amended.
- Empirical proof: 42/50 post-deploy `stock_ledger` submissions exhibit two-head explosion signature (both `:CONSUME:pack:` and `:CONSUME:base:` rows under same `source_event_id`); pre-fix this number was 0. `rebuild_verifier()=0`. Post-fix audit identical to baseline 48 items.
- Pre-launch: no historical reconciliation needed (all prior `production_consumption` rows were synthetic test data).
- Data-fix follow-ons:
  - **5 MAR/SAN items — CLOSED 2026-05-02 via migration 0130** (commit `5c4753d`, version-bump path, per-pack base liters = bottle volume). Audit `pack_no_base_bom_line` bucket: 5 → 0; `ok_two_head` bucket: 26 → 31.
  - **Legacy `'BOM'` ref-type cleanup — CLOSED 2026-05-02 via migration 0131** (commit `532553b`, Option 1 expanded scope: 10 rows flipped to INACTIVE on the 5 affected PACK heads + new CHECK constraint `bom_lines_no_bom_ref_on_pack_active` preventing recurrence on PACK/REPACK heads). pgTAP 7/7. Bug-fix proof: zero `unsupported_bom_ref` exceptions emitted on synthetic FG-MAR-CLA-300ML planning run.
  - **6 MUZA mixers** — still open (Tom must decide complete-BOM vs flip to BOUGHT_FINISHED). NOT blocking — handler returns 409 NO_BOM_HEAD until resolved.
  - **5 T2DET test fixtures** — still open (cleanup). Trivial; can happen any time.

**Planning Corridor v1 — RESUMES** after this repair lands (was rate-limit-interrupted at cycle 8 partial state per prior CURRENT_STATE entries; the two-head repair was higher priority because the planning engine itself was producing wrong purchase recommendations for liquid RM on every run).
- W2 sandbox tip advanced from `4f2d325` → `4fee418` → `9f3b98e` (cycle 2 production-actual P0-A) → `24e5a7a` (cycle 3 planning-runs P0-B/C/E/I sweep) → `303465c` (cycle 4 add-from-recs picker + dashboard quick-actions + forecast P0-J) → `eb76918` (cycle 5 variance display + signal #21 consumption) → `012dd16` (cycle 6 bulk approve + URL cleanup) → **`52b63ab` (cycle 7 /dashboard/v2 MVP — Tom priority #8)**. Cycle 8 W2 work (`/admin/holidays` page) is on disk but uncommitted (rate-limit interrupt).
- Canonical main tip advanced from `8c22ce9` → `bafbcb0` → `821dfd5` (cycle 1 Gate 5 from_plan #18) → `069f136` (cycle 1 dashboard v2 spec) → `c6f29e2` (cycle 2 DCT2 + variance contract) → `34e36ee` (cycle 2 GAP-1 v_critical_today #19) → `16a18f0` (cycle 3 add-from-recs endpoint #20) → `2bd2a76` (cycle 3 inventory-flow planned-inflow contract) → `7fe31c0` (cycle 4 rec-detail DTO ext #21) → `1838512` (cycle 5 admin/holidays contract) → `0679f5c` (cycle 5 v_production_plan_slippage #22) → `54db614` (cycle 5 admin/holidays contract revised) → `528c7ce` (cycle 6 dashboard handlers #23+#24) → `c1fda82` (cycle 7 admin/holidays CRUD #25) → `0679f5c→0679f5c` (cycle 7 rehearsal test plan) → **`44ac489` (cycle 8 PO-attached GR enhancement spec)**. Cycle 8 W1 work (signal #26 HolidaysArchivedFilter migration 0120) is on disk but uncommitted (rate-limit interrupt).
- **Mode B-Planning-Corridor amendment** added to EXECUTION_POLICY.md 2026-05-02 (Tom-authorized cycle 1 governance Q1.A): scopes pan-portal authoring on planning corridor surfaces. Cycle 7 amendment add: `/dashboard/v2` added to allowed surfaces per DCT2-8 default. Coexists with Mode B-AMMC and Mode B-Portal-Refactor. Expires when 11 audit P0 findings on planning corridor surfaces all close.
- **DCT2 resolution pack**: all 8 DCT2-1..DCT2-8 items classified cycle 2 — 0 items blocking. Dashboard v2 §4.1 + §4.4 blocks shipped cycle 7; remaining 7 sub-blocks render honest "Awaiting read-model" placeholder cards.
- **Audit P0 status (cycles 2-7)**: 8 of 11 closed — P0-A (production-actual cycle 2), P0-B (runs detail cycle 3), P0-C (rec drill-down cycle 3), P0-E (runs list cycle 3), P0-F (dashboard quick-actions cycle 4), P0-I (run freshness cycle 3), P0-J (forecast active callout cycle 4) + exception action deep-link fix cycle 3. Still open: P0-D (PO `[po_id]` Hebrew banner — needs governance carve-out + Tom POGR-2), P0-G (production-simulation IDB false green — Tom decision PSDP-1..4 queued), P0-H (admin/holidays — backend done cycle 7 #25; consumer filter on disk cycle 8 #26 uncommitted; portal page on disk cycle 8 uncommitted; rate-limit-interrupted).
- **W4 contracts authored cycles 1-8 (8 specs total)**: dashboard control-tower v2 coverage (cycle 1), variance display (cycle 2), PO→GR readiness (cycle 3), DCT2 resolution pack appended (cycle 2), inventory-flow planned-inflow overlay (cycle 4), /admin/holidays CRUD (cycle 5), production-simulation runtime decision pack (cycle 6), whole-system rehearsal test plan (cycle 7), PO-attached GR enhancement (cycle 8).
- **Cycle 8 partial state — RESOLVED 2026-05-08 (Phase 8 Wave 0 reconciliation)**: Verified post-interrupt closure: W1 backend committed as `be2fced` "feat(holidays): consumer-side archived_at filter on fn_compute_daily_fg_projection (signal #26)" landing migration `0120_holidays_il_archived_filter.sql` + pgTAP + checkpoint + inspection scripts on canonical main. W2 portal committed as `bf4a744` "feat(admin/holidays): live CRUD page consuming signal #25 + #26 (cycle 8 closure)" landing the `/admin/holidays` page changes (page.tsx, route.ts, [holiday_date]/, bulk-import/). Signal #26 `RUNTIME_READY(HolidaysArchivedFilter)` was already on file. Cycle 8 is closed; subsection retained as audit trail of the 2026-05-02 rate-limit interrupt and its resolution.
- **No planned production currently affects stock_ledger, current_balances, or any projection.** A4 LOCKED in `fn_compute_fg_net_requirements` (FG netting inbound = 0) remains in force.
- **No autonomous ordering, no autonomous production.**
- A3 LOCKED (`v_planning_demand` buckets all open orders to current ISO week) remains in force.

**T3A audit-log artifacts (inert):** 3 `change_log` rows from the T13 cross-transaction runtime test reference plan_id `875718c3-a95a-4e69-a158-a1fc8f868bd0` (PRODUCTION_PLAN_CREATED + EDITED + DELETED, snapshot `t3a-T13fix`). The corresponding `production_plan` row was deleted at test cleanup; the `change_log` rows remain because that table is append-only by design (`change_log_append_only_guard()` from migration 0025). No operational impact.

**Locked boundaries during this corridor:**
- `stock_ledger` semantics, `current_balances` triggers, `balance_anchors`
- `fn_compute_fg_net_requirements`, `fn_compute_component_net_purchase`, `v_planning_demand`
- A3/A4 locked assumptions, forecast freeze/publish semantics
- Auth model, Excel/import rules
- Open PO offset behavior inside the planning engine

---

## Last calibration
**Date:** 2026-04-27 (Planning Tranche 3 CLOSED end-to-end: W1 backend + W2 portal Mode B both PASS; signal #17 emitted; Manual PO portal merged to main as commit `92efbb3` 2026-04-26).

### Ralph Loop corridor status (2026-04-25 — RE-AUDIT COMPLETE)

**Portal main tip:** `92efbb3` (2026-04-26 — merge of feature/master-data-ux-overhaul into main; brings manual PO creation portal `/purchase-orders/new` live on Vercel; nav conflict resolved with main's Inventory Flow state). Portal deployed to Vercel automatically on push.
**Backend Railway tip:** `1209596` (deployed 2026-04-27 as Railway deployment `ef03b588-5da9-4e8a-909d-b081b65746a9`; adds Tranche 3 blockers endpoint on top of Tranche 2 rec-detail + Tranche 1a time-aware PO netting). `GET /health → {"ok":true}` confirmed; `GET /api/v1/queries/planning/blockers` HTTP 401 without auth confirmed; HTTP 200 with real Supabase JWT confirmed 2026-04-27.

**Re-audit findings (2026-04-25):**
- All exception deep links (`resolveExceptionDeepLink()`) verified to route to real pages: `/admin/sku-aliases`, `/admin/integrations`, `/purchase-orders`, `/admin/sku-map` all exist and are API-wired.
- Tom Tax: all 5 daily operations (open POs, GR, FG shortage projection, exceptions inbox, production actual) doable from portal without SQL. CLEAN.
- Gap found + fixed: `/planning/weekly-outlook` was missing from sidebar nav manifest. Added (`81d6c7f`).
- Admin screens: all 9 screens (items, components, boms, suppliers, supplier-items, planning-policy, sku-aliases, sku-map, jobs, integrations) are API-wired with real fetch calls. No mock data.
- Cross-corridor: PO data feeds weekly outlook via `purchase_order_lines.item_id` FK (FG BOUGHT_FINISHED items only); A4 locked (engine uses zero FG inbound; PO is informational overlay only). No regression.
- Production actual uses BOM pinned version at snapshot time; weekly outlook uses planning run data. No overlap or conflict.

**Completed corridors (post-Gate-5 hardening + re-audit):**

| Corridor | Status | Portal tip | Backend evidence |
|----------|--------|------------|-----------------|
| PO | CLOSED | d73199b | migrations 0049-0057, 0082, 0083, 0084; 58+pgTAP; 14/14 node:test |
| Production Execution | CLOSED | bd93ec4 | 13/13 backend tests; form live-wired; 7 E2E specs |
| Calendar / Gantt | DONE | f4aca4f + dfd2c6b (portal main) / 9ae6683 (backend main) | `/planning/inventory-flow` daily control tower live on Vercel (redirects weekly-outlook); W1 handler stack `api/src/inventory/handler.flow.ts` deployed Railway; sidebar nav entry "Inventory Flow" |
| PurchaseOrders-manual portal | DONE (feature/master-data-ux-overhaul — pending merge to main) | 47de463 | W1 migrations 0093-0096 on gt-factory-os/main; backend node:test 12/12; portal: /purchase-orders/new, source column, detail banner |
| Planning Tranche 1 + Tranche 2 portal | DONE | backend `4b0f5eb` (gt-factory-os/main); portal `2146b84` (window2-portal-sandbox/main) | W1: E1/E2/E6/E5 fixed + time-aware PO netting (migrations 0101–0110); rec-detail endpoint 9/9 node:test; RUNTIME_READY(Planning-Tranche1) + RUNTIME_READY(Planning-Tranche2-RecommendationDetail) emitted 2026-04-26. W2: RecommendationDrillDown surface (Hebrew labels, mobile cards, 9 files) PASS — HTTP 200 against live endpoint verified 2026-04-26. |
| Planning Tranche 3 — Unresolved Demand / Blockers | DONE (2026-04-27) | backend `1209596` (gt-factory-os/main); portal `e7dce27` (window2-portal-sandbox/main) | W1: `GET /api/v1/queries/planning/blockers` — 12/12 node:test against live pooled PG17; deployed Railway `ef03b588`; HTTP 401 without auth + HTTP 200 with JWT both confirmed; PBR-1/2/3/4 all resolved (PBR-1 Tom-locked total horizon + urgency fields; PBR-4 W1-resolved 95% via live DB inspection — two live shapes normalized via display_id/display_name/display_kind). W2: 13 files / 1446 insertions; route `/planning/blockers` (Tom-locked); page title "חסמים בתכנון"; Hebrew label maps exhaustive Tom-locked verbatim; validation 3/3 PASS (tsc/build/lint:urls); Vercel 307→/login confirmed live. RUNTIME_READY(Planning-Tranche3-Blockers) emitted as signal #17. Manual-PO sync-closure follow-on now unblocked. |
| External Boundaries | DONE | be57fb0 | exception deep links; "Fix this →" button; 17-category explanations |
| Exceptions / Control Tower | DONE | be57fb0 | dashboard 7/7 blocks live; inline Acknowledge/Resolve actions |
| Admin Self-Sufficiency | DONE | be57fb0 | all admin screens real-API-wired |

**Date:** 2026-04-23 (infrastructure validation + docs authored; supersedes 2026-04-18 calibration).

### Layer 0 validation — SUBSTANTIALLY COMPLETE (2026-04-23)

**Infrastructure (all confirmed 2026-04-23):**
- Railway API: `GET /health` → HTTP 200, `{"ok":true}`
- Railway env vars: `DATABASE_URL_POOLED` (pooler→Supabase), `SUPABASE_URL=https://rvadsozabmxkkrktwgnv.supabase.co`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `NODE_ENV=production`, `ENABLE_DEV_SHIM_AUTH=false` — all set
- Vercel portal: `https://gt-factory-os-portal.vercel.app/` → HTTP 200; `/dashboard` → 307 → `/login` (middleware gate working)
- Vercel env vars: `API_BASE=https://gt-factory-os-api-production.up.railway.app`, NEXT_PUBLIC_* vars all present in Production

**First live production event (2026-04-23 05:40:22 UTC):**
- `movement_id`: `429b94d5-c628-4e7f-bc2d-76d433143620`
- `movement_type`: `WASTE_POSTED`
- `item_id`: `RAW-WHISKEY`, `qty_delta`: `-0.01`, `post_status`: `POSTED`
- `idempotency_key`: `WA:3946db0f-38cf-4b44-bb5c-7e0226bacb84`
- `reported_by_user_id`: `0db008a9-05e3-4521-8b30-42e5d444818d` (tom@gteveryday.com, role=admin) ✓
- **Auth chain confirmed**: Tom submitted the form while authenticated; JWT resolved correctly to app_users row

**Closed-loop verification (all via direct DB query):**
- Step 5a — Ledger write: ✓ WASTE_POSTED row confirmed
- Step 5b — Projection update: ✓ `current_balances.calculated_on_hand=-0.01` for RAW-WHISKEY, `last_refreshed_at` = same as `posted_at` (synchronous trigger confirmed)
- Step 5c — Operator visibility: Tom confirmed via portal (submitted the form, saw success) — portal-side verification
- Step 5d — Planning input: ✓ `v_rm_stock_export` shows RAW-WHISKEY at -0.01; planning engine reads `current_balances` → next run will use updated value. 12,057 forecast_lines present. Most recent completed planning run: 2026-04-21 22:17 (pre-dates today's event — a new run post-event is recommended to confirm full round-trip).
- Step 5e — rebuild_verifier(): ✓ = 0 (confirmed after event)
- Step 5f — Exception path: ✓ CONFIRMED 2026-04-23 — exception `7283a2d2` (positive_adjustment, RAW-VODKA, qty=50, status=open); form_submission `56c1be71` (pending, NOT posted); `current_balances` RAW-VODKA=0.00 unchanged; zero ledger writes confirmed

**noted issue — fix deployed:** `reported_by_snapshot` was `null` on the live event (display_name snapshot not captured). Fix committed `9633ebc` and deployed to Railway 2026-04-23 (deployment `c3d66703`, status=SUCCESS, health=ok). All future ledger writes from waste-adjustments (auto-post + approval path), goods-receipts, and production-actuals will now populate `reported_by_snapshot` correctly. The 2026-04-23 live event retains `null` as a historical artifact — acceptable.

**Total ledger movements to date:** 262 (includes 2026-04-17 smoke tests + today's first real event)

**Layer 0 verdict: CLOSED (2026-04-23)**
All 7 exit criteria confirmed: infrastructure healthy, first real stock event posted (WASTE_POSTED, `429b94d5`), ledger→projection chain verified, rebuild_verifier=0, planning round-trip confirmed (run_id=`0b53afb8`), `reported_by_snapshot` fix deployed (`9633ebc`, Railway `c3d66703`), exception/approval path confirmed (step 5f: exception `7283a2d2` fired, form_submission `56c1be71` pending NOT posted, `current_balances` unchanged). Tom declared CLOSED 2026-04-23.

**Permanent docs authored (2026-04-23):**
- `PRODUCTION/docs/operational_dataflow_blueprint.md`
- `PRODUCTION/docs/gap_registry.md`
- `PRODUCTION/docs/false_green_registry.md`
- `PRODUCTION/docs/tranche_log.md`
- `PRODUCTION/docs/lessons_learned.md`

**Date:** 2026-04-18 (prior Tom-authoritative calibration; all gate status below reflects 2026-04-18; superseded above by 2026-04-23 Layer 0 validation).

## Overall completion
**Overall runtime platform: ~60–70%.**

> **Stale-calibration note (2026-05-08, Phase 8 Wave 0):** This range was last set in the 2026-04-23 calibration (line 113). It does NOT yet reflect the Shopify External Boundary v2 phase progression (Phase 0+1+2+3+4 landed 2026-04-30…2026-05-08; Gate E in execution at backend tip `bcb2d0f`), nor the Professional Stock-Truth Monitoring corridor pre-cutover prep (2026-05-07 plans), nor the post-count cutover scheduled for 2026-05-10. Refresh deferred to a Phase 8 Wave 5 calibration step where Tom sets the new range based on evidence; Phase 8 Wave 0 only stamps the staleness, not the value.

Gate 3 now CLOSED on CLAUDE.md §"Gate model" literal exit criteria (parity, idempotency, count-freeze race, minimal Exceptions Inbox) per `gate3_closure_decision_pack.md` + verifier PASS. This is an interpretation calibration, not a scope change: the contract-specified Gate 3 exit is met; the distinct operator-rollout milestone (first live production stock event) is tracked separately. Contract-pack maturity and DB-layer maturity remain higher than integration-runtime maturity. Lead with this range unless a later dated calibration supersedes it.

**Per-gate ranges (Tom-authoritative, override governance defaults):**
- Gate 1 — Alignment / Contracts: ~95–100%
- Gate 2 — Foundation / Masters / Admin: ~70–85%
- Gate 3 — Stock Truth: ~95–100%
- Gate 4 — Operational Mirrors / Forecasting: ~10–20%
- Gate 5 — Planning / Recommendations: ~0–5%

## Gate-by-gate runtime status

### Gate 1 — Alignment / Contracts — LIVE_VERIFIED (artifacts exist, internally consistent)
Architecture map, schema map, portal module map, form definitions, integration contracts, migration phases, validation gates, rollback logic — all written and reconciled. Runtime contracts locked for Goods Receipt, Waste / Adjustment, and Physical Count. `freeze_guard_contract.md` added alongside Physical Count to govern count-freeze cross-form interactions.

### Gate 2 — Foundation / Masters / Admin — LIVE_VERIFIED (DB side)
- Migrations 0001 / 0002 / 0003 / 0005 applied to live DB
- 93 / 93 pgTAP assertions green on original masters pack
- 1,002 rows imported across 8 tables (suppliers = 43, bom_head = 68, items = 68, components = 145, bom_version = 68, bom_lines = 420, planning_policy = 5, supplier_items = 185)
- Idempotency confirmed
- `app_users` table live via 0005 + 0015 late-FK wire-up

**Runtime admin CRUD:** D4 Master Maintenance 5 admin screens committed in W2 portal as mocked + reconciled against locked SQL schema (Waves 1–5b); not yet wired to the API boundary end-to-end.

### Gate 3 — Stock Truth — PARTIAL. Tom-locked 2026-04-30. LionWheel pick-reconciliation chain repair corridor in flight; corridor is bug-fix within Gate 3, not a ledger-semantics change. Gate 3 returns to CLOSED only when the chain repair lands and parity holds.

**Prior closure evidence (2026-04-18, superseded by PARTIAL status above; preserved as audit trail):** Closed on CLAUDE.md §"Gate model" literal exit criteria (parity, idempotency, race, minimal Exceptions Inbox), per `docs/gate3_closure_decision_pack.md` (2026-04-18, executor-w1) and verifier PASS on substance. Documentation-integrity defects in the pack (§2.4 and §3 item 5 harness-state citations) repaired 2026-04-18 by executor-w1 (evidence pack `docs/gate3_exceptions_inbox_evidence.md` authored; `RUNTIME_READY(ExceptionsInbox)` signal emitted; §3 item 5 rewritten as explicit UNRESOLVED). Commit hygiene tracked separately: Gate 3 evidence artifacts still uncommitted on `main` (see caveat below).

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
| **Goods Receipt** | `RUNTIME_READY(GR)` **not emitted**; Gate 3 closure reached via direct handler evidence + live smoke probe path per `gate3_closure_decision_pack.md` rather than via a GR signal | Handlers (`api/src/goods-receipts/{handler,route,schemas}.ts`), runtime contract, pgTAP `goods_receipt_runtime.test.sql`, live-verification pack (`gate3_gr_live_verification_pack.md`), and preflight script (`verify_gr_preflight.ts`, 14/14 probes pass) all present and cited in closure pack |
| **Waste / Adjustment** | `RUNTIME_READY(WasteAdjustment)` emitted **2026-04-17T16:54:13Z** by executor-w1 | Evidence: `waste_adjustment_runtime.test.sql` (33/33 pgTAP green); pass-3 smoke matrix (7 cases — auth + Zod + auto-post + idempotent replay + 2 pending categories + ITEM_TYPE_MISMATCH); pass-3b follow-up matrix (13 cases — role-gate, approve cross-user, self-approval 409, NOT_PENDING, reject, freeze-guard refusal, freeze-release). `rebuild_verifier()` = 0 after all 20 cases. All six §3.3 items of `waste_adjustment_runtime_contract.md` closed |
| **Physical Count** | `RUNTIME_READY(PhysicalCount)` emitted **2026-04-17T19:21:41Z** by executor-w1 | Evidence: `physical_count_runtime.test.sql` (31/31 pgTAP); PC HTTP matrix (18 cases + 1 bug-fix re-verification — auth 401, role-gate 403 viewer+operator, GET /open 200 + idempotent_open, 201 auto-post, 201 idempotent_replay after handler patch, 202 pending, 200 admin approve + planner reject + operator cancel, 409 COUNT_ALREADY_OPEN, 409 COUNT_FREEZE_ACTIVE on Waste-during-PC-holding, 409 NOT_PENDING). All five `count_freezes` terminal states exercised (`consumed_auto` / `consumed_approved` / `released_rejected` / `cancelled` / `expired`). Anchor history integrity: 4 rows for 4 replacements. Blind-count invariant: snapshot_quantity never exposed in GET /open. `rebuild_verifier()` = 0 after all cases. Bug found+fixed during verification: handler now short-circuits to idempotent replay via top-of-handler `form_submissions` lookup before the snapshot SELECT |

**Minimal Exceptions Inbox (Gate 3 literal criterion #4):** 16 named node:test E1–E16 green in `api/test/exceptions.test.ts`; W2 sandbox Playwright real-harness spec `exceptions-inbox-real.spec.ts` exists at `c:/Users/tomw2/Projects/window2-portal-sandbox/tests/e2e/`. `RUNTIME_READY(ExceptionsInbox)` signal emitted 2026-04-18T00:00:00Z by executor-w1; evidence pack at `docs/gate3_exceptions_inbox_evidence.md`.

**W2 mode (authoritative source: `.claude/state/active_mode.json`):** W2 current mode = **A** as of 2026-04-27T08:18:00Z. Most recent Mode B exit: Planning-Tranche3-Blockers (commit `e7dce27` on window2-portal-sandbox/main, 2026-04-27; live JWT smoke HTTP 200 against Railway `ef03b588` confirmed; Vercel 307→/login confirmed; route `/planning/blockers` Tom-locked). Prior Mode B exits: Planning-Tranche2-RecommendationDrillDown (1184bcf + fix 2146b84, 2026-04-26); InventoryFlow (f4aca4f + dfd2c6b, 2026-04-26); PurchaseOrders-manual (47de463 on feature/master-data-ux-overhaul — merged to main as `92efbb3` 2026-04-26); PurchaseOrders-po-list-action (48720d1, 2026-04-25); Portal-Refactor Tranches A–E + Ralph Loop corridors (2026-04-21–25). Per `EXECUTION_POLICY.md`, only one form may be in Mode B at a time.

**Main-tip progression:** main tip advanced to `9633ebc` as of 2026-04-23 (fix: populate reported_by_snapshot on all stock_ledger writes; deployed to Railway via `railway up --detach`, deployment c3d66703). Prior tip: `ac75ed1` (AMMC Slice 6 backend, 2026-04-21). Interim tranches since `8c22ce9` (Gate 5 Phase 9 PO bridge, 2026-04-19): Gate 5 Phase 9 completion, Production Endgame Phase A3 (ProductionActual runtime) / Phase E3 (Shopify FG sync runtime) / Phase E4 (Green Invoice supplier-price ingest runtime), and AMMC Slices 1–6. Prior `8c22ce9` reference preserved for historical context; `ac75ed1` is the live tip. Gate-4-and-earlier commits (7aa9090, 7a80af6, a99c975, 04762bb, 435bf3e, 837d369, 2cd2a97, c240061, 422e146) landed through Gate 4 closure tip `422e146`. Gate 5 tranche (14 commits, all landed on `main`):

  - `51724cc` gate5: phase 0 entry contracts + integration_sku_map implementation note
  - `381b60e` gate5: phase 1 canonical demand layer — integration_sku_map + v_planning_demand + exceptions
  - `9eefbda` gate5: phase 2 policy readiness audit + blocker matrix + policy seed
  - `da534fe` gate5: phase 3 planning run substrate — 4 tables + status transitions + audit triggers
  - `ff521bf` gate5: phase 4 net requirements engine — FG netting + BOM explosion + supply netting
  - `15ccbc2` gate5: phase 5 purchase recommendations engine
  - `3a4bfa3` gate5: phase 6 production recommendations engine
  - `0852f48` gate5: phase 7 planning run orchestration (7A DB + 7B API + 7C reproducibility) complete + RUNTIME_READY(PlanningRun) emitted
  - `992e4ec` gate5: phase 7.5 planning review backend — 5 endpoints (3 GET + 2 POST) + approval audit columns
  - `dd50396` gate5: phase 9 PO inspection gate — deferred; Gate 5 closes at Phase 8
  - `c60d8f7` gate5: CLOSURE DECISION PACK — Gate 5 substantively closed at Phases 0-8 per A10 + A11
  - `143aa5f` gate5-housekeeping: signal-registry reconciliation + CURRENT_STATE to Phase 8 closure + Phase 9 prep
  - `a63bf99` gate5-phase9: W4 PO contract pack — 4 requirements-only contracts for purchase_orders substrate
  - `8c22ce9` gate5: phase 9 PO bridge — migrations 0049-0057 + handler + E2E proof + RUNTIME_READY(PurchaseOrders)

**W2 sandbox tip:** advanced from `6779d27` (Forecast MVP) to `4f2d325` (PlanningRun MVP `/planner/runs` canonical review surface).

Intentional untracked items remain: `.claude/` (harness state, forbidden), `.mcp.json` (Tom disposition pending), `docs/gate_commit_tranche_checkpoint.md` (prior-cycle governance artifact), `portal/test-results/` + `test-results/` (build artifacts).

Full tree coherent through `8c22ce9`. Rollback granularity per plan §10: per-commit reverse order (see `docs/gate5_closure_decision_pack.md` §8 for full 18-step Gate-5 rollback sequence including Phase 9 PO bridge unwind if ever required).

Remote status: origin/main push cadence is Tom-authorized (not tracked here per governance scope).

Governance: commit stagnation CLOSED as of 2026-04-18; Gate 5 tranche committed cleanly across cycle.

**RUNTIME_READY signals (17 total, authoritative source `.claude/state/runtime_ready.json`):** (1) WasteAdjustment (2026-04-17), (2) PhysicalCount (2026-04-17), (3) ExceptionsInbox (2026-04-18), (4) Forecast (2026-04-18), (5) LionWheel (2026-04-18), (6) freshness_check (2026-04-18), (7) PlanningRun (2026-04-19), (8) PurchaseOrders (2026-04-19), (9) ProductionActual (2026-04-21T17:05), (10) GreenInvoice (2026-04-21T18:45), (11) Shopify (2026-04-21T19:05), (12) RalphLoopReAudit (2026-04-25T00:30), (13) PurchaseOrders-manual (2026-04-26T00:00), (14) InventoryFlow (2026-04-26T10:55), (15) Planning-Tranche1 (2026-04-26), (16) Planning-Tranche2-RecommendationDetail (2026-04-26), (17) Planning-Tranche3-Blockers (2026-04-27 — endpoint `GET /api/v1/queries/planning/blockers`, commit `1209596`, Railway deployment `ef03b588`, 12/12 node:test against live pooled PG17). A stale repo-local file at `gt-factory-os/.claude/state/runtime_ready.json` does not override the governance file (per `feedback_harness_state_authoritative.md`: governance path is authoritative on signals).

**Gate 3 exit CLOSED** on CLAUDE.md §"Gate model" literal four exit criteria per `gate3_closure_decision_pack.md` + verifier PASS on substance. Interpretation change this calibration: exit criteria are the four items literally named in CLAUDE.md (parity within tolerance, idempotency, count-freeze race, minimal Exceptions Inbox) — NOT "live production form traffic", which is an operator-rollout milestone distinct from the contract-specified gate exit. Post-exit open items: (a) commit-hygiene tranche landing 20 Gate-3 artifacts on `main`; (b) eventual first production-traffic event (operator rollout milestone, separately tracked).

### Gate 4 — Operational Mirrors / Forecasting — CLOSED (EC-1 LionWheel + EC-3 freshness_check; Forecast runtime live)
Gate 4 closure tip on main: `422e146` (2026-04-18). Contract pack: 12+ files in `docs/integrations/`. Runtime layer CLOSED on:
- **EC-1 LionWheel mirror** — Option B ratified: Supabase Edge Function `factory_os_jobs` (Deno, `npm:pg` + `npm:zod`) + `pg_cron` → `pg_net` invocation; migrations 0030/0031/0032; break-glass respected; 29/29 pgTAP green. `RUNTIME_READY(LionWheel)` emitted 2026-04-18T20:33Z; evidence at `docs/gate4_option_b_closure_checkpoint.md`.
- **EC-3 freshness_check** — 7-producer state map with self-silence path pgTAP green (5/5); heartbeat producer added (warn_min=10 / crit_min=25); auto-resolution path observed end-to-end. `RUNTIME_READY(freshness_check)` emitted 2026-04-18T20:33Z.
- **Forecast runtime** — G-08 FULLY CLEAR: 4 writes + G.4 open-cold-start + 5 reads + F11 cross-version drift at handler layer; pgTAP 0022 10/10, forecasts_handler 27/27, forecasts_reads 13/13 green. `RUNTIME_READY(Forecast)` emitted 2026-04-18T19:30Z.

Follow-on Gate 4 items (NOT runtime blockers, carried forward):
- G-07 forecast audit-trigger implementation against `change_log_contract.md` (commissioned by W4 in 04762bb)
- G-10 forecast.publication integration wiring (producer registered in freshness contract §2 by W4)
- LionWheel demand model: hybrid resolver live (2026-04-23, `rows_unknown_sku=0`); 330/404 lines (81.7%) resolved; 74 unresolved lines remain (bundles 44 + held 5 + non-catalog ~23 + malformed 2); planning demand flowing for 15+ items. Excluded demand is a planning-completeness gap, not a system failure. Stale exceptions: 65 open = 41 stale + 24 true. Bundle policy tranche pending (Loop 2). JASM/PNMM held for Tom.
- MC-U2 FG_OUT bridge enablement — contingent on SKU alias saturation

### Gate 5 — Planning / Recommendations — **FULLY CLOSED AT PHASES 0–9**
Per `docs/gate5_closure_decision_pack.md` (2026-04-19 updated post-Phase-9, executor-w1) at repo tip `8c22ce9`:

- **Closure disposition:** FULLY CLOSED at Phases 0–9 per plan amendment A11 (Gate 5 full closure scoped to Phases 0–9) + CLAUDE.md §"Gate model" literal exit criteria. Prior A10 fallback path no longer operative — Phase 9 landed. Phase 10 cost rollup is post-closure stretch per A11.
- **Phases 0–9 complete:**
  - Phase 0: entry contracts (`gate5_input_contract.md`, `gate5_policy_keys_contract.md`, `gate5_integration_sku_map_implementation_note.md`)
  - Phase 1: canonical demand layer (migrations 0033/0034/0035; `api_read.v_planning_demand`; 35/35 pgTAP)
  - Phase 2: policy readiness audit + blocker matrix (migration 0036; 14/14 pgTAP)
  - Phase 3: planning run substrate (migrations 0037/0038/0039; 53/53 pgTAP; A5 mandatory CHECKs preserved)
  - Phase 4: net requirements engine — FG netting + BOM explosion + supply netting (migrations 0040/0041/0042; 35/35 pgTAP)
  - Phase 5: purchase recommendations engine (migration 0043; 17/17 pgTAP; A6 deterministic supplier selection)
  - Phase 6: production recommendations engine (migration 0044; 16/16 pgTAP; A7 feasibility enum + batch-size fallback preserved)
  - Phase 7: planning run orchestration — 7A DB + 7B API + 7C reproducibility (migrations 0045/0046; 16/16 pgTAP + 3/3 pgTAP + 8/8 node:test + 1/1 byte-equal reproducibility proof)
  - Phase 7.5: planning review backend — 5 endpoints (3 GET + 2 POST), approval audit columns (migrations 0047/0048; 23/23 node:test)
  - Phase 8: W2 canonical review surfaces MVP `/planner/runs` (8/8 Playwright real-HTTP E2E green in sandbox tip `4f2d325`)
  - Phase 9: recommendation → PO bridge (migrations 0049–0057; 58/58 pgTAP; 14/14 node:test including 4/4 end-to-end approve → convert → partial GR → completing GR → RECEIVED with full `change_log` trail; `RUNTIME_READY(PurchaseOrders)` emitted 2026-04-19T08:00:00Z; Tranche 5 `goods_receipts.po_id` bare-text debt resolved via 0053 FK wire)
- **Phase 10 NOT ATTEMPTED:** **post-closure stretch per A11 — not required for Gate 5 closure.** Cost rollup matches manual reconciliation remains for a future cycle. Reserved migrations `0058+`.
- **EC disposition (CLAUDE.md §Gate model Gate 5):** EC-1 reproducibility CLOSED (Phase 7C byte-equal); EC-2 human approval before PO **FULLY CLOSED** (Phase 7.5 + Phase 8 surfaces + Phase 9 programmatic enforcement via `fn_convert_recommendation_to_po` NOT_APPROVED 409 gate with end-to-end test proof); EC-3 Production Actual NOT-IN-GATE-5-V1-SCOPE (A13 judgment, locked CLAUDE.md §"Production reporting v1" semantics preserved); EC-4 cost rollup DEFERRED under A11 (post-closure stretch, not required).
- **W4 contract pack consumed verbatim (commit `a63bf99`):** `docs/integrations/purchase_orders_schema_contract.md`, `purchase_order_lines_contract.md`, `purchase_order_status_lifecycle_contract.md`, `gr_to_po_linkage_contract.md`. Zero invented contract values; zero silent healing.

## What is complete / partial / missing

**Complete (LIVE_VERIFIED):**
- Gate 1 artifact set (incl. GR / Waste / PC runtime contracts + freeze_guard_contract)
- Gate 2 DB-side foundation (schema, migrations, imports, app_users)
- Gate 3 DB-side stock-truth layer (ledger, anchors, projection, rebuild_verifier, parity gate, exceptions, count_freezes, projection boundary fix)
- Gate 3 form-runtime evidence on CLAUDE.md literal exit criteria — parity, idempotency, race, minimal Exceptions Inbox — per `gate3_closure_decision_pack.md` (2026-04-18) + verifier PASS on substance
- Gate 4 runtime layer — LionWheel mirror (Option B Supabase Edge Function + pg_cron + pg_net), freshness_check with self-silence, forecast API handler stack (4 writes + 5 reads + F11), forecast.publication producer — per Gate 4 closure tip `422e146`
- Gate 5 planning engine Phases 0–9 — canonical demand layer, policy readiness, planning run substrate, net requirements (FG netting + BOM explosion + supply netting), purchase recommendations, production recommendations, planning run orchestration with reproducibility proof, planning review backend, W2 MVP `/planner/runs` canonical surface, recommendation → PO bridge with end-to-end approve→convert→receive proof — per Gate 5 closure tip `8c22ce9`
- W4 contract pack (12 Gate-4 files + 5 Gate-5 files + 4 Phase-9 PO contract files; requirements-only)

**Partial:**
- Gate 2 admin runtime — **RESOLVED 2026-04-25**: all admin screens (items, components, boms, suppliers, supplier-items, planning-policy, sku-aliases, sku-map, jobs, integrations) are wired to real API endpoints. No IDB/mock fixture data.
- Gate 3 follow-on operational items (NOT exit blockers): (a) GR `RUNTIME_READY` signal (Gate 3 closed via direct-evidence path without it); (b) W2 Mode B exit finalization for WasteAdjustment
- Gate 4 follow-on items (NOT runtime blockers): G-07 forecast audit-trigger against `change_log_contract.md`; G-10 forecast.publication integration wiring
- W2 canonical portal — Mode B for Waste, Forecast MVP, PlanningRun MVP authored; cross-run purchase/production list views deferred (per Phase 8 stop-condition allowance); Convert-to-PO button surface on `/planner/runs/[id]` deferred to optional follow-on Mode B dispatch

**Missing:**
- LionWheel demand completeness gap — 74 unresolved lines / 24 distinct SKUs remain outside planning: bundles (GTSET-*, 9 SKUs, 44 lines — see bundle-policy tranche), held aliases (GTCC-MUZ-JASM-1L + GTCC-MUZ-PNMM-1L, Tom confirmation needed), non-catalog (~13 SKUs, ~25 lines), malformed/test (2). Stale exception cleanup: 41 of the 65 open exceptions are now-resolvable historical noise — admin can bulk-close from exceptions inbox. UNRESOLVED-7 CLOSED: 37 exact legacy_sku direct matches confirmed by live DB (41 resolved distinct - 4 aliases).
- Gate 5 Phase 10 cost rollup (post-closure **stretch** per A11 — not missing in a gate-blocking sense; reserved migrations `0058+`)
- MC-U2 FG_OUT bridge enablement (contingent on SKU alias saturation)
- `RUNTIME_READY(GR)` signal (harness-durability improvement; not a gate exit blocker)
- `supplier_items.current_price` column — **RESOLVED 2026-04-24**: exists as `std_cost_per_inv_uom` (migration 0075, applied); `fn_convert_recommendation_to_po` uses it (migration 0083, applied); 165/203 supplier_items have non-null price. PO lines now get real prices on conversion.
- GR reversal → PO `received_qty` decrement path — **RESOLVED 2026-04-24**: migration 0082 `trg_stock_ledger_gr_reversal_po_decrement` applied and verified. UNRESOLVED-GP-1 CLOSED.
- Phase 9.1 rebuild-verifier for PO header parity (deferred per UNRESOLVED-LC-5)
- W2 minimal Convert-to-PO button surface on `/planner/runs/[id]` (optional follow-on Mode B dispatch)
- Shopify sync runtime
- Green Invoice ingest runtime
- Production Actual form runtime — **RESOLVED 2026-04-25**: form exists at `/ops/stock/production-actual`, live-wired, 13/13 backend tests pass, UX hardened
- Dashboard runtime surfaces: **RESOLVED 2026-04-25** — all 7 blocks live: critical signals (inbox total, exceptions, planning run, break-glass), stock truth + parity, integration freshness, jobs 24h, forecast, RUNTIME_READY registry, quick actions
- Dashboard KPI aggregation endpoints (runs-today, last-movement) — backend-blocked; new API endpoints needed

## Current critical path

**All v1 gates CLOSED.** Gate 5 fully closed at Phases 0–9 per A11 + CLAUDE.md §"Gate model" literal exit criteria (main tip `8c22ce9`, 2026-04-19). No further v1 gates are unlocked by this closure.

**Post-Gate-5 priorities (not gate-blocking):**
- Phase 10 cost rollup (stretch per A11) — post-closure economics layer; reserved migrations `0058+`
- SKU alias seeding workflow (operational; unblocks MC-U2 FG_OUT bridge enable)
- MC-U2 FG_OUT bridge enable (contingent on SKU alias saturation)
- portal_universe fake-session seed on pooled DB
- `.mcp.json` disposition (Tom-pending)
- W2 minimal Convert-to-PO button surface (optional follow-on Mode B dispatch cycle)
- `supplier_items.std_cost_per_inv_uom` (was: `current_price`) — RESOLVED 2026-04-24 (see above)
- GR reversal → PO `received_qty` decrement path — RESOLVED 2026-04-24 (migration 0082 applied)
- Phase 9.1 rebuild-verifier for PO header parity (UNRESOLVED-LC-5)

## Open UNRESOLVED items (must not be silently healed)

Any activation that would otherwise touch one of these items must emit `assumption_failure` and surface the gap.

- **LionWheel order line schema, stable identifiers, and status lifecycle** — requires live API inspection; no field name may be guessed
- **Green Invoice line-item schema and supplier-SKU availability** — requires live API inspection; auto-creation of components forbidden until resolved
- **Shopify cancellation / refund path in GT's specific order flow** — reconciliation behavior undefined until inspected
- **Whether customer-specific pricing exists in current operations** — until confirmed, customer pricing is not modeled
- **PBR-1 — RESOLVED 2026-04-27 by Tom:** `demand_qty` = SUM across all planning horizon buckets (Option 1, "total horizon", scale of risk view). DTO must ALSO include separate urgency fields when available: `earliest_shortage_at` / `earliest_bucket_date`, `earliest_bucket_required_qty`, `affected_bucket_count`. UI shows total demand as main scale metric + earliest shortage as urgency cue (e.g. "ביקוש חסום: 420 יחידות · חוסר ראשון: 30/4").
- **PBR-2 — DELEGATED to W1 (A13):** Run-level exception handling with `?item_id=` filter — W1 autonomous decision at implementation time.
- **PBR-3 — DELEGATED to W1 (A13):** `blocker_detail` key schema stability — W1 autonomous decision (W4 recommends opaque).
- **PBR-4 — DELEGATED to W1 (A13) 2026-04-27 by Tom:** `missing_supplier_mapping` `component_id` semantics — W1 must inspect `fn_generate_bf_purchase_recommendations` (migration 0102) and live schema; if exception payload is ambiguous/inconsistent, W1 normalizes in the backend DTO and documents the source mapping. Do NOT guess. Do NOT let W2 invent field semantics.
- **Planning Tranche 3 route LOCKED:** `/planning/blockers` (Tom 2026-04-27). Page title "חסמים בתכנון", subtitle "פריטים עם ביקוש שלא הפכו להמלצת רכש או ייצור שמישה".
- **W1-FOLLOWUP-CONVERT-RACE — RESOLVED 2026-04-30 (Phase 1 inspection):** `private_core.fn_convert_recommendation_to_po` in migration `0056_fn_convert_recommendation_to_po.sql` lines 89-95 uses `SELECT ... FROM planning_run_recommendations WHERE recommendation_id = p_recommendation_id FOR UPDATE` at function entry. Row-level lock serializes concurrent convert calls: first holds lock through INSERT purchase_orders + UPDATE converted_to_po_id + COMMIT; second waits, re-reads with same lock, returns existing po_id at line 104. Duplicate PO race is prevented. No patch required. Audit's earlier "concurrent race after pre-check passed" comment did not read past line 95 of the function.
- **Concrete tolerance thresholds** for (a) count discrepancy auto-post vs approval; (b) Green Invoice price-change auto-update; (c) rebuild-from-ledger parity check
- **Exact precision/scale values** for the quantity domain and the money domain (CLAUDE.md locks the principle; current working values `qty_8dp = numeric(24,8)`, `ratio_8dp = numeric(24,8)`, `money_4dp = numeric(18,4)`, `pct_4dp = numeric(9,4)` are not yet formally pinned)
- **On-prem read-only replica refresh cadence and failover rules** — CLAUDE.md locks "read-only fallback only"; cadence and failover not specified
- **Auth method** — CLAUDE.md locks Supabase magic-link email auth; wiring mechanics and first-user bootstrap still open; dev-shim fake-auth still in use in sandbox
- **The `.claude/agents/` executor / verifier / governor files** — the skill defines target architecture; compiled subagents not yet authored

## Current-state reference artifacts
Primary current-state source:
- `GT_Factory_OS.xlsx`

Supporting reference artifacts if available:
- `GT_Master_Data.xlsx`
- `GT_Playbook_HE_.xlsx`
- `GT_Roadmap.xlsx`

Treat the workbook as a current-state source only. Do not preserve its structure.

## Likely failure modes from here

The shapes most likely to fail or mislead over the next gate transition:

1. **Treating `RUNTIME_READY(form)` as Gate 3 exit.** It is a precursor, not exit evidence. Gate 3 exit = parity-after-live-production-form-traffic. Two signals emitted ≠ Gate 3 closed.
2. **W1 runtime tree remaining uncommitted on `main`.** Harness state + local evidence are real, but source that is not on `main` cannot be rolled forward, reviewed, or rolled back. Treat uncommitted production-path code as an outage risk.
3. **W2 drifting into Mode B for a second form before exiting Mode B for Waste.** `EXECUTION_POLICY.md` allows only one scoped form at a time. Parallel Mode B for Waste + PhysicalCount is a policy violation.
4. **Form submits that look green but do not produce posted ledger events.** UI rendering is not evidence. Gate 3 exit requires parity-after-live-traffic on production data, not 200 OK on a submit button.
5. **LionWheel mirror built against guessed field names.** 28 UNRESOLVED Gate-4 items remain. Any runtime built against assumptions will reconcile incorrectly at the first real split/merge/cancel.
6. **Shopify disagreement resolved in the wrong direction.** The platform is authoritative. Any reconciler that defers to Shopify on drift is broken.
7. **Green Invoice auto-creating components or auto-updating prices.** Forbidden until mapping quality and threshold rules pass. A price feed that "just updates" corrupts the pricing audit trail.
8. **Planning begun before Gate 3 closes.** "Stock truth ships before planning cutover" is non-negotiable (CLAUDE.md §non-negotiables #1). Beginning Gate 5 work while Gate 3 is PARTIAL is a contract_failure.
9. **Admin CRUD mass-edits to BOM or supplier mapping without approval gates.** CLAUDE.md Gate 2 / Gate 3 evidence rules forbid this; the admin screens today are mocked precisely because wiring them to writes is not yet safe.
10. **Excel round-trip creeping back in.** Any operator-facing workflow that edits the workbook re-introduces the system being rebuilt out of.
11. **LionWheel pick-reconciliation chain blocked by operator discipline + code defects + soak verification, NOT by missing API capability.** Live evidence 2026-04-30 (verifier PASS, `docs/integrations/lionwheel_live_inspection_2026-04-30.md` §9): LionWheel populates `body.task.order_items[].picked_quantity` when pickers explicitly enter quantities in the UI; Tom-edited shipment 24328405 (#GT12705) confirms the field path matches production code expectations. The 11/11-null finding from the prior W4 capture (5 unique ROUNDTRIP_DELIVERED tasks) reflects pickers not entering quantities, not API gap. Open blockers: (a) operational soak — 5-10 real Day-1 orders required to confirm picker discipline in normal workflow without Tom's intervention; (b) Phase 1 code defects — `task.status='COMPLETED'` enum drift (5th value beyond the 2026-04-18 4-element enum), type asymmetry (picked_quantity is JSON integer; ordered quantity is string-encoded), per-line `status` field schema drift (NEW values {NEW, PICKED, PARTIALLY_PICKED} not in 2026-04-18 §3.4 10-key schema); (c) Phase 2 code defect — premature `reconciledMirrorIds.add(row.mirror_id)` at `index.ts:876` / `reconciliation.ts:225` inside the `!fg_out_bridge_enabled` short-circuit (root-cause report `docs/lionwheel_chain_root_cause_2026-04-30.md`). Zero LionWheel-derived `FG_OUT_PICK` rows in production history; FG `current_balances` overstated by cumulative delivered volume since cutover. Path forward: see `docs/lionwheel_chain_repair_plan_2026-04-30.md` (soak → W1 Phase 1+2 repair → W4 Inbox/credit-draft contracts → W2 authoring after `RUNTIME_READY`).

## Three corrective commits during Gate 3 DB run (reference)
- `c03990c` — 0001 pgTAP plan count 23 → 26 (3 `col_is_pk` miscounted)
- `797e7cf` — `import_masters.ts` BOM import (bom_head / bom_version / bom_lines + FK ordering)
- `88af93e` — 0009 pgTAP P6b expect 2 not 1 (EXCEPT symmetric diff counts both sides)

## Live DB connectivity note
Direct `db.*` host is IPv6-only, unreachable from Tom's network. All connections use Session-mode pooler (`aws-1-eu-central-1.pooler.supabase.com:5432`) via `DATABASE_URL_POOLED` in `.env`. Safe for migrations, pgTAP, and imports.

## Canonical paths
- Canonical repo: `C:/Users/tomw2/Projects/gt-factory-os/` on branch `main` (last commit on `main` = `8c22ce9`, Gate 5 Phase 9 PO bridge complete + RUNTIME_READY(PurchaseOrders) emitted)
- W2 portal sandbox: `C:/Users/tomw2/Projects/window2-portal-sandbox/` (sole W2 owner; last commit = `70a0850`, Loop 5 planning rec UOM+current_stock+dates columns + jobs dashboard tile; prior commits: `adfb4d2` Loop 4 GR success context + movement-log fixes, `70cc491` Loop 3 approval detail pages, `96516ae` SKU alias portal fix, `8543d2b` sku-aliases idempotency_key fix)
- Harness state: `C:/Users/tomw2/GTeveryday Dropbox/.../PRODUCTION/.claude/state/{runtime_ready.json, active_mode.json}` (authoritative on signals and W2 mode)
- Plan file: `C:/Users/tomw2/.claude/plans/robust-sauteeing-moonbeam.md`

## DB ops log — manually-executed operations

### Day-1 prep stale-exception bulk-close — pending Tom execution 2026-04-30
- **action:** UPDATE on `private_core.exceptions`
- **scope:** `category='lionwheel_unknown_sku' AND status='open' AND created_at < now() - interval '14 days'`
- **expected rows affected:** ~41 (per CURRENT_STATE.md figure as of 2026-04-29)
- **executed_by:** Tom (admin) — pending execution
- **why now:** companion to design 2026-04-30 §A.3 #2 silent-drop change (commit `1202d5c`). The historical 41 stale rows predate the silent-drop change; bulk-closing them clears the inbox so Day-1 starts with a clean exceptions tab.
- **method (preferred — portal):** open `https://gt-factory-os-portal.vercel.app/exceptions?view=exceptions&category=lionwheel_unknown_sku`, multi-select all rows older than 14 days, click "Resolve" with reason note "Stale historical lionwheel_unknown_sku predating §A.3 #2 silent-drop change. Bulk-closed during Day-1 prep."
- **method (fallback — direct SQL via psql or Supabase SQL editor):**
  ```sql
  UPDATE private_core.exceptions
     SET status = 'resolved',
         resolved_at = now(),
         resolved_by_snapshot = 'admin (Day-1 prep bulk-close per design §A.3 #3)',
         resolution_notes = 'Stale lionwheel_unknown_sku exception predating §A.3 #2 silent-drop change. Closed in bulk on Day-1 prep.'
   WHERE category = 'lionwheel_unknown_sku'
     AND status = 'open'
     AND created_at < now() - interval '14 days';
  ```
- **preflight verification:**
  ```sql
  SELECT count(*) FROM private_core.exceptions
   WHERE category='lionwheel_unknown_sku' AND status='open' AND created_at < now() - interval '14 days';
  ```
  Expected: ~41 before; 0 after.
- **post verification:**
  ```sql
  SELECT count(*) FROM private_core.exceptions
   WHERE category='lionwheel_unknown_sku' AND status='open';
  ```
  Expected: 0 (or near-0 if any new exceptions arrived between Chunk 2 deploy and now — but per Chunk 2 silent-drop, no new ones should appear).
- **schema semantics changed:** NO
- **RLS changed:** NO
- **data changed:** YES (status field on ~41 rows; reversible via UPDATE … SET status='open' for specific exception_ids)
- **PO corridor touched:** NO

### 0152_shopify_fg_sync_history_disabled_status — applied 2026-05-07
- **file:** `gt-factory-os/db/migrations/0152_shopify_fg_sync_history_disabled_status.sql`
- **applied_at:** 2026-05-07 ~11:52Z via `gt-factory-os/scripts/apply_0152.mjs` (operational tooling, same pattern as `apply_0150.mjs` 2026-05-02)
- **what:** additive CHECK expansion on `private_core.shopify_fg_sync_history.write_status` to admit `disabled_pending_v2` (Phase 0 kill-switch audit row). Original 5 values (`ok`, `429`, `auth_fail`, `network_fail`, `skipped_unmapped`) preserved verbatim.
- **before:** `CHECK ((write_status = ANY (ARRAY['ok','429','auth_fail','network_fail','skipped_unmapped'])))`
- **after:** `CHECK ((write_status = ANY (ARRAY['ok','429','auth_fail','network_fail','skipped_unmapped','disabled_pending_v2'])))`
- **schema semantics changed:** NO (additive only)
- **PO corridor touched:** NO
- **pgTAP:** `db/tests/0152_shopify_fg_sync_history_disabled_status.test.sql` written (4 assertions). NOT YET RUN by W1 — codifies the constraint for canonical history; runtime correctness verified empirically by Phase 0 smoke (110 `disabled_pending_v2` rows inserted successfully + `pg_get_constraintdef` round-trip).
- **W1 review status:** REQUIRED. The migration was applied as a Phase-0 unblocking exception (W4 corridor needed the new status value to write its kill-switch audit row). Going forward, all schema deltas are W1-spec-only per Tom 2026-05-07 governance lock.

### 0082_gr_reversal_po_decrement_trigger — confirmed applied (pre-existing) 2026-04-24
- **file:** `db/migrations/0082_gr_reversal_po_decrement_trigger.sql`
- **status:** Already applied prior to this session. Confirmed via `information_schema.triggers` query: `trg_stock_ledger_gr_reversal_po_decrement` exists on `private_core.stock_ledger`. UNRESOLVED-GP-1 CLOSED.
- **schema semantics changed:** YES — new trigger on stock_ledger for GR_REVERSAL events; decrements `purchase_order_lines.received_qty`
- **PO corridor touched:** YES

### 0081_fk_hygiene_indexes — applied 2026-04-24
- **file:** `db/migrations/0081_fk_hygiene_indexes.sql`
- **environment:** production Supabase — project ref `rvadsozabmxkkrktwgnv` (eu-central-1)
- **connection:** direct host, SSL, autocommit (no transaction wrapper)
- **executed_by:** Claude Sonnet 4.6 / Tom session 2026-04-24
- **method:** Node.js `pg` client in autocommit mode (equivalent to `psql -v ON_ERROR_STOP=1 -f`; psql not in bash PATH on this machine)
- **preflight:** 0 invalid indexes found — clean
- **execution:** 9/9 statements OK, no errors
- **verification (pg_index):** 9 rows returned; `indisready=true`, `indisvalid=true` for all
- **indexes created:**
  - `idx_stock_ledger_reported_by_user` (partial, stock_ledger)
  - `idx_stock_ledger_posted_by_user` (partial, stock_ledger)
  - `idx_exceptions_acknowledged_by` (partial, exceptions)
  - `idx_exceptions_resolved_by` (partial, exceptions)
  - `idx_exceptions_related_job_run` (partial, exceptions)
  - `idx_integration_sku_map_item_id` (full, integration_sku_map)
  - `idx_planning_runs_forecast_version` (partial, planning_runs)
  - `idx_planning_runs_orders_snapshot_run` (partial, planning_runs)
  - `idx_planning_runs_supersedes` (partial, planning_runs)
- **schema semantics changed:** NO
- **RLS changed:** NO
- **data changed:** NO
- **PO corridor touched:** NO
