# PRODUCT DESIGN REVIEW — GT Menu Builder (Session 2, independent)

**Reviewer:** Session 2 (independent product review), 2026-10-01. **Reviewed:** Session 1's `06-decision-ready-product-spec.md` and its ledgers, against the live code, the live DB, live Shopify prices, the active Sales branches and the doctrine. Nothing was taken from Session 1 without re-checking it; the evidence is in `evidence/2026-10-01-session2-independent-checks.md`.
**Output:** this verdict and `09-final-reviewed-product-spec.md` (06 with every accepted change applied). **No Menu Builder implementation has begun.** All live access was read-only.

---

## Verdict

**PRODUCT DESIGN: PASS** — on `09-final-reviewed-product-spec.md`.

06 as written would have been **HOLD**. Two defects broke it: the drink card nested a button inside a button, which fails the spec's own accessibility criterion (AC 18), and a boot-time figures check would have stopped the API process that also runs stock, goods receipts and production. Two flows also had undefined behaviour: the customer share link, and a Builder link that outlives an order. All four are fixed in 09 (R-07, R-14, R-02, R-03). No blocker is open in 09.

**SALES FOUNDATION GATE: HOLD.**
- PR #329 (`9d423c1`) and PR #239 (`4b94597`) are open drafts, both unmerged.
- The Sales workstream's own status is `LIVE — HOLD`: the WebKit/iOS keyboard proof is still open.
- Units B to E are unspecified.
- New since Session 1: the amended 0362 schema is in production (task tables, task trigger, D17 index, `activity_required` off, 0 tasks) while its PR is an unmerged draft and the migration history has no 0362 row. The accepted Sales state therefore cannot be named yet, which is requirement G of the gate.

**Implementation stays blocked.** It needs `PRODUCT DESIGN = PASS` (reached), `SALES FOUNDATION GATE = PASS` (not reached) and Tom's written unlock (not given). The Session 3 preconditions are listed at the end of this file.

---

## Findings (KEEP · CHANGE · REMOVE · BLOCKER)

`06-blocker` = it made 06 unbuildable or wrong as written, and it is fixed in 09. **Touches Tom** = the change alters something Tom approved; he can veto it.

| # | Area | Session 1 | Verdict | What 09 does | Evidence |
|---|---|---|---|---|---|
| R-01 | Placement (MB-D01) | Deferred; three options; "one-line change" | **CHANGE** | Recommends **P3**: the Builder behind the existing order link. It reuses the same token, adds no text change and no schema change. P1 and P2 both change the first message, which has Tom-approved texts and buttons (D-028, D-033, U-051) and its Meta templates. That is more than "one line". Tom decides. | 4 `lj.order` taps → 2 live links → **0** lead orders; journey texts pinned byte for byte |
| R-02 | Builder link (IC-1 `lead_link.purpose`) | New link purpose; link survives orders | **REMOVE** | The Builder runs on any live lead link (`/portal/builder/<token>` next to `/portal/lead/<token>`). State is keyed by `lead_id`. The link closes at the first order, exactly as today. Sales keeps seeing the menu in the drawer. This drops a Sales-lane schema change and a forwarded link that could place a second order. | `closeLinks` closes every link of the lead (`lead.ts:220,295`); every wake-up step mints a fresh link (`wake.ts:204`) |
| R-03 | Existing customers (tile, `/portal/builder` cookie path) | In V1 | **REMOVE → V1.1** · touches Tom | V1 serves leads only. Customers come back with Unit B/C (org-level events, the expansion design). | The goal is Lead → First Order. Four problems in the customer path: 04 and 06 contradict each other on the customer's starting set; a customer send completes a real order (invoice and LionWheel within seconds), not a draft; a customer has no lead, so DR-06 cannot be met; the share link is undefined for a cookie. Only 4 portal orders exist so far. |
| R-04 | Segmentation, eligibility, fast path (MB-D02) | No questionnaire; context from the campaign; fast path | **KEEP** | The fast path uses the same token into the lead catalog | — |
| R-05 | Discovery model (MB-D06) | 4 groups, anchors, curated pre-selection, consequence chip, no filters | **KEEP** | — | 48 drinks = 17 + 16 + 10 + 5, checked against the figures file |
| R-06 | Money while building | "Money appears first on the kit"; the bar shows drinks · products | **CHANGE** · touches Tom (spec §8) | The bar shows the drink count, the kit total before VAT, and the ordering page's own minimum line and meter, word for word (`לפני מע״מ · מינימום ₪800`). Cards still show only the recommended price. | The ordering portal's bar already shows its total and the meter (`index.html:579-582, 1120-1138`). Without it the opening set's ₪1,100 appears only on the kit screen, and one tap on p64 adds ₪590 unseen: the "hidden prices / checkout surprise" failure in masterprompt §32. |
| R-07 | Drink card markup | Whole card is a `<button>`, with the details button inside it | **CHANGE** · 06-blocker | The card is an `<article>`. Inside it, a toggle `<button aria-pressed>` stretches over the card, and a sibling 44 px `פרטים` button sits on the photo corner above it. Neither is nested in the other. This also saves a 44 px row on each of 48 cards. | Interactive content inside `<button>` is invalid; axe `nested-interactive` would fail AC 18. The portal card is an `<article>` (`index.html:816`). |
| R-08 | The five starting sets | Opening set tested only (₪1,100) | **KEEP** + tests | All five kits are computed and pinned in AC 6. Tom sees two of them below: chai becomes **14 × NAMASTEA** (₪130 base → ₪910), and ube spends **₪590 on matcha for one drink** (p64, 47% of the kit). Changing a set is a data change on Tom's word. | evidence §4 |
| R-09 | Quantity model (MB-D03) | Zero questions; minimum sellable units; aggregated once | **KEEP** | — | Packs and prices re-read live |
| R-10 | ₪800 round-up | Tom's priority rule; T3 described as "purée lines, then powder lines (smallest price increment first)" | **KEEP rule · CHANGE precision** | Tom's priority stays: tea 1 L, then tea 500 ml, then the rest. The exact algorithm is now specified (09 §19), with worked results. When the round-up raised concentrate or powder lines, the note adds the approved shelf-life line. | 06's T3 had two readings for one ube-strawberry drink: 12 strawberry pouches, or 3 ube bags + 6 pouches. Shelf life (approved): concentrates a year closed, powders two years, so the surplus is cash, not waste. |
| R-11 | Coverage line | `≈40 כוסות: היביסקוס-ליים, …` | **CHANGE** (copy) | `≈40 כוסות בסך הכול: …` | Without "in total" it reads as 40 cups of each drink (masterprompt §24) |
| R-12 | Equipment add-on (MB-38, pending Tom) | Optional ₪170 kit line | **REMOVE** | Struck from V1. The detail sheet keeps `דורש מקציף וחלב`. | No data on who lacks a frother; the frother is also sold alone (₪100); a non-menu upsell line in a first kit |
| R-13 | Economics (MB-D04) | RRP on the card; cost / what you keep / % behind a tap; cash on the kit | **KEEP · CHANGE copy · precondition** | The portal's plural voice: `נשאר לכם`. One footnote defines both the amount and the % the way the PDF does. Before implementation, Tom's MB-D04 approval goes into Sales-Machine `decisions.md` as an amendment of D-018. | D-018 is CONFIRMED and says the system never states the opening menu's price or the food cost per drink; the Builder states both. Doctrine changes are Tom's and dated (Sales-Machine rule 5). Figures formula: 48/48 match. |
| R-14 | Figures integrity check | "Server refuses to start on a mismatch" | **CHANGE** · 06-blocker | A CI test fails the build on a mismatch. At runtime a mismatch closes only the Builder's routes (503 + log), never the process. | `api/src/server.ts` runs stock, goods receipts, production and planning in the same process |
| R-15 | Figures file shape | Numeric fields | **CHANGE** (precision) | A strict parser for `"₪3.25"`, `"₪20"`, `"81%"`, `"₪13.70 לכוס"` | evidence §1 |
| R-16 | Finish (MB-D08) | Two layers, one action, read-only reopen after an order | **KEEP · CHANGE** | No `התפריט שלכם שמור בקישור הזה` and no read-only reopen. After an order the link shows today's "link gone" text, which already says the order is with GT. | Follows from R-02 |
| R-17 | Help door | New copy MB-30 | **KEEP · CHANGE copy** | Reuses the approved `moreInfo` reply and `שאלות ותשובות` word for word | `lead_texts.ts:32,46`; D-033 (FAQ for everyone waiting, `בהקדם`) |
| R-18 | Lead events (IC-2) | Four new `event_type`s | **CHANGE** | One type `menu_builder` with `payload.step ∈ {opened, menu_completed, help_requested}`. `builder_kit_accepted` is dropped: `draft_order` already fires on send and now carries `builder_session_id`. `opened` is written once per Builder session. | 0362 routes by payload (`button_tap.button_id`, `note.kind`): one CHECK value instead of four. Fresh links per wake step would otherwise repeat `opened`. |
| R-19 | 24 h "built a menu, did not order" task | Approved by Tom | **KEEP · CHANGE mechanics** | A trigger cannot fire on something that did not happen. So `menu_completed` inserts a `call` task due 24 h later, and a new rule cancels it on `draft_order`; `lost`, `opt_out` and `converted` already cancel. | 0362 `tg_lead_event_task`; D17 one-open-reply index |
| R-20 | `v_sales_attention.stalled` excluding Builder events | Open question | **KEEP — no change** | Builder events stay ordinary lead events | `stalled` counts any event; 616 automated `reminder_sent` rows already reset it. A lead building a menu is active. |
| R-21 | Staff surfaces (IC-3) | Drawer block, labels, rail milestone, task reason | **KEEP · CHANGE** | The read model goes through the rep read scope (D3: reps see their own leads only). The starter kit is never labelled with the existing `kit_sent` event's words. | Closure design D3; `kit_sent` is in the live CHECK |
| R-22 | Save / resume (MB-D07) | Per identity; token survives orders; lead fields stored | **CHANGE** | One session per lead, opened from any live link of that lead; it ends at the first order. The three lead fields live only in the page until send and are never stored in the session (a forwarded link must not show them). | R-02; masterprompt §23 |
| R-23 | Analytics (MB-D10) | `builder_event`, fixed taxonomy, success on the lead | **KEEP** | Customer branch removed (R-03) | — |
| R-24 | Architecture (MB-D11) | Inside `api/src/portal`; flag `builder_allowlist` | **KEEP · CHANGE** | Flag `customer_portal_live.value.builder` = `false` · `true` · `[phones]`, because lead routes check `enabled` only and have no customer allowlist | `routes.ts:308,319` |
| R-25 | Microinteraction `navigator.vibrate(8)` | Included | **REMOVE** | — | Masterprompt §32: technically interesting, no customer value |
| R-26 | Drink data in code vs a planner table | Code, Tom-verified | **KEEP** | Session 2 drafted the 48-row table (evidence §3); it still needs Tom's check (U-MB-2) | A planner table before the first verified version is speculative |
| R-27 | Governance scope | Not examined | **KEEP** | No new-module declaration needed: Amendment A (approved 2026-08-17) covers the journey's interactive catalog. Two doctrine records are Session 3 preconditions (R-13; the August "no quantities" line superseded by MB-D03). | brain `docs/decisions/modules/sales-declaration.md` |
| R-28 | Dependency ledger currency | Heads `ff69e3c` / `1ba2c98`; DL-14 "FROZEN" | **CHANGE** | Ledger refreshed: new heads, 0362 schema in production, outreach flag reported `true`, IC-1 withdrawn, IC-2 reshaped, DL-20 (doctrine records) added | evidence §6 |
| R-29 | Context transport (DL-19) | `?c=` on the link; three vocabularies | **CHANGE** | Context is read on the server from the lead's latest `auto_message{kind:'first_menu'}` `payload.menu` (`matcha`, `tea`, …). With none, `opening`. `?c=` only overrides it for a future campaign entry. No change to Sales link minting; every fresh wake-up link carries the context. | Live payloads `{"kind":"first_menu","menu":"matcha"}` (2026-09-30) |

## What touches Tom's approvals (veto any line)

1. **R-03:** existing customers leave V1. If Tom keeps them, 09 needs three additions: the customer's starting set (opening set or derived from history), a share action without a token, and a CRM surface on the org.
2. **R-06:** the bar shows the running total and the ₪800 meter, as the ordering portal already does.
3. **R-12:** the ₪170 matcha-kit add-on is struck. It was pending his word anyway.

Unchanged and confirmed by Session 2: the zero-question kit, Tom's round-up priority, the four economics figures, the 24 h task, the two-layer finish, the five starting sets.

## Observations outside the Builder (recorded, not chased)

- The 0362 schema and its task trigger are live in production while PR #329 is an unmerged draft, and the Sales record says no production migration happened. The Sales lane should reconcile its record.
- The Sales workstream reports `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED=true` on Railway. Brain and ledger texts still say the flag is frozen or false.
- ARCHIVED Shopify products share three 1 L concentrate SKUs at ₪139.

## Session 3 entry checklist (nothing here starts before the gate)

1. `SALES FOUNDATION GATE: PASS` from a FINAL SALES RECONCILIATION PASS against the merged Unit A code. Spec first, code after.
2. Tom's written unlock.
3. Placement decided (R-01).
4. U-MB-2: the drink table (evidence §3) verified by Tom, including p12, p33 and p36.
5. Sales-Machine `decisions.md` records the D-018 amendment and the supersession of "no quantities" for the Builder (DL-20).
6. Copy batch (09 §33) approved into the customer-portal register.
7. The Sales lane accepts IC-2 (one event type plus two trigger rules) and IC-3 (drawer block). IC-4 is Builder-owned.
