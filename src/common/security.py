import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from src.common.config import app_config
from src.common.errors import UnauthorizedError
from src.models.auth_pyd import JWTRequestPayload


jwt_schema = OAuth2PasswordBearer(tokenUrl="/api/v1/login")


def verify_token(token: str = Depends(jwt_schema)) -> JWTRequestPayload:
    try:
        decoded_token: dict = jwt.decode(
            jwt=token,
            key=app_config.jwt_config.JWT_PUBLIC_KEY,
            algorithms=["EdDSA"],
            options={
                "verify_signature": True,
            },
        )

    except jwt.exceptions.PyJWTError as e:
        raise UnauthorizedError(detail=str(e))

    return JWTRequestPayload(**decoded_token)
