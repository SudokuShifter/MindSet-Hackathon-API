from uuid import UUID
from datetime import datetime
from typing import List, Optional

from src.common.database.postgres import Postgres


class CalendarRepository:
    def __init__(self, conn: Postgres):
        self._conn = conn

    async def create_calendar_entry(
        self,
        _id: UUID,
        date: datetime,
        user_id: UUID,
        mood_type_id: UUID = None,
    ):
        query = """
            INSERT INTO "Calendar" (id, date, mood_type_id, user_id)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (date) DO NOTHING
            RETURNING *
        """
        return await self._conn.pool.fetchrow(query, _id, date, mood_type_id, user_id)

    async def get_calendar(self, _id: UUID):
        query = 'SELECT * FROM "Calendar" WHERE id = $1'
        return await self._conn.pool.fetchrow(query, _id)

    async def get_user_calendar_entries(
        self,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ):
        query = 'SELECT * FROM "Calendar" WHERE user_id = $1'
        params = [user_id]

        if start_date and end_date:
            query += " AND date BETWEEN $2 AND $3"
            params.extend([start_date, end_date])
        elif start_date:
            query += " AND date >= $2"
            params.append(start_date)
        elif end_date:
            query += " AND date <= $2"
            params.append(end_date)

        query += " ORDER BY date DESC"
        return await self._conn.pool.fetch(query, *params)

    async def create_mood(
        self,
        _id: UUID,
        mood_type_id: UUID,
        activity_type_id: UUID,
        time_start: Optional[str],
        time_end: Optional[str],
        calendar_id: UUID,
    ):
        query = """
            INSERT INTO "Mood" (id, mood_type_id, activity_type_id, time_start, time_end, calendar_id)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING *
        """
        return await self._conn.pool.fetchrow(
            query,
            _id,
            mood_type_id,
            activity_type_id,
            time_start,
            time_end,
            calendar_id,
        )

    async def get_mood(self, mood_id: UUID):
        query = 'SELECT * FROM "Mood" WHERE id = $1'
        return await self._conn.pool.fetchrow(query, mood_id)

    async def get_moods_by_calendar(self, calendar_id: UUID):
        query = 'SELECT * FROM "Mood" WHERE calendar_id = $1 ORDER BY time_start'
        return await self._conn.pool.fetch(query, calendar_id)

    async def delete_mood(self, mood_id: UUID):
        query = 'DELETE FROM "Mood" WHERE id = $1 RETURNING *'
        return await self._conn.pool.fetchrow(query, mood_id)

    async def get_all_moot_types(self):
        query = """
            SELECT * FROM "MoodType"
        """
        return await self._conn.pool.fetch(query)

    async def get_all_activity_types(self):
        query = """
            SELECT * FROM "ActivityType"
        """
        return await self._conn.pool.fetch(query)