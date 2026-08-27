#!/usr/bin/env node
// Production reporting, end to end, over the live GT Factory OS API.
//
// Every write here is a real endpoint the portal also calls, which is the whole
// point: the BOM explosion, the pick netting, the cap-to-on-hand rule and the
// plan-completion link all live in one tested handler. Re-deriving any of that
// in SQL is how stock truth quietly drifts, so this script never writes SQL —
// it only orchestrates.
//
// Usage:
//   GT_API_TOKEN=<supabase access token> node report_production.mjs spec.json
//   ... | node report_production.mjs -            # spec on stdin
//
// Behind a proxy (Claude Code web sessions), prefix with NODE_USE_ENV_PROXY=1.
//
// Spec:
//   {
//     "date": "2026-08-24",                  // production date, YYYY-MM-DD
//     "event_at": "2026-08-24T09:00:00Z",    // optional; default noon Israel, never future
//     "dry_run": true,                       // preview only, no writes at all
//     "lines": [
//       { "item_id": "FG-NAM-1L", "qty": 502, "uom": "BOTTLE",
//         "base_bom_head_id": "BOM-BASE-NAM-REG", "fill_l_per_unit": 1,
//         "scrap_qty": 0, "notes": null }
//     ]
//   }
//
// Exit codes: 0 = done (or clean dry run), 2 = blocked before any write,
// 3 = failed partway (the summary says exactly what landed).

import { readFileSync } from 'node:fs';

const BASE = process.env.GT_API_BASE ?? 'https://gt-factory-os-api-production.up.railway.app';
const TOKEN = process.env.GT_API_TOKEN;

const OPEN_PLAN_STATUS = new Set(['planned', 'in_production']);
const blockers = [];
const notes = [];

// ---------------------------------------------------------------------------
// HTTP
// ---------------------------------------------------------------------------

async function call(method, path, body) {
  let res;
  try {
    res = await fetch(`${BASE}${path}`, {
      method,
      headers: {
        Authorization: `Bearer ${TOKEN}`,
        ...(body ? { 'Content-Type': 'application/json' } : {}),
      },
      ...(body ? { body: JSON.stringify(body) } : {}),
    });
  } catch (err) {
    throw new Error(
      `${method} ${path} could not reach ${BASE}: ${err.message}` +
        (process.env.HTTPS_PROXY ? ' (behind a proxy — rerun with NODE_USE_ENV_PROXY=1)' : ''),
    );
  }
  const text = await res.text();
  let parsed = text;
  try {
    parsed = JSON.parse(text);
  } catch {
    /* keep raw text */
  }
  if (!res.ok) {
    const err = new Error(`${method} ${path} -> ${res.status}: ${text.slice(0, 600)}`);
    err.status = res.status;
    err.body = parsed;
    throw err;
  }
  return parsed;
}

// ---------------------------------------------------------------------------
// Spec
// ---------------------------------------------------------------------------

function loadSpec() {
  const arg = process.argv[2];
  if (!arg) throw new Error('pass a spec file path, or "-" to read the spec from stdin');
  const raw = arg === '-' ? readFileSync(0, 'utf8') : readFileSync(arg, 'utf8');
  const spec = JSON.parse(raw);

  if (!/^\d{4}-\d{2}-\d{2}$/.test(spec.date ?? '')) throw new Error('spec.date must be YYYY-MM-DD');
  if (!Array.isArray(spec.lines) || spec.lines.length === 0) throw new Error('spec.lines must be a non-empty array');

  for (const line of spec.lines) {
    if (!line.item_id) throw new Error('every line needs an item_id');
    if (!(Number(line.qty) > 0)) throw new Error(`line ${line.item_id}: qty must be > 0`);
    if (!line.uom) throw new Error(`line ${line.item_id}: uom is required and must equal items.sales_uom`);
    if (line.base_bom_head_id && !(Number(line.fill_l_per_unit) > 0)) {
      throw new Error(`line ${line.item_id}: fill_l_per_unit is required when base_bom_head_id is set`);
    }
  }
  const ids = spec.lines.map((l) => l.item_id);
  if (new Set(ids).size !== ids.length) throw new Error('the same item appears twice in spec.lines');

  return spec;
}

// Reporting is retroactive more often than not, so default to midday on the
// production date. The report handler rejects a future event_at, which would
// otherwise bite on same-day reports filed in the morning.
function resolveEventAt(spec) {
  if (spec.event_at) return spec.event_at;
  const midday = new Date(`${spec.date}T12:00:00+03:00`);
  const safeNow = new Date(Date.now() - 60_000);
  return (midday > safeNow ? safeNow : midday).toISOString();
}

const round8 = (n) => Math.round(n * 1e8) / 1e8;

// ---------------------------------------------------------------------------
// Plans — reuse an open row for the day when there is one, and bring it in
// line with what was actually made. Silently creating a second plan next to an
// existing one is what leaves the day's plan looking like it was produced
// twice.
// ---------------------------------------------------------------------------

async function ensurePlans(spec) {
  const list = await call('GET', `/api/v1/queries/production-plan?from=${spec.date}&to=${spec.date}&include_completed=true`);
  const rows = list.rows ?? [];

  const batches = new Map(); // base_bom_head_id -> lines[]
  const singles = [];
  for (const line of spec.lines) {
    if (line.base_bom_head_id) {
      if (!batches.has(line.base_bom_head_id)) batches.set(line.base_bom_head_id, []);
      batches.get(line.base_bom_head_id).push(line);
    } else {
      singles.push(line);
    }
  }

  const planOf = new Map(); // item_id -> plan_id
  const actions = [];

  for (const [baseId, lines] of batches) {
    const open = rows.filter((r) => r.is_base_batch && r.base_bom_head_id === baseId && OPEN_PLAN_STATUS.has(r.status));
    if (open.length > 1) {
      blockers.push(
        `${spec.date}: ${open.length} open base-batch plans for ${baseId} (${open.map((r) => r.plan_id).join(', ')}). ` +
          'Cancel the duplicates in the portal first — reporting against one of them would leave the other looking unproduced.',
      );
      continue;
    }

    if (open.length === 1) {
      const plan = open[0];
      // pack_manifest edits replace the split wholesale, so send the existing
      // lines back untouched and override only what was actually reported.
      const merged = new Map(plan.pack_manifest.map((m) => [m.item_id, Number(m.qty)]));
      let changed = false;
      for (const line of lines) {
        if (merged.get(line.item_id) !== line.qty) changed = true;
        merged.set(line.item_id, line.qty);
      }
      if (changed && !spec.dry_run) {
        await call('PATCH', `/api/v1/mutations/production-plan/${plan.plan_id}`, {
          pack_manifest: [...merged].map(([item_id, qty]) => ({ item_id, qty })),
        });
      }
      actions.push({ kind: changed ? 'plan_split_updated' : 'plan_reused', plan_id: plan.plan_id, base_bom_head_id: baseId });

      // batch_size_l is fixed at creation and cannot be patched alongside the
      // split. It never drives consumption — a PACK run consumes against its
      // own bottles — so a mismatch is worth saying out loud and nothing more.
      const litres = round8([...merged].reduce((sum, [id, qty]) => {
        const fill = lines.find((l) => l.item_id === id)?.fill_l_per_unit
          ?? Number(plan.pack_manifest.find((m) => m.item_id === id)?.fill_l_per_unit ?? 0);
        return sum + qty * Number(fill || 0);
      }, 0));
      const planned = Number(plan.planned_qty);
      if (litres > 0 && Math.abs(litres - planned) > 0.5) {
        notes.push(`plan ${plan.plan_id}: split now totals ${litres} L against a ${planned} L batch (consumption is unaffected).`);
      }
      for (const line of lines) planOf.set(line.item_id, plan.plan_id);
      continue;
    }

    const batchSizeL = round8(lines.reduce((sum, l) => sum + l.qty * Number(l.fill_l_per_unit), 0));
    if (spec.dry_run) {
      actions.push({ kind: 'plan_would_be_created', base_bom_head_id: baseId, batch_size_l: batchSizeL });
      continue;
    }
    const created = await call('POST', '/api/v1/mutations/production-plan', {
      plan_type: 'base_batch',
      idempotency_key: `PRODPLAN:${spec.date}:${baseId}`,
      plan_date: spec.date,
      base_bom_head_id: baseId,
      batch_size_l: batchSizeL,
      pack_manifest: lines.map((l) => ({ item_id: l.item_id, qty: l.qty })),
      notes: spec.plan_note ?? `Production reported for ${spec.date}.`,
    });
    actions.push({ kind: 'plan_created', plan_id: created.plan_id, base_bom_head_id: baseId, batch_size_l: batchSizeL });
    for (const line of lines) planOf.set(line.item_id, created.plan_id);
  }

  for (const line of singles) {
    const open = rows.filter((r) => !r.is_base_batch && r.item_id === line.item_id && OPEN_PLAN_STATUS.has(r.status));
    if (open.length > 1) {
      blockers.push(
        `${spec.date}: ${open.length} open plans for ${line.item_id} (${open.map((r) => r.plan_id).join(', ')}). ` +
          'Cancel the duplicates in the portal first.',
      );
      continue;
    }

    if (open.length === 1) {
      const plan = open[0];
      const changed = Number(plan.planned_qty) !== line.qty;
      if (changed && !spec.dry_run) {
        await call('PATCH', `/api/v1/mutations/production-plan/${plan.plan_id}`, { planned_qty: line.qty });
      }
      actions.push({ kind: changed ? 'plan_qty_updated' : 'plan_reused', plan_id: plan.plan_id, item_id: line.item_id });
      planOf.set(line.item_id, plan.plan_id);
      continue;
    }

    if (spec.dry_run) {
      actions.push({ kind: 'plan_would_be_created', item_id: line.item_id, qty: line.qty });
      continue;
    }
    const created = await call('POST', '/api/v1/mutations/production-plan', {
      plan_type: 'production',
      idempotency_key: `PRODPLAN:${spec.date}:${line.item_id}`,
      plan_date: spec.date,
      item_id: line.item_id,
      planned_qty: line.qty,
      uom: line.uom,
      notes: spec.plan_note ?? `Production reported for ${spec.date}.`,
    });
    actions.push({ kind: 'plan_created', plan_id: created.plan_id, item_id: line.item_id });
    planOf.set(line.item_id, created.plan_id);
  }

  return { actions, planOf };
}

// ---------------------------------------------------------------------------
// Runs + preview gate
// ---------------------------------------------------------------------------

async function resolveRuns(spec, planOf) {
  // This read is what materializes the runs a plan implies, so it has to come
  // after the plans exist.
  const today = await call('GET', `/api/v1/queries/production-runs/today?date=${spec.date}`);
  const targets = [];

  for (const line of spec.lines) {
    const planId = planOf.get(line.item_id);
    if (!planId) continue; // blocked earlier
    const run = (today.rows ?? []).find(
      (r) => r.plan_id === planId && r.item_id === line.item_id && (r.stage === 'PACK' || r.stage === 'SINGLE'),
    );
    if (!run) {
      blockers.push(`no PACK/SINGLE run materialized for ${line.item_id} on plan ${planId} — check the plan's shape in the portal.`);
      continue;
    }
    if (run.status === 'REPORTED') {
      notes.push(`${line.item_id}: run ${run.run_id} is already REPORTED — left alone.`);
      continue;
    }
    if (run.status === 'CANCELLED') {
      blockers.push(`${line.item_id}: run ${run.run_id} is CANCELLED and cannot be reported.`);
      continue;
    }
    targets.push({ line, run, plan_id: planId });
  }
  return targets;
}

async function previewAll(targets) {
  for (const t of targets) {
    t.preview = await call(
      'GET',
      `/api/v1/queries/production-runs/${t.run.run_id}/consumption-preview?output_qty=${t.line.qty}`,
    );
    t.decisions = [];

    // These two counters are the whole gate. A negative projection means the
    // material is not there on paper, and a flagged line means the collected
    // quantity is off-recipe by 2x or more — both need a human to say which
    // number is the true one before anything hits the ledger.
    //
    // Tom can overrule the negative one per line: the material really did leave
    // the shelf even though the projection says there is none, usually because a
    // receipt was never booked. That take posts in full and the component sits
    // negative until the receipt lands, which is the honest record — so say
    // loudly which components it applied to.
    const negatives = t.preview.lines.filter((l) => l.would_go_negative);
    if (negatives.length > 0) {
      if (t.line.confirm_negative) {
        for (const l of negatives) t.decisions.push({ component_id: l.component_id, source: l.source, confirm_negative: true });
        notes.push(
          `${t.line.item_id}: posting against an empty projection for ` +
            negatives.map((l) => `${l.component_id} (want ${l.wanted_qty}, on hand ${l.on_hand_qty} → ${l.on_hand_after_qty})`).join('; ') +
            ' — confirmed, these will read negative until a receipt lands.',
        );
      } else {
        blockers.push(
          `${t.line.item_id}: ${negatives.length} component(s) would go negative — ` +
            negatives.map((l) => `${l.component_id} (want ${l.wanted_qty}, on hand ${l.on_hand_qty})`).join('; ') +
            '. Book the missing receipt, or set confirm_negative on this line.',
        );
      }
    }

    const unexplained = t.preview.lines.filter((l) => l.needs_explanation);
    if (unexplained.length > 0) {
      if (t.line.explanation) {
        for (const l of unexplained) {
          const existing = t.decisions.find((d) => d.component_id === l.component_id && d.source === l.source);
          if (existing) existing.explanation = t.line.explanation;
          else t.decisions.push({ component_id: l.component_id, source: l.source, confirm_negative: false, explanation: t.line.explanation });
        }
        notes.push(`${t.line.item_id}: off-recipe on ${unexplained.map((l) => l.component_id).join(', ')} — reason recorded.`);
      } else {
        blockers.push(
          `${t.line.item_id}: collected quantities differ sharply from the recipe for ` +
            `${unexplained.map((l) => l.component_id).join(', ')} — set explanation on this line with the reason.`,
        );
      }
    }
  }
}

// ---------------------------------------------------------------------------
// Report + close
// ---------------------------------------------------------------------------

async function reportAll(spec, targets, eventAt) {
  const posted = [];
  for (const t of targets) {
    const res = await call('POST', `/api/v1/mutations/production-runs/${t.run.run_id}/report`, {
      idempotency_key: `PRODREPORT:${spec.date}:${t.line.item_id}:${t.line.qty}`,
      event_at: eventAt,
      output_qty: t.line.qty,
      scrap_qty: Number(t.line.scrap_qty ?? 0),
      output_uom: t.line.uom,
      consumption_decisions: t.decisions ?? [],
      ...(t.line.qc_brix != null ? { qc_brix: t.line.qc_brix } : {}),
      ...(t.line.qc_ph != null ? { qc_ph: t.line.qc_ph } : {}),
      notes: t.line.notes ?? `Production reported for ${spec.date}.`,
    });
    posted.push({ item_id: t.line.item_id, plan_id: t.plan_id, ...res });
  }
  return posted;
}

// A base-batch plan takes several pack reports, so it never completes through
// the 1:1 path item-linked plans use. Left alone it sits "planned" forever and
// every later report of the day looks like it is missing one.
async function closeFinishedBatches(spec, planIds) {
  const closed = [];
  if (planIds.size === 0) return closed;
  const today = await call('GET', `/api/v1/queries/production-runs/today?date=${spec.date}`);
  const list = await call('GET', `/api/v1/queries/production-plan?from=${spec.date}&to=${spec.date}&include_completed=true`);

  for (const planId of planIds) {
    const plan = (list.rows ?? []).find((r) => r.plan_id === planId);
    if (!plan?.is_base_batch || !OPEN_PLAN_STATUS.has(plan.status)) continue;
    const packRuns = (today.rows ?? []).filter((r) => r.plan_id === planId && r.stage === 'PACK');
    const covered = packRuns.length > 0 && packRuns.every((r) => r.status === 'REPORTED');
    if (!covered) {
      notes.push(`plan ${planId} stays open — ${packRuns.filter((r) => r.status !== 'REPORTED').map((r) => r.item_id).join(', ')} not reported yet.`);
      continue;
    }
    try {
      const res = await call('POST', `/api/v1/mutations/production-plan/${planId}/close-batch`, {
        closure_note: `All pack SKUs reported for ${spec.date}.`,
      });
      closed.push({ plan_id: planId, coverage: res.coverage });
    } catch (err) {
      notes.push(`plan ${planId}: could not close the batch (${err.message}). The reports are posted; close it in the portal.`);
    }
  }
  return closed;
}

// ---------------------------------------------------------------------------
// Output
// ---------------------------------------------------------------------------

function printPreview(targets) {
  for (const t of targets) {
    console.log(`\n${t.line.item_id}  ${t.line.qty} ${t.line.uom}   run ${t.run.run_id} [${t.run.status}]`);
    for (const l of t.preview.lines) {
      const flag = l.would_go_negative ? '  ⚠ NEGATIVE' : l.needs_explanation ? '  ⚠ off-recipe' : '';
      console.log(
        `   -${String(l.wanted_qty).padStart(14)} ${String(l.uom).padEnd(5)} ${l.component_id.padEnd(26)}` +
          ` on hand ${String(l.on_hand_qty).padStart(14)} → ${String(l.on_hand_after_qty).padStart(14)} [${l.basis}]${flag}`,
      );
    }
  }
}

function printPosted(posted) {
  for (const p of posted) {
    console.log(`\n${p.item_id}: +${p.output_qty} ${p.output_uom}   ledger ${p.output_ledger_row_id}${p.idempotent_replay ? '  (replay)' : ''}`);
    console.log(`   submission ${p.submission_id}   plan ${p.linked_plan_id ?? p.plan_id}`);
    for (const c of p.consumed) {
      console.log(`   -${String(c.consumed_qty).padStart(14)} ${String(c.uom).padEnd(5)} ${c.component_id.padEnd(26)} [${c.basis}]`);
    }
    for (const s of p.shortfalls) {
      console.log(`   ⚠ shortfall ${s.component_id}: wanted ${s.picked_qty}, available ${s.available_qty}, took ${s.consumed_qty}`);
    }
  }
}

// ---------------------------------------------------------------------------

async function main() {
  if (!TOKEN) {
    console.error('GT_API_TOKEN is required — a Supabase access token for the reporting user.');
    process.exit(2);
  }
  const spec = loadSpec();
  const eventAt = resolveEventAt(spec);

  const health = await call('GET', '/health');
  if (!health?.ok) throw new Error(`API health check failed: ${JSON.stringify(health)}`);

  const { actions, planOf } = await ensurePlans(spec);
  const targets = blockers.length > 0 ? [] : await resolveRuns(spec, planOf);
  if (targets.length > 0) await previewAll(targets);

  const summary = { date: spec.date, event_at: eventAt, dry_run: !!spec.dry_run, plan_actions: actions, notes };

  if (blockers.length > 0) {
    console.log('BLOCKED — nothing was reported.\n');
    for (const b of blockers) console.log(`  • ${b}`);
    if (targets.length > 0) printPreview(targets);
    console.log(`\n${JSON.stringify({ ...summary, status: 'blocked', blockers }, null, 2)}`);
    process.exit(2);
  }

  if (spec.dry_run) {
    console.log(`DRY RUN — ${spec.date}, event_at ${eventAt}. No writes.`);
    printPreview(targets);
    for (const n of notes) console.log(`\n  note: ${n}`);
    console.log(`\n${JSON.stringify({ ...summary, status: 'dry_run' }, null, 2)}`);
    return;
  }

  let posted = [];
  try {
    posted = await reportAll(spec, targets, eventAt);
  } catch (err) {
    console.log('PARTIAL — some reports posted before the failure.\n');
    printPosted(posted);
    console.error(`\nfailed: ${err.message}`);
    console.log(`\n${JSON.stringify({ ...summary, status: 'partial', posted: posted.map((p) => p.submission_id), error: err.message }, null, 2)}`);
    process.exit(3);
  }

  const closed = await closeFinishedBatches(spec, new Set(posted.map((p) => p.linked_plan_id ?? p.plan_id).filter(Boolean)));

  console.log(`REPORTED — ${spec.date}, event_at ${eventAt}`);
  printPosted(posted);
  for (const c of closed) console.log(`\nbatch plan ${c.plan_id} closed.`);
  for (const n of notes) console.log(`\n  note: ${n}`);
  console.log(`\n${JSON.stringify({
    ...summary,
    status: 'reported',
    posted: posted.map((p) => ({
      item_id: p.item_id,
      submission_id: p.submission_id,
      output_ledger_row_id: p.output_ledger_row_id,
      output_qty: p.output_qty,
      output_uom: p.output_uom,
      consumed_count: p.consumed.length,
      shortfalls: p.shortfalls.length,
    })),
    closed_batches: closed.map((c) => c.plan_id),
  }, null, 2)}`);
}

main().catch((err) => {
  console.error(err.message ?? err);
  process.exit(3);
});
