# My Activity Log — Design Spec

**Date:** 2026-05-13
**Owner:** Tom
**Author of spec:** brainstorming session
**Status:** awaiting Tom approval before plan
**Supersedes:** the existing `/stock/submissions` page (which becomes a redirect)

---

## Problem

The current `/stock/submissions` page shows the operator/planner their last 20 form_submissions, but the rows are generic — only `form_type`, `status`, UUID, and timestamps. Two of the rows in the most recent screenshot have no label at all (`bom_mutate`, `purchase_order_manual_create`). The page does not:

1. Tell the user **what they actually did** in any given submission.
2. Cover credit-approval actions (a separate audit channel at `private_core.credit_decisions`) — invisible today.
3. Cover Inbox exception acknowledge/resolve actions (`acknowledged_by` / `resolved_by` on `private_core.exceptions`) — also invisible today.
4. Support long-term review — capped at 20 rows, no filters, no pagination, no search.
5. Express append-only semantics — users have no signal that this is a permanent audit trail.

## Goal

Replace `/stock/submissions` with `/me/activity` — a per-user append-only activity log unifying every user-initiated action across all three audit channels, in the same UX register and pattern as the Movement Log.

A user should be able to:
- See, in one chronological feed, every action they took in the system.
- Identify a specific past action by glanceable summary (no UUIDs in the primary row, no raw `form_type` strings).
- Page back through their full history (not capped at 20).
- Filter and search to answer "did I do X last week?"
- See enough detail per row to recognize the action, then drill into a side drawer for the full payload.
- Trust that nothing here gets edited or deleted — corrections appear as new entries.

## Non-goals

- **Not** a cross-user audit view. Admins see only their own activity here; any cross-user audit is a separate flow.
- **Not** an undo / reverse surface. Strictly read-only.
- **Not** a movement-log replacement. Activity Log shows *user actions*; Movement Log shows *stock ledger events*. They link but are not redundant — one form submission may produce several ledger rows.
- **Not** consuming `change_log` directly. That table is too fine-grained (column-level triggers) and would drown the feed.
- **Not** a CSV export surface. Could be added later without schema change; out of scope for first wave.
- **Not** login / settings-change history. Could be added in a future wave.

## Architecture

### Source channels (three)

| # | Source | Per-row identity | Actor column | Event-time column | Action types |
|---|---|---|---|---|---|
| 1 | `private_core.form_submissions` | `submission_id` | `submitted_by` | `submitted_at` (event_at + posted_at also surfaced) | 23 `form_type` values (see §"Form-type catalog" below) |
| 2 | `private_core.credit_decisions` | `decision_id` | `decided_by_user_id` | `decided_at` | `approve`, `reject` (plus state transitions through `pending_gi_action` → `gi_draft_created` → `resolved`) |
| 3 | `private_core.exceptions` (acknowledge) | `exception_id` + `'ack'` | `acknowledged_by` | `acknowledged_at` | `acknowledge` |
| 3b | `private_core.exceptions` (resolve) | `exception_id` + `'res'` | `resolved_by` | `resolved_at` | `resolve` |

Rows from source 3 are emitted as two distinct virtual events per exception (one for ack, one for resolve) when both columns are populated. This preserves append-only correctness: ack and resolve are separate user moments.

### Server: unified read model `v_my_activity_log`

A read-only view (regular view, not materialized — revisit at >10K rows per user) that UNIONs the three sources into a uniform shape:

```sql
create view private_core.v_my_activity_log as
  -- form_submissions
  select
    'sub_' || submission_id::text as activity_id,
    'form_submission'              as source_kind,
    form_type                      as action_kind,
    submitted_at                   as event_at,
    status,
    submitted_by                   as actor_user_id,
    submission_id                  as source_pk,
    raw_payload,
    posted_at,
    rejection_reason
  from private_core.form_submissions

  union all

  -- credit_decisions
  select
    'dec_' || decision_id::text,
    'credit_decision',
    decision,                       -- 'approve' or 'reject'
    decided_at,
    state,                          -- 'pending_gi_action' / 'gi_draft_created' / 'resolved' / 'rejected'
    decided_by_user_id,
    decision_id,
    -- minimal payload built from the decision + related exception:
    jsonb_build_object(
      'exception_id', exception_id,
      'reason', reason,
      'state', state
    ),
    null::timestamptz,
    null::text
  from private_core.credit_decisions

  union all

  -- exceptions acknowledge
  select
    'ack_' || exception_id::text,
    'exception_acknowledge',
    category,                       -- the exception category, e.g. 'lionwheel_credit_needed'
    acknowledged_at,
    'acknowledged',
    acknowledged_by,
    exception_id,
    jsonb_build_object('title', title, 'category', category),
    null::timestamptz,
    null::text
  from private_core.exceptions
  where acknowledged_by is not null and acknowledged_at is not null

  union all

  -- exceptions resolve
  select
    'res_' || exception_id::text,
    'exception_resolve',
    category,
    resolved_at,
    'resolved',
    resolved_by,
    exception_id,
    jsonb_build_object('title', title, 'category', category, 'resolution_notes', resolution_notes),
    null::timestamptz,
    null::text
  from private_core.exceptions
  where resolved_by is not null and resolved_at is not null;
```

(Exact column shape to be finalized during writing-plans; the structure above is the contract.)

### Server: API endpoint

`GET /api/v1/queries/me/activity`

Query params:
- `cursor` (opaque) — for keyset pagination by `event_at desc, activity_id desc`. Preferred over offset for stability.
- `limit` — default 100, max 200.
- `source_kind` (optional, repeatable) — `form_submission` | `credit_decision` | `exception_acknowledge` | `exception_resolve`.
- `action_kind` (optional, repeatable) — narrow within a source (e.g. `waste_adjustment`).
- `status` (optional, repeatable).
- `from`, `to` (optional, ISO timestamps).

Response:
```ts
interface MyActivityResponse {
  rows: MyActivityRow[];
  next_cursor: string | null;
  has_more: boolean;
}

interface MyActivityRow {
  activity_id: string;            // 'sub_<uuid>' / 'dec_<uuid>' / 'ack_<uuid>' / 'res_<uuid>'
  source_kind: 'form_submission' | 'credit_decision' | 'exception_acknowledge' | 'exception_resolve';
  action_kind: string;            // form_type | 'approve' | 'reject' | exception category
  event_at: string;               // ISO; the moment the user took the action
  posted_at: string | null;       // for form_submissions only
  status: string;
  rejection_reason: string | null;
  summary: {
    headline: string;             // never null; "Waste · Tomatoes 5 kg"
    secondary: string | null;     // "Spoilage" or null
  };
  raw_payload_present: boolean;   // signals that drawer has detail to show
}
```

`summary` is **always** populated by a server-side builder per `source_kind` + `action_kind`. If no builder exists for a combination, the API:
- Returns `{ headline: '⚠ Unknown action: ' + action_kind, secondary: '(no summary builder)' }`.
- Logs a structured warning (`activity_log.missing_builder`).
- Does **not** silently fall back.

The full `raw_payload` is **not** returned in the list response — only via the drawer endpoint below (keeps list payload light).

### Server: drawer endpoint

`GET /api/v1/queries/me/activity/:activity_id`

Returns the full normalized detail of a single activity row, including:
- `summary` (same as list).
- Full `raw_payload` (pretty-formatted, with IDs resolved to names where the builder can — e.g. `item_id` → `item_name`).
- Cross-links: for `form_submission` with stock effect → list of `stock_ledger.movement_id` produced. For `credit_decision` → the related `exception_id`. For `exception_acknowledge` / `exception_resolve` → the related `exception_id` and current status.

### Server: summary builders (one per `source_kind` + `action_kind`)

Each builder lives in `api/src/activity_log/summaries/<source_kind>/<action_kind>.ts`. Single export:

```ts
export function build(
  raw_payload: unknown,
  context: SummaryContext      // db handle for name JOINs
): Promise<{ headline: string; secondary: string | null }>;
```

#### Form-submission builders (23)

| `action_kind` | headline pattern | secondary pattern |
|---|---|---|
| `goods_receipt` | `GR · {supplier_name} · {N} lines` | `PO #{po_number_short} ({total_units} units)` |
| `waste_adjustment` | `{Waste\|Adjustment} · {item_name} {qty} {unit}` | `{reason_label}` |
| `physical_count` | `Count · {item_name} {counted} {unit}` | `Variance {±delta} {unit}` |
| `production_actual_submit` | `Production · {sku_name}` | `{units} units` |
| `forecast_save` | `Forecast saved · week of {iso_week}` | `{N} SKUs touched` |
| `forecast_publish` | `Forecast published · week of {iso_week}` | `{N} SKUs published` |
| `forecast_revise` | `Forecast revised · week of {iso_week}` | `{N} SKUs changed` |
| `forecast_discard` | `Forecast discarded · week of {iso_week}` | reason or null |
| `forecast_open_draft` | `Forecast draft opened · week of {iso_week}` | null |
| `planning_run_execute` | `Planning run` | `{N} recommendations generated` |
| `planning_rec_approve` | `Approved rec · {target_label}` | `{rec_summary}` |
| `planning_rec_dismiss` | `Dismissed rec · {target_label}` | `{dismiss_reason}` |
| `planning_rec_convert_to_po` | `Converted to PO · {supplier_name}` | `{N} items` |
| `integration_sku_map_approve` | `SKU map · {external_sku}` | `→ {internal_item_name}` |
| `item_mutate` | `Item · {item_name}` | `{mutation_kind_label}` |
| `component_mutate` | `Component · {component_name}` | `{mutation_kind_label}` |
| `supplier_mutate` | `Supplier · {supplier_name}` | `{mutation_kind_label}` |
| `supplier_item_mutate` | `Supplier item · {supplier_name} · {component_name}` | `{mutation_kind_label}` |
| `planning_policy_mutate` | `Planning policy · {target_label}` | `{mutation_kind_label}` |
| `bom_mutate` | `BOM · {bom_name}` | `{mutation_kind_label}` |
| `alias_mutate` | `Alias · {alias_value}` | `→ {target_label}` |
| `purchase_order_manual_create` | `Manual PO · {supplier_name}` | `{N} items · ₪{total}` |
| `holidays_il_mutate` | `Holiday · {holiday_name} ({date})` | `{mutation_kind_label}` |

#### Credit-decision builders (2)

| `action_kind` | headline pattern | secondary pattern |
|---|---|---|
| `approve` | `Credit approved · {exception_title}` | `{state_label}` (e.g. "GI draft created", "Pending GI action") |
| `reject` | `Credit rejected · {exception_title}` | `{reason}` |

#### Exception-event builders (2)

| `source_kind` / `action_kind` | headline pattern | secondary pattern |
|---|---|---|
| `exception_acknowledge` / `<category>` | `Acknowledged · {exception_title}` | `{category_label}` |
| `exception_resolve` / `<category>` | `Resolved · {exception_title}` | `{resolution_notes}` (truncated to 80 chars) or `{category_label}` |

### Server: RBAC

- All four roles (`operator`, `planner`, `admin`, `viewer`) may read their own activity log.
- Hard filter: `actor_user_id = session.user_id`. No query parameter can widen this. Cross-user reads return 403.

### UX: page layout

Pattern reuses [`stock/movement-log/page.tsx`](../../Projects/window2-portal-sandbox/src/app/(shared)/stock/movement-log/page.tsx) — same density toggle, sticky day headers, advanced filters disclosure, search box, pagination control, side drawer.

#### Header

- **Title:** `My activity`
- **Subtitle:** `Append-only history of every action you took in the system. Permanent — corrections create new entries.`

#### List row (replaces the current generic row)

```
Waste · Tomatoes 5 kg  [POSTED]                                       1h ago
Spoilage                                                         13 May 2026
                                                                Posted just now
```

- **Headline** — from `summary.headline`. Bold body weight. Truncates with ellipsis on overflow.
- **Status badge** — same color/tone semantics as today.
- **Secondary line** — from `summary.secondary`. Small muted text. Hidden if null.
- **Right column** — relative time top, absolute time below, posted-time (if different from event-time and not null) below that.
- **UUID** — moved out of the row body. Available via:
  - Hover/tooltip on the status badge (`Click to copy submission ID`).
  - The side drawer.

#### Day-grouped sticky headers

`Today` / `Yesterday` / weekday name (within last 7 days) / `dd Mmm yyyy`. Each header includes a count of activities under it.

#### Filters (collapsed by default)

- Date range — `from` / `to` date inputs. Quick chips: Today / This week / Last 7 days / Last 30 days.
- Source kind — multi-select chips: `Forms` / `Credit decisions` / `Inbox acknowledged` / `Inbox resolved`.
- Action kind — populated based on selected source(s). E.g. when "Forms" is selected, lists all 23 form_types.
- Status — `pending` / `posted` / `rejected` / `cancelled` / `acknowledged` / `resolved` / `approved` / `gi_draft_created`.

Filters are URL-state (?from=…&source_kind=…) so a filtered view is shareable / re-openable.

#### Search

Client-side fuzzy match across `summary.headline + summary.secondary + action_kind`. Operates on the currently-loaded page (no server round-trip per keystroke).

#### Pagination

Keyset pagination. Buttons: First / Previous / Next / Last. Page indicator: `Showing 1–100 of ~5,400`. Per-page selector: 50 / 100 / 200.

#### Side drawer (click row)

Right-side drawer (matches movement-log iteration 20). Sections:
- **Header** — headline + secondary + status badge + event timestamp.
- **Summary block** — same as the list, but full text (no truncation).
- **Payload** — pretty-printed JSON with IDs resolved to names. Collapsed by default; expand to view raw.
- **Cross-links** — links to related entities (PO header, ledger movements, exception card).
- **Audit metadata** — `activity_id`, `actor_user_id` (your name), `event_at`, `posted_at` if applicable, `idempotency_key` if applicable.
- **Append-only banner** — at the bottom of the drawer: `This is a permanent audit entry. To correct, submit a new action.`

#### States

- **Loading** — skeleton matching the row structure (day headers + 8 skeleton rows).
- **Empty** — `No activity yet. When you submit a form, approve a credit, or resolve an inbox card, it will appear here.`
- **Empty with filters** — `No activity matches your filters. Try widening the date range or removing a filter.`
- **Error** — retry button + technical-details disclosure (same pattern as movement-log).

### URL change

- New canonical URL: `/me/activity`.
- `/stock/submissions` returns a 301 to `/me/activity` (preserves any deep links). Implemented in the portal-side Next.js redirect.
- Sidebar nav: `My History` row in the STOCK section moves into a new top-level section `ME` with entry `My activity`.

## Tom Tax (Small Things That Will Hurt Later)

1. **Indexes per source on actor + event-time** — required for keyset pagination to remain fast:
   - `form_submissions(submitted_by, submitted_at desc)` — likely already exists; verify.
   - `credit_decisions(decided_by_user_id, decided_at desc)` — new index required.
   - `exceptions(acknowledged_by, acknowledged_at desc) where acknowledged_by is not null` — new partial index.
   - `exceptions(resolved_by, resolved_at desc) where resolved_by is not null` — new partial index.
2. **Per-action-kind fixture test** — every builder gets a fixture of a realistic `raw_payload` + expected summary output. Schema drift on any form will break the fixture before prod.
3. **Fail-loud on missing builder** — see §"summary builders" — any unmapped `(source_kind, action_kind)` returns a visible "⚠ Unknown action" headline + structured warning log + bumped metric. No silent fallback.
4. **Names-not-IDs invariant** — CI check rejects any builder output containing a raw `*_id` pattern in `headline` or `secondary` (regex on fixture-test outputs). Aligns with the system-wide rule.
5. **Append-only enforcement** — the view is read-only. No `INSTEAD OF` trigger added. Any future "soft delete" of a credit_decision or form_submission would need to be modeled as a *new* reversal row (e.g. `credit_decision.state = 'revoked'`), not by hiding the original.
6. **PII / secrets redaction** — the drawer's "Payload" section runs `raw_payload` through a redaction pass before display. Default deny pattern: any field whose name matches `/token|secret|password|auth/i` is replaced with `[REDACTED]`. Per-action overrides allowed when a builder needs to whitelist a specific path. No raw secrets ever reach the drawer DOM.
7. **Time-travel correctness** — `event_at` always reflects the moment of action, never the current state. State changes (e.g. credit decision moves from `pending_gi_action` to `resolved`) update the `status` field on the same row; they do NOT change `event_at` and they do NOT create a new row in the activity log (the state transition is internal to the credit decision, not a new user action).
8. **Tooltip on status badge — copy UUID affordance** — non-obvious requirement: support engineers will sometimes ask "what's the submission ID for this row" and the UUID must still be one click away. Achieved via tooltip-on-hover + click-to-copy on the status badge.
9. **Performance ceiling** — `v_my_activity_log` is a regular view. At >10K rows for a single user (likely Tom himself within a year), consider:
   - Promoting to a materialized view refreshed on a trigger / cron.
   - Or splitting the query path: load the latest page from the view, page back through per-source queries with a unified cursor.
   Decision deferred to plan-time; not a blocker for v1.
10. **/me/ namespace expansion** — by introducing the `/me/` URL prefix, leave room for `/me/profile`, `/me/notifications`, etc. without re-routing. Do **not** introduce any of those in this wave.

## Open questions (to surface during plan-writing)

- **OQ-1** — Should an admin be able to *additionally* view another user's activity log via this same page (e.g. `?as_user=…`)? Current spec says no. Plan needs to confirm.
- **OQ-2** — Should there be a "system" filter that shows events the system attributed to "no actor" (e.g. integration-triggered form submissions)? Current spec says no — activity log shows user actions only.
- **OQ-3** — Should `forecast_revise` / `forecast_discard` / `forecast_open_draft` be merged into a single "Forecast drafting" row family in the action_kind filter UI? Possibly — they are minor states of the same flow. Plan to confirm with one screenshot.
- **OQ-4** — How does the drawer render `raw_payload` for the longer payloads (e.g. a GR with 30 lines)? Current spec: pretty-print, scroll within drawer. Plan to specify max-height.

## Build sequence (preview — for plan-writing)

1. Backend: indexes on credit_decisions + exceptions.
2. Backend: `v_my_activity_log` view + pgTAP test for shape + per-source row counts.
3. Backend: summary builders module (one per action_kind) + per-builder fixture tests.
4. Backend: `/api/v1/queries/me/activity` route + Zod validator + integration test.
5. Backend: `/api/v1/queries/me/activity/:activity_id` drawer route + integration test.
6. Portal: `/me/activity` page (initially behind a feature flag).
7. Portal: side drawer component.
8. Portal: filters + search + pagination.
9. Portal: `/stock/submissions` → `/me/activity` redirect.
10. Portal: sidebar nav update.
11. UX: handoff packet + screenshots at 1440×900 + 390×844.
12. Verification: dry-run with real fixtures across all 27 builder combinations + capture screenshots.

## Verdict

This spec is ready for plan-writing once Tom approves it.

---
