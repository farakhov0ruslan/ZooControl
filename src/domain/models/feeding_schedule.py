from src.domain.models.animal import FoodType
from datetime import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class FeedingSchedule:
    id: Optional[int]
    animal_id: int
    feeding_time: datetime
    food_type: FoodType
    is_completed: bool = False

    def change_schedule(self, new_feeding_time: datetime = None,
                        new_food_type: FoodType = None) -> None:
        """
        Изменяет расписание кормления. Если переданы новые значения,
        они подставляются; при изменении расписания флаг выполненности сбрасывается.
        """
        if new_feeding_time is not None:
            self.feeding_time = new_feeding_time

        if new_food_type is not None:
            self.food_type = new_food_type
        self.is_completed = False

    def mark_completed(self) -> None:
        """
        Отмечает, что кормление выполнено, возвращая новый объект со статусом is_completed = True.
        """
        self.is_completed = True

    def __str__(self) -> str:
        status = "completed" if self.is_completed else "pending"
        return (
            f"FeedingSchedule(animal_id={self.animal_id}, feeding_time={self.feeding_time.isoformat()}, "
            f"food_type={self.food_type.value}, status={status})")
