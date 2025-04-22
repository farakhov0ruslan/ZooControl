from typing import Dict, List, Optional
from src.infrastructure.base_repository import BaseRepository
from src.domain.models.feeding_schedule import FeedingSchedule


class FeedingScheduleRepository(BaseRepository[FeedingSchedule, int]):
    def __init__(self):
        # Хранилище in‑memory: ключ — id расписания
        super().__init__()
        self._schedules: Dict[int, FeedingSchedule] = {}

    def add(self, entity: FeedingSchedule) -> None:
        if entity.id is None:
            entity.id = self._generate_id()
        if entity.id in self._schedules:
            raise ValueError(f"Расписание кормления с id {entity.id} уже существует.")
        self._schedules[entity.id] = entity

    def get_by_id(self, entity_id: int) -> Optional[FeedingSchedule]:
        return self._schedules.get(entity_id)

    def update(self, entity: FeedingSchedule) -> None:
        if entity.id not in self._schedules:
            raise ValueError(f"Расписание кормления с id {entity.id} не существует.")
        self._schedules[entity.id] = entity

    def remove(self, entity: FeedingSchedule) -> None:
        if entity.id in self._schedules:
            del self._schedules[entity.id]
        else:
            raise ValueError(f"Расписание кормления с id {entity.id} не найдено.")

    def list_all(self) -> List[FeedingSchedule]:
        return list(self._schedules.values())
