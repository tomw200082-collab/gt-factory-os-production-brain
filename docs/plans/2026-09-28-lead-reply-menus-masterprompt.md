# MASTERPROMPT — Five lead-reply menus in Canva that agree with GT's approved figures and with themselves, plus five first messages for Tom to approve

**STATUS: LIVE — not yet executed**
<!-- The executing session's last act is to change this line to SHIPPED / SUPERSEDED by <path> /
ABANDONED — why, with evidence pointers (checker output per copy, the report, the messages file). -->

> **Usage:** paste this entire file as the first message of a fresh Claude Code session. Attach
> `gt-factory-os-production-brain` and connect Canva. Do this only after Tom allowed the Canva tools
> (§6-A).
>
> **What it does:** takes five Canva menu copies from "trimmed, partly edited" to "every page
> verified", and writes five message drafts.
>
> **Where it stops:** it halts for Tom only where §6 says so.
>
> **Provenance:** written 2026-09-28 by the session that made the copies. Sources:
> - live Canva `read-design` calls on the source and copy designs, made the same day;
> - the approved figures file `.claude/skills/drinks-pricelist/drinks_final_figures.json` (dated 2026-08-27 inside);
> - the cost model `docs/pricing/2026-08-27_cost_model.py`;
> - Sales-Machine `doctrine/decisions.md`;
> - Tom's messages of 2026-09-27 and 2026-09-28, quoted in §1.1.
>
> **Authority, highest first:**
> 1. brain `CLAUDE.md`;
> 2. Sales-Machine `CLAUDE.md` and `doctrine/decisions.md`;
> 3. the figures file;
> 4. this document.
>
> **Shelf life:** §2 is presumed wrong if you paste this after 2026-10-12. Run §2.5 first. When a
> copy's state differs from §2, adapt. §4 states what each page must end as, so apply only what is
> missing, and never an edit twice.

## 0. How to work

- **Who you are here:** one Claude Code session.
  - **You hold:**
    - the Canva connector, which is Tom's account;
    - git on the brain repo, on the branch your session instructions name.
  - **You decide alone:**
    - which element to edit to reach the end state in §4;
    - the font size and line spacing of a list page;
    - the wording of the message drafts, which are proposals.
  - **Not yours:**
    - any drink figure, recipe or product page;
    - which drinks each menu keeps (§1.1);
    - sending anything to anyone.
- **Read first:**
  - brain `.claude/skills/drinks-pricelist/SKILL.md`, the whole file. Its "Editing the catalog"
    section and its LEARNED log are the Canva editing rules; they are cited here, not copied.
  - Then this document.
- **Halt conditions, evidence standard, git discipline:** inherited from brain `CLAUDE.md` (§Stop
  conditions, §Evidence, §Watching) and gt-factory-os `CLAUDE.md` (§⊥ do).
  - Additions specific to this work are in §8.
  - Watching is opt-in. After opening a PR, call `unsubscribe_pr_activity`.
- **The standard,** in Tom's words (2026-09-28): `בצורה אמינה ונכונה ובטוחה` and
  `תבדוק הכל ממש ממש ממש לעומק תוודא שזה טוב באמת`. As prohibitions you can check:
  - no figure on any page disagrees with the figures file;
  - no name or price on a list page differs from its drink page;
  - no stale label and no wrong count survives (`278`, `gt Uba · 60`);
  - every page was looked at as a picture, not only read as text.
- **Language:** this document is in English because that is the register the executor reasons best
  in. Data stays in its own script, in backticks, and is never translated.
- **Output language:**
  - To Tom: Hebrew, short and plain, ending with at most one action (his standing preference).
  - Commits, PRs and docs: concise English.

## 1. Mission and definition of done

**One testable sentence:**
- Each of the five lead-reply copies holds at most eight drinks.
- Every figure and name in it agrees with the figures file and with its own list page.
- Tom has five message drafts to approve.

| # | Condition | The observation that would prove it false |
|---|---|---|
| D1 | Drink pages per copy: opening 8, matcha 8, ube 5, chai 8, tea 8 | `check_menu.py <read> --expect-drinks N` prints `drink pages, expected` |
| D2 | Each list page names exactly the copy's drink-page titles, each with the price on its page | `check_menu.py` prints `list page lacks` or `list page names ... which no drink page shows` |
| D3 | No footer catalog label is left anywhere | `check_menu.py` prints `catalog label left` |
| D4 | Every drink page's cost, recommended price and margin equal the figures file | `check_menu.py` prints `!= figures` |
| D5 | Every WhatsApp link goes to the lead line `972547588132`, and the contact page shows `0547588132` | `check_menu.py` prints `not the lead line`, or the contact page's text still reads `0543982444` |
| D6 | Every recipe header's name equals its page title | `check_menu.py` prints `header ... != title` |
| D7 | Every page of every copy was viewed as a thumbnail and has a verdict in the report | a page number missing from the report's per-page table (80 pages in all on 2026-09-28: 17 + 14 + 11 + 12 + 26, the copies' counts in §2.2) |
| D8 | The five sources are untouched | a source's `page_count` or `updated_at` differs from §2.1 |
| D9 | Five message drafts exist in `docs/plans/2026-09-28-lead-reply-messages.md`, each within W3's bans | a draft with a dash used as punctuation, a niqqud mark, a digit, a price, an emoji, or more than 60 words |
| D10 | This file's status line reads SHIPPED, with evidence pointers | it still reads LIVE |

`check_menu.py` is `.claude/skills/drinks-pricelist/check_menu.py`. It exits 0 only when a design
passes D1 to D6. Its input is a structured read saved to a file (§2.5).

Anything not on this list is out of scope unless Tom asks.

### 1.1 Settled — do not reopen

- **Tom, 2026-09-28, in writing:**
  - **The drink cap.** A menu sent to a lead holds at most eight drinks, and its list page names
    exactly those drinks: `להוריד את מספר המשקעות כך שלא יהיו יותר משמונה משקעות בכל תפריט כי זה מבלבל`
    (his transcription; `משקעות` is `משקאות`).
  - **The menus change only in drink count and consistency.** The "there is much more, the call will
    cover it" line goes in the message:
    `את זה בוא נעשה בהודעה כרגע ולא נשנה את התפריט כלומר את התפריטים אנחנו משנים רק את כמות המשקאות`.
  - **FOOD COST stays on every drink page:** `תשאיר את הפוד קוסט.` This settles the hold in
    `docs/plans/2026-08-31-lead-content-kits.md` §3 as its option 2.
  - **The fifth line.** On the site it now reads `בניית תפריט משקאות עשיר ורווחי לעסק` (gt-site #29).
    It gets the recommended opening menu with a short note that GT recommends this menu to start
    working together:
    `כאשר אדם בוחר- ״בניית תפריט משקאות עשיר ורווחי לעסק״- הוא קודם כל מקבל את תפריט המומלץ להתחלה שלנו`.
  - **The opening menu gets a thorough pass:**
    `מבחינת התפריט ההתחלתי כנראה שצריך לעשות שם עוד שיפורים לפני שאנחנו מעלים אותו`.
  - **Per type.** The menu a customer gets matches the line they picked, to keep them focused.
    This was Tom's correction of 2026-09-27, recorded in
    `docs/plans/2026-09-27-brand-site-lead-modal-masterprompt.md` §1.1.
- **The authoring session's decisions** (Tom was told and did not object):
  - **Copies only.** Every change lands on the copies in §2.2. The sources stay as they are.
  - **The contact page's WhatsApp goes to the lead line.** It changes to `054-758-8132`
    (Sales-Machine D-019: the single destination for inbound enquiries). The menu goes out from that
    line, so a reader who taps the number stays in the same chat instead of landing on the order line
    `054-398-2444`.
  - **The drinks each menu keeps.** The rule: the base drink, one of each style (milk, water,
    carbonated, foam, fruit), each concentrate's drink where the menu shows the concentrate, and no
    drink whose recipe is known to be wrong:
    - **opening:** `חליטת היביסקוס וליים`, `גזוז היביסקוס ותפוח`, `חליטת תה ירוק לואיזה וליים`, `חליטת תות לואיזה`, `אייס צ'אי מסאלה קלאסי`, `צ'אי מסאלה קולד פואם וניל`, `אייס מאצ'ה קלאסי`, `אייס מאצ'ה תות`;
    - **matcha:** `אייס מאצ'ה קלאסי`, `אייס מאצ'ה מנגו`, `אייס מאצ'ה תות`, `אייס מאצ'ה מסאלה`, `מאצ'ה אגבה על הקרח`, `אייס מאצ'ה קפה`, `מאצ'ה קוקוס אגבה`, `מאצ'ה קוקוס תות`;
    - **ube:** all five;
    - **chai:** `אייס צ'אי מסאלה קלאסי`, `צ'אי מסאלה על הקרח`, `דירטי צ'אי`, `צ'אי מסאלה תפוז וטוניק`, `צ'אי מסאלה קולד פואם וניל`, `צ'אי מסאלה קולד פואם פיסטוק`, `צ'אי תאילנדי קוקוס קולד פואם`, `לימונדת צ'אי מסאלה`;
    - **tea:** `חליטת היביסקוס וליים`, `חליטת קמומיל ותפוח`, `חליטת תה ירוק ולמון גראס`, `לימונדת היביסקוס וליים`, `חליטת תות לואיזה`, `חליטת מנגו סנצ'ה`, `גזוז יסמין וליצ'י`, `גזוז מדברי ואפרסק`.
  - **The copies are fixed.** Do not rebuild them from their sources, and do not change which pages
    they hold.

## 2. Ground truth — measured 2026-09-28; re-verify at boot

### 2.1 The sources (must stay untouched)

| Menu | Design | Title | Pages | `updated_at` |
|---|---|---|---|---|
| Opening | `DAHTY5nfDxo` | ` Recommended initial menu` | 21 | 1788426486 |
| Matcha | `DAHT3nDxyfQ` | `Matcha Menu` | 22 | 1788426486 |
| Ube | `DAHT3kQ65Os` | `Ube Menu 2026 — GT Summer 2026` | 11 | 1788341280 |
| Chai | `DAHWHi9oVHU` | `עותק של Chai Massala Menu` | 15 | 1790259527 |
| Tea | `DAHT3nRsXkM` | `Tea Concentrates Menu` | 34 | 1788426486 |

These rows are from `search-designs` and `read-design` metadata, 2026-09-28.

**Deliberately not used:**
- `DAHTZuvZQH0` `Ube Menu`. Its figures predate the 2026-08-27 cost model: `₪4.73` and `81%`, where
  the figures file says `₪5.22` and `79%`. Its list page also names a drink it does not have.
- `DAHT3lMq1ls`, the second `Matcha Menu`. It runs in reverse order and has no list or contact page.

### 2.2 The copies

| Menu | Copy | Pages | State, 2026-09-28 |
|---|---|---|---|
| Opening | `DAHWddnBsTw` | 17 | Every W1 edit committed. Needs only verification |
| Matcha | `DAHWdenOx_0` | 14 | **Nothing committed.** A plain read that day still showed `278` and the labels. A second editing session died before its commit |
| Ube | `DAHWdbNM5Zg` | 11 | **Unknown.** An agent was editing it when the work was stopped |
| Chai | `DAHWda7NUQU` | 12 | **Unknown**, the same way |
| Tea | `DAHWdRTzG1Q` | 26 | **Unknown**, the same way |

### 2.3 Page maps (page order copied from the sources, 2026-09-28)

- **Opening `DAHWddnBsTw`:**
  - p1 cover; p2 intro;
  - p3–p10 drinks, in the §1.1 order;
  - p11 `DETOX`, p12 `FRESH`, p13 `NAMASTEA`, p14 `MATCHA`, p15 `SMOOTHIE`;
  - p16 list; p17 contact.
- **Matcha `DAHWdenOx_0`:**
  - p1 cover;
  - p2 `MATCHA` and p3 `SMOOTHIE`, both 794×1123 by design;
  - p4–p11 drinks, in the §1.1 order;
  - p12 accessories (`מוצרים משלימים להכנת המשקאות`, 794×1123);
  - p13 list, in two columns; p14 contact.
- **Ube `DAHWdbNM5Zg`:**
  - p1 cover; p2 title page; p3 `UBE`; p4 `SMOOTHIE`;
  - p5–p9 drinks (`תות`, `מנגו`, `אפרסק`, `מסאלה`, `מאצ'ה`);
  - p10 list, already correct at copy time; p11 contact.
- **Chai `DAHWda7NUQU`:**
  - p1 cover; p2 `NAMASTEA`;
  - p3–p10 drinks, in the §1.1 order;
  - p11 list; p12 contact.
- **Tea `DAHWdRTzG1Q`:**
  - p1–p16 cover, range and product pages. Many are 794×1123 by design; leave them all as they are;
  - p17–p24 drinks, in the §1.1 order;
  - p25 list; p26 contact.

### 2.4 Known-broken, adjacent, out of scope

Report these; do not fix them.

- **Matcha vanilla.** The recipe on the source's vanilla page (`אייס מאצ'ה וניל`) is the agave recipe
  word for word. The drink is not in the copy.
- **Matcha masala.** The page says `הוסיפו 50 מ״ל תמצית חליטת namastea`, and the cost model uses
  40 ml (`docs/pricing/2026-08-27_cost_model.py`, the `אייס מאצ'ה מסאלה` line). One of the two is
  wrong, and that is Tom's call.
- **Mixed page sizes** in the matcha and tea menus come from the sources: `read-design` page metadata on 2026-09-28 gives 794×1123 for their product pages and 1080×1920 for the rest.
- **The automatic reply itself is the next build:** exporting the PDFs, the WhatsApp API on the lead
  line and the send. It sits behind `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` (Sales-Machine D-005),
  with a dry run and a 24-hour soak.

### 2.5 Re-verification block

For each copy, make a structured read inside a transaction, save it, check it, and cancel the
transaction:

```text
# per copy (ids in §2.2); one copy at a time, never two in parallel (§7.1)
read-design  design_id=<copy>  open_transaction=true  filter={"fields":["design_content"]}
  -> too large to return, so the connector saves it to a file; note the path
python3 .claude/skills/drinks-pricelist/check_menu.py <saved file> --expect-drinks <8 or 5>
edit-design  transaction_id=<id>  finalize="cancel"
# sources: read-design design_id=<source> filter={"fields":["design_metadata"]} -> compare §2.1
```

The pre-edit matcha read gave this on 2026-09-28 (the saved read held pages 2, 4–11, 13 and 14):

```text
# 2026-09-28 · check_menu.py on the pre-edit matcha read, --expect-drinks 8
11 pages read · 8 drink pages · 16 list lines
  ...8 × catalog label left, 1 × header != title, 1 × not the lead line, 8 × list page names ...
18 finding(s)
```

The expected first result:
- **opening:** clean;
- **matcha:** the 18 findings of 2026-09-28 above, all of them planned in W1.
- **ube, chai and tea:** whatever the stopped agents left.

## 3. What the hard part actually is

- **This is a reconciliation job, not a trimming job.** Deleting pages took one call per menu. The
  work is that the pages disagreed with each other and with the approved figures:
  - an Ube menu with stale margins;
  - list pages naming drinks the menu does not hold;
  - a recipe copied from another drink;
  - catalog page numbers on pages that are no longer in a catalog;
  - a cups claim (`278`) that the recipe dose does not support.
  Every edit must end with the checker clean *and* the page looked at.
- **The Canva connector is transactional and fragile.** Two editing sessions died mid-work on
  2026-09-28 and took every uncommitted page with them (§7.1). Work one design at a time, and commit
  every two or three pages.
- **The messages must not read as machine-written.** Tom named it:
  `שלא ירגיש שזה AI כתב את זה- ללא מקפים מיותרים, ללא ניקוד מיותר- פשוט ולעניין`. A fluent,
  enthusiastic, dash-rich draft is the failure, not a success.

## 4. Workstreams

### W1 — Bring each copy to its end state

Work in this order: matcha, ube, chai, tea, then verify the opening menu. For each copy, run §2.5
first, then apply only what the checker and the list below say is missing, then commit, then run §2.5
again.

**Every copy (drink pages):**
- Delete each footer text element whose whole text matches `^gt [A-Za-z ]+ · \d+\s*$`.
- Keep `· Summer 2026` and every figure.

**Every copy (contact page):**
1. Apply `find_and_replace_text` on the number element: `0543982444` becomes `0547588132`.
2. Apply `format_text` with a link equal to the current link, with `972543982444` replaced by
   `972547588132`. The `?text=` part stays byte for byte.

**Every copy (list page):**
- The list names exactly the drink-page titles, in page order, as `<title> ..... ₪<price>`.
- A shorter list gets a larger `font_size` and `line_height`, so that it fills about the height it
  had before. On the opening menu, 12 lines at 34/1.55 became 8 lines at 40/1.85.
- Check the thumbnail: the list stays inside its card.

**Per copy, in addition:**

- **Matcha:**
  - p2: `278` becomes `277`. The page states 500 g of powder and the recipe uses 1.8 g a cup, so 277
    full cups; the site says 277.
  - p8: the header `אייס מאצ'ה אגבה` becomes `מאצ'ה אגבה על הקרח`.
  - p13: one centred column of the 8 lines.
    1. Replace the right column's text.
    2. Set `text_align` to center.
    3. Resize it to width 806, and place it at top 404, left 137.
    4. Delete the left column, the one starting `אייס מאצ'ה שומשום שחור`.
    5. Delete the vertical divider, a rect rotated −90° at about top 600, left 340, 432×4.
- **Chai:**
  - p5 (`דירטי צ'אי`): if the step number `4.` appears twice, change the lower one (on the row of
    `הוסיפו הרבה קצף חלב`) to `5.`.
- **Tea:**
  - p21: the header `משקה תות לואיזה` becomes `חליטת תות לואיזה`.
  - p22: the header `משקה מנגו סנצ'ה` becomes `חליטת מנגו סנצ'ה`.
  - p18: `ואורגנו /נענע טריים` becomes `ואורגנו או נענע טריים`.
- **Opening:** already done. The edits:
  - p2 reads `...ומחיות פרי, והרכבנו מהם 8 משקאות.`;
  - p6's header fix;
  - p16's list;
  - p17's number.
  Verify it, and change nothing unless the checker or the thumbnail says so.

**Acceptance:** D1 to D6 for every copy, and D8 for the sources.

### W2 — Look at every page

Take a thumbnail of every page of every copy (80 pages: 17 + 14 + 11 + 12 + 26, §2.2).

**Look for:**
- cut, overlapping or overflowing text;
- step numbers out of order;
- a step that makes no sense for its drink;
- an English subtitle that names a different drink;
- anything that says a count or a claim.

**Record every page** in the report's table, with the page number, what is on it, and one of three
verdicts:
- ok;
- fixed, with what changed;
- found, not fixed, with the quote.

The plain text read is not the visual order: recipe steps come out shuffled. Judge the order from the
picture.

**Acceptance:** D7.

### W3 — Five first messages, as drafts

Write `docs/plans/2026-09-28-lead-reply-messages.md` with five drafts. Status: `PROPOSED — Tom to
approve`.

**The five drafts:**
- one for each type (`מאצ׳ה`, `אובה`, `צ׳אי מסאלה`, `תמציות תה`);
- one for `בניית תפריט משקאות עשיר ורווחי לעסק`.

**Each draft is the reply** that goes with its PDF after the visitor sends
`היי, אני מעוניין ב<line>` to the lead line. Tom's words, which the drafts must meet:
- `הסבר קצר ולעניין ומאוד מקצועי שבו הלקוח יבין שיש איתנו עוד הרבה אופציות ובשיחה נסביר לו את זה`;
- `כך שתהיה לו סקרנות והוא יחכה לשיחה הזאת ויבוא כליד חם`;
- for the fifth, `הסבר קצר על כך שזה התפריט שאנחנו ממליצים לתחילת עבודה איתנו בצורה מנומסת רצינית ומקצועית`.

**The drafts use the site's voice and promise:**
- plural address (`אתכם`);
- the call within one business day, as the site's thanks promises:
  `קיבלנו את הפרטים ונחזור אליכם תוך יום עסקים אחד`.

**Bans, checkable per draft:**
- no dash used as punctuation (`—`, `–`, or ` - `);
- no niqqud;
- no digit;
- no price and no food cost (Sales-Machine D-018 bars the machine from stating either, and the
  message is the machine's);
- no emoji;
- at most 60 words.

**How to write them:** load the `stop-slop` skill, and draft plainly: the menu is attached, it shows
one part of what GT does, and the call will go through the rest. Send nothing and configure nothing.

**Acceptance:** D9.

### W4 — Close

**Open a PR on the brain repo, holding:**
- the messages file;
- the report, as `docs/plans/2026-09-28-lead-reply-menus-report.md` (the §9 content, in English);
- this document stamped SHIPPED, with pointers to the per-copy checker output and the messages file.

Then call `unsubscribe_pr_activity`.

**Acceptance:** D10.

## 5. Scope

**IN:** §4.

**OUT — do not touch, and do not "improve":**
- the five sources, and every other Canva design;
- the figures file, recipes, product pages, prices and FOOD COST;
- the site (gt-site) and the landing pages;
- WhatsApp, the lead line, Make and any sending;
- exporting or hosting PDFs, and the automatic reply (§2.4);
- the old `DAHTZuvZQH0` Ube menu.

## 6. Tom's part — the complete list. Nothing else is his.

**A. Before pasting:** allow the Canva tools in Claude Code.
- **Why it matters:** on 2026-09-28 every Canva call asked him for approval, and that stalled the
  work.
- **How:** add `mcp__Canva` to the allowed tools (`permissions.allow` in `.claude/settings.json`).
  Answering «always allow» at the first Canva prompt also works.
- **Time:** about 2 minutes.
- **Why only he can:** only he can grant permissions in his own session.

**B. After the report:**
- look at the five menus from the links in the report;
- approve the five message drafts, or rewrite them.
- **Time:** about 15 minutes.
- **Why only he can:** the drafts are customer-facing copy, and approving that is his (Sales-Machine
  `CLAUDE.md`, truth rule 5).

## 7. Landmines — do not rediscover these

1. **`Editing transaction … not found`, and every uncommitted page is lost.**
   - **What happened:** on 2026-09-28 it happened twice, about 28 minutes and about 40 seconds after
     opening. Both times other agents were editing other designs under the same account.
   - **Cause:** inferred, not confirmed. Opening a transaction anywhere on the account ends the open
     one.
   - **Resolution:**
     - one design, one session, no parallel agents on Canva;
     - commit every 2–3 pages;
     - on this error, make a plain read to see what was saved, reopen, and redo only the rest.
2. **Every Canva call asks for approval.**
   - **Cause:** the tools are not in the session's allow list.
   - **Resolution:** §6-A, before starting.
3. **Money text is two regions** (the `₪` normal and the digits bold). `replace_text` flattens them.
   Use `find_and_replace_text` on the exact substring; see drinks-pricelist `SKILL.md`, LEARNED
   2026-08-27.
4. **Page titles and metadata lie.**
   - Match a page by its heavy title element of about 60 px, not by its metadata title.
   - The list pages use ASCII `'` in `מאצ'ה` while other texts use `׳`.
   - Copy strings from the read; never retype them.
5. **A structured read of a whole design is too big to return.**
   - The connector saves it to a file.
   - It is JSON. If it is a list, the payload is `json.loads(d[0]['text'])`.
   - `check_menu.py` handles both.
6. **Thumbnails come back inline from the tools, but `export-download.canva.com` is blocked for
   downloads here** (drinks-pricelist LEARNED, 2026-08-27). Verify by reading and by the inline
   thumbnail. Do not try to download PDFs.
7. **A cancelled or expired transaction leaves the design unchanged.**
   - The check that follows it shows the old state; that is not a failed edit.
   - Re-read before concluding anything.

## 8. Halt conditions (additions to the inherited set)

- **A figure disagrees with the figures file** on a drink page → **STOP** editing that page. Report it
  as found, not fixed. Pricing belongs to the drinks-pricelist workflow and Tom.
- **Any edit to a design not in §2.2** → **STOP**.
- **The same page's edit fails on two fresh transactions** → **STOP**, and report what is saved.
- **Anything that would send a message or configure WhatsApp** → **STOP**. It is out of scope.

## 9. Final report (to Tom, in Hebrew; the PR body in English)

1. The five copies with their view links, and each copy's `check_menu.py` last line.
2. D1 to D10, each ✅ or ❌, with its evidence pointer. No partial credit.
3. The per-page table (80 rows, one per page of §2.2).
4. The found-not-fixed list, quoted, including the two items of §2.4.
5. The five message drafts, verbatim.
6. What is still Tom's (§6-B), and the next build (§2.4).

If anything is not ready, say so first and plainly.
