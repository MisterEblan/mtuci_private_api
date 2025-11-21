"""Сервис расписания"""

from httpx import RequestError

from ..http import HttpClient, Method
from ..models import Schedule, User
from ..config import app_config
from ..errors import ParseError, GetScheduleError
from .parsers import TimetableParser
from .request_factory import TimetableRequestFactory

from datetime import datetime
from json.decoder import JSONDecodeError

class ScheduleService:
    """Сервис расписания"""

    def __init__(
        self,
        client: HttpClient,
        user_info: User
    ):
        self.client = client
        self.user_info = user_info

    async def get_schedule(
        self,
        date: datetime
    ) -> Schedule:
        """Получает расписание на указанную дату

        Args:
            date: дата, на которую нужно получить расписание.
                Должна содержать год, месяц и день.

        Returns:
            Расписание на данную дату.

        Raises:
            GetScheduleError: ошибка при получении расписания.
        """
        try:
            params = TimetableRequestFactory().create(
                user_group=self.user_info.group,
                date=date
            )
            response = await self.client.request(
                method=Method.GET,
                url=f"{app_config.mtuci_url}/api/timetable/get",
                params=params
            )

            if not response.is_success:
                raise GetScheduleError(f"Bad status: {response.text}")

            schedule = TimetableParser().parse(
                response.json(),
                date=date
            )

            return schedule
        except ParseError as err:
            raise GetScheduleError("Error parsing response") from err

        except RequestError as err:
            raise GetScheduleError("Error requesting data") from err

        except JSONDecodeError as err:
            raise GetScheduleError(
                "Error decoding response"
            ) from err
