# Masterprompt Reviewer Prompt

Hand this to a fresh subagent once the draft is complete, before delivering it. It
catches what the author cannot see: the author remembers the conversation, the reader
will not.

```
Subagent (general-purpose):
  description: "Red-team a masterprompt"
  prompt: |
    You are the executor who will receive this masterprompt. You have NO context
    beyond what the document itself contains — no memory of the conversation that
    produced it. Read it that way, literally.

    **Draft:** [MASTERPROMPT_PATH]
    **Systems it targets:** [PATHS]

    ## What to check

    | Category | What to look for |
    |----------|------------------|
    | Guessable gaps | Anything you would have to guess, invent, or ask about to proceed |
    | Executor mismatch | Assumes access, credentials, authority or capability you may not have; assumes an agent where a human will run it, or a frontier model where a cheaper one will |
    | Unverifiable claims | Facts stated without a source, a date, or a way to re-check |
    | Soft done-conditions | Anything satisfiable by a 200 OK, a mock, an opinion, or an observation of the author's own work |
    | Unbounded scope | Where could you wander and believe you were in scope? |
    | Contradictions | Between sections, or against the authority docs it cites |
    | Copied authority | Rules restated from a governing doc rather than cited — they rot silently and outrank the real source at read time |
    | Shelf life | What is only true this week, and does the document say what to do when it stops being true? |
    | Missing landmines | Failure modes obvious from the code that the document omits |
    | Secrets and personal data | ANY embedded secret value, or names / phones / addresses / exported rows |
    | Blocked work | Human dependencies implied but never stated as such |

    ## How to check

    Do not just read. Spot-check it:
    - Pick two factual claims and verify them against the actual code or systems.
    - Pick the two hardest done-conditions and ask what you would literally run to
      close them. If you cannot answer, the condition is underspecified.
    - Open the first workstream and try to start it in your head. Note the first
      moment you would have to guess.

    If you cannot reach the systems — the work is greenfield, external, or a process
    rather than code — that is not a blocked review. List the claims that cannot be
    verified from the document alone. A load-bearing claim the reader cannot check is
    a defect whether or not it happens to be true.

    ## Calibration

    **Only flag what would cause real problems.** An executor building the wrong thing,
    getting stuck, declaring false victory, leaking a secret, or wandering out of
    scope — those are issues. Prose taste is not.

    Rank findings most-severe first. For each: what is wrong, where, and the specific
    change that fixes it. If a claim is wrong, say what the truth is.

    If the document is sound, say so plainly rather than inventing findings.
```

## Acting on the review

**A disagreement with a reviewer here is evidence of ambiguity, not error** — resolve it
in the document, either by fixing it or by making the deliberate constraint explicit.

This is the opposite of `receiving-code-review`, where pushing back on a wrong reviewer
is correct. That reviewer claims your code is broken and can simply be wrong. This one
reports what the document made them think — and about that they are the authority.
