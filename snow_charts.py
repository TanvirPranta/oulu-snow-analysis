"""Presentation-ready charts with explicit units, windows and denominators."""
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
from itertools import cycle
from snow_analysis import WINTER_MONTHS, MONTH_LABELS

COLORS = ["#007F86", "#CA6B23", "#6C5B9B"]


def save_figure(fig, path, note):
    fig.text(0.02, 0.01, note, fontsize=9)
    fig.tight_layout(rect=[0, 0.09, 1, 0.95])
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.show()
    plt.close(fig)


def plot_daily(data, figure_dir):
    fig, ax = plt.subplots(figsize=(12, 5))
    for (winter, group), color in zip(data.groupby("Winter"), cycle(COLORS)):
        series = group.set_index("Date")["Snow_depth_cm"]
        # A missing calendar date becomes a gap, not a connected line.
        series = series.reindex(pd.date_range(series.index.min(), series.index.max()))
        ax.plot(series.index, series.values, label=winter, color=color, linewidth=1.8)
    ax.set(title="Oulu Kaukovainio: daily snow depth", xlabel="Date", ylabel="Snow depth (cm)")
    ax.set_ylim(bottom=0)
    ax.legend(title="Winter")
    ax.grid(alpha=0.2)
    fig.autofmt_xdate()
    save_figure(fig, figure_dir / "daily_snow_depth.png",
                "Source: FMI. October–April only; 2023–24 begins 10 November.\nSummer gaps are excluded periods, not zero snow depth.")


def plot_monthly(monthly, figure_dir):
    chart = monthly.reset_index().pivot(index="Month", columns="Winter", values="Increase_pct").reindex(WINTER_MONTHS)
    chart.index = MONTH_LABELS
    chart = chart.astype("Float64").astype(float)
    ax = chart.plot(kind="bar", figsize=(11, 5.5), color=COLORS, width=0.8)
    ax.set(title="Daily snow-depth increase frequency by month", xlabel="Month", ylabel="Valid daily comparisons with increase (%)", ylim=(0, min(100, max(50, chart.max().max() * 1.15))))
    ax.tick_params(axis="x", rotation=0)
    ax.grid(axis="y", alpha=0.2)
    ax.set_axisbelow(True)
    ax.legend(title="Winter")
    save_figure(ax.figure, figure_dir / "monthly_snow_depth_increases.png",
                "Source: FMI. 2023–24: October unavailable, November partial. Missing is not zero.\nPercentages use valid consecutive-day comparisons, not all calendar days; increases are not measured snowfall.")


def plot_common(summary, figure_dir):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, col, title, ylabel in zip(axes, ["Snow_cover_pct", "Increase_pct"],
        ["Days with snow depth ≥1 cm", "Comparisons with depth increase >0 cm"],
        ["Valid snow-depth observations (%)", "Valid daily comparisons (%)"]):
        bars = ax.bar(summary.index, summary[col].astype(float), color=COLORS)
        ax.bar_label(bars, fmt="%.1f%%", padding=3)
        ax.set(title=title, ylabel=ylabel, ylim=(0, 110))
        ax.grid(axis="y", alpha=0.2)
        ax.set_axisbelow(True)
    fig.suptitle("Compare the same calendar window in every winter", fontsize=15)
    save_figure(fig, figure_dir / "common_window_comparison.png",
                "Source: FMI. 10 November–30 April in each winter; leap day retained. First selected day excluded from changes.")


def plot_sensitivity(sensitivity, figure_dir):
    fig, ax = plt.subplots(figsize=(10, 5))
    for (winter, group), color in zip(sensitivity.groupby("Winter"), cycle(COLORS)):
        ax.plot(group["Threshold_cm"], group["Percent"], marker="o", linewidth=2, color=color, label=winter)
    ax.set(title="Larger snow-depth increases are less frequent", xlabel="Minimum daily depth increase (cm)",
           ylabel="Valid daily comparisons (%)", xticks=sorted(sensitivity["Threshold_cm"].unique()), ylim=(0, min(100, max(30, sensitivity["Percent"].max() * 1.15))))
    ax.legend(title="Winter")
    ax.grid(alpha=0.2)
    save_figure(fig, figure_dir / "threshold_sensitivity.png",
                "Source: FMI. Common window: 10 November–30 April each winter.\nThresholds are illustrative, not official clearing triggers or measured snowfall.")


def plot_magnitudes(magnitudes, figure_dir):
    order = ["0 to <3 cm", "3 to <5 cm", "≥5 cm"]
    chart = magnitudes.pivot(index="Winter", columns="Magnitude", values="Share_of_positive_changes_pct")[order]
    counts = magnitudes.pivot(index="Winter", columns="Magnitude", values="Days")[order]
    ax = chart.plot.bar(stacked=True, figsize=(10, 5), color=["#C6DEE0", "#398D94", "#164A50"])
    for container, column in zip(ax.containers, order):
        ax.bar_label(container, labels=[f"{int(x)} days" if x else "" for x in counts[column]],
                     label_type="center", fontsize=10, color="white" if column == "≥5 cm" else "black")
    ax.set(title="Size of the observed positive snow-depth changes", xlabel="Winter", ylabel="Share of positive-change days (%)", ylim=(0, 100))
    ax.tick_params(axis="x", rotation=0)
    ax.legend(title="Daily depth change", bbox_to_anchor=(1.02, 1), loc="upper left")
    save_figure(ax.figure, figure_dir / "increase_magnitudes.png",
                "Source: FMI. Common window: 10 November–30 April. Labels show day counts.\nDenominator: positive-change days only; this chart does not show frequency across all winter days.")


def export_interactive(data, output_dir):
    fig = go.Figure()
    for (winter, group), color in zip(data.groupby("Winter"), cycle(COLORS)):
        series = group.set_index("Date")["Snow_depth_cm"]
        series = series.reindex(pd.date_range(series.index.min(), series.index.max()))
        fig.add_trace(go.Scatter(x=series.index, y=series.values, mode="lines", name=winter,
            line={"color": color}, connectgaps=False,
            hovertemplate="%{x|%d %b %Y}<br>Snow depth: %{y:.0f} cm<extra>%{fullData.name}</extra>"))
    fig.update_layout(title="Oulu Kaukovainio: daily snow depth (FMI)",
        xaxis_title="Date", yaxis_title="Snow depth (cm)", template="plotly_white",
        xaxis={"rangeslider": {"visible": True}}, yaxis={"rangemode": "tozero"},
        annotations=[dict(text="October–April only; 2023–24 is partial. Summer gaps are excluded periods.",
                          x=0, y=1.1, xref="paper", yref="paper", showarrow=False, xanchor="left")])
    fig.write_html(output_dir / "interactive_snow_depth.html", include_plotlyjs=True, auto_open=False)
    return fig
