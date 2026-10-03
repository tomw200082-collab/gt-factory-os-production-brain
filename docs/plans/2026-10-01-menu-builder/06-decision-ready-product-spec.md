# GT Menu Builder — Decision-Ready Product Spec

> **Status: PRODUCT DESIGN APPROVED — Tom, 2026-10-01, in writing ("חוץ מזה אני מאשר הכל!!!"), with his answers to U-MB-1 and U-MB-10 folded in (§15, §7.3, §36). State: WAITING FOR SALES FOUNDATION.** Built on the decisions Tom approved on 2026-10-01 (`decision-ledger.md` MB-D03, D04, D06, D08, D09 and the Session 1 decisions D02, D07, D10, D11, D12) and the deferral of placement (MB-D01). Nothing here is implemented. After Tom's approval the state is **PRODUCT DESIGN APPROVED — WAITING FOR SALES FOUNDATION**; Session 2 reviews it independently; Session 3 implements only after `SALES FOUNDATION GATE: PASS` and Tom's unlock.
> Precision target: an excellent engineering team builds this without inventing product while coding. Where a value is a parameter the spec says so and gives the default. Hebrew strings are in backticks and go to Tom as one copy batch (§33). File references point at the evidence folder and the live repos at the heads listed in `ground-truth.md`.

---

## 1. Current lead / customer journey

As reconstructed in `ground-truth.md` §1 (eight steps, live counts 2026-10-01). The part the Builder changes: today, between "I want drinks" and "I ordered", the lead holds a static PDF of ≤8 drinks and then an ordering link into 40 raw SKUs. The translation menu → bottles → quantities → cost happens in the lead's head or on the sales call.

## 2. Relevant future Sales-system journey

GT Pulse Unit A (contact loop, owned tasks, event-sourced from `lead_event`), on draft PRs gt-factory-os #329 and gt-factory-os-portal #239, release deferred by Tom 2026-09-30; Units B–E unspecified. The Builder appends to the same lead, the same event log and, under Unit A, the same task router. Detail: `ground-truth.md` §2, `dependency-ledger.md`.

## 3. Builder placement

**DEFERRED by Tom (MB-D01).** Three candidates stay open and the Builder is designed to fit all three without redesign (DR-03): (P1) its own lead journey per campaign; (P2) the first-message asset instead of the PDF; (P3) between the PDF and the order. In every placement the entry is a personal link (lead) or the portal session (customer) plus an optional category context (DR-01). The only placement-dependent wiring is which journey message carries the link; it is a one-line change in the lead journey code and a Tom-approved text (DL-08).

## 4. Segmentation and eligibility (MB-D02)

Eligible: any phone holding a `builder` link, any approved customer with a portal session. No lead-type logic. Context (`tea · matcha · chai · ube · opening`) is the only personalisation; it travels on the link (`?c=` style query, DL-19) or, for a customer, is absent (opening set). A revoked customer or an expired link gets the portal's existing "link gone" state (§11).

## 5. Bypass and fast path

- `מכירים את המוצרים? ישר לקטלוג ←` is a text link visible at the top of the Build screen from the first paint. It opens the ordering catalog for the same identity (lead mode or customer portal) with the same token or session; nothing built in the Builder is lost (the session stays saved).
- Existing customers never land in the Builder by default: it is a tile `בניית תפריט` on `/portal/` (location and look: a card in the reorder row's style, after the reorder cards).
- Back from the catalog to the Builder: the catalog page shows a small link `חזרה לתפריט שבניתם` only when a Builder session with ≥1 drink exists for that identity.

## 6. Complete customer flow

```
link / tile  →  BUILD (one scrolling screen)  →  KIT ("my menu" + "your starter kit")  →  send  →  DONE
                 ↑ detail sheet · my-menu sheet            ↑ edit kit · back to build
                 ↓ fast path → catalog                      ↓ save & return later (the link) · help door
```

Resume at any point reopens the last view with the last state (§25). The lead's fields (business, city, contact) are asked once, on the kit screen, right above the send button, exactly as the ordering portal's lead mode does today.

## 7. Screen-by-screen mobile flow (390 × 844 reference, 320 minimum)

### 7.1 BUILD — `/portal/builder/<token>` (lead) · `/portal/builder` (customer)

Top to bottom:

1. **Brand row** (scrolls away, portal `.top` pattern, 60 px): GT mark, title `בניית התפריט שלכם`, at inline-end the identity: lead → nothing; customer → `name · branch` as the portal shows it.
2. **Fast-path line** (under the title, 14 px 700, `--gt-d`, 44 px hit area): `מכירים את המוצרים? ישר לקטלוג ←`.
3. **Start banner** (`.msg` style, `--card` background, radius 16, 14 px 700, one line + one text button). Variants:
   - no context: `התחלנו מתפריט הפתיחה המומלץ שלנו · הסירו, החליפו, הוסיפו` · button `להתחיל מאפס`
   - context `matcha`: `התחלנו מתפריט המאצ׳ה · הסירו, החליפו, הוסיפו` (labels: `תפריט תמציות התה`, `תפריט האובה`, `תפריט הצ׳אי מסאלה`, the `lead_menus` labels verbatim)
   - a pre-selected drink dropped for availability: a second line `משקה אחד לא זמין כרגע ולא נבחר` / `{n} משקאות לא זמינים כרגע ולא נבחרו`
   - resumed: `המשכנו מהביקור הקודם` (replaces the first line; no button)
   - after `להתחיל מאפס`: the banner collapses (height animates out, 250 ms) and the bar reads `בחרו משקאות לתפריט`.
4. **Group chips** (pinned row, portal `.chips` pattern, 44 px pills, counts in 12 px muted): `תה קר 17` · `מאצ׳ה 16` · `צ׳אי מסאלה 10` · `אובה 5`. **Anchors, not filters:** tap scrolls to the group header (smooth unless reduced motion); the active chip follows the scroll position (IntersectionObserver on group headers). With a context the context group is first in both the chip row and the page.
5. **Groups**, in page order: context group first, then the default order `תה קר · מאצ׳ה · צ׳אי מסאלה · אובה`. Each group: header `.sec` (26 px 800) with the count of *selected* drinks in it (`מאצ׳ה · 3 נבחרו`, or just `מאצ׳ה`), then sub-family eyebrows (12 px 800, uppercase-style spacing not applicable to Hebrew; `--terra`): `חליטות קרות` · `לימונדות` · `משקאות הדגל` · `גזוז` / `אייס מאצ׳ה` · `מאצ׳ה ספיישל` · `מאצ׳ה קוקוס` / `צ׳אי מסאלה` · `קולד פואם` / (ube: none).
6. **Drink grid**: 2 columns (gap 14 px) on phone; 4 columns (gap 18 px) from a 640 px container; never 3 (portal rule). Card order inside a sub-family: the figures-file page order, except that at load time drinks whose products are already covered by the current selection move to the front of their sub-family (free-expansion-first). **Order never changes while the page is open** (no reflow under the thumb); only chips change live.
7. **Bottom bar** (fixed, ink, radius 22, min-height 64, portal `.bar`): inline-start: `5 משקאות · 3 מוצרים` (tap opens the My Menu sheet, §14); inline-end: button `לערכת הפתיחה ←` (paper on ink). Zero drinks: the bar stays, text `בחרו משקאות לתפריט`, button disabled (`aria-disabled`, `--disabled` fill). Keyboard open (visualViewport shrink >150 px): bar hidden, as the portal does.

### 7.2 Drink card (component, §9.1)

Size: full column width; photo area `aspect-ratio: 925 / 1052` (the photo's own ratio; no cropping), radius 24 top, the drink photo (`/portal/img/d-<id>-320.webp` / `-640.webp` via `srcset`, `sizes="(min-width:1100px) 240px, 50vw"`), background the group tint (tea `#F3D9DD`, matcha `#DDEBD6`, chai `#F0E2CC`, ube `#E8DFF2`, the portal's own flavour tints). Body (padding 12 px):

- **name** Heebo 800 17 px, 2 lines max, `text-wrap: balance`;
- **price line** 14 px 700 `.num`: `₪20 · מחיר מומלץ`;
- **consequence chip** (12 px 800, pill, min-height 24): `בבקבוק שכבר בחרתם` (`--ok-bg` / `--gt-d`) or `+ מוצר: FRESH` (`--card` / `--ink-soft`) or `+ 2 מוצרים: מאצ׳ה, מנגו` (two products; names as the portal's product names, GT Latin not used on chips: Hebrew-transliterated names from the `P` list are English brand names, shown as-is in `<span lang="en">`);
- **tags row** (11 px 800 badges, only when true): `ללא קפאין` · `ללא סוכר אפשרי` (a sugar-free twin exists for the product);
- **details link** 14 px 700 `--gt-d`, 44 px hit area, inline-end: `פרטים`.

States: default · selected (2.5 px ink ring, ✓ pill `.got` at inline-start of the photo, photo scale 1.02) · unavailable (greyscale .5 opacity, white stamp `לא זמין כרגע`, second line `צפי 14.10` when `back_on` is set and not passed, or `בינתיים: FRESH ללא סוכר` when the planner named an alternative; not selectable; `aria-disabled`) · pressed (scale .97, `--d-press`).

The whole card is one `<button aria-pressed>` except the `פרטים` link (its own button, stops propagation).

### 7.3 Detail sheet (`#d-<id>` in the hash; bottom sheet 88dvh, radius 26/26/0/0, portal sheet mechanics)

Top: photo (same asset, 60% width, centred, soft floor shadow), name (26 px 800), sub-family eyebrow. Then, in order:

1. **The name**, exactly as the Canva drinks menu prints it (Tom 2026-10-01: name only, no new description copy).
2. **What you need**: product lines with the consequence state: `FRESH · 1 ליטר` + chip (`כבר בתפריט` / `נוסף לערכה`), and for two-product drinks both lines. Equipment note when the product requires it: `דורש מקציף וחלב` (from `requires_equipment`).
3. **Economics block** (MB-D04): big `₪20` with `מחיר מומלץ לצרכן · כולל מע״מ` (12 px muted), then one line 14 px: `עלות רכיבים לכוס ≈ ₪3.25 · נשאר לך ≈ ₪13.70 לכוס · 81%`, then the footnote once (12 px muted): `עלות רכיבי המשקה בלבד, לפי מחירון · ללא קרח, סודה וקישוט · הערכה`. For a customer with own prices the footnote reads `… לפי מחירון …` unchanged (the estimate is list-based by design).
4. **Tags**: `ללא קפאין`, `ללא סוכר אפשרי`.
5. **Primary button** (54 px pill): `הוסיפו לתפריט` / `הסירו מהתפריט` (toggles; sheet stays open; the card behind updates).

No preparation steps, no recipe (masterprompt §13). Close: ✕ (inline-start, 44 px), backdrop, Esc, swipe down, back gesture (hash).

### 7.4 KIT — same page, `#kit` view (back button returns to BUILD)

Top to bottom:

1. **Header**: `התפריט שלי` (32 px 800) with a check mark drawn once (`draw` keyframe, 600 ms, static under reduced motion). Sub-line 14 px muted: `{n} משקאות · {p} מוצרים`.
2. **My menu list** (Layer 1): one row per drink, grouped by group with eyebrows: photo thumb 44 px, name 16 px 700, `₪20 · מומלץ` 14 px `.num`. Row tap → detail sheet. Inline-end of the header: text button `עריכה` → back to BUILD.
3. **Kit header**: `ערכת הפתיחה שלכם` (26 px 800) + one line 14 px: `הכמות הקטנה ביותר שמכסה את כל התפריט. אפשר לשנות.`
4. **Kit lines** (Layer 2), one per product, portal cart-line anatomy: product image thumb (the portal's `l-`/`p-`/`o-` asset), name (GT Latin 20 px as in the portal) + size (`1 ליטר` / `500 גרם`), size segmented control for concentrates (`1 ליטר` | `500 מ״ל`, 44 px, default 1 L), sugar-free toggle when a twin exists (`ללא סוכר`, 44 px switch), stepper (`44px | qty | 44px`, step 2 for bottles and purées, 1 for powders; `נמכר בזוגות` under bottle lines), line price `.num` ex-VAT, **coverage line** 13 px muted: `≈40 כוסות: היביסקוס-ליים, גזוז היביסקוס ותפוח` (drinks the product serves, up to 3 names then `ועוד {n}`), and the `+6 · ארגז` chip exactly as the portal.
5. **Round-up note** (only when applied; `.note` style, `--ok-bg`): `עיגלנו למינימום ההזמנה ₪800: הוספנו 2 × FRESH 1 ליטר` (multiple: `הוספנו 2 × FRESH 1 ליטר ו־2 × DETOX 1 ליטר`). The raised lines carry a 1.2 s ring highlight on first paint.
6. **Totals** (`<dl>`): `סה״כ לפני מע״מ` · `מע״מ 18%` · `סה״כ כולל מע״מ` (26 px, counts up 250 ms), the portal's minimum meter (`לפני מע״מ · מינימום ₪800`). Lead: the fine print `מחירי המחירון, לפני מע״מ` (existing string). Customer: `המחירים שלכם, לפני מע״מ`.
7. **Lead fields** (lead only; the portal's `leadForm` fieldset verbatim): `שם העסק` · `סניף או עיר` · `השם שלכם`; existing validation and errors.
8. **Primary button** (54 px): `לשלוח את ההזמנה · ₪1,298 כולל מע״מ` (≤360 px: `שליחה · ₪1,298 כולל מע״מ`). Below the minimum after edits: disabled, meter shows `חסרים עוד ₪130`, and a button `להשלים למינימום` re-runs the round-up.
9. **Secondary actions** (text, 44 px): `לשמור ולחזור אחר כך` → share sheet (§25) · `רוצים לעבור על זה יחד? נחזור אליכם` → help door (§24).

### 7.5 DONE — the portal's confirmation, in place

The portal's done screen unchanged (`קיבלנו את ההזמנה`, counts, `פירוט ההזמנה`, share, `סיום`), with the lead's next line `נחזור אליכם בקרוב לתיאום המשלוח.` and one added line above the counts: `התפריט שלכם שמור בקישור הזה.` After DONE the page reopens in read-only KIT view (steppers disabled, button replaced by `להזמין שוב` → portal for customers; for a lead `ההזמנה אצלנו, נחזור אליכם`).

### 7.6 Progress and back behaviour

Two views and two sheets; the URL hash is the state (`#build` implicit, `#kit`, `#menu` sheet, `#d-<id>` sheet). Browser back closes the top-most sheet, then returns from KIT to BUILD, then leaves. No step counter (two steps need none); the bar's count is the progress.

## 8. Information hierarchy

BUILD: the drink (photo, name) › RRP › consequence chip › tags › details. KIT: the menu › the kit lines (qty and coverage) › totals › send. The customer's attention order is "what will I serve" → "what does it take" → "what does it cost" → "send". Money appears first on the kit, never on the build screen except the RRP (a selling price, not a cost).

## 9. Component behaviour

### 9.1 Drink card
Tap toggles selection; the selection is saved (debounced 250 ms) and the kit is recomputed server-side (`POST …/kit`, §17) in the background; consequence chips of *other* cards update from the response (fade 180 ms); the bar updates immediately from local state and reconciles with the response.

### 9.2 Consequence chip
Computed per card from the current kit: products required by the drink ∖ products already in the kit. Empty set → `בבקבוק שכבר בחרתם` (for powders: `באבקה שכבר בחרתם`; for purée: `במחית שכבר בחרתם`; mixed: `במוצרים שכבר בחרתם`). One product → `+ מוצר: {name}`. Two → `+ 2 מוצרים: {a}, {b}`. On a selected card the chip reads `בתפריט` with the ✓.

### 9.3 Group chips
Anchors with scroll-spy; `aria-current="true"` on the active one; never hide cards.

### 9.4 Start banner
As §7.1-3; `להתחיל מאפס` asks nothing (undoable: a 6 s `ביטול` toast restores the set).

### 9.5 My Menu sheet (§14)
List of selected drinks with `הסרה` (44 px) per row and undo toast 6 s; footer `{n} משקאות · {p} מוצרים` and the same `לערכת הפתיחה ←` button.

### 9.6 Kit line
Stepper in sell units; removing a product (qty → 0) is allowed only through an explicit `הסרה` with a confirm line `בלי FRESH אין: היביסקוס-ליים, גזוז היביסקוס ותפוח. להסיר גם אותם מהתפריט?` · `להסיר` · `ביטול`; removing drops those drinks from the menu. Size toggle recomputes coverage and price; sugar-free toggle swaps the SKU.

### 9.7 Totals and meter
Server values only; the client never computes money (§17). The meter and `חסרים עוד ₪X` use the portal's existing component.

### 9.8 Sticky bar / side panel
<560 px bottom bar; 560–1099 bar + drawer; ≥1100 px sticky side panel 340 px (360 px from 1280) showing the My Menu list live and the CTA, in the portal's side-cart style.

## 10. Key microinteractions

| Moment | Behaviour | Tokens |
|---|---|---|
| Select a drink | ring appears, ✓ pill `pop`, photo scale 1→1.02, bar count `bump`, `navigator.vibrate(8)` on Android | `--d-ui`, `--spring` |
| Deselect | ring fades, ✓ pill scales out | `--d-ui` |
| Chip change on other cards | text crossfade 180 ms | `--ease` |
| Open detail / my-menu sheet | portal sheet: slide up 320 ms, scrim, handle | `--out` |
| Remove from my menu | row collapses 250 ms, undo toast 6 s | `--d-ui` |
| Go to kit | view slides in from inline-end 300 ms; kit lines stagger 40 ms each (max 8); total counts up 250 ms | `--out` |
| Round-up applied | raised lines ring highlight 1.2 s; note fades in | `--ease` |
| Stepper | portal stepper animation (`grow` 320 ms), coverage text recounts | existing |
| Send | portal send state machine (sending → pending → done) verbatim | existing |
| Completion | header check `draw` 600 ms once per session | existing keyframe |

Reduced motion: every duration .01 ms, no vibration, no count-up, no stagger (portal rule). No confetti, no points, no streaks.

## 11. Loading, error, empty, resume states

| State | What the customer sees |
|---|---|
| Loading | 8 skeleton cards + skeleton banner, `aria-busy`; cards paint from the static drink list first, prices and chips when the kit responds (portal "one reveal": ≤700 ms paint at once, else skeleton, past 2.5 s paint without chips) |
| Link expired / used / unknown (410) | portal `gone()` pattern: `הקישור הזה כבר לא פעיל. אם שלחתם הזמנה, היא אצלנו, ונחזור אליכם בקרוב.` + `כתבו לנו בוואטסאפ` (lead line) |
| Portal closed (503) | portal C-10 text |
| Offline | banner `אין חיבור לאינטרנט. התפריט שמור, ונמשיך כשהחיבור יחזור.`; selection keeps working locally; kit recompute retries on `online` |
| Slow kit response (>2.5 s) | chips stay as they were; bar shows a 12 px spinner next to the count |
| Kit endpoint error | `לא הצלחנו לחשב את הערכה. בדקו את החיבור ונסו שוב.` · `לנסות שוב` (last good kit stays visible, greyed) |
| Empty selection | bar `בחרו משקאות לתפריט`; KIT unreachable |
| Unavailable product (planner) | §7.2 states; a resumed selection containing it: removed, banner line `{drink} הוסר: לא זמין כרגע` |
| Resumed | banner `המשכנו מהביקור הקודם`; kit recomputed with today's prices and availability |
| Price changed between kit and send (409) | portal re-price flow: struck old price, badge `המחיר עודכן`, send again |
| Below minimum after edits | §7.4-8 |
| Stale tab (hidden >30 min) | kit recomputed on return (portal rule) |
| Send outcomes | the portal's table (201/202/401/503/422/409/network) verbatim; 410 on a lead link → `gone()` |

## 12. Drinks discovery model (MB-D06)

Four groups in the lead-menu vocabulary; context group first; curated set pre-selected; purchase-consequence chip; free expansions first at load; no filters, no search. Drink order inside a sub-family: figures-file page order.

## 13. Presets

Exactly the five approved sets (D-026), as pre-selections keyed by context: `opening` 8 · 27 · 12 · 21 · 48 · 55 · 29 · 31 — `matcha` 29 · 30 · 31 · 33 · 34 · 39 · 42 · 44 — `tea` 8 · 9 · 13 · 16 · 21 · 22 · 25 · 26 — `chai` 48 · 49 · 50 · 51 · 55 · 56 · 57 · 18 — `ube` 60 · 61 · 62 · 63 · 64 (figures-file page ids). The sets live in the Builder's drink data file next to the drinks; changing a set is a data change with Tom's word, no UI.

## 14. "My Menu" behaviour

The sticky bar is the menu's live summary; the sheet is its editor; the KIT header is its presentation. The menu is an ordered list (selection order), capped at nothing; soft guidance above 10: a one-line note in the sheet footer `רוב המקומות פותחים עם 4–8 משקאות` (no block). A drink stays in the menu when its product goes unavailable *after* selection only until the next kit recompute, which removes it with the banner line.

## 15. Quantity model (MB-D03)

Zero questions. Kit = for each product P required by any selected drink: `qty(P) = unit(P)` where unit = 2 for concentrates and purées (pairs), 1 for powders. Then the round-up (§19). Editable afterwards; the customer's edits are kept as `kit_overrides` and survive recompute unless a product leaves the menu.

Default packs (parameters): concentrate `1l` (`05` by toggle), purée `1l`, ube `500`, matcha `500`. **The ₪170 matcha kit holds no matcha**: its BOM in Factory OS (`BOM-REPACK-MAT-KIT`, active V1) is two 500 ml bottles with caps, a manual frother, a 600 ml matcha cup, a measuring cup and a branded carton (read live 2026-10-01; Tom described the same set). It is equipment, so it never replaces the powder line. **Proposed, pending Tom's word:** for a menu that needs a frother (any matcha, ube or cold-foam drink; `requires_equipment`), the kit screen shows one optional line under the products, off by default: `אין לכם מקציף? ערכת מאצ׳ה · ₪170 · מקציף, בקבוק, כוס מדידה, כוס ערבוב` with an `הוספה` button; it joins the kit as a normal line and counts toward the minimum. Struck if Tom says so.

## 16. Economic presentation (MB-D04)

Card: RRP only. Detail: the four unit figures with the estimate footnote. Kit: cash outlay with VAT lines and coverage. Never: projections, GT margins, per-customer food cost.

## 17. Calculation semantics (server-side, exact)

Inputs: figures file `pages[id] = {cost, price, marg, prof}` (cost ex-VAT ₪ with 2 decimals; price incl. VAT integer ₪), dose table `dose[id][product] = ml | g`, pack table `pack[product][size] = {ml | g, catalog_key}`, prices from the portal pricer for the identity, availability overlay, VAT 0.18, minimum 800.

- `rrp(d) = price`; `cost(d) = cost`; `kept(d) = round2(price / 1.18 − cost)`; `margin(d) = round((price/1.18 − cost) / (price/1.18) × 100)` — identical to the figures file's own `prof`/`marg`; the server asserts equality at boot and refuses to start on a mismatch (the figures file is the authority, the formula is a check).
- `products(d)` = keys of `dose[d]`; `need(P) = {d ∈ selection : P ∈ products(d)}`.
- `servings(P, size) = floor(pack[P][size] / max_{d ∈ need(P)} dose[d][P])` (conservative: the largest dose among the chosen drinks); `coverage(P) = servings(P, size) × qty(P)`; displayed as `≈{coverage} כוסות`.
- `line(P) = qty(P) × unit_price(P)`; `subtotal = round2(Σ line)`; `vat = round2(subtotal × 0.18)`; `total = round2(subtotal + vat)` — the portal's rounding verbatim.
- Money is never multiplied or divided by 1.18 anywhere else; RRP is displayed as stored.
- Unit prices: lead → `pricer.listPrices()`; customer → `pricedFor(customer)` (family rule). The kit is re-priced on every recompute and on send; drift → `PRICE_CHANGED` as the portal.

## 18. BOM-to-cart logic

Drink → products → doses from the Builder's drink data (DL-18, Tom-verified). No factory BOM is read (gt-factory-os BOMs model production, not serving). Sugar-free: the twin SKU replaces the regular at the same dose. Two-product drinks contribute to both products' `need`.

## 19. Aggregation and round-up rules

1. Aggregate per product across all selected drinks; never round per drink.
2. Base quantity = one sell unit per required product (§15).
3. If `subtotal < 800`: raise in tiers until `subtotal ≥ 800`: **T1** concentrate lines at 1 L; **T2** concentrate lines at 500 ml; **T3** purée lines, then powder lines (smallest price increment first). Within a tier: the product with the largest `|need(P)|`, ties by catalog order; one unit per step, round-robin within the tier. Only products already in the kit; never add a product.
4. Record `rounded_up = [{product, from, to}]` and render the note (§7.4-5).
5. Customer edits below the minimum leave the kit below the minimum: send disabled, `להשלים למינימום` re-runs step 3 from the current quantities.
6. Pairs are enforced by the stepper and re-checked by the server (`NOT_IN_PAIRS`), minimum by the server (`BELOW_MINIMUM`), availability by the server (`BAD_LINE`), all as the portal today.

## 20. Authoritative data sources

`ground-truth.md` §5. Runtime inputs: figures (synced copy of `drinks_final_figures.json` with provenance and CI drift check), drink data file (Tom-verified), portal catalog + pricer, availability overlay. Nothing is read from Sales-Machine cards, gt-site or Canva at runtime.

## 21. Recommendation explanation

Every number the customer could question has its reason on the screen: coverage line (why this quantity), round-up note (why more than the minimum unit), `נמכר בזוגות` (why 2), the estimate footnote (what the cost means), `מחירי המחירון` / `המחירים שלכם` (whose prices). No hidden rounding.

## 22. Finish experience (MB-D08)

§7.4–7.5. The emotional beat is the header: the menu named, the check drawn, then the kit under it with the sentence `הכמות הקטנה ביותר שמכסה את כל התפריט. אפשר לשנות.`

## 23. Purchase handoff

Send posts the kit as `lines[{key, qty, price}]` to the existing lead path (`POST /portal/api/lead/<token>/orders` + three fields → Shopify draft, never completed) or the customer path (`POST /portal/api/orders` → draft → complete). The Builder adds `builder_session_id` to the body (IC-4) and nothing else. Confirmation, Telegram and alerts are the existing ones.

## 24. CRM / sales handoff (MB-D09)

Events `builder_opened`, `builder_menu_completed` (on first entry to KIT), `builder_kit_accepted` (on send), `builder_help_requested` (help door). Help door: a sheet `רוצים לעבור על זה יחד?` · `נחזור אליכם בהקדם. בינתיים, כאן תמצאו תשובות לכל השאלות החשובות.` · button `שאלות ותשובות` (site FAQ) · the door is one tap, no form; it writes the event, which under Unit A becomes a `reply` task for the owner (or the manager queue when unowned). Menu completed without `draft_order` for 24 h → task `call` `הלקוח בנה תפריט ולא הזמין` (approved). Every staff surface carries the menu itself (DR-06): the task reason line lists the drinks (`4 משקאות: היביסקוס-ליים, …`) and the kit total.

## 25. Save / resume (MB-D07)

Server session per identity; the link reopens it for 14 days (lead) and the cookie for customers; after an order the finish is read-only. `לשמור ולחזור אחר כך` opens the native share sheet with `התפריט שלי ב-GT Everyday: <link>` (fallback `wa.me/?text=`); the link is the same personal token, so whoever receives it can edit the menu — stated on the share sheet in one line `מי שיקבל את הקישור יוכל לערוך את התפריט`.

## 26. Analytics (MB-D10)

`customer_portal.builder_event` taxonomy and the lead-level success metrics as in `05-…` §4. Attribution = `builder_session.context` + the lead's `source` / `campaign_name`.

## 27. Accessibility

44 px targets everywhere (`--h-control`); cards as `<button aria-pressed>` with full names in the accessible label (`הוספה לתפריט: חליטת היביסקוס וליים, ₪20 מומלץ`); one polite live region announcing `נוסף לתפריט: {drink} · {n} משקאות` / `הוסר מהתפריט: {drink}`; sheets `role=dialog aria-modal` with `inert` background and focus return; skip links `דילוג לתפריט` · `דילוג לערכה`; group headers are `h2`, sub-families `h3`; the meter `role=progressbar`; contrast via the portal tokens (ink 14.6:1, muted 5.8:1, green 5.6:1); focus ring 3 px `--gt`; reduced motion honoured; axe clean in every state (the portal harness extended to the Builder).

## 28. RTL and mobile behaviour

`<html lang="he" dir="rtl">`; logical properties only; `.num` LTR-isolated; English product names in `<span lang="en" translate="no">`; arrows `←` for forward; close buttons at inline-start; safe areas as the portal; tiers 560 / 1100 px; grid 2 or 4; no horizontal scroll from 320 px; keyboard-open handling as the portal; iOS Safari drop-shadow rule (soft floor only).

## 29. Security and privacy boundaries

Token in the path only; sha256 stored; 14-day expiry; reusable (not single-use) — the share-sheet line says so. Session rows hold ids and the selection, no free text from the customer except the three lead fields that already exist. The kit endpoint is rate-limited per token (parameter: 120 requests / 10 min). CSP, Origin/JSON guard, `no-store`, security headers inherited. Staff read model `service_role` only. Analytics rows carry session ids, never phone or name. No third-party script. Writes stay inside `customer_portal` plus the four proposed Sales-lane changes.

## 30. System architecture (MB-D11)

`05-…` §5: inside the ordering portal, one new page, one kit endpoint, two tables, a drink data file, a synced figures file, self-hosted images, the portal's stack and tokens, dark behind `customer_portal_live.value.builder_allowlist`.

## 31. Sales System Integration Contract

Lead → Builder → CRM → Salesperson → Recommended Cart → Order, as proposed in `05-…` §3 and §24 above. Summary of obligations:

| Builder gives | Sales system gives (proposal) |
|---|---|
| events with full payloads (names, counts, totals) | four additive `event_type`s (IC-2) |
| `v_sales_builder` read model data | drawer block, timeline labels, rail milestone, task reason text (IC-3) |
| `builder_session_id` on submissions (IC-4) | `lead_link.purpose` so Builder links survive orders (IC-1) |
| nothing sent to the customer | the journey message that carries the Builder link (placement, DL-08) |

Everything is a proposal until the FINAL SALES RECONCILIATION PASS.

## 32. Builder ↔ Sales Dependency Ledger

`dependency-ledger.md` (DL-01…DL-19, IC-1…IC-4).

## 33. Copy batch for Tom (the Builder's Hebrew, one approval pass)

Rows become `U-nn` entries in a new `§5.8` of the customer-portal UX gate at implementation. Existing portal strings reused verbatim are not listed.

| # | Where | Proposed |
|---|---|---|
| MB-01 | Title | `בניית התפריט שלכם` |
| MB-02 | Fast path | `מכירים את המוצרים? ישר לקטלוג ←` |
| MB-03 | Start banner, no context | `התחלנו מתפריט הפתיחה המומלץ שלנו · הסירו, החליפו, הוסיפו` |
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
| MB-15 | Details link | `פרטים` |
| MB-16 | Unavailable card | `לא זמין כרגע` · `צפי {d.M}` · `בינתיים: {alternative}` |
| MB-17 | Detail: needs | `מה צריך` · `כבר בתפריט` · `נוסף לערכה` · `דורש מקציף וחלב` |
| MB-18 | Detail: economics | `מחיר מומלץ לצרכן · כולל מע״מ` · `עלות רכיבים לכוס ≈ ₪{c} · נשאר לך ≈ ₪{k} לכוס · {m}%` · `עלות רכיבי המשקה בלבד, לפי מחירון · ללא קרח, סודה וקישוט · הערכה` |
| MB-19 | Detail buttons | `הוסיפו לתפריט` · `הסירו מהתפריט` |
| MB-20 | Bar | `{n} משקאות · {p} מוצרים` · `בחרו משקאות לתפריט` · `לערכת הפתיחה ←` |
| MB-21 | My-menu sheet | `התפריט שלי` · `הסרה` · `הוסר: {drink}` · `ביטול` · `רוב המקומות פותחים עם 4–8 משקאות` |
| MB-22 | Kit header | `ערכת הפתיחה שלכם` · `הכמות הקטנה ביותר שמכסה את כל התפריט. אפשר לשנות.` |
| MB-23 | Kit line | `≈{n} כוסות: {drinks}` · `ועוד {n}` · size control `1 ליטר` · `500 מ״ל` · toggle `ללא סוכר` |
| MB-24 | Remove product confirm | `בלי {product} אין: {drinks}. להסיר גם אותם מהתפריט?` · `להסיר` · `ביטול` |
| MB-25 | Round-up note | `עיגלנו למינימום ההזמנה ₪800: הוספנו {lines}` ({lines} = `2 × FRESH 1 ליטר`, joined by ` ו־`) |
| MB-26 | Below minimum after edits | `חסרים עוד ₪{r}` (existing) · button `להשלים למינימום` |
| MB-27 | Send button | `לשלוח את ההזמנה · ₪{t} כולל מע״מ` · ≤360 px `שליחה · ₪{t} כולל מע״מ` |
| MB-28 | Secondary actions | `לשמור ולחזור אחר כך` · `רוצים לעבור על זה יחד? נחזור אליכם` |
| MB-29 | Share sheet | `התפריט שלי ב-GT Everyday:` · `מי שיקבל את הקישור יוכל לערוך את התפריט` |
| MB-30 | Help door sheet | `נחזור אליכם בהקדם. בינתיים, כאן תמצאו תשובות לכל השאלות החשובות.` · `שאלות ותשובות` · `סגירה` |
| MB-31 | Done, added line | `התפריט שלכם שמור בקישור הזה.` · read-only kit `ההזמנה אצלנו, נחזור אליכם` · customer `להזמין שוב` |
| MB-32 | Offline / kit error | `אין חיבור לאינטרנט. התפריט שמור, ונמשיך כשהחיבור יחזור.` · `לא הצלחנו לחשב את הערכה. בדקו את החיבור ונסו שוב.` · `לנסות שוב` |
| MB-33 | Resumed, drink removed | `{drink} הוסר: לא זמין כרגע` |
| MB-34 | Screen-reader | `הוספה לתפריט: {drink}, ₪{n} מומלץ` · `נוסף לתפריט: {drink} · {n} משקאות` · `הוסר מהתפריט: {drink}` · `דילוג לתפריט` · `דילוג לערכה` |
| MB-35 | Portal tile (customers) | `בניית תפריט` · `בוחרים משקאות, ואנחנו מרכיבים את ההזמנה` |
| MB-36 | Catalog back link | `חזרה לתפריט שבניתם` |
| MB-37 | Staff: task and reason (DR-06) | `הלקוח בנה תפריט ולא הזמין` · `{n} משקאות: {names} · ערכה ₪{t} לפני מע״מ` · drawer block title `התפריט שבנה` · timeline `פתח את בניית התפריט` · `השלים תפריט` · `אישר ערכת פתיחה` · `ביקש לעבור על התפריט יחד` · rail `תפריט נבנה` |
| MB-38 | Equipment add-on line (proposed, pending Tom) | `אין לכם מקציף? ערכת מאצ׳ה · ₪170 · מקציף, בקבוק, כוס מדידה, כוס ערבוב` · `הוספה` |

Rules applied: no dash as punctuation inside sentences (the `·` separator and `־` maqaf as the portal uses them), no nikud, every money figure labelled with its VAT basis, plural address (`אתם`) as the portal, `stop-slop` pass before submission.

## 34. Explicit V1 non-goals (MB-D12)

`05-…` §6.

## 35. Acceptance criteria (each testable)

1. A lead opening a `builder` link with context `matcha` sees the matcha group first and the eight matcha-menu drinks selected; with no context, the eight opening-menu drinks.
2. Tapping a card toggles it, updates the bar within 100 ms locally, and the kit endpoint returns the new chips; order of cards does not change while the page is open.
3. Every card's consequence chip equals `products(d) ∖ kit.products` computed on the server (property test over all 48 × random selections).
4. For any selection, the kit contains exactly the products required, each at one sell unit before round-up; shared products appear once (property test).
5. Coverage per line equals `floor(pack / max dose among the selected drinks using it) × qty`.
6. For the opening set with list prices the kit is three concentrate pairs + matcha 500 g + a strawberry pair and the subtotal is ₪1,100 ex-VAT (figures of 2026-10-01; the test reads the live price snapshot).
7. For a selection whose base kit is below ₪800, the server raises quantities in tiers T1 → T2 → T3 until ≥ ₪800, returns `rounded_up`, and the note names every raised line; a powder-only selection reaches T3 and still ends ≥ ₪800.
8. Editing a line below the minimum disables send and shows the shortfall; `להשלים למינימום` restores a sendable kit.
9. The detail sheet's four figures equal the figures file; the boot assertion fails on a formula mismatch.
10. A product marked unavailable by the planner cannot be selected; with `back_on` set and not passed the card shows `צפי d.M`; after the date passes the line disappears without a deploy.
11. A customer with own prices sees their prices on kit lines and `לפי מחירון` on the economics footnote.
12. Send from a lead creates exactly one Shopify draft tagged `lead` with `builder_session_id` on the submission; `draftOrderComplete` is unreachable from the Builder path (the portal's existing test extended).
13. Send from a customer creates an order through the existing path; replays with the same `idem_key` create one order.
14. Reopening the link within 14 days shows the saved selection and the resumed banner; after a draft order the KIT view is read-only and the link still opens.
15. `builder_opened`, `builder_menu_completed`, `builder_kit_accepted`, `builder_help_requested` are written with full payloads; no event is written twice for one action (unique on session + event + step).
16. `builder_event` rows exist for every taxonomy event; no row contains a phone or a name.
17. 320 / 390 / 430 / 1440 px: no horizontal scroll, CLS 0 on first paint, LCP ≤ 1,300 ms on the cards-loading harness, ≤ 400 KB transferred on first load (images lazy beyond the first row).
18. axe reports 0 violations in build, detail open, my-menu open, kit, below-minimum, done, gone, offline.
19. Reduced motion: no animation longer than .01 ms, no vibration.
20. Every Hebrew string on the page is in the approved register (`portal_copy_check.mjs` extended to the Builder's files prints `0 unapproved`).
21. The Builder is invisible when `customer_portal_live.value.builder_allowlist` excludes the identity (404 for the link, no tile).
22. Nothing in the Builder writes outside `customer_portal.*` and the four contract items; no Shopify call originates in Builder code.

## 36. Unresolved assumptions

| # | Assumption | Owner | Blocks |
|---|---|---|---|
| U-MB-1 | **CLOSED 2026-10-01.** The kit's contents are in Factory OS (`GT-MAT-KIT` → `BOM-REPACK-MAT-KIT`: 2 × 500 ml bottles + caps, manual frother, 600 ml cup, measuring cup, carton; no powder) and Tom described the same set. Default matcha pack = 500 g bag. The optional equipment line (§15) is a proposal awaiting Tom's word | — | — |
| U-MB-2 | The drink → product → dose table (48 rows) does not exist in structured form; it is authored from the 2026-09-29 cost model and must be Tom-verified (DL-18) | Session 3 + Tom | everything |
| U-MB-3 | **CLOSED 2026-10-01.** Tom approved the spec with the round-up rule as given (no cap); single-product menus round up transparently, the note names every added line | — | — |
| U-MB-4 | Placement (MB-D01) and therefore which journey text carries the link; the texts are Tom's | Tom | launch wiring |
| U-MB-5 | IC-1 mechanism (`purpose` column vs separate table) and IC-2 event vocabulary are the Sales workstream's call after Unit A | Sales session | resume after order, CRM events |
| U-MB-6 | Unit A's final task trigger shape may change the `reply` / `call` routing | Sales session | tasks |
| U-MB-7 | One approved cups-per-bottle figure per product (U-021) is not required by the Builder (it derives coverage from doses) but the site's and PDF's claims should agree with the Builder's numbers | Tom / docs lane | consistency |
| U-MB-8 | Whether the five lead-menu PDFs carry the 2026-09-29 figures | menus workstream | consistency with the Builder's figures |
| U-MB-9 | The recipe defects on approved pages (p36 copied recipe, p12 name, matcha-masala 40 vs 50 ml) are resolved by the catalog owner; the Builder keys on page ids and the cost model's doses | Tom / catalog | drink data correctness |
| U-MB-10 | **CLOSED 2026-10-01.** Tom: the name from the existing Canva drinks menu only, no new description copy (§7.3) | — | — |
| U-MB-11 | Images: 48 drink photos exist on the Shopify CDN at 925×1052 (gt-site `photos.json`); their licence for self-hosting in the portal is GT's own (Canva exports) | — | images |
