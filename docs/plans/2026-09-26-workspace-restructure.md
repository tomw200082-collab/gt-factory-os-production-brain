# Workspace restructure — layered plan

**Status:** APPROVED. Tom approved rounds 1 and 2 on 2026-09-26. Each layer's item list still needs his approval before anything is removed.
**Owner:** Tom. **Method:** `grill-with-docs` (grilling + domain-modeling). Glossary: `CONTEXT.md`.
**Pace:** one layer at a time, across several days. Nothing is deleted before its layer's list is approved.

## Why

Measured 2026-09-26:

- **Most skills are invisible.** Every session loads all five repos. The skill listing is 161 skills and 76,694 characters against a 30,000-character budget (`/tmp/claude-code.log`), so 103 skills reach the model as a bare name and cannot trigger on their own.
- **Repo hooks do not run in cloud sessions.** Sessions start in `/home/user` and add each repo with `--add-dir`; the repos' `settings.json` hooks are not loaded that way. A probe (`echo "git reset --hard"`) passed the brain's guard unblocked. The enforcement the CLAUDE.md files describe (`no_autowatch`, the portal tranche guard, the Stop hooks) does not exist there.
- **The self-running layer is off.** 6 of 29 Routines are enabled: three for the sales report, the monthly Excel, and two reminders. Messi, chief-of-staff day-open and day-close, the 06:30 guardian and queue-guard are disabled.
- **Dead weight in every repo.** Backend: 117 archived scripts, docs from April–May, the BOM-cluster leftovers. Brain: 74 `docs/phase8` files, 4 legacy agents whose retirement plan (Wave 6) never started, 171 `claude/*` branches. Portal: a weekly workflow that failed 8 of its last 8 runs. Seven skills are byte-identical copies across repos.
- **The business is changing.** A distributor takes over everything after order entry, and LionWheel closes. How that will work is not known yet.

## Decisions (Tom, 2026-09-26)

| # | Decision | Lands in |
|---|---|---|
| D1 | One brain. Sales-Machine folds into this repo as `sales/`, with its own nested `CLAUDE.md` that loads only when work happens there. The Sales-Machine repo is then archived read-only. | Layer 2 |
| D2 | The brain may hold skill scripts. Nothing that deploys to production lives here. | Layer 2 |
| D3 | `WORKSPACE_MAP.md` is rewritten as the single workspace map. The Workspace table in `CLAUDE.md` shrinks to a pointer. | Layer 2 |
| D4 | GT skills live in git, in the brain. The claude.ai account keeps generic skills. | Layer 1 |
| D5 | Removal is a real deletion in git. The tag on each repo is the rollback; no `archive/` folders. This replaces the archive-only rule in `.claude/agents/ops-docs-curator.md`, which Layer 1 updates. | Every layer |
| D6 | Tom uses none of the 22 custom account skills outside Claude Code. Anything unique in them merges into the brain, and all 22 leave the account. The 11 Anthropic skills (docx, pdf, pptx, xlsx, skill-creator and the rest) stay. | Layer 1 |
| D7 | The sunset boundary holds: everything after order entry, LionWheel included, is left alone until the distributor takes it over. The switch starts on 2026-10-05 (D12). | Distributor track |
| D8 | Dropped by Tom on 2026-09-26. The monthly Excel Routine stays exactly as it is and is out of this plan. The Make webhook and the draft PRs made for it were removed: backend #308 and brain #225 are closed unmerged. The dry-run findings are recorded in #308's description. | — |

### From the grilling (Tom, 2026-09-27 to 09-28, rounds 1–8)

| # | Decision | Lands in |
|---|---|---|
| D9 | The workspace has one goal: Tom's attention, bounded by reliability. The system notices, prepares and proposes. Tom decides only what really needs him, and never on a wrong number. Growth is the result, not the workspace's job. | Every layer |
| D10 | "Knows by itself" means three things, in this order. First, a morning message that carries only what needs Tom's decision that day, with stock and system-health problems inside it. Second, the weekly production and purchase plans, ready for approval. Third, the sales radar. | Layer 5 |
| D11 | Tom holds the people question for now. The order of work is: map the base, then map what each person does physically in the factory and the office, then build the skills around that. | After Layer 5 |
| D12 | The Distributor is Icedream, and the switch starts on 2026-10-05. It covers every customer except the three Direct accounts: Eli Avrahami, Unimarket and Elita. GT brings finished goods to Icedream's warehouse and keeps taking the orders. Icedream picks, delivers, invoices the customer and collects. GT sends Icedream Consolidated invoices without product lines; the product detail lives in GT's Shopify. Open: whether GT's Shopify can feed Icedream's Hashavshevet directly. | Distributor track |
| D13 | Held stock: Icedream holds GT's finished goods for GT, and they stay GT's until delivered to the customer. GT must see finished-goods stock split into Factory stock and Held stock. How to model the split is open: the locked rule allows no stock locations in v1, so Tom decides whether and how that rule changes. | Distributor track |
| D14 | The Direct accounts keep GT's driver and GT's Green Invoice invoices, as today. LionWheel stays open for now and may close later. | Distributor track |
| D15 | Aviv is not relevant, and GT does not work with him. The Distributor is Icedream only. | — |
| D16 | Tom's method for the distributor decisions: Claude frames each one (what it is, why it matters, the options, what is missing and from whom), and Tom and the team decide. The Icedream daily report is designed from GT's needs first; its format follows from them. | Distributor track |
| D17 | Orders reach Icedream as one Order email per order. It is sent automatically the moment the order enters GT's Shopify, and Icedream's bookkeepers key it in by hand. Simple first, improved later if needed. (Tom) | Distributor track |
| D18 | Icedream's Distributor fee is a percentage of GT's revenue on the orders it handles. How the Consolidated invoice nets the fee is open and simple to settle later. (Tom) | Distributor track |
| D19 | The stock split. Tom delegated this decision to Claude.<br>**The model:**<br>- The ledger stays one pool at the single site.<br>- Icedream's deliveries post the existing `FG_OUT_PICK` movement from its Delivery report.<br>- Returns, damaged goods and count differences go through the existing approval flow (`INVENTORY_MOVEMENT`, `COUNT_ADJUST`).<br>- A truck to Icedream is a Truck transfer document, not a ledger movement.<br>- Held stock = what Icedream received, minus what it delivered, minus Icedream-side corrections. Factory stock = ledger on-hand minus Held stock. Both are known at every moment, as of the last event.<br>- Orders sent to Icedream count as committed and as planning demand until the Delivery report closes them.<br>**Not needed:** a new movement type, or any change to the locked no-locations rule.<br>**Why:** about 100 places in the code assume the single site, so a second site cannot be made safe by 05.10. | Distributor track |
| D20 | The Delivery report. Tom delegated this decision to Claude, and it is now designed from professional practice and sources.<br>- **Daily:** one Excel file by 10:00, covering the previous day, with three tabs: deliveries, movements and stock.<br>- **Per truck:** a receipt within 24 hours.<br>- **Weekly:** a blind count.<br>- **On arrival:** automatic checks, an escalation rule and KPIs.<br>The details and sources are in the decision doc "סביבת החלטות: Icedream ורכש" (https://claude.ai/artifact/G7txCCbktcPXxZyzgiCUf1). | Distributor track |
| D21 | The Morning message. Tom delegated this decision to Claude.<br>- **When:** 07:30, Sunday to Thursday, pinned to Israel time so the 25.10 clock change does not move it.<br>- **How:** an email plus a phone push.<br>- **What:** at most five Decisions, the most urgent first. Each says what happened, what Claude proposes and what is needed from Tom. On a day with none, it is one line, plus what was checked and when.<br>- **Urgent items:** anything that cannot wait for the next morning is pushed the moment it happens.<br>- **Replaces:** the 06:30 check, the 07:30 day opening and the 08:00 sales-report email. The 17:00 sales brief to Tom and Dean stays. | Layer 5 |
| D22 | LionWheel after the switch. Tom delegated this decision to Claude. From the day Icedream takes the orders, LionWheel's automatic delivery creation is switched off, so Icedream orders open no tasks. A Direct-account order gets its task through LionWheel's button until that is automated, and the Morning message flags any Direct-account order without a task. | Distributor track |
| D23 | Green Invoice's automatic invoice. Tom switches it off when the orders move to Icedream, and wants GT's own replacement. It is feasible: GT's system already works with Green Invoice (it creates clients and has a documents client). The replacement covers the Direct accounts' invoices and the Consolidated invoice. Until it is built, the office issues them by hand. The design is open. (Tom) | Distributor track |
| D24 | Truck transfers to Icedream will probably run once or twice a week on a schedule, and otherwise only for an emergency shortage of a specific product. Claude frames the replenishment design. Research is in progress. (Tom) | Distributor track |
| D25 | **The operating model from now on (Tom):**<br>- Production is reported after the fact and is normally not planned ahead.<br>- Purchasing is planned from the Sales forecast. When a Production plan exists for a specific day, purchasing follows that plan for that day. The plan comes first and the forecast second, but usually there is no plan.<br>- Three skills carry the whole operation, and each must be very high quality and precise: production reporting, purchase planning (plan first, forecast otherwise), and creating the Sales forecast.<br>- **Purchase recommendations must contain no mistakes.**<br>This replaces D10's second item: the weekly production and purchase plans become purchase recommendations driven by the forecast. | Every layer |
| D26 | **The purchasing rule (Tom):**<br>- **The need:** the Sales forecast minus finished-goods stock, rounded up with a Safety buffer. Example: forecast 100, stock 50, no plan, so buy for 50 plus the buffer.<br>- **The Production plan** is the strongest source of truth. Whenever it asks for more, it wins.<br>- **Why the forecast exists:** raw materials are always on hand, so a rushed or emergency run never stalls for them. Quality therefore starts with the forecast.<br>- **Who does what:** code calculates the numbers, and a model with broad context adds judgment. The result must be reliable, safe and simple. | Every layer |
| D27 | **The correctness rule for Purchase recommendations.** Tom delegated this decision to Claude and approved it in principle. Mistakes mean shortages and money on the floor.<br>1. Every line shows its calculation: the need, minus stock, minus open purchase orders, equals what to buy. It is then rounded to the supplier's pack and minimum, with an order-by date from the lead time, and the supplier named.<br>2. No complete data, no recommendation. A missing active recipe, lead time or minimum order, or an unclear unit, arrives as a question.<br>3. A line far beyond what GT usually buys is flagged for review.<br>4. After every Production report, material use is checked against the recipe. A large gap warns that the recipe is wrong, before it harms purchasing.<br>5. A recommendation computed on stale inputs says so. Stale means production not reported or a Delivery report missing. Nothing is recommended silently on old data.<br>6. Every change to the calculation first passes a fixed set of worked examples with known answers. | Every layer |
| D28 | **Invoicing after the switch (Tom).** Icedream issues every customer invoice. GT invoices only the Direct accounts, and sends Icedream a Consolidated invoice per period. During the transition some orders may run through GT and some through Icedream. The Direct accounts are invoiced as today, when the order is placed, until we learn otherwise. | Distributor track |
| D29 | **The mindset (Tom).** Working with Icedream runs lean startup style: build, measure, learn, improve. Nothing is fixed, and the integration is designed both ways, their service into GT and GT into their service. Every distributor-track decision is a working hypothesis that names what we measure and when we review it. Claude must not treat decisions as sealed either. | Distributor track |
| D30 | The 05.10 preparation and the purchasing rebuild run in parallel. (Tom) | Distributor track, Planning |
| D31 | **The zero-doubt rule (Tom).** A fix that changes live numbers goes in only when Claude is sure it causes no other problem. With even half a percent of doubt, it stays out.<br>First use: planning counted delivered and cancelled LionWheel tasks as open orders, 53,680 units where 1,695 were open. The fix changed one condition in the two demand views and applied it the same day (backend #316, migration 0359). It went through the normal gates: CI, `rebuild_verifier() = 0` before and after, and a test that fails 6 of 9 before the fix and passes 9 of 9 after it. | Every layer |
| D32 | **The Sales forecast (Tom):** monthly per product, six months ahead, refreshed at the start of every month, and approved by Tom. Each refresh must be created as a revision of the current version: publishing retires the old version only then, and otherwise the months they share count twice. | Planning |
| D33 | **Production reporting (Tom):** within two working days of production. Many production runs since 2026-09-07 were never entered. | Planning |
| D34 | **The system's stock is wrong (Tom):** almost all of it, not even close. It gets a Stock reset. Until then no Purchase recommendation is trusted: after D31's fix, the one for ADD-ODK-STR-1L is still 391, partly to cover a stock of −80. How and when the reset happens is round 7. The tool already exists: the portal's Bulk Count page counts the whole factory area by area, blind, and sends large differences for approval. | Every layer |
| D35 | **Purchase orders (Tom):** today most purchasing runs outside the system, and the team does not yet work with the system as it should. No rule yet. | Planning |
| D36 | **Who records (Tom).**<br>- Maxim owns every stock-recording event: Production reports, goods receipts, Truck transfers, and returns, damage and tastings.<br>- Alex places supplier orders for now. His entries in the system are unreliable, so Maxim enters what arrives by hand, and the goods receipt is the record purchasing trusts. | Every layer |
| D37 | **Why recording fails, and the direction (Tom).** Claude's diagnosis holds: recording is separate from the physical work, and nobody sees when it is missing.<br>What gets built sits as close to the production floor as possible, not as a technical layer on top that nobody uses. The existing skills are good but get sharpened to GT's concrete needs, so that Maxim can do everything simply and the system supports him. | Every layer |
| D38 | **End to end, no Open ends (Tom).** An operational skill finishes its whole job in the session that starts it. For example, a photographed tax invoice or delivery note becomes a posted, checked goods receipt. Nothing is left for Tom to follow up and nothing can be missed, so the skill can be trusted.<br>Tom's pain today: he sends a document, the session stops short, the rest waits for him, and it gets lost among everything else. | Every layer |
| D39 | **The Sales forecast, revised (Tom).** Six months ahead, updated every two weeks from the data GT has. Claude first researches how the best practitioners build such a forecast, then builds it precisely: the data exists, the method is the work. Replaces D32's monthly refresh; D32's revision rule stays. | Planning |
| D40 | **Tom approves only what moved (Tom, 2026-09-28).** The first six-month Sales forecast, October 2026 to March 2027, is published on Tom's yes as version 63650953. D40 replaces D32's approval of every version.<br>- From the next run, every two weeks, a run publishes itself unless a line moves past its limit against the published version: more than 50 units and more than 15%, 25% or 40%, by the item's weight (A, B, C).<br>- A flagged line reaches Tom as a Decision. The whole draft then waits for him, and the published version stays in force.<br>- A Routine runs every Sunday at 06:50 Israel time, in this grill session, and works only when the newest version is 13 days old or more. The first real run is on 11.10. | Planning |
| D41 | **What the forecast leaves out (Tom).**<br>- The 0.3 L teas are made to order, so they stay out.<br>- The NS variants are not launching.<br>- The American line may come around December. It stays at zero until Tom confirms a date.<br>- Matcha: nothing is known, so there is no manual change. | Planning |
| D42 | **Maxim confirms, the skill posts (Tom, round 8).** Maxim confirms the quantities he counted, and the skill posts at once: stock, prices and the check. Tom sees only what needs him, as a Decision:<br>- a price that moved more than 5%;<br>- a new item;<br>- an invoice whose sums do not close.<br>This replaces goods-receipt-from-invoice's "never post before Tom approves". | Every layer |
| D43 | **Maxim's channel is WhatsApp, on the leads number (Tom).** Tom asked for a group of him, Maxim and the leads number, running the skills from what Maxim sends there. Meta does not allow it on this number: groups run only through the Groups API, which needs an Official Business Account and is not available for numbers also used in the WhatsApp Business app, as the leads number is ([Meta](https://developers.facebook.com/documentation/business-messaging/whatsapp/groups)).<br>So Claude chose a one-to-one chat between Maxim and the leads number:<br>- the chat also shows in the WhatsApp Business app on that number;<br>- confirm buttons work there, and they do not work in groups;<br>- the backend routes Maxim's and Tom's messages to the recording skills instead of lead capture.<br>**Connected 2026-09-28.** The number had been linked to the Meta Business Suite inbox, and a number joins one platform only, so Dualhook's signup refused it (error 3441034). Tom disconnected the inbox and connected it through Dualhook. It stays in WhatsApp account 259908923862980 with id 217553368116155, so the webhook now accepts that account too (`WA_WABA_ID` on Railway, backend #322). Verified: Tom's test message was logged at 20:09 UTC as `lead_captured`, and it is the first WhatsApp lead in `sales_core.lead`. | Every layer |
| D44 | **Supplier invoices to bookkeeping (Tom).** They are already forwarded before the goods receipt, so the skill does not send them. | — |
| D45 | **A line the skill does not recognize (Tom).** Nothing is held and nothing goes to Alex. What is on the document goes into stock, as long as Maxim sent it and checked it.<br>Claude's refinement, because a wrong match splits one material across two items and breaks planning:<br>- a line with one clear match maps to it;<br>- a truly new item is created from its closest sibling and shown to Tom;<br>- only when two items could both be it does Maxim choose, with one tap. | Every layer |
| D46 | **What gets built for Maxim (Tom).** The Truck transfer to Icedream is built new. Goods receipt and the Production report are sharpened to the edge: an experienced storekeeper's judgement, without a person's slips. Round 9 goes into their details. | Every layer |

D1–D3 change authority docs. `CLAUDE.md` is Tom's to write, so each edit lands as exact text for him to approve.

## Rules for every layer

1. **Rollback point first.** The ledger records each repo's `main` commit on 2026-09-26, and any deleted file comes back from it. Tags were the plan, but the session's git proxy refuses tag pushes.
2. **Reference check on current `main`, right before the PR.** An item goes only if nothing live uses it: the five repos, the enabled Routines' prompts, deployed Edge Functions, `pg_cron` jobs, GitHub workflows and Make scenarios. Other sessions merge daily (brain #222 landed while this plan was being drafted), so yesterday's check does not count.
3. **One PR per layer or sub-layer.** It lists every item removed and why. Tom approves the list, CI goes green, then it merges.
4. **Sunset items are left alone.** No fixes and no deletions until the distributor track replaces them (Q7).
5. **Stock truth is out of scope.** This plan changes no ledger, projection or migration. Anything that touches stock goes through the distributor track and its normal gates.
6. **Every layer ends with a measured gate**, recorded in the status table below.

## Layers

| # | Layer | Scope | Gate | Risk |
|---|---|---|---|---|
| 0 | Safety net and ledger | The rollback commits. One ledger file that classifies every skill, agent, command, hook, workflow, Routine, doc cluster and branch as keep, delete, merge, move or sunset, with the evidence for each. | Tom approves the ledger. | None: read-only |
| 1 | Session weight | Delete dead and duplicate skills. Retire the Wave-6 legacy agents and dead commands. Trim the longest descriptions. Apply D4. Remove the `claude-code-setup` plugin config, which never loads. Tom disconnects unused connectors. | A fresh session logs no "Skill listing over budget" warning. `harness_guard` passes. Every enabled Routine still finds its files. | Low |
| 2 | One brain and the map | D1 (about 45 files point at Sales-Machine), D2, D3. The backend `CLAUDE.md` states its real scope: customer portal, WhatsApp bot, lead pipeline. | The sales Routines run on the new paths. No live reference to an old path remains. | Medium |
| 3 | Enforcement that runs | Keep only the guards that protect something real, load them where cloud sessions read them, and delete claims of enforcement that does not exist. | The probe is blocked in a fresh session. | Medium |
| 4 | Repo hygiene | Dead docs, archived scripts, tracked build output, merged branches, failing workflows, stale copies (gt-site's `website_lead_intake`). | CI green in every repo. The broken-reference count drops. | Low to medium |
| 5 | Automation | Define "knows by itself". Replace the four morning outputs with one. Bring each Routine back to health. Handle 2026-10-25, when Israel leaves summer time and every UTC cron shifts by an hour. | Every enabled Routine has its skill on `main`, one clean run and an owner. | Medium |
| D | Distributor track | Its own grilling once the model is known. LionWheel retirement. A new source for goods leaving stock. | Its own stock-truth gates. | High |

## Sunset list (preliminary; Layer 0 confirms it)

LionWheel appears in 365 backend files (40 of them runtime), 152 brain files, 67 portal files (41 in `src`), 9 Sales-Machine files and no gt-site files.

- **Brain skills:** `daily-delivery-dispatch` and `route-print-pack` entirely. LionWheel steps inside `daily-ops-guardian`, `stock-exceptions-sweep`, `plan-production-14d`, `weekly-opening`, `messi`, `meeting-summary`, `shopify-sync` and `close-session`.
- **Backend:** the LionWheel mirror in `factory_os_jobs`, and the Railway poll that posts goods-out (`LIONWHEEL_FG_OUT_BRIDGE_ENABLED`).
- **Portal:** the pages that read the LionWheel mirror. Layer 0 lists them.

**Stock-truth warning.** Migration `0330_lionwheel_poll_railway_cron.sql` records that every `FG_OUT_PICK` row in the ledger (3,891 at the time) came through the Railway LionWheel poll. If LionWheel closes before the distributor supplies another source for that event, finished-goods stock stops going down, and the Shopify reconciler publishes stock that is no longer there.

## Built to extend (Tom, 2026-09-26)

Later, Tom will add new teams, for example a marketing team for paid and organic campaigns. That is not part of this plan, but the cleanup has to leave room for it:

- **A new team plugs in the way sales does after Layer 2:** one folder in the brain for its doctrine and knowledge, plus its skills and agents under `.claude/`. A new domain goes through `MODULE_TEMPLATE.md` and Tom's approval (`CLAUDE.md`, New modules).
- **Every skill and agent, kept or added, earns its place.** It needs one clear operational purpose for GT, one home, and a description of 300 characters or less that leads with that purpose. The listing budget is shared, so each addition costs every session.
- **Social platforms (Tom, 2026-08-29, carried over from `agent-reach`).** Never point an automated reader at a GT-owned social login. Read public pages through a reader, and use the platform's sanctioned API (Meta Graph, LinkedIn) for authenticated data. A throwaway account is allowed only when that is unavoidable.

## Open

- The distributor switch starts on 2026-10-05 (D12). The open decisions, with proposals, owners and dates, are in the decision doc (https://claude.ai/artifact/G7txCCbktcPXxZyzgiCUf1). Still open (Tom, 2026-09-27: not known yet):
  - whether orders placed before 05.10 go through GT or through Icedream;
  - when the first truck goes, and what it carries;
  - whether every customer moves at once or region by region;
  - how the Distributor fee is netted (D18);
  - which app issues the automatic Green Invoice invoice, and whether it stops for Icedream customers.
- Planning, still open (Tom, 2026-09-27, round 6):
  - who completes the supplier data (minimum order, order multiple, pack size, lead time);
  - when the full count happens (now the Stock reset, D34);
  - which day the scheduled truck goes to Icedream.
- Stock reset, still open (Tom, 2026-09-28, round 7: no answer yet): its date (Claude proposes the day before the first truck to Icedream) and who counts.
- **The forecast Routine lives in the grill session.** "Sales forecast fortnightly" (`trig_013DX5c7hn4F8BtTe8XcyjsC`) fires into this session, because Routines cannot carry connectors in this organization and a fresh session would run without Shopify and Supabase. If this session is ever archived, the Routine stops. So once the Morning message (D21) is built, it also checks the published forecast's age: a version older than 16 days becomes a Decision.
- **Not built anywhere, and 05.10 depends on them** (code, skills and Make checked 2026-09-28):
  - the Order email (D17): without it, Icedream does not get the orders;
  - the Delivery report intake (D19, D20): LionWheel stops opening tasks for Icedream orders (D22), so without it no delivery leaves GT's stock, and the storefront shows goods that are already gone.

## Status

| Layer | State | PR | Gate evidence |
|---|---|---|---|
| 0 | done: Tom approved the ledger | #226 | `docs/plans/2026-09-26-workspace-ledger.md` |
| 1 | repo side done; account cleanup waiting for Tom | brain #227, #229, #230 · Sales-Machine #33 · portal #236, #237 · gt-site #24 · backend #311 | Model-visible repo skills went from 98 to 59, and their description characters from 45,447 to 14,350. Every skill and agent description is 300 characters or less, except the three sunset skills; the 15 brain agents' went from 8,262 to 4,136 characters. No live file names a retired agent, and `ops-docs-curator` and `/docs-hygiene-check` now delete in git per D5. `harness_guard` passes. Routines: 5 of the 6 enabled find all their files on `main`. The monthly Excel one names a skill and three scripts that exist only in draft PRs brain #162 and backend #239, open since 2026-08-25, so Layer 1 did not change it; Layer 4 keeps both branches because their PRs are open. Listing now about 44.1K; about 27.3K once the 22 account skills leave. The fresh-session check for the "over budget" warning is still to do. |
| 2 | not started | | |
| 3 | not started | | |
| 4 | not started | | |
| 5 | not started | | |
| D | model known in outline (D12); switch starts 2026-10-05; grilling in progress | | |
