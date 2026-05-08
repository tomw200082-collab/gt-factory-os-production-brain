# Future Design Notes — Operator Form UI/UX

> **Status:** PARKED. Not on critical path. Review after 0012 is built and first operator forms are live.
> **Date captured:** 2026-04-16
> **Source:** Window 2 design discussion.
> **Scope:** UI/UX improvements for S-04 Goods Receipt, S-05 Waste/Adjustment, S-06 Physical Count.
> **Constraint:** None of these alter frozen field definitions, enums, or validation rules.

---

## A. Pure Presentation (no architectural dependency)

These are client-only changes. Can be implemented during or after the first screen build pass without any backend or schema changes.

| # | Idea | Rationale |
|---|------|-----------|
| 1 | Progressive disclosure: show `item_id` + `quantity` first, expand remaining fields on demand | Most submissions are routine. Fewer visible fields = faster entry. |
| 2 | Mobile-first single-column layout with large touch targets | Operators use phones/tablets on factory floor, not desktops. |
| 3 | Barcode-first entry for `item_id` on all 3 forms | Eliminates picker search, the slowest step. Count spec already mentions barcode. |
| 4 | Glanceable success/approval states: one icon + one sentence, not a paragraph | Operators scan at speed. Billboard UX. |
| 5 | `dir="auto"` on all data-display fields for Hebrew supplier names and notes | Correct rendering without full RTL layout pass. |
| 6 | "Record another" as sole prominent post-submit action, with supplier/context pre-filled from last submission | Operators do 5-10 entries in a row. Fast re-entry is the primary flow. |
| 7 | MRU shortlist (last-10) above search pickers for supplier, item | Most operators use the same 3-4 suppliers and 40-60 items. Eliminates most typing. Pure client state. |
| 8 | Client-side count progress tracking ("12 of 38 items counted") even without server sessions | Local-only progress bar. No schema dependency. No conflict with AMB-6 deferral. |
| 9 | Short, plain labels everywhere: "Qty" not "Quantity", "Save" not "Submit adjustment", "Done" not "Submission completed successfully" | Factory UX = billboard UX. If you can't read it at a glance, it's wrong. |
| 10 | Post-count message leads with action, not numbers: "You're done" / "Planner will review" / "Please recount" — variance breakdown is secondary | Operators need to know what to do next, not parse arithmetic. |

## B. Architecture-Dependent (requires explicit future approval)

These ideas have backend or contract implications beyond the frozen field definitions. They must NOT be started without a separate design + approval cycle.

| # | Idea | Dependency | Why it needs approval |
|---|------|------------|----------------------|
| B1 | Undo last submission (60s window post-submit) | Requires a reversal-row API endpoint not in current mutation contracts. | Touches ledger append-only semantics. Must be designed with Window 1 to ensure reversal rows are idempotent and don't create double-count risk. |
| B2 | Always-local-first outbox (submission always writes locally, syncs silently) | Already proposed in portal spec outbox pattern. No new schema — but offline write + sync retry logic is non-trivial. | Affects data integrity guarantees. A naive implementation could lose submissions or double-post. Needs explicit sync/retry/conflict contract before build. |

---

*End of future design notes. Review when operator forms are live.*
