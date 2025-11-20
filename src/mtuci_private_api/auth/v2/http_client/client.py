"""Клиент для аутентификации"""

from httpx import Cookies, Headers
from ....http import BaseHttpClient

class AuthHttpClient(BaseHttpClient):
    """Клиент для аутентификации"""

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
