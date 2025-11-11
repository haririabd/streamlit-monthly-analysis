import matplotlib.pyplot as plt

def format_duration(days):
    day = int(days // 1)
    remaining_hours = int((days % 1) * 24)
    return f"{day}d {remaining_hours}h"

def plot_top10_sites_by_downtime(df):
    # Aggregate top 10 sites
    top_sites = (
        df.groupby("siteid")["duration_days"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    # Prepare positions and values
    y_positions = range(len(top_sites))
    values = top_sites.values
    labels = top_sites.index

    # Create figure
    fig, ax = plt.subplots(figsize=(8, 4), facecolor="none")

    # Plot bars with reduced gap (height controls thickness)
    ax.barh(y_positions, values, height=0.8, color="#CE4DDA", edgecolor="black")

    # Add value labels
    for i, value in enumerate(values):
        offset = value * 0.02  # 2% of the bar length
        label = format_duration(value)

        ax.text(value + offset, i, label, va="center", ha="left", fontsize=10)

    # Set y-axis labels
    ax.set_yticks(y_positions)
    ax.set_yticklabels(labels)
    ax.tick_params(axis="y", length=0)  # ← removes the tick lines

    # Style
    ax.set_xlabel("Total Downtime (Days)")
    ax.set_ylabel("Site ID")
    ax.set_title("Top 10 Sites by Downtime", fontsize=14, weight="bold")
    ax.invert_yaxis()
    ax.set_facecolor("none")
    fig.tight_layout()

    # Remove spines
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    return fig