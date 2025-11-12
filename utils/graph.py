import matplotlib.pyplot as plt
import pandas as pd

def format_duration(days):
    day = int(days // 1)
    remaining_hours = int((days % 1) * 24)
    return f"{day}d {remaining_hours}h"

# Aggregate top 10 sites
def get_top_sites_by_downtime(df, top_n=10):
    top_sites = (
        df.groupby("siteid")["duration_days"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
    )
    return top_sites

def plot_top10_sites_by_downtime(df):
    # The aggregate
    top_sites = get_top_sites_by_downtime(df)

    # Prepare positions and values
    y_positions = range(len(top_sites))
    values = top_sites.values
    labels = top_sites.index

    # Create figure
    fig, ax = plt.subplots(figsize=(8, 3.5), facecolor="none")

    # Plot bars with reduced gap (height controls thickness)
    ax.barh(y_positions, values, height=0.8, color="#CE4DDA", edgecolor="black")

    # Add value labels
    for i, value in enumerate(values):
        offset = 0.3  # 2% of the bar length
        label = format_duration(value)

        ax.text(value + offset, i, label, va="center", ha="left", fontsize=10)

    # Set y-axis labels
    ax.set_yticks(y_positions)
    ax.set_yticklabels(labels)
    ax.tick_params(axis="y", length=0)  # ← removes the tick lines

    # Style
    ax.set_xlabel("Total Downtime (Days)")
    ax.set_ylabel("Site ID")
    ax.set_title("Top 10 Sites by Downtime")
    ax.invert_yaxis()
    ax.set_facecolor("none")
    fig.tight_layout()

    # Remove spines
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    return fig

def build_downtime_table(df):
    top_sites = get_top_sites_by_downtime(df)
    
    table = pd.DataFrame({
        "SiteID": top_sites.index,
        "Total Downtime (days)": top_sites.values,
        "Readable Duration": [format_duration(d) for d in top_sites.values]
    })
    
    return table