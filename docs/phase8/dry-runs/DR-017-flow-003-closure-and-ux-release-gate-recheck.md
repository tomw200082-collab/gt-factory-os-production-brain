# Dry-Run DR-017 — FLOW-003 closure and UX release gate recheck

**Run date:** 2026-05-08
**Run mode:** Source-read recheck after FLOW-003 implementation. No browser, no Playwright,
no production deploy.
**Portal commit audited:** `9e2212e` (window2-portal-sandbox; on top of `9605553`).
**FLOW-003 implementation commit:** `9e2212e feat(planning/blockers): FLOW-003 closure —
actionable in-app ticket CTA`
**Supersedes verdict from:** DR-011 §E (FLOW-003 Role 1 = CONFIRMED P0).
**Authority:** factory-os-governor (verdict) + ux-flow-architect + ux-content-state-designer
+ accessibility-usability-auditor (joint, read-only).

---

## A. Scope

DR-017 answers four questions:

1. Is FLOW-003 closed, still HOLD, or CONDITIONAL?
2. Did `/planning/blockers` move out of HOLD?
3. Did the aggregate UX release gate change?
4. What evidence supports the verdict?

---

## B. Files inspected on portal commit `9e2212e`

| File | Path | Read scope |
|------|------|-----------|
| `_lib/labelMaps.ts` | `src/app/(planning)/planning/blockers/_lib/labelMaps.ts` | full file (107 lines) |
| `_lib/devTicketContent.ts` | `src/app/(planning)/planning/blockers/_lib/devTicketContent.ts` | full file (71 lines) — new |
| `_components/BlockerRow.tsx` | `src/app/(planning)/planning/blockers/_components/BlockerRow.tsx` | full file (282 lines) |
| `_components/BlockerCard.tsx` | `src/app/(planning)/planning/blockers/_components/BlockerCard.tsx` | full file (276 lines) |
| `_components/DevTicketModal.tsx` | `src/app/(planning)/planning/blockers/_components/DevTicketModal.tsx` | full file (162 lines) — new |
| `page.tsx` | `src/app/(planning)/planning/blockers/page.tsx` | header (lines 1–80); not modified |
| `_lib/types.ts` | `src/app/(planning)/planning/blockers/_lib/types.ts` | DTO shape confirmed; not modified |

---

## C. Behavior on commit `9e2212e` — Q4 cell for `check_po_substrate`

### C.1 — Source

`labelMaps.ts:41`:

```ts
check_po_substrate: "פתח כרטיס טיפול",
```

`BlockerRow.tsx:148-167` (Q4 cell):

```tsx
<td className="px-3 py-3">
  {isDevEscalation ? (
    <>
      <button
        type="button"
        onClick={() => setDevTicketOpen(true)}
        className="inline-flex items-center gap-1 rounded border border-accent/40 bg-accent-soft px-2 py-1 text-xs font-medium text-accent-fg hover:bg-accent-softer transition-colors"
        data-testid={`blockers-dev-ticket-trigger-${row.exception_id}`}
      >
        <LifeBuoy className="h-3 w-3" strokeWidth={2} aria-hidden />
        {fixActionHe}
      </button>
      <DevTicketModal
        row={row}
        open={devTicketOpen}
        onClose={() => setDevTicketOpen(false)}
      />
    </>
  ) : (
    <div className="text-xs text-fg">{fixActionHe}</div>
  )}
</td>
```

`isDevEscalation` is derived at line 70: `row.fix_action_label === "check_po_substrate"`.

### C.2 — Resolved behavior

| Aspect | Behavior |
|--------|---------|
| Visible CTA copy | `"פתח כרטיס טיפול"` (Tom-approved primary CTA, Phase 8 Run C) |
| Element type | `<button type="button">` |
| Tab-reachable | yes — native button is in tab order |
| Keyboard activation | Enter / Space (native button behavior) |
| Pointer activation | click |
| Screen reader role | implicit `button` |
| Visual affordance | accent-soft border + LifeBuoy icon — matches the approved Q5 fix-link styling |
| Modal mount | local to row — opens only when triggered |

The dead-text `<div>` is removed for `check_po_substrate` rows. Other subtypes
(`configure_supplier`, `configure_bom`, `review_trigger_threshold`) continue to render the
plain `<div>` in Q4 because their fix paths are still served by the `fix_route` link in Q5.

---

## D. Behavior on commit `9e2212e` — DevTicketModal

### D.1 — Modal contract

`DevTicketModal.tsx` lines 79–161:

| Aspect | Behavior |
|--------|---------|
| `role` | `dialog` |
| `aria-modal` | `"true"` |
| `aria-labelledby` | points to the title `<h2>` |
| `aria-describedby` | points to the lead `<p>` |
| `dir` | `rtl` |
| Backdrop | `bg-bg-strong/40` covering viewport; click-outside closes |
| Stop propagation | clicks inside the dialog do not close it (line 91) |
| ESC closes | `keydown` listener on window (lines 35–43) |
| Focus management | initial focus to Close button on open (line 33); focus restoration on close (line 41) |
| Body scroll | dialog content has `max-h-[60vh] overflow-auto` so long payloads remain reachable |

### D.2 — Lead description (Tom-approved interim copy)

Line 96–101:

```tsx
<p
  id={`dev-ticket-lead-${row.exception_id}`}
  className="mt-0.5 text-xs text-fg-muted"
>
  שלח לצוות הפיתוח את ID החסם
</p>
```

### D.3 — Context payload rendered in dialog body

Lines 113–149 — `<dl>` grid with 9 row-pairs:

| Field | Source |
|-------|--------|
| מזהה חסם | `row.exception_id` |
| תת-סוג | `row.category` |
| ישות מושפעת | `row.display_name (row.display_kind)` |
| הודעה | `row.blocker_label` |
| ביקוש חסום | `row.demand_qty` (conditional) |
| חוסר ראשון | `row.earliest_shortage_at` (conditional) |
| חומרה | `row.severity` |
| נוצר בזמן | `row.emitted_at` |
| ריצת תכנון | `row.run_id` |
| מסך מקור | `/planning/blockers` (literal) |

This satisfies the user's required minimum context per Run C §A: blocker id ✓, subtype ✓,
affected PO/item/planning entity ✓, current message ✓, timestamp ✓, source screen ✓.

### D.4 — Action buttons

Lines 151–172:

| Action | Behavior |
|--------|---------|
| `"העתק לטיפול"` | `navigator.clipboard.writeText(payload.body)` (lines 49–55). Always rendered. On success, button text flips to `"הועתק"` and styling switches to `bg-success-soft`. |
| `"שלח דואר לצוות פיתוח"` | `<a href="mailto:...">` (lines 165–171). Rendered only when `DEV_TEAM_EMAIL !== ""`. Currently `DEV_TEAM_EMAIL = ""` (empty default), so this button is suppressed until Tom configures the alias. |
| `"סגור"` (X icon) | Closes dialog (lines 102–110). |

When `DEV_TEAM_EMAIL` is empty, the modal footer renders an inline note:
`"ערוץ שליחה לצוות פיתוח לא הוגדר עדיין — השתמש בהעתקה."` (lines 153–157). This is a
courtesy line; the copy action is fully functional regardless.

---

## E. Behavior on commit `9e2212e` — BlockerCard (mobile)

`BlockerCard.tsx:159-181` mirrors the row treatment. The fallback `<div>` block (when
`fixHref` is null) becomes a clickable `<button>` for `check_po_substrate`, with a
sub-line `"שלח לצוות הפיתוח את ID החסם"` (Tom-approved interim copy). The same
`DevTicketModal` mounts on demand.

For non-`check_po_substrate` rows, the fallback `<div>` is unchanged (text
`"חסם זה דורש התערבות מפתח/אדמין"` remains; `fixActionHe` for those subtypes is the
correct CTA per their respective fix routes).

---

## F. Q5 fallback chip — DELIBERATELY UNCHANGED in this run

`BlockerRow.tsx:188-195`: the Q5 fallback `<span>` chip still renders `"פנה למפתח"` when
`fix_route` is null.

**Status:** unchanged — and that is correct for Run C scope.

DR-011 §E classified this as P1 (Role 2 fallback chip; downgraded from P0 candidate). Run C
prompt §C explicitly forbids "unrelated UX cleanup, unrelated copy changes." The Q5 chip
is generic fallback labelling for the location column ("where to fix this is outside the
app"), which is operationally honest for any subtype with `fix_route = null`. It is a P1
polish item, not a workflow defect.

For `check_po_substrate` rows specifically, a planner now sees:
- Q4: `"פתח כרטיס טיפול"` — clickable button (action)
- Q5: `"פנה למפתח"` — non-clickable chip (location indicator)

This is mildly inconsistent but does not reintroduce the FLOW-003 P0 — the planner has an
in-app action via Q4. The Q5 chip can be tightened in a future P1 sweep.

---

## G. Verdict — Question 1: FLOW-003 status

**FLOW-003 P0 is CLOSED.**

Evidence:
1. The Q4 dead-text `<div>` for `check_po_substrate` no longer exists (replaced by a
   tab-reachable `<button>` with `data-testid="blockers-dev-ticket-trigger-{exception_id}"`).
2. The `<button>` opens a real, accessible modal (`role="dialog" aria-modal="true"`) with
   blocker context auto-populated.
3. The planner can act in-app via clipboard copy, even with the dev-team email alias
   un-configured. Once `DEV_TEAM_EMAIL` is set, the mailto: action also becomes available.
4. The audience scope (planner + admin only) is preserved — no operator exposure introduced.
5. CLAUDE.md non-negotiable #2 ("simple operator workflows") is now satisfied for this
   subtype: the workflow has a terminal action, not a terminal "contact developer" string.
6. The Tom-approved decision in the FLOW-003 decision packet (A-with-C-interim) is
   implemented: Option A's in-app ticket CTA is the active CTA; Option C's interim copy
   ("שלח לצוות הפיתוח את ID החסם") is the descriptive lead text in the modal and the
   mobile sub-line.

There is no residual P0 condition.

---

## H. Verdict — Question 2: did `/planning/blockers` move out of HOLD?

**Yes. `/planning/blockers` moves from HOLD → CONDITIONAL_SHIP.**

Per `PRODUCTION/docs/phase8/ux/UX_RELEASE_GATE.md` framing:

| Surface | Verdict before Run C | Verdict after Run C | Reason |
|---------|---------------------|---------------------|--------|
| `/planning/blockers` | **HOLD** (FLOW-003 confirmed P0) | **CONDITIONAL_SHIP** | P0 closed; remaining items are P1 polish (Q5 chip, optional dev-team email alias configuration) |

CONDITIONAL_SHIP rather than CLEAN_SHIP because:
- The Q5 fallback chip is still P1 (intentionally deferred per Run C scope).
- `DEV_TEAM_EMAIL` is empty — the mailto: action is suppressed until Tom configures the
  team alias. Clipboard copy remains the universal action; this is acceptable v1 but
  warrants a Tom follow-up.

Both items are documented in §K.

---

## I. Verdict — Question 3: did the aggregate UX release gate change?

**Yes. Aggregate verdict moves from HOLD → CONDITIONAL_SHIP.**

Updated per-surface table:

| Surface | Pre-Run-C | Post-Run-C | Trend |
|---------|-----------|------------|-------|
| `/(ops)/stock/waste-adjustments` | CONDITIONAL_SHIP | CONDITIONAL_SHIP | unchanged |
| `/(ops)/stock/goods-receipt` | CONDITIONAL_SHIP | CONDITIONAL_SHIP | unchanged |
| `/(po)/purchase-orders/[po_id]` | CONDITIONAL_SHIP | CONDITIONAL_SHIP | unchanged |
| `/planning/blockers` | **HOLD** | **CONDITIONAL_SHIP** | **moved out of HOLD** |
| `/(ops)/stock/physical-count` | NOT_AUDITED | NOT_AUDITED | unchanged |

Aggregate verdict:
- Pre-Run-C: **HOLD** (driven entirely by FLOW-003 P0 on `/planning/blockers`).
- Post-Run-C: **CONDITIONAL_SHIP** (no P0 remains; CONDITIONAL is the correct framing
  while P1 polish items, NOT_AUDITED surfaces, and Tom-only follow-ups remain).

Not yet **SHIP** because:
- Physical count surface still NOT_AUDITED at source level.
- Multiple surfaces carry P1 polish items (INTER-001 confirmed P1, A11Y-001 form-label gap,
  Q5 fallback chip).
- `DEV_TEAM_EMAIL` not yet configured.

---

## J. Verdict — Question 4: evidence summary

| Item | Evidence path | Status |
|------|--------------|--------|
| Old dead-text mapping removed | `_lib/labelMaps.ts:41` reads `"פתח כרטיס טיפול"` | ✓ |
| New CTA renders as `<button>` (desktop) | `_components/BlockerRow.tsx:151-167` | ✓ |
| New CTA renders as `<button>` (mobile) | `_components/BlockerCard.tsx:162-181` | ✓ |
| Modal contract a11y-correct | `_components/DevTicketModal.tsx:79-95` (role/aria-modal/labelledby/describedby/ESC/focus) | ✓ |
| Tom-approved interim copy present | `_components/DevTicketModal.tsx:99` and `_components/BlockerCard.tsx:174` | ✓ |
| Required context fields all in payload | `_lib/devTicketContent.ts:36-67` | ✓ |
| No backend change | `git --no-pager diff 9605553..9e2212e -- gt-factory-os/api/ gt-factory-os/db/` returns empty (the portal repo doesn't include these paths; the change set is portal-only) | ✓ |
| No DB migration | no file under `db/migrations/` modified | ✓ |
| Typecheck PASS | `pnpm typecheck` exit 0 | ✓ |
| Build PASS | `pnpm build` exit 0; `/planning/blockers` route 24.9 kB | ✓ |
| No new test failures | 32 admin/BOM-editor tests still failing pre-existing; zero `/planning/blockers` test failure (no test file exists for this route) | ✓ |
| Commit landed | portal `9e2212e` on top of `9605553` | ✓ |

---

## K. What remains P1 / polish only

After FLOW-003 closure, `/planning/blockers` carries the following non-blocking items:

| ID | Description | Priority | Owner |
|----|-------------|----------|-------|
| FLOW-003-P1.a | Q5 fallback chip still renders `"פנה למפתח"` for any row with `fix_route = null`; mildly inconsistent with the new Q4 CTA on `check_po_substrate` rows | P1 polish | future portal-production-executor sweep |
| FLOW-003-P1.b | `DEV_TEAM_EMAIL` constant in `devTicketContent.ts` is empty; mailto: button suppressed until Tom configures the team alias | P1 (Tom action) | Tom — single touchpoint to edit |
| FLOW-003-P1.c | No automated test exists for the modal flow or the new button presence | P1 (test coverage) | future portal-production-executor sweep |
| INTER-001 | Cancel PO confirmation prompt (P1 confirmed in DR-011); not in Run C scope | P1 polish | future sweep |
| A11Y-001 | Three form inputs on `/(ops)/stock/waste-adjustments` lack programmatic labels | P1 polish | future sweep |

Long-term: Option B (root-cause planning-engine fix to remove the `check_po_substrate`
blocker class entirely) remains an architectural option per the FLOW-003 decision packet
§H. Run C explicitly chose A-with-C-interim over Option B; Option B is parked.

---

## L. STATUS block

```
STATUS: PASS

Surface: /planning/blockers (planner+admin only)
FLOW-003: CLOSED (P0 → resolved; A-with-C-interim implemented)
/planning/blockers verdict: HOLD → CONDITIONAL_SHIP
Aggregate UX gate verdict: HOLD → CONDITIONAL_SHIP
Files changed: 5 (3 modified, 2 new) — all in canonical portal repo
Backend change: 0
DB migration: 0
External integration: 0 (mailto: is browser-local URI scheme)
Typecheck: PASS
Build: PASS (/planning/blockers in manifest at 24.9 kB)
Tests: 32 pre-existing admin/BOM-editor failures unchanged; no /planning/blockers test exists or fails
Grep proof: old "פנה למפתח" CTA mapping removed; new "פתח כרטיס טיפול" + Tom-approved interim copy present
Stop conditions tripped: none
Tom approvals required:
  - FLOW-003-P1.b: provide team alias for DEV_TEAM_EMAIL when canonical
  - Aggregate UX gate transition HOLD → CONDITIONAL_SHIP requires Tom acknowledgement
Rollback: git revert 9e2212e on portal main (atomic; restores 5 files; no DB rollback needed)
Handoff: factory-os-governor (gate verdict update); ops-docs-curator (UX_RELEASE_GATE.md sync after Tom acknowledges)
```

---

**END OF DR-017 — FLOW-003 closed; /planning/blockers out of HOLD; aggregate UX gate CONDITIONAL_SHIP.**
