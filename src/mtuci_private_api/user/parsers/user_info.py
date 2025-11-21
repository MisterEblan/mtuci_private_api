"""Парсер информации о пользователе"""

from typing import Any

from ...errors import ParseError
from ...models.mtuci import User
from ...parsers import Parser

class UserInfoParser(
    Parser[dict[str, Any], User]
):
    """Парсер для ответов об информации о пользователе"""

    def validate(
        self,
        obj: dict[str, Any],
        **kwargs: Any
    ) -> bool:
        """Проверка на валидность данных

        Args:
            obj: объект, который нужно проверить.
            **kwargs: дополнительные параметры.

        Returns:
            Валидный объект или нет.
        """
        data = obj.get(
            "data", {}
        )
        response = data.get("Ответ", {})
        block_array = response.get("МассивБлоков", [])
        if not data or not block_array or not response:
            return False

        return True

    def parse(
        self,
        obj: dict[str, Any],
        **kwargs: Any
    ) -> User:
        """Парсинг объекта

        Args:
            obj: объект, который нужно распарсить.
            **kwargs: дополнительные параметры.

        Returns:
            Данные о пользователе.

        Raises:
            ParseError: ошибка парсинга.
        """
        if not self.validate(obj):
            raise ParseError("Invalid object")

        data = obj.get(
            "data", {}
        )
        response = data.get("Ответ", {})
        block_array = response.get("МассивБлоков", [])
        input_params = obj.get("inputParams", {})

        if not (personal := input_params.get("ФизическоеЛицо")):
            raise ParseError("ФизическоеЛицо not found")

        uid = personal.get("uid", "")

        if not (name := personal.get("name", "")):
            raise ParseError("User name not found")

        values = block_array[0].get("ПереченьЗначений", {})

        department = values.get("Факультет",     {}).get("name", "")
        group      = values.get("Группа",        {}).get("name", "")
        course     = values.get("Курс",          {}).get("name", "")
        speciality = values.get("Специальность", {}).get("name", "")

        return User(
            uid=uid,
            name=name,
            department=department,
            group=group,
            course=course,
            speciality=speciality
        )
