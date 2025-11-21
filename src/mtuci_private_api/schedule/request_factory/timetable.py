"""Фабркиа для запроса расписания"""

from datetime import datetime
from typing import Any
from ...http import RequestFactory

class TimetableRequestFactory(RequestFactory):
    """Фабрика запросов расписания"""

    def create(
        self,
        **kwargs: Any
    ) -> dict[str, Any]:
        """Создаёт параметры для запроса

        Args:
            **kwargs: дополнительные параметры.
                Обязательной должны содержать
                user_group и date
        """
        try:

            group: str       = kwargs.pop("user_group")
            date:  datetime  = kwargs.pop("date")

            params = {
                "value": group,
                "month": date.month - 1,
                "type": "group"
            }

            return params
        except KeyError as err:
            raise ValueError("Group or date not provided") from err
