"""Парсер пропусков конкретного предмета"""

from typing import Any
from .base import Parser
from ...errors import ParseError

class SkipsParser(
    Parser[dict[str, Any], int]
):
    """Парсер ответа о посещаемости конкретного предмета"""

    def validate(
        self,
        obj: dict[str, Any],
        **kwargs: Any
    ) -> bool:
        data = obj.get("data", {})

        response = data.get("Ответ", {})
        if not response.get("ТаблицаДанных", []):
            return False

        return True

    def parse(
        self,
        obj: dict[str, Any],
        **kwargs: Any
    ) -> int:
        if not self.validate(obj):
            raise ParseError("Object is not valid")

        data = obj.get("data", {})

        response_ = data.get("Ответ", {})
        if not (table := response_.get("ТаблицаДанных", [])):
            raise ParseError("Invalid Response: Ответ wasn't found")

        count = 0
        for subject in table:
            if not subject.get("Отметка", False):
                count += 1

        return count
