from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class AnimalMovedEvent:
    animal_id: int
    from_enclosure_id: int
    to_enclosure_id: int
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __str__(self) -> str:
        return (f"AnimalMovedEvent(animal_id={self.animal_id}, "
                f"from={self.from_enclosure_id}, to={self.to_enclosure_id})")
