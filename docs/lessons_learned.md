# GT Factory OS — Lessons Learned

> **Purpose:** Non-obvious things that caused rework. Calibration data for future estimates. Only record surprises — things that were obviously true in hindsight but cost real time when they weren't known.

---

## Format

```
### [Date]: [Short title]
**What happened:** [Situation]
**Why it was surprising:** [What the naive assumption was]
**Corrective:** [What to do differently next time]
```

---

## Entries

### 2026-08-29: The remote Claude Code container cannot install packages or reuse a browser login

**What happened:** While evaluating Agent Reach (a Python CLI that gives an agent read
access to Instagram, Facebook, LinkedIn, YouTube, Reddit and the web) as a candidate tool
for the digital roadmap, two hard limits of the web/remote session surfaced only on
contact. `pip install agent-reach` was **denied by the sandbox permission classifier** — no
package installs from a remote session. And the tool's most valuable paths (Instagram,
Facebook, LinkedIn, Reddit, XiaoHongShu) route through OpenCLI reusing a **real logged-in
desktop Chrome profile**, which no container has or can have.

**Why it was surprising:** Both limits are invisible until you hit them. A tool's README,
its skill file and its install docs all read as if any agent that "can run a command line"
can use it — the phrase Agent Reach's own README uses. Nothing in the repo distinguishes
"works in any agent" from "works only on a machine a human is logged into". The result is
that a tool can be genuinely well-suited to the job and still be unusable from where the
session actually runs.

**Corrective:** Before adopting any tool that (a) installs a package, or (b) reads a
platform that requires a login, decide **where it will run** first. Remote/web sessions get
only the zero-config surface — plain web page reads (Jina Reader), YouTube transcripts,
RSS, GitHub, MCP connectors already wired to the account. Anything needing an install or a
browser session is a **local Claude Code** task on Tom's own machine, and should be scoped
that way from the start rather than discovered halfway in. Vendoring such a tool's skill
file into a repo is still worth doing — but the skill must say so at the top, or every
future session will chase commands that do not exist. (See
`.claude/skills/agent-reach/SKILL.md`, where exactly such a note was prepended, and
`.claude/skills/VENDORED.md` for the full account.)

---

### 2026-04-23: Wrong portal directory analyzed, led to incorrect Layer 0 estimate

**What happened:** An exploration agent analyzed `PRODUCTION/portal/` instead of the canonical portal at `C:/Users/tomw2/Projects/window2-portal-sandbox/`. Concluded that auth was "completely unimplemented" and portal made "zero real API calls". Layer 0 was estimated as 2-4 weeks of bridge work. Direct investigation found fully implemented auth + API proxy, 86/100 scorecard, and deployed system. Layer 0 revised to 3-5 days validation sprint.

**Why it was surprising:** There are two portal directories in the repo layout. `PRODUCTION/portal/` is an older, separate mock-only workstream. The canonical portal is a separate project in `C:/Users/tomw2/Projects/`. The memory file `reference_gt_factory_paths.md` documents this distinction, but the exploration agent didn't have access to memory and made the wrong inference from the directory structure.

**Corrective:** Before any portal audit, explicitly verify which directory is canonical by reading `PRODUCTION/docs/reference_gt_factory_paths.md` or MEMORY.md. The canonical portal is ALWAYS `C:/Users/tomw2/Projects/window2-portal-sandbox/`. `PRODUCTION/portal/` is a dead branch for W2 purposes.

---

### 2026-04-23: Railway project named "accomplished-learning" — not "gt-factory-os"

**What happened:** Railway project is named `accomplished-learning`, not the expected `gt-factory-os-api`. This caused `railway list` to appear to not contain the GT Factory OS project.

**Why it was surprising:** The Railway public domain (`gt-factory-os-api-production.up.railway.app`) and service name (`gt-factory-os-api`) both match the expected naming. The project-level name is different and was auto-generated.

**Corrective:** When using Railway CLI, always use `railway link --project [UUID]` with the actual project ID (`807cf50c-2629-445f-ae80-83a2f5abe9b0`), not the project name. The service name `gt-factory-os-api` is reliable; the project name is not.

---

### 2026-04-23: Vercel env pull cannot decrypt encrypted ("sensitive") variables

**What happened:** `vercel env pull` downloads encrypted production vars as empty strings (`""`). `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_API_BASE`, and others appeared empty in the pulled `.env` file even though they are confirmed set via `vercel env ls`.

**Why it was surprising:** The CLI pull is documented as the way to get production env vars for local dev. It works for plain-text vars (e.g., `API_BASE` was correctly pulled as the Railway URL) but silently omits values for vars created with the "Sensitive" type.

**Corrective:** Use `vercel env ls` to confirm presence; use a live portal smoke test (login, form submission) to confirm values are correct at runtime. Never rely on `vercel env pull` for sensitive vars.

---

### 2026-07-24: "New" GT initiatives are usually adoption, not construction — check built-vs-field first

**What happened:** In an owner-facing planning session (6 initiatives across INBOUND ops + OUTBOUND sales, prepared for Alex), the initiatives were first framed as things to "build." A pre-planning read of the brain showed 5 of 6 were already ~80–90% built in the *system* — factory-mapping v3 (playbook / 9 KPIs / CCI), the procurement engine + placement queue, stock-truth (ledger / projections / guardian), and the Shopify↔inventory sync. Tom stated the crux: "many of the processes exist in the system but not in reality yet." The real remaining work is field ADOPTION / behaviour-change, not engineering.

**Why it was surprising:** The instinct on a "let's improve X" brief is to estimate build effort. For GT specifically, most of the platform already exists in code; the binding constraint is field-adoption capacity (the rollout plan caps it at ≤2 new habits/person/week), not developer time. Estimating adoption items as "builds" inflates timelines and mis-frames the owner-ask — for adopt-items it is a public mandate + freeing people/time, not "approve a build."

**Corrective:** When planning GT "improvements," classify each item build-vs-adopt against `CURRENT_STATE.md` + the factory-mapping rollout docs BEFORE estimating. Price the adoption gap (change-management, habit cadence), not the code. Sequence field-adoption serially (one live change at a time, next enters only when its KPI shows traction); run pure-build "lab" work in parallel since it needs no operator behaviour change.

### 2026-08-01: Grep proves what is in the repo, not what runs in production

**What happened:** Every Shopify write path in `gt-factory-os` is gated off by frozen sentinels, yet Shopify's numbers matched our computed available-for-sale on 50 of 51 SKUs. The writer was `shopify_available_reconcile`, an Edge Function deployed straight to prod on 2026-07-24 with no source in any repo, no migration, no CI. Migration `0302` had already acted on the opposite belief — it narrowed a feature flag on the stated premise that grep found no reader. The flag had a reader, in a function grep could not see. `0302` was harmless only because that reader happens to be scheduled by no cron job.

**Why it was surprising:** "I searched the codebase and it isn't there" feels like proof of absence, and it is — for the codebase. Deployed artifacts (Edge Functions, cron jobs, dashboard-set secrets, feature-flag rows) live outside git entirely. Three of this session's refuted claims trace to the same root: reasoning about production from repo contents alone. The same session also found two env flags already set `true` in deployed secrets against `CLAUDE.md`, and a crashing job acting as the only interlock holding a second writer in shadow — neither visible from source.

**Corrective:** Before claiming a capability is absent, disabled, or unused, enumerate the deployed surface: `list_edge_functions`, `cron.job`, `feature_flags`, function secrets. Treat "empty/quiet" as unproven rather than green — `cron.job_run_details` "succeeded" means the POST fired, not that the function succeeded. Domain depth of this kind now lives in `.claude/skills/shopify-sync/SKILL.md` (loads only when the domain is touched) rather than in boot docs.

---

*Log initiated: 2026-04-23.*

---

### 2026-08-01: INNER JOIN to `items` silently hides batch-style production plans

**What happened:** Asked for next week's production schedule (2026-08-02 → 08-08), the answer returned was "only Wednesday, DETOX." The real plan had five days: DESERTEA (Sun), FRESH (Mon), NAMASTEA (Tue), DETOX (Wed), CALM (Thu). The query used `join private_core.items i on i.item_id = pp.item_id` — an INNER join. Batch-style rows in `production_plan` carry `item_id IS NULL`; their products live in the `pack_manifest` jsonb plus `base_bom_head_id`. The INNER join dropped 4 of 6 rows. The two surviving rows were legacy per-item DETOX rows, so the truncated answer looked plausible and went unchallenged. When Tom said it was wrong, the *same broken join* was re-run against a different date literal, the identical output was treated as confirmation, and the wrong answer was defended.

**Why it was surprising:** A dropped-row join failure is invisible — there is no error, no null, no warning. The result set is internally consistent and reads as a complete answer. The mixed-schema state (some plans per-item, some as batches) means the join succeeds for *just enough* rows to look like real data rather than an empty result that would have prompted a second look.

**Corrective:** (1) When answering "what exists" from a fact table, LEFT JOIN to dimensions, never INNER — and run an unjoined `COUNT(*)` first as a control total; a smaller post-join count is a bug until proven otherwise. (2) When a portal/API surface for the data exists, read its query and mirror it — the backend is the contract. For production plans that is `gt-factory-os/api/src/production-plan/handler.reads.ts` (LEFT JOIN + `pack_manifest` expansion). (3) A "you're wrong" from Tom means change the *method*, not the parameters; re-running a flawed query is not verification.

**Canonical query — production plan for a week:**
```sql
select pp.plan_date,
       coalesce(i.item_name, pp.base_bom_head_id) as what,
       (select string_agg(mi.item_name || ' x' || m.qty::int, ', ' order by m.qty desc)
          from jsonb_to_recordset(pp.pack_manifest) as m(item_id text, qty numeric)
          left join private_core.items mi on mi.item_id = m.item_id) as packs
from private_core.production_plan pp
left join private_core.items i on i.item_id = pp.item_id   -- LEFT, always
where pp.plan_date between $from and $to
  and pp.cancelled_at is null
order by pp.plan_date, pp.created_at;
```

---

### 2026-08-06: A Notion task nobody can see is worse than no task

**What happened:** Ten task rows were written into the GT tasks database with owner recorded in `בעל תפקיד` (a multi-select). Tom looked at the tracking page and reported the tasks were missing. They were not missing — every view on that page keys on `אחראי`, a **person** property: "המשימה שלי" filters `אחראי contains me`, "לפי מקבל המשימה" groups by it, and "בהמתנה" sorts by `תאריך יעד`, which the new rows also lacked. Rows with neither field are filtered out or sink below the fold. The write succeeded and the outcome still failed.

**Why it was surprising:** Every API call returned success, the rows queried back correctly by SQL, and the two fields have near-identical Hebrew meanings. Nothing in the write path signals that one of them is load-bearing for visibility and the other is decorative.

**Corrective:** After writing to any Notion database, **read the destination page's view configuration, not just the row**. A row is only delivered when it satisfies the filters and sorts of the view the human actually opens. For the GT tasks DB (`collection://c6604298-2afb-8258-8026-87e9538244c3`) every new row needs `אחראי` (person id — Tom is `323d872b-594c-81b0-b17a-00023fb025b3`), `תאריך יעד`, and `פרויקטים`; `בעל תפקיד` is labelling only. Related: that DB has **no status property** — completion is expressed solely by filling `תאריך השלמה`, so there is no "in progress" state to set.

**Second, smaller trap from the same session:** the Notion connector exposes no delete or archive call. Removing rows from a database means `notion-move-pages` to a plain page, which preserves the page and its content but **drops every database property** (wave, project, dates). Fine for junk, lossy for anything that might come back.

---

### 2026-08-18: A red GitHub Actions check does not mean production is not deploying

**What happened:** `gt-factory-os` PR #220 sat on a red `typecheck` for nine hours across three attempts, every one finishing in 2–4 seconds with `runner_id: 0`, `runner_name: ""` and no logs — no Actions runner was ever assigned (the repo is private and bills Actions minutes; the two public repos in the same workspace built fine on the same account at the same moment). The reasonable-looking inference was that nothing in that repo could ship until Actions recovered, and the proposed remedy was to make the repo public. Both were wrong. Railway deploys `gt-factory-os` from `main` through **its own GitHub integration**, entirely independent of Actions: seconds after #220 merged, `/api/v1/queries/sales/leads` went 404 → 401 on the live API. `.github/workflows/deploy-production.yml` exists but is `workflow_dispatch`-only, so it had never been on the critical path.

**Why it was surprising:** the repo contains a deploy workflow that uses a `RAILWAY_TOKEN`, which reads as "CI deploys this." It is a manual escape hatch, not the pipeline. Nothing in the workflow file says a second, automatic path exists.

**Corrective:** before concluding a red check blocks shipping, establish two things separately — (1) is the check *required* (`mergeable_state: "unstable"` means a non-required check is red and the PR is still mergeable; `"blocked"` is the one that actually gates), and (2) what actually performs the deploy. Probe the deployed artifact rather than reasoning from the workflow files: an unauthenticated request to a new route returns **404 when the code is not deployed and 401 when it is**, which distinguishes the two in one call. Cost here: nine hours of a PR treated as blocked, plus a proposal to flip a private repo public — which would have exposed the hardcoded Shopify token that same repo carries in git history (GAP-029).

**Smaller trap from the same session:** the portal CI guard fails any new `docs/portal-os/**` artifact absent from `docs/portal-os/registry.md`. Creating a tranche file without registering it burns a full CI cycle (~6 min) after every test has already passed, because the guard runs last. Register the artifact in the same commit that creates it.

---

### 2026-08-29: Two Claude Code config files that do not do what their names say

**What happened:** Installing the `claude-code-setup` plugin across the four workspace repos surfaced two config traps in one session. First, `claude plugin install --scope project` does not append its two keys to `.claude/settings.json` — it **rewrites the whole file**. Here that produced a 153-insertion / 142-deletion diff on a governed file: UTF-8 BOM dropped, every line reindented away from the PowerShell-style formatting, hooks and permissions semantically identical but textually unrecognisable. Second, `.claude/mcp.json` had never been loaded by anything. Claude Code reads `.mcp.json` at the **repo root** — 105 occurrences of that filename in the CLI binary, zero of `.claude/mcp.json` — and no root file exists in any of the four repos. GAP-014 had been open since 2026-04-23 asking whether to keep, remove or document that file, while its own `_notes` told the reader to "enable a server by removing the `disabled: true` flag", which would have changed nothing.

**Why it was surprising:** both files look like exactly what they are named. An `install` subcommand reads as additive, and a JSON file sitting beside `settings.json` under `.claude/` reads as sibling config. The install even reports success and leaves a functionally correct file — only the diff is destroyed, which matters exactly in a repo where the diff is the review.

**Corrective:** for a governed settings file, run the tool, read the diff, and if it rewrote more than it needed, **revert and apply the change by hand** — then assert the result mechanically (parse before and after, compare every pre-existing top-level key) instead of eyeballing it. For MCP: project-scoped servers belong in `.mcp.json` at the repo root; before trusting any dot-directory config, grep the CLI binary for the filename. A config file that has never been read is worse than an absent one, because it invites edits that appear to work.

---

### 2026-09-02: A 200 that means "no such account", and two claims I made without opening the thing

**What happened:** three separate errors in one session, all the same shape — an answer accepted from something adjacent to the evidence instead of the evidence.

1. **TikTok.** Checking whether the GT brand handle was taken, the probe read the HTTP status of `tiktok.com/@handle` and reported the name free. TikTok serves **`200` for handles that do not exist**, and the string `Couldn't find this account` ships inside the i18n dictionary embedded in *every* profile page — including live ones — so grepping for it matches everywhere and proves nothing. Parsing the embedded profile JSON settled it in one request: `@gteveryday` is live, ours, id `7297668950497952769`, created 2023-11-04. The brand was never free; a status code had been treated as an answer.
2. **A two-part question, a one-word reply.** A message asked Tom two things; he answered `2. כן. יש לוגו ריבועי`. That `כן` was the answer to part 2. It was read as closing part 1 as well, and "Tom confirmed the empty channel is his" was written into `CURRENT_STATE.md` — a sole-authority file — on that reading. His next screenshot falsified it. This is exactly the failure truth rule 3 exists to prevent: an unknown was not guessed at in the open, it was quietly closed.
3. **A file's dimensions, asserted twice, never measured.** One authority file said no square logo existed (which blocked four networks) and the setup kit said `800×800`. The PNG's IHDR header says **971×960**. Two confident claims about one file, wrong in opposite directions, from a file nobody had opened.

**Why it was surprising:** all three felt verified. A 200 looks like a check. A `כן` looks like consent. A dimension written in two documents looks corroborated — but both had copied the same guess, and agreement between two documents is not evidence, it is one source counted twice.

**Corrective:**
- For any external "is this name/handle taken" check, assert on **parsed content that identifies the entity** (an id, a creation date), never on a status code, and never on a string that could be boilerplate. Prove the negative case works by running the same probe against a handle known not to exist.
- Answer *n* questions in a message, expect *n* answers. A reply with fewer parts than the question closes only the parts it names; the rest stay `UNRESOLVED`. When one word could attach to either part, it attaches to neither.
- **Open the file.** `head -c 33 x.png | xxd` gives the real width and height in one command. Any property of an artifact that is cheap to read is never inferred, quoted from a sibling document, or carried forward from an earlier draft.
