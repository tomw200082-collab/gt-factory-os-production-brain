# MB-D01 — Where the Menu Builder sits in the lead journey

> Owner-minded recommendation, Session 1, 2026-10-01. Status: **OPEN — put to Tom.** Evidence: `ground-truth.md` §1–§3, §6; `dependency-ledger.md` DL-03, DL-08, DL-09, DL-15.

## What I found

1. **The journey already has a "menu" and already has a "personal link".** Every lead gets a PDF menu of ≤8 drinks with three buttons (D-026/D-028). Tapping `אני רוצה להזמין` mints a personal link (`/portal/lead/<token>`, 14 days, reusable until the first order) that opens the ordering portal in lead mode: 40 raw SKUs, list prices, ₪800 minimum, pairs. The same link rides wake-up messages 1, 3 and 4 after a sales call. This is all merged and running (gated for real sends).
2. **The gap sits exactly between those two assets.** The PDF says "here are drinks you could serve"; the order link says "here are bottles, choose quantities". Nothing translates one into the other. The site's own FAQ promises the translation (`איך מתחילים? … אנחנו בונים לכם תפריט פתיחה למקום, כולל מתכונים, תמחור והדרכת צוות`), and the fifth site line is literally `בניית תפריט משקאות עשיר ורווחי לעסק` — today it is answered with a fixed PDF.
3. **The approved WhatsApp texts are a hard constraint.** Only the first message has buttons; every later message carries at most one link button; Tom approved the texts byte for byte on 2026-09-28 and the code pins them. A placement that needs a fourth button, a second button round or a new text reopens D-028/D-033/U-051 and the Meta template review.
4. **Identity exists only behind the link.** On the site there is no identity and no prices (Tom 2026-09-24). In WhatsApp the lead is a phone. Behind the personal link the lead is a `lead_id` + phone with list prices, planner availability, pairs, the ₪800 rule and the draft-only handoff already enforced. For an existing customer the same mechanism gives their own prices.
5. **The salesperson sees nothing of what the lead explored today.** Unit A will route specific lead events to owned tasks (`button_tap lj.more`, `draft_order`, repeat contact). A Builder event appended to the lead rides that same path.
6. **Volumes are small and the first-order step is the bottleneck:** ~1–2 leads/day, 5 `won` in two months, 71 `lost`. Every lead who orders is worth months of reorders (87–98% monthly returning rate). Tom's stated goal is Lead → First Order with fewer human touches.

## My recommendation

**Place the Builder behind the existing personal ordering link, as the first screen a lead sees after tapping `אני רוצה להזמין`, with a visible fast path to the plain product list. For existing customers it is an optional entry inside the ordering portal, never the default.**

Concretely:

- Tapping `אני רוצה להזמין` (and the order link in wake-up messages 1, 3, 4) opens `/portal/lead/<token>` as today, but the page opens on **"build your menu"** (pick drinks → see the starter purchase GT worked out → send it as the order) instead of the bare catalog. One tap, always visible, skips to the catalog: `אני כבר יודע מה להזמין` (copy for Tom's approval).
- The output of the Builder is a **pre-filled cart in the same ordering page**, priced by the same pricing function, checked by the same rules (availability, pairs, ₪800), submitted through the same draft-only lead path. No second order writer, no second price truth.
- An existing customer who comes through the Builder link gets `/portal/` as today; the Builder appears there as a tile (`בניית תפריט`), optional. Returning leads reopen the same link and find their menu where they left it (the link is reusable until the first order).
- No WhatsApp text, button or template changes in V1. The salesperson's handoff is the lead itself: the built menu and recommended cart appear on the lead in the CRM as events, and "asked for help from inside the Builder" becomes an owned task.
- The PDF stays. It is the inspiration asset inside WhatsApp (instant, no hop); the Builder is the action asset behind the link. Later, the PDF's last-page button can point at the Builder instead of a `wa.me` text (V1.1, one Canva edit, Tom's call).

## Why this is best for GT

- **Highest intent, lowest friction, zero re-approval.** It meets the lead at the one moment they have said "I want to order", replaces the hardest step (menu → bottles) and needs none of Tom's approved messages changed. The Sales dependency is the smallest possible: a link and a page that already exist in production.
- **One truth everywhere.** Identity, prices, availability, pairs, minimum, draft handoff, alerts and the lead event log are reused, not copied. The Builder cannot show a price the order page would reject.
- **Sales sees the intent before the call.** The salesperson opens the lead and sees the menu the lead built and the cart they were shown. Calls get shorter and better; self-serve leads order without a call.
- **Resume comes for free.** The personal link is the resume key for 14 days; the Builder state hangs off the lead.
- **No forced path.** The fast path keeps high-intent and repeat buyers out of the Builder; existing customers never see it by default (masterprompt §9: "do not force the Builder into every journey").
- **Measurable.** Builder events sit next to `button_tap`, `draft_order` and `converted` on the same lead, so Lead → First Order, time to order and recommendation acceptance are one query.

## Strongest alternative

**A — the Builder replaces the PDF as the first-message asset** (the lead's first touch after `היי, אני מעוניין ב…` is a Builder link, not a PDF).

- For: maximum exposure, every lead sees it, and it answers the fifth line literally.
- Against: WhatsApp interactive messages cannot carry a URL button next to the three reply buttons, so the link would have to go in the body or replace the buttons, reopening D-028/D-033 and the just-approved texts and templates; the PDF opens instantly inside WhatsApp while a web link is a hop, and a curious lead at first touch wants inspiration before commitment; the site has no identity, so a Builder reached before the form cannot price anything.
- Verdict: keep as a V2 experiment once the Builder has data behind the link; do not make it the launch placement.

Also considered and set aside for V1: on the website (no identity, no prices allowed, second data copy — recorded as a possible anonymous "inspiration mode" later); only after the sales call (loses the self-serve leads Tom wants to convert without a touch; the same link already reaches post-call leads through the wake-up messages); inside the customer portal for expansion (Unit C territory, after first orders exist).

## What changes if Tom agrees

- MB-D01 becomes FINAL — PROVISIONAL on DL-03 (link reuse semantics) and DL-08 (texts unchanged).
- The next question becomes the quantity model (MB-D03): what one thing we ask the lead so the starter cart is right.

## Decision requested

Approve the placement above, or name the moment in the journey where you see the Builder instead.
