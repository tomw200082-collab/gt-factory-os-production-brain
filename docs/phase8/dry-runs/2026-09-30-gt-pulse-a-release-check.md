# GT Pulse Unit A — release-check equivalent

**UTC:** 2026-09-30. **Method:** read-only equivalent of `.claude/commands/release-check.md`; agent dispatch unavailable. This is a scope and evidence verdict, not merge/deploy authorization.

## Targets and git state

| Repo/lane | Base | Local head | Remote tree-equivalent head | Worktree |
|---|---|---|---|---|
| Backend/API/DB/Edge | `0e3c6fb49f82e9f9bddf38e478d78c17f2173878` | `c50e59195dbd8922a80f4ce93e129550e64bf759` | `fa9c0454dd0856594678448c750fa22b09e58f29` | clean |
| Sales portal/auth | `5e45b2d91cc8938ec1945925e46f481b9146c404` | `3c8f987953e827b7a7ce3e86eea373017eab6d23` | `103354bdce2e93cc4b19232dadc46745640d3ffb` | clean |

Separate branches preserve the repo lanes. Backend diff: 17 files, 2,168 insertions/146 deletions, including additive migration `0362`, API, wake, staff email and tests. Portal diff: 45 files, 1,437 insertions/202 deletions, entirely within tranche 185's allowed sales/auth/test/docs manifest. No `.env*`, credential, `CLAUDE.md` or `EXECUTION_POLICY.md` path appears in either diff. Production migration is absent from the portal branch. Frozen customer outreach flag is neither enabled nor edited. `activity_required` is seeded false and has **not** been switched on. Migration 0362 and tranche 185 were absent on default branches at the read-only recheck; target migration history remains unresolved.

## Evidence classification

- **[Local, exact portal tree]** 1,517/1,517 unit, 57/57 relevant sales Chromium, build, typecheck, lint 0 errors/558 warnings, registry presence 1/1. Synthetic role/width matrix 40/40 with zero horizontal overflow. The full `@mocked` PR-guard Chromium command reran with JSON reporting: 125 expected, 0 skipped, 0 unexpected, 0 flaky, exit 0. This is a local equivalent, not GitHub's PR-triggered check.
- **[Push CI, exact final backend tree]** [Run 36676625217](https://github.com/tomw200082-collab/gt-factory-os/actions/runs/36676625217) on remote `fa9c0454dd0856594678448c750fa22b09e58f29` (tree `234d93bd1f48c44e92c24f5947b500206091a5d8`) completed success in both jobs. Root typecheck, staff alert 38/38, new/neighboring sales pgTAP through assertion 68 with no failure, guarded backfill stale-preview rejection plus three synthetic paths and idempotent rerun, two-connection wake/lead DB 18/18, role/activity API 11/11 and legacy workspace 14/14. The disposable Postgres migrations applied, including 0362. This is isolated CI evidence, not production migration or authenticated browser evidence. The same-display-name request-ID takeover was reproduced RED in [run 36676430834](https://github.com/tomw200082-collab/gt-factory-os/actions/runs/36676430834), then fixed by binding replay to the original account; an independent reviewer rechecked the final diff.
- **[Local, final backend tree]** Root typecheck passed; wake unit 23/23 passed on the preceding code tree (subsequent changes were backfill SQL and role-test assertions, both covered by exact-tree CI). Without local PostgreSQL, 18 DB-gated tests skip. `api npm test` failed at tsx IPC permission; broad `node --import tsx --test` hit unrelated database-dependent failures and was stopped. API package typecheck has inherited unrelated diagnostics.
- **[Production SQL, read-only 2026-09-30]** 257 leads, 183 open, 150 open unassigned; `sales_core.task` absent, `activity_required` absent, migration-history count for 0362 zero. Provisional pre-schema candidate counts: 148 manager first-contact, 2 manager call, 33 owned call. These are not the post-schema guarded preview or a write authorization.
- **[Unverifiable]** Actual deployed backend/portal SHAs, authenticated browser → API → DB journey, outreach environment flag, WebKit keyboard, exact post-schema production backlog preview and rollback execution. No production write/deploy occurred.

## Verdict: BLOCKED for merge/deploy

The lane separation and frozen outreach boundary are respected, and the branches are available for human review. The exact backend tree passed isolated PostgreSQL CI. The actual PR-triggered portal guard, connected auth/DB corridor, exact deployed target SHA/flags and count-specific backlog authorization are not proven. UX gate remains HOLD. Do not switch `activity_required`, run the batch, merge or call this shipped on this evidence. The portal's proposed Hebrew copy register also awaits Tom's exact-entry approval.

**Prepared rollback after a separately approved batch:** first disable `activity_required` if it was activated and preserve the existing outreach freeze. In one short transaction, lock `sales_core.task`, compare the previewed count and digest of *open* `source_kind='bootstrap'` rows to the approved batch record, then set `status='cancelled'`, `cancelled_by='system:gt-pulse-rollback'`, `cancelled_at=now()`, and `cancelled_reason='gt-pulse-backfill-rollback'` only on those open rows. The task trigger appends a cancellation event; done tasks and all history remain. Verify zero open bootstrap rows and recheck the old portal/API compatibility. This is a reviewable rollback recipe, **not** an executed or approved production write.
