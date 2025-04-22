# src/application/zoo_statistics_service.py

from typing import Dict
from src.infrastructure.animal_repository import AnimalRepository
from src.infrastructure.enclosure_repository import EnclosureRepository

class ZooStatisticsService:
    def __init__(
        self,
        animal_repo: AnimalRepository,
        enclosure_repo: EnclosureRepository
    ):
        self.animal_repo = animal_repo
        self.enclosure_repo = enclosure_repo

    def total_animals(self) -> int:
        return len(self.animal_repo.list_all())

    def free_enclosures_count(self) -> int:
        return sum(
            1
            for enc in self.enclosure_repo.list_all()
            if len(enc.animal_ids) < enc.capacity.value
        )

    def occupied_enclosures_count(self) -> int:
        return sum(
            1
            for enc in self.enclosure_repo.list_all()
            if len(enc.animal_ids) > 0
        )

    def animals_by_type(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for a in self.animal_repo.list_all():
            t = a.animal_type.value
            counts[t] = counts.get(t, 0) + 1
        return counts

    def unassigned_animals_count(self) -> int:
        """
        Сколько животных созданы в системе,
        но не помещены ни в один вольер.
        """
        # собираем все ID, которые уже в вольерах
        assigned = {
            aid
            for enc in self.enclosure_repo.list_all()
            for aid in enc.animal_ids
        }
        # считаем всех животных, id которых нет в assigned
        return sum(
            1
            for a in self.animal_repo.list_all()
            if a.id not in assigned
        )
