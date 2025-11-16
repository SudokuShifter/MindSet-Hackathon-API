from http import HTTPStatus

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse

from src.common.errors import UnauthorizedError
from src.services.auth_service import AuthService


class SessionMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, app: FastAPI, auth_service: AuthService, exclude_paths: list[str]
    ):
        super().__init__(app)
        self.auth_service = auth_service
        self.exclude_paths = exclude_paths

    async def dispatch(self, request: Request, call_next):
        for path in self.exclude_paths:
            if request.url.path.startswith(path):
                return await call_next(request)

        session_token = request.headers.get("SessionToken")
        flag = await self.auth_service.check_auth(session_token)

        if not flag:
            return JSONResponse(
                status_code=HTTPStatus.UNAUTHORIZED,
                content="Missing or invalid Authorization header",
            )
        return await call_next(request)
