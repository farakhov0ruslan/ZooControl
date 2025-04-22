from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class GenderEnum(str, Enum):
    male = "male"
    female = "female"


class AnimalTypeEnum(str, Enum):
    predator = "predator"
    herbivore = "herbivore"
    bird = "bird"
    fish = "fish"


class FoodTypeEnum(str, Enum):
    meat = "meat"
    vegetables = "vegetables"
    fruits = "fruits"
    fish_food = "fish_food"


class AnimalCreate(BaseModel):
    """
    Для создания — без поля id: оно будет сгенерировано репозиторием.
    """
    name: str
    birth_date: datetime
    gender: GenderEnum
    animal_type: AnimalTypeEnum
    favorite_food: FoodTypeEnum
    is_healthy: bool = True


class AnimalRead(AnimalCreate):
    """
    Для чтения/ответа — здесь уже будет поле id.
    """
    id: int

    class Config:
        orm_mode = True
