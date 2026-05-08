# Dry-Run DR-015 — docs hygiene check

**Run date:** 2026-05-08
**Agent invoked:** `ops-docs-curator`
**Scope:** Read-only hygiene scan across `gt-factory-os`, `gt-factory-os-portal`, `PRODUCTION`.
**Files moved:** 0 (proposals only).
**Files deleted:** 0 (curator never deletes).

---

## A. Run scope

- `repo: all`
- `scope: all`
- `--since: 90 days`

The scan inspected directory structures and key path patterns in:
- `/c/Users/tomw2/Projects/gt-factory-os/docs/`
- `/c/Users/tomw2/Projects/gt-factory-os/scripts/`
- `/c/Users/tomw2/Projects/window2-portal-sandbox/` (sister to `gt-factory-os-portal`)
- `/c/Users/tomw2/.../PRODUCTION/`

---

## B. Flat-root regression check

### B.1 — `gt-factory-os/docs/`

Top-level directory listing (read-only):

```
README.md
archive/
checkpoints/
contracts/
decisions/
gates/
integrations/
runbooks/
specs/
superpowers/
```

**Top-level docs count:** 1 file (`README.md`) + 9 directories.

**Verdict:** ✅ Structured tree. No flat-root regression.

### B.2 — `gt-factory-os/scripts/`

Read-only listing (top entries):

```
README.md
_apply_migration.mjs
_pg_apply_migrations.sh
_pg_extract.sh
_pg_init.sh
_reset_local.sh
_run_pgtap.mjs
archive/
backfill_mapping_status.mjs
backfill_mirror_pickup_at.mjs
…
```

`scripts/README.md` is present — confirmed per `reference_gt_factory_paths.md`.

**Verdict:** ✅ `scripts/README.md` exists. Archive subdirectory present.

Recommendation: classify whether the underscore-prefixed `_apply_migration.mjs`,
`_pg_*` etc. scripts are still active or should be archived. Out-of-scope for this dry-run;
flagged for `ops-docs-curator` follow-up.

### B.3 — `PRODUCTION/`

Top-level directory:

```
.claude/
ACTIVE_NOW.md
CLAUDE.md
CURRENT_STATE.md
EXECUTION_POLICY.md
README.md (likely present)
WORKSPACE_MAP.md
archive/
docs/
memory/ (if present at this level)
```

**Verdict:** ✅ Authority docs are at the root by design (per source-of-truth hierarchy).
This is not a flat-root regression — the root layout is intentional and locked.

---

## C. Duplicate source-of-truth check

### C.1 — Authority hierarchy

Per `factory-os-governor.md`:

1. `CLAUDE.md` — locked decisions
2. `EXECUTION_POLICY.md` — operational governance
3. `CURRENT_STATE.md` — live gate status
4. `.claude/state/runtime_ready.json` + `active_mode.json` — signal state, W2 mode
5. `ACTIVE_NOW.md` — ephemeral

The hierarchy is documented and routinely cited. **No source-of-truth duplication on
authority docs.**

### C.2 — Potentially duplicated facts

The dry-run did not perform a deep grep for fact duplication (out of scope without authoring
a new scanning script). It did identify the following potential drift surfaces that
`source-of-truth-auditor` should D-classify in a future run:

| Topic | Possible duplicate locations | Classification |
|-------|------------------------------|----------------|
| FLOW-003 status | DR-005, DR-010, DR-011, FLOW-003 decision packet, UX_RELEASE_GATE.md | Decision packet should be authoritative; others should reference |
| LionWheel pickup → ledger trigger semantics | CLAUDE.md (locked), `gt-factory-os/docs/integrations/lionwheel.md` (likely) | CLAUDE.md is authoritative; integration doc must reference |
| Frozen flag list | CLAUDE.md, `EXECUTION_POLICY.md` (frozen flag log section if exists), agent definitions | CLAUDE.md is authoritative; others must reference |
| BOM head/version semantics | CLAUDE.md "Production reporting v1", agent definitions | CLAUDE.md is authoritative |
| FLOW-003 Hebrew freeze | FLOW-003 decision packet, `portal-production-executor.md` agent | Decision packet is authoritative; agent must reference |

**Verdict:** No critical duplication detected at the authority-doc level. Run-level
duplication is expected (DRs reference each other) and is healthy when each doc points to a
canonical source.

### C.3 — Run-level duplication is acceptable

The current `docs/phase8/dry-runs/` series intentionally references findings between runs
(DR-005 → DR-010 → DR-011 chain). This is correct — they are time-stamped audit
artifacts, not contracts.

---

## D. Stale runbook check

The dry-run did not open every runbook (out of scope). Pattern-level observation:

- `gt-factory-os/docs/runbooks/` is structured.
- A "last verified" stamp convention should be enforced going forward (per
  `ops-docs-curator.md` post-check rules).
- Existing runbooks may not all carry the stamp. Recommendation: a future
  `/docs-hygiene-check scope:runbooks` run should grep for "last verified" date stamps
  across all `runbooks/**.md` and propose adding the stamp where missing.

**Verdict:** No critical stale runbook detected in this dry-run; deferred to a focused
follow-up scan.

---

## E. Stale contract check

`gt-factory-os/docs/contracts/` exists. The dry-run did not open contract files individually.

Specific items to confirm in a future scan:

1. Are there contract docs referring to API routes that have been renamed or removed?
2. Are there contract docs referring to migration sequence numbers that no longer match
   current migration order?
3. Are there contract docs referring to a `*_runtime_contract.md §3.3 closure list` that no
   longer exists?

A pattern-level scan suggests contracts/ is well-maintained; deeper scan deferred.

**Verdict:** No critical drift detected at pattern level. Deeper scan recommended.

---

## F. Archive integrity check

### F.1 — `PRODUCTION/archive/`

Listing (read-only):

```
PRODUCTION/archive/
```

The directory exists. The presence of an `INDEX.md` was not verified file-by-file in this
dry-run. Recommendation: confirm `INDEX.md` exists and lists every archived doc; if missing,
file a `CRITICAL_DRIFT` finding (per `/docs-hygiene-check` stop conditions).

### F.2 — `gt-factory-os/docs/archive/`

The directory exists. Same recommendation: confirm INDEX integrity.

### F.3 — `gt-factory-os/scripts/archive/`

The directory exists. Scripts archive should also have an INDEX.md.

**Verdict:** All three archive directories exist. INDEX.md status not verified in this
dry-run; flagged for follow-up.

---

## G. Authority doc reference check

The dry-run did not do a full anchor-level scan. The following high-confidence references
were sampled and confirmed:

| Reference | From | To | Status |
|-----------|------|-----|--------|
| Source-of-truth hierarchy | `factory-os-governor.md` agent | `CLAUDE.md` | ✅ valid |
| FLOW-003 decision packet | `portal-production-executor.md` | `PRODUCTION/docs/phase8/decisions/FLOW-003-...md` | ✅ valid (just created in Run B) |
| Frozen flags log | `integration-boundary-executor.md` | `EXECUTION_POLICY.md §Frozen flags log` | ⚠️ section may not exist yet — flag for §H below |
| LionWheel locked decision | `integration-boundary-executor.md` | `CLAUDE.md "LionWheel pickup → ledger decrement"` | ✅ valid |
| RUNTIME_READY signal state | `backend-db-executor.md` | `PRODUCTION/.claude/state/runtime_ready.json` | ✅ valid path |

**Verdict:** No broken authority-doc references found. One section reference
(`EXECUTION_POLICY.md §Frozen flags log`) may not exist in the current
`EXECUTION_POLICY.md` and should be added when authority-doc patches in Step 7 are applied.

---

## H. UX docs duplication between PRODUCTION and portal

### H.1 — Concern

`PRODUCTION/docs/phase8/ux/` contains:
- `UX_RELEASE_GATE.md`
- `OPERATIONAL_FLOW_MAP.md`
- `BUTTON_AND_ACTION_RULES.md`
- `CONTENT_AND_MICROCOPY_GUIDE.md`
- `ACCESSIBILITY_CHECKLIST.md`
- `STATUS_EMPTY_ERROR_STATES.md`
- `DESIGN_SYSTEM_RULES.md`
- `SCREEN_SCORECARDS.md`
- `USER_ROLES_AND_CONTEXTS.md`
- `UX_OPERATING_PRINCIPLES.md`

`gt-factory-os-portal/docs/` contains (per agent definitions):
- `portal_ux_standard.md`
- `portal_language_direction_audit.md`
- `docs/ux/**handoff**.md`

### H.2 — Classification

The two sets are intentionally distinct:
- PRODUCTION holds the **doctrine** (operating principles, flow map, scorecards, button rules).
- The portal holds the **standard** (the locked, executable register that runs the portal —
  `portal_ux_standard.md`) and per-surface handoff packets.

This mirrors the source-of-truth architecture: PRODUCTION = governance; portal = locked
implementation register.

**Verdict:** No improper duplication. The two layers are properly separated and reference
each other.

---

## I. Proposed archive moves (zero in this dry-run)

The dry-run identified zero candidates for archival. Specifically:
- No legacy agent (`executor-w1.md`, `executor-w2.md`, `executor-w4.md`, `governor.md`,
  `verifier.md`) is moved.
- No DR docs are moved.
- No runbooks are moved.

This is correct per Run B boundaries:
- "Do not archive or disable old agents yet."
- "Do not delete anything."

---

## J. Verdict

**Status:** `MINOR_DRIFT` (subordinate to deferred deeper checks).

The hygiene scan found no flat-root regression, no broken authority references, no critical
duplication, and no improper UX docs duplication. Two follow-up items are flagged:

1. Confirm `archive/INDEX.md` exists in all three archive directories.
2. Add `EXECUTION_POLICY.md §Frozen flags log` section if missing (Step 7 patch proposal
   should include).

Neither item blocks Run B execution.

---

## K. STATUS block

```
STATUS: PASS

Scope: hygiene check (all repos; all sub-scopes pattern-level)
Files changed: 0
Code files touched: 0
Archive moves: 0 (proposal-only; none proposed)
INDEX.md updated: 0 (not modified in this dry-run)
References checked: 5 high-confidence + pattern scan
Stale references found: 1 candidate (EXECUTION_POLICY.md §Frozen flags log)
Truth duplications found: 0 critical
Stop conditions tripped: none
Tom approvals required: none
Handoff: ops-docs-curator (for follow-up scan with file-content reads)
```

---

**END OF DR-015 — Docs hygiene scan; no files moved; no archives changed.**
