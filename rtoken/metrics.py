"""Performance metrics on a list of daily returns."""
import math

ANN = 252


def sharpe(rs):
    n = len(rs)
    m = sum(rs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in rs) / (n - 1))
    return m / sd * math.sqrt(ANN) if sd else 0.0


def sortino(rs):
    n = len(rs)
    m = sum(rs) / n
    dn = [x for x in rs if x < 0]
    dsd = math.sqrt(sum(x * x for x in dn) / n) if dn else 0.0
    return m / dsd * math.sqrt(ANN) if dsd else float("inf")


def max_drawdown(rs):
    eq = pk = 1.0
    mdd = 0.0
    for x in rs:
        eq *= 1 + x
        pk = max(pk, eq)
        mdd = min(mdd, eq / pk - 1)
    return mdd


def equity_curve(rs):
    eq = 1.0
    out = []
    for x in rs:
        eq *= 1 + x
        out.append(eq)
    return out


def summary(rs):
    n = len(rs)
    m = sum(rs) / n
    return {
        "days": n,
        "ann_return": m * ANN,
        "sharpe": sharpe(rs),
        "sortino": sortino(rs),
        "max_drawdown": max_drawdown(rs),
        "total_return": equity_curve(rs)[-1] - 1,
        "sharpe_stderr": math.sqrt(ANN / n),   # rough SE of an annualised Sharpe estimate
    }
