# Masterprompt Reviewer Prompt

Use this when dispatching a subagent to critique a masterprompt draft.

**Purpose:** Catch the gaps the author cannot see, because the author remembers the
conversation and the reader will not.

**Dispatch after:** the draft is complete, before delivering it.

```
Subagent (general-purpose):
  description: "Red-team a masterprompt"
  prompt: |
    You are the session that will receive this masterprompt. You have NO context
    beyond what the document itself contains — no memory of the conversation that
    produced it. Read it that way, literally.

    **Draft:** [MASTERPROMPT_PATH]
    **Repos/systems it targets:** [PATHS]

    ## What to check

    | Category | What to look for |
    |----------|------------------|
    | Guessable gaps | Anything you would have to guess, invent, or ask about to proceed |
    | Unverifiable claims | Facts stated without a source, date, or way to re-check |
    | Soft done-conditions | Any condition satisfiable by a 200 OK, a mock, or an opinion |
    | Unbounded scope | Where could you wander and believe you were in scope? |
    | Contradictions | Between sections, or against the authority docs it cites |
    | Stale facts | Volatile numbers with no date and no re-verify instruction |
    | Missing landmines | Failure modes obvious from the code that the document omits |
    | Secrets | ANY embedded secret value — token, key, password, connection string |
    | Blocked work | Human dependencies that are implied but never stated as such |

    ## How to check

    Do not just read. Spot-check it:
    - Pick two factual claims and verify them against the actual code or systems.
    - Pick the two hardest done-conditions and ask what you would literally run to
      close them. If you cannot answer, the condition is underspecified.
    - Open the first workstream and try to start it in your head. Note the first
      moment you would have to guess.

    ## Calibration

    **Only flag what would cause real problems.** A session building the wrong thing,
    getting stuck, declaring false victory, leaking a secret, or wandering out of
    scope — those are issues. Prose taste is not.

    Rank findings most-severe first. For each: what is wrong, where, and the specific
    change that fixes it. If a claim is wrong, say what the truth is.

    If the document is sound, say so plainly rather than inventing findings.
```

## Acting on the review

Fix findings; do not argue with them. A finding you disagree with usually means the
document is ambiguous — which is the same defect, seen from the other side.

The exception: a reviewer that flags a *deliberate* constraint as a gap. Then make the
constraint explicit in the document rather than removing it.
