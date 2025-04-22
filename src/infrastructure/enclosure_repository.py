from typing import Dict, List, Optional
from src.domain.models.enclosure import Enclosure
from src.infrastructure.base_repository import BaseRepository


class EnclosureRepository(BaseRepository[Enclosure, int]):
    def __init__(self):
        # Храним вольеры в словаре, где ключ – уникальный id вольера (int)
        super().__init__()
        self._enclosures: Dict[int, Enclosure] = {}

    def add(self, entity: Enclosure) -> None:
        if entity.id is None:
            entity.id = self._generate_id()
        if entity.id in self._enclosures:
            raise ValueError(f"Вольер с id {entity.id} уже существует.")
        self._enclosures[entity.id] = entity

    def get_by_id(self, entity_id: int) -> Optional[Enclosure]:
        return self._enclosures.get(entity_id)

    def update(self, entity: Enclosure) -> None:
        if entity.id not in self._enclosures:
            raise ValueError(f"Вольер с id {entity.id} не существует.")
        self._enclosures[entity.id] = entity

    def remove(self, entity: Enclosure) -> None:
        if entity.id in self._enclosures:
            del self._enclosures[entity.id]
        else:
            raise ValueError(f"Вольер с id {entity.id} не найден.")

    def list_all(self) -> List[Enclosure]:
        return list(self._enclosures.values())
