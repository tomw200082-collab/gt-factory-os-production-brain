# MB-D06 — How the customer discovers and chooses drinks (the selection model)

> Owner-minded recommendation, Session 1, 2026-10-01. Status: **OPEN — put to Tom.** Follows MB-D08/MB-D03/MB-D04 (approved). This is the *model* of selection; the millimetre UX (screens, copy, motion) is designed after the model is agreed (Tom 2026-10-01: "בהמשך גם צריך לחשוב טוב ולהעמיק את כל הצורה שבה יקרה ה-UX").
> Evidence: `evidence/2026-10-01-drinks-products-data-map.md` §A.3–A.4; `sales_core.app_setting.lead_menus`; Sales-Machine D-013, D-026, `knowledge/segments/sales-motion.yaml` (expansion map), `knowledge/products/catalog.yaml` (`requires_second_product`, `requires_equipment`, `caffeine_free`).

## What I found

1. **48 drinks fall into exactly the four lead-menu groups.** Tea 17 (iced tea 7, lemonade 3, signature 4, gazoz 3), matcha 16 (iced 6, specials 5, coconut 5), chai 10 (chai 6, cold foam 4), ube 5. The lead-menu keys `tea · matcha · chai · ube` cover all 48; `opening` is a cross-group pick of 8. One vocabulary for the campaign context, the PDFs and the Builder (DL-19).
2. **Five curated sets already exist and are Tom-approved** (D-026, Canva copies, ≤8 drinks each: opening 8, matcha 8, tea 8, chai 8, ube 5). Nothing new needs curating; the Builder can start from them.
3. **The expansion map is the real structure of a good menu.** 32 drinks need one GT product, 16 need two. Within a bottle the customer already has, lemonade and gazoz are free (same FRESH bottle makes היביסקוס-ליים, לימונדת היביסקוס, גזוז היביסקוס ותפוח); NAMASTEA alone opens 11 drinks from what a bar already stocks; matcha + purée opens three more; ube never stands alone. Sales doctrine says expansion is bought with "yes", towards what asks least of the bar.
4. **The lead already saw inspiration.** Every lead holding the link has the PDF of ≤8 drinks (or came off a call). DR-02 says the Builder must not re-present it as a step; it must turn it into choices.
5. **Operational facts exist per product, not per drink:** `caffeine_free` (4 concentrates), `requires_equipment` (frother and milk for matcha/ube and cold foam), `requires_second_product` (ube). A drink inherits them.
6. **The failure modes to avoid** (masterprompt §32): overwhelming choice, filter-heavy browsing, wizards, forced questions, dead-end summaries.

## My recommendation

**One scrolling screen, grouped by what the customer serves, starting from a curated set, with the purchase consequence visible on every tap.**

- **Groups = the four lead-menu keys,** in this order unless a context says otherwise: תה קר · מאצ׳ה · צ׳אי מסאלה · אובה. A context (`?c=matcha`, DR-01) moves that group to the top; the rest stay below it. Sub-families (lemonade, gazoz, cold foam, coconut) are section labels inside the group, not filters.
- **Starting point = the matching curated set, pre-selected and editable.** No context → the opening menu's 8 drinks come pre-ticked under a one-line banner `התחלנו מתפריט הפתיחה המומלץ שלנו · הסירו, החליפו, הוסיפו`. Context `matcha` → the matcha menu's 8. One tap `להתחיל מאפס` clears it. This is D-013 as a product: one recommended start, never three packages.
- **A drink card is small and says one thing:** photo, name, `₪20 · מחיר מומלץ`, and the purchase consequence as a chip: `בבקבוק שכבר בחרתם` (free expansion, green) or `+ מוצר: NAMASTEA` (adds a product, neutral). Tap = select; selected state is the same as the ordering portal's in-cart card (ring, ✓). One tap on the name opens the detail (ingredients in customers' words, the four economics figures of MB-D04, the equipment note `דורש מקציף וחלב`, caffeine-free tag). No recipe steps (masterprompt §13).
- **The chip rule is the smart part.** Because the kit is computed live from the selection, the Builder knows at every moment which drinks cost nothing extra. Sorting inside each group puts free-expansion drinks first once a bottle is chosen, so the menu grows dense before it grows wide. This is GT's expansion playbook executed by the customer, without a salesperson and without a word of upsell copy.
- **No filters, no search in V1.** Two tags only, shown on the card, never as controls: `ללא קפאין`, `ללא סוכר` (sugar-free variants are a product swap at kit level, not separate drinks; see spec note).
- **"התפריט שלי" is a sticky bar,** not a page: `5 משקאות · 3 מוצרים` and the button `לערכת הפתיחה ←`. Tapping the bar opens a sheet listing the chosen drinks with remove, exactly the ordering portal's cart sheet pattern. No count cap; soft guidance appears only above 10 drinks: `רוב המקומות פותחים עם 4–8`.
- **Unavailable product (planner flag):** its drinks stay in place, greyed, `לא זמין כרגע`, not selectable; if the planner named an alternative product, the drink says so. A pre-selected set drops those drinks silently from the start and says `משקה אחד לא זמין כרגע` in the banner.
- **Existing customer entry (optional tile in the portal):** same screen; the starting point is the drinks their past orders already make (derived from the products they buy), pre-ticked, with the free expansions sorted first. This is Unit C's basket map read-only, nothing new to build on the Sales side.

Two screens in total: build, finish. No wizard, no questions.

## Why this is best for GT

- **The customer thinks in drinks; the system thinks in bottles; the chip is the only place they meet,** and it meets them honestly: every tap shows whether the menu just got wider or just got better.
- **Starting from the approved set removes the blank page.** The lead continues the PDF instead of re-reading it (DR-02), and most menus will be edits of a good default rather than constructions from zero.
- **Dense menus are better for everyone:** more drinks per bottle means a higher-margin menu for the café, a cheaper first order relative to its menu size, and a reorder habit for GT; wide menus with one drink per bottle are the surplus-in-the-fridge story.
- **One vocabulary everywhere.** Campaign, PDF, Builder and CRM context all speak `tea · matcha · chai · ube · opening`.
- **Nothing to curate, nothing to maintain beyond the figures file and the drink → product → dose table (DL-18).**

## Strongest alternative

**Empty start, grouped by GT product** ("choose your bottles, then see what they make"). For: mirrors the purchase; teaches the product line. Against: it is the catalog the lead already has; it asks the customer to think in SKUs (masterprompt §7); it makes the first screen a shopping decision instead of a menu decision. Set aside.

Also set aside: a step-by-step wizard (venue type → category → drinks); a search-and-filter catalog of 48; presets beyond the five approved sets ("summer", "high-margin") until data says a new one is wanted.

## Spec parameters (not for Tom now)

Sugar-free variants as a kit-level swap (FRESH / DETOX sugar-free bottle replaces the regular when the customer toggles `ללא סוכר` on the product line); the exact sort inside a group; what the banner says when the context set has unavailable drinks; the detail sheet's layout; the soft-guidance threshold.

## Decision requested

Approve: four groups in the lead-menu vocabulary, the matching curated set pre-selected as the start, the purchase-consequence chip on every card with free expansions sorted first, no filters, a sticky "my menu" bar, two screens; or tell me which part should be different.
