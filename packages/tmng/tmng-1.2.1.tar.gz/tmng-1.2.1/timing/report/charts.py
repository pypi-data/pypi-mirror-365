# path: timing/report/charts.py (replace the whole file)
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

PLOTLY_THEME = "plotly_dark"


def _assign_gantt_lanes(df_group: pd.DataFrame) -> pd.DataFrame:
    """
    Assigns a non-overlapping "lane" to each event within a group (e.g., a marker_name).
    This is the core logic to prevent bars from rendering on top of each other.
    """
    df_group = df_group.sort_values(by="start_time", ascending=True)

    # lanes will store the end time of the last event placed in that lane.
    lanes = []
    lane_assignments = []

    for _, event in df_group.iterrows():
        placed = False
        # Find the first lane that is free (the event starts after the lane's last event ended)
        for i, lane_end_time in enumerate(lanes):
            if event["start_time"] >= lane_end_time:
                lanes[i] = event["end_time"]  # Occupy this lane
                lane_assignments.append(i)
                placed = True
                break

        # If no free lanes were found, create a new one.
        if not placed:
            lanes.append(event["end_time"])
            lane_assignments.append(len(lanes) - 1)

    df_group["lane"] = lane_assignments
    return df_group


def create_gantt_chart(df: pd.DataFrame) -> go.Figure:
    """
    Creates a highly usable Gantt chart grouped by Marker Name and sorted by the
    first appearance of each marker. The Y-axis is reversed to show events in a
    natural top-to-bottom chronological order.
    """
    df_gantt = df[df["duration_ms"].notna()].copy()
    if df_gantt.empty:
        return go.Figure()

    # 1. Find the first start_time for each marker_name
    df_gantt["marker_start_time"] = df_gantt.groupby("marker_name")[
        "start_time"
    ].transform("min")

    # 2. Apply the lane assignment algorithm to each marker group
    df_gantt = df_gantt.groupby("marker_name", group_keys=False).apply(
        _assign_gantt_lanes
    )

    # 3. Create the descriptive Y-axis label
    df_gantt["y_label"] = df_gantt["marker_name"]

    # 4. Sort the entire dataframe to ensure Plotly renders the Y-axis chronologically
    df_gantt.sort_values(
        by=["marker_start_time", "marker_name", "lane", "start_time"],
        ascending=True,
        inplace=True,
    )

    fig = px.timeline(
        df_gantt,
        x_start="start_time",
        x_end="end_time",
        y="y_label",
        color="marker_name",
        custom_data=["id"],
        hover_name="label",
        title="Performance Timing Gantt Chart (Timeline by Marker with Lanes)",
    )

    # Improve layout and readability
    fig.update_layout(
        template=PLOTLY_THEME,
        xaxis_title="Time",
        yaxis_title="Marker Name and Lane",
        yaxis=dict(
            title="Marker Name and Lane",
            type="category",
            categoryorder="trace",
            autorange="reversed",  # --- THIS IS THE FIX ---
        ),
        height=max(600, len(df_gantt["y_label"].unique()) * 25 + 150),
        margin=dict(l=300, r=50, t=80, b=50),
        legend=dict(
            title="Marker Names",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )

    # Disable the default hover text, as we use a custom modal on click.
    fig.update_traces(hovertemplate=None, hoverinfo="none")

    return fig


def create_flame_graph(df: pd.DataFrame) -> go.Figure:
    """Creates an interactive Flame Graph to show hierarchy."""
    df_flame = df[df["duration_ms"].notna()].copy()
    if df_flame.empty:
        return go.Figure()

    df_flame.sort_values(by="start_time", inplace=True)
    df_flame["parent"] = ""
    stack = []

    events_dict = df_flame.to_dict("index")

    for i, event_row in df_flame.iterrows():
        event = events_dict[i]
        while stack and events_dict[stack[-1]]["end_time"] <= event["start_time"]:
            stack.pop()
        if stack:
            df_flame.loc[i, "parent"] = events_dict[stack[-1]]["id"]
        stack.append(i)

    chart_height = max(600, len(df_flame["marker_name"].unique()) * 50)
    fig = px.icicle(
        df_flame,
        ids="id",
        parents="parent",
        names="label",
        values="duration_ms",
        title="Performance Timing Flame Graph (Hierarchy View)",
        custom_data=["id"],
        color="duration_ms",
        color_continuous_scale="RdBu_r",
    )
    fig.update_layout(
        template=PLOTLY_THEME, height=chart_height, margin=dict(t=50, l=25, r=25, b=25)
    )
    fig.update_traces(hovertemplate=None, hoverinfo="none")
    return fig
