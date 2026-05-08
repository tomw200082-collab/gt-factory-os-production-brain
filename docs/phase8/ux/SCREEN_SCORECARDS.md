# Screen Scorecards — GT Factory OS Portal

**Owner agent:** All five UX agents (one scorecard per surface per audit cycle)
**Authoritative status:** LIVE — updated after each /screen-scorecard run.
**Update rule:** Each /screen-scorecard run appends a new versioned scorecard entry for the surface.
**Release-gate relevance:** A surface with any RED dimension blocks ship via /ux-release-gate.

---

## What belongs here

- Versioned scorecard entries for each audited surface.
- P0/P1/P2/P3 counts per UX dimension per audit cycle.
- Overall SHIP_READY / NEEDS_WORK / BLOCKED rating.

## What must never go here

- Full finding details (those belong in the individual dry-run or audit files).
- Backend contracts or implementation details.
- Copy string proposals.

---

## Scorecard format

```
### <Route> — Audit <YYYY-MM-DD>

| Dimension | P0 | P1 | P2 | P3 | Status |
|---|---|---|---|---|---|
| Flow | 0 | 0 | 0 | 0 | — |
| Interaction | 0 | 0 | 0 | 0 | — |
| Visual | 0 | 0 | 0 | 0 | — |
| Copy | 0 | 0 | 0 | 0 | — |
| Accessibility | 0 | 0 | 0 | 0 | — |

Overall: NOT_AUDITED

Top P0 findings: (none)
Audit files: (none)
```

**Status thresholds:**
- GREEN — 0 P0, ≤2 P1
- AMBER — 0 P0, >2 P1 OR ≤1 P0 (non-blocking known issue)
- RED — ≥1 blocking P0

**Overall rating:**
- SHIP_READY — all GREEN
- NEEDS_WORK — any AMBER
- BLOCKED — any RED

---

## Scorecards

### /(ops)/goods-receipt — NOT YET AUDITED

Audit pending. Priority: HIGH (highest operator frequency, PO-link flow).
See OPERATIONAL_FLOW_MAP.md for signal reference.

---

### /(ops)/waste-adjustment — NOT YET AUDITED

Audit pending. Priority: HIGH (earliest RUNTIME_READY; likely drift).

---

### /(ops)/physical-count — NOT YET AUDITED

Audit pending. Priority: HIGH (count freeze semantics; blind count flow).

---

### /(ops)/production-actual — NOT YET AUDITED

Audit pending. Priority: MEDIUM.

---

### /planning/blockers — NOT YET AUDITED

Audit pending. Priority: HIGH (known Hebrew P0 findings from overnight audit 2026-05-01).

---

### /planning/production-plan — NOT YET AUDITED

Audit pending. Priority: MEDIUM.

---

### /planning/runs — NOT YET AUDITED

Audit pending. Priority: LOW.

---

### /planning/forecast — NOT YET AUDITED

Audit pending. Priority: MEDIUM.

---

### /planning/inventory-flow — NOT YET AUDITED

Audit pending. Priority: LOW.

---

### /po (list) — NOT YET AUDITED

Audit pending. Priority: MEDIUM.

---

### /po/[id] (detail) — NOT YET AUDITED

Audit pending. Priority: MEDIUM.

---

### /po/[id]/edit — NOT YET AUDITED

Audit pending. Priority: HIGH (complex action surface; irreversible operations).

---

### /po/new — NOT YET AUDITED

Audit pending. Priority: MEDIUM.

---

### /dashboard — NOT YET AUDITED

Audit pending. Priority: MEDIUM.

---

## Running scorecard

| Surface | Last audit | Overall | P0s |
|---|---|---|---|
| All | — | NOT_AUDITED | — |
