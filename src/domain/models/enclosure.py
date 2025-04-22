from dataclasses import dataclass
from src.domain.models.animal import Animal
from enum import Enum
from typing import List, Optional


class EnclosureType(Enum):
    PREDATOR = "predator"
    HERBIVORE = "herbivore"
    BIRD = "bird"
    AQUARIUM = "fish"


@dataclass(frozen=True)
class EnclosureSize:
    area: float  # размер в квадратных метрах

    def __post_init__(self):
        if self.area <= 0:
            raise ValueError("Размер вольера должен быть положительным")


@dataclass(frozen=True)
class Capacity:
    value: int  # максимальное количество животных

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("Максимальная вместимость должна быть положительной")


@dataclass
class Enclosure:
    id: Optional[int]
    type: EnclosureType
    size: EnclosureSize
    animal_ids: List[int]
    capacity: Capacity
    is_clean: bool = True

    def add_animal(self, animal: Animal) -> None:
        if len(self.animal_ids) >= self.capacity.value:
            raise ValueError("Вольер переполнен: нельзя добавить больше животных")
        if animal.animal_type.value != self.type.value:
            raise ValueError(
                f"Неверный тип животного: {animal.animal_type.value} "
                f"не подходит для вольера {self.type.value}"
            )
            # собственно добавление
        self.animal_ids.append(animal.id)

    def remove_animal(self, animal_id_other: int) -> bool:
        # Предполагаем, что animals – это список сущностей Animal, у которых есть атрибут id
        for idx, animal_id in enumerate(self.animal_ids):
            if animal_id == animal_id_other:
                self.animal_ids.pop(idx)
                return True
        raise ValueError(f"Животное с id {animal_id_other} не найдено")

    def clean(self) -> None:
        self.is_clean = True

    def __str__(self) -> str:
        return (f"Enclosure(id={self.id}, type={self.type.value}, size={self.size.area} sq.m, "
                f"animals={self.animal_ids}, capacity={self.capacity.value}, "
                f"is_clean={self.is_clean})")
