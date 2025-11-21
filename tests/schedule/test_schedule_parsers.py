from datetime import datetime
from typing import Any
import pytest
from src.mtuci_private_api.schedule.parsers import TimetableParser
from src.mtuci_private_api.models import Schedule, LessonType
from src.mtuci_private_api.parsers import Parser
from src.mtuci_private_api.errors import ParseError

class TestScheduleParsers:

    @pytest.fixture
    def timetable_parser(self) -> Parser[dict[str, Any], Schedule]:
        return TimetableParser()

    @pytest.fixture
    def date(self) -> datetime:
        return datetime(2025, 11, 21)

    @pytest.fixture
    def lesson_types(self) -> dict[str, LessonType]:
        return {
            "Лекции": LessonType.LECTURE,
            "Практические занятия": LessonType.PRACTICE,
            "Лабораторные работы": LessonType.LAB,
            "Зачет": LessonType.CREDIT,
            "Дифференцированный зачет": LessonType.DIFF_CREDIT,
            "Экзамен": LessonType.EXAM,
        }

    def test_timetable_parser(
        self,
        timetable_parser: Parser[dict[str, Any], Schedule],
        timetable: dict[str, Any],
        date: datetime
    ):
        schedule = timetable_parser.parse(
            timetable,
            date=date
        )

        assert schedule, f"Ожидался не пустой объект. Получили {schedule}"

        assert schedule.date == datetime(2025, 11, 21), \
        "Ожидалось, что дата будет 2025.11.21" + \
            f"Получили {schedule.date}"

        assert schedule.lessons, \
        "Ожидалось, что будут получены занятия"

    def test_timetable_parser_fail(
        self,
        timetable_parser: Parser[dict[str, Any], Schedule],
        timetable: dict[str, Any],
        date: datetime
    ):
        timetable["status"] = "bad"

        with pytest.raises(ParseError):
            timetable_parser.parse(timetable, date=date)

        timetable["status"] = "success"
        del timetable["data"]["days"]

        with pytest.raises(ParseError):
            timetable_parser.parse(timetable, date=date)

        with pytest.raises(ValueError):
            timetable_parser.parse(timetable)

    def test_timetable_parser_to_datetime(
        self,
        timetable_parser: TimetableParser,
        date: datetime
    ):
        time = "12:45"

        result = timetable_parser._to_datetime(
            time, date
        )

        assert result, f"Ожидался не пустой объект. Получили {result}"

        assert isinstance(result, datetime), \
        f"Ожидался объект datetime. Получили {type(result)}"

    
    def test_timetable_parser_to_datetime_fail(
        self,
        timetable_parser: TimetableParser,
        date: datetime
    ):
        time = "27:70"

        with pytest.raises(ValueError):
            timetable_parser._to_datetime(
                time, date
            )

    def test_timetable_get_type(
        self,
        timetable_parser: TimetableParser,
        lesson_types: dict[str, LessonType]
    ):
        for type_str, lesson_type in lesson_types.items():
            result = timetable_parser._get_type(type_str)

            assert result == lesson_type

    def test_timetable_get_type_fail(
        self,
        timetable_parser: TimetableParser,
    ):

        with pytest.raises(ParseError):
            timetable_parser._get_type("UNKWNON")
