from typing import Any
from src.mtuci_private_api.errors import ParseError
from src.mtuci_private_api.models.mtuci import Attendance
from src.mtuci_private_api.attendance.parsers import (
    AttendanceListParser,
    SkipsParser,
    SubjectParamsParser
)
from src.mtuci_private_api.parsers import Parser
import pytest

class TestAttendanceParsers:

    @pytest.fixture
    def attendance_list_parser(
            self
    ) -> Parser[dict[str, Any], list[Attendance]]:

        return AttendanceListParser()

    @pytest.fixture
    def skips_parser(
            self
    ) -> Parser[dict[str, Any], int]:

        return SkipsParser()

    @pytest.fixture
    def params_parser(
            self
    ) -> Parser[dict[str, Any], dict[str, Any]]:

        return SubjectParamsParser()

    def test_attendance_list_parser(
        self,
        attendance_list: dict[str, Any],
        attendance_list_parser: Parser[dict[str, Any], list[Attendance]]
    ):
        attendance = attendance_list_parser.parse(attendance_list)

        # print(attendance)

        assert attendance, \
        "Ожидалось, что будет получен не пустой ответ. " + \
            f"Получили {attendance}"

        assert isinstance(attendance, list), \
        f"Ожидалось, что вернётся список. Получили {type(attendance)}"

        assert all(
            isinstance(a, Attendance)
            for a in attendance
        ), "Ожидалось, что в списке будут элементы типа Attendance"

        assert len(attendance) == 12, \
        "Ожидалось, что будет получено 12 элементов. " + \
            f"Получили {len(attendance)}"

    def test_attendance_list_parser_fail(
        self,
        attendance_list: dict[str, Any],
        attendance_list_parser: Parser[dict[str, Any], list[Attendance]]
    ):
        attendance_list["state"] = "bad"

        with pytest.raises(ParseError):
            attendance_list_parser.parse(attendance_list)

        attendance_list["state"] = "ok"
        del attendance_list["data"]["Ответ"]

        with pytest.raises(ParseError):
            attendance_list_parser.parse(attendance_list)

    def test_params_parser(
        self,
        attendance_list: dict[str, Any],
        params_parser: Parser[dict[str, Any], dict[str, Any]]
    ):
        params = params_parser.parse(attendance_list)

        print(params)

        assert params, f"Ожидался не пустой ответ. Получили {params}"

        assert isinstance(params, dict), \
        f"Ожидалось, что вернётся словарь. Получили {type(params)}"

        msg = "Ожидалось, что будет получено поле {}"
        assert params.get("Дисциплина"), msg.format("Дисциплина")
        assert params.get("Контингент"), msg.format("Контингент")
        assert params.get("Семестр"), msg.format("Семестр")
        assert params.get("УчебныйГод"), msg.format("УчебныйГод")

    def test_params_parser_fail(
        self,
        attendance_list: dict[str, Any],
        params_parser: Parser[dict[str, Any], dict[str, Any]]
    ):
        del attendance_list["data"]["Ответ"]

        with pytest.raises(ParseError):
            params_parser.parse(attendance_list)

    def test_skips_parser(
        self,
        skips_list: dict[str, Any],
        skips_parser: Parser[dict[str, Any], int]
    ):
        skips = skips_parser.parse(skips_list)

        assert skips, \
        f"Ожидался не пустой ответ. Получили {skips}"
        assert skips == 20, \
        f"Ожидалось 20 пропусков. Получили {skips}"

    def test_skips_parser_fail(
        self,
        skips_list: dict[str, Any],
        skips_parser: Parser[dict[str, Any], int]
    ):
        del skips_list["data"]["Ответ"]

        with pytest.raises(ParseError):
            skips_parser.parse(skips_list)
