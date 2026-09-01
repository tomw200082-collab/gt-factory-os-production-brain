# The PR queue — triage, 2026-09-01

> **Why this exists.** 43 pull requests are open across the three repos. The oldest was
> opened `2026-07-18`. Every one of them is a piece of work that is finished but not
> landed, which means the next session cannot see it.
>
> **This is not a tidiness problem.** It is the reason the war room needed anti-collision
> contracts at all: sessions branch from `main`, and `main` does not contain the work.
> Measured 2026-09-01 by test-merging every branch against `origin/main`.

---

## 1. The number

| Repo | Open PRs | Merge clean | Conflict |
|---|---|---|---|
| `gt-factory-os-production-brain` | 30 | 25 | 5 |
| `Sales-Machine` | 13 | 8 | 5 |
| **Total** | **43** | **33** | **10** |

**33 of 43 merge with no conflict today.** They are not blocked on anything technical.

---

## 2. The cost, made concrete

**PR #188 changes `CLAUDE.md` to make PR-watching opt-in — citing `Tom 2026-09-01`, today,
in response to Tom's own instruction to stop all monitoring.** It ships a `PreToolUse` hook
(`.claude/hooks/no_autowatch.sh`) that blocks `subscribe_pr_activity`, `send_later`,
`create_trigger`, `ScheduleWakeup` and `CronCreate` unless Tom opts in.

That rule is sitting in a draft PR. **Until it lands in `main`, every session still
auto-watches** — the exact behaviour Tom asked to stop this morning. This is what an
unmerged queue costs: a governance decision made today does not bind anything until
somebody presses merge.

---

## 3. Group A — merge now, nothing can break (9 PRs)

Pure additions. Each adds new files under `docs/plans/` or `.claude/skills/` and modifies
no existing file. Blast radius is zero by construction.

| PR | Branch | Adds |
|---|---|---|
| #194 | `prompt-master-repo-oae2ib` | vendored `prompt-master` skill (MIT) |
| #193 | `caveman-ponytale-01m3a3` | `2026-08-31-q4-integration-phase-a-design.md` |
| #191 | `caveman-mode-0sk2k3` | `2026-08-31-social-foundation-masterprompt.md` |
| #190 | `caveman-ponytale-fh8gpv` | Q4 + sales-system-integration masterprompts |
| #182 | `sales-growth-existing-customers-w1oflp` | existing-customer growth masterprompt |
| #173 | `weekly-work-summary-6g4uja` | weekend handoff + Meta/WhatsApp week brief |
| #163 | `gt-initial-menu-lead-9cw4zp` | lead-welcome-menu masterprompt |
| #157 | `caveman-ponytale-gl4n5q` | queue-integrity masterprompt |
| #155 | `elite-copywriter-psych-adn95z` | `copywriter` skill + 4 references |

Plus, in `Sales-Machine`: #23, #22, #21, #15, #13, #12, #10 — all merge clean.

## 4. Group B — merge now, and the point *is* the change (1 PR)

| PR | Why it is different |
|---|---|
| **#188** | Touches `CLAUDE.md`, `.claude/settings.json`, `.gitignore`. **`CLAUDE.md` is Tom-sole-writer**, so this normally halts. It does not halt here: the amendment cites `Tom 2026-09-01` and implements the instruction Tom gave today. It still wants Tom's eye on the diff before merge — one file, twelve added lines. **Merging it is what makes "stop watching" actually stick.** |

## 5. Group C — three plans for one job (pick one, close two)

Three PRs each carry a full existing-customer growth masterprompt, under three filenames:

| PR | File | Lines |
|---|---|---|
| #182 | `2026-08-30-existing-customer-growth-masterprompt.md` | 675 |
| #183 | `2026-08-30_existing_customer_growth_MASTERPROMPT.md` | 696 |
| #190 | `2026-08-31-existing-customers-q4-masterprompt.md` | **759** |

Merging all three puts three live plans in `docs/plans/` for the same workstream, and the
war room's own rule says an unstamped plan is indistinguishable from a live one.

**Recommendation:** merge **#190** (newest, longest, and the one the war room already
routes `#6` to). Close #182 and #183 with a one-line pointer at #190 rather than merging
them. #183 also carries the MUZA retirement masterprompt and a `54,514`-line analytics
JSON — split that out rather than dragging it in behind a duplicate.

## 6. Group D — conflicted, belongs to its own session (10 PRs)

These cannot be merged by anyone but the session that wrote them, or by a deliberate
resolve. Not urgent; listed so they stop being invisible.

`gt-factory-os-production-brain`: #171 `tea-product-descriptions` · #170 `brainstorm-session`
· #166 `caveman-ponytale-kglcb9` · #164 `caveman-copywriting` · #154 `leads-live-intake`.
`Sales-Machine`: #20 · #19 · #18 · #11 · #3 · #2.

**#166 deserves a decision, not a rebase.** It is `feat(pricing): finish the 81% repricing`,
opened `2026-08-26`, 31 files, 17 of them non-doc. The cost model of record is
`2026-08-27` — one day *later* — and it shipped. A repricing PR that predates the cost model
it was meant to implement is a candidate for closing, not merging. **Verify before acting.**

**#2 and #3 in `Sales-Machine` are from `2026-07-18` and `2026-08-05`.** Six and four weeks
old. If they still matter they should be rebased today; if they do not, closing them is a
closure, not a loss.

---

## 7. What is being asked

One decision, not 43 reviews:

> **"Merge Group A and Group B; take #190 from Group C and close #182 and #183; leave
> Group D to its sessions."**

That lands **20 PRs**. The rest have a named owner and a named reason.

Whoever executes it merges oldest-first inside each group so the diffs stay small, and
re-tests for conflicts after each merge — 33 branches are clean against *today's* `main`,
and every merge moves `main`.

---

## 8. The rule that stops this recurring

The war-room skill brief (`2026-08-31-war-room-skill-masterprompt.md`) already owns the
open-ask queue. It should also own this: **a session that opens a PR and reports done has
not finished. Landed or explicitly handed over is finished.** A draft PR with a SHIPPED
stamp inside it is the worst of both — it looks complete and changes nothing.

Concretely, three lines for the skill:
1. Every masterprompt's exit checklist ends with *PR merged, or named blocker*.
2. The board carries a live PR count per workstream. `#6: 3 open PRs` is a status; "shipped"
   is not.
3. Duplicate detection at open time — same workstream, same week, different filename is the
   signature in §5, and it is cheap to catch before merge rather than after.

---

**Measured:** 2026-09-01 by test-merging all 43 branches against `origin/main`
(`git merge-tree --write-tree`). **Authority:** `system_verified` for every count and
conflict state; the recommendations in §5 and §6 are `inferred`. **Decides:** Tom.
