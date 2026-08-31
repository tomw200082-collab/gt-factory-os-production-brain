# MASTERPROMPT — GT social presence: from scattered accounts to one publishable base

**STATUS: SHIPPED — 2026-08-31**

> **Usage (Tom):** paste this whole file as the first message of a fresh Claude Code
> session with `gt-factory-os-production-brain` and `Sales-Machine` attached, and the
> Google, Dropbox, Shopify and Canva connectors on. It takes GT's public accounts from
> "eleven properties nobody owns" to "one verified base with a credentials sheet and a
> content calendar." It halts for you only where §6 says.
>
> **Provenance:** written 2026-08-31 from the live artifact `מפת הדרכים הדיגיטלית`
> (`https://claude.ai/code/artifact/09e806f6-978b-46d3-8374-eb36379710fa`, state read
> 2026-08-31: 72 tracked tasks, 8 marked done), whose own findings were measured
> 2026-08-26 against Shopify, Google and the live site. Authority:
> `gt-factory-os-production-brain/CLAUDE.md` and `Sales-Machine/CLAUDE.md` — cited, never
> copied.
>
> **Shelf life:** §2 is presumed stale after 2026-09-21. Re-read the artifact state first
> (§2.5). If reality no longer matches §2 — **adapt and record the delta in the artifact
> note field**; do not halt.

---

## 0. How to work

- **Who you are here:** one Claude Code session, frontier model, running alone. You hold
  Google Workspace (Drive/Calendar/Gmail), Dropbox, Shopify Admin API, Canva and GitHub.
  You do **not** hold Meta Business, Instagram, LinkedIn, YouTube or TikTok credentials —
  that asymmetry is the whole shape of this job. You decide anything that is reversible
  and internal. You decide nothing that posts publicly or spends money.
- **Read first, in order:** `gt-factory-os-production-brain/CLAUDE.md` ·
  `Sales-Machine/CLAUDE.md` · the artifact above, in full, including every `note` field ·
  `docs/warehouses/marketing-assets.md` (what imagery already exists and what is a known
  gap) · `docs/ceo/reference/people_rhythm.md` (who is who, and who is unavailable when).
- **Authority:** where this document and an authority doc disagree, the authority doc
  wins and this document is wrong. Halt conditions, evidence standard and git discipline
  are inherited from `gt-factory-os-production-brain/CLAUDE.md` §Stop conditions and
  §Evidence — not re-authored here. §8 lists only the additions.
- **The standard.** Tom asked for `בסיס אימתני שנוכל לעבוד איתו בעתיד` — a base solid
  enough to build on. Translated into three prohibitions you can be caught breaking:
  1. **Nothing published may be unowned.** If GT cannot log into it and change it
     tomorrow without asking a third party, it is not part of the base — it is a
     liability, and it goes on the risk list instead of the asset list.
  2. **Nothing on the credentials sheet may be a guess.** Every row is either verified
     against the live property today, or marked `לא אומת` with the reason.
  3. **No secret value is ever written to this repo, a commit, a PR, or a chat message.**
- **Language:** this document is English because that is the register you reason best in;
  every data literal stays in its own script inside backticks and is never translated.
  **Output language: concise Hebrew for anything Tom reads; concise English for
  everything else.** Short sentences. No preamble.

---

## 1. Mission and definition of done

**One testable sentence:** every public GT property is identified, owned, correctly
described, and recorded in one credentials sheet Tom can hand to a new employee — and a
90-day content calendar exists that a person can execute without asking a question.

| # | Condition | The observation that would prove it false |
|---|---|---|
| D1 | Every property in §2.1 has a row in `GT — כרטיס גישה` (Google Sheets, Tom's Drive) with owner, admin, auth method, MFA state, recovery address, renewal date, last-verified date | Open the sheet; any row with an empty `בעלים` or `אומת בתאריך` column, or any property from §2.1 with no row at all |
| D2 | Zero contradictions between properties on the four identity fields — legal name, address, phone, website | Grep every property's public profile for `072-3939395` and for any phone that is not the number decided in §6.A. One hit = fail |
| D3 | The duplicate-account question is closed on Instagram: exactly one account is public and active, the other is closed or redirects | Both handles opened in a browser; two live accounts carrying the brand = fail |
| D4 | LinkedIn company page exists, is populated, and Tom's personal profile links to it | Open the page URL: a missing page, or a stub with an empty About section, is the failure |
| D5 | A 90-day content calendar exists in the repo with one row per post: date, platform, format, asset path, caption, owner — and the first 14 days' assets exist as files | Open the calendar; any row in the first 14 days whose `asset` path does not resolve to a real file = fail |
| D6 | The Meta connection expiry of `2026-10-23` has a calendar event **and** a named human owner who confirmed they will act on it | The calendar event exists with an attendee who is not Claude |
| D7 | The artifact's task state is updated: every task you completed is marked done with a dated note naming what was verified | Open the artifact; a task you did with `done:false` or an empty note = fail |

Anything not on this list is out of scope unless Tom asks.

### 1.1 Settled — do not reopen

- **The artifact is the tracker.** Do not build a second one, do not migrate it to Notion,
  do not "upgrade" it to a new format. It already carries 72 tasks and eight completions
  with dated evidence. You write into it.
- **WhatsApp is the order channel** (artifact section `wa`, tagged `ערוץ ההזמנות בפועל`). Not a
  social network to be "grown". Its tasks are operational, not marketing.
- **The primary phone is `054-398-2444`** unless §6.A changes it. The old
  `072-3939395` is dead and gets removed everywhere it is found.
- **Google Business Profile is verified** (`g2`, done 2026-08-26). Do not redo it.

---

## 2. Ground truth — read 2026-08-31; re-verify at boot

### 2.1 The eleven properties, and what is actually known about each

| Property | State on 2026-08-26 | Who holds it |
|---|---|---|
| WhatsApp Business `054-398-2444` | live, is the real order line | `דורין` — **going on maternity leave; Tom takes over temporarily** |
| WhatsApp Business `054-758-8132` | second number, already carries a product catalog | Tom. **Purpose undecided** — artifact task `wa8` |
| Instagram `@greenteaeveryday` / `@gteveryday` | two accounts carry the brand; one has zero posts and follows hundreds | **unknown — possibly compromised.** Artifact `i1` calls this a red flag |
| Facebook page + Meta Business | live, running the lead form | **GT holds no admin.** Artifact `f2` |
| Meta ↔ Make connection | valid until **`2026-10-23`** | expiry is a calendar event (`f1`, done) |
| LinkedIn | **does not exist** | — |
| YouTube `@greenteaeveryday5540` | exists, has at least one live video, handle never customised | access unverified |
| Google Business Profile | verified `2026-08-26` | GT |
| Google Search / SEO | brand-name search only; **zero category presence** (`g6`, measured) | — |
| Email — Shopify segment `Email subscribers` | **2,969 profiles** (measured `2026-08-26`) | GT |
| Yotpo (reviews + loyalty) | **already installed and running** on `/pages/reviews` and `/pages/rewards-page` | GT — usage unknown |
| TikTok / X | brand name **not claimed** | — |

### 2.2 The eight tasks already done — do not redo them

`wa1` (mapped the numbers) · `wa2` (backup taken) · `wa2b` (device routing decided) ·
`wa3` (business profile filled) · `g2` (Google Business Profile verified) · `g6` (search
visibility measured) · `f1` (Meta expiry in calendar, 14-day + 10-hour alerts) ·
`z4` (monthly maintenance round created, recurring from `2026-09-06` 09:00).

### 2.3 What is NOT built

No credentials sheet. No brand kit files (the Drive folder was created `2026-08-26`, the
files were never uploaded — task `id5`). No LinkedIn presence at all. No content
calendar. No Instagram highlights. No YouTube branding. No decision on the second
WhatsApp number. No Meta Business admin.

### 2.4 Known-broken, adjacent, out of scope

- **Leads from the site currently go to HubSpot** (found `2026-08-26`, artifact `id4`) —
  a CRM that appears in no plan and that nobody has confirmed anyone reads. **Record it,
  do not fix it.** It belongs to the website masterprompt
  (`docs/plans/2026-08-31-website-hebrew-masterprompt.md`).
- **Five blog posts** carry spelling errors and regulatory health claims
  (`מפחית סיכון לסרטן`) — artifact `s2`. Record; the website session owns the fix.
- **The Shopify catalog** — the artifact's task `s7` audit (`2026-08-26`, read-only)
  counted 377 products, 253 archived. Not yours.

### 2.5 Re-verification block — run this before planning anything

1. Re-read the artifact with `Artifact action:"read"` on the URL above and diff its task
   state against §2.2. Tom may have ticked things since.
2. `mcp__Shopify__graphql_query` — re-count the email-consent segment; `2,969` is dated.
3. Open the two Instagram handles and record what you can see without logging in.
4. Confirm the `2026-10-23` calendar event still exists and now has a human attendee.

---

## 3. What the hard part actually is

**It looks like:** eleven accounts to tidy up.

**It actually is:** an ownership audit wearing a marketing costume. Every genuinely hard
item on this list is a question of *who can log in* — the possibly-hijacked Instagram
account, the Meta Business admin GT does not have, the YouTube channel nobody has opened,
the second WhatsApp number with a catalog on it that nobody decided the purpose of. The
content calendar is the easy half and it is worth nothing until the accounts are owned:
posting into an account you cannot recover is building on someone else's land.

**What that changes about the ordering:** do the ownership sweep first and completely,
before writing a single caption. Where ownership cannot be established, the property does
not get content — it gets a row on the risk list and a line in §6.

**Second reframe:** GT does not have a social media problem, it has a *findability*
problem. Task `g6` measured it: GT appears when someone searches the brand name and
never when someone searches the category. A café owner who has never heard of GT cannot
find it at all. Instagram follower counts do not fix that; the LinkedIn page, the Google
Business Profile and the category-search content do. Weight the plan accordingly — this
is a B2B wholesale business selling to purchasing managers, not a consumer brand.

**Third reframe:** the `2026-10-23` Meta expiry is not an admin chore. The identical
failure — a silently expired Meta connection — stopped GT's lead flow on `2026-06-07` and
went undetected for two months (`Sales-Machine/doctrine/decisions.md` D-006). It is the
single highest-consequence date in this document and it needs a human owner, not a
reminder.

---

## 4. Workstreams

### W1 — The ownership sweep (do this first, finish it before W3)

For each of the eleven properties in §2.1, establish and record: can GT log in today ·
who is the admin · is MFA on and on whose device · what is the recovery email and phone ·
does anything expire, and when.

Where you can verify through a connector you hold, verify it and cite what you ran. Where
you cannot (Instagram, Meta, LinkedIn, YouTube, TikTok, X), write the exact steps Tom
takes and what he must report back — one line each, no essays.

**Acceptance:** D1. Every row is verified or explicitly marked `לא אומת` with a reason.

### W2 — The credentials sheet — `GT — כרטיס גישה`

Build it as a Google Sheet in Tom's Drive (not in this repo, not as a committed file).
One row per property. Columns, in this order and with these exact headers:

`נכס` · `כתובת/ידית` · `בעלים עסקי` · `אדמין טכני` · `שיטת התחברות` ·
`שם הרשומה במנהל הסיסמאות` · `2FA` · `מייל שחזור` · `טלפון שחזור` · `תאריך תפוגה` ·
`אומת בתאריך` · `סיכון`

**There is no password column, and that is deliberate.** A shared sheet holding live
passwords is a breach waiting for one wrong share-link — and Tom already has an account
he suspects was compromised (§2.1, Instagram). The sheet points at a password-manager
entry by name; the secret lives there. Tom fills that manager himself (§6.D); you never
see a value. Say this to Tom in one sentence when you deliver the sheet — state it, do
not argue it — and if he still wants the values in the sheet, that is his call to make
and yours to record, not to override.

Second tab, `סיכונים`: every property GT cannot currently log into, what is at stake, and
what it costs to recover.

**Acceptance:** D1.

### W3 — Identity consistency

One identity card, applied everywhere. Source it from the Drive document Claude created
on `2026-08-26` (linked in artifact task `id1`) — that document already carries the four
contradictions, marked.

Sweep every property for the dead `072-3939395`, for the wrong legal name, and for a
missing or wrong address. Three published pages were already fixed on `2026-08-26`; the
artifact records which. Fix what you can reach; list what you cannot.

**Acceptance:** D2.

### W4 — Instagram, LinkedIn, YouTube

- **Instagram** — resolve the duplicate first (§6.B; you cannot do this without a login).
  Once resolved: convert to Professional/Business, category `מזון ומשקאות`, link to the
  Facebook page, add the WhatsApp action button, write the bio, build four highlight
  covers in Canva in the brand palette (`docs/warehouses/marketing-assets.md`, section
  `לוגו, פונטים, פלטה, DNA`), and record the opening baseline so a 90-day comparison works.
- **LinkedIn** — this is the highest-value new property in the document and the cheapest
  to build. A purchasing manager at a chain checks LinkedIn before approving a new
  supplier; GT currently reads as nonexistent there. Draft the company page in full
  (About in 3–4 paragraphs, industry `מזון ומשקאות`, logo, cover) and Tom's personal
  headline and About. Prepare everything; Tom clicks create (§6.C).
- **YouTube** — the handle `@greenteaeveryday5540` with its auto-generated suffix tells
  every visitor the channel was never set up. Fix branding, then recycle three existing
  drink-preparation videos as Shorts. **Do not shoot anything new.**

**Acceptance:** D3, D4.

### W5 — The 90-day content calendar

Write it to `Sales-Machine/doctrine/playbooks/social-calendar-2026-Q4.md`. One row per
post: `date · platform · format · asset path · caption (Hebrew, final) · owner · goal`.

Rules that make it executable rather than aspirational:
- **Two posts a week, not five.** A cadence that survives a busy week beats one that
  collapses in three weeks and takes the account's credibility with it.
- **Every asset already exists** — pull from `docs/warehouses/marketing-assets.md` and the
  category menus being built in
  `docs/plans/2026-08-31-category-menus-masterprompt.md`. A calendar that requires a photo
  shoot before week one is a calendar that does not start. Where the warehouse records a
  gap (no matcha-kit photo exists anywhere), route around it — do not schedule it.
- **B2B first.** Content that helps a café owner decide (margin per cup, prep in ten
  seconds, what the category does to an afternoon menu) outranks lifestyle photography.
- Every caption ends in the same call to action, pointing at the same WhatsApp link.

**Acceptance:** D5.

### W6 — Write the state back

Update every task you touched in the artifact: `done` where finished, and a note in the
same style as the existing ones — dated, naming what was verified and how. Then publish
the artifact to the same URL.

**Acceptance:** D7.

---

## 5. Scope

**IN:** everything in §4.

**OUT — do not touch, do not "improve":**
- The website and the Shopify storefront — artifact sections `web` and `shop` belong to
  `docs/plans/2026-08-31-website-hebrew-masterprompt.md`. You will be tempted, because
  they sit in the same artifact. Do not.
- The lead pipeline, `sales_core`, and anything in `gt-factory-os` — that is
  `docs/plans/2026-08-31-lead-response-system-masterprompt.md`.
- Paid advertising. No campaign is created, edited or paused here.
- **Posting anything publicly.** You draft; a human publishes. Every account in this
  document is customer-facing, and `Sales-Machine/CLAUDE.md` §Write boundaries puts
  customer-facing writes behind `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED`, which is `false`.
- The `700 לקוחות` and `8 שנים` claims. They appear in existing copy; they are being
  sourced in `docs/plans/2026-08-31-knowledge-book-masterprompt.md`. Reuse the existing
  wording, do not invent a new number.

---

## 6. Tom's part — the complete list, nothing else is yours

**A. Decide what `054-758-8132` is for.** It already has a product catalog on it and it
is in your hand. Three options: it becomes the API number for the automated lead system
(and then it leaves the phone app forever), it stays a manual second line, or it is
retired and merged into `054-398-2444`. **This blocks the lead system's stage 1** —
`docs/plans/2026-08-31-lead-response-system-masterprompt.md` §6. Five minutes of thought,
and it unblocks two documents. Do it first.

**B. Get into both Instagram accounts.** One of them has zero posts and follows hundreds
of people, which is what a compromised account looks like. Try the login; if it fails,
run Instagram's account-recovery flow. Report back: which handle GT controls, follower
counts, and whether either shows unfamiliar activity. **Until this is answered, no
Instagram work happens.** Around twenty minutes.

**C. Create the LinkedIn company page.** LinkedIn requires a personal profile to create a
company page and there is no API for it. The session will hand you the complete filled
text and the images; you paste and click. ~15 minutes.

**D. Fill the password manager.** One entry per property, named exactly as the sheet's
`שם הרשומה במנהל הסיסמאות` column says. Turn on MFA wherever it is off. The session
never sees a value. ~45 minutes, once.

**E. Meta Business admin — the big one.** GT is not an admin on its own Meta Business
account. This blocks the WhatsApp green tag, business verification, the lead-form
improvement, CTWA campaigns, and re-authorising the connection before it expires.
Find who is admin today and have them add the company email as full admin; if nobody can
be found, open a Meta support case with the company registration documents. **Then add a
second backup admin.** This is the single most-blocking item across all six workstreams
in the war room. Start it the day you read this — Meta support is slow.

**F. Name the human who owns `2026-10-23`.** Not a calendar reminder — a person, told out
loud, who knows that if that connection lapses the leads stop and nobody finds out for
weeks. Add them as an attendee to the existing event.

**G. Approve the content calendar** before the first post goes out, and approve which
customer names may be shown publicly.

---

## 7. Landmines — do not rediscover these

1. **A number that enters the WhatsApp Cloud API leaves the phone app permanently.**
   Anyone who then installs WhatsApp with that number on a handset disconnects the
   system. If `054-398-2444` is chosen for the API, the line `דורין` uses today moves
   into a shared inbox on the same day — that is a decision, not a side effect.
2. **Instagram's "zero posts, hundreds following" pattern is the classic signature of a
   compromised or purchased account.** Do not treat it as a dormant duplicate to be
   quietly closed. Verify before touching it, and if GT cannot log in, escalate rather
   than deleting evidence.
3. **The Meta business verification is rejected far more often on a name/address mismatch
   than on missing documents.** The company name and address in the Meta profile, on the
   submitted document and on the website must be byte-identical before submitting. Check
   all three first; a rejection costs a full re-review cycle.
4. **A new WhatsApp API account starts inside a messaging tier and a quality rating.**
   Bulk-sending on day one burns the rating before the account has any history. This is
   an additional technical reason the lead system's manual pilot is not optional.
5. **`wsrv.nl`, `HubSpot`, `Yotpo` and `Klaviyo` all appeared in the 2026-08-26 scan
   without being in anyone's plan.** Assume more exist. Before you declare a property
   list complete, read the live page source and the Shopify app list — not the plan.
6. **The artifact is `shared`, not owned, for some readers.** Publish updates to the same
   URL; a new URL orphans everyone's bookmarks and silently splits the state.

---

## 8. Halt conditions

Inherited from `gt-factory-os-production-brain/CLAUDE.md` §Stop conditions. Additions:

- Any evidence an account was accessed by someone outside GT → **STOP**, tell Tom
  immediately, change nothing, delete nothing.
- Any action that would post publicly, message a customer, or spend money → **STOP**.
- A property whose owner cannot be established → do not close it, do not rename it, do
  not "clean it up". Row on the risk list, line in §6.

---

## 9. Final report — Hebrew, short, honest

1. What a stranger could now open and see working, per property.
2. Each of D1–D7 ✅/❌ with its evidence pointer. No partial credit.
3. The numbers: properties owned / total · rows verified in the sheet · risks open.
4. The artifacts, and where they are.
5. What is still Tom's, and what is genuinely unfinished.
6. The single next action.

Then stamp this file `STATUS: SHIPPED — <date>` with evidence pointers, and commit.

---

## Execution record — 2026-08-31

Executed in one session. Evidence pointers, all in `Sales-Machine` unless stated:

| What | Where |
|---|---|
| Ownership audit + identity sweep + third-party inventory | `evidence/2026-08-31-social-property-audit.md` |
| 90-day content calendar (26 posts) | `doctrine/playbooks/social-calendar-2026-Q4.md` |
| LinkedIn company page + personal profile, filled | `doctrine/playbooks/linkedin-launch-kit.md` |
| YouTube branding + three recycled Shorts | `doctrine/playbooks/youtube-refresh-kit.md` |
| Open unknowns opened (U-014 … U-021) | `CURRENT_STATE.md` |
| Cards indexed | `knowledge/registry.yaml` |
| Credentials sheet — 24 asset rows + risk block | Tom's Drive, `GT Everyday — נכסי מותג` → `GT — כרטיס גישה`. **Deliberately not in any repo.** |
| Identity card v2 — four contradictions resolved | same folder, `GT Everyday — כרטיס זהות (מקור אמת אחד) — v2` |
| Tracker updated, same URL | `https://claude.ai/code/artifact/09e806f6-978b-46d3-8374-eb36379710fa` — 10/72 done, 19 tasks carry new dated notes |

### Definition of done — no partial credit

| # | Verdict | Evidence |
|---|---|---|
| D1 | ⚠ partial | The sheet exists with all 24 properties. 11 rows verified against the live property today; the rest carry `לא אומת` **with a reason**, exactly as §W1 allows. But `בעלים` is genuinely unknown on the Meta and Instagram rows, so the strict reading of D1 fails until §6.B and §6.E return. |
| D2 | ❌ | 42 → 29 occurrences of `072-3939395`. The 29 are one theme field the Shopify MCP refuses to write on a live theme. Recorded with the exact click path. |
| D3 | ❌ | Blocked, not attempted. Both handles serve a login wall to this environment; headless Chromium is blocked too. §6.B. |
| D4 | ❌ | Page not created — LinkedIn has no API for it. Every word and image it needs is written and waiting. |
| D5 | ✅ | 26 rows, each with date · platform · format · asset path · final Hebrew caption · owner · goal. All four assets in the first 14 days verified file-by-file against Dropbox, with byte sizes. |
| D6 | ❌ | The event is alive and correctly configured — and has zero attendees. A reminder is not an owner. §6.F. |
| D7 | ✅ | Published to the same URL. Two tasks closed with dated evidence, 19 more annotated. |

Two of seven pass. Every failure is a credential Claude does not hold, except D2, which is
a live-theme write the tooling blocks. None of them is an unfinished decision.

### What was found that no plan listed

`judge.me` running alongside Yotpo · Google Tag Manager with an unknown container owner ·
an unidentified `cloudfront.net/webtracking/rmShopifyUtils.min.js` · the legal name and
ח.פ recoverable from GT's own `/pages/אודות` · and two wrong asset paths in
`docs/warehouses/marketing-assets.md`.

Landmine 5 was right. Assume more still exist.
