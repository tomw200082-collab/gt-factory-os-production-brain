---
name: meeting-summary
description: Turn a meeting recording/transcript into a grounded, closed-loop summary — connected to Notion tasks & projects, verified against the live Factory OS + Shopify, archived in the brain, and emailed as a branded Hebrew report. Use WHENEVER Tom asks to summarize a meeting or sends meeting material — "סכם את הפגישה", "סיכום פגישה", "תסכם את הישיבה", "סיכום ישיבת רביעי", "meeting summary", "/meeting-summary", a pasted transcript, an audio/voice recording of a meeting, or a transcript file (from Drive/Dropbox/chat). Also trigger when Tom asks "מה סגרנו בפגישה" or wants last meeting's action items tracked.
---

# Meeting Summary — grounded & closed-loop

## Purpose

A professional meeting summary is not a prettier transcript. It is:
1. **Decisions separated from actions separated from information.**
2. **Every action item has an owner + due date + a place it lives** (Notion — the source of truth for tasks/projects, Tom 2026-08-02).
3. **Every number said in the room is checked against the system.** "יש 400 בקבוקים" gets verified against live stock truth before it enters the record.
4. **Closed loop:** the next meeting opens with the status of the previous one's action items. Nothing evaporates.

This skill produces that — and routes each output to its existing home. It creates **no new systems**.

## Sources of truth (⊥ invent alternatives)

| What | Where | How |
|---|---|---|
| Tasks | Notion DB **משימות** — data source `collection://c6604298-2afb-8258-8026-87e9538244c3` | create/update via Notion MCP |
| Projects | Notion DB **פרויקטים** — data source `collection://cb704298-2afb-8226-9b23-876996b62c5d` | link tasks via relation; new project = Tom approval first |
| Durable knowledge / decisions about how GT works | brain repo, routed by `close-session` §Step 4 tier system (Tier 0 boot / Tier 1 skills / Tier 2 docs) | same routing, no exceptions |
| Live operational numbers | Supabase (Factory OS) · Shopify MCP · LionWheel mirror | query live, never from memory |
| Meeting archive | `data/meetings/YYYY-MM-DD-<slug>.md` (this repo) | committed every run |
| Email delivery | Make webhook → Gmail (guardian channel, verified live) | see Stage 5 |

### Notion schema (fetched 2026-08-02 — re-fetch if a write fails validation)

**משימות** properties: `שם` (title) · `אחראי` (person) · `בעל תפקיד` (multi_select: תום, אלכס, דורין, מקסים, דניס, עדי, אדי, אמיר) · `גל` (select: גל 0…גל 4, שלב ב, שוטף, מנהלה) · `מסלול` (select: שטח, מעבדה, ציר-אלכס, מנהלה) · `פרויקטים` (relation → פרויקטים, max 1) · `תאריך יעד` (date) · `תאריך השלמה` (date).
Task-title convention observed in the DB: `<גל/שוטף/מנהלה> · <משימה>` — follow it.

**פרויקטים** properties: `שם` · `סטטוס` (לא התחיל, בתהליך, בהמתנה, הושלמו, בוטל) · `ציר` (INBOUND, OUTBOUND, מנהלה) · `מסלול` · `אחראי` · `עדיפות` (number) · `KPI` · `Description` · `מה צריך מאלכס` · `לוח זמנים לפרויקט` (date range) · `חסימה על ידי` (relation).

## Stage 0 — Intake

Accepted inputs, in order of preference:
1. **Transcript text** — pasted in chat, or a file (chat upload / Google Drive / Dropbox via MCP).
2. **Audio file** (m4a/mp3/wav) — transcribe first:
   - Primary: **ElevenLabs Scribe** — `POST https://api.elevenlabs.io/v1/speech-to-text` (multipart: `file`, `model_id=scribe_v1`, `language_code=he`, `diarize=true`), header `xi-api-key: $ELEVENLABS_API_KEY`. Keep speaker labels.
   - Alternative (if Tom picked it after the head-to-head): **Soniox** async API, `language=he`, diarization on.
   - No API key configured / no network → **HALT** and ask Tom for the transcript. ⊥ summarize from a half-heard audio guess.
3. **Rough notes** Tom typed — allowed, but mark the summary "מבוסס על נקודות, לא תמלול".

Also load, every run:
- The most recent file in `data/meetings/` (for the closed loop, Stage 4).
- Open Notion tasks whose page body carries a `meeting-summary:` origin line (created by previous runs) — query the משימות data source.

## Stage 1 — Extract

From the transcript, extract into four strict buckets (a sentence goes in ONE bucket):
- **החלטות** — something was decided. Capture verbatim intent + who decided.
- **משימות** — owner (one of the 8 people; unclear → default תום + flag), action, due date (explicit, or infer from context like "עד רביעי הבא" → ISO date; none → leave empty + flag), definition of done, related project if named.
- **שאלות פתוחות** — raised, not resolved.
- **טענות עובדתיות** — every number/claim about stock, orders, prices, customers, capacity said in the room.

Hebrew transcription reality: expect garbled product names and English terms. Resolve against `private_core.items` names and the existing lexicons (`shopify-draft-order-from-po/assets/lexicon.json`) before flagging as unknown.

## Stage 2 — Ground in reality (the whole point)

1. **Numbers vs system.** For each factual claim that maps to live data: one read-only check — Supabase SQL (stock truth, open POs, production plan, credit tracking) or Shopify MCP (committed/orders) or LionWheel mirror. Three outcomes per claim: ✓ מאומת · ✗ סתירה ("נאמר X · במערכת Y") · ◌ לא ניתן לאימות. Never silently trust the room over the system, and never overwrite the system from the room — contradictions are **surfaced**, not auto-fixed.
2. **Tasks vs Notion.** Search משימות for an existing matching task before creating anything (title semantic match). Exists → link it (and note if the meeting changed its due/owner); new → queue for creation with the project relation resolved against פרויקטים.
3. **Decisions vs locked decisions.** A meeting "decision" that would flip a frozen flag, violate stock-ledger semantics, or contradict `CLAUDE.md`/`LOCKED_DECISIONS.md` is NOT absorbed — mark it `HOLD_FOR_TOM` with the conflicting clause quoted. Stop conditions apply here like everywhere.

## Stage 3 — Approval gate (⊥ skip)

Present in chat, compact: decisions · tasks-to-create/update table (owner, due, project, existing-vs-new) · contradictions found · knowledge items and their routing tier. Creating many Notion records + sending email = mass-scale external write → **Tom approves first** ("שגר" or edits). No Notion write, no email, before approval.

## Stage 4 — Write (after approval)

1. **Notion tasks**: create pages in the משימות data source with the properties above; page body gets one origin line: `meeting-summary: <date> · <slug>` (this is the closed-loop query key). Meeting-driven updates to existing tasks: due/owner changes only. ⊥ mark tasks done on someone's behalf, ⊥ delete, ⊥ restructure the DB.
2. **New projects**: only if Tom explicitly approved that project in Stage 3.
3. **Knowledge**: route decisions/durable facts per `close-session` §Step 4 (Tier 0 = invariants only; Tier 1 = domain skill files; Tier 2 = docs). A decision that amends an authority doc → HOLD_FOR_TOM (write boundaries).
4. **Archive**: write `data/meetings/YYYY-MM-DD-<slug>.md` — participants, decisions, task table (with Notion URLs), contradictions, open questions, previous-meeting follow-up status. Commit + push (docs lane, specific paths, ⊥ `git add -A`).

## Stage 5 — Email (the beautiful part)

Fill `references/email_template.html` (RTL Hebrew, Outlook-safe inline-table HTML; bidi rule: wrap bare Latin/dates in `<span class="ltr">`). The template carries its own design contract in its header comment — read it before filling. Three things it will not forgive:
- **The hero is a thesis, ⊥ a label.** `{{THESIS_HEADLINE}}` states the single most important finding as a sentence ("השבוע ממתין לשני מסמכים מאלכס"). Write it last, after extraction.
- **The spine is earned.** The numbered dark-band sequence renders only when the meeting produced a real ordered chain with dependencies. Flat decision list → delete that section; ⊥ number things that aren't a sequence.
- **Empty section → delete the section**, header included. A heading with nothing under it reads as a bug.

Section order: hero thesis · spine (if earned) · **מהפגישה הקודמת** (closed loop) · ממתין ל־X (blockers) · רשת נושאים · מה נסגר · משימות בנושן · נאמר מול המערכת · שמור להמשך.

Send via the verified guardian channel: `curl -sS -X POST "https://hook.eu1.make.com/8yie1tl89bxsq8qqp6o47qydfr8cguji" -H "Content-Type: application/json" -d '{"subject":"GT · סיכום פגישה · <date> · <title>","html":"<filled>"}'` → Make scenario `GT Guardian — Daily Email` (6439326) → tom@gteveryday.com. Confirm HTTP 200; non-200 → say so + fall back to Gmail MCP `create_draft`. Recipient is Tom (webhook-fixed); distribution to the team = Tom forwards, or a Make-side change (separate, ask first).

## Stage 6 — Closed loop (next meeting)

Every run ends by making the next one accountable: the archive file's task table + the `meeting-summary:` origin lines in Notion are the query keys. Next run's email opens with the previous meeting's items and their live status (done = `תאריך השלמה` set in Notion; overdue = `תאריך יעד` passed). The Wednesday meeting (`plan-production-14d` day) is the anchor cadence, but the skill serves any meeting.

## Hard rules

- ⊥ invent numbers. Every figure in the email is live-verified or explicitly marked "מהפגישה — לא אומת".
- ⊥ write to Notion or send email before Stage 3 approval.
- ⊥ absorb meeting decisions that contradict locked decisions — HOLD_FOR_TOM.
- Loud failure (guardian V9 discipline): connector missing → say so in chat + halt; a silent no-op is the bug.
- Stock truth stays sacred: this skill is read-only toward Factory OS. It proposes; existing skills (production-order, procurement-planning, daily-delivery-dispatch…) execute, each with its own gates.
