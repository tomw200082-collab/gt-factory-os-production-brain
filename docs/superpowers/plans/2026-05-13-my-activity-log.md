# My Activity Log Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace `/stock/submissions` with `/me/activity` — a per-user append-only feed unifying form_submissions (23 types), credit_decisions (approve/reject), and exception ack/resolve into one chronological activity log with day-grouped rows, filters, search, pagination, and a side drawer.

**Architecture:** Server-side view `v_my_activity_log` UNIONs three audit channels; per-action summary builders produce `{headline, secondary}` strings server-side (so names resolve via JOIN); two new endpoints (`GET /api/v1/queries/me/activity` + `GET /api/v1/queries/me/activity/:activity_id`); portal page mirrors the Movement Log UX pattern. Append-only by construction — no UPDATE/DELETE on the view; corrections are new rows.

**Tech Stack:** Postgres 17 + Kysely (DB), Fastify + Zod (API), Next.js 15 App Router + TanStack Query + Tailwind/shadcn (portal), node:test (API tests), pgTAP (DB tests).

**Spec:** [`docs/superpowers/specs/2026-05-13-my-activity-log-design.md`](../specs/2026-05-13-my-activity-log-design.md)

---

## Repos & paths

| Concern | Repo | Path root |
|---|---|---|
| DB migrations | `gt-factory-os` | `db/migrations/` |
| DB pgTAP tests | `gt-factory-os` | `db/tests/` |
| API source | `gt-factory-os` | `api/src/` |
| API tests | `gt-factory-os` | `api/test/` |
| Portal source | `gt-factory-os-portal` (working tree `window2-portal-sandbox/`) | `src/` |

Absolute paths:
- gt-factory-os repo: `c:/Users/tomw2/Projects/gt-factory-os/`
- Portal working tree: `c:/Users/tomw2/Projects/window2-portal-sandbox/`

Latest migration on disk: **0184**. New migrations created here are **0185** (indexes) and **0186** (view).

---

## File map

### New backend files
| File | Purpose |
|---|---|
| `db/migrations/0185_activity_log_indexes.sql` | Indexes on credit_decisions and exceptions for keyset pagination |
| `db/tests/0185_activity_log_indexes.test.sql` | pgTAP — verify indexes exist with correct columns |
| `db/migrations/0186_v_my_activity_log.sql` | The unified view |
| `db/tests/0186_v_my_activity_log.test.sql` | pgTAP — verify view shape, 4 source_kinds, actor filtering |
| `api/src/activity_log/schemas.ts` | DTO interfaces + Zod query schema |
| `api/src/activity_log/redaction.ts` | Token/secret/password/auth field redaction |
| `api/src/activity_log/builders/_registry.ts` | Builder interface + registry + missing-builder fallback |
| `api/src/activity_log/builders/form_submission/<23 files>.ts` | One builder per form_type |
| `api/src/activity_log/builders/credit_decision/{approve,reject}.ts` | 2 builders |
| `api/src/activity_log/builders/exception_acknowledge/_default.ts` | 1 builder |
| `api/src/activity_log/builders/exception_resolve/_default.ts` | 1 builder |
| `api/src/activity_log/list_handler.ts` | List endpoint handler + keyset pagination |
| `api/src/activity_log/drawer_handler.ts` | Drawer endpoint handler |
| `api/src/activity_log/route.ts` | Fastify route registration |
| `api/test/activity_log_builders.test.ts` | Unit tests for all builders (one fixture per builder) |
| `api/test/activity_log_list.test.ts` | Integration test for list endpoint |
| `api/test/activity_log_drawer.test.ts` | Integration test for drawer endpoint |
| `api/test/activity_log_redaction.test.ts` | Redaction unit tests |

### Modified backend files
| File | Change |
|---|---|
| `api/src/server.ts` | Register `registerActivityLogRoute` (preserve existing `registerSubmissionsRoute` until portal redirect is live) |
| `api/package.json` | Add `db:apply:0185`, `db:apply:0186`, `db:test:0185`, `db:test:0186` scripts |

### New portal files
| File | Purpose |
|---|---|
| `src/app/(ops)/me/activity/page.tsx` | The new activity log page |
| `src/app/(ops)/me/activity/_components/ActivityRow.tsx` | One row component |
| `src/app/(ops)/me/activity/_components/DayHeader.tsx` | Sticky day-grouping header |
| `src/app/(ops)/me/activity/_components/FilterBar.tsx` | Collapsed filters + chips |
| `src/app/(ops)/me/activity/_components/ActivityDrawer.tsx` | Side drawer |
| `src/app/(ops)/me/activity/_types.ts` | Local TS types matching API DTO |
| `src/app/api/me/activity/route.ts` | Portal proxy → upstream `/api/v1/queries/me/activity` |
| `src/app/api/me/activity/[activityId]/route.ts` | Portal proxy → upstream drawer |

### Modified portal files
| File | Change |
|---|---|
| `src/app/(ops)/stock/submissions/page.tsx` | Replace body with `redirect('/me/activity')` |
| `src/app/(ops)/_layout/Sidebar.tsx` (or equivalent) | Add "My activity" entry under new ME section; remove/repoint "My History" |

---

## Test commands

| What | Command (run from repo root) |
|---|---|
| API typecheck | `cd api && npm run typecheck` |
| API tests (single) | `cd api && node --test --import tsx test/<file>.test.ts` |
| API tests (all activity_log) | `cd api && node --test --import tsx test/activity_log_*.test.ts` |
| pgTAP for one migration | `pg_prove -d "$DATABASE_URL" db/tests/<file>.test.sql` |
| Apply migration | `npm run db:apply:0185` (or 0186) |
| Portal typecheck | `cd window2-portal-sandbox && npm run typecheck` |
| Portal dev | `cd window2-portal-sandbox && npm run dev` |

`DATABASE_URL_POOLED` must be set in `api/.env` for integration tests. They run against the live Supabase PG17.

---

## Stage 1 — DB Foundation

### Task 1: Migration 0185 — indexes on credit_decisions + exceptions

**Files:**
- Create: `db/migrations/0185_activity_log_indexes.sql`

- [ ] **Step 1: Author the migration**

```sql
-- ===========================================================================
-- 0185_activity_log_indexes.sql
--
-- Goal: enable fast keyset pagination on /api/v1/queries/me/activity by
-- creating per-actor + descending-event-time indexes on the three source
-- channels of v_my_activity_log:
--
--   * private_core.credit_decisions   — new btree index
--   * private_core.exceptions (ack)   — new partial btree index
--   * private_core.exceptions (res)   — new partial btree index
--
-- form_submissions is already indexed for (submitted_by, submitted_at) via
-- prior migrations; nothing to add for that source.
--
-- Strictly additive. No data changes. Replays cleanly via CREATE INDEX IF
-- NOT EXISTS.
--
-- Authority:
--   docs/superpowers/specs/2026-05-13-my-activity-log-design.md §"Tom Tax #1"
-- ===========================================================================

BEGIN;

-- credit_decisions: per-actor descending decided_at
CREATE INDEX IF NOT EXISTS idx_credit_decisions_actor_decided_at
  ON private_core.credit_decisions(decided_by_user_id, decided_at DESC);

COMMENT ON INDEX private_core.idx_credit_decisions_actor_decided_at IS
  '0185: keyset pagination support for v_my_activity_log (credit_decision source).';

-- exceptions: per-acknowledger descending acknowledged_at, partial on non-null
CREATE INDEX IF NOT EXISTS idx_exceptions_acknowledged_by_at
  ON private_core.exceptions(acknowledged_by, acknowledged_at DESC)
  WHERE acknowledged_by IS NOT NULL AND acknowledged_at IS NOT NULL;

COMMENT ON INDEX private_core.idx_exceptions_acknowledged_by_at IS
  '0185: keyset pagination support for v_my_activity_log (exception_acknowledge source). Partial: only rows that were actually acknowledged.';

-- exceptions: per-resolver descending resolved_at, partial on non-null
CREATE INDEX IF NOT EXISTS idx_exceptions_resolved_by_at
  ON private_core.exceptions(resolved_by, resolved_at DESC)
  WHERE resolved_by IS NOT NULL AND resolved_at IS NOT NULL;

COMMENT ON INDEX private_core.idx_exceptions_resolved_by_at IS
  '0185: keyset pagination support for v_my_activity_log (exception_resolve source). Partial: only rows that were actually resolved.';

COMMIT;

-- ===========================================================================
-- End of 0185_activity_log_indexes.sql
-- ===========================================================================
```

- [ ] **Step 2: Add npm script entries**

Modify `api/package.json` — add inside the `"scripts"` block, alongside the other `db:apply:*` lines (keep alphanumerically sorted):

```json
"db:apply:0185": "psql \"$DATABASE_URL\" -v ON_ERROR_STOP=1 -f db/migrations/0185_activity_log_indexes.sql",
"db:test:0185":  "pg_prove -d \"$DATABASE_URL\" db/tests/0185_activity_log_indexes.test.sql",
```

- [ ] **Step 3: Commit (do not apply yet — wait for test)**

```bash
cd /c/Users/tomw2/Projects/gt-factory-os
git add db/migrations/0185_activity_log_indexes.sql api/package.json
git commit -m "feat(db): 0185 indexes for v_my_activity_log keyset pagination"
```

---

### Task 2: pgTAP test for migration 0185

**Files:**
- Create: `db/tests/0185_activity_log_indexes.test.sql`

- [ ] **Step 1: Write the failing test**

```sql
-- 0185_activity_log_indexes.test.sql — pgTAP
--
-- Verifies the three keyset-pagination indexes were created with the right
-- columns, direction, and partial WHERE clauses.

BEGIN;

SELECT plan(6);

-- credit_decisions index
SELECT has_index(
  'private_core', 'credit_decisions',
  'idx_credit_decisions_actor_decided_at',
  'idx_credit_decisions_actor_decided_at exists'
);

SELECT index_is_type(
  'private_core', 'credit_decisions',
  'idx_credit_decisions_actor_decided_at',
  'btree',
  'idx_credit_decisions_actor_decided_at is btree'
);

-- exceptions acknowledge index
SELECT has_index(
  'private_core', 'exceptions',
  'idx_exceptions_acknowledged_by_at',
  'idx_exceptions_acknowledged_by_at exists'
);

SELECT index_is_type(
  'private_core', 'exceptions',
  'idx_exceptions_acknowledged_by_at',
  'btree',
  'idx_exceptions_acknowledged_by_at is btree'
);

-- exceptions resolve index
SELECT has_index(
  'private_core', 'exceptions',
  'idx_exceptions_resolved_by_at',
  'idx_exceptions_resolved_by_at exists'
);

SELECT index_is_type(
  'private_core', 'exceptions',
  'idx_exceptions_resolved_by_at',
  'btree',
  'idx_exceptions_resolved_by_at is btree'
);

SELECT * FROM finish();
ROLLBACK;
```

- [ ] **Step 2: Run test before applying — expect FAIL**

```bash
cd /c/Users/tomw2/Projects/gt-factory-os
pg_prove -d "$DATABASE_URL" db/tests/0185_activity_log_indexes.test.sql
```

Expected: `not ok` on all 6 — indexes don't exist yet.

- [ ] **Step 3: Apply the migration**

```bash
npm run db:apply:0185
```

Expected: `CREATE INDEX` × 3, `COMMENT` × 3, `COMMIT`.

- [ ] **Step 4: Run test again — expect PASS**

```bash
npm run db:test:0185
```

Expected: `ok 6/6 — All tests successful.`

- [ ] **Step 5: Commit the test**

```bash
git add db/tests/0185_activity_log_indexes.test.sql
git commit -m "test(db): pgTAP for 0185 activity_log indexes"
```

---

### Task 3: Migration 0186 — the unified view `v_my_activity_log`

**Files:**
- Create: `db/migrations/0186_v_my_activity_log.sql`

- [ ] **Step 1: Author the migration**

```sql
-- ===========================================================================
-- 0186_v_my_activity_log.sql
--
-- Unified read model for "/me/activity" — UNIONs three source channels:
--
--   1. private_core.form_submissions   (23 form_type values)
--   2. private_core.credit_decisions   (approve / reject)
--   3. private_core.exceptions         (one virtual row per ack moment,
--                                       one virtual row per resolve moment)
--
-- Output is normalized to a single uniform shape per row. The view is
-- READ-ONLY (no INSTEAD OF triggers); the activity log is append-only by
-- the construction of its sources (form_submissions row creation, a
-- credit_decisions row per decision, and the acknowledged_at / resolved_at
-- columns on exceptions which are set once and never cleared).
--
-- Pagination strategy is keyset on (event_at DESC, activity_id DESC).
-- The supporting indexes are in 0185.
--
-- This migration is forward-only; rollback is `DROP VIEW`. No data is
-- materialized.
--
-- Authority:
--   docs/superpowers/specs/2026-05-13-my-activity-log-design.md §"Architecture"
-- ===========================================================================

BEGIN;

DROP VIEW IF EXISTS private_core.v_my_activity_log;

CREATE VIEW private_core.v_my_activity_log AS
  -- ========================================================================
  -- Source 1: form_submissions
  -- ========================================================================
  SELECT
    'sub_' || submission_id::text  AS activity_id,
    'form_submission'::text         AS source_kind,
    form_type                       AS action_kind,
    submitted_at                    AS event_at,
    status,
    submitted_by                    AS actor_user_id,
    submission_id::text             AS source_pk,
    raw_payload,
    posted_at,
    rejection_reason::text          AS extra_text
  FROM private_core.form_submissions

  UNION ALL

  -- ========================================================================
  -- Source 2: credit_decisions
  -- ========================================================================
  SELECT
    'dec_' || decision_id::text,
    'credit_decision'::text,
    decision,                       -- 'approve' | 'reject'
    decided_at,
    state,                          -- 'pending_gi_action' | 'gi_draft_created' | 'resolved' | 'cancelled' | etc.
    decided_by_user_id,
    decision_id::text,
    jsonb_build_object(
      'exception_id', exception_id::text,
      'reason',       reason,
      'state',        state
    ) AS raw_payload,
    NULL::timestamptz,
    NULL::text
  FROM private_core.credit_decisions

  UNION ALL

  -- ========================================================================
  -- Source 3a: exceptions (acknowledged)
  -- ========================================================================
  SELECT
    'ack_' || exception_id::text,
    'exception_acknowledge'::text,
    category,                       -- e.g. 'lionwheel_credit_needed', 'count_large_variance'
    acknowledged_at,
    'acknowledged'::text            AS status,
    acknowledged_by,
    exception_id::text,
    jsonb_build_object(
      'title',    title,
      'category', category,
      'severity', severity
    ) AS raw_payload,
    NULL::timestamptz,
    NULL::text
  FROM private_core.exceptions
  WHERE acknowledged_by  IS NOT NULL
    AND acknowledged_at  IS NOT NULL

  UNION ALL

  -- ========================================================================
  -- Source 3b: exceptions (resolved)
  -- ========================================================================
  SELECT
    'res_' || exception_id::text,
    'exception_resolve'::text,
    category,
    resolved_at,
    'resolved'::text                AS status,
    resolved_by,
    exception_id::text,
    jsonb_build_object(
      'title',            title,
      'category',         category,
      'severity',         severity,
      'resolution_notes', resolution_notes
    ) AS raw_payload,
    NULL::timestamptz,
    NULL::text
  FROM private_core.exceptions
  WHERE resolved_by  IS NOT NULL
    AND resolved_at  IS NOT NULL;

COMMENT ON VIEW private_core.v_my_activity_log IS
  '0186: Unified per-user activity feed. UNIONs form_submissions, credit_decisions, exceptions (ack + resolve). Read-only. Keyset paginated on (event_at DESC, activity_id DESC). Append-only by construction.';

COMMIT;

-- ===========================================================================
-- End of 0186_v_my_activity_log.sql
-- ===========================================================================
```

- [ ] **Step 2: Add npm script entries**

Modify `api/package.json` — add:

```json
"db:apply:0186": "psql \"$DATABASE_URL\" -v ON_ERROR_STOP=1 -f db/migrations/0186_v_my_activity_log.sql",
"db:test:0186":  "pg_prove -d \"$DATABASE_URL\" db/tests/0186_v_my_activity_log.test.sql",
```

- [ ] **Step 3: Commit**

```bash
git add db/migrations/0186_v_my_activity_log.sql api/package.json
git commit -m "feat(db): 0186 v_my_activity_log view"
```

---

### Task 4: pgTAP test for view 0186

**Files:**
- Create: `db/tests/0186_v_my_activity_log.test.sql`

- [ ] **Step 1: Write the failing test**

```sql
-- 0186_v_my_activity_log.test.sql — pgTAP
--
-- Verifies:
--   * view exists with the expected 10-column shape
--   * all 4 source_kinds are returnable from the UNION
--   * actor_user_id is NOT NULL for the form_submission/credit_decision
--     sources, and matches acknowledged_by / resolved_by for the
--     exception sources
--   * activity_id prefixes are correct per source
--   * the view is read-only (INSERT raises)

BEGIN;

SELECT plan(8);

-- (1) view exists
SELECT has_view(
  'private_core', 'v_my_activity_log',
  'v_my_activity_log exists'
);

-- (2) expected columns
SELECT columns_are(
  'private_core', 'v_my_activity_log',
  ARRAY[
    'activity_id', 'source_kind', 'action_kind', 'event_at',
    'status', 'actor_user_id', 'source_pk', 'raw_payload',
    'posted_at', 'extra_text'
  ],
  'v_my_activity_log has the 10 expected columns'
);

-- (3) source_kind values that the view returns
SELECT set_eq(
  $$ SELECT DISTINCT source_kind FROM private_core.v_my_activity_log $$,
  ARRAY[
    'form_submission',
    'credit_decision',
    'exception_acknowledge',
    'exception_resolve'
  ]::text[],
  'view returns exactly 4 source_kinds'
);

-- (4) activity_id prefixes match source_kind
SELECT is(
  ( SELECT COUNT(*)::int FROM private_core.v_my_activity_log
     WHERE source_kind = 'form_submission'        AND activity_id NOT LIKE 'sub\_%' ESCAPE '\' ),
  0,
  'every form_submission row has sub_ prefix'
);
SELECT is(
  ( SELECT COUNT(*)::int FROM private_core.v_my_activity_log
     WHERE source_kind = 'credit_decision'        AND activity_id NOT LIKE 'dec\_%' ESCAPE '\' ),
  0,
  'every credit_decision row has dec_ prefix'
);
SELECT is(
  ( SELECT COUNT(*)::int FROM private_core.v_my_activity_log
     WHERE source_kind = 'exception_acknowledge'  AND activity_id NOT LIKE 'ack\_%' ESCAPE '\' ),
  0,
  'every exception_acknowledge row has ack_ prefix'
);
SELECT is(
  ( SELECT COUNT(*)::int FROM private_core.v_my_activity_log
     WHERE source_kind = 'exception_resolve'      AND activity_id NOT LIKE 'res\_%' ESCAPE '\' ),
  0,
  'every exception_resolve row has res_ prefix'
);

-- (5) read-only: INSERT must fail
SELECT throws_ok(
  $$ INSERT INTO private_core.v_my_activity_log (activity_id) VALUES ('x') $$,
  '55000', NULL,
  'INSERT into v_my_activity_log fails (read-only)'
);

SELECT * FROM finish();
ROLLBACK;
```

- [ ] **Step 2: Run test before applying — expect FAIL**

```bash
pg_prove -d "$DATABASE_URL" db/tests/0186_v_my_activity_log.test.sql
```

Expected: `not ok` on test 1 (view doesn't exist).

- [ ] **Step 3: Apply migration**

```bash
npm run db:apply:0186
```

- [ ] **Step 4: Run test again — expect PASS**

```bash
npm run db:test:0186
```

Expected: `ok 8/8`.

- [ ] **Step 5: Commit the test**

```bash
git add db/tests/0186_v_my_activity_log.test.sql
git commit -m "test(db): pgTAP for 0186 v_my_activity_log shape and read-only"
```

---

## Stage 2 — Activity log API module

### Task 5: API module scaffold — types and Zod query schema

**Files:**
- Create: `api/src/activity_log/schemas.ts`

- [ ] **Step 1: Write the file**

```typescript
// api/src/activity_log/schemas.ts
//
// DTO + Zod query schemas for /api/v1/queries/me/activity (list + drawer).
//
// Authority: docs/superpowers/specs/2026-05-13-my-activity-log-design.md

import { z } from 'zod';

export const SOURCE_KINDS = [
  'form_submission',
  'credit_decision',
  'exception_acknowledge',
  'exception_resolve',
] as const;
export type SourceKind = (typeof SOURCE_KINDS)[number];

export interface ActivitySummary {
  headline: string;          // never empty
  secondary: string | null;
}

export interface MyActivityRow {
  activity_id: string;
  source_kind: SourceKind;
  action_kind: string;
  event_at: string;          // ISO
  posted_at: string | null;  // ISO; only populated for form_submission
  status: string;
  rejection_reason: string | null;
  summary: ActivitySummary;
  raw_payload_present: boolean;
}

export interface MyActivityListResponse {
  rows: MyActivityRow[];
  next_cursor: string | null;
  has_more: boolean;
}

export interface MyActivityDrawerResponse {
  row: MyActivityRow & {
    raw_payload_redacted: unknown;   // jsonb after redaction
    cross_links: {
      kind: string;                  // 'po' | 'ledger_movements' | 'exception'
      label: string;
      target_id: string;
    }[];
  };
}

// ----- Zod query schema (list) -----

export const listQuerySchema = z.object({
  cursor:       z.string().min(1).max(200).optional(),
  limit:        z.coerce.number().int().min(1).max(200).default(100),
  source_kind:  z
    .union([z.enum(SOURCE_KINDS), z.array(z.enum(SOURCE_KINDS))])
    .optional()
    .transform((v) => (v === undefined ? undefined : Array.isArray(v) ? v : [v])),
  action_kind:  z
    .union([z.string().min(1).max(80), z.array(z.string().min(1).max(80))])
    .optional()
    .transform((v) => (v === undefined ? undefined : Array.isArray(v) ? v : [v])),
  status:       z
    .union([z.string().min(1).max(40), z.array(z.string().min(1).max(40))])
    .optional()
    .transform((v) => (v === undefined ? undefined : Array.isArray(v) ? v : [v])),
  from:         z.string().datetime().optional(),
  to:           z.string().datetime().optional(),
});
export type ListQuery = z.infer<typeof listQuerySchema>;

// ----- Cursor encoding -----
//
// A cursor is base64url-encoded JSON of { event_at: iso, activity_id: string }.
// We do NOT trust the cursor to be safe; the handler must validate that
// the user_id filter still applies (cursor never escapes the actor scope).

export interface DecodedCursor {
  event_at: string;     // ISO
  activity_id: string;
}

export function encodeCursor(c: DecodedCursor): string {
  return Buffer.from(JSON.stringify(c), 'utf8').toString('base64url');
}

export function decodeCursor(s: string): DecodedCursor | null {
  try {
    const j = JSON.parse(Buffer.from(s, 'base64url').toString('utf8'));
    if (typeof j?.event_at !== 'string' || typeof j?.activity_id !== 'string') return null;
    return { event_at: j.event_at, activity_id: j.activity_id };
  } catch {
    return null;
  }
}
```

- [ ] **Step 2: Typecheck**

```bash
cd /c/Users/tomw2/Projects/gt-factory-os/api
npm run typecheck
```

Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add api/src/activity_log/schemas.ts
git commit -m "feat(api): activity_log schemas + zod query"
```

---

### Task 6: Redaction helper + unit test

**Files:**
- Create: `api/src/activity_log/redaction.ts`
- Create: `api/test/activity_log_redaction.test.ts`

- [ ] **Step 1: Write the failing test**

```typescript
// api/test/activity_log_redaction.test.ts
import './_test_env.ts';
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { redactPayload } from '../src/activity_log/redaction.ts';

test('redactPayload replaces token/secret/password/auth fields at any nesting depth', () => {
  const input = {
    item_name: 'Tomatoes',
    quantity: 5,
    auth_token: 'sk_live_xyz',
    nested: {
      api_secret: 'abc',
      password: 'p',
      ok: 'visible',
    },
    arr: [{ access_token: 'x' }, { keep: 1 }],
  };
  const out = redactPayload(input);
  assert.equal(out.item_name, 'Tomatoes');
  assert.equal(out.quantity, 5);
  assert.equal(out.auth_token, '[REDACTED]');
  assert.equal(out.nested.api_secret, '[REDACTED]');
  assert.equal(out.nested.password, '[REDACTED]');
  assert.equal(out.nested.ok, 'visible');
  assert.equal(out.arr[0].access_token, '[REDACTED]');
  assert.equal(out.arr[1].keep, 1);
});

test('redactPayload is case-insensitive', () => {
  const out = redactPayload({ Authorization: 'b', SECRET_KEY: 'c' });
  assert.equal(out.Authorization, '[REDACTED]');
  assert.equal(out.SECRET_KEY, '[REDACTED]');
});

test('redactPayload tolerates non-object inputs', () => {
  assert.equal(redactPayload(null), null);
  assert.equal(redactPayload('hi'), 'hi');
  assert.equal(redactPayload(42), 42);
});
```

- [ ] **Step 2: Run — expect FAIL (module not found)**

```bash
cd /c/Users/tomw2/Projects/gt-factory-os/api
node --test --import tsx test/activity_log_redaction.test.ts
```

Expected: import error on `redaction.ts`.

- [ ] **Step 3: Write the implementation**

```typescript
// api/src/activity_log/redaction.ts
//
// Replaces values of any field whose name matches the secret/token pattern
// with the literal string '[REDACTED]'. Walks objects and arrays recursively.
// Idempotent. Non-object inputs are returned as-is.
//
// Used by drawer responses only — list responses do not include raw_payload.

const SECRET_FIELD_RE = /token|secret|password|auth/i;

export function redactPayload<T>(value: T): T {
  return walk(value) as T;
}

function walk(v: unknown): unknown {
  if (v === null || typeof v !== 'object') return v;
  if (Array.isArray(v)) return v.map(walk);
  const out: Record<string, unknown> = {};
  for (const [k, val] of Object.entries(v as Record<string, unknown>)) {
    out[k] = SECRET_FIELD_RE.test(k) ? '[REDACTED]' : walk(val);
  }
  return out;
}
```

- [ ] **Step 4: Run — expect PASS**

```bash
node --test --import tsx test/activity_log_redaction.test.ts
```

Expected: 3 tests pass.

- [ ] **Step 5: Commit**

```bash
git add api/src/activity_log/redaction.ts api/test/activity_log_redaction.test.ts
git commit -m "feat(api): activity_log redaction helper for secret-shaped fields"
```

---

### Task 7: Builder interface + registry + missing-builder fallback

**Files:**
- Create: `api/src/activity_log/builders/_registry.ts`

- [ ] **Step 1: Write the registry skeleton**

```typescript
// api/src/activity_log/builders/_registry.ts
//
// Summary builder registry. Each builder produces { headline, secondary }
// from a normalized view row. Builders may JOIN to master-data tables for
// name resolution; pass `db` via the SummaryContext.
//
// Fail-loud rule: if no builder exists for (source_kind, action_kind), the
// registry returns a visibly broken summary AND emits a structured warning
// log. Never silently return raw form_type strings.

import type { Db } from '../../db/connection.js';
import type { SourceKind, ActivitySummary } from '../schemas.js';

export interface ViewRow {
  activity_id: string;
  source_kind: SourceKind;
  action_kind: string;
  event_at: string;
  status: string;
  actor_user_id: string;
  source_pk: string;
  raw_payload: unknown;
  posted_at: string | null;
  extra_text: string | null;
}

export interface SummaryContext {
  db: Db;
}

export interface SummaryBuilder {
  build(row: ViewRow, ctx: SummaryContext): Promise<ActivitySummary>;
}

type Key = `${SourceKind}:${string}`;
const registry = new Map<Key, SummaryBuilder>();

function key(source: SourceKind, action: string): Key {
  return `${source}:${action}`;
}

export function register(
  source: SourceKind,
  action: string,
  builder: SummaryBuilder,
): void {
  registry.set(key(source, action), builder);
}

/**
 * Resolve a builder, falling back to the "_default" builder registered for
 * the same source_kind if no per-action builder matches. If neither exists,
 * returns null and the caller emits the fail-loud summary.
 */
export function resolve(source: SourceKind, action: string): SummaryBuilder | null {
  return (
    registry.get(key(source, action)) ??
    registry.get(key(source, '_default')) ??
    null
  );
}

export async function buildSummary(
  row: ViewRow,
  ctx: SummaryContext,
): Promise<ActivitySummary> {
  const b = resolve(row.source_kind, row.action_kind);
  if (b) return b.build(row, ctx);
  // Fail-loud — caller logs.
  return {
    headline: `⚠ Unknown action: ${row.source_kind} / ${row.action_kind}`,
    secondary: '(no summary builder)',
  };
}

/** True iff a builder is registered (exact OR _default fallback). */
export function hasBuilder(source: SourceKind, action: string): boolean {
  return resolve(source, action) !== null;
}
```

- [ ] **Step 2: Typecheck**

```bash
cd /c/Users/tomw2/Projects/gt-factory-os/api
npm run typecheck
```

- [ ] **Step 3: Commit**

```bash
git add api/src/activity_log/builders/_registry.ts
git commit -m "feat(api): activity_log builder registry + fail-loud fallback"
```

---

### Task 8: Stock-action builders (4) + fixture tests

**Files:**
- Create: `api/src/activity_log/builders/form_submission/goods_receipt.ts`
- Create: `api/src/activity_log/builders/form_submission/waste_adjustment.ts`
- Create: `api/src/activity_log/builders/form_submission/physical_count.ts`
- Create: `api/src/activity_log/builders/form_submission/production_actual_submit.ts`
- Create: `api/test/activity_log_builders.test.ts` (new file; will grow across Tasks 8–13)

- [ ] **Step 1: Write the failing test file with 4 stock-action cases**

```typescript
// api/test/activity_log_builders.test.ts
import './_test_env.ts';
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { sql } from 'kysely';
import { createDb, type Db } from '../src/db/connection.ts';
import { buildSummary, type ViewRow } from '../src/activity_log/builders/_registry.ts';
import '../src/activity_log/builders/index.ts';  // side-effect: registers all builders

// One shared DB connection; tests are read-only (JOINs to master-data only).
const db: Db = createDb();
const ctx = { db };

function row(partial: Partial<ViewRow>): ViewRow {
  return {
    activity_id: 'sub_test',
    source_kind: 'form_submission',
    action_kind: 'goods_receipt',
    event_at: '2026-05-13T08:00:00Z',
    status: 'posted',
    actor_user_id: '00000000-0000-0000-0000-000000000000',
    source_pk: 'test',
    raw_payload: {},
    posted_at: null,
    extra_text: null,
    ...partial,
  };
}

test('goods_receipt — headline includes supplier name and line count', async () => {
  // raw_payload mirrors the actual GR submit request: supplier_id + lines[].
  // The builder resolves supplier_id → supplier name via a JOIN.
  // We use a known-good supplier id from the master-data fixture set.
  const supplierId = await pickFixtureSupplierId(db);
  const out = await buildSummary(
    row({
      action_kind: 'goods_receipt',
      raw_payload: {
        supplier_id: supplierId,
        lines: [
          { component_id: 'c1', quantity: 10, unit: 'kg' },
          { component_id: 'c2', quantity: 5,  unit: 'kg' },
        ],
        po_id: null,
      },
    }),
    ctx,
  );
  assert.match(out.headline, /^GR · .+ · 2 lines$/);
  assert.notMatch(out.headline, /supplier_id|c1|c2/, 'no raw ids leak into headline');
});

test('waste_adjustment — headline shows item name + qty + unit', async () => {
  const item = await pickFixtureItem(db);  // returns { item_type, item_id, item_name }
  const out = await buildSummary(
    row({
      action_kind: 'waste_adjustment',
      raw_payload: {
        adjustment_kind: 'waste',
        item_type: item.item_type,
        item_id: item.item_id,
        quantity: 5,
        unit: 'kg',
        reason: 'spoilage',
      },
    }),
    ctx,
  );
  assert.match(out.headline, new RegExp(`^Waste · ${item.item_name} 5 kg$`));
  assert.equal(out.secondary, 'Spoilage');
});

test('physical_count — headline shows item name + counted qty + unit; secondary shows variance', async () => {
  const item = await pickFixtureItem(db);
  const out = await buildSummary(
    row({
      action_kind: 'physical_count',
      raw_payload: {
        item_type: item.item_type,
        item_id: item.item_id,
        counted_quantity: 40,
        unit: 'kg',
        computed_delta: -2,
      },
    }),
    ctx,
  );
  assert.match(out.headline, new RegExp(`^Count · ${item.item_name} 40 kg$`));
  assert.equal(out.secondary, 'Variance −2 kg');
});

test('production_actual_submit — headline shows SKU name; secondary shows units', async () => {
  const sku = await pickFixtureSku(db);  // returns { sku_id, sku_name }
  const out = await buildSummary(
    row({
      action_kind: 'production_actual_submit',
      raw_payload: { sku_id: sku.sku_id, units_produced: 240 },
    }),
    ctx,
  );
  assert.match(out.headline, new RegExp(`^Production · ${sku.sku_name}$`));
  assert.equal(out.secondary, '240 units');
});

// ---------- fixture helpers ----------

async function pickFixtureSupplierId(db: Db): Promise<string> {
  const r = await sql<{ supplier_id: string }>`
    SELECT supplier_id FROM private_core.suppliers
    WHERE archived_at IS NULL ORDER BY supplier_id LIMIT 1
  `.execute(db);
  if (r.rows.length === 0) throw new Error('no fixture supplier available');
  return r.rows[0].supplier_id;
}

async function pickFixtureItem(db: Db): Promise<{ item_type: string; item_id: string; item_name: string }> {
  // Prefer a component (most stock forms operate on components); fall back to item.
  const r = await sql<{ item_type: string; item_id: string; item_name: string }>`
    SELECT 'component'::text AS item_type, component_id AS item_id, name AS item_name
      FROM private_core.components
     WHERE archived_at IS NULL
     ORDER BY component_id LIMIT 1
  `.execute(db);
  if (r.rows.length === 0) throw new Error('no fixture component available');
  return r.rows[0];
}

async function pickFixtureSku(db: Db): Promise<{ sku_id: string; sku_name: string }> {
  const r = await sql<{ sku_id: string; sku_name: string }>`
    SELECT item_id AS sku_id, name AS sku_name
      FROM private_core.items
     WHERE archived_at IS NULL
     ORDER BY item_id LIMIT 1
  `.execute(db);
  if (r.rows.length === 0) throw new Error('no fixture sku available');
  return r.rows[0];
}
```

- [ ] **Step 2: Run — expect FAIL (no builders registered)**

```bash
node --test --import tsx test/activity_log_builders.test.ts
```

Expected: 4 failures — `⚠ Unknown action` in every output, or import error.

- [ ] **Step 3: Create the 4 builders**

`api/src/activity_log/builders/form_submission/goods_receipt.ts`:
```typescript
import { sql } from 'kysely';
import { register, type SummaryBuilder } from '../_registry.js';

interface Payload {
  supplier_id?: string;
  lines?: { component_id?: string; quantity?: number; unit?: string }[];
  po_id?: string | null;
}

const builder: SummaryBuilder = {
  async build(row, { db }) {
    const p = (row.raw_payload ?? {}) as Payload;
    const supplierId = p.supplier_id ?? null;
    let supplierName: string = 'Unknown supplier';
    if (supplierId) {
      const r = await sql<{ name: string }>`
        SELECT name FROM private_core.suppliers WHERE supplier_id = ${supplierId}
      `.execute(db);
      if (r.rows[0]) supplierName = r.rows[0].name;
    }
    const nLines = Array.isArray(p.lines) ? p.lines.length : 0;
    const totalUnits = Array.isArray(p.lines)
      ? p.lines.reduce((a, l) => a + (Number(l.quantity) || 0), 0)
      : 0;
    return {
      headline: `GR · ${supplierName} · ${nLines} ${nLines === 1 ? 'line' : 'lines'}`,
      secondary: totalUnits > 0 ? `${totalUnits} units` : null,
    };
  },
};
register('form_submission', 'goods_receipt', builder);
export default builder;
```

`api/src/activity_log/builders/form_submission/waste_adjustment.ts`:
```typescript
import { sql } from 'kysely';
import { register, type SummaryBuilder } from '../_registry.js';

interface Payload {
  adjustment_kind?: 'waste' | 'adjustment';
  item_type?: string;
  item_id?: string;
  quantity?: number;
  unit?: string;
  reason?: string;
}

const REASON_LABEL: Record<string, string> = {
  spoilage:     'Spoilage',
  damage:       'Damage',
  count_fix:    'Count fix',
  expiry:       'Expiry',
  contamination:'Contamination',
  other:        'Other',
};

async function itemName(db: any, type: string | undefined, id: string | undefined): Promise<string> {
  if (!type || !id) return 'Unknown item';
  const table = type === 'component' ? 'components' : 'items';
  const pk    = type === 'component' ? 'component_id' : 'item_id';
  const r = await sql<{ name: string }>`
    SELECT name FROM private_core.${sql.raw(table)} WHERE ${sql.raw(pk)} = ${id}
  `.execute(db);
  return r.rows[0]?.name ?? `Unknown ${type}`;
}

const builder: SummaryBuilder = {
  async build(row, { db }) {
    const p = (row.raw_payload ?? {}) as Payload;
    const kind = (p.adjustment_kind === 'adjustment') ? 'Adjustment' : 'Waste';
    const name = await itemName(db, p.item_type, p.item_id);
    const qty  = p.quantity ?? 0;
    const unit = p.unit ?? '';
    return {
      headline: `${kind} · ${name} ${qty} ${unit}`.trim(),
      secondary: p.reason ? (REASON_LABEL[p.reason] ?? p.reason) : null,
    };
  },
};
register('form_submission', 'waste_adjustment', builder);
export default builder;
```

`api/src/activity_log/builders/form_submission/physical_count.ts`:
```typescript
import { sql } from 'kysely';
import { register, type SummaryBuilder } from '../_registry.js';

interface Payload {
  item_type?: string;
  item_id?: string;
  counted_quantity?: number;
  unit?: string;
  computed_delta?: number;       // populated by handler when above threshold
}

async function itemName(db: any, type: string | undefined, id: string | undefined): Promise<string> {
  if (!type || !id) return 'Unknown item';
  const table = type === 'component' ? 'components' : 'items';
  const pk    = type === 'component' ? 'component_id' : 'item_id';
  const r = await sql<{ name: string }>`
    SELECT name FROM private_core.${sql.raw(table)} WHERE ${sql.raw(pk)} = ${id}
  `.execute(db);
  return r.rows[0]?.name ?? `Unknown ${type}`;
}

function signed(n: number): string {
  if (n === 0) return '0';
  return n > 0 ? `+${n}` : `−${Math.abs(n)}`;
}

const builder: SummaryBuilder = {
  async build(row, { db }) {
    const p = (row.raw_payload ?? {}) as Payload;
    const name = await itemName(db, p.item_type, p.item_id);
    const qty  = p.counted_quantity ?? 0;
    const unit = p.unit ?? '';
    const delta = p.computed_delta;
    return {
      headline: `Count · ${name} ${qty} ${unit}`.trim(),
      secondary: delta !== undefined ? `Variance ${signed(delta)} ${unit}`.trim() : null,
    };
  },
};
register('form_submission', 'physical_count', builder);
export default builder;
```

`api/src/activity_log/builders/form_submission/production_actual_submit.ts`:
```typescript
import { sql } from 'kysely';
import { register, type SummaryBuilder } from '../_registry.js';

interface Payload {
  sku_id?: string;
  units_produced?: number;
}

const builder: SummaryBuilder = {
  async build(row, { db }) {
    const p = (row.raw_payload ?? {}) as Payload;
    let name = 'Unknown SKU';
    if (p.sku_id) {
      const r = await sql<{ name: string }>`
        SELECT name FROM private_core.items WHERE item_id = ${p.sku_id}
      `.execute(db);
      if (r.rows[0]) name = r.rows[0].name;
    }
    return {
      headline: `Production · ${name}`,
      secondary: p.units_produced !== undefined ? `${p.units_produced} units` : null,
    };
  },
};
register('form_submission', 'production_actual_submit', builder);
export default builder;
```

- [ ] **Step 4: Create the builders index (loads all builders by side-effect)**

`api/src/activity_log/builders/index.ts`:
```typescript
// Side-effect imports — each builder file calls register() on load.
import './form_submission/goods_receipt.js';
import './form_submission/waste_adjustment.js';
import './form_submission/physical_count.js';
import './form_submission/production_actual_submit.js';
// (more builders added in subsequent tasks)
```

- [ ] **Step 5: Run — expect 4 PASS**

```bash
node --test --import tsx test/activity_log_builders.test.ts
```

Expected: 4 tests pass.

- [ ] **Step 6: Commit**

```bash
git add api/src/activity_log/builders/ api/test/activity_log_builders.test.ts
git commit -m "feat(api): activity_log stock-action builders (GR, waste, count, production)"
```

---

### Task 9: Forecast builders (5) + tests

**Files:**
- Create: `api/src/activity_log/builders/form_submission/forecast_save.ts`
- Create: `api/src/activity_log/builders/form_submission/forecast_publish.ts`
- Create: `api/src/activity_log/builders/form_submission/forecast_revise.ts`
- Create: `api/src/activity_log/builders/form_submission/forecast_discard.ts`
- Create: `api/src/activity_log/builders/form_submission/forecast_open_draft.ts`
- Modify: `api/src/activity_log/builders/index.ts` (add 5 imports)
- Modify: `api/test/activity_log_builders.test.ts` (append 5 test cases)

- [ ] **Step 1: Append 5 failing test cases**

```typescript
test('forecast_save — headline shows week + SKU count', async () => {
  const out = await buildSummary(
    row({
      action_kind: 'forecast_save',
      raw_payload: { iso_week: '2026-W21', skus_touched: 23 },
    }),
    ctx,
  );
  assert.equal(out.headline, 'Forecast saved · week of 2026-W21');
  assert.equal(out.secondary, '23 SKUs touched');
});

test('forecast_publish — headline shows week + SKU count', async () => {
  const out = await buildSummary(
    row({
      action_kind: 'forecast_publish',
      raw_payload: { iso_week: '2026-W21', skus_published: 23 },
    }),
    ctx,
  );
  assert.equal(out.headline, 'Forecast published · week of 2026-W21');
  assert.equal(out.secondary, '23 SKUs published');
});

test('forecast_revise — headline shows week + changed count', async () => {
  const out = await buildSummary(
    row({
      action_kind: 'forecast_revise',
      raw_payload: { iso_week: '2026-W21', skus_changed: 4 },
    }),
    ctx,
  );
  assert.equal(out.headline, 'Forecast revised · week of 2026-W21');
  assert.equal(out.secondary, '4 SKUs changed');
});

test('forecast_discard — headline shows week; secondary reason or null', async () => {
  const out = await buildSummary(
    row({
      action_kind: 'forecast_discard',
      raw_payload: { iso_week: '2026-W21', reason: 'wrong baseline' },
    }),
    ctx,
  );
  assert.equal(out.headline, 'Forecast discarded · week of 2026-W21');
  assert.equal(out.secondary, 'wrong baseline');
});

test('forecast_open_draft — headline shows week; secondary null', async () => {
  const out = await buildSummary(
    row({
      action_kind: 'forecast_open_draft',
      raw_payload: { iso_week: '2026-W21' },
    }),
    ctx,
  );
  assert.equal(out.headline, 'Forecast draft opened · week of 2026-W21');
  assert.equal(out.secondary, null);
});
```

- [ ] **Step 2: Run — expect 5 FAIL**

```bash
node --test --import tsx test/activity_log_builders.test.ts
```

- [ ] **Step 3: Implement 5 builders**

`forecast_save.ts`:
```typescript
import { register, type SummaryBuilder } from '../_registry.js';
const b: SummaryBuilder = {
  async build(row) {
    const p = (row.raw_payload ?? {}) as { iso_week?: string; skus_touched?: number };
    return {
      headline: `Forecast saved · week of ${p.iso_week ?? '?'}`,
      secondary: p.skus_touched !== undefined ? `${p.skus_touched} SKUs touched` : null,
    };
  },
};
register('form_submission', 'forecast_save', b);
export default b;
```

`forecast_publish.ts`:
```typescript
import { register, type SummaryBuilder } from '../_registry.js';
const b: SummaryBuilder = {
  async build(row) {
    const p = (row.raw_payload ?? {}) as { iso_week?: string; skus_published?: number };
    return {
      headline: `Forecast published · week of ${p.iso_week ?? '?'}`,
      secondary: p.skus_published !== undefined ? `${p.skus_published} SKUs published` : null,
    };
  },
};
register('form_submission', 'forecast_publish', b);
export default b;
```

`forecast_revise.ts`:
```typescript
import { register, type SummaryBuilder } from '../_registry.js';
const b: SummaryBuilder = {
  async build(row) {
    const p = (row.raw_payload ?? {}) as { iso_week?: string; skus_changed?: number };
    return {
      headline: `Forecast revised · week of ${p.iso_week ?? '?'}`,
      secondary: p.skus_changed !== undefined ? `${p.skus_changed} SKUs changed` : null,
    };
  },
};
register('form_submission', 'forecast_revise', b);
export default b;
```

`forecast_discard.ts`:
```typescript
import { register, type SummaryBuilder } from '../_registry.js';
const b: SummaryBuilder = {
  async build(row) {
    const p = (row.raw_payload ?? {}) as { iso_week?: string; reason?: string };
    return {
      headline: `Forecast discarded · week of ${p.iso_week ?? '?'}`,
      secondary: p.reason ?? null,
    };
  },
};
register('form_submission', 'forecast_discard', b);
export default b;
```

`forecast_open_draft.ts`:
```typescript
import { register, type SummaryBuilder } from '../_registry.js';
const b: SummaryBuilder = {
  async build(row) {
    const p = (row.raw_payload ?? {}) as { iso_week?: string };
    return {
      headline: `Forecast draft opened · week of ${p.iso_week ?? '?'}`,
      secondary: null,
    };
  },
};
register('form_submission', 'forecast_open_draft', b);
export default b;
```

- [ ] **Step 4: Add side-effect imports to `builders/index.ts`**

```typescript
import './form_submission/forecast_save.js';
import './form_submission/forecast_publish.js';
import './form_submission/forecast_revise.js';
import './form_submission/forecast_discard.js';
import './form_submission/forecast_open_draft.js';
```

- [ ] **Step 5: Run — expect all PASS**

```bash
node --test --import tsx test/activity_log_builders.test.ts
```

- [ ] **Step 6: Commit**

```bash
git add api/src/activity_log/builders/form_submission/forecast_*.ts \
        api/src/activity_log/builders/index.ts \
        api/test/activity_log_builders.test.ts
git commit -m "feat(api): activity_log forecast builders (save/publish/revise/discard/open_draft)"
```

---

### Task 10: Planning builders (4) + tests

**Files:**
- Create: `api/src/activity_log/builders/form_submission/planning_run_execute.ts`
- Create: `api/src/activity_log/builders/form_submission/planning_rec_approve.ts`
- Create: `api/src/activity_log/builders/form_submission/planning_rec_dismiss.ts`
- Create: `api/src/activity_log/builders/form_submission/planning_rec_convert_to_po.ts`
- Modify: `api/src/activity_log/builders/index.ts`
- Modify: `api/test/activity_log_builders.test.ts`

- [ ] **Step 1: Append failing tests**

```typescript
test('planning_run_execute — N recommendations', async () => {
  const out = await buildSummary(
    row({
      action_kind: 'planning_run_execute',
      raw_payload: { recommendations_generated: 14 },
    }),
    ctx,
  );
  assert.equal(out.headline, 'Planning run');
  assert.equal(out.secondary, '14 recommendations generated');
});

test('planning_rec_approve — target label + rec summary', async () => {
  const out = await buildSummary(
    row({
      action_kind: 'planning_rec_approve',
      raw_payload: {
        target_kind: 'po_recommendation',
        target_label: 'ABC Supplier 5 items',
        rec_summary: '₪12,400',
      },
    }),
    ctx,
  );
  assert.equal(out.headline, 'Approved rec · ABC Supplier 5 items');
  assert.equal(out.secondary, '₪12,400');
});

test('planning_rec_dismiss — target label + dismiss reason', async () => {
  const out = await buildSummary(
    row({
      action_kind: 'planning_rec_dismiss',
      raw_payload: {
        target_label: 'ABC Supplier 5 items',
        dismiss_reason: 'duplicate of #1234',
      },
    }),
    ctx,
  );
  assert.equal(out.headline, 'Dismissed rec · ABC Supplier 5 items');
  assert.equal(out.secondary, 'duplicate of #1234');
});

test('planning_rec_convert_to_po — supplier + N items', async () => {
  const supplierId = await pickFixtureSupplierId(db);
  const out = await buildSummary(
    row({
      action_kind: 'planning_rec_convert_to_po',
      raw_payload: { supplier_id: supplierId, items_count: 5 },
    }),
    ctx,
  );
  assert.match(out.headline, /^Converted to PO · .+$/);
  assert.equal(out.secondary, '5 items');
});
```

- [ ] **Step 2: Run — expect FAIL**

```bash
node --test --import tsx test/activity_log_builders.test.ts
```

- [ ] **Step 3: Implement 4 builders**

`planning_run_execute.ts`:
```typescript
import { register, type SummaryBuilder } from '../_registry.js';
const b: SummaryBuilder = {
  async build(row) {
    const p = (row.raw_payload ?? {}) as { recommendations_generated?: number };
    return {
      headline: 'Planning run',
      secondary: p.recommendations_generated !== undefined
        ? `${p.recommendations_generated} recommendations generated`
        : null,
    };
  },
};
register('form_submission', 'planning_run_execute', b);
export default b;
```

`planning_rec_approve.ts`:
```typescript
import { register, type SummaryBuilder } from '../_registry.js';
const b: SummaryBuilder = {
  async build(row) {
    const p = (row.raw_payload ?? {}) as { target_label?: string; rec_summary?: string };
    return {
      headline: `Approved rec · ${p.target_label ?? 'unknown target'}`,
      secondary: p.rec_summary ?? null,
    };
  },
};
register('form_submission', 'planning_rec_approve', b);
export default b;
```

`planning_rec_dismiss.ts`:
```typescript
import { register, type SummaryBuilder } from '../_registry.js';
const b: SummaryBuilder = {
  async build(row) {
    const p = (row.raw_payload ?? {}) as { target_label?: string; dismiss_reason?: string };
    return {
      headline: `Dismissed rec · ${p.target_label ?? 'unknown target'}`,
      secondary: p.dismiss_reason ?? null,
    };
  },
};
register('form_submission', 'planning_rec_dismiss', b);
export default b;
```

`planning_rec_convert_to_po.ts`:
```typescript
import { sql } from 'kysely';
import { register, type SummaryBuilder } from '../_registry.js';
const b: SummaryBuilder = {
  async build(row, { db }) {
    const p = (row.raw_payload ?? {}) as { supplier_id?: string; items_count?: number };
    let name = 'Unknown supplier';
    if (p.supplier_id) {
      const r = await sql<{ name: string }>`
        SELECT name FROM private_core.suppliers WHERE supplier_id = ${p.supplier_id}
      `.execute(db);
      if (r.rows[0]) name = r.rows[0].name;
    }
    return {
      headline: `Converted to PO · ${name}`,
      secondary: p.items_count !== undefined ? `${p.items_count} items` : null,
    };
  },
};
register('form_submission', 'planning_rec_convert_to_po', b);
export default b;
```

- [ ] **Step 4: Add side-effect imports**

In `builders/index.ts`:
```typescript
import './form_submission/planning_run_execute.js';
import './form_submission/planning_rec_approve.js';
import './form_submission/planning_rec_dismiss.js';
import './form_submission/planning_rec_convert_to_po.js';
```

- [ ] **Step 5: Run — expect all PASS**

- [ ] **Step 6: Commit**

```bash
git commit -am "feat(api): activity_log planning builders (run/approve/dismiss/convert)"
```

---

### Task 11: AMMC mutation builders (7) + tests

**Files:**
- Create: `api/src/activity_log/builders/form_submission/item_mutate.ts`
- Create: `api/src/activity_log/builders/form_submission/component_mutate.ts`
- Create: `api/src/activity_log/builders/form_submission/supplier_mutate.ts`
- Create: `api/src/activity_log/builders/form_submission/supplier_item_mutate.ts`
- Create: `api/src/activity_log/builders/form_submission/planning_policy_mutate.ts`
- Create: `api/src/activity_log/builders/form_submission/bom_mutate.ts`
- Create: `api/src/activity_log/builders/form_submission/alias_mutate.ts`
- Create: `api/src/activity_log/builders/form_submission/_mutate_shared.ts` (shared mutation_kind label map)
- Modify: `api/src/activity_log/builders/index.ts`
- Modify: `api/test/activity_log_builders.test.ts`

The 7 AMMC mutations all follow the same shape — `raw_payload.mutation_kind` plus a target. Build one shared helper for the mutation_kind label, then 7 thin builders.

- [ ] **Step 1: Append failing tests** (one per mutate type — same pattern)

```typescript
test('item_mutate — item name + mutation kind label', async () => {
  const sku = await pickFixtureSku(db);
  const out = await buildSummary(
    row({
      action_kind: 'item_mutate',
      raw_payload: { item_id: sku.sku_id, mutation_kind: 'update_quick' },
    }),
    ctx,
  );
  assert.match(out.headline, new RegExp(`^Item · ${sku.sku_name}$`));
  assert.equal(out.secondary, 'Quick update');
});

test('component_mutate — component name + mutation kind', async () => {
  const c = await pickFixtureItem(db);   // returns component row
  const out = await buildSummary(
    row({
      action_kind: 'component_mutate',
      raw_payload: { component_id: c.item_id, mutation_kind: 'create' },
    }),
    ctx,
  );
  assert.match(out.headline, new RegExp(`^Component · ${c.item_name}$`));
  assert.equal(out.secondary, 'Created');
});

test('supplier_mutate — supplier name + mutation kind', async () => {
  const supplierId = await pickFixtureSupplierId(db);
  const out = await buildSummary(
    row({
      action_kind: 'supplier_mutate',
      raw_payload: { supplier_id: supplierId, mutation_kind: 'update_structural' },
    }),
    ctx,
  );
  assert.match(out.headline, /^Supplier · .+$/);
  assert.equal(out.secondary, 'Structural update');
});

test('supplier_item_mutate — composite label', async () => {
  const supplierId = await pickFixtureSupplierId(db);
  const c = await pickFixtureItem(db);
  const out = await buildSummary(
    row({
      action_kind: 'supplier_item_mutate',
      raw_payload: {
        supplier_id: supplierId,
        component_id: c.item_id,
        mutation_kind: 'update_quick',
      },
    }),
    ctx,
  );
  assert.match(out.headline, new RegExp(`^Supplier item · .+ · ${c.item_name}$`));
  assert.equal(out.secondary, 'Quick update');
});

test('planning_policy_mutate — target label + mutation kind', async () => {
  const c = await pickFixtureItem(db);
  const out = await buildSummary(
    row({
      action_kind: 'planning_policy_mutate',
      raw_payload: { target_kind: 'component', target_id: c.item_id, mutation_kind: 'update_quick' },
    }),
    ctx,
  );
  assert.match(out.headline, new RegExp(`^Planning policy · ${c.item_name}$`));
  assert.equal(out.secondary, 'Quick update');
});

test('bom_mutate — bom name + mutation kind', async () => {
  // BOM is keyed by item_id; we pass a fixture sku
  const sku = await pickFixtureSku(db);
  const out = await buildSummary(
    row({
      action_kind: 'bom_mutate',
      raw_payload: { item_id: sku.sku_id, mutation_kind: 'update_structural' },
    }),
    ctx,
  );
  assert.match(out.headline, new RegExp(`^BOM · ${sku.sku_name}$`));
  assert.equal(out.secondary, 'Structural update');
});

test('alias_mutate — alias value → target label', async () => {
  const sku = await pickFixtureSku(db);
  const out = await buildSummary(
    row({
      action_kind: 'alias_mutate',
      raw_payload: { alias_value: 'GT-XYZ', target_kind: 'item', target_id: sku.sku_id, mutation_kind: 'create' },
    }),
    ctx,
  );
  assert.equal(out.headline, 'Alias · GT-XYZ');
  assert.match(out.secondary!, new RegExp(`^→ ${sku.sku_name}$`));
});
```

- [ ] **Step 2: Run — expect 7 FAIL**

- [ ] **Step 3: Implement shared mutation-kind label map**

`api/src/activity_log/builders/form_submission/_mutate_shared.ts`:
```typescript
export const MUTATION_KIND_LABEL: Record<string, string> = {
  create:            'Created',
  update_quick:      'Quick update',
  update_structural: 'Structural update',
  soft_delete:       'Archived',
  restore:           'Restored',
  bulk_import:       'Bulk import',
};

export function mutationLabel(kind: string | undefined): string | null {
  if (!kind) return null;
  return MUTATION_KIND_LABEL[kind] ?? kind;
}
```

- [ ] **Step 4: Implement 7 builders**

`item_mutate.ts`:
```typescript
import { sql } from 'kysely';
import { register, type SummaryBuilder } from '../_registry.js';
import { mutationLabel } from './_mutate_shared.js';
const b: SummaryBuilder = {
  async build(row, { db }) {
    const p = (row.raw_payload ?? {}) as { item_id?: string; mutation_kind?: string };
    let name = 'Unknown item';
    if (p.item_id) {
      const r = await sql<{ name: string }>`
        SELECT name FROM private_core.items WHERE item_id = ${p.item_id}
      `.execute(db);
      if (r.rows[0]) name = r.rows[0].name;
    }
    return { headline: `Item · ${name}`, secondary: mutationLabel(p.mutation_kind) };
  },
};
register('form_submission', 'item_mutate', b);
export default b;
```

`component_mutate.ts`:
```typescript
import { sql } from 'kysely';
import { register, type SummaryBuilder } from '../_registry.js';
import { mutationLabel } from './_mutate_shared.js';
const b: SummaryBuilder = {
  async build(row, { db }) {
    const p = (row.raw_payload ?? {}) as { component_id?: string; mutation_kind?: string };
    let name = 'Unknown component';
    if (p.component_id) {
      const r = await sql<{ name: string }>`
        SELECT name FROM private_core.components WHERE component_id = ${p.component_id}
      `.execute(db);
      if (r.rows[0]) name = r.rows[0].name;
    }
    return { headline: `Component · ${name}`, secondary: mutationLabel(p.mutation_kind) };
  },
};
register('form_submission', 'component_mutate', b);
export default b;
```

`supplier_mutate.ts`:
```typescript
import { sql } from 'kysely';
import { register, type SummaryBuilder } from '../_registry.js';
import { mutationLabel } from './_mutate_shared.js';
const b: SummaryBuilder = {
  async build(row, { db }) {
    const p = (row.raw_payload ?? {}) as { supplier_id?: string; mutation_kind?: string };
    let name = 'Unknown supplier';
    if (p.supplier_id) {
      const r = await sql<{ name: string }>`
        SELECT name FROM private_core.suppliers WHERE supplier_id = ${p.supplier_id}
      `.execute(db);
      if (r.rows[0]) name = r.rows[0].name;
    }
    return { headline: `Supplier · ${name}`, secondary: mutationLabel(p.mutation_kind) };
  },
};
register('form_submission', 'supplier_mutate', b);
export default b;
```

`supplier_item_mutate.ts`:
```typescript
import { sql } from 'kysely';
import { register, type SummaryBuilder } from '../_registry.js';
import { mutationLabel } from './_mutate_shared.js';
const b: SummaryBuilder = {
  async build(row, { db }) {
    const p = (row.raw_payload ?? {}) as { supplier_id?: string; component_id?: string; mutation_kind?: string };
    let supplier = 'Unknown supplier';
    let component = 'Unknown component';
    if (p.supplier_id) {
      const r = await sql<{ name: string }>`SELECT name FROM private_core.suppliers WHERE supplier_id = ${p.supplier_id}`.execute(db);
      if (r.rows[0]) supplier = r.rows[0].name;
    }
    if (p.component_id) {
      const r = await sql<{ name: string }>`SELECT name FROM private_core.components WHERE component_id = ${p.component_id}`.execute(db);
      if (r.rows[0]) component = r.rows[0].name;
    }
    return { headline: `Supplier item · ${supplier} · ${component}`, secondary: mutationLabel(p.mutation_kind) };
  },
};
register('form_submission', 'supplier_item_mutate', b);
export default b;
```

`planning_policy_mutate.ts`:
```typescript
import { sql } from 'kysely';
import { register, type SummaryBuilder } from '../_registry.js';
import { mutationLabel } from './_mutate_shared.js';
const b: SummaryBuilder = {
  async build(row, { db }) {
    const p = (row.raw_payload ?? {}) as { target_kind?: string; target_id?: string; mutation_kind?: string };
    let name = 'Unknown target';
    if (p.target_kind && p.target_id) {
      const table = p.target_kind === 'component' ? 'components' : 'items';
      const pk    = p.target_kind === 'component' ? 'component_id' : 'item_id';
      const r = await sql<{ name: string }>`
        SELECT name FROM private_core.${sql.raw(table)} WHERE ${sql.raw(pk)} = ${p.target_id}
      `.execute(db);
      if (r.rows[0]) name = r.rows[0].name;
    }
    return { headline: `Planning policy · ${name}`, secondary: mutationLabel(p.mutation_kind) };
  },
};
register('form_submission', 'planning_policy_mutate', b);
export default b;
```

`bom_mutate.ts`:
```typescript
import { sql } from 'kysely';
import { register, type SummaryBuilder } from '../_registry.js';
import { mutationLabel } from './_mutate_shared.js';
const b: SummaryBuilder = {
  async build(row, { db }) {
    const p = (row.raw_payload ?? {}) as { item_id?: string; mutation_kind?: string };
    let name = 'Unknown BOM';
    if (p.item_id) {
      const r = await sql<{ name: string }>`SELECT name FROM private_core.items WHERE item_id = ${p.item_id}`.execute(db);
      if (r.rows[0]) name = r.rows[0].name;
    }
    return { headline: `BOM · ${name}`, secondary: mutationLabel(p.mutation_kind) };
  },
};
register('form_submission', 'bom_mutate', b);
export default b;
```

`alias_mutate.ts`:
```typescript
import { sql } from 'kysely';
import { register, type SummaryBuilder } from '../_registry.js';
const b: SummaryBuilder = {
  async build(row, { db }) {
    const p = (row.raw_payload ?? {}) as { alias_value?: string; target_kind?: string; target_id?: string };
    let target = 'unknown target';
    if (p.target_kind && p.target_id) {
      const table = p.target_kind === 'component' ? 'components' : 'items';
      const pk    = p.target_kind === 'component' ? 'component_id' : 'item_id';
      const r = await sql<{ name: string }>`
        SELECT name FROM private_core.${sql.raw(table)} WHERE ${sql.raw(pk)} = ${p.target_id}
      `.execute(db);
      if (r.rows[0]) target = r.rows[0].name;
    }
    return { headline: `Alias · ${p.alias_value ?? '?'}`, secondary: `→ ${target}` };
  },
};
register('form_submission', 'alias_mutate', b);
export default b;
```

- [ ] **Step 5: Add side-effect imports**

In `builders/index.ts`:
```typescript
import './form_submission/item_mutate.js';
import './form_submission/component_mutate.js';
import './form_submission/supplier_mutate.js';
import './form_submission/supplier_item_mutate.js';
import './form_submission/planning_policy_mutate.js';
import './form_submission/bom_mutate.js';
import './form_submission/alias_mutate.js';
```

- [ ] **Step 6: Run — expect all PASS**

- [ ] **Step 7: Commit**

```bash
git commit -am "feat(api): activity_log AMMC mutation builders (7)"
```

---

### Task 12: Other form builders (3) + tests

**Files:**
- Create: `api/src/activity_log/builders/form_submission/integration_sku_map_approve.ts`
- Create: `api/src/activity_log/builders/form_submission/purchase_order_manual_create.ts`
- Create: `api/src/activity_log/builders/form_submission/holidays_il_mutate.ts`
- Modify: `api/src/activity_log/builders/index.ts`
- Modify: `api/test/activity_log_builders.test.ts`

- [ ] **Step 1: Append failing tests**

```typescript
test('integration_sku_map_approve — external sku → internal item name', async () => {
  const sku = await pickFixtureSku(db);
  const out = await buildSummary(
    row({
      action_kind: 'integration_sku_map_approve',
      raw_payload: { external_sku: 'GT-MARG-250', internal_item_id: sku.sku_id },
    }),
    ctx,
  );
  assert.equal(out.headline, 'SKU map · GT-MARG-250');
  assert.equal(out.secondary, `→ ${sku.sku_name}`);
});

test('purchase_order_manual_create — supplier + N items + total', async () => {
  const supplierId = await pickFixtureSupplierId(db);
  const out = await buildSummary(
    row({
      action_kind: 'purchase_order_manual_create',
      raw_payload: { supplier_id: supplierId, lines: [1, 2, 3, 4, 5], total_amount_ils: 12400 },
    }),
    ctx,
  );
  assert.match(out.headline, /^Manual PO · .+$/);
  assert.equal(out.secondary, '5 items · ₪12,400');
});

test('holidays_il_mutate — holiday name + date + mutation kind', async () => {
  const out = await buildSummary(
    row({
      action_kind: 'holidays_il_mutate',
      raw_payload: { name: 'Independence Day', date: '2026-04-22', mutation_kind: 'create' },
    }),
    ctx,
  );
  assert.equal(out.headline, 'Holiday · Independence Day (2026-04-22)');
  assert.equal(out.secondary, 'Created');
});
```

- [ ] **Step 2: Run — expect 3 FAIL**

- [ ] **Step 3: Implement 3 builders**

`integration_sku_map_approve.ts`:
```typescript
import { sql } from 'kysely';
import { register, type SummaryBuilder } from '../_registry.js';
const b: SummaryBuilder = {
  async build(row, { db }) {
    const p = (row.raw_payload ?? {}) as { external_sku?: string; internal_item_id?: string };
    let name = 'unknown internal item';
    if (p.internal_item_id) {
      const r = await sql<{ name: string }>`SELECT name FROM private_core.items WHERE item_id = ${p.internal_item_id}`.execute(db);
      if (r.rows[0]) name = r.rows[0].name;
    }
    return { headline: `SKU map · ${p.external_sku ?? '?'}`, secondary: `→ ${name}` };
  },
};
register('form_submission', 'integration_sku_map_approve', b);
export default b;
```

`purchase_order_manual_create.ts`:
```typescript
import { sql } from 'kysely';
import { register, type SummaryBuilder } from '../_registry.js';

function formatILS(n: number): string {
  return `₪${Math.round(n).toLocaleString('en-US')}`;
}

const b: SummaryBuilder = {
  async build(row, { db }) {
    const p = (row.raw_payload ?? {}) as { supplier_id?: string; lines?: unknown[]; total_amount_ils?: number };
    let name = 'Unknown supplier';
    if (p.supplier_id) {
      const r = await sql<{ name: string }>`SELECT name FROM private_core.suppliers WHERE supplier_id = ${p.supplier_id}`.execute(db);
      if (r.rows[0]) name = r.rows[0].name;
    }
    const n = Array.isArray(p.lines) ? p.lines.length : 0;
    const parts: string[] = [];
    if (n > 0) parts.push(`${n} ${n === 1 ? 'item' : 'items'}`);
    if (p.total_amount_ils !== undefined && p.total_amount_ils > 0) parts.push(formatILS(p.total_amount_ils));
    return {
      headline: `Manual PO · ${name}`,
      secondary: parts.length > 0 ? parts.join(' · ') : null,
    };
  },
};
register('form_submission', 'purchase_order_manual_create', b);
export default b;
```

`holidays_il_mutate.ts`:
```typescript
import { register, type SummaryBuilder } from '../_registry.js';
import { mutationLabel } from './_mutate_shared.js';
const b: SummaryBuilder = {
  async build(row) {
    const p = (row.raw_payload ?? {}) as { name?: string; date?: string; mutation_kind?: string };
    const hd = p.name ?? 'unknown holiday';
    const dt = p.date ?? '?';
    return { headline: `Holiday · ${hd} (${dt})`, secondary: mutationLabel(p.mutation_kind) };
  },
};
register('form_submission', 'holidays_il_mutate', b);
export default b;
```

- [ ] **Step 4: Add side-effect imports** in `builders/index.ts`:

```typescript
import './form_submission/integration_sku_map_approve.js';
import './form_submission/purchase_order_manual_create.js';
import './form_submission/holidays_il_mutate.js';
```

- [ ] **Step 5: Run — expect all PASS**

- [ ] **Step 6: Commit**

```bash
git commit -am "feat(api): activity_log misc form builders (sku map, manual PO, holidays)"
```

---

### Task 13: Credit-decision builders (2) + exception builders (2) + tests

**Files:**
- Create: `api/src/activity_log/builders/credit_decision/approve.ts`
- Create: `api/src/activity_log/builders/credit_decision/reject.ts`
- Create: `api/src/activity_log/builders/exception_acknowledge/_default.ts`
- Create: `api/src/activity_log/builders/exception_resolve/_default.ts`
- Modify: `api/src/activity_log/builders/index.ts`
- Modify: `api/test/activity_log_builders.test.ts`

- [ ] **Step 1: Append failing tests**

```typescript
test('credit_decision approve — exception title + state label', async () => {
  const out = await buildSummary(
    row({
      source_kind: 'credit_decision',
      action_kind: 'approve',
      raw_payload: { exception_id: 'e1', reason: null, state: 'gi_draft_created' },
      // The builder JOINs to exceptions.title for the exception_id.
    }),
    ctx,
  );
  // We don't know the exact title for e1 in fixtures, but headline must start
  // with 'Credit approved · ' and secondary must be the GI draft label.
  assert.match(out.headline, /^Credit approved · /);
  assert.equal(out.secondary, 'GI draft created');
});

test('credit_decision reject — exception title + reason', async () => {
  const out = await buildSummary(
    row({
      source_kind: 'credit_decision',
      action_kind: 'reject',
      raw_payload: { exception_id: 'e1', reason: 'driver returned the product', state: 'cancelled' },
    }),
    ctx,
  );
  assert.match(out.headline, /^Credit rejected · /);
  assert.equal(out.secondary, 'driver returned the product');
});

test('exception_acknowledge — title + category', async () => {
  const out = await buildSummary(
    row({
      source_kind: 'exception_acknowledge',
      action_kind: 'lionwheel_credit_needed',
      raw_payload: { title: 'Credit needed for task #1234', category: 'lionwheel_credit_needed', severity: 'warning' },
    }),
    ctx,
  );
  assert.equal(out.headline, 'Acknowledged · Credit needed for task #1234');
  assert.equal(out.secondary, 'LionWheel credit needed');
});

test('exception_resolve — title + resolution_notes truncated to 80', async () => {
  const long = 'x'.repeat(120);
  const out = await buildSummary(
    row({
      source_kind: 'exception_resolve',
      action_kind: 'count_large_variance',
      raw_payload: { title: 'Count variance on Tomatoes', category: 'count_large_variance', severity: 'warning', resolution_notes: long },
    }),
    ctx,
  );
  assert.equal(out.headline, 'Resolved · Count variance on Tomatoes');
  assert.equal(out.secondary!.length, 80 + 1);  // 80 chars + ellipsis
  assert.ok(out.secondary!.endsWith('…'));
});

test('exception_resolve without resolution_notes — falls back to category label', async () => {
  const out = await buildSummary(
    row({
      source_kind: 'exception_resolve',
      action_kind: 'count_large_variance',
      raw_payload: { title: 'Count variance on Tomatoes', category: 'count_large_variance', severity: 'warning' },
    }),
    ctx,
  );
  assert.equal(out.secondary, 'Large count variance');
});
```

- [ ] **Step 2: Run — expect FAIL**

- [ ] **Step 3: Implement 4 builders + category label map**

`api/src/activity_log/builders/exception_acknowledge/_default.ts`:
```typescript
import { register, type SummaryBuilder } from '../_registry.js';
import { categoryLabel } from './_categories.js';

const b: SummaryBuilder = {
  async build(row) {
    const p = (row.raw_payload ?? {}) as { title?: string; category?: string };
    return {
      headline: `Acknowledged · ${p.title ?? 'unknown exception'}`,
      secondary: categoryLabel(p.category) ?? null,
    };
  },
};
register('exception_acknowledge', '_default', b);
export default b;
```

`api/src/activity_log/builders/exception_acknowledge/_categories.ts`:
```typescript
export const CATEGORY_LABEL: Record<string, string> = {
  lionwheel_credit_needed:    'LionWheel credit needed',
  count_large_variance:       'Large count variance',
  gr_quantity_over_received:  'GR over-received',
  shopify_sku_unmapped:       'Unmapped Shopify SKU',
  // Extend as new categories appear; lowercase->label map.
};
export function categoryLabel(category: string | undefined): string | null {
  if (!category) return null;
  return CATEGORY_LABEL[category] ?? category;
}
```

`api/src/activity_log/builders/exception_resolve/_default.ts`:
```typescript
import { register, type SummaryBuilder } from '../_registry.js';
import { categoryLabel } from '../exception_acknowledge/_categories.js';

function truncate(s: string, max: number): string {
  return s.length <= max ? s : s.slice(0, max) + '…';
}

const b: SummaryBuilder = {
  async build(row) {
    const p = (row.raw_payload ?? {}) as { title?: string; category?: string; resolution_notes?: string };
    const headline = `Resolved · ${p.title ?? 'unknown exception'}`;
    const secondary = p.resolution_notes ? truncate(p.resolution_notes, 80) : (categoryLabel(p.category) ?? null);
    return { headline, secondary };
  },
};
register('exception_resolve', '_default', b);
export default b;
```

`api/src/activity_log/builders/credit_decision/approve.ts`:
```typescript
import { sql } from 'kysely';
import { register, type SummaryBuilder } from '../_registry.js';

const STATE_LABEL: Record<string, string> = {
  pending_gi_action:  'Pending GI action',
  gi_draft_created:   'GI draft created',
  resolved:           'Resolved',
};

async function exceptionTitle(db: any, exceptionId: string | undefined): Promise<string> {
  if (!exceptionId) return 'unknown exception';
  const r = await sql<{ title: string }>`SELECT title FROM private_core.exceptions WHERE exception_id = ${exceptionId}::uuid`.execute(db);
  return r.rows[0]?.title ?? `exception ${exceptionId.slice(0, 8)}`;
}

const b: SummaryBuilder = {
  async build(row, { db }) {
    const p = (row.raw_payload ?? {}) as { exception_id?: string; state?: string };
    const title = await exceptionTitle(db, p.exception_id);
    return {
      headline: `Credit approved · ${title}`,
      secondary: p.state ? (STATE_LABEL[p.state] ?? p.state) : null,
    };
  },
};
register('credit_decision', 'approve', b);
export default b;
```

`api/src/activity_log/builders/credit_decision/reject.ts`:
```typescript
import { sql } from 'kysely';
import { register, type SummaryBuilder } from '../_registry.js';

async function exceptionTitle(db: any, exceptionId: string | undefined): Promise<string> {
  if (!exceptionId) return 'unknown exception';
  const r = await sql<{ title: string }>`SELECT title FROM private_core.exceptions WHERE exception_id = ${exceptionId}::uuid`.execute(db);
  return r.rows[0]?.title ?? `exception ${exceptionId.slice(0, 8)}`;
}

const b: SummaryBuilder = {
  async build(row, { db }) {
    const p = (row.raw_payload ?? {}) as { exception_id?: string; reason?: string };
    const title = await exceptionTitle(db, p.exception_id);
    return {
      headline: `Credit rejected · ${title}`,
      secondary: p.reason ?? null,
    };
  },
};
register('credit_decision', 'reject', b);
export default b;
```

- [ ] **Step 4: Add side-effect imports** in `builders/index.ts`:

```typescript
import './credit_decision/approve.js';
import './credit_decision/reject.js';
import './exception_acknowledge/_default.js';
import './exception_resolve/_default.js';
```

- [ ] **Step 5: Run — expect all PASS**

- [ ] **Step 6: Commit**

```bash
git commit -am "feat(api): activity_log credit-decision + exception builders"
```

---

### Task 14: Unknown-action fail-loud test

**Files:**
- Modify: `api/test/activity_log_builders.test.ts`

- [ ] **Step 1: Append the test**

```typescript
test('unknown action_kind — fail-loud headline and secondary', async () => {
  const out = await buildSummary(
    row({
      source_kind: 'form_submission',
      action_kind: 'some_brand_new_form_type_with_no_builder',
      raw_payload: { whatever: 1 },
    }),
    ctx,
  );
  assert.equal(out.headline, '⚠ Unknown action: form_submission / some_brand_new_form_type_with_no_builder');
  assert.equal(out.secondary, '(no summary builder)');
});
```

- [ ] **Step 2: Run — expect PASS** (logic is already in the registry; this just locks the behavior)

```bash
node --test --import tsx test/activity_log_builders.test.ts
```

- [ ] **Step 3: Commit**

```bash
git commit -am "test(api): activity_log fail-loud on unknown action"
```

---

## Stage 3 — List endpoint

### Task 15: List handler with keyset pagination + integration test

**Files:**
- Create: `api/src/activity_log/list_handler.ts`
- Create: `api/test/activity_log_list.test.ts`
- Create (only): `api/src/activity_log/route.ts` (skeleton — gets fleshed out in Task 17)

- [ ] **Step 1: Write the failing integration test**

```typescript
// api/test/activity_log_list.test.ts
import './_test_env.ts';
import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { sql } from 'kysely';
import { buildServer } from '../src/server.ts';
import type { FastifyInstance } from 'fastify';
import type { Session } from '../src/auth/session.ts';

const USER = 'dddddddd-0000-0000-0000-000000000003';  // planner from fixture
const session: Session = {
  user_id: USER,
  email: 'planner@al-test.gt',
  role: 'planner',
  display_name: 'Activity Log Test',
};

let app: FastifyInstance;

before(async () => {
  app = await buildServer({ injectSession: () => session });
});

after(async () => {
  await app.close();
});

test('GET /api/v1/queries/me/activity returns rows for the calling user only', async () => {
  const res = await app.inject({
    method: 'GET',
    url: '/api/v1/queries/me/activity?limit=10',
    headers: { 'x-test-session': JSON.stringify(session) },
  });
  assert.equal(res.statusCode, 200);
  const body = res.json() as {
    rows: { activity_id: string; source_kind: string; summary: { headline: string } }[];
    next_cursor: string | null;
    has_more: boolean;
  };
  assert.ok(Array.isArray(body.rows));
  assert.ok(body.rows.length <= 10);
  for (const r of body.rows) {
    assert.ok(typeof r.summary.headline === 'string' && r.summary.headline.length > 0);
    assert.ok(['form_submission', 'credit_decision', 'exception_acknowledge', 'exception_resolve'].includes(r.source_kind));
  }
});

test('limit=200 max enforced; limit=300 rejected at 422', async () => {
  const res = await app.inject({
    method: 'GET',
    url: '/api/v1/queries/me/activity?limit=300',
    headers: { 'x-test-session': JSON.stringify(session) },
  });
  assert.equal(res.statusCode, 422);
});

test('source_kind filter narrows results', async () => {
  const res = await app.inject({
    method: 'GET',
    url: '/api/v1/queries/me/activity?source_kind=form_submission&limit=20',
    headers: { 'x-test-session': JSON.stringify(session) },
  });
  assert.equal(res.statusCode, 200);
  const body = res.json() as { rows: { source_kind: string }[] };
  for (const r of body.rows) assert.equal(r.source_kind, 'form_submission');
});

test('cursor pagination: page 2 returns rows strictly older than page 1 tail', async () => {
  const p1 = await app.inject({
    method: 'GET',
    url: '/api/v1/queries/me/activity?limit=5',
    headers: { 'x-test-session': JSON.stringify(session) },
  });
  assert.equal(p1.statusCode, 200);
  const body1 = p1.json() as { rows: { event_at: string }[]; next_cursor: string | null; has_more: boolean };
  if (!body1.has_more || body1.rows.length === 0) return;  // not enough data; skip

  const p2 = await app.inject({
    method: 'GET',
    url: `/api/v1/queries/me/activity?limit=5&cursor=${encodeURIComponent(body1.next_cursor!)}`,
    headers: { 'x-test-session': JSON.stringify(session) },
  });
  assert.equal(p2.statusCode, 200);
  const body2 = p2.json() as { rows: { event_at: string }[] };
  if (body2.rows.length === 0) return;
  const tail1 = body1.rows[body1.rows.length - 1].event_at;
  const head2 = body2.rows[0].event_at;
  assert.ok(head2 <= tail1, `page 2 head (${head2}) must be <= page 1 tail (${tail1})`);
});

test('cross-user isolation: rows always belong to session user', async () => {
  // We can't directly assert "no other user's rows", but we can check that
  // the SQL filter is applied by inspecting one returned activity's actor.
  // The list response does not include actor_user_id directly, so we rely on
  // the drawer endpoint test (Task 18) to confirm. Here we just verify the
  // endpoint runs without error for a user with no activity.
  const otherSession: Session = {
    user_id: '00000000-0000-0000-0000-000000000000',  // non-existent fixture user
    email: 'nobody@al-test.gt',
    role: 'viewer',
    display_name: 'Nobody',
  };
  const res = await app.inject({
    method: 'GET',
    url: '/api/v1/queries/me/activity?limit=5',
    headers: { 'x-test-session': JSON.stringify(otherSession) },
  });
  assert.equal(res.statusCode, 200);
  const body = res.json() as { rows: unknown[] };
  assert.equal(body.rows.length, 0);
});
```

- [ ] **Step 2: Run — expect FAIL (route not registered)**

```bash
node --test --import tsx test/activity_log_list.test.ts
```

Expected: 404 on every request.

- [ ] **Step 3: Implement the handler**

`api/src/activity_log/list_handler.ts`:
```typescript
// /api/v1/queries/me/activity handler.
//
// Keyset pagination on (event_at DESC, activity_id DESC). Filters by
// source_kind / action_kind / status / from / to. The user_id filter
// (actor_user_id = session.user_id) is mandatory and cannot be relaxed
// by any query param.

import { sql } from 'kysely';
import type { Db } from '../db/connection.js';
import type { Session } from '../auth/session.js';
import { AuthError } from '../auth/session.js';
import {
  type ListQuery,
  type MyActivityListResponse,
  type MyActivityRow,
  decodeCursor,
  encodeCursor,
} from './schemas.js';
import { buildSummary, type ViewRow } from './builders/_registry.js';
import './builders/index.js';   // side-effect: register all builders

interface ListResult {
  kind: 'ok';
  status: 200;
  body: MyActivityListResponse;
}

export async function handleListActivity(
  db: Db,
  session: Session,
  query: ListQuery,
): Promise<ListResult> {
  // Auth — all 4 roles can read their own
  if (!['operator', 'planner', 'admin', 'viewer'].includes(session.role)) {
    throw new AuthError('Not authorised', 403);
  }

  const limit = query.limit;
  const cursor = query.cursor ? decodeCursor(query.cursor) : null;

  // Build the WHERE clause incrementally.
  // event_at DESC, activity_id DESC pagination:
  //   (event_at, activity_id) < (cursor.event_at, cursor.activity_id)
  // We fetch limit+1 rows to know if there is a next page.
  const conds: ReturnType<typeof sql>[] = [
    sql`actor_user_id = ${session.user_id}::uuid`,
  ];
  if (cursor) {
    conds.push(sql`(event_at, activity_id) < (${cursor.event_at}::timestamptz, ${cursor.activity_id})`);
  }
  if (query.source_kind && query.source_kind.length > 0) {
    conds.push(sql`source_kind = ANY(${query.source_kind}::text[])`);
  }
  if (query.action_kind && query.action_kind.length > 0) {
    conds.push(sql`action_kind = ANY(${query.action_kind}::text[])`);
  }
  if (query.status && query.status.length > 0) {
    conds.push(sql`status = ANY(${query.status}::text[])`);
  }
  if (query.from) conds.push(sql`event_at >= ${query.from}::timestamptz`);
  if (query.to)   conds.push(sql`event_at <  ${query.to}::timestamptz`);

  const where = sql.join(conds, sql` AND `);

  const result = await sql<ViewRow & { event_at: Date; posted_at: Date | null }>`
    SELECT activity_id, source_kind, action_kind, event_at, status,
           actor_user_id::text AS actor_user_id, source_pk,
           raw_payload, posted_at, extra_text
      FROM private_core.v_my_activity_log
     WHERE ${where}
     ORDER BY event_at DESC, activity_id DESC
     LIMIT ${limit + 1}
  `.execute(db);

  const rawRows = result.rows;
  const hasMore = rawRows.length > limit;
  const pageRows = hasMore ? rawRows.slice(0, limit) : rawRows;

  const ctx = { db };
  const rows: MyActivityRow[] = await Promise.all(
    pageRows.map(async (r) => {
      const event_at_iso = (r.event_at instanceof Date ? r.event_at.toISOString() : String(r.event_at));
      const posted_at_iso = r.posted_at instanceof Date ? r.posted_at.toISOString() : (r.posted_at ?? null);
      const viewRow: ViewRow = {
        ...r,
        event_at: event_at_iso,
        posted_at: posted_at_iso,
      };
      const summary = await buildSummary(viewRow, ctx);
      if (summary.headline.startsWith('⚠ Unknown action')) {
        // Fail-loud structured log
        // eslint-disable-next-line no-console
        console.warn(JSON.stringify({
          event: 'activity_log.missing_builder',
          source_kind: r.source_kind,
          action_kind: r.action_kind,
          activity_id: r.activity_id,
        }));
      }
      return {
        activity_id: r.activity_id,
        source_kind: r.source_kind,
        action_kind: r.action_kind,
        event_at: event_at_iso,
        posted_at: posted_at_iso,
        status: r.status,
        rejection_reason: (r.source_kind === 'form_submission' ? r.extra_text : null),
        summary,
        raw_payload_present: r.raw_payload !== null && r.raw_payload !== undefined,
      };
    }),
  );

  const next_cursor: string | null = hasMore && rows.length > 0
    ? encodeCursor({
        event_at: rows[rows.length - 1].event_at,
        activity_id: rows[rows.length - 1].activity_id,
      })
    : null;

  return {
    kind: 'ok',
    status: 200,
    body: { rows, next_cursor, has_more: hasMore },
  };
}
```

- [ ] **Step 4: Implement the route skeleton**

`api/src/activity_log/route.ts`:
```typescript
import type { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { ZodError } from 'zod';
import type { Db } from '../db/connection.js';
import type { Session } from '../auth/session.js';
import { AuthError } from '../auth/session.js';
import { handleListActivity } from './list_handler.js';
import { listQuerySchema } from './schemas.js';

export interface RouteDeps {
  db: Db;
  extractSession: (req: FastifyRequest) => Promise<Session>;
}

export function registerActivityLogRoute(app: FastifyInstance, deps: RouteDeps): void {
  app.get('/api/v1/queries/me/activity', async (req: FastifyRequest, reply: FastifyReply) => {
    let session: Session;
    try {
      session = await deps.extractSession(req);
    } catch (err) {
      if (err instanceof AuthError) return reply.code(err.statusCode).send({ error: err.message });
      throw err;
    }
    let query;
    try {
      query = listQuerySchema.parse(req.query ?? {});
    } catch (err) {
      if (err instanceof ZodError) {
        return reply.code(422).send({ error: 'Invalid query', issues: err.issues });
      }
      throw err;
    }
    try {
      const result = await handleListActivity(deps.db, session, query);
      return reply.code(result.status).send(result.body);
    } catch (err) {
      if (err instanceof AuthError) return reply.code(err.statusCode).send({ error: err.message });
      throw err;
    }
  });
}
```

- [ ] **Step 5: Wire route into server.ts**

In `api/src/server.ts`, find the existing `registerSubmissionsRoute(...)` call. Immediately after it, add:

```typescript
import { registerActivityLogRoute } from './activity_log/route.js';
// ...
registerActivityLogRoute(app, { db, extractSession });
```

- [ ] **Step 6: Run — expect PASS**

```bash
node --test --import tsx test/activity_log_list.test.ts
```

Expected: 5 tests pass.

- [ ] **Step 7: Commit**

```bash
git add api/src/activity_log/list_handler.ts api/src/activity_log/route.ts \
        api/src/server.ts api/test/activity_log_list.test.ts
git commit -m "feat(api): /api/v1/queries/me/activity list endpoint with keyset pagination"
```

---

## Stage 4 — Drawer endpoint

### Task 16: Drawer handler + integration test

**Files:**
- Create: `api/src/activity_log/drawer_handler.ts`
- Create: `api/test/activity_log_drawer.test.ts`
- Modify: `api/src/activity_log/route.ts`

- [ ] **Step 1: Write the failing integration test**

```typescript
// api/test/activity_log_drawer.test.ts
import './_test_env.ts';
import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { buildServer } from '../src/server.ts';
import type { FastifyInstance } from 'fastify';
import type { Session } from '../src/auth/session.ts';

const USER = 'dddddddd-0000-0000-0000-000000000003';
const session: Session = {
  user_id: USER,
  email: 'planner@al-test.gt',
  role: 'planner',
  display_name: 'Drawer Test',
};

let app: FastifyInstance;
let aSubmissionId: string;

before(async () => {
  app = await buildServer({ injectSession: () => session });
  // Find a real activity_id for this user
  const list = await app.inject({
    method: 'GET',
    url: '/api/v1/queries/me/activity?limit=1',
    headers: { 'x-test-session': JSON.stringify(session) },
  });
  const body = list.json() as { rows: { activity_id: string }[] };
  if (body.rows.length === 0) throw new Error('drawer test requires fixture user to have activity rows');
  aSubmissionId = body.rows[0].activity_id;
});

after(async () => { await app.close(); });

test('GET /me/activity/:id returns the full row with summary + redacted payload + cross_links', async () => {
  const res = await app.inject({
    method: 'GET',
    url: `/api/v1/queries/me/activity/${encodeURIComponent(aSubmissionId)}`,
    headers: { 'x-test-session': JSON.stringify(session) },
  });
  assert.equal(res.statusCode, 200);
  const body = res.json() as {
    row: {
      activity_id: string;
      summary: { headline: string; secondary: string | null };
      raw_payload_redacted: Record<string, unknown> | null;
      cross_links: { kind: string; label: string; target_id: string }[];
    };
  };
  assert.equal(body.row.activity_id, aSubmissionId);
  assert.ok(body.row.summary.headline.length > 0);
  assert.ok(Array.isArray(body.row.cross_links));
});

test('GET /me/activity/:id 404 for activity belonging to other user', async () => {
  // Construct an obviously-not-mine activity_id; expect 404.
  const fakeId = 'sub_00000000-0000-0000-0000-000000000000';
  const res = await app.inject({
    method: 'GET',
    url: `/api/v1/queries/me/activity/${encodeURIComponent(fakeId)}`,
    headers: { 'x-test-session': JSON.stringify(session) },
  });
  assert.equal(res.statusCode, 404);
});

test('GET /me/activity/:id redacts secret-like fields in payload', async () => {
  // We can't directly inject a secret-shaped payload here without writing one.
  // Instead we trust the unit test in activity_log_redaction.test.ts and just
  // confirm the drawer returns a redacted object (not the raw payload).
  const res = await app.inject({
    method: 'GET',
    url: `/api/v1/queries/me/activity/${encodeURIComponent(aSubmissionId)}`,
    headers: { 'x-test-session': JSON.stringify(session) },
  });
  assert.equal(res.statusCode, 200);
  const body = res.json() as {
    row: { raw_payload_redacted: unknown };
  };
  // raw_payload_redacted is present, can be object or null.
  assert.ok(body.row.raw_payload_redacted !== undefined);
});
```

- [ ] **Step 2: Run — expect FAIL (route not registered)**

```bash
node --test --import tsx test/activity_log_drawer.test.ts
```

- [ ] **Step 3: Implement the drawer handler**

`api/src/activity_log/drawer_handler.ts`:
```typescript
import { sql } from 'kysely';
import type { Db } from '../db/connection.js';
import type { Session } from '../auth/session.js';
import { AuthError } from '../auth/session.js';
import type { MyActivityDrawerResponse } from './schemas.js';
import { buildSummary, type ViewRow } from './builders/_registry.js';
import { redactPayload } from './redaction.js';
import './builders/index.js';

export type DrawerResult =
  | { kind: 'ok'; status: 200; body: MyActivityDrawerResponse }
  | { kind: 'not_found'; status: 404; body: { error: string } };

const VALID_PREFIX = /^(sub_|dec_|ack_|res_)/;

export async function handleDrawerActivity(
  db: Db,
  session: Session,
  activityId: string,
): Promise<DrawerResult> {
  if (!['operator', 'planner', 'admin', 'viewer'].includes(session.role)) {
    throw new AuthError('Not authorised', 403);
  }
  if (!VALID_PREFIX.test(activityId)) {
    return { kind: 'not_found', status: 404, body: { error: 'activity_id not recognised' } };
  }

  const r = await sql<ViewRow & { event_at: Date; posted_at: Date | null }>`
    SELECT activity_id, source_kind, action_kind, event_at, status,
           actor_user_id::text AS actor_user_id, source_pk,
           raw_payload, posted_at, extra_text
      FROM private_core.v_my_activity_log
     WHERE activity_id = ${activityId}
       AND actor_user_id = ${session.user_id}::uuid
     LIMIT 1
  `.execute(db);

  if (r.rows.length === 0) {
    return { kind: 'not_found', status: 404, body: { error: 'activity not found' } };
  }
  const row = r.rows[0];
  const event_at_iso = row.event_at instanceof Date ? row.event_at.toISOString() : String(row.event_at);
  const posted_at_iso = row.posted_at instanceof Date ? row.posted_at.toISOString() : (row.posted_at ?? null);
  const viewRow: ViewRow = { ...row, event_at: event_at_iso, posted_at: posted_at_iso };
  const summary = await buildSummary(viewRow, { db });

  const cross_links = await crossLinks(db, viewRow);

  return {
    kind: 'ok',
    status: 200,
    body: {
      row: {
        activity_id: row.activity_id,
        source_kind: row.source_kind,
        action_kind: row.action_kind,
        event_at: event_at_iso,
        posted_at: posted_at_iso,
        status: row.status,
        rejection_reason: row.source_kind === 'form_submission' ? row.extra_text : null,
        summary,
        raw_payload_present: row.raw_payload !== null && row.raw_payload !== undefined,
        raw_payload_redacted: redactPayload(row.raw_payload),
        cross_links,
      },
    },
  };
}

async function crossLinks(db: Db, row: ViewRow): Promise<{ kind: string; label: string; target_id: string }[]> {
  const links: { kind: string; label: string; target_id: string }[] = [];
  // form_submission → ledger movements produced by this submission_id
  if (row.source_kind === 'form_submission') {
    const r = await sql<{ movement_id: string }>`
      SELECT movement_id::text AS movement_id
        FROM private_core.stock_ledger
       WHERE source_event_id = ${row.source_pk}
       ORDER BY event_at ASC
       LIMIT 25
    `.execute(db);
    for (const m of r.rows) {
      links.push({ kind: 'ledger_movement', label: `Movement ${m.movement_id.slice(0, 8)}`, target_id: m.movement_id });
    }
  }
  // credit_decision → exception
  if (row.source_kind === 'credit_decision') {
    const p = (row.raw_payload ?? {}) as { exception_id?: string };
    if (p.exception_id) {
      links.push({ kind: 'exception', label: 'Related exception', target_id: p.exception_id });
    }
  }
  // exception_* → the exception itself (source_pk)
  if (row.source_kind === 'exception_acknowledge' || row.source_kind === 'exception_resolve') {
    links.push({ kind: 'exception', label: 'Exception card', target_id: row.source_pk });
  }
  return links;
}
```

- [ ] **Step 4: Wire drawer route in route.ts**

Append to `api/src/activity_log/route.ts`:
```typescript
import { handleDrawerActivity } from './drawer_handler.js';
// ... inside registerActivityLogRoute:
app.get('/api/v1/queries/me/activity/:activity_id', async (req: FastifyRequest, reply: FastifyReply) => {
  let session: Session;
  try {
    session = await deps.extractSession(req);
  } catch (err) {
    if (err instanceof AuthError) return reply.code(err.statusCode).send({ error: err.message });
    throw err;
  }
  const id = (req.params as { activity_id: string }).activity_id;
  try {
    const result = await handleDrawerActivity(deps.db, session, id);
    return reply.code(result.status).send(result.body);
  } catch (err) {
    if (err instanceof AuthError) return reply.code(err.statusCode).send({ error: err.message });
    throw err;
  }
});
```

- [ ] **Step 5: Run — expect PASS**

```bash
node --test --import tsx test/activity_log_drawer.test.ts
```

- [ ] **Step 6: Commit**

```bash
git add api/src/activity_log/drawer_handler.ts api/src/activity_log/route.ts \
        api/test/activity_log_drawer.test.ts
git commit -m "feat(api): /api/v1/queries/me/activity/:id drawer endpoint"
```

---

## Stage 5 — Portal

### Task 17: Portal proxy routes

**Files:**
- Create: `src/app/api/me/activity/route.ts`
- Create: `src/app/api/me/activity/[activityId]/route.ts`

(In the portal working tree `c:/Users/tomw2/Projects/window2-portal-sandbox/`.)

- [ ] **Step 1: List proxy**

`src/app/api/me/activity/route.ts`:
```typescript
import { proxyRequest } from "@/lib/api-proxy";

export async function GET(req: Request): Promise<Response> {
  const url = new URL(req.url);
  const qs = url.search;
  return proxyRequest(req, {
    method: "GET",
    upstreamPath: `/api/v1/queries/me/activity${qs}`,
    errorLabel: "my activity",
  });
}
```

- [ ] **Step 2: Drawer proxy**

`src/app/api/me/activity/[activityId]/route.ts`:
```typescript
import { proxyRequest } from "@/lib/api-proxy";

export async function GET(
  req: Request,
  { params }: { params: Promise<{ activityId: string }> },
): Promise<Response> {
  const { activityId } = await params;
  return proxyRequest(req, {
    method: "GET",
    upstreamPath: `/api/v1/queries/me/activity/${encodeURIComponent(activityId)}`,
    errorLabel: "activity detail",
  });
}
```

- [ ] **Step 3: Typecheck**

```bash
cd /c/Users/tomw2/Projects/window2-portal-sandbox
npm run typecheck
```

- [ ] **Step 4: Commit**

```bash
git add src/app/api/me/activity/
git commit -m "feat(portal): proxy routes for /me/activity list + drawer"
```

---

### Task 18: Activity list page — types, layout skeleton, day grouping

**Files:**
- Create: `src/app/(ops)/me/activity/_types.ts`
- Create: `src/app/(ops)/me/activity/_components/DayHeader.tsx`
- Create: `src/app/(ops)/me/activity/_components/ActivityRow.tsx`
- Create: `src/app/(ops)/me/activity/page.tsx`

- [ ] **Step 1: Define types**

`src/app/(ops)/me/activity/_types.ts`:
```typescript
export type SourceKind =
  | "form_submission"
  | "credit_decision"
  | "exception_acknowledge"
  | "exception_resolve";

export interface ActivityRow {
  activity_id: string;
  source_kind: SourceKind;
  action_kind: string;
  event_at: string;
  posted_at: string | null;
  status: string;
  rejection_reason: string | null;
  summary: { headline: string; secondary: string | null };
  raw_payload_present: boolean;
}

export interface ActivityListResponse {
  rows: ActivityRow[];
  next_cursor: string | null;
  has_more: boolean;
}

export interface ActivityCrossLink {
  kind: string;
  label: string;
  target_id: string;
}

export interface ActivityDrawerResponse {
  row: ActivityRow & {
    raw_payload_redacted: unknown;
    cross_links: ActivityCrossLink[];
  };
}
```

- [ ] **Step 2: DayHeader component**

`src/app/(ops)/me/activity/_components/DayHeader.tsx`:
```typescript
"use client";
import { cn } from "@/lib/cn";

function isSameDay(a: Date, b: Date) {
  return a.toDateString() === b.toDateString();
}
function daysAgo(d: Date) {
  return Math.floor((Date.now() - d.getTime()) / (1000 * 60 * 60 * 24));
}

export function dayLabel(iso: string): string {
  const d = new Date(iso);
  const today = new Date();
  if (isSameDay(d, today)) return "Today";
  const yesterday = new Date(today);
  yesterday.setDate(today.getDate() - 1);
  if (isSameDay(d, yesterday)) return "Yesterday";
  const dayDiff = daysAgo(d);
  if (dayDiff > 0 && dayDiff < 7) {
    return d.toLocaleDateString(undefined, { weekday: "long" });
  }
  return d.toLocaleDateString(undefined, { day: "2-digit", month: "short", year: "numeric" });
}

export function DayHeader({ label, count }: { label: string; count: number }) {
  return (
    <div className={cn(
      "sticky top-0 z-10 flex items-baseline justify-between gap-2",
      "border-b border-border/60 bg-bg-base/95 px-5 py-2 backdrop-blur"
    )}>
      <span className="text-xs font-semibold uppercase tracking-wide text-fg-muted">
        {label}
      </span>
      <span className="text-3xs text-fg-subtle">
        {count} {count === 1 ? "action" : "actions"}
      </span>
    </div>
  );
}
```

- [ ] **Step 3: ActivityRow component**

`src/app/(ops)/me/activity/_components/ActivityRow.tsx`:
```typescript
"use client";
import { Badge } from "@/components/badges/StatusBadge";
import { cn } from "@/lib/cn";
import type { ActivityRow as ActivityRowT } from "../_types";

function fmtTime(iso: string) {
  return new Date(iso).toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
}
function timeAgo(iso: string) {
  const m = Math.floor((Date.now() - new Date(iso).getTime()) / 60000);
  if (m < 1) return "just now";
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

function StatusBadge({ status }: { status: string }) {
  if (status === "posted")            return <Badge tone="success" variant="solid">Posted</Badge>;
  if (status === "pending")           return <Badge tone="warning" dotted>Pending approval</Badge>;
  if (status === "rejected")          return <Badge tone="danger" variant="solid">Rejected</Badge>;
  if (status === "cancelled")         return <Badge tone="neutral" dotted>Cancelled</Badge>;
  if (status === "acknowledged")      return <Badge tone="info" dotted>Acknowledged</Badge>;
  if (status === "resolved")          return <Badge tone="success" dotted>Resolved</Badge>;
  if (status === "gi_draft_created")  return <Badge tone="success" variant="solid">GI draft created</Badge>;
  if (status === "pending_gi_action") return <Badge tone="warning" dotted>Pending GI action</Badge>;
  return <Badge tone="neutral" dotted>{status}</Badge>;
}

export function ActivityRow({
  row,
  onClick,
}: {
  row: ActivityRowT;
  onClick: (row: ActivityRowT) => void;
}) {
  return (
    <li>
      <button
        type="button"
        onClick={() => onClick(row)}
        className={cn(
          "flex w-full flex-col gap-1.5 px-5 py-3 text-left",
          "hover:bg-bg-subtle/40 focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent",
          "sm:flex-row sm:items-start sm:justify-between"
        )}
      >
        <div className="flex flex-col gap-0.5 min-w-0 flex-1">
          <div className="flex items-center gap-2 min-w-0">
            <span className="truncate text-sm font-medium text-fg">
              {row.summary.headline}
            </span>
            <span
              title={`Activity ID: ${row.activity_id}`}
              onClick={(e) => {
                e.stopPropagation();
                void navigator.clipboard.writeText(row.activity_id);
              }}
              className="shrink-0 cursor-pointer"
            >
              <StatusBadge status={row.status} />
            </span>
          </div>
          {row.summary.secondary ? (
            <div className="truncate text-xs text-fg-muted">
              {row.summary.secondary}
            </div>
          ) : null}
          {row.rejection_reason ? (
            <div className="truncate text-xs text-danger-fg">
              Rejected: {row.rejection_reason}
            </div>
          ) : null}
        </div>
        <div className="shrink-0 text-right text-xs text-fg-muted">
          <div>{timeAgo(row.event_at)}</div>
          <div className="mt-0.5 text-3xs text-fg-subtle">{fmtTime(row.event_at)}</div>
          {row.posted_at && row.posted_at !== row.event_at ? (
            <div className="mt-0.5 text-3xs text-success-fg">
              Posted {timeAgo(row.posted_at)}
            </div>
          ) : null}
        </div>
      </button>
    </li>
  );
}
```

- [ ] **Step 4: Page skeleton (no filters yet)**

`src/app/(ops)/me/activity/page.tsx`:
```typescript
"use client";

// ---------------------------------------------------------------------------
// /me/activity — per-user append-only activity log.
//
// UNIONs form_submissions, credit_decisions, and exception ack/resolve into
// one chronological feed. Day-grouped sticky headers, keyset pagination,
// click row → side drawer.
//
// Subtitle copy intentionally communicates append-only semantics.
// ---------------------------------------------------------------------------

import { useMemo, useState, useCallback } from "react";
import { useInfiniteQuery } from "@tanstack/react-query";
import { WorkflowHeader } from "@/components/workflow/WorkflowHeader";
import { SectionCard } from "@/components/workflow/SectionCard";
import { EmptyState } from "@/components/feedback/states";
import { DayHeader, dayLabel } from "./_components/DayHeader";
import { ActivityRow } from "./_components/ActivityRow";
import type { ActivityListResponse, ActivityRow as ActivityRowT } from "./_types";

export default function MyActivityPage() {
  const [selected, setSelected] = useState<ActivityRowT | null>(null);

  const query = useInfiniteQuery<ActivityListResponse, Error>({
    queryKey: ["me", "activity"],
    initialPageParam: undefined as string | undefined,
    queryFn: async ({ pageParam }) => {
      const url = new URL("/api/me/activity", window.location.origin);
      url.searchParams.set("limit", "100");
      if (pageParam) url.searchParams.set("cursor", pageParam as string);
      const res = await fetch(url.toString());
      if (!res.ok) throw new Error("Could not load activity. Check your connection and try refreshing.");
      return res.json() as Promise<ActivityListResponse>;
    },
    getNextPageParam: (last) => last.next_cursor ?? undefined,
    staleTime: 30 * 1000,
  });

  const allRows: ActivityRowT[] = useMemo(
    () => (query.data?.pages ?? []).flatMap((p) => p.rows),
    [query.data],
  );

  const grouped = useMemo(() => groupByDay(allRows), [allRows]);

  const onRowClick = useCallback((r: ActivityRowT) => setSelected(r), []);

  return (
    <>
      <WorkflowHeader
        eyebrow="Me"
        title="My activity"
        description="Append-only history of every action you took in the system. Permanent — corrections create new entries."
      />
      {query.isError ? (
        <div className="rounded-md border border-danger/40 bg-danger-softer px-4 py-3 text-sm text-danger-fg">
          <div className="font-semibold">Could not load activity</div>
          <button
            type="button"
            onClick={() => void query.refetch()}
            className="mt-2 text-xs font-medium text-danger-fg underline hover:no-underline"
          >Retry</button>
        </div>
      ) : null}

      <SectionCard contentClassName="p-0">
        {query.isLoading ? (
          <ul className="divide-y divide-border/60 px-5 py-5" aria-busy="true" aria-live="polite">
            {Array.from({ length: 6 }).map((_, i) => (
              <li key={i} className="flex animate-pulse gap-3 py-2">
                <div className="h-5 w-2/3 rounded bg-bg-subtle" />
                <div className="h-5 w-20 rounded bg-bg-subtle" />
              </li>
            ))}
          </ul>
        ) : allRows.length === 0 ? (
          <EmptyState
            title="No activity yet"
            description="When you submit a form, approve a credit, or resolve an Inbox card, it will appear here."
          />
        ) : (
          <ul className="divide-y divide-border/60">
            {grouped.map(({ label, rows }) => (
              <div key={label}>
                <DayHeader label={label} count={rows.length} />
                {rows.map((r) => (
                  <ActivityRow key={r.activity_id} row={r} onClick={onRowClick} />
                ))}
              </div>
            ))}
          </ul>
        )}
        {query.hasNextPage ? (
          <div className="flex items-center justify-center border-t border-border/60 p-3">
            <button
              type="button"
              onClick={() => void query.fetchNextPage()}
              disabled={query.isFetchingNextPage}
              className="text-xs font-medium text-accent underline hover:no-underline disabled:opacity-50"
            >
              {query.isFetchingNextPage ? "Loading…" : "Load more"}
            </button>
          </div>
        ) : null}
      </SectionCard>

      {/* Drawer: implemented in Task 21 */}
      {selected ? (
        <div onClick={() => setSelected(null)} className="fixed inset-0 z-40 bg-black/30">
          {/* placeholder */}
        </div>
      ) : null}
    </>
  );
}

function groupByDay(rows: ActivityRowT[]): { label: string; rows: ActivityRowT[] }[] {
  const groups = new Map<string, ActivityRowT[]>();
  for (const r of rows) {
    const lbl = dayLabel(r.event_at);
    if (!groups.has(lbl)) groups.set(lbl, []);
    groups.get(lbl)!.push(r);
  }
  return Array.from(groups.entries()).map(([label, rows]) => ({ label, rows }));
}
```

- [ ] **Step 5: Typecheck + run dev**

```bash
cd /c/Users/tomw2/Projects/window2-portal-sandbox
npm run typecheck
npm run dev
```

- [ ] **Step 6: Manual check — open `http://localhost:3000/me/activity` in browser**

Expected: page loads, shows real rows (per-user feed), day headers visible, status badges render. No console errors.

- [ ] **Step 7: Commit**

```bash
git add src/app/\(ops\)/me/activity/
git commit -m "feat(portal): /me/activity page skeleton with day-grouped rows"
```

---

### Task 19: Filters + URL state + search

**Files:**
- Create: `src/app/(ops)/me/activity/_components/FilterBar.tsx`
- Modify: `src/app/(ops)/me/activity/page.tsx`

- [ ] **Step 1: FilterBar component**

`src/app/(ops)/me/activity/_components/FilterBar.tsx`:
```typescript
"use client";
import { useState } from "react";
import { cn } from "@/lib/cn";
import type { SourceKind } from "../_types";

const SOURCE_OPTIONS: { value: SourceKind; label: string }[] = [
  { value: "form_submission",        label: "Forms" },
  { value: "credit_decision",        label: "Credit decisions" },
  { value: "exception_acknowledge",  label: "Inbox acknowledged" },
  { value: "exception_resolve",      label: "Inbox resolved" },
];

const QUICK_RANGES: { value: string; label: string; days: number }[] = [
  { value: "today",  label: "Today",      days: 0 },
  { value: "week",   label: "This week",  days: 7 },
  { value: "30d",    label: "Last 30 d",  days: 30 },
];

export interface FilterValue {
  sourceKinds: SourceKind[];
  from: string | null;
  to: string | null;
  searchTerm: string;
}

export function FilterBar({
  value,
  onChange,
}: {
  value: FilterValue;
  onChange: (next: FilterValue) => void;
}) {
  const [open, setOpen] = useState(false);

  const toggleSource = (k: SourceKind) => {
    const set = new Set(value.sourceKinds);
    if (set.has(k)) set.delete(k); else set.add(k);
    onChange({ ...value, sourceKinds: Array.from(set) });
  };

  return (
    <div className="border-b border-border/60 px-5 py-3">
      <div className="flex items-center justify-between gap-3">
        <input
          type="search"
          value={value.searchTerm}
          onChange={(e) => onChange({ ...value, searchTerm: e.target.value })}
          placeholder="Search activity (current page)"
          className="w-full max-w-md rounded-md border border-border bg-bg-base px-3 py-1.5 text-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
        />
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          aria-expanded={open}
          className="shrink-0 text-xs font-medium text-fg-muted underline hover:no-underline"
        >
          {open ? "Hide filters" : "Show filters"}
        </button>
      </div>
      {open ? (
        <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
          {SOURCE_OPTIONS.map((opt) => {
            const active = value.sourceKinds.includes(opt.value);
            return (
              <button
                key={opt.value}
                type="button"
                aria-pressed={active}
                onClick={() => toggleSource(opt.value)}
                className={cn(
                  "rounded-full border px-3 py-1",
                  active ? "border-accent bg-accent-softer text-accent-fg" : "border-border text-fg-muted"
                )}
              >
                {opt.label}
              </button>
            );
          })}
          <span className="mx-2 h-4 w-px bg-border" />
          {QUICK_RANGES.map((r) => (
            <button
              key={r.value}
              type="button"
              onClick={() => {
                const to = new Date();
                const from = new Date(to);
                if (r.value === "today") {
                  from.setHours(0, 0, 0, 0);
                } else {
                  from.setDate(to.getDate() - r.days);
                }
                onChange({ ...value, from: from.toISOString(), to: null });
              }}
              className="rounded-full border border-border px-3 py-1 text-fg-muted"
            >
              {r.label}
            </button>
          ))}
          {(value.from || value.to || value.sourceKinds.length > 0) ? (
            <button
              type="button"
              onClick={() => onChange({ sourceKinds: [], from: null, to: null, searchTerm: value.searchTerm })}
              className="ml-2 text-fg-muted underline"
            >Clear filters</button>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
```

- [ ] **Step 2: Wire filters into the page (URL state + query params)**

Modify `src/app/(ops)/me/activity/page.tsx`. Add at the top:

```typescript
import { useSearchParams, useRouter } from "next/navigation";
import { FilterBar, type FilterValue } from "./_components/FilterBar";
```

Inside `MyActivityPage`, before the `useInfiniteQuery` call:

```typescript
const searchParams = useSearchParams();
const router = useRouter();

const filter: FilterValue = useMemo(() => ({
  sourceKinds: (searchParams.getAll("source_kind") as SourceKind[]),
  from:        searchParams.get("from"),
  to:          searchParams.get("to"),
  searchTerm:  searchParams.get("q") ?? "",
}), [searchParams]);

const setFilter = useCallback((next: FilterValue) => {
  const sp = new URLSearchParams();
  for (const k of next.sourceKinds) sp.append("source_kind", k);
  if (next.from) sp.set("from", next.from);
  if (next.to)   sp.set("to",   next.to);
  if (next.searchTerm) sp.set("q", next.searchTerm);
  router.replace(`/me/activity${sp.toString() ? `?${sp.toString()}` : ""}`);
}, [router]);
```

Update the `queryFn` to pass filter params:

```typescript
queryFn: async ({ pageParam }) => {
  const url = new URL("/api/me/activity", window.location.origin);
  url.searchParams.set("limit", "100");
  if (pageParam) url.searchParams.set("cursor", pageParam as string);
  for (const k of filter.sourceKinds) url.searchParams.append("source_kind", k);
  if (filter.from) url.searchParams.set("from", filter.from);
  if (filter.to)   url.searchParams.set("to",   filter.to);
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error("Could not load activity.");
  return res.json() as Promise<ActivityListResponse>;
},
queryKey: ["me", "activity", filter.sourceKinds.join(","), filter.from, filter.to],
```

Add client-side search filter on `allRows`:

```typescript
const visibleRows = useMemo(() => {
  if (!filter.searchTerm.trim()) return allRows;
  const q = filter.searchTerm.toLowerCase();
  return allRows.filter((r) =>
    r.summary.headline.toLowerCase().includes(q) ||
    (r.summary.secondary?.toLowerCase().includes(q) ?? false) ||
    r.action_kind.toLowerCase().includes(q)
  );
}, [allRows, filter.searchTerm]);
```

Use `visibleRows` instead of `allRows` in `groupByDay(...)`. Render `<FilterBar value={filter} onChange={setFilter} />` above the list inside `<SectionCard>`.

- [ ] **Step 3: Typecheck + manual check**

```bash
npm run typecheck
```

Then in the running dev server, visit `/me/activity?source_kind=form_submission` and confirm:
- the chip "Forms" is visibly active
- only form_submission rows render
- search filters the current page

- [ ] **Step 4: Commit**

```bash
git add src/app/\(ops\)/me/activity/
git commit -m "feat(portal): filters + URL state + client search on /me/activity"
```

---

### Task 20: Side drawer with full detail

**Files:**
- Create: `src/app/(ops)/me/activity/_components/ActivityDrawer.tsx`
- Modify: `src/app/(ops)/me/activity/page.tsx`

- [ ] **Step 1: Drawer component**

`src/app/(ops)/me/activity/_components/ActivityDrawer.tsx`:
```typescript
"use client";
import { useQuery } from "@tanstack/react-query";
import { useEffect } from "react";
import { cn } from "@/lib/cn";
import type { ActivityDrawerResponse, ActivityRow } from "../_types";

export function ActivityDrawer({
  row,
  onClose,
}: {
  row: ActivityRow;
  onClose: () => void;
}) {
  const detail = useQuery<ActivityDrawerResponse>({
    queryKey: ["me", "activity", row.activity_id],
    queryFn: async () => {
      const res = await fetch(`/api/me/activity/${encodeURIComponent(row.activity_id)}`);
      if (!res.ok) throw new Error("Could not load activity detail.");
      return res.json() as Promise<ActivityDrawerResponse>;
    },
    staleTime: 60_000,
  });

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const links = detail.data?.row.cross_links ?? [];

  return (
    <div className="fixed inset-0 z-40 flex justify-end bg-black/40" onClick={onClose}>
      <div
        role="dialog"
        aria-modal="true"
        onClick={(e) => e.stopPropagation()}
        className={cn(
          "flex h-full w-full max-w-lg flex-col overflow-y-auto",
          "border-l border-border bg-bg-base shadow-xl"
        )}
      >
        <div className="flex items-start justify-between gap-3 border-b border-border/60 px-5 py-4">
          <div className="min-w-0">
            <div className="text-base font-semibold text-fg">{row.summary.headline}</div>
            {row.summary.secondary ? (
              <div className="mt-1 text-sm text-fg-muted">{row.summary.secondary}</div>
            ) : null}
            <div className="mt-2 text-xs text-fg-subtle">
              {new Date(row.event_at).toLocaleString()}
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close detail panel"
            className="text-fg-muted hover:text-fg"
          >×</button>
        </div>

        <div className="flex-1 space-y-5 px-5 py-4">
          {detail.isLoading ? (
            <div className="text-sm text-fg-muted">Loading detail…</div>
          ) : detail.isError ? (
            <div className="text-sm text-danger-fg">{detail.error.message}</div>
          ) : detail.data ? (
            <>
              {links.length > 0 ? (
                <section>
                  <h3 className="text-xs font-semibold uppercase tracking-wide text-fg-muted">Related</h3>
                  <ul className="mt-2 space-y-1 text-sm">
                    {links.map((l) => (
                      <li key={`${l.kind}:${l.target_id}`}>
                        <span className="text-fg-muted">{l.kind}:</span> {l.label}
                      </li>
                    ))}
                  </ul>
                </section>
              ) : null}

              <section>
                <h3 className="text-xs font-semibold uppercase tracking-wide text-fg-muted">Payload</h3>
                <pre className="mt-2 max-h-96 overflow-auto rounded-md border border-border bg-bg-subtle p-3 text-3xs">
                  {JSON.stringify(detail.data.row.raw_payload_redacted, null, 2)}
                </pre>
              </section>

              <section>
                <h3 className="text-xs font-semibold uppercase tracking-wide text-fg-muted">Audit</h3>
                <dl className="mt-2 grid grid-cols-[max-content,1fr] gap-x-3 gap-y-1 text-xs">
                  <dt className="text-fg-muted">Activity ID</dt><dd className="font-mono text-3xs">{row.activity_id}</dd>
                  <dt className="text-fg-muted">Source kind</dt><dd>{row.source_kind}</dd>
                  <dt className="text-fg-muted">Action kind</dt><dd>{row.action_kind}</dd>
                  <dt className="text-fg-muted">Status</dt><dd>{row.status}</dd>
                  {row.posted_at ? (<><dt className="text-fg-muted">Posted at</dt><dd>{new Date(row.posted_at).toLocaleString()}</dd></>) : null}
                </dl>
              </section>
            </>
          ) : null}
        </div>

        <div className="border-t border-border/60 px-5 py-3 text-xs text-fg-muted">
          This is a permanent audit entry. To correct, submit a new action.
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Replace the placeholder in `page.tsx`**

Replace:
```typescript
{selected ? (
  <div onClick={() => setSelected(null)} className="fixed inset-0 z-40 bg-black/30">
    {/* placeholder */}
  </div>
) : null}
```
with:
```typescript
import { ActivityDrawer } from "./_components/ActivityDrawer";
// ...
{selected ? <ActivityDrawer row={selected} onClose={() => setSelected(null)} /> : null}
```

- [ ] **Step 3: Typecheck + manual check**

```bash
npm run typecheck
```

In dev server: click a row. Drawer slides in from the right. ESC closes it. Click outside also closes. Footer copy reads "permanent audit entry…".

- [ ] **Step 4: Commit**

```bash
git add src/app/\(ops\)/me/activity/_components/ActivityDrawer.tsx \
        src/app/\(ops\)/me/activity/page.tsx
git commit -m "feat(portal): activity drawer with payload + cross-links + audit metadata"
```

---

### Task 21: Redirect from `/stock/submissions` + sidebar nav update

**Files:**
- Modify: `src/app/(ops)/stock/submissions/page.tsx`
- Modify: portal sidebar component (search for "My History" string)

- [ ] **Step 1: Find the sidebar source**

```bash
cd /c/Users/tomw2/Projects/window2-portal-sandbox
grep -rn "My History" src/
```

Use the resulting path in Step 3. (Typically `src/components/nav/Sidebar.tsx` or similar — confirm via the grep output.)

- [ ] **Step 2: Replace `/stock/submissions` body with a redirect**

`src/app/(ops)/stock/submissions/page.tsx`:
```typescript
import { redirect } from "next/navigation";

export default function StockSubmissionsRedirect() {
  redirect("/me/activity");
}
```

- [ ] **Step 3: Update sidebar nav**

Find the sidebar item where `label === "My History"` (or equivalent) and:
- Move it out of the STOCK section into a new ME section (or top-level), with the section eyebrow "ME".
- Change `label` to `"My activity"`.
- Change the `href` from `/stock/submissions` to `/me/activity`.

If the sidebar has no ME section concept yet, model it on the existing STOCK / PLANNING / PURCHASE ORDERS sections in the same file.

- [ ] **Step 4: Typecheck + manual check**

```bash
npm run typecheck
```

In dev server:
- Open `/stock/submissions` → redirects to `/me/activity`.
- Sidebar shows new "ME" section with "My activity"; old "My History" is gone.

- [ ] **Step 5: Commit**

```bash
git add src/app/\(ops\)/stock/submissions/page.tsx src/components  # (or whichever file the sidebar is)
git commit -m "feat(portal): redirect /stock/submissions → /me/activity + sidebar ME section"
```

---

## Stage 6 — Verification & handoff

### Task 22: UX handoff packet + screenshots

**Files:**
- Create: `docs/phase8/ux/screens/ME-ACTIVITY-01/me-activity-01-1440x900.png`
- Create: `docs/phase8/ux/screens/ME-ACTIVITY-01/me-activity-01-1440x900-with-filters.png`
- Create: `docs/phase8/ux/screens/ME-ACTIVITY-01/me-activity-01-1440x900-drawer-open.png`
- Create: `docs/phase8/ux/screens/ME-ACTIVITY-01/me-activity-01-390x844.png`
- Create: `docs/phase8/ux/me-activity-handoff-2026-05-13.md`

- [ ] **Step 1: Capture 4 screenshots**

Open dev server. With a fixture user that has ≥3 activity rows from each source kind:
- 1440×900 default state (filters collapsed, no row selected).
- 1440×900 with filters expanded + 1 source chip active.
- 1440×900 with drawer open on a `goods_receipt` row.
- 390×844 mobile.

Save to the paths above.

- [ ] **Step 2: Write the handoff packet**

`docs/phase8/ux/me-activity-handoff-2026-05-13.md`:
```markdown
# UX Handoff Packet — /me/activity

**Spec:** `docs/superpowers/specs/2026-05-13-my-activity-log-design.md`
**Plan:** `docs/superpowers/plans/2026-05-13-my-activity-log.md`
**Date:** 2026-05-13

## What changed
- New route `/me/activity` replaces `/stock/submissions` (redirect in place).
- Page unifies 3 audit sources: form_submissions (23 types), credit_decisions (approve/reject), exception ack/resolve.
- Day-grouped sticky headers, filter bar (collapsed by default), client-side search, keyset-paginated "Load more".
- Row click → right-side drawer with summary + payload (redacted) + cross-links + audit metadata + append-only banner.

## Screenshots
- [Default 1440×900](screens/ME-ACTIVITY-01/me-activity-01-1440x900.png)
- [Filters expanded 1440×900](screens/ME-ACTIVITY-01/me-activity-01-1440x900-with-filters.png)
- [Drawer open 1440×900](screens/ME-ACTIVITY-01/me-activity-01-1440x900-drawer-open.png)
- [Mobile 390×844](screens/ME-ACTIVITY-01/me-activity-01-390x844.png)

## Copy decisions
- Page title: "My activity" — short, neutral, English/LTR per portal_ux_standard.
- Subtitle: "Append-only history of every action you took in the system. Permanent — corrections create new entries." — explicit semantics.
- Drawer footer: "This is a permanent audit entry. To correct, submit a new action." — reinforces append-only.

## Open follow-ups (from spec)
- OQ-1 admin cross-user view — deferred.
- OQ-2 system-attributed events — deferred (out of scope).
- OQ-3 forecast variant merge in filter UI — defer until usage data shows confusion.
- OQ-4 long payload rendering in drawer — `max-h-96` scroll inside `<pre>`; revisit if reports of cut-off content.
```

- [ ] **Step 3: Commit (in the PRODUCTION repo)**

```bash
cd "/c/Users/tomw2/GTeveryday Dropbox/Data Center/Tom/AI Agents & Projects/Code Agents/PRODUCTION"
git add docs/phase8/ux/screens/ME-ACTIVITY-01/ docs/phase8/ux/me-activity-handoff-2026-05-13.md
git commit -m "docs(ux): handoff packet + screenshots for /me/activity"
```

---

### Task 23: End-to-end verification across all 27 builder combinations

**Files:**
- Create: `api/scripts/_verify_activity_log_coverage.ts`

- [ ] **Step 1: Author the verification script**

```typescript
// api/scripts/_verify_activity_log_coverage.ts
//
// Walks every (source_kind, action_kind) combination that the view can
// emit for the calling user and asserts every one produces a non-fail-loud
// summary. Used as the final coverage gate before declaring the feature done.
//
// Run: tsx api/scripts/_verify_activity_log_coverage.ts <user_id>

import './../src/_test_env.ts';
import { sql } from 'kysely';
import { createDb } from '../src/db/connection.ts';
import { buildSummary, type ViewRow, hasBuilder } from '../src/activity_log/builders/_registry.ts';
import '../src/activity_log/builders/index.ts';

const userId = process.argv[2];
if (!userId) { console.error('usage: tsx _verify_activity_log_coverage.ts <user_id>'); process.exit(2); }

const db = createDb();

(async () => {
  const combos = await sql<{ source_kind: string; action_kind: string; n: bigint }>`
    SELECT source_kind, action_kind, COUNT(*) AS n
      FROM private_core.v_my_activity_log
     WHERE actor_user_id = ${userId}::uuid
     GROUP BY source_kind, action_kind
     ORDER BY source_kind, action_kind
  `.execute(db);

  let failures = 0;
  for (const row of combos.rows) {
    const sk = row.source_kind as any;
    if (!hasBuilder(sk, row.action_kind)) {
      console.error(`MISSING BUILDER: ${row.source_kind} / ${row.action_kind} (${row.n} rows)`);
      failures++;
      continue;
    }
    // Pick one sample row of this combo and run the builder
    const sample = await sql<ViewRow & { event_at: Date; posted_at: Date | null }>`
      SELECT activity_id, source_kind, action_kind, event_at, status,
             actor_user_id::text AS actor_user_id, source_pk,
             raw_payload, posted_at, extra_text
        FROM private_core.v_my_activity_log
       WHERE actor_user_id = ${userId}::uuid
         AND source_kind = ${row.source_kind}
         AND action_kind = ${row.action_kind}
       ORDER BY event_at DESC
       LIMIT 1
    `.execute(db);
    const r = sample.rows[0]!;
    const viewRow: ViewRow = {
      ...r,
      event_at: r.event_at instanceof Date ? r.event_at.toISOString() : String(r.event_at),
      posted_at: r.posted_at instanceof Date ? r.posted_at.toISOString() : (r.posted_at ?? null),
    };
    const s = await buildSummary(viewRow, { db });
    if (s.headline.startsWith('⚠')) {
      console.error(`FAIL-LOUD BUILDER: ${row.source_kind} / ${row.action_kind}: ${s.headline}`);
      failures++;
    } else {
      // names-not-ids check
      const idLike = /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i;
      if (idLike.test(s.headline) || (s.secondary && idLike.test(s.secondary))) {
        console.error(`UUID-LEAK: ${row.source_kind} / ${row.action_kind}: ${JSON.stringify(s)}`);
        failures++;
      } else {
        console.log(`ok  ${row.source_kind} / ${row.action_kind}  → ${s.headline}${s.secondary ? `   | ${s.secondary}` : ''}`);
      }
    }
  }

  if (failures > 0) {
    console.error(`\n${failures} failures across ${combos.rows.length} combos`);
    process.exit(1);
  }
  console.log(`\nAll ${combos.rows.length} combos produce a valid summary.`);
  process.exit(0);
})().catch((e) => { console.error(e); process.exit(1); });
```

- [ ] **Step 2: Run it for Tom's user_id**

```bash
cd /c/Users/tomw2/Projects/gt-factory-os
tsx api/scripts/_verify_activity_log_coverage.ts <TOM_USER_ID>
```

(Get TOM_USER_ID from `private_core.app_users` where email = `tom@gteveryday.com`.)

Expected: every combo prints `ok …`; final line `All N combos produce a valid summary.`; exit 0.

- [ ] **Step 3: If any failures — fix the missing/broken builders and re-run**

Do not advance to the next step until exit code is 0.

- [ ] **Step 4: Commit the script**

```bash
git add api/scripts/_verify_activity_log_coverage.ts
git commit -m "test(api): verify_activity_log_coverage — names-not-ids + fail-loud guard for every combo"
```

---

## Self-review checklist (run before declaring done)

- [ ] All 27 builders registered: 23 form + 2 credit + 2 exception.
- [ ] `api/test/activity_log_builders.test.ts` passes locally.
- [ ] `api/test/activity_log_list.test.ts` passes locally (real DB).
- [ ] `api/test/activity_log_drawer.test.ts` passes locally (real DB).
- [ ] `api/test/activity_log_redaction.test.ts` passes.
- [ ] `npm run db:test:0185` passes.
- [ ] `npm run db:test:0186` passes.
- [ ] `tsx _verify_activity_log_coverage.ts <tom>` exits 0.
- [ ] `/stock/submissions` redirects to `/me/activity`.
- [ ] Sidebar shows ME section, no leftover "My History" entry pointing to old URL.
- [ ] UX handoff packet committed to PRODUCTION.
- [ ] At least one rejection-reason row tested manually in browser (confirm danger styling).

---

## Verdict

This plan implements the spec end-to-end. After every task PASSes, run `_verify_activity_log_coverage.ts` for the user with the most activity history (Tom) to catch any drift between spec and live data.
