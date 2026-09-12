from .data import orderbook


def depth_report(symbols, levels=20):
    out = []
    for s in symbols:
        ob = orderbook(s, levels) or {}
        bids, asks = ob.get("bids", []), ob.get("asks", [])
        if not bids or not asks:
            out.append({"symbol": s, "spread_bps": None, "bid_depth_usd": 0.0, "ask_depth_usd": 0.0})
            continue
        bid, ask = float(bids[0][0]), float(asks[0][0])
        mid = (bid + ask) / 2
        out.append({
            "symbol": s,
            "spread_bps": (ask - bid) / mid * 1e4,
            "bid_depth_usd": sum(float(p) * float(q) for p, q in bids),
            "ask_depth_usd": sum(float(p) * float(q) for p, q in asks),
        })
    return out


def capacity(report, participation=0.10, hold=5, quantile=0.2, universe=60):
    per_side = int(universe * quantile)
    ok = [r for r in report if r["spread_bps"] is not None]
    ok.sort(key=lambda r: min(r["bid_depth_usd"], r["ask_depth_usd"]))
    if len(ok) < per_side:
        return 0.0
    thin = ok[len(ok) - per_side] if len(ok) > per_side else ok[0]
    per_name = participation * min(thin["bid_depth_usd"], thin["ask_depth_usd"])
    return per_name * per_side * 2 * hold
