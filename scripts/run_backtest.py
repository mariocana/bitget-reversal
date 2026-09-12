import csv
import itertools
import json
import sys
from dataclasses import asdict, replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rtoken import backtest, metrics  # noqa: E402
from rtoken.data import daily_closes, load_cached  # noqa: E402
from rtoken.strategy import Params  # noqa: E402

closes = daily_closes(load_cached("data/candles_1h.json"))
p = Params()
dates, daily = backtest.run(closes, p)
(is_d, is_r), (oos_d, oos_r) = backtest.split(dates, daily)

res = {
    "params": asdict(p),
    "period": {"start": str(dates[0]), "end": str(dates[-1]), "oos_start": str(oos_d[0])},
    "total": metrics.summary(daily),
    "in_sample": metrics.summary(is_r),
    "out_of_sample": metrics.summary(oos_r),
}
Path("reports").mkdir(exist_ok=True)
json.dump(res, open("reports/results.json", "w"), indent=2)
with open("reports/daily_returns.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["date", "return", "equity", "sample"])
    for d, r, e in zip(dates, daily, metrics.equity_curve(daily)):
        w.writerow([d, f"{r:.6f}", f"{e:.6f}", "OOS" if d >= oos_d[0] else "IS"])

def line(lbl, m):
    print(f"  {lbl:<14} n={m['days']:3d}  Sharpe={m['sharpe']:+5.2f} (±{m['sharpe_stderr']:.1f})  "
          f"Sortino={m['sortino']:+6.2f}  maxDD={m['max_drawdown']*100:5.1f}%  ann={m['ann_return']*100:+6.1f}%")

print(f"rToken reversal  LB={p.lookback} HOLD={p.hold} Q={p.quantile} cost={p.cost_bps}bps  "
      f"{dates[0]} -> {dates[-1]}  (OOS from {oos_d[0]})")
line("total", res["total"]); line("in-sample", res["in_sample"]); line("out-of-sample", res["out_of_sample"])

if "--grid" in sys.argv:
    print("\nparameter grid (Sharpe total / IS / OOS):")
    grid = []
    for lb, hd, q in itertools.product((3, 5, 10), (3, 5, 10), (0.2, 0.3)):
        _, r = backtest.run(closes, replace(p, lookback=lb, hold=hd, quantile=q))
        k = len(r) // 2
        row = {"lookback": lb, "hold": hd, "quantile": q,
               "sharpe": metrics.sharpe(r), "sharpe_is": metrics.sharpe(r[:k]), "sharpe_oos": metrics.sharpe(r[k:]),
               "max_drawdown": metrics.max_drawdown(r)}
        grid.append(row)
        print(f"  LB={lb:2d} HOLD={hd:2d} Q={q}   {row['sharpe']:+5.2f} / {row['sharpe_is']:+5.2f} / {row['sharpe_oos']:+5.2f}   DD={row['max_drawdown']*100:5.1f}%")
    json.dump(grid, open("reports/param_grid.json", "w"), indent=2)

def write_svg(dates, eq, oos_start, path="reports/equity.svg", W=880, H=360, PAD=50):
    lo, hi = min(eq) * 0.995, max(eq) * 1.005
    x = lambda i: PAD + i * (W - 2 * PAD) / (len(eq) - 1)
    y = lambda v: H - PAD - (v - lo) / (hi - lo) * (H - 2 * PAD)
    k = next(i for i, d in enumerate(dates) if d >= oos_start)
    pts = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(eq))
    ticks = "".join(f'<text x="{PAD-8}" y="{y(v)+4:.1f}" text-anchor="end" font-size="11">{v:.2f}</text>'
                    f'<line x1="{PAD}" x2="{W-PAD}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="#ddd"/>'
                    for v in [lo + (hi - lo) * t / 4 for t in range(5)])
    xt = "".join(f'<text x="{x(i):.1f}" y="{H-PAD+16}" text-anchor="middle" font-size="11">{dates[i]:%d %b}</text>'
                 for i in range(0, len(dates), max(1, len(dates) // 6)))
    open(path, "w").write(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="sans-serif">
<rect width="100%" height="100%" fill="white"/>{ticks}{xt}
<rect x="{x(k):.1f}" y="{PAD}" width="{x(len(eq)-1)-x(k):.1f}" height="{H-2*PAD}" fill="#f3f6fa"/>
<text x="{x(k)+6:.1f}" y="{PAD+14}" font-size="11" fill="#666">out-of-sample from {oos_start}</text>
<polyline points="{pts}" fill="none" stroke="#1f5fbf" stroke-width="2"/>
<line x1="{PAD}" x2="{W-PAD}" y1="{y(1):.1f}" y2="{y(1):.1f}" stroke="#999" stroke-dasharray="4 3"/>
<text x="{PAD}" y="{PAD-12}" font-size="13" font-weight="bold">rToken 5-day reversal, long-short, net of 15 bps</text>
</svg>''')

write_svg(dates, metrics.equity_curve(daily), oos_d[0])
print("\nwrote reports/equity.svg")
print("wrote reports/results.json, reports/daily_returns.csv")
