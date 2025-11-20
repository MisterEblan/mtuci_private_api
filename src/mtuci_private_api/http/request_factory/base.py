"""Базовый класс фабрики запросов"""

from abc import ABC, abstractmethod
from typing import Any

class RequestFactory(ABC): # pragma: no cover
    """Абстрактный класс для фабрики запросов"""

    @abstractmethod
    def create(
        self,
        **kwargs: Any
    ) -> dict[str, Any]:
        """Создаёт запрос

        Args:
            **kwargs: дополнительные параметры.

        Returns:
            Словарь с данными.
        """
