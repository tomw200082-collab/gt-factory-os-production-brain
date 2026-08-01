---
name: close-session
description: >
  Optimally close out a Claude Code work session — leave nothing dangling and nothing
  risky done silently. Detects every open loop the session created (unmerged PRs,
  live self-scheduled triggers/probes, active PR webhook subscriptions, open tasks,
  uncommitted work, uncaptured knowledge), auto-runs the safe reversible cleanup,
  PAUSES for approval on anything risky or irreversible, preserves durable knowledge
  into the production brain by type, and delivers a forward-looking closure report.
  Use this skill WHENEVER the user signals they want to end, wrap up, or optimally
  close a working session — "סגור סשן", "נסגור את הסשן", "סגירת סשן", "בוא נסיים",
  "לסגור פינות לפני שאני הולך", "close session", "wrap up", "let's close out",
  "end of session", "tie off loose ends" — even if they don't name the skill.
  Do NOT trigger for closing a single PR or issue (that is a GitHub action), for a
  release / deployment go-no-go gate (that is gate-close), or for a start-of-day /
  morning brief (that is the opposite).
---

# Close Session — optimal work-session closure

You are the session closer. A session is closed *optimally* when three things are true:

1. **Nothing dangles.** Every loop the session opened is either finished, explicitly deferred, or handed to whoever owns it next.
2. **Nothing risky happened silently.** Reversible cleanup runs on its own; anything irreversible or outward-facing waits for the human's word.
3. **The knowledge survives the container.** Durable learnings are committed into the production brain — by type — before the ephemeral session is gone.

Your job is to reach that state with the least friction — do the safe work, surface the risky work, and end with a report the user (and the next session) can act on cold.

---

## The one rule that shapes everything: safe runs, risky waits

The user picked this posture deliberately. Sort every candidate action into exactly one bucket and act accordingly.

| Bucket | Meaning | What you do |
|---|---|---|
| **SAFE** | Reversible, single-scope, affects only this session, no outward/customer/money impact — **or** an action the user has standing written authority for | **Do it automatically.** Report it. |
| **RISKY** | Irreversible, outward-facing, mass-scale, money-/customer-facing, ambiguous ownership, or touches an authority doc | **Never do it silently.** State exactly what would happen and get a yes first. |

**When unsure which bucket → it's RISKY.** Uncertainty is not a reason to act; it's a reason to ask.

### SAFE — auto-run (no approval needed)
- **Cancel this session's own pending self-probes / wake-ups** (self-bind reminders or self-scheduled check-ins this session created). Cancelling a future self-message is fully reversible and touches only this session.
- **Mark genuinely-completed tasks done** in the session task list.
- **Merge a PR when its *required* checks are green AND the change is verified** (tests N/N, typecheck/lint clean, or equivalent evidence the session actually produced). This is the standing autonomous-merge authority — no need to pause. A *non-required* check that is red does **not** block; name it and say why it's non-blocking (e.g. a known infra flake), then merge. After merging, the PR is terminal.
- **Retire a webhook subscription whose PR just became terminal** (merged/closed) — it has nothing left to report.
- **Append durable knowledge to a *non-authority* type-registry or domain skill** in the brain repo (see step 4) — reversible doc appends, committed on the working branch so the knowledge lands. Includes skill §LEARNED appends, self-compaction, and the CURRENT_STATE resolved-bullet sweep (deletions/pointers only).
- **Draft** the closure report and any summary (no external effect until sent).
- **Run read-only status checks** — PR mergeability + check state, trigger list, task list, `git status`.

### RISKY — pause for approval (present, then wait)
- **Merging a PR that has a red/failing *required* check, or an unverified high-blast-radius change.** Never merge these on authority alone — surface and wait. "Verified" means the session has real evidence; no evidence → not safe → pause.
- **Unsubscribing from a PR that is still open** (not merged/closed). A subscription isn't finished until its PR is terminal — leave it.
- **Deleting any trigger that is not this session's own probe** — recurring/operational triggers (daily loops, weekly crons) and other sessions' check-ins are off-limits. When you can't prove a trigger belongs to this session, leave it.
- **Writing or altering any AUTHORITY doc** — in the brain repo that is `CLAUDE.md`, `EXECUTION_POLICY.md`, `CURRENT_STATE.md`, `WORKSPACE_MAP.md`, `ACTIVE_NOW.md`, `AI_BRAIN_ROUTER.md`, `docs/decisions/LOCKED_DECISIONS.md`, `docs/contracts/SCHEMA_GUIDANCE.md`. Draft a patch, route to Tom / `ops-docs-curator` / `factory-os-governor`, never write directly.
- **Production deploy or applying migrations to the production DB** — deliberate, explicitly-flagged steps, never part of a close.
- **Sweeping up unrelated uncommitted work** — surface it; commit only the specific files the close itself authored (never `git add -A` / `git add .`).
- **Any other write to an external/production system** (Postgres, Shopify, LionWheel, Green Invoice, etc.) — out of scope for closing.

---

## The closure workflow

Run these in order. Steps 1–2 and 4 are automatic; step 3 is the interactive checkpoint; step 5 finishes the close.

### Step 1 — Scan for open loops (silent, read-only)

Build a picture of everything the session left open. Check each source; skip what doesn't apply.

- **Unmerged PRs** — for each repo the session touched, list open PRs on the working branch and read each one's mergeability + check status (which checks are *required* vs not, which are red and why). GitHub MCP: list/read pull requests. Discover exact tool names via ToolSearch if the prefix differs in this environment.
- **Uncommitted work** — `git status` in each working tree; note staged/unstaged/untracked and whether any authority docs are dirty.
- **Live triggers / probes** — list scheduled triggers (claude-code-remote MCP: `list_triggers`). For each, decide: *this session's own probe* (safe to cancel) or *someone else's / operational* (leave it). Distinguish by the trigger's bound session, name, and purpose.
- **Active PR webhook subscriptions** — recall which PRs this session subscribed to / was asked to watch. (There is usually no "list subscriptions" call — rely on the session's own record.)
- **Open tasks** — read the session task list; separate genuinely-done from still-open.
- **Uncaptured knowledge** — did the session produce durable facts, decisions, patterns, gaps, or gotchas worth keeping? Note each with its *type* (you'll route by type in step 4).

Do this silently. Do not narrate the scan; produce the result in step 3.

### Step 2 — Run the SAFE cleanup automatically

Execute everything in the SAFE bucket now:
- Cancel this session's own pending self-probes.
- Mark completed tasks done.
- Merge PRs that clear the bar (required green + verified); then retire those PRs' now-terminal webhook subscriptions.
- (Knowledge writes happen in step 4.)
- Draft (do not yet send) the closure report.

Keep a short ledger of what you did — it goes into the report.

### Step 3 — Present the RISKY items and wait

Show the user a single, scannable checkpoint: what you already handled (SAFE, done) and what needs their word (RISKY, pending). For each risky item give enough context to decide without scrolling back — PR number + title + which required check is red, trigger name + why it's ambiguous, the authority-doc patch you're proposing, etc.

Then stop and let them choose per item. Honor their answers exactly: act only on what they approve; leave the rest as explicitly-deferred (record it in the report so the next session sees it).

### Step 4 — Preserve the knowledge (typed routing — the self-building tier system, Tom 2026-08-01)

The workspace runs a 3-tier knowledge architecture. Route every durable fact to the tier that matches its *decay rate* — this step is what makes the architecture grow itself, so run it every close, no exceptions:

- **Tier 0 — boot docs** (`CLAUDE.md`s, `CURRENT_STATE.md`): invariants, traps, open gaps ONLY. Loaded every session — every line here costs credits forever, so a line must earn it by being true in 3 months.
- **Tier 1 — domain skills** (`.claude/skills/<domain>/SKILL.md`): all depth. Descriptions (~1 line) auto-load every session; bodies load only when the domain is touched. This is where knowledge is FREE until needed.
- **Tier 2 — queries & git**: anything volatile. State is *asked*, never written; narrative lives in commit messages.

| Knowledge type | Decay test | Destination | Write? |
|---|---|---|---|
| Domain depth — architecture, contracts, gotchas, canonical queries of one subsystem (Shopify, LionWheel, GI, planning…) | needed only when touching that domain | matching `.claude/skills/<domain>/SKILL.md` → append to **§LEARNED** (create the skill from the template below if none matches) | **auto** |
| Global trap / invariant, backend-scoped | true in 3 months, any task | `gt-factory-os/CLAUDE.md` (Claude-writable) | **auto** |
| Global trap / invariant, governance-scoped | " | brain `CLAUDE.md` | **propose only** (Tom sole writer) |
| False green / overstated readiness | — | `docs/false_green_registry.md` (match schema, append) | **auto** |
| Operational gap / data-quality finding | — | `docs/gap_registry.md` (next `GAP-###`) | **auto** |
| Cross-domain lesson fitting no single skill | cost real rework | `docs/lessons_learned.md` (dated block) | **auto** |
| Locked decision | — | `docs/decisions/LOCKED_DECISIONS.md` | **propose only** |
| Schema / contract rule | — | `docs/contracts/SCHEMA_GUIDANCE.md` | **propose only** |
| **State — status, counts, percentages, "currently X"** | stale within weeks | **⊥ write ANYWHERE.** Ensure a query answers it; add the query to the skill's §Canonical queries if missing | — |
| Session narrative — what happened, in what order | immediately | commit messages only. ⊥ docs | — |

**Skill hygiene (autonomous, no approval — skills ∉ authority docs):**
- §LEARNED > 30 lines → distill into the skill's body sections, clear the log, stamp "Last distilled <date>" in its header.
- Skill body > ~200 lines → split by concern (`<domain>-<concern>`); keep trigger keywords in every description — descriptions are the router.
- New-skill template: frontmatter `name` + `description` **listing trigger keywords** (incl. Hebrew), then sections: `## Architecture` · `## Traps` · `## Canonical queries` · `## Monitoring` · `## OPEN` · `## LEARNED — append-only log` with the 30-line self-compaction note. Model: `.claude/skills/shopify-sync/SKILL.md`.

**CURRENT_STATE sweep (part of every close, Tom 2026-08-01 lean mandate):** any bullet this session *resolved* → delete it or compress to a one-line pointer at the skill. Deletions/compressions of resolved items ride the session's work; **new claims or status changes remain propose-only**. A boot doc that says something a query contradicts is worse than an empty one.

Rules:
- **Read the target first**, match its exact format, **append** — never rewrite others' entries. Stage only the files this step touched (never `git add -A`), commit + push on the working branch so the knowledge lands.
- Authority docs (propose-only rows above): draft the patch, put it in the report, route to the owner. RISKY — waits.
- Show every entry written and every patch proposed in the closure report — visible and revertible.

### Step 5 — Deliver the closure report

End with the report (template below), then stop. The report is the session's last word — written so the next session, or the user tomorrow, can pick up cold.

---

## Closure report — use this structure

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧹 סגירת סשן — [one-line what this session was about]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ נסגר אוטומטית (בטוח/הפיך):
  • [safe action taken] …

⏸️ ממתין לאישורך (מסוכן/בלתי-הפיך):
  • [risky item] — [what would happen if approved]

🔁 נדחה במפורש / הועבר הלאה:
  • [deferred loop] — [owner or next step]

🧠 ידע שנשמר (נחת ב-production-brain, לפי סוג):
  • [type] → docs/<registry>.md — "[one-line entry]"  ✅ נכתב + נדחף
  • [authority-doc knowledge] → הצעת patch ל-<doc>, נותב ל-<owner>  ⏸️ ממתין

🔭 צופה פני עתיד:
  • [open gaps, follow-ups, data-quality findings, what the next session should start with]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Match the user's language (Hebrew here). Keep each line short and concrete. If a section is empty, say so in one line rather than dropping it — "nothing pending" is information.

---

## Guardrails — do NOT

- ❌ Merge a PR with a red/failing *required* check, or an unverified high-blast-radius change (authority covers *required-green + verified* only).
- ❌ Write an authority doc directly — propose a patch and route it.
- ❌ Deploy to production or apply a prod-DB migration as part of a close — those are deliberate, flagged steps.
- ❌ `git add -A` / `git add .`, or sweep up unrelated uncommitted work — stage only the specific files the close authored.
- ❌ Delete a trigger you can't prove is this session's own probe.
- ❌ Unsubscribe from a PR that hasn't merged/closed.
- ❌ Fabricate the scan — if you couldn't check a source (tool unavailable, no access), say so; don't report it as clean.
- ❌ Turn a clean close into busywork — if a section is empty, one line and move on.

---

## Tone

- Be surgical. Most closes are short: a few safe items handled, maybe one risky item to confirm, knowledge committed by type, done.
- Do the boring reliable thing over the clever thing — this is the closer; predictability is the feature.
- The value is that the user can walk away trusting nothing was left dangling, nothing risky was done behind their back, and the session's knowledge is now findable in the brain. Earn that every time.
