from typing import Any
from httpx import URL, Response
import pytest
from src.mtuci_private_api.http import HttpClient, Method

class ScheduleHttpClient(HttpClient):

    async def request(
        self,
        method: Method,
        url: str | URL,
        **kwargs: Any
    ) -> Response:

        with open(
            "tests/fixtures/timetable.json",
            "rb",
        ) as f:
            content = f.read()

        return Response(
            status_code=200,
            content=content
        )

@pytest.fixture
def fake_schedule_client() -> HttpClient:
    return ScheduleHttpClient()
