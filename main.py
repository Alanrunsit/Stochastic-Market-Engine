from engine import generate_simulations
from visualizer import plot_comparison_chart, plot_fan_chart


STARTING_PRICE = 90
DAYS = 300
SIMULATIONS = 120

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


def run_once(profile_key, profile, mission):
    print(f"\nStarting simulation for {profile['label']}...")
    print(mission["prompt"])
    results = generate_simulations(STARTING_PRICE, DAYS, profile["mu"], profile["sigma"], SIMULATIONS)
    print(f"Simulation complete! Generated {results.shape[1]} paths.")
    metrics = plot_fan_chart(results, STARTING_PRICE, profile["label"], mission["prompt"])
    if mission["checker"](metrics):
        print(f"Mission result: SUCCESS - {mission['success']}")
        mission_success = True
    else:
        print(f"Mission result: Not yet - {mission['hint']}")
        mission_success = False
    return results, metrics, mission_success


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

    print("Welcome to Stock Adventure!")
    print("Adjust risk, test predictions, and learn what volatility does.")

    while True:
        profile_key, profile = select_risk_level()
        mission = MISSIONS[mission_index % len(MISSIONS)]
        _, _, mission_success = run_once(profile_key, profile, mission)
        risk_history.add(profile_key)
        if mission_success:
            successful_missions += 1
        maybe_award_badges(badges, risk_history, successful_missions)
        mission_index += 1

        compare_choice = input("See side-by-side comparison mode? (y/n): ").strip().lower()
        if compare_choice == "y":
            run_comparison_mode()

        rerun = input("Run again with a new risk level? (y/n): ").strip().lower()
        if rerun != "y":
            break

    print("\nSession complete!")
    print(f"Badges earned: {', '.join(sorted(badges)) if badges else 'None yet'}")
    print("Thanks for exploring probabilities and risk.")


if __name__ == "__main__":
    main()
