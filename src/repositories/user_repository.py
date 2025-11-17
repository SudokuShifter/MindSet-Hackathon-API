from datetime import datetime
from re import A
from uuid import UUID

from fastapi import Query
from src.common.database.postgres import Postgres


class UserRepository:
    def __init__(self, conn: Postgres):
        self._conn = conn

    async def get_user_data_by_id(self, _id: UUID):
        query = """
            SELECT u.id, u.first_name, u.second_name, u.email, u.test_id, u.created_at  FROM "User" as u
            WHERE id = $1
        """
        return await self._conn.pool.fetchrow(query, _id)

    async def update_user_test(self, user_id: UUID, onboarding_test_id: UUID):
        query = """
            UPDATE "User" 
            SET onboarding_test_id = $1
            WHERE id = $2
            RETURNING *
        """
        return await self._conn.pool.execute(query, onboarding_test_id, user_id)

    async def create_onboarding_test(
        self, _id: UUID, result: str, personality_type: str, user_id: UUID
    ):
        query = """
            INSERT INTO "OnboardingTestResult" (id, result, personality_type, user_id)
            values ($1, $2, $3, $4)
        """
        return await self._conn.pool.execute(
            query, _id, result, personality_type, user_id
        )

    async def create_user(
        self,
        _id: UUID,
        first_name: str,
        second_name: str,
        email: str,
        password: str,
        creation_date: datetime,
    ):
        query = """
            INSERT INTO "User" (id, first_name, second_name, email, password, created_at)
            values ($1, $2, $3, $4, $5, $6) RETURNING *
        """
        return await self._conn.pool.execute(
            query,
            _id,
            first_name,
            second_name,
            email,
            password,
            creation_date,
        )

    async def get_user_by_email(self, email: str):
        query = """
            SELECT * FROM "User" as u
            WHERE u.email = $1
        """
        return await self._conn.pool.fetchrow(query, email)

    async def create_session(
        self,
        _id: UUID,
        user_id: UUID,
        session_token: str,
        created_at: datetime,
        expire_in: datetime,
    ):
        async with self._conn.pool.acquire() as connection:
            async with connection.transaction():
                # Удаляем старую сессию
                await connection.execute(
                    'DELETE FROM "Session" WHERE user_id = $1', user_id
                )
                # Создаем новую сессию
                return await connection.fetchrow(
                    """
                    INSERT INTO "Session" (id, user_id, session_token, created_at, expire_in)
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING *
                    """,
                    _id,
                    user_id,
                    session_token,
                    created_at,
                    expire_in,
                )

    async def get_session(self, session_token: str):
        query = """
            SELECT s.session_token FROM "Session" as s
            WHERE s.session_token = $1
        """
        return await self._conn.pool.fetchrow(query, session_token)

    async def get_session_by_user_id(self, user_id: UUID):
        query = """
            SELECT s.session_token FROM "Session" as s
            WHERE s.user_id = $1
        """
        return await self._conn.pool.fetchrow(query, user_id)

    async def delete_token(self, session_token: str):
        query = """
            DELETE FROM "Session"
            WHERE session_token = $1
        """
        return await self._conn.pool.execute(query, session_token)
