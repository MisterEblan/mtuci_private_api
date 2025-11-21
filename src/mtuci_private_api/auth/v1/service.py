"""Изначальный сервис аутентфикации"""

from httpx import Response

from .parsers import HtmlFormParser, CookieParser
from .request_factory import LoginRequestFactoryV1

from ...http import Method, BaseHttpClient

from ...errors import AuthError, ParseError
from ...config import app_config

import urllib.parse
import asyncio
import logging

logger = logging.getLogger(__name__)

class AuthServiceV1:
    """Сервис аутентификации

    Attributes:
        login: логин для входа.
        password: пароль для входа.
        client: клиент для выполнения HTTP-запросов.
        FAIL_MESSAGE: сообщение о неудачной попытке входа.
        WAIT: время в секундах,
            которое нужно подождать перед отправкой следующего запроса.
    """
    FAIL_MESSAGE = "invalid username or password"
    WAIT = 1

    def __init__(
        self,
        login: str,
        password: str,
        client: BaseHttpClient
    ):
        self.login = login
        self.password = password
        self.client = client

    async def auth(self) -> Response:
        """Аутентификация

        Returns:
            ответ от сервера.
        """
        response = await self._get_session()

        text = response.text

        data = HtmlFormParser().parse(
            text
        )

        login_url = data.pop("login_url")
        data["username"] = self.login
        data["password"] = self.password

        response = await self.client.request(
            method=Method.POST,
            url=login_url,
            data=data,
            body={}
        )

        if not self._is_success(response):
            raise AuthError("Invalid credentials")

        return response


    def _is_success(
        self,
        response: Response
    ) -> bool:
        """Проверка на успешность запроса

        Args:
            response: ответ на запрос аутентификации.

        Returns:
            Являлся ли запрос успешным.
        """
        text = response.text

        return self.FAIL_MESSAGE not in text.lower()


    #WARN: Сгенерировано AI
    def _get_jhash(self, code: int) -> int:
        """Генерирует jhash для входа

        Args:
            code: код, полученный из куки.

        Returns:
            сгенерированный jhash.
        """
        x = 123456789
        k = 0
        for i in range(1677696):
            x = ((x + code) ^ (x + (x % 3) + (x % 17) + code) ^ i) % 16776960
            if x % 117 == 0:
                k = (k + 1) % 1111
        return k

    async def _get_session(self) -> Response:
        """Выполняет первичный вход, получает куки

        Returns:
            Ответ от сервера после первичного входа.
        """
        body = LoginRequestFactoryV1().create(
            login=self.login,
            password=self.password
        )
        response_1 = await self.client.request(
            method=Method.POST,
            url=app_config.mtuci_url + \
                "/bvzauth/realms/master/login-actions/authenticate",
            data=body,
            body={}
        )

        try:
            cookies_ints = CookieParser().parse(response_1)

            code = cookies_ints[0]

            jhash = self._get_jhash(code)

            self.client.cookies.set(
                "__jhash_",
                str(jhash),
                domain="lk.mtuci.ru",
                path="/"
            )
            self.client.cookies.set(
                "__jua_",
                urllib.parse.quote(self.client.headers.get("User-Agent")),
                domain="lk.mtuci.ru",
                path="/"
            )

            await asyncio.sleep(self.WAIT)

            response_2 = await self.client.request(
                method=Method.GET,
                url=app_config.mtuci_url
            )

            return response_2

        except ParseError as err:
                raise AuthError("Error parsing Cookies") from err
