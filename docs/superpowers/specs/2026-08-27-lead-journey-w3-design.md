# Lead journey — W3: campaign context on the lead, and ownership that follows the work

> **Status:** design agreed with Tom in the brainstorming session of 2026-08-27
> ("כן, נראה נכון").
> **Scope of this spec:** W3 only (§4). W1 (routing table), W2 (sender) and the
> Meta capability probe get their own specs.
> **Supersedes, in part:** the 2026-08-27 lead-journey masterprompt, whose §2.3
> and §4 ordering are corrected here on measured evidence (§2).

---

## 1. Why this exists

The masterprompt sequences the inbound-lead work as W1 (routing table) → W2
(sender) → W3 (campaign context on the card). Two facts measured on 2026-08-27
invert that order.

**Lead volume is small and expected to stay small.** Tom, 2026-08-27, asked to
size the build: 5–10 leads per week, no campaign scale-up planned. At that rate
the sender saves roughly six minutes of labour a week. It does not buy capacity;
it buys latency. It is also the only workstream that carries external risk —
a business-initiated WhatsApp template, sent without opt-in, puts the quality
rating of the number that carries GT's live order channel at stake.

**W3 carries no external risk and attacks the real bottleneck.** 190 of 195
leads have never been worked. Warming a lead nobody calls converts a cold miss
into a warm miss. What the person who calls needs is to know what the lead
asked about, and for it to be unambiguous who is calling.

New order: **Phase 0 → W3 → W1 → W2 dry-run → W2 live.** Task order is the
implementing session's to set (masterprompt §0); no §1.1 decision is touched.

---

## 2. Corrections to the masterprompt, measured 2026-08-27

| Masterprompt says | Measured | Consequence |
|---|---|---|
| §2.3 "No campaign context on the lead card" | `campaign_name` **is** rendered — `TodayCard.tsx:158`, `LeadDrawer.tsx:300`, `LeadsTable.tsx:292` | D5's first half is already met. The gap is `ad_name` |
| §2.3 "No outbound path of any kind for leads" — read as "no WhatsApp sender exists" | `api/src/order-intake/whatsapp/send.ts` posts directly to `graph.facebook.com/v21.0/{WA_PHONE_NUMBER_ID}/messages` with a long-lived System User token. Only `sendText` / `sendButtons`; no `type: 'template'` anywhere | True for leads, false for WhatsApp. W2 needs a template method, not a transport |
| §6.D "Tom answered `עוד לא יודע`" on who runs the conversation | Tom decided 2026-08-25: `שכל ליד שנכנס יגיע לשלושתנו` — Tom, `alex.berov@gmail.com`, `avi@gteveryday.com` (source: `sales-lead-fanout` Edge Function, gt-factory-os#240) | Stale by two days. Three people share the queue; this spec is designed for three |
| §7.1 "may need Alex or the agency" for Meta | Tom, 2026-08-27: he controls the lead form, and will wire the Meta env vars | The consent line is reachable. Gates W2, not W3 |

Two further findings, both out of this spec's scope and recorded so they are not
rediscovered:

- **`order_intake.wa_event_log` holds 23,125 rows, every one `inbound`.** Zero
  outbound. Either outbound is unlogged or no message has ever left. Under the
  six-layer evidence standard the send path is not proven at layer 1. W2 must
  prove it rather than assume it.
- **`private_core.app_setting` already carries a `whatsapp_templates` key**
  (`api/src/sales/mutations_handler.ts`, `handlePutSettings`). W1 should check
  whether the routing table has a partial home there before creating one.

### 2.1 Delivery was blocked, and is not any more

Every GitHub Actions run on `gt-factory-os` failed in 5–7 seconds from
2026-08-24 20:44 to 2026-08-27 ~11:45 — `runner_id: 0`, no steps, log download
404. The repo is **private**; `gt-factory-os-portal` and
`gt-factory-os-production-brain` are **public** and their runners were healthy
throughout (`portal-pr-guard`, success, 483s, 2026-08-26). Private repos consume
the account's Actions quota; public repos do not. The cause was quota, not
runners, not workflow files, not repo settings.

Tom cleared it on 2026-08-27. Verified by re-running the failed run
`33065709487`: `runner_id: 1000005340`, checkout / setup-node / install all
executing.

Cost while it was down, both recorded so the pattern is recognisable next time:

1. **gt-factory-os#240 is merged but not running.** `deploy-edge-function.yml`
   could not execute, so `sales-leads-poll` is still v12. Alex and Avi do not
   yet receive every lead from the merged path.
2. **`sales-lead-fanout` is a live Edge Function with no source in the repo.**
   Deployed by hand as a bridge, well documented, with a delete date — but it is
   the exact deployed-vs-repo drift the masterprompt warns about in §7.2, created
   two days ago.

---

## 3. Decisions taken 2026-08-27 (Tom, in session)

| # | Decision |
|---|---|
| T1 | Build for 5–10 leads/week. No campaign scale-up assumed |
| T2 | Order: Phase 0 → W3 → W1 → W2 dry-run → W2 live |
| T3 | Tom controls the Facebook lead form; a WhatsApp consent line is achievable and gates W2 |
| T4 | Meta credentials reach Claude as environment variables, never as chat text; capability is read through a probe that returns a redacted report |
| T5 | Lead assignment stays verbal for now. **The system should let whoever enters the details take ownership automatically, because they are the one who spoke to the lead** |

T5 is the substance of §5.2–§5.3.

---

## 4. Scope

**In:**

| | Change | Repo |
|---|---|---|
| W3.1 | `ad_name` exposed on `api_read.v_sales_today` | `gt-factory-os` |
| W3.2 | Claim-on-touch: a staff actor writing to an unassigned lead becomes its assignee | `gt-factory-os` |
| W3.3 | Quick-add claims ownership for the person who typed the lead | `gt-factory-os` |
| W3.4 | Render the ad name; fix empty-string rendering | `gt-factory-os-portal` |

**Out:** W1, W2, the Meta probe, Green Invoice, any frozen flag or code sentinel,
factory-os core tables, the Shopify tax misconfiguration, the 39 unreachable
leads, the undeployed morning reminder, bulk assignment UI (U-012).

Nothing in this spec sends anything to a lead or a customer.
`SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` is untouched and stays `false`.

---

## 5. Design

### 5.1 `ad_name` on the Today view

All six live Facebook leads carry `campaign_name = 'MACHA Leads'`. The field the
portal renders is identical across every lead and therefore carries no
information. The field that separates them — `Matcha Tut` (5) vs `Matcha Mango`
(1) — is `ad_name`, and the portal renders it nowhere.

`api_read.v_sales_leads` already exposes `ad_name`; `api_read.v_sales_today`
does not. One `create or replace view` adds it.

- **Append only at the end of the select list.** `CREATE OR REPLACE VIEW` cannot
  insert a column mid-list or change existing column types; a reordered list is
  a hard error, not a silent success.
- Migration lands in `gt-factory-os/db/migrations/NNNN_*.sql` with its pgTAP
  pair. **List `db/migrations/` immediately before writing the numbered file and
  again after** (`gt-factory-os/CLAUDE.md` §Migrations); a new file appearing in
  between is a `contract_failure` halt, never a silent renumber.
- Schema is `sales_core` / `api_read`. Never `private_core`.

### 5.2 Claim-on-touch

**Rule.** After a mutation has done its own work: if the lead has no assignee
and the actor is an active staff member, the actor becomes the assignee and an
`assignment` event is appended.

Five mutations already accept `p_actor` and represent a human touching a lead:

```
record_outreach  (lead, channel, actor)
record_outcome   (lead, result, next_touch, reason, actor)
add_lead_note    (lead, note, actor)
set_next_touch   (lead, at, actor)
set_lead_status  (lead, status, reason, actor, next_touch)
```

`convert_lead` is excluded by design — it runs as
`'system:sales-leads-poll'` and a nightly job must never own a lead. The
`is_staff` test below excludes it anyway; the exclusion is stated so it is a
decision rather than an accident.

**Two new functions.**

`sales_core.is_staff(text) → boolean` is the soft form of the existing
`assert_assignee`, which raises `SALES_UNKNOWN_ASSIGNEE` (`P0001`) and so cannot
be used as a test. It carries the roster predicate:

```sql
select exists (
  select 1 from private_core.app_users
  where email = p_email and status = 'active'
    and role in ('sales_rep', 'planner', 'admin'));
```

**`assert_assignee` must be refactored to call `is_staff`, not to hold a second
copy of that predicate.** gt-factory-os#240 found and fixed three stale copies of
this exact predicate; `assert_assignee` is the fourth. Adding a fifth inline is
how that bug returns. The refactor keeps `assert_assignee`'s existing behaviour
exactly: `null` and `''` remain legal (unassigning returns a lead to the pool),
and an unknown assignee still raises.

`sales_core.claim_if_unassigned(p_lead_id uuid, p_actor text) → void`:

```sql
if p_actor is null or not sales_core.is_staff(p_actor) then return; end if;

update sales_core.lead
   set assignee = p_actor
 where id = p_lead_id
   and nullif(assignee, '') is null;      -- never steals; also the race guard

if found then
  insert into sales_core.lead_event (lead_id, event_type, payload, actor)
  values (p_lead_id, 'assignment',
          jsonb_build_object('assignee', p_actor, 'via', 'claim_on_touch'),
          p_actor);
end if;
```

**Properties, and why each is load-bearing:**

1. **Never steals.** The `nullif(assignee,'') is null` predicate sits in the
   `UPDATE`, not in a preceding `if`. Two people touching the same unowned lead
   in the same instant produce one winner and one no-op, with no reliance on the
   caller having taken `lock_lead` first. A lead already owned by Alex stays
   Alex's when Avi adds a note.
2. **In the database, not the UI.** The rule holds for the portal, for the
   action buttons in the alert email, and for any future caller. This is the
   same reasoning that put lead deduplication in the database.
3. **System actors cannot claim.** `'system:sales-leads-poll'` is not in
   `app_users`, so `is_staff` is false and the function returns before writing.
4. **Reuses `event_type = 'assignment'`.** Verified against the live
   `assign_lead` definition. `lead_event` is append-only and a new event type is
   a schema decision; none is needed here. The `via: 'claim_on_touch'` payload
   key distinguishes an implicit claim from an explicit one in the timeline.
5. **Reversible.** `assign_lead`, `bulk_assign` and the existing
   `AssigneePicker` still override. Ownership is a marker, not a lock.

### 5.3 Quick-add ownership

`handleQuickAdd` (`api/src/sales/mutations_handler.ts`) routes a manually typed
lead through `sales_core.ingest_lead` so it takes the same normalisation and
org-matching path as a Meta lead. It does not record who typed it —
`ingest_lead` has no actor parameter at all.

**`ingest_lead` is not modified.** It is the sole write path of the live intake,
the pipe that died silently for two months in 2026. A parameter with a `DEFAULT`
is backward-compatible in Postgres, but the change buys convenience, not
correctness, and the risk is asymmetric. It is also wrong semantically: an
inbound Facebook lead has no human at creation. Nobody spoke to them.

Instead, `handleQuickAdd` calls `claim_if_unassigned(lead_id, actorOf(session))`
after `ingest_lead` returns. `actorOf(session)` is the existing helper used by
`handlePutSettings`; `requireSalesAccess(session)` already gates the route.

**`claim_if_unassigned`, not `assign_lead`.** `ingest_lead` deduplicates, so a
quick-add can resolve to an existing lead (`was_new = false`). `assign_lead`
overwrites unconditionally and would let one person's quick-add take a lead
another person already owns. The claim helper cannot.

### 5.4 Portal rendering

One tranche in `gt-factory-os-portal`, under that repo's invariants (one
tranche, evidence path per done-claim, no quarantined surface re-entry).

| File | Change |
|---|---|
| `_lib/labels.ts` | add `colAd: "מודעה"` beside `colCampaign: "קמפיין"` |
| `_components/TodayCard.tsx` | show the ad when present, campaign as fallback. The card is phone-first and space is tight; the ad is the signal |
| `_components/LeadDrawer.tsx` | two separate `Field`s — `קמפיין` and `מודעה`. The drawer has room for full detail |
| `_components/LeadsTable.tsx` | add a `מודעה` column |
| all three | replace `??` with one shared helper |

**Hebrew register.** The `(sales)` route group is on the Tom-approved
Hebrew/RTL list (`gt-factory-os-portal/CLAUDE.md` §UI language, authorised
2026-08-17). `מודעה` is inside an already-authorised surface; no new
authorisation is required.

**The `??` bug.** `LeadDrawer.tsx:300` and `LeadsTable.tsx:292` use
`campaign_name ?? platform ?? "—"`. `??` catches `null`, not `''`. One live lead
carries `campaign_name = ''` and `ad_name = ''` — a Meta test lead, correctly
marked `lost` (masterprompt §7.5) — and renders as a blank cell instead of `—`.
`TodayCard.tsx:158` is already correct because it tests truthiness. One helper
removes the inconsistency:

```ts
const shown = (...vals: (string | null | undefined)[]) =>
  vals.find((v) => v?.trim())?.trim() ?? "—";
```

The same empty-string-is-not-null trap is what W1's routing lookup must honour:
`''` is no match, and an `is not null` check alone lets the test lead through to
the wrong playbook row.

---

## 6. Data flow

```
Meta lead form
  → Make (transport only, D-006)
  → POST /ingest → sales-leads-poll → sales_core.ingest_lead
  → lead + lead_event('created')            [assignee NULL — nobody has spoken]

  → alert email (Resend) to Tom, Alex, Avi  [already carries campaign + wa.me]
  → /sales/today, /sales/leads              [now also carries ad_name]

first human touch, from any surface
  → record_outreach | record_outcome | add_lead_note
    | set_next_touch | set_lead_status
  → claim_if_unassigned(lead, actor)
  → lead.assignee := actor
  → lead_event('assignment', via='claim_on_touch')

manual entry
  → POST /api/v1/mutations/sales/quick-add
  → ingest_lead  →  claim_if_unassigned(lead, actorOf(session))
```

---

## 7. Edge cases

| Case | Behaviour |
|---|---|
| Two staff touch an unowned lead simultaneously | One `UPDATE` matches, one is a no-op. One `assignment` event. No lock required |
| Lead already owned | Untouched. No event. No error |
| System actor (`system:sales-leads-poll`) | `is_staff` false → return before any write |
| Deactivated staff member (`status <> 'active'`) | `is_staff` false → no claim. Consistent with `assert_assignee` |
| `assignee = ''` in existing data | Treated as unassigned by `nullif(assignee,'')`. `assign_lead` already stores `nullif(p_assignee,'')`, so this should not occur; the guard is defensive |
| Quick-add resolves to an existing owned lead | `claim_if_unassigned` no-ops. Ownership is not transferred |
| `campaign_name = ''` and `ad_name = ''` | Renders `—` on all three surfaces |
| `ad_name` null, `campaign_name` set | Today card falls back to campaign; drawer shows `מודעה: —` |

---

## 8. Testing

Every count reported as N/N. "It should work" is not evidence.

**pgTAP** (`db/tests/NNNN_*.test.sql`):
- `v_sales_today` exposes `ad_name`, and its value matches `lead.ad_name`
- `is_staff` true for an active `sales_rep` / `planner` / `admin`; false for an
  inactive user, an unknown address, `null`, `''`, and a `system:` actor
- `assert_assignee` behaviour is unchanged after the refactor: `null` and `''`
  return, unknown raises `SALES_UNKNOWN_ASSIGNEE`
- claim sets `assignee` and appends exactly one `assignment` event
- claim on an owned lead changes nothing and appends nothing
- claim with a system actor changes nothing
- each of the five mutations claims an unassigned lead
- regression: the existing pgTAP suites on 0318–0342 stay green

**node:test** (`api/`): `handleQuickAdd` claims for the session actor; a
quick-add that resolves to an owned lead does not transfer ownership.

**vitest** (portal): the `shown` helper returns `—` for `null`, `undefined`,
`''` and `'   '`, and the first non-blank value otherwise.

**Playwright**: a lead with `ad_name` renders it on `/sales/today` and in the
drawer; the `''` lead renders `—`.

Plus `npm run typecheck` at both repo roots, and the portal's `portal-pr-guard`.

---

## 9. Acceptance

| | Condition | Evidence |
|---|---|---|
| A1 | `/sales/today` shows the ad name for a lead that has one | Observed in the browser, not asserted in a test (masterprompt D5) |
| A2 | The lead drawer shows campaign and ad as separate fields | Browser |
| A3 | A lead with empty-string campaign renders `—`, not blank, on all three surfaces | Browser + vitest |
| A4 | A staff member logging an outreach on an unassigned lead becomes its assignee, visibly, in the timeline | pgTAP + browser |
| A5 | The same action on an owned lead changes nothing | pgTAP |
| A6 | A system actor never becomes an assignee | pgTAP |
| A7 | Nothing customer-facing is live: `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` is still `false`, and no code path added here sends anything outward | grep + review |

**D5 is met in part.** Its third element — "what was auto-sent" — has nothing to
display until W2 exists, and is deliberately deferred rather than stubbed.

---

## 10. Still Tom's

Carried forward from the masterprompt §6, none of it blocking W3:

- **A.** Hand over the matcha catalog file and register it in
  `docs/warehouses/marketing-assets.md`. Blocks W2 sending, not W1 or W3.
- **B.** Confirm the VAT rate shown to customers, and whether the Shopify
  `taxesIncluded=true at 17%` misconfiguration is being fixed separately.
- **C.** Written approval before `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` flips,
  plus a clean dry-run and ≥24h soak.
- **E.** Approve the exact message wording per campaign. `בהקדם` is vaguer than
  a named time, and a specific promise is what makes the 24-hour KPI measurable.
- **New — F′.** Add a WhatsApp consent line to the Facebook lead form. Tom
  confirmed 2026-08-27 that he controls the form. A business-initiated marketing
  template sent without opt-in risks the quality rating of the number carrying
  GT's live order channel. **This ranks above A on the W2 critical path.**
- **New — G.** Deploy `sales-leads-poll` from `main` now that CI is restored,
  then drop the bridge: `drop trigger if exists lead_alert_fanout on
  sales_core.lead_event;` and delete the `sales-lead-fanout` Edge Function
  (gt-factory-os#241).

§6.D is closed: three people, decided 2026-08-25.

---

## 11. Halt conditions

Inherited from `gt-factory-os-production-brain/CLAUDE.md` §Stop conditions.
Specific to this work:

- A migration slot is taken between the two directory listings →
  `contract_failure`, halt, never renumber silently.
- Any change would let a claim overwrite an existing assignee → stop. Ownership
  transfer is explicit, or it is a bug.
- Any code path added here would reach a customer → stop.
- `ingest_lead`'s signature or behaviour would change → stop and re-open the
  §5.3 decision with Tom; it is the sole live intake path.
- A new `lead_event` type would be introduced → stop; the history is append-only
  and `assignment` already exists.
