# GT Pulse Unit A — sales UX release gate

**UTC:** 2026-09-30. **Method:** equivalent five-lens, read-only audit by the Native coding agent; `/ux-release-gate` agent dispatch is unavailable in this harness. This is not an independent five-agent verdict. Portal local head `3c8f987953e827b7a7ce3e86eea373017eab6d23`, remote tree-equivalent head `103354bdce2e93cc4b19232dadc46745640d3ffb`; backend local head `c50e59195dbd8922a80f4ce93e129550e64bf759`, remote tree-equivalent head `fa9c0454dd0856594678448c750fa22b09e58f29`. Neither is deployed.

## Scope and evidence limit

Hebrew RTL internal B2B sales: `/sales/today`, `/sales/leads`, `/sales/attention`, `/sales/orgs`, `/sales/settings`, the staff-email deep link and result sheet. Sales rep and planner/admin; 320, 390, 430 and 1440px; light/dark, reduced motion, keyboard and short viewport. Dev-shim browser with **synthetic, redacted fixtures**; 40 route×role×width renders before and after remediation, zero horizontal overflows in the second look. On the final portal head, **57/57** relevant sales Chromium cases, **1,517/1,517** unit tests, typecheck, build and lint (558 warnings, zero errors) passed. The deep-link case includes A→close→A→close→B. Screenshots: `gt-pulse-a-ux/`; no customer data. Backend [push CI 36676625217](https://github.com/tomw200082-collab/gt-factory-os/actions/runs/36676625217) passed disposable-Postgres SQL/API/race tests on the exact final tree. A **single connected browser → API → DB** staging proof and authenticated email login are unavailable. This gap blocks a production-grade UX verdict regardless of fixture pass.

## First pass: ranked findings

| # | Severity×effort | Lens | Route | Verified finding | Evidence | Remedy |
|---|---|---|---|---|---|---|
| 1 | P1/S | Flow, interaction, truth | Today | Email-only lead offered two unusable phone actions; contactless lead had the same dead end. | `sales-today-admin-mobile.png`; `TodayCard.tsx` before `81973d1`; failing `today-queue.test.tsx` (2/26). | Email-only primary `mailto:` arms an email intent; contactless opens its lead; no impossible call. |
| 2 | P1/S | Permission, copy | Settings | Sales rep could edit shared settings in the UI and `handlePutSettings` accepted a generic sales capability. | `sales-settings-rep-before-mobile.png`; `api/src/sales/mutations_handler.ts:346` before `ef0c4d7`; failing backend AuthError and browser tests. | Reject rep with HTTP 403, hide settings navigation and show Hebrew manager-only explanation on direct route. |
| 3 | P2/S | Content | Today task card | The server currently sets `reason=title`, so the task can repeat its title after “למה עכשיו”. | `api/src/sales/queries_handler.ts:140`; `TaskCard.tsx`. | Keep scoped as a small source-reason improvement; do not invent event attribution without the actual source payload. |

The independent whole-branch code review then found four Important backend defects (duplicate first-contact task, legacy cross-owner mutations, retry after reassignment, past waiting review) and three Important portal defects (channel-invalid quick actions, future review in Today, stale same-route lead query). Each was corrected in its owning repo; a second read-only reviewer pass found one nested-transaction backend edge and one same-lead reopen edge. The final backend reviewer recheck exposed same-display-name request takeover; its regression failed on the old SQL and passed after binding replay to account identity. The final backend tree passed isolated database CI; connected staging behavior remains unproven.

No visually inferred order conversion, inbound reply or customer health was accepted as fact. `LeadJourneyRail` requires a committed named event and opens its event source; the draft order test must not light conversion. The first pass had **0 verified P0, 2 verified P1, 1 P2**. The two P1s have failing reproductions and green focused checks; they are not dismissed on mock evidence alone.

## Five-lens assessment

| Lens | First pass | Remediation / evidence |
|---|---|---|
| Flow | P1 email-only dead end | Today email/contactless paths tested; Today, Leads and Attention use `/activity` for answered and quick results. |
| Interaction | P1 inaccessible action | 320/390/430 overflow and short-viewport Save checks; same result sheet in three entrypoints. |
| Visual | No verified P0/P1 | RTL render matrix, evidence rail and mobile screenshots; status colours name recorded facts. |
| Content and states | P1 shared-settings implication; P2 repeated reason | Rep sees manager-only status; duplicate `reason=title` is hidden rather than pretending to know a cause; server error preserves draft; empty/error paths inspected. Exact new Hebrew register entry remains unapproved. |
| Accessibility | No verified P0/P1 | Focus trap, labelled controls, reduced motion and named source button covered by browser/unit checks; true iOS keyboard/WebKit remains unproven. |

## Second look and governor verdict

The second self-audit inspected 40 route×role×width renders, light/dark and reduced-motion cases, the three answered entrypoints, manager contact-gap and rep ownership, and the source-linked rail. **0 verified open P0/P1 in the synthetic Unit A corridor after remediation; release verdict HOLD / BLOCKED.** The threshold also requires authenticated staging browser → API → DB, exact deployed SHA/flag/migration proof, real WebKit keyboard and Tom's exact Hebrew register approval. These are absent. A synthetic screenshot or old tranche 171/172 verdict cannot clear these gates. The gate report itself authorizes no code edit, merge, deployment or customer send.

Redacted synthetic render artifacts: [Today before](gt-pulse-a-ux/today-before.png) → [Today after](gt-pulse-a-ux/today-after.png); [rep settings before](gt-pulse-a-ux/settings-before.png) → [rep settings after](gt-pulse-a-ux/settings-after.png). The [before](gt-pulse-a-ux/matrix-before.json) and [after](gt-pulse-a-ux/matrix-after.json) matrices contain only synthetic role, route, width and layout counts. No customer records are included.
