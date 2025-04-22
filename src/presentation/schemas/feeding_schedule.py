from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class FoodTypeEnum(str, Enum):
    meat       = "meat"
    vegetables = "vegetables"
    fruits     = "fruits"
    fish_food  = "fish_food"

class FeedingScheduleCreate(BaseModel):
    animal_id: int
    feeding_time: datetime
    food_type: FoodTypeEnum

class FeedingScheduleRead(BaseModel):
    id: int
    animal_id: int
    feeding_time: datetime
    food_type: FoodTypeEnum
    is_completed: bool

    model_config = {"from_attributes": True}  # Pydantic v2
