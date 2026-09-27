# /site-gate

Run the render-grade UX and brand gate on the GT brand site (the Shopify theme generated from
`gt-site`) and produce a formal SHIP / CONDITIONAL_SHIP / HOLD verdict.

## Purpose

The brand-site counterpart of `/ux-release-gate` (operations portal) and of the customer-portal
brief (ordering portal): the same five UX agents, a different brief, and two brand dimensions the
five do not own — conversion with performance, and voice with persuasion. One ranked report, one
verdict, zero P0 before SHIP.

`gt-site/docs/SITE_GATE_BRIEF.md` is the contract. It overrides the agent definitions for this
surface (persona, rules that do not apply, what is settled, the visitor tasks, severity, output).
This command only drives it.

## Usage

```
/site-gate                              # the live site
/site-gate --preview <theme_id>         # an unpublished theme copy (PUBLISH.md names the staged one)
/site-gate --scope home|landing|entry|form
/site-gate --dimension FLOW|INTER|VIS|COPY|A11Y|CRO|BRAND   # one dimension only
```

## Step 0 — read

1. `gt-site/docs/SITE_GATE_BRIEF.md`, in full.
2. `gt-site/PUBLISH.md`, the header table: which theme is live, which is staged. Record both ids
   and the `gt-site` tip (`git -C gt-site rev-parse --short HEAD`) in the report header.
3. The brain skill `shopify-theme` when a finding may touch Liquid, assets or RTL.

## Step 1 — evidence (regenerated every run, never committed)

```
UX_OUT=<scratchpad>/gate node gt-site/tools/site_shots.mjs
UX_OUT=<scratchpad>/gate node gt-factory-os/api/scripts/site_ipad_shots.mjs
```

`--preview <id>` sets `SITE_URL=https://gteveryday.com/?preview_theme_id=<id>` on both. Then check:
`$UX_OUT/site/facts.json` and `$UX_OUT/site-ipad/site_ipad_facts.json` exist; no viewport carries
`FAILED` (a Cloudflare challenge: re-run that width alone with `SITE_VPS=<vp>`, facts merge); count
the shots. State the counts and the `takenAt` stamp in the report. The harness never creates a
lead: the form's POST is intercepted in the browser.

## Step 2 — dispatch (parallel, read-only)

Every prompt = the common head below, then its dimension line. Seven dispatches:

| Dimension | Dispatch | ID prefix |
|---|---|---|
| Flow | `ux-flow-architect` | `FLOW-` |
| Interaction | `interaction-design-specialist` | `INTER-` |
| Visual | `visual-system-designer` | `VIS-` |
| Copy and state language | `ux-content-state-designer` | `COPY-` |
| Accessibility | `accessibility-usability-auditor` | `A11Y-` |
| Conversion and performance | `general-purpose`, skills `page-cro` + `landing-page`; `facts.perf` is its | `CRO-` |
| Brand voice and persuasion | `general-purpose`, skills `ogilvy` + `copywriting`; every Hebrew proposal `copy: needs Tom` | `BRAND-` |

The five agents' frontmatter pins an older model. Pass the Agent tool's `model` override at the
highest tier it offers on each of the five, and drop the override once the pin is removed
(workspace ledger, Layer 4). If an agent is not registered in the session, dispatch
`general-purpose` with that agent file's full text read first.

Common head (fill `{AGENT}`, `{PREFIX}`, `{UX_OUT}`, `{SCOPE}`):

```
You are running as `{AGENT}` in /site-gate, the release gate for GT's BRAND SITE: gteveryday.com,
Hebrew, RTL, a Shopify theme generated from the gt-site repo. Scope this run: {SCOPE}.

STEP 1: read /home/user/gt-site/docs/SITE_GATE_BRIEF.md in full. §3 lists the parts of your
definition that do not apply here; §4 the constraints on a fix; §5 what is settled and must not be
re-opened; §7 the visitor tasks; §8 severity; §9 the output shape.
STEP 2: the evidence is under {UX_OUT}: site/shots/*.png, site/facts.json, site-ipad/*.png,
site-ipad/site_ipad_facts.json. Open the images (Read renders PNG). The source is /home/user/gt-site:
README.md first — generated files are never hand-edited, and a fix is named in generator terms.

OUTPUT: exactly BRIEF §9, ID prefix {PREFIX}, severity × effort, an exact fix, and evidence as a
shot path, a fact key or file:line for every row. Mark `(settled — Tom)`, `(parked)`,
`copy: needs Tom` and `ARCH_REQUIRED` as §8 says. Exhaustive and concrete; no padding.
Read-only: do not edit, create or delete any file anywhere.
```

## Step 3 — consolidate

One report, not seven:

- One root cause = one row, under the dimension that owns the rule; the other IDs go in the
  evidence cell.
- `(settled — Tom)` rows go to their own short list, unranked. Nothing else is dropped.
- Rank by severity, then ascending effort. The Top-N table is the deliverable; the seven reports
  are the audit trail beneath it.
- `ARCH_REQUIRED` rows are listed apart, each with the endpoint, app or data it needs.
- `factory-os-governor` reads the ranked table and issues the verdict.

## Required outputs

```
## Site gate — <date>, gt-site <tip>, theme <id> (<live|preview>)

### Evidence
<shots count · facts takenAt · widths with FAILED (none expected) · axe availability · perf summary>

### Top-N ranked actions (the deliverable — one list, all dimensions)
| # | Sev | Effort | Dimension | Surface | Finding | Proposed fix (generator terms) | Evidence |
|---|-----|--------|-----------|---------|---------|--------------------------------|----------|

### P0 findings — block ship if any present
| ID | Dimension | Surface | Description |

### P1 findings — conditional ship items
| ID | Dimension | Surface | Description |

### ARCH_REQUIRED
| ID | Needs | Owner lane |

### Visitor tasks T1–T9
| Task | Result | Where it breaks |

### Per-dimension status
| Dimension | P0 | P1 | Status |
| Flow | | | GREEN / AMBER / RED |
| Interaction | | | |
| Visual | | | |
| Copy | | | |
| Accessibility | | | |
| Conversion + performance | | | |
| Brand | | | |

### Settled items seen (not ranked)

### Verdict
SHIP | CONDITIONAL_SHIP | HOLD

### Conditions (if CONDITIONAL_SHIP) / Blockers (if HOLD)

### Tom approval required?
yes / no — reason (Hebrew copy, a switch, a design decision)

### Next action for Tom
<one concrete step>
```

**Verdict thresholds:** `SHIP` — zero P0 across all seven dimensions · `CONDITIONAL_SHIP` — zero
P0, P1 items named for the next pass, Tom approval · `HOLD` — any P0.

## Write policy

**Read-only** on `gt-site` source, `theme/`, the store and its themes. The report is the final
message. Save a record only when Tom asks: `gt-site/docs/gates/<YYYY-MM-DD>-site-gate.md`, on a
branch, by pull request. Evidence stays in the scratchpad.

## Stop conditions

- The harness cannot reach the site at any width (a challenge on all of them) → `BLOCKED`. Name
  the widths. Never audit from code alone.
- A P0 on money or a claim — a figure disagreeing with `data/drinks_final_figures.json`, a ₪ figure
  on a served page while `show_prices` is false → `HOLD` immediately; name the figure and the shot.
- Anything that would upload, duplicate or publish a theme → stop. `PUBLISH.md` §7: publishing is
  Tom's alone.
- Seven reports that disagree on a fact (a figure, a width, a string) → resolve against the facts
  file before ranking; if it cannot be resolved, say so in the report.

## Not usable for

- Editing `gt-site` source or theme files, uploading or publishing a theme, changing a figure of
  record, flipping `show_prices` / `show_pricing` / `show_portal_entry`.
- The operations portal — `/ux-release-gate`. The customer ordering portal — its brief under
  `gt-factory-os/docs/superpowers/plans/2026-09-25-customer-portal-ux-gate/`.
- Fixing findings. Fixes go through a `gt-site` PR whose CI (`build.yml`) is the mechanical gate.

## Relationship to the other gates

`/ux-release-gate` gates the operations portal · the 2026-09-25 brief gates the ordering portal ·
`/site-gate` gates the brand site. Same five agents, three briefs, one output shape. A SHIP here
says nothing about the other two.
