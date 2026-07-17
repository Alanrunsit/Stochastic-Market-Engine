import numpy as np

from data import MarketDataError, calibrate_gbm, fetch_close_prices
from engine import generate_simulations
from metrics import max_drawdown, sharpe_ratio, simple_returns
from visualizer import plot_comparison_chart, plot_fan_chart, plot_forecast


STARTING_PRICE = 90
DAYS = 300
SIMULATIONS = 120

# Analytics mode (real-stock forecasts)
HORIZON_DAYS = 252          # ~1 trading year ahead
ANALYTICS_SIMS = 500
DT_DAILY = 1 / 252          # each step is one trading day
HISTORY_WINDOW = 120        # real days drawn to the left of "today"

RISK_LEVELS = {
    "1": {"label": "Calm Seas", "mu": 0.06, "sigma": 0.12},
    "2": {"label": "Steady River", "mu": 0.07, "sigma": 0.18},
    "3": {"label": "Wavy Waters", "mu": 0.08, "sigma": 0.25},
    "4": {"label": "Wild Rapids", "mu": 0.09, "sigma": 0.34},
    "5": {"label": "Storm Mode", "mu": 0.10, "sigma": 0.44},
}

MISSIONS = [
    {
        "prompt": "Mission: Pick a risk level where most outcomes stay above $90.",
        "checker": lambda metrics: metrics["p25_final"] >= 90,
        "success": "Great call! The middle outcomes stayed above $90.",
        "hint": "Try lower volatility if too many paths dip.",
    },
    {
        "prompt": "Mission: Find a run where at least 60% of paths finish above $100.",
        "checker": lambda metrics: metrics["above_start_pct"] >= 60,
        "success": "Nice prediction! More than 60% finished above the start.",
        "hint": "Try a profile with stronger average growth.",
    },
]


def show_main_menu():
    print("\nWhat would you like to do?")
    print("  1. Forecast a real stock (Monte Carlo + risk metrics)")
    print("  2. Explore risk levels (learning demo)")
    print("  3. Compare two risk levels side-by-side")
    print("  4. Quit")
    while True:
        choice = input("Enter 1-4: ").strip()
        if choice in ("1", "2", "3", "4"):
            return {"1": "analytics", "2": "simulate", "3": "compare", "4": "quit"}[choice]
        print("Please enter 1, 2, 3, or 4.")


def run_analytics_mode():
    """Calibrate GBM from a real stock and forecast it forward with risk metrics."""
    ticker = input("\nTicker to forecast (e.g. AAPL): ").strip().upper() or "AAPL"
    print(f"Fetching {ticker} history...")
    try:
        history = fetch_close_prices(ticker, period="2y")
    except MarketDataError as exc:
        print(f"Sorry, that didn't work: {exc}")
        return

    params = calibrate_gbm(history)
    mu, sigma, start_price = params["mu"], params["sigma"], params["start_price"]

    # Metrics on the real history (the honest, credible numbers).
    hist_returns = simple_returns(history)
    hist_sharpe = sharpe_ratio(hist_returns)
    hist_mdd = max_drawdown(history)

    print(f"\nCalibrated from {len(history)} days of real data:")
    print(f"  Drift (annual mu):      {mu:6.2%}")
    print(f"  Volatility (annual):    {sigma:6.2%}")
    print(f"  Last price:             ${start_price:,.2f}")
    print(f"  Historical Sharpe:      {hist_sharpe:6.2f}")
    print(f"  Historical max drawdown:{hist_mdd:6.1%}")

    prices = generate_simulations(
        start_price, HORIZON_DAYS, mu, sigma, ANALYTICS_SIMS, dt=DT_DAILY
    )

    # Median max drawdown across the simulated futures.
    sim_mdds = [max_drawdown(prices[:, i]) for i in range(prices.shape[1])]
    median_sim_mdd = float(np.median(sim_mdds))

    subtitle = (
        f"{ticker}  |  hist Sharpe {hist_sharpe:.2f}  |  "
        f"hist max DD {hist_mdd:.0%}  |  median sim max DD {median_sim_mdd:.0%}"
    )
    recent = history[-HISTORY_WINDOW:]
    metrics = plot_forecast(
        prices, start_price, history=recent,
        title=f"{ticker}: one-year Monte Carlo forecast", subtitle=subtitle,
    )

    print(f"\nForecast over {HORIZON_DAYS} trading days ({ANALYTICS_SIMS} paths):")
    print(f"  Average ending price:   ${metrics['average_final']:,.2f}")
    print(f"  10th-90th pct range:    ${metrics['p10_final']:,.2f} - ${metrics['p90_final']:,.2f}")
    print(f"  Paths ending up:        {metrics['above_start_pct']:.1f}%")
    print(f"  Median sim max drawdown:{median_sim_mdd:6.1%}")


def select_risk_level():
    print("\nChoose your risk level:")
    for key, profile in RISK_LEVELS.items():
        print(f"  {key}. {profile['label']} (return={profile['mu']:.2f}, volatility={profile['sigma']:.2f})")
    while True:
        choice = input("Enter 1-5: ").strip()
        if choice in RISK_LEVELS:
            return choice, RISK_LEVELS[choice]
        print("Please enter a number from 1 to 5.")


def maybe_award_badges(badges, risk_history, successful_missions):
    if len(risk_history) >= 3 and "Explorer Badge" not in badges:
        badges.add("Explorer Badge")
        print("Badge earned: Explorer Badge (tried 3 risk levels)")
    if successful_missions >= 2 and "Predictor Badge" not in badges:
        badges.add("Predictor Badge")
        print("Badge earned: Predictor Badge (completed 2 missions)")


def run_simulate_mode(mission):
    print(f"\n{mission['prompt']}")
    print("Generating simulations for all risk levels...")
    all_simulations = [
        (profile["label"], generate_simulations(STARTING_PRICE, DAYS, profile["mu"], profile["sigma"], SIMULATIONS))
        for profile in RISK_LEVELS.values()
    ]
    print("Ready! Drag the slider to explore different risk levels.")
    metrics = plot_fan_chart(all_simulations, STARTING_PRICE, mission["prompt"])
    if mission["checker"](metrics):
        print(f"Mission result: SUCCESS - {mission['success']}")
        return True
    print(f"Mission result: Not yet - {mission['hint']}")
    return False


def run_comparison_mode():
    print("\nWhat Changed? Comparison mode")
    print("Pick a low-risk profile and a high-risk profile to compare side-by-side.")
    low_key, low_profile = select_risk_level()
    high_key, high_profile = select_risk_level()
    low_result = generate_simulations(STARTING_PRICE, DAYS, low_profile["mu"], low_profile["sigma"], SIMULATIONS)
    high_result = generate_simulations(STARTING_PRICE, DAYS, high_profile["mu"], high_profile["sigma"], SIMULATIONS)
    plot_comparison_chart(
        low_result,
        high_result,
        STARTING_PRICE,
        f"{low_key}-{low_profile['label']}",
        f"{high_key}-{high_profile['label']}",
    )


def main():
    badges = set()
    risk_history = set()
    mission_index = 0
    successful_missions = 0

    print("Stochastic Market Engine")
    print("Monte Carlo price forecasting and risk metrics, calibrated on real data.")

    while True:
        action = show_main_menu()
        if action == "quit":
            break
        elif action == "analytics":
            run_analytics_mode()
        elif action == "compare":
            run_comparison_mode()
        else:
            mission = MISSIONS[mission_index % len(MISSIONS)]
            mission_success = run_simulate_mode(mission)
            risk_history.update(RISK_LEVELS.keys())
            if mission_success:
                successful_missions += 1
            maybe_award_badges(badges, risk_history, successful_missions)
            mission_index += 1

    print("\nSession complete!")
    print(f"Badges earned: {', '.join(sorted(badges)) if badges else 'None yet'}")
    print("Thanks for exploring probabilities and risk.")


if __name__ == "__main__":
    main()
