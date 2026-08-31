# MASTERPROMPT — the GT brand site: from an unpublished theme to one Tom can publish

**STATUS: LIVE — not yet executed**
**SUPERSEDES:** `docs/plans/2026-08-31-website-hebrew-masterprompt.md` — written this
morning against an empty `gt-site` and a static-hosting plan. That plan is obsolete: the
Hebrew build and the image migration are done, and the site went to Shopify as a theme.

> **Usage (Tom):** paste this whole file as the first message of a fresh Claude Code
> session with `gt-site`, `gt-factory-os-production-brain`, `gt-factory-os` and
> `Sales-Machine` attached, and the Shopify, Supabase and Dropbox connectors on. It takes
> the site from "an unpublished theme nobody has seen rendered" to "publishable, and every
> number on it defensible." It halts for you only where §6 says.
>
> **Provenance:** written 2026-08-31, after the first build session, from direct
> measurement of `gt-site@afb7e17` and the live store — not from that session's report.
> `COLS` and `MK` were parsed out of `src/index.html` and compared in code against
> `.claude/skills/drinks-pricelist/drinks_final_figures.json`; theme `162206646513` was
> queried on the store; the preview URL and a local render were both attempted in
> Chromium. Prior work: `gt-site` PR #1, `gt-factory-os-production-brain` PR #187
> (`shopify-theme` skill, commit `1cdfb7c`).
>
> **Shelf life:** §2 is presumed stale after 2026-09-14. Re-run §2.6. If the theme id or
> the live theme has changed, **halt and surface it** before touching the store.

---

## 0. How to work

- **Who you are here:** one Claude Code session. You hold `gt-site` with push access,
  Shopify Admin (read **and** theme write), Supabase, Dropbox, and Chromium via Playwright.
  You own everything technical. You own **no** price, **no** claim, and **no** publish.
- **Read first, in order:**
  1. `gt-factory-os-production-brain/CLAUDE.md`
  2. `gt-factory-os-production-brain/.claude/skills/shopify-theme/SKILL.md` — **every trap
     in it was paid for once already.** If it is not on your branch, it is on
     `origin/claude/file-to-website-8quodp` in this repo, commit `1cdfb7c`.
  3. `gt-site/README.md` — the build, the theme id, how a change is deployed
  4. `gt-site` PR #1 in full — what was done and what was left open
  5. `docs/pricing/2026-08-27_COST_MODEL.md` — **especially line 78**
  6. `Sales-Machine/CLAUDE.md` and `doctrine/pricing-logic.md`
- **Authority:** the repos' `CLAUDE.md` files win. Halt conditions, evidence standard and
  git discipline are inherited from `gt-factory-os-production-brain/CLAUDE.md` — §8 lists
  only the additions.
- **The standard.** This site is the first thing a café owner sees, and it publishes 116
  prices. Three prohibitions:
  1. **No number on the page may disagree with GT's figures of record.** Not by a shekel,
     not by a percentage point.
  2. **No claim without a source**, and no placeholder text of any kind.
  3. **Nothing is published.** `HE-RU Vodoma 2024` stays MAIN until Tom says otherwise, in
     writing, in a message you can quote.
- **Be lazy on purpose.** The build pipeline works and is well made. Extend it; do not
  rewrite it. If you find yourself replacing `tools/`, you have taken a wrong turn.
- **Language:** this document is English; data literals stay in their own script in
  backticks. The site is Hebrew. **Output language: concise Hebrew for Tom, concise
  English otherwise.**

---

## 1. Mission and definition of done

**One testable sentence:** every figure and claim on the site is traceable to an approved
source, the enquiry form lands a lead in `sales_core`, and Tom has seen the page rendered
and said the word — leaving publishing as one deliberate click.

| # | Condition | The observation that would prove it false |
|---|---|---|
| D1 | Every drink figure in `COLS` **and** `MK` matches `drinks_final_figures.json` | Run the §2.6 comparison. Any of the 48 + 23 entries differing on cost, price or margin = fail |
| D2 | `COLS` and `MK` derive from one source; a price change is a one-place edit | Change one figure at the source, rebuild, and see it move in both renderings. Two edits needed = fail |
| D3 | Zero placeholder text on the page | `grep -c "ממתין לחומרים\|TODO\|placeholder" src/index.html` returns 0 |
| D4 | Every factual claim carries a source, or is gone | The three in §2.4 each resolved; a fourth found and unresolved = fail |
| D5 | The enquiry form writes to `sales_core` and alerts a human | Submit a test; `select ... from sales_core.lead order by created_at desc limit 1` does not show it = fail |
| D6 | The page has been rendered and looked at, desktop and mobile | Screenshots at 1440px and 390px exist in the PR. "The bytes are correct" is not this condition |
| D7 | Performance, accessibility and analytics each have a measured baseline | A number missing for any of the three = fail |
| D8 | `./tools/build.sh` runs in CI on every push | Push a branch with a deliberately broken anchor; CI must go red |
| D9 | The publish decision is Tom's and is recorded | Theme role of `162206646513` is `UNPUBLISHED` unless a quoted Tom instruction says otherwise |

Anything not on this list is out of scope unless Tom asks.

### 1.1 Settled — do not reopen

- **The build architecture is right.** `src/index.en.html` never edited · translation by
  character span · every patch asserts its anchor · `--identity` reproduces the source
  byte-for-byte. This is a good design. Extend it.
- **Shopify theme, not separate hosting.** The earlier plan (static repo on a CDN) is
  superseded. The site is a theme on `greenteaeveryday.myshopify.com` and the store keeps
  serving product, cart and account routes underneath.
- **The image migration is complete and correct.** See §2.3 — and read the landmine in §7.1
  before you "fix" anything about it.
- **`glassSVG` is dead code, not a broken feature.** One reference: its own definition. A
  false-green entry already records the earlier misreport. Do not "repair" it; wiring it up
  is a feature request, not a bug.
- **`HE-RU Vodoma 2024` stays MAIN.**

---

## 2. Ground truth — measured 2026-08-31 after the build session

### 2.1 What exists and is genuinely done

| | |
|---|---|
| Branch | `gt-site` `claude/file-to-website-8quodp` @ `afb7e17`, 6 commits, 91 files |
| PR | `gt-site` #1 — draft, `mergeable_state: clean` |
| Theme | `162206646513` · `GT Site v5 — Hebrew (do not publish)` · **UNPUBLISHED** · created `2026-08-31T10:57:51Z` |
| Live theme | `131669328113` · `HE-RU Vodoma 2024` · **MAIN**, last touched `2026-03-29` — untouched |
| Translation | 1,178 strings; `--identity` round-trip byte-identical |
| Step icons | 221/221 resolve (the English build resolved 214) |
| Images | 147 on Shopify's CDN, 5 dead at origin; **0 remote URLs in any theme file** |
| Section size | 57 KB of the 256 KB Liquid limit; 1 section of 25 |
| Rendered page | `dir="rtl"`, one `<h1>`, 20 `<h2>`, 114 images, 16,367 px tall, **0 JS errors**, mobile nav toggle present (`aria-label="תפריט"`) |

That last row is measured, not inherited — see §2.5.

### 2.2 The reorganizing fact: every drink figure on the site is the superseded set

`docs/pricing/2026-08-27_COST_MODEL.md:78` names the figures of record:
`.claude/skills/drinks-pricelist/drinks_final_figures.json` (last written `2026-08-27`,
commit `b31b656`). Compared in code against the site's `COLS`:

**0 of 48 match. 47 differ. 1 (`חליטת תה ירוק לואיזה וליים`) is not in the record at all.**

The site carries the figures from `docs/pricing/2026-08-05_drinks_final_figures.json` —
last written `2026-08-05` and never since. The worst gaps are not rounding:

| Drink | Site says | Record says |
|---|---|---|
| `מאצ'ה קוקוס תות` / `מנגו` / `אפרסק` | ₪7.06 · **₪28** · 70% | ₪5.79 · **₪44** · 84% |
| `אייס מאצ'ה מנגו` / `תות` / `אפרסק` | ₪6.17 · **₪26** · 72% | ₪6.46 · **₪39** · 80% |
| `גזוז מדברי ואפרסק` | ₪5.79 · **₪22** · 69% | ₪4.80 · **₪33** · 83% |
| `דירטי צ'אי` | ₪5.65 · **₪24** · 72% | ₪6.57 · **₪32** · 76% |
| `חליטת אפרסק מדברית` | ₪5.41 · **₪24** · 73% | ₪4.80 · **₪31** · 82% |
| `חליטת היביסקוס וליים` | ₪3.76 · **₪19** · 77% | ₪3.25 · **₪20** · 81% |

**And `MK` is a second copy of the same stale set** — 23 entries, each with its own
`p` / `m` / `fc`, all matching the superseded file. So the handoff's "two catalogues that
disagree with each other" is the smaller half: they also both disagree with the company.

**This is inherited, not introduced.** The R124 design was authored before the
2026-08-26/27 repricing, and the build session translated it faithfully. Nobody made a
mistake — but the site is one publish away from recommending ₪28 for a drink GT prices at
₪44, on a public page, in writing.

### 2.3 The images — done, and the trap that follows

`theme/sections/gt-home.liquid`: **0** `wsrv.nl`/`cloudfront` references, 92 `asset_url`
references. `theme/assets.manifest.json`: 147 entries mapping each asset to the URL it came
from.

`src/index.html` still contains **431** remote references. **That is correct.** It is the
browser-preview build; `tools/build_theme.py` rewrites the URLs on the way into `theme/`.
Do not "clean" it — see §7.1.

### 2.4 What is NOT resolved

- **A placeholder is on the page:** `תמונות מפעל וצוות — ממתין לחומרים`, one occurrence,
  in the About section.
- **Three unsourced claims:** `20–30% פחות אלכוהול מאשר לפני עשור` (no source anywhere in
  the file) · `51 משקאות` in one place against `48` everywhere else · `עד 85%` margin and
  `₪3.25` food cost as published figures.
- **The form is `mailto:`.** `pSend()` at line 1907 builds a message and sets
  `window.location.href='mailto:…'`. It fails silently on most mobile browsers and on any
  desktop without a configured mail client. **Every lead the site earns is currently lost.**
- **116 prices on a public URL** while `Sales-Machine/doctrine/pricing-logic.md` is
  `UNRESOLVED (U-003)`. Note: the live theme already carries a B2B pricing app
  (`bss-b2b-js.js`, 948 KB) — GT has customer-specific pricing infrastructure, so
  "behind a login" is a real option and not a rebuild.
- **`Don't Drink Boring.`** left in English as a slogan — deliberate, needs confirming.
- **5 dead images** on `403` at origin; the page's own fallback covers them.
- **One section, no `{% schema %}`** — nothing is editable in the theme editor.
- **No CI**; `tools/validate.js` is run by hand.
- **Performance, accessibility and analytics: never measured.** 63 inline `onclick`
  handlers, 69 `alt` attributes across 67 `<img>` tags in the source page.

### 2.5 The live preview cannot be rendered from a Claude session — but a local render can

Reproduced on 2026-08-31, after PR #1 reported it:

- `curl https://gteveryday.com/` → `200`; the preview URL → `302` (the cookie redirect).
- Chromium → `net::ERR_CONNECTION_RESET`, **with and without** `proxy: {server:
  'http://127.0.0.1:45361'}`. The browser does not get out; `curl` does.

So the live visual check belongs to a human on a real browser (§6.A). **What does work,
and is proven:** render the built file from disk with remote requests blocked.

```js
// node local.mjs — Playwright is at /opt/node22/lib/node_modules/playwright
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
const b = await chromium.launch({ args:['--no-sandbox'] });
const ctx = await b.newContext({ viewport:{width:1440,height:1000}, locale:'he-IL' });
await ctx.route(u => /^https?:/.test(u.href), r => r.abort());  // fonts+images are unreachable
const p = await ctx.newPage();
await p.goto('file:///home/user/gt-site/src/index.html', {waitUntil:'domcontentloaded'});
await p.waitForTimeout(3000);
await p.screenshot({ path:'desktop.png', timeout:60000 });
await p.setViewportSize({width:390,height:844});
await p.screenshot({ path:'mobile.png', timeout:60000 });
```
Without the `route` abort the screenshot hangs on `waiting for fonts to load` and times
out at 30 s. That single line is the difference between "cannot be verified" and D6.

### 2.6 Re-verification block — run before planning

```bash
git -C /home/user/gt-site fetch --all && git -C /home/user/gt-site branch -a   # other sessions?
```
```python
# the figures comparison — this is the gate, run it first
import re, json
s = open('/home/user/gt-site/src/index.html', encoding='utf-8').read()
cols = json.loads(re.search(r'const COLS=(\[.*?\]);', s, re.S).group(1))
auth = json.load(open('/home/user/gt-factory-os-production-brain/.claude/skills/'
                      'drinks-pricelist/drinks_final_figures.json', encoding='utf-8'))['pages']
A = {v['name']: v for v in auth.values()}
n = lambda x: float(str(x).replace('₪','').replace('%',''))
bad = [d['he'] for c in cols for d in c['drinks']
       if d['he'] not in A
       or abs(n(d['fc'])-n(A[d['he']]['cost'])) > 0.005
       or int(d['p']) != int(n(A[d['he']]['price']))
       or int(d['m']) != int(n(A[d['he']]['marg']))]
print(len(bad), 'of 48 wrong')      # 2026-08-31: 48
```
Then query the store and confirm `162206646513` is still `UNPUBLISHED` and
`131669328113` is still `MAIN`.

---

## 3. What the hard part actually is

**Reframe 1 — this is a correctness job now, not a build job.** The build is good: the
translation is provably lossless, the RTL work is thorough, the images are GT's, the theme
is clean. What is left is that the page states 71 sets of figures and **not one of them is
the company's current number**. Everything else on the open list — the placeholder, the
form, the sections, the CI — is smaller than that, and all of it is wasted if the site goes
up quoting last month's prices to a restaurant owner who can add.

**Reframe 2 — nobody has seen this page.** PR #1 says so plainly, and it is right: the
browser cannot reach the store from a Claude session. Every visual claim in that PR rests
on comparing bytes. That is honest and it is not the same as looking. Two of the risks here
are invisible to byte comparison — a mirrored hero whose composition now fights the copy,
and an RTL layout that is correct in CSS and wrong to a reader. §2.5 gives you a render
that works; use it before you touch anything, so you are fixing what is there rather than
what the diff implies.

**Reframe 3 — the form is the only part of this site that has a job.** A brand site for a
wholesale factory exists to turn a stranger into an enquiry. `pSend()` opens a mail client
and hopes. Every other item on the list changes how the site looks; this one is the
difference between a site that works and a brochure. GT already has `sales_core`, a live
queue, alerting, assignment and conversion tracking — the destination exists and is
running. Wire it, then prove a row arrived.

**Reframe 4 — the price-visibility question is not a web decision.** 116 wholesale prices
and a per-cup margin on a public URL is a commercial posture: it tells every competitor
exactly what GT charges, and it tells every customer that the price is the price. The copy
(`כל המחירים. על השולחן.`) says it was meant. But `U-003` is open, and the live theme
already runs a B2B pricing app, so the alternative is configuration rather than
construction. Put the choice to Tom with both costs stated (§6.C) — do not infer it from
the copy, and do not quietly hide the list.

---

## 4. Workstreams

### W1 — One source for the figures (do this first; nothing ships until D1 passes)

1. Make `drinks_final_figures.json` the input. Add a build step that reads it and emits the
   drink data, so `COLS` and `MK` are both generated rather than hand-written. That is D2,
   and it is what stops this recurring the next time a price moves.
2. `MK` is a different shape — flavour → variants, with its own titles. Generate its
   figures from the same source and keep its titles; do not flatten it into `COLS`.
3. `חליטת תה ירוק לואיזה וליים` has no entry in the record under that name. **Do not guess
   a match.** Find it by SKU or by recipe, or raise it as §6.E.
4. Re-run §2.6. `0 of 48 wrong` is the gate, and `MK` must be clean too.

Where a figure changes a **price**, that is a customer-facing change of what GT recommends
— it is right, because the record is the record, but list every one of them for Tom in the
report so he is not surprised by a ₪28 that became ₪44.

**Acceptance:** D1, D2.

### W2 — The form writes to `sales_core`

Replace the `mailto:` path with a POST to `/ingest`, carrying a `source_id` that identifies
the brand site. **The `source_id` registry is owned by the lead-system session** —
`docs/plans/2026-08-31-lead-response-system-masterprompt.md`, contract C1 in the war room.
Request a value; do not invent one.

Then prove it end to end: submit a real test enquiry, show the row in `sales_core.lead`,
and show the alert arriving. A `200` proves the request was accepted and nothing more —
`gt-factory-os-production-brain/CLAUDE.md` §Evidence puts that at layer 1 of 6.

Keep a no-JS fallback so a blocked script does not silently swallow an enquiry, and handle
the failure case visibly: an error the visitor can act on, never a silent reset.

Also record what HubSpot currently receives from the live site and hand that to Tom
(§6.D) — there may be a backlog nobody has read.

**Acceptance:** D5.

### W3 — Look at the page, then fix what you see

Run the §2.5 render at 1440px and 390px **before** planning any fix. Then work the list:
remove the placeholder, resolve the three claims per Tom's answers, and check the two things
only a render shows — the mirrored hero photographs against the Hebrew copy, and whether the
RTL layout reads correctly rather than merely computing correctly.

Put both screenshots in the PR. That is D6, and it is the condition that stops this session
repeating the last one's blind spot.

**Acceptance:** D3, D4, D6.

### W4 — Implement Tom's pricing decision (§6.C)

Public, behind a login, or removed. If behind a login, the B2B app already on the store is
the mechanism, not a new build. If public, add `noindex` on the price section's own route if
one is introduced, and say so.

### W5 — Sections Tom can edit

Split out only what he will actually edit: hero, About, FAQ, contact. Each with a
`{% schema %}` carrying its real fields. **Do not split all 13** — every section is a file
someone maintains, and the drink data is generated, so exposing it in the editor invites
exactly the hand-edit W1 exists to prevent.

Watch the limits: 25 sections per template, 256 KB per section. You are at 1 and 57 KB.

### W6 — Measure the three that were never measured

- **Performance** — Lighthouse against a locally served copy of the theme's built page
  (the live URL is unreachable, §2.5). Report LCP, CLS, TBT and total transferred weight.
  The page is 16,367 px tall with 114 images; lazy-loading is in place and Shopify serves
  WebP, so measure before optimising.
- **Accessibility** — axe or Lighthouse on the same render, plus a manual keyboard pass
  through the drink modal, the FAQ and the mobile menu. 63 inline `onclick` handlers are
  the thing to check: a `div` with an `onclick` is invisible to a keyboard and to a screen
  reader. Report the count that are not on a real button or link.
- **Analytics** — GA4 or Plausible, plus Search Console verification. Without it, nobody
  can tell whether the site works.

**Acceptance:** D7.

### W7 — CI

A workflow running `./tools/build.sh` and `tools/validate.js` on every push. Prove it fails:
move an anchor deliberately, watch CI go red, revert. A green check that has never been red
is not evidence.

**Acceptance:** D8.

### W8 — The publish rehearsal — prepare it, do not do it

Write `gt-site/PUBLISH.md`: the exact steps, the rollback (`HE-RU Vodoma 2024` is
`131669328113` — publishing it back is the undo), what to check in the first ten minutes,
and who to tell. Then stop. **Publishing is §6.F and it is Tom's.**

**Acceptance:** D9.

---

## 5. Scope

**IN:** everything in §4.

**OUT — do not touch, do not "improve":**
- **Publishing the theme.** Under any circumstances, without a quoted written instruction
  from Tom.
- **The live theme `131669328113`**, its templates, its apps, its settings.
- Shopify products, collections, prices, or the B2B app's configuration.
- `drinks_final_figures.json` — it is the record; you read it.
- `src/index.en.html` — never edited, by design.
- Rewriting `tools/`. Extend it.
- `glassSVG` — dead code, already misreported once.
- The four category landing pages — those belong to
  `docs/plans/2026-08-31-category-menus-masterprompt.md`, built on your foundation
  (war-room contract C3).
- The old blog posts and their health claims — record, do not edit.

---

## 6. Tom's part — the complete list, nothing else is yours

**A. Open the preview in your own browser and read it.**
`https://gteveryday.com/?preview_theme_id=162206646513` — the **full** URL; Shopify sets a
cookie and redirects, and a shortened link loses it. No Claude session can render this page,
so you are the only one who can see it on the real store. Mark what to change. **This is
the biggest single unblock on the list.**

**B. The prices are about to change on you.** Every one of the 48 drinks on the site carries
last month's figure. Correcting them to the record moves real numbers — `מאצ'ה קוקוס תות`
goes from a recommended ₪28 to ₪44, `אייס מאצ'ה מנגו` from ₪26 to ₪39, `דירטי צ'אי` from
₪24 to ₪32. If the record is right, say so and the session applies it. If any of these look
wrong to you, that is a figures problem and it is bigger than the website.

**C. The wholesale price list on a public page.** 116 prices and the per-cup margin, visible
to anyone including your competitors. The copy says it was deliberate; `U-003` is still
open. Public, behind a login (the B2B app is already installed), or removed. One sentence.

**D. HubSpot** — enquiries from the live site go there and nobody has confirmed anyone reads
it. Keep, migrate, or close.

**E. The claims.** `20–30% פחות אלכוהול מאשר לפני עשור` needs a source or it comes off ·
`51 משקאות` versus `48` — which · `עד 85%` and `₪3.25` — approved to publish or not ·
`Don't Drink Boring.` in English — deliberate?

**F. The publish decision, in writing.** Nothing goes live without it. When you are ready,
say the words and the session executes `PUBLISH.md`.

**G. The About photographs.** The placeholder says `ממתין לחומרים`. Factory and team photos,
or the block comes off the page — it cannot go live either way.

---

## 7. Landmines — do not rediscover these

1. **`src/index.html` contains 431 remote image URLs and that is correct.** It is the
   browser-preview build; `build_theme.py` rewrites them into `theme/`, which has zero.
   "Cleaning" the source undoes the pipeline and re-hardcodes what the build generates.
2. **Two files are named `drinks_final_figures.json`.**
   `.claude/skills/drinks-pricelist/` is the record (`2026-08-27`, keyed by Canva page
   number, field `name`). `docs/pricing/2026-08-05_…` is superseded (keyed by index, field
   `heb`). **The site is currently built on the wrong one** — that is §2.2, and reading the
   wrong file again will tell you the site is fine.
3. **The preview cookie makes a working upload look broken.** A client that drops cookies
   gets the live theme back. And once the cookie is set, the new site appears at a bare
   `gteveryday.com` in that browser — **which does not mean it was published.** Check the
   theme's `role` on the store, never the browser.
4. **`themeFilesUpsert` returns an empty `upsertedThemeFiles` on success.** Not an error.
   Verify by querying `files` and checking `size` and `contentType`.
5. **Chromium cannot reach the store from this environment** — `ERR_CONNECTION_RESET`, with
   or without the proxy, while `curl` gets `200`. Do not spend an hour on it. Render locally
   (§2.5) and give the live look to Tom.
6. **Blocking remote requests is required for a local screenshot.** Otherwise Playwright
   hangs on `waiting for fonts to load` and times out at 30 s, which reads like a broken
   page rather than an unreachable font host.
7. **Image assets are content-negotiated.** `curl` without `Accept: image/webp` gets the
   PNG — 800 KB against 94 KB for the same asset. Never infer page weight from a request
   without the header.
8. **`url()` inside a CSS custom property resolves against the stylesheet, not the
   document.** `asset_url` emits an absolute URL so it is safe; a hand-written relative path
   breaks silently.
9. **`backdrop-filter` creates a containing block.** It collapsed the mobile menu to the
   height of the nav bar once already.
10. **The theme is a duplicate of the live one**, so it carries Vodoma's apps and assets
    (`bss-b2b-js.js` is 948 KB). Product, cart and account routes render from that layer —
    if one of them looks wrong, it is Vodoma, not your section.
11. **`gt-site` may have more than one session on it.** `fetch` before your first commit and
    again before your first push.

---

## 8. Halt conditions

Inherited from `gt-factory-os-production-brain/CLAUDE.md` §Stop conditions. Additions:

- **Any action that would publish a theme, change the MAIN theme, or alter
  `131669328113`** → **STOP**. This is the one that cannot be undone quietly.
- A figure would go on the page that is not in `drinks_final_figures.json` → **STOP**.
- A claim would be published without a source → **STOP**.
- The record's own figures look wrong → **STOP** and report. Never edit the record.
- Shopify products, prices or app configuration would change → **STOP**.

---

## 9. Final report — Hebrew, short, honest

1. What Tom can now open and see, and what he must decide before it goes live.
2. D1–D9 ✅/❌ with evidence pointers. No partial credit.
3. The numbers: figures corrected `N/71` · the price changes, listed · lead test result ·
   Lighthouse, axe and analytics baselines · sections split.
4. The artifacts: PR, screenshots, `PUBLISH.md`.
5. What is still Tom's, and what is genuinely unfinished.
6. The single next action.

Then stamp this file `STATUS: SHIPPED — <date>` with evidence pointers, and commit.
