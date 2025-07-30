# path: timing/report/builder.py (replace the whole file)
from pathlib import Path
from timing.report import data, tables, html

OUTPUT_HTML_PATH = Path.cwd() / "timing_dashboard.html"


def generate_dashboard(output_path: str = str(OUTPUT_HTML_PATH)):
    """Main function to generate and save the advanced dashboard."""
    print("--- Generating Advanced Timing Dashboard ---")
    try:
        df = data.load_data_from_db()
        if df.empty:
            print("No completed timing events found. Dashboard not generated.")
            return
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    # --- NEW: Prepare data for the dynamic UI ---
    # Get all available tag keys for the "Group By" dropdown
    tag_keys = sorted(
        [col.replace("tags.", "") for col in df.columns if col.startswith("tags.")]
    )

    # The entire dataframe is passed to the frontend for dynamic rendering
    all_events_json = df.to_json(orient="records", date_format="iso")

    # Prepare data for the modal pop-up
    modal_data_df = df[["id", "label", "duration_ms", "tags_pretty"]].copy()
    event_data_map = modal_data_df.set_index("id").to_dict(orient="index")

    components = {
        "summary_table": tables.create_summary_table_html(df),
        "details_table_body": tables.create_details_table_body_html(df),
        "all_events_json": all_events_json,
        "event_data_map": event_data_map,
        "tag_keys": tag_keys,
    }

    print(f"Writing dashboard to: {output_path}")
    full_html = html.generate_html_scaffold(components)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"✅ Dashboard generated successfully! Open '{output_path}' in your browser.")
