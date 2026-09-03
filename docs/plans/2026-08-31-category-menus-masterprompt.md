# MASTERPROMPT — four category menus a lead can actually read, and the pages behind them

**STATUS: LIVE — not yet executed**

> **Usage (Tom):** paste this whole file as the first message of a fresh Claude Code
> session with `gt-factory-os-production-brain`, `Sales-Machine` and `gt-site` attached,
> and the Canva, Dropbox and Shopify connectors on. It takes GT from "two catalogs too big
> to send anyone" to "four category menus in one format, each with a landing page that
> captures a lead." It halts for you only where §6 says.
>
> **Provenance:** written 2026-08-31. The template design `Ube Menu` (Canva `DAHTZuvZQH0`,
> 9 pages) was read live and every figure on it compared against
> `.claude/skills/drinks-pricelist/drinks_final_figures.json` (`_meta.date` `2026-08-27`,
> the current authority for all 48 drinks). **Eight of nine figures on the template are
> stale and its own last page contradicts its drink pages** — §2.3. Design DNA:
> `docs/warehouses/marketing-assets.md`.
>
> **Shelf life:** §2 is presumed stale after 2026-09-28. Re-run §2.5. If a figure has
> moved, **halt and surface it** — these menus go to customers.

---

## 0. How to work

- **Who you are here:** one Claude Code session. You hold Canva (read and edit), Dropbox,
  Shopify (read), `gt-site` with push access, and the two brain repos. You may edit Canva
  designs and build pages. You may **not** set a price, invent a recipe, or publish a page
  to a live domain.
- **Read first, in order:** `gt-factory-os-production-brain/CLAUDE.md` ·
  `Sales-Machine/CLAUDE.md` · `.claude/skills/drinks-pricelist/SKILL.md` **and run it** —
  it already knows how to validate a catalog against the approved figures, and rebuilding
  that logic by hand is how you introduce a rounding bug ·
  `docs/pricing/MASTER_PROMPT_2026-08-26_catalog_repricing_and_menu.md` §7 — the Canva
  landmines are already written down and they cost real hours ·
  `docs/pricing/2026-08-27_COST_MODEL.md` · `docs/warehouses/catalog-truth.md` ·
  `docs/warehouses/marketing-assets.md`.
- **Authority:** the repos' `CLAUDE.md` files win. Halt conditions, evidence standard and
  git discipline are inherited — §8 lists only the additions.
- **The standard.** Tom's framing: these are menus, not catalogs, and they are what a lead
  receives automatically after clicking a specific ad —
  `נשלח להם את התפריט שמתאים להם... כדי להתחמם, אבל מצד שני לא להתבלבל.` Three
  prohibitions:
  1. **No figure on a customer-facing page may differ from `drinks_final_figures.json`.**
     Not by a rounding step, not by a percent.
  2. **No drink appears without a recipe that a barista can follow**, and no recipe cites
     a product GT does not sell.
  3. **No menu contradicts another menu, or itself.**
- **Be lazy on purpose.** One master template, four instances, one validation script. If
  you are hand-editing the fourth menu's typography, you built the first three wrong.
- **Language:** this document is English; data literals stay in their own script in
  backticks. The menus and pages are Hebrew. **Output language: concise Hebrew for Tom,
  concise English otherwise.**

---

## 1. Mission and definition of done

**One testable sentence:** four category menus exist in one consistent format, every
figure on them provably matches the approved authority, and each has a Hebrew landing page
in `gt-site` whose form writes a lead into `sales_core` tagged with its campaign.

| # | Condition | The observation that would prove it false |
|---|---|---|
| D1 | Four menus exist: `תה קר`, `צ'אי`, `מאצ'ה`, `אובה` | Any missing |
| D2 | Every drink figure on every menu matches `drinks_final_figures.json` | A fresh plain read of every menu page, compared **in code** against the authority, reports 0 deviations across cost, price and margin. One deviation = fail |
| D3 | Every drink on a menu has a recipe, and every ingredient in that recipe resolves to a product in `catalog-truth.md` | Join every recipe ingredient to the catalog; one unresolvable = fail |
| D4 | The 48 drinks are covered exactly once across the four menus — none missing, none duplicated | Union the four menus' drink lists against the authority's 48. Any gap or repeat = fail |
| D5 | Each menu exports as a WhatsApp-sendable file: ≤5 MB, `PNG` or `PDF`, in the decided aspect ratio | Any export over 5 MB, or in a ratio not on the approved list |
| D6 | Four landing pages live in `gt-site`, Hebrew, RTL, matching the site design system | Open each; any English body copy or LTR layout = fail |
| D7 | Each landing page's form writes to `sales_core` with a `source_id` identifying its category | Submit a test on each; `select source_id from sales_core.lead order by created_at desc limit 4` shows four distinct values = pass |
| D8 | The internal contradictions listed in §2.3 are closed in the template before it is cloned | Read `DAHTZuvZQH0` after the fix; any §2.3 item still present = fail |

Anything not on this list is out of scope unless Tom asks.

### 1.1 Settled — do not reopen

- **`Ube Menu` (`DAHTZuvZQH0`) is the format.** Tom said so. You are fixing it and cloning
  it, not redesigning it.
- **`drinks_final_figures.json` (`2026-08-27`) is frozen.** You are a transcriber. A figure
  that looks wrong is a **STOP**, never an edit.
- **Prices were deliberately not raised on `2026-08-27`.** Source:
  `docs/pricing/2026-08-27_COST_MODEL.md`, quoting Tom that day —
  `ב. אל תעלה את המחירים המומלצים יותר`. Do not "restore" a margin by moving a price.
- **The menus show FOOD COST to the customer on purpose.** It is the customer's ingredient
  cost per cup and it is the whole pitch — the customer keeps ~80%. Do not remove it, and
  do not label it in any way that could read as GT's own cost.
- **Only `קטלוג משקאות סופי 26` among the older Canva catalogs carries valid prices.** The
  other three must never be sent. Do not use them as a source.

---

## 2. Ground truth — measured 2026-08-31; re-verify at boot

### 2.1 The template, as it stands

`Ube Menu`, Canva `DAHTZuvZQH0`, 9 pages, `updated_at` 2026-08-31. Two page geometries:

| Pages | Size | Reads as |
|---|---|---|
| 1, 4, 5, 6, 7, 8 | `1080×1920` | 9:16 — story / WhatsApp |
| 2, 3, 9 | `794×1123` | A4 at 96 dpi — print |

Page 1 is a cover plus the brand story. Page 2 describes the `UBE` product. Pages 4–8 are
one drink each: English name, Hebrew name, the cost label `FOOD COST · ללא מע״מ`, the
price label `מחיר מומלץ · כולל מע״מ`, margin, and a numbered preparation. Page 9 is a
price list.

### 2.2 The 48 drinks, by family (the authority's own grouping)

`01 ICED TEA` 7 · `02 LEMONADE` 3 · `03 SIGNATURE` 4 · `04 GAZOZ` 3 ·
`05 ICE MATCHA` 6 · `06 MATCHA SPECIALS` 5 · `07 MATCHA COCONUT` 5 ·
`08 CHAI MASSALA` 6 · `09 COLD FOAM` 4 · `10 UBE` 5. **Total 48.**

Which maps onto the four menus as `תה קר` 16 · `צ'אי` 11 · `מאצ'ה` 16 · `אובה` 5 —
derive the exact split from the authority, do not hand-assign it, and prove D4 in code.

### 2.3 What is wrong with the template — verified 2026-08-31, fix before cloning

**(a) Eight of nine drink figures are stale.** The template carries the pre-`2026-08-27`
cost model. Prices are right; **costs and margins are not**:

| Drink | Template shows | Authority `2026-08-27` |
|---|---|---|
| `אייס אובה תות` / `מנגו` / `אפרסק` | ₪4.73 · ₪30 · **81%** | **₪5.22** · ₪30 · **79%** |
| `אייס אובה מסאלה` | **₪4.93** · ₪31 · **81%** | **₪6.27** · ₪31 · **76%** |
| `אייס אובה מאצ'ה` | **₪4.45** · ₪28 · **81%** | **₪4.96** · ₪28 · **79%** |

**(b) Page 9 contradicts pages 4–8, inside the same design.** It lists
`אייס אובה 24 · אובה מנגו 28 · אובה תות 28 · אובה מסאלה 28 · אובה מאצ'ה 32`. The drink
pages say `30 / 30 / 31 / 28`. It also lists an `אייס אובה` at `₪24` that has no drink
page and is not in the authority's 48.

**(c) The brand mark on the drink pages reads `gt Uba`.** It is `Ube`.

**(d) Page numbers `60`–`64` are leftovers** from the 60-page master catalog. A standalone
5-drink menu numbered 60–64 tells the reader they are holding a fragment.

**A menu with a wrong margin is worse than no menu.** It is the number the customer
decides on, and GT is the one who printed it. Fix (a)–(d) first. Cloning a broken template
four times turns one defect into four.

### 2.4 What exists to build with

- **Imagery:** `docs/warehouses/marketing-assets.md` — 11 one-litre bottle packshots, 11
  half-litre, powder bags, ODK purées, eight accessory shots, ~60 powder lifestyle images,
  17 bottle-and-glass lifestyle shots, all Tom-graded. Canva folder `FAHRTt8KXZg`.
- **Design DNA (approved):** full-bleed photo header with white text over it · `Rubik`
  for emphasis, `Heebo 300` for quiet · product names in spaced capitals · hairlines carry
  the structure · small `₪` in coral · RTL with price columns forced `direction:ltr`.
  Palette: paper `#EFE6D6` · ink `#241C15` · green `#263B18` · coral `#FA6E4D` · rule
  `#D8CCB4` · muted `#7C6E58`.
- **Known image gaps (negative records):** no photo of the matcha kit exists anywhere; the
  22-sachet matcha exists only as a 229 px thumbnail. Route around them; do not upscale.

### 2.5 Re-verification block

```bash
# the authority — {_meta, pages:{"<canva page no>":{name,cost,price,marg,prof,star}}}
python3 -c "import json;d=json.load(open('.claude/skills/drinks-pricelist/drinks_final_figures.json'));print(d['_meta']['date'],len(d['pages']))"
```
Then read `DAHTZuvZQH0` live with `mcp__Canva__read-design` and diff **in code**. Never by
eye — that is how (a) survived until now.

**Do not read `docs/pricing/2026-08-05_drinks_final_figures.json`.** It is a superseded
duplicate with a different shape and different numbers, and it will hand you a page of
contradictions that are not real.

---

## 3. What the hard part actually is

**It looks like:** make four more of the Ube menu.

**It actually is:** a correctness job first and a design job second. The template's own
margins are stale and its last page disagrees with its middle. Clone first and GT sends
four documents that misstate the single number a café owner decides on. **Fix, prove, then
clone.**

**Second reframe:** these are not catalogs. A catalog is browsed; a menu is *received*,
unrequested, on a phone, from a company the reader met sixty seconds ago in an ad. That
sets hard constraints the current template does not meet: one aspect ratio, under 5 MB,
legible at thumbnail size, and short enough to swipe through in a lift. Nine pages of
mixed A4 and 9:16 is a document, not a message.

**Third reframe:** these menus are already committed to as another system's assets. The
lead system's stage 3 (`docs/plans/2026-08-31-lead-response-system-masterprompt.md` §W4)
specifies "three content kits, one per campaign category" — **these are those kits.** Build
them to that spec (`PNG`, `1:1` or `4:5`, ≤5 MB; video 15–30 s ≤16 MB) or they will need
rebuilding. Agree the format with that session before exporting.

**Fourth reframe — the missing menu nobody has asked for.** The Q4 customer plan
(`docs/plans/2026-08-31-existing-customers-q4-masterprompt.md`) rests on replacing the
discontinued `MUZA` cocktail line at 20 customers, worth **₪192,147/yr** — the single
largest identified opportunity in the company. Its substitute is `סנגריה`, and
`UNRESOLVED U-014` records that **no drink page and no documented preparation exists for
any cocktail base in GT** — the catalog deliberately excludes them (Tom, `05/08`). So the
highest-value sales play GT has right now has no collateral at all. That is not this
document's mandate, but it is this document's capability. Raise it as §6.E; if Tom says
yes it becomes a fifth menu and it outranks everything else here on money.

---

## 4. Workstreams

### W1 — Fix the template (first; nothing is cloned until D8 passes)

Close §2.3 (a)–(d) in `DAHTZuvZQH0`. Then re-read the design and prove it in code against
the authority: 5 drinks × 3 fields, 0 deviations.

Take a JSON backup of the design before the first edit, exactly as
`docs/pricing/backups/` does. Canva has no undo an agent can reach.

**Acceptance:** D8, and D2 for the Ube menu.

### W2 — Decide and lock the format

Recommend, then confirm with Tom (§6.A):
- **`1080×1350` (4:5)** for every page of the sendable set. It is the largest ratio
  WhatsApp and Instagram both display without cropping, and it fits more of a recipe than
  `1:1`. `9:16` wastes vertical space on a static menu and crops in feed.
- **A4 as a separate export** from the same content, for printing and for a rep's folder.
- Page count per menu: cover · one page per drink · one price page. `אובה` = 7 pages;
  `תה קר` and `מאצ'ה` = 18; `צ'אי` = 13. **If that exceeds 5 MB, split by sub-family
  before you compress** — a menu at readable quality beats a complete one that is illegible.

**Acceptance:** feeds D5.

### W3 — Build the three new menus

`תה קר`, `צ'אי`, `מאצ'ה`. One master template, three instances. Every drink page carries:
English name, Hebrew name, `FOOD COST · ללא מע״מ`, `מחיר מומלץ · כולל מע״מ`, margin,
numbered preparation, and its product photo from the warehouse.

Sequence them by sales value, not by catalog order: **`צ'אי` first** — one SKU
(`NAMASTEA`, `₪65`) opens 11 drinks using only what every bar already stocks, which the
book identifies as the easiest yes in the range. Then `מאצ'ה`, then `תה קר`.

Where a recipe cites a concentrate that does not exist, fix it against the authority.
Three such defects are already known: `תמצית מנגו סנצ'ה` → `REVIVE`, `תמצית תפוח היביסקוס`
→ `FRESH`, `תמצית consciousness lychee` → `CONSCIOUSNESS`. There is also a duplicated
recipe (`אייס מאצ'ה וניל` is written identically to `מאצ'ה אגבה על הקרח`, with no vanilla,
at a different price) — that one is a real content gap, not a typo. Route it to §6.C.

**Acceptance:** D1, D2, D3, D4.

### W4 — Export and register

Export each menu in both formats. Register every file in
`docs/warehouses/marketing-assets.md` with its grade and date, and place it in the Dropbox
structure the lead system expects (`/מערכת לידים/ערכות/<קטגוריה>/`) with a `גרסה.txt`
carrying the build date — so nobody ever sends last month's prices.

**Acceptance:** D5.

### W5 — Four landing pages in `gt-site`

`/chai`, `/matcha`, `/iced-tea`, `/ube`. Build them **inside the site the website session
is standing up** (`docs/plans/2026-08-31-website-hebrew-masterprompt.md`) using its design
system and its self-hosted Hebrew fonts. Coordinate at boot: if that repo is still empty,
you either wait or you agree who lays the foundation. **Do not build a second design
system.**

Each page: the category's hook in one sentence · three or four representative drinks with
cost, price and margin · what the buyer needs to already own (`תה` and `צ'אי` need nothing;
`מאצ'ה` and `אובה` need a whisk or frother and milk — the book's operational line, and the
reason a powder pitch always includes the equipment) · the menu as a download · one form.

Same image discipline as the site: local assets, `AVIF`/`WebP`, `≤200 KB` hero, explicit
`width`/`height`. Do not hotlink Canva exports.

**Acceptance:** D6.

### W6 — Wire the forms

Post to `sales_core` `/ingest` with a `source_id` per category, matching the taxonomy owned
by `docs/plans/2026-08-31-lead-response-system-masterprompt.md` §W1. Then prove it: submit
a test on each page and show four rows arriving with four distinct `source_id` values.
`200 OK` proves acceptance, not arrival.

**Acceptance:** D7.

---

## 5. Scope

**IN:** everything in §4.

**OUT — do not touch, do not "improve":**
- **`drinks_final_figures.json`.** It is the authority. It is not edited here.
- The 60-page master catalog `DAHTYkRvEnM` and the products catalog `DAHQrpThEBE`.
  Different documents, different owners, a repricing history of their own.
- The other three Canva drink catalogs. Never sent, never sourced from.
- Prices, packages, discounts.
- The website's main pages, hosting or DNS.
- The lead system's automation. You provide assets and pages; it sends.
- **A cocktail menu** — unless Tom says yes to §6.E. Then it comes back in scope and goes
  first.

---

## 6. Tom's part — the complete list, nothing else is yours

**A. Confirm the format.** `4:5` for the sent menus plus a separate A4 for print, or
something else. One sentence, and it sets the shape of all four. ~5 minutes.

**B. Approve the corrected Ube figures going out.** The margins on the current template
read `81%` across the board; the true figures are `79% / 79% / 76%`. If that menu has
already been shown to anyone, you may want to know who. ~5 minutes.

**C. `אייס מאצ'ה וניל`.** Its recipe is written identically to `מאצ'ה אגבה על הקרח`, with
no vanilla in it, at a different price (`₪28` against `₪26`). Either it has a real recipe
nobody wrote down, or it is a duplicate that should be removed from the 48.

**D. `HOJICHA` has no recipe.** Corrected 2026-08-31 by the knowledge-book session (brain
`main` @ `cee556b`): it is **not** absent from the catalog — `GT-HOJ-BLK-500` has been
ACTIVE since `2026-07-27` with stock on hand, and `GT-HOJ-BLK-1000` (`₪750`) since
`2026-08-18`. What is missing is a recipe: a product GT actively sells that no menu can
show. Commission recipes for it, or accept that it stays off the menus.

**E. The cocktail menu — this is the money question in this document.** GT discontinued the
`MUZA` line. 20 existing customers have a `₪192,147`/year hole in their menu right now and
`סנגריה` is the replacement. There is no drink page, no recipe and no preparation spec for
any cocktail base, because the catalog deliberately excludes cocktails (your call, `05/08`,
`UNRESOLVED U-014`). Every one of those 20 conversations therefore happens with no
collateral. Do you want a cocktail menu built? If yes, it is the highest-value item on this
list and it should be built before the other three.

**F. Approve the landing page copy** before anything is published.

---

## 7. Landmines — do not rediscover these

1. **Canva rounds differently than the authority does.** Rounding profit to agorot before
   computing margin yields `81%` where the approved figure is `80%`. The formulas are in
   `_meta.formulas`: `profit = price/1.18 − cost`, `margin% = round(profit ÷ (price/1.18)
   × 100)`. Compute in that order, on unrounded values. This exact bug is already
   documented in `docs/pricing/MASTER_PROMPT_2026-08-26_catalog_repricing_and_menu.md` §7.
2. **A design and its exported PDF are two sources and both get overwritten from the
   authority.** Never validate one against the other — they can agree and both be wrong.
3. **Two files are named `drinks_final_figures.json`.** `.claude/skills/drinks-pricelist/`
   is current (`2026-08-27`, keyed by page number, field `name`).
   `docs/pricing/2026-08-05_…` is superseded (keyed by index, field `heb`, different costs,
   only five price points). Reading the wrong one manufactures contradictions.
4. **`catalog-truth.md` outranks Shopify `ACTIVE`**, by its own header. Four products in
   the current price list are Tom-graded negative records and must not appear on a menu:
   `MATCHA 50 גרם`, `GT ELITA 30 גרם`, `מקציף קוקטיילים`, `קנקן זכוכית עם מסננת`.
   **But the file can be stale in the other direction too, and was:** it recorded "no
   active SKU" for `AMERICAN` and `HOJICHA` while both had been live in Shopify for
   months, and `AMERICAN`'s two prices were swapped in the approved list. A live check on
   2026-08-31 found it and Tom approved the fix (brain `main` @ `cee556b`). Treat the file
   as authority on *what GT chooses to sell*, and verify existence against the live system
   before concluding a product does not exist.
5. **Canva has no agent-reachable undo.** Back up the design JSON before the first edit —
   `docs/pricing/backups/` shows the pattern and `RESTORE_DAHTYkRvEnM.md` exists because
   this was learned the hard way.
6. **WhatsApp re-compresses anything over its limits into unreadability, or rejects it.**
   `PNG` `1:1`/`4:5` ≤5 MB. A beautiful 12 MB export is a broken send.
7. **`אובה` never stands alone.** All five of its drinks need a second GT product. Selling
   it as a standalone entry offer produces a customer who cannot make anything. It is an
   expansion after matcha, or part of a bundle — the book is explicit and the menu's
   framing must match.
8. **`gt-site` may be under construction by a parallel session.** Check branches before
   your first commit and again before your first push.

---

## 8. Halt conditions

Inherited from `gt-factory-os-production-brain/CLAUDE.md` §Stop conditions. Additions:

- A figure in `drinks_final_figures.json` looks wrong → **STOP** and report. Never edit it.
- A drink has no valid recipe, or a recipe cites a product GT does not sell → **STOP**,
  route to §6.
- Any change to a price, or to the 48-drink set → **STOP**, Tom's.
- A menu would be exported carrying an unverified figure → **STOP**.
- A live page would be published to a customer-facing domain → **STOP**, Tom's.

---

## 9. Final report — Hebrew, short, honest

1. The four menus, as files, and the four pages, as URLs.
2. D1–D8 ✅/❌ with evidence pointers. No partial credit.
3. The numbers: drinks covered `N/48` · figures verified `N/N` · deviations found and
   closed · export sizes.
4. The artifacts, and where they are registered.
5. What is still Tom's, and what is genuinely unfinished — including §6.E.
6. The single next action.

Then stamp this file `STATUS: SHIPPED — <date>` with evidence pointers, and commit.
