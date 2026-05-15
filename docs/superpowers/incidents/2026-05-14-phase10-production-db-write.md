# Incident: Phase 10 Wave 10A — Test Writes Reached Production DB

**Date:** 2026-05-14
**Severity:** Medium — schema changes and test-row pollution on production DB; no data loss, no operational disruption, no customer impact.
**Status:** CONTAINED — recovery migration authored (0192), guardrails applied, awaiting Tom approval to apply 0192 to production.

---

## What Happened

During Phase 10 Wave 10A development (branch `feat/phase10-economics-wave10a`), migrations 0187–0191 were applied directly to the production Supabase project ("gt-ops-prod", eu-central-1) and 1,072 test-tagged rows were written to `private_core.fg_cogs_snapshots`.

The production DB is now ahead of the `main` branch. The development branch has not been pushed or merged.

---

## Root Cause

Three layers failed simultaneously:

**1. Shadow DB was decommissioned.** `DATABASE_URL_SHADOW` in `.env` pointed at `db.cwwulplflvoetopfargf.supabase.co`, a Supabase project that had been decommissioned. The hostname returned DNS NXDOMAIN. No shadow or dev DB existed as a replacement.

**2. `_run_pgtap.mjs` accepted `--allow-pooled` silently.** The pgTAP runner emitted a `WARNING:` line when `--allow-pooled` was used but did not block execution. The subagent implementer hit the DNS error on Task 1.1, found the documented fallback flag, and used it. All subsequent pgTAP runs (64 assertions across 0187, 0188, 0189, 0191) ran against the production pooled connection inside `BEGIN/ROLLBACK` blocks — safe in themselves, but established the pattern.

**3. TypeScript test suite had no production-connection guard.** `api/test/_test_env.ts` contained no check on the connection URL. The `cogs_snapshot_job.test.ts` and `cogs_snapshot_nightly_route.test.ts` test files invoked the real COGS snapshot job against the real production DB. The job writes one row per active item per invocation; the append-only trigger blocks DELETE so there was no rollback path. The tests were designed for a dev/shadow DB and ran on production.

**4. Migration runner had no production guard.** `scripts/_apply_migration.mjs` reads `DATABASE_URL_POOLED` from `.env` and applies migrations immediately, with no check that the target is production or non-production.

---

## Objects Created on Production (without main branch merge)

| Object | Type | Created by |
|---|---|---|
| `private_core.fg_cogs_snapshots` | append-only table (14 cols) | migration 0187 |
| `private_core.supplier_cost_drafts` | mutable staging table (18 cols) | migration 0188 |
| `private_core.v_fg_economics` | view (18 cols) | migration 0189 |
| `phase10-cogs-nightly` | cron.job row, active=false | migration 0190 |
| `private_core.fn_explode_bom_to_components(p_item_id text, p_qty qty_8dp)` | SQL function (STABLE) | migration 0191 |

All 5 objects are well-formed and match the spec. No existing schema was modified. No existing data was altered.

---

## Rows Written to Production

| Table | actor_snapshot | Rows | Distinct items | Last written |
|---|---|---|---|---|
| `private_core.fg_cogs_snapshots` | `<test:cogs_snapshot_job>` | 802 | 135 | 2026-05-14 11:18 UTC |
| `private_core.fg_cogs_snapshots` | `<test:cogs_snapshot_nightly_route>` | 270 | 135 | 2026-05-14 11:27 UTC |
| `private_core.supplier_cost_drafts` | — | 0 | — | — |

**Total test-tagged rows in fg_cogs_snapshots: 1,072. Non-test rows: 0.**

All 135 item_ids are real production items from `private_core.items`. The snapshot job ran against all active items and correctly computed COGS for 17 of them (the 17 FG SKUs that have complete supplier cost data). Those 17 values are mathematically correct. The 118 items with `cogs_complete=false` correctly reflect missing supplier cost data.

---

## Production Exposure at Time of Discovery

**`v_fg_economics` surfaced test-tagged rows.** The view's `latest_cogs` CTE had no `actor_snapshot` filter. It selected the most recent row per item_id by `event_at DESC` — which was the test-run rows (11:27 UTC). The view returned test-run COGS data for all 135 active items, including 17 real FG SKUs with computed `cogs_per_unit_ils` values.

**No live application route read `v_fg_economics`.** The economics read routes (Section 5 of the plan) had not been built. The deployed Railway API runs from `main`, which has no Phase 10 code.

**Cron entry was disabled.** `phase10-cogs-nightly` exists in `cron.job` with `active=false`. It cannot fire automatically.

**Railway and Vercel were not triggered.** The branch was never pushed.

---

## Recovery Decision (Tom approval 2026-05-14)

**Option 2 selected:** Add migration 0192 (`v_fg_economics_test_row_exclusion`) as a `CREATE OR REPLACE VIEW` that adds `WHERE actor_snapshot NOT LIKE '<test:%>'` to the `latest_cogs` CTE. This excludes all test-run rows from the view permanently without touching the append-only table data.

**Migration 0192 is authored but NOT applied to production.** Tom written approval is required before applying.

The test-tagged rows in `fg_cogs_snapshots` remain in the table permanently (append-only). They cannot be deleted. After migration 0192 is applied:
- The view will return `cogs_snapshot_at=NULL` for all items (since no non-test rows exist yet)
- Once a real nightly job runs (after the cron entry is activated at the G3 gate), non-test rows will populate and the view will return legitimate data
- The test-row filter in 0192 is carried forward verbatim into the Wave 10B view rebuild (migration 0195)

---

## Guardrails Applied (2026-05-14, local only — not yet pushed)

| File | Change |
|---|---|
| `scripts/_run_pgtap.mjs` | Removed `--allow-pooled` flag. DATABASE_URL_SHADOW is required; no fallback. Also added hostname check that refuses if DATABASE_URL_SHADOW contains the production project ref (`rvadsozabmxkkrktwgnv`). |
| `scripts/_apply_migration.mjs` | Added production project ref check. Halts if DATABASE_URL_POOLED contains `rvadsozabmxkkrktwgnv` unless `MIGRATION_ALLOW_PRODUCTION=confirmed` is set in the environment. |
| `api/test/_test_env.ts` | Added production project ref check at module load. Halts if DATABASE_URL_POOLED or DATABASE_URL contains `rvadsozabmxkkrktwgnv` unless `TEST_ALLOW_PRODUCTION_DB=confirmed` is set. |

---

## Current State (as of 2026-05-14)

| Item | State |
|---|---|
| Production DB vs main | **DB is ahead of main.** 5 schema objects + 1,072 rows exist on production; branch not merged. |
| v_fg_economics | Shows test-run data for 135 items. Migration 0192 (view patch) authored, not applied. |
| Branch | `feat/phase10-economics-wave10a` — 17 commits (16 feature + 1 guardrail). Not pushed. Not rebased. |
| Cron | Disabled (`active=false`). Safe. |
| Deployed Railway API | Running from `main`. No Phase 10 code deployed. No Phase 10 routes reachable. |
| Feature work | HOLD — Section 3 and beyond blocked until DB state is resolved and this branch is pushed/reviewed/merged. |

---

## Remaining Risks

1. **No shadow/dev DB exists.** Until `DATABASE_URL_SHADOW` is provisioned and set in `.env`, pgTAP tests and TypeScript tests cannot run. The new guardrails will hard-fail rather than fall back to production — correct behavior, but it means all DB-writing tests are blocked until a shadow DB is available.

2. **1,072 test rows are permanent.** `fg_cogs_snapshots` is append-only. The rows cannot be deleted. The view fix (migration 0192) makes them invisible to reporting, but they occupy storage indefinitely. A future cleanup path (e.g., a pruning procedure that bypasses the append-only guard for `actor_snapshot LIKE '<test:%>'` rows older than N days) is out of scope for v1.

3. **Migration 0192 not yet on production.** Until Tom approves and 0192 is applied, `v_fg_economics` continues to surface test-run data. Since no deployed route reads this view, operational impact is currently zero.

---

## Required Before Feature Work Resumes

- [ ] Tom approves migration 0192 for production apply
- [ ] 0192 applied to production (using `MIGRATION_ALLOW_PRODUCTION=confirmed` and documenting the apply here)
- [ ] Shadow/dev DB provisioned; `DATABASE_URL_SHADOW` updated in `.env`
- [ ] Branch pushed and PR opened (rebase onto main required first — activity log PR #25 landed after branch cut)
- [ ] PR reviewed and merged (Tom approval)
- [ ] Railway auto-deploy aligns repo and production

---

**Incident owner:** Tom (sole approver).
**Filed by:** AI brain (PRODUCTION), 2026-05-14.
