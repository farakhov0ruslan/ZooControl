from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List

T = TypeVar('T')  # Тип сущности
ID = TypeVar('ID')  # Тип уникального идентификатора


class BaseRepository(ABC, Generic[T, ID]):
    def __init__(self):
        # будем хранить последнее сгенерированное целочисленное значение
        self._last_id: ID = 0

    def _generate_id(self) -> ID:
        """
        Возвращает новое значение ID (autoincrement).
        Предполагаем, что ID всегда int.
        """
        self._last_id += 1
        return self._last_id

    @abstractmethod
    def add(self, entity: T) -> None:
        """Добавить новую сущность в репозиторий."""
        pass

    @abstractmethod
    def get_by_id(self, entity_id: ID) -> T | None:
        """Получить сущность по её уникальному идентификатору. Вернуть None, если не найдено."""
        pass

    @abstractmethod
    def update(self, entity: T) -> None:
        """Обновить данные сущности в репозитории."""
        pass

    @abstractmethod
    def remove(self, entity: T) -> None:
        """Удалить сущность из репозитория."""
        pass

    @abstractmethod
    def list_all(self) -> List[T]:
        """Вернуть список всех сущностей репозитория."""
        pass
