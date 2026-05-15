# Historical state snapshot — Phase 8 Run B / C / F / F.2 / F.2b / G AI brain rewrite (2026-05-08)

> **Origin:** migrated verbatim from `CURRENT_STATE.md` §"Phase 8 Run B + Run C status", §"Phase 8 Run F status", §"Phase 8 Run F.2 / F.2b status" during Phase 8 Run F Wave 4 Hole 2 cleanup (2026-05-09). The corresponding sections in CURRENT_STATE.md were removed; this snapshot is the audit-trail preservation.
>
> **Type:** historical state snapshot of AI-brain governance work landed during Phase 8. Not authoritative on current state. For current state of the AI-brain rewrite, read `CURRENT_STATE.md` and the production agent registry.

---

## Phase 8 Run B + Run C status (2026-05-08)

**Run B landed:** controlled production execution layer + active surface reduction plan.

- 4 production execution agents created additively (alongside legacy executors):
  - `backend-db-executor`
  - `portal-production-executor`
  - `integration-boundary-executor`
  - `ops-docs-curator`
- 5 conservative execution commands created:
  - `/portal-pr-review`
  - `/integration-dry-run`
  - `/gate-close`
  - `/incident-triage`
  - `/docs-hygiene-check`
- 5 dry-runs executed (DR-012 through DR-016) — all PASS at design level.
- FLOW-003 P0 decision packet authored.
- Active surface reduction plan documented; **no legacy agent archived**.
- Authority doc patches proposed; hooks/settings/MCP plan written.

**Run C landed (2026-05-08):** FLOW-003 closure + authority canonicalization.

- FLOW-003 P0 — **CLOSED** via portal commit `9e2212e` (window2-portal-sandbox).
  - `_lib/labelMaps.ts:check_po_substrate` → `"פתח כרטיס טיפול"` (Tom-approved CTA).
  - `BlockerRow.tsx` Q4 cell now a tab-reachable `<button>` for `check_po_substrate`.
  - `BlockerCard.tsx` mirrors the same on mobile with Tom-approved interim sub-line
    `"שלח לצוות הפיתוח את ID החסם"`.
  - New `DevTicketModal.tsx` (`role="dialog"` aria-modal, ESC closes, focus management,
    clipboard copy + optional mailto: when `DEV_TEAM_EMAIL` configured).
  - New `devTicketContent.ts` (payload helper).
  - **No backend / DB / migration change.** Pure portal change.
- DR-017 records the closure verdict.
- 9 authority-doc patches applied (CLAUDE.md ×2, EXECUTION_POLICY.md ×3,
  WORKSPACE_MAP.md ×2, CURRENT_STATE.md ×1, ACTIVE_NOW.md ×1).

**Run C did NOT:** archive or modify any legacy agent, edit hooks/settings/MCP,
push to any remote, deploy, flip any frozen flag, or change any non-FLOW-003 portal
surface.

**Open follow-ups at the time of the snapshot (P1 polish, not blockers):** Q5 fallback chip on `/planning/blockers`, optional `DEV_TEAM_EMAIL` configuration, automated test coverage for the modal flow, INTER-001 Cancel-PO confirmation polish, A11Y-001 form-label gap on waste-adjustments.

---

## Phase 8 Run F status (2026-05-08)

**Run F landed:** AI Brain kernel rewrite + central router introduction + registry/template scaffolding.

- `CLAUDE.md` rewritten as thin boot kernel: 355 lines → 133 lines (62% reduction). All locked decisions preserved. Pre-rewrite full text archived at `docs/archive/CLAUDE.md.pre-kernel-rewrite-2026-05-08.md`.
- 6 additive scaffolding files created in PRODUCTION root: `AI_BRAIN_ROUTER.md` (central decision engine), `AGENT_TEMPLATE.md`, `MODULE_TEMPLATE.md` (future-module declaration), `AGENT_REGISTRY.md` (17 agents indexed), `COMMAND_REGISTRY.md` (15 commands indexed), `VERDICT_GLOSSARY.md` (verdict tokens with semantics).
- 2 extraction files created: `docs/decisions/LOCKED_DECISIONS.md` (verbatim locked-decision text) and `docs/contracts/SCHEMA_GUIDANCE.md` (schema/integration/security/observability guidance).
- 6 low-risk drift patches applied (Wave 1): RUNTIME_READY count 31 → 35; stale lane-rename note removed from EXECUTION_POLICY.md; executor-w2 sandbox wording corrected; WAVE3 proposal banner → IMPLEMENTED; ACTIVE_NOW.md commit-tips reconciled to portal HEAD `9e2212e`; memory file `reference_gt_factory_paths.md` annotated as stale + push-policy supersession per Tom decision A.
- 5 commits (`eaa272c`, `4d5af6d`, `18d4621`, `eef4cd3`, `50e999b`) ahead of Run C tip `5833fe6`.

**Run F did NOT:** create new agents, create new commands, create new skills, edit hooks/settings/MCP, push to any remote, deploy, flip any frozen flag, change any product runtime code (no touches to `gt-factory-os/`, `gt-factory-os-portal/`, `window2-portal-sandbox/`, db migrations, env, secrets), archive any legacy agent.

**Verification (all 8 checks PASS):** tree clean; 5 Run F commits since 5833fe6; CLAUDE.md = 133 lines (within 100–180 target); all 15 changed files under PRODUCTION/; agent count = 17 unchanged; command count = 15 unchanged; no `.claude/skills/` directory created; hooks/settings/MCP untouched (empty diff). Registry coverage: AGENT_REGISTRY.md references all 17 agents; COMMAND_REGISTRY.md references all 15 commands; CLAUDE.md sibling-doc references all resolve. Locked-decision keywords from pre-rewrite CLAUDE.md all findable across kernel + extraction files + EXECUTION_POLICY.md + CURRENT_STATE.md + WORKSPACE_MAP.md + AI_BRAIN_ROUTER.md.

**Deferred items at the time of the snapshot (need Tom decision later, NOT blocking Run F):**
- CONFLICT-003 (`SIGNALS.md` emitter list) — Tom decision required (codify factory-os-governor + executor-w2 historical emissions as exceptions, or annotate as historical).
- CONFLICT-009 (W2 mode timestamp) — Phase 1 Explore could not precisely locate the target line; defer to next governance run.
- CONFLICT-010 (legacy executor policy duplication) — handled by Wave 6 archival per `docs/phase8/deprecation/ACTIVE_SURFACE_REDUCTION_PLAN.md`.
- CONFLICT-011 (absolute Windows paths in EXECUTION_POLICY.md) — low value, high noise; deferred.
- CONFLICT-012 (skill name) — **CLOSED** as Run E audit error: both `factory-os-autonomous-builder` and `factory-os-advance` exist on disk as distinct skills; not a conflict.
- D3 (completion range refresh) — per Tom decision H, no invented %; the existing range is stale. Status: NEEDS_TOM_CALIBRATION — Tom calibrates when ready.
- D6 (ralph-loop.local.md) — VERIFIED RESOLVED on disk: `.claude/ralph-loop.local.md` exists, `active: false`, `closed_at: 2026-05-08T00:00:00Z`.

**Tom decision A enshrined in kernel:** no autonomous push, no merge, no deploy. Memory file contradicting this is now annotated as superseded by EXECUTION_POLICY.md.

---

## Phase 8 Run F.2 / F.2b status (2026-05-08)

**Run F.2b completed:** PRODUCTION AI Brain pushed to private remote.

- Remote URL: `https://github.com/tomw200082-collab/gt-factory-os-production-brain.git` (private)
- Branch: `main`, HEAD: `875424b` — local = remote, verified 2026-05-08.
- No product runtime code in this repo (governance files only).
- No product code touched in Run F.2 / F.2b.

**Run G (in progress at the time of the snapshot, 2026-05-08):** final AI Brain governance closure — signals policy (CONFLICT-003), state freshness, registry count fix, acceptance record. Branch `run-g-final-brain-closure`.
