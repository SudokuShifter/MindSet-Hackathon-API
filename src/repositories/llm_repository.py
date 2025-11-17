from datetime import datetime
from uuid import UUID

from fastapi import Query
from src.common.database.postgres import Postgres


class LLMRepository:
    def __init__(self, conn: Postgres):
        self._conn = conn

    async def get_data_for_weekly_report(
        self,
        session_token: str,
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
        user_id = await self._conn.pool.execute(
            query,
            session_token,
        )
        query = """
        """

        return await self._conn.pool.execute(
            query,
            user_id,
        )
