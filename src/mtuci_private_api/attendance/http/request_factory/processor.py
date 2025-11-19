"""Реализация фабрики запросов для эндпоинта /ilk/x/getProcessor"""

from typing import Any
from .base import RequestFactory

class ProcessorRequestFactory(RequestFactory):
    """Фабрика запросов для эндпоинта /ilk/x/getProcessor"""

    def create(
        self,
        **kwargs: Any
    ) -> dict[str, Any]:
        """Создаёт запрос

        Args:
            **kwargs: параметры запроса.
                **Обязательно должны содержать параметр processor.**

        Returns:
            Словарь с данными.
        """

        if not (processor := kwargs.pop("processor")):
            raise ValueError("Processor param not found")

        body = {
            "processor": processor,
            "referrer": "/student/attendance",
            "НомерСтраницы": 0,
            **kwargs
        }

        return body
