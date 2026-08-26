# Movement 2 — the committed direction

Answered before any markup, per `frontend-design-master` Phase 1. Written down so the
next rebuild inherits the direction instead of re-deciding it.

## 1. Purpose — who reads this and what they feel

A café, bakery or hotel owner who left their name and phone number about two minutes
ago. They open a PDF on WhatsApp, one-handed, probably standing up, probably between
two other things.

What they should feel is **respected, not seduced.** The deck's argument is that GT
already knows its own numbers and is willing to show the café owner the cost as well
as the profit. The emotion is confidence. Appetite is the photography's job and it is
secondary.

This is why the deck shows FOOD COST at all. A deck that shows only profit is a deck
that is hiding something, and a buyer who has seen one supplier deck has seen that
trick. The honesty **is** the sales asset.

## 2. The aesthetic direction — Editorial, at phone scale

**Committed direction: Editorial / Magazine**, executed at 1080×1920 rather than on a
spread.

- Oversized Hebrew type that is allowed to be the loudest thing on a screen.
- A hairline rule doing all the structural work. No boxes, no cards, no panels.
- Full-bleed photography with type set **on** it, never beside it in a column.
- Violent size contrast: a product name at 130px sits two lines above a caption at 36px.
- Latin figures and the `₪` treated as display objects, not as table cells.

This is not a new direction imposed on GT. It is GT's own registered grammar —
`docs/warehouses/marketing-assets.md`, row `DNA עיצובי`: full-bleed photo at the head
of a page with white type over it, `Rubik` for anything emphatic and `Heebo` light for
the quiet passages, product names as spaced capitals, a hairline instead of boxes, a
small `₪` in coral, RTL body with price columns forced to `direction: ltr`. The
decision here was to take that grammar to 9:16 and let it get louder, because a phone
held at arm's length forgives nothing subtle.

## 3. The one unforgettable thing — S03, the mapping

Four coloured spines, twelve drinks hanging beneath them, and **exactly one hairline
that crosses.**

Eleven of the twelve drinks belong to a single GT product. `אייס מאצ׳ה מסאלה` belongs
to two. Drawn as a link diagram that fact would be invisible — eleven parallel lines
and one crossing reads as noise. Drawn as spines, the single crossing is the only
crossing on the page, so it reads as intent, and it says the thing the deck is selling:
these four bottles compound.

It gets more design effort than any other screen, and it is placed third — before any
price — so the buyer understands the shape of the offer before they are asked to judge
a number.

## 4. What this must NOT look like — explicit rejections

- **Not a spreadsheet.** No table borders, no zebra striping, no header row.
- **Not a Canva template.** No preset gradient, no stock component defaults.
- **Not a generic SaaS pricing page.** No three cards in a row, no "most popular"
  badge, no checkmark lists, no rounded-corner boxes with shadows.
- **Not a restaurant menu.** No dot leaders running from a name to a price.
- **Not an A4 brochure squeezed into a phone.** Nothing is a shrunken desktop layout.

Concretely banned from the build: card grids · rounded-corner containers around drinks ·
drop shadows · gradient headers · any icon set · emoji · stock photography of any kind.

## Constraint that overrides the skill

`frontend-design-master` Phase 3 says to load fonts from the Google Fonts CDN. **Not
here.** A `<link>` to `fonts.googleapis.com` fails behind this environment's egress
proxy, Chromium silently falls back, and the Hebrew renders in something that is not
`Rubik` — often with no error at all. Fonts are loaded with `@font-face` and `file://`
URLs from the repo's own WOFFs. D7 exists to catch a regression here.
