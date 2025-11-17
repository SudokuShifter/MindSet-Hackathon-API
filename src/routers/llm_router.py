from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, status, Query, Depends

from src.services.auth_service import AuthService
from src.interfaces.router import BaseRouter
from src.services.llm_service import LLMService
from src.models.auth_pyd import JWTRequestPayload
from src.interfaces.router import BaseRouter
from src.services.auth_service import AuthService
from src.common.security import verify_token


class LLMRouter(BaseRouter):
    def __init__(
        self,
        llm_service: LLMService,
        auth_service: AuthService,
        base_prefix: str = "",
        tags: list[str] | None = None,
    ):
        self.llm_service = llm_service
        self.auth_service = auth_service
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
        async def onboarding_test(
            credentials: Annotated[JWTRequestPayload, Depends(verify_token)],
            test_result: list[bool] = Query(..., description=""),
        ):
            response = self.llm_service.score_epi(test_result)
            await self.auth_service.create_onboarding_test(
                result=str(response["interpretation"]), user_id=UUID(credentials.sub)
            )

        @router.post("/generate_repport")
        def generate_weekly_report():
            from src.repositories.llm_repository import LLMRepository

            calendar_dump = LLMRepository.get_data_for_weekly_report()
            from src.routers.llm_all import generate_report_llm  # to do

            pass

        @router.get("/cookie")
        def get_cookie():
            return self.llm_service.generate_cookie()
