# Loose-Movement Stock-Commit (Parts B/C/D) — Design Decision Record

> **Status:** APPROVED by Tom 2026-06-14 — design locked, proceeding to the Phase-1 implementation plan.
> **Owner:** Tom · **Author:** Claude · **Touches STOCK TRUTH** (boot-kernel non-negotiable #1).
> **Full feature spec (notation, mapping, idempotency, card contract, edge cases, §R red-team corrections):**
> `~/.claude/skills/lionwheel-route-invoices/SPEC_loose_movement_delivery_note_2026-06-13.md`.
> This record locks the **build decisions + phasing + governance**; it supersedes that spec's §15 open items where they overlap.

## Goal
Make factory **exceptions** (return / exchange / sample / gift / check) detected by the `lionwheel-route-invoices` skill **actually move stock** — via a proposal **card in Tom's Inbox** that **Tom approves**, committing through `POST /api/stock-events/loose-shipment` to `stock_ledger`. **Never auto-commit.**

## Foundation already in place (verified this session)
- **Compute engine** built + unit-tested: `loose_notation` (EBNF parse), `loose_items` (resolve→item_id), `loose_movement` (legs, flags, `commit_blocked`, idempotency, same-SKU exchange-collision gate).
- **Endpoint live & ready:** `POST /api/stock-events/loose-shipment` — sole writer of `LOOSE_SHIPMENT_IN/OUT`; guards: role=admin, `confirmed_by='tom'`, delivery window `[today-7d, today+1d]`, items ACTIVE+FG; idempotency `sha256(driver_id||delivery_date||task_id||item_id)`; 201→`ledger_event_ids[]`, 409→original ids.
- **Inbox** = `private_core.exceptions`; the `credit_decisions` flow is the approve→commit precedent to mirror.

## Locked decisions (2026-06-14)

| Decision | Chosen | Rationale / rejected |
|---|---|---|
| **Sequencing** | **Phased.** Phase 1 = skill writes proposal cards to the Inbox (read-only, **no commit**) → dry-run on a real route → Phase 2 = approve→commit handler + portal → first Tom-approved live commit. | De-risks: validate the computed movements before the commit path exists. Rejected all-at-once. |
| **Who writes the card** | The **skill writes the card directly** to `exceptions` (proposal in `detail`, SELECT-before-insert dedup per §R7). | Card is a **reversible proposal, not stock**; the skill is never in the *commit* path (that's portal→endpoint). YAGNI vs a new intake endpoint. |
| **Same-SKU exchange** | **Gated** in v1 (flag `exchange_idem_collision_risk` → `commit_blocked` → manual handling). | Locked 4-input idempotency key can't disambiguate two same-SKU legs → silent half-move. The fix is a stock-events contract + governance change — defer; rare case. |
| **Portal (Part D)** | Mirror the proven **credit-decision detail page**: separate `/inbox/loose-movement/[exception_id]` via `deep_link`; **approve admin-only (Tom)**; planners view-only. | Proven precedent (§R8/R9); not the experimental typed-card inbox. |
| **Exchange `מוסר` leg kind** | `donation` for v1. | Won't 400; a dedicated `exchange_replacement_out` kind is a contract change — defer. |
| **Returns → stock** | Return = **IN to sellable** stock; reverse in the Inbox if actually waste. | YAGNI; reversal path exists. |
| **Stock safety** | Unchanged & non-negotiable: endpoint is **sole writer**, append-only, **reversal-not-edit**, **Tom approves every movement**, nothing auto-commits, same-SKU exchange gated. | Boot-kernel locked. |

## Phased build

**Phase 1 — proposal cards (zero stock risk)**
- **Part B (skill):** per non-invoice task → classify type → parse notation → resolve `item_id` → compute movement legs → write one `loose_movement_pending` card to `private_core.exceptions` (`detail` = full proposal incl. `route_dir`, `skill_version`, `task_status_at_commit`, per-leg `recipient_name`+`wp_order_id`; SELECT-before-insert on `dedupe_key`). Unit-tested with fixtures.
- **Milestone:** dry-run on a real route → cards visible **read-only** in Tom's Inbox. Nothing can commit.

**Phase 2 — approve→commit (stock-truth production)**
- **Part C (factory-os backend):** `POST …/loose-movement/:exception_id/{approve,reject}` mirroring `credit_decisions`; new `loose_movement_decisions` audit table; **multi-leg atomicity** (§R8: per-leg outcome recorded; exception `status→resolved` only when ALL legs commit; `partially_committed` retries only un-committed legs); `checkBreakGlass` (503 before any write); `emitChangeLog` (+ `change_log` action-enum migration `LOOSE_MOVEMENT_DECISION_APPROVED/REJECTED`); supplies Tom-gate fields at approve time.
- **Part D (portal):** `deep_link` branch for `loose_movement_pending` → detail page modeled on the credit detail page (capability gate, busy/feedback, idempotency-key minting, HTTP→He/En outcome mapping, per-leg edit for flagged lines) + two proxy routes (approve/reject).
- **Milestone:** end-to-end dry-run (no commit) → **first Tom-approved live commit**.

## Governance
Phase 1 (skill + reversible Inbox card) rides the existing low-risk skill posture. **Phase 2 is stock-truth production work** → decision packet → `factory-os-governor` verdict → `release-verifier` before any merge/deploy (per §R11; the endpoint itself shipped under a 2026-05-26 PROCEED_WITH_CONSTRAINTS packet). Part C only **calls** the existing endpoint and adds **no** new `movement_type` → **no** stock-events contract-v2 bump.

## Open probe item (resolved in the first live run)
Returns don't use the pick vocabulary (`לוקט/חלקית/חדש`). Pin the actual **"this return was collected"** signal in LionWheel so we never credit stock IN for a return that didn't physically come back. Until pinned, return cards are flagged/gated.

## Testing
- **Part B:** extend `loose_movement` tests with card-payload + dedup-select fixtures.
- **Part C:** handler tests mirroring `credit_decisions` — approve happy path, multi-leg partial-commit + retry, reject, break-glass 503, idempotency replay (409).
- **Part D:** portal flow tests (view, approve, reject, per-leg edit, non-admin disabled).
- **Gate:** end-to-end dry-run on a real route's exceptions (no commit) before the first live commit.
