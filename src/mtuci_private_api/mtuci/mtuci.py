"""Реализация класса Mtuci"""

from datetime import datetime
from typing import Any
from .base import AbstractMtuci
from ..http import BaseHttpClientFactory

from ..auth import AutoAuthService
from ..user import UserService
from ..attendance import AttendanceService
from ..schedule import ScheduleService
from ..models import (
    User,
    Schedule,
    Attendance
)

import logging

logger = logging.getLogger(__name__)

class Mtuci(AbstractMtuci):
    """Класс, предаставляющий собой МТУСИ

    Реализует интерфейс асинхронного контекстного менеджера,
    выполняя аутентификацию при входе в контекст и
    очищая клиент после выхода.

    Attributes:
        login:              логин пользователя.
        password:           пароль пользователя
        client_factory:     фабрика клиентов.
        auth_service:       сервис аутентификации.
        attendance_service: сервис посещаемости.
        user_service:       сервис для получения информации
                                о пользователе.
    """

    def __init__(
        self,
        login: str,
        password: str,
        client_factory = BaseHttpClientFactory()
    ):
        self.login = login
        self.password = password

        self.client_factory = client_factory
        self.client = client_factory.create()

        self.user_info: User | None = None

        self.auth_service = AutoAuthService(
            login=self.login,
            password=self.password,
            client=self.client
        )
        self.attendance_service = AttendanceService(self.client)
        self.user_service       = UserService(self.client)
        self.schedule_service   = ScheduleService(self.client)

    async def auth(
        self,
        **kwargs: Any
    ) -> None:
        """Вход в аккаунт ЛК

        Args:
            **kwargs: дополнительные параметры.

        Returns:
            Ничего, просто выполняет вход.

        Raises:
            AuthError: ошибка при входе в аккаунт.
        """
        logger.info("Authenticating")
        await self.auth_service.auth()

    async def get_user_info(
        self,
        **kwargs: Any
    ) -> User:
        """Получение информации о пользователе

        Args:
            **kwargs: дополнительные параметры.

        Returns:
            Полученная информация о пользователе.

        Raises:
            GetUserInfoError: ошибка при получении информации.
        """

        logger.info("Getting user info")

        if self.user_info:
            logger.info("Already have user info")
            return self.user_info
        else:
            logger.info(
                "User info not found. Requesting"
            )
            user = await self.user_service.get_user_info()

            self.user_info = user
            return user


    async def get_attendace(
        self,
        **kwargs: Any
    ) -> list[Attendance]:
        """Получение расписания на опредлённую дату

        Args:
            date: дата на, которую нужно получить расписание.
            **kwargs: дополнительные параметры.

        Returns:
            Расписание на дату.

        Raises:
            GetScheduleError: ошибка при получении расписания.
        """
        logger.info("Getting attendance")
        return await self.attendance_service.get_attendance()

    async def get_schedule(
        self,
        date: datetime,
        **kwargs: Any
    ) -> Schedule:
        """Получение посещаемости

        Имеет побочный эффект: вызывает get_user_info.

        Args:
            **kwargs: дополнительные параметры.

        Returns:
            Информация о посещаемости по предметам.

        Raises:
            GetAttendanceError: ошибка при получении информации
                о посещаемости.
            GetUserInfoError: ошибка при получении информации о пользователе.
        """
        logger.info("Getting schedule for %s", date)

        user = await self.get_user_info()

        return await self.schedule_service.get_schedule(
            date,
            user
        )

    async def __aenter__(self) -> "Mtuci":
        logger.debug("Entering context")
        await self.auth()
        self.user_info = await self.get_user_info()

        return self

    async def __aexit__(
        self,
        exc_type,
        exc,
        tb
    ) -> None:
        logger.debug("Exiting context, recreating client")
        self.client = self.client_factory.create()
