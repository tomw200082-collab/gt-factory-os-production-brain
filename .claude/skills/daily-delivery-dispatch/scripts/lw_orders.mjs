#!/usr/bin/env node
/**
 * Read-only: fetch open LionWheel orders, filter to a delivery zone (zones.json),
 * print each order's lines + current driver/pickup, and flag any city not in zones.json.
 *
 * Usage:  node lw_orders.mjs <zone>            e.g.  node lw_orders.mjs Center
 *         node lw_orders.mjs                    (no zone -> dump all open, grouped by zone)
 *
 * Env: LIONWHEEL_BASE_URL, LIONWHEEL_API_KEY.
 * Does NOT write anything. SKU resolution + on-hand are done by the agent via Supabase MCP
 * (see SKILL.md "Stock classification"); this script only delivers orders + cities.
 */
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const base = process.env.LIONWHEEL_BASE_URL, key = process.env.LIONWHEEL_API_KEY;
if (!base || !key) { console.error('Missing LIONWHEEL_BASE_URL / LIONWHEEL_API_KEY'); process.exit(2); }

const here = dirname(fileURLToPath(import.meta.url));
const zonesDoc = JSON.parse(readFileSync(join(here, '..', 'zones.json'), 'utf8'));
const ZONES = Object.fromEntries(
  Object.entries(zonesDoc).filter(([k]) => !k.startsWith('_'))
    .map(([z, cities]) => [z, new Set(cities.map(c => c.toLowerCase().trim()))])
);
const ALIASES = { center: 'Center', 'מרכז': 'Center', north: 'North', 'צפון': 'North', south: 'South', 'דרום': 'South' };
const argZone = process.argv[2];
const wantZone = argZone ? (ALIASES[argZone.toLowerCase()] || argZone) : null;

const norm = s => (s || '').toLowerCase().trim();
const zoneOf = city => { const n = norm(city); for (const [z, set] of Object.entries(ZONES)) if (set.has(n)) return z; return null; };

const J = async path => { const u = new URL(path, base); u.searchParams.set('key', key); return (await fetch(u, { headers: { Accept: 'application/json' } })).json(); };

const u = new URL('/api/v1/tasks.json', base); u.searchParams.set('key', key); u.searchParams.set('limit', '300');
const arr = (await (await fetch(u, { headers: { Accept: 'application/json' } })).json()).tasks || [];
const open = arr.filter(t => t.status === 'UNASSIGNED' || t.status === 'ASSIGNED').sort((a, b) => a.id - b.id);

const rows = [];
const unknownCities = new Set();
for (const t of open) {
  const z = zoneOf(t.destination_city);
  if (!z && t.destination_city) unknownCities.add(t.destination_city);
  if (wantZone && z !== wantZone) continue;
  const d = await J(`/api/v1/tasks/show/${t.id}.json`); const dt = d.task ?? d;
  rows.push({
    id: t.id, wp: t.wp_order_id || null, zone: z, city: t.destination_city || null,
    status: t.status, driver_id: dt.driver_id ?? null, pickup_at: (dt.pickup_at || '').slice(0, 10),
    lines: (t.order_items || []).map(i => ({ sku: i.sku || null, name: (i.name || '').slice(0, 40), qty: Number(i.quantity) || 0 }))
  });
}

console.log(JSON.stringify({
  zone: wantZone || 'ALL', open_total: open.length, matched: rows.length,
  unknown_cities: [...unknownCities], orders: rows
}, null, 2));
if (unknownCities.size) console.error(`\n⚠️  ${unknownCities.size} city(ies) not in zones.json — ask Tom + append: ${[...unknownCities].join(', ')}`);
