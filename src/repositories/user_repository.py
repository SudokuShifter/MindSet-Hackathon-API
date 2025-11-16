from datetime import datetime
from uuid import UUID
from src.common.database.postgres import Postgres


class UserRepository:
    def __init__(self, conn: Postgres):
        self._conn = conn

    async def create_user(
        self,
        _id: UUID,
        first_name: str,
        second_name: str,
        email: str,
        password: str,
        description: str,
        creation_date: datetime,
        personality_type: str | None = None,
    ):
        query = """
            INSERT INTO "User" (id, first_name, second_name, email, password, description, personality_type, creation_date)
            values ($1, $2, $3, $4, $5, $6, $7, $8) RETURNING *
        """
        return await self._conn.pool.execute(
            query,
            _id,
            first_name,
            second_name,
            email,
            password,
            description,
            personality_type,
            creation_date,
        )

    async def get_password_by_email(self, email: str):
        query = """
            SELECT u.password FROM "User" as u
            WHERE u.email = $1
        """
        return await self._conn.pool.fetchrow(query, email)
