from datetime import datetime, timedelta, timezone
from uuid import uuid4, UUID
import jwt

import bcrypt
from loguru import logger

from src.common.errors import BadRequestError, asyncpg_errors_decorator
from src.models.forms.auth_forms import RegisterForm
from src.repositories.user_repository import UserRepository
from src.models.auth_pyd import UserLogin
from src.models.config import JWTConfig


class AuthService:
    def __init__(self, user_repo: UserRepository, config: JWTConfig):
        self.user_repo = user_repo
        self.config = config

    @asyncpg_errors_decorator
    async def registration(self, user_data: RegisterForm):
        _id = uuid4()
        creation_date_utc = datetime.now(timezone.utc)
        creation_date_naive = creation_date_utc.replace(tzinfo=None)
        password = bcrypt.hashpw(user_data.password.encode(), bcrypt.gensalt()).decode()

        await self.user_repo.create_user(
            _id=_id,
            first_name=user_data.first_name,
            second_name=user_data.second_name,
            email=user_data.email,
            password=password,
            creation_date=creation_date_naive,
        )

        return await self.create_session(user_id=_id)

    @asyncpg_errors_decorator
    async def create_session(self, user_id):
        session_id = uuid4()
        created_at_utc = datetime.now(timezone.utc)
        expire_at_utc = created_at_utc + timedelta(hours=5)
        token = await self._generate_session_token(user_id, created_at_utc)

        created_at_naive = created_at_utc.replace(tzinfo=None)
        expire_at_naive = expire_at_utc.replace(tzinfo=None)

        await self.user_repo.create_session(
            _id=session_id,
            user_id=user_id,
            session_token=token,
            created_at=created_at_naive,
            expire_in=expire_at_naive,
        )

        return token

    async def login(self, user_data: UserLogin):
        user = await self.user_repo.get_user_by_email(user_data.email)
        if not user or not bcrypt.checkpw(
            user_data.password.encode(), user["password"].encode()
        ):
            raise BadRequestError(detail="Wrong username or password")
        return await self.create_session(user_id=user["id"])

    async def logout(self, session_token: str):
        return await self.user_repo.delete_token(session_token=session_token)

    async def _generate_session_token(
        self, user_id: UUID, created_at: datetime | None = None
    ) -> str:
        existed_session = await self.user_repo.get_session_by_user_id(user_id)

        if existed_session and existed_session.get("session_token"):
            token_str = existed_session["session_token"]
            try:
                jwt.decode(
                    token_str,
                    key=self.config.JWT_PUBLIC_KEY,
                    algorithms=["EdDSA"],
                    options={"verify_signature": True, "verify_exp": True},
                )
                return token_str
            except Exception as e:
                logger.debug(f"Existing token is invalid, creating new one: {e}")

        created_at_utc = created_at or datetime.now(timezone.utc)
        expire_at_utc = created_at_utc + timedelta(hours=5)

        new_token = jwt.encode(
            payload={
                "sub": str(user_id),
                "iat": created_at_utc,
                "exp": expire_at_utc,
                "type": "session",
            },
            key=self.config.JWT_PRIVATE_KEY,
            algorithm="EdDSA",
        )

        created_at_naive = created_at_utc.replace(tzinfo=None)
        expire_at_naive = expire_at_utc.replace(tzinfo=None)

        session_id = uuid4()
        await self.user_repo.create_session(
            _id=session_id,
            user_id=user_id,
            session_token=new_token,
            created_at=created_at_naive,
            expire_in=expire_at_naive,
        )

        return new_token

    async def check_auth(self, session_token: str):
        db_token = await self.user_repo.get_session(session_token=session_token)
        if not db_token:
            return False
        try:
            jwt.decode(
                session_token,
                key=self.config.JWT_PUBLIC_KEY,
                algorithms=["EdDSA"],
                options={"verify_signature": True, "verify_exp": True},
            )
        except Exception as e:
            logger.exception(f"Unauthorized {e}")
            return False

        return True

    async def decode_token(self, session_token: str):
        return jwt.decode(
            session_token,
            key=self.config.JWT_PUBLIC_KEY,
            algorithms=["EdDSA"],
            options={"verify_signature": True, "verify_exp": True},
        )
