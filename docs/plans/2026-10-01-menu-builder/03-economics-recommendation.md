# MB-D04 — Which economics the Builder shows, and under what names

> Owner-minded recommendation, Session 1, 2026-10-01. Status: **OPEN — put to Tom.** Follows MB-D08/MB-D03 (approved). Evidence: `evidence/2026-10-01-drinks-products-data-map.md` §A, §B, §2 C11; Sales-Machine `doctrine/commercial-terms.md` §1–§2.1; `decisions.md` D-012, D-018, D-025; `knowledge/answers/answer-bank.yaml` `is_it_profitable`; `claims#vat_presentation`.

## What I found

1. **Four of Tom's rules point in different directions on food cost.** D-018 (2026-08-31): the system never states the opening menu's price or the food cost per drink in conversation; the recommended consumer price stays public. D-025 (2026-09-28): the PDF menus a lead receives print FOOD COST on every drink page. The approved answer `is_it_profitable` says out loud "חליטה קרה עולה ₪3.25 ונמכרת ב-₪20 — 81% על ההכנסה נטו". The site shows no shekel figure (Tom 2026-09-24) but keeps margin percentages, which with the RRP imply the cost (U-047).
2. **The starter kit already shows "the opening menu's price".** Tom approved the kit total ex-VAT today, so the half of D-018 about the menu's price is superseded for the Builder.
3. **The figures are estimates by their own label.** `drinks_final_figures.json` `_meta.status`: ingredient cost on a standardized ice-filled 350 ml serving; ice, water, soda, garnish, packaging and labour excluded; milk and cream from retail prices, not invoices; pours unmeasured. Cost per cup uses GT list prices for 1 L / 1 kg packs. A 500 ml bottle gives ₪3.30 a cup, not ₪3.25.
4. **The lead already met the numbers.** Every lead who reaches the Builder came through the PDF (D-026) or the sales call; both show food cost, RRP, margin and profit per cup ("מה נשאר לך מכל כוס"). A Builder that hides the figure the PDF printed looks evasive, not discreet.
5. **VAT labelling is fixed doctrine.** Business prices ex-VAT and said so; consumer prices incl. VAT (D-012, `claims#vat_presentation`). The portal never multiplies by 1.18 and labels every amount.
6. **The trap is the aggregate, not the unit.** A "monthly profit" or "revenue potential" number needs a volume forecast the Builder refuses to ask for; it is the visually impressive ROI the masterprompt warns against (§24, §32).

## My recommendation

**Show the same four unit figures the PDF shows, per drink, in the PDF's words; never an aggregate projection.**

- **Drink card (selection) and "התפריט שלי":** the recommended consumer price, `₪20 · מחיר מומלץ לצרכן, כולל מע״מ`. Nothing else on the card.
- **One tap (progressive disclosure) per drink:** `עלות רכיבים לכוס ≈ ₪3.25 · נשאר לך ≈ ₪13.70 לכוס · 81%`, with the PDF's footnote once per screen: `עלות רכיבי המשקה בלבד, לפי מחירון · ללא קרח, סודה וקישוט · הערכה`. Same figures file, same formulas (`profit = price/1.18 − cost`).
- **"ערכת הפתיחה שלכם":** cash outlay only: line prices ex-VAT, total ex-VAT, VAT line, total incl. VAT, coverage in cups per product. No "this kit earns ₪X". The only bridge between the two layers is the coverage line, which is a count of cups, not money.
- **Pricing identity:** a lead sees list-based costs (as printed); an existing customer with own prices still sees the list-based estimate, labelled `לפי מחירון`, because the figures file has no per-customer variant and understating a cost is the one error GT cannot afford.
- **Never shown:** GT's own margins (`v_fg_unit_economics`), monthly or weekly profit, revenue potential, "savings", payback.

## Why this is best for GT

- **Consistency builds trust.** The PDF, the call, the FAQ answer and the Builder say the same number. D-025 already made the figure customer-facing for this lead; the Builder only has to agree with it.
- **Honest by construction.** Unit figures are facts from one file with their assumptions attached; the kit shows what the customer pays; nothing on the screen requires a forecast. "Consumed ≠ purchased" stays visible: the cup figure and the kit figure are different numbers with different labels.
- **The selling argument survives.** "₪3.25 → ₪20" is GT's best line (sales-motion s02); hiding it in the one place the customer makes the decision would be the only place GT stops selling.
- **Progressive disclosure keeps the card clean.** The RRP alone answers "what can I charge"; the cost line answers "is it worth it" only for who asks (masterprompt §20).

## Strongest alternative

**RRP only, no cost anywhere in the Builder** (D-018 read literally). For: the curiosity bait Tom wanted on 2026-08-31 stays intact; zero exposure of estimates. Against: the lead already holds the PDF with the cost printed (D-025), so the bait is gone; the approved answer bank states it; the site's margin % leaks it (U-047); the Builder would be the one GT surface that refuses a number the others volunteer.

Also set aside: an economics overview screen with projected monthly profit (needs the forecast we refused; the ROI trap).

## Dependencies and conditions

- Visible only behind a personal link (identity). If placement P1 ever lands the Builder on the site without identity, the site's no-prices rule governs and the economics layer is off (MB-D01).
- The figures file is read server-side at request time; the Builder never ships a copy to the client (DL-17).
- Copy goes to Tom through the §5 register batch with the rest of the Builder's Hebrew.

## Decision requested

Approve the four unit figures per drink behind one tap, RRP on the card, cash outlay only on the kit, no projections; or strike the cost line and keep RRP only.
