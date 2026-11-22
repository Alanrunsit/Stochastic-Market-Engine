"""Backtester: moving-average crossover vs buy-and-hold."""

import pandas as pd
from data import fetch_close_prices
from metrics import simple_returns, sharpe_ratio, max_drawdown

# settings
ticker = "SPY"
short_window = 50
long_window = 200
cost_rate= 0.001  # 5 bps per trade

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

trades = aligned_position.diff().fillna(0).abs()
cost = trades * cost_rate
net_strategy_returns = strategy_returns - cost

# trade
strategy_equity = (1 + net_strategy_returns).cumprod()
buy_and_hold_equity = (1 + returns).cumprod()
total_return = strategy_equity.iloc[-1] - 1
strategy_sharpe = sharpe_ratio(net_strategy_returns)
strategy_drawdown = max_drawdown(strategy_equity)

# buy-and-hold metrics
bh_return = buy_and_hold_equity[-1] - 1
bh_sharpe = sharpe_ratio(returns)
bh_drawdown = max_drawdown(buy_and_hold_equity)

print(strategy_equity.iloc[-1])
print(buy_and_hold_equity[-1])
print(f"Total return: {total_return:.2%}")
print(f"Sharpe ratio: {strategy_sharpe:.2f}")
print(f"Max drawdown: {strategy_drawdown:.2%}")

print(f"Buy-and-hold return: {bh_return:.2%}")
print(f"Buy-and-hold Sharpe ratio: {bh_sharpe:.2f}")
print(f"Buy-and-hold Max drawdown: {bh_drawdown:.2%}")
