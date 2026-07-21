# UX Release Gate — Procurement Corridor (deepened re-run)

**Date:** 2026-07-21 · **Invoked:** Tom, `/ux-release-gate` + `/deepen` + `/caveman` in chat · **Portal tip:** `1d18166` (tranches 130-133 merged)
**Prior gate:** `UX-RELEASE-GATE-procurement-corridor-2026-07-16.md` (HOLD — 1 P0, 17 P1). This run = closure verification of all 18 prior findings + fresh deep audit of tranche-130-133 code + adversarial verification (P0 dual-lens, ∀ P1 single refuter).
**Encoding:** caveman per `/caveman` (symbols; paths/strings/quotes verbatim; ⊥ = never/forbidden, ∴ = fix, → = leads-to).

## Scope

Routes: `/planning/procurement` (+ ActionList, FocusCard, FocusMode, IntegrityStrip, CalendarView, AddLineForm, `[session_po_id]/sheet`), `/purchase-orders/placement-queue` (PlacementRow), `/purchase-orders`.
New-code focus: decision engine v2 (`_lib/decision.ts`), `IntegrityStrip` + refresh, click-to-fix warning chips (`_lib/session-warnings.ts`), cancel-with-reason (both surfaces), filter/sort (both surfaces), mobile collapse.
Hebrew+RTL on `/planning/procurement` + `/purchase-orders/placement-queue`: Tom-authorized (CLAUDE.md 2026-06-17/20) — ⊥ finding.

## Visual evidence

5 shots via committed `tests/e2e/ux-shot.spec.ts` (dev-shim auth, fixture-stubbed APIs, `PW_CHROME_PATH` sandbox chromium, 0 portal files touched). Populated decision-grade session fixture (7 POs ∀ buckets/severities, trace_version 3, `input_integrity`, 2 warnings). Runs 5/5 pass.
Shots + fixtures committed: `assets/uxg-2026-07-21/` (procurement desktop+mobile, placement-queue desktop+mobile, purchase-orders desktop; fx-*.json ×3).
Render-confirmed live: 3-bucket triage + quantified shortage badges + recount chips + IntegrityStrip chips + mobile collapsed strip ("4 לבדיקה") + PQ filter/sort + discard buttons.

## Verdict

**HOLD**

1 confirmed P0 (dual-lens): INT-P0-1 — double-tap "רענון המלצות" bypasses supersede confirm → open session silently replaced, approved-not-placed POs lost. Fresh defect in tranche-133 code, S-effort fix. Threshold locked: ∃ P0 → HOLD.
Big picture positive: prior P0 (FLOW-8) CLOSED; 9/18 prior findings CLOSED, 6 PARTIAL, 3 OPEN. Corridor materially better; one new sharp edge blocks ship.

## Prior-finding closure table (deepen pass 1)

| Prior ID | Verdict | Evidence |
|---|---|---|
| FLOW-8 (P0) | **CLOSED** | Option A (Tom 2026-07-16): Doreen=planner. Dead `he` field deleted + explainer `cockpit.ts:221-237`; RoleGate/manifest correct under A. No other viewer-blocked live-Hebrew tile |
| FLOW-5 | CLOSED | PlacementRow discard+reason `PlacementRow.tsx:255-368`; `useCancelOrder` `api.ts:172-222`; banner `page.tsx:128-151` |
| FLOW-6 | CLOSED | CTA "העבר לביצוע רכש" `FocusCard.tsx:849`; placed label "הועבר לביצוע" `:54`; residual → COPY-101 |
| FLOW-9 | **OPEN** | Supersede warning still "ואישורים שלא נשמרו יאבדו" — no placed/approved/proposed split `procurement/page.tsx:131-132`; 133 added 2nd entry into same ambiguous confirm `IntegrityStrip.tsx:263` |
| FLOW-1 | CLOSED | ActionList search+bucket-filter+sort `ActionList.tsx:618-679`; summary ∀ full session `:567-616` |
| FLOW-2 | CLOSED | PQ filter+sort `placement-queue/page.tsx:225-266`; overdue banner full-queue `:54-56` |
| FLOW-3 | PARTIAL | ⊥ delete-from-session; "בטל עם סיבה" = skip w/ reason; handled bucket accumulates. 131 deferred deliberately |
| FLOW-4 | PARTIAL | Defer = skip semantics (title `FocusCard.tsx:789` "תוצע שוב אוטומטית בסבב הבא"); ⊥ dated postpone; ⊥ defer on PQ |
| INTERACTION-1 | PARTIAL | = FLOW-4 |
| INTERACTION-2 | PARTIAL | "דלג" still instant, no confirm/undo; mitigation = auto-resurface semantics (131 decision) |
| INTERACTION-3 | PARTIAL | = FLOW-3 |
| INTERACTION-4 | CLOSED | = FLOW-1 |
| INTERACTION-5 | CLOSED | = FLOW-2 |
| INTERACTION-6 | CLOSED | Backend admits `APPROVED_TO_ORDER → CANCELLED`: `cancel_handler.ts:65-75`, migration 0258 §C. Gate's "OPEN/DRAFT only" premise no longer true |
| VISUAL-9 | PARTIAL | Filter/sort affordances shipped; defer affordance = focus-mode tooltip only |
| VISUAL-12 | **OPEN** | Raw enums as filter chips `purchase-orders/page.tsx:98-104,816` (`APPROVED_TO_ORDER`…). 131 self-downgraded to "cosmetic P2" vs gate P1 — unilateral |
| COPY-5 | PARTIAL | Labels fixed AList/FCard; `FocusMode.tsx:483-484` still "{placed} בוצעו" → COPY-101 |
| A11Y-2 | **OPEN** | `FocusMode.tsx:94-97,396-432` — no focus capture; Tab trap `:216-234` cycles occluded controls |
| A11Y-003 | OPEN | ⊥ global reduced-motion token; scattered per-feature blocks only |
| A11Y-004 | OPEN | Inline `role="alertdialog"` no aria-modal/focus `procurement/page.tsx:118-122` + FocusMode |
| A11Y-010 | OPEN, **grew** | ⊥ hoisted Tooltip.Provider; 132/133 added new per-component instance `IntegrityStrip.tsx:123` |

Rollup: 9 CLOSED (incl. P0) · 6 PARTIAL · 3 OPEN · leftovers 3 OPEN.

## Top-ranked actions (single cross-dimension list — the deliverable)

Rank: severity → ascending effort. Fresh IDs = 1xx; prior open IDs kept.

| # | ID | Sev | Eff | Dim | Route | Finding | ∴ Fix | Evidence |
|---|---|-----|-----|-----|-------|---------|-------|----------|
| 1 | INT-P0-1 | **P0** | S | interaction | /planning/procurement | Double-tap "רענון המלצות" bypasses supersede confirm: tap-1 → `handleStart` sets `confirmingStart=true`, returns w/o mutate → `refreshPending` stays false → button enabled, zero feedback, confirm zone renders in header (possibly off-viewport); tap-2 → guard falls through → `startMut.mutate({supersede:true})` → session replaced silently, approved-not-placed POs lost. Backend ignores `supersede` (`api.ts:79-83`) ∴ inline confirm = ONLY guard. ⊥ lock in `useStartSession` (bare useMutation). Post-count scenario = exactly 133's target flow | Wire `confirmingStart` into IntegrityStrip: disable button + show "ממתין לאישור…" after tap-1 (kills bypass + kills silent-click I3); or render confirm inline at strip. Add double-tap regression test | `page.tsx:81-96`, `IntegrityStrip.tsx:257-272`, `api.ts:77-98`; verifier: dual-lens CONFIRMED |
| 2 | FLOW-101 | P1 | S | flow | /planning/procurement | "ללא ספק" fix chip → `/admin/masters/{components,items}/[id]` → `(admin)` layout `RoleGate minimum="admin:execute"` → planner (`admin: null`) hits hard "Access restricted" card, no back-link. ⊥ alt non-admin route to assign supplier. Blast radius narrowed: weekly runner Tom=admin; still dead-end for planner persona | Capability-check at chip render (IntegrityStrip/ActionList, not pure util): non-admin → degrade to tooltip-only + copy "פנו למנהל" | `session-warnings.ts:51-53`, `(admin)/layout.tsx:10`, `authorize.ts:58-62`, `role-gate.tsx:66-78` |
| 3 | INT-101 | P1 | S | interaction | /planning/procurement | Escape w/ FocusCard cancel-panel open → FocusMode `requestClose` → whole overlay closes; `cancelling` ∉ isDirty guard → no confirm, typed reason lost | Panel keydown: stopPropagation + `setCancelling(false)` on Escape; add `cancelling` to isDirty | `FocusMode.tsx:209-213,94-97`, `FocusCard.tsx:260-269,679-746` |
| 4 | INT-102 | P1 | S | interaction | /purchase-orders/placement-queue | Expand panel & cancel panel = independent booleans → both open simultaneously → "בצע הזמנה" + "בטל הזמנה" stacked, no hierarchy | Mutual exclusion: opening one closes other | `PlacementRow.tsx:63,70,216-218,255-258` |
| 5 | INT-103 | P1 | S | interaction+a11y | /purchase-orders/placement-queue | "נקה סינון" bare text-3xs link — no min-h/padding → touch target ≪ 24px (WCAG 2.5.8 fail); ActionList twin already fixed `min-h-[2rem]` (INTER-204) | Copy ActionList classes | `placement-queue/page.tsx:256-264` vs `ActionList.tsx:673` |
| 6 | INT-105 | P1 | S | interaction | /planning/procurement (mobile) | Refresh action lives inside collapsed-strip detail (`hidden` until expand); collapsed bar shows only "N לבדיקה" + chevron → post-count refresh loop undiscoverable on mobile | Add compact refresh hint (icon / "· רענן") to collapsed bar when `showRefresh` | `IntegrityStrip.tsx:129-156,158-164` + shot mobile |
| 7 | FLOW-104 | P1 | S | flow+copy | /planning/procurement | `can_wait` deadline rendered w/o "~" (`להזמין עד DD/MM`, `אפשר להמתין עד …`) though derived from extrapolated zeroDate; module contract mandates "~" (`decision.ts:20-30`); must_today strings comply | Add "~" when `usedTraceMath`; fallback v1 path stays plain | `ActionList.tsx:318-321`, `decision.ts:386` vs `:286-290` |
| 8 | FLOW-105 | P1 | S | flow | /purchase-orders/placement-queue | Cancel-success banner: po_number + reason, ⊥ PO link; `cancelled` state doesn't capture `po_id` → reason unreachable post-dismiss. Place banner has link | Capture `po_id` in `onCancelled`; add "צפה בהזמנה" link (mirror `:89-126`) | `placement-queue/page.tsx:75-78,128-151` |
| 9 | COPY-101 | P1 | S | copy | /planning/procurement | FocusMode never got tranche-130 corridor vocabulary: flash "ההזמנה נוצרה" `:339` + DoneSummary "{placed} בוצעו" `:483-484` vs corridor "הועבר/ה לביצוע". Mitigation on-screen (`:511-518` "ממתינות לביצוע…" + link) → P1 not P0 (verifier downgrade) | Flash → "הועברה לביצוע"; DoneSummary → "הועברו לביצוע" | `FocusMode.tsx:339,483-484` |
| 10 | VIS-101 | P1 | S | visual | corridor | Same danger action, two trigger grammars: FocusCard `Ban` icon + labeled ghost "בטל עם סיבה" vs PlacementRow icon-only `XCircle`, no visible label | One rule: labeled ghost + one icon, both surfaces | `FocusCard.tsx:796-806`, `PlacementRow.tsx:255-268` |
| 11 | A11Y-101 | P1 | S | a11y | /planning/procurement | FocusCard cancel-reason `<select>`: label w/o `htmlFor`, select w/o `id` → unlabeled control in destructive panel. PlacementRow does it right (`:279,:285`) | Mirror PlacementRow ids | `FocusCard.tsx:685-691` |
| 12 | A11Y-102 | P1 | S | a11y | /planning/procurement | Cancel panel: ⊥ focus move on open, trigger ⊥ `aria-expanded`, panel renders BEFORE trigger in DOM → reachable only shift-tab, unannounced | `aria-expanded` on trigger + focus ref on `cancelling` + reorder DOM | `FocusCard.tsx:225,248-250,679,796-804` |
| 13 | A11Y-103 | P1 | S | a11y | /purchase-orders/placement-queue | Supplier filter: ⊥ aria-live result count; ActionList twin has `role="status" aria-live="polite"` (`:684`) | Add sr-only status region | `placement-queue/page.tsx:235-243` |
| 14 | A11Y-104 | P1 | S | a11y | /planning/procurement | `--fg-subtle` light = 3.09:1 (`globals.css:59`, self-documented `:66`) on REAL data: FocusCard thead (10px uppercase) + recommended-qty td → AA fail, ⊥ large-text exemption. Dark ok (4.90:1) | S: swap 2 sites → `text-fg-muted`. L path: token ladder rebalance (deferred by 133, now site-verified) | `FocusCard.tsx:469,505`, `tailwind.config.ts:127` |
| 15 | FLOW-102 | P1 | M | flow | /planning/procurement | `skip_reason` write-only: collected + POSTed, ⊥ rendered anywhere, ∉ `PurchaseSessionPo` DTO → audit intent invisible; supersede → gone. PQ cancel contrast: reason → PO notes, visible in detail | Add field to DTO + faint caption under "דולג / בוטל" in handled row | `FocusCard.tsx:729-731`, `api.ts:169-173`, `types.ts` (absent), `ActionList.tsx:83` |
| 16 | FLOW-103 | P1 | M | flow | corridor ↔ /stock/physical-count | Recount loop half-open: chip → bare `/stock/physical-count` (⊥ `?item_id=` prefill — page SUPPORTS it `:323-328`); count success screen ⊥ return link to procurement (grep "procurement" = 0) | Pass item prefill param; add "חזרה לרשימת הרכש" success link | `ActionList.tsx:77,362-363`, `physical-count/page.tsx:323-328,746-786` |
| 17 | INT-104 | P1 | M | interaction | corridor | Filter/sort = plain useState, ⊥ URL params → ∀ click-to-fix chip round-trip (recount / warning / PO) wipes filter state; only `?view=calendar` persisted | Serialize query/bucket/sort → searchParams, shallow replace | `ActionList.tsx:486-488`, `placement-queue/page.tsx:58-59`, `page.tsx:61-63` |
| 18 | COPY-102 | P1 | M | copy | corridor | Cancel-reason catalogues diverge (2/4 vs 2/5 shared); FocusCard comment `:58-59` claims "same catalogue" — false. Two actors, incompatible audit vocabularies | Shared `CANCEL_REASONS` const; Tom picks per-role subset | merge | `FocusCard.tsx:60-65` vs `PlacementRow.tsx:35-41` |
| 19 | FLOW-9 | P1 | S | flow | /planning/procurement | PRIOR, still open — supersede warning ⊥ placed/approved/proposed breakdown; now feeds INT-P0-1's confirm too | Per-status breakdown in confirm copy | `page.tsx:131-132` |
| 20 | VISUAL-12 | P1 | S | visual+copy | /purchase-orders | PRIOR, still open — raw enum filter chips (`APPROVED_TO_ORDER`…), §1 forbidden; badge map exists, chips bypass it | `FILTER_LABEL` map mirroring POStatusBadge | `page.tsx:98-104,816`; shot purchase-orders desktop |
| 21 | A11Y-2 | P1 | M | a11y | /planning/procurement | PRIOR, still open — FocusMode close-confirm: ⊥ focus move in, Tab cycles occluded controls (= A11Y-004 class) | Focus trap + initial focus in confirm | `FocusMode.tsx:94-97,216-234,396-432` |

## P0 findings — block ship

| ID | Dimension | Route | Description |
|---|---|---|---|
| INT-P0-1 | interaction | /planning/procurement | Double-tap "רענון המלצות" = silent session supersede w/o ever seeing confirm; approved-unplaced work lost; confirm = only guard (backend ignores `supersede`). Row #1 above — full mechanism + fix there |

## P1 findings — conditional-ship items

Rows #2-21 above (17 fresh + FLOW-9, VISUAL-12, A11Y-2 prior-open). Carried PARTIAL residuals (named, next-sprint candidates, ⊥ blockers): delete-from-session (FLOW-3/INTER-3), dated defer + PQ defer (FLOW-4/INTER-1), skip w/o confirm/undo (INTER-2), defer affordance (VISUAL-9), leftovers A11Y-003/004/010.

## P2 tail (fresh, confirmed; audit trail)

| ID | Route | One-liner | Evidence |
|---|---|---|---|
| INT-201 | procurement | "כדאי לספור קודם" summary count = static span, ⊥ one-click filter to those rows | `ActionList.tsx:606-615` |
| VIS-201 | procurement | mustCost banner amount `text-fg-muted` ⊥ font-mono/semibold vs row-amount rule (verifier: deliberate de-emphasis idiom → P2) | `ActionList.tsx:589-591` |
| VIS-202 | procurement | `ChevronRight` collapsed-state icon inside `dir="rtl"` — points to reading start | `ActionList.tsx:283` |
| VIS-203 | procurement | Bucket `h2` always neutral `text-fg`; urgency tone via icon/badge only | `ActionList.tsx:725-726` |
| VIS-204 | corridor | Filter paradigm split: selects (procurement) vs pill-tabs (/purchase-orders) same mental model | shots ×2 |
| VIS-205 | procurement | Summary shows can_wait count w/o ₪ total (must_today shows both) | `ActionList.tsx:604` |
| VIS-206 | placement-queue | Sort `<select>` `w-40` clips longest label "מיין: דחיפות (ברירת מחדל)" at rest (governor-added, shot-confirmed) | `page.tsx:245-255` + shots |
| COPY-201 | procurement | Placed-success `PO {po.po_id.slice(0, 8)}…` on business key "PO-2026-NNNNN" → degenerate "PO PO-2026-…" ∀ POs identical label (mechanism corrected by verifier: not UUID) | `FocusCard.tsx:666,670` |
| COPY-202 | procurement | Hebrew number agreement: "1 בדרך ללא תאריך", "1 אספקות באיחור" | `session-warnings.ts:203,211` |
| COPY-203 | procurement | Forecast chip renders "?" on null age ("תחזית: לפני ? ימ׳") | `IntegrityStrip.tsx:205` |
| COPY-204 | /purchase-orders | Unknown-supplier: visible `({supplier_id.slice(0,8)}…)` + title `supplier_id <id>` (prior COPY-35 class, unchanged; kept P2 per precedent) | `page.tsx:993-999,1098-1108` |
| COPY-205 | placement-queue | Place-confirm claims "לא ניתן לבטל הזמנה שבוצעה דרך המערכת" — overstates irreversibility (cancel exists for OPEN); safe-direction lie | `PlacementRow.tsx:177` vs backend `cancel_handler.ts:68` |
| A11Y-201 | procurement | Refresh spinner `animate-spin` ⊥ `motion-reduce:animate-none` (PlacementRow twin has it) | `IntegrityStrip.tsx:267` vs `PlacementRow.tsx:358` |
| A11Y-202 | procurement | Link-chips (`decoration-dotted` only on hover) indistinguishable from non-link badges at rest — WCAG 1.4.1 | `IntegrityStrip.tsx:232-248` |
| GOV-201 | /home cockpit | Dead-`he` pattern recurs: `/admin/cost-drafts` tile `he` can never render (= exact pattern FLOW-8 fix deleted + warned against) | `cockpit.ts:246,373-402` |
| GOV-202 | /home cockpit | `/inventory` tile `he` unreachable (viewer groupOrder omits "stock") | `cockpit.ts:293,396-401` |
| GOV-203 | procurement | A11Y-010 debt GREW: 132/133 added per-component Tooltip.Provider | `IntegrityStrip.tsx:123` |

## Per-dimension status

| Dimension | P0 | P1 | P2 | Status |
|---|---|---|---|---|
| flow | 0 | 6 (5 fresh + FLOW-9) | — | AMBER |
| interaction | **1** | 5 fresh | 1 | **RED** |
| visual | 0 | 2 (VIS-101 + VISUAL-12) | 6 | AMBER |
| copy | 0 | 2 fresh | 5 | AMBER |
| a11y | 0 | 5 (4 fresh + A11Y-2) | 2 | AMBER |

## portal_ux_standard.md compliance

**FAIL** (narrowed vs 2026-07-16): §1 — raw enum chips `/purchase-orders` (VISUAL-12, open), supplier_id fragment+field-name title (COPY-204), degenerate id slice (COPY-201); §4 — FocusMode vocabulary split "נוצרה"/"בוצעו" vs corridor "הועבר לביצוע" (COPY-101); truthfulness — "~" contract violated on can_wait (FLOW-104), irreversibility overstated (COPY-205). §3 error-template: no new violations found in new code. Hebrew/RTL usage on 2 authorized surfaces: compliant.

## Adversarial verification

∀ P0 candidates dual-lens; ∀ fresh P1 single refuter. Outcomes:
- **INT-P0-1 CONFIRMED P0** — 6 refutation angles ∀ failed; only softener = zero test coverage of double-tap.
- **FLOW-101 downgraded P0→P1** — wall on secondary fix-nav, ⊥ daily-task block; weekly runner = admin.
- **COPY-101 downgraded P0→P1** — misleading word neutralized by same-screen "ממתינות לביצוע" + queue link.
- **REFUTED, dropped (3):** A11Y "PlacementRow cancel panel no focus move" (compliant APG disclosure: `aria-expanded` + DOM-adjacent); COPY "inbound tooltip surfaces UUID" (`po_id` = business key "PO-2026-NNNNN", readable); VIS "refresh indistinguishable from badges" (badges bordered pills; refresh = icon+accent link — distinct).
- **Downgraded P1→P2 (2):** VIS-201 (matches sibling de-emphasis idiom); COPY-201 (transient banner, working link; mechanism corrected).
- 10/10 interaction+flow P1 batch CONFIRMED; 4/5 a11y P1 CONFIRMED.

## Evidence standard (handoff contract)

STATUS: **HOLD_FOR_TOM** (gate verdict HOLD). Files changed: this report + `assets/uxg-2026-07-21/` (8 files) — brain repo only; 0 product-code files touched (read-only gate). Tests run: none (no code changed); render harness `ux-shot` 5/5 pass. Contracts referenced: `portal_ux_standard.md` §1/§3/§4, CLAUDE.md UI-language exceptions, `VERDICT_GLOSSARY.md`. Signals emitted: none. Stop conditions tripped: none. Rollback plan: n/a (docs-only). Agents: 5 UX dimensions + closure verifier + 6 adversarial verifiers (12 subagent runs).

## Tom approval required?

**yes** — (1) HOLD acknowledgment + authorize portal fix tranche (134) for INT-P0-1 + the S-effort P1 cluster (rows 2-14: ~13 one-file fixes); (2) COPY-102 needs Tom's preset-catalogue decision (which cancel reasons per role); (3) unlike 2026-07-16, ⊥ architecture decision required — pure portal-lane work, `portal-production-executor` can execute on approval.

## Next action for Tom

Approve dispatch of portal tranche 134: close INT-P0-1 (wire `confirmingStart` → IntegrityStrip disable/feedback + double-tap regression test) + S-effort P1 rows 2-14 in same tranche; M-effort rows 15-18 + FLOW-9/VISUAL-12/A11Y-2 → tranche 135. Then re-run `/ux-release-gate` for CONDITIONAL_SHIP with named P2 tail.

---
*Read-only gate. Reports to `docs/phase8/dry-runs/` per write policy. Prior-gate design directives (2026-07-16 footer) remain valid for the fix tranche.*
