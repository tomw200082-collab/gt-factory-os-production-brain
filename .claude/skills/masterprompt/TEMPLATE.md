# Masterprompt skeleton

Copy, fill, delete what does not apply. Guidance in `<angle brackets>` — remove it.
Section order is deliberate: the reader must know how to work, then what done means,
then what is true, before it reads a single task.

---

```markdown
# MASTERPROMPT — <one line: the outcome, not the activity>

> **Usage:** paste this entire file as the first message of a fresh session
> with <repos / systems> attached. It takes <the thing> from <state now> to
> <state after>. It halts for you only where a human must genuinely act — §6 is
> that complete list.
>
> **Provenance:** written <YYYY-MM-DD> from live-verified state (<what you
> queried, which project/system, when>). Authority: <governing docs, in order>.

## 0. How to work

### 0.1 Boot order
<numbered list of what to read, in order, before anything>
**Authority order:** <A → B → C>. On conflict, higher wins.

### 0.2 The standard
<the user's stated bar, translated into 2–3 concrete engineering rules>

### 0.3 Skills / tools that are mandatory
<moment → skill table>

### 0.4 Evidence standard
<what counts as proof here. What does not.>

### 0.5 Git / delivery conventions
<branch, staging discipline, PR expectations, merge authority>

### 0.6 Language
<code/commits vs user-facing>

## 1. Mission and definition of done
**One testable sentence:** <…>

| # | Condition | Evidence required |
|---|---|---|
| D1 | <binary> | <row / count / recording> |

Anything not on this list is out of scope unless <user> asks.

## 2. Ground truth — verified <date>, re-verify at boot
### 2.1 What is built and live      <table: piece · state · evidence>
### 2.2 The numbers that define the work   <code block of real counts>
### 2.3 What is NOT built
### 2.4 Known-broken and adjacent, not in scope

## 3. What the hard part actually is
<prose. the reframing. why most of the remaining work is not what it looks like.>

## 4. Workstreams
### W1 — <name>
<what, why, exact spec, and:>
**Acceptance:** <which D-condition this closes>

## 5. Scope
**IN:** everything in §4.
**OUT — do not touch, do not "improve":** <named files, systems, temptations>

## 6. <User>'s part — the complete list, nothing else is theirs
**A.** <action, why only a human can do it, how long it takes>

## 7. Landmines — do not rediscover these
1. **<symptom>** — <real cause> → <resolution>.

## 8. Halt conditions
- <condition> → **STOP**, surface, do not improvise.

## 9. Final report
State, in this order: <1..n>
If anything is not ready, say so first and plainly.
```

---

## Reminders while filling it

- §2.2 comes from **running queries**, not from memory.
- Every D-condition must be **failable**. If you cannot describe the observation that
  proves it false, rewrite it.
- §7 is worth more than §4. Spend the time there.
- §6 must end closed: everything not listed is the session's.
- No secret values. Name the secret and where it lives.
