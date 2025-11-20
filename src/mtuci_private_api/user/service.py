"""Сервис получения информации о пользователе"""

from ..errors import GetUserInfoError, ParseError
from ..models.mtuci import User
from ..http import HttpClient, Method
from ..config import app_config
from .parsers import UserInfoParser
from .request_factory import UserInfoRequestFactory

class UserService:
    """Сервис для получения информации о пользователе

    Attributes:
        client: клиент для HTTP-запросов.
    """

    def __init__(
        self,
        client: HttpClient
    ): # pragma: no cover
        self.client = client

    async def get_user_info(self) -> User:
        body = UserInfoRequestFactory().create()
        response = await self.client.request(
            method=Method.POST,
            url=f"{app_config.mtuci_url}/ilk/x/getProcessor",
            json=body
        )
        response.raise_for_status()

        data = response.json()

        try:
            user = UserInfoParser().parse(data)

            return user
        except ParseError as err:
            raise GetUserInfoError("Error parsing response") from err
