from src.mtuci_private_api.user import UserService

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
