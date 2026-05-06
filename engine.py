import numpy as np

def generate_simulations(start_price, days, mu, sigma, num_simulations):
    """
    Generates multiple price paths using the Geometric Brownian Motion model.
    start_price: initial stock price
    days: number of days to simulate
    mu: expected annual return
    sigma: annualvolatility
    num_simulations: number of simulations to generate
    """
    dt = 1 / days #time array

    drift = (mu - 0.5 * sigma**2) * dt #no randomness in the drift

    #array to store the prices 
    prices=np.zeros((days, num_simulations)) 
    prices[0] = start_price

    for t in range(1, days):
        shocks = np.random.normal(0, 1, num_simulations) #randomness in simulations
        
        prices[t] = prices[t-1] * np.exp(drift + sigma * np.sqrt(dt) * shocks)

    return prices

