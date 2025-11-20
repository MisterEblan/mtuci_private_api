"""Сервис посещаемости"""

from typing import Any
from httpx import AsyncClient

from ..http import BaseHttpClient, HttpClient, Method
from .request_factory import ProcessorRequestFactory

from .parsers import (
    AttendanceListParser,
    SubjectParamsParser,
    SkipsParser
)

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
    ):
        self.client: HttpClient = BaseHttpClient(
            session=client
        )

    async def get_attendance(self) -> list[Attendance]:
        """Получает данные о посещаемости

        Returns:
            Список предметов с информацией о посещаемости.
        """
        body = ProcessorRequestFactory().create(
            processor="getArray_ArrayDicsiplinesStudentAttendance"
        )
        response = await self.client.request(
            method=Method.POST,
            url=f"{app_config.mtuci_url}/ilk/x/getProcessor",
            body=body
        )

        data = response.json()

        try:
            subjects = AttendanceListParser().parse(data)

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
        body = ProcessorRequestFactory().create(
            processor="getArray_ArrayDicsiplinesStudentAttendance"
        )

        params = SubjectParamsParser().parse(attendance_list)
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

        response = await self.client.request(
            method=Method.POST,
            url=f"{app_config.mtuci_url}/ilk/x/getProcessor",
            body=body
        )

        data = response.json()
        skips = SkipsParser().parse(data)

        return skips
