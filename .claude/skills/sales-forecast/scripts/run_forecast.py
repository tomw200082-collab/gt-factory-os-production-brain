#!/usr/bin/env python3
"""One run of the Sales forecast: backtest, forecast, report, draft SQL.

  python3 run_forecast.py --shopify sku_month.json --skumap sku_map.psv \
      --last-full 2026-08 --partial 2026-09 --partial-frac 0.9 \
      --start 2026-10 --months 6 --supersedes <published version uuid> \
      --actor <app user uuid> --out out/

Writes out/forecast.csv, out/report.md, out/flags.json, out/draft.sql
and out/publish.sql. draft.sql opens a DRAFT and discards the skill's own stale
drafts (--discard). publish.sql runs automatically only when flags.json says
auto_publish (D40); otherwise after Tom's yes (SKILL.md).
"""
import argparse
import collections
import csv
import json
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(__file__))
import engine as E  # noqa: E402

p = argparse.ArgumentParser()
p.add_argument('--shopify', required=True)
p.add_argument('--skumap', required=True)
p.add_argument('--aliases', default='{"GTCC-NM-SAN-3.85L": "GTCC-NON-SAN-3.85L"}')
p.add_argument('--history-start', default='2024-07')
p.add_argument('--last-full', required=True, help='last complete month, YYYY-MM')
p.add_argument('--partial', default=None, help='current partial month, YYYY-MM')
p.add_argument('--partial-frac', type=float, default=1.0)
p.add_argument('--start', required=True, help='first forecast month, YYYY-MM')
p.add_argument('--months', type=int, default=6)
p.add_argument('--exclude', default='2026-04', help='comma list of months not scored (known data breaks)')
p.add_argument('--supersedes', default=None)
p.add_argument('--copy-months', default='', help='comma list of months copied unchanged from --supersedes')
p.add_argument('--actor', default=None)
p.add_argument('--published', default=None,
               help='item|YYYY-MM|qty lines of the published version being revised (flag check)')
p.add_argument('--discard', default='', help="comma list of this skill's stale draft version ids to discard")
p.add_argument('--out', required=True)
a = p.parse_args()

# Unmapped SKUs Tom has ruled out of the forecast: listed as known, never re-asked.
KNOWN_OUT = {
    'GT-HIB-LOW-0.3L': 'made to order (Tom, 2026-09-28)',
    'GT-LUI-LOW-0.3L': 'made to order (Tom, 2026-09-28)',
    'GT-CHA-LOW-0.3L': 'made to order (Tom, 2026-09-28)',
    'GT-SEN-LOW-0.3L': 'made to order (Tom, 2026-09-28)',
}
KNOWN_OUT_PREFIXES = {('GTMX-MUZ-', 'GTCC-MUZ-'): 'Muza private label, made to order (planning.demand.mto.*)'}


def known_out(sku):
    if sku in KNOWN_OUT:
        return KNOWN_OUT[sku]
    for prefixes, why in KNOWN_OUT_PREFIXES.items():
        if sku.startswith(prefixes):
            return why
    return None
os.makedirs(a.out, exist_ok=True)

raw, meta, unmapped = E.load(a.shopify, a.skumap, json.loads(a.aliases))
months = E.month_range(a.history_start, a.last_full)
series, flags = E.clean(raw, months)
exclude = tuple(x for x in a.exclude.split(',') if x)

# ---- backtest: origins from month 12 of history to 6 months before the last full month
origins = E.month_range(E.month_add(a.history_start, 12), E.month_add(a.last_full, -6))
bt = {name: E.backtest(series, meta, fn, origins, 6, exclude)
      for name, fn in (('combo (used)', E.m_combo),
                       ('research recipe: SES + damped ETS + Theta', E.m_comb_research),
                       ('benchmark: 12-month average', E.m_avg12),
                       ('benchmark: same month last year', E.m_snaive),
                       ('benchmark: last 3 months', E.m_naive3))}
best_bench = min(r['wape'] for n, r in bt.items() if n.startswith('benchmark'))
passed = bt['combo (used)']['wape'] < best_bench

# ---- forecast
H = E.month_range(a.start, E.month_add(a.start, a.months - 1))
steps = len(E.month_range(E.month_add(a.last_full, 1), H[-1]))
f = E.m_combo(series, meta, a.last_full, steps)
new_items = sorted(it for it in series if len(E.hist(series[it], a.last_full)) < 3)
for it in new_items:
    lvl = E.new_item_level(raw, it, a.last_full, a.partial, a.partial_frac)
    for t in H:
        f[it][t] = lvl
rows = sorted(((it, t, round(f[it][t])) for it in f for t in H), key=lambda r: (r[0], r[1]))
with open(os.path.join(a.out, 'forecast.csv'), 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['item_id', 'month', 'qty'])
    w.writerows(rows)

# ---- report
tot = collections.Counter()
for it, t, q in rows:
    tot[t] += q
big_unmapped = collections.Counter()
for (sku, m), q in unmapped.items():
    if m >= E.month_add(a.last_full, -5):
        big_unmapped[sku] += q
lines = [f'# Sales forecast run: history {a.history_start} to {a.last_full}, forecast {H[0]} to {H[-1]}', '']
lines += ['## Backtest (rolling origin, 6 months ahead, established items)', '',
          '| Method | Item WAPE | Bias | Monthly-total WAPE | WAPE by horizon 1..6 |', '|---|---|---|---|---|']
for name, r in bt.items():
    lines.append(f"| {name} | {r['wape']:.1%} | {r['bias']:+.1%} | {r['total_wape']:.1%} | "
                 + ' / '.join(f'{v:.0%}' for v in r['by_h'].values()) + ' |')
lines += ['', f"Test: the combo's item WAPE {bt['combo (used)']['wape']:.1%} against the best benchmark {best_bench:.1%}: "
          + ('PASS' if passed else 'FAIL, no draft (SKILL.md, Rules)'), '']
lines += [f"Actual/forecast ratio per item-month, p10 / p50 / p90 by horizon: {bt['combo (used)']['ratio_p10_p50_p90']}", '']
lines += ['## Totals per month (internal units)', '', '| ' + ' | '.join(H) + ' |', '|' + '---|' * len(H),
          '| ' + ' | '.join(f'{tot[t]:,}' for t in H) + ' |', '']
# ---- lines flagged against the published version (Tom's rule, 2026-09-28):
# over the overlapping months, a change above 15% (A), 25% (B) or 40% (C)
# and above 50 units. ABC = cumulative share of the new forecast (80/95%).
flagged = []
if a.published:
    old = collections.defaultdict(dict)
    for line in open(a.published):
        if line.strip():
            it, m, q = line.strip().split('|')
            old[it][m] = float(q)
    overlap = [t for t in H if any(t in v for v in old.values())]
    if overlap:
        new_tot = {it: sum(f[it][t] for t in overlap) for it in f}
        old_tot = {it: sum(v.get(t, 0.0) for t in overlap) for it, v in old.items()}
        total, cum, cls = sum(new_tot.values()) or 1.0, 0.0, {}
        for it, q in sorted(new_tot.items(), key=lambda x: -x[1]):
            cum += q
            cls[it] = 'A' if cum / total <= 0.8 else ('B' if cum / total <= 0.95 else 'C')
        limit = {'A': 0.15, 'B': 0.25, 'C': 0.40}
        for it in sorted(set(new_tot) | set(old_tot)):
            n, o, c = new_tot.get(it, 0.0), old_tot.get(it, 0.0), cls.get(it, 'C')
            if abs(n - o) > 50 and (o == 0 or abs(n - o) / o > limit[c]):
                flagged.append((it, c, round(o), round(n)))
    lines += [f'## Lines past their limit against the published version ({", ".join(overlap) or "no overlapping months"})', '']
    lines += [f'- {it} (class {c}): {o:,} → {n:,}' for it, c, o, n in flagged] or ['- none']
    lines += ['', 'Publish automatically: ' + ('no, the flagged lines wait for Tom' if flagged else 'yes (nothing flagged)'), '']
auto = bool(a.published) and not flagged
json.dump({'flagged': flagged, 'auto_publish': auto}, open(os.path.join(a.out, 'flags.json'), 'w'))

lines += ['## Needs a judgement', '']
for it in new_items:
    lines.append(f"- New item {it}: under 3 clean months; {round(f[it][H[0]])}/month = units since first sale / months since.")
for sku, q in big_unmapped.most_common():
    if q >= 100 and not known_out(sku):
        lines.append(f"- Unmapped Shopify SKU {sku or '(no SKU)'}: {q:,} units in the last 6 months, outside the forecast.")
lines += ['', '## Known out (ruled by Tom)', '']
for sku, q in big_unmapped.most_common():
    if q >= 100 and known_out(sku):
        lines.append(f"- {sku}: {q:,} units in the last 6 months; {known_out(sku)}.")
lines += ['', '## Cleaning', '']
for it, fl in sorted(flags.items()):
    lines.append(f'- {it}: ' + '; '.join(fl))
report = '\n'.join(lines) + '\n'
open(os.path.join(a.out, 'report.md'), 'w').write(report)

# ---- draft SQL (opens a draft; publish.sql publishes it). No draft when the test fails.
if a.supersedes and a.actor and not passed:
    print('backtest FAIL: combo does not beat the best benchmark; no draft written')
if a.supersedes and a.actor and passed:
    vid = str(uuid.uuid4())
    copy = [m for m in a.copy_months.split(',') if m]
    tag = f"fc-{H[0]}-{H[-1]}-{vid[:8]}"
    sql = [f"-- Sales forecast draft {H[0]}..{H[-1]} (sales-forecast skill). DRAFT only; publish.sql publishes it.",
           "begin;",
           f"select set_config('audit.actor_user_id','{a.actor}',true), set_config('audit.actor_snapshot','Claude (sales-forecast)',true);",
           "insert into private_core.forecast_versions (version_id, site_id, cadence, horizon_start_at, horizon_weeks, status,"
           " created_by_user_id, created_by_snapshot, supersedes_version_id, notes) values",
           f"  ('{vid}','GT-MAIN','monthly','{(copy[0] if copy else H[0])}-01',{4 * (len(H) + len(copy)) + 2},'draft','{a.actor}',"
           f"'Claude (sales-forecast)','{a.supersedes}', $n$Sales forecast {H[0]}..{H[-1]}: combo of level, SES and Theta on "
           f"working-day and seasonally adjusted Shopify units. See the skill's references/method.md.$n$);"]
    for m in copy:
        sql.append(f"insert into private_core.forecast_lines (version_id, item_id, period_bucket_key, forecast_quantity)"
                   f" select '{vid}', item_id, period_bucket_key, forecast_quantity from private_core.forecast_lines"
                   f" where version_id='{a.supersedes}' and period_bucket_key='{m}-01';")
    vals = ',\n'.join(f"  ('{vid}','{it}','{t}-01',{q})" for it, t, q in rows)
    def sub(ft, key, payload):
        body = json.dumps(payload).replace("'", "''")
        return ("insert into private_core.form_submissions (form_type, idempotency_key, submitted_by, submitted_at, event_at,"
                f" status, posted_at, posted_by, site_id, raw_payload) values ('{ft}','{key}','{a.actor}',now(),now(),'posted',"
                f"now(),'{a.actor}','GT-MAIN','{body}'::jsonb);")
    for d in [x for x in a.discard.split(',') if x]:
        sql[3:3] = [sub('forecast_discard', f'{tag}-discard-{d[:8]}', {'version_id': d, 'reason':
                        'stale draft of an earlier sales-forecast run, never approved; replaced by ' + vid}),
                    "update private_core.forecast_versions set status='discarded', discarded_by_user_id="
                    f"'{a.actor}', discarded_by_snapshot='Claude (sales-forecast)', discarded_at=now()"
                    f" where version_id='{d}' and status='draft' and created_by_snapshot='Claude (sales-forecast)';"]
    sql += ["insert into private_core.forecast_lines (version_id, item_id, period_bucket_key, forecast_quantity) values", vals + ';',
            sub('forecast_open_draft', f'{tag}-opendraft',
                {'version_id': vid, 'cadence': 'monthly', 'supersedes_version_id': a.supersedes,
                 'buckets': [f'{m}-01(copied)' for m in copy] + [f'{t}-01' for t in H],
                 'n_items': len({r[0] for r in rows}), 'source': 'sales-forecast skill',
                 'flagged': [dict(zip(('item_id', 'class', 'published', 'new'), e)) for e in flagged],
                 'auto_publish': auto, 'report_md': report}),
            "commit;"]
    open(os.path.join(a.out, 'draft.sql'), 'w').write('\n'.join(sql) + '\n')
    who = 'Auto-publish, nothing flagged (D40)' if auto else 'Tom'
    pub = [f"-- Publish the draft: {'automatic, nothing flagged (D40)' if auto else 'after Tom approves'}. One transaction.",
           "begin;",
           f"select set_config('audit.actor_user_id','{a.actor}',true), set_config('audit.actor_snapshot','{who}',true);",
           sub('forecast_save', f'{tag}-save', {'version_id': vid, 'freeze_override_reason':
               'fortnightly re-forecast (D39); the current month is copied unchanged', 'actor_role': 'admin'}),
           f"update private_core.forecast_versions set status='published', published_by_user_id='{a.actor}',"
           f" published_by_snapshot='{who}', published_at=now() where version_id='{vid}' and status='draft';",
           f"update private_core.forecast_versions set status='superseded', superseded_at=now()"
           f" where version_id='{a.supersedes}' and status='published';",
           sub('forecast_publish', f'{tag}-publish', {'version_id': vid, 'superseded_version_id': a.supersedes,
                                                     'approval': who}),
           "commit;"]
    open(os.path.join(a.out, 'publish.sql'), 'w').write('\n'.join(pub) + '\n')
    print('draft version_id', vid)

print(open(os.path.join(a.out, 'report.md')).read())
