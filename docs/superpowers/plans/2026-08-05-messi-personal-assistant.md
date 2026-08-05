# Messi Personal Assistant — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build מסי — Tom's personal assistant skill (task front door + hermetic-closure engine) on top of the CoS v2 foundation, and take the whole system live.

**Architecture:** New skill `.claude/skills/messi/` beside the two CoS v2 ritual skills, all sharing `docs/ceo/reference/` contracts. Notion stays sole master for tasks/projects (one schema addition: `תאריך התחלה`). Closure enforced at three points: 13:00 checkpoint trigger, day-close blocking gate, day-open carry display. Execution is go-gated, one-at-a-time, logged to `docs/ceo/messi/<date>.md`.

**Tech Stack:** Claude Code skills (markdown), Notion MCP, Google Calendar MCP, Claude-Code-Remote triggers (cron, fresh-session), git.

**Spec:** `docs/superpowers/specs/2026-08-05-messi-personal-assistant-design.md` (approved by Tom 2026-08-05).

## Global Constraints

- Branch: `claude/personal-assistant-scope-fmbhc2` only. PR ‎#102 already exists — update it, never open a second one.
- Hebrew with Tom, compressed; SQL/code in English.
- ⊥ `git add -A` / `git add .` — explicit paths always (brain stop-condition 5).
- G1–G8 locked (spec §2): Notion = master; registry = derived mirror; two ritual skills stay separate; night engine only via day-close approval; calendar writes only `[cos-os]` after approval.
- Notion traps: `בוצע` is a button — mark done via `תאריך השלמה` · `אחראי` is ⊥ ownership truth (`בעל תפקיד` is) · no due dates on Friday/Saturday · no bulk updates without approval · archive > delete, deletion only with Tom approval.
- Fail loud (V9): source unavailable ⇒ say "לא זמין" + reason. Never invent a number.
- Evidence culture: every PASS states files changed + checks N/N. "It should work" ⊥ evidence.
- Employee messages = drafts for Tom only. Never send directly.
- Skill descriptions in English with Hebrew trigger phrases quoted (house convention, see `daily-ops-guardian`).

## File Structure

| Path | Action | Responsibility |
|---|---|---|
| (merge) `docs/ceo/**`, `.claude/skills/chief-of-staff-daily/`, `.claude/skills/weekly-opening/` | merged in from `origin/claude/cfo-not-ceo-6cpsxi` | CoS v2 foundation |
| `docs/ceo/reference/people_rhythm.md` | create | people constraints + weekly rhythm (ported from task-companion OPERATING-GUIDE) |
| `docs/ceo/reference/notion_contract.md` | modify | + `תאריך התחלה` + messi query recipes |
| `docs/ceo/reference/state_contract.md` | modify | + loops row + messi-execution row |
| `.claude/skills/messi/SKILL.md` | create | front door: triage, ack, go-dispatch, checkpoint mode |
| `.claude/skills/messi/reference/dispatch.md` | create | mini-spec template, one-at-a-time queue, log format, fallback inbox |
| `.claude/skills/chief-of-staff-daily/SKILL.md` | modify | day-close closure gate + day-open carried loops |
| `docs/ceo/messi/` | runtime | daily execution logs + `inbox-fallback.md` (created on first use, not in this plan) |

---

### Task 1: Merge the CoS v2 foundation (Phase 0a)

**Files:**
- Merge: `origin/claude/cfo-not-ceo-6cpsxi` → `claude/personal-assistant-scope-fmbhc2`

**Interfaces:**
- Produces: `docs/ceo/reference/{notion_contract,luz_rules,verification,state_contract}.md`, `docs/ceo/{registry.md,dashboard.html,weeks/2026-08-02.md}`, `.claude/skills/{chief-of-staff-daily,weekly-opening}/SKILL.md` — every later task depends on these paths existing.

- [ ] **Step 1: Fetch and verify the source branch tip**

```bash
cd /home/user/gt-factory-os-production-brain
git fetch origin claude/cfo-not-ceo-6cpsxi
git log -1 --format='%h %s' origin/claude/cfo-not-ceo-6cpsxi
```
Expected: `2b3d68c Give the dashboard a visual identity of its own: ...`. Different hash ⇒ HALT, the branch moved — re-verify mergeability with `git merge-tree --write-tree HEAD origin/claude/cfo-not-ceo-6cpsxi` before continuing.

- [ ] **Step 2: Merge (no-ff, keep history legible)**

```bash
git merge --no-ff origin/claude/cfo-not-ceo-6cpsxi -m "merge: CoS v2 foundation (chief-of-staff-daily, weekly-opening, docs/ceo contracts) from claude/cfo-not-ceo-6cpsxi

Never merged to main; verified clean merge. Foundation for messi per
docs/superpowers/specs/2026-08-05-messi-personal-assistant-design.md."
```
Expected: clean merge, no conflict markers. Conflict ⇒ HALT (was verified clean 2026-08-05; something changed — inspect, do not force).

- [ ] **Step 3: Verify the foundation files landed**

```bash
for p in docs/ceo/reference/notion_contract.md docs/ceo/reference/luz_rules.md \
         docs/ceo/reference/verification.md docs/ceo/reference/state_contract.md \
         docs/ceo/registry.md docs/ceo/weeks/2026-08-02.md \
         .claude/skills/chief-of-staff-daily/SKILL.md .claude/skills/weekly-opening/SKILL.md; do
  test -f "$p" && echo "OK  $p" || echo "MISSING $p"
done
```
Expected: 8× `OK`, 0× `MISSING`.

- [ ] **Step 4: Push**

```bash
git push -u origin claude/personal-assistant-scope-fmbhc2
```

---

### Task 2: Port people & rhythm into the shared core (Phase 0b)

**Files:**
- Create: `docs/ceo/reference/people_rhythm.md`

**Interfaces:**
- Consumes: `origin/claude/meeting-notes-five-initiatives-r39qbn:docs/companion/OPERATING-GUIDE.md` (source of the ported facts).
- Produces: `docs/ceo/reference/people_rhythm.md` — messi SKILL.md (Task 4) and the rituals reference it by this exact path.

- [ ] **Step 1: Extract the source**

```bash
git show origin/claude/meeting-notes-five-initiatives-r39qbn:docs/companion/OPERATING-GUIDE.md > /tmp/claude-0/-home-user/9adc1070-7a1d-5a76-bf82-140a14ffa837/scratchpad/operating-guide.md
```

- [ ] **Step 2: Write `docs/ceo/reference/people_rhythm.md`**

Structure (port sections 1–2 of the source; each fact carried verbatim unless a freshness check overrides it):

```markdown
# אנשים וקצב — ליבה משותפת CoS

> נפרד מ-luz_rules: שם חוקי בניית לו"ז; כאן העובדות על האנשים והשבוע.
> מקור: task-companion OPERATING-GUIDE (28.7), הועבר ואומת 2026-08-05.
> עובדה שהתיישנה ⇒ לעדכן כאן + לציין תאריך. ⊥ שני בתים לאותה עובדה.

## האנשים
<טבלת האנשים מהמקור: תום, מקסים, דניס, דורין, מיידן, עדי, אלכס, אדי+אמיר —
עמודות: מי · תפקיד · שעות · מה חשוב. כולל האזהרות: מיידן לא זמין מ-8:00;
עדי עד 10:00, זכר; דורין מ-9:00, ראשון מ-8:30; דניס נקודת כשל יחידה>

## אילוצי הלו"ז שנגזרים
מיידן לפני 8:00 · עדי לפני 10:00 · דורין אחרי 9:00 · דניס מ-6:00.

## השבוע
<טבלת השבוע מהמקור — יום התכנון רביעי (13:00 פגישת ייצור+רכש עם אלכס,
נעילה 15:00 — מאומת מול plan-production-14d) · חמישי ביצוע רכש ·
ימי מסלול: א'/ב'/ה' מרכז, ג' צפון, ד' דרום · ראשון-חמישי בלבד>
```

- [ ] **Step 3: Freshness checks (mechanical)**

```bash
grep -l "Wednesday" .claude/skills/plan-production-14d/SKILL.md && echo "planning-day=Wednesday CONFIRMED"
grep -rn "14:00" docs/plans/2026-08-02-tom-daily-schedule.md | head -3
```
Expected: Wednesday confirmed. Any contradiction between the source and current docs (e.g., meeting times changed by the 5.8 meeting) ⇒ current doc wins, note the delta with a date inside the file. Do NOT port section 3+ of the source (Notion wiring — `notion_contract.md` owns that; iron rules — split between `notion_contract.md` and `luz_rules.md`). Do NOT port `OPEN-TASKS.md` or references to it (retired by G1).

- [ ] **Step 4: Verify single-home rule**

```bash
grep -c "מיידן" docs/ceo/reference/people_rhythm.md   # ≥1
grep -c "8:00" docs/ceo/reference/luz_rules.md         # people-hour facts must NOT be duplicated into luz_rules
```
Expected: people facts live once, in `people_rhythm.md`. `luz_rules.md` unchanged in this task.

- [ ] **Step 5: Commit**

```bash
git add docs/ceo/reference/people_rhythm.md
git commit -m "feat(cos-core): people_rhythm.md — ported from task-companion, freshness-verified"
git push
```

---

### Task 3: Notion contract — live verify + `תאריך התחלה` + recipes (Phase 1)

> **COMPLETE 2026-08-05 — gate opened, ran live.** Notion connector authorized this session.
> **The committed recipes are the ones that ran**; three engine-forced corrections are recorded
> in `notion_contract.md` §מתכוני מסי §שלוש סטיות and mirrored into the spec:
> `last_edited_time`/`lastEditedTime` **do not exist** (`no such column`) ⇒ dropped from
> `open-loops`, "בלי תזוזה" now = `started ≤ now−3h` + no later event in today's log ·
> `created_time` ⇒ **`createdTime`** · every `NOT LIKE` wrapped in `COALESCE("שם",'')`
> because NULL-titled rows exist and `NULL NOT LIKE …` drops them silently.
> `[` is a plain character here (1/0/0) ⇒ **no `SUBSTR` fallback needed**.
> **Step 4's owner-predicate sanity gate did not fire and that is not a failure:**
> `due-today` = 9 rows with and without the predicate (delta 0 today). Live distribution is
> **68 open · 66 contain תום · 2 do not** — the plan's and spec's "~66 other-people's tasks
> would slip" was inverted; both documents corrected. **Task 8 must derive its delta from the
> run-day's live data, ⊥ expect a drop.**
> **Step 5's trial row could not be archived:** the Notion connector exposes no archive/trash
> tool for pages. It is marked complete (∴ absent from every recipe) and listed for Tom under
> §פריט בדיקה פתוח — `3b304298-2afb-8120-8602-ca6a4138f17b`. Archiving needs Tom regardless
> (`notion_contract.md` §גבולות).

**GATE: requires the Notion connector authorized in this environment.** Not authorized ⇒ STATUS: BLOCKED, tell Tom exactly: "קונקטור נושן לא מאומת — לאשר בהגדרות connectors ב-claude.ai, ואז נמשיך", and stop this task (later tasks 4–7 may proceed; tasks 8–10 may not).

**Files:**
- Modify: `docs/ceo/reference/notion_contract.md`

**Interfaces:**
- Consumes: task DB `collection://c6604298-2afb-8258-8026-87e9538244c3`, projects DB `collection://cb704298-2afb-8226-9b23-876996b62c5d` (IDs already in the contract).
- Produces: property `תאריך התחלה` (**datetime** — Tom's ruling 2026-08-05, task DB) + recipe names `RECIPE:open-loops`, `RECIPE:due-today`, `RECIPE:opened-today`, `RECIPE:dup-check` — Tasks 4, 6, 8 call these by name.

**Tom's rulings 2026-08-05 that this task encodes** (decided — do not reopen):
- **R1 — the closure engine is scoped to `בעל תפקיד` = תום ONLY.** Other people's tasks travel the existing waiting-on path (`notion_contract.md` §חישובים + the waiting-on recipe), never the slip list. Without the predicate every non-Tom open task (~66 across the team) is permanently "slipping".
- **R2 — `תאריך התחלה` is a DATETIME** (`is_datetime: 1`), not a date. Three rules need hour resolution: the ack prints `מ-<שעה>`, `⚠ פתוחות: X מ-09:40`, and the checkpoint slips on `באוויר ≥3 שעות בלי תזוזה`.
- **R3 — the long-term marker is a `[ארוך]` prefix in the task title.** No new Notion property (§10 keeps `תאריך התחלה` the only schema change). Excluded inside the recipe SQL, so an unmarked task is never exempt.

- [x] **Step 1: Prove live read on both DBs**

Query via the Notion MCP (querySql over each collection URL): `SELECT "שם" FROM "<collection>" LIMIT 3` for tasks and projects. Print the 3 real rows from each into the task output (evidence).
Expected: 6 real row names total. Failure ⇒ `assumption_failure`, HALT.

- [x] **Step 2: Add the property — as a DATETIME (R2)**

Attempt via the Notion API (database update adding `תאריך התחלה`, type Date **with "Include time" ON**). If the connector exposes no schema-update capability ⇒ ask Tom to add it manually in Notion (property name exactly `תאריך התחלה`, type Date, **Include time = ON**, on מסד המשימות) and wait for his "done".
Time-only-off is a silent failure: the ack would print `מ-<שעה>` with no hour and the ≥3h slip rule would have nothing to compare. Verify in Step 3 before writing the contract.

- [x] **Step 3: Write-and-revert probe (the contract's own protocol)**

1. Create task `בדיקת מסי — למחיקה` with `תאריך יעד` = next Sunday.
2. Set `תאריך התחלה` = **now, with an hour** (`{"date:תאריך התחלה:start":"<YYYY-MM-DDTHH:MM:00+03:00>", "date:תאריך התחלה:is_datetime":1}`). Re-read; verify **the hour survives** the round-trip, not just the date. Hour lost ⇒ the property is date-only ⇒ `assumption_failure`, HALT, back to Step 2.
3. Set `תאריך השלמה` = today. Re-read; verify.
4. Confirm `last_edited_time` is selectable in querySql on this DB (`SELECT "שם", last_edited_time FROM "<tasks>" LIMIT 1`) — `RECIPE:open-loops` depends on it for "בלי תזוזה". Not selectable ⇒ record the working substitute and fix the recipe before committing.
5. Archive the trial task (archive, ⊥ delete).
Expected: every write read back identical, hour included. Evidence: the re-read values printed.

- [x] **Step 4: Update `docs/ceo/reference/notion_contract.md`**

In the tasks-schema table add the row:
```markdown
| `תאריך התחלה` | date **(datetime)** | `date:תאריך התחלה:start` + `date:תאריך התחלה:is_datetime` = **1** — שעה חובה (טום 2026-08-05). נחתם רק ע"י מסי ברגע **השיגור בפועל** או "אני על זה" של טום. ריק+יש השלמה = בוצע בלי מעקב, תקין |
```
And in §מתכוני כתיבה add the stamp recipe (so messi never guesses the shape) — heading
`**חתימת התחלה** — notion-update-page · command: update_properties`, a `json` block holding
`{ "date:תאריך התחלה:start": "YYYY-MM-DDTHH:MM:00+03:00", "date:תאריך התחלה:is_datetime": 1 }`,
and one closing line: *שעה חובה — `is_datetime: 0` כאן = באג. השעה מזינה את `מ-<שעה>` באק;
"בלי תזוזה" נמדד ב-`last_edited_time`, ⊥ בשדה הזה.* Use the exact value the Step-3 probe
round-tripped, offset included.

Append a new section at the end:
```markdown
## מתכוני מסי — שאילתות חתומות (אומתו חי 2026-08-05)

> **תחולה: `בעל תפקיד` = תום בלבד** (טום 2026-08-05, R1). של אחרים ⇒ מסלול
> ה-waiting-on, ⊥ מנוע הסגירה. `dup-check` היא היחידה ללא הסינון — כפילות
> נבדקת מול **כל** הפתוחות, גם של אחרים.
> **`[ארוך]`** בתחילת השם = ארוך-טווח (R3) ⇒ מוחרג מ-open-loops ו-opened-today.
> **⊥ מ-due-today** — הפטור הוא מ**סריקת** הסגירה היומית, ⊥ מ**יעד** שטום קבע:
> `[ארוך]` עם `תאריך יעד` = היום באמת דחופה היום וצפה. שתיים מוחרגות, אחת ⊥.

### RECIPE:open-loops — באוויר עכשיו
SELECT "שם", "date:תאריך התחלה:start" AS started, last_edited_time AS last_move,
       "בעל תפקיד", url
FROM "collection://c6604298-2afb-8258-8026-87e9538244c3"
WHERE "date:תאריך התחלה:start" IS NOT NULL AND "date:תאריך השלמה:start" IS NULL
  AND "בעל תפקיד" LIKE '%תום%'
  AND "שם" NOT LIKE '[ארוך]%'
ORDER BY started;

### RECIPE:due-today — דחופות היום שלא נסגרו
SELECT "שם", "date:תאריך התחלה:start" AS started, "בעל תפקיד", url
FROM "collection://c6604298-2afb-8258-8026-87e9538244c3"
WHERE date("date:תאריך יעד:start") = date('now') AND "date:תאריך השלמה:start" IS NULL
  AND "בעל תפקיד" LIKE '%תום%';

### RECIPE:opened-today — נפתחו היום (בתחולת מנוע הסגירה)
SELECT "שם", "date:תאריך יעד:start" AS due, "date:תאריך התחלה:start" AS started, url
FROM "collection://c6604298-2afb-8258-8026-87e9538244c3"
WHERE date(created_time) = date('now') AND "date:תאריך השלמה:start" IS NULL
  AND "בעל תפקיד" LIKE '%תום%'
  AND "שם" NOT LIKE '[ארוך]%'
  AND ("date:תאריך יעד:start" IS NOT NULL OR "date:תאריך התחלה:start" IS NOT NULL);

### RECIPE:dup-check — כפילות לפני יצירה
SELECT "שם", url FROM "collection://c6604298-2afb-8258-8026-87e9538244c3"
WHERE "date:תאריך השלמה:start" IS NULL
  AND ("שם" LIKE '%<מילה1>%' OR "שם" LIKE '%<מילה2>%' OR "שם" LIKE '%<מילה3>%');
```

**כלל מילות-המפתח ל-`dup-check`:** 2–3 **מילות תוכן** מהזריקה — שם עצם/פועל
נושאיים (⊥ מילות קישור: של, את, עם, על, לי, כדי, היום, מחר). מחוברות ב-`OR`.
**כל שורה שחוזרת = חשד** ⇒ נאמר באק (`⚠ דומה: <שם> — אותה משימה?`) ולא נוצרת
שורה שנייה עד שטום אומר. אפס תוצאות ⇒ יוצרים בשקט. פחות מ-2 מילות תוכן
בזריקה ⇒ מילה אחת, ובאק נכתב שהבדיקה חלשה.

**`בעל תפקיד` הוא multi_select** — `LIKE '%תום%'` תופס גם משימה משותפת (תום+אלכס).
זה הכיוון הרצוי, והוא בדיוק המראה של מתכון ה-waiting-on הקיים (`NOT LIKE '%תום%'`).

Run each recipe once live; paste row counts as evidence. Sanity gates:
`open-loops` and `opened-today` must return **0 rows owned by anyone but תום**, and
`due-today` row count must drop versus the same query without the owner predicate
(that delta is the ~66-task false-slip bug, proven closed).
If `created_time` / `last_edited_time` / `date('now')` syntax fails against the live
engine, fix the recipe to the syntax that works and record the correction — the
committed recipe must be the one that ran. Same for the `[ארוך]` literal: verify
`NOT LIKE '[ארוך]%'` treats `[` as a plain character on this engine; it does not ⇒
use `SUBSTR("שם",1,6) <> '[ארוך]'` and record the substitution.

- [x] **Step 5: Commit**

```bash
git add docs/ceo/reference/notion_contract.md
git commit -m "feat(cos-core): notion contract — תאריך התחלה verified live + messi recipes"
git push
```

---

### Task 4: The messi skill (Phase 2a)

> **COMPLETE — as-built snapshot (2026-08-05).** The markdown embedded below is the text this task actually wrote and that was reviewed at the time. It was **subsequently amended** by the final-review fix wave (`41d46e5..aa72835`: R1 owner scope, R3 `[ארוך]`, R4 dispatch-time stamp, §גבולות, log commit+push). **The file on disk is authoritative.** Re-running this task verbatim would revert the fix wave.

**Files:**
- Create: `.claude/skills/messi/SKILL.md`

**Interfaces:**
- Consumes: `RECIPE:*` names (Task 3), `docs/ceo/reference/{people_rhythm,notion_contract,luz_rules,verification,state_contract}.md`, `docs/ceo/reference/dispatch.md` template names (Task 5).
- Produces: modes `throw` (default) and `checkpoint` — Task 10's trigger prompt invokes `checkpoint` by name; Task 6's ritual edits reference the ack contract.

- [ ] **Step 1: Write `.claude/skills/messi/SKILL.md`**

```markdown
---
name: messi
description: >-
  מסי — Tom's personal assistant: the always-open front door for tasks and the
  hermetic-closure engine, on top of the Chief-of-Staff OS. Use WHENEVER Tom
  addresses "מסי" by name, or throws anything to track/plan/schedule without it:
  "יש לי משימה", "תכניס למשימות", "תזכיר לי", "מה נשאר היום", "תבנה לי לוז",
  "אני על זה", "סגרתי את", a pasted voice-note transcript, or a whiteboard photo
  of todos. Also mode=checkpoint (13:00 trigger): silent open-loops sweep —
  quiet when clean, one targeted push when something slips. NOT for factory-os
  code/schema/portal work (router+executors), meeting summaries (meeting-summary),
  or the fixed rituals (chief-of-staff-daily, weekly-opening).
---

# מסי — הדלת הקדמית והסוגר

**טום = סמנכ"ל GT Everyday.** עברית דחוסה. עיקרון-העל: **סגירה הרמטית** —
מה שנפתח נסגר באותו יום או מוכרע במפורש; מה שמתחילים מסיימים לפני הבא.
מסי לוקח, ⊥ מחזיר שאלה. קריאה סבירה ⇒ מניח, כותב את ההנחה באק, ממשיך.

ליבה משותפת (לפי צורך): `docs/ceo/reference/` — `notion_contract.md` (סכימות,
RECIPE:*) · `people_rhythm.md` (אנשים, שעות, שבוע) · `luz_rules.md` · `verification.md`.
פרוטוקול שיגור ולוג: `reference/dispatch.md`.

## חוזה האק — תגובה אחת לכל זריקה, ≤4 שורות

```
✓ נקלט → נושן: <סיווג> · יעד <תאריך> · <בעל תפקיד>
⏱ ~<עלות> · חוסם: <מי/כלום>
⚠ פתוחות: <שם> מ-<שעה>          ← רק כשיש (RECIPE:open-loops)
▶ יכול לבצע עכשיו — גו?          ← רק כשמסי מסוגל
```

## טריאז' — חמישה סיווגים

| סיווג | לאן | כללים |
|---|---|---|
| משימה | נושן — אוטונומי (G2) | בעל תפקיד ברירת-מחדל תום · תמיד להציע יעד; בלי יעד רק על "מתישהו" · ⊥ שישי/שבת |
| פרויקט | נושן פרויקטים + משימות ראשונות | מבני ⇒ הצעה + גו |
| ארוך-טווח | משימה + סימון | רק טום מגדיר. פטור מסגירה-יומית |
| waiting-on | משימה על בעל התפקיד + checkback | מבשיל ב-day-open |
| רעיון | נושן בלי תאריך | someday. מחוץ למנוע הסגירה |

לפני יצירה: `RECIPE:dup-check`. חשד ⇒ נאמר באק, ⊥ שורה שנייה.
`תאריך התחלה` נחתם **רק** ע"י: גו של טום · "אני על זה"/"התחלתי". ⊥ ניחוש.
"סגרתי את X" ⇒ `תאריך השלמה` + ✓.

## ביצוע — גו ⇒ שיגור

1. חתום `תאריך התחלה`. 2. כתוב ספק ל-`docs/ceo/messi/<תאריך>.md` (פורמט:
`dispatch.md`; כותב ⇒ done-criterion מכני חובה). 3. שגר סוכן רקע מהספק בלבד.
4. **אחד-אחד**: ביצוע יחיד באוויר; השאר בתור גלוי בלוג.
5. סיום ⇒ ✓ + `תאריך השלמה` + לינק (G3). תקוע >45 דק'/כשל ⇒ שורה רועשת,
נשאר באוויר, עולה בשער 17:00.
6. לא-ליום (ארוך/דורש שקט) ⇒ הצעה לתור הלילה ב-day-close. ⊥ מנוע לילה משלנו.

גבולות = המוח, בלי ריכוך: לדג'ר/דגלים קפואים/הודעות לעובדים — לעולם ·
לקוחות/המוני/בלתי-הפיך — שאלה · יומן רק `[cos-os]` אחרי אישור (G5) ·
מחיקה בנושן — רק באישור, ארכוב עדיף.

## mode=checkpoint — 13:00, א'–ה'

1. נקז `docs/ceo/messi/inbox-fallback.md` לנושן אם קיים ולא ריק.
2. `RECIPE:open-loops` + `RECIPE:due-today` + לוג היום (ספקים שאושרו ולא רצו).
3. הכל במסלול ⇒ **שקט מוחלט**: שורת `CHECKPOINT <timestamp> clean` ללוג היום, זהו.
4. מחליק (באוויר ≥3 שעות בלי תזוזה · דחופה-היום שלא התחילה · אושר-ולא-רץ ·
   waiting-on שהבשיל) ⇒ push אחד: `מסי · N מחליקות: <שם> (<מצב>) · <שם> (<מצב>)`
   + אותה שורה ללוג. ⊥ מייל, ⊥ ריצת תיקון אוטונומית.
5. שגיאת סכימה/קונקטור ⇒ `assumption_failure`: push על הכשל עצמו + שורת
   `CHECKPOINT FAILURE <סיבה>` ללוג. ⊥ להיעלם בשקט.

## כשלים

נושן לא זמין בזריקה ⇒ הזריקה ⊥ אובדת: append ל-`docs/ceo/messi/inbox-fallback.md`
(`- [ ] <טקסט הזריקה המלא> · נזרק <timestamp>`) + שורה רועשת באק. ניקוז: הריצה
הבאה של מסי/צ'קפוינט/ריטואל. 3+ באוויר ⇒ התרעה חזקה באק, ⊥ חסימה.
```

- [ ] **Step 2: Mechanical verification**

```bash
wc -l .claude/skills/messi/SKILL.md   # < 120 body lines — lean, progressive disclosure
for s in "חוזה האק" "טריאז'" "mode=checkpoint" "RECIPE:open-loops" "inbox-fallback"; do
  grep -q "$s" .claude/skills/messi/SKILL.md && echo "OK $s" || echo "MISSING $s"; done
```
Expected: 5× OK.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/messi/SKILL.md
git commit -m "feat(messi): the personal-assistant skill — front door, triage, go-gated execution, checkpoint mode"
git push
```

---

### Task 5: Dispatch protocol reference (Phase 2b)

> **COMPLETE — as-built snapshot (2026-08-05).** The markdown embedded below is the text this task actually wrote and that was reviewed at the time. It was **subsequently amended** by the final-review fix wave (`41d46e5..aa72835`: mandatory `גבולות`, canonical `CHECKPOINT` grammar, `GATE` line, `verification.md` §א' reconciliation, R4 stamp rule). **The file on disk is authoritative.** Re-running this task verbatim would revert the fix wave.

**Files:**
- Create: `.claude/skills/messi/reference/dispatch.md`

**Interfaces:**
- Consumes: spec format from `docs/ceo/reference/verification.md` §א'.
- Produces: the log-file format of `docs/ceo/messi/<YYYY-MM-DD>.md` — Task 8's dry-run and the checkpoint mode read/write exactly this shape.

- [ ] **Step 1: Write `.claude/skills/messi/reference/dispatch.md`**

```markdown
# פרוטוקול שיגור — מסי

## הלוג היומי — `docs/ceo/messi/<YYYY-MM-DD>.md`

```
# מסי · <YYYY-MM-DD>

## תור
- [x] 1. <כותרת> · גו 10:20 · הושלם 10:41 · <לינק תוצר>
- [~] 2. <כותרת> · גו 11:05 · רץ
- [ ] 3. <כותרת> · גו 11:06 · ממתין (אחד-אחד)

## ספקים
### 1. <כותרת>
מטרה:        <משפט אחד — מה יהיה נכון אחרי>
ריפו/נתיבים: <מפורש; קריאה-בלבד ⇒ "אין כתיבה">
done-criterion: <מכני — פקודה/שאילתה + פלט צפוי. חובה לכל ספק כותב>
גבולות:      <מה ⊥ לגעת>
נושן:        <URL המשימה>

## אירועים
- CHECKPOINT 13:00 clean
- FAILURE 14:22 <ספק 2>: <סיבה, פלט גולמי מקוצר>
```

## חוקים
1. הספק נכתב **לפני** השיגור. סוכן הרקע מקבל את הספק בלבד — ⊥ את שיחת הצ'אט.
2. קריאה-בלבד ⇒ מותר בלי done-criterion; כותב ⇒ done-criterion מכני חובה
   (`verification.md` §א' — אותה טבלת ✅/❌).
3. אחד-אחד: משבצת `[~]` אחת לכל היותר. סיום/כשל ⇒ הבא בתור משוגר.
4. סיום ⇒ סימון `[x]` + `תאריך השלמה` בנושן + ✓ בצ'אט. כשל/45 דק' ⇒
   `FAILURE` באירועים + שורה רועשת בצ'אט + נשאר באוויר לשער 17:00.
5. הלוג הוא האמת על "אושר-ולא-רץ" — הצ'קפוינט משווה תור מול נושן.

## inbox-fallback — `docs/ceo/messi/inbox-fallback.md`
שורות `- [ ] <הזריקה המלאה> · נזרק <timestamp>`. ניקוז ⇒ סימון `- [x]` + שורת
הנושן שנוצרה. הקובץ ⊥ נמחק — היסטוריה זולה, אובדן יקר.
```

- [ ] **Step 2: Verify + commit**

```bash
grep -c "done-criterion" .claude/skills/messi/reference/dispatch.md   # ≥2
git add .claude/skills/messi/reference/dispatch.md
git commit -m "feat(messi): dispatch protocol — spec-before-launch, one-at-a-time, loud failures"
git push
```

---

### Task 6: Ritual amendments — closure gate + carried loops (Phase 3)

> **COMPLETE — as-built snapshot (2026-08-05).** The markdown embedded below is the text this task actually wrote and that was reviewed at the time. It was **subsequently amended** by the final-review fix wave (`41d46e5..aa72835`: gate reads `⊥ מסתיים`, waiting-on exempt, provisional `נגררת`, Thursday ⇒ Sunday, previous-business-day log, 🔒 approval slot, four-state backstop, canonical trigger prompts). **The file on disk is authoritative.** Re-running this task verbatim would revert the fix wave.
>
> **Step 4's grep string is superseded.** `נגררות מאתמול` returns 0 against the live file —
> the day-open heading now reads **`נגררות מיום העסקים הקודם`** (Sunday ⇒ Thursday, ⊥ Saturday),
> and the `שער הסגירה` alternation masks the miss into a false pass. The historical Step 4 block
> below is left as-built, on purpose. **Re-verify with the current strings instead:**
> `grep -n "שער הסגירה" … && grep -n "נגררות מיום העסקים הקודם" … && grep -n "^## שלב 6" …`
> — all three must hit; a zero on any one is a real regression.

**Files:**
- Modify: `.claude/skills/chief-of-staff-daily/SKILL.md`

**Interfaces:**
- Consumes: `RECIPE:opened-today`, `RECIPE:open-loops` (Task 3); messi log path (Task 5).
- Produces: day-close stage "שער הסגירה" — the blocking gate the whole design leans on.

- [ ] **Step 1: Locate anchors (the file arrived in Task 1's merge)**

```bash
grep -n "^## שלב\|^# מצב" .claude/skills/chief-of-staff-daily/SKILL.md
```
Expected: day-open stages 1–4 and day-close stages. Structure differs ⇒ adapt insertion points, keep the inserted text verbatim.

- [ ] **Step 2: day-open — insert after the "אבן היום" item in שלב 3**

```markdown
1.5. **נגררות מאתמול** — מיד אחרי האבן: `RECIPE:open-loops` + הלוג של אתמול
(`docs/ceo/messi/<אתמול>.md`). לכל נגררת: שם · באוויר מאז · החוסם שנרשם בשער.
אפס נגררות ⇒ שורת "לולאות: נקי". ניקוז inbox-fallback אם לא ריק.
```

- [ ] **Step 3: day-close — insert a new stage between the sweep stage and the schedule-building stage**

```markdown
## שלב 2.5 — שער הסגירה (חוסם)

`RECIPE:opened-today` + `RECIPE:open-loops` + תור הלוג של היום
(`docs/ceo/messi/<היום>.md`). כל לולאה מקבלת **אחת משלוש**:

| הכרעה | פעולה |
|---|---|
| נסגרה ✓ | `תאריך השלמה` בנושן (אם חסר) + לינק תוצר |
| ארוכת-טווח | רק במילים של טום. סימון מפורש + יעד חדש |
| נגררת | חוסם בשם + משבצת מחר (נכנסת ללו"ז של שלב 3) |

**אין קטגוריה רביעית.** הריטואל ⊥ ממשיך לשלב 3 עם לולאה לא-מוכרעת — כמו
ולידציית הלו"ז. הכרעות שדורשות את טום נכנסות להודעת האישור האחת של שלב 5.
בדיקת גיבוי: שורת `CHECKPOINT` של 13:00 קיימת בלוג היום; חסרה ⇒ לדווח
"צ'קפוינט 13:00 לא רץ" במייל הערב.
```

- [ ] **Step 4: Verify + commit**

```bash
grep -n "שער הסגירה\|נגררות מאתמול" .claude/skills/chief-of-staff-daily/SKILL.md
git add .claude/skills/chief-of-staff-daily/SKILL.md
git commit -m "feat(cos-daily): closure gate in day-close + carried loops in day-open"
git push
```

---

### Task 7: State contract rows (Phase 3)

> **COMPLETE — as-built snapshot (2026-08-05).** The two rows embedded below are the text this task actually wrote and that was reviewed at the time. They were **subsequently amended** by the final-review fix wave (`41d46e5..aa72835`), which closed this task's parked finding: `תאריך התחלה` is owned by messi alone, row 8 excludes it, row 12 is a query cut ⊥ a second home, and row 13's writer column now names the rituals' `inbox-fallback` drain and `GATE` lines. **The file on disk is authoritative.** Re-running this task verbatim would revert the fix wave.

**Files:**
- Modify: `docs/ceo/reference/state_contract.md`

- [ ] **Step 1: Add two rows to the main table** (after the "לו"ז / בלוקים" row)

```markdown
| **לולאות פתוחות / באוויר** | **נושן** — `תאריך התחלה`+`תאריך השלמה`+יעד (RECIPE:open-loops) | מסי · טום | צ'קפוינט 13:00 · שער day-close · day-open |
| **ביצועי מסי** (ספקים, תור, תוצאות, fallback) | `docs/ceo/messi/**` | מסי בלבד | צ'קפוינט · day-open/close · אימות בוקר |
```

- [ ] **Step 2: Verify + commit**

```bash
grep -c "מסי" docs/ceo/reference/state_contract.md   # ≥2
git add docs/ceo/reference/state_contract.md
git commit -m "feat(cos-core): state contract — loops live in Notion, messi execution in docs/ceo/messi"
git push
```

---

### Task 8: Live dry-run (Phase 4)

**GATE: Notion authorized (Task 3 done).** Not done ⇒ BLOCKED, same message as Task 3.

**Files:**
- Runtime evidence: `docs/ceo/messi/<today>.md` (created by the run itself)

**This task tests the POST-fix-wave semantics** (R1–R4, commits `41d46e5..aa72835`). The
skill files on disk are authoritative; the assertions below exist to prove the behavior
they describe actually happens end-to-end. Run on a weekday — Fri/Sat are silent and
Notion takes no due dates then.

**Trial rows — five, all named with the `בדיקת מסי —` prefix, all archived in Step 6:**

| # | `שם` | `בעל תפקיד` | purpose |
|---|---|---|---|
| T1 | `בדיקת מסי — ספירת פתוחות` | תום | the throw / execution path |
| T2 | `בדיקת מסי — שני בתור` | תום | R4: proves a queued item is ⊥ באוויר |
| T3 | `בדיקת מסי — מחליקה` | תום | slipping checkpoint (due today, never started) |
| T4 | `בדיקת מסי — של מקסים` | **מקסים** | **R1 negative control, both recipes** — due today, never closed, **and `תאריך התחלה` set ≥3h ago**. Non-Tom **and started** ⇒ it is a candidate row for `due-today` **and** for `open-loops`; the owner predicate is the only thing keeping it out of either. Leave it unstarted and dropping `LIKE '%תום%'` from `open-loops` would pass this task clean. |
| T5 | `[ארוך] בדיקת מסי — ארוכת טווח` | תום | **R3 negative control** — prefix exempts it |

- [ ] **Step 0: Baseline the live slip set — before creating any trial row**

Every count assertion below is a **delta**, never an absolute. Tom's real backlog legitimately
contains due-today-not-started and stale-in-the-air rows; an executor cannot tell those apart
from an R1 regression, so absolutes here would fail honestly-green runs and hide real ones.
Same technique as Task 3 Step 4's owner-predicate delta.

Run `RECIPE:open-loops` + `RECIPE:due-today` and evaluate the three checkpoint criteria
(`messi/SKILL.md` §mode=checkpoint 4) against today's log **as it stands now**. Record verbatim
in the task output:

- **B₀** = the resulting slip set — the **names**, not just the count. `|B₀|` may be 0 or 20; both fine.
- **L₀** = `RECIPE:open-loops` row count.

- [ ] **Step 1: Throw** — in-session, as Tom would: `מסי, משימת ניסיון: ספור כמה משימות פתוחות יש בנושן ותכתוב את המספר ללוג`. Follow SKILL.md exactly: `RECIPE:dup-check` → create T1 (due today, `בעל תפקיד` = תום) → 4-line ack.
Expected: Notion row exists (print its URL), `בעל תפקיד` reads תום, ack matches the contract shape.

- [ ] **Step 2: Go ⇒ dispatch, and prove the stamp lands at dispatch (R4) with an hour (R2)**

Throw T2 as well, then give one go covering both. Per `messi/SKILL.md` §ביצוע the go writes
queue rows + specs; only the row that actually launches becomes `[~]`.

1. After the go, before anything completes: the log shows T1 as `[~] … שוגר <שעה>` and T2 as
   `- [ ] … ממתין (אחד-אחד)`.
2. Read both rows from Notion. **T1 `תאריך התחלה` is non-null and carries a real `HH:MM`**
   (not `00:00`, not date-only). **T2 `תאריך התחלה` is NULL** — it is approved but ⊥ באוויר.
   T2 non-null ⇒ the stamp is still firing at go ⇒ FAIL, R4 not implemented.
3. `RECIPE:open-loops` returns T1 and **not** T2.

T1's agent is read-only: run `RECIPE:open-loops`, count open tasks, append the count to the log.
Expected: log has תור + ספקים sections in `dispatch.md` shape; the agent returns a real number.

- [ ] **Step 3: Close T1, watch T2 dispatch itself** — stamp `תאריך השלמה`, mark `[x]`, ✓ with the artifact link. One-at-a-time then launches T2, which stamps **its own** `תאריך התחלה` at that moment.
Expected: T1 shows both dates; T2's stamp time is later than T1's go time — the second proof that the stamp follows dispatch, not approval. Close T2 the same way.

- [ ] **Step 4: Checkpoint rehearsal — clean, slipping, and both negative controls**

1. **Baseline arm ("clean"):** run `mode=checkpoint` with **no trial row slipping**.
   Exactly **one new** `CHECKPOINT` line, and its slip set **= B₀ exactly**:
   - `B₀ = ∅` ⇒ the line is literally `CHECKPOINT <HH:MM> clean`, **zero push**.
   - `B₀ ≠ ∅` ⇒ the line is `CHECKPOINT <HH:MM> slipping |B₀|: …` naming **exactly** B₀'s
     members and no one else, and **one** push. That is still the clean arm passing:
     quiet-when-clean is proven by the trial rows adding **nothing**, ⊥ by an absolute zero.
   - Either way **a member ∉ B₀ ⇒ FAIL**, and a member of B₀ going missing ⇒ FAIL.
   Then confirm §ביצוע 7 ran — `git log -1` shows the log commit and the push landed.
   **No commit ⇒ FAIL**: this is the whole reason the 17:00 gate can see the 13:00 run at all.
2. **Slipping:** create T3 (תום, due today, never started). Rerun.
   Expected: **slip set = B₀ ∪ {T3}**, count `|B₀|+1`, one push, and T3's own entry reads
   `בדיקת מסי — מחליקה (דחופה-היום שלא התחילה)`. `|B₀| = 0` ⇒ the line is the familiar
   `CHECKPOINT <HH:MM> slipping 1: בדיקת מסי — מחליקה (דחופה-היום שלא התחילה)`.
3. **R1 negative control:** create T4 (**מקסים**, due today, never closed, `תאריך התחלה`
   set ≥3h ago). Rerun.
   Expected: **slip set unchanged — still exactly B₀ ∪ {T3}**, count still `|B₀|+1`.
   **T4 appearing ⇒ FAIL** — the owner predicate is not in the recipe and the ~66-task
   false-slip bug is live. T4 is deliberately a candidate on **both** axes: due-today
   (criterion 2) and ≥3h in the air with no movement (criterion 1), so this arm exercises
   `LIKE '%תום%'` in `due-today` **and** in `open-loops` at once.
4. **R1, the open-loops half, asserted directly:** `RECIPE:open-loops` row count is back to
   **exactly L₀** — each trial row is excluded for its own reason (T1/T2 closed in Step 3,
   T3 never started, **T4 by the owner predicate**, T5 by `[ארוך]`) — and **T4 is absent from
   the returned rows** even though its `תאריך התחלה` is set. T4 present ⇒ `open-loops` lost
   its owner predicate; the slip list happened to stay clean only because `due-today` still
   had one. This is the assertion that makes dropping `LIKE '%תום%'` from `open-loops` alone
   a visible failure.
5. **R3 negative control:** create T5 (תום) and set its `תאריך התחלה` to a time ≥3h ago.
   Expected: T5 is absent from `RECIPE:open-loops` output and the slip set is **still**
   B₀ ∪ {T3}. Present ⇒ the `[ארוך]` predicate is missing or the engine treats `[` as a
   pattern class — apply the `SUBSTR` fallback recorded in Task 3 Step 4 and rerun.
   T5 carries **no** `תאריך יעד` of today: `[ארוך]` is exempt from the closure **sweep**,
   ⊥ from an explicit due date, so a T5 due today would legitimately surface in `due-today`.

- [ ] **Step 5: Gate rehearsal — three decisions, the exemption, and the backstop**

Run the day-close שער הסגירה stage manually on today.

1. T1/T2 appear and resolve as **נסגרה ✓**.
2. **Exemption:** T4 (מקסים) does **not** appear in the gate at all — waiting-on rows travel
   their own path. It should instead surface on the day-open waiting-on list with a nudge draft.
3. **Provisional נגררת:** leave T3 unresolved, as if only Tom could classify it. Expected: the
   gate assigns `נגררת` with blocker **`ממתין להכרעת טום`**, writes
   `GATE <HH:MM> נגררת: בדיקת מסי — מחליקה · חוסם ממתין להכרעת טום` to today's log, puts it on
   the 🔒 line of שלב 5, and **proceeds to שלב 3**. A ritual that stalls waiting for Tom ⇒ FAIL.
4. **Backstop, both arms:** delete the `CHECKPOINT` line from the log and rerun the stage ⇒ it
   must report `צ'קפוינט 13:00 לא רץ`. Then replace it with
   `CHECKPOINT <HH:MM> FAILURE <סיבה>` and rerun ⇒ it must report
   `צ'קפוינט 13:00 נפל: <סיבה>`, **not** treat the run as fine. Restore the real line after.
5. **Thursday check** (only when the rehearsal falls on a Thursday, else record N/A): the
   carried loop's משבצת lands on **Sunday**, ⊥ Friday.

- [ ] **Step 6: Evidence + commit**

Record in the task output as **N/16**. **B₀ and L₀ are quoted verbatim first** — every count
below is read against them, never as an absolute.

| # | check | proves |
|---|---|---|
| 1 | B₀ (names) + L₀ recorded **before** any trial row exists | delta baseline |
| 2 | T1 row created, `בעל תפקיד` = תום, URL printed | throw → Notion |
| 3 | ack matches the 4-line contract shape | §3 |
| 4 | T2 `תאריך התחלה` NULL while queued | **R4** |
| 5 | T1 `תאריך התחלה` non-null with a real `HH:MM` | **R2 + R4** |
| 6 | log shape — תור + ספקים + `שוגר <שעה>` | `dispatch.md` |
| 7 | T1 closed: both dates, `[x]`, artifact link | G3 |
| 8 | one new `CHECKPOINT` line, slip set = B₀ exactly (∅ ⇒ literal `clean` + zero push) | silence when clean |
| 9 | log commit + push landed | **I5** |
| 10 | slip set = B₀ ∪ {T3}, count `\|B₀\|+1`, one push | slip path |
| 11 | slip set **unchanged** after T4 (מקסים) lands — T4 ∉ it | **R1**, `due-today` half |
| 12 | `RECIPE:open-loops` = L₀; T4 absent though `תאריך התחלה` set ≥3h ago | **R1**, `open-loops` half |
| 13 | T5 (`[ארוך]`) absent from `RECIPE:open-loops`; slip set still B₀ ∪ {T3} | **R3** |
| 14 | T4 absent from the gate; present on the waiting-on path | exemption |
| 15 | provisional `נגררת` + blocker + `GATE` line + ritual proceeds | **I3** |
| 16 | backstop: missing ⇒ "לא רץ" · `FAILURE` ⇒ "נפל" | backstop |

Archive **all five** trial rows (archive, ⊥ delete).
**Authority = Tom's go on this dry-run** — ⊥ `notion_contract.md` §גבולות, which reads
`מחיקה / ארכוב | טום, תמיד` and is **unchanged by this plan**. The claim is narrow and stated
plainly: the five `בדיקת מסי —` rows are enumerated in this task's trial table and exist only
because this run created them, so approving the dry-run approves cleaning them up. **No Tom go
on record ⇒ ⊥ archive**: leave all five, list them with their URLs in the task output, and ask.
Rows this run did not create are never in scope, under any reading.

```bash
git add docs/ceo/messi/<today>.md
git commit -m "test(messi): live dry-run evidence — dispatch-time stamp, Tom-scoped slip list, gate + backstop"
git push
```

---

### Task 9: PR ready + merge + supersede ‎#85 (Phase 5a)

- [ ] **Step 1:** Update PR ‎#102 body checklist (spec ✓, plan ✓, phases ✓), mark ready-for-review.
- [ ] **Step 2:** Verify mergeable + checks state via the GitHub MCP (`pull_request_read` method `get`). This repo has no CI checks — the merge gate is the Task 8 evidence being present in the PR.
- [ ] **Step 3:** Merge ‎#102 (merge commit, house default). Brain policy: autonomous merge allowed — checks green (vacuously) & change verified (**Task 8 N/16**, evidence table at Task 8 Step 6 — including B₀/L₀).
- [ ] **Step 4:** Comment + close ‎#85: "Superseded by ‎#102 — CoS v2 merged there together with messi." (with the Claude Code attribution footer).

---

### Task 10: Triggers + go-live announcement (Phase 5b)

**Consumes:** merged main (Task 9); mode names from Task 4; ritual prompts from CoS v2 §4.6.

- [ ] **Step 1: Create the three triggers** via `create_trigger` (fresh session per fire, this environment):

| name | IL | cron summer (IDT, UTC+3) | cron winter (IST, UTC+2) | prompt |
|---|---|---|---|---|
| `cos-day-open` | 07:30 | `30 4 * * 0-4` | `30 5 * * 0-4` | `Read gt-factory-os-production-brain/CLAUDE.md, then run .claude/skills/chief-of-staff-daily mode day-open. Hebrew.` |
| `messi-checkpoint` | 13:00 | `0 10 * * 0-4` | `0 11 * * 0-4` | `Read gt-factory-os-production-brain/CLAUDE.md, then run .claude/skills/messi mode checkpoint. Silent when clean. Hebrew.` |
| `cos-day-close` | 17:00 | `0 14 * * 0-4` | `0 15 * * 0-4` | `Read gt-factory-os-production-brain/CLAUDE.md, then run .claude/skills/chief-of-staff-daily mode day-close. Hebrew.` |

**These prompt strings are canonical and mirrored verbatim in `.claude/skills/chief-of-staff-daily/SKILL.md` §טריגרים** (all three rows, checkpoint included). Change one ⇒ change both in the same commit. Create with the summer cron now; the winter column is the DST swap (`update_trigger`, last Sunday of October).

Connectors per firing: `["Notion","Google Calendar","Gmail","Supabase","Make"]` for the two rituals; `["Notion"]` only for messi-checkpoint (push goes via PushNotification, no connector needed).
messi-checkpoint also needs git push rights in its environment — its log commit (`messi/SKILL.md` §ביצוע 7) is what carries the `CHECKPOINT` line to the 17:00 gate.

- [ ] **Step 2: Verify** — `list_triggers` shows all three enabled with correct next_run_at (sanity: next day-open lands 07:30 IL). Night trigger is NOT created here — day-close arms it per G6.

- [ ] **Step 3: Announce to Tom (one message):** מה חי (מסי + שלושת הטריגרים + שעות) · הריטואל הראשון מתי · מה נשאר פתוח (אם יש) · תזכורת: זריקה ראשונה אמיתית = פשוט לכתוב "מסי, ...".

---

## Self-Review (done at write time)

- **Spec coverage:** §3 ack/identity→T4 · §4 triage+schema→T3,T4 · §5 closure→T4(checkpoint),T6 · §6 execution→T4,T5 · §7 state→T2,T3,T7 · §8 failures→T4,T5(fallback),T6(backstop) · §9 phases 0–5→T1–T10 · §10 out-of-scope honored (no extra channels, no night engine, no dashboard work) · §11 success criteria exercised by T8.
- **Placeholders:** none — every created file's content is in its task; `<...>` occurrences are runtime template slots, by design.
- **Name consistency:** `תאריך התחלה` · `RECIPE:{open-loops,due-today,opened-today,dup-check}` · `docs/ceo/messi/<YYYY-MM-DD>.md` · `inbox-fallback.md` · mode `checkpoint` — identical across T3–T10.
