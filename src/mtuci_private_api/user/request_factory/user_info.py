from typing import Any
from ...http import RequestFactory

class UserInfoRequestFactory(RequestFactory):

    def create(
        self,
        **kwargs: Any
    ) -> dict[str, Any]:
        """Создаёт тело для запроса о данных пользователя

        Args:
            **kwargs: дополнительные параметры.
                Не используются.

        Returns:
            Словарь с данными.
        """
        body = {
            "processor": "iEmployee_card",
            "referrer": "/student/profile/student_card",
            "role": "student",
            "НомерСтраницы": 0
        }

        return body
