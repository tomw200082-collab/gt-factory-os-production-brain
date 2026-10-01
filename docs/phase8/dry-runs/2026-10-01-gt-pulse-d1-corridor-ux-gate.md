# GT Pulse D1 corridor (tranche 187) — UX release gate, sales profile (2026-10-01)

## Scope

**Screens:** every screen in the Hebrew RTL sales corridor: today, leads, the lead card, attention, orgs, settings, the shell, both sheets, and the toast.

**Code:** branch `feat/gt-pulse-d1-corridor`, from `d9b1ba0` to `e4347d2`; the base is `49435b1` (D1 follow-up, live).

**Profile:**
- **Copy:** Hebrew-first, checked against the approved register. Tom approved 3 strings on 2026-10-01.
- **Roles:** manager and rep.
- **Viewports and modes:** 320, 390, 430 and 1280, in light, dark (user preference) and reduced motion.
- **Data:** a synthetic fixture with long values.

**Evidence:** 96 shots across 72 states. Every state has 0 page overflow, 0 lead-card overflow, and no text under 12px.

## Findings and dispositions

| ID | Sev | Lens | Finding | Disposition |
|---|---|---|---|---|
| FLOW-001/003/004 (previous gate) | P1/P2 | Flow | Copy HOLDs | **Closed** with Tom's 3 strings. FLOW-001 is closed by the caption; see COPY-T187-001 |
| COPY-T187-001 | P1 | Copy | "כל הלידים הפתוחים" is untrue of the flow's last node, which counts verified orders, not open leads | **Mitigated**: the caption shows the approved `UI.leadsTitle` ("לידים"). The string stays registered. **Tom decides** on a corrected caption ("כל הלידים" proposed) |
| FLOW-005 | P1 | Flow | A lost recorded on /attention had no undo | **Fixed** `1a6a9d7`, with an e2e test |
| (found by FLOW-005's test) | P1 | Interaction | The toast had no z-index, so an undo raised while a lead card was open sat under the card on Leads and Attention | **Fixed** `1a6a9d7`: z-50. The e2e test was red before the fix |
| INTER-187-001 | P1 | Interaction | Quick-add save showed no in-flight state | **Fixed** `61e1009` |
| INTER-187-002 | P1 | Interaction | The FAB covers part of a card while scrolling | **Accepted as designed**: a fixed thumb-arc action (e2e-locked) over a list that scrolls clear (9rem end padding); on phones it is now a 56px disc instead of a pill |
| A11Y-187-001 | P1 | A11y | Tab bar focus ring at 1.48:1 on the turquoise capsule, in dark mode | **Fixed** `e4347d2`: the ring is drawn outside the link, on the glass |
| A11Y-187-002 | P1 | A11y | Toast close button was 24px | **Fixed** `e4347d2`: 44px |
| FLOW-006 | P2 | Flow | Settings "saved" stayed up through later edits | **Fixed** `1a6a9d7`: clears after 3s |
| INTER-187-003/004 | P2 | Interaction | Settings and outcome-sheet saves showed no in-flight state | **Fixed** `61e1009` |
| A11Y-187-003 | P2 | A11y | Settings "saved" live region mounted at the moment of announcement | **Fixed** `e4347d2`: always present |
| A11Y-187-004 | P2 | A11y | `role=status` on a static note | **Fixed** `e4347d2` |
| VISUAL-187-001 | P2 | Visual | Lead card contact buttons wrapped to two rows at 320 | **Fixed** `1a6a9d7` |
| VISUAL-187-002 | P2 | Visual | Org list items carry no status signal | Deferred: needs a neutral-badge string (Tom) |
| FLOW-007 | P2 | Flow | Opening a lead from an org card leaves /orgs | Accepted as designed |
| INTER-187-005 | P2 | Interaction | A disabled save does not say why | Deferred: needs copy (Tom); B-FLOW-04 already covers the outcome sheet |
| COPY-T187-002 | P1 (pre-existing) | Copy | `CustomerBadge` has inline "פעיל"/"לא פעיל" outside labels.ts | Deferred, out of tranche: moving it needs register keys (Tom) |
| Landmark names | P2 (pre-existing, A11Y-004 earlier) | A11y | The two navs share one name | Deferred: needs copy |

## Lens status after repairs

| Lens | P0 | Open P1 | Status |
|---|---|---|---|
| Flow | 0 | 0 | GREEN |
| Interaction | 0 | 0 (INTER-187-002 accepted) | GREEN |
| Visual | 0 | 0 | GREEN |
| Copy | 0 | 1 Tom decision (COPY-T187-001, mitigated); 1 pre-existing outside the tranche | AMBER |
| Accessibility | 0 | 0 | GREEN |

## Checks on `e4347d2`

- Vitest 1562/1562; typecheck, lint and build all exit 0.
- Mocked sales e2e: 57 pass. The 4 failures are the known local Chromium-1194 `tel:` artifact.
- Mobile specs in Chromium at phone size: 3/3.
- No backend change, no flag. The only new copy is the 3 Tom-approved strings.
