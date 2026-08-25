# Lead-welcome menu — Hebrew copy deck (15 screens)

> **What this is.** The approved-source copy for every one of the 15 screens defined in the
> masterprompt `20260825leadwelcomemenumasterprompt.md` §W3. This file is the copy source that
> `build.py` will read; it is **not** the design and **not** the build.
>
> **Status:** APPROVED-IN-PART — copy complete. Tom settled NAMASTEA ingredients and the contact
> block on 2026-08-25; two items remain in §Open, neither blocking the build.
> **Written:** 2026-08-25. **Language of the deliverable:** Hebrew, RTL.
>
> **Numeric authority:** `.claude/skills/drinks-pricelist/drinks_final_figures.json`.
> Verified 2026-08-25: all 12 keys present, all four fields of all twelve match masterprompt §2.2
> exactly, and match the SUMMER 2026 Canva drinks catalog `DAHPi9gpfts` page-for-page.
> No figure in this file was produced here. Nothing was recomputed, adjusted or corrected.
>
> **Derived values** are marked `[DERIVED]`. `build.py` recomputes them from the twelve rows;
> the value shown is what that computation returned on 2026-08-25. Never hardcode them.

## Sources

| Source | Used for | Grade |
|---|---|---|
| `.claude/skills/drinks-pricelist/drinks_final_figures.json` | every cost / price / margin / profit | approved-Tom 2026-08-05 |
| Canva drinks catalog `DAHPi9gpfts` (read-only) | preparation steps, drink descriptions, ingredient panels | shipped catalog |
| Canva products catalog `DAHQrpThEBE` (read-only) | product descriptions, ingredient lists, contact block | shipped catalog |
| `docs/warehouses/catalog-truth.md` | what GT actually sells — **overrides the products catalog** | approved-Tom 2026-08-06 |
| Dropbox `/Data Center/PRODUCTION 2/B-BAGEL-Tea-Programme/index.html` | vision line, three-move pour, 5:1 ratio, storage, clean-label claims, 17 kcal | shipped to customer |

---

## S01 · Cover

- **Brand mark:** GT logo.
- **Eyebrow:** `GT · תפריט הפתיחה`
- **Headline:** `ארבע תמציות.` / `שנים־עשר משקאות.` / `תפריט משקאות רווחי.`
- **Vision line** (B-Bagel, translated): `המשקה הטוב יותר, הבחירה הקלה, לכולם.`
- **The four products, one line:** `FRESH · DETOX · NAMASTEA · MATCHA`

## S02 · The promise

- **Headline:** `4 מוצרים → 12 משקאות`
- **Profit line:** `רווח לכוס: ₪12.34–₪19.78` `[DERIVED: min/max of prof across the twelve]`
- **Yield line:** `20–25 כוסות מכל בקבוק` (products catalog `DAHQrpThEBE`)
- **Margin line:** `שוליים 71%–85%` `[DERIVED: min/max of marg across the twelve]`
- **Clean-label strip** (B-Bagel): `ללא חומרים משמרים · ללא צבעי מאכל · ללא תמציות טעם`
- **Calorie note** (B-Bagel): `17 קק״ל ל־100 מ״ל מוכן`

## S03 · The mapping

Diagram screen. Copy is labels only — the drawing is masterprompt §W2 Movement 4.

- **Title:** `מאיזה מוצר מיוצר כל משקה`
- **Spine labels:** `FRESH` · `DETOX` · `NAMASTEA` · `MATCHA`
- **Drink labels:** the twelve names exactly as written in S05–S12 below.
- **The one crossing:** `אייס מאצ׳ה מסאלה` hangs off both `MATCHA` and `NAMASTEA`. It is the only
  drink in the deck that consumes two GT products — that is why it is the only crossing line.
- **Caption:** `משקה אחד בלבד מחבר שני מוצרים.`

## S04 · How it is made

- **Title:** `פשוט להגיש`
- **Sub:** `כוס מושלמת בשלוש תנועות`
- **Steps** (B-Bagel three-move pour):
  1. `מלאו כוס בקרח.`
  2. `השלימו במים קרים.`
  3. `הוסיפו את תרכיז GT, ערבבו קלות, סיימו בפרוסת לימון או נענע טרייה — והגישו.`
- **Ratio callout:** `5:1` — `250 מ״ל נוזל ל־50 מ״ל תרכיז. התרכיז תמיד נכנס אחרון.`
- **Storage block:**
  `באחסון סגור — מקום קריר ויבש, לא דורש קירור.`
  `לאחר הפתיחה — לשמור בקירור; מומלץ עד 3 חודשים.`
- **Team line** (B-Bagel): `GT נבנה לצוותים עמוסים — קל להכניס, קל לתפעל, בכל משמרת.`

---

## S05 · FRESH — the product and its three drinks

**Product** (products catalog `DAHQrpThEBE`):
`FRESH · חליטה תאילנדית` — `רכיבים: פרחי היביסקוס ולײם`
`משקה מעורר ללא קפאין. צבע אדום עז, בולט ומסקרן. טעם חמצמץ עדין שמחזיר לקוחות שוב ושוב.`

| drink | FOOD COST (ex-VAT) | מחיר מומלץ (incl. VAT) | שוליים | רווח לכוס |
|---|---|---|---|---|
| `חליטת היביסקוס וליים` | `₪3.76` | `₪19` | `77%` | `₪12.34` |
| `חליטת תפוח היביסקוס` | `₪3.25*` | `₪24` | `84%` | `₪17.09` |
| `גזוז היביסקוס ותפוח` | `₪3.62*` | `₪22` | `81%` | `₪15.02` |

One-line preparation each:
- `חליטת היביסקוס וליים` — `קרח · 50 מ״ל תרכיז GT · השלימו ל־⅔ במים קרים (או סודה למוגז) · סלייס לימון ונענע`
- `חליטת תפוח היביסקוס` — `קרח · 40 מ״ל מיץ תפוחים · 40 מ״ל תרכיז GT · השלימו ל־⅔ במים · גרניש`
- `גזוז היביסקוס ותפוח` — `קרח · 40 מ״ל מיץ תפוחים · 40 מ״ל תרכיז GT · השלימו ל־⅔ בסודה (~150 מ״ל) · גרניש`

## S06 · FRESH hero — `חליטת תפוח היביסקוס`

- **Figures, large:** `₪3.25*` FOOD COST · `₪24` מחיר מומלץ · `84%` שוליים · `₪17.09 לכוס`
- **Numbered preparation** (catalog verbatim):
  1. `מלאו כוס בקרח`
  2. `הוסיפו 40 מ״ל מיץ תפוחים`
  3. `הוסיפו 40 מ״ל תרכיז GT`
  4. `השלימו ל־⅔ במים`
  5. `קשטו בגרניש לפי טעם`
- **Ingredient panel:** `קרח · 40 מ״ל מיץ תפוחים · 40 מ״ל תרכיז GT · גרניש`

## S07 · DETOX — the product and its two drinks

**Product:** `DETOX · חליטה ישראלית` — `רכיבים: תה ירוק, לואיזה, נענע ולײם`
`טעם קליל ומרענן שלקוחות אוהבים בכל גיל. נרטיב בריאות ברור שכולם מתחברים אליו ומבינים.`

| drink | FOOD COST | מחיר מומלץ | שוליים | רווח לכוס |
|---|---|---|---|---|
| `חליטת תה ירוק וליים` | `₪3.76*` | `₪19` | `77%` | `₪12.34` |
| `חליטת תות לואיזה` | `₪5.41*` | `₪24` | `73%` | `₪14.93` |

- `חליטת תה ירוק וליים` — `קרח · 50 מ״ל תרכיז GT · השלימו ל־⅔ במים קרים (או סודה למוגז) · סלייס לימון ונענע`
- `חליטת תות לואיזה` — `קרח · 40 מ״ל מחית תות · 40 מ״ל תרכיז GT · השלימו ל־⅔ במים · גרניש`

**Note:** DETOX has exactly two costed drinks in the approved file. Settled — masterprompt §1.1.2.

## S08 · DETOX hero — `חליטת תות לואיזה`

- **Descriptor** (catalog): `משקה דגל על בסיס מחית תות`
- **Figures, large:** `₪5.41*` · `₪24` · `73%` · `₪14.93 לכוס`
- **Numbered preparation:**
  1. `מלאו כוס בקרח`
  2. `הוסיפו 40 מ״ל מחית תות`
  3. `הוסיפו 40 מ״ל תרכיז GT`
  4. `השלימו ל־⅔ במים`
  5. `קשטו בגרניש לפי טעם`

## S09 · NAMASTEA — the product and its three drinks

**Product:** `NAMASTEA · חליטה הודית`
`רכיבים: שני זני תה שחור, קינמון, הל, ג׳ינג׳ר, פלפל שחור, ציפורן.`
`טעם ייחודי, להיט מכירות ענק בקרב הקהל הישראלי. נפלא כמשקה קר — גם עם מי קוקוס. נפלא כמשקה חם — גם כלאטה בשילוב משקאות חלב.`

| drink | FOOD COST | מחיר מומלץ | שוליים | רווח לכוס |
|---|---|---|---|---|
| `אייס צ׳אי מסאלה קלאסי` | `₪5.00*` | `₪24` | `75%` | `₪15.34` |
| `צ׳אי מסאלה על הקרח` | `₪3.80*` | `₪24` | `81%` | `₪16.54` |
| `צ׳אי מסאלה קולד פואם וניל` | `₪3.95*` | `₪28` | `83%` | `₪19.78` |

- `אייס צ׳אי מסאלה קלאסי` — `קרח · ⅔ כוס חלב · 50 מ״ל מסאלה GT · קצף חלב · אבקת קינמון`
- `צ׳אי מסאלה על הקרח` — `קרח · ⅔ כוס מים · 50 מ״ל מסאלה GT · הרבה קצף חלב`
- `צ׳אי מסאלה קולד פואם וניל` — `קרח · ⅔ כוס מים · 50 מ״ל מסאלה GT · קצף קר חלבי עם וניל · מקל וניל`

## S10 · NAMASTEA hero — `צ׳אי מסאלה קולד פואם וניל`

The highest profit per cup in the deck.

- **Descriptor:** `צ׳אי מסאלה עם קצף קר חלבי בטעם וניל`
- **Figures, large:** `₪3.95*` · `₪28` · `83%` · **`₪19.78 לכוס`**
- **Numbered preparation:**
  1. `מלאו כוס בקרח`
  2. `השלימו ל־⅔ במים`
  3. `יצקו 50 מ״ל תרכיז מסאלה GT`
  4. `הכתירו בקצף קר חלבי עם תמצית וניל`
  5. `קשטו במקל וניל`

## S11 · MATCHA — the product and its four drinks

**Product:** `MATCHA · אבקת מאצ׳ה טקסית יפנית ממחוז שיזואוקה` — `רכיבים: תה ירוק`
`לא טרנד חולף — המאצ׳ה כאן כדי להישאר. אנו מייבאים את המאצ׳ה שלנו היישר מהחקלאים, בהטסה מרגע הקטיפה — כך נשמרות הטריות והאיכות.`

| drink | FOOD COST | מחיר מומלץ | שוליים | רווח לכוס |
|---|---|---|---|---|
| `אייס מאצ׳ה קלאסי` | `₪3.77*` | `₪26` | `83%` | `₪18.26` |
| `מאצ׳ה אגבה על הקרח` | `₪3.35*` | `₪26` | `85%` | `₪18.68` |
| `אייס מאצ׳ה תות` | `₪6.17*` | `₪26` | `72%` | `₪15.86` |
| `אייס מאצ׳ה מסאלה` | `₪6.37*` | `₪26` | `71%` | `₪15.66` |

- `אייס מאצ׳ה קלאסי` — `קרח · ⅔ כוס חלב · 50 מ״ל מאצ׳ה (1.8 גר׳) · קצף חלב`
- `מאצ׳ה אגבה על הקרח` — `קרח · ⅔ כוס מים · 15 מ״ל סירופ אגבה · 50 מ״ל מאצ׳ה (1.8 גר׳) · קצף חלב`
- `אייס מאצ׳ה תות` — `קרח · 40 מ״ל מחית תות · ⅔ כוס חלב · 50 מ״ל מאצ׳ה (1.8 גר׳) · קצף חלב`
- `אייס מאצ׳ה מסאלה` — `קרח · 40 מ״ל תמצית מסאלה GT · ⅔ כוס חלב · 50 מ״ל מאצ׳ה (1.8 גר׳) · קצף חלב`

**Asset note:** no Tom-approved MATCHA packshot exists (masterprompt §2.4, §6.A). This screen
carries a typographic placeholder until Tom picks one.

## S12 · MATCHA hero — `מאצ׳ה אגבה על הקרח`

The highest margin of all 48 approved drinks.

- **Descriptor:** `אגבה מאצ׳ה אייס, קליל על הקרח`
- **Figures, large:** `₪3.35*` · `₪26` · **`85%`** · `₪18.68 לכוס`
- **Numbered preparation:**
  1. `מלאו כוס בקרח`
  2. `הוסיפו 15 מ״ל סירופ אגבה`
  3. `השלימו ל־⅔ במים`
  4. `יצקו 50 מ״ל תרכיז מאצ׳ה (1.8 גר׳)`
  5. `הוסיפו קצף חלב מלמעלה`

No glass photograph exists for MATCHA. Packshot plus typography only — masterprompt §2.4.

---

## S13 · What to order from GT

Names and roles. **No prices** — Tom's ruling, masterprompt §1.1.5.

- **Title:** `מה מזמינים מ־GT`
- `FRESH · חליטה תאילנדית` — `היביסקוס ולײם. הבסיס לשלושה משקאות בתפריט.`
- `DETOX · חליטה ישראלית` — `תה ירוק, לואיזה, נענע ולײם. הבסיס לשני משקאות.`
- `NAMASTEA · חליטה הודית` — `מסאלה צ׳אי. הבסיס לשלושה משקאות — וגם לאייס מאצ׳ה מסאלה.`
- `MATCHA · מאצ׳ה טקסית שיזואוקה` — `הבסיס לארבעה משקאות.`
- `SMOOTHIE · מחית תות` — `50% פרי. נדרשת לשני משקאות: חליטת תות לואיזה ואייס מאצ׳ה תות.`
- **Footer line:** `בקבוק תמצית: 20–25 כוסות. באחסון סגור — ללא קירור.`

**Do not add** `GT Elita מאצ׳ה פחית 30 גרם`, `מאצ׳ה שיזואוקה 50 גרם`, `מקציף קוקטיילים`,
`קנקן נפוליטן עם מסננת`. All four are still live in the Canva products catalog and all four are
Tom-confirmed negative records in `catalog-truth.md` (2026-08-06): not sold. Masterprompt landmine 4, D6.

## S14 · What you already have

**Title:** `מה שכבר יש לכם במטבח`

Derived 2026-08-25 by taking the union of the ingredient panels of all twelve catalog pages and
subtracting every GT product. Result:

`קרח` · `מים קרים` · `סודה` · `חלב או תחליפי חלב` · `קצף חלב` · `מיץ תפוחים` · `סירופ אגבה` ·
`אבקת קינמון` · `תמצית וניל ומקל וניל` · `לימון` · `נענע טרייה` · `גרניש לפי טעם`

**Reconciliation against the masterprompt §W3 reconnaissance list** (milk, cream, apple juice,
soda, agave syrup, lemon, mint, cinnamon, vanilla):

- Confirmed, all nine: milk, apple juice, soda, agave syrup, lemon, mint, cinnamon, vanilla —
  and **cream is not confirmed.** No catalog page calls for cream. What the pages call for is
  `קצף חלב` / `קצף קר חלבי` — milk foam, made from milk. Copy says milk foam, not cream.
- **Added by the derivation, absent from the reconnaissance list:** `קרח` and `מים` — required by
  all twelve, and the two most obviously-already-owned items on the screen.
- `מחית תות` and `תמצית מסאלה GT` are GT products, so they sit on S13, not here.

**Closing line:** `כל השאר כבר אצלכם. מ־GT מגיעים רק התרכיזים.`

## S15 · Closing

Leads with the promise. Contact block second, lower, at body scale or smaller — Tom explicit,
masterprompt §1.1.7 and D8.

- **The promise, largest element on the screen:** `נחזור אליכם בהקדם.`
- **Second line, below it:** `נשמח להתאים לכם את התפריט — לפי מה שאתם מוכרים היום.`
- **Contact block, secondary, at or below body scale:**
  `gteveryday.com` · `info@gteveryday.com` · `054-398-2444` · `gteveryday@`
- **Sign-off:** `המשקה הטוב יותר, הבחירה הקלה, לכולם.`
- GT logo. This screen and the cover are the only two that carry it.

---

## The asterisk

`* כולל הערכת עלות גרניש/קצף` — carried verbatim from the catalog, once, as a footnote.

The catalog marks **eleven of the twelve** with it; the only drink without it is
`חליטת היביסקוס וליים` (key 8). This file carries the asterisk exactly where the catalog does,
per masterprompt §2.2. Note that `drinks_final_figures.json` carries the asterisk on key `12`
only — the two disagree on the other ten. Nothing was changed on either side. Listed in §Open.

## The VAT rule

FOOD COST is ex-VAT. The recommended price includes 18% VAT.
`profit = price/1.18 − cost` · `margin = profit / (price/1.18)`.

Computing margin as `(price − cost)/price` overstates every drink by 2–5 points. The
`שוליים מוצע` column of `foodcost_proposal.csv` does exactly that — never read figures from it.

Re-derived independently on 2026-08-25 against all twelve rows: every margin and profit in this
file reproduces from cost and price under the rule above. Zero deviations.

## Open — Tom's

**Resolved by Tom, 2026-08-25:**

1. ~~NAMASTEA ingredients.~~ **Settled: follow the products catalog** (`לך לפי הקטלוג מוצרים`).
   `שני זני תה שחור, קינמון, הל, ג׳ינג׳ר, פלפל שחור, ציפורן.` No Pu-erh, no star anise —
   the B-Bagel brochure's longer list does not carry into this deck.
2. ~~The contact block.~~ **Approved as read off the products catalog footer** (`מאשר את פרטי הקשר`):
   `gteveryday.com` · `info@gteveryday.com` · `054-398-2444` · `gteveryday@`.

**Still open:**

3. **The asterisk spread.** The drinks catalog marks eleven of the twelve with
   `* כולל הערכת עלות גרניש/קצף`; `drinks_final_figures.json` marks one (key `12`). This file
   follows the drinks catalog, per masterprompt §2.2 (`carry the asterisk and its footnote,
   exactly as the catalog does`). Neither side was changed. Tom's ruling on the products catalog
   does not reach this — the asterisk lives in the drinks catalog. Carrying the wider disclosure
   is the conservative default and it stands until Tom says otherwise.
4. **The MATCHA image** for S11 — no approved packshot exists at bottle quality. Masterprompt §6.A
   says explicitly not to block on this: S11 builds with a typographic placeholder and the image
   drops in when Tom picks one from the contact sheet.

Drink-name divergence, recorded not resolved: key `12` is `חליטת תה ירוק וליים` in both the
figures file and masterprompt §2.2, and `חליטת תה ירוק לואיזה וליים` in the Canva drinks catalog.
This file uses the figures-file name.
