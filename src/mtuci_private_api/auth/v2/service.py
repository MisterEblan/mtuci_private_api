"""Вторая версия сервиса аутентфикации"""

from httpx import Response

from ...http import Method, BaseHttpClient

from ...errors import AuthError
from ...config import app_config
from .parsers import (
    ErrorMessageParser,
    LoginUrlParser,
    LoginFormParser
)
from .request_factory import LoginRequestFactory

import urllib.parse
import asyncio

# WARN: Сгенерировано AI.
class AuthServiceV2:
    """Сервис аутентификации.

    Координирует работу HTTP-клиента, парсеров и фабрики запросов
    для выполнения процесса аутентификации.

    Attributes:
        login: логин пользователя.
        password: пароль пользователя.
        client: HTTP-клиент для запросов.
        login_url_parser: парсер URL страницы входа.
        login_form_parser: парсер формы входа.
        error_parser: парсер сообщений об ошибках.
        request_factory: фабрика запросов аутентификации.
        WAIT: задержка между запросами в секундах.
    """
    WAIT = 1

    def __init__(
        self,
        login: str,
        password: str,
        client:       BaseHttpClient,
        login_url_parser:  LoginUrlParser,
        login_form_parser: LoginFormParser,
        error_parser:      ErrorMessageParser,
        request_factory:   LoginRequestFactory
    ):
        self.login = login
        self.password = password
        self.client = client
        self.login_url_parser = login_url_parser
        self.login_form_parser = login_form_parser
        self.error_parser = error_parser
        self.request_factory = request_factory

    async def auth(self) -> Response:
        """Выполняет полный цикл аутентификации

        Returns:
            HTTP-ответ от приложения после успешной аутентификации.

        Raises:
            AuthError: если аутентификация не удалась.
        """
        # 1. Получаем главную страницу
        main_resp = await self.client.request(
            Method.GET,
            app_config.mtuci_url,
            follow_redirects=False
        )

        await asyncio.sleep(self.WAIT)

        # 2. Определяем URL страницы входа
        login_url = self.login_url_parser.parse(main_resp)

        # 3. Получаем форму входа
        form_resp = await self.client.request(
            Method.GET,
            login_url,
            follow_redirects=True
        )
        
        if not self.login_form_parser.validate(form_resp):
            raise AuthError("Не удалось получить форму входа")
        
        form_data = self.login_form_parser.parse(form_resp)

        # 4. Создаём запрос для отправки credentials
        request_data = self.request_factory.create(
            action_url=form_data["action_url"],
            hidden_fields=form_data["hidden_fields"],
            form_page_url=form_data["page_url"],
            username=self.login,
            password=self.password
        )

        # 5. Отправляем credentials
        headers_backup = self.client.backup_headers()
        try:
            self.client.update_headers(request_data["headers"])
            
            resp = await self.client.request(
                Method.POST,
                request_data["url"],
                data=request_data["data"],
                follow_redirects=False,
                body={}
            )
            # Обрабатываем redirect
            if resp.status_code in (301, 302, 303, 307, 308):
                resp = await self._follow_redirect(resp)

            # Проверяем на ошибки
            await self._check_auth_errors(resp)

            # Проверяем наличие cookies
            self._validate_cookies()

            # 6. Получаем финальную страницу приложения
            await asyncio.sleep(self.WAIT)
            app_resp = await self.client.request(
                Method.GET,
                app_config.mtuci_url,
                follow_redirects=True
            )
            
            return app_resp

        finally:
            self.client.restore_headers(headers_backup)

    async def _follow_redirect(self, resp: Response) -> Response:
        """Следует по redirect после отправки формы

        Args:
            resp: ответ с redirect.

        Returns:
            Финальный ответ после redirect.

        Raises:
            AuthError: если redirect некорректен.
        """
        loc = resp.headers.get("Location")
        if not loc:
            raise AuthError("Redirect не содержит заголовок Location")

        # Делаем URL абсолютным
        if not loc.startswith("http"):
            loc = urllib.parse.urljoin(str(resp.url), loc)

        loc_resp = await self.client.request(
            Method.GET,
            loc,
            follow_redirects=True
        )

        return loc_resp

    async def _check_auth_errors(self, resp: Response) -> None:
        """Проверяет ответ на наличие ошибок аутентификации

        Args:
            resp: HTTP-ответ.

        Raises:
            AuthError: если обнаружена ошибка аутентификации.
        """
        # Проверяем, не вернулись ли мы на форму входа
        if resp.status_code == 200 and self._is_login_page(resp.text):
            error_msg = self.error_parser.parse(resp.text)
            if error_msg:
                raise AuthError(f"Ошибка входа: {error_msg}")
            raise AuthError("Ошибка входа: форма входа отображена повторно")

        # Проверяем URL на ошибки
        final_url = str(resp.url)
        if "login-error" in final_url or "message=" in final_url:
            if "message=" in final_url:
                decoded = urllib.parse.unquote(final_url.split("message=")[-1])
                raise AuthError(f"Ошибка входа в приложение: {decoded}")
            raise AuthError(f"Ошибка входа в приложение: {final_url}")

    def _validate_cookies(self) -> None:
        """Проверяет наличие необходимых cookies

        Raises:
            AuthError: если необходимые cookies отсутствуют.
        """
        cookies = self.client.cookies
        has_keycloak = any(
            k.startswith("KEYCLOAK") or k.startswith("AUTH_SESSION_ID")
            for k in cookies.keys()
        )
        
        if not has_keycloak:
            raise AuthError(
                "Вход не выполнен: отсутствуют необходимые cookies"
            )

    @staticmethod
    def _is_login_page(text: str) -> bool:
        """Проверяет, является ли страница формой входа

        Args:
            text: HTML-текст страницы.

        Returns:
            True если это страница входа.
        """
        return "kc-form-login" in (text or "") or 'name="username"' in (text or "")
