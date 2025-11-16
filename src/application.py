from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from dishka import Container
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from loguru import logger

from src.services.auth_service import AuthService
from src.interfaces.router import BaseRouter
from src.common.database.postgres import Postgres
from src.middlewares.session import SessionMiddleware
from src.common.container import setup_app_container


class Application:
    def __init__(self, container: Container, routers: list[BaseRouter]):
        self.container = container
        self.routers = routers

    def setup(self, server: FastAPI) -> None:
        server.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        auth_service = self.container.get(AuthService)
        server.add_middleware(
            SessionMiddleware,
            auth_service=auth_service,
            exclude_paths=["/api/v1/register", "/api/v1/login", "/docs", "/openapi.json"],
        )
        for router in self.routers:
            server.include_router(
                router.api_router,
                prefix=router.base_prefix,
                tags=router.tags,
            )

    def start_app(
        self,
    ) -> FastAPI:
        @asynccontextmanager
        async def lifespan(server: FastAPI) -> AsyncGenerator[None, None]:
            db = self.container.get(Postgres)
            try:
                await db.connect()
                yield
            finally:
                logger.warning("Ending ")
                await db.disconnect()

        server = FastAPI(lifespan=lifespan)
        setup_app_container(server, container=self.container)

        self.setup(server=server)
        return server
