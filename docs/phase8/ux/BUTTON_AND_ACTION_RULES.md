# Button and Action Rules — GT Factory OS Portal

**Owner agent:** `interaction-design-specialist`
**Authoritative status:** DRAFT — not yet locked.
**Update rule:** Updates require `interaction-design-specialist` finding + Tom authorization.
**Release-gate relevance:** Missing states on irreversible actions = P0; blocks ship.

---

## What belongs here

- System-wide rules for buttons, actions, and confirmations.
- The required state checklist for every action type.
- Destructive and irreversible action patterns.

## What must never go here

- Copy strings (→ CONTENT_AND_MICROCOPY_GUIDE.md).
- Accessibility rules for button focus/keyboard (→ ACCESSIBILITY_CHECKLIST.md).
- Visual token values (→ DESIGN_SYSTEM_RULES.md).

---

## Required states for every action

Every button or actionable link must have all of the following defined:

| State | Required | Notes |
|-------|---------|-------|
| Default label | YES | Plain operational English; see CONTENT_AND_MICROCOPY_GUIDE.md |
| Disabled condition | YES | When is the button disabled? What visible indicator? |
| Loading state | YES | Spinner + label change; button locked during submission |
| Destructive marking | YES | `variant="destructive"` if action deletes or cannot be undone |
| Irreversibility declaration | YES (if irreversible) | Stated in confirmation copy, not just visually |
| Post-action confirmation | YES | Toast + state change + next step pointer |
| Error state | YES | Actionable error message; inline or toast |

---

## Action type classification

### Type A — Additive (low risk)
Adding a line, creating a draft, opening a form.
- Disabled state: required.
- Confirmation: optional.
- Post-action: brief success toast.

### Type B — Mutating (medium risk)
Saving a form, updating a plan, approving a recommendation.
- Disabled state: required.
- Loading state: required.
- Post-action: toast + state change indicating what was saved.

### Type C — Consequential (high risk)
Posting to stock ledger, publishing a forecast, closing a PO.
- Confirmation dialog: REQUIRED. Must name the record and state the effect.
- Disabled state: required.
- Loading state: required.
- Post-action: clear confirmation of what was posted/published/closed + link to audit trail.

### Type D — Irreversible (highest risk)
Actions that cannot be undone: anchor creation, ledger posting, plan cancellation.
- Confirmation dialog: REQUIRED. Must explicitly state "This cannot be undone."
- Irreversibility warning: must appear BEFORE the confirm button, not after.
- Destructive styling: `variant="destructive"` on the confirm button.
- Post-action: clear record of what was done + reversal instructions if applicable.

---

## Confirmation dialog pattern

```
Title: <Verb + record name>
  Example: "Cancel Plan — Detox 1L, May 8"

Body: <What will happen> + <Impact> + <Irreversibility if applicable>
  Example: "This plan will be cancelled. Stock will not be decremented.
             This action cannot be undone. A cancellation event will be logged."

Actions:
  [Cancel this plan] (variant="destructive")   [Keep plan] (variant="secondary")

Note: "Cancel this plan" is the confirm; "Keep plan" is the dismiss.
Primary action is always on the RIGHT. Cancel/dismiss is on the LEFT.
```

---

## Button placement rules

- Primary action: **right-aligned** in the action bar or dialog footer.
- Secondary action: **left of primary**.
- Destructive confirm: **right**, `variant="destructive"`.
- Cancel/dismiss: **left**, `variant="secondary"` or `variant="ghost"`.
- Icon-only buttons: must have `aria-label` or visible tooltip.

---

## Forbidden patterns

- Auto-confirm on Enter key without explicit user intent.
- Generic "Are you sure?" without naming the record.
- "OK" as a confirmation button label.
- Destructive action with default variant (no visual distinction).
- Submit button that does not lock during submission (double-submit risk).
- Cancel button that discards unsaved work without a warning.

---

## Open questions

- [ ] Should "Approve" and "Reject" on counting workflows be Type C or Type D? (Approve creates an anchor — effectively irreversible.)
- [ ] PO line deletion: is this Type C or Type D? (PO lines can be re-added manually.)
