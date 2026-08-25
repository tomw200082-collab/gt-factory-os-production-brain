# MASTERPROMPT — GT's opening menu for a new lead: one mobile-native WhatsApp PDF

**STATUS: SHIPPED 2026-08-25 — evidence `Sales-Machine/evidence/2026-08-25-lead-welcome-menu.md`**
<!-- Executed 2026-08-25. Deliverable: `gt-factory-os-production-brain/.claude/skills/lead-welcome-menu/lead-menu.pdf` (15 screens, ratio 0.5625, 2,338,979 bytes). D1-D9 all PASS. Two items remain Tom's: approval of the finished PDF before it reaches a lead (§6.D), and the MATCHA image (§6.A), which §6.A itself says not to block on. -->
<!-- The executing session's last act is to change this line to SHIPPED / SUPERSEDED by <path> /
ABANDONED — why, with evidence pointers. -->

> **Usage:** paste this entire file as the first message of a fresh Claude Code session with
> `gt-factory-os-production-brain` and `Sales-Machine` attached, and the Google Drive, Dropbox
> and Canva MCP servers connected. It takes GT's lead-welcome menu from "designed and costed,
> nothing built" to "a production PDF Tom can send to a real lead tomorrow morning."
> It halts for Tom only where a human must genuinely act — §6 is that complete list.
>
> **Provenance:** written 2026-08-25 by the scoping session, from live reconnaissance performed
> that day: both Canva catalogs read through the Canva MCP; the approved cost figures read from
> `drinks_final_figures.json`; the asset pipeline downloaded and byte-verified through the Google
> Drive MCP; the HTML-to-PDF toolchain rendered and its output inspected. Every number below
> carries its source. Design decisions marked "Tom, 2026-08-25" were taken by Tom in that session.
>
> **Authority:** `gt-factory-os-production-brain/CLAUDE.md` → `Sales-Machine/CLAUDE.md` →
> this document. Cited below by section, never copied. Where this document and an authority doc
> disagree, the authority doc wins and this document is wrong.
>
> **Shelf life:** §2 is presumed wrong if pasted after 2026-09-08. Re-run §2.6 first.
> If the approved-figures file has changed, **halt and surface** — do not adapt. Every number on
> this page is a price a café owner will act on.

---

## 0. How to work

- **Who you are here:** a single fresh Claude Code session with full tool access, owning this
  end to end. You hold the four GT repos, the Google Drive / Dropbox / Canva / GitHub MCP
  servers, and a headless Chromium. You decide every design, typographic and layout question
  yourself. You decide **no** number, no product claim, and no price. Those come from files
  named in §2 or from Tom in §6.
- **Read first, in order:** `gt-factory-os-production-brain/CLAUDE.md` ·
  `Sales-Machine/CLAUDE.md` · `Sales-Machine/CURRENT_STATE.md` ·
  `gt-factory-os-production-brain/docs/warehouses/catalog-truth.md` ·
  `gt-factory-os-production-brain/docs/warehouses/marketing-assets.md` ·
  `gt-factory-os-production-brain/.claude/skills/drinks-pricelist/SKILL.md`
- **Authority:** halt conditions, the evidence standard, and git discipline are **inherited** from
  `gt-factory-os-production-brain/CLAUDE.md` §Stop conditions, §Evidence and §Write boundaries,
  and from `Sales-Machine/CLAUDE.md` §The 7 truth rules and §Stop conditions. They are not
  re-authored here. §8 lists only the additions specific to this work.
- **Invoke skills before acting, not after.** Start by invoking `using-superpowers`. The design
  sequence in W2 is not a suggestion — each movement names the skill that governs it.
- **The standard.** Tom set it on 2026-08-25 in three phrases, quoted verbatim:
  - `מספיק יפה עיצובית בשביל פרודקשן` — visually good enough for production.
  - `יפה בצורה הירואית, ללא דופי` — heroically beautiful, flawless.
  - `אני כבר רוצה לשלוח את זה ממחר ללקוחות` — ready to send to real customers tomorrow.

  Translated into checkable prohibitions:
  1. **Nothing on the page may be unreadable on a phone.** No content text below 36px at the
     1080px design width (D4). This is the single most common way this deliverable fails.
  2. **Nothing on the page may be a number you produced.** Every figure traces to
     `drinks_final_figures.json` or to `catalog-truth.md` (D3).
  3. **Nothing on the page may look like a template.** No stock component defaults, no generic
     SaaS card grid, no Canva-preset gradient. The design DNA is GT's own, extracted in W1.
- **Language:** this document is in English because that is the register you reason best in.
  Data literals stay in their own script, in backticks, and are never translated — a translated
  drink name matches nothing in the figures file. **The deliverable's own content is Hebrew,
  RTL.** **Output language for your replies: concise English.** Short sentences, no preamble,
  no restating the question, no summary of what you are about to do.

---

## 1. Mission and definition of done

**The artifact:** `gt-factory-os-production-brain/.claude/skills/lead-welcome-menu/lead-menu.pdf`,
built from `lead-menu.html` beside it. That path is fixed; every done-condition below refers to it.

**One testable sentence:** produce one Hebrew, right-to-left, 9:16 mobile-native PDF of exactly
15 screens that presents four GT products and twelve costed drinks to a business lead who just
left their details, built entirely from approved figures and approved assets, small enough to
send on WhatsApp, and beautiful enough that Tom sends it to a paying prospect without edits.

| # | Condition | The observation that would prove it false |
|---|---|---|
| D1 | Page geometry is 9:16 and the deck is exactly 15 screens | `python3 verify.py --geometry` prints `ratio 0.5625` (±0.001) and `pages 15`; it reads `/MediaBox` and counts `/Type /Page` with the negative-lookahead regex in §2.6 |
| D2 | The file sends on WhatsApp without degradation | `stat -c%s` on the built PDF ≤ `4194304` |
| D3 | Every drink figure is the approved figure | `python3 validate.py` prints `deviations 0`; it compares all four fields of all twelve drinks against `drinks_final_figures.json` **and independently re-derives** `profit = price/1.18 − cost` and `margin = profit / (price/1.18)` |
| D4 | Nothing is unreadable on a phone | `python3 verify.py --type-scale` prints `min content font-size 36px` or larger, scanning every `font-size` in the built CSS outside the `.legal` class |
| D5 | No wholesale price reaches the lead | `python3 verify.py --no-wholesale` finds zero matches for `₪65`, `₪33`, `₪590`, `₪375`, `₪340`, `₪175`, `₪170`, `₪118`, `₪60`, `₪37`, `₪36`, `₪30`, `₪25`, `₪20`, `₪11`, `₪10` in the rendered text layer |
| D6 | No discontinued product is shown | `python3 verify.py --no-wholesale` also finds zero matches for `GT Elita`, `מאצ׳ה 50`, `מקציף קוקטיילים`, `קנקן נפוליטן` |
| D7 | The PDF renders with no network | `grep -nE 'https?://' build/*.html build/*.css` returns nothing, and `/BaseFont` names in the PDF are only `Rubik*` and `Heebo*` |
| D8 | The closing screen leads with the promise, not the phone number | `python3 verify.py --closing` asserts that the largest `font-size` on screen S15 belongs to the return-contact promise element, that the contact block's `font-size` is at or below the body scale, and that the promise precedes the contact block in document order |
| D9 | The work is reproducible and recorded | `python3 build.py && python3 shot.py` regenerates a byte-identical-in-content PDF from a clean checkout; `marketing-assets.md` carries a dated row for every asset used; an evidence file exists per §9 |

Anything not on this list is out of scope unless Tom asks.

### 1.1 Settled — do not reopen

Decided by Tom on 2026-08-25 in the scoping session. Re-litigating these wastes the session:

1. **Four products only:** `FRESH` · `DETOX` · `NAMASTEA` · `MATCHA`.
2. **Twelve drinks, split 3 / 2 / 3 / 4.** `DETOX` gets two because only two `DETOX` drinks carry
   an approved FOOD COST; `MATCHA` gets the fourth slot. Do not invent a third `DETOX` drink.
3. **One PDF file**, containing both the drinks menu and the "what to order" section.
4. **Mobile-native, not A4.** Tom asked for a WhatsApp PDF that is explicitly not A4 and fits a
   phone perfectly: `לווצאפ כPDF אבל לא A4. שיתאים למובייל בצורה מושלמת`.
5. **No wholesale prices.** Tom's ruling was profit per cup only — `לא — רק הרווח לכוס`.
   FOOD COST per cup, recommended
   consumer price, margin % and profit per cup are all shown. Bottle and pack prices are not.
6. **Static.** No interactivity, no per-lead personalisation. The intake form collects only name,
   phone and email (`Sales-Machine/CURRENT_STATE.md`, U-013), so there is nothing to personalise on.
7. **Closing screen leads with "we will get back to you shortly."** This reaches a lead who just
   left their details; the contact block is secondary, lower, smaller.
8. **The Canva catalogs are read-only.** Tom forbade editing either catalog:
   `אסור לך לערוך אף אחד מהקטלוגים`.

---

## 2. Ground truth — measured 2026-08-25; re-verify at boot

### 2.1 The reorganizing fact

**This deliverable has already been built once, and it shipped.**
`B BAGEL × GT — Premium Iced Tea Programme` is a complete, customer-facing GT brochure: 12 pages,
`index.html` plus a 4.5 MB PDF, presenting **exactly four tea concentrates** — `DETOX`, `FRESH`,
`CONSCIOUSNESS`, `NAMASTEA` — one product page and one preparation page each.

- Dropbox: `/Data Center/PRODUCTION 2/B-BAGEL-Tea-Programme/` (ns_path `ns:13945604755//PRODUCTION 2/B-BAGEL-Tea-Programme`)
- Its `README.md` and `index.html` were read in full on 2026-08-25 through the Dropbox MCP `fetch`
  tool, which extracts text and works where `curl` does not. **Read `index.html` yourself at the
  start of W3** — it is the approved source copy for the vision line, the three-move pour, the
  per-product descriptions, the ratio callout and the storage block. Translate it into Hebrew; do
  not invent replacements for language that already shipped to a customer.

So this task is **not** an invention. It is: swap `CONSCIOUSNESS` for `MATCHA`, re-cut A4 to 9:16
mobile, translate to Hebrew, and **add the economics the precedent deliberately withheld** — its
profitability page says *"your most profitable pour"* with no figure on it. That absence is the
gap Tom is closing.

Facts established by that shipped brochure — reuse them, they are approved GT claims:
`20 premium drinks per bottle` · `5:1 ratio — 250ml liquid to 50ml concentrate, concentrate added
last` · `17 kcal / 100ml prepared` · `No preservatives · No artificial colours · No flavour
extracts` · storage: unopened needs no refrigeration, refrigerate after opening, best within
3 months · vision line: *"The better drink, the easy choice, for everyone."*

### 2.2 The approved figures — the only numeric source

`gt-factory-os-production-brain/.claude/skills/drinks-pricelist/drinks_final_figures.json`
(approved by Tom 2026-08-05; 48 drinks; its `_meta` block states the VAT rule).

**The VAT rule, and the way it goes wrong.** FOOD COST is ex-VAT. The recommended price includes
18% VAT. Profit and margin are computed on the ex-VAT revenue: `profit = price/1.18 − cost`,
`margin = profit / (price/1.18)`. Computing margin as `(price − cost)/price` overstates it by 2–5
points on every drink. The `שוליים מוצע` column of `foodcost_proposal.csv` does exactly that and
is kept only for provenance — **never read figures from that column.**

**The twelve drinks.** The key is the drink's page number in the figures file, which is also its
page number in the Canva drinks catalog `DAHPi9gpfts` — read that page for the preparation steps,
the description and the ingredient list.

| key | product | drink | cost | price | margin | profit |
|---|---|---|---|---|---|---|
| `8`  | FRESH | `חליטת היביסקוס וליים` | ₪3.76 | ₪19 | 77% | ₪12.34 |
| `23` | FRESH | `חליטת תפוח היביסקוס` | ₪3.25 | ₪24 | 84% | ₪17.09 |
| `27` | FRESH | `גזוז היביסקוס ותפוח` | ₪3.62 | ₪22 | 81% | ₪15.02 |
| `12` | DETOX | `חליטת תה ירוק וליים` | ₪3.76* | ₪19 | 77% | ₪12.34 |
| `21` | DETOX | `חליטת תות לואיזה` | ₪5.41 | ₪24 | 73% | ₪14.93 |
| `48` | NAMASTEA | `אייס צ'אי מסאלה קלאסי` | ₪5.00 | ₪24 | 75% | ₪15.34 |
| `49` | NAMASTEA | `צ'אי מסאלה על הקרח` | ₪3.80 | ₪24 | 81% | ₪16.54 |
| `55` | NAMASTEA | `צ'אי מסאלה קולד פואם וניל` | ₪3.95 | ₪28 | 83% | ₪19.78 |
| `29` | MATCHA | `אייס מאצ'ה קלאסי` | ₪3.77 | ₪26 | 83% | ₪18.26 |
| `34` | MATCHA | `מאצ'ה אגבה על הקרח` | ₪3.35 | ₪26 | 85% | ₪18.68 |
| `31` | MATCHA | `אייס מאצ'ה תות` | ₪6.17 | ₪26 | 72% | ₪15.86 |
| `33` | MATCHA + NAMASTEA | `אייס מאצ'ה מסאלה` | ₪6.37 | ₪26 | 71% | ₪15.66 |

This table is a **human-readable copy for review, not the source.** `build.py` reads
`drinks_final_figures.json` at build time and asserts that the twelve keys resolve to these
values. On any mismatch it halts with `contract_failure` — it does not "fix" either side.

Derived facts you may state on the page, each recomputed by `build.py` from the table above and
never hardcoded: profit per cup across the twelve spans **₪12.34 to ₪19.78**; margin spans
**71% to 85%**. The asterisk on key `12` means the cost includes a garnish/foam estimate — carry
the asterisk and its footnote, exactly as the catalog does.

**Why the selection is what it is** (so you do not "improve" it): each product gets an anchor the
buyer already understands, a profit hero, and a range-demonstrating variant. `34` at 85% is the
highest margin of all 48. `55` at ₪19.78 is the highest profit in the deck. `33` is the only
drink that consumes **two** of the four products, which is what makes the mapping screen worth
drawing.

### 2.3 Products — what GT actually sells

`gt-factory-os-production-brain/docs/warehouses/catalog-truth.md` is the authority.
SKUs for the four: `GT-HIB-LOW-1L` / `GT-HIB-LOW-0.5L` (FRESH) · `GT-LUI-LOW-1L` /
`GT-LUI-LOW-0.5L` (DETOX) · `GT-MAS-CHA-1L` / `GT-MAS-CHA-0.5L` (NAMASTEA) ·
`GT-SHI-CER-500` and `GT-SHI-CER-18*22` (MATCHA). Strawberry purée, used by keys `21` and `31`,
is `GT-ODK-STR-1`.

Product descriptions and ingredient lists come from the Canva products catalog `DAHQrpThEBE`,
read through the Canva MCP. **`catalog-truth.md` overrides that catalog** wherever they disagree —
see landmine 4.

### 2.4 Assets — verified reachable and verified transparent

The B-Bagel asset set is mirrored in Google Drive with byte-identical sizes, and **Google Drive's
MCP is the only working byte channel in this environment** (landmine 1).

| asset | Drive fileId | verified 2026-08-25 |
|---|---|---|
| `bottle-fresh.png` | `1SAIDMD0E5bxNoo2VYUdqH3CRR5gWCqgE` | downloaded, decoded: RGBA 1792×2400, alpha extrema `(0,255)`, all four corners alpha `0` — **transparent background confirmed** |
| `bottle-detox.png` | `1NDmMB3lKkALdU4HB5uONF811YrOmqF1U` | listed, 1,608,667 bytes — matches the Dropbox original |
| `bottle-namastea.png` | `1RMSYeRUxjBsfp7VW3ahTr1VhW02WyqRE` | listed, 1,810,057 bytes |
| `glass-fresh.jpg` | `1oXrfJhu12qrKRHQEx4_EWjrbAxc2Q6BI` | listed, 11,754,503 bytes — **must be downscaled** |
| `glass-detox.jpg` | `1dWCnUjGgGy4Gyjzuzz7383Ohq1xr6FHk` | listed, 12,164,756 bytes — **must be downscaled** |
| `glass-namastea.jpg` | `1MqrrR-Ypp_78tjmYjQd3iGZhXfUCz_b5` | listed, 11,600,577 bytes — **must be downscaled** |
| `gt-logo-black.png` | `1z-jgnJONNJGTMYmlAtYa6rlA3IfppeNE` | listed, 30,092 bytes |

A prepared glass photograph exists for `FRESH`, `DETOX` and `NAMASTEA`, and **none for `MATCHA`** —
the B-Bagel deck did not include one. Hero screen S12 therefore carries the packshot and typography
instead of a glass shot. Do not borrow another product's glass photo, and do not use stock
imagery (§8).

`bottle-consciousness.png` (`12w2BdkpDgkM_PwCo8wWoQ0EEWPEtBsVh`) exists but **is not used** —
`CONSCIOUSNESS` is not in this deck.

**GT logo, on local disk, no download needed:** `gt-factory-os-portal/public/brand/logo.png`
(56 KB). A black variant is registered in `marketing-assets.md` under the Dropbox path
`Data Center/PRODUCTION 2/B-BAGEL-Tea-Programme/assets/gt-logo-black.png`, mirrored in the same
Drive folder as the bottles.

**The open asset gap: MATCHA.** There is no Tom-approved matcha packshot at the quality of the
three bottles. `marketing-assets.md` registers four matcha images in the Dropbox folder
`AI YASTREBOVA/CATALOG/MATCHA UBE HOJICHA/PRODUCT PHOTOS/`, and that folder holds roughly sixty
files with opaque hashed names. Resolve this through §6.A — do not spend the session guessing.

**Fonts, on local disk:** `gt-factory-os-production-brain/docs/pricing/pricelist_pdf/fonts/` holds
`rubik-400/500/600/700.woff` and `heebo-400/500/700/900.woff`. Load them with `@font-face` and
`file://` URLs. Confirmed on 2026-08-25 to embed correctly into the PDF as `Rubik-Bold` and
`Heebo-Regular`.

### 2.5 The toolchain — rendered and inspected on 2026-08-25

Not inferred. A two-page 1080×1920 test document was built and rendered on this machine:

- Chromium is at `/opt/pw-browsers/chromium-1194/chrome-linux/chrome`.
- `@page { size: 1080px 1920px; margin: 0 }` produced `/MediaBox 810.00 × 1440.00` pt,
  ratio **0.5625** — exactly 9:16.
- `/Count 2` and the strict `/Type /Page` regex both returned **2**. `page-break-after: always`
  on the final screen produced **no** trailing blank page.
- Both local WOFF faces embedded; no network was used.
- `pip3 install Pillow` succeeds — `pypi.org` and `files.pythonhosted.org` are on the proxy's
  `noProxy` allowlist. Pillow 12.3.0 installed and used to verify the alpha channel above.
- There is **no** ImageMagick, no `ffmpeg` on `PATH`, no `pdfinfo`, no `qpdf`, no `gs`,
  no `pdftoppm`. Pillow plus Chromium is the whole toolkit.

Copy the proven pattern from `.claude/skills/drinks-pricelist/`: `build.py` renders data to HTML,
`shot.py` drives Chromium to PDF, `validate.py` proves the figures. `shot.py` already contains the
Chromium path resolution — reuse it rather than rewriting it.

### 2.6 Re-verification block — run this first, before writing anything

```bash
# Regenerates every volatile claim in §2. Run from the production-brain repo root. 2026-08-25 baseline in comments.
python3 - <<'PY'
import json, pathlib
p = pathlib.Path(".claude/skills/drinks-pricelist/drinks_final_figures.json")
d = json.load(p.open())["pages"]
keys = ["8","23","27","12","21","48","49","55","29","34","31","33"]
missing = [k for k in keys if k not in d]
print("figures file present:", p.is_file(), "| drinks in file:", len(d))   # baseline: True | 48
print("missing keys:", missing or "none")                                   # baseline: none
for k in keys:
    v = d[k]
    print(f'  {k:>3}  {v["cost"]:>8}  {v["price"]:>4}  {v["marg"]:>4}  {v["prof"]}')
PY

ls /opt/pw-browsers/chromium-1194/chrome-linux/chrome        # baseline: exists
ls docs/pricing/pricelist_pdf/fonts/ | wc -l                 # baseline: 8
ls ../gt-factory-os-portal/public/brand/logo.png             # baseline: exists
python3 -c "import PIL,sys;print('Pillow',PIL.__version__)" 2>/dev/null || pip3 install --quiet Pillow
```

If the figures file no longer holds all twelve keys, or any figure differs from §2.2 — **halt and
surface to Tom.** Do not adapt: a changed cost means a changed price on a page a café owner will
act on.

---

## 3. What the hard part actually is

Five reframes. Each changes what you do first.

1. **The hard part is not the content — it is the 0.36× collapse.** A 1080px-wide page rendered
   fit-to-width on a ~390px phone shrinks by 0.361×. A 16px caption lands at 5.8 effective pixels
   and is gone. This single arithmetic fact drives the entire type system: content type starts at
   36px and lives mostly at 40–44px; a product name is 110–140px; a hero figure is 150–200px.
   **Design at the phone, not at the desktop.** Every review pass looks at a page rendered to
   390px wide, never at the 1080px source.
2. **This is a re-skin of something that shipped, not a blank page.** §2.1 gives you approved
   copy, an approved structure and approved product claims. Inventing new marketing language when
   approved language exists is how this goes wrong and slow.
3. **The design DNA lives in two catalogs with two different palettes, and neither is wrong.**
   The products catalog `DAHQrpThEBE` is registered in `marketing-assets.md` as the DNA source —
   paper `#EFE6D6`, ink `#241C15`, green `#263B18`, coral `#FA6E4D`, line `#D8CCB4`, muted
   `#7C6E58`. The drinks catalog palette, sampled off live pages and used in an approved PDF, is
   ink `#26221a`, GT green `#123b39`, clay `#a8562f`, sand `#6b6455`, paper `#fbf8f2`
   (`.claude/skills/drinks-pricelist/style.css`, header comment). W1 reconciles these into one
   token set with a cited source per value. Picking one blind, or averaging them, produces a deck
   that belongs to neither catalog.
4. **The mapping screen is the product, not decoration.** Tom asked for a beautiful, minimal map
   of which products make each drink — `מיפוי יפה ומינימליסטי של מאיזה מוצרים מיוצר כל משקה`.
   It is the one screen that turns a price list into an
   argument: four bottles, twelve drinks. Give it the most design effort of any screen.
5. **A deck that shows profit and hides cost is untrustworthy; this one shows both.** FOOD COST,
   recommended price, margin and profit all appear. What is withheld is only what GT charges. Do
   not soften the cost figures to make the profit look better — the honesty is the sales asset.

---

## 4. Workstreams

### W0 — Assets, first, because everything downstream blocks on them

Create the skill directory `gt-factory-os-production-brain/.claude/skills/lead-welcome-menu/`
with an `assets/` subfolder, mirroring `drinks-pricelist/`'s layout.

Fetch each asset in §2.4 through `mcp__Google_Drive__download_file_content`. The base64 payload
exceeds the tool-result token limit and is written to a file instead — that is expected, not an
error (landmine 1). Decode from that file:

```python
import json, base64, pathlib
d = json.loads(pathlib.Path(SAVED_TOOL_RESULT).read_text())
pathlib.Path(OUT).write_bytes(base64.b64decode(d["content"]))
```

Then, with Pillow: confirm each bottle PNG is `RGBA` with corner alpha `0`; downscale every image
so its longest edge is at most 1400px; save PNGs with `optimize=True` and JPEGs at quality 82.
**Budget: the entire `assets/` folder stays under 2.5 MB** so D2 has room. Record every asset you
used as a dated row in `docs/warehouses/marketing-assets.md`, per that warehouse's four-field
contract in `docs/warehouses/README.md`.

**Acceptance:** closes part of D2 and D9.

### W1 — Extract the design DNA into tokens, before drawing anything

**Skill: `brand-guidelines`.** Read both Canva catalogs through `mcp__Canva__read-design` for text,
structure and design grammar — do not open an editing transaction; a plain read is cheaper and
cannot mutate.

**Do not try to sample colours out of Canva.** Its export and thumbnail URLs sit on hosts the
egress proxy denies (landmine 3). The palettes are already extracted and recorded, both dated and
graded, and those two records are your source:

- `docs/warehouses/marketing-assets.md`, row `פלטה` — from the products catalog, graded
  `מאושר-טום` 2026-08-06: paper `#EFE6D6`, ink `#241C15`, green `#263B18`, coral `#FA6E4D`,
  line `#D8CCB4`, muted `#7C6E58`.
- `.claude/skills/drinks-pricelist/style.css`, header comment — from the drinks catalog, sampled
  off live pages and shipped in a Tom-approved PDF: ink `#26221a`, GT green `#123b39`,
  clay `#a8562f`, sand `#6b6455`, paper `#fbf8f2`, rule `#e2dbcc`.

Produce `tokens.css` in which **every value carries a source comment** naming which record it came
from. Reconcile the two deliberately, per reframe 3: the products catalog is the registered DNA and
supplies the base; the drinks catalog supplies accents where the deck needs them. Write the rule
you applied into the comment block so the next rebuild inherits the decision instead of re-taking it.

Also lock: the four product hues used by the mapping screen and the drink blocks. Derive them from
each product's own packaging and liquid colour — `FRESH` ruby, `DETOX` green, `NAMASTEA` amber,
`MATCHA` matcha-green — and validate them as a categorical set with the `dataviz` skill's colour
formula and its runnable validator. They must stay distinguishable at thumbnail size.

**Acceptance:** every colour and type value in the build traces to a source. Closes part of D9.

### W2 — The design journey

This is the section Tom cares most about. Seven movements, in order. Each names the skill that
governs it and what it is for. Do not collapse them; do not run them out of order.

**Movement 1 — Absorb.** *(`brand-guidelines`, completed as W1.)* You cannot design in a house
style you have only been told about. Read the real catalogs, sample the real colours, and notice
the grammar: full-bleed photography with white type over it; `Rubik` for anything emphatic and
`Heebo 300` for the quiet passages; product names set as spaced capitals; a hairline rule doing the
structural work instead of boxes; a small `₪` in coral; RTL body with price columns forced to
`direction: ltr`. That grammar is registered in `marketing-assets.md` under the row `DNA עיצובי`.

**Movement 2 — Commit to a direction.** *(`frontend-design-master`, Phase 1.)* Before any markup,
answer its four questions in writing: what is the purpose and what should the reader feel; which
single aesthetic direction this is, committed fully; **what the one unforgettable thing is** — for
this deck it is the mapping screen; and explicitly what this must **not** look like. Name the
rejections: not a spreadsheet, not a Canva template, not a generic SaaS pricing page, not a
restaurant menu. Write these four answers into the skill's `SKILL.md` so the next rebuild inherits
the direction instead of re-deciding it.

**Movement 3 — Build the system.** *(`ui-ux-pro-max`.)* Convert direction into a system: the type
scale computed from reframe 1's 0.36× collapse, a spacing scale, the vertical rhythm of a
1920px-tall screen, the hierarchy rules for a drink block, and the RTL conventions. Use its UX
guideline set for hierarchy and legibility decisions rather than taste alone. Output is a written
scale — a table of every size, weight and spacing step with its purpose — not prose.

**Movement 4 — Draw the one diagram.** *(`dataviz`, plus `artifact-diagramming` for inline-SVG
craft.)* The mapping screen. It is not a graph: eleven of the twelve drinks belong to exactly one
product, so a link diagram would be eleven parallel lines and one crossing — visual noise
pretending to be information. Draw it as four coloured spines with their drinks hanging beneath,
and let the single hairline that connects `אייס מאצ'ה מסאלה` to a second spine be the one
deliberate exception. Because it is the only crossing on the page, it reads as intent. Hand-author
the SVG; do not reach for a chart library.

**Movement 5 — Execute.** *(`impeccable`.)* Run its one-time per-session setup first —
`node <skill-base-dir>/scripts/context.mjs`, where `<skill-base-dir>` is the base directory the
runtime reports when the skill loads. Then build. Follow its bounded-verification
discipline exactly: build the deck **fully**, inspect once in a single batched round, fix
everything that round surfaced in one batch, confirm with at most one more round, then stop.
Open-ended self-QA is explicitly against that skill's rules and burns the session. Render each
screen to PNG with Chromium and inspect the PNGs — never judge the deck from the HTML source.

**Movement 6 — Audit against a standard you did not set.** *(`apple-design`.)* A read-only
Human-Interface-Guidelines review of the rendered screens at true phone scale: legibility,
contrast ratios, visual hierarchy, information density, whether the eye lands where the argument
needs it to. It produces findings, not edits. Apply them in one batch. This is the movement that
catches what your own eye stopped seeing three hours ago.

**Movement 7 — Prove.** *(`verification-before-completion`.)* Run every D-condition command in §1
and paste the real output. Evidence before assertions, always. A claim of "done" without the
command output is not a claim, and `gt-factory-os-production-brain/CLAUDE.md` §Evidence governs.

Two supporting skills to invoke where they fit: **`writing-skills`** when you author the skill's
`SKILL.md`, so the package is re-runnable next season rather than a one-off; and
**`drinks-pricelist`**, whose `build.py` / `shot.py` / `validate.py` trio is the working pattern
this build copies rather than reinvents.

**Acceptance:** D4, D7, D8.

### W3 — The 15 screens

Structure fixed by Tom, 2026-08-25. Screen order is the argument; do not reorder it.

| # | Screen | Carries |
|---|---|---|
| S01 | Cover | GT logo · the deck's title · the four products in one line |
| S02 | The promise | `4 מוצרים → 12 משקאות` · profit-per-cup range `₪12.34–₪19.78` · `20–25 כוסות מכל בקבוק` |
| S03 | **The mapping** | Movement 4's diagram. The screen the deck is built around |
| S04 | How it is made | The three-move pour · the `5:1` ratio · storage |
| S05 | FRESH | The product, its ingredients, its three drinks with cost / price / margin / profit and a one-line preparation each |
| S06 | FRESH hero | `חליטת תפוח היביסקוס` full-bleed, numbered preparation steps, the figures large |
| S07 | DETOX | The product and its two drinks |
| S08 | DETOX hero | `חליטת תות לואיזה` |
| S09 | NAMASTEA | The product and its three drinks |
| S10 | NAMASTEA hero | `צ'אי מסאלה קולד פואם וניל` — the ₪19.78 drink |
| S11 | MATCHA | The product and its four drinks |
| S12 | MATCHA hero | `מאצ'ה אגבה על הקרח` — the 85% drink |
| S13 | What to order from GT | The four products plus strawberry purée. Names and roles. **No prices** |
| S14 | What you already have | The non-GT ingredients the twelve drinks need. **Derive this list**: read the ingredient panel on each of the twelve catalog pages in §2.2 and take the union of everything that is not a GT product. The 2026-08-25 reconnaissance produced milk, cream, apple juice, soda, agave syrup, lemon, mint, cinnamon and vanilla — reproduce the derivation and reconcile against that |
| S15 | Closing | **Leads with the promise that GT will get back to them shortly.** Contact details below it, secondary, at body scale or smaller |

The alternation is deliberate: a dense product screen, then a hero that breathes. Hold it.

Preparation steps, descriptions and garnishes for each drink come from that drink's page in Canva
`DAHPi9gpfts`, at the page number given by its key in §2.2. Product ingredient lists come from
`DAHQrpThEBE`, subject to `catalog-truth.md`.

Place the GT logo where a brand mark earns its place and nowhere else: the cover, and the closing
screen. A logo repeated on all fifteen screens reads as insecurity; a running footer carrying the
deck's name and screen number does that job better.

**Acceptance:** D1, D5, D6, D8.

### W4 — Verification scripts

Author `validate.py` and `verify.py` implementing exactly the observations in §1's right-hand
column. They must be able to **fail** — write a deliberately wrong value into a scratch copy, watch
the validator reject it, then revert. A validator never run against a failing input is untested.

**Acceptance:** D3, D4, D5, D6, D7.

### W5 — Package, record, ship

`SKILL.md` written per `writing-skills`, carrying Movement 2's four answers and the rebuild
command. Then: a dated evidence file in `Sales-Machine/evidence/2026-08-25-lead-welcome-menu.md`
recording files changed, checks run N/N, sources cited, authority grades, and what remains Tom's.
`Sales-Machine` receives **only** that evidence record — its constitution forbids runtime code in
that repo, and `build.py` is runtime code. Commit to `claude/gt-initial-menu-lead-9cw4zp`, open a
draft PR, and deliver the PDF to Tom with `SendUserFile`.

**Acceptance:** D9.

---

## 5. Scope

**IN:** everything in §4.

**OUT — do not touch, do not "improve":**

- **Any Canva design.** Read and export only. Never `edit-design`, never open a transaction on
  `DAHPi9gpfts` or `DAHQrpThEBE`. Tom's explicit instruction.
- **Sending anything to any lead or customer.** See §8.
- **`Sales-Machine/` beyond one evidence file.** No code, no build scripts, ever.
- **factory-os core** — `stock_ledger`, `balance_anchors`, `bom_*`, `items`, `components`.
  Not read directly, not written.
- **The other 36 drinks and the other seven products.** They are the database this deck selects
  from. Adding "just one more" is the exact failure Tom is buying this deck to avoid.
- **The drinks-pricelist skill.** Copy its patterns; do not edit it.
- **Recomputing, adjusting or "correcting" any FOOD COST, price, margin or profit.**

---

## 6. Tom's part — the complete list; nothing else is his

**A. Choose the MATCHA image.** No approved matcha packshot exists at bottle quality (§2.4).
Present him a small contact sheet — no more than six candidates from
`AI YASTREBOVA/CATALOG/MATCHA UBE HOJICHA/PRODUCT PHOTOS/`, rendered as thumbnails — and let him
pick one. Two minutes of his time. Record the choice in `marketing-assets.md` the same day, per
that warehouse's maintenance rule 1. **Do not block W1–W4 on this**; build with a typographic
placeholder for screen S11 and drop the image in when it arrives.

**B. Resolve the NAMASTEA ingredient conflict.** The products catalog lists two black teas,
cinnamon, cardamom, ginger, black pepper and clove. The shipped B-Bagel brochure adds Pu-erh and
star anise. Default to the products catalog, which is newer, and ask him to confirm in one line.

**C. Supply the contact block for screen S15.** The B-Bagel brochure shipped with the literal
placeholder `GT · contact details to add`, so there is no approved contact block to inherit. The
products catalog `DAHQrpThEBE` carries a site, a phone and an email in its closing footer — read
them from there and have Tom confirm they are the right channel for an inbound lead. Do not assume
the catalog footer is current.

**D. Approve the finished PDF** before it reaches any lead.

**E. Later, and only if he asks for automated sending:** written approval to flip
`SALES_CUSTOMER_OUTREACH_WRITE_ENABLED`. Out of scope for this session. See §8.

---

## 7. Landmines — do not rediscover these

1. **`curl` cannot reach Dropbox, Canva, Google Fonts, or any CDN.** Symptom:
   `curl: (56) CONNECT tunnel failed, response 403`. Real cause: outbound HTTPS goes through a
   policy-enforcing egress proxy whose allowlist covers only package registries and Anthropic
   endpoints (`/root/.ccr/README.md`; confirmed against `http://127.0.0.1:33991/__agentproxy/status`
   on 2026-08-25). Resolution: fetch bytes through the **Google Drive MCP**, which returns base64
   and routes via the allowed MCP proxy. Its result exceeds the tool-result token cap and is
   written to a file — decode from that file, as in W0. Never disable TLS verification, never
   unset `HTTPS_PROXY`, and do not retry a 403 — it is a policy denial, not a transient failure.
2. **Google Fonts will silently ruin the PDF.** A `<link>` to `fonts.googleapis.com` fails behind
   the proxy, Chromium falls back to a default face, and Hebrew renders in something that is not
   `Rubik` — often without an error. Use `@font-face` with `file://` URLs to the repo WOFFs.
   D7 exists to catch this.
3. **Canva is readable but not downloadable.** `mcp__Canva__read-design` returns text and
   structure through the allowed MCP proxy and works. `mcp__Canva__export-design` returns a URL on
   a Canva host the egress proxy denies, so the exported file cannot be fetched — and it also
   requires a prior `get-export-formats` call, so a direct attempt fails twice over. Take text and
   structure from Canva; take colours from the registered records named in W1; take pixels from
   Google Drive.
4. **The Canva products catalog is stale, and it looks authoritative.** It still lists
   `GT Elita מאצ'ה פחית 30 גרם`, `מאצ'ה שיזואוקה 50 גרם`, `מקציף קוקטיילים` and
   `קנקן נפוליטן עם מסננת`. `catalog-truth.md` records all four as Tom-confirmed negative records
   dated 2026-08-06: not sold. Copying the catalog's product list offers a lead products GT will
   not ship. **The warehouse beats the catalog.** D6 exists to catch this.
5. **`foodcost_proposal.csv` has a column that is wrong on purpose.** `שוליים מוצע` computes
   margin against a VAT-inclusive price using an ex-VAT cost, overstating every drink by 2–5
   points. It is retained only for provenance. Read figures from
   `drinks_final_figures.json`, never from that CSV.
6. **Type that looks generous at 1080px is unreadable at 390px.** The 0.36× collapse in reframe 1.
   Judge every screen from a PNG rendered at phone width. This is the defect most likely to survive
   to Tom's phone, because it is invisible at authoring scale.
7. **The glass photos are enormous** — §2.4 records `glass-namastea.jpg` at 11,600,577 bytes and
   `glass-detox.jpg` at 12,164,756 bytes. Either one alone blows D2. The shipped B-Bagel
   PDF solved this by downscaling 12 MB to about 65 KB with no visible loss, and it still landed at
   4.5 MB. Downscale in W0, before the first build, not as a rescue at the end.
8. **There is no ImageMagick and no Pillow preinstalled.** `pip3 install Pillow` succeeds because
   PyPI is on the proxy allowlist. Install it in W0's first step rather than discovering it missing
   mid-build. There is also no `pdfinfo`, `qpdf` or `gs` — inspect the PDF by regex over its bytes,
   using the `/MediaBox` and strict `/Type /Page` patterns from §2.6.
9. **`b.count(b'/Type /Page')` over-counts by one.** It matches the `/Pages` tree node too. Use
   `re.findall(rb'/Type\s*/Page(?![s])', b)`, which returned exactly `2` on the two-page test.
10. **`DETOX` genuinely has only two costed drinks.** Confirmed by bucketing all 48 approved
   drinks by the GT product each requires. Finding "only two" is not a search failure and is not
   fixed by looking harder — it is settled decision 1.1.2.
11. **RTL Hebrew with LTR numbers will mis-order without help.** Price and figure spans need
    `direction: ltr; unicode-bidi: isolate`, exactly as `drinks-pricelist/style.css` does for its
    `.latin` class. A `₪12.34` that renders as `12.34₪` or reorders its digits ships a wrong number.
12. **A hero screen that leads with a phone number reads as a cold sales flyer.** Screen S15's
    largest element is the promise that GT will come back to the lead. Tom was explicit. D8.

---

## 8. Halt conditions

Inherited in full from `gt-factory-os-production-brain/CLAUDE.md` §Stop conditions and
`Sales-Machine/CLAUDE.md` §Stop conditions. Additions specific to this work:

- **Any move toward sending this to a lead or customer** — an email, a WhatsApp message, a Make
  scenario, a Klaviyo flow, a webhook. `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` is `false`
  (`Sales-Machine/CURRENT_STATE.md`). Building the PDF is permitted; delivering it to a lead is a
  customer-facing write. → **STOP**, surface to Tom.
- **Any figure in `drinks_final_figures.json` that differs from §2.2.** → **STOP**. Do not adapt,
  do not recompute. A changed cost is a business decision.
- **Any impulse to write a FOOD COST, price, margin or profit that is not in the approved file** —
  including for a drink you think obviously costs the same as another. `Sales-Machine/CLAUDE.md`
  truth rule 1: inferred is never policy. → **STOP**, ask Tom.
- **Any Canva write.** If you find yourself opening an editing transaction, stop — that means you
  have mistaken the DNA source for a deliverable.
- **A missing or unusable asset** that would tempt you to substitute a generic stock image. GT
  ships its own photography or none. → **STOP**, ask Tom.

---

## 9. Final report

1. What a stranger can now watch working, end to end.
2. Each of D1–D9 marked ✅ or ❌ **with the command output that proves it**. No partial credit.
3. The numbers: page count, MediaBox ratio, file size in bytes, `validate.py` deviation count,
   minimum content font-size, asset-folder size.
4. The artifacts and where they are: the PDF's path, the skill directory, the PR link, the
   evidence file, the rows added to `marketing-assets.md`.
5. What is still Tom's, from §6, and what remains genuinely unfinished.
6. The single next action.

Use the handoff shape in `gt-factory-os-production-brain/AGENT_TEMPLATE.md` §Output format, with
verdict tokens matching `VERDICT_GLOSSARY.md`. If anything is not ready, say so first and plainly.

**Last act of the executing session:** change this file's `STATUS` line to
`SHIPPED — <evidence path>`, and commit that change. A spent masterprompt that still reads `LIVE`
gets re-executed by the next person who finds it.
