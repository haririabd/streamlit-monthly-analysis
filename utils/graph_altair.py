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

# Explicit DataFrame construction here because we’re adding derived columns
# (like Readable Duration) alongside the aggregated values.
    return pd.DataFrame({
        "SiteID": top_sites.index,
        "Downtime in days": durations,
        "Readable Duration": readable
    })
    
def get_top_repeated_sites(df, top_n=10):
    site_counts = (
        df["siteid"]
        .value_counts()
        .reset_index()
    )
    site_counts.columns = ["SiteID", "Count"]
    
    return site_counts.head(top_n)

def get_repeated_sites_comparison(df, selected_period, previous_period, top_n=10):
    # Current month counts
    current_counts = (
        df[df["month"] == selected_period]["siteid"]
        .value_counts()
        .reset_index()
    )
    current_counts.columns = ["SiteID", selected_period.strftime("%b %Y")
]
    
    # Previous month counts
    last_counts = (
        df[df["month"] == previous_period]["siteid"]
        .value_counts()
        .reset_index()
    )
    last_counts.columns = ["SiteID", previous_period.strftime("%b %Y")]

    # Merge both
    merged = pd.merge(current_counts, last_counts, on="SiteID", how="left").fillna(0)

    # Keep top N sites by current month count
    merged = merged.sort_values(selected_period.strftime("%b %Y"), ascending=False).head(top_n)

    return merged

def reshape_for_altair(merged):
    chart_data = merged.melt(
        id_vars="SiteID",
        var_name="Month",
        value_name="Count"
    )
    return chart_data

# Chart
def plot_top10_sites_by_downtime_altair(df, selected_period):
    chart_data = get_top_sites_by_downtime_df(df)

    base = alt.Chart(chart_data).encode(
        x=alt.X("Downtime in days:Q", title="Total Downtime (Days)"),
        y=alt.Y("SiteID:N", sort="-x", title="SiteID")
    )

    bars = base.mark_bar(color="#8250c4").encode(
        tooltip=["SiteID", "Downtime in days", "Readable Duration"]
    )

    labels = base.mark_text(
        align="left", baseline="middle", dx=3,
        color="#e2e8f0", fontSize=14
    ).encode(
        text="Readable Duration"
    )

    month_label = selected_period.strftime("%B %Y")
    chart = (bars + labels).properties(
        title=f"Top 10 Highest Downtime for {month_label}",
        height=450
    ).configure_title(
        font="Helvetica",
        fontSize=18,
        fontWeight="bold",
        color="#e2e8f0"
    ).configure_axisX(
        ticks=False,
        domain=False,
        grid=True,
        gridDash=[4, 4]
    ).configure_axisY(
        labelFont="Arial",
        labelFontSize=14,
        labelPadding=5,
        ticks=False,
        domain=False
    ).configure_view(
        stroke=None
    )

    return chart

# Table
def build_downtime_table(df):
    return get_top_sites_by_downtime_df(df)

def plot_repeated_sites_comparison(df, selected_period, previous_period, top_n=10):
    merged = get_repeated_sites_comparison(df, selected_period, previous_period, top_n)
    chart_data = reshape_for_altair(merged)

    chart = (
        alt.Chart(chart_data)
        .mark_line(point=True)
        .encode(
            x=alt.X("SiteID:N", sort=list(merged["SiteID"]), title="SiteID"),
            y=alt.Y("Count:Q", title="Occurance"),
            color=alt.Color("Month:N", title=None,
                            scale=alt.Scale(range=["#8250c4", "#86c9c7"]),
                            legend=alt.Legend(
                                orient="top-right"
                                )
                            ),
            tooltip=["SiteID", "Month", "Count"]
        )
        .properties(
            title=f"Top {top_n} Repeated Sites by {selected_period.strftime('%b %Y')} and {previous_period.strftime('%b %Y')}",
            height=450
        )
        .configure_axisX(
        labelPadding=10,
        labelAngle=-30,   # slant labels at -45 degrees
        labelFont="Arial",
        labelFontSize=12,
        ticks=False,
        domain=False
        ).configure_axisY(
        labelPadding=5,
        ticks=False,
        domain=False,
        grid=True,
        gridDash=[4, 4]
        ).configure_title(
            font="Helvetica",
            fontSize=18,
            fontWeight="bold",
            color="#e2e8f0"
        ).configure_view(
            stroke=None
        )
    )

    return chart

def plot_top_repeated_sites_bar(df, selected_period, top_n=10):
    chart_data = get_top_repeated_sites(df, top_n)
    
    month_label = selected_period.strftime("%B %Y")
    chart = (
        alt.Chart(chart_data)
        .mark_bar(color="#8250c4")
        .encode(
            x=alt.X("Count:Q", title="Occurance"),
            y=alt.Y("SiteID:N", sort="-x", title="SiteID"),
            tooltip=[
                alt.Tooltip("SiteID:N", title="Site ID"),
                alt.Tooltip("Count:Q", title="Frequency")
            ]
        )
        .properties(
            title=f"Top {top_n} Most Repeated Sites for {month_label}",
            height=450
        )
        .configure_title(
            font="Helvetica",
            fontSize=18,
            fontWeight="bold",
            color="#e2e8f0"
        )
        .configure_axisX(
            labelFont="Arial",
            labelFontSize=12,
            ticks=False,
            domain=False,
            grid=True,
            gridDash=[4, 4]
        )
        .configure_axisY(
            labelFont="Arial",
            labelFontSize=14,
            labelPadding=5,
            ticks=False,
            domain=False
            
        ).configure_view(
            stroke=None
        )
    )

    return chart

    