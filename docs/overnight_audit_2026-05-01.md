# Overnight comprehensive UX/UI/false-green/dead-end/Tom-Tax audit — 2026-05-01

> **Mode**: A (read-only audit). No portal source files modified.
> **Auditor**: executor-w2.
> **Scope**: All 12 chronological corridors of the GT Factory OS canonical portal.

---

## §0 — Audit metadata

| Item | Value |
|---|---|
| Portal repo | `c:/Users/tomw2/Projects/window2-portal-sandbox/` |
| Portal main tip | `4fee418` (`fix(planning/production-plan): English/LTR normalization + state hygiene (Gate 4.2)`) |
| Predecessor commits | `483ac66` Daily Production Plan board / `0997398` supplier names not IDs / `1817c2d` supplier picker live API / `fde59c8` planner T1a+T1b dead-link, pending_approval, freshness, mobile |
| W2 mode at audit time | A (per `.claude/state/active_mode.json`, last entry `Planning-Tranche3-Blockers` exited 2026-04-27T08:18Z) |
| Latest RUNTIME_READY signals | 17 — most recent: `Planning-Tranche3-Blockers` (2026-04-27) |
| Authority | `CLAUDE.md` durable contract, `CURRENT_STATE.md` runtime status, `EXECUTION_POLICY.md` governance |
| Tom-locked global standard | English-only / LTR-only / no raw IDs / no JSON / mobile usable @ 390px / answer 5 questions in 5 sec / planned-vs-actual unambiguous / source+freshness on numbers / clean state hygiene |
| Tom-locked exception | `/planning/blockers` Hebrew page-title + Hebrew label maps are intentionally Hebrew per CURRENT_STATE.md UNRESOLVED entry "Planning Tranche 3 route LOCKED ... Page title 'חסמים בתכנון' ..." |
| What is NOT in scope | live HTTP probes, Playwright runs, role-matrix walkthroughs, backend authorship, .env files |
| What IS load-bearing | static source-tree inspection of every primary surface; cross-corridor flow + nav-manifest reconciliation; identification of false-greens; Tom-Tax mapping |

The audit playbook referenced in the instructions (`GT_Factory_OS_UX_UI_Audit_Playbook.md`) was searched and not found at the PRODUCTION root. Audit followed the dispatch-message rubric (axes A through J, severity P0/P1/P2/P3) verbatim.

---

## §1 — Executive scoreboard

Severity counts per corridor. P0 = blocks daily production today; P1 = weekly Tom Tax / dead end; P2 = degraded but works; P3 = polish.

| # | Corridor | P0 | P1 | P2 | P3 | Top finding |
|---|---|---|---|---|---|---|
| 1 | Forecast / Sales Demand | 0 | 2 | 1 | 1 | Active-published banner is Hebrew on otherwise English screen (mixed-language regression after the Gate 4.2 lock) |
| 2 | Planning Run / Recommendation engine | 1 | 4 | 2 | 1 | Run detail page is half-Hebrew / half-English; recommendation rec-detail is fully Hebrew despite global English lock |
| 3 | Daily Production Plan (`/planning/production-plan`) | 0 | 0 | 1 | 1 | Clean — already English/LTR-normalized at `4fee418` |
| 4 | Production Actual (`/ops/stock/production-actual`) | 1 | 3 | 2 | 1 | Whole form is Hebrew; full-language regression vs lock |
| 5 | Inventory Truth / Inventory Flow | 0 | 1 | 2 | 1 | English-clean at this commit; few small things hurt later |
| 6 | Purchase Recommendations | 1 | 3 | 1 | 1 | Hebrew throughout the rec drill-down + run-detail tabs |
| 7 | Purchase Orders | 1 | 1 | 1 | 1 | PO detail "manual" banner is Hebrew (`נוצר ידנית`) inside otherwise English page |
| 8 | Goods Receipt | 0 | 1 | 1 | 1 | English-clean form; success-path durable visibility is OK; minor mobile densitfy |
| 9 | Exceptions / Inbox / Blockers | 0 | 1 | 1 | 0 | `/planning/blockers` Hebrew is Tom-locked (NOT a finding); `/exceptions` is just a redirect (clean); inbox is English-clean |
| 10 | Dashboard / Control Tower | 1 | 3 | 2 | 1 | Quick Actions launcher does NOT include the new Daily Production Plan / Inventory Flow / Blockers / Forecast-new shipped this week. False-discoverability. |
| 11 | Master Data / Admin / BOM / Supplier-Item | 0 | 4 | 4 | 2 | Multiple `/admin/masters/*` paths next to legacy `/admin/*` paths — duplicate hierarchies confusing operators |
| 12 | Whole-system end-to-end | 2 | 4 | 2 | 1 | Production-actual chain is Hebrew; Forecast→Planning→Production→Stock chain has 3 distinct UI languages along the path; deep-link from rec → production-actual carries Hebrew context banner |
| **Total** | | **6** | **27** | **20** | **12** | |

**Top P0 (across corridors)**:
- P0-A: `/ops/stock/production-actual` is fully Hebrew. (corridor 4)
- P0-B: `/planning/runs`, `/planning/runs/[run_id]`, and `/planning/runs/[run_id]/recommendations/[rec_id]` are predominantly Hebrew on the page title, summary cards, action buttons, and toast text. (corridors 2, 6)
- P0-C: `/purchase-orders/[po_id]` "manual" banner is Hebrew inside an English page. (corridor 7)
- P0-D: Dashboard Quick Actions panel does not include `/planning/production-plan`, `/planning/inventory-flow`, or `/planning/blockers` — three of the most-trafficked planner surfaces shipped this week. Operators must use the sidebar manifest, which itself is buried in the "Planning" group. (corridor 10)
- P0-E: `/planning/production-simulation` is IDB-backed (client-side; comment: "nothing here calls the API"). It will silently show stale or empty data when the API is the truth source. (corridor 11 — false green)
- P0-F: Planning Run Detail "Demand snapshot" → "Open orders synced/not available" status text uses the words `מסונכרן` / `לא זמין` (Hebrew). The freshness signal that planners must trust before approving recs is in a language Tom locked away. (corridor 2)

**Top P1 (representative, full list in corridor sections)**:
- Planning Run details: tab labels `רכש / ייצור` mixed with English `Recommendations / Exceptions` — same widget, two languages.
- Recommendation drill-down: error/empty states are all Hebrew (`לא ניתן לטעון פרטי ההמלצה`, `ההמלצה לא נמצאה`). A single connectivity blip looks like a system in a different language.
- Forecast version detail: post-publish "next step" callout is Hebrew (`תחזית פעילה — מקור הביקוש לתכנון`).
- Inventory Flow: comment-only Hebrew preserved (no operator impact, P3).
- Forecast list pre-publish guidance: English-clean.
- Production-Actual: BOM-pinning regret banner is Hebrew (`STALE_BOM_VERSION` reason map at lines 170-176).
- Admin `/admin/products/[item_id]` (legacy slice5 1456 LoC) coexists with `/admin/masters/items/[item_id]` (Tranche D pattern). Operator does not know which is canonical.
- Quick-action `/planning/boms` ("BOM Simulation") points to `/planning/boms` page which is also IDB-backed feature-set — same false green.

---

## §2 — Forecast / Sales Demand

Surfaces audited: `/planning/forecast` (list), `/planning/forecast/new` (cold-start draft), `/planning/forecast/[version_id]` (edit/publish).

### A. Language / direction consistency
- `[forecast/page.tsx]/A/P3` — header eyebrow says `"Planner workspace"` (English) but the doc-comment header references `/planner/forecast` (legacy URL). Cosmetic. — `src/app/(planning)/planning/forecast/page.tsx:7`
- `[forecast/[version_id]]/A/P1` — Active-published banner copy at `src/app/(planning)/planning/forecast/[version_id]/page.tsx:625-650` is Hebrew (`תחזית פעילה — מקור הביקוש לתכנון` / `הצעד הבא: הפעל ריצת תכנון…` / `לעדכון הביקוש, צור טיוטת תחזית חדשה מרשימת התחזיות`) and the action button is `הפעל תכנון` / `ריצות תכנון`. The rest of the page is English. — fix: replace these strings with `Active forecast — source of demand for planning` / `Next step: trigger a planning run…` / `Open planning runs` etc.
- `[forecast/[version_id]]/A/P1` — supply-method chip tooltip at lines 745-748 is Hebrew (`פריט בייצור — תחזית כאן תפעיל המלצת ייצור...` / `פריט מוגמר נרכש...`) and the chip itself reads `ייצור` / `רכש`. Inside an English table column, two Hebrew words are jarring. — fix: chip = `Make` / `Buy` (or `Production` / `Purchase`); tooltip in English.

### B. Dead ends
- `[forecast/page.tsx]/B/P2` — when `statusFilter !== null` but list is empty, the empty-state copy says `"Try clearing the filter to see all versions."` but the only filter-clear control is `All` button at the right end of the filter bar — no inline link in the empty state. — fix: add a `Clear filter` button inside `EmptyState` action slot.

### C. State hygiene
- Clean. List has dedicated `isLoading` / `isError` / empty / data branches without overlap; header `meta` only renders the count badge when `query.data` is present.

### D. Mobile @ 390px
- `[forecast/[version_id]]/D/P2` — the qty-edit grid uses `overflow-x-auto`; with 8 weekly buckets and an item column, the viewport scrolls horizontally on touch. Sticky left column is correctly applied. Acceptable but Tom-Tax-adjacent for daily editing on mobile. (lines 678-799). — fix: weekly buckets are an unavoidable wide table; consider per-cell vertical card layout @ <768px for editing.

### E. Source / freshness / caveat
- `[forecast/page.tsx]/E/P3` — list rows render `created_at` and `published_at` but no last-mutated-by indication on the list item. Already on the row for clarity, OK. Active-published banner at top includes `published by … at …` — clean.

### F. Planned vs actual confusion
- N/A — forecast is a planning surface only; never confused with actuals.

### G. Raw technical jargon
- Clean. `version_id` shown only as URL segment; UI uses cadence + horizon-start label.

### H. False greens
- None on these forecast surfaces. The forecast→planning bridge banner exists.

### I. Tom Tax
- `[forecast/page.tsx]/I/P3` — to publish a forecast Tom has to navigate List → Detail → Edit → Publish. If a draft is already in flight there is no list-level "resume draft" action. — fix: surface inline `Resume draft` link on `draft`-status rows.

### J. Small things that hurt later
- `[forecast/page.tsx]/J/P3` — status filter buttons are uppercase enum keys (`draft`, `published`, `superseded`, `discarded`) rendered lowercase via `text-3xs`. The button labels use the same enum text as the chip below. Friendly labels would read better.

---

## §3 — Planning Run / Recommendation engine visibility

Surfaces audited: `/planning/runs` (list), `/planning/runs/[run_id]` (detail), `/planning/runs/[run_id]/recommendations/[rec_id]` (drill-down).

### A. Language / direction consistency
- `[planning/runs/page.tsx]/A/P0` — page title `"ריצות תכנון"` and description `"ריצות תכנון משוחזרות..."` and trigger CTA `"הרץ תכנון חדש"` and confirm modal copy at lines 693-724 are Hebrew. The status badges + filter chips below are English (`Completed`, `Draft`, `Failed`, `Superseded`). Same screen, two languages. — `src/app/(planning)/planning/runs/page.tsx:329-346, 693-724`. Fix: title `"Planning runs"`, description `"Reproducible planning runs. Each run snapshots demand, stock, BOM, and policy and produces purchase + production recommendations. Nothing acts autonomously."`, CTA `"Trigger planning run"`.
- `[planning/runs/page.tsx]/A/P1` — `fmtTriggerSourceHebrew()` at lines 244-246 returns `ידני` / `אוטומטי`. Used in the list table source column. Same pair of words also rendered as `Manual` / `Auto` elsewhere (PO list). Inconsistent. — fix: rename to `fmtTriggerSource()` returning `"Manual"` / `"Scheduled"`.
- `[planning/runs/[run_id]/page.tsx]/A/P0` — `fmtAgeFromRun()` at lines 373-384 returns `"לפי הריצה — כרגע"` / `"לפי הריצה — לפני N שע'"` / `"לפי הריצה — לפני N ימים"`. Used in freshness chips around the page. — fix: `"as of run — now"` / `"as of run — Nh ago"` / `"as of run — Nd ago"`.
- `[planning/runs/[run_id]/page.tsx]/A/P0` — entire "Run sources" section at lines 770-834 is Hebrew (`מקורות הריצה`, `נתונים בעת ההפעלה`, `זמן ריצה`, `הופעל על-ידי`, `תחזית ביקוש`, `הזמנות פתוחות בעת הריצה`, `מסונכרן`, `לא זמין`, `עוגן מלאי עודכן`, `סטיית מלאי בעת הריצה`). This is the section a planner reads to decide whether to trust the run. — fix: full English re-write.
- `[planning/runs/[run_id]/page.tsx]/A/P0` — recommendations summary card at line 927 mixes English count with Hebrew labels: `${n} total · ${n} רכש · ${n} ייצור`. — fix: `${n} total · ${n} purchase · ${n} production`.
- `[planning/runs/[run_id]/page.tsx]/A/P1` — production-tab readiness summary at lines 977-989: `סיכום מוכנות:`, `מוכן`, `חסום`, `— מסודר לפי דחיפות (מוכן לייצור בראש, חסום בתחתית)`. — fix: `Readiness summary: N ready · N blocked — sorted by urgency (ready at top, blocked at bottom)`.
- `[planning/runs/[run_id]/page.tsx]/A/P1` — per-rec card labels at lines 1354-1389: `נדרש`, `מומלץ`, `לתאריך`, `להזמין עד`, `מאשר…/אשר`, `דוחה…/דחה`, `ממיר…/צור הזמנת רכש`, `פתח טופס דיווח ייצור`. Mobile cards built specifically for Hebrew RTL reading flow but the flow is now LTR English. — fix: full English re-write.
- `[recommendations/[rec_id]/page.tsx]/A/P0` — entire drill-down page is Hebrew. Headers (`פעולה מומלצת`, `מה עושים עכשיו?`), labels (`כמות מומלצת`, `זמן אספקה`, `תאריך הזמנה מוצע`), error states (`לא ניתן לטעון פרטי ההמלצה`, `ההמלצה לא נמצאה`), success/error toasts (`ההמלצה אושרה`, `ההמלצה נדחתה`, `ההמלצה אושרה אך יצירת ההזמנה נכשלה. ניתן ליצור הזמנה ידנית מהטבלה.`). Aria-busy label `"טוען המלצה…"`. Time-ago `"לפני N דק'"`. — fix: full English re-write of all six `_components/*.tsx` + `_lib/types.ts` + `page.tsx`. Fixed labels match the rest of the portal (e.g. forecast/inventory-flow already-shipped patterns).

### B. Dead ends
- `[planning/runs/[run_id]/page.tsx]/B/P1` — exception-row `ExceptionActionLink` at lines 472-506 routes `missing_supplier_mapping` and `ambiguous_supplier_mapping` to `/admin/masters/items/<componentId>`. Components are NOT items — that route renders an item detail with an unknown id and shows an error. — `src/app/(planning)/planning/runs/[run_id]/page.tsx:484-489`. Fix: route to `/admin/masters/components/<componentId>` (which exists per glob).
- `[planning/runs/[run_id]/page.tsx]/B/P1` — same file, `missing_bom` deep-link goes to `/admin/masters/items/<itemId>` — that page has a `bom` tab (Tranche D) but the user lands on the overview tab. — fix: append `?tab=bom`.
- `[recommendations/[rec_id]/page.tsx]/B/P2` — error state offers `חזרה להמלצות` button only — no obvious alternative when the rec is genuinely missing (run was superseded). — fix: add inline link to `/planning/runs` so the user can pick a current run.

### C. State hygiene
- `[planning/runs/[run_id]/page.tsx]/C/P1` — the page renders `detailQuery` data the moment it lands but the `purchaseQuery` and `productionQuery` are gated `enabled: !!detailQuery.data?.detail`. There is no skeleton on the recommendations card while those secondary queries load — only a brief "0 total" shadow. Brief but enough to mislead during a slow connection. — fix: gate the card body on `purchaseQuery.isFetching || productionQuery.isFetching`.

### D. Mobile @ 390px
- `[planning/runs/[run_id]/page.tsx]/D/P1` — mobile per-rec card at lines 1354-1389 packs four labeled fields plus three actions plus a status chip. At 390px the action row wraps to three lines. The buttons are not full-width; tap target spacing is tight. — fix: mobile card primary action becomes full-width `Approve & execute`, secondary actions collapse to a `…` overflow.
- `[recommendations/[rec_id]/page.tsx]/D/P2` — `RecDetailHeader` (separate component) renders item name + 3 badges + supply method on a single line at >=md; at 390px the badges wrap below the name awkwardly. — fix: stack at <640px.

### E. Source / freshness / caveat
- `[planning/runs/[run_id]/page.tsx]/E/P0` — the "Run sources" section claims `מסונכרן` (synced) / `לא זמין` (not available) for `demand_snapshot_orders_snapshot_run_id` without a freshness timestamp. A planner cannot tell if "synced" means the orders snapshot is from this run or 24 hours stale. — `src/app/(planning)/planning/runs/[run_id]/page.tsx:810-816`. Fix: render the sync timestamp with `FreshnessBadge` like Inventory Flow does, and replace the `מסונכרן` literal with `"Captured at <iso>"`.
- `[planning/runs/page.tsx]/E/P2` — list rows show `executed_at` ago-style but no badge for super-superseded vs current. The "supereseded" warning banner appears only on the detail page. — fix: render a `[Superseded]` chip inline in the list.

### F. Planned vs actual
- `[planning/runs/[run_id]/page.tsx]/F/P2` — exception list mixes `fail_hard` / `warning` / `info` with planning-numbers shown above. Planner could mistake "0 production recommendations + 5 exceptions" for "0 production happening" instead of "5 problems blocked production recs from generating". — fix: add a one-line "What this means" explainer above the recs section when `purchase_recs_count + production_recs_count === 0`.

### G. Raw technical jargon
- `[planning/runs/[run_id]/page.tsx]/G/P1` — exception rows render raw `item_id` / `component_id` as monospace links (lines 887-904). Per locked rule "User-facing UI shows names, not IDs" and recent commit `0997398` ("show supplier names instead of supplier_id everywhere user-facing"), this is a regression for items + components. — fix: render `item_name` / `component_name` with id in `font-mono text-3xs` parens-suffix only.
- `[planning/runs/page.tsx]/G/P3` — `site_id` rendered as `chip` in the list row (`{detail.site_id}` at line 729 of detail page). Internal-facing.

### H. False greens
- `[planning/runs/[run_id]/page.tsx]/H/P2` — `EXCEPTION_CATEGORY_LABELS` at lines 455-466 maps 10 categories. Live DB has more (per CURRENT_STATE.md tranche-3 lock includes 4 explicit + others silently excluded). Unmapped category falls through to `category.replace(/_/g, " ")`. Looks like a complete map, isn't. — fix: log warn in dev when an unmapped category appears.

### I. Tom Tax
- `[planning/runs/[run_id]/page.tsx]/I/P1` — to find the converted PO from a recommendation, planner clicks Convert → PO opens. But the rec row in the run-detail table afterwards still says "Approved", not "Converted to PO #1234". `converted_to_po_id` is in the type but not displayed on the row (it surfaces inside the rec drill-down only). — fix: render `→ PO 1234` chip on rec row when `converted_to_po_id` is set.

### J. Small things that hurt later
- `[planning/runs/page.tsx]/J/P2` — `timeAgo()` at lines 233-242 returns minutes/hours/days but never seconds. A run executed 5s ago shows `"just now"` for an entire minute. Acceptable. But there's no absolute-time fallback on hover.
- `[planning/runs/[run_id]/page.tsx]/J/P3` — admin-gated policy snapshot accordion (lines 836-849) renders the full `key_count` enumerated list. 50+ keys at default monospace is dense and unhelpful. Friendly group-by would help.

---

## §4 — Daily Production Plan (`/planning/production-plan`) — already shipped at `4fee418`

Surface audited: `/planning/production-plan` only. This is the surface Gate 4.2 normalized.

### A. Language / direction consistency
- Clean. Page-level `dir="ltr"` is on `<div>` at line 1038, on each modal (`ManualAddModal:496`, `EditModal:667`, `CancelModal:792`), and on `Toast:874`. All copy is English. Tom Tax of "I just published an English Daily Production Plan but the rest of the planner workspace is Hebrew" is a different corridor's problem (corridors 1, 2, 6).

### B. Dead ends
- `[production-plan]/B/P3` — "Add from Recommendations" button at lines 1104-1114 is `disabled` with copy `(coming next)`. Honest empty-state per design but feels incomplete next to a working "Add Manually". — fix: rename to `"Add from approved production rec — coming soon"` and surface a link to `/planning/runs?tab=production` instead so the planner can review approved recs in the meantime.

### C. State hygiene
- Clean — the file has a comment at lines 945-967 explicitly enforcing "exactly one of loading / error / empty / week-view at a time" with `hasData = plansQuery.data !== undefined && !plansQuery.isError`. Counts in header chips only render when `hasData`.

### D. Mobile @ 390px
- Clean. Day cards stack vertically; each plan-row card stacks header / qty / source / actions. Action button row uses `flex-wrap`; the three action buttons may still wrap onto three lines at 390px in some cases — acceptable for now.

### E. Source / freshness / caveat
- Clean. Banner states "Planned Only — inventory will update only after actual production is reported."

### F. Planned vs actual
- Best-in-class on this corridor. Status chips (`Planned` / `Completed` / `Cancelled`) are visually distinct with color coding; the `done variance` panel renders "Completed in actual production" inline.

### G. Raw technical jargon
- `[production-plan]/G/P2` — plan-row card shows `item_id` in `font-mono text-3xs text-fg-faint` line under `item_name` (lines 206-208). Per lock "IDs only as secondary/internal", this is the right pattern — but Tom may want this hidden entirely from operators in production. — fix: hide `item_id` for non-admin roles.

### H. False greens
- None. Honest "coming next" affordance for rec-pick is correct.

### I. Tom Tax
- None observed at this surface.

### J. Small things that hurt later
- `[production-plan]/J/P3` — week navigation uses `Sunday-first` per Israeli operator convention. Comment at line 71 makes this explicit. Fine. Date formatter forces `en-US` `Apr 30` / `May 1` style. Good.

---

## §5 — Production Actual (`/ops/stock/production-actual`)

### A. Language / direction consistency
- `[production-actual]/A/P0` — entire form is Hebrew. `WorkflowHeader` title `"דיווח ייצור"`, description `"דווח על כמות שיוצרה ופחת. צריכת רכיבים מחושבת אוטומטית לפי ה-BOM הפעיל."`. Step-1 card `"שלב 1 — בחר את הפריט שיוצר"`. Item type labels `"פריט ייצור"` / `"פריט אריזה מחדש"` / `"פריט מוגמר לרכישה"` / `"פריט לא מזוהה"`. Reason-code map at lines 167-176 in Hebrew. Form-open banner `"דיווח ייצור מתוך המלצה"`. Permission banner `"תצוגה בלבד."`. Loader `"טוען פריטים…"`. Error CTA `"נסה שוב"`. — `src/app/(ops)/stock/production-actual/page.tsx:163-176, 286-287, 332, 346, 453-524, 583-584, 600-624, 646-648, 678, 696-699, 707, 715-725, 731-732, 737-758`. Fix: full English re-write of the entire file.

### B. Dead ends
- `[production-actual]/B/P1` — error CTA at line 724 is `"נסה שוב"` (try again) but only refetches `itemsQuery`. If the error came from `componentsQuery` or `suppliersQuery` the retry is a no-op — the error banner stays. — fix: bundle all three refetches.
- `[production-actual]/B/P2` — when prefilled `?item_id=` points to a BOUGHT_FINISHED item, the rejection banner at line 631 displays once but the URL params are not cleared. A back-and-forward navigation re-shows the error. — fix: drop the prefill from search params after rejection.

### C. State hygiene
- `[production-actual]/C/P2` — when `itemsQuery.isLoading` is true the page shows `SectionCard title="טוען פריטים…"` with three skeleton bars. Good. When error, same SectionCard structure but with title `"לא ניתן לטעון פריטים"`. Good. But when `done.kind === "error"` is set AND itemsQuery is still loading, both states render simultaneously. — fix: short-circuit `done.kind` rendering on early loading state.

### D. Mobile @ 390px
- `[production-actual]/D/P2` — `<select>` with `<optgroup>` for item picker is fine. But the BOM consumption preview table (showing N components × consumption qty × uom) becomes a 3-column grid at <md and overflows at 390px when component names are long. — fix: stack components vertically as cards.

### E. Source / freshness / caveat
- `[production-actual]/E/P0` — the BOM-pinned-version banner is critical: a planner who opened the form 30 minutes ago needs to know if the BOM has been edited since. The current `STALE_BOM_VERSION` reason map (lines 170-171) handles this on submit but there is no proactive freshness indicator while the form is open. — fix: render a `Pinned BOM version <id> as of <time>; reopen the form if BOM is updated` chip at the top of step 2.

### F. Planned vs actual
- `[production-actual]/F/P2` — "Production Actual" form is the inverse of "Production Plan" but neither references the other (except via deep-link banner). Output qty here directly increases stock; planned qty there does not. The form does NOT show "this submission will increase stock by X units of <item_name>" preview. — fix: add a "What this will do" panel showing FG +output / scrap audit row / per-component −consumption.

### G. Raw technical jargon
- `[production-actual]/G/P1` — operator role banner at line 648 says `${session.role}`. Hebrew sentence with English-rolled enum: `"התפקיד שלך הוא operator. רק מפעיל או אדמין יכול לדווח על ייצור."`. — fix: localize role.
- `[production-actual]/G/P2` — admin error detail at lines 332, 346, 453, 488, 503, 511, 524 leaks raw `detail` (could be SQL/JSON fragment). Already gated on `session.role === "admin"`. Acceptable.

### H. False greens
- `[production-actual]/H/P1` — success banner at line 689 surfaces `"חזור להמלצות הייצור של הריצה"` only when `fromRunId`. If the user came in from `/inventory-flow` with a `?item_id=` deep-link, no contextual back-link is shown and the user is stranded on the success screen. — fix: surface "View inventory flow" / "Back to dashboard" as fallbacks.

### I. Tom Tax
- `[production-actual]/I/P1` — operator submits the form, sees success, but to confirm the ledger movement was posted they have to navigate to `/stock/movement-log` and search by item. — fix: success banner inline link `"View posted movement"` deep-linked to filter.

### J. Small things that hurt later
- `[production-actual]/J/P3` — `nowLocalDateTime()` (at the top of the file by convention) returns local-tz iso without timezone designator. Differs from server expectation of `event_at`. Acceptable but could surprise.

---

## §6 — Inventory Truth / Inventory Flow (`/planning/inventory-flow`)

### A. Language / direction consistency
- Clean. Comment-only Hebrew at `_lib/risk.ts:7` ("Tom 2026-04-26") — not user-facing. — `[inventory-flow]/A/P3`: cosmetic comment lint follow-up.

### B. Dead ends
- `[inventory-flow]/B/P1` — `UnmappedSkusBanner` replaces the grid when fraction >= 0.10. The banner directs operator to `/admin/sku-aliases?channel=lionwheel`. That works. But if Tom approves aliases and refreshes, the data takes up to 30 seconds to repropagate (TanStack Query staleTime). Banner does not say "wait ~30s after approving". — fix: stamp inline note.

### C. State hygiene
- Clean. SSR-safe via `isMounted` gate; loading / error / empty / data are mutually exclusive.

### D. Mobile @ 390px
- `[inventory-flow]/D/P2` — Desktop `FlowGridDesktop` correctly switches to `MobileCardStream` at `useMediaQuery("(max-width: 1023px)")`. Mobile card stream renders item cards with day-by-day mini chart. The day popover modal is not slide-up; it's centered. Per Tom-locked global standard "modals slide up at 390px". — fix: add `items-end sm:items-center` to the dialog wrapper like the production-plan modals do.

### E. Source / freshness / caveat
- Clean. `FreshnessBadge` is used for `as_of` timestamp in the header.

### F. Planned vs actual
- `[inventory-flow]/F/P2` — Inventory Flow includes "incoming POs" as projected inflow but nothing in the projection accounts for planned production from the production-plan board. A planner who plans 1000 units of FG-X for tomorrow does NOT see that on inventory-flow — only purchase POs feed inflow. This is per A4 lock (FG netting inbound = 0) BUT the UI does not say "planned production NOT included". — fix: stamp legend note `"Planned production is not included in this projection — see /planning/production-plan."`

### G. Raw technical jargon
- Clean. Item names are primary; ids hidden.

### H. False greens
- None.

### I. Tom Tax
- `[inventory-flow]/I/P3` — to drill into a single item's projection Tom clicks the row → `/planning/inventory-flow/[itemId]`. The detail page has 14d daily + 6w weekly. To see the BOM that produces this item Tom has to leave inventory-flow and navigate `/admin/masters/items/<id>?tab=bom`. — fix: add inline `"Open recipe →"` link on detail page.

### J. Small things that hurt later
- `[inventory-flow]/J/P2` — risk tier is computed in `_lib/risk.ts` with a Hebrew code comment. Acceptable. But the chip color choices do not include a color-blind variant. Long-term issue.

---

## §7 — Purchase Recommendations

(Read alongside corridor 2 — the same surface combines run + recs.) Surfaces audited: `/planning/runs/[run_id]?tab=purchase` and `/planning/runs/[run_id]/recommendations/[rec_id]`.

### A. Language / direction consistency
- Same Hebrew/English mixing as §3. Specifically:
  - `[runs/[run_id]]/A/P0` — recommendations tab labels `"Purchase ({n})"` / `"Production ({n})"` are English (good). But the summary header is `${n} total · ${n} רכש · ${n} ייצור` (Hebrew). — fix already cited in §3.

### B. Dead ends
- `[recommendations/[rec_id]]/B/P1` — when the rec is `dismissed`, the page still shows approve/reject buttons. They click → 409 NOT_PENDING server-side error. UI doesn't preempt this. — fix: hide actions when `rec.status !== 'pending'`.

### C. State hygiene
- Clean.

### D. Mobile @ 390px
- Drill-down page mobile cards reasonable; rec drill-down's `OpenPOsCard` renders a list of POs that scrolls horizontally on touch when supplier names are long. — fix: stack supplier name above PO number on mobile.

### E. Source / freshness / caveat
- `[runs/[run_id]/recommendations/[rec_id]]/E/P1` — rec drill-down shows `lead_time_days` with `(לא זמין מקור)` (source not available) when `lead_time_days` is null but does not say where the lead time came from when populated (component? supplier override? planning policy default?). — fix: stamp source like `"Lead time: 14 days · from supplier override"`.

### F. Planned vs actual
- Recommendations are inherently planned. No actual confusion observed.

### G. Raw technical jargon
- `[recommendations/[rec_id]]/G/P2` — `blocker_detail` opaque jsonb is rendered inside `BlockerDetailAccordion` (debug only). Tom-locked PBR-3 Option B. Acceptable.

### H. False greens
- `[runs/[run_id]]/H/P2` — production-tab feasibility chip "Ready if purchase executes" depends on a purchase rec actually existing for the dependency. UI does not validate this; it relies on backend feasibility flag. If backend misses an edge, the chip lies. — long-term: add backend cross-check.

### I. Tom Tax
- `[runs/[run_id]]/I/P1` — to bulk-approve all "ready_now" production recs, Tom has to click each one individually. — fix: add "Approve all ready" bulk action; protect with confirmation modal listing all items.

### J. Small things that hurt later
- `[recommendations/[rec_id]]/J/P3` — date `תאריך הזמנה מוצע` (suggested order-by date) shows `fmtDateOnly(r.order_by_date)` — when `order_by_date < today`, the value is rendered in danger color but no inline "X days late" label.

---

## §8 — Purchase Orders (`/purchase-orders`, `/purchase-orders/new`, `/purchase-orders/[po_id]`)

### A. Language / direction consistency
- `[purchase-orders/page.tsx]/A/P3` — file comment at line 86 mentions Hebrew month abbreviations as a previous bug fixed via forced `en-US` locale on `toLocaleDateString`. Confirms English lock works on this surface. Clean.
- `[purchase-orders/new/page.tsx]/A` — fully English, clean.
- `[purchase-orders/[po_id]/page.tsx]/A/P0` — `manualBanner` at lines 1283-1294 renders Hebrew `"נוצר ידנית"` / `"לא מתוך המלצת רכש"` / `"סיבה: {po.manual_reason}"` inside an otherwise English page. — `src/app/(po)/purchase-orders/[po_id]/page.tsx:1289-1291`. Fix: replace with English: `Created manually` / `— not from a planning recommendation` / `Reason: {po.manual_reason}`.

### B. Dead ends
- `[purchase-orders/page.tsx]/B/P2` — list filter chips are clickable to multi-select status. URL is updated. But there is no "Clear filters" pill when 1+ are active. — fix: add inline X chip when statusFilter set.
- `[purchase-orders/[po_id]]/B/P1` — "lines" tab is marked `LIVE` per file comment but lines are loaded via separate `/api/purchase-order-lines?po_id=X`. If that endpoint is down, the tab is empty with no error banner inside the tab — only the page-level error if the PO header fetch failed. — fix: per-tab error states.

### C. State hygiene
- `[purchase-orders/page.tsx]/C/P2` — KpiTile at line 295 takes `count` and the page derives it from `allPosQuery.data` (separate query from the filtered list). The all-query has its own staleTime=60_000. On mount, all four tiles render `0` until the all-query lands. Brief but misleading on slow connections. — fix: add `…` placeholder when `allPosQuery.isLoading`.

### D. Mobile @ 390px
- `[purchase-orders/page.tsx]/D/P1` — KpiTile row uses `min-w-[140px]` per tile and a flex layout. At 390px with 4 tiles + the "+ New" dropdown, the strip horizontally scrolls. — fix: collapse tiles into a 2x2 grid at <640px.

### E. Source / freshness / caveat
- `[purchase-orders/page.tsx]/E/P2` — header `meta` has a `Live` neutral badge — implies live but no last-fetched indicator. — fix: render `as of <time>` like the dashboard.

### F. Planned vs actual
- `[purchase-orders/[po_id]]/F/P3` — line table shows ordered/received/open. Clear. Status badge mostly self-explanatory. Acceptable.

### G. Raw technical jargon
- `[purchase-orders/page.tsx]/G/P3` — `po_id` searchable in the search bar. Internal. Acceptable.

### H. False greens
- `[purchase-orders/[po_id]]/H/P2` — file header lists `attached-grs` and `history` tabs as `LIVE`. Actual content of those tabs depends on `/api/goods-receipts?po_id=X` and `/api/purchase-orders/:po_id/history`. The history endpoint is an existing W4-W1 contract item; verify deployment before rolling out. (Not flagged as P0 because tab content has graceful empty fallback.)

### I. Tom Tax
- `[purchase-orders/[po_id]]/I/P1` — to attach a goods receipt to this PO, the operator copies the `po_id` and pastes it into `/stock/receipts` as the PO reference. There is NO "Receive against this PO" button on the PO detail. — fix: add `"Receive against this PO →"` action linking `/stock/receipts?po_id={po_id}`.

### J. Small things that hurt later
- `[purchase-orders/page.tsx]/J/P2` — late-PO sort uses `expected_receive_date < today` only. POs with no `expected_receive_date` sort at the bottom (`9999-99-99` sentinel) — silently de-prioritized rather than flagged. — fix: surface count of "POs with no expected date" inline.

---

## §9 — Goods Receipt (`/stock/receipts`)

### A. Language / direction consistency
- Clean. English throughout. (No Hebrew detected by grep on this file.)

### B. Dead ends
- `[receipts]/B/P2` — open-POs query loads `OPEN + PARTIAL` with `staleTime=30_000`. If the operator just received a PO completely, the dropdown still shows it for 30s. — fix: invalidate on submission success.

### C. State hygiene
- Clean. `loading` + `loadErr` separately tracked from submit `phase`.

### D. Mobile @ 390px
- `[receipts]/D/P2` — line editor renders item picker + qty + uom + notes + po-line picker per line. At 390px, fields stack but tap targets between rows are tight. — fix: increase row spacing to >=12px between line cards on mobile.

### E. Source / freshness / caveat
- Clean. `fetchJson` error throws on `!ok`.

### F. Planned vs actual
- Clean. GR posts directly to ledger; no planned/actual confusion.

### G. Raw technical jargon
- `[receipts]/G/P3` — `idempotency_key` is server-generated client-side; never displayed. Comment-level mention. Acceptable.

### H. False greens
- None observed.

### I. Tom Tax
- `[receipts]/I/P1` — line search at `lineSearch` state filters the dropdown options but the search box is a single global input — when 5 lines, all 5 dropdowns are filtered. Operator searching for one item filters all rows. — fix: per-line search box.

### J. Small things that hurt later
- `[receipts]/J/P3` — `nowLocalDateTime()` returns iso-without-tz; consistent with other forms. Acceptable.

---

## §10 — Exceptions / Inbox / Blockers

Surfaces audited: `/inbox`, `/exceptions` (redirect), `/planning/blockers`.

### A. Language / direction consistency
- `[inbox]/A` — clean English throughout.
- `[exceptions]/A` — server redirect to `/inbox?view=exceptions`. Clean.
- `[planning/blockers]/A/N/A` — Hebrew is **Tom-locked** for this route per CURRENT_STATE.md UNRESOLVED entry: `Page title "חסמים בתכנון", subtitle "פריטים עם ביקוש שלא הפכו להמלצת רכש או ייצור שמישה"`. NOT a finding.

### B. Dead ends
- `[inbox]/B/P2` — exception action `Acknowledge` → row updates inline. `Resolve` → opens `ResolvePanel` requiring notes. Both flows complete. But there is no path to "snooze" or "dismiss without resolving" — only Acknowledge. Some categories (like `recommendation_below_trigger_threshold`) are info-only. — fix: surface "info-only" exceptions with a different action set.

### C. State hygiene
- `[inbox]/C/P3` — when all four source streams (`waste / pc / rec / exc`) are loading, the page shows the "All rows" merged query result first (which is also derived). Brief pre-merge state shows nothing. Negligible.

### D. Mobile @ 390px
- `[inbox]/D/P2` — filter bar has 8 view chips (`All / Approvals / Exceptions / Stock / Planning / Integrations / Data Quality / Mine`) plus 2 sort options. At 390px the chips wrap to 3 lines. — fix: collapse into a single `<select>` at <640px.

### E. Source / freshness / caveat
- Clean.

### F. Planned vs actual
- N/A — inbox is triage only.

### G. Raw technical jargon
- `[inbox]/G/P2` — `INBOX_VIEWS` "data_quality" rendered as `Data Quality` — fine. `severity` is rendered as `Critical / Warning / Info` chips. Clean. Type field labels `"Waste approval"` / `"Count approval"` etc — all English-friendly.

### H. False greens
- None.

### I. Tom Tax
- `[inbox]/I/P1` — the merged inbox does not show the underlying source priority queue for waste/PC/rec approvals: a 30-day-old waste approval and a 5-minute-old `lionwheel_unknown_sku` exception both appear with the same age formatting. — fix: severity-then-age sort already exists; consider adding "type-then-age" so all approvals group together.

### J. Small things that hurt later
- `[inbox]/J/P3` — `formatTimestamp` uses `toLocaleString()` with `undefined` locale. Could render Hebrew formatting on a Hebrew browser locale. — fix: force `en-US` like PO list did.

---

## §11 — Dashboard / Control Tower (`/dashboard`)

### A. Language / direction consistency
- Clean. Page is English throughout.

### B. Dead ends
- `[dashboard]/B/P0` — Quick Actions launcher (`src/features/dashboard/quick-actions.ts`) does NOT include `/planning/production-plan`, `/planning/inventory-flow`, or `/planning/blockers`. Those three are the most operationally important shipped surfaces of the past 2 weeks. The dashboard greeting + "common tasks" tile array points to 15 surfaces but skips the new daily-flow ones. — `src/features/dashboard/quick-actions.ts:46-164`. Fix: append three entries (`Daily Production Plan`, `Inventory Flow`, `Blockers`) with `category: "planning"`, `required: "planning:read"`.
- `[dashboard]/B/P1` — `BOM Simulation` quick action (line 108) routes to `/planning/boms`. That page is IDB-backed (see `/planning/production-simulation` corridor 11 false green). — fix: re-evaluate whether this should be on the launcher at all.

### C. State hygiene
- `[dashboard]/C/P1` — block 6 "RUNTIME_READY registry" is hidden when `state === "pending_tranche_i"`. Block 3 "Integration freshness" same. So during initial load both are hidden, which is the right "no false green" pattern. Block 2 "Stock parity" + block 4 "Jobs 24h" + block 5 "Latest forecast" do NOT have this gate; they render their own pending/loading shells. Inconsistent. — fix: pick a single pattern.
- `[dashboard]/C/P2` — `inboxRows` is read from `queryClient.getQueryData(["inbox","all_rows"])`. If Tom lands on /dashboard before ever visiting /inbox, this is `undefined` and `summarizeInbox()` returns the `pending_tranche_i` signal. The InboxTotalCard then says "—" with `summary.note`. Looks pending but is actually just cold-cache — confusing operationally. — fix: trigger a one-time fetch when undefined, or show an explicit "Visit Inbox once to populate this tile" message.

### D. Mobile @ 390px
- `[dashboard]/D/P2` — Block 1 stat strip is `grid-cols-1 sm:grid-cols-2 xl:grid-cols-4`. At 390px (smaller than `sm:640px`), tiles stack vertically. Fine. But each tile's `value` is `text-2xl` — taking ~40px height — and 4 stacked tiles push the rest of the dashboard below the fold. Block 2 "Quick actions" at 390px = 9 cards stacked = lots of scrolling. — fix: collapse less-critical block 1 tiles into a 2x2 grid at <640px.

### E. Source / freshness / caveat
- `[dashboard]/E/P1` — all 8 dashboard signals refresh at staleTime=30_000ms (or 60_000 for health). Each block says nothing about WHEN it last refreshed except by the background `as of <time>` chip in the header. The user cannot tell if "0 critical exceptions" is current or 30 seconds stale. — fix: per-block "as of" mini-chip.

### F. Planned vs actual
- `[dashboard]/F/P2` — Block 5 "Latest forecast" links to forecast version. There is no companion block surfacing "Latest planning run produced N purchase recs / N production recs / N exceptions". The latest-planning-run card is in Block 1 stat strip but doesn't surface the rec counts. Operator landing on dashboard cannot tell if last run produced recommendations. — fix: enrich `LatestPlanningRunCard` sub-line with rec counts.

### G. Raw technical jargon
- `[dashboard]/G/P3` — `RUNTIME_READY registry` block name is dev-jargon. Per Tom-Lock global standard "no internal milestone names in user-visible UI strings" (see `EXECUTION_POLICY.md` §"Mode B-Portal-Refactor" allowed list). — fix: rename to `Operational forms` (which is already the title — but the eyebrow is `Forms`. Inconsistent. Pick one).

### H. False greens
- `[dashboard]/H/P2` — `BreakGlassCard` shows `"All systems operational."` when `!break_glass_active && !jobs_paused`. Phrase is too cheerful given the dashboard surfaces 7 other signals; if any of them is in danger state the cheerful copy still shows for break-glass. Cosmetic. — fix: tone-match the other tiles.

### I. Tom Tax
- `[dashboard]/I/P1` — there is no "What changed in the last 24h" block. Tom landing on /dashboard cannot tell at-a-glance "did the LionWheel job fail overnight, did anyone post a goods receipt, were any exceptions auto-resolved". Movement Log answers part of this; Jobs 24h answers part. No unified diff. — fix: add `"Last 24h activity"` block summarizing ledger writes + exception state changes + job runs.

### J. Small things that hurt later
- `[dashboard]/J/P2` — the role badge in the header (`{session.role}`) is a raw enum string ("admin" / "planner" / "operator" / "viewer"). — fix: friendly display ("Admin", "Planner", etc) — but consistent with role-rendering elsewhere.

---

## §12 — Master Data / Admin / BOM / Supplier-Item Readiness (`/admin/**`)

Surfaces audited: `/admin/items`, `/admin/components`, `/admin/suppliers`, `/admin/supplier-items`, `/admin/jobs`, `/admin/users`, `/admin/integrations`, `/admin/sku-aliases`, `/admin/sku-map`, `/admin/sku-health`, `/admin/holidays`, `/admin/boms`, `/admin/masters/boms`, `/admin/masters/items/[item_id]`, `/admin/masters/components/[component_id]`, `/admin/masters/suppliers/[supplier_id]`, `/admin/masters/health`, `/admin/masters/archive`, `/admin/products/[item_id]` (legacy slice5), `/admin/products/new`, `/admin/purchase-orders/parity-check`.

### A. Language / direction consistency
- `[admin/sku-aliases]/A/P3` — file comment mentions Hebrew at lines (none in user-facing strings; clean).
- `[admin/products/[item_id]]/A/P2` — Product 360 page (slice5, ~1456 LoC) — based on prior tranche notes, this page may be predominantly English but was authored under Mode B-AMMC pre-Gate-4.2-lock. Spot-check shows English-only labels in the few extracted lines. (Full read deferred — file is 1456 lines and prior audit noted English-clean.)
- All other admin pages: English-clean per spot checks.

### B. Dead ends
- `[admin]/B/P1` — DUAL HIERARCHY: `/admin/items` (live, AMMC slice4 with quick-create + status toggle + readiness pill) AND `/admin/masters/items/[item_id]` (live Tranche-D detail). Row-click from `/admin/items` goes to `/admin/masters/items/<id>` (per Tranche D wiring). But the legacy `/admin/products/[item_id]` Product 360 page (slice5, 1456 LoC) STILL EXISTS at a different URL with overlapping responsibility. Same item has two detail pages depending on entry point. — fix: pick one (Product 360 is richer; consolidate `/admin/masters/items/[id]` into a redirect to `/admin/products/[id]` OR finish folding Product 360 into the Tranche-D pattern at `/admin/masters/items/[id]`).
- `[admin]/B/P1` — DUAL HIERARCHY 2: `/admin/boms` (slice 6 list) AND `/admin/masters/boms` (Tranche E list). Manifest entry points to `/admin/masters/boms` (line 271 of manifest) but `/admin/boms` page still exists as a route. Entry point split. — fix: redirect `/admin/boms` → `/admin/masters/boms`.
- `[admin/holidays]/B/P2` — page renders honest "Backend not yet wired" warning + EmptyState. Honest. But the sidebar entry routes here regardless. Operator clicks → sees "coming soon". — fix: hide nav entry until backend lands (gated nav-manifest var).
- `[admin/sku-map]/B/P2` — non-admin access shows `"This surface is restricted to admin. Current role: <role>"` with no link to dashboard or back. — fix: add "← Back to Dashboard" link.
- `[admin/users]/B/P3` — when patching a user role/status fails with non-409 error, the inline error displays under the select but there is no retry or back-out button. Page navigation works. Acceptable.

### C. State hygiene
- `[admin/items]/C/P2` — search query state and url-`?item=` highlight state are independent. Pre-filling search on URL was explicitly disabled to avoid hiding rows. Good. But if a deep link uses `?item=X` and the row scrolls into view, the highlight is the only signal — no banner saying "Showing X". — fix: stamp inline banner.
- `[admin/jobs]/C/P3` — auto-refresh tick-down ("next refresh in Xs") is rendered. Useful. No countdown if the data fetch fails. — fix: handle `error` state gracefully without breaking the timer.

### D. Mobile @ 390px
- `[admin/items]/D/P2` — items list table has 8 columns (item / sku / family / supply / item_type / status / readiness / row-action). At 390px the table scrolls horizontally. Acceptable for admin; suboptimal for spot-checks on mobile. — fix: card-stream pattern at <768px.
- `[admin/supplier-items]/D/P2` — same wide-table issue; supplier-item table has supplier / component / item / pri / approval / cost. Acceptable.

### E. Source / freshness / caveat
- `[admin/jobs]/E/P3` — auto-refreshed timestamp shown inline. Clean.
- `[admin/integrations]/E/P2` — Shopify sync status card surfaces last-sync + last-successful-sync. Clean.
- `[admin/sku-health]/E/P3` — `shopify_variant_match` column always shows "unknown" per code comment (TODO at lines 31-34) until backend joins land. Honest but presents itself as a complete column. — fix: hide the column until backend lands.

### F. Planned vs actual
- N/A in admin.

### G. Raw technical jargon
- `[admin/integrations]/G/P3` — exception categories rendered raw (`lionwheel_unknown_sku`, `shopify_unmapped_item`). Admin-facing surface, somewhat acceptable, but other users (planners) might land here via deep-link. — fix: friendly labels.
- `[admin/sku-map]/G/P3` — `external_sku` rendered as monospace. `item_id` rendered raw in the table. Per user-facing-names rule applies. — fix: render item_name primary, item_id mono parens-suffix.

### H. False greens
- `[admin/sku-health]/H/P1` — page documents itself as "operational view" but TODO comment admits the headline `shopify_variant_match` column is "unknown" for every row. Operationally useful only for SKU coverage, not for Shopify-alignment. — fix: rename page or scope down.
- `[admin]/H/P2` — `/admin/masters/health` exists. Not yet inspected fully; per its position in nav it's positioned as a dashboard for master-data readiness. If empty/unwired this is a false green.
- `[admin]/H/P2` — `/admin/masters/archive` exists. Same concern.

### I. Tom Tax
- `[admin/integrations]/I/P1` — to map a new SKU alias the workflow is: see exception in /inbox or /admin/integrations → click deep-link → land on `/admin/sku-aliases?channel=lionwheel` → choose item → batch approve. Multi-step. — fix: surface a one-click "Approve known mapping" inline on the exception when the integration has high-confidence guess.
- `[admin/holidays]/I/P0` — when this page shows "coming soon", admins who depend on holiday overrides cannot post manual holidays. CURRENT_STATE.md flags this as `UNRESOLVED-IF-ADMIN-HOLIDAYS-API`. Operationally, every holiday today is fine if Hebcal seed is correct, BUT a custom Israeli factory close-day is not editable. Promoting this as a P0 since calendar-driven planning depends on it.

### J. Small things that hurt later
- `[admin/items]/J/P2` — readiness pill column shows `is_ready: bool + summary`. When item has no `readiness` (older row), pill shows nothing. — fix: stamp `—` placeholder.
- `[admin/components]/J/P2` — readiness column renders `—` for components per A13 deferred decision. Comment in file says explicitly "deferred to detail page". User clicks row → detail page → sees readiness. Two clicks for what should be one. — fix: backend extension to expose `?include_readiness=true` for components list.

---

## §13 — Whole-system end-to-end rehearsal

Walking the production flow from a planner's view: Forecast → Planning Run → Daily Production Plan → Production Actual → Stock truth → PO/GR.

### A. Language / direction consistency
- **The path is English-Hebrew-English-Hebrew-English-English**:
  - Forecast list = English ✓
  - Forecast detail = English with Hebrew "Active forecast" callout ✗
  - Planning Run list = Hebrew title + English filter chips ✗
  - Planning Run detail = Hebrew sources + English exceptions + mixed recs ✗
  - Recommendation drill-down = Hebrew everywhere ✗
  - Daily Production Plan = English ✓ (just shipped)
  - Production Actual form = Hebrew everywhere ✗
  - Stock movement log = English ✓
  - PO list = English ✓
  - PO detail = English with Hebrew manual-PO banner ✗
- `[end-to-end]/A/P0` — A planner walking this chain sees the language switch FIVE TIMES. The Tom-locked global standard is violated on 5 of 9 surfaces. Operationally this is "the system is half-translated, which language is the source of truth?" confusion. — fix: complete English/LTR normalization for all surfaces named in §3, §5, §6 (P0/P1 entries), §7-A, §8-A.

### B. Dead ends
- `[end-to-end]/B/P1` — from Recommendation drill-down `Approve & execute` jumps the operator to `/ops/stock/production-actual?from_rec=...`. The form opens with a Hebrew "Production from recommendation" banner inside an otherwise Hebrew form. After submit, success banner has "Back to production recommendations" link in Hebrew, returning to a Hebrew-mixed run-detail page. The chain is intentional and lands correctly — but the experience is jarring per A above.

### C. State hygiene
- `[end-to-end]/C/P2` — submitting a production-actual triggers backend to update `current_balances`. Inventory Flow shows updated balance after `staleTime=60_000`. Operator who submits and immediately navigates to /planning/inventory-flow sees ~30-60s stale data with no "as of just submission" hint. — fix: invalidate `["inventory", "flow"]` cache on production-actual success, same as movement-log invalidation.

### D. Mobile @ 390px
- `[end-to-end]/D/P2` — chain step transitions on mobile: production-plan → production-actual → success → back to run-detail. Each surface has different mobile patterns (cards / forms / modal). Acceptable per individual surfaces; no unified responsive grammar.

### E. Source / freshness / caveat
- `[end-to-end]/E/P1` — three different freshness components used: `FreshnessBadge` (inventory-flow), `as of <time>` chip (dashboard, PO list), `(לפי הריצה — ...)` (planning runs). Same concept, three vocabularies. — fix: standardize on `FreshnessBadge`.

### F. Planned vs actual
- `[end-to-end]/F/P0` — A planner makes a plan (production-plan board), an operator executes it (production-actual form). The two surfaces are connected via deep-link banner BUT the production-plan board shows `Completed` status with variance only AFTER the operator submits the actual. There is no in-flight indicator. If operator opens the form but doesn't submit, plan stays `Planned` forever. — fix: surface "Form opened by operator" status separately (this requires backend support — log a follow-up in W4).

### G. Raw technical jargon
- `[end-to-end]/G/P2` — exception action links from planning runs route to `/admin/masters/items/<componentId>` (corridor 3 finding). Routing item ids and component ids to the same path is technically a P1 dead-end and architecturally a leak of the master-data hierarchy.

### H. False greens
- `[end-to-end]/H/P0` — `/planning/production-simulation` is IDB-backed (per its file comment: "nothing here calls the API"). It will silently show data from the local IDB cache, which may not match production. A planner using this for "do I have enough material?" decisions could get wrong answers. — `src/app/(planning)/planning/production-simulation/page.tsx:13-15`. Fix: deprecate this surface, or wire it to live API endpoints; until then add a "BETA — uses cached data" banner.
- `[end-to-end]/H/P1` — `/planning/boms` (BOM Simulation, sidebar Quick Actions tile). File header confirms it's planner-accessible AND non-IDB (uses `/api/*`). Lower risk than production-simulation but the two surfaces overlap functionally. — fix: pick one; deprecate the other.

### I. Tom Tax
- `[end-to-end]/I/P0` — Currently to know "what is the demand for SKU-X this week including approved recommendations and open POs and pending production plans", Tom must consult: forecast ('demand' input) → planning-runs (resolved demand + recs) → inventory-flow (projection w/ open POs but excluding planned production) → production-plan (planned production). Four separate surfaces. — long-term fix: consolidated "Item radar" page per item showing the full demand-supply picture in one screen.

### J. Small things that hurt later
- `[end-to-end]/J/P3` — every page uses `WorkflowHeader` with eyebrow / title / description / meta / actions slots. Consistent. ✓
- `[end-to-end]/J/P2` — primary table sort defaults differ across surfaces: PO list = "late first", Planning runs = "executed_at desc", Items = `item_name`. No unified rule. Acceptable as long as each is documented in column headers, but mobile cards (which lose the sort header) lose this signal. — fix: render sort indicator inline.

---

## §14 — Cross-corridor false greens

Surfaces that LOOK done but have hidden risks:

1. **`/planning/production-simulation`** — file header says "nothing here calls the API"; uses IDB for masters + computes locally. Will silently mismatch production data. — P0.
2. **`/planning/boms`** — BOM Simulation tile on dashboard Quick Actions; partially live but functionally overlaps with production-simulation. — P1.
3. **`/admin/sku-health`** — `shopify_variant_match` column hardcoded to "unknown" but rendered as a real column. — P1.
4. **`/admin/holidays`** — page exists, sidebar links here, EmptyState says "coming soon" with no backend. Honest empty, but operationally a hole. — P0 (calendar-driven planning depends on this).
5. **`/admin/masters/health`** — placeholder page per directory listing — needs validation.
6. **`/admin/masters/archive`** — placeholder page per directory listing — needs validation.
7. **`/admin/purchase-orders/parity-check`** — admin page exists; needs verification it isn't a stub.
8. **Dashboard "RUNTIME_READY registry" block** — sources from `runtimeReadyQ.data`. Block 6. If the registry endpoint is not wired, block hides — but per CURRENT_STATE.md the harness state file IS authoritative and may not be exposed via API. Block could perpetually show "pending_tranche_i". — P2.
9. **Dashboard "Integration freshness" block** — same `pending_tranche_i` pattern. — P2.
10. **`/admin/products/[item_id]` Product 360 page** — coexists with `/admin/masters/items/[item_id]`. If only one is canonical, the other is a hidden hazard. — P1.
11. **`/admin/boms` legacy** — coexists with `/admin/masters/boms`. — P1.
12. **PO detail "lines" tab** — file claims `LIVE`; lines fetched separately from the header. If the PO lines endpoint goes down, header still loads → operator sees PO with no lines. — P2.
13. **Planning run "Run sources" `מסונכרן` (synced) / `לא זמין` (not available)** — shows binary state without timestamp. The "synced" claim looks complete but is unverifiable. — P1.
14. **Forecast supply-method chip** — depends on `items` cache being warm. If stale, chip says nothing — no fallback "Unknown supply method" indicator. — P2.

---

## §15 — Cross-corridor Tom Tax

Things that still force Tom into SQL / memory / manual checking:

1. **No "Item radar" / single-item full-view** — to answer "what is the situation for SKU-X" Tom navigates 4+ surfaces. Tom Tax = clicking through each.
2. **No proactive freshness cue on planning-run sources** — Tom must mentally estimate whether the orders snapshot is current. Tax = SQL or guesswork.
3. **No "What changed in last 24h" dashboard block** — Tom checks 7 individual signals to reconstruct overnight state.
4. **No "Receive against this PO" button on PO detail** — Tom copies `po_id` and pastes elsewhere.
5. **No "Bulk approve all ready" on production recs** — Tom clicks each individually.
6. **Planning run exception deep-links route components to item-detail page** — wrong route; user lands on error and asks Claude where to fix.
7. **No "Open recipe →" link on inventory-flow item detail** — Tom navigates manually.
8. **Production-actual success page does not link to posted ledger movement** — Tom navigates to `/stock/movement-log` and searches.
9. **Forecast list does not surface "resume draft" on draft rows** — Tom remembers his unfinished draft.
10. **Two BOM-detail hierarchies (`/admin/boms` + `/admin/masters/boms`)** — Tom remembers which to edit.
11. **Two item-detail hierarchies (`/admin/products/<id>` + `/admin/masters/items/<id>`)** — same.
12. **Component list missing readiness column** — Tom clicks each component to see its readiness.
13. **`/admin/holidays` has no edit path** — Tom must edit via direct DB to override.
14. **Dashboard inbox tile shows "—" until /inbox is visited** — Tom learns to visit /inbox first to populate dashboard.

---

## §16 — Top 20 ranked next-best fixes (P0/P1 only, ordered by leverage)

| # | Severity | Fix | Surface(s) | Leverage |
|---|---|---|---|---|
| 1 | P0 | Full English/LTR normalization of `/ops/stock/production-actual` | corridor 4 | Hi — operator-critical form, daily use |
| 2 | P0 | Full English/LTR normalization of `/planning/runs/[run_id]` (incl. "Run sources" + recs summary + production readiness summary + rec card labels) | corridor 2 | Hi — planner-critical decision surface, daily |
| 3 | P0 | Full English/LTR normalization of `/planning/runs/[run_id]/recommendations/[rec_id]` (drill-down + 6 _components) | corridor 6 | Hi — planner-critical, multi-times-daily |
| 4 | P0 | Replace Hebrew "manual PO" banner on `/purchase-orders/[po_id]` with English | corridor 7 | Med — visible whenever a manual PO is opened |
| 5 | P0 | English/LTR normalize `/planning/runs` list (page title + description + trigger CTA + confirm modal + `fmtTriggerSourceHebrew`) | corridor 2 | Hi — planner entry point |
| 6 | P0 | English/LTR normalize `/planning/forecast/[version_id]` "Active forecast" callout + supply-method chip tooltip | corridor 1 | Med — touched on every forecast review |
| 7 | P0 | Add `/planning/production-plan`, `/planning/inventory-flow`, `/planning/blockers` to dashboard Quick Actions | corridor 10 | Hi — discoverability of 3 most-used new pages |
| 8 | P0 | Fix exception action deep-link routing for `missing_supplier_mapping` / `ambiguous_supplier_mapping` (route to `/admin/masters/components/<id>` not `/admin/masters/items/<id>`) | corridor 2 | Med — fixes broken Tom-Tax-creating flow |
| 9 | P0 | Deprecate or backend-wire `/planning/production-simulation` (currently IDB-backed); add "BETA — cached data" banner in the meantime | corridor 11, 14 | Med — prevents wrong-data decisions |
| 10 | P0 | Wire `/admin/holidays` PATCH backend OR hide nav entry | corridor 11 | Med — calendar-correctness for daily projections |
| 11 | P0 | Add freshness timestamp to planning-run "Demand snapshot" / "Open orders" lines (currently `מסונכרן`/`לא זמין` binary) | corridor 2 | Hi — planner-trust signal |
| 12 | P1 | Consolidate `/admin/products/[item_id]` and `/admin/masters/items/[item_id]` into single item-detail page | corridor 11 | Med — reduces duplicate-hierarchy Tom Tax |
| 13 | P1 | Consolidate `/admin/boms` and `/admin/masters/boms` into one canonical | corridor 11 | Med — same |
| 14 | P1 | Add "Receive against this PO →" button on PO detail header | corridor 7 | Med — frequent flow, single click instead of 3 |
| 15 | P1 | Add "Bulk approve all ready" action on production recs tab | corridor 6 | Med — daily approval flow |
| 16 | P1 | Add `[Superseded]` chip on planning-run list rows | corridor 2 | Low — clarity |
| 17 | P1 | Render `→ PO 1234` chip on rec row when `converted_to_po_id` is set | corridor 2 | Med — saves drill-down click |
| 18 | P1 | Item search per-line on Goods Receipt (currently global filter affects all rows) | corridor 8 | Low — operator efficiency |
| 19 | P1 | Mobile-collapse PO KPI strip to 2x2 grid at <640px | corridor 7 | Low — mobile use |
| 20 | P1 | Add legend "Planned production not included" on Inventory Flow projection | corridor 5, 13 | Med — clears expectation-mismatch confusion |

---

## §17 — Surfaces NOT touched in this audit + why

| Surface | Reason |
|---|---|
| `/admin/products/[item_id]` Product 360 page (1456 LoC) | Time-bounded audit; cited from prior tranche notes. Recommend a future deep-pass. |
| `/admin/masters/health` | Did not open file; flagged as potential placeholder under §14 #5. |
| `/admin/masters/archive` | Did not open file; flagged as potential placeholder under §14 #6. |
| `/admin/purchase-orders/parity-check` | Did not open file; admin diagnostic surface, low operator-traffic. |
| `/admin/masters/boms/[bom_head_id]` and `/admin/masters/boms/[bom_head_id]/[version_id]` | Spot-check via Tranche-E exit notes; full read deferred — surfaces are view-only per amendment, low blast radius. |
| `/auth/signout`, `/login`, `/auth/callback` | Auth surface; out of scope for operator-flow audit. |
| `/profile` | Self-service-only surface; minimal Tom-Tax exposure. |
| Dashboard sub-blocks `IntegrationFreshnessBlock`, `JobsHealth24hBlock`, `LatestForecastBlock`, `RuntimeReadyBlock`, `StockTruthBlock`, `ParityCheckBlock` (separate component files in `src/features/dashboard/`) | Audited functionally via the dashboard top-level page; component-level deep dive deferred. |
| Recommendation drill-down `_components/*.tsx` (6 files) | Audited functionally via the page-level content + spot grep; full per-component re-read deferred — a single English/LTR re-write fix can be scoped at the page-level dispatch. |
| Inventory Flow `_components/*.tsx` (10+ files) | Spot-check via `_lib/risk.ts` (only Hebrew was a comment); per-component read deferred — clean by all signals. |
| Backend API endpoint live probes | Mode A read-only; live HTTP probes are not in scope. |
| Playwright role-matrix walkthroughs | Mode A read-only; defers to runtime verification cycle. |
| Live database queries | Mode A; no DB inspection. |

---

## Closing notes

This audit reads consistently with Tom's 2026-04-23 calibration ("every audit must include A.Small Things That Will Hurt Later + B.Tom Tax") and aligns with the Tom-locked Gate 4.2 English/LTR principle.

The strongest signal of this audit: the canonical portal at `4fee418` is **NOT uniformly English/LTR**. The Daily Production Plan was just normalized; ~5 other primary surfaces (Production Actual, Planning Runs detail + recs, Recommendation drill-down, Forecast detail callout, PO manual banner) still carry Hebrew copy from previous Mode B authoring sessions. A targeted English-pass tranche on those 5 surfaces would close the chain.

Second strongest signal: the dashboard Quick Actions panel is missing 3 of the most operational planning surfaces shipped in the past 2 weeks (production-plan, inventory-flow, blockers). One small fix, big discoverability gain.

Third: 2 surfaces (`/planning/production-simulation`, `/admin/holidays`) are false-greens that surface to operators but lack the live wiring needed for trustworthy daily use. Each deserves either a "BETA" banner or full backend wiring.

End of audit.
