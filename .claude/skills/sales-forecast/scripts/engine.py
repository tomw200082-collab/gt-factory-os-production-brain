"""GT Sales forecast engine (D39): monthly units per finished-goods item, 6 months ahead.

Method (backtested, see ../references/method.md):
  1. Demand = Shopify net units per SKU per month, mapped to items through
     integration_sku_map (internal units = Shopify units x multiplier).
     MTO items (planning.demand.mto.*), inactive items and unmapped SKUs are out.
  2. Cleaning: negative months, and months below 30% of the median of the
     four neighbouring months, are missing (reversal months, stockouts).
  3. Effective working days (Israel): Sun-Thu = 1, chag = 0, chol hamoed and
     erev chag = 0.5. Everything is modelled per effective day, so a holiday
     that moves between months does not move the seasonality.
  4. Seasonal indices per season group (cold teas, chai, sangria) from the
     group total, ratio to the 12-month mean, shrunk 25% toward 1. Groups with
     under two clean cycles (powders, ODK, other) get none.
  5. Three forecasts of the deseasonalised daily rate, averaged: a weighted
     recent level (last 4 months, weights 0.7^age), SES and Theta
     (Nixtla statsforecast). Averaging is the M4 lesson: combinations beat
     single methods.
  6. Items with under 3 clean months: units since first sale / months since
     first sale, flagged for a judgement.
"""
import collections
import functools
import json
import statistics
import warnings
from datetime import date, timedelta

import numpy as np

# ----------------------------------------------------------------- months
def month_add(m, k):
    y, mo = int(m[:4]), int(m[5:7])
    t = y * 12 + (mo - 1) + k
    return f"{t // 12}-{t % 12 + 1:02d}"


def month_range(a, b):
    out, m = [], a
    while m <= b:
        out.append(m)
        m = month_add(m, 1)
    return out


# ----------------------------------------------------------- season groups
COLD_TEA = {'DETOX', 'FRESH', 'REVIVE', 'CALM', 'ENERGY', 'CONSCIOUSNESS', 'DESERTEA'}
FLAT_GROUPS = {'POWDER', 'ODK', 'OTHER'}


def season_group(item, fam):
    if fam in COLD_TEA:
        return 'COLD_TEA'
    if fam == 'NAMASTEA':
        return 'CHAI'
    if item.startswith(('FG-NM-', 'FG-SAN-')):
        return 'SANGRIA'
    if item.startswith('ADD-ODK'):
        return 'ODK'
    if fam == 'MATCHA' or item.startswith(('ADD-UBE', 'FG-HOJ', 'FG-UBE', 'ADD-HOJ')):
        return 'POWDER'
    return 'OTHER'


# ------------------------------------------------------------------- data
def load(shopify_json, sku_map_psv, aliases=None):
    """shopify_json: ShopifyQL result (month, product_variant_sku, net_items_sold).
    sku_map_psv: external_sku|item_id|mult|supply|status|family|MTO.
    aliases: {extra_sku: mapped_sku} for SKUs that are the same product."""
    d = json.load(open(shopify_json))
    mp = {}
    for line in open(sku_map_psv):
        if not line.strip():
            continue
        s, i, m, sup, st, fam, mto = line.rstrip('\n').split('|')
        mp[s] = dict(item=i, mult=float(m), sup=sup, st=st, fam=fam or 'OTHER', mto=(mto == 'MTO'))
    for extra, same in (aliases or {}).items():
        if same in mp:
            mp[extra] = dict(mp[same])
    raw, meta, unmapped = collections.defaultdict(dict), {}, collections.Counter()
    for mo, sku, q in d['rows']:
        m = mp.get(sku)
        if not m:
            unmapped[(sku, mo[:7])] += int(q)
            continue
        if m['mto'] or m['st'] != 'ACTIVE':
            continue
        k = mo[:7]
        raw[m['item']][k] = raw[m['item']].get(k, 0.0) + int(q) * m['mult']
        meta[m['item']] = dict(fam=m['fam'], sup=m['sup'], group=season_group(m['item'], m['fam']))
    return raw, meta, unmapped


def clean(raw, months):
    """Missing = negative, or under 30% of the median of the four months
    around it. A run of 6+ months without sales is a relaunch: history before
    it is dropped (e.g. a single early test sale years before the launch)."""
    out, flags = {}, collections.defaultdict(list)
    for it, s in raw.items():
        first = next((m for m in months if s.get(m, 0) > 0), None)
        gap, cut = 0, None
        for m in months:
            if first is None or m < first:
                continue
            if s.get(m, 0) > 0:
                if gap >= 6:
                    cut = m
                gap = 0
            else:
                gap += 1
        if cut:
            flags[it].append(f'relaunch: history before {cut} dropped (6+ months without sales)')
            first = cut
        ser = {}
        for m in months:
            if first is None or m < first:
                continue
            v = s.get(m, 0.0)
            ser[m] = None if v < 0 else v
        for m in list(ser):
            nb = [ser.get(month_add(m, k)) for k in (-2, -1, 1, 2)]
            nb = [x for x in nb if x is not None]
            if len(nb) >= 3 and ser[m] is not None:
                med = statistics.median(nb)
                if med >= 20 and ser[m] < 0.3 * med:
                    flags[it].append(f'{m}: {int(ser[m])} vs ~{int(med)} around it, treated as missing')
                    ser[m] = None
        out[it] = ser
    return out, flags


def hist(s, upto):
    return [(m, v) for m, v in sorted(s.items()) if m <= upto and v is not None]


# ------------------------------------------------- effective working days
_EWD = {}


def ewd_table(first='2024-01', last='2028-12'):
    if _EWD:
        return _EWD
    import holidays
    years = range(int(first[:4]), int(last[:4]) + 1)
    pub = holidays.country_holidays('IL', years=years, categories=('public',))
    opt = holidays.country_holidays('IL', years=years, categories=('optional',))
    chag = set(pub)
    half = {d for d, n in opt.items() if 'חול המועד' in n} | {d - timedelta(days=1) for d in pub}
    for m in month_range(first, last):
        y, mo = int(m[:4]), int(m[5:7])
        d, tot = date(y, mo, 1), 0.0
        while d.month == mo:
            if d.isoweekday() in (7, 1, 2, 3, 4):
                tot += 0.0 if d in chag else (0.5 if d in half else 1.0)
            d += timedelta(days=1)
        _EWD[m] = tot
    return _EWD


def group_indices(series, meta, upto, shrink):
    ewd = ewd_table()
    groups = collections.defaultdict(lambda: collections.defaultdict(float))
    for it, s in series.items():
        for m, v in s.items():
            if m <= upto and v is not None:
                groups[meta[it]['group']][m] += v / ewd[m]
    idx = {}
    for g, tot in groups.items():
        if g in FLAT_GROUPS:
            idx[g] = {c: 1.0 for c in range(1, 13)}
            continue
        ms = sorted(tot)
        ratios = collections.defaultdict(list)
        for i, m in enumerate(ms):
            win = [tot[x] for x in ms[max(0, i - 6):i + 6]]
            if len(win) < 9:
                continue
            base = sum(win) / len(win)
            if base > 0:
                ratios[int(m[5:7])].append(tot[m] / base)
        raw = {c: (statistics.mean(ratios[c]) if ratios.get(c) else 1.0) for c in range(1, 13)}
        mu = statistics.mean(raw.values())
        idx[g] = {c: 1 + shrink * (raw[c] / mu - 1) for c in range(1, 13)}
    return idx


# ---------------------------------------------------------------- methods
def m_naive3(series, meta, origin, H, **k):
    out = {}
    for it, s in series.items():
        h = [v for _, v in hist(s, origin)[-3:]]
        lvl = statistics.mean(h) if h else 0.0
        out[it] = {month_add(origin, i): lvl for i in range(1, H + 1)}
    return out


def m_snaive(series, meta, origin, H, **k):
    out, fb = {}, m_naive3(series, meta, origin, H)
    for it, s in series.items():
        out[it] = {}
        for i in range(1, H + 1):
            t = month_add(origin, i)
            ly = month_add(t, -12)
            v = s.get(ly) if ly <= origin else None
            out[it][t] = v if v is not None else fb[it][t]
    return out


def m_level(series, meta, origin, H, shrink=0.75, K=4, decay=0.7, **k):
    ewd, idx = ewd_table(), group_indices(series, meta, origin, shrink)
    out = {}
    for it, s in series.items():
        si = idx.get(meta[it]['group'], {c: 1.0 for c in range(1, 13)})
        h = hist(s, origin)
        if not h:
            out[it] = {month_add(origin, i): 0.0 for i in range(1, H + 1)}
            continue
        num = den = 0.0
        for age, (m, v) in enumerate(reversed(h[-K:])):
            w = decay ** age
            num += w * v / (si[int(m[5:7])] * ewd[m])
            den += w
        r = num / den
        out[it] = {}
        for i in range(1, H + 1):
            t = month_add(origin, i)
            out[it][t] = max(0.0, r * si[int(t[5:7])] * ewd[t])
    return out


def _sf(name):
    from statsforecast.models import (ADIDA, IMAPA, TSB, AutoETS, AutoTheta, CrostonSBA,
                                      SimpleExponentialSmoothingOptimized)
    return {'theta': lambda: AutoTheta(season_length=1),
            'ses': SimpleExponentialSmoothingOptimized,
            'etsd': lambda: AutoETS(season_length=1, model='AAN', damped=True),
            'sba': CrostonSBA,
            'tsb': lambda: TSB(alpha_d=0.1, alpha_p=0.1),
            'imapa': IMAPA,
            'adida': ADIDA}[name]()


def m_sa(series, meta, origin, H, model='ses', shrink=0.75, min_len=6, **k):
    ewd, idx = ewd_table(), group_indices(series, meta, origin, shrink)
    fb = m_level(series, meta, origin, H, shrink=shrink)
    out = {}
    for it, s in series.items():
        si = idx.get(meta[it]['group'], {c: 1.0 for c in range(1, 13)})
        h = hist(s, origin)
        if len(h) < min_len:
            out[it] = fb[it]
            continue
        ysa = np.array([v / (si[int(m[5:7])] * ewd[m]) for m, v in h], dtype=float)
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                fc = _sf(model).forecast(y=ysa, h=H)['mean']
        except Exception:
            out[it] = fb[it]
            continue
        out[it] = {month_add(origin, i): max(0.0, float(fc[i - 1]) * si[int(month_add(origin, i)[5:7])] * ewd[month_add(origin, i)])
                   for i in range(1, H + 1)}
    return out


def adi(s, upto):
    """Average inter-demand interval over the months since first sale
    (missing months are skipped, not zeros). > 1.32 = intermittent (SBC)."""
    h = [v for _, v in hist(s, upto)]
    nz = sum(1 for v in h if v > 0)
    return len(h) / nz if nz else float('inf')


def m_intermittent(series, meta, origin, H, **k):
    """Mean of SBA, TSB and IMAPA on the raw monthly series (no calendar or
    seasonal scaling: these items are too sparse to carry either)."""
    out = {}
    for it, s in series.items():
        h = [v for _, v in hist(s, origin)]
        if len(h) < 3:
            out[it] = {month_add(origin, i): (statistics.mean(h) if h else 0.0) for i in range(1, H + 1)}
            continue
        y = np.array(h, dtype=float)
        fcs = []
        for name in ('sba', 'tsb', 'imapa'):
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore')
                    fcs.append(float(_sf(name).forecast(y=y, h=H)['mean'][0]))
            except Exception:
                pass
        lvl = statistics.mean(fcs) if fcs else float(y.mean())
        out[it] = {month_add(origin, i): max(0.0, lvl) for i in range(1, H + 1)}
    return out


def m_avg12(series, meta, origin, H, **k):
    out = {}
    for it, s in series.items():
        h = [v for _, v in hist(s, origin)[-12:]]
        lvl = statistics.mean(h) if h else 0.0
        out[it] = {month_add(origin, i): lvl for i in range(1, H + 1)}
    return out


def _route(series, origin, cont, inter):
    return {it: (inter[it] if adi(series[it], origin) > 1.32 else cont[it]) for it in series}


def m_combo(series, meta, origin, H, shrink=0.75, **k):
    """Used method: continuous items (ADI <= 1.32) = mean of level, SES and
    Theta on calendar- and seasonally-adjusted data; intermittent items = mean
    of SBA, TSB and IMAPA."""
    fs = [m_level(series, meta, origin, H, shrink=shrink),
          m_sa(series, meta, origin, H, model='ses', shrink=shrink),
          m_sa(series, meta, origin, H, model='theta', shrink=shrink)]
    cont = {it: {t: statistics.mean(f[it][t] for f in fs) for t in fs[0][it]} for it in fs[0]}
    return _route(series, origin, cont, m_intermittent(series, meta, origin, H))


def m_comb_research(series, meta, origin, H, shrink=0.75, **k):
    """The research brief's recipe, for comparison: mean of SES, damped ETS
    and Theta on adjusted data; intermittent route as above."""
    fs = [m_sa(series, meta, origin, H, model='ses', shrink=shrink),
          m_sa(series, meta, origin, H, model='etsd', shrink=shrink),
          m_sa(series, meta, origin, H, model='theta', shrink=shrink)]
    cont = {it: {t: statistics.mean(f[it][t] for f in fs) for t in fs[0][it]} for it in fs[0]}
    return _route(series, origin, cont, m_intermittent(series, meta, origin, H))


# ---------------------------------------------------------------- backtest
def established(series, origin, min_clean=6):
    return {it for it, s in series.items() if len(hist(s, origin)) >= min_clean}


def backtest(series, meta, method, origins, H, exclude_months=(), min_clean=6):
    """Rolling origin; scores items with >= min_clean clean months at the origin.
    wape = sum|F-A| / sum A over item-months; total_wape on monthly totals."""
    abs_e = sum_a = sum_e = tot_err = tot_a = 0.0
    by_h = collections.defaultdict(lambda: [0.0, 0.0])
    ratios = collections.defaultdict(list)
    for o in origins:
        est = established(series, o, min_clean)
        f = method(series, meta, o, H)
        mf, ma = collections.Counter(), collections.Counter()
        for it in est:
            for i, (t, fv) in enumerate(sorted(f[it].items()), start=1):
                a = series[it].get(t)
                if t in exclude_months or a is None:
                    continue
                abs_e += abs(fv - a); sum_a += a; sum_e += fv - a
                by_h[i][0] += abs(fv - a); by_h[i][1] += a
                mf[t] += fv; ma[t] += a
                if fv >= 20:
                    ratios[i].append(a / fv)
        for t in ma:
            tot_err += abs(mf[t] - ma[t]); tot_a += ma[t]
    q = {}
    for h, v in ratios.items():
        v.sort()
        pick = lambda p: v[min(len(v) - 1, int(p * len(v)))]
        q[h] = (round(pick(0.10), 2), round(pick(0.50), 2), round(pick(0.90), 2))
    return dict(wape=round(abs_e / sum_a, 3), bias=round(sum_e / sum_a, 3),
                total_wape=round(tot_err / tot_a, 3),
                by_h={h: round(v[0] / v[1], 3) for h, v in sorted(by_h.items())},
                ratio_p10_p50_p90=dict(sorted(q.items())))


# ----------------------------------------------------------- new items
def new_item_level(raw, it, origin, partial_month=None, partial_frac=1.0):
    s = raw.get(it, {})
    sold = sorted(m for m, v in s.items() if v > 0)
    if not sold:
        return 0.0
    months = month_range(sold[0], origin)
    units = sum(max(0.0, s.get(m, 0.0)) for m in months)
    n = len(months)
    if partial_month:
        units += max(0.0, s.get(partial_month, 0.0))
        n += partial_frac
    return units / n
