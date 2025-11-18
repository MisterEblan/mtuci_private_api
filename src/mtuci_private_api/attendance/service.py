"""Сервис посещаемости"""

from typing import Any
from httpx import AsyncClient

from ..models import Attendance
from ..config import app_config

class AttendanceService:
    """Сервис посещаемости

    Attributes:
        client: клиент для HTTP.
    """

    def __init__(
        self,
        client: AsyncClient
    ):
        self.client = client

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

        return self._parse(response.json())

    async def get_subject_skips(
        self,
        subject_uid: str,
        subject_name: str
    ) -> int:
        body = {
            "processor": "getData_ArrayScoreStudenLessonAttendance",
            "referrer": "student/attendance",
            "Дисциплина": {
                "catalog": "Дисциплины",
                "name": subject_name,
                "type": "CatalogRef",
                "uid": subject_uid
            }
        }

        response = await self.client.get(
            url=f"{app_config.mtuci_url}/api/timetable/get",
            params={
                "value": "БИК2404",
                "month": 10,
                "type": "group"
            }
        )

        return response
        
    def _parse(
        self,
        attendance_data: dict[str, Any]
    ) -> list[Attendance]:
        """Парсит JSON посещаемости

        Args:
            attendance_data: сырой словарь с данными о посещаемости.

        Returns:
            список предметов с посещаемостью.
        """
        data = attendance_data.get("data", {})

        if not (data := data.get("Ответ", [])):
            raise Exception("Invalid Response")

        data = data[0].get("Содержимое", {})

        table = data.get("ТаблицаДанных", [])

        result = []
        for subject in table:
            name = subject.get("ПредставлениеПары", "")
            percent = float(
                subject.get("ПроцентПосещений", "0,0")
                .replace(",", ".")
            )
            uid = None
            if command := subject.get("data", {}).get("command", []):
                uid = (
                    command[0].get("ПараметрыКоманды", {})
                    .get("Дисциплина", {})
                    .get("uid", None)
                )

            attendance = Attendance(
                uid=uid,
                subject_name=name,
                attendance_percentage=percent
            )

            result.append(attendance)

        return result
