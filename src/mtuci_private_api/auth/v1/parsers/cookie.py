"""Парсер Cookies"""

from httpx import Response
from ....parsers import Parser
from ....errors import ParseError
from typing import Any

class CookieParser(
    Parser[Response, list[int]]
):
    """Парсер Cookies"""

    def validate(
        self,
        obj: Response,
        **kwargs: Any
    ) -> bool:
        """Проверяет, что в куках есть нужные данные

        Args:
            obj: ответ с куками.
            **kwargs: дополнительные параметры. Не используются.

        Returns:
            Есть ли нужные данные в куках.
        """
        raw = obj.cookies.get("__js_p_")

        if not raw:
            return False

        return True

    def parse(
            self,
            obj: Response,
            **kwargs: Any
    ) -> list[int]:
        """Парсит куки ответа

        Args:
            obj: ответ с куками.
            **kwargs: дополнительные параметры. Не используются.

        Returns:
            Список из преобразованных в int кук.

        Raises:
            ParseError: не найдены нужные данные в куках.
        """

        if not self.validate(obj):
            raise ParseError(f"Invalid object: {obj.cookies}")

        raw = obj.cookies.get("__js_p_", "")

        raw_splitted = raw.split(",")

        raw_splitted = list(map(int, raw_splitted))

        return raw_splitted
