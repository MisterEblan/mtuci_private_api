from typing import Any
from httpx import Request, Response
import pytest
from src.mtuci_private_api.auth.v2.parsers import (
    LoginFormParser,
    ErrorMessageParser,
)
from src.mtuci_private_api.parsers import Parser
from src.mtuci_private_api.errors import ParseError

class TestAuthV2Parsers:

    # --- Responses ---

        # --- Login ---

    @pytest.fixture
    def login_response(self) -> Response:

        with open(
            "tests/fixtures/form_response.html",
            "rb"
        ) as f:
            content = f.read()

        return Response(
            status_code=200,
            content=content,
            request=Request(method="POST", url="lk.mtuci.ru")
        )

    @pytest.fixture
    def bad_status_login_response(self) -> Response:
        return Response(
            status_code=400,
        )

    @pytest.fixture
    def bad_content_login_response(self) -> Response:
        return Response(
            status_code=200,
            content=b"Nothing in here",
            request=Request(method="POST", url="lk.mtuci.ru")
        )

        # --- Loc ---

    @pytest.fixture
    def loc_response(self) -> str:
        with open(
            "tests/fixtures/loc_response.html",
            "r",
            encoding="utf-8"
        ) as f:
            content = f.read()

        return content

    @pytest.fixture
    def bad_loc_response(self) -> str:
        with open(
            "tests/fixtures/loc_response.html",
            "r",
            encoding="utf-8"
        ) as f:
            content = f.read()

        content += "<span class=\"kc-feedback-text\"> Very Bad Error </span>"


    @pytest.fixture
    def login_form_parser(self) -> Parser[Response, dict[str, Any]]:
        return LoginFormParser()

    @pytest.fixture
    def error_message_parser(self) -> Parser[str, str | None]:
        return ErrorMessageParser()

    # --- Login Form Parser ---

    def test_form_parser(
        self,
        login_form_parser: Parser[Response, dict[str, Any]],
        login_response: Response
    ):
        data = login_form_parser.parse(login_response)

        assert data, f"Ожидался не пустой объект. Получили {data}"

        assert data["action_url"], \
        "Ожидалось, что будет найдено action_url"

        assert data["hidden_fields"], \
        "Ожидалось, что будет найдено hidden_fields"

    def test_form_parser_fail_status(
        self,
        login_form_parser: Parser[Response, dict[str, Any]],
        bad_status_login_response: Response
    ):
        with pytest.raises(ParseError):
            login_form_parser.parse(bad_status_login_response)

    def test_form_parser_fail_content(
        self,
        login_form_parser: Parser[Response, dict[str, Any]],
        bad_content_login_response: Response
    ):
        with pytest.raises(ParseError):
            login_form_parser.parse(bad_content_login_response)

    # --- Error Message Parser ---

    def test_err_message_parser(
        self,
        error_message_parser: Parser[str, str | None],
        loc_response: str
    ):
        error_msg = error_message_parser.parse(loc_response)


        assert not error_msg, \
        (
            "Ожидалось, что не будет найдено сообщения об ошибке."
                f"Получили {error_msg}"
        )

    def test_err_message_parser_fail(
        self,
        error_message_parser: Parser[str, str | None],
        bad_loc_response: str
    ):
        with pytest.raises(ParseError):
            error_message_parser.parse(bad_loc_response)
