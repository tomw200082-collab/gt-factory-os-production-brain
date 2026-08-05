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

**GATE: requires the Notion connector authorized in this environment.** Not authorized ⇒ STATUS: BLOCKED, tell Tom exactly: "קונקטור נושן לא מאומת — לאשר בהגדרות connectors ב-claude.ai, ואז נמשיך", and stop this task (later tasks 4–7 may proceed; tasks 8–10 may not).

**Files:**
- Modify: `docs/ceo/reference/notion_contract.md`

**Interfaces:**
- Consumes: task DB `collection://c6604298-2afb-8258-8026-87e9538244c3`, projects DB `collection://cb704298-2afb-8226-9b23-876996b62c5d` (IDs already in the contract).
- Produces: property `תאריך התחלה` (date, task DB) + recipe names `RECIPE:open-loops`, `RECIPE:due-today`, `RECIPE:opened-today`, `RECIPE:dup-check` — Tasks 4, 6, 8 call these by name.

- [ ] **Step 1: Prove live read on both DBs**

Query via the Notion MCP (querySql over each collection URL): `SELECT "שם" FROM "<collection>" LIMIT 3` for tasks and projects. Print the 3 real rows from each into the task output (evidence).
Expected: 6 real row names total. Failure ⇒ `assumption_failure`, HALT.

- [ ] **Step 2: Add the property**

Attempt via the Notion API (database update adding `תאריך התחלה` type date). If the connector exposes no schema-update capability ⇒ ask Tom to add it manually in Notion (property name exactly `תאריך התחלה`, type Date, on מסד המשימות) and wait for his "done".

- [ ] **Step 3: Write-and-revert probe (the contract's own protocol)**

1. Create task `בדיקת מסי — למחיקה` with `תאריך יעד` = next Sunday.
2. Set `תאריך התחלה` = today. Re-read; verify the value round-trips.
3. Set `תאריך השלמה` = today. Re-read; verify.
4. Archive the trial task (archive, ⊥ delete).
Expected: every write read back identical. Evidence: the re-read values printed.

- [ ] **Step 4: Update `docs/ceo/reference/notion_contract.md`**

In the tasks-schema table add the row:
```markdown
| `תאריך התחלה` | date | `date:תאריך התחלה:start` — נחתם רק ע"י גו של טום למסי או "אני על זה". ריק+יש השלמה = בוצע בלי מעקב, תקין |
```
Append a new section at the end:
```markdown
## מתכוני מסי — שאילתות חתומות (אומתו חי 2026-08-05)

### RECIPE:open-loops — באוויר עכשיו
SELECT "שם", "date:תאריך התחלה:start" AS started, "בעל תפקיד", url
FROM "collection://c6604298-2afb-8258-8026-87e9538244c3"
WHERE "date:תאריך התחלה:start" IS NOT NULL AND "date:תאריך השלמה:start" IS NULL
ORDER BY started;

### RECIPE:due-today — דחופות היום שלא נסגרו
SELECT "שם", "date:תאריך התחלה:start" AS started, "בעל תפקיד", url
FROM "collection://c6604298-2afb-8258-8026-87e9538244c3"
WHERE date("date:תאריך יעד:start") = date('now') AND "date:תאריך השלמה:start" IS NULL;

### RECIPE:opened-today — נפתחו היום (בתחולת מנוע הסגירה)
SELECT "שם", "date:תאריך יעד:start" AS due, "date:תאריך התחלה:start" AS started, url
FROM "collection://c6604298-2afb-8258-8026-87e9538244c3"
WHERE date(created_time) = date('now') AND "date:תאריך השלמה:start" IS NULL
  AND ("date:תאריך יעד:start" IS NOT NULL OR "date:תאריך התחלה:start" IS NOT NULL);

### RECIPE:dup-check — כפילות לפני יצירה
SELECT "שם", url FROM "collection://c6604298-2afb-8258-8026-87e9538244c3"
WHERE "date:תאריך השלמה:start" IS NULL AND "שם" LIKE '%<מילת-מפתח>%';
```
Run each recipe once live; paste row counts as evidence. If `created_time` / `date('now')` syntax fails against the live engine, fix the recipe to the syntax that works and record the correction — the committed recipe must be the one that ran.

- [ ] **Step 5: Commit**

```bash
git add docs/ceo/reference/notion_contract.md
git commit -m "feat(cos-core): notion contract — תאריך התחלה verified live + messi recipes"
git push
```

---

### Task 4: The messi skill (Phase 2a)

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

- [ ] **Step 1: Throw** — in-session, as Tom would: `מסי, משימת ניסיון: ספור כמה משימות פתוחות יש בנושן ותכתוב את המספר ללוג`. Follow SKILL.md exactly: dup-check → create Notion task (due today) → 4-line ack.
Expected: Notion row exists (print its URL), ack matches the contract shape.

- [ ] **Step 2: Go** — stamp `תאריך התחלה`, write the spec to today's log per `dispatch.md`, dispatch a background agent (read-only: run `RECIPE:open-loops` + count open tasks, append the count to the log).
Expected: log file exists with תור + ספק sections; agent returns a real number.

- [ ] **Step 3: Close** — stamp `תאריך השלמה`, mark `[x]`, ✓ line with the artifact link.
Expected: Notion shows both dates on the trial task.

- [ ] **Step 4: Checkpoint rehearsal** — run mode=checkpoint manually. With nothing slipping it must print exactly one `CHECKPOINT <ts> clean` line to the log and push nothing. Then set one extra trial task due-today-not-started, rerun, expect a push draft with one slipping item; archive that trial task after.

- [ ] **Step 5: Gate rehearsal** — run the day-close שער הסגירה stage manually on today: the two trial tasks must appear, both resolvable as נסגרה ✓.

- [ ] **Step 6: Evidence + commit**

Record in the task output: 6 checks (row created · ack shape · start stamp · log shape · clean checkpoint · slipping checkpoint) as N/6. Archive both trial Notion tasks (archive, ⊥ delete).
```bash
git add docs/ceo/messi/
git commit -m "test(messi): live dry-run evidence — throw→notion→go→execute→close, checkpoint clean+slipping"
git push
```

---

### Task 9: PR ready + merge + supersede ‎#85 (Phase 5a)

- [ ] **Step 1:** Update PR ‎#102 body checklist (spec ✓, plan ✓, phases ✓), mark ready-for-review.
- [ ] **Step 2:** Verify mergeable + checks state via the GitHub MCP (`pull_request_read` method `get`). This repo has no CI checks — the merge gate is the Task 8 evidence being present in the PR.
- [ ] **Step 3:** Merge ‎#102 (merge commit, house default). Brain policy: autonomous merge allowed — checks green (vacuously) & change verified (Task 8 N/6).
- [ ] **Step 4:** Comment + close ‎#85: "Superseded by ‎#102 — CoS v2 merged there together with messi." (with the Claude Code attribution footer).

---

### Task 10: Triggers + go-live announcement (Phase 5b)

**Consumes:** merged main (Task 9); mode names from Task 4; ritual prompts from CoS v2 §4.6.

- [ ] **Step 1: Create the three triggers** via `create_trigger` (fresh session per fire, this environment):

| name | cron (UTC, IDT; winter +1h) | prompt |
|---|---|---|
| `cos-day-open` | `30 4 * * 0-4` | `Read gt-factory-os-production-brain/CLAUDE.md, then run .claude/skills/chief-of-staff-daily mode day-open. Hebrew.` |
| `messi-checkpoint` | `0 10 * * 0-4` | `Read gt-factory-os-production-brain/CLAUDE.md, then run .claude/skills/messi mode checkpoint. Silent when clean. Hebrew.` |
| `cos-day-close` | `0 14 * * 0-4` | `Read gt-factory-os-production-brain/CLAUDE.md, then run .claude/skills/chief-of-staff-daily mode day-close. Hebrew.` |

Connectors per firing: `["Notion","Google Calendar","Gmail","Supabase","Make"]` for the two rituals; `["Notion"]` only for messi-checkpoint (push goes via PushNotification, no connector needed).

- [ ] **Step 2: Verify** — `list_triggers` shows all three enabled with correct next_run_at (sanity: next day-open lands 07:30 IL). Night trigger is NOT created here — day-close arms it per G6.

- [ ] **Step 3: Announce to Tom (one message):** מה חי (מסי + שלושת הטריגרים + שעות) · הריטואל הראשון מתי · מה נשאר פתוח (אם יש) · תזכורת: זריקה ראשונה אמיתית = פשוט לכתוב "מסי, ...".

---

## Self-Review (done at write time)

- **Spec coverage:** §3 ack/identity→T4 · §4 triage+schema→T3,T4 · §5 closure→T4(checkpoint),T6 · §6 execution→T4,T5 · §7 state→T2,T3,T7 · §8 failures→T4,T5(fallback),T6(backstop) · §9 phases 0–5→T1–T10 · §10 out-of-scope honored (no extra channels, no night engine, no dashboard work) · §11 success criteria exercised by T8.
- **Placeholders:** none — every created file's content is in its task; `<...>` occurrences are runtime template slots, by design.
- **Name consistency:** `תאריך התחלה` · `RECIPE:{open-loops,due-today,opened-today,dup-check}` · `docs/ceo/messi/<YYYY-MM-DD>.md` · `inbox-fallback.md` · mode `checkpoint` — identical across T3–T10.
