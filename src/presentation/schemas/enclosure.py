# src/presentation/schemas/enclosure.py

from pydantic import BaseModel
from enum import Enum
from typing import List
from src.presentation.schemas.animal import AnimalRead


class EnclosureTypeEnum(str, Enum):
    predator = "predator"
    herbivore = "herbivore"
    bird = "bird"
    aquarium = "aquarium"


class EnclosureCreate(BaseModel):
    type: EnclosureTypeEnum
    size: float
    capacity: int
    animal_ids: List[int]
    is_clean: bool = True


class EnclosureRead(EnclosureCreate):
    id: int

    class Config:
        orm_mode = True
