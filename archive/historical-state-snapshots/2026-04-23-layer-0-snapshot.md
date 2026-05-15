# Historical state snapshot — Layer 0 validation (2026-04-23)

> **Origin:** migrated verbatim from `CURRENT_STATE.md` §"Layer 0 validation — SUBSTANTIALLY COMPLETE (2026-04-23)" during Phase 8 Run F Wave 4 Hole 2 cleanup (2026-05-09). The corresponding sections in CURRENT_STATE.md were removed; this snapshot is the audit-trail preservation.
>
> **Type:** historical state snapshot. Not authoritative on current state. For current Gate 3 status, read `CURRENT_STATE.md`.
>
> **Date of original calibration:** 2026-04-23 (infrastructure validation + docs authored; superseded the 2026-04-18 calibration).

---

## Last calibration (as of 2026-04-23)

**Date:** 2026-04-23 (infrastructure validation + docs authored; supersedes 2026-04-18 calibration).

A subsequent calibration was recorded 2026-04-27 (Planning Tranche 3 CLOSED end-to-end: backend-db backend + portal Mode B both PASS; signal #17 emitted; Manual PO portal merged to main as commit `92efbb3` 2026-04-26).

---

## Layer 0 validation — SUBSTANTIALLY COMPLETE (2026-04-23)

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
- **Auth chain confirmed:** Tom submitted the form while authenticated; JWT resolved correctly to app_users row

**Closed-loop verification (all via direct DB query):**
- Step 5a — Ledger write: ✓ WASTE_POSTED row confirmed
- Step 5b — Projection update: ✓ `current_balances.calculated_on_hand=-0.01` for RAW-WHISKEY, `last_refreshed_at` = same as `posted_at` (synchronous trigger confirmed)
- Step 5c — Operator visibility: Tom confirmed via portal (submitted the form, saw success) — portal-side verification
- Step 5d — Planning input: ✓ `v_rm_stock_export` shows RAW-WHISKEY at -0.01; planning engine reads `current_balances` → next run will use updated value. 12,057 forecast_lines present. Most recent completed planning run: 2026-04-21 22:17 (pre-dates today's event — a new run post-event is recommended to confirm full round-trip).
- Step 5e — rebuild_verifier(): ✓ = 0 (confirmed after event)
- Step 5f — Exception path: ✓ CONFIRMED 2026-04-23 — exception `7283a2d2` (positive_adjustment, RAW-VODKA, qty=50, status=open); form_submission `56c1be71` (pending, NOT posted); `current_balances` RAW-VODKA=0.00 unchanged; zero ledger writes confirmed

**Noted issue — fix deployed:** `reported_by_snapshot` was `null` on the live event (display_name snapshot not captured). Fix committed `9633ebc` and deployed to Railway 2026-04-23 (deployment `c3d66703`, status=SUCCESS, health=ok). All future ledger writes from waste-adjustments (auto-post + approval path), goods-receipts, and production-actuals will now populate `reported_by_snapshot` correctly. The 2026-04-23 live event retains `null` as a historical artifact — acceptable.

**Total ledger movements to date (as of 2026-04-23):** 262 (includes 2026-04-17 smoke tests + that day's first real event)

**Layer 0 verdict (2026-04-23): CLOSED**
All 7 exit criteria confirmed: infrastructure healthy, first real stock event posted (WASTE_POSTED, `429b94d5`), ledger→projection chain verified, rebuild_verifier=0, planning round-trip confirmed (run_id=`0b53afb8`), `reported_by_snapshot` fix deployed (`9633ebc`, Railway `c3d66703`), exception/approval path confirmed (step 5f: exception `7283a2d2` fired, form_submission `56c1be71` pending NOT posted, `current_balances` unchanged). Tom declared CLOSED 2026-04-23.

**Permanent docs authored (2026-04-23):**
- `PRODUCTION/docs/operational_dataflow_blueprint.md`
- `PRODUCTION/docs/gap_registry.md`
- `PRODUCTION/docs/false_green_registry.md`
- `PRODUCTION/docs/tranche_log.md`
- `PRODUCTION/docs/lessons_learned.md`

**Date predecessor:** 2026-04-18 (prior Tom-authoritative calibration; gate-status framing under that calibration was superseded above by 2026-04-23 Layer 0 validation).
