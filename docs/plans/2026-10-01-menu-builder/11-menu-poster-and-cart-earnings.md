# Menu poster before the cart, and what the cart earns (design, not built)

> Tom, 2026-10-01: after choosing drinks the customer first sees them as a real menu (a chosen background, titles, the GT logo, something that could later be printed as a poster for the café's entrance). Only after approving it does the customer reach the cart. The cart shows what the products cost **and how much the customer can make from them**, and the order is placed from there.
> Status: design for Tom. Changes spec 09 §6–§7 and §16 once approved. Not built.

## 1. New flow

`BUILD` → **`MENU` (the poster)** → `KIT` (cart + earnings) → send → `DONE`

The poster replaces the "התפריט שלי" list at the top of today's KIT. The cart then starts with the products.

## 2. The poster screen (feasible: composition, not image editing)

The drink photos are transparent cut-outs, normalised to one size and centred (`normalize-photos.py`). So the page can compose a menu live from layers: background, the customer's drinks, names, prices, logo. No Photoshop step exists.

- **Format:** portrait at the print ratio 1 : 1.414 (A-series), drawn at a fixed design size and scaled to the phone's width, so what the customer sees is what would print.
- **Layout by count:** 1–4 drinks in large tiles · 5–8 in a 2-column grid · 9–12 in 3 columns · more than 12 as a text menu with small photos. Drinks are grouped by `תה קר · מאצ׳ה · צ׳אי מסאלה · אובה` with section titles, the way a menu board reads.
- **On each drink:** photo, name, recommended consumer price incl. VAT (the number the café charges). Prices are not editable in V1, because every earnings figure depends on them.
- **Header:** the business name if the customer types it (optional field under the poster, default `התפריט שלנו`). It pre-fills `שם העסק` in the order form, so one field moves earlier and reads as ownership, not a form.
- **Footer:** the GT Everyday logo, small.
- **Background:** three curated choices (light paper · dark ink · GT green), picked with swatches under the poster. No free colour picker; the set keeps every combination legible.
- **Actions:** `התפריט מוכן · להמשך ←` (primary) · `עריכה` (back to BUILD).
- **Save as image:** in the real portal the page draws the same poster onto a canvas and offers it as a PNG. The preview page cannot download files, so it shows the poster only. A print-ready A3 PDF is a later server step.
- **Print limits found:** page 20's only clean cut is 298 × 520 px (fine on a phone, soft at A3), so it needs a re-export from Canva `DAHUB_z-lP0`. Print also needs the logo as a vector or a high-resolution file; the portal's `logo.png` is 7 KB.

This is not the struck 24-hour branded-menu reward (MB-D08): nothing is promised or printed. It is the customer's own menu, shown before the cart.

## 3. Earnings on the cart (the precise part)

**What the number is:** money left after ingredient costs if every cup the kit makes is sold at the recommended price. Ex-VAT, the same basis as the cart total: `kept(d) = price/1.18 − cost`, from the approved figures file.

**What it is not:** profit. Ice, soda, garnish, cups, labour and rent are excluded (the figures file's own basis). So the label is the PDF's approved term `נשאר לכם`, never `רווח`, and the condition is stated: `אם כל הכוסות נמכרות במחיר המומלץ`.

**The trap measured:** multiplying each bottle's cups by its drinks' `kept` and summing the lines (Tom's example, applied line by line) counts a cup of a two-product drink once per product.

| Starting menu | Cart before VAT | Per-bottle sum (double counts) | Correct: each cup once | Cups |
|---|---|---|---|---|
| opening | ₪1,100 | ₪8,390 | **₪5,214** | 291 |
| matcha | ₪960 | ₪8,709 | **₪5,123** | 254 |
| tea | ₪1,270 | ₪7,905 | **₪5,223** | 320 |
| chai | ₪910 | ₪5,117 | **₪5,117** | 280 |
| ube | ₪1,255 | ₪13,761 | **₪4,547** | 240 |

Menus with one product per drink agree (chai). Two-product menus overstate up to 3×. A customer who later finds the number inflated stops trusting every number GT shows.

**Method (server-side, in `kit.mjs`):**
1. Split each product's volume evenly among the drinks that use it: `share(P) = volume(P) / Σ dose`.
2. Each drink gets the cups its scarcest product allows: `cups(d) = floor(min share(P))`.
3. Earnings = `Σ cups(d) × kept(d)`.

This is conservative: stock a drink could not use under an even mix is not counted. Each line shows its cups, and the lines of the drinks' main product (concentrate or powder) carry their earnings. Purée lines show `משמש ב־…` and no shekels, so the lines add up exactly to the total.

**On screen (cart top, one card, same VAT basis on both sides):**
`העגלה: ₪1,100 לפני מע״מ` · `מהמוצרים האלה ≈291 כוסות` · `נשאר לכם ≈₪5,214 לפני מע״מ`, with one line under it: `אם כל הכוסות נמכרות במחיר המומלץ, אחרי עלות הרכיבים. ללא קרח, סודה, כוסות ועבודה.`

Then the lines, the totals with VAT, the three fields and the send button, as today. The order is placed from this screen.

## 4. Decisions this changes

- **MB-D04 / spec §16:** "never projections". Tom now asks for a cart-level earnings figure. It is shown under the conditions above. This also goes into the D-018 doctrine record (DL-20).
- **Spec §7.4:** the "התפריט שלי" list leaves the KIT; the poster replaces it.
- **New copy:** for Tom's register (poster header default, three background names, the summary card, the purée line).
