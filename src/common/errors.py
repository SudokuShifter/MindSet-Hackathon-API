from http import HTTPStatus

from fastapi.exceptions import HTTPException
from asyncpg.exceptions import (
    NotNullViolationError,
    ForeignKeyViolationError,
    UniqueViolationError,
    InvalidColumnReferenceError,
)


class NotFoundError(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=HTTPStatus.NOT_FOUND, detail=detail)


class BadRequestError(HTTPException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=HTTPStatus.BAD_REQUEST, detail=detail)


class UnauthorizedError(HTTPException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=HTTPStatus.UNAUTHORIZED, detail=detail)


class InternalServerError(HTTPException):
    def __init__(self, detail: str = "Internal Server Error"):
        super().__init__(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=detail)


class ConflictError(HTTPException):
    def __init__(self, detail: str = "Conflict"):
        super().__init__(status_code=HTTPStatus.CONFLICT, detail=detail)


def asyncpg_errors_decorator(func):
    async def inner(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except NotNullViolationError as e:
            raise ConflictError(detail=f"Not null relations: {e}")
        except ForeignKeyViolationError as e:
            raise NotFoundError(detail=f"Object not found: {e}")
        except UniqueViolationError as e:
            raise BadRequestError(detail=f"Object with relation already exist: {e}")
        # except InvalidColumnReferenceError as e:
        #     raise BadRequestError(
        #         detail=f"Object with relation already exist: {e}"
        #     )

    return inner
