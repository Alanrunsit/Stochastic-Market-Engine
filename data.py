"""Real market data ingestion and GBM calibration.

Pulls historical prices with yfinance and derives the drift (mu) and
volatility (sigma) that feed the Monte Carlo engine, so simulations are
anchored to a real stock instead of hand-picked constants.
"""

import numpy as np

from metrics import TRADING_DAYS

try:
    import yfinance as yf
except ImportError:  # pragma: no cover - surfaced to the user at runtime
    yf = None


class MarketDataError(Exception):
    """Raised when data can't be fetched (bad ticker, no network, etc.)."""


def fetch_close_prices(ticker, period="2y"):
    """Fetch a clean 1-D array of adjusted daily closes for a ticker.

    ticker: symbol like "AAPL"
    period: yfinance period string ("1y", "2y", "5y", ...)
    Raises MarketDataError on any failure so callers can degrade gracefully.
    """
    if yf is None:
        raise MarketDataError(
            "yfinance is not installed. Run: pip install -r requirements.txt"
        )
    try:
        frame = yf.download(
            ticker, period=period, progress=False, auto_adjust=True
        )
    except Exception as exc:  # network, rate limit, etc.
        raise MarketDataError(f"Could not download {ticker!r}: {exc}") from exc

    if frame is None or frame.empty or "Close" not in frame:
        raise MarketDataError(f"No price data returned for {ticker!r}.")

    closes = np.asarray(frame["Close"].dropna().to_numpy(), dtype=float).ravel()
    if closes.size < 30:
        raise MarketDataError(
            f"Only {closes.size} data points for {ticker!r}; need at least 30."
        )
    return closes


def calibrate_gbm(prices, periods_per_year=TRADING_DAYS):
    """Estimate GBM drift (mu) and volatility (sigma) from a price history.

    Uses daily log returns:
      sigma_annual = std(log_returns) * sqrt(252)
      mu_annual    = mean(log_returns) * 252 + 0.5 * sigma_annual**2
    The +0.5*sigma^2 converts the log-return drift back to the mu used in the
    engine's exp(mu - 0.5*sigma^2) term.

    Returns a dict: {"start_price", "mu", "sigma"}.
    """
    prices = np.asarray(prices, dtype=float)
    log_returns = np.diff(np.log(prices))
    sigma = float(log_returns.std(ddof=1) * np.sqrt(periods_per_year))
    mu = float(log_returns.mean() * periods_per_year + 0.5 * sigma**2)
    return {"start_price": float(prices[-1]), "mu": mu, "sigma": sigma}
