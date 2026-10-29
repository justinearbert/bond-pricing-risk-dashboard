import pytest
from bond_math import Bond, price, yield_to_maturity, risk_metrics


def test_par_bond_when_coupon_equals_yield():
    bond = Bond(face=1000, coupon_rate=0.05, maturity_years=5, payments_per_year=2)
    assert price(bond, 0.05) == pytest.approx(1000)


def test_zero_coupon_price():
    bond = Bond(face=1000, coupon_rate=0.0, maturity_years=5, payments_per_year=2)
    assert price(bond, 0.04) == pytest.approx(1000 / 1.02**10)


def test_ytm_recovers_input():
    bond = Bond()
    assert yield_to_maturity(bond, price(bond, 0.0475)) == pytest.approx(0.0475)


def test_price_decreases_when_rates_rise():
    bond = Bond()
    assert price(bond, 0.06) < price(bond, 0.04)


def test_positive_duration_convexity_dv01():
    metrics = risk_metrics(Bond(), 0.05)
    assert metrics['modified_duration'] > 0
    assert metrics['convexity'] > 0
    assert metrics['dv01'] > 0
