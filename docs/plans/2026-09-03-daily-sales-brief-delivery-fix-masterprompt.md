# MASTERPROMPT — the daily sales brief arrives Sun–Thu between 17:00 and 17:30, or Tom's phone tells him why before 17:40

**STATUS: LIVE — not yet executed**
<!-- The executing session's last act is to change this to SHIPPED / SUPERSEDED by <path> /
ABANDONED — why, with evidence pointers. -->

> **Usage:** paste this entire file as the first message of a fresh session with
> `gt-factory-os` and `gt-factory-os-production-brain` attached, and the **GitHub, Make and
> Gmail** connectors enabled. It takes the daily brief from "sent by a Claude Routine that
> physically cannot attach the report, with nothing checking arrival" to "scheduled by Make,
> built and sent by GitHub Actions, audited every evening."
> It halts for Tom only where a human must genuinely act — §6 is that complete list.
>
> **Provenance:** written 2026-09-03 from a live incident and its repair, measured in this
> environment, not recalled. The 2026-09-02 brief was built correctly (`run_daily.sh`, 5/5
> stages) and never sent; the same brief was then delivered by GitHub Actions run **#136** at
> `2026-09-03T05:46:19Z`. Every figure in §2 was observed on 2026-09-02/03; the workflow YAML,
> the pipeline guard and the Make account were read at source on 2026-09-03.
> Authority: `gt-factory-os-production-brain/CLAUDE.md` · `gt-factory-os/CLAUDE.md` ·
> `gt-factory-os/tools/sales-forecast/README.md` — the pipeline's own documentation, which
> **wins on anything about data semantics**.
>
> **Shelf life:** §2 is presumed wrong if pasted after **2026-09-17**. Run §2.6 first.
> If reality no longer matches §2 — a different sender is live, the workflow has changed, the
> brief is already arriving reliably — **halt and surface to Tom**; do not adapt silently.
> This document exists because three silent adaptations produced three misses.

## 0. How to work

- **Who you are here:** one fresh agent session holding both repos, the **GitHub MCP tools**
  (`mcp__github__*` — there is no `gh` CLI), the **Make MCP tools** (`mcp__Make__*`, which can
  create and edit scenarios), the **Gmail connector**, and the Green Invoice credentials as
  environment variables. You may push to your designated branch and open a draft PR.
- **Read first, in order:** this file · `gt-factory-os/tools/sales-forecast/README.md`
  (*How it runs* and *Notes*) · `.github/workflows/daily-sales-forecast.yml` ·
  `gt-factory-os/tools/sales-forecast/build_forecast.py` lines 30–65.
- **Authority:** cited by path and section, never copied. Where this document and an authority
  doc disagree, the authority doc wins and this document is wrong — say so in your report.
- **Halt conditions, evidence standard, git discipline:** inherited from
  `gt-factory-os-production-brain/CLAUDE.md` §Stop conditions, §Evidence, §Write boundaries.
  Deltas specific to this work are in §8.
- **The standard, in Tom's own words:** `זה חייב לעבוד` ("this has to work") — he has been made to look foolish in
  front of investors three times. Translated into checkable prohibitions:
  1. **Nothing wrong or partial may be sent.** Every figure the recipients read comes out of
     the generated files byte for byte.
  2. **Nothing may fail silently.** Every failure path ends in a message to Tom the same
     evening.
  3. **Nothing may depend on a human editing a calendar.** A fix that works until 2026-10-25
     and then breaks on DST is not a fix.
- **Language:** this document is English because that is the register you reason best in. Data
  literals stay in their own script, in backticks, never translated. **Output language:
  concise English** — short sentences, no preamble, no restating the question — with the
  single closing line to Tom in Hebrew.

## 1. Mission and definition of done

**One testable sentence:** Sunday through Thursday, Tom and Dean each hold the generated brief
with the interactive report attached by 17:30 Israel — and on any evening it does not arrive,
Tom is told before 17:40.

| # | Condition | The observation that would prove it false |
|---|---|---|
| D1 | The brief is built and sent **server-side**; no model session ever handles the report bytes | any code path that puts `dashboard/GT_Sales_Forecast.html` bytes into a tool-call argument or a Make field |
| D2 | The mail carries the **exact generated** subject, HTML body and attachment | sent subject ≠ `email_subject.txt`; body re-rendered rather than `file://…email_body.html`; no `GT_Sales_Forecast.html` attachment |
| D3 | Both recipients, every send | a `to:` line missing `tom@gteveryday.com` or `arbel.dean@gmail.com` |
| D4 | Exactly one brief per business day | Gmail `in:sent subject:"GT · מכירות" newer_than:1d` returns 0 or 2 for one date |
| D5 | Delivery is **verified**, not assumed | a run reported as "sent" with no Gmail Sent hit for that date's subject |
| D6 | A miss reaches Tom by 17:40 Israel | the brief is absent from Sent at 17:40 and no alert was sent |
| D7 | The schedule survives 2026-10-25 DST with **no human edit** | the send lands at 16:00 Israel, or `build_forecast.py` aborts on its cutoff guard, on 2026-10-25 |
| D8 | Both repos left clean | `git status --porcelain` non-empty in either repo |
| D9 | The retired standing instruction cannot be followed by mistake | `docs/plans/2026-09-02-daily-sales-brief-routine-masterprompt.md` still reads `STATUS: LIVE` while describing the Gmail-connector send |
| D10 | The old Claude Routine no longer sends | two briefs arrive on one day, or the retired Routine is still enabled after cutover |

Anything not on this list is out of scope unless Tom asks.

### 1.1 Settled — do not reopen

- **The cutoff is 17:00; the basis is net of credit notes, ex-VAT.** `CUTOFF_HOUR` in
  `build_forecast.py` is the authority, and 17:00 is measured, not arbitrary — `README.md`
  *Reading a day that is still open* shows the capture curve turning there. **Do not change it.**
- **Recipients: `tom@gteveryday.com` and `arbel.dean@gmail.com`.** Both, always, and they live
  in the workflow YAML, not in a secret. (`REPORT_RECIPIENTS` is dead — it once held a reversed
  address that silently misdelivered.)
- **The email is the generated one.** Tom's instruction was `בדיוק באותו HTML` ("exactly the same HTML"). You do not author,
  restyle or summarise it.
- **`SALES_REPORT_DATE` is never set on the daily path.** It replays a **past** day only.
  See landmine 7.4 — the README's description of it is stale.
- **Read-only against Green Invoice.** The pipeline writes to no external system.

## 2. Ground truth — measured 2026-09-02/03; re-verify at boot

### 2.1 What is live right now

- **The pipeline works and is not the problem.** `tools/sales-forecast/run_daily.sh`, five
  stages, pure Python stdlib, **no `pip install`, ever**. ~80 s.
- **The current sender is a Claude Routine** (`דוח מכירות יומי · 17:00 · לתום ולדין`, cron
  `0 14 * * 0-4` UTC) mailing through the Gmail connector — `README.md:22`. **This is the
  component being replaced**, and it must be turned off (D10).
- **`.github/workflows/daily-sales-forecast.yml` exists, is `workflow_dispatch`-only, and
  works.** It runs the same `run_daily.sh` on a GitHub runner and mails via
  `dawidd6/action-send-mail@v3` with `html_body: file://…email_body.html` and
  `attachments: tools/sales-forecast/dashboard/GT_Sales_Forecast.html`. Recipients hardcoded.
  It has an `Alarm on failure` step — see landmine 7.2.
- **GitHub Actions minutes are available again** — run #136 executed 2026-09-03.
- **pg_cron is not in the path.** `daily_sales_report` / `daily_sales_report_verify` were
  unscheduled 2026-08-31. Migration `0339` remains only as history.

### 2.2 Make — read at source 2026-09-03, and it is the missing clock

```
organization  6913249 "My Organization" · zone eu1.make.com · isPaused false
timezone      Asia/Jerusalem          ← the whole DST problem disappears here
plan          Teams · 480,000 operations/month  (this job needs ~44/month)
team          1240098 "My Team"       ← create scenarios here
proven        `http` MakeRequest module used in 4 existing scenarios
              `google-email` ActionSendEmail used in "GT Leads — Instant"
```

Make schedules in the **account's timezone**, so "17:00" means 17:00 in Israel in July and in
December. No UTC arithmetic, no October edit, no two-cron trick.

**But Make is not magic: existing scenarios carry real error counts** (`GT Sales — hourly
pulse` 9 errors; `GT Sales — lead intake → /ingest` 32 errors, 2 in the DLQ). A Make scenario
that breaks is exactly as silent as everything else. This is why §4 W3 exists.

### 2.3 The numbers — the 2026-09-02 brief, built in-session and delivered by run #136

```
run_daily.sh            5/5 stages · exit 0 · ended on its "DONE →" line
cutoff 17:00 · capture=0.955 measured over 115 trading days
subject   GT · מכירות 02/09/2026 עד 17:00: ₪34,592 (80% מהיעד · שנה +51% מאשתקד)
day       actual ₪34,592    vs expected ₪43,040    =  80%
month     actual ₪72,147    vs expected ₪80,401    =  90%
quarter   actual ₪1,534,327 vs expected ₪1,660,768 =  92%
year      actual ₪4,100,907 vs expected ₪4,109,161 = 100%   (+51% vs last year)
outputs   email_subject.txt 96 B · email_body.html 12,027 B
          dashboard/GT_Sales_Forecast.html 76,322 B
credits held out of netting (expense, not returned product): 2 lines, ₪36,907 total
delivery  Actions run #136 · dispatched 05:44:54Z · completed 05:46:23Z (89 s) · success
          Gmail Sent 05:46:19Z · both recipients · message size 120,675 B
```

The 120,675 B sent size against a 12,027 B body is the attachment's fingerprint: a body-only
mail is ~15 KB. Two held-out credit lines is the expected count.

### 2.4 The measurement that defines the whole task

The Gmail connector accepts an attachment **only as one inline base64 string inside a single
tool call**. Measured in this environment 2026-09-02 — `wc -c` on the generated file gave **76,322 B**
and `base64 -w0` on it gave **101,764 characters** — which the harness itself
counts as **~93,570 tokens**. Two independent observations on 2026-09-02: the `Read` tool
**refused to return the file whole** (capped ~25,000 tokens; it is one unsplittable line), and
composing the `create_draft` call **exceeded the session's single-response output limit**.

**A model session physically cannot carry this attachment.** Not a skill problem, not a retry
problem, not a prompt problem. Any design that asks a session — or a Make field — to hold the
report bytes is already broken. Treat this as a law.

### 2.5 Adjacent things that are not yours

- **`schedule:` is gone from the workflow on purpose** — GitHub cron fires 1–2.5 h late and
  cannot hold a 17:00–17:30 window (`README.md:30`). Do not re-add it.
- **The Actions-cost objection is dead.** ~22 runs/month × 2 billed minutes ≈ **44
  minutes/month, ~2% of the 2,000 allowance** (`README.md:39`). What exhausted the quota on
  2026-08-30 was issue **#217**'s design, which slept a runner until the target minute and burned
  ~3,164 minutes/month, ~158% of the allowance (both figures from `README.md` *How it runs*, the #217
  row), taking unrelated workflows down with it. **Never resurrect a
  sleeping runner.**
- **The sales-report artifact is a different report** (Shopify-sourced, whole days, its own
  Routine). It will not agree with this brief and both are right. Do not touch it.

### 2.6 Re-verification block — run at boot, before trusting anything above

```bash
cd ~/gt-factory-os/tools/sales-forecast
ls run_daily.sh build_forecast.py build_email_body.py
grep -c "CUTOFF_HOUR=17" build_forecast.py                 # expect 1
TZ=Asia/Jerusalem date +'%Y-%m-%d %H:%M %a'                # anchors every "today" below
grep -n "html_body:\|attachments:\|^          to:" ../../.github/workflows/daily-sales-forecast.yml
```

```
# GitHub MCP — has the brief been going out, and did anything change?
mcp__github__actions_list  method=list_workflow_runs  resource_id=daily-sales-forecast.yml
# Make MCP — what exists today
mcp__Make__scenarios_list  teamId=1240098
mcp__Make__connections_list teamId=1240098      # is there a GitHub connection yet? a Google one?
# Gmail — the only proof that matters
in:sent subject:"GT · מכירות" newer_than:7d
```

A gap on any Sun–Thu in that Gmail search is a miss. Count them; that count is the problem
statement, and closing it is the job.

## 3. What the hard part actually is

- **It looks like an email bug. It is an architecture that asks one component to do two jobs.**
  The brief needs a **punctual trigger** and a **sender that can attach the 76,322 B report (§2.4)**. GitHub
  `schedule:` attaches but runs hours late. A Claude Routine is punctual but cannot attach
  (§2.4). Each of the three failures was a redesign that swapped one for the other and re-broke
  the half that had been working. **The fix is not a better transport — it is to stop asking one
  component for both.** Make keeps the clock, Actions builds and sends, and a second Make
  scenario audits. Run #136 already proved the middle link end to end.
- **The real defect is not the misses — it is that nothing ever noticed them.** `README.md:50`,
  in the project's own words: *"a firing that never happens is visible only as a missing email.
  That is the current honest limit."* That is why Tom learns about this from investors instead
  of from his phone. **A send path without an auditor is not finished, however elegant.**
  Verification is the deliverable; the rewiring is the easy half.
- **The alarm that exists cannot fire on the failure that happened.** `Alarm on failure` is a
  *step inside the job*. On 2026-08-30 the run died in six seconds before the job started, so it
  never ran. An in-band alarm cannot report an out-of-band death — the auditor has to live
  outside the thing it audits, which is why it is a separate Make scenario and not a step.
- **Take the language model out of the critical path.** This is a fixed daily mechanical job:
  same time, same command, same two recipients. It had a nondeterministic component doing a
  deterministic task, and the nondeterminism is precisely where it broke. After this change no
  model runs in the daily path at all — Make fires, Actions builds and mails, Make checks. A
  session is only ever involved when something has already gone wrong.
- **DST is an outage already on the calendar.** `0 14 * * 0-4` UTC is 17:00 only while IDT
  holds; from **2026-10-25** it is 16:00 and `build_forecast.py` will correctly refuse to publish
  a 17:00 label over 16:00 data. Make's Asia/Jerusalem scheduling removes this permanently —
  which is the point of moving the clock rather than patching the cron.

## 4. Workstreams

Four, in order. W1+W2 are the fix, W3 is what keeps it fixed, W4 stops the next session from
following the retired design.

### W1 — Make becomes the clock and the dispatcher
Create a Make scenario in team `1240098`, named `GT · דוח מכירות יומי — dispatch`:
1. **Schedule:** daily **17:00**, days **Sunday–Thursday**, account timezone Asia/Jerusalem.
2. **HTTP module** → `POST https://api.github.com/repos/tomw200082-collab/gt-factory-os/actions/workflows/daily-sales-forecast.yml/dispatches`
   with `{"ref":"main"}`, `Accept: application/vnd.github+json`, and the GitHub credential from
   §6A. A `204` is success **at the API level only** — see landmine 7.3.
3. **Idempotency:** before dispatching, do not send twice. The cheapest correct guard is the
   workflow's own `concurrency` group plus the auditor in W3; if you add a Gmail pre-check
   inside this scenario, it must not become a second failure mode. Prefer simple.
4. **Error handling:** attach a Make error handler that emails Tom if the HTTP call does not
   return 204. Do not let the scenario fail silently into the DLQ.

**Acceptance:** D1, D2, D3, D7.

### W2 — Turn off the old sender, and prove only one brief goes out
The Claude Routine `דוח מכירות יומי · 17:00 · לתום ולדין` must stop sending, or Tom and Dean get
two briefs a day and D4 fails. **Whether a session can disable a claude.ai Routine is unverified** —
check `CronList`/`CronDelete` first; if they do not cover it, this is Tom's, per §6B, and your
report must say D10 is open until he confirms.

Cut over on a day you can watch: Make dispatches, the brief arrives once, and the Routine is
already off. **Do not run both for a day "to be safe" — that is a guaranteed duplicate.**

**Acceptance:** D4, D10.

### W3 — An auditor that lives outside the thing it audits
A second Make scenario, `GT · דוח מכירות יומי — auditor`, scheduled **17:40 Sunday–Thursday**,
Asia/Jerusalem, holding only a Google connection:
1. Search Gmail for today's brief — `in:sent subject:"GT · מכירות" newer_than:1d`, or the
   equivalent Gmail-module search.
2. **If found:** stop. Silence is the correct output of a healthy evening.
3. **If not found:** send Tom an alert naming the date and stating plainly that no brief went
   out. Email at minimum; WhatsApp if the account already has that connection.

It must not share a failure mode with W1: separate scenario, minimum surface, no GitHub, no repo.

**The backstop, because Make can be down too:** add one line to the existing morning ritual
(`gt-factory-os-production-brain/.claude/skills/chief-of-staff-daily/`, day-open 07:30) that
checks whether yesterday's Sun–Thu brief is in Sent and flags it if not. It rides a proven daily
routine, adds no new component, and catches a total Make outage by the next morning.

**Acceptance:** D5, D6.

### W4 — Retire the instruction that describes the broken design
- Stamp `docs/plans/2026-09-02-daily-sales-brief-routine-masterprompt.md` **`SUPERSEDED by
  docs/plans/2026-09-03-daily-sales-brief-delivery-fix-masterprompt.md`** with a one-line reason.
  Leave the rest as history.
- Rewrite `tools/sales-forecast/README.md` *How it runs* to describe Make → Actions → auditor,
  and fix the stale `SALES_REPORT_DATE` sentence (landmine 7.4).
- Do **not** create a new authority doc (brain `CLAUDE.md` §Forbidden assumptions).

**Acceptance:** D9.

### Testing without spamming Dean
Do **not** rehearse against the live recipients. Test on your branch with the workflow's `to:`
narrowed to `tom@gteveryday.com` alone, dispatching with `ref=<your branch>`; the run uses that
ref's workflow. Prove the whole chain there — Make fires, the run completes, the mail arrives,
and the auditor alerts when you point it at a date with no brief. **Restore `to:` to both
recipients before anything merges** and confirm with `grep -n "^          to:"` that `main`
carries both. One real 17:00 send is the final proof, not a rehearsal.

## 5. Scope

**IN:** everything in §4.

**OUT — do not touch, do not "improve":**
- `CUTOFF_HOUR`, the netting rule, `mapping.credit_is_sales_reduction()`, the capture
  measurement, the recipients. Data-semantics decisions; changing one silently invalidates every
  earlier brief.
- The generated email's HTML, wording, styling or figures — Tom: `בדיוק באותו HTML`.
- `schedule:` in the workflow, and any sleeping-runner design (§2.5).
- The sales-report artifact and its Routine.
- pg_cron and migration `0339`. History, not a live job; reviving it re-imports the
  401-looks-like-success problem its own header documents.
- The other Make scenarios in team `1240098`. Several already carry errors and DLQ entries;
  they are not yours and fixing them is a different job.
- Any attempt to make a model session or a Make field carry the dashboard bytes (§2.4).

## 6. Tom's part — the complete list, nothing else is his

**A. Give Make permission to dispatch the workflow.** Make needs GitHub credentials it does not
have. Preferred: a **fine-grained PAT scoped to `gt-factory-os` with `Actions: read and write`
only**, created by Tom and pasted directly into the Make connection/HTTP header. **Never paste a
token into chat, this document, a commit or a PR.** Note: `github_actions_dispatch_token` in the
Supabase vault belonged to the retired pg_cron dispatch and should be treated as expired — issue
a fresh one rather than retrieving the old. ~5 minutes.

**B. Disable the old Claude Routine** `דוח מכירות יומי · 17:00 · לתום ולדין` in the claude.ai
Routines UI — only if W2's `CronList`/`CronDelete` check shows you cannot. Until he does, D10 is
open and a duplicate is possible. ~2 minutes.

**C. Confirm the GitHub Actions minute budget.** The brief needs ~44 min/month of a 2,000
allowance, but 2026-08-30 proved an unrelated workflow can eat the quota and kill the brief
silently. He owns the billing page; you cannot read it.

**D. Decide the fallback when Actions is unavailable.** If the quota is gone, the brief cannot be
sent with its attachment by any path in this design. Two options, his call: **(i)** the auditor
alerts him and he dispatches manually when minutes return, or **(ii)** `build_email_body.py`
gains a no-attachment body variant whose footer does not claim a file is attached, so a degraded
but truthful brief can go out. **Default to (i); build nothing for (ii) until he chooses it** —
(ii) changes the email he just said must not change.

## 7. Landmines — do not rediscover these

1. **"I'll just attach it from the session."** 76,322 B → 101,764 base64 chars → ~93,570 tokens (§2.4),
   past both the `Read` cap and the single-response output limit (§2.4) → **no version of this
   works.** Dispatch the workflow instead.
2. **A green `Alarm on failure` step proves nothing about the failure you care about.** It is a
   step inside the job; a run that dies before the job starts sends no alarm and left no trace on
   2026-08-30 → the auditor checks **Gmail Sent**, never the workflow's opinion of itself.
3. **A `204` from the dispatch API is not a send.** It means "queued". The run can still die on
   minutes and the mail step can still fail → the 17:40 auditor is what closes this, not the
   HTTP status.
4. **`README.md` line ~101 says `SALES_REPORT_DATE` "bypasses the before-cutoff guard". That is
   stale.** The guard now tests the labelled instant (`build_forecast.py:58`): a **past** date
   passes because its 17:00 is behind us, and `SALES_REPORT_DATE=<today>` at 09:00 is correctly
   **refused**. Do not use it to force a report before 17:00; fix the sentence (W4).
5. **Dispatching before 17:00 Israel produces a false alarm, not a brief.** The build aborts on
   the cutoff guard, the job fails, and the alarm step mails Tom that the report failed — noise
   that trains him to ignore the alarm. Make's Asia/Jerusalem scheduling is what prevents this;
   do not "help" by adding a UTC cron beside it.
6. **Dispatching a workflow on a branch runs that branch's YAML.** That is how you test safely —
   and how you ship a narrowed `to:` if you forget to restore it.
7. **A Make scenario fails as silently as anything else.** Two scenarios in this very team carry
   9 and 32 errors with items in the DLQ (§2.2). Give W1 an error handler and never treat "the
   scenario exists" as "the scenario ran".
8. **`git pull --ff-only` fails in this environment** with "no tracking information" on the
   session's designated branch. Use `git fetch origin main` and branch from `origin/main`.
9. **The 17:00 report is frozen and never revised**; month/quarter/year rebuild each run and
   self-heal. A re-run of a past day reproduces that day's headline exactly — which is why run
   #136 could deliver the 02/09 figure unchanged on 03/09.

## 8. Halt conditions

Inherited set cited in §0. Additions specific to this work:

- **You are about to put report bytes into a tool argument or a Make field** → **STOP**. That is
  the defect this document exists to remove.
- **A change would alter a figure, a recipient, the cutoff, or the generated HTML** → **STOP**,
  surface to Tom.
- **You cannot verify a send actually landed** → do **not** report success. Say so plainly.
- **Both the old Routine and the new Make schedule would be live at once** → **STOP**; a
  duplicate brief is a real cost.
- **A secret would be written into chat, this document, a commit or a PR** → **STOP**. Name it
  and where it lives; never its value.
- **Never end a run silently.** Either the brief went out and you can point at the Sent message,
  or Tom hears why it did not.

## 9. Final report

Concise English.

1. What a stranger can now watch working, end to end — name the Make scenario, the run id and
   the Sent message.
2. Each done-condition D1–D10 ✅/❌ with its evidence pointer. No partial credit.
3. The numbers from §2.6: how many Sun–Thu days in the last week carried a brief.
4. The artifacts: the PR, the changed files, the Make scenario ids.
5. What is still Tom's (§6), and what is genuinely unfinished.
6. The single next action.

Then one short Hebrew line to Tom. If anything is not ready, say so first and plainly.
Tokens per `gt-factory-os-production-brain/VERDICT_GLOSSARY.md`.
