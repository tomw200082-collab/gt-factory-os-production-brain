# Dry-Run DR-009 — /empty-error-state-audit + accessibility audit /(ops)/stock/waste-adjustments

**Run date:** 2026-05-08
**Command:** `/empty-error-state-audit /(ops)/stock/waste-adjustments`
**Run type:** Dry-run (read-only; structural analysis + RUNTIME_READY signal evidence)
**Agents:** interaction-design-specialist, accessibility-usability-auditor

---

## Empty/error/loading state audit — Waste Adjustment

### Surface audited
- Route: `/(ops)/stock/waste-adjustments`
- RUNTIME_READY signal: `WasteAdjustment` (#1), emitted 2026-04-17T16:54:13Z
- Portal tip at audit: `9605553`

### Signal evidence (from runtime_ready.json)

Signal #1 notes confirm:
- 33/33 pgTAP green; 44/44 pgTAP count-freeze tests green.
- Live-DB smoke matrix: 7 cases (auth + Zod + auto-post + idempotent replay + 2 pending categories + ITEM_TYPE_MISMATCH).
- Pass-3b: 13 cases (role-gate + approve happy path + self-approval 409 + NOT_PENDING + reject + freeze-guard + freeze-release).
- All 6 waste_adjustment_runtime_contract.md §3.3 items closed.

The backend is thorough. The question is whether the portal surface reflects this.

---

### State coverage analysis (from structural knowledge — full source read pending)

| State | Expected behavior | Confirmed? | Finding |
|---|---|---|---|
| Loading | Skeleton blocks; no count chips; no "0 X" | NOT CONFIRMED | A11Y-001 candidate |
| Error (request failed) | One inline error block; actionable; no raw API error | NOT CONFIRMED | A11Y-001 candidate |
| Empty (no items to show — N/A for a form) | Form should always be present for operators | N/A | — |
| Freeze-guard active | "In count freeze" message with guidance | PARTIALLY CONFIRMED (from pgTAP: freeze-guard refusal tested) | NEEDS PORTAL VERIFICATION |
| Pending approval | "Your adjustment is pending approval" | NOT CONFIRMED from portal side | FLOW-005 (from DR-006) |
| Post-submit success | Confirmation with what was posted | NOT CONFIRMED | FLOW-005 continuation |

---

## Accessibility audit — Waste Adjustment

### WCAG checks (structural analysis)

| Check | Status | Finding |
|---|---|---|
| Input labels | UNKNOWN — full source read required | A11Y-001 candidate |
| Tab order / keyboard submission | UNKNOWN | A11Y-002 candidate |
| Submit button accessible name | UNKNOWN (icon-only buttons on forms are common) | A11Y-002 candidate |
| Inline error associated with input | UNKNOWN | A11Y-001 candidate |
| `aria-live` for freeze-guard or approval-pending status | NOT CONFIRMED | A11Y-003 candidate |
| Focus returns after submit | NOT CONFIRMED | A11Y-002 candidate |

---

### Accessibility findings

#### [A11Y-001] Form label and error association — unconfirmed, candidate P1
- **Severity:** P1 candidate (needs full read to confirm or clear)
- **Category:** form labels
- **Description:** Waste Adjustment form likely has fields for item selection, quantity, reason. Whether each field has a programmatic label and whether validation errors are associated with the triggering field via `aria-describedby` is unknown from structural analysis.
- **Proposed fix (if missing):** Add `aria-describedby` linking error messages to their inputs; ensure all inputs have `<label for=...>` or `aria-label`.
- **Acceptance criterion:** Every input on the waste adjustment form has a programmatic label; every validation error is announced when the field is blurred or the form is submitted.
- **Full source read required:** YES.

#### [A11Y-002] Keyboard submission path — unconfirmed
- **Severity:** P0 candidate (blocking if submit is mouse-only)
- **Category:** keyboard navigation
- **Description:** Whether the form submit button is reachable by Tab and activatable by Enter/Space is unknown from structural analysis.
- **Proposed fix (if missing):** Ensure submit button is a native `<button type="submit">` or has `type="submit"` equivalent, is in the Tab order, and responds to keyboard activation.
- **Full source read required:** YES.

#### [A11Y-003] Freeze-guard state announcement
- **Severity:** P1 candidate
- **Category:** screen-reader state announcements
- **Description:** When an item is in a count freeze, the form shows a freeze-guard message. Whether this message is in an `aria-live` region (so screen readers announce it without user navigation) is unknown.
- **Proposed fix:** Freeze-guard message should be in `role="status"` or `aria-live="polite"` region.

---

### Key finding for Tom

The waste adjustment backend is exemplary (33+44+13 pgTAP green; full role matrix verified).
The portal surface's accessibility has not been audited yet. Given the surface is over 3 weeks old
(RUNTIME_READY 2026-04-17), there is meaningful a11y drift risk. Recommend running the full
`/empty-error-state-audit` + a11y audit with a full source read as the next UX sprint task.

---

### Handoff packet

```yaml
handoff_packet:
  surface: /(ops)/stock/waste-adjustments
  audit_date: 2026-05-08
  authored_by: accessibility-usability-auditor
  status: DRAFT — structural analysis only; full source read required
  portal_tip: 9605553
  wcag_level_audited: AA (structural only)
  keyboard_tested: no (static analysis)
  screen_reader_tested: no (static analysis)
  findings:
    - id: A11Y-001
      severity: P1 candidate
      category: form labels
      description: Label and error association unconfirmed
      full_read_required: yes
    - id: A11Y-002
      severity: P0 candidate
      category: keyboard navigation
      description: Keyboard submission path unconfirmed
      full_read_required: yes
    - id: A11Y-003
      severity: P1 candidate
      category: screen-reader state announcements
      description: Freeze-guard message aria-live coverage unconfirmed
```

---

**DRY-RUN STATUS: STRUCTURAL ANALYSIS (full source read required)**
**P0 candidates: 1 (A11Y-002 — keyboard submission; unconfirmed)**
**P1 candidates: 2 (A11Y-001 form labels, A11Y-003 freeze-guard announcement)**
