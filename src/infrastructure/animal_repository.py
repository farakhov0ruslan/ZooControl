from typing import List, Dict
from src.domain.models.animal import Animal
from src.infrastructure.base_repository import BaseRepository


class AnimalRepository(BaseRepository[Animal, int]):
    def __init__(self):
        # Хранение животных в словаре, ключ – уникальный id
        super().__init__()
        self._animals: Dict[int, Animal] = {}

    def add(self, entity: Animal) -> None:
        if entity.id is None:
            entity.id = self._generate_id()

        if entity.id in self._animals:
            raise ValueError(f"Животное с  id {entity.id} уже существует.")
        self._animals[entity.id] = entity

    def get_by_id(self, entity_id: int) -> Animal | None:
        return self._animals.get(entity_id)

    def update(self, entity: Animal) -> None:
        if entity.id not in self._animals:
            raise ValueError(f"Животное с id {entity.id} не существует.")
        # Обновляем запись – так как объекты immutable, просто перезаписываем данные
        self._animals[entity.id] = entity

    def remove(self, entity: Animal) -> None:
        if entity.id in self._animals:
            del self._animals[entity.id]
        else:
            raise ValueError(f"Животное с id {entity.id} не существет.")

    def list_all(self) -> List[Animal]:
        return list(self._animals.values())
