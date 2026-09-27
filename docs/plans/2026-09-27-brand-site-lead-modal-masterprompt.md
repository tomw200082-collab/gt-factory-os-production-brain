# MASTERPROMPT — gteveryday.com: every lead button opens a lead window that lands a real lead and gets out of the way, the page reads and looks better, and the live theme can no longer miss work that already shipped

**STATUS: LIVE — not yet executed**
<!-- The executing session's last act is to change this line to SHIPPED / SUPERSEDED by <path> /
ABANDONED — why, with evidence pointers (merge SHAs, live checksums, gate record, lead row id). -->

> **Usage:** paste this entire file as the first message of a fresh session with three repos
> attached: `gt-site` (the brand site generator and its Shopify theme files), `gt-factory-os` (the lead
> intake function, the copy checker, the site harness and the gate records) and
> `gt-factory-os-production-brain` (governance and skills). It takes gteveryday.com from "every
> call-to-action throws the visitor to the bottom of the page, and three merged improvements never
> reached the live theme" to "every call-to-action opens a short lead window that sends a real lead and
> closes itself where the visitor was, the page's words and visuals have passed the UX release gate,
> and the live theme carries exactly what gt-site `main` builds". It halts for Tom only where §6 says so;
> §6 is that complete list. This file lives in the brain repo at
> `docs/plans/2026-09-27-brand-site-lead-modal-masterprompt.md`, on `main` once its PR is merged.
>
> **Provenance:** written 2026-09-27 by the session that shipped gt-site #23, #25 and #26. Sources:
> - Shopify Admin GraphQL: the theme list and the `checksumMd5` of every GT file in the live theme and
>   four unpublished themes, read through the Shopify MCP;
> - gt-site `origin/main` at `4c45338`;
> - the deployed `website_lead_intake` function (Supabase MCP `get_edge_function`, version 8);
> - `sales_core.lead` counts (read-only SQL);
> - live `gteveryday.com` fetched with curl;
> - Shopify's docs for the GitHub integration and `themeFilesUpsert`;
> - `npx @shopify/cli@4.8.2 theme push --help`, run in the container;
> - Tom's written request of 2026-09-27, quoted in §0 and §1.1.
>
> Authority, in order: brain `CLAUDE.md` → `EXECUTION_POLICY.md` → `gt-factory-os/CLAUDE.md` →
> `gt-site/PUBLISH.md` → brain `.claude/skills/shopify-theme/SKILL.md`. They are cited below, never copied.
>
> **Shelf life:** §2 is presumed wrong if pasted after 2026-10-11. Run §2.5 first.
> - **Theme facts drifted** (a different MAIN id, new gt-site commits, another theme touched): adapt. W1
>   re-derives them; that is its job.
> - **The intake contract differs** (§2.2, table B): halt and surface to Tom before writing form code.

## 0. How to work

- **Who you are here.** One autonomous agent session with the three repos and these tools:
  - **Shopify MCP.** Read. `themeDuplicate`. `themeFilesUpsert` on unpublished themes only. Its own
    description says it refuses publishing, theme deletion, and any file write to the live (MAIN) theme.
    Its `graphql_mutation` tool says the host app may ask the user to confirm each mutation. So when
    the CLI token exists, push previews with the CLI; otherwise keep MCP mutations to one duplicate
    and one upsert call per round, and list them in §6-D.
  - **Shopify CLI, possibly.** `npx -y @shopify/cli@4.8.2` runs in this container, and the store answers
    on the network (both checked 2026-09-27). It is usable only if Tom did §6-A before this session
    started: then `SHOPIFY_CLI_THEME_TOKEN` is set. Test with `test -n "$SHOPIFY_CLI_THEME_TOKEN"` and
    never echo it.
  - **The rest.** The Supabase MCP (read-only SQL, `get_edge_function`), the GitHub MCP, and Playwright
    with Chromium and axe-core. There is **no WebKit** (`/opt/pw-browsers` holds Chromium only).
  - **What you hold.** Tom's merge autonomy under brain `CLAUDE.md` §Authorization: required checks
    green and the change verified.
  - **What you do not hold:**
    - approval of new customer-visible Hebrew (§6-B);
    - putting anything on the live storefront (§6-C);
    - deleting a theme;
    - any change to the lead intake's contract.
- **The method is Tom's, in writing (2026-09-27):**
  `ההתחלה בסיור מוחות עם הסקיל של סופר פאוורס, המשך עם UX רליס גייט, ולבסוף סימפליפיקיישן וריפיקיישן בפור קומפלישן, ככה שאני לא אצטרך לוודא אותו בכלל, כמו שעשינו, זה עבד טוב בפעמים הקודמות.`
  In practice:
  1. **Brainstorm.** Use the `brainstorming` skill (brain `.claude/skills/brainstorming/`). Once you
     have done the reading and run §2.5, your first message to Tom is a single brainstorm round, not code:
     - the design of §4 W3 in his words;
     - the questions of §6-B, asked in the same message;
     - any §2.5 difference from §2.

     Record his answers in §1.1 before W3 starts. Work on W1 in parallel; it needs no answer.
  2. **Design at the highest level.** The dialog is designed with the frontend-design skill your session
     lists (`frontend-design-master`, and gt-site's `.claude/skills/taste-skill`), inside the page's
     existing visual language. A second style bolted onto a finished page is a finding, not a feature.
  3. **Gate.** The UX release gate (brain `.claude/commands/ux-release-gate.md`) runs render-grade on
     the preview theme (W5).
  4. **Close.** `simplify` plus brain `ponytail-review` on every diff, with each cut and each skipped cut
     written down. Then `verification-before-completion` on the exact heads, then the ship (W7).

  Tom's closing words are the standard for evidence: he must not need to check anything himself. Every
  claim in the report is something you observed, with its pointer.
- **Read first, in order.**
  1. Brain `CLAUDE.md`, `gt-factory-os/CLAUDE.md` and `gt-site/PUBLISH.md`.
  2. `gt-site/README.md`, the Build and Deploying sections. The "five steps" line is stale; `tools/build.sh`
     runs 13 steps.
  3. Brain `.claude/skills/shopify-theme/SKILL.md`.
  4. `gt-factory-os/docs/superpowers/plans/2026-09-25-customer-portal-ux-gate.md`, for three things: the
     gate's shape, how its §5 approves copy, and §9 (the site's iPad findings). Also its `…-gate/BRIEF.md`.
  5. `gt-factory-os/supabase/functions/website_lead_intake/index.ts`, which is the deployed copy.
  6. `gt-factory-os/api/scripts/site_ipad_shots.mjs`, the site harness you will extend.

  Then run §2.5 and compare it with §2.2.
- **Authority.** The docs listed under Provenance, cited not restated. Where this document and an authority
  doc disagree, the authority doc wins and this document is wrong; say so in the report.
- **Inherited.** Halt conditions, evidence standard and git discipline come from brain `CLAUDE.md` §Stop
  conditions and §Evidence, and `gt-factory-os/CLAUDE.md` §Checks and §⊥ do. Deltas are in §8 only.
- **Watching:** brain `CLAUDE.md` §Watching. After every `create_pull_request`, call
  `unsubscribe_pr_activity` at once. No check-ins, no Routines.
- **The standard, in Tom's words (2026-09-27):**
  - `חלונית שבה משאירים פרטים בצורה פשוטה ברורה ומאוד מאוד יפה ופשוטה וחזקה שממירה הכי הרבה`
  - `כאשר הוא משאיר את הפרטים החלונית תיסגר אוטומטית והוא יוכל להמשיך לגלול`
  - `הכי חשוב זה שכל פעם הtheme שאתה מפרסם ומשפר יהיה העדכני ביותר`

  As prohibitions you can check:
  - Once the page's script has loaded, no call-to-action moves the page.
  - The window never says "received" unless the intake answered `ok: true` to a request a human could
    have sent (§3.3).
  - After your last push, no GT file in the live theme differs from what gt-site `main` builds.
  - Nothing an admin set in the theme is lost: the favicon, and `show_portal_entry`.
- **Language:** this document is in English because that is the register the executor reasons best in.
  Data literals stay in their own script, in backticks, and are never translated. **Output language:
  concise English** — short sentences, no preamble, no restating the question. Messages to Tom (the
  brainstorm round, §6 asks, and the §9 report) are in Hebrew, short and direct, and end with one action
  for him or `אין צורך בפעולה ממך`.

## 1. Mission and definition of done

**One testable sentence:** on gteveryday.com, every lead call-to-action opens a lead window. The window
sends a real lead to the sales system, closes itself on success with the page exactly where it was, and
passes the UX release gate together with the page's improved copy and visuals. The live theme's GT files
then equal gt-site `main`'s build, byte for byte, through a ship path written down so the next session
cannot skip a file.

| # | Condition | The observation that would prove it false |
|---|---|---|
| D1 | **Live equals the repo.** After W7 the live theme holds every file in the GT set (W1 defines it), and each one's `checksumMd5` equals the md5 of the same file staged from the merged gt-site head. `templates/*.json` are compared as parsed JSON; Shopify's leading `/* … */` comment is ignored. Images (content-addressed `gt-<hash>.*`) are compared by presence. The theme-owned values are unchanged from their 2026-09-27 state: `config/settings_data.json` still names `shopify://shop_images/gt-favicon-2026.png`, and `templates/index.json` `sections.main.settings` still reads `show_portal_entry: true`, `third_party_pixels: true`, `analytics_id: ""`. | The W1 drift check, run against the live theme after the push, prints any mismatch or any missing file. Without the CLI token, its input is the raw MCP query and response saved to a file beside the report, not values copied by hand. The favicon line differs. The business entry `כניסה לעסקים` is missing from live `gteveryday.com` HTML. |
| D2 | **One ship path, written where sessions look.** gt-site has the stage and drift tools of W1. `gt-site/PUBLISH.md`, `gt-site/README.md` §Deploying and brain `.claude/skills/shopify-theme/SKILL.md` all describe the same protocol: stage the whole GT set, check drift, push the whole set, check drift again. A preview is duplicated from MAIN at the moment it is needed, never from another unpublished theme. | Any of the three docs still tells a session to upload only the files a PR changed, or to duplicate a non-MAIN theme as the base. The drift check does not run in the ship step it describes. |
| D3 | **No button moves the page.** Every lead call-to-action in §2.2 table C (16 `href="#contact"` in `src/index.html`, plus the three flavour cards that `strip_prices.py` retargets, which open the product window first) opens the lead dialog. Checked at `p390` and `d1360` on the preview theme: `scrollY` is the same (±1 px) before the click, while open, and after close. With JavaScript not yet loaded, the link still reaches `#contact`. | The harness facts (W4) for each call-to-action. Any `scrollY` delta, or any call-to-action that does not open the dialog. |
| D4 | **The lead lands, then the dialog leaves.** On a stubbed 200 `{ok:true}`: <br>• a success state shows; <br>• the dialog closes itself after the delay Tom agreed (§1.1); <br>• focus returns to the call-to-action that opened it; <br>• `scrollY` is unchanged; <br>• `generate_lead` is pushed exactly once. <br>On 400 `missing_fields`, 400 `bad_phone`, 502, a 15 s timeout and offline, the dialog stays open, keeps every value, and shows that case's message and the WhatsApp and phone fallback. The request body is the deployed contract (§2.2, table B), and `elapsed_ms` counts from navigation start (§3.3). Success means `res.ok`, `body.ok` and a `was_new` key in the body; a send is held until `performance.now() ≥ 3000`. | Harness scenarios per response class, and assertions on the request body. A scenario that opens the dialog 2 s after load and submits 0.5 s later must send only once `performance.now()` has passed 3000, with `elapsed_ms` ≥ 3000 measured from navigation start. A stubbed `{ok:true}` without `was_new` (the intake's silent drop) must not show the success state. |
| D5 | **Accessible and device-safe.** <br>• Modal to assistive technology, with focus trapped and returned. Esc, the × button and the backdrop all close it. <br>• Every field has a visible label, the right `autocomplete` token and a font of at least 16 px. <br>• The four required fields and the consent are visible without scrolling inside the dialog at `p390` (390×844), keyboard closed. <br>• No horizontal overflow from 320 to 1920 px. <br>• `prefers-reduced-motion` is honoured. <br>• axe reports 0 violations with the dialog open, in error and in success. <br>• The product, recipe and purée windows and the phone menu work as before. | Harness facts and axe runs. Any regression in the existing site iPad scenarios (`site_ipad_facts.json` before and after). |
| D6 | **One real lead, from the live page.** After W7, one submission through the live dialog on `gteveryday.com`, using the test identity in §6-C, creates exactly one `sales_core.lead` with `source = 'website_form'` and `form_name = 'partner_enquiry'`. Its `note` event carries the call-to-action's `interest`, and it has an `alert_sent` event. Before sending, check that no lead with `external_id = 'web-<today UTC>-<last 9 digits>'` exists: a second lead from the same number on the same day is `was_new: false` with no note (table B), so send on a day it does not exist. | The SQL in §2.5, run before and after (count +1, the event rows present). A proof run on the preview only, or on a stub only, fails this. |
| D7 | **The gate says SHIP.** The UX release gate runs on the preview theme: the five dimensions plus a site-device dimension for phone and iPad. Scope is the dialog, the call-to-action flow, and the page's copy and visuals. Result, in the gate's own words (`ux-release-gate.md`): SHIP, meaning 0 P0 and every dimension GREEN, in at most 3 rounds, signed by `factory-os-governor`. CONDITIONAL_SHIP counts only if Tom approved in writing the P1s it names. The record is `gt-site/docs/2026-09-27-site-ux-gate.md`, with `reports/` beside it. | HOLD after round 3; CONDITIONAL_SHIP without Tom's written approval of its P1s; no governor line; no record. |
| D8 | **The copy is governed.** Every new or changed customer-visible Hebrew string is in the approved set (§6-B): backticked rows in a new `### 5.5` of `gt-factory-os/docs/superpowers/plans/2026-09-25-customer-portal-ux-gate.md`, placed before its `## 6.` and numbered `U-16` onward. The checker reads only rows matching `[CU]-<n>` inside §5 (`portal_copy_check.mjs`, `batchStrings`); U-15 set the precedent for site strings. `SITE_FILES` names every gt-site file that holds site Hebrew and that this work touches. Today it misses `tools/patch_form.py`, `i18n/parts/he_visible_2.py` and `he_visible_3.py`, and any new patch. The checker diffs gt-site's working tree against gt-site `origin/main`, so it is run **before** the gt-site merge, with gt-site checked out at the PR head as the sibling `../gt-site` and every new file committed. After the merge it checks nothing. It prints `0 unapproved`, and `--self-test` exits 1. The gt-site `build` workflow's price and number guards pass. | The checker's two runs at the gt-site PR head (with their timestamps before the merge), and the workflow run. |
| D9 | **Simplified, then verified on the exact heads, then merged.** <br>• One `simplify:` commit per repo touched, listing cuts and skipped cuts. <br>• Then, run later than the last code commit: `tools/build.sh` exits 0, `python3 tools/build_theme.py` runs, and `git status --porcelain` is empty. <br>• The gt-site `build` workflow is green on the PR head. <br>• The harness is re-run and D3–D5 re-read. <br>• The copy checker runs (D8). <br>• The gt-factory-os PR's required checks are green. <br>• Three PRs merged: gt-site, gt-factory-os (harness, `SITE_FILES`, the §5.5 rows), and the brain (the `shopify-theme` skill, this file's stamp). | Run timestamps against the last commit; the workflow runs; the three merge SHAs. |
| D10 | **Stamped and reported.** <br>• `gt-site/PUBLISH.md` names the live theme and the new ship path. <br>• `186686636273` is recorded as superseded: its two changes are on `main` and ship with this work. <br>• This file's status line reads SHIPPED with pointers. <br>• A Hebrew report in the §9 shape reaches Tom, with before and after shots of the call-to-action flow on a phone and on a desktop. | The line still reads LIVE; no report; PUBLISH.md still names `186686636273` as next. |

D1 and D6 need §6-C. Without it they are ❌, and the report says so first. Anything not on this list is
out of scope unless Tom asks.

### 1.1 Settled — do not reopen

- **Tom, 2026-09-27, in writing:**
  - A call-to-action opens a window instead of jumping to the bottom (`במקום שכאשר לוחצים על ה CTA באתר שמוביל ישר לחלק הכי תחתון`).
  - The window closes itself after the details are sent, and the visitor keeps scrolling.
  - It is designed at the highest UX and UI level, with the frontend-design skills.
  - The site's copy and visuals improve through the UX release gate.
  - Every theme published must be the most current.
  - He prefers to work on the live theme continuously (`אם היה אפשר פשוט לעבוד על אותו אחד שכבר חי כל הזמן ולשפר אותו ברמה שוטפת זה היה הכי טוב`).
  - The method in §0.
  - He asked for these improvements **before** `186686636273` (`כניסה לעסקים`) is published. So it is
    not published on its own; its content is on `main` (#23, #25) and ships with this work.
- **Earlier and still in force:**
  - The entry reads `כניסה לעסקים` on desktop and in the menu, and `לעסקים` on the phone pill
    (gt-site #25, Tom 2026-09-27).
  - The products stand on a soft floor shadow, with no `drop-shadow` on cut-out images (#23; the
    lesson is in brain `docs/lessons_learned.md`, 2026-09-26).
  - No prices on the site (`data/site_flags.json` `show_prices: false`).
  - The site's WhatsApp number stays `054-398-2444` (Sales-Machine `CURRENT_STATE.md` U-032).
- **Author's decisions from the 2026-09-27 reconnaissance.** Present them in the brainstorm round; they
  reopen only if Tom writes otherwise.
  1. **The intake contract is not touched.** Deployed `website_lead_intake` v8 requires `contact_name`,
     `venue`, `city` and `phone`. The dialog asks for exactly those four, plus the existing consent
     `אפשר לפנות אליי בנושא אספקה סיטונאית.`, unchanged in meaning and still required. The optional
     fields (role, email, interest, message) may be offered but never required. No new `form_name`:
     unknown values collapse to `partner_enquiry`, and adding one is a backend change with a
     `campaign_map` row.
  2. **The call-to-action's intent travels in `interest`,** using the form's existing options, which the
     intake stores in the lead's note:
     - `רוצה מחירון`, `לקבלת הקטלוג המלא` and `רוצה מחירון ותמחירים` preselect `המחירון המלא`;
     - the others preselect nothing;
     - when the visitor leaves `interest` empty, the send carries the call-to-action's context instead:
       for `הוסיפו לתפריט`, the product's name as the page shows it. The intake stores `interest` as free
       text (up to 120 characters) in the lead's note, so this is data, not visible copy.

     The dialog's heading may follow the intent. That is copy, so it goes into §6-B.
  3. **Progressive enhancement.**
     - Every call-to-action keeps `href="#contact"`.
     - A page opened with `#contact` in its URL scrolls to the section as it does today; the dialog
       never opens on load.
     - There is **one form implementation**, one submit path (`pSend`) and one state.
     - Without JavaScript, the `#contact` section still offers the direct phone, WhatsApp and mail links.

     Recommended shape: the form stays in `#contact`, and the dialog borrows that same node while it is
     open. Decide it in the brainstorm.
  4. **Theme-owned is not repo-owned.** Two things belong to the theme and are never overwritten from
     the repo:
     - `config/settings_data.json` (the favicon since 2026-09-25 16:02Z);
     - admin settings inside `templates/*.json`. On live, `templates/index.json`
       `sections.main.settings` holds three: `show_portal_entry: true`, `third_party_pixels: true`,
       `analytics_id: ""`.

     `stage_theme` copies `sections.main.settings` from the target theme's current file at staging
     time, so a push never changes an admin value. The repo's generated file is brought to the same
     three values, so the repo also describes live.
  5. **The four landing pages stay unpublished** (`/pages/<slug>` answers 404). Their files join the GT
     set, so live stops lagging; their own forms and buttons are out of scope.
  6. **Ship path.** If §6-A is done, the GT set is pushed with the CLI straight into the live theme
     (`--allow-live --nodelete`), after it has passed on a preview. Otherwise the fallback in W7 applies.
     GitHub-integration sync of the whole theme is not this work (§3.2).

## 2. Ground truth — measured 2026-09-27; re-verify at boot

### 2.1 What is built and live

- **Live theme:** `166730072305` `GT 2026 Site — כניסת לקוחות`, MAIN. Its publish time is not recorded; the
  `updatedAt` stamps point to 2026-09-25 15:25Z (inference, not verified). There are 17 themes in the store; Shopify's
  limit is 20.
- **The home form posts to the intake.** Live `gt-site.js` contains
  `functions/v1/website_lead_intake` (curl of the served asset, 2026-09-27).
- **The deployed intake is `website_lead_intake` version 8.** It is identical to `gt-factory-os`
  `supabase/functions/website_lead_intake/index.ts` (`f5ef4d0`, #284). The copy in
  `gt-site/supabase/functions/` is older; do not edit or deploy it.
- **Leads.** `sales_core.lead` with `source = 'website_form'`: 8 `partner_enquiry` and 1
  `landing-site-chai`, from 2026-08-31 on, the last at 2026-09-27 02:55Z.
- **gt-site `origin/main` is `4c45338`** (#26). There are no open PRs, and no remote branch has theme
  content newer than `main`.

### 2.2 The numbers

**A. GT files in the live theme against gt-site `main`** (md5 prefixes; the repo side is
`git show <rev>:<path> | md5sum`):

| File | Live | Built by `main` | State |
|---|---|---|---|
| `layout/gt.liquid` | `bcba3957` | `bcba3957` | same |
| `sections/gt-home.liquid` | `3f6119e5` | `810d8bf9` | live lacks #25 |
| `assets/gt-site.css` | `79af38b9` | `743fa85e` | live lacks #23 and #25 |
| `assets/gt-site.js` | `6bd22e13` | `eb8f5a64` | live lacks #22 (dwell time from navigation start; deep-link close) |
| `assets/gt-lp.js` | `024bf1bf` | `6a9fe371` (`tools/landing-pages/out/`) | live lacks #17 and #22 |
| `sections/gt-lp-chai.liquid` (the other three alike) | `d5359432` | `bcbe8b59` | live lacks #17: `data-endpoint` is empty on live `?view=chai` |
| `assets/gt-lp.css` | `d68fc6a6` | `d68fc6a6` | same |
| `templates/index.json` | `sections.main.settings`: `show_portal_entry: true`, `third_party_pixels: true`, `analytics_id: ""` | `settings: {}` | theme-owned values; staged from the target, repo brought to match (§1.1.4) |
| `config/settings_data.json` | favicon `gt-favicon-2026.png` | not in the repo | theme-owned; set in MAIN 2026-09-25 16:02:54Z and in no doc |

- **Unpublished themes.**
  - `186686636273` is MAIN plus `f4b054e`'s `gt-home.liquid` and `gt-site.css`.
  - `166741213425`, `לוגו חדש בלשונית`, is a copy of MAIN taken three minutes *before* the favicon
    change, so it holds the old favicon.
  - `166708576497`, `טפסים למערכת המכירות`, holds #17's landing files but none of #21.

  None holds code that is missing from `main`. The only thing that exists in a theme and nowhere else is
  the favicon setting.

**B. The intake contract** (deployed v8, read 2026-09-27):
- `POST` JSON, with CORS for `https://gteveryday.com`, `https://www.gteveryday.com` and
  `https://greenteaeveryday.myshopify.com`.
- Required: `contact_name`, `venue`, `city`, `phone`. The phone needs at least 9 digits. The email is
  checked for format when present.
- Answers:
  - `{ok:true}` **without storing anything** when the honeypot `company_website` is non-empty or when
    `elapsed_ms < 3000`;
  - `400 missing_fields` / `bad_phone` / `bad_email`;
  - `502 ingest_unreachable` / `ingest_failed`;
  - `503 not_configured`.
- Only the real path returns a `was_new` key (`{ok: true, was_new: …}`); the two silent drops return
  `{ok: true}` alone. The page tells them apart by that key.
- One lead per phone number per day: `external_id = web-<date>-<last 9 digits>`. A repeat answers
  `was_new: false` and writes no note.
- `form_name` accepts `partner_enquiry` and `landing-site-{chai,matcha,iced-tea,ube}`; anything else is
  stored as `partner_enquiry`.

**C. Lead calls-to-action on the Hebrew page** (`src/index.html` at `4c45338`; line numbers drift):

| # | Line | Where | Label |
|---|---|---|---|
| 1 | 1130 | sticky nav | `רוצים להתחיל` |
| 2 | 1137 | hero | `אני מעוניין` |
| 3–12 | 1147 | the 10 hero slides | `רוצה מחירון` |
| 13 | 1178 | `#products` | `לקבלת הקטלוג המלא` |
| 14 | 1231 | the economics card after `#drinks` | `רוצה מחירון ותמחירים` |
| 15 | 1416 | `.bigcta` | `רוצים להתחיל` |
| 16 | 1562 | inside the product window `#fmodal` | `הוסיפו לתפריט` (also closes that window) |

In the served theme, `strip_prices.py` also retargets three flavour cards to `#contact` (served total
19); with JavaScript on, they open `#fmodal` first. The direct channels (phone, mail, Instagram,
WhatsApp) are not lead calls-to-action and stay as they are.

**D. Size.** `gt-home.liquid` is 65,430 bytes; CI fails the section at 262,144. `gt-site.css` is
80,786 bytes and `gt-site.js` is 70,420 bytes (wc, 2026-09-27).

### 2.3 What is NOT built
- the lead dialog, and any interception of `#contact` links;
- a stage and drift tool for themes;
- a CLI ship path;
- phone and desktop scenarios in the site harness;
- copy-gate coverage of `patch_form.py`, `he_visible_2.py` and `he_visible_3.py`.

### 2.4 Known-broken, adjacent, out of scope unless the gate raises it
- **The existing windows lack accessibility basics.** `#fmodal` has no `role`, `#pmodal` has no Esc,
  there are no focus calls anywhere, and scroll is locked two different ways (`html.cm-lock` and
  `body.style.overflow`). The gate decides what is P0 or P1 there.
- **GTM has no trigger on `generate_lead`** (`gt-site/docs/2026-09-02_analytics.md`). Analytics
  configuration is out of scope.
- **`PUBLISH.md` §1 still lists two open blockers:** B2 (Tom's real-browser look) and B4 (About
  photos). B3's text is stale; `show_prices: false` has removed the price list since 2026-09-24.

### 2.5 Re-verification block

```bash
# 1. repos (run from each clone)
git -C gt-site fetch -q origin && git -C gt-site log --oneline -5 origin/main          # expect 4c45338 on top, or newer
for f in theme/sections/gt-home.liquid theme/assets/gt-site.css theme/assets/gt-site.js \
         tools/landing-pages/out/gt-lp.js tools/landing-pages/out/gt-lp-chai.liquid; do
  echo "$f $(git -C gt-site show origin/main:$f | md5sum | cut -c1-8)"; done
# 2. live page: the form endpoint and the landing endpoint
curl -sL https://gteveryday.com/ | grep -o '//gteveryday.com/cdn/shop/t/[0-9]*/assets/gt-site\.js[^"]*' | head -1
curl -sL "https://gteveryday.com/?view=chai" | grep -o 'data-endpoint="[^"]*"' | head -1   # 2026-09-27: empty
# 3. CLI path available?
test -n "$SHOPIFY_CLI_THEME_TOKEN" && echo cli-token-present || echo cli-token-absent
```

- **Shopify MCP.** Run
  `themes(first:25){nodes{id name role updatedAt}}`. Then run
  `theme(id:"gid://shopify/OnlineStoreTheme/<MAIN>"){files(filenames:[…the GT set…]){nodes{filename checksumMd5 updatedAt}}}`.
- **Supabase MCP.**
  - `get_edge_function website_lead_intake`: expect version 8 and the contract in table B.
  - The lead count:
    ```sql
    -- 2026-09-27: partner_enquiry 8, landing-site-chai 1
    select form_name, count(*), max(created_at) from sales_core.lead
    where source = 'website_form' group by 1;
    ```

## 3. What the hard part actually is

1. **The dialog is the visible deliverable. The failure Tom named is shipping.**
   - Three merged site PRs (#22, #23, #25) are not live.
   - The landing files on live are two PRs behind.
   - A favicon exists only inside the live theme.

   The cause is mechanical, and it will eat this work too unless it is fixed first:
   - each upload sent only the files its PR changed;
   - previews were duplicated from whichever theme looked newest;
   - the landing outputs (`tools/landing-pages/out/`) were never in the upload check;
   - publishing swaps the **whole** theme, so anything edited in MAIN after the preview was duplicated
     is lost on publish.

   W1 closes all four before the dialog ships.
2. **"Work on the live theme directly" was checked on 2026-09-27; this is the answer.**
   - The Shopify MCP refuses writes to MAIN and refuses publishing (its tool description).
   - The Admin token in the environment belongs to the custom app `Inventory & OS System` and has no
     theme scope (`currentAppInstallation.accessScopes`, read without printing the token).
   - `themeFilesUpsert` needs `write_themes` plus an exemption from Shopify (its docs).
   - Shopify's own route is the CLI with a Theme Access password: `shopify theme push --theme <live id>
     --allow-live --nodelete` pushes files straight into the live theme. The theme id never changes,
     and admin edits are never swapped away. That is the continuous live work Tom asked for, with one
     setup action by him (§6-A).
   - The GitHub integration also works in principle, but only with the **full** theme at a branch root.
     That theme holds hundreds of third-party files (`bss-b2b-js.js` 948,928 bytes,
     `customer-fields.js` 814,360 bytes), and every admin or app edit is committed back to the branch.
     It is a separate, larger decision.
3. **The intake can say `ok` while storing nothing** (table B). A dialog that measures `elapsed_ms` from
   when it opened turns every fast, autofilled human into a silently dropped "bot" — and thanks them.
   Rules:
   - measure from navigation start (`performance.now()` is already that, and #22 made the form use it);
   - keep the honeypot unreachable to autofill (`tabindex="-1"`, `autocomplete="off"`, hidden by
     clipping, never by a large negative offset; CI bans that because of an RTL incident);
   - hold the send until `performance.now() ≥ 3000`, so no human can be dropped;
   - treat only `res.ok && body.ok && 'was_new' in body` as success, with a code comment naming the
     intake's two silent drops, since this couples the page to that function.
4. **The page is generated.**
   - `src/index.html` and `theme/*` are build outputs, and CI rejects a hand edit.
   - Markup comes from patches that run in a fixed order, anchored on text with exact-count asserts.
   - `patch_form.py` writes the form; `patch_a11y`, `patch_ux`, `patch_launch` and `patch_ipad` run after
     it and anchor on its markup.

   The dialog therefore belongs in a new patch that runs after `patch_ipad` and just before
   `validate.js` in `tools/build.sh`. Visible
   Hebrew goes through the translation tables (`i18n/parts/he_visible_*.py`), or literally into the new
   patch, as `patch_rtl_shell.py` does.
5. **WebKit cannot be observed here.** The iPhone is where this dialog lives or dies, and the harness is
   Chromium. So the known WebKit traps are written as rules and checked in code review. They are listed
   in §7, and each line in the report says "rule applied, not observed on WebKit".

## 4. Workstreams

### W0 — Boot and baseline (about 30 minutes)
1. Do the reading in §0 and run §2.5.
2. In a clean checkout, `tools/build.sh` exits 0 and `python3 tools/build_theme.py` leaves
   `git status --porcelain` empty. On 2026-09-27 the only output was a `<div>` balance warning,
   438 / 439.
3. Run the site harness once against live and keep its facts as the "before".
4. Record the §2.5 differences.

### W1 — One ship path (the freshness fix; runs while Tom answers W2)
1. **Define the GT set once, in code:**
   - `theme/layout/gt.liquid`;
   - `theme/sections/gt-home.liquid`;
   - `theme/assets/gt-site.{css,js}`;
   - `theme/templates/index.json`;
   - every file in `tools/landing-pages/out/`, mapped to its theme folder: `gt-lp-*.liquid` to
     `sections/`, `gt-lp.{css,js}` to `assets/`, `index.*.json` and `page.*.json` to `templates/`;
   - the images named in `theme/assets.manifest.json`, which are content-addressed as `gt-<hash>.*`.
2. **`tools/stage_theme.*`** writes the GT set into one staging directory in theme layout and asserts
   that nothing else is in it. Two rules:
   - **Images.** They are not in the repo; `theme/assets.manifest.json` maps each name to a remote URL.
     Stage only the images the target theme lacks, by name, downloaded through Node with TLS verified.
   - **`templates/index.json`.** Take `sections.main.settings` from the target theme's current file
     (§1.1.4).
3. **`tools/theme_drift.*`** compares the staged set with a theme's `{filename: checksumMd5}`, taken from
   the MCP files query or a CLI pull. `templates/*.json` are compared as parsed JSON with the leading
   comment ignored. Images are compared by presence. It exits 1 on any difference and prints each one.
4. **Bring the repo to match live's theme-owned template values** (the three in §1.1.4) in the
   generated `templates/index.json`. `config/settings_data.json` stays out of the GT set.
5. **Rewrite `gt-site/PUBLISH.md`, `README.md` §Deploying and brain `shopify-theme` SKILL.md** to that
   one protocol:
   1. duplicate MAIN at the moment of use (never another theme);
   2. push the whole staged set;
   3. run the drift check, expecting 0;
   4. preview;
   5. only then go live;
   6. run the drift check against live, expecting 0.

   In the skill, name the partial-upload path as the cause of the 2026-09-27 drift. The README's
   live-theme table is also stale (it names `162206646513`); correct it.
6. **Keep a single preview theme.** Duplicate MAIN once, as `GT site — preview 2026-09-27`, and reuse it
   for every round by re-pushing the whole set. There are 17 of 20 slots today.

**Acceptance:** D2, and the tools D1 needs.

### W2 — Brainstorm round with Tom (one message, early)
Send it in Hebrew. It contains:
- the design of W3 in his words, with one visual: a phone mock of the dialog, built with the
  frontend-design skill and sent as an image or an artifact;
- the §1.1 author's decisions, stated as decisions;
- §6-B, asked;
- any §2.5 difference.

Record his answers in §1.1. If he is silent, continue on W1 and W4, and do not merge W3. If he is
still silent when everything else is done, end as HOLD_FOR_TOM with a report of what is ready and the
one answer you need.

### W3 — The lead dialog (gt-site; a new last patch plus the translation tables)

**Opening.**
- Clicks on any §2.2-C call-to-action are delegated from the document, with the default prevented
  only when the dialog code is loaded.
- `הוסיפו לתפריט` closes `#fmodal`, then opens the dialog.
- Use a native `<dialog>` with `showModal()`. It gives the top layer (no z-index war with nav 80,
  `#fmodal` 90, `#cmodal` 200, `#pmodal` 210), inertness and Esc. Add a focus return to the invoker and
  a click-outside close.
- Scroll lock reuses `html.cm-lock`. Do not use `position: fixed` on `body`: on iOS it jumps the page.
- Copy `cmOpen`'s `pushState` pattern, so the phone's back button closes the dialog instead of leaving
  the site.

**Content.**
- The four required fields and the consent come first. The optional fields sit behind one disclosure,
  or are left out of the dialog; decide in the brainstorm.
- Labels are visible and not placeholders.
- `autocomplete`: `name`, `organization`, `address-level2`, `tel`, `email`. Phone gets
  `inputmode="tel"`.
- The primary button stays reachable with the keyboard open.
- The heading and supporting line follow the call-to-action's intent, where Tom approved it (§6-B).

**Layout.** A bottom sheet on phones, sized with `dvh` and `overscroll-behavior: contain`. A centred
card from tablet width up. Motion only where `prefers-reduced-motion` allows; the close timing does not
depend on motion.

**Sending.** Reuse `pSend` and its endpoint. Add the call-to-action's `interest` (§1.1.2). Keep
`elapsed_ms` from navigation start, hold the send until `performance.now() ≥ 3000`, and count as success
only `res.ok && body.ok && 'was_new' in body` (§3.3).
- **On success:** a success state inside the dialog, then an automatic close after the agreed delay.
  The recommendation to Tom is about 2 s, long enough to read one line. Focus returns to the invoker.
- **After that,** any call-to-action opens the dialog in its sent state, with the WhatsApp line. The
  intake keeps one lead per phone per day anyway.
- **On failure:** the existing specific messages and the `PF_ERR` fallback, inside the dialog.

**Analytics.** Push `generate_lead` once per confirmed lead, with a `lead_cta` field naming the
call-to-action.

**Budget.** No library. The section stays under CI's section limit (262,144 bytes, §2.2 D); it is
65,430 bytes today.

**Acceptance:** D3, D4, D5.

### W4 — The site harness (gt-factory-os `api/scripts/site_ipad_shots.mjs`, extended in place)
Keep the file name; the gate brief cites it.

**Viewports.** Add `p320`, `p390`, `p430`, `t768`, `d1360` and `d1920` beside the iPad ones.
`SITE_VPS` already selects which to run. Every context today is `isMobile: true, hasTouch: true` with a
Mac Safari user agent, so give each viewport its own device settings:
- phones get an iPhone user agent with touch;
- desktops get no touch and a desktop user agent;
- the iPad ones stay as they are.

**Scenes, for each call-to-action:** before the click, the dialog open, each error class, the sent
state, after the automatic close, and the product window's `הוסיפו לתפריט`.

**Facts:** `scrollY` at each step, the focused element, overflow, the dialog's box, and axe results.

**Stubbing.** Every request to `**/functions/v1/website_lead_intake` is intercepted with
`route.fulfill`, one fixture per response class. The harness also aborts any unstubbed `POST` to that
URL. A real submission emails staff, so only D6 may send one.

**Render.** Point `SITE_URL` at `https://gteveryday.com/?preview_theme_id=<preview id>`.

**Acceptance:** evidence for D3–D5 and D7.

### W5 — Design passes, then the UX release gate (about 3 hours)

**Brief.** Write it from the 2026-09-25 gate's `BRIEF.md`, re-aimed at the brand site:
- who arrives: a café or restaurant owner, mostly on a phone, often from an ad or WhatsApp;
- the bar;
- the constraints of §1.1;
- the severity scale.

**Agents.** The five from `ux-release-gate.md`, plus the site-device dimension (phone and iPad). Where
your harness does not register a named agent, dispatch a general-purpose agent with that agent file's
text, as 2026-09-25 did.

**The gate covers more than the dialog:**
- the page's words: headings, call-to-action labels, the form's lines, and the four different labels for
  one destination (`gt-site/docs/2026-09-03_ux-review.md`);
- its visuals: hierarchy, rhythm, the first screen on a phone.

Its "world-class upgrades" section is where the improvements Tom asked for come from.

**Fixing.** Fix every P0 and P1 on the branch. Collect every changed or new Hebrew string into one
before-and-after batch for §6-B.

**Record.** `gt-site/docs/2026-09-27-site-ux-gate.md`. At most 3 rounds.

**Acceptance:** D7, and the D8 batch.

### W6 — Simplify, verify, merge
1. `simplify` plus `ponytail-review` on the gt-site and gt-factory-os diffs. Record every cut and every
   skipped cut. Behaviour, copy, ARIA and harness facts are identical across it.
2. `verification-before-completion`: every D9 run, all later than the last code commit.
3. Run the copy checker at the gt-site PR head, before any merge (D8). Then merge on each PR's own
   green checks:
   - gt-factory-os: the harness, `SITE_FILES`, the §5.5 rows;
   - gt-site;
   - the brain: the `shopify-theme` skill; this file's stamp follows in W7.

**Acceptance:** D8, D9.

### W7 — Ship, prove, report

**With §6-A done.** The preview pushes in W5 used the same command against the preview theme. After
Tom's go (§6-C):
1. Stage from the merged head.
2. `npx -y @shopify/cli@4.8.2 theme push --store greenteaeveryday.myshopify.com --theme <preview id> --path <staged dir> --nodelete --json`,
   then run the drift check on the preview.
3. The same push with `--theme <live id> --allow-live`, then run the drift check on live.

**Without §6-A.**
1. Duplicate MAIN now, not earlier, so no admin edit is lost when it is swapped. That is the 19th of 20
   slots. If it fails, deleting a theme is Tom's call.
2. Upsert the whole staged set through the MCP, then run the drift check on that theme.
3. Hand Tom the exact theme id to publish.
4. After his click, run the drift check on live.

In both cases, `updatedAt` on every non-GT file in MAIN must be older than the duplicate's creation.
Otherwise duplicate again.

**Then:**
- D6 on the live page;
- `PUBLISH.md` updated, with rollback = push the previous staged set, or publish the pre-push duplicate;
- this file stamped;
- the §9 report.

**Acceptance:** D1, D6, D10.

## 5. Scope

**IN:** everything in §4.

**OUT — do not touch, do not "improve":**
- **The lead intake:** `website_lead_intake`, `sales-leads-poll`, `sales_core`. No new fields, no new
  `form_name`, no deploy, no edit of gt-site's stale copy.
- **The customer ordering portal** (`gt-factory-os/api/src/portal/`) and the staff portal repo.
- **The landing pages' own forms, buttons and publication.**
- **Syncing the full theme through the GitHub integration.**
- **Deleting any theme, and any theme-editor setting except the one named in §1.1.4.**
- **GTM or pixel configuration, prices, the WhatsApp number.**
- **Anything in Shopify** that is not a GT-set file.

## 6. Tom's part — the complete list. Nothing else is his.

**A. Before pasting this file, optional (about 3 minutes).**
1. In Shopify admin, install Shopify's free **Theme Access** app.
2. Create a password for himself; it arrives by email.
3. Add it in this cloud environment's settings (the environment menu in the session's title bar, then
   Edit) as the variable `SHOPIFY_CLI_THEME_TOKEN`. A new session picks it up. It is never pasted into
   the chat.

This is what makes continuous work on the live theme possible (§3.2). Without it, W7's fallback applies,
and publishing stays a click of his.

**B. In the brainstorm round (W2), a few one-line answers:**
1. The design as described, with the author's decisions of §1.1.
2. The automatic-close delay. The default is about 2 s.
3. **Copy approval mode:**
   - either the gate's COPY dimension GREEN plus the governor approves the batch, and Tom sees it in the
     report;
   - or the batch is sent to him before ship.

   The default is to send it to him. His answer is recorded, and the approved strings become §5.5 `U-16`…
   rows either way (D8).
4. **Only with §6-A done:** may the three superseded themes (`186686636273`, `166741213425`,
   `166708576497`) be deleted? The default is no.

**C. Going live (one word, after the SHIP message).** Send it with:
- the preview link;
- what will change on live:
  - the dialog;
  - the gated copy and visuals;
  - #22, #23 and #25;
  - the four landing pages' files. The pages stay unpublished, but live `?view=<slug>` will start
    sending real leads to the sales system, and those pages were never gated.

His "go" puts the GT set on the live theme. A "go" given earlier, before the design or the gate existed,
does not count. Without the §6-A token, it is his Publish click on the theme id you give him instead.
- The D6 test lead uses the business's own public number `054-398-2444` and the name
  `בדיקת מערכת — להתעלם`. Tell him in the same message that this one lead will reach the sales queue
  and the staff alert.

**D. Nothing else**, except any confirmation the Shopify MCP asks of him for a mutation (§0); keep
those to one duplicate and one upsert per round. He is not asked to verify anything:
- merges are yours under the gates;
- the harness, the gate and the checks are yours;
- a WebKit gap is reported, not handed to him.

## 7. Landmines — do not rediscover these

1. **"The push deleted half the store."** `shopify theme push` deletes remote files that are not in the
   local directory unless you pass `--nodelete`. Use both `--nodelete` and a staging directory that
   holds only the GT set; `stage_theme` asserts the second.
2. **"The business entry vanished from live."** The repo's `templates/index.json` has `settings: {}` and
   the switch defaults to false (`build_theme.py`); two more admin settings live in the same object.
   `stage_theme` takes `sections.main.settings` from the target theme (§1.1.4). The drift check compares
   parsed JSON.
3. **"The tab logo went back to the old one."** Something wrote `config/settings_data.json`, or a theme
   duplicated before 2026-09-25 16:02Z was published. That file is never in the GT set. Duplicate only
   from MAIN, only at the moment of use.
4. **"The thank-you showed but no lead arrived."** `elapsed_ms < 3000` or a filled honeypot gets a
   silent `ok` (table B). Measure from navigation start; test the fast-autofill case (D4); keep the
   honeypot's attributes.
5. **"It says we already got it, but the message is missing."** The same phone on the same day gets
   `was_new: false` and no note. That is by design. The sent state covers it; do not "fix" the intake.
6. **"CORS error in the harness."** The intake allows only the three origins in table B. Render the
   preview through `gteveryday.com?preview_theme_id=…`, and stub the endpoint anyway.
7. **"The preview shows the live theme."** The preview link sets a cookie. In curl use
   `curl -c jar -b jar -L`; in Playwright keep one context per viewport, as the harness does.
8. **"Chromium cannot load the page's images."** The agent proxy's CA is in Node's store but not
   Chromium's. The harness's `viaNode` route fetches through Node, with TLS still verified. Never
   disable verification.
9. **"The harness hit a challenge page."** Cloudflare sometimes challenges a run. Re-run only that
   viewport with `SITE_VPS`; the facts file merges.
10. **"`upsertedThemeFiles` came back empty."** It always does, even on success. Verify with checksums
    (the drift check), never with that field.
11. **"themeDuplicate failed."** The store is at its 20-theme limit (17 on 2026-09-27; the preview
    makes 18, the fallback's duplicate 19). Reuse the one preview theme; deleting themes is Tom's call
    (§6-B4).
12. **"The patch's anchor was not found."** A later patch anchors on the form markup. Put the dialog
    patch after `patch_ipad` and just before `validate.js` in `tools/build.sh`, anchor on stable markers, and keep the exact-count asserts.
13. **"Hebrew in my patch comments failed the copy checker."** The checker reads every Hebrew literal
    in the files it scans, comments included. Write comments in English.
14. **"The checker passes but the new copy was never checked."** `SITE_FILES` did not name the file
    that holds it. Extend `SITE_FILES` in the same work (D8), then run `--self-test`.
15. **"CI failed on price tokens or `left:-9999px`."** The gt-site `build` workflow bans `₪`,
    `מחיר מומלץ` and large negative offsets in served files. Hide the honeypot by clipping, as the form
    already does.
16. **"The phone zoomed in when the field was tapped."** iOS zooms on focus when inputs are under 16 px.
    Use 16 px or more. Not observable in Chromium; it is a rule.
17. **"The page jumped to the top when the dialog closed on iPhone."** That is `position: fixed` body
    locking. Use `html.cm-lock` (overflow) and restore nothing by hand. It is a rule, reported as not
    observed on WebKit.
18. **"The button hid under the keyboard."** Size the sheet with `dvh`, not `vh`; keep the submit button
    in the scrolling content, not fixed to the bottom.
19. **"Back left the site."** Opening without `pushState` means the phone's back button navigates away.
    Copy `cmOpen`'s pattern (`src/index.html` around 1805–1808 at `4c45338`).
20. **"The form in the dialog was invisible, then slid in."** `#pform` has the class `rv`, which is
    `opacity: 0` until an IntersectionObserver adds `.on` when `#contact` scrolls into view. When the
    dialog borrows the form before that, add `.on` at once, with no transition. axe on an invisible form
    is not evidence.
21. **"The product window's button opened two windows."** `הוסיפו לתפריט` sits inside `#fmodal`. Close
    it first, then open the dialog, and return focus to the card that opened `#fmodal`.
22. **"I edited `src/index.html` and CI failed."** It is generated. Edit the patches or
    `src/index.en.html` with `tools/remap_string_ids.py`, rebuild, and commit the outputs.
23. **"The PR got auto-watched."** Opening a PR subscribes the session server-side. Call
    `unsubscribe_pr_activity` right after each `create_pull_request`.
24. **"I printed the theme password."** Test presence with `test -n`, never expand it into output, and
    pass it only through the environment variable the CLI reads.

## 8. Halt conditions (additions to the inherited set)

- **A push without `--nodelete`, or a staging directory holding any file outside the GT set** → STOP.
- **Any write to the live theme without Tom's §6-C word** → STOP.
- **The deployed intake differs from table B** → STOP and surface before form code.
- **A GT file in MAIN matches no gt-site commit** (someone edited live code directly) → pull it into the
  repo first. If it conflicts with `main`'s intent → STOP and surface. `templates/index.json` is exempt:
  its settings are theme-owned (§1.1.4).
- **The gate is not SHIP after round 3** → do not ship; report.

## 9. Final report

In Hebrew, to Tom, in the shape of `gt-factory-os/docs/superpowers/plans/2026-09-26-customer-portal-availability-report.md`:
1. What a stranger can now watch working, end to end: tap any button, the dialog opens, send, it closes
   itself, the page is where it was, the lead is in the sales queue.
2. D1–D10 ✅/❌ with evidence pointers — no partial credit.
3. The numbers:
   - live-versus-repo drift (0 of N);
   - harness facts per viewport;
   - axe;
   - the copy checker;
   - CI runs;
   - lead count before and after.
4. The artifacts:
   - PRs and merge SHAs;
   - live checksums;
   - the gate record;
   - screenshots (before and after, phone and desktop);
   - the D6 lead's id and time, with no personal data.
5. What is still Tom's, and what is genuinely unfinished, including every WebKit rule applied but not
   observed.
6. The single next action.

If anything is not ready, say so first and plainly. Then change this file's status line.
