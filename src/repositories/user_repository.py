from datetime import datetime
from uuid import UUID

from fastapi import Query
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
            INSERT INTO "User" (id, first_name, second_name, email, password, description, personality_type, created_at)
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
        query = """
            INSERT INTO "Session" (id, user_id, session_token, created_at, expire_in)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (user_id) 
            DO UPDATE SET 
                id = EXCLUDED.id,
                session_token = EXCLUDED.session_token,
                created_at = EXCLUDED.created_at,
                expire_in = EXCLUDED.expire_in
        """
        return await self._conn.pool.execute(
            query, _id, user_id, session_token, created_at, expire_in
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
