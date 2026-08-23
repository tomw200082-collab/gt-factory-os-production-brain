# GT Everyday — wholesale order page

**Master prompt for Antigravity.** Paste the whole thing as the opening message.
Everything factual in it is verified against the live catalog, the printed pricelist
artwork, and three months of real order data. Nothing here is a placeholder.

---

You are the design lead and front-end engineer on this build. Read the entire brief
before writing any code. Every fact below is verified — do not invent a product, a
price, a size, or a Hebrew string, and do not "improve" a number.

## 1. What you are building

GT Everyday is a small beverage factory in Israel. It sells tea-extract concentrates,
matcha, powders, fruit purées and brewing tools **wholesale to cafés, restaurants and
bars**. Today a café owner reorders over WhatsApp through a salesperson.

Build the page that replaces that conversation: a café owner opens it on a phone,
browses the catalog, builds an order, submits it, and shortly after receives a payment
link.

- **Primary user:** a café owner or bar manager, on a phone, mid-shift, reading Hebrew.
- **The page's single job:** make it obvious what GT sells and what it costs, and get a
  real order out of them without a phone call.
- **This is not a consumer shop.** Nobody buys one bottle. The buyer is restocking a
  bar for the week. Design for quantity, repetition and speed — not for browsing
  pleasure.

## 2. Hard rules — breaking any of these makes the build unusable

1. **Every displayed price is ex-VAT (ללא מע״מ).** Never add VAT. Never show a
   VAT-inclusive figure anywhere except the minimum-order line in §6.
2. **Never invent a product, price, flavour or description.** The catalog in §5 is
   complete and exact. If something seems missing, it is deliberately not sold.
3. **Hebrew, RTL.** `<html lang="he" dir="rtl">`. Every interface string in Hebrew.
   English appears only where it already does: product names (FRESH, DETOX, MATCHA)
   and small Latin eyebrows. **No lorem ipsum and no machine-translated Hebrew** —
   write real copy, or use the strings given here.
4. **Build no payment integration.** No Stripe, no PayPal, no card form, no PayPlus
   SDK, no checkout. Payment happens outside this app, via a link sent later. See §7.
5. **No third-party scripts.** No analytics, chat widget, cookie banner, newsletter
   popup, or font CDN. Self-host fonts.
6. **Do not fake stock, delivery dates, reviews, testimonials, or customer logos.**
   If you need an unavailable state, wire it to the API contract in §7 and leave it
   empty in the mock.

## 3. Stack and tooling

- **Next.js 15 (App Router) + TypeScript + Tailwind CSS**, deployed on Vercel.
- **21st.dev Magic MCP** — add it in Antigravity and lean on it for the interactive
  parts: quantity steppers, the cart sheet, sticky summary bars, form controls,
  toasts. **Caveat you must respect:** its output is LTR and English-first, and styled
  to a generic marketplace default. Every component it hands you gets reworked for RTL
  and re-skinned to §4 before it ships. If a component still looks like it came off a
  component marketplace, it is not done.
- **shadcn/ui** as the primitive layer underneath.
- **Framer Motion** for §9.
- Run a real browser against your own output at 390×844 and look at it after every
  meaningful change. Never call a section finished from reading the code.

## 4. Visual identity — inherited, not invented

This brand has a printed wholesale pricelist with a strong identity, and the page must
be recognisably the same brand. These values are sampled from the artwork itself, not
guessed:

```
paper   #EFE6D6   page ground — warm off-white, slightly pink
ink     #241C15   product names, primary text
green   #263B18   section titles, dark blocks — deep olive, not emerald
clay    #C6421F   the ₪ mark, and essentially nothing else. One accent, used rarely
sand    #7E715D   descriptions, secondary text
rule    #D8CCB4   hairline dividers
```

**Type:** Rubik 500/600 carries product names, prices and titles. Heebo 400 carries
body and descriptions. Both cover Hebrew fully. Self-host as woff2.

**Where you have freedom:** scale, rhythm, composition, motion, and how photography is
used. The printed sheet is a document; this is a screen. It should feel authored for a
screen, not like a PDF someone uploaded.

**Where you do not:** the six colours and the two typefaces. Do not add a gradient
system, a second accent, a glassmorphism layer, or a neon.

## 5. The catalog — complete and exact

### תמציות תה · Tea extracts

Every flavour comes in two sizes at the same two prices:
**1 ליטר ₪65 · 500 מ״ל ₪33.** The price never varies by flavour — so state it **once
per section**, not on every row. This is the single most important structural decision
on the page: eleven rows that each repeat ₪65 / ₪33 is a spreadsheet, not a design.

One litre yields **20–25 served cups**.

| Name | Hebrew description |
|---|---|
| FRESH | חליטה תאילנדית · היביסקוס ועליים |
| FRESH ללא סוכר | חליטה תאילנדית · ללא תוספת סוכר |
| DETOX | חליטה ישראלית · תה ירוק, לואיזה ונענע |
| DETOX ללא סוכר | חליטה ישראלית · ללא תוספת סוכר |
| ENERGY | חליטת שנגחאי · תה ירוק ולמון גראס |
| CALM | חליטה צרפתית · קמומיל, תפוח וציפורן |
| CONSCIOUSNESS | חליטה קוריאנית · יסמין וליצ׳י |
| REVIVE | חליטה יפנית · סנצ׳ה ופסיפלורה |
| DESERTEA | חליטה מדברית · חמישה צמחי בר |
| NAMASTEA | חליטה הודית · צ׳אי מסאלה |
| AMERICAN | חליטה אמריקאית · תה שחור, יוזו והדרים |

### מאצ׳ה ואבקות · Matcha & powders

| Product | Detail | ₪ |
|---|---|---|
| MATCHA שיזואוקה | מאצ׳ה טקסית יפנית · שקית 500 גרם | 590 |
| MATCHA שיזואוקה | מאצ׳ה טקסית יפנית · 22 שקיות 18 גרם | 590 |
| HOJICHA | מאצ׳ה שחורה קלויה · 500 גרם | 375 |
| UBE | אבקת שורש יאם סגול · 1 ק״ג | 340 |
| UBE | אבקת שורש יאם סגול · 500 גרם | 175 |
| MATCHA KIT | ערכת מאצ׳ה מלאה להכנה | 170 |

### מחיות פרי · Fruit purées

SMOOTHIE מנגו · SMOOTHIE תות · SMOOTHIE אפרסק — each `מחית פרי 50% · 1 ליטר`, **₪60**.

### מוצרים משלימים · Tools & serveware

| Product | Detail | ₪ |
|---|---|---|
| קערת מאצ׳ה קרמית | צ׳אוואן מסורתי | 118 |
| מקציף מאצ׳ה חשמלי | מקציף ידני נטען | 100 |
| מטרפת במבוק | צ׳אסן 100 שיניים | 37 |
| כוס זכוכית 600 מ״ל | כוס מדידה מחוסמת | 30 |
| מעמד למטרפה | צ׳אסן טאטה | 25 |
| כוס מדידה | ג׳יגר מודפס | 20 |
| כף מדידה במבוק | צ׳אשאקו | 11 |
| בקבוק מאצ׳ה 500 מ״ל | בקבוק זכוכית כהה | 10 |

## 6. Ordering rules — these are the product, not fine print

These come from three months of real order data (1,357 orders, 5,085 picked lines).
They are not arbitrary, and how gracefully you express them is most of the UX work.

**A. The carton.** Teas ship in a **6-bottle carton**, and mixed flavours in one carton
are fine. The rule is therefore **not** a minimum per flavour — it is that the **total
number of tea bottles in the order must be a multiple of 6**. Any mix, any sizes.

Two thirds of real orders already satisfy this, and the average order is 1.08 bottles
short of the next carton. So this must feel like a nudge, never a wall:

- A live carton meter — e.g. `ארגז 3 מתוך 3 · שלם` or `עוד 2 בקבוקים להשלמת הארגז`.
- When short, offer the completion inline, from flavours already in the cart.
- Never block scrolling, never modal, never scold. Submit stays disabled with a plain
  reason until the total is whole, and the reason is always one tap from resolved.

**This meter is the page's signature interaction. Spend your craft here.**

**B. Minimum order: ₪944 including VAT.** The only VAT-inclusive number on the page.
Show progress toward it, in the same quiet register as the carton meter.

**C. Only sell what is actually in stock.** Every measured order failure in the data
was a shortage, not a picking mistake. An unavailable flavour renders unavailable and
uncounted — never accepted and apologised for later. The availability flag comes from
the API (§7); in the mock, everything is available except one flavour, so the empty
state is real and designed.

**D. Prices are the list price for everyone.** Long-standing customers have negotiated
prices, which a human applies before the payment link goes out. State this plainly
near the total — not in a footer, not as vague "subject to approval". Use exactly:

> המחירים המוצגים הם מחירון סיטונאי, ללא מע״מ.
> ללקוחות עם מחירים מוסכמים — המחיר שלכם יופיע בלינק התשלום.

## 7. The flow and the API contract

```
catalog page → cart → checkout details → POST /api/orders
                                            ↓
                        (server) creates a draft order, returns a reference
                                            ↓
                     a human at GT reviews it and adjusts prices
                                            ↓
                        payment link sent to the customer by email
                                            ↓
                          customer pays · tax invoice issues automatically
```

Your job is everything up to and including `POST /api/orders`. Build against these
contracts and mock them in a route handler — the real implementations are wired in the
company's backend afterwards.

```ts
// GET /api/catalog  → the catalog of §5, plus live availability
type CatalogItem = {
  id: string;
  group: 'tea' | 'powder' | 'puree' | 'tool';
  name: string;              // FRESH
  note: string;              // חליטה תאילנדית · היביסקוס ועליים
  size: string;              // "1 ליטר" | "500 מ״ל" | "500 גרם" …
  priceExVat: number;        // 65
  available: boolean;
  cartonSize: number;        // 6 for tea, 1 for everything else
  image: string;
};

// POST /api/orders
type OrderSubmission = {
  lines: { id: string; qty: number }[];
  business: {
    name: string;            // שם העסק
    taxId: string;           // ח.פ — validate the Israeli check digit before submit
    contactName: string;
    phone: string;
    email: string;           // goes to bookkeeping
    address: string;
    note?: string;
  };
};
type OrderResponse = { reference: string };  // e.g. "W-1042"
```

**The confirmation screen must not say the order is confirmed** — it is not, until a
human approves it. Say:

> קיבלנו את ההזמנה. נעבור עליה ונשלח לכם לינק לתשלום.

## 8. Produce two directions, not one

The client has not chosen a mood. Build the same page twice, at `/a` and `/b`, sharing
the data layer and the cart logic, differing only in art direction:

- **A — warm and rich.** Full-bleed photography, large scale, generous motion, a
  catalog that reads like a magazine. The paper ground carries big product images and
  the type gets dramatic in the section openers.
- **B — quiet and expensive.** Restraint, air, precise typography, product centred and
  small on a large field, almost no motion. Closer to Aesop than to a webshop.

Both must be complete and shippable. Do not build one properly and sketch the other.

## 9. Motion

Motion serves the order, not the eye. Earn each one:
- Product images settle on load in a short staggered sequence, once.
- The carton meter animates when it changes — it is the page's heartbeat.
- Adding to cart moves something; the cart summary reacts visibly.
- Respect `prefers-reduced-motion` completely. No parallax, no scroll-jacking, no
  cursor followers, no marquee.

## 10. References

Study these before designing, and take structure and restraint from them rather than
copying surfaces: **Aesop** (product catalog, typographic discipline), **Ghia**
(beverage brand, colour and confidence), **Graza** (product photography and playful
scale). None of them is Hebrew — steal the rhythm, not the layout, and remember that
mirroring for RTL is a redesign, not a CSS flag.

## 11. Assets

Product photography will be supplied separately at full resolution. Build against
`/public/products/<slug>.png` and a solid `paper`-coloured placeholder of the right
aspect ratio, so swapping the real images in changes nothing structural.

Do not generate product images. Do not use stock photos of other brands' bottles.

## 12. Done means

- Renders correctly at 390×844, 768, and 1440, with no horizontal scroll at any width.
- Every price on the page matches §5 exactly. A diff against §5 finds nothing.
- The carton rule holds: an order of 7 tea bottles cannot be submitted; 6 or 12 can;
  a mixed carton of 2 FRESH + 2 CALM + 2 REVIVE can.
- The ₪944 floor blocks submission below it, with a clear reason.
- An unavailable item cannot be added.
- The ח.פ field rejects a wrong check digit and says so in Hebrew.
- Keyboard reachable end to end, visible focus, correct heading order, real `alt` text.
- Lighthouse ≥ 95 performance and accessibility on mobile.
- No third-party requests in the network tab.
- Both `/a` and `/b` are complete.

## 13. Do not

Do not add a hero video, an FAQ accordion, a "trusted by" logo row, testimonials, a
countdown, a discount code field, a blog, a newsletter capture, or a loyalty tier. Do
not add a second accent colour. Do not translate the interface to English. Do not
build an admin screen — it already exists elsewhere.

If you think one of the rules above is wrong, say so in your summary and build it as
written anyway.
