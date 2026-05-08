# Authority Doc Patch Proposals — Phase 8 Run B

**Status:** PROPOSAL ONLY. No authority doc edited. No patch applied.
**Date:** 2026-05-08
**Author:** factory-os-governor + ops-docs-curator + source-of-truth-auditor (joint, read-only).
**Authorizes:** nothing. Tom is the only writer of authority docs. Each proposed patch
requires explicit Tom approval before being applied.

---

## A. Scope

This document proposes **minimal** patches to the five authority docs to reflect Run B's
new agents and commands. All patches are additive or pointer-only. None removes a locked
decision. None shrinks any doc for aesthetics.

| Authority doc | Proposed patches |
|---------------|------------------|
| `CLAUDE.md` | 1 (UX/UI as first-class production discipline; pointer to agents) |
| `EXECUTION_POLICY.md` | 3 (W1/W2/W4 → new agents map; lanes; approval thresholds) |
| `WORKSPACE_MAP.md` | 2 (Phase 8 agent locations; UX canon pointer) |
| `CURRENT_STATE.md` | 2 (Wave 8 status entry; FLOW-003 P0 entry) |
| `ACTIVE_NOW.md` | 1 (optional short status refresh) |

---

## B. CLAUDE.md proposed patch

### B.1 — Patch B.CL.1 — UX/UI as first-class production discipline

**Where:** Add a new section between the existing `## Locked decisions` block and
`### Deployment` block. Title: `### UX / UI doctrine`.

**Reason:** Run B's UX agents and the FLOW-003 P0 prove that UX/UI is not a polish layer
on top of the platform — it is part of the locked architecture. Without a CLAUDE.md
clause, future runs may treat UX as deferrable.

**Proposed exact text:**

```markdown
### UX / UI doctrine

UX/UI is a first-class production discipline, not a polish layer. The portal is the
operator workflow and the operator workflow is half the platform. The following is locked:

- The five UX agents (`ux-flow-architect`, `interaction-design-specialist`,
  `visual-system-designer`, `ux-content-state-designer`, `accessibility-usability-auditor`)
  are read-only auditors. They do not write portal source.
- `portal_ux_standard.md` (in the portal repo) is the locked register; only
  `ux-content-state-designer` may write it.
- A surface with an open P0 finding from `/ux-release-gate` may not ship.
- Hebrew operator copy is per-string Tom-pinned; no surface-wide approval is implied.
- Every user-visible portal change requires a UX handoff packet before merge.

The UX gate runs in parallel with the technical gate; both must pass.
```

**Risk if applied incorrectly:** none — purely additive.

**Approval:** Tom only.

### B.2 — Patch B.CL.2 — Production agent architecture pointer

**Where:** Add to the existing `## Source-of-truth map` section. **Append** a new
sub-bullet at the end of the section, **do not** modify existing bullets.

**Proposed exact text (appended):**

```markdown
### Production agent architecture (Phase 8)

Production execution is performed by four conservative agents:
- `backend-db-executor` — backend API, DB, migrations, jobs (replaces `executor-w1` after Wave 6).
- `portal-production-executor` — Next.js portal authoring (replaces `executor-w2` after Wave 6).
- `integration-boundary-executor` — LionWheel / Shopify / Green Invoice / Edge Functions (replaces `executor-w4` after Wave 6).
- `ops-docs-curator` — docs hygiene + archive (new role; no executor-era predecessor).

Governance is performed by:
- `factory-os-governor` — go/no-go (replaces `governor.md` after Wave 6).
- `release-verifier` — pre-merge / pre-deploy verification.
- `source-of-truth-auditor` — cross-doc drift classification.
- `verifier.md` — post-executor PASS/FAIL (kept indefinitely).

The five UX agents listed in §UX / UI doctrine round out the operating layer. All agents
follow the source-of-truth hierarchy already locked in this document.
```

**Risk if applied incorrectly:** none — purely additive pointer.

**Approval:** Tom only.

---

## C. EXECUTION_POLICY.md proposed patches

### C.1 — Patch C.EP.1 — Window → agent mapping

**Where:** Add a new section after the existing `## Window ownership (locked)` table.
Title: `### Phase 8 production agent mapping`.

**Reason:** The Window vocabulary is preserved (W1/W2/W4) but each Window now has both a
legacy executor and a new production agent dispatchable for that Window. Operators need
a clear map.

**Proposed exact text:**

```markdown
### Phase 8 production agent mapping

| Window | Legacy executor (active until Wave 6) | New production agent (Phase 8 Run B) |
|--------|----------------------------------------|---------------------------------------|
| W1 — DB / Schema / Migrations / Tests | `executor-w1` | `backend-db-executor` |
| W2 — Canonical Portal / Production UI | `executor-w2` | `portal-production-executor` |
| W4 — Integrations / Jobs / Exports / Dashboard | `executor-w4` | `integration-boundary-executor` |
| W3 — Sandbox / Mock UI | (no canonical owner; sandbox-only) | (no agent — never canonical) |
| W5 — Architecture / Governance | `governor.md` (legacy) | `factory-os-governor` (Run A) |
| Cross-Window — Docs / Archive / Hygiene | (no role) | `ops-docs-curator` (new role) |

Both columns remain dispatchable through Wave 6. After Wave 6 evidence (per
`PRODUCTION/docs/phase8/deprecation/ACTIVE_SURFACE_REDUCTION_PLAN.md`), legacy executors
move to `archive/legacy-agents/`. Tom must approve each archive step.

The UX agents (`ux-flow-architect`, `interaction-design-specialist`, `visual-system-designer`,
`ux-content-state-designer`, `accessibility-usability-auditor`) are read-only and do not
own a Window. They produce handoff packets that `portal-production-executor` consumes.
```

**Risk:** the table format is identical to the existing `## Window ownership (locked)`
table; no formatting drift introduced.

**Approval:** Tom only.

### C.2 — Patch C.EP.2 — Execution lanes

**Where:** Add a new section after C.EP.1. Title: `### Execution lanes (Phase 8)`.

**Proposed exact text:**

```markdown
### Execution lanes (Phase 8)

| Lane | Owners | Active simultaneously? |
|------|--------|------------------------|
| Backend / DB / migrations | `backend-db-executor` OR `executor-w1` (one at a time) | yes — alongside other lanes |
| Portal | `portal-production-executor` OR `executor-w2` (one at a time) | yes |
| Integration / jobs | `integration-boundary-executor` OR `executor-w4` (one at a time) | yes |
| Docs / hygiene / archive | `ops-docs-curator` | yes |
| UX audit | UX agents (parallel; read-only) | yes |
| Governance | `factory-os-governor` (read-only) | always-on |
| Pre-merge gate | `release-verifier` | on demand |
| Source-of-truth | `source-of-truth-auditor` | on demand |

Maximum 4 simultaneous executor lanes (backend + portal + integration + docs). UX agents
do not count as a lane (they are read-only). Governance and gates do not count as a lane.

A lane may be carried by either the legacy executor or the new production agent — never
both at once. The default is the new production agent unless Tom specifies otherwise.
```

**Risk:** none — additive.

**Approval:** Tom only.

### C.3 — Patch C.EP.3 — Frozen flags log section + approval thresholds

**Where:** Per DR-015 finding, the section `EXECUTION_POLICY.md §Frozen flags log` is
referenced by `integration-boundary-executor.md` but may not exist in the current
EXECUTION_POLICY.md. **Add the section** at the bottom of EXECUTION_POLICY.md before any
existing `## Legacy amendments` section.

**Proposed exact text:**

```markdown
## Frozen flags log

These environment flags must remain `false` in production until Tom written authorization
explicitly flips them. Each flip requires a successful dry-run, a ≥24h soak, and a
RUNTIME_READY signal from the relevant executor.

| Flag | Default | Authorized state | Authorization reference |
|------|---------|------------------|------------------------|
| `LIONWHEEL_FG_OUT_BRIDGE_ENABLED` | `false` | `false` (Phase 8 Wave 0; no flip authorized) | CLAUDE.md "LionWheel pickup → ledger decrement" locked decision |
| `SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED` | `false` | `false` (Phase 5 only; not approved) | CLAUDE.md "Shopify v2 phase plan"; current corridor evidence in `gt-factory-os/docs/superpowers/evidence/2026-05-07-shopify-phase0-bleeding-stopped.md` |

A flag flip without all four prerequisites (Tom written approval, dry-run evidence,
≥24h soak, RUNTIME_READY) emits `frozen_flag_unexpected_state` and halts integration writes.

## Approval thresholds (Phase 8 Run B)

| Action | Approval required |
|--------|------------------|
| Production DB migration | Tom written |
| Adding a new movement_type to stock_ledger | Tom written |
| Changing BOM head/version/lines columns | Tom written |
| Hebrew copy change (any surface) | Tom register entry |
| FLOW-003 resolution (any change to /planning/blockers substrate code) | Tom written per FLOW-003 decision packet |
| Frozen flag flip | Tom written + dry-run + ≥24h soak + RUNTIME_READY |
| External integration write (LW/Shopify/GI POST/PUT/DELETE) | Tom written + dry-run |
| Vercel production deploy | Tom written |
| Supabase Edge Function deploy | Tom written |
| Auth flow change (middleware.ts, (auth)/**) | Tom written |
| `git push` to any remote | Tom (always requires explicit user instruction) |
| Archiving any legacy agent | Tom written + Wave 6 evidence per ACTIVE_SURFACE_REDUCTION_PLAN.md |
| Updating any authority doc | Tom (only writer) |
| RUNTIME_READY emission with full test evidence | none — self-authorizing |
| Local dev work on dev DB | none |
| New unit / integration test (no production change) | none |
```

**Risk:** none — additive section.

**Approval:** Tom only.

---

## D. WORKSPACE_MAP.md proposed patches

### D.1 — Patch D.WM.1 — Phase 8 agent locations

**Where:** Append a new section at the end of `## BOX 1 — PRODUCTION/`. Title:
`### Phase 8 agents and commands (locations)`.

**Proposed exact text:**

```markdown
### Phase 8 agents and commands (locations)

| Path | Owner |
|------|-------|
| `PRODUCTION/.claude/agents/factory-os-governor.md` | governance (Run A) |
| `PRODUCTION/.claude/agents/release-verifier.md` | pre-merge gate (Run A) |
| `PRODUCTION/.claude/agents/source-of-truth-auditor.md` | drift detection (Run A) |
| `PRODUCTION/.claude/agents/ux-flow-architect.md` | flow doctrine (Run A) |
| `PRODUCTION/.claude/agents/interaction-design-specialist.md` | buttons/forms (Run A) |
| `PRODUCTION/.claude/agents/visual-system-designer.md` | tokens/layout (Run A) |
| `PRODUCTION/.claude/agents/ux-content-state-designer.md` | copy/register (Run A) |
| `PRODUCTION/.claude/agents/accessibility-usability-auditor.md` | a11y (Run A) |
| `PRODUCTION/.claude/agents/backend-db-executor.md` | backend executor (Run B) |
| `PRODUCTION/.claude/agents/portal-production-executor.md` | portal executor (Run B) |
| `PRODUCTION/.claude/agents/integration-boundary-executor.md` | integration executor (Run B) |
| `PRODUCTION/.claude/agents/ops-docs-curator.md` | docs curator (Run B) |
| `PRODUCTION/.claude/agents/executor-w1.md` | legacy DB executor (active until Wave 6) |
| `PRODUCTION/.claude/agents/executor-w2.md` | legacy portal executor (active until Wave 6) |
| `PRODUCTION/.claude/agents/executor-w4.md` | legacy integration executor (active until Wave 6) |
| `PRODUCTION/.claude/agents/governor.md` | legacy governor (active until Wave 6) |
| `PRODUCTION/.claude/agents/verifier.md` | post-executor verifier (kept indefinitely) |
| `PRODUCTION/.claude/commands/` | 15 commands (Run A: 7 UX + 3 core; Run B: 5 execution) |
```

**Risk:** none — additive pointer table.

**Approval:** Tom only.

### D.2 — Patch D.WM.2 — UX canon and handoff doc pointers

**Where:** Append after the `## BOX 2 — Canonical Runtime` section. Title:
`### UX canon (PRODUCTION) and portal locked register (portal)`.

**Proposed exact text:**

```markdown
### UX canon (PRODUCTION) and portal locked register (portal)

UX doctrine and locked register are split by purpose:

- **Doctrine** (PRODUCTION; produced by UX agents):
  - `PRODUCTION/docs/phase8/ux/UX_RELEASE_GATE.md`
  - `PRODUCTION/docs/phase8/ux/OPERATIONAL_FLOW_MAP.md`
  - `PRODUCTION/docs/phase8/ux/BUTTON_AND_ACTION_RULES.md`
  - `PRODUCTION/docs/phase8/ux/CONTENT_AND_MICROCOPY_GUIDE.md`
  - `PRODUCTION/docs/phase8/ux/STATUS_EMPTY_ERROR_STATES.md`
  - `PRODUCTION/docs/phase8/ux/ACCESSIBILITY_CHECKLIST.md`
  - `PRODUCTION/docs/phase8/ux/DESIGN_SYSTEM_RULES.md`
  - `PRODUCTION/docs/phase8/ux/SCREEN_SCORECARDS.md`
  - `PRODUCTION/docs/phase8/ux/USER_ROLES_AND_CONTEXTS.md`
  - `PRODUCTION/docs/phase8/ux/UX_OPERATING_PRINCIPLES.md`

- **Locked register** (portal; only `ux-content-state-designer` writes):
  - `gt-factory-os-portal/docs/portal_ux_standard.md`
  - `gt-factory-os-portal/docs/portal_language_direction_audit.md`
  - `gt-factory-os-portal/docs/ux/**handoff**.md` (per-surface packets)

- **Decisions** (PRODUCTION; Tom-approved decision packets):
  - `PRODUCTION/docs/phase8/decisions/FLOW-003-planning-blockers-p0-decision-packet.md`
  - (additional decision packets as authored)
```

**Risk:** none — additive pointer.

**Approval:** Tom only.

---

## E. CURRENT_STATE.md proposed patches

### E.1 — Patch E.CS.1 — Phase 8 Run B status entry

**Where:** Append a new section near the top of `CURRENT_STATE.md` (before the active
corridor entries). Title: `## Phase 8 Run B status (2026-05-08)`.

**Reason:** `CURRENT_STATE.md` is the live gate authority. After Run B lands, the runtime
status must reflect the existence of the new agents, commands, and the deferred items.

**Proposed exact text:**

```markdown
## Phase 8 Run B status (2026-05-08)

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
- FLOW-003 P0 decision packet created; **Tom decision required** before any
  `/planning/blockers` substrate code change.
- Active surface reduction plan documented; **no legacy agent archived**.
- Authority doc patches proposed; **none applied** in Run B.
- Hooks / settings / MCP / CLAUDE.md hardening proposed; **none applied** in Run B.

**Run B did NOT:** touch product code, touch portal code, change UX copy, edit hooks /
settings / MCP / CLAUDE.md, archive any legacy agent, push to any remote, deploy, or
flip any frozen flag.

**Run B git evidence:** four commits on `PRODUCTION/main` (see latest `git log --oneline -10`).
```

**Risk:** the section is bounded; does not contradict existing entries.

**Approval:** Tom only.

### E.2 — Patch E.CS.2 — UX gate aggregate HOLD entry (FLOW-003)

**Where:** Append to `CURRENT_STATE.md` after E.CS.1. Title:
`## UX release gate (2026-05-08)`.

**Reason:** Run A's `/ux-release-gate` returned aggregate HOLD because of FLOW-003.
`CURRENT_STATE.md` is the live gate authority; the FLOW-003 P0 must be visible there.

**Proposed exact text:**

```markdown
## UX release gate (2026-05-08)

**Aggregate verdict:** HOLD.

**Per-surface verdicts:**
- `/(ops)/stock/waste-adjustments` — CONDITIONAL_SHIP (A11Y-001 form-label gap pending; A11Y-002 cleared)
- `/(ops)/stock/goods-receipt` — CONDITIONAL_SHIP
- `/(po)/purchase-orders/[po_id]` — CONDITIONAL_SHIP (INTER-001 downgraded to confirmed P1)
- `/planning/blockers` — **HOLD (P0 confirmed; FLOW-003)**
- `/(ops)/stock/physical-count` — NOT_AUDITED at source level

**FLOW-003 P0:** see `PRODUCTION/docs/phase8/decisions/FLOW-003-planning-blockers-p0-decision-packet.md`.
Tom written decision required before any change. Aggregate HOLD remains until ALL of:
1. Tom answers the four questions in §N of the decision packet.
2. The chosen option is implemented per the decision packet's allowed scope.
3. A follow-up `/ux-release-gate` returns CONDITIONAL_SHIP or SHIP for `/planning/blockers`.
```

**Risk:** none — adds a current-state row.

**Approval:** Tom only.

---

## F. ACTIVE_NOW.md proposed patch (optional)

### F.1 — Patch F.AN.1 — Short status refresh

**Where:** `ACTIVE_NOW.md` — replace the current operator-context block with a short
two-line refresh.

**Proposed exact text:**

```markdown
## Active now (2026-05-08)

Phase 8 Run B landed: 4 production execution agents, 5 commands, 5 dry-runs, FLOW-003
decision packet, active surface reduction plan, authority + hooks proposals (proposals
only; no apply). Aggregate UX gate HOLD pending FLOW-003 Tom decision. PRODUCTION remote
deferred — safe to push when Tom provides URL.
```

**Risk:** `ACTIVE_NOW.md` is ephemeral; refresh is low-risk per
`feedback_harness_state_authoritative.md` (CURRENT_STATE.md is the gate authority; ACTIVE_NOW.md is
operator context only).

**Approval:** Tom only — but lower bar than other authority docs because the file is
explicitly ephemeral.

---

## G. Patch application order (when Tom approves)

If Tom approves all patches, apply in this order:

1. **CLAUDE.md (B.CL.1, B.CL.2)** — locked truth first.
2. **EXECUTION_POLICY.md (C.EP.1, C.EP.2, C.EP.3)** — operational governance second; depends
   on CLAUDE.md UX/UI doctrine clause being in place.
3. **WORKSPACE_MAP.md (D.WM.1, D.WM.2)** — pointer-only; depends on the above.
4. **CURRENT_STATE.md (E.CS.1, E.CS.2)** — runtime status; references all of the above.
5. **ACTIVE_NOW.md (F.AN.1)** — operator context refresh; lowest priority.

Each patch should be applied as a separate Tom-approved commit.

---

## H. Patches NOT proposed in Run B

For clarity, the following changes are **deliberately NOT** proposed in Run B even though
they could be argued for:

- Removing or rewording any locked decision in CLAUDE.md.
- Changing the source-of-truth hierarchy.
- Changing the gate model (Gates 1–5).
- Adding any new locked decision (e.g. "MCP must remain disabled forever").
- Changing the LionWheel pickup trigger semantics.
- Changing the BOM two-head model.
- Changing the Hebrew copy register policy.
- Removing the `verifier.md` legacy agent.
- Pre-archiving any legacy agent before Wave 6 evidence.

These are deliberately out of scope for Run B.

---

## I. STATUS block

```
STATUS: PASS

Scope: Authority doc patch proposals (5 docs; 9 patches total)
Files changed: 0 (no authority doc edited)
Patches proposed: 9
Patches applied: 0
Locked decisions removed: 0 (forbidden)
Tom approval required for each patch: yes (every one)
Application order documented: yes
Patches NOT proposed (out-of-scope): listed in §H
Handoff: factory-os-governor + Tom (each patch awaits Tom written approval)
```

---

**END OF AUTHORITY DOC PATCH PROPOSALS — No authority doc edited in Run B.**
