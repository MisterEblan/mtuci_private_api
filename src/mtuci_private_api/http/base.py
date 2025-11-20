"""Абстрактный клиент и базовая реализация"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

from httpx import AsyncClient, Response

class Method(str, Enum):
    """Перечисление методов для запросов"""
    GET  = "get"
    POST = "post"

class HttpClient(ABC): # pragma: no cover
    """Абстрактный HTTP-клиент для запросов"""

    @abstractmethod
    async def request(
        self,
        method: Method,
        url: str,
        **kwargs: Any
    ) -> Response:
        """Выполняет запрос

        Args:
            method: метод запроса.
            url: URL для запроса.
            **kwargs: дополнительные параметры **запроса**.
        """

class BaseHttpClient(
    HttpClient
):
    """Базовая реализация HTTP-клиента

    Attributes:
        session: авторизированная сессия.
    """
    def __init__(
        self,
        session: AsyncClient
    ):
        self.session = session

    async def request(
        self,
        method: Method,
        url: str,
        **kwargs: Any
    ) -> Response:
        """Выполняет запрос

        Args:
            method: метод запроса.
            url: URL для запроса.
            **kwargs: дополнительные параметры **запроса**.
                Если запрос имеет метод POST, то в kwargs должен
                содержаться параметр body.

        Returns:
            HTTP-ответ
        """
        match method:
            case Method.GET:
                return await self.session.get(
                    url=url,
                    **kwargs
                )

            case Method.POST:
                body = kwargs.pop("body")

                return await self.session.post(
                    url=url,
                    json=body,
                    **kwargs
                )
