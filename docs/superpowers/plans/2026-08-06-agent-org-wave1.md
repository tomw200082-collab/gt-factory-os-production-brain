# Agent-Org Wave 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up Messi HQ (20:00 evening loop → dispatch → calendar → morning email) plus the two wave-1 agents and their seeded warehouses, per the approved spec `docs/superpowers/specs/2026-08-06-agent-org-wave1-design.md`.

**Architecture:** Everything is docs + one runtime binding. The permanent memory is two warehouse files; the two agents are `.claude/agents/` charters dispatched from Messi's session; the loop is a new `mode=evening` in the existing messi skill, run by a self-bind trigger into the one session that has connectors. No runtime code, no schema.

**Tech Stack:** brain-repo markdown · Claude Code agents · CCR triggers (`create_trigger`/`send_later`/`fire_trigger`) · Make webhook scenario 6439326 (real Gmail send) · Google Calendar MCP · Notion MCP.

## Global Constraints

- **Noisy failure everywhere:** every run leaves a committed log line in `docs/ceo/messi/<YYYY-MM-DD>.md`; a run that produced nothing says so by email. Silence = bug. (Spec §3.)
- **Dispatch packets:** every writing packet carries a mechanical `done-criterion` **and** the two verbatim boundary sentences — `⊥ merge · ⊥ deploy · ⊥ מיגרציית פרוד` + *"יורש את `.claude/skills/messi/SKILL.md` §גבולות במלואו"* (`messi/reference/dispatch.md` law 2). A packet missing either is not dispatched.
- **Calendar:** `[cos-os]`-prefixed blocks only; events without the prefix are read-only, never moved/edited/deleted. Timezone `Asia/Jerusalem`. No due dates or blocks on Friday/Saturday.
- **Employee messages: drafts only, Tom sends.** Customer-facing / money / irreversible / mass ⇒ ask Tom (batched to the morning email).
- **Warehouse record rule:** every entry carries what · exact path · quality grade (`מאושר-טום` / `טוב` / `ישן — אל תשתמש`) · last-verified date. An entry without a date does not exist. Corrections land same-day.
- **Git:** explicit paths only (`⊥ git add -A`), commit at end of every task, push `origin HEAD` on branch `claude/gt-everyday-catalog-tasks-qellwd` (restarted from main).
- **Authority:** `CLAUDE.md` unchanged (Tom sole writer). The messi SKILL.md edits in Task 6 implement Tom's written decisions of 2026-08-06 (spec §2) and cite them.

**Working directory for all tasks:** `/home/user/gt-factory-os-production-brain` on branch `claude/gt-everyday-catalog-tasks-qellwd` (created from `origin/main`).

---

### Task 1: Warehouse infrastructure — format contract

**Files:**
- Create: `docs/warehouses/README.md`

**Interfaces:**
- Produces: the record format + freshness rules that Tasks 2–3 instantiate and the agents in Tasks 4–5 cite as `docs/warehouses/README.md §פורמט`.

- [ ] **Step 1: Write the file**

```markdown
# מחסני חומרים — חוזה הפורמט

> הכרעת טום 2026-08-06 (ספק `docs/superpowers/specs/2026-08-06-agent-org-wave1-design.md` §2.2):
> "איפה בדיוק החומרים המעודכנים והאיכותיים" הוא נכס מבני שמתוחזק,
> לא ידע שנמצא מחדש כל סשן.

## פורמט

מחסן = קובץ `docs/warehouses/<domain>.md`. כל רשומה נושאת ארבעה שדות, תמיד:

| שדה | כלל |
|---|---|
| **מה** | שם עברי/עסקי חד-משמעי |
| **נתיב מדויק** | דרופבוקס (נתיב מלא) / קאנבה (design/folder id) / ריפו / שופיפיי (SKU) |
| **דירוג** | `מאושר-טום` (שימש בתוצר שטום אישר) · `טוב` (נבדק, לא אושר בתוצר) · `ישן — אל תשתמש` |
| **אומת** | תאריך `YYYY-MM-DD`. **רשומה בלי תאריך = לא קיימת** — אסור לצטט אותה |

## כללי תחזוקה

1. **כל תיקון של טום נרשם באותו יום** במחסן התחום — כל תיקון משולם פעם אחת (ספק §2.8).
2. בעל המחסן: הסוכן של התחום. מסי אוכף בביקורת יום ראשון (ספק §8):
   רשומות שתאריך האימות שלהן בן >30 יום מסומנות `⚠ לאימות`.
3. רשומת-שלילה היא רשומה לגיטימית: "X קיים במערכת אבל **לא** בשימוש/לא נמכר —
   מקור: טום, תאריך". היא שווה בערכה לרשומת-חיוב.
4. מחיקת רשומה — לעולם לא. דירוג `ישן — אל תשתמש` + תאריך במקום.

## מחסנים פעילים

| קובץ | תחום | סוכן בעלים |
|---|---|---|
| `marketing-assets.md` | נכסי שיווק ועיצוב | `gt-assets-designer` |
| `catalog-truth.md` | מה אנחנו באמת מוכרים | `gt-catalog-truth` |
```

- [ ] **Step 2: Verify**

Run: `grep -c 'אומת' docs/warehouses/README.md`
Expected: ≥1; file exists with the two tables.

- [ ] **Step 3: Commit**

```bash
git add docs/warehouses/README.md
git commit -m "docs(warehouses): format contract — 4-field records, same-day corrections, negative entries"
```

---

### Task 2: Seed `marketing-assets.md` (hash-verified against Dropbox)

**Files:**
- Create: `docs/warehouses/marketing-assets.md`
- Modify: `docs/pricing/2026-08-06_customer_pricelist_pdf.md` (§Structure band-photo names — they are unverified from-memory names; fix from the hash check)

**Interfaces:**
- Consumes: format from Task 1.
- Produces: the warehouse `gt-assets-designer` (Task 4) declares as its source of truth.

**Background for the implementer:** the V3 pricelist build (`docs/pricing/pricelist_pdf/build.py`) names its inputs by *local working filenames* (`hd/h14.png`, `pw/p23.png`…). The Dropbox originals must be re-identified by **content hash**, not by the filenames in the V2/V3 record (three of them are suspected wrong). Dropbox `get_file_metadata` returns `content_hash` = Dropbox's block-hash (SHA-256 of concatenated SHA-256s of 4MB blocks — for files ≤4MB this is `sha256(sha256(content))`).

- [ ] **Step 1: Hash-identify the three band photos + cover**

The local files live in the (possibly reclaimed) scratchpad `…/scratchpad/pl2/{hd,pw,src}`. If the scratchpad still exists, compute for each of `hd/h14.png`, `pw/p23.png`, `hd/h12.png`, `src/cover.png`:

```python
import hashlib, pathlib
def dropbox_hash(p, BLOCK=4*1024*1024):
    h = b''.join(hashlib.sha256(c).digest()
                 for c in iter(lambda f=open(p,'rb'): f.read(BLOCK), b''))
    return hashlib.sha256(h).hexdigest()
```

then list the Dropbox folders `AI YASTREBOVA/CATALOG/2 slide/`, `…/MATCHA UBE HOJICHA/PRODUCT PHOTOS/` via MCP `get_file_metadata`/`list_folder` and match `content_hash`. If the scratchpad is gone, fall back to the session-derived mapping below and mark those four rows `טוב` instead of `מאושר-טום` until re-verified:
`עמוד תמציות = hf_20260717_095305_735f0e22…` · `עמוד אבקות = PRODUCT PHOTOS/hf_20260727_113138_1cc0f989…` · `עמוד מוצרים משלימים = hf_20260717_091636_5647e772…` · `שער = hf_20260717_103013_6f6ccba2…` (השער אושר ע"י טום בכתב — נשאר `מאושר-טום`).

- [ ] **Step 2: Write the warehouse**

```markdown
# מחסן נכסי שיווק ועיצוב

> פורמט ותחזוקה: `docs/warehouses/README.md`. בעלים: `gt-assets-designer`.
> נזרע 2026-08-06 מסשן המחירון (רשומה: `docs/pricing/2026-08-06_customer_pricelist_pdf.md`).

## בקבוקי 1 ליטר — `AI YASTREBOVA/all bottles/` (דרופבוקס)

| מה | קובץ | דירוג | אומת |
|---|---|---|---|
| FRESH | `fresh.jpg` | מאושר-טום | 2026-08-06 |
| FRESH ללא סוכר | `fresh +.jpg` | מאושר-טום | 2026-08-06 |
| DETOX | `detox.jpg` | מאושר-טום | 2026-08-06 |
| DETOX ללא סוכר | `detox +.jpg` | מאושר-טום | 2026-08-06 |
| ENERGY | `energy.jpg` | מאושר-טום | 2026-08-06 |
| CALM | `calm.jpg` | מאושר-טום | 2026-08-06 |
| CONSCIOUSNESS | `consiusness.jpg` | מאושר-טום | 2026-08-06 |
| REVIVE | `revive.jpg` | מאושר-טום | 2026-08-06 |
| DESERTEA | `desert tea.jpg` | מאושר-טום | 2026-08-06 |
| NAMASTEA | `namastea.jpg` | מאושר-טום | 2026-08-06 |
| AMERICAN | `american.png` | מאושר-טום | 2026-08-06 |

## קרפים 500 מ"ל — אותה תיקייה

| מה | קובץ | דירוג | אומת |
|---|---|---|---|
| FRESH 500 | `fresh small.jpg` | מאושר-טום | 2026-08-06 |
| FRESH ללא סוכר 500 | `fresh small +.jpg` | מאושר-טום | 2026-08-06 |
| DETOX 500 | `detox small.jpg` | מאושר-טום | 2026-08-06 |
| DETOX ללא סוכר 500 | `detox small +.jpg` | מאושר-טום | 2026-08-06 |
| ENERGY 500 | `energy small.jpg` | מאושר-טום | 2026-08-06 |
| CALM 500 | `calm small.jpg` | מאושר-טום | 2026-08-06 |
| CONSCIOUSNESS 500 | `consiusness - small.jpg` | מאושר-טום | 2026-08-06 |
| REVIVE 500 | `revive small.jpg` | מאושר-טום | 2026-08-06 |
| DESERTEA 500 | `desert tea small.png` | מאושר-טום | 2026-08-06 |
| NAMASTEA 500 | `Namastea small.png` | מאושר-טום | 2026-08-06 |
| AMERICAN 500 | `American small.png` | מאושר-טום | 2026-08-06 |

## אבקות — `AI YASTREBOVA/CATALOG/MATCHA UBE HOJICHA/`

| מה | קובץ | דירוג | אומת |
|---|---|---|---|
| שקית מאצ'ה שחורה (פקשוט) | `PRODUCT PHOTOS/hf_20260727_104410_ac14498b-8746-4a34-a985-3fb1276f5104.png` | מאושר-טום | 2026-08-06 |
| שקית הוג'יצ'ה זהב (פקשוט) | `hf_20260727_092139_3a32c397-75f0-466e-af5e-3a9bae8f702c.png` | מאושר-טום | 2026-08-06 |
| שקית אובה לבנה (פקשוט) | `hf_20260727_092317_5c1a5972-9388-40d6-a547-1fa260ade5d1.png` | מאושר-טום | 2026-08-06 |
| סטיל-לייף מאצ'ה (מטרפות+אייס+שקית) | `<שם הקובץ מצעד 1 — hash-verified>` | מאושר-טום | 2026-08-06 |
| התיקייה כולה — ~60 תמונות לייפסטייל של אבקות | `MATCHA UBE HOJICHA/` + `PRODUCT PHOTOS/` + `+ colors/` | טוב | 2026-08-06 |

## מחיות ODK — `AI YASTREBOVA/CATALOG/ODK/` (פקשוטים נקיים, ~3MB)

| מה | קובץ | דירוג | אומת |
|---|---|---|---|
| מנגו | `hf_20260720_155530_6c219095-573e-4980-b1b3-dfcf88456cfc.png` | מאושר-טום | 2026-08-06 |
| תות | `hf_20260720_155600_ba5475a0-6733-4ce1-ae17-a7029c6c37d9.png` | מאושר-טום | 2026-08-06 |
| אפרסק | `hf_20260720_155612_a56babef-528b-4c07-a31a-98c23eb31085.png` | מאושר-טום | 2026-08-06 |

## אביזרים — `AI YASTREBOVA/small products/`

| מה | קובץ | דירוג | אומת |
|---|---|---|---|
| קערת מאצ'ה | `hf_20260731_140406_2886352a-1adb-4429-b126-a65bad4e70eb.png` | מאושר-טום | 2026-08-06 |
| מקציף מאצ'ה + ראשים | `hf_20260731_140349_dc6f231d-b3f8-4e71-9c86-73fa5eb76054.png` | מאושר-טום | 2026-08-06 |
| מטרפת במבוק + תוף | `hf_20260731_140415_6426b471-ebc5-4e84-a36d-21d275d9c3a4.png` | מאושר-טום | 2026-08-06 |
| כוס זכוכית 600 | `hf_20260731_140340_62fff06f-ccd5-4e2c-82a8-8b053b4f3dda.png` | מאושר-טום | 2026-08-06 |
| מעמד למטרפה | `hf_20260731_140443_5aa8238c-b8aa-4cb4-bf05-09fbdc569748.png` | מאושר-טום | 2026-08-06 |
| ג'יגר מודפס | `hf_20260731_140434_bfd2fef6-0093-448f-8cec-09244b5f3035.png` | מאושר-טום | 2026-08-06 |
| כף במבוק | `hf_20260731_140424_9ccd8292-2223-4ba7-b5e3-a2fcbcb51205.png` | מאושר-טום | 2026-08-06 |
| בקבוק מאצ'ה חום 500 | `hf_20260731_140358_e98677ba-3a75-4213-8242-d9c556e73a10.png` | מאושר-טום | 2026-08-06 |

## תמונות ראש-עמוד ולייפסטייל — `AI YASTREBOVA/CATALOG/2 slide/`

| מה | קובץ | דירוג | אומת |
|---|---|---|---|
| שער המחירון (בחירת טום) | `hf_20260717_103013_6f6ccba2-eba5-4411-bcac-1a75f9e9df3b.png` | מאושר-טום | 2026-08-06 |
| ראש עמוד תמציות (V3) | `<מצעד 1>` | מאושר-טום | 2026-08-06 |
| ראש עמוד אבקות (V3, מתיקיית האבקות) | ר' סעיף אבקות — הסטיל-לייף | מאושר-טום | 2026-08-06 |
| ראש עמוד מוצרים משלימים (V3) | `<מצעד 1>` | מאושר-טום | 2026-08-06 |
| התיקייה כולה — 17 תמונות לייפסטייל בקבוקים+כוסות | `CATALOG/2 slide/` | טוב | 2026-08-06 |
| בקבוקים על מדף — קיר שמנת ("המדף") | `AI YASTREBOVA/all bottles/` קבצי `* 2.jpg` | טוב | 2026-08-06 |

## לוגו, פונטים, פלטה, DNA

| מה | נתיב | דירוג | אומת |
|---|---|---|---|
| לוגו gt שחור | דרופבוקס `Data Center/PRODUCTION 2/B-BAGEL-Tea-Programme/assets/gt-logo-black.png` | מאושר-טום | 2026-08-06 |
| לוגו gt ירוק-מותג (#263B18) | דרופבוקס `New/ARCHIVE/Previous-Session-2026-03-16/BRAND-IDENTITY/Logos/GT_Logo_Black.png` (הקובץ ירוק למרות השם) | מאושר-טום | 2026-08-06 |
| פונטים — Rubik 400/500/600/700 + Heebo 300/500, WOFF עברית מלאה | ריפו `docs/pricing/pricelist_pdf/fonts/` (+ שיטת ההורדה: `getfonts.py`, UA של Firefox 27) | מאושר-טום | 2026-08-06 |
| פלטה | נייר `#EFE6D6` · דיו `#241C15` · ירוק `#263B18` · קורל `#FA6E4D` · קו `#D8CCB4` · מעומעם `#7C6E58` | מאושר-טום | 2026-08-06 |
| DNA עיצובי | צילום full-bleed בראש עמוד + טקסט לבן עליו · Rubik לכל מודגש, Heebo 300 לשקט · שמות מוצרים בקפיטל מרווח · קו-שערה עושה את המבנה · ₪ קטן בקורל · RTL עם עמודות מחיר `direction:ltr` | מאושר-טום | 2026-08-06 |
| קטלוג מוצרים בקאנבה (מקור ה-DNA) | Canva design `DAHQrpThEBE` | מאושר-טום | 2026-08-06 |
| תיקיית קאנבה — פקשוטים 1L + ODK + אבקות | Canva folder `FAHRTt8KXZg` | טוב | 2026-08-06 |

## פערים ידועים (רשומות-שלילה)

| מה | מצב | אומת |
|---|---|---|
| ערכת מאצ'ה | אין תצלום בשום מקום — דרופבוקס/שופיפיי/קאנבה | 2026-08-06 |
| מאצ'ה 22 שקיות | קיימת רק תמונה זעירה 229px בשופיפיי — לא שמישה להדפסה | 2026-08-06 |
```

Replace the two `<מצעד 1>` markers with the hash-verified filenames from Step 1 (or the fallback names with `טוב`).

- [ ] **Step 3: Fix the pricelist record's band names**

In `docs/pricing/2026-08-06_customer_pricelist_pdf.md` §Structure, replace the three `hf…` band names with the verified ones from Step 1, and add one line under the table: `(שמות קבצי הבאנד אומתו ב-hash מול דרופבוקס 2026-08-06 — הגרסה הקודמת של הטבלה נשאה שמות מהזיכרון.)`

- [ ] **Step 4: Verify**

```bash
python3 - <<'PY'
import re, pathlib
s = pathlib.Path('docs/warehouses/marketing-assets.md').read_text()
rows = [l for l in s.splitlines() if l.startswith('|') and 'אומת' not in l and '---' not in l]
undated = [r for r in rows if not re.search(r'\d{4}-\d{2}-\d{2}', r)]
assert not undated, undated
assert '<מצעד 1>' not in s and '<שם הקובץ' not in s, 'unresolved markers'
print('rows:', len(rows), 'all dated, no markers')
PY
```
Expected: `all dated, no markers`.

- [ ] **Step 5: Commit**

```bash
git add docs/warehouses/marketing-assets.md docs/pricing/2026-08-06_customer_pricelist_pdf.md
git commit -m "docs(warehouses): seed marketing-assets from the pricelist session, band photos hash-verified"
```

---

### Task 3: Seed `catalog-truth.md`

**Files:**
- Create: `docs/warehouses/catalog-truth.md`

**Interfaces:**
- Consumes: format from Task 1; prices from `docs/pricing/2026-08-05_shopify_products_exvat.tsv`.
- Produces: the warehouse `gt-catalog-truth` (Task 5) owns; the price/product source `gt-assets-designer` is required to read.

- [ ] **Step 1: Write the file**

```markdown
# מחסן אמת קטלוגית — מה אנחנו באמת מוכרים

> פורמט: `docs/warehouses/README.md`. בעלים: `gt-catalog-truth`.
> **הכלל: ACTIVE בשופיפיי הוא רמז. הקובץ הזה הוא האמת.**
> מקור מחירים: `docs/pricing/2026-08-05_shopify_products_exvat.tsv` (ללא מע"מ) —
> המחסן לא ממציא מחיר, הוא מצביע. נזרע 2026-08-06 מהמחירון המאומת (V3, 0 סטיות).

## תמציות תה — ליטר ₪65 · 500 מ"ל ₪33 (ללא מע"מ)

| מוצר | SKU ליטר | SKU 500 מ"ל | מקור | אומת |
|---|---|---|---|---|
| FRESH | GT-HIB-LOW-1L | GT-HIB-LOW-0.5L | TSV | 2026-08-06 |
| FRESH ללא סוכר | GT-HIB-FRE-1L | GT-HIB-FRE-0.5L | TSV | 2026-08-06 |
| DETOX | GT-LUI-LOW-1L | GT-LUI-LOW-0.5L | TSV | 2026-08-06 |
| DETOX ללא סוכר | GT-LUI-FRE-1L | GT-LUI-FRE-0.5L | TSV | 2026-08-06 |
| ENERGY | GT-LEM-LOW-1L | GT-LEM-LOW-0.5L | TSV | 2026-08-06 |
| CALM | GT-CHA-LOW-1L | GT-CHA-LOW-0.5L | TSV | 2026-08-06 |
| CONSCIOUSNESS | GT-JAS-LOW-1L | GT-JAS-LOW-0.5L | TSV | 2026-08-06 |
| REVIVE | GT-SEN-LOW-1L | GT-SEN-LOW-0.5L | TSV | 2026-08-06 |
| DESERTEA | GT-INF-DES-1L | GT-INF-DES-0.5L | TSV | 2026-08-06 |
| NAMASTEA | GT-MAS-CHA-1L | GT-MAS-CHA-0.5L | TSV | 2026-08-06 |
| AMERICAN | — אין SKU פעיל — | — | טום 2026-08-05 (₪65/₪33) | 2026-08-06 |

## מאצ'ה ואבקות

| מוצר | SKU | ₪ ללא מע"מ | מקור | אומת |
|---|---|---|---|---|
| מאצ'ה שיזואוקה 500 גרם | GT-SHI-CER-500 | 590 | TSV | 2026-08-06 |
| מאצ'ה שיזואוקה 22×18 גרם | GT-SHI-CER-18*22 | 590 | TSV | 2026-08-06 |
| HOJICHA 500 גרם | — אין SKU פעיל — | 375 | טום 2026-08-05 | 2026-08-06 |
| UBE 1 ק"ג | UBE-POWDER-1-KG | 340 | TSV | 2026-08-06 |
| UBE 500 גרם | UBE-POWDER-0.5-KG | 175 | TSV | 2026-08-06 |
| ערכת מאצ'ה | GT-MAT-KIT | 170 | TSV | 2026-08-06 |

## מחיות פרי

| מוצר | SKU | ₪ | מקור | אומת |
|---|---|---|---|---|
| SMOOTHIE מנגו 1 ל' | GT-ODK-MAN-1 | 60 | TSV | 2026-08-06 |
| SMOOTHIE תות 1 ל' | GT-ODK-STR-1 | 60 | TSV | 2026-08-06 |
| SMOOTHIE אפרסק 1 ל' | GT-ODK-PEA-1 | 60 | TSV | 2026-08-06 |

## מוצרים משלימים

| מוצר | SKU | ₪ | מקור | אומת |
|---|---|---|---|---|
| קערת מאצ'ה קרמית | AP-BWL-MAT | 118 | TSV | 2026-08-06 |
| מקציף מאצ'ה חשמלי | AP-FRO-MAT | 100 | TSV | 2026-08-06 |
| מטרפת במבוק | AP-WHK-MAT | 37 | TSV | 2026-08-06 |
| כוס זכוכית 600 מ"ל | AP-CUP-MAT-600 | 30 | TSV | 2026-08-06 |
| מעמד למטרפה | AP-STA-MAT | 25 | TSV | 2026-08-06 |
| כוס מדידה | GT-GLA-CUP | 20 | TSV | 2026-08-06 |
| כף מדידה במבוק | AP-SCO-MAT | 11 | TSV | 2026-08-06 |
| בקבוק מאצ'ה 500 מ"ל | GT-MAT-BTL-RU | 10 | TSV | 2026-08-06 |

## רשומות-שלילה — ACTIVE בשופיפיי, לא נמכר / לא בקטלוג

| מוצר | SKU | קביעת טום (2026-08-06, סשן המחירון) | אומת |
|---|---|---|---|
| GT Elita מאצ'ה פחית 30 גרם | GT-SHI-CER-30 | "זה לא אמור להיות שם" | 2026-08-06 |
| מאצ'ה שיזואוקה 50 גרם | GT-SHI-CER-50 | "אנחנו לא מוכרים אותה" | 2026-08-06 |
| מקציף קוקטיילים | GTCFR-GTCOC-FRO | ירד מהמחירון | 2026-08-06 |
| קנקן נפוליטן עם מסננת | AP-JUG-NEA | "לא רלוונטי" | 2026-08-06 |

> הערת תחולה: הקביעות חלות על **הקטלוג ללקוחות**. האם המוצרים האלה נמכרים
> בערוצים אחרים (אתר-צרכן, מקרה חד-פעמי) — שאלה פתוחה לסריקת הדריפט הראשונה.
```

- [ ] **Step 2: Verify — every SKU row cross-checks against the TSV**

```bash
python3 - <<'PY'
import re, pathlib
tsv = {}
for l in pathlib.Path('docs/pricing/2026-08-05_shopify_products_exvat.tsv').read_text().splitlines():
    p = l.split('\t')
    if len(p) >= 4 and not l.startswith('#'):
        try: tsv[p[0]] = float(p[3])
        except ValueError: pass
s = pathlib.Path('docs/warehouses/catalog-truth.md').read_text()
skus = re.findall(r'\b((?:GT|AP|UBE|GTCFR)[A-Z0-9*.\-]+)\b', s)
missing = [k for k in skus if k not in tsv]
assert not missing, f'SKUs not in TSV: {missing}'
for sku, price in re.findall(r'\| ((?:GT|AP|UBE)[A-Z0-9*.\-]+) \| (\d+) \|', s):
    assert tsv[sku] == float(price), f'{sku}: file {price} vs TSV {tsv[sku]}'
print('SKUs found:', len(set(skus)), '— all in TSV, all prices match')
PY
```
Expected: `all in TSV, all prices match`.

- [ ] **Step 3: Commit**

```bash
git add docs/warehouses/catalog-truth.md
git commit -m "docs(warehouses): seed catalog-truth — 28 sold rows + 4 reasoned negatives, TSV-cross-checked"
```

---

### Task 4: Agent charter — `gt-assets-designer`

**Files:**
- Create: `.claude/agents/gt-assets-designer.md`
- Modify: `REGISTRY.md` (add a `## Business agents (2)` section after the engineering agents table — Task 5 adds the second row to the same table)

**Interfaces:**
- Consumes: warehouses from Tasks 2–3.
- Produces: agent type `gt-assets-designer`, dispatchable by name from Messi's session (Task 6 cites it in the triage table).

- [ ] **Step 1: Write the agent file**

```markdown
---
name: gt-assets-designer
description: >-
  GT's assets & design agent — builds catalogs, pricelists, decks and visual
  assets to ~80% quality using ONLY registered warehouse assets and the design
  DNA. Dispatched by Messi's evening run or ad-hoc when Tom asks for a visual
  deliverable. Never contacts customers, never writes to Shopify, never invents
  a price or product — product/price truth comes from docs/warehouses/
  catalog-truth.md and docs/pricing/2026-08-05_shopify_products_exvat.tsv only.
tools: Read, Write, Edit, Glob, Grep, Bash
---

# gt-assets-designer — סוכן נכסים ועיצוב

צ'רטר עשרת השדות (ספק 2026-08-06 §5). וריאנט עסקי של `AGENT_TEMPLATE.md`.

| שדה | תוכן |
|---|---|
| עושה בפועל | קטלוגים, מחירונים, מצגות, נכסים ויזואליים — ברמת 80%, לפי ה-DNA שבמחסן |
| שעות | ריצות ערב (משוגר ע"י מסי) · אד-הוק כשטום מבקש |
| **במפורש לא** | ⊥ שולח ללקוחות · ⊥ כותב לשופיפיי · ⊥ ממציא מחיר/מוצר · ⊥ קונה/מתחייב · ⊥ merge · ⊥ deploy · ⊥ מיגרציית פרוד |
| מחליט לבד | בחירת נכסים מהמחסן, פריסה, טיפוגרפיה — בתוך ה-DNA |
| מחייב טום | שינוי DNA · שימוש בנכס שאין לו רשומת מחסן · כל דבר שיוצא ללקוח |
| מחליף | אין — מסי מדווח "לא בוצע" במייל הבוקר |
| קצב | לפי שיגור בלבד |
| שלושה כללי ברזל | (1) מספר רק ממקור אמת — `catalog-truth.md` + ה-TSV (2) נכס רק מהמחסן, או נרשם בו קודם עם תאריך (3) כל תוצר מסתיים בבלוק "מה חסר לי" מפורש — גם כשריק |
| ממשק נכנס | ספק שיגור ממסי (`messi/reference/dispatch.md`) + שני המחסנים |
| ממשק יוצא | תוצר בריפו (או scratchpad עם העתק-ריפו) + שורת דיווח: הצלחה/חסימה+סיבה |

## נתיבים מותרים (רשימה ממצה — נתיב ∉ כאן ⇒ ⊥ כתיב)

- `docs/pricing/**` (תוצרים ותיעוד שלהם) · `docs/warehouses/marketing-assets.md`
- scratchpad של הסשן · `git add` בנתיבים האלה + commit + push לענף הנוכחי

## תנאי עצירה

- נכס נדרש ואין לו רשומת מחסן ⇒ עצור, רשום ב"מה חסר לי", המשך בלי הנכס.
- מספר נדרש ואינו במקורות האמת ⇒ עצור את השורה, סמן `חסר-מקור` — ⊥ להמציא.
- כל תנאי עצירה של `CLAUDE.md` §Stop conditions ⇒ HALT + שורה רועשת למסי.

## תבנית עבודה מוכחת

מחירון V3: `docs/pricing/pricelist_pdf/build.py` (HTML→PDF, פונטים מוטמעים,
cutouts ב-`cut.py`, אימות מחירים מול TSV, שומר-גלישה). התחל ממנה, אל תמציא צנרת.
```

- [ ] **Step 2: Add the registry section**

In `REGISTRY.md`, immediately after the closing paragraph of the agents table ("Legacy ↔ new are additive pairs…"), insert:

```markdown
## Business agents (wave 1, 2026-08-06)

| Agent | Dispatched by | Write | Allowed write paths |
|---|---|---|---|
| `gt-assets-designer` | messi evening run / Tom ad-hoc | autonomous within paths | `docs/pricing/**`, `docs/warehouses/marketing-assets.md`, scratchpad |
```

- [ ] **Step 3: Verify**

Run: `head -12 .claude/agents/gt-assets-designer.md` — frontmatter has `name` + `description` + `tools`; `grep -c 'gt-assets-designer' REGISTRY.md` ≥ 1.

- [ ] **Step 4: Commit**

```bash
git add .claude/agents/gt-assets-designer.md REGISTRY.md
git commit -m "agents: gt-assets-designer — business charter, warehouse-only assets, truth-only figures"
```

---

### Task 5: Agent charter — `gt-catalog-truth`

**Files:**
- Create: `.claude/agents/gt-catalog-truth.md`
- Modify: `REGISTRY.md` (second row in the Business agents table from Task 4)

**Interfaces:**
- Consumes: warehouse from Task 3.
- Produces: agent type `gt-catalog-truth`, cited by Task 6's triage + Sunday audit.

- [ ] **Step 1: Write the agent file**

```markdown
---
name: gt-catalog-truth
description: >-
  GT's catalog-truth agent — owns docs/warehouses/catalog-truth.md, the
  authoritative "what we actually sell" list. Reads Shopify (read-only) to
  detect drift between ACTIVE products and the warehouse, flags it in the
  morning email, and records Tom's corrections same-day. Never writes to
  Shopify, never sets prices, never removes a product without Tom's explicit
  word.
tools: Read, Write, Edit, Glob, Grep, Bash
---

# gt-catalog-truth — סוכן אמת קטלוגית

צ'רטר עשרת השדות (ספק 2026-08-06 §5).

| שדה | תוכן |
|---|---|
| עושה בפועל | מחזיק את `catalog-truth.md` · סורק דריפט מול שופיפיי (קריאה) · רושם תיקוני טום באותו יום |
| שעות | סריקת דריפט בריצת ערב של יום ראשון · עדכון מיידי בכל תיקון |
| **במפורש לא** | ⊥ כותב לשופיפיי · ⊥ קובע מחיר · ⊥ מוחק מוצר בלי הוראת טום מפורשת · ⊥ merge · ⊥ deploy · ⊥ מיגרציית פרוד |
| מחליט לבד | סימון דריפט · הוספת רשומה מאומתת-מקור |
| מחייב טום | כל קביעת "לא מוכרים X" · כל שינוי מחיר |
| מחליף | אין — מסי מדווח |
| קצב | שבועי + לפי אירוע |
| שלושה כללי ברזל | (1) ACTIVE בשופיפיי הוא רמז — המחסן הוא האמת (2) כל רשומה עם מקור ותאריך (3) דריפט מדווח — לעולם לא מתוקן בשקט בשופיפיי |
| ממשק נכנס | תיקוני טום · ה-TSV · קריאת שופיפיי (GraphQL, read-only) |
| ממשק יוצא | המחסן + בלוק דריפט למייל הבוקר |

## נתיבים מותרים (רשימה ממצה)

- `docs/warehouses/catalog-truth.md` בלבד · `git add` בו + commit + push לענף הנוכחי

## סריקת הדריפט (קנונית)

1. שופיפיי GraphQL: כל המוצרים `status:ACTIVE` + SKUs + מחירים (קריאה בלבד).
2. שלושה כיוונים: ACTIVE שאינו במחסן (לא כרשומת-חיוב ולא כשלילה) ·
   רשומת-חיוב שכבר ⊥ ACTIVE · מחיר שופיפיי ≠ מחיר המקור שהמחסן מצביע עליו.
3. פלט: בלוק "דריפט קטלוגי" עם ההמלצה — לעולם לא תיקון בשופיפיי.

## תנאי עצירה

- שופיפיי לא נגיש ⇒ `FAILURE` רועש בלוג מסי — ⊥ לדלג בשקט על הסריקה.
- כל תנאי עצירה של `CLAUDE.md` §Stop conditions ⇒ HALT + שורה רועשת.
```

- [ ] **Step 2: Add the registry row**

Append to the Business agents table from Task 4:

```markdown
| `gt-catalog-truth` | messi evening run (Sundays) / on correction | autonomous within paths | `docs/warehouses/catalog-truth.md` |
```

- [ ] **Step 3: Verify**

`grep -c 'gt-catalog-truth' REGISTRY.md` ≥ 1; frontmatter valid.

- [ ] **Step 4: Commit**

```bash
git add .claude/agents/gt-catalog-truth.md REGISTRY.md
git commit -m "agents: gt-catalog-truth — owns catalog-truth warehouse, read-only Shopify drift scan"
```

---

### Task 6: `mode=evening` — the 20:00 procedure + messi SKILL.md amendments

**Files:**
- Create: `.claude/skills/messi/reference/evening-run.md`
- Modify: `.claude/skills/messi/SKILL.md` (three surgical edits, exact strings below)

**Interfaces:**
- Consumes: agents from Tasks 4–5, warehouses from Tasks 2–3, dispatch protocol `reference/dispatch.md` (unchanged).
- Produces: the procedure the 20:00 trigger (Task 7) invokes by the words `mode=evening`.

- [ ] **Step 1: Write `reference/evening-run.md`**

```markdown
# mode=evening — ריצת 20:00 של מסי (משרד מסי)

> ספק: `docs/superpowers/specs/2026-08-06-agent-org-wave1-design.md`.
> טריגר self-bind אל תוך סשן משרד-מסי: `0 17 * * 0-4` UTC (20:00 IL קיץ;
> **חורף `0 18`** — נבדק בביקורת יום ראשון). הסשן מתמשך — הקונטקסט נשמר,
> והקונקטורים איתו. **⊥ להריץ מסשן טרי — אין לו קונקטורים (אומת 2026-08-06).**

## שלבים — כסדרם, בלי לדלג

### 1 · איסוף
- נושן: משימות פתוחות של טום — `בעל תפקיד` = תום (מנוע הסגירה, נעול טום
  2026-08-05). **בנוסף** ודא שכל משימה שנוצרת נושאת גם `אחראי` = טום —
  הוויוז מסננים לפי `אחראי` (ממצא חי 2026-08-06); בלעדיו טום לא רואה אותה.
- הזריקות של טום מהיום (בצ'אט של המשרד / `inbox-fallback.md` — נקז לפי
  `reference/dispatch.md` §inbox-fallback).
- פרויקטים רצים: PRs פתוחים של הענפים החיים, שורות `[!]` מהלוג של אתמול,
  משימות המשך שנרשמו בריצה קודמת.

### 2 · סיווג — כל משימה לתחום
| תחום | יעד |
|---|---|
| נכסים / עיצוב / קטלוגים / מצגות | `gt-assets-designer` |
| קטלוג / מוצרים / מחירים / "לא מוכרים" | `gt-catalog-truth` |
| ייצור / רכש / משלוחים | הסקילים הקיימים (guardian, plan-production-14d, procurement-planning, daily-delivery-dispatch) — ⊥ לשגר ריצה כפולה אם רוטינת הבוקר שלהם ממילא תרוץ; לרשום "יטופל ברוטינת הבוקר" |
| קוד / סכימה / פורטל | `AI_BRAIN_ROUTER.md` — ליין, ⊥ כאן |
| אחר | מסי עצמו, או שאלה מרוכזת לטום במייל הבוקר |

### 3 · שיגור
לפי `reference/dispatch.md` בדיוק: ספק לפני שיגור · done-criterion מכני
וגבולות מילוליים לכל ספק כותב · אחד-אחד (`[~]` יחיד) · `[!]` אחרי 45 דק'.
סוכן עם צ'רטר (`gt-assets-designer` / `gt-catalog-truth`) משוגר **בשמו** —
הצ'רטר הוא הזהות; הספק מוסיף את המשימה, ⊥ מחליף את הצ'רטר.
עבודת קונקטורים (דרופבוקס/קאנבה/נושן/שופיפיי/ג'ימייל) — **בתוך הסשן בלבד**.
עבודת ריפו טהורה — מותר סשן-ילד ענן.
יעד: תוצרי 80%. תוצר תקוע ⊥ מושלם בכוח — `[!]` + סיבה, וזה מופיע בבוקר.

### 4 · הלו"ז למחר → קלנדר
1. קרא את יומן מחר (קריאה): פגישות קיימות = מסלע — ⊥ זז.
2. בנה בלוקים מהמשימות והפרויקטים, לפי `docs/ceo/reference/luz_rules.md`
   ואילוצי האנשים (מיידן לפני 8:00 · עדי לפני 10:00 · דורין אחרי 9:00 ·
   רביעי = יום התכנון · ⊥ שישי/שבת).
3. כתוב אוטונומית דרך Google Calendar MCP: כותרת מתחילה `[cos-os] ` תמיד,
   `Asia/Jerusalem`. עדכון/מחיקה — רק אירועים שכותרתם מתחילה `[cos-os]`.
   (הכרעת טום 2026-08-06, ספק §2.4+§2.7 — גובר על "מסי ⊥ כותב יומן" הישן.)

### 5 · חימוש מייל הבוקר
`send_later` ל-06:25 IL עם הודעה: "מייל הבוקר של מסי — הרכב ושלח לפי
evening-run.md §6". (הרכבה בבוקר, לא בערב — כדי לתפוס תוצרים שהסתיימו
בלילה ושינויי קלנדר מאוחרים.)

### 6 · מייל הבוקר (הערת ה-06:25)
מרכיב HTML RTL קצר: **תוצרי הלילה** (קישורים) · **מה נתקע ולמה** (כל `[!]`)
· **דריפט/התרעות** · **שאלות לטום** (מרוכזות) · **הלו"ז של היום**.
שולח **באמת** דרך תרחיש Make ‎6439326 — `scenarios_run` עם
`data = {"subject": …, "html": …}` (נשלח ל-tom@gteveryday.com; הוכח 2026-08-06).
`status:1` = נשלח. כשל ⇒ שורת `FAILURE` בלוג + ניסיון שני; כשל כפול ⇒
push לצ'אט של טום.

### 7 · לוג — כל ריצה, גם ריקה
`docs/ceo/messi/<YYYY-MM-DD>.md` לפי `reference/dispatch.md`, בתוספת שורת
אירוע אחת: `EVENING <HH:MM> dispatched <N> · done <M> · failed <K>` (או
`EVENING <HH:MM> empty` כשאין כלום). קומיט+push (`SKILL.md` §ביצוע 7).
**ריצה בלי שורת EVENING בקומיט = הריצה לא קרתה.**

## ביקורת יום ראשון (בתוך ריצת הערב של יום ראשון)
1. `gt-catalog-truth` — סריקת הדריפט השבועית.
2. מחסנים: רשומות שאומתו לפני >30 יום ⇒ `⚠ לאימות` בקובץ.
3. טריגרים: `list_triggers` — הטריגר של הערב ירה אתמול-שלשום? שורות
   EVENING קיימות? חסר ⇒ שורה רועשת במייל הבוקר.
4. שעון: אם ישראל עברה שעון ⇒ עדכן את ה-cron (`update_trigger`) ורשום.

## יחסים לריטואלים הקיימים
- day-close (17:00) ממשיך כרגיל **מלבד** בניית הלו"ז ושער G5 שלה — הלו"ז
  עבר לריצת הערב (הכרעת טום 2026-08-06). day-open (07:30) קורא את אותו לוג.
- רוטינות הבוקר של הגרדיאן — ללא שינוי; ריצת הערב ⊥ מריצה אותן.
```

- [ ] **Step 2: Three surgical edits to `SKILL.md`**

Edit 1 — the description frontmatter: after the sentence about `mode=checkpoint` (`…one targeted push when something slips.`) insert:

```
Also mode=evening (20:00 trigger): the nightly run — gather open tasks,
dispatch to the professional agents, build tomorrow's calendar, arm the
06:25 morning email (reference/evening-run.md).
```

Edit 2 — §גבולות, replace the line:

```
- **יומן: מסי ⊥ כותב, גם ⊥ `[cos-os]`.** בקשת לו"ז/בלוק ⇒ נאספת ומנותבת לשער G5
  של `chief-of-staff-daily` (day-close). הכתיבה קורית שם, אחרי אישור טום.
```

with:

```
- **יומן: מסי כותב אוטונומית — בלוקים שכותרתם מתחילה `[cos-os]` בלבד** (טום
  2026-08-06, ספק agent-org-wave1 §2.4+§2.7; מחליף את "מסי ⊥ כותב יומן").
  אירועים בלי הקידומת — קריאה בלבד, ⊥ זז, ⊥ נערך, ⊥ נמחק. הכתיבה קורית
  בריצת הערב (`reference/evening-run.md` §4); זריקת-לו"ז ביום מחכה לערב
  אלא אם טום אמר "עכשיו".
```

Edit 3 — §ביצוע rule 6, replace:

```
6. לא-ליום (ארוך/דורש שקט) ⇒ הצעה לתור הלילה ב-day-close. ⊥ מנוע לילה משלנו.
```

with:

```
6. לא-ליום (ארוך/דורש שקט) ⇒ לתור ריצת הערב 20:00 (`reference/evening-run.md`) —
   זה מנוע הלילה שלנו מאז 2026-08-06; ⊥ תור לילה נפרד ב-day-close.
```

And append to the modes area, after the whole `## mode=checkpoint` section:

```
## mode=evening — 20:00, א'–ה'

הבעלים של הפרוצדורה: `reference/evening-run.md`. ⊥ לנסח כאן מחדש.
טריגר self-bind אל סשן משרד-מסי (⊥ סשן טרי — אין קונקטורים).
```

- [ ] **Step 3: Verify**

```bash
grep -c 'evening' .claude/skills/messi/SKILL.md          # ≥3
grep -c 'cos-os' .claude/skills/messi/SKILL.md           # ≥2, ולא נשארה שורת "מסי ⊥ כותב"
grep -c '⊥ מנוע לילה משלנו' .claude/skills/messi/SKILL.md # 0
test -f .claude/skills/messi/reference/evening-run.md && echo OK
```

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/messi/SKILL.md .claude/skills/messi/reference/evening-run.md
git commit -m "messi: mode=evening — 20:00 loop, autonomous [cos-os] calendar, morning email (Tom 2026-08-06)"
```

---

### Task 7: Push, PR, merge, then bind the 20:00 trigger

**Files:** none (runtime).

**Interfaces:**
- Consumes: everything above, merged to main (the trigger's session reads main).
- Produces: Routine `messi-evening` bound to the Messi HQ session.

- [ ] **Step 1: Push and open the PR**

```bash
git push -u origin claude/gt-everyday-catalog-tasks-qellwd
```
Open a draft PR to main titled `agents+messi: wave 1 — warehouses, two business agents, mode=evening`; body lists the six commits; mark ready + squash-merge (docs-only, verified — standing authorization).

- [ ] **Step 2: Choose the HQ session and bind the trigger**

**The HQ session for wave 1 is the session executing this plan** — it is interactively authenticated and demonstrably holds every needed connector (Canva, Dropbox, Notion, Gmail, Make, Shopify, Google Calendar, GitHub). Do NOT create a fresh session for this (`create_session` children are not interactively authenticated — untested connector risk; fresh-Routine sessions are proven broken).

Call `create_trigger` (self-bind — no `persistent_session_id`, no `create_new_session_on_fire`):

```
name: "messi-evening"
cron_expression: "0 17 * * 0-4"
prompt: "mode=evening — ריצת הערב של מסי. פעל לפי gt-factory-os-production-brain/.claude/skills/messi/reference/evening-run.md, על main העדכני (git fetch קודם). זו ריצה מתוזמנת: בצע את כל השלבים 1–7 כסדרם, כולל קומיט+push של הלוג וחימוש מייל הבוקר. כישלון רועש — אין יציאה בשקט."
```

- [ ] **Step 3: Verify the binding**

`list_triggers` → a row named `messi-evening`, enabled, `next_run_at` = the coming Sun–Thu 17:00 UTC, bound to this session (persist). Record the `trig_…` id in the day's messi log.

- [ ] **Step 4: Log line + commit**

Append to `docs/ceo/messi/<today>.md`: `EVENING-SETUP <HH:MM> trigger <trig_id> bound · mode=evening live`, commit+push (explicit path).

---

### Task 8: Supervised dry-run (acceptance test)

**Files:** none (runtime). This is the spec's success gate in miniature.

- [ ] **Step 1: Seed a real test task**

Ensure at least one real open task exists for the run (e.g., the existing Notion task "שופיפיי — סדר עומק + תכנית" or a small assets task Tom threw). If none, add one Notion task: "טסט ריצת ערב — לבנות עמוד דוגמה מהמחסן" (delete-after per Tom's archiving rule — mark completed after the test).

- [ ] **Step 2: Fire**

`fire_trigger` on `messi-evening` with text: "ריצת בדיקה מפוקחת — בצע את הלולאה המלאה עכשיו; ה-send_later של המייל יכוון ל-+10 דקות במקום 06:25, חד-פעמית."

- [ ] **Step 3: Acceptance checklist — all five, mechanically**

1. `docs/ceo/messi/<today>.md` carries an `EVENING …` line **and is pushed** (`git log origin/main -- docs/ceo/messi/` or the session branch).
2. ≥1 dispatch ran with a packet that satisfies dispatch.md law 2 (grep the log for `גבולות` + `done-criterion`).
3. A `[cos-os]` block exists in tomorrow's calendar (list_events) — and no non-`[cos-os]` event was modified.
4. Tom received the email (Make `scenarios_run` returned `status:1`; Tom confirms receipt).
5. A deliverable link exists in the log (or a reasoned `[!]`).

- [ ] **Step 4: Fix-forward and report**

Anything failing ⇒ fix in this session, re-fire once. Then report to Tom: the five checks with their evidence, the trigger id, and what the first real 20:00 run will pick up. Mark the test Notion task completed.

---

## Self-Review (done at plan-writing time)

- **Spec coverage:** §2 decisions → Tasks 6–7 (loop, calendar, email), 2–3 (warehouses), 4–5 (agents), 8 (success gate); §3 seams/noisy-failure → evening-run §7 + dispatch law reuse; §7 runtime constraint → Task 7 Step 2; §8 Sunday audit → evening-run §ביקורת; §9 out-of-scope respected (no engineering-agent edits beyond additive registry section, no Shopify writes anywhere).
- **Placeholders:** the two `<מצעד 1>` markers in Task 2 are deliberate build-time inputs produced by Step 1 of the same task and asserted absent by Step 4's script. No TBDs elsewhere.
- **Type/name consistency:** agent names `gt-assets-designer`/`gt-catalog-truth` identical across Tasks 4, 5, 6; warehouse filenames identical across Tasks 1–6; trigger name `messi-evening` identical across Tasks 7–8.
```
