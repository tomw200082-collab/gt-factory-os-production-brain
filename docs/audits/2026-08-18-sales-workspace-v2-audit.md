# Sales Workspace v2 — Adversarial Audit (Phase 0)

**Date:** 2026-08-18 · **Trigger:** v2 masterprompt Phase 0 · **Posture:** skeptical auditor assuming v1 was competent but wrong somewhere.
**Method:** five parallel audit lenses (`ux-flow-architect`, `interaction-design-specialist`, `accessibility-usability-auditor`, `portal-admin-surface-auditor`, `visual-system-designer`) over the full `(sales)` portal tree, the 13 proxy routes, the 14 backend endpoints, and migrations 0318–0323 — followed by an independent refutation pass that attacked the 20 load-bearing claims, and by direct live-production verification (SQL against `rvadsozabmxkkrktwgnv`, deployed-state probes).
**Verdict scale:** `CONFIRMED` = survived refutation with exact code/live evidence · `ADJUSTED` = direction right, detail corrected · `PLAUSIBLE` = consistent with evidence but not provable from code alone. Grades follow the Sales-Machine constitution (`system_verified` / `doc_confirmed` / `inferred`).

Refutation outcome: 18/20 claims CONFIRMED, 1 ADJUSTED, 1 settled against the claiming auditor (see V-10). Line citations verified to ±3 lines.

---

## 0 · Live-state verification — deltas against masterprompt §2

Every F-row we built on was re-verified. Three rows needed material correction; the rest held.

| # | Live fact (2026-08-18, `system_verified`) | Delta vs masterprompt |
|---|---|---|
| L1 | 188 leads, **all `status='new'`, 0 assigned, 0 with `next_touch_at`**; 189 `lead_event` rows (188 `created` + **1 `outreach`**) | Confirms F6 — and adds: the v1 loop has effectively not started. One outreach ever. |
| L2 | Newest lead `created_at` = **2026-08-09**. Zero new leads in 9 days. Sole source: `import_meta_export` | Sharper than F20: the intake is not "waiting on credentials", it is an empty pipe **today**. Speed-to-lead is currently ∞. |
| L3 | **39/188 leads have neither phone nor email** (uncontactable); 2 flagged `possible_duplicate_of`. Workable queue = 149 | Matches v1 plan §2; the 39 sit in the Today queue as permanent dead weight. |
| L4 | Age spread: 16 leads at 90–98 days, **39 leads older than 113 days (up to 1157)** | F21's "expire early September" applies to Meta's copy; our copy is already imported. The real September risk is L2 — leads landing in Meta *now* are not imported and will age out unseen. |
| L5 | PII lock holds: `api_read.v_sales_*` (5 views) + 7 `sales_core` write functions granted to **`service_role` only**; no `authenticated` grants | Confirms the §1 non-negotiable. |
| L6 | Migrations 0318–0323 applied to prod (incl. the `customer_badge_fix` re-apply); portal `/sales/today` → 307; API unauth → **401** on `gt-factory-os-api-production.up.railway.app` | Confirms F1/F4/F7. (A probe of a wrong subdomain returns 404 — the 404-vs-401 test only works against the real host.) |
| L7 | No sales-related Edge Function deployed (10 functions listed, none sales) | Confirms F20. |
| L8 | Roles live: admin 27 · operator 20 · planner 35 · viewer 23 = 105 users; ≥69 test-like emails; no `sales` role | Confirms F9/F10/F11. |
| L9 | `app_setting`: `sla_hours` {hours: 24} + `whatsapp_templates` (3 Hebrew templates) | Confirms F14. |
| L10 | **Governance drift:** brain PR **#139** (Amendment A recorded approved, v1 implementation plan, GAP-029/030, lessons 2026-08-18) and Sales-Machine PR **#5** (U-011/012/013) are **unmerged drafts**. The masterprompt cites their contents as canonical; `main` of both repos does not contain them | New finding — INF-1 below. |

---

## 1 · P0 findings

### P0-1 · The Today queue is a wall of 188 with a hardcoded shape — and the first card is a lead from 2023
**Claim:** `v_sales_today` admits every untouched `new` lead (188/188 today); ordering is hardcoded twice — `queries_handler.ts:50-56` (`item_type` CASE, then `coalesce(next_touch_at, created_at) asc`) on top of the view's item_type derivation (0323:140-147); the only "cap" is client-side render batching `PAGE = 12` (`TodayQueue.tsx:28`). `asc` on `created_at` means the **oldest** lead — 2023-06-18, uncontactable — is the first card an agent sees. No cap, weights, or ordering knob exists in `app_setting` (0322:55-62 seeds two keys only).
**Evidence:** live SQL (L1), `api/src/sales/queries_handler.ts:50-56`, `_components/TodayQueue.tsx:28`, `db/migrations/0323:187-190`.
**Consequence (Tom):** "אני פותח את האפליקציה כדי לדעת למי להתקשר — ומקבל קיר של 188 שמתחיל בליד מת מ-2023. אין מערכת שמחליטה מי החמישה של היום, אז אני בוחר אקראית או סוגר."
**Verdict:** CONFIRMED (`system_verified`). This is U-011 in code. Sources: FLOW-001, admin-F4, INTER-009/010, VISUAL-003 (mobile leads list = one 19,879px scroll, unpaginated — `LeadsTable.tsx:40-78`).

### P0-2 · Assignment is a dead end: invisible, unvalidated, one-at-a-time, and pointing at nobody
**Claim:** (a) `assignee` is rendered in **zero** list surfaces — LeadsTable's 7 columns, TodayCard, OrgList all omit it; search predicates exclude it (`format.ts:130-142`); it appears only inside the drawer's own edit field and in past timeline events. (b) `assignBodySchema = z.object({assignee: z.string()})` — no `.email()`, no allowlist, no existence check (`schemas.ts:37-39`); the UI is a bare text input. (c) No bulk endpoint exists (`route.ts:144-218` registers only per-`:lead_id` singletons); no row selection in any table. (d) The backend's `?assignee=` queue scoping is complete and **has zero portal callers** (`api.ts:92-98` fetches bare URL). (e) There is no `sales` role, Erik has no account, and ≥69 test users pollute any naive picker.
**Evidence:** refutation R4/R5/R6/R8 all CONFIRMED with exact lines; live L8.
**Consequence (Tom):** "חילקתי לאריק 50 לידים — מהרגע הזה אני לא יכול לראות מה שלו ומה שלי בשום מסך, הוא לא יכול להתחבר בכלל, ואם טעיתי באות אחת במייל הליד שייך לרוח רפאים ואף מסך לא יגיד לי."
**Verdict:** CONFIRMED (`system_verified`). **Blocked on Tom's §6.1 A/B/C decision** — the picker, the roster, and queue scoping all hang on it. Sources: FLOW-002, admin-F1/F2/F3/F10/F15, INTER-003.

### P0-3 · One tap in the drawer makes a lead permanently invisible: `working` with no next touch
**Claim:** `set_lead_status('working')` (0322:112-150) has no next-touch requirement — while `record_outcome` enforces `SALES_NEXT_TOUCH_REQUIRED` (0322:287-289, 313-316). The Today view admits `working` leads only when `next_touch_at is not null and <= now()` (0323:187-190). Drawer status button and next-touch input are separate saves (`LeadDrawer.tsx:276-298`). A lead set to `working` in the drawer without a date leaves the queue forever; it remains findable only under the leads-table "בטיפול" tab.
**Consequence (Tom):** "סימנתי 'בטיפול' בלי לקבוע תאריך — הליד נעלם מהתור לתמיד בלי שום תזכורת. הכלל שבנינו — אין ליד פתוח בלי מגע הבא — קיים רק במסלול אחד מתוך שניים."
**Verdict:** CONFIRMED (`system_verified`; refutation R1, incl. the recoverability nuance). Source: FLOW-003.

### P0-4 · A call from anywhere except Today ends in silence: the outcome is dropped
**Claim:** `OutcomeSheet` mounts only in `today/page.tsx`. The leads page arms call intents (`leads/page.tsx:60-61, 175-178`) but renders no sheet; `today/page.tsx:59-63` **clears** any pending intent whose lead is absent from today's rows. Drop is fully silent — no toast, no event. Only the arm-time `outreach` event survives.
**Consequence (Tom):** "התקשרתי מתוך הטבלה לליד בטיפול, סגרתי איתו משהו — ושום דבר לא שאל אותי מה קרה. השיחה לא נרשמה, המגע הבא לא נקבע. 'כל שיחה נגמרת עם הבאה מתוזמנת' נכון רק לחברי התור."
**Verdict:** CONFIRMED (`system_verified`; refutation R2 traced the full path). Sources: FLOW-009, admin-F9.
**Corollary (admin-F17 / R17, CONFIRMED):** `add_lead_note` also stamps `first_touch_at` (0322:171) and nothing can un-stamp it or return a lead to `new` — one accidental note permanently kills the new/SLA signal.

### P0-5 · Nothing aggregates what is stuck, slipping, or unowned — Tom's daily question has no screen
**Claim (ADJUSTED per refutation R3):** per-lead overdue markers exist (SlaBadge "עבר זמן", red `next_touch_overdue` date cells). What does not exist anywhere: an aggregate — `v_sales_week_stats` carries only week_new/working_now/week_converted (0323:196-207), StatsStrip renders exactly those three (and on live data reads **"0 · 0 · 0"** — all 188 leads predate this ISO week), tab bar carries no badges, no stuck/overdue/unassigned tab or view exists. The server-side ingredients (`next_touch_overdue`, `due_follow_up` bucket) are computed and never composed for an admin.
**Consequence (Tom):** "השאלה היומית שלי — מה תקוע, מה מחליק, מה בלי בעלים — נענית היום ב-SQL או בכלל לא. והמסך נפתח על שורה שאומרת 'השבוע: 0 לידים' מעל 188 לידים שנשרפים."
**Verdict:** CONFIRMED as adjusted (`system_verified`). Sources: FLOW-004/010/012, admin-F5/F7.

### P0-6 · The intake pipe is empty NOW — 9 days of Meta leads already invisible
**Claim:** newest lead in prod = 2026-08-09; sole source is the one-time CSV import; no sales Edge Function is deployed. Any lead submitted to Meta since Aug 9 is invisible to the system, and Meta deletes at 90 days. The masterprompt schedules intake wiring at Phase 3 (after Phase 2 lands and is reviewed) — on current cadence that extends the blind window by weeks.
**Consequence (Tom):** "בזמן שאנחנו משפצים את המסך, לידים אמיתיים ממטא לא נכנסים לשום מקום כבר תשעה ימים. speed-to-lead לא יכול להתקיים כשהצינור ריק."
**Verdict:** CONFIRMED (`system_verified`, live L2/L7). Sequencing risk, not a v1 code bug — v2 plan must pull the intake credential ask **forward** (it stays gated on Tom's two credentials; only its place in line changes).

### P0-7 · Visual: the destructive action shouts and the operational number whispers
**Claim:** (a) "אבוד" sits in the primary action row of every card in `hsl(0 72% 46%)` red — the same value as the SLA alarm token (`s-btn-danger-quiet` borrows `--s-sla-overdue`, tokens:259) — competing with the teal primary "התקשר" 188 times per session. (b) The section count ("187") — the one number that states the size of the fire — renders 12px in `--s-fg-faint`, the lightest ink on the page (`TodayQueue.tsx:63`).
**Consequence (Tom):** "הכפתור הכי בולט בכרטיס הוא היציאה מהלולאה, והמספר הכי חשוב במסך הוא הטקסט הכי חלש בו."
**Verdict:** code facts CONFIRMED (`system_verified`); the attention claim is design judgment — PLAUSIBLE and consistent with Hick's law at 188 repetitions. Sources: VISUAL-001/002/012.

---

## 2 · P1 findings (consolidated; every row survived refutation unless marked)

| ID | Finding | Evidence | Verdict |
|---|---|---|---|
| P1-1 | **Next-touch defaults are DST-naive and Shabbat-blind:** `no_answer` → tomorrow, `whatsapp_sent` → +2d, both at `date_trunc('day', now()) + 6h` = **06:00 UTC fixed** — 09:00 IL only in summer, 08:00 in winter; day boundary is the UTC day; a Thursday "לא ענה" lands Friday, a Friday one lands **Shabbat**. User never sees the date before submit (no preview, no custom option on these two paths). | 0322:281-286 · OutcomeSheet.tsx:174-191 · R19 | CONFIRMED |
| P1-2 | Assignment and next-touch are decoupled — assigning writes no due date, violating §6.1's "assignment without a next action is a to-do that rots" | LeadDrawer.tsx:331-408 · 0322:198-215 | CONFIRMED |
| P1-3 | SLA badge is binary and, on live data, **uniform**: 188/188 untouched leads all show "עבר זמן" — a timer on everything is a timer on nothing (inverse of the token file's own design note). No day-count, no Meta-expiry signal. | SlaBadge.tsx:15-21 · 0323:175-179 · R9 | CONFIRMED |
| P1-4 | OutcomeSheet backdrop tap bypasses the `busy` guard the buttons and Escape both honor — mid-write dismissal, error has nowhere to render | OutcomeSheet.tsx:124-126 vs 96, 340 · R11 | CONFIRMED |
| P1-5 | Drawer Escape/backdrop discard unsaved note/assignee text with no dirty-check | LeadDrawer.tsx:98-102, 145-147 · R12 | CONFIRMED |
| P1-6 | Drawer lost-path stores the literal string **"אחר"** as `lost_reason` (no free-text branch; OutcomeSheet has one) — the exact failure 0318's header says the schema exists to prevent | LeadDrawer.tsx:301-329 · labels.ts:68 · R16 | CONFIRMED |
| P1-7 | Lost reasons hardcoded in `labels.ts:63-69`; "אחר" compared as a magic string in two places; editing the list = portal deploy | labels.ts · OutcomeSheet.tsx:114,303 | CONFIRMED |
| P1-8 | Settings writes are unaudited: `app_setting` has no actor, no event; SLA 24→96 retroactively recolors every lead's `sla_state` (computed live) with zero trace | 0322:46-73 · mutations_handler.ts:227-253 · R18 | CONFIRMED |
| P1-9 | No undo on "אבוד" (recovery = 4-5 taps through drawer); no optimistic update on postpone (card lingers, invites double-tap) | INTER-004 · api.ts:171-174 | CONFIRMED |
| P1-10 | Mutation errors mislabeled: network failure on any POST shows "לא הצלחנו לטעון את התור"; 401 surfaces English "Not authenticated" in the Hebrew UI | api.ts:47-48, 63 · api-proxy.ts:97-99 | CONFIRMED |
| P1-11 | Touch targets below the §8 44px floor: header trio + 2 dialog closes at 40px; `.s-tab` 40px; OrgCard lead links ≈34px | SalesShell.tsx:102,112,127 · tokens:308 · OrgCard.tsx:129 · R13 | CONFIRMED |
| P1-12 | Lost-reason `role="radiogroup"` has no roving tabindex / arrow keys (the leads tablist does it correctly — inconsistency, not ignorance) | OutcomeSheet.tsx:287-301 · R14 | CONFIRMED |
| P1-13 | FAB at `insetInlineEnd:16` = physical **bottom-left** in RTL — off the right-thumb arc | SalesShell.tsx:186 · R15 | CONFIRMED |
| P1-14 | Age carries no urgency gradient — "לפני 19 ימים" renders identically to "לפני 1 ימים", 12px muted | TodayCard.tsx:118-123 | CONFIRMED |
| P1-15 | Two agents can work the same lead with no in-progress signal (DB serializes the events; UI shows nothing) | TodayCard.tsx · 0322:219-240 | PLAUSIBLE (scenario) / code facts CONFIRMED |
| P1-16 | Ghost button renders an opaque white rectangle on the tinted returning-customer card | TodayCard.tsx:75-85 · tokens:246-255 | CONFIRMED |
| P1-17 | Muted/faint text tiers differ by 3% lightness — the three-level hierarchy reads as two on a phone | tokens:25-27 | PLAUSIBLE (perceptual; token math `system_verified`) |
| P1-18 | Desktop table rows: `cursor-pointer` with zero hover affordance; skeleton height 132px vs real card ≈188px (load flash); status column repeats the active tab on every row | LeadsTable.tsx:117-123 · EmptyStates.tsx:64 | CONFIRMED |
| P1-19 | **The ops→sales switch shipped and the primary user cannot find it.** Tranche 163 / PR #214 added `SalesSwitch` to the factory TopBar (merged, deployed) — but it renders icon-only (`ArrowLeftRight`) below `sm`, ghost-styled, unlabeled, among five other topbar icons; its only name is an English hover `title` that phones never show. Tom, 2026-08-18 (v2 session, in writing): "צריך להיות מקש ברור מהחלק של התפעול למעבר למכירות. כרגע יש רק מהמכירות לתפעול" — the feature exists and reads as absent to the one person it was built for. | TopBar.tsx:221-231 · tranche 163 doc | CONFIRMED (`user_confirmed` + `system_verified`) |

## 3 · P2 findings (abridged — full detail in the five agent reports)

Quick-add captures no next-touch/assignee for hot inbound leads (FLOW-014) · lost-reason UI differs between sheet (radio) and drawer (select) (FLOW-015/INTER-014) · orgs page shows only the **first** lead's timeline per org — the Patio-case repeat submission would be invisible (FLOW-016; P1 for the returning-customer story) · three identical "שמור" buttons in the drawer (VISUAL-014) · conversion card's only distinction is a 35%-opacity border (VISUAL-015) · `ShopifySnapshot.status` leaks English "active" into Hebrew UI (VISUAL-017) · StatsStrip returns null while loading (CLS) (INTER-015) · save buttons never show "שומר…" (INTER-016) · SLA input `aria-invalid` with no error text; hint not associated; quick-add required-field unmarked; disabled no-phone button relies on `title` (iOS VoiceOver silent); events-load completion unannounced; CommandK input border removed (1.4.11 gap); tab active state color-only; 11px text at arm's length in a van (A11Y-005..012) · card shadow at 4% opacity visually absent (VISUAL-013) · settings reachable on phone only via 40px header gear.

**What is clean (explicit):** RTL logical-properties discipline 100% (zero physical properties, `<bdi dir="ltr">` on every number/phone) · focus traps + return-focus on all five dialogs · `prefers-reduced-motion` fully honored · F17 contrast suite green (21 pairs × 2 themes) · unique per-route titles · `aria-hidden` on content behind sheets · 16px inputs (no iOS zoom) · zero TODO/mock/`any` in the `(sales)` tree · all 14 endpoints admin-gated 14/14 · `won` evidence-only doubly enforced · `lead_event` append-only trigger-enforced.

---

## 4 · Infrastructure / governance findings

**INF-1 (P1) · v1's governance tail is unmerged.** Brain PR **#139** (Amendment A recorded, v1 implementation plan, GAP-029/030, lessons 2026-08-18) and Sales-Machine PR **#5** (U-011/012/013) are draft, unmerged; the v2 masterprompt cites their contents as canonical facts. Verified: the content exists on branch `claude/caveman-mode-oenfxl` in both repos and matches the citations. Until merged, `main` disagrees with the masterprompt's fact base and v2 docs cannot reference them by stable path. → First execution step of v2: merge both (checks green), then stack.

**INF-2 (P0, standing) · GAP-029:** live-shaped Shopify Admin token in `gt-factory-os` git history (`scripts/cleanup_shopify_sku_map.mjs:73`). Not this session's work; blocks ever making that repo public. Surfaced here once, per masterprompt §9 — rotate per runbook, then strip. Not forgotten.

**INF-3 (P2) · GAP-030:** flaky e2e (`production-picking.spec.ts:95`, 5s `toHaveURL` vs `next dev` on-demand compile). Needs its own XS tranche — in the v2 plan.

---

## 5 · The admin-control table — §5 scored against reality

| §5 control | Verdict | Evidence |
|---|---|---|
| Assign/reassign — single | **PARTIAL** — drawer-only, free-text, result invisible in every list | LeadDrawer.tsx:384-407 · schemas.ts:37-39 |
| Assign/reassign — **bulk** | **MISSING** | route.ts:144-218 · LeadsTable (no selection) |
| Assignment rules (round-robin / capacity / manual) | **MISSING** — no table, no function, no setting | migrations 0318-0323 full read |
| Queue shape — daily cap per agent | **MISSING** — `PAGE=12` is render batching | TodayQueue.tsx:28 |
| Queue shape — ordering weights | **MISSING** — hardcoded twice | queries_handler.ts:50-56 · 0323:140-147 |
| SLA hours | **EXISTS** (unaudited — P1-8) | SettingsForm.tsx:74-95 |
| WhatsApp templates | **EXISTS** (3 fixed keys) | SettingsForm.tsx:52-71 · wa.ts:38-45 |
| Lost reasons — editable list | **MISSING** — hardcoded + magic string + drawer stores "אחר" | labels.ts:63-69 |
| People — who can work leads | **MISSING** — blocked on §6.1 decision + Erik account | no endpoint/page anywhere |
| Audit trail across leads | **PARTIAL** — per-lead timeline only; no cross-lead read at API or UI | queries_handler.ts:85-89 |
| Stuck / slipping view | **MISSING** — ingredients computed, never composed | 0323:78-80,187-190 |

**Score: 2 EXISTS · 2 PARTIAL · 7 MISSING.** The admin can operate, not administer. Also missing below the §5 list: org edit/merge (186 read-only orgs), duplicate confirm/dismiss ("כפול?" badge asks a question nobody can answer), lead identity-field correction (a typo'd phone is uncorrectable outside SQL), unassign as a discoverable action.

---

## 6 · What we got wrong in v1

1. **The core invariant has a second door.** "No open lead without a next touch" was enforced in `record_outcome` and forgotten in `set_lead_status('working')` — the drawer uses the second path (P0-3).
2. **We built per-assignee scoping and never plugged it in.** `?assignee=` works end-to-end server-side; zero portal callers (P0-2d).
3. **The outcome loop was built for one screen** while arming happens from two — off-queue outcomes are silently discarded, and the discard code is deliberate (`capture.clear()` on missing row) (P0-4).
4. **The stats strip was tuned for steady state** and reads 0·0·0 against the actual runtime condition (backlog clearance) (P0-5).
5. **Server defaults encode UTC**, not Israel: 06:00 UTC "09:00" drifts an hour every DST flip, and nothing skips Friday/Shabbat (P1-1).
6. **The queue was never volume-tested against its own data.** 188 leads render, but oldest-first ordering surfaces 2023 dead leads first, mobile leads list is a 19,879px scroll, and 39 uncontactable rows were left inside the working set (P0-1).
7. **v1's governance tail was left unmerged** — the facts the next session builds on live in draft PRs (INF-1).
8. **We shipped a crossing the primary user cannot find.** The ops→sales switch (tranche 163) is live in production and Tom asked for it as a missing feature the same day — "done" was verified with tsc and vitest, never with the user's eyes on a phone (P1-19).

---

## 7 · Pre-mortem — it is 2026-11 and everyone is back in WhatsApp

1. **The wall outlasted everyone's patience.** The queue never got cut to a daily commitment; 99+ new-lead cards, oldest-first, every morning. Scanning the same wall for two weeks beat the habit out of both users. (P0-1, P1-3, P1-14)
2. **Erik's leads went into a black hole.** No account, free-text assignment, no per-agent queue, no ownership column — his 40 leads vanished from Tom's view and never arrived anywhere. They stopped assigning and back-channeled in WhatsApp. (P0-2, P1-2)
3. **Missed follow-ups accumulated in silence until the overdue pile became a second wall.** No aggregate signal, no notification (Resend unwired), no stuck view — by mid-October the due-follow-up bucket was 60 deep and opening the app felt like the original problem. (P0-5, P0-6, P1-1)

---

## 8 · Status

**STATUS: PASS (audit complete).**
Files changed: this report only · Tests: none run (read-only phase; F17 suite verified green by inspection of CI history claim only — not re-run) · Contracts referenced: masterprompt v2 §§1-9, v1 plan §5-6 (LOCKED), brain CLAUDE.md evidence standard, Sales-Machine constitution · Signals: none emitted · Stop conditions: none tripped (no code written, no flags touched, PII: no lead names/phones in this report) · Tom approvals required: §6.1 A/B/C assignment decision (blocks P0-2), token changes (3 proposed by visual audit), Phase 1 plan approval (the hard gate) · Rollback: n/a (doc only) · Next handoff: Phase 1 plan (`docs/plans/2026-08-18-sales-workspace-v2-plan.md`).
