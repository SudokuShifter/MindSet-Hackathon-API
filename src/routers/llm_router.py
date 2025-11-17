from fastapi import (
    APIRouter,
    status,
    Query,
)

from src.interfaces.router import BaseRouter
from src.services.llm_service import LLMService


class LLMRouter(BaseRouter):
    def __init__(
        self,
        llm_service: LLMService,
        base_prefix: str = "",
        tags: list[str] | None = None,
    ):
        self.llm_service = llm_service
        self._base_prefix = base_prefix
        self._tags = tags or []

    @property
    def tags(self) -> list[str]:
        return self._tags

    @property
    def base_prefix(self) -> str:
        return self._base_prefix

    @property
    def api_router(self) -> APIRouter:
        server = APIRouter()
        self._register(server)
        return server

    def _register(self, router: APIRouter) -> None:
        @router.post("/onboarding_test", status_code=status.HTTP_201_CREATED)
        def onboarding_test(test_result: list[bool] = Query(..., description="")):
            return self.llm_service.score_epi(test_result)

        @router.post("/generate_repport")
        def generate_weekly_report():
            from src.repositories.llm_repository import LLMRepository

            calendar_dump = LLMRepository.get_data_for_weekly_report()
            from src.routers.llm_all import generate_report_llm  # to do

            pass
