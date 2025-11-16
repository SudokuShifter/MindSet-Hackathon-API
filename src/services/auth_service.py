from datetime import datetime, timedelta
from uuid import uuid4, UUID
import jwt

import bcrypt
from loguru import logger

from src.common.errors import BadRequestError
from src.models.forms.auth_forms import RegisterForm
from src.repositories.user_repository import UserRepository
from src.models.auth_pyd import UserLogin
from src.models.config import JWTConfig


class AuthService:
    def __init__(self, user_repo: UserRepository, config: JWTConfig):
        self.user_repo = user_repo
        self.config = config

    async def registration(self, user_data: RegisterForm):
        _id = uuid4()
        creation_date = datetime.now()
        password = bcrypt.hashpw(user_data.password.encode(), bcrypt.gensalt()).decode()

        await self.user_repo.create_user(
            _id=_id,
            first_name=user_data.first_name,
            second_name=user_data.second_name,
            email=user_data.email,
            password=password,
            description=user_data.description,
            creation_date=creation_date,
        )

        return await self._generate_session_token(user_id=_id, created_at=creation_date)

    async def login(self, user_data: UserLogin):
        user = await self.user_repo.get_user_by_email(user_data.email)
        if not user or not bcrypt.checkpw(
            user_data.password.encode(), user["password"].encode()
        ):
            raise BadRequestError(detail="Wrong username or password")
        return await self._generate_session_token(user_id=user["id"])

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
                )
                return token_str
            except Exception as e:
                logger.debug(f"Existing token is invalid, creating new one: {e}")
        
        created_at = created_at or datetime.now()
        expire_at = created_at + timedelta(hours=5)
        
        new_token = jwt.encode(
            payload={
                "sub": str(user_id),
                "iat": created_at,
                "exp": expire_at,
                "type": "session",
            },
            key=self.config.JWT_PRIVATE_KEY,
            algorithm="EdDSA",
        )
        
        session_id = uuid4()
        await self.user_repo.create_session(
            _id=session_id,
            user_id=user_id,
            session_token=new_token,
            created_at=created_at,
            expire_in=expire_at,
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
            )
        except Exception as e:
            logger.exception(f"Unauthorized {e}")
            return False

        return True
