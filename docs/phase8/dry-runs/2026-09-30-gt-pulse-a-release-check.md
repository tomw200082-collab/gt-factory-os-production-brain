# GT Pulse Unit A — release-check equivalent

**UTC:** 2026-09-30. **Method:** read-only equivalent of `.claude/commands/release-check.md`; agent dispatch unavailable. This is a scope and evidence verdict, not merge/deploy authorization.

## Targets and git state

| Repo/lane | Base | Local head | Remote tree-equivalent head | Worktree |
|---|---|---|---|---|
| Backend/API/DB/Edge | `0e3c6fb49f82e9f9bddf38e478d78c17f2173878` | `8865f581a00188e99f2f5278b66b9dc35447535d` | `ee84be34cdc1a76596a1e1d70a2a5f66d0ec6050` | clean |
| Sales portal/auth | `5e45b2d91cc8938ec1945925e46f481b9146c404` | `3c8f987953e827b7a7ce3e86eea373017eab6d23` | `103354bdce2e93cc4b19232dadc46745640d3ffb` | clean |

Separate branches preserve the repo lanes. Backend diff: 17 files, 2,168 insertions/146 deletions, including additive migration `0362`, API, wake, staff email and tests. Portal diff: 45 files, 1,437 insertions/202 deletions, entirely within tranche 185's allowed sales/auth/test/docs manifest. No `.env*`, credential, `CLAUDE.md` or `EXECUTION_POLICY.md` path appears in either diff. Production migration is absent from the portal branch. Frozen customer outreach flag is neither enabled nor edited. `activity_required` is seeded false and has **not** been switched on. Migration 0362 and tranche 185 were absent on default branches at the read-only recheck; target migration history remains unresolved.

## Evidence classification

- **[Local, exact portal tree]** 1,517/1,517 unit, 57/57 relevant sales Chromium, build, typecheck, lint 0 errors/558 warnings, registry presence 1/1. Synthetic role/width matrix 40/40 with zero horizontal overflow. The full `@mocked` PR-guard Chromium command reran with JSON reporting: 125 expected, 0 skipped, 0 unexpected, 0 flaky, exit 0. This is a local equivalent, not GitHub's PR-triggered check.
- **[Older CI only]** Backend `12fa6c3` passed pgTAP 65/65, two-connection DB cases 18/18 and role/API 8/8. This is not CI for the final migration/API head.
- **[Local, final backend tree]** Root typecheck and wake unit 23/23 passed. Eighteen DB-gated tests skip without a local disposable PostgreSQL. `api npm test` failed at tsx IPC permission; `node --import tsx --test` reached unrelated database-dependent suites and was stopped after inherited failures. API package typecheck has pre-existing unrelated diagnostics. Latest push CI is not exposed by the connected GitHub wrapper, which lists PR-triggered runs only.
- **[Production SQL, read-only 2026-09-30]** 257 leads, 183 open, 150 open unassigned; `sales_core.task` absent, `activity_required` absent, migration-history count for 0362 zero. Provisional pre-schema candidate counts: 148 manager first-contact, 2 manager call, 33 owned call. These are not the post-schema guarded preview or a write authorization.
- **[Unverifiable]** Actual deployed backend/portal SHAs, authenticated browser → API → DB journey, outreach environment flag, WebKit keyboard, exact post-schema production backlog preview and rollback execution. No production write/deploy occurred.

## Verdict: BLOCKED for merge/deploy

The lane separation and frozen outreach boundary are respected, and the branches are available for human review. The final backend migration and DB race checks, actual PR-triggered portal guard, connected auth/DB corridor, exact target SHA/flags and count-specific backlog authorization are not proven. UX gate remains HOLD. Do not switch `activity_required`, run the batch, merge or call this shipped on this evidence. The portal's proposed Hebrew copy register also awaits Tom's exact-entry approval.

**Prepared rollback after a separately approved batch:** first disable `activity_required` if it was activated and preserve the existing outreach freeze. In one short transaction, lock `sales_core.task`, compare the previewed count and digest of *open* `source_kind='bootstrap'` rows to the approved batch record, then set `status='cancelled'`, `cancelled_by='system:gt-pulse-rollback'`, `cancelled_at=now()`, and `cancelled_reason='gt-pulse-backfill-rollback'` only on those open rows. The task trigger appends a cancellation event; done tasks and all history remain. Verify zero open bootstrap rows and recheck the old portal/API compatibility. This is a reviewable rollback recipe, **not** an executed or approved production write.
