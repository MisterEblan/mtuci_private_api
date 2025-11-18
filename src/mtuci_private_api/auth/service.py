"""Сервис аутентфикации"""

from typing import Any
from httpx import URL, AsyncClient, Response

from ..errors import AuthError
from ..config import app_config

from bs4 import BeautifulSoup

import urllib.parse
import asyncio

class AuthService:
    """Сервис аутентификации

    Attributes:
        login: логин для входа.
        password: пароль для входа.
        client: клиент для выполнения HTTP-запросов.
        FAIL_MESSAGE: сообщение о неудачной попытке входа.
        WAIT: время в секундах,
            которое нужно подождать перед отправкой следующего запроса.
    """

    def __init__(
        self,
        login: str,
        password: str,
        client: AsyncClient
    ):
        self.login = login
        self.password = password
        self.client = client

        self.FAIL_MESSAGE = "invalid username or password"
        self.WAIT = 1

    async def auth(self) -> Response:
        """Аутентификация

        Returns:
            ответ от сервера.
        """
        response = await self._get_session()

        text = response.text

        soup = BeautifulSoup(text, "html.parser")

        if not (form := soup.find("form")):
            raise AuthError("Form not found")

        data = {}
        for inp in form.find_all("input"):
            name = inp.get("name")
            value = inp.get("value", "")
            if name:
                data[name] = value

        data["username"] = self.login
        data["password"] = self.password

        login_url = URL(form["action"])

        response = await self.client.post(login_url, data=data)

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

    def _make_body(self) -> dict[str, Any]:
        """Создаёт тело запроса аутентификации

        Returns:
            Словарь с телом запроса.
        """
        return {
            "username": self.login,
            "password": self.password,
            "rememberMe": "on",
            "credentialId": ""
        }

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
        body = self._make_body()
        response_1 = await self.client.post(
            url=app_config.mtuci_url + \
                "/bvzauth/realms/master/login-actions/authenticate",
            data=body
        )

        raw = response_1.cookies.get("__js_p_")

        if not raw:
            print(response_1.text)
            raise AuthError("Cookies not received")

        raw_splitted = raw.split(",")

        code = int(raw_splitted[0])
        age  = int(raw_splitted[1])
        sec  = int(raw_splitted[2])

        jhash = self._get_jhash(code)

        self.client.cookies.set("__jhash_", str(jhash), domain="lk.mtuci.ru", path="/")
        self.client.cookies.set(
            "__jua_",
            urllib.parse.quote(self.client.headers.get("User-Agent")),
            domain="lk.mtuci.ru",
            path="/"
        )

        await asyncio.sleep(self.WAIT)

        response_2 = await self.client.get(app_config.mtuci_url)

        return response_2
