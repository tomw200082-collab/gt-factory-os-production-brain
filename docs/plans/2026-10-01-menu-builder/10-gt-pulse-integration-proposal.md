# Menu Builder ↔ GT Pulse — how a rep sees the customer's menu and kit (proposal)

> 2026-10-01, Session 2, at Tom's request: "so that a rep can see exactly what the customer put in the cart". **Thinking only.** Nothing here is built in the Sales system, and nothing changes GT Pulse.
> Built preview: https://claude.ai/artifact/2BrWABm82tPHyMwiSuFPQj · code: gt-factory-os branch `claude/menu-builder-preview` (`api/src/portal/builder/`, not routed, not deployed).

## 1. Where GT Pulse is today (read live, 2026-10-01 ~08:10 UTC)

- **Unit A is in production.** PR #329 merged (`30759a2`); migration 0362 applied with `rebuild_verifier()=0`; portal `eb36b83`; the 184-task backlog was applied with Tom's approval (146 first contact in the manager queue, 37 + 1 call). `activity_required` is off. Tasks route from `lead_event` through `tg_lead_event_task`, owners follow `lead.assignee`, reps see only their own leads (D3), and each lead has at most one open `reply` task (D17).
- **D phase 1 is being built now** (tranche 186, portal PR #240): new colour tokens, a petrol Today header, and a four-node **mini journey rail on every Today card** (received → contacted → next action → order).
- **Not started:** units B (business + full order history), C (retention and expansion; the "basket map") and the rest of D (business circle, contact compass, event river, basket map).

## 2. What the rep should see (the target)

The rep opens a lead and sees what the customer is building, not a pointer to it:

1. **The menu:** drink photos and names, in the customer's order, with what changed (added after the starting set, removed from it).
2. **The kit as it stands now:** product lines, quantities, cups covered, total before VAT, whether the ₪800 round-up was applied, and whether the customer edited quantities.
3. **Liveness:** `בונה עכשיו` when the customer was active in the last 10 minutes. A call at that moment lands in the middle of the decision.
4. **The next move:** the task the system already opened (asked for help → `reply`; finished a menu and did not order within 24 h → `call`), with the menu in its reason line.

## 3. How it connects (smallest change on each side)

| Layer | Builder side (owned by the Builder) | GT Pulse side (Sales lane, after D1) |
|---|---|---|
| State | `customer_portal.builder_session` per lead: selection, starting set, kit snapshot (lines, totals, round-up, edits), `last_active_at`, status (`building` · `kit_viewed` · `ordered`) | — |
| Read model | `api_read.v_sales_builder`: one row per lead, built from the session; never raw jsonb in the UI | Reads it through the existing sales query handler **with the D3 rep scope** |
| Events | Writes `menu_builder` with `step ∈ {opened, menu_completed, help_requested}`; the existing `draft_order` gets `builder_session_id` | CHECK +1 value; two trigger rules: `help_requested → reply` (D17 dedups), `menu_completed → call` due +24 h, cancelled by `draft_order` |
| Lead drawer | — | Block `התפריט שבנה`: drinks, kit lines, total, `עודכן לפני X דק׳`, the live dot, the changes against the starting set; one link "לראות כמו שהלקוח רואה" (read-only staff view of the same Builder page) |
| Today card | — | **No fifth rail node** (D1's rail is fixed at four and approved). A small line under the reason: `תפריט · 8 משקאות · ₪1,100`, and the live dot. |
| Timeline | — | Labels for the three steps; the starter kit is never called by the existing `kit_sent` event's words |
| Later (unit C) | The sent kit is the lead's first basket | The basket map compares kit → first order → reorders: what the menu promised and what the café actually reorders |

## 4. Prices

The kit is priced only by the portal pricer: list prices for a lead, today from Shopify. When the price book (`sales_core.list_price` / `customer_price`, 0 rows today) becomes the source, the pricer reads it and the Builder follows with no change of its own. The drawer shows the total the customer saw at their last change, plus a mark if today's prices give a different total. GT Pulse never computes a kit or a price.

## 5. What it needs from each side, in order

1. Tom: placement (spec §3) and the go to build the server side.
2. Builder lane: the session table, the kit endpoint around `kit.mjs`, the read model, the event writes (code that exists in no other workstream).
3. Sales lane, once D1 merges: the CHECK value, the two trigger rules, the drawer block, the Today line, the labels, each in its own tranche with Tom-approved Hebrew.
4. Unit C, later: the basket map that reads the kit.

The preview already answers what the customer sees. Liveness, the drawer and the tasks need the server build, because the preview keeps the menu in the phone's browser.
