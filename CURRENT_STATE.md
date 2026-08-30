# GT Factory OS — Current State

> Sole authority on live gate status, completion, critical path, open gaps.
> Other docs **point** here, ⊥ restate. ⊥ relax a locked decision in `CLAUDE.md`.
> On signals & W2 mode, `.claude/state/*.json` win — this file reconciles from them.
> **Volatile.** History ∉ this file → `docs/archive/CURRENT_STATE.pre-lean-2026-07-31.md`.

**Last calibrated:** 2026-08-01.
**Doc contract (Tom 2026-08-01):** this file holds open gaps + gate status + UNRESOLVED **only**. Domain depth → `.claude/skills/<domain>/SKILL.md` (descriptions auto-load; bodies on demand). Anything a query can answer ∉ prose here. History → git log.

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

Evidence for the range: all gates closed · bridge live daily since 2026-05-10 · Shopify sync live 53/53 (2026-08-01) · portal 92/100 · ~155 commits across backend+portal 2026-05-18→07-17 · offset by the open gaps below.

## Landed & live

**Factory-mapping v3 (2026-07-22/23)** — org model → operating system. Docs `docs/factory-mapping/`, playbook v2 in force `docs/playbook/operator-playbook-he.md`. Skills: `daily-delivery-dispatch`, `route-print-pack`, `daily-ops-guardian` (Stage 0.5 + `queue-guard` Thu 15:50 + `sunday-prep` Sat 20:00). Portal tranches 136/137/138 (PRs #178/#177/#180). Backend T8 (#176) + G1 migration 0287 `v_production_plan_vs_actual`, applied prod & live-verified.

**Procurement corridor (2026-07-16/17)** — migrations 0284–0286 (PRs #170/#171) applied prod & live-verified; portal tranches 132–133 (PRs #172/#173); `procurement-planning` skill (PRs #41/#42). Fixed live bug: `item_type <> 'SYSTEM'` on a mostly-NULL column silently dropped 7 sellable BOUGHT_FINISHED lines per session → `IS DISTINCT FROM`.

**LionWheel FG_OUT bridge** — cutover 2026-05-10, continuous prod use since. `LIONWHEEL_FG_OUT_BRIDGE_ENABLED` behaviorally `true`. ⊥ flip back without Tom rollback decision + parity replay. Two legitimate reversal classes (delivery-correction; count-freeze-driven) ratified in `docs/decisions/LOCKED_DECISIONS.md` §LionWheel. `LIONWHEEL_PICK_ADJUSTMENT` = Tom-approved-manual-only; production code ⊥ emit it. Count-freeze race has operational fix: migration `0277_fg_out_movement_pause.sql` + portal tranche 118.

## Shopify sync — LIVE, verified 2026-08-01

**53/53** sellable items sync `*/5` via sole writer Edge Fn `shopify_available_reconcile` (SET `GREATEST(0, on_hand − committed)` → converges, ⊥ drift). ⊥ real-time: ≤ ~20 min for a Shopify order to reflect (Tom-accepted). Watchdogs cron 26 `*/15`: sync-health `0308` + second-writer tripwire `0310`, auto-resolving exceptions.
**Status = query, ⊥ this file:** `select private_core.run_shopify_sync_health('manual')`.
**All depth — architecture, traps, canonical queries, 0302–0311 history → skill `shopify-sync`.** The 2026-07-31 bullets that stood here (sync-writes-nothing, network_fail, 40 negatives, stale exceptions, "flag has no reader") are **resolved or superseded** — ⊥ act on old revisions.

Open (Shopify): **none.** Coverage = every ACTIVE sellable item mapped (0311, 0314). Corridor retired: cron 16+19 off (0312), 571 stale exceptions closed (0313), `shopify_fg_push` tombstoned. Exception inbox = 1 real item (`shopify_oversell:FG-MAT-30G`) + the `EXCLUDED-NONSTOCK` sentinel.
**⊥ raise the ~60 unmapped Shopify variants / Muzot lines (Tom 2026-08-01):** out of scope, ⊥ a sync gap — coverage runs system→Shopify. Detail: skill `shopify-sync`.

## Open — needs Tom

- **`audit_runs` empty — P2 reporting gap, ⊥ a stock-truth gap.** Table exists (0151), `row_count = 0`; it was specced for a Python multi-layer audit skill (`layer1_pct`..`layer5_pct`, `verdict`, `report_jsonb`, alert dispatch) that was never built. Blocked on `JOB_RUNNER_TOKEN` + container at `AUDIT_SCRIPT_PATH`.
  **⊥ confuse with nightly stock-truth verification, which runs and is green.** `cron.job` 12 `nightly_rebuild_verifier` (`0 3 * * *`, active) → `private_core.run_rebuild_verifier('cron_nightly')` → writes `private_core.job_runs`. **83/83 succeeded since 2026-05-11, `drift_count = 0` every run**, latest 2026-08-01 03:00 (217 keys, 1.2s). It auto-opens a critical `projection_drift` exception per drifted balance key and auto-resolves them at zero drift. `CLAUDE.md` §Source-of-truth "rebuild-verified nightly" is accurate.
- **Shopify storefront cleanup + capability activation** — `docs/plans/2026-08-26-shopify-storefront-cleanup.md`. Read live 2026-08-26: 377 products, 122 ACTIVE, 253 archived · **74 of the 122 (61%) at zero or negative stock** · production inputs (packaging, RM, a ₪5,000 sealing machine) and 12 customer private-label SKUs (Elita ×10, Babka ×2) publicly purchasable · 52/122 handles carry `copy`, several naming a different product. Reframing finding: **draft orders 10,000+ completed / 163 open vs 1 completed online checkout in 365d** — the storefront ⊥ the sales channel, the draft order is. Also unused: 0 marketing activities · 0 GT-owned product metafields · 2,969 email subscribers against 0 campaigns ever sent (Klaviyo). **⊥ fix inventory in Shopify** — we are authoritative, reconciler overwrites `available` every 5 min; negatives are a source-truth question, and whether un-publishing changes the FG sync surface is unanswered. 6 Tom decisions gate the work (storefront purpose · production inputs listed? · private-label public? · archived keep-or-delete · one email tool or two · the 163 open drafts).
- Maxim's portal user (email) — last piece of tranche 137. Dennis provisioned.
- Alex conversation — pack ready (`docs/factory-mapping/2026-07-22-alex-package-he.md`), gates rollout weeks 5–6.
- Telegram bot token + chat_id (monitoring alerts). `app_users` uuid for count import.
- Read-only verify exact Railway env literal for `LIONWHEEL_FG_OUT_BRIDGE_ENABLED`.

## Deferred (Tom decision, ⊥ blocking)

SQL `tier` semantics (portal now classifies from trace math, underlying tier still old floor-breach logic) · `cover_days` buffer over-buffers 81/81 components sampled — needs plan-aware formula · ₪-at-risk trend needs a "previous session" definition · `--fg-subtle` light-theme contrast 3.09:1 unaudited · A11Y-003/004/010 · Dorin persona split · Maiden LionWheel driver record · Sat customer reminder · widen CI `typecheck` to `api/src` · flaky `supabase` postinstall in CI · PO-header parity extension to `rebuild_verifier` (UNRESOLVED-LC-5, deferred since 2026-04; recovered from pre-lean archive audit 2026-08-01 — PO corridor has run months without it, ? still wanted) · production reporting ! accept actual-produced qty, ⊥ assume full 500L batch (Tom 2026-07-29: Sun 26/7 + Mon 27/7 tank batches ran but sat `OVERDUE` because RM collection wasn't logged cleanly first; worked around by hand-closing the two `production_plan` rows — checkmark only, qty unchanged; needs `backend-db-executor` design pass on "report production" to decouple confirmed output qty from RM-collection completeness).

Pre-lean-archive audit 2026-08-01 also verified: G-07 forecast audit-trigger & G-10 `forecast.publication` producer **built** (migrations 0026/0027) · April's `lionwheel_unknown_sku` bulk-close effectively done (~41 → 11 open, all newer instances, live in `/exceptions`) · every other pre-lean "open" item resolved, superseded, or already on a list above.

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
3. Shopify FG disagreement resolved wrong way — **we are authoritative; the reconciler overwrites Shopify from our truth every 5 min** (Tom 2026-08-01, now also in `CLAUDE.md` §Source of truth). Shopify owns only its order pipeline.
4. Green Invoice auto-creating components or auto-updating prices → corrupts price audit trail.
5. Admin CRUD mass-editing BOM or supplier mapping without approval gates.
6. Excel round-trip creeping back via any operator workflow that edits the workbook.
7. Empty ≠ green — a gate query returning 0 rows may mean the query is wrong (precedent: skill staleness-gate used `item_type='COMPONENT'`, never matches live taxonomy `RM`/`PKG`/`FG`, read green for weeks).
8. Restating a count that has a JSON source of truth → drift. Point at the file.
9. Grep proves what's in the repo, ⊥ what's live in prod — deployed Edge Functions/cron jobs/DB flags leave no source trace (cost: `0302`, twice — 2026-07-17 flag anomaly, 2026-08-01 orphan writer). `list_edge_functions` + direct table reads before claiming "no reader"/"nothing writes X". Periodically audit governance-sensitive tables (`feature_flags`, `active_mode.json`) for writes with no corresponding migration/commit — that mismatch is itself the signal, even when the code-level gate is separately intact.

## Reference

Current-state workbook: `GT_Factory_OS.xlsx` (source only, ⊥ preserve structure). Supporting: `GT_Master_Data.xlsx`, `GT_Playbook_HE_.xlsx`, `GT_Roadmap.xlsx`.
Live DB: Supabase `rvadsozabmxkkrktwgnv` (`gt-ops-prod`, PG17), Session-mode pooler via `DATABASE_URL_POOLED` — direct `db.*` host is IPv6-only.
Portal tranche history: `gt-factory-os-portal/docs/portal-os/registry.md` + `.../scorecard.md`. ⊥ duplicated here.
Reference PR numbers, ⊥ shas — local mains lag GitHub squash-merges.
