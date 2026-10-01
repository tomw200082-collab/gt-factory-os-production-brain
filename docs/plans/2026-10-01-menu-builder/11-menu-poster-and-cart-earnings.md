# Menu poster before the cart, and what the cart earns

> Tom, 2026-10-01: after choosing drinks the customer first sees them as a real menu (a chosen background, titles, the GT logo, something that could later be printed as a poster for the café's entrance). Only after approving it does the customer reach the cart. The cart shows what the products cost **and how much the customer can make from them**, and the order is placed from there.
> Tom's go, same day: "תשתמש במילה רווח ולא נשאר לכם. Go. קח את הרקעים שיש לנו בקאנבה בתיקיית הרקעים… כתב heebo. עם המחיר ליד כל משקה ועם הסימן ₪."
> Status: **built in the preview** (gt-factory-os `claude/menu-builder-preview`, `api/src/portal/builder/`, commit `bf9cf213`; https://claude.ai/artifact/2BrWABm82tPHyMwiSuFPQj version 3). Not routed, not deployed. Changes spec 09 §6–§7 and §16.

## 1. Flow

`BUILD` → **`MENU` (the poster)** → `KIT` (the cart, with what it earns) → send → `DONE`

- The bar, the side panel and the "התפריט שלי" sheet now lead to the menu (`לראות את התפריט ←`), not to the cart.
- The menu's primary action is `התפריט מאושר · לעגלה ←`. The cart's back action returns to the menu, and the menu's back action returns to the drinks.
- The "התפריט שלי" list left the top of the cart; the poster replaced it.

## 2. The poster

The poster is composition, not image editing: a background, the customer's drink cut-outs, names, prices, and the logo.

- **Format:** portrait, 1 : 1.414 (A4/A3). Every length is in container units, so the phone shows exactly what would print.
- **Backgrounds:** six of the eleven in Canva "Backgrounds / Clean backgrounds" (GT's palm-shadow set):
  - light, with dark text: חול (the default, the same family as Tom's own "תפריט הפתיחה המומלץ" design), מרווה, אפרסק, חרדל;
  - dark, with cream text and a yellow price: טורקיז, שזיף.

  They were exported at full size through a scratch copy in Canva ("Menu Builder — background export (scratch copy, safe to delete)", `DAHWw9x93-A`). The page carries 1200 px WebP files of 18–45 KB each.
- **Type:** Heebo throughout.
  - The title is the business name if the customer typed one, else `תפריט המשקאות`, sized by its length.
  - Under the title: the groups on the menu (`תה קר · מאצ׳ה · צ׳אי מסאלה`) and a short rule.
- **Each drink:** the glass, its name, and the recommended consumer price with the shekel sign (`₪20`, as in Tom's Canva pages). Prices cannot be edited, because every profit figure depends on them.
- **Layout by size:**
  - **Up to 20 drinks:** tiles. The page tries every column count and keeps the one with the largest glass that still fits, every name whole on at most two lines, preferring full rows.
  - **Beyond 20:** a two-column list with section titles. The columns split where they balance best, and a section split across them repeats its title.
  - **Names are never cut.** An estimate chooses the layout; the browser then measures, and shrinks type and glasses together if anything would wrap a third line or reach the footer.
  - Checked at 1, 2, 3, 4, 6, 8, 12, 16, 24 and 48 drinks.
- **Footer:** the GT Everyday logo, dark or light to suit the background.
- **Under the poster:**
  - the background swatches (a radio group that works with the arrow keys);
  - `שם העסק` (optional, at most 40 characters), which also pre-fills the order form's `שם העסק`;
  - the approve button and `עריכת המשקאות`.
- **Not in the preview:** saving the poster as an image and printing it. The preview cannot download files. In the real portal this is a canvas PNG and, later, an A3 PDF made on the server. Print needs the Canva originals (the preview's 1200 px files are for the screen) and page 20's re-export.

## 3. What the cart earns

**The number:** money left after every ingredient of the drink, if every cup the cart pours is sold at the recommended price. It is ex-VAT, the same basis as the cart total. Tom's word is **רווח**. The conditions sit directly under the figures:

`אם כל הכוסות נמכרות במחיר המומלץ שבתפריט. אחרי עלות כל רכיבי המשקה. לא כולל קרח, סודה, כוסות, עבודה ושכירות.`

**Method (`kit.mjs` `computeEarnings`, run by the server build too):**

1. **Cups.** Every drink on the menu sells the same number of cups until a product it needs runs out. The drinks that can still be made keep selling (max-min fair "water-filling"). Each cup is counted once, and no product pours more than the cart holds.
2. **Profit per cup** = `price / 1.18` − the figures' other ingredients − the GT products at the cart's own line price.
   - The other ingredients are milk, syrup, lemon and the like, measured as `cost` − the GT products at the default pack (verified ≥ 0 for all 48 drinks).
   - The cart's own line price means a 500 ml bottle earns slightly less per cup than a litre.
3. **Payback:** the cups, in the same mix, whose takings net of the other ingredients repay the cart.

**This replaces the first draft's method.** The first draft split each product evenly and limited every drink by its scarcest product. That dropped cups the cart actually pours. On the opening menu it left out 114 of the 405 cups, mostly matcha the café paid for: one 500 g bag makes 277 cups, while the tea runs out after 44.

| Starting menu | Cart before VAT | First draft (even split, min) | **Built (each cup once, nothing left to pour)** | Cups | Payback (cups) |
|---|---|---|---|---|---|
| opening | ₪1,100 | ₪5,214 · 291 cups | **₪7,347** | 405 | 53 |
| matcha | ₪960 | ₪5,123 · 254 | **₪5,484** | 272 | 42 |
| tea | ₪1,270 | ₪5,223 · 320 | **₪5,222** | 320 | 63 |
| chai | ₪910 | ₪5,117 · 280 | **₪5,117** | 280 | 43 |
| ube | ₪1,255 | ₪4,547 · 240 | **₪4,746** | 250 | 57 |

The naive per-bottle sum (₪8,390 for opening) still double counts two-product cups and is not used anywhere.

**On screen (top of the cart, a dark-green card in the palette of Tom's figures pages, profit in yellow):**
- **Heading:** `כמה אפשר להרוויח מהעגלה`.
- **Three tiles:** `עלות העגלה ₪1,100 · לפני מע״מ` · `כוסות ≈405 · מהמוצרים בעגלה` · `רווח ≈₪7,347 · לפני מע״מ`.
- **Payback line:** `העגלה מחזירה את עצמה אחרי כ־53 כוסות, מתוך 405`.
- **The conditions.**
- **`פירוט לפי משקה`:** each drink with its cups × profit per cup, ordered by profit, adding up exactly to the total. Below it, one sentence on how it was counted.

**Elsewhere in the cart:**
- **Each product line** says how many cups it goes into: `≈44 כוסות: …`. This uses the same allocation, so the card and the lines tell one story. (The engine's `coverage` field, AC 5, is unchanged and still tested.)
- **Automatic round-up to the minimum:** the note now says what the added units make, e.g. `הוספנו 12 × Namastea 1 ליטר · זה עוד ≈240 כוסות ו־≈₪4,387 רווח.` This makes the minimum read as stock, not as a penalty.
- **The totals** end with `רווח משוער מהעגלה, לפני מע״מ ≈₪7,347`, next to the send button.
- **Live updates:** changing a quantity, size or sugar-free option recomputes everything. Adding a product whose drinks are limited by another product adds no cups, which is the honest signal.

**Drink detail:** the tile `נשאר לכם מכל כוס` is now `רווח לכוס`. The footnote reads `רווח = המחיר המומלץ פחות מע״מ, פחות עלות רכיבי המשקה`.

## 4. Decisions this changes

- **MB-D04 / spec §16 ("no projections"):** changed by Tom. The cart shows cost, cups, profit and payback under the conditions above (MB-R14). This is still owed to the D-018 doctrine record (DL-20).
- **MB-R08 (copy `נשאר לכם`):** changed by Tom to `רווח` (MB-R14).
- **Spec §7.4:** the "התפריט שלי" list left the cart; the poster replaced it (MB-R15).
- **Doc 11 first draft, §3 method:** replaced by the method above (MB-R16).

## 5. Verified (2026-10-01)

- `node --test api/src/portal/builder/kit.test.mjs`: **14/14**. The 6 new tests cover:
  - a shared product;
  - a two-product cup counted once;
  - water-filling;
  - 500 ml pricing;
  - the five sets;
  - 400 random menus: never pours more than the cart holds, drinks add up, nothing left to pour.
- Playwright on Chromium at 390 × 844, 320 × 640 and 1440 × 900:
  - the full flow (drinks → menu → six backgrounds → business name → cart → back to menu → back to drinks; chai round-up → below minimum → complete → send → done);
  - axe: 0 violations on the menu and the cart;
  - horizontal overflow 0 at 320, 390 and 1440;
  - the poster fits at all ten sizes with no name cut;
  - no console errors.
