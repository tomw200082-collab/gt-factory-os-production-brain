# MASTERPROMPT — the daily sales brief reaches Tom and Dean by 17:05, or they hear why

**STATUS: LIVE**
<!-- The executing session's last act is to change this to SHIPPED / SUPERSEDED by <path> /
ABANDONED — why, with evidence pointers. A recurring Routine does NOT stamp this: the
document is the Routine's standing instruction, not a one-shot plan. Stamp it only when
the Routine itself is retired or replaced. -->

> **Usage:** this is the standing instruction for a scheduled Routine that fires a fresh
> session **Sunday through Thursday at 17:00 Israel time** with `gt-factory-os` attached.
> It builds the day's net sales brief from Green Invoice and mails it to Tom and Dean.
>
> **This is not the sales-report artifact.** That is a different report, from a different
> source, on a different schedule — see §1.2. Confusing the two is the main way this
> document gets misread.
>
> **Provenance:** written 2026-09-02 from a real run of the pipeline in this environment —
> `SALES_REPORT_DATE=2026-09-01 bash run_daily.sh`, 1m18s wall clock, all three output
> files produced, headline `₪36,074`. Every number in §2 was observed in that run, not
> recalled. The live-system claims in §1.2 and §2.3 were checked against `cron.job` and
> the repository on the same day.
> Authority: `gt-factory-os-production-brain/CLAUDE.md` ·
> `gt-factory-os/tools/sales-forecast/README.md` — the pipeline's own documentation, which
> wins on anything about data semantics.
>
> **Shelf life:** the §2 numbers are a fingerprint, not a target — they change every day by
> design. What must stay true is the *shape*: three output files, two recipients, one send,
> and figures carried byte for byte.

## 0. How to work

- **Who you are here:** one fresh session per firing, no memory of yesterday. You hold the
  Gmail connector and a clone of `gt-factory-os`. The Green Invoice credentials are
  environment variables in this environment, not a connector.
- **Your job is mechanical, and that is the point.** The pipeline computes; you carry.
  Do not summarise, re-type, round, translate, recompute or "improve" any figure. Every
  number Tom and Dean read comes out of the generated files, byte for byte. A number you
  retyped is a number nobody can trace.
- **Read first:** `gt-factory-os/tools/sales-forecast/README.md`. It is the authority on
  what the figures mean — the net basis, the 17:00 freeze, why no hour reaches 100%. This
  document supplies the run, the traps and the halt conditions, and does not restate it.
- **Authority:** where this document and that README disagree, the README wins and this
  document is wrong — say so in the run report.
- **Halt conditions, evidence standard:** inherited from
  `gt-factory-os-production-brain/CLAUDE.md` §Stop conditions and §Evidence. Deltas for
  this work only are in §7.
- **The standard:** `עדיף פחות — אסור לשקר`. A missing brief gets chased; a wrong one gets
  acted on. When in doubt, send nothing and say why.
- **First action, before anything else:** run the boot checks in §2.5. They cost one
  paste and they tell you at minute one whether the pipeline and the schedule have
  drifted apart — which is the failure that would otherwise reach Tom's inbox looking fine.
- **Language:** these instructions are English because that is the register you reason
  best in. **Output language: concise English** for your own replies and run report —
  short sentences, no preamble — with the single line to Tom in Hebrew. The email body
  itself is Hebrew and is *generated*: you never write it.

## 1. Mission and definition of done

**One testable sentence:** on a business evening, Tom and Dean each hold one email whose
every figure came out of a pipeline run that finished minutes earlier — the 17:00 firing
plus the pipeline's measured 1m18s, so in the inbox within a few minutes of the hour.

| # | Condition | The observation that would prove it false |
|---|---|---|
| D1 | The pipeline ran to completion today | `run_daily.sh` exited non-zero, or printed anything other than its `DONE →` line last |
| D2 | All three outputs exist and are non-empty | `email_subject.txt`, `email_body.html` or `dashboard/GT_Sales_Forecast.html` is missing or zero bytes |
| D3 | The mail carries the generated subject | the sent subject differs by even one character from `email_subject.txt` |
| D4 | The mail carries the generated body, whole | `email_body.html` was edited, truncated, re-flowed, or re-rendered rather than sent as-is |
| D5 | Exactly one send, to exactly two recipients | Gmail sent-mail shows zero, or two, briefs for today — or a `to:` line missing either address |
| D6 | The interactive report is attached | the message has no `GT_Sales_Forecast.html` attachment |
| D7 | A failed run sent nothing | a brief went out on a day whose run report records a failure |
| D8 | The run left no repository dirty | `git status --porcelain` non-empty in `gt-factory-os` |

Anything not on this list is out of scope unless Tom asks.

### 1.1 Settled — do not reopen

- **The basis is net of credit notes** — Green Invoice document type `330`, the credit-note
  type used throughout `pull_credits.py` — ex-VAT. Not gross.
  Cancel-and-reissue is common at GT, so a gross report double-counts: on 2026-08-09 one
  order was invoiced three times and credited twice, showing ₪780,561 against a true net
  of ₪266,658. `build_forecast.py` aborts if `credit_lines.json` is missing rather than
  publish gross figures under a net label.
- **The day is frozen at 17:00** from Green Invoice `creationDate`, and the expectation and
  the year-ago comparator are cut to the same hour. A re-run reproduces the same 17:00
  report, never a later, larger one. `CUTOFF_HOUR` in `build_forecast.py` is the authority.
- **Recipients: `tom@gteveryday.com` and `arbel.dean@gmail.com`.** Both, always. No third
  address without Tom. No customer-facing message, ever.
- **Read-only against Green Invoice.** The pipeline writes to no external system.

### 1.2 This is not the sales-report artifact — the two, side by side

Two sales reports run on different days of the same week and will not agree. Both are
right. Knowing why is the difference between a cross-check and a fire drill.

| | this daily brief | the sales-report artifact |
|---|---|---|
| Source | Green Invoice invoices | Shopify orders |
| Basis | net of credit notes, ex-VAT | `discountedTotalSet.shopMoney`, ex-VAT, cancelled excluded |
| Cut | frozen at 17:00 Israel | whole days, `Asia/Jerusalem` |
| Delivered as | an email, built fresh each run | a republished artifact at a fixed URL |
| Standing instruction | this file | `2026-08-30-weekly-sales-report-routine-masterprompt.md` |

Worked example, 2026-09-01: this brief reports `₪36,074`; the artifact's daily sheet
reports `₪38,966` for the same day. The gap is the 17:00 cut (capture measured `0.955`
that run) plus credit netting plus invoice-vs-order timing — `38,966 × 0.955 ≈ 37,213`,
and credits close most of the rest. **A gap of this size and direction is expected.** A
gap that reverses sign, or exceeds ~15%, is worth surfacing to Tom; it is not worth
holding the send for.

**This Routine never touches the artifact.** It does not publish it, read it, or link it.

## 2. Ground truth — measured 2026-09-02; re-verify at boot

### 2.1 What is built and live

- **The pipeline:** `gt-factory-os/tools/sales-forecast/run_daily.sh` — five stages,
  pure Python standard library, **no `pip install`**. Never install packages in a
  scheduled run.
- **Its outputs**, written beside the scripts: `email_subject.txt`, `email_body.html`,
  `dashboard/GT_Sales_Forecast.html`.
- **Credentials:** `GREENINVOICE_API_BASE_URL`, `GREENINVOICE_KEY_ID`,
  `GREENINVOICE_SECRET` — already environment variables in this environment (verified
  2026-09-02). Nothing to configure.
- **Transport:** the **Gmail connector**, enabled on the Routine itself. This is the one
  manual dependency and the one thing that has actually failed.

### 2.2 The numbers — replay run of 2026-09-01, executed 2026-09-02

```
run_daily.sh  5/5 stages  ·  1m18s wall clock
cutoff 17:00 · capture=0.955 measured over 115 trading days
subject   GT · מכירות 01/09/2026 עד 17:00: ₪36,074 (101% מהיעד · שנה +51% מאשתקד)
day       actual ₪36,074    vs expected ₪35,772    = 101%
month     actual ₪36,074    vs expected ₪35,772    = 101%
quarter   actual ₪1,499,379 vs expected ₪1,616,581 =  93%
year      actual ₪4,065,959 vs expected ₪4,065,657 = 100%
outputs   email_subject.txt 97 B · email_body.html 12,034 B
          dashboard/GT_Sales_Forecast.html 75,717 B
credits held out of netting (expense, not returned product): 2 lines, ₪36,907 total
```

Two held-out credit lines is the expected count and the script prints them every run so
the list cannot rot unnoticed. A sudden jump there is worth a line to Tom.

### 2.3 What is NOT in the path any more — do not re-introduce it

- **GitHub Actions.** On 2026-08-30 the account's Actions minutes ran out at 15:06 UTC;
  the 17:00 dispatch created a run that died in six seconds without the job ever starting,
  and nothing arrived. `.github/workflows/daily-sales-forecast.yml` still exists and still
  accepts a `workflow_dispatch` — **nothing dispatches it, and running it sends a real
  brief to both recipients.** Never call it from this Routine.
- **pg_cron.** `daily_sales_report` and `daily_sales_report_verify` were unscheduled on
  2026-08-31. Verified 2026-09-02: neither appears in `cron.job`. Migration `0339` stays
  in history because it was never reverted by a later migration; it records how the job
  was created, not that it is running.
- **SMTP.** Blocked in this environment — port 465 times out, verified 2026-08-31. If the
  Gmail connector is missing, there is no fallback transport. Do not improvise one.

### 2.4 Known limits, stated rather than hidden

- **A firing that never happens is invisible.** While pg_cron drove this, a dropped
  dispatch left a `private_core.job_runs` row. Nothing writes that row now. A missing
  brief is the only signal, and it is a signal only if somebody notices. Open.
- **Roughly a tenth of the day is not on the books at 17:00**, and the residual ~2.5% is
  backdating, not a late tail. This is why the report compares like with like rather than
  reading a partial day against a full-day bar. README, *Reading a day that is still open*.
- **The frozen daily headline is never revised.** Month, quarter and year rebuild from
  full history each run and self-heal; the day does not.

### 2.5 Re-verification block — run at boot, before trusting anything above

```bash
git -C "$HOME/gt-factory-os" pull --ff-only

cd "$HOME/gt-factory-os/tools/sales-forecast"
ls run_daily.sh build_forecast.py build_email_body.py     # all three present
grep -c "CUTOFF_HOUR=17" build_forecast.py                # expect 1
for v in GREENINVOICE_API_BASE_URL GREENINVOICE_KEY_ID GREENINVOICE_SECRET; do
  [ -n "${!v}" ] && echo "$v ok" || echo "$v MISSING"
done
TZ=Asia/Jerusalem date +'%Y-%m-%d %H:%M %a'               # must be >= 17:00, Sun-Thu
```

A missing credential, or a `CUTOFF_HOUR` that is no longer `17` while the Routine still
fires at 14:00 UTC, means the pipeline and the schedule have drifted apart. Halt and tell
Tom rather than sending a brief labelled with an hour that does not match its data.

**Where the run happens:** copy the scripts to the session's scratchpad and work there —
`<scratchpad>/sf/`. The pipeline writes `data/` and `dashboard/` beside itself, and
leaving those inside the clone fails D8.

## 3. What the hard part actually is

- **It looks like sending an email. It is refusing to send the wrong one.** Every guard in
  this pipeline exists because a plausible number gets acted on. `build_forecast.py`
  aborts rather than publish gross-under-a-net-label, rather than label an hour that has
  not happened, and rather than compare a partial day to a full-day bar. Your job inherits
  that posture: the send is the easy half.
- **The temptation is to be helpful with the figures.** Rounding a shekel, translating a
  label, "fixing" a percentage that looks off — each one severs the number from the run
  that produced it. Carry the files.
- **A duplicate brief is a real cost**, not a harmless retry. Two briefs with different
  numbers for the same day is worse than none. If you cannot tell whether a send
  succeeded, check Gmail sent mail before trying again.

## 4. Workstreams

Three, in order. Each one's acceptance is a done-condition from §1; nothing here is
parallel and nothing here is optional.

### W1 — Build
Pull, copy the scripts to `<scratchpad>/sf/`, run `bash run_daily.sh`. Expect ~80 seconds
and a final `DONE →` line. Do not set `SALES_REPORT_DATE` — the daily run reports today.
**Acceptance:** D1, D2.

### W2 — Send (Gmail connector, `send_message`)
```
to:          tom@gteveryday.com AND arbel.dean@gmail.com   (both, always)
subject:     the exact contents of email_subject.txt
htmlBody:    the exact contents of email_body.html, whole and unedited
body:        a plain-text fallback carrying the same headline numbers,
             read off the same files
attachments: dashboard/GT_Sales_Forecast.html
             base64 · filename GT_Sales_Forecast.html · mimeType text/html
```
Send exactly once. **Acceptance:** D3, D4, D5, D6.

### W3 — Report
One short Hebrew line to Tom with the headline figure. Note anything from §2.2 that moved
unexpectedly — a jump in held-out credit lines, a capture ratio far from `0.955`.

## 5. Scope

**IN:** everything in §4.

**OUT — do not touch, do not "improve":**

- Any figure, label or percentage in the generated files.
- `CUTOFF_HOUR`, the netting rule, `mapping.credit_is_sales_reduction()`, the recipients.
  All are data-semantics decisions; changing one silently invalidates every earlier brief.
- `gt-factory-os/tools/sales-forecast/*` — read and run them, do not edit them mid-run. A
  script fix is a separate PR on a weekday, never inside a scheduled send.
- The GitHub Actions workflow (§2.3) and anything in pg_cron.
- The sales-report artifact (§1.2). Different Routine, different source.
- Any write to any external system. This run is read-only apart from the one email.

## 6. Tom's part

**Create the Routine** from the appendix, and confirm the **Gmail connector is enabled on
it**. Nothing else is his — the credentials and the pipeline are already in place.

Worth a decision when he has a minute, not blocking:

- **§2.4, first bullet:** a firing that never happens is currently invisible. If that
  matters, the cheapest fix is a second Routine that checks for today's brief in Gmail and
  pings only when it is absent. Not built; not proposed as urgent.

## 7. Halt conditions

Inherited set cited in §0. Additions specific to this work:

- **Gmail connector missing from the session** → do **not** improvise another transport
  (§2.3). Tell Tom in one Hebrew line that the Routine needs the Gmail connector enabled
  on it in the claude.ai Routines UI.
- **Pipeline fails, or any of the three outputs is missing or empty** → send **nothing**.
  Tell Tom the exact error. Never invent, estimate, or carry over yesterday's figure.
- **A boot check in §2.5 fails** → halt, tell Tom, send nothing.
- **It is before 17:00 Israel** → `build_forecast.py` will refuse, and it is right to.
  Do not reach for `SALES_REPORT_DATE` to get past it: that guard exists because a report
  labelled 17:00 must hold 17:00 data.
- **The run would change a figure, a recipient, or a threshold** → halt, surface to Tom.
- **Never end this run silently.** Either the brief went out, or Tom hears why it did not.

## 8. Final report

Concise English, at the end of every firing:

1. Whether the brief went out, to whom, and with what headline figure.
2. Each done-condition D1–D8 ✅/❌ with its evidence pointer — no partial credit.
3. The Gmail message id.
4. Anything from §2.2 that moved unexpectedly.
5. The single next action, if any.

If anything is not ready, say so first and plainly. Tokens per
`gt-factory-os-production-brain/VERDICT_GLOSSARY.md`.

---

## Appendix — Routine configuration

**Connectors the fired session needs:**

| Connector | Why | Access used |
|---|---|---|
| Gmail | the one email to Tom and Dean | send |

**Nothing else.** Green Invoice is reached through environment variables, not a connector.
No Shopify, no Supabase, no Drive, no Calendar, no Context7 — the previous Routine carried
all of them and used none. Fewer connectors is less that can go wrong at 17:00.

**Repository:** `gt-factory-os` only.

**No outcome branches.** This Routine never pushes. If one is configured, remove it.

**Schedule:** Sunday-Thursday 17:00 Israel time → cron `0 14 * * 0-4` in UTC while IDT
holds. From **2026-10-25** Israel leaves DST and the same expression fires at 16:00, which
`build_forecast.py` will refuse outright — move it to `0 15 * * 0-4` that week.

**Session mode:** a fresh session per firing.

**Routine prompt — paste this as the Routine's message:**

```
Send the GT daily sales brief. It is now 17:00 Israel (this fires 14:00 UTC, Sun-Thu).

Read gt-factory-os-production-brain/docs/plans/2026-09-02-daily-sales-brief-routine-masterprompt.md
first — it is the standing instruction for this Routine, including its halt conditions
and the boot checks in section 2.5. This message is the short form of it.

Your job is mechanical. The pipeline produces the email; you only carry it. Do not
summarise, re-type, round, translate or "improve" any figure — every number Tom and
Dean read must come from the generated files, byte for byte.

STEP 1 — BUILD
  git -C ~/gt-factory-os pull --ff-only
  copy ~/gt-factory-os/tools/sales-forecast/*.py and *.sh into <scratchpad>/sf/
  cd <scratchpad>/sf && bash run_daily.sh
~80 seconds. Pure Python stdlib — never pip install. It reads GREENINVOICE_API_BASE_URL,
GREENINVOICE_KEY_ID and GREENINVOICE_SECRET, already environment variables here. Work in
the scratchpad, not in the clone: the pipeline writes data/ and dashboard/ beside itself
and must leave the repo clean. Do NOT set SALES_REPORT_DATE — the daily run reports today.

STEP 2 — SEND (Gmail connector, send_message)
  to:          tom@gteveryday.com AND arbel.dean@gmail.com   (both, always)
  subject:     the exact contents of email_subject.txt
  htmlBody:    the exact contents of email_body.html, copied whole and unedited
  body:        plain-text fallback carrying the same headline numbers, off the same files
  attachments: dashboard/GT_Sales_Forecast.html, base64,
               filename GT_Sales_Forecast.html, mimeType text/html
Send exactly once. If you are unsure whether a send succeeded, check Gmail sent mail
before retrying — a duplicate brief is a real cost.

STEP 3 — REPORT
One short Hebrew line to Tom with the headline number.

DO NOT
- Do not call GitHub Actions. The workflow daily-sales-forecast.yml still accepts a
  dispatch and would send a second real brief to both recipients. Nothing dispatches it.
- Do not touch the sales-report artifact. That is a different report on a different
  Routine, from Shopify rather than Green Invoice. The two will not agree, and both are
  right — section 1.2 of the masterprompt explains the gap.
- Do not edit any figure, recipient, threshold, or script.

FAILURE RULES — these matter more than the send
- Gmail connector missing from this session: do NOT improvise another transport. SMTP is
  blocked here (port 465 times out, verified). Tell Tom in one Hebrew line that the
  Routine needs the Gmail connector enabled on it in the claude.ai Routines UI.
- Pipeline fails, or any of email_subject.txt / email_body.html /
  dashboard/GT_Sales_Forecast.html is missing or empty: send NOTHING and tell Tom the
  exact error. A wrong or partial number gets acted on; a missing brief gets chased.
  Never invent, estimate or carry over yesterday's figure.
- Never end this run silently. Either the brief went out, or Tom hears why it did not.
עדיף פחות — אסור לשקר.
```
