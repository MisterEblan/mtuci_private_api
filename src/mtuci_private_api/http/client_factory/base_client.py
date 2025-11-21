"""Фабрика базовых HTTP-клиентов"""

from typing import Any

from httpx import AsyncClient
from ..base import BaseHttpClient, HttpClient
from .base import HttpClientFactory

class BaseHttpClientFactory(HttpClientFactory):
    """Фабрика базовых HTTP-клиентов"""

    def create(
        self,
        **kwargs: Any
    ) -> HttpClient:
        """Создаёт базовый HTTP-клиент
        
        Args:
            **kwargs: дополнительные параметры.
                Не используются.

        Returns:
            Базовый HTTP-клиент с установленными заголовками.
        """

        httpx_client = self._get_httpx_client()

        return BaseHttpClient(httpx_client)


    def _get_httpx_client(self) -> AsyncClient:
        """Создаёт асинхронный httpx клиент с заголовками

        Returns:
            Асинхронный клиент httpx
                с установленными заголовками
                и параметрами.
        """
        return AsyncClient(
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:142.0) " + \
                    "Gecko/20100101 Firefox/142.0",
                "Accept": "text/html,application/xhtml+xml," + \
                    "application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            },
            # cookies=Cookies(),
            follow_redirects=True
        )
