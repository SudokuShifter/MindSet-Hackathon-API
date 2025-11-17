import jwt
from fastapi import Header, Security
from fastapi.security import APIKeyHeader

from src.common.config import app_config
from src.common.errors import UnauthorizedError
from src.models.auth_pyd import JWTRequestPayload


session_token_header = APIKeyHeader(
    name="SessionToken", description="JWT токен без префикса Bearer"
)


def verify_token(
    session_token: str = Security(session_token_header),
) -> JWTRequestPayload:
    try:
        decoded_token: dict = jwt.decode(
            jwt=session_token,
            key=app_config.jwt_config.JWT_PUBLIC_KEY,
            algorithms=["EdDSA"],
            options={
                "verify_signature": True,
            },
        )
        print(decoded_token)

    except jwt.exceptions.PyJWTError as e:
        raise UnauthorizedError(detail=str(e))

    return JWTRequestPayload(**decoded_token)
