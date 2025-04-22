# src/presentation/mappers/animal_mapper.py

from src.domain.models.animal import Animal as DomainAnimal, BirthDate, Gender, AnimalType, FoodType
from src.presentation.schemas.animal import AnimalCreate, AnimalRead


class AnimalMapper:
    @staticmethod
    def from_create(dto: AnimalCreate) -> DomainAnimal:
        """
        Преобразует Pydantic‑модель AnimalCreate в доменную модель Animal.
        ID при этом оставляем None, репозиторий проставит auto‑increment.
        """
        return DomainAnimal(
            id=None,
            name=dto.name,
            birth_date=BirthDate(dto.birth_date),
            gender=Gender(dto.gender.value),
            animal_type=AnimalType(dto.animal_type.value),
            favorite_food=FoodType(dto.favorite_food.value),
            is_healthy=dto.is_healthy,
        )

    @staticmethod
    def to_read(domain: DomainAnimal) -> AnimalRead:
        """
        Преобразует доменную модель Animal в Pydantic‑модель AnimalRead.
        """
        return AnimalRead(
            id=domain.id,
            name=domain.name,
            birth_date=domain.birth_date.value,
            gender=domain.gender.value,
            animal_type=domain.animal_type.value,
            favorite_food=domain.favorite_food.value,
            is_healthy=domain.is_healthy,
        )
