# ux-flow-audit — the procurement corridor, end to end — 2026-07-30

**Trigger:** Tom (2026-07-30, in writing, same session as the placement-queue gate): "תחשוב כמו
מתכנן רכש מקצועי ותעבור על הזרימה של כל הרצף… המסדרון צריך להיות יותר ממקד — כל הזמן תשאל את
השאלה: האם יש פה משהו מבלבל או שברור לגמרי מה צריך להיות הצעד הבא?"
**Corridor:** `/planning/production-plan` → `/planning/meeting` (two-week lock) →
`/planning/procurement` → `/purchase-orders/placement-queue` → `/stock/receipts` (entry links only).
**State audited:** portal branch `claude/procurement-execution-ux-x3p14w` at `42129e2` — tranche 154
applied (PR #198 open, awaiting Tom's visual review). Queue internals explicitly out of scope —
this audit is about the handoffs into and out of each stage.
**Agent:** ux-flow-architect. Read-only. Unit of analysis: the transition, not the page.

## Corridor map (the deliverable Tom asked for)

| # | Stage | Next step from here | Verdict |
|---|---|---|---|
| 1 | Production plan | → meeting to lock drafts | **PARTIAL** — horizon-week drafts link to the meeting with `?week=`; the *current* week's draft count is plain text with no CTA (the most common pre-lock state has no forward path) |
| 2 | Meeting — lock step | → board / → Sunday procurement | **PASS** — post-lock banner leads with "View the locked week →" and "For Sunday: open Procurement →"; CadenceRail names the Thursday/Sunday/Daily rhythm; `stepForToday()` auto-selects |
| 2b | Meeting — procure step | → procurement + receipts | **PASS** — ProcurePanel is a real handoff hub |
| 3 | Procurement session | → placement queue | **PARTIAL** — INT-P0-1 verified CLOSED; but the no-session Sunday return renders nothing below the work queue (no "a lock happened Thursday — start a session" orientation), and the supersede confirm still doesn't split safe vs. lost counts (FLOW-9 → FLOW-202) |
| 4 | Placement queue | → receipts; split loops back | **PASS** (tranche 154) — post-placement banner links receipts + names the split sibling; post-cancel banner lacks a return-to-procurement link (P2) |
| 5 | Receipts | — | not audited (out of scope); inbound links confirmed |

Cross-cutting: the corridor crosses an invisible **nav boundary** — Procurement sits in the
Planning sidebar group (auto-expands), Orders to Place sits in the collapsed Purchase Orders group.
The final leg of the corridor exists only as in-page links. A weekly cycle touches ≥5 routes and
only the meeting page's CadenceRail communicates the corridor's order.
Dead-weight check: `/planning/weekly-outlook`, `/planning/purchase-session`,
`/planning/purchase-calendar` are permanent redirects — correctly not live stops.

## Findings

| ID | Class | Sev | Effort | Finding | Proposed fix | Evidence |
|---|---|---|---|---|---|---|
| FLOW-201 | FLOW_COMPLETION | P1 | M | Current-week "N drafts" on the production plan is plain text — no link to the meeting; the identical horizon-week case already links with `?week=` | Mirror the existing horizon pattern for the current week | `production-plan/page.tsx:2256-2261` vs `:2203-2226` |
| FLOW-202 | FLOW_COMPLETION | P1 | S | Supersede confirm (carry-forward of FLOW-9, open since 2026-07-16) doesn't distinguish POs already in APPROVED_TO_ORDER (safe) from in-session approvals (lost) | Split the count by status tier in the confirm copy — data already on the session object | `procurement/page.tsx:130-132` |
| INTER-201 | FLOW_COMPLETION | P1 | M | Nav group split hides the corridor's final leg: Procurement in Planning (auto-expands), Orders to Place in collapsed Purchase Orders | Surface "Orders to Place" inside the Planning group (same route + capability guard), or auto-expand on corridor referral | `nav/manifest.ts:261-423` |
| FLOW-203 | POLISH | P2 | S | Post-cancellation banner on the queue has no return-to-procurement link (post-placement banner does link receipts) | Add "חזרה לרכש" secondary link | `placement-queue/page.tsx:342-373` |
| FLOW-204 | POLISH | P2 | S | No-session state on procurement renders nothing (`!session ? null`) — Sunday-returning planner gets no "start a session" orientation | Orientation card beneath the work queue referencing the existing start button | `procurement/page.tsx:247` |
| COPY-201 | POLISH | P2 | S | FocusMode done headline carries an emoji ("סיימת את מושב הרכש 🎉") — off-register for an operational surface | Remove emoji | `FocusMode.tsx:479` |

## Prior findings verified CLOSED (not re-reported)

INT-P0-1 (double-tap supersede bypass — `refreshConfirming` wired at `procurement/page.tsx:231`,
IntegrityStrip disables on pending/confirming), FLOW-8 (Dorin=planner, Option A), COPY-101
(corridor vocabulary in FocusMode), FLOW-103 (count link re-pointed, tranche 153), FLOW-101,
INT-102, and tranche 154's VIS-101.

## Focus verdict (the three moments "what's next" is not obvious, in corridor order)

1. **Plan → meeting:** the current-week draft count — the most common pre-lock state — is a number
   with no door. The mechanism exists eight lines above for horizon weeks.
2. **Thursday → Sunday:** the post-lock banner points at Sunday correctly, but Sunday's procurement
   page doesn't remember Thursday — an empty no-session state with no "start here."
3. **Procurement → queue:** the corridor's last leg crosses a collapsed nav group; it exists only
   as in-page links.

The meeting page is the corridor's strong axis — CadenceRail + post-lock banner + ProcurePanel are
exactly what "focused" looks like; the rest of the corridor should be pulled up to it.

## Escalations

None. All six findings are portal-source-only. No ARCH_REQUIRED, no governor escalation, no token
or backend change.

## Recommended execution

- **Tranche 155 (S-batch, one sitting):** FLOW-202 + FLOW-203 + FLOW-204 + COPY-201.
- **Tranche 156 (M-batch):** FLOW-201 + INTER-201.
- Both after Tom's visual review + merge of PR #198, so the executor works on the merged queue.

**Tom approval required:** yes — tranche authorization (155/156 split or one combined tranche).
**Next action for Tom:** approve the split (or say "הכול בטראנץ' אחד") and I execute.
