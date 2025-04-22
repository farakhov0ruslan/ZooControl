from dataclasses import dataclass
from datetime import datetime, timezone
from typing import  Optional
from enum import Enum


class AnimalType(Enum):
    Predator = "predator"
    Herbivore = "herbivore"
    Bird = "bird"
    Fish = "fish"


class FoodType(Enum):
    MEAT = "meat"  # мясо (подходит для хищников)
    VEGETABLES = "vegetables"  # овощи (подходит для травоядных)
    FRUITS = "fruits"  # фрукты (возможно, для некоторых видов)
    FISH_FOOd = "fish_food"


class InvalidBirthDateError(ValueError):
    pass


@dataclass(frozen=True)
class BirthDate:
    value: datetime

    def __post_init__(self):
        dt = self.value
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        # Сравниваем с текущей датой и временем в UTC
        if dt > datetime.now(timezone.utc):
            raise InvalidBirthDateError("Дата рождения не может быть в будущем")

    def __str__(self) -> str:
        # Удобное строковое представление, например, в формате ISO8601
        return self.value.isoformat()


class Gender(Enum):
    Male = "male"
    FEMALE = "female"


@dataclass
class Animal:
    id: Optional[int]
    animal_type: AnimalType
    name: str
    birth_date: BirthDate
    gender: Gender
    favorite_food: FoodType
    is_healthy: bool = True

    def feed(self, food: str) -> 'Animal':
        """
        Метод кормления животного.
        Доработать
        """
        print("")
        return self

    def heal(self):
        "Доработать"
        return self

    def move_to(self, new_enclosure: str) -> 'Animal':
        """
        Перемещает животное в новый вольер.
         Доработать
        """
        return self

    def __str__(self) -> str:
        return (
            f"Animal(id={self.id}, name={self.name}, birth_date={self.birth_date}, "
            f"gender={self.gender.value}, animal_type={self.animal_type.value})"
        )
