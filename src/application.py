from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from loguru import logger

from src.interfaces.router import BaseRouter
from src.models.config import AppConfig
from src.routers.default import DefaultRouter
from src.common.database.postgres import Postgres


class Application:
    def __init__(
        self,
        config: AppConfig,
        routers: list[BaseRouter]
    ):
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
        for router in self.routers:
            server.include_router(
                router.api_router,
                prefix=router.base_prefix,
                tags=router.tags,
            )

    def start_app(self) -> FastAPI:
        @asynccontextmanager
        async def lifespan(server: FastAPI) -> AsyncGenerator[None, None]:
            try:
                # await db.init_db()
                yield
            finally:
                logger.warning("Ending ")
                # await db.close()

        server = FastAPI(lifespan=lifespan)
        self.setup(server=server)
        return server
