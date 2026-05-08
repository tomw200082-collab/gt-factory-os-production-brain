# Accessibility Checklist — GT Factory OS Portal

**Owner agent:** `accessibility-usability-auditor`
**Authoritative status:** DRAFT. Based on WCAG 2.1 Level AA.
**Update rule:** Additions by accessibility-usability-auditor; Tom authorization to lock.
**Release-gate relevance:** P0 a11y findings block ship via /ux-release-gate.

---

## What belongs here

- Per-category accessibility checklists for portal surface audits.
- Severity model aligned to portal_language_direction_audit.md.
- Known a11y patterns and violations specific to this portal.

## What must never go here

- Microcopy or copy strings (→ CONTENT_AND_MICROCOPY_GUIDE.md).
- Visual contrast token values (→ DESIGN_SYSTEM_RULES.md — tokens; `accessibility-usability-auditor` identifies the issue, `visual-system-designer` proposes the token fix).
- Backend contracts or DB semantics.

---

## Severity model (aligned to portal_language_direction_audit.md)

| Severity | Meaning | Ship gate |
|----------|---------|-----------|
| P0 | Blocks a user from completing a core task by keyboard or screen reader | Block ship |
| P1 | Significant friction; workaround exists but is painful | Conditional ship; fix next sprint |
| P2 | Affects some users; easy workaround | Backlog |
| P3 | Minor polish; WCAG AA edge case | Nice to have |

---

## Checklist by category

### 1. Contrast (WCAG 1.4.3 / 1.4.11)

- [ ] Normal text (< 18px, not bold): 4.5:1 minimum against background.
- [ ] Large text (≥ 18px or ≥ 14px bold): 3:1 minimum.
- [ ] UI components (input borders, focus rings, button borders): 3:1 against adjacent color.
- [ ] Status colors (green/amber/red chips): do not rely on color alone; always paired with a label.
- [ ] Dark mode: same contrast ratios apply in dark theme.

**Audit method:** Use browser DevTools color picker or axe DevTools extension.
**Escalation:** Contrast fixes require `visual-system-designer` to propose token changes.

---

### 2. Focus order and keyboard navigation (WCAG 2.1.1 / 2.4.3)

- [ ] All interactive elements reachable by Tab in logical reading order.
- [ ] Focus order matches visual order (no DOM-order surprises).
- [ ] No focus traps except modal dialogs (and those escape via Escape key).
- [ ] Focus visible on all elements (`:focus-visible` ring present; no bare `outline: none`).
- [ ] Modal dialogs: focus moves to dialog on open; returns to trigger on close.
- [ ] Dropdown menus navigable by arrow keys; Enter/Space to select; Escape to dismiss.
- [ ] Date pickers fully keyboard-navigable.
- [ ] All forms submittable by keyboard without mouse.
- [ ] Destructive confirm dialogs reachable and dismissable by keyboard.

**P0 examples:**
- Submit button only clickable by mouse.
- Modal that cannot be closed by keyboard.
- Focus disappears after a form submission (user lost in the DOM).

---

### 3. Form labels and inputs (WCAG 1.3.1 / 3.3.2)

- [ ] Every input has a programmatic label: `<label for=...>`, `aria-label`, or `aria-labelledby`.
- [ ] Placeholder text is not the sole label (placeholders disappear on typing).
- [ ] Helper text associated with input: `aria-describedby`.
- [ ] Error messages associated with the triggering input: `aria-describedby`.
- [ ] Required fields: `aria-required="true"` or native `required` attribute.
- [ ] Required fields also marked visually (asterisk + legend).
- [ ] Date pickers, comboboxes, custom selects: correct ARIA role and name.
- [ ] File inputs: accessible label and feedback on file selected.

**P0 examples:**
- Input field with no label of any kind.
- Error message shown visually but not associated with the input via ARIA.

---

### 4. ARIA name-role-value (WCAG 4.1.2)

- [ ] All icon-only buttons: `aria-label` describing the action (not the icon name).
- [ ] Disclosure/expand buttons: `aria-expanded` reflects open/closed state.
- [ ] Tab panels: `role="tablist"`, `role="tab"`, `role="tabpanel"` with `aria-selected` and `aria-controls`.
- [ ] Modal dialogs: `role="dialog"`, `aria-modal="true"`, `aria-labelledby` pointing to the dialog title.
- [ ] Comboboxes/autocomplete: `role="combobox"` with `aria-expanded` and `aria-autocomplete`.
- [ ] Status chips and badges: if purely decorative, `aria-hidden="true"`. If informative, must have text or `aria-label`.
- [ ] `aria-hidden="true"` never applied to interactive elements or their ancestors.
- [ ] `aria-live` regions for: toast messages, inline errors, loading completions, status updates.

**P0 examples:**
- Icon-only button with no accessible name (e.g., hamburger menu, close button, delete icon button).
- Dialog with no label, so screen reader announces blank modal.

---

### 5. Screen-reader state announcements (WCAG 4.1.3)

- [ ] Route changes announce new page (via document.title change and/or a skip-to-main heading change).
- [ ] Form submission success: announced via `aria-live="polite"` region (toast alone is insufficient if the toast is outside the live region).
- [ ] Inline errors: announced without requiring the user to tab to the error field.
- [ ] Loading state: "Loading..." announced (can be via `aria-busy="true"` on the container).
- [ ] Filter/search results change: total count announced (e.g., "24 results").
- [ ] Count updates in tables after mutation: announced.

---

### 6. Usability friction (beyond WCAG)

These are P1/P2 usability findings, not strict WCAG violations:

- [ ] Most common task completable in < 30 seconds without a mouse.
- [ ] No single-misclick path to a destructive action (confirmation is required, or action is at least 2 clicks away).
- [ ] Recovery from a mistake is possible without leaving the current page.
- [ ] Long forms can be saved mid-way (or the cost of losing progress is clearly stated).
- [ ] Status of background processes (planning run, count approval) is visible without a manual refresh.

---

## Known portal a11y debt (as of Phase 8 Wave 2, 2026-05-08)

These are flagged for audit but not yet confirmed as violations:

| Surface | Suspected issue | Priority |
|---------|----------------|---------|
| `/planning/blockers` | Hebrew strings in operator-facing labels may not be properly wrapped in `<bdi>` | P0 candidate |
| All forms | Icon-only action buttons (delete, edit, expand) likely missing `aria-label` | P1 candidate |
| Toast notifications | May not be in `aria-live` region | P1 candidate |
| Modal dialogs | Need to verify focus management on open/close | P1 candidate |
| Status chips | Color-only status without text label on mobile view | P1 candidate |

**These must be confirmed by running `/empty-error-state-audit` or `/ux-release-gate` on the relevant surfaces.**
