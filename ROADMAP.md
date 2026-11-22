# Roadmap

Where the Stochastic Market Engine is headed, one credible rung at a time.

## Done
- Real market data ingestion (`yfinance`) and GBM calibration from log returns.
- Risk metrics: Sharpe ratio, max drawdown (on real data and simulated paths).
- Fan-chart forecast anchored to a stock's real recent price.
- Unit tests for metrics and calibration; real README and dependency manifest.

## Next
1. **Backtesting.** Walk-forward test of a simple strategy (e.g. moving-average
   crossover) versus buy-and-hold, reported with Sharpe and drawdown.
2. **Options pricing.** European option pricer via Monte Carlo and Black-Scholes,
   with the Greeks. The highest-signal quant project.
3. **Portfolio layer.** Multi-asset simulation, correlation matrix, and a
   Markowitz efficient frontier (consider `PyPortfolioOpt` / `Riskfolio-Lib`).
4. **Packaging polish.** Type hints throughout, `pyproject.toml`, and CI.

## Later
- Alternative models beyond GBM (jump diffusion, stochastic volatility) to show
  awareness of GBM's limits.
- Value-at-Risk and Conditional VaR alongside drawdown.
