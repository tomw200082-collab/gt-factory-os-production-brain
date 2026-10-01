# GT Pulse Unit A — release packet (pre-production, 2026-10-01)

**This is a packet for a later decision, not a release.** Nothing here was merged, deployed,
migrated, flagged or backfilled in production. Tom deferred production on 2026-09-30.

## 1. What is being released

| Lane | Branch | Final SHA | PR | Checks on this exact head |
|---|---|---|---|---|
| Backend / DB | `feat/gt-pulse-a-sales-contact-loop` | `9d423c1fa77748f61292b0e875059ab48d8ff825` | [#329](https://github.com/tomw200082-collab/gt-factory-os/pull/329) draft, mergeable clean, base `04cb0f6` | `sales-db`, `staff-mail`, `typecheck` green |
| Portal | `feat/gt-pulse-a-sales-corridor` | `a7ccffddb0693ec5c24ac9ab38a07ed06ab6d5a6` | [#239](https://github.com/tomw200082-collab/gt-factory-os-portal/pull/239) draft, mergeable clean, base `5e45b2d` | `ci` (portal-pr-guard) green |

- Migration: `db/migrations/0362_sales_activity_tasks.sql`, the highest numbered file. It is unapplied in every
  environment. sha256 `b9fca7e033b3f1356ba64e912862c11bb2391ec0761d42e60d7a458b7d764fac`. Recheck the slot
  against `main` immediately before applying it.
- Backfill script: `db/scripts/gt_pulse_a_task_backfill.sql`, sha256
  `be19caecf2f56ef409ed96546c8c0ddb9409f0453ea24cd83b0d89ec3fac5ee1`.
- Design: Sales-Machine `docs/superpowers/specs/2026-10-01-gt-pulse-a-preprod-closure-design.md`
  (D1–D13), plan `docs/superpowers/plans/2026-10-01-gt-pulse-a-preprod-closure.md`.

## 2. Evidence on the final heads

- **pgTAP:** 0318 18/18, 0322 24/24, 0324 10/10, 0360 22/22, 0361 27/27, 0362 88/88. The backfill
  preview/apply/stale-digest/idempotence script passes. All of this ran on a CI-replica disposable
  PostgreSQL 17.
- **Node:**
  - order-intake Vitest 267/267, including the two-connection wake race and the order-line reply DB tests.
  - API `sales_workspace_tasks` 14/14, `sales_workspace` 14/14, `sales_leads_poll_alerts` 38/38.
  - Root typecheck exit 0.
- **Portal:**
  - Vitest 1536/1536; typecheck, lint and build all exit 0.
  - Mocked sales Chromium: 55 pass locally. 4 fail locally and are an environment artifact: the
    same 4 `tel:` tests fail identically on base `1ba2c98` with local Chromium 1194, and pass in PR
    CI on Chromium 1217.
- **Connected isolated staging:** 22/22 at 390px and 22/22 at 1280px
  (`2026-10-01-gt-pulse-a-connected/proof-*.log`).
  - Stack: local GoTrue (ES256 JWKS), production portal build, the real API with
    `NODE_ENV=production` and no dev shim, and Postgres built from `db/migrations`. Identities are
    synthetic only.
  - **Login and deep link:** a signed-out staff link goes through login with the destination
    kept, and the magic link lands on the lead.
  - **Atomic save:** a note, action and date save atomically, and the request correlates to the
    committed `lead_event` rows and the owned `task` row.
  - **Timeout and retry:** a timeout after commit plus a reload keeps the draft; the retry reuses
    the request ID and writes one fact.
  - **Rep isolation:** a rep is denied another owner's timeline (403), sees only their own leads
    and their own activity feed, and gets the approved "unavailable" state on a foreign deep link.
  - **Entry points and routing:** Today, Leads and Attention all save through the atomic command.
    An order-line reply routes one reply task to the owner.
  - **Date floor:** a typed past date is lifted to the first schedulable date.
  - **Manager:** reads everything and holds the unowned queue.
- **UX:**
  - Fixture render gate and connected five-lens audit: first pass, repairs, then a re-run (see
    `2026-10-01-gt-pulse-a-ux-dispositions.md` and the governor verdict below).
  - Connected screenshots cover 320/390/430/1280, dark (the real user preference) and reduced
    motion. Keyboard reaches the task actions for both rep and manager.
- **Reviews:**
  - Backend whole-branch review: 0 Critical. I1, I2 and M1–M4 fixed (`27538a7`). M5 (org counts
    shown to a rep) accepted: counts only, no rows.
  - Portal whole-branch review: 0 Critical. Important #1 and #2 fixed (`a7ccffd`, `9d423c1`);
    Minor #4 and #7 fixed; the rest are recorded.
  - Ponytail review: lean.

## 3. Production preflight (read-only, observed 2026-10-01 05:07–06:20 UTC)

| Item | Observed | Meaning |
|---|---|---|
| Supabase `rvadsozabmxkkrktwgnv` | `sales_core.task` absent; 261 leads | 0362 not applied |
| Supabase branches | `main`, `bom-cluster-shadow` only | no paid branch exists |
| Vercel portal production | `dpl_CuXtU3i8wc1Rb3NzyPMU1Sn5MWqL` READY at `5e45b2d` (portal `main`) | no GT Pulse code live |
| Railway `gt-factory-os-api` production | SUCCESS deployment 2026-09-29 20:54 UTC, `reason=deploy`, **no commit SHA in metadata** (a CLI upload one minute after a `04cb0f6` git deploy) | source SHA not provable; the release must deploy from a git SHA |
| Railway `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` | **`true`** | Contradicts Sales-Machine `CURRENT_STATE.md` ("remains `false`"). `order_intake.wa_event_log` holds 4 non-dry-run outbound `first_menu` sends, the last at 2026-09-30 14:32 UTC. This branch adds no sending path. **Tom must confirm or reverse this; it was not touched.** |
| Active sales users | 2 `admin`, 4 `planner`, 0 `sales_rep` | Everyone is a manager today; D3 rep scope is future-proofing |

## 4. Ordered procedure for the later production session

Do these only after Tom's explicit production instruction.

1. **Preflight, re-run and record:**
   - Stock-truth check.
   - `main` unmoved, or re-merge and re-verify.
   - 0362 is still the next free slot.
   - `rebuild_verifier()=0`.
   - The outreach flag's value is decided by Tom.
2. **Backend:**
   - Merge #329.
   - Apply 0362 to production. Checksum as above.
   - Deploy the API **from the merge SHA via git**, not a CLI upload.
   - Verify `/health`, `GET /queries/sales/tasks` (401 unauthenticated) and `to_regclass('sales_core.task')`.
3. **Portal:**
   - Merge #239 and deploy to the same Vercel project.
   - Signed-out staff deep link → login → lead, for a real manager.
   - Record one activity on a synthetic or internal lead and correlate it to its committed rows.
4. **Real email:** confirm one staff alert email via Resend opens the right lead. This is the only
   part staging could not exercise.
5. **Backfill:**
   - Run the read-only preview on production:
     `psql -X -v ON_ERROR_STOP=1 -f db/scripts/gt_pulse_a_task_backfill.sql` → `PREVIEW_TOTAL|<n>|<digest>`.
   - Present the exact count and digest to Tom.
   - Apply only with his count-specific written go:
     `-v gt_pulse_apply=YES -v gt_pulse_expected_count=<n> -v gt_pulse_expected_digest=<digest>`.
   - Per D8, contactless leads that have an owner route to that owner.
6. **`activity_required`:** stays off until Today, Leads and Attention are proven live on the
   atomic command. It is a separate step.

## 5. Rollback

- **Portal:** Vercel instant rollback to `dpl_CuXtU3i8wc1Rb3NzyPMU1Sn5MWqL`.
- **API:** redeploy the previous git SHA.
- **0362:** additive (new tables, functions, triggers and one partial index), so no data is
  dropped. If behaviour must stop, drop the two routing triggers (`lead_event_task`,
  `lead_task_owner`) and the `wa_event_log` stop-lock trigger in one transaction. Keep the tables
  and history.
- **Backfill:** cancel only `source_key like 'bootstrap:%'` open tasks, with actor and reason. Never
  delete.

## 6. Not proven here (HOLD until the production session or a real device)

- WebKit/iOS keyboard-open save.
- Screen reader behaviour.
- iOS date-input locale.
- Resend delivery to real inboxes.
- `tel:` on real phones.
- Railway runtime parity with the source.

## 7. One decision for Tom

Production go/no-go for this packet, together with the outreach-flag question in §3.

## 8. Release verifier (2026-10-01, final heads)

Verdict **CONDITIONALLY_SAFE**, no blockers.
- Heads match origin and are 0 behind `main`. Trees are clean.
- Every portal file is in the tranche 185 manifest.
- No frozen flag, stock or factory-core change.
- 0362 is `main`'s 0361 + 1.
- Every Hebrew string is in the register.

Conditions and their status:
1. `supabase/functions/sales-leads-poll/_lib/email.ts` is in scope: it is Unit A plan task 1 (the staff email opens the lead).
2. The PR's `ux-gate` job is label-gated and was skipped. The five-lens gate ran in-session (section 2 and the dispositions file) with the governor verdict. The later production session may also label-trigger it on the final head.
3. PRs stay draft until Tom's go.

## 9. Update 2026-10-01 07:40 UTC

Tom approved the B-FLOW-04 string. Portal final head is now **`4b94597f5c953f048dec4574375102beb16d13e7`**: the hint is shown under a disabled Save and linked by `aria-describedby`. Vitest 1537/1537; typecheck, lint and build exit 0. The governor's connected-audit condition on copy is met. The remaining HOLD is WebKit/iOS keyboard proof on a real device. The backend head is unchanged (`9d423c1`).
