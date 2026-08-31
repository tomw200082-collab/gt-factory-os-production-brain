# Category landing pages — design + lead-capture spec

**STATUS: SUPERSEDED IN PART — all four pages are built and deployed to theme
`162206646513`. D1 was reversed by Tom the same day; see §0.1. Read §0.1 before
treating anything below as current.**

> Four Hebrew landing pages, one per product family, whose only job is to turn ad
> traffic into a lead in `sales_core`. Written 2026-08-31 after reading the live
> theme, its CSS, its JS and the `/ingest` contract. Every claim below was checked
> against a source; none is inferred from the rendered page alone.

---

## 0. Decisions already taken (Tom, 2026-08-31)

| # | Decision | Consequence |
|---|---|---|
| D1 | ~~**No cost, price or margin figure appears on these pages.**~~ **REVERSED — see §0.1.** | Superseded 2026-08-31. |
| D2 | **Leads land in the sales system attached to the ops system** — `sales_core` in `gt-factory-os`. | Not Shopify customers, not a mailbox. See §5. |

Everything else in §7 is still open.

---

## 0.1 What changed after this spec was written (2026-08-31)

**D1 was reversed by Tom, in writing, the same day**: *"שים עלויות של משקאות לפי
הקטלוג הזה"* — put drink costs on the pages, sourced from his Canva catalog
`DAHTYkRvEnM`. The pages now lead with the economics rather than hiding them: every
drink card carries cost per serving, recommended price and the percentage the venue
keeps. §3 and §4 are written against the reversed decision and are stale wherever
they argue for withholding figures. D2 stands unchanged.

That catalog was verified against the frozen authority `drinks_final_figures.json`
(2026-08-27) before a single figure was transcribed: **48/48 names matched, 0 figure
deviations, 0 authority names absent, and an independent VAT re-derivation gave 0/48
mismatches.** Tom's source and the frozen authority are the same numbers.

Also settled since:

- **All four pages are built**, not one then three clones. §6's "chai first" sequence
  did not survive contact — the generator made per-page hand-building pointless.
- **The matcha page covers hojicha**, at Tom's instruction, as a small secondary block
  rather than a page of its own.
- **`gt-site.css` reuse was wrong.** §1.2 claimed four pages needed zero new CSS. They
  needed their own stylesheet, and — more importantly — their own class namespace:
  `gt-site.css` carries unscoped `.glass`, `.hero`, `.btn`, `.wrap`, `.eyebrow`,
  `.logo`, `.serif` rules that reach into any markup reusing those names and set every
  property the new stylesheet does not declare. `.glass` (`position:absolute;
  opacity:0`) hid the pages' signature element on all four pages while the rest of the
  layout looked correct.
- **Preview needs no publishing.** Alternate index templates plus Shopify's
  `?view={suffix}` render all four pages inside the theme preview with no page record
  involved, so `/pages/{slug}` stays 404 on the live storefront. The page records stay
  unpublished until Tom says otherwise.

Runtime lives in `gt-site`, `tools/landing-pages/` (PR #3). This file stays a plan
record; it is not the authority on what shipped.

---

## 1. What already exists — verified, not assumed

Theme `GT Site v5 — Hebrew (do not publish)`, id `162206646513`, role `UNPUBLISHED`,
built on `BT Vodoma Food 3.1.2`. **`updated_at` 2026-08-31 11:29 UTC** — it was being
edited the same hour this was written. Confirm ownership before any write.

```
layout/gt.liquid          1,644 B   no nav, no footer, no theme chrome
templates/index.json        137 B   already declares "layout": "gt"
sections/gt-home.liquid  57,358 B   the whole homepage is one section
assets/gt-site.css       59,280 B   733 rules, hand-written, RTL, responsive
assets/gt-site.js        57,530 B
assets/gt-*.webp          ~150      local images, already optimised
```

`layout/gt.liquid` in full is a doctype, three Google fonts, `gt-site.css` and
`{{ content_for_layout }}`. **The "strip the navigation and keep one clean page" step
is already done and shipped.** There is nothing to duplicate and nothing to delete.

A landing page is therefore: one `templates/page.<name>.json` carrying
`"layout": "gt"`, plus one `sections/gt-lp-<name>.liquid`. No theme fork.

### 1.1 Design tokens — `:root` of `gt-site.css`

```
base     --ink #20241F   --ink-soft #4B5148  --paper #FBF8F2  --card #F3EFE6
         --gt  #3E6E34   --gt-d #2B4F24      --terra #C4744B  --line #E7E1D3
family   --matcha #5FA34C   --ube #7B5CC6   --nama #D96B3F
         --fresh #E63950    --detox #4E8C4A --energy #F0A63A --revive #E2634B
         --consc #C4327E    --desert #C9922F --calm #8B7FBF
```

Type: `Assistant` 300–800 (body) · `Bellefair` (display serif) · `Playfair Display`
italic (numerals, `.num`). Document is `lang="he" dir="rtl"`.

### 1.2 Components available for reuse — no new CSS required

`.hero` `.hs-*` (hero slider) · `.eyebrow` · `.sec-head` · `.wrap` · `.cm-*` (drink card:
photo, numbered steps, ingredients) · `.mgrid` `.mcard` · `.mx*` · `.stats` `.stat` ·
`.steps4` `.step` · `.qgrid` `.qcard` · `.fgrid` `.fcard` (FAQ) · `.tools-grid` ·
`.partner` `.pf-*` (form) · `.bigcta` `.btn` `.cta` · `.ticker` · `.imgband` · `.duo` ·
`.rv` (reveal, honours `prefers-reduced-motion`).

**Rule: if a fourth page needs a component the first three did not, the first was built
wrong.** Zero new CSS files. One accent token swap per page.

---

## 2. The four pages

| Page | Handle | Accent | Entry barrier for the buyer |
|---|---|---|---|
| `צ'אי` | `/pages/chai` | `--nama #D96B3F` | none — works with what a bar already owns |
| `מאצ'ה` + `מאצ'ה שחורה` | `/pages/matcha` | `--matcha #5FA34C` + a second accent for hojicha | whisk or frother, and milk |
| `אובה` | `/pages/ube` | `--ube #7B5CC6` | never stands alone — needs a second GT product |
| `תה קר` | `/pages/iced-tea` | proposed `--fresh #E63950` | none |

Two accents are unresolved and are Tom's: the `תה קר` accent (seven family tokens
already exist; `--fresh` is proposed for maximum separation from the other three) and a
`מאצ'ה שחורה` token, which does not exist yet — a roasted brown is proposed, value TBD.

**Sequence by ease of yes, not catalog order: `צ'אי` first, then `מאצ'ה`, then `תה קר`,
then `אובה`.**

---

## 3. Page anatomy — what persuades once the numbers are gone

D1 removes the homepage's strongest argument. That is not a loss if the number becomes
the *reason to convert* rather than the content of the page:

> **The price list is the reward for leaving details.**

Every CTA on these pages therefore promises the full price list, a tasting, or a menu
built for the venue — and none of them shows a figure.

What carries the page instead, all of it already available:

1. **Hero** — one photograph, family name, one sentence of what it lets the venue serve.
   Accent token colours the eyebrow, the rule and the CTA.
2. **The drinks** — `.mgrid` of the family's drinks, each opening a `.cm-*` card with the
   photograph, the numbered preparation and the ingredients. **The four-stat block at the
   bottom of that component is removed on these pages** (D1).
3. **"What you need to already own"** — the operational line. `תה` and `צ'אי` need nothing;
   `מאצ'ה` and `אובה` need a whisk or frother and milk. This is the sentence that decides
   whether a café owner believes they can start on Sunday.
4. **Four steps to serve** — `.steps4`, unchanged.
5. **Range** — how many drinks the one bottle or bag opens. A count, not a price.
6. **Proof** — `.qgrid`. Requires real, permissioned quotes; none may be written.
7. **Capture** — §5.

No section repeats a claim from another. No page contradicts another.

---

## 4. What must not appear

- ~~Any cost, price, margin or profit figure (D1).~~ **Reversed — §0.1.** The figures
  are now the pages' argument, and every one traces to the frozen 48-drink authority.
- Any drink whose preparation is not documented.
- Any product on the `catalog-truth.md` negative-record list.
- Any partner, venue or customer name without recorded permission.
- Any health, kosher, organic or certification claim.
- Any cup-yield or shelf-life number that is not traceable to an approved source —
  including the ones already live on the homepage, which need confirming, not copying.

---

## 5. Lead capture — the part that does not work today

### 5.1 The current form captures nothing

`pSend()` in `gt-site.js` ends with:

```js
window.location.href = 'mailto:info@gteveryday.com?subject=' + ... ;
f.classList.add('sent');
```

It opens the visitor's mail client and marks the form "sent". There is **no server call,
no `sales_core` row, no Shopify customer, no analytics event**. On mobile most visitors
never complete a `mailto:` handoff, and nothing records that they tried. The only capture
path on the site that currently works is the WhatsApp link.

### 5.2 The `/ingest` contract — and why the browser cannot call it

Route `ingest` on Edge Function `sales-leads-poll`, second factor
`X-Lead-Ingest-Token` matched against `LEAD_INGEST_TOKEN`. There is no rate limiting and
no captcha on it. **A shared secret cannot live in a public page's JavaScript**, so a
browser form must not call `/ingest` directly.

`_lib/ingest_body.ts` already anticipates this caller — its header names "a future website
form" — and accepts a flat shape:

```json
{
  "source":       "site-chai",
  "contact_name": "...",
  "display_name": "<business name>",
  "phone":        "...",
  "email":        "...",
  "city":         "...",
  "form_name":    "landing-chai",
  "platform":     "site",
  "campaign_name": "<from utm_campaign>",
  "ad_name":       "<from utm_content>"
}
```

A lead needs at least a phone or an email. `external_id` is optional — omitted, a stable
one is derived from phone/email plus `created_at`, so a retried POST is idempotent rather
than a duplicate lead.

**Correction to earlier framing:** the per-category discriminator is the `source` field
(`sales_core.lead.source`, unique with `external_id`), not a `source_id`. The taxonomy
below is a proposal, and must be agreed with whoever owns the intake taxonomy before use:
`site-chai` · `site-matcha` · `site-iced-tea` · `site-ube`.

### 5.3 Recommended path: Make as the server hop

The landing page posts to a Make webhook; Make attaches `LEAD_INGEST_TOKEN` and calls
`/ingest`. No new code in `gt-factory-os`, no secret in the browser, and it reuses the
transport already decided for Facebook leads (D-006) — including the hourly pulse that
already watches for a dead intake. Rate limiting and spam filtering sit in the Make
scenario, not in the Edge Function.

Rejected alternatives: a Shopify App Proxy (requires a private app for one form); a new
public token-less endpoint (new attack surface on the lead table).

### 5.4 Three capture paths per page, in this priority

1. **WhatsApp** — `wa.me/972543982444`, deep-linked with a per-page prefilled message so
   the category is known from the first word. Works today. Sticky on mobile.
2. **Form** — the `.partner` component, posting per §5.3. Fewer fields than the homepage's
   ten: business name, contact name, phone, city, and the consent checkbox. Email optional.
3. **Phone** — `tel:` link, visible without scrolling.

A page is not done until a test submission on it produces a row in `sales_core.lead`
carrying that page's `source`. A `200 OK` proves acceptance, not arrival.

---

## 6. Definition of done

| # | Condition | The observation that would prove it false |
|---|---|---|
| L1 | Four pages exist, each on `layout: gt`, each with one accent token | Any page pulling in the site nav or footer |
| L2 | No cost, price, margin or profit figure on any of the four | One figure found in a plain read of the rendered pages |
| L3 | Every drink shown has a documented preparation, and every ingredient resolves to `catalog-truth.md` | One unresolvable ingredient |
| L4 | Zero new CSS files; no new component that only one page uses | A rule added for a single page |
| L5 | Each page carries all three capture paths of §5.4 | Any page missing one |
| L6 | A test submission on each page writes a `sales_core.lead` row with that page's `source` | Fewer than four distinct `source` values arriving |
| L7 | Hebrew, RTL, and the pages pass a mobile read at 360 px | Any LTR block or horizontal scroll |
| L8 | No page is published to a customer-facing domain without Tom's word | A live URL |

---

## 7. Open — Tom's, and blocking where marked

| # | Question | Blocking |
|---|---|---|
| U-L1 | `מאצ'ה שחורה` is `HOJICHA`. Shopify carries it ACTIVE (0.5 kg, 20 units; 1 kg, 0 units; 30 g DRAFT) but `catalog-truth.md` records "אין SKU פעיל" — which is right? | yes, for that page |
| U-L2 | **No preparation exists for hojicha anywhere.** A page whose argument is "here is what you serve tomorrow" has nothing to show. Commission recipes, or the matcha page covers regular matcha only | yes, for that page |
| U-L3 | Accent colour for `תה קר` — `--fresh #E63950` proposed | yes |
| U-L4 | Accent colour for `מאצ'ה שחורה` — no token exists; a roasted brown is proposed | yes |
| U-L5 | Who is editing theme `162206646513`? It changed 2026-08-31 11:29 UTC | yes, before any write |
| U-L6 | `source` taxonomy — agree `site-<category>` with the intake owner | yes, before L6 |
| U-L7 | Which drinks appear on each page, and does the homepage's drink set or the 48-drink authority define the families? Independent of D1, since the *names and preparations* still have to come from one place | yes |
| U-L8 | Are the yield and shelf-life lines already live on the homepage confirmed, or inherited copy? | no, but they cannot be reused until answered |

---

## 8. Halt conditions

Inherited from `CLAUDE.md` §Stop conditions. Additions:

- A figure would appear on a page → **STOP** (D1).
- A drink would be shown with no documented preparation → **STOP**.
- A form would be wired with `LEAD_INGEST_TOKEN` reachable from the browser → **STOP**.
- A page would be published to a live domain → **STOP**, Tom's.
- A write to theme `162206646513` while its current editor is unknown → **STOP** (U-L5).

---

**Next action:** Tom answers U-L1 through U-L4. Then one page — `צ'אי` — is built end to
end and proven against L1–L7 before the other three are cloned from it.
