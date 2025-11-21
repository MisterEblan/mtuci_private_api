"""Парсер для извлечения URL страницы"""

from typing import Any
import urllib.parse
from bs4 import BeautifulSoup
from httpx import Response
from ....parsers import Parser

class LoginUrlParser(
    Parser[Response, str]
):
    """Парсер для извлечения URL страницы"""

    default_url = (
        "https://lk.mtuci.ru/"
        "bvzauth/realms/master/protocol/openid-connect/auth"
    )

    def validate(
            self,
            obj: Response,
            **kwargs: Any
    ) -> bool:
        """Проверяет, содержит ли ответ информацию о URL входа

        Args:
            obj: HTTP-ответ.

        Returns:
            True если ответ содержит redirect или HTML с формой.
        """
        if obj.status_code in (301, 302, 303, 307, 308):
            return "Location" in obj.headers
        return bool(obj.text)

    def parse(
            self,
            obj: Response,
            **kwargs: Any
    ) -> str:
        """Извлекает URL страницы входа из ответа

        Args:
            obj: HTTP-ответ от главной страницы.

        Returns:
            URL страницы входа.

        Raises:
            ParseError: если не удалось найти URL входа.
        """
        # 1. Проверяем redirect
        if obj.status_code in (301, 302, 303, 307, 308):
            loc = obj.headers.get("Location")
            if loc:
                return self._make_absolute(loc, str(obj.url))

        # 2. Парсим HTML
        soup = BeautifulSoup(obj.text, "html.parser")

        # Ищем ссылки/формы с Keycloak auth
        candidate = self._find_auth_link(soup)
        if candidate:
            return self._make_absolute(candidate, str(obj.url))

        # 3. Fallback на стандартный URL
        return self.default_url

    def _find_auth_link(
            self,
            soup: BeautifulSoup
    ) -> str | None:
        """Ищет ссылку на аутентификацию в HTML

        Args:
            soup: объект для парсинга HTML.

        Returns:
            Найденную ссылку или ничего.
        """

        a = soup.find("a", href=True)
        if a and self._is_auth_url(a["href"]):
            return a["href"]

        # Ищем в формах
        form = soup.find("form", action=True)
        if form and self._is_auth_url(form["action"]):
            return form["action"]

        # Ищем meta refresh
        meta = soup.find("meta", {"http-equiv": "refresh"})
        if meta and "url=" in meta.get("content", ""):
            content = meta["content"]
            return content.split("url=")[-1]

        return None

    @staticmethod
    def _is_auth_url(url: str) -> bool:
        """Проверяет, является ли URL ссылкой на аутентификацию

        Args:
            url: URL для проверки.

        Returns:
            Является ли ссылкой на аутентификацию.
        """
        return "protocol/openid-connect" in url or "login-actions" in url

    @staticmethod
    def _make_absolute(url: str, base_url: str) -> str:
        """Преобразует относительный URL в абсолютный

        Args:
            url: относительный URL.
            base_url: базовый URL.

        Returns:
            абсолютный URL.
        """
        if url.startswith("http"):
            return url
        return urllib.parse.urljoin(base_url, url)
