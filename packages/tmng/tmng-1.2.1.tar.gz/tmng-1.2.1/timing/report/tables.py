import pandas as pd
import re


def create_summary_table_html(df: pd.DataFrame) -> str:
    """Creates an HTML table with aggregated stats per marker_name."""
    if df.empty:
        return ""
    summary = (
        df.groupby("marker_name")["duration_ms"]
        .agg(["count", "mean", "min", "max", "std", "sum"])
        .reset_index()
    )
    summary.columns = [
        "Marker Name",
        "Count",
        "Avg Duration (ms)",
        "Min (ms)",
        "Max (ms)",
        "Std Dev (ms)",
        "Total Time (ms)",
    ]
    for col in summary.columns[2:]:
        summary[col] = summary[col].round(2)
    return summary.to_html(
        index=False, table_id="summary-table", classes="display compact", border=0
    )


def create_details_table_body_html(df: pd.DataFrame) -> str:
    """Creates the HTML for the body of the details table (<tr> elements only)."""
    if df.empty:
        return '<tr><td valign="top" colspan="6" class="dataTables_empty">No data available in table for the selected filters</td></tr>'

    details_df = df[
        ["start_str", "marker_name", "process_id", "duration_ms", "id"]
    ].copy()
    details_df["Tags"] = df.apply(
        lambda row: f'<button class="context-button" data-event-id="{row["id"]}">View</button>',
        axis=1,
    )
    # Generate HTML from pandas, which includes <table> and <tbody> tags
    full_html_table = details_df.to_html(
        index=False, header=False, border=0, escape=False
    )

    # Extract only the content within the <tbody> tag (the <tr> elements)
    match = re.search(r"<tbody>(.*)</tbody>", full_html_table, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""  # Return empty string if no rows were generated
