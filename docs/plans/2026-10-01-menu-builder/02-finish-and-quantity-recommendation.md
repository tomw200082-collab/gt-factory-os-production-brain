# MB-D08 + MB-D03 — The final output: what the lead holds when the Builder is done, and how quantities get there

> Owner-minded recommendation, Session 1, 2026-10-01. Status: **DECIDED by Tom, 2026-10-01** — layers 1, 2 and the action approved ("את אחת, שתיים ושלוש אני מאשר ומחזק מאוד"); the 24-hour branded-menu reward is **not added** ("את ארבע אל תוסיף"); one amendment to layer 2 (below). Recorded in `decision-ledger.md` as MB-D08 and MB-D03 (FINAL — PROVISIONAL on DL-06/DL-09).
>
> **Tom's amendment to layer 2 (the ₪800 rule):** "כאשר ההזמנה לא מגיעה למינימום המערכת אוטומטית מעגלת למעלה כדי שההזמנה תגיע למינימום את המוצר לפי העדיפות שלו — קודם תה 1 ליטר, אחר כך תה חצי ליטר ואז השאר." The suggestion ladder in the original text (free expansion first, then a product, then quantity) is replaced by this automatic round-up, see §Amendment. Asked right after Tom deferred placement (MB-D01) and said the final output is decided "ממש בקרוב, בסשן הזה".
> Evidence: `ground-truth.md` §1, §3, §5–§6; `evidence/2026-10-01-drinks-products-data-map.md` §A.4, §C; `evidence/2026-10-01-customer-portal-reconstruction.md` §4–§6.

## What I found

1. **Pack structure, not volume, decides a first order.** GT sells concentrates in 1 L (₪65, ≈20 cups at 50 ml) and 500 ml (₪33, ≈10 cups), matcha in 500 g (₪590, ≈277 cups) or a ₪170 kit whose contents are not recorded anywhere, ube 500 g (₪175, ≈250 cups), purées in 1 L pouches (₪60, ≈25 servings), and tea and purée sell in pairs. The recommended opening menu (8 drinks: FRESH, DETOX, NAMASTEA, matcha, strawberry purée) costs **₪1,100 ex-VAT in its minimum sellable units** (three concentrate pairs ₪390, matcha 500 g ₪590, a purée pair ₪120). It clears the ₪800 minimum before anyone forecasts a single cup. A two-drink tea menu does not (one concentrate pair = ₪130).
2. **Nobody knows a café's volume, least of all for a drink it has never sold.** No consumption data exists per café (data map §3 gap 1). Any forecast the Builder asks for is a guess the customer makes to satisfy a form.
3. **Reorder is cheap and frequent.** Centre deliveries run three times a week, north and south weekly, with a 14:00 cutoff; the ordering portal already does reorder-by-max in one tap. A small, honest first order costs the customer at most a few days of waiting, never a season.
4. **Tom's August doctrine said "no quantities"** ("לא יורדים לכמויות. הפלט של הקטלוג = סוגי מוצרים. מיפוי טעם-לסל, לא MRP", 2026-08-04, Sales-Machine PR #3, unmerged). It was written when the output went to a sales conversation. Today the output can go straight to the draft-only order link, and Tom said today "ואז לקבל את העגלה מוכנה".
5. **The emotional reward Tom wants is "this is my menu"** (masterprompt §19, §26), and GT already decided a reward that fits it exactly: the 24-hour branded-menu offer (D-011, 2026-08-04: order within 24 h and get the chosen menu designed with the customer's logo, print-ready, free; printing at their cost). Its automation was never built (U-012).
6. **Consumed ≠ purchased must stay visible** (masterprompt §24). The honest number per product is coverage in cups, which the data supports directly (pack servings × dose), not a "weeks of stock" claim that needs a forecast.

## My recommendation

**The finish is two layers and one action.** The customer sees "התפריט שלי" and, under it, "ערכת הפתיחה שלכם", then sends the order. No forecast question anywhere in V1.

**Layer 1 — התפריט שלי.** The drinks they chose, as a menu: name, recommended consumer price (incl. VAT, the public number by D-018), the drink photo. This is the artifact; it is what the 24-hour offer prints.

**Layer 2 — ערכת הפתיחה שלכם.** GT's computed starter kit, shown as an editable cart:

- **Rule:** for every GT product any chosen drink needs, the *minimum sellable quantity* in its default pack (a pair of 1 L bottles for a concentrate, one bag for a powder, a pair of pouches for a purée). Shared products are aggregated once across drinks; nothing is rounded per drink (masterprompt §25).
- **Each line says what it covers:** `FRESH · 2 × 1 ליטר · ≈40 כוסות של היביסקוס-ליים וגזוז היביסקוס` (coverage = pack servings × quantity, using the drinks' doses; mixed doses show the conservative number). This is the whole "consumed ≠ purchased" story in one line.
- **Editable with the portal's own stepper** (pairs step 2, carton +6). Removing a product greys the drinks that depend on it: `בלי FRESH אין היביסקוס-ליים`.
- **Total ex-VAT against the ₪800 minimum,** with the portal's meter. Below it, the assist offers, in this order: drinks that need no new product (free expansion, e.g. a lemonade or a gazoz from a bottle already in the kit), then one more product, then quantity.
- **Availability:** a product the planner marked unavailable cannot enter the kit; its drinks show `לא זמין כרגע` and are not selectable (the August gate: a drink whose product is out of stock is never offered as available).
- **Default packs are a parameter for the spec, not a question for Tom now:** 1 L for concentrates, 500 g for ube, a purée pair; matcha needs the kit's contents first (NEEDS DATA).

**One action, three doors.**
- Primary `לשלוח את ההזמנה`: a lead goes through the existing draft-only path (`customer_portal.lead_submission` → Shopify draft, never completed by the system, confirmation, Telegram); a customer goes through the normal order path with their own prices. No second order writer.
- `לשמור ולחזור אחר כך`: the personal link *is* the save; a WhatsApp "share to myself/partner" of the link. No account, no email.
- A quiet `רוצים לעבור על זה יחד? נחזור אליכם`: writes a lead event and, under Unit A, an owned task (the same shape as `רוצה לשמוע עוד`); the reply follows D-033 (FAQ link, no promised time).

**The reward.** If Tom keeps D-011: the finish states it plainly, `הזמנה תוך 24 שעות — התפריט הזה מעוצב עם הלוגו שלכם, מוכן להדפסה, במתנה`. The clock starts at **menu completion**, not at link send (D-011 counted from the link, which can be days before the lead builds anything). Fulfilment in V1 is manual in Canva at today's volume (a handful a month); the Builder only records the promise and the deadline on the lead.

**What the finish does not show in V1:** food cost per cup, profit per cup, monthly revenue projections. Whether and how economics appear is the next question (MB-D04).

## Amendment — the ₪800 round-up rule (Tom, 2026-10-01)

When the starter kit totals less than ₪800 ex-VAT, the system raises quantities **automatically** until the total reaches the minimum, by product priority:

1. tea concentrate 1 L;
2. tea concentrate 500 ml;
3. everything else (purées, powders).

Rules for the spec: only products already in the kit are raised (the menu never gains a product the lead did not choose); increments follow the sell unit (pairs for tea and purée, one bag for powders); within a priority tier, the product used by the most chosen drinks is raised first, then round-robin; the round-up is shown, never silent: one line under the total, `עיגלנו למינימום ההזמנה ₪800: הוספנו 2 × FRESH 1 ליטר`, and every raised line keeps its coverage text; the customer can still edit after the round-up, and the send button re-checks the minimum (server-side, as the portal does today). Open for the spec, not for Tom: a menu with no tea at all (ube- or matcha-only) reaches tier 3 immediately, so the round-up may add a second powder bag; the spec states the exact behaviour for that edge.

## Why this is best for GT

- **Zero cognitive load, full honesty.** No question the customer cannot answer; every number on the screen is a fact (pack, price, cups), not a projection.
- **The basket is right-sized by the product, not by a sales trick.** Minimum units of a real menu already clear ₪800 in most cases; the assist handles the rest with free expansion first, which is also GT's own expansion playbook (tea → lemonade/gazoz at zero new product).
- **Reorder carries the volume.** A café that sells more reorders within the week through the portal; GT learns real volume from orders, not from a form.
- **It is buildable on what exists.** Pricing, pairs, minimum, availability, draft-only submission, confirmation and alerts are all live code; the Builder adds the drink → product → dose table and the aggregation, both server-side.
- **Sales gets the right signal.** The kit and the menu land on the lead as events; a draft order becomes an owned task under Unit A; the quiet help door becomes a `reply` task.
- **The August anchor is kept in spirit.** No MRP, no forecast, product types first; the only addition is the smallest quantity that makes the menu real.

## Strongest alternative

**One question, scaled kit.** After the menu, one chip row: `כמה משקאות קרים ביום אצלכם, בערך? ≈10 · ≈30 · ≈60 · יותר`, scaling the kit to about two weeks of stock (rounded to pairs, labelled as an estimate).
- For: a bigger, more personal first basket; a volume signal for Sales.
- Against: the answer is a guess for a new menu; a wrong guess lands as surplus in the customer's fridge and as mistrust at GT's door; it reintroduces a form step; weekly delivery makes the gain small.
- Verdict: keep as a V1.1 experiment measured by acceptance and reorder, not as the launch model.

Also set aside: **menu only, no quantities** (the August doctrine as written) with the salesperson building the order. It keeps the human touch but loses every self-serve order and the "GT already worked out what I need" moment; and **cart only, no menu artifact**, which drops the reward the customer is building toward.

## What changes if Tom agrees

- MB-D08 and MB-D03 become FINAL (PROVISIONAL on DL-09 order handoff and DL-06 task kinds).
- The August "no quantities" line is recorded as superseded for the Builder.
- D-011 (24 h branded menu) is confirmed or struck, with the clock moved to menu completion.
- Next question: MB-D04, which economics the finish shows and under what names (food cost vs D-018 / D-025 / `show_prices`).

## Decision requested

Approve the two-layer finish with the zero-question starter kit, and say whether the 24-hour branded-menu offer stays; or stop me where you disagree.
