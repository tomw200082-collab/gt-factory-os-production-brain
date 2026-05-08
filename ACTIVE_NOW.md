# GT Factory OS — Active Now

> **Authority:** ephemeral operator context. **Not authoritative on anything.** `CURRENT_STATE.md` is the sole authority on gate status, completion range, critical path, and open gaps. On any disagreement, defer to `CURRENT_STATE.md`.

**Last refreshed:** 2026-05-08 (project structure consolidation — Phase 1 complete)

---

## Two active corridors

**1 — Shopify External Boundary v2**
Phase 0+1+2+3+4 landed. Gate E (Option C — SKU allowlist guard) in execution.
Hard stop: no live GraphQL inventory mutation until Phase 5 readiness + Tom approval.
Bridge state: `SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED=false` — do not flip.
Latest backend commit: `bcb2d0f` (GE-D bridge starvation fix).

**2 — Planning Corridor v1 (Tranche 3 ACTIVE)**
Tranche 1+2 DONE. Tranche 3 (Unresolved Demand / Blockers) in flight.
W4 contract PASS. W1 backend dispatched. W2 portal waits for `RUNTIME_READY(Planning-Tranche3-Blockers)`.
Tranche 4+ (Forecast Workspace) queued.

---

## Key live state

| Item | Value |
|------|-------|
| RUNTIME_READY signals | 31 |
| W2 portal tip | `933052c` (fix: auth PKCE) |
| Backend tip | `bcb2d0f` (shopify GE-D) |
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

- Portal (`window2-portal-sandbox` / `gt-factory-os-portal`): `933052c`
- Backend (`gt-factory-os/main`): `bcb2d0f`
