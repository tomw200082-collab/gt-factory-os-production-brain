# Historical state snapshot — Planning Corridor v1 detailed state (2026-05-08)

> **Origin:** migrated verbatim from `CURRENT_STATE.md` §"Active corridor — Planning Corridor v1 (baseline 2026-04-30)" during Phase 8 Run F Wave 4 Hole 2 cleanup (2026-05-09). The corresponding section in CURRENT_STATE.md was condensed to a one-line pointer; this snapshot is the audit-trail preservation of the full evidence detail at the time of the cleanup.
>
> **Type:** historical state snapshot of two parallel corridors (Shopify External Boundary v2 + Professional Stock-Truth Monitoring) and the Planning Corridor v1 evidence chain. Not authoritative on current state. For current corridor identity and active lane(s), read `ACTIVE_NOW.md`.

---

## Active corridor — Planning Corridor v1 (baseline 2026-04-30)

**Parallel corridor 2 — Shopify External Boundary v2 (in flight 2026-05-07):** plan authored at `gt-factory-os/docs/superpowers/plans/2026-05-07-shopify-lionwheel-external-boundary-v2.md`. **Phase 0 CLOSED 2026-05-07T11:55Z** — kill switch live (`SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED=false`); v1 blind `inventory_levels/set.json available=N` writes blocked end-to-end (10K+/day mutations stopped); migration `0152_shopify_fg_sync_history_disabled_status.sql` applied to live DB (CHECK expansion); evidence at `gt-factory-os/docs/superpowers/evidence/2026-05-07-shopify-phase0-bleeding-stopped.md` (PRs #6/#7/#8 merged). **Phase 1 CLOSED 2026-05-07T13:00:55Z** — 4 contracts + 3 backend-db specs landed (PR #9, commit `e123276`): `shopify_fg_sync_contract_v2.md` (17 sections, 9 readiness gates G-1..G-9, blind-available-set forbidden, `ignoreCompareQuantity` restricted to repair-command-only); `shopify_fulfillment_bridge_contract.md` (15 sections, disjoint trigger from FG sync, idempotency `lw_fulfillment:<lw_task_id>`); `shopify_movement_policy.md` (live-DB enumeration of 18 movement_type values, default UNDECIDED for unknowns); `shopify_v2_phase2_implementation_plan.md` (full 15-scenario test matrix with given/when/then). v1 SUPERSEDED banner. Verifier PASS 10/10. **Phase 2+3+4 in flight** under Tom's 2026-05-07 end-to-end-with-hard-stop directive: backend-db schema migrations (≥0153) + integration pure modules in parallel, then integration wiring + shadow logging. **Hard stop:** no live GraphQL inventory mutation, no live fulfillment bridge enablement until Phase 5 readiness report and explicit Tom approval. 13 historical `shopify_drift` exceptions remain untouched (REPORT/TRIAGE ONLY).

**Cycle-trail evidence files added 2026-05-07** (post-PR-#17 R2 real adapters merged 18:50:48Z; Edge Function v28 deployed; 52/52 tests pass; both `*_LIVE_ADAPTER_WIRED` sentinels remain `false`):
- `gt-factory-os/docs/superpowers/evidence/2026-05-07-shopify-pre-live-decision-pack-v2.md` (pre-live readiness decision pack)
- `gt-factory-os/docs/superpowers/evidence/2026-05-07-shopify-r2-adapter-run.md` (R2 real-adapter shadow-mode evidence)
- `gt-factory-os/docs/superpowers/evidence/2026-05-07-shopify-gate-e-preparation-and-drift-closure-plan.md` (PR #18 merged 19:27:20Z, commit `7f82ee1`, 5 deliverables: 8-blocker drift list, LW `lw_qty_picked` enrichment recovery post-key-rotation, Gate E execution pack on candidate test SKU `ADD-GAR-ANISE`, sentinel circularity options A/B/C/D, 7-blocker ordered list)
- **Open Tom decisions blocking next dispatch (snapshot date):** GE-1 (test SKU confirmation; recommended `ADD-GAR-ANISE`), GE-2 (sentinel strategy — Option C SKU-allowlist-scoped flag recommended; Option B time-bounded global flip as fallback). GE-4 (task 24442225 `wp_order_id`) resolved as `#GT12757` by integration verifier.

**Parallel corridor — Professional Stock-Truth Monitoring (in flight 2026-05-07):** plan authored at `PRODUCTION/docs/superpowers/plans/2026-05-07-professional-monitoring.md`. Tom-locked Sunday 2026-05-10 as cutover day (post physical count). **Pre-cutover prep landed this session:** (1) 70 LionWheel SKU mappings written to `integration_sku_map` — coverage went 0→83% on terminal lines (558/683 in last 14d will post on bridge flip; 122 silently skip per excluded_legacy_bundle/excluded_non_stock; 3 → exception inbox). (2) 2 new master items created: `FG-SAN-BAB-RED-750ML` (RED SANGRIA BABA 0.75L, shares BOM with FG-SAN-RED-750ML), `AP-DRI-PIN-1KG` (PINEAPPLE DRIED 1KG, BOUGHT_FINISHED). (3) Typo fix on `AP-TAP-PIN-0.6` (was "MANGO", now "PINEAPPLE"). (4) Sentinel item `EXCLUDED-NONSTOCK` (`is_stock_managed=false`) created as the FK target for excluded mappings. (5) Sunday cutover runbook authored at `PRODUCTION/docs/superpowers/runbooks/2026-05-10-sunday-cutover-runbook.md`. **In flight:** B.1 (audit_runs migration 0151 + daily Railway cron, executor-w1) + B.2 (Telegram alert dispatcher, executor-w4) — both dispatched in background. **Bridge state:** `LIONWHEEL_FG_OUT_BRIDGE_ENABLED=false` — DO NOT FLIP until Sunday post-count per runbook §5. **Open Tom dependencies:** Telegram bot token + chat_id (runbook §10), JOB_RUNNER_TOKEN provisioning, app_users uuid for count import. Two SKUs intentionally left unmapped (`""` empty + `7290003803217` EAN, 5 lines/30d total — exception inbox).

**Active program:** Forecast → Planning Run → Production Recommendations → Daily Production Plan → Purchase Recommendations → Production Actual / PO. Driven by Tom's autonomous-program directive 2026-04-30.

**T1 status (planning corridor UX clarity):**
- T1 deployed green at portal commit `fde59c8` (Vercel + Railway portal-side both `state: success`, 2026-04-30T13:02:52Z / 13:03:37Z).
- T1 manual browser walkthrough (9-item checklist) NOT YET RUN.
- T1 is CODE-COMPLETE / DEPLOYED, not production-verified. Status A (production-verified) requires the manual click-through.
- Static verification: typecheck `EXIT=0`; no remaining `window.confirm` in `/planning/runs`; no remaining dead `/convert` portal navigation; `JSON.stringify(body)` admin-gated; reason_codes mapped before display.

**Active follow-ups:**
- `W1-FOLLOWUP-CONVERT-RACE` — RESOLVED 2026-04-30 (see Open UNRESOLVED items below; row-locked via `FOR UPDATE` in migration 0056).

**Daily Production Plan v1 — Gates 3A → 3B → 4 → 4.2 → 5 (from_plan) DONE on disk (2026-04-30 → 2026-05-01); cycle 1 of overnight Ralph Loop reconciled the state:**
- Table `private_core.production_plan` — APPLIED to live Supabase 2026-04-30 ~13:02. Migration file canonical filename: `db/migrations/0115_production_plan.sql` (renamed from 0114 to resolve slot collision with `0114_master_data_cleanup_phase1.sql`; live DB unchanged by rename — no migration tracking table exists in repo, verified by grep). Test file: `db/tests/0115_production_plan.test.sql`. 10/10 runtime functional assertions PASS via Node-based runner (formal `pg_prove` not run; pgTAP file ready). Contract: `gt-factory-os/docs/production_plan_contract.md`.
- API endpoints `/api/v1/queries/production-plan` + `/api/v1/mutations/production-plan` — Gate 3B DONE at canonical main `bafbcb0` (2026-04-30). 14/14 node:test PASS against live pooled Supabase PG17.
- Route `/planning/production-plan` — Gate 4 DONE at portal main `483ac66` (2026-04-30); Gate 4.2 English/LTR + state hygiene DONE at portal main `4fee418` (2026-05-01). Audit P0 surfaces remain open on OTHER planning surfaces — see `PRODUCTION/docs/overnight_audit_2026-05-01.md` (16 P0 / 38 P1 / 50 P2 / 29 P3 across 12 corridors).
- `production_actual` `from_plan_id` parameter — Gate 5 additive linkage DONE this cycle (overnight Ralph Loop cycle 1, 2026-05-01). Signal #18 `RUNTIME_READY(ProductionActual-FromPlan)` emitted 2026-05-01T16:35:00Z; Railway deployment `2edf9930-2164-4a1c-904a-259932ee68f4` healthy; 4 new conflict codes (`PLAN_NOT_FOUND` / `PLAN_ITEM_MISMATCH` / `PLAN_ALREADY_COMPLETED` / `PLAN_CANCELLED`); live-DB `PRODUCTION_PLAN_LINKED_ACTUAL` change_log_action already present from migration 0115. Evidence: `gt-factory-os/docs/production_actual_from_plan_checkpoint.md` + `api/test/production_actual_from_plan.test.ts` (8/8 PASS, independently re-run by verifier). Committed and pushed: gt-factory-os/main `821dfd5` (backend-db Gate 5 from_plan tranche) + `069f136` (integration dashboard control-tower v2 spec).
- Inventory-flow planned-inflow overlay — Gate 5b, NOT YET IMPLEMENTED.
- Dashboard control-tower v2 coverage requirements spec authored this cycle: `gt-factory-os/docs/integrations/dashboard_control_tower_v2_coverage_requirements.md` (integration, 721 lines, 7 GAPs, 8 UNRESOLVED items DCT2-1..DCT2-8). GAP-7 (production_actual.from_plan column) closed same cycle by backend-db signal #18.
- **RUNTIME_READY signal count: 35** (was 17 → 18 ProductionActual-FromPlan → 19 CriticalToday → 20 AddFromRecommendations → 21 Planning-Tranche2-RecommendationDetail-v1.1 → 22 ProductionPlanSlippage → 23 DashboardCriticalToday → 24 DashboardSlippedPlans → 25 AdminHolidays → 26 HolidaysArchivedFilter → 27 LionWheelOrderNote → 28 LionWheelCreditDecisionBackend → 29 PlannedInflowByDay → 30 LionWheelRuntimeClosure → 31 ProductionActual-TwoHead (Tom-screenshotted critical bug fix; 6 tranches landed 2026-05-02; verifier PASS; FULL GO 2026-05-02 — Tom confirmed visual portal acceptance on FG-DES-1L; data-fix follow-on migration 0130 closed the 5 MAR/SAN `pack_no_base_bom_line` anomaly via version-bump path; see `PRODUCTION/docs/two_head_bom_repair_evidence.md` + `PRODUCTION/docs/2026-05-02-two-head-bom-explosion-repair-plan.md`)).

**Two-Head BOM Repair (2026-05-02) — closed end-to-end:**
- Bug: Production Actual handler did single-level BOM explosion on `items.primary_bom_head_id` (PACK) only; data model has TWO heads per MANUFACTURED item — PACK (packaging) + BASE (liquid recipe). Same blind spot in planning engine `fn_explode_bom_to_components`. Tom screenshotted FG-DES-1L showing only 4 packaging components, no liquid.
- Fix: 6 tranches in one day. Migration 0127 added `production_actual.base_bom_version_id_pinned`. Migration 0126 v2 of `fn_explode_bom_to_components` (recursive two-head walker; same signature, no caller change). Handler `loadTwoHeadBomContext` helper + 4 new node:tests; 7 new conflict reason codes. Portal page.tsx grouped sub-headings (`רכיבי אריזה` / `רכיבי נוזל`) + composition banner. CLAUDE.md §"Production reporting v1" amended.
- Empirical proof: 42/50 post-deploy `stock_ledger` submissions exhibit two-head explosion signature (both `:CONSUME:pack:` and `:CONSUME:base:` rows under same `source_event_id`); pre-fix this number was 0. `rebuild_verifier()=0`. Post-fix audit identical to baseline 48 items.
- Pre-launch: no historical reconciliation needed (all prior `production_consumption` rows were synthetic test data).
- Data-fix follow-ons:
  - 5 MAR/SAN items — CLOSED 2026-05-02 via migration 0130 (commit `5c4753d`, version-bump path, per-pack base liters = bottle volume). Audit `pack_no_base_bom_line` bucket: 5 → 0; `ok_two_head` bucket: 26 → 31.
  - Legacy `'BOM'` ref-type cleanup — CLOSED 2026-05-02 via migration 0131 (commit `532553b`, Option 1 expanded scope: 10 rows flipped to INACTIVE on the 5 affected PACK heads + new CHECK constraint `bom_lines_no_bom_ref_on_pack_active` preventing recurrence on PACK/REPACK heads). pgTAP 7/7. Bug-fix proof: zero `unsupported_bom_ref` exceptions emitted on synthetic FG-MAR-CLA-300ML planning run.
  - 6 MUZA mixers — still open (Tom must decide complete-BOM vs flip to BOUGHT_FINISHED). NOT blocking — handler returns 409 NO_BOM_HEAD until resolved.
  - 5 T2DET test fixtures — still open (cleanup). Trivial; can happen any time.

**Planning Corridor v1 — RESUMES** after this repair lands (was rate-limit-interrupted at cycle 8 partial state per prior CURRENT_STATE entries; the two-head repair was higher priority because the planning engine itself was producing wrong purchase recommendations for liquid RM on every run).
- portal sandbox tip advanced from `4f2d325` → `4fee418` → `9f3b98e` (cycle 2 production-actual P0-A) → `24e5a7a` (cycle 3 planning-runs P0-B/C/E/I sweep) → `303465c` (cycle 4 add-from-recs picker + dashboard quick-actions + forecast P0-J) → `eb76918` (cycle 5 variance display + signal #21 consumption) → `012dd16` (cycle 6 bulk approve + URL cleanup) → `52b63ab` (cycle 7 /dashboard/v2 MVP — Tom priority #8). Cycle 8 portal work (`/admin/holidays` page) is on disk but uncommitted (rate-limit interrupt).
- Canonical main tip advanced from `8c22ce9` → `bafbcb0` → `821dfd5` (cycle 1 Gate 5 from_plan #18) → `069f136` (cycle 1 dashboard v2 spec) → `c6f29e2` (cycle 2 DCT2 + variance contract) → `34e36ee` (cycle 2 GAP-1 v_critical_today #19) → `16a18f0` (cycle 3 add-from-recs endpoint #20) → `2bd2a76` (cycle 3 inventory-flow planned-inflow contract) → `7fe31c0` (cycle 4 rec-detail DTO ext #21) → `1838512` (cycle 5 admin/holidays contract) → `0679f5c` (cycle 5 v_production_plan_slippage #22) → `54db614` (cycle 5 admin/holidays contract revised) → `528c7ce` (cycle 6 dashboard handlers #23+#24) → `c1fda82` (cycle 7 admin/holidays CRUD #25) → `0679f5c→0679f5c` (cycle 7 rehearsal test plan) → `44ac489` (cycle 8 PO-attached GR enhancement spec). Cycle 8 backend-db work (signal #26 HolidaysArchivedFilter migration 0120) is on disk but uncommitted (rate-limit interrupt).
- Mode B-Planning-Corridor amendment added to EXECUTION_POLICY.md 2026-05-02 (Tom-authorized cycle 1 governance Q1.A): scopes pan-portal authoring on planning corridor surfaces. Cycle 7 amendment add: `/dashboard/v2` added to allowed surfaces per DCT2-8 default. Coexists with Mode B-AMMC and Mode B-Portal-Refactor. Expires when 11 audit P0 findings on planning corridor surfaces all close.
- DCT2 resolution pack: all 8 DCT2-1..DCT2-8 items classified cycle 2 — 0 items blocking. Dashboard v2 §4.1 + §4.4 blocks shipped cycle 7; remaining 7 sub-blocks render honest "Awaiting read-model" placeholder cards.
- Audit P0 status (cycles 2-7): 8 of 11 closed — P0-A (production-actual cycle 2), P0-B (runs detail cycle 3), P0-C (rec drill-down cycle 3), P0-E (runs list cycle 3), P0-F (dashboard quick-actions cycle 4), P0-I (run freshness cycle 3), P0-J (forecast active callout cycle 4) + exception action deep-link fix cycle 3. Still open: P0-D (PO `[po_id]` Hebrew banner — needs governance carve-out + Tom POGR-2), P0-G (production-simulation IDB false green — Tom decision PSDP-1..4 queued), P0-H (admin/holidays — backend done cycle 7 #25; consumer filter on disk cycle 8 #26 uncommitted; portal page on disk cycle 8 uncommitted; rate-limit-interrupted).
- integration contracts authored cycles 1-8 (8 specs total): dashboard control-tower v2 coverage (cycle 1), variance display (cycle 2), PO→GR readiness (cycle 3), DCT2 resolution pack appended (cycle 2), inventory-flow planned-inflow overlay (cycle 4), /admin/holidays CRUD (cycle 5), production-simulation runtime decision pack (cycle 6), whole-system rehearsal test plan (cycle 7), PO-attached GR enhancement (cycle 8).
- Cycle 8 partial state — RESOLVED 2026-05-08 (Phase 8 Wave 0 reconciliation): Verified post-interrupt closure: backend-db backend committed as `be2fced` "feat(holidays): consumer-side archived_at filter on fn_compute_daily_fg_projection (signal #26)" landing migration `0120_holidays_il_archived_filter.sql` + pgTAP + checkpoint + inspection scripts on canonical main. portal committed as `bf4a744` "feat(admin/holidays): live CRUD page consuming signal #25 + #26 (cycle 8 closure)" landing the `/admin/holidays` page changes (page.tsx, route.ts, [holiday_date]/, bulk-import/). Signal #26 `RUNTIME_READY(HolidaysArchivedFilter)` was already on file. Cycle 8 is closed; subsection retained as audit trail of the 2026-05-02 rate-limit interrupt and its resolution.
- No planned production currently affects stock_ledger, current_balances, or any projection. A4 LOCKED in `fn_compute_fg_net_requirements` (FG netting inbound = 0) remains in force.
- No autonomous ordering, no autonomous production.
- A3 LOCKED (`v_planning_demand` buckets all open orders to current ISO week) remains in force.

**T3A audit-log artifacts (inert):** 3 `change_log` rows from the T13 cross-transaction runtime test reference plan_id `875718c3-a95a-4e69-a158-a1fc8f868bd0` (PRODUCTION_PLAN_CREATED + EDITED + DELETED, snapshot `t3a-T13fix`). The corresponding `production_plan` row was deleted at test cleanup; the `change_log` rows remain because that table is append-only by design (`change_log_append_only_guard()` from migration 0025). No operational impact.

**Locked boundaries during this corridor:**
- `stock_ledger` semantics, `current_balances` triggers, `balance_anchors`
- `fn_compute_fg_net_requirements`, `fn_compute_component_net_purchase`, `v_planning_demand`
- A3/A4 locked assumptions, forecast freeze/publish semantics
- Auth model, Excel/import rules
- Open PO offset behavior inside the planning engine

---

## Main-tip progression and Gate 5 commit log (snapshot at 2026-05-08)

**Main-tip progression:** main tip advanced to `9633ebc` as of 2026-04-23 (fix: populate reported_by_snapshot on all stock_ledger writes; deployed to Railway via `railway up --detach`, deployment c3d66703). Prior tip: `ac75ed1` (AMMC Slice 6 backend, 2026-04-21). Interim tranches since `8c22ce9` (Gate 5 Phase 9 PO bridge, 2026-04-19): Gate 5 Phase 9 completion, Production Endgame Phase A3 (ProductionActual runtime) / Phase E3 (Shopify FG sync runtime) / Phase E4 (Green Invoice supplier-price ingest runtime), and AMMC Slices 1–6.

**Gate 5 tranche (14 commits, all landed on `main`):**

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
  - `a63bf99` gate5-phase9: integration PO contract pack — 4 requirements-only contracts for purchase_orders substrate
  - `8c22ce9` gate5: phase 9 PO bridge — migrations 0049-0057 + handler + E2E proof + RUNTIME_READY(PurchaseOrders)

**portal sandbox tip:** advanced from `6779d27` (Forecast MVP) to `4f2d325` (PlanningRun MVP `/planner/runs` canonical review surface).

Intentional untracked items remained at the time of the snapshot: `.claude/` (harness state, forbidden), `.mcp.json` (Tom disposition pending), `docs/gate_commit_tranche_checkpoint.md` (prior-cycle governance artifact), `portal/test-results/` + `test-results/` (build artifacts).

Full tree coherent through `8c22ce9`. Rollback granularity per plan §10: per-commit reverse order (see `docs/gate5_closure_decision_pack.md` §8 for full 18-step Gate-5 rollback sequence including Phase 9 PO bridge unwind if ever required).

Remote status (snapshot date): origin/main push cadence is Tom-authorized.

Governance: commit stagnation CLOSED as of 2026-04-18; Gate 5 tranche committed cleanly across cycle.

---

## RUNTIME_READY signals enumeration (snapshot at 2026-04-27)

> The authoritative source for signals is `.claude/state/runtime_ready.json`. The list below captures the signal #1..#17 enumeration that was inline in CURRENT_STATE.md before the cleanup; the latest count at the time of cleanup was 35.

**RUNTIME_READY signals (17 total at 2026-04-27, authoritative source `.claude/state/runtime_ready.json`):** (1) WasteAdjustment (2026-04-17), (2) PhysicalCount (2026-04-17), (3) ExceptionsInbox (2026-04-18), (4) Forecast (2026-04-18), (5) LionWheel (2026-04-18), (6) freshness_check (2026-04-18), (7) PlanningRun (2026-04-19), (8) PurchaseOrders (2026-04-19), (9) ProductionActual (2026-04-21T17:05), (10) GreenInvoice (2026-04-21T18:45), (11) Shopify (2026-04-21T19:05), (12) RalphLoopReAudit (2026-04-25T00:30), (13) PurchaseOrders-manual (2026-04-26T00:00), (14) InventoryFlow (2026-04-26T10:55), (15) Planning-Tranche1 (2026-04-26), (16) Planning-Tranche2-RecommendationDetail (2026-04-26), (17) Planning-Tranche3-Blockers (2026-04-27 — endpoint `GET /api/v1/queries/planning/blockers`, commit `1209596`, Railway deployment `ef03b588`, 12/12 node:test against live pooled PG17).

A stale repo-local file at `gt-factory-os/.claude/state/runtime_ready.json` does not override the governance file (per memory `feedback_harness_state_authoritative.md`: governance path is authoritative on signals).

---

## Gate 3 prior closure evidence (snapshot)

**Prior closure evidence (2026-04-18, superseded by current PARTIAL status; preserved as audit trail):** Closed on CLAUDE.md §"Gate model" literal exit criteria (parity, idempotency, race, minimal Exceptions Inbox), per `docs/gate3_closure_decision_pack.md` (2026-04-18, executor-w1) and verifier PASS on substance. Documentation-integrity defects in the pack (§2.4 and §3 item 5 harness-state citations) repaired 2026-04-18 by executor-w1 (evidence pack `docs/gate3_exceptions_inbox_evidence.md` authored; `RUNTIME_READY(ExceptionsInbox)` signal emitted; §3 item 5 rewritten as explicit UNRESOLVED). Commit hygiene tracked separately: Gate 3 evidence artifacts still uncommitted on `main` at the time of the prior closure (see caveat at the time).

Gate 3 exit CLOSED on CLAUDE.md §"Gate model" literal four exit criteria per `gate3_closure_decision_pack.md` + verifier PASS on substance. Interpretation change at the time: exit criteria are the four items literally named in CLAUDE.md (parity within tolerance, idempotency, count-freeze race, minimal Exceptions Inbox) — NOT "live production form traffic", which is an operator-rollout milestone distinct from the contract-specified gate exit. Post-exit open items at the time: (a) commit-hygiene tranche landing 20 Gate-3 artifacts on `main`; (b) eventual first production-traffic event (operator rollout milestone, separately tracked).

---

## Canonical paths (snapshot)

> Authoritative source for canonical paths is `WORKSPACE_MAP.md`. The list below was inline in CURRENT_STATE.md prior to cleanup.

- Canonical repo: `C:/Users/tomw2/Projects/gt-factory-os/` on branch `main` (last commit on `main` = `8c22ce9` at the time of the snapshot, Gate 5 Phase 9 PO bridge complete + RUNTIME_READY(PurchaseOrders) emitted)
- portal sandbox: `C:/Users/tomw2/Projects/window2-portal-sandbox/` (sole portal owner; last commit at the time = `70a0850`, Loop 5 planning rec UOM+current_stock+dates columns + jobs dashboard tile; prior commits: `adfb4d2` Loop 4 GR success context + movement-log fixes, `70cc491` Loop 3 approval detail pages, `96516ae` SKU alias portal fix, `8543d2b` sku-aliases idempotency_key fix)
- Harness state: `C:/Users/tomw2/GTeveryday Dropbox/.../PRODUCTION/.claude/state/{runtime_ready.json, active_mode.json}` (authoritative on signals and portal mode)
- Plan file: `C:/Users/tomw2/.claude/plans/robust-sauteeing-moonbeam.md`
