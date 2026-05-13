# UX Handoff Packet — /me/activity

**Spec:** `docs/superpowers/specs/2026-05-13-my-activity-log-design.md`
**Plan:** `docs/superpowers/plans/2026-05-13-my-activity-log.md`
**Date:** 2026-05-13
**Status:** Implemented — awaiting merge + deploy for live screenshots

---

## What changed

- New route `/me/activity` replaces `/stock/submissions` (redirect in place).
- Page unifies 3 audit sources: form_submissions (23 types), credit_decisions (approve/reject/acknowledge), exception ack/resolve.
- Day-grouped sticky headers, filter bar (visible by default), client-side search, keyset-paginated "Load more".
- Row click → right-side drawer with summary + payload (redacted) + cross-links + audit metadata + append-only banner.
- Sidebar: new **ME** section with "My activity" entry; old "My History" entry removed.

---

## Architecture

| Layer | Detail |
|---|---|
| DB view | `private_core.v_my_activity_log` (migration 0186) — UNION of 3 sources |
| DB indexes | `0185` — keyset pagination indexes on credit_decisions + exceptions |
| API list | `GET /api/v1/queries/me/activity` — keyset cursor, up to 200/page, 4 filters |
| API drawer | `GET /api/v1/queries/me/activity/:activity_id` — full detail + redacted payload + cross-links |
| Builders | 27 total: 23 form_submission + 2 credit_decision + 1 exception_acknowledge (_default) + 1 exception_resolve (_default) |
| Portal proxy | `/app/api/me/activity/route.ts` + `[activityId]/route.ts` |
| Portal page | `/app/(ops)/me/activity/page.tsx` — `useInfiniteQuery`, day groups, filters, drawer |

---

## Test results (pre-merge)

| Test file | Result |
|---|---|
| `db/tests/0185_activity_log_indexes.test.sql` | 6/6 PASS (live Supabase) |
| `db/tests/0186_v_my_activity_log.test.sql` | 7/7 PASS (live Supabase) |
| `api/test/activity_log_redaction.test.ts` | 3/3 PASS |
| `api/test/activity_log_builders.test.ts` | 29/29 PASS |
| `api/test/activity_log_list.test.ts` | 5/5 PASS (live DB) |
| `api/test/activity_log_drawer.test.ts` | 3/3 PASS (live DB) |
| `api/scripts/_verify_activity_log_coverage.ts` | 22/22 combos for Tom's user — exit 0 |
| Portal typecheck | PASS |

---

## Copy decisions

| Surface | Copy | Rationale |
|---|---|---|
| Page title | "My activity" | Short, neutral, English/LTR per portal_ux_standard |
| Subtitle | "Append-only history of every action you took in the system. Permanent — corrections create new entries." | Explicit semantics — no confusion about editing history |
| Drawer footer | "This is a permanent audit entry. To correct, submit a new action." | Reinforces append-only at the moment of reading a specific row |
| Empty state title | "No activity yet" | Neutral, honest |
| Empty state body | "When you submit a form, approve a credit, or resolve an Inbox card, it will appear here." | Educates on what feeds the log |

---

## Screenshots

Screenshots to be captured after feature branch is merged and deployed to production.
Paths reserved:

- `screens/ME-ACTIVITY-01/me-activity-01-1440x900.png` — default state (filters visible, no drawer)
- `screens/ME-ACTIVITY-01/me-activity-01-1440x900-with-filters.png` — Forms filter chip active
- `screens/ME-ACTIVITY-01/me-activity-01-1440x900-drawer-open.png` — drawer open on a goods_receipt row
- `screens/ME-ACTIVITY-01/me-activity-01-390x844.png` — mobile

---

## Open follow-ups

| ID | Topic | Disposition |
|---|---|---|
| OQ-1 | Admin cross-user view | Deferred — no scope in this wave |
| OQ-2 | System-attributed events (no actor) | Deferred — out of scope |
| OQ-3 | Forecast variant merge in filter UI | Defer until usage data shows confusion |
| OQ-4 | Long payload rendering in drawer | `max-h-96` scroll inside `<pre>`; revisit if truncation reports appear |

---

## Commits (feature branch `feat/my-activity-log`)

### gt-factory-os

| Hash | Description |
|---|---|
| `425ebab` | feat(db): 0185 indexes for v_my_activity_log keyset pagination |
| `0e94882` | test(db): pgTAP for 0185 activity_log indexes |
| `ce955cb` | feat(db): 0186 v_my_activity_log unified activity view |
| `bca9a67` | test(db): pgTAP for 0186 v_my_activity_log shape and read-only |
| `7440e32` | feat(api): activity_log schemas + zod query |
| `39fb9b3` | feat(api): activity_log redaction helper for secret-shaped fields |
| `0469e97` | feat(api): activity_log builder registry + fail-loud fallback |
| `5e171f8` | feat(api): activity_log stock-action builders (GR, waste, count, production) |
| `48c13a2` | feat(api): activity_log forecast builders |
| `941056e` | feat(api): activity_log planning builders |
| `2efb913` | feat(api): activity_log AMMC mutation builders (7) |
| `92d3da6` | feat(api): activity_log misc form builders (sku map, manual PO, holidays) |
| `6bb290b` | feat(api): activity_log credit-decision + exception builders |
| `931f905` | feat(api): /api/v1/queries/me/activity list endpoint with keyset pagination |
| `dcda199` | feat(api): /api/v1/queries/me/activity/:id drawer endpoint |
| `1954587` | fix(api): activity_log handlers — explicit raw row type for Date narrowing |
| `00f4019` | test(api): verify_activity_log_coverage — names-not-ids + fail-loud guard |

### window2-portal-sandbox

| Hash | Description |
|---|---|
| `bd57c53` | feat(portal): proxy routes for /me/activity list + drawer |
| `cf0dccf` | feat(portal): /me/activity page skeleton with day-grouped rows |
| `96d5adb` | feat(portal): filters + URL state + client search on /me/activity |
| `74dbd60` | feat(portal): activity drawer with payload + cross-links + audit metadata |
| `cb064d5` | feat(portal): redirect /stock/submissions → /me/activity + sidebar ME section |

---

**Owner:** Tom (review + merge)
**Handoff written:** 2026-05-13
