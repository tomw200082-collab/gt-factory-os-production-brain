# Status, Empty, and Error States — GT Factory OS Portal

**Owner agent:** `interaction-design-specialist`, `ux-content-state-designer`
**Authoritative status:** DRAFT. Extends portal_ux_standard.md §3 (state hygiene).
**Update rule:** Additions by either owner agent; Tom authorization to lock.
**Release-gate relevance:** P0 — any violation of one-primary-state-at-a-time blocks ship.

---

## What belongs here

- State machine rules for every portal surface.
- Copy templates for empty, error, and success states.
- Status term registry (operator-facing names for system states).

## What must never go here

- Backend enum values (those belong in gt-factory-os/docs/contracts/).
- Raw error codes or HTTP status codes.
- Visual token values (→ DESIGN_SYSTEM_RULES.md).

---

## One-primary-state rule (from portal_ux_standard.md §3)

A surface must show **exactly one** primary state at any time:

| State | Trigger | Required behavior |
|-------|---------|-------------------|
| Loading | Request in flight, no prior data | Skeleton blocks. NO counts, chips, or "0 X" messages. |
| Error | Request failed, no usable data | One inline error block. NO data rendering. |
| Empty | Request succeeded, zero rows | One empty-state message + primary CTA(s). |
| Loaded | Request succeeded, rows present | The data view. |

**Chips and count badges** are ONLY shown when `query.data !== undefined && !query.isError`.
Showing a chip during loading or error is always a defect.

---

## Empty state pattern

```
[Icon or illustration — optional]

No [things] yet for this [scope].
[Secondary context — when they'll appear, or why they're not here yet.]

[Primary CTA button]  [Secondary CTA button — optional]
```

Examples:
- "No goods receipts yet for this PO. You can record a receipt when goods arrive."
- "No planning blockers found. Your planning run is clear to proceed."
- "No purchase orders in the last 30 days."

---

## Error state pattern

```
[Error icon]

[Short plain-English description of what failed.]
[Actionable next step for the operator.]

[Retry button — if retry is possible]  [Contact support / planner link — if not]
```

Examples:
- "Couldn't load goods receipts. Try refreshing. If the problem persists, contact your planner."
- "Couldn't save this plan. The plan may have been modified by another user. Reload to see the latest version."

**Never show:** raw HTTP status codes, API path fragments, JSON error bodies, stack traces.

---

## Post-action success state pattern

```
[Success icon]

[What was saved/posted/published + the specific record name.]
[What the effect is, if non-obvious.]
[Next step pointer.]
```

Examples:
- "Goods receipt saved. 24 units of Detox 1L posted to stock. View receipt history ↗"
- "Plan cancelled. Detox 1L — May 8 is now marked as Cancelled. No stock movement was recorded."
- "Forecast published for May 2026. Planners can now run planning against this version."

---

## Inline mutation error pattern (alongside loaded data)

```
[Warning icon inline with the action area]

[Specific error: what failed, what the operator should do.]
```

Example (inside a form after submit failure):
- "Couldn't submit this waste adjustment. The item Detox 1L is in a count freeze. Try again after the count is complete."

---

## Status term registry (operator-facing display names)

All status values that appear in operator-facing UI must use these exact terms.
Do not use raw backend enum values.

| Context | Backend status / state | Operator-facing display |
|---------|----------------------|------------------------|
| Production plan | `PLANNED` | Planned |
| Production plan | `COMPLETED` | Completed |
| Production plan | `CANCELLED` | Cancelled |
| Production plan | `BLOCKED` | Blocked |
| Production plan | `AT_RISK` | At Risk |
| PO | `OPEN` | Open |
| PO | `CLOSED` | Closed |
| PO | `CANCELLED` | Cancelled |
| Goods receipt | (no terminal status) | — |
| Count | `pending` | Pending approval |
| Count | `approved` | Approved |
| Count | `rejected` | Rejected |
| Count | `cancelled` | Cancelled |
| Exception | `open` | Open |
| Exception | `acknowledged` | Acknowledged |
| Exception | `resolved` | Resolved |
| Forecast | published | Published |
| Forecast | draft | Draft |
| Planning run | completed | Completed |
| Planning run | in_progress | Running |

**Update rule:** Add new status terms here when a new RUNTIME_READY signal lands and the
surface uses status-term display. Coordinate with `ux-content-state-designer`.

---

## Loading skeleton rules

- Skeletons must match the final layout dimensions (column count, row height).
- Skeletons must animate (pulse or shimmer) to signal "data is coming."
- Skeletons must NOT be replaced by "0 items" or an empty state while still loading.
- Skeleton duration: if data takes >3s on a slow connection, add a "Still loading..." message.
