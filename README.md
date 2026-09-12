# rToken short-term reversal

**Bitget AI Hackathon S2 — Alpha Factory track, sub-theme: rToken factor strategies.**

A dollar-neutral, one-week reversal factor on Bitget's tokenized US stocks (rTokens), with fills
and capacity taken from the order book rather than from the reported volume. Pure Python, no
dependencies, fully reproducible from the committed data snapshot.

```bash
python scripts/run_backtest.py --grid      # results.json, daily_returns.csv, equity.svg, param_grid.json
python tests/test_backtest.py              # lookahead / cost / signal-capture checks
python scripts/liquidity_report.py         # live book snapshot + capacity (run during US cash hours)
```

