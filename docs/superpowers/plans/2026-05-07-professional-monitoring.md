# GT Factory OS — Professional Stock-Truth Monitoring Plan

> **For agentic workers:** REQUIRED — implement via `superpowers:subagent-driven-development` (one subagent per chunk, never inline). This file is plan-only. Execution is a separate, dispatched action.
>
> **Authoring session:** 2026-05-07. Plan-mode session; no code written here.
>
> **Successor to:** `2026-05-06-stock-event-perfect-flow.md` (Phase 0 + Phase 1 chunks 1–7 substantively done; Phase 2/3 remain). This plan **does not duplicate** the perfect-flow plan — it consumes its outputs (chain semantics, mapping_status enum, audit-skill 5 layers) and adds the operator-grade observability layer that the perfect-flow plan deferred.

---

## 0 · Mission

Every stock movement that happens in the real world (LionWheel delivery, Goods Receipt, Waste, Production, Count) shall appear automatically in `private_core.stock_ledger` within ≤15 minutes, **and** that fact shall be observable from outside the running session — by cron, by alert, by dashboard — so that Tom can rely on the system 24/7 without running ad-hoc SQL.

This is the line between "the chain runs" and "professional stock-truth observability." Today the chain *runs* (with a feature gate). After this plan, monitoring runs **autonomously**, alerting fires **automatically**, and a single `/dashboard/stock-health` page tells Tom whether the system is healthy without him having to ask.

---

## 1 · Tom-locked decisions (this session, 2026-05-07)

These four answers shape every chunk below. They are locked for the duration of this plan; revisiting them requires a plan amendment.

| Decision | Locked answer | Implication |
|---|---|---|
| **D-MON-1** Primary alerting channel | **Telegram** (existing `telegram:configure` skill) | B.2 builds a single Telegram dispatcher; CRITICAL → immediate DM, FAIL → morning summary. Email/Slack deferred. |
| **D-MON-2** Resolution source for unresolved SKUs / conversions | **Admin-portal worklists** (`/admin/sku-aliases` + `/admin/integrations`) | A.2 + A.3 + C.3 share the same UI substrate: a typed "needs-decision" worklist with one-click resolve actions, backed by `integration_sku_map` rows. No Excel cleanup track. |
| **D-MON-3** Dashboard route | **New `/dashboard/stock-health`** | C.1 ships an isolated route. `/dashboard/v2` is untouched. Deep links from Telegram alerts target `stock-health`. |
| **D-MON-4** Zone D (operator cutover) timing | **Parallel with B+C** | D.1 (training) and D.2 (Excel→read-only) start as soon as A.4 lands; D.3 (`daily-inventory-agent` strip-down) gates on 7 consecutive stable audit days. |

**Reaffirmed from CLAUDE.md (not relitigated here):** LionWheel pickup → ledger trigger is `ROUNDTRIP_DELIVERED`/`COMPLETED` only; ledger is append-only with reversal rows; UI shows names not IDs; English/LTR by default; 24h shadow soak before Shopify-write flip.

---

## 2 · Top-line success criteria (audit-skill measurable)

Plan is complete when **every** assertion below holds for **7 consecutive Israel-time days**:

1. **Latency ≤15 min** — for any LionWheel task transitioning to `ROUNDTRIP_DELIVERED`/`COMPLETED`, a `FG_OUT_PICK` row appears in `stock_ledger` within 15 minutes of the LW status change. Measured by `audit_runs.metrics_jsonb.lw_pick_latency_p95_seconds`.
2. **Coverage ≥99%** — Layer 1 (LW shipment coverage) and Layer 2 (qty variance) both ≥99% on every nightly run. Layer 4 (Shopify parity) ≥99% post-flip of `ENABLE_SHOPIFY_FG_WRITE`. Layer 5 (mass balance) ≥99%.
3. **Top-line verdict = PASS** — `run_audit.py --quiet --json` exits 0 every nightly run.
4. **Mean time to alert ≤5 min** — when `verdict ≠ PASS`, a Telegram message lands in Tom's DM within 5 minutes of `audit_runs.finished_at`.
5. **No silent failures** — `private_core.audit_runs` has one row per scheduled cron tick (success OR failure). Missing tick = the missing-tick watchdog (B.1.4) pages within 30 min.
6. **Exception SLA** — `private_core.exceptions` rows older than 24h auto-bump severity; older than 7d block planning runs (enforced by trigger added in B.3).
7. **Dashboard truth** — `/dashboard/stock-health` shows the same numbers as the audit JSON, refreshed within 60 seconds of the latest `audit_runs` row.
8. **Operator workflow** — for at least one continuous week, Goods Receipt + Waste + Production submissions come through the portal forms (not Excel), with `daily-inventory-agent` running in **read-only verification mode** only.

---

## 3 · Authoritative reference paths (used by every chunk)

- **Repo:** `C:/Users/tomw2/Projects/gt-factory-os` (canonical) and worktree `C:/Users/tomw2/Projects/gt-factory-os.worktrees/perfect-flow/` (preferred for this plan).
- **Migrations:** `gt-factory-os/db/migrations/` — next free slot **`0151`** (0149 + 0150 already applied to live Supabase per user message at session open).
- **pgTAP tests:** `gt-factory-os/db/tests/`
- **API:** `gt-factory-os/api/src/integrations/lionwheel/{reconciliation,poller,schemas,sku_resolver}.ts` (**LOCKED** — no edits in this plan).
- **API new modules:** `gt-factory-os/api/src/monitoring/` (new dir; alerting + audit-history reads).
- **Portal:** `portal/` (window2-portal-sandbox) — new route `/dashboard/stock-health`.
- **Audit skill:** `C:/Users/tomw2/.claude/skills/stock-event-accuracy-audit/scripts/run_audit.py` (extend with `--persist` flag in B.1; do not rewrite from scratch).
- **CLAUDE.md** (durable contract) — never edited by this plan.
- **CURRENT_STATE.md** — one pointer line added at end of this plan (last task, M.1 below).

---

## 4 · Plan map — 16 chunks across 4 zones

| Zone | Chunk | Workstream | Outcome (1 measurable acceptance) | Subagent type |
|---|---|---|---|---|
| **A — Foundation (1–3 days, sequential)** | A.1 | Bridge flip + soak | `LIONWHEEL_FG_OUT_BRIDGE_ENABLED=true` on Railway; `audit_runs` shows ≥1 `FG_OUT_PICK` row in last 24h; zero `fg_out_skipped_bridge_disabled` in 24h logs. | `executor-w1` |
| | A.2 | Unresolved SKU worklist (LW) | `/admin/sku-aliases` exposes the 229 unresolved LW SKUs with one-click resolve; queue size drops by ≥80% in 48h. | `executor-w2` |
| | A.3 | Conversion-unknown worklist (Shopify) | `/admin/integrations` exposes the 35 conversion-unknown Shopify SKUs; resolutions write `internal_units_per_shopify_unit` to `integration_sku_map`. | `executor-w2` |
| | A.4 | Shopify FG-write flip | `ENABLE_SHOPIFY_FG_WRITE=true` after 24h shadow; `daily-inventory-agent` Shopify-write call-sites hard-disabled (read-only verification only). | `executor-w1` + `executor-w4` |
| **B — Monitoring layer (3–5 days, mostly parallel after A.1)** | B.1 | Daily audit cron + `audit_runs` table | Migration 0151 lands `audit_runs`; Railway scheduled task fires `run_audit.py --persist` daily 06:00 IL; 7 consecutive rows present. | `executor-w1` + `executor-w4` |
| | B.2 | Telegram alerting dispatcher | Verdict ≠ PASS → DM in Tom's Telegram within 5 min; CRITICAL exception → DM within 5 min; PASS → silent. | `executor-w4` |
| | B.3 | Exception SLA enforcement | `exceptions.severity` auto-bumps at 24h; `>7d` open exception in `severity='high'` blocks `fn_start_planning_run` with named error. | `executor-w1` |
| | B.4 | Audit-history retention + archive | 90 days hot in `audit_runs`; older runs migrated nightly to `audit_runs_archive`; archive read-only. | `executor-w1` |
| | B.5 | Mass-balance Layer 5 hardening | Layer 5 covers multi-anchor histories, retired tasks, reversal-paired rows; pgTAP fixture proves correctness on 6 named edge cases. | `executor-w4` (audit skill author) |
| **C — Dashboard + UX (3–5 days, parallel with B)** | C.1 | `/dashboard/stock-health` route | Page renders top-line gauge + per-layer breakdown + 7d/30d trend, reading from `audit_runs`; SSR within 1s on cold cache. | `executor-w2` |
| | C.2 | `/dashboard/exceptions` typed cards | All open exceptions render as severity-coded cards with action buttons matching subtype guidance (per `feedback_action_buttons_match_guidance.md`). | `executor-w2` |
| | C.3 | Operator action surfaces | `/admin/sku-aliases?status=unresolved` and `/admin/integrations?conversion=unknown` are first-class worklists with counter banner on `/dashboard/stock-health`. | `executor-w2` |
| | C.4 | Severity banners on `/dashboard` | Negative-on-hand, stuck-in-flight, phantom-event banners surface on `/dashboard` (top-of-page) with severity color. | `executor-w2` |
| **D — Operator cutover (1–2 weeks, parallel with B+C)** | D.1 | Operator portal training | Tom + 2 operators submit ≥10 GR + ≥5 Waste forms via portal in one week; zero falls back to Excel for those event classes. | (Tom-led, no subagent) |
| | D.2 | Excel → nightly read-only export | Cron writes `GT_Factory_OS_export_<date>.xlsx` from curated read models nightly 22:00 IL; Excel master is no longer authored by hand. | `executor-w4` |
| | D.3 | `daily-inventory-agent` strip-down | After 7 stable audit days post-A.4, agent's FG-write call-sites are deleted (not flagged off); agent runs in read-only verification mode forever. | `executor-w1` |
| **M — Master close-out** | M.1 | `CURRENT_STATE.md` reconciliation + plan-tag | One-line pointer added to `CURRENT_STATE.md`; `git tag professional-monitoring-complete` after 7 stable audit days. | (post-D.3 final) |

**Phasing diagram:**

```
Day 1                Day 3        Day 7              Day 14            Day 21+
─┬─ A.1 (flip)       ─┬─ A.4 (Shopify flip)
 ├─ A.2 (LW worklist)  │
 ├─ A.3 (Shopify ws)   │
                       ├─ B.1 (audit cron)            ┐
                       ├─ B.2 (Telegram)              │
                       ├─ B.3 (SLA)                   ├─ 7-day soak ─┬─ D.3 strip-down
                       ├─ B.4 (retention)             │              ├─ M.1 close
                       ├─ B.5 (mass-balance harden)   │              │
                       │                              │              │
                       ├─ C.1 (stock-health)          │              │
                       ├─ C.2 (exceptions)            │              │
                       ├─ C.3 (worklists)             │              │
                       ├─ C.4 (banners)               │              │
                       │                              │              │
                       ├─ D.1 (training, parallel) ───┘              │
                       └─ D.2 (Excel read-only) ─────────────────────┘
```

**Critical-path pin:** A.1 blocks every B + C + D chunk. B.1 must precede B.2/B.3/B.4 (those write to or read from `audit_runs`). Inside B and C, all other chunks are independently dispatchable.

---

## 5 · Detailed chunks

Every chunk below specifies: **outcome**, **files**, **TDD sequence**, **rollback**, **subagent dispatch directive**.

---

### Chunk A.1 — LIONWHEEL_FG_OUT_BRIDGE_ENABLED flip + 24h shadow soak

**Outcome:** With the gate flipped, the next LionWheel poll cycle that observes a `ROUNDTRIP_DELIVERED`/`COMPLETED` task with `lw_qty_picked` populated **writes** a `FG_OUT_PICK` ledger row. Within 24h of flip, ≥1 such row exists; zero `fg_out_skipped_bridge_disabled` log lines occur in that window. `current_balances` for FG items decreases for shipped-out goods.

**Files (modify only):**
- Railway env var: `LIONWHEEL_FG_OUT_BRIDGE_ENABLED` (`false` → `true`) — set via Railway dashboard (no code change).
- Verification probe: `gt-factory-os/scripts/verify_bridge_post_flip.mjs` (new, ≤80 LOC).

**TDD sequence:**

1. **Pre-flip sanity (test before action)** — run audit skill, capture baseline:
   ```
   python "C:/Users/tomw2/.claude/skills/stock-event-accuracy-audit/scripts/run_audit.py" --days 7 --json > .audits/pre_a1_flip.json
   ```
   Assert in `verify_bridge_post_flip.mjs`: `pre_a1_flip.layer1.matched == 0` (no real picks yet) AND `phantom_events.length == 0`.

2. **Pre-flip mirror-state check** — query `private_core.orders_mirror_lines WHERE lw_pick_enrichment_status='enriched' AND ledger_movement_id IS NULL AND lw_qty_picked IS NOT NULL` — record count `N_pending`. After flip + first poll cycle, expect `N_pending` to drop by ≥1.

3. **Flip the gate** — Railway dashboard: set env var, redeploy. Capture deployment id.

4. **Wait one poll cycle** — GitHub Actions cron fires every 15 min; wait 20 min wall clock OR fire `POST /api/v1/internal/jobs/lionwheel-poll` manually with `JOB_RUNNER_TOKEN`.

5. **Post-flip verification** — `verify_bridge_post_flip.mjs` runs:
   - SQL: `SELECT count(*) FROM private_core.stock_ledger WHERE movement_type='FG_OUT_PICK' AND posted_at > '<flip_at>'` → must be ≥1.
   - SQL: `SELECT count(*) FROM private_core.orders_mirror_lines WHERE lw_pick_enrichment_status='enriched' AND ledger_movement_id IS NULL AND lw_qty_picked IS NOT NULL` → must be `< N_pending`.
   - Audit skill re-run: top-line should rise above pre-flip baseline; Layer 1 coverage > 0.

6. **24h soak** — `audit_runs` row at next 06:00 IL must show `verdict='PASS'` (or `'FAIL'` only on items unrelated to LW pick chain). If verdict regresses on LW layers, **rollback** (see below).

7. **Sign-off** — script writes `.audits/a1_signoff.md` summarizing flip time, first FG_OUT_PICK row id, soak status. Tom reviews + green-lights B and C.

**Rollback:** Set `LIONWHEEL_FG_OUT_BRIDGE_ENABLED=false` on Railway, redeploy. Already-posted `FG_OUT_PICK` rows are NOT deleted (ledger is append-only). To compensate, post `FG_OUT_PICK_REVERSAL` rows for any incorrect posts via admin script (this is a real possibility — the script exists in skeleton, not built; if A.1 rolls back, B.5 mass-balance Layer 5 must be authored before the rollback completes to identify which rows to reverse).

**Subagent dispatch:** `executor-w1`. Mode: live-DB allowed (verification queries). Strict scope: `verify_bridge_post_flip.mjs` only; **no edits to `reconciliation.ts` / `poller.ts` / `schemas.ts`**. Dispatch payload includes baseline JSON path, expected pre-flip/post-flip values, and explicit "do not edit chain code" guard.

---

### Chunk A.2 — `/admin/sku-aliases` unresolved-LW worklist

**Outcome:** Tom navigates to `/admin/sku-aliases?status=unresolved&channel=lionwheel`, sees a sortable table of 229 distinct unresolved `lw_sku` values with: count of orders affected, earliest/latest order date, suggested `item_id` from fuzzy match (top-3, `0..1` confidence), one-click "Resolve to <item>" / "Mark excluded_legacy_bundle" / "Mark non-stock" buttons. Each button writes one `integration_sku_map` row + recomputes `orders_mirror_lines.item_id` for all rows referencing that `lw_sku`. After 48h of Tom resolving the queue, `unresolved_count` drops by ≥80%.

**Files:**
- Modify: `portal/src/app/admin/sku-aliases/page.tsx` — add `status` + `channel` query params, status filter, severity-coded counts.
- Modify: `portal/src/app/admin/sku-aliases/route.ts` — add `GET ?status=unresolved` filter.
- New: `gt-factory-os/api/src/admin/sku-aliases/handler.resolve.ts` — `POST /api/v1/admin/sku-aliases/resolve` with body `{ source_channel, external_sku, action: 'resolve' | 'excluded_legacy_bundle' | 'excluded_non_stock' | 'pending', target_item_id? }`.
- New: `gt-factory-os/api/src/admin/sku-aliases/handler.suggest.ts` — `GET /api/v1/admin/sku-aliases/suggest?lw_sku=<sku>` returns top-3 fuzzy matches with confidence.
- New: `gt-factory-os/api/test/admin_sku_aliases_resolve.test.ts` — 8 cases.
- New: `gt-factory-os/db/tests/0151c_sku_alias_resolve.test.sql` — pgTAP for the back-fill trigger.

**TDD sequence:**

1. **Failing tests first** — write `admin_sku_aliases_resolve.test.ts`:
   - role-gate: viewer 403, operator 403, planner 200, admin 200
   - resolve action: writes `mapping_status='active' + item_id=<target>` row, back-fills `orders_mirror_lines.item_id` for that `lw_sku`
   - excluded_legacy_bundle: writes `mapping_status='excluded_legacy_bundle'`, does NOT back-fill `item_id`, exception emitted with category `lionwheel_legacy_bundle`
   - idempotent: same body twice → second call returns 200 `{ noop: true }`
   - audit trail: `change_log` row written with action `SKU_ALIAS_RESOLVED`
   - fuzzy suggest: returns at most 3, confidence ≥0.0, sorted desc
2. **Implement handlers** — `handler.resolve.ts` opens transaction: insert/update `integration_sku_map`, recompute `orders_mirror_lines.item_id` via `UPDATE ... FROM ... WHERE lw_sku = $sku AND item_id IS NULL`, emit `change_log`, optionally close any open `lionwheel_unresolved` exceptions for this sku.
3. **Implement portal page** — TanStack Query for the list endpoint, `<button>` rows trigger mutation. Hebrew labels per existing `/admin/sku-aliases` register; English fallback per `feedback_portal_ui_english_ltr.md`. Names not IDs (per `feedback_names_not_ids_in_ui.md`) — show `item_name`, not `item_id`, in the suggest dropdown.
4. **Run tests** — 8/8 PASS.
5. **Commit** — single commit per layer (DB → API → portal). 3 commits total.

**Rollback:** `git revert <commit_a2>`; the 229 unresolved SKUs are unchanged in DB. Any `integration_sku_map` rows Tom resolved during the rollback window stay resolved (which is fine — they're correct).

**Subagent dispatch:** `executor-w2` for portal + `executor-w4` for handler spec, then `executor-w1` for handler implementation. Dispatch in two waves: (1) handler + tests; (2) portal page after handler is green.

---

### Chunk A.3 — `/admin/integrations` conversion-unknown Shopify worklist

**Outcome:** Tom sees the 35 Shopify SKUs whose `internal_units_per_shopify_unit` is unset (or default `1.0` despite `pack_size != 1L` in the linked `items` row). Each row shows: `external_sku`, `item_name`, current `pack_size` from items master, last-known Shopify-on-hand vs internal-on-hand divergence (units), suggested conversion ("This SKU is a 6-pack → 6.0", etc.). One-click "Apply conversion = N" sets `internal_units_per_shopify_unit` and triggers a Layer 4 recompute on next audit.

**Files:**
- Modify: `portal/src/app/admin/integrations/page.tsx` — add tab "Conversion review" with the 35 rows.
- New: `gt-factory-os/api/src/admin/integrations/handler.set_conversion.ts` — `POST /api/v1/admin/integrations/sku-map/conversion` with body `{ external_sku, internal_units_per_shopify_unit, source_channel: 'shopify' }`.
- New: `gt-factory-os/api/src/admin/integrations/handler.list_conversion_unknown.ts` — `GET /api/v1/admin/integrations/sku-map/conversion-unknown`.
- New: `gt-factory-os/api/test/admin_integrations_conversion.test.ts` — 6 cases.

**TDD sequence:**

1. **Failing tests** —
   - role-gate: viewer 403, planner 403, admin 200 (conversion changes are admin-only)
   - validation: `internal_units_per_shopify_unit > 0` enforced (matches existing `integration_sku_map_units_positive` CHECK)
   - audit trail: `change_log` row with old/new conversion
   - idempotent on identical body
   - listing: returns rows where `internal_units_per_shopify_unit = 1.0` AND linked `items.pack_size != 1` (heuristic for "probably wrong")
   - explicit-set survives: setting conversion to `1.0` for a true-1L item writes `set_explicit_at` so it doesn't reappear in the worklist
2. **Implement** — straightforward UPDATE with `change_log` audit; back-compute Shopify-vs-internal divergence in the listing query for the UI.
3. **Portal** — uses existing `/admin/integrations` shell; one new tab.
4. **Commit + 6/6 PASS.**

**Rollback:** `git revert`; previously-set conversions stay (correct data is correct).

**Subagent dispatch:** `executor-w2` (portal) + `executor-w1` (handler). Wave-2 dependency on `executor-w4` for the contract doc `gt-factory-os/docs/integrations/sku_map_conversion_contract.md` first (≤1h work).

---

### Chunk A.4 — Shopify FG-write flip + agent read-only

**Outcome:** After 24h shadow soak with `ENABLE_SHOPIFY_FG_WRITE=false` and `factory-os` writes to a shadow log only, the gate flips to `true` AND `daily-inventory-agent`'s Shopify-write call-sites are guarded with a hard kill-switch (env `DAILY_AGENT_SHOPIFY_WRITE_DISABLED=true`). For 7 consecutive days, exactly one writer touches Shopify (Factory OS); audit Layer 4 ≥99%; `system_locks.shopify_fg_writer` row held by Factory OS only.

This chunk depends on **Chunk 8** of the prior `2026-05-06-stock-event-perfect-flow.md` plan being complete (the continuous Shopify FG writer code + active-writer mutex). If that chunk is not landed, A.4 cannot execute — flag and pause.

**Files (per existing perfect-flow chunk 8 already; this chunk is the *gate flip*, not the build):**
- Railway env: `ENABLE_SHOPIFY_FG_WRITE` (false → true), `DAILY_AGENT_SHOPIFY_WRITE_DISABLED` (new, set true).
- Verification: `gt-factory-os/scripts/verify_shopify_writer_post_flip.mjs` (new, ≤120 LOC).
- Documentation: append-only entry in `private_core.maintenance_log` with action `shopify_fg_write_flipped`.

**TDD sequence:**

1. **Verify perfect-flow chunk 8 landed** — query for `system_locks.shopify_fg_writer` row absence pre-flip, presence post-flip when writer runs. If chunk 8 missing → halt + flag to Tom.
2. **24h shadow** — set `ENABLE_SHOPIFY_FG_WRITE=false` but enable shadow logging mode (per chunk 8 design); Factory OS computes intended writes, logs to `private_core.shopify_write_shadow_log`. Audit skill Layer 4 (parity) compares shadow-intended vs actual Shopify on-hand.
3. **Shadow assert** — after 24h, ≥95% of shadow rows match Shopify within 0.5 units; remaining <5% fall into known categories (delivery in flight, count freeze active). If shadow doesn't match, halt + investigate.
4. **Disable agent FG write** — set `DAILY_AGENT_SHOPIFY_WRITE_DISABLED=true` in `daily-inventory-agent` config OR strip the call-sites if the agent is locally-run. Verify by running agent in dry-run: it logs "shopify_write_skipped: kill_switch_active" instead of POSTing.
5. **Flip gate** — `ENABLE_SHOPIFY_FG_WRITE=true`, redeploy.
6. **Wait one writer cycle** + verify `system_locks.shopify_fg_writer` row appears with `holder_name='factory_os'`.
7. **Post-flip 24h** — Layer 4 ≥99%. If regression, set gate back to false + agent flag back to false.

**Rollback:** Two-step: (1) `ENABLE_SHOPIFY_FG_WRITE=false`; (2) `DAILY_AGENT_SHOPIFY_WRITE_DISABLED=false`. The agent resumes Shopify writes within its next cron tick. Append-only `maintenance_log` records the rollback.

**Subagent dispatch:** `executor-w1` for verification script + `executor-w4` for shadow-log assertion. **No** runtime code changes in this chunk — pre-existing chunk 8 is the build; this is the operational flip. If chunk 8 not landed, dispatch `executor-w1` to it first as a precondition (out-of-plan work; flag to Tom).

---

### Chunk B.1 — Daily audit cron + `audit_runs` table

**Outcome:** Migration `0151_audit_runs.sql` lands; `private_core.audit_runs` exists with the schema below. Railway scheduled task fires `run_audit.py --persist --window 7d` daily at **06:00 Asia/Jerusalem**. After 7 days, `SELECT count(*) FROM audit_runs WHERE run_kind='scheduled_daily'` ≥7. Each row carries top-line + per-layer rates, verdict, and a JSON blob with the full report.

**Schema (Tom-reviewable in this plan; subagent implements verbatim unless flagged):**

```sql
CREATE TABLE private_core.audit_runs (
  audit_run_id      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  run_kind          text NOT NULL CHECK (run_kind IN
    ('scheduled_daily','adhoc','post_deploy','post_migration','rollback_check')),
  started_at        timestamptz NOT NULL,
  finished_at       timestamptz,                  -- NULL while running
  window_start      timestamptz NOT NULL,
  window_end        timestamptz NOT NULL,
  window_days       int NOT NULL,
  verdict           text CHECK (verdict IN
    ('PASS','FAIL','FAIL_NEG_BALANCE','INCOMPLETE','RUN_ERROR')),
  top_line_pct      numeric(6,2),
  layer1_pct        numeric(6,2),
  layer2_pct        numeric(6,2),
  layer3_pct        numeric(6,2),
  layer4_pct        numeric(6,2),
  layer5_pct        numeric(6,2),
  exit_code         int,
  metrics_jsonb     jsonb NOT NULL DEFAULT '{}'::jsonb,  -- counts, latencies, drift_skus, etc.
  report_jsonb      jsonb NOT NULL DEFAULT '{}'::jsonb,  -- full audit report
  alert_dispatched_at timestamptz,                -- set by B.2 when Telegram fires
  alert_dispatch_attempts int NOT NULL DEFAULT 0,
  alert_dispatch_error text,
  created_at        timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX audit_runs_started_at_idx
  ON private_core.audit_runs (started_at DESC);
CREATE INDEX audit_runs_run_kind_started_at_idx
  ON private_core.audit_runs (run_kind, started_at DESC);
CREATE INDEX audit_runs_verdict_started_at_idx
  ON private_core.audit_runs (verdict, started_at DESC) WHERE verdict <> 'PASS';

-- Append-only guard: rows are written once at run-start (started_at + run_kind),
-- updated once at finish (verdict + metrics + report + finished_at), and once
-- by the alerter (alert_dispatched_at). NO further writes allowed.
CREATE OR REPLACE FUNCTION private_core.audit_runs_append_only_guard()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF (OLD.finished_at IS NOT NULL AND NEW.finished_at IS NULL) THEN
    RAISE EXCEPTION 'audit_runs.finished_at cannot be unset';
  END IF;
  IF (OLD.verdict IS NOT NULL AND NEW.verdict IS DISTINCT FROM OLD.verdict) THEN
    RAISE EXCEPTION 'audit_runs.verdict immutable once set';
  END IF;
  -- alert_dispatched_at: allow first-set only
  IF (OLD.alert_dispatched_at IS NOT NULL
      AND NEW.alert_dispatched_at IS DISTINCT FROM OLD.alert_dispatched_at) THEN
    RAISE EXCEPTION 'audit_runs.alert_dispatched_at immutable once set';
  END IF;
  RETURN NEW;
END $$;

CREATE TRIGGER trg_audit_runs_append_only
  BEFORE UPDATE ON private_core.audit_runs
  FOR EACH ROW EXECUTE FUNCTION private_core.audit_runs_append_only_guard();
```

**Files:**
- New: `gt-factory-os/db/migrations/0151_audit_runs.sql`
- New: `gt-factory-os/db/tests/0151_audit_runs.test.sql` (≥10 pgTAP cases incl. immutability invariants)
- Modify: `C:/Users/tomw2/.claude/skills/stock-event-accuracy-audit/scripts/run_audit.py` — add `--persist`, `--run-kind`, `--db-url-env` flags. New module `audit_persist.py` next to it.
- New: `gt-factory-os/api/src/jobs/audit_run_job.ts` — thin wrapper Railway scheduled task invokes; spawns Python subprocess and tracks the started/finished `audit_runs` row.
- New: Railway service config — add scheduled task `audit_daily_06_il` (cron `0 3 * * *` UTC = 06:00 IL year-round given +03:00 fixed; revisit if DST policy changes).

**TDD sequence:**

1. Write `0151_audit_runs.test.sql` (≥10 cases): table + columns + indexes + verdict CHECK + run_kind CHECK + immutability triggers (3 cases: cannot unset finished_at, cannot change verdict, cannot rewrite alert_dispatched_at).
2. Apply migration; run pgTAP — 10/10 PASS.
3. Extend `run_audit.py`: add `--persist` and `--run-kind`. On startup, INSERT `started_at + run_kind + window` row → save audit_run_id. On finish, UPDATE the row with `finished_at + verdict + per-layer pcts + metrics + report`. Use a separate connection from the read connection so a long audit doesn't hold a write lock.
4. Local smoke: `python run_audit.py --days 7 --persist --run-kind adhoc` → row appears with full report.
5. Railway scheduled task: configure cron, deploy, observe first scheduled run lands. Confirm row appears 06:00 IL the next morning.
6. 7-day soak: assert ≥7 rows.
7. Commit.

**Rollback:** `DROP TABLE private_core.audit_runs CASCADE`; remove Railway scheduled task; revert `run_audit.py` changes. Audit data lost; recreate from JSON archives if needed (not currently archived — accept loss on rollback).

**Subagent dispatch:** `executor-w1` (DDL + pgTAP + handler wrapper); `executor-w4` (audit-skill `--persist` extension + dispatcher script). Wave-1 = migration; Wave-2 = audit-skill mod + Railway config.

---

### Chunk B.2 — Telegram alerting dispatcher

**Outcome:** Within 5 minutes of an `audit_runs` row landing with `verdict ∈ ('FAIL','FAIL_NEG_BALANCE')` OR a new `private_core.exceptions` row landing with `severity='critical'`, a Telegram message arrives in Tom's DM via the existing `telegram:configure` bot. Message contains: verdict, top-line %, the offending layer(s) and counts, and a deep link to `/dashboard/stock-health` (or to the relevant exception card). PASS verdicts are silent. The dispatcher is idempotent — re-dispatching the same `audit_run_id` is a no-op.

**Files:**
- New: `gt-factory-os/api/src/monitoring/telegram_dispatcher.ts`
- New: `gt-factory-os/api/src/monitoring/handler.dispatch_alerts.ts` — POST `/api/v1/internal/jobs/dispatch-alerts` (job-token-protected)
- New: `gt-factory-os/api/test/telegram_dispatcher.test.ts` — 7 cases (no real Telegram; mock fetch)
- Modify: `.github/workflows/lionwheel-poll-cron.yml` (or new `dispatch-alerts-cron.yml`) — fire `dispatch-alerts` every 5 min.
- New env vars: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_TOM_CHAT_ID` (Railway secrets).
- New table column: NONE — uses existing `audit_runs.alert_dispatched_at` (idempotency anchor).

**Message format (Tom-locked default; subagent must NOT improvise):**
```
🚨 Factory OS — verdict: FAIL  (top-line 87.4%)
Layer 1 (LW coverage): 96.1% ✅
Layer 2 (qty variance): 99.8% ✅
Layer 3 (sync freshness): 78.2% ⚠️  ← drift
Layer 4 (Shopify parity): 99.5% ✅
Layer 5 (mass balance): 91.0% ⚠️  ← drift

Top issues:
• 4 stuck-in-flight tasks >24h (layer 3)
• 2 mass-balance violations: FG-CAL-1L (delta 12.5L), RAW-VODKA (delta -3L)

→ https://gt-factory-os-portal.vercel.app/dashboard/stock-health?run=<id>
Run id: 3f4a... | Window 2026-05-06 → 2026-05-07
```

For CRITICAL exceptions:
```
🔴 CRITICAL — <exception.title>
Item: <item_name>  |  Category: <category>
Created: <created_at IL>  |  Age: 12 min

→ https://.../dashboard/exceptions?id=<exception_id>
```

**TDD sequence:**

1. **Failing tests** — `telegram_dispatcher.test.ts`:
   - PASS verdict → no fetch call
   - FAIL verdict → exactly one fetch call to `https://api.telegram.org/bot<token>/sendMessage` with parsed message
   - FAIL_NEG_BALANCE → distinct emoji + critical-tier subject
   - retry on 429: respects `retry_after` header up to 3 attempts
   - idempotent on `audit_run_id`: second dispatch with same id is no-op (`alert_dispatched_at` already set)
   - CRITICAL exception triggers separate code path (no audit_run_id involved)
   - dispatch failure: writes `alert_dispatch_error` + increments attempts; does NOT block future runs
2. **Implement** dispatcher: pure function `buildMessage(audit_run) → string`, side-effect function `sendTelegram(token, chat_id, text) → result`. Handler reads recent `audit_runs WHERE finished_at > now() - '15 min'::interval AND alert_dispatched_at IS NULL AND verdict <> 'PASS'`.
3. **5-min cron**: GH Actions `dispatch-alerts-cron.yml` calls `POST /api/v1/internal/jobs/dispatch-alerts` every 5 min with `JOB_RUNNER_TOKEN`.
4. **Smoke test:** insert a fake `audit_runs` row with verdict=FAIL via SQL, fire dispatcher, assert Telegram receives. Then run again — assert no second message.
5. **End-to-end soak**: cause a real FAIL by temporarily breaking the chain (e.g., set a bogus mapping) and confirm DM lands within 5 min. Revert the break.
6. Commit.

**Rollback:** `git revert`; the cron task can be removed via a second commit if rollback breaks tests.

**Subagent dispatch:** `executor-w4` for the message-format contract + `executor-w1` for the handler + `telegram-channel:configure` skill cross-load for token resolution. Wave-1 = pure-function tests (no network); Wave-2 = end-to-end smoke (Tom in the loop because real DMs).

---

### Chunk B.3 — Exception SLA enforcement (24h bump, 7d planning-block)

**Outcome:** A scheduled job (Railway) runs every 1h at HH:05; for every `private_core.exceptions` row with `status='open' AND severity='medium' AND created_at < now() - '24 hours'::interval`, it bumps `severity='high'` and writes a `change_log` row. For severity='high' AND created_at < now() - '7 days'::interval, the planning RPC `fn_start_planning_run` raises `RAISE EXCEPTION 'PLANNING_BLOCKED_BY_OLD_EXCEPTIONS' USING DETAIL = ...`. Acceptance: pgTAP fixtures prove the bump works at 24h0m + 1s and the planning block fires at 7d0h0m + 1s.

**Files:**
- New: `gt-factory-os/db/migrations/0152_exception_sla_enforcement.sql`
- New: `gt-factory-os/db/tests/0152_exception_sla_enforcement.test.sql`
- Modify: `gt-factory-os/api/src/exceptions/handler.list.ts` — add `age_bucket` column (`<24h`, `24h-7d`, `>7d`) for UI use.
- New: Railway scheduled task `exception_sla_hourly` (cron `5 * * * *` UTC).
- New: `gt-factory-os/api/src/jobs/exception_sla_job.ts` — hourly job invokes `private_core.fn_run_exception_sla_pass()`.

**TDD sequence:**

1. Write pgTAP `0152_exception_sla_enforcement.test.sql` (10 cases):
   - bump triggers at 24h0m + 1s
   - bump does NOT trigger at 23h59m
   - bump idempotent (already-high stays high, no double change_log)
   - resolved exception not affected
   - `fn_start_planning_run` rejects with named error when ≥1 high exception ≥7d
   - `fn_start_planning_run` succeeds when no >7d high exceptions
   - block message names the offending exception_ids
   - bypass: admin can override with `force=true` parameter (writes `change_log` action `PLANNING_RUN_FORCE_OVERRIDE`)
   - 7d threshold rounds down to second precision (no flapping)
   - SLA pass writes one `audit_runs` row with `run_kind='post_migration'` for traceability (or NOT — flag as `D-MON-OPEN-1`, see open-decisions)
2. Implement migration with `fn_run_exception_sla_pass()` + `fn_start_planning_run` block. Use existing planning-run RPC; modify in-place (Phase 5 lock); coordinate with `executor-w1` re. Phase 5 lock — this counts as a contract change.
3. Verify by inserting a fixture exception with `created_at = now() - '24h0m1s'::interval`, run the job, assert severity bumped.
4. Soak 24h with real data; assert ≥1 medium→high transition observed in `change_log` if any old exceptions exist.

**Open-decision flag:** **D-MON-OPEN-1** — should the SLA pass itself create an `audit_runs` row? My recommendation: NO; it's a write job, not an audit. Use `change_log` only. Flagging because it's reasonable to disagree.

**Rollback:** Drop the trigger / function; revert `fn_start_planning_run`. `change_log` history retained.

**Subagent dispatch:** `executor-w1`. Mode B authorization needed because this modifies a Phase-5-locked function (`fn_start_planning_run`); coordinate with `governor` agent for sign-off before dispatch.

---

### Chunk B.4 — Audit-history retention + archive

**Outcome:** Migration `0153_audit_runs_archive.sql` adds `private_core.audit_runs_archive` (same schema, no triggers, `STORAGE EXTERNAL` for jsonb columns). A nightly job (Railway, 03:00 IL) moves rows older than 90 days from `audit_runs` → `audit_runs_archive` in batches of 100. Archive table is read-only (REVOKE INSERT/UPDATE/DELETE on `archive_writer` role; only the move-job role retains INSERT). Acceptance: after 90 days of operation, `audit_runs` row count ≤ ~90; archive grows monotonically.

**Files:**
- New: `gt-factory-os/db/migrations/0153_audit_runs_archive.sql`
- New: `gt-factory-os/db/tests/0153_audit_runs_archive.test.sql`
- New: `gt-factory-os/api/src/jobs/audit_archive_job.ts` — nightly mover.
- New: Railway scheduled task `audit_archive_nightly` (cron `0 0 * * *` UTC = 03:00 IL).

**TDD sequence:**

1. pgTAP: archive table exists, same schema, indexes present, `audit_run_id` is the unique key (not regenerated).
2. Move-job test: seed 5 rows older than 90d + 5 newer; run move; assert 5 in archive + 5 in main; old archive rows immutable.
3. Job idempotency: re-run the move; nothing happens (rows already moved have unique-key conflict → ON CONFLICT DO NOTHING).
4. Permission test: connect as a non-admin role, attempt INSERT into archive → permission denied.
5. Soak: deploy; observe nightly job emits 0 moves until day 91.

**Rollback:** Stop the archive job; archive table can stay (read-only data). If schema bug: drop the table; data loss = whatever was moved (recoverable from jsonb_pg_dump if archived backups exist).

**Subagent dispatch:** `executor-w1`.

---

### Chunk B.5 — Mass-balance Layer 5 hardening

**Outcome:** Audit skill's Layer 5 covers the six edge cases below correctly; a fixture suite proves it. Currently Layer 5 uses `latest anchor + post-anchor delta` which fails on multi-anchor histories and ignores reversal pairs.

**Edge cases (Tom-confirmed during plan review):**
1. **Multi-anchor history** — item has 3 anchors (Jan, Feb, Mar). Audit must use the most recent anchor whose `created_at ≤ window_end`, not the absolute latest. (Today's code uses absolute latest — CORRECT for "current state" but incorrect for "windowed truth".) This case is FLAGGED as **D-MON-OPEN-2** below; Tom's decision needed before B.5 implementation.
2. **Reversal pair** — `FG_OUT_PICK -6` + `FG_OUT_PICK_REVERSAL +6` net zero; both must be summed (current code does this correctly; need a test asserting it stays so).
3. **Retired LionWheel task** — `orders_mirror.retired_at IS NOT NULL`; ledger row exists; mass-balance must still account for the qty_delta (ledger is source of truth, mirror retirement is a metadata fact).
4. **Anchor on the same microsecond as a `COUNT_ADJUST` row** — current code uses `>` not `>=` to avoid double-counting; assert with a fixture that exact-microsecond rows are not double-counted.
5. **Items with zero ledger activity but a stale `current_balances`** — formula: `expected = anchor_qty + 0`; actual = whatever's in current_balances. If they diverge, that's a real drift (current_balances trigger missed an event → bug). Layer 5 should report this as a violation.
6. **Newly-created item with no anchor and no ledger** — `expected = 0`, `actual = 0` → match. Don't crash.
7. **Item with anchor_at > anchor.created_at by a clock-skew margin** — should NEVER happen, but Layer 5 should not silently accept it. Emit `data_quality` warning.

**Files:**
- Modify: `C:/Users/tomw2/.claude/skills/stock-event-accuracy-audit/scripts/run_audit.py` — Layer 5 SQL refactored to handle case 1 correctly (windowed anchor selection), case 5 explicitly tested, case 7 emits data_quality.
- New: `C:/Users/tomw2/.claude/skills/stock-event-accuracy-audit/tests/test_layer5_fixtures.py` — pytest with 6 fixtures covering above. Uses an isolated test schema or mocked DB.
- New: `C:/Users/tomw2/.claude/skills/stock-event-accuracy-audit/references/layer5-edge-cases.md` — reference doc with the 6 cases + expected behaviors.

**TDD sequence:**

1. **Fixture fixtures first** — author the 6 test cases in `test_layer5_fixtures.py` as failing tests against the current code. Tests should fail on case 1 (multi-anchor) and case 7 (clock skew); pass on the others (current code correctness).
2. **Tom-review the cases** — flag D-MON-OPEN-2 (windowed-anchor semantics) before implementing.
3. **Implement** — refactor Layer 5 SQL to:
   - SELECT the anchor where `created_at = (SELECT max(created_at) FROM balance_anchors_current WHERE item_id = sl.item_id AND created_at <= window_end)`
   - Compute deltas with `posted_at > anchor.created_at AND posted_at <= window_end`
   - Add a clock-skew check: if `anchor.anchor_at > anchor.created_at + 1 minute`, emit data_quality warning
4. **Run tests** — 6/6 PASS.
5. **Commit** + run nightly audit; assert Layer 5 reports the same top-line as before for healthy items, flags new violations only on real drift.

**Open-decision flag D-MON-OPEN-2:** windowed-anchor semantics — should Layer 5 use the anchor at `window_end` (windowed truth) or the absolute-latest anchor (current truth)? My recommendation: **windowed truth**. A user asking "was the system consistent over the past 7 days?" wants the anchor that was in force during that window, not one created today.

**Rollback:** revert audit-skill commit; Layer 5 reverts to current behavior (which is mostly correct for steady-state).

**Subagent dispatch:** `executor-w4` (audit-skill author). No DB writes. Pure read + Python refactor.

---

### Chunk C.1 — `/dashboard/stock-health` route

**Outcome:** Tom navigates to `https://gt-factory-os-portal.vercel.app/dashboard/stock-health` and sees:
- **Top-line gauge** (large): top-line % from latest `audit_runs` row, color-coded (≥99% green, 95-99% yellow, <95% red).
- **Per-layer breakdown** (5 stacked bars): Layer 1–5 with rates + matched/total + ⚠️ if skipped.
- **7-day trend chart**: top-line %, x-axis days, simple SVG line chart.
- **30-day trend chart**: same, longer.
- **Last run metadata**: started_at IL, window, run_kind, alert_dispatched_at if set, deep link to raw report jsonb.
- **Drill-down per item** (tab): table of items with mass-balance violations, layer-3 stuck-in-flight, layer-1 unmatched shipments. Click a row → modal with the full ledger entries for that item.

**Files:**
- New: `portal/src/app/dashboard/stock-health/page.tsx`
- New: `portal/src/app/dashboard/stock-health/route.ts` (data loader, role-gated planner+admin)
- New: `portal/src/components/dashboard/StockHealthGauge.tsx`
- New: `portal/src/components/dashboard/LayerBreakdown.tsx`
- New: `portal/src/components/dashboard/TrendChart.tsx` (no external chart lib in v1; raw SVG)
- New: `portal/src/components/dashboard/ItemDrillModal.tsx`
- New: `gt-factory-os/api/src/queries/audit-runs/handler.list.ts` — `GET /api/v1/queries/audit-runs?days=30` returns array of (audit_run_id, started_at, top_line_pct, layer_pcts, verdict).
- New: `gt-factory-os/api/src/queries/audit-runs/handler.get.ts` — `GET /api/v1/queries/audit-runs/:id` returns full report_jsonb + metrics_jsonb.
- New: `gt-factory-os/api/test/audit_runs_queries.test.ts` — 5 cases.

**Audience gate:** planner + admin only (per `project_inbox_audience_planner_admin_only.md`). Operator + viewer get 403 with helpful message ("This page is for planning + admin users").

**TDD sequence:**

1. Failing tests: list endpoint returns rows ordered by started_at desc, capped at `?days=`; get endpoint returns 200 with full report or 404; both gated planner+admin only.
2. Implement endpoints + react-query hooks.
3. Implement page with mock data first (storybook-ish), then wire to real endpoints.
4. Verify SSR < 1s on cold cache (Vercel deployment timing).
5. Names not IDs: drill-down modal shows `item_name` (not `item_id`) primarily; ID is small subtitle.
6. English/LTR copy default; Hebrew labels only where existing register dictates (no new register entries needed for this page — defaults English).
7. Commit.

**Rollback:** `git revert` portal commit; the page becomes 404. Audit data remains intact.

**Subagent dispatch:** `executor-w2` (portal — Mode B amendment needed for `/dashboard/stock-health`; coordinate with governor) + `executor-w1` (queries handlers).

---

### Chunk C.2 — `/dashboard/exceptions` typed cards

**Outcome:** Existing `/admin/exceptions` (or wherever exceptions surface today) is replaced or supplemented by `/dashboard/exceptions`. Each open exception renders as a typed card (Decision / To-Do / Warning / Info per `project_inbox_audience_planner_admin_only.md`); action buttons match subtype guidance from `feedback_action_buttons_match_guidance.md` (single source of truth: `SUBTYPE_ACTIONS` map). Severity color (high=red border, medium=yellow, low=gray). Filter chips: severity, age (`<24h`, `24h-7d`, `>7d`), category. One-click resolve / dismiss / "open in PO" / "seed alias" inline.

**Files:**
- New or extend: `portal/src/app/dashboard/exceptions/page.tsx`
- New: `portal/src/components/exceptions/ExceptionCard.tsx`
- New: `portal/src/components/exceptions/SubtypeActions.ts` (the `SUBTYPE_ACTIONS` map — single source of truth for body + buttons)
- Existing handler: `gt-factory-os/api/src/exceptions/` — verify list endpoint supports filtering by `age_bucket`, `severity`, `category`.

**TDD sequence:**

1. Verify SUBTYPE_ACTIONS map matches existing card-type → action mapping; add new categories as needed (`lionwheel_unresolved`, `shopify_drift`, etc.).
2. Failing portal e2e (Playwright): page renders 3 fixture exceptions with correct cards + buttons.
3. Implement components + page.
4. Verify role-gate (planner+admin only).
5. Verify deep-link target: `?id=<exception_id>` opens that card focused.
6. Commit.

**Rollback:** `git revert`; if it replaced an existing surface, the existing one stays (don't delete the old route in this chunk).

**Subagent dispatch:** `executor-w2`.

---

### Chunk C.3 — Operator action surfaces (`/admin/sku-aliases?status=unresolved` etc.)

**Outcome:** Counter banner on `/dashboard/stock-health`: "229 SKUs need seeding" + link, "35 conversion-unknown" + link. Both link to filtered worklists implemented in A.2 + A.3. The counter recalculates on each page load (cheap query: `SELECT count(*) FROM integration_sku_map WHERE mapping_status = 'pending_item_creation' OR (item_id IS NULL AND source_channel='lionwheel')`).

**Files:**
- Modify: `portal/src/app/dashboard/stock-health/page.tsx` — add `OperatorWorklistBanner` block.
- New: `portal/src/components/dashboard/OperatorWorklistBanner.tsx`
- New: `gt-factory-os/api/src/queries/worklists/handler.counts.ts` — `GET /api/v1/queries/worklists/counts` returns `{ unresolved_lw: int, conversion_unknown_shopify: int, ... }`.

**TDD sequence:**

1. Failing test: counts endpoint returns expected shape.
2. Implement + integrate banner.
3. Verify clicking banner navigates to filtered worklist.
4. Verify the banner shows zero state ("All SKUs mapped ✅") when both counts are 0.
5. Commit.

**Rollback:** revert C.3; banner disappears; worklists still accessible directly.

**Subagent dispatch:** `executor-w2`.

---

### Chunk C.4 — Severity banners on `/dashboard`

**Outcome:** Top of `/dashboard` (existing v2) shows up to 3 severity-coded banners:
- 🔴 **Negative on-hand**: "<N> items are at negative stock" (from `current_balances WHERE calculated_on_hand < 0`)
- 🟠 **Stuck in flight**: "<N> tasks have been ROUNDTRIP_DELIVERED >24h with no FG_OUT_PICK ledger row"
- 🟡 **Phantom events**: "<N> ledger rows reference orders_mirror_lines that don't exist"

Each banner: severity color, headline, count, "View details →" button to drill-down. Auto-dismiss when count = 0.

**Files:**
- Modify: `portal/src/app/dashboard/v2/page.tsx` (or wherever `/dashboard` lives) — add `SeverityBanners` block at top.
- New: `portal/src/components/dashboard/SeverityBanners.tsx`
- New: `gt-factory-os/api/src/queries/dashboard/handler.severity_banners.ts` — single endpoint returns all three counts in one call (cheap).

**TDD sequence:**

1. Failing tests for banner counts query; assert correct SQL semantics.
2. Implement + portal integration.
3. Verify each banner deep-links correctly: negative → `/dashboard/stock-health?filter=negative`; stuck → `?filter=stuck-in-flight`; phantom → `?filter=phantom`.
4. Commit.

**Rollback:** revert; banners disappear; underlying data still accessible via `/dashboard/stock-health`.

**Subagent dispatch:** `executor-w2`.

---

### Chunk D.1 — Operator portal training (Tom-led, no subagent)

**Outcome:** Tom + 2 operators run for 1 week using portal forms (`/ops/stock/goods-receipts`, `/ops/stock/waste-adjustments`, `/ops/stock/production-actual`, `/ops/stock/physical-counts`) instead of Excel. Tom captures friction in `PRODUCTION/operator_training_log_2026-05-XX.md`. Acceptance: ≥10 GR + ≥5 Waste + ≥3 Production submissions land via portal in week 1; Tom personally signs off "operators can do daily flow without me".

**Files:** `PRODUCTION/operator_training_log_2026-05-XX.md` (Tom-authored).

**TDD sequence:** N/A (operational training).

**Rollback:** Operators resume Excel; agent keeps writing FG to Shopify; A.4's flip stands.

**Subagent dispatch:** None. Tom-led. Optional: `general-purpose` agent for capturing weekly check-in summary into the log.

---

### Chunk D.2 — Excel → nightly read-only export

**Outcome:** A nightly job at 22:00 IL runs `gt-factory-os/scripts/export_excel_readonly.mjs` which reads curated read-models (current_balances, recent ledger, open POs, exceptions, audit_runs) and writes `GT_Factory_OS_export_<YYYY-MM-DD>.xlsx` to `PRODUCTION/exports/`. This file is **never** read back by the system; it's a human-readable archive only.

**Files:**
- New: `gt-factory-os/scripts/export_excel_readonly.mjs`
- New: Railway scheduled task `excel_export_nightly` (cron `0 19 * * *` UTC = 22:00 IL).
- New: `gt-factory-os/api/test/excel_export.test.ts` (smoke: file produced, shape correct, opens in openpyxl).

**TDD sequence:**

1. Failing test: script writes file; openpyxl loads it without errors; sheet names match contract.
2. Implement reads + xlsx writer (using `exceljs` or similar).
3. Verify zero round-trip: existing Excel-import tools refuse to consume this export (file has a hidden marker sheet `_EXPORT_ONLY_DO_NOT_REIMPORT`).
4. Soak: 7 nights, file appears each night.
5. Commit.

**Rollback:** Disable the cron task; old exports stay on disk.

**Subagent dispatch:** `executor-w4`.

---

### Chunk D.3 — `daily-inventory-agent` strip-down

**Outcome:** After 7 consecutive PASS audit verdicts post-A.4, the agent's Shopify-write call-sites are deleted (not flagged off — physical removal). The agent's role contracts to: read from Shopify, read from Factory OS, output a daily reconciliation report to Telegram (parallel to B.2 channel, not redundant), run no writes. The skill description in `~/.claude/skills/daily-inventory-agent/SKILL.md` is updated to "read-only verification mode".

**Files:**
- Modify: `~/.claude/skills/daily-inventory-agent/SKILL.md` — strip `update Shopify on-hand` from its "what it does" section; add explicit "DOES NOT WRITE TO SHOPIFY (since 2026-05-XX)".
- Modify: `~/.claude/skills/daily-inventory-agent/scripts/*` — delete Shopify-write functions; preserve Shopify-read functions for verification.
- Tom signs off on a final read-only-mode run by reviewing one report.

**TDD sequence:**

1. **Pre-condition:** 7 PASS audit days post-A.4 verified by `audit_runs` query.
2. **Behavioral test before deletion** — run agent in current state, capture output baseline.
3. **Delete Shopify-write code paths** — leave reads.
4. **Run agent again** — output should still produce the daily report; the delta vs Factory OS should be zero (or near-zero) because A.4 ensured Factory OS is the writer.
5. **SKILL.md updates** — Tom reviews + approves.
6. Commit.

**Rollback:** Restore from git history. Re-enable agent's writes by setting `DAILY_AGENT_SHOPIFY_WRITE_DISABLED=false`.

**Subagent dispatch:** `executor-w1`. Coordinate with Tom on agent skill — that's a personal-skill modification, not a Factory OS change.

---

### Chunk M.1 — Close-out: `CURRENT_STATE.md` reconciliation + tag

**Outcome:** After 7 stable post-D.3 days, append a one-line pointer to `CURRENT_STATE.md` under the active corridor section, citing this plan + the closure date. Tag the canonical repo `professional-monitoring-complete-2026-XX-YY`.

**Files:**
- Modify: `PRODUCTION/CURRENT_STATE.md` — single line in active-corridor section.
- `git tag` on `gt-factory-os` main.

**TDD sequence:** N/A. Close-out is a documentation + tagging step.

**Rollback:** N/A.

**Subagent dispatch:** None. Tom + governor sign-off.

---

## 6 · Open decisions still requiring Tom's input

- **D-MON-OPEN-1** (B.3) — should the SLA-pass job create an `audit_runs` row? Recommendation: NO. Awaiting Tom confirmation before B.3 dispatch.
- **D-MON-OPEN-2** (B.5) — windowed-anchor vs absolute-latest-anchor semantics in mass-balance? Recommendation: windowed-anchor. Awaiting Tom confirmation before B.5 dispatch.
- **D-MON-OPEN-3** (cross-cutting) — Telegram chat-id provisioning. The `telegram:configure` skill needs to confirm Tom's chat_id is stored as `TELEGRAM_TOM_CHAT_ID`. If not yet stored, A.4 + B.2 cannot fire. Tom should run `/telegram:configure` to verify.

---

## 7 · Rollback master table

| If chunk fails | Rollback action | Data loss? |
|---|---|---|
| A.1 | Set `LIONWHEEL_FG_OUT_BRIDGE_ENABLED=false`; redeploy. | None (ledger append-only; bad rows reversed via FG_OUT_PICK_REVERSAL admin script). |
| A.2 | `git revert`; resolved aliases remain (correct). | None. |
| A.3 | `git revert`; set conversions remain. | None. |
| A.4 | Two-step: gate=false, then agent kill-switch=false. | None (Shopify resumes agent writes within 1 cron cycle). |
| B.1 | DROP TABLE audit_runs; remove cron. | All audit history lost (acceptable since fresh feature). |
| B.2 | `git revert` + remove cron. | None (alerts may have been missed during outage). |
| B.3 | Drop trigger + revert `fn_start_planning_run`. | None (severity bumps stay; behaviour reverts). |
| B.4 | Stop archive job; archive table can stay. | None (data still queryable). |
| B.5 | Revert audit-skill commit. | None (Layer 5 reverts to mostly-correct steady-state behavior). |
| C.1 | `git revert`; page becomes 404. | None. |
| C.2 | `git revert`; existing exception surface stays. | None. |
| C.3 | `git revert`; banner disappears; worklists still accessible. | None. |
| C.4 | `git revert`; banners disappear. | None. |
| D.1 | Operators resume Excel; agent keeps writing. | None (training log archived). |
| D.2 | Disable cron; old exports stay on disk. | None. |
| D.3 | Restore from git; re-enable agent writes via env flag. | None. |

---

## 8 · Out of scope (deliberate)

- **Forecast freshness audit** — separate audit + plan; tracked via `forecast.publication` freshness producer.
- **Green Invoice price ingest accuracy** — not a stock-truth concern; separate plan.
- **Customer pricing / FEFO / multi-location / bin tracking** — v1 contract excludes (CLAUDE.md §"Recommended v1 scope").
- **Excel cleanup for historical workbooks** — D.2 only writes new exports; cleaning prior workbooks is operational housekeeping.
- **iOS / mobile app for the dashboard** — Telegram covers mobile alerting; a mobile dashboard is a future plan.
- **Multi-warehouse / multi-site monitoring** — v1 is GT-MAIN site only.

---

## 9 · Subagent dispatch summary (for the implementer of this plan)

| Subagent | Owns chunks | Notes |
|---|---|---|
| `executor-w1` | A.1 (verify), A.4 (verify), B.1 (DDL + handler), B.3, B.4, D.3 | Live-DB authority. Phase-5 lock waiver needed for B.3 (`fn_start_planning_run` modification) — coordinate with `governor`. |
| `executor-w2` | A.2 (portal), A.3 (portal), C.1, C.2, C.3, C.4 | Mode B-Stock-Health amendment to EXECUTION_POLICY.md needed before C.1 — `/dashboard/stock-health` is a new pan-portal surface. |
| `executor-w4` | A.2 (handler spec), A.3 (handler spec), B.1 (audit-skill `--persist`), B.2 (Telegram contract + dispatcher), B.5 (audit-skill Layer 5 refactor), D.2 | Audit-skill custodian. |
| `governor` | All gate-flips (A.1, A.4) sign-off; Mode B amendments | No code; governance only. |
| `verifier` | Every chunk's acceptance | Runs after subagent claims completion. |

---

## 10 · Master acceptance — does the plan succeed?

The plan succeeds when **all eight assertions in §2** hold for 7 consecutive Israel-time days. Tag `professional-monitoring-complete-2026-XX-YY` is created. `CURRENT_STATE.md` has one new pointer line. The audit cron has fired ≥7 times with verdict=PASS. Telegram has received a non-zero number of test alerts (manually triggered) and zero spurious alerts. Tom signs off.

This plan **does not** count UI rendering as "done" (per `feedback_build_doctrine.md`). Acceptance is parity, invariants, and the golden-path live audit-cron PASS streak.

---

*Authored 2026-05-07 in plan-mode session. No code changes shipped during authoring. Implementation requires explicit Tom dispatch — start with Chunk A.1 once D-MON-OPEN-3 (Telegram chat-id provisioning) is confirmed.*
