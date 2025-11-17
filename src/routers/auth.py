from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request

from src.models.forms.auth_forms import LoginForm, RegisterForm
from src.models.auth_pyd import JWTRequestPayload
from src.interfaces.router import BaseRouter
from src.services.auth_service import AuthService
from src.common.security import verify_token


class AuthRouter(BaseRouter):
    def __init__(
        self,
        auth_service: AuthService,
        base_prefix: str = "",
        tags: list[str] | None = None,
    ):
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
        @router.post("/register")
        async def register(register_form: RegisterForm):
            return await self.auth_service.registration(register_form)

        @router.post("/login")
        async def login(login_form: LoginForm):
            return await self.auth_service.login(login_form)

        @router.post("/logout")
        async def logout(request: Request):
            return await self.auth_service.logout(request.headers.get("SessionToken"))

        @router.post("/me")
        async def me(
            credentials: Annotated[JWTRequestPayload, Depends(verify_token)],
        ):
            return await self.auth_service.get_info_about_user(
                _id=UUID(credentials.sub)
            )
