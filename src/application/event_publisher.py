# src/application/event_publisher.py

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

class EventPublisher(ABC):
    @abstractmethod
    def publish(self, event: Any) -> None:
        """Опубликовать доменное событие."""
        pass

class FileEventPublisher(EventPublisher):
    def __init__(self, filepath: str = "zoo_events.log"):
        self.filepath = filepath

    def publish(self, event: Any) -> None:
        # Простая запись: ISO‑тайм + строковое представление события
        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write(f"{datetime.utcnow().isoformat()} | {event}\n")