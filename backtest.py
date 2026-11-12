"""Backtester: moving-average crossover vs buy-and-hold."""

import pandas as pd
from data import fetch_close_prices
from metrics import simple_returns, sharpe_ratio, max_drawdown

# settings
ticker = "SPY"
short_window = 50
long_window = 200

# load data
close_prices = fetch_close_prices(ticker, period="5y")
print("Loaded", len(close_prices), "days of data for", ticker)

# calculate returns
returns = simple_returns(close_prices)

# moving averages
short_ma = pd.Series(close_prices).rolling(short_window).mean()
long_ma = pd.Series(close_prices).rolling(long_window).mean()

signal = (short_ma > long_ma).astype(int)

position = signal.shift(1).fillna(0)
aligned_position = position.iloc[1:]
strategy_returns = aligned_position * returns
