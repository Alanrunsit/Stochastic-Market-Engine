import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import StrMethodFormatter
from matplotlib.widgets import Slider


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


def plot_fan_chart(all_simulations, start_price, mission_text=None):
    """Show fan chart with a slider to switch between risk levels.

    all_simulations: list of (label, prices_array) tuples, one per risk level.
    Returns metrics for whichever level was selected when the window closes.
    """
    fig = plt.figure(figsize=(12, 7), facecolor=PAPER)
    ax = fig.add_subplot(1, 1, 1)
    ax.set_facecolor(SKY)

    current = {}

    def redraw(idx, flush=True):
        ax.cla()
        ax.set_facecolor(SKY)
        label, prices = all_simulations[idx]
        bp, bl, al = _draw_single_chart(ax, prices, start_price, f"Stock Adventure: {label}")
        current.update(band_possible=bp, band_likely=bl, average_line=al, prices=prices)

        if mission_text:
            ax.text(
                0.5, 0.965,
                mission_text.replace("$", r"\$"),
                transform=ax.transAxes,
                ha="center", va="top", fontsize=10,
                color="#7f5539", fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.35", fc="#fff7e6", ec="#f4a261", alpha=0.9),
            )

        current["explanation_box"] = ax.annotate(
            "Click yellow, green, pink,\nor finish dots for a clue.",
            xy=(0.98, 0.92), xycoords="axes fraction",
            ha="right", va="top", fontsize=9,
            bbox=dict(boxstyle="round,pad=0.35", fc="#ffffff", ec="#8ecae6", alpha=0.95),
        )

        if flush:
            fig.canvas.draw_idle()

    redraw(0, flush=False)

    slider_ax = fig.add_axes([0.15, 0.03, 0.7, 0.025])
    slider_ax.set_facecolor(PAPER)
    slider = Slider(
        slider_ax, "Risk Level  ",
        0, len(all_simulations) - 1,
        valinit=0, valstep=1,
        color="#06d6a0",
    )
    slider.valtext.set_text(all_simulations[0][0])

    def update(val):
        idx = int(slider.val)
        redraw(idx)
        slider.valtext.set_text(all_simulations[idx][0])

    slider.on_changed(update)

    def on_click(event):
        if event.inaxes != ax:
            return
        prices = current.get("prices")
        if prices is None:
            return
        message = "Each click explores how many\nrandom tries make a forecast."
        artist_hit = None
        for artist, text in (
            (current["band_likely"], "Green band (25%-75%):\nthe middle pack of futures.\nHalf the paths end inside it."),
            (current["band_possible"], "Yellow band (10%-90%):\na wider adventure zone.\nMost paths stay inside it."),
            (current["average_line"], "Pink line:\nthe average of all futures.\nIt is a guide, not a promise."),
        ):
            contains, _ = artist.contains(event)
            if contains:
                artist_hit = text
                break
        if artist_hit:
            message = artist_hit
        elif event.xdata is not None and event.xdata > prices.shape[0] * 0.94:
            message = "Finish dots:\neach dot is one simulated ending.\nGreen dots beat the start line."
        current["explanation_box"].set_text(message)
        fig.canvas.draw_idle()

    fig.canvas.mpl_connect("button_press_event", on_click)
    fig.subplots_adjust(left=0.07, right=0.97, top=0.91, bottom=0.13)
    plt.show()

    final_idx = int(slider.val)
    return _summarize_results(all_simulations[final_idx][1], start_price)


def plot_forecast(prices, start_price, history=None, title="Forecast", subtitle=None):
    """Fan chart of simulated paths anchored to a real price history.

    prices: simulated paths array (steps x num_simulations), starting at day 0
    start_price: the real last price the simulation starts from
    history: optional 1-D array of real prices leading up to start_price;
             drawn on negative x so day 0 is "today"
    subtitle: optional one-line metrics string shown under the title
    """
    fig = plt.figure(figsize=(12, 7), facecolor=PAPER)
    ax = fig.add_subplot(1, 1, 1)
    ax.set_facecolor(SKY)

    _draw_single_chart(ax, prices, start_price, title)

    if history is not None and len(history) > 0:
        history = np.asarray(history, dtype=float)
        hist_x = np.arange(-len(history) + 1, 1)  # ends at day 0
        ax.plot(
            hist_x, history,
            color=INK, linewidth=2.4, label="Real History", zorder=5,
        )
        ax.axvline(x=0, color="#6c757d", linestyle=":", linewidth=1.4, alpha=0.8)
        ax.set_xlim(hist_x[0], (prices.shape[0] - 1) * 1.08)
        ax.legend(fontsize=8.5, loc="upper left", frameon=True, facecolor="white", edgecolor="#8ecae6")

    if subtitle:
        ax.text(
            0.5, 0.965, subtitle,
            transform=ax.transAxes, ha="center", va="top",
            fontsize=10, color="#7f5539", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.35", fc="#fff7e6", ec="#f4a261", alpha=0.9),
        )

    fig.subplots_adjust(left=0.07, right=0.97, top=0.91, bottom=0.1)
    plt.show()

    return _summarize_results(prices, start_price)


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
