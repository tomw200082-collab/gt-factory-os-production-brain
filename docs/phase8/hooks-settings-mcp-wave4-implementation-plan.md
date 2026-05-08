# Hooks / Settings / MCP / CLAUDE.md Wave 4 Implementation Plan

**Status:** PLAN ONLY. No hook script changed. No setting changed. No MCP enabled. No
CLAUDE.md edited.
**Date:** 2026-05-08
**Author:** factory-os-governor + ops-docs-curator (joint, read-only).
**Builds on:** `PRODUCTION/docs/phase8/WAVE4-HOOKS-SETTINGS-MCP-CLAUDE-PROPOSALS.md` (Run A).

---

## A. Why a separate plan rather than direct apply

Run B's mandate is "controlled production execution layer + active surface reduction." The
Wave 4 hardening (hooks, settings, MCP, CLAUDE.md) was authored as a *proposal* in Run A.
Apply is gated on:

1. The new agents existing (Run B Step 2 — done).
2. The dry-run chain proving the new agents reason correctly (Run B Step 5 — done).
3. Tom written approval per category.
4. A documented rollback for each category.
5. A proof of false-positive rates for hooks before any of them becomes a hard block.

This plan prepares the apply pack so Tom can approve any subset in any order. Each section
is independently apply-able.

---

## B. Hooks to add later

### B.1 — `pre_commit_authority_doc_guard` (PreToolUse, hard block)

**Purpose:** Reject any `Write` or `Edit` that targets `CLAUDE.md`, `EXECUTION_POLICY.md`,
`WORKSPACE_MAP.md`, `CURRENT_STATE.md` unless the calling agent is `factory-os-governor`
acting under explicit Tom approval.

**Implementation:** extend `.claude/hooks/pre_tool_use.sh` with a path-matching check
against the protected authority doc list.

**Hard or warning:** **HARD BLOCK.** Authority docs are the source of truth; an
accidental write is high cost.

**False-positive risk:** medium. Tom often patches authority docs himself directly via
his editor. The hook only fires on agent-mediated writes, not on Tom's direct file edits.

**Rollback:** revert the section of `pre_tool_use.sh` and restart the session.

**Proposed exact patch (pseudo-shell; real script must be tested):**

```bash
# .claude/hooks/pre_tool_use.sh — append before the script's exit 0
PROTECTED_AUTHORITY_DOCS=(
  "CLAUDE.md"
  "EXECUTION_POLICY.md"
  "WORKSPACE_MAP.md"
  "CURRENT_STATE.md"
)
# read the proposed file path from stdin / arg per harness convention
# if matches and tool != "factory-os-governor under approval token" → exit 1 with message
```

(Exact shell syntax depends on harness contract; the above is intent only.)

### B.2 — `pre_commit_secret_guard` (PreToolUse, hard block)

**Purpose:** Reject any tool call whose target path matches `.env*`, `*.pem`, `*.key`,
`credentials/**`, `secrets/**`. Already partially covered by `.gitignore`; the hook fires
**before** the write attempt to avoid even local file creation with sensitive content.

**Hard or warning:** **HARD BLOCK.**

**False-positive risk:** very low.

**Rollback:** revert the hook section.

### B.3 — `pre_commit_destructive_command_guard` (PreToolUse, hard block)

**Purpose:** Reject `rm -rf`, `git reset --hard`, `git push --force` (force-push to main),
`git checkout --`, `git restore .`, `git clean -f`, `git branch -D`, `--no-verify`,
`--no-gpg-sign`, `--no-edit` (in `git rebase`).

**Hard or warning:** **HARD BLOCK with bypass token.** Tom can authorize a one-off bypass by
prefixing the command with an explicit token (e.g. `# tom-approved-destructive: <reason>`).

**False-positive risk:** medium. `rm -rf` on a temp directory is sometimes legitimate;
the bypass token covers it.

**Rollback:** revert the hook section.

### B.4 — `pre_commit_archive_promotion_block` (PreToolUse, hard block)

**Purpose:** Reject any tool call that promotes content from `archive/**` back into an
active path (e.g. `git mv archive/legacy-agents/executor-w1.md .claude/agents/`) unless
explicitly Tom-approved with an inline token.

**Hard or warning:** **HARD BLOCK with token.**

**False-positive risk:** very low.

**Rollback:** revert the hook section.

### B.5 — `pre_commit_out_of_lane_warning` (PreToolUse, **warning only**)

**Purpose:** Detect when a tool call writes outside the calling agent's allowed paths
(per the agent definition's `allowed_paths` block). Print a warning; do not block.

**Hard or warning:** **WARNING ONLY.** Hard blocks here would over-fire for the first few
weeks; warning lets the operator see the violation and route correctly.

**False-positive risk:** medium initially; expected to drop as agent dispatch hygiene
improves. After 4 weeks of warning-only data, consider promoting to a hard block.

**Rollback:** revert the hook section.

### B.6 — `pre_commit_ux_visible_change_warning` (PreToolUse, **warning only**)

**Purpose:** Detect when a tool call writes to a portal page file (e.g.
`gt-factory-os-portal/src/app/**/page.tsx`) without an open UX handoff packet for the
surface. Print a warning.

**Hard or warning:** **WARNING ONLY.**

**False-positive risk:** medium. Bug fixes and pure refactors do not always need a new
packet.

**Rollback:** revert the hook section.

### B.7 — `pre_commit_button_action_state_warning` (PreToolUse, **warning only**)

**Purpose:** Detect a portal change that adds a `<button>` element without nearby
loading / error / confirmation state. Print a warning naming the button location.

**Hard or warning:** **WARNING ONLY.**

**False-positive risk:** high. Many buttons have state handled at parent. Warning is
useful as a prompt; hard block would over-fire.

**Rollback:** revert the hook section.

### B.8 — `pre_commit_cross_lane_pr_warning` (PreToolUse, **warning only**)

**Purpose:** Detect that a single staged-files set crosses lane boundaries (e.g. backend
files + portal files in one commit). Print a warning suggesting two PRs.

**Hard or warning:** **WARNING ONLY.**

**False-positive risk:** medium.

**Rollback:** revert the hook section.

---

## C. Hooks to extend later (already exist)

### C.1 — `session_start.sh`

**Current behavior:** prints session info on session start.

**Proposed extension:** also emit a brief health summary:
- `git status --short` line count.
- Frozen flags state (with secrets masked: `SET len=N`).
- Last RUNTIME_READY signal id and date.
- Active gate from `CURRENT_STATE.md`.
- UX gate aggregate verdict from `UX_RELEASE_GATE.md`.

Keep the output to ≤ 10 lines so it doesn't dominate the session start.

### C.2 — `subagent_stop.sh`

**Current behavior:** captures subagent exit context.

**Proposed extension:** also enforce the agent-output STATUS block format. If the agent
output is missing the `STATUS:` line, print a warning. Do not block.

### C.3 — `stop.sh`

**Current behavior:** session stop hook.

**Proposed extension:** on session stop, run a quick hygiene scan:
- Confirm `git status --short` is clean.
- Confirm no `.env*` files in the working tree (other than gitignored).
- Confirm frozen flags state matches expected.

Output a one-line summary.

---

## D. Hard-block matrix

| Hook | Hard / warning | Why |
|------|---------------|------|
| Authority doc guard | HARD | doc integrity is high cost |
| Secret guard | HARD | secret leak is irreversible |
| Destructive command guard | HARD with token | data loss is irreversible |
| Archive promotion block | HARD with token | stale code revival |
| Out-of-lane write | WARNING | needs data first |
| UX-visible change without handoff | WARNING | avoid over-firing |
| Button without state | WARNING | many false positives at first |
| Cross-lane PR | WARNING | stylistic, not blocking |

---

## E. False-positive risk assessment

| Hook | Initial FP rate | After 4 weeks | After 12 weeks |
|------|-----------------|---------------|----------------|
| Authority doc guard | low | low | low |
| Secret guard | very low | very low | very low |
| Destructive command guard | medium | low | low (with token) |
| Archive promotion block | very low | very low | very low |
| Out-of-lane write | medium-high | medium | low |
| UX-visible change | medium | low-medium | low |
| Button without state | high | medium | medium |
| Cross-lane PR | medium | medium | medium |

The warning-only set should accumulate 4–12 weeks of false-positive data before any of
them is promoted to hard block. Promotion requires Tom approval + a documented
false-positive rate < 5%.

---

## F. Rollback plan

For every hook addition or extension:

1. Each hook script change must be a separate commit with a clear message and a comment
   block stating "added <YYYY-MM-DD>; rollback: revert this commit."
2. Rollback = `git revert <commit>` followed by session restart so the hook config reloads.
3. For `settings.json` additions: keep `settings.json.bak-<timestamp>` of the prior version
   in the repo for trivial restoration.
4. For `mcp.json` additions: keep a similar backup.
5. Rollback must be Tom-approved (since hooks are part of the operating layer).

---

## G. Settings / `.claude/settings.json` proposals

The current `settings.json` already wires:
- `SessionStart` → `session_start.sh`
- `PreToolUse` (Write|Edit|NotebookEdit|Bash) → `pre_tool_use.sh`
- `SubagentStop` → `subagent_stop.sh`
- `Stop` → `stop.sh`

**No new hooks events are proposed.** The B.1–B.8 hooks all extend `pre_tool_use.sh` rather
than registering new event types. Keeping the event surface flat reduces risk.

**Permissions block (separate from hooks):** propose adding to `permissions.deny`:

```json
"permissions": {
  "deny": [
    "Bash(rm -rf:*)",
    "Bash(git push --force*)",
    "Bash(git reset --hard*)",
    "Bash(git checkout -- *)",
    "Bash(git clean -f*)",
    "Bash(git branch -D *)",
    "Read(.env*)",
    "Read(*.pem)",
    "Read(*.key)",
    "Write(.env*)",
    "Edit(.env*)"
  ]
}
```

`permissions.allow` remains as-is.

**Apply note:** the deny list must be tested in dev mode first because permission denials
are surfaced to the operator; over-denying creates friction.

---

## H. MCP enablement prerequisites

### H.1 — Why MCP remains disabled in Run B

Per CLAUDE.md "Input-source map" — explicitly: "MCP is not a runtime input channel.
Claude Code tooling must not become part of the live operational path."

This is a locked decision. MCP must remain disabled for the **runtime** of GT Factory OS.

The question MCP could legitimately answer: are there governance / audit / metrics reads
that the agents could perform via MCP without becoming a runtime input channel? Possibly.
But the bar for enabling MCP at all is high.

### H.2 — Which agents would (hypothetically) benefit from MCP

| Agent | MCP target | Use case |
|-------|-----------|----------|
| `factory-os-governor` | GitHub MCP | read PR list / commit history without `gh` CLI on operator's machine |
| `release-verifier` | GitHub MCP | read CI status, deploy logs |
| `source-of-truth-auditor` | postgres-readonly MCP | read live schema / contract drift |
| `integration-boundary-executor` | LionWheel / Shopify / GI dedicated MCP | dry-run reads via MCP rather than direct curl |
| `ops-docs-curator` | filesystem MCP | cross-repo doc scans |

**These are hypothetical only.** None of these is approved for Run B.

### H.3 — Credentials required (if Tom ever approves any MCP)

Each MCP server requires a credential. Per `feedback_env_display_allowlist.md`: never
echo credentials; print `SET len=N` only.

Required if approved:
- GitHub MCP: GitHub personal access token (read-only scopes only — `repo:read`).
- postgres-readonly MCP: read-only Postgres role credentials, scoped to specific schemas.
- LionWheel / Shopify / GI MCPs: existing API tokens (already present in `.env`).
- Filesystem MCP: no new credential; uses local filesystem.

### H.4 — Security risk

| MCP | Risk | Mitigation |
|-----|------|-----------|
| GitHub | low (read-only token) | scope-limited token; rotate quarterly |
| postgres-readonly | medium (live DB exposure) | read-only role; no schema write; audit log enabled |
| LionWheel | medium (API quota) | dry-run only; rate-limit |
| Shopify | high (could enable blind-write if scope misconfigured) | DO NOT enable until Phase 5; flag-gated |
| GI | medium | dry-run only |
| Filesystem | low | local-only |

### H.5 — Proposed enablement order (only when Tom approves)

If Tom ever approves MCP enablement, propose this order:

1. **Filesystem MCP** (lowest risk; immediate value for `ops-docs-curator`).
2. **GitHub MCP** (low risk; useful for `factory-os-governor` and `release-verifier`).
3. **postgres-readonly MCP** (medium risk; useful for `source-of-truth-auditor`).
4. **LionWheel / GI MCPs** (medium risk; only after dry-run proof).
5. **Shopify MCP** (highest risk; only after Phase 5 + flag-flip).

**No MCP is enabled in Run B.** The current `mcp.json` is unchanged.

---

## I. CLAUDE.md hardening

### I.1 — Run B does NOT propose CLAUDE.md hardening edits

The CLAUDE.md additions proposed in `PRODUCTION/docs/phase8/authority-doc-patch-proposals.md`
(Run B Step 7) are sufficient for the Run B operating layer. **Additional CLAUDE.md
hardening is deliberately not proposed in Run B.**

If Tom wants additional CLAUDE.md hardening, candidate clauses include:
- Explicit "MCP is forbidden in runtime" clause (already in CLAUDE.md as part of
  "Input-source map" — could be promoted to "Absolute non-negotiables").
- Explicit "destructive operations require Tom written approval" clause.
- Explicit "no agent may push to a remote without explicit user instruction" clause.

These are not proposed for Run B; they are listed as candidates for a future Tom-approved
hardening pass.

### I.2 — Why hardening is gated

CLAUDE.md is a durable contract. Adding clauses to it is irreversible (in practice — a
locked decision that has been removed has weak trust). The bar is:

- The clause prevents a real defect (not a hypothetical one).
- The clause is covered by hooks AND agent definitions AND CLAUDE.md (defense in depth).
- The clause does not contradict any existing locked decision.

Run B does not meet this bar for any candidate clause. Run C or later runs may.

---

## J. Apply order (when Tom approves any subset)

| Apply unit | Risk | Rollback effort | Recommended order |
|-----------|------|-----------------|-------------------|
| Settings `permissions.deny` additions | low | trivial (revert) | 1st |
| Hook B.2 (secret guard) | very low | trivial | 2nd |
| Hook B.4 (archive promotion block) | very low | trivial | 3rd |
| Hook B.1 (authority doc guard) | low | trivial | 4th |
| Hook B.3 (destructive command guard) | low (with token) | trivial | 5th |
| Hook extensions C.1 / C.2 / C.3 | low | trivial | 6th |
| Hook B.5 (out-of-lane warning) | low (warning only) | trivial | 7th |
| Hook B.6 (UX-visible warning) | low (warning only) | trivial | 8th |
| Hook B.7 (button-state warning) | low (warning only) | trivial | 9th |
| Hook B.8 (cross-lane warning) | low (warning only) | trivial | 10th |
| MCP filesystem | medium | revert mcp.json | 11th (only if Tom approves) |
| Other MCPs | medium-high | revert mcp.json + rotate creds | 12th+ (only after dedicated approval pass) |
| CLAUDE.md hardening | high (durable contract change) | hard | last (only after explicit Tom directive) |

Each apply unit should be a separate Tom-approved commit. Bundling reduces auditability.

---

## K. STATUS block

```
STATUS: PASS

Scope: Hooks / settings / MCP / CLAUDE.md hardening implementation plan
Hooks added: 0
Settings changed: 0
MCP enabled: 0
CLAUDE.md edits applied: 0
Plan units defined: 8 hooks + 3 hook extensions + 1 settings update + 5 MCP options + CLAUDE.md candidates
Apply order documented: yes (12+ ordered apply units)
Rollback documented: yes (per unit)
Tom approval required: yes (per unit)
False-positive risk assessed: yes (per hook; warning-only for high-FP hooks)
Stop conditions: none — Run B is plan-only
Handoff: factory-os-governor + Tom (each apply unit awaits Tom written approval)
```

---

**END OF HOOKS / SETTINGS / MCP / CLAUDE.md WAVE 4 PLAN — No hardening applied in Run B.**
