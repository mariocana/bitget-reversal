import json
import time
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://api.bitget.com/api/v2/spot/market"
CLOSE_HOUR_UTC = 19   # bar 19:00-20:00 UTC = 15:00-16:00 ET; its close is the 16:00 ET print


def _get(url, retries=4):
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=25) as r:
                return json.load(r)["data"]
        except Exception:
            time.sleep(1 + attempt)
    return []


def stock_symbols(instruments_path=None):
    """All online rToken symbols. Reads the cached instruments file if given."""
    if instruments_path and Path(instruments_path).exists():
        data = json.load(open(instruments_path))["data"]
    else:
        data = _get("https://api.bitget.com/api/v3/market/instruments?category=spot")
    return sorted(x["symbol"] for x in data if x.get("symbolType") == "stock" and x.get("status") == "online")


def liquid_universe(symbols, n=60):
    """Top-n by reported 24h volume. The number itself is mirrored from the US tape,
    but its *ranking* is still a fair proxy for which names get real on-venue flow."""
    tickers = _get(f"{BASE}/tickers")
    want = set(symbols)
    ranked = sorted((t for t in tickers if t["symbol"] in want),
                    key=lambda t: -float(t.get("usdtVolume") or 0))
    return [t["symbol"] for t in ranked[:n]]


def history(symbol, granularity="1h", pages=14):
    """Paginated history-candles. Returns {ts_ms: [open, high, low, close, base_vol]}.
    limit maxes at 200 per call; 14 pages of 1h ~ 135 days."""
    rows = {}
    end = int(time.time() * 1000)
    for _ in range(pages):
        h = _get(f"{BASE}/history-candles?symbol={symbol}&granularity={granularity}&limit=200&endTime={end}")
        if not h:
            break
        for c in h:
            rows[int(c[0])] = [float(x) for x in c[1:6]]
        nxt = min(int(c[0]) for c in h)
        if nxt >= end:
            break
        end = nxt
        time.sleep(0.06)
    return rows


def orderbook(symbol, limit=20):
    return _get(f"{BASE}/orderbook?symbol={symbol}&limit={limit}")


def daily_closes(candles_1h):
    """{date: {symbol: close}} using the 16:00 ET print (close of the 19:00 UTC bar).
    Weekend bars are sparse and low-volume; requiring the 19h bar keeps only real sessions."""
    closes = defaultdict(dict)
    for sym, rows in candles_1h.items():
        for ts, c in rows.items():
            dt = datetime.fromtimestamp(int(ts) / 1000, tz=timezone.utc)
            if dt.hour == CLOSE_HOUR_UTC:
                closes[dt.date()][sym] = c[3]
    return closes


def load_cached(path="data/candles_1h.json"):
    return json.load(open(path))
