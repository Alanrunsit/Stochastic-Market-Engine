"""Hand-checked tests for the risk metrics and GBM calibration."""

import numpy as np
import pytest

from metrics import max_drawdown, sharpe_ratio, simple_returns
from data import calibrate_gbm


def test_simple_returns():
    result = simple_returns([100, 110, 99])
    assert np.allclose(result, [0.1, -0.1])


def test_sharpe_exact_value():
    # mean 0.01, sample std sqrt(0.0002), *sqrt(2) -> exactly 1.0
    assert sharpe_ratio([0.0, 0.02], periods_per_year=2) == pytest.approx(1.0)


def test_sharpe_zero_volatility_is_zero():
    assert sharpe_ratio([0.01, 0.01, 0.01]) == 0.0


def test_sharpe_is_scale_invariant():
    base = [0.01, -0.005, 0.02, -0.01, 0.015]
    scaled = [3 * r for r in base]
    assert sharpe_ratio(base) == pytest.approx(sharpe_ratio(scaled))


def test_max_drawdown_basic():
    assert max_drawdown([100, 120, 90, 130]) == pytest.approx(-0.25)


def test_max_drawdown_monotonic_up_is_zero():
    assert max_drawdown([1, 2, 3, 4]) == 0.0


def test_calibrate_gbm_constant_growth():
    # prices with a constant daily log return of 0.0004 => sigma 0, mu 0.1008
    t = np.arange(100)
    prices = 100 * np.exp(0.0004 * t)
    params = calibrate_gbm(prices)
    assert params["sigma"] == pytest.approx(0.0, abs=1e-9)
    assert params["mu"] == pytest.approx(0.0004 * 252, rel=1e-6)
    assert params["start_price"] == pytest.approx(prices[-1])
