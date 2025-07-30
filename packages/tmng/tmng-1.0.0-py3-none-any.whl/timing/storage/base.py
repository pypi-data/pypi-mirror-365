# path: timing/storage/base.py
from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional, List
from ..models import TimingEvent


class BaseStorage(ABC):
    @abstractmethod
    def setup(self) -> None:
        pass

    @abstractmethod
    def write_start(self, event: TimingEvent) -> None:
        pass

    @abstractmethod
    def read(self, event_id: UUID) -> Optional[TimingEvent]:
        pass

    @abstractmethod
    def write_stop(self, event: TimingEvent) -> None:
        pass

    @abstractmethod
    def read_all_completed(self) -> List[TimingEvent]:
        pass
