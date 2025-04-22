
from injector import Module, provider, singleton, Injector
from src.infrastructure.animal_repository import AnimalRepository
from src.infrastructure.enclosure_repository import EnclosureRepository
from src.infrastructure.feeding_schedule_repository import FeedingScheduleRepository
from src.application.animal_transfer_service import AnimalTransferService
from src.application.feeding_organization_service import FeedingOrganizationService
from src.application.zoo_statistics_service import ZooStatisticsService
from src.application.event_publisher import FileEventPublisher, EventPublisher


class AppModule(Module):
    @singleton
    @provider
    def provide_animal_repository(self) -> AnimalRepository:
        return AnimalRepository()

    @singleton
    @provider
    def provide_enclosure_repository(self) -> EnclosureRepository:
        return EnclosureRepository()

    @singleton
    @provider
    def provide_schedule_repository(self) -> FeedingScheduleRepository:
        return FeedingScheduleRepository()

    @singleton
    @provider
    def provide_event_publisher(self) -> EventPublisher:
        return FileEventPublisher()

    @singleton
    @provider
    def provide_animal_transfer_service(
        self,
        animal_repo: AnimalRepository,
        enclosure_repo: EnclosureRepository,
        event_publisher: EventPublisher,
    ) -> AnimalTransferService:
        return AnimalTransferService(animal_repo, enclosure_repo, event_publisher)

    @singleton
    @provider
    def provide_feeding_organization_service(
        self,
        schedule_repo: FeedingScheduleRepository,
        event_publisher: EventPublisher,
    ) -> FeedingOrganizationService:
        return FeedingOrganizationService(schedule_repo, event_publisher)

    @singleton
    @provider
    def provide_zoo_statistics_service(
        self,
        animal_repo: AnimalRepository,
        enclosure_repo: EnclosureRepository,
    ) -> ZooStatisticsService:
        return ZooStatisticsService(animal_repo, enclosure_repo)

injector = Injector([AppModule()])