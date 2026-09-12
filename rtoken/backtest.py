from .strategy import Params, eligible, build_tranche


def run(closes, p=Params()):
    days = sorted(d for d in closes if len(closes[d]) >= 40)
    first_idx = {}
    for i, d in enumerate(days):
        for s in closes[d]:
            first_idx.setdefault(s, i)

    daily, dates, open_tr = [], [], []
    warm = max(p.vol_window, p.lookback)
    for i in range(warm, len(days) - 1):
        d, nx = days[i], days[i + 1]
        syms = eligible(closes, days, i, first_idx, p)
        if len(syms) < p.min_universe:
            continue
        open_tr.append((i, *build_tranche(closes, days, i, syms, p)))
        open_tr = [t for t in open_tr if i - t[0] < p.hold]

        r = 0.0
        for _, wl, ws in open_tr:
            rl = sum(w * (closes[nx][s] / closes[d][s] - 1) for s, w in wl.items() if s in closes[nx])
            rs = sum(w * (closes[nx][s] / closes[d][s] - 1) for s, w in ws.items() if s in closes[nx])
            r += (rl - rs) / 2 / p.hold          # each tranche is 1/HOLD of capital, 50/50 long/short
        r -= p.cost_bps / 1e4 / p.hold
        daily.append(r)
        dates.append(nx)
    return dates, daily


def split(dates, daily, oos_start=None):
    if oos_start is None:
        k = len(daily) // 2
    else:
        k = next(i for i, d in enumerate(dates) if d >= oos_start)
    return (dates[:k], daily[:k]), (dates[k:], daily[k:])
