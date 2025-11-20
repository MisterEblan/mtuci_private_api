from typing import Any
import pytest

from src.mtuci_private_api.models import User
from src.mtuci_private_api.parsers import Parser
from src.mtuci_private_api.user import UserInfoParser
from src.mtuci_private_api.errors import ParseError

class TestUserInfoParsers:

    @pytest.fixture
    def user_info_parser(self) -> Parser[dict[str, Any], User]:
        return UserInfoParser()

    def test_user_info_parser(
        self,
        user_info: dict[str, Any],
        user_info_parser: Parser[dict[str, Any], User]
    ):

        user = user_info_parser.parse(user_info)

        assert user, f"Ожидался не пустой объект. Получили {user}"

        print(user)

        msg = "Ожидалось, что будет поле {}"
        assert user.name,       msg.format("name")
        assert user.department, msg.format("department")
        assert user.group,      msg.format("group")
        assert user.speciality, msg.format("speciality")
        assert user.course,     msg.format("course")

    def test_user_info_parser_fail_validation(
        self,
        user_info: dict[str, Any],
        user_info_parser: Parser[dict[str, Any], User]
    ):
        del user_info["data"]["Ответ"]

        with pytest.raises(ParseError, match="Invalid object"):
            user_info_parser.parse(user_info)

    def test_user_info_parser_fail_personal(
        self,
        user_info: dict[str, Any],
        user_info_parser: Parser[dict[str, Any], User]
    ):

        del user_info["inputParams"]["ФизическоеЛицо"]

        with pytest.raises(ParseError, match="ФизическоеЛицо not found"):
            user_info_parser.parse(user_info)

    def test_user_info_parser_fail_name(
        self,
        user_info: dict[str, Any],
        user_info_parser: Parser[dict[str, Any], User]
    ):
        del user_info["inputParams"]["ФизическоеЛицо"]["name"]

        with pytest.raises(ParseError, match="User name not found"):
            user_info_parser.parse(user_info)
