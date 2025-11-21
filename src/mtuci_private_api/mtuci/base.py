"""Абстрактный МТУСИ"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from ..models import User, Schedule, Attendance

class AbstractMtuci(ABC):
    """Абстрактный класс для представления МТУСИ"""

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
    async def get_schedule(
        self,
        date: datetime,
        **kwargs: Any
    ) -> Schedule:
        """Получение расписания на опредлённую дату

        Args:
            date: дата на, которую нужно получить расписание.
            **kwargs: дополнительные параметры.

        Returns:
            Расписание на дату.

        Raises:
            GetScheduleError: ошибка при получении расписания.
        """

    @abstractmethod
    async def get_attendace(
        self,
        **kwargs: Any
    ) -> list[Attendance]:
        """Получение посещаемости

        Args:
            **kwargs: дополнительные параметры.

        Returns:
            Информация о посещаемости по предметам.

        Raises:
            GetAttendanceError: ошибка при получении информации
                о посещаемости.
        """
