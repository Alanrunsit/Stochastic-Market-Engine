import numpy as np

def generate_simulations(start_price, days, mu, sigma, num_simulations, dt=None):
    """
    Generates multiple price paths using the Geometric Brownian Motion model.
    start_price: initial stock price
    days: number of steps to simulate
    mu: expected annual return
    sigma: annual volatility
    num_simulations: number of simulations to generate
    dt: length of one step in years. Defaults to 1/days (a fixed one-year
        horizon). Pass 1/252 to make each step a real trading day.
    """
    if dt is None:
        dt = 1 / days #one-year horizon split into `days` steps

    drift = (mu - 0.5 * sigma**2) * dt #no randomness in the drift

    #array to store the prices 
    prices=np.zeros((days, num_simulations)) 
    prices[0] = start_price

    for t in range(1, days):
        shocks = np.random.normal(0, 1, num_simulations) #randomness in simulations
        
        prices[t] = prices[t-1] * np.exp(drift + sigma * np.sqrt(dt) * shocks)

    return prices

