# path: timing/report/data.py (replace the whole file)
import json
import logging
from typing import Optional

import pandas as pd

from ..config import timing_settings
from ..storage.sqlite import SqliteStorage

logger = logging.getLogger(__name__)


def _human_tags(tags: Optional[dict]) -> str:
    """Pretty JSON for modal display."""
    try:
        return json.dumps(tags or {}, indent=2, ensure_ascii=False)
    except Exception as exc:
        logger.warning("Failed to pretty‑print tags: %s", exc)
        return "{}"


def load_data_from_db() -> pd.DataFrame:
    """
    Read all completed events, validate, and return a dataframe
    with exploded tags for powerful filtering and grouping.
    """
    db_path = timing_settings.DB_PATH
    if not db_path.exists():
        raise FileNotFoundError(f"Timing DB not found at {db_path}")

    storage = SqliteStorage(db_path=db_path)
    events = storage.read_all_completed()

    if not events:
        logger.info("No completed timing events found.")
        return pd.DataFrame()

    df = pd.DataFrame([e.model_dump() for e in events])

    # --- Data wrangling for charts & tables ---
    df["start_time"] = pd.to_datetime(df["start_utc"], utc=True)
    df["end_time"] = pd.to_datetime(df["end_utc"], utc=True, errors="coerce")
    df["duration_ms"] = df["duration_ms"].round(2)

    t0 = df["start_time"].min()
    df["start_ms_relative"] = ((df["start_time"] - t0).dt.total_seconds() * 1000).round(
        2
    )
    df["start_str"] = df["start_ms_relative"].astype(str) + " ms"

    # --- MODIFICATION: Handle tags ---
    df["tags_pretty"] = df["tags"].apply(_human_tags)
    df["id"] = df["id"].astype(str)

    # Explode tags into their own columns for filtering (e.g., 'tags.action', 'tags.chain')
    tags_df = pd.json_normalize(df["tags"]).add_prefix("tags.")
    df = pd.concat([df, tags_df], axis=1)

    # Create the main label
    df["label"] = df.apply(
        lambda r: f"{r['marker_name']} (PID: {r['process_id']}) ({r['duration_ms']:.2f} ms)",
        axis=1,
    )

    logger.info("Loaded %d validated events for dashboard.", len(df))
    return df
