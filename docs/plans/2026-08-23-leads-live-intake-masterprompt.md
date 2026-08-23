# MASTERPROMPT — Leads Live Intake: turn the built workspace into a flowing pipeline

> **Usage (Tom):** paste this entire file as the first message of a fresh Claude Code
> session on a frontier model, with all four repos attached (`gt-factory-os`,
> `gt-factory-os-portal`, `gt-factory-os-production-brain`, `Sales-Machine`).
> The session builds everything that can be built without you, **halts exactly once**
> for two credentials only you can create, then brings the pipeline live and proves it
> with six-layer evidence. Your part is listed in §5 — do it in parallel while the
> session builds; nothing else is yours.
>
> **Provenance:** written 2026-08-23 in session `claude/sales-system-lead-flow-czhmrl`,
> from live-verified state (Supabase `rvadsozabmxkkrktwgnv` queried 2026-08-23; deployed
> Edge Functions listed 2026-08-23). Design authority for everything herein:
> `docs/superpowers/specs/2026-08-10-sales-leads-pipeline-design.md` (merged, PR #127).
> This file adds no new design decisions — it sequences the two phases of that spec
> that have not shipped, and closes the documentation loop.

---

## 0. Operating instructions — read before anything else

1. **Boot order (mandatory reads, in order):**
   1. `gt-factory-os-production-brain/CLAUDE.md`
   2. `gt-factory-os/CLAUDE.md`
   3. `Sales-Machine/CLAUDE.md` → `Sales-Machine/CURRENT_STATE.md` → `Sales-Machine/doctrine/decisions.md`
   4. `gt-factory-os-production-brain/docs/superpowers/specs/2026-08-10-sales-leads-pipeline-design.md` — **read it in full; it is the design.**
   5. This file's remaining sections.
2. **Authority order:** production-brain `CLAUDE.md` → `gt-factory-os/CLAUDE.md` →
   `Sales-Machine/CLAUDE.md` → the 2026-08-10 design spec → this file. On conflict,
   higher wins; if this file conflicts with a constitution, STOP and surface it.
3. **Skills are mandatory, not suggestions:**

   | Moment | Skill |
   |---|---|
   | Session start | `using-superpowers` |
   | Before coding | `superpowers:writing-plans` — a short task-level plan from §4, then execute it |
   | Every implementation task | `superpowers:test-driven-development` |
   | Any failure or surprise | `superpowers:systematic-debugging` |
   | Before any "done" or "live" claim | `superpowers:verification-before-completion` |

   Do **not** use `brainstorming` — the design phase is finished and Tom approved it
   (Amendment A, 2026-08-17). Do not re-litigate anything marked LOCKED in the spec.
4. **Language:** code, comments, commits, PR bodies, docs — English. Email templates and
   any user-visible string — Hebrew, per the spec (§7 gives the exact subjects).
5. **Git:** work on the branch this session designates for each repo; push with
   `git push -u origin <branch>`; open PRs; never `git add -A`. Merge autonomously only
   when checks are green and the change is verified (production-brain authorization,
   Tom 2026-06-20); the prod deploy + migration-apply autonomy of 2026-07-24 applies,
   with its one-line announcement before dispatch.
6. **First message back to Tom, before any code:** repeat §5 (his checklist) so he can
   create the credentials while you build. Then build without waiting.

## 1. Mission

**One sentence:** every lead that reaches GT's Facebook/Instagram forms lands in
`sales_core` within ~10 minutes, Tom gets a Hebrew email with customer context and a
portal link, nothing that Meta still holds from the last 90 days is lost, a converted
lead is marked `won` from Shopify order evidence automatically, and the pipeline can
never again die silently — a daily heartbeat tells Tom when it is broken **and** when it
is quiet.

Everything upstream (schema, import, workspace UI) and downstream (Today queue, outcome
loop) of this mission already shipped. This session closes the gap in the middle:
**intake and the closed loop.**

## 2. State as of 2026-08-23 — verify fresh at boot, do not trust this table blindly

| Piece | State 2026-08-23 | Evidence |
|---|---|---|
| `sales_core` schema (org / lead / lead_event, append-only, phone normalisation, `ingest_lead`) | LANDED | gt-factory-os migrations 0318–0321, PR #219, 43/43 pgTAP |
| Workspace data layer + admin-gated endpoints (`api/src/sales/**`) | LANDED | migrations 0322–0323, PR #220 |
| Workspace v2 backend (assignment, queue shape, attention, activity feed) | LANDED | migrations 0324–0327, PR #222 |
| Portal workspace `/apps` + `(sales)` route group (today / leads / orgs / attention / settings) | LANDED | portal PRs #213–#215, tranches 162–172 |
| Historical import | LANDED — 188 leads / 186 orgs in prod; latest lead `2026-08-09`; all 188 still `status='new'` | live SQL 2026-08-23 |
| **`sales-leads-poll` Edge Function (spec §6)** | **DOES NOT EXIST** — not in `supabase/functions/`, not deployed | repo grep + `list_edge_functions`, 2026-08-23 |
| **Close-the-loop job + heartbeat (spec §6.3)** | **DOES NOT EXIST** | same |
| Secrets `META_PAGE_ACCESS_TOKEN`, `RESEND_API_KEY` | **MISSING — Tom-only** (spec §6.5) | Sales-Machine `CURRENT_STATE.md` |

**The clock:** Meta retains leads 90 days. The intake has been dead since 2026-06-07;
99 leads arrived after that and were recovered only up to the 2026-08-10 export. The
earliest of those fall off Meta in early September — and every lead submitted after
2026-08-09 exists **only** at Meta right now. First live poll run must backfill the full
90-day window (idempotent dedupe on `unique (source, external_id)` makes overlap with the
import harmless — that is by design, spec §6.1).

## 3. Scope

**IN (this session):**
1. Spec Phase 3 — `sales-leads-poll` Supabase Edge Function: 10-minute poll route,
   `POST /ingest` bearer route, Resend alert on genuinely new leads, one alert per lead
   enforced by `lead_event(alert_sent)`. Spec §6.1, §6.2, §7, §10.
2. Spec Phase 4 — daily close-the-loop route (open leads × Shopify order check → `won` +
   `converted_order_ref` + `lead_event(converted)`) and the heartbeat email. Spec §6.3.
3. Scheduling + deploy: cron registration following the repo's existing secured pattern
   (study `shopify_available_reconcile` scheduling and migration 0309's auth approach);
   deploy via the existing `deploy-edge-function.yml` workflow. Deploy **dark** first —
   the function must be safe and inert while secrets are absent.
4. Live bring-up after Tom's secrets: backfill, field-mapping verification against one
   real fetched lead **before** any mapping is finalized (spec §6.1 — no field name
   assumed), test lead, six-layer evidence, induced-silence heartbeat test.
5. Documentation closure (§6 below).

**OUT (do not touch, do not "improve"):**
- Portal code. The workspace already renders whatever lands in `sales_core`.
- Any message to a lead or customer. `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` stays
  `false`. Imports and backfills never email (spec §8); only genuinely new live leads do.
- factory-os core schema, `stock_ledger`, `factory_os_jobs/index.ts` (frozen sentinels
  live there — schedule the daily route as a second cron on the sales function instead).
- The spreadsheets import (D13), the churn radar, Klaviyo or any new vendor, queue-shape
  product changes (U-011 is Tom's decision, not yours).
- Green Invoice.

## 4. Build plan — task level

Work TDD; keep each task's diff minimal; the spec carries the design so implement, don't
redesign. Suggested order:

1. **Recon (read-only):** spec in full; `db/migrations/0318`–`0327`; `api/src/sales/**`;
   `supabase/functions/shopify_available_reconcile/` (scheduling + auth pattern);
   existing Shopify read path used by the daily sales forecast (for the conversion
   check); `sales_core.app_setting` (migration 0322) — the natural home for the poll
   cursor. Verify live state per §2. Any surprise → `assumption_failure`, halt, report.
2. **Ingest core tests first:** unit tests (mocked Graph API + mocked Resend) for: field
   mapping incl. unknown-field alarm; cursor advance only after successful write; overlap
   idempotency; one-alert-per-lead; malformed payload rejected + logged; known-customer
   subject variant (`🔁`) vs new (`🟢`). pgTAP already covers schema rules — do not
   duplicate; add pgTAP only if a new DB object (cursor row, event type) needs it.
3. **Function:** `supabase/functions/sales-leads-poll/` with three routes: `poll`
   (10-min), `daily` (close-the-loop + heartbeat), `ingest` (bearer
   `LEAD_INGEST_TOKEN`). Missing secrets → clean no-op with a logged reason, never a
   crash loop. Resend sender is a small module inside this function — no Make (D10).
4. **Migration(s):** cron registration + any cursor/event-type rows. Follow
   `gt-factory-os/CLAUDE.md` migration bracket rule (list `db/migrations/` immediately
   before and after writing a numbered file; new file in between → HALT
   `contract_failure`).
5. **Deploy dark:** CI green, `deploy-edge-function.yml`, one-line announcement, verify
   the function responds and no-ops without secrets. Push, PR, merge when green.
6. **HARD STOP — credentials.** Generate `LEAD_INGEST_TOKEN` (random 32+ bytes), hand it
   to Tom with §5, and wait. Never ask Tom to paste `META_PAGE_ACCESS_TOKEN` or
   `RESEND_API_KEY` into chat — he sets them in the Supabase dashboard directly.
7. **Live bring-up:** confirm secrets present (health check — never print values). Fetch
   **one real lead** and verify field mapping against it before enabling the mapping
   (spec §2.3 is the cautionary tale). Set cursor to now−90d; run the backfill; report
   accepted / merged-duplicate / rejected counts and how many of the post-2026-08-09
   leads were recovered. Backfill sends no email.
8. **Prove it (spec §11):** Tom submits a test lead via Meta's Lead Ads Testing Tool →
   row in `lead` → `lead_event(created)` → email received by Tom → visible in portal
   Today queue → portal status change writes an event → exception paths (duplicate
   payload: no second lead, no second email; malformed payload rejected + logged).
   Induce silence (or simulate) to prove the heartbeat fires. Report N/N.
9. **Watch the first day:** before ending the session, self-schedule a check-in
   (`send_later`, ~2h and ~24h out) to confirm the 10-minute cron is actually running
   and the first heartbeat arrived.

## 5. Tom's part — the complete list; nothing else is yours

**A. Meta System User token (~10 min, only you have Business Manager admin):**
1. business.facebook.com → Settings (GTeveryday portfolio) → Users → **System users** →
   create (or reuse) a system user, role Employee is enough.
2. Assign assets: the GT Everyday **Facebook Page**, with full control of leads access.
3. Generate token: permissions **`leads_retrieval`** + `pages_show_list` +
   `pages_read_engagement`; expiry **never**. Copy it once.
4. Supabase dashboard → project `rvadsozabmxkkrktwgnv` → Edge Functions → Secrets →
   add `META_PAGE_ACCESS_TOKEN` = the token.

**B. Resend (~5 min):** sign up at resend.com with `tom@gteveryday.com` → create API
key → add secret `RESEND_API_KEY` the same way. (Domain SPF/DKIM can wait — sending to
your own address works immediately.)

**C. `LEAD_INGEST_TOKEN`:** the session will hand you a generated value — add it as the
third secret, same screen.

**D. Test lead (~2 min, after the session says "live"):**
developers.facebook.com/tools/lead-ads-testing → pick the GT page + live form → submit —
then confirm the email reached you and the lead shows in
gt-factory-os-portal.vercel.app/sales/today.

**E. Two product decisions (whenever, not blocking):**
- **U-011** — the Today queue holds all 188 imported leads because they are genuinely
  untouched. Decide: work the backlog down as a triage sprint, or cap the daily queue.
- **U-013** — with Alex: should the Facebook form ask for the business name again? (Live
  form is name/phone/email only, so orgs are inferred. Recommended: yes.)

**F. The part no system does:** the calls. The queue at `/sales/today` is the plan;
outcomes are one tap. That habit is the sales machine.

## 6. Documentation closure — the session finishes by writing, not just shipping

1. `Sales-Machine/CURRENT_STATE.md`: mark Live intake LANDED (dated, with PR + evidence
   pointers), mark Conversion job LANDED, update the side-track table, and fix the stale
   pointer that still calls the module declaration "PR #46 — DRAFT" (it is APPROVED
   2026-08-04, Amendment A APPROVED 2026-08-17 — see
   `production-brain/docs/decisions/modules/sales-declaration.md`).
2. `Sales-Machine/evidence/`: one dated snapshot — backfill counts, recovered-lead count,
   test-lead evidence, heartbeat proof.
3. Production-brain: append a Build-record row to
   `docs/decisions/modules/sales-declaration.md` (same style as the 2026-08-17 rows).
4. Every PASS claim carries the 8 PASS fields (production-brain `CLAUDE.md` §Evidence).

## 7. Halt conditions (beyond the constitutions')

- Meta responds with a shape the spec did not predict → `assumption_failure`: record the
  raw response, halt the mapping, surface to Tom.
- Any path would email a lead/customer, or flip any frozen flag → STOP.
- Secrets absent at bring-up → wait; never fake, never stub live evidence.
- A migration slot conflict per the bracket rule → `contract_failure`, halt.

## 8. Final report to Tom (Hebrew, short)

What went live, backfill numbers (accepted / merged / rejected / recovered-since-08-09),
six-layer evidence N/N, PRs merged, what remains his (§5 D–F leftovers), and the one next
action.
