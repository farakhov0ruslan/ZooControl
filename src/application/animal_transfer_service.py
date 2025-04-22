from src.domain.events.animal_moved_event import AnimalMovedEvent
from src.domain.models.animal import Animal
from src.domain.models.enclosure import Enclosure
from src.infrastructure.base_repository import BaseRepository
from src.application.event_publisher import EventPublisher


class AnimalTransferService:
    def __init__(
        self,
        animal_repo: BaseRepository[Animal, int],
        enclosure_repo: BaseRepository[Enclosure, int],
        event_publisher: EventPublisher,
    ):
        self.animal_repo = animal_repo
        self.enclosure_repo = enclosure_repo
        self.event_publisher = event_publisher

    def transfer(self, animal_id: int, to_enclosure_id: int) -> None:
        # Получаем животное и вольер-назначение
        animal = self.animal_repo.get_by_id(animal_id)
        if not animal:
            raise ValueError(f"Животное с id={animal_id} не найдено.")
        to_enclosure = self.enclosure_repo.get_by_id(to_enclosure_id)
        if not to_enclosure:
            raise ValueError(f"Вольер с id={to_enclosure_id} не найден.")

        # Ищем текущий вольер, где содержится животное
        from_enclosure = None
        for enc in self.enclosure_repo.list_all():
            if any(a_id == animal_id for a_id in enc.animal_ids):
                from_enclosure = enc
                break
        if from_enclosure is None:
            raise ValueError(f"Животное id={animal_id} не находится ни в одном вольере.")

        # Убираем из старого и добавляем в новый
        from_enclosure.remove_animal(animal_id)
        to_enclosure.add_animal(animal)

        # Сохраняем изменения
        self.enclosure_repo.update(from_enclosure)
        self.enclosure_repo.update(to_enclosure)

        # Публикуем событие перемещения
        evt = AnimalMovedEvent(
            animal_id=animal_id,
            from_enclosure_id=from_enclosure.id,
            to_enclosure_id=to_enclosure.id,
        )
        self.event_publisher.publish(evt)
