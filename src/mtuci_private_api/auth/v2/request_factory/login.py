from typing import Any
from ....http import RequestFactory

class LoginRequestFactory(RequestFactory):
    """Фабрика для создания запросов аутентификации"""

    required = [
        "action_url",
        "hidden_fields",
        "form_page_url",
        "username",
        "password"
    ]

    def create(
            self,
            **kwargs: Any
    ) -> dict[str, Any]:
        """Создаёт данные для POST-запроса аутентификации

        Expected kwargs:
            - action_url (str): URL для отправки формы
            - hidden_fields (dict): скрытые поля формы
            - form_page_url (str): URL страницы с формой (для Referer)
            - username (str): логин
            - password (str): пароль

        Returns:
            Словарь с ключами: url, headers, data

        Raises:
            ValueError: если отсутствуют обязательные параметры.
        """
        for key in self.required:
            if key not in kwargs:
                raise ValueError(f"Отсутствует обязательный параметр: {key}")

        action_url    = kwargs["action_url"]
        hidden_fields = kwargs["hidden_fields"]
        form_page_url = kwargs["form_page_url"]
        username = kwargs["username"]
        password = kwargs["password"]

        # Формируем заголовки
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://lk.mtuci.ru",
            "Referer": form_page_url,
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "document",
        }

        # Формируем тело запроса
        body = dict(hidden_fields)
        body.update({
            "username": username,
            "password": password,
            "rememberMe": hidden_fields.get(
                "rememberMe",
                hidden_fields.get("remember-me", "on")
            ),
            "credentialId": hidden_fields.get("credentialId", "")
        })

        return {
            "url": action_url,
            "headers": headers,
            "data": body
        }
