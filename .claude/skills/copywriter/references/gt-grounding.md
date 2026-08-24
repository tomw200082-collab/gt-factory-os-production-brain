# GT Everyday — grounding before you write a claim

GT sells beverage bases wholesale to Israeli HoReCa. The copy craft in this skill applies
unchanged; what changes is that **every fact must come from a named, dated source** — the
Sales-Machine constitution treats an undated volatile fact as a defect, not a shortcut.

## Where truth actually lives

| You need | Read | Notes |
|---|---|---|
| What we sell, real names, SKUs | `gt-factory-os-production-brain/docs/warehouses/catalog-truth.md` | "ACTIVE in Shopify is a hint; this file is the truth" |
| Prices | `docs/pricing/2026-08-05_shopify_products_exvat.tsv` (via catalog-truth) | **ex-VAT** — customer-facing copy must state the VAT basis |
| Approved images and design assets | `docs/warehouses/marketing-assets.md` | owner: `gt-assets-designer` |
| Accounts, segments, market research | `Sales-Machine/knowledge/` + `registry.yaml` | every card carries source, date, authority grade |
| Dated numbers you may quote | `Sales-Machine/evidence/<date>-*.md` | true *as of* their date; never quote as "current" |
| What is decided vs proposed | `Sales-Machine/doctrine/decisions.md` | |
| Open unknowns | `Sales-Machine/CURRENT_STATE.md` (UNRESOLVED table) | |

Authority grades matter: `user_confirmed` (Tom said it) and `system_verified` are usable in
copy; `inferred` is a hypothesis and is never policy — so it is never a claim.

## Not decided yet — do not write around it

- **ICP (U-005)** and the **Core Story** are explicitly UNRESOLVED. Positioning statements
  like "our ideal customer is…" or an education-first narrative presented as doctrine would
  be inventing policy. Write the copy for the audience the request names, mark the positioning
  assumption, and let Tom confirm.
- Several account histories are open questions (U-001, U-002). Never write a win-back that
  asserts *why* an account went quiet.

## Hard boundaries

- **Nothing is sent.** `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` is `false`. This skill produces
  drafts for Tom; it does not email, message, or publish to a customer or a lead.
- **Prices and product names are never written from memory.** Pull them, or mark them for
  verification.
- **Portal and product UI strings are a different lane** — they go through
  `ux-content-state-designer` and the portal's Hebrew register table, not through here.
- Claims about stock, delivery windows, or lead times touch factory truth; source them from
  the operational systems or leave them out.

## The "to verify" habit

Any number, customer name, or capability claim that reaches a draft carries its source inline
during drafting, and appears in the deliverable's **To verify** list if it could not be
sourced. A short verify list is a sign of a careful draft. Silent confidence is the failure
mode this repo exists to prevent.
