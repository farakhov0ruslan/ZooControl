# main.py
from fastapi import FastAPI, Depends
from injector import Injector

from src.application.di import AppModule
from src.application.animal_transfer_service import AnimalTransferService
from src.application.feeding_organization_service import FeedingOrganizationService
from src.application.zoo_statistics_service import ZooStatisticsService

from src.presentation.routers.animal_router import animal_router
from src.presentation.routers.enclosure_router import enclosure_router
from src.presentation.routers.feeding_router import feeding_router
from src.presentation.routers.stats_router import stats_router


# создаём Injector и подключаем модуль
injector = Injector([AppModule()])

app = FastAPI(
    title="Zoo Management API",
    description="Управление животными, вольерами и расписанием кормлений",
    version="1.0.0",
    docs_url="/docs",     # Swagger UI
    redoc_url="/redoc",   # ReDoc
    openapi_url="/openapi.json"
)


# адаптеры для Depends
def get_animal_transfer_service() -> AnimalTransferService:
    return injector.get(AnimalTransferService)


def get_feeding_org_service() -> FeedingOrganizationService:
    return injector.get(FeedingOrganizationService)


def get_zoo_stats_service() -> ZooStatisticsService:
    return injector.get(ZooStatisticsService)


# подключаем роутеры
app.include_router(
    animal_router,
    prefix="/animals",
    tags=["animals"],
    dependencies=[Depends(get_animal_transfer_service)]
)

app.include_router(
    enclosure_router,
    prefix="/enclosures",
    tags=["enclosures"],
    dependencies=[Depends(get_animal_transfer_service)]
)

app.include_router(
    feeding_router,
    prefix="/feedings",
    tags=["feedings"],
    dependencies=[Depends(get_feeding_org_service)]
)

app.include_router(
    stats_router,
    prefix="/stats",
    tags=["stats"],
    dependencies=[Depends(get_zoo_stats_service)]
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
