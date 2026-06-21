#!/usr/bin/env node
/**
 * Set driver_id + pickup_at on LionWheel tasks, and verify each by re-read.
 * NEVER sets status. POST-APPROVAL ONLY — run after Tom has approved the exact plan.
 *
 * Usage:  node lw_apply.mjs <YYYY-MM-DD> <driver_id> <task_id> [task_id...]
 *         node lw_apply.mjs 2026-06-22 28174 25540245 25246242
 *         node lw_apply.mjs <YYYY-MM-DD> null <task_id...>   # unassign (only if Tom asked)
 *
 * Env: LIONWHEEL_BASE_URL, LIONWHEEL_API_KEY.
 */
const base = process.env.LIONWHEEL_BASE_URL, key = process.env.LIONWHEEL_API_KEY;
if (!base || !key) { console.error('Missing LIONWHEEL_BASE_URL / LIONWHEEL_API_KEY'); process.exit(2); }

const [date, driverArg, ...ids] = process.argv.slice(2);
if (!date || !/^\d{4}-\d{2}-\d{2}$/.test(date) || !driverArg || ids.length === 0) {
  console.error('Usage: node lw_apply.mjs <YYYY-MM-DD> <driver_id|null> <task_id...>'); process.exit(2);
}
const driver_id = driverArg === 'null' ? null : Number(driverArg);
if (driverArg !== 'null' && !Number.isInteger(driver_id)) { console.error('driver_id must be an integer or "null"'); process.exit(2); }

const put = async (id) => {
  const u = new URL(`/api/v1/tasks/${id}/update`, base); u.searchParams.set('key', key);
  const r = await fetch(u, { method: 'PUT', headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ driver_id, pickup_at: date }) });            // NOTE: no status field, ever
  return { status: r.status, body: (await r.text()).slice(0, 100).replace(/\s+/g, ' ') };
};
const read = async (id) => {
  const u = new URL(`/api/v1/tasks/show/${id}.json`, base); u.searchParams.set('key', key);
  const d = await (await fetch(u, { headers: { Accept: 'application/json' } })).json(); const dt = d.task ?? d;
  return { driver_id: dt.driver_id ?? null, pickup_at: (dt.pickup_at || '').slice(0, 10), status: dt.status };
};

let ok = 0, bad = 0;
for (const id of ids) {
  const w = await put(id); const a = await read(id);
  const good = w.status === 200 && a.driver_id === driver_id && a.pickup_at === date;
  if (good) ok++; else bad++;
  console.log(`${id}: PUT ${w.status} "${w.body}" -> drv:${a.driver_id ?? 'null'} ${a.pickup_at} ${a.status} ${good ? 'OK' : 'CHECK'}`);
}
console.log(`\nDone: ${ok} ok, ${bad} need-check, of ${ids.length}. (status left untouched on all)`);
process.exit(bad ? 1 : 0);
