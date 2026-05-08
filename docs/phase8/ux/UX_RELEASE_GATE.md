# UX Release Gate — GT Factory OS Portal

**Owner agent:** `accessibility-usability-auditor` (gate criteria), `factory-os-governor` (verdict)
**Authoritative status:** DRAFT. Gate criteria not yet locked.
**Update rule:** Criteria additions require Tom authorization; P0 threshold is non-negotiable.
**Release-gate relevance:** THIS IS THE GATE. A HOLD verdict from this document blocks all portal releases.

---

## What belongs here

- The formal UX release gate criteria.
- Pass/fail thresholds per dimension.
- The escalation path from a UX HOLD to a Tom decision.

## What must never go here

- Implementation details of how findings are fixed.
- Copy strings or design tokens.
- Backend contracts.

---

## UX release gate — criteria

A portal commit is UX-production-ready when ALL of the following are true:

### Criterion 1 — Zero P0 findings (hard gate)

No P0 (DECISION_GRADE) findings across all five UX dimensions on all audited routes.

P0 examples that block ship:
- A button with no confirmation on an irreversible action.
- An operator-facing form showing a raw backend enum name.
- A surface that shows "0 items" during a loading state.
- An icon-only button with no accessible name.
- A keyboard-unreachable submit button.
- A mandatory form field with no label of any kind.
- A Hebrew string in operator-facing UI on a surface with no Tom-pinned Hebrew register.

### Criterion 2 — Full flow coverage (hard gate for high-frequency surfaces)

For every `/(ops)/` route and `/planning/production-plan`:
- The full operational cycle must be covered: entry → terminal action → post-action visibility → auditability.
- `ux-flow-architect` must have produced a PASS on each flow stage.

### Criterion 3 — State hygiene (hard gate)

For every route:
- Loading / error / empty / loaded states implemented and non-overlapping.
- No chips or count badges during loading or error states.

### Criterion 4 — P1 findings documented

All P1 (FLOW_COMPLETION) findings must be:
- Listed by name in the release note.
- Scheduled for resolution (sprint/cycle identified).
- Tom-acknowledged.

P1 findings do not block ship but must be acknowledged.

### Criterion 5 — portal_ux_standard.md compliance

The route must not violate any locked standard in `portal_ux_standard.md`:
- Language: English only in operator-facing UI.
- Direction: LTR only.
- State hygiene: one primary state at a time.
- Button conventions: per §4.

### Criterion 6 — Copy clean

No forbidden copy patterns (raw enums, UUIDs, developer language, raw error codes) in
operator-facing UI on the routes in scope.

---

## Verdict thresholds

| Verdict | Criteria |
|---------|---------|
| `SHIP` | Criteria 1–3 and 5–6 fully met. Criterion 4 met (P1s documented). |
| `CONDITIONAL_SHIP` | Criteria 1–3, 5–6 met. Criterion 4: P1s present but Tom-acknowledged for next sprint. |
| `HOLD` | Any criterion 1, 2, 3, 5, or 6 not met. |

---

## Gate execution

The gate is run via `/ux-release-gate`. The `factory-os-governor` issues the formal verdict.

### Gate inputs
- Routes in scope (all `/(ops)/` + `/planning/production-plan` for a standard gate; reduced scope for focused gates).
- Portal commit hash being evaluated.
- Five UX agent audit reports for each route in scope.

### Gate outputs
1. Formal verdict: SHIP / CONDITIONAL_SHIP / HOLD.
2. P0 blockers listed (if HOLD).
3. P1 conditionals listed (if CONDITIONAL_SHIP).
4. Tom approval required for CONDITIONAL_SHIP.
5. Next action for Tom.

---

## Escalation path

If a UX agent finds a P0 that requires backend changes to fix (ARCH_REQUIRED):
1. Agent classifies as ARCH_REQUIRED and halts the finding (does not block ship).
2. `factory-os-governor` routes to `backend-db-executor` for a backend fix.
3. After backend fix lands (RUNTIME_READY signal), UX audit re-runs on the affected surface.
4. Gate re-evaluates.

ARCH_REQUIRED findings are tracked but do not block ship if the UX surface degrades gracefully
in the absence of the missing backend capability.

---

## Gate history

| Date | Portal commit | Verdict | P0 count | P1 count | Audited routes |
|------|--------------|---------|----------|----------|----------------|
| — | — | NOT_RUN | — | — | — |
