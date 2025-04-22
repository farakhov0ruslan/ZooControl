from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.domain.models.animal import FoodType


@dataclass(frozen=True)
class FeedingTimeEvent:
    schedule_id: int
    animal_id: int
    scheduled_time: datetime
    food_type: FoodType
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
