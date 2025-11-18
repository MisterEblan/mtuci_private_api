from src.mtuci_private_api.user import UserService
from src.mtuci_private_api.models import User

class TestUserService:

    async def test_get_user_info(
        self,
        user_service: UserService
    ):
        info = await user_service.get_user_info()

        assert isinstance(
            info, User
        )
