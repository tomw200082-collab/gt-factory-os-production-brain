# MASTERPROMPT — the daily sales brief arrives Sun–Thu between 17:00 and 17:30, and is never silently wrong

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
> **Shelf life:** §2 is presumed wrong if pasted after **2026-09-17**. Run §2.7 first.
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
| D4 | Exactly one brief per business day | the dated query `in:sent subject:"GT · מכירות DD/MM/YYYY"` for today returns 0, or returns 2 |
| D5 | Delivery is **verified**, not assumed | a run reported as "sent" with no Gmail Sent hit for **today's dated** subject |
| D6 | A miss reaches Tom by 17:40 Israel | the dated subject is absent from Sent at 17:40 and no alert was sent |
| D7 | The schedule carries **no UTC offset anywhere**, so DST cannot move it | the Make org timezone is not `Asia/Jerusalem`, or the dispatcher's schedule contains a cron/UTC offset, or any other UTC-scheduled sender still exists. (Observable today. The 2026-10-26 confirmation is a §9 follow-up, not a blocker.) |
| D8 | Both repos left clean | `git status --porcelain` non-empty in either repo |
| D9 | The retired standing instruction cannot be followed by mistake | `docs/plans/2026-09-02-daily-sales-brief-routine-masterprompt.md` still reads `STATUS: LIVE` while describing the Gmail-connector send |
| D10 | The old Claude Routine no longer sends | two briefs arrive on one day, or the retired Routine is still enabled after cutover |
| D11 | The morning backstop exists | `grep` of `.claude/skills/chief-of-staff-daily/SKILL.md` day-open finds no yesterday-brief-in-Sent check |
| D12 | A day with no invoices **fails loudly instead of re-sending yesterday** | `DATA_THRU != TODAY` with `SALES_REPORT_DATE` unset produces a sent email rather than a failed job (§2.4) |

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
plan          Teams · 480,000 operations/month  (both scenarios together: <100/month)
team          1240098 "My Team"       ← create scenarios here
proven        `http` MakeRequest module used in 4 existing scenarios
connections   Facebook ×4 · Shopify · Google ×5 · Google Restricted · Gmail ("new leads",
              id 6308857, valid to 2027-02-20)
MISSING       **no GitHub connection of any kind** — W1 cannot fire until §6A is done
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

**Run #136 was a deliberate replay, not a normal 17:00 run — do not cite it as one.** It ran at
08:44 Israel on 2026-09-03 on branch commit `3d02aac`, which set `SALES_REPORT_DATE: '2026-09-02'`
in the workflow's build step; commit `22e1327` reverted that line immediately after. It proves the
*transport* (server-side attachment, both recipients, exact HTML) and nothing about the schedule.

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

### 2.5 The stale-day trap — how this system can be *wrong* rather than merely missing

Found 2026-09-03 by red-teaming this document; confirmed by reading the code. **Nothing in the
live pipeline prevents it today.**

```python
build_forecast.py:49   DATA_THRU=max(d for d in ((l.get("date") or "")[:10] for l in L) if d<=TODAY)
build_forecast.py:50   INTRADAY = DATA_THRU==TODAY
build_forecast.py:58   if cutoff_epoch(DATA_THRU) > NOW.timestamp(): raise SystemExit(...)
build_email_body.py:21 day=D["data_thru"]; ddmy="/".join(reversed(day.split("-")))
build_email_body.py:29 TILL=f" עד {AT}" if INTRA else ""
build_email_body.py:166 head=f"GT · מכירות {ddmy}{TILL}"
```

`DATA_THRU` is the newest date that has **any** invoice, not necessarily today. If Green Invoice
returns nothing dated today at 17:00 — an outage, an auth failure, a holiday-shortened day, or
simply no sales yet — `DATA_THRU` falls back to a previous day, whose 17:00 is long past, so the
cutoff guard is **silent**, the job exits 0, and **yesterday's brief is sent again** to both
recipients. Its subject carries yesterday's date and, because `INTRADAY` is false, loses the
` עד 17:00` marker.

Two consequences that shape the design:
1. **The auditor must be keyed to today's date**, or it finds the stale brief, matches, and
   certifies the failure as healthy. An undated `subject:"GT · מכירות"` search is worse than no
   auditor, because it manufactures confidence.
2. **Better to refuse than to detect.** D12 asks for a guard beside `build_forecast.py:58`:
   abort when `DATA_THRU != TODAY` and `SALES_REPORT_DATE` is unset. That converts a silent
   wrong-numbers send into a failed job, which the auditor then reports honestly.

### 2.6 Adjacent things that are not yours

- **`schedule:` is gone from the workflow on purpose** — GitHub cron fires 1–2.5 h late and
  cannot hold a 17:00–17:30 window (`README.md:30`). Do not re-add it.
- **The Actions-cost objection is dead.** ~22 runs/month × 2 billed minutes ≈ **44
  minutes/month, ~2% of the 2,000 allowance** (`README.md:39`). What exhausted the quota on
  2026-08-30 was issue **#217**'s design, which slept a runner until the target minute and burned
  ~3,164 minutes/month (`README.md` *How it runs*, the #217 row), ~158% of the allowance
  (`README.md:39`), taking unrelated workflows down with it. **Never resurrect a
  sleeping runner.**
- **The sales-report artifact is a different report** (Shopify-sourced, whole days, its own
  Routine). It will not agree with this brief and both are right. Do not touch it.

### 2.7 Re-verification block — run at boot, before trusting anything above

```bash
# Do NOT use ~ : HOME is /root here while the repos are checked out elsewhere. Anchor on the repo.
R="$(git -C gt-factory-os rev-parse --show-toplevel 2>/dev/null || git rev-parse --show-toplevel)"
cd "$R/tools/sales-forecast" || exit 1
ls run_daily.sh build_forecast.py build_email_body.py
grep -c "CUTOFF_HOUR=17" build_forecast.py                 # expect 1
TZ=Asia/Jerusalem date +'%Y-%m-%d %H:%M %a'                # anchors every "today" below
# line 89 is the report recipients; line 108 is the failure alarm and is Tom-only BY DESIGN
grep -n "html_body:\|attachments:\|to: tom@" "$R/.github/workflows/daily-sales-forecast.yml"
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
Create a Make scenario in team `1240098`, named `GT · דוח מכירות יומי — dispatch`.

0. **Create it INACTIVE** (`scenarios_create`; do **not** call `scenarios_activate`). Activation
   is the cutover and belongs at the end of W2, after D10 is closed. An active new clock beside a
   live old Routine is two briefs to Tom and Dean — see §8.
1. **Schedule:** daily **17:00**, days **Sunday–Thursday**, account timezone Asia/Jerusalem.
   No cron string, no UTC offset — that is what D7 checks.
2. **HTTP module.** Confirm the repo slug first with `mcp__github__get_file_contents` on
   `.github/workflows/daily-sales-forecast.yml` (a wrong slug 404s indistinguishably from a bad
   token). Then:
   - `POST https://api.github.com/repos/tomw200082-collab/gt-factory-os/actions/workflows/daily-sales-forecast.yml/dispatches`
   - Body type **Raw / JSON** — Make's HTTP module defaults to form-urlencoded and that returns
     400 you will then debug blind. Body: `{"ref":"main"}`
   - Headers: `Authorization: Bearer <token from §6A>` · `Accept: application/vnd.github+json` ·
     `Content-Type: application/json` · `X-GitHub-Api-Version: 2022-11-28`
   - Expected `204 No Content`. A `204` is success **at the API level only** — landmine 7.3.
3. **No dedupe logic here.** The workflow's `concurrency` group (`daily-sales-forecast`,
   `cancel-in-progress: false`) **serialises** runs, it does not drop them — two dispatches are
   two emails, just not at once. Duplicate detection is W3's job: the auditor alerts on `≥2` as
   well as on `0`. Do not invent a second guard here.
4. **Error handling:** attach a Make error handler that alerts Tom if the call does not return
   204, so a failure lands somewhere other than the DLQ.

**Acceptance:** a Make firing at 17:00 Israel produced Actions run *N*, and the Gmail Sent
message for **today's dated subject** exists, and its size is of the order of the 120,675 B
observed for run #136 (§2.3) rather than the ~12 KB of a body-only mail — that size gap is the
attachment's fingerprint. (D2 and D3 are regression guards on
a file W1 does not touch — check them once before merge, not here; D3 is deliberately false
while `to:` is narrowed for testing.)

### W2 — Turn off the old sender, and prove only one brief goes out
The Claude Routine `דוח מכירות יומי · 17:00 · לתום ולדין` must stop sending, or Tom and Dean get
two briefs a day and D4 fails. **Whether a session can disable a claude.ai Routine is unverified** —
check `CronList`/`CronDelete` first; if they do not cover it, this is Tom's, per §6B, and your
report must say D10 is open until he confirms.

Cut over on a day you can watch, in this order: **(1)** confirm the Routine is off, **(2)** then
`scenarios_activate` the W1 dispatcher, **(3)** watch that exactly one brief arrives.
**Never run both for a day "to be safe" — that is a guaranteed duplicate.**

**Acceptance:** D4, D10.

### W3 — An auditor that lives outside the thing it audits
A second Make scenario, `GT · דוח מכירות יומי — auditor`, scheduled **17:40 Sunday–Thursday**,
Asia/Jerusalem, holding only a Google connection:
1. Search Gmail Sent for **today's dated** subject — build the query from the run date, e.g.
   `in:sent subject:"GT · מכירות {{formatDate(now; "DD/MM/YYYY"; "Asia/Jerusalem")}}"`.
   **Never search the undated `subject:"GT · מכירות"`** — §2.5 shows a stale-day send carries
   yesterday's date, so an undated query matches it and certifies the failure as healthy.
2. **Exactly 1 hit:** stop. Silence is the correct output of a healthy evening.
3. **0 hits:** alert Tom, naming the date, saying plainly that no brief went out.
4. **≥2 hits:** alert Tom — that is the duplicate detector D4 relies on after this session ends.

It must not share a failure mode with W1: separate scenario, minimum surface, no GitHub, no repo.

**Proving the alert fires — one prescribed method, so two executors do the same thing:** clone
the auditor as `GT · דוח מכירות יומי — auditor (drill)`, fix its date to a known-empty Friday,
`Run once`, confirm the alert arrives, then **delete the clone**. **Never edit the live auditor's
query to test it** — a forgotten edit leaves a permanently silent auditor, which is precisely the
defect in §2.5. The clone's deletion is part of D8's evidence.

**The backstop, because Make can be down too:** add a yesterday-brief-in-Sent check to the day-open
path of `gt-factory-os-production-brain/.claude/skills/chief-of-staff-daily/SKILL.md` (07:30). It
rides a proven daily ritual, adds no new component, and catches a total Make outage by the next
morning. Note it changes Tom's morning email, so keep it to one line and flag it in your report.

**Acceptance:** D5, D6, D11.

### W4 — Retire the instruction that describes the broken design
- Stamp `docs/plans/2026-09-02-daily-sales-brief-routine-masterprompt.md` **`SUPERSEDED by
  docs/plans/2026-09-03-daily-sales-brief-delivery-fix-masterprompt.md`** with a one-line reason.
  Leave the rest as history.
- Rewrite `tools/sales-forecast/README.md` *How it runs* to describe Make → Actions → auditor,
  and fix the stale `SALES_REPORT_DATE` sentence (landmine 7.4). The Routine is described as the
  live sender in several places, not just that section — enumerate them rather than trusting a
  line list that rots:
  `grep -n "Claude Routine\|Routine\|Gmail connector\|2026-09-02-daily-sales-brief" README.md`
- **Fix the workflow's own header.** `daily-sales-forecast.yml:17-31` still says
  *"SINCE 2026-08-31 THIS WORKFLOW IS DORMANT […] Nothing dispatches this workflow any more"* and
  line 28 points the next reader at the very document you are stamping SUPERSEDED. Left alone, D9
  passes while every pointer that caused this confusion survives.
- Do **not** create a new authority doc (brain `CLAUDE.md` §Forbidden assumptions).

**Acceptance:** D9 — whose falsifier is now broader: any `grep` for
`2026-09-02-daily-sales-brief-routine-masterprompt`, or for `Claude Routine` as the live sender,
in `daily-sales-forecast.yml` or `README.md`, that does not sit inside an explicitly historical
block.

**Merging:** W4's documentation changes go to `main` under brain `CLAUDE.md` §Authorization once
checks are green — a draft PR leaves D9 false on `main`. This work requires **no** change to
`daily-sales-forecast.yml` beyond the header comment; if you make one, it must be merged **before**
the dispatcher is activated, because W1 dispatches `{"ref":"main"}`.

### Testing without spamming Dean
Do **not** rehearse against the live recipients.

**Narrow only the `Email the report` step's `to:` (`daily-sales-forecast.yml:89`).** The second
`to:` at line **108** belongs to `Alarm on failure` and is Tom-only by design — leave it. Dispatch
with `ref=<your branch>`; the run uses that ref's workflow.

**Before any test dispatch, read landmine 7.5.** A pre-17:00 dispatch is *not* reliably a no-op:
if today has no invoice yet it will rebuild and send **yesterday's** brief for real, to whatever
`to:` currently holds. Narrow `to:` first, always.

Restore with a single check that has exactly one expected hit:
`grep -n 'to: tom@gteveryday.com,arbel.dean@gmail.com' .github/workflows/daily-sales-forecast.yml`.
One real 17:00 send is the final proof, not a rehearsal.

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

**E. Authorize — or confirm — a Make Google connection on `tom@gteveryday.com` with Gmail
read/search scope.** The auditor must *search Tom's Sent folder*. The only proven Gmail usage in
this account is a **send** action (`google-email` in `GT Leads — Instant`), which establishes
neither read scope nor that the connection is authenticated as `tom@gteveryday.com` rather than
another Google account. An auditor pointed at the wrong mailbox finds nothing and alarms every
night until Tom mutes it — which is worse than no auditor. Confirm the mailbox identity and the
scope before shipping it; if a browser OAuth consent is needed, only Tom can click it. ~3 minutes.

**F. Confirm the alert channel.** §1 promises Tom is *told* by 17:40. Email is the floor; if he
wants it to reach his phone, a WhatsApp/push connection must exist in Make. Ask which he wants —
do not assume email is enough for the man who found out from investors.

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
5. **A pre-17:00 dispatch is NOT reliably harmless — it can send a real, stale brief.** The
   cutoff guard tests `DATA_THRU`, not today (§2.5). It aborts only if today **already has an
   invoice**. If today has none, the run rebuilds **yesterday's** brief and mails it for real to
   whatever `to:` holds. So: never dispatch before narrowing `to:` (line 89), and never dispatch
   on a live Sun–Thu before 17:00. Make's Asia/Jerusalem scheduling is what keeps the production
   path clear of this; do not "help" by adding a UTC cron beside it.
6. **Dispatching a workflow on a branch runs that branch's YAML.** That is how you test safely —
   and how you ship a narrowed `to:` if you forget to restore it.
7. **A Make scenario fails as silently as anything else.** Two scenarios in this very team carry
   9 and 32 errors with items in the DLQ (§2.2). Give W1 an error handler and never treat "the
   scenario exists" as "the scenario ran".
8. **Do not assume your session branch is based on current `main`, or that it has an upstream.**
   On 2026-09-02 `git pull --ff-only` failed in `gt-factory-os` with "no tracking information"
   until an upstream was set. Always `git fetch origin main` and branch from `origin/main`
   explicitly rather than pulling.
9. **The most dangerous failure is a brief that looks fine and carries yesterday's numbers.**
   See §2.5. Symptom: a brief whose subject shows a past date and lacks ` עד 17:00`. Cause:
   `DATA_THRU` falling back when today has no invoices, with the cutoff guard silent. Resolution:
   date-keyed auditor (W3) and, properly, the D12 guard in `build_forecast.py`.
10. **The 17:00 report is frozen and never revised**; month/quarter/year rebuild each run and
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
- **The Make dispatcher would be active while the old Routine is still enabled** → **STOP**.
  Activation is the cutover (W2), not a step in W1.
- **You are about to dispatch before 17:00 Israel with `to:` not narrowed** → **STOP** (landmine 7.5).
- **You cannot prove the auditor reads Tom's mailbox** → `HOLD_FOR_TOM` (§6E). Do not ship a green
  auditor you cannot prove is looking at the right Sent folder.
- **Never end a run silently.** Either the brief went out and you can point at the Sent message,
  or Tom hears why it did not.

## 9. Final report

Concise English.

1. What a stranger can now watch working, end to end — name the Make scenario, the run id and
   the Sent message.
2. Each done-condition D1–D10 ✅/❌ with its evidence pointer. No partial credit.
3. The §2.7 baseline **captured at boot, before any dispatch of yours**: how many Sun–Thu days
   in the preceding week carried a brief. Quote that captured number, not a re-measurement — by
   closing time your own test sends are in the same folder.
4. The artifacts: the PR, the changed files, the Make scenario ids.
5. What is still Tom's (§6), and what is genuinely unfinished.
6. The single next action.
7. **Follow-ups with dates**, so they are not lost: confirm on **2026-10-26** that the first
   post-DST send landed at 17:00 Israel (D7's long-horizon half), and confirm §6D's fallback
   decision is recorded.

Then one short Hebrew line to Tom. If anything is not ready, say so first and plainly.
Tokens per `gt-factory-os-production-brain/VERDICT_GLOSSARY.md`.
