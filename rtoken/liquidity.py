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


def capacity(report, participation=0.10, hold=5, quantile=0.2, universe=60, tail_pct=0.10):
    """Rough strategy capacity. Selection is by signal, not by depth, so any eligible name can end up in a
    side; the binding constraint is the thin tail. We take the `tail_pct` depth quantile of names with a
    two-sided book, `participation` of it per rotation, quantile*universe names per side, HOLD tranches open."""
    per_side = int(universe * quantile)
    ok = sorted(min(r["bid_depth_usd"], r["ask_depth_usd"]) for r in report if r["spread_bps"] is not None)
    if len(ok) < per_side:
        return 0.0
    thin = ok[int(len(ok) * tail_pct)]
    return participation * thin * per_side * 2 * hold
