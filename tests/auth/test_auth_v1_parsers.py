import re
from typing import Any
import pytest
from src.mtuci_private_api.auth.v1.parsers import HtmlFormParser
from src.mtuci_private_api.parsers import Parser
from src.mtuci_private_api.errors import ParseError

class TestAuthV1Parsers:

    @pytest.fixture
    def html_form_parser(self) -> Parser[str, dict[str, Any]]:
        return HtmlFormParser()
    
    @pytest.fixture
    def html_form(self) -> str:
        with open(
            "tests/fixtures/v1_auth_response2",
            "r",
            encoding="utf-8"
        ) as f:
            content = f.read()

        return content

    def test_html_form_parser(
        self,
        html_form_parser: Parser[str, dict[str, Any]],
        html_form: str
    ):
        data = html_form_parser.parse(html_form)

        assert data, f"Ожидался не пустой объект. Получили {data}"
        assert data["login_url"], \
        "Ожидалось, что будет найден URL для входа"

    def test_html_form_parser_fail(
        self,
        html_form_parser: Parser[str, dict[str, Any]],
        html_form: str
    ):
        html_form = re.sub("<form .*", "", html_form)

        with pytest.raises(ParseError):
            html_form_parser.parse(html_form)
