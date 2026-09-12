"""python -m pytest tests/  (or: python tests/test_backtest.py)"""
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rtoken import backtest, metrics
from rtoken.strategy import Params


def synthetic(n_days=80, n_sym=60):
    """Alternating up/down names: perfect reversal every session -> strategy must be profitable."""
    closes = {}
    d0 = date(2026, 1, 5)
    px = {f"S{i}": 100.0 for i in range(n_sym)}
    for t in range(n_days):
        d = d0 + timedelta(days=t + t // 5 * 2)   # skip weekends
        for i, s in enumerate(px):
            up = ((i + t) % 2 == 0)
            px[s] *= 1.01 if up else 0.99
        closes[d] = dict(px)
    return closes


def test_reversal_is_captured():
    closes = synthetic()
    _, r = backtest.run(closes, Params(lookback=1, hold=1, seasoning=0, min_universe=10, vol_scale=False, cost_bps=0))
    assert sum(r) > 0 and metrics.sharpe(r) > 5


def test_costs_reduce_return():
    closes = synthetic()
    _, a = backtest.run(closes, Params(lookback=1, hold=1, seasoning=0, min_universe=10, cost_bps=0))
    _, b = backtest.run(closes, Params(lookback=1, hold=1, seasoning=0, min_universe=10, cost_bps=50))
    assert sum(a) > sum(b)


def test_no_lookahead():
    """Shifting all prices after the last used close must not change the first return."""
    closes = synthetic()
    _, a = backtest.run(closes, Params(seasoning=0, min_universe=10))
    days = sorted(closes)
    for s in closes[days[-1]]:
        closes[days[-1]][s] *= 2
    _, b = backtest.run(closes, Params(seasoning=0, min_universe=10))
    assert a[:-1] == b[:-1]


if __name__ == "__main__":
    test_reversal_is_captured(); test_costs_reduce_return(); test_no_lookahead(); print("ok")
