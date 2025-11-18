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

        data = response.json()

        return await self._parse(data)

    async def get_subject_skips(
        self,
        subject_uid: str,
        subject_name: str
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

        response = await self.client.post(
            url=f"{app_config.mtuci_url}/ilk/x/getProcessor",
            json=body
        )
        data = response.json()

        params = self._get_params(data)
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

        data = response.json().get("data", {})

        response_ = data.get("Ответ", {})
        if not (table := response_.get("ТаблицаДанных", [])):
            raise Exception("Invalid Response")

        count = 0
        for subject in table:
            if not subject.get("Отметка", False):
                count += 1
        
        return count

    async def _parse(
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

            skips = None
            if name and uid:
                skips = await self.get_subject_skips(
                    subject_uid=uid,
                    subject_name=name
                )

            attendance = Attendance(
                uid=uid,
                subject_name=name,
                attendance_percentage=percent,
                skips=skips
            )

            result.append(attendance)

        return result

    def _get_params(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        response = raw_data.get(
            "data", {}
        ).get("Ответ", [])

        if not response:
            raise Exception("Invalid Response")

        params_structure = response[0].get(
            "СтруктураПараметров", {}
        )
        if not (command := params_structure.get("command", [])):
            raise Exception("Invalid Response")

        command_params = command[0].get("ПараметрыКоманды", {})

        return command_params
