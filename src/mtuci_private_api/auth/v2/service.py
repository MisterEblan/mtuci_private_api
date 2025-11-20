"""Вторая версия сервиса аутентфикации"""

from typing import Any
from httpx import AsyncClient, Response

from ...http import Method

from ...errors import AuthError
from ...config import app_config

from .http_client import AuthHttpClient

from bs4 import BeautifulSoup

import urllib.parse
import asyncio

# WARN: Сгенерировано AI.
class AuthServiceV2:
    """Сервис аутентификации

    Attributes:
        login: логин для входа.
        password: пароль для входа.
        client: клиент для выполнения HTTP-запросов.
        FAIL_MESSAGE: сообщение о неудачной попытке входа.
        WAIT: время в секундах,
            которое нужно подождать перед отправкой следующего запроса.
    """
    FAIL_MESSAGE = "invalid username or password"
    WAIT = 1

    def __init__(
        self,
        login: str,
        password: str,
        client: AuthHttpClient
    ):
        self.login = login
        self.password = password
        self.client = client


    async def auth(self) -> Response:
        """Аутентифицирует в ЛК

        Returns:
            HTTP-ответ.
        """
        main_resp = await self._get_main()
        await asyncio.sleep(self.WAIT)

        # 1. Find URL that hosts the login form (either redirect location or page content)
        login_url = await self._discover_login_url(main_resp)

        # 2. GET the login page (where the form is) and parse form
        action_url, hidden_fields, form_page_url = await self._fetch_login_form(login_url)

        # 3. Prepare headers and body, then POST credentials to action_url
        # Referer must be the page where form was obtained
        headers_backup = dict(self.client.headers)
        try:
            self.client.headers.update({
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "https://lk.mtuci.ru",  # https://lk.mtuci.ru
                "Referer": form_page_url,
                "Sec-Fetch-User": "?1",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Dest": "document",
            })

            body = self._make_body(hidden_fields)
            resp = await self.client.request(
                method=Method.POST,
                url=action_url,
                data=body,
                follow_redirects=False
            )
            # If server responded with redirect -> follow manually to ensure cookies are set properly
            if resp.status_code in (301, 302, 303, 307, 308):
                loc = resp.headers.get("Location")
                if not loc:
                    raise AuthError("Redirect from login form has no Location header")
                # make absolute
                if not loc.startswith("http"):
                    loc = urllib.parse.urljoin(str(action_url), loc)
                # follow with redirects enabled to land on final page
                resp = await self.client.request(
                    method=Method.GET,
                    url=loc,
                    follow_redirects=True
                )

            # If 200 and still on login form -> extract error message if any
            if resp.status_code == 200 and self._is_login_form_page(resp.text):
                # parse error messages
                soup = BeautifulSoup(resp.text, "html.parser")
                err = soup.find("span", {"class": "kc-feedback-text"}) or soup.find("div", {"class": "alert-error"})
                msg = err.text.strip() if err else "Unknown login error (login form re-presented)"
                raise AuthError(f"Login failed: {msg}")

            final_url = str(resp.url)
            # If Keycloak returned login-error via redirect query param
            if "login-error" in final_url or "message=" in final_url:
                decoded = urllib.parse.unquote(final_url.split("message=")[-1]) if "message=" in final_url else final_url
                raise AuthError(f"Application login failed: {decoded}")

            # Heuristic: check that keycloak identity/session cookies present
            if not any(k.startswith("KEYCLOAK") or k.startswith("AUTH_SESSION_ID") for k in self.client.cookies.keys()):
                # maybe login succeeded in keycloak but app-level cookie missing; try hitting main page once
                check = await self.client.request(
                    method=Method.GET,
                    url=app_config.mtuci_url,
                    follow_redirects=True
                )
                if not any(k.startswith("KEYCLOAK") or k.startswith("AUTH_SESSION_ID") for k in self.client.cookies.keys()):
                    raise AuthError("Login appears unsuccessful: key cookies not present after authentication")

            # Final: try to visit application main page to get app cookies (js anti-bot etc.)
            await asyncio.sleep(self.WAIT)
            app_resp = await self.client.request(
                method=Method.GET,
                url=app_config.mtuci_url,
                follow_redirects=True
            )
            return app_resp

        finally:
            # restore headers that might be important for outer flows
            self.client.headers.clear()
            self.client.headers.update(headers_backup)

    async def _get_main(self) -> Response:
        """Делает GET запрос на главную страницу,
        чтобы получить данные о локации.

        Returns:
            Ответ на запрос.
        """
        resp = await self.client.request(
            method=Method.GET,
            url=app_config.mtuci_url,
            follow_redirects=False
        )
        return resp

    async def _discover_login_url(
            self,
            main_resp: Response
    ) -> str:
        """Определяет URL для входа в аккаунт

        Если в ответ на запрос главной страницы пришёл редирект,
        то используем Location заголовок.
        Если пришёл HTML - парсим и ищем ссылки/формы для Keycloak auth.

        Args:
            main_response: ответ на запрос главной страницы.

        Returns:
            URL для входа.            
        """
        # 1) redirect from server (common)
        if main_resp.status_code in (301, 302, 303, 307, 308):
            loc = main_resp.headers.get("Location")
            if loc:
                if not loc.startswith("http"):
                    loc = urllib.parse.urljoin(str(main_resp.url), loc)
                return loc

        # 2) maybe main page contains link / script redirect to auth — parse HTML
        text = main_resp.text or ""
        soup = BeautifulSoup(text, "html.parser")

        # look for forms or anchors that contain 'protocol/openid-connect' or 'login-actions'
        candidate = None
        a = soup.find("a", href=True)
        if a and ("protocol/openid-connect" in a["href"] or "login-actions" in a["href"]):
            candidate = a["href"]

        if not candidate:
            form = soup.find("form", action=True)
            if form and ("protocol/openid-connect" in form["action"] or "login-actions" in form["action"]):
                candidate = form["action"]

        if not candidate:
            # meta refresh fallback
            meta = soup.find("meta", {"http-equiv": "refresh"})
            if meta and "url=" in meta.get("content", ""):
                content = meta["content"]
                candidate = content.split("url=")[-1]

        if not candidate:
            # last resort: use standard auth entry — but without guessing state
            return "https://lk.mtuci.ru/bvzauth/realms/master/protocol/openid-connect/auth"
        # make absolute
        if not candidate.startswith("http"):
            candidate = urllib.parse.urljoin(str(main_resp.url), candidate)
        return candidate

    async def _fetch_login_form(self, login_url: str) -> tuple[str, dict[str, str], str]:
        """GET the login page and extract form.action and hidden fields. Returns (action_url, hidden_fields, page_url)."""
        resp = await self.client.request(
            method=Method.GET,
            url=login_url,
            follow_redirects=True
        )
        if resp.status_code != 200:
            raise AuthError(f"Failed to fetch login page: {resp.status_code}")

        page_url = str(resp.url)
        soup = BeautifulSoup(resp.text, "html.parser")

        # Prefer well-known Keycloak form id
        form = soup.find("form", {"id": "kc-form-login"}) or soup.find("form")
        if not form:
            # Dump a little context to help debugging
            snippet = (resp.text or "")[:500]
            raise AuthError(f"Login form not found on page {page_url}. Snippet: {snippet}")

        action = form.get("action")
        if not action:
            raise AuthError("Login form action URL not found")

        # absolute action
        if not action.startswith("http"):
            action = urllib.parse.urljoin(page_url, action)

        hidden: dict[str, str] = {}
        for inp in form.find_all("input"):
            name = inp.get("name")
            if not name:
                continue
            if inp.get("type") == "hidden" or name in ("execution", "session_code", "tab_id", "credentialId"):
                hidden[name] = inp.get("value", "") or ""
            # also capture any prefilled fields (some builds use value attr)
            elif inp.get("value"):
                # keep prefilled visible fields too (but will be overwritten by username/password)
                hidden[name] = inp.get("value", "")

        # ensure we didn't miss execution/session_code/tab_id — they're critical
        # but we won't fabricate them: if missing, we still proceed and server will reject — this surfaces earlier
        return action, hidden, page_url

    def _make_body(self, hidden_fields: dict[str, str]) -> dict[str, Any]:
        """Create POST body merging hidden fields and credentials."""

        """Создаёт тело POST запроса, сливая в него и креды и скрытые поля

        Args:
            hidden_fields: найденные скрытые поля.

        Returns:
            Тело запроса.
        """
        body = dict(hidden_fields)  # copy
        # overwrite or set required fields
        body.update({
            "username": self.login,
            "password": self.password,
            # some deployments expect "remember-me" or "rememberMe" with different values
            "rememberMe": hidden_fields.get("rememberMe", hidden_fields.get("remember-me", "on")),
            # ensure credentialId exists
            "credentialId": hidden_fields.get("credentialId", "")
        })
        return body

    @staticmethod
    def _is_login_form_page(text: str) -> bool:
        """Определяет, есть ли на странице форма для ввода данных

        Args:
            text: HTML-страница.

        Returns:
            Является ли страницей для входа.
        """
        return "kc-form-login" in (text or "") or "name=\"username\"" in (text or "")
