from httpx import Response
import pytest
from src.mtuci_private_api.errors import GetUserInfoError
from src.mtuci_private_api.user import UserService
from src.mtuci_private_api.http import HttpClient
from unittest.mock import AsyncMock

class TestUserService:

    async def test_get_user_info(
        self,
        user_service: UserService
    ):
        info = await user_service.get_user_info()

        print(info)
        msg = "Ожидалось, что будет получен {}"

        assert info
        assert info.uid,        msg.format("uid")
        assert info.department, msg.format("факультет")
        assert info.course,     msg.format("курс")
        assert info.group,      msg.format("группа")
        assert info.speciality, msg.format("специальность")

    async def test_get_user_info_fail(
        self,
    ):
        mock_response = AsyncMock(Response)
        mock_response.is_success = False
        mock_response.text = "Very bad error"

        fake = AsyncMock(HttpClient)
        fake.request.return_value = mock_response

        user_service = UserService(client=fake)
        with pytest.raises(GetUserInfoError, match="Request wasn't successful"):
            await user_service.get_user_info()

    async def test_get_user_info_fail_parser(
        self,
    ):
        mock_response = AsyncMock(Response)
        mock_response.is_success = True
        mock_response.json.return_value = {"state": "bad"}

        fake = AsyncMock(HttpClient)
        fake.request.return_value = mock_response

        user_service = UserService(client=fake)
        with pytest.raises(GetUserInfoError, match="Error parsing response"):
            await user_service.get_user_info()

