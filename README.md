# Stochastic Market Engine

A Monte Carlo forecasting and risk tool for equities. It calibrates a Geometric
Brownian Motion (GBM) model on a real stock's history, simulates hundreds of
possible one-year price paths, and reports risk metrics on both the real data
and the simulated futures.

It also ships with an interactive learning demo (a risk-level slider) for
building intuition about volatility.

## What it does

- **Calibrates on real data.** Pulls a ticker's history with `yfinance` and
  estimates annual drift (`mu`) and volatility (`sigma`) from its daily log
  returns.
- **Simulates forward.** Runs a vectorized GBM Monte Carlo of many price paths
  over a one-year horizon (daily steps).
- **Scores risk.** Computes the Sharpe ratio and maximum drawdown on the real
  history, plus the median simulated max drawdown across paths.
- **Visualizes it.** Draws a fan chart of the simulated paths anchored to the
  stock's recent real price, with percentile bands and a "today" line.

## Methodology

GBM models the price as `S_t = S_0 * exp((mu - 0.5*sigma^2)*t + sigma*W_t)`.
Calibration inverts the daily log returns:

- `sigma_annual = std(log_returns) * sqrt(252)`
- `mu_annual = mean(log_returns) * 252 + 0.5 * sigma_annual^2`

Metrics:

- **Sharpe ratio** = `mean(excess returns) / std(excess returns) * sqrt(252)`
- **Max drawdown** = the largest peak-to-trough drop along a price path.

## Install

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

Then pick option **1** and enter a ticker (e.g. `AAPL`). The tool prints the
calibrated parameters and risk metrics, then opens the forecast chart.

Menu:

1. Forecast a real stock (Monte Carlo + risk metrics)
2. Explore risk levels (learning demo)
3. Compare two risk levels side-by-side
4. Quit

## Tests

```bash
pytest
```

## Project layout

```
data.py         real-data fetch + GBM calibration
engine.py       vectorized GBM Monte Carlo simulation
metrics.py      Sharpe ratio, max drawdown, returns
visualizer.py   fan charts and the real-history overlay
main.py         CLI: analytics mode + learning demo
tests/          unit tests for the metrics and calibration
```

See `ROADMAP.md` for where this is headed (backtesting, options pricing,
portfolio optimization).

## Disclaimer

This is an educational modeling tool, not investment advice. GBM assumes
constant volatility and normal returns, which real markets violate.
