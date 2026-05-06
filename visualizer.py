import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import StrMethodFormatter


AVATAR_STYLES = [
    ("Rocket", "#ff006e", "^"),
    ("Turtle", "#3a86ff", "o"),
    ("Rollercoaster", "#8338ec", "s"),
]

PATH_COLORS = ["#118ab2", "#06d6a0", "#ffbe0b", "#fb5607", "#8338ec"]
INK = "#073b4c"
PAPER = "#fff7e6"
SKY = "#eaf7ff"


def _money(value):
    return rf"\${value:.0f}"


def _summarize_results(prices, start_price):
    final_prices = prices[-1]
    average_final = float(np.mean(final_prices))
    p10_final = float(np.percentile(final_prices, 10))
    p25_final = float(np.percentile(final_prices, 25))
    p75_final = float(np.percentile(final_prices, 75))
    p90_final = float(np.percentile(final_prices, 90))
    above_start_pct = float(np.mean(final_prices >= start_price) * 100.0)
    above_start_count = int(np.sum(final_prices >= start_price))
    return {
        "average_final": average_final,
        "p10_final": p10_final,
        "p25_final": p25_final,
        "p75_final": p75_final,
        "p90_final": p90_final,
        "above_start_pct": above_start_pct,
        "above_start_count": above_start_count,
        "simulation_count": int(prices.shape[1]),
    }


def _label_percentile(ax, day, value, label, color):
    ax.annotate(
        label,
        xy=(day, value),
        xytext=(8, 0),
        textcoords="offset points",
        va="center",
        fontsize=8.5,
        color=color,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.22", fc="white", ec=color, alpha=0.9),
    )


def _draw_single_chart(ax, prices, start_price, title, compact=False):
    days = np.arange(prices.shape[0])
    average_path = np.mean(prices, axis=1)
    p10 = np.percentile(prices, 10, axis=1)
    p25 = np.percentile(prices, 25, axis=1)
    p75 = np.percentile(prices, 75, axis=1)
    p90 = np.percentile(prices, 90, axis=1)

    band_possible = ax.fill_between(days, p10, p90, color="#ffd166", alpha=0.36, label="Surprise Zone (10%-90%)")
    band_likely = ax.fill_between(days, p25, p75, color="#06d6a0", alpha=0.38, label="Middle Pack (25%-75%)")

    # Each thin path is one random Monte Carlo trial.
    sample_count = min(28 if not compact else 12, prices.shape[1])
    sample_indices = np.linspace(0, prices.shape[1] - 1, sample_count, dtype=int)
    for color_index, idx in enumerate(sample_indices):
        ax.plot(
            days,
            prices[:, idx],
            color=PATH_COLORS[color_index % len(PATH_COLORS)],
            alpha=0.16 if not compact else 0.13,
            linewidth=1.1,
        )

    # Avatar paths give kids a memorable way to track outcomes.
    avatar_indices = np.linspace(0, prices.shape[1] - 1, len(AVATAR_STYLES), dtype=int)
    for avatar_idx, (avatar_name, avatar_color, marker) in zip(avatar_indices, AVATAR_STYLES):
        ax.plot(days, prices[:, avatar_idx], color=avatar_color, linewidth=2.3, alpha=0.95, label=f"{avatar_name} Path")
        ax.scatter(
            days[-1],
            prices[-1, avatar_idx],
            s=70 if not compact else 45,
            marker=marker,
            color=avatar_color,
            edgecolor="white",
            linewidth=1.2,
            zorder=5,
        )

    average_line, = ax.plot(days, average_path, color="#ef476f", linewidth=3, label="Average Path")
    ax.axhline(
        y=start_price,
        color="#6c757d",
        linestyle="--",
        linewidth=1.8,
        alpha=0.9,
        label="Start Line",
    )

    if not compact:
        endpoint_colors = np.where(prices[-1] >= start_price, "#06d6a0", "#ef476f")
        ax.scatter(
            np.full(prices.shape[1], days[-1]),
            prices[-1],
            s=22,
            c=endpoint_colors,
            alpha=0.45,
            edgecolors="none",
            label="Finish Dots",
            zorder=4,
        )
        _label_percentile(ax, days[-1], p90[-1], "90%", "#ff9f1c")
        _label_percentile(ax, days[-1], p75[-1], "75%", "#2a9d8f")
        _label_percentile(ax, days[-1], p25[-1], "25%", "#2a9d8f")
        _label_percentile(ax, days[-1], p10[-1], "10%", "#ff9f1c")
    ax.set_title(title, fontsize=18 if not compact else 14, fontweight="bold", color=INK, pad=16)
    ax.set_xlabel("Days Ahead", fontsize=12 if not compact else 10, fontweight="bold", color=INK)
    ax.set_ylabel("Price ($)", fontsize=12 if not compact else 10, fontweight="bold", color=INK)
    ax.yaxis.set_major_formatter(StrMethodFormatter("${x:.0f}"))
    ax.tick_params(axis="both", colors=INK, labelsize=10 if not compact else 8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#8ecae6")
    ax.spines["bottom"].set_color("#8ecae6")
    ax.grid(color="white", linestyle="-", linewidth=1.0, alpha=0.9)
    ax.set_xlim(days[0], days[-1] * (1.08 if not compact else 1.0))
    ax.legend(fontsize=8.5 if not compact else 7, loc="upper left", frameon=True, facecolor="white", edgecolor="#8ecae6")

    return band_possible, band_likely, average_line


def _draw_finish_histogram(ax, prices, start_price):
    final_prices = prices[-1]
    ax.set_facecolor("#fffdf7")
    ax.hist(final_prices, bins=16, color="#8ecae6", edgecolor="white", linewidth=1.2)
    ax.axvline(start_price, color="#6c757d", linestyle="--", linewidth=2, label="Start")
    ax.axvline(np.mean(final_prices), color="#ef476f", linewidth=3, label="Average")
    ax.set_title("Finish Line Pile-Up", fontsize=13, fontweight="bold", color=INK)
    ax.set_xlabel("Final price", fontsize=10, color=INK, fontweight="bold")
    ax.set_ylabel("How many paths", fontsize=10, color=INK, fontweight="bold")
    ax.xaxis.set_major_formatter(StrMethodFormatter("${x:.0f}"))
    ax.tick_params(axis="both", colors=INK, labelsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#8ecae6")
    ax.spines["bottom"].set_color("#8ecae6")
    ax.grid(axis="y", color="#e9ecef", linewidth=1)
    ax.legend(fontsize=8, frameon=True, facecolor="white", edgecolor="#8ecae6")


def _draw_scoreboard(ax, metrics, start_price):
    ax.set_axis_off()
    ax.set_facecolor(PAPER)
    ax.set_title("Monte Carlo Scoreboard", fontsize=13, fontweight="bold", color=INK, pad=8)

    below_count = metrics["simulation_count"] - metrics["above_start_count"]
    rows = [
        ("Random futures tried", f"{metrics['simulation_count']}"),
        ("Finished above start", f"{metrics['above_start_count']} of {metrics['simulation_count']}"),
        ("Finished below start", f"{below_count} of {metrics['simulation_count']}"),
        ("Average finish", _money(metrics["average_final"])),
        ("Middle pack finish", f"{_money(metrics['p25_final'])} to {_money(metrics['p75_final'])}"),
    ]

    y = 0.84
    for label, value in rows:
        ax.text(0.04, y, label, transform=ax.transAxes, fontsize=9.5, color="#4a4e69", fontweight="bold")
        ax.text(0.96, y, value, transform=ax.transAxes, fontsize=10, color=INK, fontweight="bold", ha="right")
        y -= 0.13

    bar_y = 0.14
    ax.add_patch(
        patches.FancyBboxPatch(
            (0.04, bar_y),
            0.92,
            0.11,
            boxstyle="round,pad=0.01,rounding_size=0.03",
            transform=ax.transAxes,
            facecolor="#f1f3f5",
            edgecolor="#dee2e6",
        )
    )
    win_width = 0.92 * metrics["above_start_pct"] / 100.0
    ax.add_patch(
        patches.FancyBboxPatch(
            (0.04, bar_y),
            win_width,
            0.11,
            boxstyle="round,pad=0.01,rounding_size=0.03",
            transform=ax.transAxes,
            facecolor="#06d6a0",
            edgecolor="#06d6a0",
        )
    )
    ax.text(
        0.5,
        bar_y + 0.055,
        f"{metrics['above_start_pct']:.1f}% at or above {_money(start_price)}",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=9,
        color=INK,
        fontweight="bold",
    )


def plot_fan_chart(prices, start_price, profile_label, mission_text=None):
    fig = plt.figure(figsize=(12, 8.5), facecolor=PAPER)
    grid = fig.add_gridspec(2, 2, height_ratios=[3.4, 1.45], hspace=0.22, wspace=0.24)
    ax = fig.add_subplot(grid[0, :])
    hist_ax = fig.add_subplot(grid[1, 0])
    score_ax = fig.add_subplot(grid[1, 1])
    ax.set_facecolor(SKY)

    band_possible, band_likely, average_line = _draw_single_chart(
        ax,
        prices,
        start_price,
        f"Stock Adventure: {profile_label}",
    )
    metrics = _summarize_results(prices, start_price)
    _draw_finish_histogram(hist_ax, prices, start_price)
    _draw_scoreboard(score_ax, metrics, start_price)

    math_fact = (
        f"Math fact: {metrics['above_start_pct']:.1f}% of simulations finished at or above {_money(start_price)}."
    )
    subtitle = (
        f"Middle 50% ended between {_money(metrics['p25_final'])} and {_money(metrics['p75_final'])}. "
        f"Average ending value: {_money(metrics['average_final'])}."
    )
    ax.text(0.02, 0.02, f"{math_fact}\n{subtitle}", transform=ax.transAxes, fontsize=9.5, color=INK)

    avatar_note = (
        "Avatar spotlight: Rocket, Turtle, and Rollercoaster are real paths from the same random run."
    )
    ax.text(0.02, 0.12, avatar_note, transform=ax.transAxes, fontsize=9, color="#4a4e69")

    if mission_text:
        ax.text(
            0.5,
            0.965,
            mission_text.replace("$", r"\$"),
            transform=ax.transAxes,
            ha="center",
            va="top",
            fontsize=10,
            color="#7f5539",
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.35", fc="#fff7e6", ec="#f4a261", alpha=0.9),
        )

    explanation_box = ax.annotate(
        "Click yellow, green, pink,\nor finish dots for a clue.",
        xy=(0.98, 0.92),
        xycoords="axes fraction",
        ha="right",
        va="top",
        fontsize=9,
        bbox=dict(boxstyle="round,pad=0.35", fc="#ffffff", ec="#8ecae6", alpha=0.95),
    )

    def on_click(event):
        if event.inaxes != ax:
            return

        message = "Each click explores how many\nrandom tries make a forecast."
        artist_hit = None
        for artist, text in (
            (
                band_likely,
                "Green band (25%-75%):\nthe middle pack of futures.\nHalf the paths end inside it.",
            ),
            (
                band_possible,
                "Yellow band (10%-90%):\na wider adventure zone.\nMost paths stay inside it.",
            ),
            (
                average_line,
                "Pink line:\nthe average of all futures.\nIt is a guide, not a promise.",
            ),
        ):
            contains, _ = artist.contains(event)
            if contains:
                artist_hit = text
                break
        if artist_hit:
            message = artist_hit
        elif event.xdata is not None and event.xdata > prices.shape[0] * 0.94:
            message = (
                "Finish dots:\neach dot is one simulated ending.\nGreen dots beat the start line."
            )

        explanation_box.set_text(message)
        fig.canvas.draw_idle()

    fig.canvas.mpl_connect("button_press_event", on_click)
    fig.subplots_adjust(left=0.06, right=0.985, top=0.9, bottom=0.08)
    plt.show()
    return metrics


def plot_comparison_chart(low_result, high_result, start_price, low_label, high_label):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    fig.patch.set_facecolor(PAPER)
    for ax in axes:
        ax.set_facecolor(SKY)

    _draw_single_chart(axes[0], low_result, start_price, f"Comparison: {low_label}", compact=True)
    _draw_single_chart(axes[1], high_result, start_price, f"Comparison: {high_label}", compact=True)

    low_metrics = _summarize_results(low_result, start_price)
    high_metrics = _summarize_results(high_result, start_price)
    range_width_low = low_metrics["p90_final"] - low_metrics["p10_final"]
    range_width_high = high_metrics["p90_final"] - high_metrics["p10_final"]

    summary_text = (
        f"Range width changed from {_money(range_width_low)} to {_money(range_width_high)}. "
        f"Average ending value changed from {_money(low_metrics['average_final'])} to {_money(high_metrics['average_final'])}. "
        f"Percent ending above start changed from {low_metrics['above_start_pct']:.1f}% to {high_metrics['above_start_pct']:.1f}%."
    )
    fig.suptitle("What Changed? Side-by-Side Comparison", fontsize=16, fontweight="bold", color=INK)
    fig.text(0.5, 0.02, summary_text, ha="center", fontsize=10, color="#4a4e69")

    plt.tight_layout(rect=(0, 0.06, 1, 0.94))
    plt.show()
