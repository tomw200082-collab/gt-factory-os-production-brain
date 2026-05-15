# /docs-hygiene-check

Read-only hygiene scan of the operational documentation ecosystem. Identifies flat-root
regressions, duplicate source-of-truth, stale archive references, runbook freshness, and
orphaned doc references. Coordinated by `ops-docs-curator`. Proposes archive moves only;
never deletes; never edits authority docs.

## Purpose

Keep documentation hygiene measurable and acted on without burying executors or governors in
ambient cleanup. The check produces a single report Tom can review in 5 minutes and route to
`ops-docs-curator` for proposal-only fixes.

## Usage

```
/docs-hygiene-check
/docs-hygiene-check repo:gt-factory-os
/docs-hygiene-check repo:gt-factory-os-portal
/docs-hygiene-check repo:PRODUCTION
/docs-hygiene-check scope:runbooks
/docs-hygiene-check scope:contracts
/docs-hygiene-check scope:archive
/docs-hygiene-check scope:flat-root
```

## Arguments

| Arg | Required | Description |
|-----|---------|-------------|
| repo | no | Limit scan to one repo. Default: all three. |
| scope | no | Limit scan to one of `runbooks`, `contracts`, `archive`, `flat-root`, `references`, `all`. Default `all`. |
| --since | no | ISO date for "stale" threshold. Default: 90 days. |

## Agents involved

| Agent | Role |
|-------|------|
| `ops-docs-curator` | Drives the scan; produces report; proposes archive moves |
| `source-of-truth-auditor` | (Optional) deep-scans for D-classification of any drift detected |
| `factory-os-governor` | (Optional) issues go/no-go on any archive-move proposal |

## Required inputs

1. The scope argument (or default `all`).
2. List of all `*.md` files under the in-scope repo(s) and folders.
3. `PRODUCTION/archive/INDEX.md` (or its absence — flagged if missing).
4. `gt-factory-os/docs/contracts/`, `gt-factory-os/docs/integrations/`, `gt-factory-os/docs/runbooks/`.
5. `gt-factory-os-portal/docs/` excluding the UX standards docs (which are UX agent territory).
6. `PRODUCTION/docs/` and `PRODUCTION/archive/`.

## Required outputs

A hygiene report at `PRODUCTION/docs/phase8/hygiene/HC-<NNN>-<date>.md` containing:

1. **Run metadata** — date, scope, repos scanned, file counts.
2. **Flat-root regression check** — any directory with > 30 unstructured top-level docs
   (configurable threshold). Lists offenders.
3. **Duplicate source-of-truth check** — facts stated in two or more docs without explicit
   cross-reference. Lists each duplication with locations and proposed canonical owner.
4. **Stale runbook check** — runbooks without a "last verified" date stamp, or older than
   the --since threshold. Lists each.
5. **Stale contract check** — contract docs whose referenced symbols (file paths, function
   names, route paths) no longer appear in the codebase. Lists each.
6. **Orphaned doc check** — docs with zero inbound references from active code or other docs.
   Excludes docs in `archive/`. Lists each candidate.
7. **Archive integrity check** — archive docs without an INDEX.md entry; INDEX.md entries
   pointing to nonexistent paths. Lists each.
8. **Registry integrity check (MANDATORY)** — count-vs-disk verification for `PRODUCTION/AGENT_REGISTRY.md` and `PRODUCTION/COMMAND_REGISTRY.md`. The check must:
   - Compute `ls PRODUCTION/.claude/agents/*.md | wc -l` and compare against the "Total active agents" claim in `AGENT_REGISTRY.md`.
   - Compute `ls PRODUCTION/.claude/commands/*.md | wc -l` and compare against the "Total active commands" claim in `COMMAND_REGISTRY.md`.
   - Verify per-section subtotals in each registry sum to the global total (e.g., COMMAND_REGISTRY: UX + governance + execution = global). Any section header showing a count must match the actual table-row count beneath it.
   - Verify every agent file on disk has a row in AGENT_REGISTRY, and every row in AGENT_REGISTRY points to a file that exists. Same check for COMMAND_REGISTRY.
   - Lists each mismatch with: claimed count, actual count, missing/extra entries, exact line reference.
   - Mandatory trigger: any commit touching `PRODUCTION/AGENT_REGISTRY.md`, `PRODUCTION/COMMAND_REGISTRY.md`, `PRODUCTION/.claude/agents/**`, or `PRODUCTION/.claude/commands/**` must run this sub-check before the commit lands. If `/docs-hygiene-check` is invoked with no scope arg, this sub-check always runs.
9. **Authority doc reference check** — docs referencing CLAUDE.md, EXECUTION_POLICY.md,
   WORKSPACE_MAP.md, CURRENT_STATE.md by section/anchor that no longer exists. Lists each.
10. **Verdict** — one of:
    - `CLEAN` — all checks green; no proposals.
    - `MINOR_DRIFT` — limited proposals; no critical drift.
    - `SIGNIFICANT_DRIFT` — multiple categories show drift; recommend a focused
      `ops-docs-curator` follow-up run.
    - `CRITICAL_DRIFT` — authority doc references broken, contract drift detected, or registry integrity broken;
      escalate to `factory-os-governor`.
11. **Proposed archive moves** — list of (original_path, proposed_archive_path, reason).
    Each proposal is **proposal only**; not executed.

## Allowed scope (read-only)

- Read all `*.md` files in scope.
- Read all source code files (read-only) for inbound-reference checks.
- Read recent git log (read-only).
- Write the hygiene report doc.
- Write a hygiene history entry under `PRODUCTION/docs/phase8/hygiene/INDEX.md`.

## Forbidden scope

- **No edits to any doc** other than the hygiene report and its INDEX.
- **No archive moves** — propose only; the actual move is a separate Tom-approved step.
- **No deletions, ever.**
- **No edits to authority docs.**
- **No edits to UX standards.**
- **No code changes.**
- **No external API calls.**

## Side-effect policy

Writes the hygiene report and the optional INDEX entry. No other state changes.

## Validation requirements

The command must verify:

1. The scan covered every in-scope file (no time-based truncation).
2. Every duplicate-truth proposal names the canonical owner (the one that should keep the
   fact; the others should reference it instead).
3. Every archive-move proposal includes a reference check showing zero live inbound references.
4. Every "stale runbook" proposal cites the missing "last verified" stamp.
5. Every "stale contract" proposal cites the specific symbol or path that no longer exists.
6. The registry integrity sub-check ran (mandatory; never skipped) and its disk-vs-claim numbers are recorded in the report — even when both registries are clean.

## Tom approval triggers

The hygiene report alone authorizes nothing. Tom must explicitly authorize:

- Any archive move proposed by the report.
- Any patch to authority docs that the report identifies as needed (Tom is the only writer).
- Any reorganization that moves a doc out of its current path.
- Any new INDEX.md (if missing).

## Stop conditions

| Condition | Action |
|-----------|--------|
| `archive/INDEX.md` missing | `CRITICAL_DRIFT` — propose creation; do not auto-create |
| Authority doc reference broken | `CRITICAL_DRIFT` — escalate to factory-os-governor |
| Contract doc references symbol no longer in codebase | `SIGNIFICANT_DRIFT` — route to canonical author |
| Same fact stated in three or more docs without cross-reference | `SIGNIFICANT_DRIFT` |
| Flat-root regression detected (> 30 unstructured top-level docs) | `SIGNIFICANT_DRIFT` |
| Doc with active inbound reference proposed for archive | `STOP` — never propose archiving an actively-referenced doc |
| AGENT_REGISTRY or COMMAND_REGISTRY count claim mismatches disk reality | `CRITICAL_DRIFT` — registry integrity is broken; escalate to factory-os-governor; `ops-docs-curator` proposes the patch |
| Per-section subtotal in a registry does not match table-row count | `SIGNIFICANT_DRIFT` — same-day fix expected before next dispatch |
| Agent or command file on disk has no registry row, or vice versa | `CRITICAL_DRIFT` — registry no longer indexes the active surface |

## GitHub / mobile usability

- The report is plain markdown; suitable for review in any editor or browser.
- The command does not interact with GitHub.

## Local-only limitations

- The scan operates on the local file tree. It does not check GitHub-only files (e.g. PR
  descriptions, issue templates).

## Example

```
/docs-hygiene-check
/docs-hygiene-check repo:PRODUCTION
/docs-hygiene-check scope:flat-root
/docs-hygiene-check scope:contracts repo:gt-factory-os
```

## Not usable for

- Executing archive moves (proposal only).
- Deleting any doc.
- Editing authority docs.
- Editing UX standards.
- Editing runtime code.
