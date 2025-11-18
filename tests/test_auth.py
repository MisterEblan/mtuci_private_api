from httpx import AsyncClient
from src.mtuci_private_api.auth import AuthService
from src.mtuci_private_api.errors import AuthError
import pytest

class TestAuth:

    @pytest.mark.asyncio
    async def test_auth(
        self,
        auth_service: AuthService
    ):
        response = await auth_service.auth()

        # print(response.text)
        # print(
        #     "Status:", response.status_code
        # )
        # print("Headers:", response.headers)
        # print("Cookies:", response.cookies)

    # @pytest.mark.asyncio
    # async def test_fail(
    #         self,
    # ):
    #     service = AuthService(
    #         login="smth",
    #         password="123",
    #         client=AsyncClient()
    #     )
    #
    #     with pytest.raises(AuthError):
    #         await service.auth()
    #
