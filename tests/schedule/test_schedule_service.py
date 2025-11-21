from src.mtuci_private_api.schedule import ScheduleService
from src.mtuci_private_api.models import Schedule

from datetime import datetime

class TestScheduleService:

    async def test_get_schedule(
        self,
        schedule_service: ScheduleService
    ):
        schedule = await schedule_service.get_schedule(
            date=datetime(2025, 11, 21)
        )

        print(schedule)

        assert schedule, (
            "Ожидался не пустой объект. ",
            f"Получили {schedule}"
        )

        assert isinstance(schedule, Schedule), (
            "Ожидался объект класса Schedule. ",
            f"Получили {type(schedule)}"
        )
