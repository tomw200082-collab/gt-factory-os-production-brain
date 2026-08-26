# MASTERPROMPT — the final catalog carries the approved figures, then a new opening menu is built from it

**STATUS: SHIPPED 2026-08-26.** Do not re-run.

Executed end to end on 2026-08-26. Evidence:

- Approved figures transcribed into `.claude/skills/drinks-pricelist/drinks_final_figures.json`
  from a page-by-page read of `DAHPi9gpfts`; margin and profit re-derive from
  `price/1.18 - cost` with 0 mismatches across all 48 rows.
- Backup: `docs/pricing/backups/2026-08-26_DAHTYkRvEnM_pre-repricing.json`
  (48 drink-page records + 4 summary columns). Restore tooling:
  `scripts/canva_catalog_backup.py`, runbook `docs/pricing/RESTORE_DAHTYkRvEnM.md`.
- Catalog `DAHTYkRvEnM`: 144 drink-page fields and 144 summary-table values match the
  figures file with 0 deviations. 0 asterisks on drink-page costs, 44 on the table,
  absent on figures pages 8/16/17/18. All 96 money elements kept two textRegions with a
  normal-weight shekel sign. A pre/post element diff shows 112 elements changed — the
  109 written drink-page fields plus the 3 summary columns; 35 fields already carried
  their target value and were skipped. Nothing else in the design changed.
- Menu `DAHTY5nfDxo`: 21 pages — the 20 in the §4.4 order plus the original placeholder,
  which stays until Tom types the exact phrase the delete requires. Page 21 keeps its
  four hyperlinks. `DAHTXqsXzDg` still reports 20 pages and `DAHTYkRvEnM` 60, proving
  the pages were copied and not moved.

> **Usage:** paste this entire file as the first message of a fresh session with the
> Canva MCP (`mcp__Canva__*`), a shell, and push access to
> `tomw200082-collab/gt-factory-os-production-brain`. Work on your session's designated
> branch. It halts for Tom in exactly one place — §6 is that complete list.
>
> **Provenance:** written 2026-08-26 from direct reads of both live Canva designs on
> that date (`mcp__Canva__read-design`, plain and structured), not from memory or from a
> prior brief.
>
> **Shelf life: 7 days from 2026-08-26.** Past that, re-run §2.6 before touching
> anything. **Divergence protocol: HALT and report.** If the live state does not match
> §2, do not adapt. The likely cause is that someone else edited the catalog, and
> adapting would write approved figures over an edit nobody has reviewed.

---

## §0 — How to work

**Who you are here.** A fresh session holding: the Canva MCP, a shell, and push access
to `gt-factory-os-production-brain`. You may decide method freely. You may not decide any
figure, any wording, or any design change — see §1.1.

**Read first, in order:**
1. `CLAUDE.md` (repo boot kernel).
2. `.claude/skills/drinks-pricelist/SKILL.md` — the current-figures block at the top.
3. `.claude/skills/drinks-pricelist/drinks_final_figures.json` — the frozen authority for
   all 48 figures.

**Authority.** `CLAUDE.md` wins every conflict, cited not restated. Halt conditions,
evidence standard and git discipline are inherited from `CLAUDE.md` §Stop conditions,
§Evidence and §Write boundaries. §8 below lists only the additions specific to this work.
Where this document and `CLAUDE.md` disagree, `CLAUDE.md` wins and this document is wrong.

**The standard, in Tom's words:** "this is a valuable catalog, no embarrassments in it."
Translated into three checkable prohibitions:
- Nothing on any page changes except the three figures named in §2.4 and the three
  column blocks named in §2.5.
- No element is created and none is deleted, on any page of either design.
- No write happens before the backup in W1 exists and has been read back.

**Output language: concise English.** Short sentences. No preamble, no restating the
task, no narrating what you are about to do. Every Hebrew string in this document is a
data literal inside backticks — copy it byte-for-byte and never translate it.

**First action:** run the re-verification block in §2.6. Do not open an editing
transaction before it returns the expected counts.

---

## §1 — Mission and definition of done

**One testable sentence:** the catalog `DAHTYkRvEnM` states the approved figures on all
48 drink pages and on its summary table, a byte-exact rollback for it exists in the repo,
and `DAHTY5nfDxo` holds a 20-page opening menu whose shell is the existing menu's and
whose 12 drink pages are copies of the repriced catalog's.

| # | Condition | The observation that would prove it false |
|---|---|---|
| D1 | Backup exists and round-trips | `docs/pricing/backups/2026-08-26_DAHTYkRvEnM_pre-repricing.json` holds 48 drink-page records and 4 summary-column strings; `python3 scripts/canva_catalog_backup.py --verify` on the pre-edit dump reports 0 differences |
| D2 | Catalog drink pages match the figures | a fresh plain read of the 48 drink pages, compared in code against `drinks_final_figures.json`, reports 0 deviations across 144 fields |
| D3 | Summary table matches the figures | the three column strings on page 60 re-parse to 48 costs, 48 prices, 48 margins, each equal to the figures file, with the family grouping of §2.5 intact |
| D4 | Nothing else changed in the catalog | a diff of the pre-edit dump against a fresh post-edit dump touches only the elements listed in §2.4 and §2.5 — every other element's characters are byte-identical |
| D5 | Asterisks follow the decision | 0 of the 48 drink-page cost elements carry `*`; the summary-table cost column carries `*` on 44 of 48 rows, absent on the rows for figures pages `8`, `16`, `17`, `18` |
| D6 | New menu is built | `DAHTY5nfDxo` has exactly 20 pages in the order of §4.4, and its page 20 still carries the same 4 hyperlinks as the source menu's page 20 |
| D7 | New menu's drinks carry the new figures | the 12 drink pages of `DAHTY5nfDxo` show the same three figures as their source catalog pages |
| D8 | Committed, pushed, stamped | `git status` clean on your designated branch, and this file's status line no longer reads LIVE |

Anything not on this list is out of scope unless Tom asks.

### §1.1 — Settled, do not reopen

Every one of these was decided by Tom on 2026-08-26. Re-deciding any of them is a defect,
not an improvement.

1. **The 48 figures are frozen.** `drinks_final_figures.json` is the authority. You are a
   transcriber, not a pricer. A figure that looks wrong is a HALT, never a recomputation.
2. **No asterisks on the 48 drink pages.** In this catalog `*` already means something
   else on the page — see §2.4. The summary table keeps its asterisks, because its
   footnote explains them.
3. **No profit-per-cup line.** This catalog's drink pages carry three figures. Do not add
   a fourth element.
4. **The summary table on page 60 is in scope** and is updated in the same pass.
5. **The new menu's drink pages are copies of the catalog's pages**, not rebuilds of the
   old menu's drink layout. They will look like the catalog: three figures, no ingredient
   chip row, the catalog's own labels. That is the intended result.
6. **Task order is fixed:** the catalog is finished and its transaction committed before a
   single page is copied into the menu. A page copied early carries the old numbers.

---

## §2 — Ground truth, measured 2026-08-26; re-verify at boot

### §2.1 — The three designs

| Role | id | Pages | Title |
|---|---|---|---|
| Target catalog | `DAHTYkRvEnM` | 60 | `Copy of ליאת 11.8.26 קטלוג משקאות מעודכן` |
| Template menu, read-only source | `DAHTXqsXzDg` | 20 | `תפריט פתיחה מומלץ` |
| Target menu, near-empty | `DAHTY5nfDxo` | 1 | `תפריט פתיחה מומלץ חדש` |

All three are `1080x1920`, fixed pages, `isEditable: true`.

`DAHTYkRvEnM` is **not** the catalog that was repriced on 2026-08-26. That was
`DAHPi9gpfts`, 64 pages, a different edition with a different page layout. Do not open it,
do not copy from it, and do not reuse any element id measured against it.

### §2.2 — Catalog structure

60 pages: 1 cover, 10 family dividers, **48 drink pages**, 1 summary table.

Dividers sit at pages `2, 10, 14, 19, 23, 30, 36, 42, 49, 54`. The cover is page 1. The
summary table is page 60. Every other page is a drink page.

### §2.3 — Page map: catalog page to figures-file page

Verify this map at boot by name before you rely on it (§2.6). Do not derive it from the
running numbers printed on the pages — those are wrong in places (§7.6).

| Family | Catalog pages | Figures pages |
|---|---|---|
| `01 · חליטות קרות` | 3,4,5,6,7,8,9 | 8,9,10,11,12,13,14 |
| `02 · לימונדות` | 11,12,13 | 16,17,18 |
| `03 · Fruitea · חליטות תה` | 15,16,17,18 | 20,21,22,23 |
| `04 · גזוז` | 20,21,22 | 25,26,27 |
| `05 · אייס מאצ'ה` | 24,25,26,27,28,29 | 29,30,31,32,33,34 |
| `06 · קולקציית מאצ׳ה מיוחדת` | 31,32,33,34,35 | 36,37,38,39,40 |
| `07 · מאצ'ה קוקוס` | 37,38,39,40,41 | 42,43,44,45,46 |
| `08 · צ'אי מסאלה` | 43,44,45,46,47,48 | 48,49,50,51,52,53 |
| `09 · צ'אי מסאלה קולד פואם` | 50,51,52,53 | 55,56,57,58 |
| `10 · אובה` | 55,56,57,58,59 | 60,61,62,63,64 |

The two sequences are strictly parallel: catalog drink pages in reading order map to the
figures file's keys in ascending order. The family named `03` is titled `Fruitea` in this
catalog and `משקאות דגל` in the figures file's provenance. Same four drinks, renamed band.

### §2.4 — What a drink page looks like, measured on catalog page 3

Three text elements carry figures. Nothing else on the page is in scope.

| Field | Matches | Font size | Structure |
|---|---|---|---|
| cost | `^₪\d+\.\d\d$` | ~48.0 | **two textRegions**: `₪` normal weight, then the digits bold |
| price | `^₪\d+$` | ~48.0 | **two textRegions**: `₪` normal weight, then the digits bold |
| margin | `^\d\d%$` | ~50.7 | one textRegion |

Locate them **by content pattern and font size, never by a stored id.** On page 3 the ids
were `LBP7z4LgKbTjhWnQ` (cost), `LByKTJFJVhmQrVR1` (price), `LB314xjpsjhW6DPr` (margin);
ids are per page and are not stable across sessions.

To match: concatenate the element's `textRegions[].characters` into one string before
applying the pattern — the cost element stores `₪` and `3.76` as separate regions and
neither half matches on its own. Read the font size from
`textRegions[0].formatting.fontSize`, and band it rather than testing equality: the money
elements measured `48.0002` and the margin `50.6668` on page 3, and sibling pages vary in
the last decimals. A band of 40 to 80 separates all three from every other text element on
the page.

**The page's drink title** is the single text element at roughly `top: 62` whose font size
is `60`. On page 3 it reads `חליטת היביסקוס וליים`. Do not confuse it with the recipe
heading lower down, which repeats the name, may carry a trailing `*`, and continues
`אופן הכנה:` in a second region — nor with the design's own page `title` and `notes`
fields, which hold English and partial names.

Adjacent elements that must not change, quoted here so you recognise them and leave them
alone: the cost label `FOOD COST` + `ללא מע״מ`, the price label `מחיר מומלץ לצרכן` +
`כולל מע״מ`, the margin label `ר ו ו ח` (with spaces, exactly as written), the running
header `gt Iced Tea · 01`, the footer `· Summer 2026`, the recipe heading
`אופן הכנה:` (with a colon), the numbered steps, and per-page footnotes such as
`*נטול קפאין` and `*בסיס מאצ׳ה Classic: ערבבו 1.8 גרם אבקה עם 50 מ״ל מים עד לקבלת תערובת חלקה.`

**The `*` on these pages already means caffeine-free, or points at the matcha-base note.**
It has never meant a garnish-cost estimate here. This is why D5 requires zero asterisks on
drink-page costs.

### §2.5 — What the summary table looks like, measured on catalog page 60

Four text elements hold the table body, each one column, each a single string with
newlines. Ids measured 2026-08-26, to be re-located by content at boot:

| Column | Element id suffix | Content |
|---|---|---|
| names | `LBD4dsjfg56M4vDH` | 48 names in family groups. **Read-only. Never write it.** |
| cost | `LB5KYwbT5wrvxrpk` | 48 values, `*` on 44 of them |
| price | `LBRpFcrdnQwZvzQX` | 48 values |
| margin | `LBqqQp7kmW5yKfXY` | 48 values |

**The exact string shape**, verified against all three value columns: one leading `\n`,
then the ten family groups joined by `\n\n`, each group's rows joined by `\n`, and no
trailing newline. Group sizes in order: `7, 3, 4, 3, 6, 5, 5, 6, 4, 5`. In Python:

```python
# rebuilds one column exactly as page 60 stores it (verified 2026-08-26 against all 3 columns)
GROUPS = [7, 3, 4, 3, 6, 5, 5, 6, 4, 5]          # sums to 48
def column(values):
    out, i = [], 0
    for n in GROUPS:
        out.append("\n".join(values[i:i + n])); i += n
    return "\n" + "\n\n".join(out)
```

The footnote element reads
`עלות = ללא מע״מ · מחיר מומלץ = כולל מע״מ 18% · רווח מחושב על ההכנסה נטו · * כולל הערכת עלות גרניש/קצף`
and does not change. The ten band headings (`01 · חליטות קרות · ICED TEA` and its nine
siblings) are separate elements and do not change.

### §2.6 — Re-verification block, run this first

```bash
# 1. the figures file is the one this brief was written against (2026-08-26)
cd gt-factory-os-production-brain
python3 - <<'PY'
import json
d = json.load(open(".claude/skills/drinks-pricelist/drinks_final_figures.json"))
p = d["pages"]
assert len(p) == 48, len(p)
assert sum(1 for v in p.values() if v["star"]) == 44
assert p["8"]["cost"] == "₪3.11" and p["8"]["price"] == "₪20" and p["8"]["marg"] == "82%"
assert p["42"]["marg"] == "82%"          # the rounding case, see landmine 7
print("figures file OK:", len(p), "pages,", sum(1 for v in p.values() if v["star"]), "asterisks")
PY
```

Then, through the Canva MCP, with no transaction open:

1. `read-design DAHTYkRvEnM` metadata. Expect `page_count: 60`. Anything else: **HALT**.
   Then `read-design DAHTY5nfDxo` metadata. Expect `page_count: 1`. It is owned by a
   different Canva user in the same team than the catalog is; if it cannot be read, or a
   transaction cannot be opened on it, **HALT** and tell Tom the account needs edit
   access — do not build the menu somewhere else.
2. Plain-read catalog pages `3, 18, 60`. Expect page 3 to still read `₪3.76` / `₪19` /
   `77%`, page 18 to read `₪5.41` / `₪24` / `73%`, and page 60's cost column to still
   begin `₪3.76`. Any mismatch means somebody edited the catalog after 2026-08-26:
   **HALT and report**, do not adapt.
3. Plain-read the 48 drink pages and check each page's title against the figures-file name
   for its mapped key. Expect 47 exact matches and exactly one known divergence: catalog
   page 7 reads `חליטת תה ירוק לואיזה וליים` where the figures file says
   `חליטת תה ירוק וליים`. A second divergence: **HALT**.

---

## §3 — What the hard part actually is

**The visible task is typing 144 numbers. The actual risk is everything you type them
next to.** Each figure sits inside a two-part text element whose ₪ sign and digits carry
different weights, on a page that also uses the asterisk for an unrelated footnote, in a
catalog whose own summary page already disagrees with its own drink pages. The failure
mode is not a wrong number. It is a right number that flattened a font, ate a footnote, or
got written to a page that was never in the map.

**The catalog is already internally inconsistent, and that is not yours to fix.** Page 18
prices `חליטת תפוח היביסקוס` at `₪5.41` with `73%`; page 60 prices the same drink at
`₪3.25*` with `84%`. Two pages both print the running number `· 45`. The first iced tea
prints `· 01` where its siblings print `· 09` through `· 14`. You overwrite the figures
from the authority file and leave every one of those cosmetic defects exactly as found.

**The backup is the product, not the paperwork.** Canva exposes no undo through this API.
The only rollback that exists after your first write is the one you wrote before it. Build
it, read it back, and only then open an editing transaction.

**The menu is a page-copy job, not an authoring job.** `merge-designs` copies whole pages
between designs. Nothing about the 12 drink pages is retyped, which is why W4 runs after
W2 and W3 have committed and not before.

---

## §4 — Workstreams, in this order

### W1 — Backup and rollback, before any write

**Capture.** Open one read-only transaction on `DAHTYkRvEnM` and structurally read every
page. This exceeds the tool's token cap; that is expected and harmless — see landmine 3.
Parse the saved result file offline. Cancel the transaction when done.

Keep the raw structured dump at
`<scratchpad>/catalog_pre_edit_raw.json`. It is session-local, it is the instrument that
closes D4, and it is not committed — it runs to megabytes. The committed backup below is
the durable rollback: it holds the original text of every element this work can touch,
which is everything a restore needs.

**Write** `docs/pricing/backups/2026-08-26_DAHTYkRvEnM_pre-repricing.json`:

```json
{
  "_meta": {"design_id": "DAHTYkRvEnM", "page_count": 60, "captured": "2026-08-26",
            "method": "read-design structured, one read-only transaction, cancelled"},
  "drink_pages": {
    "3": {"figures_page": 8, "title": "...",
          "cost":   {"element": "LB...", "text": "₪3.76", "regions": 2, "font_size": 48.0002},
          "price":  {"element": "LB...", "text": "₪19",   "regions": 2, "font_size": 48.0002},
          "margin": {"element": "LB...", "text": "77%",   "regions": 1, "font_size": 50.6668}}
  },
  "summary_page": {"page_index": 60,
    "columns": {"names": {"element": "LB...", "text": "..."},
                "cost": {"...": "..."}, "price": {"...": "..."}, "margin": {"...": "..."}}}
}
```

**Write** `scripts/canva_catalog_backup.py` with two modes:
- `--emit-restore` reads the backup and prints an ordered JSON list of `edit-design`
  operations that put every original string back — `find_and_replace_text` for the drink
  pages, `replace_text` for the three summary columns. A future session pastes those
  operations and the catalog returns to its 2026-08-26 state.
- `--verify <before.json> <after.json>` diffs two raw structured dumps element by element
  and reports every element whose characters differ. D4 is closed by running it against
  `catalog_pre_edit_raw.json` and a fresh post-edit dump, and finding that the differing
  set is exactly the 144 drink-page elements plus the 3 summary columns.

**Write** `docs/pricing/RESTORE_DAHTYkRvEnM.md`: how to run both modes, and the explicit
statement that the restore re-locates elements by content and font size because ids are
not stable between sessions.

Commit all three before the first catalog write. **Acceptance: D1.**

### W2 — The 48 drink pages

For each catalog drink page in §2.3, look up the mapped figures-file entry and write three
values. Strip the asterisk from the figures file's cost — §1.1 item 2.

**Use `find_and_replace_text` for cost and price**, finding the digits only and replacing
the digits only. `replace_text` on those elements collapses their two textRegions into one
and turns the `₪` bold — landmine 1. **Use `replace_text` for margin**, which has a single
region.

So for catalog page 3, mapped to figures page `8`, whose entry is `₪3.11` / `₪20` / `82%`:

```json
[{"type": "find_and_replace_text", "locator_id": "<PAGE>-<COSTELEM>",  "find_text": "3.76", "replace_text": "3.11"},
 {"type": "find_and_replace_text", "locator_id": "<PAGE>-<PRICEELEM>", "find_text": "19",   "replace_text": "20"},
 {"type": "replace_text",          "locator_id": "<PAGE>-<MARGINELEM>", "text": "82%"}]
```

`locator_id` must carry the page prefix — landmine 2. Pass
`is_editable: true, is_responsive: false, is_empty: false`. One page per call.

Where a page already carries the target value, skip that operation rather than writing an
identical string.

**Write page 3 first, alone. Re-read it and confirm the cost element still reports two
textRegions with `₪` at normal weight.** Only then continue. Commit the transaction every
8 pages; a lost transaction costs every uncommitted page in it.

**Acceptance: D2, D5 (drink-page half).**

### W3 — The summary table, page 60

Rebuild the three value columns in code from the figures file using the `column()` helper
in §2.5, then write each with one `replace_text`. Costs here **keep** their asterisks:
`*` on the 44 entries whose figures-file `star` is true, absent on the four whose `star`
is false. Do not touch the names column, the band headings, or the footnote.

Re-read the page and confirm each column re-parses to 48 values in groups of
`7,3,4,3,6,5,5,6,4,5`. Commit.

**Acceptance: D3, D5 (table half).**

### W4 — The new opening menu, only after W2 and W3 are committed

Target `DAHTY5nfDxo`. It currently holds 1 placeholder page.

Build it with `merge-designs`, `type: modify_existing_design`, appending in this exact
order. Use one `insert_pages` operation per catalog page so the order is unambiguous:

| New menu page | Source | Source page |
|---|---|---|
| 1 | `DAHTXqsXzDg` | 1 (cover) |
| 2 | `DAHTXqsXzDg` | 2 (intro) |
| 3 | `DAHTYkRvEnM` | 3 |
| 4 | `DAHTYkRvEnM` | 18 |
| 5 | `DAHTYkRvEnM` | 22 |
| 6 | `DAHTYkRvEnM` | 7 |
| 7 | `DAHTYkRvEnM` | 16 |
| 8 | `DAHTYkRvEnM` | 43 |
| 9 | `DAHTYkRvEnM` | 50 |
| 10 | `DAHTYkRvEnM` | 44 |
| 11 | `DAHTYkRvEnM` | 24 |
| 12 | `DAHTYkRvEnM` | 26 |
| 13 | `DAHTYkRvEnM` | 28 |
| 14 | `DAHTYkRvEnM` | 29 |
| 15-19 | `DAHTXqsXzDg` | 15,16,17,18,19 (the five product pages) |
| 20 | `DAHTXqsXzDg` | 20 (contact links) |

That catalog-page order reproduces the existing menu's 12 drinks in the existing menu's
order: `חליטת היביסקוס וליים`, `חליטת תפוח היביסקוס`, `גזוז היביסקוס ותפוח`,
`חליטת תה ירוק לואיזה וליים`, `חליטת תות לואיזה`, `אייס צ'אי מסאלה קלאסי`,
`צ'אי מסאלה קולד פואם וניל`, `צ'אי מסאלה על הקרח`, `אייס מאצ'ה קלאסי`, `אייס מאצ'ה תות`,
`אייס מאצ'ה מסאלה`, `מאצ'ה אגבה על הקרח`. Confirm each copied page's title against that
list before the delete step.

Then delete the placeholder, which is now page 1. **This is the one step that stops for
Tom — see §6.** After the delete, the design has 20 pages.

Read the finished design back and confirm: 20 pages; `DAHTXqsXzDg` still reports 20 pages
and `DAHTYkRvEnM` still reports 60, proving the pages were copied and not moved; page 20
still carries its four hyperlinks (`gteveryday.com`, the Instagram profile, the WhatsApp link with its prefilled
message, and the `mailto:` address); the 12 drink pages show the figures written in W2.

**Acceptance: D6, D7.**

### W5 — Land it

Commit the backup, the script, the runbook and this file's stamp. Push with
`git push -u origin <your designated branch>`, retrying network failures at 2s, 4s, 8s,
16s. Open a draft PR if none is open for the branch. Stamp this file `SHIPPED` with
pointers to the backup path, the two design ids, and the commit.

**Acceptance: D8.**

---

## §5 — Scope

**IN:** everything in §4.

**OUT — do not touch, do not improve:**
- The old catalog `DAHPi9gpfts` and the old menu `DAHTXqsXzDg`. The menu is a read-only
  copy source in W4; it is never edited.
- Any drink name, recipe step, ingredient line, label, band heading, footnote, header
  number or footer in either design. The running-number defects in §7.6 stay as found.
- The cover page and the ten divider pages of the catalog.
- The names column of the summary table.
- Page geometry, fonts, colors, images, and element counts anywhere.
- `drinks_final_figures.json` itself. It is the authority; it is not edited by this work.
- Any recomputation of a cost, price, margin or profit.
- Sending anything to a lead or a customer. `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` is
  `false`; delivery is Tom's to decide.
- Merging the branch or closing anyone's PR.

---

## §6 — Tom's part, the complete list, nothing else is his

**A. Approve the page operations in W4.** `merge-designs` asks for confirmation before
inserting pages, and refuses a delete without the literal phrase `I approve the deletion`.
No paraphrase is accepted for the delete — not "yes", not "go ahead", not "I approve".

Ask once, in a single message: the 18 pages to be inserted and where they come from, plus
the one page to be deleted (page 1 of `DAHTY5nfDxo`, the empty placeholder), and request
that exact phrase. One phrase covers both. Takes him ten seconds. Do not split this into
two round-trips.

Everything else in this document is yours. The figures are already approved, the five
decisions in §1.1 are already made, and the catalog write does not need a second go-ahead.

---

## §7 — Landmines, do not rediscover these

1. **The cost and price elements have two textRegions.** `replace_text` writes one region
   and the `₪` inherits the digits' bold weight — a visible typographic change on a page
   Tom called valuable. → Use `find_and_replace_text` on the digits only, and verify the
   region count after the first page.
2. **A bare element id fails the whole batch.** Passing `LBP7z4LgKbTjhWnQ` instead of
   `PBrMd12yfFHKQYQH-LBP7z4LgKbTjhWnQ` returns `"Page ID did not match the expected
   pattern"` on every operation in the call, and the thumbnail still renders, which reads
   like success. → Always prefix with the page's `locator_id`. Check every operation's
   status, not the picture.
3. **Structured multi-page reads exceed the tool's token cap.** The call reports overflow
   and writes the result to a file. The transaction still opened and its id is inside that
   file. → This is the intended path for W1. Parse the file offline; do not retry the read
   in smaller pieces and do not assume the transaction failed.
4. **The catalog's asterisk is not the pricelist's asterisk.** On drink pages `*` marks
   `*נטול קפאין` and the matcha-base note. Copying the 44-asterisk convention onto drink
   pages would attach a meaning the page never explains. → Drink pages: no asterisk on
   cost. Page 60 only: asterisks per the figures file.
5. **Page 60 and the drink pages already contradict each other.** Neither is ground truth.
   → Both are overwritten from `drinks_final_figures.json`. Do not use one to validate the
   other, and do not report the disagreement as a defect you introduced.
6. **The running numbers printed on the pages are unreliable.** The first iced-tea page
   prints `· 01` where the family runs `· 09` to `· 14`; the `Fruitea` family prints `· 01`
   to `· 04`; two matcha-coconut pages both print `· 45`. → Map by page position and drink
   name only. Never key anything off the printed number, and never correct it.
7. **The margin formula uses unrounded profit.** `round((price/1.18 - cost)/(price/1.18)*100)`.
   Rounding the profit to agorot first yields `81%` where the approved figure for figures
   page `42` is `82%`. → If you write a re-derivation check, follow `_meta.formulas` in the
   figures file exactly.
8. **Prices move a long way in two families.** Every `07 · מאצ'ה קוקוס` page currently
   prints `₪28` and the approved prices are `₪34`, `₪32`, `₪44`, `₪44`, `₪44`. Page 60
   currently prints `₪3.25*` for a drink whose approved cost is `₪2.73*`. → Large deltas
   are expected. They are not a sign you mis-mapped a page; verify the name, then write.
9. **`merge-designs` is the only tool for page copies, and it demands confirmation.** It
   refuses to run a delete without the exact phrase in §6, and it wants a plain
   confirmation before inserts too. → Budget one round-trip with Tom, and batch the
   inserts so you only need it once.
10. **Canva has no undo API.** There is no version to roll back to through this interface.
    → W1 before W2. Always.

---

## §8 — Halt conditions

Inherited from `CLAUDE.md` §Stop conditions. Additions specific to this work:

- `DAHTYkRvEnM` does not report exactly 60 pages → **STOP**.
- Any of the three probe pages in §2.6 step 2 does not show its expected pre-edit values
  → **STOP** and report. Someone edited the catalog; writing now could double-apply.
- A drink page yields other than exactly one cost, one price and one margin match →
  **STOP** for that page, report it, continue with none of them.
- A second name divergence beyond the known catalog-page-7 case → **STOP**.
- A figure in `drinks_final_figures.json` looks wrong → **STOP** and report. Never
  recompute, never correct.
- Any write attempted before the W1 backup exists and has been read back → **STOP**.
- Tom has not typed the exact phrase for the placeholder delete → leave the placeholder in
  place, finish everything else, and report the design as 21 pages pending his word.

---

## §9 — Final report

1. What a stranger can now open and see working, end to end.
2. Each of D1 through D8, marked done or not done, each with its evidence pointer. No
   partial credit.
3. The numbers: pages written of 48, fields written of 144, summary-table values written
   of 144, deviations found on re-read, asterisk count on drink pages and on the table,
   pages in the new menu.
4. The artifacts and where they are: backup path, script path, runbook path, commit, PR,
   and both design ids.
5. What is still Tom's, and what remains genuinely unfinished.
6. The single next action.

If anything is not ready, say so first and plainly.
