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

A masterprompt is a single self-contained document pasted as the first message of a
fresh session, which then executes the work without coming back to ask what you meant.

**The one constraint that generates every rule below: the reader has total amnesia and
unlimited competence.** It is as capable as you. It knows nothing you learned. Every
fact you verified, every dead end you burned hours on, every decision that got reversed
— if it is not in the document it does not exist, and the new session will rediscover
it the slow way or contradict it confidently.

So the job is not "write instructions." It is **transfer everything expensive you know,
and nothing you merely believe.** Those are different disciplines, and the second is
where masterprompts fail.

## When to Use

- Multi-step work a fresh session will own end to end
- Any handoff across a context boundary — new session, another agent, another person
- Work Tom will re-run later, or hand to someone else
- Anything where being wrong is expensive

**When NOT to use:**

- The work fits in this session → **do it**. A masterprompt for a 20-minute task is
  procrastination with formatting.
- The ask is a question → answer it.
- Scope is still forming → that is a conversation, not a document.

## Quick Reference

| Phase | Output | Skippable |
|---|---|---|
| 1 Reconnaissance | Dated numbers from live systems | **Never** |
| 2 Spine | Done-sentence, the hard part, blockers, settled decisions | Never |
| 3 Write | The document | Never |
| 4 Red-team | Gaps closed, guesses marked | **Never** |
| 5 Deliver | File · commit · draft PR · SendUserFile | Never |

---

## Phase 1 — Reconnaissance

**Nothing is written before this phase produces numbers.**

The most common way a masterprompt fails is being written from a conversation summary —
compressed, lossy, and confidently stale. Go and look:

1. **Query the live systems.** Row counts, states, timestamps, last-success times. Not
   "the pipeline works" — `count(*)`, `max(created_at)`, and what they imply.
2. **Read the current code**, not your memory of writing it. Signatures drift.
3. **Check what actually runs.** Deployed functions, cron entries, feature flags, CI
   workflows. Grepping the repo is not sufficient — check deployed state.
4. **Establish the baseline.** Which failures are pre-existing? A session that inherits
   two broken tests and thinks it caused them chases ghosts for an hour.
5. **Read the governing docs** in authority order; note where they conflict.

**Greenfield — nothing running yet?** Reconnaissance still applies, it just changes
target. Verify the environment, the versions, the existing conventions to match, what
the neighbouring systems actually expose, and every constraint the work must live
inside. "There is nothing to query" is almost never true, and it is never a licence to
write from imagination.

Then hunt for **the fact that reorganizes everything** — the one that, once known,
changes what the work even is:

> `leads 188 · leads ever touched 0 · live leads ever received 0`
> A system described as "built and tested" had never carried a real record or been used
> by a human. That reframed the task from "finish the features" to "nothing here has
> ever been exercised."

If reconnaissance produced only confirmations, you did not look hard enough. Ask: *what
would have to be true for this work to be unnecessary — or twice as large as it looks?*
Then go check.

**Date every volatile claim** and instruct the reader to re-verify rather than trust.

## Phase 2 — Find the spine

Answer these before writing a section. They determine the document's shape.

1. **What single sentence defines done?** One testable sentence. If it needs "and also"
   three times, the scope is wrong.
2. **What is actually hard here?** Usually not the feature work. This becomes the
   analytical section — the thing that separates a masterprompt from a ticket. A
   checklist produces checklist-following; the analysis is what lets the session decide
   well in situations you failed to anticipate.
3. **What is genuinely blocked on a human?** Enumerate it, closed.
4. **What will it get wrong?** Every landmine you hit, it will hit.
5. **What is settled and must not be reopened?** Without this it helpfully re-litigates
   decisions that were already approved.

## Phase 3 — Write

### Mandatory sections

- **Usage header** — how to paste, what to attach, what it must produce.
- **Provenance** — written when, verified how, which docs are authoritative in what
  order. Enables re-verification.
- **Mission + done-conditions** — the one sentence, then a numbered table of **binary**
  conditions, each naming **the evidence that closes it**. Not "improve X" but "X is
  true, and here is the row / count / recording that proves it." No partial credit.
- **Ground truth** — dated reconnaissance numbers, split into what is built · what is
  not · what is known-broken-and-out-of-scope.
- **The analysis** — what the hard part actually is, in prose. The section a lazy
  prompt omits and the one that raises quality most.
- **Workstreams** — ordered, dependencies stated, each with an acceptance criterion
  tied back to a done-condition.
- **Scope IN and OUT** — the OUT list is not optional. Name specific files, systems and
  temptations. Unbounded scope is the standard failure mode.
- **The human's part** — complete, closed, minimal. Say "this list is complete";
  it stops a session stalling politely.
- **Landmines** — symptom → real cause → resolution. Highest value per token.
- **Halt conditions** — what makes it stop and surface rather than improvise.
- **Report format** — the shape the answer returns in.

### Situational sections

- **Working agreement** — boot order, mandatory skills, evidence standard, git rules,
  language rules. Include whenever house conventions exist; they are never inferred.
- **The standard being held to** — when the user states one ("zero mistakes in front of
  my boss"), translate it into two or three concrete engineering rules. Restated as a
  human standard it changes no behaviour; translated, it does.
- **Verification recipe** — exact commands and queries that prove each condition.

### Prose rules

- **Say why, not only what.** Reasoning survives the unanticipated case; steps do not.
- **Prefer the specific.** `sales_core.convert_lead()` beats "the conversion function."
- **Mark confidence honestly** — verified / assumed / unknown.
- **Write imperatives to the session**, not narration about it.
- **Length is not the enemy; padding is.** Every section must change what it does.
- **English for the prompt itself** unless told otherwise; user-facing output language
  is a separate instruction inside it.

## Phase 4 — Red-team your own document

Read it **as the receiving session, with amnesia**:

- **Where would I have to guess?** Every guess is a gap — close it or mark it UNKNOWN.
- **What reads as permission to do something dumb?** Tighten it.
- **Which "done" could I claim without doing the work?** Any condition satisfiable by a
  `200 OK` or a passing mock is not a done-condition.
- **What contradicts what** — between sections, and against the authority docs?
- **Which facts will be stale when this is pasted?** Mark them re-verify.
- **What am I asserting that I did not check?** Check it or downgrade it.

Naming the wrong turn beats describing the right one: *"if you find yourself doing X,
stop — that means Y."*

For anything high-stakes, hand the draft to a fresh subagent using
`REVIEWER-PROMPT.md` in this directory and fix what it finds.

## Phase 5 — Deliver

1. Write to `docs/plans/YYYY-MM-DD-<slug>-masterprompt.md`.
2. Commit on the designated branch, push, open a **draft PR** whose body says why the
   document exists and what reconnaissance produced it.
3. `SendUserFile` so it can be copied straight out.
4. In chat: the reorganizing fact, the shape of the work, what is still blocked on the
   user. Do not paraphrase the document — he has it.

## Calibration

Scale honestly. A masterprompt with three sections and four landmines for a bounded
task is **correct**, not lazy. Mandatory sections stay; their length varies.

| Scope | Shape |
|---|---|
| Bounded, one system | Mission · done-conditions · ground truth · landmines · scope OUT · report |
| Multi-system feature | Add workstreams, the analysis, the human's part, halt conditions |
| Production readiness / handoff | Full kit, plus working agreement and the standard |

The test is not word count. It is: **can it execute without asking me anything?**

## Secrets

- **Never embed a secret value** — no token, key, password, connection string or
  cookie. Not truncated, not "just this once."
- **Name the secret and where it lives** ("`LEAD_INGEST_TOKEN`, Supabase Edge Function
  secrets"), never its value.
- **When a human must supply one**, design so no session holds it: the human sets it
  directly; the session verifies through an observable side effect instead. Prefer
  **rotate over retrieve** — a fresh value set in two places beats extracting a live
  one and leaves no secret in a transcript. Where the platform supports a secret
  reference (e.g. a Make custom variable), reference it by name and never see it.
- If a masterprompt cannot be written without a secret in it, the design is wrong.

## Common Mistakes

| Mistake | Why it costs |
|---|---|
| Writing from the conversation summary | Lossy and stale; you assert false things confidently |
| "Improve the X experience" | Unfalsifiable — declared done having changed nothing |
| Omitting the OUT list | Scope creep is the standard failure mode |
| Burying the human's blockers | The session stalls, pesters, or invents around them |
| Skipping landmines | It re-burns every hour you already burned |
| Restating a human standard verbatim | "Zero mistakes" changes nothing until translated into rules |
| Padding to look thorough | Every section must change behaviour; the rest is noise |
| Assuming shared context | There is none. This is the whole constraint |
| Presenting a guess as fact | The most expensive thing the document can do |
| Letting `200 OK` close a condition | It proves one layer. Demand the observable end state |

## Final checklist

- [ ] Reconnaissance run against live systems, not memory — and it produced numbers
- [ ] The reorganizing fact is identified and stated up front
- [ ] Done-conditions are binary and each names its evidence
- [ ] Every volatile fact is dated and marked re-verify
- [ ] Scope OUT is explicit and names specifics
- [ ] The human's part is complete and closed
- [ ] Landmines carry symptom → real cause → resolution
- [ ] Halt conditions present
- [ ] No secret values anywhere
- [ ] Red-team pass done as the amnesiac reader
- [ ] Report format specified
- [ ] Delivered: file · commit · draft PR · SendUserFile

## Files

- `TEMPLATE.md` — the skeleton to fill.
- `REVIEWER-PROMPT.md` — hand a draft to a fresh subagent for adversarial critique.
