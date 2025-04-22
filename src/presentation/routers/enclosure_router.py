# src/presentation/routers/enclosure_router.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from src.presentation.schemas.enclosure import EnclosureCreate, EnclosureRead
from src.presentation.mappers.enclosure_mapper import EnclosureMapper
from src.infrastructure.enclosure_repository import EnclosureRepository
from src.infrastructure.animal_repository import AnimalRepository
from src.application.di import injector

def get_enclosure_repo() -> EnclosureRepository:
    return injector.get(EnclosureRepository)

def get_animal_repo() -> AnimalRepository:
    return injector.get(AnimalRepository)

enclosure_router = APIRouter()

@enclosure_router.get("/", response_model=List[EnclosureRead])
def list_enclosures(
    repo: EnclosureRepository = Depends(get_enclosure_repo),
):
    """
    Получить список всех вольеров.
    """
    domain_enclosures = repo.list_all()
    return [EnclosureMapper.to_read(e) for e in domain_enclosures]

@enclosure_router.post(
    "/",
    response_model=EnclosureRead,
    status_code=status.HTTP_201_CREATED,
)
def create_enclosure(
    data: EnclosureCreate,
    repo: EnclosureRepository              = Depends(get_enclosure_repo),
    animal_repo: AnimalRepository          = Depends(get_animal_repo),
):
    """
    Создать новый вольер (с автоматическим присвоением id).
    Принимает список animal_ids, все они будут провалидированы.
    """
    try:
        domain_enclosure = EnclosureMapper.from_create(data, animal_repo)
        repo.add(domain_enclosure)
    except ValueError as e:
        # сюда попадут ошибки: не найден animal_id, переполнение или mismatch типов
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return EnclosureMapper.to_read(domain_enclosure)

@enclosure_router.delete(
    "/{enclosure_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_enclosure(
    enclosure_id: int,
    repo: EnclosureRepository = Depends(get_enclosure_repo),
):
    """
    Удалить вольер по ID.
    """
    enc = repo.get_by_id(enclosure_id)
    if not enc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enclosure not found",
        )
    repo.remove(enc)
    return None
