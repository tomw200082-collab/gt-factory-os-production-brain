# Dry-Run DR-011 — /ux-release-gate (full source reads, three P0 candidates)

**Run date:** 2026-05-08
**Command:** `/ux-release-gate --focus flow,interaction,a11y` (full source reads)
**Run type:** Dry-run (read-only; full source reads of three target surfaces)
**Agents invoked:** factory-os-governor (verdict), accessibility-usability-auditor (A11Y-002), ux-flow-architect + ux-content-state-designer (FLOW-003), interaction-design-specialist (INTER-001)
**Portal tip at audit:** `9605553` (window2-portal-sandbox)
**Supersedes:** DR-010 verdict (HOLD pending full source reads — now resolved)

---

## A. Candidate IDs in scope

| ID | Surface | Candidate from |
|----|---------|---------------|
| A11Y-002 | `/(ops)/stock/waste-adjustments` | DR-009 (P0 candidate — keyboard submission) |
| FLOW-003 | `/planning/blockers` | DR-005 (P0 candidate — "contact developer" terminal action) |
| INTER-001 | `/purchase-orders/[po_id]` | DR-008 (P0 candidate — Cancel PO confirmation completeness) |

---

## B. Routes/surfaces audited

| Candidate | Route | File(s) read |
|-----------|-------|--------------|
| A11Y-002 | `/(ops)/stock/waste-adjustments` | `src/app/(ops)/stock/waste-adjustments/page.tsx` (1057 lines, full read) |
| FLOW-003 | `/planning/blockers` | `_lib/labelMaps.ts` (104 lines, full); `_components/BlockerRow.tsx` (lines 100–200); `_components/BlockerCard.tsx` (lines 120–200); `page.tsx` (top-of-file comment) |
| INTER-001 | `/purchase-orders/[po_id]` | `src/app/(po)/purchase-orders/[po_id]/page.tsx` (lines 511–642 cancel mutations; lines 1335–1389 cancel UI; full grep for cancel/confirm patterns across 1390 lines) |

---

## C. Exact source files read

```
C:/Users/tomw2/Projects/window2-portal-sandbox/src/app/(ops)/stock/waste-adjustments/page.tsx
C:/Users/tomw2/Projects/window2-portal-sandbox/src/app/(planning)/planning/blockers/_lib/labelMaps.ts
C:/Users/tomw2/Projects/window2-portal-sandbox/src/app/(planning)/planning/blockers/_components/BlockerRow.tsx
C:/Users/tomw2/Projects/window2-portal-sandbox/src/app/(planning)/planning/blockers/_components/BlockerCard.tsx
C:/Users/tomw2/Projects/window2-portal-sandbox/src/app/(planning)/planning/blockers/page.tsx (header comments only)
C:/Users/tomw2/Projects/window2-portal-sandbox/src/app/(po)/purchase-orders/[po_id]/page.tsx
```

---

## D. Exact UI behavior found

### D.1 — A11Y-002 (waste-adjustments keyboard submission)

| Element | Source location | Behavior |
|---------|----------------|----------|
| Form element | `page.tsx:681` | `<form onSubmit={handleSubmit}>` — native HTML form. Enter on any text input within the form submits. |
| Submit button | `page.tsx:1032-1051` | `<button type="submit">` — native submit button. Tab-reachable; Enter/Space activates. |
| Reset button | `page.tsx:1025-1031` | `<button type="button">` — Tab-reachable; Enter/Space activates. |
| Disabled state | `page.tsx:1038` | `disabled={phase === "submitting" || confirmPending}` — disables during in-flight submit and during confirm panel. |
| Loading state | `page.tsx:1041-1045` | `<IconSpinner /> Submitting…` text. |
| Quantity ± buttons | `page.tsx:827-840, 852-865` | Both have `aria-label="Decrease/Increase quantity by 1"`. Tab-reachable. |
| Combobox | `page.tsx:286-303` | Full keyboard handler: ArrowDown/Up navigate; Enter selects; Escape closes. `aria-autocomplete="list"`, `aria-expanded`, `role="listbox"`, `role="option"`, `aria-selected`. |
| Reason chip group | `page.tsx:904-908` | `role="group" aria-label="Reason code"`. |
| Reason chip buttons | `page.tsx:911-925` | `aria-pressed={reasonCode === r}`. Tab-reachable. |
| Confirm panel (positive direction) | `page.tsx:972-977` | `role="alertdialog" aria-modal="false" aria-label="Confirm positive adjustment"`. Confirm/Cancel buttons inside are Tab-reachable. |
| Result banner | `page.tsx:592, 599` | `role="status"` — implicit `aria-live="polite"`. |
| Loading skeleton | `page.tsx:657` | `aria-busy="true" aria-live="polite"`. |
| Radio buttons (loss/positive) | `page.tsx:701-710, 733-743` | `<input type="radio" className="sr-only">` wrapped in `<label>` — radio is in tab order; arrow keys navigate within radiogroup; the styled card is the visible label. |

**Observation on A11Y-001 (form labels) — separate from A11Y-002 but observed during read:**

| Field | Programmatic label | Status |
|-------|-------------------|--------|
| Event time (datetime-local) | `<label>` wraps `<input>` (page.tsx:780) | OK |
| Item / component combobox | `<span>Item / component *</span>` parent is `<div>`; input has no `aria-labelledby` | **GAP** |
| Quantity | `<span>Quantity *</span>` parent is `<div>`; input has no `aria-labelledby` (page.tsx:822-851) | **GAP** |
| Unit (select) | `<label>` wraps `<select>` (page.tsx:882) | OK |
| Notes (textarea) | `<span>Notes *</span>` parent is `<div>`; textarea has no `aria-labelledby` (page.tsx:937-959) | **GAP** |

Three inputs lack programmatic labels. A11Y-001 is therefore **CONFIRMED P1** (not raised here for resolution; documented for the next a11y sprint).

### D.2 — FLOW-003 (blockers "פנה למפתח")

The Hebrew string "פנה למפתח" appears in **two distinct UI roles** that share the same wording:

**Role 1 — Q4 column ("מה עושים עכשיו?" / "what to do now?") as a CTA value**

- **Source:** `_lib/labelMaps.ts:37` — `check_po_substrate: "פנה למפתח"`
- **Map name:** `FIX_ACTION_LABEL_HE` (line 34)
- **Comment:** `// Tom-locked verbatim 2026-04-27.` (line 33)
- **Trigger:** Backend's planning engine emits `fix_action_label: "check_po_substrate"` for any blocker of subtype `po_substrate_absent_supply_not_netted`.
- **Render location:**
  - `BlockerRow.tsx:144-146` (desktop table, Q4 cell): `<td><div>{fixActionHe}</div></td>` — text "פנה למפתח"
  - `BlockerCard.tsx:147-167` (mobile card, CTA pill): when `fixHref` is null, renders fixActionHe inside a styled `<div>` with sub-line "חסם זה דורש התערבות מפתח/אדמין"

**Role 2 — Q5 column ("איפה מתקנים?" / "where to fix?") as a fallback chip**

- **Source:** `BlockerRow.tsx:163-168`
  ```tsx
  <span
    className="inline-flex items-center gap-1 rounded border border-border/60 bg-bg-subtle px-2 py-1 text-xs text-fg-muted"
    title="חסם זה דורש התערבות מפתח/אדמין"
  >
    פנה למפתח
  </span>
  ```
- **Trigger:** `fix_route` is null on the blocker DTO (no in-app fix URL exists).
- **Page-level comment confirms this is intentional:** `page.tsx:16` — `5. איפה מתקנים? (fix_route link OR "פנה למפתח" when null)`

**Source comments confirm Tom-locked verbatim:**
- `labelMaps.ts:24` — `// Tom-locked verbatim 2026-04-27.` (BLOCKER_LABEL_HE)
- `labelMaps.ts:33` — `// Tom-locked verbatim 2026-04-27.` (FIX_ACTION_LABEL_HE)

**Behavioral interpretation:**
- A planner viewing a `check_po_substrate` blocker sees BOTH cells say "פנה למפתח" (Q4 CTA + Q5 location). There is no in-app action — the planner must contact a developer manually (no email link, no ticket form, no developer name, no expected timeline).
- For other blocker subtypes where `fix_route` is null but `fix_action_label` is operator-actionable (e.g. `configure_supplier`), Q4 shows the action text and Q5 shows the fallback "פנה למפתח" pill. That mixed state is internally inconsistent.

### D.3 — INTER-001 (Cancel PO confirmation)

**Two-step inline confirmation IS implemented:**

| Step | Line | UI |
|------|------|-----|
| Trigger | `page.tsx:1348-1357` | `<button type="button" className="btn btn-ghost btn-sm text-danger-fg hover:bg-danger/10">Cancel PO</button>`. Visible when `canCancelPo` (planner/admin + PO status OPEN/DRAFT). On click: `setCancelConfirming(true)`. |
| Confirm prompt | `page.tsx:1358-1377` | `<span>Cancel this PO?</span>` + `<button className="btn btn-sm bg-danger text-fg-inverted hover:bg-danger/90">Yes, cancel</button>` + `<button className="btn btn-ghost btn-sm">Keep</button>`. |
| Loading state | `page.tsx:1367` | `{cancelMut.isPending ? "Cancelling…" : "Yes, cancel"}` |
| Error surfaced | `page.tsx:540-552, 1345-1346` | Specific server errors mapped to friendly messages: "this PO has posted receipts. Cancel individual open lines first." / "Only OPEN and DRAFT POs can be cancelled." |

**Backend safety (server-side enforcement):**
- Cancel is rejected for PO status not in {OPEN, DRAFT}.
- Cancel is rejected when there are posted receipts.
- These errors are surfaced inline.

**Line-level cancel — SEPARATE flow (page.tsx:919-936):**
- `<span>Cancel line?</span>` + `<button>Yes</button>` + `<button>No</button>`
- Same two-step pattern; even less specific copy ("Yes" / "No").

**Compliance check vs `BUTTON_AND_ACTION_RULES.md` Type D (irreversible) requirements:**

| Requirement | Status |
|-------------|--------|
| Confirmation present | ✅ |
| Trigger button uses danger styling | ⚠️ partial — `btn-ghost` with danger text; not solid danger |
| Confirm button uses destructive solid styling | ✅ `bg-danger text-fg-inverted` |
| Easy escape (Cancel/Keep) | ✅ "Keep" button |
| Loading state on confirm | ✅ "Cancelling…" |
| Error state surfaced inline | ✅ |
| Confirmation prompt **names the entity** (PO number / order_number) | ❌ "Cancel this PO?" is generic |
| Confirmation **mentions consequences** (open lines won't be received; receipts retained, etc.) | ❌ |
| Confirmation **mentions irreversibility** ("This cannot be undone") | ❌ |

---

## E. Confirmed P0 / cleared / downgraded

| ID | Verdict | Reason |
|----|---------|--------|
| **A11Y-002** | **CLEARED** | Submit is `<button type="submit">` inside `<form onSubmit>`. Native HTML form behavior covers keyboard submission. Tab-reachable. Enter on any text input submits. Disabled state correctly blocks during in-flight. No defect. |
| **FLOW-003** | **CONFIRMED P0** (Role 1 only — `check_po_substrate` CTA). Role 2 (Q5 fallback chip) is **DOWNGRADED to P1**. | Role 1 is a CTA value — it makes "contact a developer" the planner's primary daily action for an entire blocker subtype, with no in-app path to actually do it. Role 2 is honest fallback labelling and is internally consistent with the "no fix_route" state; it's a polish item, not a P0. Both strings are Tom-locked verbatim per `labelMaps.ts:33`, so any change requires Tom approval. |
| **INTER-001** | **DOWNGRADED to P1 (confirmed)** | Confirmation IS present (two-step inline). Server-side guards exist for irreversibility-with-side-effects. Confirm button uses destructive styling. Did not meet P0 bar of "irreversible action with NO confirmation". Remaining gaps (PO number not named in prompt; consequences not stated; irreversibility not stated) are P1 polish. Trigger button styling using `btn-ghost` instead of solid danger is a minor inconsistency. |

**Confirmed P0 count after full reads: 1 (FLOW-003 Role 1 only).**
**Cleared P0 candidates: 1 (A11Y-002).**
**Downgraded to P1: 2 (INTER-001, FLOW-003 Role 2).**

---

## F. Evidence

### F.1 — A11Y-002 evidence

```tsx
// page.tsx:681
<form onSubmit={handleSubmit} className="space-y-5 pb-24">

// page.tsx:1032-1051
<button
  type="submit"
  className={cn(
    "btn btn-primary transition-colors duration-150",
    phase === "submitting" && "cursor-wait"
  )}
  disabled={phase === "submitting" || confirmPending}
  data-testid="waste-submit"
>
  {phase === "submitting" ? (
    <span className="flex items-center gap-2">
      <IconSpinner />
      Submitting…
    </span>
  ) : direction === "positive" ? (
    "Review & submit"
  ) : (
    "Submit adjustment"
  )}
</button>
```

### F.2 — FLOW-003 evidence (Role 1 — CTA)

```ts
// _lib/labelMaps.ts:32-39
// fix_action_label (English key → Hebrew CTA copy)
// Tom-locked verbatim 2026-04-27.
export const FIX_ACTION_LABEL_HE: Record<FixActionLabelKey, string> = {
  configure_supplier: "הגדר ספק",
  configure_bom: "הגדר BOM",
  check_po_substrate: "פנה למפתח",
  review_trigger_threshold: "בדוק סף הפעלה",
};
```

```tsx
// _components/BlockerRow.tsx:143-146
{/* Q4 — מה עושים עכשיו? */}
<td className="px-3 py-3">
  <div className="text-xs text-fg">{fixActionHe}</div>
</td>
```

### F.3 — FLOW-003 evidence (Role 2 — Q5 fallback)

```tsx
// _components/BlockerRow.tsx:148-170
{/* Q5 — איפה מתקנים? */}
<td className="px-3 py-3">
  {fixHref ? (
    <Link href={fixHref} ...>
      <Wrench /> לתיקון <ExternalLink />
    </Link>
  ) : (
    <span
      className="inline-flex items-center gap-1 rounded border border-border/60 bg-bg-subtle px-2 py-1 text-xs text-fg-muted"
      title="חסם זה דורש התערבות מפתח/אדמין"
    >
      פנה למפתח
    </span>
  )}
</td>
```

### F.4 — INTER-001 evidence

```tsx
// page.tsx:1348-1377
{canCancelPo && !cancelConfirming && (
  <button
    type="button"
    className="btn btn-ghost btn-sm text-danger-fg hover:bg-danger/10"
    onClick={() => { setCancelConfirming(true); setCancelError(null); }}
    disabled={cancelMut.isPending}
  >
    Cancel PO
  </button>
)}
{canCancelPo && cancelConfirming && (
  <div className="flex items-center gap-1.5">
    <span className="text-xs text-fg-muted">Cancel this PO?</span>
    <button
      type="button"
      className="btn btn-sm bg-danger text-fg-inverted hover:bg-danger/90"
      onClick={() => cancelMut.mutate()}
      disabled={cancelMut.isPending}
    >
      {cancelMut.isPending ? "Cancelling…" : "Yes, cancel"}
    </button>
    <button
      type="button"
      className="btn btn-ghost btn-sm"
      onClick={() => { setCancelConfirming(false); setCancelError(null); }}
      disabled={cancelMut.isPending}
    >
      Keep
    </button>
  </div>
)}
```

---

## G. Recommendations

### G.1 — A11Y-002

**No action required.** Cleared. The form is fully keyboard-accessible. (A11Y-001 form labels gap is documented separately for the next a11y sprint — three inputs need `aria-labelledby` or proper `<label>` wrap.)

### G.2 — FLOW-003 (CONFIRMED P0; Tom decision required)

**This is the most direct operator-facing defect found in the Wave 2 audit.** A planner viewing a `check_po_substrate` blocker has no in-app path to act. The CTA is "פנה למפתח" with no developer name, mailto link, or ticket form. The blocker stays in the queue indefinitely.

**Do not change copy without Tom approval.** Both strings are Tom-locked verbatim per `labelMaps.ts:24, 33`.

**Recommended alternatives — for Tom decision:**

**Option A — Replace CTA with a self-service ticket action (preferred)**
Convert the `check_po_substrate` row to a clickable CTA that opens a pre-filled ticket form (Linear / GitHub / mailto / internal `/admin/dev-tickets`). Hebrew alternatives for the button label:
- `דווח באג` ("report bug")
- `פתח כרטיס לדב` ("open ticket to dev")
- `שלח דיווח` ("send report")

The ticket would carry the blocker context: `exception_id`, `blocker_label`, `display_name` (item or component name), `demand_qty`, `earliest_shortage_at`, current planning_run_id.

This requires backend work (a `dev-tickets` endpoint or mailto template) — not a portal-only change. Owner: `backend-db-executor` + `portal-production-executor` after the endpoint exists.

**Option B — Investigate and remove the blocker class (most thorough)**
`check_po_substrate` exists because the planning engine cannot answer some question about open POs for this blocker. If the engine logic can be fixed so that the substrate is checkable in-app, this entire blocker subtype goes away. Owner: planning engine work — out of UX scope but the right architectural answer.

**Option C — Accept and document (least disruptive)**
Leave "פנה למפתח" as the CTA, but document under what conditions it appears, who the developer is, and what info to send. This means a runbook entry, not a copy change. Hebrew alternative for the CTA could optionally be tightened to e.g. `שלח לדב את ID החסם` ("send the blocker ID to a dev") — slightly more actionable.

**Recommended: Option A.**
**Stand-by: Option C** as an interim until Option A's backend work lands.

### G.3 — FLOW-003 Role 2 (Q5 fallback chip — P1)

Acceptable as-is. The wording is appropriate for the "where" column when `fix_route` is null. Could optionally be tightened in a future sprint to a one-click ticket action (consistency with Option A above), but no urgency.

### G.4 — INTER-001 (P1 confirmed; Tom decision optional)

Cancel PO confirmation is implemented but lean. Recommended polish (not P0):

1. **Name the entity in the prompt:** Change `"Cancel this PO?"` to `"Cancel PO ${po.order_number ?? po.po_id}?"`.
2. **State the consequences in the prompt:** Add `"Open lines won't be received."` (only when `po.status === "OPEN"`).
3. **State irreversibility:** Add `"This cannot be undone."`
4. **Tighten trigger styling:** Replace `btn-ghost` trigger with a true destructive variant (`btn-danger` or shadcn `variant="destructive"`) — current `btn-ghost text-danger-fg` is under-emphasized for an irreversible action.
5. **Same fixes for line cancel** (`page.tsx:919-936`): name the line ("Cancel line: ${line.component_name}?"); state consequence; replace generic Yes/No with "Yes, cancel" / "Keep".

These are P1 — not blocking, but low-effort to do once and they remove a real Tom-Tax friction point. Owner: `portal-production-executor` after Tom approves the prompt copy.

---

## H. Tom decision required

| ID | Tom decision required | What to decide |
|----|----------------------|----------------|
| A11Y-002 | NO | Cleared. |
| FLOW-003 (Role 1 P0) | **YES** | Choose Option A / B / C above. If Option A, also approve Hebrew CTA wording. |
| FLOW-003 (Role 2 P1) | NO | Acceptable as-is; defer. |
| INTER-001 (P1) | OPTIONAL | Approve polish copy ("Cancel PO PO-12345? Open lines won't be received. This cannot be undone.") and trigger variant change. Or defer. |
| A11Y-001 (P1, observed during read) | NO (defer) | Three inputs need programmatic labels. Schedule for next a11y sprint. |
| FLOW-007 (P1, confirmed during INTER-001 read) | NO (defer) | "View receipts" link shows on CANCELLED POs (page.tsx:1336) where there are no receipts. Document for next portal sprint. |

---

## I. Updated UX release gate verdict

### I.1 — Wave 2 scope per-dimension status

| Dimension | P0 confirmed | P0 candidates remaining | P1 candidates | Status |
|---|---|---|---|---|
| Flow | 1 (FLOW-003 Role 1) | 0 | 7 | **RED — confirmed P0** |
| Interaction | 0 | 0 | 2 (INTER-001, INTER-002) | AMBER |
| Visual | 0 | 0 | 0 | NOT_AUDITED |
| Copy | 0 | 0 | 0 | (Hebrew register Tom-locked; FLOW-003 copy decision required) |
| Accessibility | 0 | 0 | 4 (A11Y-001 ×3 inputs, A11Y-003) | AMBER |

### I.2 — Verdict

**HOLD — confirmed P0 (FLOW-003 Role 1).**

This is no longer a "structural-analysis HOLD" (DR-010). It is a **confirmed P0 defect HOLD**. The threshold per `UX_RELEASE_GATE.md`: any confirmed P0 → HOLD.

Three of the four DR-010 candidates resolved cleanly:
- A11Y-002: cleared.
- INTER-001: downgraded to P1.
- FLOW-003 Role 2: downgraded to P1.

The remaining defect (FLOW-003 Role 1) requires:
1. Tom decision on Option A / B / C (Section G.2).
2. If Option A: backend ticket endpoint + portal CTA wiring + Tom-approved Hebrew copy.
3. Re-run `/ux-release-gate` after fix lands.

**The gate cannot issue SHIP or CONDITIONAL_SHIP for the Wave 2 scope until FLOW-003 is resolved.**

### I.3 — What CAN ship now (per-surface)

| Surface | Verdict |
|---------|---------|
| `/(ops)/stock/waste-adjustments` | **CONDITIONAL_SHIP** (zero P0; A11Y-001 P1 documented) |
| `/(ops)/stock/receipts` | **CONDITIONAL_SHIP** (zero P0; FLOW-001/002/007 P1s documented — pending full read) |
| `/(ops)/stock/physical-count` | NOT_AUDITED at source level (DR-006 was structural only) |
| `/purchase-orders/[po_id]` | **CONDITIONAL_SHIP** (zero P0; INTER-001 + INTER-002 + FLOW-007 P1s documented) |
| `/planning/blockers` | **HOLD** (FLOW-003 Role 1 confirmed P0) |

### I.4 — Aggregate verdict

**HOLD** — driven by `/planning/blockers` only. All other Wave 2 surfaces would issue CONDITIONAL_SHIP individually.

---

**END OF DR-011. Tom decision required on FLOW-003 Option A/B/C before re-running the gate.**
