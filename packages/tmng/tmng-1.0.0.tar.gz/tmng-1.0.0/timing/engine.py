# path: timing/engine.py (replace the whole file)
import logging
from uuid import UUID
from typing import Any, Dict, Optional

from .config import timing_settings
from .models import TimingEvent
from .storage.base import BaseStorage
from .storage.sqlite import SqliteStorage

logger = logging.getLogger(__name__)


class TimingEngine:
    def __init__(self) -> None:
        self._storage: Optional[BaseStorage] = None

    def get_storage(self) -> BaseStorage:
        if self._storage is None:
            self._storage = SqliteStorage(db_path=timing_settings.DB_PATH)
        return self._storage

    def is_enabled(self) -> bool:
        return timing_settings.IS_ENABLED

    def setup(self) -> None:
        if not self.is_enabled():
            print(
                "⚠️ Timing tool is disabled (TIMING_TOOL_ENABLED is not 'true'). Skipping DB setup."
            )
            return
        self.get_storage().setup()
        print(f"✅ Timing database setup complete for: {timing_settings.DB_PATH}")

    def start_event(self, marker_name: str, tags: Dict[str, Any]) -> UUID | None:
        try:
            # --- MODIFICATION: Pass tags to the event model ---
            event = TimingEvent(marker_name=marker_name, tags=tags)
            self.get_storage().write_start(event)
            return event.id
        except Exception as e:
            logger.error(
                f"TIMING: Failed to start event '{marker_name}': {e}", exc_info=True
            )
            return None

    def stop_event(self, event_id: UUID) -> None:
        try:
            event = self.get_storage().read(event_id)
            if not event:
                logger.warning(
                    f"TIMING: Could not find event with ID '{event_id}' to stop."
                )
                return
            event.stop()
            self.get_storage().write_stop(event)
            # --- MODIFICATION: Log tags instead of context ---
            tags_str = f" (Tags: {event.tags})" if event.tags else ""
            logger.info(
                f"TIMING: '{event.marker_name}' took {event.duration_ms:.2f}ms.{tags_str}"
            )
        except Exception as e:
            logger.error(
                f"TIMING: Failed to stop event '{event_id}': {e}", exc_info=True
            )


_engine_instance: Optional[TimingEngine] = None


def get_engine() -> TimingEngine:
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = TimingEngine()
    return _engine_instance
