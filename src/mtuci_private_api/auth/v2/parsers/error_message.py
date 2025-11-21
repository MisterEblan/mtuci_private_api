from typing import Any

from bs4 import BeautifulSoup
from ....parsers import Parser
from ....errors import ParseError

class ErrorMessageParser(
    Parser[str, str | None]
):
    """Парсер сообщений об ошибках из HTML"""

    def validate(
            self,
            obj: str,
            **kwargs: Any
    ) -> bool:
        """Проверяет, является ли текст HTML-страницей

        Args:
            obj: HTML-текст.

        Returns:
            True если текст не пустой.
        """
        return bool(obj)

    def parse(
            self,
            obj: str,
            **kwargs: Any
    ) -> str | None:
        """Извлекает сообщение об ошибке из HTML

        Args:
            obj: HTML-текст страницы.

        Returns:
            Сообщение об ошибке или None.

        Raises:
            ParseError: если HTML некорректный.
        """
        if not self.validate(obj):
            raise ParseError(f"Invalid object: {obj}")
        try:
            soup = BeautifulSoup(obj, "html.parser")
            
            # Ищем стандартные элементы с ошибками Keycloak
            err = (
                soup.find("span", {"class": "kc-feedback-text"}) or 
                soup.find("div", {"class": "alert-error"})
            )
            
            if err:
                return err.text.strip()
            
            return None
        except Exception as e:
            raise ParseError(f"Html parsing error: {e}")
