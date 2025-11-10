import matplotlib.pyplot as plt

def plot_top10_sites_by_downtime(df):
    # Aggregate top 10 sites
    top_sites = (
        df.groupby("siteid")["duration_minutes"]
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
    ax.barh(y_positions, values, height=0.7, color="#4DA8DA", edgecolor="black")

    # Add value labels
    for i, value in enumerate(values):
        offset = value * 0.02  # 2% of the bar length
        ax.text(value + offset, i, f"{value:.2f}", va="center", ha="left", fontsize=10, color="black")

    # Set y-axis labels
    ax.set_yticks(y_positions)
    ax.set_yticklabels(labels)

    # Style
    ax.set_xlabel("Total Downtime (minutes)")
    ax.set_ylabel("Site ID")
    ax.set_title("Top 10 Sites by Downtime", fontsize=14, weight="bold")
    ax.invert_yaxis()
    ax.set_facecolor("none")
    fig.tight_layout()

    # Remove spines
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    return fig