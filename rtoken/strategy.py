import math
from dataclasses import dataclass


@dataclass
class Params:
    lookback: int = 5        # sessions
    hold: int = 5            # sessions
    quantile: float = 0.2    # fraction of universe on each side
    seasoning: int = 10      # sessions a symbol must have traded before it is eligible
    min_universe: int = 55   # skip sessions where fewer names are eligible (launch period)
    vol_window: int = 20     # sessions, for inverse-vol weights
    vol_scale: bool = True
    cost_bps: float = 15.0   # round-trip cost per rotated dollar; see liquidity.py for why 15


def eligible(closes, days, i, first_day_idx, p):
    d = days[i]
    need = max(p.vol_window, p.lookback)
    out = []
    for s in closes[d]:
        if first_day_idx[s] > i - p.seasoning:
            continue
        if all(s in closes[days[j]] for j in range(i - need, i + 1)):
            out.append(s)
    return out


def inverse_vol(closes, days, i, syms, p):
    w = {}
    for s in syms:
        r = [closes[days[j]][s] / closes[days[j - 1]][s] - 1 for j in range(i - p.vol_window + 1, i + 1)]
        m = sum(r) / len(r)
        sd = math.sqrt(sum((x - m) ** 2 for x in r) / len(r))
        w[s] = 1.0 / max(sd, 1e-4)
    return w


def build_tranche(closes, days, i, syms, p):
    d = closes[days[i]]
    d0 = closes[days[i - p.lookback]]
    ranked = sorted(syms, key=lambda s: d[s] / d0[s] - 1)
    k = max(1, int(len(ranked) * p.quantile))
    longs, shorts = ranked[:k], ranked[-k:]
    if p.vol_scale:
        w = inverse_vol(closes, days, i, longs + shorts, p)
    else:
        w = {s: 1.0 for s in longs + shorts}
    wl = sum(w[s] for s in longs)
    ws = sum(w[s] for s in shorts)
    return {s: w[s] / wl for s in longs}, {s: w[s] / ws for s in shorts}
