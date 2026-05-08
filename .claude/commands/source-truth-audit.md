# /source-truth-audit

Invoke the `source-of-truth-auditor` to find conflicting, stale, orphaned, and duplicate facts
across GT Factory OS authority documents, memory, agents, commands, and docs.

## Purpose

Scans all authority-bearing files, classifies every fact that exists in more than one place, and
proposes exact text patches to reconcile conflicts. Does not apply patches automatically.
Read-only. Produces a structured audit report with conflict classification and patch proposals.

## Usage

```
/source-truth-audit
/source-truth-audit --scope <area>
/source-truth-audit --focus <D1|D2|D3|D4|D5|D6|D7|D8|D9|D10>
/source-truth-audit --quick
```

**With no argument:** full scan of all authority docs, memory, agents, commands, docs, and archive.

**With `--scope`:** limit to a named area. Valid scopes:
- `authority` — CLAUDE.md, CURRENT_STATE.md, EXECUTION_POLICY.md, WORKSPACE_MAP.md, ACTIVE_NOW.md
- `state` — runtime_ready.json, active_mode.json, SIGNALS.md
- `agents` — .claude/agents/*.md
- `commands` — .claude/commands/*.md
- `memory` — memory/MEMORY.md, memory/*.md
- `docs` — PRODUCTION/docs/**, gt-factory-os/docs/**, gt-factory-os-portal/docs/**
- `archive` — PRODUCTION/archive/** (read for historical context only)

**With `--focus`:** run only the named D-series conflict check (D1–D10). Fast targeted check.

**With `--quick`:** scan only authority docs and harness state (skips memory, archive, portal docs).

## Agents involved

Primary: `source-of-truth-auditor`
Supporting: `factory-os-governor` (conflict resolution when authority hierarchy is ambiguous)

## Required inputs

The auditor reads all files within the declared scope. No argument → full scope.

Key files always included regardless of scope flag:
- `PRODUCTION/CLAUDE.md`
- `PRODUCTION/CURRENT_STATE.md`
- `PRODUCTION/EXECUTION_POLICY.md`
- `PRODUCTION/.claude/state/runtime_ready.json`
- `PRODUCTION/.claude/state/active_mode.json`

## Required outputs

```
## source-of-truth-auditor report

### Scope audited
### Summary (counts by class)

### Conflicts (detailed)
#### [CONFLICT-NNN] <name>
- Class: STALE / CONFLICTING / ORPHANED / SHADOW
- Authoritative copy: <path> — <section> — <content>
- Conflicting copy: <path> — <section> — <content>
- Resolution: <cite authority hierarchy>
- Patch proposal: <exact text diff, or "requires Tom decision">

### D-series scan (D1–D10)
| ID | Status | Finding |

### Recommended next actions
### Tom decisions required
```

## Write policy

**Read-only.** Audit reports may be saved to `PRODUCTION/docs/phase8/dry-runs/` when run with
`--save` or in dry-run mode. No automatic edits to authority docs. No git mutations.

## Patch proposal policy

Patches are proposed, never applied. The format is exact text replacement — a human or
`factory-os-governor`-approved executor applies them. Every patch proposal includes:
- File to edit
- Authoritative source
- Current text (exact)
- Proposed replacement (exact)
- Reason
- Tom approval required: yes / no
- Risk: LOW / MEDIUM / HIGH

Changes to `CLAUDE.md` are never proposed as patches — those require Tom directly.

## Stop conditions

- A conflict suggests a locked `CLAUDE.md` decision was violated post-lock → halt, escalate.
- A conflict cannot be resolved by the authority hierarchy → escalate to Tom.
- A `runtime_ready.json` signal is missing for a gate claimed as closed → halt, escalate.
- A memory file references a deleted artifact → flag ORPHANED, continue scan.

## Not usable for

- Applying patches automatically.
- Editing `CLAUDE.md`.
- Changing harness state files directly.
- Resolving conflicts that require Tom's architectural judgment.
