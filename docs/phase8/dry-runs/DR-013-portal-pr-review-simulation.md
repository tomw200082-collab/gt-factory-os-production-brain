# Dry-Run DR-013 — portal PR review simulation

**Run date:** 2026-05-08
**Agents invoked:** `portal-production-executor` (review-only mode), all four UX agents
(`ux-flow-architect`, `interaction-design-specialist`, `ux-content-state-designer`,
`accessibility-usability-auditor`), `release-verifier`, `factory-os-governor`.
**Scope:** Process simulation — no real PR exists. The dry-run validates how the new
`/portal-pr-review` command coordinates the agents and produces a verdict.
**FLOW-003 status:** confirmed P0 per DR-011; aggregate UX gate is HOLD.

---

## A. Why a process simulation rather than a real PR review

Run B is "controlled execution layer build-out." Product code is not allowed to change.
There is no in-flight portal PR to review against `gt-factory-os-portal/main` in this
session. To prove the new portal-review brain works without authoring a real review, this
dry-run simulates the `/portal-pr-review` command against a hypothetical PR with three
representative diff classes:

1. A small accessibility fix on `/(ops)/stock/waste-adjustments` (low-risk fix path).
2. A copy change introducing a new Hebrew string (Tom-register gate path).
3. A change touching `/planning/blockers` substrate code (FLOW-003 freeze gate path).

The simulation tests whether the agent network produces the **right verdict** for each
class, not whether real lines pass.

---

## B. PR class 1 — small a11y fix on `/(ops)/stock/waste-adjustments`

### Hypothetical diff

```
src/app/(ops)/stock/waste-adjustments/page.tsx |  3 +++
1 file changed, 3 insertions(+)
```

The change adds `aria-labelledby` to the Item / component combobox, the Quantity input,
and the Notes textarea — closing **A11Y-001** (three inputs lacking programmatic labels per
DR-011 §D.1 / Observation).

### Process executed by `/portal-pr-review`

1. `portal-production-executor` reads the diff (3 inserts).
2. `accessibility-usability-auditor` confirms the fix matches the documented A11Y-001 finding.
3. `ux-flow-architect` confirms no flow change.
4. `ux-content-state-designer` confirms no copy change.
5. `interaction-design-specialist` confirms no interaction change.
6. `visual-system-designer` confirms no token change.
7. RUNTIME_READY check: not API-bound; n/a.
8. FLOW-003 freeze check: `/(ops)/stock/waste-adjustments` is not in the freeze list. PASS.
9. `release-verifier` confirms clean tree, no `.env` in diff, no secrets.
10. `factory-os-governor` issues verdict.

### Expected verdict

**`MERGE_OK`** — clean a11y fix with documented finding; release-verifier independent confirmation
required at merge time; no Tom approval needed.

### What this proves

The new system can route a low-risk fix to a clean MERGE_OK without inventing extra friction.
It also proves the chain *does* require all UX agents to confirm "no impact in my domain"
before the verdict, not just the relevant one.

---

## C. PR class 2 — new Hebrew copy on a non-frozen surface

### Hypothetical diff

```
src/app/(planning)/planning/page.tsx       |  2 +-
src/app/(planning)/planning/_lib/copy.ts   | +5
2 files changed, 6 insertions(+), 1 deletion(-)
```

The change adds a new helper string `"חישוב הצעת רכש מתעדכן…"` ("purchase recommendation
recalculating…") to a planner-facing surface that does not have a Tom-approved register
entry for this string.

### Process executed by `/portal-pr-review`

1. `portal-production-executor` reads the diff and detects new Hebrew copy.
2. `ux-content-state-designer` checks the Hebrew register for the new string.
3. Register lookup: **MISS**. The string has no entry in `portal_ux_standard.md` or
   `CONTENT_AND_MICROCOPY_GUIDE.md` for this surface.
4. `accessibility-usability-auditor`, `interaction-design-specialist`,
   `ux-flow-architect`, `visual-system-designer` all clean.
5. FLOW-003 freeze: surface is not `/planning/blockers`; PASS the freeze check.
6. `release-verifier` clean.
7. `factory-os-governor` issues verdict.

### Expected verdict

**`HOLD_FOR_TOM`** — copy is new; Tom must add the register entry before merge.
Specifically:
- The string is operationally clear in plain Hebrew.
- It does not cross any locked decision.
- It still requires Tom register entry per `feedback_portal_ui_english_ltr.md`:
  "Hebrew only on surfaces with explicit Tom-pinned register."

### What this proves

The chain correctly identifies that a *non-FLOW-003* Hebrew copy change still needs Tom
approval. A naive system would treat all Hebrew on planner surfaces as pre-approved (because
planning surfaces use Hebrew); the correct behavior is per-string register, not per-surface.

---

## D. PR class 3 — diff touches FLOW-003 frozen files

### Hypothetical diff

```
src/app/(planning)/planning/blockers/_lib/labelMaps.ts | 1 +/-
1 file changed, 1 insertion(+), 1 deletion(-)
```

The change rewords `"פנה למפתח"` → `"שלח לדב את ID החסם"` (Option C tightening per the
FLOW-003 decision packet).

### Process executed by `/portal-pr-review`

1. `portal-production-executor` reads the diff.
2. **First** check: FLOW-003 freeze list. `_lib/labelMaps.ts` IS in the freeze list per the
   FLOW-003 decision packet §O.
3. The chain **STOPS** at this gate. No further agent review is needed; the verdict is
   pre-determined by the freeze.
4. The chain produces a `BLOCK` verdict with citation to:
   - `PRODUCTION/docs/phase8/decisions/FLOW-003-planning-blockers-p0-decision-packet.md`
   - The Tom-locked verbatim comment at `labelMaps.ts:33`.
5. `release-verifier` reports `flow_003_freeze_violation`.
6. `factory-os-governor` issues `BLOCK`.

### Expected verdict

**`BLOCK`** — FLOW-003 freeze violation. Even if Tom would later approve Option C, this
specific PR does not have the requisite written Tom approval cited inline. The chain refuses
to merge it under the decision-packet gate.

### What this proves

The chain correctly enforces the FLOW-003 freeze even when the proposed change matches the
recommendation in the FLOW-003 decision packet. The freeze is a procedural gate; matching
the recommendation is necessary but not sufficient. **Tom written approval must appear
inline in the PR description before the freeze can be lifted for that PR specifically.**

---

## E. Process findings

### E.1 — How portal PRs should be reviewed

The chain is correct. The simulation shows:

1. The diff drives the gate set, not the surface name.
2. The freeze list is checked **first**; nothing else matters until that check passes.
3. RUNTIME_READY is checked only when the diff is API-bound.
4. The Hebrew register is checked per-string, not per-surface.
5. A11y / interaction / flow / content / visual-system agents all sign off in parallel; any
   "MISS" produces a verdict block, not just an advisory note.
6. `release-verifier` is the gate for clean tree, secrets, scope; it does not duplicate the
   UX gate.
7. `factory-os-governor` aggregates and issues the final verdict.

### E.2 — UX handoff requirement

A user-visible surface change in the diff requires a UX handoff packet for that surface.
The simulation's class 1 fix did not require a new packet (A11Y-001 finding pre-existed
per DR-011). Class 2 would have required a register entry from `ux-content-state-designer`,
which is the handoff format for copy changes. Class 3 is frozen entirely.

### E.3 — What blocks merge

| Block reason | When triggered |
|--------------|---------------|
| FLOW-003 freeze touched | Diff includes any of the four frozen files for `/planning/blockers` |
| Hebrew register MISS | Diff includes new or changed Hebrew copy |
| Backend file in diff | Diff includes any path under `gt-factory-os/api/**` or `db/**` |
| `.env*` in diff | Diff includes any `.env*` |
| Auth-flow file in diff | Diff includes `middleware.ts` or `(auth)/**` |
| `next.config.*` or `tsconfig.json` in diff | Build/tooling change |
| RUNTIME_READY missing for API-bound change | Surface uses an unwritten endpoint |
| UX_RELEASE_GATE shows HOLD on the surface | Aggregate gate not yet cleared |

### E.4 — What can be deferred

| Deferable item | Why |
|---------------|-----|
| Visual-system audit when no token used | `visual-system-designer` may rubber-stamp |
| Flow audit when no flow change | `ux-flow-architect` may rubber-stamp |
| A11y audit when no input/focus change | `accessibility-usability-auditor` may rubber-stamp |
| Browser smoke test | Required for `portal-production-executor` to commit, not for the review chain |

A "rubber-stamp" still produces a verdict line in the report, just a clean one. The agent
must explicitly say "no impact in my domain"; silence is not consent.

---

## F. Coordination matrix

| Class | a11y | interaction | flow | content | visual | RUNTIME_READY | freeze | release-verifier | governor verdict |
|-------|------|------------|------|---------|--------|---------------|--------|------------------|------------------|
| 1: a11y fix | confirms fix | n/a | n/a | n/a | n/a | n/a | clear | clean | MERGE_OK |
| 2: new copy | n/a | n/a | n/a | **HOLD** | n/a | n/a | clear | clean | HOLD_FOR_TOM |
| 3: freeze touched | (not run) | (not run) | (not run) | (not run) | (not run) | (not run) | **BLOCK** | n/a | BLOCK |

The matrix demonstrates that the chain stops as soon as a hard block fires. It does not
waste agent cycles on a foregone conclusion.

---

## G. STATUS block

```
STATUS: PASS

Scope: portal PR review chain coordination simulation (3 representative diff classes)
Files changed: 0 (no real PR exists; simulation only)
Tests run: 0 (no real diff to test)
Verdicts produced: 3 (MERGE_OK, HOLD_FOR_TOM, BLOCK)
FLOW-003 freeze respected: yes (class 3 explicitly blocked)
RUNTIME_READY check: applied where relevant
UX handoff requirement: confirmed for user-visible changes
Stop conditions tripped: flow_003_freeze_violation (class 3 only — by design)
Tom approvals required: register entry (class 2); FLOW-003 lift (class 3, pending decision packet)
Rollback plan: n/a — no production change
Handoff: factory-os-governor — chain validated
```

---

**END OF DR-013 — Portal PR review chain validated. No real PR reviewed. No portal source touched.**
