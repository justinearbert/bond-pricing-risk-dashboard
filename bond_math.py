"""Educational fixed-rate bond analytics with nominal annual yield compounded m times/year."""
from dataclasses import dataclass

import numpy as np
from scipy.optimize import brentq


@dataclass(frozen=True)
class Bond:
    face: float = 1000.0
    coupon_rate: float = 0.04
    maturity_years: float = 5.0
    payments_per_year: int = 2

    def __post_init__(self):
        if self.face <= 0:
            raise ValueError("Face value must be positive.")
        if self.coupon_rate < 0:
            raise ValueError("Coupon rate cannot be negative.")
        if self.maturity_years <= 0 or self.payments_per_year not in (1, 2, 4, 12):
            raise ValueError("Use a positive maturity and 1, 2, 4, or 12 payments/year.")
        periods = self.maturity_years * self.payments_per_year
        if not np.isclose(periods, round(periods)):
            raise ValueError("Maturity must be an exact multiple of the coupon period.")


def cashflows(bond: Bond):
    n = round(bond.maturity_years * bond.payments_per_year)
    times = np.arange(1, n + 1) / bond.payments_per_year
    flows = np.full(n, bond.face * bond.coupon_rate / bond.payments_per_year)
    flows[-1] += bond.face
    return times, flows


def price(bond: Bond, ytm: float) -> float:
    """Full price at a coupon date (clean = dirty), using nominal annual YTM."""
    m = bond.payments_per_year
    if 1 + ytm / m <= 0:
        raise ValueError("YTM must exceed -payments_per_year.")
    t, cf = cashflows(bond)
    return float(np.sum(cf / (1 + ytm / m) ** (m * t)))


def yield_to_maturity(bond: Bond, market_price: float) -> float:
    if market_price <= 0:
        raise ValueError("Market price must be positive.")
    m = bond.payments_per_year
    f = lambda y: price(bond, y) - market_price
    low = -m + 1e-8
    high = 0.1
    while f(high) > 0 and high < 1e6:
        high = 2 * high + 0.1
    return float(brentq(f, low, high))


def risk_metrics(bond: Bond, ytm: float):
    """Analytic Macaulay/modified duration, convexity, and positive DV01 (price loss for +1bp)."""
    m = bond.payments_per_year
    t, cf = cashflows(bond)
    disc = (1 + ytm / m) ** (m * t)
    pv = cf / disc
    p = float(np.sum(pv))
    macaulay = float(np.sum(t * pv) / p)
    modified = macaulay / (1 + ytm / m)
    # second derivative of price wrt nominal annual yield divided by price
    convexity = float(np.sum(pv * t * (t + 1 / m) / (1 + ytm / m) ** 2) / p)
    dv01 = (price(bond, ytm - 0.0001) - price(bond, ytm + 0.0001)) / 2
    return {"price": p, "macaulay_duration": macaulay,
            "modified_duration": modified, "convexity": convexity, "dv01": dv01}


def scenarios(bond: Bond, base_ytm: float, shocks_bp=(-200, -100, -50, 0, 50, 100, 200)):
    base = price(bond, base_ytm)
    rows = []
    for bp in shocks_bp:
        new_y = base_ytm + bp / 10000
        if 1 + new_y / bond.payments_per_year <= 0:
            continue
        new_p = price(bond, new_y)
        rows.append({"Rate shock (bp)": int(bp), "New yield (%)": 100 * new_y,
                     "Bond price": new_p, "P&L": new_p - base, "Return (%)": 100 * (new_p / base - 1)})
    return rows
