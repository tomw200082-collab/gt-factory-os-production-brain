# GT Factory OS — Active Now

> **Authority:** today's dispatch context only. Names the active corridor(s), the active lane(s), what's being worked on now, what must NOT be touched, and the open Tom decisions blocking the next dispatch.
>
> **Not authoritative on:** gate status, completion %, critical path, UNRESOLVED items, failure modes, UX gate verdict — those live in `CURRENT_STATE.md` (sole authority). Operational signals and portal mode live in `.claude/state/runtime_ready.json` and `.claude/state/active_mode.json` (sole authority). On any disagreement, defer to those files.
>
> **Refresh cadence:** at corridor transition, cycle boundary, or when an active Tom decision opens or closes. Not refreshed on every gate-status change (those go to CURRENT_STATE).
>
> **Allowed sections (closed list, Phase 8 Run F Wave 4 Hole 2 cleanup, 2026-05-09):**
> 1. Active corridors
> 2. Active lanes today
> 3. Key live state pointers
> 4. Open Tom decisions blocking next dispatch
> 5. What must NOT be touched (this cycle)
> 6. Commit tips
>
> **Last refreshed:** 2026-05-08 (Phase 8 Run G — final AI Brain governance closure; Run F.2b pushed PRODUCTION to private remote `gt-factory-os-production-brain` at HEAD `875424b`; Run G closing signals policy, state freshness, registry, and acceptance record on branch `run-g-final-brain-closure`; no product runtime change).

---

## Active corridors

**1 — Shopify External Boundary v2**
Phase 0+1+2+3+4 landed. Gate E (Option C — SKU allowlist guard) in execution.
Hard stop: no live GraphQL inventory mutation until Phase 5 readiness + Tom approval.
Bridge state: `SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED=false` — do not flip.
Latest backend commit: `bcb2d0f` (GE-D bridge starvation fix).

**2 — Planning Corridor v1 (Tranche 3 CLOSED 2026-04-27)**
Tranches 1+2+3 DONE end-to-end. RUNTIME_READY(Planning-Tranche3-Blockers) emitted as signal #17.
Backend tip for Tranche 3: `1209596` (Railway `ef03b588`); portal closure: `e7dce27` (window2-portal-sandbox/main).
Portal currently in Mode A (`active_mode.json` last_updated 2026-05-02T22:00Z, no scoped form).
Tranche 4+ (Forecast Workspace) queued; later cycles (cycles 7–8 closure incl. signal #25 + #26 holidays-archived-filter) shipped.

**3 — Professional Stock-Truth Monitoring**
Sunday 2026-05-10 cutover day (post physical count). Pre-cutover prep landed 2026-05-07: 70 LionWheel SKU mappings, 2 new master items, runbook authored at `PRODUCTION/docs/superpowers/runbooks/2026-05-10-sunday-cutover-runbook.md`.
Bridge state: `LIONWHEEL_FG_OUT_BRIDGE_ENABLED=false` — do not flip until Sunday post-count per runbook §5.

**4 — AI Brain Run G governance closure**
Final AI Brain governance closure on branch `run-g-final-brain-closure`. Patching SIGNALS.md (CONFLICT-003 closed), CURRENT_STATE.md, ACTIVE_NOW.md, COMMAND_REGISTRY.md count fix, PRODUCTION-REMOTE-PLAN.md status, FINAL_AI_BRAIN_ACCEPTANCE.md creation. PR pending Tom merge. No product runtime change.

For the full evidence chain across these corridors, see `archive/historical-state-snapshots/2026-05-08-planning-corridor-detailed-state.md` and `archive/historical-state-snapshots/2026-05-08-phase8-ai-brain-rewrite-snapshot.md`.

---

## Active lanes today

| Lane | Status | Notes |
|------|--------|-------|
| backend-db | quiet | Awaiting Tom decision on next dispatch |
| portal | Mode A | No scoped form active; window2-portal-sandbox HEAD `9e2212e` (FLOW-003 closure) |
| integration | quiet | Shopify v2 Phase 5 readiness work pending Tom approval |
| docs | active | Phase 8 Run F Wave 4 Hole 2 cleanup in progress (this dispatch) |
| governance | always-on | factory-os-governor read-only |
| ux-audit | on-demand | Latest: DR-017 (post-Run-C UX release gate recheck) |

Maximum 4 simultaneous executor lanes (backend-db + portal + integration + docs); UX, governance, release-gate, source-of-truth do not count as a lane.

---

## Key live state

| Item | Value | Authoritative source |
|------|-------|----------------------|
| RUNTIME_READY signals | 35 (latest: GoodsReceipt-FromPO 2026-05-02T19:30Z) | `.claude/state/runtime_ready.json` |
| Portal mode | Mode A (no scoped form) | `.claude/state/active_mode.json` |
| Portal tip | `9e2212e` (FLOW-003 closure — actionable in-app ticket CTA; Run C 2026-05-08) | window2-portal-sandbox/main |
| Backend tip | `a6c80ec` (PR #21 structure consolidation; last code commit: `bcb2d0f` GE-D) | gt-factory-os/main |
| Railway | healthy | Railway dashboard |
| Vercel (portal) | ready — `gt-factory-os-portal.vercel.app` | Vercel dashboard |
| LionWheel bridge | `LIONWHEEL_FG_OUT_BRIDGE_ENABLED=false` — do not flip until Sunday post-count | `EXECUTION_POLICY.md` §Frozen flags log |
| Shopify bridge | `SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED=false` — frozen until Phase 5 readiness | `EXECUTION_POLICY.md` §Frozen flags log |
| Sunday 2026-05-10 | Physical count + bridge cutover day | runbook `docs/superpowers/runbooks/2026-05-10-sunday-cutover-runbook.md` |

For gate-by-gate status / completion / critical path / UNRESOLVED items / failure modes — read `CURRENT_STATE.md`.

---

## Open Tom decisions (blocking next dispatch)

- GE-1: confirm test SKU (recommended `ADD-GAR-ANISE`)
- GE-2: sentinel strategy (Option C SKU-allowlist recommended)
- Telegram bot token + chat_id for monitoring alerts (runbook §10)
- JOB_RUNNER_TOKEN provisioning
- app_users uuid for count import

---

## What must NOT be touched (this cycle)

- `LIONWHEEL_FG_OUT_BRIDGE_ENABLED` — frozen until Sunday post-count
- `SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED` — frozen until Phase 5 readiness
- Planning engine locked boundaries (A3/A4, `fn_compute_fg_net_requirements`, etc.)
- Stock ledger semantics and `balance_anchors`

---

## Commit tips

- Portal (`window2-portal-sandbox` / `gt-factory-os-portal`): `9e2212e` (FLOW-003 closure — Phase 8 Run C, 2026-05-08)
- Backend (`gt-factory-os/main`): `a6c80ec` (last code commit: `bcb2d0f`)
