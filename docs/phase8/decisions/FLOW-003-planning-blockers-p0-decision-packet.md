# FLOW-003 — Planning Blockers P0 Decision Packet

**Status:** DECISION-READY (Tom decision required before any change).
**Date:** 2026-05-08
**Source audit:** DR-005 (initial flag), DR-010 (held pending source reads), DR-011 (full source reads, confirmed P0).
**Audited tip:** `9605553` (window2-portal-sandbox).
**Run:** Phase 8 Run B — controlled execution layer build-out.
**Author:** factory-os-governor + ux-flow-architect + ux-content-state-designer (joint, read-only).

---

## A. Summary of the confirmed P0

`/planning/blockers` exposes a **planner-facing call-to-action that has no in-app resolution path.** Specifically, for any blocker of subtype `po_substrate_absent_supply_not_netted`, the planning engine emits `fix_action_label = "check_po_substrate"`, which the portal renders as the Hebrew string **`"פנה למפתח"`** ("contact a developer") in the **"מה עושים עכשיו?" / "what to do now?" CTA column**.

A planner viewing this row cannot act in the portal. There is no developer name, no mailto link, no ticket form, no expected timeline. The blocker remains in the planner's queue indefinitely until a developer is contacted manually through some out-of-band channel.

This is the most direct operator-facing defect found in the Wave 2 UX audit cycle. It is the sole reason `/ux-release-gate` returned **HOLD** at the aggregate level on 2026-05-08.

---

## B. Route / surface

- **Route:** `/(planning)/planning/blockers`
- **Components involved:**
  - `_lib/labelMaps.ts` (string source)
  - `_components/BlockerRow.tsx` (desktop table — Q4 cell + Q5 cell)
  - `_components/BlockerCard.tsx` (mobile card — CTA pill + sub-line)
  - `page.tsx` (header comment confirming intentional "פנה למפתח" fallback semantics)
- **Triggering blocker subtype:** `po_substrate_absent_supply_not_netted`
- **Audience:** planners and admins (per `project_inbox_audience_planner_admin_only.md`; operators do not see this surface).

---

## C. Exact source files and locations already read

Read in DR-011 (full source reads):

| File | Lines read | Relevant range |
|------|-----------|---------------|
| `src/app/(planning)/planning/blockers/_lib/labelMaps.ts` | 1–104 (full) | 32–39 (FIX_ACTION_LABEL_HE), 33 (Tom-lock comment) |
| `src/app/(planning)/planning/blockers/_components/BlockerRow.tsx` | 100–200 | 143–146 (Q4 cell), 148–170 (Q5 cell) |
| `src/app/(planning)/planning/blockers/_components/BlockerCard.tsx` | 120–200 | 147–167 (mobile fallback CTA pill + sub-line) |
| `src/app/(planning)/planning/blockers/page.tsx` | header comment only | line 16 (intentional fallback documented) |

No new source reads are required for this decision. All evidence is in DR-011 §D.2 and §F.2–F.3.

---

## D. Current behavior

### D.1 — Role 1 (Q4 — "מה עושים עכשיו?" CTA value) — confirmed P0

- The Hebrew string `"פנה למפתח"` is hard-coded in `FIX_ACTION_LABEL_HE` at `labelMaps.ts:37` for the key `check_po_substrate`.
- The string is rendered in `BlockerRow.tsx:144-146` as plain text inside the Q4 `<td>`. Not a link, not a button, no `onClick`.
- On mobile, `BlockerCard.tsx:147-167` renders the same string inside a styled `<div>` (CTA pill style) with the sub-line `"חסם זה דורש התערבות מפתח/אדמין"` ("this blocker requires developer/admin intervention").
- The string is **Tom-locked verbatim 2026-04-27** per `labelMaps.ts:33` — therefore copy may not be changed without Tom's explicit approval.

### D.2 — Role 2 (Q5 — "איפה מתקנים?" fallback chip) — downgraded to P1

- When `fix_route` is null on the blocker DTO, `BlockerRow.tsx:163-168` renders the same Hebrew string `"פנה למפתח"` inside a static `<span>` chip with a `title` attribute explaining the meaning.
- This is honest fallback labelling consistent with the documented "no fix_route" state. It is **not** a CTA — it is a location indicator that says "the location to fix this is outside the app."
- Cleared as P0 by DR-011 §E. Confirmed P1 polish item.

---

## E. Why it is a P0

1. **It is a CTA, not a status indicator.** The Q4 column is operationally framed as the planner's primary daily action ("what to do now"). Putting "contact a developer" there equates planner work with developer escalation, which is a workflow design failure.
2. **It has no in-app resolution path.** No mailto, no ticket, no developer name, no SLA expectation. The planner cannot self-serve.
3. **It applies to an entire blocker subtype** — `po_substrate_absent_supply_not_netted`. This is not a one-off edge case; every occurrence of this subtype hits the same dead end.
4. **Operator/planner workflow is the project's mission.** CLAUDE.md non-negotiable #2 states the rebuild must deliver "simple operator workflows." A terminal "contact developer" instruction is the opposite of a simple workflow.
5. **It violates the operational-flow-map requirement** (UX_OPERATING_PRINCIPLES.md) that every step must support entry → terminal action → post-action visibility. The terminal action here is undefined.

---

## F. Why it cannot be changed without Tom approval

- Both `BLOCKER_LABEL_HE` and `FIX_ACTION_LABEL_HE` carry `// Tom-locked verbatim 2026-04-27.` comments at `labelMaps.ts:24` and `labelMaps.ts:33`.
- Hebrew copy in this surface is a Tom-pinned register entry per `feedback_portal_ui_english_ltr.md`.
- Changing the string OR replacing it with a link/button/handler changes operator-visible workflow language and routing — a UX-visible portal change that requires UX agent handoff per `EXECUTION_POLICY.md`.
- A self-service ticket action (Option A below) requires either a backend endpoint or an external integration. That is `backend-db-executor` and possibly `integration-boundary-executor` work, both of which require Tom approval per their agent definitions.
- Removing the blocker subtype entirely (Option B below) means changing planning-engine logic — a `backend-db-executor` change with explicit Tom approval per CLAUDE.md locked decisions on planning engine semantics.

In short: **every viable resolution path crosses a Tom-approval boundary.**

---

## G. Option A — self-service ticket / action with blocker context prefilled

### G.1 — Description

Convert the `check_po_substrate` row's Q4 cell from plain text into a clickable CTA that opens a pre-filled ticket form. Candidate destinations:

- **Internal endpoint:** `POST /admin/dev-tickets` writing to a new `dev_tickets` table or `exceptions` row with category `dev_escalation`. Most aligned with CLAUDE.md (no external system writes by default).
- **External:** mailto link with structured body, or Linear/GitHub Issues integration. These would route through `integration-boundary-executor` and require external-write approval.
- **Hybrid:** internal write + email notification to a developer alias.

The ticket payload would carry blocker context the planner already has on screen:
- `exception_id` / `blocker_id`
- `blocker_label` (e.g. `po_substrate_absent_supply_not_netted`)
- `display_name` (item or component name) — enforced per `feedback_names_not_ids_in_ui.md`
- `demand_qty`
- `earliest_shortage_at`
- current `planning_run_id`
- planner identity (from auth)
- timestamp

Hebrew button label candidates (Tom decides exact wording):
- `דווח באג` ("report bug")
- `פתח כרטיס לדב` ("open ticket to dev")
- `שלח דיווח` ("send report")
- `שלח לדב את החסם` ("send the blocker to a dev")

### G.2 — Required work

| Layer | Work | Owner |
|-------|------|-------|
| DB | New table `dev_tickets` OR extension of `exceptions` with new category | `backend-db-executor` |
| API | `POST /admin/dev-tickets` route + Zod schema | `backend-db-executor` |
| Portal | Replace Q4 plain-text with CTA button calling new endpoint; success/loading/error states; Q5 stays as-is | `portal-production-executor` |
| UX | Microcopy register entries for button label, success message, error message; standard confirmation pattern | `ux-content-state-designer` |
| Optional | Email notification or external integration | `integration-boundary-executor` |

### G.3 — Why this is the recommended direction

Per CLAUDE.md non-negotiable #2 ("simple operator workflows") and the operational-flow-map principle, **every operator-visible action should have an in-app terminal step.** Option A is the only option that makes the CTA actually act.

---

## H. Option B — fix root cause and remove the `check_po_substrate` blocker class

### H.1 — Description

`check_po_substrate` exists because the planning engine cannot reliably answer a question about open POs for the `po_substrate_absent_supply_not_netted` subtype. Possible root-cause directions:

- The engine sees a blocker condition but lacks the data to compute a fix proposal because PO substrate state is ambiguous.
- A specific data shape (e.g. PO line without a canonical component_id, or PO at a status that prevents netting) cannot be resolved by the engine and is escalated as "developer-only."

If the planning-engine logic is fixed so that the substrate is checkable in-app — e.g. by netting the PO substrate, by surfacing the missing data as a different kind of blocker (e.g. "set component on PO line"), or by elimimating the unreachable code path — this entire blocker subtype goes away.

### H.2 — Required work

| Layer | Work | Owner |
|-------|------|-------|
| Investigation | Trace why `po_substrate_absent_supply_not_netted` is emitted and what the engine cannot resolve | `backend-db-executor` (engine), with `source-of-truth-auditor` for contract review |
| Engine | Possibly: change netting logic; change blocker emission rules; reclassify subtype to a planner-actionable subtype | `backend-db-executor` |
| Tests | Parity tests; rebuild verification for any planning-run output that changes | `backend-db-executor` |
| Portal | Possibly: removal of the dead `check_po_substrate` key from `FIX_ACTION_LABEL_HE`; might be no UI change at all if the engine simply stops emitting | `portal-production-executor` (small) |

### H.3 — Why this is potentially the most thorough

If the substrate can be made checkable in-app by improving engine logic, the workflow defect goes away at the source instead of being papered over with a ticket button. This is the architectural answer.

### H.4 — Why this is not the default recommendation

- The investigation cost is unbounded; the engine logic that emits this subtype may be defensible. There may be legitimate cases where developer-only intervention is the correct answer (e.g. a PO created via the manual path with a non-canonical component_id that the engine cannot map).
- Even if Option B is the long-term answer, the workflow defect needs immediate mitigation. Option A or Option C must still ship in the interim.

---

## I. Option C — interim runbook / copy clarification

### I.1 — Description

Leave the CTA as `"פנה למפתח"` (or sharpen it to `"שלח לדב את ID החסם"`) and ship a runbook that:

- Names the developer to contact (or a team alias).
- Specifies what info to send (blocker_id, exception_id, display_name, planning_run_id).
- Sets an expected response time.
- Lives in `docs/runbooks/planning-blockers-developer-escalation.md` (created by `ops-docs-curator`).
- Is referenced from the Q4 cell via a `title` tooltip (no copy change to the CTA itself if Tom prefers; or a small sub-line in the table row).

The Hebrew CTA could optionally be tightened to `"שלח לדב את ID החסם"` ("send the blocker ID to a dev") which is more actionable than `"פנה למפתח"` while still not requiring a backend change.

### I.2 — Required work

| Layer | Work | Owner |
|-------|------|-------|
| Runbook | New file `docs/runbooks/planning-blockers-developer-escalation.md` | `ops-docs-curator` |
| Portal | Optional `title` attribute change on the CTA cell, OR optional sub-line. **No CTA copy change without Tom approval.** | `portal-production-executor` (tiny) |
| UX | If sub-line is added: register entry for the helper text | `ux-content-state-designer` |

### I.3 — Why this is acceptable as an interim only

Option C does not fix the workflow. It documents the workaround. Acceptable for ≤ 2 weeks while Option A's backend work is scheduled. **Not acceptable as the v1 production answer.**

---

## J. Risks of each option

### J.1 — Option A risks

| Risk | Severity | Mitigation |
|------|---------|-----------|
| Backend endpoint creates an unbounded internal-ticket surface that nobody owns operationally | medium | Define ticket lifecycle in the runbook; assign default owner; cap retention |
| Email/external integration fails silently and tickets are lost | medium-high | Internal-only path first; external integration only after dry-run + Tom approval |
| Pre-filled context exposes data the developer should not have (e.g. supplier names, customer info) | low | Audit the payload; restrict to operationally required fields |
| The ticket button itself becomes a dumping ground for non-`check_po_substrate` issues | low | Keep the CTA tied to the specific subtype; surface generic feedback through a separate path |
| Adds a new movement_type-equivalent surface with audit obligations | low | Use the `exceptions` table or a tightly-scoped new table with creator + timestamp + payload |

### J.2 — Option B risks

| Risk | Severity | Mitigation |
|------|---------|-----------|
| Engine investigation reveals the blocker is correct as-emitted; option provides no path forward | medium | Time-box investigation; if engine defensible, fall back to Option A |
| Engine fix introduces parity drift in `planning_runs` / `planning_run_lines` | high | Parity test gate; rebuild verification; rollback plan |
| Downstream surfaces (purchase recommendation review, production recommendation review) silently change behavior | high | Source-of-truth audit before merge; release-verifier mandatory |
| Investigation cost is unbounded | medium | Time-box to one focused dry-run |

### J.3 — Option C risks

| Risk | Severity | Mitigation |
|------|---------|-----------|
| Runbook is ignored; planners still don't know what to do | high | Tooltip / sub-line referencing the runbook; train planners |
| Workflow defect persists in production indefinitely | high | Treat Option C as a 2-week interim with a hard cutover to Option A |
| Documentation drift — runbook stale within weeks | medium | `ops-docs-curator` ownership; quarterly review |
| Tooltip-only signaling fails on touch devices | medium | Add a sub-line in the row body, not just a `title` attribute |

---

## K. UX impact of each option

### K.1 — Option A

- Planner can act in-app. CTA becomes a real CTA. Daily-use friction drops on every `check_po_substrate` blocker occurrence.
- Tom Tax (per `feedback_tom_lens_audit_calibration.md`): **negative** — planner saves out-of-band work; developer side gains structured tickets instead of unstructured pings.
- Smallest source-of-truth churn: just adds a new ticket route / endpoint; doesn't touch ledger, projections, or planning engine.

### K.2 — Option B

- If successful, the CTA never appears. Best UX. Highest engineering cost.
- If unsuccessful, planner still sees `"פנה למפתח"` but with one fewer reason for it to appear (some prior emissions reclassified). Net UX improvement is bounded by how much the engine fix reclassifies.

### K.3 — Option C

- Planner reads a tooltip / runbook. Workflow is still terminal at "contact a developer." Daily-use friction unchanged.
- Tom Tax: **slightly negative** — tooltip discoverability is poor; touch devices may miss it.
- Acceptable for ≤ 2 weeks only.

---

## L. Backend / integration implications of each option

### L.1 — Option A

- New table `dev_tickets` OR extension of `exceptions` table — `backend-db-executor` with migration sequence number reserved (next available `0175+`).
- New API route `POST /admin/dev-tickets` — `backend-db-executor`.
- Optional notification path: email or external — `integration-boundary-executor` only with Tom approval; default v1 is internal-only.
- Idempotency: ticket creation must include an idempotency key derived from `(blocker_id, planner_id, day)` to prevent duplicate tickets on double-click.
- Audit: ticket creation logged; no impact on stock ledger, projections, or planning runs.

### L.2 — Option B

- Possibly migration to add a new blocker subtype OR remove an old one (must keep enum value for historical rows per CLAUDE.md migration discipline).
- Possibly changes to `planning_run_lines` blocker emission logic.
- Mandatory: parity test gate; rebuild verification; release-verifier; full source-of-truth audit on contract docs.
- May trigger `STALE_PLANNING_VERSION` semantics if a run output changes during deploy.

### L.3 — Option C

- No backend or integration changes.
- Pure docs work + (optional) tiny portal `title` attribute or helper sub-line.

---

## M. Recommended option

**Recommended: Option A (self-service ticket / internal endpoint), with Option C as an explicit ≤ 2-week interim.**

### M.1 — Reasoning

1. CLAUDE.md non-negotiable #2 ("simple operator workflows") is best served by Option A.
2. Option A is the smallest set of changes that converts the CTA into an actual CTA — the workflow defect is fixed at the user-visible layer without disturbing the planning engine.
3. Option B is the architecturally cleanest answer but cost is unbounded; should be scheduled separately as a planning-engine investigation, not as the v1 fix.
4. Option C alone is not acceptable as the v1 production answer because it leaves the workflow terminal at "contact a developer."

### M.2 — Proposed sequencing

| Phase | Work | Approx. effort | Tom approval gate |
|-------|------|---------------|------------------|
| Now (interim, ≤ 2 weeks) | Option C runbook + tooltip / sub-line if Tom approves | 1 dry-run + 1 small portal commit | yes (any UX-visible portal change) |
| Next (Option A) | Internal-only `POST /admin/dev-tickets` endpoint + portal CTA | 1 backend migration + 1 portal commit + UX handoff packet | yes (new operator-facing form per portal-production-executor) |
| Later (Option B if warranted) | Planning-engine investigation + possible reclassification | dedicated dry-run + parity gate | yes (BOM/ledger/planning-engine logic changes per CLAUDE.md) |

---

## N. Exact decision needed from Tom

Tom must answer the following four questions in writing:

1. **Which option is approved as the v1 fix path?** (A / B / C / A-with-C-as-interim / other)
2. **If Option A:** is the internal-only `POST /admin/dev-tickets` endpoint approved, OR is an external integration (email / Linear / GitHub) preferred?
3. **If Option C is approved as interim:** is the existing `"פנה למפתח"` to remain verbatim, OR is `"שלח לדב את ID החסם"` (or another tightening) approved? Provide exact Hebrew copy.
4. **Hebrew button label for Option A** (when Option A is approved): `דווח באג` / `פתח כרטיס לדב` / `שלח דיווח` / `שלח לדב את החסם` / other.

Tom must also confirm:

5. **The audience scope** (planner+admin only, per `project_inbox_audience_planner_admin_only.md`).
6. **Who is the named developer / team alias** for the runbook (Option C) and the ticket destination (Option A)?

---

## O. Forbidden actions until Tom decides

Until Tom answers in writing, the following are **forbidden** in this run and any subsequent run:

- Edit `_lib/labelMaps.ts` (FIX_ACTION_LABEL_HE or BLOCKER_LABEL_HE).
- Edit `_components/BlockerRow.tsx` Q4 or Q5 cells.
- Edit `_components/BlockerCard.tsx` mobile fallback.
- Edit `page.tsx` for `/planning/blockers`.
- Add a `dev_tickets` table or migration.
- Add a `POST /admin/dev-tickets` endpoint.
- Add an external integration for ticket forwarding.
- Update `portal_ux_standard.md` for the blocker CTA.
- Update `CONTENT_AND_MICROCOPY_GUIDE.md` for `check_po_substrate`.
- Mark FLOW-003 closed in `UX_RELEASE_GATE.md`.
- Lift the aggregate HOLD verdict on `/ux-release-gate`.

The aggregate HOLD on `/ux-release-gate` remains in effect until Tom decides AND the chosen option is implemented AND a follow-up `/ux-release-gate` run returns CONDITIONAL_SHIP or SHIP for `/planning/blockers`.

---

## P. Cross-references

- DR-005 — initial flag (`docs/phase8/dry-runs/DR-005-ux-flow-audit-planning-blockers.md`)
- DR-010 — gate verdict held pending source reads (`docs/phase8/dry-runs/DR-010-ux-release-gate-wave2-scope.md`)
- DR-011 — full source reads, P0 confirmed (`docs/phase8/dry-runs/DR-011-ux-release-gate-full-source-reads.md`)
- `docs/phase8/ux/UX_RELEASE_GATE.md` — current aggregate verdict
- `docs/phase8/ux/OPERATIONAL_FLOW_MAP.md` — flow doctrine that this defect violates
- CLAUDE.md non-negotiable #2 — "simple operator workflows"
- `project_inbox_audience_planner_admin_only.md` — audience scope
- `feedback_portal_ui_english_ltr.md` — Hebrew register policy
- `feedback_names_not_ids_in_ui.md` — naming conventions for ticket payload
- `feedback_tom_lens_audit_calibration.md` — Tom Tax calibration

---

**END OF DECISION PACKET — Tom decision required. No code, copy, or contract change occurs until Tom answers in writing.**
