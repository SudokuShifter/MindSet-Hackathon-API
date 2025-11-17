from dishka import Scope, Container, Provider, provide, make_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from src.clients.base_client import BaseClient
from src.clients.llm_client import LLMClient
from src.interfaces.router import BaseRouter
from src.repositories.example_repository import ExampleRepository
from src.routers.auth import AuthRouter
from src.routers.default import DefaultRouter
from src.routers.llm_router import LLMRouter
from src.routers.calendar_router import CalendarRouter
from src.services.example import ExampleService
from src.models.config import AppConfig
from src.common.database.postgres import Postgres
from src.repositories.user_repository import UserRepository
from src.repositories.calendar_repository import CalendarRepository
from src.repositories.todo_calendar_repository import TodoCalendarRepository
from src.services.auth_service import AuthService
from src.services.llm_service import LLMService
from src.services.calendar_service import CalendarService


class ConfigProvider(Provider):
    @provide(scope=Scope.APP)
    def get_config(self) -> AppConfig:
        return AppConfig.create()


class ClientProvider(Provider):
    @provide(scope=Scope.APP)
    def get_base_client(self) -> BaseClient:
        return BaseClient(base_url="https://google.com")

    @provide(scope=Scope.APP)
    def get_llm_client(self, config: AppConfig) -> LLMClient:
        return LLMClient._create_client(config=config.llm_config)


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    def get_db(self, app_config: AppConfig) -> Postgres:
        return Postgres(dsn=app_config.db_config.DB_URL)


class RepositoryProvider(Provider):
    @provide(scope=Scope.APP)
    def get_example_repository(self, conn: Postgres) -> ExampleRepository:
        return ExampleRepository(conn=conn)

    @provide(scope=Scope.APP)
    def get_user_repository(self, conn: Postgres) -> UserRepository:
        return UserRepository(conn=conn)

    @provide(scope=Scope.APP)
    def get_calendar_repository(self, conn: Postgres) -> CalendarRepository:
        return CalendarRepository(conn=conn)

    @provide(scope=Scope.APP)
    def get_todo_calendar_repository(self, conn: Postgres) -> TodoCalendarRepository:
        return TodoCalendarRepository(conn=conn)


class ServiceProvider(Provider):
    @provide(scope=Scope.APP)
    def get_example_service(
        self, client: BaseClient, repo: ExampleRepository
    ) -> ExampleService:
        return ExampleService(base_client=client, example_repo=repo)

    @provide(scope=Scope.APP)
    def get_auth_service(self, repo: UserRepository, config: AppConfig) -> AuthService:
        return AuthService(user_repo=repo, config=config.jwt_config)

    @provide(scope=Scope.APP)
    def get_llm_service(self, llm_client: LLMClient) -> LLMService:
        return LLMService(client=llm_client)

    @provide(scope=Scope.APP)
    def get_calendar_service(
        self,
        calendar_repo: CalendarRepository,
        todo_calendar_repo: TodoCalendarRepository,
    ) -> CalendarService:
        return CalendarService(
            calendar_repo=calendar_repo, todo_calendar_repo=todo_calendar_repo
        )


class RouterProvider(Provider):
    @provide(scope=Scope.APP)
    def get_default_router(self, service: ExampleService) -> DefaultRouter:
        return DefaultRouter(
            example_service=service, base_prefix="/api/v1", tags=["default"]
        )

    @provide(scope=Scope.APP)
    def get_auth_router(self, service: AuthService) -> AuthRouter:
        return AuthRouter(auth_service=service, base_prefix="/api/v1", tags=["auth"])

    @provide(scope=Scope.APP)
    def get_llm_router(self, llm_service: LLMService) -> LLMRouter:
        return LLMRouter(llm_service=llm_service, base_prefix="/api/v1", tags=["llm"])

    @provide(scope=Scope.APP)
    def get_calendar_router(self, calendar_service: CalendarService) -> CalendarRouter:
        return CalendarRouter(
            calendar_service=calendar_service, base_prefix="/api/v1", tags=["calendar"]
        )

    @provide(scope=Scope.APP)
    def get_all_routers(
        self,
        default_router: DefaultRouter,
        auth_router: AuthRouter,
        llm_router: LLMRouter,
        calendar_router: CalendarRouter,
    ) -> list[BaseRouter]:
        return [default_router, auth_router, llm_router, calendar_router]


def create_container() -> Container:
    return make_container(
        ClientProvider(),
        ConfigProvider(),
        DatabaseProvider(),
        RepositoryProvider(),
        ServiceProvider(),
        RouterProvider(),
    )


def setup_app_container(app: FastAPI, container: Container) -> None:
    setup_dishka(container, app)
