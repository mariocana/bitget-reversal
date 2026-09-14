# Submission texts — Bitget AI Hackathon S2

Form (EN/CN, same fields): https://forms.gle/GyWZCMCPocgJdJon6
Official post to retweet (required): https://x.com/Bitget_AI/status/2097230641452785752
Track: **Alpha Factory** · Sub-theme: **rToken factor strategies**
Repo: `https://github.com/mariocana/bitget-reversal` · X posts: `https://x.com/mc95000/status/2098854862997926063` (submission), `https://x.com/mc95000/status/2099502287865418233` (14 Sep live-book check) · Team Lead Bitget UID: `<UID>` (required — app: profile icon → number under the name)

---

## X post (copy, then paste the tweet URL into the form)

> Built a one-week reversal factor on Bitget's tokenized US stocks for #BitgetHackathon @Bitget_AI.
>
> Sharpe 2.9 net of costs over 75 sessions, positive in both halves. Pure Python, reproducible from the committed data.
>
> The part most entrants will miss: rToken volume mirrors the US tape — the real book is 10,000× thinner. Sizing off it is fiction. We size off the order book.
>
> `https://github.com/mariocana/bitget-reversal`

---

## 1. Thesis

Recent one-week losers among tokenized US stocks outperform recent one-week winners over the following week. This is the classic short-term reversal (Jegadeesh 1990, Lehmann 1990): uninformed order flow pushes prices away from value and liquidity providers are paid to carry them back.

rTokens are an unusually good place to harvest it. The venue is young (most names listed April 2026), the on-venue book is thin, and the participant base is crypto-native rather than professional equity market makers — so temporary price pressure should be larger and slower to correct than on the underlying exchange. We confirmed the effect with a cross-sectional rank IC of −0.097 (t = −2.6) for the 5-day signal against the following 5-day return, negative in both halves of the sample.

## 2. Target user

A systematic trader or fund running market-neutral equity factors who wants exposure to rTokens without taking directional US-equity risk. The strategy is dollar-neutral, rebalances once per session at the 16:00 ET close, rotates 20% of the book per day, and has explicit capacity limits derived from the live order book.

## 3. Validation data

- 60 rTokens with the highest reported 24h volume, 1-hour candles from Bitget's public v2 spot endpoints, 28 Apr – 9 Sep 2026 (committed as `data/candles_1h.json`).
- Session close = close of the 19:00 UTC bar (the 16:00 ET print).
- Backtest window 22 May – 9 Sep 2026: **75 sessions**, split 37 in-sample / **38 out-of-sample** at 17 Jul.
- Costs: 15 bps round-trip on every rotated dollar (observed cash-hour spreads on large names 3–8 bps).

| | sessions | Sharpe | Sortino | max DD | ann. return | win rate |
|---|---|---|---|---|---|---|
| total | 75 | 2.89 ± 1.8 | 5.59 | −5.8% | +63% | 52% |
| in-sample | 37 | 0.99 ± 2.6 | 1.76 | −5.8% | +27% | 43% |
| out-of-sample | 38 | 6.47 ± 2.6 | 17.96 | −1.4% | +98% | 61% |

All figures are **observed** (backtest on committed data), net of a 15 bps round-trip cost on every rotated dollar. Turnover: 20% of the book per session. Rolling 30-session Sharpe: min +0.51, median +5.26, positive in 100% of windows. No out-of-sample decay (OOS/IS = 6.6). `±` is the standard error of the Sharpe estimate. Both halves are positive; the drawdown is entirely in-sample. Parameter grid (lookback × hold ∈ {3,5,10}²): the effect lives at 3–5 / 3–5 and fades by 10, the decay profile of a genuine short-horizon reversal.

Three venue facts we verified that the brief does not state, and that make most backtests on rTokens wrong: (1) the venue trades 24/5, not 24/7 — a fixed 49h gap every weekend plus US holidays; (2) reported volume mirrors the underlying US tape (RSPYUSDT reports ~$28B/day; its live book holds ~$0.5M) so sizing on `usdtVolume` overstates capacity by 4–5 orders of magnitude; (3) overnight aggregate volume is <1% of the cash-session peak. The strategy therefore trades only at the close and measures capacity from the book (`scripts/liquidity_report.py`).

## 4. Progress

Complete and reproducible. `python scripts/run_backtest.py --grid` regenerates every number above from the committed snapshot in ~10 s with no dependencies (Python 3.9+). `tests/test_backtest.py` enforces no-lookahead, cost monotonicity, and signal capture on synthetic data. `scripts/fetch_data.py` refreshes the snapshot; `scripts/liquidity_report.py` snapshots the live book and prints strategy capacity.

## 5. Deliverables

- Public repo with strategy code, backtester, data snapshot, tests.
- `reports/results.json`, `reports/daily_returns.csv` (per-session returns with IS/OOS flag), `reports/equity.svg`, `reports/param_grid.json`.
- README with thesis, method, robustness (parameter grid, concentration, why in-sample is weaker), venue-data findings, and limitations.

## 6. AI perspective (optional)

An LLM (Claude) was used as a research assistant: probing the API to discover that rTokens sit under `category=SPOT/symbolType=stock`, that v3 rejects them and v2 works, and that the volume field is mirrored; writing and refactoring the data loader, backtester and tests. The trading signal itself is a rule, not a model — no LLM is in the loop at decision time. That is deliberate for an Alpha Factory entry: the score is quantitative, and a rule-based factor is auditable and re-runnable by the judges in seconds.

## LLM role (separate form field)

Research and engineering assistant, not a component of the strategy. It found the venue-data facts (24/5 calendar, mirrored volume, empty overnight book) by querying the public API, and it wrote the code. Signal generation and portfolio construction are deterministic rules with no model inference at runtime.
