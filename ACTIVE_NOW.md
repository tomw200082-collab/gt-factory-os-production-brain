# GT Factory OS — Active Now

> **Authority:** ephemeral operator context. **Not authoritative on anything.** `CURRENT_STATE.md` is the sole authority on gate status, completion range, critical path, and open gaps. On any disagreement, defer to `CURRENT_STATE.md`.

**Last refreshed:** 2026-07-17 (procurement corridor audit + rebuild). See `CURRENT_STATE.md` §"Procurement corridor — audit + rebuild (2026-07-16/17)" for full detail: backend migrations 0284-0286 (`gt-factory-os` PRs #170/#171), portal tranches 132-133 (`gt-factory-os-portal` PRs #172/#173), procurement-planning skill upgrades (this repo, PRs #41/#42) — all merged and live-verified. Current tips: brain `148ea88`, backend `20a50fb`, portal `1d18166`.

**Prior refresh (2026-05-23, post-cutover reconciliation, preserved as history):** Sunday 2026-05-10 LionWheel FG_OUT bridge cutover EXECUTED. Bridge in continuous production use through 2026-05-21+. Backend tip `bc2d34d` 2026-05-18; portal tip `5dfb549` 2026-05-18 (both ~10 days past Run G). `rebuild_verifier() = 0` confirmed 2026-05-23 via Supabase MCP read-only audit. Brain authority docs patched to record post-cutover truth and ratify reversal-class semantics — see `CURRENT_STATE.md` §"Post-cutover state (2026-05-10..2026-05-23)" and the `LOCKED_DECISIONS.md` §LionWheel amendments (Tom direct edit, same PR).

**Everything between 2026-05-23 and 2026-07-16 not named above (Shopify Gate E, LionWheel monitoring follow-ups, the ~11 portal tranches 090/119-131 shipped in that window, etc.) has not been re-verified in this refresh** — see the coverage note at the top of the new `CURRENT_STATE.md` section.

---

## Phase 8 Run F / F.2b / G — state

**Run F landed (2026-05-08):** AI Brain kernel rewrite — CLAUDE.md 355 → 133 lines; 6 scaffolding files in PRODUCTION root; 2 extraction files in docs/; 6 commits on main.

**Run F.2b completed (2026-05-08):** PRODUCTION remote established — `https://github.com/tomw200082-collab/gt-factory-os-production-brain.git` (private), HEAD `875424b`. No product code touched.

**Run G in progress (2026-05-08):** patching SIGNALS.md (CONFLICT-003 closed), CURRENT_STATE.md, ACTIVE_NOW.md, COMMAND_REGISTRY.md count fix, PRODUCTION-REMOTE-PLAN.md status, FINAL_AI_BRAIN_ACCEPTANCE.md creation. Branch `run-g-final-brain-closure`. PR pending Tom merge.

---

## Two active corridors

**1 — Shopify External Boundary v2**
Phase 0+1+2+3+4 landed. Gate E (Option C — SKU allowlist guard) in execution.
Hard stop: no live GraphQL inventory mutation until Phase 5 readiness + Tom approval.
Bridge state: `SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED=false` — do not flip.
Latest backend commit: `bcb2d0f` (GE-D bridge starvation fix).

**2 — Planning Corridor v1 (Tranche 3 CLOSED 2026-04-27)**
Tranches 1+2+3 DONE end-to-end. RUNTIME_READY(Planning-Tranche3-Blockers) emitted as signal #17.
Backend tip for Tranche 3: `1209596` (Railway `ef03b588`); portal closure: `e7dce27` (window2-portal-sandbox/main).
W2 currently in Mode A (`active_mode.json` last_updated 2026-05-02T22:00Z, no scoped form).
Tranche 4+ (Forecast Workspace) queued; later cycles (cycles 7–8 closure incl. signal #25 + #26 holidays-archived-filter) shipped.

---

## Key live state

| Item | Value |
|------|-------|
| RUNTIME_READY signals | 35 on file as of 2026-05-08; post-cutover re-count pending against `.claude/state/runtime_ready.json` |
| W2 portal tip | `5dfb549` (2026-05-18 — production-simulation date-range plan mode PR #36) |
| Backend tip | `bc2d34d` (2026-05-18 — Railway redeploy; last code commit `d81af0f` 2026-05-18 PR #38) |
| Railway | healthy |
| Vercel (portal) | ready — `gt-factory-os-portal.vercel.app` |
| LionWheel bridge | **behaviorally `true`** — cutover EXECUTED Sunday 2026-05-10; 487 `FG_OUT_PICK` rows in live ledger as of 2026-05-21; `rebuild_verifier() = 0`. Exact Railway env-var literal `NEEDS_READONLY_VERIFICATION` (Tom decision 2026-05-23: do not read or write env vars in this docs cycle). |
| Sunday 2026-05-10 | **EXECUTED.** 29 cutover-day rows; ramp to 103 rows/day by 2026-05-14; 29 count-freeze reversals 2026-05-13; 6 Tom-approved manual `LIONWHEEL_PICK_ADJUSTMENT` backfill rows 2026-05-17. Runbook `docs/superpowers/runbooks/2026-05-10-sunday-cutover-runbook.md` is the historical reference. |

---

## Open Tom decisions (blocking next dispatch)

- **Read-only verify** exact Railway env-var literal for `LIONWHEEL_FG_OUT_BRIDGE_ENABLED` (Tom decision 2026-05-23: `NEEDS_READONLY_VERIFICATION`; not changed in this docs cycle).
- **Shopify Gate E — Tom decided 2026-05-23:** GE-1 test SKU = `ADD-GAR-ANISE`; GE-2 sentinel strategy = Option C (SKU-allowlist). Corridor execution still open against these inputs.
- **Tom manual patch required before brain PR merge:** `docs/decisions/LOCKED_DECISIONS.md` §LionWheel — ratify second reversal class (count-freeze interaction) + ratify `LIONWHEEL_PICK_ADJUSTMENT` as Tom-approved-manual-only (any future use requires Tom approval). Patch text in `TEST-GT-START/docs/ruflo/26_LIONWHEEL_POST_CUTOVER_GOVERNANCE_PATCH_PACKET.md` §4.C.
- `JOB_RUNNER_TOKEN` provisioning + Python audit-skill container deployment (closes `audit_runs` cron blind-spot; tracked P1, not P0).
- Telegram bot token + chat_id for monitoring alerts (runbook §10).
- app_users uuid for count import.

---

## What must NOT be touched

- `SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED` — frozen until Phase 5 readiness + Tom written approval.
- `LIONWHEEL_FG_OUT_BRIDGE_ENABLED` post-cutover state — **do not flip back to `false`** without explicit Tom rollback decision + parity replay. Bridge is operationally live since 2026-05-10.
- Planning engine locked boundaries (A3/A4, `fn_compute_fg_net_requirements`, etc.).
- Stock-ledger semantics; `balance_anchors`.

---

## Commit tips

- Portal (`gt-factory-os-portal`): `5dfb549` (2026-05-18 — production-simulation date-range plan mode PR #36).
- Backend (`gt-factory-os`): `bc2d34d` (2026-05-18 — Railway redeploy; last code commit `d81af0f` 2026-05-18 PR #38).
- Brain (`gt-factory-os-production-brain`): `258ac3c` (2026-05-08 Run G); this patch advances the tip post-Run-G for the first time.
