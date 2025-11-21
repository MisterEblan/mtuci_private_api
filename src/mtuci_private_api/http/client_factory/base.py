"""Абстрактная фабрика"""
from abc import ABC, abstractmethod
from typing import Any

from ..base import HttpClient

class HttpClientFactory(ABC):
    """Абстрактная фабрика HTTP-клиентов"""

    @abstractmethod
    def create(
        self,
        **kwags: Any
    ) -> HttpClient:
        """Создаёт HTTP-клиент

        Args:
            **kwargs: дополнительные параметры.

        Returns:
             HTTP-клиент.
        """
