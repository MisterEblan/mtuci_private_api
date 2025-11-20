"""Реализация фабрики запросов для эндпоинта /ilk/x/getProcessor"""

from typing import Any
from ...http.request_factory import RequestFactory

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

        try:
            processor = kwargs.pop("processor")

            body = {
                "processor": processor,
                "referrer": "/student/attendance",
                "НомерСтраницы": 0,
                **kwargs
            }

            return body
        except KeyError as err:
            raise ValueError("Processor param not found") from err
