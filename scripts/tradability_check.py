import glob
import json
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rtoken import backtest, metrics  # noqa: E402
from rtoken.data import daily_closes, load_cached  # noqa: E402
from rtoken.strategy import Params  # noqa: E402

snap = sorted(glob.glob("data/orderbook_*.json"))[-1]
book = json.load(open(snap))["book"]
empty = sorted(r["symbol"] for r in book if r["spread_bps"] is None)
H = load_cached("data/candles_1h.json")
live = {s: v for s, v in H.items() if s not in empty}
print(f"snapshot {snap}: {len(empty)} of {len(H)} books empty -> {', '.join(empty)}\n")

def line(lbl, r):
    k = len(r) // 2
    roll = metrics.rolling_sharpe(r)
    print(f"  {lbl:<36} n={len(r):3d}  Sharpe={metrics.sharpe(r):+5.2f}  IS={metrics.sharpe(r[:k]):+5.2f}  "
          f"OOS={metrics.sharpe(r[k:]):+5.2f}  maxDD={metrics.max_drawdown(r)*100:5.1f}%  roll30 min={min(roll):+.2f}")

p = Params()
line("all 60 names (reported figures)", backtest.run(daily_closes(H), p)[1])
p2 = replace(p, min_universe=int(len(live) * 0.9))
line(f"{len(live)} names with a live book", backtest.run(daily_closes(live), p2)[1])
line(f"{len(live)} names, 25 bps costs", backtest.run(daily_closes(live), replace(p2, cost_bps=25))[1])
