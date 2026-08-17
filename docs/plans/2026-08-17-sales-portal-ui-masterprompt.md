# MASTERPROMPT — GT Sales Workspace: Plan Everything, Then Build Everything

> **Usage (Tom):** Paste this entire file as the first message of a fresh Claude Code
> session running a frontier model. The session executes **Phase A (planning)** and then
> **stops**. You then switch to a cheaper model (same session or a new one with the plan
> attached) and say "execute the plan" — **Phase B** builds it. Do not paste fragments;
> the file is deliberately self-contained.
>
> **Provenance:** Written 2026-08-17 in session `claude/sales-system-planning-th2gna`,
> after a full brainstorming pass with Tom locked every product decision below. This
> revision supersedes the earlier same-day revision of this file (git history has it).
> Deep design spec: `docs/superpowers/specs/2026-08-10-sales-leads-pipeline-design.md`.

---

## 0. Operating instructions — read before anything else

1. **Two phases, hard stop between them.**
   - **Phase A — PLAN (you, now, frontier model):** produce a complete, code-level
     implementation plan plus all governance artifacts. Then STOP and tell Tom to switch
     models. Phase A writes documents and governance records only — **no product code.**
   - **Phase B — EXECUTE (cheaper model, later):** follow the plan task-by-task with
     test-driven discipline. Phase B must never need to make a product decision; if it
     does, the plan failed — it should surface the question instead of guessing.
2. **Skills are mandatory, not suggestions.** This project carries the Superpowers skill
   suite plus portal-specific gates. Use exactly these, at these moments:

   | Moment | Skill / tool | Why |
   |---|---|---|
   | Session start | `using-superpowers` | establishes skill discipline |
   | Phase A planning | `superpowers:writing-plans` | the plan document, bite-sized TDD tasks, zero placeholders |
   | Phase B execution | `superpowers:executing-plans` | batch execution with checkpoints (cheapest reliable mode for a non-frontier model) |
   | Every implementation task | `superpowers:test-driven-development` | failing test first, always |
   | Before any "done" claim | `superpowers:verification-before-completion` | evidence before assertions |
   | Every UI surface, before coding it | `impeccable` → `shape` | UX plan per screen (installed in Phase B task 1) |
   | After all UI lands | `impeccable` → `audit`, `polish`, `harden` | quality floor, edge cases, error states |
   | After touching any shell/nav file | `/portal-regression-guard` | factory surfaces must not drift |
   | End of Phase B | `portal-tranche-verifier` agent + `/portal-scorecard` | certification with evidence |

   Do **not** use `brainstorming` — it already happened; this document is its output and
   Tom approved every decision in it. Do not re-litigate decisions marked LOCKED.
3. **Authority order:** production-brain `CLAUDE.md` → portal `CLAUDE.md` (tranches,
   hooks, UI language) → this file → the plan you write. On conflict, higher wins; if
   this file conflicts with a repo constitution, STOP and surface it.
4. **Language:** all user-facing UI copy in the sales workspace is Hebrew (authorized
   below). All code, comments, commit messages, PR bodies, and docs are English.

## 1. Mission and definition of success

Build the **GT Sales Workspace** inside the existing portal — a world-class,
workflow-first CRM surface in the structural style of monday.com but with GT's own
quieter identity, for a single heavy user today and multiple agents tomorrow.

**Success is one sentence:** Tom logs in on his phone, picks "מכירות", and lands on a
**Today queue** that tells him exactly what to do now — call these two new leads, follow
up on these three, one returning customer needs attention; every call ends with a
one-tap outcome that schedules the next touch; the full lead list, the business pages,
search, and quick-add are one tap away; and the whole thing looks and feels like a
product a top-tier SaaS company shipped, in Hebrew RTL, on real data (188 leads already
live in production).

## 2. What already exists — verified 2026-08-17. Build on it; do not rebuild it.

1. **Schema `sales_core` is live in production** (Supabase project
   `rvadsozabmxkkrktwgnv`, gt-ops-prod): tables `org` / `lead` / `lead_event`
   (append-only, trigger-enforced), Israeli phone normalisation on write, and a single
   write path `sales_core.ingest_lead(...)`. Migrations 0318–0321, 43/43 pgTAP green.
2. **188 real leads are in the database** (`source='import_meta_export'`), 2023-06-18 →
   2026-08-09. 99 of them arrived after the old intake died (2026-06-07) and were never
   seen by a human. 39 old organic rows have no phone/email (uncontactable history).
   2 rows carry `possible_duplicate_of`. 3 orgs are matched to existing customers with a
   dated snapshot in `org.shopify_snapshot` / `org.shopify_snapshot_at` — one of them
   (ליוניל יזמות / פטיו) is a churned customer who re-filled the lead form and got
   silence. That row is the emotional proof of this build.
3. **Rules live in the schema, not the UI:** `status='won'` requires
   `converted_order_ref` (a Shopify order proves winning; there is no "won" button
   anywhere, ever). `status='lost'` requires `lost_reason`. Statuses:
   `new` / `working` / `won` / `lost`. The `lead_event.event_type` CHECK currently
   allows: `created`, `status_change`, `note`, `assignment`, `next_touch_set`,
   `alert_sent`, `converted`, `matched_existing_customer`, `imported` — it MAY be
   extended additively by migration (never remove a value).
4. **Draft PRs open:** production-brain **#127** (spec + plans), gt-factory-os **#219**
   (migrations + import evidence). Both on branch `claude/sales-system-planning-th2gna`.
5. **Not built yet:** anything in the portal (`(sales)` route group, `/apps`), the
   `api_read` views for sales, mutation functions, and the live Meta intake + Resend
   alert (a separate track waiting on Tom's credentials — explicitly OUT of your scope).
6. **Portal facts you may rely on:** Next.js 15 App Router, Tailwind **3.4** (CSS
   variables + shadcn/ui, no Tailwind 4 assumptions), TanStack Query, Supabase SSR auth,
   Playwright + vitest configured. The public root page `/` is deliberately static
   (Tranche 018 — do not touch). Route groups today: `(admin) (auth) (economics) (inbox)
   (ops) (planner) (planning) (po) (production) (shared)`. Portal governance: every
   change scoped to one tranche with a full file manifest (a PreToolUse hook enforces
   it), evidence required on every "done", and a Stop hook requires ending responses
   with "Next action: …".

## 3. Authorizations — Tom pasting this file constitutes written approval of exactly these

1. **Merge draft PRs #127 (production-brain) and #219 (gt-factory-os)** after verifying
   clean merge state. This makes `main` your base. First action of Phase A.
2. **Record Amendment A as APPROVED** in
   `docs/decisions/modules/sales-declaration.md` (production-brain), dated, referencing
   the 2026-08-07 masterprompt and this file. Record this build there too.
3. **Add one row to the Hebrew-exception table in the portal `CLAUDE.md`** (Tom is that
   file's sole writer; this row is written under his explicit authorization, verbatim):
   `| /apps + route group (sales) — all screens | sales workspace, Hebrew-first | 2026-08-17 |`
4. **Adopt the `impeccable` design skill** (Apache-2.0) into the portal repo, vendored
   and committed, with a third-party notice file.
5. **Create the `(sales)` shell and a new additive tokens file** as specified in §6.
   `globals.css`, `tailwind.config.ts`, and UX-standard files stay untouched.

Frozen flags stay frozen. `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` stays `false`.
Nothing is ever sent to a lead or customer. `stock_ledger` / `balance_anchors` /
factory-os core schema: never touched.

## 4. Repos to attach (add_repo)

| Repo | Role in this build |
|---|---|
| `tomw200082-collab/gt-factory-os-portal` | the build itself |
| `tomw200082-collab/gt-factory-os` | views + mutation functions migration |
| `tomw200082-collab/gt-factory-os-production-brain` | governance, spec, decision records |
| `tomw200082-collab/Sales-Machine` | update `CURRENT_STATE.md` at the end only |

## 5. Product specification — every item below is LOCKED (Tom, 2026-08-17)

### 5.1 Information architecture — three screens, no more

```
/sales/today   ← HOME. The work queue. (/sales redirects here)
/sales/leads   ← the full table: status tabs, search, filters, drawer
/sales/orgs    ← businesses (the 186 lead-born orgs): account card + timeline
/sales/settings← minimal: WhatsApp templates + SLA parameter. Nothing else.
```

- **Mobile (primary):** bottom tab bar — היום · לידים · עסקים. Settings via a menu.
- **Desktop:** slim sidebar, same three sections; **⌘K** command palette for navigation
  and global search.
- **Do not build:** a reports/insights screen (a thin stats strip on Today covers it),
  customer import of the full 560-customer base (the tracker serves them; the future
  churn radar decides its own needs), agent management UI, permissions UI.

### 5.2 The Today queue — the product's heart

A CRM fails as a database you visit; it succeeds as a queue that tells you what to do.
The queue is **computed per assignee from day one** (leads where
`assignee = current user OR assignee IS NULL`; admins see everything plus an
assignee filter) — zero extra UI today, zero rework when Erik joins.

**Item types, in display order:**
1. **🎉 Conversions** — leads newly marked `won` by order evidence (from
   `lead_event.converted` since last visit). Celebratory card: business, order ref,
   amount. This is the reason to open the app in the morning.
2. **לקוח חוזר** — a new lead whose org is an existing customer
   (`matched_existing_customer`). Highest-urgency actionable card, visually distinct:
   show the customer context (₪/yr from the dated snapshot, last order, churn status).
   The Patio case, never silent again.
3. **New leads** — `status='new'`, no first touch yet. SLA clock visible.
4. **Due follow-ups** — `next_touch_at <= now`, oldest first.
5. Nothing else. When the queue is empty: a designed **"סיימת להיום ✓"** state.

**Stats strip** at the top: `השבוע: X לידים · Y בטיפול · Z הומרו`. One line, no charts.

### 5.3 The one-tap outcome loop — the discipline mechanic

Every actionable card carries: **התקשר** (`tel:`) · **וואטסאפ** (`wa.me` with a
pre-filled template — see 5.7) · **דחה** · **אבוד**. Tapping call/WhatsApp records an
outreach intent; when the user returns to the app (visibility/focus), a **single
outcome sheet** appears with four large buttons:

- **ענה, מתקדם** → status `working` if `new`; pick next touch in one tap
  (מחר / עוד 3 ימים / עוד שבוע / תאריך).
- **לא ענה** → auto-schedules retry tomorrow, stays in queue.
- **וואטסאפ נשלח** → next touch in 2 days.
- **אבוד** → reason picker (required), lead leaves the queue.

Mechanics (enforced, not hoped for):
- A queue item is cleared **only** by a captured outcome. No "handled, roughly".
- Every recorded outcome writes its `lead_event`s and a `next_touch_at` in one
  transaction — an open lead without a next-touch date cannot exist after any touch.
- The **first** outcome/note/status-change on a lead sets `first_touch_at` (stops SLA).
- SLA badge: green under the SLA parameter (default 24h) from `created_at`, red past
  it, **shown only until first touch** — after that the badge disappears (a timer on
  everything means a timer on nothing).
- Event types: extend the CHECK additively (migration) with `outreach`
  (payload: channel) and `outcome` (payload: result) rather than overloading `note`.

### 5.4 Leads screen — the full table

- Status tabs with Hebrew display labels (schema values unchanged):
  חדש / בטיפול / הומר ✓ / אבוד. Counts on tabs.
- Row: business name (anchor, sticky start-column) · contact · phone · campaign/platform
  · lead age · SLA badge (per 5.3 rule) · לקוח-קיים badge (with ₪/yr when snapshot
  exists) · next-touch date · subtle duplicate badge when `possible_duplicate_of` set.
- Default sort: new + overdue-next-touch on top. Search field always visible
  (name / business / phone — phone matching goes through normalisation).
- **Drawer, not a page** (opens from inline-end; use CSS logical properties everywhere):
  all fields · full `lead_event` timeline in Hebrew · actions: status (בטיפול /
  אבוד+reason modal), add note, set next touch, assignee (free text for now) ·
  `tel:` / `wa.me` / `mailto:` links · `won` shown as an evidence banner with order ref
  — never a button.
- Multi-select + bulk status action **only if trivially cheap**; otherwise defer and
  record the deferral.

### 5.5 Orgs screen — thin account pages

- List of the 186 lead-born orgs: name, phone, customer badge, lead count, last
  activity. Same search.
- Account card (drawer or page — plan decides): identity fields · its leads · Shopify
  snapshot context (dated, from `org.shopify_snapshot`) · merged event timeline.
- This is the seam churn-radar/whitespace/account-value plug into later. Do not build
  those. Do not import the 560-customer base.

### 5.6 Quick-add, global search, PWA

- **"+ ליד חדש"** floating action (mobile) / button (desktop): contact name (required),
  phone, business name, free-text source note. Writes through
  `sales_core.ingest_lead` with `source='manual'` and a generated external id. Ten
  seconds, three fields, done — leads that arrive by phone or word-of-mouth must not
  stay invisible.
- **Global search** (⌘K + mobile search screen): leads + orgs by name/business/phone/
  email. Pasting an unknown caller's number answers "who is this?" instantly.
- **PWA:** installable — manifest (name "GT Sales", start_url `/sales/today`, standalone
  display, GT icons), scoped so it does not conflict with any existing portal manifest
  (discover first). Full-screen app feel on Tom's phone.

### 5.7 Settings — exactly two things

- **WhatsApp templates:** editable message templates by context (ליד חדש / תזכורת /
  לקוח חוזר), stored in a small `sales_core.app_setting` key-value table (jsonb),
  seeded with sensible Hebrew defaults. Used by the wa.me buttons.
- **SLA hours:** numeric parameter, default 24 (spec S-01), same table.
- Nothing else on this screen. Resist.

### 5.8 Visual language — "monday's structure, GT's identity"

- Take monday's **structure**: colored status pill as the row's visual anchor · dense
  grouped tables with sticky headers · side panel over navigation · always-visible
  search · a bulk-action bar on multi-select · exactly one strong accent color for the
  single primary action per screen.
- Reject monday's **identity**: no color-everywhere (noise for a single heavy user),
  no monday palette or logo. Color is reserved for **status and SLA only**. White
  surfaces, hairline borders, an 8px spacing grid, motion 150–200ms with intent.
- Typography: **Rubik** (excellent Hebrew, already used in GT materials),
  `font-variant-numeric: tabular-nums` on every number/date column.
- Hebrew RTL throughout via `dir="rtl"` + CSS logical properties (no `left`/`right`
  physical properties in new code).
- First-party reference allowed: monday's Vibe design system is MIT
  (`vibe.monday.com`) — mine it for measurements and patterns. Do NOT install the
  library, do NOT copy its CSS wholesale. Never copy AGPL/GPL code (Twenty, EspoCRM,
  Frappe); visual inspiration from anything is free.
- Empty / loading / error states are **designed on purpose** (impeccable
  `onboard`/`harden`) — including per-tab empty states and a network-error state with
  retry.

### 5.9 Explicitly deferred (recorded so nobody "helpfully" builds them)

Call-script cards (doctrine not yet Tom-verified) · manual duplicate merge · lost-reason
analytics · full keyboard model beyond ⌘K/Esc/Enter · reports screen · agent management
· any Meta/Resend intake work (separate track) · importing the 560-customer base.

## 6. Technical architecture — LOCKED

### 6.1 Shell split

- **`/apps`** — post-login switchboard: two large cards, **ייצור** / **מכירות**.
  Remembers last choice (cookie) and offers direct skip. Only roles with sales access
  see the sales card (today: admin; discover the portal's role mechanism in
  `app_users` + middleware and gate minimally). Other roles' login flow unchanged.
  Discover how the current post-login redirect works and change it minimally.
- **`src/app/(sales)/`** route group with its own `layout.tsx`: `dir="rtl"`, `lang="he"`,
  `data-app="sales"` on the wrapper, its own navigation chrome. Factory groups untouched.
- **Tokens:** new file `src/app/(sales)/sales-tokens.css`, imported only by the sales
  layout, all variables scoped under `[data-app="sales"]`. shadcn components consume the
  CSS variables. **Never edit** `globals.css`, `tailwind.config.ts`, or UX-standard docs.

### 6.2 Data layer

- **Reads:** new migration(s) in `gt-factory-os` (next free number after #219 merges —
  verify; expected 0322+) creating `api_read` views following the repo's existing
  view/grant pattern exactly (discover it from existing `api_read` migrations first):
  `v_sales_leads` (lead + org name + customer badge fields + derived age/SLA/overdue),
  `v_sales_lead_events`, `v_sales_orgs`, `v_sales_today` (the queue, per-assignee),
  `v_sales_week_stats` (the stats strip).
- **Writes:** SQL functions in `sales_core`, each writing the change + its
  `lead_event`(s) transactionally: `set_lead_status(lead_id, status, reason, actor)`
  (rejects `won` — only the future conversion job writes that),
  `add_lead_note(lead_id, note, actor)`, `set_next_touch(lead_id, at, actor)`,
  `assign_lead(lead_id, assignee, actor)`, `record_outreach(lead_id, channel, actor)`,
  `record_outcome(lead_id, result, next_touch_at, reason, actor)` (implements the whole
  5.3 loop server-side, including first_touch and the no-open-lead-without-next-touch
  rule). pgTAP on all of them, including the `won` rejection. **pgTAP 1.3.3 gotcha**
  (documented in existing test headers): the schema-qualified assertion form always
  takes one extra argument — `has_column('sales_core','org','x')` tests a table named
  `sales_core`.
- **Portal access:** discover how existing portal screens read and mutate (Supabase
  client? API routes? Fastify?) and follow that exact pattern. Do not invent a new
  data-access layer. TanStack Query for caching, optimistic updates on the outcome loop.
- Personal data discipline: no lead names/phones in commits, PR bodies, screenshots
  cropped or on non-sensitive rows where possible, no CSV files in git.

### 6.3 Quality gates

- TDD per task (failing test first). vitest + typecheck clean. Playwright on the
  critical path: queue renders → outcome captured → event written; list renders → tab
  switch → drawer → status change → event written. Discover how existing Playwright
  tests provision data and mimic exactly.
- End-to-end evidence with **real data**: screenshots (desktop + mobile) of Today with
  the real queue, Leads with 188 rows, a drawer open, org card, empty states; a SQL
  query showing the `lead_event` row a UI action created.
- `/portal-regression-guard` green after shell changes; `portal-tranche-verifier` +
  `/portal-scorecard` at the end. Factory scorecard must not regress.

## 7. PHASE A — what you produce now (planning only)

1. **Governance first:** merge #127 + #219 (authorized above). Record Amendment A.
   Add the Hebrew-exception row. Open a **new tranche** in `docs/portal-os/tranches/`
   (next free number) with the **complete file manifest** — the PreToolUse hook enforces
   it; every file Phase B will touch must be listed, including
   `.claude/skills/impeccable/**`, `PRODUCT.md`, all `(sales)` files, `/apps`, manifest/
   icons, and the portal `CLAUDE.md` row. Update `_active.txt`.
2. **Write the implementation plan** with `superpowers:writing-plans` to
   `docs/superpowers/plans/2026-08-17-sales-workspace-implementation.md`
   (production-brain). Requirements: bite-sized tasks (one TDD cycle each), exact file
   paths, real code in every step (the writing-plans skill bans placeholders), exact
   impeccable commands scheduled per UI task (`shape` before each screen; `audit`,
   `polish`, `harden` as the final tasks), the migration SQL drafted in full, the view
   SQL drafted in full, Playwright specs drafted. Order the tasks: impeccable install →
   data layer (migrations + pgTAP) → tokens + shell + `/apps` → Today queue + outcome
   loop → Leads + drawer → Orgs → quick-add + search + PWA → settings → quality pass →
   PRs + state updates. Each task independently verifiable.
3. **Self-review** the plan against §5–§6 (spec coverage, placeholder scan, type
   consistency across tasks), fix inline, commit, push, open/update the draft PR.
4. **STOP.** Print: the plan path, the tranche number, and this exact instruction to
   Tom: *"The plan is complete and committed. Switch to a cheaper model and tell the
   session to execute the plan with superpowers:executing-plans."* End with the portal's
   required "Next action: …" line. Do not begin Phase B yourself.

## 8. PHASE B — how the executor works (cheaper model)

1. Invoke `superpowers:executing-plans`. Read the plan. Execute in order, one task at a
   time, TDD cycle per task, committing per task with clear messages (no model names in
   commits/PRs). First task installs impeccable:
   `npx impeccable install --providers=claude --scope=project`, commit the vendored
   skill + hook manifest, add `docs/third-party/impeccable-NOTICE.md` (Apache-2.0,
   version), run `/impeccable init` (writes `PRODUCT.md` — a new file, allowed).
2. Never leave the tranche manifest. Never edit forbidden files. If a task cannot
   proceed as written, STOP and report — do not improvise product decisions.
3. Use `superpowers:verification-before-completion` before claiming any task done, and
   before the final report. Screenshots at the milestones the plan marks.
4. Finish: draft PRs (portal + gt-factory-os) with screenshots in the body, update
   `Sales-Machine/CURRENT_STATE.md` and the sales-declaration build record, and report
   with the 8 PASS fields (files changed · tests N/N · contracts referenced · signals
   emitted · stop conditions tripped · Tom approvals required · rollback plan · next
   handoff).

## 9. Boundaries — never, in either phase

- Touch `globals.css`, `tailwind.config.ts`, UX-standard files, factory route groups,
  the public `/` page, or anything outside the tranche manifest.
- Build Meta intake, Resend email, or anything that sends to a lead/customer.
- Install UI libraries (Vibe/MUI/AntD/…) — shadcn + tokens only. impeccable is
  dev-tooling, not a runtime dependency.
- Copy AGPL/GPL-licensed code. `git add -A` / `git add .`. Push to `main` outside the
  §3 authorizations. Non-draft PRs.
- Re-decide anything marked LOCKED. Ship an English string on a sales screen.

## 10. Open items for Tom (surface at the end; none block this build)

- Meta System User token + Resend API key (the live-intake track; the 90-day lead
  retention clock is running — earliest unseen leads expire early September).
- S-01 SLA hours (parameter, default 24) · S-04 add business-name question back to the
  Facebook form · U-011 Erik's role and assignment flow.
