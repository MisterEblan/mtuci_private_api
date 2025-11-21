from typing import Any
import urllib.parse
from bs4 import BeautifulSoup, Tag
from httpx import Response

from ....errors import ParseError
from ....parsers import Parser

class LoginFormParser(
    Parser[Response, dict[str, Any]]
):
    """Парсер HTML-формы входа"""

    def validate(
        self,
        obj: Response,
        **kwargs: Any
    ) -> bool:
        """Проверяет, что ответ содержит форму входа

        Args:
            obj: HTTP-ответ.

        Returns:
            True если страница содержит форму входа.
        """
        if obj.status_code != 200:
            return False
        text = obj.text or ""
        return "kc-form-login" in text or "name=\"username\"" in text

    def parse(
            self,
            obj: Response,
            **kwargs: Any
    ) -> dict[str, Any]:
        """Извлекает данные формы входа

        Args:
            obj: HTTP-ответ со страницей входа.

        Returns:
            Данные формы: action URL, скрытые поля, URL страницы.

        Raises:
            ParseError: если форма не найдена или некорректна.
        """
        if obj.status_code != 200:
            raise ParseError(f"Unexpected code: {obj.status_code}")

        page_url = str(obj.url)
        soup = BeautifulSoup(obj.text, "html.parser")

        # Ищем форму
        form = soup.find("form", {"id": "kc-form-login"}) or soup.find("form")
        if not form:
            snippet = (obj.text or "")[:500]
            raise ParseError(f"Login form not found {page_url}. Snippet: {snippet}")

        # Извлекаем action
        action = form.get("action")
        if not action:
            raise ParseError("Form doesn't have \"action\" attribute")

        # Делаем action абсолютным
        if not action.startswith("http"):
            action = urllib.parse.urljoin(page_url, action)

        # Извлекаем скрытые поля
        hidden_fields = self._extract_hidden_fields(form)

        return {
            "action_url": action,
            "hidden_fields": hidden_fields,
            "page_url" :page_url
        }

    @staticmethod
    def _extract_hidden_fields(form: Tag) -> dict[str, str]:
        """Извлекает скрытые поля из формы

        Args:
            form: BeautifulSoup элемент формы.

        Returns:
            Словарь со скрытыми полями.
        """
        hidden = {}
        for inp in form.find_all("input"):
            name = inp.get("name")
            if not name:
                continue

            # Скрытые поля и важные технические поля
            if (inp.get("type") == "hidden" or 
                name in ("execution", "session_code", "tab_id", "credentialId")):
                hidden[name] = inp.get("value", "") or ""
            # Предзаполненные видимые поля
            elif inp.get("value"):
                hidden[name] = inp.get("value", "")

        return hidden
