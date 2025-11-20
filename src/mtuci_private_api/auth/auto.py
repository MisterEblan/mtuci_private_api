"""Сервис автоматического выбора версии аутентификации"""

from enum import Enum
from httpx import AsyncClient, Response

from .service_v1 import AuthServiceV1

from .v2 import AuthServiceV2
from .v2.parsers import (
    ErrorMessageParser,
    LoginFormParser,
    LoginUrlParser
)
from .v2.request_factory import LoginRequestFactory
from .v2.http_client import AuthHttpClient

from ..errors import AuthError


import logging

logger = logging.getLogger(__name__)

class DetectedAuth(str, Enum):
    """Перечисление возможных версий аутентификации"""
    V1 = "v1"
    V2 = "v2"

class AutoAuthService:

    parsers = {
        "error_parser": ErrorMessageParser(),
        "login_url_parser": LoginUrlParser(),
        "login_form_parser": LoginFormParser(),
    }

    def __init__(
        self,
        login: str,
        password: str,
        client: AuthHttpClient
    ):
        self.login = login
        self.password = password
        self.client   = client
        self._detected: DetectedAuth | None = None


    async def auth(self) -> Response:
        """Автоматическая аутентификация

        Пробует сначала первую версию
        сервиса аутентификации, затем - вторую.

        Returns:
            Ответ от сервера.
        """
        if self._detected == DetectedAuth.V1:
            try:
                return await AuthServiceV1(
                    login=self.login,
                    password=self.password,
                    client=self.client
                ).auth()
            except AuthError as err:
                logger.error("Error with auth V1: %s", err)
                self._detected = None

        if self._detected == DetectedAuth.V2:
            try:
                return await AuthServiceV2(
                    login=self.login,
                    password=self.password,
                    client=self.client,
                    **self.parsers,
                    request_factory=LoginRequestFactory()
                ).auth()
            except AuthError as err:
                logger.error("Error with auth V2: %s", err)
                self._detected = None

        try:
            response = await AuthServiceV1(
                login=self.login,
                password=self.password,
                client=self.client
            ).auth()

            self._detected = DetectedAuth.V1
            return response
        except AuthError as err:
            logger.error("Error detecting V1: %s", err)

            response = await AuthServiceV2(
                login=self.login,
                password=self.password,
                client=self.client,
                **self.parsers,
                request_factory=LoginRequestFactory()
            ).auth()

            self._detected = DetectedAuth.V2

            return response
