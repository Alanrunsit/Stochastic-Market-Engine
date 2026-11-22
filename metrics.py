"""Risk metrics for price paths and return series.

Small, dependency-light functions used to score both real historical data
and simulated Monte Carlo paths. Everything here is deterministic and unit
tested in tests/test_metrics.py.
"""

import numpy as np

TRADING_DAYS = 252


def simple_returns(prices):
    """Period-over-period simple returns from a 1-D price series.

    prices: sequence of prices (len N)
    returns: np.ndarray of length N-1, where r_t = P_t / P_{t-1} - 1
    """
    prices = np.asarray(prices, dtype=float)
    return prices[1:] / prices[:-1] - 1.0


def sharpe_ratio(returns, risk_free=0.0, periods_per_year=TRADING_DAYS):
    """Annualized Sharpe ratio of a periodic return series.

    returns: sequence of periodic (e.g. daily) simple returns
    risk_free: annual risk-free rate, converted to per-period internally
    periods_per_year: 252 for daily data

    Returns 0.0 when the returns have no volatility (avoids divide-by-zero).
    """
    returns = np.asarray(returns, dtype=float)
    if returns.size == 0:
        return 0.0
    per_period_rf = risk_free / periods_per_year
    excess = returns - per_period_rf
    std = excess.std(ddof=1) if excess.size > 1 else excess.std()
    if std == 0:
        return 0.0
    return float(excess.mean() / std * np.sqrt(periods_per_year))


def max_drawdown(price_path):
    """Largest peak-to-trough drop of a price path, as a negative fraction.

    A return of -0.35 means the path fell 35% from a prior peak at its worst.
    Returns 0.0 for a path that never falls below its running maximum.
    """
    prices = np.asarray(price_path, dtype=float)
    if prices.size == 0:
        return 0.0
    running_max = np.maximum.accumulate(prices)
    drawdowns = prices / running_max - 1.0
    return float(drawdowns.min())
