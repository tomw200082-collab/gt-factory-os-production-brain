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
| D7 | The sunset boundary holds: everything after order entry, LionWheel included, is left alone until the distributor takes it over. When the switch happens is not known yet. | Distributor track |
| D8 | Before the Routine fires on 2026-10-01: review brain #162, backend #239 and Sales-Machine #12, bring them up to date with `main`, dry-run without the upload, and merge. If the dry run is not clean, pause the Routine instead. | Before Layer 0 |

D1–D3 change authority docs. `CLAUDE.md` is Tom's to write, so each edit lands as exact text for him to approve.

## Rules for every layer

1. **Rollback point first.** Tag `pre-restructure-2026-09-26` on each repo's `main` before the first deletion.
2. **Reference check on current `main`, right before the PR.** An item goes only if nothing live uses it: the five repos, the enabled Routines' prompts, deployed Edge Functions, `pg_cron` jobs, GitHub workflows and Make scenarios. Other sessions merge daily (brain #222 landed while this plan was being drafted), so yesterday's check does not count.
3. **One PR per layer or sub-layer.** It lists every item removed and why. Tom approves the list, CI goes green, then it merges.
4. **Sunset items are left alone.** No fixes and no deletions until the distributor track replaces them (Q7).
5. **Stock truth is out of scope.** This plan changes no ledger, projection or migration. Anything that touches stock goes through the distributor track and its normal gates.
6. **Every layer ends with a measured gate**, recorded in the status table below.

## Layers

| # | Layer | Scope | Gate | Risk |
|---|---|---|---|---|
| 0 | Safety net and ledger | The tags. One ledger file that classifies every skill, agent, command, hook, workflow, Routine, doc cluster and branch as keep, delete, merge, move or sunset, with the evidence for each. | Tom approves the ledger. | None: read-only |
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

## Open

- When the switch to the distributor happens (D7). Until it is known, LionWheel breakages get fixed only when they threaten stock truth or a customer.

## Status

| Layer | State | PR | Gate evidence |
|---|---|---|---|
| D8 | in progress | | |
| 0 | not started | | |
| 1 | not started | | |
| 2 | not started | | |
| 3 | not started | | |
| 4 | not started | | |
| 5 | not started | | |
| D | waiting for the distributor model | | |
