"""Фабрика запросов для аутентификации версии 1"""

from typing import Any
from ....http import RequestFactory

class LoginRequestFactoryV1(RequestFactory):
    """Фабрика запросов для аутентификации версии 1"""

    def create(
        self,
        **kwargs: Any
    ) -> dict[str, Any]:
        """Создаёт запрос для аутентификации

        Args:
            **kwargs: дополнительные параметры.
                Должны содержать login и password.

        Returns:
            Тело запроса.

        Raises:
            ValueError: если не были переданы login и password
        """
        try:
            login = kwargs.pop("login")
            password = kwargs.pop("password")

            return {
                "username": login,
                "password": password,
                "rememberMe": "on",
                "credentialId": ""
            }

        except KeyError as err:
            raise ValueError("Login or password not provided") from err
