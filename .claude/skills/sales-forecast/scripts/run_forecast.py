#!/usr/bin/env python3
"""One run of the Sales forecast: backtest, forecast, report, draft SQL.

  python3 run_forecast.py --shopify sku_month.json --skumap sku_map.psv \
      --last-full 2026-08 --partial 2026-09 --partial-frac 0.9 \
      --start 2026-10 --months 6 --supersedes <published version uuid> \
      --actor <app user uuid> --out out/

Writes out/forecast.csv, out/report.md and out/draft.sql. The SQL opens a
DRAFT version only; publishing is a separate, approved step (SKILL.md).
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
p.add_argument('--out', required=True)
a = p.parse_args()
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
lines += ['## Needs a judgement', '']
for it in new_items:
    lines.append(f"- New item {it}: under 3 clean months; {round(f[it][H[0]])}/month = units since first sale / months since.")
for sku, q in big_unmapped.most_common():
    if q >= 100:
        lines.append(f"- Unmapped Shopify SKU {sku or '(no SKU)'}: {q:,} units in the last 6 months, outside the forecast.")
lines += ['', '## Cleaning', '']
for it, fl in sorted(flags.items()):
    lines.append(f'- {it}: ' + '; '.join(fl))
open(os.path.join(a.out, 'report.md'), 'w').write('\n'.join(lines) + '\n')

# ---- draft SQL (opens a draft; never publishes). No draft when the test fails.
if a.supersedes and a.actor and not passed:
    print('backtest FAIL: combo does not beat the best benchmark; no draft written')
if a.supersedes and a.actor and passed:
    vid = str(uuid.uuid4())
    copy = [m for m in a.copy_months.split(',') if m]
    sql = [f"-- Sales forecast draft {H[0]}..{H[-1]} (sales-forecast skill). DRAFT only; publish after approval.",
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
    tag = f"fc-{H[0]}-{H[-1]}-{vid[:8]}"
    sub = ("insert into private_core.form_submissions (form_type, idempotency_key, submitted_by, submitted_at, event_at,"
           " status, posted_at, posted_by, site_id, raw_payload) values ('{ft}','{key}','{actor}',now(),now(),'posted',now(),"
           "'{actor}','GT-MAIN','{payload}'::jsonb);")
    sql += ["insert into private_core.forecast_lines (version_id, item_id, period_bucket_key, forecast_quantity) values", vals + ';',
            sub.format(ft='forecast_open_draft', key=f'{tag}-opendraft', actor=a.actor,
                       payload=json.dumps({'version_id': vid, 'cadence': 'monthly', 'supersedes_version_id': a.supersedes,
                                           'buckets': [f'{m}-01(copied)' for m in copy] + [f'{t}-01' for t in H],
                                           'n_items': len({r[0] for r in rows}), 'source': 'sales-forecast skill'})),
            "commit;"]
    open(os.path.join(a.out, 'draft.sql'), 'w').write('\n'.join(sql) + '\n')
    pub = ["-- Publish the draft after Tom's approval. One transaction.", "begin;",
           f"select set_config('audit.actor_user_id','{a.actor}',true), set_config('audit.actor_snapshot','Tom',true);",
           sub.format(ft='forecast_save', key=f'{tag}-save', actor=a.actor,
                      payload=json.dumps({'version_id': vid, 'freeze_override_reason':
                                          'fortnightly re-forecast (D39); the current month is copied unchanged', 'actor_role': 'admin'})),
           f"update private_core.forecast_versions set status='published', published_by_user_id='{a.actor}',"
           f" published_by_snapshot='Tom', published_at=now() where version_id='{vid}' and status='draft';",
           f"update private_core.forecast_versions set status='superseded', superseded_at=now()"
           f" where version_id='{a.supersedes}' and status='published';",
           sub.format(ft='forecast_publish', key=f'{tag}-publish', actor=a.actor,
                      payload=json.dumps({'version_id': vid, 'superseded_version_id': a.supersedes})),
           "commit;"]
    open(os.path.join(a.out, 'publish.sql'), 'w').write('\n'.join(pub) + '\n')
    print('draft version_id', vid)

print(open(os.path.join(a.out, 'report.md')).read())
