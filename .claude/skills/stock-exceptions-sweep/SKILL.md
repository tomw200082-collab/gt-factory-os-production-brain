---
name: stock-exceptions-sweep
description: >-
  Daily sweep over COMPLETED LionWheel tasks (all drivers) that turns every
  physical stock movement the pick bridge never saw — supplements (השלמת סחורה,
  תעודת משלוח), free goods (ללא חיוב), exchanges, returns, tastings, subcontract
  (עמיתה) and deliveries without order lines — into a FILLED inventory-movement
  proposal in the Factory OS inbox: proposed lines with evidence, a Hebrew
  rationale and open questions. Proposals only; a human approves and only then
  does stock_ledger move. Runs by itself in the API every day at 06:30 (pg_cron);
  use this skill to check a run, dry-run a window or explain a proposal —
  "/stock-exceptions-sweep", "סוויפ חריגי מלאי", "תנועות מלאי מהמשלוחים".
---

# stock-exceptions-sweep

**Tom's written approval (2026-09-23, verbatim):** `תכתוב לי מאסטרפרומפט שאדביק בסשן חדש והוא יבצע הכל מקצה לקצה כולל SIMPLIFY וVERIFICATION BEFORE COMPLITION בסוף כך שאני לא אצטרך לוודא אותו. שימזג והכל ויוודא שירוק. עבודה מקצה לקצה ללא השארת קצוות פתוחים בכלל.`
Given in reply to the diagnosis that proposals must move to a daily sweep that submits filled proposals. Scope: submitting **pending** inventory-movement proposals. Never approving, never the ledger.
**Tom, 2026-09-24 (verbatim):** `אני לא רוצה להפעיל מחדש את הROUTINE הזה.` — the daily-ops-guardian Routine stays off, so the sweep moved out of the guardian into the API (gt-factory-os `api/src/inventory-movements/sweep/`, PR #278) and runs on pg_cron.
Plan of record: `docs/plans/2026-09-23-stock-exceptions-masterprompt.md`.

## What it guarantees

- Every completed LionWheel task that moved stock outside the pick bridge reaches the inbox (`/inbox/approvals/inventory-movement/<id>`) within one daily run, **with at least one proposed line or an open question saying why none could be derived**. The API refuses anything emptier than that.
- Humans approve; `stock_ledger` posts only on approval. The run submits through the same handler as the portal, as **Claude Bot** (`bot@gteveryday.com`, role `operator`; env `SWEEP_ACTOR_EMAIL`). It refuses to run as anything but an active operator, and an operator cannot approve, so Tom approves as usual.
- Its only other write: one `lw_supplier_pickup_no_receipt` exception per supplier pickup with no goods receipt within ±2 days. It is raised once, ever, per task.
- No history is proposed. The live window is the last 3 days. Old movements may already be absorbed by physical counts (47 FG `COUNT_ADJUST` rows since June), and approving them now would double-correct. The job refuses a window unless it is a dry run.

## How it runs

- **Daily, by itself:** pg_cron `stock_exceptions_sweep` (`30 3 * * *` UTC = 06:30 IDT) posts to `POST /api/v1/internal/jobs/stock-exceptions-sweep` with the vault `JOB_RUNNER_TOKEN` (migration `0351`). The route answers 202 and runs in the background.
- **Every run is a `private_core.job_runs` row** (`job_name = 'job.stock_exceptions_sweep'`, `triggered_by` = `cron` or `trigger:dry_run`). `output_summary` holds the report:
  - `counts` per class and `proposals`;
  - `notices` (supplier pickups without a receipt, transfers);
  - `cheques` (every task skipped as a cheque, so a stock task wrongly skipped would show);
  - `errors`, and `submitted` (status, `submission_id` and `replay` per proposal).
- **A dry run or a backtest** is the same endpoint with a body. The bearer is concatenated inside SQL from the vault, never pasted or printed. Run it through the Supabase Management API (a statement, not `read_only`), then read `job_runs`:

```sql
select net.http_post(
  url := 'https://gt-factory-os-api-production.up.railway.app/api/v1/internal/jobs/stock-exceptions-sweep',
  headers := jsonb_build_object('Content-Type', 'application/json', 'Authorization', 'Bearer ' ||
    (select decrypted_secret from vault.decrypted_secrets where name = 'factory_os_job_runner_token')),
  body := '{"dry_run": true, "from": "2026-06-15", "to": "2026-09-22"}'::jsonb,
  timeout_milliseconds := 30000);
-- then: select status, output_summary from private_core.job_runs
--        where job_name = 'job.stock_exceptions_sweep' order by started_at desc limit 1;
```

Idempotency key = `sweep:<lw_task_id>`. Consecutive runs overlap by two days, and a replay returns the same pending proposal. A proposal Tom already decided comes back `409 NOT_PENDING`, which is expected and not an error.
The rules live in `text.ts` (classification) and `derive.ts` (lines), with tests in `api/test/stock_exceptions_sweep_rules.test.ts` and `stock_exceptions_sweep.test.ts`.

## Classes (first match wins, on the visit's recipient name + every note field)

| Class | Signal | Result |
|---|---|---|
| not_completed | `lw_status ≠ COMPLETED` (incl. `CANCELED`) | nothing |
| cheque | the cheque pattern (below) on the title | skipped, listed |
| order | has order lines and no exchange/return/tasting/free-goods word | nothing — the pick bridge posted it |
| subcontract | `עמיתה`, `מדבקות מאצה` | proposal (+ rule-confirmation question) |
| transfer | pick-up word + `ומסירה/ואספקה/ולספק … ל<not מפעל>` | email line only (net zero for our stock) |
| supplier | pick-up word + supplier word/`suppliers.supplier_name_short` | email line only when no goods receipt ±2 days. It is a goods receipt, not an inventory movement |
| free_goods | `ללא חיוב` | proposal |
| supplement | `השלמ`, `תעודת …שלוח` (title) | proposal |
| exchange / return / tasting | `החלפ` / `החזר` / `טעימ`, `דגימ`; pick-up from a customer = return | proposal |
| delivery | no order lines, a 5-digit GI number in the title, or a GI link resolved to a document | proposal |
| unclear | anything else without order lines | proposal with an open question |

Cheque pattern (§1.1): `(^|[\s\-])צ['׳]?ק(ים)?($|[\s\-])` — never `צ.?ק`, which also matches יצחק.
`קבלת סחורה בין 7:00-12:00` is delivery hours. The sweep never classifies on `קבל`.

## Where the lines come from (never a guessed quantity)

1. **The Green Invoice document the task names.** The number comes from the title, the notes or the task's GI link. Type comes from the word next to the number (`חשבונית` → 305 tax invoice, `תעודת …שלוח` → 200 delivery note); with no word, from the first digit (2xxxx / 6xxxx). The document's client must share a word with the task's customer, or the sweep asks instead.
   - **Delivery note or plain delivery** → the document's lines out, mapped as follows:
     - `catalogNum` = `items.barcode`, with leading zeros ignored. Next, the approved `integration_sku_map` alias (`source_channel='green_invoice'`, with its units multiplier). Last, the line description.
     - `excluded_non_stock` aliases, `דמי משלוח` and `פיקדון` are dropped.
     - Anything else that is unmapped becomes a question.
   - **Invoice named on a supplement** → it is the *original* order's invoice (e.g. `השלמת סחורה 63810` = order `#GT13977`, whose shortage was 6×FRESH 0.5L). The lines are that order's open `credit_tasks`, linked through `credit_task_ids`. Approval then closes them if the quantity covers them. With no open shortage, the sweep asks and does not guess from the invoice.
   - **Invoice of an order already picked by another task** → a question, never a second decrement.
2. **The customer's open `credit_tasks`.** Used on non-invoice supplements to link shortages of the same customer and branch for the items shipped. With no lines at all, they are listed as candidates in the question.
3. **Explicit `N × product size` in the text.** Examples: `5×1L חליטה מדברית`, `2 ארגזים דיטוקס 0.5 ליטר` (cases × `case_pack`), `60 יח' Nonomimi Sangria 1000ml`.
   - Product words come from `docs/warehouses/catalog-truth.md` and its SKU codes (היביסקוס = FRESH, לואיזה = DETOX, מדברית = DESERTEA, מסאלה = NAMASTEA, קמומיל = CALM).
   - A missing size, two products in one breath, or `מכל סוג` becomes a question.
   - A lone singular noun (`בקבוק …`) is 1, with confidence `low`.
4. **Otherwise an open question**, carrying the verbatim text.

Units: FG lines use `coalesce(items.sales_uom,'UNIT')` like the pick bridge. `FG-MAT-18G` is sold in cartons of 22 bags and stocked in bags, so document and credit-task quantities are multiplied by 22 (`CARTON_BAG_FACTOR`).
Return and exchange always carry `האם הסחורה חוזרת למלאי או לפחת?`. An exchange with no order lines proposes the item back in and the replacement out.

## Backtest — 2026-06-15..2026-09-22 (run 2026-09-23, rerun 2026-09-24)

1,459 tasks in the window. 112 were not completed and produced nothing. 1,212 were orders covered by the pick bridge. 27 cheques were skipped, all genuine (listed in the run). There were 20 supplier pickups (11 with no goods receipt within ±2 days) and 7 transfers, which became 18 notices. That left **81 proposals**: supplement 27, free_goods 18, return 9, subcontract 9, unclear 8, exchange 6, delivery 4.
33 proposals carry lines (71 lines, 14 credit-task links). The rest carry open questions. Every supplement that names a document number (12) got lines, except two that got an explicit question: 63161 names an inactive item, and 63914's order has no open shortage.
Cross-check: GI-20269 (hand-posted 2026-06-30 with Tom's approval) comes out as exactly the four lines Tom approved: 180 DETOX 1L, 60 NAMASTEA 1L, 36 REVIVE 1L, 1100 bags MATCHA 18G.
Parity (2026-09-24): the API's TypeScript rules, run over the same inputs, reproduce the Python report task by task — same counts, 81/81 proposals identical (only Green Invoice's per-call download tokens differ), same notices and cheques.

## Data contracts (live, 2026-09-23)

- LionWheel `GET /api/v1/tasks/show/{id}.json` → `status` (`COMPLETED`/`CANCELED`), `completed_at` `DD/MM/YYYY HH:MM`, `notes`, `driver_note` (often the GI download link), `org_note`, `order_items[]`, `pod_link`, `visits[0].recipient_name` (the title), `visits[0].notes`. A deleted task answers 404; the sweep falls back to the mirror title.
- Green Invoice: see `route-print-pack/SKILL.md` §Data contracts (search by `number` + `type`, `income[]` fields). The API needs `GREENINVOICE_KEY_ID`/`GREENINVOICE_SECRET` on Railway (`GREENINVOICE_API_BASE_URL` defaults to the public API). Without them every named document becomes an open question instead of lines. The job never drops a movement over it. On 2026-09-24 the keys were missing: auth failed with HTTP 400, and `gi_credit_drafts` has failed the same way since May.
- Green Invoice PDF (a task that names no number but carries a GI link): `unpdf` reads the page; pdf.js prints the type before the number (`תעודת משלוח 20272`), pymupdf printed it after, and both orders are accepted.
- DB: the API reads Postgres directly. From a Claude session, read `job_runs` through the Supabase Management API (`read_only: true`); the container has no route to the pooler's TCP 5432.
- Submit: the job calls `handleInventoryMovementSubmit`, the code behind `POST /api/v1/mutations/inventory-movements`, with body = the proposal (`proposed_lines[]` with `source`/`evidence_ref`/`confidence`, `rationale`, `open_questions[]`, `evidence[]`, `credit_task_ids[]`) + `idempotency_key`, `source_ref` = task id, `event_at` = completion time. It fails with 409 plus `offending_field` when a proposed item or unit is wrong.

## Never

- Write `form_submissions`, `inventory_movements`, `exceptions` or `stock_ledger` directly (Supabase MCP included). It bypasses every check the API makes.
- Approve, reject or edit a proposal. That is Tom's step (the bot is an `operator`).
- Widen the live window to reach history (§1.1).
- Run a live sweep from a Claude session. The API job is the only live runner; a session dry-runs through the endpoint.
- Use `captured_at` for windows. It is the last poll time and moves every poll; windows use `lw_completed_at`.
