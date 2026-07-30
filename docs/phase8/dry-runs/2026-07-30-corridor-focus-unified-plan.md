# Corridor focus — unified execution plan — 2026-07-30

**Inputs:** corridor walk (`2026-07-30-ux-flow-audit-procurement-corridor.md`) + three per-page focus
audits (production-plan / meeting / procurement, agent reports in session) + Tom's cadence directive.
**Discipline:** ponytail — every finding passed the ladder; merged duplicates, killed low-value M/L
items, kept one-liners. 33 raw findings → **24 executable items + 4 named skips + 1 backend escalation**.

## Tom's cadence change (locked, 2026-07-30 in writing)

**Wednesday = the meeting** (production planning + lock + procurement planning). **Thursday = the
procurement execution.** Was Thursday/Sunday. Encoding is centralized: `stepForToday()` in
`meeting/_lib/cadence.ts:215-216` (2 lines) + STEPS sub-labels `page.tsx:110-111` (2 lines)
+ 6 user-facing copy strings. Fix = 4 functional lines, one `CADENCE_DAYS` constant, 6 string swaps,
comment sweep. Thursday count-list (tranche 153) now shares Thursday with procurement — count in the
morning, order with fresh stock truth; kept as-is unless Tom says otherwise.
NOT cadence: "Sun–Thu capacity" (`page.tsx:856`) is the factory work-week — do not touch.
Brain-side docs mention Thursday/Sunday (`plan-production-14d`, `procurement-planning`,
`daily-ops-guardian` skills) — flagged to ops-docs-curator lane, not this tranche.

## Tranche 155 — one batch, portal-only, all on existing primitives

### A. Cadence re-encode (MEET-310, P1)
As above. Flips on deploy — today is already Wednesday; if Tom wants a delayed flip he says so.

### B. Real bugs the focus audits caught (all one-liners)
| ID | Bug | Fix |
|---|---|---|
| PLAN-304 | Today strip shows "Unnamed product" for base batches | use existing `planLabel(p)` — `page.tsx:2481` |
| PLAN-306 | Drafts counted as "unreported" + offered "Move to tomorrow" (contradicts the draft banner above) | `&& p.status !== 'draft'` — `board-summary.ts:79` |
| MEET-308 | "won't produce unless **firmed**" — jargon COPY-001 missed | "unless you lock them" — `page.tsx:1303-1305` |

### C. Focus batch (S-effort each)

**Production plan** — the page must say "review drafts → lock" when drafts exist:
- PLAN-301 (+ subsumes corridor FLOW-201): when drafts exist, the teal primary becomes
  "Review drafts in Weekly Meeting →" (`?step=firm&week=`); add-buttons demote to secondary.
- PLAN-302 banner copy: one destination (meeting), drop the Planning-Overview fork.
- PLAN-303 status bar: split disclaimer / metrics / nav links into three visible blocks.
- PLAN-305 draft cards: delete the duplicate lock link (keep chip-area one).
- PLAN-308 state-aware page description (3 strings + conditional).
- PLAN-309 "excludes drafts" footnote on WEEK COMPLETION.
- PLAN-310-lite: mobile — timeline rail behind a closed disclosure; board reachable first swipe.

**Meeting** — one primary per step + "done" state:
- MEET-301 "Regenerate drafts" → text link when drafts exist (button only on empty first-run).
- MEET-304 regenerate trigger gets warning tone when `editedDraftCount > 0`.
- MEET-302 kill the "At-risk check: Flow" pseudo-KPI → plain "Inventory flow →" link.
- MEET-303-lite: CadenceRail Lock step shows a ✓ done state when the week is locked
  (query-derived, no new API). Procure-side completion deferred — see skips.
- MEET-305 "Edited" badge tooltip = `updated_at` + editor (fields already in the row).
- MEET-307 "Order calendar" tile → sub-link under "Open Procurement".
- MEET-309 mobile week range: drop `truncate`, compact format.

**Procurement** — the session is the page; everything else is context:
- PROC-301 (**P0**): WorkQueue CTA must reflect real PO status — a proposed session PO renders
  a muted "בסשן — אישור דרוש" pill, never "בצע מול ספק" while ActionList shows "פתח במיקוד"
  for the same supplier. + scope label on the WorkQueue header.
- PROC-302: session summary + "התחל מיקוד" promoted to position 2; WorkQueue below the
  ActionList, collapsed unless `overdueCount > 0`.
- PROC-303 (+306 merged): one KPI progress line on the session card —
  "{placed} הועברו · {approved} ממתינים · {proposed} לסקירה" from existing `totals.by_status`;
  the red strip keeps only must-today + amount.
- PROC-305: WorkQueue heading → "מעקב הזמנות בדרך ובעיכוב"; eyebrow "מושב רכש — {date}" above
  the ActionList.
- PROC-307: filter bar only when `pos.length > 8`; mobile collapsed.

**Corridor handoffs** (from the walk):
- FLOW-202 supersede confirm splits safe (APPROVED_TO_ORDER) vs lost (in-session) counts.
- FLOW-204 no-session orientation card (start-session reference) — pairs with Thursday cadence.
- FLOW-203 post-cancel banner gets "חזרה לרכש".
- COPY-201 drop the 🎉.
- INTER-201: "Orders to Place" appears in the Planning nav group too (same route + guard —
  a few manifest lines, not the M the audit sized).

### Named skips (ponytail: not built until reality asks)
| Skipped | Why | Add when |
|---|---|---|
| PROC-304 three-tier visual hierarchy (L) | PROC-302 reorder + PROC-305 labels deliver most of it | still confusing after reorder ships |
| PLAN-307 rail draft-color (M) | PLAN-306 fix + draft banner already carry the signal | a planner actually misreads the rail |
| MEET-303 Procure-side completion (M) | needs a new session-status read on the meeting page | planners report missing "am I done" |
| Status-bar metric pruning on mobile (part of PLAN-310) | rail disclosure buys the fold back alone | 390px still noisy after rail folds |

### Escalation (backend lane, not this tranche)
**MEET-306 (P0-comprehension):** W1 batch titles derived from `base_bom_head_id` → "DET STR".
Fix = add `base_name` to the production-plan list DTO (`gt-factory-os`, backend-db-executor lane,
small read-DTO change) + one portal fallback line. Routed separately; portal batch does not wait.

### Still parked (unchanged)
COPY-110 cancel-reason catalogue (needs Tom's per-role subset) · A11Y-106 token contrast (frozen
tokens, own tranche) · INTER-108 form wrapper.

## Ordering

1. Tom reviews + merges portal PR #198 (tranche 154 — the queue) — keeps review clean.
2. Tranche 155 executes on the same branch → new PR.
3. MEET-306 backend DTO as its own small change in `gt-factory-os`.

**Tom approval required:** yes — this plan (one tranche, 24 items) + merge timing of #198.
**Next action for Tom:** "מאשר 155" (and merge #198, or tell me to merge it).
