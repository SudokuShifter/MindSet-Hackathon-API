from uuid import UUID
from datetime import datetime
from typing import List, Optional

from src.common.database.postgres import Postgres


class TodoCalendarRepository:
    def __init__(self, conn: Postgres):
        self._conn = conn

    async def create_todo_calendar(self, _id: UUID, date: datetime, user_id: UUID):
        query = """
            INSERT INTO "ToDoCalendar" (id, date, user_id)
            VALUES ($1, $2, $3)
            RETURNING *
        """
        return await self._conn.pool.fetchrow(query, _id, date, user_id)

    async def get_todo_calendar(self, calendar_id: UUID):
        query = 'SELECT * FROM "ToDoCalendar" WHERE id = $1'
        return await self._conn.pool.fetchrow(query, calendar_id)

    async def get_user_todo_calendars(
        self, user_id: UUID, date: Optional[datetime] = None
    ):
        query = 'SELECT * FROM "ToDoCalendar" WHERE user_id = $1'
        params = [user_id]

        if date:
            query += " AND date = $2"
            params.append(date)

        query += " ORDER BY date DESC"
        return await self._conn.pool.fetch(query, *params)

    async def update_todo_calendar(
        self, calendar_id: UUID, date: Optional[datetime] = None
    ):
        if date is None:
            return await self.get_todo_calendar(calendar_id)

        query = """
            UPDATE "ToDoCalendar" 
            SET date = $2 
            WHERE id = $1 
            RETURNING *
        """
        return await self._conn.pool.fetchrow(query, calendar_id, date)

    async def delete_todo_calendar(self, calendar_id: UUID):
        query = 'DELETE FROM "ToDoCalendar" WHERE id = $1 RETURNING *'
        return await self._conn.pool.fetchrow(query, calendar_id)

    async def create_todo_mood(
        self,
        _id: UUID,
        advice: Optional[str],
        checkbox: bool,
        time_start: Optional[str],
        time_end: Optional[str],
        todo_calendar_id: UUID,
        mood_type_id: UUID,
    ):
        query = """
            INSERT INTO "ToDoMood" 
            (id, advice, checkbox, time_start, time_end, todo_calendar_id, mood_type_id)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *
        """
        return await self._conn.pool.fetchrow(
            query,
            _id,
            advice,
            checkbox,
            time_start,
            time_end,
            todo_calendar_id,
            mood_type_id,
        )

    async def get_todo_mood(self, todo_mood_id: UUID):
        query = 'SELECT * FROM "ToDoMood" WHERE id = $1'
        return await self._conn.pool.fetchrow(query, todo_mood_id)

    async def get_todo_moods_by_calendar(self, todo_calendar_id: UUID):
        query = """
            SELECT * FROM "ToDoMood" 
            WHERE todo_calendar_id = $1 
            ORDER BY time_start
        """
        return await self._conn.pool.fetch(query, todo_calendar_id)

    async def toggle_todo_mood_checkbox(self, todo_mood_id: UUID):
        query = """
            UPDATE "ToDoMood" 
            SET checkbox = NOT checkbox 
            WHERE id = $1 
            RETURNING *
        """
        return await self._conn.pool.fetchrow(query, todo_mood_id)

    async def delete_todo_mood(self, todo_mood_id: UUID):
        query = 'DELETE FROM "ToDoMood" WHERE id = $1 RETURNING *'
        return await self._conn.pool.fetchrow(query, todo_mood_id)
