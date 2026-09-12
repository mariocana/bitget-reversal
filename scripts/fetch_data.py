import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rtoken.data import history, liquid_universe, stock_symbols  # noqa: E402

N = int(sys.argv[1]) if len(sys.argv) > 1 else 60
syms = stock_symbols("data/instruments.json")
univ = liquid_universe(syms, N)
out = {}
for i, s in enumerate(univ, 1):
    out[s] = history(s, "1h", pages=14)
    print(f"[{i}/{len(univ)}] {s}: {len(out[s])} bars", flush=True)
json.dump(out, open("data/candles_1h.json", "w"))
print("wrote data/candles_1h.json")
