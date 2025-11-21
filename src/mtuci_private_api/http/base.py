"""Абстрактный клиент и базовая реализация"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

from httpx import URL, AsyncClient, Cookies, Headers, Response

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
        url: str | URL,
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
    @property
    def headers(self) -> Headers:
        return self.session.headers

    @property
    def cookies(self) -> Cookies:
        """Доступ к cookies клиента"""
        return self.session.cookies

    def backup_headers(self) -> dict[str, str]:
        """Сохраняет текущие заголовки"""
        return dict(self.session.headers)

    def restore_headers(self, backup: dict[str, str]) -> None:
        """Восстанавливает заголовки из backup"""
        self.session.headers.clear()
        self.session.headers.update(backup)

    def update_headers(self, headers: dict[str, str]) -> None:
        """Обновляет заголовки клиента"""
        self.session.headers.update(headers)
