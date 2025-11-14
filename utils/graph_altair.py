import pandas as pd
import altair as alt

def format_duration(days):
    day = int(days // 1)
    remaining_hours = int((days % 1) * 24)
    return f"{day}d {remaining_hours}h"

def get_top_sites_by_downtime_df(df, top_n=10):
    # Aggregate max downtime per site
    top_sites = (
        df.groupby("siteid")["duration_days"]
        .max()
        .sort_values(ascending=False)
        .head(top_n)
    )

    # Clean and format
    durations = pd.to_numeric(top_sites.values, errors="coerce")
    readable = [format_duration(d) for d in durations]

    return pd.DataFrame({
        "SiteID": top_sites.index,
        "Max Downtime (days)": durations,
        "Readable Duration": readable
    })

# Chart
def plot_top10_sites_by_downtime_altair(df):
    chart_data = get_top_sites_by_downtime_df(df)

    base = alt.Chart(chart_data).encode(
        x=alt.X("Max Downtime (days):Q", title="Total Downtime (Days)"),
        y=alt.Y("SiteID:N", sort="-x", title="Site ID")
    )

    bars = base.mark_bar(color="#615fff").encode(
        tooltip=["SiteID", "Max Downtime (days)", "Readable Duration"]
    )

    labels = base.mark_text(
        align="left", baseline="middle", dx=3,
        color="#e2e8f0", font="Helvetica", fontSize=14
    ).encode(
        text="Readable Duration"
    )

    chart = (bars + labels).properties(
        title="Top 10 Sites with Highest Downtime",
        height=450
    ).configure_title(
        font="Helvetica",
        fontSize=18,
        fontWeight="bold",
        color="#e2e8f0"
    ).configure_axisY(
        labelFont="Arial",
        labelFontSize=14
    )

    return chart

# Table
def build_downtime_table(df):
    return get_top_sites_by_downtime_df(df)
