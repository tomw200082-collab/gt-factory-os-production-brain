# Order-Intake Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **EXECUTION GATE:** This is the first of four sub-plans for the WhatsApp order-intake module
> (spec: `docs/superpowers/specs/2026-06-24-whatsapp-order-intake-design.md`). **Do not start
> executing until both gates clear:** (G1) `MODULE_TEMPLATE.md` filled for `order-intake` + Tom
> written approval; (G2) is irrelevant to *this* plan (offline, no Meta). This plan is offline and
> needs no WhatsApp/Meta. The other three sub-plans (commit path, WhatsApp transport, front-gate/
> sessions) are written separately after this one lands.

**Goal:** Port the proven 2026-06-23 order logic (`lookup.mjs` resolve/prices + `create_draft.mjs`
calc/guard) into a pure, dependency-injected TypeScript engine in gt-factory-os that turns a
structured order spec into a resolved, priced cart with flags — and prove it by replaying the 9 real
orders entered that day, asserting identical carts, totals, and flags.

**Architecture:** Pure functions over a `ShopifyCatalogPort` interface (variant resolution + last-paid
lookup), so the engine is fully testable offline with fixtures captured from real Shopify data. No
live network in unit tests. The Claude free-text parse and the live Shopify/Green-Invoice adapters are
*separate* sub-plans; this engine consumes already-structured lines (barcode/sku/qty), exactly the
shape of today's `.outputs/order-*.json` specs.

**Tech Stack:** TypeScript (ESM/NodeNext, `.js` import specifiers), Zod, vitest. No new runtime deps.

## Global Constraints

- ESM only (`"type": "module"`); import sibling modules with explicit `.js` extension.
- Schemas in Zod (match existing `integrations/greeninvoice/types.ts` style).
- Tests in vitest (`import { describe, it, expect } from 'vitest'`); run with `npx vitest run <path>`.
- Prices are entered **directly per unit — never ×1.18** (store is tax-inclusive; Shopify extracts VAT).
- Order total invariant: `total === Σ(unit_price × bottles)`; double-VAT (`≈ total×1.18`) is a guard FAIL.
- Resolve to **ACTIVE variants only**; HALT on discontinued matcha SKUs `GT-MAR-*` / `GT-KOG-*` / `*-XP-*`
  (GT sells Shizuoka only).
- `bottles = qty_bottles ?? (qty_cartons × (pack ?? pack_default ?? 1))`.
- Module isolation: everything under `api/src/order-intake/**`; **no writes to factory-os core schema**.
- No placeholders, DRY, YAGNI, TDD, commit after every green task.

---

## File Structure

- Create `api/src/order-intake/engine/types.ts` — Zod schemas + types: `RawLine`, `ResolvedLine`,
  `PricedLine`, `Flag`, `Cart`, `GuardResult`, `ResolveStatus`.
- Create `api/src/order-intake/engine/ports.ts` — `ShopifyCatalogPort` interface + `VariantRecord`,
  `ResolveResult` types (the only seam to live Shopify; implemented for real in a later sub-plan).
- Create `api/src/order-intake/engine/bottles.ts` — `bottlesOf(line, packDefault)`.
- Create `api/src/order-intake/engine/resolve.ts` — `resolveVariant(line, port)` + discontinued guard.
- Create `api/src/order-intake/engine/pricing.ts` — `priceLine(...)` last-paid/catalog + price flags.
- Create `api/src/order-intake/engine/guard.ts` — `expectedTotal(cart)`, `evaluateGuard(cart)`.
- Create `api/src/order-intake/engine/build-cart.ts` — `buildCart(spec, port)` orchestrator.
- Create `api/src/order-intake/engine/__tests__/*.test.ts` — one test file per module above.
- Create `api/src/order-intake/engine/__fixtures__/2026-06-23/` — `specs.json` (9 input specs),
  `catalog.json` (variant + last-paid fixture), `expected-carts.json` (the 9 expected carts).

---

### Task 1: Engine types (Zod)

**Files:**
- Create: `api/src/order-intake/engine/types.ts`
- Test: `api/src/order-intake/engine/__tests__/types.test.ts`

**Interfaces:**
- Produces: `RawLine`, `ResolvedLine`, `PricedLine`, `Flag`, `Cart`, `GuardResult` Zod schemas +
  inferred types; `ResolveStatus = 'OK' | 'UNMATCHED' | 'AMBIGUOUS' | 'NO_ACTIVE' | 'DISCONTINUED'`.

- [ ] **Step 1: Write the failing test**

```ts
// __tests__/types.test.ts
import { describe, it, expect } from 'vitest';
import { RawLine, Flag } from '../types.js';

describe('engine types', () => {
  it('RawLine accepts a carton line and a bottle line', () => {
    expect(RawLine.parse({ name: 'NAMASTEA 1L', barcode: '0693493238205', qty_bottles: 12 }).qty_bottles).toBe(12);
    expect(RawLine.parse({ name: 'ENERGY 0.5L', sku: 'GT-LEM-LOW-0.5L', qty_cartons: 1, pack: 6 }).pack).toBe(6);
  });

  it('RawLine rejects a line with neither qty_bottles nor qty_cartons', () => {
    expect(() => RawLine.parse({ name: 'x', barcode: '1' })).toThrow();
  });

  it('Flag carries a code and human message', () => {
    const f = Flag.parse({ code: 'PRICE_GAP', message: 'last-paid 600 != catalog 590', line: 'matcha' });
    expect(f.code).toBe('PRICE_GAP');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd C:/Users/tomw2/Projects/gt-factory-os && npx vitest run api/src/order-intake/engine/__tests__/types.test.ts`
Expected: FAIL — cannot find module `../types.js`.

- [ ] **Step 3: Write minimal implementation**

```ts
// types.ts
import { z } from 'zod';

export const RawLine = z.object({
  name: z.string(),
  barcode: z.string().optional(),
  sku: z.string().optional(),
  qty_bottles: z.number().int().positive().optional(),
  qty_cartons: z.number().int().positive().optional(),
  pack: z.number().int().positive().optional(),
  unit_price: z.number().nonnegative().optional(), // manual override (e.g. PO price, or free=0)
}).refine((l) => l.qty_bottles != null || l.qty_cartons != null, {
  message: 'line needs qty_bottles or qty_cartons',
});
export type RawLine = z.infer<typeof RawLine>;

export const ResolveStatus = z.enum(['OK', 'UNMATCHED', 'AMBIGUOUS', 'NO_ACTIVE', 'DISCONTINUED']);
export type ResolveStatus = z.infer<typeof ResolveStatus>;

export const Flag = z.object({
  code: z.enum([
    'NO_HISTORY_CATALOG', 'PRICE_GAP', 'NO_PRICE', 'UNMATCHED', 'AMBIGUOUS',
    'NO_ACTIVE', 'DISCONTINUED', 'ZERO_PRICE', 'GUARD_FAIL',
  ]),
  message: z.string(),
  line: z.string().optional(),
});
export type Flag = z.infer<typeof Flag>;

export const ResolvedLine = RawLine.and(z.object({
  variant_id: z.string().optional(),
  variant_sku: z.string().optional(),
  variant_title: z.string().optional(),
  variant_price_catalog: z.number().optional(),
  resolve_status: ResolveStatus,
}));
export type ResolvedLine = z.infer<typeof ResolvedLine>;

export const PricedLine = z.object({
  name: z.string(),
  variant_id: z.string().optional(),
  variant_sku: z.string().optional(),
  variant_title: z.string().optional(),
  bottles: z.number().int().nonnegative(),
  unit_price: z.number().nonnegative().nullable(),
  price_source: z.enum(['manual', 'last-paid', 'catalog', 'none']),
  resolve_status: ResolveStatus,
});
export type PricedLine = z.infer<typeof PricedLine>;

export const GuardResult = z.object({
  expected: z.number(), totalOK: z.boolean(), notDoubleVat: z.boolean(), pass: z.boolean(),
});
export type GuardResult = z.infer<typeof GuardResult>;

export const Cart = z.object({
  lines: z.array(PricedLine),
  expected_total: z.number(),
  flags: z.array(Flag),
  ready: z.boolean(), // no flags AND every line resolved+priced
});
export type Cart = z.infer<typeof Cart>;
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npx vitest run api/src/order-intake/engine/__tests__/types.test.ts`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add api/src/order-intake/engine/types.ts api/src/order-intake/engine/__tests__/types.test.ts
git commit -m "feat(order-intake): engine Zod types"
```

---

### Task 2: bottlesOf

**Files:**
- Create: `api/src/order-intake/engine/bottles.ts`
- Test: `api/src/order-intake/engine/__tests__/bottles.test.ts`

**Interfaces:**
- Produces: `bottlesOf(line: { qty_bottles?: number; qty_cartons?: number; pack?: number }, packDefault?: number): number`

- [ ] **Step 1: Write the failing test**

```ts
import { describe, it, expect } from 'vitest';
import { bottlesOf } from '../bottles.js';

describe('bottlesOf', () => {
  it('uses qty_bottles when present', () => expect(bottlesOf({ qty_bottles: 12 }, 6)).toBe(12));
  it('multiplies cartons by line pack', () => expect(bottlesOf({ qty_cartons: 1, pack: 6 }, 1)).toBe(6));
  it('falls back to packDefault when no line pack', () => expect(bottlesOf({ qty_cartons: 2 }, 6)).toBe(12));
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npx vitest run api/src/order-intake/engine/__tests__/bottles.test.ts`
Expected: FAIL — cannot find `../bottles.js`.

- [ ] **Step 3: Write minimal implementation**

```ts
// bottles.ts
export function bottlesOf(
  line: { qty_bottles?: number; qty_cartons?: number; pack?: number },
  packDefault?: number,
): number {
  if (line.qty_bottles != null) return Number(line.qty_bottles);
  const pack = line.pack ?? packDefault ?? 1;
  return Number(line.qty_cartons) * Number(pack);
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npx vitest run api/src/order-intake/engine/__tests__/bottles.test.ts`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add api/src/order-intake/engine/bottles.ts api/src/order-intake/engine/__tests__/bottles.test.ts
git commit -m "feat(order-intake): bottlesOf helper"
```

---

### Task 3: ShopifyCatalogPort + resolveVariant (with discontinued guard)

**Files:**
- Create: `api/src/order-intake/engine/ports.ts`
- Create: `api/src/order-intake/engine/resolve.ts`
- Test: `api/src/order-intake/engine/__tests__/resolve.test.ts`

**Interfaces:**
- Produces (ports.ts):
  ```ts
  export interface VariantRecord { id: string; sku: string; barcode: string | null; price: string; status: 'ACTIVE' | 'ARCHIVED' | 'DRAFT'; title: string; }
  export interface LastPaid { price: number; order: string; date: string; }
  export interface ShopifyCatalogPort {
    variantsByQuery(query: string): Promise<VariantRecord[]>;          // e.g. "barcode:0608614315239" | "sku:GT-LUI-LOW-1L"
    lastPaid(customerId: string, variantId: string): Promise<LastPaid | null>;
  }
  ```
- Produces (resolve.ts): `resolveVariant(line: RawLine, port: ShopifyCatalogPort): Promise<ResolvedLine>`
- Consumes: `RawLine`, `ResolvedLine`, `ResolveStatus` from `types.js`.

- [ ] **Step 1: Write the failing test**

```ts
// __tests__/resolve.test.ts
import { describe, it, expect } from 'vitest';
import { resolveVariant } from '../resolve.js';
import type { ShopifyCatalogPort, VariantRecord } from '../ports.js';

function portOf(map: Record<string, VariantRecord[]>): ShopifyCatalogPort {
  return { async variantsByQuery(q) { return map[q] ?? []; }, async lastPaid() { return null; } };
}
const V = (o: Partial<VariantRecord>): VariantRecord =>
  ({ id: 'gid://x/1', sku: 'S', barcode: '1', price: '65.00', status: 'ACTIVE', title: 'T', ...o });

describe('resolveVariant', () => {
  it('matches a single ACTIVE variant by barcode', async () => {
    const port = portOf({ 'barcode:0608614315239': [V({ sku: 'GT-LUI-LOW-1L', title: 'DETOX 1000ml' })] });
    const r = await resolveVariant({ name: 'DETOX 1L', barcode: '0608614315239', qty_bottles: 1 }, port);
    expect(r.resolve_status).toBe('OK');
    expect(r.variant_sku).toBe('GT-LUI-LOW-1L');
  });

  it('falls back from barcode to sku', async () => {
    const port = portOf({ 'sku:GTCC-MUZ-JASM-1L': [V({ sku: 'GTCC-MUZ-JASM-1L', title: 'Muza Jasmin' })] });
    const r = await resolveVariant({ name: 'Jasmin', sku: 'GTCC-MUZ-JASM-1L', qty_bottles: 4 }, port);
    expect(r.resolve_status).toBe('OK');
  });

  it('returns AMBIGUOUS when barcode hits two ACTIVE variants', async () => {
    const port = portOf({ 'barcode:0693493237826': [V({ sku: 'GTCC-MUZ-JASM-1L' }), V({ sku: 'GTCC-TRO-JAP-1L' })] });
    const r = await resolveVariant({ name: 'Jasmin', barcode: '0693493237826', qty_bottles: 4 }, port);
    expect(r.resolve_status).toBe('AMBIGUOUS');
  });

  it('HALTs DISCONTINUED on a Maruei SKU', async () => {
    const port = portOf({ 'barcode:0726529648065': [V({ sku: 'GT-MAR-CER-500', title: 'Maruei 500g' })] });
    const r = await resolveVariant({ name: 'matcha', barcode: '0726529648065', qty_bottles: 1 }, port);
    expect(r.resolve_status).toBe('DISCONTINUED');
  });

  it('returns UNMATCHED when nothing is found', async () => {
    const r = await resolveVariant({ name: 'x', barcode: '000', qty_bottles: 1 }, portOf({}));
    expect(r.resolve_status).toBe('UNMATCHED');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npx vitest run api/src/order-intake/engine/__tests__/resolve.test.ts`
Expected: FAIL — cannot find `../resolve.js`.

- [ ] **Step 3: Write minimal implementation**

```ts
// ports.ts
export interface VariantRecord { id: string; sku: string; barcode: string | null; price: string; status: 'ACTIVE' | 'ARCHIVED' | 'DRAFT'; title: string; }
export interface LastPaid { price: number; order: string; date: string; }
export interface ShopifyCatalogPort {
  variantsByQuery(query: string): Promise<VariantRecord[]>;
  lastPaid(customerId: string, variantId: string): Promise<LastPaid | null>;
}
```

```ts
// resolve.ts
import type { RawLine, ResolvedLine } from './types.js';
import type { ShopifyCatalogPort, VariantRecord } from './ports.js';

const DISCONTINUED = (sku: string | undefined): boolean =>
  !!sku && (/^GT-MAR-/.test(sku) || /^GT-KOG-/.test(sku) || /-XP-/.test(sku));

export async function resolveVariant(line: RawLine, port: ShopifyCatalogPort): Promise<ResolvedLine> {
  const tries: string[] = [];
  if (line.barcode) {
    tries.push(`barcode:${line.barcode}`);
    if (/^0/.test(line.barcode)) tries.push(`barcode:${line.barcode.replace(/^0+/, '')}`);
  }
  if (line.sku) tries.push(`sku:${line.sku}`);

  let all: VariantRecord[] = [];
  for (const q of tries) { const nodes = await port.variantsByQuery(q); if (nodes.length) { all = nodes; break; } }

  const base = { ...line };
  if (!all.length) return { ...base, resolve_status: 'UNMATCHED' };
  if (all.some((v) => DISCONTINUED(v.sku))) return { ...base, resolve_status: 'DISCONTINUED' };

  const active = all.filter((v) => v.status === 'ACTIVE');
  if (active.length === 1) {
    const v = active[0];
    return { ...base, resolve_status: 'OK', variant_id: v.id, variant_sku: v.sku, variant_title: v.title, variant_price_catalog: Number(v.price) };
  }
  if (active.length === 0) return { ...base, resolve_status: 'NO_ACTIVE' };
  return { ...base, resolve_status: 'AMBIGUOUS' };
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npx vitest run api/src/order-intake/engine/__tests__/resolve.test.ts`
Expected: PASS (5 tests).

- [ ] **Step 5: Commit**

```bash
git add api/src/order-intake/engine/ports.ts api/src/order-intake/engine/resolve.ts api/src/order-intake/engine/__tests__/resolve.test.ts
git commit -m "feat(order-intake): variant resolution + discontinued guard"
```

---

### Task 4: priceLine (last-paid → catalog → manual) + price flags

**Files:**
- Create: `api/src/order-intake/engine/pricing.ts`
- Test: `api/src/order-intake/engine/__tests__/pricing.test.ts`

**Interfaces:**
- Consumes: `ResolvedLine` (with `variant_id`, `variant_price_catalog`), `ShopifyCatalogPort.lastPaid`,
  `bottlesOf`, `Flag`, `PricedLine`.
- Produces: `priceLine(line: ResolvedLine, customerId: string, packDefault: number, port: ShopifyCatalogPort): Promise<{ priced: PricedLine; flags: Flag[] }>`

- [ ] **Step 1: Write the failing test**

```ts
// __tests__/pricing.test.ts
import { describe, it, expect } from 'vitest';
import { priceLine } from '../pricing.js';
import type { ShopifyCatalogPort, LastPaid } from '../ports.js';
import type { ResolvedLine } from '../types.js';

const port = (lp: LastPaid | null): ShopifyCatalogPort =>
  ({ async variantsByQuery() { return []; }, async lastPaid() { return lp; } });
const resolved = (o: Partial<ResolvedLine>): ResolvedLine =>
  ({ name: 'x', qty_bottles: 1, resolve_status: 'OK', variant_id: 'gid://x/1', variant_sku: 'S', variant_price_catalog: 65, ...o }) as ResolvedLine;

describe('priceLine', () => {
  it('uses last-paid when present', async () => {
    const { priced, flags } = await priceLine(resolved({}), 'c1', 6, port({ price: 54, order: '#1', date: '2026-06-01' }));
    expect(priced.unit_price).toBe(54);
    expect(priced.price_source).toBe('last-paid');
    expect(flags).toHaveLength(0);
  });

  it('flags PRICE_GAP when last-paid != catalog', async () => {
    const { priced, flags } = await priceLine(resolved({ variant_price_catalog: 590 }), 'c1', 6, port({ price: 600, order: '#1', date: '2026-06-01' }));
    expect(priced.unit_price).toBe(600);
    expect(flags.map((f) => f.code)).toContain('PRICE_GAP');
  });

  it('falls back to catalog and flags NO_HISTORY_CATALOG', async () => {
    const { priced, flags } = await priceLine(resolved({ variant_price_catalog: 590 }), 'c1', 6, port(null));
    expect(priced.unit_price).toBe(590);
    expect(priced.price_source).toBe('catalog');
    expect(flags.map((f) => f.code)).toContain('NO_HISTORY_CATALOG');
  });

  it('keeps a manual unit_price (PO/free) over last-paid, no flag for the override itself', async () => {
    const { priced } = await priceLine(resolved({ unit_price: 490, variant_price_catalog: 590 }), 'c1', 6, port({ price: 600, order: '#1', date: '2026-06-01' }));
    expect(priced.unit_price).toBe(490);
    expect(priced.price_source).toBe('manual');
  });

  it('flags ZERO_PRICE for a free line', async () => {
    const { flags } = await priceLine(resolved({ unit_price: 0 }), 'c1', 6, port(null));
    expect(flags.map((f) => f.code)).toContain('ZERO_PRICE');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npx vitest run api/src/order-intake/engine/__tests__/pricing.test.ts`
Expected: FAIL — cannot find `../pricing.js`.

- [ ] **Step 3: Write minimal implementation**

```ts
// pricing.ts
import type { ResolvedLine, PricedLine, Flag } from './types.js';
import type { ShopifyCatalogPort } from './ports.js';
import { bottlesOf } from './bottles.js';

export async function priceLine(
  line: ResolvedLine, customerId: string, packDefault: number, port: ShopifyCatalogPort,
): Promise<{ priced: PricedLine; flags: Flag[] }> {
  const flags: Flag[] = [];
  const catalog = line.variant_price_catalog ?? null;
  const lp = line.variant_id ? await port.lastPaid(customerId, line.variant_id) : null;

  let unit_price: number | null;
  let price_source: PricedLine['price_source'];
  if (line.unit_price != null) { unit_price = line.unit_price; price_source = 'manual'; }
  else if (lp) { unit_price = lp.price; price_source = 'last-paid'; }
  else if (catalog != null) { unit_price = catalog; price_source = 'catalog'; }
  else { unit_price = null; price_source = 'none'; }

  if (unit_price == null) flags.push({ code: 'NO_PRICE', message: `no last-paid and no catalog`, line: line.name });
  if (lp && catalog != null && Math.abs(lp.price - catalog) > 0.001)
    flags.push({ code: 'PRICE_GAP', message: `last-paid ${lp.price} != catalog ${catalog} (using ${unit_price})`, line: line.name });
  else if (!lp && price_source === 'catalog' && catalog != null)
    flags.push({ code: 'NO_HISTORY_CATALOG', message: `no purchase history — used catalog ${catalog}`, line: line.name });
  if (unit_price === 0) flags.push({ code: 'ZERO_PRICE', message: `zero-price line — confirm intentional`, line: line.name });

  const priced: PricedLine = {
    name: line.name, variant_id: line.variant_id, variant_sku: line.variant_sku, variant_title: line.variant_title,
    bottles: bottlesOf(line, packDefault), unit_price, price_source, resolve_status: line.resolve_status,
  };
  return { priced, flags };
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npx vitest run api/src/order-intake/engine/__tests__/pricing.test.ts`
Expected: PASS (5 tests).

- [ ] **Step 5: Commit**

```bash
git add api/src/order-intake/engine/pricing.ts api/src/order-intake/engine/__tests__/pricing.test.ts
git commit -m "feat(order-intake): last-paid pricing with catalog fallback + flags"
```

---

### Task 5: VAT guard (expectedTotal + double-VAT detection)

**Files:**
- Create: `api/src/order-intake/engine/guard.ts`
- Test: `api/src/order-intake/engine/__tests__/guard.test.ts`

**Interfaces:**
- Consumes: `PricedLine`, `GuardResult`.
- Produces: `expectedTotal(lines: PricedLine[]): number`; `evaluateGuard(lines: PricedLine[], observedTotal: number): GuardResult`.
  (`observedTotal` is what a later live `draftOrderCalculate` returns; in unit tests we pass the expected
  total to prove the arithmetic, and the double-VAT case to prove detection.)

- [ ] **Step 1: Write the failing test**

```ts
// __tests__/guard.test.ts
import { describe, it, expect } from 'vitest';
import { expectedTotal, evaluateGuard } from '../guard.js';
import type { PricedLine } from '../types.js';

const L = (bottles: number, unit_price: number): PricedLine =>
  ({ name: 'x', bottles, unit_price, price_source: 'last-paid', resolve_status: 'OK' });

describe('guard', () => {
  it('expectedTotal = Σ(unit × bottles)', () => {
    expect(expectedTotal([L(12, 65), L(6, 45)])).toBe(1050);
  });
  it('passes when observed equals expected', () => {
    const g = evaluateGuard([L(12, 65)], 780);
    expect(g.pass).toBe(true);
  });
  it('counts a zero-price line correctly', () => {
    expect(expectedTotal([L(24, 65), L(1, 0)])).toBe(1560);
  });
  it('FAILs on a double-VAT total', () => {
    const g = evaluateGuard([L(12, 65)], 780 * 1.18);
    expect(g.notDoubleVat).toBe(false);
    expect(g.pass).toBe(false);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npx vitest run api/src/order-intake/engine/__tests__/guard.test.ts`
Expected: FAIL — cannot find `../guard.js`.

- [ ] **Step 3: Write minimal implementation**

```ts
// guard.ts
import type { PricedLine, GuardResult } from './types.js';

const r2 = (x: number) => Math.round(x * 100) / 100;

export function expectedTotal(lines: PricedLine[]): number {
  return r2(lines.reduce((s, l) => s + Number(l.unit_price ?? 0) * l.bottles, 0));
}

export function evaluateGuard(lines: PricedLine[], observedTotal: number): GuardResult {
  const expected = expectedTotal(lines);
  const totalOK = Math.abs(observedTotal - expected) <= 0.05;
  const notDoubleVat = Math.abs(observedTotal - expected * 1.18) > 0.5;
  return { expected, totalOK, notDoubleVat, pass: totalOK && notDoubleVat };
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npx vitest run api/src/order-intake/engine/__tests__/guard.test.ts`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add api/src/order-intake/engine/guard.ts api/src/order-intake/engine/__tests__/guard.test.ts
git commit -m "feat(order-intake): VAT/total guard with double-VAT detection"
```

---

### Task 6: buildCart orchestrator

**Files:**
- Create: `api/src/order-intake/engine/build-cart.ts`
- Test: `api/src/order-intake/engine/__tests__/build-cart.test.ts`

**Interfaces:**
- Consumes: `resolveVariant`, `priceLine`, `expectedTotal`, `RawLine`, `Cart`, `Flag`, `ShopifyCatalogPort`.
- Produces:
  ```ts
  export interface OrderSpec { customer_id: string; pack_default?: number; lines: RawLine[]; }
  export function buildCart(spec: OrderSpec, port: ShopifyCatalogPort): Promise<Cart>;
  ```
  `Cart.ready === true` iff zero flags AND every line `resolve_status === 'OK'` AND every `unit_price != null`.

- [ ] **Step 1: Write the failing test**

```ts
// __tests__/build-cart.test.ts
import { describe, it, expect } from 'vitest';
import { buildCart } from '../build-cart.js';
import type { ShopifyCatalogPort, VariantRecord } from '../ports.js';

const V = (o: Partial<VariantRecord>): VariantRecord =>
  ({ id: 'gid://x/1', sku: 'S', barcode: '1', price: '65.00', status: 'ACTIVE', title: 'T', ...o });

const cleanPort: ShopifyCatalogPort = {
  async variantsByQuery(q) {
    if (q === 'barcode:0693493238205') return [V({ id: 'gid://x/mas', sku: 'GT-MAS-CHA-1L', title: 'NAMASTEA 1000ml' })];
    return [];
  },
  async lastPaid() { return { price: 65, order: '#1', date: '2026-06-01' }; },
};

describe('buildCart', () => {
  it('produces a ready cart for a clean order', async () => {
    const cart = await buildCart(
      { customer_id: 'c1', pack_default: 6, lines: [{ name: 'NAMASTEA 1L', barcode: '0693493238205', qty_bottles: 12 }] },
      cleanPort,
    );
    expect(cart.ready).toBe(true);
    expect(cart.expected_total).toBe(780);
    expect(cart.flags).toHaveLength(0);
    expect(cart.lines[0].variant_sku).toBe('GT-MAS-CHA-1L');
  });

  it('is not ready when a line is unmatched', async () => {
    const cart = await buildCart(
      { customer_id: 'c1', lines: [{ name: 'mystery', barcode: '404', qty_bottles: 1 }] },
      cleanPort,
    );
    expect(cart.ready).toBe(false);
    expect(cart.flags.map((f) => f.code)).toContain('UNMATCHED');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npx vitest run api/src/order-intake/engine/__tests__/build-cart.test.ts`
Expected: FAIL — cannot find `../build-cart.js`.

- [ ] **Step 3: Write minimal implementation**

```ts
// build-cart.ts
import type { RawLine, Cart, Flag, PricedLine } from './types.js';
import type { ShopifyCatalogPort } from './ports.js';
import { resolveVariant } from './resolve.js';
import { priceLine } from './pricing.js';
import { expectedTotal } from './guard.js';

export interface OrderSpec { customer_id: string; pack_default?: number; lines: RawLine[]; }

export async function buildCart(spec: OrderSpec, port: ShopifyCatalogPort): Promise<Cart> {
  const packDefault = spec.pack_default ?? 6;
  const lines: PricedLine[] = [];
  const flags: Flag[] = [];

  for (const raw of spec.lines) {
    const resolved = await resolveVariant(raw, port);
    if (resolved.resolve_status !== 'OK') {
      flags.push({ code: resolved.resolve_status as Flag['code'], message: `line "${raw.name}": ${resolved.resolve_status}`, line: raw.name });
    }
    const { priced, flags: priceFlags } = await priceLine(resolved, spec.customer_id, packDefault, port);
    lines.push(priced);
    flags.push(...priceFlags);
  }

  const expected_total = expectedTotal(lines);
  const ready = flags.length === 0 && lines.every((l) => l.resolve_status === 'OK' && l.unit_price != null);
  return { lines, expected_total, flags, ready };
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npx vitest run api/src/order-intake/engine/__tests__/build-cart.test.ts`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add api/src/order-intake/engine/build-cart.ts api/src/order-intake/engine/__tests__/build-cart.test.ts
git commit -m "feat(order-intake): buildCart orchestrator (resolve+price+flags)"
```

---

### Task 7: Golden replay of the 2026-06-23 orders

This is the proof: the engine must reproduce the 9 real carts. Fixtures are captured once from the
`.outputs/` specs and the recorded Shopify data, then frozen.

**Files:**
- Create: `api/src/order-intake/engine/__fixtures__/2026-06-23/catalog.json` — map of `query → VariantRecord[]`
  and `customerId|variantId → LastPaid`, hand-built from the resolved `.outputs/order-*.json` (each enriched
  line already carries `variant_id`, `variant_sku`, `variant_title`, `variant_price_catalog`, and its chosen
  `unit_price`/source). Include the Jasmin barcode collision (two ACTIVE) and a Maruei row to keep guards honest.
- Create: `api/src/order-intake/engine/__fixtures__/2026-06-23/specs.json` — the 9 input specs (pre-enrichment
  shape: `name`/`barcode`/`sku`/`qty_*`/optional `unit_price`), copied from the PRODUCTION `.outputs/` files.
- Create: `api/src/order-intake/engine/__fixtures__/2026-06-23/expected-carts.json` — for each order:
  `{ expected_total, ready, line_count, flag_codes: string[] }` from the 2026-06-23 run
  (e.g. Blicker total 590 ready=false flags `NO_HISTORY_CATALOG`; Babka total 2750 flags include `PRICE_GAP`;
  HaChalonot total 4680 flags include `ZERO_PRICE`).
- Create: `api/src/order-intake/engine/__tests__/replay.test.ts`

**Interfaces:**
- Consumes: `buildCart`, `OrderSpec`, the fixture JSON. Builds an in-memory `ShopifyCatalogPort` from `catalog.json`.

- [ ] **Step 1: Build the fixtures**

Copy the 9 specs from `g:/האחסון שלי/חדש ומסודר/PRODUCTION/.outputs/order-*.json` into `specs.json`
(strip the enrichment fields, keep `customer_id`, `pack_default`, and each line's `name/barcode/sku/qty_*/
unit_price`). From the same enriched files build `catalog.json`: for every line emit
`"barcode:<bc>" → [{id,sku,barcode,price:<catalog>,status:"ACTIVE",title:<variant_title>}]` and
`"<customer_id>|<variant_id>" → {price:<line unit_price when source was last-paid>, order:"hist", date:"2026-06-01"}`
only for lines whose 2026-06-23 price came from last-paid (no entry → forces catalog/again-flag, matching that day).
Add the Jasmin collision (`"barcode:0693493237826" → [JASM ACTIVE, TRO ACTIVE]`) and one Maruei row.
Record expected totals/flags in `expected-carts.json` from the §report table (590/2750/1655/1560/2452/2410/1950/1181/4680).

- [ ] **Step 2: Write the failing test**

```ts
// __tests__/replay.test.ts
import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { buildCart, type OrderSpec } from '../build-cart.js';
import type { ShopifyCatalogPort, VariantRecord, LastPaid } from '../ports.js';

const here = (p: string) => fileURLToPath(new URL(`../__fixtures__/2026-06-23/${p}`, import.meta.url));
const specs = JSON.parse(readFileSync(here('specs.json'), 'utf8')) as Record<string, OrderSpec>;
const catalog = JSON.parse(readFileSync(here('catalog.json'), 'utf8')) as {
  variants: Record<string, VariantRecord[]>; lastPaid: Record<string, LastPaid>;
};
const expected = JSON.parse(readFileSync(here('expected-carts.json'), 'utf8')) as
  Record<string, { expected_total: number; ready: boolean; line_count: number; flag_codes: string[] }>;

const port: ShopifyCatalogPort = {
  async variantsByQuery(q) { return catalog.variants[q] ?? []; },
  async lastPaid(c, v) { return catalog.lastPaid[`${c}|${v}`] ?? null; },
};

describe('2026-06-23 golden replay', () => {
  for (const key of Object.keys(expected)) {
    it(`reproduces ${key}`, async () => {
      const cart = await buildCart(specs[key], port);
      const exp = expected[key];
      expect(cart.expected_total).toBe(exp.expected_total);
      expect(cart.lines).toHaveLength(exp.line_count);
      expect(cart.ready).toBe(exp.ready);
      expect([...new Set(cart.flags.map((f) => f.code))].sort()).toEqual([...exp.flag_codes].sort());
    });
  }
});
```

- [ ] **Step 3: Run test to verify it fails**

Run: `npx vitest run api/src/order-intake/engine/__tests__/replay.test.ts`
Expected: FAIL initially — fixture mismatches (totals/flags). Adjust `catalog.json`/`expected-carts.json`
until each order matches the 2026-06-23 result. A persistent mismatch is a real engine bug — fix the engine,
not the expectation.

- [ ] **Step 4: Run the whole engine suite**

Run: `npx vitest run api/src/order-intake/engine`
Expected: PASS — all unit tests + 9 replay cases green.

- [ ] **Step 5: Typecheck + commit**

```bash
cd C:/Users/tomw2/Projects/gt-factory-os && npx tsc --noEmit
git add api/src/order-intake/engine/__fixtures__ api/src/order-intake/engine/__tests__/replay.test.ts
git commit -m "test(order-intake): golden replay of the 9 real 2026-06-23 orders"
```

---

## Self-Review

**Spec coverage (engine slice of §4 PARSE / §6 flags / §11 testing):**
- Resolve barcode→sku→ACTIVE, AMBIGUOUS/UNMATCHED/NO_ACTIVE → Task 3. ✓
- Discontinued matcha HALT (Maruei/Kogamo/XP) → Task 3. ✓
- Last-paid pricing, catalog fallback, manual override, price flags → Task 4. ✓
- Zero-price line flag → Task 4/5. ✓
- VAT guard + double-VAT → Task 5. ✓
- Cart assembly + ready/flags → Task 6. ✓
- Replay today's 9 orders (parity) → Task 7. ✓
- *Out of scope here (separate sub-plans):* Claude free-text parse + intent (uses the lexicon), the live
  `ShopifyCatalogPort` adapter (`draftOrderCalculate`/GraphQL), Green-Invoice commit, WhatsApp transport,
  front gate + sessions. Noted at top.

**Placeholder scan:** none — every step has runnable code/commands. Task 7 Step 1 is a fixture-build action
with an explicit construction recipe (not a code block, but a precise data-derivation procedure), which is
appropriate for a fixtures task.

**Type consistency:** `ShopifyCatalogPort.variantsByQuery`/`lastPaid` used identically in Tasks 3, 4, 6, 7.
`RawLine`/`ResolvedLine`/`PricedLine`/`Cart`/`Flag` names consistent across tasks. `bottlesOf` signature
matches its use in pricing. `resolve_status` values match the `ResolveStatus` enum.
```
