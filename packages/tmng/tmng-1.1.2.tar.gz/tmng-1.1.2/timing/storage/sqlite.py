# path: timing/storage/sqlite.py (replace the whole file)
import json
import sqlite3
import logging
from pathlib import Path
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from ..models import TimingEvent
from .base import BaseStorage

logger = logging.getLogger(__name__)

# --- MODIFICATION: Replaced 'context' column with 'tags' ---
CREATE_SQL = """
CREATE TABLE IF NOT EXISTS timing_events (
    id              TEXT    PRIMARY KEY,
    marker_name     TEXT    NOT NULL,
    process_id      INTEGER NOT NULL,
    start_utc       TEXT    NOT NULL,
    end_utc         TEXT,
    start_perf_ns   INTEGER NOT NULL,
    duration_ms     REAL,
    tags            TEXT,
    UNIQUE(id, start_utc)
);
"""


class SqliteStorage(BaseStorage):
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as c:
            c.execute("PRAGMA journal_mode=WAL;")
            c.execute("PRAGMA synchronous = NORMAL;")
            c.execute(CREATE_SQL)

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path, timeout=30, isolation_level="IMMEDIATE")

    def setup(self) -> None:
        with self._conn() as c:
            c.execute(CREATE_SQL)

    def write_start(self, event: TimingEvent) -> None:
        with self._conn() as c:
            c.execute(
                "INSERT INTO timing_events (id, marker_name, process_id, start_utc, start_perf_ns, tags) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    str(event.id),
                    event.marker_name,
                    event.process_id,
                    event.start_utc.isoformat(),
                    event.start_perf_ns,
                    json.dumps(event.tags, ensure_ascii=False),
                ),
            )

    def read(self, event_id: UUID) -> Optional[TimingEvent]:
        with self._conn() as c:
            c.row_factory = sqlite3.Row
            row = c.execute(
                "SELECT * FROM timing_events WHERE id = ?", (str(event_id),)
            ).fetchone()
            if not row:
                return None
            return self._row_to_event(row)

    def write_stop(self, event: TimingEvent) -> None:
        with self._conn() as c:
            c.execute(
                "UPDATE timing_events SET end_utc = ?, duration_ms = ? WHERE id = ?",
                (
                    event.end_utc.isoformat() if event.end_utc else None,
                    event.duration_ms,
                    str(event.id),
                ),
            )

    def read_all_completed(self) -> List[TimingEvent]:
        with self._conn() as c:
            c.row_factory = sqlite3.Row
            rows = c.execute(
                "SELECT * FROM timing_events WHERE end_utc IS NOT NULL ORDER BY start_utc ASC"
            ).fetchall()
            return [self._row_to_event(r) for r in rows]

    @staticmethod
    def _row_to_event(row: sqlite3.Row) -> TimingEvent:
        data = dict(row)
        # --- MODIFICATION: Load 'tags' instead of 'context' ---
        data["tags"] = json.loads(data["tags"] or "{}")
        data["start_utc"] = datetime.fromisoformat(data["start_utc"])
        data["end_utc"] = (
            datetime.fromisoformat(data["end_utc"]) if data["end_utc"] else None
        )
        return TimingEvent.model_validate(data)
