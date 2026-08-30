# MASTERPROMPT — the sales report is final and in Tom's inbox every Sunday by 09:00 IL

**STATUS: LIVE — not yet executed**
<!-- The executing session's last act is to change this to SHIPPED / SUPERSEDED by <path> /
ABANDONED — why, with evidence pointers. A weekly Routine does NOT stamp this: the
document is the Routine's standing instruction, not a one-shot plan. Stamp it only when
the Routine itself is retired or replaced. -->

> **Usage:** this is the standing instruction for a scheduled Routine that fires a fresh
> session every Sunday at 08:00 Israel time with `gt-factory-os`,
> `gt-factory-os-production-brain` and `Sales-Machine` attached. It takes the sales
> report from "last week's numbers" to "this morning's numbers, gate-verified, link in
> Tom's inbox". It halts for Tom only where §6 says so.
>
> **Provenance:** written 2026-08-30, from a full manual run of the pipeline that
> morning — Shopify bulk operation `gid://shopify/BulkOperation/8003722150129`
> (33,602 objects, completed `2026-08-30T07:00:48Z`), all four gates green, artifact
> republished and email sent at 10:00 IL. Every number in §2 was observed in that run,
> not recalled.
> Authority: `gt-factory-os-production-brain/CLAUDE.md` ·
> `gt-factory-os-production-brain/EXECUTION_POLICY.md` ·
> `gt-factory-os-production-brain/.claude/skills/weekly-sales-report/SKILL.md` — cited
> below, never copied.
>
> **Shelf life:** §2 numbers are a fingerprint, not a target — they change every week by
> design. What must stay true is the *shape*: same artifact URL, same four gates, same
> script paths. If a boot check in §2.5 contradicts this document, **halt and surface to
> Tom** rather than adapting — a silently changed pipeline is exactly the failure this
> report exists to prevent.

## 0. How to work

- **Who you are here:** one fresh agent session per firing, no memory of last week. You
  hold the Shopify MCP connector (read-only use here), the Gmail MCP connector, the
  `Artifact` tool, and local clones of the three repos above. You may decide everything
  inside §4 alone. You may not change taxonomy, thresholds, or the recipient.
- **First action, before anything else:** run the boot checks in §2.5. They cost one
  paste and they are the difference between a stale checkout crashing at minute nine and
  you knowing at minute one.
- **Read first, in order:**
  1. `gt-factory-os-production-brain/.claude/skills/weekly-sales-report/SKILL.md` — **the
     procedure. Follow its steps 1–8 verbatim.** This document does not restate them; it
     supplies the cadence, the ground truth, and the traps.
  2. `Sales-Machine/recipes/sales-report.md` — the method and the five correctness gates.
  3. `gt-factory-os/scripts/sales-report/README.md` — the run order.
- **Authority:** where this document and any file above disagree, that file wins and this
  document is wrong — say so in the run report.
- **Halt conditions, evidence standard, git discipline:** inherited from
  `gt-factory-os-production-brain/CLAUDE.md` §Stop conditions and §Evidence. Deltas for
  this work only are in §8.
- **The standard**, in Tom's words from `SKILL.md` step 8: `עדיף פחות — אסור לשקר`
  ("better less — lying is forbidden"). Translated into three checkable prohibitions:
  1. Nothing is published that failed a gate.
  2. No number reaches the email that did not come out of `out/*.json` or the bridge run
     in this same session.
  3. The freshness stamp is the bulk operation's real `completedAt`, never the time you
     happen to be writing the email.
- **Language:** these instructions are English because that is the register you reason
  best in. Data literals stay in their own script, in backticks, and are never
  translated. **Output language: concise English** for your own replies and run report —
  short sentences, no preamble. **The email body and the report page stay Hebrew**, per
  `SKILL.md` — that is audience, not register.

## 1. Mission and definition of done

**One testable sentence:** every Sunday morning the artifact at the fixed URL carries
gate-verified numbers stamped with this morning's pull time, and Tom has one email
holding the link, the stamp, three opening numbers and one thing to check.

| # | Condition | The observation that would prove it false |
|---|---|---|
| D1 | The artifact is republished to the **same** URL | `Artifact action:"read" url:"https://claude.ai/code/artifact/ad0dd380-d95e-4a21-94e3-af9ee386fc88"` → header line does **not** contain today's date and the pull time |
| D2 | Full-window identity within tolerance | `GT_RANGE_END=<END> python3 analyze_bridge.py` final block prints `FAIL`, or `\|delta\|` above `0.5%` |
| D3 | Order counts reconcile exactly | `out/gates.json` → any entry in `gate2` with `match_all: false` |
| D4 | Taxonomy coverage total, nothing discarded | `out/gates.json` → `gate3.skus_total != gate3.mapped_tsv + gate3.historical` |
| D5 | Manual sanity holds | the three orders in `gates.json.gate5_sample` re-pulled live differ from the file on any SKU, quantity or `discountedTotalSet` |
| D6 | Exactly one email delivered to `tom@gteveryday.com` | Gmail shows zero, or two, messages with today's subject |
| D7 | A failed gate published nothing | the artifact's stamp advanced on a morning whose run report records a `FAIL` |
| D8 | The run left no repository dirty | `git status --porcelain` non-empty in any of the three repos |

Anything not on this list is out of scope unless Tom asks.

### 1.1 Settled — do not reopen

Approved by Tom 2026-08-24, re-confirmed in the 2026-08-30 run:

- The revenue base is the stored ex-VAT price — line `discountedTotalSet.shopMoney`.
- The independent anchor is ShopifyQL `total_sales`. `net_sales`, `gross_sales`,
  `taxes` and `customer.amountSpent` are **forbidden** in report numbers: the store is
  configured `taxesIncluded=true @17%`, so those columns subtract a fictitious `17/117`.
- Month attribution is `Asia/Jerusalem`, not UTC.
- Cancelled orders are excluded from revenue and reported separately; refunds are zero
  across the whole window because GT cancels rather than refunds.
- The SKU mapping table approved by Tom on 2026-08-24 (202 SKUs then, 203 in the
  2026-08-30 run — §2.2), the historical bucket, and the three manual chain assignments
  are frozen. `*-chain` tags from the field were **not** adopted.
- Recipient: `tom@gteveryday.com` only. No customer-facing message, ever
  (`SALES_CUSTOMER_OUTREACH_WRITE_ENABLED=false`).

## 2. Ground truth — measured 2026-08-30 10:00 IL; re-verify at boot

### 2.1 What is built and live

- **The artifact:** `https://claude.ai/code/artifact/ad0dd380-d95e-4a21-94e3-af9ee386fc88`
  — permanent. Republishing means calling `Artifact` with `url` set to exactly that.
- **The pipeline:** `gt-factory-os/scripts/sales-report/` — `build_facts.py` →
  `analyze_bridge.py` → `build_report.py`. Inputs `raw/orders.jsonl` and
  `shopifyql_month.json` live beside the scripts and are not in git.
- **The price map:** `gt-factory-os-production-brain/docs/pricing/2026-08-05_shopify_products_exvat.tsv`
  (hardcoded absolute path inside `build_facts.py` — see landmine 8).
- **The procedure:** `weekly-sales-report` skill, present in the brain repo.

### 2.2 The numbers — run of 2026-08-30, window `2024-08` → `2026-08`

```
orders pulled 7,255 · counted 6,882 · cancelled 360 · test 0 · no customer 0
fact rows 20,371 · SKUs 203 · customers 806 · historical SKUs 98
FULL WINDOW 2024-08..2026-07 (24 months)  identity=9,565,345  total_sales=9,579,699
                                          delta=-0.150%  tolerance=±0.5%  ->  PASS
months matching to the shekel 14/24 · order-count match 24/24 · coverage 203/203
manual sanity 3/3  (#GT11030, #GT9836, #GT12842 re-pulled live, identical line by line)

last 12 full months 08/25-07/26   ₪5,806,284   +54.5% vs the 12 before
last full month 07/2026           ₪724,387     +45.4% vs 07/2025
partial 08/2026 as of 30/08       ₪767,284
active customers, 12 months       585
bulk operation                    33,602 objects, 18.1 MB, ~8 minutes wall clock
```

### 2.3 What is NOT built

- No automatic evidence snapshot. `Sales-Machine/evidence/` holds `2026-08-24` only;
  weekly runs do not write one (see §5 OUT).
- No Excel export in the weekly path — `build_excel.py` needs `openpyxl`, which is not
  installed in this environment.
- No alert if the Routine itself fails to fire. A silent Sunday is invisible.

### 2.4 Known-broken, adjacent, out of scope

- Four SKUs of the 0.3-litre extract line — `GT-HIB-LOW-0.3L`, `GT-LUI-LOW-0.3L`,
  `GT-CHA-LOW-0.3L`, `GT-SEN-LOW-0.3L` — did ₪243,000 in `2026-08` and are **not** in
  the price map, so they land in the visible historical bucket. Correct behaviour, but
  the mapping wants updating: Tom's call, §6C.
- `2026-04` shows a −₪269,006 reversal spike: a retroactive cleanup that cancelled ~60
  orders from 2024–2025 in one month. Pre-existing, explained, not a defect.
- `2026-08` is skewed by one live ₪229,500 order plus two cancelled versions of it from
  the same customer. Never read the partial month as a trend.
- `U-003` (pricing-tag semantics) and `U-010` (chain unification) remain open in
  `Sales-Machine/CURRENT_STATE.md`. Not this run's business.

### 2.5 Re-verification block — run at boot, before trusting anything above

```bash
# 1. the scripts exist and carry the 2026-08-30 fixes (all four checks must hit)
cd "$HOME/gt-factory-os/scripts/sales-report"
grep -c "MCP tool returns every cell as a string" build_facts.py      # expect 1
grep -c "tzinfo is not None" build_report.py                          # expect 1
grep -c "GT_RANGE_END" analyze_bridge.py                              # expect >=1
ls -l bulk_query.graphql                                              # the pull query

# 2. the price map is where build_facts.py expects it
ls -l "$HOME/gt-factory-os-production-brain/docs/pricing/2026-08-05_shopify_products_exvat.tsv"

# 3. the window this run will use (END = current month, Israel time)
TZ=Asia/Jerusalem date +%Y-%m
```

Any of the greps returning `0`, or a missing `bulk_query.graphql`, means you are on a
checkout that predates the fixes: landmines 1–3 are live and will crash or silently
mislead you. Halt and tell Tom the branch is stale rather than patching around it in a
scheduled run.

**Where the run happens:** copy the scripts into the session's scratchpad directory and
work there — `<scratchpad>/sr/`, with `raw/` and `out/` beneath it. Never run them inside
the clone: `raw/orders.jsonl` and `out/*.json` are untracked build output, and leaving
them in `gt-factory-os/scripts/sales-report/` fails D8 and risks committing 18 MB of
customer order data.

## 3. What the hard part actually is

- **It looks like report generation. It is a reconciliation.** The deliverable is not a
  page of numbers; it is the claim that these numbers can be defended against Shopify's
  own aggregates. That is why a failed gate cancels publication instead of degrading it.
- **The eight-minute wait is where scheduled sessions lie.** A bulk operation is
  asynchronous. There is a strong pull to report progress you have not observed. Poll
  `currentBulkOperation` until `status` is literally `COMPLETED`; `RUNNING` with a
  rising `objectCount` is not "nearly done", and `objectCount: 0` for the first two
  minutes is normal, not a stall.
- **The most dangerous output is a plausible one.** Every gate in this pipeline exists
  because a wrong number that looks right survives a Wednesday meeting and becomes a
  decision. The forbidden ShopifyQL columns (§1.1) are the canonical example: they are
  right there in the same response, they look authoritative, and they are wrong by
  `17/117`.

## 4. Workstreams

Each cites the `SKILL.md` step it executes. Do not re-derive the steps from here.

### W1 — Pull (`SKILL.md` steps 1–3)
Window END = current month in Israel time. Run the bulk operation using
`gt-factory-os/scripts/sales-report/bulk_query.graphql` — the exact field set the scripts
read — with its `created_at` updated to the first day of END−24 months minus one day.
Poll to `COMPLETED`, download the JSONL to `<workdir>/raw/orders.jsonl`. Record `completedAt`
and convert it to Israel time — that is the freshness stamp for everything downstream.
Pull the ShopifyQL monthly anchor into `shopifyql_month.json` beside it.
**Acceptance:** D2's inputs exist; the stamp is written down.

### W2 — Build (`SKILL.md` step 4)
Copy the scripts to the workdir, then `build_facts.py`, then `build_report.py`, both
with `GT_RANGE_END`, the second also with `GT_PULLED_AT` set to the bulk `completedAt`.
**Acceptance:** `report.html` exists and its header line carries today's date and the
pull time in Israel time.

### W3 — Gate (`SKILL.md` step 5, `recipes/sales-report.md` §five gates)
Run `analyze_bridge.py` and read its final `FULL WINDOW … PASS/FAIL` block. Read
`gate2`, `gate3` from `out/gates.json`. Re-pull the three `gate5_sample` orders live and
compare line by line.
**Acceptance:** D2, D3, D4, D5 all green — or the failure path in §8.

### W4 — Publish (`SKILL.md` step 6)
`Artifact` publish of `report.html` **with `url` set to the fixed URL**, a short `label`
and a `note` carrying the run's gate numbers. No `favicon`.
**Acceptance:** D1.

### W5 — Email (`SKILL.md` step 7)
Hebrew, plain, no decoration, to `tom@gteveryday.com`. Subject and the four body
elements are specified in `SKILL.md` step 7 — follow it exactly. Add one line only if
an unmapped SKU cleared ₪20,000 in the latest month (`SKILL.md` step 5, non-blocking).
**Acceptance:** D6.

## 5. Scope

**IN:** everything in §4.

**OUT — do not touch, do not "improve":**

- The taxonomy, the SKU map, the chain assignments, the ₪ base, the anchor column. All
  Tom-locked; changing one silently invalidates every earlier snapshot.
- `gt-factory-os/scripts/sales-report/*` — read and run them, do not edit them mid-run.
  A script fix is a separate PR on a weekday, never inside a scheduled publish.
- Any Shopify write. The bulk operation is a read; nothing else touches the store.
- `Sales-Machine/evidence/` — weekly runs do not write snapshots. Tom asks when he wants
  one.
- The second sales artifact `9d94c4ff-7ea2-4ddc-a148-0a1781ad1c3e` (the approval gate
  page). It changes only when taxonomy changes, which is §6C.
- Any factory-os core table. `Sales-Machine/CLAUDE.md` §Hard boundaries.

## 6. Tom's part — the complete list, nothing else is his

**A. Create the Routine.** Connectors, cron and the ready-to-paste prompt are in the
appendix. Two minutes.

**B. Reconcile the cadence wording.** `SKILL.md` line 13 currently reads
`בכל רביעי בבוקר` — Wednesday. The Routine is Sunday 08:00. One of the two is wrong;
Tom says which, then the skill line gets a one-line edit. Until then, follow the
Routine's schedule and note the conflict in the run report.

**C. The 0.3-litre mapping.** Four SKUs, ₪243,000 in `2026-08`, unmapped (§2.4). Adding
them to the price map is a taxonomy change and needs Tom's written approval plus the
gate page. Until approved they stay in the visible historical bucket — which is correct,
just noisier than it needs to be.

**D. Define "what to check this week."** `SKILL.md` step 7d asks for the biggest YoY
drop **in the last full month**. Computed in the 2026-08-30 run over 2026-07 vs 2025-07,
that yields a largest drop of ₪8,400 — noise. The same run over 12 months yields
`המגדלור 17 - תל כודאדי` at −₪108,136 (₪124,264 → ₪16,128), which is decision-grade.
**Default if Tom says nothing: use the 12-month window and label it as such in the
email.**

**E. Merge both branches before the first Sunday firing** — `claude/update-sales-report-dhbejx`
in `gt-factory-os` (the script fixes and `bulk_query.graphql`) and the same branch in
`gt-factory-os-production-brain` (this document). A fired session clones the **default**
branch: until these land there, the script fixes are absent (landmines 1–3 go live) and
this file does not exist for the Routine to read. Its prompt then takes the
"file is missing" path in the appendix — an email saying nothing ran, which is the
correct failure but still a wasted Sunday.

## 7. Landmines — do not rediscover these

1. **`TypeError: unsupported operand type(s) for -: 'float' and 'str'` in `build_facts.py`
   or `build_report.py`** — the ShopifyQL MCP tool returns every cell as a *string*,
   while the 2026-08-24 hand-saved file held numbers → both scripts now coerce on load.
   On a pre-fix checkout, convert `rows` to `[date, int, float…]` before running.
2. **The page says 07:00 when the pull was at 10:00** — `build_report.py` used to format
   `GT_PULLED_AT` verbatim, so a UTC `completedAt` printed as if it were local → it now
   converts any offset-aware value to Israel time. Still pass `completedAt` verbatim;
   do not pre-convert by hand and do not strip the `Z`.
3. **The bridge silently compares the wrong months** — `analyze_bridge.py` had the window
   `2024-08 … 2026-08` hardcoded, so from September onward it would have excluded the
   newest month and still printed a confident table → it now derives the window from
   `GT_RANGE_END`. Always export that variable for all three scripts.
4. **`gate1` in `out/gates.json` is not the gate.** It compares `fact_rev` to `ql_net`,
   and `ql_net` is a forbidden column (§1.1) — it shows deltas around `+15%` on a
   perfectly healthy run. The real gate is the `FULL WINDOW … PASS/FAIL` line printed by
   `analyze_bridge.py` against `total_sales`. Reading `gate1` as the verdict fails the
   report for no reason; ignoring the bridge publishes a wrong one.
5. **Publishing without `url`** silently creates a *new* artifact. Tom's bookmark and
   every earlier email then point at a frozen page while the fresh numbers sit at a URL
   nobody has. Always pass `url`; never pass `favicon` on a republish.
6. **`sleep 60 && check` is blocked** by the Bash tool, and chaining short sleeps to get
   around it is also blocked. Use a background `sleep` and poll between wakeups. The
   bulk operation took ~8 minutes on 33,602 objects; budget 15.
7. **The three sanity orders are always the same three** — `random.seed(20260824)` is
   fixed. That is intentional and it is still a real check: re-pull them *live* every
   week. Recognising the order numbers is not evidence.
8. **`build_facts.py` hardcodes an absolute path** to the price TSV under
   `/home/user/gt-factory-os-production-brain/...`. If the clone lands elsewhere the run
   dies on a missing file — check §2.5 item 2 before blaming the data.
9. **Israel leaves DST on 2026-10-25.** A UTC cron of `0 5 * * 0` fires at 08:00 while
   IDT (UTC+3) holds and at **07:00** from 2026-11-01. Either accept the hour or move
   the cron to `0 6 * * 0` that week (§6A).
10. **`build_excel.py` will fail** with `ModuleNotFoundError: No module named 'openpyxl'`.
    It is not part of the weekly path. Do not install packages inside a scheduled run.

## 8. Halt conditions

Inherited set cited in §0. Additions specific to this work:

- **Any gate fails** → **STOP.** Do not publish. Send the short Hebrew failure email
  specified in `SKILL.md` step 8, naming the deviation and stating that the link still
  shows the previous version and its date. A stale-but-true page beats a fresh lie.
- **Bulk operation not `COMPLETED` within 30 minutes, or `errorCode` non-null** → treat
  as a gate failure: no publish, failure email, name the operation id.
- **A boot check in §2.5 fails** → **STOP**, tell Tom the pipeline moved, publish
  nothing.
- **The run would change taxonomy, thresholds, the recipient, or the artifact URL** →
  **STOP**, surface to Tom. These are §1.1 and §6 territory.
- **Two firings overlap** (a previous Sunday's session still running) → do not start a
  second bulk operation; Shopify allows one query bulk operation at a time and the new
  request will cancel or queue behind it. Report and stop.

## 9. Final report

Concise English, at the end of every firing:

1. What a stranger can now watch working, end to end.
2. Each done-condition D1–D8 ✅/❌ with its evidence pointer — no partial credit.
3. The numbers: the `FULL WINDOW` line, order match `N/N`, coverage `N/N`, sanity `N/N`,
   and the three email figures.
4. The artifacts: artifact URL and the Gmail message id.
5. What is still Tom's from §6, and what remains genuinely unfinished.
6. The single next action.

If anything is not ready, say so first and plainly. Tokens per
`gt-factory-os-production-brain/VERDICT_GLOSSARY.md`.

---

## Appendix — Routine configuration

**Connectors the fired session needs:**

| Connector | Why | Access used |
|---|---|---|
| Shopify | the bulk order pull and the ShopifyQL anchor | read only |
| Gmail | the one email to `tom@gteveryday.com` | send |

Nothing else. The `Artifact` tool is built in — it is not a connector and must not be
requested as one. No Supabase, no LionWheel, no Green Invoice: this report never touches
them.

**Schedule:** Sunday 08:00 Israel time → cron `0 5 * * 0` in UTC while IDT holds. See
landmine 9 for the 2026-10-25 DST change.

**Session mode:** a fresh session per firing. Do not bind it to an existing session —
each week must start from a clean context, and the numbers must be pulled, not
remembered.

**Routine prompt — paste this as the Routine's message:**

```
Run the GT weekly sales-report refresh.

Read and execute, in this order:
1. gt-factory-os-production-brain/docs/plans/2026-08-30-weekly-sales-report-routine-masterprompt.md
   — the standing instruction for this Routine. Follow it, including its halt conditions.
2. gt-factory-os-production-brain/.claude/skills/weekly-sales-report/SKILL.md
   — the procedure itself, steps 1-8.

If either file is missing, stop and email tom@gteveryday.com saying the report did not
run this morning and why. Do not improvise the pipeline from memory.

The artifact URL is fixed:
https://claude.ai/code/artifact/ad0dd380-d95e-4a21-94e3-af9ee386fc88
Publish to that URL or not at all. A failed correctness gate means no publish and a
short Hebrew failure email instead — never a published number you cannot defend.
```
