# STANDING INSTRUCTION — the daily sales brief: dispatch it, then prove it arrived

**STATUS: LIVE — this is the Routine's standing instruction, read on every firing.**

> ## ⚠️ THIS SUPERSEDES THE "STEP 2 — SEND" TEXT IN THE ROUTINE MESSAGE
>
> The Routine's pasted message still says to build the report and send it yourself through the
> Gmail connector. **That instruction is dead and must not be followed.** It is physically
> impossible (§1) and it is why the 2026-09-02 brief never went out.
>
> **You do not build the report. You do not send any email. You dispatch a workflow and then
> prove the mail arrived.** Where the Routine message and this file disagree, this file wins —
> the Routine message itself says so ("it is the standing instruction for this Routine … This
> message is the short form of it").
>
> Rewritten 2026-09-03 after the third consecutive miss. Full analysis, and the plan this came
> from: `docs/plans/2026-09-03-daily-sales-brief-delivery-fix-masterprompt.md`.

## 1. Why you must not send it yourself

The brief carries `dashboard/GT_Sales_Forecast.html` as an attachment — 76,322 B, which is
101,764 base64 characters (~93,570 tokens). The Gmail connector accepts an attachment only as one
inline base64 string in a single tool call. Measured 2026-09-02: the `Read` tool refused to return
the file whole, and composing the `create_draft` call exceeded the session's output limit.

**A session cannot carry this attachment. Not with a retry, not with a better prompt.** Every
minute spent trying is a minute the brief is late. Dispatch the workflow instead — it attaches the
file server-side, from disk, and it is proven (Actions run #136, 2026-09-03, delivered to both
recipients with the attachment).

## 2. What to do, in order

**Stop at the first step that says stop. Do not improvise past it.**

1. **Check the hour.** `TZ=Asia/Jerusalem date +'%Y-%m-%d %H:%M %a'`.
   - Before **17:00** Israel → **stop silently.** Do not dispatch. `build_forecast.py` refuses to
     label an hour that has not happened, and a dispatch would fail the job and mail Tom a false
     alarm. (This is also the daylight-saving guard: the Routine's cron is UTC, so from
     2026-10-25 one firing lands at 16:00. Stopping is the correct response to that firing.)
   - Not Sunday–Thursday → stop silently.

2. **Check it has not already gone out.** Gmail, with **today's date in the subject**:
   `in:sent subject:"GT · מכירות DD/MM/YYYY"` (today, Israel).
   - Found → **stop silently.** A duplicate brief is a real cost.
   - **Never search the undated `subject:"GT · מכירות"`** — a stale-day send carries an earlier
     date, so an undated search matches it and tells you a healthy day when it is not.

3. **Dispatch the builder-and-sender.**
   `mcp__github__actions_run_trigger` · `method=run_workflow` ·
   `owner=tomw200082-collab` · `repo=gt-factory-os` ·
   `workflow_id=daily-sales-forecast.yml` · `ref=main`.
   A `204` means *queued*, not sent.

4. **Poll the run to completion.** `mcp__github__actions_list method=list_workflow_runs
   resource_id=daily-sales-forecast.yml` to find it, then `mcp__github__actions_get
   method=get_workflow_run`. Typical wall clock ~90 s. Wait for `status=completed`.

5. **Prove the mail exists.** Search Gmail Sent again for today's dated subject. It must exist,
   carry **both** `tom@gteveryday.com` and `arbel.dean@gmail.com`, and be of the order of
   120 KB — a body-only mail is ~15 KB, so the size gap is the attachment's fingerprint.

6. **Report.** One short Hebrew line to Tom with the headline figure, read from the sent subject.

## 3. When something fails — notify, never improvise

Any of these → **push notification to Tom in Hebrew, immediately, naming what failed**:

- The dispatch call errors, or the run never appears.
- The run completes with `conclusion != success`.
- The run succeeds but no message with today's dated subject is in Sent.
- The run dies before the job starts (this happened 2026-08-30 when the account's Actions minutes
  ran out — note the workflow's own `Alarm on failure` step is *inside* the job and cannot fire in
  this case, so **you** are the only detector).

**Do not** send a substitute email from the session. **Do not** send the brief without its
attachment — the generated body states that the full report is attached, so a body-only send is a
false statement. **Do not** edit any figure, recipient, threshold or script.

**Never end a firing silently.** Either the brief went out and you can point at the Sent message,
or Tom hears why it did not.

## 4. What the numbers mean — do not re-derive or "improve" them

- The day is **frozen at 17:00** Israel from Green Invoice `creationDate`, and the expectation and
  the year-ago comparator are cut to the same hour, so a later or manual run reproduces the same
  17:00 report rather than a larger one.
- The basis is **net of credit notes, ex-VAT**. Cancel-and-reissue is common at GT; a gross report
  double-counts.
- Since 2026-09-03 `build_forecast.py` **refuses** when a scheduled run finds no invoice dated
  today — otherwise it silently rebuilt an earlier day and mailed it under that date with a
  different figure. If the job fails with `no invoice dated … yet`, that is this guard working:
  report it to Tom, do not work around it, and never set `SALES_REPORT_DATE` to get past it.
- `SALES_REPORT_DATE` replays a **past** day only. The daily firing never sets it.

Authority on data semantics: `gt-factory-os/tools/sales-forecast/README.md`. It wins over this
file on anything about what the figures mean.

## 5. Recipients and scope — settled, do not reopen

- `tom@gteveryday.com` **and** `arbel.dean@gmail.com`, both, always. They are hardcoded in
  `.github/workflows/daily-sales-forecast.yml`; you never type them into a message.
- Out of scope, every firing: the sales-report artifact (a different report, Shopify-sourced, its
  own Routine — the two will not agree and both are right), pg_cron, migration `0339`, and any
  change to the email's HTML.

## 6. Known open item

Same-evening detection when the Routine itself never fires is not yet covered — nothing outside
this session watches for that. A morning backstop runs in the day-open ritual. The permanent fix
(an independent 17:40 auditor) is specified in
`docs/plans/2026-09-03-daily-sales-brief-delivery-fix-masterprompt.md` §4 W3 and needs one
credential from Tom.

---
**Output language:** concise English for your own reporting, with the single line to Tom in
Hebrew. The email body itself is Hebrew and is *generated* — you never write it.
`עדיף פחות — אסור לשקר.`
