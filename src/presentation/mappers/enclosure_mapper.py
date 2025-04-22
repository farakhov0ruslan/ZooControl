# src/presentation/mappers/enclosure_mapper.py

from typing import List
from src.domain.models.enclosure import (
    Enclosure as DomainEnclosure,
    EnclosureSize,
    Capacity,
    EnclosureType,
)
from src.presentation.schemas.enclosure import EnclosureCreate
from src.infrastructure.animal_repository import AnimalRepository


class EnclosureMapper:
    @staticmethod
    def from_create(
        dto: EnclosureCreate,
        animal_repo: AnimalRepository
    ) -> DomainEnclosure:
        """
        Преобразует EnclosureCreate в доменную модель Enclosure.
        Все проверки (существование животного, вместимость, тип) выполняются
        внутри доменной логики Enclosure.add_animal.
        """
        # При создании сразу передаём пустой список animal_ids
        domain = DomainEnclosure(
            id=None,
            type=EnclosureType(dto.type.value),
            size=EnclosureSize(dto.size),
            animal_ids=[],             # <-- вот здесь
            capacity=Capacity(dto.capacity),
            is_clean=dto.is_clean,
        )

        # Добавляем каждое животное через метод домена (валидация capacity & type)
        for aid in dto.animal_ids:
            animal = animal_repo.get_by_id(aid)
            if not animal:
                raise ValueError(f"Animal with id={aid} not found")
            domain.add_animal(animal)

        return domain

    @staticmethod
    def to_read(
        domain: DomainEnclosure
    ) -> dict:
        """
        Преобразует доменную модель Enclosure в словарь для Pydantic‑схемы.
        """
        return {
            "id":          domain.id,
            "type":        domain.type.value,
            "size":        domain.size.area,
            "capacity":    domain.capacity.value,
            "is_clean":    domain.is_clean,
            "animal_ids":  domain.animal_ids,
        }
