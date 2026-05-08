# GT Factory OS — Active Now

> **Authority:** ephemeral operator context. **Not authoritative on anything.** `CURRENT_STATE.md` is the sole authority on gate status, completion range, critical path, and open gaps. On any disagreement, defer to `CURRENT_STATE.md`.

**Last refreshed:** 2026-05-08 (Phase 8 Run F — AI Brain kernel rewrite + router scaffolding landed; CLAUDE.md 355 → 133 lines; 6 new scaffolding files in PRODUCTION root; 2 extraction files in docs/; no product runtime change; no push, no merge, no deploy).

---

## Phase 8 Run C — landed

FLOW-003 P0 closed via `9e2212e` on `gt-factory-os-portal/main` (in-app ticket CTA on `/planning/blockers`; no backend / DB change). DR-017 records closure verdict. 9 authority-doc patches applied (CLAUDE.md, EXECUTION_POLICY.md, WORKSPACE_MAP.md, CURRENT_STATE.md, ACTIVE_NOW.md). No legacy agents touched. No hooks/settings/MCP changes. No remote push. No deploy. PRODUCTION remote still deferred.

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
| RUNTIME_READY signals | 35 (latest: GoodsReceipt-FromPO 2026-05-02T19:30Z) |
| W2 portal tip | `9e2212e` (FLOW-003 closure — actionable in-app ticket CTA; Run C 2026-05-08) |
| Backend tip | `a6c80ec` (PR #21 structure consolidation; last code commit: `bcb2d0f` GE-D) |
| Railway | healthy |
| Vercel (portal) | ready — `gt-factory-os-portal.vercel.app` |
| LionWheel bridge | `LIONWHEEL_FG_OUT_BRIDGE_ENABLED=false` — do not flip until Sunday post-count |
| Sunday 2026-05-10 | Physical count + bridge cutover day (see runbook `docs/superpowers/runbooks/2026-05-10-sunday-cutover-runbook.md`) |

---

## Open Tom decisions (blocking next dispatch)

- GE-1: confirm test SKU (recommended `ADD-GAR-ANISE`)
- GE-2: sentinel strategy (Option C SKU-allowlist recommended)
- Telegram bot token + chat_id for monitoring alerts (runbook §10)
- JOB_RUNNER_TOKEN provisioning
- app_users uuid for count import

---

## What must NOT be touched

- `LIONWHEEL_FG_OUT_BRIDGE_ENABLED` — frozen until Sunday post-count
- `SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED` — frozen until Phase 5 readiness
- Planning engine locked boundaries (A3/A4, `fn_compute_fg_net_requirements`, etc.)
- Stock ledger semantics and `balance_anchors`

---

## Commit tips

- Portal (`window2-portal-sandbox` / `gt-factory-os-portal`): `9e2212e` (FLOW-003 closure — Phase 8 Run C, 2026-05-08; verified via `git log -1 main` on `window2-portal-sandbox` during Run F Wave 1 reconciliation)
- Backend (`gt-factory-os/main`): `a6c80ec` (last code commit: `bcb2d0f`)
