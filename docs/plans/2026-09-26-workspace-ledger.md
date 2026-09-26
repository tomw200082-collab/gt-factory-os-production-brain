# Workspace ledger — what stays, what goes

**For:** `docs/plans/2026-09-26-workspace-restructure.md`, Layer 0.
**Status:** DRAFT. Layer 1 below is itemized and waits for Tom's approval. Layers 2–5 are listed as rules and counts; each is itemized when its layer starts.

**Evidence.** The inventory taken on 2026-09-26 covers every `SKILL.md`, agent and command in the five repos and in the claude.ai account. For each it records:
- description size, file count and last commit;
- references from outside any skill folder: docs, `CLAUDE.md`, agents, commands, scripts and the enabled Routines' prompts.

**Caveat.** There is no usage telemetry. A skill fires from its description and leaves no trace in files, so "no references" means nothing in the workspace depends on it. It does not mean nobody used it. Where that matters, the row says so.

**Rollback point.** This is `main` of each repo on 2026-09-26:
- backend `91a59cb`
- brain `532c151`
- portal `db43c40`
- Sales-Machine `ca1eed5`
- gt-site `2472e16`

Any deleted file comes back with `git checkout <sha> -- <path>`. The plan called for tags, but the session's git proxy refuses tag pushes.

## Layer 1 — session weight

**Goal.** Today every session's skill listing is 161 entries and 76,694 characters against a 30,000-character budget, so 103 entries reach the model as a bare name. After this layer it is about 28,900 characters, and every description is visible again.

### Delete — 61 skills

| Group | Skills | Why |
|---|---|---|
| Sales-Machine, Google APIs (10) | `data-manager-api-audience-ingestion`, `data-manager-api-event-ingestion`, `data-manager-api-setup`, `finding-google-skills`, `google-ads-api-account-diagnostics`, `google-ads-api-mcp-setup`, `google-ads-api-quickstart`, `google-analytics-admin-api-basics`, `google-analytics-data-api-basics`, `retrieving-developer-knowledge` | No credentials exist in the workspace, and nothing outside the skills references them. Upstream (`google/skills`) is public if they are ever needed. |
| Sales-Machine, byte-identical copies of brain skills (5) | `agent-reach`, `copy-editing`, `copywriting`, `ogilvy`, `stop-slop` | The brain keeps one copy; `agent-reach` goes entirely (below). |
| Sales-Machine, marketing methods nothing uses (7) | `analytics-tracking`, `competitor-alternatives`, `content-strategy`, `programmatic-seo`, `schema-markup`, `seo-audit`, `gt-marketing-playbook` | Nothing outside the skills references them. `gt-marketing-playbook` routes to the copy set and needs a context file that was never written. |
| Brain, caveman and ponytail helpers (10) | `caveman-commit`, `caveman-compress`, `caveman-help`, `caveman-review`, `caveman-stats`, `cavecrew`, `ponytail-audit`, `ponytail-debt`, `ponytail-gain`, `ponytail-help` | Nothing uses them, and three cannot work: `caveman-stats` needs a hook that was never installed, `cavecrew` needs subagents that were never copied, and `caveman-compress` overwrites the file it is pointed at. `caveman` and `ponytail` themselves stay. |
| Brain, copies of skills kept elsewhere (3) | `apple-design`, `frontend-design` (the portal holds identical copies), `skill-creator` (the account holds Anthropic's copy) | One home per skill. |
| Brain, `agent-reach` (1) | `agent-reach` | Its command-line tool cannot be installed in cloud sessions, so there it is documentation, not capability. Native web fetch and search cover the public reads. Tom vendored it on 2026-08-29, so keeping it is his call. |
| Portal (2) | `canvas-design`, `vercel-react-best-practices` | Nothing outside the skills references them. `canvas-design` is 83 files and 5.4 MB of fonts, and it is listed in the portal's own `.gitignore`. |
| gt-site (1) | `ui-ux-pro-max` | Same name as the portal's copy but a different version; only one can load. The portal copy stays. |
| Account, custom (22) | see "Account" below | Decision D6. |

### Move — 2 skills

`landing-page` and `page-cro` move from Sales-Machine to the brain's `.claude/skills/`. `landing-page` is cited by 15 lead-intake and lead-response docs. `page-cro` is cited by the customer-portal UX-gate prompts of 2026-09-25.

### Keep — 72 skills

| Group | Skills |
|---|---|
| GT operations (19) | `chief-of-staff-daily`, `close-session`, `customer-setup-shopify-gi`, `daily-ops-guardian`, `drinks-pricelist`, `goods-receipt-from-invoice`, `masterprompt`, `meeting-summary`, `messi`, `plan-production-14d`, `procurement-planning`, `production-order`, `report-production`, `shopify-draft-order-from-po`, `shopify-sync`, `shopify-theme`, `stock-exceptions-sweep`, `weekly-opening`, `weekly-sales-report` |
| Sunset (2), untouched | `daily-delivery-dispatch`, `route-print-pack` |
| Method (20) | `grill-with-docs`, `grilling`, `domain-modeling`, `caveman`, `ponytail`, `ponytail-review`, and the whole superpowers set: `brainstorming`, `writing-plans`, `executing-plans`, `subagent-driven-development`, `verification-before-completion`, `test-driven-development`, `systematic-debugging`, `dispatching-parallel-agents`, `finishing-a-development-branch`, `receiving-code-review`, `requesting-code-review`, `using-git-worktrees`, `using-superpowers`, `writing-skills` |
| Copy and pages (6) | `copywriting`, `ogilvy`, `copy-editing`, `stop-slop`, `landing-page`, `page-cro` |
| Design, portal (13) | `interface-review`, `impeccable`, `frontend-design`, `apple-design`, `ui-ux-pro-max`, `web-design-guidelines`, `better-accessibility`, `better-colors`, `better-interface`, `better-layout`, `better-typography`, `better-ui`, `better-writing`. Each is cited by the customer-portal UX-gate prompts of 2026-09-25 or by portal plans. |
| gt-site (1) | `taste-skill` |
| Account, Anthropic (11) | `brand-guidelines`, `docs`, `docx`, `learn`, `mcp-builder`, `pdf`, `pptx`, `skill-creator`, `theme-factory`, `web-artifacts-builder`, `xlsx` |

`copywriting` and `ogilvy` have no references outside the skills, but Tom asked for them on 2026-08-26. They stay until he says otherwise.

**Reference check.** The superpowers set stays whole because its core skills call its helpers, and `masterprompt` calls two of them. `interface-review` stays because `better-interface` calls it; it is hidden from the listing, so it costs nothing. No kept skill depends on a deleted one. Two mentions remain, and both are harmless:
- `caveman` mentions "/caveman-compress exempt" in passing.
- `copywriting`'s transitions note points to `seo-audit`, which was never in the brain to begin with.

### Shorten — 29 descriptions, to 300 characters or less

Every trigger phrase stays. What goes is process detail, which already lives in the body. The two sunset skills keep their text.

`daily-ops-guardian` 1,270 · `shopify-draft-order-from-po` 1,042 · `close-session` 1,005 · `production-order` 990 · `weekly-opening` 961 · `ui-ux-pro-max` 914 · `chief-of-staff-daily` 906 · `report-production` 899 · `procurement-planning` 897 · `impeccable` 895 · `messi` 869 · `customer-setup-shopify-gi` 855 · `ponytail` 826 · `apple-design` 792 · `better-typography` 772 · `plan-production-14d` 757 · `stock-exceptions-sweep` 682 · `better-accessibility` 671 · `better-colors` 636 · `meeting-summary` 605 · `better-layout` 585 · `better-ui` 522 · `shopify-theme` 503 · `page-cro` 500 · `better-writing` 493 · `weekly-sales-report` 487 · `ponytail-review` 456 · `shopify-sync` 442 · `goods-receipt-from-invoice` 436

### Agents — retire the four legacy ones

The four are `executor-w1`, `executor-w2`, `executor-w4` and `governor`. Their retirement ("Wave 6") never started. Their replacements already exist: `backend-db-executor`, `portal-production-executor`, `integration-boundary-executor` and `factory-os-governor`.

The same PR updates the live references: `EXECUTION_POLICY.md:27-29` (the legacy column), `AI_BRAIN_ROUTER.md:29` and `REGISTRY.md:24-27`. Mentions in backend code comments and in archived docs are history and stay.

`verifier` stays; `docs/phase8/deprecation/ACTIVE_SURFACE_REDUCTION_PLAN.md` keeps it indefinitely. The other 19 agents stay. The portal's five auditors are decided together with the portal process in Layer 4.

### Settings

Remove the `claude-code-setup` plugin and its marketplace from the `settings.json` of the backend, brain, portal and Sales-Machine. Every session clones that marketplace for a single skill (`claude-automation-recommender`) that nothing uses.

### Account — Tom's hands, in claude.ai settings

- **Skills.** The 22 custom skills leave the account (D6). What moves into the brain first: see "Account merges" below.
- **Connectors.** Disconnect Booking.com, Expedia, Kiwi.com and Spotify, which have no GT use. Also disconnect Figma: no GT file mentions it, and if Tom designs in it, it stays. Together these add hundreds of tool names to every session. Keep the rest; Klaviyo appears in the runtime system map.

### Account merges

All 22 were read in full, and each one's key facts were checked against the brain, Sales-Machine and the backend master-data fixtures.

- **Merge 1.** `gt-recruitment-outreach` becomes a reference doc, not a skill: `docs/ceo/reference/recruitment.md`. Hiring happens far less often than the brain's bar for a skill.
  - It carries the steps and the gotchas that exist nowhere else: the job-site search queries and noise senders, decoding Windows-1255 Hebrew, and the approved outreach tone and template.
  - It also carries the rule that Alex screens drivers from the CV in the email body, and the 45-minute interview invite.
  - The dated list of open roles is dropped; both roles are filled.
  - The file is added to the shared references in `messi`.
- **Delete 21**, because nothing in them is unique:
  - `morning`, `tom-context-engine`, `gt-context-harvester`, `gt-brain-compiler`, `curate-and-improve`, `import-memory`, `gt-inbox-sorter`
  - `gt-axis-business`, `gt-axis-marketing`, `gt-axis-production`, `gt-axis-systems`
  - `gt-marketing-architect`, `gt-sheets-designer`, `gt-data-center-advisor`, `manufacturing-intelligence`, `make-master`
  - `domain-investigation`, `expert-second-opinion`, `flowchart-visualizer`, `mermaid-diagram`, `frontend-design-master`

  Several are wrong today:
  - `manufacturing-intelligence` says planning happens on Sunday and gives a 7-day lead time; the brain says Wednesday and 14 days.
  - `gt-sheets-designer` has three wrong email addresses.
  - `make-master` names Make tools that no longer exist.
- **Loose ends, fixed in the same PR.**
  - `.claude/skills/VENDORED.md:157-158` says `domain-investigation` and `gt-marketing-architect` live in the brain. They never did; the line gets corrected.
  - `docs/knowledge/gt-axis-*/registry.yaml` name `gt-context-harvester` as their only writer. Their entries already exist elsewhere, so they are deleted after a reference check.
- **Open.** `gt-axis-systems` lists BizIbox for banking, and no repo mentions it. It gets recorded with the connected systems only if Tom confirms GT still uses it.

### Gate

- A fresh session logs no "Skill listing over budget" warning.
- `harness_guard.py` passes.
- Every file named in an enabled Routine's prompt still exists.

## Layer 2 — one brain and the map (itemized at layer start)

- **Sales-Machine moves into the brain.** Its 151 tracked files go to `sales/`. Its `CLAUDE.md` becomes `sales/CLAUDE.md`, which loads only when work happens there.
- **About 46 files point at Sales-Machine and get rewritten:**
  - 25 in the brain, including the knowledge-book scripts that write into it and the recipe path in `weekly-sales-report`;
  - 16 in the backend, which cite decision IDs only (no path change);
  - 2 in the portal and 3 in gt-site.
- **Then the repo is archived read-only.** That is Tom's click in GitHub.
- **Authority docs.** `WORKSPACE_MAP.md` is rewritten, the `CLAUDE.md` Workspace table becomes a pointer, and `CLAUDE.md:28` changes per D2. Tom gets the exact text for each.
- **Backend `CLAUDE.md`** states its real scope: customer portal, WhatsApp bot and lead pipeline.

## Layer 3 — enforcement that runs (itemized at layer start)

None of these hooks runs in cloud sessions today.

| Hook | Repo | Verdict |
|---|---|---|
| `no_autowatch.sh` (PreToolUse) | backend, brain, Sales-Machine, gt-site | Keep one copy, loaded where cloud sessions read it |
| `pre_tool_use.sh` guard | brain | Replace the destructive-command rules with native `permissions.deny`; drop the rules that can never match (sandbox, portal RUNTIME_READY, W4) |
| `session_start.sh` | brain | Delete: it prints 141 KB to stderr, which never reaches the model |
| Stop, SubagentStop | brain | Delete: stderr only |
| tranche guard (PreToolUse) | portal | Decide with the portal process (Layer 4); its pointer is stuck at tranche 180 |
| SubagentStop evidence, Stop "Next action" | portal | Delete, unless the portal process stays |
| `impeccable` (PostToolUse) | portal | Keep with `impeccable`; advisory only |
| `npm install` (SessionStart) | backend, portal | Keep: tests need it when the environment is built |
| `setup-graphify.sh` | backend, brain, portal | Keep one copy |

## Layer 4 — repo hygiene (itemized at layer start)

- **Backend**
  - `scripts/archive` (117 files) and 29 one-off scripts.
  - Docs untouched since April–May: checkpoints (64), gates (33), and the integration docs for retired Shopify jobs. LionWheel docs are sunset.
  - BOM-cluster leftovers: `db/tests` 0156–0174 and `db/proposed` (18 files).
  - Tracked output: `test-results/`, `.claude/evidence`, `docs/gates/*.json`.
  - `docs/superpowers/specs/2026-09-24-portal-page`: 30 files identical to `api/src/portal/public`.
- **Brain**
  - `docs/phase8` (74 files).
  - `docs/portal-os-scaffolding` (30 files, 18 of them duplicated in the portal).
  - `archive/` (90 files); under D5, git history is the archive.
  - Stale root docs: `ACTIVE_NOW.md`, the skill count in `REGISTRY.md`, the portal score in `CURRENT_STATE.md`.
- **Portal**
  - 30 legacy docs and the June audit reports.
  - The drift and ux-gate workflows: 8 of 8 recent runs failed, and they are pinned to a brain branch from June.
  - The stuck tranche pointer.
  - 13 files that still name `window2-portal-sandbox`.
- **gt-site**
  - The stale copy of `website_lead_intake`; the backend copy is the one deployed.
  - The unused `shopify-ai-toolkit` plugin (66 files, 6.5 MB).
- **Branches.** The brain alone has 171 `claude/*` branches. In every repo, delete those whose PR is merged or closed.

## Layer 5 — automation (itemized at layer start)

- **Routines: 29.**
  - 6 enabled: the three sales-report runs, the monthly Excel, and two expiry reminders (Make on 2026-10-09, Meta on 2026-10-16). The monthly Excel stays exactly as it is (Tom, 2026-09-26).
  - 10 disabled one-shot check-ins, auto-disabled when their session ended: delete.
  - 13 switched off: messi, chief-of-staff, the guardian, queue-guard, and older sales variants. Decide which come back, as one morning output instead of four.
- **2026-10-25:** Israel leaves summer time. From then on, the enabled Routines' UTC crons fire an hour earlier by Israel time.
- **Define "knows by itself."**
