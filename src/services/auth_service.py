from datetime import datetime, UTC, timedelta
from uuid import uuid4
import jwt

import bcrypt

from src.repositories.user_repository import UserRepository
from src.models.auth_pyd import UserInput, UserLogin
from src.models.config import AppConfig


class UserService:
    def __init__(self, user_repo: UserRepository, app_config: AppConfig):
        self.user_repo = user_repo
        self.app_config = app_config

    async def registration(self, user_data: UserInput):
        _id = uuid4()
        creation_date = datetime.now()
        password = bcrypt.hashpw(user_data.password, bcrypt.gensalt())

        return await self.user_repo.create_user(
            _id=_id,
            first_name=user_data.first_name,
            second_name=user_data.second_name,
            email=user_data.email,
            password=password,
            description=user_data.description,
            creation_date=creation_date,
        )

    async def login(self, user_data: UserLogin):
        password = await self.user_repo.get_password_by_email(user_data.email)
        flag = bcrypt.checkpw(
            bcrypt.hashpw(user_data.password, bcrypt.gensalt()), password
        )

        if flag:
            pass

    def _generate_access_token(self, user_id: int, created_at: datetime | None) -> str:
        created_at = created_at or datetime.now(tz=UTC)
        return jwt.encode(
            payload={
                "sub": str(user_id),
                "iat": created_at,
                "exp": created_at + timedelta(hours=5),
                "type": "session",
            },
            key=self.app_config.jwt_config.JWT_PRIVATE_KEY,
            algorithm="EdDSA",
        )
