"""Парсер таблицы занятий"""

from datetime import datetime
from typing import Any

from ...models import Lesson, LessonType
from ...parsers import Parser
from ...models import Schedule
from ...errors import ParseError

class TimetableParser(
    Parser[dict[str, Any], Schedule]
):
    """Парсер таблицы занятий"""

    def validate(
        self,
        obj: dict[str, Any],
        **kwargs: Any
    ) -> bool:
        """Проверяет статус ответа и содержание days

        Args:
            obj: таблица занятий.
            **kwargs: дополнительные параметры.
                Не используются.

        Returns:
            Валидна ли таблица.
        """
        if not obj.get("status", "") == "success":
            return False

        if not obj.get("data", {}).get("days"):
            return False

        return True

    def parse(
        self,
        obj: dict[str, Any],
        **kwargs: Any
    ) -> Schedule:
        """Парсит таблицу занятий

        Args:
            obj: словарь с таблицей занятий.
            **kwargs: дополнительные параметры.
                Должны содержать date.

        Returns:
            Расписание на день.

        Raises:
            ParseError: если не пройдена валидация.
        """
        try:

            date: datetime = kwargs.pop("date")
            today = date.strftime("%d.%m.%Y")

            if not self.validate(obj):
                raise ParseError(f"Invalid object: {obj}")

            data = obj.get("data", {})
            days = data.get("days", {})

            todays_schedule: list[dict[str, Any]] = days.get(today, [])

            lessons: list[Lesson] = []
            for lesson in todays_schedule:
                name:       str       = lesson.get("UF_DISCIPLINE", "")
                type_:      str       = lesson.get("UF_TYPE", "")
                start_time: str       = lesson.get("UF_TIME_START", "00:00")
                end_time:   str       = lesson.get("UF_TIME_END", "00:00")
                is_retake:  bool      = bool(
                    int(
                        lesson.get("UF_IS_RETAKE", "0")
                    )
                )
                audience:   list[str] = lesson.get("UF_AUDIENCE", [])
                teachers:   list[str] = lesson.get("UF_TEACHER", [])

                lesson = Lesson(
                    name=name,
                    type_=self._get_type(type_),
                    is_retake=is_retake,
                    teachers=teachers,
                    audience=audience,
                    start_time=self._to_datetime(start_time, date),
                    end_time=self._to_datetime(end_time, date)
                )

                lessons.append(lesson)

            return Schedule(
                date=date,
                lessons=lessons
            )


        except KeyError as err:
            raise ValueError("date argument not provided") from err

    def _to_datetime(
        self,
        time_str: str,
        date: datetime
    ) -> datetime:
        """Преобразует время занятия в datetime

        Args:
            time_str: строка формате "%H:%M"
                с временем занятия.
            date: дата, по которой был поиск.

        Returns:
            Время занятия в формате datetime.

        Raises:
            ValueError: если не совпадает формат.
        """
        format_ = "%H:%M"
        result = datetime.strptime(time_str, format_)
        result = result.replace(
            year=date.year,
            month=date.month,
            day=date.day
        )

        return result

    def _get_type(self, type_str: str) -> LessonType:
        """Определяет тип занятия

        Args:
            type_str: строка с типом занятия.

        Returns:
            Одно из перечислений типа занятий.

        Raises:
            ParseError: не был определён тип занятия.
        """
        match type_str:
            case "Лекции":
                return LessonType.LECTURE
            case "Практические занятия":
                return LessonType.PRACTICE
            case "Зачет":
                return LessonType.CREDIT
            case "Лабораторные работы":
                return LessonType.LAB
            case "Экзамен":
                return LessonType.EXAM
            case "Дифференцированный зачет":
                return LessonType.DIFF_CREDIT

        raise ParseError(f"Unknown type of lesson: {type_str}")
