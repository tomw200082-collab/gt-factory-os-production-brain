# Wave 4 — Hooks, Settings, MCP, and CLAUDE.md Proposals

**Status:** PROPOSAL ONLY — no changes applied. No hooks modified. No settings changed.
**No MCP entries enabled. No CLAUDE.md edits made.**
**Date:** 2026-05-08

These proposals are Wave 4 deliverables. Wave 4 does not execute until Wave 3
dry-runs (10–12) have produced PASS evidence and Tom approves Wave 4 go/no-go.

---

## Section 1: Hook proposals

The hook rollout uses two tiers. Tier A are hard-block rules with low false-positive
risk. Tier B are warning-only rules that need agent metadata to be accurate before
they can be promoted to hard-blocks.

### Tier A — Hard-block rules (propose for Wave 4 step 4.1)

#### H1: Stale ACTIVE_NOW.md warning (extend existing hook)

- **File:** `.claude/hooks/session_start.sh`
- **Current state:** Hook exists and warns on stale ACTIVE_NOW.md.
- **Proposed extension:** Also warn if `active_mode.json` and `ACTIVE_NOW.md`
  disagree on the current W2 mode (Mode A vs Mode B).
- **Enforcement:** warn-only on stderr (already in place; extend only).
- **False-positive risk:** very low.

#### H2: Archive-to-canonical promotion block

- **File:** `.claude/hooks/pre_tool_use.sh`
- **Trigger:** `Edit` or `Write` tool where `dst` path is canonical
  (`api/**`, `db/**`, `src/**`) AND `src` path is under any `archive/`.
- **Enforcement:** hard-block with message:
  `BLOCKED: Promoting archived content to canonical path requires Tom approval.`
- **False-positive risk:** very low (archive paths are clearly namespaced).

#### H3: `.env*` read/write protection

- **File:** `.claude/hooks/pre_tool_use.sh` + `settings.json`
- **Trigger:** Any `Write` or `Edit` tool targeting a path matching `.env*`
  OR any `Bash` command containing literal `> .env` or `>> .env`.
- **Current state:** `settings.json` already has `Bash(edit .env*)` as deny.
- **Proposed addition:** Extend to `Write` and `Edit` tools with `.env*` in the
  target path. Also add `Read(.env*)` as `ask` (read is OK but should require
  explicit user confirmation each session).
- **Enforcement:** hard-block for writes; `ask` for reads.
- **False-positive risk:** near-zero (`.env` writes should never happen in any workflow).

#### H7: Out-of-lane write guard

- **File:** `.claude/hooks/pre_tool_use.sh`
- **Trigger:** `Write` or `Edit` tool where the target path is in a repo owned
  by a different lane from the calling agent's declared lane.
- **Lane ownership:** (from agent definitions)
  - `backend-db-executor` → `gt-factory-os/api/**`, `gt-factory-os/db/**`
  - `portal-production-executor` → `gt-factory-os-portal/src/**`
  - `integration-boundary-executor` → `gt-factory-os/api/src/integrations/**`
  - UX agents → `gt-factory-os-portal/docs/ux/**` only
- **Enforcement:** hard-block if detectable from subagent metadata; warn-only
  fallback if subagent metadata is unavailable (current subagent metadata
  reliability is unknown — test in Wave 4 smoke-test before promoting to hard-block).
- **False-positive risk:** medium until metadata reliability is confirmed.

#### H8: Archive-as-truth in evidence (extend existing)

- **File:** `.claude/hooks/subagent_stop.sh`
- **Current state:** Hook exists (annotates BLOCKED on archive-as-truth).
- **Proposed extension:** Also annotate when a subagent evidence section references
  a file path under `archive/` as a primary source (not just supplementary).
- **Enforcement:** annotate as BLOCKED; do not hard-stop the subagent.

#### H10: Destructive `Bash(rm -rf*)` → ask

- **File:** `settings.json`
- **Current state:** probably not yet in settings.json.
- **Proposed addition:** Add `Bash(rm -rf*)` to `permissions.ask` list.
- **Enforcement:** ask before run.
- **False-positive risk:** very low (rm -rf is rarely intentional in this workflow).

#### H11: `Bash(supabase functions deploy*)` → ask

- **File:** `settings.json`
- **Proposed addition:** Add `Bash(supabase functions deploy*)` to `permissions.ask` list.
- **Enforcement:** ask before run.

#### H12: `Bash(railway *)`, `Bash(vercel *)` → ask

- **File:** `settings.json`
- **Proposed addition:** Add `Bash(railway *)` and `Bash(vercel *)` to `permissions.ask` list.
- **Enforcement:** ask before run.

---

### Tier B — Warning-only rules (propose for Wave 4 step 4.2; warn only, never hard-block in Wave 4)

#### H4: Cross-lane PR warning

- **File:** `.claude/hooks/pre_tool_use.sh` on `git commit*`
- **Trigger:** A git commit touches files in more than one lane (e.g., both
  `gt-factory-os/db/` and `gt-factory-os-portal/src/`).
- **Enforcement:** warn only — annotate on stderr:
  `WARN: This commit touches multiple lanes. Verify this is intentional.`
- **Promotion to hard-block:** after one full UX dry-run cycle; false-positive
  rate must be <5%.

#### H5: Portal source change without UX handoff

- **File:** `.claude/hooks/pre_tool_use.sh` on `Edit` / `Write` to `portal src/`
- **Trigger:** Write to `gt-factory-os-portal/src/app/**` where no handoff packet
  exists in `docs/ux/` for the target route.
- **Enforcement:** warn only — annotate:
  `WARN: Portal source change without UX handoff packet. Confirm UX gate status.`
- **Promotion to hard-block:** after UX agent dry-runs prove consistent handoff
  packet creation.

#### H6: Button or action without state annotations

- **File:** `.claude/hooks/pre_tool_use.sh` on `Write` adding a `<Button` or
  `onClick` pattern
- **Trigger:** New file written to `src/app/**` contains `<Button` or `onClick=`
  without a loading or disabled pattern in proximity.
- **Enforcement:** warn only — annotate:
  `WARN: New action detected. Verify disabled, loading, and error states per BUTTON_AND_ACTION_RULES.md.`
- **False-positive risk:** high for list items and navigation; stay warn-only
  indefinitely until pattern matching is tightened.

#### H9: UX-visible change at session end without UX gate

- **File:** `.claude/hooks/stop.sh`
- **Trigger:** Session commits contain writes to `src/app/**` but no
  `/ux-release-gate` was run in the session.
- **Enforcement:** warn only — annotate on stop:
  `WARN: Portal source changes landed without a /ux-release-gate run this session.`
- **Promotion:** after three sessions of H9 triggering where the gate was genuinely
  needed (not false positive), promote to hard-block.

---

### Tier B promotion protocol

Tier B rules are reviewed after one full UX dry-run cycle (Wave 2 dry-runs 4–10
producing at least one PASS). Promotion to hard-block requires:
1. False-positive rate <5% across dry-runs.
2. Tom approval.
3. One-line entry in EXECUTION_POLICY.md §Hooks evolution log.

---

## Section 2: `settings.json` proposed changes

No settings changes applied in this wave. The following changes are proposed for
Wave 4 step 4.1:

```json
{
  "permissions": {
    "ask": [
      "Bash(rm -rf*)",
      "Bash(rm -r*)",
      "Bash(supabase functions deploy*)",
      "Bash(railway *)",
      "Bash(vercel *)",
      "Bash(git push --force*)",
      "Bash(git reset --hard*)",
      "Read(.env*)"
    ],
    "deny": [
      "Bash(edit .env*)",
      "Write(.env*)",
      "Edit(.env*)"
    ]
  }
}
```

**Note on existing deny rules:** `settings.json` already has `Bash(edit .env*)` as
deny. The proposed additions extend that existing deny set and add the new `ask` set.
No existing allow or deny rules are removed in Wave 4.

---

## Section 3: MCP policy (all disabled; nothing changed)

All five MCP servers remain disabled. No placeholder entries are removed.

| Server | Current state | Wave 4 action |
|--------|--------------|---------------|
| `filesystem-canonical` | disabled | keep disabled; no change |
| `github` | disabled | keep disabled; activation gate not met |
| `postgres-readonly` | disabled | keep disabled; activation gate not met |
| `sentry` | disabled | keep disabled placeholder |
| `linear` | disabled | keep disabled placeholder |

### MCP activation gate (any server)

Before any MCP entry flips from `disabled: true` to `disabled: false`, ALL of
these must be true:

1. Tom explicitly approves the credential in writing.
2. The role is read-only where the integration permits read-only.
3. The exact agents and commands that consume the MCP are named in
   EXECUTION_POLICY.md §MCP usage.
4. The activation is recorded in EXECUTION_POLICY.md §MCP activation log with
   date, agent list, and credential reference.
5. A rollback procedure (set `disabled: true`, rotate the credential, audit recent
   calls) is documented before activation.

### Why not enable `github` MCP now

`factory-os-governor` and `release-verifier` would benefit from GitHub PR
introspection. However:
- No PAT has been provisioned.
- The PAT scope (minimum: `metadata:read`, `pull_requests:read`) has not been
  agreed with Tom.
- Risk documentation in EXECUTION_POLICY.md §MCP usage is not yet written.
Until all five activation gate items are met, `github` MCP stays disabled.

### Why not enable `postgres-readonly` MCP now

`release-verifier` would benefit from direct parity checks. However:
- No Supabase read-only role has been provisioned.
- The credential for that role has not been confirmed available.
- Named users (`release-verifier`, `source-of-truth-auditor`) are listed in the
  design but not yet in EXECUTION_POLICY.md.
Until all five activation gate items are met, `postgres-readonly` stays disabled.

### Deletion of `sentry` and `linear` placeholders

Deferred. After one full production cycle and after `/source-truth-audit` has run
twice confirming no agent references `sentry` or `linear` MCP, Tom may approve
deletion. Until then, disabled placeholders remain.

---

## Section 4: CLAUDE.md proposed changes

No CLAUDE.md edits applied in this wave.

One clause is proposed for Wave 5 step 5.3. It is reproduced here exactly as it
would appear in the final file so Tom can review the precise wording before approval:

### Proposed insertion — UX/UI as a production discipline

Location: after the "Testing posture" section, before "What Claude must not do".

Exact proposed text:

```
## UX/UI operating discipline

UX and UI quality are production concerns, not polish. Every operator-facing portal
surface must pass a UX release gate before it is considered complete.

- **`portal_ux_standard.md`** (Gate 4.2 locked standard, 2026-04-30) is the sole
  authority on portal language, state hygiene, button naming, and banner conventions.
  No agent may modify it without Tom's explicit approval.
- **Five UX agents** collaborate to audit portal surfaces: `ux-flow-architect`,
  `interaction-design-specialist`, `visual-system-designer`, `ux-content-state-designer`,
  `accessibility-usability-auditor`. Run `/ux-release-gate` to execute the full gate.
- **Gate verdicts** follow the threshold: SHIP (zero P0), CONDITIONAL_SHIP (zero P0;
  P1s documented), HOLD (any confirmed P0). A HOLD blocks the surface from being
  declared complete.
- **Hebrew copy** appears only on surfaces with a Tom-pinned register entry.
  `ux-content-state-designer` owns the register. No Hebrew copy is introduced
  without a register entry.
```

**Why this clause:** CLAUDE.md has no current mention of UX or portal quality. Phase 8
introduces five UX agents and a UX release gate. Without a CLAUDE.md anchor, the
UX discipline has no authority-layer backing and future agents can ignore it. This
clause makes UX quality a first-class locked discipline alongside testing posture.

**What this clause does NOT do:**
- Does not override any existing locked decision.
- Does not change the Hebrew/English rules (those are already in §UI language).
- Does not add new forbidden patterns.
- Does not touch the gate model (§Gate model).

**Tom approval:** required before this clause is applied. The clause is proposal-only.

---

## Section 5: What was deliberately NOT proposed

1. **Hardening CLAUDE.md beyond the UX clause** — No other CLAUDE.md changes are
   proposed. The Phase 8 plan (revision 2) §K.4 explicitly lists no CLAUDE.md edit
   beyond the UX clause.

2. **Enabling any MCP** — The five activation gate items are not met for any server.

3. **Promoting Tier B hooks to hard-block** — Tier B stays warn-only until dry-runs
   prove stability.

4. **Adding agent-dispatching logic to hooks** — Hooks are prevention and annotation
   tools only. They do not spawn agents, call commands, or make routing decisions.

5. **Any runtime-path changes** — MCP, hooks, and settings are tooling. None of these
   proposals create a runtime dependency on Claude Code for live factory operations.
   CLAUDE.md §Input-source map explicitly forbids MCP as a runtime input channel.

---

**END OF WAVE 4 PROPOSALS — No hooks modified. No settings changed. No MCP enabled.
No CLAUDE.md edited. Tom approval required before any of Section 1–4 is applied.**
