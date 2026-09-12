import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rtoken.data import load_cached  # noqa: E402
from rtoken.liquidity import capacity, depth_report  # noqa: E402

syms = list(load_cached("data/candles_1h.json"))
rep = depth_report(syms)
now = datetime.now(timezone.utc)
Path("reports").mkdir(exist_ok=True)
json.dump({"ts": now.isoformat(), "book": rep}, open(f"data/orderbook_{now:%Y%m%d_%H%M}.json", "w"), indent=1)

ok = [r for r in rep if r["spread_bps"] is not None]
empty = [r["symbol"] for r in rep if r["spread_bps"] is None]
sp = sorted(r["spread_bps"] for r in ok)
dp = sorted(min(r["bid_depth_usd"], r["ask_depth_usd"]) for r in ok)
print(f"{now:%a %d %b %H:%M} UTC  universe={len(rep)}  books with both sides={len(ok)}  empty={len(empty)}")
if ok:
    print(f"  spread bps   median={sp[len(sp)//2]:.1f}  p90={sp[int(len(sp)*.9)]:.1f}")
    print(f"  depth (20 lvls, thinner side, USD)   median=${dp[len(dp)//2]:,.0f}  p10=${dp[int(len(dp)*.1)]:,.0f}")
    cap = capacity(rep)
    print(f"  strategy capacity at 10% participation: ~${cap:,.0f}")
if empty:
    print("  empty books:", ", ".join(empty[:12]) + (" ..." if len(empty) > 12 else ""))
