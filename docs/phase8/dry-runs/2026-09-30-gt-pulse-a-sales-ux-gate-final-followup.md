# GT Pulse Unit A — final branch UX gate follow-up

**Observed 2026-09-30 UTC. Verdict: HOLD.** This is a five-lens equivalent self-audit of synthetic rendered sales routes, following the [first gate](2026-09-30-gt-pulse-a-sales-ux-gate.md). The native multi-auditor dispatch and connected staging session were unavailable. This report makes no production release signal.

**Exact code:** backend `42b560422cd327533135333b12390994a39304c9`; portal `a2e1786c33fc8b257240d7076113222ec8a80028`. The latter has a Vercel READY **preview**, `dpl_HYaZsiPk27eBJYMjyh3jv3q5nrn4` (`target=null`), not a production deployment. The backend exact-SHA branch CI run `36688872012` passed both jobs on disposable PostgreSQL: 0362 pgTAP 79/79, two-connection lead/wake DB tests 19/19, role/activity API 11/11, legacy workspace 14/14, staff alert 38/38, plus migration/backfill script and root typecheck. No customer-facing send was exercised.

## Five lenses and second look

| Lens | Final rendered and interaction evidence | Remaining limit |
|---|---|---|
| Flow | Today task call now carries its source task ID into the atomic activity request. Leads and Attention retain owed outcomes; three entrypoints use activity for answered and quick results. Mocked Chromium sales tests 58/58. | Authenticated staff-email login through a connected API and database is unproved. |
| Interaction | Outcome sheet makes the Leads background inert and `aria-hidden`; keyboard focus and dismissed intent were exercised. Short viewport save cases passed. | Real iOS/WebKit with keyboard open is unproved. |
| Visual | Fresh 40-route/role/width matrix: two roles × five routes × 320/390/430/1440px. Zero horizontal overflow, zero missing headings. Light/dark and reduced-motion mocked cases passed. | Fixtures are synthetic; no connected production state was rendered. |
| Content/state | Source-linked task title and reason, no false conversion from a draft, unowned rep state, missing deep-link state, error/draft recovery, and channel-neutral “תוצאת קשר” inspected. The original exact Hebrew register table has contextual assent; later exact entries, listed in portal tranche 185, await separate register assent. | New copy cannot be treated as production-approved. |
| Accessibility | RTL labels, focus trap, live regions, 44px touch checks and Leads inert background have automated coverage; mocked browser asserted the `inert` transition. | True assistive-tech and WebKit keyboard proof absent. |

The synthetic corridor has **zero verified open P0/P1** after repair. Independent backend and portal whole-branch reviewers rechecked the final diffs; no Important or Critical code finding remained. `/simplify` was unavailable; an explicit ponytail pass removed the redundant `atNineAM` wrapper in the portal while keeping `israelNineAMAfter` and DST behavior. Backend locks, request identity, audit history and wake stop conditions were retained. Focused helper/sheet/labels checks: 41/41.

The original before/after evidence remains [Today before](gt-pulse-a-ux/today-before.png) and [Today after](gt-pulse-a-ux/today-after.png), plus [settings before](gt-pulse-a-ux/settings-before.png) and [settings after](gt-pulse-a-ux/settings-after.png). Fresh redacted synthetic images: [rep Today mobile](gt-pulse-a-ux-final/after-today-sales_rep-390.png), [rep Leads mobile](gt-pulse-a-ux-final/after-leads-sales_rep-390.png), [planner Attention desktop](gt-pulse-a-ux-final/after-attention-planner-1440.png), and [40-cell matrix](gt-pulse-a-ux-final/matrix.json). The fixture deliberately cannot prove real ownership or login.

**Governor verdict: HOLD / BLOCKED for release.** R4 requires connected rep/manager auth → browser → API → committed DB transitions and a true keyboard/WebKit pass. The Vercel preview, mock browser and disposable DB each prove a different seam; they do not combine into one connected proof. No production merge, migration, flag switch, backfill or customer outreach is authorized by this report.