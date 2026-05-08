# UX Operating Principles — GT Factory OS

**Owner agent:** `ux-flow-architect` (primary), all five UX agents (co-authors)
**Authoritative status:** DRAFT — not yet locked. Lock requires Tom authorization.
**Created:** 2026-05-08 (Phase 8 Wave 2)
**Update rule:** Any agent may propose additions. Only Tom may lock a principle.
**Release-gate relevance:** All P0 findings that contradict a locked principle block ship.

---

## What belongs here

- System-wide UX doctrine that applies to every GT Factory OS portal surface.
- Principles that arbitrate between UX agent recommendations when they conflict.
- The definition of "production-ready" for UX purposes.

## What must never go here

- Surface-specific rules (those belong in SCREEN_SCORECARDS.md or the relevant audit file).
- Visual token values (those belong in DESIGN_SYSTEM_RULES.md).
- Microcopy strings (those belong in CONTENT_AND_MICROCOPY_GUIDE.md).
- Backend contracts or DB semantics.

---

## Core principles

### P1 — Operational flow is the product

A surface is not done when it renders data. It is done when a factory operator can complete
their task without guessing, waiting for a developer, or opening Excel.

The full operational cycle must be supported on every surface:
> Entry → Processing → Review → Decision → Terminal action → Post-action visibility → Auditability → User confidence

### P2 — Confidence before action

Every irreversible or consequential action must give the operator enough context to act with
confidence. "Are you sure?" is not confidence. "Post 24 units of Detox 1L to stock. This cannot
be undone." is confidence.

### P3 — One primary state at a time

A surface must show exactly one primary state at any moment: loading, error, empty, or loaded.
Mixed states (e.g., showing "0 items" during a load) are always a defect, never a design choice.

### P4 — Actionable failures

Every error message must tell the operator what to do, not just what went wrong. "Contact your
planner" is more valuable than "Error 409".

### P5 — System-level changes, not one-off fixes

Every UX improvement must produce or reference a system rule that prevents the same issue
recurring on other surfaces. One-off fixes without system rules are technical UX debt.

### P6 — English first, Hebrew where Tom-locked

Operator-facing UI is English/LTR. Hebrew appears only in data values and on surfaces where
Tom has explicitly set a Hebrew copy register. This is a hard rule, not a preference.

### P7 — Keyboard-navigable, not keyboard-optional

Every portal action must be completable by keyboard alone. Mouse-only workflows are a
production defect.

### P8 — Post-action is part of the action

A form submission that shows a generic "Success" toast and returns the user to a blank state is
incomplete. The post-action state must tell the operator what was saved, where to find it, and
what to do next.

---

## Definition of production-ready UX

A surface is production-ready when:

1. All P0 findings are resolved (zero DECISION_GRADE issues).
2. The full operational cycle (P1 principle) is covered.
3. Every action has: label, disabled state, loading state, post-action confirmation, and error state.
4. Loading / error / empty / loaded states are correctly implemented.
5. The surface is keyboard-navigable end-to-end.
6. No forbidden copy patterns (raw enums, UUIDs, developer language, raw error codes).
7. The `/ux-release-gate` check returns SHIP or CONDITIONAL_SHIP with named P1 items.

---

## Open questions (to be resolved before locking)

- [ ] Should P2 (confidence before action) require a specific confirmation dialog pattern, or is inline copy sufficient for lower-risk destructive actions?
- [ ] What is the threshold for requiring a reversal path vs. just a strong confirmation?
- [ ] Mobile/tablet breakpoint: is a single-column layout sufficient, or does the portal need a dedicated tablet layout?
