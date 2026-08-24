---
name: masterprompt
description: >
  Use when Tom asks for a masterprompt / מאסטרפרומפט / "a prompt I'll paste into a new
  session", when handing substantial work to a session or agent that shares none of
  this conversation's context, or when work must be executed by someone who was not
  present when it was scoped. Also on the /masterprompt trigger.
---

# Masterprompt

## Overview

A masterprompt is a self-contained brief handed to a fresh executor, which then does
the work without coming back to ask what you meant.

**Three premises generate every rule here. Each rule below cites its parent.**

1. **Zero shared context.** The reader knows nothing you learned. If a fact is not in
   the document it does not exist, and the reader will rediscover it the slow way or
   contradict it confidently.
2. **Your own knowledge is dated and lossy.** Not the reader's problem — yours. This is
   why reconnaissance is non-negotiable and why a masterprompt written from a
   conversation summary asserts false things with confidence.
3. **The reader has your capability but not your authority.** Not your credentials, not
   your standing to decide. A fully competent stranger will happily decide something
   that was never theirs to decide.

## When to Use

- Multi-step work a fresh executor will own end to end
- Any handoff across a context boundary — new session, another agent, another person
- Work that will be re-run later, or handed on again
- Anything where being wrong is expensive

**When NOT to use:**

- The work fits in this session → **do it**. A masterprompt for a 20-minute task is
  procrastination with formatting.
- The ask is a question → answer it.
- Scope is still forming → that is a conversation, not a document.
- **A task-level plan for work already scoped** → that is `writing-plans`. A
  masterprompt wraps; a plan nests inside it.

---

## Phase 1 — Reconnaissance *(premise 2)*

**Nothing is written before this produces observations.**

Items 1–4 are independent; run them concurrently (`dispatching-parallel-agents`).
Item 5 shapes how you read the rest.

1. **Measure the current state at its source.** Counts, states, timestamps, last-success
   times. Not "the pipeline works" — the number, and what it implies.
2. **Read the current artifact**, not your memory of writing it. Signatures drift.
3. **Verify the thing that will run, not the artifact that describes it.** Deployed code
   over committed code; the live form over the form spec; the API's real response over
   its documentation; what the person currently believes over the last email.
4. **Establish the baseline.** Which failures pre-date you? An executor that inherits
   two broken tests and thinks it caused them chases ghosts for an hour.
5. **Read the governing docs** and note conflicts. **If no authority order exists,
   establish one and state it** — "if the code and this document disagree, X wins."

**Non-software reconnaissance is still reconnaissance.** Read the last three artifacts
of this kind and what happened to them · ask the people holding unwritten constraints ·
get source documents, not descriptions of them · find who already tried this and what
they hit. Greenfield changes the target, never the requirement.

### Hunt for the fact that reorganizes everything

The one that, once known, changes what the work *is*:

> `leads 188 · leads ever touched 0 · live leads ever received 0`
> A system described as "built and tested" had never carried a real record or been used
> by a human. That reframed the task from "finish the features" to "nothing here has
> ever been exercised."

Ask: *what would have to be true for this work to be unnecessary — or twice as large as
it looks?* Then check.

**If nothing surprised you, do not manufacture a surprise.** Name the two things you
assumed and did not check, and check them. "The state is as expected" is a legitimate
finding — record it with its evidence.

## Phase 2 — The spine

**0. Who is the reader, and what can they actually do?** *(premise 3)* Agent or human ·
one session or a chain · frontier or cheap · which systems, credentials and repos they
hold · what they may decide alone. **Every later choice follows from this.** A human
needs time estimates and no boot order. A cheaper executor needs decisions pre-made
rather than analysis to reason over. A chained pair needs the handoff written into §0.

1. **What single sentence defines done?** If it needs "and also" three times, the scope
   is wrong.
2. **What is actually hard here?** Usually not the visible deliverable.
3. **What is genuinely blocked on a person?** *(premise 3)* Enumerate it, closed.
4. **What will it get wrong?** *(premise 1)* Every landmine you hit, it will hit.
5. **What is settled and must not be reopened?** Without this it re-litigates decisions
   that were already approved.

Q3 and Q5 come from the conversation, not from the systems — draft them while Phase 1
runs.

## Phase 3 — Write

Start from `TEMPLATE.md` in this directory; it holds the skeleton and the section
numbering. **`TEMPLATE.md` is the single source of the section list** — this page only
covers what authors get wrong.

### The invariant core — present at every size

Mission · **falsifiable** done-conditions · dated ground truth · scope OUT · landmines ·
provenance · report shape.

### The rest are triggered, not mandatory

| Include | When |
|---|---|
| Halt conditions | the work can touch something irreversible |
| The human's part | anything is genuinely blocked on a person |
| The analysis | the hard part is not the visible deliverable |
| Working agreement | house conventions exist — they are never inferred |
| The standard | the requester stated one ("zero mistakes in front of my boss") |

### Cite authority, never copy it

`AGENT_TEMPLATE.md:255` — *"Cite, do not duplicate. Authority docs are referenced by
section, not pasted."* This binds masterprompts. A copied rule is a **competing
authority** the reader meets first, at §0, before it ever opens the real one — and it
rots the moment the source is amended. Reference by path and section; state only the
project-specific delta. **Halt conditions and evidence standards are inherited, not
re-authored** — say so explicitly, because you also told the reader your lists are
complete.

### Every done-condition must be able to fail

> **Name the observation that would prove it false, made on something you do not
> control.**

Instances of the same defect: "improve X" names no observation · a `200 OK` observes
the wrong layer · "zero mistakes" is a value until translated into checkable bans · a
passing mock observes your own work. Test: describe the world in which you would have
to say "not done." Cannot? Rewrite the condition.

### Prose rules

- **Say why, not only what.** Reasoning survives the unanticipated case; steps do not.
- **Prefer the specific** — paths, identifiers, versions, counts.
- **Every claim carries its provenance** *(premise 2)*: observed (with date and how) ·
  told to you (by whom, when) · inferred (and marked as such).
- **Write imperatives to the reader**, not narration about them.
- **Length is not the enemy; padding is.** For each section, name the specific wrong
  action it prevents. No answer → cut it.
- **Write it in the language the executor will reason in.** State the output language
  separately.

## Phase 4 — Red-team *(premise 1)*

Read it **as the reader, with amnesia**. The check categories live in
`REVIEWER-PROMPT.md` — run that table against your own draft.

**High stakes → dispatch a fresh subagent with `REVIEWER-PROMPT.md` instead.** You
cannot simulate the amnesia the check depends on. Do not do both; the self-pass output
is discarded the moment the reviewer returns.

Naming the wrong turn beats describing the right one: *"if you find yourself doing X,
stop — that means Y."*

## Phase 5 — Deliver

**The document must land somewhere the executor can reach at paste time, addressable
and unedited, and the requester must be able to lift it out of the chat in one move.**

1. **A durable location** — a dated repo path for repo work, otherwise a file or link
   the executor can open.
2. **Immutable by reference** — commit and PR where version control exists; a dated
   filename where it does not.
3. **Hand over the artifact itself**, not a summary of it.
4. **Chat message** = the reorganizing fact, the shape of the work, what is still
   theirs. Do not paraphrase the document — they have it.

**Paste or point?** Pasting freezes a possibly-stale document and is size-bounded.
Pointing stays current but breaks when the branch merges and changes silently under the
executor. Pick deliberately and say which.

**Stamp it.** The document carries `STATUS: LIVE — not yet executed` from the moment it
is written; the executing session's last act is to stamp it `SHIPPED` / `SUPERSEDED by
<path>` / `ABANDONED — why`, with evidence pointers. Make that a done-condition of the
masterprompt itself. Without it, a spent masterprompt is indistinguishable from a live
one, and the most likely bad outcome of a re-paste is re-running work that already
shipped.

**Surviving a delayed paste.** State a shelf life, carry a runnable block that
regenerates ground truth, and pick the divergence protocol — when reality no longer
matches, does the executor adapt or halt? Slots for all three are in `TEMPLATE.md`.

*In this workspace:* `docs/plans/YYYY-MM-DD-<slug>-masterprompt.md`, the session's
designated branch, a draft PR, then `SendUserFile`.

---

## Calibration

Scale to the work. The invariant core stays; the triggered sections apply or do not.
A masterprompt with four sections and four landmines for a bounded task is **correct**,
not lazy.

The test is not word count. It is: **the only questions it comes back with are the ones
you decided in advance it should come back with.** The human's part and the halt
conditions are that complete question set; anything outside them is a gap in the
document. ("Asks nothing at all" is the wrong target — it rewards guessing.)

## Never embed what cannot be un-disclosed

A masterprompt is **transmitted** — pasted into an unknown session, committed, PR'd,
read by people you did not choose. Anything whose disclosure is irreversible is
referenced, never embedded.

- **Secrets.** No token, key, password, connection string or cookie — not truncated, not
  "just this once." Name the secret and where it lives, never its value.
- **Personal and customer data.** No names, phone numbers, addresses or exported rows in
  the document, the commit, the PR body, or a screenshot. Point at the query instead.
- **When a human must supply a secret**, design so no session holds it: they set it
  directly; the executor verifies through an observable side effect. **Prefer rotate
  over retrieve** — a fresh value set in two places beats extracting a live one and
  leaves nothing in a transcript. Where the platform supports a named secret reference,
  reference it and never see it.

If a masterprompt cannot be written without embedding one, the design is wrong.

## Final checklist

- [ ] Reconnaissance run at source, not from memory — and it produced observations
- [ ] The reorganizing fact is stated up front, or its absence is recorded with evidence
- [ ] Who the reader is, and what they hold, is written down
- [ ] Every done-condition names the observation that would prove it false
- [ ] Authority docs are cited by section, never copied
- [ ] Every volatile fact is dated; shelf life and divergence protocol stated
- [ ] Scope OUT is explicit and names specifics
- [ ] The human's part is complete and closed
- [ ] Landmines carry symptom → real cause → resolution
- [ ] No secret values, no personal data, anywhere
- [ ] Red-team pass done — self or dispatched, not both
- [ ] Status line present; delivery location durable and addressable
