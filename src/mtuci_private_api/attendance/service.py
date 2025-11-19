"""Сервис посещаемости"""

from typing import Any
from httpx import AsyncClient

from .parsers.base import Parser

from ..errors import GetAttendanceError, ParseError

from ..models import Attendance
from ..config import app_config

class AttendanceService:
    """Сервис посещаемости

    Attributes:
        client: клиент для HTTP.
    """

    def __init__(
        self,
        client: AsyncClient,
        attendance_list_parser: Parser[
            dict[str, Any], list[Attendance]
        ],
        skips_parser: Parser[dict[str, Any], int],
        params_parser: Parser[dict[str, Any], dict[str, Any]]
    ):
        self.client = client
        self.attendance_list_parser = attendance_list_parser
        self.skips_parser = skips_parser
        self.params_parser = params_parser

    async def get_attendance(self) -> list[Attendance]:
        """Получает данные о посещаемости

        Returns:
            Список предметов с информацией о посещаемости.
        """
        body = {
            "processor": "getArray_ArrayDicsiplinesStudentAttendance",
            "referrer": "/student/attendance",
            "НомерСтраницы": 0
        }
        response = await self.client.post(
            url=f"{app_config.mtuci_url}/ilk/x/getProcessor",
            json=body
        )

        data = response.json()

        try:
            subjects = self.attendance_list_parser.parse(data)
            
            for subject in subjects:
                if subject.subject_name and subject.uid:
                    skips = await self.get_subject_skips(
                        subject.uid,
                        subject.subject_name,
                        data
                    )
                    subject.skips = skips

            return subjects
        except ParseError as err:
            raise GetAttendanceError("Failed to get attendance") from err

    async def get_subject_skips(
        self,
        subject_uid: str,
        subject_name: str,
        attendance_list: dict[str, Any]
    ) -> int:
        """Получает количество пропусков по предмету

        Args:
            subject_uid: идентификатор предмета.
            subject_name: название предмета.

        Returns:
            Количество пропусков.
        """
        body = {
            "processor": "getArray_ArrayDicsiplinesStudentAttendance",
            "referrer": "/student/attendance",
            "НомерСтраницы": 0
        }

        params = self.params_parser.parse(attendance_list)
        params["Дисциплина"] = {
            "type": "CatalogRef",
            "catalog": "Дисциплины",
            "uid": subject_uid,
            "name": subject_name
        }

        del body["НомерСтраницы"]
        body["processor"] = "getData_ArrayScoreStudenLessonAttendance"
        body = {
            **body,
            **params
        }

        response = await self.client.post(
            url=f"{app_config.mtuci_url}/ilk/x/getProcessor",
            json=body
        )

        data = response.json()
        skips = self.skips_parser.parse(data)

        return skips


    def _get_params(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        response = raw_data.get(
            "data", {}
        ).get("Ответ", [])

        if not response:
            raise GetAttendanceError("Invalid Response: Ответ wasn't found")

        params_structure = response[0].get(
            "СтруктураПараметров", {}
        )
        if not (command := params_structure.get("command", [])):
            raise GetAttendanceError("Invalid Response: command wasn't found")

        command_params = command[0].get("ПараметрыКоманды", {})

        return command_params
