from src.domain.events.feeding_time_event import FeedingTimeEvent
from src.domain.models.feeding_schedule import FeedingSchedule
from src.infrastructure.base_repository import BaseRepository
from src.application.event_publisher import EventPublisher
from datetime import datetime


class FeedingOrganizationService:
    def __init__(
        self,
        schedule_repo: BaseRepository[FeedingSchedule, int],
        event_publisher: EventPublisher,
    ):
        self.schedule_repo = schedule_repo
        self.event_publisher = event_publisher

    def schedule_feeding(
        self,
        schedule: FeedingSchedule
    ) -> None:
        """Добавить новое кормление в расписание."""
        self.schedule_repo.add(schedule)

    def change_schedule(
        self,
        schedule_id: int,
        new_time: datetime = None,
        new_food_type=None
    ) -> None:
        """Изменить время и/или тип корма для существующего расписания."""
        sched = self.schedule_repo.get_by_id(schedule_id)
        if sched is None:
            raise ValueError(f"Расписание id={schedule_id} не найдено.")
        sched.change_schedule(new_time, new_food_type)
        # при изменении флаг is_completed сбрасывается внутри метода
        self.schedule_repo.update(sched)

    def mark_completed(self, schedule_id: int) -> None:
        """Отметить выполнение кормления и опубликовать событие."""
        sched = self.schedule_repo.get_by_id(schedule_id)
        if sched is None:
            raise ValueError(f"Расписание id={schedule_id} не найдено.")
        updated = sched.mark_completed()
        self.schedule_repo.update(updated)

        evt = FeedingTimeEvent(
            schedule_id=schedule_id,
            animal_id=sched.animal_id,
            scheduled_time=sched.feeding_time,
            food_type=sched.food_type.value
        )
        self.event_publisher.publish(evt)
