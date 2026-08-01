# GT Factory OS — Current State

> Sole authority on live gate status, completion, critical path, open gaps.
> Other docs **point** here, ⊥ restate. ⊥ relax a locked decision in `CLAUDE.md`.
> On signals & W2 mode, `.claude/state/*.json` win — this file reconciles from them.
> **Volatile.** History ∉ this file → `docs/archive/CURRENT_STATE.pre-lean-2026-07-31.md`.

**Last calibrated:** 2026-07-31.

## Status

| | |
|---|---|
| Overall platform | **~85–90%** (Tom-owned figure; set 2026-07-31 from evidence below, supersedes stale `~60–70%` carried since 2026-04-23) |
| v1 gates 1–5 | **ALL CLOSED.** Gate 3 returned to CLOSED — LionWheel chain repair landed, bridge in continuous prod use since 2026-05-10, `rebuild_verifier() = 0` |
| Portal readiness | 92/100, 9/10 categories ≥8 (`gt-factory-os-portal/docs/portal-os/scorecard.md`) |
| Stock truth | holds. `rebuild_verifier() = 0` |
| RUNTIME_READY | `.claude/state/runtime_ready.json` is sole authority. 36 entries at last verify 2026-07-17. ⊥ restate this count elsewhere |
| W2 mode | A (`active_mode.json`, since 2026-05-02T22:00Z) |
| Railway / Vercel | healthy / ready |

Evidence for the range: all gates closed · bridge live daily since 2026-05-10 · portal 92/100 · ~155 commits across backend+portal 2026-05-18→07-17 spanning economics, production-planning, order-intake, decision-board, procurement · offset by 2 named open gaps below (`audit_runs`, Shopify Gate E).

## Landed & live

**Factory-mapping v3 (2026-07-22/23)** — org model → operating system. Docs `docs/factory-mapping/`, playbook v2 in force `docs/playbook/operator-playbook-he.md`. Skills: `daily-delivery-dispatch`, `route-print-pack`, `daily-ops-guardian` (Stage 0.5 + `queue-guard` Thu 15:50 + `sunday-prep` Sat 20:00). Portal tranches 136/137/138 (PRs #178/#177/#180). Backend T8 (#176) + G1 migration 0287 `v_production_plan_vs_actual`, applied prod & live-verified.

**Procurement corridor (2026-07-16/17)** — migrations 0284–0286 (PRs #170/#171) applied prod & live-verified; portal tranches 132–133 (PRs #172/#173); `procurement-planning` skill (PRs #41/#42). Fixed live bug: `item_type <> 'SYSTEM'` on a mostly-NULL column silently dropped 7 sellable BOUGHT_FINISHED lines per session → `IS DISTINCT FROM`.

**LionWheel FG_OUT bridge** — cutover 2026-05-10, continuous prod use since. `LIONWHEEL_FG_OUT_BRIDGE_ENABLED` behaviorally `true`. ⊥ flip back without Tom rollback decision + parity replay. Two legitimate reversal classes (delivery-correction; count-freeze-driven) ratified in `docs/decisions/LOCKED_DECISIONS.md` §LionWheel. `LIONWHEEL_PICK_ADJUSTMENT` = Tom-approved-manual-only; production code ⊥ emit it. Count-freeze race has operational fix: migration `0277_fg_out_movement_pause.sql` + portal tranche 118.

## Open — needs Tom

- **Shopify FG sync writes nothing.** 70,259 `disabled_pending_v2` rows in 7d, **zero `ok`**. Cause: `SHOPIFY_FG_SYNC_LIVE_ADAPTER_WIRED = false` hardcoded (`supabase/functions/factory_os_jobs/index.ts:87`, Tom-locked 2026-05-07 R1, proven unbypassable by `api/test/shopify_policy.test.ts` S21–S24). ⊥ a flag flip — needs code change + Edge Function deploy + Phase 5 gates. Gate E inputs already decided: GE-1 SKU `ADD-GAR-ANISE`, GE-2 Option C SKU-allowlist (Tom 2026-05-23). Corridor has zero commits since `bcb2d0f` (2026-05-08).
- **`network_fail` is a misnamed status — DIAGNOSED 2026-07-31, ⊥ a network problem.** It means "variant absent from the active-products cache"; the label was never renamed when semantics changed (`index.ts:2699` comment says so). All 671 rows/7d are **one SKU**: `ADD-MAT-BOWL` carries `items.sku='AP-MAT-BOWL'`, Shopify's variant is **`AP-BWL-MAT`** — token transposition. Fix ! Tom confirm the two are the same product ("TRADITIONAL MATCHA BOWL NONOMIMI" vs Shopify "Ceramic Matcha Bowl", ₪118) — ⊥ guess an alias mapping. Then map via `integration_sku_map`, ⊥ by editing `items.sku`.
- **Mapping coverage is 46/47 real FG items (97.9%).** The 48th sweep row is `EXCLUDED-NONSTOCK`, the deliberate FK-target sentinel — working as designed but emitting a false `skipped_unmapped` every cycle; filter it out of the sweep.
- **40 active Shopify products sit at negative inventory** (worst: `GTMN-PIK-254` −2,675, `GTCC-TRO-JAP-1L` −1,482 @ ₪88, `GT-GLA-MAT-PRINT` −1,400, `AP-PLA-STR-11` −941, `GTCC-MUZ-PNMM-1L` −653 @ ₪92). Platform counts are unanchored while the sync is off. ! per-SKU adjudication before anything overwrites them — some "WH Products" wholesale rows may be intentional.
- **~76 of the 78 open `shopify_variant_not_found` exceptions are stale** — test fixtures (`T2DET-*`, `T3BLK-*`, `T22JOB-*`, `TEST-LW-PROBE-FG-1`) still ACTIVE FINISHED_GOOD in prod and swept every cycle. Deactivate + bulk-close.
- **`disabled_pending_v2` writes ~70k rows/week** (4 runs/hr × 84 rows), burying real signal in `shopify_fg_sync_history`. Emit one summary row per run instead.
- **`shopify_available_reconcile_live`** flag `enabled=true allowlist="*"` (2026-07-24, description records Tom approval) — but **no reconcile function exists in the repo**. Tracked by migration 0302. Confirm intent or retire the flag.
- **`audit_runs` empty — P2 reporting gap, ⊥ a stock-truth gap.** Table exists (0151), `row_count = 0`; it was specced for a Python multi-layer audit skill (`layer1_pct`..`layer5_pct`, `verdict`, `report_jsonb`, alert dispatch) that was never built. Blocked on `JOB_RUNNER_TOKEN` + container at `AUDIT_SCRIPT_PATH`.
  **⊥ confuse with nightly stock-truth verification, which runs and is green.** `cron.job` 12 `nightly_rebuild_verifier` (`0 3 * * *`, active) → `private_core.run_rebuild_verifier('cron_nightly')` → writes `private_core.job_runs`. **83/83 succeeded since 2026-05-11, `drift_count = 0` every run**, latest 2026-08-01 03:00 (217 keys, 1.2s). It auto-opens a critical `projection_drift` exception per drifted balance key and auto-resolves them at zero drift. `CLAUDE.md` §Source-of-truth "rebuild-verified nightly" is accurate.
- Maxim's portal user (email) — last piece of tranche 137. Dennis provisioned.
- Alex conversation — pack ready (`docs/factory-mapping/2026-07-22-alex-package-he.md`), gates rollout weeks 5–6.
- Telegram bot token + chat_id (monitoring alerts). `app_users` uuid for count import.
- Read-only verify exact Railway env literal for `LIONWHEEL_FG_OUT_BRIDGE_ENABLED`.

## Shopify cutover — BLOCKED by two findings (shadow report, 2026-08-01)

Phase 3 ran read-only against the 47 swept items. **⊥ enable live writes until both are resolved.**

1. **Our qty ≈ 2× Shopify on essentially every FG line, several at exactly 2.000.**
   `GT-LUI-FRE-1L` 766/383 · `GT-ODK-MAN-1` 394/197 · `GTEL-MAR-PEA-0.3L` 458/229 · `GT-MAS-CHA-0.5L` 486/243 · `GT-JAS-LOW-1L` 950/473 · `GT-SEN-LOW-1L` 940/452 · `GT-LUI-LOW-1L` 1576/659.
   Exact 2.000 ratios ⊥ coincidence — points at a UOM / pack-size mismatch (bottles vs 2-packs) or double-counting in the `SUM(cb.calculated_on_hand)` aggregation. **Pushing live today would double every storefront quantity.** ! root-cause before any write.
2. **Duplicate SKUs across multiple Shopify variants.** `GT-LUI-FRE-1L` appears on 3 variants (383/0/0), `GT-LUI-LOW-1L` on 2 (659/0), `GT-MAS-CHA-0.5L` on 2 (0/243). The sync keys `skuCache` by SKU (Map, one `inventory_item_id` per key), so it would write to an arbitrary one and leave the rest stale — possibly writing the live number onto a dead 0-qty duplicate.

Gate E scope (`ADD-GAR-ANISE` only, migration 0302) limits blast radius but resolves neither.

## Deferred (Tom decision, ⊥ blocking)

SQL `tier` semantics (portal now classifies from trace math, underlying tier still old floor-breach logic) · `cover_days` buffer over-buffers 81/81 components sampled — needs plan-aware formula · ₪-at-risk trend needs a "previous session" definition · `--fg-subtle` light-theme contrast 3.09:1 unaudited · A11Y-003/004/010 · Dorin persona split · Maiden LionWheel driver record · Sat customer reminder · widen CI `typecheck` to `api/src` · flaky `supabase` postinstall in CI.

## UNRESOLVED — ⊥ silently heal

Any activation touching these ! emit `assumption_failure` and surface the gap.

- **LionWheel** order-line schema, stable identifiers, status lifecycle — ! live API inspection. ⊥ guess field names.
- **Green Invoice** line-item schema + supplier-SKU availability — ! live inspection. Auto-creating components ⊥ until resolved.
- **Shopify** cancellation / refund path in GT's order flow — reconciliation undefined until inspected.
- **Customer-specific pricing** — ⊥ modeled until confirmed it exists in real operations.
- **Tolerance thresholds** — count-discrepancy auto-post vs approval · GI price-change auto-update · rebuild-from-ledger parity.
- **Precision/scale** not formally pinned. Working: `qty_8dp`/`ratio_8dp` = `numeric(24,8)`, `money_4dp` = `numeric(18,4)`, `pct_4dp` = `numeric(9,4)`.
- **Auth** — Supabase magic-link locked; wiring mechanics + first-user bootstrap open.
- **On-prem read-only replica** refresh cadence + failover unspecified.

## Failure modes to watch

1. UI green ≠ posted ledger event. 200 OK on submit ⊥ evidence.
2. Integration runtime built on guessed field names → reconciles wrong at first real split/merge/cancel.
3. Shopify disagreement resolved wrong way — platform is authoritative.
4. Green Invoice auto-creating components or auto-updating prices → corrupts price audit trail.
5. Admin CRUD mass-editing BOM or supplier mapping without approval gates.
6. Excel round-trip creeping back via any operator workflow that edits the workbook.
7. Empty ≠ green — a gate query returning 0 rows may mean the query is wrong (precedent: skill staleness-gate used `item_type='COMPONENT'`, never matches live taxonomy `RM`/`PKG`/`FG`, read green for weeks).
8. Restating a count that has a JSON source of truth → drift. Point at the file.

## Reference

Current-state workbook: `GT_Factory_OS.xlsx` (source only, ⊥ preserve structure). Supporting: `GT_Master_Data.xlsx`, `GT_Playbook_HE_.xlsx`, `GT_Roadmap.xlsx`.
Live DB: Supabase `rvadsozabmxkkrktwgnv` (`gt-ops-prod`, PG17), Session-mode pooler via `DATABASE_URL_POOLED` — direct `db.*` host is IPv6-only.
Portal tranche history: `gt-factory-os-portal/docs/portal-os/registry.md` + `.../scorecard.md`. ⊥ duplicated here.
Reference PR numbers, ⊥ shas — local mains lag GitHub squash-merges.
