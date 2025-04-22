from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from src.presentation.schemas.animal import AnimalCreate, AnimalRead
from src.presentation.mappers.animal_mapper import AnimalMapper
from src.application.di import injector
from src.application.animal_transfer_service import AnimalTransferService
from src.domain.models.animal import InvalidBirthDateError

def get_animal_service() -> AnimalTransferService:
    return injector.get(AnimalTransferService)

animal_router = APIRouter()


@animal_router.get("/", response_model=List[AnimalRead])
def list_animals(
    service: AnimalTransferService = Depends(get_animal_service),
):
    """
    Получить список всех животных.
    """
    domain_animals = service.animal_repo.list_all()
    return [AnimalMapper.to_read(a) for a in domain_animals]


@animal_router.post("/", response_model=AnimalRead, status_code=status.HTTP_201_CREATED)
def create_animal(
    data: AnimalCreate,
    service: AnimalTransferService = Depends(get_animal_service),
):
    """
    Создать новое животное. id будет сгенерирован автоматически.
    """
    try:
        dom = AnimalMapper.from_create(data)
        service.animal_repo.add(dom)
    except InvalidBirthDateError as e:
        # Pydantic уже валидирует формат даты, но домен проверяет будущее время
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return AnimalMapper.to_read(dom)


@animal_router.delete("/{animal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_animal(
    animal_id: int,
    service: AnimalTransferService = Depends(get_animal_service),
):
    """
    Удалить животное по ID.
    """
    animal = service.animal_repo.get_by_id(animal_id)
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Animal not found",
        )
    service.animal_repo.remove(animal)
    return None


@animal_router.post(
    "/{animal_id}/transfer/{enclosure_id}",
    status_code=status.HTTP_200_OK,
)
def transfer_animal(
    animal_id: int,
    enclosure_id: int,
    service: AnimalTransferService = Depends(get_animal_service),
):
    """
    Переместить животное в другой вольер.
    """
    try:
        service.transfer(animal_id, enclosure_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return {"status": "ok"}
