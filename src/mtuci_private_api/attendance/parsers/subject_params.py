"""Парсер для получения параметров запроса"""

from typing import Any
from ...parsers import Parser
from ...errors import ParseError

class SubjectParamsParser(
    Parser[dict[str, Any], dict[str, Any]]
):
    """
    При запросе списка посещаемости в ответ также приходят
    дополнительные параметры, вроде текущего года обучения,
    семестра и т.д.
    Данный парсер вытаскивает данные параметры, т.к.
    они требуются для дальнейших запросов
    """

    def validate(
        self,
        obj: dict[str, Any],
        **kwargs: Any
    ) -> bool:
        response = obj.get(
            "data", {}
        ).get("Ответ", [])

        if not response:
            return False

        params_structure = response[0].get(
            "СтруктураПараметров", {}
        )
        if not params_structure.get("command", []):
            return False

        return True

    def parse(
        self,
        obj: dict[str, Any],
        **kwargs: Any
    ) -> dict[str, Any]:

        if not self.validate(obj):
            raise ParseError("Object is invalid")

        response = obj.get(
            "data", {}
        ).get("Ответ", [])

        params_structure = response[0].get(
            "СтруктураПараметров", {}
        )
        command = params_structure.get("command", [])
        command_params = command[0].get("ПараметрыКоманды", {})

        return command_params # type:ignore
