# MASTERPROMPT — GT's site: Hebrew, owned, and able to survive a Tuesday

**STATUS: LIVE — not yet executed**

> **Usage (Tom):** paste this whole file as the first message of a fresh Claude Code
> session with `gt-site`, `gt-factory-os-production-brain` and `Sales-Machine` attached,
> and the Shopify, Dropbox and Vercel connectors on. It takes the R124 design from "an
> English HTML file whose images live on somebody else's server" to "a Hebrew site GT
> owns, hosted, fast, and wired to the lead pipeline." It halts for you only where §6
> says.
>
> **Provenance:** written 2026-08-31. `GT_Site_v5_R124.html` was extracted from the
> artifact `מפת הדרכים הדיגיטלית`
> (`https://claude.ai/code/artifact/09e806f6-978b-46d3-8374-eb36379710fa`, task `w1`) and
> measured directly: 204,386 bytes, `lang="en"`, 215 proxied `<img>` references over 144
> unique sources, 7 of which were fetched with `HEAD` — 145,949,148 bytes total, **19.9 MB
> average per image**. The `gt-site` repo was cloned and inspected: one `README.md`, HEAD
> `dc3346c`. Nothing has been built.
>
> **Shelf life:** §2 is presumed stale after 2026-09-28. Re-run §2.5. A parallel session
> may already be working on this — **check `gt-site` branches at boot before writing a
> line** (Tom said on 2026-08-31 that a parallel session is in progress).

---

## 0. How to work

- **Who you are here:** one Claude Code session. You hold `gt-site` with push access,
  Shopify Admin (read), Dropbox, Vercel and Canva. You own everything technical about the
  site. You own **no** claim it makes, **no** price it prints, and **no** DNS record.
- **Read first, in order:** `gt-factory-os-production-brain/CLAUDE.md` ·
  `Sales-Machine/CLAUDE.md` · the artifact above, sections `web` and `shop`, including
  every `note` · `docs/warehouses/marketing-assets.md` (brand DNA, palette, fonts, and
  which product photos exist) · `docs/warehouses/catalog-truth.md` (what GT actually
  sells) · `docs/pricing/2026-08-05_shopify_products_exvat.tsv` (the only price authority).
- **Authority:** the repos' `CLAUDE.md` files win. Halt conditions, evidence standard and
  git discipline are inherited from `gt-factory-os-production-brain/CLAUDE.md` — §8 lists
  only the additions.
- **The standard.** Tom's ask was Hebrew plus "whatever helps decode the image problem,
  technically." Three prohibitions:
  1. **No asset the site needs may live on a server GT does not control.** Not a CDN GT
     does not pay for, not a free proxy, not an artifact URL.
  2. **No page may print a number that is not in an approved source file.**
  3. **No form may lose a lead.** Every submission lands somewhere a human is known to
     look, and the session proves it with a test submission it can see arrive.
- **Be lazy on purpose.** This is a single-page marketing site for a wholesale beverage
  factory. It needs no framework, no CMS, no database, no build pipeline beyond an image
  script. Static HTML/CSS on a CDN. Every layer you add is a layer someone maintains
  instead of selling. If you find yourself scaffolding a component library, stop.
- **Language:** this document is English; data literals stay in their own script in
  backticks. **The site becomes Hebrew.** **Output language: concise Hebrew for Tom,
  concise English otherwise.**

---

## 1. Mission and definition of done

**One testable sentence:** `gteveryday.com` serves a Hebrew, right-to-left, self-hosted
version of R124 that loads fast on a phone, prints only verified numbers, and delivers
every enquiry into `sales_core`.

| # | Condition | The observation that would prove it false |
|---|---|---|
| D1 | Zero external image dependencies | `grep -c "wsrv.nl\|cloudfront.net" dist/**/*.html` returns 0 |
| D2 | Every image is served from the repo, in a modern format, sized for its slot | Any served image over 300 KB, or any `<img>` without `width`/`height` |
| D3 | The page is Hebrew and RTL throughout | `<html lang="he" dir="rtl">`; any untranslated English string outside a brand name or a product's own English name |
| D4 | Mobile Lighthouse performance ≥ 85 and LCP < 2.5 s on a throttled 4G profile | Run it; a lower score is the failure |
| D5 | Every price and product claim on the page reconciles to an approved source | Join every printed figure to the TSV and `catalog-truth.md`; one mismatch = fail |
| D6 | The enquiry form writes a lead into `sales_core` and a human is alerted | Submit a test enquiry; `select * from sales_core.lead order by created_at desc limit 1` does not show it = fail |
| D7 | Old URLs resolve — no live link returns 404 | Crawl the current sitemap against the new site; any 404 from a page that exists today = fail |
| D8 | The site is deployed on infrastructure GT controls, from a git repo, and a redeploy is one command | The deployment cannot be reproduced from `gt-site` alone |

Anything not on this list is out of scope unless Tom asks.

### 1.1 Settled — do not reopen

- **R124 is the design.** Tom handed it over on `2026-08-26` and the artifact records it as
  the truth version. Do not redesign it. You are porting, translating and fixing it.
- **Shopify stays the order system.** The artifact is explicit: the storefront is not being
  replaced. This is the marketing site.
- **`greentea-everyday.com` is a second domain on the same Shopify store**, already
  redirecting (verified `2026-08-26`, artifact `id2`). It is not a duplicate site. Do not
  "fix" it.
- **Google Business Profile is verified.** Leave it.

---

## 2. Ground truth — measured 2026-08-31; re-verify at boot

### 2.1 What exists

- `GT_Site_v5_R124.html` — 204,386 bytes, one file. Sections: `products`, `drinks`,
  `matcha`, `purees`, `tools`, `pricing`, `about`, `faq`, `contact`. Fonts loaded:
  `Bellefair`, `Playfair Display`, `Assistant`. One WhatsApp link:
  `https://wa.me/972543982444`. It is embedded as a base64 `data:` URI inside the artifact
  state under task `w1` — extract it from there, that is the canonical copy.
- `gt-site` — empty repo, `README.md` only, HEAD `dc3346c`, default branch `main`.
- The live Shopify site — 33 pages scanned `2026-08-26`; two were corrected then.

### 2.2 The image situation, measured

| Measure | Value |
|---|---|
| `<img>` references routed through `wsrv.nl` | **215** |
| Unique source images behind them | **144** |
| Average size, 7 sampled with `HEAD` | **19.9 MB** |
| Implied raw payload for all 144 | **≈2.9 GB** |
| One sampled image, fetched direct (`curl`, 2026-08-31) | 29,739,083 bytes |
| The same image via `wsrv.nl` (`curl`, 2026-08-31) | 1,089,481 bytes |
| Host of every source | `d8j0ntlcm91z4.cloudfront.net/user_3DnHlJj9…` — Claude's user-upload CDN |

The page renders only because a **free third-party proxy** (`wsrv.nl`) downscales roughly
three gigabytes of source imagery on every load. GT pays that proxy nothing, has no
agreement with it, and does not own the origin.

### 2.3 What is NOT built

No hosting. No domain pointing anywhere new. No Hebrew version. No local assets. No form
backend. No analytics. No redirect map. No sitemap. No structured data.

### 2.4 Known-broken, adjacent

- **Enquiries currently go to HubSpot** — a CRM in nobody's plan, which nobody has
  confirmed anyone reads (artifact `id4`, found `2026-08-26`). Both a lead-loss risk and a
  data-protection question.
- **The partner form loses leads** — artifact task `w3` says so outright.
- **Three claims contradict each other across live pages**: cups per bottle reads `33` on
  `גרינטי לעסקים`, `30` on `רכיבים`, and `13` in R124 itself. The approved figure is
  **20 cups from a 1 L bottle at a 50 ml pour** (`Sales-Machine` book §02 and the cost
  model). Customer count also varies by page.
- **Five blog posts** (most recent `01/2022`) carry spelling errors and regulatory health
  claims including `מפחית סיכון לסרטן`. That is a regulatory exposure, not a typo.
- **Three `301` redirects were created `2026-08-26`** to fix dead blog links pointing at
  archived products. Preserve them.
- **The password page** may still be indexed (artifact `s5`, half-closed).

### 2.5 Re-verification block

```bash
git -C /home/user/gt-site fetch --all && git -C /home/user/gt-site branch -a   # parallel session?
grep -o 'https://wsrv\.nl/?url=[^"]*' GT_Site_v5_R124.html | wc -l            # expect 215
curl -sI "<one decoded cloudfront url>" | grep -i content-length              # still ~20 MB?
```
If the CloudFront URLs now return `403`/`404`, the site has already lost its images and
this becomes urgent rather than important.

---

## 3. What the hard part actually is

**It looks like:** translate a page into Hebrew and put it online.

**It actually is:** the site does not own its own content. 2.9 GB of imagery sits on
Claude's user-upload CDN and reaches visitors only through a free proxy that owes GT
nothing. Those URLs are not a hosting arrangement — they are the residue of how the design
was made. Publish as-is and GT ships a site that can go blank on a Tuesday, with nobody
holding a copy of what it looked like. **The image migration is the project.** The Hebrew
conversion is a day's careful work; the assets are the week.

**Second reframe:** ~20 MB per image is not an optimisation opportunity, it is a defect.
These are full-resolution generation outputs displayed at a few hundred pixels. Correctly
encoded, the entire site should serve **under 3 MB total** — a thousandfold reduction, and
the difference between a site that works on 4G in a café and one that does not. This is
the single highest-leverage technical act in the whole document.

**Third reframe:** Hebrew is not translation. It is `dir="rtl"`, mirrored layout, a font
stack that actually has Hebrew glyphs (`Bellefair` and `Playfair Display` do not — only
`Assistant` does, so every heading currently styled in a Latin display face will fall back
and look broken), numerals and currency that stay LTR inside RTL text, and a
`hreflang`/`lang` story. `marketing-assets.md` already records the approved solution GT
used for its price list: `Rubik` and `Heebo` with full Hebrew WOFF files, RTL with price
columns forced to `direction:ltr`. Reuse it. It is proven and it is already in the repo.

**Fourth reframe:** the form is a lead system component, not a website feature. It
currently posts to a CRM nobody watches while `sales_core` — with a live queue, alerting,
assignment and conversion tracking — sits unused by the site. Wiring the form to
`/ingest` is worth more than any copy change on the page.

---

## 4. Workstreams

### W1 — Stand up the repo (first hour)

`gt-site` is empty. Set up the smallest thing that works: `src/` static HTML, `assets/`
images, `scripts/` the image pipeline, `dist/` built output. Vercel for hosting; it is
already a connector GT holds and it deploys from git with no configuration to maintain.

**No framework.** One page, no dynamic content, no auth, no database. Next.js here buys a
build step, a dependency tree and a maintenance surface for zero capability.

Commit R124 unmodified as `src/reference/GT_Site_v5_R124.html` first, before touching
anything, so every later diff is readable against the original.

**Acceptance:** D8.

### W2 — The image migration (the big one)

1. Extract all 144 unique source URLs from R124.
2. Download every one. Expect ~3 GB; **watch disk** — this session has a fixed writable
   allowance, so process in batches and delete originals as you go.
3. For each, determine its real rendered size from the CSS, then encode: `AVIF` primary,
   `WebP` fallback, at `1x` and `2x`. Target **≤200 KB hero, ≤80 KB product shot**.
4. Write them into `assets/img/` with meaningful names — `fresh-1l.avif`, not
   `hf_20260720_172831_855d699e.png`. Names are documentation.
5. Rewrite every reference to a local `<picture>` with `srcset`, explicit `width`/`height`
   (this alone removes the layout shift that will otherwise cap D4), `loading="lazy"`
   below the fold, and real Hebrew `alt` text.
6. Record the mapping in `assets/img/SOURCES.md`: original URL → local file → where used.
   When someone asks in six months where a photo came from, that file answers.

**Cross-check against `docs/warehouses/marketing-assets.md`** — many of these images are
already catalogued there with a Tom-approved grade and a Dropbox path. Where the warehouse
has a better original, use it and note the swap. Where the warehouse records a **gap** (no
photo of the matcha kit exists anywhere; the 22-sachet matcha exists only as a 229 px
thumbnail), do not stretch a small file — leave the slot out and list it in §6.

**Acceptance:** D1, D2, and most of D4.

### W3 — Hebrew and RTL

`<html lang="he" dir="rtl">`. Font stack from `marketing-assets.md`: `Rubik` 400/500/600/700
and `Heebo` 300/500, self-hosted WOFF from `docs/pricing/pricelist_pdf/fonts/` — **do not
load them from Google Fonts**; they are already in the repo and self-hosting removes a
third-party dependency and a round trip.

Translate every string. Product names keep their English form (`FRESH`, `DETOX`,
`NAMASTEA` — that is how they appear on the bottle and in the catalog). Prices, SKUs and
phone numbers get `direction:ltr` inside their RTL containers, or they render backwards.

Mirror the layout, not just the text: padding, margins, icon direction, carousel
direction, form field alignment.

**Acceptance:** D3.

### W4 — Verify every number on the page

Join every printed figure to `docs/pricing/2026-08-05_shopify_products_exvat.tsv`,
`docs/warehouses/catalog-truth.md` and `docs/pricing/2026-08-05_drinks_final_figures.json`.
Emit a diff table. Zero rows is the gate.

Two known landmines here: the cups-per-bottle contradiction (§2.4 — the approved figure is
**20 from 1 L at 50 ml**), and the products `catalog-truth.md` marks as negative records
which must not appear in a customer-facing list at all — the same four the knowledge-book
session is handling (`docs/plans/2026-08-31-knowledge-book-masterprompt.md` §2.3).
**Coordinate; do not resolve them independently and end up with two different answers on
two GT surfaces.**

**Acceptance:** D5.

### W5 — The form

Post to `sales_core` `/ingest` with a `source_id` identifying the site. Agree the contract
with `docs/plans/2026-08-31-lead-response-system-masterprompt.md` §W1 — that session owns
the intake taxonomy and there must be exactly one.

Then prove it end to end: submit a real test enquiry and show the row in `sales_core.lead`
and the alert arriving. `200 OK` proves the request was accepted, nothing more —
`gt-factory-os-production-brain/CLAUDE.md` §Evidence is explicit that a `200` observes
layer 1 of 6.

Record what HubSpot currently receives and hand the decision to Tom (§6.D). Do not
silently cut it — there may be months of leads in there.

**Acceptance:** D6.

### W6 — Launch hygiene

Redirect map from every existing URL (preserve the three `301`s from `2026-08-26`) ·
`sitemap.xml` · `robots.txt` that excludes `/password` · Open Graph and Twitter cards ·
`Organization` and `Product` JSON-LD (`schema-markup` skill) · GA4 or Plausible ·
Search Console verification (artifact `g1`, still open) · 404 page · favicon set.

Then the checklist: mobile at 360 px, tablet, desktop; Lighthouse on all four categories;
every link clicked; the form submitted from a phone.

**Acceptance:** D4, D7.

---

## 5. Scope

**IN:** everything in §4.

**OUT — do not touch, do not "improve":**
- **The Shopify storefront, theme, products and collections.** The artifact's `s7` audit
  (`2026-08-26`) counted 377 products and 253 archived,
  and a catalog decision Tom has not made. Artifact section `shop` is a separate job.
- The five old blog posts. Record the health-claim exposure loudly (§6.E) and leave them —
  editing regulatory copy without approval is worse than leaving it.
- Social accounts — `docs/plans/2026-08-31-social-foundation-masterprompt.md`.
- The lead pipeline internals — you call `/ingest`, you do not modify it.
- DNS. You prepare records and instructions; Tom points them.
- **Redesigning R124.** Port it. If you believe a section is wrong, say so in the report.
- The four category landing pages — those are
  `docs/plans/2026-08-31-category-menus-masterprompt.md`, built **into this same repo**
  using the design system you establish here. Leave them room; do not build them.

---

## 6. Tom's part — the complete list, nothing else is yours

**A. Where the site lives.** Same domain as the shop with the shop on a path, a
subdomain, or a different domain entirely. This is the decision the artifact calls `w2`
and it changes the redirect map, so it is needed before W6. ~10 minutes.

**B. Point the DNS** once the session hands you the exact records. A few minutes, and it is
the only step that makes the site real.

**C. Approve the Hebrew copy.** The session translates; only you decide how GT speaks.
Read it once end to end before it is public.

**D. HubSpot: keep, migrate or close.** Enquiries are going there today and nobody has
confirmed anyone reads them. If they are being read, someone needs telling that the
destination changes. If they are not, there may be a backlog worth exporting first.

**E. The five blog posts.** They contain `מפחית סיכון לסרטן` and similar. Your own
boundaries chapter forbids exactly this. Decide: rewrite, unpublish, or accept the risk —
in writing, so the decision has an owner.

**F. Approve which customer names appear publicly** (the site names several).

**G. Confirm the cups-per-bottle figure.** Three GT surfaces currently say `33`, `30` and
`13`. The approved arithmetic gives **20 from a 1 L bottle**. Say it once and it gets
fixed everywhere.

---

## 7. Landmines — do not rediscover these

1. **`wsrv.nl` is a free public proxy with rate limits, and it is currently load-bearing.**
   Bulk-downloading 144 images *through it* will get you throttled mid-migration. Fetch
   from the CloudFront origin directly; the proxy is only how the browser renders them.
2. **~20 MB per image × 144 ≈ 3 GB, and this session's disk is a fixed allowance.**
   `df` will mislead: "Avail 0" with low "Used" means the allowance is spent, not that the
   machine is broken. Batch, encode, delete originals, repeat.
3. **`Bellefair` and `Playfair Display` have no Hebrew glyphs.** Every heading using them
   falls back silently and the page looks broken in a way that reads as "cheap site", not
   as "missing font". Swap the display faces before translating, not after.
4. **The CloudFront URLs are artifact-upload URLs, not a hosting product.** They can rotate
   or expire with no notice and no warning to GT. If a fetch starts returning `403`, that
   is not a transient error — stop and tell Tom immediately, because it means the only
   copy of the site's imagery outside the warehouse is going away.
5. **Shopify is misconfigured as `taxesIncluded=true @17%`.** The stored line price is
   ex-VAT. Any price pulled from Shopify's tax/net/gross columns is wrong by `17/117`.
   Use the TSV. Same trap documented in `Sales-Machine/recipes/sales-report.md`.
6. **A parallel session may be on this** (Tom, 2026-08-31). Check `gt-site` branches before
   your first commit, and again before your first push. Two sessions rewriting 215 image
   references in one file is a merge nobody wins.
7. **`200 OK` from the form proves the request was accepted, not that a lead exists and
   not that a human was alerted.** Watch the row appear.
8. **Do not delete the three `301` redirects created `2026-08-26`.** They fix dead blog
   links pointing at archived products, in the blog and everywhere else at once.

---

## 8. Halt conditions

Inherited from `gt-factory-os-production-brain/CLAUDE.md` §Stop conditions. Additions:

- Any CloudFront source returns `403`/`404` → **STOP** the migration, tell Tom. The
  imagery is disappearing and that is now the urgent problem.
- Any change to Shopify products, theme or collections → **STOP**.
- Any DNS change → **STOP**, Tom's.
- The site would go live with a number not traced to an approved source → **STOP**.
- Publishing a health claim about a product → **STOP**.

---

## 9. Final report — Hebrew, short, honest

1. The URL a stranger can open, and what they see, on a phone.
2. D1–D8 ✅/❌ with evidence pointers. No partial credit.
3. The numbers: images migrated · total page weight before/after · Lighthouse scores ·
   figures reconciled · redirects mapped.
4. The artifacts, and where they are.
5. What is still Tom's, and what is genuinely unfinished.
6. The single next action.

Then stamp this file `STATUS: SHIPPED — <date>` with evidence pointers, and commit.
