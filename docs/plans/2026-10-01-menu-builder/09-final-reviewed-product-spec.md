# GT Menu Builder — FINAL REVIEWED PRODUCT SPEC

> **Status: PRODUCT DESIGN: PASS (Session 2, 2026-10-01) — WAITING FOR SALES FOUNDATION.** This file supersedes `06-decision-ready-product-spec.md` for implementation. It is 06 with every accepted Session 2 change applied. Each change carries its finding id `[R-nn]` from `08-independent-review.md`, where the evidence is. Text without a tag is 06 unchanged in substance.
> Tom approved 06 on 2026-10-01. Three changes here touch that approval (R-03, R-06, R-12) and are listed in `08-…` §"What touches Tom's approvals"; he can veto any of them. Implementation stays hard-blocked until `SALES FOUNDATION GATE: PASS` and Tom's written unlock.
> Precision target: an engineering team builds this without inventing product while coding. Parameters are named, with defaults. Hebrew strings are in backticks and go to Tom as one copy batch (§33).

---

## 1. Current lead journey

As reconstructed in `ground-truth.md` §1. Today, between "I want drinks" and "I ordered", the lead holds a static PDF of ≤8 drinks and then an ordering link into 40 raw SKUs. The step menu → bottles → quantities → cost happens in the lead's head or on the sales call. Live on 2026-10-01: 4 `אני רוצה להזמין` taps → 2 live links → **0 lead orders** (`evidence/…-session2-independent-checks.md` §6).

## 2. Relevant future Sales-system journey

GT Pulse Unit A (contact loop, owned tasks, event-sourced from `lead_event`): backend PR #329 at `9d423c1` and portal PR #239 at `4b94597`, both draft. The 2026-10-01 closure design (Sales-Machine `status/gt-pulse-a-2026-09-30`) adds D1–D17. The ones that bind the Builder: D3 reps read their own leads only; D6/D17 at most one open `reply` task per lead (partial unique index); D8 tasks follow the owner. The amended 0362 schema is already present in production with 0 tasks; its PR is unmerged `[R-28]`. Units B–E are unspecified. The Builder appends to the same lead and the same event log, and its tasks ride Unit A's router.

## 3. Builder placement `[R-01]`

**Recommended: P3, the Builder behind the existing order link.** Tom decides; until then the status is DEFERRED.

- **P3 (recommended).** `אני רוצה להזמין` and the order link in wake-up messages 1, 3 and 4 open the Builder instead of the bare catalog. Mechanism: the link the journey already mints opens `/portal/builder/<token>`. This is the same `customer_portal.lead_link` token; `/portal/lead/<token>` stays the catalog (the fast path). One change in Sales-owned code: the minted path, or a default view on `/portal/lead/<token>`. No WhatsApp text, button, template or schema changes.
- **P1 (own journey per campaign)** and **P2 (instead of the PDF)** both change the first message. That reopens Tom's byte-for-byte texts, D-028/D-033 (one round of three reply buttons; a URL cannot sit beside them) and the Meta templates. The Builder itself is identical in all three; only the entry differs.

The Builder works unchanged in every placement (DR-03): entry is always a live lead link, and context comes from the lead (§4).

## 4. Segmentation and eligibility `[R-03, R-29]`

- **V1 = leads only.** Eligible: a phone holding a live `lead_link` while `customer_portal_live.enabled` is true and `value.builder` admits it (§30). No lead-type logic.
- **Existing customers are not in V1** (no tile, no `/portal/builder` cookie route). They return in V1.1 with Unit B/C. Until then a phone already mapped to a customer gets its own portal link as today (D-028).
- **Context** (`tea · matcha · chai · ube · opening`) is derived on the server: the `payload.menu` of the lead's latest `auto_message{kind:'first_menu'}` event (live today, e.g. `"menu":"matcha"`). No event means `opening`. An optional `?c=<key>` on the Builder URL overrides it (only for a future campaign entry, P1). The link format needs no change and every fresh wake-up link carries the context for free.

## 5. Bypass and fast path

- `מכירים את המוצרים? ישר לקטלוג ←` is a text link at the top of BUILD from the first paint. It opens `/portal/lead/<token>` with the same token. The Builder session stays saved.
- On the lead catalog, `חזרה לתפריט שבניתם` shows only when this lead has a Builder session with ≥1 drink.

## 6. Complete customer flow

```
lead link  →  BUILD (one scrolling screen)  →  KIT ("my menu" + "your starter kit")  →  send  →  DONE
               ↑ detail sheet · my-menu sheet          ↑ edit kit · back to build
               ↓ fast path → lead catalog               ↓ share the link · help door
```

Reopening a live link of the lead returns to the last view with the last state (§25). The three lead fields are asked once, on KIT, above the send button, as the lead catalog asks them today.

## 7. Screen-by-screen mobile flow (390 × 844 reference, 320 minimum)

### 7.1 BUILD — `/portal/builder/<token>`

Top to bottom:

1. **Brand row** (scrolls away, portal `.top` pattern, 60 px): GT mark, title `בניית התפריט שלכם`. No identity line (a lead has no account name).
2. **Fast-path line** (under the title, 14 px 700, `--gt-d`, 44 px hit area): `מכירים את המוצרים? ישר לקטלוג ←`.
3. **Start banner** (`.msg` style, `--card` background, radius 16, 14 px 700, one line + one text button). Variants:
   - context `opening`: `התחלנו מתפריט הפתיחה המומלץ שלנו · הסירו, החליפו, הוסיפו` · button `להתחיל מאפס`
   - other contexts: `התחלנו מ{תפריט המאצ׳ה} · הסירו, החליפו, הוסיפו` (labels: the `lead_menus` labels verbatim)
   - a pre-selected drink dropped for availability: second line `משקה אחד לא זמין כרגע ולא נבחר` / `{n} משקאות לא זמינים כרגע ולא נבחרו`
   - resumed: `המשכנו מהביקור הקודם` (replaces the first line; no button)
   - after `להתחיל מאפס`: the banner collapses (height animates out, 250 ms) and the bar reads `בחרו משקאות לתפריט`.
4. **Group chips** (pinned row, portal `.chips` pattern, 44 px pills, counts in 12 px muted): `תה קר 17` · `מאצ׳ה 16` · `צ׳אי מסאלה 10` · `אובה 5`. Anchors, not filters: a tap scrolls to the group header (smooth unless reduced motion), and the active chip follows the scroll (IntersectionObserver on group headers). The context group comes first in the chip row and on the page.
5. **Groups**, in page order: the context group first, then `תה קר · מאצ׳ה · צ׳אי מסאלה · אובה`. Each group has a header `.sec` (26 px 800) with its selected count (`מאצ׳ה · 3 נבחרו`, or just `מאצ׳ה`). Sub-family eyebrows (12 px 800, `--terra`): `חליטות קרות` · `לימונדות` · `משקאות הדגל` · `גזוז` / `אייס מאצ׳ה` · `מאצ׳ה ספיישל` · `מאצ׳ה קוקוס` / `צ׳אי מסאלה` · `קולד פואם` / (ube: none).
6. **Drink grid**: 2 columns (gap 14 px) on a phone; 4 columns (gap 18 px) from a 640 px container; never 3 (portal rule). Order inside a sub-family follows the figures-file page order, except that at load time drinks whose products the current selection already covers move to the front of their sub-family. **Order never changes while the page is open**; only chips change live.
7. **Bottom bar** `[R-06]` (fixed, ink, radius 22, min-height 64, the portal `.bar` anatomy):
   - inline-start, a 44 px target that opens the My Menu sheet (§14): a cup glyph with the drink count `5` (the portal's `bag` badge pattern), then in the middle column the base-kit total `₪1,100` (`.num`, 17 px 800, `tween` count) over the portal's existing line `לפני מע״מ · מינימום ₪800` / `לפני מע״מ · עברתם את המינימום` and the portal's meter track (`--p` fill);
   - inline-end, the button `לערכת הפתיחה ←` (paper on ink).
   - The total is the server's `subtotal_base`: minimum sell units plus the customer's own kit edits, **before** the round-up (§17). When it is below ₪800 the meter shows the gap, and the round-up happens on KIT with its note. With zero drinks the bar reads `בחרו משקאות לתפריט`, shows no total, and the button is disabled (`aria-disabled`, `--disabled` fill).
   - The bar's `aria-label` follows the portal's pattern: `{n} משקאות, ₪{x} לפני מע״מ. חסרים עוד ₪{r} למינימום.` / `… עברתם את המינימום.`
   - Keyboard open (visualViewport shrinks >150 px): the bar hides, as in the portal.

### 7.2 Drink card (component, §9.1) `[R-07]`

**Markup:** `<article class="dcard">` containing (a) a toggle `<button aria-pressed>` whose `::after` stretches over the whole card (the stretched-target pattern), with the accessible name `הוספה לתפריט: {name}, ₪{rrp} מומלץ` / `הסרה מהתפריט: …`, and (b) a sibling `<button>` `פרטים` positioned above the stretch (`z-index`), on the photo's inline-end top corner: a paper pill, 12 px 800 text, 44 × 44 hit area. The two buttons never nest.

Size: full column width. The photo area uses `aspect-ratio: 925 / 1052` (the photo's own ratio, no cropping) and radius 24 at the top. It shows `/portal/img/d-<id>-320.webp` / `-640.webp` via `srcset`, `sizes="(min-width:1100px) 240px, 50vw"`, on the group tint (tea `#F3D9DD`, matcha `#DDEBD6`, chai `#F0E2CC`, ube `#E8DFF2`). Body (padding 12 px):

- **name** Heebo 800 17 px, 2 lines max, `text-wrap: balance`;
- **price line** 14 px 700 `.num`: `₪20 · מחיר מומלץ`;
- **consequence chip** (12 px 800, pill, min-height 24): `בבקבוק שכבר בחרתם` (`--ok-bg` / `--gt-d`) or `+ מוצר: FRESH` (`--card` / `--ink-soft`) or `+ 2 מוצרים: מאצ׳ה, מנגו`. English brand names are shown as-is in `<span lang="en" translate="no">`;
- **tags row** (11 px 800 badges, only when true): `ללא קפאין` · `ללא סוכר אפשרי`.

States: default · selected (2.5 px ink ring, ✓ pill `.got` at the photo's inline-start, photo scale 1.02) · unavailable (greyscale .5 opacity, white stamp `לא זמין כרגע`, second line `צפי 14.10` when `back_on` is set and not passed, or `בינתיים: FRESH ללא סוכר` when the planner named an alternative; the toggle is `aria-disabled`; `פרטים` stays available) · pressed (scale .97, `--d-press`).

### 7.3 Detail sheet (`#d-<id>` in the hash; bottom sheet 88dvh, radius 26/26/0/0, portal sheet mechanics)

Top: the photo (same asset, 60% width, centred, soft floor shadow), the name (26 px 800) exactly as the Canva drinks menu prints it (Tom 2026-10-01), and the sub-family eyebrow. Then, in order:

1. **What you need** (`מה צריך`): product lines with their consequence state, e.g. `FRESH · 1 ליטר` + chip (`כבר בתפריט` / `נוסף לערכה`); a two-product drink shows both lines. Equipment note when the product requires it: `דורש מקציף וחלב` (`requires_equipment`).
2. **Economics** (MB-D04) `[R-13]`: a big `₪20` with `מחיר מומלץ לצרכן · כולל מע״מ` (12 px muted). Then one 14 px line: `עלות רכיבים לכוס ≈ ₪3.25 · נשאר לכם ≈ ₪13.70 לכוס · 81%`. Then the footnote, two 12 px muted lines that carry the PDF's own definition: `נשאר לכם = המחיר פחות מע״מ, פחות עלות הרכיבים. גם האחוז מחושב כך.` · `עלות רכיבי המשקה בלבד, לפי מחירון · ללא קרח, סודה וקישוט · הערכה`.
3. **Tags**: `ללא קפאין`, `ללא סוכר אפשרי`.
4. **Primary button** (54 px pill): `הוסיפו לתפריט` / `הסירו מהתפריט`. It toggles; the sheet stays open and the card behind it updates.

No preparation steps, no recipe (masterprompt §13). Close: ✕ (inline-start, 44 px), backdrop, Esc, swipe down, back gesture (hash).

### 7.4 KIT — same page, `#kit` view (back returns to BUILD)

Top to bottom:

1. **Header**: `התפריט שלי` (32 px 800) with a check mark drawn once (`draw` keyframe, 600 ms, static under reduced motion). Sub-line 14 px muted: `{n} משקאות · {p} מוצרים`.
2. **My menu list** (layer 1): one row per drink, grouped by group with eyebrows: photo thumb 44 px, name 16 px 700, `₪20 · מומלץ` 14 px `.num`. A row tap opens the detail sheet. At the header's inline-end, the text button `עריכה` returns to BUILD.
3. **Kit header**: `ערכת הפתיחה שלכם` (26 px 800) + one 14 px line: `הכמות הקטנה ביותר שמכסה את כל התפריט. אפשר לשנות.`
4. **Kit lines** (layer 2), one per product, in the portal cart-line anatomy: product thumb (the portal's `l-`/`p-`/`o-` asset), name (GT Latin 20 px) + size; a size control for concentrates (`1 ליטר` | `500 מ״ל`, 44 px, default 1 L); a `ללא סוכר` switch (44 px) where a twin exists; the stepper (`44px | qty | 44px`, step 2 for bottles and purées, 1 for powders, `נמכר בזוגות` under bottle lines); the line price `.num` before VAT; the **coverage line** `[R-11]`, 13 px muted, `≈40 כוסות בסך הכול: היביסקוס-ליים, גזוז היביסקוס ותפוח` (up to 3 names, then `ועוד {n}`); and the portal's `+6 · ארגז` chip.
5. **Round-up note** `[R-10]` (only when applied; `.note` style, `--ok-bg`): line 1 `עיגלנו למינימום ההזמנה ₪800: הוספנו 12 × NAMASTEA 1 ליטר` (several lines are joined with ` ו־`). Line 2 appears when a concentrate line was raised: `תמציות נשמרות שנה בבקבוק סגור, בלי קירור.` When a powder line was raised: `אבקות נשמרות שנתיים.` When both: both sentences on one line. Both come from the approved claim `shelf_life`. The raised lines get a 1.2 s ring highlight on first paint.
6. **Totals** (`<dl>`): `סה״כ לפני מע״מ` · `מע״מ 18%` · `סה״כ כולל מע״מ` (26 px, counts up 250 ms), the portal's minimum meter, and the existing fine print `מחירי המחירון, לפני מע״מ`.
7. **Lead fields** (the portal's `leadForm` fieldset verbatim): `שם העסק` · `סניף או עיר` · `השם שלכם`, with the existing validation and errors. They are kept in the page only, never in the Builder session `[R-22]`.
8. **Primary button** (54 px): `לשלוח את ההזמנה · ₪1,298 כולל מע״מ` (≤360 px: `שליחה · ₪1,298 כולל מע״מ`). Below the minimum after edits it is disabled, the meter shows `חסרים עוד ₪130`, and the button `להשלים למינימום` re-runs the round-up.
9. **Secondary actions** (text, 44 px): `לשמור ולחזור אחר כך` opens the share sheet (§25) · `רוצים לעבור על זה יחד? נחזור אליכם` opens the help door (§24).

### 7.5 DONE — the portal's lead confirmation, in place `[R-16]`

The portal's done screen unchanged (`קיבלנו את ההזמנה`, counts, `פירוט ההזמנה`, share, `סיום`) with the lead line `נחזור אליכם בקרוב לתיאום המשלוח.` The order closes every link of the lead, as today (`closeLinks`). A reload, or a later open of any of its links, gets the portal's existing "link gone" state, which already says the order is with GT. Nothing in V1 reopens the menu after an order; Sales sees it on the lead (§24).

### 7.6 Progress and back behaviour

Two views and two sheets; the URL hash is the state (`#build` implicit, `#kit`, `#menu` sheet, `#d-<id>` sheet, `#help` sheet). Browser back closes the top-most sheet, then returns from KIT to BUILD, then leaves. No step counter; the bar's count and meter are the progress.

## 8. Information hierarchy `[R-06]`

BUILD: the drink (photo, name) › RRP › consequence chip › tags; the bar carries the running consequence (drinks, base-kit total, minimum). KIT: the menu › the kit lines (qty and coverage) › totals › send. The attention order is "what will I serve" → "what does it take" → "what does it cost" → "send". On cards, the only money is the RRP (a selling price). The purchase total sits in one place, the bar, labelled with its VAT basis, as on the ordering page.

## 9. Component behaviour

### 9.1 Drink card
A tap toggles selection. The selection is saved (debounced 250 ms) and the kit recomputed on the server (`POST …/kit`, §17) in the background. Chips of *other* cards and the bar total update from the response (chip fade 180 ms, total `tween`). The bar count updates immediately from local state; the total waits for the server and shows a 12 px spinner after 400 ms.

### 9.2 Consequence chip
Computed on the server per card: products required by the drink minus products already in the kit. Empty set → `בבקבוק שכבר בחרתם` (powder: `באבקה שכבר בחרתם`; purée: `במחית שכבר בחרתם`; mixed: `במוצרים שכבר בחרתם`). One product → `+ מוצר: {name}`. Two → `+ 2 מוצרים: {a}, {b}`. On a selected card the chip reads `בתפריט` with the ✓.

### 9.3 Group chips
Anchors with scroll-spy; `aria-current="true"` on the active one; they never hide cards.

### 9.4 Start banner
As §7.1-3. `להתחיל מאפס` asks nothing and can be undone: a 6 s `ביטול` toast restores the set.

### 9.5 My Menu sheet (§14)
The selected drinks, each with `הסרה` (44 px) and a 6 s undo toast; footer `{n} משקאות · {p} מוצרים` and the same `לערכת הפתיחה ←` button.

### 9.6 Kit line
The stepper counts sell units. Taking a product to 0 needs an explicit `הסרה` and a confirm line: `בלי FRESH אין: היביסקוס-ליים, גזוז היביסקוס ותפוח. להסיר גם אותם מהתפריט?` · `להסיר` · `ביטול`; removing drops those drinks from the menu. The size toggle recomputes coverage and price; the sugar-free toggle swaps the SKU.

### 9.7 Totals and meter
Server values only; the client never computes money (§17). The meter and `חסרים עוד ₪X` use the portal's existing component.

### 9.8 Sticky bar / side panel
Below 560 px: bottom bar. 560–1099 px: bar + drawer. From 1100 px: a sticky side panel, 340 px (360 px from 1280), with the My Menu list live, the base-kit total and meter, and the CTA, in the portal's side-cart style.

## 10. Key microinteractions

| Moment | Behaviour | Tokens |
|---|---|---|
| Select a drink | the ring appears, the ✓ pill pops, photo scale 1→1.02, the bar count bumps `[R-25: no vibration]` | `--d-ui`, `--spring` |
| Deselect | the ring fades, the ✓ pill scales out | `--d-ui` |
| Chips and total after a recompute | chip text crossfades 180 ms; the bar total tweens | `--ease` |
| Open detail / my-menu / help sheet | portal sheet: slide up 320 ms, scrim, handle | `--out` |
| Remove from my menu | the row collapses 250 ms; 6 s undo toast | `--d-ui` |
| Go to kit | the view slides in from inline-end 300 ms; kit lines stagger 40 ms each (max 8); the total counts up 250 ms | `--out` |
| Round-up applied | raised lines get a 1.2 s ring highlight; the note fades in | `--ease` |
| Stepper | portal stepper animation (`grow` 320 ms); the coverage text recounts | existing |
| Send | the portal send state machine (sending → pending → done) verbatim | existing |
| Completion | the header check draws (600 ms) once per session | existing keyframe |

Reduced motion: every duration .01 ms, no count-up, no stagger (portal rule). No confetti, no points, no streaks.

## 11. Loading, error, empty, resume states

| State | What the customer sees |
|---|---|
| Loading | 8 skeleton cards + a skeleton banner, `aria-busy`. Cards paint from the static drink list first; prices, chips and the bar total follow when the kit responds (portal "one reveal": ≤700 ms paint at once, else skeleton; past 2.5 s, paint without chips) |
| Link expired / used / unknown (410) | the portal's `gone()` pattern: `הקישור הזה כבר לא פעיל. אם שלחתם הזמנה, היא אצלנו, ונחזור אליכם בקרוב.` + `כתבו לנו בוואטסאפ` (lead line) |
| Builder off for this phone (`value.builder` excludes it) | 404, the portal's not-found; the lead's catalog link keeps working `[R-24]` |
| Portal closed (503) | portal C-10 text |
| Offline | banner `אין חיבור לאינטרנט. התפריט שמור, ונמשיך כשהחיבור יחזור.`; selection keeps working locally; the kit recomputes on `online` |
| Slow kit response (>2.5 s) | chips and the total stay as they were; the bar shows a 12 px spinner |
| Kit endpoint error | `לא הצלחנו לחשב את הערכה. בדקו את החיבור ונסו שוב.` · `לנסות שוב` (the last good kit stays visible, greyed) |
| Builder routes closed by the figures check `[R-14]` | 503 on `/portal/builder*` only; the page shows the portal C-10 text with the fast-path link to the catalog |
| Empty selection | bar `בחרו משקאות לתפריט`; KIT unreachable |
| Unavailable product (planner) | §7.2 states. A resumed selection that contains it drops the drink, with the banner line `{drink} הוסר: לא זמין כרגע` |
| Resumed | banner `המשכנו מהביקור הקודם`; the kit is recomputed with today's prices and availability |
| Price changed between kit and send (409) | the portal re-price flow: struck old price, badge `המחיר עודכן`, send again |
| Below minimum after edits | §7.4-8 |
| Stale tab (hidden >30 min) | the kit recomputes on return (portal rule) |
| Send outcomes | the portal lead-path table (201/409/410/422/502/503/network) verbatim |

## 12. Drinks discovery model (MB-D06)

Four groups in the lead-menu vocabulary; the context group first; the curated set pre-selected; the purchase-consequence chip; free expansions first at load; no filters, no search. Order inside a sub-family follows the figures-file page order.

## 13. Starting sets `[R-08]`

Exactly the five approved sets (D-026), pre-selected by context (figures-file page ids): `opening` 8 · 27 · 12 · 21 · 48 · 55 · 29 · 31 — `matcha` 29 · 30 · 31 · 33 · 34 · 39 · 42 · 44 — `tea` 8 · 9 · 13 · 16 · 21 · 22 · 25 · 26 — `chai` 48 · 49 · 50 · 51 · 55 · 56 · 57 · 18 — `ube` 60 · 61 · 62 · 63 · 64. They live in the drink data file; changing a set is a data change on Tom's word, with no UI.

What each set becomes as a kit at today's list prices (evidence §4; pinned in AC 6):

| Set | Base kit | After round-up | Shape |
|---|---|---|---|
| `opening` | ₪1,100 | ₪1,100 | 5 products; matcha 500 g is 54% for 2 drinks |
| `matcha` | ₪960 | ₪960 | 4 products |
| `tea` | ₪1,270 | ₪1,270 | 10 products (7 concentrates, 3 purées) |
| `chai` | ₪130 | ₪910 | **14 × NAMASTEA 1 L** (one-product menu, ₪800 rule) |
| `ube` | ₪1,255 | ₪1,255 | matcha 500 g is 47% of the kit, for one drink (p64) |

## 14. "My Menu" behaviour

The sticky bar is the menu's live summary, the sheet is its editor, and the KIT header is its presentation. The menu is an ordered list in selection order, with no cap. Above 10 drinks, a one-line note in the sheet footer: `רוב המקומות פותחים עם 4–8 משקאות` (it blocks nothing). If a drink's product goes unavailable after selection, the drink stays in the menu until the next kit recompute, which removes it with the banner line.

## 15. Quantity model (MB-D03) `[R-12]`

Zero questions. For each product P required by any selected drink: `qty(P) = unit(P)`, where unit = 2 for concentrates and purées (pairs) and 1 for powders. Then the round-up (§19). The kit stays editable; the customer's edits are kept as `kit_overrides` and survive a recompute unless the product leaves the menu.

Default packs (parameters): concentrate `1l` (`05` by toggle), purée `1l`, ube `500`, matcha `500`. The ₪170 matcha kit (`GT-MAT-KIT`, equipment, no powder) is **not offered** in the Builder in V1. The detail sheet's `דורש מקציף וחלב` covers the equipment need.

## 16. Economic presentation (MB-D04)

- Card: the RRP only.
- Detail sheet: the RRP, the ingredient cost per cup, what is left per cup, and the %, with the two-line footnote (§7.3).
- Bar: the base-kit total and the minimum, before VAT.
- Kit: cash outlay with the VAT lines and coverage.
- Never: projections, GT margins, per-customer food cost.
- Precondition `[R-13]`: Sales-Machine `decisions.md` records Tom's amendment of D-018 for the Builder (DL-20).

## 17. Calculation semantics (server-side, exact)

Inputs: the figures file `pages[id] = {cost, price, marg, prof}` `[R-15]`, stored as display strings and parsed strictly (`"₪3.25"` → 3.25 ex-VAT; `"₪20"` → 20 incl. VAT; `"81%"` → 81; `"₪13.70 לכוס"` → 13.70; anything else fails the parse). The dose table `dose[id][product] = ml | g` (DL-18). The pack table `pack[product][size] = {ml | g, catalog_key}`. List prices from `pricer.listPrices()`. The availability overlay `withAvailability`. VAT `VAT_RATE` (0.18) and minimum `MIN_ORDER_PRE_VAT` (800), both imported from `build-cart.ts`, never restated.

- `rrp(d) = price`; `cost(d) = cost`; `kept(d) = round2(price / 1.18 − cost)`; `margin(d) = round((price/1.18 − cost) / (price/1.18) × 100)`. These must equal the file's own `prof`/`marg` (verified 48/48 on 2026-10-01).
- **Integrity check `[R-14]`:** a CI test asserts the equality for every page and fails the build on any mismatch. At runtime the same check runs when the figures load. A failure logs `[portal] builder figures mismatch: <ids>` and closes only `/portal/builder*` (503). It never throws during boot and never touches other routes.
- `products(d)` = keys of `dose[d]`; `need(P) = {d ∈ selection : P ∈ products(d)}`.
- `servings(P, size) = floor(pack[P][size] / max_{d ∈ need(P)} dose[d][P])` (conservative: the largest dose among the chosen drinks); `coverage(P) = servings(P, size) × qty(P)`; shown as `≈{coverage} כוסות בסך הכול`.
- `line(P) = qty(P) × unit_price(P)`; `subtotal = round2(Σ line)`; `vat = round2(subtotal × 0.18)`; `total = round2(subtotal + vat)`: the portal's rounding verbatim.
- `subtotal_base` = the subtotal of minimum units plus `kit_overrides`, before the round-up (the bar). `subtotal` = after the round-up (KIT and send).
- Money is never multiplied or divided by 1.18 anywhere else; the RRP is displayed as stored.
- Unit prices: list prices (lead). The kit is re-priced on every recompute and on send; drift → `PRICE_CHANGED`, as the portal does.

## 18. BOM-to-cart logic

Drink → products → doses come from the Builder's drink data (DL-18, Tom-verified; Session 2's draft is `evidence/…-session2-independent-checks.md` §3). No factory BOM is read: Factory OS BOMs model production, not serving. Sugar-free: the twin SKU replaces the regular at the same dose. A two-product drink counts in both products' `need`.

## 19. Aggregation and round-up rules `[R-10]`

1. Aggregate per product across all selected drinks; never round per drink.
2. Base quantity = one sell unit per required product (§15), then `kit_overrides`.
3. **Round-up (Tom 2026-10-01, priority: tea 1 L → tea 500 ml → the rest).** Tiers: **T1** concentrate lines at 1 L; **T2** concentrate lines at 500 ml; **T3** all purée and powder lines together. While `subtotal < 800`:
   - take the first tier that has a line in the kit;
   - in it, pick the line with the fewest units added so far by this round-up; ties go to the line used by the most selected drinks, then the smaller sell-unit price, then catalog order;
   - add one sell unit to it (a pair for bottles and pouches, one bag for powders).
   Only products already in the kit are raised; the round-up never adds a product.
4. Worked results (pinned in AC 7): `chai` set → NAMASTEA 2 → 14 (₪910). One FRESH drink → FRESH 14 (₪910). `אייס מאצ'ה קלאסי` alone → matcha 2 × 500 g (₪1,180). `אייס אובה תות` alone → ube 3, strawberry 6 (₪885). `אייס מאצ'ה תות` alone → matcha 1, strawberry 4 (₪830).
5. Record `rounded_up = [{product, from, to}]` and render the note (§7.4-5).
6. If the customer edits below the minimum, the kit stays below it: send is disabled, and `להשלים למינימום` re-runs step 3 from the current quantities.
7. Pairs are enforced by the stepper and re-checked by the server (`NOT_IN_PAIRS`); the minimum by the server (`BELOW_MINIMUM`); availability by the server (`BAD_LINE`). All as the portal does today.

## 20. Authoritative data sources

`ground-truth.md` §5. Runtime inputs: the figures (a synced copy of `drinks_final_figures.json` with provenance, the CI drift check and the integrity check), the drink data file (Tom-verified), the portal catalog and pricer, the availability overlay, and the lead's `first_menu` event for context (§4). Nothing is read at runtime from Sales-Machine cards, gt-site or Canva.

## 21. Recommendation explanation

Every number a customer could question has its reason on the screen:

- the coverage line, `בסך הכול` (why this quantity);
- the round-up note and its shelf-life line (why more than the minimum unit, and why that is safe);
- `נמכר בזוגות` (why 2);
- the two-line economics footnote (what the cost and what-is-left mean);
- `מחירי המחירון` (whose prices);
- the bar's minimum line (how far from ₪800).

No hidden rounding.

## 22. Finish experience (MB-D08)

§7.4–7.5. The emotional beat is the header: the menu named and the check drawn, then the kit under it with `הכמות הקטנה ביותר שמכסה את כל התפריט. אפשר לשנות.`

## 23. Purchase handoff `[R-02, R-03, R-18]`

Send posts the kit as `lines[{key, qty, price, label}]` plus the three fields to the existing lead path, `POST /portal/api/lead/<token>/orders` (Shopify draft tagged `lead`, never completed by the system, D-029). The body gains one optional field, `builder_session_id` (uuid); the server stores it on `lead_submission` (IC-4) and adds it to the `draft_order` event payload. Nothing else changes: confirmation, Telegram and alerts are the existing ones, and `closeLinks` closes the lead's links as today.

## 24. CRM / sales handoff (MB-D09) `[R-17, R-18, R-19, R-21]`

**One lead event type, `menu_builder`** (actor `system:menu-builder`, written directly like `website_lead_intake`), with `payload.step`:

| step | When | Payload |
|---|---|---|
| `opened` | first open of a Builder session (once per session, whatever link) | `session_id`, `context` |
| `menu_completed` | first entry to KIT in the session | `session_id`, `drinks [{id, name}]`, `drink_count`, `product_count`, `kit_subtotal_ex_vat`, `rounded_up` |
| `help_requested` | help door tapped | `session_id`, `screen`, `drink_count`, `kit_subtotal_ex_vat` |

The kit's send is the existing `draft_order` event, now carrying `builder_session_id`; no separate "kit accepted" event.

**Task routing** (rules in the Unit A trigger, Sales lane, IC-2):
- `help_requested` → a `reply` task for the owner, or the manager queue when the lead is unowned. The one-open-reply index (D17) dedups it.
- `menu_completed` → a `call` task titled `הלקוח בנה תפריט ולא הזמין`, **due 24 h after the event**, `source_key` `builder:nudge:<lead_id>:<session_id>`. A new rule cancels it on the lead's `draft_order`; the existing rules cancel it on `lost`, `opt_out` and `converted` (Tom approved the 24 h task).

**Help door:** one tap on `רוצים לעבור על זה יחד? נחזור אליכם` writes the event and opens the `#help` sheet. The sheet shows the approved reply verbatim, `בשמחה! נתקשר אליכם בהקדם לשיחה קצרה.` / `בינתיים, כאן תמצאו תשובות לכל השאלות החשובות שלכם, ותכירו אותנו ואת צורת העבודה שלנו מקרוב.`, the button `שאלות ותשובות` (site FAQ) and `סגירה`. No form.

**Staff surfaces carry the menu itself (DR-06):** the task reason line (`4 משקאות: היביסקוס-ליים, … · ערכה ₪1,100 לפני מע״מ`), the drawer block `התפריט שבנה` (drinks, kit lines with coverage, total, status, age), the timeline labels and the rail milestone. They read `api_read.v_sales_builder` through the rep read scope (D3: reps see their own leads only). Staff labels never reuse the existing `kit_sent` event's wording.

## 25. Save / resume (MB-D07) `[R-02, R-22]`

- One server session per lead (`customer_portal.builder_session`, unique open row per `lead_id`), opened from any live link of that lead. Wake-up messages mint fresh links; all of them resume the same session.
- The session ends when the lead's draft order is created (status `ordered`). After that every link of the lead is closed by the existing `closeLinks`.
- The session stores ids, the context, the selection, `kit_overrides` and timestamps. It never stores the three lead fields.
- `לשמור ולחזור אחר כך` opens the native share sheet with `התפריט שלי ב-GT Everyday: <link>` (fallback `wa.me/?text=`). The link is the lead's personal token, so whoever receives it can edit the menu and send it as this lead's order request (a draft only). The sheet says so in one line: `מי שיקבל את הקישור יוכל לערוך את התפריט ולשלוח אותו אלינו`.

## 26. Analytics (MB-D10)

`customer_portal.builder_event` (append-only, server-written): `open` (context, resumed) · `drink_view` · `drink_add` · `drink_remove` · `preset_cleared` · `menu_completed` · `economics_viewed` · `kit_shown` (lines, subtotal, rounded_up, base below minimum) · `kit_edited` (line, from, to) · `kit_submitted` (submission id; named apart from the lead event `kit_sent`) · `help_requested` · `fast_path` · `resumed`. "Abandoned" is a query (no `menu_completed` after N days), not an event. Success is measured on the lead: Lead → First Order (`converted`), time from `opened` to `draft_order`, kit acceptance (sent kit vs shown kit, line by line), AOV of Builder vs non-Builder lead orders, human touches per converted lead, and recovery after a `builder:nudge` task. One read model serves this, `api_read.v_sales_builder_funnel`; no dashboard in V1. Attribution = session context + the lead's `source` / `campaign_name`.

## 27. Accessibility `[R-07]`

- 44 px targets everywhere (`--h-control`).
- Cards follow §7.2's markup: two sibling buttons, never nested. The toggle's accessible name is the full name and price.
- One polite live region announces `נוסף לתפריט: {drink} · {n} משקאות · ₪{x} לפני מע״מ` / `הוסר מהתפריט: {drink}`.
- Sheets are `role=dialog aria-modal`, with an `inert` background and focus return.
- Skip links `דילוג לתפריט` · `דילוג לערכה`. Group headers are `h2`, sub-families `h3`. The meters are `role=progressbar`.
- Contrast via the portal tokens (ink 14.6:1, muted 5.8:1, green 5.6:1). Focus ring 3 px `--gt`. Reduced motion honoured.
- axe clean in every state (the portal harness extended to the Builder).

## 28. RTL and mobile behaviour

- `<html lang="he" dir="rtl">`; logical properties only; `.num` LTR-isolated; English product names in `<span lang="en" translate="no">`.
- Arrows `←` point forward; close buttons sit at inline-start; safe areas as in the portal.
- Tiers 560 / 1100 px; grid 2 or 4; no horizontal scroll from 320 px.
- Keyboard-open handling as in the portal; the iOS Safari drop-shadow rule (soft floor only).

## 29. Security and privacy boundaries `[R-02, R-22]`

- The token travels in the path only and is stored as sha256. The lead-link rules are unchanged: 14 days, reusable until the lead's first draft order, then closed.
- Session rows hold ids, context and selection, and no free text from the customer.
- The kit endpoint is rate-limited per token (parameter: 120 requests / 10 min).
- CSP, the Origin/JSON guard, `no-store` and the security headers are inherited from the portal scope.
- The staff read model is `service_role` only, behind the rep read scope.
- Analytics rows carry session ids, never a phone or a name. No third-party script.
- Writes stay inside `customer_portal.*`, plus the IC-2 lead events and the optional `builder_session_id` in the `draft_order` payload.

## 30. System architecture (MB-D11) `[R-14, R-24]`

- **Where:** inside `gt-factory-os/api/src/portal/`, in the same `registerPortalRoutes` scope.
- **Routes:** `GET /portal/builder/:token` (page), `GET /portal/api/builder/:token` (bootstrap: drinks, session, context), `POST /portal/api/builder/:token/kit` (selection + overrides → kit; saves the session), `POST /portal/api/builder/:token/event` (help door and analytics intents). Send reuses `POST /portal/api/lead/:token/orders`.
- **Data:** `api/src/portal/builder/drinks.ts` (48 rows, Tom-verified). `api/src/portal/builder/figures.json` (synced, with provenance, the drift check and the integrity check of §17). Self-hosted images `/portal/img/d-<id>-{320,640}.webp`.
- **Frontend:** the portal's stack (one HTML file, inline CSS, ES5 IIFE, shared `:root` tokens enforced by `tokens.test.ts`).
- **Tables:** `customer_portal.builder_session`, `customer_portal.builder_event`, and `lead_submission.builder_session_id` (nullable).
- **Gate:** `customer_portal_live.enabled` **and** `customer_portal_live.value.builder`. That value is `false` (default: the Builder routes answer 404), `true` (every lead) or an array of E.164 phones (only those leads' links). The lead routes have no customer allowlist, which is why this is a phone list.

## 31. Sales System Integration Contract `[R-02, R-18, R-21]`

Lead → Builder → CRM → Salesperson → Recommended Cart → Order.

| Builder gives | Sales system gives (proposal) |
|---|---|
| `menu_builder` events with full payloads (names, counts, totals) | **IC-2:** one additive `event_type` `menu_builder`; two trigger rules (`help_requested` → `reply`; `menu_completed` → `call` due +24 h, cancelled by `draft_order`) |
| `v_sales_builder` read-model data | **IC-3:** drawer block, timeline labels, rail milestone, task reason text, under the rep read scope |
| `builder_session_id` on `lead_submission` and in the `draft_order` payload (**IC-4**, Builder lane) | — |
| nothing sent to the customer | the journey link that opens the Builder (placement, §3) |

~~IC-1 `lead_link.purpose`~~ is withdrawn: the Builder uses the existing link unchanged. Everything here is a proposal until the FINAL SALES RECONCILIATION PASS.

## 32. Builder ↔ Sales Dependency Ledger

`dependency-ledger.md` (DL-01…DL-20; IC-2…IC-4; IC-1 withdrawn).

## 33. Copy batch for Tom (one approval pass)

Rows become `U-nn` entries in a new `§5.8` of the customer-portal UX gate at implementation. Existing approved strings reused verbatim are marked *(existing)* and need no new approval.

| # | Where | Proposed |
|---|---|---|
| MB-01 | Title | `בניית התפריט שלכם` |
| MB-02 | Fast path | `מכירים את המוצרים? ישר לקטלוג ←` |
| MB-03 | Start banner, opening | `התחלנו מתפריט הפתיחה המומלץ שלנו · הסירו, החליפו, הוסיפו` |
| MB-04 | Start banner, context | `התחלנו מ{תפריט המאצ׳ה} · הסירו, החליפו, הוסיפו` |
| MB-05 | Start banner button | `להתחיל מאפס` · undo `ביטול` |
| MB-06 | Banner, unavailable in set | `משקה אחד לא זמין כרגע ולא נבחר` · `{n} משקאות לא זמינים כרגע ולא נבחרו` |
| MB-07 | Banner, resumed | `המשכנו מהביקור הקודם` |
| MB-08 | Group chips | `תה קר` · `מאצ׳ה` · `צ׳אי מסאלה` · `אובה` |
| MB-09 | Sub-families | `חליטות קרות` · `לימונדות` · `משקאות הדגל` · `גזוז` · `אייס מאצ׳ה` · `מאצ׳ה ספיישל` · `מאצ׳ה קוקוס` · `צ׳אי מסאלה` · `קולד פואם` |
| MB-10 | Card price line | `₪{n} · מחיר מומלץ` |
| MB-11 | Consequence chip, free | `בבקבוק שכבר בחרתם` · `באבקה שכבר בחרתם` · `במחית שכבר בחרתם` · `במוצרים שכבר בחרתם` |
| MB-12 | Consequence chip, adds | `+ מוצר: {name}` · `+ 2 מוצרים: {a}, {b}` |
| MB-13 | Chip on a selected card | `בתפריט` |
| MB-14 | Tags | `ללא קפאין` · `ללא סוכר אפשרי` |
| MB-15 | Details button | `פרטים` |
| MB-16 | Unavailable card | `לא זמין כרגע` · `צפי {d.M}` · `בינתיים: {alternative}` |
| MB-17 | Detail: needs | `מה צריך` · `כבר בתפריט` · `נוסף לערכה` · `דורש מקציף וחלב` |
| MB-18 | Detail: economics `[R-13]` | `מחיר מומלץ לצרכן · כולל מע״מ` · `עלות רכיבים לכוס ≈ ₪{c} · נשאר לכם ≈ ₪{k} לכוס · {m}%` · `נשאר לכם = המחיר פחות מע״מ, פחות עלות הרכיבים. גם האחוז מחושב כך.` · `עלות רכיבי המשקה בלבד, לפי מחירון · ללא קרח, סודה וקישוט · הערכה` |
| MB-19 | Detail buttons | `הוסיפו לתפריט` · `הסירו מהתפריט` |
| MB-20 | Bar `[R-06]` | `בחרו משקאות לתפריט` · `לערכת הפתיחה ←` · the minimum line *(existing)* `לפני מע״מ · מינימום ₪800` / `לפני מע״מ · עברתם את המינימום` · aria `{n} משקאות, ₪{x} לפני מע״מ.` + *(existing)* `חסרים עוד ₪{r} למינימום.` / `עברתם את המינימום.` |
| MB-21 | My-menu sheet | `התפריט שלי` · `הסרה` · `הוסר: {drink}` · `ביטול` · `{n} משקאות · {p} מוצרים` · `רוב המקומות פותחים עם 4–8 משקאות` |
| MB-22 | Kit header | `ערכת הפתיחה שלכם` · `הכמות הקטנה ביותר שמכסה את כל התפריט. אפשר לשנות.` |
| MB-23 | Kit line `[R-11]` | `≈{n} כוסות בסך הכול: {drinks}` · `ועוד {n}` · size control `1 ליטר` · `500 מ״ל` · toggle `ללא סוכר` |
| MB-24 | Remove product confirm | `בלי {product} אין: {drinks}. להסיר גם אותם מהתפריט?` · `להסיר` · `ביטול` |
| MB-25 | Round-up note `[R-10]` | `עיגלנו למינימום ההזמנה ₪800: הוספנו {lines}` ({lines} = `12 × NAMASTEA 1 ליטר`, joined by ` ו־`) · `תמציות נשמרות שנה בבקבוק סגור, בלי קירור.` · `אבקות נשמרות שנתיים.` (claim `shelf_life`, approved) |
| MB-26 | Below minimum after edits | `חסרים עוד ₪{r}` *(existing)* · button `להשלים למינימום` |
| MB-27 | Send button | `לשלוח את ההזמנה · ₪{t} כולל מע״מ` · ≤360 px `שליחה · ₪{t} כולל מע״מ` |
| MB-28 | Secondary actions | `לשמור ולחזור אחר כך` · `רוצים לעבור על זה יחד? נחזור אליכם` |
| MB-29 | Share sheet `[R-22]` | `התפריט שלי ב-GT Everyday:` · `מי שיקבל את הקישור יוכל לערוך את התפריט ולשלוח אותו אלינו` |
| MB-30 | Help door sheet `[R-17]` | *(existing, `TEXT.moreInfo`)* `בשמחה! נתקשר אליכם בהקדם לשיחה קצרה.` / `בינתיים, כאן תמצאו תשובות לכל השאלות החשובות שלכם, ותכירו אותנו ואת צורת העבודה שלנו מקרוב.` · *(existing)* `שאלות ותשובות` · `סגירה` |
| MB-31 | Done `[R-16]` | none new: the portal's lead done screen *(existing)* |
| MB-32 | Offline / kit error | `אין חיבור לאינטרנט. התפריט שמור, ונמשיך כשהחיבור יחזור.` · `לא הצלחנו לחשב את הערכה. בדקו את החיבור ונסו שוב.` · `לנסות שוב` |
| MB-33 | Resumed, drink removed | `{drink} הוסר: לא זמין כרגע` |
| MB-34 | Screen reader | `הוספה לתפריט: {drink}, ₪{n} מומלץ` · `הסרה מהתפריט: {drink}` · `נוסף לתפריט: {drink} · {n} משקאות · ₪{x} לפני מע״מ` · `הוסר מהתפריט: {drink}` · `דילוג לתפריט` · `דילוג לערכה` |
| ~~MB-35~~ | ~~Portal tile~~ | removed with customers `[R-03]` |
| MB-36 | Catalog back link | `חזרה לתפריט שבניתם` |
| MB-37 | Staff (tranche register) | task `הלקוח בנה תפריט ולא הזמין` · reason `{n} משקאות: {names} · ערכה ₪{t} לפני מע״מ` · drawer `התפריט שבנה` · timeline `פתח את בניית התפריט` · `השלים תפריט` · `ביקש לעבור על התפריט יחד` · rail `תפריט נבנה` |
| ~~MB-38~~ | ~~Equipment add-on~~ | removed `[R-12]` |

Rules applied: no dash as punctuation inside sentences (the `·` separator and `־` maqaf as the portal uses them), no nikud, every money figure labelled with its VAT basis, plural address (`אתם`/`לכם`) as in the portal, and a `stop-slop` pass before submission.

## 34. Explicit V1 non-goals (MB-D12, amended)

- Content and features: hot or winter drinks · recipes or preparation steps · any volume forecast or business-type questionnaire · sets beyond the five approved · discount tiers or customer-specific pricing logic · the 24 h branded-menu reward (struck by Tom) · printing or generating a menu file · any WhatsApp or email sent by the Builder · AI suggestions · filters, search, sorting controls · dark mode · English.
- Audiences and surfaces: an anonymous site mode · new staff-portal screens (only the drawer block and labels) · multi-branch or chain logic.
- Data: allergen or nutrition data · per-customer food cost · GT internal margins · a dashboard.
- **Added by Session 2:** existing customers and the portal tile `[R-03]` · the equipment add-on `[R-12]` · a link or menu that outlives the first order `[R-02]` · vibration `[R-25]`.

## 35. Acceptance criteria (each testable)

1. A lead whose latest `first_menu` event has `menu: matcha` opens a live link at `/portal/builder/<token>` and sees the matcha group first with the eight matcha-set drinks selected. With no `first_menu`, the opening set. `?c=tea` overrides the event `[R-29]`.
2. Tapping a card toggles it and updates the bar count within 100 ms locally. The kit endpoint returns the new chips and `subtotal_base`; the bar total equals it. The order of cards does not change while the page is open.
3. Every card's consequence chip equals `products(d) ∖ kit.products` computed on the server (property test over all 48 drinks × random selections).
4. For any selection, the kit holds exactly the required products, each at one sell unit before the round-up; shared products appear once (property test).
5. Coverage per line equals `floor(pack / max dose among the selected drinks using it) × qty`.
6. At the price snapshot the test reads, the five sets produce the kits of §13: `opening` ₪1,100 (3 concentrate pairs + matcha 500 g + a strawberry pair); `matcha` ₪960; `tea` ₪1,270 with 10 products; `chai` ₪130 base → 14 × NAMASTEA ₪910; `ube` ₪1,255 `[R-08]`.
7. The round-up follows §19 exactly: the five worked results in §19-4 hold; the note names every raised line; the shelf-life line appears exactly when a concentrate or powder line was raised `[R-10]`.
8. Editing a line below the minimum disables send and shows the shortfall; `להשלים למינימום` restores a sendable kit.
9. The detail sheet's figures equal the figures file. The CI test fails on any formula mismatch or parse failure. A mismatched file at runtime yields 503 on `/portal/builder*` only, while `/portal/`, `/portal/lead/*` and every Factory OS route keep answering `[R-14]`.
10. A product the planner marked unavailable cannot be selected. With `back_on` set and not passed the card shows `צפי d.M`; after that date passes the line disappears without a deploy.
11. Send creates exactly one Shopify draft tagged `lead`, with `builder_session_id` on the `lead_submission` row and in the `draft_order` payload. `draftOrderComplete` is unreachable from the Builder path (the portal's existing test, extended).
12. After that draft, every link of the lead answers 410 with the `gone()` text; the Builder session status is `ordered` `[R-02]`.
13. Reopening any live link of the lead within its validity shows the saved selection and the resumed banner, including a link minted later by a wake-up message `[R-22]`.
14. `menu_builder` events are written with full payloads: `opened` once per session, `menu_completed` once per session, `help_requested` per tap. No event is written twice for one action (unique on session + step for the first two) `[R-18]`.
15. `builder_event` rows exist for every taxonomy event. No row contains a phone or a name, and `builder_session` holds none of the three lead fields `[R-22]`.
16. 320 / 390 / 430 / 1440 px: no horizontal scroll, CLS 0 on first paint, LCP ≤ 1,300 ms on the cards-loading harness, ≤ 400 KB transferred on first load (images lazy beyond the first row).
17. axe reports 0 violations, including `nested-interactive`, in build, detail open, my-menu open, help open, kit, below-minimum, done, gone and offline `[R-07]`.
18. Reduced motion: no animation longer than .01 ms.
19. Every Hebrew string on the page is in the approved register (`portal_copy_check.mjs` extended to the Builder's files prints `0 unapproved`).
20. With `value.builder` false, or a phone list that excludes the lead, `/portal/builder/<token>` answers 404 and `/portal/lead/<token>` is unaffected `[R-24]`.
21. Nothing in the Builder writes outside `customer_portal.*`, the `menu_builder` lead events and the `draft_order` payload key. No Shopify call originates in Builder code.
22. Under Unit A (IC-2 accepted): `help_requested` on a lead with an open `reply` task creates no second task (D17); `menu_completed` creates one `call` task due +24 h, which the lead's `draft_order` cancels.

## 36. Unresolved assumptions

| # | Assumption | Owner | Blocks |
|---|---|---|---|
| U-MB-1 | CLOSED 2026-10-01 (kit = equipment). The add-on is now removed `[R-12]` | — | — |
| U-MB-2 | The drink → product → dose table. Session 2's 48-row draft is in `evidence/…-session2-independent-checks.md` §3 and must be Tom-verified (DL-18) | Tom (+ Session 3) | every kit |
| U-MB-3 | CLOSED 2026-10-01 (round-up as Tom gave it); exact algorithm and worked results now in §19 | — | — |
| U-MB-4 | Placement: P3 recommended (§3); Tom decides | Tom | launch wiring |
| U-MB-5 | ~~IC-1 mechanism~~ withdrawn. IC-2 shape (one `menu_builder` type) is the Sales workstream's to accept after Unit A | Sales session | CRM events |
| U-MB-6 | Unit A's final trigger shape may change the `reply` / `call` routing | Sales session | tasks |
| U-MB-7 | Cups-per-bottle claims on the site and PDFs should agree with the Builder's derived coverage | Tom / docs lane | consistency |
| U-MB-8 | Whether the five lead-menu PDFs carry the 2026-09-29 figures | menus workstream | consistency |
| U-MB-9 | Recipe defects (p12 name, p33 40 vs 50 ml, p36 copied recipe) | Tom / catalog | drink data |
| U-MB-10 | CLOSED 2026-10-01 (name only on the detail sheet) | — | — |
| U-MB-11 | 48 drink photos on the Shopify CDN at 925 × 1052; self-hosted from GT's Canva exports | — | images |
| U-MB-12 | Purée shelf life is in no approved claim, so the round-up note says nothing for purées | Tom | copy only |
| U-MB-13 | Doctrine records: the D-018 amendment and the supersession of "no quantities" (DL-20) | Tom | implementation start |
