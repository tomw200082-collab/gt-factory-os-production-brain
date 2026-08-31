# MASTERPROMPT — build the war-room skill, from a day that actually ran one

**STATUS: LIVE — not yet executed**

> **Usage (Tom):** paste this whole file as the first message of a fresh Claude Code
> session with `gt-factory-os-production-brain` attached. It turns the coordination
> pattern that ran on 2026-08-31 into a reusable skill, so the next time you dump a pile
> of work the session behaves this way by construction instead of by luck. It halts for
> you only where §6 says.
>
> **Provenance:** written 2026-08-31 at the end of the day it describes. Every number in
> §2 was measured from `git log`, the PR list and the produced files — not recalled. The
> session being described is the one that wrote it, so §2.4 is a self-assessment and is
> marked as such.
>
> **Shelf life:** §2 is a historical record and does not go stale. §2.5's survey of
> neighbouring skills does — re-run it if pasted after 2026-09-30, because a skill that
> duplicates an existing one is worse than no skill.

---

## 0. How to work

- **Who you are here:** one Claude Code session writing a skill. You hold the brain repo
  with push access. You decide the skill's structure and wording. You do **not** decide
  the two questions in §6.A and §6.B — they change the skill's shape and they are Tom's.
- **Read first, in order:**
  1. `.claude/skills/writing-skills/SKILL.md` — **the house way to write one.** Follow it;
     this document supplies the content, not the format.
  2. `.claude/skills/writing-skills/testing-skills-with-subagents.md` — how a skill is
     proven to work. D6 depends on it.
  3. `.claude/skills/masterprompt/SKILL.md` and its `TEMPLATE.md` — the skill you are
     building sits **on top** of this one and must not re-teach any of it.
  4. `.claude/skills/close-session/SKILL.md` — owns knowledge routing at session end. The
     war room hands off to it rather than reinventing that step.
  5. `.claude/skills/messi/SKILL.md` and `chief-of-staff-daily/SKILL.md` — Tom's existing
     task and rhythm layer. **The overlap here is the biggest design risk in this work**
     (§3, reframe 4).
  6. `docs/plans/2026-08-31-WAR-ROOM.md` — the artefact the pattern produced.
  7. Any two of the six masterprompts dated `2026-08-31` — read them as specimens of the
     output the skill must reliably produce.
- **Authority:** `gt-factory-os-production-brain/CLAUDE.md` wins. Note especially
  §Non-negotiables ("⊥ second writable fallback system") and §Write boundaries — both bear
  directly on §6.A. Halt conditions and evidence standard are inherited, not re-authored.
- **The standard.** Tom asked for a skill that focuses him and makes him stronger at
  running many things at once — his words: `לפקס אותי ולחזק אותי מולטיטאסקינג`
  Three prohibitions that make that checkable:
  1. **The skill may not create a second task system.** If it ends up holding a list that
     competes with Notion, it has failed regardless of how good the list is.
  2. **No mechanism may depend on Tom relaying information between sessions** where a
     machine-readable channel already exists.
  3. **No step in the skill may be un-runnable.** "Coordinate with the other session" is
     the exact failure this document exists to remove: sessions cannot talk.
- **Be lazy on purpose.** One skill. Reuse `masterprompt`, `writing-skills` and
  `close-session` by reference. If you find yourself writing a second skill, or a
  framework, stop — §5 forbids it and §3 explains why.
- **Language:** this document is English; data literals stay in their own script in
  backticks. **Output language: concise Hebrew for Tom, concise English otherwise.**

---

## 1. Mission and definition of done

**One testable sentence:** a fresh session that loads this skill and receives a pile of
mixed work runs the 2026-08-31 pattern — recon, numbered briefs, ownership contracts,
repo-read tracking, self-correction, three live asks — without being told any of it.

| # | Condition | The observation that would prove it false |
|---|---|---|
| D1 | The skill exists at `.claude/skills/war-room/SKILL.md` and passes the house format | `writing-skills` conventions violated; frontmatter description that does not name its triggers |
| D2 | It cites `masterprompt`, `writing-skills` and `close-session` by path and re-teaches none of them | Any paragraph that restates how to write a masterprompt = fail |
| D3 | The intake step freezes the user's own numbering as an identifier | Give it a dump of 5 tasks where task 3 is the most urgent; if the produced board renumbers 3 to 1, fail |
| D4 | Ownership contracts are generated **before** dispatch, from the briefs themselves | Give it two briefs that both name one shared resource; if neither brief gains an owner line, fail |
| D5 | Tracking reads the repo and the PRs, not the user's relayed messages | The skill's tracking step must name the commands. "Ask the user for an update" as the primary channel = fail |
| D6 | A subagent given only the skill and a task dump produces the expected behaviour | Run the `testing-skills-with-subagents` procedure. Any of D3, D4, D5 not observed in its behaviour = fail |
| D7 | At most three live asks are surfaced to the human at once | Feed it a scenario with nine human-blocked items; a reply listing all nine = fail |
| D8 | The self-correction rule is present and specific | The skill must name the trigger, not the sentiment. "Be humble" = fail; "a session that contradicts you ran queries you did not" = pass |

Anything not on this list is out of scope unless Tom asks.

### 1.1 Settled — do not reopen

- **One skill, not a suite.** The pattern is one loop with phases, not four collaborating
  skills.
- **`masterprompt` writes the briefs.** The war room decides *what* briefs exist, who owns
  what across them, and what happens after. It never re-teaches brief-writing.
- **`close-session` owns end-of-session knowledge routing.** Hand off; do not duplicate.
- **The PR body is the status channel** (§3, reframe 2). Do not design a parallel status
  file format before reading that section.
- **The pattern is proven, not hypothetical.** It ran for one full day and produced the
  evidence in §2. You are encoding something that worked, not inventing something new.

---

## 2. Ground truth — the day being encoded, measured 2026-08-31

### 2.1 What the pattern produced

| | |
|---|---|
| Input | one message, six pieces of work, mixed structure — two with pasted artefact text, one described only as "find it yourself" |
| Recon | 3 repos, plus live Supabase, Shopify, Canva and four published artefacts |
| Output | **8 documents, 3,194 lines** (`git diff --stat da13c0d..HEAD -- docs/plans/`) — six briefs, one board, one superseding rewrite |
| Dispatch | six sessions, pasted by Tom, running in parallel |
| Landed the same day | 4 pull requests merged — `gt-site#1`, brain `#187`, `#192`, `#189` |
| Commits on `main` from those sessions | 12, between 11:38 and 18:29 |
| Cross-session contracts issued | 3 (`C1` intake, `C2` answer bank, `C3` shared repo) |
| Board corrections forced by reality | **2** — both from sessions disproving the board |
| Merge conflicts resolved | 1 |
| Check-ins run | ~5 hourly; **1** caught something real |

### 2.2 The three findings that made the briefs worth pasting

Each came from running something, and each changed what the work *was*:

- **`141` of `199` leads unanswered, `130` never touched.** Five of the six workstreams
  were about generating more demand. None was the constraint.
- **The site's images: 144 unique files averaging `19.9 MB`, ≈2.9 GB, served through a
  free third-party proxy from a CDN GT does not own.** Reframed "translate the site" into
  "the site does not own its own content."
- **`0` of `48` drink figures on the site matched the figures of record.** Found by
  parsing `COLS` and diffing in code, not by reading either document.

**None of the three was in any document.** All three came from measurement. This is the
single most transferable fact about the day and the skill's first phase must enforce it.

### 2.3 The mechanisms that worked, and why

- **Closed `§6` lists.** Each brief ended human-blocked work at an explicit, finite list.
  Tom could see his whole surface across six workstreams in one place.
- **Contracts.** Three shared resources had two claimants each. Naming one owner per
  resource stopped three duplicate builds — the answer bank, the lead intake taxonomy and
  the `gt-site` foundation.
- **Reading `git log` instead of waiting.** Twice the board learned the true state from
  merged commits before Tom mentioned it.
- **Correcting the board when disproved.** Both times a session's deeper measurement beat
  the board's reading, the board changed and said so in the commit message.

### 2.4 Where the pattern was weak — self-assessed, and the reason this skill is worth writing

**a. A wrong finding shipped into a brief.** The repo holds two files named
`drinks_final_figures.json`; the board read the superseded one and wrote that the
knowledge book's figures were wrong. They were correct — `9/9` on re-check. It was caught
before dispatch, but only by chance.
**The missing trigger:** the finding contradicted an artefact Tom had already approved and
was actively using. *That contradiction is evidence of a stale source, not of bad work.*

**b. The user's numbering was silently changed.** The board sorted workstreams by priority
and Tom had to ask which brief was which number.

**c. Contracts were retrofitted.** They were issued only after Tom reported six sessions
running. Until then the briefs said "agree with that session" — an instruction no session
can execute, because sessions cannot talk to each other.

**d. Blind between messages.** Every update arrived either as a paste from Tom or as a
merged commit the board happened to check.

**e. Fifteen live asks.** `T1`–`T15` was a backlog presented to a man who had asked to be
focused.

**f. No cost awareness.** Six frontier sessions ran in parallel and the board never
mentioned what that costs.

**g. Cadence ignored state.** A fixed 60-minute check-in regardless of whether six
sessions were mid-flight or everything was blocked on one human decision.

### 2.5 What already exists — survey before you write a line

| Skill | Owns | Overlap risk |
|---|---|---|
| `masterprompt` | writing one brief for a context-free executor | **none — build on it** |
| `writing-skills` | how a skill is written and tested | none — follow it |
| `close-session` | end-of-session cleanup and knowledge routing | hand off to it |
| `dispatching-parallel-agents` | **subagents inside one session**, isolated context | **none** — different problem; do not conflate |
| `messi`, `chief-of-staff-daily`, `weekly-opening` | Tom's tasks, day rhythm, weekly rocks; **Notion is master** | **high — see §3 reframe 4 and §6.A** |
| `.claude/state/*.json` | append-only signals, `emitted_by` + `evidence_path` convention | a precedent to follow **if** §6.B says files at all |

### 2.6 Re-verification block

```bash
ls .claude/skills/                                    # has a war-room skill appeared since?
git log --oneline --since="2026-08-31" origin/main | head -20
sed -n '1,20p' .claude/skills/messi/SKILL.md          # is Notion still master for tasks?
```

---

## 3. What the hard part actually is

**Reframe 1 — the product is a true board and a short list, not documents.** The first
hour of the day was document-writing and it went well. The following six hours were state
ownership: which workstream is where, what contradicts what, what is blocked on whom. The
documents are a one-time output; the board is the thing that has to stay true all day. A
skill that optimises brief quality and leaves tracking vague will reproduce the good first
hour and none of the rest.

**Reframe 2 — the status channel already exists and it is the pull request.** The instinct
is to invent a status file the sessions write and the war room reads. Resist it for one
observation: the richest, most accurate account of any workstream on 2026-08-31 was the
body of `gt-site` PR #1 — it carried the measurements, the open questions and the explicit
"not verified" line, and it was more useful than the summary a human relayed. Sessions
already write PR bodies. GitHub already wakes a subscribed session on PR events. The tools
to read them already exist. **So the mechanism is: every brief's `§9` report shape says the
report goes in the PR body, and the war room subscribes and reads it.** No new convention,
no new file, nothing for the human to carry. The corollary the skill must also state: a
workstream that has produced no PR is invisible, so intake records where each workstream's
output will land, and silence past a threshold is itself a signal to surface.

**Reframe 3 — the war room is the one component nothing tests.** Sessions are disproved by
reality all day: a query returns, CI goes red, a test fails. The war room writes prose
about other people's work and no gate ever runs against it. That is exactly how a wrong
finding shipped (§2.4a). Two rules follow, and they belong in the skill as posture rather
than as a checklist item:
- **When a session contradicts the board, assume the session is right.** It ran the query;
  the board read a file. Verify, then correct the board, and say so where the correction
  is visible.
- **A finding that contradicts work the human already approved is suspect by default.**
  Check the source's currency — its recency, and whether anything names a different file
  as the record — before writing the finding down.

**Reframe 4 — the human's attention is the scarcest thing in the system, and it is
already spoken for.** Every mechanism should reduce either what Tom must *relay* or what
he must *decide*; those are the only two currencies. But he already has a task layer —
`messi` and Notion — and the kernel forbids a second writable system. `T1`–`T15` was, in
plain terms, a second task list. This is the fork the skill cannot resolve on its own
(§6.A): either war-room asks are short-lived session-blockers that never enter Notion, or
they are Notion items and the board only points at them. Design for whichever Tom picks;
do not build both.

**Reframe 5 — dispatch is a fan-out with no back-channel, and that is a design constraint,
not a limitation to apologise for.** Six sessions, no inter-session communication, one
human as the only router. Everything downstream follows from it: contracts must be written
into the briefs because they cannot be negotiated later; ownership must be singular
because arbitration has no venue; status must be pulled from artefacts because it cannot
be pushed between peers.

---

## 4. Workstreams

### W1 — The skill's spine

Write `.claude/skills/war-room/SKILL.md` around the loop the day actually ran. Phases,
each with its own trigger to move on:

1. **Intake.** Split the dump into numbered workstreams. **Freeze the user's numbering as
   an identifier** — views may sort by anything, IDs never move. Echo the list back before
   any recon, flagging which are underspecified and which name an existing artefact.
2. **Recon.** Measure at source, per workstream, before writing anything. The bar is §2.2:
   the phase is not done until each workstream has either a fact that changes what the
   work is, or an explicit recorded finding that the state is as expected.
3. **Write.** Hand to `masterprompt`. The war room contributes only what that skill cannot
   know: cross-workstream ownership, and the report shape from reframe 2.
4. **Contract.** Before dispatch, list every resource named in two or more briefs. Each
   gets exactly one owner, written **into both briefs**. Generated at write time, never
   retrofitted.
5. **Dispatch.** Hand the human paste-ready briefs plus, per workstream, where its output
   will land.
6. **Track.** Poll PRs and `git log`; never wait for a relay. Cadence follows state, not
   the clock — tight while work is in flight, long and quiet while everything is blocked
   on a human, stopped when all workstreams are closed.
7. **Correct.** Reframe 3, as posture.
8. **Focus.** At most three live asks. Retire aggressively. One "if you do one thing now."
9. **Close.** Hand to `close-session`.

**Acceptance:** D1, D2, D3, D4, D5, D8.

### W2 — The focus mechanism

The weakest part of the day (§2.4e) and the thing Tom explicitly asked for. Specify:

- **Three live asks, maximum.** Ranked by what each unblocks — count the workstreams, not
  the effort.
- **One next action.** Every report to the human ends with the single highest-leverage
  thing only he can do.
- **Retirement is active.** An ask stays live until the board has evidence it is done —
  from a PR, a commit, or the human saying so. It does not linger because nobody looked.
- **Held asks stay visible but quiet** — one line saying how many are waiting behind the
  three, so the human knows the list is bounded and not lost.

Whether these asks are war-room-local or Notion items is §6.A. **Write the mechanism so
either answer drops in.**

**Acceptance:** D7.

### W3 — Prove it with a subagent

Follow `writing-skills/testing-skills-with-subagents.md`. Give a fresh subagent only the
skill and a synthetic dump — five workstreams, one obviously most urgent but numbered
third, two sharing one resource, four items needing a human decision. Then observe:

- Did it keep the user's numbering? (D3)
- Did it produce an owner for the shared resource, in both briefs? (D4)
- Did it name repo and PR reads as its tracking channel? (D5)
- Did it surface three asks or nine? (D7)

Record what it did, not what you hoped. A skill that needs the author present is not a
skill — that is the whole test.

**Acceptance:** D6.

### W4 — Route the day's transferable knowledge

Four landmines from 2026-08-31 generalise past this skill. Route each by type, per
`close-session` §knowledge routing — **do not paste them into the skill**, which is about
coordination, not about GT's catalogue:

- Two files with the same name, one superseded, and the pointer to the record living in a
  third document (`COST_MODEL.md:78`).
- A curated truth file can be stale in **both** directions — it denied two products that
  had been live for months.
- Unscoped CSS class names leak across every page on a shared Shopify theme.
- An artefact's checkbox state lives in one browser's `localStorage` and is invisible to
  everyone else, including the session that built it.

### W5 — Cost, if §6.D says so

If Tom wants it: one line per report — how many sessions are live and roughly what the
parallelism is costing. Six frontier sessions is a real number and the day never mentioned
it. If he does not want it, drop it entirely rather than making it optional-and-ignored.

---

## 5. Scope

**IN:** everything in §4.

**OUT — do not touch, do not "improve":**
- **A second skill.** One file plus at most one reference. If the content will not fit,
  the content is too broad — cut it, do not split it.
- **Re-teaching `masterprompt`.** Cite it.
- **A framework, an agent, a command surface beyond a single trigger.** GT's kernel
  forbids new authority layers without Tom's written decision.
- **Notion, `messi`, `chief-of-staff-daily`, `weekly-opening`.** Not yours to change. The
  war room fits around them per §6.A.
- **The six `2026-08-31` masterprompts and the war-room board.** They are specimens and
  history. Read; do not edit.
- **Any authority doc** — `CLAUDE.md`, `EXECUTION_POLICY.md`, `CURRENT_STATE.md`.

---

## 6. Tom's part — the complete list, nothing else is yours

**A. The one that changes the skill's shape: does the war room hold your action list, or
point at Notion?** Today it held `T1`–`T15` itself, which is in plain terms a second task
system — and the kernel forbids one, while `messi` says Notion is master. Two workable
answers: war-room asks are short-lived session-blockers that never enter Notion and die
when the workstream closes; or every ask is a Notion item and the board only points. Pick
one. **W2 cannot be written until you do.** ~10 minutes.

**B. Do sessions write a status file, or is the PR body enough?** The recommendation is
the PR body — it already exists, it was the best account of any workstream today, and it
costs nothing. Say yes and it goes into every future brief's report shape. Say no and the
skill needs a file convention instead. ~5 minutes.

**C. How should it interrupt you?** Today it reported when you asked and went quiet
otherwise. Options: silent unless something is blocked or broken; a fixed check-in; or
push the moment an ask matures. This decides the tracking phase's default.

**D. Do you want cost tracking?** One line per report on live sessions and what the
parallelism is costing, or nothing at all.

**E. Trigger and name.** `/war-room`, `חמ"ל`, both, or always-on whenever you dump more
than three things at once.

---

## 7. Landmines — do not rediscover these

1. **`dispatching-parallel-agents` sounds like this skill and is not.** It is about
   subagents inside one session with isolated context. This is about independent sessions
   a human pastes, which cannot see each other at all. Conflating them produces advice
   that assumes a back-channel that does not exist.
2. **A skill that duplicates an existing one is worse than no skill** — two documents
   claiming the same ground, drifting. §2.5 is the survey; re-run it if this sat unpasted.
3. **The kernel forbids a second writable task system** (`CLAUDE.md` §Non-negotiables).
   §6.A is not a preference question; it is a compliance question.
4. **Writing a skill from the memory of a session is the same error the skill warns
   about.** The day is on disk: `git log`, the PR list, the eight documents. Measure it.
5. **A skill nobody can run is prose.** Every phase needs an observable exit. "Do
   thorough reconnaissance" is not one; "each workstream has a fact that changes what the
   work is, or a recorded finding that it does not" is.
6. **The self-correction rule dies if written as sentiment.** "Be open to being wrong"
   changes no behaviour. Name the trigger: a session contradicts the board, or a finding
   contradicts already-approved work.
7. **Do not let the skill grow a template for the briefs.** `masterprompt/TEMPLATE.md`
   exists and is the single source of that section list. A second template will drift from
   it within a week.

---

## 8. Halt conditions

Inherited from `gt-factory-os-production-brain/CLAUDE.md` §Stop conditions. Additions:

- The design requires a second task system, or writing to Notion → **STOP**, §6.A.
- Any authority doc would be edited → **STOP**.
- The skill would exceed one file plus one reference → **STOP** and cut scope.
- A neighbouring skill would need changing to make this one fit → **STOP** and surface it.

---

## 9. Final report — Hebrew, short, honest

1. What a fresh session now does differently, in one sentence.
2. D1–D8 ✅/❌ with evidence pointers. No partial credit.
3. The subagent test: what it actually did on each of D3, D4, D5, D7.
4. The artefacts and where they are.
5. What is still Tom's, and what is genuinely unfinished.
6. The single next action.

Put this report in the PR body — that is the mechanism this document argues for, and this
work should be the first to use it.

Then stamp this file `STATUS: SHIPPED — <date>` with evidence pointers, and commit.
