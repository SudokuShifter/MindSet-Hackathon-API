from typing import Annotated
from fastapi import APIRouter, Depends, Query, Body, HTTPException
from datetime import date, datetime
from uuid import UUID

from src.common.errors import BadRequestError
from src.models.auth_pyd import JWTRequestPayload
from src.interfaces.router import BaseRouter
from src.services.calendar_service import CalendarService
from src.common.security import verify_token


class CalendarRouter(BaseRouter):
    def __init__(
        self,
        calendar_service: CalendarService,
        base_prefix: str = "",
        tags: list[str] | None = None,
    ):
        self.calendar_service = calendar_service
        self._base_prefix = base_prefix
        self._tags = tags or ["calendar"]

    @property
    def tags(self) -> list[str]:
        return self._tags

    @property
    def base_prefix(self) -> str:
        return self._base_prefix

    @property
    def api_router(self) -> APIRouter:
        router = APIRouter()
        self._register(router)
        return router

    def _register(self, router: APIRouter) -> None:
        # Calendar endpoints
        @router.post("/entries")
        async def create_calendar_entry(
            credentials: Annotated[JWTRequestPayload, Depends(verify_token)],
            date: Annotated[date, Body()],
        ):
            """
            Создать запись в календаре
            """
            try:
                if date != datetime.now().date():
                    raise BadRequestError(detail="date is not current")

                return await self.calendar_service.create_calendar(
                    date=date, user_id=credentials.sub
                )
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

        @router.get("/entries")
        async def get_calendar_entries(
            credentials: Annotated[JWTRequestPayload, Depends(verify_token)],
            start_date: Annotated[date, Query()],
            end_date: Annotated[date, Query()],
        ):
            """
            Получить записи календаря пользователя за период
            """
            try:
                entries = await self.calendar_service.get_user_calendar_entries(
                    user_id=credentials.sub, start_date=start_date, end_date=end_date
                )
                return {"entries": entries}
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

        # Mood endpoints
        @router.post("/moods")
        async def create_mood(
            credentials: Annotated[JWTRequestPayload, Depends(verify_token)],
            mood_type_id: Annotated[UUID, Body()],
            activity_type_id: Annotated[UUID, Body()],
            time_start: Annotated[str, Body()],
            time_end: Annotated[str, Body()],
            calendar_id: Annotated[UUID, Body()],
        ):
            """
            Создать запись настроения
            """
            try:
                return await self.calendar_service.create_mood(
                    mood_type_id=mood_type_id,
                    activity_type_id=activity_type_id,
                    time_start=time_start,
                    time_end=time_end,
                    calendar_id=calendar_id,
                    user_id=credentials.sub,
                )
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

        @router.post("/moods/date")
        async def create_mood_for_date(
            credentials: Annotated[JWTRequestPayload, Depends(verify_token)],
            mood_type_id: Annotated[UUID, Body()],
            activity_type_id: Annotated[UUID, Body()],
            time_start: Annotated[str, Body()],
            time_end: Annotated[str, Body()],
            target_date: Annotated[date, Body()],
        ):
            """
            Создать запись настроения для конкретной даты
            """
            try:
                return await self.calendar_service.create_mood_for_date(
                    mood_type_id=mood_type_id,
                    activity_type_id=activity_type_id,
                    time_start=time_start,
                    time_end=time_end,
                    target_date=target_date,
                    user_id=credentials.sub,
                )
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

        @router.get("/moods/period")
        async def get_moods_by_period(
            credentials: Annotated[JWTRequestPayload, Depends(verify_token)],
            start_date: Annotated[date, Query()],
            end_date: Annotated[date, Query()],
        ):
            """
            Получить все настроения за период
            """
            moods = await self.calendar_service.get_moods_by_period(
                user_id=credentials.sub, start_date=start_date, end_date=end_date
            )
            return {"moods": moods}

        @router.get("/moods/statistics")
        async def get_mood_statistics(
            credentials: Annotated[JWTRequestPayload, Depends(verify_token)],
            start_date: Annotated[date, Query()],
            end_date: Annotated[date, Query()],
        ):
            """
            Получить статистику по настроениям за период
            """
            stats = await self.calendar_service.get_mood_statistics(
                user_id=credentials.sub, start_date=start_date, end_date=end_date
            )
            return {"statistics": stats}

        @router.get("/moods/{mood_id}")
        async def get_mood(
            credentials: Annotated[JWTRequestPayload, Depends(verify_token)],
            mood_id: UUID,
        ):
            """
            Получить запись настроения по ID
            """
            try:
                mood = await self.calendar_service.get_mood(mood_id, credentials.sub)
                if not mood:
                    raise HTTPException(status_code=404, detail="Mood not found")
                return {"mood": mood}
            except ValueError as e:
                raise HTTPException(status_code=403, detail=str(e))

        @router.get("/moods/calendar/{calendar_id}")
        async def get_moods_by_calendar(
            credentials: Annotated[JWTRequestPayload, Depends(verify_token)],
            calendar_id: UUID,
        ):
            """
            Получить все настроения для календарной записи
            """
            try:
                moods = await self.calendar_service.get_moods_by_calendar(calendar_id)
                return {"moods": moods}
            except ValueError as e:
                raise HTTPException(status_code=403, detail=str(e))

        @router.get("/moods/date/{target_date}")
        async def get_moods_by_date(
            credentials: Annotated[JWTRequestPayload, Depends(verify_token)],
            target_date: date,
        ):
            """
            Получить все настроения для конкретной даты
            """
            moods = await self.calendar_service.get_moods_by_date(
                target_date, credentials.sub
            )
            return {"moods": moods}

        @router.delete("/moods/{mood_id}")
        async def delete_mood(
            credentials: Annotated[JWTRequestPayload, Depends(verify_token)],
            mood_id: UUID,
        ):
            """
            Удалить запись настроения
            """
            try:
                success = await self.calendar_service.delete_mood(
                    mood_id, credentials.sub
                )
                if not success:
                    raise HTTPException(status_code=404, detail="Mood not found")
                return {"message": "Mood deleted successfully"}
            except ValueError as e:
                raise HTTPException(status_code=403, detail=str(e))

        @router.get("/mood/types")
        async def get_all_mood_types():
            return await self.calendar_service.get_all_mood_types()

        @router.get("/activity/types")
        async def get_all_mood_types():
            return await self.calendar_service.get_all_activity_types()
