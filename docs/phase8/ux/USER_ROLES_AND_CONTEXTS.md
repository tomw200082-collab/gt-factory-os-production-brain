# User Roles and Contexts — GT Factory OS Portal

**Owner agent:** `ux-flow-architect`
**Authoritative status:** DRAFT. Role definitions from CLAUDE.md §Auth and roles (locked).
**Update rule:** Role additions require CLAUDE.md update (Tom-only). Context additions by ux-flow-architect.
**Release-gate relevance:** Route access violations (operator seeing planner UI) = P0.

---

## What belongs here

- Canonical role definitions and their portal access context.
- Daily workflow context for each role (what they do, what they need to see).
- Role-specific UX considerations.

## What must never go here

- Backend RLS rules or API permission logic.
- Auth implementation details.
- Copy strings.

---

## Canonical roles (from CLAUDE.md §Auth and roles)

| Role | Auth method | Portal access | Daily context |
|------|-------------|---------------|---------------|
| `operator` | Supabase magic-link | Operational forms only | Files production reports, goods receipts, waste adjustments; does not see planning or purchasing |
| `planner` | Supabase magic-link | Planning + operational oversight | Creates/approves plans, manages purchase orders, reviews recommendations, views dashboard |
| `admin` | Supabase magic-link | Full portal including admin CRUD | Manages master data, runs migrations, creates manual POs, manages users |
| `viewer` | Supabase magic-link | Read-only dashboard | Views stock truth and planning status; cannot submit any form |

---

## Operator — daily context

**Who:** Factory floor staff at GT Everyday.
**Primary tasks:**
1. File a production report at end of each production run.
2. Record goods received from a supplier delivery.
3. Record waste or adjustment when inventory discrepancy is found.

**What they need to see:**
- Today's planned production (what to make today).
- The production report form (what to fill in after making it).
- The goods receipt form (when goods arrive).
- Confirmation that their submission posted correctly.

**What they must NOT see:**
- Planning run details, recommendation engine output.
- PO creation or approval flows.
- Dashboard exception inbox (Decision/To-Do/Warning/Info cards — planner+admin only per project memory).
- Admin master data CRUD.

**UX priorities for operators:**
- Speed above all. An operator filing a report should take < 60 seconds on a familiar route.
- Error recovery must not require a developer. The form must tell them what to do.
- Mobile-first: many operators use a tablet or phone on the factory floor.
- Hebrew data values (product names, supplier names) must render correctly in LTR layout.

---

## Planner — daily context

**Who:** Tom (and eventually Alex). Responsible for planning, purchasing, and production oversight.
**Primary tasks:**
1. Review planning run output and approve/adjust recommendations.
2. Create or approve purchase orders.
3. Review planning blockers and resolve them.
4. Edit monthly forecast.
5. Review dashboard for stock truth and exceptions.
6. Monitor LionWheel open orders vs. inventory.

**What they need to see:**
- Full planning surface (runs, recommendations, blockers, forecast).
- PO list and PO edit flows.
- Goods receipt history (to verify deliveries against POs).
- Dashboard with exception inbox.
- Inventory flow with planned overlay.

**UX priorities for planners:**
- Context at a glance. The planner should see the current state of every open decision without drilling into individual records.
- Confidence before approval. A recommendation must show the underlying demand, supply, and gap before the planner approves.
- Auditability. A planner who approved a PO last week must be able to find that PO and see what was received against it.

---

## Admin — daily context

**Who:** Technical operator / Tom. Manages master data and system health.
**Primary tasks:**
1. Add or update items, components, BOMs, suppliers.
2. Create a manual PO when planning flow cannot be used.
3. Manage user accounts.
4. View jobs monitor and exception inbox.

**UX priorities for admins:**
- Data accuracy over speed. An admin edit is less frequent but higher stakes.
- Change review. Admin CRUD should show what was before and what is being changed.
- Error prevention. Master data changes that would break a live planning run should be flagged.

---

## Viewer — daily context

**Who:** External stakeholders, observers.
**Access:** Read-only dashboard and stock view. No forms.

**UX priorities for viewers:**
- Clarity. The viewer cannot take any action, so every piece of information should be self-explanatory without additional context.

---

## Role-based UX rules

1. **Route gating is not a design substitute.** If a route is gated to planners, it should still be well-designed for planners — not just hidden from operators.
2. **Operator forms must be fast and recoverable.** They are high-frequency, time-sensitive.
3. **Planner screens must show context.** A recommendation without supporting data is not useful.
4. **Inbox cards (Decision/To-Do/Warning/Info) are for planner+admin only.** Operators submit forms but never see the Exceptions Inbox cards.
5. **Viewers see data, never forms.** Any button or CTA visible to a viewer is a P0 permission bug.
