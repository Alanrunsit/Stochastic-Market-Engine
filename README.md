# Stochastic Market Engine

An interactive Monte Carlo simulator that shows what risk actually looks like. You pick a risk level, and the engine simulates 120 possible future price paths for a stock over 300 trading days using Geometric Brownian Motion. The paths spread out into a "fan" of outcomes, so you can see how volatility widens the range of what might happen.

## Features

- **Five risk profiles**, from *Calm Seas* (6% return, 12% volatility) to *Storm Mode* (10% return, 44% volatility)
- **Fan chart** of every simulated path with percentile bands, plus a histogram of where the paths finish and a scoreboard of key stats
- **Missions** that ask you to predict outcomes, such as picking a risk level where most paths stay above $90
- **Comparison mode** that puts a low-risk and a high-risk run side by side
- **Badges** for exploring different risk levels and completing missions

## How it works

Each day, every path moves by a small fixed drift plus a random shock drawn from a normal distribution:

```
price[t] = price[t-1] * exp((mu - sigma²/2) * dt + sigma * sqrt(dt) * Z)
```

`mu` is the expected return, `sigma` is the volatility, and `Z` is the random shock. The simulation runs on NumPy arrays and the charts are drawn with Matplotlib.

| File | Role |
| --- | --- |
| `engine.py` | Generates the simulated price paths |
| `visualizer.py` | Fan chart, histogram, scoreboard, and comparison view |
| `main.py` | Terminal menu, missions, and badges |

## Run it

```bash
pip install -r requirements.txt
python3 main.py
```
