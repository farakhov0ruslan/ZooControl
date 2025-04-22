**Отчёт по выполнению Д/З №2**

---

## 1. Реализация требуемого функционала

| **Пункт ТЗ**                                                                                            | **Где реализовано**                                                                                                                  |
|---------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| **Управление животными**                                                                                |                                                                                                                                      |
| • Добавить новое животное                                                                               | `src/presentation/routers/animal_router.py`: метод `POST /animals/` <br> `src/domain/models/animal.py`: конструктор `Animal` и VO `BirthDate` <br> `src/infrastructure/animal_repository.py`: `add()` недефолтные id, автогенерация  |
| • Удалить животное                                                                                      | `src/presentation/routers/animal_router.py`: метод `DELETE /animals/{id}` <br> `AnimalRepository.remove()`                            |
| • Просмотреть список животных                                                                           | `src/presentation/routers/animal_router.py`: метод `GET /animals/` <br> `AnimalRepository.list_all()`                                 |
|                                                                                                         |                                                                                                                                      |
| **Управление вольерами**                                                                                |                                                                                                                                      |
| • Добавить новый вольер                                                                                 | `src/presentation/routers/enclosure_router.py`: `POST /enclosures/` <br> `src/domain/models/enclosure.py`: `Enclosure` и VO `Capacity`, `EnclosureSize` <br> `src/infrastructure/enclosure_repository.py`: `add()` |
| • Удалить вольер                                                                                        | `DELETE /enclosures/{id}` в `enclosure_router.py` <br> `EnclosureRepository.remove()`                                                  |
| • Просмотреть все вольеры                                                                               | `GET /enclosures/` в `enclosure_router.py` <br> `EnclosureRepository.list_all()`                                                      |
|                                                                                                         |                                                                                                                                      |
| **Перемещение животных между вольерами**                                                                |                                                                                                                                      |
| • Endpoint `/animals/{id}/transfer/{enclosure_id}`                                                      | `src/presentation/routers/animal_router.py`: `transfer_animal()` <br> `src/application/animal_transfer_service.py`: метод `transfer()`  |
|                                                                                                         |                                                                                                                                      |
| **Расписание кормлений**                                                                                |                                                                                                                                      |
| • Добавить новое кормление                                                                             | `POST /feedings/` в `src/presentation/routers/feeding_router.py` <br> `src/domain/models/feeding_schedule.py`: `FeedingSchedule` и VO  |
| • Просмотреть расписание                                                                                | `GET /feedings/` в `feeding_router.py`                                                                                                 |
| • Изменить расписание (время/тип пищи)                                                                  | `PUT /feedings/{id}` в `feeding_router.py` <br> `FeedingSchedule.change_schedule()`                                                   |
| • Отметить кормление выполненным                                                                       | `POST /feedings/{id}/complete` в `feeding_router.py` <br> `FeedingSchedule.mark_completed()`                                          |
|                                                                                                         |                                                                                                                                      |
| **Статистика зоопарка**                                                                                 |                                                                                                                                      |
| • Общее число животных                                                                                  | `GET /stats/total_animals` в `src/presentation/routers/stats_router.py` <br> `ZooStatisticsService.total_animals()`                   |
| • Кол‑во свободных / занятых вольеров / животных без вольера / животных по типам                        | Эндпоинты в `stats_router.py` и методы в `src/application/zoo_statistics_service.py`:<br>– `free_enclosures_count()`<br>– `occupied_enclosures_count()`<br>– `unassigned_animals_count()`<br>– `animals_by_type()` |

**Дополнительно**  
- **In‑memory хранилище**: все репозитории (`AnimalRepository`, `EnclosureRepository`, `FeedingScheduleRepository`) хранят данные в Python‑словарях .  
- **Swagger / OpenAPI‑документация**: автоматически доступна по `GET /docs` и `GET /openapi.json` благодаря FastAPI. Через неё проверяли все CRUD‑эндпоинты, перемещения и статистику.

---

## 2. Применённые концепции Domain‑Driven Design и принципы Clean Architecture

### 2.1. DDD

1. **Entities**:  
   – `Animal`, `Enclosure`, `FeedingSchedule` в `src/domain/models` .  
2. **Value Objects** для «примитивов» с валидацией:  
   – `BirthDate` (дата рождения, не в будущем),<br>   `EnclosureSize` (положительная площадь),<br>   `Capacity` (положительная вместимость) .  
3. **Инкапсуляция бизнес‑правил внутри доменных объектов**:  
   – `Enclosure.add_animal()` проверяет вместимость и соответствие типа животного вольеру;  
   – `FeedingSchedule.change_schedule()` сбрасывает `is_completed`;  
   – `FeedingSchedule.mark_completed()` меняет статус;  
   – `BirthDate.__post_init__()` проверяет, что дата ≤ сегодня.  
4. **Доменные события**:  
   – `AnimalMovedEvent`, `FeedingTimeEvent` в `src/domain/events` .  

### 2.2. Clean Architecture

1. **Разделение на слои**:  
   - **Domain** (ядро, без внешних зависимостей) .  
   - **Application** (сервисы, orchestration) зависит только от Domain и абстракций репозиториев/event‑publisher.  
   - **Infrastructure** (репозитории) зависит от Domain и Application‑интерфейсов (`BaseRepository<T,ID>`) .  
   - **Presentation** (FastAPI‑роутеры) зависит от Application.  
2. **Зависимости «внутрь»**: модули Domain не импортируют ничего из верхних слоёв; репозитории и сервисы импортируют только абстракции Domain и интерфейсы (`BaseRepository`, `EventPublisher`).  
3. **Инверсия зависимостей**:  
   - Интерфейсы `BaseRepository` и `EventPublisher` определены в Application/Domain, реализации — в Infrastructure/Application соответственно.  
   - DI‑контейнер (Injector + `AppModule`) связывает интерфейсы с конкретными классами.  
4. **Отсутствие «протекания» бизнес‑логики наружу**: роутеры лишь вызывают сервисы/репозитории и маппят DTO, а всё «тяжёлое» — в Domain/Service.

---
Добавим в отчёт отдельный раздел с чётким описанием слоёв и инструкцией по запуску проекта.

---

## Архитектура – слоёвое разделение

Проект строго разделён на четыре слоя по принципам Clean Architecture и DDD:

### 1. Domain (доменный слой)  
– **Сущности и Value Objects** (в папке `src/domain/models/`):  
  - `Animal` (+ Value Object `BirthDate`, `Gender`, `AnimalType`, `FoodType`)  
  - `Enclosure` (+ VO `EnclosureSize`, `Capacity`, `EnclosureType`)  
  - `FeedingSchedule` (+ VO `FoodType`)  
– **Доменные события** (в `src/domain/events/`):  
  - `AnimalMovedEvent`  
  - `FeedingTimeEvent`  
– **Интерфейсы**:  
  - `BaseRepository<T,ID>` – контракт для всех репозиториев (в Application или Infrastructure).  
  - `EventPublisher` – контракт для публикации доменных событий.

Все классы домена не знают про FastAPI, репозитории или остальную инфраструктуру. Валидация и бизнес‑правила («нет переполнения вольера», «дата рождения не в будущем», «сброс флага кормления») инкапсулированы внутри методов доменных объектов.

### 2. Application (прикладной слой)  
– **Сервисы** (в `src/application/`):  
  - `AnimalTransferService` – логика перемещения животных между вольерами;  
  - `FeedingOrganizationService` – расписание и выполнение кормлений;  
  - `ZooStatisticsService` – сбор статистики (включая новый `unassigned_animals_count`);  
– **EventPublisher** (реализация `FileEventPublisher`) – пишет доменные события в лог-файл.  
– **DI‑модуль** `AppModule` – связывает интерфейсы репозиториев и издателя с конкретными классами через Injector.

Сервисы работают только с доменными объектами и репозиториями через абстракции, не знают про HTTP.

### 3. Infrastructure (инфраструктурный слой)  
– **In‑memory репозитории** (`src/infrastructure/…Repository.py`):  
  - `AnimalRepository`  
  - `EnclosureRepository`  
  - `FeedingScheduleRepository`  
  – унаследованы от `BaseRepository` и отвечают за хранение/генерацию `id`.

Infrastructure‑модуль зависит от Domain‑коткрейтов, но не знает про FastAPI.

### 4. Presentation (слой представления / API)  
– **FastAPI‑роутеры** (`src/presentation/routers/…_router.py`):  
  - `animal_router` – CRUD + transfer;  
  - `enclosure_router` – CRUD вольеров;  
  - `feeding_router` – CRUD и управление расписанием кормлений;  
  - `stats_router` – статистика зоопарка.  
– **Pydantic‑схемы** (`src/presentation/schemas/*.py`): модели запросов и ответов;  
– **Mapper‑классы** (`src/presentation/mappers/*.py`): перевод DTO ↔ Domain.

Роутеры зависят только от Application‑сервисов и репозиториев через `Depends`.

---

## Запуск и тестирование


1. **Установка зависимостей**  
   Файл `requirements.txt` содержит (пример):
   ```text
   fastapi
   uvicorn[standard]
   injector
   pydantic
   pytest
   pytest-cov
   httpx
   ```
   Установите их:
   ```bash
   pip install -r requirements.txt
   ```

2. **Запуск приложения**  
   ```bash
   python main.py
   ```  
   После старта API-документация доступна по:
   - Swagger UI:  `http://127.0.0.1:8000/docs``  

3. **Запуск тестов и проверка покрытия**  
   ```bash
   pytest --cov=src --cov-report=html
   ```  
   После выполнения откройте `htmlcov/index.html` в браузере, чтобы увидеть подробный отчёт по покрытию.  

---

**Вывод**:  
Приложение соответствует требованиям ДЗ: реализованы все основные Use‑cases, чётко разделены слои по Clean Architecture, бизнес‑логика полностью инкапсулирована в доменные модели, а для примитивов использованы Value Objects. Реализован логгер событий.