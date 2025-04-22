# src/presentation/routers/feeding_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime

from src.infrastructure.animal_repository import AnimalRepository
from src.presentation.schemas.feeding_schedule import (
    FeedingScheduleCreate,
    FeedingScheduleRead
)
from src.application.di import injector
from src.application.feeding_organization_service import FeedingOrganizationService
from src.domain.models.feeding_schedule import FeedingSchedule as DomainFS
from src.domain.models.animal import FoodType as DomainFoodType


def get_service() -> FeedingOrganizationService:
    return injector.get(FeedingOrganizationService)


def get_animal_repo() -> AnimalRepository:
    return injector.get(AnimalRepository)


feeding_router = APIRouter(
)


@feeding_router.get("/", response_model=List[FeedingScheduleRead])
def list_schedules(
    svc: FeedingOrganizationService = Depends(get_service)
):
    """
    Получить список всех расписаний кормления.
    """
    schedules = svc.schedule_repo.list_all()
    return [
        FeedingScheduleRead(
            id=s.id,
            animal_id=s.animal_id,
            feeding_time=s.feeding_time,
            food_type=s.food_type.value,
            is_completed=s.is_completed
        )
        for s in schedules
    ]


@feeding_router.post("/", response_model=FeedingScheduleRead, status_code=status.HTTP_201_CREATED)
def create_schedule(
    data: FeedingScheduleCreate,
    svc: FeedingOrganizationService = Depends(get_service),
    animal_repo: AnimalRepository = Depends(get_animal_repo),
):
    """
    Добавить новое кормление в расписание.
    """
    if not animal_repo.get_by_id(data.animal_id):
        raise HTTPException(status_code=404, detail=f"Животное с id = {data.animal_id} не найдено")

    dom = DomainFS(
        id=None,  # автогенерация в репозитории
        animal_id=data.animal_id,
        feeding_time=data.feeding_time,
        food_type=DomainFoodType(data.food_type.value),
    )
    try:
        svc.schedule_repo.add(dom)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    # Возвращаем модель чтения, где уже есть id и is_completed=False

    return FeedingScheduleRead(
        id=dom.id,
        animal_id=dom.animal_id,
        feeding_time=dom.feeding_time,
        food_type=dom.food_type.value,
        is_completed=dom.is_completed,
    )


@feeding_router.put("/{schedule_id}", response_model=FeedingScheduleRead)
def change_schedule(
    schedule_id: int,
    new_time: datetime = None,
    new_food: str = None,
    svc: FeedingOrganizationService = Depends(get_service)
):
    """
    Изменить время и/или тип пищи в расписании.
    """
    sched = svc.schedule_repo.get_by_id(schedule_id)
    if not sched:
        raise HTTPException(status_code=404, detail="Schedule not found")
    try:
        sched.change_schedule(new_time, svc.schedule_repo.get_by_id(
            schedule_id).food_type if new_food is None else new_food)
        svc.schedule_repo.update(sched)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return FeedingScheduleRead(
        id=sched.id,
        animal_id=sched.animal_id,
        feeding_time=sched.feeding_time,
        food_type=sched.food_type.value,
        is_completed=sched.is_completed
    )


@feeding_router.post("/{schedule_id}/complete", response_model=FeedingScheduleRead)
def complete_feeding(
    schedule_id: int,
    svc: FeedingOrganizationService = Depends(get_service)
):
    """
    Отметить кормление выполненным.
    """
    sched = svc.schedule_repo.get_by_id(schedule_id)
    if not sched:
        raise HTTPException(status_code=404, detail=f"Расписания с id {schedule_id} не найдено")
    sched.mark_completed()
    svc.schedule_repo.update(sched)
    return FeedingScheduleRead(
        id=sched.id,
        animal_id=sched.animal_id,
        feeding_time=sched.feeding_time,
        food_type=sched.food_type.value,
        is_completed=sched.is_completed
    )
