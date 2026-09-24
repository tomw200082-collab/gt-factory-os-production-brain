# MASTERPROMPT — the sales-report Routine publishes every morning without anyone tapping "approve"

**STATUS: LIVE — not yet executed**
<!-- The executing session's last act is to change this line to SHIPPED / ABANDONED — why,
with evidence pointers (D1–D3 below). -->

> **Usage:** paste this entire file as the first message of a fresh Claude Code session
> with `gt-factory-os-production-brain` attached. It takes the Routine from "parks every
> morning on one approval prompt" to "publishes and emails with nobody watching". The
> fix is one sharing change that only Tom can click; this session diagnoses, walks Tom
> through it, and proves it held.
>
> **Provenance:** written 2026-09-24 from the Routine run of that morning (session
> `a3ccc5ec-bc04-512d-a602-66061e220e8c`): its tool-call timestamps, its Claude Code debug
> log, a live settings experiment, and the official docs fetched the same hour
> (`code.claude.com/docs/en/routines.md`, `artifacts.md`, `cloud-environments.md`,
> `permission-modes.md`). Every fact in §2 was observed there, not recalled.
> Authority: the docs above, then `gt-factory-os-production-brain/CLAUDE.md`, then the
> standing Routine instruction
> `docs/plans/2026-08-30-weekly-sales-report-routine-masterprompt.md` — cited, never copied.
>
> **Shelf life:** presumed stale after 2026-10-08. Re-run §2.5 first. If §2.5 shows the
> artifact is already not public, or the docs' republish rule has changed, **halt and
> report to Tom** — do not adapt.

## 0. How to work

- **Who you are here:** a fresh session. You can read artifacts (`Artifact action:"read"`),
  read Gmail, read files in the brain repo. You **cannot** change an artifact's sharing —
  the Artifact tool states this and only the owner can do it from the page's Share
  control. So Tom clicks; you diagnose, instruct, and verify.
- **Read first:** §2 of this file, then `code.claude.com/docs/en/routines.md` (the section
  starting "When the routine's schedule or **Run now** starts a run") — fetch it live.
- **Authority:** where the live docs and this file disagree, the docs win; say so in the
  final report.
- **Halt conditions, evidence standard:** inherited from `CLAUDE.md` §Stop conditions and
  §Evidence. Additions in §8.
- **The standard (Tom, 2026-09-24):** "it must work 100%, leave no room for doubt." As
  checkable bans: no "should work now" without the §1 observation · no settings-file or
  allowlist change offered as the fix (§7 landmine 1 proves it does nothing) · no second
  fix attempted in parallel, so a pass is attributable.
- **Language:** this file is English; UI labels and data stay as written.
  **Output language: concise Hebrew** — Tom is the reader of every step. Short sentences,
  numbered clicks, no preamble.

## 1. Mission and definition of done

**One testable sentence:** a scheduled or **Run now** firing of the sales-report Routine
republishes `https://claude.ai/code/artifact/ad0dd380-d95e-4a21-94e3-af9ee386fc88` and sends
its email with no approval prompt reaching Tom.

| # | Condition | The observation that would prove it false |
|---|---|---|
| D1 | The artifact is no longer shared publicly | `Artifact action:"read" url:<the URL above>` → header line still contains `shared with anyone with the link` (or any other public-share wording) |
| D2 | A Routine run publishes unprompted | Tom presses **Run now** (or waits for the next Sunday–Thursday 09:00 firing) and **either** an approval prompt reaches him **or** the report email's send time is more than 20 minutes after the `הנתונים עד HH:MM` time in its own subject line |
| D3 | This file is stamped | the `STATUS:` line above still reads `LIVE` at the end of the session |

Anything else is out of scope unless Tom asks.

### 1.1 Settled — do not reopen

- The artifact URL is fixed (Tom, 2026-08-30 masterprompt §1.1). Do not create a new
  artifact to dodge the rule — publishing a *new* artifact always asks (routines.md).
- The Routine and its pipeline are unchanged by this work.

## 2. Ground truth — measured 2026-09-24; re-verify at boot

### 2.1 The rule that decides it (routines.md, fetched 2026-09-24)

> Routines run autonomously … without stopping for approval apart from some artifact
> actions. When the routine's schedule or Run now starts a run, Claude republishes an
> existing artifact without asking only when all of these hold:
> · You can edit the artifact and it belongs to your own organization
> · The artifact isn't shared publicly, and isn't shared with specific people or your
>   organization with the latest version chosen as the version viewers see
> · The publish carries only the page, with no supporting files … and doesn't force over a newer version
> · The page holds no grant that reaches beyond the page, such as connector calls
> In every other case … Claude asks first.

### 2.2 How the artifact measures against it (observed 2026-09-24)

| Condition | State | Evidence |
|---|---|---|
| Owned, editable, own org | ✅ | `Artifact read` header: `owned by you` |
| **Not shared publicly** | ❌ **the blocker** | `Artifact read` header: `shared with anyone with the link (viewers see a pinned earlier version, not this live version)`; publish result: `shared as "Anyone with the link"` |
| Page only, no force | ✅ | the pipeline publishes `report.html` alone, no `files`, no `force` |
| No grant beyond the page | ✅ | `Artifact read`: `no runtime capabilities declared` |

The cost, measured in that run's transcript (UTC):

```
mcp__Shopify__graphql_mutation   05:03:17.168 → 05:03:17.756   no wait
mcp__Gmail__send_message         06:23:28.586 → 06:23:29.322   no wait
Bash (every call)                permissionDecisionMs ≤ 88 ms   no wait
Artifact publish                 05:07:39.018 → 06:22:13.787   parked 1 h 15 min until Tom approved
```

The Artifact publish was the only call that waited for a person. The email then went out at
09:23 Israel time for data stamped 08:05.

### 2.3 What is NOT the cause (tested; do not retry)

- **Settings / allowlists.** The session launches with `--allowed-tools … Bash … mcp__Shopify__* … mcp__Gmail__*`
  — those were never the problem. The cloud Claude Code process reads permissions only from
  `/root/.claude/settings.json` and `/home/user/.claude/settings.json`; both absent. The
  brain repo's committed `.claude/settings.json` is **not loaded** (debug log:
  `allow rules for destination 'projectSettings' with 0 rule(s)`), matching
  cloud-environments.md: a multi-repo session "starts above the clones and doesn't read them".
- **An `Artifact` allow rule does not release it.** Experiment 2026-09-24 06:28Z: wrote
  `{"permissions":{"allow":["Artifact"]}}` to `/root/.claude/settings.json`; the log confirmed
  `allow rules for destination 'userSettings' with 1 rule(s): ["Artifact"]`; the next
  republish still waited `permissionDecisionMs=88536` for Tom. File removed afterwards.
- **Permission mode.** Routines have "no permission-mode picker" (routines.md); cloud sessions
  ignore `bypassPermissions` and `dontAsk` from settings (permission-modes.md).

### 2.4 Adjacent, out of scope

- Public viewers of that link already see a *pinned earlier version*, not the live one — so
  the public link currently serves stale numbers, and it exposes customer names and revenue
  to anyone holding the URL, no sign-in required.
- Because repo settings are not loaded in multi-repo Routine sessions, the repo hooks (e.g.
  `.claude/hooks/no_autowatch.sh`) do not run there either. Report it to Tom as a finding;
  do not fix it here.

### 2.5 Re-verification block — run at boot

```text
1. Artifact action:"read" url:"https://claude.ai/code/artifact/ad0dd380-d95e-4a21-94e3-af9ee386fc88"
   → copy the header's sharing phrase verbatim.
2. WebFetch https://code.claude.com/docs/en/routines.md
   → confirm the four republish conditions in §2.1 still read the same.
3. Gmail search: subject:"דוח המכירות מעודכן" newer_than:14d
   → for each message: send time vs the HH:MM in its subject. Gaps > 20 min = mornings that parked.
```

If step 1 already shows no public sharing, skip to D2 — the cause may have moved; halt if D2 then fails.

## 3. What the hard part actually is

- **It looks like a permissions setting. It is a sharing setting.** Every instinct (allowlist,
  settings.json, bypass mode) is wrong here, and each was tested. The only lever is the
  artifact's audience.
- **The decision is Tom's, not technical:** who, besides Tom, needs to open this page? That
  answer picks the option in §6.

## 4. Workstreams

### W1 — Boot and confirm (§2.5)
Run §2.5. Tell Tom, in one Hebrew paragraph, the blocker and the three measurements.
**Acceptance:** Tom has the diagnosis with evidence.

### W2 — Walk Tom through the change (§6 A–B)
Ask the one question in §6A. Then give numbered clicks for the matching option. Label the
controls as the docs name them (the **Share** control in the page header; the audience;
"which version viewers see"). If you do not know an exact on-screen label, say so rather
than inventing one.
**Acceptance:** D1 — re-run §2.5 step 1 and quote the new header.

### W3 — Prove it (§6 C)
Ask Tom to press **Run now** on the Routine and to tell you whether any approval prompt
appeared. Then check Gmail: the new email's send time vs its subject stamp.
**Acceptance:** D2.

### W4 — Stamp
Change this file's `STATUS:` to `SHIPPED` with the D1–D3 evidence, or `ABANDONED — why`.
Commit on the session's designated branch, open a draft PR, then immediately
`unsubscribe_pr_activity` (brain `CLAUDE.md` §Watching).
**Acceptance:** D3.

## 5. Scope

**IN:** §4.
**OUT — do not touch:** the Routine's prompt, schedule, repos or connectors · the
pipeline scripts and `SKILL.md` · any `.claude/settings*.json` (§2.3) · publishing to the
artifact yourself from this session (it would ask Tom and prove nothing about Routine runs)
· creating a new artifact or Routine · the second artifact `9d94c4ff-7ea2-4ddc-a148-0a1781ad1c3e`.

## 6. Tom's part — the complete list, nothing else is his

**A. One answer: does anyone besides you need to open this page?**
- **No** (the email goes only to Tom) → Option 1.
- **Yes** → Option 2, knowing its cost.

**B. The click (about 1 minute).** Open the artifact URL → **Share** in the page header →
- **Option 1 (recommended):** set the audience to private / only you. You still see every
  version live as the owner. Anyone else holding the old link loses access.
- **Option 2:** share within the organization (Team/Enterprise plans only), and set the
  version viewers see to a **pinned** version, not "latest". The Routine then republishes
  silently, but viewers see only the pinned version until Tom moves the pin. Public
  ("Anyone with the link") must be off in both options.

**C. The proof (about 15 minutes, one extra report email today):** press **Run now** on the
Routine and say whether an approval prompt appeared. Declining is acceptable; D2 is then
checked on the next Sunday–Thursday 09:00 run instead.

## 7. Landmines

1. **"Add Artifact to the allowlist" / "commit a settings.json"** — looks like the fix, is not:
   tested 2026-09-24, the allow rule loaded and the publish still parked 88 s. → The rule is
   in routines.md §2.1; only sharing changes the outcome.
2. **Republishing from this interactive session to "test"** — it will prompt Tom because this
   is not a Routine run, and it proves nothing about Routine behaviour. → Test only with
   **Run now** (W3).
3. **Sharing it with the organization and leaving "latest" as the viewer version** — still
   fails condition 2; the Routine keeps asking. → Pin a version, or keep it private.
4. **Re-sharing publicly later** — silently brings the daily prompt back. → Tell Tom this in
   the final report, in one line.
5. **An email that arrives on time is not proof by itself** — Tom may have approved within a
   minute. → D2 requires both: no prompt reached Tom, and the gap ≤ 20 min.

## 8. Halt conditions

- §2.5 shows the docs' republish rule changed → **STOP**, report the new text, do not improvise.
- D1 passes but D2 fails (a Run now still prompts) → **STOP**. Report the exact prompt text Tom
  saw and the run's time; do not try settings, a new artifact, or a second fix.
- Tom's answer to §6A is neither option (e.g. "public must stay") → **STOP**: the prompt cannot
  be removed while the page is public; state that plainly and end.

## 9. Final report

Concise Hebrew, to Tom:
1. What changed, in one line.
2. D1–D3 ✅/❌, each with its evidence (the header phrase, the Run now result, the email gap).
3. The one thing that would bring the prompt back (landmine 4).
4. The adjacent finding from §2.4 (hooks don't run in multi-repo Routines), as a note.
5. The single next action, or "none".
