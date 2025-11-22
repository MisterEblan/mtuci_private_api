"""Сервис автоматического выбора версии аутентификации"""

from enum import Enum
from httpx import Response

from .v1 import AuthServiceV1

from .v2 import AuthServiceV2
from ..errors import AuthError

from ..http import BaseHttpClient

import logging

logger = logging.getLogger(__name__)

class DetectedAuth(str, Enum):
    """Перечисление возможных версий аутентификации"""
    V1 = "v1"
    V2 = "v2"

class AutoAuthService:
    """Автоматический сервис аутентификации"""

    def __init__(
        self,
        login: str,
        password: str,
        client: BaseHttpClient
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
        logger.info("Detecting auth version")
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
            logger.info("Detected V1")
            return response
        except AuthError as err:
            logger.error("Error while trying V1: %s", err)

            response = await AuthServiceV2(
                login=self.login,
                password=self.password,
                client=self.client,
            ).auth()

            logger.info("Detected V2")
            self._detected = DetectedAuth.V2

            return response
