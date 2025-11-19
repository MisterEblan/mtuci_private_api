"""Сервис получения информации о пользователе"""

from typing import Any
from httpx import AsyncClient

from ..errors import GetUserInfoError
from ..models.mtuci import User
from ..config import app_config

class UserService:
    """Сервис для получения информации о пользователе

    Attributes:
        client: клиент для HTTP-запросов.
    """

    def __init__(
        self,
        client: AsyncClient
    ):
        self.client = client

    async def get_user_info(self) -> User:
        body = {
            "processor": "iEmployee_card",
            "referrer": "/student/profile/student_card",
            "role": "student",
            "НомерСтраницы": 0
        }
        response = await self.client.post(
            url=f"{app_config.mtuci_url}/ilk/x/getProcessor",
            json=body
        )
        response.raise_for_status()

        data = response.json()

        return self._parse(data)

    def _parse(
        self,
        raw_user_info: dict[str, Any]
    ) -> User:
        data = raw_user_info.get(
            "data", {}
        )
        response = data.get("Ответ", {})
        block_array = response.get("МассивБлоков", [])

        if not data or not block_array or not response:
            raise GetUserInfoError("Не найден ответ от сервера")

        uid = raw_user_info.get(
            "inputParams", {}
        ).get(
            "ФизическоеЛицо", {}
        ).get("uid", "")

        values = block_array[0].get("ПереченьЗначений", {})

        department = values.get("Факультет",     {}).get("name", "")
        group      = values.get("Группа",        {}).get("name", "")
        course     = values.get("Курс",          {}).get("name", "")
        speciality = values.get("Специальность", {}).get("name", "")

        return User(
            uid=uid,
            department=department,
            group=group,
            course=course,
            speciality=speciality
        )
