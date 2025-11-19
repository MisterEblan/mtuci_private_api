from abc import ABC, abstractmethod
from typing import Any

class Parser[T, P](ABC):
    """Абстрактный парсер"""

    @abstractmethod
    def validate(
        self,
        obj: T,
        **kwargs: Any
    ) -> bool:
        """Проверка на валидность данных

        Args:
            obj: объект, который нужно проверить.
            **kwargs: дополнительные параметры.

        Returns:
            Валидный объект или нет.
        """

    @abstractmethod
    def parse(
        self,
        obj: T,
        **kwargs: Any
    ) -> P:
        """Парсинг объекта

        Args:
            obj: объект, который нужно распарсить.
            **kwargs: дополнительные параметры.

        Returns:
            Распаршенный объект.

        Raises:
            ParseError: ошибка парсинга.
        """
