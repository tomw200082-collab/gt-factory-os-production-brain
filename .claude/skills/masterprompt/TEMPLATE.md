# Masterprompt skeleton

Copy, fill, delete what does not apply. Guidance in `<angle brackets>` — remove it.
**This file is the single source of the section list.** `SKILL.md` covers the phases and
the principles; per-section how-to lives here, beside the section it serves.

Section order is deliberate: the reader must know who they are and how to work, then
what done means, then what is true, before it reads a single task.

---

```markdown
# MASTERPROMPT — <the outcome, not the activity>

**STATUS: LIVE — not yet executed**
<the executing session's last act is to change this to SHIPPED / SUPERSEDED by <path> /
ABANDONED — why, with evidence pointers>

> **Usage:** paste this entire file as the first message of a fresh session with
> <repos / systems> attached. It takes <the thing> from <state now> to <state after>.
> It halts for you only where a human must genuinely act — §6 is that complete list.
>
> **Provenance:** written <date>, from <what was measured, where, when>.
> Authority: <docs, in order> — cited below, never copied.
>
> **Shelf life:** §2 is presumed wrong if pasted after <date ~2 weeks out>. Re-run §2.5
> first. If reality no longer matches §2, <adapt / halt and surface> — pick one.

## 0. How to work
<Include only what applies. Do not number empty headings — they get filled with noise.>

- **Who you are here:** <agent or human · one session or a chain · what systems,
  credentials and repos you hold · what you may decide alone>
- **Read first:** <paths, in order>
- **Authority:** <doc + section>, cited not restated. Where this document and an
  authority doc disagree, the authority doc wins and this document is wrong.
- **Halt conditions, evidence standard, git discipline:** inherited from <path §section>.
  Deltas specific to this work only: <…>
- **The standard:** <the requester's words, then 2–3 checkable prohibitions>
- **Language:** this document is in English because that is the register the executor
  reasons best in; data literals stay in their own script, in backticks, and are never
  translated. **Output language: concise English** — short sentences, no preamble, no
  restating the question. <adjust register if the requester asked for something else>

## 1. Mission and definition of done
**One testable sentence:** <…>

| # | Condition | The observation that would prove it false |
|---|---|---|
| D1 | <binary> | <the command or query itself, not a description of it> |

Anything not on this list is out of scope unless <requester> asks.

### 1.1 Settled — do not reopen
<decisions already made and approved, with who approved and when>

## 2. Ground truth — measured <date>; re-verify at boot
### 2.1 What is built and live
### 2.2 The numbers <paste real output>
### 2.3 What is NOT built
### 2.4 Known-broken, adjacent, out of scope
### 2.5 Re-verification block
```sql
-- the actual runnable commands that regenerate 2.2, so re-checking costs one paste
```

## 3. What the hard part actually is
<3–6 reframes. Each: what the work looks like from outside · what it actually is · what
that changes about the ordering. "The intake is a pipe with no water in it."
"Architecturally complete and functionally dead." "A queue containing everything is not
a queue." Omit this section when the hard part IS the visible deliverable.>

## 4. Workstreams
### W1 — <name>
<what, why, exact spec>
**Acceptance:** <which D-condition this closes>

## 5. Scope
**IN:** everything in §4.
**OUT — do not touch, do not "improve":** <named files, systems, temptations>

## 6. <Requester>'s part — the complete list, nothing else is theirs
**A.** <action · why only a human can do it · how long it takes>

## 7. Landmines — do not rediscover these
<Select from: every hour you burned · every place the obvious diagnosis was wrong ·
every pre-existing failure that will look like the reader's fault · every tool whose
green light means less than it appears · every case where two causes produce identical
symptoms.>
1. **<symptom>** — <real cause> → <resolution>.

## 8. Halt conditions
<Inherited set cited in §0. List here ONLY the additions specific to this work.>
- <condition> → **STOP**, surface, do not improvise.

## 9. Final report
1. What a stranger can now watch working, end to end
2. Each done-condition ✅/❌ with its evidence pointer — no partial credit
3. The numbers
4. The artifacts, and where they are
5. What is still <requester>'s, and what remains genuinely unfinished
6. The single next action

If anything is not ready, say so first and plainly.
<Where the house has a handoff format — e.g. AGENT_TEMPLATE.md §Output format with
tokens matching VERDICT_GLOSSARY.md — default to it instead of inventing a shape.>
```

---

## Filling the harder sections

**§1 when the deliverable is an answer, not an artifact.** Research, an assessment, a
decision memo — there are no rows to point at. The condition is met when the question is
answered with: each claim's source named and dated · a stated confidence per claim ·
what was checked and found *not* to matter · the observation that would change the
answer. "The analysis is thorough" is the "improve X" of research work. For this shape
§3 is not preliminary — it *is* the deliverable, so weight the phases accordingly.

**§0 translating a stated standard.** Ask what a violation would look like **to the
person who stated it**, then write those two or three as prohibitions with observable
subjects. "Zero mistakes in front of my boss" → *nothing on screen may be false ·
nothing may be dead · nothing may depend on luck.*

**§7 is worth more than §4.** Tasks the reader could infer; landmines it cannot.

**§6 must end closed.** Everything not listed is the executor's.

**No secret values. No personal or customer data.** Not in the document, the commit, the
PR body, or a screenshot. Name the secret and where it lives; point at the query rather
than pasting rows.
