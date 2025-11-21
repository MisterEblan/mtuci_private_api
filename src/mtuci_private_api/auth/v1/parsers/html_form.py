"""Парсер HTML форм"""

from typing import Any

from bs4 import BeautifulSoup
from httpx import URL
from ....parsers import Parser
from ....errors import ParseError

class HtmlFormParser(
    Parser[str, dict[str, Any]]
):
    """Парсер HTML форм"""

    def validate(
        self,
        obj: str,
        **kwargs: Any
    ) -> bool:
        """Проверяет, есть ли на странице форма

        Args:
            obj: HTML-страница.
            **kwargs: дополнительные параметры.
                Не используются.

        Returns:
            Есть ли форма на странице.
        """
        soup = BeautifulSoup(obj, "html.parser")

        if not soup.find("form"):
            return False

        return True

    def parse(
        self,
        obj: str,
        **kwargs: Any
    ) -> dict[str, Any]:
        """Парсит HTML в поисках формы

        Args:
            obj: HTML-страница.
            **kwargs: дополнительные параметры. Не используюстя.

        Returns:
            Словарь с данными из формы.
            **Также содержит ключ login_url с URL для входа.**

        Raises:
            ParseError: на странице не было найдено формы.
        """

        if not self.validate(obj):
            raise ParseError(f"Invalid object: {obj[:500]}")

        soup = BeautifulSoup(obj, "html.parser")

        form = soup.find("form")

        data = {}
        for inp in form.find_all("input"):
            name = inp.get("name")
            value = inp.get("value", "")
            if name:
                data[name] = value

        login_url = URL(form["action"])

        data["login_url"] = login_url

        return data
