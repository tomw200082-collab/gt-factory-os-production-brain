# GI Credit Draft on Approve — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** When a planner/admin approves a `lionwheel_credit_needed` exception in the Factory OS inbox, the system automatically creates a credit-note draft in Green Invoice (Morning) — pre-filled with the original invoice's customer, the variance lines at the original prices, and a link to the original invoice — for Tom/Dorin to review and issue manually in the Morning UI. The system never issues the credit; it only creates the draft.

**Architecture:**
1. Approve handler enhanced — after the existing `credit_decisions` insert (state `pending_gi_action`), it now calls a new `greeninvoice/credit_draft_creator` module.
2. The creator searches Morning for the original invoice by Shopify order id (matching against `remarks`), fetches the full document for client.id + income lines + prices, builds a type-330 payload with `signed: false` and `linkedDocumentIds: [original.id]`, POSTs to `/documents`, and persists the returned `id` + `url` to a new `private_core.gi_credit_drafts` audit table.
3. The decision state transitions `pending_gi_action → gi_draft_created`. The inbox card flips to "טיוטה נוצרה ב-GI" with a link to the GI document.
4. On failure (Morning unreachable, original not found, type-320 not yet supported, ambiguous match) — decision stays at `pending_gi_action`, an explicit error is surfaced, and Tom handles in GI manually exactly as today.

**Tech Stack:** Node.js 22 + Fastify (api/), Kysely + Postgres (db/), `node-fetch` native, TypeScript strict, Zod schemas, Vitest. Reuses existing Morning JWT auth pattern from `scripts/green_invoice_connectivity_probe.ts`. Reuses existing `private_core.credit_decisions` table.

**Critical assumption to verify before Task 2:** Morning's POST `/documents` with `signed: false` creates a non-final document visible in the GI UI under "טיוטות". This is verified by **Task 1**. If Task 1 shows `signed: false` produces a final unsigned invoice (not a draft), the plan switches to fallback architecture documented inline in Task 1.

---

## File Structure

### New files
- `api/src/integrations/greeninvoice/client.ts` — typed Morning API client (auth, search, fetch document, post document).
- `api/src/integrations/greeninvoice/credit_draft_creator.ts` — pure orchestration: given exception → returns built payload → POSTs → returns result. Has tests against fixtures.
- `api/src/integrations/greeninvoice/types.ts` — Morning API request/response Zod schemas.
- `api/src/integrations/greeninvoice/__tests__/credit_draft_creator.test.ts` — unit tests with mocked client.
- `db/migrations/0181_gi_credit_drafts.sql` — audit table for every draft creation attempt + columns on `credit_decisions`.
- `db/migrations/0182_credit_decisions_state_gi_draft_created.sql` — admit new state value.
- `scripts/green_invoice_signed_false_verify.ts` — Task 1 verification probe (test POST + immediate fetch + cancel).
- `scripts/green_invoice_cancel_document.ts` — companion utility to cancel a single document by id (used in Task 1 cleanup).

### Modified files
- `api/src/inbox/credit_decisions/handler.ts` — after `INSERT credit_decisions` + `UPDATE exceptions`, call `credit_draft_creator`. On success, UPDATE the decision row with `gi_draft_document_id`, `gi_draft_url`, state `gi_draft_created`; UPDATE the exception status `resolved`. On failure, the decision stays at `pending_gi_action` and an error row is written to `gi_credit_drafts.attempts`. Wrap in transaction; the existing approve invariant (no GI call) is replaced.
- `api/src/inbox/credit_decisions/schemas.ts` — extend `ApproveSuccessResponse` with optional `gi_draft_document_id`, `gi_draft_url`, `gi_draft_status`. Keep backward compat for clients that haven't been updated.
- `api/test/credit_decisions_handlers.test.ts` — add integration test cases for the new GI-draft path (mock the client). Existing tests must still pass without modification of behavior expectations beyond response payload additions.
- `gt-factory-os-portal` (window2-portal-sandbox) inbox card — display the new `gi_draft_document_id`/`gi_draft_url` if present. **Out of scope for this plan** — separate handoff packet because portal authoring is gated by UX handoff per CLAUDE.md. The API contract is delivered here; portal wiring follows.

### Removed files
None.

---

## Task 1: Verify `signed: false` behavior in Morning (BLOCKING)

**Why first:** the entire architecture rests on the assumption that POST /documents with `signed: false` creates a non-final / draft document. If Morning instead creates a fully-issued unsigned credit (with sequential number, possibly emailed), the architecture changes — we'd need to switch to "preview-only via `/documents/preview` + manual create in GI" mode. Verify cheaply now, not after writing 800 lines of handler code.

**Files:**
- Create: `scripts/green_invoice_signed_false_verify.ts`
- Create: `scripts/green_invoice_cancel_document.ts`
- Test target: existing real PROD Morning invoice for order #GT12839 (`e2b5abbf-74fa-4a9d-b626-310d1cdecf9e`, customer מנדרין מרכז הכרמל)

- [ ] **Step 1: Write the verification script**

Create `scripts/green_invoice_signed_false_verify.ts` that:
1. Authenticates against Morning.
2. POSTs `/documents` with `type:330, signed:false, attachment:false, linkedDocumentIds:[<original>]`, single low-quantity line (qty=1) at the original price, currency ILS, vatType 0, `description: "TEST — verify signed:false — DELETE ME"`.
3. Immediately GETs the created document and logs: `signed`, `status`, `number`, `url.he`.
4. Pauses 5 seconds, then GETs again to detect any auto-finalization.
5. Prints exact created `id` so cleanup script can target it.
6. Does NOT cancel. Cancel is a separate explicit step.

```typescript
// scripts/green_invoice_signed_false_verify.ts
import 'dotenv/config';

const rawBase = process.env.GREENINVOICE_API_BASE_URL!;
const keyId = process.env.GREENINVOICE_KEY_ID!;
const secret = process.env.GREENINVOICE_SECRET!;
const ORIGINAL_ID = 'e2b5abbf-74fa-4a9d-b626-310d1cdecf9e'; // GT12839 invoice
const CLIENT_ID = 'fa9fffb3-da38-45db-86ef-023f05e82e71';
const CATALOG = '0762497394207'; // Muza Apple Zest Cocktail 1000ml — matches the variance card

const apiBase = (rawBase.replace(/\/+$/, '').replace(/\/v\d+$/, '') + '/v1/');

async function token(): Promise<string> {
  const r = await fetch(apiBase + 'account/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id: keyId, secret }),
  });
  const j = await r.json() as { token?: string };
  if (!j.token) throw new Error('auth failed');
  return j.token;
}

(async () => {
  const t = await token();
  const today = new Date().toISOString().slice(0, 10);
  const body = {
    type: 330,
    date: today,
    lang: 'he',
    currency: 'ILS',
    vatType: 0,
    description: 'TEST — verify signed:false — DELETE ME',
    remarks: 'verification probe; will be cancelled',
    client: { id: CLIENT_ID },
    income: [{
      catalogNum: CATALOG,
      description: 'Muza Apple Zest Cocktail 1000ml',
      quantity: 1,
      price: 80,
      currency: 'ILS',
      currencyRate: 1,
      vatType: 0,
    }],
    linkedDocumentIds: [ORIGINAL_ID],
    signed: false,
    attachment: false,
  };
  console.log('POST', apiBase + 'documents');
  console.log('BODY', JSON.stringify(body, null, 2));
  const post = await fetch(apiBase + 'documents', {
    method: 'POST',
    headers: { Authorization: `Bearer ${t}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const created = await post.json();
  console.log('CREATED', JSON.stringify(created, null, 2));
  const id = (created as { id?: string }).id;
  if (!id) {
    console.error('NO ID RETURNED — POST failed');
    process.exit(1);
  }
  const fetched = await fetch(apiBase + 'documents/' + id, {
    headers: { Authorization: `Bearer ${t}` },
  });
  const full = await fetched.json();
  console.log('IMMEDIATE_FETCH', JSON.stringify({
    id: (full as any).id,
    type: (full as any).type,
    number: (full as any).number,
    signed: (full as any).signed,
    status: (full as any).status,
    cancellable: (full as any).cancellable,
  }, null, 2));
  await new Promise((r) => setTimeout(r, 5000));
  const fetched2 = await fetch(apiBase + 'documents/' + id, {
    headers: { Authorization: `Bearer ${t}` },
  });
  const full2 = await fetched2.json();
  console.log('POST_5S_FETCH', JSON.stringify({
    signed: (full2 as any).signed,
    status: (full2 as any).status,
  }, null, 2));
  console.log('=== DOCUMENT TO CANCEL:', id, '===');
})();
```

- [ ] **Step 2: Run the verification script**

```bash
cd "C:/Users/tomw2/Projects/gt-factory-os"
npx tsx scripts/green_invoice_signed_false_verify.ts
```

Expected outputs to capture:
- `signed` field in the created document
- `status` value (0=פתוח, 1=סגור, 3=מבטל, 4=שבוטל)
- Whether a sequential `number` was assigned
- Whether the document appears in GI UI under "טיוטות" vs "חשבוניות זיכוי"

- [ ] **Step 3: Manually inspect the result in GI UI**

Open https://app.greeninvoice.co.il/ and check:
1. Does the new document appear under "טיוטות" tab?
2. Does it appear under "חשבוניות זיכוי"?
3. Was an email sent to the customer (check customer "נשלח אימייל" indicator)?
4. Can it be edited from the UI?

Document findings in `docs/integrations/green_invoice_credit_draft_signed_false_verification.md`.

- [ ] **Step 4: Write the cancel script**

Create `scripts/green_invoice_cancel_document.ts`:

```typescript
import 'dotenv/config';
const rawBase = process.env.GREENINVOICE_API_BASE_URL!;
const keyId = process.env.GREENINVOICE_KEY_ID!;
const secret = process.env.GREENINVOICE_SECRET!;
const targetId = process.argv[2];
if (!targetId) { console.error('usage: tsx green_invoice_cancel_document.ts <doc-id>'); process.exit(2); }
const apiBase = (rawBase.replace(/\/+$/, '').replace(/\/v\d+$/, '') + '/v1/');

(async () => {
  const r = await fetch(apiBase + 'account/token', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id: keyId, secret }),
  });
  const { token } = await r.json() as { token: string };
  // Morning's "cancel" mechanism: POST /documents/{id}/cancel  (or equivalent — verify with statuses)
  const cancel = await fetch(apiBase + 'documents/' + targetId + '/cancel', {
    method: 'POST', headers: { Authorization: `Bearer ${token}` },
  });
  console.log('cancel status', cancel.status, await cancel.text());
})();
```

- [ ] **Step 5: Cancel the test document**

```bash
npx tsx scripts/green_invoice_cancel_document.ts <doc-id-from-step-2>
```

Verify in GI UI that the document is now status "מבוטל".

- [ ] **Step 6: Record decision in handoff doc**

Write to `docs/integrations/green_invoice_credit_draft_signed_false_verification.md`:
- The exact request payload sent
- The exact response received
- The `signed`/`status`/`number` observed
- Where it appeared in GI UI (טיוטות vs other)
- Whether an email was triggered
- **The architectural decision:** if `signed:false` IS a draft → proceed with plan as-written. If it's an issued unsigned invoice → switch to the fallback (Task 1B).

- [ ] **Step 7: Commit verification artifacts**

```bash
git add scripts/green_invoice_signed_false_verify.ts scripts/green_invoice_cancel_document.ts
git add docs/integrations/green_invoice_credit_draft_signed_false_verification.md
git commit -m "verify: Morning POST /documents signed:false behavior"
```

### Task 1B (fallback, only if Task 1 shows `signed:false` issues a real invoice):

If `signed:false` does NOT produce a draft, the plan changes:
- The "draft" lives entirely in `private_core.gi_credit_drafts` in Factory OS.
- The inbox card shows the prepared payload + a PDF preview obtained from `POST /documents/preview` (read-only).
- A second explicit "Issue in GI" button performs the actual POST `/documents` with `signed:true` — this remains a Tom-controlled action, NOT auto-fired on approve.
- All subsequent tasks (2–6) adapt: handler does NOT call POST `/documents`; it only stores the prepared payload and renders a preview.

Choose path based on Task 1 evidence before starting Task 2.

---

## Task 2: DB migration — `gi_credit_drafts` table + decision columns

**Files:**
- Create: `db/migrations/0181_gi_credit_drafts.sql`
- Create: `db/migrations/0182_credit_decisions_state_gi_draft_created.sql`
- Test: `api/test/db/migrations/0181_smoke.test.ts`

- [ ] **Step 1: Write the gi_credit_drafts migration**

```sql
-- db/migrations/0181_gi_credit_drafts.sql
-- Author: subagent-driven-development for plan 2026-05-12-gi-credit-draft-on-approve
-- Purpose: audit every Morning credit-draft creation attempt, store the
--          resulting GI document id/url, and link back to the credit_decisions
--          row that triggered it.
--
-- Authority: docs/superpowers/plans/2026-05-12-gi-credit-draft-on-approve.md §Task 2

BEGIN;

CREATE TABLE IF NOT EXISTS private_core.gi_credit_drafts (
  draft_id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
  decision_id           uuid        NOT NULL REFERENCES private_core.credit_decisions(decision_id),
  exception_id          uuid        NOT NULL,
  wp_order_id           text        NOT NULL,
  -- Original Morning invoice we credited from.
  original_document_id  text        NULL,
  original_document_type integer    NULL,   -- 305 or 320
  original_document_number text     NULL,
  -- Snapshot of variance line(s) used.
  variance_lines        jsonb       NOT NULL,
  client_id             text        NULL,
  client_name           text        NULL,
  -- POST result (NULL if creation failed).
  gi_draft_document_id  text        NULL,
  gi_draft_url          text        NULL,
  gi_response           jsonb       NULL,
  -- Lifecycle.
  state                 text        NOT NULL DEFAULT 'pending'
                                    CHECK (state IN ('pending','succeeded','failed','search_no_match','search_ambiguous','original_type_unsupported','client_resolution_failed')),
  failure_reason        text        NULL,
  attempts              integer     NOT NULL DEFAULT 0,
  created_at            timestamptz NOT NULL DEFAULT now(),
  updated_at            timestamptz NOT NULL DEFAULT now(),
  succeeded_at          timestamptz NULL
);

CREATE INDEX IF NOT EXISTS idx_gi_credit_drafts_decision
  ON private_core.gi_credit_drafts (decision_id);
CREATE INDEX IF NOT EXISTS idx_gi_credit_drafts_exception
  ON private_core.gi_credit_drafts (exception_id);
CREATE INDEX IF NOT EXISTS idx_gi_credit_drafts_state
  ON private_core.gi_credit_drafts (state)
  WHERE state <> 'succeeded';

-- One pending+succeeded row per decision is enough; failures may accumulate
-- as separate rows for audit, but only the latest is meaningful.
CREATE UNIQUE INDEX IF NOT EXISTS uq_gi_credit_drafts_decision_alive
  ON private_core.gi_credit_drafts (decision_id)
  WHERE state IN ('pending','succeeded');

-- Convenience columns directly on credit_decisions for fast UI reads. Backfilled
-- by the handler; never touched by anything else.
ALTER TABLE private_core.credit_decisions
  ADD COLUMN IF NOT EXISTS gi_draft_document_id text NULL,
  ADD COLUMN IF NOT EXISTS gi_draft_url         text NULL,
  ADD COLUMN IF NOT EXISTS gi_draft_attempts    integer NOT NULL DEFAULT 0;

COMMIT;
```

- [ ] **Step 2: Write the state-admittance migration**

```sql
-- db/migrations/0182_credit_decisions_state_gi_draft_created.sql
-- Admit new state value 'gi_draft_created' on credit_decisions.state, which
-- previously accepted only ('pending_gi_action','cancelled').
--
-- Authority: docs/superpowers/plans/2026-05-12-gi-credit-draft-on-approve.md §Task 2

BEGIN;

-- credit_decisions.state was free-text per migration 0122 with no CHECK; if a
-- CHECK has since been added in 0124 or later, replace it. Otherwise the
-- block below is a no-op.
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.check_constraints
    WHERE constraint_schema = 'private_core'
      AND check_clause LIKE '%credit_decisions%state%'
  ) THEN
    EXECUTE 'ALTER TABLE private_core.credit_decisions DROP CONSTRAINT IF EXISTS credit_decisions_state_check';
  END IF;
END $$;

ALTER TABLE private_core.credit_decisions
  ADD CONSTRAINT credit_decisions_state_check
  CHECK (state IN ('pending_gi_action','gi_draft_created','gi_draft_failed','cancelled'));

COMMIT;
```

- [ ] **Step 3: Apply migrations against local DB**

```bash
cd "C:/Users/tomw2/Projects/gt-factory-os"
node scripts/apply_migration.mjs db/migrations/0181_gi_credit_drafts.sql
node scripts/apply_migration.mjs db/migrations/0182_credit_decisions_state_gi_draft_created.sql
```

Expected: both report `applied=1`. Verify with:

```bash
psql "$DATABASE_URL" -c "\d private_core.gi_credit_drafts"
psql "$DATABASE_URL" -c "\d private_core.credit_decisions"
```

- [ ] **Step 4: Write smoke test**

```typescript
// api/test/db/migrations/0181_smoke.test.ts
import { describe, it, expect, beforeAll } from 'vitest';
import { sql } from 'kysely';
import { getDb } from '../../../src/db/connection.js';

describe('migration 0181 gi_credit_drafts', () => {
  const db = getDb();

  it('table exists with expected columns', async () => {
    const res = await sql<{ column_name: string }>`
      SELECT column_name FROM information_schema.columns
      WHERE table_schema = 'private_core' AND table_name = 'gi_credit_drafts'
    `.execute(db);
    const cols = res.rows.map((r) => r.column_name).sort();
    expect(cols).toContain('draft_id');
    expect(cols).toContain('decision_id');
    expect(cols).toContain('gi_draft_document_id');
    expect(cols).toContain('variance_lines');
    expect(cols).toContain('state');
  });

  it('credit_decisions has new gi_draft_* columns', async () => {
    const res = await sql<{ column_name: string }>`
      SELECT column_name FROM information_schema.columns
      WHERE table_schema = 'private_core' AND table_name = 'credit_decisions'
        AND column_name IN ('gi_draft_document_id','gi_draft_url','gi_draft_attempts')
    `.execute(db);
    expect(res.rows.length).toBe(3);
  });

  it('state check admits gi_draft_created', async () => {
    // Insert a dummy decision and try the new state.
    const id = await sql<{ exception_id: string }>`
      SELECT exception_id::text FROM private_core.exceptions LIMIT 1
    `.execute(db);
    if (id.rows.length === 0) return; // empty DB, skip
    const probe = sql`
      INSERT INTO private_core.credit_decisions
        (exception_id, decided_by_user_id, decision, idempotency_key, state)
      VALUES (${id.rows[0].exception_id}::uuid,
              gen_random_uuid(),
              'approve',
              'smoke-' || gen_random_uuid()::text,
              'gi_draft_created')
      RETURNING decision_id
    `.execute(db);
    await expect(probe).resolves.toBeDefined();
  });
});
```

- [ ] **Step 5: Run smoke test**

```bash
cd "C:/Users/tomw2/Projects/gt-factory-os"
npx vitest run api/test/db/migrations/0181_smoke.test.ts
```

Expected: 3/3 PASS.

- [ ] **Step 6: Commit**

```bash
git add db/migrations/0181_gi_credit_drafts.sql db/migrations/0182_credit_decisions_state_gi_draft_created.sql
git add api/test/db/migrations/0181_smoke.test.ts
git commit -m "feat(db): gi_credit_drafts audit table + gi_draft_created state"
```

---

## Task 3: Morning API client module

**Files:**
- Create: `api/src/integrations/greeninvoice/types.ts`
- Create: `api/src/integrations/greeninvoice/client.ts`
- Test: `api/src/integrations/greeninvoice/__tests__/client.test.ts`

- [ ] **Step 1: Write the Zod types**

```typescript
// api/src/integrations/greeninvoice/types.ts
import { z } from 'zod';

export const IncomeLine = z.object({
  catalogNum: z.string().optional(),
  description: z.string().optional(),
  quantity: z.number(),
  price: z.number(),
  currency: z.string().default('ILS'),
  currencyRate: z.number().default(1),
  vatType: z.number().default(0),
});
export type IncomeLine = z.infer<typeof IncomeLine>;

export const Doc = z.object({
  id: z.string(),
  type: z.number(),
  number: z.union([z.string(), z.number()]).optional(),
  documentDate: z.string().optional(),
  remarks: z.string().optional().nullable(),
  description: z.string().optional().nullable(),
  signed: z.boolean().optional(),
  status: z.number().optional(),
  currency: z.string().optional(),
  client: z.object({
    id: z.string().optional(),
    name: z.string().optional(),
    taxId: z.string().optional(),
  }).optional(),
  income: z.array(IncomeLine).optional(),
  url: z.object({
    he: z.string().optional(),
    en: z.string().optional(),
    origin: z.string().optional(),
  }).optional(),
});
export type Doc = z.infer<typeof Doc>;

export const SearchResponse = z.object({
  total: z.number().optional(),
  items: z.array(Doc).optional(),
});

export const CreateDocBody = z.object({
  type: z.number(),
  date: z.string(),
  lang: z.string().default('he'),
  currency: z.string().default('ILS'),
  vatType: z.number().default(0),
  description: z.string().optional(),
  remarks: z.string().optional(),
  client: z.object({ id: z.string() }),
  income: z.array(IncomeLine),
  linkedDocumentIds: z.array(z.string()).optional(),
  signed: z.boolean().optional(),
  attachment: z.boolean().optional(),
});
export type CreateDocBody = z.infer<typeof CreateDocBody>;

export const CreateDocResponse = z.object({
  id: z.string(),
  number: z.union([z.string(), z.number()]).optional(),
  signed: z.boolean().optional(),
  url: z.object({
    he: z.string().optional(),
    en: z.string().optional(),
    origin: z.string().optional(),
  }).optional(),
});
export type CreateDocResponse = z.infer<typeof CreateDocResponse>;
```

- [ ] **Step 2: Write the client**

```typescript
// api/src/integrations/greeninvoice/client.ts
import { Doc, SearchResponse, CreateDocBody, CreateDocResponse } from './types.js';
import type { CreateDocBody as CreateDocBodyType, CreateDocResponse as CreateDocResponseType, Doc as DocType } from './types.js';

export interface GreenInvoiceClient {
  searchByRemarks(needle: string, fromDate: string, type?: number[]): Promise<DocType[]>;
  getDocument(id: string): Promise<DocType>;
  createDocument(body: CreateDocBodyType): Promise<CreateDocResponseType>;
}

interface Config {
  apiBaseUrl: string;
  keyId: string;
  secret: string;
}

export function createGreenInvoiceClient(cfg: Config): GreenInvoiceClient {
  const apiBase = (cfg.apiBaseUrl.replace(/\/+$/, '').replace(/\/v\d+$/, '') + '/v1/');
  let cachedToken: { value: string; expires: number } | null = null;

  async function getToken(): Promise<string> {
    const now = Date.now();
    if (cachedToken && cachedToken.expires > now + 60_000) return cachedToken.value;
    const r = await fetch(apiBase + 'account/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: cfg.keyId, secret: cfg.secret }),
    });
    if (!r.ok) throw new Error(`Morning auth failed status=${r.status}`);
    const j = await r.json() as { token: string; expires?: number };
    cachedToken = { value: j.token, expires: (j.expires ?? (now / 1000 + 1800)) * 1000 };
    return j.token;
  }

  async function auth(): Promise<HeadersInit> {
    return { Authorization: `Bearer ${await getToken()}` };
  }

  return {
    async searchByRemarks(needle, fromDate, type = [305, 320]) {
      const r = await fetch(apiBase + 'documents/search', {
        method: 'POST',
        headers: { ...(await auth()), 'Content-Type': 'application/json' },
        body: JSON.stringify({ page: 1, pageSize: 200, type, fromDate, sort: 'documentDate' }),
      });
      if (!r.ok) throw new Error(`Morning search failed status=${r.status}`);
      const j = SearchResponse.parse(await r.json());
      const items = j.items ?? [];
      return items.filter((d) => (d.remarks ?? '').includes(needle));
    },
    async getDocument(id) {
      const r = await fetch(apiBase + 'documents/' + encodeURIComponent(id), {
        headers: await auth(),
      });
      if (!r.ok) throw new Error(`Morning getDocument failed id=${id} status=${r.status}`);
      return Doc.parse(await r.json());
    },
    async createDocument(body) {
      const validated = CreateDocBody.parse(body);
      const r = await fetch(apiBase + 'documents', {
        method: 'POST',
        headers: { ...(await auth()), 'Content-Type': 'application/json' },
        body: JSON.stringify(validated),
      });
      const text = await r.text();
      if (!r.ok) throw new Error(`Morning createDocument failed status=${r.status} body=${text.slice(0, 500)}`);
      return CreateDocResponse.parse(JSON.parse(text));
    },
  };
}
```

- [ ] **Step 3: Write client tests with mocked fetch**

```typescript
// api/src/integrations/greeninvoice/__tests__/client.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { createGreenInvoiceClient } from '../client.js';

describe('GreenInvoiceClient', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('searchByRemarks filters by remarks substring after API call', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch' as any).mockImplementation(async (url: any) => {
      const u = String(url);
      if (u.endsWith('/account/token')) {
        return new Response(JSON.stringify({ token: 'TOK', expires: Date.now() / 1000 + 1800 }), { status: 200 });
      }
      if (u.endsWith('/documents/search')) {
        return new Response(JSON.stringify({
          items: [
            { id: 'a', type: 305, remarks: 'מספר הזמנה באתר: #GT12839' },
            { id: 'b', type: 305, remarks: 'מספר הזמנה באתר: #GT99999' },
            { id: 'c', type: 305, remarks: null },
          ],
        }), { status: 200 });
      }
      throw new Error('unexpected url ' + u);
    });
    const client = createGreenInvoiceClient({
      apiBaseUrl: 'https://api.greeninvoice.co.il/api/v1',
      keyId: 'k', secret: 's',
    });
    const hits = await client.searchByRemarks('#GT12839', '2026-05-01');
    expect(hits.map((h) => h.id)).toEqual(['a']);
    fetchSpy.mockRestore();
  });

  it('createDocument rejects malformed body before fetch', async () => {
    const client = createGreenInvoiceClient({
      apiBaseUrl: 'https://api.greeninvoice.co.il/api/v1',
      keyId: 'k', secret: 's',
    });
    await expect(client.createDocument({
      // type missing
      date: '2026-05-12',
      lang: 'he', currency: 'ILS', vatType: 0,
      client: { id: 'c' },
      income: [{ catalogNum: 'X', description: 'd', quantity: 1, price: 10, currency: 'ILS', currencyRate: 1, vatType: 0 }],
    } as any)).rejects.toThrow();
  });

  it('caches token across calls', async () => {
    let tokenCallCount = 0;
    vi.spyOn(globalThis, 'fetch' as any).mockImplementation(async (url: any) => {
      const u = String(url);
      if (u.endsWith('/account/token')) {
        tokenCallCount++;
        return new Response(JSON.stringify({ token: 'TOK', expires: Date.now() / 1000 + 1800 }), { status: 200 });
      }
      return new Response(JSON.stringify({ items: [] }), { status: 200 });
    });
    const client = createGreenInvoiceClient({
      apiBaseUrl: 'https://api.greeninvoice.co.il/api/v1',
      keyId: 'k', secret: 's',
    });
    await client.searchByRemarks('x', '2026-05-01');
    await client.searchByRemarks('y', '2026-05-01');
    expect(tokenCallCount).toBe(1);
  });
});
```

- [ ] **Step 4: Run client tests**

```bash
cd "C:/Users/tomw2/Projects/gt-factory-os"
npx vitest run api/src/integrations/greeninvoice/__tests__/client.test.ts
```

Expected: 3/3 PASS.

- [ ] **Step 5: Commit**

```bash
git add api/src/integrations/greeninvoice/client.ts api/src/integrations/greeninvoice/types.ts
git add api/src/integrations/greeninvoice/__tests__/client.test.ts
git commit -m "feat(gi-client): typed Morning API client (search, fetch, create)"
```

---

## Task 4: Credit-draft creator (pure orchestration)

**Files:**
- Create: `api/src/integrations/greeninvoice/credit_draft_creator.ts`
- Test: `api/src/integrations/greeninvoice/__tests__/credit_draft_creator.test.ts`

- [ ] **Step 1: Write the creator function signature + outcome envelope**

```typescript
// api/src/integrations/greeninvoice/credit_draft_creator.ts
import type { GreenInvoiceClient } from './client.js';

export interface ExceptionDetail {
  item_id: string;
  item_name: string;
  lw_qty_ordered: number;
  lw_qty_picked: number;
  shortage_delta: number;
  wp_order_id: string;
}

export type CreatorOutcome =
  | { kind: 'success'; gi_document_id: string; gi_url: string | null; original_document_id: string; original_document_type: number; original_document_number: string | number | null; variance_lines: unknown[] }
  | { kind: 'search_no_match'; reason: string }
  | { kind: 'search_ambiguous'; reason: string; candidate_ids: string[] }
  | { kind: 'original_type_unsupported'; reason: string; original_type: number; original_id: string }
  | { kind: 'line_not_found_in_original'; reason: string; original_id: string; sku: string }
  | { kind: 'gi_post_failed'; reason: string };

export async function createCreditDraft(
  client: GreenInvoiceClient,
  detail: ExceptionDetail,
  now: () => Date = () => new Date(),
): Promise<CreatorOutcome> {
  // 1. Search Morning for the original invoice.
  const fromDate = new Date(now().getTime() - 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
  const needle = `#${detail.wp_order_id}`;
  const matches = await client.searchByRemarks(needle, fromDate);
  if (matches.length === 0) return { kind: 'search_no_match', reason: `no Morning doc with remarks containing ${needle} in last 30 days` };
  if (matches.length > 1) return { kind: 'search_ambiguous', reason: `${matches.length} candidates`, candidate_ids: matches.map((m) => m.id) };

  const candidate = matches[0];
  if (candidate.type !== 305) {
    // Branch B (320 two-step) not in scope for this plan.
    return { kind: 'original_type_unsupported', reason: `original type ${candidate.type} not supported (only 305)`, original_type: candidate.type, original_id: candidate.id };
  }

  // 2. Fetch full document to get income lines + client.id.
  const full = await client.getDocument(candidate.id);
  if (!full.client?.id) return { kind: 'gi_post_failed', reason: 'original document missing client.id' };
  const targetLine = full.income?.find((l) => l.catalogNum === detail.item_id || l.description === detail.item_name);
  if (!targetLine) {
    return { kind: 'line_not_found_in_original', reason: 'no income line matches the shortage item', original_id: full.id, sku: detail.item_id };
  }

  // 3. Build and POST the credit draft.
  const today = now().toISOString().slice(0, 10);
  try {
    const created = await client.createDocument({
      type: 330,
      date: today,
      lang: 'he',
      currency: 'ILS',
      vatType: 0,
      description: `זיכוי על חוסר במסירה — הזמנה ${detail.wp_order_id}`,
      remarks: `מקור: ${full.remarks ?? ''} | חוסר: ${detail.item_name} × ${detail.shortage_delta}`,
      client: { id: full.client.id },
      income: [{
        catalogNum: targetLine.catalogNum,
        description: targetLine.description,
        quantity: detail.shortage_delta,
        price: targetLine.price,
        currency: 'ILS',
        currencyRate: 1,
        vatType: targetLine.vatType ?? 0,
      }],
      linkedDocumentIds: [full.id],
      signed: false,
      attachment: false,
    });
    return {
      kind: 'success',
      gi_document_id: created.id,
      gi_url: created.url?.he ?? null,
      original_document_id: full.id,
      original_document_type: full.type,
      original_document_number: full.number ?? null,
      variance_lines: [{
        sku: targetLine.catalogNum,
        description: targetLine.description,
        ordered: detail.lw_qty_ordered,
        picked: detail.lw_qty_picked,
        credited: detail.shortage_delta,
        unit_price: targetLine.price,
      }],
    };
  } catch (e) {
    return { kind: 'gi_post_failed', reason: (e as Error).message };
  }
}
```

- [ ] **Step 2: Write creator tests**

```typescript
// api/src/integrations/greeninvoice/__tests__/credit_draft_creator.test.ts
import { describe, it, expect, vi } from 'vitest';
import { createCreditDraft } from '../credit_draft_creator.js';

const fixedNow = () => new Date('2026-05-12T08:00:00Z');

function fakeClient(overrides: Partial<{
  search: any[];
  doc: any;
  postThrows: string | null;
  postReturns: any;
}>) {
  return {
    searchByRemarks: vi.fn(async () => overrides.search ?? []),
    getDocument: vi.fn(async () => overrides.doc),
    createDocument: vi.fn(async () => {
      if (overrides.postThrows) throw new Error(overrides.postThrows);
      return overrides.postReturns ?? { id: 'new-doc-id', url: { he: 'https://gi/url' } };
    }),
  };
}

const baseDetail = {
  item_id: '0762497394207',
  item_name: 'Muza Apple Zest Cocktail 1000ml',
  lw_qty_ordered: 3,
  lw_qty_picked: 1,
  shortage_delta: 2,
  wp_order_id: 'GT12839',
};

describe('createCreditDraft', () => {
  it('search_no_match when zero candidates', async () => {
    const client = fakeClient({ search: [] });
    const r = await createCreditDraft(client as any, baseDetail, fixedNow);
    expect(r.kind).toBe('search_no_match');
  });

  it('search_ambiguous when multiple candidates', async () => {
    const client = fakeClient({ search: [{ id: 'a', type: 305 }, { id: 'b', type: 305 }] });
    const r = await createCreditDraft(client as any, baseDetail, fixedNow);
    expect(r.kind).toBe('search_ambiguous');
  });

  it('original_type_unsupported when candidate is 320', async () => {
    const client = fakeClient({ search: [{ id: 'a', type: 320 }] });
    const r = await createCreditDraft(client as any, baseDetail, fixedNow);
    expect(r.kind).toBe('original_type_unsupported');
  });

  it('line_not_found_in_original when SKU absent', async () => {
    const client = fakeClient({
      search: [{ id: 'a', type: 305 }],
      doc: { id: 'a', type: 305, client: { id: 'c' }, income: [{ catalogNum: 'OTHER', price: 10, quantity: 1 }] },
    });
    const r = await createCreditDraft(client as any, baseDetail, fixedNow);
    expect(r.kind).toBe('line_not_found_in_original');
  });

  it('success — builds correct payload and returns gi_document_id', async () => {
    const client = fakeClient({
      search: [{ id: 'orig-id', type: 305, remarks: '#GT12839' }],
      doc: {
        id: 'orig-id', type: 305, number: 62648,
        remarks: 'מספר הזמנה באתר: #GT12839',
        client: { id: 'mandarin-id', name: 'מנדרין' },
        income: [{ catalogNum: '0762497394207', description: 'Muza Apple Zest', price: 80, quantity: 3, vatType: 0 }],
      },
    });
    const r = await createCreditDraft(client as any, baseDetail, fixedNow);
    expect(r.kind).toBe('success');
    if (r.kind !== 'success') return;
    expect(r.gi_document_id).toBe('new-doc-id');
    expect(client.createDocument).toHaveBeenCalledOnce();
    const body = client.createDocument.mock.calls[0][0] as any;
    expect(body.type).toBe(330);
    expect(body.signed).toBe(false);
    expect(body.client.id).toBe('mandarin-id');
    expect(body.linkedDocumentIds).toEqual(['orig-id']);
    expect(body.income[0].quantity).toBe(2);
    expect(body.income[0].price).toBe(80);
    expect(body.income[0].catalogNum).toBe('0762497394207');
  });

  it('gi_post_failed when createDocument throws', async () => {
    const client = fakeClient({
      search: [{ id: 'orig-id', type: 305 }],
      doc: {
        id: 'orig-id', type: 305,
        client: { id: 'c' },
        income: [{ catalogNum: '0762497394207', description: 'x', price: 80, quantity: 3, vatType: 0 }],
      },
      postThrows: 'Morning createDocument failed status=500',
    });
    const r = await createCreditDraft(client as any, baseDetail, fixedNow);
    expect(r.kind).toBe('gi_post_failed');
  });
});
```

- [ ] **Step 3: Run creator tests**

```bash
cd "C:/Users/tomw2/Projects/gt-factory-os"
npx vitest run api/src/integrations/greeninvoice/__tests__/credit_draft_creator.test.ts
```

Expected: 6/6 PASS.

- [ ] **Step 4: Commit**

```bash
git add api/src/integrations/greeninvoice/credit_draft_creator.ts api/src/integrations/greeninvoice/__tests__/credit_draft_creator.test.ts
git commit -m "feat(gi-credit-draft): pure orchestrator with outcome envelope"
```

---

## Task 5: Wire creator into the approve handler

**Files:**
- Modify: `api/src/inbox/credit_decisions/handler.ts` (replace lines 38-41 invariant + extend the approve handler tail)
- Modify: `api/src/inbox/credit_decisions/schemas.ts` (extend response)
- Modify: `api/test/credit_decisions_handlers.test.ts` (add new cases)
- Create: `api/src/integrations/greeninvoice/persistence.ts` (helper to write the audit row)

- [ ] **Step 1: Write the persistence helper**

```typescript
// api/src/integrations/greeninvoice/persistence.ts
import { sql } from 'kysely';
import type { Db } from '../../db/connection.js';
import type { ExceptionDetail, CreatorOutcome } from './credit_draft_creator.js';

export async function persistDraftAttempt(
  db: Db,
  args: {
    decision_id: string;
    exception_id: string;
    detail: ExceptionDetail;
    outcome: CreatorOutcome;
  },
): Promise<void> {
  const { decision_id, exception_id, detail, outcome } = args;
  const stateMap: Record<CreatorOutcome['kind'], string> = {
    success: 'succeeded',
    search_no_match: 'search_no_match',
    search_ambiguous: 'search_ambiguous',
    original_type_unsupported: 'original_type_unsupported',
    line_not_found_in_original: 'failed',
    gi_post_failed: 'failed',
  };
  const state = stateMap[outcome.kind];
  const isOk = outcome.kind === 'success';

  await sql`
    INSERT INTO private_core.gi_credit_drafts (
      decision_id, exception_id, wp_order_id,
      original_document_id, original_document_type, original_document_number,
      variance_lines, gi_draft_document_id, gi_draft_url,
      gi_response, state, failure_reason, attempts,
      succeeded_at
    ) VALUES (
      ${decision_id}::uuid,
      ${exception_id}::uuid,
      ${detail.wp_order_id}::text,
      ${isOk ? (outcome as any).original_document_id : null}::text,
      ${isOk ? (outcome as any).original_document_type : null}::int,
      ${isOk ? String((outcome as any).original_document_number ?? '') : null}::text,
      ${JSON.stringify(isOk ? (outcome as any).variance_lines : [detail])}::jsonb,
      ${isOk ? (outcome as any).gi_document_id : null}::text,
      ${isOk ? (outcome as any).gi_url : null}::text,
      ${JSON.stringify(outcome)}::jsonb,
      ${state}::text,
      ${'reason' in outcome ? outcome.reason : null}::text,
      1,
      ${isOk ? sql`now()` : sql`NULL`}
    )
  `.execute(db);

  if (isOk) {
    await sql`
      UPDATE private_core.credit_decisions
         SET state = 'gi_draft_created',
             gi_draft_document_id = ${(outcome as any).gi_document_id}::text,
             gi_draft_url = ${(outcome as any).gi_url}::text,
             gi_draft_attempts = gi_draft_attempts + 1
       WHERE decision_id = ${decision_id}::uuid
    `.execute(db);
  } else {
    await sql`
      UPDATE private_core.credit_decisions
         SET gi_draft_attempts = gi_draft_attempts + 1
       WHERE decision_id = ${decision_id}::uuid
    `.execute(db);
  }
}
```

- [ ] **Step 2: Update the approve handler**

In `api/src/inbox/credit_decisions/handler.ts`:

Replace the SC-A3 INVARIANT comment block (lines 38-41) with:

```typescript
// GI CREDIT DRAFT FLOW: after writing credit_decisions + flipping the
// exception to pending_gi_action, the handler attempts to create a draft
// credit-note in Green Invoice via the credit_draft_creator. On success the
// decision state advances to 'gi_draft_created' and the exception is marked
// 'resolved'. On any failure the decision stays at 'pending_gi_action' so
// the operator (Tom/Dorin) handles the credit manually in GI; the failure
// is recorded in gi_credit_drafts for audit. Authority:
// docs/superpowers/plans/2026-05-12-gi-credit-draft-on-approve.md §Task 5.
```

In `handleApproveCredit`, after the existing `INSERT credit_decisions` and `UPDATE exceptions` calls (but still inside the transaction), add the GI call. Replace the existing success return with:

```typescript
    // Fetch the exception detail JSON to extract variance fields.
    const detailRow = await sql<{ detail: any }>`
      SELECT detail::jsonb AS detail FROM private_core.exceptions
       WHERE exception_id = ${exceptionId}::uuid
    `.execute(trx);
    const rawDetail = detailRow.rows[0]?.detail;
    const parsed = typeof rawDetail === 'string' ? JSON.parse(rawDetail) : rawDetail;
    const detail = {
      item_id: String(parsed?.item_id ?? ''),
      item_name: String(parsed?.item_name ?? ''),
      lw_qty_ordered: Number(parsed?.lw_qty_ordered ?? 0),
      lw_qty_picked: Number(parsed?.lw_qty_picked ?? 0),
      shortage_delta: Number(parsed?.shortage_delta ?? 0),
      wp_order_id: String(parsed?.wp_order_id ?? ''),
    };

    // Call Morning. On any error we still complete the decision insert
    // (already done above) and report the failure in the response.
    let gi: Awaited<ReturnType<typeof createCreditDraft>> | null = null;
    try {
      const client = createGreenInvoiceClient({
        apiBaseUrl: process.env.GREENINVOICE_API_BASE_URL!,
        keyId: process.env.GREENINVOICE_KEY_ID!,
        secret: process.env.GREENINVOICE_SECRET!,
      });
      gi = await createCreditDraft(client, detail);
      await persistDraftAttempt(trx as unknown as Db, {
        decision_id: decisionRow.decision_id,
        exception_id: exceptionId,
        detail,
        outcome: gi,
      });
      if (gi.kind === 'success') {
        await sql`
          UPDATE private_core.exceptions
             SET status = 'resolved'::text,
                 resolved_by = ${session.user_id}::uuid,
                 resolved_at = now(),
                 resolution_notes = ${'GI draft ' + gi.gi_document_id}::text,
                 updated_at = now()
           WHERE exception_id = ${exceptionId}::uuid
        `.execute(trx);
      }
    } catch (e) {
      // Persistence or auth failed before we got an outcome.
      await persistDraftAttempt(trx as unknown as Db, {
        decision_id: decisionRow.decision_id,
        exception_id: exceptionId,
        detail,
        outcome: { kind: 'gi_post_failed', reason: (e as Error).message },
      });
      gi = { kind: 'gi_post_failed', reason: (e as Error).message };
    }

    return {
      kind: 'ok',
      status: 201,
      body: {
        exception_id: exceptionId,
        decision_id: decisionRow.decision_id,
        status: gi?.kind === 'success' ? 'gi_draft_created' : 'pending_gi_action',
        decided_at: toIso(decisionRow.decided_at),
        decided_by_user_id: session.user_id,
        decided_by_snapshot: session.display_name,
        idempotent_replay: false,
        gi_draft: gi?.kind === 'success'
          ? { document_id: gi.gi_document_id, url: gi.gi_url, original_number: gi.original_document_number }
          : { error: gi?.kind ?? 'unknown', reason: gi && 'reason' in gi ? gi.reason : 'unknown' },
      },
    };
```

At the top of the file, add imports:

```typescript
import { createGreenInvoiceClient } from '../../integrations/greeninvoice/client.js';
import { createCreditDraft } from '../../integrations/greeninvoice/credit_draft_creator.js';
import { persistDraftAttempt } from '../../integrations/greeninvoice/persistence.js';
```

- [ ] **Step 3: Update response schema**

In `api/src/inbox/credit_decisions/schemas.ts`, extend `ApproveSuccessResponse`:

```typescript
export const ApproveSuccessResponse = z.object({
  exception_id: z.string().uuid(),
  decision_id: z.string().uuid(),
  status: z.enum(['pending_gi_action', 'gi_draft_created']),
  decided_at: z.string(),
  decided_by_user_id: z.string().uuid(),
  decided_by_snapshot: z.string(),
  idempotent_replay: z.boolean(),
  gi_draft: z.union([
    z.object({
      document_id: z.string(),
      url: z.string().nullable(),
      original_number: z.union([z.string(), z.number()]).nullable(),
    }),
    z.object({
      error: z.string(),
      reason: z.string(),
    }),
  ]).optional(),
});
```

- [ ] **Step 4: Add new test cases**

In `api/test/credit_decisions_handlers.test.ts`, add cases:
- approve creates a real DB row + calls mocked GI client + returns `status: 'gi_draft_created'` with `gi_draft.document_id`
- approve when GI returns `search_no_match` keeps decision at `pending_gi_action`, persists row in `gi_credit_drafts` with state `search_no_match`
- approve when GI throws on network keeps decision at `pending_gi_action` and exception NOT moved to resolved

Mock the GI client by `vi.mock('../../src/integrations/greeninvoice/client.js')` returning a fake whose behavior is set per test.

- [ ] **Step 5: Run all credit_decisions tests**

```bash
cd "C:/Users/tomw2/Projects/gt-factory-os"
npx vitest run api/test/credit_decisions_handlers.test.ts
```

Expected: existing tests still PASS + 3 new tests PASS.

- [ ] **Step 6: Run full repo test suite**

```bash
cd "C:/Users/tomw2/Projects/gt-factory-os"
npx vitest run
```

Expected: total test count >= previous baseline; zero failures.

- [ ] **Step 7: Commit**

```bash
git add api/src/inbox/credit_decisions/handler.ts api/src/inbox/credit_decisions/schemas.ts
git add api/src/integrations/greeninvoice/persistence.ts
git add api/test/credit_decisions_handlers.test.ts
git commit -m "feat(approve): create GI credit draft on approve; backward-compatible response"
```

---

## Task 6: End-to-end live verification on PROD with one real exception

**Files:**
- Create: `docs/integrations/green_invoice_credit_draft_e2e_verification_2026-05-12.md`

- [ ] **Step 1: Deploy the new handler to PROD**

(Per CLAUDE.md, deploy is Tom-only. The plan stops at "PR ready for Tom to merge + deploy". Subagents do not push or deploy.)

- [ ] **Step 2: Trigger one real approve on GT12839 (or whichever exception is pending)**

Tom clicks "אשר זיכוי" in the inbox. The response should now include:

```json
{
  "status": "gi_draft_created",
  "gi_draft": {
    "document_id": "...",
    "url": "https://www.greeninvoice.co.il/...",
    "original_number": 62648
  }
}
```

- [ ] **Step 3: Open the URL in Tom's browser**

Verify the draft appears in GI as expected (location depends on Task 1's findings: טיוטות tab or חשבוניות זיכוי tab).

- [ ] **Step 4: Confirm: no email was sent to customer**

Check the customer's row in Morning for "נשלח אימייל" indicator. Confirm zero.

- [ ] **Step 5: Confirm Factory OS state**

```sql
SELECT decision_id, state, gi_draft_document_id, gi_draft_url
  FROM private_core.credit_decisions
 WHERE state = 'gi_draft_created'
 ORDER BY decided_at DESC LIMIT 5;

SELECT draft_id, decision_id, state, failure_reason, succeeded_at
  FROM private_core.gi_credit_drafts
 ORDER BY created_at DESC LIMIT 5;
```

- [ ] **Step 6: Write the e2e verification doc**

Capture the full end-to-end trace (exception → approve → GI document → cancel/issue in GI UI) in `docs/integrations/green_invoice_credit_draft_e2e_verification_2026-05-12.md`.

- [ ] **Step 7: Update memory**

Update `feedback_credit_flow_creates_draft_not_invoice.md` to reflect new runtime state: handler now creates GI draft; manual creation no longer needed for the simple (type-305) flow.

- [ ] **Step 8: Commit**

```bash
git add docs/integrations/green_invoice_credit_draft_e2e_verification_2026-05-12.md
git commit -m "evidence: GI credit draft e2e verified on PROD"
```

---

## Self-review

1. **Spec coverage:** Tom's ask = "when I approve, system creates a draft of the credit with all the data; only draft, not issue." Covered by Tasks 1-5. Task 6 is the live verification.

2. **Branch-B (type 320) handling:** out of scope of "make the basic case work first"; routed to `original_type_unsupported`. If Tom needs Branch B later, that's a follow-on plan.

3. **What this plan deliberately does NOT do:**
   - Does not POST `signed: true` (no auto-issue).
   - Does not modify the inbox card UI in the portal (separate plan, requires UX handoff per CLAUDE.md).
   - Does not add a retry job / cron for failed drafts (the failure path leaves the decision at `pending_gi_action` so the existing manual lane handles it).
   - Does not mirror Morning documents in our DB (fetch-on-demand is sufficient).
   - Does not handle Shopify cancellations (those don't go through credit_needed today).
   - Does not deploy or push.

4. **Risk surface:**
   - Task 1 must complete BEFORE Task 2-5; the architecture pivot is real if `signed:false` doesn't behave as expected.
   - The handler change widens the transaction (now includes a network call). If Morning is slow/down, approve becomes slow. Acceptable for now — the existing path was instant because it did nothing. Mitigation: 10s timeout on the GI client fetch (already implicit in Node's default). If this becomes a problem, move the GI call out of the transaction and into a background dispatch — but that's a follow-on optimization, not a correctness issue.

---

**Plan complete. Saved to `docs/superpowers/plans/2026-05-12-gi-credit-draft-on-approve.md`.**

Execution choice:
1. **Subagent-Driven (recommended)** — fresh subagent per task with review checkpoints.
2. **Inline execution** — current session, batch with checkpoints.
