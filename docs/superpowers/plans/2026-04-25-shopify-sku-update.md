# Shopify Variant SKU Update — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update the `sku` field on every active Shopify product variant to the GT platform's canonical `item_id`, then seed `integration_sku_map` with approved mappings so the 15-minute inventory sync resolves all FG items without `skipped_unmapped` exceptions.

**Architecture:** A TypeScript script reads a mapping CSV (`shopify_variant_gid → platform_item_id`), calls Shopify Admin GraphQL `productVariantUpdate` for each variant with rate-limit backoff, and writes an audit report. A separate Node script seeds `integration_sku_map` with `approval_status='approved'` rows using the same mapping. A verify pass reads Shopify back to confirm all SKUs match before seeding the DB.

**Tech Stack:** Node.js 20, TypeScript, `tsx` (direct TS execution), Shopify Admin GraphQL API `2025-07`, `csv-parse`, `pg` (Postgres client for DB seed)

---

## Context

- **Sync infrastructure:** deployed, running `*/15 * * * *` via `pg_cron` (migration 0066)
- **Current state:** all 61 FG-eligible items (`supply_method IN ('MANUFACTURED','BOUGHT_FINISHED','REPACK') AND status='ACTIVE'`) return `write_status='skipped_unmapped'` because `integration_sku_map` has zero approved Shopify rows
- **Mapping key:** the sync matches `integration_sku_map.external_sku` against Shopify `variant.sku` — so once we (a) update Shopify SKUs and (b) seed the map, the next cron cycle resolves all items
- **No fetcher HTTP implementation yet:** the sync currently runs the mapping-check logic and logs `skipped_unmapped`; the actual `inventorySetQuantities` HTTP push may not be implemented. Steps 7.7–7.10 (sync validation) are best-effort and depend on the fetcher runtime state — mark CONDITIONAL if the push log shows no HTTP calls.

---

## File Structure

| File | Action | Purpose |
|---|---|---|
| `scripts/shopify-sku-update/mapping.csv` | Create (human-provided) | Input: `shopify_variant_gid,platform_item_id` |
| `scripts/shopify-sku-update/schema.ts` | Create | Zod schemas for CSV row and result shapes |
| `scripts/shopify-sku-update/fetch-shopify-products.ts` | Create | One-shot: dump all Shopify products+variants to JSON (mapping prep aid) |
| `scripts/shopify-sku-update/update-shopify-skus.ts` | Create | Reads mapping CSV, calls `productVariantUpdate` per variant |
| `scripts/shopify-sku-update/verify-shopify-skus.ts` | Create | Reads Shopify back, confirms each variant SKU matches mapping |
| `scripts/shopify-sku-update/seed-integration-sku-map.ts` | Create | Inserts/upserts approved rows into `private_core.integration_sku_map` |

---

## Chunk 1: Data Preparation

### Task 1: Fetch Shopify Product List (Mapping Aid)

**Files:**
- Create: `scripts/shopify-sku-update/fetch-shopify-products.ts`

This script dumps all Shopify products and their variants to JSON so you can see the variant GIDs and current SKUs. It is NOT the update script — it is read-only and safe to run multiple times.

- [ ] **Step 1.1: Create the scripts directory**

```bash
mkdir -p "scripts/shopify-sku-update"
```

- [ ] **Step 1.2: Write the product fetch script**

```typescript
// scripts/shopify-sku-update/fetch-shopify-products.ts
import { writeFileSync } from 'fs';

const SHOPIFY_STORE = process.env.SHOPIFY_STORE_DOMAIN!;
const SHOPIFY_TOKEN = process.env.SHOPIFY_ACCESS_TOKEN!;
const API_VERSION = '2025-07';
const GQL = `https://${SHOPIFY_STORE}/admin/api/${API_VERSION}/graphql.json`;

const PRODUCTS_QUERY = `
  query GetProducts($cursor: String) {
    products(first: 50, after: $cursor) {
      edges {
        node {
          id
          title
          handle
          variants(first: 10) {
            edges {
              node {
                id
                sku
                title
              }
            }
          }
        }
      }
      pageInfo { hasNextPage endCursor }
    }
  }
`;

async function main() {
  if (!SHOPIFY_STORE || !SHOPIFY_TOKEN) {
    console.error('Missing SHOPIFY_STORE_DOMAIN or SHOPIFY_ACCESS_TOKEN');
    process.exit(2);
  }

  const results: object[] = [];
  let cursor: string | null = null;
  let hasNextPage = true;

  while (hasNextPage) {
    const res = await fetch(GQL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Shopify-Access-Token': SHOPIFY_TOKEN,
      },
      body: JSON.stringify({ query: PRODUCTS_QUERY, variables: { cursor } }),
    });
    if (!res.ok) { console.error(`HTTP ${res.status}`); process.exit(1); }
    const json: any = await res.json();
    const page = json?.data?.products;
    for (const edge of page.edges) {
      results.push({
        product_gid: edge.node.id,
        title: edge.node.title,
        handle: edge.node.handle,
        variants: edge.node.variants.edges.map((v: any) => ({
          variant_gid: v.node.id,
          current_sku: v.node.sku ?? '',
          variant_title: v.node.title,
        })),
      });
    }
    hasNextPage = page.pageInfo.hasNextPage;
    cursor = page.pageInfo.endCursor;
    if (hasNextPage) await new Promise(r => setTimeout(r, 300));
  }

  writeFileSync('scripts/shopify-sku-update/shopify-products.json', JSON.stringify(results, null, 2));
  console.log(`Wrote ${results.length} products to scripts/shopify-sku-update/shopify-products.json`);
}

main().catch(e => { console.error(e); process.exit(1); });
```

- [ ] **Step 1.3: Set environment variables**

```bash
export SHOPIFY_STORE_DOMAIN=<your-store>.myshopify.com
export SHOPIFY_ACCESS_TOKEN=<token from Shopify Admin → Settings → Apps → [your custom app] → Admin API access token>
```

- [ ] **Step 1.4: Run the fetch script**

```bash
npx tsx scripts/shopify-sku-update/fetch-shopify-products.ts
```

Expected: Creates `scripts/shopify-sku-update/shopify-products.json`. Output: "Wrote N products to..."

- [ ] **Step 1.5: Verify product count looks correct**

```bash
cat scripts/shopify-sku-update/shopify-products.json | python3 -c "import json,sys; p=json.load(sys.stdin); print(len(p), 'products,', sum(len(x['variants']) for x in p), 'variants')"
```

Expected: N products, at least 61 variants total (one per FG item).

---

### Task 2: Query Platform FG Items

Before building the mapping CSV you need to see the canonical `item_id` values from the platform.

- [ ] **Step 2.1: Get DATABASE_URL**

From Railway dashboard or Supabase → Settings → Database → Connection String (use the non-pooled URI for scripts).

```bash
export DATABASE_URL=<from-Railway-or-Supabase>
```

- [ ] **Step 2.2: Query all FG-eligible items**

```bash
psql $DATABASE_URL -c "
SELECT item_id, name, supply_method, legacy_sku
FROM private_core.items
WHERE supply_method IN ('MANUFACTURED','BOUGHT_FINISHED','REPACK')
  AND status = 'ACTIVE'
ORDER BY item_id;" 2>&1 | tee scripts/shopify-sku-update/platform-items.txt
```

Expected: ~61 rows. Each row shows the `item_id` (e.g., `GT-LUI-LOW-1L`) which becomes the new Shopify SKU value and the `integration_sku_map.external_sku` value.

---

### Task 3: Build the Mapping CSV

**Files:**
- Create: `scripts/shopify-sku-update/mapping.csv`

Match each row from `shopify-products.json` (variant_gid) to each row from `platform-items.txt` (item_id).

- [ ] **Step 3.1: Create `mapping.csv` with header**

```csv
shopify_variant_gid,platform_item_id
gid://shopify/ProductVariant/1234567890,GT-LUI-LOW-1L
gid://shopify/ProductVariant/2345678901,GT-HIB-LOW-1L
...
```

**Rules:**
- One row per Shopify variant (not per product)
- `shopify_variant_gid` must be a full GID string: `gid://shopify/ProductVariant/<numeric_id>`
- `platform_item_id` must exactly match `item_id` from the items table (case-sensitive)
- The Shopify `variant.sku` field will be set to `platform_item_id`
- `integration_sku_map.external_sku` will also be set to `platform_item_id`

- [ ] **Step 3.2: Count rows — must equal number of FG items**

```bash
tail -n +2 scripts/shopify-sku-update/mapping.csv | wc -l
```

Expected: same count as the platform items query result (likely 61).

---

## Chunk 2: Scripts

### Task 4: Write Schema Types

**Files:**
- Create: `scripts/shopify-sku-update/schema.ts`

- [ ] **Step 4.1: Verify zod is available**

```bash
node -e "require('zod'); console.log('ok')" 2>/dev/null || npm install zod csv-parse pg
```

If the project's `package.json` already has `zod` and `csv-parse`, this is a no-op. If not, install them:

```bash
cd scripts/shopify-sku-update && npm init -y && npm install zod csv-parse pg tsx typescript && cd ../..
```

- [ ] **Step 4.2: Write the schema file**

```typescript
// scripts/shopify-sku-update/schema.ts
import { z } from 'zod';

export const MappingRow = z.object({
  shopify_variant_gid: z
    .string()
    .regex(/^gid:\/\/shopify\/ProductVariant\/\d+$/, 'Must be gid://shopify/ProductVariant/<number>'),
  platform_item_id: z.string().min(1, 'platform_item_id required'),
});
export type MappingRow = z.infer<typeof MappingRow>;

export const UpdateResult = z.object({
  shopify_variant_gid: z.string(),
  platform_item_id: z.string(),
  status: z.enum(['ok', 'user_error', 'http_error', 'rate_limit_exceeded', 'skipped']),
  confirmed_sku: z.string().optional(),
  error: z.string().optional(),
});
export type UpdateResult = z.infer<typeof UpdateResult>;
```

---

### Task 5: Write the Update Script

**Files:**
- Create: `scripts/shopify-sku-update/update-shopify-skus.ts`

- [ ] **Step 5.1: Write the update script**

```typescript
// scripts/shopify-sku-update/update-shopify-skus.ts
import { parse } from 'csv-parse/sync';
import { readFileSync, writeFileSync } from 'fs';
import { join } from 'path';
import { MappingRow, UpdateResult } from './schema';

const SHOPIFY_STORE = process.env.SHOPIFY_STORE_DOMAIN!;
const SHOPIFY_TOKEN = process.env.SHOPIFY_ACCESS_TOKEN!;
const API_VERSION = '2025-07';
const DRY_RUN = process.argv.includes('--dry-run');
const RATE_LIMIT_MS = 600; // 600ms between calls ≈ 1.6 req/sec (conservative under Shopify's 2 req/sec restored rate)

const GQL = `https://${SHOPIFY_STORE}/admin/api/${API_VERSION}/graphql.json`;

const UPDATE_MUTATION = `
  mutation UpdateSku($variantId: ID!, $sku: String!) {
    productVariantUpdate(input: { id: $variantId, sku: $sku }) {
      productVariant { id sku }
      userErrors { field message }
    }
  }
`;

async function callGql(variables: object, attempt = 0): Promise<any> {
  const res = await fetch(GQL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Shopify-Access-Token': SHOPIFY_TOKEN,
    },
    body: JSON.stringify({ query: UPDATE_MUTATION, variables }),
  });

  if (res.status === 429) {
    if (attempt >= 3) throw new Error('rate_limit_exceeded after 3 retries');
    const wait = parseInt(res.headers.get('Retry-After') ?? '2', 10) * 1000;
    console.log(`    Rate limited — waiting ${wait}ms`);
    await new Promise(r => setTimeout(r, wait));
    return callGql(variables, attempt + 1);
  }

  if (!res.ok) throw new Error(`HTTP ${res.status} ${res.statusText}`);
  return res.json();
}

async function main() {
  if (!SHOPIFY_STORE || !SHOPIFY_TOKEN) {
    console.error('❌ Missing env: SHOPIFY_STORE_DOMAIN or SHOPIFY_ACCESS_TOKEN');
    process.exit(2);
  }

  const csvPath = join(__dirname, 'mapping.csv');
  const rows = (parse(readFileSync(csvPath, 'utf8'), { columns: true, skip_empty_lines: true }) as unknown[])
    .map((r, i) => {
      const result = MappingRow.safeParse(r);
      if (!result.success) {
        console.error(`❌ Invalid row ${i + 2}:`, r, result.error.flatten());
        process.exit(1);
      }
      return result.data;
    });

  console.log(`Loaded ${rows.length} rows. DRY_RUN=${DRY_RUN}\n`);

  const results: UpdateResult[] = [];

  for (const row of rows) {
    const { shopify_variant_gid, platform_item_id } = row;
    const variantNum = shopify_variant_gid.split('/').pop();
    process.stdout.write(`  [${variantNum}] → "${platform_item_id}" ... `);

    if (DRY_RUN) {
      console.log('skipped (dry-run)');
      results.push({ shopify_variant_gid, platform_item_id, status: 'skipped' });
      continue;
    }

    try {
      const json = await callGql({ variantId: shopify_variant_gid, sku: platform_item_id });
      const userErrors: any[] = json?.data?.productVariantUpdate?.userErrors ?? [];
      if (userErrors.length > 0) {
        const msg = userErrors.map((e: any) => `${e.field}: ${e.message}`).join('; ');
        console.log(`❌ user_error: ${msg}`);
        results.push({ shopify_variant_gid, platform_item_id, status: 'user_error', error: msg });
      } else {
        const confirmed = json?.data?.productVariantUpdate?.productVariant?.sku;
        console.log(`✅ confirmed sku="${confirmed}"`);
        results.push({ shopify_variant_gid, platform_item_id, status: 'ok', confirmed_sku: confirmed });
      }
    } catch (err: any) {
      const status = err.message.startsWith('rate_limit') ? 'rate_limit_exceeded' : 'http_error';
      console.log(`❌ ${err.message}`);
      results.push({ shopify_variant_gid, platform_item_id, status, error: err.message });
    }

    await new Promise(r => setTimeout(r, RATE_LIMIT_MS));
  }

  writeFileSync(join(__dirname, 'update-report.json'), JSON.stringify(results, null, 2));

  const ok = results.filter(r => r.status === 'ok').length;
  const failed = results.filter(r => !['ok', 'skipped'].includes(r.status)).length;
  console.log(`\nDone. ${ok} updated, ${failed} failed. Report: scripts/shopify-sku-update/update-report.json`);
  if (failed > 0) process.exit(1);
}

main().catch(e => { console.error(e); process.exit(1); });
```

- [ ] **Step 5.2: Run dry-run to validate CSV parsing**

```bash
SHOPIFY_STORE_DOMAIN=dummy.myshopify.com \
SHOPIFY_ACCESS_TOKEN=dummy \
npx tsx scripts/shopify-sku-update/update-shopify-skus.ts --dry-run
```

Expected: Prints all rows as "skipped (dry-run)". No HTTP calls. Exit code 0.

If any row shows ❌: fix the `mapping.csv` row and re-run until all rows parse cleanly.

---

### Task 6: Write the Verify Script

**Files:**
- Create: `scripts/shopify-sku-update/verify-shopify-skus.ts`

- [ ] **Step 6.1: Write the verify script**

```typescript
// scripts/shopify-sku-update/verify-shopify-skus.ts
import { parse } from 'csv-parse/sync';
import { readFileSync } from 'fs';
import { join } from 'path';
import { MappingRow } from './schema';

const SHOPIFY_STORE = process.env.SHOPIFY_STORE_DOMAIN!;
const SHOPIFY_TOKEN = process.env.SHOPIFY_ACCESS_TOKEN!;
const API_VERSION = '2025-07';
const GQL = `https://${SHOPIFY_STORE}/admin/api/${API_VERSION}/graphql.json`;

const GET_VARIANT = `
  query GetVariant($id: ID!) {
    productVariant(id: $id) { id sku displayName }
  }
`;

async function main() {
  if (!SHOPIFY_STORE || !SHOPIFY_TOKEN) { console.error('Missing env'); process.exit(2); }

  const rows = (parse(readFileSync(join(__dirname, 'mapping.csv'), 'utf8'), { columns: true, skip_empty_lines: true }) as unknown[])
    .map(r => MappingRow.parse(r));

  console.log(`Verifying ${rows.length} variants...\n`);

  let matched = 0, mismatched = 0, missing = 0;

  for (const { shopify_variant_gid, platform_item_id } of rows) {
    const res = await fetch(GQL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Shopify-Access-Token': SHOPIFY_TOKEN },
      body: JSON.stringify({ query: GET_VARIANT, variables: { id: shopify_variant_gid } }),
    });
    const json: any = await res.json();
    const v = json?.data?.productVariant;

    if (!v) {
      console.error(`  ❌ NOT FOUND: ${shopify_variant_gid}`);
      missing++;
    } else if (v.sku !== platform_item_id) {
      console.error(`  ❌ MISMATCH: ${v.displayName} — expected "${platform_item_id}", got "${v.sku ?? '(empty)'}"` );
      mismatched++;
    } else {
      console.log(`  ✅ ${v.displayName} — "${v.sku}"`);
      matched++;
    }

    await new Promise(r => setTimeout(r, 300));
  }

  console.log(`\n${matched} matched, ${mismatched} mismatched, ${missing} missing`);
  if (mismatched + missing > 0) process.exit(1);
}

main().catch(e => { console.error(e); process.exit(1); });
```

---

### Task 7: Write the DB Seed Script

**Files:**
- Create: `scripts/shopify-sku-update/seed-integration-sku-map.ts`

After Shopify SKUs are updated, this script seeds `integration_sku_map` so the 15-minute sync can resolve each FG item. The `external_sku` value is the same as `platform_item_id` because we just set Shopify's `variant.sku` to `platform_item_id`.

- [ ] **Step 7.1: Write the seed script**

```typescript
// scripts/shopify-sku-update/seed-integration-sku-map.ts
import { parse } from 'csv-parse/sync';
import { readFileSync } from 'fs';
import { join } from 'path';
import { Client } from 'pg';
import { MappingRow } from './schema';

const DATABASE_URL = process.env.DATABASE_URL!;
const APPROVED_BY_EMAIL = 'tom@gteveryday.com';

async function main() {
  if (!DATABASE_URL) { console.error('Missing DATABASE_URL'); process.exit(2); }

  const rows = (parse(readFileSync(join(__dirname, 'mapping.csv'), 'utf8'), { columns: true, skip_empty_lines: true }) as unknown[])
    .map(r => MappingRow.parse(r));

  const db = new Client({ connectionString: DATABASE_URL });
  await db.connect();

  const userRes = await db.query(`SELECT id FROM auth.users WHERE email = $1`, [APPROVED_BY_EMAIL]);
  if (userRes.rows.length === 0) {
    console.error(`❌ User not found: ${APPROVED_BY_EMAIL}`);
    await db.end();
    process.exit(1);
  }
  const approvedByUserId: string = userRes.rows[0].id;
  console.log(`Approving as user: ${approvedByUserId} (${APPROVED_BY_EMAIL})\n`);

  let inserted = 0, updated = 0;

  for (const { platform_item_id } of rows) {
    // external_sku = platform_item_id because we just set Shopify variant.sku = platform_item_id
    const result = await db.query(`
      INSERT INTO private_core.integration_sku_map
        (alias_id, source_channel, external_sku, item_id, approval_status,
         approved_by_user_id, approved_at, notes, site_id)
      VALUES
        (gen_random_uuid(), 'shopify', $1, $1, 'approved',
         $2, NOW(), 'seeded via shopify-sku-update 2026-04-25', 'GT-MAIN')
      ON CONFLICT (source_channel, external_sku) DO UPDATE
        SET approval_status      = 'approved',
            item_id              = EXCLUDED.item_id,
            approved_by_user_id  = EXCLUDED.approved_by_user_id,
            approved_at          = NOW(),
            notes                = EXCLUDED.notes
      RETURNING (xmax = 0) AS was_inserted
    `, [platform_item_id, approvedByUserId]);

    const wasInserted: boolean = result.rows[0]?.was_inserted;
    console.log(`  ${wasInserted ? '➕' : '🔄'} ${platform_item_id}`);
    if (wasInserted) inserted++; else updated++;
  }

  await db.end();
  console.log(`\nDone. ${inserted} inserted, ${updated} upserted.`);
}

main().catch(e => { console.error(e); process.exit(1); });
```

---

## Chunk 3: Production Execution

### Task 8: Pre-flight Checks

- [ ] **Step 8.1: Set all environment variables**

```bash
export SHOPIFY_STORE_DOMAIN=<store>.myshopify.com
export SHOPIFY_ACCESS_TOKEN=<admin api token>
export DATABASE_URL=<non-pooled connection string from Supabase>
```

- [ ] **Step 8.2: Confirm Shopify token has write access**

The token must have `write_products` and `read_inventory` scopes. Verify in Shopify Admin → Apps → [custom app] → API credentials → Scopes.

- [ ] **Step 8.3: Count DB rows before (should be 0)**

```bash
psql $DATABASE_URL -c "SELECT COUNT(*) FROM private_core.integration_sku_map WHERE source_channel='shopify';"
```

Expected: `0`

---

### Task 9: Run the Update (Live)

- [ ] **Step 9.1: Verify BEFORE — capture baseline state**

```bash
npx tsx scripts/shopify-sku-update/verify-shopify-skus.ts 2>&1 | tee scripts/shopify-sku-update/before-update.log
```

Expected: Most lines show MISMATCH or empty SKU. Exit code non-zero (that's correct — this is the baseline).

- [ ] **Step 9.2: Run the update script (LIVE — this writes to Shopify)**

```bash
npx tsx scripts/shopify-sku-update/update-shopify-skus.ts
```

Expected: Every line shows `✅ confirmed sku="<item_id>"`. Exit code 0.

**If any lines show ❌:** Do NOT proceed to seeding. Investigate the failed variants. Re-run only the failed rows (edit a temp CSV) or fix and re-run the full script (it is idempotent — updating an already-correct SKU is a no-op).

- [ ] **Step 9.3: Verify AFTER — confirm all SKUs updated**

```bash
npx tsx scripts/shopify-sku-update/verify-shopify-skus.ts 2>&1 | tee scripts/shopify-sku-update/after-update.log
```

Expected: All lines show `✅`. Exit code 0. If any MISMATCH: investigate before proceeding.

---

### Task 10: Seed the DB Mapping

Only run after Step 9.3 passes cleanly.

- [ ] **Step 10.1: Run the seed script**

```bash
npx tsx scripts/shopify-sku-update/seed-integration-sku-map.ts
```

Expected: All rows show `➕` (inserted). Final line: "Done. N inserted, 0 upserted." Exit code 0.

- [ ] **Step 10.2: Verify DB seed**

```bash
psql $DATABASE_URL -c "
SELECT
  COUNT(*) AS total,
  COUNT(*) FILTER (WHERE approval_status='approved') AS approved
FROM private_core.integration_sku_map
WHERE source_channel='shopify';"
```

Expected: `total = approved = N` (matching the row count in mapping.csv).

---

### Task 11: Validate Sync Cycle (Best-Effort)

> **Note:** Steps 11.2–11.5 depend on the fetcher HTTP push implementation being deployed. If the sync runtime only performs the mapping-check pass (not the actual Shopify API push), the history will show mapping resolution but not `write_status='ok'`. Check with the fetcher implementation owner if results are unexpected.

- [ ] **Step 11.1: Check when the next cron fires**

```bash
psql $DATABASE_URL -c "
SELECT jobname, schedule, active, last_run_started_at
FROM cron.job
WHERE jobname LIKE '%shopify%';"
```

Wait up to 15 minutes for the next cycle.

- [ ] **Step 11.2: Check sync state after one cycle**

```bash
psql $DATABASE_URL -c "
SELECT last_sync_at, last_successful_sync_at, last_sync_writes_ok, last_sync_writes_failed
FROM private_core.shopify_sync_state;"
```

Expected: `last_sync_writes_ok = N`, `last_sync_writes_failed = 0`.

- [ ] **Step 11.3: Check history for write statuses**

```bash
psql $DATABASE_URL -c "
SELECT write_status, COUNT(*)
FROM private_core.shopify_fg_sync_history
WHERE created_at > NOW() - INTERVAL '20 minutes'
GROUP BY write_status;"
```

Expected: `write_status='ok'` with count = N. Zero `skipped_unmapped` rows.

- [ ] **Step 11.4: Confirm exceptions inbox is clear**

```bash
psql $DATABASE_URL -c "
SELECT COUNT(*)
FROM private_core.exceptions
WHERE category = 'shopify_unmapped_item'
  AND resolved_at IS NULL;"
```

Expected: `0`

- [ ] **Step 11.5: Check portal admin integrations view**

Navigate to `/admin/integrations` in the portal.

Expected:
- Status badge: `fresh`
- Last sync writes ok: N
- Items skipped: 0

---

## Exit Criteria

All of the following must be true before this task is declared complete:

- [ ] `EC-1` — `verify-shopify-skus.ts` exits 0 with all rows showing `✅`
- [ ] `EC-2` — `integration_sku_map` has N rows with `source_channel='shopify'` and `approval_status='approved'`
- [ ] `EC-3` — Zero open `shopify_unmapped_item` exceptions in the DB
- [ ] `EC-4` — Sync cycle shows no `skipped_unmapped` rows in `shopify_fg_sync_history` (CONDITIONAL on fetcher runtime)
- [ ] `EC-5` — `update-report.json` shows zero failed rows
