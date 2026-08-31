# Content kits — the three category kits, exported and held

> **Date:** 2026-08-31 · **Branch:** `claude/caveman-mode-phzjqa`
> **Covers:** setup-artifact tasks **3.1** (recipes per category) and **3.4** (media library).
> **Status: EXPORTED — HELD. Do not send these files to a lead until §3 is decided.**

---

## 1. What was done

The artifact's task 3.1 asks for three recipes per category, exported as single pages. It
reads as a design job. It is not: **the pages already exist.** GT's opening-menu deck
(Canva `DAHTY5nfDxo`, *"תפריט פתיחה מומלץ חדש"*, updated 2026-08-30) carries all twelve
drinks, one per page, each with its preparation steps and its recipe.

So this was an export, and it is done. Twelve PNGs, `1080×1920`, **0.76–0.93 MB each** —
comfortably inside WhatsApp's 5 MB image limit, with no compression needed.

## 2. The kits

| Kit | Pages | Drinks |
|---|---|---|
| **tea** | 3–7 | חליטת היביסקוס וליים · משקה תפוח היביסקוס · גזוז היביסקוס ותפוח · חליטת תה ירוק לואיזה וליים · משקה תות לואיזה |
| **chai** | 8–10 | אייס צ'אי מסאלה קלאסי · צ'אי מסאלה קולד פואם וניל · צ'אי מסאלה על הקרח |
| **powder** | 11–14 | אייס מאצ'ה קלאסי · אייס מאצ'ה תות · אייס מאצ'ה מסאלה · מאצ'ה אגבה על הקרח |

Page mapping verified by reading pages 2, 3, 7, 8, 10, 11, 14 and 15 back from Canva
before exporting — pages 1–2 are the cover and intro, 15–19 are the ingredient pages and
20 is the contact page. A wrong page range would have produced kits with the wrong drinks
in them, silently.

`tea` carries five drinks rather than three, because FRESH and DETOX are two concentrates
inside one category. That is a better kit, not a deviation worth correcting.

## 3. **Why they are held — and this is Tom's call**

**Every drink page prints `FOOD COST` in its bottom strip**, beside the margin percentage.
The `ice massala classic` page reads `₪5.57 FOOD COST ללא מע"מ` next to `77% רווח`.

That is in direct conflict with a decision Tom made **the same day**:

> **D-013** — *neither the price of the opening menu nor the food cost per drink is ever
> stated by the system.* Both are transfer rows. "זה פיתוי של סקרנות הלקוח כי זה הכי מעניין
> ולכן דווקא את שניהם אנחנו לא אומרים."

These kits are the system's customer-facing asset. Sending them sends the food cost.

**Three ways out, and the choice is Tom's, not a build decision:**

1. **Remove the `FOOD COST` block from the twelve pages** and re-export. The margin
   percentage can stay — it is the selling argument — though note `U-021`: margin plus
   consumer price implies the cost arithmetically (₪20 at 81 % is ₪3.80), so keeping the
   margin keeps a weaker version of the same leak.
2. **Keep the deck as it is** and treat D-013 as applying to the *conversation* rather
   than to the *catalogue* — a defensible position, but it should be said out loud and
   written down, because the answer bank currently refuses to state a number the kit
   hands over on a plate.
3. **Two versions:** the full deck for a live sales conversation, a cost-free set for
   automated sends. More assets to keep in sync — the version file below exists exactly
   because that goes wrong.

**Until one is chosen, the files stay where they are and go to nobody.** This is the
masterprompt's own halt condition: *a template or automated answer would state a price
that is not an approved row → STOP.*

## 4. Still open on the kits

- **Aspect ratio.** The deck is `9:16`; the artifact asks for `1:1` or `4:5`. 9:16 sends
  fine as a WhatsApp image but the in-chat preview crops it. Re-framing changes Tom's
  layout, so it was **not** done unilaterally — a marketing call.
- **3.2 — the videos.** Not started. 15–30 s, ≤16 MB.
- **3.4 — the media library.** Blocked until the lead number is in the API: `media_id`s
  are per-WABA, so they cannot be minted before the number exists. Send by `media_id`,
  never by URL — a URL send is slower and depends on Dropbox link permissions that change
  silently.
- **Dropbox (3.3).** The folder structure was **not** created. The available Dropbox tool
  writes text files only and cannot upload a PNG, so creating the tree would have produced
  an empty scaffold and a false claim of "assets uploaded".

## 5. The version file

Ships beside the assets so nobody sends an old kit — artifact task 3.3. Kept as data here
so the record survives whatever storage is chosen.

```
kit_version: 2026-08-31
source: Canva DAHTY5nfDxo "תפריט פתיחה מומלץ חדש" (deck updated 2026-08-30)
export: PNG 1080x1920, regular quality, 12 files, 0.76-0.93 MB each
status: HELD — FOOD COST visible on every page, conflicts with D-013
tea:    01_fresh_hibiscus_lime · 02_fresh_apple_hibiscus · 03_fresh_apple_soda
        04_detox_green_verbena_lime · 05_detox_strawberry
chai:   01_namastea_ice_masala_classic · 02_namastea_cold_foam_vanilla
        03_namastea_on_the_rocks
powder: 01_matcha_ice_classic · 02_matcha_strawberry · 03_matcha_masala · 04_matcha_agave
```

## 6. Where the category mapping lives

Not in this file, and not in a spreadsheet: **`sales_core.campaign_map`** (migration
`0340`) maps an ad's `source_id` to one of `tea` / `chai` / `powder`, and
`sales_core.lead_event` type **`kit_sent`** records which kit went to which lead and when
(migration `0340`). The moment a kit is cleared to send, both halves of D6 already exist.

---

## Evidence

- **Files produced:** 12 PNGs, exported from Canva `DAHTY5nfDxo` on 2026-08-31, sizes
  verified individually (all between 764,339 and 934,208 bytes).
- **Verified visually:** `chai/01_namastea_ice_masala_classic.png` opened and read — the
  correct drink, correct recipe, and the `FOOD COST ₪5.57` strip that puts the whole set
  on hold.
- **Not done, and why:** Dropbox tree (tool cannot upload binaries), media library (needs
  the WABA), videos (not started), re-framing to 4:5 (Tom's layout, not mine to change).
- **Stop condition tripped:** yes — §3. Held for Tom rather than shipped.
