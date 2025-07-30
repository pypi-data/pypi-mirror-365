# path: timing/models.py (replace the whole file)
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class TimingEvent(BaseModel):
    """
    One logical timing span with structured, queryable tags.
    """

    id: UUID = Field(default_factory=uuid4)
    marker_name: str
    process_id: int = Field(default_factory=os.getpid)

    start_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_utc: Optional[datetime] = None

    start_perf_ns: int = Field(default_factory=time.perf_counter_ns)
    duration_ms: Optional[float] = None

    # --- MODIFICATION: Replaced 'context' with 'tags' for structured grouping ---
    tags: Dict[str, Any] = Field(default_factory=dict)

    def stop(self) -> None:
        """Fill end_utc + duration_ms exactly once."""
        if self.end_utc is None:
            self.end_utc = datetime.now(timezone.utc)
            self.duration_ms = (time.perf_counter_ns() - self.start_perf_ns) / 1_000_000

    class Config:
        from_attributes = True
        validate_assignment = True
