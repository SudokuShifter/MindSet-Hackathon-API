from datetime import datetime, date, timedelta, time
from typing import Any
from uuid import UUID, uuid4

from src.repositories.calendar_repository import CalendarRepository
from src.repositories.todo_calendar_repository import TodoCalendarRepository


class CalendarService:
    def __init__(self, calendar_repo: CalendarRepository, todo_calendar_repo: TodoCalendarRepository):
        self.calendar_repo = calendar_repo
        self.todo_calendar_repo = todo_calendar_repo
    
    async def create_calendar(self, date: date, user_id: UUID):
        _id = uuid4()
        return await self.calendar_repo.create_calendar_entry(_id, date, user_id)

    async def get_calendar(self, _id: UUID):
        return await self.get_calendar(_id)
    
    async def get_user_calendar_entries(
        self,
        user_id: UUID,
        start_date: date | None = None,
        end_date: date | None = None,
        period: date | None = None
    ) -> list[dict[str, Any]]:
        """
        Получить записи календаря пользователя с различными вариантами фильтрации
        """
        # Если указан период, вычисляем даты автоматически
        if period and not (start_date or end_date):
            start_date, end_date = self._calculate_period_dates(period)
        
        # Если указаны datetime - преобразуем в date
        if isinstance(start_date, datetime):
            start_date = start_date.date()
        if isinstance(end_date, datetime):
            end_date = end_date.date()
        
        entries = await self.calendar_repo.get_user_calendar_entries(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return [dict(entry) for entry in entries] if entries else []
    
    def _calculate_period_dates(self, period: str) -> tuple[date, date]:
        """
        Вычислить даты начала и конца периода
        """
        today = date.today()
        
        if period == 'day':
            return today, today
        elif period == 'week':
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)
            return start, end
        elif period == 'month':
            start = date(today.year, today.month, 1)
            if today.month == 12:
                end = date(today.year, 12, 31)
            else:
                end = date(today.year, today.month + 1, 1) - timedelta(days=1)
            return start, end
        elif period == 'year':
            start = date(today.year, 1, 1)
            end = date(today.year, 12, 31)
            return start, end
        else:
            raise ValueError(f"Unknown period: {period}")

    async def create_mood(
        self,
        mood_type_id: UUID,
        activity_type_id: UUID,
        time_start: str,
        time_end: str,
        calendar_id: UUID,
        user_id: UUID
    ) -> dict[str, Any]:
        """
        Создать новую запись настроения
        """
        # Проверяем, что календарь существует и принадлежит пользователю
        calendar_entry = await self.calendar_repo.get_calendar(calendar_id)
        if not calendar_entry:
            raise ValueError("Calendar entry not found")

        if calendar_entry['user_id'] != UUID(user_id):
            raise ValueError("Calendar entry does not belong to user")
        
        # Валидация времени
        if time_start and time_end:
            self._validate_time_range(time_start, time_end)
        
        _id = uuid4()
        
        mood = await self.calendar_repo.create_mood(
            _id=_id,
            mood_type_id=mood_type_id,
            activity_type_id=activity_type_id,
            time_start=time_start,
            time_end=time_end,
            calendar_id=calendar_id
        )
        
        return dict(mood) if mood else None

    async def create_mood_for_date(
        self,
        mood_type_id: UUID,
        activity_type_id: UUID,
        time_start: str,
        time_end: str,
        target_date: date,
        user_id: UUID
    ) -> dict[str, Any]:
        """
        Создать запись настроения для конкретной даты
        (автоматически создает или находит календарную запись)
        """
        # Ищем календарную запись для даты
        calendar_entries = await self.calendar_repo.get_user_calendar_entries(
            user_id=user_id,
            start_date=target_date,
            end_date=target_date
        )
        
        if calendar_entries:
            calendar_id = calendar_entries[0]['id']
        else:
            # Создаем новую календарную запись
            calendar_id = uuid4()
            calendar_entry = await self.calendar_repo.create_calendar_entry(
                _id=calendar_id,
                date=target_date,
                user_id=user_id
            )
            calendar_id = calendar_entry['id']
        
        return await self.create_mood(
            mood_type_id=mood_type_id,
            activity_type_id=activity_type_id,
            time_start=time_start,
            time_end=time_end,
            calendar_id=calendar_id,
            user_id=user_id
        )

    async def get_mood(self, mood_id: UUID, user_id: UUID) -> dict[str, Any] | None:
        """
        Получить запись настроения по ID с проверкой прав доступа
        """
        mood = await self.calendar_repo.get_mood(mood_id)
        return dict(mood)

    async def get_moods_by_calendar(
        self,
        calendar_id: UUID,
    ) -> list[dict[str, Any]]:
        """
        Получить все настроения для календарной записи с проверкой прав
        """
        moods = await self.calendar_repo.get_moods_by_calendar(calendar_id)
        return [dict(mood) for mood in moods] if moods else []

    async def get_moods_by_date(
        self,
        target_date: date,
        user_id: UUID
    ) -> list[dict[str, Any]]:
        """
        Получить все настроения для конкретной даты
        """
        calendar_entries = await self.calendar_repo.get_user_calendar_entries(
            user_id=UUID(user_id),
            start_date=target_date,
            end_date=target_date
        )
        
        if not calendar_entries:
            return []
        
        calendar_id = calendar_entries[0]['id']
        return await self.get_moods_by_calendar(calendar_id)

    async def get_moods_by_period(
        self,
        user_id: UUID,
        start_date: date,
        end_date: date
    ) -> list[dict[str, Any]]:
        """
        Получить все настроения за период
        """
        # Получаем календарные записи за период
        calendar_entries = await self.calendar_repo.get_user_calendar_entries(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        if not calendar_entries:
            return []
        
        # Собираем все настроения для найденных календарных записей
        all_moods = []
        for calendar_entry in calendar_entries:
            moods = await self.calendar_repo.get_moods_by_calendar(calendar_entry['id'])
            for mood in moods:
                mood_dict = dict(mood)
                mood_dict['date'] = calendar_entry['date']  # Добавляем дату для удобства
                all_moods.append(mood_dict)
        
        # Сортируем по дате и времени
        all_moods.sort(key=lambda x: (
            x['date'],
            x['time_start'] or '00:00'
        ))
        
        return all_moods

    async def delete_mood(self, mood_id: UUID, user_id: UUID) -> bool:
        """
        Удалить запись настроения с проверкой прав
        """
        # Проверяем права доступа
        mood = await self.get_mood(mood_id, user_id)
        if not mood:
            return False
        
        deleted = await self.calendar_repo.delete_mood(mood_id)
        return deleted is not None

    async def get_mood_statistics(
        self,
        user_id: UUID,
        start_date: date,
        end_date: date 
    ) -> dict[str, Any]:
        """
        Получить статистику по настроениям
        """
        moods = await self.get_moods_by_period(user_id, start_date, end_date)
        
        if not moods:
            return {
                "total_moods": 0,
                "mood_type_distribution": {},
                "activity_type_distribution": {},
                "time_distribution": {},
                "period": {
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None
                }
            }
        
        # Статистика по типам настроений
        mood_type_stats = {}
        activity_type_stats = {}
        time_stats = {"morning": 0, "afternoon": 0, "evening": 0, "night": 0}
        
        for mood in moods:
            # Статистика по mood_type_id
            mood_type = str(mood['mood_type_id'])
            mood_type_stats[mood_type] = mood_type_stats.get(mood_type, 0) + 1
            
            # Статистика по activity_type_id
            activity_type = str(mood['activity_type_id'])
            activity_type_stats[activity_type] = activity_type_stats.get(activity_type, 0) + 1
            
            # Статистика по времени суток
            if mood['time_start']:
                time_category = self._categorize_time(mood['time_start'])
                time_stats[time_category] += 1
        
        return {
            "total_moods": len(moods),
            "mood_type_distribution": mood_type_stats,
            "activity_type_distribution": activity_type_stats,
            "time_distribution": time_stats,
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }

    def _validate_time_range(self, time_start: str, time_end: str) -> None:
        """
        Валидация временного диапазона
        """
        try:
            start = datetime.strptime(time_start, '%H:%M').time()
            end = datetime.strptime(time_end, '%H:%M').time()
            
            if start >= end:
                raise ValueError("Start time must be before end time")
                
        except ValueError as e:
            raise ValueError(f"Invalid time format: {e}")

    def _categorize_time(self, time_str: str) -> str:
        """
        Категоризация времени суток
        """
        try:
            time_obj = datetime.strptime(time_str, '%H:%M').time()
            
            if time_obj < time(12, 0):
                return "morning"
            elif time_obj < time(17, 0):
                return "afternoon"
            elif time_obj < time(22, 0):
                return "evening"
            else:
                return "night"
        except ValueError:
            return "unknown"
    
    async def get_all_mood_types(self):
        return await self.calendar_repo.get_all_moot_types()
    
    async def get_all_activity_types(self):
        return await self.calendar_repo.get_all_activity_types()