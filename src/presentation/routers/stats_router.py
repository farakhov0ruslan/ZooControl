from fastapi import APIRouter, Depends
from typing import Dict

from src.application.di import injector
from src.application.zoo_statistics_service import ZooStatisticsService


def get_zoo_stats_service() -> ZooStatisticsService:
    return injector.get(ZooStatisticsService)


stats_router = APIRouter()


@stats_router.get("/total_animals", response_model=int, summary="Общее число животных")
def total_animals(service: ZooStatisticsService = Depends(get_zoo_stats_service)):
    """
    Возвращает общее количество животных в зоопарке.
    """
    return service.total_animals()


@stats_router.get("/free_enclosures", response_model=int, summary="Количество свободных вольеров")
def free_enclosures(service: ZooStatisticsService = Depends(get_zoo_stats_service)):
    """
    Возвращает количество вольеров, где есть хотя бы одно свободное место.
    """
    return service.free_enclosures_count()


@stats_router.get("/occupied_enclosures", response_model=int, summary="Количество занятых вольеров")
def occupied_enclosures(service: ZooStatisticsService = Depends(get_zoo_stats_service)):
    """
    Возвращает количество вольеров, где содержится хотя бы одно животное.
    """
    return service.occupied_enclosures_count()


@stats_router.get("/animals_by_type", response_model=Dict[str, int],
                  summary="Распределение животных по видам")
def animals_by_type(service: ZooStatisticsService = Depends(get_zoo_stats_service)):
    """
    Возвращает словарь, где ключ — тип животного, значение — количество.
    """
    return service.animals_by_type()

@stats_router.get("/unassigned_animals", summary="Животные без вольера")
def unassigned_animals(service: ZooStatisticsService = Depends(get_zoo_stats_service)) -> int:
    """
    Возвращает число животных, которые еще не помещены ни в один вольер.
    """
    return service.unassigned_animals_count()