from datetime import datetime
import json
from src.mtuci_private_api.mtuci import Mtuci

class TestMtuci:

    async def test_auth(
        self,
        mtuci: Mtuci
    ):
        await mtuci.auth()

    async def test_get_user_info(
        self,
        mtuci: Mtuci
    ):
        await mtuci.auth()

        user = await mtuci.get_user_info()

        assert user, \
        f"Ожидался не пустой объект. Получили {user}"

    async def test_get_attendance(
        self,
        mtuci: Mtuci
    ):
        await mtuci.auth()

        attendance = await mtuci.get_attendace()

        assert attendance, \
        f"Ожидался не пустой объект. Получили {attendance}"

    async def test_get_schedule(
        self,
        mtuci: Mtuci
    ):
        await mtuci.auth()
        await mtuci.get_user_info()

        schedule = await mtuci.get_schedule(datetime(2025, 11, 21))

        assert schedule, \
        f"Ожидался не пустой объект. Получили {schedule}"

    async def test_management(
        self,
        mtuci_login: str,
        mtuci_password: str
    ):
        async with Mtuci(
            login=mtuci_login,
            password=mtuci_password
        ) as mtuci:
            user = await mtuci.get_user_info()
            attendance = await mtuci.get_attendace()
            schedule = await mtuci.get_schedule(datetime(2025, 11, 21))

        # print("User:", user)
        # print("Attendance:", json.dumps(
        #     attendance,
        #     ensure_ascii=False,
        #     indent=2,
        #     default=str
        # ))
        # print("Schedule:", json.dumps(
        #     schedule,
        #     ensure_ascii=False,
        #     indent=2,
        #     default=str
        # ))

        assert user
        assert attendance
        assert schedule
