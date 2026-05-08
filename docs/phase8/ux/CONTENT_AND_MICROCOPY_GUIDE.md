# Content and Microcopy Guide — GT Factory OS Portal

**Owner agent:** `ux-content-state-designer`
**Authoritative status:** DRAFT. Extends portal_ux_standard.md §1 (language) — which is locked.
**Update rule:** New copy rules by ux-content-state-designer; Tom locks each addition.
**Release-gate relevance:** P0 forbidden patterns block ship; P1 jargon is conditional.

---

## What belongs here

- Copy templates and patterns for all operator-facing strings.
- Extension of the standard term lexicon from portal_ux_standard.md.
- Hebrew/English operational clarity rules.
- Jargon removal patterns.

## What must never go here

- Backend enum values or API field names (those belong in backend contracts).
- Visual system rules (→ DESIGN_SYSTEM_RULES.md).
- Interaction mechanics (→ BUTTON_AND_ACTION_RULES.md).

---

## Authority reference

The master copy standard is `gt-factory-os-portal/docs/portal_ux_standard.md` (Gate 4.2, locked).
This document EXTENDS it. On any conflict, portal_ux_standard.md wins.

---

## Standard term lexicon (from portal_ux_standard.md §1)

Use these terms verbatim in all operator-facing UI:

| Concept | Required term | Forbidden alternatives |
|---------|--------------|----------------------|
| The product being produced | `Product` | item, sku, item_id, SKU |
| Quantity intended | `Planned quantity` | qty, planned_qty |
| Quantity actually produced | `Produced quantity` | output_qty, actual qty |
| The day a plan applies to | `Production day` | plan_date, plan day |
| Plan not yet run | `Planned` | open, pending |
| Plan with filed actual | `Completed` | done, finished, closed |
| Plan cancelled | `Cancelled` | dismissed, rejected |
| Plan blocked by missing input | `Blocked` | error, fail |
| Plan likely to slip | `At Risk` | warning, caution |
| Last completed planning run | `Last Planning Run` | latest run, run history tip |
| Last inventory event posted | `Last Inventory Update` | last ledger event |
| Form that posts inventory truth | `Production Report` | production actual, ledger event |
| Action that opens that form | `Open Production Report` | submit actual, run actual |
| Cancel a plan | `Cancel Plan` | dismiss plan, void plan |
| Reason field on cancel | `Reason for Cancellation` | reason_code, cancel_reason |
| Planning recommendation | `Production recommendation` / `Purchase recommendation` | rec, recommendation_id |
| Adding a rec to a plan | `Add from Recommendations` | import rec, attach rec |
| Manual entry path | `Add Manually` | manual create, custom plan |

---

## Extended lexicon (Phase 8 additions — pending Tom lock)

| Concept | Proposed term | Notes |
|---------|--------------|-------|
| Goods receipt record | `Goods Receipt` | Not "GR", not "receipt" alone |
| Posting to stock | `Posted to stock` | Not "committed", "ledgered", "saved" |
| Physical count submitted | `Count submitted` | Not "form submitted" |
| Planning blocker resolved | `Blocker resolved` | Not "dismissed", "closed" |
| Purchase order created | `Purchase order created` | Not "PO created", not "order created" |
| Partial receipt | `Partial receipt` | Not "partial GR", not "partial delivery" |

---

## Forbidden patterns (P0 — block ship if found)

These strings must never appear in operator-facing UI in production:

| Forbidden pattern | Example | Replacement |
|------------------|---------|-------------|
| Raw enum names | `BOUGHT_FINISHED`, `FG_OUT_PICK`, `PLAN_NOT_EDITABLE` | Use display term from status registry |
| Raw UUIDs/internal IDs | `item_id: abc-123` | Show product name |
| Developer language | `mutate`, `dispatch`, `payload`, `handler` | Plain operational verb |
| API path fragments | `/api/v1/mutations/production-plan` | Not shown to operators |
| SQL fragments | `WHERE status IN (...)` | Not shown to operators |
| Raw HTTP codes | `409`, `500`, `403` without context | See error state templates |
| Empty string as label | `""` | Always provide a label |
| `JSON.stringify(body)` | `{"code":"...","message":"..."}` | Parse and display human message |

---

## Hebrew/English rules

**Rule 1:** Operator-facing UI strings are English only. This is locked in CLAUDE.md and portal_ux_standard.md.

**Rule 2:** Hebrew data values (supplier names, item descriptions, contacts) are allowed in data cells.

**Rule 3:** Hebrew strings in UI chrome (buttons, labels, banners, status chips, column headers) are P0 findings unless Tom has explicitly pinned a Hebrew copy register for that surface.

**Rule 4:** Hebrew data values inside LTR layout must be wrapped in `<bdi>` to preserve number/punctuation directionality.

**Rule 5 (known surface):** `/planning/blockers` — Tom has not yet pinned a Hebrew register as of 2026-05-08. Any Hebrew in operator-facing copy on this route is a P0 finding.

---

## Copy style rules

- **Plain and direct.** No "Please", no "Thank you", no passive voice in action labels.
- **Verb-first for buttons.** "Save", "Cancel", "Approve", "Submit".
- **Noun-first for section headings.** "Goods receipts", "Open plans", "Planning blockers".
- **No exclamation marks.** Factory operators are working, not celebrating.
- **No ellipsis (`...`) in status labels.** Use "Loading" or a skeleton, not "Loading...".
- **Numbers:** whole numbers for quantities; commas for thousands (`1,240`); two decimal places for money (`₪12.50`).

---

## Copy review checklist (for ux-content-state-designer)

When auditing any surface:
- [ ] Every button label matches the standard term lexicon.
- [ ] No forbidden patterns are present.
- [ ] Error messages are actionable (tell the operator what to do).
- [ ] Empty states follow the template ("No [thing] yet for this [scope].").
- [ ] Success states name the specific record and next step.
- [ ] No Hebrew in operator-facing chrome (unless Tom-locked register exists).
- [ ] Confirmation dialogs name the specific record being affected.
